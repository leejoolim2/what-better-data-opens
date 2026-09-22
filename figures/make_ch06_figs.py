"""Chapter 6 figures at true print width (4.55 in)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, pandas as pd, numpy as np, pathlib, warnings
import statsmodels.formula.api as smf
warnings.filterwarnings("ignore")
W=4.55
INK,TEAL,RED,GREY,GOLD = "#16283C","#0E7C7B","#B3372B","#8A99A6","#B7791F"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":7.2,
 "axes.edgecolor":INK,"axes.labelcolor":INK,"text.color":INK,
 "xtick.color":INK,"ytick.color":INK,"xtick.labelsize":6.6,"ytick.labelsize":6.6,
 "axes.spines.top":False,"axes.spines.right":False,
 "figure.facecolor":"white","savefig.facecolor":"white"})
D=str(pathlib.Path(__file__).resolve().parents[1]/"data")+"/"
p=pd.read_csv(D+"ch03_viirs_panel_adm2.csv",parse_dates=["date"])
cw=pd.read_csv(D+"ch03_boundary_crosswalk_tashkent.csv")
m=p.merge(cw,left_on="shapeID",right_on="new_shapeID",how="left")
m["unit"]=m.old_shapeID.fillna(m.shapeID); m["w"]=m.area_share.fillna(1.0)
o=m.dropna(subset=["avg_rad"]).copy(); o["num"]=o.w*o.avg_rad
h=(o.groupby(["unit","date"]).agg(num=("num","sum"),cv=("w","sum"),
   cf=("cf_cvg","mean")).reset_index())
h["y"]=np.log(h.num/h.cv)
def save(n): plt.savefig(f"{n}.png",dpi=320,bbox_inches="tight"); plt.close()

# 6.1 the within transformation: raw vs demeaned
sel=sorted(h.unit.unique())[:6]
sub=h[h.unit.isin(sel)].copy()
sub["dm"]=sub.y-sub.groupby("unit").y.transform("mean")
fig,ax=plt.subplots(1,2,figsize=(W,2.0),sharex=True)
for u in sel:
    g=sub[sub.unit==u]
    ax[0].plot(g.date,g.y,lw=.8,color=INK,alpha=.75)
    ax[1].plot(g.date,g.dm,lw=.8,color=TEAL,alpha=.8)
ax[0].set_title("raw log radiance",fontsize=7.0)
ax[1].set_title("after subtracting each unit's mean",fontsize=7.0)
ax[1].axhline(0,color=RED,lw=.8,ls="--")
for a_ in ax: a_.tick_params(labelsize=6.0)
ax[0].set_ylabel("log(avg_rad)",fontsize=6.4)
plt.tight_layout(); save("fig6_1_within_transform")

# 6.2 variance decomposition + R2 absorbed
gm=h.y.mean(); um=h.groupby("unit").y.transform("mean")
btw=((um-gm)**2).mean(); wth=((h.y-um)**2).mean()
r_u=smf.ols("y ~ C(unit)",h).fit().rsquared
r_t=smf.ols("y ~ C(date)",h).fit().rsquared
r_b=smf.ols("y ~ C(unit)+C(date)",h).fit().rsquared
fig,ax=plt.subplots(1,2,figsize=(W,1.75))
ax[0].bar(["between\nunits","within\nunits"],[btw/(btw+wth)*100,wth/(btw+wth)*100],
          color=[GREY,TEAL],width=.55)
for i,v in enumerate([btw/(btw+wth)*100,wth/(btw+wth)*100]):
    ax[0].text(i,v+2,f"{v:.1f}%",ha="center",fontsize=6.6)
ax[0].set_ylim(0,108); ax[0].set_ylabel("share of variance",fontsize=6.4)
ax[0].set_title("where the variation is",fontsize=7.0)
ax[1].bar(["unit FE","time FE","both"],[r_u,r_t,r_b],color=[INK,GREY,TEAL],width=.55)
for i,v in enumerate([r_u,r_t,r_b]): ax[1].text(i,v+.02,f"{v:.3f}",ha="center",fontsize=6.6)
ax[1].set_ylim(0,1.13); ax[1].set_ylabel("$R^2$ absorbed",fontsize=6.4)
ax[1].set_title("what the dummies take",fontsize=7.0)
for a_ in ax: a_.tick_params(labelsize=6.2)
plt.tight_layout(); save("fig6_2_variance")

# 6.3 coefficient across specifications
specs=[("pooled","y ~ cf"),("+ unit FE","y ~ cf + C(unit)"),
       ("+ unit & time FE","y ~ cf + C(unit) + C(date)")]
est=[]; ses=[]
for _,f in specs:
    r=smf.ols(f,h).fit(cov_type="cluster",cov_kwds={"groups":h.unit})
    est.append(r.params["cf"]*1000); ses.append(r.bse["cf"]*1000)
fig,ax=plt.subplots(figsize=(W,1.7))
ax.errorbar(range(3),est,yerr=[1.96*s for s in ses],fmt="o",ms=5,capsize=3,lw=1.2,
            color=INK,ecolor=INK,mfc="white")
ax.axhline(0,color=RED,lw=.9,ls="--")
ax.set_xticks(range(3)); ax.set_xticklabels([s[0] for s in specs],fontsize=6.6)
ax.set_ylabel("coefficient on cf_cvg\n(× 1000)",fontsize=6.4)
ax.set_xlim(-.4,2.4)
save("fig6_3_specifications")
print("ch06 figures done")
