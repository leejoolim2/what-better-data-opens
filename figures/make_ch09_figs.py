"""Chapter 9 figures at true print width (4.55 in)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, pandas as pd, numpy as np, pathlib, warnings
import statsmodels.formula.api as smf
from sklearn.linear_model import LogisticRegression
from sklearn.neighbors import NearestNeighbors
warnings.filterwarnings("ignore")
W=4.55
INK,TEAL,RED,BLUE,GREY = "#16283C","#0E7C7B","#B3372B","#276DC3","#8A99A6"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":7.2,
 "axes.edgecolor":INK,"axes.labelcolor":INK,"text.color":INK,
 "xtick.color":INK,"ytick.color":INK,"xtick.labelsize":6.6,"ytick.labelsize":6.6,
 "axes.spines.top":False,"axes.spines.right":False,
 "figure.facecolor":"white","savefig.facecolor":"white"})
D=str(pathlib.Path(__file__).resolve().parents[1]/"data")+"/"
d=pd.read_csv(D+"ch09_matching_phnompenh.csv")
covs=["pre_sales_index","floor_area_m2","dist_road_m","frontage_m","years_open"]
labs=["pre-programme sales","floor area","distance to road","frontage","years open"]
d["ps"]=LogisticRegression(max_iter=3000).fit(d[covs].values,d.program).predict_proba(d[covs].values)[:,1]
def save(n): plt.savefig(f"{n}.png",dpi=320,bbox_inches="tight"); plt.close()
def smd(df,v,w=None):
    a=df[df.program==1]; b=df[df.program==0]
    if w is None: ma,mb,va,vb=a[v].mean(),b[v].mean(),a[v].var(),b[v].var()
    else:
        ma=np.average(a[v],weights=a[w]); mb=np.average(b[v],weights=b[w])
        va=np.average((a[v]-ma)**2,weights=a[w]); vb=np.average((b[v]-mb)**2,weights=b[w])
    return (ma-mb)/np.sqrt((va+vb)/2)

# 9.1 common support
tr=d[d.program==1]; ct=d[d.program==0]
fig,ax=plt.subplots(figsize=(W,1.85))
ax.hist(ct.ps,bins=30,color=BLUE,alpha=.55,label="control (575)")
ax.hist(tr.ps,bins=30,color=RED,alpha=.55,label="treated (225)")
lo,hi=max(tr.ps.min(),ct.ps.min()),min(tr.ps.max(),ct.ps.max())
ax.axvline(lo,color=INK,ls=":",lw=.9); ax.axvline(hi,color=INK,ls=":",lw=.9)
ax.set_xlabel("propensity score",fontsize=6.6); ax.set_ylabel("count",fontsize=6.6)
ax.legend(fontsize=6.0,frameon=False)
ax.text(hi+.01,ax.get_ylim()[1]*.6,"no treated\nunits here",fontsize=5.8,color=INK)
save("fig9_1_common_support")

# 9.2 love plot
cal=0.2*d.ps.std()
nn=NearestNeighbors(n_neighbors=1).fit(ct[["ps"]].values)
dist,idx=nn.kneighbors(tr[["ps"]].values); keep=dist.flatten()<=cal
matched=pd.concat([tr[keep],ct.iloc[idx.flatten()[keep]]])
d["w"]=np.where(d.program==1,1.0,d.ps/(1-d.ps))
before=[abs(smd(d,v)) for v in covs]
after_m=[abs(smd(matched,v)) for v in covs]
after_w=[abs(smd(d,v,"w")) for v in covs]
y=np.arange(len(covs))
fig,ax=plt.subplots(figsize=(W,1.95))
ax.axvline(.1,color=GREY,ls="--",lw=.9)
ax.scatter(before,y,s=38,color=RED,label="before",zorder=3)
ax.scatter(after_m,y,s=38,facecolor="white",edgecolor=TEAL,lw=1.3,label="after matching",zorder=3)
ax.scatter(after_w,y,s=24,color=BLUE,marker="s",label="after weighting",zorder=3)
for i,(b,a) in enumerate(zip(before,after_m)): ax.plot([b,a],[i,i],color=GREY,lw=.7,zorder=1)
ax.set_yticks(y); ax.set_yticklabels(labs,fontsize=6.4); ax.invert_yaxis()
ax.set_xlabel("|standardised mean difference|",fontsize=6.6)
ax.legend(fontsize=5.9,frameon=False,loc="lower right")
ax.text(.105,-.45,"0.1 threshold",fontsize=5.6,color=GREY)
save("fig9_2_love_plot")

# 9.3 estimator comparison
est={"naive\ndifference":d[d.program==1].post_sales_index.mean()-d[d.program==0].post_sales_index.mean(),
     "regression\nonly":smf.ols("post_sales_index ~ program + "+" + ".join(covs),d).fit().params["program"],
     "matching\n(means)":matched[matched.program==1].post_sales_index.mean()-matched[matched.program==0].post_sales_index.mean(),
     "matching\n+ regression":smf.ols("post_sales_index ~ program + "+" + ".join(covs),matched).fit().params["program"],
     "IPW":smf.wls("post_sales_index ~ program",d,weights=d.w).fit().params["program"],
     "doubly\nrobust":smf.wls("post_sales_index ~ program + "+" + ".join(covs),d,weights=d.w).fit().params["program"]}
fig,ax=plt.subplots(figsize=(W,1.8))
ks=list(est); vs=[est[k] for k in ks]
ax.bar(range(len(ks)),vs,color=[RED]+[TEAL]*5,width=.55)
ax.axhline(5.0,color=INK,ls="--",lw=1.1)
ax.text(5.45,5.4,"truth 5.0",fontsize=6.0,ha="right")
for i,v in enumerate(vs): ax.text(i,v+.3,f"{v:.2f}",ha="center",fontsize=6.0)
ax.set_xticks(range(len(ks))); ax.set_xticklabels(ks,fontsize=5.8)
ax.set_ylim(0,17); ax.set_ylabel("estimated ATT",fontsize=6.4)
save("fig9_3_estimators")
print("ch09 figures done")
