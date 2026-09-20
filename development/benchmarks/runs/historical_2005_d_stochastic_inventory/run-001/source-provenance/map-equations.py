"""Bind every inline equation to its actual PICF offset via Word CHPX FKPs."""
from pathlib import Path
import sys,struct,json,re
HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'work/extraction-deps'))
import olefile
u32=lambda b,o:struct.unpack_from('<I',b,o)[0]
with olefile.OleFileIO(next(HERE.glob('*.doc'))) as ole:
    w=ole.openstream('WordDocument').read(); table=ole.openstream('1Table').read()
    fc,lcb=struct.unpack_from('<II',w,154+12*8); bte=table[fc:fc+lcb]; n=(lcb-4)//8
    runs=[]
    for k in range(n):
        pn=u32(bte,4*(n+1)+4*k)&0x3fffff; fkp=w[pn*512:(pn+1)*512]; crun=fkp[511]
        for j in range(crun):
            start,end=struct.unpack_from('<II',fkp,j*4); off=fkp[4*(crun+1)+j]*2
            grp=fkp[off+1:off+1+fkp[off]] if off else b''
            pos=0; props={}
            while pos+2<=len(grp):
                code=struct.unpack_from('<H',grp,pos)[0]; pos+=2; spra=code>>13
                size=[1,1,2,4,2,2,None,3][spra]
                if size is None: size=grp[pos]; pos+=1
                props[code]=grp[pos:pos+size]; pos+=size
            runs.append((start,end,props))
    pieces=json.loads((HERE/'ole-structure.json').read_text())['pieces']
    previews=json.loads((HERE/'equation-previews/index.json').read_text())
    body=(HERE/'body-piece-table.txt').read_text(encoding='utf-8')
    mapping=[]
    data=ole.openstream('Data').read()
    for cp,ch in enumerate(body):
        if ch!='\x01': continue
        piece=next(p for p in pieces if p['start']<=cp<p['end'])
        char_fc=piece['offset']+(cp-piece['start'])*(1 if piece['compressed'] else 2)
        props=next(p for a,b,p in runs if a<=char_fc<b)
        assert 0x6a03 in props, (cp,char_fc,props)
        picf=u32(props[0x6a03],0); end=picf+u32(data,picf)
        hits=[r for r in previews if picf<=r['data_offset']<end]; assert len(hits)==1
        mapping.append(dict(equation=len(mapping)+1,cp=cp,char_fc=char_fc,picf_offset=picf,preview=hits[0]['file']))
    assert len(mapping)==len(previews)==76
    (HERE/'equation-mapping.json').write_text(json.dumps(mapping,indent=2)+'\n',encoding='utf-8')
    print('Verified mappings:',len(mapping),'in-order:',all(x['preview']==f"preview-{x['equation']:03d}.wmf" for x in mapping))
