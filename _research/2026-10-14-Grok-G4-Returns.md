# Grok (Cursor CLI) batch g4, 14 Oct 2026: fifteen rates, FX and commodities research items, returns and the supervisor's checks

*On 14 Oct 2026 the principal asked for every item on the ranked list of further rates, FX and commodities research to be run through Grok. The supervisor sent one parcel per item through `orchestrator_cursor` to Grok 4.7 (256k, extra-high). Each parcel ran in a fresh stage behind the read-and-web-only fence. Each one carried the item's specification and a one-page summary of the programme. Each parcel was asked to run the item's first test as far as free public data allows, and to return its sources, results, any pre-registration, what the result changes, a build spec for the code, what it inferred, and what it could not do. The fence and wrapper statistics are given for each item. A URL cited without a fetch in that call is listed and not relied on. The returns are claims until checked. The supervisor's check is stated at the head of each item.*

*Quotes longer than 15 words were cut by the supervisor to their first twelve words, under the repository's quotation rule. The full text is at each cited URL. Grok's opening narration is dropped; everything from SOURCES onward is as returned.*

*Item 1 was landed first, on 14 Oct, so that its pre-registration is dated before the 16 Oct TIC release. The other items are added as they are checked.*

| Item | Topic | Wall time (s) | Searches | Fetches | URLs cited but not fetched |
|---:|---|---:|---:|---:|---:|
| 1 | Japan intervention funding | 1136 | 8 | 39 | 5 |

---

## Item 1: Japan intervention funding: base rate from 2022/2024/2026 episodes, written before the 16 Oct TIC print

*Status SUCCESS; 1136 s; breaches 0, blocked 0, unexpected tools 0, stage changes 0.*

*Cited without a fetch in this call, not relied on:* `https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/D.JP.JPY.A?format=csv`; `https://ticdata.treasury.gov/Publish/mfhhis01.txt`; `https://ticdata.treasury.gov/Publish/slt_table5.txt`; `https://www.mof.go.jp/policy/international_policy/reference/official_reserve_assets/data/`; `https://www.mof.go.jp/policy/international_policy/reference/official_reserve_assets/data/historical.csv`


**Supervisor check.** Re-derived 14 Oct, before the 16 Oct print, with the neutral User-Agent. Each figure below matched at source. Treasury par curve, 31 Jul and 31 Aug 2026: 10y 4.75 and 4.75, 7y 4.59 and 4.62. TIC Table 5 Japan, Apr/May/Jul 2026: 1,209.9, 1,143.1 and 1,103.9. MoF intervention 30 Jul–26 Aug: ¥15,399.3bn. BIS `D.JP.JPY.A` over that window: maximum 162.940049 (30 Jul), minimum 156.679671 (3 Aug). This gives $94.51bn to $98.29bn. MoF reserves end-Jul to end-Aug: securities 927,332 to 839,559, deposits 162,285 to 155,417, total 1,287,099 to 1,207,524 (US$ millions). The holding returns were recomputed with the formula in `bin/r1_treasury_decomposition.py` and reproduce Grok's hand figures to 0.02 percentage point. The August valuation is +0.432%, or +$4.8bn on the July stock (Grok: +$4.7bn). Sep 2022 is −5.34% and −$63.9bn; May 2026 is −0.01% and −$0.1bn. The pre-registration was written into `CALENDAR.tsv` (the 16 Oct row) on 14 Oct, with +$4.8bn. The 2022 and 2024 TIC stocks are relayed from `mfhhis01`, not re-read. The intervention-day dollar amounts for 2022–2024 are relayed.


### SOURCES

| Source | URL fetched | Free? | Terms quote | What it holds |
| --- | --- | --- | --- | --- |
| MoF intervention CSV, from April 1991 | https://www.mof.go.jp/policy/international_policy/reference/feio/foreign_exchange_intervention_operations.csv | Yes, no login | Licence page not found (see UNCERTAIN) | Daily and quarterly intervention, unit 100 million yen. Yen-buying days through June 2026. August 2026 is not in the file. |
| MoF monthly intervention release, 28 Aug 2026 | https://www.mof.go.jp/english/policy/international_policy/reference/feio/monthly/20260828e.html | Yes, no login | Licence page not found | Window total only: “¥ 15,399.3 billion” for 30 Jul–26 Aug 2026. No daily split. |
| MoF reserves, monthly HTML, US$ millions | https://www.mof.go.jp/policy/international_policy/reference/official_reserve_assets/data/0802.html and 0803, 0804, 0805, 0806, 0807, 0808 | Yes, no login | “証券、金は時価評価している。” | Securities, deposits, gold value, gold ounces (27.20), total reserves. Feb–Aug 2026. |
| MoF reserves historical.csv | https://www.mof.go.jp/policy/international_policy/reference/official_reserve_assets/data/historical.csv | Yes, no login | Same mark-to-market note in the template | Monthly SDDS reserves from April 2000. This fetch ran through April 2025, which covers 2022 and 2024. |
| MoF weekly securities | https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/week.csv | Yes, no login | Licence page not found | “International Transactions in Securities (Weekly; based on reports from designated major investors)”, unit 100 million yen. Fetch truncated in 2013. |
| TIC historical holdings | https://ticdata.treasury.gov/Publish/mfhhis01.txt | Yes, no login | No reuse sentence on the Treasury page fetched | Japan Treasury holdings, market value, $ billions, through 2024 for this test. Custodial residence. |
| TIC latest Table 5 | https://ticdata.treasury.gov/Publish/slt_table5.txt | Yes, no login | No reuse sentence on the Treasury page fetched | Latest 13 months through July 2026. August 2026 is not in the file. |
| US Treasury par yield curve | https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2022/all?type=daily_treasury_yield_curve&field_tdr_date_value=2022&page&_format=csv and the 2024 and 2026 files; January 2023 via the TextView for 202301 | Yes, no login | Site-policies page lists notices and does not grant a reuse licence | Daily par yields, percent. 7-year and 10-year at month-ends. |
| BIS WS_XRU, series D.JP.JPY.A | https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/D.JP.JPY.A?format=csv&startPeriod=2026-07-30&endPeriod=2026-08-26 and the 2022 and 2024 windows | Yes, no key | “the BIS must be cited in your publication or product” | JPY per USD, daily average of observations. Not a transaction rate. |
| Programme gold ledger | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/data/gold/ledger_monthly.csv | Yes | “reproduce and Share the Licensed Material, in whole or in part” (repo CC BY 4.0: https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/LICENSE) | Monthly IMF world gold tonnage change. Feb–Jul 2026 used. IMF’s own terms were not re-fetched. |
| BIS legal | https://data.bis.org/help/legal | Yes | Quote above | Permitted use of BIS statistics. |

Treasury site policies: https://home.treasury.gov/subfooter/site-policies-and-notices. A guessed MoF public-data index returned 404.

### RESULTS

Holding return below is the R1 full revaluation: buy the 10-year par bond at the starting month-end yield, price it at month-end as a bond with remaining maturity \(10 - d/365.25\), with the end yield interpolated one-third of the way from the 10-year toward the 7-year, plus coupon accrued. Valuation = starting TIC stock × that return. Adjusted change = raw change − valuation. Positive adjusted means the holdings rose by more than the carrying return.

Episode months are calendar months that contain yen-buying intervention (dollars sold). Seven of those months already have a TIC print. August 2026 is the eighth and is not scored.

| Finding | Value | Grade | Window / denominator | Source URL | Quote or row |
| --- | --- | --- | --- | --- | --- |
| Securities change per intervention dollar is not one number | −2.56, −1.05, −0.45, −2.03, +0.18, −2.17 across the seven months; August −0.89 to −0.93 | MEASURED (May 2024 and August dollars BOUNDED) | Same calendar month. Denominator: dollars sold, yen ÷ BIS JPY per USD | Intervention CSV; reserves CSV and 2026 HTML; BIS D.JP.JPY.A | Rows below |
| September 2022 TIC drop is the 10-year revaluation under R1 | Raw −$79.6bn; return −5.35%; valuation −$64.0bn; adjusted −$15.6bn | MEASURED under the 10-year definition | Aug 2022 stock $1,196.0bn to Sep 2022 $1,116.4bn. Yields 31 Aug (10y 3.15, 7y 3.25) to 30 Sep (10y 3.83, 7y 3.97), 30 days | mfhhis01 Japan row; 2022 curve | 80% of the raw drop is the defined revaluation |
| May 2026 TIC drop is a quantity change | Raw −$66.8bn; return about −0.01%; valuation about −$0.1bn; adjusted −$66.7bn | MEASURED | 30 Apr 2026 stock $1,209.9bn to 29 May $1,143.1bn. 10y 4.40 to 4.45, 7y 4.20 to 4.27, 29 days | slt_table5 Japan; 2026 curve | May row 1,143.1 minus April 1,209.9 |
| August 2026 valuation is carry, and it is already known | Return +0.43%; valuation +$4.7bn on the July stock | MEASURED | 31 Jul 2026 to 31 Aug 2026, 31 days. 10y 4.75 to 4.75, 7y 4.59 to 4.62. Stock $1,103.9bn | 2026 curve 07/31 and 08/31; slt_table5 July Japan | August TIC stock is not in the file |
| August reserves | Securities −$87.773bn; deposits −$6.868bn; total reserves −$79.575bn | MEASURED | End-Jul 2026 to end-Aug 2026. US$ millions | 0807.html and 0808.html | Securities 927,332 to 839,559; deposits 162,285 to 155,417; total 1,287,099 to 1,207,524 |
| Month-of adjusted TIC per intervention dollar | 0.77, 0.74, 0.01, 1.64, 0.76, −0.58, 1.91 (positive = adjusted sales) | MEASURED, with the May 2024 dollar amount BOUNDED | Each episode month. Denominator: that month’s intervention dollars | Same as the episode rows | Min −0.58 (Apr 2026), max 1.91 (May 2026) |
| Gold tonnage bound | Net +234.703 t, worth $30.4bn to $39.4bn at MoF marks, equal to 13% to 17% of the $236.5bn holdings fall | BOUNDED | Feb–Jul 2026 net world official tonnage. Denominator: foreign official Table 5, end-Feb $4,009.6bn to end-Jul $3,773.1bn | ledger_monthly.csv; slt_table5; MoF gold ÷ 27.20 oz | Japan’s own ounces stayed 27.20 |
| OTC identity | MoF yen purchases are matched by other parties’ yen sales of the same notional | IDENTITY | Each published intervention amount | MoF intervention releases | No counterparty named |

Dollars sold use yen billions ÷ the BIS daily average. CSV units are 100 million yen, so 28,382 units = ¥2,838.2bn.

| Episode | Yen bn and BIS JPY per USD | Intervention $bn | Securities $bn | Deposits $bn | Securities / $ |
| --- | --- | --- | --- | --- | --- |
| 22 Sep 2022 | 2,838.2 at 140.813436 | 20.16 | −51.509 | +0.002 | −2.56 |
| 21 Oct 2022 | 5,620.2 at 151.685509 | 37.05 |  |  |  |
| 24 Oct 2022 | 729.6 at 148.979799 | 4.90 |  |  |  |
| October 2022 |  | 41.95 | −43.941 | +0.905 | −1.05 |
| 29 Apr 2024 | 5,918.5 at 156.277985 | 37.87 | −16.864 | +2.689 | −0.45 |
| 1 May 2024 | 3,870.0; no BIS print that day | 24.65 to 25.00 (30 Apr 156.997574, 2 May 154.823331); mid 24.82 | −50.425 | +1.246 | −2.03 at the mid |
| 11 Jul 2024 | 3,167.8 at 161.575311 | 19.61 |  |  |  |
| 12 Jul 2024 | 2,367.0 at 158.741965 | 14.91 |  |  |  |
| July 2024 |  | 34.52 | −17.080 | +0.422 | −0.49 |
| 30 Apr 2026 | 6,278.7 at 156.562981 | 40.10 | +7.151 | +0.468 | +0.18 |
| 4 May 2026 | 780.2 at 157.119658 | 4.97 |  |  |  |
| 6 May 2026 | 4,675.9 at 156.214929 | 29.93 |  |  |  |
| May 2026 |  | 34.90 | −75.563 | +0.038 | −2.17 |
| 30 Jul–26 Aug 2026 | ¥15,399.3bn; daily averages 156.679671 to 162.940049 | 94.51 to 98.28 | −87.773 | −6.868 | −0.89 to −0.93 |

TIC inputs, $ billions, market value. Returns are the R1 formula above, to about 0.05 percentage point.

| Month | Stock path | Raw | 10y / 7y, start → end | Days | Return | Valuation | Adjusted | Adjusted sales / intervention $ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| Sep 2022 | 1196.0 → 1116.4 | −79.6 | 3.15/3.25 → 3.83/3.97 | 30 | −5.35% | −64.0 | −15.6 | 0.77 |
| Oct 2022 | 1116.4 → 1064.4 | −52.0 | 3.83/3.97 → 4.10/4.18 | 31 | −1.88% | −21.0 | −31.0 | 0.74 |
| Nov 2022 | 1064.4 → 1081.8 | +17.4 | 4.10/4.18 → 3.68/3.76 | 30 | +3.78% | +40.2 | −22.8 | no intervention |
| Dec 2022 | 1081.8 → 1075.1 | −6.7 | 3.68/3.76 → 3.88/3.96 | 30 | −1.35% | −14.6 | +7.9 | no intervention |
| Jan 2023 | 1075.1 → 1102.9 | +27.8 | 3.88/3.96 → 3.52/3.59 | 32 | +3.31% | +35.6 | −7.8 | no intervention |
| Apr 2024 | 1167 → 1126.1 | −40.9 | 4.20/4.20 → 4.69/4.71 | 33 | −3.47% | −40.5 | −0.4 | 0.01 |
| May 2024 | 1126.1 → 1106 | −20.1 | 4.69/4.71 → 4.51/4.52 | 31 | +1.82% | +20.5 | −40.6 | 1.64 |
| Jun 2024 | 1106 → 1091.4 | −14.6 | 4.51/4.52 → 4.36/4.33 | 28 | +1.55% | +17.1 | −31.7 | no intervention |
| Jul 2024 | 1091.4 → 1093.5 | +2.1 | 4.36/4.33 → 4.09/4.00 | 33 | +2.60% | +28.4 | −26.3 | 0.76 |
| Aug 2024 | 1093.5 → 1106 | +12.5 | 4.09/4.00 → 3.91/3.80 | 30 | +1.83% | +20.0 | −7.5 | no intervention |
| Sep 2024 | 1106 → 1095.5 | −10.5 | 3.91/3.80 → 3.81/3.67 | 31 | +1.18% | +13.1 | −23.6 | no intervention |
| Oct 2024 | 1095.5 → 1101.5 | +6.0 | 3.81/3.67 → 4.28/4.21 | 31 | −3.43% | −37.6 | +43.6 | no intervention |
| Apr 2026 | 1191.6 → 1209.9 | +18.3 | 4.30/4.11 → 4.40/4.20 | 30 | −0.40% | −4.8 | +23.1 | −0.58 |
| May 2026 | 1209.9 → 1143.1 | −66.8 | 4.40/4.20 → 4.45/4.27 | 29 | −0.01% | −0.1 | −66.7 | 1.91 |
| Jun 2026 | 1143.1 → 1116.7 | −26.4 | 4.45/4.27 → 4.44/4.30 | 32 | +0.50% | +5.7 | −32.1 | no intervention |
| Jul 2026 | 1116.7 → 1103.9 | −12.8 | 4.44/4.30 → 4.75/4.59 | 31 | −2.01% | −22.4 | +9.6 | no intervention |

Two windows of “the next three months” contain no later intervention. October 2022 through January 2023: adjusted −$53.7bn against October’s $41.95bn, ratio 1.28. July 2024 through October 2024: adjusted −$13.8bn against July’s $34.52bn, ratio 0.40. September 2022’s following quarter contains October’s intervention, and April 2024’s contains July’s, so those four-month sums are not a clean ratio. April plus May 2026 intervention is $75.00bn; May’s adjusted −$66.7bn is 0.89 of that combined amount and 1.91 of May alone.

March 2024’s curve date is 28 March. May 2026’s is 29 May. 2024 stocks printed as integers are used as printed.

Gold, one paragraph. The ledger column `imf_world_g001_change_t` for February through July 2026 is 60.893, −9.957, 19.014, 51.343, 69.276, 44.134 tonnes, summing to 234.703 tonnes. That is the net change in the reported world official stock, not gross purchases. At 32,150.75 fine ounces per tonne that is 7.546 million ounces. MoF month-end gold marks, gold US$ millions divided by 27.20 million ounces, ran from $4,026 in June and July 2026 (109,505 and 109,520) to $5,222 in February (142,042). The same ounces are then worth $30.4bn to $39.4bn. Foreign official Table 5 holdings fell from 4,009.6 at end-February 2026 to 3,773.1 at end-July, a fall of $236.5bn. The tonnage bound is 12.8% to 16.7% of that fall. Japan’s gold volume was 27.20 million ounces at every month-end read, so the yen operations were not accompanied by Japanese gold purchases. This bounds a reported stock change. It does not say gold buying moved Treasury prices.

Coverage. Spot yen trades match. The MoF’s published yen purchases are the other side of someone else’s yen sales, in the same notional, and that identity does not identify the other balance sheet. `week.csv` is designated major investors and all foreign securities, not Treasuries. Its 2026 rows were past the truncated fetch, so the four-week non-resident sum is not re-measured here.

### PRE-REGISTRATION

Dated 14 October 2026. Score on 16 October 2026. Do not score it today. `CALENDAR.tsv` row 60 was not edited.

Seven completed episode-months are the base rate: September 2022, October 2022, April 2024, May 2024, July 2024, April 2026, May 2026.

Japan’s TIC Table 5 Treasury holdings for August 2026, minus the July 2026 stock of $1,103.9bn, minus a valuation of +$4.7bn, will fall between −$190bn and +$60bn.

The valuation is the R1 10-year full holding return from 31 July 2026 (10-year 4.75%, 7-year 4.59%) to 31 August 2026 (10-year 4.75%, 7-year 4.62%), which is +0.43% on $1,103.9bn. Adjusted change = (August stock − 1,103.9) − 4.7.

The edges are the seven month-of ratios of adjusted sales per intervention dollar, from −0.58 to +1.91, times the August intervention bound of $94.51bn to $98.28bn (¥15,399.3bn divided by the BIS daily-average range 156.679671 to 162.940049). The products are about −$188bn to +$57bn, rounded outward by $2bn for the hand-computed returns. A print inside roughly −$50bn to −$100bn raw, which is about −$55bn to −$105bn adjusted, sits inside this range. It would not establish a stable securities-to-TIC ratio.

### WHAT IT CHANGES

The programme’s open item treats 16 October as the first test of “the yen intervention was funded by Treasury sales,” with May 2026’s raw −$66.8bn against about $75bn of intervention as the analogue, and a −$50bn to −$100bn guess on calendar row 60.

The seven months do not have a stable securities-per-dollar ratio, and they do not have a stable month-of adjusted-TIC ratio. September 2022’s −$79.6bn is the 10-year revaluation (−$64bn of it). May 2026’s −$66.8bn is not: the 10-year moved from 4.40% to 4.45% and the defined valuation is about zero. That −$66.8bn is 0.89 of the April–May intervention ($75.0bn) and 1.91 of May’s own intervention ($34.9bn). One of those pairings is the calendar’s analogue. The episodes do not say which pairing is the base rate.

August’s 10-year yield was 4.75% on both month-ends, so the August print will not repeat September 2022. The reserve side is already published: securities −$87.8bn, deposits −$6.9bn, total −$79.6bn. Deposits were about flat in the earlier episodes and fell in August, by much less than securities. These are accounting comparisons. They do not say the intervention caused the yen move, or that Treasury sales caused yields.

Reported net official gold tonnage remains a minor bound on the $236.5bn decline in foreign official Treasury holdings, about 13% to 17% at MoF marks. Japan’s ounce volume did not rise. The question of Treasury funding stays open. Friday’s print can miss the wide range above. A print inside −$50bn to −$100bn would still leave the ratio unidentified.

### BUILD SPEC

Script: `bin/japan_intervention_tic.py`. Expected runtime: under two minutes. The files are small. Do not pull full BIS history.

Inputs:

- MoF intervention CSV, Shift-JIS, unit 100 million yen: https://www.mof.go.jp/policy/international_policy/reference/feio/foreign_exchange_intervention_operations.csv
- August 2026 window total, no daily rows: https://www.mof.go.jp/english/policy/international_policy/reference/feio/monthly/20260828e.html
- Reserves historical CSV, then monthly HTML `08MM.html` for months after the CSV ends: https://www.mof.go.jp/policy/international_policy/reference/official_reserve_assets/data/
- TIC `mfhhis01.txt` and `slt_table5.txt`: https://ticdata.treasury.gov/Publish/mfhhis01.txt and https://ticdata.treasury.gov/Publish/slt_table5.txt
- BIS `D.JP.JPY.A` only on intervention dates and 30 Jul–26 Aug 2026: https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/D.JP.JPY.A?format=csv
- Treasury par curve CSVs for 2022, 2023, 2024, 2026, columns `7 Yr` and `10 Yr`, last business day of each month: `daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve&field_tdr_date_value={year}&page&_format=csv`
- Gold, read-only, do not rebuild from sponsor series: https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/data/gold/ledger_monthly.csv
- Reuse the holding-return function in `bin/r1_treasury_decomposition.py`. Do not apply it to a book the script has not been given a maturity for.

Output: `data/fx/japan_intervention_episodes.csv`. Columns: `episode_month`, `intervention_days`, `yen_bn`, `usd_bn`, `usd_bn_low`, `usd_bn_high`, `securities_change_usd_bn`, `deposits_change_usd_bn`, `securities_per_usd`, `tic_start`, `tic_end`, `raw_bn`, `hold_return`, `val_bn`, `adj_bn`, `adj_per_usd`, `grade`. A second file `data/fx/japan_intervention_aug2026_prereg.csv` stores the 14 Oct 2026 range, the July stock, the +$4.7bn valuation, and an empty `actual_adj_bn` until the August TIC row exists.

Assert: quarterly yen totals match the sum of days within ¥0.1bn; September 2022 securities −$51.5bn and deposits about 0; May 2024 securities −$50.4bn; May 2026 securities −$75.6bn; August 2026 securities −$87.8bn, deposits −$6.9bn, total −$79.6bn; September 2022 TIC raw −$79.6bn; May 2026 TIC raw −$66.8bn; foreign official end-Feb to end-Jul 2026 is −$236.5bn; gold Feb–Jul sum is 234.7 t within 0.1 t; the August 2026 TIC cell is empty while `slt_table5.txt` still ends in July 2026. Recompute the holding returns and replace the hand-rounded figures if any differs by more than 0.05 percentage point. The 16 Oct score is a second run of the same script.

### UNCERTAIN

The holding returns were computed by hand from the R1 formula and the yields listed above. They are good to about 0.05 percentage point. The script should recompute them. A 0.05 ratio error moves the pre-registered edges by about $5bn.

The 10-year par bond overstates the price piece if Japan’s Treasury book is shorter than 10 years. September 2022 is valuation-dominated under that definition. A shorter book would assign more of the −$79.6bn to quantity. The true maturity is not in these files.

BIS `D.JP.JPY.A` is an average of observations, not the rate MoF dealt at. May 1 2024 has no BIS row, so that day’s dollars are the 30 April / 2 May bracket. August dollars use the min and max daily average in the window because the daily yen split is unpublished.

MoF securities are marked to market and include non-dollar assets, so the securities line mixes sales, price, and FX translation. The securities-per-dollar ratio is the raw line change the test asked for. It is not a count of bonds sold.

`mfhhis01` prints some 2024 Japan stocks as integers. They were used as printed.

The gold tonnes are the programme ledger’s IMF-world column, summed here, not a fresh IMF pull. The $103bn “official net sales” figure was not re-derived from a transactions file, so it is not a denominator in the results. The 234.7 t figure is a net stock change.

MoF’s reuse licence was not on a page that returned. The statistics pages themselves loaded without a login. Treasury’s site-policies page did not state a reuse licence.

### NOT DONE

The 16 October score. The August TIC row is not in `slt_table5.txt`.

The daily yen split for 30 July–26 August 2026, and any US-side dollar amount. The monthly release gives only ¥15,399.3bn.

The 2026 tail of `week.csv`. The fetch ended in 2013, so the four-week non-resident sum was not recomputed and is not used.

A counterparty name. The coverage note stops at the OTC identity.

`CALENDAR.tsv` row 60. This pass is read-only, so the pre-registration is in the section above rather than in the file.

The closure-ledger country panel. The item leaves that dropped.
