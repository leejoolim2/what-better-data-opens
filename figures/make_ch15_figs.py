"""Chapter 15 figures at true print width (4.55 in)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np, warnings
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch, Circle
from matplotlib.path import Path
warnings.filterwarnings("ignore")
W=4.55
INK,TEAL,RED,BLUE,GREY = "#16283C","#0E7C7B","#B3372B","#276DC3","#8A99A6"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":7.2,
 "axes.edgecolor":INK,"axes.labelcolor":INK,"text.color":INK,
 "xtick.color":INK,"ytick.color":INK,"xtick.labelsize":6.6,"ytick.labelsize":6.6,
 "axes.spines.top":False,"axes.spines.right":False,
 "figure.facecolor":"white","savefig.facecolor":"white"})
def save(n): plt.savefig(f"{n}.png",dpi=320,bbox_inches="tight"); plt.close()

# 15.A the pipeline, monochrome
fig,ax=plt.subplots(figsize=(W,2.35))
ax.set_xlim(-.04,1.04); ax.set_ylim(-.16,1.06); ax.axis("off")
def box(x,y,ww,h,t,fs=5.9,bold=False,lw=.9):
    ax.add_patch(FancyBboxPatch((x,y),ww,h,boxstyle="round,pad=0.008,rounding_size=0.015",
        fc="white",ec=INK,lw=lw))
    ax.text(x+ww/2,y+h/2,t,ha="center",va="center",fontsize=fs,color=INK,
            weight="bold" if bold else "normal",linespacing=1.35)
def arr(x1,y1,x2,y2):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=7,lw=.9,color=INK))
w_,g_,h_=.29,.055,.22
row1=["raw data\n(read-only)","build script\n(fixed seed)","analysis-ready\ndata"]
row2=["analysis\nscripts","outputs:\nfigures, tables","verification\nscript"]
for i,t in enumerate(row1):
    x=.005+i*(w_+g_); box(x,.72,w_,h_,t,bold=(i==1))
    if i<2: arr(x+w_,.83,x+w_+g_,.83)
for i,t in enumerate(row2):
    x=.005+i*(w_+g_); box(x,.30,w_,h_,t,bold=(i==2),lw=1.5 if i==2 else .9)
    if i<2: arr(x+w_,.41,x+w_+g_,.41)
xe=.005+2*(w_+g_)+w_/2; xs=.005+w_/2
wrap=Path([(xe,.72),(xe,.63),(xs,.63),(xs,.52)],
          [Path.MOVETO,Path.LINETO,Path.LINETO,Path.LINETO])
ax.add_patch(FancyArrowPatch(path=wrap,arrowstyle="-|>",mutation_scale=7,lw=.9,color=INK))
box(.24,.00,.52,.20,"every run reproduces every number",bold=True,lw=1.5,fs=6.2)
arr(.50,.30,.50,.21)
ax.text(.005,-.12,"nothing is edited by hand at any stage",fontsize=5.6,color=GREY,style="italic")
save("fig15A_pipeline")

# 15.1 geomasking and k-anonymity
rng=np.random.default_rng(11)
n=60
x=rng.uniform(0,10,n); y=rng.uniform(0,10,n)
ang=rng.uniform(0,2*np.pi,n); rad=rng.uniform(.3,1.2,n)
xm=x+rad*np.cos(ang); ym=y+rad*np.sin(ang)
fig,ax=plt.subplots(1,3,figsize=(W,1.75))
ax[0].scatter(x,y,s=9,color=RED); ax[0].set_title("exact locations",fontsize=6.4)
ax[1].scatter(x,y,s=9,color=GREY,alpha=.35)
ax[1].scatter(xm,ym,s=9,color=TEAL)
for i in range(0,n,4):
    ax[1].plot([x[i],xm[i]],[y[i],ym[i]],color=GREY,lw=.4)
ax[1].set_title("displaced 0.3–1.2 km",fontsize=6.4)
gx=(x//2.5)*2.5+1.25; gy=(y//2.5)*2.5+1.25
from collections import Counter
cnt=Counter(zip(gx,gy))
for (cx,cy),k in cnt.items():
    ax[2].add_patch(plt.Rectangle((cx-1.25,cy-1.25),2.5,2.5,fill=False,ec=GREY,lw=.5))
    ax[2].text(cx,cy,str(k),ha="center",va="center",fontsize=6.4,
               color=RED if k<5 else INK, weight="bold" if k<5 else "normal")
ax[2].set_title("aggregated: count per cell",fontsize=6.4)
for a in ax:
    a.set_xlim(-.5,10.5); a.set_ylim(-.5,10.5); a.set_aspect("equal")
    a.set_xticks([]); a.set_yticks([])
ax[2].text(5,-1.9,"red = fewer than 5; do not publish",fontsize=5.6,color=RED,ha="center")
plt.tight_layout(); save("fig15_1_geomasking")
print("ch15 figures done")
