# Schema Reference

Every synthetic file in `data/` replicates the schema of a real, public source.
Column names, units, coordinate systems, and code values are those of the real data.
**To use your own country's data, replace the file and keep the column names.**

---

## `admin_frame_adm2.csv` — spatial frame
**Replicates:** geoBoundaries ADM2 (`gbOpen`), https://www.geoboundaries.org

| Column | Real source column | Notes |
|---|---|---|
| `shapeID` | `shapeID` | join key used by every other file |
| `shapeName`, `shapeISO`, `shapeGroup`, `shapeType` | identical | `shapeGroup` = ISO3 |
| `lon`, `lat` | centroid, EPSG:4326 | geoBoundaries ships WGS84 |
| `area_km2` | computed | project to a metric CRS before computing |

**Replace with real data:** run `acquisition/02_geoboundaries.py`.

---

## `ch03_viirs_panel_adm2.csv` — nightlights panel (Ch. 3, 6)
**Replicates:** NOAA VIIRS DNB Monthly V1 (`VCMSLCFG`), zonal mean by ADM2

| Column | Real band | Unit |
|---|---|---|
| `avg_rad` | `avg_rad` | nW·cm⁻²·sr⁻¹ |
| `cf_cvg` | `cf_cvg` | count of cloud-free observations in the month |
| `date` | image date | first day of month |

**Missingness is deliberate.** Where `cf_cvg = 0`, `avg_rad` is `NaN` — exactly as in the
real product during monsoon months. Do not impute zero; a zero radiance and an unobserved
radiance are different things.

**Replace with real data:** run `acquisition/01_viirs_nightlights.js` in Earth Engine.

---

## `ch03_boundary_crosswalk_tashkent.csv` — boundary change (Ch. 3)
**Replicates:** the structure of national statistical office crosswalk tables issued when
administrative units are split or merged.

| Column | Meaning |
|---|---|
| `old_shapeID`, `new_shapeID` | unit before / after the change |
| `effective_from` | date the new geography takes effect |
| `area_share` | share of the old unit's area assigned to the new unit |

Use `area_share` to interpolate a consistent panel backwards. Chapter 3 shows why an
unadjusted panel breaks at the change date.

---

## `ch04_dhs_household_nairobi.csv` — household survey (Ch. 4, 5)
**Replicates:** DHS Household Recode. Real DHS variable names are retained.

| Column | DHS meaning | Codes |
|---|---|---|
| `hhid` | household identifier | cluster + household |
| `hv001` / `hv002` | cluster / household number | |
| `hv005` | household sample weight | divide by 1,000,000 |
| `hv009` | number of household members | |
| `hv024` / `hv025` | region / type of residence | 1 = urban |
| `hv201` | source of drinking water | 11–13 piped, 21 tubewell, 31–32 well |
| `hv205` | type of toilet facility | 11–12 flush, 21–22 pit, 31 none |
| `hv206` | has electricity | 0/1 |
| `hv270` / `hv271` | wealth index quintile / score | score ×100000 |
| `serv_1..3`, `sat_1..3` | reflective indicators (5-point) | added for Ch. 4 |
| `ctx_infra_index` | cluster-level context | added for Ch. 5 |

**Replace with real data:** register at https://dhsprogram.com, request the Household
Recode for your country, and keep the `hv*` names. The Chapter 4–5 code will run unchanged
except for the constructed indicators, which come from your own instrument.

---

## `ch10_iv_slope.csv` — terrain instrument (Ch. 10)
**Replicates:** SRTM 30 m elevation, slope in degrees, zonal mean by unit.
`slope_deg_srtm` and `elevation_m` are the standard outputs of `gdaldem slope`.

**Replace with real data:** `acquisition/03_worldpop_srtm.py`.

---

## `ch12_scm_cities.csv` — city panel (Ch. 12)
**Replicates:** World Bank WDI indicator codes as column names.

| Column | WDI code |
|---|---|
| `EN_POP_DNST` | EN.POP.DNST |
| `NY_GDP_PCAP_CD` | NY.GDP.PCAP.CD |
| `IS_VEH_NVEH_P3` | IS.VEH.NVEH.P3 |

**Replace with real data:** `acquisition/04_wdi_panel.py`.

---

## Files with no direct real counterpart

`ch01`, `ch07`, `ch08`, `ch09`, `ch11`, `ch13`, `ch14` encode **policy assignment** —
who was treated, and when. No open dataset provides this for the six study cities, so the
treatment structure is simulated. The *covariates* in these files still follow the schemas
above, and the treatment structures follow real institutional designs:

- `ch11` reproduces the population-threshold fiscal transfer rule found in several
  decentralised systems (Kenya, Indonesia).
- `ch14` reproduces the geometry of point interventions with a defined spillover radius.
