"""Legacy-DOC visual verification; cache stays inside this run."""
import json
from pathlib import Path
import aspose.words as aw
import fitz

RUN=Path(__file__).resolve().parents[1]
p=next((RUN/"work/source").glob("*.doc"))
d=aw.Document(str(p))
text=d.to_string(aw.SaveFormat.TEXT)
(RUN/"work/original-text.txt").write_text(text,encoding="utf-8")
pdf=RUN/"work/original-render.pdf"
d.save(str(pdf))
with fitz.open(pdf) as f:
    for i,page in enumerate(f):
        page.get_pixmap(matrix=fitz.Matrix(1.3,1.3)).save(RUN/f"work/doc-page-{i+1}.png")
    n=len(f)
(RUN/"results/doc-extraction.json").write_text(json.dumps({"pages_rendered":n,"text_characters":len(text),
 "word_tables":d.get_child_nodes(aw.NodeType.TABLE,True).count,"extractor":"Aspose.Words; evaluation branding is renderer output, not original evidence",
 "images_purpose":"Source drawings only; no network or coordinates inferred; original map is independent JPG"},indent=2),encoding="utf-8")
print(n,"pages rendered for independent visual verification")
