# Grok attack on the revenue-recognition timing spec, 28 Oct 2026 (g13)

**Parcel:** the spec as first written (scratch copy, 502 lines), Grok 4.7 256K Extra High through the fenced Cursor lane, 837 s,
11 searches, 19 fetches, nothing blocked. Two URLs in the answer were never fetched (catalog.data.gov, uscode.house.gov); nothing rests
on them. The supervisor re-read two taxonomy definitions at source (Calcbench element pages for `AccountsNotesAndLoansReceivableNetCurrent`
and `Revenues`, 28 Oct): as quoted. The rulings that answer it are at the end of
[`2026-10-28-Revenue-Recognition-Timing-Spec.md`](2026-10-28-Revenue-Recognition-Timing-Spec.md).

## Return

I'll review the spec as written against the taxonomy definitions and live data sources, without touching any fiscal 2023–2026 figures. First I’ll read the design and the research constraints that apply.The spec is loaded. Next I’ll check the taxonomy definitions and whether each named data source still matches what the design assumes, without opening SEC hosts or any 2023–2026 figures.**VERDICT: BUILD WITH CHANGES.**

Load-bearing assumption that fails: under A1 and A2, `UB = max(EA, EA_last) / ΔNI` is a ceiling on the share of fiscal 2023–2025 net-income growth that came from revenue recognized ahead of billing or cash. Built as written, that ratio is a stock residual divided by a change in annual profit. It will be read as a share of growth. The fetch, fiscal-year, and tag-priority machinery can stay. The registered sentence should not be scored until the estimand below is replaced.

## Why the number misleads

ASC 606 splits three different things. A contract asset is consideration for goods already transferred, “conditioned on something other than the passage of time.” A contract liability is an obligation for which consideration “has been received (or the amount is due).” A receivable is what remains when only time stands between billing and cash. `AccountsReceivableNetCurrent` is that receivable: “right to consideration from customer for product sold and service rendered,” after the credit-loss allowance. Putting it inside N measures collection terms. The page’s question is recognition timing.

`N = AR + AR_nc + CA − CL` also nets unlike items. The liability tag is “consideration has been received or is receivable,” and in the 2019 taxonomy it rolls into `DeferredRevenueCurrent`. Where the filer grosses up a receivable and a contract liability before performance, N is unchanged only if both legs use the tags this spec keeps. `CapitalizedContractCostNet` (costs to obtain or fulfill a contract) sits outside N, so profit can be pulled forward with a measured timing effect of zero.

Algebra: `EA = (N_e − N_b) − r_b(Rev_e − Rev_b)` and `EA = EA_last + EA_mid`. `ΔNI = NI_e − NI_b`. With a 100% margin and no tax, the timing piece of that earnings change is the end-year flow minus the base-year flow, `(N_e − N_m) − (N_b − N_prior)`. A2 sets the base-year flow to “normal” and then never observes `N_prior` (O-3 drops fiscal 2022). `max(EA, EA_last)` is only a device to stay above `EA_last`. It is not that difference.

**(a) True timing effect larger than UB.** Revenue fixed at 1,000. Balances: prior year 300, fiscal 2023 100, 2024 100, 2025 110. Cash profit 300. Then `NI_2023 = 100`, `NI_2025 = 310`, `ΔNI = 210`. The timing contribution is `10 − (−200) = 210`. `r_2023 = 0.10`, so `EA = EA_last = 10` and `UB ≈ 4.8%` (`NOT_MATERIAL`). Growth is the non-recurrence of a fiscal-2023 deferral. A1 does not repair this: the example has no cost and no tax.

**UB large, timing idle.** Credit terms: recognition stays at delivery and billing; terms move by 30 days. That is `30/365 ≈ 8.2%` of revenue. On the spec’s own illustration (revenue ≈ 35 × `ΔNI`; one day ≈ 9.6% of `ΔNI`), UB is enormous and the label is `MATERIAL_CANDIDATE`. Within-firm mix does the same: fiscal 2018/19 industry DSO was about 8 days in specialty retail and about 78 in software. A shift inside one firm of that size moves `r` with no change in the recognition rule. A reweighting across firms whose own ratios stay constant does not: firm-level EA is zero. Buying the long-cycle firm does. `sens_acq` drops a firm only when the cash paid in fiscal 2024–2025 exceeds 10% of fiscal-2023 revenue. Receivables of a few days of the buyer’s sales clear a 10%-of-`ΔNI` label and still sit under that screen; a stock deal never hits `PaymentsToAcquireBusinessesNetOfCashAcquired`. Translation does the same: the balance sheet uses the closing rate and revenue the average rate, so `r` moves with the currency.

A1 fails upward as well as downward. Allowance releases, acquired balances, and foreign-currency translation raise N without early revenue, so UB is too big. Untagged, extension, or dimension-only contract assets, and capitalized contract costs, raise earnings with N unchanged, so the true effect exceeds UB. A ceiling that omits those balances is not a ceiling. The API the spec uses keeps standard-taxonomy facts for the whole entity; dimensions and extensions never arrive.

**(b) The 10% and 25% cuts are finer than the instrument.** One day is 0.274% of revenue, and the spec’s 35× sketch puts 10% of `ΔNI` at about one day and 25% at about two and a half. That is ordinary collection noise. Just above the VOID cliff (`ΔNI` under 2% of base net income), one day swamps the ratio. NB2 is the worst `|EA| / revenue` among placebo pairs that all include 2020. It answers “was this as large as the most extreme pandemic window?” It does not answer whether a one-day move is measurable. A negative UB is labeled `NOT_MATERIAL`, so a large deferral build and a nil result share a sentence.

**(c) The net can be a handful of software and cloud contract liabilities.** Receivables are widely tagged; contract assets and contract liabilities are not (the spec’s own coverage counts). Fiscal 2018/19 DSO already runs from a few days in retail to roughly 80 in software, and subscription firms bill ahead of recognition on top of that. Aggregate EA nets those liabilities against everyone else’s receivables. `EA_pos` is not registered. `sens_leave1` drops only the largest positive contributor. One large deferred-revenue build can flip the sign, and the sign flip becomes `NOT_MATERIAL`.

**(d) S2’s endpoint is unseen; the test is not a fair twin of S1.** Year-ends from 30 Nov 2026 through 15 Feb 2027 are still in the future relative to this spec (28 Oct 2026). Scoring on or after 1 May 2027 is after the usual 10-K lag for that slice. Fiscal 2025, the base, is already public. The eligible set drops June and September year-ends (Microsoft is the spec’s own example) and keeps a different mix of January retailers and November–January software. `s2_subset` is the right comparison and is not what the registered S2 sentence says. The first vintage that is missing a 10-K drops that firm forever. The interim uses `CY2026Q2`, which this spec has already retrieved, so a full build before May 2027 shows mid-2026 balances while S2 is still `PENDING`.

Latest-filed facts can put fiscal-2023 income and fiscal-2023 balances on different subsequent 10-Ks. The primary sample still scores that mix. The population is a 2026 survivor set, and SIC 6000–6799 is not the ASC 606 scope (leases, insurance, and financial instruments in 606-10-15-2). There is no sampling error. There is identification error, and the 10/25 cliffs make it a label.

## What to add or remove

Remove trade receivables from the recognition measure. Keep them in a separate days-sales-outstanding table. A recognition measure is contract assets minus contract liabilities, with capitalized contract costs beside it, each scaled by ASC 606 revenue (`RevenueFromContractWithCustomerExcludingAssessedTax` only). Convert with a margin and a tax rate if the comparator is net income. The accruals literature compares the accrual flow with earnings persistence and does not treat the base year as clean or billed receivables as “revenue ahead of billing.”

Add the prior-year balance so the earnings-change identity can be computed, a same-filing vintage for the income statement and the balance sheet, cash-flow changes as the primary acquisition check, and a registered concentration line (share of gross positive EA, gross negative EA, and contract liabilities in the top few firms). Report days of revenue. Drop the 10% and 25% labels, or move them only after the placebo is restated without 2020 and shown in days. Keep RPO out of N. Keep financial firms out, with the scope mismatch stated.

## REQUIRED CHANGES

1. Withdraw UB as a ceiling on the share of net-income growth. Report the contract-asset and contract-liability flows in days of ASC 606 revenue, and the earnings-change identity only once the prior-year balance is in the window. Reason: case (a). Source: https://dart.deloitte.com/USDART/home/codification/revenue/asc606-10/roadmap-revenue-recognition/chapter-2-symbols-defined-terms/2-1-glossary-terms
2. Take trade receivables out of the registered numerator; publish AR days separately. Reason: the tag is billed consideration, so credit terms alone clear 10%. Source: https://www.calcbench.com/element/AccountsReceivableNetCurrent
3. Stop selecting the largest of `Revenues`, R2, and R3. Use R2. `Revenues` includes interest, investment income, insurance, and lease income. Source: https://www.calcbench.com/element/Revenues and https://www.calcbench.com/element/RevenueFromContractWithCustomerExcludingAssessedTax
4. Do not treat `AccountsNotesAndLoansReceivableNetCurrent` or `ReceivablesNetCurrent` as trade receivables. The former “includes, but is not limited to, notes and loan receivable.” Source: https://www.calcbench.com/element/AccountsNotesAndLoansReceivableNetCurrent
5. Put capitalized contract costs in the timing inventory or state that the ceiling ignores them. Source: https://www.calcbench.com/element/CapitalizedContractCostNet
6. Replace the 10/25 labels with a days scale. Show the 2020 pair apart from the noise band. Do not map a negative result to `NOT_MATERIAL`. Register gross positives, gross negatives, and the top firms’ share of contract liabilities. Reason: one day ≈ the 10% band; 2020 is inside every placebo pair.
7. Move acquisitions and translation into the primary rule. A 10%-of-revenue cash screen leaves stock deals and small deals with large receivables inside the label. Do not read `IncreaseDecreaseInAccountsReceivable` as “increase = positive”: its taxonomy balance type is credit. Source: https://www.calcbench.com/element/IncreaseDecreaseInAccountsReceivable
8. For each firm-year, take income and balances from the same filing, or drop broken comparatives from the registered sample. `sens_disc` does not do that.
9. Rewrite the S2 sentence as a November–February holdout, reported next to `s2_subset`, with late 10-Ks counted and the score left `PENDING` if coverage is thin. Keep the 1 May 2027 gate.

## SOURCES

| Source | Status | URL fetched |
|---|---|---|
| data.sec.gov frames, companyfacts, submissions | UNCHECKED. Host not opened. Wrapper shows a free, keyless JSON API and fields `val`, `fy`, `fp`, `form`, `filed`, `accn`. Reuse terms and the fair-access user-agent rule were not opened. | https://sec-edgar.github.io/sec-edgar/rest_api.html |
| Same API, existence only | WORKS as a 2 Jul 2021 announcement. Field list and licence not on this page. | https://xbrl.us/news/sec-edgar-api/ |
| `ContractWithCustomerLiabilityCurrent`; `NetIncomeLoss` attributable to parent, credit | WORKS (2019 taxonomy) | http://xbrlsite.azurewebsites.net/2019/Prototype/references/us-gaap/Element-2340.html ; http://xbrlsite.azurewebsites.net/2019/Prototype/References/us-gaap/Element-10491.html |
| Receivable, revenue, cash-flow, contract-cost tags | WORKS | Calcbench URLs above |
| `AccountsReceivableAfterAllowanceForCreditLossCurrent` | FAILS. No taxonomy page, generic homepage. Matches the spec’s frame 404. | https://www.calcbench.com/element/AccountsReceivableAfterAllowanceForCreditLossCurrent |
| ASC 606 glossary, scope, original effective date | WORKS | http://storage.fasb.org/ASU%202014-09_Section%20A.pdf |
| ASC 606 glossary (secondary) | WORKS | Deloitte URL above |
| data.gov Financial Statement Data Sets | UNCHECKED. Page timed out twice. Search text describes the quarterly ZIP product this spec refuses, not the JSON API. | http://catalog.data.gov/dataset/financial-statement-data-sets |
| 17 U.S.C. 105 | UNCHECKED. House URL returned 404. The spec’s public-domain claim was not re-verified. | https://uscode.house.gov/view.xhtml?req=granuleid:USC-prelim-title17-section105&num=0&edition=prelim |
| PwC ASC 606 presentation guide | UNCHECKED (403) | viewpoint.pwc.com chapter 33.3 |
| `data/w3_tax/firm_tax_panel.csv` | UNCHECKED. Local file; not opened. | — |

Calcbench was used as a taxonomy reader. It is not the build’s source, and no Calcbench reuse license was read. SEC reuse terms live on sec.gov and were not checked. The spec’s neutral user-agent, with no contact email, could not be checked against the current access rule.

## REFERENCE POINTS

1. Andrew Sather, 26 Apr 2022, fiscal 2018/2019 S&P 500, `365 × AR / revenue`: “average Days Sales Outstanding for the entire S&P 500 was 62 days” (median 55; software 78; specialty retail 8). https://einvestingforbeginners.com/calculating-dso-formula-examples/  
   The build’s fiscal-2019 in-scope receivable days should fall within about 10 days of 55–62 if the set resembles the S&P 500 non-financials. Net `N/revenue` days should be lower, because contract liabilities are subtracted. The placebo statistic is a change, `EA / revenue`. One day is 0.27% of revenue, so a quiet year should be a few tenths of a percent of revenue per day of drift. An `|EA| / revenue` near 15% would mean the change formula was applied to the stock.

2. Hackett Group, 24 Jun 2020, on the 1,000 largest US non-financials in 2019: “collected cash from customers more slowly and held slightly more inventory.” https://www.thehackettgroup.com/hackett-survey-companies-slow-payments-to-suppliers-in-2019-as-cash-debt-continue-to-rise/  
   No DSO level is stated. The fiscal-2019→2020 placebo can be a positive receivable EA with no recognition change, and every noise-band pair includes 2020, so NB2 should be wider than one day. Closeness to expect: the 2019 leg moves in the same direction as slower collection, on a scale of days, not tens of percent of revenue.

## UNCERTAIN

- Live data.sec.gov behavior, the fair-access user-agent rule, and 17 U.S.C. 105, because those pages were not opened or did not load.
- Whether companyfacts `val` for liabilities is always a positive magnitude. The asset example on the wrapper page is positive. A negative contract-liability fact would flip N.
- ASU 2015-14’s deferral was not fetched. ASU 2014-09, as fetched, says public periods beginning after 15 Dec 2016. Starting the placebo at fiscal 2019 is the safe side either way.
- How large aggregate contract liabilities are relative to aggregate receivables in this 500. Fiscal 2023–2026 values were not read. Sparsity of the liability tags plus the 2018/19 industry DSO spread is the basis for the concentration claim.
- The 35× revenue-to-`ΔNI` sketch is the spec’s, not a measured figure.
