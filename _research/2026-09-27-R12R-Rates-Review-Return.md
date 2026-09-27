# R12R return — adversarial review of R1 and R2 (27 Sep 2026)

**Run 27 Sep 2026 by Grok.** This answers `Parcel_R12R_Rates_Review_For_Grok_Cursor.md` against repo HEAD `eda278c`.
- **Status: REVIEW RETURN.** The supervisor adjudicates. Nothing here edits R1, R2, their scripts, their tables, N2c or CORRECTIONS.md.
- **Reproduction:** both scripts were re-run on a scratch copy. Every table under `data/r1_rates/` and `data/r2_rates/` came out
  byte-identical. R1's latest common date is 2026-09-18, and R2's checks are 52 with 0 FAIL.
- **Independence:** every figure in "your value" below comes from my own Python on sources I downloaded, not from our scripts.
  That code is not committed; this file is the record.

**Summary of verdicts.**
- **R1 STANDS on its measured claims:** levels, the real-yield split, the model read and the holder return. Its survey section
  is right in sign but wrong in three supporting statements, which are about coverage, dates and horizon.
- **R2 is WEAKENED on three points.**
  - "Duration outgrew face value" depends on market-value weighting.
  - The Fed's share of the extra duration is about 9–13% on a QT counterfactual, not 4%.
  - The buyer table double counts about $144bn of pensions.
- **R2's total holds:** +36% at constant prices, across every curve choice tried.

**Assumptions made (stated, not asked):**
- "Our value" means the value printed in R1, R2 or their tables at `eda278c`.
- "Public" means marketable Treasuries outside SOMA, as in R2.
- The SPF first-quarter deadline is taken from the Philadelphia Fed's release-date file. Treasury data use the same date or,
  if it was not a trading day, the last trading day before it.
- For the survey horizon split, I take TBILLA–TBILLD (the current year and the next three calendar years) as years 1–4. The
  years 5–10 implied rate is (10×BILL10 − 4×mean(TBILLA–D))/6.
- For the QT counterfactual, runoff is taken as the fall in SOMA Treasury par from 27 Dec 2023 to the trough on 3 Dec 2025. The
  public is assumed to have absorbed it pro rata to the coupon and TIPS issuance mix of the same months.

## Section 1 — RE-DERIVED

| claim | our value | your value | source (URL, table or page) | match or mismatch |
|---|---|---|---|---|
| 10y par, 29 Dec 2023 → 18 Sep 2026 | 3.88 → 5.01 (+113bp) | 3.88 → 5.01 (+113bp) | Treasury par curve CSV (home.treasury.gov daily-treasury-rates.csv, type daily_treasury_yield_curve); Fed H.15 zip (federalreserve.gov/datadownload, rel=H15) | match |
| 10y TIPS | 1.72 → 2.68 (+96bp) | 1.72 → 2.68 (+96bp) | Treasury real curve CSV (daily_treasury_real_yield_curve); H.15 | match |
| 10y breakeven | +17bp | 2.16 → 2.33, +17bp | same, by difference | match |
| 2y | +53bp | 4.23 → 4.76, +53bp | Treasury par CSV; H.15 | match |
| 10y at 13 Feb 2026 | 4.04 | 4.04 | Treasury par CSV | match |
| window endpoints | 29 Dec 2023 and 18 Sep 2026 | both are trading days; 18 Sep 2026 is the last date with ACM, KW and Treasury all present | ACMTermPremium.xls; feds200533.csv | match (see T1 for endpoint sensitivity) |
| ACM 10y full window | expected +9 / term premium +97 (fitted +107) | +9.3 / +97.3 (fitted +106.6); ACMY10 − ACMRNY10 − ACMTP10 max abs error 0.000 | newyorkfed.org/medialibrary/media/research/data_indicators/ACMTermPremium.xls | match |
| Kim-Wright 10y full window | expected +22 / term premium +87 (fitted +109) | +22.0 / +86.8 (fitted +108.8) | federalreserve.gov/data/yield-curve-tables/feds200533.csv | match |
| KW term premium cross-check | 0.519 (13 Feb 2026), 0.839 (14 Aug 2026) | 0.5194, 0.8393 | feds200533.csv, THREEFYTP10 | match |
| par vs fitted-zero gap | "a few basis points" | Gürkaynak-Sack-Wright 10y zero +108.9, GSW par +108.0, Treasury par +113: 4–6bp gap | federalreserve.gov/data/yield-curve-tables/feds200628.csv | match |
| survey table, 10y par change Feb 2024 → Feb 2026 | −23bp (14 Feb dates) | −4bp on actual deadlines (6 Feb 2024 4.09; 2 Mar 2026 4.05) | Treasury par CSV; spf-release-dates.txt | mismatch (date choice) |
| survey table, ACM expected 10y change | −92bp | −81bp on actual deadlines | ACM xls | mismatch (date choice), sign same |
| survey table, KW expected 10y change | −39bp | −33bp on actual deadlines | feds200533.csv | mismatch (date choice), sign same |
| SPF BILL10 change | +15bp | +15.2bp (2.836 → 2.988) | philadelphiafed.org SPF historical-data/meanlevel.xlsx, sheet BILL10 | match |
| SPF BOND10 change | +35bp | +34.5bp (3.553 → 3.898) | meanlevel.xlsx, sheet BOND10 | match |
| SPF Q1 deadlines | approximated by 14 Feb | 6 Feb 2024; 11 Feb 2025; 2 Mar 2026 (survey run 20 Feb–2 Mar 2026, delayed) | philadelphiafed.org/-/media/frbp/assets/surveys-and-data/survey-of-professional-forecasters/spf-release-dates.txt | mismatch (2026 is two weeks late) |
| holder return, constant-maturity 10y, full window | +3.29% (summed) | +3.54% compounded, full revaluation monthly; +3.49% daily-rebalanced | Treasury par CSV, own code | small mismatch, same conclusion |
| three-month bills, full window | +12.17% (summed) | +12.74–12.91% compounded | Treasury par CSV 3m | small mismatch (compounding) |
| holder return 2024 / 2025 / equity window | −1.51 / 7.97 / 6.73 | −1.37 / 8.30 / 7.11 | own code | small mismatch, same sign |
| MSPD total marketable, 31 Dec 2023 → 31 Aug 2026 ($bn) | 26,366 → (R2 table) | 26,371.7 → 31,828.0 in Table 1; R2's totals are lower by the Federal Financing Bank (5.5 and 3.6) | api.fiscaldata.treasury.gov mspd_table_1 | match (FFB gap as R2 states) |
| MSPD bills ($bn) | 21.5% → 22.8% of marketable | 5,675.8 → 7,248.1 (21.5% → 22.8%) | mspd_table_1 | match |
| Fed Treasury holdings, H.4.1 ($m) | exact on four dates | 27 Dec 2023 4,790,547; 31 Dec 2025 4,227,801; 24 Jun 2026 4,488,106; 26 Aug 2026 4,546,169 | federalreserve.gov/releases/h41/ 20231228, 20260102, 20260625, 20260827, table 1 | match |
| public 10-year equivalents, market prices ($bn) | 9,539 → 11,936 | 9,538.4 → 11,935.9 (exact coupon schedules, dirty prices) | MSPD Table 3 API; SOMA API; Treasury curves | match |
| public 10-year equivalents, constant end-2023 prices ($bn) | 9,539 → 12,943 (+36%) | 9,538.4 → 12,942.5 (+35.7%); GSW curve engine +35.8% | as above plus feds200628/feds200805 | match |
| public face value ($bn) | 21,576 → 27,278 (+26%) | 21,575.7 → 27,278.2 (+26.4%) | MSPD Table 3; SOMA | match |
| Fed 10-year equivalents, constant prices ($bn) | 3,320 → 3,178 (−142) | 3,319.8 → about 3,178 | SOMA API; Treasury curves | match |
| nominal coupons > 10y to run ($trn) | 4.2 → 5.4 (+29%) | 4,172 → 5,369 (+28.7%) | MSPD Table 3 | match |
| average coupon on the stock | 2.4% → 3.3% | 2.40% → 3.31% | MSPD Table 3 | match |
| SOMA par-weighted Treasury modified duration (engine validation, not an R2 claim) | not stated | 6.55 / 6.69 / 6.71 years at end-2023/24/25 | NY Fed omo2024 p.26 and omo2025 p.28 state 6.6 / 6.7 / 6.7 | match (validates my engine) |
| Z.1 buyer rows 2024:Q1–2026:Q2 ($bn) | ROW 1,325; MMF 1,012; MF 640; Ins+pen 551; Banks 491; HH 459; Other 419; BD 231; Fed −344 | same nine values to 0.1 | federalreserve.gov/releases/z1/20260911/z1_csv_files.zip (8,336,582 bytes) | match (as built) |
| rows minus net issuance | +$132bn "overlap" | +132.1 as built; −12.1 after removing a 144.2 double count (T8) | Z.1 CSV: FU593061105 = FU573061105 + FU343061105 + FU223061143 exactly | mismatch (it is a double count, not an overlap) |
| insurers and pensions | $0.55trn | about $0.41trn (550.9 − 144.2) | Z.1 CSV; `bin/build_closure_2026Q2.py` lines 167–168 | mismatch |
| MMF Treasury holdings change, Dec 2023 → Jun 2026 | $1.01trn (Z.1) | +1,011.7 (2,269.5 → 3,281.2) | data.financialresearch.gov/v1/series/timeseries?mnemonic=MMF-MMF_T_TOT-M | match |
| Fed share of the public's extra duration | about 4% ($0.14trn) | 9–13% ($0.32–0.43trn) on a QT refinancing counterfactual (T7) | SOMA API; MSPD Table 3; own code | mismatch (measure choice) |

## Section 2 — ATTACKS

| target | strongest case against | evidence | verdict | what would settle it |
|---|---|---|---|---|
| T1 levels and endpoints | End-2023 was a local low after a fast rally, so "+113bp" depends on the start date. | 10y was 4.98 on 19 Oct 2023 and 3.79 on 27 Dec 2023. From 19 Oct 2023 to 18 Sep 2026 the rise is only +3bp. The 10y was 5.17 on 25 Sep 2026, a week after the window. Levels themselves match H.15 and the Treasury CSVs exactly. | STANDS | Nothing to settle on levels. Add one line that the window starts just after an 119bp rally from the Oct 2023 peak. |
| T2 model read | Mixing fitted zero yields with par yields could hide a gap. | The identities are read correctly (ACM exact; KW expected = THREEFY10 − THREEFYTP10 per the Board's mnemonics). The par vs zero gap is 4–6bp, unallocated, and R1 says so. GSW gives the same 4–5bp gap independently. | STANDS | None needed. Optionally show the gap as a residual column. |
| T3 survey check | Wrong dates, a mismatched horizon, and no 2026 coverage. | The sign disagreement survives actual deadlines: ACM −81, KW −33 against SPF +15 (BILL10) and +35 (BOND10). FOMC longer-run median rose 2.5 → 3.1 (Dec 2023 → Jun 2026), same sign as SPF. **But the split by horizon changes the story:** years 1–4, SPF −54, ACM −118, KW −72, all falling. Years 5–10 implied, SPF +62, ACM −56, KW −8. The disagreement sits only at the 5–10y horizon. Quarterly SPF 4-year bill averages exist, and they rose 2026Q1 → Q3 by +35 against ACM +58 and KW +48. So SPF does cover the 2026 rise at short horizons. KW's survey use is in parameter estimation; daily factors move with yields, so the dependence is weak for changes. | STANDS on sign, WEAKENED on supporting statements | Redo the table on the true deadlines, add the horizon split, and state that the dispute is about 5–10y expectations. Blue Chip long-range surveys (not free) or the SEP longer-run dots would settle the long horizon further. |
| T4 holder return | Summing, not compounding, and approximating roll-down could flip the comparison. | Full revaluation, compounded monthly: +3.54% (daily: +3.49%) against R1 3.29. Bills compounded 12.74–12.91 against R1 12.17. UTEN (ICE BofA Current 10Y tracker): 2024 −1.67, 2025 +7.82. S&P Current 10Y TR for the year to 31 Jul 2025 was 1.71% (my 2.32). Bloomberg Short Treasury TR 2024 was 5.26% (R1 bills 5.26). The gap to bills is about 9pp either way. | STANDS | A free daily constant-maturity total-return index for the full window would settle the exact level. |
| T5 supply totals | MSPD and H.4.1 could differ from R2's security-level build. | MSPD Table 1 totals and bills match; the only gap is the Federal Financing Bank, as stated. H.4.1 matches on all four pages opened. Treating about $13–17bn of intragovernmental non-FFB marketables as public is immaterial. | STANDS | None. |
| T6 10-year-equivalent method | The constant-price measure prices high-coupon bonds at a premium and so credits quantity for coupon changes. "Duration outgrew face value" may be an artefact of market-value weighting. | The +36% is robust to curve choice: fixed 2023 curve +35.7%, fixed Aug 2026 curve +35.9%, average curve +35.8%, GSW engine +35.8/+36.0, TIPS beta 0.5 +36.3%, FRN duration 0.25 no change. **Par-weighted duration (par × modified duration, the NY Fed's SOMA convention):** +24.9% on any fixed curve and +26.5% on own curves, against face +26.4%. So duration did not outgrow face on a par basis. The MV-weighted gap is about half coupon/price and half higher duration per MV dollar (+3.8%). At market prices, 10-year equivalents rose +25.1% but DV01 only +20.0%, because the 10y benchmark duration fell from 8.22 to 7.89. Clean vs dirty prices change levels by under 0.5%. | WEAKENED | Report par-weighted and DV01 alongside the MV constant-price number; restate "outgrew face value" as measure-dependent. |
| T7 Fed share | The change in the Fed's own 10-year equivalents is not QT's contribution. It nets ageing against rollovers and ignores what Treasury had to refinance. | SOMA Treasury par fell $602bn from 27 Dec 2023 to 3 Dec 2025, about $575bn of it coupons. Gross coupon and TIPS issuance over the same months was about $8.43trn, at 0.721 10-year equivalents per dollar on the end-2023 curve (0.557 aged to Aug 2026). Refinancing the runoff therefore put $0.32–0.43trn of 10-year equivalents on the public: 9–13% of +$3.40trn. The NY Fed reports say ageing in SOMA was offset by reinvestment, which is what R2's −$0.14trn measures. | WEAKENED | Treasury's own attribution of issuance to SOMA redemptions (TBAC financing tables) with the maturity mix of the replacement issues. |
| T8 buyer table | The rows double count, MMF composition is assumed, and ROW and households overlap. | N2c adds FU593061105 (pension total) and FU223061143 (state and local DB pensions). In the Sept 2026 Z.1 CSV, FU593061105 = FU573061105 + FU343061105 + FU223061143 exactly, so $144.2bn is counted twice. Remove it and the rows fall $12bn short of net issuance. OFR MMF Treasury holdings rose $1,011.7bn, matching Z.1. OFR gives no bills/FRN/coupon split and SEC N-MFP bulk data refused scripted download, but rule 2a-7 (397-day maturity cap, WAM 60 days) bounds MMF duration regardless. The Oct 2025 FEDS Note puts about $1.4trn of Cayman hedge-fund Treasuries outside TIC at end-2024. Z.1 households are a residual, so those holdings sit in households, not ROW. | WEAKENED | A corrected N2c build without FU223061143; a Z.1 vintage stating whether it adopts the TIC adjustment; N-MFP holdings by security type. |
| T9 outside estimates | R2's magnitudes could be out of line with published figures. | NY Fed: SOMA total 10-year equivalents $5.96trn → $5.44trn (2024), $5.13trn (2025), par-weighted and incl. MBS, so not comparable in level, same direction. TBAC Q1 2026 charge scenario keeps the privately held bill share about flat. Treasury's TBAC presentations give WAM 70.9 months at 31 Jan 2024 (R2: 5.89 years total) and a 22.2% bill share at 31 Jul 2026 (R2 about 22.3%). No free 2024–26 estimate of public 10-year equivalents found. | STANDS (where comparable) | A published public 10-year-equivalent series (for example in a TBAC appendix). |
| T10 causation | Wording could imply flows caused the yield move. | Neither note states that flows caused the move; both disclaim it. Soft spots: script docstring line 4 says duration "is what matters for yields"; R1 line 49 reads "as rate cuts were priced"; R2 lines 28 and 105 frame "not the Fed's runoff" as settled. | STANDS, with three wording fixes | Reword the three lines (Section 4). |

## Section 3 — OUTSIDE ESTIMATES

| figure | value | source (URL, page) | agrees with R1 or R2? |
|---|---|---|---|
| SOMA 10-year equivalents, total domestic incl. MBS | $5.96trn (end-2023) → $5.44trn (end-2024) | newyorkfed.org/medialibrary/media/markets/omo/omo2024-pdf.pdf, p.26 and Chart 14 | not comparable in level (includes MBS, par-weighted); yes in direction (R2 Fed falls) |
| SOMA 10-year equivalents | $5.44trn → $5.13trn (end-2025) | newyorkfed.org/medialibrary/media/markets/omo/omo2025-pdf.pdf, p.28 | not comparable in level; yes in direction |
| SOMA Treasury par-weighted duration | 6.6 → 6.7 (2024), 6.7 (2025); ageing offset by reinvestment | omo2024 p.26; omo2025 p.28 | yes (supports reading R2's Fed change as ageing minus rollovers) |
| Treasury WAM of marketable debt | 70.9 months at 31 Jan 2024 | home.treasury.gov/system/files/221/TreasuryPresentationToTBACQ12024.pdf, WAM chart | yes (R2 total 5.89 years at end-2023) |
| bill share of marketable debt | 22.2% at 31 Jul 2026 | home.treasury.gov/system/files/221/TreasuryPresentationToTBACQ32026.pdf, bill share chart | yes (R2 about 22.3%) |
| TBAC charge scenario, bill share | about 21.6% → 23.2% of total, privately held share about unchanged | home.treasury.gov/system/files/221/TBACCharge1Q12026.pdf | yes in direction; supports public bill share not rising |
| TBAC charges on duration supply | no 10-year-equivalent figure in Q3 2024, Q4 2025 or Q1 2026 charges | TBACCharge1Q32024.pdf, TBACCharge1Q42025.pdf, TBACCharge1Q12026.pdf | not comparable |
| Cayman hedge-fund Treasuries outside TIC | about $1.4trn at end-2024 ($1.85trn per Form PF) | federalreserve.gov/econres/notes/feds-notes/the-cross-border-trail-of-the-treasury-basis-trade-20251015.html | no for R2 line 55 (the undercount sits in households, not ROW) |
| Cayman hedge-fund net purchases | $1.2trn in Jan 2022–Dec 2024, 37% of net notes and bonds issuance | same FEDS Note | not comparable (different window); supports R2's levered-buyer point |
| basis trade size; hedge-fund share | about $0.83trn (Sep 2025); holdings about 4.5% → 8.5% of outstanding | federalreserve.gov/econres/notes/feds-notes/decomposing-hedge-funds-u-s-treasury-exposures-20260622.html | yes (R2 line 58) |
| FOMC longer-run fed funds median | 2.5 (Dec 2023) → 3.0 (Dec 2025) → 3.1 (Mar and Jun 2026) | federalreserve.gov/monetarypolicy/fomcprojtabl20231213.htm, …20251210.htm, …20260318.htm, …20260617.htm | agrees with R1's survey sign; disagrees with the models' long-horizon expectations |
| ICE BofA Current 10Y via UTEN | 2024 −1.67%; 2025 +7.82%; Jan 2024–Aug 2026 +4.22% | portfolioslab.com/symbol/UTEN (monthly returns) | yes (R1-method 2024 −1.51, 2025 7.97) |
| S&P US Treasury Current 10Y TR, 1 Aug 2024–31 Jul 2025 | 1.71% | profunds.com/globalassets/profunds/documents/annual-reports/rising_rates_opportunity_10_annual_ic.pdf, performance table | yes, within about 0.5pp (R1-method 2.21) |
| Bloomberg Short Treasury TR, 2024 | 5.26% | sec.gov/Archives/edgar/data/1758583/000158064225001631/arcaustreasury_ncsr.htm | yes (R1 bills 2024 5.26) |
| academic 10-year-equivalent method | method only, no 2024–26 estimate | Li and Wei, FEDS 2012-37 (federalreserve.gov/pubs/feds/2012/201237/201237abs.html) | not comparable |

## Section 4 — OVERCLAIMS OR GRADE ERRORS

| file:line | what the note says | what the evidence supports |
|---|---|---|
| R1 (`2026-09-27-R1-Treasury-10y-Decomposition.md`):26 | February 2024 to February 2026 is "the only span the survey covers". | SPF is quarterly. Its 4-year bill path covers 2024Q1–2026Q3 (deadline 11 Aug 2026); only BILL10 and BOND10 are first-quarter only. |
| R1:26–27 | Models and survey have opposite signs over the span. | True for 10-year averages, but years 1–4 agree in sign (SPF −54, ACM −118, KW −72). The dispute is years 5–10 only. |
| R1:53–54 | "the survey disputes even that". | It disputes the long-horizon part only; near-term expectations fell in all three. |
| R1:63 | 10y par change −23bp, ACM −92, KW −39. | On actual deadlines: −4, −81, −33. Signs unchanged. |
| R1:66 | Survey is annual and "its latest reading predates the 2026 rise". | The quarterly SPF 4-year bill path rose +35bp from 2026Q1 to 2026Q3, alongside the rise. |
| R1:70 | 14 February approximates the survey deadline. | Deadlines were 6 Feb 2024, 11 Feb 2025 and 2 Mar 2026. The 2026 approximation is two weeks early. |
| R1:69 | KW "is not independent of surveys". | Surveys enter parameter estimation; daily changes are driven by yields. Weak for changes, not a disqualifier. |
| R1:96–97 | The rise came "from the long end, concentrated after February 2026". | After 13 Feb 2026 the 2y rose +136bp and the 10y +97bp; R1's own line 50 says the front end led in 2026. |
| R1:98–99 | "three measures give three answers". | All three agree that near-term expected rates fell over 2024–26; they diverge on 5–10y. |
| R1:30–31 vs 118 | Holder return graded MEASURED, yet listed under Inferred. | Inconsistent grade. It is a derived approximation; label it inferred (the level re-derives within 0.3pp). |
| R1:49 | "as rate cuts were priced". | An interpretation label, not measured; acceptable if kept as a label (line 47 says so), but it is causal wording. |
| CHARTER.md:75 | "the rise was real yields and the long end". | Real yields yes. "The long end" holds for the full window only; the front end led after Feb 2026. |
| R2 (`2026-09-27-R2-Treasury-Duration-Supply-And-Holders.md`):7 and :27 | "all 52 checks pass" / "every check passes". | The checks test par totals, bills and H.4.1 against sources, not the duration or 10-year-equivalent figures. The phrase overstates what was checked. |
| R2:24–27 | "duration supply grew faster than face value". | True under MV weighting (+36% vs +26%). Under par weighting it is +24.9% (fixed curve) or +26.5% (own curves), about equal to face. |
| R2:27 vs 120–121 | Constant-price measure graded MEASURED, yet listed as inferred. | Inconsistent grade; it is a derived measure. |
| R2:28 and :32; also :105–106 | "Treasury issuance supplied it, not the Fed's runoff"; about 96%. | On a QT refinancing counterfactual the Fed accounts for 9–13%. Treasury issuance still dominates, but "not the Fed's runoff" is too strong. |
| R2:29 | "+$0.06trn in 2025–26 as it resumed buying". | Net purchases began only in mid-December 2025; the 2025 gain was mostly coupon rollovers offsetting ageing. The 2026 bill purchases add almost no duration (R2 line 31 agrees). |
| R2:33 | "Issuance shifted toward bills". | Total bill share rose 21.5 → 22.8%, but the public's bill share fell 25.3% → 24.6% because SOMA bills rose 222 → 542bn. |
| R2:51–52 | The nine rows "overlap slightly" by $132bn. | $144.2bn is an arithmetic double count (state and local DB pensions inside the pension total). Corrected rows fall $12bn short. |
| R2:44 | Insurers and pensions $0.55trn. | About $0.41trn after removing the double count. |
| R2:53 | "Money-market funds took bills". | MMFs hold bills, FRNs and short coupons; composition not obtained. Rule 2a-7 bounds their duration, so the conclusion survives, but the wording overstates. |
| R2:55–56 | ROW "includes hedge funds domiciled offshore"; Cayman $1.85trn. | The FEDS Note says TIC misses about $1.4trn of it; with households as the residual, that part sits in households, not ROW. |
| `bin/r2_duration_supply.py`:4 | "Duration, not face value, is what matters for yields". | An unsupported causal premise; the charter bars claiming flows moved yields. Reword to "duration measures rate risk supplied". |

## Section 5 — LOAD-BEARING ASSUMPTIONS

| note | the assumption that sinks it if wrong | why |
|---|---|---|
| R1 | That ACM and Kim-Wright measure long-horizon (years 5–10) expected short rates well enough to leave a term premium. | Surveys (SPF years 5–10 +62bp, SEP longer run +60bp) say long-horizon expectations rose while both models say they fell. If the surveys are right, most of the 97bp/87bp "term premium" is expectations, and R1's full-window split reverses. R1 already grades the split HYPOTHESIS, so R1's measured claims survive either way. |
| R2 | That market-value-weighted duration at a fixed end-2023 curve is the right quantity of duration supply, together with the Z.1 row attribution. | Under par weighting (the NY Fed's convention) duration grew no faster than face. The buyer rows carry a $144bn double count and place TIC-missed hedge-fund holdings in ROW rather than households. The +36% headline survives; the "faster than face" and "96% Treasury" framings do not. |

## Section 6 — CITATIONS CHECKED

| source | opened? | says what is cited? |
|---|---|---|
| Treasury daily par yield curve CSV (home.treasury.gov daily-treasury-rates.csv) | yes | yes |
| Treasury daily real yield curve CSV | yes | yes |
| NY Fed ACMTermPremium.xls | yes | yes |
| Fed Board feds200533.csv (Kim-Wright) | yes | yes |
| Fed Board three-factor term structure model page | yes | yes (surveys used in estimation) |
| Fed Board feds200628.csv (GSW nominal) and feds200805.csv (TIPS) | yes | yes |
| Fed Board H.15 data download (FRB_H15.zip) | yes | yes |
| Philadelphia Fed SPF meanlevel.xlsx (BILL10, BOND10, TBILL) | yes | yes |
| Philadelphia Fed spf-release-dates.txt | yes | yes (deadlines as stated) |
| Philadelphia Fed SPF 2026 Q1 survey page | search snippet only | yes (delayed survey window) |
| MSPD Table 1 and Table 3 (api.fiscaldata.treasury.gov) | yes | yes |
| NY Fed SOMA API (markets.newyorkfed.org/api/soma) | yes | yes |
| H.4.1 releases 20231228, 20260102, 20260625, 20260827 | yes | yes |
| Z.1 20260911 CSV zip | yes | yes |
| N2c note `2026-09-12-N2c-Closure-Refresh-2026Q2.md` and `bin/build_closure_2026Q2.py` | yes | yes (and shows the double count) |
| FEDS Note, 15 Oct 2025, cross-border trail of the basis trade | yes | yes |
| FEDS Note, 22 Jun 2026, decomposing hedge funds' Treasury exposures | summary page and search snippet; full text not read | yes for $0.83trn; hedge-fund share figures from snippet |
| NY Fed omo2024 and omo2025 annual reports (PDF) | yes | yes |
| TBAC charges Q3 2024, Q4 2025, Q1 2026 | yes | yes (no 10-year-equivalent figure) |
| Treasury presentations to TBAC Q1 2024 and Q3 2026 | yes | yes |
| FOMC SEP tables 20231213, 20251210, 20260318, 20260617 | yes | yes |
| OFR money-market fund monitor API, MMF-MMF_T_TOT-M | yes | yes (total only, no split) |
| SEC N-MFP bulk data | no (403 to scripted fetch) | not checked |
| PortfoliosLab UTEN page | yes | yes (monthly returns; market price basis) |
| ProFunds Rising Rates Opportunity 10 annual report, Jul 2025 | yes | yes (index 1.71%) |
| Arca U.S. Treasury Fund N-CSR, FY2024 (SEC) | yes | yes (benchmark 5.26%) |
| Li and Wei, FEDS 2012-37 | abstract and method only | yes (method, no 2024–26 figure) |
| Kim and Wright (2005) FEDS 2005-33 paper | search snippet only | not checked in full |
| FRED | no (unreachable) | not used |
| Repository context: CHARTER.md (Grades; the no-flows-caused-yield rule), THE_ASK.md E-007, CORRECTIONS.md C-102 | yes | yes |

Counts: 30 sources listed. 24 opened in full, and all 24 say what is cited here. 4 were seen only in part or by snippet. 2 were not opened: FRED was unreachable, and N-MFP refused the download.

## Section 7 — OBSERVED vs INFERRED, then UNCERTAIN

**Observed:**
- Every yield level and change, the model outputs, SPF values and deadlines, and the SEP medians.
- MSPD, H.4.1 and SOMA holdings; Z.1 series and their identity.
- OFR MMF totals; published index returns.

**Inferred:**
- My holder-return levels.
- All 10-year-equivalent and par-weighted duration figures (pricing model).
- The years 5–10 survey rate (by subtraction).
- The QT counterfactual.
- The household placement of TIC-missed hedge-fund holdings.
- That MMF duration stays small (from rule 2a-7, not holdings data).

**UNCERTAIN:**

| item | what I inferred | what would settle it |
|---|---|---|
| MMF Treasury composition | bills, FRNs and short coupons, duration bounded by 2a-7 | N-MFP security-level holdings, 2024–26 |
| Z.1 treatment of TIC-missed hedge-fund holdings | the Sept 2026 vintage still books them in households | a Z.1 release note on ROW Treasury methodology |
| QT counterfactual | runoff absorbed pro rata to the coupon mix; bills share of runoff about 5% | Treasury attribution of issuance to SOMA redemptions |
| SPF horizon alignment | calendar-year forecasts approximate years 1–4 from each deadline | a horizon-matched survey (SPF 5-year-forward, Blue Chip long-range) |
| UTEN basis | market price returns less fee approximate the index | ICE index total-return data (not free) |
| KW and surveys | survey use limited to parameter estimation, so daily changes are yield-driven | the Board's current estimation notes |
| residual after correction | rows fall $12bn short of net issuance; small but unexplained | a full N2c rebuild on the corrected pension line |
