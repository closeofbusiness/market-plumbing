# US money market funds' claims on non-US financial institutions, by parent country and instrument

This table shows how much US money market funds held at each month-end since January 2011 in claims on banks and other financial institutions whose ultimate parent, the company at the top of the group, is headquartered outside the United States, by that parent's home country and by type of instrument. The figures come from the funds' own monthly holdings reports to the Securities and Exchange Commission, called Form N-MFP, as compiled by the Treasury's Office of Financial Research (OFR), which assigns each security's issuer, or for a repurchase agreement (repo) the firm on the other side of the trade, called the repo counterparty, to its ultimate parent.

It records month-end holdings only; it does not show why they changed, and a change in holdings is not a measure of money moved. The months run from 31 January 2011 to 30 September 2026; this vintage is the OFR release updated 15 October 2026.

## Country basis

The country is the home country of the ultimate parent, not the place where a branch sits: a US branch of a Japanese bank counts as Japan. The OFR takes it from the address of the ultimate parent's headquarters or, if that differs, the country where its sources suggest the parent has its most substantial operations. It is the only basis the OFR offers, and it matches how the BIS paper below discusses bank funding; a residence basis is not available from this source.

Repo cleared through the Fixed Income Clearing Corporation (FICC) is reported with FICC as the counterparty, and the OFR maps FICC to the United States, so a non-US bank's cleared repo does not appear under its own country. The table carries FICC as a separate memo line, MEMO_FICC, outside every non-US total. A fall in a country line may be offset by a rise in the FICC line shown next to it.

The OFR's parent mapping is imperfect: for example `Natexis + Natixis` and `Groupe BPCE` are separate parents, and so are two Northwestern Mutual entries. This table takes the OFR's parents and countries as published and never re-maps them. The country groups are:

- **EA**: euro area (2026 membership applied to every date)
- **FR**: France (also inside EA)
- **JP**: Japan
- **CA**: Canada
- **UK**: United Kingdom
- **CH**: Switzerland
- **NORDIC**: Sweden, Norway and Denmark
- **AUNZ**: Australia and New Zealand (every country the OFR lists under its region Australia)
- **OTHER_ASIA**: every other country the OFR lists under Asia
- **OTHER**: every other non-US country
- **ALL_NONUS**: the sum of the nine groups EA, JP, CA, UK, CH, NORDIC, AUNZ, OTHER_ASIA and OTHER (FR is inside EA and is not added again)
- **MEMO_FICC**: repo cleared through FICC, which the OFR maps to the USA; outside every non-US total

## What is counted

Only the OFR's `Financial Institution` sector of non-US countries, summed over prime, government and tax-exempt funds (the OFR renamed its fund categories in April 2016 and again in 2024, and the build joins the old and new names). Instruments: repo (by collateral: Treasury, government agency, other), unsecured (certificates of deposit, time deposits, financial commercial paper, other notes), asset-backed commercial paper (ABCP, which the OFR assigns to the sponsoring bank's parent and which stays in the total) and other (non-financial commercial paper, Treasury and agency debt). Repo + unsecured + ABCP + other = total. These month-end changes are not flows of funds, and the table does not test window dressing or any other motive.

The measure `bank_only` counts only parents the builder classed as banks (deposit-taking institutions and bank holding companies); broker-dealers are classed `other_fin` and insurers `insurer`, and both are left out of `bank_only`. The classification is in `parents.csv`.

## Levels and shares

Billions of US dollars at month-end, all fund types, by country group. The endpoints are every February from 2011 to 2026 and 31 August 2026: all are mid-quarter months, because a quarter-end month can be unusually low or high, and an endpoint there would put a quarter-end move into a multi-year change.

| Month-end | ALL_NONUS | EA | FR | JP | CA | UK | CH | NORDIC | AUNZ | OTHER_ASIA | OTHER | MEMO_FICC |
|---|---|---|---|---|---|---|---|---|---|---|---|---|
| 2011-02-28 | 1,422.2 | 622.4 | 285.0 | 82.5 | 146.3 | 277.0 | 83.6 | 106.1 | 103.6 | 0.5 | 0.3 | 0.0 |
| 2012-02-29 | 1,271.2 | 355.3 | 128.3 | 131.2 | 192.1 | 240.4 | 111.2 | 105.9 | 130.1 | 4.6 | 0.4 | 0.0 |
| 2013-02-28 | 1,345.0 | 433.5 | 208.8 | 162.7 | 232.1 | 167.7 | 81.5 | 134.9 | 118.6 | 12.5 | 1.5 | 0.0 |
| 2014-02-28 | 1,324.7 | 455.5 | 251.3 | 181.1 | 222.6 | 137.5 | 66.3 | 136.9 | 97.2 | 25.9 | 1.6 | 0.0 |
| 2015-02-28 | 1,317.6 | 415.2 | 255.2 | 187.3 | 231.0 | 139.6 | 53.8 | 156.6 | 101.0 | 30.4 | 2.7 | 0.2 |
| 2016-02-29 | 1,285.3 | 444.5 | 303.2 | 173.0 | 230.6 | 107.1 | 63.5 | 157.4 | 83.0 | 24.2 | 2.1 | 0.1 |
| 2017-02-28 | 832.0 | 345.1 | 248.3 | 127.5 | 163.7 | 71.5 | 19.8 | 55.6 | 38.2 | 9.9 | 0.8 | 0.0 |
| 2018-02-28 | 1,097.1 | 411.4 | 285.2 | 176.7 | 212.8 | 142.0 | 43.1 | 55.9 | 41.9 | 12.8 | 0.6 | 21.3 |
| 2019-02-28 | 1,219.6 | 410.3 | 295.4 | 224.9 | 264.2 | 150.9 | 45.9 | 67.8 | 40.6 | 14.5 | 0.5 | 103.0 |
| 2020-02-29 | 1,416.1 | 481.3 | 312.5 | 259.9 | 328.2 | 179.6 | 31.5 | 62.0 | 52.7 | 20.3 | 0.5 | 202.1 |
| 2021-02-28 | 1,181.6 | 430.2 | 285.3 | 222.1 | 263.2 | 138.1 | 21.1 | 64.2 | 31.2 | 11.3 | 0.2 | 92.6 |
| 2022-02-28 | 936.2 | 322.2 | 203.3 | 185.6 | 212.5 | 97.9 | 14.1 | 57.8 | 30.8 | 15.4 | 0.0 | 141.2 |
| 2023-02-28 | 918.0 | 298.6 | 168.6 | 186.9 | 217.0 | 84.7 | 8.1 | 57.7 | 40.4 | 24.6 | 0.0 | 183.9 |
| 2024-02-29 | 1,445.2 | 445.4 | 287.3 | 274.9 | 361.0 | 202.3 | 8.6 | 77.5 | 50.3 | 25.2 | 0.0 | 490.6 |
| 2025-02-28 | 1,423.0 | 471.4 | 317.3 | 276.3 | 376.9 | 166.6 | 3.9 | 47.0 | 55.8 | 25.1 | 0.0 | 910.6 |
| 2026-02-28 | 1,478.8 | 479.2 | 330.9 | 261.2 | 450.7 | 160.3 | 5.2 | 46.0 | 53.7 | 22.5 | 0.0 | 1,206.4 |
| 2026-08-31 | 1,488.7 | 517.7 | 354.6 | 255.4 | 425.8 | 166.8 | 7.7 | 43.3 | 54.0 | 18.1 | 0.0 | 966.9 |

All US money funds' claims on non-US financial institutions (ALL_NONUS) by measure, with the share of all US money funds' investments:

| Month-end | headline | bank_only | secured | unsecured | abcp | misc | headline, percent of all US money funds | all US money funds |
|---|---|---|---|---|---|---|---|---|
| 2011-02-28 | 1,422.2 | 1,402.5 | 405.2 | 900.9 | 100.3 | 15.6 | 47.161 | 3,015.5 |
| 2012-02-29 | 1,271.2 | 1,260.7 | 463.6 | 708.3 | 82.2 | 17.2 | 42.629 | 2,982.1 |
| 2013-02-28 | 1,345.0 | 1,323.6 | 407.9 | 828.3 | 82.3 | 26.5 | 44.918 | 2,994.3 |
| 2014-02-28 | 1,324.7 | 1,295.0 | 303.2 | 923.6 | 70.7 | 27.3 | 43.770 | 3,026.6 |
| 2015-02-28 | 1,317.6 | 1,295.2 | 259.9 | 967.2 | 67.0 | 23.6 | 43.444 | 3,032.9 |
| 2016-02-29 | 1,285.3 | 1,263.6 | 347.1 | 840.6 | 77.0 | 20.7 | 41.049 | 3,131.2 |
| 2017-02-28 | 832.0 | 783.5 | 493.6 | 307.4 | 22.7 | 8.3 | 28.340 | 2,935.9 |
| 2018-02-28 | 1,097.1 | 1,030.2 | 697.4 | 364.4 | 27.8 | 7.5 | 34.624 | 3,168.6 |
| 2019-02-28 | 1,219.6 | 1,154.9 | 750.0 | 427.2 | 36.7 | 5.7 | 35.460 | 3,439.4 |
| 2020-02-29 | 1,416.1 | 1,351.5 | 828.4 | 539.1 | 39.9 | 8.8 | 35.130 | 4,031.0 |
| 2021-02-28 | 1,181.6 | 1,108.3 | 730.4 | 417.1 | 21.4 | 12.7 | 24.323 | 4,857.8 |
| 2022-02-28 | 936.2 | 888.0 | 536.5 | 373.0 | 16.7 | 10.1 | 18.225 | 5,137.1 |
| 2023-02-28 | 918.0 | 873.6 | 430.1 | 441.9 | 32.5 | 13.5 | 17.339 | 5,294.3 |
| 2024-02-29 | 1,445.2 | 1,388.5 | 864.3 | 528.1 | 45.2 | 7.5 | 22.078 | 6,545.9 |
| 2025-02-28 | 1,423.0 | 1,367.0 | 910.8 | 459.5 | 45.0 | 7.7 | 19.261 | 7,388.2 |
| 2026-02-28 | 1,478.8 | 1,435.4 | 973.6 | 450.4 | 45.0 | 9.8 | 17.703 | 8,353.3 |
| 2026-08-31 | 1,488.7 | 1,435.8 | 1,007.9 | 424.3 | 47.5 | 9.1 | 17.452 | 8,530.6 |

## Change from 2024 to 2026

Month-end levels in billions of dollars at the first and last of the 2024-2026 endpoints, the percent change between them (100 times the natural log of the ratio), and the change in the share of all US money funds' investments in percentage points. The in-between endpoints are in `summary.csv`.

| Group | Measure | 2024-02-29 | 2025-02-28 | 2026-02-28 | 2026-08-31 | percent change, first to last | change in share of all US money funds, points |
|---|---|---|---|---|---|---|---|
| ALL_NONUS | headline | 1,445.2 | 1,423.0 | 1,478.8 | 1,488.7 | 3.0 | -4.626 |
| ALL_NONUS | secured | 864.3 | 910.8 | 973.6 | 1,007.9 | 15.4 | -1.389 |
| ALL_NONUS | unsecured | 528.1 | 459.5 | 450.4 | 424.3 | -21.9 | -3.094 |
| EA | headline | 445.4 | 471.4 | 479.2 | 517.7 | 15.0 | -0.735 |
| FR | headline | 287.3 | 317.3 | 330.9 | 354.6 | 21.0 | -0.232 |
| JP | headline | 274.9 | 276.3 | 261.2 | 255.4 | -7.3 | -1.205 |
| CA | headline | 361.0 | 376.9 | 450.7 | 425.8 | 16.5 | -0.524 |
| UK | headline | 202.3 | 166.6 | 160.3 | 166.8 | -19.3 | -1.134 |
| CH | headline | 8.6 | 3.9 | 5.2 | 7.7 | -11.6 | -0.042 |
| NORDIC | headline | 77.5 | 47.0 | 46.0 | 43.3 | -58.4 | -0.678 |
| AUNZ | headline | 50.3 | 55.8 | 53.7 | 54.0 | 7.0 | -0.136 |
| OTHER_ASIA | headline | 25.2 | 25.1 | 22.5 | 18.1 | -33.0 | -0.172 |
| OTHER | headline | 0.0 | 0.0 | 0.0 | 0.0 | n/a | 0.000 |
| MEMO_FICC | headline | 490.6 | 910.6 | 1,206.4 | 966.9 | 67.8 | 3.839 |

## Quarter-ends

The question is how far a quarter-end month-end falls below the neighbouring month-ends, in percent. For a group's level L at the quarter-end month q, with q-1 and q+1 the month-ends on either side, the fall below the neighbouring months is 100 x [ln L(q) - 1/2 (ln L(q-1) + ln L(q+1))], half of the percent change into q minus the percent change out of q. A negative number means q is lower than the average of its neighbours. For Canadian banks' fiscal quarter-ends (31 January, 30 April, 31 July, 31 October) the previous month-end is a calendar quarter-end, so only the next month is used: the fall is minus the percent change from the fiscal month-end to the next one. No basis other than the calendar one uses a calendar quarter-end month as a neighbour.

**Noise reference.** The standard deviation of the month-on-month percent changes from January to February, April to May, July to August and October to November (the only changes that touch no calendar quarter-end month) in the same window, divided by the square root of 2 for the two-sided rows. **Comparison with Australia and New Zealand.** For each other group, the paired difference between its fall below the neighbouring months and the AUNZ fall in the same quarters, with n, mean and standard error. **Windows.** `post_reform` is the 38 quarters 2017Q1 to 2026Q2 (after the 14 October 2016 prime-fund reform), frozen; `pre_reform` is 2011Q1 to 2016Q2 (22 quarters); the third and fourth quarters of 2016 are written as rows but in no summary; 2026Q3 onward is `after_freeze`, and a quarter whose next month-end is not yet published carries only the change into it.

**The single primary row** is repo (`secured`) held by ALL_NONUS at calendar quarter-ends in the `post_reform` window: n = 38, mean fall below the neighbouring months -9.9632 percent (standard error 1.0234, median -8.6924), noise reference 4.3952 percent, pattern `lower`. The prediction fixed before the build was a mean fall of 5 percent or more. **Every other row, group, basis and window is exploratory.** `pattern` is `lower` when the mean is at least twice its standard error below zero, `higher` when at least twice above, `neither` otherwise and `insufficient` below 8 quarters; it describes the sample and says nothing about why.

Calendar basis, `post_reform` window (exploratory except the first secured row):

| Group | Measure | Quarters (n) | Mean fall below neighbours, percent (standard error) | Median | Noise reference, percent | Pattern | Minus AUNZ: n, mean (se) |
|---|---|---|---|---|---|---|---|
| ALL_NONUS | headline | 38 | -9.2576 (se 0.7868) | -8.9192 | 2.9857 | lower | 38: -11.2409 (se 1.5725) |
| ALL_NONUS | bank_only | 38 | -9.6389 (se 0.7945) | -9.0767 | 2.9755 | lower | 38: -11.6203 (se 1.5976) |
| ALL_NONUS | secured | 38 | -9.9632 (se 1.0234) | -8.6924 | 4.3952 | lower | 38: -8.6295 (se 2.8701) |
| ALL_NONUS | unsecured | 38 | -8.9085 (se 1.1784) | -8.1357 | 2.2465 | lower | 38: -11.7562 (se 1.8911) |
| EA | secured | 38 | -20.6143 (se 1.9669) | -16.9861 | 4.3762 | lower | 38: -19.2807 (se 3.4121) |
| FR | secured | 38 | -22.4699 (se 2.3358) | -21.2658 | 4.6616 | lower | 38: -21.1363 (se 3.6244) |
| JP | secured | 38 | -3.5195 (se 0.8456) | -2.8855 | 4.5708 | lower | 38: -2.1858 (se 2.9599) |
| CA | secured | 38 | 7.7082 (se 1.4334) | 8.7865 | 7.7799 | higher | 38: 9.0419 (se 2.9677) |
| UK | secured | 38 | -22.0936 (se 2.2485) | -18.3638 | 10.3843 | lower | 38: -20.7599 (se 2.8754) |
| CH | secured | 38 | -40.9924 (se 9.3479) | -14.7356 | 14.4458 | lower | 38: -39.6587 (se 10.3751) |
| NORDIC | secured | 20 | -11.6894 (se 7.4348) | -3.4033 | 27.6561 | neither | 20: -16.7003 (se 9.2567) |
| AUNZ | secured | 38 | -1.3337 (se 2.8558) | -1.3962 | 11.7928 | neither |  |
| OTHER_ASIA | secured | 8 | -19.3584 (se 11.7688) | -14.8207 | 10.7647 | neither | 8: -11.8307 (se 12.5445) |
| OTHER | secured | 0 | n/a |  |  | insufficient |  |

Japan's fiscal year ends in March (n = 10 March quarter-ends in the window, a small number), set beside its other quarter-ends (n = 28); Canada's fiscal quarter-ends use the next month only, for the reason above:

| Basis | Group | Measure | Statistic | Quarters (n) | Mean fall below neighbours, percent (standard error) | Noise reference, percent | Pattern |
|---|---|---|---|---|---|---|---|
| jp_march | JP | headline | two_sided | 10 | -5.0195 (se 1.3716) | 3.4248 | lower |
| jp_march | JP | secured | two_sided | 10 | -4.8267 (se 1.8624) | 4.5708 | lower |
| jp_other | JP | headline | two_sided | 28 | -2.8369 (se 0.5944) | 3.4248 | lower |
| jp_other | JP | secured | two_sided | 28 | -3.0526 (se 0.9414) | 4.5708 | lower |
| ca_fiscal | CA | headline | one_sided | 38 | -7.8267 (se 1.3148) | 8.1051 | lower |
| ca_fiscal | CA | secured | one_sided | 38 | -10.5070 (se 1.7848) | 11.0024 | lower |

## Set beside the BIS CGFS Paper 65

The paper's words are quoted briefly with their printed page numbers; the right-hand column is descriptive and carries no verdict.

| What CGFS Paper 65 says (BIS, June 2020) | What this table holds |
|---|---|
| Non-US banks "now obtain less funding from US MMFs" (p 20), after the 2016 reform cut prime funds by about 1 trillion dollars (p 20). | ALL_NONUS headline: 1,285.3 billion dollars on 2016-02-29 and 1,478.8 billion on 2026-02-28; share of all US money funds 41.049 percent and 17.703 percent. |
| French banks raise dollars "mainly via overnight repos from US MMFs" (p 67) and US money funds "have become the most important repo counterparties to French banks" (pp 67-68). | FR secured (repo): 154.6 billion dollars on 2016-02-29 and 292.9 billion on 2026-02-28. Repo cleared through FICC is in MEMO_FICC, not in FR. |
| "some non-US banks significantly reduce their matched book repo activity at quarter-ends" (p 35); no country is named. | Primary row, ALL_NONUS secured, calendar quarter-ends, post_reform: n 38, mean fall below the neighbouring months -9.9632 percent (standard error 1.0234). |
| Australian banks "are not subject to the quarter- or year-end balance sheet constraints" (p 73). | AUNZ secured, same basis and window: n 38, mean -1.3337 percent (standard error 2.8558). The paired differences against AUNZ are in qe_summary.csv. |
| Tenor "has shortened considerably" (p 27). | Not measured here: the OFR monitor has no maturity by country. |

## Tenor is not available

The OFR monitor has no maturity by country, so nothing here says how long the repo or paper runs. The SEC's N-MFP data sets would supply it and would be a separate piece of work.

## Revisions and vintages

Each OFR release revises the complete series, and the monitor's files are overwritten in place. Each complete crawl is kept as a vintage (`vintages.csv`), and `revisions.csv` is rewritten on every build from all adjacent pairs of cached vintages. Vintages held: 1 (2026-10-15). Cells changed in the latest pair: none yet, only one vintage.

## Columns

**levels_country.csv**: Month-end holdings by the OFR's parent country and instrument, all fund types together, non-US countries only, nonzero cells; one `total` row per country and month.
- `month_end`: calendar month-end
- `country`: the OFR's country label for the ultimate parent
- `country_group`: the group of section above (France is shown under EA)
- `instrument_group`: repo_treasury, repo_agency, repo_other, cd, time_deposit, fin_cp, other_note, abcp, misc, unallocated, or total
- `usd_mn`: millions of US dollars
- `pct_of_mmf_total`: percent of the total investments of all US money funds that month-end
- `pct_of_nonus_fi`: percent of the ALL_NONUS headline that month-end
- `vintage`: the OFR release the row comes from (its updated date)

**levels_group.csv**: Month-end holdings by country group, fund type and measure.
- `month_end`: calendar month-end
- `country_group`: EA, FR, JP, CA, UK, CH, NORDIC, AUNZ, OTHER_ASIA, OTHER, ALL_NONUS or MEMO_FICC
- `fund_lineage`: all, prime, government or tax_exempt (each lineage joins the OFR's category names before and after 2016 and 2024)
- `measure`: headline (all instruments), bank_only (parents classed as banks), secured (repo), unsecured (certificates of deposit, time deposits, financial commercial paper, other notes), abcp, misc
- `usd_mn`: millions of US dollars
- `pct_of_mmf_total`: percent of all US money funds
- `pct_of_lineage_total`: percent of the same fund lineage's total
- `vintage`: as above

**quarter_ends.csv**: One row per quarter-end month, group, measure and basis.
- `quarter`: calendar quarter holding the month
- `qe_month`: the month-end examined
- `basis`: calendar, jp_march, jp_other or ca_fiscal
- `stat_kind`: two_sided, or one_sided for ca_fiscal
- `country_group`: as above
- `measure`: headline, bank_only, secured or unsecured
- `level_prev_usd_mn, level_qe_usd_mn, level_next_usd_mn`: levels at the previous, examined and next month-end, millions of dollars
- `chg_in_pct, chg_out_pct`: percent change into and out of the examined month-end (100 times the natural log of the ratio)
- `below_nbrs_pct`: how far the examined month-end falls below the neighbouring months, percent; negative means lower than the neighbours
- `below_nbrs_usd_mn`: the same in millions of dollars, level minus the average of the neighbours
- `window`: post_reform, transition, pre_reform or after_freeze
- `frozen_set`: yes for quarters up to 2026Q2
- `primary`: yes on the single primary row set
- `blind`: yes only for rows whose answer was not seen before the build
- `vintage`: as above

**qe_summary.csv**: The summary of quarter_ends.csv per basis, window, group and measure.
- `n_quarters, n_blank`: quarters with and without a computed value
- `mean_below_nbrs_pct, median_below_nbrs_pct, n_negative, sd_below_nbrs_pct, se_mean_below_nbrs_pct`: mean, median, count of negative values, sample standard deviation and standard error of the mean
- `noise_clean_sd_pct, noise_n`: the noise reference and the number of changes it uses
- `pattern`: lower, higher, neither or insufficient: a description of the sample
- `paired_n_vs_aunz, paired_mean_diff_vs_aunz_pct, paired_se_vs_aunz_pct`: the paired difference against AUNZ over quarters where both are computed: n, mean, standard error
- `primary, blind, vintage`: as above

**parents.csv**: The OFR's non-US financial-institution parents, with the builder's classification.
- `parent, country, country_group`: the OFR's parent name, country label and group
- `kind`: bank, insurer or other_fin
- `first_month, last_month`: first and last month-end with a nonzero holding
- `usd_mn_latest`: millions of dollars at the latest month-end
- `vintage`: as above

**summary.csv**: Levels, shares and changes at the named endpoints, revision counts and the hit rate. One statistic per row.
- `question, window, country_group, measure, from_month, to_month`: what the row answers
- `statistic, value, unit`: the statistic, its value and unit
- `primary, blind`: as above

**revisions.csv**: Cells whose value differs between two adjacent cached OFR releases (rewritten on every build).
- `vintage_prev, vintage_new, month_end, country, instrument_group`: the pair and the cell
- `usd_mn_prev, usd_mn_new, change_usd_mn`: values in millions of dollars

**vintages.csv**: One row per cached OFR release.
- `vintage, ofr_updated, ofr_asof`: the release key and the OFR's own updated and as-of dates
- `requests, nodes`: requests made and chart files held
- `manifest_sha256`: hash of the list of files held
- `api_total_check`: result of the comparison with the OFR's total series
- `kind_table_sha256`: hash of the classification table

**checks.csv**: The checks run by the build and their results.
- `check_id, description, expected, observed, status`: PASS, WARN or FAIL

**fetch_log.csv**: Every request the fetch made.
- `utc_time, host, path, status, bytes, sha256`: when, to which OFR host, for which file, with what result

## Source and copyright

Office of Financial Research, "OFR Money Market Fund Monitor", refreshed monthly, https://www.financialresearch.gov/money-market-funds/. The OFR's legal notice says works of its federal employees carry no copyright and asks for credit; the OFR's own notes say its parent and country mapping draws on regulatory filings, company disclosures and commercial data, so the raw chart files are not republished here and only derived statistics are. Build script: `bin/mmf_nonus_banks.py`. Provenance, labels, builder decisions and the request record are in `SOURCES.md`.
