"""Create traceable PNGs from the already-run CSV outputs."""
from pathlib import Path
import csv, json
import matplotlib.pyplot as plt

RUN=Path(__file__).resolve().parents[1]
OUT=RUN/'outputs'; FIG=RUN/'results/figures'; FIG.mkdir(parents=True,exist_ok=True)

def rows(name):
    with (OUT/name).open(encoding='utf-8',newline='') as f: return list(csv.DictReader(f))

q=rows('q2-time-curves.csv')
fig,ax=plt.subplots(figsize=(8,4.8))
for rho,color in [('0.5','#b42318'),('0.05','#1769aa')]:
    z=[r for r in q if r['rho']==rho]
    ax.plot([float(r['time_s']) for r in z],[float(r['mechanism_gamma']) for r in z],label=f'rho={rho}',color=color,lw=2)
ax.axhline(.03,color='#333333',ls='--',lw=1,label='requirement gamma=0.03')
ax.set(xlabel='time t (s)',ylabel='reflected/direct power ratio gamma',title='2011B Q2: finite-area multi-reflection model')
ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(FIG/'q2-gamma-vs-time.png',dpi=180);plt.close(fig)

o=rows('q2-order-convergence.csv')
fig,ax=plt.subplots(figsize=(8,4.8))
for rho,color in [('0.5','#b42318'),('0.05','#1769aa')]:
    z=[r for r in o if r['rho']==rho and r['time_s']=='2.0']
    ax.plot([int(r['max_bounces']) for r in z],[float(r['gamma']) for r in z],marker='o',label=f'rho={rho}',color=color)
ax.axhline(.03,color='#333333',ls='--',lw=1,label='requirement gamma=0.03')
ax.set(xlabel='maximum reflection order K',ylabel='gamma at t=2 s',title='Numerical convergence by reflection order')
ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(FIG/'q2-order-convergence.png',dpi=180);plt.close(fig)

e=json.loads((OUT/'q2-extrema.json').read_text(encoding='utf-8'))
fig,ax=plt.subplots(figsize=(7,4.5))
for r,color in [(e[0],'#b42318'),(e[1],'#1769aa')]:
    ax.errorbar([r['rho']],[r['grid161_min']],yerr=[[r['grid161_min']-r['grid161_min']],[r['grid161_max']-r['grid161_min']]],fmt='o',capsize=4,color=color,label=f"rho={r['rho']}")
ax.axhline(.03,color='#333333',ls='--',lw=1,label='requirement gamma=0.03')
ax.set(xlabel='normal reflectivity rho (dimensionless)',ylabel='gamma range over 0 <= t <= 4 s',title='Requirement margin under the two given materials')
ax.grid(alpha=.25);ax.legend();fig.tight_layout();fig.savefig(FIG/'q2-requirement-margin.png',dpi=180);plt.close(fig)

print('Wrote:',*[str(p) for p in sorted(FIG.glob('*.png'))],sep='\n')
