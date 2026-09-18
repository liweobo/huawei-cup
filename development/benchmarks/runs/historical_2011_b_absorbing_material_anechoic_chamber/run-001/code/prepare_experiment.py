from pathlib import Path
import sys,json,hashlib
from datetime import datetime,timezone
RUN=Path(__file__).resolve().parents[1];REPO=RUN.parents[4]
sys.path.insert(0,str(REPO/'skill/scripts'))
from runtime_provenance import validate_experiment_record,apply_protocol_change
def write(path,x):
    p=RUN/path;p.parent.mkdir(parents=True,exist_ok=True);p.write_text(json.dumps(x,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
def sha(p):return hashlib.sha256(p.read_bytes()).hexdigest()
now=datetime.now(timezone.utc).isoformat()
params={'B':18.,'H':14.,'L':15.,'b':1.,'R':14.,'s':.3,'beta_deg':45.,'T':4.,'rho_values':[.5,.05],'initial_intensity_normalization':1.,'q1_half_angles_deg':[10.,15.,30.,45.],'q1_incidence_deg':[0.,30.,60.],'q1_azimuth_deg':[0.,45.,90.],'q1_entry_fractions':[.1,.3,.7,.9],'q1_normalized_height_m':1.,'q1_illustrative_rho':.5}
write('parameters.json',params)
write('source-provenance/facts-freeze.json',{'frozen_at':now,'files':{p:sha(RUN/p) for p in ['problem-facts.md','quantity-ledger.md','assumptions.md','mathematical-model.md','parameters.json']}})
protocol={'type':'deterministic_geometric_optics_power_sum','models':['q1_exact_2d','q1_exact_3d','q2_one_bounce','q2_multiple_specular_bounces'],'parameters':'parameters.json','validation':[{'type':'analytic_and_physical_invariants'},{'type':'image_vs_explicit_ray_trace','max_order':4},{'type':'bounce_order_refinement','orders':[1,2,4,8,16,24,32,40]},{'type':'area_quadrature','orders':[1,3,5,9]},{'type':'time_refinement','counts':[81,161]},{'type':'q1_uniform_landing','counts':[256,512,1024]},{'type':'sensitivity','parameters':['rho'],'relative_deltas':[.05,.10],'label':'SIMULATED_PERTURBATION'}],'calibration':'NONE','independent_measurements':'NONE','randomness':'NONE','status_scope':'prescribed_ray_model_only'}
record={'schema_version':1,'experiment_id':'EXP-2011B-GEOMETRIC-001','run_id':'run-001','created_at':now,'problem':RUN.parent.name,'question':'Q1,Q2-flat,Q2-effective','status':'PLANNED','updated_by_workflow':'design_model','planned_protocol':protocol,'executed_protocol':protocol,'protocol_changed':False,'change_reason':'','comparable_to_original_plan':True,'protocol_change_disclosure':None,'input_artifacts':['ART-SOURCE-DOC','ART-PARAMETERS'],'code_artifacts':['ART-SIMULATE'],'output_artifacts':[],'random_seed':None,'metrics':{},'evidence_ids':[],'executed_protocol_note':'Protocol initialized to intended procedure; no results yet. Actual execution is reconciled after run.'}
record=apply_protocol_change(record);assert not validate_experiment_record(record)
write('experiment-records/EXP-2011B-GEOMETRIC-001.yaml',record)
manifest=json.loads((RUN/'workspace-manifest.yaml').read_text(encoding='utf-8'))
manifest.update(created_at=now,active_run_id='run-001',writable_root=str(RUN),isolation_mode='user_authorized_repository_scoped',prior_run_artifacts_visible=True,developer_repository_visible=True,evaluator_files_visible=True,allowed_read_roots=['source','extraction',str(REPO/'skill')],status='MODELS_FROZEN',isolation_disclosure='Existing development repository is visible to root audit and regression; no clean-room claim. User explicitly selected this benchmark run directory. Only current source/domain inputs consumed for modeling.')
write('workspace-manifest.yaml',manifest)
print('Facts frozen; Experiment Record PLANNED validated. Repository-scoped isolation disclosed, not claimed as clean room.')
