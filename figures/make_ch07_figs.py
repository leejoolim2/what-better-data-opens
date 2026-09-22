"""Chapter 7 figures at true print width (4.55 in)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, pandas as pd, numpy as np, pathlib, warnings
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import statsmodels.formula.api as smf
warnings.filterwarnings("ignore")
W=4.55
INK,TEAL,RED,BLUE,GREY = "#16283C","#0E7C7B","#B3372B","#276DC3","#8A99A6"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":7.2,
 "axes.edgecolor":INK,"axes.labelcolor":INK,"text.color":INK,
 "xtick.color":INK,"ytick.color":INK,"xtick.labelsize":6.6,"ytick.labelsize":6.6,
 "axes.spines.top":False,"axes.spines.right":False,
 "figure.facecolor":"white","savefig.facecolor":"white"})
D=str(pathlib.Path(__file__).resolve().parents[1]/"data")+"/"
d=pd.read_csv(D+"ch07_did_hanoi.csv",parse_dates=["date"])
def save(n): plt.savefig(f"{n}.png",dpi=320,bbox_inches="tight"); plt.close()

# 7.A the double difference, monochrome
fig,ax=plt.subplots(figsize=(W,1.95))
ax.set_xlim(-.05,1.05); ax.set_ylim(-.22,1.08); ax.axis("off")
def cell(x,y,w,h,t,fs=6.2,bold=False,lw=.9):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.008,rounding_size=0.015",
        fc="white",ec=INK,lw=lw))
    ax.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=fs,color=INK,
            weight="bold" if bold else "normal",linespacing=1.35)
def arr(x1,y1,x2,y2,lw=.9):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=7,lw=lw,color=INK))
ax.text(.19,1.00,"before",ha="center",fontsize=6.4,style="italic")
ax.text(.47,1.00,"after",ha="center",fontsize=6.4,style="italic")
ax.text(.005,.72,"treated",fontsize=6.2,style="italic")
ax.text(.005,.36,"control",fontsize=6.2,style="italic")
cell(.16,.62,.18,.24,"2.207"); cell(.38,.62,.18,.24,"2.331")
cell(.16,.26,.18,.24,"2.515"); cell(.38,.26,.18,.24,"2.580")
arr(.34,.74,.38,.74); ax.text(.35,.90,"+0.124",fontsize=6.0,ha="center",color=INK)
arr(.34,.38,.38,.38); ax.text(.35,.14,"+0.065",fontsize=6.0,ha="center",color=INK)
cell(.66,.44,.34,.24,"0.124 − 0.065\n= 0.059",bold=True,lw=1.6)
arr(.56,.74,.66,.60); arr(.56,.38,.66,.52)
ax.text(.83,.30,"the double difference",fontsize=5.8,ha="center",color=GREY,style="italic")
ax.text(.02,-.16,"cell entries are mean log radiance",fontsize=5.6,color=GREY)
save("fig7A_double_difference")

# 7.1 group trends
g=d.groupby(["treated","date"]).log_avg_rad.mean().reset_index()
fig,ax=plt.subplots(figsize=(W,2.0))
for tr,c,ls,lab in [(1,RED,"-","treated (15)"),(0,BLUE,"--","control (25)")]:
    s=g[g.treated==tr]; ax.plot(s.date,s.log_avg_rad,color=c,ls=ls,lw=1.3,label=lab)
ax.axvline(pd.Timestamp("2024-01-01"),color=GREY,ls=":",lw=1.0)
ax.text(pd.Timestamp("2024-02-01"),g.log_avg_rad.min()+.02,"road opens",fontsize=6.0,color=GREY)
ax.set_ylabel("mean log radiance",fontsize=6.6)
ax.legend(fontsize=6.0,frameon=False,loc="upper left")
save("fig7_1_trends")

# 7.2 event study
d["rel"]=d.t-25
ev=d[(d.rel>=-12)&(d.rel<=11)].copy()
terms=[]
for k in range(-12,12):
    if k==-1: continue
    nm=f"L{abs(k)}" if k<0 else f"F{k}"
    ev[nm]=((ev.rel==k)&(ev.treated==1)).astype(int); terms.append(nm)
es=smf.ols("log_avg_rad ~ "+" + ".join(terms)+" + C(shapeID) + C(date)",ev).fit(
    cov_type="cluster",cov_kwds={"groups":ev.shapeID})
ks=list(range(-12,12)); bs=[];se=[]
for k in ks:
    if k==-1: bs.append(0); se.append(0); continue
    nm=f"L{abs(k)}" if k<0 else f"F{k}"
    bs.append(es.params[nm]); se.append(es.bse[nm])
fig,ax=plt.subplots(figsize=(W,2.05))
ax.axvspan(-.5,11.5,color=TEAL,alpha=.07)
ax.errorbar(ks,bs,yerr=[1.96*s for s in se],fmt="o",ms=3,capsize=2,lw=.9,
            color=INK,ecolor=GREY,mfc="white")
ax.axhline(0,color=INK,lw=.7); ax.axvline(-.5,color=RED,ls=":",lw=1.0)
ax.plot(-1,0,"o",ms=4,color=RED)
ax.set_xlabel("months relative to opening",fontsize=6.6)
ax.set_ylabel("coefficient",fontsize=6.6)
ax.text(-11.5,max(bs)*.92,"reference: −1",fontsize=5.8,color=RED)
save("fig7_2_event_study")
print("ch07 figures done")
