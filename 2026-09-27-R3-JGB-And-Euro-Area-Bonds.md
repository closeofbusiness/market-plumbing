# R3 — Japanese and euro-area government bonds: what moved the 10-year yields, and who bought (27 Sep 2026)

**Status: FINDING, first pass. Supervisor, 27 Sep. Not yet reviewed from outside.** R1 and R2 asked two questions of US
Treasuries: what moved the 10-year yield (the charter's question 1, prices), and who bought against what net supply
(question 2, money). This note asks both of Japanese government bonds (JGBs) and of euro-area government bonds, with the
German Bund as the benchmark. Every major correction in this programme has come from outside review; R3 has had none yet.
- **Script:** [`bin/r3_jgb_egb.py`](bin/r3_jgb_egb.py). **Tables:** [`data/r3_rates/`](data/r3_rates/).
- **Inputs,** fetched by the script and not redistributed:
  - Japan: the Ministry of Finance's daily JGB yields and its auction history; the JSDA's daily reference prices; the Bank of
    Japan's Flow of Funds, through its data API.
  - Euro area: the Bundesbank's daily Bund yields and its expected real rate; the ECB's yield curves, convergence yields,
    Survey of Professional Forecasters, holdings by sector (SHSS) and debt outstanding (CSEC); the ECB's asset purchase
    programme histories.
- **Dates:** prices run from end-2023 to 24 Sep 2026, the latest date every price source covers. Holdings run to 2026Q2.

## The answer

1. **Both 10-year yields rose more than the US 10-year did.** The US 10-year rose 113bp to 18 Sep (R1).
   - **Japan: 0.65% to 3.07%, +243bp. Real yields rose about 145bp and breakeven inflation about 97bp.** So inflation
     compensation did about two-fifths of Japan's rise. In the US it did a sixth. *MEASURED; the breakeven is derived (method
     below).*
   - **Germany: 2.06% to 3.62%, +156bp, almost all of it real.** There is no free market breakeven for Bunds. On the
     Bundesbank's survey-based measure, the expected real rate rose 135bp and the implied survey inflation expectation did
     not move. The ECB's long-term inflation survey fell 10bp. The ECB's own reading of 2025 agrees: almost all of the rise
     was in the real component (ECB blog, 16 Jan 2026). *MEASURED, on a survey-based split.*
   - The euro-area AAA curve rose 149bp at ten years, close to the Bund.
2. **The front ends rose too, and in the latest quarter they led.**
   - Japan's 2-year rose 186bp, about three-quarters of the 10-year's rise, as the BoJ raised rates.
   - Germany's 2-year rose 95bp. In 2024 it fell 33bp while the 10-year rose 37bp, as the ECB cut.
   - From 30 Jun to 24 Sep 2026 the 2-year rose 80bp in Germany and 53bp in Japan. The US 2-year rose 62bp from 30 Jun to
     18 Sep (R1). *MEASURED; that the three moved together is a reading, not a test.*
3. **Italy's spread over Germany narrowed 92bp, to 80bp. France's widened 27bp, to 82bp.** These are monthly averages,
   December 2023 against August 2026. France now pays about what Italy pays. *MEASURED.*
4. **Whether the rises were term premium or expected rates is not measured here.** No free, maintained term-premium series
   exists for JGBs or Bunds; both scouting passes looked. Published estimates:
   - **Japan.** The BoJ estimates that since summer 2024 expected short rates and the term premium have contributed "roughly
     the same degree" to the 10-year's rise. It puts the effect of its purchase cuts at about 25bp, of which about 10bp
     comes from its shrinking holdings (Bank of Japan Review 2026-E-10, August 2026).
   - **Euro area.** The ECB's 10-year term-premium estimate rose through the first half of 2023, fell back, and "has been
     fairly stable since" (Lane, 11 Jun 2025).
   - *HYPOTHESIS for any split.* Both estimates come from models, which is the lesson of C-102 and C-125.
5. **Holders lost against cash.** A constant-maturity 10-year position, fully revalued and compounded month by month, returned
   −13.9% in Japan against +1.6% for the 1-year. In Germany it returned −4.7% against +6.9%. *MEASURED; derived from the
   yield curves by the method below.*
6. **Who bought JGBs as the BoJ stepped back.** Flow of Funds transactions, 2024Q1–2026Q2, in trillion yen:

   | Buyer | Net purchases |
   |---|---:|
   | Bank of Japan | −63.0 |
   | Banks (depository corporations) | +54.7 |
   | Public pensions | +32.3 |
   | Overseas | +23.7 |
   | Households and nonprofits | +9.7 |
   | Private pension funds | +4.8 |
   | Other financial intermediaries | +3.6 |
   | Nonfinancial corporations | +3.1 |
   | Securities investment trusts | +2.4 |
   | General government, excluding public pensions | +2.1 |
   | Financial auxiliaries and public captive institutions | +1.8 |
   | Insurance | −5.8 |
   | **Net issuance** | **+69.5** |

   - Transactions exclude price changes, like the Z.1 flows in R2. The rows partition the holders, and the script checks
     that every quarter. *MEASURED.*
   - The BoJ's share of JGBs, at market value, fell from 53.8% to 46.7%. Its sales accelerated: ¥6.0trn in 2024,
     ¥33.0trn in 2025, ¥24.0trn in the first half of 2026.
   - Overseas buying began in 2025 (¥16.6trn); in 2024 it was flat. Insurers turned net sellers in 2025.
   - The BoJ's own face-value estimate for June 2024 to March 2026 points the same way: its holdings −49, banks +36,
     overseas +27, pensions +20, households +6, insurers −5 (trillion yen; BoJ Review 2026-E-10, Chart 8).
7. **Who absorbed euro-area government debt.** Holdings at face value, 20 euro-area countries, 2023Q4 to 2026Q2, in € billions:

   | Holder | 2023Q4 | 2026Q2 | Change |
   |---|---:|---:|---:|
   | Eurosystem (national central banks and the ECB) | 3,419.6 | 2,668.8 | −750.9 |
   | Banks | 1,528.7 | 2,253.8 | +725.1 |
   | Rest of the world | 2,248.3 | 3,078.2 | +829.9 |
   | Investment funds (non-money-market) | 952.2 | 1,192.3 | +240.1 |
   | Insurance corporations | 1,318.7 | 1,448.9 | +130.2 |
   | General government | 477.8 | 595.0 | +117.2 |
   | Pension funds | 445.1 | 548.4 | +103.3 |
   | Households and nonprofits | 383.3 | 482.7 | +99.4 |
   | Other financial institutions | 61.8 | 141.3 | +79.5 |
   | Money market funds | 53.6 | 99.9 | +46.3 |
   | Nonfinancial corporations | 95.6 | 125.2 | +29.7 |
   | **Total outstanding** | **10,984.7** | **12,634.5** | **+1,649.8** |

   - The rest of the world is total outstanding minus all euro-area holders. The euro-area rows partition those holders,
     and the script checks that. *MEASURED; stocks at face value, whose changes are net purchases at face value.*
   - The Eurosystem's share fell from 31.1% to 21.1%. Its own programme holdings (PSPP and PEPP public-sector, at amortised
     cost) fell from €4,017bn to €2,983bn over the same months. That total also includes supranational bonds.
   - The ECB notes that the foreign segment increasingly reflects hedge funds, and that its data cannot split it (ECB
     Financial Stability Review, May 2026, box "Along the curve"). That is the same pattern C-124 found in US Treasuries.
8. **The common pattern, and its limit.** In all three markets the central bank shrank its holdings while governments issued.
   Banks absorbed much of it in Japan and the euro area; foreign investors did in the euro area and, from 2025, in Japan;
   Japan's public pensions bought heavily. This is timing, not cause. The charter forbids claiming that flows or official
   selling caused a yield move, and item 4 shows the premium split is not measured. *HYPOTHESIS.*

## The price tables

**Japan** (percent; breakeven at the newest 10-year JGBi's maturity):

| date | 10-year | 2-year | 30-year | JGBi used | JGBi real yield | breakeven | real 10-year (implied) |
|---|---:|---:|---:|---|---:|---:|---:|
| 2023-12-29 | 0.647 | 0.048 | 1.662 | #28 | −0.64 | 1.22 | −0.57 |
| 2024-12-30 | 1.111 | 0.599 | 2.252 | #29 | −0.40 | 1.42 | −0.31 |
| 2025-12-30 | 2.066 | 1.167 | 3.354 | #30 | 0.22 | 1.77 | 0.29 |
| 2026-06-30 | 2.690 | 1.382 | 3.873 | #31 | 0.66 | 1.99 | 0.70 |
| 2026-09-24 | 3.073 | 1.912 | 4.115 | #31 | 0.80 | 2.20 | 0.88 |

**Germany and the euro area** (percent):

| date | Bund 10-year | Bund 2-year | AAA 10-year | expected real 10-year (survey) | implied survey inflation | Italy 10-year | France 10-year |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2023-12-29 | 2.06 | 2.35 | 2.08 | −0.01 | 2.17 | 3.82 | 2.65 |
| 2024-12-31 | 2.43 | 2.02 | 2.45 | 0.14 | 2.10 | 3.32 | 3.01 |
| 2025-12-31 | 2.94 | 2.11 | 2.95 | 0.81 | 2.11 | 3.55 | 3.56 |
| 2026-06-30 | 2.93 | 2.50 | 2.92 | 0.94 | 2.10 | 3.73 | 3.68 |
| 2026-09-24 | 3.62 | 3.30 | 3.57 | 1.34 | 2.17 | 3.99 | 4.00 |

The Italian and French yields are monthly averages for the month shown; the latest is August 2026.

**By period, in basis points:**

| period | JGB 10y | JGB 2y | JGB breakeven | Bund 10y | Bund 2y | Bund expected real | Italy–Germany spread |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2024 | +46 | +55 | +20 | +37 | −33 | +16 | −58 |
| 2025 | +95 | +57 | +35 | +51 | +9 | +66 | −40 |
| 2026 to 30 Jun | +62 | +21 | +22 | −1 | +39 | +14 | +3 |
| 30 Jun to 24 Sep | +38 | +53 | +21 | +69 | +80 | +40 | +3 |
| end-2023 to 24 Sep 2026 | **+243** | **+186** | **+97** | **+156** | **+95** | **+135** | **−92** |

**Method notes:**
- **Japan's breakeven** follows the Ministry of Finance's own method: the newest 10-year inflation-indexed JGB against the
  nominal curve at the same remaining maturity. The real yield is computed here, semiannual compound, from the JSDA's
  reference price and the coupon in the Ministry's auction history. The deflation floor on principal is ignored. The
  implied real 10-year subtracts that breakeven from the nominal 10-year, a maturity gap of about half a year.
  - **Checked:** the Ministry's chart for 17 Sep 2026 shows a JGBi yield of 0.836%, a nominal yield at matched maturity of
    2.925% and a breakeven of 2.089%. The same issue computed here gives 0.80% and 2.20% a week later, on 24 Sep, after
    nominal yields rose. A same-day check waits on the JSDA file for 17 Sep, which the JSDA's rate limit has blocked so far.
- **Germany's real yield** is the Bundesbank's expected real rate: the average 10-year Bund yield minus Consensus inflation
  forecasts, monthly. The implied survey inflation uses the month's average Svensson 10-year as a stand-in for that
  average yield.
- **Holder's return:** buy a new 10-year bond at each month's start at that day's yield, price it at the month's end on the
  day's curve, and add the coupon accrued; compound the months. The cash leg is the 1-year yield. The Japanese and German
  curves are treated as par curves, an approximation of a few basis points.

## What this does and does not establish

- **It establishes that** both 10-year yields rose more than the US 10-year. Japan's rise was split between real yields and
  inflation compensation; Germany's was almost all real. Central banks shrank in both markets while banks, pension funds and
  foreign investors absorbed the supply.
- **It does not establish why.** The term premium is not measured, and published estimates are model constructs.
- **It does not measure duration.** R2 measured the rate risk the US public had to absorb, bond by bond. The BoJ's holdings
  by issue and the Ministry's maturity ladder would allow the same for JGBs; the euro area publishes only the
  Eurosystem's weighted average maturity (8.57 years for the PSPP in August 2026).
- **It makes no claim that flows caused the moves.**

## Next

- **Outside review.** R3 has not been attacked. A review parcel for Grok in Cursor, as R12R was for R1 and R2, is next.
- **Duration for JGBs:** the BoJ's holdings by issue (published every ten days) against the Ministry's maturity ladder.
- **A same-day check of Japan's breakeven** against the Ministry's chart, once the JSDA's 17 Sep file can be fetched.
- **A market breakeven for the euro area.** France's inflation-linked bonds are more liquid than Germany's; no free bulk
  source was found in this pass.

## Observed vs derived vs inferred

**Observed:** every yield level, the survey values, the Flow of Funds transactions, SHSS holdings and CSEC debt outstanding.
**Derived by a stated method** (graded MEASURED, and dependent on the method): Japan's JGBi real yields and breakevens,
Germany's implied survey inflation, the holder's returns, and the rest of the world's holdings (a residual).
**Inferred:** that the three front ends moved together for a common reason, and the reading of who absorbed the supply as a
common pattern.
