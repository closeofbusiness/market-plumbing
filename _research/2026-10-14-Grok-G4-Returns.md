# Grok (Cursor CLI) batch g4, 14 Oct 2026: fifteen rates, FX and commodities research items, returns and the supervisor's checks

*On 14 Oct 2026 the principal asked for every item on the ranked list of further rates, FX and commodities research to be run through Grok. The supervisor sent one parcel per item through `orchestrator_cursor` to Grok 4.7 (256k, extra-high). Each parcel ran in a fresh stage behind the read-and-web-only fence. Each one carried the item's specification and a one-page summary of the programme. Each parcel was asked to run the item's first test as far as free public data allows, and to return its sources, results, any pre-registration, what the result changes, a build spec for the code, what it inferred, and what it could not do. The fence and wrapper statistics are given for each item. A URL cited without a fetch in that call is listed and not relied on. The returns are claims until checked. The supervisor's check is stated at the head of each item.*

*Quotes longer than 15 words were cut by the supervisor to their first twelve words, under the repository's quotation rule. The full text is at each cited URL. Grok's opening narration is dropped; everything from SOURCES onward is as returned.*

*Item 1 was landed first, on 14 Oct, so that its pre-registration was committed before the 16 Oct TIC release. The other fourteen followed the same evening. Item 14's first call ended without an answer and was resumed in the same Cursor session; its statistics merge the two calls. Item 5's first launch was refused by the model before any tool ran and was relaunched.*

| Item | Topic | Wall time (s) | Searches | Fetches | URLs cited but not fetched |
|---:|---|---:|---:|---:|---:|
| 1 | Japan intervention funding | 1136 | 8 | 39 | 5 |
| 2 | COT lead-lag at the right horizon, plus the ICE Brent leg (and a page-sentence check) | 822 | 10 | 23 | 5 |
| 3 | Public swap-tape ledger | 762 | 11 | 25 | 7 |
| 4 | The yen against the rate gap | 1141 | 11 | 46 | 7 |
| 5 | Copper visible-stock ledger from Cochilco (LME, COMEX, SHFE), with the printed y/y column corrected | 704 | 17 | 22 | 2 |
| 6 | R1 second opinions in hours | 719 | 20 | 27 | 2 |
| 7 | Who took the duration | 681 | 13 | 33 | 3 |
| 8 | Is the swap-dealer line an index-investment proxy? Calibrate COT to the CFTC Index Investment Data, 2007-2015 | 1044 | 4 | 62 | 3 |
| 9 | Gold against 10y real yields | 1024 | 11 | 35 | 2 |
| 10 | US external balance sheet identity | 615 | 17 | 23 | 1 |
| 11 | 20 Nov BIS preregistration pack | 863 | 15 | 35 | 3 |
| 12 | IMF currency composition of the IIP | 1258 | 9 | 60 | 4 |
| 13 | Treasury intermediation pack | 933 | 12 | 43 | 5 |
| 14 | Refunding-day and buyback event study, daily leg only, with an unclean 4 Nov observation logged in advance | 951 | 17 | 24 | 4 |
| 15 | Global comovement in 10y yields | 945 | 17 | 43 | 3 |

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

---

## Item 2: COT lead-lag at the right horizon, plus the ICE Brent leg (and a page-sentence check)

*Status SUCCESS; 822 s; breaches 0, blocked 0, unexpected tools 0, stage changes 0.*

*Cited without a fetch in this call, not relied on:* `https://publicreporting.cftc.gov/resource/72hh-3qpy.json`; `https://publicreporting.cftc.gov/resource/kh3c-gbw2.json`; `https://www.eia.gov/dnav/pet/hist_xls/RBRTEd.xls`; `https://www.eia.gov/dnav/pet/hist_xls/RWTCd.xls`; `https://www.ice.com/publicdocs/futures/COTHist{2011..2026}.csv`

*The stream carried an abandoned first draft of the SOURCES table spliced into the final answer; only the final draft is reproduced.*


**Supervisor check.** Re-fetched from the CFTC futures-only dataset (`72hh-3qpy`, code 067651) with the neutral User-Agent. 8 Sep 2026: long 218,960, short 107,229, net 111,731. 6 Oct 2026: long 178,353, short 124,755, net 53,598. Both match. The four-week cut is therefore a futures-only figure (−52%). On the combined report it is −25%. The page sentence "halved it in the last four weeks" was qualified on 14 Oct to name the report. The E-021 note's "n=148" does not match `data/cftc_cot/leadlag.csv`, which has 145 same-week and 144 next-week pairs. It was corrected in place. ICE Brent rows and the Kemp figures are relayed.


### SOURCES

| Source | URL fetched | Free? | Terms quote | What it holds |
|---|---|---|---|---|
| ICE COT index | https://www.ice.com/cot-report-links | Yes, no login | See website terms below | Links to yearly CSVs, 2011 through 2026 |
| ICE COT 2026 | https://www.ice.com/publicdocs/futures/COTHist2026.csv | Yes, no login | “only for your own personal, non-commercial use” | All ICE Futures Europe commodities; futures-only and combined; CFTC-style columns. Fetch returned rows through 31 Mar 2026, then stopped |
| ICE COT 2011 | https://www.ice.com/publicdocs/futures/COTHist2011.csv | Yes, no login | Same website terms | Same layout. Two Brent rows per date, same market name, split only by `FutOnly_or_Combined`. Dates mix `01/04/2011` and `1/18/2011`. Swap short/spread headers use a double underscore |
| ICE website terms | https://www.ice.com/privacy-security-center/terms-of-use | Public page | “only for your own personal, non-commercial use” | Also: “does not include use of any data mining, robots”. No “confidential” label on the COT files in the terms read |
| CFTC futures-only | https://publicreporting.cftc.gov/resource/72hh-3qpy.json | Yes, no key | “Government information at the CFTC website is in the public domain.” | Disaggregated COT. WTI is `067651`, “WTI-PHYSICAL - NEW YORK MERCANTILE EXCHANGE” |
| CFTC combined | https://publicreporting.cftc.gov/resource/kh3c-gbw2.json | Yes, no key | Same public-domain policy: https://www.cftc.gov/WebPolicy/index.htm | Futures-and-options combined, same contract code |
| EIA reuse | https://www.eia.gov/about/copyrights_reuse.php | Yes | “U.S. government publications are in the public domain” | Cushing WTI spot used by the ledger is `https://www.eia.gov/dnav/pet/hist_xls/RWTCd.xls` (named in the public script; the xls was not re-downloaded here) |
| Programme ledgers and note | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-10-12-E021-Where-The-Money-Comes-From-Rates-FX-Commodities.md and `data/cftc_cot/{wti,gold,copper}_ledger.csv`, `leadlag.csv`, `windows.csv`, `report.txt` | Public repo | Repo content; CFTC and EIA inputs are public domain | Gold, WTI and copper ledgers exist. WTI carries EIA dollars. Gold and copper prices are kept out of the public files |
| Kemp, 7 Jun 2026 | https://jkempenergy.com/2026/06/07/oil-bears-bet-hormuz-crisis-is-mostly-over/ | Yes, no login | Terms not read | Secondary reading of ICE Brent futures and options, in million barrels |

Managed-money net below is long minus short. Spreading is excluded. One contract is 1,000 barrels.

### RESULTS

Four report dates. WTI from the CFTC rows. Brent only where the ICE file actually returned the row.

| Report date | WTI futures-only net | WTI futures-only, % of OI | WTI combined net | WTI combined, % of OI | ICE Brent combined net |
|---|---:|---:|---:|---:|---:|
| 31 Mar 2026 | 73,347 | 3.61% of 2,030,970 | 130,717 | 4.30% of 3,039,583 | 429,853 |
| 30 Jun 2026 | 81,282 | 4.25% of 1,914,443 | 93,713 | 3.65% of 2,568,532 | not in the returned slice |
| 8 Sep 2026 | 111,731 | 5.76% of 1,939,911 | 139,339 | 5.35% of 2,605,602 | not in the returned slice |
| 6 Oct 2026 | 53,598 | 2.84% of 1,889,422 | 104,491 | 4.12% of 2,533,937 | not in the returned slice |

WTI futures-only longs and shorts: 31 Mar 177,780 / 104,433; 30 Jun 203,601 / 122,319; 8 Sep 218,960 / 107,229; 6 Oct 178,353 / 124,755. Combined: 31 Mar 214,757 / 84,040; 30 Jun 199,357 / 105,644; 8 Sep 226,753 / 87,414; 6 Oct 198,618 / 94,127.

| Finding | Value | Grade | Window / denominator | Source URL | Quote or row |
|---|---|---|---|---|---|
| Page path is NYMEX WTI futures-only | 15,743 on 30 Dec 2025; 111,731 on 8 Sep 2026; 53,598 on 6 Oct 2026 | MEASURED | Managed-money net contracts, those three Tuesdays | CFTC `72hh-3qpy`, code `067651`; page text at the E021 raw URL above | 30 Dec long 146,234 short 130,491. E021: “15,743 contracts on 30 Dec 2025 … 111,731 on 8 Sep 2026 …” |
| Four-week futures-only cut | −58,133 contracts, −52.0%, −58.133 million barrels | MEASURED | 8 Sep to 6 Oct 2026; net contracts, and contracts × 1,000 barrels | Same CFTC futures-only rows | 53,598 − 111,731. The page’s “−58 mb” is this figure rounded |
| Four-week combined cut | −34,848 contracts, −25.0%, −34.848 million barrels | MEASURED | Same four Tuesdays; combined net contracts | CFTC `kh3c-gbw2`, code `067651` | 104,491 − 139,339. `windows.csv` has the same pair, 139,339 to 104,491 |
| Twelve-week combined change | +18,108 contracts | MEASURED | 14 Jul to 6 Oct 2026; combined net contracts | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/data/cftc_cot/windows.csv | Row `wti,combined,12 weeks` |
| ICE Brent combined, 31 Mar | 429,853 contracts (9.76% of OI 4,403,803), equal to 429.853 million barrels | MEASURED | Managed-money net, futures and options, 31 Mar 2026 | COTHist2026.csv row `ICE Brent Crude Futures and Options`, `260331`, `Combined` | Long 470,101, short 40,248. Futures-only that day is 382,072 (long 432,381, short 50,309) |
| Brent book into early June | 429 million barrels on 31 Mar; 253 million barrels in the week ending 2 Jun | BOUNDED | Kemp’s million-barrel rounding of ICE Brent futures and options | https://jkempenergy.com/2026/06/07/oil-bears-bet-hormuz-crisis-is-mostly-over/ | “net position of 253 million barrels”; “429 million … on March 31”. 429 million matches 429,853 contracts. This is not the 30 Jun row |
| Full-sample week count | 875 weeks | MEASURED | Weekly reports, 5 Jan 2010 through 6 Oct 2026, code `067651` | CFTC futures-only count query; `report.txt` | `count_report_date_as_yyyy_mm_dd` = 875. Report: “3 contracts x 875 weekly reports” |
| Published one-week test | Same week r = +0.380 (n = 145); next week r = −0.078 (n = 144); 5% band ±0.163 | MEASURED | WTI managed-money weekly contract change vs percent price change; 2 Jan 2024 to 6 Oct 2026 | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/data/cftc_cot/leadlag.csv | Futures-only row. 1.96/√145 = 0.163. Same-week r is above the band. Next-week r is inside it. Coincident with the week, no detectable one-week lead in this window |
| Page’s other sample size | n = 148 appears in the E021 table; the lead-lag file has 145 and 144 | MEASURED for 145 and 144; 148 not reproduced | Same 2024–26 test | E021 raw URL and `leadlag.csv` | Inclusive Tuesdays from 2 Jan 2024 to 6 Oct 2026: 1,008 days / 7 = 144 steps, plus the first week = 145. Next-week drops the last week, so 144 |
| Minimum detectable correlation, full sample | h = 1: 0.066 (n = 875). h = 2: 0.094 (438). h = 4: 0.132 (219). h = 8: 0.187 (109). h = 13: 0.24 (67). h = 26: 0.34 (34) | BOUND | \|r\| > 1.96/√(n/h), two-sided 5%, n = 875 overlapping weekly returns treated as n/h independent observations. Not an estimated coefficient | Count from the CFTC query above | 1.96/√875 = 0.0663; 875/13 = 67.3 and 1.96/√67 = 0.240; 875/26 = 33.7 and 1.96/√34 = 0.336 |
| 2011 Brent file shape | Two Brent rows on 4 Jan 2011, both named “ICE Brent Crude Futures”, OI 870,690 (`FutOnly`) and 878,891 (`Combined`) | MEASURED | File structure, 2011 | COTHist2011.csv | Last column carries the report type. The market name does not |

The page does not use the word “halved”. The −52% cut is the futures-only arithmetic. Proposed sentence: “NYMEX WTI futures-only managed money went from 15,743 net contracts on 30 …”

Correction to register: add “NYMEX futures-only” beside the 15,743 / 111,731 / 53,598 / −58 mb figures. The benchmark name on the page is already WTI. The report type is missing, and those counts are the futures-only book.

### WHAT IT CHANGES

The C-142 line in `state.md` (15,743 to 111,731, then 53,598) matches the CFTC futures-only rows. Combined 130,717 / 93,713 / 104,491 matches too. The 12-week sign flip is in `windows.csv`: futures-only −8,376, combined +18,108.

This does not show that the position change caused the price. The 2024–26 next-week correlation stays inside ±0.163. The same-week correlation, +0.380, is the same week as the price.

It does change how strong that null is. The published test can see a correlation of about 0.16. On all 875 weeks, a one-week correlation of about 0.07 would clear the same 5% bar, and at 13 and 26 weeks only correlations of about 0.24 and 0.34 would. That full-sample regression was not run, so the page cannot yet say “no detectable lead” at the full-sample size.

Brent on 31 Mar is a different book from WTI that day (429,853 combined contracts against 73,347 futures-only). Kemp’s reading says that Brent book was down to about 253 million barrels by 2 Jun, while WTI futures-only rose from 73,347 on 31 Mar to 81,282 on 30 Jun. Crude sentences have to keep the benchmark and the report type. The four-week Brent path (the −24% claim) is still unmeasured here.

### BUILD SPEC

`bin/pull_ice_cot.py`, then `bin/cot_horizon_leadlag.py`. Keep the ICE branch out of `bin/pull_cftc_cot.py`. The website terms forbid robots and systematic retrieval, so this is a one-shot local download of 16 files, not a crawler. Store the raw CSVs locally. Commit only the aggregate ledger, with an ICE attribution.

Inputs

- `https://www.ice.com/publicdocs/futures/COTHist{2011..2026}.csv`
- Brent rows: commodity code `B`. Report type from `FutOnly_or_Combined`. From 2026 the combined name is `ICE Brent Crude Futures and Options - ICE Futures Europe`. In 2011 both rows share the name `ICE Brent Crude Futures`.
- Accept `Swap_Positions_Short_All` and `Swap__Positions_Short_All`.
- Parse `As_of_Date_In_Form_YYMMDD` first. The other date field mixes `01/06/2026`, `1/13/2026` and `3/31/2026`.
- WTI, gold, copper positions: existing ledgers, CFTC `72hh-3qpy` and `kh3c-gbw2`, codes `067651`, `088691`, `085692`.
- WTI price: column already on `wti_ledger.csv`, EIA `RWTCd.xls`.
- Brent price, if used: `https://www.eia.gov/dnav/pet/hist_xls/RBRTEd.xls`. Drop any return that uses a print after 1 Oct 2026.
- Gold and copper prices stay local. No price column in a public file.

Outputs

- `data/cftc_cot/brent_ledger.csv`: `report_date`, `report_type`, `market_name`, `oi`, `mm_long`, `mm_short`, `mm_spread`, `mm_net`, `mm_net_pct_oi`, `pm_long`, `pm_short`, `pm_net`, `net_bbl`.
- `data/cftc_cot/horizon_leadlag.csv`: `contract`, `report_type`, `horizon_weeks`, `regressor`, `n`, `n_eff`, `coef`, `nw_se`, `boot_p05`, `boot_p95`, `r_detect`. Horizons 1, 2, 4, 8, 13, 26. Regressors: lagged change in net as % of open interest, lagged level as % of open interest, and trailing 1-, 3-, 6- and 12-month returns (the reverse regression). Newey-West lag equal to the horizon. Block bootstrap, block length equal to the horizon, 1,000 draws.

Assert

- Brent combined on 2026-03-31: `mm_net == 429853`.
- WTI futures-only: 2026-09-08 `111731`, 2026-10-06 `53598`. Combined: `139339` and `104491`.
- One Brent combined row per date in 2026. In 2011, two Brent rows per date.
- WTI week count 2010-01-05 to 2026-10-06 equals 875. The 2024 window still prints n = 145 and n = 144.
- Public files contain no gold or copper price column.
- Brent returns stop at 2026-10-01.

Runtime: about 3 minutes for the 16 CSVs, under 1 minute for the regressions.

### UNCERTAIN

- The website terms read here limit COT reuse to personal, non-commercial use and forbid robots. They do not call the files confidential. Whether a committed aggregate ledger is allowed is a legal reading, not something the COT page states.
- “Futures-and-options rows exist only from 13 Mar 2013” was not checked. January 2011 already has a `Combined` row, with a slightly different open interest from `FutOnly` (870,690 vs 878,891 on 4 Jan 2011), so it is a second row, and the market name does not say “and Options”.
- Producer net −381,970 was not in the rows returned. On 31 Mar 2026, Brent combined producers are 1,294,565 long and 1,854,221 short, net −559,656.
- n = 148 is only in the E021 summary sentence. The script’s lead-lag starts at 2024-01-01 and writes 145 and 144. What the extra three weeks were is not in the files read.
- Kemp’s 253 million barrels is his rounding for the week ending 2 Jun, not a contract count taken from the CSV.
- The detectable-correlation figures use n/h as if those slices were independent. A block bootstrap can move them. They are a power bound, not a fitted lead.

### NOT DONE

- ICE Brent managed-money nets for 30 Jun, 8 Sep and 6 Oct 2026. `COTHist2026.csv` is free and downloaded, and the fetch stopped inside the 31 Mar block, before those rows. The −24% Brent claim (265,753 to 201,052) was not recomputed.
- Local projections at horizons 1, 2, 4, 8, 13 and 26, Newey-West standard errors, the block bootstrap, and the trailing-return regression. That needs the script above. It was not run by hand, and no shell was used.
- EIA `RWTCd.xls` and `RBRTEd.xls` were not re-downloaded. The 8 Sep price of $94.21 on the page was not re-read from EIA. `report.txt` gives 6 Oct at $96.24 and a four-week price change of +2.2%, which is consistent with a price near $94.
- Gold and copper lead-lag correlations were not recomputed. The public `leadlag.csv` has WTI only.

---

## Item 3: Public swap-tape ledger: swap spreads, CPI-swap breakeven and cross-currency basis from one parser

*Status SUCCESS; 762 s; breaches 0, blocked 0, unexpected tools 0, stage changes 0.*

*Cited without a fetch in this call, not relied on:* `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value_month={YYYYMM}`; `https://kgc0418-tdw-data-0.s3.amazonaws.com/cftc/eod/CFTC_CUMULATIVE_RATES_2024_10_11.zip`; `https://kgc0418-tdw-data-0.s3.amazonaws.com/cftc/eod/CFTC_CUMULATIVE_RATES_{YYYY}_{MM}_{DD}.zip`; `https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/CFTC_CUMULATIVE_RATES_2024_10_11.zip`; `https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/CFTC_CUMULATIVE_RATES_2026_10_13.zip`; `https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/CFTC_CUMULATIVE_RATES_{YYYY}_{MM}_{DD}.zip`; `https://www.bankofengland.co.uk/-/media/boe/files/statistics/yield-curves/latest-yield-curve-data.zip`


**Supervisor check.** The Treasury par and real rows for 29 Sep and 13 Oct 2026 match the Treasury CSVs (13 Oct: 10y par 5.21, real 2.88). **One finding in this return is wrong.** Grok reports HTTP 500 on every DTCC cumulative-rates file on or after 14 Oct 2024. From the supervisor's machine, with the neutral User-Agent, the files download: 2026-10-13 is a 1.4 MB zip holding a 15 MB CSV, and 2024-10-14 and 2025-04-09 return 200. 2024-10-11 returns 404. The archive cutoff is confirmed, the data is reachable, and the build is not blocked. The 500s were Grok's fetch tool, which does not handle zip bodies. The "process breach" row is the email leak by an in-house proposer agent earlier on 14 Oct, which was reported to the principal that day. It was carried in from the item text, and Grok sent no address. DTCC's reuse terms are still unread, so no raw DTCC file is committed. Only derived medians will be published, once the terms are read.


### SOURCES

| Source | URL fetched | Free? | Terms quote | What it holds |
| --- | --- | --- | --- | --- |
| CFTC/DTCC cumulative rates zip (S3) | `https://kgc0418-tdw-data-0.s3.amazonaws.com/cftc/eod/CFTC_CUMULATIVE_RATES_2024_10_11.zip`, `..._2024_10_14.zip`, `..._2026_10_13.zip`, and a nonexistent `..._1999_01_01.zip` | No login page. Every `.zip` GET returned HTTP 500 and no rows. Listing the bucket returned Access Denied. | S3 list body: "Access Denied". | Dated end-of-day rates zip named in the item. Bytes were not readable here. |
| Same file via the dashboard API | `https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/CFTC_CUMULATIVE_RATES_2024_10_11.zip` (404). `..._2024_10_14.zip`, `..._2025_04_09.zip`, `..._2026_10_13.zip` (500). Dashboard: `https://pddata.dtcc.com/ppd/cftcdashboard` | Yes, no login. 11 Oct 2024 is not served. The other three dates were not 404, and the zip body was not readable. | — | Cumulative CFTC rates report for one UTC date. |
| DTCC PPD user guide v2.8 (May 2025), on the same S3 host | `https://kgc0418-tdw-data-0.s3.amazonaws.com/gtr/static/gtr/docs/RT_PPD_quick_ref_guide.pdf` | Yes. The PDF downloaded. | "available for 366 days from the current date" and "© 2025 DTCC. All rights reserved." | Cumulative slice = all transactions published that UTC date, one asset class. Rates fields include Action type, fixed rates, spreads, day-count, underliers, notionals. No party-identity column in Appendix A. History note: data from 29 Dec 2023. |
| DTCC website terms, last updated 11 Mar 2026 | `https://www.dtcc.com/terms` | Yes. | "YOU SHALL NEITHER ACCESS NOR USE THE DTCC SITE" and "may be subject to separate agreements with DTCC". | Acceptance terms and a separate-agreement override. The fetched text has no sentence that grants republication of derived series. |
| Treasury par yield XML | `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value_month=202504`, `...202609`, `...202610` | Yes, no login. | No reuse clause on this feed. Description fetched from the rates page below. | Daily par yields, percent. Fields `BC_2YEAR`, `BC_5YEAR`, `BC_10YEAR`, `BC_30YEAR`. |
| Treasury par real yield XML | Same pattern with `data=daily_treasury_real_yield_curve` for `202504`, `202609`, `202610` | Yes, no login. | No reuse clause on the feed page. | TIPS par real yields, percent, at 5, 7, 10, 20, 30 years. No 2-year. |
| Treasury feed catalogue and rates page | `https://home.treasury.gov/treasury-daily-interest-rate-xml-feed` and `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_yield_curve` | Yes. | "nominal coupon security that pays semiannual interest" and "These par yields are derived from indicative, bid-side market price quotations". | Five series only: par, bills, long-term, par real, real long-term. No breakeven series. Par yields are CMTs read from the daily par curve, NY Fed bid quotes near 15:30. |
| BoE yield curves | `https://www.bankofengland.co.uk/statistics/yield-curves` and `https://www.bankofengland.co.uk/-/media/boe/files/statistics/yield-curves/latest-yield-curve-data.zip` | Page is public. The latest zip returned HTTP 500 and was not opened. | "the spreadsheet for the latest month" and "there would be no objection to electronic storage". OIS quotes: "continuously compounded and quoted on an annual basis". | Gilt nominal, real, and inflation curves, plus a SONIA OIS curve. Latest file is the current month. Daily OIS archive is a separate zip listed at 11.8MB. OIS source line: Bloomberg and Bank calculations. |
| BoE legal / Open Government Licence | `https://www.bankofengland.co.uk/legal` and `https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/` | Yes. | "subject to the terms of the UK Open Government Licence" and "copy, publish, distribute and transmit the Information". OGL also excludes "third party rights the Information Provider is not authorised to license". | Database and statistical releases may be reused under OGL v3.0 with attribution. Third-party material in a Bank page stays with the originator. |

### RESULTS

| Finding | Value | Grade | Window / denominator | Source URL | Quote or row reference |
| --- | --- | --- | --- | --- | --- |
| Process breach | Logged 14 Oct 2026. A personal email was sent as the User-Agent on four HEAD probes and one streaming read to `kgc0418-tdw-data-0.s3.amazonaws.com`. The standing rule allows that contact on sec.gov hosts only. Every other host uses `ThirdDerivativeResearch`. This session did not send the address. | Process log | S3 host, those five requests | Item record; host checked this session | — |
| Dashboard file before the stated cutoff | HTTP 404 | MEASURED | File date 2024-10-11, CFTC cumulative rates | `https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/CFTC_CUMULATIVE_RATES_2024_10_11.zip` | Status 404 Not Found |
| Dashboard files on and after 14 Oct 2024, including a test date inside the old 366-day claim | HTTP 500, no rows, for 2024-10-14, 2025-04-09, and 2026-10-13 | MEASURED as a failed GET | Those three UTC file dates | `https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/CFTC_CUMULATIVE_RATES_2026_10_13.zip` and the two earlier dates | Status 500. A fake S3 key `..._1999_01_01.zip` also returned 500, so 500 does not prove the object exists. |
| S3 Glacier / `InvalidObjectState` | Not re-read. The 11 Oct 2024, 14 Oct 2024, and 13 Oct 2026 S3 zips all returned HTTP 500 and no XML error body. | — | Object GET, those dates | `https://kgc0418-tdw-data-0.s3.amazonaws.com/cftc/eod/CFTC_CUMULATIVE_RATES_2024_10_11.zip` | No `InvalidObjectState` body |
| Treasury par yields, 9 Apr 2025 | 2y 3.91, 5y 4.06, 10y 4.34, 30y 4.72 percent | MEASURED | US par curve, that date. Percent per the `BC_*` fields. | `.../pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value_month=202504` | `NEW_DATE` 2025-04-09 |
| Treasury par yields, 29 Sep 2026 | 2y 4.89, 5y 5.06, 10y 5.26, 30y 5.59 percent | MEASURED | Same, that date | `...field_tdr_date_value_month=202609` | XML id 326, `NEW_DATE` 2026-09-29 |
| Treasury par yields, 13 Oct 2026 | 2y 4.79, 5y 5.00, 10y 5.21, 30y 5.56 percent | MEASURED | Same, that date. Matches the critique's Treasury par print. | `...field_tdr_date_value_month=202610` | XML id 335, `NEW_DATE` 2026-10-13 |
| 10y par breakeven | 9 Apr 2025: 4.34 − 2.07 = 2.27 pp. 29 Sep 2026: 5.26 − 2.91 = 2.35 pp. 13 Oct 2026: 5.21 − 2.88 = 2.33 pp. | IDENTITY | 10-year par yield minus 10-year par real yield, those three dates. This is the par difference. The feed has no breakeven series. | Par and real XML URLs above | 13 Oct 2026 real row is id 335, `TC_10YEAR` 2.88. 29 Sep 2026 real id 326, `TC_10YEAR` 2.91. 9 Apr 2025 real `TC_10YEAR` 2.07. |
| 5y and 30y par breakeven, same identity | 9 Apr 2025: 2.45 and 2.22 pp. 29 Sep 2026: 2.34 and 2.30 pp. 13 Oct 2026: 2.33 and 2.28 pp. | IDENTITY | Par minus par real at 5y and 30y. No 2y real yield exists on this feed. | Same | `TC_5YEAR` / `TC_30YEAR` on those rows: 1.61/2.50, 2.72/3.29, 2.67/3.28 |
| Change in the 10y Treasury par split | 9 Apr 2025 to 13 Oct 2026: par +87 bp, real +81 bp, par breakeven +6 bp. 29 Sep 2026 to 13 Oct 2026: par −5 bp, real −3 bp, par breakeven −2 bp. | MEASURED | Difference of the identity above. Levels, not a cause of the move. | Same rows | 5.21 − 4.34 = 0.87; 2.88 − 2.07 = 0.81; 2.33 − 2.27 = 0.06 |
| Quiet-session Treasury moves | 28→29 Sep 2026: 2y −3 bp, 5y 0, 10y +2 bp, 30y +3 bp, 10y par breakeven +1 bp (2.34 to 2.35). 29→30 Sep 2026: 2y −1, 5y +3, 10y +3, 30y +5, breakeven +1 bp (2.35 to 2.36). | MEASURED | One-session change in the Treasury par curve. This is not the swap tape's IQR/√n. | `...202609` par ids 325–327 and real ids 325–327 | 28 Sep 10y par 5.24, real 2.90. 30 Sep 10y par 5.29, real 2.93. |
| Next published Treasury session after 9 Oct 2026 | 9→13 Oct: 2y −1 bp, 5y −2, 10y −3, 30y −4, 10y par breakeven 0 (2.33 to 2.33). No rows for 10, 11, or 12 Oct. | MEASURED | Published-row gap, Treasury par curve | `...202610` ids 334 and 335 | 9 Oct `BC_10YEAR` 5.24, `TC_10YEAR` 2.91 |
| USD OIS medians, swap spreads, ACT/360 versus bond-equivalent band, 10y CPI swap minus TIPS, JPY/USD and EUR/USD 1–3y medians, swap IQR/√n | No value | — | — | Zip URLs above | No CSV row was read |

Worked check on 13 Oct 2026: `BC_10YEAR` 5.21 minus `TC_10YEAR` 2.88 equals 2.33 percentage points, which is the critique's TIPS figure. The swap half of that illustration (OIS 4.65/4.72/4.80/4.90 and CPI swap 2.454) was not recomputed.

### PRE-REGISTRATION

None. The item does not ask for a number to be written down before a data release. The "before any code" steps are the archive check, this breach log, and the terms read.

### WHAT IT CHANGES

The programme's gaps are unchanged. There is still no free cross-currency basis series and no free swap-spread series, so FX remains a flow map without a price-side hedge-cost ledger. The BIS C-136 reading is untouched, because no 1–3y basis price was measured. R1's rates split is untouched: the +6 bp par-breakeven change from 9 Apr 2025 to 13 Oct 2026 is a different window from the +17 bp breakeven in the end-2023 to 18 Sep 2026 account, and it is a Treasury par difference, not a CPI-swap print. The swap-substitution test is still unrun. Nothing here is a flow causing a yield or a dollar move.

What is now checked: on 13 Oct 2026 the Treasury comparator in the earlier critique matches the official par row, and 2.33 pp is `BC_10YEAR` minus `TC_10YEAR`. The 11 Oct 2024 cumulative file is absent from the dashboard API. Publishing a derived series is still blocked, because the fetched DTCC terms do not contain a reuse grant.

### BUILD SPEC

Script: `scripts/cftc_swap_tape_daily.py`. Hardcode `User-Agent: ThirdDerivativeResearch`. Assert the header equals that string and contains no `@`.

Inputs:

- `https://kgc0418-tdw-data-0.s3.amazonaws.com/cftc/eod/CFTC_CUMULATIVE_RATES_{YYYY}_{MM}_{DD}.zip`
- If that body is not a zip, the same name at `https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/CFTC_CUMULATIVE_RATES_{YYYY}_{MM}_{DD}.zip`
- `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/pages/xml?data=daily_treasury_yield_curve&field_tdr_date_value_month={YYYYMM}` fields `BC_2YEAR`, `BC_5YEAR`, `BC_10YEAR`, `BC_30YEAR`
- `...data=daily_treasury_real_yield_curve&field_tdr_date_value_month={YYYYMM}` fields `TC_5YEAR`, `TC_10YEAR`, `TC_30YEAR`

First dates: 2025-04-09, 2026-09-28, 2026-09-29, 2026-09-30, 2026-10-13, plus a status-only probe of 2024-10-11.

Outputs, and no raw zip in the repo:

- `data/swap_tape_status.csv`: `date_utc, url, http_status, error_code, nbytes, zip_ok`
- `data/swap_tape_daily.csv`: `date_utc, series, tenor_years, ccy_pair, daycount, n, median_raw, q1, q3, iqr, iqr_over_sqrt_n, min_raw, max_raw, median_bey, treasury_par, treasury_real, par_breakeven, spread_bp_raw, spread_bp_bey, package_share, cap_share`

Use the PPD columns `Action type`, `Product name`, `Unique Product Identifier`, `UPI Underlier Name`, `Underlier ID-Leg 1/2`, `Notional currency-Leg 1/2`, `Execution Timestamp`, `Effective Date`, `Expiration Date`, `Fixed rate-Leg 1/2`, `Spread-Leg 1/2`, `Spread notation-Leg 1`, `Fixed rate day count convention-leg 1`, `Package indicator`, `Notional amount-Leg 1`. Keep `Action type == NEWT` and log the other action counts. Spot-start: effective date within 7 days of execution. Tenor = (expiration − effective) / 365.25, within 0.35 years of 2, 5, 10, or 30. USD SOFR OIS: USD, underlier contains SOFR, leg-1 fixed rate filled, leg-2 fixed rate blank. 10y CPI: USD, underlier contains CPI. JPY/USD and EUR/USD float-float: both fixed rates blank, a spread filled, tenor from 1 to 3 years inclusive. On the first file, print product-name counts and abort if the chosen label has n = 0.

Assert: a non-zip or `InvalidObjectState` or 404 writes a status row and no median; `iqr_over_sqrt_n = (q3−q1)/sqrt(n)`; par breakeven equals `BC_10YEAR − TC_10YEAR`; a missing Treasury row (holiday) leaves the spread blank. If day-count is ACT/360 and the rate is decimal, `median_bey = 2*((1 + median_raw*365/360)**0.5 − 1)`, and the gap versus the raw rate stays inside 0 to 5 bp for rates of 0 to 10 percent. Read `Spread notation` before converting a basis to bp. Store local CSV only. A publish flag stays off until a human-read DTCC reuse grant is on file.

Runtime target: under 2 minutes per UTC day including download, and under 10 minutes for the six dates above. Log bytes and elapsed time. Fail the parse step if one day exceeds 120 seconds.

### UNCERTAIN

- HTTP 500 on a `.zip` URL is ambiguous. The missing 1999 key failed the same way, and the readable S3 error this session was only the bucket-list "Access Denied". A client that can save the body, or an XML `InvalidObjectState` / `NoSuchKey`, would settle the Glacier claim and whether 14 Oct 2024, 9 Apr 2025, and 13 Oct 2026 are actually downloadable.
- The May 2025 guide says files last 366 days and start 29 Dec 2023. The dashboard API returned 404 for 11 Oct 2024 and not for 9 Apr 2025. Those two statements agree only if the 500s are real zip responses. That is not shown.
- DTCC republication rights are not in the terms text that rendered. The guide's "all rights reserved" is the strongest clause read.
- OIS, CPI, and cross-currency rows were not seen, so the product-name and which-leg-carries-the-spread rules above are filters to test, not confirmed labels. Basis sign and spread units depend on `Spread notation`.
- The par breakeven is a par minus par-real identity. A zero-coupon CPI swap is a different instrument. The 2y has no real yield on this feed.
- BoE "latest" being one month is taken from the page's own "latest month" wording. The zip was not opened. The OIS curve's source line names Bloomberg, and the OGL excludes third-party rights the Bank cannot license.
- No Treasury copyright sentence was on the feed or the rates page. The semiannual coupon fact is from the bill-rate note on that same rates page.

### NOT DONE

- Swap-spread medians at 2/5/10/30y, the ACT/360 versus bond-equivalent band, n, IQR, and IQR/√n, on all three dates. The zip bytes never became rows, and this session could not unpack a zip.
- 10y CPI swap minus the 2.33 pp par breakeven.
- JPY/USD and EUR/USD 1–3y spread medians, including the unverified −39/−49/−39 bp and −1/−7/−4 bp prints.
- Quiet-period day-to-day dispersion of the swap series, and therefore the smallest basis-point move that series can resolve.
- An S3 body that says `InvalidObjectState` for a pre-14 Oct 2024 file, or a successful GET for a later file.
- A DTCC clause that allows a published derived series.
- The BoE latest and archive zips were not opened. UK curves are outside the first test's arithmetic.

---

## Item 4: The yen against the rate gap: first price-side FX decomposition

*Status SUCCESS; 1141 s; breaches 0, blocked 0, unexpected tools 0, stage changes 0.*

*Cited without a fetch in this call, not relied on:* `https://api.github.com/repos/closeofbusiness/market-plumbing/contents/data/vintages/r3`; `https://api.statistiken.bundesbank.de/rest/data/BBSSY/D.REN.EUR.A630.000000WT1010.A?startPeriod=2023-12-29&endPeriod=2023-12-29&format=csv`; `https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y+SR_2Y?format=csvdata`; `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve&field_tdr_date_value={year}&page&_format=csv`; `https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/D.JP.JPY.A`; `https://www.ecb.europa.eu/services/data-reuse/html/index.en.html`; `https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/qa.htm`


**Supervisor check.** BIS `D.JP.JPY.A` re-fetched: 141.475113 on 29 Dec 2023 and 157.888307 on 18 Sep 2026. Both match. The Treasury rows match the 2026 CSV used for items 1 and 3. No regression was run; the endpoint and path rows are arithmetic on those prints. The JGB and ECB legs are relayed.


### SOURCES

| Source | URL fetched | Free? | Terms quote | What it holds |
| --- | --- | --- | --- | --- |
| BIS USD rates, yen | `https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/D.JP.JPY.A` (dated CSV pulls) | Yes, no login | "if the statistics are reproduced, the BIS must be cited" | Daily average yen per 1 USD |
| BIS USD rates, euro | same API, key `D.XM.EUR.A` | Yes, no login | same BIS sentence | Daily average euro per 1 USD |
| BIS statistics terms | `https://data.bis.org/help/legal` | Yes | same citation sentence | Reuse terms. The older permitted-use URL returned Access denied |
| US Treasury par yields | `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve&field_tdr_date_value={year}&page&_format=csv` for 2023, 2024, 2025, 2026 | Yes, no login | Not read. The data.gov catalog page timed out | Daily par yields, percent. Headers include `2 Yr` and `10 Yr`. A month filter was ignored and returned the year |
| MoF JGB curve | `https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv` | Yes, no login | "Public Data License (Version 1.0; PDL 1.0) applies unless any rights are indicated." | Daily constant-maturity yields, percent. The fetch returned only the 1974 start |
| MoF notice | `https://www.mof.go.jp/english/about_mof/notice/index.html` | Yes | same PDL sentence | Points at PDL 1.0 |
| Japan PDL 1.0 | `https://www.digital.go.jp/en/resources/open_data/public_data_license_v1.0` | Yes | "Commercial use of “This Content” is also permitted." | Open-data licence. Numerical data are outside copyright |
| MoF yield definition | `https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/qa.htm` | Yes | n/a (definition, not a licence) | "semiannual compound interest rate on a constant maturity basis" |
| MoF intervention, 2026 Q2 | `https://www.mof.go.jp/english/policy/international_policy/reference/feio/quarter/2026_2Qe.html` | Yes, no login | same MoF PDL sentence | Daily yen amounts, released 7 Aug 2026 |
| MoF intervention, Jul–Aug 2026 | `https://www.mof.go.jp/english/policy/international_policy/reference/feio/monthly/20260828e.html` | Yes, no login | same MoF PDL sentence | One period total, released 28 Aug 2026. No daily split |
| ECB AAA spot curve | `https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y+SR_2Y?format=csvdata` for 2023-12-29, 2025-04-04–11, and 2026-09-18–24 | Yes, no login | Not found. `https://www.ecb.europa.eu/services/data-reuse/html/index.en.html` returned 404 | AAA nominal Svensson spot, continuous compounding, percent |
| Programme extracts | `https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/data/r1_rates/levels.csv`, `data/r3_rates/jp_levels.csv`, `data/r3_rates/jp_changes.csv`, `data/r3_rates/ea_levels.csv` | Yes, public raw | Repository files, not a primary licence | Five dates each. US rows re-checked on the Treasury CSV. JGB rows were not re-read from MoF |
| Daily JGB vintage | `https://api.github.com/repos/closeofbusiness/market-plumbing/contents/data/vintages/r3` | — | — | 404. Not on `main` |
| Bundesbank current 10y | `https://api.statistiken.bundesbank.de/rest/data/BBSSY/D.REN.EUR.A630.000000WT1010.A?startPeriod=2023-12-29&endPeriod=2023-12-29&format=csv` | — | — | HTTP 500. On-the-run Bund, not constant maturity |

### RESULTS

Units: Treasury and JGB yields are percent per year. ECB spots are percent per year, continuous compounding. BIS FX is foreign currency per 1 USD, daily average. Log changes are natural logs of the ratio of those levels. Gap means US par minus the foreign yield, in percentage points. Association only: none of these rows is a fitted residual, and none reads a flow as the cause of a price.

| Finding | Value | Grade | Window / denominator | Source URL | Quote or row |
| --- | --- | --- | --- | --- | --- |
| USD/JPY level | 141.475113 | MEASURED | 2023-12-29; yen per USD | BIS `D.JP.JPY.A` | Item’s 141.475 |
| USD/JPY level | 157.888307 | MEASURED | 2026-09-18; yen per USD | BIS `D.JP.JPY.A` | Item’s 157.888 |
| Log change, yen | 157.888307 / 141.475113 = 1.116015; Δln = +0.10976 | IDENTITY from those two prints | 2023-12-29 to 2026-09-18; BIS daily average | BIS `D.JP.JPY.A` | Dollar stronger against the yen |
| 2026 peak in the fetched sample | 163.913082 on 2026-07-28 | MEASURED | BIS daily averages fetched 2026-01-02 through 2026-10-06 | BIS `D.JP.JPY.A` | Item’s 163.9 |
| 30 Jul print | 162.940049 | MEASURED | 2026-07-30; same BIS series | BIS `D.JP.JPY.A` | Matches 162.94 to two decimals |
| US 10y par | 3.88 on 2023-12-29; 5.01 on 2026-09-18; change +1.13pp | MEASURED | those dates; percent par | Treasury 2023 and 2026 CSVs, column `10 Yr` | Matches `levels.csv` and state.md |
| US 2y par | 4.23 on 2023-12-29; 4.76 on 2026-09-18; change +0.53pp | MEASURED | those dates; percent par | Treasury CSVs, column `2 Yr` | Matches `levels.csv` |
| US on the JGB end date | 10y 5.18, 2y 4.87 | MEASURED | 2026-09-24; percent par | Treasury 2026 CSV | 17bp and 11bp above 18 Sep |
| JGB levels used for gaps | 2023-12-29: 10y 0.647, 2y 0.048. 2026-09-24: 10y 3.073, 2y 1.912 | BOUNDED | those dates; percent, semiannual compound constant maturity | `jp_levels.csv` | MoF file was not re-read past 1974. 3.073 − 0.647 = 2.426pp; `jp_changes.csv` rounds that to +243bp |
| Same-day 10y gap | 3.233 to 2.107; change −1.126pp | BOUNDED | 2023-12-29 to 2026-09-24; US par minus repo JGB | Treasury rows minus `jp_levels.csv` | 3.88−0.647=3.233; 5.18−3.073=2.107 |
| Same-day 2y gap | 4.182 to 2.958; change −1.224pp | BOUNDED | same dates and denominator | same | 4.23−0.048=4.182; 4.87−1.912=2.958 |
| The item’s 1.3pp | +1.13pp US to 18 Sep minus +2.43pp JGB to 24 Sep = −1.30pp | IDENTITY on those printed legs | mixed end dates, four business days apart | Treasury 18 Sep; `jp_changes.csv` 24 Sep | Both tenors narrow by about 1.1–1.2pp on the same-day window, so the endpoints do not separate 2y from 10y |
| Path of the 10y gap and USD/JPY | 2023-12-29→2024-12-30: gap +0.206pp, Δln FX +0.10777 (157.573727 / 141.475113). →2025-12-30: gap −1.365pp, Δln FX −0.00965 (156.060219 / 157.573727). →2026-06-30: gap −0.324pp, Δln FX +0.04004 (162.43637 / 156.060219). →2026-09-24: gap +0.357pp, Δln FX −0.02230 (158.854579 / 162.43637) | FX MEASURED; gaps BOUNDED | subperiod endpoints; US `10 Yr` on the JGB date minus repo JGB 10y. 2024-12-30 US 10y is 4.55 (4.58 is 31 Dec). 2025-12-30 US 10y is 4.14 | Treasury year CSVs; BIS `D.JP.JPY.A`; `jp_levels.csv` | Sum of the four Δln equals the full-span Δln to 24 Sep, +0.11587. Signs agree in the first two stretches and disagree in 2026 |
| EUR/USD control | BIS euro per USD 0.904977 → 0.8726, so USD per EUR 1.105000 → 1.146000; Δln = +0.03643 | MEASURED | 2023-12-29 to 2026-09-18; dollars per euro | BIS `D.XM.EUR.A` | Dollar weaker against the euro while stronger against the yen |
| US minus ECB AAA | 10y gap 1.799 to 1.480, change −0.319pp. 2y gap 1.794 to 1.545, change −0.249pp | BOUNDED | 2023-12-29 to 2026-09-18; US par minus AAA continuous spot | Treasury rows; ECB `SR_10Y` 2.0808856999 → 3.529753074; `SR_2Y` 2.4363455063 → 3.2152124072 | Different instruments. 2026-09-24 AAA 3.5661681763 and 3.2294000719 match `ea_levels.csv` |
| Week containing 9 Apr 2025 | Fri 4 Apr to Fri 11 Apr: USD/JPY 145.211178 → 142.843293, Δln −0.01644. USD per EUR Δln +0.02580 (EUR per USD 0.904404 → 0.881368). US 2y 3.68 → 3.96; US 10y 4.01 → 4.48. AAA 2y 1.8215221075 → 1.7300159396; AAA 10y 2.6475520891 → 2.6037026531. US−AAA gap changes +0.372pp (2y) and +0.514pp (10y) | Legs MEASURED; mixed-convention gap BOUNDED | one week; raw changes, not a residual | BIS both keys; Treasury 2025 CSV; ECB pull for 2025-04-04 to 2025-04-11 | Wednesday 9 Apr itself: USD/JPY 144.508828, US 2y 3.91, US 10y 4.34, AAA 2y 1.7508397125, AAA 10y 2.6865951501. Japan yields that week were not read |
| Dated Q2 2026 intervention | 30 Apr ¥6,278.7bn; 4 May ¥780.2bn; 6 May ¥4,675.9bn. Page total ¥11,734.9bn (day sum 11,734.8) | MEASURED | those days; billion yen, dollars sold for yen | MoF `2026_2Qe.html` | Spot, BIS daily average: 29 Apr 159.789851 → 30 Apr 156.562981 (Δln −0.02040). 30 Apr → 4 May 157.119658 (Δln +0.00355). 5 May 157.812767 → 6 May 156.214929 (Δln −0.01018). US 10y those days: 4.42, 4.40, 4.45, 4.43, 4.36 |
| Jul–Aug 2026 intervention | ¥15,399.3bn for 30 Jul–26 Aug, released 28 Aug 2026 | MEASURED | that period total; billion yen | MoF `20260828e.html` | No official day list. Nearby BIS prints: 28 Jul 163.913082, 30 Jul 162.940049, 31 Jul 160.235089, 3 Aug 156.679671. US 10y: 4.61, 4.68, 4.75 on 28, 30 and 31 Jul |

The 2024–26 claim that the yen move is unexplained by rates stays **HYPOTHESIS**. The weekly coefficients, standard errors, R² and cumulative residual were not computed. A large persistent residual is not established by endpoints: the 10y gap widened in 2024 while USD/JPY rose, narrowed by 1.37pp in 2025 while USD/JPY barely fell, then narrowed and later widened in 2026 with the opposite FX sign in both of those stretches.

### PRE-REGISTRATION

Dated 14 Oct 2026, written before any coefficient. The item’s windows are the specification. Operational Friday bounds, assuming 18 Sep 2026 is a Friday because 14 Oct 2026 is a Wednesday:

- W1: week-ending Fridays 2018-01-05 through 2021-12-31
- W2: 2022-01-07 through 2023-12-29
- W3: 2024-01-05 through 2026-09-18

Horizon: the contemporaneous week only. Dependent variable: weekly change in the natural log of the spot. USD/JPY uses BIS yen per dollar. EUR/USD uses dollars per euro, the reciprocal of BIS euro per dollar. Regressors: weekly change in the 2y gap and the 10y gap, percentage points, same week, no leads and no lags. Japan gap: Treasury par minus MoF constant-maturity. Euro gap in this build: Treasury par minus ECB AAA continuous spot, until a Bund par series returns. Week end is Friday, or the previous common business day. Sample is the intersection of dates. The item sets no residual-share cutoff and names no unreleased print to forecast, so no numeric range was added. Series through 18 Sep 2026 were already public.

### WHAT IT CHANGES

State.md still stands on the sentence that matters: FX is a flow map with no price-side decomposition and no repeatable ledger script. This pass does not supply that table, so it does not move flow items 1, 3, 11 and 12 to the core of FX, and it does not show that a front-end gap explains the yen.

It does fix the motivating comparison. The 1.3pp narrowing pairs the US 10y on 18 Sep 2026 with the JGB 10y on 24 Sep 2026. On a shared end date, 24 Sep, both the 2y and 10y gaps are narrower by a bit more than 1.1pp, while log USD/JPY is higher by 0.116. Over the same 18 Sep span, log dollars-per-euro is higher by 0.036 and the US–AAA gaps are narrower by about 0.25–0.32pp. The two crosses did not move as one dollar move.

The BIS levels named in the item check out, including 141.475113, 157.888307 and the 28 Jul 2026 peak of 163.913082 inside the fetched 2026 sample. The 30 Jul figure of 162.94 is that same BIS series. The Jul–Aug 2026 daily intervention split remains unpublished, which is what state.md already says.

### BUILD SPEC

Script: `bin/fx_rate_gap.py`. Runtime: under 3 minutes. The MoF history file dominates; the regression itself is seconds.

Inputs:

- BIS `D.JP.JPY.A` and `D.XM.EUR.A`, `startPeriod=2018-01-01`, `endPeriod=2026-09-18`, `format=csv`. USD per EUR = 1 / euro per USD.
- Treasury par CSVs for 2018–2026 from the year URL above. Select `2 Yr` and `10 Yr` by header. Files from 2025 add a `1.5 Month` column.
- MoF `jgbcme_all.csv`, header on the second row, missing as `-`, columns `2Y` and `10Y`. The GitHub path `data/vintages/r3/jgbcme_all.csv` 404s, so the script reads the MoF URL.
- ECB `YC` keys `B.U2.EUR.4F.G_N_A.SV_C_YM.SR_2Y` and `SR_10Y`.
- Intervention: `2026_2Qe.html`, the quarterly index, and `20260828e.html`. Flag 30 Jul–26 Aug 2026 as a period total until the Q3 daily release.
- Policy-rate gaps are the rest of the item, after the 2y/10y table. Their codes were not fetched here; the script must resolve Fed, BoJ and ECB policy rates and assert a non-empty response. No FRED.

Outputs:

- `data/fx_rate_gap/weekly_panel.csv`: `week_end`, `usdjpy`, `eur_per_usd`, `usd_per_eur`, `us2`, `us10`, `jp2`, `jp10`, `aaa2`, `aaa10`, `gap_jp_2y`, `gap_jp_10y`, `gap_ea_2y`, `gap_ea_10y`, `dln_usdjpy`, `dln_eurusd`, `d_gap_jp_2y`, `d_gap_jp_10y`, `d_gap_ea_2y`, `d_gap_ea_10y`, `intervention_yen_bn`, `marker_2025_04_09`.
- `data/fx_rate_gap/ols_by_window.csv`: `pair`, `window`, `n`, `beta_2y`, `se_2y`, `beta_10y`, `se_10y`, `r2`, `cum_dln`, `cum_fitted`, `cum_resid`.
- `data/fx_rate_gap/event_weeks.csv`: the same residual columns for each official intervention date and for the week of 9 Apr 2025.

Assert: 2023-12-29 USD/JPY = 141.475113; 2026-09-18 = 157.888307; 2026-07-28 = 163.913082 and is the max of the 2026 sample through the file end; 2026-07-30 = 162.940049; Treasury 2023-12-29 is 4.23 and 3.88; 2026-09-18 is 4.76 and 5.01; 2026-09-24 is 4.87 and 5.18; MoF 2023-12-29 is 0.048 and 0.647; MoF 2026-09-24 is 1.912 and 3.073; ECB 2023-12-29 `SR_2Y` = 2.4363455063 and `SR_10Y` = 2.0808856999; ECB 2026-09-18 `SR_2Y` = 3.2152124072 and `SR_10Y` = 3.529753074; Q2 2026 days are exactly 2026-04-30, 2026-05-04 and 2026-05-06 at 6278.7, 780.2 and 4675.9 billion yen. The design matrix has no leads or lags. The output text does not say that intervention leaned against rates.

### UNCERTAIN

- JGB 2y and 10y on the five key dates come from `jp_levels.csv`. The official CSV was fetched and confirmed to exist, but its 2023–26 rows were not returned.
- The JGB print for 18 Sep 2026 is unread, so a same-day gap on the item’s FX end date is unknown. The same-day figure used here ends 24 Sep.
- No second publisher was fetched for 162.94 on 30 Jul 2026. The BIS print equals that number to two decimals.
- The 2026 maximum is inside files fetched through 6 Oct 2026. 7–14 Oct was not fetched.
- Treasury reuse terms were not on a page that returned. A search listing pointed at CC0; that catalog page was not read. The CC0 deed itself does not name this series.
- ECB statistics-reuse terms were not found. The data API did return the yields.
- Bundesbank on-the-run yields were not read (HTTP 500). `ea_levels.csv` Bund columns were therefore unused. ECB AAA spot is not a Bund par yield.
- The first Fridays of 2018, 2022 and 2024 were taken from the calendar, not from a fetched holiday file.
- Historical intervention CSV links did not survive the index-page fetch. Days before 2026 Q2 were not listed.

### NOT DONE

- The first test itself: weekly OLS of Δlog USD/JPY and Δlog EUR/USD on Δ2y and Δ10y gaps in W1, W2 and W3, with standard errors, R², cumulative fitted value and cumulative residual. Shell and code execution were not allowed, and a few hundred weekly rows were not inverted by hand.
- Dating those residuals on intervention days and on 9 Apr 2025.
- Official daily dates inside 30 Jul–26 Aug 2026.
- Any 2018–21 or 2022–23 yield or FX calculation beyond locking the windows.
- Policy-rate gaps, and real or breakeven gaps.
- A sentence in which intervention explains, or leans against, the rate move.

---

## Item 5: Copper visible-stock ledger from Cochilco (LME, COMEX, SHFE), with the printed y/y column corrected

*Status SUCCESS; 704 s; breaches 0, blocked 0, unexpected tools 0, stage changes 0.*

*Cited without a fetch in this call, not relied on:* `https://boletin.cochilco.cl/productos/boletin.asp?anio=YYYY&mes=MM&tabla=tabla4_1`; `https://www.cochilco.cl/web/historico-inventarios-mundiales-de-cobre/`


**Supervisor check.** Cochilco's weekly report for 5–9 Oct 2026 was re-fetched. LME 233,025, COMEX 711,610, SHFE 58,744, total 1,003,379. The printed Var. Anual column reads +14.6%, +523.6%, −45.3% and +136.1%. All match. Grok's frozen-base finding reproduces: 711,610 / 114,113 − 1 = +523.6%. That is a defect in Cochilco's weekly column, not in this programme. E-021's "about 93 kt on the year" is the year-on-year change (+93.6 kt), so it stands. The note now also gives the window and the +87.7 kt rise since 2 Jan. Monthly table 4.1 and the July and August weeklies are relayed.


### SOURCES

| Source | URL fetched | Free? | Terms quote | What it holds |
|---|---|---|---|---|
| Weekly index | https://www.cochilco.cl/web/informe-semanal-del-cobre/ | Yes, no login | No reuse sentence on the page | List of weekly copper reports, 2024 through the week of 5–9 Oct 2026 |
| Weekly PDF, 9 Oct 2026 | https://www.cochilco.cl/web/download/1006/2026/16972/informe-del-mercado-internacional-del-cobre-semana-del-5-a-9-de-octubre-de-2026.pdf | Yes, no login | "Fuentes: LME · COMEX · SHFE · Refinitiv" | Levels, weekly changes, and a printed Var. Anual column, labelled TM |
| Weekly PDF, 6–9 Oct 2025 | https://www.cochilco.cl/web/download/969/2025/14926/informe-del-mercado-internacional-del-cobre-semana-del-6-a-9-de-octubre-de-2025.pdf | Yes, no login | No reuse sentence in the extracted text | Year-ago LME, COMEX, SHFE and the three-exchange total, in tonnes |
| Weekly PDF, 2 Jan 2026 | https://www.cochilco.cl/web/download/1006/2026/15256/informe-del-mercado-internacional-del-cobre-semana-del-29-de-diciembre-de-2025-al-2-de-enero-de-2026.pdf | Yes, no login | No reuse sentence in the extracted text | LME 145,325 t, COMEX 451,833 t, SHFE 111,703 t, total 708,861 t |
| Weekly PDFs, 10 Jul, 17 Jul, 14 Aug 2026 | https://www.cochilco.cl/web/download/1006/2026/16661/informe-del-mercado-internacional-del-cobre-semana-del-6-a-10-de-julio-de-2026.pdf ; https://www.cochilco.cl/web/download/1006/2026/16676/informe-del-mercado-internacional-del-cobre-semana-del-13-al-17-de-julio-de-2026-2.pdf ; https://www.cochilco.cl/web/download/1006/2026/16753/informe-del-mercado-internacional-del-cobre-semana-del-10-a-14-de-agosto-de-2026.pdf | Yes, no login | Same Refinitiv footer | Four-report test of the printed Var. Anual column |
| Bulletin table 4.1, Sep 2026 | https://boletin.cochilco.cl/productos/boletin.asp?anio=2026&mes=09&tabla=tabla4_1 | Yes, no login | No reuse sentence on the page | Month-end LME, COMEX, SHFE, total, in "TM Fin de Período / MT at Close", through Sep 2026, including Dec 2024 |
| Bulletin table 4.2, Jul 2025 | https://boletin.cochilco.cl/productos/boletin.asp?anio=2025&mes=07&tabla=tabla4_2 | Yes, no login | "obtenida a través de Reuters" | Daily stocks by exchange, header "(TM / MT)", COMEX in the same total as LME |
| La Rueda, 9 Oct 2026 | https://www.cochilco.cl/web/download/1037/octubre-2026/16969/rueda-09-10-2026.pdf | Yes, no login | "Se autoriza la reproducción total o parcial, citando la fuente" | Daily LME, COMEX and SHFE stocks in T.M.; also "Fuente: LSEG" |
| Open-data record | https://datos.gob.cl/dataset/4e3f3c68-3ede-449b-988d-835fd62fc139 and https://datos.gob.cl/api/3/action/package_show?id=4e3f3c68-3ede-449b-988d-835fd62fc139 | Yes, no login | "copy, modify, distribute and perform the work, even for commercial purposes" (CC0 deed at https://creativecommons.org/publicdomain/zero/1.0/) | Portal record for Jan 1990–Dec 2023. The resource URL is the HTML page below, not an xlsx |
| Historical page | https://www.cochilco.cl/web/historico-inventarios-mundiales-de-cobre/ | Yes, no login | "Archivos de datos históricos en formato Excel al año 2023" | Claims monthly and annual Excel through 2023. Direct file URL was not in the fetch |
| Current workbook page | https://boletin.cochilco.cl/estadisticas/inventarios.asp | Yes, no login | No reuse sentence on the page | "Inventarios Mundiales de Cobre", monthly 55 KB and annual 29 KB. The href did not survive the fetch |
| Programme notes | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-10-12-E021-Where-The-Money-Comes-From-Rates-FX-Commodities.md and https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/_research/2026-10-12-E021-commodities-inhouse-return.md | Public repo | Repository content | E-021 repeats "up about 93 kt on the year". The in-house return has the two LME levels and does not print 93 kt or +523.6% |

The file named `inventarios-mundiales-del-cobre-mensual-2.xlsx` was not found. GitHub code search returned HTTP 401, so the note check is the two files above plus a web search of the repo that returned no hits.

### RESULTS

Levels are metric tonnes. Chilean PDFs use `.` as the thousands separator.

**Identity, 9 Oct 2026.** LME 233,025 + COMEX 711,610 + SHFE 58,744 = 1,003,379. Weekly changes −11,875 + 4,792 + 20,000 = +12,917. Grade IDENTITY. Window: the 9 Oct 2026 report. Same identity on 9 Oct 2025: 139,475 + 304,380 + 95,034 = 538,889. And on 2 Jan 2026: 145,325 + 451,833 + 111,703 = 708,861.

**Year-on-year from levels, 9 Oct 2025 to 9 Oct 2026.** Denominator is each series’ own 9 Oct 2025 level.

| Series | 9 Oct 2025 | 9 Oct 2026 | Change | Computed y/y | Printed Var. Anual |
|---|---:|---:|---:|---:|---:|
| LME | 139,475 | 233,025 | +93,550 | +67.1% | +14.6% |
| COMEX | 304,380 | 711,610 | +407,230 | +133.8% | +523.6% |
| SHFE | 95,034 | 58,744 | −36,290 | −38.2% | −45.3% |
| Total | 538,889 | 1,003,379 | +464,490 | +86.2% | +136.1% |

Grade MEASURED. The printed column is not this change.

**The printed column uses one frozen base.** These four levels reproduce every printed percentage on 10 Jul, 17 Jul, 14 Aug and 9 Oct 2026 when the percentage is rounded to one decimal: LME 203,400 t, COMEX 114,113 t, SHFE 107,380 t, sum 424,893 t. Example for 9 Oct: 711,610 / 114,113 − 1 = 523.601%, which prints as +523.6%; 1,003,379 / 424,893 − 1 = 136.149%, which prints as +136.1%. Those bases are not the 9 Oct 2025 levels. They sit between the March 2025 and April 2025 month-ends in table 4.1 (end-March total 533,920 t; end-April total 420,113 t). Grade MEASURED. Window: those four 2026 Fridays. Denominator: this frozen triple, not the matching week of 2025.

**The monthly bulletin’s own percent change is computed from levels.** September 2026 versus September 2025, table 4.1: LME 249,400 / 143,400 − 1 = 73.9%; COMEX 703,813 / 294,007 − 1 = 139.4%; SHFE 38,744 / 95,034 − 1 = −59.2%; total 991,957 / 532,441 − 1 = 86.3%. Those match the bulletin’s printed row. Grade MEASURED. The defect is the 2026 weekly Var. Anual column.

**COMEX share of three-exchange visible stocks.** Denominator is LME + COMEX + SHFE.

| Date | COMEX | Total | Share |
|---|---:|---:|---:|
| 31 Dec 2024 | 84,514 | 430,086 | 19.7% |
| 9 Oct 2025 | 304,380 | 538,889 | 56.5% |
| 31 Dec 2025 | 451,833 | 710,961 | 63.6% |
| 30 Sep 2026 | 703,813 | 991,957 | 71.0% |
| 9 Oct 2026 | 711,610 | 1,003,379 | 70.9% |

Grade MEASURED. Cochilco prints 70.9% for 9 Oct 2026. 711,610 / 1,003,379 = 70.92%.

**Accounting split, 31 Dec 2024 to 9 Oct 2026.** Total +573,293 t. COMEX +627,096 t. LME −38,375 t. SHFE −15,428 t. The non-US decline is 53,803 t, which equals the COMEX rise minus the rise in the total. Grade IDENTITY. Over the matched year 9 Oct 2025 to 9 Oct 2026, non-US stocks rose by 57,260 t (LME +93,550, SHFE −36,290) while COMEX rose 407,230 t. The share shift is measured. A transfer of existing metal accounts for the 53,803 t non-US decline since end-2024, which is 8.6% of the COMEX increase. The rest of the COMEX increase equals the rise in the three-exchange total.

**LME from 2 Jan 2026 to 9 Oct 2026.** 233,025 − 145,325 = +87,700 t, which is +87.7 kt. Grade MEASURED. Denominator: the 2 Jan level. E-021’s "about 93 kt" equals the year-on-year tonne change (+93.6 kt), not this window.

**Units.** Table 4.2 is headed "(TM / MT)", and on 31 Jul 2025 its COMEX close of 233,977 t matches table 4.1. The three columns add to the printed total. Grade MEASURED for the common tonne label. The short-ton conversion factor was not on the page.

**Share of world stocks.** The published total is the three exchanges. China bonded metal and off-warrant metal are outside it by the series definition. Grade IDENTITY for that coverage. No world-stock denominator was in the fetched pages, so a share of world stocks has no value.

**Tariff arbitrage.** The weekly prose links the US stock to tariff uncertainty and a COMEX premium. The proclamation was not fetched. Grade HYPOTHESIS. This pass does not treat the stock move as the cause of the price.

### WHAT IT CHANGES

State.md says COMEX and SHFE copper stocks are unavailable and that copper has only a COT ledger. That stock gap is partly closed. Cochilco publishes the three exchanges, free and without login, in tonnes, and they add up. On 9 Oct 2026, 70.9% of that visible total sat on COMEX, against 56.5% a year earlier and 19.7% at end-2024.

The COT line is unchanged: managed money can be flat while the warehouse location changes. Those are different objects. The location share is now a measured fact about exchange-visible metal. It is not a share of world stocks, and it does not identify tariff arbitrage.

Correction to register against E-021 (12 Oct 2026), which says LME stocks are "up about 93 kt on the year (relayed by Grok)":

- From 2 Jan 2026 to 9 Oct 2026 the fetched levels give +87.7 kt.
- From 9 Oct 2025 to 9 Oct 2026 they give +93.6 kt.
- "About 93 kt" matches the second window. It should not be used as the 2026 rise from 2 January.
- The in-house return already had 233.0 kt on 9 Oct and 145.3 kt on 2 Jan, from Westmetall. Those match Cochilco. Their difference is 87.7 kt.

The defective +523.6% and +136.1% were not in E-021 or the in-house return. They are still printed in Cochilco’s own 9 Oct 2026 weekly table. The monthly bulletin’s September percent-change row is the one that matches the levels.

Still open in state.md: no free copper futures curve, no commodity-index investment series, and no measure of bonded or off-warrant metal.

### BUILD SPEC

Script: `bin/build_copper_visible_ledger.py`. Outputs stay local. The weekly footer and table 4.2 both name Refinitiv/Reuters as the upstream source. La Rueda’s reproduction grant covers La Rueda with a Cochilco citation; it does not clear a public redistribution of the Refinitiv-sourced stock series. CC0 on datos.gob.cl covers the 1990–2023 record only.

Inputs:

- Monthly spine: `https://boletin.cochilco.cl/productos/boletin.asp?anio=YYYY&mes=MM&tabla=tabla4_1`. Latest fetched edition is `anio=2026&mes=09`.
- Daily check file: same URL with `tabla=tabla4_2`.
- Weekly index: `https://www.cochilco.cl/web/informe-semanal-del-cobre/`. Parse linked PDFs from Jan 2025 through the latest week. Do not request the xlsx by the old name until its href is read off `https://boletin.cochilco.cl/estadisticas/inventarios.asp`.
- Do not use Westmetall. Do not copy the printed Var. Anual into the year-on-year columns.

Outputs, local:

- `data/copper/copper_visible_monthly.csv`
- `data/copper/copper_visible_weekly.csv`
- `data/copper/copper_yoy_checks.csv`

Columns: `date`, `freq`, `lme_t`, `comex_t`, `shfe_t`, `total_t`, `sum_gap_t`, `comex_share`, `printed_yoy_lme`, `printed_yoy_comex`, `printed_yoy_shfe`, `printed_yoy_total`, `yoy_lme`, `yoy_comex`, `yoy_shfe`, `yoy_total`, `yoy_base_date`, `source_url`. No world-stock share column.

Assert:

- `abs(lme_t + comex_t + shfe_t - total_t) <= 1` on every row.
- 2024-12-31 = 271,400 / 84,514 / 74,172 / 430,086.
- 2025-10-09 = 139,475 / 304,380 / 95,034 / 538,889.
- 2026-01-02 = 145,325 / 451,833 / 111,703 / 708,861.
- 2026-10-09 = 233,025 / 711,610 / 58,744 / 1,003,379, with recomputed y/y +67.1 / +133.8 / −38.2 / +86.2 within 0.05 percentage point.
- Printed y/y on 2026-10-09 is +14.6 / +523.6 / −45.3 / +136.1 and is not written into `yoy_*`.
- Base 203,400 / 114,113 / 107,380 reproduces printed y/y on 2026-07-10, 2026-07-17, 2026-08-14 and 2026-10-09 within 0.05 percentage point.
- September 2026 bulletin y/y is 73.9 / 139.4 / −59.2 / 86.3.
- Unit label is TM or MT. Drop the row otherwise.

Expected runtime: about 10 minutes. The bulletin parse is seconds. The time is one polite pass over roughly 80 weekly PDFs.

### UNCERTAIN

- The 2025-layout PDFs are titled, in search results, "Agradecemos la difusión de esta información citando su fuente". That sentence was not in the extracted body. A direct look at the PDF metadata would settle it.
- Nearby integers around 203,400 / 114,113 / 107,380 may also fit. This triple fits. Uniqueness was not proved.
- The frozen base is inside April 2025. The exact day needs table 4.2 for April 2025.
- Inverting the weekly "incremento anual" gives a start-of-2025 base of about 426,000 t (708,861 / 1.664 and 538,889 / 1.265). The bulletin’s 31 Dec 2024 total is 430,086 t. The 4 kt gap is larger than one-decimal rounding. The 426,000 t figure was not printed as a stock.
- COMEX is labelled in the same TM total as LME. The short-ton factor itself was not printed, and no CME stock file was opened.
- E-021’s "on the year" is ambiguous. The two windows above are what separate 87.7 kt from 93.6 kt.

### NOT DONE

- Every week from Jan 2025 through Oct 2026 was not parsed. Six weekly dates were.
- The named workbook was not opened. The open-data record stops at Dec 2023 and points at an HTML page. The 55 KB file’s URL was not in the fetched page, so 1990–2022 was not read. Dec 2024 through Sep 2026 was read from table 4.1.
- A CME print in short tons was not fetched, so the conversion factor is unchecked.
- Full-repo search returned HTTP 401. Notes other than E-021 and the commodities in-house return were not opened for +523.6% or +136.1%.
- The tariff proclamation was not fetched.
- No world-stock series, bonded or off-warrant, was in the pages fetched.
- The correction is stated here and was not written into the repository. This pass was read-only.

---

## Item 6: R1 second opinions in hours: Cleveland Fed inflation expectations and the 5y5y forward against SPF/SEP

*Status SUCCESS; 719 s; breaches 0, blocked 0, unexpected tools 0, stage changes 0.*

*Cited without a fetch in this call, not relied on:* `https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv`; `https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/historical-data/meanlevel.xlsx`


**Supervisor check.** **This return's upper figure depends on the model vintage.** The Cleveland Fed's own workbook (`inflation-expectations.xlsx`) was re-fetched on 14 Oct and already carries the October 2026 run. It revises September 2026 to 10y expected inflation 2.5821 and inflation risk premium 0.4278, against the 2.5726 and 0.4579 Grok read through FRED. On the October vintage, expected inflation plus risk premium rose 25.1bp from Dec 2023 to Sep 2026 (2.7587 to 3.0099), not 27.2bp. The gap to TIPS (+17bp) is 8.1bp, inside the item's ~10bp threshold, so the breakeven row is not changed to a range. The model figure is reported beside it with its vintage. Dec 2023 matches exactly in both. GSW `feds200628` on 18 Sep 2026 re-derived: SVENY05 4.8191, SVENY10 4.9970, 5y5y 5.1749%. It matches. FRED refused the supervisor's script, as it always has.


### SOURCES

| Source | URL fetched | Free? | Terms quote | What it holds |
|---|---|---|---|---|
| Cleveland Fed inflation expectations | https://www.clevelandfed.org/indicators-and-data/inflation-expectations | Yes, no login | “noncommercial, personal, or educational purposes only” (privacy page) | Monthly model: expected inflation 1–30y, inflation risk premium, real risk premium, real interest rate. Inputs named on the page: Blue Chip CPI, inflation swaps, CPI, vintage FRED CPI, 1–6m T-bill CMT, 1–15y continuously compounded Treasury zeros, SPF median 10y CPI. “As TIPS are not used in the model.” Headline on 14 Oct 2026: 10y expected inflation 2.73% (next update 10 Nov 2026). Spreadsheet href did not survive the page conversion. |
| Cleveland terms | https://www.clevelandfed.org/privacy | Yes | “reproduce Federal Reserve Bank of Cleveland publications, or portions thereof” | Reuse is for noncommercial, personal, or educational use, with credit. |
| FRED tables of the Cleveland series | https://fred.stlouisfed.org/data/EXPINF10YR ; https://fred.stlouisfed.org/data/TENEXPCHAINFRISPRE ; https://fred.stlouisfed.org/data/REAINTRATREARAT10Y ; https://fred.stlouisfed.org/data/TENEXPCHAREARISPRE | Yes, no login | “Don't do any data mining, scraping or extraction of FRED data.” | Monthly percent, not seasonally adjusted, 1982-01-01 to 2026-09-01, last updated 2026-09-11 2:49 PM CDT. Source line: Federal Reserve Bank of Cleveland. The graph CSV endpoint returned HTTP 500. |
| FRED terms | https://fred.stlouisfed.org/legal | Yes | “free to access and use FRED at no cost” | Personal, non-commercial, educational use. Separate ban on use for training machine-learning systems. |
| Fed Board nominal yield curve (GSW), HTML | https://www.federalreserve.gov/data/yield-curve-tables/feds200628_1.html | Yes, no login | “information on Board's website is in the public domain and may be copied” | Staff Svensson curve. SVENYxx are continuously compounded zero yields, in percent. Page 1 includes the 18-09-2026 row. |
| Same file, CSV | https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv | Public URL; this fetch returned HTTP 500 | Same Board disclaimer | Full daily file. Not read. |
| FOMC SEP, December 2023 | https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20231213.htm | Yes, no login | Same public-domain sentence | Released 13 Dec 2023. Median longer-run federal funds rate 2.5%. |
| FOMC SEP, September 2026 | https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260916.htm | Yes, no login | Same | Released 16 Sep 2026, meeting 15–16 Sep. Median longer-run federal funds rate 3.2% (June projection on the same table: 3.1%). |
| Philadelphia Fed SPF | https://www.philadelphiafed.org/surveys-and-data/real-time-data-research/survey-of-professional-forecasters | Yes, no login | No reuse sentence on the page fetched | Survey page, documentation, and mean/median files. The historical workbook was not opened. |
| Programme note R1 | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-27-R1-Treasury-10y-Decomposition.md | Public repo | The file is the programme’s own note | Baselines: 10y +113 bp (3.88% to 5.01%), TIPS +96 bp, breakeven +17 bp. SPF years 5–10: 2.28% (deadline 6 Feb 2024) to 2.90% (2 Mar 2026), change cell +61 bp. ACM years 5–10 −56 bp; Kim-Wright −8 bp. |

### RESULTS

Levels are percent. Changes are basis points (100 × the difference in percent). Cleveland dates are the model month, which the page dates as the first of that month. The September 2026 row was published 11 Sep 2026, so it is the last run on or before 18 Sep 2026. The 14 Oct headline of 2.73% is outside the window.

| Finding | Value | Grade | Window / denominator | Source URL | Quote or row |
|---|---|---|---|---|---|
| 10y expected inflation | 2.27841034% on 2023-12-01; 2.57264358% on 2026-09-01; **+29.4 bp** | MEASURED | Model months Dec 2023 to Sep 2026. Annualised expected CPI inflation over the next 10 years. | https://fred.stlouisfed.org/data/EXPINF10YR | Rows `2023-12-01` and `2026-09-01` |
| 10y inflation risk premium | 0.48027438% to 0.45791264%; **−2.2 bp** | MEASURED | Same months. Premium, in percent, for inflation differing from expectations. | https://fred.stlouisfed.org/data/TENEXPCHAINFRISPRE | Same two dates |
| Inflation compensation (expected inflation + inflation risk premium) | 2.75868472% to 3.03055622%; **+27.2 bp** | MEASURED | Same months. Sum of the two published series. Gap versus R1’s TIPS breakeven of +17 bp is **+10.2 bp**. | Both FRED URLs above | Addition of those four cells |
| 10y real interest rate | 1.68089907% to 2.24490054%; **+56.4 bp** | MEASURED | Same months. The page’s real-rate series, the one it plots against TIPS. Gap versus R1’s TIPS yield of +96 bp is **−39.6 bp**. | https://fred.stlouisfed.org/data/REAINTRATREARAT10Y | Same two dates |
| 10y real risk premium | 1.3498560% to 1.3354966%; **−1.4 bp** | MEASURED | Same months. Compensation for unexpected changes in the real rate. | https://fred.stlouisfed.org/data/TENEXPCHAREARISPRE | Same two dates |
| GSW 5y5y forward, end of window only | SVENY05 = 4.8191, SVENY10 = 4.9970; **5y5y = 5.1749%** continuously compounded (2×4.9970 − 4.8191) | MEASURED | One day, 18 Sep 2026. Average continuously compounded short rate over years 5–10, which includes a term premium. | https://www.federalreserve.gov/data/yield-curve-tables/feds200628_1.html | Row `18-09-2026` |
| SEP longer-run federal funds | 2.5% (13 Dec 2023) to 3.2% (16 Sep 2026); **+70 bp** | MEASURED | Median participant’s longer-run appropriate funds rate. A different object from the 5y5y forward. | The two `fomcprojtabl` URLs above | Table 1, federal funds rate, longer-run median |
| SPF bill rate, years 5–10 | 2.28% to 2.90%; R1’s change cell **+61 bp** | MEASURED in R1; not recomputed here | Deadlines 6 Feb 2024 to 2 Mar 2026. Implied as (10 × the 10-year average − 4 × years 1–4) / 6. Printed levels differ by 62 bp at two decimals. | R1 URL above | Survey table, change row |

Swaps, surveys, and TIPS are linked. The Cleveland model is built from Treasury zeros, inflation swaps, Blue Chip, CPI, and the SPF, and the page uses the TIPS comparison as an out-of-sample check. A match would be a consistency check. These pieces are changes in published rates. Nothing here identifies a flow as the source of the yield move.

The four Cleveland changes do not add to the +113 bp nominal rise (expected inflation +29.4, inflation risk premium −2.2, real rate +56.4, real risk premium −1.4). They are model outputs set beside R1, not a split of the par yield. R1’s own identity still holds inside the Treasury curves: TIPS +96 bp and breakeven +17 bp sum to the +113 bp nominal rise.

### WHAT IT CHANGES

The breakeven line in `state.md` should be a range. Cleveland inflation compensation rose 27.2 bp against the TIPS breakeven of +17 bp. The difference is 10.2 bp, which is the item’s threshold of about 10 bp, so the row is about **+17 bp (TIPS) to +27 bp (Cleveland expected inflation plus inflation risk premium)** over this window.

The real-yield comparison is wider. The model’s 10-year real rate rose 56.4 bp against TIPS +96 bp, a gap of 39.6 bp. The page already treats that TIPS-versus-model gap as taxes, liquidity, and the embedded option. The market fact in `state.md` stays: the nominal +113 bp splits as TIPS +96 and breakeven +17 inside the Treasury curves. The model real rate is a second series and rose by about 56 bp.

C-125 stays unresolved. The 5y5y change was not measured, so it cannot be lined up with ACM (−56 bp) or the SPF (+61 bp). The SEP longer-run median rose 70 bp, from 2.5% to 3.2%, which matches the figure already in R1 and in the same direction as the SPF. It is a longer-run policy median, not the market 5y5y, so it does not narrow the flag.

### BUILD SPEC

`bin/r6_cleveland_gsw_check.py`. Expected runtime under two minutes if the yield-curve CSV returns; the Cleveland series are a few hundred monthly rows.

**Inputs**

- Cleveland workbook. Read the href from https://www.clevelandfed.org/indicators-and-data/inflation-expectations. Do not guess the path. Columns needed: date, 10y expected inflation, inflation risk premium, real interest rate, real risk premium.
- Fallback already read: the four FRED table URLs above, series `EXPINF10YR`, `TENEXPCHAINFRISPRE`, `REAINTRATREARAT10Y`, `TENEXPCHAREARISPRE`. FRED’s terms restrict scraping, and the programme already finds that FRED refuses scripts, so the Cleveland file is the input to keep.
- GSW: https://www.federalreserve.gov/data/yield-curve-tables/feds200628.csv. Parse from the header row that contains `Date`, `SVENY05`, `SVENY10`. This environment got HTTP 500; the HTML pages `feds200628_1.html` and `feds200628_2.html` are the fallback. Dates are `DD-MM-YYYY`.
- SPF, as in `bin/r1_treasury_decomposition.py`: https://www.philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/historical-data/meanlevel.xlsx, sheets `BILL10` and `TBILL`. Years 5–10 = (10 × the 10-year average − 4 × years 1–4) / 6. Deadlines from the Philadelphia Fed release-date file.
- SEP longer-run federal funds medians from the two `fomcprojtabl` pages above.

**Outputs**

- `data/r6_rates/cleveland_levels.csv`: `date`, `exp_inf_10y`, `inf_rp`, `real_rate`, `real_rp`, `infl_comp`.
- `data/r6_rates/gsw_5y5y.csv`: `date`, `sveny05`, `sveny10`, `fwd_5y5y_cc`.
- `data/r6_rates/changes.csv`: `object`, `start_date`, `end_date`, `start_level`, `end_level`, `change_bp`, `r1_bp`, `gap_bp`.

**Assert**

- Cleveland has 2023-12-01 and 2026-09-01, and no later month is used as the endpoint. The 14 Oct 2026 headline is out of the window.
- GSW has 2023-12-29 and 2026-09-18, neither missing.
- `fwd_5y5y_cc` equals `2*SVENY10 − SVENY05` within 0.1 bp.
- Flag the breakeven row for a range when the inflation-compensation change differs from +17 bp by more than about 10 bp. Record the real-rate gap against +96 bp the same way.
- Write no sentence in which a flow causes the yield change.

### UNCERTAIN

- The inflation-compensation figure is the sum of expected inflation and the inflation risk premium. The Cleveland page defines each piece and does not label that sum a breakeven. The item asks for that comparison.
- Model months (1 Dec 2023, 1 Sep 2026) are not the market dates (29 Dec 2023, 18 Sep 2026). The September 2026 model was posted 11 Sep 2026.
- “About 10 bp” is the item’s wording. The measured gap is 10.2 bp, so the range is the call taken here.
- R1 prints SPF years 5–10 as 2.28 and 2.90 and prints the change as +61 bp. The unrounded workbook would settle the 1 bp.
- The 18 Sep 2026 zeros were read from the HTML table earlier in this session and were not re-fetched after the CSV failure.

### NOT DONE

- The GSW change, and the 5y5y minus SPF/SEP gap. The CSV returned HTTP 500. Page `feds200628_2.html` starts at 07-11-2024 and the fetch ended before 29-12-2023. Page `feds200628_3.html` starts at 07-12-2022, so 29 Dec 2023 is on page 2 below the cut. No verified `SVENY05` or `SVENY10` for that date, and no search-page figure was used in its place. The same block covers 6 Feb 2024 and 2 Mar 2026, so the survey-deadline forward was not computed either.
- The Cleveland spreadsheet itself. The download link’s address was stripped in conversion, and a path was not guessed. The four FRED tables of those series were used instead.
- The SPF workbook was not opened. The +61 bp is the change cell in the fetched R1 note.

---

## Item 7: Who took the duration: N-PORT Treasury holdings by maturity as an audit of the Z.1 funds/ETF row

*Status SUCCESS; 681 s; breaches 0, blocked 0, unexpected tools 0, stage changes 0.*

*Cited without a fetch in this call, not relied on:* `https://www.sec.gov/files/dera/data/form-n-port-data-sets/2024q1_nport.zip`; `https://www.sec.gov/files/dera/data/form-n-port-data-sets/2026q3_nport.zip`; `https://www.sec.gov/files/dera/data/form-n-port-data-sets/{yyyy}q{n}_nport.zip`


**Supervisor check.** `data/r2_rates/duration_supply.csv`, column `public_10yeq_fixed_bn`: 9,539.1 (end-2023), 12,757.4 (30 Jun 2026), 12,943.0 (31 Aug 2026). All match. Z.1 table S.124.3.s (ETFs) was re-fetched: Treasury securities `LM563061103` 502.3 (2023) and 807.6 (2026:Q2). Both match. The mutual-fund and closed-end lines, and the flow tables, are relayed. No N-PORT file was read: the 2026 Q3 bulk zip is on sec.gov, which only the supervisor may fetch, with the declared contact. That is a build for the supervisor.


### SOURCES

| Source | URL fetched | Free? | Terms quote | What it holds |
| --- | --- | --- | --- | --- |
| SEC Form N-PORT data sets | https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets | Yes, no login | "we cannot guarantee the accuracy of the data" | Quarterly bulk zips, October 2019–September 2026. 2026 Q3 is listed as a ZIP of 440.95 MB. Page reviewed 30 Sep 2026. |
| Data.gov harvest of the same set | http://catalog.data.gov/harvest_record/b3e700e7-6516-41a6-bdec-af7ad5f425b8/raw | Yes | "This data asset is an open government data asset." | Download URLs `https://www.sec.gov/files/dera/data/form-n-port-data-sets/{yyyy}q{n}_nport.zip` through 2026 Q2. License link is https://www.usa.gov/government-copyright. Catalog ends 30 Jun 2026 and does not list 2026 Q3. |
| N-PORT readme | https://www.sec.gov/files/nport_readme.pdf | Yes | "provided as-filed" | Tab-delimited tables. `FUND_REPORTED_HOLDING` has `ISSUER_TYPE` and `ASSET_CAT`. `DEBT_SECURITY` has `MATURITY_DATE`. `INTEREST_RATE_RISK` has DV01 and DV100 at 3 months, 1 year, 5, 10 and 30 years. `REPURCHASE_COLLATERAL` is a separate table. |
| Form N-PORT | https://www.sec.gov/files/formn-port.pdf | Yes | "Anyone can access and download this information for free" is the EDGAR access line at https://www.sec.gov/search-filings/edgar-search-assistance/accessing-edgar-data | Issuer categories include "corporate, U.S. Treasury, U.S. government agency". Item B.3 DV01 is required only if debt positions exceed 25% of NAV, and it is the whole portfolio. Item C.10 collateral can be "U.S. Treasuries (including strips)". Money-market funds do not file. |
| Vanguard Long-Term Treasury Fund N-PORT-P | https://www.sec.gov/Archives/edgar/data/106444/000175272424222308/primary_doc.xml | Yes | Same EDGAR access line | Report date 2024-07-31. Cash Treasuries are `ASSET_CAT` `DBT` and `ISSUER_TYPE` `UST`. Fannie Mae on the same filing is `USGSE`. Futures are `DIR`, not `UST`. |
| Z.1, 11 Sep 2026 | https://www.federalreserve.gov/releases/z1/current/html/S124_1_s.htm , https://www.federalreserve.gov/releases/z1/current/html/S124_3_s.htm , https://www.federalreserve.gov/releases/z1/current/html/S124_2_s.htm , and the matching `_t` flow pages | Yes | "in the public domain and may be copied and distributed without permission" (https://www.federalreserve.gov/disclaimer.htm) | Treasury levels and flows for mutual funds, ETFs and closed-end funds. |
| Z.1 unit caption, 19 Mar 2026 vintage | https://www.federalreserve.gov/releases/Z1/20260319/html/f124.htm | Yes | Same Board disclaimer | "Billions of dollars; quarterly figures are seasonally adjusted annual rates" |
| Treasury par curve, 2023 | https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2023/all?type=daily_treasury_yield_curve&field_tdr_date_value=2023&page&_format=csv | Yes | No reuse sentence on the pages fetched. The curve page says "Yields are interpolated by the Treasury from the daily par yield curve." | Daily CMT par yields. Last 2023 session is 29 Dec 2023. |
| R2 supply and script | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/data/r2_rates/duration_supply.csv and https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/bin/r2_duration_supply.py | Yes (public repo) | Programme file, not a third-party licence | Public fixed-curve 10-year equivalents, and the par-duration formula. |
| In-house N-PORT census | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/data/nport/nport_2026Q3_file_stats.csv and `bin/census_nport_bulk.py` | Yes | Programme file | AI-issuer name census of `2026q3_nport.zip`, not a Treasury maturity table. |

### RESULTS

| Finding | Value | Grade | Window / denominator | Source URL | Quote or row reference |
| --- | --- | --- | --- | --- | --- |
| Public fixed-curve 10-year equivalents, the R2 "$3.4trn" | End-2023 $9,539.1bn; 30 Jun 2026 $12,757.4bn; 31 Aug 2026 $12,943.0bn. Change to 31 Aug +$3,403.9bn. Change to 30 Jun +$3,218.3bn. One-seventh of the Aug change is $486bn; of the Jun change, $460bn. | MEASURED | Fixed end-2023 curve; denominator is the 10-year par duration, 8.223 years on 31 Dec 2023. Public means total marketable minus SOMA. | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/data/r2_rates/duration_supply.csv and `duration_supply_changes.csv` | Row `2023-12-31` `public_10yeq_fixed_bn` 9539.1; row `2026-06-30` 12757.4; row `2026-08-31` 12943.0; changes row `2023-12-31 to 2026-08-31` `d_public_10yeq_fixed_bn` 3403.9 |
| End-2023 curve used for those factors | 29 Dec 2023 (31 Dec was a Sunday). 3-month 5.40%, 6-month 5.26%, 1-year 4.79%, 2-year 4.23%, 3-year 4.01%, 5-year 3.84%, 7-year 3.88%, 10-year 3.88%, 20-year 4.20%, 30-year 4.03%. | MEASURED | Percent per year, par yields | Treasury 2023 CSV above | CSV row `12/29/2023` |
| R2 par factors, 10-year equivalents per $1 par | 3-month bill 0.0300; 6-month bill 0.0592; 1-year 0.1174; 2-year 0.2309; 3-year 0.3405; 5-year 0.5482; 7-year 0.7392; 10-year 1.000; 20-year 1.635; 30-year 2.106. Bills use \(T/(1+yT)\). Coupon bonds use \((1/y)(1-(1+y/2)^{-2T})\), then divide by 8.223. Worked 2-year: \(y=0.0423\), \((1.02115)^4=1.08732\), duration \(0.08031/0.0423=1.899\), factor \(1.899/8.223=0.231\). | MEASURED | Per $1 par of a par bond on the 29 Dec 2023 curve. This is the bucket version of R2. R2 itself prices each CUSIP. | R2 script `par_mod_duration` and `bill_price_duration`; curve CSV | `d10_par_duration` 8.223 on `2023-12-31` |
| Z.1 Treasury stock, mutual funds + ETFs + closed-end funds | End-2023: 1,389.7 + 502.3 + 2.1 = $1,894.1bn. 2026:Q2: 1,741.2 + 807.6 + 2.0 = $2,550.8bn. Market-value change +$656.7bn. | MEASURED | Billions of dollars, end of period. Series `LM653061105`, `LM563061103`, `LM553061103`. Money-market funds are not in these three tables. | September 2026 S124.1.s, S124.3.s, S124.2.s | Line "Treasury securities". On S124.1.s the 2025 column equals 2025:Q4 (1,685.2), so the annual column is the year-end stock. |
| Z.1 Treasury net purchases, same three sectors | 2024 + 2025 + 2026:Q1/4 + 2026:Q2/4 = 321.925 + 318.175 − 0.1 = $640.0bn. | MEASURED | Billions of dollars, 2024:Q1–2026:Q2. Quarterly columns are annual rates: the four 2025 ETF quarters average to 140.25 against the 2025 annual figure 140.3. | September 2026 S124.1.t, S124.3.t, S124.2.t; unit caption on the 19 Mar 2026 F.124 page | Flow lines `FA653061105`, `FA563061103`, `FA553061103` |
| Scaling that $640.0bn by the par factors | 3-month factor gives about $19bn of 10-year equivalents. 30-year factor gives about $1,348bn. | BOUNDED | Dollars of net purchases times a single par factor. Not a maturity mix, and not a price effect. | Curve, R2 formula, Z.1 flows | Spans both cutoffs in the item ($0.1trn and about $0.5trn) |
| June 2026 N-PORT Treasury holdings times those factors, and fund-level 10-year DV01 for funds with Treasury share above 50% | Not computed | — | Would be the 30 Jun 2026 report date inside the 2026 Q3 zip, one filing per series | Zip listed, body not fetched | See NOT DONE |
| 2026 Q3 filing mix in the programme census | 14,066 filings; 5,627,083 holding rows; report dates 2026-06-30 × 7,063 and 2026-07-31 × 4,195. Zip sha256 `2f5ee059234d2e28f16d0451d9fcb405aab3dad5d92cded74c8ea9ffc4b66c38`. Stream time 86.9 seconds. | MEASURED | Counts of filings in the 2026 Q3 dissemination, as previously parsed. Not re-streamed here. The script matches AI-issuer names, not `ISSUER_TYPE`. | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/data/nport/nport_2026Q3_file_stats.csv | Keys `filings_total`, `report_date_top3`, `holding_rows` |
| Bulk code for a Treasury note | `DBT` / `UST` | MEASURED | One fund, report date 2024-07-31, not the 2026 zip | Vanguard primary_doc.xml | CUSIP `912810SY5`, maturity 2041-05-15, coupon 2.25% fixed, principal $103,700,000, value $77,612,968.75, `DBT`, `UST` |

These are holdings and net purchases. Nothing here is a test that those purchases moved the 10-year yield.

### WHAT IT CHANGES

The duration split in state.md stays unmeasured. R2 already said Z.1 gives dollars, not maturities, and that who took the duration is a hypothesis. The September 2026 Z.1 vintage re-derives that funds row as $640.0bn of Treasury net purchases from 2024 through 2026:Q2, and a market-value stock of $2,550.8bn at 2026:Q2, up $656.7bn from end-2023. Multiplying the $640.0bn by the R2 par factors reaches both of the item's thresholds, so the dollar row still cannot say whether registered funds were a first-order duration sink or bystanders.

The $3.4trn figure is the public fixed-curve increase to 31 Aug 2026 (+$3,403.9bn). The N-PORT date the item lines up with, 30 Jun 2026, is +$3,218.3bn on the same column. This pass does not use the result against C-124. The local `data/nport` files do not contain Treasury maturity buckets.

### BUILD SPEC

Script: `bin/nport_treasury_duration.py`. Leave `bin/census_nport_bulk.py` as the AI-issuer census.

Inputs:

- Zips, 11 files, 2024 Q1 through 2026 Q3: `https://www.sec.gov/files/dera/data/form-n-port-data-sets/2024q1_nport.zip` through `2026q3_nport.zip`. A December 2023 report date is filed in 2024 Q1, which is why the set starts there. Declared-contact User-Agent, sec.gov hosts only.
- Tables inside each zip: `SUBMISSION.tsv` (`REPORT_DATE`, `FILING_DATE`), `FUND_REPORTED_INFO.tsv` (`SERIES_ID`, `NET_ASSETS`), `FUND_REPORTED_HOLDING.tsv` (`ISSUER_TYPE`, `ASSET_CAT`, `CURRENCY_VALUE`, `CURRENCY_CODE`, `PAYOFF_PROFILE`), `DEBT_SECURITY.tsv` (`MATURITY_DATE`, `COUPON_TYPE`, `ANNUALIZED_RATE`), `INTEREST_RATE_RISK.tsv` (the five `INTRST_RATE_CHANGE_*_DV01` columns, `CURRENCY_CODE`).
- Keep cash lines with `ISSUER_TYPE=UST` and `ASSET_CAT=DBT`. Drop `DIR`. Do not sum `REPURCHASE_COLLATERAL.tsv`.
- Curve: the 2023 Treasury CSV above, session 2023-12-29, and `par_mod_duration` / bill formula from `bin/r2_duration_supply.py`, divided by 8.223.
- Z.1 comparison series: `LM653061105`, `LM563061103`, `LM553061103` and flows `FA653061105`, `FA563061103`, `FA553061103`.
- Denominator: `public_10yeq_fixed_bn` in `data/r2_rates/duration_supply.csv`.

Outputs:

- `data/nport/treasury_buckets.csv` — `report_date`, `bucket`, `fair_value_usd_bn`, `n_lines`, `n_series`, `tenyeq_fixed_bn`, `factor`.
- `data/nport/treasury_funds_gt50.csv` — `report_date`, `series_id`, `accession`, `net_assets_usd`, `treasury_fair_value_usd`, `treasury_share`, `dv01_3m_usd`, `dv01_1y_usd`, `dv01_5y_usd`, `dv01_10y_usd`, `dv01_30y_usd`.
- `data/nport/treasury_duration_summary.csv` — one row per snapshot: bucket 10-year equivalents, sum of 10-year key-rate DV01 for series with Treasury share above 0.50, and the Z.1 dollar stock.

Assert: 2026 Q3 sha256 matches `2f5ee059234d2e28f16d0451d9fcb405aab3dad5d92cded74c8ea9ffc4b66c38` when the zip is the census file; report-date counts 7,063 on 2026-06-30 and 4,195 on 2026-07-31; one surviving filing per series at that report date, using the census survivor rule; `CURRENCY_VALUE` within $5 plus 0.01% of `PERCENTAGE/100*NET_ASSETS`; a sample of `UST` rows has Treasury in the issuer name; bucket 10-year equivalents sum to the unbucketed total. Print the Z.1 dollar gap. Do not require N-PORT to equal Z.1: Z.1 mutual funds are ICI reporters, and N-PORT also includes BDCs and interval funds, which Z.1 now tables as S124.5 and S124.6. DV01 is whole-portfolio and is missing when debt is under 25% of NAV.

Runtime: the existing census streamed 5.6 million rows in 87 seconds. Eleven quarters of holdings plus the debt and DV01 joins is about 30–45 minutes once the zips are on disk. The download is about 5 GB and is the slow part.

### UNCERTAIN

The 2026 Q3 href is inferred as `https://www.sec.gov/files/dera/data/form-n-port-data-sets/2026q3_nport.zip` from the catalog pattern. The directory URL returned 404, and the 440.95 MB body was not downloaded. A GET that returns the census sha256 would settle the URL.

The September HTML tables, as converted, did not include the "Billions of dollars" line. The 19 Mar 2026 F.124 page states that caption for the same ETF Treasury series, and the September 2025 ETF quarters average to the 2025 annual flow, which is the annual-rate convention.

`UST` was read on a 31 Jul 2024 filing. The 2026 TSV could in principle use another token. The first thousand `UST` rows of `2026q3` would settle it. The repurchase-agreement `ASSET_CAT` code was not on that filing.

Bucket factors are par bonds. R2 prices each CUSIP's coupon on the fixed curve. A 1.625% of 2050, which appears in the Vanguard filing, is not a par bond at a 4.03% 30-year yield, so a 30-year bucket factor mis-states it. CUSIP-level pricing is the check.

The $16.7bn gap between the $656.7bn market-value increase and the $640.0bn of net purchases is not a clean valuation residual: flows are seasonally adjusted and levels are not.

### NOT DONE

The first test's N-PORT half is not done. Computing Treasury fair value by remaining maturity, times the factors above, for the 30 Jun 2026 snapshot, and summing 10-year DV01 for series with Treasury share above 50%, requires streaming `FUND_REPORTED_HOLDING` (about 5.6 million rows in the 2026 Q3 file) and joining `DEBT_SECURITY` and `INTEREST_RATE_RISK`. That zip is 440.95 MB. It was not fetched whole, and there was no way here to pull only those rows. The same block applies to the other snapshots back to end-2023. No pre-registration was written: the item does not ask for one, and the 2026 Q3 dataset is already listed.

---

## Item 8: Is the swap-dealer line an index-investment proxy? Calibrate COT to the CFTC Index Investment Data, 2007-2015

*Status SUCCESS; 1044 s; breaches 0, blocked 0, unexpected tools 0, stage changes 0.*

*Cited without a fetch in this call, not relied on:* `https://publicreporting.cftc.gov/resource/72hh-3qpy.csv`; `https://www.cftc.gov/sites/default/files/idc/groups/public/@marketreports/documents/file/indexinvestmentMMYY.pdf`; `https://www.cftc.gov/sites/default/files/idc/groups/public/@marketreports/documents/file/indexinvestment{MMYY}.pdf`


**Supervisor check.** All nine correlations were recomputed from the 34-row level table in this return, and each matches to two decimals. Gold: −0.03, −0.14 and +0.10. Copper: +0.03, +0.09 and −0.01. WTI: +0.42, −0.24 and +0.38. CFTC futures-only swap-dealer rows were re-fetched for 25 Jun 2013 and 27 Oct 2015. Gold: 44,960/60,902 and 56,525/119,427. WTI: 116,253/418,565 and 227,077/272,697. All match. The index-investment figures are relayed: none of the 34 CFTC PDFs was re-read.


### SOURCES

| Source | URL fetched | Free? | Terms quote | What it holds |
| --- | --- | --- | --- | --- |
| CFTC Index Investment Data index | https://www.cftc.gov/MarketReports/IndexInvestmentData/index.htm | Yes, no login | "The final report is for data collected as of October 30, 2015" | Month-end index notionals and futures-equivalent contracts. Monthly from July 2010; quarterly before that. Discontinued after October 2015. |
| Same page via Wayback (full date list) | https://web.archive.org/web/2016/https://www.cftc.gov/MarketReports/IndexInvestmentData/index.htm | Yes | Same CFTC page | Lists 75 report dates, December 2007–30 October 2015, each with PDF and Excel. |
| IID report PDFs | `https://www.cftc.gov/sites/default/files/idc/groups/public/@marketreports/documents/file/indexinvestmentMMYY.pdf` | Yes, no login | "Government information at the CFTC website is in the public domain." (https://www.cftc.gov/WebPolicy/index.htm) | One-page tables: notional long/short/net in billion USD, and futures-equivalent long/short/net in thousands of contracts, for markets above $0.5bn net notional. |
| IID explanatory notes | https://www.cftc.gov/MarketReports/IndexInvestmentData/ExplanatoryNotes/index.htm | Yes | "includes index investment for all futures and OTC markets" | Special-call snapshot of swap dealers and index funds, including OTC and, for WTI, ICE Futures Europe. Net is the better market measure. Not exchange open interest. |
| Discontinuation release 7282-15 | https://www.cftc.gov/PressRoom/PressReleases/7282-15 | Yes | "discontinued the collection and release of the monthly Index Investment Data" | Final release 25 November 2015, for October 2015. |
| Disaggregated COT notes | https://www.cftc.gov/sites/default/files/idc/groups/public/@commitmentsoftraders/documents/file/disaggregatedcotexplanatorynot.pdf | Yes | "A swap dealer is an entity that deals primarily in swaps" | Four trader classes from 4 September 2009. Pre-2009 history is backcast: "recent classifications had to be used to classify the historical positions". |
| COT explanatory notes (PRE) | https://www.cftc.gov/MarketReports/CommitmentsofTraders/ExplanatoryNotes/index.htm | Yes | "The COT Public Reporting Environment (PRE) provides an application programming interface" | Official free API over COT columns, no key used. |
| Disaggregated futures-only API | https://publicreporting.cftc.gov/resource/72hh-3qpy.csv | Yes, no key | No separate licence page on the host. CFTC web-policy quote above. | Weekly Tuesday positions. Gold `088691`, copper `085692` (`COPPER- #1`), WTI `067651` (`WTI-PHYSICAL`). Columns `swap_positions_long_all`, `swap__positions_short_all`. |
| Historical compressed COT index | https://www.cftc.gov/MarketReports/CommitmentsofTraders/HistoricalCompressed/index.htm | Yes | Same CFTC web policy | Bulk year files for disaggregated futures-only from 2006–09 onward. Not downloaded. |

Every 2013–15 PDF requested returned the table. Excel siblings were listed, not opened.

### RESULTS

Pass rule, fixed before any correlation: a series passes only if, on changes whose both report dates fall in 31 January 2013–30 October 2015, Pearson r of Δ(IID net) with Δ(swap long) or Δ(swap net) is above 0.50, or with Δ(swap short) is below −0.50. Minimum 24 changes. This window has 33.

Alignment, also fixed before the correlations: Disaggregated COT futures-only, latest Tuesday on or before the IID date. Swap net = long − short. Spreads stay out of both legs. IID figures below are the published thousands of contracts; correlations use those figures (scaling does not change r). COT figures are contracts.

| Finding | Value | Grade | Window / denominator | Source URL | Quote or row |
| --- | --- | --- | --- | --- | --- |
| Gold, ΔIID net vs Δswap long | r = −0.03 | MEASURED | 33 monthly changes, Feb 2013–Oct 2015; contracts | IID `indexinvestment0113.pdf`–`1015.pdf`; COT `72hh-3qpy` code `088691` | Fails >0.50 |
| Gold, ΔIID net vs Δswap short | r = −0.14 | MEASURED | same | same | Fails <−0.50 |
| Gold, ΔIID net vs Δswap net | r = +0.10 | MEASURED | same | same | Fails >0.50 |
| Copper, ΔIID net vs Δswap long | r = +0.03 | MEASURED | same; code `085692` | same pattern | Fails >0.50 |
| Copper, ΔIID net vs Δswap short | r = +0.09 | MEASURED | same | same | Fails <−0.50 |
| Copper, ΔIID net vs Δswap net | r = −0.01 | MEASURED | same | same | Fails >0.50 |
| WTI, ΔIID net vs Δswap long | r = +0.42 | MEASURED | same; code `067651` | same pattern | Closest, still fails >0.50 |
| WTI, ΔIID net vs Δswap short | r = −0.24 | MEASURED | same | same | Fails <−0.50 |
| WTI, ΔIID net vs Δswap net | r = +0.38 | MEASURED | same | same | Fails >0.50 |
| Gold level, 28 Jun 2013 / COT 25 Jun 2013 | IID net 114,000; swap long 44,960; short 60,902; net −15,942 | MEASURED | one date; contracts | `indexinvestment0613.pdf`; COT row 2013-06-25 | Matches the seeded triple |
| Gold level, 29 Aug 2014 / COT 26 Aug 2014 | IID net 136,000; swap long 62,318; short 143,707; net −81,389 | MEASURED | one date; contracts | `indexinvestment0814.pdf`; COT row 2014-08-26 | Seeded triple |
| Gold level, 30 Oct 2015 / COT 27 Oct 2015 | IID net 119,000; swap long 56,525; short 119,427; net −62,902 | MEASURED | one date; contracts | `indexinvestment1015.pdf`; COT row 2015-10-27 | Page row "Gold … 149 (31) 119" |
| June 2010 anchor, not in the correlation | Gold net 100,000; copper 65,000; WTI 462,000 | MEASURED | 30 Jun 2010; thousands of contracts ×1,000 | `indexinvestment0610.pdf` | Clean table |
| Commodity pass | Gold fail, copper fail, WTI fail | MEASURED | 2013–15 changes | rows above | No error band is opened |

These are co-movements of position changes. They are not a claim that either position caused a price.

Levels used, so the correlations can be re-derived. IID net is thousands of contracts. COT long and short are contracts. Dates are IID as-of, then the matched Tuesday.

| IID date | COT Tue | Gold IID | Gold L | Gold S | Copper IID | Copper L | Copper S | WTI IID | WTI L | WTI S |
| --- | --- | --- | --- | --- | --- | --- | --- | --- | --- | --- |
| 2013-01-31 | 01-29 | 124 | 55064 | 90878 | 89 | 53997 | 11181 | 349 | 125014 | 395643 |
| 2013-02-28 | 02-26 | 119 | 53742 | 82223 | 88 | 55739 | 12414 | 346 | 130567 | 404519 |
| 2013-03-28 | 03-26 | 119 | 36400 | 99887 | 87 | 59816 | 6487 | 349 | 123761 | 379807 |
| 2013-04-30 | 04-30 | 117 | 43088 | 95699 | 89 | 61025 | 6105 | 360 | 123179 | 355578 |
| 2013-05-31 | 05-28 | 117 | 45571 | 67221 | 89 | 57766 | 6104 | 358 | 108801 | 395363 |
| 2013-06-28 | 06-25 | 114 | 44960 | 60902 | 85 | 61140 | 6979 | 348 | 116253 | 418565 |
| 2013-07-31 | 07-30 | 118 | 45472 | 66832 | 90 | 57775 | 6858 | 343 | 95991 | 517230 |
| 2013-08-30 | 08-27 | 118 | 48785 | 115893 | 90 | 57231 | 10951 | 351 | 124005 | 534744 |
| 2013-09-30 | 09-24 | 120 | 55458 | 114094 | 92 | 56974 | 10890 | 354 | 125116 | 501113 |
| 2013-10-31 | 10-29 | 117 | 47817 | 128344 | 92 | 52827 | 10011 | 352 | 140467 | 464159 |
| 2013-11-29 | 11-26 | 117 | 63173 | 97319 | 86 | 55072 | 7912 | 346 | 156031 | 479942 |
| 2013-12-31 | 12-31 | 107 | 56130 | 94708 | 84 | 42166 | 11948 | 335 | 141587 | 500835 |
| 2014-01-31 | 01-28 | 119 | 51561 | 104134 | 81 | 44083 | 10248 | 302 | 154156 | 479983 |
| 2014-02-28 | 02-25 | 117 | 48341 | 128194 | 77 | 46142 | 7792 | 288 | 124884 | 513004 |
| 2014-03-31 | 03-25 | 117 | 44944 | 144546 | 78 | 50952 | 4350 | 288 | 130611 | 491116 |
| 2014-04-30 | 04-29 | 120 | 59711 | 140198 | 81 | 51086 | 6351 | 294 | 128458 | 475447 |
| 2014-05-30 | 05-27 | 126 | 65353 | 129094 | 80 | 50711 | 6141 | 290 | 123369 | 480899 |
| 2014-06-30 | 06-24 | 133 | 57677 | 151141 | 82 | 55406 | 6382 | 296 | 104340 | 500151 |
| 2014-07-31 | 07-29 | 135 | 58093 | 151446 | 83 | 56503 | 5207 | 304 | 119077 | 470945 |
| 2014-08-29 | 08-26 | 136 | 62318 | 143707 | 80 | 57020 | 3104 | 305 | 119804 | 429130 |
| 2014-09-30 | 09-30 | 136 | 72866 | 101792 | 82 | 57371 | 5053 | 307 | 118432 | 388702 |
| 2014-10-31 | 10-28 | 131 | 64780 | 113829 | 80 | 56160 | 3248 | 307 | 140097 | 363072 |
| 2014-11-28 | 11-25 | 129 | 75262 | 106985 | 79 | 55301 | 3819 | 308 | 110460 | 330584 |
| 2014-12-31 | 12-30 | 127 | 59587 | 118521 | 78 | 58082 | 4169 | 330 | 122086 | 326324 |
| 2015-01-30 | 01-27 | 114 | 49720 | 159364 | 89 | 60474 | 2880 | 418 | 142675 | 304868 |
| 2015-02-27 | 02-24 | 116 | 67813 | 132099 | 86 | 62859 | 3286 | 425 | 183707 | 338204 |
| 2015-03-31 | 03-31 | 121 | 70154 | 100941 | 90 | 63712 | 3076 | 469 | 220302 | 319910 |
| 2015-04-30 | 04-28 | 124 | 57350 | 110507 | 91 | 64953 | 2181 | 457 | 193839 | 343487 |
| 2015-05-29 | 05-26 | 122 | 66036 | 101323 | 91 | 63533 | 5920 | 455 | 196383 | 368646 |
| 2015-06-30 | 06-30 | 120 | 77261 | 86957 | 91 | 49710 | 4101 | 447 | 186458 | 353313 |
| 2015-07-31 | 07-28 | 115 | 83026 | 61828 | 88 | 46946 | 2195 | 456 | 209902 | 327978 |
| 2015-08-31 | 08-25 | 104 | 82325 | 79068 | 84 | 46109 | 2269 | 480 | 218135 | 299743 |
| 2015-09-30 | 09-29 | 116 | 61785 | 72838 | 84 | 44236 | 2677 | 472 | 212026 | 283332 |
| 2015-10-30 | 10-27 | 119 | 56525 | 119427 | 82 | 44916 | 3199 | 479 | 227077 | 272697 |

Endpoint checks that the change sums match the level gaps: gold IID 119−124 = −5; gold swap long 56,525−55,064 = +1,461; copper IID 82−89 = −7; WTI IID 479−349 = +130; WTI swap long 227,077−125,014 = +102,063; WTI swap short 272,697−395,643 = −122,946. Each of those matched the sum of the 33 changes.

Gold, copper, and WTI were above the $0.5bn line in every one of these 34 reports, so none dropped out of the table. July 2014 WTI is the amended posted file (long 444 thousand, net 304 thousand), as the index page describes.

### PRE-REGISTRATION

Dated 14 October 2026, written before any correlation was calculated.

A swap-dealer series is an index-investment proxy for gold, copper, or WTI only if, on the 33 month-to-month changes with both dates inside 31 January 2013–30 October 2015, the Pearson correlation of changes in contracts satisfies one of: r(Δ IID net, Δ swap long) > 0.50, r(Δ IID net, Δ swap net) > 0.50, or r(Δ IID net, Δ swap short) < −0.50. At least 24 changes are required. Levels do not decide the pass. In-sample correlations, if computed, do not decide it. A pass on crude or copper would still be a 2010–15 relationship and would stay HYPOTHESIS if applied to 2026. This sample fails that statement for every commodity and every series.

### WHAT IT CHANGES

The state says there is no commodity index-investment data because the CFTC stopped it in October 2015. The archive through 30 October 2015 is still free and public. The gap remains for every date after that.

C-141's roughly 117 t deepening of the gold swap-dealer net short cannot be read as index or passive supply. The gold index-investment row stays not measurable. That is now a tested negative on the 2013–15 proxy, on top of the missing post-2015 series. The 117 t figure itself was not re-measured here.

The item's other branch does not open. Crude and copper also fail, so no proxy and no error band is adopted for them. WTI swap-long changes are the nearest co-movement, at 0.42, which is under the bar.

Nothing here attributes a price move. The charter still stands: a position change is not a cause of a price.

### BUILD SPEC

Script: `scripts/iid_swap_proxy.py`. Expected runtime: 2–5 minutes for 75 one-page PDFs plus three SODA pulls.

Inputs:

- IID PDFs, all 75: `https://www.cftc.gov/sites/default/files/idc/groups/public/@marketreports/documents/file/indexinvestment{MMYY}.pdf` for MMYY from `1207` through `1015` on the date list above (11 quarterly through `0610`, then monthly `0710`–`1015`). Multiply the published "thousands" by 1,000.
- COT futures-only: `https://publicreporting.cftc.gov/resource/72hh-3qpy.csv` with `$select=report_date_as_yyyy_mm_dd,swap_positions_long_all,swap__positions_short_all` and `cftc_contract_market_code` in `088691`, `085692`, `067651`. The short column has a double underscore. No app token.

Outputs:

- `data/iid_panel.csv`: `asof_date, commodity, iid_long, iid_short, iid_net, source_file`
- `data/cot_swap_matched.csv`: `asof_date, cot_tuesday, commodity, cftc_code, swap_long, swap_short, swap_net`
- `data/iid_cot_changes.csv`: `end_date, commodity, d_iid_net, d_swap_long, d_swap_short, d_swap_net`
- `data/iid_cot_corr.csv`: `commodity, series, window, n_changes, pearson_r, pass`

Assert:

- 75 files parsed; gold, copper, and WTI present in each 2013–15 month.
- 30 Oct 2015 gold IID net = 119,000. 30 Jun 2010 gold IID net = 100,000.
- COT 2015-10-27 gold long = 56,525, short = 119,427, net = −62,902.
- COT 2014-08-26 gold long = 62,318, net = −81,389.
- COT 2013-06-25 gold long = 44,960, net = −15,942.
- Matched Tuesday is the latest Tuesday on or before the IID date.
- OOS n = 33. Reproduced r within 0.02 of gold −0.03 / −0.14 / +0.10, copper +0.03 / +0.09 / −0.01, WTI +0.42 / −0.24 / +0.38 (long, short, net).
- July 2014 WTI is the amended posted file.
- Do not regress prices. Hamilton–Wu stays dropped. In-sample (changes inside July 2010–December 2012) is reported and does not flip the pass.

### UNCERTAIN

The nine correlations were computed by hand from the table above. Change-sums match the endpoint gaps. A rebuild should still confirm each r within 0.02. WTI long at 0.42 is the only figure close enough to the bar that an arithmetic error could matter; the margin checksums and a second arrangement of the same sums both give 0.42.

Futures-and-options combined was not retrieved (a guessed dataset id returned HTTP 400). Futures-only is the series that matches the seeded gold figures exactly. IID equivalents include delta-adjusted options, so combined COT is the sensitivity worth running.

IID prints are rounded to 1,000 contracts. Gold's monthly changes have a standard deviation of about 5.5 thousand contracts, so gold's near-zero correlations are coarse. They are not close to 0.50. WTI's large 2014–15 changes make that rounding unimportant.

`publicreporting.cftc.gov` had no separate terms paragraph on the pages fetched. Public-domain status is taken from the CFTC web policy for CFTC website information.

The December 2007 PDF extracted with merged columns. It was not used in the correlations.

### NOT DONE

Thirty-nine of the 75 IID files were not opened. The pass window, January 2013–October 2015, was opened in full (34 files), plus 30 June 2010 and a degraded read of December 2007.

In-sample correlations for July 2010–December 2012 were not computed. Quarterly 2008–June 2010 changes were not computed. Disaggregated classifications before 4 September 2009 are backcast, so a 2008 swap-dealer correlation would not be a contemporaneous classification.

No futures-and-options combined test. No price regression. The Hamilton–Wu re-run was dropped, as the item requires.

---

## Item 9: Gold against 10y real yields: standard errors and a structural-break date (Erb-Harvey through Oct 2026)

*Status SUCCESS; 1024 s; breaches 0, blocked 0, unexpected tools 0, stage changes 0.*

*Cited without a fetch in this call, not relied on:* `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{YYYY}/all?type=daily_treasury_real_yield_curve&field_tdr_date_value={YYYY}&page&_format=csv`; `https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx`


**Supervisor check.** The 2026 monthly 10y real yields re-derived from the Treasury real-yield CSV match every day count and sum given (Jan 20 days / 38.14 … Sep 21 / 55.40). The World Bank October 2026 Pink Sheet gold row was re-fetched: quarterly 3,459, 4,152, 4,876, 4,512 and 4,268, then Jul 4,073, Aug 4,411, Sep 4,319. All match. OLS re-run on the nine 2026 months: slope −20.2% per percentage point, SE 5.5, R² 0.66. This matches. The 2025 quarters and the dollar-index regression are relayed.


### SOURCES

| Source | URL fetched | Free? | Terms quote | What it holds |
| --- | --- | --- | --- | --- |
| Treasury par real yield curve, 2026 daily | https://home.treasury.gov/resource-center/data-chart-center/interest-rates/TextView?type=daily_treasury_real_yield_curve&field_tdr_date_value=2026 | Yes, no login | No licence line on this page | Daily R-CMT, percent. 10 YR on 13 Oct 2026 is 2.88; on 9 Oct 2026 is 2.91; on 30 Sep 2026 is 2.93 |
| Treasury par real yield curve, 2025 daily CSV | https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2025/all?type=daily_treasury_real_yield_curve&field_tdr_date_value=2025&page&_format=csv | Yes, no login | No licence line on the rate page | Full-year daily 5/7/10/20/30-year real yields, percent. 31 Dec 2025 10 YR is 1.93 |
| Treasury rate archives | https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rate-archives | Yes, no login | No licence line on this page | Lists `par-real-yield-curve-rates-2003-2023.csv` and the 2003–2009, 2010–2019, and 2020–2023 pieces. Bulk files not downloaded |
| USA.gov government works | https://www.usa.gov/government-copyright | Yes, no login | "Not everything that appears on a federal government website is a government work." | Agency-level check still required. This is not a Treasury public-domain grant |
| Pink Sheet, 2 Oct 2026 | https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Pink-Sheet-October-2026.pdf | Yes, no login | Site remainder terms, below | Gold, $/toz, "spot average of daily rates." Jul 4,073; Aug 4,411; Sep 4,319. Annual 2023 1,943; 2024 2,388; 2025 3,442. Quarters 2025Q3 3,459; 2025Q4 4,152; 2026Q1 4,876; 2026Q2 4,512; 2026Q3 4,268 |
| Pink Sheet, 2 Jul 2026 | https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Pink-Sheet-July-2026.pdf | Yes, no login | Same remainder terms | Apr 4,721; May 4,587; Jun 4,228; 2026Q2 4,512 |
| Pink Sheet, 2 Apr 2026 | https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Pink-Sheet-April-2026.pdf | Yes, no login | Same remainder terms | Jan 4,753; Feb 5,020; Mar 4,856; 2026Q1 4,876. Also 2025Q1 2,863 and 2025Q2 3,293 |
| Pink Sheet monthly history workbook | https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx | URL is public | Not read | HTTP 500 on two fetches. Body not read |
| World Bank site terms | https://www.worldbank.org/en/about/legal/terms-of-use-for-datasets | Yes, no login | "you may not make any derivative work or commercial use" | Remainder materials: non-commercial use; derivative or commercial use needs prior written consent. Data-catalog CC BY was not found attached to the Pink Sheet |
| Fed H.10 nominal broad dollar, monthly | https://www.federalreserve.gov/releases/h10/summary/jrxwtfb_nm.htm | Yes, no login | "information on Board's website is in the public domain" | Index, Jan 2006 = 100.0000. Release 1 Oct 2026. Dec 2021 115.8045; Dec 2023 119.8331; Dec 2025 120.1883; Sep 2026 119.2152. Full Jan 2006–Sep 2026 table |
| Fed disclaimer | https://www.federalreserve.gov/disclaimer.htm | Yes, no login | "may be copied and distributed without permission" | Cite the Board. A DDP CSV was not the file read |
| In-house commodities return | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/_research/2026-10-12-E021-commodities-inhouse-return.md | Yes, public repo | Repo file, no separate licence line read | Quoted weekly slopes −11.9, −3.4, −17.7 per pp, from a sponsor-derived price. Scratch files not kept |
| IMF-based gold ledger | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/data/gold/ledger_monthly.csv | Yes, public repo | IMF terms page not re-fetched | Tonnes and XDR value effects, 2019-01 through 2026-09. No gold price |

Treasury’s own footnote on the 2026 rate page: "Treasury began using a monotone convex spline (MC) method" on 12/6/2021, and "the TIPS yield curve began using the most recently auctioned TIPS" on 12/01/2008. Rates are "Real Constant Maturity Treasury" rates (R-CMT), in percent.

### RESULTS

Observations used, so the slopes can be re-derived. Gold is the Pink Sheet average of daily rates, $/toz. The real yield is the business-day mean of the Treasury 10 YR R-CMT, percent. The dollar is the equal-weight average of the three Fed monthly index levels (Jan 2006 = 100).

2026 months (yield sum / days): Jan gold 4,753, yield 38.14/20 = 1.907; Feb 5,020, 34.67/19 = 1.825; Mar 4,856, 42.00/22 = 1.909; Apr 4,721, 42.61/22 = 1.937; May 4,587, 40.78/20 = 2.039; Jun 4,228, 45.76/21 = 2.179; Jul 4,073, 51.77/22 = 2.353; Aug 4,411, 50.34/21 = 2.397; Sep 4,319, 55.40/21 = 2.638. Jan and Sep sums were re-added from the 2026 page (38.14 and 55.40).

2025 daily sums behind the quarters: Q1 46.80+38.51+40.87 = 126.18 over 61 days (2.069); Q2 42.80+44.32+41.73 = 128.85 over 62 days (2.078); Q3 44.18+39.54+36.73 = 120.45 over 64 days (1.882); Q4 38.65+32.90+41.78 = 113.33 over 62 days (1.828). Gold: 2,863; 3,293; 3,459; 4,152. Dollar: 127.6519; 122.3588; 120.2392; 120.7893.

2026 quarters: yield 114.81/61 = 1.882, 129.15/63 = 2.050, 157.51/64 = 2.461. Gold 4,876; 4,512; 4,268. Dollar 119.0186; 119.2997; 119.5545. Published quarter checks: (4753+5020+4856)/3 = 4,876.33; (4721+4587+4228)/3 = 4,512; (4073+4411+4319)/3 = 4,267.67.

Specification assumed for every slope below: log gold on an intercept and the real yield in percentage points. The slope times 100 is the percent gold move per percentage point. Standard errors are classical OLS. They are not Newey–West.

| Finding | Value | Grade | Window / denominator | Source URL | Quote or row reference |
| --- | --- | --- | --- | --- | --- |
| 10y real yield, 13 Oct 2026 | 2.88% | MEASURED | That business day; R-CMT percent | Treasury 2026 TextView URL above | Row 10/13/2026, column 10 YR |
| 10y real yield, 9 Oct 2026 | 2.91% | MEASURED | That business day; R-CMT percent | Same | Row 10/09/2026, column 10 YR |
| Pink Sheet gold, Sep 2026 | $4,319/toz | MEASURED | Sep 2026 average of daily rates | October 2026 Pink Sheet PDF | Gold row, September |
| Pink Sheet gold, Jul 2026 | $4,073/toz | MEASURED | Jul 2026 average of daily rates | Same | Gold row, July |
| Jan–Sep 2026 levels slope | −20.2% per pp; classical 95% interval −33% to −7%; R² 0.66; n=9 | MEASURED point; interval BOUNDED | 9 monthly averages; % gold per pp of the 10y real yield | Gold PDFs + Treasury 2026 page | Hand OLS on the nine rows above. Residual signs come in blocks, so this interval is the wrong precision statement |
| Feb–Sep 2026 changes slope | −31.9% per pp; classical 95% −75% to +11%; R² 0.36; n=8 | MEASURED point; "covers zero" is BOUNDED | 8 monthly changes; same denominator | Same | Interval covers zero and positive values. Wider HAC errors would still cover zero |
| 2025Q1–2026Q3 levels slope | −2.1% per pp; classical SE 40 pp; 95% about −105% to +101%; R² 0.0005; n=7 | MEASURED point; "cannot be estimated" is BOUNDED | 7 quarters, 21 months; same denominator | 2025 CSV + Pink Sheet quarter prints | Gold rose from $2,863 to $4,268 while the real yield went from 2.07% to 2.46% |
| Same quarters, real yield and log broad dollar | Real-yield partial −0.2% per pp, classical 95% about −63% to +62%. Dollar partial −6.8, classical 95% about −12.2 to −1.3. R² 0.75; n=7 | BOUNDED | 7 quarters; % gold per pp, and % gold per 1% dollar index | Same + H.10 page | In-sample co-movement of two trending series. This is not a cause, and it is not a forecast from a fit that ends in Dec 2021 |
| Quoted weekly slopes | −11.9 (2018–21, R² 0.32); −3.4 (2024–Oct 2026, R² 0.01); −17.7 (Mar–Oct 2026, R² 0.18, n=32) | HYPOTHESIS | Weekly; % per pp, as quoted | In-house return URL above | Sponsor-derived price. Not recomputed |
| Official gold stock change | 36,516.811 t in Aug 2026 minus 36,180.150 t in Dec 2025 = 336.7 t | MEASURED stock change | Tonnes, Dec 2025–Aug 2026, carry-forward reporters | Ledger URL above | Not entered in the price regression |

### WHAT IT CHANGES

The commodities paragraph in `state.md` stands: the source of the gold rise is not attributed, and official tonnes stay a stock fact rather than a cause.

The E-021 line that real-yield sensitivity collapsed and then came back in 2026 stays a hypothesis. On public data, a 2026-only monthly levels slope is about −20% per percentage point, near the quoted weekly −17.7, and the Feb–Sep changes interval runs from about −75% to +11% per percentage point. Adding the four quarters of 2025 takes the levels slope to about −2% per percentage point with an R² of about 0.0005. The page can say a real-yield link cannot be estimated on this roughly 21-month quarterly window. A dated 2022–23 regime shift was not estimated, so that wording stays off the page. The residual a real-yield-and-dollar story would leave after a fit through Dec 2021 was not computed, so this test does not bound how much of the later rise that story leaves unexplained.

### BUILD SPEC

`bin/gold_real_yield_break.py`. Runtime under 2 minutes once the workbook downloads; the regression, sup-F, and 1,000 bootstrap draws on about 250 months are a few seconds. If the xlsx still returns HTTP 500, the 2006–2021 half cannot run.

Inputs:

- Pink Sheet monthly workbook, gold row, $/toz, spot average of daily rates. Candidate URL is the xlsx above (HTTP 500 here). Resolve the live link from https://www.worldbank.org/en/research/commodity-markets. Vintage date stored on every output row.
- Treasury 10 YR, percent. Year CSVs `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{YYYY}/all?type=daily_treasury_real_yield_curve&field_tdr_date_value={YYYY}&page&_format=csv` for 2024–2026, plus the archive file `par-real-yield-curve-rates-2003-2023.csv` listed on the archives page. Keep the business-day mean and the month-end.
- Broad dollar: `https://www.federalreserve.gov/releases/h10/summary/jrxwtfb_nm.htm`, Jan 2006 = 100. The fit starts Jan 2006 because this index starts there.
- Exploratory file only, separate from the price slope: `https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/data/gold/ledger_monthly.csv`, columns `official_change_cf_t` and `official_reporters_cf_t`.
- No GLD, IAU, LBMA, WGC, or LME column.

Outputs:

- `data/gold/real_yield_monthly.csv`: `month, gold_usd_per_toz, tips10_avg_pct, tips10_eom_pct, broad_dollar_2006jan100, ln_gold, ln_dollar, dln_gold, d_tips10, dln_dollar`
- `data/gold/real_yield_results.csv`: `window, spec, n, beta_tips, se_classical, se_hac, hac_lags, r2, beta_dollar, se_dollar_hac`
- `data/gold/real_yield_break.csv`: `trim, sup_stat, break_month, ci_low, ci_high`
- `data/gold/real_yield_rolling36.csv`: `end_month, beta_tips, boot_lo, boot_hi`
- `data/gold/real_yield_oos.csv`: `month, ln_gold, fitted, residual_log`, label `unexplained_by_real_yield_and_dollar`

Asserts: 13 Oct 2026 10 YR = 2.88; 30 Sep 2026 = 2.93; Sep 2026 mean = 55.40/21; gold Jan–Sep 2026 = 4753, 5020, 4856, 4721, 4587, 4228, 4073, 4411, 4319; quarter prints match those means within rounding; 2025 quarters 2863, 3293, 3459, 4152; dollar Jan 2006 = 100, Dec 2021 = 115.8045, Sep 2026 = 119.2152. Reproduced hand checks within 0.01: 2026 levels beta −0.202, 2026 changes beta −0.319, 2025Q1–2026Q3 levels beta −0.021. Newey–West lag `floor(4*(n/100)^(2/9))`, lag printed. Quandt–Andrews 15% trim; `ci_low`/`ci_high` are the dates not rejected at 5%, not a single date. Bootstrap 1,000, seed 20261014, percentile 2.5/97.5, 36-month window. Estimation sample ends 2021-12; forecast 2022-01 through the last Pink Sheet month (Sep 2026 on the 2 Oct vintage). Flag the 2021-12-06 spline break and the 2008-12-01 TIPS knot break. The coefficient and the residual are associations.

### UNCERTAIN

The −11.9 / −3.4 / −17.7 figures were read as levels semi-elasticities because the note reports them as percent per percentage point and gives an R² of 0.32 for 2018–21. The equation itself was not in the public note. The unkept scratch script would settle the specification.

2025 daily yield totals are hand sums from the 2025 CSV. A one-line error would move the quarterly slope slightly. It would not turn an R² of about 0.0005 into a tight slope. The script’s re-sum is the check.

The dollar coefficient’s second decimal is hand arithmetic. The classical interval on seven quarterly levels is a weak precision statement. HAC on a monthly sample from 2006 would settle whether the dollar partial stays below zero.

Pink Sheet gold is described as a spot average of daily rates. Whether that average is a vendor price, and whether any catalog CC BY grant covers it, was not on the PDF. The site remainder terms were read. A derivative-works consent question remains.

The end-2023 real yield of 1.72% quoted in the in-house note was not re-fetched. The 2023 archive file is the check.

### NOT DONE

HAC standard errors on the three weekly windows. The local price file is a sponsor-derived series and is outside public outputs.

Quandt–Andrews, the 36-month bootstrap bands, the fit through Dec 2021, and the 2022–Sep 2026 forecast. The monthly history workbook returned HTTP 500, and there is no shell in this run, so those statistics were not computed even on the short sample.

October 2026 gold. The 2 Oct 2026 Pink Sheet ends in September. The January 2026 Pink Sheet PDF returned HTTP 404, so Oct–Dec 2025 monthly gold was not assembled; the quarters were.

A Fed DDP CSV. The series used is the H.10 monthly HTML. A Treasury-specific public-domain sentence was not on the rate pages. The IMF source terms were not re-fetched; the public ledger file was.

---

## Item 10: US external balance sheet identity: BEA IIP flows, prices and exchange rates, 2019-2026Q2

*Status SUCCESS; 615 s; breaches 0, blocked 0, unexpected tools 0, stage changes 0.*

*Cited without a fetch in this call, not relied on:* `https://apps.bea.gov/api/data`


**Supervisor check.** BEA's Q2 2026 IIP release PDF was re-fetched. It says the liabilities increase was "driven by price changes of $3.95 trillion and financial transactions of $978.9 billion", and that the net position was −$22.42 trillion. Both match. The 81% is 3.95 / 4.87. The FRED stock levels are relayed: FRED refuses the supervisor's scripts.


### SOURCES

| Source | URL fetched | Free? | Terms quote | What it holds |
| --- | --- | --- | --- | --- |
| BEA ITA/IIP news release, 24 Sep 2026 (BEA 26–41) | https://www.bea.gov/sites/default/files/2026-09/ita-iip226.pdf | Yes, no login | "in the public domain and may be used or reproduced without specific permission" (https://www.bea.gov/help/faq/147) | Q2 2026 current account, financial-account transactions, and IIP levels. Price and transactions for the asset and liability changes are in the text. Exchange-rate and other-change lines are not. |
| Same release, HTML | https://www.bea.gov/news/2026/us-international-transactions-and-investment-position-2nd-quarter-2026 | Yes, no login | Same BEA public-domain sentence | Same figures as the PDF. Points to interactive Tables 1.1, 1.2, and 1.3 for history. |
| "Historical Comparisons" PDF named in the item | https://www.bea.gov/sites/default/files/2026-09/ita-iip226-hist.pdf | Yes, no login | Same BEA public-domain sentence | One page of record comparisons for Q2 2026 international transactions, seasonally adjusted, billions of dollars. No IIP price, exchange-rate, or other-change columns, and no quarterly ledger from 2019. |
| BEA IIP landing page | https://www.bea.gov/data/intl-trade-investment/international-investment-position | Yes, no login | Same BEA public-domain sentence | End-Q2 2026 net −$22.42tn, assets $46.97tn, liabilities $69.39tn. Links the release, the historical-comparisons PDF, and interactive tables. |
| BEA interactive tables | https://apps.bea.gov/iTable/?reqid=62&step=1 and https://apps.bea.gov/iTable/tb_download.html?pid=144 | Page is public; the table did not render | Same BEA public-domain sentence | Shell only: "Please select a table to download." No Table 1.3 rows. |
| BEA API user guide (20 Apr 2026) and signup | https://apps.bea.gov/api/_pdf/bea_web_service_api_user_guide.pdf and https://apps.bea.gov/API/signup/index.html | Free after registration; not used | "users must obtain a unique 36-character UserID by registering" | Dataset `IIP`. Parameters `TypeOfInvestment`, `Component`, `Frequency` (`A`, `QNSA`), `Year`. Documented components include `Pos`, `ChgPosTrans`, `ChgPosPrice`. |
| BEA definitions, 27 Mar 2024 release | https://www.bea.gov/news/2024/us-international-investment-position-4th-quarter-and-year-2023 | Yes, no login | Same BEA public-domain sentence | Identity: other changes are price, exchange-rate, and volume-and-valuation n.i.e. Quarterly price and exchange-rate detail was announced to start in 2023Q1. |
| BEA concepts landing page | https://www.bea.gov/resources/methodologies/us-international-economic-accounts-concepts-methods | Yes, no login | Same BEA public-domain sentence | Current handbook posted September 2026. The PDF body was not read. |
| FRED Table 1.1 positions (BEA source) | https://fred.stlouisfed.org/series/IIPUSASSQ and https://fred.stlouisfed.org/series/IIPUSLIAQ | Yes, no login | "Don't do any data mining, scraping or extraction of FRED data." | End-of-period stocks, millions of dollars, not seasonally adjusted. Updated 24 Sep 2026. Latest five quarters only on the series page. Full-history data pages timed out. |
| TIC SLT Table 1 (securities counterpart) | https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/slt_table1.html | Yes, no login | No reuse sentence on the pages fetched | Foreign holdings of U.S. long-term securities by country: holdings, net U.S. sales, valuation change, millions of dollars. Valuation is `n.a.` through 2023-01 in the rows returned. |
| TIC "Using TIC" | https://home.treasury.gov/data/treasury-international-capital-tic-system/contact-tic-using-tic | Yes, no login | No reuse sentence on the page fetched | Says the tables are txt, CSV, and HTML for download into spreadsheets. |

### RESULTS

The Q2 2026 liability rise is 81% price: $3.95 trillion of a $4.87 trillion increase. Transactions were $978.9 billion, about one-fifth of that increase. The wording "money flowing in" fits the transactions line. It does not fit the stock change.

Numbers used, all for 2026Q2 unless noted. Positions are end of quarter.

FRED, millions of dollars, not seasonally adjusted, updated 24 Sep 2026:

- Assets: Q1 43,251,828; Q2 46,968,523. Change = 3,716,695 million ($3,716.695 billion), which rounds to BEA's $3.72 trillion.
- Liabilities: Q1 64,520,916; Q2 69,388,842. Change = 4,867,926 million ($4,867.926 billion), which rounds to BEA's $4.87 trillion.
- Net = assets − liabilities: Q1 −21,269,088 million (−$21.269 trillion, BEA −$21.27 trillion); Q2 −22,420,319 million (−$22.420 trillion, BEA −$22.42 trillion).
- Net change = −1,151,231 million. Asset change minus liability change equals the same −1,151,231 million.

BEA release text, paired with the historical-comparisons PDF (billions of dollars; that PDF's header says seasonally adjusted):

- Asset transactions 663.301; liability transactions 978.860; financial-derivative transactions −54.139; net financial-account transactions −369.699.
- Check: 663.301 − 978.860 − 54.139 = −369.698. The $0.001 billion gap is rounding.
- Published price: assets $3.03 trillion; liabilities $3.95 trillion.

Liability price share, using BEA's published rounded figures: 3.95 / 4.87 = 0.8111, which is 81% to the nearest percent. Using the unrounded stock change and price taken as $3,950 billion: 3,950 / 4,867.926 = 0.8115. Transactions are 978.860 / 4,867.926 = 0.2011. Those two shares and the residual below use the same denominator, the Q2 change in liabilities.

Residual on liabilities = 4,867.926 − 3,950 − 978.860 = −60.934 billion. The price figure is published only to $0.01 trillion, so this residual sits in a band of about −$56 billion to −$66 billion. It is the part of the stock change left after published price and published transactions. BEA's own categories for that part are exchange-rate changes and changes in volume and valuation n.i.e. The Q2 release does not split them. On assets the same residual is 3,716.695 − 3,030 − 663.301 = +23.394 billion, about $18 billion to $28 billion once the $3.03 trillion rounding is allowed for.

Asset price share on the same basis is 3,030 / 3,716.695 = 0.815.

| Finding | Value | Grade | Window / denominator | Source URL | Quote or row |
| --- | --- | --- | --- | --- | --- |
| End-Q2 net IIP equals assets minus liabilities | −$22.420 trillion = 46,968,523 − 69,388,842 million | IDENTITY | End-2026Q2; net = assets − liabilities | https://fred.stlouisfed.org/series/IIPUSLIAQ and https://fred.stlouisfed.org/series/IIPUSASSQ | Q2 2026 rows: liabilities 69,388,842; assets 46,968,523. BEA text: "−$22.42 trillion" |
| Opening stock plus published change equals closing stock | Liabilities 64,520,916 + 4,867,926 = 69,388,842 million. Assets 43,251,828 + 3,716,695 = 46,968,523 | IDENTITY | 2026Q1 end to 2026Q2 end; change in that stock | Same FRED series | Q1 and Q2 2026 rows |
| Liability rise is 81% price | 3.95 / 4.87 = 81.1%; unrounded change gives 81.1% | IDENTITY | 2026Q2; denominator = change in U.S. liabilities, $4.87 trillion as published | https://www.bea.gov/sites/default/files/2026-09/ita-iip226.pdf | "driven by price changes of $3.95 trillion and financial transactions of $978.9 billion" |
| Liability transactions are one-fifth of the stock rise | $978.860 billion / $4,867.926 billion = 20.1% | IDENTITY | 2026Q2; same liability-change denominator | https://www.bea.gov/sites/default/files/2026-09/ita-iip226-hist.pdf | Row "Transactions in liabilities" 978.860 |
| Exchange-rate plus other changes on liabilities | −$60.9 billion, band about −$56 to −$66 billion, −1.3% of the liability rise | BOUNDED | 2026Q2; residual of the liability change after published price and transactions | Release PDF plus FRED levels | Not a printed line. Price is published to $0.01 trillion |
| Same residual on assets | +$23.4 billion, band about +$18 to +$28 billion | BOUNDED | 2026Q2; residual of the asset change | Same | Price published as $3.03 trillion |
| Financial-account adds up | 663.301 − 978.860 − 54.139 = −369.698, against −369.699 | IDENTITY | 2026Q2; net financial-account transactions, billions of dollars, seasonally adjusted | https://www.bea.gov/sites/default/files/2026-09/ita-iip226-hist.pdf | Rows for assets, liabilities, derivatives, and net financial transactions |
| Historical PDF parses back to 2019 | It does not. The file is a Q2 2026 record comparison. No price or exchange-rate history | MEASURED | File dated 24 Sep 2026; not a 2019–2026Q2 panel | https://www.bea.gov/sites/default/files/2026-09/ita-iip226-hist.pdf | Title: "Historical Comparisons". Header: "Billions of dollars, seasonally adjusted" |
| Exchange-rate line is a currency revaluation | Definition read; Q2 2026 magnitude not separately published | HYPOTHESIS for the Q2 size; the definition itself is BEA's | Definition page is 27 Mar 2024; Q2 2026 line absent from the release text | https://www.bea.gov/news/2024/us-international-investment-position-4th-quarter-and-year-2023 | "changes in the value of foreign-currency-denominated assets and liabilities" |

The exchange-rate line, where BEA publishes it, is the dollar value of foreign-currency positions after foreign currencies move against the dollar. The Q2 2026 release does not give the currency weights behind that line, so the line is not a hedge measure. This quarter the whole residual that contains it is about −$61 billion on liabilities, next to a $3.95 trillion price change. The test does not size a large dollar-fall effect on the U.S. liability stock.

Positions in the release are not seasonally adjusted. The transaction figures that match $663.3 billion and $978.9 billion sit in a PDF headed seasonally adjusted. The residual above therefore uses an unadjusted stock change and those transaction figures together, which is how the release presents them.

### WHAT IT CHANGES

State.md's FX section says money is still flowing into U.S. securities: about $1,600 billion of foreign private net purchases of long-term securities over August 2025–July 2026, and $1,754.4 billion of foreign net purchases of all long-term U.S. securities. Those are securities flows over about a year. They stay as stated. The new fact is about a different object: the change in the whole liability stock in one quarter.

For 2026Q2, financial transactions raised U.S. liabilities by $979 billion, and the stock rose $4.87 trillion. Price changes are 81% of that stock rise. "Money flowing in" describes the transactions slice. It does not describe the stock change. That is an IDENTITY qualifier on wording. It is not a claim that flows caused prices, or that prices caused the dollar.

The net position at end-2026Q2 is −$22.42 trillion (assets $46.97 trillion, liabilities $69.39 trillion). That stock was not in the state summary.

The test does not fill the gap state.md names for FX: no price-side decomposition of the dollar, and no measured split between hedging and selling. The exchange-rate piece of the balance sheet was not separately published for this quarter, and the residual that contains it is about 1% of the liability rise. Hedging ratios in the state summary are untouched. The item's instruction to drop the TIC reconciliation and the statistical-discrepancy bound stands: those were not used. TIC remains the securities-only counterpart, and the $1.75 trillion / $2.88 trillion / $0.23 trillion split in the item was not re-derived.

### BUILD SPEC

Script: `iip_change_identity.py`. Runtime: a few seconds on a saved workbook; under two minutes if the API path is used, with requests sent one at a time (guide limit 100 requests per minute).

Inputs, in this order:

1. A browser export of IIP Table 1.3, "Change in the U.S. Net International Investment Position," and Table 1.1, saved locally from https://apps.bea.gov/iTable/?reqid=62&step=1. The live page did not return rows to a non-JavaScript fetch. Do not parse `ita-iip226-hist.pdf` as the history.
2. Optional, only with a user-supplied key in the environment, never written into the repo: `GET https://apps.bea.gov/api/data` with `method=GetData`, `DataSetName=IIP`, `Frequency=QNSA`, and `Year=2019,2020,2021,2022,2023,2024,2025,2026`. The guide allows many years only with a single `TypeOfInvestment`, and many investment types only with a single year. Call `GetParameterValues` for `TypeOfInvestment` and `Component` and keep the returned keys. The guide itself shows `Pos`, `ChgPosTrans`, `ChgPosPrice`, `FinAssetsExclFinDeriv`, and `FinLiabsFoa`. Take total assets, total liabilities, and the exchange-rate and volume-and-valuation keys from that list rather than from a hard-coded guess.
3. Level check only, not a file written into the repo: FRED `IIPUSASSQ` and `IIPUSLIAQ`. FRED's terms forbid scraping and storing FRED content in another database. BEA is the source to keep.

Output: `data/iip_identity_q.csv`. Columns: `quarter`, `side` (assets, liabilities, net), `type_of_investment`, `opening_musd`, `transactions_nsa_musd`, `transactions_sa_musd`, `price_musd`, `exchange_rate_musd`, `other_nie_musd`, `closing_musd`, `residual_musd`, `price_share`.

Assert:

- For each NSA row, opening + NSA transactions + price + exchange rate + other n.i.e. = closing, within $1 million or the table's stated rounding.
- Assets − liabilities = net, for positions and for each component published on both sides.
- 2026Q2 pins: liability transactions 978,860 million; asset transactions 663,301 million; liability close 69,388,842; asset close 46,968,523; price share 3.95/4.87 within 0.805 to 0.817.
- Positions cover 2019Q1–2026Q2. Record the first quarter in which price and exchange-rate cells are non-blank. BEA's 27 Mar 2024 notice said the quarterly split starts in 2023Q1; a blank 2019–2022 quarterly valuation is an expected result to record, not a silent fill.
- Do not treat the exchange-rate column as a hedge ratio, and do not use the statistical discrepancy (−124.925 in the historical-comparisons PDF) as a bound.

### UNCERTAIN

- The −$61 billion liability residual mixes exchange-rate changes, volume-and-valuation n.i.e., any derivative position change that is outside the $978.9 billion transactions line, and any gap between seasonally adjusted transactions and not-seasonally-adjusted positions. Table 1.3 is what separates those. It was not read.
- The 27 Mar 2024 definitions say derivative transactions and derivative valuation are published net, not split into assets and liabilities, and that price, exchange-rate, and n.i.e. were then shown annually. The same release announced quarterly detail from 2023Q1. Whether the 2026 Table 1.3 still withholds the gross derivative split, or has backcast quarterly valuation before 2023Q1, was not re-read.
- The September 2026 concepts PDF was not opened, so the current paragraph 22.5 wording was not checked against the 2024 definition.
- FRED copyright tags for `IIPUSASSQ` and `IIPUSLIAQ` were not on the series pages fetched. The series notes name BEA as the source. BEA's own site states the public-domain terms above.
- TIC reuse terms were not on the pages fetched. Respondent-level forms are confidential; that is a different document from the published country table.
- Component codes other than `Pos`, `ChgPosTrans`, and `ChgPosPrice` were not in the API guide text that was read. A third-party page mentioned `ChgPosXRate`; that code stays unverified until `GetParameterValues` returns it.

### NOT DONE

- The separate exchange-rate and other-change lines for 2026Q2, and the quarterly identity from 2019 through 2026Q2. Table 1.3 did not render without JavaScript. The API needs a registered key; none was requested or used. The named historical PDF does not contain those rows.
- 2019 position levels. The FRED series pages showed Q2 2025–Q2 2026 only. The full-history data pages timed out.
- The item's TIC securities split of net $1.75 trillion, valuation $2.88 trillion, residual $0.23 trillion. The item says to drop that reconciliation. The country file rendered from Austria downward, not a grand-total row for a stated window, so those three figures were not recomputed.
- Instrument detail (direct, portfolio, other, reserves) for the Q2 price share. The release text gives only the all-instrument totals.

---

## Item 11: 20 Nov BIS preregistration pack: FX-swap turnover (London, New York) and OTC gold in tonnes

*Status SUCCESS; 863 s; breaches 0, blocked 0, unexpected tools 0, stage changes 0.*

*Cited without a fetch in this call, not relied on:* `https://stats.bis.org/api/v1/data/BIS,WS_OTC_DERIV2,1.0/H.A.D.B.5J.A.5J.A.USD.TO1.A.A.3.C?format=csv`; `https://stats.bis.org/api/v1/data/BIS,WS_OTC_DERIV2,1.0/H.A.H.B.5J.A.5J.A.USD.TO1.A.A.3.C?format=csv`; `https://stats.bis.org/api/v1/data/BIS,WS_OTC_DERIV2,1.0/H.A.I.B.5J.A.5J.A.USD.TO1.A.A.3.C?format=csv`


**Supervisor check.** BIS `WS_OTC_DERIV2` key `H.A.D.B.5J.A.5J.A.USD.TO1.A.A.3.C` was re-fetched. 2023-S1 61,103,464.253; 2024-S1 66,139,364.184; 2025-S1 75,703,774.784; 2025-S2 74,022,849.397 (US$ millions). June-on-June +8.24% and +14.46%. The band of +11% to +18% is $84,031,190m to $89,330,454m. All match. The pre-registration was written into `CALENDAR.tsv` on 14 Oct. The BIS release calendar was checked the same day and gives the 2026-S1 release as "no later than" 16 Nov 2026, not 20 Nov, so the row was re-dated. The turnover survey figures (BoE, New York Fed) and the gold rows are relayed.


### SOURCES

| Source | URL fetched | Free? | Terms quote | What it holds |
|---|---|---|---|---|
| BIS OTC derivatives, forwards and FX swaps, USD leg | https://stats.bis.org/api/v1/data/BIS,WS_OTC_DERIV2,1.0/H.A.D+I.B.5J.A.5J.A.USD.TO1.A.A.3.C?startPeriod=2022-S1&format=csv and https://data.bis.org/topics/OTC_DER/BIS,WS_OTC_DERIV2,1.0/H.A.D.B.5J.A.5J.A.USD.TO1.A.A.3.C | Yes, no login | “if the statistics are reproduced, the BIS must be cited” | Semi-annual net-net notionals, millions of USD. Code D is “outright forwards and fx swaps.” Code I is “currency swaps.” |
| BIS OTC gold notional and gross market value | https://stats.bis.org/api/v1/data/BIS,WS_OTC_DERIV2,1.0/H.A.A.L.5J.A.5J.A.TO1.TO1.A.A.3.C?startPeriod=2023-S1&format=csv and the gross-market-value key with `H.D.A.L…`; title at https://data.bis.org/topics/OTC_DER/BIS,WS_OTC_DERIV2,1.0/H.A.A.L.5J.A.5J.A.TO1.TO1.A.A.3.C | Yes, no login | Same BIS terms, fetched at https://data.bis.org/help/legal | Global gold, all instruments, “total (all counterparties),” “total (all sectors),” millions of USD. Latest period on the file is 2025-S2. |
| BIS terms | https://data.bis.org/help/legal | Yes | “The use of the statistics is unrestricted, provided that” | Citation, no paid enclosure of the figures, no claim of BIS endorsement. |
| BoE FXJSC | https://www.bankofengland.co.uk/markets/london-foreign-exchange-joint-standing-committee/results-of-the-semi-annual-fx-turnover-survey-april-2026 ; April 2025 and October 2025 and October 2024 result pages; April 2024 tables at https://www.bankofengland.co.uk/-/media/boe/files/markets/foreign-exchange-joint-standing-committee/semi-annual-fx-turnover-survey-results/2024/table-of-participating-financial-institutions-survey-results-tables-1-4-apr-2024.pdf | Yes to read, no login | “personal use or internal use within an individual organisation for non-commercial purposes” | Average daily UK FX turnover, USD billions, price-setting dealer in the UK, long leg of each swap once. April 2026 published 11 August 2026. |
| BoE legal page | https://www.bankofengland.co.uk/legal | Yes | The Open Government Licence sentence on that page applies to “the Database,” not to the FXJSC pages, which do not state it | FXJSC reuse is the general non-commercial rule above, unless the Bank grants more. |
| New York FXC, 11 August 2026 | https://www.newyorkfed.org/medialibrary/Microsites/fxc/files/2026/Volume-Survey-Press-Release-08112026 and https://www.newyorkfed.org/medialibrary/Microsites/fxc/files/2026/aprfxsurvey2026.pdf ; April 2025 release https://www.newyorkfed.org/medialibrary/Microsites/fxc/files/2025/Volume-Survey-Press-Release-07222025 | Yes, no login | “use, copy, and distribute Content for your personal or business purposes” | North American average daily OTC FX volume, millions of USD, 20 banks, long leg once. The release says “The Committee is not part of the Federal Reserve Bank of New York.” |
| NY Fed terms | https://www.newyorkfed.org/privacy/termsofuse | Yes | Quote above; keep the New York Fed’s source notice, and do not imply endorsement | Site-wide licence. FXC pages sit on that site. |
| LBMA / IBA prices | https://www.lbma.org.uk/prices-and-data/precious-metal-prices | History is not free | “A licence from IBA is required in order to obtain, use or redistribute” | The public page no longer holds the history. It has moved to MyLBMA and needs an IBA licence. |
| Third-party month-end LBMA reprints | https://learn.bulliontradingllc.com/charts/gold-price-in-2024/ and https://learn.bulliontradingllc.com/charts/gold-price-in-2025/ | Page loaded without login | Not stated on those pages. The benchmark itself is the IBA licence above | One last LBMA fixing per month, rounded to the dollar: $2,609 on 2024-12-30; $4,368 on 2025-12-30. No end-June 2024 fixing on the 2024 page. |
| Programme calendar and C-132 | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CALENDAR.tsv and https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-10-12-E021-Where-The-Money-Comes-From-Rates-FX-Commodities.md | Public repo | Repository licence not re-read | The 2026-11-20 row asks whether the dollar-leg year-on-year stays near +15.5% or falls toward +8%, June against June only. |

FX swaps alone, key `H.A.H.B.5J.A.5J.A.USD.TO1.A.A.3.C`, returned HTTP 404. Outright forwards alone, code E, also returned 404. The published stock is the combined forwards-and-FX-swaps series.

### RESULTS

BIS amounts below are the fetched `OBS_VALUE` figures. `UNIT_MULT` is 6, so the unit is millions of US dollars. S1 is end-June and S2 is end-December: 2025-S1 is above 2024-S2 in both series, and 2025-S2 is the last period on the file. Turnover is average daily dealing, not an outstanding stock.

| Finding | Value | Grade | Window / denominator | Source URL | Quote or row reference |
|---|---|---|---|---|---|
| London FX-swap turnover, April 2026 vs April 2025 | $2,172bn vs $1,563bn per day, **+39.0%** (2,172/1,563 − 1). Both surveys: 25 banks | MEASURED | April 2026 / April 2025 daily average, all currencies, USD | April 2026 and April 2025 BoE result pages | “rising by $332 billion to $2,172 billion”; April 2025: “FX swaps increased to $1,563 billion” |
| London FX-swap turnover, April 2025 vs April 2024 | $1,563bn vs $1,521bn per day, **+2.8%**. Reporters 25 vs 27 | BOUNDED | April 2025 / April 2024. The 2024 table lists 27 names, including Credit Suisse | April 2024 PDF, Table 1, “Foreign exchange swaps 1521” | Panel is not constant, so +2.8% is not a like-for-like bank set |
| New York FX-swap turnover, April 2026 vs April 2025 | $467,195mn vs $412,800mn per day, **+13.2%**. Dollar change on the PDF is +54,395. Both years: 20 banks, 22 trading days | MEASURED | April 2026 / April 2025 daily average | April 2026 PDF, swaps row; 11 Aug 2026 release | PDF: “467,195” and “13.2%”. Release: swaps “rose by … 13.2 percent” |
| New York FX-swap turnover, prior April | Published **+11.0%** year-on-year in April 2025. The April 2024 dollar level was not on a file fetched here | MEASURED for the rate | April 2025 / April 2024, as published | 22 July 2025 release | “swaps rising by 11.0 percent” |
| Two-centre April swap turnover | $1,975.8bn per day in April 2025 to $2,639.2bn in April 2026, **+33.6%** | MEASURED | Sum of the two daily averages. Not a world total. Asian surveys were not opened | Same BoE and NY pages | Price-setting location differs, so the two surveys are added rather than treated as one book |
| Forwards and FX swaps, dollar leg, end-June | 2024-S1: 66,139,364.184. 2025-S1: 75,703,774.784. **+14.46%**. Prior June: 2023-S1 61,103,464.253 to 2024-S1, **+8.24%** | MEASURED | 2025-S1 / 2024-S1, and 2024-S1 / 2023-S1. Millions of USD, net-net, all counterparties | BIS key `H.A.D.B.5J.A.5J.A.USD.TO1.A.A.3.C` | Portal title: “outright forwards and fx swaps, us dollar … outstanding - notional amounts” |
| Same series, end-December | 2024-S2: 65,126,903.898. 2025-S2: 74,022,849.397 ($74.023trn). **+13.66%** | MEASURED | 2025-S2 / 2024-S2 | Same key | Same file |
| Currency swaps, dollar leg | 2025-S2: 39,474,064.312 ($39.474trn), **+19.00%** vs 2024-S2 33,174,329.654 | MEASURED | 2025-S2 / 2024-S2 | BIS key with `DER_INSTR=I` | Portal title: “for currency swaps, us dollar” |
| The programme’s $113.5trn | D + I at 2025-S2 = 113,496,913.709 ($113.497trn), **+15.46%** vs 2024-S2 sum 98,301,233.552. End-June 2025 sum 113,870,058.865 is **+14.92%** vs end-June 2024 | IDENTITY for the sum; MEASURED for the year-on-year | Same semester. The +15.5% is December on December of this wider sum | Both keys above | Half-on-half, 2025-S1 minus 2024-S2, is $15.569trn. That is the seasonal gap C-132 removes |
| New York −21.4% and +18.3% | The 11 August release puts “Nonfinancial Customers” declining by 21.4 percent and “Other Financial Customers” increasing by 18.3 percent in the counterparty sentence. The swap sentence is separate: swaps −6.2% on October 2025 | MEASURED as the release’s wording | October 2025 to April 2026, all instruments in that sentence | 11 Aug 2026 release | Swap-only percent changes were not recomputed. The swap table gives April 2026 levels only: other financial 132,616 and nonfinancial 20,642, millions per day |
| Gold notional, USD | 2024-S1: 1,025,143.253. 2025-S2: 1,136,812.731. **+10.89%** | MEASURED | 2025-S2 / 2024-S1. This window mixes June and December | Gold notional key | Matches the critic’s $1,025,143m and $1,136,813m after rounding |
| Gold gross market value / notional | 2024-S1: 35,206.293 / 1,025,143.253 = **3.434%**. 2025-S2: 111,126.771 / 1,136,812.731 = **9.775%** | MEASURED | Gross market value divided by notional, same two semesters | Both gold keys | Matches 3.4% and 9.8% after one-decimal rounding |
| Gold, same semester | End-Dec 2025 notional is +10.93% vs end-Dec 2024 (1,024,820.109). The ratio went from 4.175% (42,782.520 / 1,024,820.109) to 9.775% | MEASURED | 2025-S2 / 2024-S2 | Same | Reported because C-132 forbids a June-versus-December growth rate |
| Implied gold quantity | End-Dec 2024: 1,024,820,109,000 / 2,609 / 32,150.7466 = **12.22 kt**. End-Dec 2025: 1,136,812,731,000 / 4,368 / 32,150.7466 = **8.09 kt** | BOUNDED | Notional divided by a rounded third-party month-end fixing. Troy ounce = 31.1034768 g | BIS gold notional; bullion pages above | The critic’s 13.7 kt to 8.2 kt was not reproduced. No end-June 2024 fixing was fetched. $4,368 gives 8.09 kt, not 8.2 kt |

The tonne figures are a quantity reading of notional divided by a price. They are not a cause of the gold price, and they do not say who holds which side. Dollar notional rose while the implied ounce quantity fell because the fixing rose by more than the quantity fell: 4,368/2,609 − 1 = +67.4%, and 8.09/12.22 − 1 = −33.8%. The product of those ratios is the +10.9% dollar change.

London’s all-instrument April 2026 year-on-year on the same page is +14%. The swap line, +39%, is the one used here.

### PRE-REGISTRATION

Dated **14 October 2026**, before the end-June 2026 BIS OTC release (programme calendar, 20 November 2026). This session cannot edit `CALENDAR.tsv`. The row to receive it is the 2026-11-20 BIS OTC row.

**Call.** The global net-net US-dollar notional of outright forwards and FX swaps, BIS `WS_OTC_DERIV2` key `H.A.D.B.5J.A.5J.A.USD.TO1.A.A.3.C`, at 2026-S1 will be **+11% to +18%** versus the 2025-S1 observation of **75,703,774.784 million dollars**. That is a level of **84,031,190 to 89,330,454 million dollars** ($84.031trn to $89.330trn).

**Falsified** if that print is below +11% or above +18%. Currency swaps are outside the call. A half-on-half change against end-December 2025 does not score it.

**Why this band.** Last June was +14.46%, and the June before that was +8.24%. Same-month swap turnover did not slow after April 2025: London went from +2.8% to +39.0%, and New York from +11.0% to +13.2%. The item’s rule then keeps the stock year-on-year away from the +8% accumulation pace. The band sits on +14.5% and does not pass London’s +39% dealing-volume change through into the stock. Dealing volume is not the outstanding notional. In the previous June, the stock year-on-year was already +14.5% while London April swap turnover was only +2.8%.

Grade of the call itself: **HYPOTHESIS**. Grade of the turnover facts used to place the band: as in the table.

### WHAT IT CHANGES

The state file’s “FX swap dollar debt … $113.5trn (+15.5% y/y, accelerating from +8.0%)” is the arithmetic of forwards-and-FX-swaps plus currency swaps. That sum and that December year-on-year check out. The BIS label “outright forwards and fx swaps” is the $74.023trn December stock, +13.66% year-on-year, and the June stock that 20 November will update was +14.46%, up from +8.24%. The +8% accumulation pace is the prior June of that series. The +15.5% figure is not the FX-swap line on its own.

Turnover does not pull that June year-on-year back toward +8%. The open question on the calendar becomes the range above. Nothing in these prints shows that dealing volume, or the gold-ounce decline, caused a price. The cross-currency basis is still unmeasured, so hedged versus unhedged demand is unchanged. The gold dollar ratio is a new measured fact beside the commodity paragraph: gross market value went from 3.434% of notional at end-June 2024 to 9.775% at end-December 2025, while dollar notional rose 10.9%. The ounce decline is bounded, and it does not name a holder.

### BUILD SPEC

Script: `bin/build_bis_otc_fx_gold.py`. Runtime: under one minute. Five small CSVs, no bulk file.

Inputs:

- `https://stats.bis.org/api/v1/data/BIS,WS_OTC_DERIV2,1.0/H.A.D.B.5J.A.5J.A.USD.TO1.A.A.3.C?format=csv` (forwards and FX swaps)
- `https://stats.bis.org/api/v1/data/BIS,WS_OTC_DERIV2,1.0/H.A.I.B.5J.A.5J.A.USD.TO1.A.A.3.C?format=csv` (currency swaps, stored separately)
- `https://stats.bis.org/api/v1/data/BIS,WS_OTC_DERIV2,1.0/H.A.H.B.5J.A.5J.A.USD.TO1.A.A.3.C?format=csv` (FX swaps alone; today 404)
- Gold notional `H.A.A.L.5J.A.5J.A.TO1.TO1.A.A.3.C` and gross market value `H.D.A.L.5J.A.5J.A.TO1.TO1.A.A.3.C`, same API prefix
- Optional local IBA/LBMA file, gitignored, columns `date`, `usd_per_troy_oz`. If absent, leave tonnes blank
- Turnover cells are not in an API: BoE headline pages and the April 2024 Table 1 PDF; NY `aprfxsurvey` PDFs

Outputs:

- `data/bis_otc/fx_usd_leg.csv`: `time_period`, `der_instr`, `label`, `obs_value_usd_mn`, `yoy_same_semester`
- `data/bis_otc/gold.csv`: `time_period`, `notional_usd_mn`, `gmv_usd_mn`, `gmv_over_notional`, `price_usd_oz`, `price_date`, `tonnes_implied`
- `data/fx_turnover/lon_ny_fx_swaps.csv`: `center`, `month`, `adv_usd_bn`, `reporters`, `yoy_same_month`
- `data/bis_otc/prereg_2026-11-20.tsv`: one row with base `75,703,774.784`, band `+0.11` to `+0.18`, registered `2026-10-14`

Assert:

- `UNIT_MEASURE=USD` and `UNIT_MULT=6`
- 2025-S2 D + I = 113,496,913.709 within 0.01, and that sum is not labelled FX swaps
- D 2025-S1 / D 2024-S1 − 1 = +14.458% within 0.01 percentage point
- The year-on-year function rejects S1 against S2
- Gold 2024-S1 ratio = 0.034343 and 2025-S2 ratio = 0.097753, within 1e-6
- No 2026-S1 row until the release; when it appears, score it against the band
- If code H ever returns, it must be less than or equal to D and must not be added to D
- London April 2026 / April 2025 − 1 = 2,172/1,563 − 1

### UNCERTAIN

The word “gold” on the portal was re-read on the second fetch of the notional page. The sector query for a non-total counterparty timed out, so “totals only” is the series label (“total (all counterparties),” “total (all sectors)”), not a full scan of other keys. A later 200 with another sector code would settle that.

The $2,609 and $4,368 fixings are a dealer’s rounded reprint of “one last available LBMA fixing per month,” dated 30 December, not a fetched IBA file and not necessarily the 31 December 2025 auction. The ounce quantity moves about 1.3% for a $56 change in the fixing, which is the gap between 8.09 kt and the critic’s 8.2 kt. The licensed file’s end-June 2024 and end-December 2025 prices, and the price convention embedded in dealers’ USD notionals, would settle the tonnes.

April 2024 New York dollars are implied by the published +11.0%, not read from that survey’s table. London’s October 2024 swap level was not taken from the spreadsheet; the page gives a 44% share of $3,217bn, which is too round to use. London day-counts for April 2025 and April 2026 were not on the headline pages. April 2024 states 21 working days.

Code H’s 404 is read as “not published at this cut.” A different dimension order that returns FX swaps alone would narrow the stock toward the turnover definition.

### NOT DONE

`CALENDAR.tsv` was not edited. This session is read-only. The pre-registration is the statement above.

FRED’s London gold CSV and the IMF commodity page timed out. The LBMA history page requires an IBA licence, so it was not bypassed. End-June 2024 tonnes, and the critic’s 13.7 kt, were therefore not recomputed.

The critic’s regression of the market-value ratio on the trailing gold return was not re-estimated. The item says to publish the two facts, not the model.

Asian primary survey pages were left unopened, as the item instructs. The −21.4% and +18.3% figures were not recomputed from an October 2025 swap-by-counterparty table.

---

## Item 12: IMF currency composition of the IIP: USD share of non-resident debt claims, as exposure weights for the hedge-ratio bound

*Status SUCCESS; 1258 s; breaches 0, blocked 0, unexpected tools 0, stage changes 0.*

*Cited without a fetch in this call, not relied on:* `https://api.imf.org/external/sdmx/2.1/data/IMF.STA,IIPCC/DEU?format=csv`; `https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/ER/~/{ISO3}.XDC_USD.EOP_RT.Q`; `https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/IIPCC/~/DEU.A_P.DCNRES_DIC.USD+FC+XDC+EUR+OTHC+UALLC.USD.Q`; `https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/IIPCC/~/{ISO3}.A_P.{IND}.{CCY}.USD.{Q|A}?c[TIME_PERIOD`


**Supervisor check.** IMF `IIPCC` Germany history re-fetched with the neutral User-Agent (debt claims on non-residents, US$ units). USD 901,684,652,600 (2019-Q4) and 1,135,071,419,400 (2026-Q2). FC 1,524,694,207,600 and 1,882,586,183,400. XDC 4,774,012,997,400 and 6,937,356,537,000. 2019-Q1: USD 915,141,307,500, FC 1,525,018,677,000, XDC 4,762,072,717,500. All match. The shares re-derive: USD/FC 59.14% to 60.29%; USD/all claims 14.56% (2019-Q1) to 12.87% (2026-Q2). The "14.6% to 12.9%" this return discusses came from the item text, not from any committed file. The other reporters' rows, the sector split and the yen adjustment are relayed.


### SOURCES

| Source | URL fetched | Free? | Terms quote | What it holds |
| --- | --- | --- | --- | --- |
| IMF IIPCC dataflow | https://api.imf.org/external/sdmx/3.0/structure/dataflow/IMF.STA/IIPCC/13.0.0?references=datastructure&detail=full | Yes, no login | "may be subject to special terms of use" | Currency composition of debt claims, debt liabilities, and foreign-currency derivative notionals. Dimensions: `COUNTRY.BOP_ACCOUNTING_ENTRY.INDICATOR.CURRENCY.UNIT.FREQUENCY`. |
| IMF IIPCC data | https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/IIPCC/~/DEU.A_P.DCNRES_DIC.USD+FC+XDC+EUR+OTHC+UALLC.USD.Q | Yes | same copyright page | End-period stocks. `OBS_VALUE` reads as US dollars (`SCALE="6"` on the series). Germany 2026-Q2 dollar claims are $1.135trn, matching the critic’s figure. |
| IMF currency codelist | https://api.imf.org/external/sdmx/3.0/structure/codelist/IMF.STA/CL_BOP_CURRENCY/3.0.0 | Yes | same | `USD`, `EUR`, `JPY` are children of `FC`. `FC` is "Foreign Currency". `XDC` is "Domestic currency". `OTHC` is "Other currencies". `_T` is "All currencies". |
| IMF indicator codelist | https://api.imf.org/external/sdmx/3.0/structure/codelist/IMF.STA/CL_BOP_INDICATOR/10.0.0/DCNRES_DIC | Yes | same | `DCNRES_DIC`: "Debt claims on nonresidents". Sectors: S121 central bank, S122 deposit-takers, S12R other financial corporations, S13 general government, S1Z other sectors, S1ZOTH the residual inside S1Z, `DCNRESICL_DIC` inter-company lending. |
| IMF availability | https://api.imf.org/external/sdmx/2.1/availableconstraint/IMF.STA,IIPCC,13.0.0/DEU.A_P..USD.USD.Q?references=none&mode=available | Yes | same | Units `EUR` and `USD` are legal. Published currencies in that constraint: `FC`, `JPY`, `OTHC`, `USD`, `XDC`, `XDRB`, `XXDR`, `_T`, `EUR`. |
| IMF exchange rates | https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/ER/~/DEU+JPN.XDC_USD.EOP_RT.Q?c%5BTIME_PERIOD%5D=ge:2019-Q4%2Ble:2026-Q2 | Yes | same | End-of-quarter national currency per US dollar. Yen: 144.74 (2025-Q2), 162.20 (2026-Q2). |
| IMF copyright page | https://www.imf.org/en/about/copyright-and-terms | Page is public | "may be subject to special terms of use" | The special-terms clauses below that sentence did not render on two fetches. |
| Dataset blurb | https://data.imf.org/Datasets/IIIPCC | Yes | not on that page | "snapshot of the currency breakdown of a country's foreign financial assets" |

The item’s 2.1 URL with only the country code, `https://api.imf.org/external/sdmx/2.1/data/IMF.STA,IIPCC/DEU?format=csv`, returned HTTP 500. `IIIPCC` on the 2.1 API returned HTTP 404. The working calls are SDMX 3.0, dataflow `IMF.STA/IIPCC`, version `~`, full six-part key, and `c[TIME_PERIOD]=ge:…+le:…`.

### RESULTS

Stocks are end-of-quarter positions in US dollars. The share is `CURRENCY=USD` divided by `CURRENCY=FC` (foreign currency, which excludes domestic currency `XDC`). Claims are `A_P` / `DCNRES_DIC`. Nothing here is a flow, and nothing is a price move.

| Finding | Value | Grade | Window / denominator | Source URL | Quote or row reference |
| --- | --- | --- | --- | --- | --- |
| Germany dollar claims, all foreign-currency debt claims | $1,135,071,419,400 / $1,882,586,183,400 = **60.293%** | MEASURED | 2026-Q2 stock; USD / FC, XDC excluded | [DEU 2026-Q2](https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/IIPCC/~/DEU.A_P.DCNRES_DIC.USD+JPY+EUR+OTHC+FC+XDC+_T.EUR+USD.Q?c%5BTIME_PERIOD%5D=ge:2026-Q2%2Ble:2026-Q2) | `CURRENCY=USD` 1135071419400; `FC` 1882586183400; `JPY` 33059691000; `OTHC` 714455073000. Those three sum to FC. |
| Same stock as a share of all debt claims | $1,135,071,419,400 / $8,819,942,720,400 = **12.869%** | MEASURED | 2026-Q2; USD / `_T`, and `_T` = FC + XDC | same | `_T` 8819942720400; `XDC` 6937356537000. 12.869% rounds to the critic’s 12.9%. The $1.135trn and $1.883trn FC figures are 2026-Q2, not 2026-Q1. |
| Germany, 2026-Q1, share of all claims | $1,117,283,656,000 / $8,667,085,468,600 = **12.891%** | MEASURED | 2026-Q1; USD / (FC+XDC) | [DEU history](https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/IIPCC/~/DEU.A_P.DCNRES_DIC.USD+FC+XDC+EUR+OTHC+UALLC.USD.Q) | 2026-Q1 USD 1117283656000, FC 1839877765600, XDC 6827207703000. Non-domestic share that quarter is 60.726%. |
| Germany, 2019-Q1, share of all claims | **14.556%** | MEASURED | 2019-Q1; USD / (FC+XDC) | same history URL | USD 915141307500, FC 1525018677000, XDC 4762072717500. This is the critic’s “14.6% in 2019”. 2019-Q4 is 14.315%. |
| Germany non-domestic share, 2019-Q4 to 2026-Q2 | 59.139% to **60.293%** (+1.15 pp) | MEASURED | Quarter-end stocks; USD / FC | history URL and 2019-Q4 cross-country pull | 2019-Q4 USD 901684652600, FC 1524694207600. |
| Germany private non-domestic share | 59.648% to **61.133%** (+1.48 pp) | MEASURED | 2019-Q4 to 2026-Q2; private = total minus S13. S121 has no FC or USD row | [sectors 2026-Q2](https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/IIPCC/~/DEU.A_P.DCNRES_DIC+DCNRES_DIC_S121+DCNRES_DIC_S122+DCNRES_DIC_S12R+DCNRES_DIC_S13+DCNRES_DIC_S1Z+DCNRES_DIC_S1ZOTH+DCNRESICL_DIC.USD+FC+XDC.USD.Q?c%5BTIME_PERIOD%5D=ge:2026-Q2%2Ble:2026-Q2) and [2019-Q4 sectors](https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/IIPCC/~/DEU.A_P.DCNRES_DIC_S121+DCNRES_DIC_S122+DCNRES_DIC_S12R+DCNRES_DIC_S13+DCNRES_DIC_S1ZOTH+DCNRESICL_DIC.USD+FC.USD.Q?c%5BTIME_PERIOD%5D=ge:2019-Q4%2Ble:2019-Q4) | 2026-Q2 private USD $1,121,861,215,800 / private FC $1,835,116,500,600. Government USD/FC fell from 48.61% to 27.83%, on a book of $13.2bn. |
| Sector add-up, Germany 2026-Q2 | FC and USD both close to the dollar | IDENTITY | 2026-Q2; FC and USD separately | sector URL above | `S1Z` = `S12R` + `S1ZOTH`. Total = S122 + S13 + S1Z + inter-company. S121 appears only in XDC ($1,233,243,262,800). |
| Germany sector USD/FC, 2026-Q2 | Banks 71.53%; other financial 52.10%; other residual 57.13%; inter-company 49.25%; government 27.83% | MEASURED | 2026-Q2; sector USD / sector FC | same | Banks USD 615530086200 / FC 860560335000. Dollar-stock weights of the $1.135trn: banks 54.23%, other financial 28.65%, inter-company 10.50%, other residual 5.46%, government 1.16%. |
| Germany, four-quarter non-domestic share | 60.932% to 60.293% = **−0.64 pp** | MEASURED | 2025-Q2 to 2026-Q2; USD / FC | history URL | 2025-Q2 USD 1119969060000, OTHC 682092280000, FC 1838069868000. Implied yen = $36,008,528,000. |
| Yen held at the 2025-Q2 rate | Share would be **60.166%**, a −0.77 pp change. Yen depreciation contributed about **+0.13 pp** | BOUNDED | Same window. Yen revalued with IMF yen per dollar, 144.74 then 162.20. `OTHC` ($714.5bn, 38% of FC) left in current dollars | [yen rates](https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/ER/~/DEU+JPN.XDC_USD.EOP_RT.Q?c%5BTIME_PERIOD%5D=ge:2019-Q4%2Ble:2026-Q2) | `JPN.XDC_USD.EOP_RT.Q`: 144.74 and 162.20. Constant-yen stock = 33059691000 × 162.20 / 144.74 = $37,047,684,676. |
| Euro-unit versus dollar-unit share | No second published share. A single exchange rate cancels in the ratio | IDENTITY | 2026-Q2. `UNIT=EUR` shells for Germany have no `OBS_VALUE`. Canada `UNIT=EUR` returned an empty dataset | Germany unit URL above; [Canada EUR unit](https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/IIPCC/~/CAN.A_P.DCNRES_DIC.USD+FC.EUR.Q?c%5BTIME_PERIOD%5D=ge:2026-Q2%2Ble:2026-Q2) | This is not the COFER constant-FX adjustment. COFER revalues each currency at a base rate. The unit switch does not. |
| Dollar liabilities, Germany | **$784,772,004,600** | MEASURED | 2026-Q2; `L_P` / `DLNRES_DIC` / `USD` | [liabilities](https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/IIPCC/~/DEU.L_P.DLNRES_DIC.USD+FC+XDC.USD.Q?c%5BTIME_PERIOD%5D=ge:2026-Q1%2Ble:2026-Q2) | 2026-Q2 USD 784772004600. 2026-Q1 is $734,174,895,200. The critic’s $0.785trn is 2026-Q2. |
| Derivative notionals | No observation | MEASURED as absent | Germany 2026-Q2, `F7FCT_DIC`, assets and liabilities, USD and FC | [F7 query](https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/IIPCC/~/DEU.A_P+L_P.F7FCT_DIC.USD+FC.USD.Q?c%5BTIME_PERIOD%5D=ge:2026-Q2%2Ble:2026-Q2) | Empty dataset. A stored zero was not returned. |

Non-domestic dollar share, debt claims. Korea is 2025-Q4. The other named reporters are 2026-Q2.

| Reporter | USD stock | FC stock | USD / FC | USD / all claims |
| --- | --- | --- | --- | --- |
| Canada | $1,622.587bn | $1,942.110bn | 83.548% | 74.446% |
| Spain | $377.420bn | $487.178bn | 77.471% | 15.745% |
| Korea (2025-Q4) | $523.137bn | $691.205bn | 75.685% | 73.146% |
| Netherlands | $1,668.447bn | $2,472.776bn | 67.473% | 30.369% |
| Germany | $1,135.071bn | $1,882.586bn | 60.293% | 12.869% |
| Switzerland | $1,262.069bn | $2,287.712bn | 55.167% | 47.984% |
| France | confidential (`STATUS="C"`) | $2,597.284bn | not computable | not computable |
| United States | no USD row | $2,316.687bn | not a non-domestic dollar series | dollar book is XDC, $10,371.502bn |

From 2019-Q4 to the latest point, USD/FC changed by: Canada +7.31 pp, Germany +1.15 pp, Spain −0.04 pp, Korea −0.17 pp, Netherlands −0.18 pp, Switzerland −1.67 pp. There is no common fall.

United States 2026-Q2 foreign-currency book: euro $1,007.784bn + yen $267.667bn + other $1,041.236bn = FC $2,316.687bn. Source: the USA component query in this session. Dollars are domestic currency, so they are outside the non-domestic denominator.

Among reporters with a published USD line, dollar-claim weights are Netherlands 25.32%, Canada 24.63%, Switzerland 19.16%, Germany 17.23%, Korea 7.94%, Spain 5.73%. France is out because the split is confidential. The US XDC dollar stock is a different object and is not in those weights.

The named missing centres returned an empty dataset for FC debt claims from 2024-Q4 through 2026-Q2: GBR, SWE, NOR, IRL, LUX, CHN, AUT, BEL, DNK, AUS. Brazil, Mexico and Poland did return 2026-Q2 USD and FC lines (USD/FC 88.37%, 3.36% and 26.73%). Italy was in that request and returned no series. The “eight reporters” list is the item’s list; the file has more quarterly reporters than those eight.

### WHAT IT CHANGES

The fx section of `state.md` still has no hedge ratio and no free cross-currency basis. These stocks do not fill either gap. Currency of denomination is unchanged by hedging, and the derivative-notional extract for Germany 2026-Q2 was empty, so net exposure after hedges is still unavailable.

What changes is the exposure-weight input the item was meant to supply, and the Germany reading inside the item. The fall from 14.6% to 12.9% is real and is the dollar’s share of all German debt claims. Over the same span the dollar’s share of foreign-currency claims rose, from 59.14% at 2019-Q4 to 60.29% at 2026-Q2, and the private slice rose from 59.65% to 61.13%. Euro-denominated claims grew faster than foreign-currency claims (XDC from $4,774bn to $6,937bn). That is a larger domestic-currency book, not a smaller dollar weight inside the foreign-currency book.

COFER in `state.md` is a different denominator: official reserve currency shares, constant-FX −0.94 pp over four quarters. This panel’s private non-domestic shares do not repeat that decline. That leaves the central-bank reserve result as it stands. It does not show private diversification away from the dollar in these debt-claim books, and it cannot say whether the claims are hedged.

### BUILD SPEC

Script: `bin/iipcc_usd_share.py`. Chunk by country. Unfiltered annual Japan returned HTTP 500.

Inputs:

- Data: `https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/IIPCC/~/{ISO3}.A_P.{IND}.{CCY}.USD.{Q|A}?c[TIME_PERIOD]=ge:{start}+le:{end}` with `Accept: text/csv`.
- `IND`: `DCNRES_DIC`, `DCNRES_DIC_S121`, `DCNRES_DIC_S122`, `DCNRES_DIC_S12R`, `DCNRES_DIC_S13`, `DCNRES_DIC_S1Z`, `DCNRES_DIC_S1ZOTH`, `DCNRESICL_DIC`.
- `CCY`: `USD+EUR+JPY+OTHC+FC+XDC+_T`.
- Same key with `UNIT=EUR`. Keep the column even when empty.
- Rates: `https://api.imf.org/external/sdmx/3.0/data/dataflow/IMF.STA/ER/~/{ISO3}.XDC_USD.EOP_RT.Q`.
- Countries: USA, DEU, FRA, NLD, CHE, CAN, ESP, KOR, JPN, plus BRA, MEX, POL. Assert an empty extract for GBR, SWE, NOR, IRL, LUX, CHN, AUT, BEL, DNK, AUS.

Outputs:

- `data/fx/iipcc_claims_usd.csv` — `country, time_period, indicator, currency, unit, obs_value_usd, status`.
- `data/fx/iipcc_share_by_sector.csv` — `country, time_period, sector, usd_usd, fc_usd, xdc_usd, usd_share_of_fc, usd_share_of_total, usd_stock_weight`.
- `data/fx/iipcc_exposure_weights.csv` — one row per country-sector at the latest common quarter, weights summing to 1 over rows with a numeric USD line.

Assert:

- `FC = USD + EUR + JPY + OTHC` within $1,000 where none of those rows is `STATUS=C`. If EUR is missing and the other three sum to FC, record EUR as zero.
- `_T = FC + XDC`.
- `S1Z = S12R + S1ZOTH` and `S122 + S13 + S1Z + DCNRESICL = DCNRES_DIC`, separately for USD and FC.
- Never fill `STATUS=C` with zero.
- Japan: if a year is off by about 10× or 100× from both neighbours, or the naive share prints as 0.0, drop the year and set `japan_excluded=1`.
- If both units exist, `usd_share` in EUR units and USD units must match. If EUR is empty, write `unit_eur_empty=1`.
- Constant-FX column revalues only JPY with `XDC_USD`. Leave `OTHC` in current dollars and set `othc_unrevalued=1`.

Runtime: about 2 minutes for these countries, quarterly from 2019, one country per request. Do not pull every currency in `CL_BOP_CURRENCY`.

### UNCERTAIN

- `SCALE="6"` was not decoded from a codelist. The observations are treated as US dollars because 2026-Q2 Germany matches the critic’s $1.135trn and $1.883trn. A scale codelist entry would settle it.
- 2025-Q2 German yen, $36,008,528,000, is FC minus USD minus OTHC, not a direct `JPY` observation. Fetch that one cell.
- Korea’s 2025-Q4 FC exceeds USD+JPY+OTHC by $62.8bn. That gap is the unpublished euro line until fetched.
- The US dollar series has values at 2026-Q2 and empty shells at 2019-Q4. The start quarter was not pinned down.
- `S1ZOTH` is labelled “Other sectors: Other”. The arithmetic says it is the non-financial residual inside S1Z. The codelist description is vaguer than that.
- The IMF special-terms paragraphs after “set out below” did not render. The reuse conditions beyond that sentence are unread.
- Germany’s euro per dollar did not return for `DEU` or `EUR` on `XDC_USD` / `USD_XDC`, so euro-unit stock levels were not computed. The share identity does not need the rate.

### NOT DONE

- Japan’s mis-scaled years were not repaired. Every annual `JPN` query returned HTTP 500, so Japan is excluded rather than corrected.
- France’s dollar share: `STATUS=C` on USD, EUR, JPY and OTHC at 2019-Q4 and 2026-Q2.
- A full constant-FX share. Only the yen leg was revalued, and only for Germany’s last four quarters. `OTHC` has no published currency split.
- A numeric zero on `F7FCT_DIC`. The extract was empty.
- Short-term rows (`DCNRES_DIC_S`, `…_S122_S`, and the other `_S` codes in the availability constraint) were not pulled.
- No pre-registration. The item does not ask for one.

---

## Item 13: Treasury intermediation pack: primary-dealer DV01 chart with the eSLR definition note, then settlement-day repo dispersion

*Status SUCCESS; 933 s; breaches 0, blocked 0, unexpected tools 0, stage changes 0.*

*Cited without a fetch in this call, not relied on:* `https://markets.newyorkfed.org/api/pd/get/PDPOSGST-TOT_PDPOSGSC-G7L11_PDPOSGSC-G11L21_PDPOSGSC-G21.json`; `https://markets.newyorkfed.org/api/rates/secured/sofr/search.json`; `https://markets.newyorkfed.org/api/rates/secured/sofr/search.json?startDate=&endDate=`; `https://markets.newyorkfed.org/api/rp/reverserepo/propositions/search.json`; `https://markets.newyorkfed.org/api/rp/reverserepo/propositions/search.json?startDate=&endDate=`


**Supervisor check.** New York Fed primary-dealer series `PDPOSGST-TOT` re-fetched: 256,389 (27 Dec 2023), 557,087 (25 Mar 2026) and 432,032 (30 Sep 2026), in millions. All match. The SOFR row for 30 Jun 2025 was re-fetched: median 4.45%, 99th percentile 4.65%, volume $2,946bn. It matches. The long-end bucket sums, the DTS cash figures and ON RRP are relayed. The "$176bn par" label that this return calls the wrong unit came from the item text, not from any committed file.


### SOURCES

| Source | URL fetched | Free? | Terms quote | What it holds |
| --- | --- | --- | --- | --- |
| NY Fed primary dealer positions | `https://markets.newyorkfed.org/api/pd/get/PDPOSGST-TOT.json` and `…/PDPOSGSC-G7L11_PDPOSGSC-G11L21_PDPOSGSC-G21.json` | Yes, no login | "use, copy, and distribute Content for your personal or business purposes" | Weekly net positions, millions of dollars. `PDPOSGST-TOT` is total Treasury ex-TIPS. The three buckets are coupons >7–11y, >11–21y, and >21y. Latest week 2026-09-30. `?startDate=` and `/api/pd/get/SBN2024/{keyid}.json` returned HTTP 400. |
| NY Fed series breaks | `https://markets.newyorkfed.org/api/pd/list/seriesbreaks.json` | Yes | Same NY Fed license | SBN2024 runs 2024-07-03 onward. The 11–21y and >21y buckets start 2022-01-05. |
| FR 2004 form page | `https://www.federalreserve.gov/apps/reportingforms/Report/Index/FR_2004` | Yes | No reuse sentence on this page. OMB 7100-0003. | "switching the reporting of position data to market value from par value". FR 2004A is dealers' outright positions, published as an aggregate. |
| Bowman speech, 1 Oct 2026 | `https://www.federalreserve.gov/newsevents/speech/bowman20261001a.htm` | Yes | No data-license sentence on the speech. | eSLR effective 1 Apr 2026, "optional early adoption beginning January 1, 2026". Supervisory positions "to over $700 billion at the end of April". Footnote: "Data from Federal Reserve Board, Form FR 2052a". |
| Fiscal Data DTS | Issues and redemptions on `…/v1/accounting/dts/deposits_withdrawals_operating_cash` | Yes, no login | "offered free, without restriction, and available to copy, adapt, redistribute" | Table II lines "Public Debt Cash Issues (Table IIIB)" and "Public Debt Cash Redemp. (Table IIIB)". `transaction_today_amt` is in millions of dollars. 342 business days, 2025-06-02 through 2026-10-09. |
| Fiscal Data TGA | `…/dts/operating_cash_balance` for 2026-06-15 | Yes | Same Fiscal Data license | TGA opening and closing balances, millions of dollars. |
| NY Fed SOFR | `https://markets.newyorkfed.org/api/rates/secured/sofr/search.json` | Yes | SOFR is a reference rate: "subject to the Terms of Use posted at newyorkfed.org" | `percentRate` is the volume-weighted median, percent. `percentPercentile99` and `volumeInBillions`. |
| NY Fed ON RRP | `https://markets.newyorkfed.org/api/rp/reverserepo/propositions/search.json` | Yes | Same NY Fed license. Not in the reference-rate restriction list. | `totalAmtAccepted` in dollars. The all-results search path returned HTTP 400. |
| NY Fed SOMA | `https://markets.newyorkfed.org/api/soma/summary.json` | Yes | Same NY Fed license | Weekly `bills`, `notesbonds`, and other holdings. Full history from 2003; recent rows were not in the truncated response. |
| Programme R2 note | `https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-27-R2-Treasury-Duration-Supply-And-Holders.md` | Yes | GitHub public file. | Public 10y-equivalents at constant end-2023 prices rose $9.5trn to $12.9trn, +$3.404trn, through 31 Aug 2026. |
| IORB | `https://www.federalreserve.gov/monetarypolicy/reserve-balances.htm` and H.15 `https://www.federalreserve.gov/releases/h15/` | Page is free | No reuse quote retrieved. | The reserve-balances table is a JavaScript placeholder. H.15 for 13 Oct 2026 does not list IORB. FRED `IORB` CSV returned HTTP 500. |
| NY Fed terms | `https://www.newyorkfed.org/privacy/termsofuse.html` (updated 6/9/2023) | — | License quote above | Primary dealer, SOMA, and ON RRP fall under the general license. SOFR needs the reference-rate notice. |

### RESULTS

Dispersion is p99 minus the volume-weighted median, in basis points. Net cash is public-debt cash issues minus cash redemptions, millions of dollars in the source, shown below in billions. The before window is an assumption: 2 Jun 2025–29 May 2026. The after window is 1 Jun 2026–9 Oct 2026, the last DTS day returned. June 2026 is in the after window.

**Dealer stock (fair value, not par).** The critic's levels match the API exactly.

| Finding | Value | Grade | Window / denominator | Source | Row |
| --- | --- | --- | --- | --- | --- |
| Total net Treasury ex-TIPS | $256.389bn on 2023-12-27; $540.028bn on 2026-03-18; $546.887bn on 2026-04-15; $432.032bn on 2026-09-30 | MEASURED | Wednesday net, millions of USD, all primary dealers | PD `PDPOSGST-TOT` | JSON values 256389, 540028, 546887, 432032 |
| Change in that total | +$175.643bn | MEASURED | 2023-12-27 to 2026-09-30 | Same | 432032 − 256389 |
| Annual mean of the Wednesday total | $212bn (2023), $302bn (2024), $397bn (2025); $476.669bn on 2025-12-31 | MEASURED | Calendar-year mean of weekly nets. 2025 has 53 Wednesdays. | Same | Matches the item's rounded means. Hand sums were $212.3bn, $301.6bn, $397.2bn. |
| Sample peak of the total | $557.087bn on 2026-03-25 | MEASURED | Highest week in the fetched 2026 file | Same | 557087 |
| Coupons over 7 years, sum of three buckets | $63.701bn on 2023-12-27; $150.265bn on 2025-12-31; $166.321bn on 2026-04-01; $133.062bn on 2026-09-30 | MEASURED | Sum of G7L11 + G11L21 + G21, millions of USD | Three bucket keyids | 17619+20721+25361=63701; 48913+42269+59083=150265; 38599+56961+37502=133062 |
| 2022–23 range of that long-end sum | $31.238bn (2022-06-15) to $63.701bn (2023-12-27) | MEASURED | Every 2022 Wednesday was summed. 2023 was checked at the October trough and the December peak. | Same | 2022-06-15: −6183+14317+23104=31238 |
| Long-end stock versus that range | 30 Sep 2026 is 2.09× the 2022–23 maximum, and 31 Dec 2025 was already 2.36× | MEASURED | Same fair-value sum. Not a post-rule break. | Same | 133062/63701=2.09; 150265/63701=2.36 |
| Path around the eSLR dates | Long end $150.3bn on 31 Dec 2025, $166.3bn on 1 Apr 2026, $133.1bn on 30 Sep 2026. Total net peaked 25 Mar 2026, then fell to $432.0bn, below the 31 Dec 2025 level. | MEASURED | Weekly nets. Early adoption 1 Jan 2026; rule effective 1 Apr 2026. | PD series and Bowman speech | Speech: "optional early adoption beginning January 1, 2026" |
| FR 2004 versus Bowman | Published net fair value at end-April 2026 is about $507–$547bn, not "over $700 billion". End-2025 net is $477bn, not about $600bn. | MEASURED | Different objects: FR 2004 aggregate net fair value versus confidential FR 2052a. | Both sources | Speech footnote names Form FR 2052a |
| $175.6bn / R2's +$3.404trn | 5.2% | BOUNDED | Unlike units. Numerator is the change in net fair value of all dealer Treasuries ex-TIPS. Denominator is the public stock's constant-price 10y-equivalents, end-2023 to 31 Aug 2026. | PD and R2 note | Not a duration share |
| Long-end DV01, central factors | About $79mn per bp on 2023-12-27 and about $157mn per bp on 2026-09-30 | BOUNDED | Assumed modified durations 7.5y, 12y, and 16y. DV01 = fair value × duration × 0.0001. Low/high factor ranges still leave 30 Sep 2026 above the 2022–23 maximum. | PD buckets. R2's security-level factors were not read. | Mix shifted toward 11–21y, so average duration eased; the stock more than doubled. |

The structural-break and half-life test was skipped, as the item says, with about nine months after 1 Apr 2026.

**SOFR p99 minus median on the ten largest net-cash days in each window.**

Before, mean net cash $92.5bn, mean dispersion 12.0bp, median dispersion 10.5bp.

| Date | Net cash | SOFR median | p99 | Dispersion | Volume |
| --- | --- | --- | --- | --- | --- |
| 2025-09-02 | $133.277bn | 4.39% | 4.50% | 11bp | $2,947bn |
| 2025-06-30 | $112.353bn | 4.45% | 4.65% | 20bp | $2,946bn |
| 2025-07-31 | $104.416bn | 4.39% | 4.48% | 9bp | $2,933bn |
| 2025-09-30 | $92.023bn | 4.24% | 4.38% | 14bp | $3,148bn |
| 2025-12-31 | $86.748bn | 3.87% | 4.00% | 13bp | $3,485bn |
| 2025-06-02 | $85.117bn | 4.35% | 4.43% | 8bp | $2,771bn |
| 2026-03-16 | $79.677bn | 3.70% | 3.79% | 9bp | $3,178bn |
| 2025-09-15 | $79.116bn | 4.51% | 4.68% | 17bp | $2,877bn |
| 2025-12-15 | $76.291bn | 3.75% | 3.85% | 10bp | $3,270bn |
| 2025-12-01 | $76.167bn | 4.12% | 4.21% | 9bp | $3,454bn |

After, mean net cash $59.4bn, mean dispersion 9.0bp, median 9bp.

| Date | Net cash | SOFR median | p99 | Dispersion | Volume |
| --- | --- | --- | --- | --- | --- |
| 2026-06-15 | $76.293bn | 3.69% | 3.78% | 9bp | $3,147bn |
| 2026-08-31 | $72.980bn | 3.68% | 3.77% | 9bp | $3,056bn |
| 2026-07-28 | $68.647bn | 3.65% | 3.74% | 9bp | $2,977bn |
| 2026-06-01 | $62.592bn | 3.65% | 3.74% | 9bp | $3,224bn |
| 2026-08-04 | $59.679bn | 3.66% | 3.74% | 8bp | $3,036bn |
| 2026-06-30 | $57.064bn | 3.68% | 3.80% | 12bp | $3,418bn |
| 2026-09-30 | $56.855bn | 3.90% | 3.99% | 9bp | $3,230bn |
| 2026-07-21 | $55.041bn | 3.61% | 3.69% | 8bp | $2,975bn |
| 2026-09-15 | $43.261bn | 3.64% | 3.72% | 8bp | $2,952bn |
| 2026-07-15 | $42.056bn | 3.64% | 3.73% | 9bp | $3,104bn |

| Finding | Value | Grade | Window / denominator | Source |
| --- | --- | --- | --- | --- |
| After minus before, mean dispersion | −3.0bp (9.0 versus 12.0) | MEASURED | Ten largest net public-debt cash days in each window above. Denominator is that day's SOFR volume-weighted median. | DTS Table II and SOFR API |
| Everyday June 2026 dispersion | 8–9bp on 1–5 Jun 2026 | MEASURED | Same definition, not restricted to large cash days | SOFR search, 2026-06-01 to 2026-06-05: p99−median of 0.09, 0.08, 0.09, 0.08, 0.08 |
| 15 Jun 2026 is also a tax day | Public-debt net cash $76.293bn. TGA opened at $816.023bn and closed at $979.791bn. Deposits were $234.538bn. | MEASURED | One DTS day. Tax deposits are not in the net-cash definition. | Issues 120019, redemptions 43726, TGA `open_today_bal` |
| ON RRP, selected days | $818.869bn on 2023-12-27; $460.731bn on 2025-06-30; $16.954bn on 2025-09-15; $105.993bn on 2025-12-31; $0.581bn on 2026-06-15 | MEASURED | Accepted amount, dollars, that operation date. Quarter-end prints are much larger than the 15 Sep 2025 print. | ON RRP propositions |

The −3bp gap is a comparison of two unmatched tails. The after window's ten largest days are smaller ($59bn versus $93bn), and both lists are full of month-ends, quarter-ends, and tax dates. On 15 Sep 2025, ON RRP was only $17bn and dispersion was still 17bp. That is not a slope of dispersion on Treasury cash, and it is not evidence that cash raising widened repo.

**Definitional gap.** FR 2004A positions are fair value, switched from par in 1990, and they are outright positions. The published series is one net number per week. The instructions, read earlier in this session, say to report in millions of dollars, at fair value, to net the same CUSIP, and not to report derivative contracts except forwards. Bowman's $600bn to over $700bn is Form FR 2052a, which is not public. The two cannot be reconciled from the published net. The item's "$176bn par" label is the wrong unit: the $175.6bn change is fair value.

### WHAT IT CHANGES

Relative to `state.md`, this does not change the duration result or the yield result. R2's +$3.404trn of public 10y-equivalents remains the stock that was absorbed. Dealers' published net book rose by $176bn of fair value, and the long end is above its 2022–23 range, but that elevation was already there on 31 Dec 2025, before either eSLR date. After 1 Apr 2026 the total net gave back the first-quarter rise. That is not a strained-conduit signature of a post-rule break, so it does not raise the weight on the refunding study.

The settlement-day SOFR tail was not wider after June 2026. On the item's own rule, a positive slope matters only if it is large. This comparison is not that slope, and it is not large in the direction the item flagged. It does not move the levered-bid ledger (futures shorts and Form PF) up the list.

No flow here is read as causing the 113bp rise in the 10-year yield.

### BUILD SPEC

Script: `bin/r13_dealer_dv01_repo_dispersion.py`. Expected runtime under two minutes, almost all HTTP. The SOMA summary is a long file and should be filtered after download.

Inputs:

- Dealer nets: `https://markets.newyorkfed.org/api/pd/get/PDPOSGST-TOT_PDPOSGSC-G7L11_PDPOSGSC-G11L21_PDPOSGSC-G21.json`. No date query. Millions of USD, fair value.
- DTS issues: `…/deposits_withdrawals_operating_cash?fields=record_date,transaction_today_amt&filter=transaction_catg:eq:Public Debt Cash Issues (Table IIIB),record_date:gte:2022-09-01`. Same call for `Public Debt Cash Redemp. (Table IIIB)`.
- TGA: `…/operating_cash_balance`, account type `Treasury General Account (TGA) Closing Balance`, field `open_today_bal`, millions.
- SOFR: `https://markets.newyorkfed.org/api/rates/secured/sofr/search.json?startDate=&endDate=`.
- ON RRP: `https://markets.newyorkfed.org/api/rp/reverserepo/propositions/search.json?startDate=&endDate=`, `totalAmtAccepted` in dollars.
- Fed bills: `https://markets.newyorkfed.org/api/soma/summary.json`, field `bills`. Confirm the unit in the SOMA dictionary before using it.
- Reserves: H.4.1 was not fetched. Do not invent a series code.
- IORB: no working file URL yet. FRED CSV returned HTTP 500.
- Durations: a midpoint table stored in the script (7.5 / 12 / 16, with the low-high range above). Do not use CME. Join `bin/r2_duration_supply.py` only after that file is read.

Outputs:

- `data/r13/dealer_weekly.csv` — `asof_date`, `tot_fv_usd_mn`, `g7l11`, `g11l21`, `g21`, `long_end_fv_usd_mn`, `dv01_usd_per_bp`, `dv01_low`, `dv01_high`.
- `data/r13/net_cash_days.csv` — `record_date`, `issues_usd_mn`, `redemptions_usd_mn`, `net_usd_mn`, `tax_date_flag`, `month_end_flag`.
- `data/r13/sofr_dispersion_top10.csv` — `record_date`, `window`, `net_usd_mn`, `sofr_median`, `sofr_p99`, `dispersion_bp`, `volume_usd_bn`, `onrrp_usd`, `tga_usd_mn`.
- `data/r13/dispersion_regression.csv` — coefficient on net cash, coefficient on net cash × ON RRP (or reserves), controls for TGA, tax dates, month-end, and SOMA bills, with standard errors, n, and the sample window. Label it as a sensitivity of repo dispersion to Treasury cash raising.

Assert: totals 256389, 540028, 546887, 432032; long-end sums 63701 and 133062; 2026-06-15 issues 120019 and redemptions 43726; SOFR 2026-06-01 median 3.65 and p99 3.74; dispersion equals p99 minus median; G11L21 and G21 start 2022-01-05; no structural-break test.

### UNCERTAIN

The before window starts 2 Jun 2025 rather than at the DTS start in Sep 2022. A longer before window could replace some of the ten days. The 11th before day was 5 Aug 2025 at $74.0bn, so the cutoff is not a tie. The 2026 long-end peak was not taken from a sum of every week; 25 Feb 2026 at $175.739bn was the highest week added. The 30 Sep 2026 level does not depend on that peak. DV01 factors are assumed par-bond durations, not R2's security-level factors. SOMA `bills` was not read from a data dictionary. The FR 2052a line behind Bowman's $600bn to $700bn is not public. A full ON RRP path, rather than the five dates above, would date when ordinary-day usage fell from hundreds of billions to the teens.

### NOT DONE

The regression of dispersion on net cash, interacted with ON RRP or reserves and controlled for TGA, tax dates, month-end, and Fed bill buying. That needs the script. IORB was not measured: the Board page did not render a rate, H.15 does not list it, and the FRED CSV returned HTTP 500. Reserve balances were not fetched. Auction-settlement markers were not pulled as a separate auction file; the cash days above are the settlement measure used. No chart image was drawn. The half-life test stays skipped.

---

## Item 14: Refunding-day and buyback event study, daily leg only, with an unclean 4 Nov observation logged in advance

*Status SUCCESS; 951 s; breaches 0, blocked 0, unexpected tools 0, stage changes 0.*

*Cited without a fetch in this call, not relied on:* `https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query`; `https://home.treasury.gov/policy-issues/financing-the-government/quarterly-refunding/most-recent-quarterly-refunding-documents`; `https://www.newyorkfed.org/medialibrary/media/research/data_indicators/ACMTermPremium.xls`; `https://www.newyorkfed.org/medialibrary/media/research/staff_reports/metadata_2011_sr340_term_structure_linear.pdf`


**Supervisor check.** The first call ended with rc 1 and no answer after 15 fetches. It was resumed in the same Cursor session and stage, and the statistics above merge the two calls. The event-day closes were re-read from the Treasury 2025 and 2026 par CSVs. 5 Feb 2025: 10y 4.52→4.43, 30y 4.75→4.64. 6 May 2026: 4.43→4.36 and 4.98→4.94. 5 Aug 2026: 4.63→4.63 and 5.18→5.17. 19 Aug 2026: 4.71→4.65 and 5.28→5.19. All match. Treasury press release sb0607 was re-fetched and says the long-end buyback maximum "will be at least $4 billion per operation". The Wednesday placebo percentiles (−8 and +8bp, n=107) are relayed: the exclusion list was not rebuilt. The pre-registration for 4 Nov was written into `CALENDAR.tsv` on 14 Oct, with the 2 Nov financing estimates as a separate row.


### SOURCES

| Source | URL fetched | Free? | Terms quote | What it holds |
| --- | --- | --- | --- | --- |
| Treasury par yield curve CSV, 2023–2026 | `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2026/all?type=daily_treasury_yield_curve&field_tdr_date_value=2026&page&_format=csv` (same pattern for 2023, 2024, 2025) | Yes, no login | No reuse sentence on the CSV pages opened | Business-day par CMT, percent per year. 2023–24: 1-month through 30-year. 2025–26 adds 1.5-month. Latest row 13 Oct 2026 |
| Quarterly refunding statements, Nov 2023–Aug 2026 | `https://home.treasury.gov/news/press-releases/jy1864`, `jy2062`, `jy2315`, `jy2512`, `sb0384`, `sb0489`, `sb0590`, plus `sb0010`, `sb0120`, `sb0212`, `sb0305` | Yes, no login | No reuse sentence on the pages opened | Auction-size tables, forward guidance, buyback plans. Next statement dated Wednesday 4 Nov 2026 |
| 19 Aug 2026 buyback release | `https://home.treasury.gov/news/press-releases/sb0607` | Yes, no login | No reuse sentence on the page opened | Long-end liquidity-support maximum: “will be at least $4 billion per operation”, effective 9 Sep through 4 Nov 2026 |
| Refunding calendar page | `https://home.treasury.gov/policy-issues/financing-the-government/quarterly-refunding/most-recent-quarterly-refunding-documents` | Yes, no login | No reuse sentence on the page opened | Financing estimates next on 2 Nov 2026; refunding documents next on 4 Nov 2026. Neither date is a row in the programme calendar |
| FiscalData `auctions_query` | Dataset `https://fiscaldata.treasury.gov/datasets/treasury-securities-auctions-data/treasury-securities-auctions-data`; API docs `https://fiscaldata.treasury.gov/api-documentation/`; probe `https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/accounting/od/auctions_query` | Yes, no account or token | “offered free, without restriction, and available to copy, adapt, redistribute” | Announced and auctioned marketable Treasuries, 15 Nov 1979–20 Oct 2026. Fields include `auction_date`, `security_term`, `offering_amt` |
| NY Fed ACM | `https://www.newyorkfed.org/medialibrary/media/research/data_indicators/ACMTermPremium.xls` (HTTP 500, twice); terms shell `https://www.newyorkfed.org/terms-of-use`; metadata `https://www.newyorkfed.org/medialibrary/media/research/staff_reports/metadata_2011_sr340_term_structure_linear.pdf` | File named and public; this fetch failed | “Please cite.” | Daily and monthly ACM term premium, fitted yield, and risk-neutral yield, 1y–10y. The monthly plot CSV is month-end only |
| FOMC calendar | `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm` | Yes, no login | No reuse sentence on the page opened | Meeting dates. Decision day taken as the second day. July 2026 minutes released 19 Aug 2026 |
| BLS release schedules | `https://www.bls.gov/schedule/2024/`, `/2025/`, `/2026/`, and `https://www.bls.gov/schedule/news_release/cpi.htm` | Yes, no login | No reuse sentence on the pages opened | CPI at 08:30 ET. 4 Nov 2026 is not a CPI day; October CPI is Tuesday 10 Nov 2026 |
| Programme calendar | `https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CALENDAR.tsv` | Public repo | Repository file, no separate data licence on that file | No 2 Nov 2026 or 4 Nov 2026 refunding row |

### RESULTS

Units are par constant-maturity yields, percent per year. The 1-day change is the announcement-day close minus the prior Treasury business day, in basis points. Refunding statements are 08:30 ET, so that close is the first close after the text. Placebo days are other Wednesdays from 8 Nov 2023 through 7 Oct 2026. Excluded from the placebo: the event Wednesdays below, FOMC decision Wednesdays, and CPI Wednesdays (10 Apr, 15 May, 14 Aug, 11 Sep, 13 Nov, 11 Dec 2024; 15 Jan, 12 Feb, 12 Mar, 11 Jun 2025; 11 Mar, 10 Jun, 12 Aug 2026). Percentiles use nearest rank, `ceil(p × n)`, on n = 107.

| Finding | Value | Grade | Window / denominator | Source URL | Quote or row |
| --- | --- | --- | --- | --- | --- |
| Wednesday placebo, 10y and 30y | 5th percentile −8 bp, median 0, 95th percentile +8 bp. 10y min −10, max +16 (6 Nov 2024). 30y min −11 (8 Nov 2023), max +16 (6 Nov 2024) | MEASURED | 1-day CMT change; Wednesdays 8 Nov 2023–7 Oct 2026; n=107 after FOMC and CPI drops | Treasury year CSVs above; FOMC and BLS calendars above | Rank 6 = −8 bp; rank 102 = +8 bp |
| Nominal coupon increases | 1 Nov 2023 and 31 Jan 2024 raise coupon sizes. 1 May 2024 stops further increases | MEASURED as text; price link is HYPOTHESIS | Those three statements. All three are FOMC decision days, so they are out of the clean set | `jy1864`, `jy2062`, `jy2315` | “continue gradually increasing coupon auction sizes”; 31 Jan also announces the increases and says no further increases are anticipated beyond that quarter |
| Clean nominal coupon-size changes | 0 | MEASURED | 12 statements from 1 Nov 2023 to 5 Aug 2026, after dropping five FOMC decision days | Size tables in `jy2512`, `sb0010`, `sb0489`, `sb0590` | From the July 2024 grid onward the nominal coupon block stays 2y 69, 3y 58, 5y 70, 7y 44, 10y 42/39/39, 20y 16/13/13, 30y 25/22/22, FRN 28/28/30 |
| Clean statement-day yield changes | See the eight rows below | MEASURED for the bp; supply reading HYPOTHESIS | 1-day CMT change on the event date | Treasury CSVs | Levels under each row |
| 19 Aug 2026 buyback size | Per-operation maximum for 10–20y and 20–30y goes from $2bn to at least $4bn, effective 9 Sep–4 Nov 2026. 10y −6 bp, 30y −9 bp | HYPOTHESIS | 1-day CMT change, 19 Aug vs 18 Aug 2026. Sign matches larger buybacks (yields down). 10y is inside [−8, +8]; 30y is 1 bp outside | `sb0607`; CSV rows 19 Aug and 18 Aug 2026 | “will be at least $4 billion per operation”. Closes: 10y 4.65 vs 4.71; 30y 5.19 vs 5.28 |
| Joint supply-effect hit | None under a both-maturity, outside-band, supply-sign rule | HYPOTHESIS | Clean events only. Ceiling set by the item | Same | The only clean size change does not put both maturities outside the band |

Clean Wednesday observations, levels in percent, changes in bp. Band is [−8, +8].

| Date | What the text did | 10y t / t−1 | Δ10 | 30y t / t−1 | Δ30 |
| --- | --- | --- | --- | --- | --- |
| 30 Oct 2024 | Coupon grid unchanged versus the July 2024 and February 2025 tables. Buyback paragraph not read in full | 4.29 / 4.28 | +1 | 4.49 / 4.52 | −3 |
| 5 Feb 2025 | Nominal grid unchanged Nov 2024–Apr 2025. Not CPI, not an FOMC decision | 4.43 / 4.52 | −9 | 4.64 / 4.75 | −11 |
| 30 Apr 2025 | Nominal grid unchanged. Same morning is the Employment Cost Index at 08:30 | 4.17 / 4.19 | −2 | 4.66 / 4.64 | +2 |
| 5 Nov 2025 | Nominal grid unchanged. December 5y TIPS reopening +$1bn, to $24bn | 4.17 / 4.10 | +7 | 4.74 / 4.67 | +7 |
| 4 Feb 2026 | “maintaining nominal coupon and FRN auction sizes”. Liquidity buybacks up to $38bn; cash-management cap stated at $75bn | 4.29 / 4.28 | +1 | 4.91 / 4.90 | +1 |
| 6 May 2026 | Same maintain sentence. Liquidity cap $38bn; cash-management cap $25bn. 20y reopening settlement moves to Friday from the June reopening | 4.36 / 4.43 | −7 | 4.94 / 4.98 | −4 |
| 5 Aug 2026 | Same maintain sentence and the same nominal grid. Buyback caps $38bn and $25bn, matching May | 4.63 / 4.63 | 0 | 5.17 / 5.18 | −1 |
| 19 Aug 2026 | Buyback maximum at least $4bn. FOMC minutes of 28–29 Jul released the same day | 4.65 / 4.71 | −6 | 5.19 / 5.28 | −9 |

FOMC decision days, shown so the contaminated supply news is visible. They are not in the clean set. Supply-increase days all closed with lower yields.

| Date | Overlap | Δ10 | Δ30 | News |
| --- | --- | --- | --- | --- |
| 1 Nov 2023 | FOMC | −11 | −8 | Coupon sizes up; 10y +$2bn, 30y +$1bn |
| 31 Jan 2024 | FOMC and Employment Cost Index 08:30 | −7 | −6 | Another quarter of coupon increases; small-value buyback tests in April |
| 1 May 2024 | FOMC | −6 | −5 | Further coupon increases stopped; regular buybacks start 29 May, up to $2bn |
| 31 Jul 2024 | FOMC and Employment Cost Index 08:30 | −6 | −5 | Coupon guidance unchanged; 20-CUSIP cap removed |
| 30 Jul 2025 | FOMC | +4 | +3 | Coupons maintained; long-end buyback frequency doubled; liquidity-support cap “from $30 billion per quarter to $38 billion” |

5 Feb 2025 is the one flat-grid day with both yields outside the band, and the move is down. That is a placebo breach without a coupon-size change. 19 Aug 2026 has the buyback sign and misses the joint rule because the 10y change is inside the band.

### PRE-REGISTRATION

Dated 14 October 2026, before the 2 November financing estimates and the 4 November statement.

On 4 November 2026, score the close minus the 3 November 2026 close, in basis points, for the par 10-year and par 30-year CMT. 3 November is a business day on the BLS calendar (JOLTS at 10:00). A supply-effect reading requires both changes strictly outside [−8, +8] bp, the same sign, and that sign equal to the supply news in the 4 November statement: up if nominal coupon sizes rise above the current grid or the long-end buyback maximum is cut below “at least $4 billion”; down if coupon sizes fall or that maximum is raised. One maturity outside, mixed signs, or the opposite sign does not count. ACM 10-year term premium uses the same sign rule against its own Wednesday 5th–95th percentile once the daily file is readable; it has no numeric band today. The 30-year swap spread is out of this score until item 3 exists.

This observation is unclean even if it clears the band. 4 November is the session after the 3 November 2026 election. It is not an FOMC decision day (the October meeting is 27–28 Oct; the next is 8–9 Dec) and not a CPI day (CPI is Tuesday 10 Nov). The grade ceiling is HYPOTHESIS. 2 November, the 15:00 financing estimates, is calendared and is not this close-to-close score.

### WHAT IT CHANGES

The rates charter in `state.md` still stands: no flow in this programme has been shown to cause a yield move. This test does not supply that identification. The coupon increases since November 2023 fall on FOMC decision days, and the one clean buyback-size announcement does not move both the 10-year and the 30-year outside the Wednesday band. A null on 4 November would say the same thing with low power. A both-maturity, right-sign breach on 4 November would be the first candidate, and the election keeps it at HYPOTHESIS. Nothing here settles the term-premium versus expected-rate split. 2 November and 4 November are still absent from `CALENDAR.tsv`.

### BUILD SPEC

Script: `bin/refunding_day_daily.py`. Runtime under 2 minutes; the ACM workbook is about 10MB and the yield files are one year each.

Inputs:

- Yield CSVs, one year per URL, `type=daily_treasury_yield_curve`, years 2023–2026 and then the new year.
- Event list from the press-release URLs above, plus `sb0607`.
- FOMC second days from `https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm`.
- CPI 08:30 dates from `https://www.bls.gov/schedule/2024/`, `/2025/`, `/2026/`.
- ACM daily sheet in `ACMTermPremium.xls`, columns `DATE` and `ACMTP10`, when the file returns HTTP 200. Do not substitute the month-end plot CSV.
- Swap spread only after item 3 writes a daily 30-year series. FiscalData `v1/accounting/od/auctions_query` is the check that `offering_amt` matches the statement grid, not a price input.

Outputs:

- `data/refunding_events.csv`: `date`, `guidance_change`, `buyback_change`, `fomc_decision`, `cpi_0830`, `unclean`, `prior_date`, `y10`, `y30`, `d10_bp`, `d30_bp`, `acmtp10`, `d_acmtp10_bp`.
- `data/refunding_placebo_wednesdays.csv`: `date`, `d10_bp`, `d30_bp`, `d_acmtp10_bp`.
- `data/refunding_prereg_2026-11-04.csv`: the band, the sign rule, `scored=false` until the 4 Nov close exists.

Assert: 12 statements plus the 19 Aug buyback; FOMC drops include 1 Nov 2023, 31 Jan 2024, 1 May 2024, 31 Jul 2024, 30 Jul 2025; none of the eight clean dates above is a CPI day; 19 Aug 2026 prints −6 and −9; the placebo percentile function reproduces −8 and +8 on this vintage; the 4 Nov row stays unscored beforehand; the note does not say the flow caused the yield. Add 2 Nov and 4 Nov 2026 to `CALENDAR.tsv`.

### UNCERTAIN

November 2023’s CPI weekday was not on a BLS page opened here. If it was a Wednesday, placebo n falls by one. The 30 Oct 2024 buyback paragraph was not read in full; the coupon grid is unchanged by comparing the July 2024 and February 2025 tables. The 4 Feb 2026 “$75 billion” cash-management sentence was read from the press-release extract, then compared with the full 6 May text at $25bn. Whether those caps are like-for-like quarters is an inference. Search extracts of later buyback operation notices show a $6,000,000,000 figure; the 19 Aug policy page that was opened says the maximum “will be at least $4 billion per operation”, not $6bn. ISM services for the week of 4 Nov was not opened. The Aug 19 price move shares the day with the FOMC minutes release.

### NOT DONE

ACM 1-day changes: `ACMTermPremium.xls` returned HTTP 500 on both tries, so there is no term-premium number and no ACM band. The 30-year swap spread was not computed; it waits on item 3, and no swap-spread file was in the repo paths opened. The 30-minute tape was left out, as the item says. 4 November cannot be scored; the close does not exist yet. The `auctions_query` probe for a bond on 12 Aug 2026 returned an empty page because that day’s long coupon was the 10-year note; the endpoint and field names did answer.

---

## Item 15: Global comovement in 10y yields: US, Germany, UK, Japan, weekly and low-frequency, with break-date intervals

*Status SUCCESS; 945 s; breaches 0, blocked 0, unexpected tools 0, stage changes 0.*

*Cited without a fetch in this call, not relied on:* `https://api.statistiken.bundesbank.de/rest/data/BBSIS/D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A`; `https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y?format=csvdata&detail=dataonly&startPeriod=2018-01-01`; `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve&field_tdr_date_value={year}&page&_format=csv`


**Supervisor check.** The US weekly 10y changes were re-derived from the Treasury 2026 par CSV (last print of each ISO week, 2 Jan to 31 Jul 2026). They reproduce all 30 changes Grok lists, and the endpoints 4.19 and 4.75. The three correlations recomputed from the listed changes are 0.76, 0.88 and 0.72. They match. The Bund leg (Bundesbank) and the JGB and ECB rows are relayed.


### SOURCES

| Source | URL fetched | Free? | Terms quote | What it holds |
|---|---|---|---|---|
| US Treasury par yield curve | `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/2026/all?type=daily_treasury_yield_curve&field_tdr_date_value=2026&page&_format=csv` and the 2024 file of the same form; December 2023 also read from the monthly XML `field_tdr_date_value_month=202312` | Yes, no login | "not available for any work of the United States Government" (`https://www.govinfo.gov/content/pkg/USCODE-2023-title17/html/USCODE-2023-title17-chap1-sec105.htm`) | Daily par yields, percent. 2026 file runs 2 Jan–13 Oct 2026. 10-year is the column `10 Yr`. |
| US Treasury par real yield curve | same CSV path with `type=daily_treasury_real_yield_curve` for 2023 and 2026 | Yes, no login | Same statute | Daily TIPS par real yields, percent. Columns `5 YR` through `30 YR`. |
| Bundesbank Svensson 10-year | `https://www.bundesbank.de/statistic-rmi/StatisticDownload?tsId=BBSIS.D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A&mode=its&its_csvFormat=en&its_currency=default&its_dateFormat=default&its_from=2026-01&its_to=2026-08` | Yes, no login | "free to save, forward or reproduce the information" (`https://www.bundesbank.de/en/homepage/user-information/conditions-for-the-general-use-of-the-website-764706`) | Daily Svensson spot rate on listed Federal securities, residual maturity 10.0 years, unit percent. This download's `last update` is `2026-08-03`. Rows exist from 2 Jan through 3 Aug 2026. October returned a header only. |
| Bundesbank REST | `https://api.statistiken.bundesbank.de/rest/data/BBSIS/D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A?...` | Endpoint refused | Same site terms | HTTP 500. A shorter `BBK01/WT1010` call returned HTTP 400. |
| MoF JGB curve, current month | `https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/jgbcme.csv` | Yes, no login | MoF applies PDL1.0 where no other mark is shown (`https://www.mof.go.jp/about_mof/notice/index.html`). PDL1.0: "商用利用も可能です" and numerical data are outside copyright (`https://www.digital.go.jp/resources/open_data/public_data_license_v1.0`) | October 2026 only. Constant-maturity yields, percent. MoF Q&A: "semiannual compound interest rate on a constant maturity basis" (`https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/qa.htm`). |
| MoF JGB history | `https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv` | Yes, no login | Same | Full history exists. The fetch began at 1974/9/24 and stopped in 1979, so 2018–2026 rows were not read. |
| ECB AAA 10-year spot | `https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y?startPeriod=2026-09-01&endPeriod=2026-10-13&format=csvdata&detail=dataonly` | Yes, no login | English copyright section did not render. Danish page of the same notice: "Enhver videregivelse eller gengivelse af oplysninger skal være nøjagtig, og ECB skal anføres som kilde." (`https://www.ecb.europa.eu/services/using-our-site/disclaimer/html/index.da.html`) | Euro-area AAA government-bond 10-year spot, Svensson, continuous compounding, percent per annum. Not the Bund. |
| BoE gilt curves | Page `https://www.bankofengland.co.uk/statistics/yield-curves`. Fetch of `.../latest-yield-curve-data.zip` returned HTTP 500. Archive zips are listed, not opened. | Page is public. Zip not retrieved. | Database: "subject to the terms of the UK Open Government Licence" (`https://www.bankofengland.co.uk/legal`). OGL: "copy, publish, distribute and transmit the Information" (`https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/`). The yield-curve spreadsheets are website Resources, whose stated permission is personal or internal non-commercial use. Charts name Bloomberg and Tradeweb. | Nominal, real and inflation gilt curves. The page says there is no API. Nominal daily archive is listed as ZIP 39.2MB; real daily as ZIP 25.1MB. |

### RESULTS

| Finding | Value | Grade | Window / denominator | Source URL | Quote or row |
|---|---|---|---|---|---|
| US 10-year par rose 113bp, of which real 96bp and breakeven 17bp | 3.88% to 5.01% nominal; real 1.72% to 2.68%; breakeven 2.16% to 2.33% | MEASURED | Levels in percent. 29 Dec 2023 to 18 Sep 2026. Breakeven is nominal minus real on those dates. | Par and real CSVs above; Dec 2023 par also in the monthly XML | `2023-12-29` par `BC_10YEAR` 3.88; real row `12/29/2023` `10 YR` 1.72. `09/18/2026` par `10 Yr` 5.01; real `10 YR` 2.68. |
| US and Bund weekly changes moved together in early 2026, while the US level rose further | Correlation of weekly changes: US nominal–Bund 0.76; US nominal–US real 0.88; US real–Bund 0.72. Two-nominal first-factor share 88% of the correlation trace. Over the same weeks the US 10-year rose 56bp (4.19 to 4.75) and the Bund 25bp (2.96 to 3.21); US real rose 53bp (1.94 to 2.47). | MEASURED for this pair and window. Not the four-country test. | 30 weekly changes, weeks ending 9 Jan 2026–31 Jul 2026. Last print of each calendar week. Changes in basis points. Denominator of the share is the trace of the 2×2 correlation matrix, which equals 2. | Treasury 2026 par and real CSVs; Bundesbank StatisticDownload Jan–Aug 2026 | Sums of the 30 changes, in bp: US 56, real 53, Bund 25. Sums of squares: 2560, 1739, 1559. Cross-products: US×real 1858, US×Bund 1521, real×Bund 1182. Share `(1+0.76)/2`. |
| That 88% does not put the term-premium split in a global-factor frame | The share is high because there are only two series and their correlation is 0.76. Japan and the UK are absent, August–October 2026 is absent, and no break date was estimated. | HYPOTHESIS if read as the item's 2024–26 conclusion | Same 30 weeks. Not a cause. | Same rows | The Bund's cumulative rise is 25bp against the US 56bp in this slice. |
| Item's Bund prints for 1–2 Oct 2026 were not in the file | Download `last update,2026-08-03`. Last numeric row is `2026-08-03,3.21`. July month-end is `2026-07-31,3.21`. | MEASURED as a property of this file | This endpoint, fetched 14 Oct 2026 | StatisticDownload URL above | Header line `last update,2026-08-03 12:53:39` |
| ECB AAA is a different curve from the Bund | 1 Oct 2026: 3.592%. 2 Oct 2026: 3.464%. 24 Sep 2026: 3.566%. | MEASURED | Daily spot, percent per annum, continuous compounding | ECB URL above | `TIME_PERIOD` `2026-10-01` `OBS_VALUE` 3.5921733451; `2026-10-02` 3.4639685465 |
| JGB 10-year in the October file | 1 Oct 3.092%; 13 Oct 3.019% | MEASURED | Daily constant-maturity percent. October 2026 file only. | `jgbcme.csv` | Rows `2026/10/1` and `2026/10/13`, column `10Y` |
| JGB 3.057% on 30 Sep 2026 | Not re-read | — | The history file's fetch stopped in 1979; the current file starts 1 Oct | `jgbcme_all.csv` starts `1974/9/24` | — |

The 30 weekly changes, in basis points, order US nominal, US real, Bund, from the week ending 9 Jan through 31 Jul: −1/−4/−4, +6/+1/−3, 0/+1/+7, +2/−2/−4, −4/−2/−2, −18/−11/−5, +4/+3/−4, −11/−8/−5, +18/+8/+15, +13/+12/+10, +11/+9/+5, +5/+12/+12, −9/−14/−8, −4/−4/+1, −5/−5/0, +5/−1/0, +8/+2/+7, −1/+2/−10, +21/+17/+11, −3/+6/−5, −11/−9/−10, +10/+12/+7, −7/−2/−4, −2/+4/−2, −8/−3/−11, +11/+8/+8, +7/+6/+11, −1/−1/+6, +14/+12/+5, +6/+4/−3.

Holiday weeks use the last print inside the week: Bund 2 Apr (Good Friday) and 30 Apr (1 May), US 18 Jun (Juneteenth) and 2 Jul (Independence Day). Sample standard deviations of those weekly changes are about 9.2bp (US nominal), 7.5bp (US real) and 7.3bp (Bund).

### WHAT IT CHANGES

It does not change the programme state. The US split of +113bp into real +96bp and breakeven +17bp, from 29 Dec 2023 to 18 Sep 2026, re-derives from the Treasury files. The new number is descriptive comovement only: in January–July 2026 the US 10-year and the Bund Svensson 10-year had a weekly-change correlation of 0.76, while the US level rose 56bp and the Bund 25bp. That does not move the unsettled term-premium split into a global-factor frame, and it does not retire the separate US and Japan/Germany accounts. Japan, the UK, the rest of 2024–26, and break dates are missing. Nothing here is a cause of a yield move.

### BUILD SPEC

Script `bin/r15_yield_comovement.py`. Runtime about 1–3 minutes if the UK zip is downloaded once and cached; the JGB history file must be streamed, not loaded through a truncated reader.

Inputs:

- US par, by year: `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{year}/all?type=daily_treasury_yield_curve&field_tdr_date_value={year}&page&_format=csv` for 2018, 2019, 2022, 2023, 2024, 2025, 2026. Column `10 Yr`.
- US real, same path with `type=daily_treasury_real_yield_curve`. Column `10 YR`.
- Bund: `StatisticDownload` with `tsId=BBSIS.D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A`, `its_csvFormat=en`, full span 2018-01-01 to today. The REST path returned HTTP 500 on 14 Oct 2026; try it again and do not silently prefer it.
- JGB: `https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv` plus `.../jgbcme.csv`. Column `10Y`. Percent, semiannual constant maturity.
- UK nominal and real: archive zips linked from `https://www.bankofengland.co.uk/statistics/yield-curves` (nominal daily listed at 39.2MB, real daily at 25.1MB), plus the latest-month zip once its href is read from that page. Use the 10-year spot column. `.../latest-yield-curve-data.zip` returned HTTP 500 in this session.
- ECB AAA, robustness only, not as the Bund: `https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y?format=csvdata&detail=dataonly&startPeriod=2018-01-01`.

Outputs:

- `data/r15/weekly_panel.csv`: `week_ending`, `obs_date_*`, `us_nom`, `us_real`, `us_bei`, `bund_nom`, `jgb_nom`, `gilt_nom`, `gilt_real`.
- `data/r15/factor_shares.csv`: `window`, `series_set`, `n`, `rho_*`, `lambda1_corr`, `share_corr`, `lambda1_cov`, `share_cov`.
- `data/r15/bai_perron.csv`: `country`, `break_date`, `ci_low`, `ci_high`.

Assert: US 29 Dec 2023 10-year equals 3.88 and real equals 1.72; US 18 Sep 2026 equals 5.01 and 2.68; JGB 13 Oct 2026 `10Y` equals 3.019; Bund file's last date is within five business days of the run, otherwise write the lag and do not treat October as missing data; each week uses one observation per market; a week is dropped if any series in the set is missing; correlation-matrix eigenvalues sum to the number of series within 1e-8; Bai-Perron on the weekly level, trimming 15%, at most three breaks, 95% intervals. Windows are 2018–19, 2022–23 and 2024 through the latest common week. Report correlation-matrix and covariance-matrix shares separately. Do not regress yields on flows.

### UNCERTAIN

The Bund CSV header says percent and does not state compounding. The US series is a semiannual par yield; the ECB AAA series is a continuously compounded spot. Weekly changes were not converted. Holiday weeks were paired by calendar week, not by the same timestamp. The sums above were added by hand from the fetched rows; an error of about 20 in a cross-product would move a correlation by about 0.01. The Bundesbank file ending on 3 Aug 2026 may be a stale download channel rather than the end of the series. The 3.66% and 3.49% Bund prints for 1–2 Oct, and the JGB 3.057% for 30 Sep, were not in the rows retrieved. Whether the gilt spreadsheet may be redistributed is not settled by the Database's Open Government Licence line, because the yield-curve page points at the general website terms and names Bloomberg and Tradeweb as inputs.

### NOT DONE

Four-country first-factor shares for 2018–19, 2022–23 and the whole of 2024–26. Japan could not be included: the history file was truncated at 1979 and the current file is October only, which is too short for a weekly correlation. The UK zip was not read (HTTP 500 on the latest-month URL; the archive xlsx was not opened). Bai-Perron break dates and their intervals were not computed. The cumulative common-component split of the +113bp, +243bp and +156bp level moves was not computed. German, UK and Japanese real-yield weekly series were not added. The Bundesbank REST API returned HTTP 500.
