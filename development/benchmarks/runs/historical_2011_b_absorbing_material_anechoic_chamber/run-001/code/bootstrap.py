"""Read-only source retrieval and integrity snapshot for the strict 2011B run."""
from pathlib import Path
import hashlib, json, subprocess, sys, urllib.request, urllib.parse
from datetime import datetime, timezone

RUN = Path(__file__).resolve().parents[1]
REPO = RUN.parents[4]
BENCHMARK = RUN.parent.name
def sha(p):
    h = hashlib.sha256()
    with p.open('rb') as f:
        for b in iter(lambda: f.read(1024 * 1024), b''): h.update(b)
    return h.hexdigest()
def write(path, obj):
    p = RUN / path; p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(json.dumps(obj, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
def git(*args): return subprocess.check_output(['git', *args], cwd=REPO, text=True, encoding='utf-8').strip()
def snapshot():
    roots = [REPO/'skill', REPO/'development/benchmarks']
    return {p.relative_to(REPO).as_posix(): sha(p) for root in roots for p in sorted(root.rglob('*')) if p.is_file() and RUN.parent not in p.parents}
def get(url):
    url = urllib.parse.quote(url, safe=':/?=&%')
    req=urllib.request.Request(url, headers={'User-Agent':'2011B-strict-blind-source-audit','Accept':'application/vnd.github+json'})
    with urllib.request.urlopen(req, timeout=90) as r: return r.read()
if __name__ == '__main__':
    mode=sys.argv[1]
    if mode=='init':
        assert not (RUN/'source-provenance/integrity-before.json').exists()
        before={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'head':git('rev-parse','HEAD'),'skill_tree':git('rev-parse','HEAD:skill'),'branch':git('branch','--show-current'),'git_status':git('status','--short'),'files':snapshot()}
        write('source-provenance/integrity-before.json',before)
        write('workspace-manifest.yaml',{'schema_version':1,'benchmark_id':BENCHMARK,'run_id':'run-001','allowed_write_root':str(RUN),'allowed_read_roots':[str(REPO/'skill'),str(RUN)],'immutable_inputs':[],'status':'SOURCE_ACQUISITION','note':'JSON is valid YAML. Historical assets read only for hashing and regression; no historical solutions consumed.'})
        print(json.dumps({k:v for k,v in before.items() if k!='files'},ensure_ascii=False)); print('Protected files:',len(before['files']))
    elif mode=='download':
        directory='国赛试题/2011年研究生数学建模竞赛试题'
        api='https://api.github.com/repos/zhanwen/MathModel/contents/'+urllib.parse.quote(directory,safe='/')+'?ref=master'
        listing=json.loads(get(api)); write('source-provenance/directory-listing.json',listing)
        filename='2011B题吸波材料与微波暗室问题的数学建模.doc'
        entry=next(x for x in listing if x['name']==filename)
        p=RUN/'source'/filename; p.parent.mkdir(exist_ok=True)
        p.write_bytes(get(entry['download_url']))
        record={'source_status':'USER_DESIGNATED_HISTORICAL_MIRROR','official_origin_independently_verified':False,'directory_url':'https://github.com/zhanwen/MathModel/tree/master/'+directory,'api_url':api,'file_url':entry['html_url'],'download_url':entry['download_url'],'git_blob_sha':entry['sha'],'sha256':sha(p),'bytes':p.stat().st_size,'retrieved_utc':datetime.now(timezone.utc).isoformat(),'excellent_solutions_accessed':False,'scope':'Only the specified 2011 problem directory listing and exact target DOC were requested.'}
        write('source-provenance/source.json',record)
        manifest=json.loads((RUN/'workspace-manifest.yaml').read_text(encoding='utf-8')); manifest['immutable_inputs']=[{'path':str(p),'sha256':sha(p)}]; manifest['status']='INPUT_AUDIT'; write('workspace-manifest.yaml',manifest)
        print(json.dumps(record,ensure_ascii=False)); print('Directory entries:',[x['name'] for x in listing])
    elif mode=='check':
        before=json.loads((RUN/'source-provenance/integrity-before.json').read_text(encoding='utf-8')); after=snapshot()
        changes=[p for p in sorted(before['files'].keys()|after.keys()) if before['files'].get(p)!=after.get(p)]
        result={'timestamp_utc':datetime.now(timezone.utc).isoformat(),'head':git('rev-parse','HEAD'),'skill_tree':git('rev-parse','HEAD:skill'),'skill_tree_unchanged':git('rev-parse','HEAD:skill')==before['skill_tree'],'protected_file_count_before':len(before['files']),'protected_file_count_after':len(after),'changed_protected_paths':changes,'pass':not changes,'git_status':git('status','--short')}
        write('source-provenance/integrity-after.json',result); print(json.dumps(result,ensure_ascii=False)); assert result['pass']
