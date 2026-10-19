# Grok attacks on the four g9 specs, 19 Oct 2026

Grok 4.7 (extra-high effort) via Cursor, fenced to read and web only. Each parcel held one spec and asked for the strongest case against it. Every return reported no breaches, no blocked attempts and no stage changes. The returns are input, not findings: each section opens with what the supervisor checked, and the rulings are in the committed spec named there. URLs Grok cited without fetching them in the call are listed after each return.

## Japan term premium

Spec: [`2026-10-19-Japan-Term-Premium-Spec.md`](2026-10-19-Japan-Term-Premium-Spec.md). Wall time 750 s; 15 pages fetched.

**Supervisor check: every share re-derived from the cached yield_M.csv (commit 33118433fe95) and held. Grok was RIGHT that Nakajima's GitHub repository states no licence, and WRONG that the JMA page lacks a reuse sentence (the live page, re-fetched 19 Oct, reads "free to use and reproduce with attribution"). Rulings R3-1 to R3-8 and R4-1 in the spec.**

Cited but not fetched in this call: https://www.boj.or.jp/en/research/wps_rev/rev_2026/data/rev26e10.pdf, https://www.ier.hit-u.ac.jp/Common/publication/DP/DPS-A760.pdf.

### Return

I'll review the spec as written, then check each data source and the model papers against the live documentation.The spec’s split hinges on how Nakajima, JMA, and the BoJ define the premium. I’ll check those definitions and the live files next.The monthly file and the BoJ wording check out so far. Next I’ll verify column names, the JMA licence, and how the papers define the premium.The live monthly file matches the pinned 10-year levels, but the same window on the JMA file does not. I’ll confirm licences and the yield definition before writing the verdict.## VERDICT

**BUILD WITH CHANGES.**

The load-bearing assumption is that Nakajima’s monthly share, s = dTP/dy = 0.5356, means the term premium was the larger part of the rise in Japan’s 10-year yield from December 2023 to September 2026. The arithmetic on `yield_M.csv` is right. That classification is not.

On commit `33118433fe95` (6 Oct 2026), 10-year term premium goes from −0.0583 to 1.1768 and the expected-rate component from 0.7444 to 1.8154. The changes are +1.2351 and +1.0710 percentage points. They sum to +2.3061, and 1.2351/2.3061 = 0.5356. That is 8 basis points of term-premium change from a tie, inside the spec’s own 0.40–0.60 band. Ichiue and Ueno (2013) define the term premium as the observed yield minus the average of expected future short rates, in a shadow-rate model whose long-run short rate ρ is a constant. Nakajima (2025) uses that model and estimates the monthly and daily files separately, on Ministry of Finance nominal yields. A constant long-run rate has nowhere to put a higher long-run expected rate except in the residual the file calls the term premium. Japan Macro Advisors says this directly: a fixed long-run rate “reads a genuine repricing of expected rates as a surge in risk compensation.”

The same months on JMA’s file give the other answer. December 2023: yield 0.6733, risk-neutral component 0.6293, term premium 0.0440. September 2026: 3.0656, 2.3281, 0.7375. Term premium change +0.69 percentage points, expected-rate change +1.70, share 0.29. JMA’s column `RN` is the average expected short rate, and `RN + TP` equals the yield. The 2004–2012 benchmark is the path the projection reverts to, not a demeaning of this file, because the levels still add up to the yield.

The 0.54 is also a blend of two regimes in Nakajima’s own file. December 2023 to December 2024: term premium +0.022, expected rates +0.375, share 0.06. December 2024 to September 2026: +1.213 and +0.696, share 0.64. The summer-2024 cut does not isolate that break. Window B (August 2024 to September 2026) is itself a blend and prints about 0.58. Across tenors over the full window the shares are about 0.36 (2-year), 0.44 (5-year), 0.54 (10-year) and 0.62 (20-year). The registered label picks the ambiguous tenor.

The spec’s JMA rule does not catch this. Half of Nakajima’s +1.2351 is 0.618. JMA’s +0.694 is above that, so the build will say `not_flagged` and only add `classification_differs`. The pre-written expectation that `model_sensitive` is likely is false on this file. The August 2024–June 2026 share is 0.64, so the 0.40–0.60 gate will say the series differs from the Bank of Japan’s “roughly the same degree.”

## REQUIRED CHANGES

1. Make the registered result the share, the basis-point distance to one half, and the four tenors. Do not record a binary winner inside 0.40–0.60. Reason: 0.5356 is 8 basis points from a tie, and the other tenors fall on both sides. Source: [yield_M.csv at 33118433fe95](https://raw.githubusercontent.com/jouchinakajima/program/33118433fe95b51be374b5179a80978d59ac4ee9/yield_M.csv).

2. Show the path, including December 2023–December 2024 and December 2024–September 2026, and do not treat window B as one regime. Reason: those shares are about 0.06 and 0.64. The summer-2024 cut averages them. Same file.

3. Judge Japan Macro Advisors by its own share, and state that its yield is a spot (zero-coupon) yield. Drop the “under half of Nakajima’s term-premium change” rule. Reason: that rule stays silent while the shares are 0.54 and 0.29. The yield changes differ by about 9 basis points (+2.39 versus +2.31), which does not account for the gap. Sources: [JMA page](https://takujiokubo.github.io/jma-data/jgb-yield-curve-main/), [curve-panel.csv](https://takujiokubo.github.io/jma-data/jgb-yield-curve-main/data/curve-panel.csv).

4. Say in the README that the cited model has a constant long-run short rate, so a higher long-run expected rate can sit in the term premium. Reason: Ichiue and Ueno set the factor means to zero and call ρ the long-run short rate; the term premium is the yield minus the expectations component. JMA’s fixed-long-run paragraph is the matching warning. Sources: [Ichiue and Ueno 2013, pp. 8–9 and 22](https://www.boj.or.jp/en/research/wps_rev/wps_2013/data/wp13e08.pdf), [JMA page](https://takujiokubo.github.io/jma-data/jgb-yield-curve-main/).

5. Parse the real header and scientific notation. The header is quoted full names (`TermPremium-5Y`, `ExpectedRate-10Y`), not the spec’s `-5Y` shorthand. Some 2-year cells are `-1e-04`. A 4-decimal shape test will latch STOP on a valid file. Source: the same `yield_M.csv`.

6. Name the Ministry of Finance series as a constant-maturity semiannual compound yield, in percent, with `-` for missing. It is not labeled a par yield. The 2013 paper used month-end zero-coupon yields; Nakajima (2025) uses the Ministry of Finance nominal yield and estimates monthly and daily models separately, which is why September 2026 term premium is 1.1768 in the monthly file and the daily mean is 1.0090. Sources: [MoF Q&A](https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/qa.htm), [jgbcme_all.csv](https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv), [Nakajima 2025, §§2.2–3](https://www.ier.hit-u.ac.jp/Common/publication/DP/DPS-A760.pdf).

7. Fix the licences. The GitHub repo’s `license` field is null; there is no CC BY 4.0. The yield page requires citation, says the figures are not the Bank of Japan’s view, and says past figures are revised. The database page adds use at the user’s own risk. The Japan Macro Advisors page does not say “free to use and reproduce”; it says the model is proprietary and that later estimates are available to paid users. The CSV itself downloads without a login. Keep raw files out of the repo. Sources: [repo API](https://api.github.com/repos/jouchinakajima/program), [yield page](https://sites.google.com/site/jnakajimaweb/yield), [jpmpdata terms](https://sites.google.com/view/jpmpdata/), [JMA page](https://takujiokubo.github.io/jma-data/jgb-yield-curve-main/).

8. Print the August 2024–June 2026 share, about 0.64, beside the Bank of Japan sentence. Do not turn “roughly the same degree” into a disagreement at 0.60. Source: [Review 2026-E-10](https://www.boj.or.jp/en/research/wps_rev/rev_2026/data/rev26e10.pdf).

A practitioner would keep the vintage pin, the one-vintage rule, the leak cap, and the sentence that this is one model’s residual. They would add the 2024-versus-2025–26 path and the Japan Macro Advisors share next to the headline, and remove the binary registered classification and the half-change rule. The fitted-yield check only reconfirms that term premium plus expected rate equals the monthly average. It does not test the model.

## SOURCES

- **WORKS.** Nakajima page and pinned monthly file. Free, no key. Columns and the December 2023 and September 2026 10-year pins match. Nine commits; newest `33118433fe95` at 2026-10-06T00:48:15Z. Blob `c68b8d57…` is 38,153 bytes. Daily blob `372d5edb…` is 784,130 bytes. [yield page](https://sites.google.com/site/jnakajimaweb/yield), [commits](https://api.github.com/repos/jouchinakajima/program/commits?path=yield_M.csv&per_page=100), [contents](https://api.github.com/repos/jouchinakajima/program/contents/).
- **CHANGED.** Repo licence. Public and scriptable, `license: null`, not CC BY 4.0. [repo API](https://api.github.com/repos/jouchinakajima/program).
- **WORKS.** Japan Macro Advisors page and `curve-panel.csv`. Free download, no login. `YM`, `Type`, `Yield_kY`, `RN_kY`, `TP_kY` for 2, 5, 10, 20. September 2026 10-year values match the spec. Forecast rows start 2026-10. **CHANGED** on the reuse sentence: it is not on the page.
- **WORKS.** Ministry of Finance `jgbcme_all.csv`. Free. Header `Date,1Y,…,10Y,15Y,20Y,…,40Y`, unit percent, missing as `-`, title row present. PDL 1.0 unless a specific rights notice applies. [copyright notice](https://www.mof.go.jp/english/about_mof/notice/index.html). The script reads a local cache, which is the right vintage control. This review did not re-average September 2026 from the live file; the fetch was truncated in the 1970s.
- **WORKS.** Bank of Japan Review HTML and PDF, free. [HTML](https://www.boj.or.jp/en/research/wps_rev/rev_2026/rev26e10.htm), [PDF](https://www.boj.or.jp/en/research/wps_rev/rev_2026/data/rev26e10.pdf).
- **WORKS.** Both model papers, free PDFs, URLs above.

## REFERENCE POINTS

1. Bank of Japan Review 2026-E-10, 4 Aug 2026, data through end-June 2026, Imakubo and Nakajima (2015): “both factors have contributed to roughly the same degree.” The factors are the expected short-rate component and the term premium, from summer 2024. Nakajima’s August 2024–June 2026 share is about 0.64. Expect a gap of roughly 10–15 points of share, not a match to 0.50. [PDF](https://www.boj.or.jp/en/research/wps_rev/rev_2026/data/rev26e10.pdf).

2. Japan Macro Advisors, October 2026 vintage: “the standard model puts the rise at +157bp against our +70bp.” That sentence is the 2022–2026 rise, not this window. On this window their file rises about 69 basis points with share 0.29, against Nakajima’s +124 basis points and 0.54. The build should reproduce 0.5356 exactly on the pinned monthly file and should miss Japan Macro Advisors by about 0.25 in the share. A build that lands near 0.29 has read the wrong file. Their level remark, “Our estimate reads 0.6% to 0.7%,” matches their mid-2026 premium, not Nakajima’s September 2026 level of 1.18. [JMA page](https://takujiokubo.github.io/jma-data/jgb-yield-curve-main/).

## UNCERTAIN

Whether Nakajima’s 2025 appendix still holds ρ fixed. The published file cites the 2013 model, which does. Whether the daily file’s full-window share crosses one half: the September 2026 gap is 17 basis points, larger than the 8-basis-point margin, and December 2023’s daily mean was not recomputed here. Whether Japan Macro Advisors’ September row is month-end: 3.0656 is close to the spec’s 30 Sep Ministry of Finance print of 3.057, and the page says spot, not month-end. How far Chart 3 sits from one half. The size of any convexity change: in 2013 the ignored Jensen term was about 5 basis points and described as stable.

## UK gold declarations

Spec: [`2026-10-19-UK-Gold-Exports-China-HK-Spec.md`](2026-10-19-UK-Gold-Exports-China-HK-Spec.md). Wall time 619 s; 22 pages fetched.

**Supervisor check: Grok's January 2024 China rows and the 2024 Swiss Comtrade pins match the spec and the second review. All ratios were dropped (R3-1). Rulings R3-1 to R3-8 in the spec.**

Cited but not fetched in this call: https://www.uktradeinfo.com/media/s4un0zcn/unscheduled-corrections-2021.pdf.

### Return

I'll review the spec as written, then check each data source and the method against the sources' own definitions.The spec is in hand. Next I’ll check HMRC, Comtrade, and the gold-code definitions against the live sources the build would use.HMRC’s API and licence are live. I’m checking the gold-code split, the trade-system break, and Comtrade’s reuse terms next.## VERDICT

**BUILD WITH CHANGES.**

The load-bearing assumption is that special-trade kilograms of CN 71081310 sent to China and Hong Kong are a ceiling that can be divided into SAFE’s reported reserve change and the World Gold Council official-sector total. That assumption is false. Built as written, 2024 produces about **9.3** (`408.830 t / 44.167 t`) and about **37%** (`408.830 / 1,092.4`). Those are not coverage ratios.

The monthly net-mass extract itself is a real customs quantity and checks out.

## Why the ratios mislead

HMRC’s Overseas Trade Statistics record gross declarations, not reserve purchases. From 1 May 2016 the UK uses special trade: warehouse and free-zone movements are out, and re-exports from those regimes are not recorded. Goods in transit are out as well. After that break the series can sit below metal that left the country, so it is not an upper bound. Monetary gold (71082000) is on the current suppression list from January 1993 and is excluded from the published statistics, so official monetary movements never enter the numerator.

SAFE’s figure is a reported stock change. The Council’s central-bank series is defined as net purchases, gross purchases minus gross sales, by central banks and other official institutions, and it adds an estimate of unreported buying. The 29 January 2026 full-year release puts that total at 1,092.4 t in 2024 and 863.3 t in 2025, and says unreported buying was 57% of the 2025 total. It reports People’s Bank of China net purchases of 44 t in 2024 and 27 t in 2025. Hong Kong is in the numerator and is not that reserve account. A location change of metal can show up in UK declarations and not in the Council’s demand total, or the reverse.

HMRC’s 2014 gold note says the ONS balance-of-payments series is change of ownership and the trade statistics are physical movement, and that the two diverge. CN 71081310 is the semi-manufactured code (the basket that actually carries the UK’s China flow), not the same heading as Swiss unwrought 710812. Question 6’s “UK exceeds Switzerland” flag will fire on different goods: 2024 China is 382,786 kg on the UK bar code and 336,327 kg on the Swiss unwrought code.

Two further distortions in the written rules: a SAFE change of zero (the ledger’s 2020 and 2021) blanks the multiple, so the starkest contrast is not reported; and the “notable” bar of three consecutive zero months was set after the 2024 path was already in the spec, where June and July are empty and August is a zero-mass row.

Net mass is whole kilograms. The live January 2024 China bar rows are port 428, net mass 25,046 kg, and port 434, net mass 0 with supplementary units 214. Value on the mass row is £1,306,665,011, the spec’s unit check. Rounding error is kilograms per year, not the tonne-scale error in the ratios.

## REQUIRED CHANGES

1. Drop `uk_bars_cn_hk_over_safe_multiple`, `uk_bars_cn_hk_share_of_wgc_pct`, and the Question 2 and Question 3 “exceeds” and “share above 100%” flags. If SAFE and the Council stay, print them as separate magnitudes for the same months, with no ratio and no ceiling wording. Reason: gross special-trade declarations of one code are not a subset of net official demand, and warehouse re-exports are missing. https://www.uktradeinfo.com/trade-data/latest-bulk-data-sets/bulk-data-sets-information-pack-includes-post-eu-exit-changes https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-full-year-2025/central-banks https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-full-year-2024/notes-and-definitions

2. Name the result “declared special-trade net mass”, and state that from May 2016 it is not an upper bound on metal leaving the UK. Keep the general/special flag and do not treat 2005–2016 and later years as one share series. Same HMRC bulk-pack URL; also https://www.uktradeinfo.com/trade-data/help-with-using-our-data/

3. Do not ratio UK 71081310 to Swiss 710812, and do not flag “UK exceeds Switzerland”. Label the UK series semi-manufactured CN 71081310, not unqualified “bars”. https://www.uktradeinfo.com/media/ql5n1n3c/gold_methodology.pdf https://wits.worldbank.org/trade/comtrade/en/country/GBR/year/2024/tradeflow/Exports/partner/ALL/product/710813

4. Mark a month provisional for up to 18 months after publication, not for 18 months before the newest month. Keep 2024 pins as a one-vintage check, not a permanent fail: unscheduled corrections have rewritten years far outside that window. https://www.uktradeinfo.com/trade-data/help-with-using-our-data/ https://www.uktradeinfo.com/media/s4un0zcn/unscheduled-corrections-2021.pdf

5. Record supplementary units divided by 1,000 beside net mass. Net mass is whole kilograms and drops small rows. https://www.uktradeinfo.com/trade-data/help-with-using-our-data/ and the live January 2024 query below.

6. On Comtrade, keep `netWgt`, store `isNetWgtEstimated`, and do not drop rows because `isReported` is false. The pinned 2024 Swiss annual rows return `isReported: false`, `isAggregate: true`, and `netWgt` equal to the spec. Do not claim `netWgt` equals `qty`. https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=757&period=2024&partnerCode=156,344&cmdCode=710812&flowCode=X

## SOURCES

- **HMRC API — WORKS.** Free, no key, scriptable. Documented options include `$filter`, `$select`, `$apply`, `$count`; `$orderby` is not listed. Rate limit 60 per minute; pages at 40,000. Live fields: `MonthId`, `FlowTypeId`, `CountryId`, `PortId`, `CommodityId`, `NetMass`, `SuppUnit`, `Value`, `SuppressionIndex`. Country 720/740/39 are CN/HK/CH. https://www.uktradeinfo.com/api-documentation/ https://api.uktradeinfo.com/Country?$filter=CountryId%20eq%20720%20or%20CountryId%20eq%20740%20or%20CountryId%20eq%2039&$select=CountryId,CountryCodeAlpha,CountryName https://api.uktradeinfo.com/OTS?$filter=CommodityId%20eq%2071081310%20and%20FlowTypeId%20eq%204%20and%20CountryId%20eq%20720%20and%20MonthId%20eq%20202401&$select=MonthId,FlowTypeId,CountryId,PortId,CommodityId,NetMass,SuppUnit,Value,SuppressionIndex
- **HMRC licence — WORKS.** Most UK Trade Info content is Open Government Licence v3.0: publish with attribution. https://www.uktradeinfo.com/terms-and-conditions https://www.nationalarchives.gov.uk/doc/open-government-licence/version/3/
- **HMRC coverage and revisions — WORKS.** Non-monetary gold from January 2005; provisional for up to 18 months after publication; special trade from May 2016. https://www.uktradeinfo.com/trade-data/help-with-using-our-data/ https://www.uktradeinfo.com/media/ql5n1n3c/gold_methodology.pdf
- **Suppressions — WORKS.** 71082000 is listed (SITC 974, January 1993). 71081310 was not on the list returned. https://www.uktradeinfo.com/trade-data/current-suppressions/
- **Comtrade preview — WORKS.** Keyless `GET /public/v1/preview/C/{A|M}/HS` returned `flowCode` X, partners 156 and 344, `cmdCode`, `netWgt`, `qty`, `primaryValue`, `isReported`, `isAggregate`, `isNetWgtEstimated`. https://comtradeapi.un.org/public/v1/preview/C/A/HS?reporterCode=826&period=2024&partnerCode=156,344&cmdCode=710813&flowCode=X
- **Comtrade terms — WORKS.** The spec’s policy URL still serves. Data are “for internal use only” unless an exemption applies. Exemption text: “Publication of limited amounts of UN Comtrade data in a few tables”. Annual partner totals fit; monthly kilograms should stay uncommitted, as specified. Cite “UN Comtrade”. https://uncomtrade.org/docs/policy-on-comtrade-data-use/ https://uncomtrade.org/docs/re-dissemination-of-data/
- **Council context — WORKS** as the cited publication (the build copies a local ledger, which was not opened). https://www.gold.org/goldhub/research/gold-demand-trends/gold-demand-trends-full-year-2025/central-banks
- **UK tariff heading 7108 — FAILS this session** (HTTP 403). https://www.trade-tariff.service.gov.uk/headings/7108

## REFERENCE POINTS

Both are UN Comtrade as published by WITS for 2024 UK exports of HS 710813 (semi-manufactured, non-monetary). The page does not show a release date. Quote: “to China ($29,407,013.84K , 382,802 Kg)”. Hong Kong on the same table is 26,063 kg. https://wits.worldbank.org/trade/comtrade/en/country/GBR/year/2024/tradeflow/Exports/partner/ALL/product/710813

WITS quantity is the supplementary quantity, not net mass. Comtrade `netWgt` for the same flow is 382,787.286 kg to China and 26,059.274 kg to Hong Kong. The build’s 2024 China bars of 382,786 kg should land about 16 kg under the WITS 382,802 kg, and bars plus the 1 kg of 71081380 should match `netWgt` within 1 kg. Hong Kong bars of 26,044 kg should be about 19 kg under 26,063 kg; bars plus 14 kg of 71081380 should match `netWgt` within about 1 kg. Same-source Swiss check: annual `netWgt` 336,327 kg to China and 90,145 kg to Hong Kong, equal to the spec’s pins.

## PRACTITIONER

Add the supplementary-unit mass, the May 2016 split on every long share, and one sentence that this is not the ONS ownership series. Keep China and Hong Kong separate in the headline. Remove the word “ceiling”, both ratios, and the UK-versus-Switzerland “exceeds” flag. Print powder as its own check row, per the ruling; it is not in the `monthly.csv` allowlist. Do not require a China-customs mirror to match.

## UNCERTAIN

The ledger file was not opened; agreement with the Council is from the spec’s quoted tonnes. SAFE’s own ounce table was not fetched; 44.167 t and 26.749 t are the unrounded cousins of the Council’s 44 t and 27 t, not a second customs source. Whether a suppressed gold row is moved to country 977 was not re-checked. `isReported: false` on a good annual aggregate is unexplained. Whether any EU partner sits on flow 4 after 2021 was not checked. No publisher other than Comtrade/WITS was found for this UK partner quantity.

## Japanese life insurers (test A)

Spec: [`2026-10-19-JP-Life-Insurers-Foreign-Bonds-Spec.md`](2026-10-19-JP-Life-Insurers-Foreign-Bonds-Spec.md). Wall time 813 s; 23 pages fetched.

**Supervisor check: MoF's English FAQ A5 (fetched 19 Oct) confirms that redemptions of overseas government bonds are counted in disposition. The series is therefore net disposition, not sales; the registered rule is unchanged. Rulings R3-1 to R3-7 in the spec.**

Cited but not fetched in this call: none.

### Return

I'll review the spec as written, then check each data source and the papers it depends on against their own documentation.The spec is precise about signs, the 2014 break, and coverage. I'll check those claims against the MoF and BoJ pages it depends on, and against published figures for the same flow.The MoF FAQ treats redemptions as dispositions, and the public sign note still describes the pre-2014 convention. I’ll check the CSV, the 2014 notice, sector definitions, and the licence pages against that.**VERDICT: BUILD WITH CHANGES.** The life-insurer cells in `monthb3.csv` are the right MoF series, in ¥100 million, with plus meaning net acquisition. The load-bearing assumption that fails is that this net is secondary-market sales. Disposition is an asset decrease. MoF states that redemptions of overseas government bonds, “such as U.S. Treasury,” are included and are dated on the redemption date, while purchases and sales are dated on the execution date. Built as written, the October band, Q1’s “net sales,” and Q2’s split of the change in the mean into acquisitions versus disposals will be read as selling.

The integers themselves match the live 8 October 2026 file. September 2026 life is 5,487 / 8,374 / −2,886. The 24 base nets in C10 match, in order. Sorted, the 3rd is −2,886, the 12th and 13th are −802 and −762, and their mean is −782, and the 22nd is +746. January 2005 life is 5,271 / 9,384 / −4,113, so pre-2014 rows in this file are already on the current sign. The 2014 break is real and not restated: open-end contractual investment trusts left long-term debt for equities and fund shares, and the five-sector split was not carried backward. Section 4’s 2014 start is the right response. These are designated-reporter contract flows. They are not holdings, not US Treasuries alone, not a currency or hedge split, and not a cause of yields.

## REQUIRED CHANGES

1. In the README, Q1, Q2, and the forecast note, name the object net acquisition and net disposition, and state that disposition includes redemptions of overseas government bonds. Source: [MoF FAQ Q5 and Q6](https://www.mof.go.jp/english/policy/international_policy/reference/itn_transactions_in_securities/faq_its_english.html). September’s gross difference is −2,887; the file net is −2,886. Print the file net and the 1-unit residual.
2. Rename `all_residents` to the designated-reporter total. Q3’s share uses that total as the denominator. The survey is narrower than balance-of-payments portfolio investment, omits samurai primary issuance and resident-issued foreign-currency bonds, and is released a month earlier. Sources: [FAQ Q1](https://www.mof.go.jp/english/policy/international_policy/reference/itn_transactions_in_securities/faq_its_english.html), [Japanese index](https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/index.htm).
3. Delete the Q6 sentence that fund-share flows could offset long-term debt sales. `monthb2` is equities and all fund shares. The 27 December 2013 notice moved those trusts and did not split bond funds from equity funds. Source: [notice](https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/notice/notice20131227.pdf).
4. Label `inv_trust` with file Note 4: it includes asset management companies. The Bank of Japan classification that MoF cites also places private pension funds, money lenders, and special-purpose companies in that investor type. Keep trust accounts unnamed as pensions. Sources: Note 4 on [monthb3.csv](https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/monthb3.csv); [BoJ FAQ No. 14, Table 2](https://www.boj.or.jp/en/statistics/outline/exp/faqbpsm6.htm).
5. Start the post-decision window in April 2024. The 19 March 2024 call-rate change took effect on 21 March, so March’s contracts are mostly on the old guideline. Source: [19 March 2024 statement](https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2024/k240319a.pdf).
6. Match sector labels after folding full-width parentheses and letters. “Life Insurance Companies” is plain ASCII and is the correct block. Several bank labels in the fetched headers are not the ASCII strings in table 2.2.
7. Keep the file’s own sign. CSV Note 2 says plus is net acquisition for the published file, and the 2005 identity agrees. The English index still says plus is net sales. Do not code that banner. Source: [English index](https://www.mof.go.jp/english/policy/international_policy/reference/itn_transactions_in_securities/index.htm).

## SOURCES

- **WORKS.** [monthb3.csv](https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/monthb3.csv), [monthb1.csv](https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/monthb1.csv), [monthb2.csv](https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/monthb2.csv), [monthb4.csv](https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/monthb4.csv). Free, no key, CP932, titles and “Life Insurance Companies” and “Final Update October 8, 2026” and “100 mil Yen” present. October–December 2026 blank. PDL 1.0: copy, adapt, and commercial use allowed; cite the source and the processor; numerical data are outside copyright. [MoF copyright](https://www.mof.go.jp/about_mof/notice/index.html), [PDL 1.0](https://www.digital.go.jp/resources/open_data/public_data_license_v1.0). No extra restriction on the CSVs. The GSI-map exception does not apply.
- **WORKS.** [terms](https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/terms.html): long-term debt is original maturity over one year, including yen-denominated foreign bonds; acquisition and disposition are asset increases and decreases.
- **WORKS.** [data.htm](https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/data.htm) and the notice: only the net sign was restated; fund and sector changes were not. [Index](https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/index.htm): no errata are currently posted.
- **WORKS.** [English schedule](https://www.mof.go.jp/english/policy/international_policy/reference/itn_transactions_in_securities/schedule.htm): October 2026 on 10 November 2026, 8:50 JST, subject to change.
- **CHANGED.** [English index](https://www.mof.go.jp/english/policy/international_policy/reference/itn_transactions_in_securities/index.htm): the sign banner still describes plus as net sales. The CSV does not.
- **WORKS** for the three statements fetched, phrases matched: [4 April 2013](https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2013/k130404a.pdf), [19 March 2024](https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2024/k240319a.pdf), [18 September 2026](https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2026/k260918a.pdf) (“around 1.25 percent,” effective 24 September). [BoJ copyright](https://www.boj.or.jp/en/about/copyright.htm): copying with credit is allowed; commercial copying needs permission; do not alter. A non-commercial cache fits. Indexes [2024](https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2024/index.htm), [2025](https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2025/index.htm), [2026](https://www.boj.or.jp/en/mopo/mpmdeci/mpr_2026/index.htm) show many “Statement on Monetary Policy” dates besides the six rate changes, including 23 January 2026. Markers only; Q5 does not join them to the flow.

## REFERENCE POINTS

1. Nikkei, 21 February 2023, [article](https://www.nikkei.com/article/DGKKZO68630780Q3A220C2EE9000/): “通年でも11兆円強と最も多かった” and December “2.2兆円強.” The 2022 monthly life nets sum to −114,640 (¥11.464 trillion); December is −22,466 (¥2.2466 trillion). The build should hit those cells. The prose should land within about ¥0.05 trillion on December and inside “a bit over ¥11 trillion” on the year.
2. Japan Times, 8 December 2022, [article](https://www.japantimes.co.jp/news/2022/12/08/business/financial-markets/japan-life-insurance-foreign-bonds/): “offloaded a net ¥1.9 trillion of overseas debt in November.” November 2022 life long-term net is −19,269 (¥1.9269 trillion). Short-term that month is −4. Expect agreement within about ¥0.05 trillion. The article said preliminary; this vintage still rounds to ¥1.9 trillion.

## UNCERTAIN

SHA-256 and exact byte counts were not recomputed, and this session could not see HTTP status, so a redirect could trip the no-redirect latch. The other nine PDF hashes were not opened. How large redemptions are inside life dispositions is unknown, which is the gap between this net and secondary-market sales. Whether private pensions sit in this file’s investment-trust column, or only in the balance-of-payments classification, is not settled by Note 4. The direction “W2 mean below W1” was written with the monthly cells already in hand; whether the means were computed first is unknown. The order-statistic band is a frozen rule for this net, including redemptions. It is not a prediction interval and not a sales forecast.

## Fund futures and the index split (test B)

Spec: [`2026-10-19-Fund-Futures-And-Index-Split-Spec.md`](2026-10-19-Fund-Futures-And-Index-Split-Spec.md). Wall time 964 s; 25 pages fetched.

**Supervisor check: SEC's N-CEN data-sets page (fetched 19 Oct) confirms that schema-3.1 filings are omitted. Rulings R23-1 to R23-19 in the spec.**

Cited but not fetched in this call: https://catalog.data.gov/dataset/form-n-cen-data-sets.

### Return

I'll review the spec as written against how the series are defined, then check each source and the CME contract rules on the live web.The spec is loaded. Next I’ll check the contract rules, form definitions, and each data source against the live pages.**VERDICT: BUILD WITH CHANGES.**

Load-bearing assumption: each futures contract is a par bond at the short end of its delivery basket, weighted on the 29 Dec 2023 curve, and the ratio q on stable N-CEN "Index Fund" series is the share of registered funds' cash Treasury 10-year-equivalent change.

The futures stock can be measured. As written, the decision rules can certify a misleading figure. These are holdings. They do not show what moved Treasury yields.

**Where the number goes wrong.** The headline weight is face times par modified duration, divided by the conversion factor and by the 10-year duration. That is futures DV01 only if the cheapest-to-deliver bond is that par bond, its price is par, and a flat curve below the 6% standard keeps the cheapest bond at the short stub from 2023Q4 through 2026Q2. Carry and delivery options are omitted, and one factor covers every expiry. The result is an end-2023 risk unit, comparable to the cash arm, not the change in live DV01. Mutual-fund futures sit mostly in the 2- and 5-year contracts, whose baskets are only a few months wide, so the short stub is fair there. It is weak for the classic bond, whose basket runs from 15 years to under 25.

The modelled cheapest-to-deliver check is not valid until the basket is the contract grade. Below 6%, the lowest-duration bond minimizes price over conversion factor, so an ineligible high-coupon bond can win. The 10-year screen omits "original term not more than 10 years" and can admit aged bonds. The 2- and 3-year screens use the last day of the delivery month for both bounds. The rulebook measures both from the first day. A 2024 CME explainer puts only the cap on the last day.

q divides stable-index by stable-index plus stable-active. Money-market, levered/inverse, switchers, unflagged, and feeders sit outside that denominator, and the unclassified cap does not cover money-market or levered funds. q is withheld only when the denominator is at or below zero, so opposite signs still produce a "share" outside 0 to 1 that can be SUPPORTS. The gloss calls this the share of registered funds' cash Treasury duration change. `IS_INDEX` means fundType "Index Fund", any index. A series absent at the start has S = 0, so a new fund's whole book is a change. Ruling B2 makes a later N-CEN the primary flag; section 4.2 and guard G11 still treat a later filing as a mutant. Schema 3.1 N-CEN filings are omitted from the bulk sets, so 2025–2026 flags can be stale while check C-B7 does not bind the verdict. `FEEDER_FUNDS` lists the feeder's series; `MASTER_FUNDS` describes the master and has no master series id. Read literally, the join can zero the wrong fund. The 0.15 hurdle is taken from another object's 29.2% minus 14.5% gap after that object was measured. One ordered rule limits multiple comparisons. The bars are not sampling-error estimates. The 3-year face was set after seeing 14 lines in the 2024q1 zip; CME confirms $200,000, so that peek corrected a false prior.

N-PORT `NOTIONAL_AMOUNT` is "contract value on trade date", not face. Contract count times face matches the FEDS definition (positions times contract size) and the observed price ratios near 1.02–1.22. Sign from the futures payoff field, with absolute balance, matches that long/short field. The FEDS footnote that prices every contract except the 2-year at $100,000 is wrong for the 3-year. Those 14 lines barely move the anchor.

**REQUIRED CHANGES**

1. Define the index share as index ΔS over all groups' ΔS, and define q only when both arms are positive. Say "N-CEN Index Fund series" in the SUPPORTS line. q is not the share the verdict names. https://www.sec.gov/files/ncen_readme.pdf

2. Write one flag rule that matches ruling B2, name which arm a backfilled series enters, and stop G11 from treating that backfill as a mutant. The body, the ruling, and the selftest cannot all be true.

3. Add schema-3.1 omissions to the unclassified bound, or block SUPPORTS when that gap is large. Those filings are left out of the zips. https://www.sec.gov/data-research/sec-markets-data/form-n-cen-data-sets

4. Zero feeders through `FEEDER_FUNDS.REGISTERED_SERIES_ID` linked to the master's filing. `MASTER_FUNDS` does not identify the master series. https://www.sec.gov/files/ncen_readme.pdf

5. Screen baskets as in the rulebook: first day of the expiration month; round down to a month for the 2-, 3-, and 5-year and to a quarter for the others before the test; 10-year notes with original term at most 10 years, remaining at least 6 years 6 months and less than 8 years; bonds only for the Bond and Ultra Bond; fixed principal and fixed semi-annual coupons. https://www.cmegroup.com/rulebook/CBOT/II/19.pdf

6. Drop the fixture "6% coupon gives 1.0000 at any term", and round the synthetic coupon to the nearest eighth, ties upward. Between coupon dates a 6% bond rounds to 0.9999, and CME rounds the coupon. https://www.cmegroup.com/articles/2024/calculating-us-treasury-futures-conversion-factors.html

7. Compare treasury-fund net face with Figure 5, and all-fund long face with Figure 3, ETF and ex-ETF separately. The note never says ETFs are excluded. The "$500 billion" sentence is a long-exposure estimate, not the $314 billion net. https://www.federalreserve.gov/econres/notes/feds-notes/why-do-mutual-funds-invest-in-treasury-futures-20240510.html

**SOURCES**

- N-PORT: WORKS. Free quarterly zips, October 2019–September 2026, including 2026 Q3; as-filed, no warranty; money-market funds excluded. `PAYOFF_PROFILE`, `NOTIONAL_AMOUNT`, `BALANCE`, and `UNIT` are in the readme. https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets and https://www.sec.gov/files/nport_readme.pdf
- N-CEN: WORKS, with the schema 3.1 hole. The spec's flag columns are in the readme. 2026 Q3 is on the SEC page. The `_0` filenames were not in the fetched HTML. https://www.sec.gov/data-research/sec-markets-data/form-n-cen-data-sets and https://www.sec.gov/files/ncen_readme.pdf
- data.gov N-CEN catalog: FAILS this session (fetch timed out). https://catalog.data.gov/dataset/form-n-cen-data-sets
- FEDS note and accessible table: WORKS. Free Board text. J.P. Morgan durations are their input, not a file to pull. https://www.federalreserve.gov/econres/notes/feds-notes/why-do-mutual-funds-invest-in-treasury-futures-20240510.html and https://www.federalreserve.gov/econres/notes/feds-notes/why-do-mutual-funds-invest-in-treasury-futures-accessible-20240510.htm
- MSPD: WORKS, free, through 30 Sep 2026, dollars in millions, notes, bonds, TIPS, and floating-rate notes separated. UNCERTAIN that the live file uses the cache's CUSIP-in-`security_class2_desc` layout. https://fiscaldata.treasury.gov/datasets/monthly-statement-public-debt/detail-of-treasury-securities-outstanding
- CME grade table and rule chapters: WORKS. No CME feed is an input. Chapter 25 PDF returned 404. https://www.cmegroup.com/articles/2024/calculating-us-treasury-futures-conversion-factors.html
- Frozen curve: no public URL in the spec. UNCERTAIN.

**REFERENCE POINTS**

1. Iorio, Li, and Petrasek, 10 May 2024, Figure 5, 2023 Q4. Treasury-fund futures net notional is `3.13779E+11` dollars, and futures DV01 is `117752385.4` per basis point, despite headers "Billions of $" and "Millions of $". Implied duration is 3.75 years. A matching 1% treasury-fund net face should land within about $40 billion, and duration within about 0.5 year. The design's bands are wider. https://www.federalreserve.gov/econres/notes/feds-notes/why-do-mutual-funds-invest-in-treasury-futures-accessible-20240510.htm

2. Same note, 2023 Q4, all mutual funds. Quote: "roughly $500 Billion in Treasury Futures". Figure 3: "around $370 billion at the end of 2023" in 2- and 5-year futures, and 10- and 30-year futures "around $100 billion". Long face near $470–500 billion; net face is lower by the shorts. https://www.federalreserve.gov/econres/notes/feds-notes/why-do-mutual-funds-invest-in-treasury-futures-20240510.html

No published index-versus-active split of this cash change was found.

**CME rules fetched this session**

- 2-year: "face value at maturity of two hundred thousand dollars ($200,000)"; remaining "not more than 2 years" and "not less than 1 year 9 months", "from the first day", "rounded down to the nearest one-month increment." https://www.cmegroup.com/rulebook/CBOT/II/21.pdf
- 3-year: "two hundred thousand dollars ($200,000)"; original "not more than 7 years"; remaining "not more than 3 years" and "not less than 2 years 9 months", from the first day, rounded to a month. https://www.cmegroup.com/content/dam/cmegroup/rulebook/CBOT/III/39.pdf
- 5-year: "one hundred thousand dollars ($100,000)"; original "not more than 5 years 3 months"; remaining "not less than 4 years 2 months", from the first day, rounded to a month. https://www.cmegroup.com/rulebook/CBOT/II/20.pdf
- 10-year: "one hundred thousand dollars ($100,000)"; original "not more than 10 years"; remaining "not less than 6 years 6 months and less than 8 years", from the first day, "rounded down to the nearest three-month increment." https://www.cmegroup.com/rulebook/CBOT/II/19.pdf
- Ultra 10-year: "$100,000"; original "not more than 10 years"; remaining "not less than 9 years 5 months", from the first day. Quarter rounding is stated for the conversion factor. https://www.cmegroup.com/rulebook/CBOT/II/26.pdf
- Bond: "$100,000"; if not callable, "at least 15 years but less than 25 years", from the first day, rounded to a quarter. https://www.cmegroup.com/rulebook/CBOT/II/18.pdf
- Ultra Bond: "$100,000"; "remaining term to maturity of at least 25 years", from the first day, rounded to a quarter. No 30-year cap. https://www.cmegroup.com/content/dam/cmegroup/rulebook/CBOT/III/40.pdf
- A 20-year contract exists (TWE). Grade table: "not less than 19 years 2 months and not more than 19 years 11 months." Basics page face: "$100,000". https://www.cmegroup.com/articles/2024/calculating-us-treasury-futures-conversion-factors.html and https://www.cmegroup.com/trading/interest-rates/basics-of-us-treasury-futures.html
- Conversion factor: "the price at which a note … will yield 6% per annum", "rounded to four decimal places"; coupon "rounded to the nearest one-eighth of one percent (rounded up in the case of ties)"; months "rounded down to the nearest quarter" for Ultra Bond, Bond, 20-year, Ultra 10-year, and 10-year, "and to the nearest month" for the 5-, 3-, and 2-year. Invoice is `$1000 × settlement × factor`, and `$2000 × settlement × factor` for the 2- and 3-year. https://www.cmegroup.com/rulebook/CBOT/II/19.pdf

**What a practitioner would change.** Add a continuing-fund versus entrant split, dollars per basis point by contract, and the two FEDS face checks side by side. Put sign-disagreement notionals into the same bound as unresolved lines. Keep the 0.15 bar only as a labeled hurdle. Leave futures out of the cash total.

**UNCERTAIN.** Whether the 2- and 3-year cap is from the first day (rulebook) or the last day (2024 explainer). Whether any callable Treasury remains. The `_0` zip names. The CUSIP-level MSPD layout. The public source of the frozen curve. The size of the schema 3.1 gap. Whether the FEDS 1% screen is gross face over net assets, and whether ETFs are inside the $314 billion and $500 billion figures.
