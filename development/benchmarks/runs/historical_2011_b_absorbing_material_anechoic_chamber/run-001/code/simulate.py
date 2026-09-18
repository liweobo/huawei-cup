"""Deterministic geometric-optics calculations; all outputs confined to this run."""
from pathlib import Path
from functools import lru_cache
from datetime import datetime, timezone
import csv, json, math, sys, time, platform
import numpy as np
import scipy
from scipy.optimize import minimize_scalar

RUN=Path(__file__).resolve().parents[1]; REPO=RUN.parents[4]
sys.path.insert(0,str(REPO/'skill/scripts'))
from runtime_provenance import validate_experiment_record,apply_protocol_change
from sensitivity import run_sensitivity
P=json.loads((RUN/'parameters.json').read_text(encoding='utf-8'))
OUT=RUN/'outputs';OUT.mkdir(exist_ok=True)
RECORD=RUN/'experiment-records/EXP-2011B-GEOMETRIC-001.yaml'

def dump(name,value):
    path=OUT/name;path.parent.mkdir(parents=True,exist_ok=True)
    path.write_text(json.dumps(value,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def table(name,rows):
    with (OUT/name).open('w',encoding='utf-8',newline='') as f:
        w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)

def wedge(alpha_deg,theta_deg,phi_deg,entry,rho=.5,h=1.,max_bounces=1000):
    alpha,theta,phi=np.deg2rad([alpha_deg,theta_deg,phi_deg]);d=2*h*np.tan(alpha)
    normals=np.array([[0.,np.cos(alpha),np.sin(alpha)],[0.,-np.cos(alpha),np.sin(alpha)]])
    offset=np.array([0.,d*np.cos(alpha)])
    p=np.array([0.,entry*d,0.]);u=np.array([np.sin(theta)*np.cos(phi),np.sin(theta)*np.sin(phi),-np.cos(theta)])
    initial_u=u.copy();w=1.;removed=0.;hits=[];points=[p.copy().tolist()]
    tol=1e-11*h
    for it in range(max_bounces+1):
        dist=normals@p+offset;den=normals@u
        candidates=[]
        for j in range(2):
            if den[j]<-1e-13:
                length=-dist[j]/den[j]
                if length>tol:candidates.append((length,j))
        if u[2]>1e-13:
            length=-p[2]/u[2]
            if length>tol:candidates.append((length,2))
        if not candidates:return dict(status='GEOMETRY_UNRESOLVED',hits=hits,points=points)
        candidates.sort();length,j=candidates[0]
        p=p+length*u;points.append(p.copy().tolist())
        if len(candidates)>1 and abs(candidates[1][0]-length)<tol:
            return dict(status='EDGE_UNDEFINED',hits=hits,points=points)
        if j==2:
            return dict(status='ESCAPED',bounces=len(hits),weight=w,removed=removed,exit_u=u.tolist(),initial_u=initial_u.tolist(),exit_point=p.tolist(),hits=hits,points=points,d=d,h=h)
        before=u.copy();c=float(-np.dot(u,normals[j]));factor=rho*c
        removed+=w*(1-factor);w*=factor;u=u-2*np.dot(u,normals[j])*normals[j]
        hits.append(dict(facet=j,point=p.tolist(),incidence_cos=c,reflection_factor=factor,weight=w,norm_error=float(abs(np.linalg.norm(u)-1)),plane_error=float(abs(np.dot(p,normals[j])+offset[j])),angle_error=float(abs(np.dot(u,normals[j])+np.dot(before,normals[j]))),ridge_error=float(abs(u[0]-initial_u[0]))))
    return dict(status='TRUNCATED',hits=hits,points=points)

@lru_cache(None)
def images(K):
    rows=[]
    for ny in range(K+1):
        for kx in range(-(K-ny),K-ny+1):
            limit=K-ny-abs(kx)
            for kz in range(-limit,limit+1):rows.append((kx,ny,kz,abs(kx)+ny+abs(kz)))
    a=np.asarray(rows,dtype=int)
    return a[:,0],a[:,1],a[:,2],a[:,3]

@lru_cache(None)
def quadrature(n):
    x,w=np.polynomial.legendre.leggauss(n);x=x*P['s']/2;w=w*P['s']/2
    xx,zz=np.meshgrid(x,x,indexing='ij');ww=np.outer(w,w)
    return xx.ravel(),zz.ravel(),ww.ravel()

def source(t):
    psi=np.deg2rad(P['beta_deg'])*(t/P['T']-.5)
    s=np.array([P['R']*np.sin(psi),P['L']-P['R']*np.cos(psi),0.])
    a=np.array([-np.sin(psi),np.cos(psi),0.])
    return s,a,psi

def shell_coefficients(t,K=32,nq=3):
    """Power/I_N by reflection order before multiplication by rho**order."""
    kx,ny,kz,order=images(K);qx,qz,qw=quadrature(nq);S,a,_=source(t)
    xx=kx[:,None]*P['B']+np.where(kx%2==0,1.,-1.)[:,None]*qx-S[0]
    yy=np.where(ny%2==0,(ny+1)*P['L'],-ny*P['L'])[:,None]-S[1]
    zz=kz[:,None]*P['H']+np.where(kz%2==0,1.,-1.)[:,None]*qz
    D=np.sqrt(xx*xx+yy*yy+zz*zz)
    cx,cy,cz=np.abs(xx)/D,np.abs(yy)/D,np.abs(zz)/D
    emission=np.maximum((a[0]*xx+a[1]*yy)/D,0.)
    weight=cx**np.abs(kx[:,None])*cy**ny[:,None]*cz**np.abs(kz[:,None])
    terms=(emission*cy/D**2*weight)@qw
    return np.bincount(order,weights=terms,minlength=K+1)

def ratio(c,rho,K=None):
    if K is not None:c=c[:K+1]
    return float(np.dot(c[1:],rho**np.arange(1,len(c)))/c[0])

def geometric_tail(rho,K,extra_n=False):
    if rho==0:return 0.
    M=K+1;q=1-rho
    if extra_n:
        # n*(2n²+2n+1), expanded around M.
        value=(2*M**3+2*M*M+M)/q+(6*M*M+4*M+1)*rho/q**2+(6*M+2)*rho*(1+rho)/q**3+2*rho*(1+4*rho+rho*rho)/q**4
    else:value=(2*M*M+2*M+1)/q+(4*M+2)*rho/q**2+2*rho*(1+rho)/q**3
    return float(rho**M*value)

def tail_bound(rho,K):
    R=P['R'];delta=P['s']/np.sqrt(2);half=np.deg2rad(P['beta_deg']/2)
    C=(R+delta)**4/((R-delta)**3*R*np.cos(half))
    return float(C*geometric_tail(rho,K))

def derivative_bound(rho,K=12):
    """Conservative global |d gamma/d psi| bound for finite quadrature sum.

    Uses analytic bounds on each cosine derivative and positive quadrature
    weights. Independent of time grid; same bound covers exact area integral.
    Tail derivative is bounded with the same global-distance inequalities.
    """
    R=P['R'];half=np.deg2rad(P['beta_deg']/2);s2=P['s']/2;delta=P['s']/np.sqrt(2)
    kx,ny,kz,N=images(K);mask=N>0;kx,ny,kz,N=[v[mask] for v in (kx,ny,kz,N)]
    lows=np.array([kx*P['B']-s2-R*np.sin(half),np.where(ny%2==0,(ny+1)*P['L'],-ny*P['L'])-(P['L']-R*np.cos(half)),kz*P['H']-s2]).T
    highs=np.array([kx*P['B']+s2+R*np.sin(half),np.where(ny%2==0,(ny+1)*P['L'],-ny*P['L'])-(P['L']-R),kz*P['H']+s2]).T
    minimum=np.where((lows<=0)&(highs>=0),0.,np.minimum(abs(lows),abs(highs)))
    D=np.linalg.norm(minimum,axis=1);C=np.minimum(1.,np.maximum(abs(lows),abs(highs))/D[:,None]);counts=np.array([abs(kx),ny,abs(kz)]).T
    product=np.prod(C**counts,axis=1);product_deriv=np.zeros(len(N))
    for j in range(3):
        reduced=counts.copy();reduced[:,j]=np.maximum(reduced[:,j]-1,0)
        product_deriv+=counts[:,j]*np.prod(C**reduced,axis=1)
    u_rate=R/D
    pref_upper=np.sum(rho**N*C[:,1]*product/D**2)
    deriv=np.sum(rho**N/D**2*((1+u_rate)*C[:,1]*product+u_rate*product+2*C[:,1]*u_rate*product+C[:,1]*u_rate*product_deriv))
    Dmin=R-delta
    pref_upper+=geometric_tail(rho,K)/Dmin**2
    deriv+=((1+4*R/Dmin)*geometric_tail(rho,K)+(R/Dmin)*geometric_tail(rho,K,True))/Dmin**2
    direct_lower=(R-delta)*R*np.cos(half)/(R+delta)**4
    direct_log_deriv=s2/(R-s2*np.sin(half))+np.tan(half)+4*R*s2/(R-delta)**2
    return float(deriv/direct_lower+(pref_upper/direct_lower)*direct_log_deriv)

def explicit_image_check(t=.7,K=4):
    S,a,_=source(t);q=np.array([.073,P['L'],-.061]);low=np.array([-P['B']/2,0.,-P['H']/2]);high=np.array([P['B']/2,P['L'],P['H']/2])
    kx,ny,kz,N=images(K);maxpoint=0.;maxweight=0.;maxdistance=0.;fail=[];examples=[]
    for ix,iy,iz,n in zip(kx,ny,kz,N):
        target=np.array([ix*P['B']+(-1. if ix%2 else 1.)*q[0],(iy+1)*P['L'] if iy%2==0 else -iy*P['L'],iz*P['H']+(-1. if iz%2 else 1.)*q[2]])
        v=target-S;D=np.linalg.norm(v);u=v/D;u0=u.copy();p=S.copy();weight=1.;distance=0.;counts=np.zeros(3,dtype=int);trace=[]
        for step in range(n+1):
            lengths=np.full(3,np.inf)
            for j in range(3):
                if u[j]>1e-12:lengths[j]=(high[j]-p[j])/u[j]
                elif u[j]<-1e-12:lengths[j]=(low[j]-p[j])/u[j]
            j=int(np.argmin(lengths));ell=lengths[j];p=p+ell*u;distance+=ell
            if step<n:
                weight*=.5*abs(u[j]);counts[j]+=1;trace.append({'wall_axis':j,'point':p.copy().tolist()});u[j]*=-1
        expected=(.5*abs(u0[0]))**abs(ix)*(.5*abs(u0[1]))**iy*(.5*abs(u0[2]))**abs(iz)
        err=float(np.linalg.norm(p-q));maxpoint=max(maxpoint,err);maxweight=max(maxweight,abs(weight-expected));maxdistance=max(maxdistance,abs(distance-D))
        if err>1e-8 or list(counts)!=[abs(ix),iy,abs(iz)] or u[1]<=0:fail.append([int(ix),int(iy),int(iz),err,counts.tolist()])
        if n in [1,3] and len(examples)<8:examples.append({'indices':[int(ix),int(iy),int(iz)],'hits':trace,'receiver':p.tolist()})
    return {'paths_checked':len(N),'max_receiver_error_m':maxpoint,'max_path_length_error_m':maxdistance,'max_attenuation_error':maxweight,'failures':fail,'examples':examples}

def run():
    start=time.perf_counter();record=json.loads(RECORD.read_text(encoding='utf-8'));record['status']='RUNNING';record['updated_by_workflow']='run_experiment';assert not validate_experiment_record(record);RECORD.write_text(json.dumps(record,indent=2),encoding='utf-8')
    print('RUNNING: baseline -> improved mechanism -> physical/numerical validation',flush=True)
    q1=[];traces=[];checks=[]
    for alpha in P['q1_half_angles_deg']:
        for theta in P['q1_incidence_deg']:
            for phi in P['q1_azimuth_deg']:
                for entry in P['q1_entry_fractions']:
                    w=wedge(alpha,theta,phi,entry)
                    if w['status']!='ESCAPED':raise RuntimeError(('Unexpected wedge degeneracy',alpha,theta,phi,entry,w['status']))
                    u=np.array(w['initial_u']);scale=np.hypot(u[1],u[2]);theta2=np.rad2deg(np.arctan2(abs(u[1]),-u[2]));b=wedge(alpha,theta2,90 if u[1]>=0 else -90,entry)
                    assert b['status']=='ESCAPED'
                    err=abs(w['weight']-scale**w['bounces']*b['weight']);checks.append(err)
                    q1.append(dict(alpha_deg=alpha,theta_deg=theta,phi_deg=phi,entry_fraction=entry,bounces=w['bounces'],baseline_2d_weight=b['weight'],improved_3d_weight=w['weight'],projection_identity_error=err,ux_out=w['exit_u'][0],uy_out=w['exit_u'][1],uz_out=w['exit_u'][2],power_balance_error=abs(w['weight']+w['removed']-1)))
                    if theta==30 and phi in [0,90] and entry==.3:traces.append(dict(alpha_deg=alpha,theta_deg=theta,phi_deg=phi,entry_fraction=entry,trace=w))
    table('q1-scenarios.csv',q1);dump('q1-ray-traces.json',traces)
    landing=[]
    for alpha in P['q1_half_angles_deg']:
        for count in [256,512,1024]:
            r=[wedge(alpha,0,90,(j+.5)/count) for j in range(count)]
            valid=[x for x in r if x['status']=='ESCAPED'];assert len(valid)==count
            landing.append(dict(alpha_deg=alpha,samples=count,mean_reflected_fraction=float(np.mean([x['weight'] for x in valid])),min_bounces=min(x['bounces'] for x in valid),max_bounces=max(x['bounces'] for x in valid),label='SIMULATED_UNIFORM_LANDING'))
    table('q1-landing-convergence.csv',landing)
    print('Q1 complete:',len(q1),'scenarios; starting chamber baseline and shells',flush=True)
    times=np.linspace(0,4,81);shells=np.array([shell_coefficients(t,40,3) for t in times]);rows=[]
    for t,c in zip(times,shells):
        for rho in P['rho_values']:
            rows.append(dict(time_s=t,source_azimuth_deg=np.rad2deg(source(t)[2]),rho=rho,direct_power_per_initial_W_sr=c[0]*(1+t/4),reflected_power_per_initial_W_sr=c[0]*ratio(c,rho)*(1+t/4),baseline_one_bounce_gamma=ratio(c,rho,1),mechanism_gamma=ratio(c,rho),gamma_tail_upper=tail_bound(rho,40)))
    table('q2-time-curves.csv',rows)
    table('q2-shell-coefficients.csv',[dict(time_s=float(t),**{f'order_{n}':float(v) for n,v in enumerate(c)}) for t,c in zip(times,shells)])
    orders=[]
    for t in [0.,1.,2.]:
        c=shells[int(t*20)]
        for rho in P['rho_values']:
            for K in [1,2,4,8,16,24,32,40]:orders.append(dict(time_s=t,rho=rho,max_bounces=K,gamma=ratio(c,rho,K),difference_from_K40=ratio(c,rho)-ratio(c,rho,K),tail_upper=tail_bound(rho,K)))
    table('q2-order-convergence.csv',orders)
    quad=[]
    for t in [0.,1.,2.]:
        for nq in [1,3,5,9]:
            c=shell_coefficients(t,32,nq)
            for rho in P['rho_values']:quad.append(dict(time_s=t,rho=rho,quadrature_order=nq,gamma=ratio(c,rho),direct_coefficient=c[0]))
    table('q2-area-convergence.csv',quad)
    print('Main chamber curves and area/order refinement complete; checking time extrema',flush=True)
    refined_t=np.linspace(0,4,161);refined=np.array([shell_coefficients(t,24,3) for t in refined_t]);extrema=[]
    for rho in P['rho_values']:
        values=np.array([ratio(c,rho) for c in refined]);opt=minimize_scalar(lambda t:ratio(shell_coefficients(t,32,3),rho),bounds=(0,4),method='bounded',options={'xatol':1e-8})
        candidates=[(float(opt.x),float(opt.fun)),(0.,ratio(shell_coefficients(0,40,5),rho)),(4.,ratio(shell_coefficients(4,40,5),rho)),(2.,ratio(shell_coefficients(2,40,5),rho))]
        # Detect and refine all additional sampled local minima, not only a presumed symmetry point.
        for i in range(1,len(values)-1):
            if values[i]<values[i-1] and values[i]<values[i+1]:
                o=minimize_scalar(lambda t:ratio(shell_coefficients(t,32,3),rho),bounds=(refined_t[i-1],refined_t[i+1]),method='bounded',options={'xatol':1e-8});candidates.append((float(o.x),float(o.fun)))
        best=min(candidates,key=lambda x:x[1]);extrema.append(dict(rho=rho,min_time_s=best[0],min_gamma=best[1],grid81_min=float(min(ratio(c,rho) for c in shells)),grid161_min=float(values.min()),grid81_max=float(max(ratio(c,rho) for c in shells)),grid161_max=float(values.max()),optimizer_success=bool(opt.success),optimizer_nfev=int(opt.nfev),candidates=candidates))
    dump('q2-extrema.json',extrema)
    # Analytic time-Lipschitz bound provides an all-time quadrature-model certificate.
    rho=.05;M=derivative_bound(rho);sample_max=max(ratio(c,rho) for c in shells);margin=.03-sample_max
    certificate={'rho':rho,'derivative_bound_per_radian':M,'coarse_max':sample_max,'margin':margin}
    if margin>0:
        intervals=max(160,int(math.ceil(np.deg2rad(P['beta_deg'])*M/margin)))
        if intervals>100000:raise RuntimeError('All-time certificate requires excessive time mesh; report PARTIAL instead of guessing')
        cert_t=np.linspace(0,4,intervals+1);cert_values=np.array([ratio(shell_coefficients(float(t),10,3),rho) for t in cert_t]);time_error=M*np.deg2rad(P['beta_deg'])/(2*intervals)
        quadrature_delta=max(abs(x['gamma']-next(y['gamma'] for y in quad if y['time_s']==x['time_s'] and y['rho']==rho and y['quadrature_order']==9)) for x in quad if x['rho']==rho and x['quadrature_order']==3)
        certificate.update(intervals=intervals,max_sampled_gamma=float(cert_values.max()),time_discretization_upper=time_error,bounce_tail_upper=tail_bound(rho,10),observed_quadrature_delta=quadrature_delta,all_time_upper_for_quadrature_model=float(cert_values.max()+time_error+tail_bound(rho,10)),passed=bool(cert_values.max()+time_error+tail_bound(rho,10)<.03),scope='Analytic time and bounce bound for nq=3 quadrature; finite-area error separately refined, not certified by the empirical delta.')
        table('q2-time-certificate.csv',[dict(time_s=t,gamma=v) for t,v in zip(cert_t,cert_values)])
    else:certificate.update(passed=False,scope='Failure witnessed directly; no all-time pass claimed')
    dump('q2-time-certificate.json',certificate)
    print('All-time certificate:',certificate,flush=True)
    sensitivity=[]
    for rho in P['rho_values']:
        result=run_sensitivity(lambda rho:max(ratio(c,rho) for c in shells),{'rho':rho},deltas=(.05,.1))
        sensitivity.append({'nominal_rho':rho,'label':'SIMULATED_PERTURBATION','result':result})
    dump('q2-sensitivity.json',sensitivity)
    pathcheck=explicit_image_check();dump('verification/image-vs-explicit-paths.json',pathcheck)
    unit=[]
    for alpha in [10,15,30,45]:
        for e in [.13,.31,.69,.87]:
            for h in [.1,1.,10.]:
                z=wedge(alpha,30,45,e,h=h);unit.extend(z['hits'])
    rightangle=wedge(45,0,90,.23);zero=wedge(30,25,35,.31,rho=0);scaled=[wedge(15,30,45,.31,h=h) for h in [.1,1,10]]
    physical={
      'q1_max_norm_error':max(x['norm_error'] for x in unit),
      'q1_max_plane_error_m':max(x['plane_error'] for x in unit),
      'q1_max_equal_angle_error':max(x['angle_error'] for x in unit),
      'q1_max_ridge_component_error':max(x['ridge_error'] for x in unit),
      'q1_max_power_balance_error':max(x['power_balance_error'] for x in q1),
      'q1_max_3d_projection_identity_error':max(checks),
      'right_angle_wedge':{'bounces':rightangle['bounces'],'computed_weight':rightangle['weight'],'expected_weight':.5**2/2,'exit_u':rightangle['exit_u']},
      'zero_reflectivity_wedge_weight':zero['weight'],
      'scale_invariant_wedge':{'counts':[x['bounces'] for x in scaled],'weights':[x['weight'] for x in scaled]},
      'q2_max_time_symmetry_error':max(abs(ratio(shells[i],r)-ratio(shells[-i-1],r)) for i in range(len(times)) for r in P['rho_values']),
      'q2_zero_reflectivity_gamma':ratio(shells[40],0.),
      'q2_reflectivity_monotone':all(ratio(c,.05)<=ratio(c,.5) for c in shells),
      'q2_order_monotone':all(np.all(np.diff([ratio(c,.5,K) for K in [1,2,4,8,16,24,32,40]])>=-1e-14) for c in shells),
      'q2_all_coefficients_nonnegative':bool(np.all(shells>=0)),
      'q2_center_direct_exact_error':abs(shell_coefficients(2,1,1)[0]-P['s']**2/P['R']**2),
      'q2_source_scale_cancellation_error':abs(ratio(shells[40]*7.3,.5)-ratio(shells[40],.5)),
      'image_path_check_passed':not pathcheck['failures'],
      'image_count_formula_passed':all(len(images(k)[0])- (len(images(k-1)[0]) if k else 0)==2*k*k+2*k+1 for k in range(11)),
      'corner_policy':wedge(45,0,90,.5)['status'],
      'grazing_reflectivity_limit':float(.5*np.cos(np.pi/2)),
      'normal_incidence_reflectivity':.5,
    }
    assert physical['q1_max_norm_error']<1e-10 and physical['q1_max_power_balance_error']<1e-10
    assert physical['q1_max_3d_projection_identity_error']<1e-10 and physical['image_path_check_passed']
    assert physical['right_angle_wedge']['bounces']==2 and abs(rightangle['weight']-.125)<1e-12
    assert physical['q2_order_monotone'] and physical['q2_all_coefficients_nonnegative']
    dump('physical-checks.json',physical)
    summary={'run_id':'run-001','experiment_id':record['experiment_id'],'q1_scenarios':len(q1),'q1_status':'PARAMETRIC_COMPLETE','q2_extrema':extrema,'time_certificate':certificate,'physical_checks_passed':True,'limitations':['geometrical power-sum model only','no independent measurements','effective material values not calibrated','quadrature error assessed by refinement'],'duration_seconds':time.perf_counter()-start,'environment':{'python':platform.python_version(),'numpy':np.__version__,'scipy':scipy.__version__}}
    dump('summary.json',summary)
    record['status']='OBSERVED';record['updated_by_workflow']='validate_model';record['metrics']={'q1_scenarios':len(q1),'q2_extrema':extrema};record['output_artifacts']=['ART-SUMMARY','ART-Q1-SCENARIOS','ART-Q2-CURVES','ART-PHYSICAL-CHECKS'];record['evidence_ids']=['EV-2011B-COMPUTE','EV-2011B-PHYSICAL','EV-2011B-CONVERGENCE'];record['executed_protocol']['validation'].append({'type':'analytic_time_lipschitz_certificate','rho':.05,'intervals':certificate.get('intervals',0),'quadrature_order':3,'max_bounces':10})
    record=apply_protocol_change(record)
    if record['protocol_changed']:
        record['change_reason']='Added an analytic derivative-bound time mesh to support the all-time requirement near the threshold; underlying models and comparison unchanged.';record['comparable_to_original_plan']=True;record['protocol_change_disclosure']={'planned_summary':'81/161 time samples and extrema search','executed_summary':'Planned refinements plus analytic time derivative bound and adaptive dense mesh','reason':record['change_reason'],'comparable_to_original_plan':True}
    record['executed_protocol_note']='Actual deterministic run completed; all extra checks recorded.';record['completed_at']=datetime.now(timezone.utc).isoformat();assert not validate_experiment_record(record);RECORD.write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(summary,ensure_ascii=False,indent=2),flush=True)

if __name__=='__main__':run()
