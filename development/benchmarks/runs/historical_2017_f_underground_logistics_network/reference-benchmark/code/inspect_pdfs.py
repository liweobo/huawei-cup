"""Read-only PDF extraction/rendering; all intermediate artifacts are ignored."""
import argparse
import json
from pathlib import Path
from pypdf import PdfReader
import fitz

ROOT=Path(__file__).resolve().parents[1]


def extract():
    manifest_path=ROOT/"reference-manifest.json"
    manifest=json.loads(manifest_path.read_text(encoding="utf-8")) if manifest_path.exists() else {
        "files":[dict(path=p.relative_to(ROOT).as_posix(),reference_id=p.stem) for p in (ROOT/"work/pdfs").glob("*.pdf")]}
    rows=[]
    for item in manifest["files"]:
        path=ROOT/item["path"]; reader=PdfReader(path); doc=fitz.open(path)
        out=ROOT/"work/text"/item["reference_id"]; out.mkdir(parents=True,exist_ok=True)
        pages=[]
        for i,page in enumerate(reader.pages):
            text=page.extract_text(extraction_mode="layout")
            alternate=doc[i].get_text()
            (out/f"{i+1:03}.txt").write_text(text,encoding="utf-8",newline="\n")
            (out/f"{i+1:03}.fitz.txt").write_text(alternate,encoding="utf-8",newline="\n")
            pages.append(dict(page=i+1,pypdf_characters=len(text),fitz_characters=len(alternate),images=len(doc[i].get_images())))
        rows.append(dict(reference_id=item["reference_id"],page_count=len(reader.pages),
            metadata={str(k):str(v) for k,v in (reader.metadata or {}).items()},pages=pages,
            text_quality="NATIVE_TEXT_AVAILABLE_FORMULAS_TABLES_REQUIRE_VISUAL_CHECK",
            visual_verification="PENDING"))
        print(item["reference_id"],len(reader.pages),"pages",sum(p["pypdf_characters"] for p in pages),"characters")
    (ROOT/"extraction-audit.json").write_text(json.dumps(rows,ensure_ascii=False,indent=2)+"\n",encoding="utf-8",newline="\n")


def show(ref,start,end):
    for p in range(start,end+1):
        print(f"\n===== {ref} PDF PAGE {p} =====\n")
        print((ROOT/"work/text"/ref/f"{p:03}.fitz.txt").read_text(encoding="utf-8"))


def render(ref,pages):
    doc=fitz.open(ROOT/"work/pdfs"/(ref+".pdf"))
    out=ROOT/"work/rendered"/ref; out.mkdir(parents=True,exist_ok=True)
    for p in pages:
        pix=doc[p-1].get_pixmap(matrix=fitz.Matrix(1.5,1.5),alpha=False)
        pix.save(out/f"{p:03}.png"); print(str(out/f"{p:03}.png"))


if __name__=="__main__":
    p=argparse.ArgumentParser(); p.add_argument("mode",choices=["extract","text","render"]); p.add_argument("ref",nargs="?"); p.add_argument("pages",nargs="*",type=int)
    args=p.parse_args()
    if args.mode=="extract": extract()
    elif args.mode=="text": show(args.ref,*args.pages)
    else: render(args.ref,args.pages)
