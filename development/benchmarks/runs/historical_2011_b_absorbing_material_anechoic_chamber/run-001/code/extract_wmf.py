"""Independent recovery of original embedded WMF payloads (no OCR guessing)."""
from pathlib import Path
import sys, tempfile, re, struct, json
RUN=Path(__file__).resolve().parents[1]
for p in [RUN/'.tmp/deps',RUN/'.tmp/parserdeps',*Path(tempfile.gettempdir()).glob('pip-unpack-*/olefile*.whl')]:sys.path.insert(0,str(p))
import olefile
out=RUN/'.tmp/wmf';out.mkdir(parents=True,exist_ok=True)
with olefile.OleFileIO(str(next((RUN/'source').glob('*.doc')))) as ole:
    records=[]
    for stream in ['Data','WordDocument']:
        b=ole.openstream(stream).read()
        for m in re.finditer(b'\x01\x00\x09\x00\x00\x03',b):
            start=m.start(); size=struct.unpack_from('<I',b,start+6)[0]*2
            if 18<=size<=len(b)-start and b[start+size-6:start+size]==b'\x03\x00\x00\x00\x00\x00':
                p=out/f'wmf-{len(records):03}.wmf';p.write_bytes(b[start:start+size]);records.append({'file':p.name,'stream':stream,'offset':start,'bytes':size})
    (RUN/'extraction').mkdir(exist_ok=True)
    (RUN/'extraction/wmf-inventory.json').write_text(json.dumps(records,indent=2),encoding='utf-8')
    raw=ole.openstream('WordDocument').read().decode('utf-16-le',errors='replace')
    a=raw.find('2011年全国研究生');z=raw.find('3. 张以漠，应用光学')
    if a>=0 and z>=0:(RUN/'extraction/raw-main-stream.txt').write_text(raw[a:z+55].replace('\r','\n'),encoding='utf-8')
print('Original WMF payloads recovered:',len(records))
