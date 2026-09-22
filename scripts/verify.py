"""
Verify that every dataset recovers its planted truth.
Run:  python scripts/verify.py     (exits non-zero if any check fails)
"""
import sys, warnings
import numpy as np, pandas as pd
import statsmodels.api as sm, statsmodels.formula.api as smf
from scipy.optimize import minimize
warnings.filterwarnings("ignore")

R = lambda f: pd.read_csv("data/" + f)
FAILED = []

def check(label, truth, estimate, tol, note=""):
    good = abs(estimate - truth) <= tol
    if not good:
        FAILED.append(label)
    print(f"{label:5s} truth {truth:>8} | estimate {estimate:8.4f} | "
          f"{'PASS' if good else 'FAIL'}  {note}")

# CH1 -------------------------------------------------------------
d = R("ch01_identification.csv")
adj = smf.ols("sales_growth_pct~program+prior_footfall+floor_area_m2+dist_market_m",
              d).fit().params["program"]
naive = d[d.program == 1].sales_growth_pct.mean() - d[d.program == 0].sales_growth_pct.mean()
check("CH1", 3.0, adj, .6, f"(naive {naive:.2f})")

# CH3 -------------------------------------------------------------
# Book specification (Section 3.5.5): harmonised panel, unit and year fixed effects.
sys.path.insert(0, "notebooks"); from _common import harmonised_panel
h = harmonised_panel()
h["covid"] = ((h.date >= "2020-04-01") & (h.date <= "2020-08-01")).astype(int)
check("CH3", -0.22, smf.ols("log_rad~covid+C(unit)+C(year)", h).fit().params["covid"], .05,
      "(book: -0.1942)")

# CH4 / CH5 -------------------------------------------------------
d = R("ch04_dhs_household_nairobi.csv")
d["serv"] = d[["serv_1", "serv_2", "serv_3"]].mean(axis=1)
d["sat"] = d[["sat_1", "sat_2", "sat_3"]].mean(axis=1)
check("CH4", 0.42, smf.ols("sat~serv", d).fit().params["serv"], .08, "(3-item mean; 1 item gives 0.309)")
m = sm.MixedLM.from_formula("y_wellbeing~1", groups="hv001", data=d).fit()
v = float(m.cov_re.iloc[0, 0])
check("CH5", 0.18, v / (v + m.scale), .06)

# CH7 -------------------------------------------------------------
d = R("ch07_did_hanoi.csv")
check("CH7", 0.060, smf.ols("log_avg_rad~treated+post+treat_post", d).fit().params["treat_post"], .012)

# CH9 -------------------------------------------------------------
d = R("ch09_matching_phnompenh.csv")
check("CH9", 5.0, smf.ols("post_sales_index~program+pre_sales_index+floor_area_m2"
                          "+dist_road_m+frontage_m+years_open", d).fit().params["program"], .8)

# CH10 ------------------------------------------------------------
d = R("ch10_iv_slope.csv")
f1 = smf.ols("transit_access_index~slope_deg_srtm+mean_floor_area_m2+building_age_yr", d).fit()
d["fit"] = f1.fittedvalues
check("CH10", 0.15, smf.ols("log_land_price~fit+mean_floor_area_m2+building_age_yr",
                            d).fit().params["fit"], .04, f"(instrument partial F {f1.tvalues['slope_deg_srtm']**2:.0f})")

# CH11 ------------------------------------------------------------
d = R("ch11_rdd_transfer.csv")
es = [smf.ols("invest_per_capita_usd~eligible*running",
              d[abs(d.running) <= b]).fit().params["eligible"] for b in (20000, 10000, 5000)]
check("CH11", 120.0, float(np.mean(es)), 10, f"(bandwidths {[round(e) for e in es]})")

# CH12 ------------------------------------------------------------
d = R("ch12_scm_cities.csv")
pre = d[d.year < 2015]
w = pre.pivot(index="year", columns="city_id", values="transit_share_pct")
don = [c for c in w.columns if c != "CITY-07"]
r = minimize(lambda v: np.mean((w["CITY-07"].values - w[don].values @ v) ** 2),
             np.repeat(1 / len(don), len(don)), method="SLSQP", bounds=[(0, 1)] * len(don),
             constraints={"type": "eq", "fun": lambda v: v.sum() - 1}, options={"maxiter": 800})
full = d.pivot(index="year", columns="city_id", values="transit_share_pct")
gap = full["CITY-07"].values - full[don].values @ r.x
check("CH12", 9.0, float(gap[-1]), 3, f"(pre-RMSPE {np.sqrt(r.fun):.2f})")

# CH13 ------------------------------------------------------------
d = R("ch13_spatial_grid.csv"); xy = d[["col", "row"]].values
W = ((np.abs(xy[:, 0:1] - xy[:, 0]) + np.abs(xy[:, 1:2] - xy[:, 1])) == 1).astype(float)
W = W / W.sum(1, keepdims=True)
res = smf.ols("log_land_value~built_up_pct+green_pct+pop_density", d).fit().resid.values
mi = (res @ (W @ res)) / (res @ res)
check("CH13", 0.70, mi, .12, "(residual Moran's I, SAR required)")

# CH14 ------------------------------------------------------------
d = R("ch14_spillover_panel.csv")
fl = smf.ols("log_avg_rad~treated:post+in_spillover_ring:post+C(cell_id)+C(date)", d).fit()
check("CH14", 0.06, fl.params["treated:post"], .015, "(direct)")
check("CH14", 0.02, fl.params["in_spillover_ring:post"], .012, "(spillover)")

print("-" * 62)
if FAILED:
    print("FAILED:", ", ".join(FAILED)); sys.exit(1)
print("All checks passed.")
