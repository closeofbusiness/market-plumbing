# P2b — the cleanest test: does the top 10's share of earnings lag its share of value? (12 Sep 2026)

**Status: DATA, with the first method retracted.** Ranked item 2 (second half). Scripts
`bin/top10_earnings_vs_weight.py` (fetch + single-frame) and `bin/top10_corrected_nearest_instant.py`;
tables `data/p2b_top10/`.

**The answer (corrected measure):** the top 10 companies' share of S&P 500 earnings **led** their share of
float-adjusted value in 2015 (24.5% vs 21.5%), 2017 (27.3% vs 22.8%) and 2019 (30.5% vs 24.5%); the two were
**level** in 2021 (28.8% vs 29.0%) and 2023 (31.4% vs 32.0%); and only in **2025** does value lead earnings,
by **4.3 points** (38.8% vs 34.5%). So concentration has been overwhelmingly earnings-backed, with a modest
gap opening in the most recent year — the part a flow explanation could claim.

**RETRACTED: the first run's headline.** It reported earnings lagging value in 5 of 6 years, with a 10.1-point
gap in 2025. That measure took every company's float from one calendar quarter, which structurally excluded
every company whose fiscal second quarter ends elsewhere — Apple, Microsoft, Costco, P&G, Visa, Oracle and
Nike among them — from the value side while their profits stayed in the earnings side. Both tables are kept
in `data/p2b_top10/` so the difference stays visible; only the corrected one is to be used.

**Supervisor verification (12 Sep):** Apple's float re-pulled from the SEC frame — $3.253trn at 2025-03-28,
matching the agent exactly; Microsoft correctly absent from that frame (its fiscal Q2 ends 31 December, so it
is matched from the prior-quarter frame). Float coverage rose from 76-79% to 92-98% of mapped members.

**Caveats:** `EntityPublicFloat` is a filing-cycle snapshot, not a simultaneous cross-section; the five-frame
window still misses a fiscal Q2 ending in Oct-Dec (2-8 companies a year unmatched); membership comes from a
free historical-constituents dataset; tickers are mapped through SEC's current-ticker file, so older
constituents that were renamed or acquired do not map (coverage rises from 76% in 2015 to 96% in 2025); six
SEC float records with scale errors (up to a million-fold) are excluded and logged.

---

## The agent's return (Sonnet), corrected run

Corrected-method results are complete and consistent (same 6 outlier records independently flagged by the same $5T bound in both runs, confirming the sanity check is robust). Here is the full comparison.

## Headline: the fiscal-misalignment fix changes the finding substantially — it reverses for 3 of 6 years

## (1) Apple and Microsoft confirmation

Both now appear **in the universe and in the top-10 in every single year**, 2015–2025:

| Year | AAPL | MSFT |
|---|---|---|
| 2015 | in top10, $709.9B (end 2015-03-27, this-year Q1) | in top10, $365.3B (end 2014-12-31, prior-year Q4) |
| 2017 | in top10, $747.5B (this-year Q1) | in top10, $466.5B (prior-year Q4) |
| 2019 | in top10, $874.7B (this-year Q1) | in top10, $769.6B (prior-year Q4) |
| 2021 | in top10, $2.021T (this-year Q1) | in top10, $1.700T (prior-year Q4) |
| 2023 | in top10, $2.591T (this-year Q1) | in top10, $1.800T (prior-year Q4) |
| 2025 | in top10, $3.253T (this-year Q1) | in top10, $3.100T (prior-year Q4) |

Apple is consistently matched via `thisQ1I` (its fiscal Q2 ends late March), Microsoft consistently via `prevQ4I` (its fiscal Q2 ends Dec 31 of the prior calendar year) — both with lag ≈ 0 days relative to their own instant, i.e. exactly as their 10-Ks report it. Nothing else needed adjusting for this to work; the mechanism behaved as expected.

## (2) Year table: both measures, with the gap

| Year | Weight (orig) | Earnings (orig) | Gap orig (W−E) | Weight (corrected) | Earnings (corrected) | Gap corrected (W−E) |
|---|---|---|---|---|---|---|
| 2015 | 0.2075 | 0.1831 | **+0.0244** (lags) | 0.2152 | 0.2446 | **−0.0294** (leads) |
| 2017 | 0.2303 | 0.2003 | **+0.0301** (lags) | 0.2277 | 0.2725 | **−0.0448** (leads) |
| 2019 | 0.2365 | 0.2413 | −0.0048 (≈parity) | 0.2450 | 0.3051 | **−0.0600** (leads) |
| 2021 | 0.2650 | 0.2204 | **+0.0446** (lags) | 0.2899 | 0.2882 | +0.0017 (≈parity) |
| 2023 | 0.2902 | 0.2437 | **+0.0465** (lags) | 0.3195 | 0.3140 | +0.0054 (≈parity) |
| 2025 | 0.3812 | 0.2798 | **+0.1014** (lags) | 0.3877 | 0.3446 | **+0.0431** (lags, less than half the original gap) |

The positive-only earnings variant moves the same way (2015/2017/2019 flip to earnings-leads; 2021/2023 shrink from ~+0.05 to ~+0.01; 2025 shrinks from +0.105 to +0.048) — the reversal is not an artifact of loss-makers.

## (3) Does the lag finding survive?

**It does not survive as originally stated.** Under the corrected, per-company nearest-fiscal-instant measure:
- **2015, 2017, 2019: the finding reverses.** Earnings share exceeds weight share in all three (top-10 companies captured a *larger* share of earnings than of value) — the opposite of the single-frame result.
- **2021, 2023: the finding disappears.** The gap collapses to under 0.6 percentage points either direction — indistinguishable from parity given the measurement's own noise.
- **2025: the finding survives but is roughly halved.** Weight still leads earnings, but the gap shrinks from 10.1 points to 4.3 points.

The single-frame run's headline (earnings lags weight in 5 of 6 years, gap widening sharply) was substantially an artifact of Apple and Microsoft's complete, mechanical absence from the float side of that measurement, not a fiscally-aligned reading of the data. The only part of the original finding that holds up at all under the corrected measure is a modest, real gap in 2025.

## (4) Coverage, restated

Float coverage (companies with a usable float value ÷ mapped members) jumped substantially under the corrected method, exactly as expected since it now looks across a full year of instants per company instead of one calendar quarter for everyone:

| Year | Float coverage, orig | Float coverage, corrected | Earnings coverage (unchanged either way) |
|---|---|---|---|
| 2015 | 287/379 = 75.7% | 351/379 = **92.6%** | 318/379 = 83.9% |
| 2017 | 314/405 = 77.5% | 387/405 = **95.6%** | 362/405 = 89.4% |
| 2019 | 320/424 = 75.5% | 399/424 = **94.1%** | 377/424 = 88.9% |
| 2021 | 354/448 = 79.0% | 438/448 = **97.8%** | 417/448 = 93.1% |
| 2023 | 373/473 = 78.9% | 460/473 = **97.2%** | 447/473 = 94.5% |
| 2025 | 385/485 = 79.4% | 476/485 = **98.1%** | 451/485 = 93.0% |

A residual 2–8 companies per year (varies) still have no float match across all 5 frames — the specified window (prevQ3, prevQ4, thisQ1, thisQ2, thisQ3, spanning ~Sep 30 Y−1 to ~Sep 30 Y) does not cover a fiscal Q2-end falling in Oct–Dec of year Y itself (that would need `thisQ4I`, which was not in the specified frame set); `max_lag_days` of 215–303 in every year confirms a handful of companies are still only weakly matched at the edge of the window. I implemented exactly the 5-frame window as specified rather than expanding it, and flag this as a residual, quantified gap rather than a silent correction.

## Method notes

- The same $5T sanity bound caught the same 6 outlier records (Garmin 2015/2017, Host Hotels 2019, Zimmer Biomet 2021, Domino's Pizza and M&T Bank 2023) under the new method too — logged to the new `float_outliers_excluded_corrected.csv`, unchanged treatment (excluded like a missing value).
- Median lag between the chosen instant and 30 June of year Y was 0.0 days in five of six years (2019 was 2.0 days) — the great majority of the ~350–480 mapped companies each year are calendar-year filers whose fiscal Q2 lands exactly or almost exactly on 30 June, so the correction's effect is concentrated on a minority of large, non-calendar-fiscal-year companies (which happens to include Apple and Microsoft).
- All 23 new SEC requests for this correction, plus the earlier run's requests, completed with zero 403/429 responses. The declared-contact UA went to sec.gov hosts only throughout, including in this corrected-method script (verified: it imports and reuses `top10.py`'s `http_get`/UA-selection code unchanged, and this script never touches a non-sec.gov host).
- Per the note in your message, I did not need to further adjust anything about the SEC-etiquette compliance fix — my `top10.py` copy already only sends the declared-contact UA to sec.gov hosts.

## Files (scratch directory, project folder still untouched)

- `.../top10_by_year.csv`, `.../float_outliers_excluded.csv` — original single-frame method (unchanged from before)
- `.../top10_corrected.py` — new companion script implementing the nearest-instant method (imports the fixed `top10.py`, does not modify it)
- `.../top10_by_year_corrected.csv` — corrected method's year table (all columns above plus `median_lag_days`, `max_lag_days`, and per-frame source counts `n_from_prevQ3`/`prevQ4`/`thisQ1`/`thisQ2`/`thisQ3`)
- `.../float_outliers_excluded_corrected.csv` — corrected method's outlier log
- `.../unmapped.csv` — unchanged (membership/mapping didn't change)
- `.../cache/` — now also holds the 23 newly-fetched instant frames (`float_CY{2014..2024}{Q3I,Q4I}.json`, `float_CY{2015,2017,2019,2021,2025}Q1I.json`, `float_CY{2015,2017,2019,2021,2023,2025}Q3I.json`), all directly under `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/wave1/p2b/cache/`
