"""Cross-check a legacy Word DOC with OLE/piece-table and Aspose parsing."""

from __future__ import annotations

import hashlib
import json
import re
import struct
import sys
from difflib import SequenceMatcher
from pathlib import Path


RUN = Path(__file__).resolve().parents[1]
DEPS = RUN / ".tmp" / "deps"
sys.path.insert(0, str(DEPS))

import olefile  # type: ignore  # noqa: E402
import aspose.words as aw  # type: ignore  # noqa: E402


SOURCE = next((RUN / "source-provenance" / "original").glob("*.doc"))
OUT = RUN / "extraction"
OUT.mkdir(parents=True, exist_ok=True)


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def write_json(name: str, payload: object) -> None:
    (OUT / name).write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
        newline="\n",
    )


def u32(data: bytes, offset: int) -> int:
    return struct.unpack_from("<I", data, offset)[0]


def extract_piece_table() -> tuple[str, dict[str, object]]:
    with olefile.OleFileIO(str(SOURCE)) as ole:
        streams = []
        for parts in ole.listdir():
            data = ole.openstream(parts).read()
            streams.append(
                {
                    "path": "/".join(parts),
                    "bytes": len(data),
                    "sha256": sha256(data),
                }
            )
        word = ole.openstream("WordDocument").read()
        flags = struct.unpack_from("<H", word, 10)[0]
        table_name = "1Table" if flags & 0x0200 else "0Table"
        table = ole.openstream(table_name).read()
        fc_clx, lcb_clx = struct.unpack_from("<II", word, 0x1A2)
        clx = table[fc_clx : fc_clx + lcb_clx]
        pos = 0
        while pos < len(clx) and clx[pos] == 1:
            pos += 3 + struct.unpack_from("<H", clx, pos + 1)[0]
        if pos >= len(clx) or clx[pos] != 2:
            raise RuntimeError("Piece table Pcdt marker not found")
        plc_length = u32(clx, pos + 1)
        plc = clx[pos + 5 : pos + 5 + plc_length]
        piece_count = (plc_length - 4) // 12
        pieces = []
        chunks = []
        for index in range(piece_count):
            cp_start, cp_end = struct.unpack_from("<II", plc, index * 4)
            pcd_offset = 4 * (piece_count + 1) + 8 * index
            packed = u32(plc, pcd_offset + 2)
            compressed = bool(packed & 0x40000000)
            file_offset = packed & 0x3FFFFFFF
            if compressed:
                file_offset //= 2
            byte_count = (cp_end - cp_start) * (1 if compressed else 2)
            raw = word[file_offset : file_offset + byte_count]
            if compressed:
                # This document's Chinese body is Unicode; retain a guarded fallback.
                decoded = raw.decode("cp1252", errors="replace")
            else:
                decoded = raw.decode("utf-16le", errors="replace")
            chunks.append(decoded)
            pieces.append(
                {
                    "index": index,
                    "cp_start": cp_start,
                    "cp_end": cp_end,
                    "file_offset": file_offset,
                    "compressed": compressed,
                    "bytes": byte_count,
                    "replacement_characters": decoded.count("�"),
                }
            )
        all_stories = "".join(chunks)
        ccp_text = u32(word, 0x4C)
        main = all_stories[:ccp_text]
        controls = {
            "inline_object_0x01": main.count("\x01"),
            "table_cell_0x07": main.count("\x07"),
            "line_break_0x0b": main.count("\x0b"),
            "page_break_0x0c": main.count("\x0c"),
            "field_begin_0x13": main.count("\x13"),
            "field_separator_0x14": main.count("\x14"),
            "field_end_0x15": main.count("\x15"),
        }
        metadata = {
            "extractor": "OLE WordDocument/0Table-or-1Table piece-table parser",
            "source": str(SOURCE),
            "ole_valid": olefile.isOleFile(str(SOURCE)),
            "table_stream": table_name,
            "fib_flags": flags,
            "fcClx": fc_clx,
            "lcbClx": lcb_clx,
            "ccpText": ccp_text,
            "piece_count": piece_count,
            "pieces": pieces,
            "control_character_counts": controls,
            "streams": streams,
            "object_pool_stream_count": sum(
                item["path"].startswith("ObjectPool/") for item in streams
            ),
            "data_stream_present": any(item["path"] == "Data" for item in streams),
        }
        return main, metadata


def clean_text(value: str) -> str:
    value = value.replace("\r\x07", "\n").replace("\x07", "\t")
    value = value.replace("\r", "\n").replace("\x0b", "\n").replace("\x0c", "\n")
    value = re.sub(r"[\x00-\x06\x08-\x0a\x0e-\x12\x16-\x1f]", "", value)
    value = value.replace("\x13", "[FIELD_BEGIN]").replace("\x14", "[FIELD_SEPARATOR]")
    value = value.replace("\x15", "[FIELD_END]").replace("\x01", "[INLINE_OBJECT]")
    return value


def normalize_for_compare(value: str) -> str:
    value = value.replace("Evaluation Only. Created with Aspose.Words. Copyright 2003-2026 Aspose Pty Ltd.", "")
    value = re.sub(r"\s+", "", value)
    return value


def extract_aspose() -> tuple[str, dict[str, object]]:
    document = aw.Document(str(SOURCE))
    parser_text = document.get_text()
    tables = []
    table_nodes = document.get_child_nodes(aw.NodeType.TABLE, True)
    for t_index in range(table_nodes.count):
        table = table_nodes[t_index].as_table()
        rows = []
        for r_index in range(table.rows.count):
            row = table.rows[r_index]
            cells = []
            for c_index in range(row.cells.count):
                cells.append(clean_text(row.cells[c_index].get_text()).strip())
            rows.append(cells)
        tables.append({"table": t_index + 1, "rows": rows})

    fields = []
    for f_index in range(document.range.fields.count):
        field = document.range.fields[f_index]
        try:
            code = field.get_field_code()
        except Exception as exc:  # pragma: no cover - parser-version guard
            code = f"[FIELD_CODE_ERROR: {type(exc).__name__}]"
        fields.append(
            {
                "field": f_index + 1,
                "type": str(field.type),
                "code": code,
                "result": getattr(field, "result", None),
            }
        )

    shapes = []
    images_dir = OUT / "images"
    image_nodes = document.get_child_nodes(aw.NodeType.SHAPE, True)
    for s_index in range(image_nodes.count):
        shape = image_nodes[s_index].as_shape()
        entry: dict[str, object] = {
            "shape": s_index + 1,
            "shape_type": str(shape.shape_type),
            "width_points": shape.width,
            "height_points": shape.height,
            "has_image": bool(shape.has_image),
        }
        if shape.has_image:
            images_dir.mkdir(exist_ok=True)
            extension = shape.image_data.image_type.name.lower()
            if extension == "unknown":
                extension = "bin"
            path = images_dir / f"shape-{s_index + 1:03d}.{extension}"
            shape.image_data.save(str(path))
            entry.update(
                {
                    "extracted_file": path.relative_to(RUN).as_posix(),
                    "bytes": path.stat().st_size,
                    "sha256": sha256(path.read_bytes()),
                }
            )
        try:
            ole = shape.ole_format
            entry["ole_present"] = ole is not None
            if ole is not None:
                entry["ole_prog_id"] = ole.prog_id
                entry["ole_source_full_name"] = ole.source_full_name
        except Exception:
            entry["ole_present"] = False
        shapes.append(entry)

    render_dir = OUT / "pages"
    render_dir.mkdir(exist_ok=True)
    for page in range(document.page_count):
        options = aw.saving.ImageSaveOptions(aw.SaveFormat.PNG)
        options.page_set = aw.saving.PageSet(page)
        options.horizontal_resolution = 150
        options.vertical_resolution = 150
        document.save(str(render_dir / f"page-{page + 1}.png"), options)

    tmp = RUN / ".tmp"
    tmp.mkdir(exist_ok=True)
    document.save(str(tmp / "parser-converted.docx"))
    document.save(str(tmp / "parser-converted.html"))

    structure = {
        "extractor": "Aspose.Words 26.9 evaluation parser",
        "page_count": document.page_count,
        "section_count": document.sections.count,
        "paragraph_count": document.get_child_nodes(aw.NodeType.PARAGRAPH, True).count,
        "table_count": table_nodes.count,
        "tables": tables,
        "field_count": document.range.fields.count,
        "fields": fields,
        "shape_count": image_nodes.count,
        "shapes": shapes,
        "rendered_pages": [
            path.relative_to(RUN).as_posix() for path in sorted(render_dir.glob("*.png"))
        ],
        "evaluation_parser_warning": "Rendered pages may contain an Aspose evaluation watermark; compare source body with the independent piece table.",
    }
    return parser_text, structure


def main() -> None:
    piece_text, ole_structure = extract_piece_table()
    (OUT / "piece-table-main.txt").write_text(
        piece_text.rstrip("\r\n") + "\n", encoding="utf-8", newline="\n"
    )
    (OUT / "piece-table-readable.txt").write_text(
        clean_text(piece_text).rstrip("\r\n") + "\n",
        encoding="utf-8",
        newline="\n",
    )
    write_json("ole-structure.json", ole_structure)

    parser_text, parser_structure = extract_aspose()
    (OUT / "parser-text.txt").write_text(
        parser_text.rstrip("\r\n") + "\n", encoding="utf-8", newline="\n"
    )
    write_json("parser-structure.json", parser_structure)

    left = normalize_for_compare(clean_text(piece_text))
    right = normalize_for_compare(clean_text(parser_text))
    audit = {
        "piece_table_characters_normalized": len(left),
        "parser_characters_normalized": len(right),
        "sequence_similarity": SequenceMatcher(None, left, right).ratio(),
        "piece_text_contained_in_parser": left in right,
        "parser_text_contained_in_piece": right in left,
        "piece_replacement_characters": piece_text.count("�"),
        "parser_replacement_characters": parser_text.count("�"),
        "piece_control_character_counts": ole_structure["control_character_counts"],
        "ole_object_pool_stream_count": ole_structure["object_pool_stream_count"],
        "aspose_table_count": parser_structure["table_count"],
        "aspose_field_count": parser_structure["field_count"],
        "aspose_shape_count": parser_structure["shape_count"],
        "status": "PENDING_VISUAL_AND_SEMANTIC_REVIEW",
    }
    write_json("cross-parser-audit.json", audit)
    print(json.dumps(audit, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
