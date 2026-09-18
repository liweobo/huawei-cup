"""Fetch only explicitly named general textbook/library pages; no search queries."""
from pathlib import Path
import urllib.request, json, hashlib, re
from datetime import datetime, timezone
RUN=Path(__file__).resolve().parents[1]
SOURCES=[
 ('reflection','https://openstax.org/books/university-physics-volume-3/pages/1-2-the-law-of-reflection','Specular reflection: incident and reflected angles equal with respect to the surface normal.','Close ray direction update for planar reflecting surfaces.'),
 ('quadrature','https://numpy.org/doc/stable/reference/generated/numpy.polynomial.legendre.leggauss.html','Gauss-Legendre nodes and weights integrate polynomials of degree up to 2n-1 on [-1,1].','Finite quiet-zone area integration and resolution checks.'),
]
records=[]
for name,url,claim,why in SOURCES:
    try:
        with urllib.request.urlopen(urllib.request.Request(url,headers={'User-Agent':'Mozilla/5.0'}),timeout=40) as r: b=r.read()
        p=RUN/'.tmp/domain'/f'{name}.html';p.parent.mkdir(parents=True,exist_ok=True);p.write_bytes(b)
        clean=re.sub('<[^>]+>',' ',re.sub(r'<(script|style)[\s\S]*?</\1>','',b.decode(errors='replace')))
        clean=re.sub(r'\s+',' ',clean)
        anchors=['angle of reflection','law of reflection'] if name=='reflection' else ['2*deg','2*deg - 1','2*deg','degree','Weights']
        excerpts=[]
        for a in anchors:
            for m in list(re.finditer(re.escape(a),clean,re.I))[:3]: excerpts.append(clean[max(0,m.start()-200):m.end()+400])
        records.append(dict(id=name,source=url,claim=claim,why_needed=why,confidence='PENDING_CONTENT_REVIEW',sha256=hashlib.sha256(b).hexdigest(),excerpts=excerpts,retrieved_utc=datetime.now(timezone.utc).isoformat()))
    except Exception as e: records.append(dict(id=name,source=url,claim=claim,why_needed=why,confidence='UNVERIFIED_FETCH_FAILED',error=str(e)))
p=RUN/'source-provenance/domain-retrieval.json';p.write_text(json.dumps(records,ensure_ascii=False,indent=2),encoding='utf-8')
print(p.read_text(encoding='utf-8'))
