# Grok scoping of the next free-data measurements, 1 Nov 2026 (g15)

**Parcel:** `page.html` (docs/index.html at 19dacee), Grok 4.7 256K Extra High through the fenced Cursor lane, 1098 s, 12 searches,
25 fetch calls, no blocked or unexpected tool. Two URLs in the answer (FRED SKEW and the CFO Survey methodology page) were never fetched
and are dropped; Grok itself reported both as 404. The parcel listed what is built or declined and forbade computing any result.

**Supervisor's rulings (1 Nov):**
- **Take forward (1), the CFO Survey's expected S&P 500 return, as g15, reframed.** It was set aside on 14 Sep
  (2026-09-14-P5iv-Third-Premium-Measure.md, "Also on disk") because the panel gives no matched bond expectation, so it cannot be
  differenced into a premium. That still holds, and g15 builds no premium. What the page leans on instead is one sentence about the
  equity leg: "in the survey, equity expectations actually rose" (§02), which rests on a single panel (the Philadelphia Fed SPF,
  STOCK10, Q1 2024 to Q1 2026, +15.4bp; C-082). The CFO Survey's 10-year most-likely S&P 500 return is a second, independent panel
  on that same leg, quarterly from 2001. g15 tests whether it agrees, against its own pre-break noise. Spot check by the supervisor on 1 Nov:
  the Q3 2026 results page carries the table "Expected Annual S&P 500 Returns Over Next 12 Months and Next 10 Years" with a
  "Download Current and Historical Data" link. **Disclosure:** that check showed the supervisor the Q2 and Q3 2026 values of the table;
  no Q1 2024 or Q1 2026 value was seen. Surveys extrapolate past returns (Greenwood and Shleifer), so a rise is not proof of a higher
  discount rate; the spec must say so.
- **(2) OFR term tri-party repo rates: take as g16,** for the quarter-end stress question (the 2-7 and 8-30 day buckets start
  15 Aug 2025; the 30-or-fewer-day bucket runs 22 Aug 2014 to 13 Aug 2025, a break the spec must handle).
- **(3) Next-year operating-lease payments: declined.** It reads the recognised lease liability, not the stack the page is about.
- **(4) Cboe SKEW: declined.** The website terms bar publishing without consent; also a tail-risk index, not a premium.

The candidates are Grok's. Apart from the spot check above, the supervisor has not re-read each source.

## Return

GAPS
1. Who bought inside the household line: the Fed’s residual, and the holder side still cannot be split by legal entity on free data.
2. What the multiple’s resilience was made of: most of the measured compression restates the rate rise, and a third premium series without a bond leg is what the page says would settle the rest.
3. Whether the off-balance-sheet lease stack is fragile: Amazon’s term loan is already read; Oracle’s matured guarantee and the hand re-read of leases not yet commenced are queued.
4. Quarter-end funding stress: June and September did not show it, and December is set up as prints alone. The swap tape still has no daily series for swaps of a week to three months.
5. The term premium in government bonds: US models and the survey split on years five to ten; Germany was searched twice and is not reopened; Japan remains a model estimate.
6. Retirement flows after 2023: official defined-contribution flow tables stop in 2023, later ICI figures are balances, and the 2024 bulletin is the December read.
7. How much foreign Treasury demand is hedged is still unmeasured. Semiannual Japanese life-insurer PDFs stay declined.
8. Unreported central-bank gold is stated as not measurable on free data. No new source was searched this session.

CANDIDATE 1
GAP: “A third premium series that does not share a bond leg”
SOURCE URL: https://www.richmondfed.org/research/national_economy/cfo_survey/data_and_results/2026/20260923_data_and_results
QUOTE: “Expected Annual S&P 500 Returns Over Next 12 Months and Next 10 Years”
ACCESS: Quarterly. The stock-market block is on the quarterly HTML results pages, with no key. The earliest quarter read this session is the fourth quarter of 2021, on the 30 March 2022 commentary (https://www.richmondfed.org/research/national_economy/cfo_survey/research_and_commentary/2022/20220330_research_commentary). The third-quarter 2026 page is the latest fetched. The 25 March 2026 page says “Revised historical data are available for download,” but that file’s URL was not in the fetched text. The methodology URL https://www.richmondfed.org/research/national_economy/cfo_survey/methodology returned 404.
TERMS: No licence is stated on the pages fetched. The table source line is “Duke Fuqua School of Business, Federal Reserve Banks of Richmond and Atlanta.” Whether the download may be republished is UNCERTAIN. The methodology page, or a data-use note linked from the download, would settle it.
DESIGN: The population is US firms in The CFO Survey that said they closely follow the stock market. The statistic is the published most-likely annual S&P 500 return over the next 12 months and over the next 10 years, kept as that return. The comparison window is each quarter from the fourth quarter of 2021 through the third quarter of 2026, set beside the page’s 2024–26 window for the multiple. Assumption: “bond leg” means a premium defined by subtracting a Treasury yield. These tables say “S&P 500 Returns” and “actual return” and do not mention a Treasury yield. This is the equity-return block, not the declined Philadelphia Fed corporate-profit forecasts.
TRAP: Revisions. The 25 March 2026 page says survey data from the second quarter of 2020 through the fourth quarter of 2025 were revised, while the stock-market note on the 2022 commentary winsorizes at 2.5 and 97.5 percent and the 2026 notes winsorize at 5 percent. A spliced history mixes those treatments. Whether the stock-market block itself sits inside the revised file is UNCERTAIN.

CANDIDATE 2
GAP: “Neither June nor September showed it.”
SOURCE URL: https://data.financialresearch.gov/v1/series/full?mnemonic=REPO-TRIV1_AR_LE30-P&start_date=2019-03-29&end_date=2019-03-29
QUOTE: “Volume-weighted mean interest rate of term repurchase agreements starting on a given day and maturing in 30 or fewer days that were settled in tri-party repo, after excluding transactions with the Federal Reserve”
ACCESS: Daily JSON from the OFR series API, no key. The same call worked for REPO-TRIV1_AR_OO-P, REPO-TRIV1_AR_B27-P and REPO-TRIV1_AR_B830-P. Metadata start date for the 30-or-fewer-day series is 2014-08-22, and its last_update field is 2025-08-14. The 2–7 day and 8–30 day series each have metadata start date 2025-08-15. The mnemonic glossary (https://www.financialresearch.gov/short-term-funding-monitor/mnemonics/) says “Between 2 and 30 Days (series discontinued after August 13, 2025).” The dataset page (https://www.financialresearch.gov/short-term-funding-monitor/datasets/repo/) says the release is daily rates and volumes “broken out by tenor and underlying collateral.” The one-day gap between 13 August and 14 August 2025 was not reconciled; the last non-empty date of the old series was not read.
TERMS: The series notes say “The interest rate information published in this release is provided for informational purposes only” and that it “is not administered to International Organization of Securities Commissions (IOSCO) standards and is not intended to be referenced in contracts.” The metadata rights description is empty. Any licence beyond that note is UNCERTAIN. An OFR data-use page would settle it.
DESIGN: The population is tri-party repo excluding Federal Reserve transactions. The statistic is the volume-weighted mean rate on agreements maturing in 30 or fewer days, and after the split the separate 2–7 day and 8–30 day means. The comparison is each calendar quarter-end against the other business days of that month, from 22 August 2014 on the combined bucket and from 15 August 2025 on the two successor buckets, including the June and September turns the page already describes. This is a different OFR dataset from the money-fund monitor already used.
TRAP: A suppressed print can look like a quiet quarter-end. The notes say missing values are either no trading or disclosure edits. The old 30-day bucket also ends as the two new buckets begin, so a spliced “term rate” has a break. The release says these means use different transactions from SOFR and “do not allow for direct comparisons” with the New York Fed reference rates.

CANDIDATE 3
GAP: “Whether the off-balance-sheet lease stack is fragile.”
SOURCE URL: https://data.sec.gov/api/xbrl/companyconcept/CIK0000789019/us-gaap/LesseeOperatingLeaseLiabilityPaymentsDueNextTwelveMonths.json
QUOTE: “Amount of lessee's undiscounted obligation for lease payment for operating lease to be paid in next fiscal year following current fiscal year.”
ACCESS: Quarterly and annual, direct JSON, no key. The fetched file is Microsoft, label “Lessee, Operating Lease, Liability, to be Paid, Year One,” with 10-Q, 10-K and one 8-K facts whose period-end dates run from 2018-06-30 through 2026-09-30. The API page (https://www.sec.gov/search-filings/edgar-application-programming-interfaces) says “These APIs do not require any authentication or API keys to access.” The other four large spenders, and the later-year payment tags, were not fetched, so their coverage is UNCERTAIN. One companyconcept call each would settle it.
TERMS: No licence is stated on the API page fetched. These are public SEC filings.
DESIGN: The population is Microsoft for the file already fetched, with the page’s other large AI spenders added only after the same tag is confirmed for each. The statistic is one undiscounted operating-lease payment due in the next fiscal year per period-end, preferring the annual report when a later filing repeats the date. The comparison window is fiscal quarters from 30 June 2018 through 30 September 2026 against fiscal year-end 2023. This does not re-read the queued not-yet-commenced total or Oracle’s guarantee.
TRAP: Wrong stack. The tag is the recognized next-year payment, and its own description says it follows a rolling approach that can drop interim periods. The page says the $1,122.9bn of leases signed but not yet commenced has no machine-readable tag. Reading this series as that stack would answer a different question. The same period-end also appears on a later 8-K, so keeping every row double-counts.

CANDIDATE 4
GAP: “A third premium series that does not share a bond leg”
SOURCE URL: https://cdn.cboe.com/api/global/us_indices/daily_prices/SKEW_History.csv
QUOTE: “CBOE has developed a complementary indicator that measures perceived tail risk.”
ACCESS: Daily CSV, no key. The header is DATE,SKEW and the first row is 01/02/1990. The fetch was truncated before the last row, so the file’s end date was not read. The definition is from https://www.cboe.com/micro/skew/documents/skewwhitepaperjan2011.pdf. The dashboard https://www.cboe.com/us/indices/dashboard/skew/ returned no descriptive text. https://fred.stlouisfed.org/series/SKEW returned 404. This is Cboe’s skew index, not the declined WRDS SVIX.
TERMS: The white paper opens “CBOE Proprietary Information” and “All rights reserved.” The website terms (https://www.cboe.com/terms/, last updated 16 November 2022) allow one copy “for your personal non-commercial use” and say you may not “publish” or “distribute” the materials “without Cboe's prior written consent” except “fair use.” Whether a published series or chart is fair use is UNCERTAIN. A written answer from Cboe to a request to use the content would settle it.
DESIGN: The population is the Cboe SKEW index, the 30-day S&P 500 option price of tail risk described in the white paper. The statistic is the month-end index level, with no Treasury yield subtracted to turn it into a spread. The comparison is 2024–26 against 2015–19 on the daily file. Assumption: the page’s “bond leg” is a premium defined as a yield minus a Treasury yield. SKEW is not defined that way. The white paper does use a Treasury bill yield as the discount rate inside the option formula.
TRAP: A series that only looks free. The CSV downloads without a key, and the terms still restrict publication. It is also a tail-risk index, so it cannot by itself settle the page’s 49bp earnings-yield split. The 1990 start may include a back-cast: the 2011 paper says it is introducing the index and that the document contains back-tested performance. How much of the file is back-tested is UNCERTAIN.

NONE FOUND
Short-tenor FX swap basis, the price the page says the DTCC tape lacks for a week to three months. Fetched https://www.boj.or.jp/en/statistics/market/forex/fxdaily/, which publishes daily spot foreign-exchange rates and, in its correction list, “Turnover of Swap (US Dollar/Yen).” That is turnover, not a basis. No downloadable 1-week, 1-month or 3-month basis file was on the pages fetched. Web search results for an official CSV were papers and spot-rate pages, not a series file.
Defined-contribution dollar flows after 2023. Fetched https://www.ici.org/defined-contribution-plan-participants-activities. The latest item on that page is “Defined Contribution Plan Participants’ Activities, First Quarter 2023” and its supplemental xls, dated 28 July 2023. Fetched https://www.ici.org/research/stats/retirement, which lists “The US Retirement Market, Second Quarter 2026 (xls).” That page does not say the workbook contains contributions or withdrawals, and the workbook was not opened, so a hidden flow table is UNCERTAIN. Raw Form 5500 stays declined.
A scriptable years-5-to-10 term premium other than the models and the forecasters’ survey the page already uses. Fetched https://www.newyorkfed.org/markets/market-intelligence/survey-of-market-expectations and https://www.newyorkfed.org/markets/opolicy/operating_policy_241010. Excel results exist from the July 2023 survey onward, and the 2026 page has a Data column. The index page describes expectations for the federal funds rate, the Fed’s balance sheet, and economic indicators. The September 2026 questions PDF returned no readable question text, so a 5-to-10-year yield question was not confirmed. The German search was not reopened.
Japanese life-insurer hedge ratio in a scriptable file. Fetched https://www.seiho.or.jp/english/statistics/summary/, an index of monthly Excel workbooks back to fiscal 2019. The page does not name a hedge ratio, and no workbook was opened, so a sheet inside one is UNCERTAIN rather than absent. The declined semiannual PDFs were not reopened.

RANKING
1. Candidate 1, the CFO S&P return block, would change the most, because the page’s unresolved premium sentence is exactly an expected-return path that is not built by subtracting a bond yield, and this block is that path on a free quarterly page.
2. Candidate 2, the OFR term tri-party rates, would change the June and September “no stress” sentence, because those turns were read from overnight prints and sizes, and this file is the 2-to-30-day repo rate over the same calendar days, with a history back to August 2014 on the combined bucket.
3. Candidate 3, Microsoft’s next-year operating-lease payment, would add a rollover fact the lease section does not have, but it leaves the off-balance-sheet stack and the queued Oracle test untouched, so the fragility verdict would move less than the label suggests.
4. Candidate 4, Cboe SKEW, would add a long daily tail-risk price with no yield spread in its definition, and it would change the published page least until the republication terms are cleared, because the terms as fetched restrict publishing the series.