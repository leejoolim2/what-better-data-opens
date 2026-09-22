"""Regenerate every figure in the book into figures/output/.  Run: python figures/make_all.py"""
import subprocess, sys, glob, os
here = os.path.dirname(os.path.abspath(__file__)); out = os.path.join(here, "output")
os.makedirs(out, exist_ok=True); failed = []
for s in sorted(glob.glob(os.path.join(here, "make_ch*_figs.py"))):
    r = subprocess.run([sys.executable, s], cwd=out, capture_output=True, text=True)
    print(("ok    " if r.returncode == 0 else "FAIL  ") + os.path.basename(s))
    if r.returncode: failed.append(s); print(r.stderr[-400:])
print(f"{len(glob.glob(os.path.join(out, '*.png')))} figures in figures/output/")
sys.exit(1 if failed else 0)
