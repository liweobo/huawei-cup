"""Run current checks without changing Skill or historical artifacts."""
from pathlib import Path
import subprocess,sys,json,os,time
RUN=Path(__file__).resolve().parents[1]; ROOT=RUN.parents[4]
env={**os.environ,'PYTHONDONTWRITEBYTECODE':'1','PYTHONUTF8':'1'}
checks=[('default_pytest',[sys.executable,'-m','pytest','-q','-p','no:cacheprovider']),
        ('development_tests',[sys.executable,'-m','pytest','-q','development/tests','-p','no:cacheprovider','--basetemp',str(RUN/'work/pytest')])]
checks += [(name,[sys.executable,f'development/harness/{name}.py']) for name in ['smoke_test','routing_test','trigger_test','adversarial_trigger_test','behavior_contract_test','trajectory_test','trajectory_safety_test','historical_artifact_test','postmortem_regression_test','problem_facts_test','run001_integrity_test','run002_integrity_test','run003_integrity_test','run_attempt_integrity_test','clean_room_regression_test','temporal_availability_regression_test','runtime_binding_regression_test','portable_runtime_regression_test','repository_packaging_regression_test','phase5_regression_test']]
records=[]
for name,cmd in checks:
    start=time.time()
    try:
        p=subprocess.run(cmd,cwd=ROOT,env=env,stdout=subprocess.PIPE,stderr=subprocess.STDOUT,encoding='utf-8',errors='replace',timeout=300)
        output=p.stdout; code=p.returncode
    except subprocess.TimeoutExpired as e:
        output=str(e.stdout); code=124
    (RUN/f'validation/{name}.log').write_text(output,encoding='utf-8')
    records.append(dict(check=name,command=cmd,exit_code=code,seconds=time.time()-start,log=f'validation/{name}.log'))
    (RUN/'validation/repository-checks.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    print(name,code,output[-350:].replace('\n',' '),flush=True)
