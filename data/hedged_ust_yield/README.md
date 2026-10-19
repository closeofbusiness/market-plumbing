# FX-hedged 10-year Treasury: the rolling 3-month carry

This folder measures the rolling 3-month carry of a currency-hedged 10-year US Treasury for euro-based and yen-based investors, month by month, and sets it against the 10-year government yield at home. This measures an incentive. It does not show what led any investor to buy, sell or hedge.

## The latest result

**Euro-based investor**, headline variant H3 (the locked 3-month forward built from overnight-index swap rates and the 3-month cross-currency basis). Every figure is in percent or percentage points; a month marked `partial` is incomplete. `pickup` is the hedged carry minus the euro 10-year yield (ECB AAA curve); it is a comparison of two yields, not a gain anyone received. Months with no row had fewer than 10 swap prints in one of the three cells the headline needs (see `n_basis` and the ledger). The October 2024 cells use prints from 14 October only, the first day in the archive. No FX forward quote is used: the forward rate is built from the overnight-index swap rates and the basis, so the spot rate cancels.

| month | 10y Treasury | euro 10y | rate-gap term | basis term | hedged carry | pickup |
|---|---:|---:|---:|---:|---:|---:|
| 2024-10 | 4.095 | 2.354 | -1.602 | -0.029 | 2.465 | 0.111 |
| 2024-11 | 4.356 | 2.412 | -1.643 | -0.043 | 2.670 | 0.258 |
| 2024-12 | 4.391 | 2.292 | -1.622 | -0.037 | 2.733 | 0.441 |
| 2025-01 | 4.629 | 2.591 | -1.696 | -0.019 | 2.915 | 0.324 |
| 2025-03 | 4.280 | 2.822 | -2.025 | 0.005 | 2.261 | -0.562 |
| 2025-04 | 4.279 | 2.605 | -2.189 | -0.015 | 2.075 | -0.530 |
| 2025-06 | 4.383 | 2.607 | -2.455 | -0.014 | 1.914 | -0.692 |
| 2025-07 | 4.392 | 2.706 | -2.483 | 0.005 | 1.914 | -0.791 |
| 2025-09 | 4.120 | 2.756 | -2.151 | 0.011 | 1.980 | -0.776 |
| 2025-10 | 4.062 | 2.687 | -2.012 | -0.034 | 2.016 | -0.671 |
| 2025-11 | 4.094 | 2.736 | -1.982 | -0.033 | 2.079 | -0.657 |
| 2025-12 | 4.143 | 2.899 | -1.813 | -0.020 | 2.310 | -0.589 |
| 2026-01 | 4.213 | 2.890 | -1.776 | 0.028 | 2.465 | -0.425 |
| 2026-02 | 4.126 | 2.810 | -1.769 | 0.024 | 2.381 | -0.430 |
| 2026-03 | 4.246 | 2.964 | -1.743 | -0.028 | 2.475 | -0.489 |
| 2026-04 | 4.319 | 3.060 | -1.656 | -0.006 | 2.657 | -0.403 |
| 2026-05 | 4.484 | 3.090 | -1.571 | 0.001 | 2.914 | -0.176 |
| 2026-06 | 4.470 | 3.005 | -1.485 | -0.005 | 2.981 | -0.025 |
| 2026-07 | 4.600 | 3.131 | -1.511 | 0.003 | 3.091 | -0.039 |
| 2026-08 | 4.684 | 3.214 | -1.431 | 0.003 | 3.256 | 0.042 |
| 2026-09 | 4.989 | 3.493 | -1.496 | 0.003 | 3.496 | 0.003 |

**Yen-based investor**, annual means of complete months (the Bank of Japan's terms keep monthly yen figures out of this folder; see below). Variant H3 and the diagnostics (A_hist: the dated overnight rates, no basis; B: the realised overnight rates) are shown where they exist.

| period | variant | hedged carry | pickup | rate-gap term | basis term | months |
|---|---|---:|---:|---:|---:|---:|
| 2025 | H3 | 0.318447 | -1.269988 | -3.672460 | -0.253371 | 10 |
| 2026_ytd | H3 | 1.470724 | -1.124989 | -2.860640 | -0.169369 | 8 |
| L_2026-09 | H3 | 1.987312 | -1.005974 | -2.848100 | -0.153636 | 1 |
| anchor_2025-03 | H3 | 0.113615 | -1.407575 | -3.876748 | -0.290113 | 1 |
| 2023 | A_hist | -1.182656 | -1.753710 | -5.140189 | 0.000000 | 12 |
| 2024 | A_hist | -0.930429 | -1.837621 | -5.137632 | 0.000000 | 12 |
| 2025 | A_hist | 0.414934 | -1.121666 | -3.878639 | 0.000000 | 12 |
| 2026_ytd | A_hist | 1.545764 | -1.005460 | -2.913308 | 0.000000 | 9 |
| L_2026-09 | A_hist | 2.173287 | -0.819998 | -2.815760 | 0.000000 | 1 |
| anchor_2025-03 | A_hist | 0.325891 | -1.195300 | -3.954585 | 0.000000 | 1 |
| 2023 | B | -1.295711 | -1.866765 | -5.253244 | 0.000000 | 12 |
| 2024 | B | -0.758706 | -1.665898 | -4.965909 | 0.000000 | 12 |
| 2025 | B | 0.543344 | -0.993256 | -3.750229 | 0.000000 | 12 |
| 2026_ytd | B | 1.450513 | -0.993954 | -2.892311 | 0.000000 | 7 |
| anchor_2025-03 | B | 0.332657 | -1.188533 | -3.947819 | 0.000000 | 1 |

Validation: the build was compared with hedged yields published by Ginnie Mae, TD Economics and BlackRock (`references.csv`). The test is whether the median gap between this build and the published figures stays within 25 basis points (0.25 percentage points), separately for the two forms (H and P) and the two hedge lengths (3 months and 1 year). Results: H 1y PASS; H 3m PASS; P 1y PASS; P 3m PASS. The rules, including how whole-percent quotes are scored, are in the table's `note` column.

**Correction.** Corrected on 19 Oct 2026 after independent verification: the ledger's monthly stage dropped overnight-index swap trades booked under the COMPOUND index names (USD-SOFR-COMPOUND and EUR-EuroSTR-COMPOUND), because its first version required the letters OIS in the index name. The euro 3-month headline moved by at most 2.4bp and the 1-year variant by up to 21bp (September 2026). No yen sign and no 3-month sign changed; the euro 1-year pickup in July 2026 moved from +0.0002 to -0.0131 percentage points, a sign change around zero. The validation gate still passes. The gate medians before and after are in `checks.csv`, rows C17.

## Columns

`monthly.csv` (euro rows only):

- `month`: calendar month, YYYY-MM.
- `pair`: `euro`.
- `variant`: H3 and P3 (3-month, headline and plain form), H12 and P12 (1-year), and the diagnostics A_rt, A_hist, A_effr (spot overnight rates) and B (realised overnight rates).
- `role`: HEADLINE, MAIN or DIAGNOSTIC.
- `n_days`: Treasury business days in the month's means.
- `partial`: 1 if the month's last business day is missing for any leg.
- `qe_turn_early`: 1 if the month is March, June, September or December, so that the quarter end falls in the first 30 days of the hedge windows.
- `ust10_pct`: the 10-year Treasury par yield (semiannual), monthly mean.
- `home10_pct`: the euro 10-year yield, derived from ECB statistics (recomputed on a semiannual basis), monthly mean.
- `rate_gap_term_pp`: the contribution to the hedged carry of the gap between the dollar and the euro short rate over the hedge.
- `basis_term_pp`: the contribution to the hedged carry of the cross-currency basis (zero for the diagnostics).
- `hedged_carry_pct`: the 10-year Treasury yield plus the two terms above, an exact sum of those columns.
- `pickup_pp`: the hedged carry minus `home10_pct`, an exact difference of those columns.
- `form_gap_bp`: 100 x (H - P), in bp, on the H and P rows.
- `basis_tenor`: `3m`, `1y` or `none`.
- `hedge_days_mean`: the mean number of days in the hedge windows of the month's business days.
- `n_ois_us, n_ois_home, n_basis`: the number of prints behind the month's SOFR, euro short-term-rate and cross-currency cells.

`yen_summary.csv`: `period`, `variant`, `statistic`, `value`, `credit`. Each value is the mean of the complete months in the period. A `period` of `2023`, `2024` or `2025` is that calendar year; `2026_ytd` is January 2026 to the latest complete month; `anchor_YYYY-MM` is the single first month in which the yen headline exists (the first month with 10 or more swap prints in each of the three cells it needs), here `anchor_2025-03`; and `L_YYYY-MM` is the latest complete month, here `L_2026-09`.

`summary.csv`: the descriptive questions; yen values are blank and only a `notable` flag is given. `references.csv`: the published figures the build is compared with. `checks.csv`, `pins.csv` and `fetch_log.csv`: input checks, pinned values and the request log.

## Why yen appears only as annual figures

The Bank of Japan's copyright page allows copying with credit but excludes commercial copying, and its API notice asks for a prescribed credit. This project therefore commits no monthly series built from the Bank's TONA: the yen rows of `yen_summary.csv` are annual means of complete months plus two anchor months, and the yen monthly path is kept in a local cache. This service uses the API provided by the "Bank of Japan Time-Series Data Search." The Bank of Japan does not guarantee the content of the service.

## Defined terms

- **Swap print and swap tape.** A print is one reported swap trade. The swap tape is the public record of such trades that US rules require (the Depository Trust and Clearing Corporation publishes it); the ledger in `data/swap_tape/` turns the tape into monthly medians, which are the only place the swap rates and the basis enter this folder.
- **Hedging cost.** What a rolled currency hedge costs per year: the gap between the dollar and the home short rate over the hedge tenor, plus any premium that dollar borrowers pay on top of it. The rate-gap term and the basis term are minus that cost.
- **Cross-currency basis.** The spread on the yen or euro overnight-rate leg of a currency swap against flat SOFR, in bp, as on the US-reported swap tape. A negative basis is a premium to borrow dollars and lowers the carry. It is a median of swap prints and is not the price of FX-swap forward points.
- **Pickup.** The hedged carry minus the 10-year government yield at home.
- **OIS.** An overnight-index swap: a fixed rate exchanged for the compounded overnight rate. The 3-month and 1-year fixed rates are used here as the market's price of the overnight rate over the hedge window.
- **Rolling carry.** The yield plus the annualised gain or loss of a hedge that is renewed every 3 months (or every year for H12 and P12), at the month's prices. It is not the return from holding a hedged bond to maturity, which depends on ten years of future short rates.
- **Bond-basis form (H) and plain-subtraction form (P).** H converts the forward rate with day counts and compounding before it is added to the yield (a semiannual rate, like the yields); P subtracts the quoted rate gap and adds the basis as quoted. `form_gap_bp` is their difference.

## One worked row

`monthly.csv`, euro, H3, 2026-09: 10-year Treasury 4.989048 + rate-gap term -1.496049 + basis term 0.002563 = hedged carry 3.495561. Minus the euro 10-year yield 3.493015, the pickup is 0.002546. The rate-gap term uses the 789 SOFR and 312 euro short-term-rate swap prints and the basis the 40 cross-currency prints of the month (ledger, DTCC).

## Provenance and terms

- **U.S. Treasury** (home.treasury.gov): daily par yield curve, 10-year; a US government work.
- **Ministry of Finance Japan** (www.mof.go.jp): the JGB 10-year; Public Data License 1.0, attribution given.
- **European Central Bank** (data-api.ecb.europa.eu): the euro short-term rate and its compounded index, and the AAA yield-curve parameters. The euro 10-year yield in this folder is derived from ECB statistics (recomputed on a semiannual basis) and is not an ECB publication.
- **Federal Reserve Bank of New York** (markets.newyorkfed.org): SOFR, EFFR and the SOFR Index. The SOFR, EFFR and SOFR Index data are subject to the Terms of Use posted at newyorkfed.org. The New York Fed is not responsible for publication of the data by this project, does not sanction or endorse any particular republication, and has no liability for your use. The data here are modified (monthly means of daily values, and the hedged carry computed from them) and the modifications are this project's, not the New York Fed's. This project is not affiliated with the New York Fed, which does not sanction, endorse, or recommend any products or services offered by it. The SOFR data are calculated by the New York Fed using data provided under a license granted to it by DTCC Solutions LLC.
- **Bank of Japan** (www.stat-search.boj.or.jp): TONA. This service uses the API provided by the "Bank of Japan Time-Series Data Search." The Bank of Japan does not guarantee the content of the service.
- **Du, Keerati and Schreger** panel and the **Deutsche Bundesbank** series are used for checks only and stay in the local cache.
- **DTCC.** The swap-tape cells in this folder (the 3-month and 1-year overnight-index-swap and cross-currency medians) come from the ledger in data/swap_tape/, which derives them from DTCC Public Price Dissemination, CFTC cumulative interest-rate reports (https://pddata.dtcc.com), under THE_ASK.md E-024. E-024, in the principal's choice (a): script the DTCC public price dissemination files despite DTCC's website terms; the use is non-commercial; no raw DTCC file or row is committed or redistributed; only derived statistics (medians, quartiles, counts) are published, and they cite DTCC; requests are sequential and paced and carry the neutral project User-Agent; any technical refusal ends the run rather than being routed around. The ledger's monthly stage extends the same ruling to monthly medians at 10 or more prints. The raw files stay outside the repository, and this folder's script never reads them. Nothing here licenses anyone to use DTCC's data commercially.

