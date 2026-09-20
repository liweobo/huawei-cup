"""2005D only: analytic regenerative costs and independent event accounting.

No general-purpose simulation framework. All quantities use a common inventory
unit within a policy (items for Q2, cubic metres for Q4).
"""
from dataclasses import dataclass, replace
import numpy as np
from scipy.optimize import minimize, minimize_scalar
from scipy.special import softmax, expit, logit

@dataclass
class Policy:
    target: np.ndarray
    own: np.ndarray
    rate: np.ndarray
    h: np.ndarray
    g: np.ndarray
    p: np.ndarray
    tau: float
    k: float=10.

    @property
    def L(self): return float(np.maximum(self.target-self.rate*self.tau,0).sum())

    def audit(self):
        assert np.all(self.rate>0) and np.all(self.target>0)
        assert np.all(self.own>=-1e-10) and np.all(self.own<=self.target+1e-10)
        assert np.all(self.g>=self.h) and self.tau>0
        assert self.tau<=np.max(self.target/self.rate)+1e-8

    def record(self):
        self.audit()
        return {**{x:getattr(self,x).tolist() for x in ('target','own','rate','h','g','p')},'tau':float(self.tau),'L':self.L,'fixed_order':self.k,'feasible':True}

@dataclass
class Law:
    values: np.ndarray | None=None
    weights: np.ndarray | None=None
    lower: float=1.
    upper: float=3.

    @property
    def mean(self):
        return (self.lower+self.upper)/2 if self.values is None else float(self.weights@self.values)

    def draw(self,u):
        if self.values is None: return self.lower+(self.upper-self.lower)*u
        return self.values[np.searchsorted(np.cumsum(self.weights),u,side='right')]

    def positive_power(self,offset,power):
        """E[(offset+X)+**power], exactly under this law."""
        offset=np.asarray(offset)
        if self.values is None:
            return (np.maximum(offset+self.upper,0)**(power+1)-np.maximum(offset+self.lower,0)**(power+1))/((power+1)*(self.upper-self.lower))
        return np.sum(np.maximum(offset[...,None]+self.values,0)**power*self.weights,axis=-1)

    def remaining_square(self,z,d,tau):
        if self.values is None:
            return (np.maximum(z-d*(tau+self.lower),0)**3-np.maximum(z-d*(tau+self.upper),0)**3)/(3*d*(self.upper-self.lower))
        return np.sum(np.maximum(z[...,None]-d[...,None]*(tau+self.values),0)**2*self.weights,axis=-1)

    def tail(self,x):
        x=np.asarray(x)
        if self.values is None: return np.clip((self.upper-x)/(self.upper-self.lower),0,1)
        return np.sum((self.values>x[...,None]+1e-10)*self.weights,axis=-1)

def empirical(samples):
    values,counts=np.unique(samples,return_counts=True)
    return Law(values.astype(float),counts/counts.sum())

def expected(policy,law,penalty='lost'):
    policy.audit(); b,a,d=policy.target,policy.own,policy.rate
    t=policy.tau+law.mean
    area=(b*b-law.remaining_square(b,d,policy.tau))/(2*d)
    z=b-a
    rent_area=(z*z-law.remaining_square(z,d,policy.tau))/(2*d)
    lost=d*law.positive_power(policy.tau-b/d,1)
    loss_charge=policy.p*lost if penalty=='lost' else policy.p*d*law.positive_power(policy.tau-b/d,2)/2
    parts=np.array([policy.k,np.sum(policy.h*(area-rent_area)),np.sum(policy.g*rent_area),loss_charge.sum()])
    return dict(cost_per_day=float(parts.sum()/t),components_per_day=(parts/t).tolist(),cycle_cost=float(parts.sum()),cycle_days=float(t),stockout_probability=float(law.tail(np.min(b/d)-policy.tau)),stockout_by_product=law.tail(b/d-policy.tau).tolist(),fill_by_product=(1-lost/(d*t)).tolist(),fill_volume=float(1-lost.sum()/(d.sum()*t)),lost_per_cycle=lost.tolist())

def single_policy(item,L):
    arr=lambda x:np.array([float(x)])
    return Policy(arr(item['target']),arr(item['own_capacity']),arr(item['rate']),arr(item['holding_own']),arr(item['holding_rented']),arr(item['shortage_value']),float((item['target']-L)/item['rate']))

def optimize_single(item,law,penalty='lost',integer=False):
    q=item['target']; r=item['rate']; upper=q-1e-6
    fun=lambda L:expected(single_policy(item,L),law,penalty)['cost_per_day']
    if integer:
        choices=[float(x) for x in range(int(q))]
    else:
        leads=law.values if law.values is not None else np.array([law.lower,law.upper])
        points=sorted(set([0.,upper]+[float(x) for x in np.r_[r*leads,item['own_capacity']+r*leads] if 0<x<upper]))
        choices=points.copy()
        for lo,hi in zip(points,points[1:]):
            result=minimize_scalar(fun,bounds=(lo,hi),method='bounded',options={'xatol':1e-10})
            if result.success: choices.append(float(result.x))
    best=min(choices,key=fun)
    return single_policy(item,best),dict(candidates=len(choices),boundary_infimum=bool(abs(best-upper)<2e-6),integer=integer,claim='FINITE_INTEGER_OPTIMUM' if integer else 'EMPIRICAL_MODEL_PIECEWISE_MINIMUM')

def joint_baseline(items,own=6.,total=10.,law=None):
    v=np.array([x['volume'] for x in items]); d=np.array([x['rate'] for x in items])*v
    b=total*d/d.sum(); a=own*d/d.sum()
    return Policy(b,a,d,np.array([x['holding_own'] for x in items])/v,np.array([x['holding_rented'] for x in items])/v,np.array([x['shortage_value'] for x in items])/v,max(1e-6,total/d.sum()-(law or Law()).mean))

def optimize_joint(base,law,penalty='lost'):
    own=base.own.sum(); extra=base.target.sum()-own
    def decode(z):
        a=own*softmax(np.r_[z[:2],0]); b=a+extra*softmax(np.r_[z[2:4],0])
        return replace(base,target=b,own=a,tau=float(np.max(b/base.rate)*expit(z[4])))
    ao=base.own/base.own.sum(); ae=(base.target-base.own)/extra
    z0=np.r_[np.log(ao[:2]/ao[2]),np.log(ae[:2]/ae[2]),logit(base.tau/np.max(base.target/base.rate))]
    shifts=[np.zeros(5),[1,0,-1,0,0],[-1,0,1,0,0],[0,1,0,-1,0],[0,-1,0,1,0],[0,0,0,0,1],[1,-1,-1,1,-1],[-1,1,1,-1,1]]
    best=base; value=expected(base,law,penalty)['cost_per_day']; trace=[]
    for i,shift in enumerate(shifts):
        f=lambda z:expected(decode(z),law,penalty)['cost_per_day']
        result=minimize(f,np.clip(z0+shift,-12,12),method='L-BFGS-B',bounds=[(-12,12)]*5,options={'ftol':1e-13,'gtol':1e-7,'maxiter':800,'maxls':40})
        candidate=decode(result.x); candidate.audit(); cost=f(result.x); before=value
        if cost<value: best,value=candidate,cost
        trace.append(dict(start=i,feasible=True,cost=float(cost),incumbent_before=float(before),incumbent_after=float(value),success=bool(result.success),termination=str(result.message),evaluations=int(result.nfev),latent=result.x.tolist()))
    return best,trace

def simulate_cycles(policy,leads,penalty='lost'):
    """Vectorized independent event paths: trapezoids between actual break events.

    The last dimension indexes successive regenerative cycles. Time observations
    within a cycle are never used as independent uncertainty samples.
    """
    policy.audit(); leads=np.asarray(leads); assert np.all(leads>=0)
    shape=leads.shape; end=policy.tau+leads; m=len(policy.target)
    inventory=np.broadcast_to(policy.target,shape+(m,)).copy()
    fulfilled=np.zeros_like(inventory); lost=np.zeros_like(inventory)
    own_charge=np.zeros(shape); rent_charge=np.zeros(shape); shortage=np.zeros(shape)
    points=[np.zeros(shape),end,np.full(shape,policy.tau)]
    for b,a,d in zip(policy.target,policy.own,policy.rate):
        points.extend([np.minimum(end,(b-a)/d),np.minimum(end,b/d)])
    points=np.sort(np.stack(points,axis=-1),axis=-1)
    peak_own=0.; peak_rent=0.; max_balance=0.
    for j in range(points.shape[-1]-1):
        dt=points[...,j+1]-points[...,j]
        requested=dt[...,None]*policy.rate
        served=np.minimum(inventory,requested); missing=requested-served
        after=inventory-served
        own_start=np.minimum(inventory,policy.own); own_end=np.minimum(after,policy.own)
        rent_start=inventory-own_start; rent_end=after-own_end
        own_charge+=np.sum((own_start+own_end)/2*policy.h,axis=-1)*dt
        rent_charge+=np.sum((rent_start+rent_end)/2*policy.g,axis=-1)*dt
        if penalty=='lost': shortage+=np.sum(missing*policy.p,axis=-1)
        else: shortage+=np.sum((lost+missing/2)*policy.p,axis=-1)*dt
        fulfilled+=served; lost+=missing; inventory=after
        assert np.min(inventory)>=-1e-10
        assert np.max(own_start.sum(axis=-1))<=policy.own.sum()+1e-9
        peak_own=max(peak_own,float(own_start.sum(axis=-1).max()))
        peak_rent=max(peak_rent,float(rent_start.sum(axis=-1).max()))
        max_balance=max(max_balance,float(np.abs(policy.target-fulfilled-inventory).max()))
    received=policy.target-inventory
    assert np.min(received)>=-1e-10
    assert np.max(abs(policy.target+received-fulfilled-policy.target))<1e-8
    assert np.max(abs(fulfilled+lost-end[...,None]*policy.rate))<1e-8
    components=np.stack([np.full(shape,policy.k),own_charge,rent_charge,shortage],axis=-1)
    cycle_cost=components.sum(axis=-1)
    return dict(path_cost=cycle_cost.sum(axis=-1)/end.sum(axis=-1),cycle_cost=cycle_cost,cycle_days=end,components=components,stockout=np.any(lost>1e-9,axis=-1),fill=1-lost.sum(axis=(-2,-1))/(end.sum(axis=-1)*policy.rate.sum()),audit=dict(max_conservation_error=max_balance,max_own=peak_own,max_rented=peak_rent,capacity_violations=0,nonnegative_violations=0,one_order_and_arrival_per_cycle=True))

def finite_path(policy,multipliers,lead_u,adaptive=False):
    """Q5: explicit day/arrival/aggregate-threshold events, lost-sales inventory."""
    H=len(multipliers); inv=policy.target.copy(); t=0.; arrival=np.inf; order_index=0
    costs=np.zeros(4); fulfilled=np.zeros(len(inv)); lost=np.zeros(len(inv)); received=np.zeros(len(inv))
    req_total=np.zeros(len(inv)); stockout_days=set(); max_error=0.; requests=[]
    while t<H-1e-10:
        day=min(int(np.floor(t+1e-9)),H-1)
        # A day multiplier is the current exogenous rate, never a policy input.
        rates=policy.rate*multipliers[day]
        past= multipliers[max(0,day-14):day]
        L=min(policy.target.sum()-1e-6,policy.L*(float(np.mean(past)) if adaptive and len(past) else 1.))
        if abs(t-arrival)<1e-8:
            incoming=policy.target-inv; assert np.all(incoming>=-1e-8)
            received+=incoming; inv=policy.target.copy(); arrival=np.inf
        if not np.isfinite(arrival) and inv.sum()<=L+1e-9:
            assert order_index<len(lead_u)
            arrival=t+1+2*lead_u[order_index]; order_index+=1; costs[0]+=policy.k
        event=min(float(day+1),arrival,float(H))
        # Solve exact next total-inventory threshold crossing in this day segment.
        if not np.isfinite(arrival) and inv.sum()>L:
            breaks=sorted(set([0.,event-t]+[float(x) for x in inv/rates if 0<x<event-t]))
            for lo,hi in zip(breaks,breaks[1:]):
                start=np.maximum(inv-rates*lo,0).sum(); finish=np.maximum(inv-rates*hi,0).sum()
                if start>=L and finish<=L:
                    slope=rates[inv-rates*lo>1e-10].sum()
                    event=min(event,t+lo+(start-L)/slope); break
        duration=event-t
        assert duration>1e-11, (t,arrival,inv,L)
        # Include each own/rented boundary and stockout before integrating cost.
        cuts=sorted(set([0.,duration]+[float(z) for z in np.r_[(inv-policy.own)/rates,inv/rates] if 0<z<duration]))
        for lo,hi in zip(cuts,cuts[1:]):
            dt=hi-lo; before=inv.copy(); demand=rates*dt; served=np.minimum(before,demand); missed=demand-served
            inv=before-served
            own0=np.minimum(before,policy.own); own1=np.minimum(inv,policy.own)
            costs[1]+=np.sum(policy.h*(own0+own1)/2)*dt
            costs[2]+=np.sum(policy.g*((before-own0)+(inv-own1))/2)*dt
            costs[3]+=np.sum(policy.p*missed)
            req_total+=demand; fulfilled+=served; lost+=missed
            if missed.sum()>1e-9: stockout_days.add(day)
            max_error=max(max_error,float(np.abs(policy.target+received-fulfilled-inv).max()))
            assert inv.min()>=-1e-9 and np.minimum(inv,policy.own).sum()<=policy.own.sum()+1e-8
        t=event
    assert np.max(abs(req_total-fulfilled-lost))<1e-7
    return dict(cost_per_day=float(costs.sum()/H),components_per_day=(costs/H).tolist(),fill=float(fulfilled.sum()/req_total.sum()),stockout_days=len(stockout_days),orders=order_index,pending_at_terminal=bool(np.isfinite(arrival)),terminal_inventory=inv.tolist(),max_conservation_error=max_error)
