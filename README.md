# What Better Data Opens — code and data

Companion repository for **Joolim Lee, *What Better Data Opens: Structure, Identification, and
Spatial Causality for Urban Research*** (Urban Research Methods, Volume 2, 2026).

Volume 1, [*Starting With What You Have*](https://github.com/leejoolim2/starting-with-what-you-have),
showed what can be learned from the data a city already holds and drew a firm line at claims of
cause. This volume crosses that line. Every number and figure in the book is produced by the code
in this repository, and every notebook ends by checking its results against the printed book.

[![Code: MIT](https://img.shields.io/badge/code-MIT-blue.svg)](LICENSE)
[![Data: CC0](https://img.shields.io/badge/data-CC0%201.0-lightgrey.svg)](data/LICENSE)

> **The data are synthetic.** Every file in `data/` is simulated on the schema of a real public
> source — VIIRS nightlights, geoBoundaries, DHS, World Bank WDI — but none of it measures a real
> place. The datasets exist so that each method can be checked against a known answer. **Do not
> cite them as evidence about any city or policy.**

---

## Quick start

```bash
git clone https://github.com/leejoolim2/what-better-data-opens.git
cd what-better-data-opens
pip install -r requirements.txt

python scripts/verify.py        # every dataset still recovers its planted truth
bash notebooks/run_all.sh       # every notebook reproduces its chapter and checks it
python figures/make_all.py      # every figure in the book, into figures/output/
```

Each command reports a failure if anything does not reproduce. The full run takes a few minutes
on a laptop. To read rather than run, open any notebook in `notebooks/` on GitHub — outputs are
saved.

---

## Chapter map

Every dataset carries a known answer, planted before the analysis was written. The table shows
what a conventional analysis concludes and what the chapter's design recovers.

| Ch. | Design | Notebook | Planted truth | Naive estimate | Design-based |
|:--|:--|:--|--:|--:|--:|
| 1 | Adjustment for confounding | `ch01_identification` | 3.0 | 6.96 | 3.12 |
| 3 | Building a panel from satellites | `ch03_panel` | −0.22 | — | −0.194 |
| 4 | Latent constructs | `ch04_measurement` | 0.42 | 0.309 (one item) | 0.410 (three items) |
| 5 | Multilevel models | `ch05_multilevel` | ICC 0.18 | — | ICC 0.214 |
| 6 | Panel fixed effects | `ch06_fixed_effects` | *(machinery; no treatment)* | | |
| 7 | Difference-in-differences | `ch07_did` | 0.060 | 0.124 (before–after) | 0.0588 |
| 8 | Staggered adoption | `ch08_staggered` | 0.0570 | 0.0500 (TWFE) | 0.0566 |
| 9 | Matching and weighting | `ch09_matching` | 5.0 | 14.94 | 5.22 |
| 10 | Instrumental variables | `ch10_iv` | 0.15 | 0.470 (OLS) | 0.151 |
| 11 | Regression discontinuity | `ch11_rdd` | 120 | — | 124.2 |
| 12 | Synthetic control | `ch12_scm` | 5.73 | — | 4.68 |
| 13 | Spatial regression | `ch13_spatial` | 0.0333 (total effect) | 0.0196 (OLS coef.) | 0.0362 |
| 14 | Spillovers | `ch14_spillover` | 0.060 / 0.020 | 0.0568 | 0.0622 / 0.0211 |

Chapters 2, 15 and 16 have no analysis of their own. Where recovery is deliberately imperfect —
Chapter 12's conservative bias, Chapter 13's inflated spatial parameter — the reason is explained
in the chapter and in [`answers/true_parameters.md`](answers/true_parameters.md).

---

## Repository layout

```
what-better-data-opens/
├─ data/            13 synthetic datasets on real schemas (CC0)
├─ schemas/         SCHEMA.md — which real source each file copies, column by column
├─ notebooks/       one notebook per method chapter; run_all.sh executes them all
├─ figures/         one script per chapter; make_all.py regenerates every book figure
├─ scripts/         make_data.py (generator) and verify.py (planted-truth checks)
├─ acquisition/     scripts that fetch the REAL sources for your own city
└─ answers/         planted truths and how well each design recovers them
```

---

## Using your own data

The synthetic files copy the real sources' column names, units and coordinate systems. Replace a
file with real data under the same column names and the chapter's notebook runs unchanged. The
final check against the book will then fail, as it should: your data are not the book's.

| To obtain | Script | Source |
|:--|:--|:--|
| Monthly night-time lights by district | `acquisition/01_viirs_nightlights.js` | VIIRS DNB monthly (Google Earth Engine, free account) |
| Administrative boundaries | `acquisition/02_geoboundaries.py` | geoBoundaries |
| Population and terrain slope | `acquisition/03_worldpop_srtm.py` | WorldPop, SRTM |
| Country indicators | `acquisition/04_wdi_panel.py` | World Bank WDI |

Fetched files go to `data/real/`, which is excluded from version control. Two warnings from the
book: always keep the VIIRS `cf_cvg` band, because a zero radiance does not mean no lights were
observed (Chapter 3); and record which geoBoundaries vintage you downloaded, because boundaries
change (Section 3.5.3).

---

## Without writing code

Every chapter has a *Tools and Flow* section that carries out the same analysis with free
graphical software — GeoDa, QGIS, jamovi, gretl, Google Earth Engine, or a spreadsheet. Appendix C
of the book maps each procedure to its Python and R equivalents.

---

## Reproducibility

- `scripts/make_data.py` sets one named seed per dataset; regenerating the data is byte-identical.
- `scripts/verify.py` checks every planted truth and exits non-zero on any failure.
- Each notebook's last cell compares its results with the numbers printed in the book. Before
  publication that check caught a rounding error in the manuscript (Section 9.5.6).
- Tested versions are pinned in `requirements.txt`.

---

## The series

| Volume | Title | Repository |
|:--|:--|:--|
| 1 | *Starting With What You Have: Quantitative and Spatial Methods for Urban Research in the Global South* | [starting-with-what-you-have](https://github.com/leejoolim2/starting-with-what-you-have) |
| 2 | *What Better Data Opens: Structure, Identification, and Spatial Causality for Urban Research* | this repository |

---

## Licence

- **Code** — [MIT](LICENSE)
- **Data** — [CC0 1.0](data/LICENSE), public domain dedication

Both permit use, modification and redistribution, including commercially, without permission.

## Citation

See [`CITATION.cff`](CITATION.cff), or use GitHub's *Cite this repository* button.

## Errors

If a notebook fails its final check on your machine, or you find an error in the book, please
[open an issue](https://github.com/leejoolim2/what-better-data-opens/issues) with the notebook
name, the failing value, and the output of `pip freeze`.
