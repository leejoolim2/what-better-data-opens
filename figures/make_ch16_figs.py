"""Chapter 16 figure: every design in the book, naive against corrected."""
import matplotlib; matplotlib.use("Agg")
import matplotlib.pyplot as plt, numpy as np
W=4.55
INK,TEAL,RED,GREY = "#16283C","#0E7C7B","#B3372B","#8A99A6"
plt.rcParams.update({"font.family":"DejaVu Sans","font.size":7.2,
 "axes.edgecolor":INK,"axes.labelcolor":INK,"text.color":INK,
 "xtick.color":INK,"ytick.color":INK,"xtick.labelsize":6.6,"ytick.labelsize":6.6,
 "axes.spines.top":False,"axes.spines.right":False,
 "figure.facecolor":"white","savefig.facecolor":"white"})

# chapter, label, truth, naive, corrected
rows=[
 (1 ,"Confounding",            3.0,   6.96,  3.12),
 (4 ,"Measurement",            0.42,  0.309, 0.410),
 (7 ,"Difference-in-diff.",    0.060, 0.124, 0.0588),
 (8 ,"Staggered timing",       0.0570,0.0500,0.0566),
 (9 ,"Selection",              5.0,   14.94, 5.22),
 (10,"Endogeneity",            0.15,  0.470, 0.1512),
 (11,"Threshold",              120.0, None,  124.2),
 (12,"Single treated unit",    5.73,  None,  4.68),
 (13,"Spatial dependence",     0.0333,0.0196*1.0,0.0362),
 (14,"Spillover",              0.060, 0.0568,0.0622),
]
def pct(v,t): return None if v is None else (v/t-1)*100
naive=[pct(n,t) for _,_,t,n,_ in rows]
corr =[pct(c,t) for _,_,t,_,c in rows]
labs=[f"{c}. {l}" for c,l,_,_,_ in rows]
y=np.arange(len(rows))

fig,ax=plt.subplots(figsize=(W,3.0))
ax.axvline(0,color=INK,lw=1.0)
ax.axvspan(-10,10,color=TEAL,alpha=.10)
for i,(nv,cv) in enumerate(zip(naive,corr)):
    if nv is not None:
        ax.plot([nv,cv],[i,i],color=GREY,lw=.8,zorder=1)
        ax.scatter(nv,i,s=34,color=RED,zorder=3)
    ax.scatter(cv,i,s=34,facecolor="white",edgecolor=TEAL,lw=1.5,zorder=3)
ax.set_yticks(y); ax.set_yticklabels(labs,fontsize=6.3); ax.invert_yaxis()
ax.set_xlabel("error against the planted truth (%)",fontsize=6.6)
ax.set_xlim(-65,215)
ax.scatter([],[],s=34,color=RED,label="naive estimate")
ax.scatter([],[],s=34,facecolor="white",edgecolor=TEAL,lw=1.5,label="design-based estimate")
ax.legend(fontsize=6.0,frameon=False,loc="lower right")
ax.text(12,-0.42,"±10%",fontsize=5.8,color=TEAL)
plt.savefig("fig16_1_summary.png",dpi=320,bbox_inches="tight"); plt.close()
print("ch16 figure done")
for c,l,t,n,cc in rows:
    print(f"  Ch{c:2d} {l:22s} truth {t:<8} naive {str(round(pct(n,t),1) if n else '—'):>7}%  design {pct(cc,t):+6.1f}%")
