"""Render figures only from this run's saved physical graph and yearly records."""
import json
import os
from pathlib import Path
RUN=Path(__file__).resolve().parents[1]
os.environ["MPLCONFIGDIR"]=str(RUN/"work/matplotlib")
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.collections import LineCollection

d=json.loads((RUN/"results/primary/design.json").read_text(encoding="utf-8"))
nodes={n["id"]:n for n in d["nodes"]}; out=RUN/"figures"; out.mkdir(exist_ok=True)
fig,ax=plt.subplots(figsize=(13,10),layout="constrained")
colors={"park-primary":"#999999","primary-primary":"#147d65","primary-secondary":"#bb6826"}
for kind,color in colors.items():
    lines=[[(nodes[e["u"]]["x_km"],nodes[e["u"]]["y_km"]),(nodes[e["v"]]["x_km"],nodes[e["v"]]["y_km"])] for e in d["edges"] if e["kind"]==kind]
    ax.add_collection(LineCollection(lines,colors=color,linewidths=.5 if kind=="park-primary" else .9,alpha=.22 if kind=="park-primary" else .7,label=f"{kind} physical tunnels ({len(lines)})"))
for kind,marker,color,size in [("secondary","o","#c65f30",10),("primary","^","#11785a",18),("park","s","#17252a",55)]:
    ns=[n for n in nodes.values() if n["type"]==kind]
    ax.scatter([n["x_km"] for n in ns],[n["y_km"] for n in ns],s=size,marker=marker,c=color,label=f"{kind} ({len(ns)})",zorder=3)
    if kind=="park":
        for n in ns: ax.annotate(n["id"],(n["x_km"],n["y_km"]),xytext=(7,7),textcoords="offset points",fontsize=10)
ax.autoscale(); ax.margins(.12); ax.set_aspect("equal")
ax.set_xlabel("X / km (XLS metres divided by 1000)"); ax.set_ylabel("Y / km (local planar assumption)")
ax.set_title("2017F computed network: 118 primary + 118 secondary stations\n1120 built hypothetical physical tunnels; no engineering constructability claim",fontsize=13)
ax.legend(loc="upper left",fontsize=9,framealpha=.95); ax.grid(alpha=.12)
fig.savefig(out/"primary-network.png",dpi=160); plt.close(fig)

years=json.loads((RUN/"results/q4-annual.json").read_text(encoding="utf-8"))
fig,axes=plt.subplots(2,1,figsize=(10,8),layout="constrained")
x=[r["year"] for r in years]
axes[0].bar(x,[r["annual_work_km"] for r in years],color="#147d65")
axes[0].set_ylabel("Construction work / km"); axes[0].set_title("Eight-year scenario: equal work, incomplete tunnels unavailable")
axes[1].plot(x,[100*r["underground_fraction"] for r in years],"o-",color="#147d65",label="Underground share of original grown freight")
axes[1].plot(x,[100*(1-r["underground_fraction"]) for r in years],"s-",color="#c65f30",label="Surface fallback, including intra-region OD")
axes[1].set_ylim(0,100); axes[1].set_xlabel("Year (source day is t=0)"); axes[1].set_ylabel("Freight share / %")
axes[1].legend(); axes[1].grid(alpha=.2)
fig.savefig(out/"construction-phasing.png",dpi=160); plt.close(fig)
print("Saved two source-coordinate/result-derived figures")
