# R3 — Japanese and euro-area government bonds: what moved the 10-year yields, and who bought (27 Sep 2026)

**Status: FINDING, first pass, corrected after outside review. Supervisor, 27–28 Sep.** R1 and R2 asked two questions of US
Treasuries: what moved the 10-year yield (the charter's question 1, prices), and who bought against what net supply
(question 2, money). This note asks both of Japanese government bonds (JGBs) and of euro-area government bonds, with the
German Bund as the benchmark.
- **Corrected 28 Sep (C-126 to C-128)** after Grok's adversarial review (R3R). The levels, both buyer tables and the holder
  returns survived. Three things did not:
  - Japan's breakeven share is a range, not two-fifths.
  - Germany's rise was not almost all real: market breakevens exist, and in 2026 they did about half or more.
  - The common pattern was stated too broadly.
  The adjudication is at the end of [`_research/2026-09-28-R3R-JGB-EGB-Review-Return.md`](_research/2026-09-28-R3R-JGB-EGB-Review-Return.md).
- **Script:** [`bin/r3_jgb_egb.py`](bin/r3_jgb_egb.py). **Tables:** [`data/r3_rates/`](data/r3_rates/).
- **Inputs,** fetched by the script and not redistributed:
  - Japan: the Ministry of Finance's daily JGB yields and its auction history; the JSDA's daily reference prices; the Bank of
    Japan's Flow of Funds, through its data API.
  - Euro area: the Bundesbank's daily Bund yields and its expected real rate; the Deutsche Finanzagentur's daily linker
    breakevens (last twelve months only); the ECB's yield curves, convergence yields, Survey of Professional Forecasters,
    holdings by sector (SHSS) and debt outstanding (CSEC); the ECB's asset purchase programme histories.
- **Dates:** prices run from end-2023 to 24 Sep 2026, pinned so that re-runs reproduce. Holdings run to 2026Q2.

## The answer

1. **Both 10-year yields rose more than the US 10-year did,** though to different end dates. The US 10-year rose 113bp to
   18 Sep (R1), and about 129bp to 25 Sep (R3R).
   - **Japan: 0.65% to 3.07%, +243bp.**
     - Breakeven inflation rose 82 to 97bp, depending on how switches between inflation-indexed issues are handled. Real
       yields took the rest, 145 to 161bp.
     - So inflation compensation did between a third and two-fifths of Japan's rise. In the US it did a sixth.
     - *BOUNDED*: 82bp chains fixed issues; 97bp follows the newest issue. The breakeven's level matches the Ministry of
       Finance's own chart within 3bp (R3R, 17 Sep 2026).
   - **Germany: 2.06% to 3.62%, +156bp, mostly real, but not almost all.**
     - Market breakevens exist only for the last twelve months: the Deutsche Finanzagentur publishes a daily series for each
       inflation-linked Bund. In 2026 the breakevens of the 6.6-year and 19.6-year linkers rose 49bp and 34bp (the 3.6-year's
       rose 70bp), against the Bund's +68bp. So inflation compensation did about half or more of this year's rise.
     - The Bundesbank's survey-based measure missed that. It subtracts Consensus inflation forecasts, and shows the expected
       real rate up 135bp over the window with survey inflation flat.
     - For 2024 and 2025 no market breakeven was obtained. Surveys and the ECB's decomposition of 2025 point to real rates.
     - *HYPOTHESIS* for the full-window split; *MEASURED* for the 2026 linker breakevens as published.
   - The euro-area AAA curve rose 149bp at ten years, close to the Bund.
2. **The front ends rose too, and in the latest quarter they led.**
   - Japan's 2-year rose 186bp, about three-quarters of the 10-year's rise, as the BoJ raised rates.
   - Germany's 2-year rose 95bp. In 2024 it fell 33bp while the 10-year rose 37bp, as the ECB cut.
   - From 30 Jun to 24 Sep 2026 the 2-year rose 80bp in Germany and 53bp in Japan. The US 2-year rose 62bp from 30 Jun to
     18 Sep (R1). *MEASURED; that the three moved together is a reading, not a test.*
3. **Italy's spread over Germany narrowed 92bp, to 80bp. France's widened 27bp, to 82bp.** These are monthly averages,
   December 2023 against August 2026. France now pays about what Italy pays. *MEASURED.*
4. **Whether the rises were term premium or expected rates is not measured here.** No free, maintained term-premium series
   exists for JGBs or Bunds. Published readings:
   - **Japan.** The BoJ estimates that since summer 2024 expected short rates and the term premium have contributed "roughly
     the same degree" to the 10-year's rise. It puts the effect of its purchase cuts at about 25bp, of which about 10bp
     comes from its shrinking holdings (Bank of Japan Review 2026-E-10, August 2026).
   - **Euro area.** The ECB now says the rise in long-term yields since late 2024 was "driven largely by higher real term
     premia" (Economic Bulletin 6/2026). Its model estimate had been stable from late 2023 to June 2025 (Lane, 11 Jun 2025),
     so that earlier reading does not cover this window's largest moves. Over June to September 2026 the ECB puts
     one-year-forward inflation swaps up about 15bp, to 2.3%, with the five-year-forward rate steady near 2.2%.
   - *HYPOTHESIS for any split.* Both are model constructs, which is the lesson of C-102 and C-125.
5. **Holders lost against cash.** A constant-maturity 10-year position, fully revalued and compounded month by month, returned
   −13.9% in Japan against +1.6% for the 1-year. In Germany it returned −4.7% against +6.9%. The Japanese figure sits in line
   with the NOMURA-BPI 7–11 year index on the sub-periods R3R could check. *MEASURED; derived from the yield curves by the
   method below.*
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
   - **The BoJ did not sell outright.** Its holdings fell because redemptions exceeded purchases. The net reduction grew:
     ¥6.0trn in 2024, ¥33.0trn in 2025, ¥24.0trn in the first half of 2026. Its share of JGBs, at market value, fell from
     53.8% to 46.7%.
   - Overseas buying began in 2025 (¥16.6trn); in 2024 it was flat. Insurers turned net sellers in 2025.
   - The GPIF's disclosures imply about ¥31trn of inflows to domestic bonds over the window, against the public pensions'
     +32.3 (R3R). The BoJ's own investor estimate (BoJ Review 2026-E-10, Chart 8) is built from the same Flow of Funds, so it
     checks the arithmetic, not the data.
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
   - **The rest of the world's level is uncertain by about €0.28trn.** The ECB's euro-area total exceeds the sum of the
     20 countries by that much at both dates, and nothing found explains it. Its change moves by under €10bn.
   - Bulgaria's residents left the rest of the world when Bulgaria joined in 2026. That understates the rest of the world's
     rise by roughly €10–17bn (R3R's estimate, not re-derived).
   - The Eurosystem's share fell from 31.1% to 21.1%. Its own programme holdings (PSPP and PEPP public-sector, at amortised
     cost) fell from €4,017bn to €2,983bn over the same months. That total also includes supranational bonds.
   - The ECB notes that the foreign segment increasingly reflects hedge funds, and that its data cannot split it (ECB
     Financial Stability Review, May 2026, box "Along the curve"). That is the same pattern C-124 found in US Treasuries.
8. **Who absorbed the supply differs by market.**
   - **Japan:** banks and public pensions took most of the BoJ's net reduction. Overseas investors joined from 2025, and
     insurers sold.
   - **Euro area:** banks and the rest of the world took most of the Eurosystem's, with investment funds and insurers next.
     Pension funds took 6%.
   - In both, the central bank shrank while governments issued. That the shift in holders moved yields is not tested: the
     charter forbids claiming that flows or official selling caused a yield move, and item 4 shows the premium split is not
     measured. *HYPOTHESIS.*

## The price tables

**Japan** (percent; breakeven at the newest 10-year JGBi's maturity):

| date | 10-year | 2-year | 30-year | JGBi used | JGBi real yield | breakeven | real 10-year (implied) |
|---|---:|---:|---:|---|---:|---:|---:|
| 2023-12-29 | 0.647 | 0.048 | 1.662 | #28 | −0.64 | 1.22 | −0.57 |
| 2024-12-30 | 1.111 | 0.599 | 2.252 | #29 | −0.40 | 1.42 | −0.31 |
| 2025-12-30 | 2.066 | 1.167 | 3.354 | #30 | 0.22 | 1.77 | 0.29 |
| 2026-06-30 | 2.690 | 1.382 | 3.873 | #31 | 0.66 | 1.99 | 0.70 |
| 2026-09-24 | 3.073 | 1.912 | 4.115 | #31 | 0.80 | 2.20 | 0.88 |

On any one date the outstanding JGBi issues disagree by up to 19bp: on 30 Jun 2026, #29 gives 1.80% and #31 gives 1.99%.
Every issue at every key date is in [`data/r3_rates/jp_breakeven_issues.csv`](data/r3_rates/jp_breakeven_issues.csv).

**Germany and the euro area** (percent):

| date | Bund 10-year | Bund 2-year | AAA 10-year | expected real 10-year (survey) | implied survey inflation | Italy 10-year | France 10-year |
|---|---:|---:|---:|---:|---:|---:|---:|
| 2023-12-29 | 2.06 | 2.35 | 2.08 | −0.01 | 2.17 | 3.82 | 2.65 |
| 2024-12-31 | 2.43 | 2.02 | 2.45 | 0.14 | 2.10 | 3.32 | 3.01 |
| 2025-12-31 | 2.94 | 2.11 | 2.95 | 0.81 | 2.11 | 3.55 | 3.56 |
| 2026-06-30 | 2.93 | 2.50 | 2.92 | 0.94 | 2.10 | 3.73 | 3.68 |
| 2026-09-24 | 3.62 | 3.30 | 3.57 | 1.34 | 2.17 | 3.99 | 4.00 |

The Italian and French yields are monthly averages for the month shown; the latest is August 2026.

**German linker breakevens and real yields** (percent, Deutsche Finanzagentur; the series start in late September 2025):

| linker (remaining maturity) | breakeven 30 Dec 2025 | 30 Jun 2026 | 24 Sep 2026 | real yield 30 Dec 2025 | 24 Sep 2026 |
|---|---:|---:|---:|---:|---:|
| DE0001030559 (3.6 years) | 1.64 | 1.71 | 2.34 | 0.75 | 1.03 |
| DE0001030583 (6.6 years) | 1.74 | 1.83 | 2.22 | 0.90 | 1.22 |
| DE0001030575 (19.6 years) | 1.96 | 2.04 | 2.30 | 1.41 | 1.56 |

**By period, in basis points:**

| period | JGB 10y | JGB 2y | JGB breakeven, newest issue | JGB breakeven, fixed issues | Bund 10y | Bund 2y | Bund expected real (survey) | Italy–Germany spread |
|---|---:|---:|---:|---:|---:|---:|---:|---:|
| 2024 | +46 | +55 | +20 | +23 | +37 | −33 | +16 | −58 |
| 2025 | +95 | +57 | +35 | +29 | +51 | +9 | +66 | −40 |
| 2026 to 30 Jun | +62 | +21 | +22 | +9 | −1 | +39 | +14 | +3 |
| 30 Jun to 24 Sep | +38 | +53 | +21 | +21 | +69 | +80 | +40 | +3 |
| end-2023 to 24 Sep 2026 | **+243** | **+186** | **+97** | **+82** | **+156** | **+95** | **+135** | **−92** |

In the first half of 2026 most of the newest-issue breakeven's +22bp is the switch from issue #30 to #31; holding #30, it
rose 9bp.

**Method notes:**
- **Japan's breakeven** is close to the Ministry of Finance's method, which sets the newest 10-year inflation-indexed JGB
  against a 10-year coupon JGB of the same maturity. The nominal leg here is the Ministry's constant-maturity curve at that
  maturity instead; the two differ by 1 to 4bp (R3R).
  - The real yield is computed here, semiannual compound, from the JSDA's reference price and the coupon in the Ministry's
    auction history. The deflation floor on principal is ignored; R3R's rough estimate of its value is under 1bp at these
    yields.
  - "Newest issue" follows the benchmark as it changes. "Fixed issues" holds, for each period between key dates, the issue
    that was newest at the start, and chains the periods.
  - The implied real 10-year subtracts the newest-issue breakeven from the nominal 10-year, a maturity gap of about half a
    year.
  - **Checked:** on 17 Sep 2026 R3R found this method within 3bp of the Ministry's chart (0.836% real, 2.089% breakeven).
    The supervisor could not re-fetch that day's JSDA file, because of the JSDA's rate limit.
- **Germany's survey real yield** is the Bundesbank's expected real rate: the average 10-year Bund yield minus Consensus
  inflation forecasts, monthly. The implied survey inflation uses the month's average Svensson 10-year as a stand-in for
  that average yield. It cannot see market inflation compensation or its risk premium, which is why it missed 2026.
- **German linkers** are the Finanzagentur's published breakevens and real yields. Germany stopped issuing linkers in 2024,
  so their breakevens carry liquidity premia. Their window rolls: the cached page is what reproduces the table.
- **Holder's return:** buy a new 10-year bond at each month's start at that day's yield, price it at the month's end on the
  day's curve, and add the coupon accrued; compound the months. The cash leg is the 1-year yield. The Japanese and German
  curves are treated as par curves, an approximation of a few basis points.

## What this does and does not establish

- **It establishes that** both 10-year yields rose more than the US 10-year. In Japan inflation compensation did between a
  third and two-fifths of the rise. In Germany the rise was mostly real over the window, but in 2026 inflation compensation
  did about half or more. Central banks shrank in both markets: banks and public pensions absorbed Japan's supply, banks
  and foreign investors the euro area's.
- **It does not establish why.** The term premium is not measured, and published estimates are model constructs.
- **It does not measure duration.** R2 measured the rate risk the US public had to absorb, bond by bond. The BoJ's holdings
  by issue and the Ministry's maturity ladder would allow the same for JGBs. The euro area publishes only the Eurosystem's
  weighted average maturity (8.57 years for the PSPP in August 2026).
- **It makes no claim that flows caused the moves.**

## Next

- **Duration for JGBs:** the BoJ's holdings by issue (published every ten days) against the Ministry's maturity ladder.
- **A market breakeven for Bunds before late 2025.** Candidates: archived Finanzagentur pages, France's inflation-linked
  bonds, or an ECB inflation-swap series. Any of them would test the full-window split.
- **The rest of the world's level:** an ECB explanation of the gap between its euro-area total and the country sum.

## Observed vs derived vs inferred

**Observed:** every yield level, the survey values, the Finanzagentur's linker breakevens as published, the Flow of Funds
transactions, SHSS holdings and CSEC debt outstanding.
**Derived by a stated method:** Japan's JGBi real yields and breakevens (BOUNDED by the issue choice), Germany's implied
survey inflation, the holder's returns, and the rest of the world's holdings (a residual).
**Inferred:** the full-window real share for Bunds, that the three front ends moved together for a common reason, and that
GPIF flows stand in for public pensions' JGB purchases.
