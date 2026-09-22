"""Chapter 4 figures at true print width (4.55 in)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, pandas as pd, numpy as np, pathlib, warnings
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Ellipse
import statsmodels.formula.api as smf
warnings.filterwarnings("ignore")
W=4.55
INK,TEAL,RED,GREY = "#16283C","#0E7C7B","#B3372B","#8A99A6"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":7.2,
 "axes.edgecolor":INK,"axes.labelcolor":INK,"text.color":INK,
 "xtick.color":INK,"ytick.color":INK,"xtick.labelsize":6.6,"ytick.labelsize":6.6,
 "axes.spines.top":False,"axes.spines.right":False,
 "figure.facecolor":"white","savefig.facecolor":"white"})
D=str(pathlib.Path(__file__).resolve().parents[1]/"data")+"/"
d=pd.read_csv(D+"ch04_dhs_household_nairobi.csv")
S=["serv_1","serv_2","serv_3"]; T=["sat_1","sat_2","sat_3"]
def save(n): plt.savefig(f"{n}.png",dpi=320,bbox_inches="tight"); plt.close()

# 4.A measurement model, monochrome
fig,ax=plt.subplots(figsize=(W,2.15))
ax.set_xlim(-.04,1.04); ax.set_ylim(-.14,1.08); ax.axis("off")
def rect(x,y,w,h,t,fs=6.0):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.008,rounding_size=0.015",
        fc="white",ec=INK,lw=.9))
    ax.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=fs,color=INK)
def oval(x,y,t):
    ax.add_patch(Ellipse((x,y),.22,.34,fill=False,ec=INK,lw=1.4))
    ax.text(x,y,t,ha="center",va="center",fontsize=6.2,color=INK,weight="bold")
def arrow(x1,y1,x2,y2,lw=.9):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=7,
        lw=lw,color=INK))
ys=[.88,.55,.22]
# reflective: latent -> indicators
for y,l in zip(ys,[".85",".84",".84"]):
    rect(.00,y-.09,.19,.18,f"serv_{ys.index(y)+1}")
    arrow(.19,.55,.20,y) if False else None
for i,(y,l) in enumerate(zip(ys,[".85",".84",".84"])):
    arrow(.25,.55,.195,y)
    ax.text(.245,(y+.55)/2+(.03 if y!=.55 else .05),l,fontsize=5.4,color=INK,ha="right")
oval(.36,.55,"Service\naccess")
for i,(y,l) in enumerate(zip(ys,[".87",".86",".85"])):
    rect(.81,y-.09,.19,.18,f"sat_{i+1}")
    arrow(.77,.55,.805,y)
    ax.text(.757,(y+.55)/2+(.03 if y!=.55 else .05),l,fontsize=5.4,color=INK,ha="left")
oval(.66,.55,"Satis-\nfaction")
arrow(.475,.55,.545,.55,lw=1.7)
ax.text(.51,.63,"0.41",fontsize=6.8,ha="center",weight="bold",color=INK)
ax.text(.51,.28,"structural path",fontsize=5.6,ha="center",color=GREY,style="italic")
ax.text(.00,-.11,"squares = observed items    ovals = latent constructs    "
        "arrows = reflective loadings",fontsize=5.4,color=GREY)
save("fig4A_measurement_model")

# 4.1 attenuation by indicator count
bs=[]
for k in (1,2,3):
    d["sm"]=d[S[:k]].mean(1); d["tm"]=d[T[:k]].mean(1)
    bs.append(smf.ols("tm~sm",d).fit().params["sm"])
fig,ax=plt.subplots(figsize=(W,1.85))
ax.bar(["1 item","2 items","3 items"],bs,color=[RED,GREY,TEAL],width=.5)
ax.axhline(.42,color=INK,ls="--",lw=1.1)
ax.text(2.42,.428,"truth 0.42",fontsize=6.2,ha="right")
for i,b in enumerate(bs):
    ax.text(i,b+.012,f"{b:.3f}\n({(b/.42-1)*100:+.0f}%)",ha="center",fontsize=6.2)
ax.set_ylim(0,.50); ax.set_ylabel("estimated path coefficient",fontsize=6.6)
save("fig4_1_attenuation")
print("ch04 figures done")
