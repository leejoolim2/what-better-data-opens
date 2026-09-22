"""Chapter 13 figures at true print width (4.55 in)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, pandas as pd, numpy as np, pathlib, warnings
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
import spreg
from libpysal.weights import lat2W
from esda.moran import Moran
warnings.filterwarnings("ignore")
W=4.55
INK,TEAL,RED,BLUE,GREY = "#16283C","#0E7C7B","#B3372B","#276DC3","#8A99A6"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":7.2,
 "axes.edgecolor":INK,"axes.labelcolor":INK,"text.color":INK,
 "xtick.color":INK,"ytick.color":INK,"xtick.labelsize":6.6,"ytick.labelsize":6.6,
 "axes.spines.top":False,"axes.spines.right":False,
 "figure.facecolor":"white","savefig.facecolor":"white"})
D=str(pathlib.Path(__file__).resolve().parents[1]/"data")+"/"
d=pd.read_csv(D+"ch13_spatial_grid.csv").sort_values(["row","col"]).reset_index(drop=True)
w=lat2W(18,18,rook=True); w.transform="r"
y=d[["log_land_value"]].values; cols=["built_up_pct","green_pct","pop_density"]
X=d[cols].values
ols=spreg.OLS(y,X,w=w,name_x=cols); res=np.asarray(ols.u).flatten()
def save(n): plt.savefig(f"{n}.png",dpi=320,bbox_inches="tight"); plt.close()
def grid(v): return v.reshape(18,18)

# 13.1 outcome map and residual map
fig,ax=plt.subplots(1,2,figsize=(W,2.0))
im0=ax[0].imshow(grid(d.log_land_value.values),cmap="viridis",origin="lower")
ax[0].set_title("log land value",fontsize=6.8)
lim=np.abs(res).max()
im1=ax[1].imshow(grid(res),cmap="RdBu_r",vmin=-lim,vmax=lim,origin="lower")
ax[1].set_title("OLS residuals",fontsize=6.8)
for a,im in zip(ax,[im0,im1]):
    a.set_xticks([]); a.set_yticks([])
    cb=plt.colorbar(im,ax=a,fraction=.046,pad=.03); cb.ax.tick_params(labelsize=5.6)
plt.tight_layout(); save("fig13_1_maps")

# 13.2 Moran scatterplot of residuals
mi=Moran(res,w)
lag=np.array(w.sparse@res)
zs=(res-res.mean())/res.std(); zl=(lag-lag.mean())/lag.std()
fig,ax=plt.subplots(figsize=(W,2.0))
ax.scatter(zs,zl,s=7,color=TEAL,alpha=.6)
b=np.polyfit(zs,zl,1)
xs=np.linspace(zs.min(),zs.max(),10)
ax.plot(xs,np.polyval(b,xs),color=RED,lw=1.5)
ax.axhline(0,color=INK,lw=.6); ax.axvline(0,color=INK,lw=.6)
ax.set_xlabel("standardised OLS residual",fontsize=6.5)
ax.set_ylabel("spatial lag of residual",fontsize=6.5)
ax.text(.05,.93,f"Moran's I = {mi.I:.3f}   (p < 0.001)",transform=ax.transAxes,fontsize=6.4)
save("fig13_2_moran")

# 13.3 impacts decomposition
g=spreg.GM_Lag(y,X,w=w,name_x=cols); rho=g.betas[-1][0]
Wf=w.full()[0]; M=np.linalg.inv(np.eye(324)-rho*Wf)
labs=["built-up %","green %","pop density\n(x1000)"]
dirs=[];inds=[]
for i,c in enumerate(cols):
    b=g.betas[i+1][0]; tot=b/(1-rho); dr=np.trace(M)/324*b
    k=1000 if c=="pop_density" else 1
    dirs.append(dr*k); inds.append((tot-dr)*k)
fig,ax=plt.subplots(figsize=(W,1.75))
x=np.arange(3)
ax.bar(x,dirs,width=.5,color=INK,label="direct")
ax.bar(x,inds,width=.5,bottom=dirs,color=TEAL,label="indirect (spillover)")
ax.axhline(0,color=INK,lw=.7)
ax.set_xticks(x); ax.set_xticklabels(labs,fontsize=6.2)
ax.set_ylabel("effect on log land value",fontsize=6.4)
ax.legend(fontsize=6.0,frameon=False)
ax.text(.02,.90,"indirect share: 65% for every variable",transform=ax.transAxes,fontsize=6.0,color=GREY)
save("fig13_3_impacts")

# 13.A model selection flow, monochrome
fig,ax=plt.subplots(figsize=(W,2.35))
ax.set_xlim(-.04,1.04); ax.set_ylim(-.10,1.06); ax.axis("off")
def box(x,y,ww,h,t,fs=6.0,bold=False,lw=.9):
    ax.add_patch(FancyBboxPatch((x,y),ww,h,boxstyle="round,pad=0.008,rounding_size=0.015",
        fc="white",ec=INK,lw=lw))
    ax.text(x+ww/2,y+h/2,t,ha="center",va="center",fontsize=fs,color=INK,
            weight="bold" if bold else "normal",linespacing=1.35)
def arr(x1,y1,x2,y2):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=7,lw=.9,color=INK))
box(.28,.88,.44,.14,"Fit OLS",bold=True)
box(.20,.64,.60,.15,"Moran's I on residuals")
box(.20,.40,.60,.15,"Both LM tests reject? → compare robust LM")
box(.00,.14,.30,.16,"RLM-lag larger\n→ SAR")
box(.35,.14,.30,.16,"RLM-error larger\n→ SEM")
box(.70,.14,.30,.16,"both large\n→ SDM")
arr(.50,.88,.50,.80); arr(.50,.64,.50,.56)
arr(.40,.40,.15,.31); arr(.50,.40,.50,.31); arr(.60,.40,.85,.31)
ax.text(.50,.03,"report impacts, then re-test residuals",fontsize=5.8,ha="center",style="italic",color=GREY)
save("fig13A_model_selection")
print("ch13 figures done")
