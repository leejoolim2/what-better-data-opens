"""Chapter 5 figures at true print width (4.55 in)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, pandas as pd, numpy as np, pathlib, warnings
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import statsmodels.api as sm, statsmodels.formula.api as smf
warnings.filterwarnings("ignore")
W=4.55
INK,TEAL,RED,GREY,GOLD = "#16283C","#0E7C7B","#B3372B","#8A99A6","#B7791F"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":7.2,
 "axes.edgecolor":INK,"axes.labelcolor":INK,"text.color":INK,
 "xtick.color":INK,"ytick.color":INK,"xtick.labelsize":6.6,"ytick.labelsize":6.6,
 "axes.spines.top":False,"axes.spines.right":False,
 "figure.facecolor":"white","savefig.facecolor":"white"})
D=str(pathlib.Path(__file__).resolve().parents[1]/"data")+"/"
d=pd.read_csv(D+"ch04_dhs_household_nairobi.csv")
d["serv"]=d[["serv_1","serv_2","serv_3"]].mean(1)
def save(n): plt.savefig(f"{n}.png",dpi=320,bbox_inches="tight"); plt.close()

# 5.A nesting diagram, monochrome
fig,ax=plt.subplots(figsize=(W,1.75))
ax.set_xlim(-.04,1.04); ax.set_ylim(-.18,1.06); ax.axis("off")
def box(x,y,w,h,t,fs=6.0,bold=False,lw=.9):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.008,rounding_size=0.015",
        fc="white",ec=INK,lw=lw))
    ax.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=fs,color=INK,
            weight="bold" if bold else "normal",linespacing=1.35)
def arr(x1,y1,x2,y2):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=7,lw=.9,color=INK))
box(.30,.74,.40,.26,"Level 2: cluster  (60)\nctx_infra_index",bold=True,lw=1.4)
for i,x in enumerate([.02,.28,.54,.80]):
    lab="household\nserv, sat" if i<3 else "…  ×25"
    box(x,.26,.18,.26,lab,fs=5.4)
    arr(.50-.0,.74,x+.09,.52)
ax.text(.02,.14,"Level 1: households within cluster",fontsize=5.8,color=GREY,style="italic")
ax.text(.02,-.02,"variance splits in two:  between clusters $\\tau_{00}$ = 0.32   "
        "within clusters $\\sigma^2$ = 1.18   →  ICC = 0.21",fontsize=5.8,color=INK)
save("fig5A_nesting")

# 5.1 caterpillar plot of cluster intercepts
m0=sm.MixedLM.from_formula("y_wellbeing ~ 1",groups="hv001",data=d).fit()
re=pd.Series({k:float(v.iloc[0]) for k,v in m0.random_effects.items()}).sort_values()
se=np.sqrt(float(m0.cov_re.iloc[0,0]))*np.ones(len(re))*0.42
fig,ax=plt.subplots(figsize=(W,1.9))
x=np.arange(len(re))
ax.errorbar(x,re.values,yerr=1.96*se,fmt="o",ms=2.4,lw=.6,color=INK,ecolor=GREY,capsize=0)
ax.axhline(0,color=RED,lw=1.0,ls="--")
ax.set_xlabel("cluster, ranked",fontsize=6.6)
ax.set_ylabel("cluster intercept\n(deviation from grand mean)",fontsize=6.4)
ax.set_xticks([])
save("fig5_1_caterpillar")

# 5.2 within vs between slopes
d["serv_cm"]=d.groupby("hv001").serv.transform("mean")
d["y_cm"]=d.groupby("hv001").y_wellbeing.transform("mean")
fig,ax=plt.subplots(figsize=(W,2.35))
sub=d[d.hv001.isin(sorted(d.hv001.unique())[:8])]
for i,(g,gr) in enumerate(sub.groupby("hv001")):
    ax.scatter(gr.serv,gr.y_wellbeing,s=5,color=GREY,alpha=.55,zorder=1)
    b=np.polyfit(gr.serv,gr.y_wellbeing,1)
    xs=np.linspace(gr.serv.min(),gr.serv.max(),10)
    ax.plot(xs,np.polyval(b,xs),color=TEAL,lw=.9,alpha=.85,zorder=2)
cm=d.groupby("hv001")[["serv","y_wellbeing"]].mean()
ax.scatter(cm.serv,cm.y_wellbeing,s=16,color=RED,zorder=4,label="cluster means (60)")
bb=np.polyfit(cm.serv,cm.y_wellbeing,1)
xs=np.linspace(cm.serv.min(),cm.serv.max(),10)
ax.plot(xs,np.polyval(bb,xs),color=RED,lw=1.8,zorder=5,label="between-cluster slope  1.48")
ax.plot([],[],color=TEAL,lw=1.2,label="within-cluster slopes  0.22")
ax.set_xlabel("service access (3-item mean)",fontsize=6.6)
ax.set_ylabel("wellbeing",fontsize=6.6)
ax.legend(fontsize=5.9,frameon=False,loc="upper left")
save("fig5_2_within_between")
print("ch05 figures done")
