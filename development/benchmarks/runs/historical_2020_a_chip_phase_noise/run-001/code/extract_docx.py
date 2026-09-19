from __future__ import annotations

import argparse
import json
import re
import shutil
import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET


W = "http://schemas.openxmlformats.org/wordprocessingml/2006/main"
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
REL = "http://schemas.openxmlformats.org/package/2006/relationships"
NS = {"w": W, "m": "http://schemas.openxmlformats.org/officeDocument/2006/math", "a": "http://schemas.openxmlformats.org/drawingml/2006/main", "r": R}


def local_name(tag: str) -> str:
    return tag.rsplit("}", 1)[-1]


def text_of(node: ET.Element) -> str:
    return "".join(node.itertext())


def compact_formula(node: ET.Element) -> str:
    parts = []
    for child in node.iter():
        name = local_name(child.tag)
        if name == "t" and child.text:
            parts.append(child.text)
        elif name == "br":
            parts.append("\n")
    return "".join(parts).strip()


def paragraph_payload(p: ET.Element, index: int) -> dict:
    formulas = [ET.tostring(x, encoding="unicode") for x in p.iter() if local_name(x.tag) == "oMath"]
    drawings = []
    for blip in p.iter():
        if local_name(blip.tag) == "blip":
            rid = blip.attrib.get(f"{{{R}}}embed") or blip.attrib.get(f"{{{R}}}link")
            if rid:
                drawings.append(rid)
    return {
        "index": index,
        "style": next((x.attrib.get(f"{{{W}}}val") for x in p if local_name(x.tag) == "pPr" for x in x if local_name(x.tag) == "pStyle"), None),
        "text": text_of(p).strip(),
        "formulas_linear": [compact_formula(x) for x in p.iter() if local_name(x.tag) == "oMath"],
        "formulas_omml": formulas,
        "drawing_relationship_ids": drawings,
    }


def table_payload(tbl: ET.Element, index: int) -> dict:
    rows = []
    for tr in tbl:
        if local_name(tr.tag) != "tr":
            continue
        cells = []
        for tc in tr:
            if local_name(tc.tag) != "tc":
                continue
            cells.append(text_of(tc).strip())
        rows.append(cells)
    return {"index": index, "rows": rows}


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("docx", type=Path)
    ap.add_argument("out", type=Path)
    args = ap.parse_args()
    out = args.out
    out.mkdir(parents=True, exist_ok=True)
    package_dir = out / "package"
    if package_dir.exists():
        shutil.rmtree(package_dir)
    package_dir.mkdir()
    media_dir = out / "media"
    media_dir.mkdir(exist_ok=True)
    embedded_dir = out / "embedded"
    embedded_dir.mkdir(exist_ok=True)

    with zipfile.ZipFile(args.docx) as zf:
        names = zf.namelist()
        for name in names:
            target = package_dir / name
            target.parent.mkdir(parents=True, exist_ok=True)
            target.write_bytes(zf.read(name))
            if name.startswith("word/media/"):
                (media_dir / Path(name).name).write_bytes(zf.read(name))
            if name.startswith("word/embeddings/"):
                (embedded_dir / Path(name).name).write_bytes(zf.read(name))

    document = ET.parse(package_dir / "word/document.xml").getroot()
    body = next((x for x in document if local_name(x.tag) == "body"), None)
    paragraphs = []
    tables = []
    ordered = []
    pidx = 0
    tidx = 0
    if body is not None:
        for child in body:
            name = local_name(child.tag)
            if name == "p":
                item = paragraph_payload(child, pidx)
                paragraphs.append(item)
                ordered.append({"kind": "paragraph", "index": pidx})
                pidx += 1
            elif name == "tbl":
                item = table_payload(child, tidx)
                tables.append(item)
                ordered.append({"kind": "table", "index": tidx})
                tidx += 1

    formulas = [
        {"paragraph_index": p["index"], "linear": linear, "omml": omml}
        for p in paragraphs
        for linear, omml in zip(p["formulas_linear"], p["formulas_omml"])
    ]
    rels = {}
    rel_path = package_dir / "word/_rels/document.xml.rels"
    if rel_path.exists():
        rel_root = ET.parse(rel_path).getroot()
        for rel in rel_root:
            rid = rel.attrib.get("Id")
            if rid:
                rels[rid] = {"type": rel.attrib.get("Type"), "target": rel.attrib.get("Target"), "target_mode": rel.attrib.get("TargetMode")}

    comments = []
    comments_path = package_dir / "word/comments.xml"
    if comments_path.exists():
        root = ET.parse(comments_path).getroot()
        for c in root:
            if local_name(c.tag) == "comment":
                comments.append({"id": c.attrib.get(f"{{{W}}}id"), "author": c.attrib.get(f"{{{W}}}author"), "text": text_of(c).strip()})

    structure = {
        "package_files": names,
        "paragraph_count": len(paragraphs),
        "table_count": len(tables),
        "formula_count": len(formulas),
        "media_files": sorted(p.name for p in media_dir.iterdir()),
        "embedded_files": sorted(p.name for p in embedded_dir.iterdir()),
        "relationships": rels,
        "external_relationships": {k: v for k, v in rels.items() if v.get("target_mode") == "External"},
        "comments": comments,
        "ordered_body": ordered,
        "paragraphs": paragraphs,
        "tables": tables,
        "formulas": formulas,
    }
    (out / "document-structure.json").write_text(json.dumps(structure, ensure_ascii=False, indent=2), encoding="utf-8")

    lines = ["# Extracted 2020A DOCX text", "", "This is a structural extraction from the supplied DOCX. Formula XML is preserved separately.", ""]
    pmap = {p["index"]: p for p in paragraphs}
    tmap = {t["index"]: t for t in tables}
    for item in ordered:
        if item["kind"] == "paragraph":
            p = pmap[item["index"]]
            text = p["text"] or "[EMPTY PARAGRAPH]"
            lines.append(f"P{p['index']}: {text}")
            for f in p["formulas_linear"]:
                lines.append(f"  FORMULA_LINEAR: {f}")
        else:
            t = tmap[item["index"]]
            lines.append(f"TABLE{t['index']}:")
            for row in t["rows"]:
                lines.append("  | " + " | ".join(row) + " |")
    (out / "extracted-text.md").write_text("\n".join(lines) + "\n", encoding="utf-8")

    formula_lines = []
    for f in formulas:
        formula_lines.append(f"PARAGRAPH {f['paragraph_index']} LINEAR: {f['linear']}")
        formula_lines.append(f["omml"])
        formula_lines.append("")
    (out / "formulas-omml.xml.txt").write_text("\n".join(formula_lines), encoding="utf-8")


if __name__ == "__main__":
    main()
