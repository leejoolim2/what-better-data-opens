"""Chapter 11 figures at true print width (4.55 in)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, pandas as pd, numpy as np, pathlib, warnings
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
d=pd.read_csv(D+"ch11_rdd_transfer.csv"); d["r"]=d.running/1000.0
def save(n): plt.savefig(f"{n}.png",dpi=320,bbox_inches="tight"); plt.close()

s=d[abs(d.r)<=20].copy(); s["bin"]=pd.cut(s.r,20)
g=s.groupby("bin",observed=True).agg(x=("r","mean"),y=("invest_per_capita_usd","mean")).reset_index()
fig,ax=plt.subplots(figsize=(W,2.25))
ax.scatter(s.r,s.invest_per_capita_usd,s=2.5,color=GREY,alpha=.30,zorder=1)
ax.scatter(g[g.x<0].x,g[g.x<0].y,s=22,color=BLUE,zorder=3,label="binned mean, ineligible")
ax.scatter(g[g.x>0].x,g[g.x>0].y,s=22,color=RED,zorder=3,label="binned mean, eligible")
for side,col in [(-1,BLUE),(1,RED)]:
    sub=s[np.sign(s.r)==side]
    b=np.polyfit(sub.r,sub.invest_per_capita_usd,1)
    xs=np.linspace(0 if side>0 else -20,20 if side>0 else 0,10)
    ax.plot(xs,np.polyval(b,xs),color=col,lw=1.5,zorder=4)
ax.axvline(0,color=INK,ls=":",lw=1.0)
ax.set_xlabel("population minus 50,000  (thousands)",fontsize=6.6)
ax.set_ylabel("investment per capita (USD)",fontsize=6.6)
ax.legend(fontsize=5.9,frameon=False,loc="upper left")
save("fig11_1_rd_plot")

hs=[30,20,15,10,7.5,5,3]; est=[];se=[]
for h in hs:
    sub=d[abs(d.r)<=h]; m=smf.ols("invest_per_capita_usd ~ eligible*r",sub).fit()
    est.append(m.params["eligible"]); se.append(m.bse["eligible"])
fig,ax=plt.subplots(figsize=(W,1.85))
x=np.arange(len(hs))
ax.errorbar(x,est,yerr=[1.96*e for e in se],fmt="o",ms=4,capsize=3,lw=1.1,
            color=INK,ecolor=GREY,mfc="white")
ax.axhline(120,color=TEAL,ls="--",lw=1.1)
ax.text(6.4,126,"truth 120",fontsize=6.0,color=TEAL,ha="right")
ax.set_xticks(x); ax.set_xticklabels([f"{h:g}" for h in hs],fontsize=6.2)
ax.set_xlabel("bandwidth (thousands of people)",fontsize=6.5)
ax.set_ylabel("estimated jump (USD)",fontsize=6.4)
save("fig11_2_bandwidth")

orders=[1,2,4,6,8]; ge=[];gs=[]
for p in orders:
    f="invest_per_capita_usd ~ eligible*("+"+".join(f"I(r**{k})" for k in range(1,p+1))+")"
    m=smf.ols(f,d).fit(); ge.append(m.params["eligible"]); gs.append(m.bse["eligible"])
fig,ax=plt.subplots(1,2,figsize=(W,1.85))
ax[0].errorbar(range(len(orders)),ge,yerr=[1.96*e for e in gs],fmt="o",ms=4,capsize=3,
               lw=1.1,color=RED,ecolor=GREY,mfc="white")
ax[0].axhline(120,color=TEAL,ls="--",lw=1.1)
ax[0].set_xticks(range(len(orders))); ax[0].set_xticklabels(orders,fontsize=6.2)
ax[0].set_xlabel("global polynomial order",fontsize=6.4)
ax[0].set_ylabel("estimated jump",fontsize=6.4)
ax[0].set_title("global fit on all data",fontsize=6.8)
lo=[];ls_=[]; sub=d[abs(d.r)<=20]
for p in [1,2,3,4]:
    f="invest_per_capita_usd ~ eligible*("+"+".join(f"I(r**{k})" for k in range(1,p+1))+")"
    m=smf.ols(f,sub).fit(); lo.append(m.params["eligible"]); ls_.append(m.bse["eligible"])
ax[1].errorbar(range(4),lo,yerr=[1.96*e for e in ls_],fmt="o",ms=4,capsize=3,
               lw=1.1,color=TEAL,ecolor=GREY,mfc="white")
ax[1].axhline(120,color=TEAL,ls="--",lw=1.1)
ax[1].set_xticks(range(4)); ax[1].set_xticklabels([1,2,3,4],fontsize=6.2)
ax[1].set_xlabel("local polynomial order",fontsize=6.4)
ax[1].set_title("local fit, bandwidth 20",fontsize=6.8)
for a in ax: a.tick_params(labelsize=6.0); a.set_ylim(40,190)
plt.tight_layout(); save("fig11_3_polynomial")

fig,ax=plt.subplots(figsize=(W,1.6))
ax.hist(d[d.r<0].r,bins=np.arange(-35,1,2),color=BLUE,alpha=.6)
ax.hist(d[d.r>=0].r,bins=np.arange(0,44,2),color=RED,alpha=.6)
ax.axvline(0,color=INK,ls=":",lw=1.0)
ax.set_xlabel("population minus 50,000 (thousands)",fontsize=6.5)
ax.set_ylabel("municipalities",fontsize=6.4)
save("fig11_4_density")
print("ch11 figures done")
