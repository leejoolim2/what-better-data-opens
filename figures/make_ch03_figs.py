"""Chapter 3 figures, drawn at the true text width of the 6x9 page (4.55 in)."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, pandas as pd, numpy as np
from matplotlib.colors import ListedColormap
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path
import statsmodels.formula.api as smf, warnings, os
warnings.filterwarnings("ignore")

W = 4.55                                   # text block width, inches
INK,TEAL,RED,BLUE,GREY,GOLD = "#16283C","#0E7C7B","#B3372B","#276DC3","#8A99A6","#B7791F"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":7.2,
    "axes.edgecolor":INK,"axes.labelcolor":INK,"text.color":INK,
    "xtick.color":INK,"ytick.color":INK,"xtick.labelsize":6.6,"ytick.labelsize":6.6,
    "axes.spines.top":False,"axes.spines.right":False,
    "figure.facecolor":"white","savefig.facecolor":"white"})
import pathlib
D = str(pathlib.Path(__file__).resolve().parents[1] / "data") + "/"
p = pd.read_csv(D+"ch03_viirs_panel_adm2.csv", parse_dates=["date"])
cross = pd.read_csv(D+"ch03_boundary_crosswalk_tashkent.csv")
m = p.merge(cross, left_on="shapeID", right_on="new_shapeID", how="left")
m["unit"]=m.old_shapeID.fillna(m.shapeID); m["w"]=m.area_share.fillna(1.0)
o = m.dropna(subset=["avg_rad"]).copy(); o["num"]=o.w*o.avg_rad
h = o.groupby(["unit","date"]).agg(num=("num","sum"),cv=("w","sum")).reset_index()
h["avg_rad"]=h.num/h.cv; h["log_rad"]=np.log(h.avg_rad)

def save(n): plt.savefig(f"{n}.png", dpi=320, bbox_inches="tight"); plt.close()

# 3.1 completeness
piv=(p.assign(s=np.where(p.avg_rad.isna(),1,2))
       .pivot_table(index="shapeID",columns="date",values="s",fill_value=0))
order=p.groupby("shapeID").city.first().reindex(piv.index).sort_values()
fig,ax=plt.subplots(figsize=(W,2.9))
ax.imshow(piv.loc[order.index].values,aspect="auto",interpolation="nearest",
          cmap=ListedColormap(["#FFFFFF",RED,"#CFE3E2"]))
ax.set_xticks([i for i,d in enumerate(piv.columns) if d.month==1])
ax.set_xticklabels([d.year for d in piv.columns if d.month==1])
ax.set_yticks([]); y=0
for c,g in order.groupby(order,sort=False):
    ax.axhline(y-.5,color=INK,lw=.5); ax.text(-1.6,y+len(g)/2,c,ha="right",va="center",fontsize=6.2); y+=len(g)
ax.text(0,-0.16,"white = unit absent    red = no cloud-free night    pale = usable",
        transform=ax.transAxes,fontsize=5.8,color=GREY)
save("fig3_1_completeness")

# 3.3 seam
sid="UZB-ADM2-001"
fig,ax=plt.subplots(figsize=(W,2.1))
ax.plot(p[p.shapeID==sid].date,p[p.shapeID==sid].avg_rad,color=INK,lw=1.1,label="old unit")
ax.plot(p[p.shapeID==sid+"-A"].date,p[p.shapeID==sid+"-A"].avg_rad,color=RED,lw=1.1,ls="--",label='naive: "-A" as continuation')
r=h[h.unit==sid]; r=r[r.date>="2022-01-01"]
ax.plot(r.date,r.avg_rad,color=TEAL,lw=1.4,label="repaired (crosswalk)")
ax.axvline(pd.Timestamp("2022-01-01"),color=GREY,ls=":",lw=.9)
ax.annotate("+11.1% artefact",xy=(pd.Timestamp("2022-03-01"),10.9),
            xytext=(pd.Timestamp("2022-09-01"),13.6),color=RED,fontsize=6.4,
            arrowprops=dict(arrowstyle="->",color=RED,lw=.9))
ax.set_ylabel("avg_rad",fontsize=6.8); ax.set_ylim(6.3,15.4)
ax.legend(fontsize=5.9,frameon=False,loc="upper left",handlelength=1.6)
save("fig3_3_seam")

# 3.4 validation
mo=h.groupby(h.date.dt.to_period("M")).log_rad.mean(); mo.index=mo.index.to_timestamp()
fig,ax=plt.subplots(figsize=(W,2.1))
ax.axvspan(pd.Timestamp("2020-04-01"),pd.Timestamp("2020-08-01"),color=RED,alpha=.10)
for u in list(h.unit.unique())[::4]:
    g=h[h.unit==u]; ax.plot(g.date,g.log_rad,color=GREY,lw=.25,alpha=.35)
ax.plot(mo.index,mo.values,color=INK,lw=1.5)
ax.text(pd.Timestamp("2020-06-01"),mo.max()+.30,"restrictions",ha="center",fontsize=6.2,color=RED)
ax.set_ylabel("log(avg_rad)",fontsize=6.8); ax.set_ylim(mo.min()-.8,mo.max()+.55)
save("fig3_4_validation")

# 3.5 seasonal
h["month"]=h.date.dt.month
dev=h.groupby("month").log_rad.mean()-h.log_rad.mean()
cvg=p.assign(mm=p.date.dt.month).groupby("mm").cf_cvg.mean()
fig,ax=plt.subplots(1,2,figsize=(W,1.7))
ax[0].bar(dev.index,dev.values,color=[RED if v<0 else TEAL for v in dev.values])
ax[0].axhline(0,color=INK,lw=.6); ax[0].set_title("seasonal deviation, log radiance",fontsize=6.6)
ax[1].bar(cvg.index,cvg.values,color=BLUE); ax[1].set_title("cloud-free nights (cf_cvg)",fontsize=6.6)
for a in ax: a.set_xticks([1,4,7,10]); a.set_xlabel("month",fontsize=6.4)
plt.tight_layout(); save("fig3_5_seasonal")

# 3.A crosswalk flow  |  3.B pipeline  — monochrome, padded
def box(ax,x,y,w,hh,t,fs=6.0,bold=False,lw=0.9):
    ax.add_patch(FancyBboxPatch((x,y),w,hh,
        boxstyle="round,pad=0.010,rounding_size=0.02",
        fc="white",ec=INK,lw=lw))
    ax.text(x+w/2,y+hh/2,t,ha="center",va="center",fontsize=fs,color=INK,
            weight="bold" if bold else "normal",linespacing=1.4)
def arr(ax,x1,y1,x2,y2):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",
        mutation_scale=8,lw=0.9,color=INK))
def frame(ax):
    ax.set_xlim(-.05,1.05); ax.set_ylim(-.16,1.08); ax.axis("off")

fig,ax=plt.subplots(figsize=(W,2.5)); frame(ax)
box(ax,.00,.70,.30,.24,"Old boundary\nvintage (ADM2)")
box(ax,.00,.38,.30,.24,"New boundary\nvintage")
box(ax,.38,.54,.24,.24,"INTERSECT\n(QGIS: Vector →\nGeoprocessing)",bold=True)
box(ax,.70,.54,.30,.24,"Intersection polygons\nold_id × new_id")
box(ax,.70,.26,.30,.20,"area_share =\n$area / area_of_old")
box(ax,.70,.00,.30,.20,"crosswalk.csv",bold=True,lw=1.5)
arr(ax,.30,.82,.38,.72); arr(ax,.30,.50,.38,.60)
arr(ax,.62,.66,.70,.66); arr(ax,.85,.54,.85,.46); arr(ax,.85,.26,.85,.20)
ax.text(0,.20,"keep the intersection layer\nand the area table:\nboth are auditable",
        fontsize=5.6,color=INK,va="top",linespacing=1.5,style="italic")
save("fig3A_crosswalk_flow")

fig,ax=plt.subplots(figsize=(W,1.95)); frame(ax)
steps=["Satellite\narchive","Zonal mean\nby unit","Unit × month\ntable + cf_cvg",
       "Harmonise\nunits","Validate on\nknown event","Analysis-ready\npanel"]
w=.29; gap=.055; hh=.30
for i,t in enumerate(steps):
    row,col = divmod(i,3)
    x = .01 + col*(w+gap)
    y = .58 - row*.42
    box(ax,x,y,w,hh,t,fs=6.2,bold=(i==5),lw=1.5 if i==5 else .9)
    if col<2: arr(ax,x+w,y+hh/2,x+w+gap,y+hh/2)
# 1행 끝 → 2행 처음: 꺾인 한 줄짜리 화살표
from matplotlib.path import Path as MPath
x_end   = .01 + 2*(w+gap) + w/2      # 3번 박스 하단 중앙
x_start = .01 + w/2                  # 4번 박스 상단 중앙
y_mid   = .52
verts = [(x_end,.58), (x_end,y_mid), (x_start,y_mid), (x_start,.46)]
ax.add_patch(FancyArrowPatch(path=MPath(verts,[MPath.MOVETO]+[MPath.LINETO]*3),
    arrowstyle="-|>", mutation_scale=8, lw=.9, color=INK,
    joinstyle="miter", capstyle="butt"))
ax.text(.01,.02,"cf_cvg = 0 → missing, never zero",fontsize=5.6,color=INK,style="italic")
ax.text(.55,.02,"keep the pre-change geography",fontsize=5.6,color=INK,style="italic")
save("fig3B_pipeline")
print("done")
