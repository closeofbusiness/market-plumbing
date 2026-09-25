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


## RUN 1 — public web sources (E-015)

**Run clock:** 2026-09-25 morning Europe/Berlin. **Tool:** Cursor `WebSearch` (no date/recency filter in the tool; window applied by reading dates), plus `WebFetch` on candidate URLs for dates and visible text. **Never logged in; never bypassed a paywall or sign-in wall.** Paywalled items: headline + visible opening only.

**Window:** keep items published **2026-09-10 through 2026-09-25**. Drop undated. Official Fed / NY Fed / OFR / Treasury / FRED releases are prints, listed separately, **out of the sentiment counts**.

### Method note

Each of the seven parcel strings was searched verbatim (nothing else). The search tool returns a short first page (~5 links) per call; those links were read. Where a second pass was needed (failed query, or primer-only ABCP page), the same verbatim string was searched again and those links were read too. Read-count below = every result inspected, including official, out-of-window, and off-topic. “Kept” = in-window, non-official, direct URL + date, usable without login.

### Per-query balance

| query | items read | stress | quiet | mixed | off-topic | kept (URL+date, in window, non-official) | dropped (no URL / undated / out of window / paywall-blocked body) | official (listed separately) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `quarter-end repo` | 10 | 0 | 0 | 1 | 0 | 1 | 4 | 5 |
| `quarter end funding` | 10 | 0 | 0 | 0 | 3 | 0 | 3 | 4 |
| `SOFR quarter-end` | 8 | 0 | 0 | 0 | 0 | 0 | 3 | 5 |
| `month-end repo` | 7 | 0 | 0 | 0 | 0 | 0 | 2 | 5 |
| `TRS funding` | 10 | 0 | 0 | 0 | 10 | 0 | 0 | 0 |
| `stock loan quarter end` | 7 | 0 | 0 | 0 | 2 | 0 | 4 | 1 |
| `ABCP` | 10 | 0 | 0 | 0 | 2 | 0 | 8 | 0 |
| **Total (sum of rows; some URLs recur across queries)** | **62** | **0** | **0** | **1** | **17** | **1** | **24** | **20** |

Stress/quiet/mixed columns count only **kept** items. Off-topic includes Teacher Retirement System of Texas hits under `TRS funding`, startup “funding” trackers under `quarter end funding`, and ABCP primers with no dated Sep-2026 market read.

### Kept items (in window, non-official)

| date | role | URL | one-line paraphrase | tag |
|---|---|---|---|---|
| 2026-09-22 | commentator | https://martyau79.substack.com/p/22sept2026-traditional-markets-and | Au79 Macro (Marty Gold): paid note; visible TL;DR cites a sharp trailing-72h drop in Fed/global net liquidity from a ~$154.5bn TGA rise — macro-liquidity, not desk repo colour. | mixed |

No other in-window non-official page with both a direct URL and a usable date survived the seven verbatim searches. Equilend H1 2026 securities-lending review (2026-07-21), Alpha in Academia “Quarter-End Is a Tail Event” (2026-08-21), Lead Lag Report repo note (2026-08-01), and the NY Fed Teller Window repo-framework post (2026-09-01) were read and **dropped as out of window** (Sep 1 is before Sep 10). A Reuters headline on quarter-end money-market stress appeared in search synthesis with a **2025-09-12** path and 404’d on fetch — not kept.

### Official / print sources read (out of sentiment counts)

- Board of Governors FEDS Note, “What Happens on Quarter-Ends in the Repo Market,” 2025-06-06: https://www.federalreserve.gov/econres/notes/feds-notes/what-happens-on-quarter-ends-in-the-repo-market-20250606.html (and accessible-data twin).
- NY Fed Teller Window, “A Framework for Understanding the U.S. Treasury Repo Market,” 2026-09-01: https://tellerwindow.newyorkfed.org/2026/09/01/a-framework-for-understanding-the-u-s-treasury-repo-market/
- NY Fed Teller Window / Liberty Street pieces on year-end and month-end money markets (2024–2025 dates).
- NY Fed SOFR / reference-rate pages; FRED series pages surfaced under stock-loan and SOFR queries.
- Perli NY Fed speech on quarter-end repo pressures (2024-11-12).

These describe the known reporting-date mechanism (dealer balance-sheet pullback, sponsored-repo shift, SOFR upper-tail). They are **not** September 2026 desk sentiment.

### Distinct sources (denominator)

| source | role |
|---|---|
| Au79 Macro / Marty Gold (Substack) | commentator |
| Federal Reserve Board (FEDS Notes) | official (print) |
| Federal Reserve Bank of New York (Teller Window, speeches, reference rates) | official (print) |
| OFR / FRED / DTCC-linked pages as surfaced | official (print) |
| Equilend Data & Insights | desk-adjacent data vendor (out of window) |
| Alpha in Academia | strategist/quant blog (out of window) |
| Lead Lag Report (Michael Gayed) | commentator (out of window) |
| Investopedia / Bank of Canada / law-firm ABCP primers | primer / unknown (not dated Sep-2026 colour) |
| Teacher Retirement System of Texas (and mirrors) | off-topic under `TRS funding` |

**Distinct non-official in-window sentiment sources: 1** (commentator). Three loud or familiar names outside the window are not “the market.”

### Observed vs inferred

**Observed:** seven verbatim Cursor `WebSearch` passes (plus targeted re-searches on the same strings); 62 result rows read; **1** kept in-window non-official item; that item is macro-liquidity / TGA, not sponsored-repo, stock-loan, or ABCP colour; `TRS funding` returned pension-contribution noise only; ABCP returned primers only; no `x.com/.../status/...` links with readable text without login.

**Inferred:** with a one-item in-window non-official sample and no dated stress colour on questions 1–3, the June 2026 “quiet” base rate is not overturned by public-web sentiment before the turn. Confidence is low because the searchable public web, under these neutral strings, barely populated the window.

### Pre-registered calls vs June 2026 (public web, E-015)

1. Quarter-end repo (squeeze / specials / sponsored-vs-bilateral): **SIMILAR** — no in-window non-official stress colour; official notes restate the usual turn mechanism without a Sep-2026 desk panic read.
2. Equity financing (stock loan / TRS / margin): **SIMILAR** — `TRS funding` was off-topic; `stock loan quarter end` had no in-window keep; no step-up chatter in window.
3. ABCP / conduits vs equity-TRS or HQLA-repo legs: **SIMILAR** — primer-only results; zero dated Sep-2026 conduit pullback items kept.
4. Versus June 2026 overall: **SIMILAR** — one mixed macro-liquidity note does not reclassify the turn vs June’s quiet base rate.

RUN 2 (1 Oct) and the 30 Sep / 1 Oct prints score these calls right / wrong / unscorable.


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

## UNCERTAIN (method)

A desk blog at `conks.plumbing` has dated Sep-2026 money-market posts (e.g. 13 Sep structural cleared-repo piece; 24 Sep snapshot with orderly SOFR/GC). Those URLs did **not** appear in the seven verbatim Cursor `WebSearch` result pages, so they are **not** in the kept counts or the four calls. Widening the query list or browsing off-result domains would break RUN 1 / RUN 2 comparability (parcel: same searches, same tool, same rules).

## Do-not list (checked)

- Chatter not presented as a print.
- Missing OFR Q2 not treated as a finding.
- No scalar multiplier; no claim about what drove prices (C-077).
- Queries not widened mid-run.
