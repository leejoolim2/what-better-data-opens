"""Chapter 8 figures at true print width (4.55 in)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, pandas as pd, numpy as np, pathlib, warnings
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Rectangle
import statsmodels.formula.api as smf
warnings.filterwarnings("ignore")
W=4.55
INK,TEAL,RED,BLUE,GREY,GOLD = "#16283C","#0E7C7B","#B3372B","#276DC3","#8A99A6","#B7791F"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":7.2,
 "axes.edgecolor":INK,"axes.labelcolor":INK,"text.color":INK,
 "xtick.color":INK,"ytick.color":INK,"xtick.labelsize":6.6,"ytick.labelsize":6.6,
 "axes.spines.top":False,"axes.spines.right":False,
 "figure.facecolor":"white","savefig.facecolor":"white"})
D=str(pathlib.Path(__file__).resolve().parents[1]/"data")+"/"
d=pd.read_csv(D+"ch08_did_staggered.csv",parse_dates=["date"])
d["rel"]=pd.to_numeric(d.rel_time,errors="coerce")
d["is_tc"]=(d.cohort!="never").astype(int)
def save(n): plt.savefig(f"{n}.png",dpi=320,bbox_inches="tight"); plt.close()

# 8.1 treatment adoption chart
order={"2023-01":0,"2023-07":1,"2024-01":2,"never":3}
u=d.drop_duplicates("shapeID")[["shapeID","cohort"]].copy()
u["o"]=u.cohort.map(order); u=u.sort_values(["o","shapeID"]).reset_index(drop=True)
months=sorted(d.date.unique())
M={m:i for i,m in enumerate(months)}
fig,ax=plt.subplots(figsize=(W,2.2))
for i,r in u.iterrows():
    g=d[d.shapeID==r.shapeID]
    for _,row in g.iterrows():
        col=INK if row.treat_now==1 else "#E8EDF0"
        ax.add_patch(Rectangle((M[row.date],i),1,1,facecolor=col,edgecolor="none"))
ax.set_xlim(0,len(months)); ax.set_ylim(0,len(u))
yt=[]; lab=[]
start=0
for c in ["2023-01","2023-07","2024-01","never"]:
    n=(u.cohort==c).sum(); yt.append(start+n/2); lab.append(c); start+=n
    ax.axhline(start,color="white",lw=1.2)
ax.set_yticks(yt); ax.set_yticklabels(lab,fontsize=6.2)
xt=[i for i,m in enumerate(months) if pd.Timestamp(m).month==1]
ax.set_xticks(xt); ax.set_xticklabels([pd.Timestamp(months[i]).year for i in xt])
ax.set_xlabel("month",fontsize=6.6); ax.invert_yaxis()
ax.set_title("dark = treated in that month",fontsize=6.8,loc="left")
save("fig8_1_adoption")

# 8.2 contaminated vs clean event study
def evstudy(clean):
    if clean:
        ev=d[(d.cohort=="never")|((d.rel>=-9)&(d.rel<=15))].copy()
        mk=lambda k: ((ev.is_tc==1)&(ev.rel==k)).astype(int)
    else:
        ev=d[d.rel.notna()].copy(); ev=ev[(ev.rel>=-9)&(ev.rel<=15)]
        mk=lambda k: (ev.rel==k).astype(int)
    terms=[]
    for k in range(-9,16):
        if k==-1: continue
        nm=("L%d"%abs(k)) if k<0 else ("F%d"%k)
        ev[nm]=mk(k); terms.append(nm)
    r=smf.ols("log_avg_rad ~ "+" + ".join(terms)+" + C(shapeID) + C(date)",ev).fit(
        cov_type="cluster",cov_kwds={"groups":ev.shapeID})
    ks=list(range(-9,16)); b=[];s=[]
    for k in ks:
        if k==-1: b.append(0); s.append(0); continue
        nm=("L%d"%abs(k)) if k<0 else ("F%d"%k)
        b.append(r.params[nm]); s.append(r.bse[nm])
    return ks,b,s
fig,ax=plt.subplots(1,2,figsize=(W,2.1),sharey=True)
for a,(cl,ti,col) in zip(ax,[(False,"already-treated used as controls",RED),
                             (True,"never-treated only",TEAL)]):
    ks,b,s=evstudy(cl)
    a.errorbar(ks,b,yerr=[1.96*x for x in s],fmt="o",ms=2.6,capsize=1.8,lw=.8,
               color=col,ecolor=GREY,mfc="white")
    tv=[0 if k<0 else min(.015*(k+1),.06) for k in ks]
    a.plot(ks,tv,color=INK,lw=1.0,ls="--")
    a.axhline(0,color=INK,lw=.6); a.axvline(-.5,color=GREY,ls=":",lw=.8)
    a.set_title(ti,fontsize=6.6); a.set_xlabel("months since treatment",fontsize=6.4)
    a.tick_params(labelsize=6.0)
ax[0].set_ylabel("coefficient",fontsize=6.4)
ax[1].text(6,.005,"dashed = truth",fontsize=5.8,color=INK)
plt.tight_layout(); save("fig8_2_two_event_studies")

# 8.3 estimator comparison
nev=d[d.cohort=="never"]; ests=[];ws=[]
for coh in ["2023-01","2023-07","2024-01"]:
    sub=pd.concat([d[d.cohort==coh],nev]); g=pd.Timestamp(coh+"-01")
    sub=sub.assign(post=(sub.date>=g).astype(int),tr=(sub.cohort==coh).astype(int))
    sub["tp"]=sub.tr*sub.post
    m=smf.ols("log_avg_rad ~ tp + C(shapeID) + C(date)",sub).fit()
    ests.append(m.params["tp"]); ws.append(len(sub[(sub.tr==1)&(sub.post==1)]))
tw=smf.ols("log_avg_rad ~ treat_now + C(shapeID) + C(date)",d).fit()
agg=np.average(ests,weights=ws)
fig,ax=plt.subplots(figsize=(W,1.7))
names=["TWFE\n(single coef)","2023-01\ncohort","2023-07\ncohort","2024-01\ncohort","weighted\naggregate"]
vals=[tw.params["treat_now"]]+ests+[agg]
cols=[RED,GREY,GREY,GREY,TEAL]
ax.bar(range(5),vals,color=cols,width=.55)
ax.axhline(.057,color=INK,ls="--",lw=1.1)
ax.text(4.45,.0585,"true ATT",fontsize=6.0,ha="right")
for i,v in enumerate(vals): ax.text(i,v+.002,f"{v:.4f}",ha="center",fontsize=6.0)
ax.set_xticks(range(5)); ax.set_xticklabels(names,fontsize=6.0)
ax.set_ylim(0,.075); ax.set_ylabel("estimated effect",fontsize=6.4)
save("fig8_3_estimators")
print("ch08 figures done")
