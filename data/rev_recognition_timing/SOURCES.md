# Sources, requests and builder decisions: revenue-recognition timing in the net-income growth of the W3 firm set

The specification is `_research/2026-10-28-Revenue-Recognition-Timing-Spec.md`, committed at 2cd528f (with the supervisor's rulings of rounds 1 and 2) before the first request. Every number comes from data.sec.gov (R10).

## Requests

**By the spec author, 28 Oct 2026** (57 requests, all GET to data.sec.gov, sequential, at least 1.0 s apart, 14,747,233 bytes; 54 x 200 and 3 x 404; no redirect followed, no retry, no 403 or 429). They used the neutral User-Agent of CLAUDE.md's working rules, with no address. The supervisor's 8 coverage requests of the same day used it too (their list is not in the specification).

| # | UTC (28 Oct) | Path | Status | Bytes | sha256, first 12 |
|---|---|---|---|---|---|
| 1 | 06:21:31 | `/api/xbrl/frames/us-gaap/ContractWithCustomerLiability/USD/CY2019Q4I.json` | 200 | 170,706 | `6ae9cd741778` |
| 2 | 06:21:33 | `/api/xbrl/frames/us-gaap/ContractWithCustomerLiabilityCurrent/USD/CY2019Q4I.json` | 200 | 228,064 | `989bcca3c607` |
| 3 | 06:21:34 | `/api/xbrl/frames/us-gaap/ContractWithCustomerLiabilityNoncurrent/USD/CY2019Q4I.json` | 200 | 105,398 | `24a9375a313f` |
| 4 | 06:21:35 | `/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNet/USD/CY2019Q4I.json` | 200 | 79,080 | `08b9525c0817` |
| 5 | 06:21:37 | `/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNetCurrent/USD/CY2019Q4I.json` | 200 | 69,195 | `344a307d46bf` |
| 6 | 06:21:38 | `/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNetNoncurrent/USD/CY2019Q4I.json` | 200 | 23,553 | `dbc2bc7dfcd5` |
| 7 | 06:21:40 | `/api/xbrl/frames/us-gaap/Revenues/USD/CY2019.json` | 200 | 435,064 | `112eb1b4349f` |
| 8 | 06:21:41 | `/api/xbrl/frames/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/USD/CY2019.json` | 200 | 467,424 | `bb44dd228eb4` |
| 9 | 06:21:42 | `/api/xbrl/frames/us-gaap/NetIncomeLoss/USD/CY2019.json` | 200 | 946,165 | `f15e595eca6b` |
| 10 | 06:21:44 | `/api/xbrl/frames/us-gaap/ContractWithCustomerLiabilityCurrent/USD/CY2019Q2I.json` | 200 | 174,582 | `67fb471fe612` |
| 11 | 06:21:45 | `/api/xbrl/frames/us-gaap/ContractWithCustomerLiabilityCurrent/USD/CY2019Q3I.json` | 200 | 178,358 | `9c1d503fdd5d` |
| 12 | 06:21:47 | `/submissions/CIK0000789019.json` | 200 | 185,671 | `6acb47292f97` |
| 13 | 06:21:48 | `/api/xbrl/companyfacts/CIK0000723531.json` | 200 | 3,497,237 | `c14cf3666260` |
| 14 | 06:22:25 | `/api/xbrl/frames/us-gaap/ContractWithCustomerLiability/USD/CY2023Q4I.json` | 200 | 177,860 | `9e4576f5040c` |
| 15 | 06:22:26 | `/api/xbrl/frames/us-gaap/ContractWithCustomerLiabilityCurrent/USD/CY2023Q4I.json` | 200 | 267,855 | `49d6c222fea4` |
| 16 | 06:22:28 | `/api/xbrl/frames/us-gaap/ContractWithCustomerLiabilityNoncurrent/USD/CY2023Q4I.json` | 200 | 110,695 | `663928642186` |
| 17 | 06:22:29 | `/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNet/USD/CY2023Q4I.json` | 200 | 79,430 | `eb0d0814f431` |
| 18 | 06:22:31 | `/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNetCurrent/USD/CY2023Q4I.json` | 200 | 74,624 | `db9080afdf8b` |
| 19 | 06:22:32 | `/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNetNoncurrent/USD/CY2023Q4I.json` | 200 | 23,638 | `5e73d816e127` |
| 20 | 06:22:33 | `/api/xbrl/frames/us-gaap/AccountsReceivableNetCurrent/USD/CY2023Q4I.json` | 200 | 442,699 | `85bc970e0e18` |
| 21 | 06:22:35 | `/api/xbrl/frames/us-gaap/ReceivablesNetCurrent/USD/CY2023Q4I.json` | 200 | 60,780 | `4358c0aa9a8b` |
| 22 | 06:22:36 | `/api/xbrl/frames/us-gaap/AccountsNotesAndLoansReceivableNetCurrent/USD/CY2023Q4I.json` | 200 | 14,350 | `904d3f03bc6b` |
| 23 | 06:22:38 | `/api/xbrl/frames/us-gaap/ContractWithCustomerReceivableAfterAllowanceForCreditLossCurrent/USD/CY2023Q4I.json` | 200 | 4,824 | `384bd988bcf5` |
| 24 | 06:22:39 | `/api/xbrl/frames/us-gaap/DeferredRevenueCurrent/USD/CY2023Q4I.json` | 200 | 80,634 | `60472c932ba4` |
| 25 | 06:22:40 | `/api/xbrl/frames/us-gaap/RevenueRemainingPerformanceObligation/USD/CY2023Q4I.json` | 200 | 104,247 | `8d373307e21c` |
| 26 | 06:22:42 | `/api/xbrl/frames/us-gaap/AccountsReceivableNetNoncurrent/USD/CY2023Q4I.json` | 200 | 11,509 | `73110e8df10d` |
| 27 | 06:22:43 | `/api/xbrl/frames/us-gaap/UnbilledContractsReceivable/USD/CY2023Q4I.json` | 200 | 20,815 | `5a6f0f729260` |
| 28 | 06:22:44 | `/api/xbrl/frames/us-gaap/ContractWithCustomerLiability/USD/CY2025Q4I.json` | 200 | 155,939 | `4916481b82d4` |
| 29 | 06:22:46 | `/api/xbrl/frames/us-gaap/ContractWithCustomerLiabilityCurrent/USD/CY2025Q4I.json` | 200 | 247,125 | `8cb8c0d85191` |
| 30 | 06:22:47 | `/api/xbrl/frames/us-gaap/ContractWithCustomerLiabilityNoncurrent/USD/CY2025Q4I.json` | 200 | 102,336 | `77466be9a3b9` |
| 31 | 06:22:49 | `/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNet/USD/CY2025Q4I.json` | 200 | 68,029 | `b7cf577ed3bc` |
| 32 | 06:22:50 | `/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNetCurrent/USD/CY2025Q4I.json` | 200 | 72,161 | `85db54cf43b6` |
| 33 | 06:22:52 | `/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNetNoncurrent/USD/CY2025Q4I.json` | 200 | 21,703 | `5ca0a1f9ad65` |
| 34 | 06:22:53 | `/api/xbrl/frames/us-gaap/AccountsReceivableNetCurrent/USD/CY2025Q4I.json` | 200 | 407,016 | `ec500eddb769` |
| 35 | 06:22:54 | `/api/xbrl/frames/us-gaap/ReceivablesNetCurrent/USD/CY2025Q4I.json` | 200 | 49,720 | `c255dafc343b` |
| 36 | 06:22:55 | `/api/xbrl/frames/us-gaap/DeferredRevenueCurrent/USD/CY2025Q4I.json` | 200 | 63,046 | `4f1eefc2c4ee` |
| 37 | 06:22:57 | `/api/xbrl/frames/us-gaap/RevenueRemainingPerformanceObligation/USD/CY2025Q4I.json` | 200 | 97,460 | `82ae0957285e` |
| 38 | 06:22:58 | `/api/xbrl/frames/us-gaap/ContractWithCustomerLiability/USD/CY2026Q2I.json` | 200 | 125,018 | `b5c0105dd845` |
| 39 | 06:23:00 | `/api/xbrl/frames/us-gaap/ContractWithCustomerLiabilityCurrent/USD/CY2026Q2I.json` | 200 | 204,482 | `679f55bb2777` |
| 40 | 06:23:01 | `/api/xbrl/frames/us-gaap/ContractWithCustomerAssetNetCurrent/USD/CY2026Q2I.json` | 200 | 60,650 | `25be4564636f` |
| 41 | 06:23:02 | `/api/xbrl/frames/us-gaap/AccountsReceivableNetCurrent/USD/CY2026Q2I.json` | 200 | 344,333 | `31327d7f1981` |
| 42 | 06:23:04 | `/api/xbrl/frames/us-gaap/RevenueRemainingPerformanceObligation/USD/CY2026Q2I.json` | 200 | 87,872 | `d17b561817e2` |
| 43 | 06:23:17 | `/api/xbrl/frames/us-gaap/Revenues/USD/CY2023.json` | 200 | 409,960 | `fc7cf4e32d91` |
| 44 | 06:23:18 | `/api/xbrl/frames/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/USD/CY2023.json` | 200 | 480,689 | `13d3dd083fe1` |
| 45 | 06:23:20 | `/api/xbrl/frames/us-gaap/RevenueFromContractWithCustomerIncludingAssessedTax/USD/CY2023.json` | 200 | 119,965 | `81187c80bc89` |
| 46 | 06:23:21 | `/api/xbrl/frames/us-gaap/NetIncomeLoss/USD/CY2023.json` | 200 | 974,484 | `250bd2dd6e12` |
| 47 | 06:23:22 | `/api/xbrl/frames/us-gaap/Revenues/USD/CY2025.json` | 200 | 345,804 | `ed2f734d3f98` |
| 48 | 06:23:24 | `/api/xbrl/frames/us-gaap/RevenueFromContractWithCustomerExcludingAssessedTax/USD/CY2025.json` | 200 | 414,741 | `a400a02d09ca` |
| 49 | 06:23:25 | `/api/xbrl/frames/us-gaap/RevenueFromContractWithCustomerIncludingAssessedTax/USD/CY2025.json` | 200 | 101,372 | `356cb1414f8d` |
| 50 | 06:23:26 | `/api/xbrl/frames/us-gaap/NetIncomeLoss/USD/CY2025.json` | 200 | 869,214 | `e6434be0c524` |
| 51 | 06:23:28 | `/api/xbrl/frames/us-gaap/IncreaseDecreaseInAccountsReceivable/USD/CY2025.json` | 200 | 472,718 | `9409e31becf3` |
| 52 | 06:23:29 | `/api/xbrl/frames/us-gaap/IncreaseDecreaseInContractWithCustomerLiability/USD/CY2025.json` | 200 | 204,315 | `213ccd678323` |
| 53 | 06:23:31 | `/api/xbrl/frames/us-gaap/PaymentsToAcquireBusinessesNetOfCashAcquired/USD/CY2025.json` | 200 | 198,735 | `59ba5d240c0d` |
| 54 | 06:25:30 | `/api/xbrl/frames/us-gaap/AccountsReceivableAfterAllowanceForCreditLossCurrent/USD/CY2023Q4I.json` | 404 | 366 | `eb09525baa3d` |
| 55 | 06:25:32 | `/api/xbrl/frames/us-gaap/AccountsReceivableAfterAllowanceForCreditLossCurrent/USD/CY2025Q4I.json` | 404 | 386 | `c03b5fb89acd` |
| 56 | 06:25:33 | `/api/xbrl/frames/us-gaap/AccountsReceivableAfterAllowanceForCreditLossCurrent/USD/CY2026Q2I.json` | 404 | 366 | `cae5a74c1ed8` |
| 57 | 06:26:01 | `/api/xbrl/frames/us-gaap/AccountsNotesAndLoansReceivableNetCurrent/USD/CY2025Q4I.json` | 200 | 12,771 | `8ff0403f2815` |

**By this build** (the fetch modes; the supervisor runs them with the contact string in SEC_UA, which no file holds; every request is a row of fetch_log.csv and every kept body a row of vintages.csv):

| Kind | Status | Requests |
|---|---|---|
| companyfacts | 200 | 500 |
| frames | 200 | 66 |
| submissions | 200 | 781 |

## Rules applied

- **Fiscal year Y** is the report date of the firm's original form 10-K with a report date from Y-04-01 to (Y+1)-03-31 (a 10-K/A or 10-KT never defines it); none is `year_gap`, two or more `fy_ambiguous`. The `fy` and `fp` labels are never used.
- **Facts**: USD only; an instant has end equal to D_Y, a duration has end equal to D_Y and 350 to 380 days. Primary basis `own_10k`: the fact whose accn is that year's 10-K; sensitivity `sens_latest`: the latest-filed fact, ties to the largest accn. Facts within 7 days of D_Y are a diagnostic (`near_end`); a needed value with a near fact but no exact one makes the firm `end_mismatch`.
- **Tags** (2.4): CA, CL (total, else current plus noncurrent, else DeferredRevenue), revenue R2, R3, Revenues, NetIncomeLoss; receivables, contract costs, remaining performance obligations, unbilled receivables and the cash-flow change tags are descriptive.
- **Evidence behind the total rule**, observed on fiscal 2019 by the spec author (per-firm comparisons within 0.5%, no sums): liabilities at CY2019Q4I, all three tags 59 (total = current + noncurrent in 45, = current in 1, neither in 13); total and current without noncurrent 36 (equal 14, total larger 13, total smaller 9); total only 81; current only 51; current and noncurrent 49. Contract assets: all three 9 (total = parts in 8); total and current 7 (equal 3, larger 3, smaller 1); total only 61; current only 28; current and noncurrent 13. Revenue at CY2019: 104 firms tag both Revenues and R2 (equal 49, Revenues larger 50, smaller 5).

## What the spec author looked at before any build (the blind rule, 2.7)

Fiscal-2019 identity comparisons and end-date offsets; for the 2023-2026 frames only counts (how many of the 500 appear, end months, durations, set intersections), no value of any firm; one submissions file (filing metadata) and one companyfacts file (structure and filing dates of facts ending in 2018 and 2019). No T, EA, r or share, and no sum, average or ratio of any fiscal 2023-2026 value, was computed.

## Builder decisions

Where the specification is ambiguous the stricter reading about leaks, blindness and causal wording was taken. None of these changes a rule, a threshold, a window, a registered text, a label or a hashed block.

1. **Canonical texts rebuilt from constants.** 4.6 and 4.7 are built in the script from the numbers the code itself uses (thresholds, floor, dates, tag names), so editing one changes its sha256 and the build refuses to write registered.csv; the allowlist of 5 is pasted. The three hashes are the ones the supervisor gave. They are checked at every build (C11) and by the selftest (G10, G12).

2. **Aggregates are sums of the written whole-dollar cells.** R8 rounds each USD cell to whole dollars at write time, but C07 and success criterion 6 ask the sum of contributions.csv to equal T, T_pos and the change in net income within 1 USD, and independent rounding would leave several dollars of gap over several hundred firms. Each firm's cells are therefore rounded half-even once, when its record is made, and every aggregate (T, T_pos, T_neg, the change in net income, the net income and revenue sums, and so every share and label) is computed from those cells on unrounded Decimals. The difference from summing unrounded values is under half a dollar a firm. Rounding to the printed decimals still happens only at write time.

3. **Entity names in title case; the README names contributors by ticker.** SEC registrant names are upper case, and a name such as Vulcan Materials Co would carry the banned verdict token for materiality (success criterion 4 greps case-sensitively, and the wording ban catches the word in the README). entity_name is therefore written in title case, the README lists contributors by ticker, and the names stay in contributors.csv and firms.csv. Names are read from the cached submissions files at build time, because no extract column holds them.

4. **README sentence 2 is the denial sentence.** Section 0 makes the denial sentence the second README sentence; section 5 lists the results before it. The first sentence carries what was measured and the S1 and S1P results, the second is the denial sentence verbatim, and a paragraph with the thresholds follows. The README lists contributors by ticker, not by name.

5. **Extraction runs inside the fetch modes.** cf_extract.csv needs each firm's D_Y to pick the facts within 7 days of it, so fetch-companyfacts refuses to start (exit 5) until fetch-submissions has written submissions_extract.csv. A fetch mode writes its extract, from all cached bodies and sorted, once every planned body is cached or recorded as 404; a run that stops short prints what is missing and writes no extract. Firms whose submissions file is 404 get no companyfacts request (they are no_sec_record).

6. **Fetch mechanics.** --vintage is required and must be today's UTC date or an existing vintage folder, so the 2027-05-01 gate cannot be opened by naming a future vintage. Exit codes: 0 done, 2 STOP or no contact string or a data error, 3 network fault, 4 a run ended by its cap or by --max-requests with work left, 5 refused. The 1.0 s gap is measured from the end of the previous reply to the next request, timestamps in fetch_log.csv carry milliseconds, and a network fault is logged with status 0. A 404 recorded in vintages.csv is final for the vintage and is not requested again. A body in raw/ that does not match its vintages.csv row stops the run (exit 5) and is never fetched over. A 404 on an older submissions page, a reply for another CIK and a 200 that is valid JSON but not the document asked for latch STOP like the other content failures. The STOP file's body_head has the contact string replaced if a reply echoes it.

7. **Frames plan.** 13 balance-sheet tags at CY2019Q4I, CY2023Q4I and CY2025Q4I and 9 duration tags at CY2019, CY2023 and CY2025 (22 tags, 66 requests), plus CY2026Q4I and CY2026 from 2027-05-01 on (22 more). Any 2026 period is held back before that date, which is stricter than the specification's CY2026Q2I and later. The probe-only tags of 2.5 (AccountsReceivableNetNoncurrent, ContractWithCustomerReceivableAfterAllowanceForCreditLossCurrent, AccountsReceivableAfterAllowanceForCreditLossCurrent) are not fetched.

8. **What cf_extract holds.** Every USD fact of the tags of 2.4 whose end is within 7 days of a needed D_Y (2019 to 2025, and 2026 from 2027-05-01), with filed, form and accn. Before the S2 date nothing after D_2025 (or after 2026-03-31 where there is no D_2025) is extracted, so FY2025's near-end diagnostic sees only facts up to D_2025 and not the 7 days after it: the hashed P5 reads plus or minus 7 days while R1-10 forbids later facts, and the stricter blind reading was taken. The file may be large (tens of megabytes); it is committed whole.

9. **The pre stage.** build --stage pre reads only submissions rows reported up to 2023-03-31, only facts ending up to each firm's D_2022 plus 7 days (decided on the end date before any value is converted) and only the CY2019 frames. Besides placebo.csv (windows, NB1 and NB2, from which the medians follow) and coverage.csv (CY2019 periods only; n_cik_in_scope counts the fy2020_fy2022 scope), it writes the files that let the placebo be checked: firms.csv (status for the window fy2020_fy2022), firm_years.csv (FY2019-FY2022), firm_tags.csv, panel.csv and contributions.csv for the three placebo windows, and checks.csv (C01, C03, C04 and C06 to C14; C02 and C05 need later frames or filings and run in the full stage). The full stage rewrites these files whole and rewrites placebo.csv only if its bytes would change, so the stage-order test of criterion 9 can hold. A pre build is refused for a vintage whose S1 is already scored. The cash-flow sign convention is also set in this stage's data (fiscal 2019-2022) and written by the full stage.

10. **Vintages and what accumulates.** headline.csv, registered.csv, vintages.csv and fetch_log.csv accumulate over vintages (their keys carry the vintage); revisions.csv is regenerated from headline.csv on every build and lists the statistics that differ between adjacent vintages. The other files describe the last vintage built. S1 and S1P are written on the first full vintage and kept verbatim by later ones; placebo.csv is the band frozen on that vintage. S2 and S2P get a row per vintage until one is scored (VOID included) and are then kept verbatim.

11. **Required inputs and gaps.** R1-15 and P11 are read literally: N, revenue and net income must be stated at every needed year, FY2022 to FY2025 for S1, even though the change in net income uses only FY2023 and FY2025. A contract-balance family with a tag at some needed years only, and no complete set of parts, is a gap (gap_n); a Noncurrent tag alone, stated at every year, counts as parts. Two different values for one context in one filing are treated as missing, not resolved, and counted in the build's console output.

12. **Near-end facts.** Near facts (end 1 to 7 days from D_Y) are looked for in the year's own 10-K only. A firm is end_mismatch when, at some needed year, no tag of revenue, net income, contract assets or contract liabilities (DeferredRevenue included) has an exact fact and one of them has a near fact. near_end is set when any such near fact exists.

13. **Structure details.** total_gt_parts is set when the total is used and exceeds the parts tagged at some year. sens_parts uses the parts wherever they are tagged at every year. DeferredRevenueNoncurrent is extracted with DeferredRevenueCurrent for the fallback. A firm with no contract tag at any needed year has N = 0 (structure absent_everywhere) and stays in scope.

14. **Sensitivity samples.** Every sensitivity except sens_gap0 starts from the primary firm set: sens_acq, sens_disc, sens_trim, sens_r2only and sens_leave1 drop firms; sens_parts, sens_unbilled and sens_latest change values (sens_latest keeps the primary firms and their tags, with latest-filed values); sens_gap0 adds the firms whose only gap is gap_n, the missing side set to 0, with the revenue floor applied. acq2 sums PaymentsToAcquireBusinessesNetOfCashAcquired over FY2023-FY2025 against FY2023 revenue (R2-5); a firm that does not tag it is not flagged. s2_subset is the primary firms in the S2 set: before 2027-05-01 those whose fiscalYearEnd falls in 1130-1231 or 0101-0215 and that are in scope on FY2024-FY2025, afterwards the firms S2 actually scores.

15. **VOID and PENDING rows.** A VOID row writes no share but keeps T, the change in net income, direction and qualifier, which do not depend on the sign of that change. PENDING and PENDING_THIN rows write no number except n_firms for PENDING_THIN (the firms eligible at fiscal 2025), with qualifier none and no direction; the coverage count is in headline.csv.

16. **Placebo and statistics details.** Medians are over all windows of each length (R2-2). NB1 and NB2 are ratios of |T| to end-year revenue, written as percents. placebo.csv's share_pct is blank where the VOID conditions hold. The ticker column of contributions.csv carries the joined tickers (GOOGL|GOOG). Contributors tie-break on the CIK. The window and sample enumerations of section 5 are the only ones written.

17. **Checks.** C02 is evaluated on the first vintage only and is INFO afterwards. C03 compares exact counts (a warning on any difference). C07 reads the written cells. C13 needs the raw cache (--raw overrides its place) and fails if it is absent. A population drift (C01 FAIL) stops the build before anything is written. C14 compares only pairs that exist in both sources.

18. **What the selftest reads.** R7 lets the script read the panel and its own folders only. The selftest also reads bin/check.sh (read-only) and nothing else outside them, because R1-25 asks G10 and G12 to be cross-checked against M27's literal copies of the 4.6 hash and the eighteen header lines. It builds its synthetic world in a temporary folder, makes no request and never reads SEC_UA from the environment.

19. **Guard M27.** In bin/check.sh, warn-only, appended after M26 and called after it in --all. It holds its own copy of the eighteen header lines and of the 4.6 hash, treats a folder with no README.md as the pre stage (missing names are then a warning), and prints one line per problem.

20. **Supervisor ruling S2-R1 (28 Oct 2026): S2 coverage and a fiscal year-end mismatch.** Dated 28 Oct 2026, from the supervisor, after the first full build of vintage 20261028. (a) The denominator of the 70% test is unchanged: the firms eligible by the FY2025 rule (a fiscalYearEnd in 1130-1231 or 0101-0215 in the submissions file, and in scope on FY2024-FY2025). (b) The numerator, n_with_fy2026_10k, counts a firm only when its FY2026 original 10-K's period end lies inside [2026-11-30, 2027-02-15]; a firm with two or more original 10-Ks in the FY2026 window is not counted either (it is fy_ambiguous). (c) A firm in the denominator whose FY2026 10-K ends outside the window is never counted and, at scoring, is excluded from S2 and S2P with the status end_mismatch. The first case is a firm whose submissions file says fiscalYearEnd 1231 while its FY2026 10-K ends on 2026-06-30 and was filed on 2026-08-14 (the data do not show that the year-end changed; no 10-KT has been filed). The status is stated in headline.csv (n_s2_end_mismatch, n_s2_fy_ambiguous and n_s2_no_fy2026_10k beside n_eligible_fy2025 and n_with_fy2026_10k; the four counts add up to the denominator), in the README's S2 section and in its table of S2 statuses. An existing status was used because a new one would have to be added to P12 in the hashed 4.7 block, which this ruling leaves alone; end_mismatch is read here as the period end not matching the S2 window, which is wider than P5's 7-day rule for facts. A dedicated status would also need the allowed-status lists of section 5 and of the script changed; the M27 guard checks no status value and would not change. No rule, threshold, label or hashed block changes, and S1 and S1P are not re-scored.

21. **Supervisor ruling R3-1 (28 Oct 2026): the same-filing sensitivity, added after the result was seen.** An independent check on 28 Oct 2026 recomputed r_(t-1) from the year-t original 10-K's own comparative column (N and revenue of year t-1 as reported in the same accession as year t) instead of the first-reported figures of year t-1, and the ruling adds it as the sample sens_samefiling. It was added after the primary result was seen, by that check, and is not part of the rule set fixed in advance; the README's sensitivity table says so. The build computes it offline from the vintage's cf_extract.csv, which already holds every fact that ends within 7 days of a fiscal year-end whatever filing carries it (so the comparative columns of later 10-Ks are in it). N_t, revenue_t and the change in net income are the primary's; only r_(t-1) in the base-year and end-year excess accruals changes. The tags are those of the firm's primary structure for each of contract assets, contract liabilities and revenue. Where the year-t 10-K does not state every one of them for year t-1, r_(t-1) falls back to the first-reported value for that year; headline.csv states how many firms do that (n_samefiling_fallback). It also states how many firms' comparatives were restated, meaning any tag's comparative differs from the first-reported value (n_samefiling_restated). On vintage 20261028 the build gives T 23,698,570,553 USD, S1 9.992% and S1P 24.510%, the verifier's figures to the dollar; GE's T_i moves by -2,606,864,195.68 USD exactly (-2,606,864,196 between the two whole-dollar cells; the verifier's -2,606,864,195 is within 1 USD). The fallback count here is 6 firms (11 firm-years); the verifier's 20 equals the build's count of restated firms, so the verifier's wording 'on the fallback' is read as 'restated'. The primary sample, S1 and S1P are not changed and registered.csv is not touched.

22. **Supervisor ruling R3-2 (28 Oct 2026): fragility counts.** Descriptive, not a new registered statement. For every firm in the primary sample the build removes it alone, rescores S1 and S1P on the other firms (same VOID rule, same thresholds, S1 against NB2 as ever) and counts the firms whose removal takes S1 below 10% and S1P below 25%; a count is zero when the full sample is already below the threshold. headline.csv holds n_leave1_s1_below_10, n_leave1_s1p_below_25 and, for each firm that takes S1 below 10%, leave1_s1_share_pct_<ticker>; the README names those firms. On vintage 20261028: 4 firms for S1 (BA 4.309%, DELL 8.197%, GE 8.761%, GD 9.732%) and 17 for S1P, as the verifier found. A removal that leaves S1P exactly at 25% would count as below; none does.

23. **Supervisor ruling R3-3 (28 Oct 2026): the README opening.** The ruling overrides the specification's wording of item (1), 'came from revenue booked ahead of or behind billing', which reads as attribution. The opening now states, in this order, that the share is a ceiling for the tagged balances under assumption A1 and not an estimate ('at most'); the S1 and S1P figures with their labels; and, after the denial sentence, one sentence on fragility (the firms whose removal takes S1 below 10%, how many of the 13 samples give a different label, and the same-filing figure). The denial sentence stays verbatim and is still the second sentence of the opening paragraph, as section 0 of the specification requires, so it sits between the figures and the fragility sentence. The direction ('T is above zero, so the timing added to reported growth') appears only later, after the ceiling. A short provenance paragraph follows; its sentence on the independent check appears only for the vintage it describes (20261028).

24. **Supervisor ruling R3-4 (28 Oct 2026): the README for a cold reader.** Fixes made after a reader who knows accounting read the README cold: the 500 firms are described (S&P 500 registrants as workstream W3 holds them); CIK, T, T_i, the labels, S1 and S1P, the base year (fiscal 2023), vintage and the placebo windows are defined at first use; the thresholds are said to have been fixed in advance by the project; the assumptions keep the names A1 and A3 and the text says why there is no A2; the receivables tag is called by its name instead of A1; company facts, dimensioned balances and extensions are explained; the one-line argument for 'at least as large as the effect' is given; every flag and every status is defined, with the reason year_gap firms are dropped; the megacap firms are named; NB1 and NB2 are expanded; N in days, costs in days and receivable days are defined; the cash-flow cross-check says why its figure differs from the headline; fiscalYearEnd and PENDING_THIN are explained; and the earnings weight states its denominator (455 of the 500 CIKs on vintage 20261028: 45 state no fiscal 2025 NetIncomeLoss fact, 10 of them financial firms and 35 not). Only the denominator counts are new numbers (headline.csv: ni_2025_missing_financial and ni_2025_missing_other).

25. **Supervisor ruling R3-5 (28 Oct 2026): wording for a firm whose year-end does not match.** The data do not show a completed change of fiscal year-end for the end_mismatch firm: the submissions file says fiscalYearEnd 1231, the firm's latest original 10-K covers the year to 30 June 2026, and no 10-KT (transition report) has been filed. The README says exactly that, built from the data for each such firm (the fiscalYearEnd read, the period end of the latest original 10-K, and whether a 10-KT is on file), and does not say that the year-end changed.

26. **Cash-flow sign convention, measured (R1-7).** Set on fiscal 2019-2022 for firms without acquisitions, as the sign that matches the balance-sheet change in most firm-years: contract assets 1 (8 firm-years agree, 3 oppose), contract liabilities 1 (64, 4), trade receivables 1 (167, 27). A sign of +1 means the tag is positive when the balance rises.

### Fixes after the first run (R9)

None yet. A post-registration fix is listed here with its old and new value.
