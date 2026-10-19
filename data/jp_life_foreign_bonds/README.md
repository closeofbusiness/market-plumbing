# Japanese life insurers' foreign long-term bonds: monthly acquisitions and dispositions

Japanese life insurers' monthly acquisitions and dispositions of foreign bonds issued with an original maturity of more than one year, as reported to the Ministry of Finance by designated major investors, with other investor types beside them. These are recorded acquisitions and dispositions, redemptions included. They do not show why any investor acquired or disposed of bonds, or any effect on prices.

**Coverage.** Designated major investors only: the survey is narrower than balance-of-payments portfolio investment and is released earlier (the month after the month it covers, against the month after next). The total block is therefore `designated_reporters_total`, never all residents.

## The latest result

Life insurers, long-term debt (monthb3), Final Update 2026-10-08, latest published month 2026-09. Amounts are ¥ billion (the file's ¥100 million divided by 10); plus is net acquisition and minus is net disposition. `basis` is explained under the breaks below. The rows are sums of the months in the file.

The windows used below and in `questions.csv`: W0 is 2014 to 2018, W1 is 2019 to 2023, W2 runs from March 2024 to the latest month, and W2b from April 2024.

Life insurers' net, long-term debt: +19.04 trillion yen over W0 (18 of 60 months of net disposition), −14.23 trillion yen over W1 (39 of 60) and −3.84 trillion yen over W2 (23 of 31).

| period type | period | basis | months | acquisitions | dispositions | net |
|---|---|---|---:|---:|---:|---:|
| CY | 2014 | new_from_2014 | 12 | 12201.4 | 10030.6 | 2170.4 |
| CY | 2015 | new_from_2014 | 12 | 12065.5 | 9601.7 | 2463.4 |
| CY | 2016 | new_from_2014 | 12 | 22815.7 | 12566.6 | 10249.0 |
| CY | 2017 | new_from_2014 | 12 | 15454.6 | 13645.5 | 1809.2 |
| CY | 2018 | new_from_2014 | 12 | 21637.1 | 19292.6 | 2344.5 |
| CY | 2019 | new_from_2014 | 12 | 16299.1 | 13607.2 | 2692.0 |
| CY | 2020 | new_from_2014 | 12 | 13652.9 | 15507.9 | -1854.9 |
| CY | 2021 | new_from_2014 | 12 | 11925.1 | 12679.7 | -754.3 |
| CY | 2022 | new_from_2014 | 12 | 15614.4 | 27078.5 | -11464.0 |
| CY | 2023 | new_from_2014 | 12 | 12122.3 | 14970.1 | -2847.9 |
| CY | 2024 | new_from_2014 | 12 | 11856.4 | 13533.9 | -1677.7 |
| CY | 2025 | new_from_2014 | 12 | 9131.2 | 9803.8 | -672.6 |
| FY | 2014 | new_from_2014 | 12 | 11505.5 | 9725.6 | 1779.4 |
| FY | 2015 | new_from_2014 | 12 | 14955.7 | 9431.5 | 5523.8 |
| FY | 2016 | new_from_2014 | 12 | 21223.4 | 13484.5 | 7738.7 |
| FY | 2017 | new_from_2014 | 12 | 19662.6 | 16237.3 | 3425.6 |
| FY | 2018 | new_from_2014 | 12 | 18727.7 | 17573.1 | 1154.7 |
| FY | 2019 | new_from_2014 | 12 | 15143.3 | 14240.7 | 902.6 |
| FY | 2020 | new_from_2014 | 12 | 13484.4 | 14653.3 | -1168.8 |
| FY | 2021 | new_from_2014 | 12 | 13499.4 | 13868.6 | -368.9 |
| FY | 2022 | new_from_2014 | 12 | 14252.8 | 26882.0 | -12629.1 |
| FY | 2023 | new_from_2014 | 12 | 11428.9 | 13262.8 | -1834.0 |
| FY | 2024 | new_from_2014 | 12 | 11139.5 | 13028.8 | -1889.7 |
| FY | 2025 | new_from_2014 | 12 | 9599.3 | 10809.8 | -1210.3 |
| CY_YTD | 2026-01..2026-09 | new_from_2014 | 9 | 6870.0 | 8627.1 | -1757.0 |
| FY_YTD | 2026-04..2026-09 | new_from_2014 | 6 | 4199.3 | 4739.5 | -540.1 |

**The October 2026 rule.** The Net cell of life insurers' long-term debt for October 2026 is compared with a rule registered on 2026-10-19, before the print: point −¥78.2 billion, range −¥288.6 billion to +¥74.6 billion (the 24 monthly Net cells from 2024-10 to 2026-09; point is the median, range the 3rd to the 22nd order statistic; a print equal to an edge is inside). Status: PENDING: October 2026 is not yet published in any cached vintage; MoF publishes it on 10 Nov 2026 at 08:50 JST. This is a frozen rule on this net, redemptions included. It is not a forecast of sales.

## Defined terms

- **Acquisition**: an increase in holdings of foreign long-term debt (MoF: an increase of assets).
- **Disposition**: sales, redemptions and other reductions in holdings (the file's term); redemptions of overseas government bonds are included, MoF FAQ A5. Whether redemptions of other bonds are included is not stated.
- **Net acquisition and net disposition**: the file's Net cell. Plus is net acquisition; minus is net disposition (file Note 2).
- **Recorded at contract**: purchases and sales on the execution date, redemptions on the redemption date (MoF FAQ A6). These are flows of contracts, not holdings.
- **Long-term debt**: bonds issued with an original maturity of more than one year, classified by the residence of the issuer, not by currency.
- **Designated reporters**: the designated major investors named by the Finance Minister.
- **Dealers** (`fi_firms`, financial instruments firms) and their share of reported gross contracts: the share is of all designated reporters' acquisitions or dispositions in a window. Life insurers' share of reported gross contracts is dealer-inclusive and is printed beside the dealers' own.
- **Trust accounts** (`trust_accounts`): the trust accounts of banks and trust banks.
- **Investment trusts** (`inv_trust`): investment trust management companies, including asset management companies (file Note 4); for the classification see BoJ FAQ No. 14.
- **Fiscal year**: the Japanese fiscal year, April to March, labelled by its starting year.

## What this series cannot say

- why any investor acquired or disposed of bonds, or any effect on a yield, spread or exchange rate;
- how much of a disposition was a sale and how much a redemption;
- anything about US Treasuries alone, about currency, or about hedged against unhedged bonds (the file mixes all three);
- anything about holdings (these are flows of contracts);
- anything about bonds held through funds: since 2014 fund shares sit with equities in monthb2, with no split between bonds and equities.

## Breaks and the March 2024 note

- **January 2014.** From 2014 open-end contractual investment trusts, previously in long-term debt, are counted in equity and investment fund shares, and the five-sector split is not applied to earlier months. MoF did not restate earlier months; the questions in `questions.csv` use 2014 onward only.
- **October 2007.** Securities companies and investment trust companies became financial instruments firms and investment trust management companies (file Note 3); months to September 2007 use the old categories.
- **Sign.** The file's own: plus is net acquisition. Before January 2014 MoF recompiled only the sign of the net for earlier months; the file confirms the identity Net = Acquisition − Disposition within 1 unit from 2014 and within 4 before. The English index page's older sign banner is stale and is not used.
- **March 2024.** The 19 March 2024 decision took effect on 21 March, so most of March 2024 is before it. Window W2 starts in March 2024 as registered; W2b starts in April 2024 and leaves it out.

## A worked row

**March 2024, life insurers: 11,783 − 13,790 = −2,007** (¥100 million). MoF rounds each cell separately, so Net can differ from the subtraction by 1.

## Columns

- `monthly.csv`: `month` (YYYY-MM); `instrument` (`ltd` long-term debt = monthb3, `equity_funds` = monthb2, `std` short-term debt = monthb4, `all` = monthb1); `sector`; `acquisition_100m_yen`, `disposal_100m_yen` (the file's disposition) and `net_100m_yen` in ¥100 million, the Net cell as MoF prints it; `basis` (`old_to_2013` or `new_from_2014`).
- `annual.csv`: `period_type` (CY calendar year, FY fiscal year April to March labelled by its starting year, CY_YTD and FY_YTD year to date); `period`; `basis` (also `mixed_2013_2014` for FY2013 and `mixed_2007` for 2007); `months` summed; the three sums; `file_total_net_100m_yen` (the file's own CY or FY Net cell) and `diff_100m_yen` (sum of months minus the file's cell).
- `boj_dates.csv`: `decision_date`, `effective_date`, `month`, `action`, `phrase` (under 15 words), `url` and the `sha256` of the cached statement (Bank of Japan, Statement on Monetary Policy).
- `questions.csv`: `run_label` (instrument, vintage and latest month), `question` (Q1 to Q6), `window`, `instrument`, `sector`, `statistic`, `value`, `unit` and `denominator`; `notable` is `yes` or `no` where a rule exists.
- `forecast_score.csv`: The registered point, low and high and the October 2026 Net cell, in file units; `status` (PENDING, INSIDE, BELOW, ABOVE or LATE_VINTAGE); `of_record`; the recomputed band where a base month is revised.
- `vintages.csv`: One row per cached MoF file: Final Update date, retrieval time, bytes, sha256, published months and the last month.
- `revisions.csv`: Differences between consecutive vintages of the same file for the six committed sectors, with old and new values; `kind` is `revised`, `new` (a month or cell that was blank) or `removed`.
- `checks.csv`: `check_id`, what was tested, what was expected, what was observed, and PASS, FAIL, WARN or INFO.
- `pins.csv`: Published values the spec pins, with their source and unit.
- `fetch_log.csv`: One row per request: UTC time, host, path, status, bytes and sha256.

## Provenance

Source: Ministry of Finance Japan, "International Transactions in Securities" (designated reporters, monthly; monthb1-b4.csv), https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/, PDL1.0, retrieved 2026-10-19. Processed by the Third Derivative project (re-laid out and summed; values unchanged).

Bank of Japan, Statement on Monetary Policy, on the dates in `boj_dates.csv`; only dates and phrases under 15 words are cited.

Build decisions, including two fixes made after the first build, are listed in [SOURCES.md](SOURCES.md).

Vintages cached (file, Final Update, sha256 first 12): monthb3 2026-10-08 5c70e53f3c95; monthb1 2026-10-08 f9d96ca4553f; monthb2 2026-10-08 eb8570560c63; monthb4 2026-10-08 751df62b428c.
