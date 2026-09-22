# Planted Truths and Recovery

Every dataset carries a known answer, fixed before the analysis was written. This file records
each planted value, what a conventional analysis concludes, and what the chapter's design
recovers. All figures are those printed in the book and reproduced by the notebooks.

| Ch. | Dataset | Planted truth | Naive | Design-based | Error |
|:--|:--|--:|--:|--:|--:|
| 1 | `ch01_identification.csv` | ATE 3.0 | 6.96 (difference in means) | 3.12 (adjusted); 2.92 (randomised arm) | +4% |
| 3 | `ch03_viirs_panel_adm2.csv` | COVID dip −0.22 | — | −0.194 (harmonised, unit + year FE) | −12% |
| 4 | `ch04_dhs_household_nairobi.csv` | path 0.42 | 0.309 (one item) | 0.410 (three items) | −2% |
| 5 | same file | ICC 0.18 | — | 0.214 | sampling |
| 7 | `ch07_did_hanoi.csv` | DID 0.060 | 0.124 (before–after) | 0.0588 | −2% |
| 8 | `ch08_did_staggered.csv` | ATT 0.0570 | 0.0500 (single TWFE) | 0.0566 (cohort-weighted) | −1% |
| 9 | `ch09_matching_phnompenh.csv` | ATT 5.0 | 14.94 | 4.56–5.22 across five estimators | ≤ 9% |
| 10 | `ch10_iv_slope.csv` | β 0.15 | 0.470 (OLS) | 0.151 (2SLS; partial F 677) | +1% |
| 11 | `ch11_rdd_transfer.csv` | jump 120 | — | 124.2 (bandwidth 10) | +4% |
| 12 | `ch12_scm_cities.csv` | mean effect 5.73 | — | 4.68 (p = 0.033) | −18% |
| 13 | `ch13_spatial_grid.csv` | total effect 0.0333; ρ 0.61 | 0.0196 (OLS coefficient) | 0.0362 total; ρ 0.70 | +9% |
| 14 | `ch14_spillover_panel.csv` | direct 0.060; spillover 0.020 | 0.0568 | 0.0622 / 0.0211 | +4% / +6% |

## Where recovery is deliberately imperfect

**Chapter 4 — correction overshoots.** Dividing the three-item estimate by the reliabilities gives
0.507, further from the truth than the uncorrected 0.410. Disattenuation should not be applied to
well-measured constructs (Section 4.5.6).

**Chapter 8 — the naive estimate is biased by design.** The effect grows over time, so a single
two-way fixed effects coefficient uses already-treated units as controls and understates by 12 per
cent. Its event study also shows a pre-trend that does not exist (Section 8.5.3).

**Chapter 12 — synthetic control is conservative.** Weights fitted to the pre-period absorb part
of the treated unit's idiosyncratic variation, so the gap understates the effect. Report such
estimates as likely lower bounds (Section 12.5.4).

**Chapter 13 — ρ absorbs omitted structure.** A spatially smooth amenity that is not in the file
inflates the spatial parameter to 0.70 (GMM) and 0.87 (maximum likelihood) against a planted 0.61.
Total impacts are still recovered within nine per cent. Report impacts; do not interpret ρ
(Section 13.5.7).

## A caution

Every dataset was built so that its design would work: selection in Chapter 9 runs only through
recorded covariates, the instrument in Chapter 10 satisfies the exclusion restriction by
construction, and the running variable in Chapter 11 is not manipulated. The results above show
that the methods recover the truth **when their assumptions hold**. They say nothing about how
often those assumptions hold in real data (Section 16.2).
