# Spec: revenue-recognition timing in the earnings growth of the W3 firm set, fiscal 2023 to fiscal 2025, from SEC XBRL on data.sec.gov (spec author, 28 Oct 2026; rewritten to apply the supervisor rulings of round 1)

*Page context: `docs/index.html` §09 "The gaps that remain", bullet "The last of earnings quality" ("Revenue-recognition timing is what
remains"), and the §08 ledger rows on earnings (tax cut, C-098; useful lives, E2; stock-based compensation and R&D moot, C-095). Chosen in
[`_research/2026-10-28-Grok-G13-Scoping.md`](2026-10-28-Grok-G13-Scoping.md) (item 1). Attacked in
[`_research/2026-10-28-Grok-G13-Revenue-Timing-Attack.md`](2026-10-28-Grok-G13-Revenue-Timing-Attack.md). Lands as
`_research/2026-10-28-Revenue-Recognition-Timing-Spec.md`. House style follows `_research/2026-10-26-Z1-Corporate-Bond-Holders-Spec.md`.
Script `bin/rev_recognition_timing.py`, outputs `data/rev_recognition_timing/`, vintages `data/vintages/rev_recognition_timing/`, check.sh
guard **M27**. Repository read at `db75c57`. The rulings at the end are the record; this body applies round 1 (R1-1 to R1-26). Where the
body and a ruling differ, the ruling wins.*

*"Observed" means seen by the spec author on 28 Oct 2026 in 57 requests to data.sec.gov (06:21-06:26 UTC, 2.8) or in the repository; this
rewrite made no request. "Relayed" means taken from a ruling, a review, a project file or general knowledge, not re-read at source.
**Blind:** the spec author has computed no T, EA, r or share, no sum, average or ratio of any fiscal 2023-2026 value, and has read no single
firm's fiscal 2023-2026 value. 2.7 lists exactly what was looked at. The first draft's departures D1-D6 are settled by round 1 (R1-1, R1-5,
R1-6, R1-8, R1-9, R1-10); the unit of 500 CIKs (D1) stands in 2.1.*

## 0. Goal, and what the result can and cannot say

- **Measure**, for the non-financial firms among the 500 CIKs, the net contract position N = contract assets − contract liabilities (the ASC
  606 measure of revenue recognised ahead of billing, or behind it), and each year's **excess accrual** AA_t = N_t − r_{t−1} × Rev_t: the part
  of the year's change in N beyond what growth at the previous year's ratio r = N / Rev would give. The **timing contribution** to the
  window's change in net income is T = Σ_i (AA_i,e − AA_i,b); for S1, AA_2025 − AA_2023, which needs FY2022 to FY2025 (R1-1).
- **Register** (4.6) the net share T / ΔNI and the gross-positive share Σ_i max(T_i, 0) / ΔNI on fiscal 2023 to 2025 (S1, S1P), and the same
  two on fiscal 2025 to 2026 for firms whose fiscal 2026 ends between 30 Nov 2026 and 15 Feb 2027 (S2, S2P), which no one can have seen when
  this spec is committed. Thresholds 10% and 25%; the direction of T is reported separately (R1-5).
- **Describe**: T in days of revenue; the ten largest contributors each way with their flags; the five largest firms' shares of gross
  positive T, gross negative T and contract liabilities (R1-11); the sensitivities; the placebo windows; trade receivables in days with the
  same T construction, labelled "collection, not recognition" (R1-2); capitalized contract costs in days (R1-4); remaining performance
  obligations; a cash-flow cross-check; and the primary sample's weight in the 500 CIKs' net income (R1-22).

**It can say** how large the timing piece of these firms' change in reported net income was, for the tagged contract balances. Under (A1)
every dollar of excess accrual reached net income, with no cost and no tax, T is that timing piece: an IDENTITY, not a bound (R1-1). Because
A1 ignores the margin and the tax rate, |T| overstates the effect's size, so |T| / ΔNI is BOUNDED, a ceiling on the size of the effect of
**the tagged balances only** (A3: timing in untagged, extension or dimension-only balances is invisible). Inputs are MEASURED: as first
reported in each year's own 10-K. The reference year's own excess accrual is measured, not assumed (the first draft's A2 is withdrawn).

**It cannot say:**
- **anything about prices or flows of money.** A balance-sheet accrual is not a cause of a price move; no sentence says otherwise;
- **whether any firm managed its earnings or broke a rule.** N moves for ordinary reasons: milestone billing, contract mix, a large contract
  near year-end. Stock-funded acquisitions and currency translation can move N with no change in recognition and are not screened (R1-7);
- **anything about collection terms.** Trade receivables are billed consideration awaiting cash; they are outside N and reported apart (R1-2);
- **anything about cost timing.** Capitalized contract costs can move profit with N unchanged; the measure ignores them (R1-4);
- **anything about financial firms** (excluded by SIC, which is not the same boundary as ASC 606's scope, 2.1), or an index-level correction
  to the page's 71-82% earnings share (the firm set is the 2026 survivor set and the window is two years).

**Required README sentence 2 (the denial sentence, exempt from G13, verbatim):** "A change in contract assets or contract liabilities
relative to revenue is a balance-sheet accrual: it shows when revenue was booked against billing, not why, and nothing here says it moved any
price or any flow of money."

## 1. Hard requirements

- **R1. Free public data, one host.** Host allowlist: `data.sec.gov` only (submissions, companyfacts, frames). Refused before the request:
  every other host, explicitly `www.sec.gov`, `efts.sec.gov` and the Financial Statement and Notes ZIPs. No key.
- **R2. User-Agent (R1-17).** The fetch modes read `SEC_UA` from the environment (the declared contact that CLAUDE.md, by the principal's
  ruling of 12 Sep, gives sec.gov hosts), refuse to run without it (exit 2), and never write its value to any file, log or output; G15 tests that it
  is absent from every written byte. Header `Accept-Encoding: identity`. **Only the supervisor runs the fetch modes.** The builder writes the
  code and the selftest and runs `build` offline on the supervisor's cache. The spec author's 57 probe requests and the supervisor's 8
  coverage requests of 28 Oct used the neutral UA `Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)`;
  SOURCES.md says so.
- **R3. Crawl (R1-18).** GET only; no redirect followed; **no retry of any kind**; timeout 300 s; at least 1.0 s between requests (G15 treats
  0.9 s as a violation). Caps per run: `fetch-submissions` 1,000 requests, `fetch-companyfacts` 600, `fetch-frames` 250. **Resumable:** a body
  already in `raw/` whose sha256 matches its `vintages.csv` row is not re-requested. Statuses are assigned after the fetches.
- **R3a. STOP latch.** A 404 on a frame means "no facts for this tag and period" (observed for
  `AccountsReceivableAfterAllowanceForCreditLossCurrent`): logged as `absent`, no STOP. A 404 on a submissions or companyfacts file marks the
  firm `no_sec_record`. Any 403 or 429, any other non-200 (3xx included), or a 200 body that is empty, HTML or not JSON writes
  `data/vintages/rev_recognition_timing/STOP_rrt`, created exclusively (`open(..., "x")`) with five lines `status`, `utc_time`, `url_path`,
  `retry_after`, `body_head`; with the latch present no request is made and the run exits 2. **Only a person deletes a STOP file.** A
  timeout prints `FAIL network <path>`, exits 3, writes no STOP and retries nothing.
- **R4. Vintages.** Raw JSON bodies go to `data/vintages/rev_recognition_timing/<YYYYMMDD>/raw/` (gitignored; key = UTC date the vintage
  began). Committed per vintage: `frames_extract.csv`, `cf_extract.csv`, `submissions_extract.csv` (rows for the 500 CIKs only), and every
  raw body's sha256, bytes and UTC time in `vintages.csv`. `build --vintage YYYYMMDD` reads one vintage. S1 and S1P are scored on the first
  full vintage and never re-scored; the placebo band is frozen from it (R1-13); a later vintage writes `revisions.csv`.
- **R5. Frozen population.** `data/w3_tax/firm_tax_panel.csv`, sha256 pinned in the population block (4.7) and C01.
- **R6. Wording (G13).** No causal, price, motive or misconduct wording in README.md except the denial sentence. Say "excess accrual",
  "booked ahead of billing", "timing contribution", "ordinary explanations", "operating cash flow"; never "causes", "abnormal", "inflated",
  "pulled forward", "premature", "manipulated", "aggressive", "low-quality" or "material" (R1-5, R1-24).
- **R7. Code ownership.** `bin/rev_recognition_timing.py` is new, standard library only, and reads no project file other than the panel and
  its own two folders. No existing script changes, apart from a new warn-only guard M27 in `bin/check.sh`.
- **R8. Parsing and numbers.** JSON read with `parse_float=Decimal, parse_int=Decimal`; `decimal` precision 28. Missing is never zero, except
  under the absent-everywhere rule (P8). Every threshold comparison uses the unrounded Decimal; half-even rounding at write time only:
  `_usd` whole dollars, `r` 6 decimals, `_pct` and `_days` 3 decimals.
- **R9. Post-registration fixes** go in SOURCES.md "Builder decisions" with the old value beside the new. No registered number changes after
  the supervisor's rulings.
- **R10. One source.** Every number comes from data.sec.gov; no other source enters any output cell.

## 2. Data

### 2.1 Population (observed unless marked)

`data/w3_tax/firm_tax_panel.csv`: 503 rows, 500 distinct `cik10`, all ten digits; landed 24 Sep 2026 (commit `1976ae86`), sha256
`7b65abda3aed6b0acf7cf2614a14ae1d74a7aa8991880716f69aa5b25e11966b`, 343,641 bytes. Shared CIKs: 0001652044 (GOOGL, GOOG), 0001754301
(FOXA, FOX), 0001564708 (NWSA, NWS); `tickers` in `firms.csv` joins them with `|`.

**Financial firms are excluded by SIC 6000-6799 inclusive** (P2), read from `sic` in the submissions file (field observed: Microsoft 7372).
Why (relayed): ASC 606 excludes financial instruments, leases and insurance contracts (606-10-15-2), a bank's receivables are loans, and
REITs (SIC 6798) earn mostly lease income. The SIC range is not ASC 606's scope: it also drops exchanges, brokers and insurance brokers,
whose fees are under ASC 606, and keeps card networks and processors under non-6xxx codes (O-6). **The count excluded is the build's
output.** **Earnings weight (R1-22):** `headline.csv` and the README report the primary sample's Σ NI_2025 over the 500 CIKs' Σ NI_2025,
financials included, each firm's FY2025 net income as first reported (firms without one are counted, not imputed).

**Megacap subset (descriptive, O-4):** E2's six (Alphabet 0001652044, Amazon 0001018724, Meta 0001326801, Microsoft 0000789019, Oracle
0001341439, NVIDIA 0001045810) plus Apple 0000320193, Broadcom 0001730168 and Tesla 0001318605, all in the panel.

### 2.2 Fiscal years: a date rule, not a label (P3)

Firms label fiscal years differently: in the W3 panel's `pretax_end_2025` column, NVIDIA's "2025" ends 2025-01-26 and Walmart's 2025-01-31,
but Home Depot's ends 2026-02-01, Lowe's 2026-01-30, Target's and Salesforce's 2026-01-31 (observed). **D_Y is the `reportDate` of the firm's
original 10-K (form exactly `10-K`) with `reportDate` in [Y-04-01, (Y+1)-03-31]**, from `filings.recent` in the submissions file (fields
observed: `form`, `reportDate`, `filingDate`, `accessionNumber`; Microsoft's block holds 1,004 filings back to 2020-09-02); older pages listed
under `files` are fetched from `data.sec.gov/submissions/` when a needed year is older than the block. None → `year_gap` (flag `gap_10k`);
two or more → `fy_ambiguous`; a 10-K/A or 10-KT never defines D_Y. Years needed: FY2019-FY2025 now (placebo FY2019-FY2022, S1 FY2022-FY2025),
FY2026 for S2. Observed for Microsoft: 10-K report dates 2021-06-30 to 2026-06-30, so D_2023 = 2023-06-30, D_2025 = 2025-06-30; its FY2026
10-K was filed 2026-07-29, so Microsoft is not S2-eligible.

### 2.3 Source and fact selection (P4, P5; R1-8, R1-20)

- **Every firm is served by its companyfacts file** (one request per firm, all 500 CIKs so that R1-22's denominator includes financials).
  **Primary basis `own_10k`:** each fiscal year's N, Rev and NI are the facts whose `accn` is that year's original 10-K accession, so a year's
  ratio never mixes filings (R1-8). AA_t still joins two filings by construction (r_{t−1} from year t−1's 10-K, N_t and Rev_t from year t's).
  **Sensitivity `sens_latest`:** the latest-filed fact (latest `filed`, ties to the largest `accn`), which is what a frame serves (observed: in
  Paychex's companyfacts the 2019-05-31 `ContractWithCustomerLiabilityCurrent` fact carries `frame` CY2019Q2I on the copy filed 2020-07-17
  in the next 10-K, not on the original of 2019-07-24).
- **Matching.** Instants: `end` = D_Y exactly. Durations: `end` = D_Y and 350 ≤ `end − start` ≤ 380 days. Facts within ±7 days of D_Y are
  counted as a diagnostic (flag `near_end`); a firm with no exact match for a needed value but a near one gets `end_mismatch` (R1-20). Units
  USD only. Selection never uses `fy` or `fp`, which belong to the filing (observed: a 2018-05-31 fact carries fy 2019, fp Q1).
- **Why frames serve only coverage and checks (observed).** `NetIncomeLoss/CY2019` held Microsoft's year to 2019-06-30 and Oracle's and
  Nike's to 2020-05-31; `CY2019Q4I` instants were 10-Q dates for June and September year-ends (offsets for the 500 in
  `ContractWithCustomerLiabilityCurrent/CY2019Q4I`: 144 at 0 days, 20 within ±7, the rest −37 to +33). At `CY2025`/`CY2025Q4I`, net income
  and a receivable tag both exist for 365 of the 500 CIKs and their end dates differ for 78 (`CY2023`: 364 and 78). Frames are fetched for
  the coverage table, C02-C04 and C14 only.
- **Dimensional and extension facts** are absent from companyfacts and frames (relayed); that is A3.

### 2.4 Tags, priority and structure (P6-P10; R1-2, R1-3, R1-4, R1-14)

| Component | Tags, in priority order | Rule |
|---|---|---|
| CA, contract assets | total `ContractWithCustomerAssetNet`; parts `ContractWithCustomerAssetNetCurrent` + `...AssetNetNoncurrent` | total if total ≥ Current (+ Noncurrent where tagged) at every needed year, else parts; flag `total_gt_parts`; `sens_parts` uses the parts wherever they exist at every needed year |
| CL, contract liabilities | total `ContractWithCustomerLiability`; parts `ContractWithCustomerLiabilityCurrent` + `...LiabilityNoncurrent`; fallback `DeferredRevenueCurrent` + `DeferredRevenueNoncurrent` | as CA; the fallback only if no `ContractWithCustomerLiability*` tag appears at any needed year |
| Rev, revenue (required) | R2 `RevenueFromContractWithCustomerExcludingAssessedTax`; R3 `RevenueFromContractWithCustomerIncludingAssessedTax`; `Revenues` | R2 if at every needed year, else R3, else `Revenues` (flag `rev_fallback`; `sens_r2only` drops those firms); one tag per window |
| NI (required) | `NetIncomeLoss` (attributable to the parent) | no fallback |
| AR, trade receivables (descriptive, R1-2) | A1 `AccountsReceivableNetCurrent` only | AR days and T_AR in `receivables.csv`; A2 and A3 are not trade receivables, as their definitions say |
| Contract costs (descriptive, R1-4) | `CapitalizedContractCostNet` | in days of revenue beside N |
| Descriptive only | `RevenueRemainingPerformanceObligation`; `UnbilledContractsReceivable`; `IncreaseDecreaseInContractWithCustomerAsset`, `...Liability`, `IncreaseDecreaseInAccountsReceivable` | coverage, `sens_unbilled`, the cash-flow cross-check |
| Flags | `PaymentsToAcquireBusinessesNetOfCashAcquired`; `IncomeLossFromDiscontinuedOperationsNetOfTax` (coverage not probed) | `acq2`, `disc_ops` |

**N = CA − CL.** A firm with no contract-balance tag at any needed year has N = 0 every year and stays in scope (R1-2). A tag present at
some needed years only → `year_gap` (flag `gap_n`), out of the primary sample; `sens_gap0` sets the missing side to 0. Never a total with its
parts; never `DeferredRevenue*` beside a `ContractWithCustomerLiability*` tag.

**Evidence behind the total rule (observed on fiscal 2019, per-firm comparisons within 0.5%, no sums).** At `CY2019Q4I`, of the 500:
liability total, current and noncurrent all tagged 59 (total = current + noncurrent in 45, total = current in 1, neither in 13); total and
current without noncurrent 36 (total = current 14, total > current 13, **total < current 9**); total only 81; current only 51; current and
noncurrent 49. Contract assets: all three 9 (total = parts in 8); total and current 7 (equal 3, total > current 3, total < current 1); total
only 61; current only 28; current and noncurrent 13. The R1-14 rule sends the "total below its own parts" cases to the parts.
**Revenue tags in `CY2019`:** 104 of the 500 tag both `Revenues` and R2 (equal 49, `Revenues` larger 50, smaller 5); `Revenues` includes
interest, lease and insurance income (R1-3), hence last.

**Remaining performance obligations are descriptive only:** contracted revenue not yet recognised, billed or not, a backlog that grows with
bookings; the billed part already sits in contract liabilities. **Unbilled receivables** (32 of the 500 at `CY2023Q4I`) may be receivables or
contract assets; the primary excludes them; `sens_unbilled` adds them to CA for firms with no contract-asset tag (O-5).

### 2.5 Coverage observed (count of the 500 CIKs with a fact in the frame, any end date, financial firms not yet removed)

| Tag | CY2023Q4I | CY2025Q4I | CY2026Q2I (probe only) | All filers (`pts`) 2023 / 2025 / 2026Q2 |
|---|---|---|---|---|
| ContractWithCustomerLiability | 183 | 176 | 157 | 1,366 / 1,199 / 960 |
| ContractWithCustomerLiabilityCurrent | 217 | 218 | 200 | 2,064 / 1,904 / 1,573 |
| ContractWithCustomerLiabilityNoncurrent | 130 | 131 | not fetched | 855 / 791 |
| ContractWithCustomerAssetNet | 83 | 82 | not fetched | 610 / 523 |
| ContractWithCustomerAssetNetCurrent | 67 | 67 | 63 | 571 / 553 / 464 |
| ContractWithCustomerAssetNetNoncurrent | 31 | 31 | not fetched | 180 / 165 |
| DeferredRevenueCurrent | 42 | 42 | not fetched | 620 / 485 |
| AccountsReceivableNetCurrent (A1) | 311 | 317 | 292 | 3,393 / 3,122 / 2,636 |
| AccountsNotesAndLoansReceivableNetCurrent (A2) | 18 | 17 | not fetched | 107 / 95 |
| ReceivablesNetCurrent (A3) | 70 | 74 | not fetched | 462 / 377 |
| RevenueRemainingPerformanceObligation | 132 | 134 | 127 | 798 / 748 / 674 |
| UnbilledContractsReceivable | 32 | not fetched | not fetched | 155 |
| AccountsReceivableNetNoncurrent | 13 | not fetched | not fetched | 86 |
| ContractWithCustomerReceivableAfterAllowanceForCreditLossCurrent | 4 | not fetched | not fetched | 33 |
| AccountsReceivableAfterAllowanceForCreditLossCurrent | 404 | 404 | 404 | no such frame |

Durations, `CY2023` / `CY2025`: `Revenues` 243 / 232; R2 317 / 307; R3 42 / 38; NetIncomeLoss 475 / 467; at `CY2025` only:
IncreaseDecreaseInAccountsReceivable 254, IncreaseDecreaseInContractWithCustomerLiability 100, PaymentsToAcquireBusinessesNetOfCashAcquired 273.
`CapitalizedContractCostNet` was not probed. Every fact was USD, numeric, one per CIK; the supervisor's all-filer counts reproduce exactly.
**Combinations (CIK sets only):** any `ContractWithCustomerLiability*` tag at both `CY2023Q4I` and `CY2025Q4I`: 280 (19 at 2023 only, 12 at
2025 only); any contract-asset tag at both: 122 (10 and 9 one-sided); at `CY2023Q4I`, `DeferredRevenueCurrent` beside a
`ContractWithCustomerLiability*` tag 26 (a double count if both were used), alone 16; any revenue tag in both years 482; NetIncomeLoss in
both 465. Absent from both the `CY2025` revenue and net-income frames: HONA, PSKY, SNDK, STX, TFC, WDC. **The `CY2026Q2I` column records the
probe's counts only; the build fetches no `CY2026Q2I` or later instant before 1 May 2027 (R1-10).**

### 2.6 Licence and citation

US government works (17 U.S.C. 105; relayed, not re-verified: Grok's fetch of the statute page failed). Every CSV's `# source:` line and the
README cite: US Securities and Exchange Commission, EDGAR XBRL APIs (companyfacts, submissions, frames) on data.sec.gov, vintage <YYYYMMDD>.

### 2.7 What the spec author looked at (the blind rule)

- **Fiscal 2019 (allowed):** the per-firm identity comparisons of 2.4 at `CY2019Q4I` and `CY2019` (counts within 0.5%, no sums); start and end
  dates of eight named firms in four 2019 frames; end-date offset counts in three 2019 instant frames.
- **2023-2026 frames (41 bodies, plus three 404s):** for each, `pts`, `uom`, the keys of the data entries, how many of the 500 CIKs appear,
  duplicate CIKs (none), whether every `val` is numeric (all were), counts of end months, offsets and durations; set intersections of CIKs
  across tags; and whether the 2023 and 2025 net-income and receivable frames share each firm's end date. **No `val` was printed, summed,
  averaged, ratioed or compared, for any firm.** Ticker lists printed: CIKs lacking A1 and A3 at `CY2025Q4I` (124), those carrying A2 (13), and
  the six of 2.5.
- **Microsoft's submissions file:** filing metadata only. **Paychex's companyfacts file:** structure, and (end, start, fy, fp, form, frame,
  filed) for facts ending 2018-2019 under four tags; no value read.
- The raw 2023-2026 bodies and the companyfacts file were deleted from the spec author's scratch folder after the first draft; their sha256
  prefixes are in 2.8. This rewrite read no data. The illustrative scale in 4.0 is general knowledge, not these data.

### 2.8 Requests made by the spec author (goes to SOURCES.md)

57 requests, all GET to `data.sec.gov`, sequential, at least 1.0 s apart (enforced by the probe script), the neutral User-Agent of R2,
`Accept-Encoding: identity`, no redirect followed, no retry, no 403 or 429. 14,747,233 bytes in total. Statuses: 54 × 200, 3 × 404.
Host `data.sec.gov`; `frames/` stands for
`/api/xbrl/frames/us-gaap/`.

| # | UTC | Path | Status | Bytes | sha256, first 12 | # | UTC | Path | Status | Bytes | sha256, first 12 |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 1 | 06:21:31 | `frames/ContractWithCustomerLiability/USD/CY2019Q4I.json` | 200 | 170,706 | `6ae9cd741778` | 2 | 06:21:33 | `frames/ContractWithCustomerLiabilityCurrent/USD/CY2019Q4I.json` | 200 | 228,064 | `989bcca3c607` |
| 3 | 06:21:34 | `frames/ContractWithCustomerLiabilityNoncurrent/USD/CY2019Q4I.json` | 200 | 105,398 | `24a9375a313f` | 4 | 06:21:35 | `frames/ContractWithCustomerAssetNet/USD/CY2019Q4I.json` | 200 | 79,080 | `08b9525c0817` |
| 5 | 06:21:37 | `frames/ContractWithCustomerAssetNetCurrent/USD/CY2019Q4I.json` | 200 | 69,195 | `344a307d46bf` | 6 | 06:21:38 | `frames/ContractWithCustomerAssetNetNoncurrent/USD/CY2019Q4I.json` | 200 | 23,553 | `dbc2bc7dfcd5` |
| 7 | 06:21:40 | `frames/Revenues/USD/CY2019.json` | 200 | 435,064 | `112eb1b4349f` | 8 | 06:21:41 | `frames/RevenueFromContractWithCustomerExcludingAssessedTax/USD/CY2019.json` | 200 | 467,424 | `bb44dd228eb4` |
| 9 | 06:21:42 | `frames/NetIncomeLoss/USD/CY2019.json` | 200 | 946,165 | `f15e595eca6b` | 10 | 06:21:44 | `frames/ContractWithCustomerLiabilityCurrent/USD/CY2019Q2I.json` | 200 | 174,582 | `67fb471fe612` |
| 11 | 06:21:45 | `frames/ContractWithCustomerLiabilityCurrent/USD/CY2019Q3I.json` | 200 | 178,358 | `9c1d503fdd5d` | 12 | 06:21:47 | `/submissions/CIK0000789019.json` | 200 | 185,671 | `6acb47292f97` |
| 13 | 06:21:48 | `/api/xbrl/companyfacts/CIK0000723531.json` | 200 | 3,497,237 | `c14cf3666260` | 14 | 06:22:25 | `frames/ContractWithCustomerLiability/USD/CY2023Q4I.json` | 200 | 177,860 | `9e4576f5040c` |
| 15 | 06:22:26 | `frames/ContractWithCustomerLiabilityCurrent/USD/CY2023Q4I.json` | 200 | 267,855 | `49d6c222fea4` | 16 | 06:22:28 | `frames/ContractWithCustomerLiabilityNoncurrent/USD/CY2023Q4I.json` | 200 | 110,695 | `663928642186` |
| 17 | 06:22:29 | `frames/ContractWithCustomerAssetNet/USD/CY2023Q4I.json` | 200 | 79,430 | `eb0d0814f431` | 18 | 06:22:31 | `frames/ContractWithCustomerAssetNetCurrent/USD/CY2023Q4I.json` | 200 | 74,624 | `db9080afdf8b` |
| 19 | 06:22:32 | `frames/ContractWithCustomerAssetNetNoncurrent/USD/CY2023Q4I.json` | 200 | 23,638 | `5e73d816e127` | 20 | 06:22:33 | `frames/AccountsReceivableNetCurrent/USD/CY2023Q4I.json` | 200 | 442,699 | `85bc970e0e18` |
| 21 | 06:22:35 | `frames/ReceivablesNetCurrent/USD/CY2023Q4I.json` | 200 | 60,780 | `4358c0aa9a8b` | 22 | 06:22:36 | `frames/AccountsNotesAndLoansReceivableNetCurrent/USD/CY2023Q4I.json` | 200 | 14,350 | `904d3f03bc6b` |
| 23 | 06:22:38 | `frames/ContractWithCustomerReceivableAfterAllowanceForCreditLossCurrent/USD/CY2023Q4I.json` | 200 | 4,824 | `384bd988bcf5` | 24 | 06:22:39 | `frames/DeferredRevenueCurrent/USD/CY2023Q4I.json` | 200 | 80,634 | `60472c932ba4` |
| 25 | 06:22:40 | `frames/RevenueRemainingPerformanceObligation/USD/CY2023Q4I.json` | 200 | 104,247 | `8d373307e21c` | 26 | 06:22:42 | `frames/AccountsReceivableNetNoncurrent/USD/CY2023Q4I.json` | 200 | 11,509 | `73110e8df10d` |
| 27 | 06:22:43 | `frames/UnbilledContractsReceivable/USD/CY2023Q4I.json` | 200 | 20,815 | `5a6f0f729260` | 28 | 06:22:44 | `frames/ContractWithCustomerLiability/USD/CY2025Q4I.json` | 200 | 155,939 | `4916481b82d4` |
| 29 | 06:22:46 | `frames/ContractWithCustomerLiabilityCurrent/USD/CY2025Q4I.json` | 200 | 247,125 | `8cb8c0d85191` | 30 | 06:22:47 | `frames/ContractWithCustomerLiabilityNoncurrent/USD/CY2025Q4I.json` | 200 | 102,336 | `77466be9a3b9` |
| 31 | 06:22:49 | `frames/ContractWithCustomerAssetNet/USD/CY2025Q4I.json` | 200 | 68,029 | `b7cf577ed3bc` | 32 | 06:22:50 | `frames/ContractWithCustomerAssetNetCurrent/USD/CY2025Q4I.json` | 200 | 72,161 | `85db54cf43b6` |
| 33 | 06:22:52 | `frames/ContractWithCustomerAssetNetNoncurrent/USD/CY2025Q4I.json` | 200 | 21,703 | `5ca0a1f9ad65` | 34 | 06:22:53 | `frames/AccountsReceivableNetCurrent/USD/CY2025Q4I.json` | 200 | 407,016 | `ec500eddb769` |
| 35 | 06:22:54 | `frames/ReceivablesNetCurrent/USD/CY2025Q4I.json` | 200 | 49,720 | `c255dafc343b` | 36 | 06:22:55 | `frames/DeferredRevenueCurrent/USD/CY2025Q4I.json` | 200 | 63,046 | `4f1eefc2c4ee` |
| 37 | 06:22:57 | `frames/RevenueRemainingPerformanceObligation/USD/CY2025Q4I.json` | 200 | 97,460 | `82ae0957285e` | 38 | 06:22:58 | `frames/ContractWithCustomerLiability/USD/CY2026Q2I.json` | 200 | 125,018 | `b5c0105dd845` |
| 39 | 06:23:00 | `frames/ContractWithCustomerLiabilityCurrent/USD/CY2026Q2I.json` | 200 | 204,482 | `679f55bb2777` | 40 | 06:23:01 | `frames/ContractWithCustomerAssetNetCurrent/USD/CY2026Q2I.json` | 200 | 60,650 | `25be4564636f` |
| 41 | 06:23:02 | `frames/AccountsReceivableNetCurrent/USD/CY2026Q2I.json` | 200 | 344,333 | `31327d7f1981` | 42 | 06:23:04 | `frames/RevenueRemainingPerformanceObligation/USD/CY2026Q2I.json` | 200 | 87,872 | `d17b561817e2` |
| 43 | 06:23:17 | `frames/Revenues/USD/CY2023.json` | 200 | 409,960 | `fc7cf4e32d91` | 44 | 06:23:18 | `frames/RevenueFromContractWithCustomerExcludingAssessedTax/USD/CY2023.json` | 200 | 480,689 | `13d3dd083fe1` |
| 45 | 06:23:20 | `frames/RevenueFromContractWithCustomerIncludingAssessedTax/USD/CY2023.json` | 200 | 119,965 | `81187c80bc89` | 46 | 06:23:21 | `frames/NetIncomeLoss/USD/CY2023.json` | 200 | 974,484 | `250bd2dd6e12` |
| 47 | 06:23:22 | `frames/Revenues/USD/CY2025.json` | 200 | 345,804 | `ed2f734d3f98` | 48 | 06:23:24 | `frames/RevenueFromContractWithCustomerExcludingAssessedTax/USD/CY2025.json` | 200 | 414,741 | `a400a02d09ca` |
| 49 | 06:23:25 | `frames/RevenueFromContractWithCustomerIncludingAssessedTax/USD/CY2025.json` | 200 | 101,372 | `356cb1414f8d` | 50 | 06:23:26 | `frames/NetIncomeLoss/USD/CY2025.json` | 200 | 869,214 | `e6434be0c524` |
| 51 | 06:23:28 | `frames/IncreaseDecreaseInAccountsReceivable/USD/CY2025.json` | 200 | 472,718 | `9409e31becf3` | 52 | 06:23:29 | `frames/IncreaseDecreaseInContractWithCustomerLiability/USD/CY2025.json` | 200 | 204,315 | `213ccd678323` |
| 53 | 06:23:31 | `frames/PaymentsToAcquireBusinessesNetOfCashAcquired/USD/CY2025.json` | 200 | 198,735 | `59ba5d240c0d` | 54 | 06:25:30 | `frames/AccountsReceivableAfterAllowanceForCreditLossCurrent/USD/CY2023Q4I.json` | 404 | 366 | `eb09525baa3d` |
| 55 | 06:25:32 | `frames/AccountsReceivableAfterAllowanceForCreditLossCurrent/USD/CY2025Q4I.json` | 404 | 386 | `c03b5fb89acd` | 56 | 06:25:33 | `frames/AccountsReceivableAfterAllowanceForCreditLossCurrent/USD/CY2026Q2I.json` | 404 | 366 | `cae5a74c1ed8` |
| 57 | 06:26:01 | `frames/AccountsNotesAndLoansReceivableNetCurrent/USD/CY2025Q4I.json` | 200 | 12,771 | `8ff0403f2815` |  |  |  |  |  |  |

## 3. Method

0. **Spec first.** This spec, with the rulings, is committed under `_research/` before the first fetch and **before 2026-11-30** (S2's
   eligibility date; criterion 11). SOURCES.md cites that commit.
1. **`fetch-submissions`** (supervisor): the 500 submissions files plus older pages where 2.2 needs them → `submissions_extract.csv`.
2. **`fetch-companyfacts`** (supervisor): the 500 companyfacts files → `cf_extract.csv` (every candidate fact for the tags of 2.4 whose `end`
   is within 7 days of a needed D_Y, FY2019-FY2025, and FY2026 from 1 May 2027, with `filed`, `form`, `accn`). **No fact with `end` after the
   firm's D_2025 (or after 2026-03-31 where there is no D_2025) is extracted or read before 1 May 2027** (R1-10, C10).
3. **`fetch-frames`** (supervisor): the tags of 2.4 at `CY2019Q4I`, `CY2023Q4I`, `CY2025Q4I` and `CY2019`, `CY2023`, `CY2025`, for coverage,
   C02-C04 and C14 only (about 70 requests). **No `CY2026Q2I` or later instant and no `CY2026` duration before 1 May 2027** (G8).
4. **Statuses** (P12), assigned after the fetches, per window: `no_sec_record`, `financial_sic`, `no_sic`, `fy_ambiguous`, `end_mismatch`,
   `year_gap` (flags `gap_10k`, `gap_n`, `gap_rev`, `gap_ni`), `tiny_revenue` (revenue below 100,000,000 USD at any needed year), else
   `in_scope`. `firms.csv` carries the S1 status; other windows' membership shows in `contributions.csv` and the `n_firms` columns.
5. **Tags and values** (2.4), chosen per window → `firm_tags.csv`; values per window, basis (`own_10k`, `latest_filed`), firm and year →
   `panel.csv`.
6. **Per firm:** N_t = CA_t − CL_t; r_t = N_t / Rev_t; AA_t = N_t − r_{t−1} × Rev_t (equivalently (r_t − r_{t−1}) × Rev_t);
   T_i = AA_i,e − AA_i,b; ΔNI_i = NI_i,e − NI_i,b. Described, not registered: EA_i = (r_e − r_b) × Rev_e (R1-1).
7. **Per sample:** T = Σ T_i; T_pos = Σ max(T_i, 0); T_neg = Σ min(T_i, 0); ΔNI = Σ ΔNI_i; share = T / ΔNI × 100; share_pos = T_pos / ΔNI ×
   100; VOID tested first (Σ NI_b ≤ 0, or ΔNI < 0.02 × Σ NI_b, which covers ΔNI ≤ 0); labels on |share| and share_pos; `direction` from the
   sign of T; `t_pct_rev` = T / Σ Rev_e × 100 and `t_days_rev` = T / Σ Rev_e × 365. T and ΔNI always cover the same firms.
8. **Samples** (`headline.csv`; each gets T, T_pos, shares and labels as statistics, never registered): `primary`; `mega`; `s2_subset` (S1's
   statistic on the S2-eligible firms, R1-9); `sens_gap0`; `sens_acq` (drop firms whose acquisitions over the window's years exceed 2% of
   base-year revenue, R1-7, O-15); `sens_disc` (drop firms with non-zero discontinued-operations income in a needed year); `sens_trim` (drop
   |r| > 1 at any needed year); `sens_unbilled`; `sens_r2only` (R1-3); `sens_parts` (R1-14); `sens_latest` (R1-8); `sens_leave1` (drop the
   largest positive T_i).
9. **Contributors:** the ten largest T_i and the ten most negative (S1 primary), each with its flags and its share of T_pos or T_neg.
   **Concentration (R1-11):** the five largest firms' shares of T_pos, of T_neg and of Σ CL at FY2025, as statistics, not verdicts.
10. **Placebo** (R1-6, R1-13; the NB line of 4.6): T on FY2020→FY2022 (inputs FY2019-FY2022), FY2020→FY2021 and FY2021→FY2022, each on
    its own in-scope set, one row each with `includes_fy2020`. NB1 = max |T| / Σ Rev_e over one-year windows without FY2020 as an endpoint
    (as written, FY2021→FY2022 alone, O-11); NB2 = the two-year window's |T| / Σ Rev_e. Medians beside the maxima (O-12). Frozen from the
    first full vintage; S2 uses the frozen NB1. The band rests on three windows and the README says so.
11. **Receivables (R1-2, `receivables.csv`):** for primary firms with A1 at every needed year, AR days per year (Σ AR / Σ Rev × 365) and the
    same T construction on N^AR = AR (T_AR, in USD and days), `measure` = `collection_not_recognition`.
12. **Contract costs (R1-4):** Σ `CapitalizedContractCostNet` / Σ Rev × 365 per year beside N in days, over firms tagging it at every year.
13. **Remaining performance obligations** (descriptive): Σ at FY2022-FY2025 over in-scope firms reporting all four, n, and in days.
14. **Cash-flow cross-check** (descriptive, R1-7): T with each year's change in N taken from the cash-flow change tags of 2.4 instead of the
    balance sheet. Their sign convention is set by the builder on FY2019-FY2022 for firms without acquisitions (the sign that matches the
    balance-sheet change in most firm-years), recorded in Builder decisions, never assumed.
15. **Stages.** `build --stage pre` writes what needs no FY2023-or-later value (placebo, NB1, NB2, coverage, statuses for the placebo windows,
    fiscal years) and nothing else; `build --stage full` writes the rest. The supervisor reads `placebo.csv` to check the build, not to tune
    (R1-5). companyfacts files hold every year, so FY2023-or-later values are on disk, unread, before `--stage pre`; C10 tests what the code
    reads, not what is on disk (R1-19).

## 4. Questions, fixed in advance (answers in `headline.csv`, `registered.csv`, `contributors.csv`, `placebo.csv`, `receivables.csv`)

**4.0 Noise and resolution.** The firms are a census of a fixed set, so there is no sampling error; what limits a reading is identification:
tag choice, acquisitions, translation and ordinary contract-mix movement. One day of revenue is 1/365 = 0.274%. If the non-financial firms'
FY2025 revenue were about 35 times their ΔNI (an illustrative order of magnitude from general knowledge, **not computed from these data**),
one day would be about 9.6% of ΔNI, so the 10% threshold sits near one day and 25% near two and a half. That is why T is printed in days
beside every share (R1-5) and why the qualifier compares |T| / Σ Rev with the placebo band of the same statistic and window length. The
thresholds are the supervisor's, are not calibrated, and are not moved after the placebo is seen (C-090, C-091; R1-5).

- **Q1** Coverage per tag and period (`coverage.csv`); exclusions by status; the earnings weight (R1-22). **Q2** S1 and S1P: T, T_pos,
  ΔNI, both shares, labels, direction, qualifier, T in days (`registered.csv`). **Q3** The sensitivities and whether any changes a label.
  **Q4** Contributors with flags. **Q5** Concentration. **Q6** The megacap subset. **Q7** The placebo windows, NB1, NB2, medians.
  **Q8** Receivables in days and T_AR. **Q9** Contract costs in days. **Q10** Remaining performance obligations. **Q11** The cash-flow
  cross-check. **Q12** S2 and S2P beside `s2_subset`, on the first full build on or after 1 May 2027.
- **Not asked:** anything about prices, flows of money or motives; any judgement on a named firm; any correction of the page's 71-82% figure.

### 4.6 Registered statements (the script holds `SPEC_PREREG_SHA256` and refuses to write `registered.csv` if its constants do not reproduce this text byte for byte; one line per statement, LF endings, final LF included)

```
S1|window=FY2023..FY2025|sample=primary|vintage=first_full_build|N=CA-CL|r_t=N_t/Rev_t|AA_t=N_t-r_(t-1)*Rev_t|T_i=AA_i,2025-AA_i,2023|T=sum_i(T_i)|dNI=sum_i(NI_i,2025-NI_i,2023)|order=VOID,labels|VOID=sum_i(NI_i,2023)<=0_or_dNI<0.02*sum_i(NI_i,2023)|share=T/dNI|test=abs(share)|SHARE_BELOW_10=abs(share)<10%|SHARE_10_TO_25=10%<=abs(share)<=25%|SHARE_ABOVE_25=abs(share)>25%|direction=with_growth_if_T>0;against_growth_if_T<0;zero_if_T=0|qualifier=within_pre_window_range_if_abs(T)/sum_i(Rev_i,2025)<=NB2_else_outside_pre_window_range|compare=unrounded_decimal_prec28
S1P|window=FY2023..FY2025|sample=primary|vintage=first_full_build|T_i=as_S1|dNI=as_S1|order=VOID,labels|VOID=as_S1|share_pos=sum_i(max(T_i,0))/dNI|test=share_pos|SHARE_BELOW_10=share_pos<10%|SHARE_10_TO_25=10%<=share_pos<=25%|SHARE_ABOVE_25=share_pos>25%|direction=as_S1|qualifier=as_S1|compare=unrounded_decimal_prec28
S2|window=FY2025..FY2026|sample=s2_eligible|vintage=first_full_build_on_or_after_2027-05-01|N=CA-CL|r_t=N_t/Rev_t|AA_t=N_t-r_(t-1)*Rev_t|T_i=AA_i,2026-AA_i,2025|T=sum_i(T_i)|dNI=sum_i(NI_i,2026-NI_i,2025)|order=PENDING,PENDING_THIN,VOID_thin,VOID,labels|PENDING=no_full_build_on_or_after_2027-05-01|PENDING_THIN=fewer_than_70%_of_firms_S2_eligible_and_in_scope_at_FY2025_have_a_FY2026_10-K|VOID_thin=still_PENDING_THIN_on_or_after_2027-08-01|VOID=sum_i(NI_i,2025)<=0_or_dNI<0.02*sum_i(NI_i,2025)|share=T/dNI|test=abs(share)|labels=as_S1|direction=as_S1|qualifier=within_pre_window_range_if_abs(T)/sum_i(Rev_i,2026)<=NB1_frozen_else_outside_pre_window_range|late_filers=counted|reported_beside=s2_subset|compare=unrounded_decimal_prec28
S2P|window=FY2025..FY2026|sample=s2_eligible|vintage=as_S2|T_i=as_S2|dNI=as_S2|order=as_S2|PENDING=as_S2|PENDING_THIN=as_S2|VOID_thin=as_S2|VOID=as_S2|share_pos=sum_i(max(T_i,0))/dNI|test=share_pos|labels=as_S1P|direction=as_S2|qualifier=as_S2|compare=unrounded_decimal_prec28
NB|statistic=T_as_S1_on_each_window|windows=FY2020..FY2022(two-year,inputs_FY2019..FY2022);FY2020..FY2021(one-year,inputs_FY2019..FY2021);FY2021..FY2022(one-year,inputs_FY2020..FY2022)|firm_set=in_scope_on_the_window's_own_years_by_the_population_block|includes_fy2020=yes_if_FY2020_is_an_endpoint|NB1=max_abs(T)/sum_i(Rev_i,e)_over_one-year_windows_without_FY2020_as_an_endpoint|NB2=abs(T)/sum_i(Rev_i,e)_of_the_two-year_window|medians=reported_beside_the_maxima|frozen=first_full_vintage|S2_uses=frozen_NB1
```

**sha256 of that text: `6d113eb3905efff2447989c1de31475b7398e1d44def1cdec43cdd7eb80fc43e`** (2,409 bytes, 5 lines). `registered.csv` carries it in `prereg_sha256`,
and M27 holds its own literal copy (R1-16).

**In words.** **S1:** "The timing contribution of the tagged contract balances to these firms' change in net income from fiscal 2023 to
fiscal 2025 is below 10% of that change in size: |T| / ΔNI < 10%." **S1P:** the same with no firm's offset netted: Σ max(T_i, 0) / ΔNI <
10%. Labels: `SHARE_BELOW_10` (< 10%), `SHARE_10_TO_25` (10% to 25% inclusive), `SHARE_ABOVE_25` (> 25%); `VOID` is tested first (base net
income not positive, or ΔNI below 2% of it, which covers ΔNI ≤ 0) and carries a `void_reason`. `direction` is `with_growth` (T > 0: timing
added to reported growth), `against_growth` (T < 0) or `zero` (O-13), reported beside the label, never folded into it. The qualifier is
`within_pre_window_range` when |T| / Σ Rev_e is at most the frozen band of the same window length (NB2 for S1, NB1 for S2), else
`outside_pre_window_range`. **S2, S2P:** the same on fiscal 2025 to 2026, for firms whose FY2026 year-end falls between 2026-11-30 and
2027-02-15, reported beside `s2_subset`. `PENDING` until a full build on or after 1 May 2027; `PENDING_THIN` if fewer than 70% of the firms
S2-eligible and in scope at FY2025 (P13, O-14) then have a FY2026 10-K on data.sec.gov, re-run monthly; `VOID` (reason `thin_coverage`) if
still thin on or after 1 Aug 2027. Late filers are counted (R1-9).

**CALENDAR rows (text, for the builder to add at landing, R1-26):** `2027-05-03`, "Revenue-recognition timing S2: the supervisor runs
python3 bin/rev_recognition_timing.py fetch-submissions, fetch-companyfacts, fetch-frames (SEC_UA set), then build --vintage <today> --stage
full; read registered.csv rows S2 and S2P (label, direction, qualifier) beside s2_subset; PENDING_THIN means re-run in a month; S1 and S1P are
not re-scored"; and `2027-08-02`, "Revenue-recognition timing S2: if still PENDING_THIN, the next full build writes VOID (thin_coverage)".

### 4.7 Population rules (the script holds `SPEC_POP_SHA256`; same conventions; R1-12)

```
P1|panel=data/w3_tax/firm_tax_panel.csv|sha256=7b65abda3aed6b0acf7cf2614a14ae1d74a7aa8991880716f69aa5b25e11966b|unit=distinct_cik10|n=500
P2|exclude=sic_6000..6799_inclusive|sic_from=data.sec.gov_submissions|missing_sic=excluded
P3|D_Y=reportDate_of_the_original_form_10-K_with_reportDate_in_[Y-04-01,(Y+1)-03-31]|none=year_gap|two_or_more=fy_ambiguous|10-K/A_or_10-KT=never_defines_D_Y
P4|source=companyfacts_for_every_firm|primary_basis=own_10k:the_fact_whose_accn_is_the_year_Y_original_10-K_accession|sens_latest=latest_filed,ties_to_largest_accn|unit=USD|select_by=end_and_start,never_fy_or_fp
P5|instant=end==D_Y|duration=end==D_Y_and_350<=days(end-start)<=380|no_exact_but_abs(end-D_Y)<=7_days=end_mismatch
P6|CA=ContractWithCustomerAssetNet_if_total>=Current(+Noncurrent_where_tagged)_at_every_needed_year;else_parts=ContractWithCustomerAssetNetCurrent+ContractWithCustomerAssetNetNoncurrent|flag=total_gt_parts|sensitivity=sens_parts
P7|CL=ContractWithCustomerLiability_if_total>=Current(+Noncurrent_where_tagged)_at_every_needed_year;else_parts=ContractWithCustomerLiabilityCurrent+ContractWithCustomerLiabilityNoncurrent|fallback=DeferredRevenueCurrent+DeferredRevenueNoncurrent_only_if_no_ContractWithCustomerLiability*_tag_at_any_needed_year|never_a_total_with_its_parts
P8|N=CA-CL|receivables_not_in_N|no_contract_balance_tag_at_any_needed_year=N_is_0_every_year_and_in_scope|a_tag_at_some_needed_years_only=year_gap(gap_n);sens_gap0_sets_the_missing_side_to_0
P9|Rev=R2:RevenueFromContractWithCustomerExcludingAssessedTax;then_R3:RevenueFromContractWithCustomerIncludingAssessedTax;then_Revenues_only_if_neither_R2_nor_R3_at_every_needed_year(flag_rev_fallback)|one_tag_per_window|sens_r2only=drop_rev_fallback
P10|NI=NetIncomeLoss|no_fallback
P11|needed_years=S1:FY2022..FY2025;S2:FY2024..FY2026;placebo:each_window's_inputs|year_gap=N_or_Rev_or_NI_or_D_Y_missing_at_a_needed_year|floor=Rev>=100000000_USD_at_every_needed_year_else_tiny_revenue
P12|status_order=no_sec_record,financial_sic,no_sic,fy_ambiguous,end_mismatch,year_gap,tiny_revenue,in_scope
P13|S2_eligible=in_scope_for_S2_and_D_2026_in_[2026-11-30,2027-02-15]|S2_eligible_at_FY2025=fiscalYearEnd_MMDD_in_[1130,1231]or[0101,0215]_and_in_scope_on_FY2024..FY2025
```

**sha256 of that text: `6a68f3d883929120d55f490bb799280a81e661c13773acdc8251905167d7c769`** (2,240 bytes, 13 lines). `registered.csv` carries it in `population_sha256`.

## 5. Outputs

**Script `bin/rev_recognition_timing.py`.** Modes `fetch-submissions`, `fetch-companyfacts`, `fetch-frames` (supervisor only, under R1-R3a),
`build --vintage YYYYMMDD --stage pre|full` (offline, byte-identical on re-run), `selftest` (synthetic, no network, under 30 s). Committed
files in `data/rev_recognition_timing/` (the first fifteen lines below) and `data/vintages/rev_recognition_timing/<YYYYMMDD>/` (the last
three); each CSV begins with one `# source:` line.

**Header allowlist, canonical text.** One line per file, `<name>:<headers comma-joined, no spaces>`, LF endings, final LF included, in this
order. The script holds `SPEC_ALLOW_SHA256`; **`bin/check.sh` holds its own literal copy of these eighteen lines** and never reads them from
the script. M27 skips the `# source:` line.

```
firms.csv:cik10,tickers,entity_name,sic,fye_mmdd,status,flags
firm_years.csv:cik10,fiscal_year,period_end,accession,filing_date
firm_tags.csv:window,cik10,component,structure,tags
panel.csv:window,basis,cik10,fiscal_year,period_end,revenue_tag,revenue_usd,ni_usd,ca_usd,cl_usd,n_usd,r,ar_usd,contract_cost_usd
contributions.csv:window,sample,cik10,ticker,aa_base_usd,aa_end_usd,t_usd,dni_usd,rev_end_usd,flags
headline.csv:vintage,window,sample,statistic,value,unit,n_firms
registered.csv:statement_id,window,sample,vintage,n_firms,numerator_usd,t_usd,dni_usd,ni_base_usd,share_pct,t_pct_rev,t_days_rev,noise_band_pct_rev,qualifier,direction,label,void_reason,prereg_sha256,population_sha256
contributors.csv:window,side,rank,cik10,ticker,entity_name,t_usd,share_of_side_pct,flags
placebo.csv:window,years,includes_fy2020,n_firms,t_usd,t_pos_usd,rev_end_usd,t_pct_rev,dni_usd,share_pct
receivables.csv:window,row_type,fiscal_year,measure,n_firms,ar_usd,rev_usd,ar_days,t_ar_usd,t_ar_days_rev
coverage.csv:tag,period,role,n_cik_all500,n_cik_in_scope
checks.csv:check_id,description,expected,observed,status
vintages.csv:vintage,url_path,status,bytes,sha256,retrieved_utc
fetch_log.csv:utc_time,vintage,host,path,status,bytes,sha256,elapsed_s
revisions.csv:vintage_prev,vintage_new,window,sample,statistic,value_prev,value_new
frames_extract.csv:vintage,tag,period,cik10,accn,start,end,val
cf_extract.csv:vintage,cik10,tag,start,end,val,accn,form,fp,fy,filed
submissions_extract.csv:vintage,cik10,sic,fye_mmdd,form,report_date,filing_date,accession
```

**sha256 of that text: `99e8e8f929139485e37cec69c3e1afd6623d33a40d8cbc854ad0c05e75e55376`** (1,547 bytes, 18 lines). A builder who needs a column changes this text and
its hash first, logs it in Builder decisions, and tells the supervisor.

**Allowed values.** In `firms.csv`, `status` in {in_scope, no_sec_record, financial_sic, no_sic, fy_ambiguous, end_mismatch, year_gap,
tiny_revenue}; `flags` everywhere a `|`-joined subset of {acq2, disc_ops, rev_fallback, total_gt_parts, extreme_r, near_end, gap_10k, gap_n,
gap_rev, gap_ni, gap0_imputed, unbilled_added}; `component` in {ca, cl, rev, ni, ar, contract_cost}; `structure` in {single, total, parts,
deferred_revenue, absent_everywhere, gap}; `basis` in {own_10k, latest_filed}; `window` in {fy2023_fy2025, fy2025_fy2026, fy2020_fy2022,
fy2020_fy2021, fy2021_fy2022}; `includes_fy2020` in {yes, no}; `sample` in {primary, mega, s2_subset, s2_eligible, sens_gap0, sens_acq,
sens_disc, sens_trim, sens_unbilled, sens_r2only, sens_parts, sens_latest, sens_leave1}; `unit` in {usd, pct, days, count, ratio, label};
`side` in {positive, negative}; `row_type` in {level, window_t}; `measure` in {collection_not_recognition}; `role` in {component, revenue,
net_income, receivable, contract_cost, descriptive, flag}; `statement_id` in {S1, S1P, S2, S2P}; `label` in {SHARE_BELOW_10,
SHARE_10_TO_25, SHARE_ABOVE_25, VOID, PENDING, PENDING_THIN}; `void_reason` in {none, base_not_positive, dni_small, thin_coverage};
`direction` in {with_growth, against_growth, zero}; `qualifier` in {within_pre_window_range, outside_pre_window_range, none}; `status` in
`checks.csv` in {PASS, WARN, FAIL, INFO}; in `vintages.csv` and `fetch_log.csv` it is the HTTP code. Keys unique: `firms.csv` (cik10);
`firm_years.csv` (cik10, fiscal_year); `firm_tags.csv` (window, cik10, component); `panel.csv` (window, basis, cik10, fiscal_year);
`contributions.csv` (window, sample, cik10); `headline.csv` (vintage, window, sample, statistic); `registered.csv` (statement_id, vintage);
`contributors.csv` (window, side, rank); `placebo.csv` (window); `receivables.csv` (window, row_type, fiscal_year). **No output carries
HELD, FALSIFIED, PROVEN, CAUSED, REFUTED, MATERIAL or NOT_MATERIAL.**

- **`README.md`** (generated; G13 scans it), plain words, in this order: (1) two opening sentences: what was measured ("how much of the
  change in these firms' net income from fiscal 2023 to fiscal 2025 came from revenue booked ahead of or behind billing in their tagged
  contract balances") and the S1 and S1P results (shares, labels, direction, qualifier, T in days, number of firms, earnings weight);
  (2) the denial sentence; (3) A1 and A3 in one sentence each, with "the share is a ceiling on size for the tagged balances, not an estimate
  of the effect"; (4) what is left out: receivables (collection, not recognition), capitalized contract costs, stock-funded acquisitions,
  currency translation, dimension-only balances; (5) the S1 table with sensitivities and the megacap subset; (6) contributors each way with
  their flags and the sentence "a large contributor is not a finding about that firm", and the concentration statistics; (7) the placebo
  windows, the band and the qualifier, saying the band rests on three windows, two of them with fiscal 2020 as an endpoint; (8) the
  receivables table, contract costs, remaining performance obligations and the cash-flow cross-check, each marked descriptive; (9) S2, S2P
  and when they are scored; (10) coverage and exclusions, with the count of financial firms and the SIC-versus-ASC 606 boundary; (11) a
  column dictionary glossing "contract asset" (revenue booked, not yet billable), "contract liability" (billing or cash received before
  revenue is booked), "excess accrual" (the part of a year's change in the net contract position beyond what growth at the previous year's
  ratio would give), "trade receivable", "remaining performance obligation", "fiscal year", "vintage", "operating cash flow"; (12) citations.
- **`SOURCES.md`:** every URL with date and status (2.8, the 404s included), the note that the spec author's 57 and the supervisor's 8
  requests of 28 Oct used the neutral UA (R1-17), the fiscal-year and fact-selection rules, the 2019 evidence of 2.4, 2.7, Builder decisions.

## 6. Leak and integrity rules

1. Committed: in `data/rev_recognition_timing/` only the fifteen CSVs, README.md and SOURCES.md; in each vintage folder only the three extract
   CSVs; never a `.json`, `.zip`, `.html` or STOP file. The `raw/` cache is gitignored (O-9).
2. No local path (`/Users/`, `/private/`, `~/`), no `@`, no email address, no personal name, and **no byte of `SEC_UA`'s value** in any written
   file (R1-17). Company names in `entity_name` are SEC registrant names. The script writes nothing outside its two folders except landing's
   `.gitignore` rule, REPRODUCE.md paragraph and CALENDAR lines.

## 7. Selftests (synthetic only; each guard applies its own mutant, and an uncaught mutant fails the selftest; R1-25's fixtures are two-sided)

**G13's literal patterns, both compiled with `re.I`** (pasted, not imported). `CAUSAL_RX` (as in the Z.1 spec):

```
\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of)\b
```

`EXTRA_RX` (this build's ban list with R1-24's additions; the denial sentence is exempt):

```
\b(?:in|out)flows?\b|\bflow(?:s|ed|ing)?\s+(?:into|out\s+of|from|to)\b|\bmanipulat\w*|\bmanag(?:e|ed|es|ing)\s+(?:earnings|results|revenue)\b|\bearnings\s+management\b|\baggressive\w*|\bfraud\w*|\bmisstat\w*|\binflat(?:e|ed|es|ing)\b|\bboost(?:s|ed|ing)?\b|\bpadd(?:ed|ing)\b|\bchannel[- ]stuff\w*|\blow[- ]quality\b|\bfake\b|\billusory\b|\bnot\s+real\b|\b(?:prices?|valuations?|multiples?|stocks?|shares)\s+(?:rose|fell|rallied|moved|jumped|dropped)\b|\bmaterial\w*|\boverstat\w*|\bpulled\s+forward\b|\bflatter\w*|\bprematur\w*|\bwindow[- ]dressing\b|\bred\s+flags?\b|\bfictitious\b|\bsmooth(?:ed|ing)\b|\babnormal\w*
```

| Guard | Protects | Mutant that must be caught |
|---|---|---|
| G1 parsing | R8 | a float sum; a missing fact read as 0; a non-USD unit accepted; **a value above 2^53 and a fractional value** read through float; `pts` used as a count of the 500 |
| G2 fiscal years | 2.2 | a 10-K/A or 10-KT defining D_Y; the `fy` label used (a retailer with reportDate 2026-02-01 put in FY2026); a window edge off by a day (2026-03-31, 2026-04-01); two 10-Ks in a window not `fy_ambiguous` |
| G3 fact selection | 2.3, R1-8, R1-20 | **durations of 349, 350, 380 and 381 days** (only 350-380 accepted); a fact 3 days off D_Y used (must be `end_mismatch` when no exact match); the latest-filed fact used in `own_10k`; a year's ratio taking N and Rev from different accessions; `sens_latest` using first-reported values; selection by `fy`/`fp` |
| G4 tags and structure | 2.4, R1-3, R1-14 | the parts used where total ≥ parts at every year; the total used where it is below its parts in one year; total and parts added; `DeferredRevenueCurrent` beside a `ContractWithCustomerLiability*` tag; `Revenues` used where R2 exists at every year; R3 skipped for `Revenues`; a revenue tag switching between years; A2 or A3 in AR days; receivables added to N |
| G5 statuses and gaps | 2.4, P8, P11 | a firm with no contract tag at any year excluded (must be in scope, N = 0); a partially tagged component kept in `primary`; FY2022 missing not giving `year_gap`; `sens_gap0` not imputing 0; `no_mid` or `no_receivable` written |
| G6 statistic and labels | 3.6-3.7, 4.6 | T computed as EA; AA with r_t instead of r_{t−1}; T_pos netting offsets; labels on the signed share; **VOID not tested first** (ΔNI ≤ 0 with \|share\| < 10 must be VOID); fixtures ΔNI/Σ NI_b = **0.0199 (VOID), 0.0201 (not VOID)**; \|share\| = **9.9996, 10.0000, 10.0001, 25.0000, 25.0001** → BELOW_10, 10_TO_25, 10_TO_25, 10_TO_25, ABOVE_25 on unrounded Decimals; direction wrong for T < 0 |
| G7 exclusions | 2.1, P2, P11 | SIC 6000 or 6799 kept; 5999 or 6800 excluded; revenue of 99,999,999 USD in one needed year kept |
| G8 S2 gate | 4.6, R1-9, R1-10 | FY2026 year-ends **2026-11-29 (out), 2026-11-30 (in), 2027-02-15 (in), 2027-02-16 (out)**; a `CY2026Q2I`-or-later instant or `CY2026` duration fetched, or a fact with `end` after D_2025 read, before 2027-05-01; S2 scored before then (must be PENDING); 69.99% coverage not PENDING_THIN, 70.00% PENDING_THIN; still thin on 2027-08-01 not VOID |
| G9 contributors and concentration | 3.9 | eleven rows on a side; flags missing; share computed over T instead of T_pos or T_neg; top five taken by absolute value across sides |
| G10 registered | 4.6, 4.7 | **a constant edited so either block's sha256 changes** (build refuses `registered.csv`); `prereg_sha256` differing from M27's literal copy; NB1 used for S1 |
| G11 placebo | 3.10 | a FY2023-or-later value read in `--stage pre`; a window other than the three; EA instead of T; a FY2020-endpoint window in NB1; the band recomputed from a later vintage for S2 |
| G12 allowlists | 5 | an extra or renamed column; `SPEC_ALLOW_SHA256` not the hash of the canonical text, **or not equal to M27's literal copy**; `# source:` compared as a header; a sixteenth CSV in the output folder; check.sh reading the header lines from the script; a duplicate key |
| G13 wording | R6 | the patterns above applied to README.md except the denial sentence; the README template passes; "timing inflated earnings", "the firms boosted revenue", "revenue was pulled forward", "abnormal accruals", "a material share", "receivables drove the rally" and "money flowed into software" each fail |
| G14 STOP latch | R3a | AST scan: a STOP path reached by any remove, rename, replace, `write_text`, `write_bytes`, or `open` in mode w or a; a planted `STOP_rrt` blocks every request (exit 2, file unchanged); 301, 403, 429, 500, empty, HTML and non-JSON bodies each write STOP with five fields; a frame 404 writes no STOP; a timeout exits 3 |
| G15 fetch safety | R1-R3, R1-17, R1-18 | a request to any host but data.sec.gov; a fetch with `SEC_UA` unset (must exit 2); **`SEC_UA`'s value in any written byte** (fixture value planted, every output scanned); a redirect followed; a retry; **a 0.9 s gap**; a cap exceeded; a body already cached with a matching sha256 re-requested |
| G16 vintages | R4 | a build mixing two vintages; S1 re-scored on a later vintage; `revisions.csv` appended instead of regenerated |
| G17 leak guard | 6 | on a planted folder: a `.json`, a `/Users/` path, an `@`, each reported; the clean folder passes |
| G18 descriptive tables | 3.11-3.14 | AR days with A2 or A3; T_AR added to T; `measure` missing; contract costs added to N; a cash-flow sign assumed rather than set from FY2019-FY2022 |
| G19 isolation | R7 | AST scan: the script opens a project path other than the panel and its own folders (fixture: `data/w3_tax/results.json`) |

## 8. Pinned checks (`checks.csv`)

- **C01 Panel (FAIL):** sha256 `7b65abda3aed6b0acf7cf2614a14ae1d74a7aa8991880716f69aa5b25e11966b`, 343,641 bytes, 503 rows, 500 distinct `cik10`, the three shared CIKs of 2.1.
- **C02 Coverage pins (WARN, first vintage only):** each `CY2023Q4I` and `CY2025Q4I` count of the 500 in 2.5 within ±5 (filers amend; a larger move is reported, not fixed).
- **C03 Structure pins (WARN):** the fiscal-2019 presence and identity counts of 2.4, re-derived from the `CY2019Q4I` and `CY2019` frames.
- **C04 Alignment pins (WARN):** the `NetIncomeLoss/CY2019` dates of 2.3 (Microsoft 2018-07-01 to 2019-06-30; Oracle and Nike 2019-06-01 to 2020-05-31).
- **C05 Microsoft (FAIL):** D_2023 = 2023-06-30, D_2025 = 2025-06-30, FY2026 10-K filed 2026-07-29, not S2-eligible.
- **C06 Content (FAIL):** frames for A1, `ContractWithCustomerLiabilityCurrent`, R2 and NetIncomeLoss return 200 at every fetched period; every fact used is USD and numeric.
- **C07 Tamper (FAIL):** per panel row N = CA − CL within 1 USD; per window and sample, Σ contributions equals the headline T, T_pos and ΔNI within 1 USD.
- **C08 Same filing (FAIL):** every `own_10k` value's `accn` equals that firm-year's original 10-K accession (R1-8).
- **C09 Fiscal years (FAIL):** every in-scope firm's D_Y comes from a form-`10-K` `reportDate` inside its window.
- **C10 Blind order (FAIL):** the code reads no FY2023-or-later value in `--stage pre`, and no `CY2026Q2I`-or-later instant, `CY2026` duration or fact with `end` after D_2025 before 2027-05-01 (R1-10, R1-19).
- **C11 Hashes (FAIL):** the constants reproduce the three hashes of 4.6, 4.7 and 5; `prereg_sha256` in `registered.csv` equals 4.6's.
- **C12 Fixed output (FAIL):** a second `build` leaves every output sha256 unchanged.
- **C13 Cache integrity (FAIL):** each raw body's sha256 and size equal its `vintages.csv` row.
- **C14 Frames against companyfacts (FAIL, R1-21):** for the first 15 in-scope December year-end CIKs in panel order (O-16), the latest-filed companyfacts value equals the frame value within 1 USD for A1, `ContractWithCustomerLiabilityCurrent`, R2 and NetIncomeLoss at `CY2019Q4I`/`CY2019`, wherever both exist.

## 9. Success criteria (each with the command and the number that would disprove it)

1. `python3 bin/rev_recognition_timing.py selftest` prints G1 to G19, each `caught`, and exits 0. **Disproved by** any `SURVIVED`, a missing G-number, or a non-zero exit.
2. **Supervisor's fetches:** `fetch_log.csv` rows all have host `data.sec.gov`, no status 403, 429 or 3xx, no gap below 1.0 s; and `grep -rlF "$SEC_UA" data/rev_recognition_timing data/vintages/rev_recognition_timing | wc -l` prints **0**. **Disproved by** another host, a STOP file, a shorter gap, or any file holding the UA.
3. `build --vintage <v> --stage full`, then `grep -c ',FAIL$' data/rev_recognition_timing/checks.csv` prints **0**. WARN rows (C02-C04) are reported to the supervisor.
4. `grep -rlE 'HELD|FALSIFIED|PROVEN|CAUSED|REFUTED|MATERIAL' data/rev_recognition_timing/ | wc -l` prints **0**; `registered.csv` has S1 and S1P rows labelled SHARE_* or VOID and S2 and S2P rows labelled PENDING, all with the 4.6 and 4.7 hashes.
5. **Hand re-derivation by a verifier** from `cf_extract.csv` without the script, for three firms named by the supervisor (a December year-end, a June year-end, one using a contract-asset total): N, r, AA_2023, AA_2025, T_i and ΔNI_i from the `own_10k` facts equal `contributions.csv`. **Disproved by** any difference above 1 USD (0.000001 for r).
6. A `python3 -I -c` sum over `contributions.csv` (window `fy2023_fy2025`, sample `primary`) reproduces T, T_pos and ΔNI in `registered.csv` within 1 USD and both shares to 3 decimals. **Disproved by** a larger gap.
7. **M27** (warn-only, in `bin/check.sh --all`), with its own copies of the eighteen header lines and the 4.6 hash: the file names; headers (skipping `# source:`); no `.json`, `.zip` or STOP in git; no local path or `@`; no G13 pattern in README.md outside the denial sentence; no banned verdict word (✗); labels, directions and qualifiers only from 5 (✗); `prereg_sha256` equal to its copy (✗); C07's sums (✗); no duplicate key (✗). **On a scratch copy** with a planted `.json`, a renamed header, a `MATERIAL` cell and a T that does not equal its contributions, M27 prints **four** ✗ lines; on the clean folder, ✓. Shown failing on the planted copy before it lands.
8. **Supervisor hash step:** extract the three canonical blocks from this spec and take their sha256: they equal `SPEC_PREREG_SHA256`, `SPEC_POP_SHA256`, `SPEC_ALLOW_SHA256`, M27's literal copies, and `6d113eb3905efff2447989c1de31475b7398e1d44def1cdec43cdd7eb80fc43e`, `6a68f3d883929120d55f490bb799280a81e661c13773acdc8251905167d7c769`, `99e8e8f929139485e37cec69c3e1afd6623d33a40d8cbc854ad0c05e75e55376`.
9. **Stage order:** `placebo.csv` with three windows, NB1 and NB2 comes from a `--stage pre` run older than any `--stage full` output. **Disproved by** a full-stage file older than the placebo file.
10. **README cold-reader test.** Three fresh agents read only the README: a non-specialist, an accountant, and one told to report both S1 shares, labels, direction and qualifier. **Pass** only if the first two can say what a contract asset and a contract liability are, that receivables and contract costs are left out, that the share is a ceiling on size for tagged balances, that financial firms are excluded, and that nothing here is about prices or misconduct; and the third reports all of it. **Fail** if any reader thinks a firm managed its earnings or that timing moved the market.
11. **Spec before data:** `git log --diff-filter=A --format=%cI -- _research/2026-10-28-Revenue-Recognition-Timing-Spec.md` is earlier than the first `utc_time` in `fetch_log.csv` and earlier than 2026-11-30T00:00:00Z. **Disproved by** a later commit, or none.
12. **May 2027 run:** after the supervisor's fetches and a full build on or after 2027-05-01, `registered.csv` has S2 and S2P rows labelled SHARE_*, VOID or PENDING_THIN (with the coverage share in `headline.csv`), and the S1 and S1P rows are unchanged. **Disproved by** a changed S1 or S1P value, or PENDING after that date.
13. **Registration (R1-26):** at landing, the two CALENDAR rows of 4.6 and a `RESEARCH_STATE.md` §5 row for S2 naming the goal row it serves exist; no findings document and no read-table row. **Disproved by** a missing row.

**Landing (builder):** `.gitignore` rule for `raw/`, REPRODUCE.md paragraph, the CALENDAR rows and the RESEARCH_STATE.md §5 row (R1-26), M27, a HANDOVER row; commits nothing.

## 10. OPEN questions

Answered or closed by round 1: O-1 (reworded in 3.15: the pre stage is a build check; FY2023-or-later values are on disk, unread; C10 tests
what the code reads, R1-19), O-2 (receivables leave N; AR days use A1 only, R1-2), O-3 (FY2022 added, R1-1), O-7 (signs set by the builder,
R1-7), O-8 (both shares registered, R1-1), O-10 (the estimand is T, R1-1). Still open:

- **O-4 Megacap list.** Nine names (2.1); E2's six alone keep continuity with the page's useful-life row.
- **O-5 Unbilled receivables.** Placement unknown in companyfacts; `sens_unbilled` shows the effect for firms with no contract-asset tag.
- **O-6 Financial boundary.** SIC 6000-6799 is not ASC 606's scope (Grok); it drops exchanges, brokers and insurance brokers and keeps card
  networks. The supervisor may keep SIC 6200-6299 and 6411.
- **O-9 Raw cache.** About 2 GB if the 500 companyfacts files average the 3.5 MB of the one observed; kept locally, moved to the private
  Dropbox companion, or deleted after extraction with only the sha256 kept.

New questions raised by applying the rulings (not decided here; the spec's placeholder is in brackets):

- **O-11 `includes_fy2020` and NB1 (R1-6).** FY2021→FY2022 needs FY2020 balances as r_2020 inside AA_2021. Read as "FY2020 as an endpoint",
  NB1 is that one window [the hashed text uses this reading]; read as "FY2020 among the inputs", no one-year window qualifies and NB1 is empty.
- **O-12 Medians beside the maxima (R1-13).** Each band has one qualifying window, so a median over windows equals the maximum. Median over
  all windows of each length (FY2020 included), or the median across firms of |T_i| / Rev_i? [the former].
- **O-13 Direction at T = 0 (R1-5).** The ruling names two values; the hashed text adds `zero` for T = 0 exactly.
- **O-14 S2 eligibility before FY2026 exists (R1-9).** The 70% test needs the eligible set at FY2025, before any FY2026 year-end date is
  known. [P13: submissions `fiscalYearEnd` between 1130 and 0215, and in scope on FY2024-FY2025.]
- **O-15 `sens_acq` years (R1-7).** With T built from FY2022-FY2025, "the window's years" could be FY2024-FY2025 or FY2023-FY2025, and the
  base revenue FY2023 or FY2022. [FY2023-FY2025 against FY2023 revenue, since AA_2023 depends on the FY2023 change.]
- **O-16 C14's firm set (R1-21).** "In-scope" for S1 needs FY2022-FY2025 data, so C14 runs only in `--stage full`; choosing the 15 firms from
  the FY2020→FY2022 placebo scope instead would let it run in `--stage pre`. [S1 scope, full stage.]
- **O-17 `sens_r2only` (R1-3).** As ruled it drops `rev_fallback` firms only, so firms on R3 stay. Should R3 firms also be dropped? [kept]
- **O-18 `population_sha256` in `registered.csv`.** R1-16 names only `prereg_sha256`; the spec adds the population hash beside it to bind the
  sample to the result (R1-12). The supervisor may strike the column, which changes the allowlist hash.

## Supervisor rulings

*Appended here by the supervisor, newest last, before any data run; they override the body. Round 1 is copied verbatim from the supervisor's
file except one substitution: a personal name in R1-17 is replaced by "The principal" (house rule: no personal identifiers in public files).*

## Supervisor rulings, round 1 (Grok attack and Sonnet second review), 28 Oct 2026 — before any build

Grok's attack (fenced Cursor lane, 837 s, 19 fetches, nothing blocked; verdict BUILD WITH CHANGES) is kept in
`_research/2026-10-28-Grok-G13-Revenue-Timing-Attack.md`. The Sonnet second review (no network; verdict BUILD WITH CHANGES; both hashes
reproduced, panel sha256 and the 2.8 table confirmed) is summarised in R1-12 to R1-24. The supervisor re-read two of its taxonomy citations at source (Calcbench element
pages for `AccountsNotesAndLoansReceivableNetCurrent` and `Revenues`, 28 Oct): both definitions are as quoted. Two URLs in its answer were
never fetched (catalog.data.gov, uscode.house.gov); nothing below rests on them.

- **R1-1 The estimand changes (Grok A1, case (a); accepted).** EA and EA_last are stock residuals; they miss an abnormal accrual in the base
  year reversing out (Grok's worked case: true timing contribution 210 against UB 4.8%). A2 is no longer assumed; it is measured. Define, per
  firm and fiscal year t, the abnormal accrual AA_t = (r_t − r_{t−1}) × Rev_t, with N and r as amended in R1-2. The timing contribution to the
  window's change in net income is **T = Σ_i (AA_i,e − AA_i,b)**, which for S1 is AA_2025 − AA_2023 and needs balances and revenue at FY2022,
  FY2023, FY2024 and FY2025 (O-3 resolved: FY2022 is added). Under A1 (no cost, no tax) T is the timing piece of ΔNI for the tagged balances,
  an identity, not a bound; it overstates the magnitude by the margin and the tax rate, so |T| / ΔNI is a ceiling on the size of the effect
  of the tagged balances only. Register on **share = T / ΔNI** (net, the aggregate identity) and on **share_pos = Σ_i max(T_i, 0) / ΔNI** (gross positive, the
  stricter ceiling: no firm's offset is netted; Sonnet item 1). EA, EA_last and UB are withdrawn from `registered.csv`; EA may stay in
  `headline.csv` as a described statistic.
- **R1-2 Trade receivables leave the registered numerator (Grok change 2; accepted).** N = CA − CL: contract assets minus contract
  liabilities, the ASC 606 measure of revenue recognised ahead of billing (contract asset) or behind it (contract liability). Trade
  receivables are billed consideration awaiting cash: a collection-terms measure. They are reported in a separate descriptive table in days
  of revenue (AR days, A1 `AccountsReceivableNetCurrent` only; A2 and A3 are not trade receivables, as their definitions say), with the
  same T construction beside it, labelled "collection, not recognition". Firms with no contract-balance tag at any year have N = 0 at every
  year (the absent-everywhere rule) and stay in scope: zero is the right value for a firm without contract balances. The `no_receivable`
  status is withdrawn.
- **R1-3 Revenue tag (Grok change 3; accepted with a fallback).** R2 `RevenueFromContractWithCustomerExcludingAssessedTax` first, then R3,
  then `Revenues` only when neither R2 nor R3 exists at every year the window needs, flagged `rev_fallback`; no "largest" rule. Sensitivity
  `sens_r2only` drops the flagged firms.
- **R1-4 Capitalized contract costs (Grok change 5; accepted, descriptive).** `CapitalizedContractCostNet` is fetched and reported beside N in
  days of revenue. It is cost timing, outside N; the README says the measure ignores it.
- **R1-5 Labels and sign (Grok change 6 and Sonnet item 4; partly accepted).** The thresholds stay 10% and 25%, applied to |share| and to
  share_pos, with the labels `SHARE_BELOW_10`, `SHARE_10_TO_25`, `SHARE_ABOVE_25` (no "material": audit vocabulary) and the sign reported
  separately: `direction` = `with_growth` (T > 0, timing added to reported growth) or `against_growth` (T < 0). A large negative share is no
  longer folded into NOT_MATERIAL. **Overruled:** replacing the share with a days scale. The page's question is a share of earnings growth;
  days are reported beside it (T in days of FY2025 revenue) so a reader can see the resolution. The thresholds are not moved after the
  placebo is seen (O-1 answered: the supervisor reads `placebo.csv` from `--stage pre` only to check the build, not to tune).
- **R1-6 Placebo (Grok change 6; accepted).** Placebo windows of the same T statistic on years that need no FY2023-or-later input:
  two-year FY2020→FY2022 (inputs FY2019-FY2022) and one-year FY2020→FY2021 and FY2021→FY2022 (one-year T = AA_e − AA_b on consecutive
  years). Each is reported on its own row with `includes_fy2020` = yes/no; the qualifier uses NB1 = max |T| / ΣRev over one-year windows
  without FY2020 as an endpoint, NB2 = the two-year window's |T| / ΣRev, both shown. The band is thin (three windows) and the README says so.
- **R1-7 Acquisitions and translation (Grok change 7; partly accepted).** `sens_acq` drops firms whose
  `PaymentsToAcquireBusinessesNetOfCashAcquired` over the window's years exceeds 2% (was 10%) of base-year revenue; stock-funded deals and
  currency translation are not screened, and the README says both can move N with no change in recognition. The cash-flow change tags
  stay descriptive; their sign convention is determined by the builder on FY2019-FY2022 for firms without acquisitions (the sign that
  matches the balance-sheet change in most firm-years), recorded in Builder decisions, never assumed.
- **R1-8 Same-filing values (Grok change 8; accepted).** Primary: each fiscal year's N, Rev and NI as first reported in that year's own
  original 10-K (the fact whose `accn` is the year-t 10-K accession), so a year's ratio never mixes filings. Sensitivity `sens_latest`: the
  latest-filed values. Consequence: every firm is served by its companyfacts file (one request per firm, about 500); frames are kept for the
  coverage table and C02-C04 only. Routing (2.3) collapses to one path.
- **R1-9 S2 (Grok (d) and change 9; accepted).** S2 is the November-to-February holdout, reported beside `s2_subset` (S1's statistic on
  the same firms). PENDING until a full build on or after 1 May 2027; if fewer than 70% of the S2-eligible firms in scope at FY2025 have a
  FY2026 10-K on data.sec.gov at that build, PENDING_THIN, re-run monthly; VOID after 1 Aug 2027 if still thin. Late filers are counted.
- **R1-10 The interim is removed (Grok (d); accepted).** A mid-2026 balance is partial information about FY2026 while S2 is unscored.
  No CY2026Q2I or later instant is fetched or used before 1 May 2027 (G8 and C10 extend to it).
- **R1-11 Concentration (Grok change 6; accepted, descriptive).** Report the five largest firms' shares of gross positive T, gross negative
  T and of total contract liabilities at FY2025, fixed here as statistics, not verdicts.
- **R1-12 VOID first; population hashed (Sonnet item 3; accepted).** The canonical text says VOID is tested first (Σ NI_b ≤ 0, or ΔNI < 0.02
  × Σ NI_b, which covers ΔNI ≤ 0). A third canonical block, the population rules (SIC 6000-6799 excluded, the 100,000,000 USD revenue floor,
  the tag priorities of 2.4 as amended, the duration rule, the structure and gap rules, R1-8's source rule), is hashed with the statements,
  so the sample cannot drift after a result is seen.
- **R1-13 Qualifier on the same statistic (Sonnet item 2; accepted).** The qualifier compares |T| / ΣRev_e with the placebo band of the same
  T statistic and window length (R1-6); NB1, NB2 and the placebo firm-set rule are in the hashed text; the band is frozen from the first
  vintage and S2 uses the frozen value; medians are reported beside the maxima.
- **R1-14 Total versus parts (Sonnet item 5; accepted).** Use the total when total ≥ Current (+ Noncurrent where tagged) at every year the
  window needs; else the parts; flag `total_gt_parts`; sensitivity `sens_parts`. G4 gains the mutant.
- **R1-15 Missing years (Sonnet item 6; accepted).** A firm needs N, Rev and NI at every year its window uses (FY2022-FY2025 for S1);
  otherwise status `year_gap`, out of the primary sample. `no_mid` is withdrawn.
- **R1-16 Headers (Sonnet item 7; accepted).** `contributors.csv` gains `flags`; `contributions.csv` is keyed (window, sample, cik10);
  `fetch_log.csv` gains `vintage` and `elapsed_s`; `registered.csv` carries `prereg_sha256`, and M27 holds its own literal copy of that hash.
  Hash convention: each block's lines with LF endings, the final LF included. Re-hash once after all changes.
- **R1-17 User-Agent and who fetches (Sonnet item 8; ruled).** The principal's ruling of 12 Sep (CLAUDE.md) gives sec.gov hosts a declared contact,
  and data.sec.gov is a sec.gov host. The fetch modes therefore read `SEC_UA` from the environment, refuse to run without it (exit 2), and
  never write it to any file, log or output; G15 tests that it is absent from every written byte. **Only the supervisor runs the fetch
  modes.** The builder writes the code and the selftest and runs `build` offline on the supervisor's cache. The spec author's 57 probe
  requests and the supervisor's 8 coverage requests of 28 Oct used the neutral UA; SOURCES.md says so.
- **R1-18 Fetch practicality (Sonnet item 9; accepted).** Each fetch mode is resumable: a body already in `raw/` with its `vintages.csv`
  sha256 is not re-requested. Caps: submissions 1,000, companyfacts 600, frames 250. The gap is at least 1.0 s and G15 tests 0.9 s as a
  violation. Timeout 300 s. Statuses are assigned after the fetches (routing is gone, R1-8), so the circularity disappears.
- **R1-19 The blind property, stated honestly (Sonnet item 10; accepted).** companyfacts files hold every year, so FY2023-or-later values are
  on disk, unread, before `--stage pre`. C10 tests what the code reads, not what is on disk; O-1 is reworded to say so. The pre stage is a
  build check, not a tuning step (R1-5).
- **R1-20 Fiscal-year matching (Sonnet item 11; accepted).** Strict equality of fact `end` with D_Y stays; facts within ±7 days are counted
  as a diagnostic, and a firm with no exact match but a near one gets status `end_mismatch`, not `no_revenue`.
- **R1-21 Frames against companyfacts (Sonnet item 12; accepted).** C14 (FAIL): for the first 15 in-scope December year-end CIKs in panel
  order, the latest-filed companyfacts value equals the frame value within 1 USD for A1, `ContractWithCustomerLiabilityCurrent`, R2 and
  NetIncomeLoss at CY2019Q4I/CY2019 (pre-window years only).
- **R1-22 Coverage of earnings (Sonnet item 13; accepted).** `headline.csv` and the README report the primary sample's Σ NI_2025 over the
  500 CIKs' Σ NI_2025 (financials included), so "these firms" has a stated weight.
- **R1-23 S2's reference year (Sonnet item 14; resolved by R1-1).** T = AA_2026 − AA_2025 includes the reference year's own excess accrual.
- **R1-24 Words (Sonnet's Words section; accepted).** "Abnormal accrual" becomes **excess accrual** (glossed: the part of a year's change
  in the net contract position beyond what growth at the previous year's ratio would give). The README avoids "causes" ("ordinary
  explanations") and "cash flow from" ("operating cash flow"). EXTRA_RX adds `overstat\w*`, `pulled\s+forward`, `flatter\w*`,
  `prematur\w*`, `window[- ]dressing`, `red\s+flags?`, `fictitious`, `smooth(?:ed|ing)\b`, `abnormal\w*`. A named contributor list carries
  its flags and the sentence that a large contributor is not a finding about that firm.
- **R1-25 Guards that pass on a broken build (Sonnet; accepted).** Two-sided fixtures: G6 at 0.0199, 0.0201, 9.9996, 10.0000, 10.0001,
  25.0000, 25.0001; G8 at 2026-11-29, 2026-11-30, 2027-02-15, 2027-02-16; G3 at 349, 350, 380 and 381 days; G1 with a value above 2^53 and
  a fractional value; G15 at 0.9 s; G10 and G12 cross-checked against M27's literal copies.
- **R1-26 Registration (CLAUDE.md, "four places"; Sonnet's open point).** Landing adds the CALENDAR rows (S2, 2027-05-03) and a
  `RESEARCH_STATE.md` §5 row for S2 naming the goal row it serves; no findings document is written, so no read-table row.
- **Overruled or deferred:** Grok's "days scale instead of shares" (R1-5); Grok's "cash-flow changes as the primary acquisition check"
  (coverage too thin: 100 of the 500 tag `IncreaseDecreaseInContractWithCustomerLiability` at CY2025; descriptive only, R1-7).

## Supervisor rulings, round 2 (open questions after the rewrite), 28 Oct 2026 — before any build

The supervisor re-derived the three canonical hashes from this file (4.6 `6d113eb3…`, 4.7 `6a68f3d8…`, 5 `99e8e8f9…`): all match. No
ruling below changes a hashed block.
- **R2-1 (O-11).** FY2020 counts only as an endpoint, as the NB block says. The README notes that the FY2021→FY2022 window uses FY2020
  balances as the prior-year input to its FY2021 excess accrual.
- **R2-2 (O-12).** Medians are over all windows of that length, FY2020 endpoints included (two one-year windows; one two-year window). The
  README says the band rests on three windows and is thin.
- **R2-3 (O-13).** `zero` is accepted as a direction value.
- **R2-4 (O-14).** The placeholder stands (P13).
- **R2-5 (O-15).** The placeholder stands: acquisitions over FY2023-FY2025 against FY2023 revenue, the years whose balances enter T.
- **R2-6 (O-16).** C14 runs in the **pre stage**, on the first 15 December year-end CIKs in panel order that are in scope for the two-year
  placebo window, at CY2019Q4I/CY2019, so the extraction is checked before any FY2023-or-later value is read. Section 8's C14 text is read
  this way.
- **R2-7 (O-17).** `sens_r2only` drops `rev_fallback` firms only, as P9 says. R3 is ASC 606 revenue including assessed taxes; Grok's
  objection was to `Revenues`, which carries non-ASC 606 income.
- **R2-8 (O-18).** `population_sha256` in `registered.csv` is accepted (it is already in the allowlist hash).
- **R2-9 (the name in R1-17).** Accepted: public files say "the principal".
- **R2-10 (the author's additions).** `\bmaterial\w*` in the wording ban, the 2027-08-02 CALENDAR row, and the banned output words are
  accepted.
