# UK customs declarations of semi-manufactured gold to China and Hong Kong

This table counts the kilograms of gold that UK customs export declarations sent to China and Hong Kong each month, from HMRC trade statistics. It counts declared shipments, not buyers, and it is not a measure of central-bank buying.

CN (the Combined Nomenclature, the UK tariff's classification) 71081310 is the tariff's own heading for semi-manufactured gold (bars, rods, wire, sections, plates, sheets and strips over 0.15 mm). The kilograms are the declared net mass that HMRC (HM Revenue and Customs, the UK customs authority) records on export declarations to non-EU destinations; the latest HMRC pull in this folder is dated 2026-10-19 and its newest month is 2026-08.

## What it leaves out

- **London vault transfers.** Gold that changes owner by book entry inside a London vault never appears on a customs declaration. This is a physical-movement series. It is not the change-of-ownership series of the ONS (Office for National Statistics).
- **The May 2016 break.** From May 2016 warehouse and free-zone movements are outside the figures, so this series is not an upper bound, ceiling or cap on metal leaving the UK. Months before May 2016 are general trade and are not like-for-like with later months; every annual and window row carries a `trade_system` column (`general`, `special` or `mixed` for 2016). HMRC's help page for its data (https://www.uktradeinfo.com/trade-data/help-with-using-our-data, read by hand on 19 Oct 2026) says that from May 2016 it changed how it compiles non-EU statistics, "from the general trade to the special trade system", and that special trade excludes goods placed in customs warehouses. That page does not mention free zones; the free-zone exclusion comes from the project's written specification and has not been checked against an HMRC page.
- **Monetary gold** (CN 71082000) is suppressed by HMRC and is never in these figures.
- **Other routes into China.** Gold reaches China from Chinese mines, from Switzerland and from elsewhere, none of which this series sees.
- **Onward movement from Hong Kong.** Hong Kong is a trading hub and is not the reserve account of the People's Bank of China (PBoC); what leaves it for the mainland is outside this table.

## Why the figures are not compared with other sources

This folder prints three other magnitudes beside the UK kilograms, each in its own column and table, and computes no ratio, multiple or share of any two of them. The reasons are definitional. HMRC records gross physical declarations. The central-bank total of the World Gold Council (WGC) counts net additions and includes an estimate for reserves that governments do not report. Hong Kong is not the PBoC's reserve account. China's reserve change, reported by the State Administration of Foreign Exchange (SAFE), is a stock change. UK declarations and SAFE's reported additions measure different things, so a UK figure larger or smaller than SAFE's is expected either way and is not a comparison.

## The latest result

**UK declared net mass of CN 71081310, tonnes** (kilograms divided by 1,000; HMRC pull 2026-10-19). `provisional` counts the months of the year that are within 18 months of first publication; a year with a blank month has no total. Hong Kong and China are separate columns; `CN_HK` is their sum.

| year | trade_system | China | Hong Kong | China + Hong Kong | provisional months | blank months |
|---|---|---:|---:|---:|---:|---:|
| 2019 | special | 184.782 | 6.001 | 190.783 | 0 | 0 |
| 2020 | special | 9.900 | 12.031 | 21.931 | 0 | 0 |
| 2021 | special | 0.000 | 12.672 | 12.672 | 0 | 0 |
| 2022 | special | 300.165 | 260.169 | 560.334 | 0 | 0 |
| 2023 | special | 281.283 | 111.605 | 392.888 | 0 | 0 |
| 2024 | special | 382.786 | 26.044 | 408.830 | 0 | 0 |
| 2025 | special | 186.866 | 30.304 | 217.170 | 10 | 0 |
| 2026 (2026-01 to 2026-08) | special | 193.084 | 27.771 | 220.855 | 8 | 0 |

**Switzerland's exports of HS (Harmonized System) 710812 (unwrought gold), as reported to UN Comtrade, tonnes, completed years only.** HS 710812 and the UK's CN 71081310 are different headings, and Switzerland records imports by origin, so these are not a mirror of the UK figures and nothing here adds or compares the two.

| year | China | Hong Kong | China + Hong Kong | status |
|---|---:|---:|---:|---|
| 2012 | blank | 137.662 | blank | partial |
| 2013 | 249.881 | 955.964 | 1205.845 | complete |
| 2014 | 213.148 | 377.240 | 590.388 | complete |
| 2015 | 292.125 | 493.555 | 785.680 | complete |
| 2016 | 442.195 | 320.682 | 762.877 | complete |
| 2017 | 316.697 | 244.482 | 561.179 | complete |
| 2018 | 431.950 | 222.470 | 654.420 | complete |
| 2019 | 180.569 | 73.201 | 253.770 | complete |
| 2020 | blank | blank | blank | partial |
| 2021 | blank | 79.065 | blank | partial |
| 2022 | 478.176 | 45.481 | 523.657 | complete |
| 2023 | 444.108 | 131.822 | 575.930 | complete |
| 2024 | blank | 90.145 | blank | partial |
| 2025 | blank | 18.769 | blank | partial |

**Context magnitudes, tonnes, each in its own column.** UK: declared net mass of CN 71081310 to China and Hong Kong. SAFE: China's reported change in official gold reserves, as the gold ledger in `data/gold/` carries it. WGC: the World Gold Council's published central-bank total for the full year. Gap: the gold ledger's published WGC total minus the official total based on the IMF (International Monetary Fund), which the ledger itself says is not a measure of reserves that governments do not report. A blank is stated in `note` in `context.csv`.

| window | trade_system | UK China + Hong Kong | SAFE reported change | WGC central banks | WGC minus IMF gap |
|---|---|---:|---:|---:|---:|
| 2019 | special | 190.783 | 95.799 | blank | blank |
| 2020 | special | 21.931 | 0.000 | blank | blank |
| 2021 | special | 12.672 | 0.000 | blank | blank |
| 2022 | special | 560.334 | 62.207 | 1081.900 | 1110.258 |
| 2023 | special | 392.888 | 224.878 | 1050.800 | 541.589 |
| 2024 | special | 408.830 | 44.167 | 1092.400 | 830.336 |
| 2025 | special | 217.170 | 26.749 | 863.300 | 557.257 |
| 2026_to_2026-08 | special | 220.855 | 80.247 | blank | blank |

## Blank months

The two sources are treated differently, on purpose. A month for which HMRC has no row for a partner is written as **zero** (`status` `no_rows`): HMRC publishes every non-zero partner-month and no gold row has ever been suppressed or placed under a confidential country, which is an observed behaviour (19 Oct 2026) and not an HMRC statement. If any 7108 row in a month is suppressed or sits under a confidential country, the China, Hong Kong and all-destination cells of that month are blank (`unattributable`), and a suppressed partner row is blank (`suppressed`). A Comtrade month with no record is **blank**, never zero, because Comtrade is a reporter-submitted mirror and absence there is not evidence of zero. An annual total is blank when any of its months is blank. For the UK series `net_mass_kg_known_months` then holds the sum of the known months; for the Swiss series it stays blank, so that no single month can be recovered by subtraction.

## Columns

`monthly.csv`: `month`; `partner` (`CN` China, `HK` Hong Kong, `CN_HK` their sum, `CH` Switzerland as an upstream refining leg, `ALL_NON_EU` every non-EU destination); `series` (`cn71081310` is semi-manufactured gold (bars, rods, wire, sections, plates, sheets and strips over 0.15 mm); `other` is CN 71081200 plus 71081380; `powder` is CN 71081100, kept in no other series); `net_mass_kg` is the sum of HMRC `NetMass` over ports and codes, over rows with `SuppressionIndex` 0; `supp_unit_div_1000` is the supplementary quantity ÷ 1,000 (grams under the CN), not reconciled to net mass, and it is not used in any result; `rows_n`; `status`; `trade_system`; `provisional`; `vintage` (the pull date). Quantities published by WITS (the World Bank's World Integrated Trade Solution) are supplementary quantities and differ from net mass by kilograms (China 2024: 382,802 against 382,786 kg, as read by a reviewer on WITS and not re-read here).

`annual.csv`: the same by calendar year, with `months_n`, `months_blank`, `net_mass_kg_known_months` and `provisional_months`. `swiss_mirror_annual.csv`: Swiss HS 710812 by completed year, `net_wgt_estimated_months` counting months Comtrade flags as estimated, `comtrade_annual_kg` the annual record and `monthly_sum_minus_annual_kg` the difference of the two. `context.csv`: the magnitudes above. `revisions.csv`: every changed cell between two HMRC pulls, append-only. `summary.csv`: the pre-registered descriptive questions, with `blind`. `checks.csv`: the checks. `fetch_log.csv`: every request.

## One worked row

China, CN 71081310, January 2024: HMRC holds a row for port 428 of 25046 kg and a row for port 434 of 0 kg; their sum is the single `monthly.csv` row `2024-01,CN,cn71081310,25046,25049.455,2,ok,special,no,2026-10-19`.

## Provenance

Contains public sector information licensed under the Open Government Licence v3.0. HMRC Overseas Trade Statistics (`api.uktradeinfo.com`), non-EU exports, retrieved 2026-10-19. Swiss figures: UN Comtrade public preview (`comtradeapi.un.org`), reporter Switzerland, retrieved 2026-10-19. UN Comtrade data are for internal use and may not be re-disseminated without the permission of the United Nations Statistics Division (UNSD), except limited amounts in a few tables; only completed-year totals per partner are published here, and monthly Swiss values stay in an ignored cache. The first Comtrade backfill is about 176 calls (about 18 minutes at 6 seconds) and may end on a 429, in which case the build ships UK-only and says so. SAFE: "Official Reserve Assets"; WGC: Gold Demand Trends; both as the gold ledger (`data/gold/`) cites them. Build decisions, including one fix made after the first build, are listed in [SOURCES.md](SOURCES.md).
