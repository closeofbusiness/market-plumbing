# R4R return: the October additions, attacked (Run 2026-10-11 by Grok)

Repo state read: HEAD 34b1d4a. Grades follow the charter: nothing here says flows caused a price move. Quotes are 15 words or fewer. Every figure marked "re-derived" was recomputed from the named source file, not from a note. Where I could not reach a source I say so under UNCERTAIN.

## 1. RE-DERIVED

| claim | our value | your value | source | match or mismatch |
|---|---|---|---|---|
| T1 Public 10y-equivalent, fixed curve, 29 Dec 2023 to 31 Aug 2026 | +24.8% (558.0 to 696.5 ¥trn) | +24.8%; script re-run gives identical supply table | data/r3_rates/jgb_duration_supply.csv, plus a fresh run of bin/r3b_jgb_duration.py (72 checks, 0 fail) | match |
| T1 Same from 31 Oct 2024 (observed) | +16.0% (600.4 to 696.5) | +16.0% | same | match |
| T1 re-run difference | n/a | only the 30 Sep 2026 BoJ row differs (MoF curve date 24 Sep to 30 Sep; 10y-eq own curve 263.123 to 263.125) | jgb_duration_boj_only.csv | immaterial |
| T2 0.1% 2033 linker real yield 29 Dec 2023 to 30 Dec 2025 | 0.03% to 0.90%, +87bp | 0.0320% to 0.9008%, +87bp | Bundesbank monthly xlsx, Dec 2023 (sheet 29.12.2023) and Dec 2025 (sheet 30.12.2025), row DE0001030583 | match |
| T2 Interpolated nominal yield, same dates | 2.00% to 2.66%, +66bp | Feb 2033 and Aug 2033 Bunds interpolated to 15 Apr 2033: 1.999% to 2.662%, +66bp | same files | match |
| T2 Breakeven change | -21bp (1.97% to 1.76%) | 1.967% to 1.761%, -21bp | same | match |
| T3 Leveraged-fund net short, six contracts, end-2025 | -$1,154bn face | -1,154.3 (30 Dec 2025) | CFTC TFF futures-only raw file on disk, codes 042601, 044601, 043602, 043607, 020601, 020604, face $200k for 2Y and $100k for the rest | match |
| T3 Same, 29 Sep 2026 | -$774bn | -774.3 | same | match |
| T3 Same, 14 Jul 2026 | -$923.5bn | -923.5 | same | match |
| T3 Pre-March-2020 peak | -$612bn on 6 Aug 2019 | -612.1 on 6 Aug 2019 (series starts Jan 2018) | same | match |
| T3 Live API spot check, 10Y note, 29 Sep 2026 | long 510,579, short 2,547,011 | identical | CFTC Socrata gpe5-46if, anonymous call | match |
| T3 Ratio under C-129 | about 1.5x to 1.9x | 923.5/612.1 = 1.51; 1,154.3/612.1 = 1.89; 774.3/612.1 = 1.26 | same | match (29 Sep 2026 is 1.3x, below the stated range) |
| T3 Fed cross-check, three contracts gross short | n/a | 749.7bn on 30 Jul 2019 and 714.9bn on 9 May 2023, against the Fed's "$750 billion" and "nearly $715 billion" | FEDS Note 30 Aug 2023 (text via search result) against our raw file | match |
| T4 Beignet one-per-fund, 2026Q2 file and 2026Q3 file | $9.73bn and $9.72bn | 9.727 and 9.719 | data/nport/*_registrants.csv, sum of value_one_per_series | match |
| T4 CoreWeave one-per-fund | $2.73bn to $5.08bn | 2.730 to 5.076 | same | match |
| T4 Beignet on one as-of date | not in note | 31 Mar 2026: $8.76bn (222 filings); 30 Jun 2026: $8.73bn (252 filings) | data/nport/*_period_coverage.csv | new check, supports flat |
| T4 CoreWeave on one as-of date | not in note | 31 Mar: $1.10bn; 30 Jun: $2.35bn | same | new check, supports doubling |
| T4 36% of the deal | 9.7 / 27 | 9.72 / 27.294 = 35.6% (fair value over face) | S&P/IFR via search: $27.294bn issue | match, but the basis mixes fair value and face |
| T5 2024Q1 to 2026Q1 M&A retirement | $911.3bn | 911.32 | Fed EFA quarterly CSV fetched 11 Oct 2026 | match |
| T5 Same window net retirement | $704.0bn | 704.00 | same | match |
| T5 Ratio | 129.4% | 129.4% | same | match |
| T5 Old vintage in repo | 858.0 and 679.1 (126.3%) | 858.00 and 679.12 | data/supply_decomp/fed_efa/ | match (repo copy is the pre-18-Sep vintage) |
| T5 Offset Z.1 minus EFA net issuance | mean +5.3bn, correlation 0.993, 119 quarters | on the 46 quarters on disk (2015Q1 to 2026Q2): mean +6.0, sd 9.1, correlation 0.993 | data/z1_equity_netbuyers/ (FU103164105.Q) against the EFA CSV | correlation matches; 119 quarters not testable from the repo |
| T6 Annual mean c, 2023 and 2026 | 14.21 and 9.08 (down 36%) | 14.21 and 9.29 through 23 Sep (down 34.6%); 9.08 was to 12 Aug | data/history/collateral_multiplier_weekly.csv | match to 12 Aug; later data move it 1.5pp |
| T6 Imputed weeks | 154 of 704 | 154 of 704 | same | match |
| T6 Weeks with R_T under $100bn since 2022 | 12 | 12 (7 in Nov-Dec 2022, 5 in 2023); 21 more in 2015-17 | same | match |
| T7 NDFI draw range | $107bn to $297bn | 9.84% (6.42/65.24) and 27.29% (19.55/71.64) times $1,089.8bn = $107.2bn and $297.4bn | note's own rates; base from RV1 | match arithmetically |
| T7 Acharya-Steffen Table 4 | $336.6bn of $1,243.9bn (27.1%); AAA-A 8.71, BBB 33.00, non-IG 39.14, unrated 24.00 | identical; March alone 297,928 (24.0%) | NBER w27601 PDF, Table 4 printed p. 46 | match |
| T8 z_k(W2, M2) at 2026-06 and 2026-03 | 22.96% and 23.07% | 22.963% and 23.074% | _research/n2b_v2/zk_v2.csv inputs: W2 6,902.0 and 6,801.7; D1 23,155.2 and 22,676.1 | match |
| T8 W2 composition | W1 5,582.0 + hedge-fund reverse repo 1,320.0 | 6,902.0 | same | match |

## 2. ATTACKS

| target | strongest case against | evidence | verdict | what would settle it |
|---|---|---|---|---|
| 1 JGB duration supply | The "constant yields" frame fixes the 29 Dec 2023 curve, when the 10-year was 0.65%. At that yield, long issues carry inflated duration, so the measure over-weights long issues and over-states growth in rate risk. | Public face x years to maturity (an unpriced measure) grew +18.2% from end-2023 and +10.9% from Oct 2024, against +24.8% and +16.0%. Public face grew 28.6% and 20.6%. Exclusions are immaterial: JGBi ¥10.8trn and ¥9.2trn, retail ¥14.5trn and ¥22.5trn, STRIPS ¥0.26trn, against about ¥1,100trn. An observed end-2023 stock by issue was not found; the MoF Debt Management Report gives by-series stocks at fiscal year-end (31 Mar 2024, opened) and a redemption table by issue, which would bracket end-2023 better than the 2022 snapshot. | WEAKENED. Direction and rough size stand; the headline point estimate is curve-dependent by 5 to 7 points. | Re-run at a fixed 2026 curve, and report a range across fixed curves. Replace the interpolation with the MoF 31 Mar 2024 by-issue stock. |
| 2 German 2024-25 split | One linker is a thin market, and the nominal comparator is an interpolation between 2.3% and 2.6% coupon Bunds, while the linker has a 0.1% coupon. A rising liquidity or safety premium would show as a falling breakeven. | All three yields re-derive to the basis point. The 2030 and 2046 linkers agreeing in sign is in the note, not re-tested. Liquidity evidence is mixed: Finanzagentur says trading fell to €41bn in 2025 from €58bn (-29%); an SF Fed paper (Christensen et al., revised July 2026) finds neither safety premia nor trading conditions worsened after the Nov 2023 stop, though I could not confirm its sample end. No free direct evidence of a premium rise over 2024-25 was found. | STANDS as MEASURED on a fixed issue; BOUNDED attribution is the right grade. | A bid-ask or premium series for each linker through Dec 2025 (Bloomberg-type data, not free). |
| 3 CFTC and C-129 | The net short of leveraged funds is not the basis trade, and face (constant contract size) is not market value. The per-contract DV01s are second-hand. | Codes and face sizes verified against the Fed's description of six contracts and CFTC's own contract_units field. CME's current micro-futures page gives Ultra 10-Year $88 and Ultra T-Bond $204.68 DV01, against the script's $91 and $215; it does not touch the headline face figures. Net short record is -1,184bn on 12 Nov 2024. The 1.5x to 1.9x ratio re-derives; on gross shorts it is 1.6x. The likely source of 2.2-2.8x is a ratio to March-April 2020 levels, not the 2019 peak: 923.5 over weekly March 2020 values of 437, 385, 376, 354 and 343bn gives 2.1x to 2.7x. | STANDS (level and C-129 correction). | Quote the date and measure beside any ratio. |
| 4 N-PORT | Different as-of mixes across the two files, one fund family dominating, and fair value read as exposure. | On a single as-of date (31 Mar against 30 Jun) Beignet is $8.76bn and $8.73bn, so flat holds without the dedup rule. The 139 registrants in both quarters held $9.69bn then $9.39bn (-3%); the rest of the Q3 total is new entrants (170 against 146 registrants). PIMCO Funds is $6.2bn of $9.7bn (64%). CoreWeave doubles on every cut. Subsidiary groupings are supported by company releases: WULF Compute LLC issued $3.2bn of 7.75% notes (TeraWulf press release) and Cipher Compute LLC $1.4bn of 7.125% notes (via search). The debt-only rule keeps derivative (DE) lines named for the issuer; their size was not testable without raw rows. | STANDS | Re-run with the DE lines excluded, and on par value rather than fair value. |
| 5 EFA revision | The arithmetic is right, but the window stops at 2026Q1 while the Fed file now has 2026Q2. The "stable offset" and eREIT explanations are not shown. | Adding 2026Q2 (net +151.95, M&A 133.5) gives net -552.05 and M&A 1,044.8 over ten quarters, 189%. The Fed's own definition says EFA net "Equals series FA103164155.Q ... divided by 4", so the offset is between two Z.1 series codes, not between EFA and Z.1 methods. The offset is not stable by year: mean about +20 a quarter in 2021, +12.6 in 2022, about -2 to +4 in 2023-26. It is not seasonal (Q1 +9.1, other quarters +4.6 to +5.3). | WEAKENED. Claim of 129.4% STANDS; the offset story is unproven. | Read the Fed's series descriptions for FU103164105 and FA103164155. |
| 6 Collateral multiplier | The 2023 peak is a handful of thin year-end weeks; 2026 is partial; imputation is heaviest in the recent years. | Excluding weeks with R_T under $100bn, 2023 is 13.27 against 2026's 9.29 (-30%). Medians 13.07 and 8.71 (-33%). Ratio-of-sums 13.49 and 9.09. Imputed weeks since 2022 average c = 11.60 against 11.83 for published weeks. The 13-week peak, 22.0 in Jan 2023, would give -51%. Current c is still 25% above 2019-21 (7.4 to 7.95). | STANDS | A second source for SO and SI (an independent venue total) for the imputed 2025 weeks, 46 of 53. |
| 7 RV1 sizing | The low end is a public-firm utilization rate, not bank NDFI lines. The note's own cross-check, scaled to today's funded book, points to the top of the range, and the 35% of lines in warehouse and capital-call have no 2020 draw record. | Table 4 re-read: non-IG drew 39.14% and unrated 24.00%; applying 39.14% gives $427bn. The H.8 cross-check (+$82-92bn on about $600bn, +15%) applied to a funded book of about $1.7trn (secondary web source, not the Call Report) would be about $250bn. The 9.7% low end mixes a Y-14 sample numerator with an FSR denominator (the note admits this). The Call Report 12.7% fall in unused C&I commitments is a legitimate like-for-like anchor, but it is for nonfinancial borrowers. | WEAKENED. The 107-297bn range is a 2020-behaviour band, not a bound; its low end has no NDFI-specific anchor. | RC-L item 1.e.(3) by subtype for 2020Q1 and 2020Q2, if the bulk files carry it. |
| 8 z_k at 2026Q2 | A 0.11pp fall is smaller than routine revision. | Applying the +6bn Form PF revision to March alone gives 23.09, a fall of 0.13. The sign flips if June M2 is revised down by about $145bn (0.63%) or W2 up by $43bn (0.65%). The 40bn gap between the ALFRED and H.6 M2 vintages (23,155.2 and 23,115.2) is 0.03pp. The D1 and W2 columns carry no Z.1 input, so the D4 vintage mix does not touch the headline. | WEAKENED. The plateau stands; "a fall" is not distinguishable from zero. | Rebuild with the Aug 2026 ALFRED file on both quarters, and report the change with a band. |

## 3. OUTSIDE ESTIMATES

| figure | value | source | agrees with ours? |
|---|---|---|---|
| Leveraged-fund gross short, 2Y/5Y/10Y, July 2019 high | about $750bn | FEDS Note, 30 Aug 2023 (text via search result) | yes (our 30 Jul 2019: 749.7bn) |
| Same, 9 May 2023 | nearly $715bn | same | yes (714.9bn) |
| Leveraged-fund short futures "well over $1 trillion" at end-2023 | over $1tn notional | FEDS Note, 8 Mar 2024 (via search result) | not comparable (gross, market-value notional; our gross six-contract short at end-2023 was about $1.2tn face) |
| Select hedge funds net short, Dec 2023 | $1.04tn | CFTC staff paper, Mixon and Orlov (via search result) | not comparable (private position data, not the TFF class) |
| Net short "about $600 billion", comparable to 2019 and March 2020 | $600bn | BIS Quarterly Review box (via search result; date not confirmed) | not comparable, undated |
| Basis trade size, Sept 2023 | $260bn to $574bn | FEDS Note, 8 Mar 2024 | not comparable (basis trade, not futures net) |
| German linker trading volume | €41bn in 2025, from €58bn | Deutsche Finanzagentur page | yes, supports the liquidity caveat |
| German linker safety premium | average 0.33%; no worsening after the stop | SF Fed WP 2025-03 | not comparable; cuts against a large liquidity effect |
| Beignet Investor issue | $27.294bn, 6.581%, 2049 | S&P and IFR via search | yes |
| NDFI unused commitments, Q2 2026 | $1.09tn | tigzig.com (secondary; snippet only) | yes, secondary |
| Acharya-Steffen drawdown rates | 27.1% total; 8.71/33.00/39.14/24.00 | NBER w27601 Table 4 (opened) | yes. A search summary gave different figures (6.01/23.04/26.63/12.29) which the paper does not support. |
| Fed EFA, 2026Q2 | net +151.95bn, M&A 133.5bn | Fed EFA CSV | not in the note |

## 4. OVERCLAIMS OR GRADE ERRORS

| file:line | what the note says | what the evidence supports |
|---|---|---|
| 2026-09-27-R3-JGB-And-Euro-Area-Bonds.md, follow-up of 8 Oct, the "+16.0%" and "+24.8%" bullets | a quarter more rate risk "at constant yields" | direction holds; size depends on the fixed curve (+10.9% to +16.0% from Oct 2024 on two measures); say "10.9-16.0%" or state the curve |
| 2026-09-13-S1-Supply-Decomposition.md, item 2 of the open list (the 9 Oct RESOLVED banner) | "a stable offset" explains the gap | offset swings from about +20 a quarter (2021) to about 0 (2024-25); eREIT cause "likely" is unproven, and EFA net is by definition the Z.1 FA series divided by 4 |
| 2026-09-13-S1-Supply-Decomposition.md, item 1 of the same list | EFA "ends at 2026:Q1" | the Fed file now carries 2026Q2 (net +151.95bn); the 9-quarter window is stale |
| CORRECTIONS.md, C-108 update of 9 Oct | window 2024Q1 to 2026Q1, 129.4% | arithmetic right; with 2026Q2 it is 189% over ten quarters, and net issuance has turned positive in 2026 |
| 2026-09-27-RV1-Drawdown-Sizing.md, "The answer" | the sizing as a range | a 2020-behaviour band; the 9.7% and 9.8% low ends have no NDFI-line anchor; H.8 cross-check scaled to today suggests about $250bn |
| 2026-08-31-N2b-zk-The-Wholesale-Share.md, update of 4 Oct | "a fall of 0.11pp" | within revision noise (a $145bn M2 revision flips it); describe as a plateau |
| bin/pull_cftc_tff.py docstring, DV01 notes | primary DV01 set is CME's January 2024 worked example | CME's current page gives Ultra 10Y $88 and Ultra Bond $204.68; the script's $91 and $215 are close; only affects the 10-year-equivalent columns |
| CORRECTIONS.md, C-129 | "2.2 times is the 10-year contract's post-2020 peak" | the ratio 2.1x to 2.7x also fits 2026 positions against March 2020 weekly levels; that may be the original basis (INFERRED) |

## 5. LOAD-BEARING ASSUMPTIONS

| target | assumption that sinks it if wrong |
|---|---|
| 1 | Holding the end-2023 yield curve fixed is a neutral way to isolate quantity; at 0.65% it inflates long-issue duration |
| 2 | One linker's breakeven against an interpolated higher-coupon nominal isolates inflation compensation, i.e. the linker safety and liquidity premium did not rise |
| 3 | Leveraged-fund net short at constant contract face is comparable over 2019-2026 (it ignores price level and counts directional shorts as basis trade) |
| 4 | Fair value of lines matched by name and CUSIP is the exposure, with nothing material missed under other names or CUSIPs |
| 5 | The Z.1-minus-EFA offset is a stable definitional gap (eREITs), not a changing series concept |
| 6 | R_T = SO - SI, the thin difference of two large legs, is a stable measure of the collateral base across venues and the 2022 data change |
| 7 | March 2020 draw rates, built under a Fed backstop, transfer to warehouse and capital-call lines that were not drawn then |
| 8 | Quarter-on-quarter changes of 0.1pp in z_k are measurable given M2 and Form PF revisions |

## 6. CITATIONS CHECKED

| source | opened? | says what I cite? |
|---|---|---|
| Bundesbank monthly xlsx, Dec 2023 (bundesbank.de, blob 901932) | yes, parsed | yes |
| Bundesbank monthly xlsx, Dec 2025 (blob 947258) | yes, parsed | yes |
| NBER w27601, Acharya and Steffen (nber.org PDF) | yes, Table 4 read | yes (the search summary's different rates are wrong) |
| Fed EFA quarterly CSV (federalreserve.gov/releases/efa) | yes | yes |
| CFTC Socrata API gpe5-46if, one row | yes | yes |
| MoF Debt Management Report FY2023, by-name tables (mof.go.jp, 2023nenpou04.pdf) | yes, text extracted, tables located; not used numerically | yes: stock by series and a by-issue redemption table at FY-end |
| Bundesbank prices-and-yields index page | yes | yes (monthly xlsx per month) |
| Deutsche Finanzagentur inflation-linked page | search-result text only | yes |
| SF Fed WP 2025-03 / Banque de France DT1012 | search-result text only | yes on "neither ... negatively impacted"; sample end not seen |
| FEDS Note 30 Aug 2023; FEDS Note 8 Mar 2024 | search-result text only | yes |
| BIS Quarterly Review box on margin leverage | search-result text only | yes; date not seen |
| CFTC staff paper (Mixon and Orlov) | search-result text only | yes |
| CME micro Treasury futures page | search-result text only | yes; the CME DV01 primer PDF text read via snippet only |
| S&P Global Ratings and IFR on Beignet; stillhousedata | search-result text only | yes |
| TeraWulf press release; sec.gov filings for WULF Compute and Cipher | search-result text only; sec.gov not opened per the rules | yes for the notes and amounts |
| tigzig.com Q2 2026 NDFI post | search-result text only | secondary; not primary |

## 7. OBSERVED vs INFERRED, then UNCERTAIN

| item | status | what would settle it |
|---|---|---|
| All re-derived figures in section 1 | OBSERVED (recomputed from files or live source) | n/a |
| Likely basis of the old 2.2-2.8x (ratio to March 2020 levels) | INFERRED from arithmetic | the author of the original claim |
| 2026Q2 EFA row timing and revision status | OBSERVED in file fetched 11 Oct; publication date not confirmed | Fed release calendar |
| UNCERTAIN: whether eREITs cause the Z.1-EFA offset | open | Fed series descriptions for the two codes |
| UNCERTAIN: SF Fed paper sample end | open | read the paper's data section |
| UNCERTAIN: D4 vintage mix in target 8 | not tested; needs the Sep 2026 Z.1 zip | rebuild z1.csv from one release |
| UNCERTAIN: the Q2 2026 RC-L figure $1,089.8bn | not re-read at source (bulk download not tried); a secondary source gives $1.09tn | FFIEC or FDIC Call Report file |
| UNCERTAIN: the 119-quarter offset statistics | repo holds 46 quarters of Z.1; not reproduced | full Z.1 FU103164105.Q history |
| UNCERTAIN: DE lines inside the N-PORT debt-only rule | raw rows not in repo | rerun with DE excluded |
| UNCERTAIN: whether linker liquidity premia rose in 2024-25 | no free direct series found | a bid-ask history |
| NOTE: the handover integrity check shows a mismatch against the 9 Oct 18:42:45 stamp (ask 21 against 20, series 562 against 559). Read as later commits (E-020 and H.8 data); the principal approved proceeding. | known | n/a |
