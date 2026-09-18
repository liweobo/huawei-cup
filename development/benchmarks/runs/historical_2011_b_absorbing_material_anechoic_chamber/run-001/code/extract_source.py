"""Extract legacy DOC with a run-local parser, retaining original untouched."""
from pathlib import Path
import sys, json, hashlib, re
RUN=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(RUN/'.tmp/deps'))
sys.path.insert(0,str(RUN/'.tmp/parserdeps'))
import olefile
import aspose.words as aw

src=next((RUN/'source').glob('*.doc'))
out=RUN/'extraction'; out.mkdir(exist_ok=True)
tmp=RUN/'.tmp'; tmp.mkdir(exist_ok=True)
with olefile.OleFileIO(str(src)) as ole:
    streams=[{'path':'/'.join(x),'bytes':ole.get_size(x)} for x in ole.listdir()]
    raw=ole.openstream('WordDocument').read().decode('utf-16-le',errors='replace')
    begin=raw.find('2011年全国研究生'); end=raw.find('3. 张以漠，应用光学')
    if begin>=0 and end>=0:
        text=raw[begin:end+55].replace('\r','\n')
        (out/'raw-main-stream.txt').write_text(text,encoding='utf-8')
(out/'ole-inventory.json').write_text(json.dumps(streams,ensure_ascii=False,indent=2),encoding='utf-8')
doc=aw.Document(str(src))
(out/'parser-text.txt').write_text(doc.get_text(),encoding='utf-8')
doc.save(str(tmp/'converted.docx'))
doc.save(str(tmp/'converted.html'))
print('Pages:',doc.page_count,'shapes:',doc.get_child_nodes(aw.NodeType.SHAPE,True).count)
for i in range(doc.page_count):
    options=aw.saving.ImageSaveOptions(aw.SaveFormat.PNG)
    options.page_set=aw.saving.PageSet(i)
    options.horizontal_resolution=140
    options.vertical_resolution=140
    doc.save(str(out/f'page-{i+1}.png'),options)
print('Extraction complete. Parser is evaluation edition; review watermark/truncation against raw stream.')
