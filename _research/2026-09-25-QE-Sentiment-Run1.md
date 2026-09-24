# QE Sentiment RUN 1 — 25 Sep 2026 (expectations, before the turn)

**Parcel:** `Parcel_QE_Sentiment_25Sep_DRAFT_For_Grok.md` (FINAL despite filename).  
**Agent:** grok. **Executor clock when written:** 2026-09-24 evening Europe/Berlin (contact titled 25 Sep).  
**Method constraint:** every kept item needs a direct `https://x.com/.../status/...` URL (C-048 / C-079).

## Neutral queries (verbatim — reuse unchanged for RUN 2 on 1 Oct)

1. `quarter-end repo`
2. `quarter end funding`
3. `SOFR quarter-end`
4. `month-end repo`
5. `TRS funding`
6. `stock loan quarter end`
7. `ABCP`

## X sample — BLOCKED

Attempted Live search at `https://x.com/search?q=quarter-end%20repo&src=typed_query&f=live` (and the other six strings). The box browser hit X’s sign-in wall (“See what’s happening” / Continue with phone|Google|Apple). No post bodies and no status URLs were readable without authentication.

| query | posts read | stress | quiet | mixed | off-topic | kept (with URL) | dropped (no URL) |
|---|---:|---:|---:|---:|---:|---:|---:|
| (all seven) | 0 | 0 | 0 | 0 | 0 | 0 | 0 |

**Distinct accounts:** 0. **Balance of stress vs quiet (X):** not observable — login wall, not an empty market.

Per parcel rule (“URL or drop”; “never route around a block”), the X section stops here. RUN 2 must re-use the same seven strings.

## Vault prints read on the day (`data/series.tsv` latest vintages)

Parcel aliases → actual keys:

| parcel name | series_key in vault | as_of | value |
|---|---|---|---|
| finra_margin_debit_balances_bn | `finra_margin_debit_balances_bn` | 2026-08 | 1453.8 |
| ficc_sponsored_total_bn | `ficc_sponsored_total_bn` | 2026-08-20 | 2295.6 |
| actrix_sponsored_share_of_cleared_pct | `actrix_sponsored_share_of_cleared_pct` | 2026-07 | 31.1 |
| abcp_outstanding_bn | `abcp_outstanding_bn` | 2026-08-19 | 488.4 |
| hf_repo_borrowing_bn | `hf_repo_borrowing_bn` | 2026-03-31 | 3243.0 |

No June-2026 rows exist in `data/series.tsv` for these five keys (FINRA has Jul 1417.2 then Aug 1453.8; FICC/Actrix/ABCP are single late-summer points; HF repo last print is Q1). OFR Q2 HF data still unpublished — not treated as a finding.

## Open-market prints (not X; separate from the designed sample)

FRED daily (retrieved 2026-09-24 from fred.stlouisfed.org CSV):

- SOFR: 2026-09-16 3.62 → 2026-09-17 3.85 → 2026-09-23 3.87 ([FRED SOFR](https://fred.stlouisfed.org/series/SOFR), as of 23 Sep 2026).
- SOFR 99th percentile: 2026-09-16 3.70 → 2026-09-17 3.93 → 2026-09-23 3.95 ([FRED SOFR99](https://fred.stlouisfed.org/series/SOFR99), as of 23 Sep 2026).
- ON RRP (RRPONTSYD): 2026-09-23 0.461 ([FRED RRPONTSYD](https://fred.stlouisfed.org/series/RRPONTSYD), as of 23 Sep 2026).

The mid-September SOFR step coincides with the FOMC window; it is **not** scored here as quarter-end stress without desk chatter.

## Observed vs inferred

**Observed:** X login wall; seven query strings recorded; vault vintages above; FRED SOFR/SOFR99/RRP path through 23 Sep.  
**Inferred (low confidence):** with zero usable X items, the designed sentiment balance cannot overturn the parcel’s June-2026 “quiet” base rate.

## Pre-registered calls vs June 2026 (one word each)

These are required by the parcel even when the X sample is empty. They are **provisional**, driven by the June quiet base rate plus the absence of readable stress chatter — **not** by a counted X balance.

1. Quarter-end repo (squeeze / specials / sponsored-vs-bilateral): **SIMILAR**
2. Equity financing (stock loan / TRS / margin): **SIMILAR**
3. ABCP / conduits vs equity-TRS or HQLA-repo legs: **SIMILAR**
4. Versus June 2026 overall: **SIMILAR**

RUN 2 (1 Oct) and the 30 Sep / 1 Oct prints score these calls right / wrong / unscorable.

## Do-not list (checked)

- Chatter not presented as a print.
- Missing OFR Q2 not treated as a finding.
- No scalar multiplier; no claim about what drove prices (C-077).
- Queries not widened mid-run.
