# E-021 first pass — rates: in-house Sonnet agent's return (raw record)

*12 Oct 2026. The return of a Sonnet research agent, kept verbatim as a record; the supervisor's synthesis and checks are in `2026-10-12-E021-Where-The-Money-Comes-From-Rates-FX-Commodities.md`. Agent output is a claim until re-derived; the supervisor re-derived one load-bearing number per market (stated in the synthesis). Scratch files it cites lived in a session scratchpad and are not kept.*

---

I built the map for all four markets. The repo was only read, not edited. Everything below was fetched on 12 Oct 2026 and the raw files are in the `inh_rates/` scratch directory. The one thing I could not get is the ICI weekly flows: ICI returned HTTP 403 "Access Denied" to scripted fetches, and I did not work around it.

I used two Sonnet agents for the literature. I re-checked every quote I cite against the text they saved: all 37 matched, and none is over 15 words. I also spot-checked eight of their paper summaries against the opened text, and all held. Units are on every number; "10q" means 2024Q1–2026Q2.

## Findings that change the repo's picture

1. **Who absorbed US net issuance has shifted.** Z.1 (11 Sep vintage, read from the repo's `data/vintages/z1_20260911/` files) closes exactly every quarter, including the nonfinancial noncorporate row.

   | Group | Prior 4q (2024Q3–2025Q2) | Last 4q (2025Q3–2026Q2) |
   |---|---|---|
   | Net issuance | $1,615bn | $2,360bn |
   | Rest of world | $709bn (44%) | $294bn (12%) |
   | Money funds | $164bn | $668bn (28%) |
   | Fed | −$266bn | +$264bn (11%) |
   | Mutual funds, ETFs and closed-end | $176bn | $378bn |

   *MEASURED, in dollars.*

2. **The official-holdings decline since February is mostly not selling.** TIC foreign official holdings fell $236bn from Feb to Jul 2026.
   - Net sales were $103bn, of which bills were $99bn.
   - Valuation was −$107bn.
   - The unexplained residual was −$27bn.
   - Japan's Ministry of Finance sold dollars for ¥11.7trn between 30 Apr and 6 May 2026. That the intervention funded the bill sales is a HYPOTHESIS.

3. **H.4.1 custody is not a proxy for official holdings.** Marketable Treasuries in Fed custody fell $401bn (−13.5%) from 27 Dec 2023 to 7 Oct 2026. TIC official holdings fell $23bn (−0.6%) from Dec 2023 to Jul 2026.

4. **The repo's "money funds are net sellers" watch item has reversed in Q3.**
   - OFR's N-MFP series shows the Q2 fall as −$145.2bn against Z.1's −$144.9bn.
   - July and August then added $415bn, to $3,697bn.
   - That was funded by a cut in Treasury repo lending (−$221bn) plus new fund assets (+$130bn). The Fed repo drain that funded 2024–25 is exhausted: $969bn in Dec 2023 to $7bn in Jun 2026.

5. **Japanese residents turned net sellers of foreign bonds in 2026.** Net sales were ¥4.5trn through 3 Oct, against net purchases of ¥12.1trn in 2025. Banks sold ¥13.2trn (Jan–Sep) while trust accounts bought ¥11.4trn.

I found nothing that contradicts R1–R3's levels. TIC Table 5 for Feb–Jul 2026 matches the repo's 17 Sep extract exactly. TIC's net foreign purchases for Jan 2024–Jun 2026 are $1,440bn against Z.1's rest-of-world $1,325bn, an 8% gap.

## (A) Flows

| Flow | Buyer | Seller | Funding | Direction | Size and period | Grade | Source |
|---|---|---|---|---|---|---|---|
| Fed | Fed | Dealers and banks (secondary market); Treasury (rollovers) | New reserves; reserves are $3.03trn at 7 Oct | Out, then in | Z.1 −$344bn over 10q. Holdings $4,790bn (27 Dec 2023), $4,228bn (31 Dec 2025), $4,566bn (7 Oct 2026). Bills +$329bn since 31 Dec 2025; +$14bn over 4 weeks, +$56bn over 12 weeks | MEASURED | Z.1 FU713061103; H.4.1 |
| Foreign official | Foreign central banks | Dealers | FX reserves; Japan intervention ¥11.7trn, Apr–May 2026 | In 2024–25, out 2026 | Net +$30bn (2024), +$53bn (2025), −$13bn (Jan–Jul 2026); −$55bn over 4m, −$72bn over 12m. Holdings $3,773bn (Jul 2026) | MEASURED flows; BOUNDED official/private split; funding HYPOTHESIS | TIC SLT Table 3; MoF |
| Foreign private | Foreign banks, funds, insurers, offshore hedge funds | Dealers | FX-hedged (cost not on free data); repo for hedge funds | In, slowing | +$682bn (2024), +$520bn (2025), +$201bn (Jan–Jul 2026); +$111bn over 4m, +$368bn over 12m (prior 12m +$619bn) | MEASURED flows; funding HYPOTHESIS | TIC SLT Table 3 |
| Custody centres | Funds and intermediaries for unnamed owners | Dealers | Unknown | In | UK $998bn (+$102bn over 12m); Cayman $460bn (+$23bn over 12m); Belgium $471bn; Luxembourg $442bn. Fed staff put the Cayman hedge-fund shortfall at about $1.4trn at end-2024 | BOUNDED | TIC Table 5; FEDS Note 15 Oct 2025 |
| Basis trade and levered funds | Hedge funds (cash long, futures short) | Dealers and real money (cash side) | Repo: Form PF borrowing $3,382bn (30 Jun 2026) from about $2.0trn at end-2023. Lenders include money funds (Treasury repo $1,695bn, Aug 2026) | Built 2024–25, part unwound 2026 | Leveraged-fund futures short −$774bn (26 Dec 2023), −$1,154bn (30 Dec 2025), −$802bn (6 Oct 2026), all contract face. Form PF net Treasury long $864bn (30 Jun 2026) | MEASURED (futures, Form PF); BOUNDED (cash leg) | CFTC TFF; OFR; FEDS Notes |
| Money funds | Money-market funds | Treasury (bills) and dealers | Shareholder inflows; Fed repo drain (−$586bn in 2024, −$310bn in 2025); since 2026 a shift out of repo | In 2024–25, out H1 2026, in Jul–Aug | +$1.01trn over 10q (Z.1; OFR $2,270bn Dec 2023 to $3,281bn Jun 2026). H1 2026 −$236bn; Jul–Aug +$415bn | MEASURED | OFR MMF; Z.1 |
| Mutual funds and ETFs | Funds | Dealers | Investor flows (ICI not obtained) | In, accelerating | $640bn over 10q; $378bn in last 4q vs $176bn | MEASURED dollars; funding HYPOTHESIS | Z.1 |
| Banks | US commercial banks | Dealers | Deposits +$1,224bn (H.8, Sep 2025 to Sep 2026); reserves | In, flat recently | $491bn over 10q; $190bn in last 4q. H.8 Treasury and agency holdings $4,783bn (Sep avg), +$124bn over 12m, −$45bn over the last 4 weeks | MEASURED holdings; funding BOUNDED (accounting) | Z.1; H.8 |
| Insurers and pensions | Insurers, pension funds | Dealers | Premiums and contributions | In | $407bn over 10q; $205bn in last 4q vs $18bn | MEASURED | Z.1 |
| Household row | Probably offshore hedge funds that TIC misses | Dealers | Prime brokerage and repo | In | $459bn over 10q; $207bn in last 4q | Dollars MEASURED; attribution HYPOTHESIS (C-124) | Z.1; Cordes–Ferris |
| Dealers | Primary dealers | Treasury (auctions) | Repo | In | Z.1 $231bn over 10q. Net position $256bn (27 Dec 2023), $477bn (31 Dec 2025), $432bn (30 Sep 2026) | MEASURED | Z.1; NY Fed |
| JGB: BoJ shrinks | Banks, public pensions, overseas | BoJ (redemptions exceed purchases, not sales) | Banks: reserves released by the BoJ's shrinking; others unknown | BoJ out | Flow of Funds 10q: BoJ −¥63.0trn, banks +¥54.7trn, public pensions +¥32.3trn, overseas +¥23.7trn. Last 4q: BoJ −¥44.5trn, banks +¥31.7trn, public pensions +¥20.4trn, overseas +¥10.0trn, insurers −¥5.7trn. Overseas was −¥0.4trn in 2026Q2 after +¥7.6trn in Q1. BoJ accounts ¥588.4trn (Dec 2023) to ¥504.0trn (Sep 2026) | MEASURED | BoJ Flow of Funds; BoJ accounts |
| Japan outflow | Japanese banks, trust accounts, insurers | Foreign issuers | Yen funding | Out in 2026 | Residents' net foreign bonds: +¥3.6trn (2024), +¥12.1trn (2025), −¥4.5trn (2026 to 3 Oct) | MEASURED; cause HYPOTHESIS | MoF weekly and monthb3 |
| Euro: Eurosystem shrinks | Banks, rest of world, funds | Eurosystem | Unknown | Eurosystem out | Public-sector holdings −€1,128bn (Dec 2023 to Sep 2026, amortised cost); last 4q −€314bn. Banks +€318bn over the last 4q; investment funds +€90bn. Banks' buying slowed from €164bn (Jan–Apr 2026) to €36bn (May–Aug) | MEASURED | ECB APP/PEPP, SHSS, BSI |
| Gilts: BoE shrinks | Non-residents, hedge funds; defined-benefit pension demand falling (BoE FSR) | Bank of England | Unknown | BoE out | APF £895bn (Feb 2022) to £488bn (16 Sep 2026); −£70bn over 12m (£21bn active sales). Overseas holdings £757.3bn (2026Q2), +£61.0bn over 4 quarters including valuation | MEASURED stock; absorbers BOUNDED | BoE minutes Sep 2026; ONS HEWD |

## (B) Measures

All URLs are as fetched. "Lately" gives the 4-period and 12-period readings.

| Series | Code / URL | Freq; lag | Stock or flow | Latest fetched | In or out lately | How to measure change |
|---|---|---|---|---|---|---|
| TIC SLT Table 3 (the old Form S transactions are folded into SLT) | ticdata.treasury.gov/Publish/slt_table3.txt | Monthly; about 6–7 weeks (Aug data due 16 Oct per a search summary of Treasury's July release, not opened) | Stock, flow, valuation | Jul 2026 total $9,248bn, net +$35bn; official $3,773bn | Total +$56bn over 4m, +$296bn over 12m. Official −$55bn and −$72bn. Private +$111bn and +$368bn | Δholdings = net + valuation + residual. Bills' net is the position change |
| TIC Table 5 (major holders) | .../slt_table5.txt | Monthly; same | Stock | Japan $1,104bn; China $618bn; UK $998bn | Japan −$88bn and −$52bn. China −$35bn and −$78bn. UK +$71bn and +$102bn | Compare against Table 3 flows to separate valuation |
| TIC SLT Table 4 (gross) | .../slt_table4.txt | Monthly | Gross flow | 12m foreign gross purchases $45.8trn, sales $45.6trn, net $0.25trn | Net is 0.5% of gross | Never read net alone |
| TIC annual survey (SHL), June 2025 | .../Documents/shl2025r.pdf (Apr 2026) | Annual; 10 months | Stock | Treasury holdings $7.67trn | See section (C) | Table 1 gives net, valuation and "other" |
| H.4.1 custody | federalreserve.gov/releases/h41/current/ (memo item) | Weekly; 1 day | Stock at face value | Marketable Treasuries $2,565bn (7 Oct 2026) | −$25bn over 4 weeks, −$32bn over 12 weeks, −$212bn over 52 weeks | Week-over-week; not holdings, since custody migrates. The Fed's data-download package returned empty bodies to scripts, so I used the weekly pages |
| H.4.1 Fed holdings and foreign repo pool | same | Weekly | Stock | Fed Treasuries $4,566bn; foreign repo pool $331bn | Fed +$14bn and +$56bn | Face value includes TIPS compensation |
| H.8 banks | federalreserve.gov/releases/h8/current/, Table 2 | Weekly; 9 days | Stock, seasonally adjusted | $4,759.7bn (30 Sep week) | −$45bn over 4 weeks | Includes valuation and agency debt; use call reports for Treasury-only |
| Z.1 | federalreserve.gov/releases/z1/, FU263061105 and others | Quarterly; about 10 weeks | Flow | 2026Q2: net issuance $237bn | See (A) | Compare vintages; large revisions |
| Treasury auction results | api.fiscaldata.treasury.gov, `auctions_query` | Daily | Primary-market flow | 8 Oct 2026 | Dealers 15% (2024Q1) to 11% (2026Q3) of competitive coupons; direct 18% to 25%; indirect 67% to 64% | Class shares, not holders |
| Treasury investor-class allotments | home.treasury.gov/data/investor-class-auction-allotments | About 2 weeks | Primary-market flow | Issues to 30 Sep 2026 | Of non-Fed fixed-coupon allotments, 2023 / 2024 / 2025 / 2026 to Sep: investment funds 68% / 70% / 73% / 71%; foreign and international 14.9% / 12.5% / 12.8% / 14.6%; dealers 16.3% / 16.3% / 13.6% / 13.8% | "Investment funds" mixes hedge funds and asset managers |
| NY Fed primary dealers | markets.newyorkfed.org/api/pd/get/PDPOSGST-TOT.json | Weekly; 1–2 weeks | Stock | $432bn (30 Sep 2026) | −$28bn over 4 weeks, −$35bn over 12 weeks | Net long ex-TIPS |
| ON RRP | markets.newyorkfed.org/api/rp/reverserepo/... | Daily | Stock | $0.3bn (9 Oct) | Drained | No longer a funding source |
| OFR money funds | data.financialresearch.gov, `MMF-MMF_T_TOT-M`, `MMF-MMF_RP_T_TOT-M`, `MMF-MMF_RP_wFR-M` | Monthly; about 6 weeks | Stock | Treasuries $3,697bn (Aug 2026) | +$515bn over 4m, +$548bn over 12m | N-MFP-based; ties to Z.1 within $0.3bn |
| OFR Form PF | hf/v1 `FPF-ASSETCLASS_LTREASURY_SUM`, `...STREASURY_SUM`, `FPF-BORROW_REPO_SUM` | Quarterly; about 3.5 months | Stock | Long $2,362bn, short $1,498bn, repo $3,382bn (30 Jun 2026) | Net $791bn to $864bn over 1q | Exposures, not holdings |
| CFTC TFF | publicreporting.cftc.gov/resource/gpe5-46if.json | Weekly; 3 days | Stock (contract face) | −$801.7bn leveraged net short, six contracts (6 Oct 2026) | +$14bn (smaller short) over 4 weeks, +$122bn over 12 weeks, +$354bn over 52 weeks | The short is a basis-trade proxy only |
| ICI weekly flows | ici.org/research/stats/flows and /mmf | Weekly | Flow | **Not fetched**: 403 Access Denied. Search snippets only: money-fund assets $7.98trn (2 Sep 2026); bond funds +$7.13bn (week to 8 Jul) | Unknown | — |
| MoF weekly securities transactions | mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/week.csv | Weekly; 5 days | Flow, ¥100mn | Week 27 Sep–3 Oct 2026 | Residents' foreign bonds −¥1.84trn over 4 weeks, −¥2.90trn over 12 weeks. Non-residents' Japanese medium/long-term debt +¥1.40trn and +¥0.34trn (+¥10.2trn over 52 weeks) | Designated major investors only. Not JGB-only and not Treasury-only |
| MoF sector detail | `monthb3.csv` | Monthly; 8 days | Flow | Sep 2026 | Residents' total foreign bonds −¥1.22trn over 4m, −¥5.09trn over 12m | By banks, trusts, insurers |
| BoJ Flow of Funds | stat-search.boj.or.jp API, db FF, `FOF_FFAF{sector}311` | Quarterly; about 11 weeks | Flow | 2026Q2 | See (A) | Transactions; stocks via `FOF_FFAS...` |
| BoJ accounts | db BS01, `MABJMA5B` | Monthly; 8 days | Stock | ¥504.0trn (Sep 2026) | −¥29.1trn over 4m, −¥51.0trn over 12m | Book value; R3b uses face (¥513.0trn Aug) |
| ECB APP/PEPP | ecb.europa.eu/mopo/pdf/APP_breakdown_history.csv and PEPP file | Monthly; 2 weeks | Stock | €2,889bn (Sep 2026) | −€124bn over 4m, −€454bn over 12m | Amortised cost |
| ECB SHSS and BSI | `SHSS.Q.N.U2...` as in R3; `BSI.M.U2.N.A.A30.A.1.U2.2100.Z01.E` (stock), `...A.4...` (flow) | Quarterly 3.5 months; monthly 5–6 weeks | Stock and flow | SHSS 2026Q2; BSI Aug 2026 €2,392bn | Banks €36bn over 4m, €279bn over 12m | The ECB's euro-area balance-of-payments code was not found |
| UK | ONS `HEWD` (overseas gilt holdings); ONS `MEX2` (APF nominal) | Quarterly; monthly | Stock | £757.3bn (2026Q2); £407.7bn nominal (Aug 2026) | Overseas +£61.0bn over 4 quarters | The BoE's £488bn is on a purchase-proceeds basis, not nominal |

## (C) Literature

QT effects range from about 10bp (BoJ) to 25bp (BoE) on the 10-year yield, and from about 35bp per €1trn of holdings cut (ECB, survey-based) to about 80bp for a hypothetical Fed sale (Norges Bank Investment Management (NBIM), a demand-system estimate). The objects differ (announcement versus holdings versus supply), so these ranges are not directly comparable. As a programme claim they stay HYPOTHESIS.

| Finding | Authors, year | URL opened | Quote |
|---|---|---|---|
| QT raises yields; domestic nonbanks replaced central-bank holdings | Du, Forbes & Luzzetti, NBER WP 32321, 2024 | https://www.nber.org/papers/w32321.pdf | "QT announcements increase government bond yields, steepening the yield curve" |
| Runoff of about $2.5trn is equivalent to roughly 50bp of policy rate | Crawley, Gagnon, Hebden & Trevino, FEDS Note, 2022 | https://www.federalreserve.gov/econres/notes/feds-notes/substitutability-between-balance-sheet-reductions-and-policy-rate-hikes-some-illustrations-20220603.html | "roughly equivalent to raising the policy rate a little more than 50 basis points" |
| The 2023 rise was term premium | Diercks & Asnani, FEDS Note, 2024 | https://www.federalreserve.gov/econres/notes/feds-notes/the-treasury-tantrum-of-2023-20240903.html | "the rise in yields was primarily driven by an increase in term premiums" |
| Households (linked to foreign hedge funds) took Fed runoff in the first year of 2022 QT | Cordes & Ferris, FEDS Note, 2024 | https://www.federalreserve.gov/econres/notes/feds-notes/who-buys-treasuries-when-the-fed-reduces-its-holdings-20240614.html | "households purchased a large portion of Treasury securities the Fed no longer holds" |
| Market more price-sensitive; $100bn of supply adds about 3bp on the 5-year | Beltran & Li, IFDP 1447, Sep 2026 (preliminary) | https://www.federalreserve.gov/econres/ifdp/files/ifdp1447.pdf | "increase in Treasury supply currently raises five-year yields by approximately 3 basis points" |
| QT raises repo rates' sensitivity to supply | Anbil, Anderson, Cordes & Ruprecht, FEDS Note, 2026 | https://www.federalreserve.gov/econres/notes/feds-notes/repo-markets-and-the-feds-balance-sheet-implications-for-monetary-policy-implementation-20260826.html | "overall liquidity declines while the private sector must hold more Treasury securities" |
| Basis traders absorbed supply in 2017–19 | Glicoes et al., FEDS Note, 2024 | https://www.federalreserve.gov/econres/notes/feds-notes/quantifying-treasury-cash-futures-basis-trades-20240308.html | "basis traders absorbed much of the increased Treasury supply" |
| Basis trade about $830bn | Monin, FEDS Note, 2026 | https://www.federalreserve.gov/econres/notes/feds-notes/decomposing-hedge-funds-u-s-treasury-exposures-20260622.html | "basis trade has grown to approximately $830 billion as of September 2025" |
| TIC undercounts Cayman hedge funds | Barth et al., FEDS Note, 2025 | https://www.federalreserve.gov/econres/notes/feds-notes/the-cross-border-trail-of-the-treasury-basis-trade-20251015.html | "the TIC data appear to severely undercount Cayman-domiciled hedge funds' holdings of U.S. Treasuries" |
| TIC attributes holdings to the custodian's country | Judson & Kim, FEDS Note, 2026 | https://www.federalreserve.gov/econres/notes/feds-notes/measuring-cross-border-securities-positions-explaining-asymmetries-20260213.html | "are all recorded in TIC by the residence of the overseas depository" |
| The survey's residual covers series breaks and custody shifts; Treasuries held by foreigners rose $7.11trn to $7.67trn (June 2024–June 2025), of which official −$0.06trn | Treasury, NY Fed and Board, SHL 2025 report, Apr 2026 | https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/shl2025r.pdf | "can include series breaks, respondent panel changes, custody shifts, potential measurement errors" |
| Preferred habitat: arbitrageurs transmit shocks | Vayanos & Vila, Econometrica, 2021 | https://researchonline.lse.ac.uk/id/eprint/106509/2/Vayanos_a_preferred_habit_model_of_the_term_structure_published.pdf | "Shocks to the short rate are transmitted to long rates through arbitrageurs' carry trades" |
| Supply raises yields (2013 author draft) | Greenwood & Vayanos, RFS, 2014 | https://personal.lse.ac.uk/vayanos/Papers/BSEBR_RFS14.pdf | "positively related to bond yields and future returns" |
| Treasury supply moves spreads (2010 draft hosted by Treasury) | Krishnamurthy & Vissing-Jorgensen, JPE, 2012 | https://home.treasury.gov/system/files/276/2011-session-4-vissing-tsy-demand-PAPER.pdf | "changes in Treasury supply have large effects on a variety of yield spreads" |
| Dealer leverage and supply explain the regime change | Du, Hébert & Li, NY Fed SR 1023, 2022 | https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr1023.pdf | "increased bond supply and tightening leverage constraints can explain this change in regime" |
| Non-bank investors absorb most supply and are most yield-sensitive | Fang, Hardy & Lewis, BIS WP 1099, 2023 | https://www.bis.org/publications/working-paper-1099-who-holds-sovereign-debt-and-why-it-matters.pdf | "Private non-bank investors absorb disproportionately more sovereign debt supply than other investors" |
| 10% more debt means about 60bp on 10-year yields | NBIM, Discussion Note 1/2024 | https://www.nbim.no/contentassets/3b1b351fa63a47c3967bee50033f8b74/investor-demand-and-government-bond-pricing.pdf | "45 percent is absorbed by private domestic investors" |
| QE moves yields more than QT | Eren, Schrimpf & Xia, BIS WP 1105, 2023 (rev. 2025) | https://www.bis.org/publications/working-paper-1105-demand-government-debt-0.pdf | "the impact of QE on yields being greater than that of QT" |
| JGB purchase cuts add about 10bp (stock effect); about 25bp including flow. BoJ holdings −¥49trn, market participants +¥95trn | BoJ, Review 2026-E-10, Aug 2026 | https://www.boj.or.jp/en/research/wps_rev/rev_2026/data/rev26e10.pdf | "we find that the impact is modest, at around 10 basis points" |
| Overseas investors and pension funds are now marginal buyers | BoJ, Market Operations in FY2025, 2026 | https://www.boj.or.jp/en/research/brp/mor/data/mor260812.pdf | "Overseas investors and pension funds are playing an increasingly prominent role as buyers" |
| Private investors must absorb ¥30–50trn a year | AMRO, Japan Selected Issue 3, 2024 | https://amro-asia.org/wp-content/uploads/2025/03/SI3.-Balancing-Demand-and-Supply-of-Government-Bonds-post-BOJs-Tapering.pdf | "private investors will have to add JPY30-50 trillion of JGBs to their holding" |
| QT raises term premia (about 35bp per €1trn, survey-based) | Akkaya et al., ECB Blog, 2024 | https://www.ecb.europa.eu/press/blog/date/2024/html/ecb.blog241114~6a3182c0bd.en.html | "QT will result in an increase in long-term interest rates via higher term premia" |
| Eurosystem easing fell from about 175bp to about 75bp | Cipollone, ECB speech, Feb 2025 | https://www.ecb.europa.eu/press/key/date/2025/html/ecb.sp250218~cc20f3518c.en.html | "the easing impact has now fallen to around 75 basis points" |
| Hedge funds are entering euro sovereign markets (holdings data cannot split them) | ECB Financial Stability Review, May 2026 | https://www.ecb.europa.eu/press/financial-stability-publications/fsr/html/ecb.fsr202605~50566915a7.en.html | "global hedge funds increasing their presence in euro area sovereign bond markets" |
| Foreign creditors gained as the Eurosystem shrank | Bundesbank Monthly Report, Apr 2024 | https://publikationen.bundesbank.de/publikationen-en/reports-studies/monthly-reports/monthly-report-april-2024-929362?article=government-debt-in-the-euro-area-current-developments-in-creditor-structure--929590 | "Foreign creditors, in particular, gained in importance in Germany and France" |
| QE mirror: foreigners sold 70% of ECB purchases (QE side) | Koijen et al., Banque de France WP 601, 2018 | https://publications.banque-france.fr/sites/default/files/medias/documents/document-de-travail_601_2016.pdf | "We find that 70% of ECB purchases are sold by the foreign sector" |
| First annual QT programme raises the 10-year gilt yield by 20bp in low stress | Joyce & Lengyel, BoE SWP 1097, 2024 | https://www.bankofengland.co.uk/-/media/boe/files/working-paper/2024/the-yield-curve-impact-of-debt-issuance-and-the-implications-for-qt.pdf | "would raise 10-year yields by 20 basis points under low market stress" |
| QT adds 15–25bp; the 10-year rose 325bp, about 150bp of it term premium | BoE Monetary Policy Report, Aug 2025 | https://www.bankofengland.co.uk/-/media/boe/files/monetary-policy-report/2025/august/monetary-policy-report-august-2025.pdf | "a modest increase in long-term interest rates of between 15–25 basis points" |
| Defined-benefit pension demand for gilts has fallen | BoE Financial Stability Report, Jul 2026 | https://www.bankofengland.co.uk/financial-stability-report/2026/july-2026 | "pension funds have reduced their demand for gilts" |
| Absorption shifting to non-residents | Mann, BoE speech, 13 May 2026 | https://www.bankofengland.co.uk/-/media/boe/files/speech/2026/old-exposures-new-actors-speech-by-catherine-l-mann.pdf | "with a growing share of absorption now coming from non-residents" |
| Gilt supply is met by more price-sensitive buyers | Panigrahi & Sidhu, BoE Bank Insights, Jan 2026 | https://www.bankofengland.co.uk/bank-insights/2026/what-were-the-drivers-of-uk-long-term-interest-rates-in-2025 | "long-maturity gilt supply is increasingly being met by more price-sensitive participants" |
| 2026 yield rise reflects fiscal pressure | BIS Quarterly Review, Sep 2026 | https://www.bis.org/publications/qr-202609_0.pdf | "rising term premia that reflected fiscal pressures rather than inflation concerns" |

## Measurement results for section 3 (flows versus valuation, net versus gross, vintages)

- **TIC does not close on its own columns.** The change in long-term holdings minus (net purchases + valuation) is −$104bn (2024) and −$100bn (2025) for foreign official, and +$90bn (2025) and +$104bn (Jan–Jul 2026) for non-official. For the Treasury survey the "other" residual is −$0.07trn, official −$0.11trn, over June 2024–June 2025 (SHL 2025).
- **Monthly TIC against the annual survey, June 2025, long-term debt:** about 0.4% in total (SLT $13,900bn against SHL $13,840bn). By country the gaps are larger: Belgium −$53bn, UK −$50bn, Luxembourg −$38bn, and $113bn "country unknown" in the survey.
- **Net is tiny against gross.** Foreign gross purchases and sales of Treasury notes and bonds were about $45.8trn and $45.6trn over 12m, so net is 0.5% of gross.

## (D) Three measurements to build next

1. **Primary-market duration by investor class.** Apply R2's pricing and modified durations to each issue in the Treasury investor-class files (coupons and bills), multiplied by each class's allotment share. This gives 10-year equivalents taken at auction per class per quarter. Compare it with Z.1 dollars; the gap is secondary-market redistribution. It attacks the "who took the duration" gap directly. The "investment funds" class (about 71%) stays unresolved.
2. **A TIC closure ledger.** Each month, tabulate Δholdings = net + valuation + residual for official, private and the five custody centres, anchored to SHL Table 1 and H.4.1 custody, with the Barth Cayman overlay shown as a separate range. Publish the residual (about ±$100bn a year for official) as the error bar on every official-versus-private statement.
3. **A funding ledger for the levered bid.** Line up the weekly CFTC short and dealer net positions, the monthly money-fund Treasury repo and direct holdings, and the quarterly Form PF long, short and repo. Then run a lead-lag test with block-bootstrap ranges on whether money-fund shifts from repo to bills (Jul–Aug 2026: repo −$221bn, direct +$415bn) precede changes in hedge-fund shorts or repo. This stays HYPOTHESIS until the test is done.

## (E) Uncertain items

- **ICI is blocked and unmeasured.** Bond-fund and money-fund weekly direction over 4 and 12 periods is unknown; the two numbers I have are search-snippet only.
- **The IMF and one Fed paper were not opened.** The IMF Global Financial Stability Report, Article IVs and COFER gave 403 to the agents. Smith–Valcarcel on the Fed's balance sheet unwind (Kansas City Fed) timed out. The DMO Quarterly Review (gilt holdings by sector) is JavaScript-rendered, so UK holdings by sector beyond the overseas stock and the APF are not measured.
- **Release dates and series gaps.** The TIC August release date (16 Oct) comes from a search summary and was not opened. The Japan FX-intervention file lists only through Q2 2026. No ECB balance-of-payments code was found (400), so euro-area non-resident flows are not fetched.
- **Basis-trade size is not a holdings measure.** The CFTC short is only a proxy for the cash leg, and its 10-year equivalents carry about ±25% DV01 uncertainty. In 2026 the CFTC short fell while Form PF net long rose, a conflict I did not resolve.
- **Classification limits.** Auction classes ("indirect", "investment funds") are not holders. The MoF weekly series covers designated major investors and includes all foreign bonds, not Treasuries.
- **Basis mismatch.** The BoE's £488bn APF figure is on a purchase-proceeds basis and ONS shows £407.7bn nominal, so levels from the two sources are not comparable.
- **Literature caveats.**
  - Krishnamurthy–Vissing-Jorgensen is the 2010 draft and Greenwood–Vayanos the 2013 author draft; the published versions were not opened.
  - Du–Hébert–Li is the NY Fed 2022 version, not the Journal of Financial Economics (JFE) paper.
  - Eser et al., a QE-side paper on the ECB's asset purchase programme, was opened but not cited.
- **The funding column is mostly inference.** I measured the money-fund and hedge-fund repo links, but the funding of foreign private demand (FX-hedged versus repo) cannot be measured on free data, because the cross-currency basis is not free.

Files are in `<session-scratchpad>/inh_rates/`, in the subdirectories `tic/`, `h41/`, `h8/`, `mof/`, `misc/`, `ecb/`, `uk/`, `shl/`, `lit_us/` and `lit_intl/`.
