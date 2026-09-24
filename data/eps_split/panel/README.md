# EPS-split firm panel (d3)

Per-firm diluted-share panel behind `2026-09-18-EPS-Split.md` / C-093.

Landed 24 Sep 2026 from executor `/workspace/tdr/data/eps_split/panel/`. Raw `companyfacts/` JSON (≈1.8 GB) was **not** copied (size; regenerable from SEC with `SEC_UA`).

Primary analytic files:
- `diluted_waso_firm_year.csv` / `diluted_waso_splitadj_v2.csv` — firm-year diluted WASO
- `firm_dlog_shares_weighted_v2.csv` — weighted Δlog shares
- `firm_year_shares_mcap_v2.csv` — firm-year shares × mcap weights
- `entity_shares_*`, `repurchase_*`, `sbc_*`, `ratio_outliers*_v2.csv` — supporting pulls
- `yahoo_splits.csv`, 1,511 stock-split events from Yahoo Finance, is third-party data. It is kept in the private companion
  under the same path, not here (THE_ASK E-010); `.gitignore` keeps a local copy out of commits. The `*_splitadj*` files are derived from it.

Scalars: see `../results_v2.json` (already in repo).
