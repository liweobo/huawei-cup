"""Independently read original XLS; emit cell-traceable directed source data."""
import csv
import hashlib
import json
import math
import sys
from pathlib import Path
import numpy as np

RUN=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(RUN/"work/deps"))
import xlrd
from python_calamine import CalamineWorkbook


def excel_col(n):
    s=""
    while n:
        n,r=divmod(n-1,26)
        s=chr(65+r)+s
    return s


def write_csv(path, fields, rows):
    with path.open("w",encoding="utf-8",newline="") as f:
        w=csv.DictWriter(f,fieldnames=fields); w.writeheader(); w.writerows(rows)


if __name__=="__main__":
    source=json.loads((RUN/"source-manifest.json").read_text(encoding="utf-8"))
    for f in source["files"]:
        assert hashlib.sha256((RUN/f["path"]).read_bytes()).hexdigest()==f["sha256"]
    p=next((RUN/"work/source").glob("*.xls"))
    b=xlrd.open_workbook(p,formatting_info=True); cb=CalamineWorkbook.from_path(str(p))
    comparisons=[]
    for s in b.sheets():
        c=cb.get_sheet_by_name(s.name).to_python()
        mismatches=[]
        for r in range(s.nrows):
            for k in range(s.ncols):
                other=c[r][k] if r<len(c) and k<len(c[r]) else ""
                if s.cell_value(r,k)!=other: mismatches.append([r,k])
        comparisons.append({"sheet":s.name,"dimensions":[s.nrows,s.ncols],"mismatches":mismatches})
    assert not any(c["mismatches"] for c in comparisons)
    od,attr=b.sheets()
    rows=[int(od.cell_value(r,0)) for r in range(1,od.nrows)]
    cols=[int(od.cell_value(0,c)) for c in range(1,od.ncols)]
    ids=[int(attr.cell_value(r,0)) for r in range(1,attr.nrows)]
    assert rows==cols==ids==list(range(1,5))+list(range(791,901))
    raw=np.array([od.row_values(r)[1:] for r in range(1,od.nrows)],dtype=float)
    D=raw.T.copy()
    assert raw.shape==(114,114) and np.isfinite(D).all() and (D>=0).all()
    inputs=RUN/"inputs"; inputs.mkdir(exist_ok=True)
    records=[]
    for i,node in enumerate(ids):
        v=attr.row_values(i+1)
        record={"id":node,"node_type":"park" if i<4 else "region","x_m":v[3],"y_m":v[4],"area_km2":v[1],"area_m2":v[2],"congestion":v[5],"source_row":i+2}
        assert all(isinstance(v[k],float) and math.isfinite(v[k]) for k in [3,4])
        if i>=4:
            assert all(isinstance(v[k],float) and v[k]>0 for k in [1,2,5])
            assert abs(v[2]-v[1]*1e6)<1e-6
        else: assert v[1]==v[2]==v[5]==""
        records.append(record)
    write_csv(inputs/"locations.csv",list(records[0]),records)
    demands=[{"origin":ids[i],"destination":ids[j],"tonnes_per_day":float(D[i,j]),
              "source_cell":excel_col(i+2)+str(j+2)} for i in range(114) for j in range(114)]
    write_csv(inputs/"directed-demand.csv",list(demands[0]),demands)
    exchange=D.sum(axis=0)+D.sum(axis=1)
    audit={"run_id":RUN.name,"experiment_id":"EXP-2017F-SC-001","source_hashes":"PASS","reader_checks":comparisons,
        "canonical_summary":{"source_od_rows":114,"source_od_columns":114,"location_rows":114,"region_rows":110,"park_rows":4,
          "missing_od_cells":0,"blank_park_attribute_cells":12,"duplicate_ids":0,"invalid_rows":0,"negative_or_nonfinite_od":0},
        "orientation":{"original":"COLUMN_ORIGIN_ROW_DESTINATION","derived_csv":"explicit origin and destination columns; D[origin,destination] is original transpose"},
        "daily_tonnes":float(D.sum()),"park_outbound":D[:4].sum(axis=1).tolist(),"park_inbound":D[:,:4].sum(axis=0).tolist(),
        "park_related_tonnes":float(D[:4].sum()+D[4:,:4].sum()),"region_region_tonnes":float(D[4:,4:].sum()),
        "asymmetric_pairs":int(np.triu(D!=D.T,1).sum()),"nonzero_diagonal":[{"id":ids[i],"tonnes":float(D[i,i])} for i in range(114) if D[i,i]],
        "region_exchange_min_max":[float(exchange[4:].min()),float(exchange[4:].max())],
        "regions_over_4000":[{"id":ids[i],"in_plus_out":float(exchange[i])} for i in range(4,114) if exchange[i]>4000],
        "congestion_min_max":[min(r["congestion"] for r in records[4:]),max(r["congestion"] for r in records[4:])],
        "units":{"od":"tonnes/day; DOC tonnes and worksheet full-day title","coordinates":"metres","area":["km2","m2"],"congestion":"dimensionless original index"},
        "crs":"NOT_GIVEN","origin":"NOT_GIVEN","projection":"NOT_GIVEN","park_semantics":"SOURCE_CROSS_REFERENCE_INFERENCE",
        "diagonal_handling":"PRESERVED; routing policy declared separately","map_geometry":"No pixel distances used","full_day_dispatch_sensitivity":"station scope not inferred from OD data"}
    (RUN/"results/input-audit.json").write_text(json.dumps(audit,ensure_ascii=False,indent=2)+"\n",encoding="utf-8")
    print(json.dumps(audit,ensure_ascii=False,indent=2))
