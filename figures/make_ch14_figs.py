"""Chapter 14 figures at true print width (4.55 in text block)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, pandas as pd, numpy as np, pathlib
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from matplotlib.path import Path
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
d = pd.read_csv(D+"ch14_spillover_panel.csv", parse_dates=["date"])
g = d.drop_duplicates("cell_id").copy()
FE = " + C(cell_id) + C(date)"
def fit(df, rhs):
    return smf.ols("log_avg_rad ~ "+rhs+FE, df).fit(
        cov_type="cluster", cov_kwds={"groups": df.cell_id})
def save(n): plt.savefig(f"{n}.png", dpi=320, bbox_inches="tight"); plt.close()

# 14.1 geography (referenced at width=70%)
fig,ax=plt.subplots(figsize=(3.2,3.3))
c=g[(g.treated==0)&(g.in_spillover_ring==0)]
ax.scatter(c.x_km,c.y_km,s=42,marker="s",color="#E8EDF0",edgecolor="white",lw=.5,label="control (105)")
r=g[g.in_spillover_ring==1]
ax.scatter(r.x_km,r.y_km,s=42,marker="s",color="#F0C9C1",edgecolor="white",lw=.5,label="ring ≤2 km (36)")
t=g[g.treated==1]
ax.scatter(t.x_km,t.y_km,s=52,marker="s",color=RED,edgecolor="white",lw=.5,label="treated (3)")
for _,row in t.iterrows():
    ax.add_patch(Circle((row.x_km,row.y_km),2.0,fill=False,ls="--",lw=.8,color=RED))
ax.set_aspect("equal"); ax.set_xlabel("km",fontsize=6.6); ax.set_ylabel("km",fontsize=6.6)
ax.legend(fontsize=5.8,frameon=False,loc="upper center",bbox_to_anchor=(.5,-.14),ncol=3,
          handletextpad=.3,columnspacing=.9)
save("fig14_1_geography")

# 14.2 trajectories
d["grp"]=np.where(d.treated==1,"treated",np.where(d.in_spillover_ring==1,"ring","far"))
mo=d.groupby(["grp","date"]).log_avg_rad.mean().reset_index()
base=mo[mo.date<"2024-01-01"].groupby("grp").log_avg_rad.mean()
fig,ax=plt.subplots(figsize=(W,2.0))
for grp,col,ls,lab in [("treated",RED,"-","treated (3)"),("ring",GOLD,"--","ring ≤2 km (36)"),
                       ("far",BLUE,":","far >2 km (105)")]:
    s=mo[mo.grp==grp]; ax.plot(s.date,s.log_avg_rad-base[grp],color=col,ls=ls,lw=1.3,label=lab)
ax.axvline(pd.Timestamp("2024-01-01"),color=GREY,ls=":",lw=.9); ax.axhline(0,color=INK,lw=.6)
ax.set_ylabel("log radiance, centred",fontsize=6.6)
ax.legend(fontsize=5.9,frameon=False,loc="upper left",handlelength=2.2)
save("fig14_2_trajectories")

# 14.3 distance bands
cuts={"treated":(-.01,0),"b0_1":(0,1),"b1_2":(1,2),"b2_3":(2,3),"b3_4":(3,4)}
for k,(lo,hi) in cuts.items():
    d[k]=((d.dist_to_treat_km>lo)&(d.dist_to_treat_km<=hi)).astype(int)
m=fit(d," + ".join(f"{k}:post" for k in cuts))
co=[m.params[f"{k}:post"] for k in cuts]; se=[m.bse[f"{k}:post"] for k in cuts]
fig,ax=plt.subplots(figsize=(W,1.95))
ax.axvspan(.5,2.5,color=GOLD,alpha=.10)
ax.errorbar(range(5),co,yerr=[1.96*s for s in se],fmt="o",ms=4.2,capsize=2.6,lw=1.1,
            color=INK,ecolor=INK,mfc="white")
for i,col in enumerate([RED,GOLD,GOLD,GREY,GREY]): ax.plot(i,co[i],"o",ms=4.2,color=col)
ax.axhline(0,color=INK,lw=.6)
ax.set_xticks(range(5)); ax.set_xticklabels(["treated","0–1 km","1–2 km","2–3 km","3–4 km"],fontsize=6.4)
ax.set_ylabel("effect vs cells >4 km",fontsize=6.6)
ax.text(1.5,max(co)*.62,"spillover zone",ha="center",fontsize=6.0,color=GOLD)
save("fig14_3_bands")

# 14.4 design comparison + accounting
mb=fit(d,"treated:post + in_spillover_ring:post")
nT,nR=int(g.treated.sum()),int(g.in_spillover_ring.sum())
b,gam=mb.params["treated:post"],mb.params["in_spillover_ring:post"]
fig,ax=plt.subplots(1,2,figsize=(W,1.9))
names=["naive","nearby\ncontrols","donut","explicit"]
vals=[.0568,.0536,.0622,.0622]; ses=[.0039,.0041,.0039,.0039]
ax[0].barh(range(4),vals,xerr=[1.96*s for s in ses],color=[RED,RED,TEAL,TEAL],
           error_kw=dict(ecolor=INK,lw=.8),height=.62)
ax[0].axvline(.06,color=INK,ls="--",lw=1.0)
ax[0].text(.0607,3.6,"truth",fontsize=5.8)
ax[0].set_yticks(range(4)); ax[0].set_yticklabels(names,fontsize=6.0); ax[0].invert_yaxis()
ax[0].set_xlim(.045,.072); ax[0].set_xlabel("direct effect",fontsize=6.4)
ax[1].bar(["treated\n3 cells","ring\n36 cells"],[nT*b,nR*gam],color=[RED,GOLD],width=.55)
ax[1].set_ylabel("total log-radiance change",fontsize=6.4)
ax[1].text(1,nR*gam*.5,"80%",ha="center",fontsize=8,weight="bold",color="white")
for a in ax: a.tick_params(labelsize=6.0)
plt.tight_layout(); save("fig14_4_compare")

# 14.A exposure-mapping decision diagram (monochrome)
def box(ax,x,y,w,h,t,fs=6.0,bold=False,lw=.9):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.010,rounding_size=0.02",
        fc="white",ec=INK,lw=lw))
    ax.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=fs,color=INK,
            weight="bold" if bold else "normal",linespacing=1.4)
def arr(ax,x1,y1,x2,y2):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=8,lw=.9,color=INK))
fig,ax=plt.subplots(figsize=(W,2.45))
ax.set_xlim(-.05,1.05); ax.set_ylim(-.14,1.08); ax.axis("off")
box(ax,.30,.82,.40,.18,"What is the channel?",bold=True)
box(ax,.00,.50,.30,.22,"Physical proximity\n(footfall,\nland market)",fs=5.8)
box(ax,.35,.50,.30,.22,"Network\n(bus route,\nsupply chain)",fs=5.8)
box(ax,.70,.50,.30,.22,"Administrative\n(shared budget,\npolicy)",fs=5.8)
box(ax,.00,.20,.30,.20,"exposure =\ndistance ≤ R")
box(ax,.35,.20,.30,.20,"exposure =\nhops on the network")
box(ax,.70,.20,.30,.20,"exposure =\nsame jurisdiction")
box(ax,.10,-.08,.80,.18,"Estimate the exposure zone from the data;\nalways report the outermost band",bold=True,lw=1.5,fs=6.0)
arr(ax,.45,.82,.15,.73); arr(ax,.50,.82,.50,.73); arr(ax,.55,.82,.85,.73)
arr(ax,.15,.50,.15,.41); arr(ax,.50,.50,.50,.41); arr(ax,.85,.50,.85,.41)
wrap=Path([(.15,.20),(.15,.15),(.50,.15),(.50,.11)],
          [Path.MOVETO,Path.LINETO,Path.LINETO,Path.LINETO])
ax.add_patch(FancyArrowPatch(path=wrap,arrowstyle="-|>",mutation_scale=8,lw=.9,color=INK))
save("fig14A_exposure_choice")
print("ch14 figures done")
