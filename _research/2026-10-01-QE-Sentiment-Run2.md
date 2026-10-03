# QE Sentiment RUN 2 — after the 30 Sep 2026 turn

**Parcel:** `Parcel_QE_Sentiment_25Sep_DRAFT_For_Grok.md`. **Calendar:** row 2026-10-03 (re-dated 28 Sep from 1 Oct; principal token-reset). **Agent:** grok. **Lane:** public web only (E-015 / C-121), same as registered RUN 1.

**Run clock:** 2026-10-03 morning Europe/Berlin. **Started from HEAD:** `79f81a8` (`Housekeeping 30 Sep: OFR hedge-fund Q2 landed; quarter-end rows dated to their prints`). **Tool:** Cursor `WebSearch` (verbatim seven strings only; no date/recency filter in the tool; window applied by reading dates), plus `WebFetch` on candidate URLs for dates and visible text. **Never logged in; never bypassed a paywall or sign-in wall.** Paywalled items: headline + visible opening only.

**Window:** keep items published **2026-09-26 through 2026-10-03** inclusive. Drop undated. Official Fed / NY Fed / OFR / Treasury / FRED / DTCC releases are prints, listed separately, **out of the sentiment counts**.

**Filename note:** path kept as `_research/2026-10-01-QE-Sentiment-Run2.md` per parcel/calendar even though the run executed on 3 Oct.

## Method note

Each of the seven parcel strings was searched verbatim (nothing else), twice per string (first page + second pass, matching RUN 1). The search tool returns a short first page (~5 links) per call; those links were read. Candidate URLs were opened with `WebFetch` for dates and visible text. Read-count below = every result inspected, including official, out-of-window, off-topic, and second-pass rows. “Kept” = in-window, non-official, on-topic for the four questions, direct URL + date, usable without login. Off-topic in-window pages are counted in the off-topic column, not as kept.

## Per-query balance

| query | items read | stress | quiet | mixed | off-topic | kept (URL+date, in window, non-official, on-topic) | dropped (no URL / undated / out of window / paywall-blocked body) | official (listed separately) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| `quarter-end repo` | 10 | 0 | 0 | 0 | 0 | 0 | 3 | 7 |
| `quarter end funding` | 10 | 0 | 0 | 0 | 2 | 0 | 3 | 5 |
| `SOFR quarter-end` | 10 | 0 | 0 | 0 | 0 | 0 | 3 | 7 |
| `month-end repo` | 10 | 0 | 0 | 0 | 0 | 0 | 4 | 6 |
| `TRS funding` | 10 | 0 | 0 | 0 | 10 | 0 | 0 | 0 |
| `stock loan quarter end` | 10 | 0 | 1 | 0 | 1 | 1 | 6 | 2 |
| `ABCP` | 10 | 0 | 0 | 0 | 0 | 0 | 10 | 0 |
| **Total (sum of rows; some URLs recur across queries)** | **70** | **0** | **1** | **0** | **13** | **1** | **29** | **27** |

Stress/quiet/mixed columns count only **kept** items. Off-topic includes Teacher Retirement System of Texas hits under `TRS funding`, Indian/US startup-funding trackers under `quarter end funding`, and the CurvedTrading page for ticker **LOAN** (Manhattan Bridge Capital) under `stock loan quarter end`.

## Kept items (in window, non-official, on-topic)

| date | role | URL | one-line paraphrase | tag |
|---|---|---|---|---|
| 2026-10-03 | desk-adjacent data | https://chartexchange.com/symbol/nasdaq-qqq/borrow-fee/ | ChartExchange QQQ borrow-fee board: as of early 3 Oct ET, ~9.8m shares available at 0.25% annualised fee (IBKR feed) — GC-like availability, no hard-to-borrow stress signal. | quiet |

No other in-window non-official on-topic page with both a direct URL and a usable date survived the seven verbatim searches. Equilend Q3 2025 securities-lending release (2025-10-03), Alpha in Academia “Quarter-End Is a Tail Event” (2026-08-21), Curved cost-to-borrow primer (2026-08-13), Fed FEDS note on repo and the balance sheet (2026-08-26), and the Reuters/MWC June-2026 “quiet facilities” piece (2026-06-30) were read and **dropped as out of window**. Datapile’s Q3 2026 USA startup-funding page had **no usable publication date** — dropped undated. Inc42’s India startup-funding note (2026-09-30) is in window but **off-topic** under `quarter end funding` (VC rounds, not money-market turn colour).

## Official / print sources read (out of sentiment counts)

- Board of Governors FEDS Note, “What Happens on Quarter-Ends in the Repo Market,” 2025-06-06: https://www.federalreserve.gov/econres/notes/feds-notes/what-happens-on-quarter-ends-in-the-repo-market-20250606.html (and accessible-data twin).
- Board of Governors FEDS Note, “Repo Markets and the Fed’s Balance Sheet…,” 2026-08-26: https://federalreserve.gov/econres/notes/feds-notes/repo-markets-and-the-feds-balance-sheet-implications-for-monetary-policy-implementation-20260826.html (out of sentiment window; print/background).
- NY Fed Teller Window / Liberty Street / Perli speech pages on year-end and quarter-end money markets (2024–2025 dates).
- NY Fed SOFR / TGCR / BGCR Markets API (secured rates) and ON RRP `rp/results` API — used for turn prints below.
- DTCC Sponsored Membership Volume CSV (`cms-prod.dtcc.com/data/SponsoredVolume.csv`) — latest row on fetch was **2026-09-24**; no 25–30 Sep rows yet.
- Fed Board CP weekly outstandings via `data/series.tsv` (`abcp_outstanding_bn` as_of 2026-09-30).

These describe the known reporting-date mechanism or supply open-market levels. They are **not** September-turn desk sentiment.

## Distinct sources (denominator)

| source | role |
|---|---|
| ChartExchange (QQQ borrow board) | desk-adjacent data vendor |
| Inc42 | journalist / startup tracker (off-topic under funding query) |
| CurvedTrading (ticker LOAN page) | commentator / data site (off-topic ticker collision) |
| Teacher Retirement System of Texas (and mirrors) | off-topic under `TRS funding` |
| Federal Reserve Board (FEDS Notes) | official (print) |
| Federal Reserve Bank of New York (Teller Window, speeches, Markets API) | official (print) |
| DTCC Sponsored Volume CSV | official (print) |
| Equilend Data & Insights | desk-adjacent data vendor (out of window) |
| Alpha in Academia | strategist/quant blog (out of window) |
| Reuters / MWC mirror (June 2026 quiet facilities) | journalist (out of window) |
| Investopedia / Bank of Canada / law-firm ABCP primers | primer / unknown (not dated Sep–Oct 2026 colour) |

**Distinct non-official in-window on-topic sentiment sources: 1** (desk-adjacent data). Three loud or familiar names outside the window are not “the market.”

## Observed vs inferred

**Observed:** fourteen verbatim Cursor `WebSearch` passes (seven strings × two); 70 result rows read; **1** kept in-window non-official on-topic item (QQQ borrow board, quiet); `TRS funding` again returned only pension noise; ABCP returned primers only; no `x.com/.../status/...` links with readable text without login; SOFR/TGCR/BGCR/ON RRP and ABCP prints available for the turn; DTCC sponsored CSV still ended at 24 Sep on 3 Oct morning.

**Inferred:** with a one-item in-window on-topic sample and no dated stress colour on questions 1–3, public-web sentiment after the turn does not overturn the June 2026 “quiet” base rate. Confidence remains low for the same design reason as RUN 1: neutral-string web search barely populates the window. The **prints** carry the real test (below).

## Prints used for scoring (30 Sep / 1 Oct cluster)

### From `data/series.tsv` (parent pull vintage `2026-10-03T07:17Z` where present)

| series_key | as_of | value | unit | note |
|---|---|---:|---|---|
| `abcp_outstanding_bn` | 2026-09-30 | 504.4 | $bn | Wed week; SA Fed Board CP |
| `abcp_outstanding_bn` | 2026-09-23 | 501.7 | $bn | pre-turn baseline (27 Sep pull) |
| `ficc_sponsored_total_bn` | 2026-09-24 | 2420.6 | $bn | **latest DTCC row; not 30 Sep** |
| `ficc_sponsored_total_bn` | 2026-09-23 | 2430.6 | $bn | calendar pre-turn baseline |
| `fed_on_rrp_bn` | 2026-10-02 | 1.5 | $bn | series latest; turn days from API below |
| `sofr_pct` | 2026-10-01 | 3.87 | % | series latest; **30 Sep from API below** |
| `finra_margin_debit_balances_bn` | 2026-08 | 1453.8 | $bn | Sep FINRA not yet in vault |
| `actrix_sponsored_share_of_cleared_pct` | 2026-07 | 31.1 | % | Sep Actrix not yet in vault |

No June-2026 rows in `series.tsv` for `ficc_sponsored_total_bn`, `abcp_outstanding_bn`, or daily SOFR. Calendar states FICC sponsored total **2,862bn on 30 Jun 2026** (context only; not a series.tsv vintage — not used as a scored June baseline from the vault).

### Open-market API fetches on run day (not substituted into series.tsv; for scoring only)

NY Fed Markets API `rates/secured/sofr|tgcr|bgcr` and `rp/results` (Reverse Repo, overnight fixed-rate, Treasury accepted):

| print | 2026-06-29 | 2026-06-30 (Jun turn) | 2026-09-29 | 2026-09-30 (Sep turn) | 2026-10-01 |
|---|---:|---:|---:|---:|---:|
| SOFR % | 3.62 | **3.68** | 3.88 | **3.90** | 3.87 |
| SOFR p99 % | 3.71 | **3.80** | 3.97 | **3.99** | 3.97 |
| SOFR volume $bn | 3126 | 3418 | 2967 | 3230 | 3067 |
| TGCR % | 3.60 | **3.64** | 3.87 | **3.88** | 3.84 |
| BGCR % | 3.60 | **3.64** | 3.87 | **3.88** | 3.84 |
| ON RRP $bn | 3.5 | **26.9** | 11.4 | **11.5** | 0.4 |

Pre-turn baseline (calendar / 27 Sep pull): SOFR 3.88% / p99 3.96% (24 Sep); ON RRP 0.6bn (25 Sep); ABCP 501.7bn (23 Sep).

**Turn vs prior day:** Sep SOFR +2 bp (3.88→3.90), p99 +2 bp; Jun SOFR +6 bp (3.62→3.68), p99 +9 bp. Sep ON RRP ~11.5bn vs Jun ~26.9bn. Sep ABCP +2.7bn week-on-week through the Wednesday that is quarter-end.

**Missing for scoring (do not invent):** CME AXW total-return futures basis (no free vault series); `actrix_sponsored_share_of_cleared_pct` for Sep; `finra_margin_debit_balances_bn` for Sep; `ficc_sponsored_total_bn` for **30 Sep** (DTCC CSV top row still 24 Sep as of run morning).

## RUN 2 pre-registered calls vs June 2026

1. Quarter-end repo (squeeze / specials / sponsored-vs-bilateral): **SIMILAR** — SOFR/GC turn was mild and smaller than June’s day-over-day spike; ON RRP rose into the turn but to roughly half June’s take-up; no in-window stress chatter; FICC 30 Sep print still missing so sponsored-vs-bilateral shift at the turn date is not observed.
2. Equity financing (stock loan / TRS / margin): **SIMILAR** — one quiet QQQ borrow snapshot; `TRS funding` off-topic again; AXW basis and FINRA Sep absent.
3. ABCP / conduits vs equity-TRS or HQLA-repo legs: **SIMILAR** — `abcp_outstanding_bn` rose 501.7→504.4 through Wed 30 Sep (no outstanding pullback); primer-only web colour.
4. Versus June 2026 overall: **SIMILAR** — available rate and ABCP prints do not show a tighter turn than June; if anything the SOFR/ON RRP turn was milder, but missing FICC/AXW/Actrix/FINRA legs block an EASIER upgrade.

## Scoring table — RUN 1 registered calls (public-web E-015)

RUN 1 registered (all **SIMILAR**):

| # | RUN 1 call | RUN 2 call | prints named in parcel | score | why |
|---|---|---|---|---|---|
| 1 | SIMILAR | SIMILAR | SOFR/GC at turn; `ficc_sponsored_total_bn`; `actrix_sponsored_share_of_cleared_pct` | **right** (on SOFR/GC + RRP); FICC 30 Sep and Actrix Sep legs **unscoreable** | Day-over-day SOFR/TGCR and ON RRP show a quiet-to-mild turn, not tighter than June. Sponsored-total for 30 Sep not in DTCC CSV yet; Actrix still July. |
| 2 | SIMILAR | SIMILAR | CME AXW basis; `finra_margin_debit_balances_bn` | **unscoreable** | No AXW basis in vault; FINRA still Aug 1453.8. Sentiment sample too thin to score alone. |
| 3 | SIMILAR | SIMILAR | `abcp_outstanding_bn` | **right** | ABCP outstanding rose through the 30 Sep Wednesday print — no conduit-outstanding pullback vs pre-turn. |
| 4 | SIMILAR | SIMILAR | all of the above vs 30 Jun | **right** on available legs; overall still **partial** | Available SOFR/GC/RRP/ABCP legs are consistent with SIMILAR (lean milder than June on the rate/RRP turn). Full vs-June score blocked where June vault rows or Sep FICC/AXW/Actrix/FINRA are missing. |

## UNCERTAIN (method / data)

- Same design limit as RUN 1 / supervisor check: neutral-string web search returned almost no in-window practitioner colour. Absence of stress chatter is not strong evidence of a quiet market.
- Practitioner sites that did not appear in the seven result pages (e.g. money-market newsletters) are **not** in the counts — widening queries would break RUN 1 / RUN 2 comparability.
- DTCC Sponsored Volume CSV had not advanced past **2026-09-24** by run morning 3 Oct; calendar expected 30 Sep to post next business day. Treat FICC turn-day sponsored total as **missing**, not zero.
- Parent `bin/pull_series.py --only dtcc,fed_cp,nyfed_rates,nyfed_rrp` had appended ABCP 30 Sep and rates through early Oct by `2026-10-03T07:17Z`; series still lacked SOFR as_of 2026-09-30 (API used for that day). No further series appends observed while waiting.
- CME AXW basis remains unscored; no free series key in the vault.

## Do-not list (checked)

- Chatter not presented as a print.
- Missing OFR Q2 not treated as a finding (Q2 now published 30 Sep — used only as background; not a Sep-turn sentiment item).
- No scalar multiplier; no claim about what drove prices (C-077).
- Queries not widened mid-run; no login; no paywall bypass.
- No git commit / push; no handover write (parent owns those).

## Gates note

Gates already green at start (parent): fresh clone HEAD `79f81a8`; Singh-Ask path empty; `bin/check.sh --handover` integrity ✓ (claude stamp 2026-09-30T08:39:43). This return does **not** re-block those gates.

## Supervisor check (3 Oct 2026)

**Verified against the repository's own series histories (`data/history/`):** every turn print in the table above matches. SOFR
3.62 → 3.68 at the June turn and 3.88 → 3.90 at September's; the 99th percentile 3.71 → 3.80 and 3.97 → 3.99; ON RRP 26.9bn on
30 Jun and 11.5bn on 30 Sep. ABCP 504.4bn on 30 Sep against 501.7bn a week earlier. The method matches RUN 1: the seven
verbatim strings, the same lane, a dated window, and no widening mid-run.

**Filled after the run:** DTCC posted 30 Sep later on 3 Oct. FICC sponsored activity rose 2,476.7 → 2,729.9bn on the turn day
(+253bn, +10.2%), against 2,625.9 → 2,862.1bn at the June turn (+236bn, +9.0%). The sponsored leg of call 1 is therefore SIMILAR,
and call 1 scores **right** on SOFR/GC, ON RRP and sponsored volume. Only the Actrix share stays unscoreable.

**Scores as adjudicated:**
- Call 1: right; the Actrix leg unscoreable.
- Call 2: unscoreable, because no free AXW basis exists and FINRA's September edition is not out.
- Call 3: right.
- Call 4: right on every leg available.

**Weight:** the scores come from the prints, not from the sentiment search, which kept one item of 70. RUN 1 kept one of 62. Two
runs of generic web search have not seen practitioner chatter in either direction, so they cannot tell "quiet" from "invisible".
That bears on the December design (calendar, 4 Oct).
