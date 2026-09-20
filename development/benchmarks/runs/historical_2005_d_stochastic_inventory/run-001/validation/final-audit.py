"""Independent reviewer checks of saved results and the frozen Skill guard."""
from pathlib import Path
import sys,json,hashlib,copy
import numpy as np
import yaml
RUN=Path(__file__).resolve().parents[1]; ROOT=RUN.parents[4]
sys.path.insert(0,str(RUN/'simulation-code')); sys.path.insert(0,str(ROOT))
from inventory import Policy,simulate_cycles,empirical,expected,single_policy,Law
from run import rng,summary
from skill.scripts.runtime_provenance import apply_protocol_change,validate_experiment_record

def load(path): return json.loads((RUN/path).read_text())
def save(path,value): (RUN/path).write_text(json.dumps(value,indent=2,allow_nan=False)+'\n',encoding='utf-8')
def policy(row):
    x=row['policy']; return Policy(*[np.array(x[k]) for k in ['target','own','rate','h','g','p']],x['tau'],x['fixed_order'])

record=yaml.safe_load((RUN/'experiment-record.yaml').read_text())
record['status']='RUNNING'; record['updated_by_workflow']='validate_model'
(RUN/'experiment-record.yaml').write_text(yaml.safe_dump(record,sort_keys=False),encoding='utf-8')
inputs=load('inputs.json'); single=load('results/single.json'); joint=load('results/joint.json'); q5=load('results/q5.json')
audits=[]
for row in single+[joint]:
    for label in ['baseline','primary']:
        result=row[label]; p=policy(result); p.audit(); exact=result['exact']
        error=abs(sum(exact['components_per_day'])-exact['cost_per_day']); assert error<1e-10
        assert abs(sum(result['mc_components_per_day'])-result['mc']['mean'])<1e-10
        assert 0<=exact['stockout_probability']<=1 and 0<=exact['fill_volume']<=1
        assert result['audit']['capacity_violations']==0
        assert result['audit']['max_conservation_error']<1e-8
        audits.append(dict(product=row.get('product','joint'),policy=label,component_error=error,pass_=True))
for label in ['static','adaptive']:
    assert abs(sum(q5[label]['components_per_day'])-q5[label]['cost']['mean'])<1e-10
    assert q5[label]['max_conservation_error']<1e-8

# Dependent lead sensitivity uses circular 4-observation blocks with independent
# complete trajectories. Each marginal remains the empirical PMF exactly.
x=inputs['items'][2]; data=np.array(x['lead_times']); n=len(data); p=policy(single[2]['primary'])
leads=np.stack([data[(rng(601,r).integers(n,size=256)[:,None]+np.arange(4))%n].reshape(-1) for r in range(256)])
sim=simulate_cycles(p,leads)
dependent=dict(scope='SCENARIO: circular block lead dependence, fixed empirical marginal',block_length=4,R=256,N=1024,cost=summary(sim['path_cost']),iid_cost=single[2]['primary']['mc'],analytic_long_run_cost=expected(p,empirical(data))['cost_per_day'],audit=sim['audit'],event_count=int(sim['stockout'].sum()),event_interval='No iid binomial interval: leads within blocks are dependent')
save('validation/dependent-lead-sensitivity.json',dependent)

# Service at a discrete support boundary is not stable under arbitrary rounding.
boundary=[]
for epsilon in [1.,.01,1e-6,1e-9]:
    pol=single_policy(x,x['target']-epsilon); ans=expected(pol,empirical(data))
    boundary.append(dict(epsilon=epsilon,L=pol.L,cost=ans['cost_per_day'],fill=ans['fill_volume'],exact_math_stockout_probability=float(np.mean(data>pol.L/x['rate'])),warning='Do not round L to Q and preserve the same stockout probability'))
save('validation/boundary-sensitivity.json',boundary)

# Execute, not merely describe, the ordered-event counterexample.
def replay(order):
    inventory=0.; fulfilled=0.; lost=0.; received=0.
    for event in order:
        if event=='demand':
            served=min(inventory,1.); inventory-=served; fulfilled+=served; lost+=1.-served
        else: inventory+=1.; received+=1.
    assert abs(received-fulfilled-inventory)<1e-12
    return dict(end_inventory=inventory,fulfilled=fulfilled,lost=lost,cost=5*lost,conservation_pass=True)
probe=load('validation/ordered-protocol-probe.json')
probe['executed_counterexample']={'correct_integrate_then_receive':replay(['demand','arrival']),'wrong_receive_then_integrate':replay(['arrival','demand'])}
assert probe['observed_protocol_changed'] is False and probe['validator_errors']==[]
save('validation/ordered-protocol-probe.json',probe)
save('validation/final-model-audit.json',dict(status='PASS_WITH_DECLARED_SCOPE',cost_capacity_service_checks=audits,q5_conservation_pass=True,dependent_lead_sensitivity=True,event_order_guard='REPRODUCED_FALSE_NEGATIVE; primary implementation was not altered',rice_open_boundary='cost infimum, not attained L<Q optimum; integer admissible optimum L=39',discrete_uniform_sensitivity_service='ESTIMATE_UNSTABLE at numerical support boundary; do not interpret reported tiny-positive shortage as reliable service probability'))
record['executed_protocol']['additional_validation']['dependent_lead_block_simulation']={'R':256,'N':1024,'block_length':4,'product':3}
record['executed_protocol']['additional_validation']['rice_boundary_sensitivity']=True
record['status']='OBSERVED'; record=apply_protocol_change(record)
record['protocol_change_disclosure']['executed_summary']+='; independent final cost/capacity audit, circular-block lead simulation and rice boundary sensitivity'
record['protocol_change_disclosure']['reason']+='; rice input lag correlation and open-boundary optimum required targeted follow-up'
record['change_reason']=record['protocol_change_disclosure']['reason']
record['output_artifacts']+=['DEPENDENT-LEAD','FINAL-MODEL-AUDIT','BOUNDARY-SENSITIVITY','ORDER-PROBE']
assert not validate_experiment_record(record),validate_experiment_record(record)
(RUN/'experiment-record.yaml').write_text(yaml.safe_dump(record,sort_keys=False),encoding='utf-8')
print('Independent model audit PASS; event-order provenance false negative reproduced; dependent lead cost',dependent['cost'])
