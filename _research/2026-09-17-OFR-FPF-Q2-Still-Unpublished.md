# OFR Hedge Fund Monitor — 2026Q2 still unpublished (17 Sep 2026)

**Status:** SLIPPED — re-date, do not close. Calendar row was due 18 Sep (already slipped from 10 Sep).
**machineId:** `56a83289-aaaa-453d-a7c7-aa768bd566bb`
**Checked:** 17 Sep 2026 via OFR Hedge Fund Monitor API `https://data.financialresearch.gov/hf/v1/series/full`

## Finding

2026Q2 Form PF aggregates are **not published**. Binding series for the calendar row still end at **2026-03-31 (Q1)**:

| mnemonic | last obs date | last value | unit |
|---|---|---:|---|
| `FPF-BORROW_REPO_SUM` | 2026-03-31 | 3,243 | $bn (API stores dollars; /1e9) |
| `FPF-ASSETCLASS_REPO_REVERSEREPO_SUM` | 2026-03-31 | 1,399 | $bn |

Q1 vintage previously noted `schedule.last_update` ≈ 2026-06-04. At the ~65-day lag after quarter-end, Q2 was due ~3 Sep; as of **17 Sep** it is **~14 days late**. Positive signal unchanged: last observation date later than 2026-03-31 (or API last_update later than 2026-06-04).

## What this is not

- Not a close — the series is live; the vintage is late.
- Not a pull — `bin/pull_series.py --only ofr_hf` would only re-write the Q1 points already in `data/series.tsv`.
- No new numbers entered into `data/series.tsv` from this check.

## Calendar action (parent)

Re-date the 2026-09-18 OFR FPF row to **2026-09-24** (weekly re-check). Do not roll silently again without a dated row. Keep OPEN. Same positive-signal language.

## Gates that still wait on Q2

- D10 / D3 §8 collateral-leg growth after Q1
- N2b v2 / C-070 amendment: `FPF-ASSETCLASS_REPO_REVERSEREPO_SUM` cash-lending leg

## Re-check 19 Sep 2026 (early)

Still **unpublished**. API check 19 Sep ~18:50 CEST:

| mnemonic | last_update | last obs | value |
|---|---|---|---:|
| `FPF-BORROW_REPO_SUM` | 2026-06-04 12:52:35 | 2026-03-31 | $3,243bn |
| `FPF-ASSETCLASS_REPO_REVERSEREPO_SUM` | 2026-06-04 12:52:35 | 2026-03-31 | $1,399bn |

No series.tsv append (would only reprint Q1). Calendar row **2026-09-24** stays OPEN — do not mark DONE on Q1 reprint. Positive signal unchanged: last obs > 2026-03-31.

## Route fix 22 Sep 2026 (folded into W2 day — not a separate parcel)

**Working route (observed):**
```
curl -sS 'https://data.financialresearch.gov/hf/v1/series/full?mnemonic=FPF-BORROW_REPO_SUM'
```
Returns JSON key `FPF-BORROW_REPO_SUM`, `timeseries.aggregation` list of `[date, value]`.
Same pattern for `FPF-ASSETCLASS_REPO_REVERSEREPO_SUM`.

**Broken routes (do not use):**
- `https://data.financialresearch.gov/v1/series/timeseries?mnemonic=FPF-BORROW_REPO_SUM` → `Invalid mnemonic` (missing `/hf/` namespace).
- `https://www.financialresearch.gov/hedge-fund-monitor/data/` → HTTP 404.

**Publication status 22 Sep:** still **Q1 only**. Last aggregation obs **2026-03-31** = $3,243bn (`FPF-BORROW_REPO_SUM`); reverse-repo asset class last **2026-03-31** = $1,399bn. `schedule.last_update` still **2026-06-04**. This is non-publication, not a wrong-route artefact — the working `/hf/` route confirms Q2 is absent.

Positive signal: last aggregation date ≥ `2026-06-30`.
