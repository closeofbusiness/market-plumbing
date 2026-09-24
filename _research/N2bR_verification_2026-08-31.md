# N2bR verification — 2026-08-31. Grok adversarial review of the z_k build
**Return preserved verbatim: `N2bR_zk_Review_Return_paste.md`. Outcome: Claim 3 (my headline)
FALLS — C-070. Claims 1, 2, 4, 5 stand with amendments, all folded into the doc's §7.**

## Re-measured in-house, all CONFIRMED
- **The endpoint artefact.** Recomputed Fed-inclusive z_k from my own history CSVs at nine
  dates: 15.32 / 17.85 / 19.99 / 19.05 / 18.76 / 20.03 / 19.52 / 19.46 / 19.05 (%) for
  2021-12, 2022-12, 2023-06, 2023-12, 2024-12, 2025-06, 2025-12, 2026-06, 2026-07. Grok's
  independently computed values match mine **to the decimal at five of six** dates it quoted;
  the sixth (2026-06) differs 0.03pp, explained by ALFRED-vs-current-H.6 M2 vintage
  (23,155.2 vs 23,115.2). My "flat" result was two endpoints that coincided at 19.05%.
- **The attribution failure.** MMF Treasuries 2,269.5 → 3,452.6 = **+1,183.1bn** over the same
  window in which the RRP drained 961.9bn; MMF AUM +2,010.6bn. Both from my own history files.
  The drain is smaller than the Treasury build alone, so "78.8% of private-repo growth is the
  RRP" compares two similar-sized stock changes and pins nothing.
- **The Form PF time series exists** — `hf_reverse_repo_exposure_bn` = 1,399.0 at 2026-03-31 is
  already in `data/series.tsv`. v1 claimed no comparable series existed for the hedge-fund leg;
  it was in our own data layer.
- The category-error argument (ON RRP funds the central bank, not a bank, so a Fed-inclusive
  measure is not z_k) is definitional and correct on WP/11/289's own wording.

## Not verified here
FRED-hosted series Grok cited (RMFSL, CURRSL, BOGZ1FL103020005Q, BOGZ1FL763169330Q,
LTDACBM027NBOG at 2,538.087) — fred.stlouisfed.org is unreachable from this sandbox (documented
in `bin/pull_series.py`). Its H.8/H.6 numbers that I *could* reach all matched. The FHLB and
corporate-deposit figures are relayed **unverified**.

## Scoreboard
Sixth external review; the fifth to break something load-bearing. This one broke my own
headline within hours of my publishing it, on the exact risk I had written into the parcel.
