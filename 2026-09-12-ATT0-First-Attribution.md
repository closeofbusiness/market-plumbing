# ATT0 — the first attribution, and what it rules out (12 Sep 2026)

**Status: RESULT (negative, and load-bearing).** The goal's central question is what drives asset prices and where
the money comes from. This is the first attempt to size the flow channel against the fundamentals benchmark.
Inputs: `2026-09-11-P1-Equity-Net-Buyers.md` (who bought), `2026-09-11-P2a-Return-Decomposition.md` (earnings vs
valuation), `2026-09-11-P3-Price-Impact-Multiplier.md` (the multiplier, no central value — C-077).
Data: `data/att0/attribution_v0.csv` (18 rows), `data/att0/benchmarks.csv`; script `bin/attribution_v0.py`.

## What the test was

Three candidate flow objects x three multipliers (2, 5, 9) x two windows, against four benchmarks. The design is
the one the outside reviewer proposed when it overturned the earlier M = 5 decision (`_research/P3R_verification_2026-09-12.md`).

## What it found — three things, in order of confidence

**1. A constant multiplier applied to aggregate flows is refuted by the sign test.** In 2015-19 the market's total
net flow was NEGATIVE ($-396bn) while market value rose $16.2trn; nonfinancial-corporate net issuance was more
negative still ($-2,244bn, buybacks). Both predict a falling market at every multiplier. Only the switching object —
ETF net purchases minus mutual-fund net purchases (+$1,604bn) — carries the right sign.

**2. No single multiplier fits both windows, so the scalar itself is not stable.** The switching object matches the
multiple-expansion component at about x3 in 2015-19 (C x 2 = $3.2trn and C x 5 = $8.0trn bracket B3 = $4.8trn), but
the same object needs a multiplier BELOW 1 in 2024-26 (C x 2 = $8.9trn against B3 = $3.3trn, an overshoot of 2.7x).
A channel whose coefficient has to move by a factor of three between windows is not yet a measured channel.

**3. The two benchmarks disagree, and that disagreement is the real finding.**
- Against earnings alone, valuation explains only **7.6%** of the 2024-26 price change — about **$3.3trn** of a
  $46.9trn rise in market value. On this benchmark the run-up is an earnings story and the flow channel's maximum
  room is small.
- Against a constant risk premium at today's real yields, the market sits about **36% above counterfactual —
  roughly $44trn**. Holding the multiple flat while real yields rose from ~0.5% to ~2.0% IS the valuation support;
  measuring against earnings alone hides it.
The gap between $3.3trn and $44trn is the whole argument about what drives prices, and it is a question about the
risk premium and real rates, not one a flow multiplier can answer.

## What this changes in the plan

- The flow channel cannot be sized by multiplier arithmetic on Z.1 lines. Sizing it needs demand elasticities by
  holder sector (a demand system), or an event-based design — a new item, not a rerun of this one.
- The decisive work is now the (e) benchmark, extended: decompose the price/earnings multiple into the part real
  yields explain and the part the risk premium explains, by window. That is where both a liquidity story and a
  fundamentals story must show themselves.
- B4 is fragile and must not be quoted alone: its 2015-19 value flips sign depending on whether the final-year
  multiple is taken from the average earnings yield (-$2.4trn) or the point-in-time ratio (+$0.6trn), and its
  baseline window is the same window it scores, which makes window 1 near-circular. Window 2 is directionally
  stable (+$44.2trn vs +$41.2trn).

## Supervisor checks (12 Sep)

The switching object reproduces from P1's own figures ($2,460.9bn ETFs minus -$2,009.0bn mutual funds = $4,469.9bn)
and the 7.6% valuation share reproduces from P2a's annual rows (1.1747 x 0.9958 x 0.8856 = 1.036 against a price
factor of 1.590). The agent re-derived every figure from the quarterly file rather than the pre-aggregated one and
cross-checked 16 aggregates. Objects are holder-role flows; the issuer-basis alternative is materially larger and is
recorded in `benchmarks.csv`.

---

## The computing agent's return (Sonnet)

## Attribution v0 — computed and cross-checked

Output written (read-only project folder untouched):
- `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/wave1/att0/attribution_v0.csv` (18 rows)
- `.../att0/benchmarks.csv` (2 rows, one per window, all inputs included)
- `.../att0/attribution_v0.py` (reproducible; reads only the three named source files; re-derives everything from `netbuyers_quarterly_2026Q2.csv` rather than trusting the pre-aggregated periods file, then cross-checks against it — all 16 cross-checks passed to the 4th decimal)

All dollar figures are $bn. Every ratio below is `predicted_bn ÷ BX_bn` (dimensionless); every percentage names what it's a percentage **of**.

### Benchmarks per window

| | 2015Q1–2019Q4 | 2024Q1–2026Q2 |
|---|---|---|
| B1 = end level − start level (Z.1, All sectors/total) | 53325.518 − 37131.603 = **16193.915** | 123687.233 − 76767.801 = **46919.432** |
| B2 = Σ revaluation, same rows | **16590.254** | **43676.319** |
| B3 = (log P/E change ÷ log price change) × B2 | share = 0.126096/0.435938 = **28.93%** of the log price change → **4798.761** | share = 0.035284/0.463842 = **7.61%** → **3322.408** |
| B4 = (gap between actual and counterfactual avg P/E, ÷ actual avg P/E) × end level | gap −0.985 PE ÷ 21.542 actual PE = **−4.57%** of end-level market value → **−2437.485** | gap +9.344 PE ÷ 26.174 actual PE = **+35.70%** → **44155.246** |

B3/B4 inputs: window 1 uses calendar years 2015–2019 from `decomp_annual.csv`; window 2 uses 2024, 2025, and **the 2026_YTD row (Jan–Jun 2026 only — not a full year, as instructed)**. B4's 2015–2019 average ERP baseline (3.957%, fixed, used for both windows) plus each window's own TIPS average (0.482% weighted by trading days for window 1; 1.985% for window 2) gives the counterfactual earnings yield, inverted to a counterfactual P/E, compared against 100÷earnings_yield_avg_pct in the window's final year (2019: 21.542; 2026 YTD: 26.174).

### 18-row prediction table (compact; $bn; ratios = predicted÷benchmark)

```
Window   Obj  Value($bn)   M   Predicted   /B1     /B2     /B3     /B4
15-19    A     -396.3      2     -792.7   -0.05   -0.05   -0.17    0.33
15-19    A     -396.3      5    -1981.7   -0.12   -0.12   -0.41    0.81
15-19    A     -396.3      9    -3567.1   -0.22   -0.22   -0.74    1.46
15-19    B    -2244.0      2    -4487.9   -0.28   -0.27   -0.94    1.84
15-19    B    -2244.0      5   -11219.8   -0.69   -0.68   -2.34    4.60
15-19    B    -2244.0      9   -20195.6   -1.25   -1.22   -4.21    8.29
15-19    C     1604.0      2     3208.1    0.20    0.19    0.67   -1.32
15-19    C     1604.0      5     8020.2    0.50    0.48    1.67   -3.29
15-19    C     1604.0      9    14436.4    0.89    0.87    3.01   -5.92
24-26    A     3243.1      2     6486.2    0.14    0.15    1.95    0.15
24-26    A     3243.1      5    16215.6    0.35    0.37    4.88    0.37
24-26    A     3243.1      9    29188.0    0.62    0.67    8.79    0.66
24-26    B     -540.7      2    -1081.4   -0.02   -0.02   -0.33   -0.02
24-26    B     -540.7      5    -2703.6   -0.06   -0.06   -0.81   -0.06
24-26    B     -540.7      9    -4866.4   -0.10   -0.11   -1.46   -0.11
24-26    C     4469.8      2     8939.7    0.19    0.20    2.69    0.20
24-26    C     4469.8      5    22349.2    0.48    0.51    6.73    0.51
24-26    C     4469.8      9    40228.5    0.86    0.92   12.11    0.91
```
(A = total net issuance; B = nonfinancial-corporate net issuance, issuer role; C = ETF holder flow − mutual-fund holder flow. Full precision in the CSV.)

### Wrong sign in 2015–2019
Since M is always positive, `sign(predicted) = sign(object value)`. B1, B2 and B3 are all **positive** in 2015–2019 (the market rose). Object A (−396.3) and object B (−2244.0) are both negative, so **all 6 combinations — A×{2,5,9} and B×{2,5,9} — predict a fall in market value against an observed rise: wrong sign, at every M.** Object C (+1604.0) has the correct sign at all three M values. (Object B is also negative, and therefore wrong-signed against B1/B2/B3, in 2024–2026 — not asked for, but the same arithmetic fact.)

### Within a factor of two (ratio between 0.5 and 2.0, same direction)

**vs B3:**
- 2015–19: C×2 (0.67x), C×5 (1.67x). [A×9 and B×2 land at 0.74x/0.94x magnitude but with the opposite sign, so not counted as a match.]
- 2024–26: A×2 (1.95x) only. [B×5 and B×9 land at 0.81x/1.46x magnitude but opposite sign.]

**vs B4:**
- 2015–19: A×5 (0.81x), A×9 (1.46x), B×2 (1.84x) — all same-sign because B4 itself is negative here. [C×2 is 1.32x in magnitude but opposite sign.] Note: B4's baseline years and this window's years are identical, so this benchmark is close to a circular check for window 1, not an independent one.
- 2024–26: A×9 (0.66x), C×5 (0.51x), C×9 (0.91x).

### Ambiguities resolved (with the material alternative shown)
1. **Object A** = `All sectors,total` flow (the Z.1 identity total). Unambiguous — confirmed against the P3 doc's own header, which quotes this same −$396bn figure for 2015–19.
2. **Object C** = ETF **holder** flow − mutual-fund **holder** flow (net purchases of the underlying equities), not ETF **issuer_detail** flow (new ETF-share creation) minus mutual-fund holder flow. The P3 header's own figures (+$2.46trn ETF / −$2.01trn MF, 2024–26) match the holder-role numbers exactly, confirming this choice. **Alternative (issuer_detail basis) is materially different:** 2147.058 vs 1604.049 (2015–19); 5612.771 vs 4469.832 (2024–26) — both in `benchmarks.csv`.
3. **B4's window TIPS average**: weighted by trading-day count per `decomp_annual.csv`'s `n_days_tips` (window 2 mixes two full years with one 173-day half-year). Simple-average alternative barely moves it (44292.3 vs 44155.2 in window 2) — immaterial.
4. **B4's "actual average P/E in the final year"**: computed as 100÷`earnings_yield_avg_pct` (matching the same yield→P/E inversion used for the counterfactual), not the point-in-time `PE_end`. **This one is materially different, including sign, in window 1**: avg-yield basis gives B4 = **−2437.5**; point-in-time `PE_end` basis gives B4 = **+585.8** (opposite sign). Window 2 is directionally stable either way (44155.2 vs 41151.1). Both bases are in `benchmarks.csv`.

### Inputs I could not compute
None — every figure the brief asked for was computable from the three named files. The four items above are stated choices with alternatives shown, not gaps.
