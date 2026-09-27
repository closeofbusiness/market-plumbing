# R1 — What moved the US 10-year Treasury yield, end-2023 to 18 Sep 2026 (27 Sep 2026)

**Status: FINDING. Supervisor, 27 Sep.** This is the first rates pass: the charter's question 1 (prices), for US Treasuries.
- **Script:** [`bin/r1_treasury_decomposition.py`](bin/r1_treasury_decomposition.py).
- **Tables:** [`data/r1_rates/`](data/r1_rates/).
- **Inputs,** fetched by the script and not redistributed:
  - the US Treasury's daily nominal and real par yield curves;
  - the New York Fed's ACM term-premium estimates;
  - the Fed Board's Kim-Wright estimates;
  - the Philadelphia Fed's Survey of Professional Forecasters.
- **Dates:** 18 Sep 2026 is the last date all four sources cover.

## The answer

1. **The 10-year rose 113bp, from 3.88% to 5.01%, and real yields did almost all of it.** The 10-year TIPS yield rose 96bp, and
   inflation compensation (the breakeven) rose 17bp. *MEASURED; the two parts sum to the total by identity.*
2. **The long end rose more than the front end.** The 2-year rose 53bp, so the gap between the 10-year and the 2-year widened by
   60bp, from −35bp to +25bp. Over the equity window, which ends on 30 Jun 2026, the 2-year fell 9bp while the 10-year rose 56bp.
   *MEASURED.*
3. **Most of the rise is recent.** The 10-year stood at 4.04% in mid-February 2026, so 97bp of the 113bp came after that. In the
   latest quarter alone it rose 57bp, and the 2-year rose 62bp alongside it, so the most policy-sensitive maturities moved just as
   much. *MEASURED.*
4. **Whether the long-end rise was a higher term premium or higher expected rates cannot be measured on free data.**
   - Over the full window, both yield-curve models put most of the rise on the term premium: ACM 97bp of 107bp, Kim-Wright 87bp
     of 109bp.
   - February 2024 to February 2026 is the only span the survey covers. Over it, the models' expected path of short rates fell
     (ACM −92bp, Kim-Wright −39bp), while forecasters' expected average bill rate rose (+15bp). The signs are opposite.
   - A term premium is whatever a model's expectations leave over, which is the lesson of C-102 in the equity work. So this split
     is a model construct. *HYPOTHESIS.*
5. **Holders lost against cash.** A constant-maturity 10-year position returned about +3.3%: income +11.6%, roll-down +1.0%, and
   price −9.3%. Rolling three-month bills returned about +12.2% over the same window. *MEASURED; a derived approximation.*

## By period, in basis points

| period | 10y | 2y | real 10y | breakeven | ACM: expected / term premium | Kim-Wright: expected / term premium |
|---|---:|---:|---:|---:|---|---|
| 2024 | +70 | +2 | +52 | +18 | −13 / +82 | +11 / +60 |
| 2025 | −40 | −78 | −31 | −9 | −62 / +27 | −27 / −12 |
| 2026 to 30 Jun | +26 | +67 | +27 | −1 | +47 / −24 | +10 / +13 |
| 30 Jun to 18 Sep | +57 | +62 | +48 | +9 | +37 / +13 | +28 / +26 |
| end-2023 to 30 Jun 2026 (the equity window) | +56 | −9 | +48 | +8 | −28 / +85 | −6 / +61 |
| end-2023 to 18 Sep 2026 | +113 | +53 | +96 | +17 | +9 / +97 | +22 / +87 |

The model columns decompose each model's fitted zero-coupon yield, so their totals differ from the par-yield change by a few basis
points.

**Reading the curve** (MEASURED; the labels are interpretation):
- **2024:** the long end led. The 10-year rose while the 2-year stayed flat.
- **2025:** the fall was led by the front end, as rate cuts were priced.
- **2026:** the rise was led by the front end, as the policy path was repriced upward. In the latest quarter the whole curve rose
  by about the same amount.

The two models' year-by-year splits disagree with each other, in 2025 and early 2026 even in sign. Only the full-window
direction is common to both, and the survey disputes even that for the years it covers.

## The survey check

| survey (February) | 10y par | ACM expected | Kim-Wright expected | SPF: 10-year average bill rate | SPF: 10-year bond yield |
|---|---:|---:|---:|---:|---:|
| 2024 | 4.27 | 4.38 | 4.03 | 2.84 | 3.55 |
| 2025 | 4.47 | 4.15 | 3.90 | 3.13 | 3.99 |
| 2026 | 4.04 | 3.46 | 3.64 | 2.99 | 3.90 |
| **change, Feb 2024 to Feb 2026** | **−23bp** | **−92bp** | **−39bp** | **+15bp** | **+35bp** |

**Caveats:**
- The survey is annual (February), and its latest reading predates the 2026 rise.
- Its expected bill rate is the 10-year average of a three-month bill: close to, but not the same as, the models' expected short
  rate.
- Kim-Wright uses survey forecasts in its estimation, so it is not independent of surveys.
- The 14 February reference date approximates the survey deadline.

## A holder's return, in percent

| period | income | roll-down | price | total | three-month bills |
|---|---:|---:|---:|---:|---:|
| 2024 | 4.21 | 0.12 | −5.83 | −1.51 | 5.26 |
| 2025 | 4.27 | 0.54 | 3.16 | 7.97 | 4.23 |
| 2026 to 30 Jun | 2.11 | 0.29 | −2.14 | 0.27 | 1.82 |
| 30 Jun to 18 Sep | 1.01 | 0.08 | −4.53 | −3.43 | 0.85 |
| end-2023 to 30 Jun 2026 | 10.59 | 0.95 | −4.81 | 6.73 | 11.32 |
| end-2023 to 18 Sep 2026 | 11.60 | 1.03 | −9.34 | 3.29 | 12.17 |

**Method:** month by month on the Treasury par curve.
- Income is the yield times the time elapsed.
- Roll-down is modified duration times the 7-to-10-year slope per year, times the time elapsed.
- The price effect is minus duration times the change in yield.

The months are summed, not compounded, so this is a rough band (E-005), not an index.

## What this does and does not establish

- **It establishes that** the 10-year's rise came from real yields and from the long end, concentrated after February 2026 and in
  the latest quarter.
- **It does not establish why.** A higher term premium and higher long-run expected rates cannot be told apart here: three
  measures give three answers.
- **It says nothing about who bought.** That is question 2, next (R2).
- **It makes no claim that flows caused the move.** The charter forbids claiming that FX, official buying or commodity flows
  caused a yield move.
- **It covers the US only.** JGBs and euro-area government bonds are a later pass (R3).

## Next

- **R2: who bought, against what net supply.**
  - Supply: net duration supply, meaning Treasury issuance in 10-year equivalents, bills versus coupons, and the Fed's runoff.
  - Holders: the Fed's Financial Accounts, TIC data on foreign official and private buyers, and the cash-futures basis trade.
  - It reuses what the repository already has; an inventory is under way.
- **R3: JGBs and euro-area government bonds,** from Japan's Ministry of Finance and the ECB's free data.
- **Near-term expectations:** market-implied rates for the next two to three years (SOFR futures) could separate the near end of
  item 4. Nothing free reaches the 10-year horizon.

## Observed vs inferred

**Observed:** every change in level (the Treasury curves), the model outputs (ACM, Kim-Wright) and the survey values (SPF).
**Inferred:** the holder-return approximation, and the period readings (which end of the curve led).
