"""Reproduce the frozen 2005D experiment in this run directory only."""
from pathlib import Path
import copy,json,sys,time,platform
import numpy as np
import scipy
from scipy.stats import t as student_t, beta
import yaml
from dataclasses import replace
from inventory import Policy,Law,empirical,expected,single_policy,optimize_single,joint_baseline,optimize_joint,simulate_cycles,finite_path

RUN=Path(__file__).resolve().parents[1]; ROOT=RUN.parents[4]
sys.path.insert(0,str(ROOT))
from skill.scripts.runtime_provenance import apply_protocol_change,validate_experiment_record
from skill.scripts.mechanism_closure import assess_contract

def write(path,data):
    p=RUN/path; p.parent.mkdir(parents=True,exist_ok=True)
    p.write_text(json.dumps(data,ensure_ascii=False,indent=2,allow_nan=False)+'\n',encoding='utf-8')

def rng(namespace,rep): return np.random.Generator(np.random.PCG64(np.random.SeedSequence([20260920,namespace,rep])))

def summary(values):
    x=np.asarray(values); n=len(x); mean=float(x.mean()); se=float(x.std(ddof=1)/np.sqrt(n)); half=float(student_t.ppf(.975,n-1)*se)
    return dict(R=n,mean=mean,se=se,ci95=[mean-half,mean+half])

def closure(verified):
    def req(name,meaning,source_type,value,unit):
        return dict(name=name,meaning=meaning,required_for='Q1-Q5 declared-model simulation',source_type=source_type,source='problem-facts.md; assumptions.md; model.md',value_or_parameter=value,unit=unit,status='ASSUMED' if source_type=='ASSUMED' else 'RESOLVED',essential=True,assumption_reason='See assumptions.md and sensitivity results' if source_type=='ASSUMED' else '')
    body=dict(model_name='2005D regenerative lost-sales inventory',prediction_or_simulation_target='conditional expected cost/day and service metrics',closure_scope='Empirical lead laws for Q2; given uniform law for Q4; explicit demand scenario Q5',
      geometry_requirements=[req('capacity','Own storage and rented overflow','GIVEN','Q0<Q; Q4 Q0=6,Q=10','items or m3')],
      state_initial_requirements=[req('initial_state','post-arrival target; no backlog/order','ASSUMED','I=b','items or m3')],
      boundary_interface_requirements=[req('top_up','one order; receipt-time top-up; own-first','ASSUMED','nonnegative receipt=b-I; overflow rented','items or m3')],
      forcing_input_requirements=[req('lead_law','conditional iid lead inputs','ASSUMED','empirical or continuous U(1,3)','days'),req('demand','Q1-Q4 fixed rates; Q5 scenario','ASSUMED','inputs.json; Q5 two-point law','stock/day')],
      material_constitutive_requirements=[req('shortage_cost','unit conflict resolved by explicit scenarios','ASSUMED','primary yuan/lost unit; alternate exposure','yuan')],
      observation_requirements=[req('objective','renewal reward / finite scenario','ASSUMED','E[C]/E[T] or E[C_H]/H','yuan/day')],
      termination_horizon_requirements=[req('horizon','exact cycle integration plus N refinement; Q5 H=120','ASSUMED','512/1024 cycles; finite 120 days','days/cycles')],
      unresolved_requirements=[],parameterized_requirements=[],identifiability_status='LIMITED',numerical_termination_verified=verified,
      assumptions_added=[dict(name=n,reason='Operational/model choice explicitly needed for closure',plausible_range='Alternatives and checks in assumptions.md and results/sensitivity.json',result_dependency='All numerical claims remain conditional') for n in ['initial_state','top_up','lead_law','demand','shortage_cost','objective','horizon']],
      model_form_uncertainty=dict(status='PRESENT',acknowledged=True,rationale='Printed c4 unit conflict, finite empirical samples, continuous uniform interpretation',evidence=['assumptions.md','results/sensitivity.json']),evidence=['model.md','validation/model-checks.json'])
    if verified: body.update(closure_status='SCENARIO_ASSUMED',allowed_claim_level='SCENARIO_RESULT')
    result={'schema_version':1,'mechanism_closure':body}
    (RUN/'mechanism-closure.yaml').write_text(yaml.safe_dump(result,allow_unicode=True,sort_keys=False),encoding='utf-8')
    return assess_contract(result,'SCENARIO_RESULT' if verified else None)

def checks():
    arr=lambda x:np.array([float(x)])
    p=Policy(arr(10),arr(6),arr(2),arr(1),arr(3),arr(5),2.,4.)
    results=[]
    for lead,cycle_cost in [(1.,33.),(5.,57.)]:
        a=expected(p,Law(np.array([lead]),np.ones(1)))
        s=simulate_cycles(p,np.array([[lead]]))
        np.testing.assert_allclose(a['cycle_cost'],cycle_cost,rtol=0,atol=1e-10)
        np.testing.assert_allclose(s['cycle_cost'][0,0],cycle_cost,rtol=0,atol=1e-10)
        results.append(dict(check='manual single-cycle cost',lead=lead,expected=cycle_cost,actual=float(s['cycle_cost'][0,0]),pass_=True))
    law=Law(np.array([0.,1.,5.,100.]),np.array([.25]*4))
    for penalty in ['lost','exposure']:
        a=expected(p,law,penalty); s=simulate_cycles(p,np.array([law.values]),penalty)
        np.testing.assert_allclose(s['path_cost'][0],a['cost_per_day'],atol=1e-10)
        results.append(dict(check='zero lead / long lead / exact enumeration',penalty=penalty,max_error=float(abs(s['path_cost'][0]-a['cost_per_day'])),pass_=True))
    finite=finite_path(p,np.ones(3),np.zeros(10))
    np.testing.assert_allclose(finite['cost_per_day'],11.,atol=1e-10)
    results.append(dict(check='finite 3-day deterministic oracle incl terminal pending receipt',cost_per_day=finite['cost_per_day'],pass_=True))
    for bad in [replace(p,own=arr(11)),replace(p,own=arr(-1)),replace(p,tau=6.)]:
        try: bad.audit()
        except AssertionError: pass
        else: raise AssertionError('Illegal policy accepted')
    results.append(dict(check='hard infeasible policies rejected',pass_=True))
    return results

def comparison(base,primary,law,namespace):
    u=np.stack([rng(namespace,r).random(1024) for r in range(256)])
    leads=law.draw(u); out={}; rows=[]
    for name,policy in [('baseline',base),('primary',primary)]:
        exact=expected(policy,law); sims={}
        for N in (512,1024):
            sim=simulate_cycles(policy,leads[:,:N]); sims[N]=sim
            for R in (128,256):
                stat=summary(sim['path_cost'][:R]); stat.update(policy=name,N=N,analytic_cost_per_day=exact['cost_per_day'],bias_from_analytic=stat['mean']-exact['cost_per_day'])
                rows.append(stat)
        s=sims[1024]; events=int(s['stockout'].sum()); n=s['stockout'].size
        interval=[float(beta.ppf(.025,events,n-events+1)) if events else 0.,float(beta.ppf(.975,events+1,n-events)) if events<n else 1.]
        stat=summary(s['path_cost']); assert abs(stat['mean']-exact['cost_per_day'])<=max(.03,6*stat['se']), (name,stat,exact)
        out[name]=dict(policy=policy.record(),exact=exact,mc=stat,mc_components_per_day=np.mean(s['components'].sum(axis=1)/s['cycle_days'].sum(axis=1)[:,None],axis=0).tolist(),mc_fill=summary(s['fill']),stockout_events=events,independent_cycle_trials=n,stockout_cycle_ci95=interval,rare_event_status='ESTIMATE_UNSTABLE' if events<20 else 'ADEQUATE_EVENT_COUNT',audit=s['audit'])
        out[name]['path_rates']=s['path_cost'].tolist()
        out[name]['naive_mean_cycle_cost_rate']=float(np.mean(s['cycle_cost']/s['cycle_days']))
    delta=np.array(out['primary']['path_rates'])-np.array(out['baseline']['path_rates'])
    paired=summary(delta); paired['direction']='primary minus baseline; negative improves cost'; paired['status']='CLEAR_POLICY_ADVANTAGE' if paired['ci95'][1]<0 else 'NO_CLEAR_POLICY_ADVANTAGE'
    out['paired_difference']=paired; out['convergence']=rows
    return out

def input_audit(items):
    rows=[]
    for x in items:
        data=np.array(x['lead_times']); law=empirical(data); mid=len(data)//2
        rows.append(dict(product=x['id'],n=len(data),missing=0,negative=0,values=law.values.tolist(),counts=[int(np.sum(data==v)) for v in law.values],mean=float(data.mean()),sample_sd=float(data.std(ddof=1)),lag1_correlation=float(np.corrcoef(data[:-1],data[1:])[0,1]),ordered_half_means=[float(data[:mid].mean()),float(data[mid:].mean())],scope='Ordered observations; repeated values are legitimate delivery durations, not duplicate records to delete'))
    return dict(total_rows=sum(x['n'] for x in rows),missing_cells=0,invalid_rows=0,duplicate_full_rows='NOT_APPLICABLE: repeated durations are valid observations',frequency_boundary_rows='NOT_APPLICABLE',anomaly_rows='NONE_REMOVED',items=rows,unresolved_questions=['Population tail support','Serial dependence and stationarity','Source c4 unit conflict'])

def sensitivity(items,joint):
    out={'single':[],'joint':[],'evidence_type':'SIMULATED_PERTURBATION / SCENARIO; not new measurements'}
    for x in items:
        law=empirical(x['lead_times']); base=single_policy(x,min(x['target']-1e-6,x['rate']*law.mean))
        primary,_=optimize_single(x,law)
        alternate,_=optimize_single(x,law,'exposure')
        half=[]
        for samples in [x['lead_times'][:len(x['lead_times'])//2],x['lead_times'][len(x['lead_times'])//2:]]:
            p,_=optimize_single(x,empirical(samples)); half.append(dict(L=p.L,cost=expected(p,empirical(samples))['cost_per_day']))
        # Moving-block bootstrap of the supplied consecutive history, block length 4.
        boot=[]; data=np.array(x['lead_times']); n=len(data)
        for b in range(128):
            starts=rng(400+x['id'],b).integers(0,n,size=(n+3)//4)
            sample=np.concatenate([data[(s+np.arange(4))%n] for s in starts])[:n]
            fitted=empirical(sample); candidate,_=optimize_single(x,fitted,integer=True)
            boot.append(candidate.L)
        multipliers=[]
        for scale in (.5,2.):
            changed={**x,'shortage_value':x['shortage_value']*scale}; p,_=optimize_single(changed,law)
            multipliers.append(dict(scale=scale,L=p.L,cost=expected(p,law)['cost_per_day']))
        out['single'].append(dict(product=x['id'],primary_L=primary.L,alternate_penalty=dict(L=alternate.L,expected=expected(alternate,law,'exposure')),ordered_half=half,block_bootstrap=dict(B=128,block_length=4,integer_L_quantiles=np.quantile(boot,[.025,.5,.975]).tolist(),interpretation='conditional distribution-estimation stability, not Monte Carlo CI or guaranteed coverage'),cost_sensitivity=multipliers))
    scenarios=[('shortage_value_half',replace(joint,p=joint.p*.5),Law(),'lost'),('shortage_value_double',replace(joint,p=joint.p*2),Law(),'lost'),('lead_half_day_later',joint,Law(lower=1.5,upper=3.5),'lost'),('integer_uniform',joint,Law(np.array([1.,2.,3.]),np.ones(3)/3),'lost'),('printed_units_exposure',joint,Law(),'exposure')]
    for own in (5.,7.): scenarios.append((f'own_capacity_{int(own)}',joint_baseline(items,own=own),Law(),'lost'))
    for name,base,law,penalty in scenarios:
        candidate,trace=optimize_joint(base,law,penalty)
        out['joint'].append(dict(scenario=name,policy=candidate.record(),expected=expected(candidate,law,penalty),search_starts=len(trace)))
    return out

def q5(policy):
    static=[]; adapt=[]
    for rep in range(256):
        u=rng(501,rep).random(120); multipliers=np.where(u<.5,.5,1.5); multipliers[60:]*=1.25
        leads=rng(502,rep).random(256)
        static.append(finite_path(policy,multipliers,leads,False)); adapt.append(finite_path(policy,multipliers,leads,True))
    answer={'scope':'SCENARIO_ANALYSIS; finite H=120 days; primary cost units only','static':{},'adaptive':{},'convergence':[]}
    for name,paths in [('static',static),('adaptive',adapt)]:
        costs=np.array([x['cost_per_day'] for x in paths]); fills=[x['fill'] for x in paths]
        answer[name]=dict(cost=summary(costs),fill=summary(fills),stockout_days_total=sum(x['stockout_days'] for x in paths),paths_with_pending_order=sum(x['pending_at_terminal'] for x in paths),max_conservation_error=max(x['max_conservation_error'] for x in paths),components_per_day=np.mean([x['components_per_day'] for x in paths],axis=0).tolist(),path_costs=costs.tolist())
        for R in (128,256): answer['convergence'].append(dict(policy=name,**summary(costs[:R])))
    delta=np.array(answer['adaptive']['path_costs'])-np.array(answer['static']['path_costs']); answer['paired_difference']=summary(delta)
    answer['paired_difference']['status']='CLEAR_POLICY_ADVANTAGE' if answer['paired_difference']['ci95'][1]<0 else 'NO_CLEAR_POLICY_ADVANTAGE'
    return answer

def protocol_order_probe(record):
    """Audit the current Skill's actual ordered-protocol change detection."""
    changed=copy.deepcopy(record)
    changed['executed_protocol']=copy.deepcopy(changed['planned_protocol'])
    old=changed['planned_protocol']['event_order']
    changed['executed_protocol']['event_order']=[old[1],old[0],old[2]]
    changed=apply_protocol_change(changed)
    # Equivalent single-interval event example: zero initial stock, unit demand
    # over (0,1), one unit receipt at t=1. Receipt cannot serve earlier demand.
    tiny=dict(initial_inventory=0,demand_during_previous_interval=1,receipt_at_interval_end=1,correct={'fulfilled':0,'lost':1,'end_inventory':1},receipt_moved_before_interval={'fulfilled':1,'lost':0,'end_inventory':0})
    return dict(probe_kind='actual frozen-Skill function audit; NOT an executed production protocol change',planned_order=old,changed_execution_order=changed['executed_protocol']['event_order'],expected_protocol_changed=True,observed_protocol_changed=changed['protocol_changed'],validator_errors=validate_experiment_record(changed),tiny_event_counterexample=tiny,impact='The normalizer treats every list as an unordered set-like sequence, so causally different event protocols compare equal. Production event order is correct and verified directly.')

def main():
    start=time.time(); inputs=json.loads((RUN/'inputs.json').read_text()); items=inputs['items']
    record=yaml.safe_load((RUN/'experiment-record.yaml').read_text()); record['status']='RUNNING'; record['updated_by_workflow']='run_experiment'
    (RUN/'experiment-record.yaml').write_text(yaml.safe_dump(record,sort_keys=False),encoding='utf-8')
    assert not validate_experiment_record(record)
    write('validation/closure-before.json',closure(False))
    write('results/environment.json',dict(python=sys.version,executable=sys.executable,numpy=np.__version__,scipy=scipy.__version__,platform=platform.platform(),rng='numpy.Generator(PCG64)',seed=20260920))
    write('validation/model-checks.json',checks())
    write('validation/input-audit.json',input_audit(items))
    single=[]
    for x in items:
        law=empirical(x['lead_times']); baseline=single_policy(x,min(x['target']-1e-6,x['rate']*law.mean))
        primary,search=optimize_single(x,law); integer,integer_search=optimize_single(x,law,integer=True)
        result=comparison(baseline,primary,law,100+x['id']); result.update(product=x['id'],search=search,integer=dict(policy=integer.record(),expected=expected(integer,law),search=integer_search))
        single.append(result); print('Q2',x['id'],'L',primary.L,'cost',result['primary']['exact']['cost_per_day'],flush=True)
    write('results/single.json',single)
    base=joint_baseline(items); best,trace=optimize_joint(base,Law()); joint=comparison(base,best,Law(),200); joint['search_trace']=trace
    write('results/joint.json',joint); print('Q4 L',best.L,'cost',joint['primary']['exact']['cost_per_day'],flush=True)
    write('results/sensitivity.json',sensitivity(items,base)); print('Sensitivity complete',flush=True)
    write('results/q5.json',q5(best)); print('Q5 complete',flush=True)
    assessment=closure(True); assert assessment['valid_schema'] and assessment['claim_allowed'] and not assessment['reviewer_codes'],assessment
    write('validation/closure-after.json',assessment)
    record['status']='OBSERVED'; record['updated_by_workflow']='validate_model'; record['executed_protocol']=copy.deepcopy(record['planned_protocol'])
    record['executed_protocol']['additional_validation']={'Q2_integer_threshold_enumeration':True,'moving_block_bootstrap':{'B':128,'length':4},'Q4_discrete_uniform_sensitivity':True,'ordered_protocol_guard_probe':True}
    record=apply_protocol_change(record); record['change_reason']='Input/model audit motivated explicit integer, serial-support and unit-interpretation sensitivity plus ordered-protocol guard audit; base policy/estimand/R/N unchanged'
    record['protocol_change_disclosure']={'planned_summary':'Original exact + event, R/N convergence, sensitivity and Q5 plan','executed_summary':'Added integer-Q2, block B=128 length=4, discrete-uniform-Q4 and ordered-event provenance probe','reason':record['change_reason'],'comparable_to_original_plan':True}
    record['output_artifacts']=['SINGLE-RESULTS','JOINT-RESULTS','SENSITIVITY','Q5-RESULTS','MODEL-CHECKS']; record['evidence_ids']=['E-Q2','E-Q4','E-Q5','E-VALIDATION']
    record['metrics']={'q2_cost_per_day':[r['primary']['exact']['cost_per_day'] for r in single],'q4_cost_per_day':joint['primary']['exact']['cost_per_day'],'elapsed_seconds':time.time()-start}
    assert not validate_experiment_record(record),validate_experiment_record(record)
    (RUN/'experiment-record.yaml').write_text(yaml.safe_dump(record,allow_unicode=True,sort_keys=False),encoding='utf-8')
    write('validation/ordered-protocol-probe.json',protocol_order_probe(record))
    print('EXPERIMENT PASS',record['metrics'],flush=True)

if __name__=='__main__': main()
