import csv, hashlib, json, math, statistics, collections
from pathlib import Path
import openpyxl

P = Path(r'C:\Users\aaa\Desktop\text\pressure-test\附件一（训练集）.xlsx')
OUT = Path(r'C:\Users\aaa\Desktop\test\attachment1_audit.json')
ANOM = Path(r'C:\Users\aaa\Desktop\test\attachment1_anomalies.csv')

EXPECTED_T = {25, 50, 70, 90}
EXPECTED_W = {'正弦波', '三角波', '梯形波'}

def is_num(x):
    return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(float(x))

def qtile(xs, q):
    if not xs: return None
    a = sorted(xs)
    pos = (len(a)-1)*q
    lo = int(math.floor(pos)); hi = int(math.ceil(pos))
    if lo == hi: return float(a[lo])
    return float(a[lo] + (a[hi]-a[lo])*(pos-lo))

def five(xs):
    return {'min': min(xs), 'q1': qtile(xs,.25), 'median': qtile(xs,.5), 'q3': qtile(xs,.75), 'max': max(xs), 'mean': statistics.fmean(xs)} if xs else {}

def iqr_bounds(xs, k=1.5):
    if not xs: return (None,None)
    q1,q3=qtile(xs,.25),qtile(xs,.75); i=q3-q1
    return (q1-k*i, q3+k*i)

def wave_features(w):
    # w is expected to be 1024 samples; preserve enough descriptors for QC.
    vals=[float(x) for x in w if is_num(x)]
    if not vals: return {}
    d=[vals[i+1]-vals[i] for i in range(len(vals)-1)]
    absd=[abs(x) for x in d]
    signs=[]
    for x in d:
        if abs(x) <= 1e-12: continue
        s=1 if x>0 else -1
        if not signs or s != signs[-1]: signs.append(s)
    return {
        'n': len(vals),
        'mean': statistics.fmean(vals),
        'std': statistics.pstdev(vals),
        'min': min(vals), 'max': max(vals), 'pp': max(vals)-min(vals),
        'rms': math.sqrt(statistics.fmean([x*x for x in vals])),
        'max_abs': max(abs(x) for x in vals),
        'max_diff': max(absd) if absd else 0.0,
        'mean_abs_diff': statistics.fmean(absd) if absd else 0.0,
        'turns': max(0, len(signs)-1),
        'up_frac': sum(x>0 for x in d)/len(d) if d else None,
        'endpoint_jump': abs(vals[-1]-vals[0]) if len(vals)>1 else None,
        'zero_crossings': sum(vals[i] == 0 or vals[i]*vals[i+1] < 0 for i in range(len(vals)-1)),
    }

def make_hash(vals):
    h=hashlib.sha1()
    for v in vals:
        h.update(repr(v).encode('utf-8')); h.update(b'|')
    return h.hexdigest()

def audit():
    # First pass: formulas in metadata columns only; non-data-only mode is much lighter this way.
    wb_formula=openpyxl.load_workbook(P, read_only=True, data_only=False)
    formula_info={}
    for ws in wb_formula.worksheets:
        f_cells=[]; f_by_col=collections.Counter()
        for row in ws.iter_rows(min_row=1, max_col=4, values_only=False):
            for c in row:
                if isinstance(c.value,str) and c.value.startswith('='):
                    f_cells.append(c.coordinate); f_by_col[c.column_letter]+=1
        formula_info[ws.title]={'count':len(f_cells),'by_col':dict(f_by_col),'examples':f_cells[:10]}
    wb_formula.close()

    wb=openpyxl.load_workbook(P, read_only=True, data_only=True)
    result={'file':P.name,'sheets':[],'totals':{'rows':0,'missing_cells':0,'non_numeric_expected':0,'invalid_temperature':0,'frequency_outside_stated_range':0,'nonpositive_loss':0,'duplicate_full_rows':0}}
    anomaly_rows=[]; global_hashes=set(); duplicate_hashes=collections.Counter()
    for ws in wb.worksheets:
        print('auditing',ws.title, flush=True)
        first = next(ws.iter_rows(min_row=1,max_row=1,values_only=True))
        headers=list(first)
        n=ws.max_row-1; cols=ws.max_column
        missing_by_col=[0]*cols; nonnum_by_col=[0]*cols
        temp_counter=collections.Counter(); wave_counter=collections.Counter(); temp_wave=collections.Counter()
        freq=[]; loss=[]; logloss=[]; pp=[]; wave_means=[]; wave_stds=[]; maxdiff=[]; endpoint=[]
        material=ws.title
        row_flags=[]; row_hash_counts=collections.Counter()
        for ridx,row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=1):
            row=list(row)
            # Pad if the iterator yields fewer cells than max_column.
            if len(row)<cols: row.extend([None]*(cols-len(row)))
            result['totals']['rows'] += 1
            missing=sum(v is None for v in row)
            result['totals']['missing_cells'] += missing
            for j,v in enumerate(row):
                if v is None: missing_by_col[j]+=1
            t,f,p,w=row[0],row[1],row[2],row[3]
            if is_num(t): temp_counter[str(int(t) if float(t).is_integer() else t)]+=1
            else: nonnum_by_col[0]+=1
            if is_num(f): freq.append(float(f))
            else: nonnum_by_col[1]+=1
            if is_num(p):
                loss.append(float(p))
                if p>0: logloss.append(math.log10(float(p)))
            else: nonnum_by_col[2]+=1
            if isinstance(w,str): wave_counter[w]+=1
            else: nonnum_by_col[3]+=1
            temp_wave[f'{t}|{w}']+=1
            wave=row[4:1028]
            st=wave_features(wave)
            if st and st['n'] != 1024:
                row_flags.append(('wave_point_count',ridx,st['n']))
            if st:
                pp.append(st['pp']); wave_means.append(st['mean']); wave_stds.append(st['std']); maxdiff.append(st['max_diff']); endpoint.append(st['endpoint_jump'])
            # Expected column type / range checks.
            flags=[]
            if t not in EXPECTED_T: flags.append('temperature_category')
            if is_num(f) and not (50000 <= f <= 500000): flags.append('frequency_outside_50000_500000')
            elif not is_num(f): flags.append('frequency_non_numeric')
            if not is_num(p) or p <= 0: flags.append('loss_nonpositive_or_non_numeric')
            if w not in EXPECTED_W: flags.append('wave_label')
            if st.get('n') != 1024: flags.append('wave_length_or_missing')
            if st and (not all(math.isfinite(st[k]) for k in ['mean','std','min','max','pp','max_diff','endpoint_jump'])): flags.append('wave_nonfinite')
            if flags:
                row_flags.append((ridx,flags,t,f,p,w,st.get('n') if st else 0))
            # Hash complete record for exact duplicates.
            rh=make_hash(row[:1028])
            row_hash_counts[rh]+=1
        # Statistical flags based on row-level robust bounds.
        robust_specs=[('loss',loss),('log10_loss',logloss),('B_pp',pp),('B_mean',wave_means),('B_std',wave_stds),('max_abs_dB',maxdiff),('endpoint_jump',endpoint)]
        robust_bounds={name:iqr_bounds(vals) for name,vals in robust_specs}
        robust_counts={name:0 for name,_ in robust_specs}; robust_examples={name:[] for name,_ in robust_specs}
        # Second pass only if needed to collect row IDs for robust flags; compute cheap descriptors again.
        if loss:
            for ridx,row in enumerate(ws.iter_rows(min_row=2, values_only=True), start=1):
                row=list(row); p=row[2]; st=wave_features(row[4:1028])
                candidates={'loss':float(p) if is_num(p) else None,'log10_loss':math.log10(float(p)) if is_num(p) and p>0 else None,'B_pp':st.get('pp') if st else None,'B_mean':st.get('mean') if st else None,'B_std':st.get('std') if st else None,'max_abs_dB':st.get('max_diff') if st else None,'endpoint_jump':st.get('endpoint_jump') if st else None}
                for name,val in candidates.items():
                    lo,hi=robust_bounds[name]
                    if val is not None and (val<lo or val>hi):
                        robust_counts[name]+=1
                        if len(robust_examples[name])<12: robust_examples[name].append({'row':ridx+1,'value':val})
        exact_dupes=sum(v-1 for v in row_hash_counts.values() if v>1)
        invalid_t=sum(v for k,v in temp_counter.items() if float(k) not in EXPECTED_T)
        outfreq=sum(1 for x in freq if not (50000<=x<=500000))
        nonpos=sum(1 for x in loss if x<=0)
        sheet={
            'title':ws.title,'rows':n,'columns':cols,'headers':headers[:8]+['...']+(headers[-3:] if cols>11 else []),
            'formula_info':formula_info.get(ws.title,{}),
            'missing_total':sum(missing_by_col),'missing_by_first8':{str(i+1):missing_by_col[i] for i in range(min(8,cols))},
            'non_numeric_by_first4':{str(i+1):nonnum_by_col[i] for i in range(4)},
            'temperature':{'counts':dict(temp_counter),'invalid_count':invalid_t},
            'frequency':{'summary':five(freq),'outside_stated_range_count':outfreq,'outside_examples':sorted(set(x for x in freq if not (50000<=x<=500000)))[:20],'unique_count':len(set(freq))},
            'loss':{'summary':five(loss),'log10_summary':five(logloss),'nonpositive_count':nonpos,'zero_count':sum(x==0 for x in loss)},
            'wave_label':{'counts':dict(wave_counter),'invalid_count':sum(v for k,v in wave_counter.items() if k not in EXPECTED_W)},
            'temperature_wave_counts':dict(temp_wave),
            'wave_features':{'B_pp':five(pp),'B_mean':five(wave_means),'B_std':five(wave_stds),'max_abs_dB':five(maxdiff),'endpoint_jump':five(endpoint)},
            'exact_duplicate_rows':exact_dupes,
            'deterministic_row_flags':len(row_flags),
            'robust_iqr_flags':robust_counts,'robust_examples':robust_examples,
            'sample_rows':[]
        }
        # Save a few deterministic examples without bloating output.
        for ridx,row in enumerate(ws.iter_rows(min_row=2,max_row=5,values_only=True), start=2):
            row=list(row); st=wave_features(row[4:1028]); sheet['sample_rows'].append({'row':ridx,'temperature':row[0],'frequency':row[1],'loss':row[2],'wave':row[3],'wave_n':st.get('n') if st else 0,'B_pp':st.get('pp') if st else None})
        result['sheets'].append(sheet)
        result['totals']['duplicate_full_rows'] += exact_dupes
        result['totals']['invalid_temperature'] += invalid_t
        result['totals']['frequency_outside_stated_range'] += outfreq
        result['totals']['nonpositive_loss'] += nonpos
        # Store deterministic flags in CSV later in a compact form, using a fresh limited pass only if present.
        if row_flags:
            for item in row_flags[:200]:
                if len(item)>=7 and isinstance(item[1],list):
                    anomaly_rows.append({'material':material,'row':item[0],'type':'deterministic','flags':';'.join(item[1]),'temperature':item[2],'frequency':item[3],'loss':item[4],'wave':item[5],'wave_n':item[6]})
    wb.close()
    with ANOM.open('w',newline='',encoding='utf-8-sig') as f:
        wr=csv.DictWriter(f,fieldnames=['material','row','type','flags','temperature','frequency','loss','wave','wave_n'])
        wr.writeheader(); wr.writerows(anomaly_rows)
    OUT.write_text(json.dumps(result,ensure_ascii=False,indent=2),encoding='utf-8')
    print('wrote',OUT)
    print('wrote',ANOM)

if __name__=='__main__': audit()
