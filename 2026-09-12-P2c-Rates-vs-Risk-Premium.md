# P2c — what holds the valuation up: real rates or the risk premium (12 Sep 2026)

**Status: PARTLY RETRACTED 13 Sep — see [C-078]. Read this header before quoting anything below.**
The arithmetic stands; the level claim does not. Ranked item 2. Script `bin/rates_vs_premium.py`; data
`_research/2026-09-12-P2c-*.csv`. Attacked by ATT1 (Grok in Cursor) and verified by me, 13 Sep.

**WHAT SURVIVES — and it is the finding.** Between Dec-2023 and Jun-2026 real yields ROSE 0.34 points, which
subtracted multiple, while the equity risk premium COMPRESSED by about 49bp on our trailing construction. That
compression is independently corroborated: Damodaran's forward-looking, growth-adjusted ERP (T12m) fell 40bp
over the same months, 4.60% -> 4.20% (`ERPbymonth.xlsx`, fetched 13 Sep 2026). Two different constructions,
one of them carrying an explicit growth term, move the same way by nearly the same amount. **Rising real
rates were a headwind; premium compression is what held the multiple up, and it is what any money, flow or
liquidity story now has to explain.**

**WHAT IS DEAD — the level claim.** The counterfactual multiple and the share-of-valuation figures this
document originally led with are withdrawn as results. They are baseline-dependent across a four-fold range
(10.9% on a Dec-2023 baseline to 43.1% on 2010-19; ours was one choice among them), the residual embeds
expected growth rather than isolating risk pricing (Damodaran's growth input rose 8.74% -> 13.69% over the
very same window), and the counterfactual pairs a baseline premium with today's real yield when the two are
correlated -0.6991 over 2003-2026. See [C-078] for the full reasoning and the numbers.

**ALSO CORRECTED — do not quote the endpoints.** "The multiple rose only 3.6%" is an artefact of where the
window is cut. The path was 24.35 (Dec-23) -> 28.60 (Dec-24) -> 28.48 (Dec-25) -> 25.22 (Jun-26): it rose
17.5% in 2024 and gave it back in H1-2026 as trailing earnings jumped 22.75%. Quote the path.

**The identity caveat, which this document should have led with.** E/P := r + residual, so a Shapley split of
1/(r+p) sums to the change in P/E *by construction*. The split describes; it does not test. Agreement between
the two legs is arithmetic, not evidence.

**A correction to the project's earlier wording (mine, 12 Sep; still stands):** I had described the multiple holding up while
real yields rose AS the support. That is backwards. The rate move was a drag. The support is premium compression,
and premium compression is what any money, flow or liquidity story now has to explain.

**Timing detail that matters:** almost all the net compression happened in **2024 alone** (-0.86 points). On
trailing earnings the premium was flat to slightly wider in 2025 and the first half of 2026 — though on
cyclically-adjusted earnings it kept compressing, because trailing earnings jumped 22.75% in H1 2026 while the
ten-year earnings base barely moved. The two measures disagree in direction for the most recent half-year.

**Independent cross-check.** Damodaran's forward-looking implied premium (free, his own model) sits 1-5 points
ABOVE our trailing residual at every date — expected, since his model carries a growth term and ours does not. But
its decade-long decline is almost identical (-1.9 points against our -1.87). So: the compression is corroborated;
our LEVEL (about 1.8% today) must not be quoted as "the" equity risk premium — about 4.1% forward is the
defensible level. The two series disagree leg-by-leg for 2015-19.

**What this is not.** An accounting identity (earnings yield = real yield + residual), not a fair-value judgment. A
compressed premium describes how the market prices risk against its own history; it is not proof of mispricing.
And 2020 shows the measure's failure mode: the trailing premium collapsed that year because reported earnings
collapsed, not because risk pricing eased.

---

## The agent's return (Sonnet)

All four CSVs and the script are complete, verified, and reproducible (ran three times with identical output; exit code 0 each time). Deliverables are in `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/wave2/p2c/`: `rates_vs_premium.py`, `monthly_series.csv` (285 rows, 2003-01 to 2026-09), `decomposition_annual.csv` (46 rows), `decomposition_windows.csv` (4 rows), `damodaran_compare.csv` (5 rows). Nothing was written to the read-only project folder. Damodaran's site fetched successfully (HTTP 200) with the specified User-Agent; no fallback needed.

## 1. Window decomposition (trailing E/P, primary measure)

Real yield = FRED DFII10 monthly mean. Premium = trailing E/P − real yield (a backward accounting residual, not a forward premium — see caveats).

**2015-2019 (Dec-2014 → Dec-2019).** E/P 4.98%→4.39% (−0.59pp of earnings yield): real yield fell 0.37pp, premium fell 0.22pp — both compressing, both push the multiple up. P/E 20.08→22.78 (+2.70 points = **+13.4% of the Dec-2014 market value**, earnings held fixed): rate effect **+1.67 points (+8.3% of Dec-2014 value)**, premium effect **+1.03 points (+5.1%)**. Falling *rates* did more of the work than premium compression here (~62/38 split).

**2024-2026 (Dec-2023 → Jun-2026, last month with reported trailing E).** E/P 4.11%→3.96% (−0.14pp): real yield **rose** 0.34pp, premium **fell** 0.49pp. P/E 24.35→25.22 (+0.87 points = **+3.6% of the Dec-2023 market value**): rate effect **−2.14 points (−8.8% of Dec-2023 value)** — a drag — premium effect **+3.01 points (+12.4%)**, more than offsetting it. Within this window, rising real rates *subtracted* from the multiple; all the net expansion (and then some) came from the premium. Non-obvious detail: almost all of the net premium compression happened in **2024 alone** (−0.86pp that year); 2025 and H1-2026 show the trailing premium roughly flat to slightly *widening* (+0.20pp, +0.17pp) — compression here is front-loaded, not a smooth trend.

(Rate/premium effects use the exact two-path Shapley split of P/E=100/(rate+premium), which sums to the true ΔP/E with no leftover cross-term — method documented in the script.)

## 2. How much of the 2024-26 valuation LEVEL each accounts for

Baseline = Jan2015-Dec2019 monthly average (real yield 0.48%, premium 3.96%). At 2026-06, actual P/E = 25.22 (of Jun-2026 earnings).
- ~~Holding premium at the 2015-19 average, today's real yield alone implies P/E 16.30 — actual exceeds it by
  8.92 points = 35.4% of today's actual valuation level (equivalently, actual is 54.7% above that
  counterfactual).~~ **RETRACTED 13 Sep [C-078].** The arithmetic reproduces; the claim does not travel. The
  same computation yields 10.9% to 43.1% depending only on which baseline period is chosen, and the residual
  being held constant contains expected growth, which rose from 8.74% to 13.69% across the window. Quote the
  baseline band or say nothing.
- Holding real yield at the 2015-19 average, today's actual (compressed) premium alone implies P/E 44.06 — actual is *below* it by 18.84 points = **−74.7% of today's actual level**.

Read together: essentially all of today's elevated multiple, and then some, traces to the compressed premium; the rise in real rates is a large partial offset, not a support. (This is a materially more precise statement than "rates rising is the valuation support" — rates were a headwind within the window and remain one relative to the 2015-19 baseline.)

## 3. The four counterfactual P/Es (trailing E)

| Window (end) | Actual P/E | (a) actual rate + baseline premium | (b) baseline rate + actual premium |
|---|---|---|---|
| 2015-2019 (2019-12) | 22.78 | 24.39 (−7.1% of level) | 21.14 (+7.2% of level) |
| 2024-2026 (2026-06) | 25.22 | 16.30 (+35.4% of level) | 44.06 (−74.7% of level) |

Window 1's comparison is near-circular (its own baseline overlaps the window) — ATT0 flagged the same fragility for its B4 metric — so treat only window 2 as a genuine out-of-sample test. Window 2's +35.4% is close to (not identical to) ATT0's own +35.7%, computed on annual averages rather than point-in-time endpoints; the near-agreement is reassuring given ATT0 itself found that convention choice could flip window 1's sign.

## 4. Damodaran cross-check (independent, free, forward-looking)

Damodaran's headline "Implied ERP (FCFE)" (3-stage FCFE/DDM model, current cash yield + analyst growth estimates, minus his own *nominal* T-Bond rate) vs. our trailing residual (real-yield basis):

| Year (Dec) | Ours | Damodaran (nominal) | Damodaran restated on real-rate basis* | Gap (ours − Damodaran, real-basis) |
|---|---|---|---|---|
| 2015 | 3.49% | 6.12% | 7.64% | −4.15pp |
| 2019 | 4.25% | 5.20% | 6.92% | −2.67pp |
| 2023 | 2.27% | 4.60% | 6.78% | −4.51pp |
| 2025 | 1.61% | 4.23% | 6.47% | −4.86pp |
| Latest (Damodaran Sept-2026 vs. our Jun-2026 — 3-month gap, flagged) | 1.79% | 4.09% | 6.38% | −4.60pp |

*restated = Damodaran's ERP + (DGS10−DFII10) breakeven inflation at that date, to put both on the same real-risk-free-rate footing; this is our own transformation, not his reported figure.

**Level**: ours runs 1-5pp below Damodaran's throughout — expected, because his model prices in earnings/cash-flow growth (his own growth assumption is running 10-14% recently) while bare trailing E/P has no growth term and structurally understates any "true" premium. **Direction/magnitude of change** (the part that validates the compression finding): Damodaran's own ERP fell ~1.9pp from 2015 to 2025 (6.12%→4.23%); ours fell ~1.87pp (3.49%→1.61%) — similar total decline despite the large level gap. They do **not** agree leg-by-leg: 2015→2019 ours *rose* (+0.76pp) while Damodaran's *fell* (−0.92pp). **Which way it cuts**: the independent series does not contradict "the premium has compressed" — if anything it shows slightly more cumulative compression since 2015 — but it says our absolute *level* (1.6-1.8% today) should not be read as "the" market risk premium; ~4.1% forward is the more defensible level.

## 5. Does CAPE (cyclically-adjusted earnings) change the answer? Yes, materially

Real yield changes are unaffected by the earnings measure; premium changes are not.
- 2015-19: CAPE yield 3.73%→3.30%; rate effect +2.97 pts, premium effect +0.57 pts (rates ~84% of the expansion, vs ~62% under trailing E — bigger tilt toward rates).
- 2024-26: CAPE yield 3.18%→2.49% (a −0.69pp fall vs. trailing's −0.14pp); P/E(CAPE) 31.45→40.15: rate effect −4.75, **premium effect +13.44** — over 4x the trailing-E premium effect (+3.01). ~~Level share vs. 2015-19 baseline: 52.2% of today's level (CAPE) vs 35.4% (trailing).~~ **[C-103 — WITHDRAWN 22 Sep.** This is the **same method** C-078 killed, run on CAPE earnings instead of trailing, and it survived in this file for ten days because the ban patterns matched the dead claim's *numbers*, not its *method*. Every C-078 ground — free baseline parameter, off-manifold counterfactual, growth embedded in the residual — applies here unchanged. **UNSETTLED** if anyone wants it back: re-run C-078's own six-baseline sensitivity on the CAPE construction.**]
- Caveat: CAPE's counterfactual-(b) P/E for window 2 is 125.7x (gap −213% of level) — a numerically fragile artifact of dividing by a near-zero counterfactual yield (~0.8%), not a serious forecast; don't quote it standalone.
- Genuine sign flip: for Jan-Jun 2026 alone, trailing premium *widened* slightly (+0.17pp) while CAPE premium *kept compressing* (−0.32pp) — because trailing E jumped ~22.75% YTD (mechanically raising E/P), while CAPE's 10-year earnings base barely moved. So the split changes not just in magnitude but, in the most recent half-year, in direction.

## Caveats that matter

1. Trailing E/P has no growth term and is not forward-looking (per the brief). 2020 is the clearest failure mode: the trailing premium fell sharply that year almost entirely because reported trailing E cratered (COVID air-pocket), not because risk pricing eased — CAPE shows the *opposite* sign for premium that year and is the more credible read for that episode.
2. Window-1 counterfactuals are close to circular (baseline = window). Only window 2's level-share numbers are a genuine test.
3. This uses point-in-time month-end endpoints throughout, not annual averages — close to but not identical to ATT0's B4 convention.
4. Rising real rates were a *drag* on the 2024-26 multiple, not a support; wording that conflates "rates rose while the multiple stayed up" with "rates are supporting valuation" is backwards — it's the premium doing the work, against a rate headwind.
5. The Damodaran comparison mixes genuinely different constructs (nominal forward DDM-ERP with a growth term vs. real trailing no-growth residual); only the decade-long direction/magnitude of change, not the level gap, should be read as corroboration.
6. Damodaran's "latest" (Sept-2026) is compared against our Jun-2026 (Shiller trailing E is blank from July 2026 on); a flat-E same-month approximation is in the CSV, clearly flagged as approximate.
7. Shiller's Sept-2026 price is a single-day snapshot per the source file's own footnote — irrelevant to headline figures (which stop at Jun-2026) but relevant if extended later.
8. All of this is an accounting identity (E/P = real yield + residual), not a fair-value judgment — a compressed premium describes how the market is pricing risk relative to history, not proof it is mispricing it.
