"""Chapter 10 figures at true print width (4.55 in)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, pandas as pd, numpy as np, pathlib, warnings
from matplotlib.patches import FancyArrowPatch, Circle
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
d=pd.read_csv(D+"ch10_iv_slope.csv")
ctrl="mean_floor_area_m2 + building_age_yr"
def save(n): plt.savefig(f"{n}.png",dpi=320,bbox_inches="tight"); plt.close()

# 10.A the IV diagram, monochrome
fig,ax=plt.subplots(figsize=(W,1.95))
ax.set_xlim(-.04,1.04); ax.set_ylim(-.34,1.12); ax.axis("off")
def node(x,y,t,r=.075,dash=False):
    ax.add_patch(Circle((x,y),r,fill=False,ec=INK,lw=1.1,
                        linestyle="--" if dash else "-"))
    ax.text(x,y,t,ha="center",va="center",fontsize=6.6,color=INK)
def arrow(x1,y1,x2,y2,r1=.075,r2=.075,dash=False):
    dx,dy=x2-x1,y2-y1; L=np.hypot(dx,dy)
    ax.add_patch(FancyArrowPatch((x1+dx/L*r1,y1+dy/L*r1),(x2-dx/L*r2,y2-dy/L*r2),
        arrowstyle="-|>",mutation_scale=8,lw=1.0,color=INK,
        linestyle="--" if dash else "-"))
node(.34,.42,"Z"); node(.58,.42,"X"); node(.86,.42,"Y"); node(.72,.92,"U",dash=True)
arrow(.34,.42,.58,.42); arrow(.58,.42,.86,.42)
arrow(.72,.92,.58,.42); arrow(.72,.92,.86,.42)
ax.text(.46,.49,"relevance",fontsize=5.6,ha="center",style="italic")
ax.text(.72,.49,"the effect",fontsize=5.6,ha="center",style="italic")
ax.text(.72,1.05,"unobserved",fontsize=5.6,ha="center",color=GREY,style="italic")
# excluded path
ax.add_patch(FancyArrowPatch((.36,.34),(.83,.34),arrowstyle="-|>",mutation_scale=8,
    lw=1.0,color=RED,linestyle=":",connectionstyle="arc3,rad=0.30"))
ax.text(.60,-.12,"excluded by assumption",fontsize=5.8,ha="center",color=RED,style="italic")
ax.text(.00,1.06,"Z  terrain slope\nX  transit access\nY  land price\nU  development potential",
        fontsize=5.6,va="top",color=INK,linespacing=1.6)
save("fig10A_iv_diagram")

# 10.1 first stage + reduced form
f1=smf.ols(f"transit_access_index ~ slope_deg_srtm + {ctrl}",d).fit()
fig,ax=plt.subplots(1,2,figsize=(W,1.9))
ax[0].scatter(d.slope_deg_srtm,d.transit_access_index,s=3,color=TEAL,alpha=.35)
b=np.polyfit(d.slope_deg_srtm,d.transit_access_index,1)
xs=np.linspace(d.slope_deg_srtm.min(),d.slope_deg_srtm.max(),20)
ax[0].plot(xs,np.polyval(b,xs),color=INK,lw=1.3)
ax[0].set_xlabel("terrain slope (degrees)",fontsize=6.4)
ax[0].set_ylabel("transit access",fontsize=6.4)
ax[0].set_title(f"first stage:  t = {f1.tvalues['slope_deg_srtm']:.1f}",fontsize=6.8)
ax[1].scatter(d.slope_deg_srtm,d.log_land_price,s=3,color=BLUE,alpha=.35)
b2=np.polyfit(d.slope_deg_srtm,d.log_land_price,1)
ax[1].plot(xs,np.polyval(b2,xs),color=INK,lw=1.3)
ax[1].set_xlabel("terrain slope (degrees)",fontsize=6.4)
ax[1].set_ylabel("log land price",fontsize=6.4)
ax[1].set_title("reduced form",fontsize=6.8)
for a in ax: a.tick_params(labelsize=6.0)
plt.tight_layout(); save("fig10_1_first_stage")

# 10.2 weak instrument simulation
rng=np.random.default_rng(7)
noises=[0,2,4,6,8,12,16,24]; Fs=[];Bs=[]
for nz in noises:
    d2=d.copy(); d2["z"]=d2.slope_deg_srtm+rng.normal(0,nz,len(d2))
    fa=smf.ols(f"transit_access_index ~ z + {ctrl}",d2).fit()
    d2["fit2"]=fa.fittedvalues
    Bs.append(smf.ols(f"log_land_price ~ fit2 + {ctrl}",d2).fit().params["fit2"])
    Fs.append(fa.tvalues["z"]**2)
fig,ax=plt.subplots(figsize=(W,1.9))
ax.semilogx(Fs,Bs,"o-",color=INK,ms=4,lw=1.0)
ax.axhline(.15,color=TEAL,ls="--",lw=1.1); ax.axvline(10,color=RED,ls=":",lw=1.1)
ax.text(8.6,-.20,"F = 10",fontsize=6.0,color=RED,ha="left")
ax.text(620,.20,"truth 0.15",fontsize=6.0,color=TEAL)
ax.set_xlabel("first-stage F statistic (log scale)",fontsize=6.5)
ax.set_ylabel("2SLS estimate",fontsize=6.5)
ax.set_ylim(-.32,.58)
ax.invert_xaxis()
save("fig10_2_weak_instrument")

# 10.3 estimator comparison
ols=smf.ols(f"log_land_price ~ transit_access_index + {ctrl}",d).fit()
import statsmodels.api as sm
Z=sm.add_constant(d[["slope_deg_srtm","mean_floor_area_m2","building_age_yr"]])
X=sm.add_constant(d[["transit_access_index","mean_floor_area_m2","building_age_yr"]])
y=d.log_land_price.values
Xh=Z.values@np.linalg.lstsq(Z.values,X.values,rcond=None)[0]
bb=np.linalg.lstsq(Xh,y,rcond=None)[0]
res=y-X.values@bb; s2=res@res/(len(y)-X.shape[1])
se=np.sqrt(np.diag(s2*np.linalg.inv(Xh.T@Xh)))
fig,ax=plt.subplots(figsize=(W,1.4))
vals=[ols.params["transit_access_index"],bb[1]]; errs=[ols.bse["transit_access_index"],se[1]]
ax.barh([0,1],vals,xerr=[1.96*e for e in errs],color=[RED,TEAL],height=.5,
        error_kw=dict(ecolor=INK,lw=1))
ax.axvline(.15,color=INK,ls="--",lw=1.1)
ax.text(.157,1.42,"truth 0.15",fontsize=6.2)
ax.set_yticks([0,1]); ax.set_yticklabels(["OLS","2SLS"],fontsize=6.8); ax.invert_yaxis()
ax.set_xlabel("coefficient on transit access",fontsize=6.5); ax.set_xlim(0,.55)
save("fig10_3_ols_vs_2sls")
print("ch10 figures done")
