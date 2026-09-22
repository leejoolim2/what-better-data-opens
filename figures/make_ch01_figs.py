"""Chapter 1 figures at true print width (4.55 in text block)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, pandas as pd, numpy as np, pathlib
from matplotlib.patches import FancyArrowPatch, Circle
import statsmodels.formula.api as smf, warnings
warnings.filterwarnings("ignore")

W = 4.55
INK,TEAL,RED,BLUE,GREY,GOLD = "#16283C","#0E7C7B","#B3372B","#276DC3","#8A99A6","#B7791F"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":7.2,
    "axes.edgecolor":INK,"axes.labelcolor":INK,"text.color":INK,
    "xtick.color":INK,"ytick.color":INK,"xtick.labelsize":6.6,"ytick.labelsize":6.6,
    "axes.spines.top":False,"axes.spines.right":False,
    "figure.facecolor":"white","savefig.facecolor":"white"})
D = str(pathlib.Path(__file__).resolve().parents[1] / "data") + "/"
d = pd.read_csv(D+"ch01_identification.csv")
def save(n): plt.savefig(f"{n}.png", dpi=320, bbox_inches="tight"); plt.close()

# ── FIG 1.A  three DAGs, monochrome ─────────────────────────────
def node(ax,x,y,t,r=.11):
    ax.add_patch(Circle((x,y),r,fill=False,ec=INK,lw=1.1))
    ax.text(x,y,t,ha="center",va="center",fontsize=8,color=INK)
def arrow(ax,x1,y1,x2,y2,r1=.11,r2=.11):
    dx,dy=x2-x1,y2-y1; L=np.hypot(dx,dy)
    x1a,y1a = x1+dx/L*r1, y1+dy/L*r1
    x2a,y2a = x2-dx/L*r2, y2-dy/L*r2
    ax.add_patch(FancyArrowPatch((x1a,y1a),(x2a,y2a),arrowstyle="-|>",
        mutation_scale=9,lw=1.1,color=INK))

fig,axs=plt.subplots(1,3,figsize=(W,1.85))
titles=["Confounder","Mediator","Collider"]
for ax,ti in zip(axs,titles):
    ax.set_xlim(0,1); ax.set_ylim(0,1); ax.axis("off")
    ax.set_title(ti,fontsize=7.6,pad=3)

ax=axs[0]
node(ax,.5,.85,"C"); node(ax,.15,.15,"X"); node(ax,.85,.15,"Y")
arrow(ax,.5,.85,.15,.15); arrow(ax,.5,.85,.85,.15); arrow(ax,.15,.15,.85,.15)
ax.text(.5,-.02,"control C",ha="center",fontsize=6.2,style="italic")

ax=axs[1]
node(ax,.15,.15,"X"); node(ax,.5,.85,"M"); node(ax,.85,.15,"Y")
arrow(ax,.15,.15,.5,.85); arrow(ax,.5,.85,.85,.15)
ax.text(.5,-.02,"do not control M",ha="center",fontsize=6.2,style="italic")

ax=axs[2]
node(ax,.15,.85,"X"); node(ax,.85,.85,"Y"); node(ax,.5,.15,"K")
arrow(ax,.15,.85,.5,.15); arrow(ax,.85,.85,.5,.15)
ax.text(.5,-.02,"never control K",ha="center",fontsize=6.2,style="italic")

plt.tight_layout(); save("fig1A_three_dags")

# ── FIG 1.1  balance dot-plot ────────────────────────────────────
def smd(df,t,v):
    a=df[df[t]==1][v]; b=df[df[t]==0][v]
    return (a.mean()-b.mean())/np.sqrt((a.var()+b.var())/2)
vars_=["prior_footfall","floor_area_m2","dist_market_m"]
labels=["prior footfall","floor area","distance to market"]
obs=[smd(d,"program",v) for v in vars_]
rct=[smd(d,"program_rct",v) for v in vars_]

fig,ax=plt.subplots(figsize=(W,1.9))
y=np.arange(len(vars_))
ax.scatter(obs,y,s=44,color=RED,zorder=3,label="observational")
ax.scatter(rct,y,s=44,facecolor="white",edgecolor=TEAL,linewidth=1.4,zorder=3,label="randomised")
for yi,o,r in zip(y,obs,rct):
    ax.plot([o,r],[yi,yi],color=GREY,lw=.8,zorder=1)
ax.axvline(0,color=INK,lw=.7)
ax.axvspan(-.1,.1,color=GREY,alpha=.15)
ax.set_yticks(y); ax.set_yticklabels(labels,fontsize=6.8)
ax.set_xlabel("standardised mean difference",fontsize=6.6)
ax.legend(fontsize=6.2,frameon=False,loc="lower right")
ax.invert_yaxis()
save("fig1_1_balance")

# ── FIG 1.2  estimates vs truth ─────────────────────────────────
adj = smf.ols("sales_growth_pct~program+prior_footfall+floor_area_m2+dist_market_m", d).fit()
naive = d[d.program==1].sales_growth_pct.mean() - d[d.program==0].sales_growth_pct.mean()
rct = smf.ols("sales_growth_rct_pct~program_rct", d).fit().params["program_rct"]
names=["naive\n(observational)","adjusted\n(observational)","randomised\n(no adjustment)"]
vals=[naive, adj.params["program"], rct]
cols=[RED,TEAL,TEAL]
fig,ax=plt.subplots(figsize=(W,1.7))
ax.barh(range(3),vals,color=cols,height=.55)
ax.axvline(3.0,color=INK,ls="--",lw=1.1)
ax.text(3.08,2.55,"planted truth = 3.0",fontsize=6.2)
ax.set_yticks(range(3)); ax.set_yticklabels(names,fontsize=6.6); ax.invert_yaxis()
ax.set_xlabel("estimated effect (percentage points)",fontsize=6.6)
save("fig1_2_estimates")
print("ch01 figures done")
