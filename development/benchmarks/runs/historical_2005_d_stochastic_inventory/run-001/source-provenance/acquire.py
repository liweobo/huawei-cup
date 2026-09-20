"""Acquire only the user-authorized original problem; never fetch solutions."""
import base64
import hashlib
import json
from pathlib import Path
import subprocess
import urllib.request
import urllib.parse

RUN = Path(__file__).resolve().parents[1]
ROOT = RUN.parents[4]
EXPECTED = 'cc7540cbfa71e42d5a8809e933a3856e3c924197'
DIRECTORY = '国赛试题/2005年研究生数学建模竞赛试题'

def git(*args):
    return subprocess.check_output(['git', *args], cwd=ROOT).decode('utf-8').strip()

def freeze():
    target = RUN / 'source-provenance/integrity-before.json'
    if target.exists():
        raise RuntimeError('Initial snapshot already exists; do not overwrite')
    paths = set((ROOT / 'skill').rglob('*'))
    for base in [ROOT / 'development/benchmarks/runs', ROOT / 'development/benchmarks/problems']:
        for p in base.rglob('*'):
            rel = p.relative_to(base).as_posix().lower()
            if any(y in rel for y in ('2020', '2011', '2022', '2023', '2024')):
                paths.add(p)
    files = {p.relative_to(ROOT).as_posix(): hashlib.sha256(p.read_bytes()).hexdigest()
             for p in sorted(paths) if p.is_file()}
    data = dict(head=git('rev-parse', 'HEAD'), branch=git('branch', '--show-current'),
                skill_tree=git('rev-parse', 'HEAD:skill'),
                status=git('status', '--porcelain=v1', '--untracked-files=all'),
                files=files, scope='All files, including untracked, in skill and historical 2011/2020/2022/2023/2024 benchmark run/problem paths')
    target.write_text(json.dumps(data, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')
    print(json.dumps({k:v for k,v in data.items() if k not in ('files','status')}), 'files',len(files))

def get(url):
    req = urllib.request.Request(url, headers={'User-Agent':'huawei-cup-blind-original-problem-audit'})
    with urllib.request.urlopen(req, timeout=60) as response:
        return json.load(response)

def acquire():
    folder_url = 'https://api.github.com/repos/zhanwen/MathModel/contents/' + urllib.parse.quote(DIRECTORY) + '?ref=master'
    listing = get(folder_url)
    matches = [f for f in listing if f['sha'] == EXPECTED]
    if len(matches) != 1:
        raise RuntimeError('Expected blob not uniquely present in authorized folder')
    entry = matches[0]
    blob_url = 'https://api.github.com/repos/zhanwen/MathModel/git/blobs/' + EXPECTED
    blob = get(blob_url)
    content = base64.b64decode(blob['content'])
    observed = hashlib.sha1(b'blob '+str(len(content)).encode()+b'\0'+content).hexdigest()
    assert observed == EXPECTED == entry['sha'] == blob['sha']
    path = RUN / 'source-provenance' / entry['name']
    path.write_bytes(content)
    record = dict(source_tree='https://github.com/zhanwen/MathModel/tree/master/'+DIRECTORY,
                  file_url=entry['html_url'], raw_url=entry['download_url'], directory_api=folder_url,
                  blob_api=blob_url, blob_sha=observed, sha256=hashlib.sha256(content).hexdigest(),
                  bytes=len(content), original_file=path.name, access_date='2026-09-20',
                  directory_entries=[{'name':f['name'],'sha':f['sha'],'type':f['type']} for f in listing],
                  excellent_solutions_accessed=False)
    (RUN / 'source-provenance/source.json').write_text(json.dumps(record,ensure_ascii=False,indent=2)+'\n',encoding='utf-8')
    print(json.dumps(record,ensure_ascii=False,indent=2))

if __name__ == '__main__':
    freeze()
    acquire()
