# Grok batch g8, 19 Oct 2026: scoping for the next builds and one pre-registration

Five parcels through orchestrator_cursor (Grok 4.7, fenced read + web). All SUCCESS: no breaches, nothing blocked, guard equal. **Input, not result.**

## Supervisor check

- **Parcel 1:** September 2026 was already published (8 Oct), so the forecast is for October (10 Nov). All 24 monthly base rates, the median (-¥78.2bn) and the band (-¥288.6bn to +¥74.6bn) re-derived from monthb3.csv by the supervisor; registered in CALENDAR.tsv (row 2026-11-10).
- **Parcel 2:** N-CEN design accepted as scoping for the test-B spec; field names to be checked on one zip by the builder.
- **Parcel 3:** confirmed by the supervisor's own HMRC API sums for 2024 (71081310: China 382,786 kg, Switzerland 305,087 kg, Hong Kong 26,044 kg; 71081200: China 0). The gold build is revised (CALENDAR row 2026-10-27).
- **Parcel 4:** confirmed: the author is Jouchi Nakajima; the GitHub copy of yield_M.csv re-read (Dec 2023 TP -0.0583, ER 0.7444; Sep 2026 TP 1.1768, ER 1.8154; TP share 0.54). CALENDAR row 2026-11-03 corrected.
- **Parcel 5:** X2 confirmed against the live H.8 release: Table 11 (foreign-related institutions, not seasonally adjusted) net due to related foreign offices about $810-930bn in recent weeks, positive = owed to related foreign offices; the negative figures are domestically chartered banks. X3 and X6 codes recorded for their specs; X6 values not yet re-read.

## Grok return 1: Japanese life insurers: source facts, base rates, October pre-registration

I'll start from the three local files, then pull the Ministry of Finance series and the insurers' own fiscal-2026 statements before writing the forecast.The local row points at the Ministry of Finance monthly file and treats Green’s life-insurer claim as unsourced. I’ll fetch that series, its notes, and the insurers’ own fiscal-2026 plans.The CSV is readable and already contains September 2026. I’ll confirm the release calendar, revision rules, Bank of Japan dates, and the insurers’ own fiscal-2026 plans before treating any month as still unpublished.September 2026 is already in the Ministry of Finance file. The pre-registered forecast below is for the next unpublished month, October 2026.

## SOURCE FACTS

The file is [monthb3.csv](https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/monthb3.csv), final update 8 October 2026. WebFetch returned it as text. Japanese headers were garbled (CP932). English headers and every figure were readable.

**Life insurance companies** are one block of three columns — Acquisition, Disposition, Net — after Financial Instruments Firms and before Non-Life Insurance Companies. September 2026 reads 5,487 / 8,374 / −2,886. Those three columns, plus the trust-bank trust accounts, financial-instruments firms, non-life, and investment-trust blocks, add to Other Financial Corporations. **Unit:** “100 mil Yen” (¥100 million). **First month in the file:** January 2005. The [index](https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/index.htm) says publication starts in January 2005 and is not continuous with the pre-2005 statistic.

**Sign,** from [data.htm](https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/data.htm): from January 2014 transactions, plus is net acquisition and minus is net disposition. All figures below use that sign. **“Long-term debt”** in the [glossary](https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/terms.html) is original maturity over one year, including yen-denominated foreign bonds. Classification is by the issuer’s residence. The reporters are designated institutions, a narrower set than balance-of-payments securities investment, which the index says is published the month after next.

**Release,** from the [schedule](https://www.mof.go.jp/english/policy/international_policy/reference/itn_transactions_in_securities/schedule.htm), 08:50 Japan time, “subject to change”:

- September 2026: **8 October 2026**. data.htm confirms “令和8年9月中” was released that day. October–December 2026 rows in the CSV are blank.
- October 2026: **10 November 2026**.

**Revisions:** the index’s errata line is “現在、公表している情報はありません。” No routine rewrite calendar for this file was on the pages fetched. Balance-of-payments securities investment, a different series, is marked preliminary and revised, including an annual revision in early April ([bppi.htm](https://www.mof.go.jp/policy/international_policy/reference/balance_of_payments/bppi.htm)).

**Bank of Japan call-rate decisions fetched:** 19 March 2024, negative rates and yield-curve control ended, “around 0 to 0.1 percent” ([statement](https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2024/k240319a.pdf)); 31 July 2024, “around 0.25 percent” ([statement](https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2024/k240731a.pdf)); 24 January 2025, “around 0.5 percent”; 19 December 2025, “around 0.75 percent”; 16 June 2026, “around 1.0 percent”; 18 September 2026, “around 1.25 percent,” effective 24 September ([statement](https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2026/k260918a.pdf)).

## BASE RATES

Life insurers’ net purchases of foreign long-term debt. Plus means net acquisition. ¥ billion = file units ÷ 10.

**Last 24 months**

| Month | Net | Month | Net |
|---|---:|---|---:|
| Oct 2024 | +74.6 | Oct 2025 | −38.5 |
| Nov 2024 | −197.0 | Nov 2025 | −64.9 |
| Dec 2024 | −196.4 | Dec 2025 † | −254.3 |
| Jan 2025 * | −212.8 | Jan 2026 | +40.2 |
| Feb 2025 | −216.3 | Feb 2026 | −618.7 |
| Mar 2025 | −250.1 | Mar 2026 | −638.4 |
| Apr 2025 | −76.2 | Apr 2026 | −80.2 |
| May 2025 | +530.9 | May 2026 | +17.9 |
| Jun 2025 | −4.6 | Jun 2026 ‡ | −41.3 |
| Jul 2025 | −199.3 | Jul 2026 | −10.6 |
| Aug 2025 | +80.9 | Aug 2026 | −137.3 |
| Sep 2025 | +32.6 | Sep 2026 § | −288.6 |

\* 24 Jan 2025 hike to ~0.5%. † 19 Dec 2025 hike to ~0.75%. ‡ 16 Jun 2026 hike to ~1.0%. § 18 Sep 2026 hike to ~1.25%, effective 24 Sep, so most of September was still at ~1.0%. The March 2024 and July 2024 decisions sit before this window.

Sum of these 24 months: −¥2,748.4 billion. Median −¥78.2 billion. Nineteen months are net sales.

**Calendar-year nets, ¥ trillion**

| 2019 | 2020 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026 Jan–Sep |
|---:|---:|---:|---:|---:|---:|---:|---:|
| +2.692 | −1.855 | −0.754 | −11.464 | −2.848 | −1.678 | −0.673 | −1.757 |

The largest net-sales year in this window is 2022, before the March 2024 end of negative rates. Full-year 2024 and 2025 were smaller net sales. 2026 through September is already a larger net sale than either of those full years, mostly February (−¥618.7 billion) and March (−¥638.4 billion).

**July–September quarters, ¥ billion:** 2019 +234.3; 2020 −914.5; 2021 +543.4; 2022 −3,731.9; 2023 −5.2; 2024 −974.9; 2025 −85.8; **2026 −436.5** (July −10.6, August −137.3, September −288.6).

## INSURERS' STATED PLANS

No Life Insurance Association fiscal-2026 foreign-bond plan turned up on the pages fetched. Plans are company briefings. They are holdings plans, and they split hedged from open. The MoF column does neither.

- **Nippon Life, June 2026 slides** ([ir202606.pdf](https://www.nissay.co.jp/assets/kaisha/gyoseki/document/ir202606.pdf)): fiscal-2026 policy column is ヘッジ外債「増加」 and オープン外債「減少」. The text says it will add “投資妙味のあるヘッジ外債”.
- **Dai-ichi Life, 15 May 2026** ([results PDF](https://www.dai-ichi-life.co.jp/company/results/kessan/2025/pdf/index_001.pdf)): “為替オープン外債は、リスク許容度や為替動向を踏まえて、残高を削減する方針です。” Hedged foreign bonds: balance “維持”.
- **Daiwa compilation, 28 April 2026** ([memorandum](https://www.uk.daiwacm.com/media/294245/28apr26dm.pdf)), “various media reports,” ten majors: “Life insurers remain cautious about accumulating foreign bonds.” On unhedged bonds, “none plan to increase them.” Its table has Nippon unhedged as flat. Nippon’s own June slides say decrease. Daiwa’s Sumitomo row is hedged increase, unhedged decrease. That cell is Daiwa’s, not a company document fetched here.
- **Fukoku, second half, interview 15 October, story 16 October** ([reprint](https://news.infoseek.co.jp/article/16reutersJAPAN_KBN3VW0O9/)): foreign-currency bonds down ¥25 billion for the year; hedged book “残高ゼロを維持”; “オープン外債は引き続き減少”.

## PREDICTION

**September 2026 and July–September 2026 cannot be pre-registered.** Both are already in the 8 October file. Writing a range for them now would be a back-fit. Observed September net is −¥288.6 billion (bought ¥548.7 billion, sold ¥837.4 billion). Observed Q3 is −¥436.5 billion. Among the eight July–September quarters since 2019, that sits inside the historical min–max and below the 2019–2025 median (−¥85.8 billion).

**October 2026, registered 19 October 2026, before the 10 November print.**

- **Rule.** Sort life-insurer monthly nets for October 2024–September 2026 (n=24). Point = median. Range = 3rd through 22nd order statistics (drop the two lowest and the two highest). Bounds are themselves historical months: September 2026 and October 2024.
- **Point:** −¥78.2 billion.
- **Range:** −¥288.6 billion to +¥74.6 billion.
- **FALSIFIED IF** the October 2026 life net in the next monthb3 vintage is below −¥288.6 billion or above +¥74.6 billion. A print equal to either bound is inside.
- **In:** the month looks like the recent central mass, modest net sales or a small net purchase. It does not show a new break beyond the last two years. It leaves Green’s “bid removed” claim where the project already has it: an unsourced claim. This flow has been net sales in most months since late 2024, and the heavy year was 2022.
- **Above** (more than +¥74.6 billion): net buying outside that central band. For that month it cuts against a vanished bid. May 2025 (+¥530.9 billion) shows a single month can do this without a new regime.
- **Below** (more than −¥288.6 billion of net sales): heavier disposal than every month in the last 24 except February and March 2026. That is a larger flow in the direction of an exit. It is still one month, all foreign long-term debt, and not a statement about any price.

October will be the first full month after the 24 September effective date of the 1.25 percent guideline. The rule does not use that fact. It is only the history.

## LIMITS

The column is residents’ contracts in non-residents’ long-term debt, all currencies together, acquisitions and disposals, designated reporters.

- **Currency, and US share.** Issuer residence mixes dollar bonds with yen bonds of foreign issuers. The US Treasury share is not in the file. MoF points currency and sovereign-by-country series to the Bank of Japan time-series site ([bppi.htm](https://www.mof.go.jp/policy/international_policy/reference/balance_of_payments/bppi.htm)). Those cuts are not life-insurer-only.
- **Hedged versus unhedged.** Absent here. Company slides split them, and they can offset inside one MoF net: Nippon plans to add hedged and cut open. The project’s hedge panel already has nine major Japanese life insurers at about 60 percent in 2021 and about 40 percent in 2024, a BIS reading of a Bank of Japan chart, with no single ratio.
- **Holdings versus flows.** This file is contracts. Stocks are in the Bank of Japan Flow of Funds, quarterly; 2026 Q2 was released 17 September 2026 ([page](https://www.boj.or.jp/en/statistics/sj/index.htm)). General-account balance sheets (Nippon’s June slides, Dai-ichi’s 15 May accounts) give each firm’s foreign-bond book.

Flows are described as flows. Nothing above is a claim that these purchases moved a yield.

## UNCERTAIN

- Whether 2005–2013 rows in this CSV were restated onto the post-2013 sign. The note covers transactions from January 2014. The 27 December 2013 methods notice would settle it. Annual totals here start in 2019, so the forecast does not use those rows.
- Whether the 10 November vintage rewrites months already in the 8 October file. Diff the two CSVs.
- Sumitomo’s hedged fiscal-2026 plan. Daiwa says increase. A company PDF was not fetched. Sumitomo’s own briefing would settle it.
- Whether the Flow of Funds workbook’s life-insurance subsector isolates foreign long-term debt. The index page lists the release. The September 2026 time-series workbook would settle it.
- The April Reuters roundup returned 401, so it is not quoted. Nippon’s June slides and Dai-ichi’s May PDF are the company texts used.

## Grok return 2: N-CEN index flag joined to N-PORT (test B)

I'll start from the three local notes, then pull the SEC N-CEN bulk-file specs and the bond-fund literature those notes need.The local notes set the absorption figures and name N-CEN as the index flag. Next I’ll read the SEC bulk-file pages and the bond-index papers those figures need.The N-CEN dictionary is in hand. I’ll confirm the form’s index item and filing lag, the N-PORT join keys, and two or three sources on passive bond demand.The queued test splits registered funds’ 2026 first-half Treasury duration absorption into index and active funds. On the measured arm that absorption is **$162.1bn** of 10-year equivalents, **29.2%** of the public’s addition that half, against a **14.5%** starting stock share. The index flag is annual and does not name the index.

## SOURCE FACTS

Bulk files are the quarterly zips on the SEC Form N-CEN data sets page, **2018 Q3 through 2026 Q3** (page header: September 2018–September 2026). The dictionary is the N-CEN readme. Filings are XML, published as tab-delimited tables. The page says filings in EDGAR schema **3.1** are omitted for now.

The report itself is annual (rule 30a-1): within **75 days** of fiscal year-end, or of calendar year-end for unit investment trusts, with a **12b-25** extension of up to **15 days**. The zip is quarterly. A filing after **5:30 p.m. Eastern** on the quarter’s last business day waits for the next zip. `SUBMISSION` holds `N-CEN`, `N-CEN/A`, and the `NT` notices. `REPORT_ENDING_PERIOD` is Item A.1.a. `FILING_DATE` is the EDGAR date.

Index flag, in `FUND_REPORTED_INFO` (Parts C and D):

- `IS_INDEX` = `Y` if Item C.3.b fund type is “Index Fund.” The form’s definition is a fund, including an ETF, that seeks to track a specified index. Types are “check all that apply,” so `IS_INDEX` can be `Y` together with `IS_ETF`, `IS_FUND_OF_FUND`, or `IS_MASTER_FEEDER`.
- The form does not ask for the index’s name. Related fields are `IS_INDEX_AFFILIATED`, `IS_INDEX_EXCLUSIVE`, and the four tracking-difference fields (`RETURN_*`, `STDV_*`, Items C.3.b.ii–iii).
- `IS_MULTI_INVERSE_INDEX` is a separate type (Item C.3.c). `IS_FUND_TYPE_NA` is `Y` when fund type is N/A.

Join keys, fund grain first:

| Key | N-CEN | N-PORT |
|---|---|---|
| Series ID | `FUND_REPORTED_INFO.SERIES_ID` (C.1.b), key with accession | `FUND_REPORTED_INFO.SERIES_ID` (A.2.b) |
| Series LEI | `FUND_REPORTED_INFO.LEI` (C.1.c), nullable | `SERIES_LEI` (A.2.c), nullable |
| CIK | `SUBMISSION.CIK` and `REGISTRANT.CIK` (B.1.c), registrant | `REGISTRANT.CIK` (A.1.c) |
| Registrant LEI | `REGISTRANT.LEI` (B.1.d), nullable | `REGISTRANT.LEI` (A.1.d), nullable |
| Class ID | `SHARES_OUTSTANDING.CLASS_ID` (C.2.d.ii) | `MONTHLY_TOTAL_RETURN.CLASS_ID` only |

Holdings live on `FUND_REPORTED_HOLDING`, keyed by accession and `HOLDING_ID`, with no class id. `FUND_ID` is accession plus CIK plus series and changes every filing. N-PORT `DESIGNATED_INDEX_NAME` is the Relative VaR index (Item B.10.b), not the tracking index.

N-PORT sets run October 2019–September 2026. The readme says filings are disseminated quarterly and the data-sets page keeps only disseminated public holdings. The futures scoping states that the public file is the third month of the fund’s fiscal quarter; that form sentence was not re-fetched here.

## CLASSIFICATION RULES

Assign the flag from the latest `N-CEN` or `N-CEN/A` whose `REPORT_ENDING_PERIOD` is on or before the N-PORT `REPORT_DATE`, taking the latest `FILING_DATE` for that period. Ignore `NT` rows. An amendment restates the whole form.

- `IS_INDEX` = `Y`, and `IS_MULTI_INVERSE_INDEX` not `Y`: index arm. Levered or inverse funds are a side line.
- A Part C row with `IS_INDEX` null: not an index fund. The readme defines the field as `Y` when that type is checked.
- `IS_FUND_TYPE_NA` = `Y` with no other type flag, or `N/A` sitting beside a type flag: unclassified.
- No `FUND_REPORTED_INFO` row (unit-investment-trust ETF, schema 3.1 gap, or not yet filed): unclassified. Do not fill from a filing dated after the position date in the primary test.
- A flag that flips between end-2023 and 30 June 2026: the primary share uses only series whose flag is the same at both dates. Print switchers beside it. A conversion moves the whole stock into the new bucket’s change, which is a reclassification, not new buying.
- ETF versus mutual fund is a cross-tab of `IS_ETF` and `IS_INDEX`, not a substitute for the index test. `IS_ETMF` stays separate. Interval funds stay in the index test via `IS_INTERVAL` and still answer Item C.3. Closed-end funds also complete Part C. Item C.3.a is checked if the series offers an ETF class, so one series can mix an ETF class and a mutual-fund class; those series stay in the index test and leave the ETF contrast.
- Drop `IS_MONEY_MARKET` = `Y`, matching the R2b exclusion.
- Keep a fund-of-funds’ own Treasury lines. The instruction defines a fund of funds as holding other investment-company securities above section 12(d)(1)(A), and it carves out holdings that exist only under rule 12d1-1. Drop a feeder’s Treasury lines when `FEEDER_FUNDS.REGISTERED_SERIES_ID` or `MASTER_FUNDS` points at a master that is in the same N-PORT window. `IS_UNDERLYING_FUND` stays in; it marks a variable-annuity underlying fund.
- Join holdings on `SERIES_ID`. Leave `CLASS_ID` off that join.

## LITERATURE

Treasury Borrowing Advisory Committee, “Trends in demand for US Treasury securities,” February 2026, https://home.treasury.gov/system/files/221/TBACCharge2Q12026.pdf. “Treasuries are now 46% of the Bloomberg US Aggregate Index.” The same slide says “Higher index weightings generates increased marginal demand for US Treasuries,” tied to indexed-bond-fund assets from ICI. That is the committee’s description of index weights. It is not a holding-level Treasury measurement, and it is not a yield result.

Sushko and Turner, “The implications of passive investing for securities markets,” BIS Quarterly Review, 11 March 2018, https://www.bis.org/publ/qtrpdf/r_qt1803j.htm. “passive bond funds has risen to almost 5% of the US bond market” as of June 2017, for the whole US bond market. On behavior: “requires no trading in the absence of changes in index composition.” They also treat closet indexing as common in bond funds, and they find index-mutual-fund flows steadier than ETF flows in the stress windows they plot. Their price regressions are their claims; this test does not use them.

Kashyap, Kovrijnykh, Li, and Pavlova, “The Benchmark Inclusion Subsidy,” NBER Working Paper 25337 (2018); Journal of Financial Economics 142 (2021), https://www.nber.org/papers/w25337. “Benchmarking generates additional, inelastic demand for assets inside the benchmark.” The page states a general benchmarking model. It does not report a Treasury or Aggregate holdings share.

## DECISION RULE

One comparison, set before the split is built. Use the R2b measured arm only: cash Treasuries, fixed end-2023 curve, same lag and windows. Let `q` be index-fund 2026H1 10-year equivalents divided by classified funds’ 2026H1 change. Let `s0` be those index funds’ share of the end-2023 registered-fund stock. Unclassified series stay out of `q` and are reported. The base is **$162.1bn**. This is a holder split. It is not a cause of yields, and it is not a share of the public’s **$3,218.3bn**.

The 15-point bar matches the measured 2026 first-half excess of funds over their own stock share: **29.2 − 14.5 = 14.7** points, rounded to 15. The 10-point rise is judged against 2024 (`q` on **$203.2bn**) and 2025 (`q` on **$184.0bn**).

- **Supports** the queued claim (a much larger marginal share, and a rising one) only if, on the stable-flag sample, `q` ≥ **60%**, `q − s0` ≥ **15** points, and 2026H1 `q` is at least **10** points above both 2024 and 2025. With unclassified change near zero, 60% is at least **$97.3bn** of the **$162.1bn**.
- **Against** if stable-flag `q` ≤ **40%** and `q − s0` ≤ **0**, and the anchors below pass. Index funds then take at most about **$64.8bn** of the half-year and do not exceed their stock share.
- **Inconclusive** otherwise. That includes a large but flat `q` (the level and the rise disagree), `|unclassified change|` above **$16.2bn** (10% of $162.1bn), stable-flag `q` and all-series `q` differing by more than **10** points, `IS_INDEX_EXCLUSIVE` = `Y` accounting for more than half of `q − s0`, or the 15-point gap appearing only among `IS_ETF` = `Y` while index mutual funds’ own excess is under **5** points. Moving levered or inverse funds into the index arm also makes the result inconclusive if that move crosses 60% or 40%.

The Z.1-scaled arm is not a second test. R2b already records that the ETF scaler is government-bond ETF assets by objective, not Treasuries split by an index flag. Futures stay out of this object.

## PITFALLS

Active funds that hug the Aggregate are coded active. Anadu, Kruttli, McCabe, and Osambela, FEDS 2018-060r1, https://www.federalreserve.gov/econres/feds/files/2018060r1pap.pdf, write that “some nominally active investment funds behave passively,” and that “active decisions are needed to implement some indexing strategies, particularly for bonds.” N-CEN’s tracking-error fields are filled only when `IS_INDEX` is `Y`, so closet indexers lower `q`. As of March 2020 they put passive funds at 30% of bond-fund assets, using Morningstar. That is an asset share through 2020, not a 2026 Treasury-duration share.

A higher index share can be ETF growth. `IS_ETF` and `IS_INDEX` are separate boxes, and most ETFs are index funds. BIS find ETF flows more volatile than index-mutual-fund flows, so the two are different holders. The inconclusive clause above is the guard.

N-PORT’s public file is one disseminated month per fiscal quarter, not a 30 June position for every fund. Rebalancing between public months is invisible. The **$162.1bn** already uses that month. The index flag is annual and can lag the position by 75 days plus 15, and then by up to a quarter in the zip, so the flag on a June 2026 holding often describes an earlier fiscal year.

`IS_INDEX` is any specified index. It is silent on the Aggregate, on market-cap weights, and on whether the fund is a bond fund. Equity index funds, custom exclusive indexes, and Treasury-bill indexes all qualify.

## UNCERTAIN

- Whether a blank `IS_INDEX` is stored as null or as `N`. A value count on one zip would settle it. The readme only defines `Y`.
- The codes inside `INVESTMENT_COMPANY_TYPE` (Item B.6). The readme does not list them.
- How many 2025–26 filings the schema 3.1 omission removes, and the date EDGAR 25.2 began. The data-sets page states the omission and not the count.
- Whether unit-investment-trust ETFs, which file Parts E and F and not Part C, appear in the R2b N-PORT universe with no `IS_INDEX`. A match of those series to `FUND_REPORTED_INFO` would settle it.
- No bulk field names the tracked index. `DESIGNATED_INDEX_NAME` is the VaR index. A prospectus text field is outside these zips.
- How often `IS_ETF` is `Y` because only one class is an ETF. A class-level ticker check would settle the size of that mislabel.
- Whether a variable-annuity separate account and its `IS_UNDERLYING_FUND` both report the same Treasury lines. An overlap of series in one zip would settle it.
- `s0` is not in the R2b note. The 15-point test needs it from this build.
- The BIS “almost 5%” figure is June 2017 and all US bonds, and they treat nearly all ETFs as passive. The Kashyap page does not measure Treasuries.

## Grok return 3: Gold trade cap design check (HMRC OTS)

I'll read the planned build and the earlier gold-bound design, then check HMRC's trade API and the public mirror sources against that design.The design names HMRC’s open trade API and a China–Hong Kong gold-export cap. I’ll confirm the live fields and the official gold treatment, then check Swiss, Hong Kong and China mirrors.The China call returned no rows, so I’ll check whether the codes and partners are live, and pull the official gold notes and mirror series.**VERDICT.** Do not build the cap as written. On the live HMRC API, 2024 non-EU exports of CN8 `71081200` are 3,083 kg in total: Switzerland 3,000 kg, Hong Kong 17 kg, and China does not appear. The gold-bar mass is in `71081310`: 852,567 kg of non-EU exports, of which China 382,786 kg, Switzerland 305,087 kg and Hong Kong 26,044 kg. A China–Hong Kong ceiling on `7108.12` cannot bound unreported official buying. A ceiling on `71081310` is wide enough to sit in the same range as the whole World Gold Council residual, and it still does not name the buyer.

**SOURCE FACTS.** The API is the current Overseas Trade Statistics service, not a successor. Base `https://api.uktradeinfo.com`. Trade rows: `GET /OTS`, OData, no Authorisation header. Confirmed fields: `Commodity/Cn8Code`, `Country/CountryCodeAlpha` (China `CN`, Hong Kong `HK`, Switzerland `CH`), `FlowTypeId`, `NetMass`, `Value`, `MonthId`, `SuppressionIndex`. `FlowTypeId` 4 is non-EU exports. Net mass is kilograms: “which will be in kilograms (kg).” `Value` is the sterling value field in HMRC’s own samples. Pagination is 40,000 rows. “Rate-limited to 60 requests per minute.” Terms: “published under the Open Government Licence.” The fetched terms text does not print “v3”.

Live codes: `71081100` powder; `71081200` unwrought non-monetary, excluding powder; `71081310` bars, rods, wire and sections; `71081380` other semi-manufactured; `71082000` monetary gold. A June 2024 non-EU `71081200` row returned `SuppressionIndex` 0, `NetMass` 9, partner Singapore. June 2024 `71082000` returned `@odata.count` 0.

Prepared tables “go back to the year 2000.” Non-monetary gold is in the published series from January 2005. Publication “typically occurs 6 to 8 weeks after the reference month.” The calendar sets UK overseas trade in goods statistics for September 2026 on 12 November 2026. Figures stay provisional for up to 18 months. The minimum `MonthId` query timed out.

**TREATMENT OF MONETARY GOLD.** HMRC’s annex, updated 9 December 2025: monetary gold “is not included in the published OTS,” while “non-monetary gold is included in the published OTS” from January 2005. The 12 March 2014 note says the same and lists `7108 1200`, `7108 1310` and `7108 1380` inside non-monetary gold. The exclusions list names “Monetary gold.”

The Bank of England says customers trade bars in its vaults and “the name of the owner will change,” without moving the bar. ONS, revised 16 January 2026: HMRC OTS records “goods physically entering or leaving the UK,” while ONS uses a Bank of England survey of change of ownership and drops the HMRC precious-metals rows from its headline figures to avoid double counting. ONS defines non-monetary gold as “gold bullion not owned by central banks.” A foreign central bank that only changes the name on a London bar is outside this cap.

The 2016 change that the pages do document is the recording system, not a new gold code. From May 2016, non-EU statistics moved “from the general trade to the special trade system.” “Special trade excludes those goods placed in customs warehouses.” No fetched HMRC page changes the gold commodity list in 2017 or 2018.

**MIRROR DATA.** Switzerland is the useful mirror, as a separate ceiling. FOCBS records “customs tariff heading 7108.1200” for gold in raw form, monthly by country in SwissImpex from 2012. From 1 January 2021, imports only are split into mined gold (911) and refined gold (912/913 at or above 99.5 percent, 914 below). The open tariff-number files include `TN8 EXP`, monthly from 1988, about 4.7 GB. Terms: “You may use this dataset for non-commercial purposes.” Commercial use needs permission. World Bank WITS, drawing on UN Comtrade, shows 2024 Swiss exports of HS `710812`: world 1,432,310 kg, China 336,327 kg, Hong Kong 90,145 kg. That page labels the nomenclature “HS 1988/92 (H0)”.

Adding UK exports to Switzerland to Swiss exports to China counts the same metal twice and mixes `71081310` with `710812`. Set beside each other, the 2024 China legs are 382,786 kg (UK `71081310`) and 336,327 kg (Swiss `710812`). The planned UK `71081200` series does not contain that flow.

Hong Kong Census and Statistics Department keeps gold out of ordinary merchandise tables. Its explanatory note: tables other than “Trade in Gold and Specie” omit SITC Rev. 4 Division 97, “Gold, non-monetary,” and Division 98, “Gold, monetary.” Hong Kong uses the general system, so re-exports stay in total exports. Transit on a through bill of lading is excluded. A month includes declarations lodged up to the 14th of the next month. Partner is country of consignment. Trade-IDDS is on data.gov.hk, monthly, with a public API specification. A kilogram call was not completed here.

The English index of China Customs, through September 2026, lists aggregate and “major exports” releases and has no gold line on the page.

**PRIOR WORK.** World Gold Council, 29 January 2026: central banks and other institutions 1,092.4 tonnes in 2024 and 863.3 tonnes in 2025. “Unreported buying” is “57% of the annual total” in 2025, the gap between Metals Focus and reported data. Reported buyers include Poland, which “added a further 102t,” and the People’s Bank of China, whose “full year net purchases” were 27 tonnes, holdings “2,306t.” Swaps are excluded. The notes do not cite HMRC.

WGC, 15 January 2025, source SAFE: China “reported 44t of gold purchases” in 2024, holdings 2,280 tonnes. The same note, source China Customs, says November 2024 gold imports were “totalling 108t.” One customs month is already larger than that year’s reported central-bank addition. No fetched paper uses the HMRC OTS API as a central-bank buying series.

**DECISION RULE.** Fix this before 27 October.

1. Build two series, both in kilograms of `NetMass`, non-EU exports only (`FlowTypeId` 4): `71081310` and, beside it, `71081200` plus `71081380`. Partners: China and Hong Kong. Leave `71082000` out.
2. Keep a partner kilogram only when `SuppressionIndex` is 0. If the index withholds country or quantity, leave the month blank.
3. Read it as a ceiling on declared special-trade shipments. Official buying that used that declaration cannot exceed it. The ceiling does not identify the buyer.
4. Place the Swiss `7108.1200` export to the same partners next to it. Do not add UK-to-Switzerland to Swiss-to-China.
5. Ignore `Value` when the question is mass. Sterling values move when the gold price moves.
6. On 27 October the scheduled month in hand is August 2026. September is dated 12 November. Keep revising for 18 months.
7. A co-movement with the gold price is descriptive only.

Fail the build if the `71081310` China plus Hong Kong total is treated as unreported central-bank buying, or if `71081200` alone is treated as the London-bar cap.

**PITFALLS.** Since May 2016, gold that only enters or leaves a customs warehouse is outside OTS, and so is transit. Refining sends London bars to Switzerland to be recast; the UK row to Switzerland is an upstream leg. Vault book-entry never becomes a customs row. Declared destination is not the final holder. Hong Kong re-exports to the mainland sit in a separate general-trade series. `71081200` and `71081310` are different codes in the UK file, while Switzerland’s bar heading is `7108.1200`. Using `Value` as if it were tonnes misstates the mass.

**UNCERTAIN.** The API’s first month for these codes: the minimum-month call timed out. Whether any month of `71082000` is published beyond the empty June 2024 extract. The 2024 total for `71081380`, which was not pulled. That the Open Government Licence text is specifically v3. The WITS “H0” label on a 2024 extract. The HS code, kilogram unit and licence behind the China Customs series that WGC cites, because the customs workbook was not opened. Hong Kong’s kilogram unit and API rate limit, because no quantity call was returned. A separate HMRC gold-code revision in 2017 or 2018: none was on the pages fetched. What would settle these points is one `MonthId` minimum call, a 2024 `71081380` aggregate, the OGL deed linked from the terms page, an FOCBS SwissImpex export extract for `7108.1200`, the China Customs gold table, and one Trade-IDDS quantity call for SITC 97.

## Grok return 4: Japan term premium sources

I'll start from the three files in this folder, then follow public links for Nakajima's `yield_M.csv` and other free Japan term-premium series.The calendar names Tomoyuki Nakajima’s `yield_M.csv`, while the earlier hunt points at Jouchi Nakajima’s pages. I’ll open those pages and the Bank of Japan sources next.The file is on Jouchi Nakajima’s site, not a Tomoyuki Nakajima page. I’ll open that page, follow its download link, and check the Bank of Japan and other free series.The yield page names the file but the fetch dropped the download link. I’ll recover that link from the page, then read the Bank of Japan review and the other public series.The calendar’s “Tomoyuki Nakajima” is the wrong person. The file is Jouchi Nakajima’s. No Tomoyuki page linking `yield_M.csv` turned up. The Google Sites attachment address itself did not survive the page fetch, so the columns below are from the same-named file in his GitHub repository, whose last month matches the page.

## SOURCES

| Name | URL fetched | Data downloadable? | Sample | Frequency | Terms |
| --- | --- | --- | --- | --- | --- |
| Jouchi Nakajima, shadow rate, term premium, expected rates | Page: https://sites.google.com/site/jnakajimaweb/yield . Terms mirror: https://sites.google.com/view/jpmpdata/ . File read: https://raw.githubusercontent.com/jouchinakajima/program/main/yield_M.csv (listed by the repo contents API; README points at his program page) | Yes. Page names `yield_M.csv` and `yield_D.csv`. Sites href not recovered. GitHub copy was read | File: 199501–202609. Page: “1995/Jan. to 2026/Sep. (updated in 2026/Oct.)” | Monthly file. Daily file named, not read. “Updated every quarter.” | “Cite the below articles when using this dataset.” Papers named on the page: Ichiue and Ueno, BoJ WP 13-E-8 (2013); Nakajima, Hitotsubashi DP A.760 (2025). “not the official view of the Bank of Japan.” Japan’s Monetary Policy Database: “dataset use is at users' own risk.” “The past figures are subject to updates.” No open licence on the page or in the GitHub listing |
| BoJ Review 2026-E-10 (4 Aug 2026) | https://www.boj.or.jp/en/research/wps_rev/rev_2026/rev26e10.htm and https://www.boj.or.jp/en/research/wps_rev/rev_2026/data/rev26e10.pdf | No series. PDF only. Model stated as Imakubo and Nakajima (2015), not the public `yield_M` model | Chart 3: cumulative change from Aug 2024, “as of end-June 2026” | One chart, not a maintained file | Review notice only. No spreadsheet and no open licence on the landing page |
| BoJ Financial System Report, April 2026 | https://www.boj.or.jp/en/research/brp/fsr/fsr260421.htm | No term-premium file. Linked workbook is stress scenarios only. Data “as of end-March 2026” | Not a premium sample | Semiannual report | “credit the source” for non-commercial use; permission required for commercial copying |
| BoJ research-data page | https://www.boj.or.jp/en/research/research_data/index.htm | No term-premium workbook. CPI, output gap, trade, consumption only | — | — | Credit the source; commercial copying needs permission |
| Japan Macro Advisors, ACM-style JGB curve | https://takujiokubo.github.io/jma-data/jgb-yield-curve-main/ | Page says each chart’s data can be downloaded. CSV bytes were not read | History from 2002; 40-year from Nov 2007. Vintage October 2026, origin September 2026. Dotted from October 2026 is a projection | Monthly | “updated estimates are available for paid users upon request.” “Details of the yield curve model are proprietary.” Posted vintage is on an open page. Variant of Adrian, Crump and Moench (2013) with a Bauer–Rudebusch shifting long-run rate |
| Leo Krippner / LJKmfa government-yield decomposition, includes Japan | https://www.ljkmfa.com/visitors/ , https://www.ljkmfa.com/subscribe-trial/ , documentation https://www.ljkmfa.com/wp-content/uploads/2025/12/GlobalGovernmentRiskPremiums20251127FINAL.pdf | Visitors page lists “Yield curve decompositions” dated 29/09/2026. “All of the up-to-date results are now freely available.” Workbook href was stripped; the file was not opened | Documentation: government curves from 1995; Japan OIS from 6 Aug 2009. Maturities 2, 5, 10, 30 years | “histories are all available on a daily basis”; he aims to update at month-end | No licence statement on the pages read. Three-factor shadow/lower-bound model plus surveys (Krippner 2022). Government premium is fitted JGB yield minus the OIS expected-policy component |
| Xiaoxia Ye, Japan term-premium term structure | https://www.xiaoxiaye.me/Home/research/all_data_pages/term-premium/more-term-premium | Page says “click here to download”; href not recovered | “July 1986 to Jul 2022” | Daily, 1-year to 10-year | “All the data are in percentage.” No licence on the page. Ends before this window. Method: Ye, *Journal of Fixed Income* (2015) |

Bank of Japan Outlook reports, the BIS, and a Kim–Wright-style Japan file were not opened as downloadable series. The IMF 2026 Article IV PDF fetch timed out, so it is not quoted.

## WHAT THEY SAY

**Nakajima file, read, not a prose claim.** Units are not stated on the page. They are inferred as percentage points because `ExpectedRate-10Y` plus `TermPremium-10Y` is 2.99 in 202609, next to the project’s 10-year yield of 3.07. Header:

`YYYYMM, ShadowRate, TermPremium-2Y, TermPremium-5Y, TermPremium-7Y, TermPremium-10Y, TermPremium-15Y, TermPremium-20Y, ExpectedRate-2Y, ExpectedRate-5Y, ExpectedRate-7Y, ExpectedRate-10Y, ExpectedRate-15Y, ExpectedRate-20Y`

December 2023: 10-year term premium −0.06, expected rate 0.74, sum 0.69. September 2026: 1.18, 1.82, sum 2.99. Over 2023Q4–2026Q3 the sum rises 2.31 points, of which the term premium is 1.24 (54%) and the expected rate 1.07 (46%). From August 2024 to June 2026, the same file gives about 64% term premium (1.13 of 1.75).

**BoJ Review, August 2026, data end-June 2026, from summer 2024.** “both factors have contributed to roughly the same degree.” That is expected short rates and the term premium, on Imakubo and Nakajima (2015). Separately, the estimated purchase-reduction piece “has been about 25 basis points,” and the stock-effect piece is “modest, at around 10 basis points.” Those are reported regression contributions. This note does not treat holdings or flows as the cause of the price.

**JMA, October 2026 vintage, about 2022–2026, not the end-2023 window alone.** “the standard model puts the rise at +157bp against our +70bp.” As of mid-July 2026, “Our estimate reads 0.6% to 0.7%,” against about 1.2% in what they call a standard model. Nakajima’s July 2026 10-year term premium is 1.17, close to that 1.2% figure. That match is inferred, not something JMA states.

**Krippner, 27 November 2025.** Japan is one of five countries in the workbook. The “almost three percentage points” risk-premium line is a five-country composite since 2020/21, not a Japan 2023–26 share. Country charts were not transcribed. “apart from Japan” refers only to later policy-rate cuts offsetting the expected-policy component elsewhere.

**Breakeven.** No fetched source states inflation compensation’s share of this nominal rise. The project’s one-third to two-fifths breakeven range is a different cut: expected inflation can sit inside expected nominal short rates, and an inflation risk premium inside the term premium. Nakajima’s 1.07-point expected-rate rise is large enough to contain an 0.8–1.0-point breakeven rise. JMA’s warning that a fixed long-run rate pushes expected inflation into the term premium points the same way. Nothing read here contradicts the breakeven range.

## RECOMMENDATION

Use Jouchi Nakajima’s monthly `yield_M.csv` as the build series: `TermPremium-10Y` and `ExpectedRate-10Y`. Cite Ichiue and Ueno (2013) and Nakajima (2025). Keep the file local and gitignored. There is no open licence.

Do not treat the BoJ chart as a second series. It is a different model, a PDF, and it stops at June 2026. Use it only as a qualitative check. Use JMA, if the chart download opens without a login, as the ACM-style cross-check. Leave Krippner for a later pass once the Visitors workbook link is followed. Ye stops in July 2022.

The October 2026 vintage already runs through September 2026, so it covers 2023Q4–2026Q3 before 3 November. The page says updates are quarterly.

## DECISION RULE

Fix this before reading a later vintage. History is revised every quarter, so recompute from the file in hand. Do not hard-code the shares above.

1. Window: 202312 to 202609. If the file’s last month is earlier than 202609, stop and report the vintage. Do not extend past 202609 for this test.
2. Let the fitted 10-year change be the change in `ExpectedRate-10Y` plus `TermPremium-10Y`. Call these changes Δer and Δtp, and Δy = Δer + Δtp.
3. If Δy is under 0.25, do not classify.
4. Share s = Δtp / Δy. If s > 0.50, the larger part is the term premium. If s < 0.50, the larger part is the expected short rate. If s is from 0.40 to 0.60 inclusive, also flag “close to even.”
5. On the file read now, s = 0.54, so the rule says term premium is the larger part, and “close to even.” That does not fail the BoJ sentence, which is a different model and starts in summer 2024.
6. Optional cross-check, same months, only if JMA’s download is actually opened: if JMA’s 10-year term-premium change is under half of Nakajima’s Δtp, label Nakajima’s majority model-sensitive. Do not replace the breakeven result.
7. A contradiction of the project’s breakeven range requires a source that measures inflation compensation’s share of this same nominal rise and places it outside one-third to two-fifths. A term-premium share is not that test.

## UNCERTAIN

- The Sites href for `yield_M.csv` was not recovered (archive lookup timed out; the page fetch dropped the link). The GitHub file ends in 202609, which matches the page, but byte-identity with the Sites attachment was not proved. Opening the link on the yield page would settle it.
- Units, and the claim that the two 10-year columns sum to the fitted yield, are inferred. The page never says “percent.”
- `trtms.csv` in the same GitHub repo is not `yield_M`. Its 10-year column does not match `TermPremium-10Y`, and the file does not define itself. It was not used.
- Krippner’s Japan 10-year path for 2023–26 is in a workbook whose link was not recovered.
- JMA’s CSV was not read, so the +70bp line is the page’s 2022–26 statement, not a recomputed 202312–202609 change.
- The IMF Article IV PDF timed out. Outlook PDFs and any BIS Japan term-premium file were not fetched, so “none exists” is not established.
- Whether Nakajima posts another vintage before 3 November. The page says quarterly, and the latest stated update is October 2026.

## Grok return 5: CGFS 65 candidates X2, X3, X6: series and codes

I'll read the two project files first, then look up the exact series, codes, and methods for X2, X3, and X6.The reading treats X2, X3, and X6 as open free-data candidates. I’ll look up the Fed, SEC/OFR, and BIS identifiers and the papers that define how each series is read.The public identifiers are in view. Next I’ll open the Fed, SEC, OFR, and BIS pages that define the codes, the sign, and the breaks.X2, X3, and X6 measure dollar funding of non-US entities. They are positions. Nothing below is a claim that a flow or a position moved a price.

Assumption: X2 is the foreign-related H.8 line only. X6 “banks” means private plus public banks, and “other financial” means private plus public other financial institutions. Central banks stay separate.

## X2. Foreign banks’ US offices, net due to related foreign offices

**Question.** What is the net dollar position of foreign banks’ US branches and agencies against their own foreign offices, including the head office?

**SERIES AND CODES.** Board of Governors H.8 series, billions of dollars. The H.8 about page says these series are the Data Download Program and FRED downloads. Identifiers below are the ones FRED publishes for that release.

| Series ID | Frequency | Adjustment | Latest reading |
|---|---|---|---|
| `NDFFRIW027NBOG` | Weekly, Wednesday | Not seasonally adjusted | Week of 7 Oct 2026: **836.8600** |
| `NDFFRIW027SBOG` | Weekly, Wednesday | Seasonally adjusted | Same week: **869.1235** |
| `NDFFRIM027NBOG` | Monthly | Not seasonally adjusted | Sep 2026: **859.9365** |
| `NDFFRIM027SBOG` | Monthly | Seasonally adjusted | Sep 2026: **904.1937** |

Use the weekly not-seasonally-adjusted series. Monthly levels are pro rata averages of the weekly levels. Seasonally adjusted foreign-related figures are a residual of the other bank groups.

**DEFINITION AND SIGN.** Foreign-related institutions are US branches and agencies of foreign banks, plus Edge Act and agreement corporations. A positive value means the US office owes related foreign offices: a funding inflow to the US office from the head office and related offices. A negative value means the US office is funding those foreign offices. The item sits on the liability side even when negative. Foreign-owned US subsidiary banks sit in the domestically chartered aggregates. International banking facilities are treated as foreign offices, so they are outside the US panel and their positions with the branch fall inside this net.

**HISTORY AND BREAKS.** The FRED chart runs from 3 January 1973. Until October 1996 the foreign-related panel also included New York investment companies. The H.8 does not publish a percent change for this line because the level can be negative. Early seasonally adjusted levels can be negative because the seasonal factor is a residual.

**LITERATURE.** Goulding and Nolle, IFDP 1064 (2012), https://www.federalreserve.gov/pubs/ifdp/2012/1064/revision/ifdp1064r.htm — “a positive net due-to value represents a funding inflow to FBAs.”

**PITFALL.** One net number for every parent country and every related office. It misses dollar funding that never passes through the US branch, and it misses foreign-owned US subsidiary banks.

**SIZE.** Small.

## X3. US money funds’ lending to non-US banks

**Question.** How much dollar paper and repo do US money funds hold on non-US banks, by the bank’s parent country and by remaining tenor, including quarter-end months?

**SERIES AND CODES.** SEC Form N-MFP3, free EDGAR filings, flat file documented in https://www.sec.gov/files/nmfp_readme.pdf. Portfolio rows are `SCHPORTFOLIOSECURITIES`.

- Issuer: `NAMEOFISSUER` (Item C.1), `LEI` (C.4), `CUSIP_NUMBER` (C.3), `ISIN` (C.5.a), `CIK` (C.5.b), `RSSDID` (C.5.c).
- Instrument: `INVESTMENTCATEGORY` (C.6). Part D of the same readme names the categories, including financial-company commercial paper, certificates of deposit, non-negotiable time deposits, asset-backed commercial paper, and repurchase agreements.
- Maturity: `INVESTMENTMATURITYDATEWAM` (C.11), `INVESTMENTMATURITYDATEWAL` (C.12), `FINALLEGALINVESTMENTMATURITYDATE` (C.13).
- Amount: `EXCLUDINGVALUEOFANYSPONSORSUPP` (C.18.b).

There is no issuer-country field on that table. The country codes in the readme are for the accountant’s address.

N-MFP3 submissions began in 2024. The same data set carries legacy N-MFP, N-MFP1, and N-MFP2 back to November 2010. Holdings are as of the last business day of the month, so the quarter-end print is the March, June, September, and December report.

**OFR.** The Money Market Fund Monitor says its charts cover investments in different countries and that chart data are downloadable: https://www.financialresearch.gov/money-market-funds/. The Short-term Funding Monitor’s MMF mnemonic list has no series by issuer country. A metadata search for “country” returned an empty list. The named series that come closest are `MMF-MMF_RP_wFFI-M` (repo with foreign financial institutions), `MMF-MMF_RP_wDFI-M` (repo with US financial institutions), and `MMF-MMF_BRA_TOT-M` (bank-related assets): https://data.financialresearch.gov/v1/metadata/mnemonics?dataset=mmf.

The Fed’s EFA tables are a separate free country cut, from December 2010. Table 1 is by country. Table 2 is by country, fund type, instrument, and maturity. https://www.federalreserve.gov/releases/efa/efa-project-money-market-funds-investment-holdings-detail.htm — “The country labels represent the country of domicile of the security issuer.”

**DEFINITION AND SIGN.** A holding is an asset of the fund and a dollar liability of the issuer. Nationality is assigned outside the form, by the parent’s headquarters. Domicile is the legal issuer’s country.

**HISTORY AND BREAKS.** Public security-level history starts with November 2010 filings. The form version changes across N-MFP, N-MFP1, N-MFP2, and N-MFP3. The flat file stacks them; legacy-only columns end in `_L`.

**LITERATURE.** ICI, Form N-MFP FAQ (18 May 2015), https://www.ici.org/faqs/faq/mmfs/faqs_nmfp — “assigning a country and region based on the geographical location of the issuer’s parent.”

**PITFALL.** Parent nationality is built, not filed. `LEI` may be empty. A US subsidiary of a foreign bank, including a Treasury-repo counterparty, is a US legal issuer and a foreign parent. The Fed country tables use domicile. Month-end data show the quarter-end stock and miss any reversal inside the month.

**SIZE.** Medium.

## X6. BIS international debt securities, US dollar, by sector

**Question.** How large is dollar bond funding of non-US issuers, split by banks, other financials, non-financial corporations, and government, on a residence basis and on a parent-nationality basis?

**SERIES AND CODES.** Dataflow `BIS,WS_DEBT_SEC2_PUB,1.0` (international debt securities, BIS-compiled). API: `https://stats.bis.org/api/v1/data/BIS,WS_DEBT_SEC2_PUB,1.0/{key}`.

Key order, from the CSV header: `FREQ.ISSUER_RES.ISSUER_NAT.ISSUER_BUS_IMM.ISSUER_BUS_ULT.MARKET.ISSUE_TYPE.ISSUE_CUR_GROUP.ISSUE_CUR.ISSUE_OR_MAT.ISSUE_RE_MAT.ISSUE_RATE.ISSUE_RISK.ISSUE_COL.MEASURE`.

For these stocks: `Q` quarterly; `3P` all countries; sector code or `1` for all; ultimate sector `1` when the sector is the immediate issuer; `C` international markets; `A` all issue types, currency groups, maturities, rates, risk, and collateral; `USD`; `I` amounts outstanding. Unit multiplier 6 means millions of dollars. Face value.

Portal titles name the sector inside a fixed “excluding residents of …” sentence. Code `J` in that sentence is “non-financial corporations,” which matches the FRED source code `Q:3P:3P:J:1:C:A:A:TO1:…` for residence of non-financial issuers.

Immediate-issuer sector (`ISSUER_BUS_IMM`), all countries, USD, 2026-Q2, millions of dollars:

| Code | Portal sector name | Value |
|---|---|---|
| `1` | All issuers | 16,274,316 |
| `E` | Private banks | 3,571,393 |
| `I` | Public banks | 171,670 |
| `7` | Central bank | 27,716 |
| `G` | Private other financial institutions | 6,931,679 |
| `K` | Public other financial institutions | 626,109 |
| `B` | Financial corporations (`E+I+7+G+K`) | 11,328,567 |
| `J` | Non-financial corporations | 2,220,789 |
| `2` | General government | 1,870,266 |
| `S` | International institutions | 854,694 |

`E+I+7+G+K+J+2+S` equals the all-issuer total. Banks for this project are `E+I` (3,743,063). Other financials are `G+K` (7,557,788).

Example key `Q.3P.3P.1.1.C.A.A.USD.A.A.A.A.A.I`: all issuers, all countries, USD, amounts outstanding, **16,274,316 million dollars in 2026-Q2**. The same key with `US` in the nationality slot, `Q.3P.US.1.1.C.A.A.USD.A.A.A.A.A.I`, is **4,849,552**. The arithmetic remainder, 11,424,764, is every nationality in that total other than US.

Residence uses `ISSUER_RES` and the sector in `ISSUER_BUS_IMM`, with `ISSUER_BUS_ULT=1`. Parent nationality uses `ISSUER_NAT`. The FRED residence series puts the sector in the immediate-sector position.

**DEFINITION AND SIGN.** Stocks at face value, not holdings. The BIS defines these securities as “issued outside the local market of the country where the borrower resides,” and classifies a security as international if registration, governing law, or listing differs from the immediate issuer’s residence, with foreign currency as a further criterion. “The nationality of the issuer is the country where the issuer’s parent is headquartered.” https://data.bis.org/topics/IDS

**HISTORY AND BREAKS.** The FRED all-currency non-financial series runs from 1966. The first date of these USD sector keys was not read. The latest row’s pre-break field is empty. The portal points to the June 2021 Quarterly Review box for the international-versus-domestic rule.

**LITERATURE.** FRED notes on the BIS non-financial series, https://fred.stlouisfed.org/series/IDSNFAMRIAO3P — “the BIS bases the nationality of an issuer on the residency of its controlling parent.”

**PITFALL.** `3P` includes US parents ($4.850 trillion of the $16.274 trillion). A local-market dollar bond can fall outside this international set. Nationality moves a Cayman or US vehicle to the parent’s country. These issuer stocks overlap the project’s existing BIS global-liquidity securities totals if both are added.

**SIZE.** Small.

## UNCERTAIN

- The Data Download Program CSV “Series ID” cell was not opened. The four `NDFFRI*` codes are the Board identifiers on FRED. Opening one H.8 DDP CSV would settle the token.
- No fetched note shows a 2010s level break in the foreign-related net-due series. A 2019 Call Report change about equity in foreign subsidiaries, if it exists, belongs to domestically chartered banks (FFIEC 031), not this foreign-related line. The March 2019 FFIEC 031 instructions and the H.8 notes archive would settle it.
- The first quarter of the USD sector keys was not read. `startPeriod=1960` on `Q.3P.3P.1.1.C.A.A.USD.A.A.A.A.A.I` would settle it. Any level shift from the 2021 international-bond rule was not quantified.
- The portal’s English title also says “all currencies, US Dollar” because the currency-group dimension is `A` and the currency is `USD`. The USD non-financial stock ($2.221 trillion) is well below FRED’s all-currency non-financial stock (code `TO1`, $4.859 trillion in 2026-Q1), which is the check that `ISSUE_CUR=USD` is the dollar denomination. The codelist label for currency-group `A` would close it.
- A published BIS “banks” line might equal `E+I` or `E+I+7`. The codes were read; the published table total was not.
- The nationality-sector key (sector in `ISSUER_BUS_ULT`, immediate sector `1`) was not valued. One call with `J` or `E` in position 5 would settle the amount.
- The OFR monitor may still download a country chart that is absent from the mnemonic list. The monitor’s Data button, or the current successor to the 2016 reference guide, would settle it.
- The exact `INVESTMENTCATEGORY` token, long name or code, was not read from a filing. One N-MFP3 portfolio record would settle it.
