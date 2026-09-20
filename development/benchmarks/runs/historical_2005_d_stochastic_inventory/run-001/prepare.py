"""Freeze verified transcription, input mapping and the pre-experiment protocol."""
from pathlib import Path
import hashlib,json,re,sys,copy
import yaml
RUN=Path(__file__).resolve().parent
ROOT=RUN.parents[4]
sys.path.insert(0,str(ROOT))
from skill.scripts.runtime_provenance import apply_protocol_change,validate_experiment_record

def write(path,text):
    p=RUN/path; p.parent.mkdir(parents=True,exist_ok=True); p.write_text(text.strip()+'\n',encoding='utf-8')

def main():
    labels=['r','c_1','c_2','c_3','c_2 <= c_3','c_4','X','X','Q_0','q','Q','Q_0 < Q','q','L','L*',
            'r','c_1','c_2','c_3','c_4','Q_0','Q','r','c_1','c_2','c_3','c_4','Q_0','Q',
            'r','c_1','c_2','c_3','c_4','Q_0','Q','L*','m','c_1','X','m','r_i','(i=1,2,...,m)',
            'v_i','(i=1,2,...,m)','c_2i','c_3i','(i=1,2,...,m)','c_4i','(i=1,2,...,m)',
            'm','Q_0','m','Q','Q_0 < Q','m','q','L','L*','m','Q_0i','(i=1,2,...,m)','m','Q_i',
            '(i=1,2,...,m)','v_1 = 0.05','v_2 = 0.04','v_3 = 0.10','Q_0 = 6','Q = 10','X','L*',
            'Q_0i','(i=1,2,3)','Q_i','(i=1,2,3)']
    body=(RUN/'source-provenance/body-piece-table.txt').read_text(encoding='utf-8')
    pattern=r'\x13 EMBED Equation\.3  \x14\x01\x15'
    assert len(re.findall(pattern,body))==len(labels)==76
    iterator=iter(enumerate(labels,1))
    def replace(_):
        i,label=next(iterator); return f' [{label}]{{EQ{i:03d}}} '
    transcription=re.sub(pattern,replace,body).strip()
    write('source-provenance/problem-transcription.txt',transcription)
    write('source-provenance/equations.json',json.dumps([dict(id=f'EQ{i:03d}',text=x,status='VERIFIED_PREVIEW_AND_POSITION') for i,x in enumerate(labels,1)],ensure_ascii=False,indent=2))
    histories=re.findall(r'\n((?:\d+ ){10,}\d+)\s*[。.]',body)
    samples=[[int(x) for x in row.split()] for row in histories]
    assert [len(x) for x in samples]==[36,43,61]
    items=[]
    for i,(r,h,e,p,q0,q,v,n) in enumerate([(12,.01,.02,.95,40,60,.05,'noodles'),(15,.03,.04,1.5,40,60,.04,'tissue'),(20,.06,.08,1.25,20,40,.10,'rice')]):
        items.append(dict(id=i+1,name=n,rate=r,order_cost=10,holding_own=h,holding_rented=e,shortage_value=p,own_capacity=q0,target=q,volume=v,lead_times=samples[i]))
    inputs=dict(items=items,joint=dict(own_capacity_volume=6,target_volume=10,order_cost=10,lead_uniform=[1,3]),source_sha256='164ec41eb17115f9ae7c64a0f0c7244759353c82e29e498f98f091c0ce88565d',shortage_unit_status='SOURCE_CONFLICT; primary assumes yuan per lost item')
    write('inputs.json',json.dumps(inputs,ensure_ascii=False,indent=2))
    manifest=dict(schema_version=2,isolation_mode='strict_blind_within_developer_checkout',run_id='run-001',benchmark_id='historical_2005_d_stochastic_inventory',created_at='2026-09-20',active_run_id='run-001',immutable_inputs=[dict(source_artifact_id='SOURCE-DOC',path='source-provenance/仓库容量有限条件下的随机存贮模型（D）.doc',sha256=inputs['source_sha256'])],writable_root=str(RUN),allowed_write_root=str(RUN),allowed_read_roots=[str(RUN),str(ROOT/'skill'),str(ROOT/'development/tests'),str(ROOT/'development/harness')],prior_run_artifacts_visible=True,developer_repository_visible=True,evaluator_files_visible=True,blindness='No problem-specific solutions accessed. Historical files hashed only; no claim of platform-enforced clean room.')
    write('workspace-manifest.yaml',yaml.safe_dump(manifest,allow_unicode=True,sort_keys=False))
    protocol=dict(target='long-run expected cost per calendar day for Q1-Q4; finite 120-day scenario for Q5',primary='analytic renewal-reward expectation; independent event simulation as verification',distribution={'Q2':'empirical PMF from each ordered history, iid cycles assumed','Q4':'continuous Uniform(1,3) given; iid cycles assumed','Q5':'explicit two-point daily demand SCENARIO, shared lead Uniform(1,3)'},shortage='lost sales, primary cost yuan/lost item; alternative cumulative loss exposure scenario',replication_unit='complete independent regenerative trajectory of N cycles; Q5 complete 120-day trajectory',random_library='numpy.Generator(PCG64), SeedSequence([20260920, experiment_namespace, replication_id])',search='Q2 exact finite-support piecewise minimization; Q4 bounded feasible multistart continuous search, no stochastic search seeds',validation=[{'type':'event_vs_analytic','parameters':{'R':[128,256],'cycles':[512,1024]}},{'type':'deterministic_and_boundary_cases','parameters':{}},{'type':'paired_policy_CRN','parameters':{'binding':'replication_id and order_index'}},{'type':'sensitivity','parameters':{'cost':[0.5,2.0],'lead':'Q4 Uniform(1.5,3.5); Q2 empirical ordered half and block uncertainty','capacity':[5,7]}},{'type':'Q5_scenario','parameters':{'R':[128,256],'days':120,'shift_day':60,'shift_multiplier':1.25,'adaptive_window':14}}],event_order=['integrate demand and holding on open interval','receive and top up at arrival','review/order at event time'],warmup='none: each arrival regenerates same target state',policy_claim='Q2 optimum under empirical model; Q4 best found under declared model; Q5 no real-world stochastic claim')
    record=dict(schema_version=1,experiment_id='EXP-2005D-001',run_id='run-001',created_at='2026-09-20',problem='historical_2005_d_stochastic_inventory',question='Q1-Q5',status='PLANNED',updated_by_workflow='design_model',planned_protocol=protocol,executed_protocol={},protocol_changed=True,change_reason='Execution has not started',comparable_to_original_plan=True,protocol_change_disclosure=None,input_artifacts=['SOURCE-DOC','INPUTS'],code_artifacts=['SIMULATION-CODE'],output_artifacts=[],random_seed=20260920,metrics={},evidence_ids=[])
    record=apply_protocol_change(record)
    assert not validate_experiment_record(record)
    write('experiment-record.yaml',yaml.safe_dump(record,allow_unicode=True,sort_keys=False))
    write('experiment-record-planned.yaml',yaml.safe_dump(record,allow_unicode=True,sort_keys=False))
    print('Verified transcription and 36/43/61 observations frozen; PLANNED experiment PASS')

if __name__=='__main__': main()
