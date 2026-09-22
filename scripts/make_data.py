"""
Urban Research Methods · Volume 2 — "What Better Data Opens"
Synthetic data generator with real-schema replication
=============================================================

DESIGN PRINCIPLE
----------------
Every synthetic file replicates the *exact schema* of a real public source:
column names, coordinate reference system, units, code systems, and missing-data
patterns. A reader who obtains the real file for their own country can drop it in
place and the book's code runs unchanged.

Each dataset carries a planted true value so the reader can check whether the
estimator recovers it. Truths are recorded in answers/true_parameters.md.

Run:  python scripts/make_data.py
Requires: numpy, pandas
"""

import json, os
import numpy as np
import pandas as pd

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

SEEDS = {"ch01": 101, "ch03": 303, "ch04": 404, "ch05": 505, "ch07": 707,
         "ch08": 808, "ch09": 909, "ch10": 171, "ch11": 122, "ch12": 112,
         "ch13": 113, "ch14": 114}

# Six-city set used throughout the book.
CITIES = [
    # name, iso3, adm1 label, n_adm2 units, lon0, lat0 (approximate city centre)
    ("Phnom Penh",   "KHM", "Phnom Penh",      14, 104.92, 11.56),
    ("Hanoi",        "VNM", "Ha Noi",          30, 105.83, 21.03),
    ("Tashkent",     "UZB", "Toshkent Shahri", 12,  69.24, 41.31),
    ("Nairobi",      "KEN", "Nairobi",         17,  36.82, -1.29),
    ("Philadelphia", "USA", "Philadelphia",    12, -75.16, 39.95),
    ("Manchester",   "GBR", "Manchester",      32,  -2.24, 53.48),
]


def out(*parts):
    p = os.path.join(ROOT, *parts)
    os.makedirs(os.path.dirname(p), exist_ok=True)
    return p


def write(df, *parts):
    df.to_csv(out(*parts), index=False, encoding="utf-8")
    return os.path.join(*parts)


# ══════════════════════════════════════════════════════════════════
# Shared: geoBoundaries-style ADM2 frame
#   Schema source: geoBoundaries ADM2 (shapeName, shapeISO, shapeID,
#   shapeGroup, shapeType). Real files: geoboundaries.org
# ══════════════════════════════════════════════════════════════════
def build_admin_frame(rng):
    rows = []
    for city, iso3, adm1, n_units, lon0, lat0 in CITIES:
        for i in range(1, n_units + 1):
            rows.append({
                "shapeID":    f"{iso3}-ADM2-{i:03d}",
                "shapeName":  f"{city} District {i}",
                "shapeISO":   f"{iso3}.{i}",
                "shapeGroup": iso3,
                "shapeType":  "ADM2",
                "adm1_name":  adm1,
                "city":       city,
                # centroid in WGS84 (EPSG:4326), as geoBoundaries provides
                "lon": round(lon0 + rng.normal(0, .055), 5),
                "lat": round(lat0 + rng.normal(0, .045), 5),
                "area_km2": round(float(rng.gamma(3.0, 6.0) + 2), 2),
            })
    df = pd.DataFrame(rows)
    df["dist_cbd_km"] = np.nan
    for city, _, _, _, lon0, lat0 in CITIES:
        m = df.city == city
        df.loc[m, "dist_cbd_km"] = np.sqrt(
            ((df.loc[m, "lon"] - lon0) * 111 * np.cos(np.radians(lat0))) ** 2
            + ((df.loc[m, "lat"] - lat0) * 111) ** 2).round(3)
    return df


# ══════════════════════════════════════════════════════════════════
# CH 1 · From Description to Cause
#   Observational vs randomised versions of the same population.
#   True ATE = 3.0 percentage points.
# ══════════════════════════════════════════════════════════════════
def make_ch01():
    rng = np.random.default_rng(SEEDS["ch01"])
    n = 400
    TRUE_ATE = 3.0

    prior_footfall = rng.normal(50, 15, n).clip(10, 100)   # confounder
    floor_area     = rng.lognormal(3.6, .45, n).clip(15, 300)
    dist_market_m  = rng.gamma(2.0, 250, n).clip(30, 2000)

    # Observational: high-footfall areas are far more likely to be selected
    p = 1 / (1 + np.exp(-(-6.5 + .115 * prior_footfall - .0006 * dist_market_m)))
    program = rng.binomial(1, p)

    base = (-4.0 + .22 * prior_footfall + .004 * floor_area - .0008 * dist_market_m)
    sales_growth = base + TRUE_ATE * program + rng.normal(0, 2.5, n)

    program_rct = rng.binomial(1, .5, n)
    sales_growth_rct = base + TRUE_ATE * program_rct + rng.normal(0, 2.5, n)

    df = pd.DataFrame({
        "area_id": [f"PP-{i:03d}" for i in range(1, n + 1)],
        "city": "Phnom Penh",
        "prior_footfall": prior_footfall.round(1),
        "floor_area_m2": floor_area.round(1),
        "dist_market_m": dist_market_m.round(0),
        "program": program,
        "sales_growth_pct": sales_growth.round(2),
        "program_rct": program_rct,
        "sales_growth_rct_pct": sales_growth_rct.round(2),
    })
    return write(df, "data", "ch01_identification.csv"), {"true_ate": TRUE_ATE, "n": n}


# ══════════════════════════════════════════════════════════════════
# CH 3 / CH 6 · Nightlights panel  (+ boundary-change scenario)
#   Schema source: NOAA VIIRS DNB Monthly V1 (VCMSLCFG) aggregated to ADM2.
#   Real bands: avg_rad (nW/cm2/sr), cf_cvg (cloud-free coverage count).
# ══════════════════════════════════════════════════════════════════
def make_ch03(admin):
    rng = np.random.default_rng(SEEDS["ch03"])
    months = pd.date_range("2019-01-01", "2024-12-01", freq="MS")

    rows = []
    for _, u in admin.iterrows():
        base = np.exp(2.6 - .06 * u.dist_cbd_km + rng.normal(0, .35))
        trend = rng.normal(.0035, .0012)
        for k, m in enumerate(months):
            # seasonal + monsoon cloud effect on coverage
            seas = .04 * np.sin(2 * np.pi * k / 12)
            covid = -.22 if pd.Timestamp("2020-04-01") <= m <= pd.Timestamp("2020-08-01") else 0.0
            rad = base * np.exp(trend * k + seas + covid + rng.normal(0, .06))
            cf = int(np.clip(rng.poisson(14) - (8 if m.month in (6, 7, 8, 9) else 0), 0, 31))
            rows.append({
                "shapeID": u.shapeID, "city": u.city, "shapeGroup": u.shapeGroup,
                "date": m.strftime("%Y-%m-01"),
                "avg_rad": round(float(rad), 4),
                "cf_cvg": cf,
                "n_pixels": int(u.area_km2 * 4.3),
                "area_km2": u.area_km2,
            })
    panel = pd.DataFrame(rows)
    # Real VIIRS is unusable where cloud-free coverage is zero
    panel.loc[panel.cf_cvg == 0, "avg_rad"] = np.nan

    # ---- Boundary change actually present in the panel -------------------
    # From 2022-01 three Tashkent districts are split in two. The old IDs stop
    # appearing and six new IDs begin. The panel is therefore NOT consistent
    # across the break; Chapter 3 asks the reader to repair it.
    split_ids = sorted(admin[admin.city == "Tashkent"].shapeID)[:3]
    brk = "2022-01-01"
    after = panel[(panel.shapeID.isin(split_ids)) & (panel.date >= brk)].copy()
    panel = panel.drop(after.index)
    halves = []
    for suffix, tilt in (("A", 1.22), ("B", 0.78)):     # denser core vs periphery
        h = after.copy()
        h["shapeID"] = h.shapeID + "-" + suffix
        h["avg_rad"] = (h.avg_rad * tilt * np.exp(rng.normal(0, .03, len(h)))).round(4)
        h["area_km2"] = (h.area_km2 / 2).round(2)
        h["n_pixels"] = (h.n_pixels // 2).astype(int)
        halves.append(h)
    panel = pd.concat([panel] + halves, ignore_index=True)
    panel = panel.sort_values(["shapeID", "date"]).reset_index(drop=True)

    # Boundary change: Tashkent splits 3 districts into 6 from 2022-01
    tk = split_ids
    xw = []
    for old in tk:
        for s in ("A", "B"):
            xw.append({"old_shapeID": old, "new_shapeID": f"{old}-{s}",
                       "effective_from": "2022-01-01", "area_share": 0.5})
    for sid in sorted(admin[admin.city == "Tashkent"].shapeID)[3:]:
        xw.append({"old_shapeID": sid, "new_shapeID": sid,
                   "effective_from": "2022-01-01", "area_share": 1.0})
    crosswalk = pd.DataFrame(xw)

    f1 = write(panel, "data", "ch03_viirs_panel_adm2.csv")
    f2 = write(crosswalk, "data", "ch03_boundary_crosswalk_tashkent.csv")
    return (f1, f2), {"months": len(months), "units": len(admin),
                      "obs": len(panel), "missing_pct": round(panel.avg_rad.isna().mean() * 100, 1),
                      "planted": "COVID dip Apr-Aug 2020 (-22% log)"}


# ══════════════════════════════════════════════════════════════════
# CH 4 / CH 5 · DHS-schema household survey (Nairobi)
#   Schema source: DHS Household Recode. Real variable names retained:
#   hhid, hv001 cluster, hv002 household, hv005 weight, hv009 size,
#   hv024 region, hv025 urban/rural, hv270 wealth quintile, hv206 electricity,
#   hv201 water source, hv205 toilet type, hv271 wealth score.
# ══════════════════════════════════════════════════════════════════
def make_ch04():
    rng = np.random.default_rng(SEEDS["ch04"])
    n_clusters, hh_per = 60, 25

    # Cluster-level context (level 2). ICC target ≈ 0.18
    ctx_infra = rng.normal(0, 1, n_clusters)                 # neighbourhood infrastructure
    u_cluster = rng.normal(0, np.sqrt(.18), n_clusters)      # random intercept

    rows = []
    for c in range(n_clusters):
        for h in range(hh_per):
            size = int(np.clip(rng.poisson(4.2) + 1, 1, 15))
            wealth_score = (.55 * ctx_infra[c] + rng.normal(0, .8))
            quint = int(np.clip(np.digitize(wealth_score, [-1.0, -.3, .3, 1.0]) + 1, 1, 5))
            elec = int(rng.random() < 1 / (1 + np.exp(-(0.2 + 1.1 * wealth_score))))
            water = int(rng.choice([11, 12, 13, 21, 31, 32],
                                   p=[.22, .18, .12, .18, .18, .12]))  # DHS hv201 codes
            toilet = int(rng.choice([11, 12, 21, 22, 31],
                                    p=[.20, .25, .25, .20, .10]))      # DHS hv205 codes

            # Latent constructs (Ch.4 PLS-SEM): service access -> satisfaction
            serv = (.45 * elec + .35 * (water < 20) + .30 * (toilet < 20)
                    + .25 * ctx_infra[c] + rng.normal(0, .5))
            TRUE_PATH = 0.42
            satis_latent = TRUE_PATH * serv + .18 * wealth_score + rng.normal(0, .6)
            # three reflective indicators per construct, 5-point Likert
            def lik(x, load, noise=.38):
                return int(np.clip(round(3 + load * x + rng.normal(0, noise)), 1, 5))

            rows.append({
                "hhid":  f"{c+1:04d} {h+1:03d}",
                "hv001": c + 1, "hv002": h + 1,
                "hv005": int(rng.normal(1_000_000, 120_000)),
                "hv009": size,
                "hv024": 1, "hv025": 1,                    # Nairobi, urban
                "hv201": water, "hv205": toilet, "hv206": elec,
                "hv270": quint, "hv271": round(wealth_score * 100000),
                "serv_1": lik(serv, .92), "serv_2": lik(serv, .86), "serv_3": lik(serv, .80),
                "sat_1":  lik(satis_latent, .90), "sat_2": lik(satis_latent, .86),
                "sat_3":  lik(satis_latent, .82),
                "ctx_infra_index": round(float(ctx_infra[c]), 3),
                "y_wellbeing": round(float(2.8 + .55 * satis_latent + u_cluster[c]
                                           + .30 * ctx_infra[c] + rng.normal(0, 1.0)), 3),
            })
    df = pd.DataFrame(rows)
    return write(df, "data", "ch04_dhs_household_nairobi.csv"), {
        "n_households": len(df), "n_clusters": n_clusters,
        "true_path_serv_to_sat": 0.42, "target_icc": 0.18}


# ══════════════════════════════════════════════════════════════════
# CH 7 · Difference-in-Differences (Hanoi ring-road opening)
# ══════════════════════════════════════════════════════════════════
def make_ch07():
    rng = np.random.default_rng(SEEDS["ch07"])
    TRUE = 0.060
    units = [f"VNM-ADM2-{i:03d}" for i in range(1, 41)]
    months = pd.date_range("2022-01-01", periods=36, freq="MS")
    treated = set(rng.choice(units, 15, replace=False))
    open_m = pd.Timestamp("2024-01-01")

    fe = {u: rng.normal(2.35, .28) - (.12 if u in treated else 0) for u in units}
    rows = []
    for u in units:
        for k, m in enumerate(months):
            tr, po = int(u in treated), int(m >= open_m)
            y = (fe[u] + .0035 * k + .012 * np.sin(2 * np.pi * k / 12)
                 + TRUE * tr * po + rng.normal(0, .035))
            rows.append({"shapeID": u, "city": "Hanoi", "date": m.strftime("%Y-%m-01"),
                         "t": k + 1, "treated": tr, "post": po, "treat_post": tr * po,
                         "log_avg_rad": round(y, 4),
                         "pop_density": round(float(rng.normal(9800, 2600)), 0)})
    return write(pd.DataFrame(rows), "data", "ch07_did_hanoi.csv"), {
        "true_effect_log": TRUE, "true_effect_pct": round((np.exp(TRUE) - 1) * 100, 2),
        "n_units": 40, "n_treated": 15, "treatment": "2024-01"}


# ══════════════════════════════════════════════════════════════════
# CH 8 · Staggered adoption
# ══════════════════════════════════════════════════════════════════
def make_ch08():
    rng = np.random.default_rng(SEEDS["ch08"])
    units = [f"UNIT-{i:02d}" for i in range(1, 61)]
    months = pd.date_range("2022-01-01", periods=48, freq="MS")
    sh = list(rng.permutation(units))
    cohort = {}
    cohort.update({u: pd.Timestamp("2023-01-01") for u in sh[:15]})
    cohort.update({u: pd.Timestamp("2023-07-01") for u in sh[15:30]})
    cohort.update({u: pd.Timestamp("2024-01-01") for u in sh[30:45]})
    for u in sh[45:]:
        cohort[u] = pd.NaT

    fe = {u: rng.normal(2.35, .30) for u in units}
    rows = []
    for u in units:
        g = cohort[u]
        for k, m in enumerate(months):
            if pd.isna(g):
                rel, eff = np.nan, 0.0
            else:
                rel = (m.year - g.year) * 12 + (m.month - g.month)
                eff = 0.0 if rel < 0 else min(.015 * (rel + 1), .06)
            rows.append({"shapeID": u, "date": m.strftime("%Y-%m-01"), "t": k + 1,
                         "cohort": "never" if pd.isna(g) else g.strftime("%Y-%m"),
                         "first_treat_t": 0 if pd.isna(g) else int((g.year - 2022) * 12 + g.month),
                         "rel_time": "" if pd.isna(rel) else int(rel),
                         "treat_now": 0 if (pd.isna(g) or m < g) else 1,
                         "log_avg_rad": round(fe[u] + .0032 * k + eff + rng.normal(0, .033), 4)})
    return write(pd.DataFrame(rows), "data", "ch08_did_staggered.csv"), {
        "dynamic": "+0.015 per month, saturating at 0.06",
        "cohorts": "2023-01 / 2023-07 / 2024-01 / never", "n_units": 60}


# ══════════════════════════════════════════════════════════════════
# CH 9 · Matching and weighting (Phnom Penh business upgrading)
# ══════════════════════════════════════════════════════════════════
def make_ch09():
    rng = np.random.default_rng(SEEDS["ch09"])
    n, TRUE_ATT = 800, 5.0
    pre_sales   = rng.normal(100, 22, n).clip(40, 190)
    floor_area  = rng.lognormal(3.4, .5, n).clip(10, 250)
    dist_road_m = rng.gamma(2.2, 220, n).clip(20, 1800)
    frontage_m  = rng.normal(6, 2.2, n).clip(2, 15)
    years_open  = rng.integers(1, 31, n)

    p = 1 / (1 + np.exp(-(-4.6 + .030 * pre_sales + .010 * floor_area
                          - .0011 * dist_road_m + .14 * frontage_m - .02 * years_open)))
    treat = rng.binomial(1, p)
    post = (18 + .82 * pre_sales + .05 * floor_area - .0016 * dist_road_m
            + .5 * frontage_m + TRUE_ATT * treat + rng.normal(0, 5.5, n))

    df = pd.DataFrame({
        "biz_id": [f"KHM-B{i:04d}" for i in range(1, n + 1)],
        "city": "Phnom Penh",
        "pre_sales_index": pre_sales.round(1),
        "floor_area_m2": floor_area.round(1),
        "dist_road_m": dist_road_m.round(0),
        "frontage_m": frontage_m.round(1),
        "years_open": years_open,
        "program": treat,
        "post_sales_index": post.round(1)})
    return write(df, "data", "ch09_matching_phnompenh.csv"), {"true_att": TRUE_ATT, "n": n}


# ══════════════════════════════════════════════════════════════════
# CH 10 · Instrumental variables — terrain slope as instrument
#   Schema source: SRTM 30m elevation -> slope (degrees)
# ══════════════════════════════════════════════════════════════════
def make_ch10():
    rng = np.random.default_rng(SEEDS["ch10"])
    n, TRUE_BETA = 800, 0.15
    unobs_potential = rng.normal(0, 1, n)                     # unobserved confounder
    slope_deg = rng.gamma(2.0, 2.2, n).clip(.2, 24)           # instrument (SRTM)

    transit_access = (5.0 - .24 * slope_deg + .70 * unobs_potential + rng.normal(0, .5, n))
    log_price = (7.2 + TRUE_BETA * transit_access + .60 * unobs_potential
                 + .002 * rng.normal(78, 18, n) + rng.normal(0, .25, n))

    df = pd.DataFrame({
        "shapeID": [f"KHM-ADM3-{i:03d}" for i in range(1, n + 1)],
        "slope_deg_srtm": slope_deg.round(3),
        "elevation_m": (12 + slope_deg * 6 + rng.normal(0, 8, n)).round(1),
        "transit_access_index": transit_access.round(3),
        "mean_floor_area_m2": rng.normal(78, 18, n).round(1).clip(30, 160),
        "building_age_yr": rng.integers(1, 41, n),
        "log_land_price": log_price.round(4)})
    return write(df, "data", "ch10_iv_slope.csv"), {
        "true_beta": TRUE_BETA, "instrument": "slope_deg_srtm",
        "endogenous": "transit_access_index", "n": n}


# ══════════════════════════════════════════════════════════════════
# CH 11 · Regression discontinuity — population-based fiscal transfer
# ══════════════════════════════════════════════════════════════════
def make_ch11():
    rng = np.random.default_rng(SEEDS["ch11"])
    n, CUT, TRUE_JUMP = 900, 50000, 120.0
    pop = rng.normal(CUT, 14000, n).clip(15000, 95000)
    run = pop - CUT
    elig = (run >= 0).astype(int)
    invest = (380 + .0042 * run + 9.0e-9 * run ** 2 + TRUE_JUMP * elig
              + rng.normal(0, 85, n))
    df = pd.DataFrame({
        "muni_id": [f"KEN-M{i:03d}" for i in range(1, n + 1)],
        "population": pop.round(0),
        "running": run.round(0),
        "eligible": elig,
        "invest_per_capita_usd": invest.round(1),
        "region_type": rng.choice(["metropolitan", "secondary", "rural"], n, p=[.3, .25, .45]),
        "share_under15_pct": rng.normal(41, 5, n).round(1).clip(20, 60)})
    return write(df, "data", "ch11_rdd_transfer.csv"), {
        "true_jump": TRUE_JUMP, "cutoff": CUT, "n": n, "design": "sharp"}


# ══════════════════════════════════════════════════════════════════
# CH 12 · Synthetic control — one city adopts a transit policy
#   Schema source: World Bank WDI indicator codes
# ══════════════════════════════════════════════════════════════════
def make_ch12():
    rng = np.random.default_rng(SEEDS["ch12"])
    cities = [f"CITY-{i:02d}" for i in range(1, 31)]
    years = list(range(2000, 2024))
    TREATED, TYEAR = "CITY-07", 2015

    base  = {c: rng.normal(38, 6) for c in cities}
    slope = {c: rng.normal(.35, .20) for c in cities}
    common = np.cumsum(rng.normal(0, .5, len(years)))

    rows = []
    for c in cities:
        dens = rng.normal(4200, 900); gdp = rng.normal(2800, 600); car = rng.normal(.38, .07)
        for i, yr in enumerate(years):
            eff = min(1.2 * (yr - TYEAR + 1), 9.0) if (c == TREATED and yr >= TYEAR) else 0.0
            val = (base[c] + slope[c] * i + common[i] + eff
                   + .0009 * dens - 6.0 * car + rng.normal(0, .8))
            rows.append({
                "city_id": c, "year": yr,
                "transit_share_pct": round(val, 3),
                "EN_POP_DNST": round(dens + rng.normal(0, 40), 0),      # WDI code
                "NY_GDP_PCAP_CD": round(gdp * (1 + .02 * i) + rng.normal(0, 50), 0),
                "IS_VEH_NVEH_P3": round(car + .004 * i + rng.normal(0, .005), 4),
                "treated": int(c == TREATED), "post": int(yr >= TYEAR)})
    return write(pd.DataFrame(rows), "data", "ch12_scm_cities.csv"), {
        "treated_unit": TREATED, "treat_year": TYEAR,
        "true_effect": "+1.2 p.a. cumulative, capped at +9.0", "n_donors": 29}


# ══════════════════════════════════════════════════════════════════
# CH 13 · Spatial regression — grid city with autocorrelation
# ══════════════════════════════════════════════════════════════════
def make_ch13():
    rng = np.random.default_rng(SEEDS["ch13"])
    ncol = nrow = 18
    cell = 1000.0
    ix, iy = np.meshgrid(np.arange(ncol), np.arange(nrow))
    ix, iy = ix.ravel(), iy.ravel()
    n = len(ix)
    cx, cy = ix * cell + cell / 2, iy * cell + cell / 2
    d_cbd = np.sqrt((cx - 7.5 * cell) ** 2 + (cy - 9.5 * cell) ** 2) / 1000

    D = np.sqrt((cx[:, None] - cx[None, :]) ** 2 + (cy[:, None] - cy[None, :]) ** 2) / 1000
    K = np.exp(-(D / 2.2) ** 2); K /= K.sum(1, keepdims=True)
    field = K @ rng.normal(0, 1, n); field = (field - field.mean()) / field.std()

    built   = (52 - 1.9 * d_cbd + 7 * rng.normal(0, 1, n)).clip(5, 95)
    green   = (18 + 1.4 * d_cbd + 5 * rng.normal(0, 1, n)).clip(1, 70)
    pop_den = (14000 - 620 * d_cbd + 2600 * rng.normal(0, 1, n)).clip(300, 40000)

    # Spatially lagged dependent structure: y = (I - rho W)^-1 (Xb + e), rho = 0.61
    RHO = 0.61
    W = ((np.abs(ix[:, None] - ix) + np.abs(iy[:, None] - iy)) == 1).astype(float)
    W = W / W.sum(1, keepdims=True)
    Xb = 6.9 + .013 * built - .004 * green + .000012 * pop_den + .12 * field
    y = np.linalg.solve(np.eye(n) - RHO * W, Xb + rng.normal(0, .10, n))

    df = pd.DataFrame({
        "cell_id": [f"G{i:03d}" for i in range(1, n + 1)],
        "col": ix, "row": iy,
        "x_m": cx.round(1), "y_m": cy.round(1),
        "dist_cbd_km": d_cbd.round(3),
        "built_up_pct": built.round(2),
        "green_pct": green.round(2),
        "pop_density": pop_den.round(0),
        "log_land_value": y.round(4)})
    return write(df, "data", "ch13_spatial_grid.csv"), {
        "true_rho": RHO, "n_cells": n, "weights": "rook, row-standardised"}


# ══════════════════════════════════════════════════════════════════
# CH 14 · Spillover — treatment effect leaks into neighbours
#   Direct 0.06, spillover 0.02 within 2 km. Ignoring spillover
#   attenuates the naive DID estimate.
# ══════════════════════════════════════════════════════════════════
def make_ch14():
    rng = np.random.default_rng(SEEDS["ch14"])
    DIRECT, SPILL, RADIUS = 0.06, 0.02, 2.0
    ncol = nrow = 12
    ix, iy = np.meshgrid(np.arange(ncol), np.arange(nrow))
    ix, iy = ix.ravel(), iy.ravel()
    n = len(ix)
    cx, cy = ix * 1.0, iy * 1.0                      # km grid

    treated_cells = np.zeros(n, dtype=int)
    for c in [(3, 3), (8, 4), (5, 9)]:               # three intervention sites
        treated_cells |= ((ix == c[0]) & (iy == c[1])).astype(int)

    tidx = np.where(treated_cells == 1)[0]
    dmin = np.full(n, np.inf)
    for t in tidx:
        d = np.sqrt((cx - cx[t]) ** 2 + (cy - cy[t]) ** 2)
        dmin = np.minimum(dmin, d)
    in_ring = ((dmin > 0) & (dmin <= RADIUS)).astype(int)

    months = pd.date_range("2022-01-01", periods=36, freq="MS")
    open_m = pd.Timestamp("2024-01-01")
    fe = rng.normal(2.4, .25, n)

    rows = []
    for i in range(n):
        for k, m in enumerate(months):
            post = int(m >= open_m)
            eff = post * (DIRECT * treated_cells[i] + SPILL * in_ring[i])
            rows.append({
                "cell_id": f"C{i+1:03d}", "x_km": cx[i], "y_km": cy[i],
                "date": m.strftime("%Y-%m-01"), "t": k + 1,
                "treated": int(treated_cells[i]),
                "dist_to_treat_km": round(float(dmin[i]), 3),
                "in_spillover_ring": int(in_ring[i]),
                "post": post,
                "log_avg_rad": round(float(fe[i] + .003 * k + eff + rng.normal(0, .030)), 4)})
    return write(pd.DataFrame(rows), "data", "ch14_spillover_panel.csv"), {
        "true_direct": DIRECT, "true_spillover": SPILL, "radius_km": RADIUS,
        "n_cells": n, "n_treated": int(treated_cells.sum()),
        "n_ring": int(in_ring.sum())}


if __name__ == "__main__":
    rng0 = np.random.default_rng(1)
    admin = build_admin_frame(rng0)
    write(admin, "data", "admin_frame_adm2.csv")

    meta = {}
    meta["ch01"] = make_ch01()
    meta["ch03"] = make_ch03(admin)
    meta["ch04"] = make_ch04()
    meta["ch07"] = make_ch07()
    meta["ch08"] = make_ch08()
    meta["ch09"] = make_ch09()
    meta["ch10"] = make_ch10()
    meta["ch11"] = make_ch11()
    meta["ch12"] = make_ch12()
    meta["ch13"] = make_ch13()
    meta["ch14"] = make_ch14()

    with open(out("scripts", "_generation_log.json"), "w", encoding="utf-8") as f:
        json.dump({k: {"files": v[0], "spec": v[1]} for k, v in meta.items()},
                  f, ensure_ascii=False, indent=2, default=str)
    for k, v in meta.items():
        print(f"{k:6s} {v[0]}\n       {v[1]}")
