"""Chapter 2 figure: the two-question triage diagram, monochrome."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt
from matplotlib.patches import FancyBboxPatch, FancyArrowPatch
from matplotlib.path import Path
INK = "#16283C"
W = 4.55
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":7.2,
    "figure.facecolor":"white","savefig.facecolor":"white"})

def box(ax,x,y,w,h,t,fs=6.4,bold=False,lw=0.9,dashed=False):
    ax.add_patch(FancyBboxPatch((x,y),w,h,boxstyle="round,pad=0.010,rounding_size=0.02",
        fc="white",ec=INK,lw=lw,linestyle="--" if dashed else "-"))
    ax.text(x+w/2,y+h/2,t,ha="center",va="center",fontsize=fs,color=INK,
            weight="bold" if bold else "normal",linespacing=1.35)
def arr(ax,x1,y1,x2,y2):
    ax.add_patch(FancyArrowPatch((x1,y1),(x2,y2),arrowstyle="-|>",mutation_scale=8,lw=.9,color=INK))
def lbl(ax,x,y,t):
    ax.text(x,y,t,fontsize=5.8,color=INK,style="italic",ha="center")

fig,ax=plt.subplots(figsize=(W,3.55))
ax.set_xlim(-.05,1.05); ax.set_ylim(.28,1.06); ax.axis("off")

box(ax,.20,.86,.60,.14,"Is treatment assigned by a threshold\non a running variable?",bold=True)
box(ax,.72,.62,.30,.14,"Regression Discontinuity\n— Chapter 11")
arr(ax,.80,.86,.87,.76); lbl(ax,.94,.81,"yes")

box(ax,.20,.62,.44,.14,"Do you observe the same units\nbefore and after treatment?",bold=True)
arr(ax,.40,.86,.40,.76); lbl(ax,.44,.81,"no")

box(ax,.02,.34,.40,.16,"Panel designs\nTable 2.1, rows 1–3\n(Chapters 7, 8, 12)")
arr(ax,.30,.62,.22,.50); lbl(ax,.30,.55,"yes")

box(ax,.50,.34,.40,.16,"Cross-sectional designs\nTable 2.1, rows 4, 5, 7\n(Chapters 9, 10, 1)")
arr(ax,.42,.62,.62,.50); lbl(ax,.56,.55,"no")

ax.annotate("", xy=(.02,.42), xytext=(-.03,.42),
            arrowprops=dict(arrowstyle="-",lw=0))  # spacer, no-op
plt.tight_layout(); plt.savefig("fig2A_triage.png", dpi=320, bbox_inches="tight"); plt.close()
print("done")
