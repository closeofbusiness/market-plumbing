# P5(iii) + Jiang-Vayanos-Zheng — is the effect concentrated in the megacaps? (13 Sep 2026)

**Status: RESULT, MIXED — and the mixed part is the honest part.** Ranked item 2, merged from our own
concentration question and the JVZ prediction. Data `data/p5_concentration/`. Supervisor-verified 13 Sep.

**AN ERROR OF MINE THIS CORRECTS.** I wrote in RESEARCH_STATE and told the principal that this test was
"runnable on holdings we already hold." **That was wrong and I never checked it.** The only holdings data on
disk is Norges Bank's own 13F, which cannot support an S&P 500 cross-section. The agent checked and said so.
The test was still runnable — but on prices, not holdings, and the flow side is the binding constraint.

## 1. Concentration: the gap tripled to quadrupled

Measured on **official S&P indices**, not a home-made construction — that choice matters, see the bias note.

| window | basis | cap-weighted | equal-weighted | gap, annualised |
|---|---|---|---|---|
| 2015-19 | price | +55.30% | +43.07% | **+1.78pp/yr** |
| 2015-19 | total return | +72.07% | +55.48% | **+2.24pp/yr** |
| 2024-26 | price | +60.08% | +35.14% | **+7.23pp/yr** |
| 2024-26 | total return | +65.73% | +41.31% | **+6.91pp/yr** |

**Cross-checked by me against our own Shiller series**, which is independent of the agent's price source:
2015-19 cap-weighted +54.64% on monthly averages against its +55.30% on month-end closes — the residual is
exactly the averaging convention. Denominator: 503-name official indices, both windows.

## 2. Idiosyncratic volatility: the direction reversed

Market-model residual against the S&P, per ticker per quarter, minimum 40 daily observations.

| window | top-10 | rest | ratio | n (ticker-quarters) |
|---|---|---|---|---|
| 2015-19 | 14.80% | 21.58% | **0.686** | 200 / 7,233 |
| 2024-26 (2023 list) | 26.92% | 27.83% | 0.967 | 110 / 5,192 |
| 2024-26 (2025 list) | 28.94% | 27.79% | **1.042** | 110 / 5,192 |

**The largest firms went from 31% calmer than the market to level with or above it.** That is the direction
JVZ predict, and it is the half of their prediction that is genuinely falsifiable — price concentration alone
fits many stories.

## 3. And then the dose-response test fails, with the wrong sign

Correlating quarterly ETF-sector net equity purchases (Z.1) against the same-quarter top-10-minus-rest gap:

| window | corr with idio-vol gap | corr with return gap | n |
|---|---|---|---|
| 2015-19 | +0.05 (t≈0.21) | +0.37 (t≈1.70) | 20 quarters |
| 2024-26 | **−0.74 (t≈−3.08)** | −0.06 | 10 quarters |

The lead specification — prior-quarter flow to this quarter's gap, the more literal reading of "following
inflows" — gives **−0.47 and −0.60**, also the wrong sign. The agent also computed a pooled-window
correlation of +0.43 and **declined to lead with it**, flagging it as the level-shift confound this project
has already been caught by three times (C-077, C-078, C-080). That was the right call.

## [E-005 RESTATEMENT, 14 Sep] Read the verdict below as a weak negative, not a refutation

The dose-response test rests on **ten quarterly observations** of an industry-wide flow proxy. Under the
principal's 14 Sep standard, that is weak evidence against the flow linkage — **not** evidence of absence,
and not a reason to stop carrying the passive-bid hypothesis. The concentration and idiosyncratic-volatility
findings below are the robust part and stand on their own.

## Verdict on JVZ: partially present, not attributable

- **Price half: supported.** Top-10 outperformance over equal weight widened from ~2-4pp/yr to ~14-24pp/yr.
- **Idio-vol half: the level shift is there**, in the predicted direction.
- **The link to passive flows specifically: NOT supported.** The quarterly dose-response is insignificant in
  one window and significantly *negative* in the other.

**The alternative explanation is our own prior work.** A genuine earnings concentration in the megacaps —
which F1, the Oracle read and the AI-capex documents establish independently — produces exactly this joint
pattern with no flow mechanism at all. Nothing here distinguishes the two.

## What would settle it, and why we cannot

A **monthly-or-higher-frequency, S&P-500-index-fund-specific flow series.** What exists free is quarterly,
industry-wide and not index-specific. The targeted series live in Morningstar Direct, ICI member data and the
CRSP mutual-fund database — all paywalled, all out of scope. **This is the same shape of failure as the Tier
B first stage: the economics are testable, the flow data is not published at the frequency the test needs.**
That is now twice in one day, on unrelated designs, and it is starting to look like the binding constraint on
the whole money-to-price question rather than a property of either design.

## Method notes worth keeping

- **The P2b guard held.** All 10 names in each of three top-10 lists were confirmed present in both the
  membership snapshot and the price data — 10/10 each time, printed not assumed. That is the specific failure
  that reversed P2b, and it did not recur.
- **A survivorship bias caught and disclosed rather than smoothed.** The agent's own from-scratch "rest of
  market" for 2015-19 covered only 386 of 499 names (79.4%), and the missing fifth skews to names that
  underperformed before disappearing — biasing that comparison *toward* understating the top-10 gap. It led
  with the official equal-weight benchmarks instead. For 2024-26 coverage was 96.4% and the two agree.
- **Bot-detection was respected.** The first price source returned a proof-of-work challenge; the agent did
  not attempt it and switched sources.
