"""Read legacy Word piece table and preserve equation preview streams separately."""
from pathlib import Path
import sys, struct, json, hashlib
HERE = Path(__file__).resolve().parent
sys.path.insert(0,str(HERE.parent/'work/extraction-deps'))
import olefile

def u32(b,o): return struct.unpack_from('<I',b,o)[0]

with olefile.OleFileIO(next(HERE.glob('*.doc'))) as ole:
    streams = []
    out=HERE/'embedded'; out.mkdir(exist_ok=True)
    for parts in ole.listdir():
        data=ole.openstream(parts).read()
        streams.append({'name':'/'.join(parts),'bytes':len(data),'sha256':hashlib.sha256(data).hexdigest()})
        if parts[0]=='ObjectPool':
            (out/('_'.join(parts).replace('\x01','1').replace('\x03','3'))).write_bytes(data)
    word=ole.openstream('WordDocument').read()
    flags=struct.unpack_from('<H',word,10)[0]
    table=ole.openstream('1Table' if flags&0x200 else '0Table').read()
    fc,lcb=struct.unpack_from('<II',word,0x1a2)
    clx=table[fc:fc+lcb]
    pos=0
    while clx[pos]==1: pos+=3+struct.unpack_from('<H',clx,pos+1)[0]
    assert clx[pos]==2
    length=u32(clx,pos+1); plc=clx[pos+5:pos+5+length]; n=(length-4)//12
    chunks=[]; pieces=[]
    for i in range(n):
        c0,c1=struct.unpack_from('<II',plc,i*4)
        pcd=4*(n+1)+8*i
        packed=u32(plc,pcd+2); compressed=bool(packed&0x40000000)
        offset=packed&0x3fffffff
        if compressed: offset//=2
        size=(c1-c0)*(1 if compressed else 2)
        text=word[offset:offset+size].decode('cp1252' if compressed else 'utf-16le')
        chunks.append(text)
        pieces.append(dict(start=c0,end=c1,offset=offset,compressed=compressed))
    raw=''.join(chunks)
    (HERE/'body-piece-table.txt').write_text(raw.replace('\r','\n'),encoding='utf-8')
    (HERE/'ole-structure.json').write_text(json.dumps(dict(streams=streams,pieces=pieces,flags=flags,fcClx=fc,lcbClx=lcb,ccpText=u32(word,0x4c)),indent=2)+'\n',encoding='utf-8')
    print(raw.replace('\r','\n'))
    print(json.dumps(streams,ensure_ascii=False))
