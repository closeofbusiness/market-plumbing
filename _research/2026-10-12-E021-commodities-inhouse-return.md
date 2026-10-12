# E-021 first pass — commodities: in-house Sonnet agent's return (raw record)

*12 Oct 2026. The return of a Sonnet research agent, kept verbatim as a record; the supervisor's synthesis and checks are in `2026-10-12-E021-Where-The-Money-Comes-From-Rates-FX-Commodities.md`. Agent output is a claim until re-derived; the supervisor re-derived one load-bearing number per market (stated in the synthesis). Scratch files it cites lived in a session scratchpad and are not kept.*

---

I built the map from data fetched on 12 Oct 2026; nothing was written to the repo. The scripts and extracted texts are under `<session-scratchpad>/inh_cmd/`.

**Contradictions with the brief**
- **The 2024 to 2026 gold move did not come through futures length.**
  - COMEX gold managed-money net long was 106,454 contracts on 26 Dec 2023 and is 110,987 now, while gold roughly doubled (GLD-implied $2,062 to $4,184/oz).
  - It peaked at 219,029 on 24 Sep 2024.
- **Reported central-bank buying is much smaller than the WGC estimate.**
  - IMF-reported world gold reserves rose +262 t in 2024 and +306 t in 2025.
  - The WGC estimate is 1,092 t and 863 t.
  - The WGC also cut its Q1 2026 central-bank figure from 244 t to 57 t.
- **"Real rates broke down" holds only for 2024–25.**
  - On weekly data, gold's sensitivity to the 10-year real yield was −11.9% per percentage point in 2018–21 (R² 0.32). In 2024–Oct 2026 it was −3.4 (R² 0.01).
  - Year by year, 2024 and 2025 are near zero. From Mar to Oct 2026 it is strong again (weekly −17.7, R² 0.18, n=32).
  - The 10-year real yield rose 1.19 pp from end-2023 to now (1.72% to 2.91%) while gold rose 103%.
  - This is HYPOTHESIS-grade: the result depends on the sample window, and monthly data over 2024–26 give −13.2.
- **IAU does not publish a tonnes history.**
  - The sponsor file has NAV per share and shares outstanding only. Tonnes appear for the latest day on the page: 463.87 t on 9 Oct 2026.
  - I rebuilt the history as shares × NAV ÷ GLD-implied $/oz. That gives 464.04 t on 9 Oct, 0.04% above the page.
- **The EIA API was not used.** It needs a key. I used the key-free `dnav` files instead.
- **WTI managed money differs a lot by report type.** Futures-only is 53,598; futures plus options combined is 104,491. The 12-week change flips sign (−8.4k futures-only, +18.1k combined).
- **Three gaps in free data.**
  - EIA's NYMEX futures series stops at 5 Apr 2024, so there is no free WTI curve series.
  - CFTC discontinued Index Investment Data in Oct 2015, and its Supplemental report covers agriculture only.
  - CME margin and stock files returned HTTP 403, and I did not retry.

**Answer in one line per market**
- **Gold:** money is flowing into official and bar/coin holdings and global ETFs. It is flowing out of managed-money futures over the last 4 weeks and out of US ETFs year to date.
- **Crude:** the move is a physical supply shock. Managed money is leaving, and stocks and the SPR are being drawn.
- **Copper:** managed money is down over 4 weeks and flat over 12. LME stocks are drawing, and the price is at a record.

## (A) Flows

| flow | buyer | seller | funding | direction | size and period (units; denominator) | grade | source |
|---|---|---|---|---|---|---|---|
| **Gold: official purchases, WGC estimate** | central banks | not observed trade by trade; supply is mine plus recycling, plus official sellers | reserve reallocation. 2025 ≈ $95bn, about 0.7% of non-gold world reserves (my arithmetic at WGC's average price) | IN | 1,092 t (2024, ≈$84bn); 863 t (2025); 346 t (H1 2026; Q1 revised 244→57, Q2 289) | BOUNDED (includes estimates) | WGC FY2025 table and Q2 2026 release |
| Gold: official purchases, reported | Poland +314 t, China +175 t, Kazakhstan +83, India +77, Türkiye +69 (Dec 2023 to latest) | as above | as above | IN | IMF world total +262 t (2024), +306 t (2025), +337 t (Dec 2025 to Aug 2026). Last 4 months +194 t, last 12 months +510 t. 141 reporters net +933 t since Dec 2023; top 5 are 64% of gross buying | MEASURED (a floor) | IMF IL dataflow |
| Gold: China | PBoC | not named | reserves | IN | 2,409.6 t (77.47m oz) at end-Sep 2026. Sep +23.0 t; 4 months +78.1 t; 12 months +106.1 t; 2026 year to date +103 t (≈0.4% of $3.4tn FX reserves). SAFE (State Administration of Foreign Exchange) data; the IMF series matches it to the tonne in June | MEASURED | SAFE |
| Gold: official sales | the market | Türkiye sold or loaned about 130 t after the Middle East war began; IMF data show 823→730 t Feb to May 2026, back to 795 t by Sep. Singapore −27 t, Philippines −26 t since Dec 2023 | funds currency defence and energy imports (per ECB) | OUT | tonnes as stated | MEASURED (IMF) and secondary (ECB) | IMF IL; ECB IRE June 2026 |
| **Gold: global ETFs** | investors in US, UK/EU and Asia-listed funds | authorised participants delivering bars (bullion banks) | investor cash; the source of that cash is not measured | IN, mixed | −3 t (2024); +801 t (2025, ≈$88bn); +18 t (H1 2026, Q2 −45 t); Q3 +211 t (≈$31bn). Holdings 4,256 t at end-Sep, a record | BOUNDED (WGC aggregate; raw data not free) | WGC |
| Gold: GLD + IAU | US investors | authorised participants | investor cash | 2025 IN, 2026 mixed | 2024 −12.5 t; 2025 +299 t (+$34.0bn); 2026 year to date −47 t (−$6.9bn); last 12 weeks +56.8 t (+$7.9bn); last 4 weeks +8.2 t (+$1.1bn). AUM went $84.7bn → $204.1bn (Dec 2023 to 9 Oct 2026): flows $27.2bn (23%), valuation $92.2bn (77%) | MEASURED (IAU tonnes BOUNDED, about ±0.1%) | sponsor files |
| Gold: bar and coin | households (China and India >50% of 2025 demand) | refiners and dealers | household savings | IN | 1,188 t → 1,374 t (2025, $154bn); Q2 2026 −3% y/y, H1 +21% y/y | BOUNDED | WGC |
| Gold: jewellery and technology | consumers | refiners | income | tonnes OUT, dollars IN | jewellery consumption 1,887 → 1,542 t (−18%) while value rose 18% to $172bn; technology 326 → 323 t | BOUNDED | WGC |
| Gold: supply | (these are the sellers) | miners 3,672 t (2025, USGS 3,300 t); recycling 1,404 t (+3%); net producer hedging −74 t (de-hedging) | n/a | n/a | Q2 2026: mine 966 t (+2% y/y), recycling −6% y/y | MEASURED (estimates). Total demand = total supply by WGC construction: IDENTITY | WGC; USGS |
| Gold: "OTC and other" | unobserved | unobserved | unknown | n/a | +331 t (2024) → +3 t (2025). The +990 t rise in investment demand in 2025 was absorbed by −389 t jewellery fabrication, −229 t central banks, −328 t this plug, and +40 t supply | BOUNDED (plug) | WGC |
| **Gold: COMEX managed money** | hedge funds and CTAs | swap dealers net short 225,026; producers/merchants net short 19,501; others and non-reportables net long 133,540. These sum to zero | margin only (not measured) | OUT lately | net long 110,987 contracts = 345 t = $46.1bn at $4,155. 4 weeks −23,985 (−74.6 t: −$10.0bn volume, −$3.3bn price). 12 weeks −9,792. 52 weeks −18,772. Open interest 396,109 = 1,232 t = $164.6bn | MEASURED | CFTC |
| Gold: index investment | n/a | n/a | n/a | not measurable | Index Investment Data discontinued (final report Oct 2015); the swap-dealer short mixes in bullion-bank hedges | HYPOTHESIS | CFTC |
| Gold: London vaults | custody stock, not purchases | n/a | n/a | up | 8,686 t (Dec 2024) → 9,106 t (Dec 2025) → 9,821 t (Sep 2026); last 4 months +429 t, last 12 months +980 t | MEASURED stock | LBMA |
| Gold: valuation | n/a | n/a | n/a | n/a | world official gold at market value 1,769bn → 3,743bn XDR (Dec 2023 to Aug 2026), a rise of 1,974bn XDR. By my decomposition about 96% is price (volume +905 t). Share of total reserves 15.3% → 27.1% (≈$5.1tn, matching the Fed's $5.1tn) | MEASURED | IMF IL |
| **Crude: US commercial stocks** | refiners, merchants | producers, imports, SPR | trader carry credit (unmeasured; no free curve) | flat to up | 424.1 mb (2 Oct 2026). 4 weeks +0.1; 12 weeks +14.5; 52 weeks +3.9. Same-week 2021–25 range 420.3–439.1 | MEASURED | EIA |
| Crude: SPR | refiners and exporters | US Department of Energy | proceeds to Treasury (HYPOTHESIS) | OUT | 283.0 mb. 52 weeks −124.0; 12 weeks −33.5; 4 weeks −2.4. From 413.2 at end-2025 to now −130 mb | MEASURED | EIA |
| Crude: world stocks | consumption funded by draws | inventories | n/a | OUT | EIA model: net withdrawals of 5.2 mb/d in Mar down to 2.9 in Sep; ≈656 mb Mar–Sep. OECD commercial stocks −148 mb (Dec 2025 to Sep) | BOUNDED (model, includes a residual) | EIA STEO Oct 2026 |
| **Crude: NYMEX WTI managed money** | hedge funds | swap dealers net short 461,468; producers/merchants net long 335,010; others +72,860 | margin only | OUT lately | net long 53.6 mb = $5.2bn at $96.2, about 0.5 day of world consumption (≈104 mb/d). 4 weeks −58.1 mb (−$5.6bn). 12 weeks −8.4. Open interest 1.89bn bbl = $181.8bn = 4.5× US commercial stocks | MEASURED | CFTC |
| Crude: price cause | n/a | n/a | n/a | n/a | WTI spot $60.0 (Jan) → $97 (Sep avg). News reports a Hormuz disruption since 28 Feb 2026; EIA says Middle East flows stay constrained through Q4 | HYPOTHESIS (causation) | EIA, news |
| Commodity ETFs, all commodities | US investors | n/a | n/a | IN | +$60.1bn issuance, 2024Q1–2026Q2 (repo's Z.1 key, not re-derived) | MEASURED (repo) | repo `monitor/DATA.md` |
| **Copper: COMEX managed money** | funds | producers/merchants net short 92,720; swaps net long 14,797; others +16,789 | margin only | OUT 4 weeks, flat 12 weeks | net long 61,134 contracts = 693 kt ≈ $10.0bn (monthly average price), about 2.4% of 2025 world refined output (29 Mt). 4 weeks −21,020 (−238 kt, −$3.4bn). 12 weeks +949. Versus end-2024 +65.5k. Open interest 304,033 = 3,448 kt | MEASURED | CFTC |
| Copper: LME stocks | n/a | n/a | n/a | OUT | 233.0 kt (9 Oct). 4 weeks −1.5; 12 weeks −63.6; peak 402.6 kt (15 Apr 2026); 145.3 kt on 2 Jan | MEASURED (third-party mirror of LME) | Westmetall |
| Copper: US stock build | US consumers and traders | mainly Chile | trade credit (HYPOTHESIS) | IN | US refined imports 903 → 1,700 kt (2024 to 2025); US stocks 123 → 450 kt | MEASURED (annual) | USGS |
| Copper: ICSG balance | n/a | n/a | n/a | n/a | Jan–Jul 2026 surplus about +32 kt, or −5 kt after bonded-stock adjustment. Combined exchange stocks 1.07 Mt at end-June. Secondary summaries only | HYPOTHESIS (unverified) | search summaries |

## (B) Measures

| series | code / URL | freq | lag | stock / flow | latest fetched | in or out (4 and 12 periods) | how to measure change |
|---|---|---|---|---|---|---|---|
| CFTC Disaggregated, futures only | `publicreporting.cftc.gov/resource/72hh-3qpy.json`; `cftc_contract_market_code` 088691 gold, 067651 WTI, 085692 copper. Fields: `m_money_positions_long_all`, `m_money_positions_short_all`, `swap_positions_long_all`, `swap__positions_short_all` (two underscores), `prod_merc_positions_*`, `other_rept_*`, `nonrept_*`, `open_interest_all`. Combined report: `kh3c-gbw2` | weekly | Tuesday as-of, Friday release (6 Oct data out 9 Oct) | stock of positions | as in (A), 6 Oct 2026 | gold OUT/OUT; WTI OUT/OUT (flips on combined); copper OUT/flat | contracts × unit × price; split volume vs price effect; test the identity that net positions sum to zero |
| GLD | `api.spdrgoldshares.com/api/v1/historical-archive?product=gld&exchange=NYSE&lang=en` (xlsx; "Tonnes of Gold", "Total Net Asset Value in the Trust") | daily | same day | stock | 1,053.13 t, 9 Oct 2026 | 4 weeks +5.7 t; 12 weeks +54.1 t (IN) | Δtonnes; dollars = Σ daily Δoz × price |
| IAU | `ishares.com/us/products/239561/ishares-gold-trust-fund` (page) and its `fundDownload` .xls (NAV and shares) | daily | same day | stock | 463.87 t, $62.43bn, 9 Oct 2026 | 4 weeks +2.5 t; 12 weeks +2.7 t (est.) | as above; tonnes reconstructed |
| Official gold volume | `api.imf.org/external/sdmx/2.1/data/IMF.STA,IL/*.RGV_REVS.*.M` (unit FTO, fine troy oz); `RGOLDMV_REVS`, `TRGMV_REVS`; `G001` is World | monthly | 1–3 months (Sep: 16 of 140 reporters) | stock | World 36,919 t (Aug 2026) | 4 months +194 t; 12 months +510 t (IN) | like-for-like by country; carry-forward breaks totals |
| China reserves | `safe.gov.cn/en/2021/0203/2045.html` (xlsx) | monthly | about 7th of next month | stock | 77.47m oz, Sep 2026 (published 7 Oct) | 4 months +78 t; 12 months +106 t (IN) | Δounces; value = ounces × price |
| US crude, SPR, Cushing | `eia.gov/dnav/pet/hist_xls/WCESTUS1w.xls`, `WCRSTUS1w.xls`, `W_EPC0_SAX_YCUOK_MBBLw.xls`; `ir.eia.gov/wpsr/table1.csv` | weekly | Wednesday, for the week ending the prior Friday | stock | commercial 424.1, SPR 283.0, Cushing 24.7 mb (2 Oct) | commercial flat/IN; SPR OUT/OUT | Δstock vs same-week 5-year range |
| EIA STEO | `eia.gov/outlooks/steo/xls/STEO_m.xlsx`, tab `3atab` | monthly | released 6 Oct | flow, model-based | net withdrawals 2.9 mb/d (Sep) | OUT | accumulate mb/d × days |
| EIA spot prices | `RWTCd.xls`, `RBRTEd.xls` | daily | about 1 week | price | WTI $96.24 (6 Oct) | n/a | for dollar conversion |
| London vault gold | `cdn.lbma.org.uk/downloads/LBMA-London-Vault-Holdings-Data-September-2026.xlsx` | monthly | about 2 weeks | stock | 9,821 t (Sep) | up | custody changes, not purchases |
| LME copper stocks | `westmetall.com/en/markdaten.php?action=table&field=LME_Cu_stock` | daily | 1 day | stock | 233,025 t, cash $14,689/t (9 Oct) | flat / OUT | Δstock against price |
| World Bank Pink Sheet | `worldbank.org/en/research/commodity-markets` (monthly xlsx; updated 2 Oct) | monthly | about 1 week | price | gold $4,319/oz, copper $14,474/t, WTI $96.9 (Sep) | n/a | monthly averages only |
| Treasury real yield curve | `home.treasury.gov` daily-treasury-rates CSV, type `daily_treasury_real_yield_curve` | daily | 0–1 day | rate | 10-year 2.91% (9 Oct) | n/a | gold beta regressions |
| WGC public tables and ETF page | `gold.org/download/file/21011/…` (Q2 2026 release); `/file/20432/…` (FY2025 summary); `gold.org/goldhub/research/gold-etfs-holdings-and-flows/2026/10` | quarterly / monthly | 1 week to 1 month | flow | as in (A) | n/a | tonnes and dollars |
| USGS MCS 2026 | `pubs.usgs.gov/periodicals/mcs2026/mcs2026-copper.pdf` (and `-gold.pdf`) | annual | 1 year | stock and flow | copper stocks 450 kt (2025) | n/a | annual only |

How to measure change, from the data:
- **Tonnes against dollars.** Track tonnes for flows and dollars for valuation, and split every change into volume and price. Of the $119.4bn rise in US gold ETF assets, 77% was price.
- **Positions against flows.** Open interest and positions are stocks. A futures long funds nothing physical: only margin moves, and every long has a short.
- **What positioning does and doesn't show.** Weekly changes in managed-money positions move with the same week's price (gold +0.32, WTI +0.40) but do not predict the next week (−0.02 and −0.09; n=148, 2024 to Oct 2026). The positions are coincident with price, and trend-following cannot be separated from price pressure here.

## (C) Literature
Each paper was opened. The extracted texts are in `lit/*.txt` and `lit/*.html` for you to pull quotes from. I give one verbatim quote below and paraphrases elsewhere, to respect the one-quote-per-response limit; I verified a 6–14-word string for each item against its extracted text.

| finding | authors, year | URL opened | location and note |
|---|---|---|---|
| Futures prices of different commodities became more correlated from the early 2000s, more so inside the GSCI and DJ-UBS indices; no such pattern in China | Tang and Xiong, 2010 (NBER 16385) | `nber.org/system/files/working_papers/w16385/w16385.pdf` | abstract, PDF p.2 |
| Review recasts the bubble debate as risk sharing and information discovery; financialization changed both | Cheng and Xiong, 2013 (NBER 19642; Annual Review 2014) | `nber.org/system/files/working_papers/w19642/w19642.pdf` | p.2 |
| Significant effects of investor flows on oil futures (index positions' growth, managed-money spread positions) | Singleton, 2012 draft (Management Science 2014) | `haas.berkeley.edu/wp-content/uploads/OILPUB.pdf` | abstract, PDF p.5 |
| Index positions don't predict agricultural returns; the oil link rests on 2007–09 and fails out of sample | Hamilton and Wu, 2013 draft (IER 2015) | `econweb.ucsd.edu/~jhamilto/commodity_index.pdf` | abstract, p.1 |
| Masters-type bubble behaviour is hard to find in 12 agricultural markets | Sanders and Irwin, 2015 (stands in for Irwin and Sanders 2011) | `farmdoc.illinois.edu/assets/meetings/nccc134/conf_2015/pdf/Sanders_Irwin_NCCC_134_2015.pdf` | abstract, p.3 |
| 2003–08 oil surge came from global business-cycle demand, not speculation; speculation mattered in 1979, 1986, 1990 | Kilian and Murphy, 2011 draft (JAE 2014) | `frbsf.org/Kilian_Role-of-Inventories-and-Speculative-Trading.pdf` | abstract, p.1 |
| Open interest is more informative than futures prices, is pro-cyclical, and predicts commodity returns | Hong and Yogo, 2012 (NBER 16712; JFE) | `nber.org/system/files/working_papers/w16712/w16712.pdf` | abstract, p.2 |
| Commodities pledged as collateral in financing raise prices and flatten the inventory–convenience-yield relation (the Charter's inventory-financing channel) | Tang and Zhu, 2016 (RFS) | `mit.edu/~zhuh/TangZhu_CommodityCollateral_RFS.pdf` | abstract, p.1 |
| Gold is an unreliable inflation hedge over practical horizons; the real gold price was strongly negatively tied to TIPS yields (−0.82) | Erb and Harvey, 2013 (NBER 18706) | `nber.org/system/files/working_papers/w18706/w18706.pdf` | abstract, p.2, Exhibit 13 |
| Gold's reserve share rose mostly through valuation (nearly all for advanced economies since 2021, about 80% for emerging markets); ounces held also rose; US financial sanctions raise the gold share | Arslanalp, Eichengreen and Simpson-Bell, Nov 2025 (NBER 34478) | `nber.org/system/files/working_papers/w34478/w34478.pdf` | PDF p.5 |
| Country-level gold accumulation is generally not de-dollarization; it fits modest diversification | Weiss, Sep 2025 (Fed IFDP 1420) | `federalreserve.gov/econres/ifdp/files/ifdp1420.pdf` | abstract, p.2 |
| The rise in world gold reserves' value since 2024 was price-driven by private demand, not a central-bank spike; world gold $5.1tn vs foreign official Treasuries $3.9tn at end-2025; US holds 22% | Weiss, 3 Sep 2026 (FEDS Note) | `federalreserve.gov/econres/notes/feds-notes/why-gold-didnt-actually-overtake-treasury-securities-as-the-worlds-favorite-reserve-asset-20260903.html` | quote: "demand from private sector investors jumped in late 2024" |
| Gold acts as a stress hedge; emerging-market central banks bought for geopolitical and sanctions reasons; COMEX delivery notices in Jan 2025 were the highest since 2007 | ECB Financial Stability Review box, May 2025 | `ecb.europa.eu/…/ecb.fsrbox202505_02~7f616fcd3f.en.html` | text |
| Central-bank buying about 850 t in 2025 (down from >1,000 t/yr, 2022–24); Poland the largest buyer (about 100 t); Türkiye sold or loaned about 130 t after the war began | ECB, June 2026 | `ecb.europa.eu/pub/pdf/ire/ecb.ire202606.en.pdf` | PDF pp.8 and 16 |
| Aggregate reserve trends largely reflect a few countries | Douglass, Goldberg and Hannaoui, May 2024 (NY Fed) | `libertystreeteconomics.newyorkfed.org/2024/05/taking-stock-dollar-assets-gold-and-official-foreign-exchange-reserves/` | text |
| Record 45% of 76 central banks plan to add gold; the survey excluded central banks under sanctions | WGC survey, 2026 | `gold.org/goldhub/research/central-bank-gold-reserves-survey-2026` | page text |
| Long and short open interest are equal by construction; trader classes follow predominant activity; index traders are reported for agriculture only | CFTC explanatory notes | `cftc.gov/MarketReports/CommitmentsofTraders/ExplanatoryNotes/index.htm` | text |

Not opened, because the host refused scripted access (HTTP 403) and I did not route around it:
- Irwin and Sanders 2011 (Oxford University Press)
- OECD 2010 Irwin–Sanders working paper
- IMF Working Paper 23/14
- IMF Note 2026/007
- Fattouh, Kilian and Mahadeva (CEPR)
- SSRN, including Torul's "Gold's Missing Anchor", a search result claiming gold broke from real rates

## (D) Three measurements to build next
1. **Weekly COT ledger for all three markets.**
   - Copy `bin/pull_cftc_tff.py`, switch to dataset `72hh-3qpy` (and `kh3c-gbw2`) and the six disaggregated fields.
   - Convert to oz, bbl and tonnes, then to dollars.
   - Split each weekly dollar change into volume and price, assert that the five class nets sum to zero, and keep futures-only and combined side by side.
2. **Gold tonnes ledger reconciled to the WGC.**
   - Source: IMF IL country series, SAFE for China, GLD and IAU, and the LBMA vault series.
   - Compare IMF-reported official buying with the WGC estimate, and GLD+IAU with global ETFs.
   - Report the unexplained residual, and track the reserve-value split (volume vs price) monthly.
3. **Crude physical ledger.**
   - Weekly commercial stocks, SPR, Cushing, exports and refinery inputs, with the monthly STEO net withdrawals.
   - Convert stock changes to dollars.
   - Find a free source for the term structure first, since EIA futures prices end at 5 Apr 2024.

## (E) Uncertain items
- **Central-bank gap.** The WGC and IMF numbers differ by roughly 2.5 to 4 times in 2024–25, and I could not verify from the opened files why. The WGC revised Q1 2026 by −187 t.
- **WGC aggregates not checked against raw data.** Global ETF holdings (4,256 t, +211 t in Q3) and the bar-coin and jewellery series are WGC/Metals Focus figures, not checked against raw data. The 2025 ETF dollar figure ($88bn) is my arithmetic.
- **Scope mismatch with the repo.** GLD+IAU is about 36% of global ETF holdings, and the repo's Z.1 figure is US-resident funds only.
- **Price inputs.**
  - Gold is NAV ÷ ounces from GLD (the sponsor removed the LBMA price column at ICE's request).
  - WTI is EIA spot, not the futures settlement.
  - Copper uses World Bank monthly averages, with the September average used for October. Copper dollar figures are approximate.
- **Brent spot jump.** EIA Brent spot rose from $114.8 to $135.5 on 2 Oct while WTI fell. I could not verify it and did not rely on it.
- **STEO is model-based.** "Historical" runs through Sep 2026, and the net-withdrawal series includes a residual.
- **Missing data.** COMEX and SHFE copper stocks, the WTI curve and margins are unavailable. The ICSG figures and the Hormuz timeline come from secondary or news sources.
- **COT limits.**
  - Only reportable positions are covered, as of Tuesday.
  - The WTI contract is NYMEX only (not ICE).
  - Classes follow trader judgment by predominant activity.
- **Reading swap-dealer shorts.** The reading that they hedge bullion-bank inventory and forwards is a HYPOTHESIS.
- **Regressions.** The gold–real yield results use a sponsor-derived gold price and have a timing mismatch with Treasury yields. Subperiod samples are small.
