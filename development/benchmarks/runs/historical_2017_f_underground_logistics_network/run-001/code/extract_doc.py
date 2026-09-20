"""Validate the legacy Word piece table against an independent document engine.

All conversions and extracted images are audit caches, never formal graph data.
"""
import hashlib
import json
import re
import struct
from pathlib import Path

import olefile

RUN = Path(__file__).resolve().parents[1]
SOURCE = next((RUN / "source").glob("*.doc"))
WORK = RUN / "work" / "verified-extraction"
WORK.mkdir(parents=True, exist_ok=True)


def h(data):
    return hashlib.sha256(data).hexdigest()


def visible(text):
    text = re.sub(r"\x13[^\x14\x15]*\x14", "", text)
    text = re.sub(r"\x13[^\x15]*\x15", "", text)
    return re.sub(r"[\s\x00-\x1f]", "", text)


with olefile.OleFileIO(SOURCE) as ole:
    original_data = ole.openstream("Data").read()
    streams = [{"path": p, "bytes": len(ole.openstream(p).read()),
                "sha256": h(ole.openstream(p).read())} for p in ole.listdir()]
    wd = ole.openstream("WordDocument").read()
    assert struct.unpack_from("<H", wd)[0] == 0xA5EC
    table_name = "1Table" if struct.unpack_from("<H", wd, 10)[0] & 0x200 else "0Table"
    table = ole.openstream(table_name).read()
    fc, size = struct.unpack_from("<II", wd, 0x1A2)
    clx = table[fc:fc + size]
    offset = 0
    while clx[offset] == 1:
        offset += 3 + struct.unpack_from("<H", clx, offset + 1)[0]
    assert clx[offset] == 2
    size = struct.unpack_from("<I", clx, offset + 1)[0]
    plc = clx[offset + 5:offset + 5 + size]
    count = (size - 4) // 12
    assert size == 12 * count + 4
    cps = struct.unpack_from("<" + "I" * (count + 1), plc)
    text, pieces = "", []
    for i in range(count):
        encoded_fc = struct.unpack_from("<I", plc, 4 * (count + 1) + 8 * i + 2)[0]
        compressed = bool(encoded_fc & 0x40000000)
        pos = encoded_fc & 0x3FFFFFFF
        if compressed:
            pos //= 2
        n = cps[i + 1] - cps[i]
        raw = wd[pos:pos + n * (1 if compressed else 2)]
        text += raw.decode("cp1252" if compressed else "utf-16-le")
        pieces.append({"cp_start": cps[i], "cp_end": cps[i + 1], "fc": pos, "compressed": compressed})
    assert len(text) == cps[-1]
    (WORK / "piece-table-text.txt").write_text(text, encoding="utf-8")
    (WORK / "visible-text.txt").write_text(visible(text), encoding="utf-8")

manifest = {"source_sha256": h(SOURCE.read_bytes()), "table_stream": table_name,
            "streams": streams, "pieces": pieces, "characters": len(text),
            "piece_table_text_sha256": h(text.encode()),
            "binary_embedded_object_streams": [s for s in streams if any("ObjectPool" in p for p in s["path"])],
            "status": "EXTRACTION_UNVERIFIED", "independent_engine": None}

try:
    import aspose.words as aw

    doc = aw.Document(str(SOURCE))
    engine_text = doc.get_text()
    (WORK / "aspose-text.txt").write_text(engine_text, encoding="utf-8")
    shapes = []
    for i, node in enumerate(doc.get_child_nodes(aw.NodeType.SHAPE, True)):
        shape = node.as_shape()
        info = {"index": i, "name": shape.name, "has_image": shape.has_image,
                "shape_type": str(shape.shape_type), "text": shape.get_text(),
                "anchor_paragraph": shape.parent_paragraph.get_text() if shape.parent_paragraph else None}
        if shape.has_image:
            data = bytes(shape.image_data.image_bytes)
            info.update({"bytes": len(data), "sha256": h(data), "image_type": str(shape.image_data.image_type)})
            info["present_in_original_data_stream"] = data in original_data
            info["provenance"] = "ORIGINAL_SOURCE" if data in original_data else "RENDERER_GENERATED_OR_UNVERIFIED"
            path = WORK / f"image-{i}.bin"
            path.write_bytes(data)
        shapes.append(info)
    pdf = WORK / "problem-render.pdf"
    doc.save(str(pdf))
    manifest.update({"independent_engine": "Aspose.Words for Python 26.9.0 (evaluation)",
                     "page_count": doc.page_count,
                     "paragraphs": doc.get_child_nodes(aw.NodeType.PARAGRAPH, True).count,
                     "tables": doc.get_child_nodes(aw.NodeType.TABLE, True).count,
                     "fields": [{"type": str(f.type), "code": f.get_field_code(), "result": f.result} for f in doc.range.fields],
                     "shapes": shapes,
                     "piece_visible_contained_in_engine": visible(text) in visible(engine_text),
                     "engine_visible_contained_in_piece": visible(engine_text) in visible(text),
                     "render_pdf_sha256": h(pdf.read_bytes())})
    paragraphs = [visible(p) for p in text.split("\r")]
    paragraphs = [p for p in paragraphs if p and not p.isdigit()]
    unmatched = [p for p in paragraphs if p not in visible(engine_text)]
    manifest["visible_paragraph_check"] = {"checked": len(paragraphs), "unmatched": unmatched,
                                           "status": "PASS" if not unmatched else "EXTRACTION_UNVERIFIED"}
    manifest["original_image_count"] = sum(s.get("present_in_original_data_stream", False) for s in shapes)
    manifest["renderer_added_image_count"] = sum(s.get("has_image", False) and not s.get("present_in_original_data_stream", False) for s in shapes)
    import pymupdf
    with pymupdf.open(pdf) as rendered:
        for i, page in enumerate(rendered):
            page.get_pixmap(matrix=pymupdf.Matrix(1.5, 1.5)).save(str(WORK / f"page-{i + 1}.png"))
        manifest["rendered_page_count"] = len(rendered)
        rendered_text = "\n".join(p.get_text() for p in rendered)
        (WORK / "rendered-text.txt").write_text(rendered_text, encoding="utf-8")
        manifest["rendered_text_sha256"] = h(rendered_text.encode())
except Exception as error:
    manifest["independent_engine_error"] = repr(error)

(RUN / "source-provenance" / "extraction-audit.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
print(json.dumps({k: v for k, v in manifest.items() if k not in ("streams", "rendered_text", "shapes", "fields")}, ensure_ascii=False, indent=2))
