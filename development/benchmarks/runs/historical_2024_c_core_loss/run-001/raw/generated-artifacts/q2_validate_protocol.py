"""Q2: validate temperature-corrected Steinmetz models under several splits."""
from __future__ import annotations

import csv, json, math, time
from pathlib import Path
import numpy as np
import openpyxl
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score
from sklearn.model_selection import KFold, GroupKFold, train_test_split

BASE=Path(r'C:\Users\aaa\Desktop\text\pressure-test')
OUT=Path(r'C:\Users\aaa\Desktop\test\outputs\q2_validation')
F0=100000.0; B0=0.1; T0=25.0; TR=65.0

def feat(row):
    t,f,p,w=row[:4]; b=np.asarray(row[4:1028],dtype=float)
    bm=(float(b.max())-float(b.min()))/2
    return float(t),float(f),float(p),bm

def load():
    wb=openpyxl.load_workbook(BASE/'附件一（训练集）.xlsx',read_only=True,data_only=True)
    ws=wb['材料1']; out=[]
    for i,row in enumerate(ws.iter_rows(min_row=2,values_only=True),start=2):
        t,f,p,b=feat(list(row)); w=list(row)[3]
        if w=='正弦波': out.append({'row':i,'T':t,'f':f,'P':p,'Bm':b})
    wb.close(); return out

def design(rows, kind):
    z=[]
    for r in rows:
        lf=math.log(r['f']/F0); lb=math.log(r['Bm']/B0); th=(r['T']-T0)/TR
        if kind=='SE': x=[1,lf,lb]
        elif kind=='T1': x=[1,lf,lb,th]
        elif kind=='T2': x=[1,lf,lb,th,th*th]
        elif kind=='TI': x=[1,lf,lb,th,th*lf,th*lb]
        else: raise ValueError(kind)
        z.append(x)
    return np.asarray(z,float)

def target(rows): return np.log(np.asarray([r['P'] for r in rows],float))

def predict_metrics(model,X,y,rows):
    yp=model.predict(X); p=np.exp(yp); actual=np.exp(y)
    smape=float(np.mean(2*np.abs(p-actual)/(np.abs(p)+np.abs(actual))))
    return {'rmse_log':float(np.sqrt(np.mean((yp-y)**2))),'mae':float(mean_absolute_error(actual,p)),'rmse':float(np.sqrt(mean_squared_error(actual,p))),'smape':smape,'r2_log':float(r2_score(y,yp)),'median_ape':float(np.median(np.abs(p-actual)/actual))}

def fit_eval(train,valid,kind):
    model=LinearRegression(fit_intercept=False)
    model.fit(design(train,kind),target(train))
    return predict_metrics(model,design(valid,kind),target(valid),valid),model

def evaluate_split(rows, train_idx, valid_idx, label):
    train=[rows[i] for i in train_idx]; valid=[rows[i] for i in valid_idx]
    result={'split':label,'train_n':len(train),'valid_n':len(valid),'models':{}}
    for kind in ['SE','T1','T2','TI']:
        m,model=fit_eval(train,valid,kind)
        result['models'][kind]=m|{'coefficients':model.coef_.tolist()}
    return result

def bootstrap(rows, n=300, seed=2024):
    rng=np.random.default_rng(seed); out={k:[] for k in ['SE','T1','T2','TI']}; gains=[]
    N=len(rows)
    for _ in range(n):
        idx=rng.integers(0,N,size=N); oob=np.setdiff1d(np.arange(N),np.unique(idx))
        if len(oob)<30: continue
        train=[rows[i] for i in idx]; valid=[rows[i] for i in oob]
        mets={}
        for kind in out:
            mm,_=fit_eval(train,valid,kind); out[kind].append(mm['rmse_log']); mets[kind]=mm['rmse_log']
        gains.append(mets['SE']-mets['T2'])
    def summ(a):
        a=np.asarray(a); return {'n':int(len(a)),'mean':float(a.mean()),'q025':float(np.quantile(a,.025)),'median':float(np.median(a)),'q975':float(np.quantile(a,.975))}
    return {'rmse_log':{k:summ(v) for k,v in out.items()},'SE_minus_T2_rmse_log':summ(gains),'T2_better_fraction':float(np.mean(np.asarray(gains)>0))}

def main():
    OUT.mkdir(parents=True,exist_ok=True)
    rows=load(); N=len(rows); y=np.asarray([r['P'] for r in rows])
    # Confirm whether there is a real time field; there is only Excel row order.
    frequencies=np.asarray([r['f'] for r in rows]); temps=np.asarray([r['T'] for r in rows]); bms=np.asarray([r['Bm'] for r in rows])
    idx=np.arange(N)
    report={'data':{'n':N,'excel_row_min':rows[0]['row'],'excel_row_max':rows[-1]['row'],'has_timestamp':False,'sort_order_note':'Rows are in workbook order; no timestamp or elapsed-time column is provided.','temperature_counts':{str(t):int(np.sum(temps==t)) for t in sorted(set(temps))},'frequency_min':float(frequencies.min()),'frequency_max':float(frequencies.max()),'Bm_min':float(bms.min()),'Bm_max':float(bms.max())},'splits':[]}
    tr,va=train_test_split(idx,test_size=.2,random_state=2024)
    report['splits'].append(evaluate_split(rows,tr,va,'random_80_20'))
    # ordinary shuffled 5-fold, and grouped frequency bins (quantile bins).
    kf=KFold(n_splits=5,shuffle=True,random_state=2024)
    for fold,(tr,va) in enumerate(kf.split(idx),1): report['splits'].append(evaluate_split(rows,tr,va,f'random_fold_{fold}'))
    for temp in sorted(set(temps)):
        va=np.where(temps==temp)[0]; tr=np.where(temps!=temp)[0]
        report['splits'].append(evaluate_split(rows,tr,va,f'leave_temperature_{int(temp)}'))
    freq_bins=np.digitize(frequencies,np.quantile(frequencies,[.2,.4,.6,.8]),right=True)
    bm_bins=np.digitize(bms,np.quantile(bms,[.2,.4,.6,.8]),right=True)
    for name,groups in [('frequency_quantile',freq_bins),('Bm_quantile',bm_bins)]:
        for g in range(5):
            va=np.where(groups==g)[0]; tr=np.where(groups!=g)[0]
            report['splits'].append(evaluate_split(rows,tr,va,f'leave_{name}_{g+1}'))
    # Row-order split is a diagnostic only, not a true time split.
    cut=int(.8*N); report['splits'].append(evaluate_split(rows,idx[:cut],idx[cut:],'row_order_80_20_diagnostic'))
    report['bootstrap']=bootstrap(rows)
    # Perturb T, f, Bm by small relative noise and refit/evaluate on the same random holdout.
    rng=np.random.default_rng(2024); sensitivity=[]
    base_tr,base_va=train_test_split(idx,test_size=.2,random_state=2024)
    for name,noise in [('temperature_1C',('T',1.0)),('frequency_1pct',('f',.01)),('Bm_1pct',('Bm',.01))]:
        rr=[dict(r) for r in rows]
        key,scale=noise
        for r in rr:
            if key=='T': r[key]+=rng.normal(0,scale)
            else: r[key]*=(1+rng.normal(0,scale))
        rec=evaluate_split(rr,base_tr,base_va,'perturbed')
        sensitivity.append({'perturbation':name,'metrics':{k:{m:v for m,v in z.items() if m in ['rmse_log','smape','r2_log']} for k,z in rec['models'].items()}})
    report['sensitivity']=sensitivity
    (OUT/'q2_validation.json').write_text(json.dumps(report,ensure_ascii=False,indent=2),encoding='utf-8')
    with (OUT/'q2_validation_summary.csv').open('w',newline='',encoding='utf-8-sig') as f:
        w=csv.writer(f); w.writerow(['split','model','rmse_log','mae','rmse','smape','r2_log','median_ape'])
        for s in report['splits']:
            for k,m in s['models'].items(): w.writerow([s['split'],k,m['rmse_log'],m['mae'],m['rmse'],m['smape'],m['r2_log'],m['median_ape']])
    print(json.dumps(report,ensure_ascii=False,indent=2))

if __name__=='__main__': main()
