"""Chapter 12 figures at true print width (4.55 in)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, pandas as pd, numpy as np, pathlib, warnings
from scipy.optimize import minimize
warnings.filterwarnings("ignore")
W=4.55
INK,TEAL,RED,BLUE,GREY = "#16283C","#0E7C7B","#B3372B","#276DC3","#8A99A6"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":7.2,
 "axes.edgecolor":INK,"axes.labelcolor":INK,"text.color":INK,
 "xtick.color":INK,"ytick.color":INK,"xtick.labelsize":6.6,"ytick.labelsize":6.6,
 "axes.spines.top":False,"axes.spines.right":False,
 "figure.facecolor":"white","savefig.facecolor":"white"})
D=str(pathlib.Path(__file__).resolve().parents[1]/"data")+"/"
d=pd.read_csv(D+"ch12_scm_cities.csv"); T,TY="CITY-07",2015
def save(n): plt.savefig(f"{n}.png",dpi=320,bbox_inches="tight"); plt.close()
pre=d[d.year<TY]; w=pre.pivot(index="year",columns="city_id",values="transit_share_pct")
full=d.pivot(index="year",columns="city_id",values="transit_share_pct"); yrs=full.index.values
def fit(y,X):
    n=X.shape[1]
    r=minimize(lambda v:np.mean((y-X@v)**2),np.repeat(1/n,n),method="SLSQP",
        bounds=[(0,1)]*n,constraints={"type":"eq","fun":lambda v:v.sum()-1},
        options={"maxiter":1500,"ftol":1e-14})
    return r.x
don=[c for c in w.columns if c!=T]
wts=fit(w[T].values,w[don].values); synth=full[don].values@wts; gap=full[T].values-synth

# 12.1 paths: treated, synthetic, donor mean
fig,ax=plt.subplots(figsize=(W,2.1))
ax.plot(yrs,full[T].values,color=RED,lw=1.6,label="CITY-07 (treated)")
ax.plot(yrs,synth,color=INK,lw=1.5,ls="--",label="synthetic CITY-07")
ax.plot(yrs,full[don].values.mean(1),color=GREY,lw=1.1,ls=":",label="donor mean (29)")
ax.axvline(TY,color=GREY,ls=":",lw=1.0)
ax.text(TY+.3,full[T].min()+1,"levy adopted",fontsize=6.0,color=GREY)
ax.set_ylabel("transit share (%)",fontsize=6.6)
ax.legend(fontsize=5.9,frameon=False,loc="upper left")
save("fig12_1_paths")

# 12.2 gap plot
fig,ax=plt.subplots(figsize=(W,1.8))
ax.plot(yrs,gap,color=TEAL,lw=1.6)
true=[0 if y<TY else min(1.2*(y-TY+1),9.0) for y in yrs]
ax.plot(yrs,true,color=INK,lw=1.1,ls="--",label="true effect")
ax.axhline(0,color=INK,lw=.7); ax.axvline(TY,color=GREY,ls=":",lw=1.0)
ax.set_ylabel("gap: actual − synthetic",fontsize=6.5)
ax.legend(fontsize=5.9,frameon=False,loc="upper left")
save("fig12_2_gap")

# 12.3 placebo: all cities' gaps
fig,ax=plt.subplots(figsize=(W,2.0))
ratios={}
for c in full.columns:
    dn=[x for x in full.columns if x!=c]
    wc=fit(w[c].values,w[dn].values)
    g=full[c].values-full[dn].values@wc
    pr=np.sqrt(np.mean(g[yrs<TY]**2)); po=np.sqrt(np.mean(g[yrs>=TY]**2))
    ratios[c]=po/pr if pr>0 else np.nan
    if c!=T: ax.plot(yrs,g,color=GREY,lw=.6,alpha=.45)
ax.plot(yrs,gap,color=RED,lw=1.8,label="CITY-07")
ax.axhline(0,color=INK,lw=.7); ax.axvline(TY,color=GREY,ls=":",lw=1.0)
ax.set_ylabel("gap",fontsize=6.5); ax.legend(fontsize=6.0,frameon=False,loc="upper left")
ax.set_title("placebo: the same analysis run on every city",fontsize=6.8,loc="left")
save("fig12_3_placebo")

# 12.4 RMSPE ratio ranking
rk=pd.Series(ratios).sort_values(ascending=False)
fig,ax=plt.subplots(figsize=(W,1.7))
cols=[RED if c==T else GREY for c in rk.index]
ax.bar(range(len(rk)),rk.values,color=cols,width=.75)
ax.set_xticks([]); ax.set_xlabel("cities, ranked",fontsize=6.5)
ax.set_ylabel("post / pre RMSPE ratio",fontsize=6.4)
ax.text(0.6,rk.values[0]*.92,"CITY-07",fontsize=6.2,color=RED)
save("fig12_4_rmspe_ratio")
print("ch12 figures done")
