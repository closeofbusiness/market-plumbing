# R1 — What moved the US 10-year Treasury yield, end-2023 to 18 Sep 2026 (27 Sep 2026)

**Status: FINDING, corrected after outside review. Supervisor, 27 Sep.** This is the first rates pass: the charter's question 1
(prices), for US Treasuries.
- **Corrected 27 Sep (C-125)** after Grok's adversarial review (R12R). The levels, the real-yield split and the model reads
  survived. The survey check did not: it now uses the true survey deadlines and splits the horizon at four years. The holder's
  return is now fully revalued and compounded. The adjudication is at the end of
  [`_research/2026-09-27-R12R-Rates-Review-Return.md`](_research/2026-09-27-R12R-Rates-Review-Return.md).
- **Script:** [`bin/r1_treasury_decomposition.py`](bin/r1_treasury_decomposition.py).
- **Tables:** [`data/r1_rates/`](data/r1_rates/).
- **Inputs,** fetched by the script and not redistributed:
  - the US Treasury's daily nominal and real par yield curves;
  - the New York Fed's ACM term-premium estimates;
  - the Fed Board's Kim-Wright estimates;
  - the Philadelphia Fed's Survey of Professional Forecasters (SPF) and its release-date file.
- **Dates:** 18 Sep 2026 is the last date all four sources cover.

## The answer

1. **The 10-year rose 113bp, from 3.88% to 5.01%, and real yields did almost all of it.** The 10-year TIPS yield rose 96bp, and
   inflation compensation (the breakeven) rose 17bp. *MEASURED; the two parts sum to the total by identity.*
   - The window opens just after a 119bp rally: the 10-year was 4.98% on 19 Oct 2023 and 3.79% on 27 Dec 2023. Measured from
     that October peak, the rise to 18 Sep 2026 is 3bp. A week after the window, on 25 Sep 2026, it was 5.17%.
2. **Over the full window the long end rose more than the front end.** The 2-year rose 53bp, so the gap between the 10-year and
   the 2-year widened by 60bp, from −35bp to +25bp. Over the equity window, which ends on 30 Jun 2026, the 2-year fell 9bp while
   the 10-year rose 56bp. *MEASURED.*
3. **Most of the rise is recent, and the front end led it.** The 10-year stood at 4.04% on 13 Feb 2026, so 97bp of the 113bp
   came after that. Over the same months the 2-year rose 136bp. In the latest quarter alone the 10-year rose 57bp and the 2-year
   62bp. *MEASURED.*
4. **Whether the rise was a higher term premium or higher expected rates is not settled on free data, and the dispute is about
   years 5 to 10.**
   - Over the full window, both yield-curve models put most of the rise on the term premium: ACM 97bp of 107bp, Kim-Wright 87bp
     of 109bp.
   - Between the SPF's first-quarter surveys of 2024 and 2026, all three measures say the expected short rate for the next four
     years fell: the survey by 54bp, ACM by 118bp, Kim-Wright by 72bp.
   - For years 5 to 10 they split. The survey implies a rise of 61bp; ACM says a fall of 56bp and Kim-Wright a fall of 8bp. The
     FOMC's median longer-run federal funds rate rose with the survey, from 2.5% in December 2023 to 3.1% in June 2026 and 3.2% in
     September 2026.
   - If the surveys are right about the long horizon, most of the models' term-premium rise is expectations. A term premium is
     whatever a model's expectations leave over, which is the lesson of C-102 in the equity work. So this split is a model
     construct. *HYPOTHESIS.*
5. **Holders lost against cash.** A constant-maturity 10-year position returned about +3.5%, fully revalued and compounded month
   by month. Rolling three-month bills returned about +12.9% over the same window. The first-order split is income +11.6%,
   roll-down +1.0% and price −9.3%. *MEASURED; derived from the par curve by the method below.*

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
direction is common to both, and the surveys dispute its long-horizon part.

## The survey check

Each survey is dated by its response deadline, from the Philadelphia Fed's release-date file. Rates are percent; changes are
basis points.

| survey (deadline) | 10y par | ACM expected, years 1–4 / 5–10 | Kim-Wright expected, years 1–4 / 5–10 | SPF bill rate, years 1–4 / 5–10 | SPF 10-year bond yield |
|---|---:|---:|---:|---:|---:|
| 2024Q1 (6 Feb 2024) | 4.09 | 4.57 / 4.11 | 4.10 / 3.84 | 3.67 / 2.28 | 3.55 |
| 2025Q1 (11 Feb 2025) | 4.54 | 4.26 / 4.09 | 3.94 / 3.90 | 3.50 / 2.89 | 3.99 |
| 2026Q1 (2 Mar 2026) | 4.05 | 3.39 / 3.55 | 3.39 / 3.77 | 3.12 / 2.90 | 3.90 |
| **change, 2024Q1 to 2026Q1** | **−4** | **−118 / −56** | **−72 / −8** | **−54 / +61** | **+35** |

Over the whole ten years, ACM's expected rate fell 81bp and Kim-Wright's 33bp, while the SPF's expected bill rate rose 15bp.

**The survey covers 2026.** The years 1–4 forecasts are asked every quarter. From the 2026Q1 survey to the 2026Q3 survey
(deadline 11 Aug 2026), the SPF's four-year average rose 35bp, ACM's four-year expected rate 58bp and Kim-Wright's 47bp, while
the 10-year par yield rose 65bp. All levels are in [`data/r1_rates/survey_check.csv`](data/r1_rates/survey_check.csv).

**Caveats:**
- Years 1–4 for the survey are its annual forecasts for the current and next three calendar years, which approximate the four
  years after each deadline. Years 5–10 are implied as (10 × the ten-year average − 4 × years 1–4) / 6, for the survey and the
  models alike.
- The survey's expected bill rate is for a three-month bill: close to, but not the same as, the models' expected short rate.
- Kim-Wright uses survey forecasts to estimate its parameters, but its daily changes are driven by yields. It is not a survey
  measure.
- The 2026Q1 survey was delayed by the federal government shutdown.

**Cross-check:** the Kim-Wright term premium in this pull is 0.519% on 13 Feb 2026 and 0.839% on 14 Aug 2026. That matches the
"~0.52% to 0.82–0.85%" the Treasury-buyers synthesis quoted from a secondary source ([`2026-09-11-Who-Buys-Treasuries-Synthesis.md`](2026-09-11-Who-Buys-Treasuries-Synthesis.md)),
which is now re-pulled from the Fed Board's own file.

## A holder's return, in percent

| period | income | roll-down | price | total, first-order | total, full revaluation | three-month bills |
|---|---:|---:|---:|---:|---:|---:|
| 2024 | 4.21 | 0.12 | −5.83 | −1.51 | −1.37 | 5.39 |
| 2025 | 4.27 | 0.54 | 3.16 | 7.97 | 8.30 | 4.32 |
| 2026 to 30 Jun | 2.11 | 0.29 | −2.14 | 0.27 | 0.27 | 1.84 |
| 30 Jun to 18 Sep | 1.01 | 0.08 | −4.53 | −3.43 | −3.34 | 0.85 |
| end-2023 to 30 Jun 2026 | 10.59 | 0.95 | −4.81 | 6.73 | 7.11 | 11.96 |
| end-2023 to 18 Sep 2026 | 11.60 | 1.03 | −9.34 | 3.29 | 3.54 | 12.91 |

**Method:** month by month on the Treasury par curve.
- **The first-order split,** summed over the months:
  - income is the yield times the time elapsed;
  - roll-down is modified duration times the 7-to-10-year slope per year, times the time elapsed;
  - the price effect is minus duration times the change in yield.
  It leaves out convexity, which is why its total runs below the full revaluation.
- **The full revaluation** buys a new 10-year par bond at each month's start and prices it at the month's end, as a slightly
  shorter bond on that day's curve, plus the coupon accrued. The months are compounded. Grok's review computed the same figures
  independently: +3.54%, −1.37, +8.30 and +7.11.
- **Bills** earn the three-month yield times the time elapsed, compounded.

This is a derived measure on the par curve, not an index; a free daily total-return index for the full window was not found.

## What this does and does not establish

- **It establishes that** the 10-year's rise came from real yields. Over the full window the long end rose more than the 2-year.
  Most of the rise came after February 2026, and in that stretch the front end led.
- **It does not establish why.** All three measures agree that expected short rates for the next four years fell over 2024–26.
  They split on years 5 to 10, and there a term premium cannot be told apart from long-run expectations on free data.
- **It says nothing about who bought.** That is question 2 (R2).
- **It makes no claim that flows caused the move.** The charter forbids claiming that FX, official buying or commodity flows
  caused a yield move.
- **It covers the US only.** JGBs and euro-area government bonds are a later pass (R3).

## Next

- **R2, who bought against what net supply:** done, in
  [`2026-09-27-R2-Treasury-Duration-Supply-And-Holders.md`](2026-09-27-R2-Treasury-Duration-Supply-And-Holders.md).
- **R3: JGBs and euro-area government bonds,** from Japan's Ministry of Finance and the ECB's free data.
- **The long horizon.** The free long-horizon surveys are the SPF's ten-year questions (first quarter only) and the FOMC's
  longer-run projections. Blue Chip's long-range survey would add a third but is not free. Market-implied rates for the next two
  to three years (SOFR futures) would add a market check on the near end.

## Observed vs inferred

**Observed:** every change in level (the Treasury curves), the model outputs (ACM, Kim-Wright), the survey values (SPF, FOMC) and
the survey deadlines.
**Derived by a stated method** (graded MEASURED, and dependent on the method): the holder's return.
**Inferred:** the years 5–10 survey rate (by subtraction, from calendar-year forecasts), and the period readings (which end of the
curve led).
