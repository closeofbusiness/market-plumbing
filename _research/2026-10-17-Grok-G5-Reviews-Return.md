# Grok (Cursor CLI) batch g5, 17 Oct 2026: outside reviews of R2b, ST1 and the Brent claims, and the N-PORT–Z.1 gap
*Four parcels went to Grok 4.7 (256k, extra-high) through `orchestrator_cursor`, each in a fresh stage behind the read-and-web-only fence. All four ended SUCCESS, with no fence breaches, no blocked attempts, no unexpected tools and no stage changes. The returns are claims until checked; the supervisor's check is at the head of each. Quotes longer than 15 words were cut to twelve words.*

---

## Parcel 1: Adversarial review of R2b (registered funds and Treasury duration)

*Status SUCCESS; 878 s; 16 fetches; cited but not fetched: 1.*

**Supervisor check.** Arithmetic re-confirmed. Money-fund Treasury stock re-read at Z.1 S.123 (2,269.5 and 3,281.6). One URL cited without a fetch (a table page for the ~$2bn closed-end row) is not relied on. Changes: R2b outside-review section; page R2b sentence notes the line is close to pro-rata.

### 1. Claims

**CLAIM:** “ΔS, end-2023 to 30 Jun 2026 … $549.2bn”
**VERDICT:** STANDS
**REASON:** Base 10-year equivalents rise from 1,387.745524 to 1,936.986234, so ΔS is 549.24071 on a public denominator of 3,218.3. Matched vintage is 568.3 and the 30 Jun 2026 curve is 517.1; both stay above 460.
**SOURCE:** `tsy_verdict.csv`, `measured_ds_bn`; `tsy_windows.csv` base rows 2023Q4 and 2026Q2
**QUOTE:** “measured_ds_bn,549.24071”
**UNCERTAIN:** none on the arithmetic. The figure is par times a fixed-curve factor, not market-value DV01.

**CLAIM:** “Z.1-scaled arm … $449.7bn”
**VERDICT:** STANDS
**REASON:** P1 rescales each end by Z.1’s three-row Treasury market value over N-PORT value: 449.734802, which is 14.0% of 3,218.3. It misses 460 by 10.3.
**SOURCE:** `tsy_verdict.csv`, `z1scaled_p1_ds_bn`; `tsy_change.csv` row P1 full
**QUOTE:** “z1scaled_p1_ds_bn,449.734802”
**UNCERTAIN:** none on the product. The duration of the $131bn market-value gap is assumed, not read.

**CLAIM:** “The two arms straddle the first-order line.”
**VERDICT:** WEAKENED
**REASON:** 549.2 is above 460 and 449.7 is 10.3 below it, so the pre-registered labels differ. Both shares, 17.1% and 14.0%, sit against a 14.5% starting share of the same 3,218.3. The hurdle is one-seventh, 459.76, only about $8bn under a pro-rata 468. Clearing it mostly restates that the holder is ordinary size. The $99bn arm gap is the average book factor, about 0.75, applied to an unidentified value gap.
**SOURCE:** `tsy_verdict.csv`, `line_first_order_bn` and `verdict`; note, “The verdict lines”
**QUOTE:** “If the arms disagree, the verdict is not established.”
**UNCERTAIN:** A maturity split of the N-PORT–Z.1 wedge would settle whether 449.7 is a real second measurement.

**CLAIM:** “The excess over pro-rata has no established sign”
**VERDICT:** STANDS
**REASON:** Measured excess is +2.52pp, +$81bn, on starting share 14.548% of 9,539.1. P1 excess is −1.26pp, −$41bn, on a scaled starting share of 15.235%. The sign flips; the amounts are small next to 3,218.3.
**SOURCE:** `tsy_change.csv`, M0 full and P1 full, columns `excess_pp` and `excess_bn`
**QUOTE:** “sign not established (the arms differ)”
**UNCERTAIN:** none.

**CLAIM:** “10-year equivalents at the fixed end-2023 curve”
**VERDICT:** WEAKENED
**REASON:** The unit matches R2’s denominator, so the 17.1% share is the right share of that object. Inside the fund book the factor is 10-year equivalents divided by par (checks: 10-year factor 1, 30-year 2.1059). Coupon value beyond ten years rose only $131bn of a $788bn value increase, 17%, and par rose $154bn of $804bn, 19%. The same fixed-curve exercise on 30 Jun 2026 cuts measured ΔS from 549.2 to 517.1 and leaves the share at 17.0% of a rebuilt 3,047.4.
**SOURCE:** `tsy_checks.csv` row C9; `tsy_buckets.csv` coupons 10–20 and 20+ at 2023Q4 and 2026Q2; `tsy_change.csv` row M8 full
**QUOTE:** “10y/2y/30y fixed-curve par-bond factors”
**UNCERTAIN:** Public par and market value by bucket are not in these files, so the par-versus-market bias in r is not re-derived. Same-CUSIP prices would cancel; only mix differences would remain.

**CLAIM:** “Where it sat: mostly beyond ten years.”
**VERDICT:** WEAKENED
**REASON:** Coupon 10-year equivalents beyond ten years are 52.9% of measured ΔS and 52.1% of the starting stock, so the increase follows the old mix. The funds’ share of the public’s long-coupon stock slipped from 16.8% (722.8 / 4,309.8) to 16.5% (1,013.4 / 6,132.5). They took 15.9% of the public’s new long-coupon 10-year equivalents (290.7 / 1,822.6), close to their 17.1% of all new duration.
**SOURCE:** `tsy_buckets.csv`, 2023Q4 and 2026Q2, `coupons` `10-20` and `20+`
**QUOTE:** “it largely reflects the funds' existing maturity mix.”
**UNCERTAIN:** none on these buckets. TIPS and STRIPS beyond ten years would raise the fund-book share toward 60%; that is a wider cut than the sentence the note computes.

**CLAIM:** “In the first half of 2026 … a fifth and three-tenths”
**VERDICT:** STANDS
**REASON:** 162.1 / 556.1 = 29.2% and 125.7 / 556.1 = 22.6%, against a 14.5% stock share at the start of the half. Absolute measured ΔS was +38 in 2025H1, +146 in 2025H2, and +162 in 2026H1, so the level break is mid-2025. The published 15.4% for calendar 2025 averages those halves. Quarterly public ΔP is not in the tables, so a 2025H2 share is not identified.
**SOURCE:** `tsy_change.csv` rows M0 and P1 `2026H1`; `tsy_windows.csv` base `tenyeq_fixed_bn` at 2024Q4, 2025Q2, 2025Q4, 2026Q2
**QUOTE:** “2026H1 … 0.291501” and “0.226013”
**UNCERTAIN:** The half-year public path inside 2025. A quarterly public 10-year-equivalent series would settle it.

**CLAIM:** “the funds' share of the added risk rose through the window”
**VERDICT:** WEAKENED
**REASON:** The three published flow shares do rise: measured 13.9%, 15.4%, 29.2%, and scaled 10.3%, 14.4%, 22.6%, each over that period’s ΔP (1,464.5, 1,197.7, 556.1). The stock share was flat at 14.5% through end-2025 and 15.2% at 30 Jun 2026. 2026H1 measured excess, +$81bn, equals the whole-window measured excess because 2024 and 2025 cancel.
**SOURCE:** `tsy_change.csv`, M0 and P1 period rows; `tsy_windows.csv` `share_of_public_fixed`
**QUOTE:** “Both agree on the direction.”
**UNCERTAIN:** none on the three bins.

**CLAIM:** “Money-market funds are outside it.”
**VERDICT:** STANDS
**REASON:** Z.1 puts money funds on S.123, not in the three rows used here. Their Treasury stock rose from $2,269.5bn at end-2023 to $3,281.6bn at 2026Q2, a +$1,012bn value change larger than N-PORT’s +$788bn. Rule 2a-7 keeps that book inside about 60 days. At the file’s bill factor of about 0.02, the duration change is on the order of $20bn, under 1pp of 3,218.3. Even a 0.05 factor is about $51bn.
**SOURCE:** `tsy_windows.csv` does not contain money funds; Fed S.123.s line 6, fetched this session
**QUOTE:** “average maturity of a fund's portfolio to 60 days”
**UNCERTAIN:** Money-fund 10-year equivalents are not measured here. N-MFP maturities would settle the $20bn estimate.

**CLAIM:** “registered funds filing Form N-PORT” scaled to three Z.1 rows
**VERDICT:** WEAKENED
**REASON:** The September 11, 2026 Z.1 levels match the file to the million: mutual funds $1,741.237bn and ETFs $807.612bn at 2026Q2; closed-end Treasuries stay near $2bn. Interval funds are a separate sector, S.124.6, and that table has no Treasury line. The scale still divides by N-PORT market value. Mutual-fund bills were $12.830bn at end-2023 and $12.960bn at 2026Q2, while N-PORT bills were $188bn then $371bn. The wedge is not a miniature of the whole book, whose 10-year equivalents per dollar are about 0.75.
**SOURCE:** `tsy_windows.csv` `z1_mf_bn`, `z1_etf_bn`, `z1_cef_bn`, `nport_over_z1`; Fed S.124.1–S.124.3 and S.124.6
**QUOTE:** “hedge funds are not included”
**UNCERTAIN:** How much of the $85bn start shortfall and $46bn end excess is fiscal-month timing. Only about half the funds report in the quarter-end month (`funds_m0` 6,415 of 12,609, then 6,923 of 13,799). A pure quarter-end rerun would settle it.

**CLAIM:** “Treasury futures held by funds are not measured”
**VERDICT:** WEAKENED
**REASON:** Leaving futures out of cash ΔS is the right match to a cash ΔP of 3,218.3. The note’s relayed rise of about $120bn is not in these tables. Added only to the numerator it would lift the scaled arm from 449.7 to about 570, through the 460 line. A May 2024 Fed note, data through 2023Q4, puts mutual-fund futures near $500bn notional and only 7% of portfolio DV01 against 31% from Treasury securities, with the mutual-fund increase in 2- and 5-year contracts.
**SOURCE:** note, “What this does and does not establish”; `tsy_verdict.csv` `futures`
**QUOTE:** “futures contribute just 7 percent”
**UNCERTAIN:** The 2024–2026 change in futures 10-year equivalents. An N-PORT futures rerun on the same curve would settle whether +$120bn is real.

**CLAIM:** ETFs held by other funds would change the answer
**VERDICT:** WEAKENED
**REASON:** Z.1 records ETF Treasuries on S.124.3 and mutual-fund holdings of fund shares as equities, and ICI drops funds of funds from totals to avoid double counting. N-PORT likewise reports the ETF’s bonds on the ETF’s form. An end-point excess of N-PORT over Z.1 of $45.5bn (2,596.4 − 2,550.9) is the entire room for a look-through double count, and P1 already scales it away. It does not stack on top of the scaled arm.
**SOURCE:** `tsy_windows.csv` 2026Q2 base `tsy_value_bn` 2596.382843 and `z1_sum_bn` 2550.863; ICI 2026 Fact Book, “Methods and Assumptions”
**QUOTE:** “Funds of funds are excluded from the data”
**UNCERTAIN:** Master-feeder pairs that both report the same Treasuries. The tables have no feeder flag.

**CLAIM:** “It is a holding share, not a price effect.”
**VERDICT:** STANDS
**REASON:** The files define r as a holder share of cash Treasuries on a frozen curve. They do not say fund buying moved yields.
**SOURCE:** `tsy_verdict.csv`, `holder_share_not_price_effect`; note, “What this does and does not establish”
**QUOTE:** “Nothing here says that fund buying moved yields.”
**UNCERTAIN:** none.

### 2. External checks

| Figure | Date and units | URL fetched | Against the files |
|---|---|---|---|
| Mutual funds, Treasury securities, $1,741,237 million | 2026Q2, market value, not seasonally adjusted | https://fred.stlouisfed.org/series/BOGZ1LM653061105Q | Matches `z1_mf_bn` 1741.237. Q4 2025 $1,685,159 million matches 1685.159. S.124.1 rounds 2023 to 1389.7 against the file’s 1389.718. |
| ETFs, Treasury securities, $807,612 million | 2026Q2, market value | https://fred.stlouisfed.org/series/BOGZ1LM563061103Q | Matches `z1_etf_bn` 807.612. Q4 2025 $705,991 million matches 705.991. S.124.3.s shows 2023 at 502.3 against 502.261. |
| Closed-end Treasury securities, about $2.0bn | 2023–2026Q2, market value | https://www.federalreserve.gov/releases/z1/20260911/html/S124_2_s.htm | Matches a ~$2bn closed-end row. Too small to move ΔS. |
| Mutual-fund bills $12,830 million (end-2023) and $12,960 million (2026Q2); other Treasuries $1,376,888 million and $1,728,277 million | Levels, millions | https://fred.stlouisfed.org/series/BOGZ1LM653061113A and https://fred.stlouisfed.org/series/BOGZ1LM653061125Q | Bills plus other equal the file’s mutual-fund Treasury total. Mutual-fund Treasury growth is notes, bonds, TIPS, and FRNs, not bills. Z.1 still has no maturity past “ex-bills,” so it does not confirm the 53% long-coupon split. |
| Money-market Treasury securities $2,269.5bn (2023) and $3,281.6bn (2026Q2) | Z.1 S.123.s line 6, billions | https://www.federalreserve.gov/releases/z1/20260911/html/S123_s.htm | Absent from the files, as the note says. Dollar change +$1,012bn; duration change is small under rule 2a-7. |
| ICI: investment companies held 19% of Treasury and agency securities at year-end 2025; long-term mutual funds 6%, money funds 11%, other registered 2%. The 6% long-term share is unchanged in 2023, 2024, and 2025 | Year-end, share of market value, Treasuries plus agencies | https://www.icifactbook.org/pdf/2026-factbook.pdf | Does not confirm 14.5% of Treasury 10-year equivalents. The flat long-term share through 2025 agrees with the file’s flat 14.5% stock share through end-2025. No 2026H1 figure. ICI’s 98% coverage line and fund-of-funds exclusion are the population caveat above. |
| TBAC investor profile: money funds $3,232bn, ETFs $676bn, “Federal Reserve as of 9/30/2025” | Holdings, billions, 30 Sep 2025 | https://home.treasury.gov/system/files/221/TBACCharge2Q12026.pdf | Money funds match S.123 2025Q3 ($3,232.4bn). ETFs match S.124.3 ($674.9bn). The slide’s mutual-fund cell reads $1,576bn against Z.1’s $1,641.2bn; the extracted columns are jammed, so that cell is not a clean disagreement. |
| Mutual funds held roughly $500bn of Treasury futures notional at 2023Q4; futures were 7% of portfolio DV01 and cash Treasuries 31%, in a Treasury-fund sample | Notional and DV01 shares, through 2023Q4 | https://www.federalreserve.gov/econres/notes/feds-notes/why-do-mutual-funds-invest-in-treasury-futures-20240510.html | Does not measure the note’s relayed +$120bn over 2024–2026. It says futures DV01 was the smaller piece at the window’s start, and mutual-fund growth was in shorter contracts. |
| Interval and tender-offer funds, assets $160.1bn (2023) to $320.6bn (2026Q2); debt line is municipals plus corporate and foreign bonds only | Billions | https://www.federalreserve.gov/releases/z1/20260911/html/S124_6_s.htm | No Treasury line. They do not explain the $131bn gap. |

### 3. The single weakest point

The published verdict treats a $10.3bn miss as a veto. Measured holdings clear $460bn by $89bn. The scaled arm misses by $10.3bn only because each end is multiplied by Z.1 market value over N-PORT market value. That ratio moves from 95.5% to 101.8%, and the $131bn difference in growth, times the book’s roughly 0.75 10-year equivalents per dollar, is the whole $99bn gap between 549 and 450. Z.1 itself shows mutual-fund bills stuck near $13bn while N-PORT bills run from $188bn to $371bn, so the missing dollars are a poor candidate for the book’s average maturity. The pre-registered rule then converts that assumption into “NOT ESTABLISHED.” What the two arms actually agree on is narrower and firmer: about 14% to 17% of the new 10-year equivalents, within a couple of points of the 14.5% starting share, with a higher flow share in the last three half-years than in early 2025.

### 4. Not done

The SEC zips are not in this folder, so the line-by-line build was not rerun. The relayed futures increase of about $120bn and the verifier floor of $443bn are not in the committed tables. The Treasury Bulletin OFS-2 API returned no rows for “Mutual funds,” and the bulletin PDFs did not yield a clean ownership cell. No outside source found here publishes registered-fund Treasury 10-year equivalents for 2024–2026; the Fed futures note stops at 2023Q4. Public par and market value by maturity are not in these files, so a market-value DV01 version of ΔP was not computed. A quarter-end-only fund subset and a master-feeder flag are not in the tables. The annual bill series page is dated 11 Jun 2026 while the other Z.1 pages are 11 Sep 2026; those bill levels still add to the September mutual-fund total, and a later bill revision was not separately visible.

---

## Parcel 2: Adversarial review of ST1 (swap tape), with external levels

*Status SUCCESS; 740 s; 15 fetches; cited but not fetched: 0.*

**Supervisor check.** The Treasury Borrowing Advisory Committee quote (sb0213: 10y at -53bp, July 2025) was re-read at source. The St. Louis Fed page refused the supervisor's scripted request, so its averages stay relayed. Changes: ST1 outside-review section; page swap sentence now says April-September 2025 and cites the committee.

### 1. Claims

**CLAIM:** “negative at every maturity, least so at the short end”  
**VERDICT:** STANDS  
**REASON:** Every monthly median in the file is negative, and the 2-year is the least negative in every month. From 14–31 Oct 2024 to 1–13 Oct 2026 the medians move from −20.32, −32.83, −47.49 and −82.25 to −13.75, −28.50, −39.20 and −66.38, a net 6.6, 4.3, 8.3 and 15.9bp on 9, 13, 13 and 13 days against 7, 8, 8 and 8 days. The 30-year was negative on all 481 days with a figure.  
**SOURCE:** `st1_monthly_medians.csv` rows 5–8 and 246–249; `summary.csv` row 6  
**QUOTE:** “share_30y_quoted_spread_negative,1.0000,481”  
**UNCERTAIN:** none for these rows. The 13 Oct 2026 prints (−38.9 at 10y, −65.2 at 30y) are not in either file.

**CLAIM:** “most negative single days were in April 2025”  
**VERDICT:** WEAKENED  
**REASON:** Those days and the prints −29.5, −42.2, −58.5 and −93.4 are not in the monthly file. April’s own medians, −53.59 at 10y (20 days) and −86.33 at 30y (20 days), are inside the sample, not at the edge. The most negative months are July 2025 at 10y (−55.10, 21 days) and May 2025 at 30y (−88.12, 20 days).  
**SOURCE:** `st1_monthly_medians.csv` rows 67, 69, 78, 96  
**QUOTE:** “2025-07,swap_spread_quoted_bp,10,21,-55.10”  
**UNCERTAIN:** a daily ledger would settle whether 8 Apr and 21 Apr 2025 were the single-day lows.

**CLAIM:** “The narrowing began in October 2025, and it was not one-way.”  
**VERDICT:** WEAKENED  
**REASON:** The quoted path matches the file: −53.04, −47.33, −43.80, −39.63, −37.40 from Sep 2025 through Jan 2026 (21, 22, 17, 19 and 20 days). The sustained step is October, 5.7bp on 21 then 22 days. July is still the trough (−55.10, 21 days), and August had already moved 2.3bp, to −52.77 on 21 days. The reversal is real: March 2026 is −46.88 on 22 days, 0.5bp from October 2025’s −47.33.  
**SOURCE:** `st1_monthly_medians.csv` rows 96, 108, 120, 126, 156, 174  
**QUOTE:** “2026-03,swap_spread_quoted_bp,10,22,-46.88”  
**UNCERTAIN:** none on the monthly path. An external print dates a daily turn to 15 July 2025 (below).

**CLAIM:** “30-year went past its October level: −80 against −75”  
**VERDICT:** WEAKENED  
**REASON:** October 2025 is −75.10 on 21 days and March 2026 is −79.48 on 22 days, so the 30-year did cheapen past its October level by 4.4bp. The printed “−80” is 0.5bp past the median, which rounds to −79.  
**SOURCE:** `st1_monthly_medians.csv` rows 128 and 176  
**QUOTE:** “2026-03,swap_spread_quoted_bp,30,22,-79.48”  
**UNCERTAIN:** none.

**CLAIM:** “widest monthly medians were July 2025 … and May 2025”  
**VERDICT:** STANDS  
**REASON:** July 2025 is the most negative 10-year month at −55.10 (21 days). May 2025 is the most negative 30-year month at −88.12 (20 days). No other month in the 25-month file is wider.  
**SOURCE:** `st1_monthly_medians.csv` rows 78 and 96  
**QUOTE:** “2025-05,swap_spread_quoted_bp,30,20,-88.12”  
**UNCERTAIN:** none.

**CLAIM:** “Day-to-day changes in the 10-year spread have a standard deviation of 1.2bp (469”  
**VERDICT:** STANDS  
**REASON:** The file gives 1.208bp on 469 pairs, 0.932bp on the 185 pairs where the 10-year Treasury moved 2bp or less, a slope of −0.084 on 469 pairs, and a share of 1.0 under 10bp on those 469 pairs. The 10-year headline clears ten trades on 0.9719 of 498 Treasury days.  
**SOURCE:** `summary.csv` rows 5, 11–14  
**QUOTE:** “dod_sd_quoted_bp_10y,1.208,469”  
**UNCERTAIN:** none.

**CLAIM:** “about +13bp at 10 years now, within +12 to +22bp”  
**VERDICT:** STANDS  
**REASON:** October 2026 is +13.45 on 8 days. Across 25 months the 10-year gap runs from +11.92 (March 2026, 22 days) to +22.30 (November 2024, 13 days). The 5-year runs from −4.21 to +25.53, and the 30-year from +9.77 (April 2025, 12 days) to +23.00 (December 2025, 7 days). Summing the 30-year month counts gives 240 days.  
**SOURCE:** `st1_monthly_medians.csv` rows 4, 14, 146, 178, 244  
**QUOTE:** “2026-10,cpi_gap_fisher_bp,10,8,13.45”  
**UNCERTAIN:** none on the medians. Part of the 30-year gap is par-versus-zero curve shape, as the README states; these files do not split that piece out.

**CLAIM:** “low from January to April and high from June to October, in both years”  
**VERDICT:** WEAKENED  
**REASON:** The March troughs match: −3.35 in March 2025 (17 days) and −4.21 in March 2026 (22 days). August–October 2025 are +21.78, +22.31 and +22.33 (20, 21 and 21 days). April 2025 breaks the low window: +8.65 on 18 days, against −3.35 the month before. The 2026 “high” season peaks at +17.98 (August, 21 days), about 4bp under 2025.  
**SOURCE:** `st1_monthly_medians.csv` rows 55, 66, 110, 122, 178, 230  
**QUOTE:** “2025-04,cpi_gap_fisher_bp,5,18,8.65”  
**UNCERTAIN:** the note already marks the seasonal reading as a hypothesis. Two seasons cannot separate a calendar effect from a one-off.

**CLAIM:** “dollar-borrowing premium against the yen has roughly halved”  
**VERDICT:** WEAKENED  
**REASON:** The pooled medians do halve: −47.50 on 9 days in Oct 2024 to −22.38 on 7 days in Oct 2026, a remaining share of 22.38/47.50. Half of −47.50 is −23.75, and September 2026 is the first month through it, at −23.56 on 17 days; August is −24.25 on 18 days. The project’s own README says this pool mixes maturities and should be read as a level, not a change. The per-tenor defense is not in this file.  
**SOURCE:** `st1_monthly_medians.csv` rows 12, 228, 240, 252; `swap_tape_README.md` lines 108–110  
**QUOTE:** “Read it as a level, not as a change”  
**UNCERTAIN:** average maturity “2.5 to 3.6 years,” and the 1y/3y/5y paths, are not in these files. A per-tenor file would settle the mix.

**CLAIM:** “against the euro and sterling it is near zero”  
**VERDICT:** WEAKENED  
**REASON:** Sterling’s latest median is +2.44 on 7 days, with a sample high of +6.31 (December 2025, 14 days). The euro’s latest median is −4.38 on 9 days, against −4.69 on 13 days in Oct 2024. January 2026 was −0.44 on 21 days; October 2026 has given that back. “Near zero” fits sterling and early-2026 euro, and it overstates the latest euro print.  
**SOURCE:** `st1_monthly_medians.csv` rows 10, 160, 250, 251  
**QUOTE:** “2026-10,xccy_pool1to5_bp_EURUSD,1-5,9,-4.38”  
**UNCERTAIN:** none on the medians.

**CLAIM:** “Nothing here says that a flow caused a spread to move.”  
**VERDICT:** STANDS  
**REASON:** The note, the README, and the regulation paragraph all measure the spread and date a rule. They do not say a flow moved a price. The files do not make that error.  
**SOURCE:** `2026-10-15-ST1-Swap-Spreads-Inflation-Gap-And-Basis.md` lines 67–69 and 122–123; `swap_tape_README.md` line 3  
**QUOTE:** “It does not say that any flow moves any price.”  
**UNCERTAIN:** the 1 Jan 2026 and 1 Apr 2026 rule dates are attributed to a speech outside this folder.

**CLAIM:** “executed between 14:30 and 16:30 New York time”  
**VERDICT:** WEAKENED  
**REASON:** The window is a real filter, and the note’s own whole-day gap has a stated standard deviation of 1.8bp and a stated peak of 7.8bp, larger than the 2bp resolution and larger than several monthly steps. Those window diagnostics are not in `summary.csv`. Monthly 10-year levels still match external snapshots within about 2bp, so the window is not inventing the path.  
**SOURCE:** the note, lines 27–31; `swap_tape_README.md` lines 77–78  
**QUOTE:** “reaches 7.8bp, on 18 Dec 2024”  
**UNCERTAIN:** the 0.4bp, 1.8bp and 7.8bp window gaps are not recomputed in the two CSVs.

**CLAIM:** “one trading platform is excluded from the headline”  
**VERDICT:** WEAKENED  
**REASON:** BILT is dropped because, on 13 Oct 2026, its 10-year rows sat 61.7bp below the rest. The README says what BILT denotes has not been read from the CFTC specification. These files contain no BILT share and no all-platforms monthly path, so the filter’s effect on the 25-month history is unmeasured here.  
**SOURCE:** `swap_tape_README.md` lines 77–78 and 116–117  
**QUOTE:** “10y rows sat 61.7bp below the rest”  
**UNCERTAIN:** whether BILT was that far off on any day besides 13 Oct 2026.

**CLAIM:** “A bond-equivalent version … is 1–2bp less negative.”  
**VERDICT:** WEAKENED  
**REASON:** The quoted-minus-Treasury headline is a mixed convention: an ACT/360 swap rate against a semiannual Treasury par yield. The 1–2bp bond-equivalent gap is not in either CSV. It is too small to explain a 25bp disagreement with the St. Louis Fed average, and too small to close the 4–5bp 30-year gaps versus 2026 dealer asset-swap snapshots below.  
**SOURCE:** the note, lines 32–33; `swap_tape_README.md` lines 55–58 and 89  
**QUOTE:** “Day-count code A004 is read as ACT/360”  
**UNCERTAIN:** the 1–2bp figure itself is not in the CSVs. The README only asserts the adjustment is at most 3bp.

**CLAIM:** “It is published as a pooled 1–5-year median.”  
**VERDICT:** WEAKENED  
**REASON:** There is no time window and no platform filter on the cross-currency rows, and a single tenor is published only on days with at least ten trades. The October yen endpoints have 9 and 7 days. US-reported trades omit other repositories; that limit is disclosed. The one like-for-like external euro print, below, still matches the pool.  
**SOURCE:** the note, lines 38–40 and 123; `swap_tape_README.md` lines 80 and 108–110  
**QUOTE:** “Trades reported to other regulators' repositories are not in it.”  
**UNCERTAIN:** the share of global yen basis volume that never reaches the CFTC tape.

### 2. External checks

Compared with the monthly median for the same month. Same-tape pages are identified as such.

| Figure | Date, tenor, units | URL fetched | Against the file |
|---|---|---|---|
| TBAC: 10-year Treasury–SOFR spread −53bp, with Treasuries described as having cheapened | Letter of 30 Jul 2025; “currently”; bp | https://home.treasury.gov/news/press-releases/sb0213 | Agrees. July 2025 median −55.10 on 21 days; gap 2.1bp. |
| Bloomberg via Tradition: 2y −25, 10y −56, 30y −87, swap minus Treasury | 15 Jul 2025; bp | https://www.tradition.com/media/365113/mml4_tradition.pdf | Agrees with the July medians −24.30 (9 days), −55.10 (21), −85.80 (21). Gaps 0.7, 0.9 and 1.2bp. A single day against a month. |
| Same letter: 10-year turning point on 15 Jul 2025, after the April tariff shock | 15 Jul 2025 | same PDF | The monthly trough is July (−55.10), and the large step is October (−53.04 to −47.33). |
| St. Louis Fed, Bloomberg LIBOR and SOFR: 2025 average 10y −26bp, 5y −13bp, swap minus Treasury | Averages, data retrieved 24 Sep 2025; table row “2025”; bp | https://www.stlouisfed.org/on-the-economy/2025/oct/are-u-s-treasuries-still-convenient | Disagrees. Unweighted average of the 2025 monthly medians through September is about −50.5 at 10y and about −33.5 for the full-year 5y medians. Gaps are about 25bp and 20bp. The same page’s 2024 10y average is −18, against this file’s Oct–Dec 2024 medians near −49. |
| Dealer letter: 10y asset-swap +37.5 on 2 Jan 2026 and +38.0 on 28 Aug 2026, so swap spreads −37.5 and −38.0 | Those dates; bp | https://www.linkedin.com/pulse/major-markets-letter-39-rate-expectations-fiscal-reckoning-bqobe | Agrees. January median −37.40 (20 days), gap 0.1bp. August median −40.12 (21 days), gap 2.1bp. |
| Same letter: 5y +26.8 then +27.2; 2y +16.0 then +13.4 | 2 Jan 2026 and 28 Aug 2026; bp, Treasury minus SOFR | same URL | Agrees after the sign flip. Gaps 0.1 to 0.9bp against the January and August medians. |
| Same letter: 30y +68.4 on 2 Jan and on 28 Aug, and +74.1 in early March, so −68.4, −68.4 and −74.1 | Those dates; bp | same URL | January is at the edge: median −65.53 (20 days), gap 2.9bp. August median −72.62 (21 days), gap 4.2bp, outside 3bp. Early-March −74.1 against the March median −79.48 (22 days), gap 5.4bp. |
| Same letter: 10-year asset-swap 52bp at the beginning of November 2024, so a swap spread of −52 | Early Nov 2024; bp | same URL | Agrees. November 2024 median −50.05 on 18 days; gap 2.0bp. |
| PIMCO / Bloomberg: 10-year SOFR swap spreads “deeply negative” | As of 13 Jul 2026; no bp level in the text | https://www.pimco.com/lu/en/insights/the-credit-market-lens-rich-spreads-cheap-treasuries-and-an-incomplete-explanation | Sign only. July 2026 median is −42.52 on 21 days. No level to test. |
| irates.today, public tape: 10y −39.0 and 30y −65.8, data through 9 Oct 2026; constant-maturity 10y −39.7 versus −46.0 a year earlier, data through 15 Oct 2026 | bp | https://irates.today/week.html and https://irates.today/asw.html | Agrees, and it is the same DTCC tape, not an independent source. October medians −39.20 and −66.38 (8 days). October 2025 10y median −47.33 against the “year ago” −46.0. |
| Mizuho summary, Bloomberg: ESTR/SOFR 5y −2.38; TONAR/SOFR 3m −15.75; SONIA/SOFR 3m +2.0 | 4 Sep 2026; bp | https://finvaulta.com/research/mizuho-international/cross-currency-weekly-2026-09-04 | Euro 5y agrees with the September pool median −2.12 (21 days); gap 0.3bp, tenor against a pool. Yen 3m does not match the 1–5y pool −23.56 (17 days); gap 7.8bp, and the tenors differ. Sterling 3m is 0.8bp from the pool +2.75. The page says not to treat it as independent verification. |
| BIS: 1-year basis versus the dollar became more negative from March to April/May 2025 for the euro and for Asian currencies including the yen on the chart | Change, not a level; 1-year; chart scale marked to −12bp | https://www.bis.org/publications/bulletin-105-us-dollars-slide-april-2025-role-fx-hedging.pdf | Direction agrees with the yen pool, −39.28 (20 days) to −43.75 (19 days). The extracted text has no yen bar height, so the size is unchecked. |
| NY Fed: 5-year inflation-swap minus breakeven “averaged approximately 30 basis points since 2004” | Average from 2004 to a chart in a 1 Jul 2024 article; bp | https://libertystreeteconomics.newyorkfed.org/2024/07/exploring-the-tips-treasury-valuation-puzzle/ | Not a 2025–26 month. The ledger’s highest 5-year month is +25.53 (Oct 2024, 13 days), and March 2026 is −4.21 (22 days). This does not confirm the note’s +12 to +22 at 10 years. |

### 3. The single weakest point

The weakest claim is that the most negative single days were in April 2025, with prints of −58.5 at 10 years and −93.4 at 30 years. Nothing in the monthly file or the diagnostics file contains a daily print, so those four numbers have no denominator here. What the file does show is that April’s medians (−53.59 and −86.33, each on 20 days) were not the extreme months: July’s 10-year median is −55.10 on 21 days, and May’s 30-year median is −88.12 on 20 days. A Bloomberg snapshot on 15 July 2025 is already −56 and −87, as wide as those monthly troughs. April was a wide, stressed month. Calling it the location of the extremes is ahead of the evidence in this folder.

### 4. Not done

The daily ledger is not in the folder, so 8 Apr 2025, 21 Apr 2025, the 13 Oct 2026 trade counts, the 14:30–16:30 versus full-day gaps, and the bond-equivalent 1–2bp gap could not be recomputed. The per-tenor yen path and the 2.5–3.6 year average maturity are not in `st1_monthly_medians.csv`. No fetched BIS, Bank of Japan, or ECB page states a 1–5 year USD/JPY basis-swap level in basis points for 2025–26; the BIS bulletin’s chart gives a change, and the text extraction does not label the yen bar. No fetched page states a dated 2025–26 CPI-swap minus TIPS gap in basis points: the NY Fed figure is a since-2004 average in a July 2024 article, the TerminalFin fetch returned no basis table, Reuters returned 401, and Bloomberg Professional returned 403. The leverage-ratio dates are cited to a speech outside this folder. BILT’s share of trades, on any day but the one 13 Oct 2026 anecdote, is not in these files.

---

## Parcel 3: Adversarial review of the ICE Brent and WTI positioning claims

*Status SUCCESS; 1505 s; 14 fetches; cited but not fetched: 0.*

**Supervisor check.** Its FALLS on "added length on the way up" led to C-146. The supervisor re-read the WTI weekly path, and the pre-publication audit then caught an over-correction, so the final wording describes swings. Its EIA finding (the Brent spot prints are real and persistent) led to relabelling the flag eia_spot_gap_unverified and extending it to 16 Oct.

### 1. Claims

**CLAIM:** “126,906 on 30 Dec 2025; 382,072 on 31 Mar 2026”  
**VERDICT:** STANDS  
**REASON:** Those futures-only nets are the rows for those Tuesdays, and 382,072 is the maximum of the 40 futures-only readings in 2026.  
**SOURCE:** `brent_nets_2024_2026.csv` lines 107 and 120  
**QUOTE:** “382072” on 2026-03-31, futures-only managed money  
**UNCERTAIN:** No. Press checks below match the futures-and-options net, not this futures-only high.

**CLAIM:** “96,437 on 7 Jul … 15% above” end-2025  
**VERDICT:** STANDS  
**REASON:** 96,437 is below 126,906, and the spot went from 62.30 to 71.78, which is 9.48/62.30 = 15.2%. Only two 2026 rows, 30 Jun and 7 Jul, sit below the end-2025 net.  
**SOURCE:** `brent_nets_2024_2026.csv` lines 107 and 134  
**QUOTE:** “96437” at “71.7800” on 2026-07-07  
**UNCERTAIN:** No.

**CLAIM:** “275,879 on 15 Sep; 186,288 on 6 Oct”  
**VERDICT:** STANDS  
**REASON:** Both futures-only nets match those Tuesdays. The 6 Oct price cell is flagged; the net is not.  
**SOURCE:** `brent_nets_2024_2026.csv` lines 144 and 147  
**QUOTE:** “275879” then “186288”  
**UNCERTAIN:** No for the contracts. The 125.44 price on line 147 is the flagged print.

**CLAIM:** “From 8 Sep to 6 Oct it fell 28%, after rising in the first week.”  
**VERDICT:** WEAKENED  
**REASON:** The net move is (186,288 − 259,481) / 259,481 = −73,193/259,481 = −28.2%, and the first week rose by 16,398. From the 15 Sep high the cut is 89,591/275,879 = 32.5% in three weeks. The 28% uses the lower 8 Sep base.  
**SOURCE:** `brent_nets_2024_2026.csv` lines 143–147; `brent_windows.csv` line 3  
**QUOTE:** “259481,186288,-73193” over four weeks  
**UNCERTAIN:** No for the arithmetic. The 28% figure hides the intra-window peak.

**CLAIM:** Options “from 265,753 to 201,052, a fall of 24%.”  
**VERDICT:** STANDS  
**REASON:** (201,052 − 265,753) / 265,753 = −64,701/265,753 = −24.3%. Combined also rose in week one, to 282,657, so the drop from that peak is 28.8%.  
**SOURCE:** `brent_nets_2024_2026.csv` lines 143–144 and 147; `brent_windows.csv` line 8  
**QUOTE:** “265753,201052,-64701”  
**UNCERTAIN:** No.

**CLAIM:** “During the 2026 rise it had added length” month by month  
**VERDICT:** FALLS  
**REASON:** On Brent, six months show a higher spot at month-end. Length rose in five. From 25 Aug to 29 Sep the spot rose 25.72/88.24 = 29% (88.24 to 113.96) while the net fell 29,800/225,261 = 13% (225,261 to 195,463). Inside September, 1 Sep to 29 Sep is +18.7% in price and −21.8% in the net (249,964 to 195,463). The week of 3 Mar, the first $12 jump, cut 54,198 contracts as the spot rose 12.07/71.21 = 17%. The spot high, 138.21 on 7 Apr, is a week after the position high, and that week the net fell 7,346. January–February had already taken the net from 126,906 to 300,712 while the spot went only from 62.30 to 71.21.  
**SOURCE:** `brent_nets_2024_2026.csv` lines 107, 115–116, 120–121, 141, 143–146  
**QUOTE:** “88.2400 … 225261” then “113.9600 … 195463”  
**UNCERTAIN:** The October week is uncertain because 125.44 is flagged. September and 3 Mar and 7 Apr use unflagged prices. The WTI sentence itself is an endpoint comparison, 15,743 to 111,731, and those two contract counts match CFTC republishers; this folder has no WTI price column, so a WTI month-by-month price test was not possible.

**CLAIM:** “Pooled over 2024–26 (145 weeks) … Brent r = 0.58, NYMEX WTI 0.38.”  
**VERDICT:** STANDS  
**REASON:** Futures-only same-week Pearson is 0.581 on 145 weeks and 0.380 on 145 weeks. Both clear the file’s 0.163 band.  
**SOURCE:** `brent_leadlag.csv` line 3; `leadlag.csv` line 2  
**QUOTE:** “145,0.581” and “145,0.380”  
**UNCERTAIN:** No.

**CLAIM:** “In 2026's 40 weeks alone: Brent 0.60, WTI 0.04.”  
**VERDICT:** WEAKENED  
**REASON:** Re-derived Brent r is about 0.60 on those 40 weeks (the 40 contract changes sum to 59,382, which equals 186,288 − 126,906). At n = 40 the 5% band is 1.96/√40 = 0.31, so 0.60 is outside it. A WTI r of 0.04 would sit inside that band. The 0.04 is not in `leadlag.csv`, which has only the pooled 0.380.  
**SOURCE:** `brent_nets_2024_2026.csv` lines 107–147 for Brent; `leadlag.csv` has no 2026 row  
**QUOTE:** “40,2025-12-30,2026-10-06” in `brent_windows.csv` line 7  
**UNCERTAIN:** The third digit of the Brent 0.60 is hand arithmetic. The WTI 0.04 was not re-derived. A weekly WTI position-and-price file would settle it.

**CLAIM:** Next week “−0.01 (ICE Brent) and −0.08 (NYMEX WTI)” inside “±0.16”, n about 144  
**VERDICT:** STANDS  
**REASON:** Futures-only next-week Pearson is −0.008 and −0.078 on 144 weeks. The file’s band is 0.163, and 1.96/√144 = 0.163. Both sit inside ±0.16 and inside ±0.163.  
**SOURCE:** `brent_leadlag.csv` line 3; `leadlag.csv` line 2  
**QUOTE:** “144,-0.008” and “144,-0.078”  
**UNCERTAIN:** No for these two numbers.

**CLAIM:** “coincident, no lead detected” for this n  
**VERDICT:** WEAKENED  
**REASON:** “No lead detected” matches a failure to reject zero: |−0.008| and |−0.078| are below 0.163. The same sentence calls ±0.16 the smallest correlation the sample can tell from zero. That is the 5% critical value under independent weeks, and a true lead near 0.10 would usually be missed at n = 144. The README also says part of Tuesday’s move can fall in the next-week return. The same-week Brent result, 0.58 pooled and about 0.60 in 2026, is the part that supports “coincident.” The 2026 WTI figure, if it is 0.04, does not.  
**SOURCE:** `brent_leadlag.csv` line 3; `ice_brent_README.md` lines 74–75  
**QUOTE:** “Part of Tuesday's move can fall in the next week”  
**UNCERTAIN:** How much serial correlation widens 0.163. A lead of 0.08 would still be inside a moderately wider band.

**CLAIM:** Without the 6 Oct print, Brent is “0.59 and 0.00.”  
**VERDICT:** WEAKENED  
**REASON:** The README’s same-week futures-only figure moves from 0.581 to 0.588, which rounds to 0.59. The lead-lag file’s next-week figure with the print included is already −0.008. The “0.00” without that print is not a column in the lead-lag file.  
**SOURCE:** `ice_brent_README.md` line 73; `brent_leadlag.csv` line 3  
**QUOTE:** “0.581 and 0.661 with it, 0.588 and 0.668 without”  
**UNCERTAIN:** The next-week correlation after dropping the 6 Oct return. Recomputing the 144 pairs without that return would settle it.

**CLAIM:** The files say a flow caused the price.  
**VERDICT:** STANDS  
**REASON:** They do not. The section says the split between supply disruption and financial demand is unmeasured, and it labels the correlations “coincident, no lead detected.” The README says a futures long funds nothing physical.  
**SOURCE:** `e021_crude_section.md` lines 4–5 and 24–25; `ice_brent_README.md` line 3  
**QUOTE:** “It does not say that any position moved any price”  
**UNCERTAIN:** No.

### 2. External checks

| Figure | Date | Units | URL fetched | Agrees with the files? |
|---|---|---|---|---|
| ICE Brent money-manager net +76,026 to 240,748 lots | Tuesday before the 17 Aug 2026 note, i.e. 11 Aug 2026 | Contracts; report type unnamed in the article | https://think.ing.com/articles/the-commodities-feed-oil-near-90-on-escalating-middle-east-risks/ | Agrees with futures-and-options combined on line 139 (240,748; weekly change 76,026 from 164,722). Futures-only that day is 245,941. |
| Same ING note: NYMEX WTI net longs +2,665 to 103,715 lots | Same Tuesday | Lots; report type unnamed | same URL | Does not match futures-only WTI on 11 Aug, which republishers put at 79,916. Likely the combined WTI net. This folder has no WTI combined series. |
| Money managers bought 78 million barrels of ICE Brent futures and options in the week ending 17 Mar, and 396 million since 16 Dec | Weeks ending 17 Mar 2026 and from 16 Dec 2025 | Barrels; futures and options | https://www.linkedin.com/posts/john-kemp-4275063_brent-bulls-ascendant-as-war-prolonged-and-activity-7441563124568195072-fh9m | Agrees with combined: 351,032 to 428,704 is 77.7 million barrels, and 32,940 on 16 Dec 2025 to 428,704 is 395.8 million barrels. |
| Speculator net long fell 3,250 to 201,052 | Week ended 6 Oct 2026 | Contracts; “speculators,” type unnamed | https://www.insigtx.com/en/news/ice-data-shows-net-long-positions-of-brent-crude-speculators-045060/ | Agrees with combined managed-money net on line 147, and with the change from 204,302. It is not the futures-only 186,288. |
| Net long cut to a little over 201,000 lots, third straight down week, “futures and options data” | As of 6 Oct 2026 | Lots; futures and options | https://www.engine.online/news/speculators-cut-net-long-positions-in-brent-82a1 | Agrees with combined 201,052 and with three down weeks from 282,657. Also says ICE Brent was trading above $100. |
| NYMEX WTI-PHYSICAL managed money 178,353 long and 124,755 short | 6 Oct 2026 | Contracts of 1,000 barrels; futures only; CFTC code 067651 | https://www.cftc.gov/sites/default/files/files/dea/cotarchives/2026/futures/petroleum_lf100626.htm | Net is 53,598. Agrees with the section’s 6 Oct WTI figure. This CFTC page is not ICE Brent. NYMEX Brent Last Day managed money that day is 4,600 long and 1,243 short. |
| WTI managed-money net 15,743; 111,731; 53,598 | 30 Dec 2025; 8 Sep 2026; 6 Oct 2026 | Contracts; futures only; 1,000 barrels | https://humanityvector.com/metric/cot-crude-oil-managed-money-net and https://businessquant.com/economic-data/cotwtimm/ | Agrees with the three WTI contract counts. 111,731 − 53,598 = 58,133 contracts, which is the −58 million barrels. |
| EIA Europe Brent 135.51, 125.51, 125.44, then 126.00 to 126.55 | 2, 5 and 6 Oct 2026, and 7–14 Oct 2026 | Dollars per barrel; spot | https://plainvitals.com/economy/indicator/DCOILBRENTEU | 125.44 and the 29 Sep print of 113.96 match the file. The series is still 126.55 on 14 Oct. |
| EIA spot $125.44 on 6 Oct and $125.51 on 5 Oct; a Brent futures quote of $102.48 on the morning of 5 Oct | 5–6 Oct 2026 | Spot dollars per barrel, and a futures quote | https://marketspeaker.com/briefs/european-brent-spot-price-125-44-eia/ | Confirms the file’s prints and a gap of about $23 versus that futures quote. The README’s “about $20” and “ICE settled near $102” are the same gap. It does not show EIA retracting the prints. |

The 2–6 Oct EIA prints are real published spots, and they stayed high through 14 Oct on the republished series. A futures quote near $102 on 5 Oct confirms they sat about $20–$23 above the futures price the files compare them with. That supports “suspect as a futures price.” It does not, by itself, show a one-off data error: the following sessions are still $126–$130, and the spot write-up treats $125.44 as the spot.

### 3. The single weakest point

“Added length on the way up” is an endpoint sentence laid on a path that does the opposite in the weeks that made the 2026 rise. Most of the first-leg length was already on, 300,712 contracts, by 24 Feb, with the spot only at 71.21 against 62.30 at end-2025. The week the spot jumped $12, 3 Mar, managed money cut 54,198 contracts. The spot then peaked at 138.21 on 7 Apr, one week after the position high, and the net fell again. The second leg’s September finish is the clean break: from 25 Aug to 29 Sep the unflagged spot rose 29% and the futures-only net fell 13%, because the cut after 15 Sep (80,416 contracts) was larger than the add into that peak, while the price giveback from 130.80 to 113.96 did not erase the rise from 88.24. The two-leg list and the 28% four-week figure are the right turning points and the right net percentage, and both are computed off bases that sit below the high inside the window. The same-week correlation, about 0.60 in 2026, can stand beside that: it is an average across 40 weeks, and these weeks are why it is not 1.

### 4. Not done

Bloomberg’s 13 Mar and 17 Jul 2026 oil-positioning articles returned 403, so the search snippets that mention 351,032 and a gross long of 357,154 were not used. John Kemp’s June post, the one the README treats as 253 million barrels on 2 Jun, timed out; the March post did fetch and matches the combined book. The EIA daily table at eia.gov was fetched and the extract stopped in the 1990s–2000s, so 125.44 was confirmed from republishers, not from an EIA row read here. No fetched page quotes the futures-only levels 126,906, 382,072, 96,437, 275,879 or 186,288; the outside matches are futures and options. The WTI 2026 correlation of 0.04, the WTI prices $57.79 and $94.21, and any ICE official settlement file for 2–14 Oct were not in this folder and were not recomputed. The Strategic Petroleum Reserve sentence and the copper sentence were outside this check.

---

## Parcel 4: Source hunt: why N-PORT and Z.1 differ by $131bn

*Status SUCCESS; 439 s; 20 fetches; cited but not fetched: 0.*

**Supervisor check.** Both Fed definitions re-read on the Fed's series pages on 17 Oct: the ETF row is ICI government-bond ETF total net assets, and the latest mutual-fund quarter is estimated. Changes: R2b outside-review section; the 11 Dec CALENDAR row gains a re-run of the scaled arm.

### Explanations

### 1. The ETF “Treasury” row is government-bond fund assets, not every ETF’s Treasury holdings

**EXPLANATION.** `LM563061103` is the quarter-end total net assets of ETFs in ICI’s government-bond objective, plus a hybrid-fund slice, minus an estimated money-market-fund share. It is not a security-level sum of Treasury lines across all ETFs. ICI’s government-bond objective is prospectus-based and includes bonds issued or backed by the US government. A fund is in that objective only if government securities are at least about two-thirds of the portfolio. Investment-grade and multisector funds can hold large Treasury positions and still sit outside it. Z.1’s agency table has a mutual-fund row and no ETF row, so agency securities inside government-bond ETFs are not shown separately from this Treasury line. Mutual funds are handled differently: their Treasury row is holdings of government securities minus an agency share.

**EVIDENCE.** https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=LM563061103&t= — “Table 6 Total Net Assets, Bond, Government Bond”. https://www.ici.org/research/stats/iob_update/classification/iob_definitions — “bonds issued, or backed, by the US government”. https://www.ici.org/viewpoints/21_view_covid2 — “up to two-thirds of their assets in Treasury and agency bonds” and “nearly half of their $2,159 billion of assets in government bonds” (investment-grade mutual funds, December 2019). https://www.federalreserve.gov/releases/z1/20260911/html/f3_3_s.htm — mutual funds are an agency holder; ETFs are not a line.

**PLAUSIBLE SIZE.** Large enough to cover the whole $131bn, with an uncertain sign. The ETF row itself is $502bn rising to $808bn. The 2019 ICI fact shows roughly $1tn of government bonds sitting in mutual funds that are not classified as government-bond funds. The same rule applied to ETFs can hide or mislabel tens to low hundreds of billions. Agencies inside the government-bond ETF total would make Z.1 too high. Treasuries in other bond ETFs would make Z.1 too low. Both can be true at once.

**FITS THE PATH?** Partly. A fixed agency contamination would keep N-PORT/Z.1 below 1 and would tend to widen the dollar gap as the ETF row grows. That does not fit the rise through 100%. It does fit if Treasury holdings outside government-bond ETFs grew faster than any agency piece inside the row. The path is a drift from 95.5% to about 99% by 2025Q4–2026Q1, then a jump. This explanation fits the drift better than the one-quarter jump.

**UNCERTAIN.** The net of the two biases is not measured here. What would settle it is an N-PORT split of Treasury market value by ICI objective, set next to ICI Table 6 government-bond ETF assets for the same dates.

### 2. The latest mutual-fund quarter is an estimate, not the ICI stock

**EXPLANATION.** The mutual-fund government-securities stock is ICI’s market value for completed quarters. The guide says the newest quarter is estimated from the previous stock, price indexes, and estimated transactions. In the 11 September 2026 vintage, that newest quarter is 2026Q2. The Treasury row is that government total minus agencies.

**EVIDENCE.** https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FL653061003&t= — “Data for the most recent quarter estimated”. https://www.federalreserve.gov/RELEASES/Z1/current/introductory_text.htm — “All data through 2026:Q2.”

**PLAUSIBLE SIZE.** About $70bn of the $131bn change, not the earlier $61bn. From 2026Q1 to 2026Q2, N-PORT rises $104.8bn and the three Z.1 rows rise $35.1bn. The mutual-fund row rises only $7.6bn, after increases of $43.9bn and $48.5bn in the two prior quarters. The gap moves from −$24.2bn to +$45.5bn in that one quarter.

**FITS THE PATH?** Yes for the 2026Q2 jump (99.0% to 101.8%). No for the climb from 95.5% to 99.0% through 2026Q1, which in this vintage should already be ICI stocks.

**UNCERTAIN.** The estimation sentence was last edited 7 June 2016. The September 2026 release does not say 2026Q2 is still estimated. A later Z.1 vintage, after ICI’s quarterly composition is in, would settle it.

### 3. Mutual-fund Treasuries are a residual after a CRSP agency share

**EXPLANATION.** `LM653061105` equals ICI long-term plus short-term US government securities, minus agency- and GSE-backed securities. Since 2010Q4 that agency share is a security-level CRSP calculation, with linear interpolation when a quarter is missing. Both pieces include variable-annuity long-term mutual funds. The sector is open-end companies that report to ICI. Money-market funds, ETFs, and hedge funds are outside it. Debt securities are at market value from 1980Q1.

**EVIDENCE.** https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FL653061003&t= — “long-term US government securities plus short term government securities”. https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FL653061703&t= — “unpublished ICI data and estimated by linear interpolation”. https://www.federalreserve.gov/releases/z1/20260911/z1_tables_description.pdf — “including variable annuity mutual funds”. https://www.federalreserve.gov/releases/z1/20260911/html/f3_3_s.htm — mutual-fund agencies are $685.4bn at end-2023 and $782.5bn at 2026Q2.

**PLAUSIBLE SIZE.** A few percentage points of the government book is $50–150bn. End-2023 government holdings are about $2,075bn ($1,390bn Treasuries plus $685bn agencies). A 5-point error in the agency share is about $100bn. The share only has to drift a couple of points to matter for the change.

**FITS THE PATH?** Only if the Treasury share of mutual-fund government holdings rose and Z.1’s CRSP share lagged. That would lift N-PORT/Z.1 gradually. It does not explain the 2026Q2 jump by itself. It also sits awkwardly next to the published mutual-fund comparison below, which has N-PORT Treasuries above Z.1, while this project’s combined ratio starts below 1.

**UNCERTAIN.** CRSP’s error versus N-PORT is not published as a dollar series. A quarterly CRSP-versus-N-PORT agency share for the same open-end universe would settle it.

### 4. ICI misses some reporters and drops funds of funds

**EXPLANATION.** Fact Book totals include only firms that report to ICI, stated as at least 98% of industry assets, and they drop funds of funds so assets are not counted twice. Funds of funds usually hold fund shares, not the underlying Treasuries, so the exclusion avoids double-counting the Treasury stock rather than creating it. Any Treasury bonds owned directly by a fund of funds would be in N-PORT and not in ICI.

**EVIDENCE.** https://www.icifactbook.org/pdf/2025-factbook.pdf — “at least 98 percent of industry assets” and “Funds of funds are excluded from the data to avoid double counting.”

**PLAUSIBLE SIZE.** The 2% coverage margin is about $40bn at the start and about $50bn at the end if non-reporters hold Treasuries in the same proportion. The change in that wedge is much smaller than $131bn unless the uncovered share itself rose. Direct Treasury holdings of funds of funds are an extra, likely smaller, piece.

**FITS THE PATH?** Weakly, and with the wrong sign at the start. Missing reporters make N-PORT higher than Z.1. The file starts with N-PORT $85bn lower. A rising uncovered share can contribute to the later climb toward 101.8%, on the order of tens of billions, not the whole gap.

**UNCERTAIN.** ICI does not publish the Treasury holdings of non-reporters or of funds of funds. Those two stocks would settle it.

### 5. Different fund populations: variable annuities, interval funds, tender-offer funds, BDCs, money funds

**EXPLANATION.** Z.1’s mutual-fund sector includes variable-annuity mutual funds that report to ICI. Money-market funds are outside all three rows and outside N-PORT; they file N-MFP, and their Treasury line is separate ($2,269.5bn at end-2023, $3,281.6bn at 2026Q2). BDCs are their own sector. Interval and tender-offer funds are also their own sector, built from N-PORT, and the 11 September 2026 balance sheet has no Treasury line. Their debt securities are $28.7bn at end-2023 and $43.2bn at 2026Q2, split only into municipals and corporate and foreign bonds. Closed-end `LM553061103` is ICI’s unpublished government-bond detail, about $2bn.

**EVIDENCE.** https://www.sec.gov/data-research/sec-markets-data/form-n-port-data-sets — “other than a Fund that is regulated as a money market fund”. https://www.federalreserve.gov/RELEASES/Z1/current/introductory_text.htm — “Full SEC form N-PORT through 2026:Q1 with partial data”. https://www.federalreserve.gov/releases/z1/20260911/html/S124_6_s.htm — debt lines are municipals and corporate and foreign bonds only. https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=LM553061103&t= — “unpublished detail on assets of closed-end funds, government bonds”.

**PLAUSIBLE SIZE.** Too small to be the gap. Interval and tender-offer debt changes by about $15bn, and Z.1 assigns none of it to Treasuries. Closed-end funds cannot contribute more than their $2bn stock. Money funds are large and correctly outside both measures. Variable-annuity mutual funds are in the Z.1 mutual-fund sector; registered ones also file N-PORT, so they are not a documented one-sided exclusion.

**FITS THE PATH?** No. A growing interval-fund Treasury sleeve would nudge the ratio up, but the Z.1 N-PORT build does not show that sleeve.

**UNCERTAIN.** Whether a few insurance-dedicated funds report to ICI and do not appear in the public N-PORT sets. The SEC Registered Fund Statistics PDF that lists N-3 and interval counts timed out and was not read.

### 6. Market value versus par, and the par-weighted price index

**EXPLANATION.** These three rows are market-value stocks (`LM`). The liability total for Treasuries is net of premiums and discounts; the large instrument discrepancy is that valuation difference for the whole market, not a fund-level par concept. ICI levels are the mutual-fund stock. The Merrill Lynch Treasury master, par-weighted, is used to estimate capital gains, which split a change in market value into transactions and revaluations. Closed-end capital gains use a Treasury/agency par-weighted index, on a $2bn stock. ICI has shown that this residual can miss true transactions by on the order of $100bn in a violent quarter. That is a flow error. It changes these levels only in a quarter that is still estimated.

**EVIDENCE.** https://www.federalreserve.gov/releases/z1/20260911/html/table_desc_instruments.htm — “shown at market value for most sectors”. https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FL653061003&t= — “Merrill Lynch Treasury master par weighted price index”. https://www.ici.org/node/63417/printable/pdf — “adjusting this difference by estimated capital gains on Treasury securities” and “can’t distinguish the split between transactions in Treasuries versus agencies”.

**PLAUSIBLE SIZE.** Not $131bn of the historical stock. In the file, N-PORT par is about 10% above N-PORT market value at end-2023 ($1,997bn versus $1,809bn) and about 8% above at 2026Q2 ($2,801bn versus $2,596bn). If Z.1 were at par, the ratio would sit near 90% and would not cross 100%. The index can move the latest quarter by tens of billions. ICI’s 2020 example shows a flow residual near $130bn; that does not restate the 2023–2026 levels.

**FITS THE PATH?** No, except as the mechanism inside explanation 2. A par-versus-market wedge would stay below 1. The ratio rises through 1.

**UNCERTAIN.** Nothing further on the historical levels. The open point is whether 2026Q2 was still the estimated quarter.

### 7. Hybrid gross-up and the money-fund subtraction inside the ETF row

**EXPLANATION.** The ETF row adds a slice of hybrid ETFs equal to the government-bond share of hybrid open-end mutual funds, and from 2010Q4 subtracts money-market-fund shares estimated from Morningstar fixed-income ETFs. These are adjustments to an objective total, not a holding-by-holding Treasury count.

**EVIDENCE.** https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=LM563061103&t= — “plus a portion of Hybrid Funds equal to the share” and “subtract money market fund holdings estimated as the share”.

**PLAUSIBLE SIZE.** Low tens of billions. A few percent of the $502–808bn ETF row is about $15–40bn. The change in a proportional error is smaller, roughly $10–30bn of the growth gap.

**FITS THE PATH?** Only as a small drift in the same direction as the ETF row’s growth. It does not produce the 2026Q2 jump.

**UNCERTAIN.** The hybrid share and the money-fund share are not published on the series page. Morningstar’s fixed-income ETF money-fund weight would settle the subtraction.

### 8. Fiscal-quarter timing versus calendar quarter-end

**EXPLANATION.** Public N-PORT is the last month of each fund’s fiscal quarter. Z.1 is a calendar quarter-end stock. A stable one-month lag while holdings are rising keeps N-PORT below Z.1.

**EVIDENCE.** https://www.nber.org/system/files/working_papers/w34494/w34494.pdf — “Only the last month of each quarter is disseminated publicly”. The local note’s filing-lag test moves measured duration by about $0.002bn.

**PLAUSIBLE SIZE.** Small relative to $131bn if the project’s three-month window is doing what the note says. A full-quarter lag on a $100bn quarterly increase would be material, but the lag test in the note is not.

**FITS THE PATH?** No. Holdings rise in every base-vintage quarter. A stable lag would keep the ratio under 1. It goes to 101.8%.

**UNCERTAIN.** Little. The path already rejects a stable lag as the main cause.

### 9. Published N-PORT versus Z.1 comparisons

**EXPLANATION.** The comparison that was found is mutual funds only, through 2024, and it says N-PORT Treasury totals sit above the Financial Accounts. It gives no dollar gap. No OFR paper comparing long-term-fund N-PORT Treasuries with Z.1 or ICI was found. OFR pages that were opened are Form N-MFP money-fund monitors, which are outside this gap.

**EVIDENCE.** https://www.nber.org/system/files/working_papers/w34494/w34494.pdf — “N-PORT is above the Flow of Funds systematically in recent years”.

**PLAUSIBLE SIZE.** Unknown in dollars. The chart is not labeled with a gap. Directionally it says the mutual-fund piece of this project’s gap may have the opposite sign from the combined 95.5% starting ratio, which pushes the opening shortfall onto the ETF row.

**FITS THE PATH?** It matches a world in which mutual-fund N-PORT is already at or above Z.1, so the combined ratio can start below 1 only if the ETF row is high. It does not cover 2025–2026Q2 and does not explain the jump.

**UNCERTAIN.** The figure’s dollar gap was not readable in the fetched text. Digitizing Figure 2d, and extending it with ETFs, would settle it.

### Rank

1. ETF government-bond objective assets used as the Treasury stock. This is the only documented construction that is the wrong concept relative to N-PORT line items, and the ETF row is large enough ($305bn of the Z.1 increase) to carry the gap. It fits the gradual climb better than the last quarter.
2. A still-estimated 2026Q2 mutual-fund stock. This fits the jump from 99.0% to 101.8% and about $70bn of the change, and it does not fit the earlier climb.
3. The CRSP agency residual inside mutual funds. The agency stock is $685–783bn, so a modest share error is large enough, but the sign is not identified and the published mutual-fund comparison leans the other way.
4. ICI’s 98% coverage and the funds-of-funds exclusion. Tens of billions, and the wrong sign for the opening shortfall.
5. The hybrid gross-up and money-fund subtraction. Low tens of billions, a small drift with the ETF row.
6. Par versus market, and the par-weighted index, as a story about the historical levels. The rows are market value. The index matters for flows and for a quarter that is still estimated, which is explanation 2.
7. Interval funds, tender-offer funds, BDCs, variable annuities, and money funds. Money funds are outside both measures. The N-PORT-based interval sector shows no Treasury line and only about $15bn of debt-securities growth.
8. Fiscal-quarter timing. The ratio crossing 100% while the stock is rising rejects a stable lag.

Taken together, 1 and 2 can add to $131bn without any one of them having to do all the work. 1 is the candidate for the move from 95.5% to about 99%. 2 is the candidate for 2026Q2. If 1 is really an agency-versus-Treasury mix rather than a missing population of similar bonds, scaling the whole N-PORT book to the Z.1 total is the wrong correction for the duration test. The file’s Z.1 arm applies one scalar to the whole book.

### NOT DONE

- The SEC Registered Fund Statistics PDF (`im-investment-registered-fund-statistics-202512.pdf`) timed out, so N-3 variable-annuity counts and the published interval-fund asset totals in that report were not read.
- No OFR paper comparing N-PORT long-term Treasury aggregates with Z.1 or ICI was found. The OFR pages fetched are money-fund N-MFP statistics.
- GCAP’s Treasury chart has no readable dollar gap, and it stops in 2024 and covers mutual funds, not ETFs.
- ICI’s subscription Table 6 and the unpublished closed-end government-bond detail were not available, so the ETF objective-versus-holdings net was not sized from ICI’s own holdings.
- The series-guide sentences for these rows were last edited in 2016 (mutual funds), 2019 (closed-end), and 2022 (ETFs). That the latest mutual-fund quarter was still estimated on 11 September 2026 is the guide’s rule, not a sentence in that release.
