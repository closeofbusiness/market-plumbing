# US state and local government pension systems: money in, money out and holdings, survey years 2013 to 2025

This table shows how much US state and local government pension systems took in and paid out in each survey year from 2013 to 2025, and the cash and investments they reported holding, in the Census Bureau's Annual Survey of Public Pensions. Its one primary row compares survey year 2023 with survey year 2025: benefit payments per dollar of contributions went from 1.3127 to 1.3277, a change of +1.141%, labelled `within_band`, which means smaller than the largest past revision of this ratio (1.898%); that is not the same as no change.

It records the pension systems' own accounts only: a benefit payment is not a sale of equities, a contribution is not a purchase of them, and nothing here shows what the systems bought or sold in markets. These systems promise retirees a set benefit. Money in is what employees and governments paid in; money out is benefits to retirees and refunds to members who left. Beside the table are the cash and investments the systems reported holding. The figures are the Census Bureau's national estimates from its Annual Survey of Public Pensions. Survey year 2025 covers the fiscal years that most systems ended on 30 June 2025. Census does not say on what date holdings are measured; we take it to be the end of each system's fiscal year.

Survey year 2025 is a first release (a release is one posting of the survey's files by the Census Bureau), and the next release is expected to revise it and the years back to 2022.

## Timing

A survey year covers the fiscal year that begins on 1 July of the previous year and ends on 30 June of the survey year. Systems whose fiscal year ends after 30 June report their previous fiscal year. The exceptions are state systems in Alabama and Michigan, which report October to September, and in Texas, which reports September to August. Survey year 2025 is therefore mostly July 2024 to June 2025. Census's publication, file layouts and methodology do not say on what date holdings are measured, so the column `assets_end_usd_mn` carries an assumption in its name: the end of each system's fiscal year. These are survey years, not calendar years, and nothing here is set beside a calendar-year or quarterly series.

## What is counted

Nine lines, nationally, in millions of US dollars: employee contributions; government contributions; total contributions (the two together); benefit payments; withdrawals (refunds to members who leave); investment earnings excluding gains and losses; gains and losses on investments (signed); administrative and investment expenses; and cash and investments held. Net cash flow is contributions minus benefits minus withdrawals. It is neither the press release's gap of benefits minus contributions ($103.23bn in survey year 2025, which leaves out withdrawals) nor NASRA's external cash flow, which is a different measure on a different set of plans. Investment earnings here exclude gains. Administrative and investment expenses are their own line and are not part of net cash flow.

## Full-count years, sample years and the old years

In a *full-count year* (a census year: survey years 2017 and 2022) Census collects every system and every weight is 1. In a *sample year* it collects a sample and weights each row so that the weighted sum estimates the national total, so the figure carries sampling error. The error is reported as a *CV*: the coefficient of variation, which is the sampling error as a share of the estimate. Census publishes CVs in its sample-year summary tables (a summary table is Census's workbook of national and state totals for one survey year); no 2025 CV file is posted on www2.census.gov, so survey year 2025 has no CV here. System counts are the published counts from each year's summary table (a unit file is Census's row-by-row file, one row per system and item; its row count is not a system count); survey year 2025 has no summary table, and its publication counts 311 state systems and 4,061 local systems.

Survey years 2013 to 2016 are a separate, labelled segment (`old`) built from Census's summary tables; survey years 2017 to 2025 are the `current` segment (2020 comes from its summary table only). The 2015 brief says that more than 2,200 local systems were added in 2015, that the data may include hybrid and other post-employment funds, and that 2012 and 2015 should be compared only with caution. In the old years "earnings on investments" include gains and losses, so they sit in their own column. From 2017 the schema, the earnings definition and the asset detail change. For both reasons no change is computed within the old years or between 2016 and 2017; old years appear as single-year rows only.

## Beside the project's other retirement measures

The project's figures for private defined-contribution plans stop at 2023 and cover different plans on different dates; nothing in this table is added to, subtracted from or compared in one number with them. The Federal Reserve's Z.1 accounts record state and local defined-benefit plans' equity transactions in calendar quarters; this table is a cash account on fiscal years. The two are never set side by side.

## Levels

Millions of dollars are shown here as billions of dollars (`$bn`) to one decimal; the CSV files hold millions to three decimals.

**Current segment, `$bn`**

| Survey year | Kind | Contributions | Benefits | Withdrawals | Net cash flow | Earnings excluding gains | Gains and losses | Expenses | Cash and investments | Systems published |
|---|---|---|---|---|---|---|---|---|---|---|
| 2017 | census | 200.6 | 297.9 | 7.0 | -104.4 | 84.1 | 368.0 | 17.3 | 4,077.3 | 5,529 |
| 2018 | sample | 218.8 | 311.7 | 7.1 | -100.0 | 97.3 | 329.0 | 19.1 | 4,346.0 | 5,420 |
| 2019 | sample | 226.3 | 322.7 | 6.9 | -103.3 | 94.3 | 140.2 | 20.3 | 4,442.6 | 5,332 |
| 2020 | sample | 242.0 | 336.7 | 7.1 | -101.7 | 94.3 | 153.6 | 21.0 | 4,597.4 | 5,340 |
| 2021 | sample | 247.8 | 352.0 | 7.0 | -111.2 | 96.1 | 1,046.8 | 25.4 | 5,616.0 | 5,302 |
| 2022 | census | 288.0 | 368.1 | 7.7 | -87.8 | 108.9 | -115.5 | 27.9 | 5,422.7 | 4,634 |
| 2023 | sample | 294.7 | 386.9 | 8.1 | -100.2 | 110.7 | 79.3 | 26.2 | 5,484.5 | 4,566 |
| 2024 | sample | 304.5 | 404.5 | 8.5 | -108.4 | 114.6 | 466.4 | 30.4 | 5,984.0 | 4,535 |
| 2025 | sample | 315.0 | 418.2 | 8.7 | -111.9 | 123.2 | 493.6 | 32.5 | 6,490.2 | not in a summary table |

**Old segment, `$bn` (earnings include gains and losses)**

| Survey year | Contributions | Benefits | Withdrawals | Net cash flow | Earnings including gains | Cash and investments | Systems published |
|---|---|---|---|---|---|---|---|
| 2013 | 152.8 | 242.3 | 5.8 | -95.3 | 374.3 | 3,289.3 | 3,992 |
| 2014 | 165.2 | 253.6 | 6.5 | -94.9 | 546.8 | 3,706.6 | 3,972 |
| 2015 | 179.9 | 269.1 | 6.3 | -95.5 | 155.8 | 3,802.1 | 6,299 |
| 2016 | 190.6 | 283.4 | 6.1 | -98.8 | 51.2 | 3,733.4 | 6,276 |

## Ratios and the primary row

**The primary row** (the only one fixed in advance as primary): the change in benefit payments per dollar of contributions, segment `current`, from survey year 2023 to survey year 2025: 1.3127 to 1.3277, +1.141%, `within_band`. Every other row below is exploratory. `within_band` means smaller than one past revision. It does not mean no change.

**The band.** The band is 1.898%. It is the largest of 3 past revisions of the ratio, set by one full-count-year re-post (survey year 2022, -1.898%). The sample-year revisions were +0.102% (survey year 2023), +0.176% (survey year 2024), and the largest of them is 0.176%. The band was fixed after the first build. The first build had already shown the survey year 2023 to 2025 change (about +1.1% on the press-release figures), so both the band and that change were seen before the band was frozen. A label is a description set against one past revision. It is not a test.

| Span | Benefits per dollar of contributions, first year | second year | Change in dollars | Change in percent | Label | Status |
|---|---|---|---|---|---|---|
| survey year 2017 to survey year 2023 | 1.4855 | 1.3127 | -0.1728 | -11.634 | below_band | exploratory |
| survey year 2023 to survey year 2024 | 1.3127 | 1.3282 | +0.0155 | +1.184 | within_band | exploratory |
| survey year 2023 to survey year 2025 | 1.3127 | 1.3277 | +0.0150 | +1.141 | within_band | primary |
| survey year 2024 to survey year 2025 | 1.3282 | 1.3277 | -0.0006 | -0.043 | within_band | exploratory |

**Ratios by survey year.** Benefit payments per dollar of contributions is benefits divided by total contributions. Net cash flow as a share of opening assets is 100 times net cash flow divided by the previous survey year's cash and investments in the same release and the same segment; it is blank for 2013, 2015 (its opening assets cross the 2014-to-2015 jump in the number of systems) and 2017 (the segment changes). It is the main measure. Net cash flow as a share of end-of-year assets divides by the same survey year's cash and investments. End-of-year assets include that year's investment gains ($493.6bn in survey year 2025), so net cash flow is a smaller share of end-of-year assets in years with large gains; the share of opening assets is the main measure for that reason.

| Survey year | Segment | Benefits per dollar of contributions | Benefits and withdrawals per dollar of contributions | Net cash flow, % of opening assets | Net cash flow, % of end-of-year assets | Income per dollar of gap | Income per dollar of gap, after expenses | Sampling bound on the first ratio, % |
|---|---|---|---|---|---|---|---|---|
| 2013 | old | 1.5857 | 1.6238 | blank | -2.898 | not defined | not defined | 0.100 |
| 2014 | old | 1.5350 | 1.5745 | -2.886 | -2.561 | not defined | not defined | 0.085 |
| 2015 | old | 1.4955 | 1.5306 | blank | -2.511 | not defined | not defined | 0.357 |
| 2016 | old | 1.4863 | 1.5184 | -2.599 | -2.647 | not defined | not defined | 0.354 |
| 2017 | current | 1.4855 | 1.5207 | blank | -2.561 | 0.8049 | 0.6907 | 0.000 |
| 2018 | current | 1.4243 | 1.4570 | -2.453 | -2.301 | 0.9731 | 0.8173 | 0.321 |
| 2019 | current | 1.4261 | 1.4566 | -2.378 | -2.326 | 0.9123 | 0.7623 | 0.229 |
| 2020 | current | 1.3913 | 1.4205 | -2.290 | -2.213 | 0.9266 | 0.7678 | 0.146 |
| 2021 | current | 1.4204 | 1.4488 | -2.419 | -1.981 | 0.8640 | 0.7035 | 0.137 |
| 2022 | current | 1.2784 | 1.3050 | -1.564 | -1.620 | 1.2401 | 0.9415 | 0.000 |
| 2023 | current | 1.3127 | 1.3401 | -1.849 | -1.828 | 1.1042 | 0.8756 | 0.108 |
| 2024 | current | 1.3282 | 1.3561 | -1.977 | -1.812 | 1.0573 | 0.8259 | 0.308 |
| 2025 | current | 1.3277 | 1.3552 | -1.870 | -1.724 | 1.1015 | 0.8536 | not posted |

**Investment income against the gap** (current segment only). The gap is the amount by which benefits plus withdrawals exceeded contributions. The first income ratio is interest, dividends and other investment income per dollar by which payouts exceeded contributions; it was 1.1042 in survey year 2023 and 1.1015 in survey year 2025. The second adds administrative and investment expenses to the payouts: 0.8756 and 0.8536. The table does not show which money paid which benefit.

**Sampling bound.** The last column is 100 times the sum of the published CVs of benefits and of contributions, a ceiling on the sampling CV of the first ratio whatever their correlation. It is 0.108% for survey year 2023 and 0.308% for survey year 2024, and 0 in full-count years. It is blank for survey year 2025, because no 2025 CV file is posted on www2.census.gov. Revisions have been larger than this sampling error.

## Revisions and vintages

Each Census release revises earlier years. A vintage is the set of files fetched together, identified by their posting dates. The unit files in this vintage carry these posting dates (survey years after the colon): 2026-05-14: 2022, 2023, 2024, 2025; 2025-05-23: 2017, 2018, 2019, 2021. The summary tables: 2025-05-23: 2017, 2018, 2019, 2020, 2021, 2022, 2023, 2024; 2018-08-06: 2013, 2014, 2015, 2016. Where a summary table and a unit file carry different dates, the ratio of benefits to contributions changed by -1.898% for survey year 2022, +0.102% for survey year 2023, +0.176% for survey year 2024. `revisions.csv` is regenerated on every build from each year's summary table against its unit file where their dates differ, and from every adjacent pair of complete cached vintages. This file set is vintage `1e8f842133376a6b`; its newest unit file is ASPP_Unit_File_2025.csv, dated 2026-05-14. The next release (survey year 2026) is not announced; May 2027 is expected on this pattern. One statement is registered in advance, and it is about revisions only: in the first release carrying survey year 2026, the re-posted survey year 2025 benefits per dollar of contributions differs from this build's value by less than 1.898%. Nothing is registered about the cash flows themselves.

## Column dictionary

Every file begins with a `# source:` line. `segment` and `schema` are `old` (survey years 2013 to 2016) or `current` (2017 to 2025). `year_kind` is `census` (full-count year) or `sample`. `pp` is a percentage point. `source_kind` is `unit_file` or `summary`. Money columns are millions of US dollars to three decimals.

- `national.csv`: one row per survey year, 2013 to 2025. `contrib_employee_usd_mn`, `contrib_government_usd_mn`, `contrib_total_usd_mn`, `benefits_usd_mn`, `withdrawals_usd_mn`, `earnings_ex_gains_usd_mn` (current segment), `earnings_old_schema_usd_mn` (old segment, includes gains), `gains_losses_usd_mn` (signed), `expenses_admin_invest_usd_mn`, and `assets_end_usd_mn` (cash and investments; an assumption that holdings are measured at the end of each system's fiscal year). `net_cash_usd_mn` = contributions minus benefits minus withdrawals; it is negative when payouts exceed contributions. `systems_published` is the published count. `cv_*` are published CVs as fractions, blank in full-count years and for 2025. `summary_file_date` and `source_file_date` are the posting dates of the summary table and of the file the row was built from.

- `ratios.csv`: `benefits_per_contrib_usd` = benefits / total contributions; `benefits_withdrawals_per_contrib_usd` = (benefits + withdrawals) / total contributions; `net_cash_pct_of_assets_start` = 100 x net cash / the previous survey year's `assets_end` (same release, same segment); `net_cash_pct_of_assets_end` = 100 x net cash / the same survey year's `assets_end`; `income_per_net_cash_gap_usd` = earnings excluding gains / (benefits + withdrawals - contributions), blank if that denominator is not positive; `income_per_gap_after_expenses_usd` = earnings excluding gains / (benefits + withdrawals + expenses - contributions); `ratio_cv_bound_pct` = 100 x (CV of benefits + CV of contributions).

- `summary.csv`: one row per statistic, keyed by (`question`, `segment`, `from_year`, `to_year`, `statistic`); `pattern` is `above_band`, `below_band`, `within_band` or `n_a`, and only the percent change of the ratio carries one; `primary` marks the one primary row. `revisions.csv`: the value in the earlier and the later source, the change in millions and in percent (against the size of the earlier value). `vintages.csv`, `checks.csv` and `fetch_log.csv` record the cache, the checks and the requests.

## Citation

U.S. Census Bureau, Annual Survey of Public Pensions, survey years 2013-2025, unit files and summary tables, https://www.census.gov/programs-surveys/aspp.html, vintage 1e8f842133376a6b (newest unit file 2026-05-14). Census asks users who make their own estimates to cite the Census Bureau as the source of the original data only. The raw files stay in the gitignored cache, and only national totals are committed. How the numbers were fetched, the checks and the builder's decisions are in [SOURCES.md](SOURCES.md).
