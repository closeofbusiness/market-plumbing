# CV1 stage 2 v2: did managers' perceived uncertainty fall? Aggregate proxies, build output

Specification: `_research/2026-11-13-CV1-Stage2-Aggregate-Proxies-Spec.md` (section Version 2, binding). Its sha256, pinned in `bin/cv1_stage2_uncertainty.py` and in `bin/check.sh` (M31), is `7cda4b28fe824781f426ea9f3d76ad6f4caa09c7a104792b5f332c0a6bc7b270`; `build` refuses to score if the file differs.
Built by `python3 bin/cv1_stage2_uncertainty.py build` from raw files frozen in the ignored cache `data/vintages/cv1_stage2/raw/`. `registered.csv` was written before any statistic was computed.

What these numbers can and cannot show: an aggregate series cannot attribute a change to AI. Only CV1-S1 v2 and CV1-S4 v2 carry labels. SUPPORT means consistent, not attributed. S2, S3, S5 and S6 are descriptive: none may be read as supporting or weakening stage 2.

## Labelled statements

### CV1-S1 v2

Y = a + b1 log(EPU) + b2 log(VIX) + b3 log(SPF dispersion) + d Treatment + e, OLS, N = 73 months (baseline Dec 2016 to Dec 2019: 37; treatment Jan 2023 to Dec 2025: 36).

| a | b1 (log EPU) | b2 (log VIX) | b3 (log SPF) | d | baseline residual SD (n-1, N=37) | effect size d / SD | label |
|---|---|---|---|---|---|---|---|
| 3.3183 | -0.0297 | 0.0096 | 0.2521 | 0.9290 | 0.2945 | 3.1551 | AGAINST |

### CV1-S4 v2

Numerator: unsmoothed `SalesRevGrowthUnc_percent`; denominator: `RealizedSalesGrowth_p90` minus `_p10`, observed rows only. R is the ratio of window means. N months baseline 37 of 37, treatment 24 of 24.

| window | N months | mean numerator | mean denominator | R |
|---|---|---|---|---|
| baseline Dec 2016 to Dec 2019 | 37 | 3.0342 | 21.1119 | 0.1437 |
| treatment Jan 2024 to Dec 2025 | 24 | 3.7966 | 24.8425 | 0.1528 |

R_T / R_B = 1.0634. Label: **UNLABELLED_S1_NOT_SUPPORT** (the statement is labelled only if CV1-S1 v2 is SUPPORT, and it is not).

Under the spec's fall-back rule for a sheet with no observed/projected flag (months at least 12 months before the workbook's last-updated date, 2026-10-28), R_B = 0.1437 (N=37) and R_T = 0.1515 (N=22); this variant is printed in `sensitivity.csv` only.

## Descriptive outputs (no label)

- `s2_beigebook_editions.csv`: 95 editions from 2015-01-14 to 2026-10-14; per edition the sentence count of the twelve District texts, the dictionary (a) and (b) counts and their rates per 1,000 sentences. 0 editions could not be parsed: none.
- `s3_dallas_uncertainty.csv`: not-seasonally-adjusted `uncri - uncrd` by month, TMOS (106 months) and TSSOS (106 months) separately, sheets `ms_nsa_Oct26` and `tssos_nsa_Oct26`. Negative = more firms said uncertainty fell this month than rose.
- `s5_boe_dmp.csv` (single_month): Jan 2023 to Dec 2025 mean 4.7248 (N=36 months) over Jan 2017 to Dec 2019 mean 4.5270 (N=36 months) = ratio 1.0437. This comparison mixes Brexit, the UK energy shock and carried-forward answers; it is not in US residual units.
- `s5_boe_dmp.csv` (three_month_average): Jan 2023 to Dec 2025 mean 4.7541 (N=36 months) over Jan 2017 to Dec 2019 mean 4.5198 (N=36 months) = ratio 1.0518. This comparison mixes Brexit, the UK energy shock and carried-forward answers; it is not in US residual units.
- `s6_btos.csv`: forecast-difficulty share (difficult or very difficult): 1 cycle(s) with a value out of 82 in the free national workbook; AI use, original wording: 54 cycles; AI use, current workbook: 25 cycles with a value. Lines are never spliced.

## Sources, retrieval and file hashes

| file | URL | retrieved (UTC) | sha256 |
|---|---|---|---|
| sbu-data.xlsx | https://www.atlantafed.org/-/media/Project/Atlanta/FRBA/Documents/research-and-data/surveys/business-uncertainty/sbu-data.xlsx | 2026-11-13T15:21:45Z | 661664969069211aed8459aa75fca6e9d9eb588a4f32cca7f60f2f4ff4c27d53 |
| US_Policy_Uncertainty_Data.xlsx | https://www.policyuncertainty.com/media/US_Policy_Uncertainty_Data.xlsx | 2026-11-13T15:21:45Z | f235b94f47b7862ab39c010e759118774c9a95f34f8016bb49906da227b0b66a |
| VIX_History.csv | https://cdn-api.cboe.com/api/global/us_indices/daily_prices/VIX_History.csv | 2026-11-13T15:21:46Z | 2a21208b9e9f61ad60e4d6b028bb9afc85483e4b0b94b69d2f0b1922dfd96820 |
| Dispersion_1.xlsx | https://www.philadelphiafed.org/-/media/FRBP/Assets/Surveys-And-Data/survey-of-professional-forecasters/historical-data/Dispersion_1.xlsx | 2026-11-13T15:21:47Z | 09c03595c26a004faa40d38318901eb02072590557d90923b81ce00b422da43e |
| tmos_alldata.xls | https://www.dallasfed.org/%7E/media/Documents/research/surveys/tmos/documents/alldata.xls | 2026-11-13T15:21:48Z | 937d709058cfc03ac02f2e69d9d846ae07d5e2340c445fade5a8bbcfef564ee4 |
| tssos_alldata.xls | https://www.dallasfed.org/%7E/media/Documents/research/surveys/tssos/documents/tssos_alldata.xls | 2026-11-13T15:21:49Z | 3dcb66477ad52cc2f77bba2228b766aa83e00e32a2d8fd602c0cc68f762788fb |
| monthly-dmp-data-october-2026.xlsx | https://www.bankofengland.co.uk/-/media/boe/files/decision-maker-panel-survey/2026/monthly-dmp-data-october-2026.xlsx | 2026-11-13T15:21:49Z | b3379c0903cf9b9543264c820b7151768f23d5c68a43512b371da6b26f36615f |
| National.xlsx | https://www.census.gov/hfp/btos/downloads/National.xlsx | 2026-11-13T15:21:50Z | 019cc3fff1ac2a985f27741084777780c4f9c7899a26b29dcf49392cad643f59 |
| AI_Core_Questions_original.xlsx | https://www.census.gov/hfp/btos/downloads/AI%20Core%20Questions.xlsx | 2026-11-13T15:21:51Z | e058a098af64427b0cf0c1455435023aeb9a84142a55175d322687e61a3da3ce |
| AI_Question_Wording_Updates.pdf | https://www.census.gov/hfp/btos/downloads/AI%20Question%20Wording%20Updates.pdf | 2026-11-13T15:21:52Z | 91b018352b693d500258cb649b7c8b1747d5fbfb5f065eeb8969276dd1068c28 |
| Beige Book pages (360 files) | https://www.federalreserve.gov/monetarypolicy/beigebook<YYYY>.htm year indexes and the pages they link (the 2026 index is beige-book-default.htm) | see the cache fetch log | 0f54ed8b34d54c332fba21fd3035c9660c642221a92c2390c60f886995bb5c80 (sha256 of the sorted list of file name and file sha256) |

SBU workbook last-updated date (from the workbook): 2026-10-28. Dallas workbooks: the one sheet in each is `ms_nsa_Oct26` and `tssos_nsa_Oct26`; the names confirm not seasonally adjusted. Dispersion file last updated 14 Aug 2026 (from the Philadelphia Fed page). BoE workbook: October 2026.

## Computations

- **S1 monthly inputs.** Y: `SalesRevGrowthUnc_percent` on sheet `Index Values (unsmoothed) `. EPU: `News_Based_Policy_Uncert_Index` on sheet `Main News Index`, taken as the monthly 10-paper index, logged. VIX: the mean of the daily `CLOSE` over every row of the calendar month, logged. SPF: D1 (75th minus 25th percentile) of the CPI forecast for horizon T+4 from the Philadelphia Fed's Dispersion_1 workbook, sheet `CPI`, each survey quarter's value assigned to the three calendar months of that quarter, logged. The local monthly panel is written to the ignored cache, not committed.
- **OLS.** Normal equations solved by Gaussian elimination with partial pivoting (`ols`); tested against a hand-computed case in `selftest`. Effect size = d divided by the sample standard deviation (n-1) of the residuals of the baseline months.
- **S4.** Months present in both the unsmoothed numerator and the observed denominator within each window; R = mean(numerator) / mean(denominator). Thresholds: SUPPORT if R_T <= 0.9 R_B, AGAINST if R_T >= R_B, else INCONCLUSIVE; unlabelled unless S1 v2 is SUPPORT.
- **S2.** Per edition, text of the twelve District sections pooled; sentences counted as in `split_sentences`; (a) = whole-word match of uncertain, uncertainty, uncertainties (case-insensitive); (b) = (a) and no whole word of {tariff, tariffs, election, elections, shutdown, regulation, regulations, regulatory, tax, taxes, fiscal, geopolitical, sanctions, immigration, pandemic, covid, brexit, congress, legislation} and no phrase of {federal reserve, interest rate, interest rates, debt ceiling, stock market, financial market, financial markets}. Rate = 1,000 x count / sentences.
- **S3.** `uncri` minus `uncrd` per month, per survey; the workbook's own `uncr` column was checked to equal that difference to within 0.15 for every month.
- **S5.** Means of the workbook's sales-growth uncertainty column, over the two registered windows; ratio of the treatment mean to the baseline mean.
- **S6.** Shares copied from the workbooks; forecast difficulty is the sum of the two answers named in the spec's wording.

Workbook note defining the S5 column (verbatim): "Data are percentage growth rates for realised and expected sales growth. Sales growth uncertainty is the average standard deviations of expected sales growth within firms."

## Implementation choices

- Cache location: the spec says the raw files go in an ignored path, and `data/vintages/` is not ignored as a whole; the script creates `data/vintages/cv1_stage2/` with its own `.gitignore` holding `*`, so nothing in it can be committed. No existing file was edited for this.
- Label boundaries are inclusive as the spec writes them: an effect size of exactly -0.5 is SUPPORT and exactly 0 is AGAINST; exactly 0.9 x R_B is SUPPORT and exactly R_B is AGAINST. Only values strictly between the thresholds are INCONCLUSIVE.
- SPF 'one-year CPI forecast dispersion': the Philadelphia Fed publishes cross-sectional dispersion for the quarterly CPI forecasts at horizons T to T+4 (annualised quarterly inflation). The horizon four quarters ahead, T+4, is taken as the one-year forecast; D1 = 75th minus 25th percentile. The other horizons are in `sensitivity.csv`. The annual-average CPI forecasts have no dispersion file there.
- VIX: the CBOE URL answers with a 307 to the same organisation's other host (cdn-api.cboe.com); the redirect was followed once inside the same registrable domain.
- EPU: the sheet is called `Main News Index` and its column `News_Based_Policy_Uncert_Index`; it is read as the monthly 10-paper index the spec names.
- Baseline residual SD uses the n-1 divisor; the n divisor is in `sensitivity.csv`.
- S4 'observed rows only': the sheet has no explicit flag column, but the observed rows are those with the realised percentiles filled in; the projected rows carry only `postline*` columns and are never used. The spec's fall-back rule (months at least 12 months before the vintage date) is therefore not the registered rule here; it is printed as a variant in `sensitivity.csv`.
- S4 months: a month enters a window only if both the numerator and the denominator exist; the counts are printed.
- S2 pages: for 2015 to 2023 each edition is one page with all twelve District sections, found by the fixed District headings (First District--Boston ... or Federal Reserve Bank of Boston ...); for 2024 onwards each District has its own page, built from the edition's summary-page link. The summary pages themselves are not fetched. The national summary is excluded because a section starts only at a District heading.
- S2 headings: four 2019 editions carry mistyped District headings on the Board's pages ('Federal Reserve Bank of Federal Reserve Bank of New York'; a bare 'St. Louis'); the District heading pattern accepts a repeated or missing 'Federal Reserve Bank of' prefix, still against the fixed twelve city names.
- S2 edition dates: release dates. For 2015 to 2023 from the page title; for 2024 onwards the page file name carries a cycle month that can differ from the release month (the March 2024 release sits in a file named 202402), so the summary pages on the year's index are paired in order with the release dates of the PDF links on the same index. The 2026 editions come from beige-book-default.htm, the 2026 year index returning 404.
- S2 sentence counting: text blocks are cut at paragraph and line breaks; section titles (lines wholly in bold or italic, headings) and two fixed boilerplate lines (Return to top; For more information about District economic conditions ...) are not text; every other piece counts as a sentence whether or not it ends with a stop. The splitter breaks on . ? ! followed by whitespace except after initials chained with periods (U.S., U.K., D.C.) and the abbreviations st, mt, ft, mr, mrs, ms, dr, jr, sr, inc, corp, co, ltd, vs, approx and the month abbreviations jan, feb, aug, sept, oct, nov, dec. A sentence that ends in U.S. and is followed by a new sentence is therefore not split.
- S2 dictionaries: whole-word, case-insensitive; phrases match with any run of whitespace between their words. No stems.
- S3: the Dallas files carry one sheet each, named for not seasonally adjusted data; the file with the .xls name is an xlsx container and was read as one.
- S5: the workbook has no column headed in the spec's words; its sheet `Subjective uncertainty` has `Sales growth uncertainty (%)` and its Notes sheet defines that as the average standard deviation of expected sales growth within firms, so the column is used. Both the single-month and the three-month-average columns are reported; v1 named the three-month average and v2 is silent.
- S6: lines are told apart by the question text and by collection dates, not by question number. The original AI series comes from Census's AI Core (original) workbook (to the cycle collected up to 5 Oct 2025); the current national workbook's AI-use cycles from collection start 17 Nov 2025 carry the business-functions wording until the cycle collected from 19 Oct 2026, where the Super Intelligence wording starts. The three groups are written as separate lines and never combined.
- The Beige Book fetch honours at most two requests a second to federalreserve.gov (about one every 0.65 s).

Projected-only rows in the realised-growth sheet (no observed percentiles, only `postline*` columns): 2027-10.

## Independent recompute (14 Nov 2026)

Gemini 4 Hydrogen (Medium) recomputed CV1-S1 v2 blind. It was given the four raw files and the registered method, but not our result. Every coefficient, the baseline residual SD (0.294451), the effect size (3.155098) and both Ns (37 and 36) agree with `scores.csv` to six decimal places. It identified the SPF column `CPI_D1(T+4)` from the header rows by itself. Asked about three values the files do not contain (SPF 2026Q4, SBU November 2026, VIX 14 November 2026), it answered "not in the files" each time. The supervisor confirmed each against the files.
