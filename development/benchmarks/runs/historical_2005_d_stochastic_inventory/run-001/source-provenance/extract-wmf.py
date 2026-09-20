from pathlib import Path
import sys,struct,json,zlib
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'work/extraction-deps'))
import olefile
out=HERE/'equation-previews'; out.mkdir(exist_ok=True)
with olefile.OleFileIO(next(HERE.glob('*.doc'))) as ole:
    data=ole.openstream('Data').read()
    records=[]
    for i in range(len(data)-2):
        if data[i]!=120 or data[i+1] not in (1,94,156,218): continue
        try: preview=zlib.decompress(data[i:])
        except zlib.error: continue
        if preview[:6]!=b'\x01\x00\x09\x00\x00\x03': continue
        size=struct.unpack_from('<I',preview,6)[0]*2
        assert size==len(preview)
        name=f'preview-{len(records)+1:03d}.wmf'
        (out/name).write_bytes(preview)
        records.append(dict(file=name,data_offset=i,bytes=size,preceding_hex=data[max(0,i-70):i].hex()))
    (out/'index.json').write_text(json.dumps(records,indent=2)+'\n',encoding='utf-8')
    print('previews',len(records)); print(records[:2])
