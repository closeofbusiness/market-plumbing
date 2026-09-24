# The safe-asset share re-examined

Is the constant Gorton-Lewellen-Metrick share a null on quantity, or an equilibrium that
safe-asset supply itself produces? Raised as an operator objection to a project claim.

**Answer: the null fails, but not for the reason proposed — and what replaces it is stronger.**

*21 August 2026.*

---

# SYNTHESIS AND ADVERSARIAL VERIFICATION

**What I verified independently:** the standard-error and elasticity arithmetic below is my own, computed from GLM's published Table 1 alone (no data required — it back-solves the residual variance from their reported coefficients, t-statistics and R²). It reproduces GLM's *other* reported standard error to the digit, which is the check that makes it trustworthy. No Z.1 archive exists on this machine, so I could **not** re-run either researcher's reconstruction; where I rely on those, I say so and I flag where the two disagree.

---

## 1. IS THE OPERATOR RIGHT THAT THE GLM NULL DOES NOT HOLD?

**The arithmetic first, since he asked for it (Researcher 1's levels, 1952:Q4 → 2026:Q1):**

| | 1952:Q4 | 2026:Q1 | multiple | CAGR |
|---|---|---|---|---|
| Numerator (safe assets, GLM high est.) | $0.642trn | $114.13trn | **177.8×** | 7.33% |
| Denominator (all-sector liabilities + equity) | $1.736trn | $415.10trn | **239.1×** | 7.76% |
| Share | 36.98% | 27.49% | — | — |

**He is right, and the arithmetic settles the narrow question: yes, the numerator grew — about 178-fold nominally. A constant ratio over a 239-fold denominator is not a statement that safe-asset quantity was stable. Anyone using GLM as a quantity null is misusing it.**

But the arithmetic is the weakest part of his case, because it is compatible with every hypothesis on the table. Four things are stronger, and three of them attack the premise rather than the inference.

**(a) The premise is wrong. "s.e. 0.003" is not the tightness of the share — it is the standard error of a regression intercept, and it understates the dispersion by a factor of 7.7.** This is my own verification, from GLM's numbers only:

- t = 114.76 on a constant of 0.332 ⟹ unrounded se(const) = 0.002893
- For t = 1…239: Σ(t−t̄)² = 1,137,640; the intercept's design factor is 0.129776
- ⟹ residual SD **s = 0.02229**
- Check: that s predicts se(trend) = **0.0000209**, and GLM report **0.00002**. It also recovers their trend coefficient from their own t-statistic (−1.72 × 0.0000209 = −0.0000359 → prints as −0.00004). The back-out is right.
- With R² = 0.012, the **unconditional SD of the share is 0.0224 = 2.24 percentage points**; CV = 6.7%; the implied ±2SD band is **28.7% to 37.7%, a nine-point range.**

Researcher 1 got 0.0231 by the same route and cross-checked it against the Fed's own FEDS Note (2020), which reports SD = 2.3%. Three routes, one answer: **~2.2–2.4pp, not 0.3pp.** The phrase "constant to three decimal places over seven decades" is a misreading that entered downstream of GLM; GLM label their standard error correctly and never make that claim.

**(b) The constancy is a property of one of two constructions GLM publish side by side, and the choice is undefended.** Same table, same data, same window; the only difference is an 85% haircut on MBS/ABS and long-term financial debt that the paper asserts without derivation. On the **low** estimate: trend −0.00021 (se 0.00002), **t = −11.71, R² = 0.367, −5.0pp over the sample** (I reproduce the −5.00pp from their own coefficient). And I back out its residual SD as 0.0191 — **the two constructions have the same dispersion; they differ only in whether the series trends.** The literature cites the flat one. That is a selection, not a finding.

**(c) R² = 0.012 against a linear trend is not evidence of constancy.** It is evidence of no linear drift, which a driftless random walk also delivers — and a random walk is the *opposite* of constant. GLM run no unit-root or mean-reversion test. Their Table 1 cannot distinguish "constant at 33.2%" from "persistent series that happened to start at 37% and wander." The out-of-sample record discriminates, and it discriminates against constancy.

**(d) It does not survive extension, and the break is statistically sharp.** Two independent reconstructions on the 2026:Q1 vintage:

| | R1 | R2 |
|---|---|---|
| 2011:Q3–Q4 | 34.13% | 35.15% |
| 2026:Q1 | 27.49% | 27.99% |
| minimum of 297 quarters | 26.95% (2025:Q4) | 27.45% (2025:Q4) |

Both agree on the minimum's date, converge to within 0.5pp, and each replicates the GLM-window intercept to within 0.3pp (R2: 0.3294 ± 0.0030 vs GLM's 0.332 ± 0.003). Against the in-sample distribution I derived above, 2026:Q1 sits at **z = −2.33 to −2.55**, i.e. *outside the 95% band implied by GLM's own regression*. The post-2011 trend of −0.000776/qtr (NW se 0.000154) differs from the in-sample trend at **t = −4.76**. The published FEDS Note extension (mean 31.1%, SD 2.3%, 1952–2020) independently shows the drift beginning.

**(e) Where the operator's mechanism is wrong — and this matters, because his stated mechanism is the one a referee will kill.**

His claim is that constancy is mechanical *because safe supply drives the valuation in the denominator*. Two problems.

First, **"drives" does not deliver constancy; only a unit elasticity does.** The realised long-run elasticity dlogN/dlogD over 1952–2026 is **0.946**. That 5.4% shortfall is *exactly* the whole story: it takes the share from 36.98% to 27.49%. An elasticity of 0.98 would have put the 2026 share at 33.1%, 1.00 at 36.98%. The result requires a knife edge, and the knife edge is demonstrably not held.

Second, **rising equity valuation moves the share the wrong way for his story.** It enlarges the denominator without enlarging the numerator, pushing the share *down*. Both researchers find this dominates the residual variation: R2 gets share = 0.3943 − 0.4735 × (equity/denominator), R² = 0.670, corr = −0.818; R1's variance decomposition of log(share) attributes 55.0% to the equity-valuation term. Valuation is what *breaks* the constancy, not what manufactures it.

**The real mechanical problem is simpler and worse than the one he identified: the numerator is a strict subset of the denominator.** Co-movement in the par block is close to accounting. And GLM ran a Monte Carlo against precisely this and **did not clear it** — per Researcher 1's read of the paper, ~30% of simulated coefficients were smaller than their Panel B −0.466. Mechanical construction remains a live, un-rejected explanation of their own headline result, by their own test.

**Verdict on (1): the operator is right that the null fails, right that the numerator grew, and wrong about the mechanism. His conclusion survives on stronger grounds than his argument. Give him the subset point — it needs no causal claim at all.**

---

## 2. THE PAR-VERSUS-MARKET POINT

**Half right, and the wrong half is load-bearing. State it plainly: the characterisation was an inference and it does not survive contact with the construction.**

**The numerator side is confirmed, and by direct measurement rather than inference.** Researcher 2's decomposition of the narrow par-money numerator's $97.53trn level change 1951:Q4–2026:Q1: **98.8% transactions, 0.3% revaluation, 0.9% other volume changes.** Treasury liabilities carry a revaluation series that is *identically zero in all 297 quarters* (FR313161105.Q). On the household side, 77–79% of the safe block is par by construction (deposits + MMF at $1 NAV). The numerator is par. Confirmed.

**The denominator side is wrong, in three distinct ways.**

1. **It is not wealth.** It is FL894194005, the unconsolidated sum of financial liabilities and equity across all sectors. It double-counts every intermediated claim — 1.32× US net wealth in 1952, **2.51× today.**
2. **It contains no real estate at all.** Housing is not a liability of any sector, so it cannot appear. Household nonfinancial assets, **$62.93trn at 2026:Q1**, are entirely outside it. The project's phrase "equities and real estate" describes an aggregate that contains neither in the way implied.
3. **It is majority par.** R2's level-change decomposition: 1952–2026 is **61.5% transactions / 36.8% revaluation**; across GLM's own window it was **79.4% / 18.1%.**

So the "striking co-movement between a par numerator and a market-valued denominator" is not the object. Both sides are dominated by par claims; the numerator is inside the denominator; and the dispersion is 2.2pp, not 0.3pp. **Three legs of the framing fail simultaneously.**

**What survives, and it is the better version of the point:** the denominator's market-valued fraction is *growing*, and that growth is what ends the constancy. R2's revaluation share of the denominator's change: 18.1% across GLM's window → **49.2% (2011–2026) → 66.6% (2022:Q4–2025:Q4)**. This is the same fact the project already established from the other side (80.2% of the 2023–25 net-worth rise was holding gains — ⚠ **the "83.7% equity-linked" formerly cited here is withdrawn per C-046: a 61.7%–83.7% range turning on the pension-entitlement treatment, not a measured value. The 80.2% stands and carries this argument on its own.**). GLM's window is the last era in which the denominator was predominantly a transactions aggregate. **The constancy held while the denominator behaved like a quantity and failed once it started behaving like a valuation.** That is a real, publishable, and considerably sharper claim than the one the project made — and it makes the *par* character of the numerator the interesting asymmetry rather than a coincidence.

**⚠ Unresolved measurement dispute you must settle before publishing any level.** R1 and R2 disagree materially on how much of the denominator is market-valued:

| | 1952:Q4 | 2011:Q3 | 2026:Q1 |
|---|---|---|---|
| R1 (corporate equities + mutual fund shares only) | 11.6% | ~19.7% (2010:Q4) | **31.1%** |
| R2 (+ DI equity, pension entitlements, life reserves) | 42.9% | 39.1% | **52.4%** |

They disagree on the level by ~21pp and on the *sign of the long-run change*. R1's justification ("the Z.1 revalues only these") is too narrow — DC pension entitlements move one-for-one with the market value of underlying assets, and direct-investment equity is market-valued in the Z.1. R2's set is closer to economic substance; R1's is closer to the published FR revaluation series. **Do not publish either level until reconciled.** The saving grace: both reach the same *qualitative* conclusion — equity valuation is the dominant driver of the headline ratio's variation (R² 0.67 / variance share 55%) — so the conclusion is robust to the definition even though the levels are not.

---

## 3. DIRECTION OF CAUSATION

**Neither (2) nor (3). The honest answer is third factor plus accounting, and I will not split the difference: both of the operator's causal hypotheses are rejected in their strong forms by the evidence already in hand, and no aggregate observational design can separate their weak forms.**

**Against (2), wealth-driven demand — this is the strongest single result in the dossier:**
- Household safe-asset holdings have **zero elasticity to wealth: β = −0.071 (NW se 0.088); H₀: β = 1 rejected at t = −12.1** (DFA, 1989:Q3–2026:Q1). Safe assets are bought out of *saving*, and ~76–80% of the wealth increase is revaluation, which generates no saving. This is the mechanism the project already established, running in reverse.
- At the aggregate: dlog(safe) on dlog(equity wedge) = **−0.0077 (se 0.0132), R² = 0.001.** Equity revaluation does not move the safe stock. At all.
- Cross-sectionally the gradient runs the *wrong way*: the top 0.1% hold a *lower* safe share (15.8%) than the bottom 50% (25.7%). Bach–Calvet–Sodini and Fagereng et al. corroborate — richer holders take *more* risk, not less.

**Against (3), collateral-driven supply:**
- The measured shadow price of Treasury collateralisability is **0.53bp** (se 0.009) over ~540,000 repo transactions. A channel priced at half a basis point cannot deliver percentage-point moves in aggregate valuations. This is the magnitude gate and (3) fails it by orders of magnitude.
- The only fully-specified structural model (Lenel 2018) puts a QE2-sized safe-asset shock at **−28bp on bills, +1bp on corporate bonds, equity effect negligible.**
- Haddad–Muir: the intermediary risk-appetite factor prices credit (0.57, se 0.22) and MBS (0.30, se 0.13) but **not stocks (0.12, se 0.09, R² = 0.8%).** Equities are ~84% of the revaluation in question, and they are the asset class intermediary constraints demonstrably do *not* reach.
- Lead-lag: wealth Granger-causes repo (Σ = +1.624, R² = 0.174); repo does not Granger-cause wealth (Σ = −0.0043).
- Margin debt is **1.33% of equity market value** and untrended against its own history. The direct leverage channel into equities is too small to carry the claim.

**What survives, and it is positive rather than merely negative:** the safe-asset stock scales with **nominal income**, not with wealth and not with collateral demand. Long-run elasticity to nominal GDP ≈ **1.05**; short-run cyclical coefficient **−0.278 (t = −2.76)** — the exact signature of a nominal buffer stock, accumulating in downturns and tracking nominal output over the long run. Nagel closes the loop: the T-bill supply coefficient collapses from −95.35 (se 27.83) to **−9.51 (se 12.00)** once the fed funds rate enters. The variable doing the work in this literature is the monetary stance, and it is a common driver of both sides of the ratio.

**Two adversarial corrections I owe, both against researchers on my own side of this verdict:**

**Researcher 3's headline is start-date dependent and materially misleading as stated.** "The collateral multiplier ran backwards" rests on repo-per-Treasury falling from **1.070 (2007:Q4)** to 0.219 (2026:Q1). 2007:Q4 is the peak of the pre-crisis shadow-banking build-out. Researcher 4's own series shows repo/GDP going **0.000 (1952) → 0.283 (2007) → 0.143 (2026)**. Over 1952–2007 the multiplier ran *strongly forwards*. The correct statement is that the collateral multiplier rose enormously through 2007 and has been compressed since — which is *consistent with* an episodic collateral channel switched off by post-crisis regulation, i.e. with Geanakoplos, not a refutation of him. Do not publish 1.070 → 0.219 as a trend. (R3 also flags, correctly, that it mixes measurement bases and so violates the project's own rule.)

**Researcher 4's "no in-sample variation in the collateral first stage" is overstated.** Federal liabilities/GDP went **0.84 (1952) → 0.49 (1980) → 0.87 (2011)** — a 42% fall then a 78% rise. That is substantial low-frequency variation; it merely happens to be endpoint-equal. The correct claim is not "no variation" but "no *exogenous* variation": the 1952–80 fall is inflation eroding nominal war debt (endogenous to the price level, i.e. to the very third factor at issue) and the 1980–2011 rise is deficits driven by the cycle and by policy.

**And the asymmetry nobody stated:** hypotheses (2) and (3) are **not symmetrically testable.** You can shock safe-asset supply exogenously; you cannot shock household wealth exogenously. So (3) is falsifiable and (2) is not, with available instruments. **A paper that eliminates (3) may not therefore conclude (2).** This is the trap the operator's own framing sets, and it must be closed explicitly.

**Restated as a verdict:** the constancy requires no causal explanation, because the numerator is a subset of the denominator and both scale with nominal income. The residual variation is equity valuation. The operator's dichotomy is a false one applied to an artefact.

---

## 4. THE DISCRIMINATING TEST

**Assessments, then the pick.**

**Debt-ceiling episodes (2011, 2013, 2015, 2021, 2023, 2025) — reject as primary.** Fatal confound: a debt-ceiling standoff *is itself a risk event*. The outcome variable both hypotheses bet on (the risk premium) moves for a third reason — technical default fear — which neither hypothesis is about. And post-2013 the ON RRP is an elastic safe-asset substitute that breaks the first stage: quantity contracts in bills are absorbed rather than transmitted.

**The 2023 post-suspension bill deluge — reject as primary, keep as description.** Researcher 4's RRP-absorption reading is genuinely clever: the fraction of >$1trn of net bill issuance absorbed by MMF drawdown of ON RRP rather than by new saving directly measures whether the demand schedule pre-existed. Keep that as a descriptive statistic. But it is n = 1 and it sits inside H2 2023 — the largest monetary-policy repricing in a decade. Nagel's warning at maximum force. Not identification.

**QE — reject, and note it is the *worst* candidate despite the intuitive appeal.** Reserves sit *inside* the safe numerator ($2.468trn in 2011:Q3 → $12.430trn in 2026:Q1). QE is therefore a within-numerator composition swap, not a quantity shock, executed simultaneously with the strongest available signal about the policy path. Any post-2008 lead-lag it produces is a third factor by construction.

**QT / RRP drain 2022–25 — keep as secondary.** Better than QE: pre-announced, calendar-based, largely not state-contingent; ~$2.5trn out of the RRP and ~$2trn of Treasuries returned to private balance sheets. Still inside the rate cycle.

**Levered vs unlevered asset classes — already run.** Haddad–Muir *is* this test, and it returns 0.57 on credit, 0.30 on MBS, 0.12 (se 0.09) on stocks. Existing best evidence, and it points against (3) reaching equities.

**BEST — the mid-April tax-date bill-supply surprise (Lenel's design), extended to equities, gated three ways.** Regress the outcome on the *unexpected* component of Treasury issuance in the week around mid-April tax dates. Why it wins: (i) a one-week window makes it wealth-orthogonal by construction; (ii) the FOMC does not respond to April receipts within a week, so it survives Nagel where every episode-based design does not; (iii) it repeats — ~20 events 2005–2026 — so it has power that n = 1 episodes never will; (iv) **it already has a published, identified first stage on credit (slope 4.9bp per 1% of consumption, against a model prediction of 4.1bp)**, which supplies both a validity check and a magnitude benchmark.

Three gates, all of which must clear:
1. **Mechanism.** The shock must move the observable price of collateral — Ross's maturity-matched collateral spread, GC repo minus IORB, non-centrally-cleared haircuts. *If bill supply surges and the collateral spread does not compress, no collateral channel operated regardless of what equities did.*
2. **Outcome.** The response of the aggregate equity valuation ratio / ERP. Wealth-driven demand predicts ≈ 0; collateral-driven supply predicts > 0.
3. **Magnitude.** The equity coefficient must be reconcilable with a 0.53bp shadow price and 4.9¢ marginal dealer pass-through per Treasury dollar. **A large equity coefficient without a corresponding move in gate 1 is evidence of a fiscal-news confound, not of collateral.** Run credit and MBS in parallel as positive controls; the collateral hypothesis requires the equity coefficient to be of the same order as the credit coefficient.

**DECISIVE COMPLEMENT, and underweighted by all four researchers — regulatory changes to collateral eligibility.** The SLR exemption (granted April 2020, expiry announced 19 March 2021, effective 31 March 2021), the LCR HQLA definitions, and the 2023 Treasury clearing mandate all change the **collateral *value* of an unchanged stock**. That is the cleanest possible separation of "quantity of safe assets" from "collateral capacity" — precisely the distinction hypothesis (3) requires and precisely what a pure supply shock cannot give you, because supply shocks move both. The SLR expiry is a sharp, dated, **quantity-neutral** shock to intermediary balance-sheet capacity. If capacity rather than quantity is the operative variable, this is where it shows, and nothing else in the candidate set isolates it.

**And the honest limit, which must go in the paper:** these designs can *kill* hypothesis (3) and can never *establish* hypothesis (2). Nor do they address the low-frequency claim — the leverage cycle is episodic, not linear, and a linear regression at any frequency is the wrong instrument for it. The episodic case survives everything above: March 2020, September 2019 and quarter-end CIP dislocations show the constraint binds occasionally and hard, and nothing in this dossier bounds what a *binding* episode does to valuations. Only what a non-binding steady state does.

**One historical note.** The largest wealth-orthogonal safe-asset supply shock in US history is the WWII debt build-up and its post-war erosion — federal debt/GDP fell from ~106% (1946) to 0.84 (1952). **GLM's sample begins in 1952:Q1 and excludes it by construction.** Extending the series back to 1945:Q4, where the Z.1 permits, is the cheapest available increase in identifying variation and nobody has done it.

---

## 5. PUBLISHABILITY

**The honest output is a negative finding plus a well-posed question. Both are publishable. No causal claim is.**

### He CAN claim (verifiable, and the first three need no data at all)

1. **The cited standard error is a regression intercept's, not the share's dispersion.** Residual SD ≈ 2.2–2.4pp; CV ≈ 6.7%; implied ±2SD band 28.7%–37.7%. Back-out from GLM's own table, cross-validated because it reproduces their reported se(trend) exactly, and corroborated by the Fed's own FEDS Note (SD 2.3%). **This is arithmetic on published numbers and cannot be contested.**
2. **The constancy is a knife-edge property of an undocumented 15% haircut.** GLM's low estimate, same table, trends −5.0pp at t = −11.7, R² = 0.367. Both constructions have the same dispersion. The literature cites one.
3. **R² = 0.012 against a trend is not evidence of constancy** — it is evidence of no linear drift, which a driftless random walk also delivers. GLM run no mean-reversion test.
4. **Numerator ×177.8, denominator ×239.1, 1952:Q4 → 2026:Q1.** A constant ratio is not a quantity null. Realised long-run elasticity 0.946 against the 1.000 constancy requires.
5. **The constancy does not extend.** ~27.5–28.0% at 2026:Q1, sample minimum in 2025:Q4, z = −2.3 to −2.6 against GLM's own in-sample distribution, trend break at t = −4.8. *With the caveat below on reconstruction.*
6. **The denominator is not wealth.** Unconsolidated gross claims, 2.51× US net wealth, containing no owner-occupied housing ($62.9trn), no durables, no non-produced assets.
7. **The numerator is a strict subset of the denominator, and GLM's own Monte Carlo did not clear mechanical construction.**
8. **Equity valuation, not safe-asset supply, drives the residual variation** (R² 0.67, corr −0.82; variance share 55%) — and it drives the share *down*.

### He MUST NOT claim

- **That the numerator is par and the denominator market value.** Both sides are majority par; there is no real estate in the denominator; it was an inference and it does not survive.
- **Any causal direction.** Not (2), not (3), not "both." Nothing here identifies one.
- **That FL894194005 *is* GLM's denominator.** It is an identification by inference — their verbatim phrase plus three quantitative checks (assets/GDP 4.56–4.58× and 11.01–11.09× against their stated ~4× and ~10×, factor 2.41 against their 2.5, and reproduction of their intercept and standard errors). **That is strong evidence and it is not a citation.** Write to Gorton, Lewellen and Metrick before it appears as one.
- **That either reconstruction is GLM's series.** ~20 appendix series were retired in the 2013 restructuring. Both rebuilds are top-down. State this in the text, not a footnote.
- **The sign of the trend inside the GLM window, in either direction.** Vintage-dependent: GLM got −0.00004 on a 2011 vintage; the rebuilds get +0.000025 to +0.000046 on the 2026 vintage. Both indistinguishable from zero. Cite it as "no detectable trend," never as a sign.
- **That collateral supply does not affect valuations.** Only the non-binding steady-state linear version is rejected. The episodic case is untouched.
- **That wealth-driven demand is falsified.** It is falsified *for households, 1989–2026*. Institutional cash pools — corporate treasurers, insurers, reserve managers, securities lenders, the actual marginal demanders in the Pozsar account — were not measured by anyone here.
- **The repo/Treasury 1.070 → 0.219 ratio.** Peak-start, mixed measurement bases, violates the project's own rule. Cut it.
- **Researcher 2's +0.509 private-on-government complementarity, until reconciled.** It carries the *opposite sign* to KVJ's −0.5 and to GLM's own Panel B −0.466. Different specification (transactions on transactions, GDP-controlled) versus theirs (ratios on debt/GDP). Both cannot appear in one paper unreconciled; a referee will find it immediately.
- **The margin-debt/market-cap ratio from a secondary aggregator.** Replace with FINRA's own Rule 4521(d) release.

### The form of words that survives a competent economist

> Gorton, Lewellen and Metrick (2012) report that the safe-asset share of total US financial claims averaged 33.2% between 1952 and 2011 with no significant time trend, and the figure is widely cited as though the share were constant to within ±0.3 percentage points. It was not. The 0.003 is the standard error of a regression intercept, correctly labelled by the authors; the implied standard deviation of the share itself is approximately 2.2 percentage points, roughly seven and a half times larger, and the series ranges over some nine points inside their own sample. The same table reports a second construction of the same numerator, differing only in an undocumented 15% haircut on mortgage- and asset-backed securities, on which the share declines five points over the identical window at t = −11.7. The constancy is a property of one of two constructions, and the paper does not defend the choice.
>
> Two independent reconstructions on the June 2026 vintage of the Financial Accounts place the share at 27.5% and 28.0% at 2026:Q1 — between 2.3 and 2.6 in-sample standard deviations below the reported mean, and outside the 95% band implied by the original regression — with the minimum of 297 quarters in 2025:Q4. Neither is the authors' own series: approximately twenty of their appendix series were retired in the 2013 restructuring of the accounts, and both rebuilds are top-down. Both nevertheless replicate the original intercept to within 0.3 percentage points, and both find the same post-2011 decline.
>
> The share is better described as a highly persistent series with no linear drift inside a sixty-year window than as a constant. An R² of 0.012 against a time trend is evidence of the former, not the latter; a driftless random walk produces the same statistic.
>
> Two features of the construction bear on how the result should be read. The denominator is not aggregate wealth but the unconsolidated sum of financial liabilities and equity across all sectors — 2.5 times US net wealth today, containing no owner-occupied housing, no consumer durables and no non-produced assets. And the numerator is a strict subset of that denominator, so co-movement between them is partly an accounting identity rather than an economic fact. The authors tested this with a Monte Carlo and did not clear it: roughly 30% of simulated coefficients were smaller than the one they report. Mechanical construction remains an un-rejected explanation of the finding, by the paper's own test.
>
> Finally, a constant ratio does not follow from safe-asset supply "driving" the denominator. Constancy requires the elasticity of numerator to denominator to be exactly one. The realised long-run elasticity over 1952–2026 is 0.946, and that shortfall alone accounts for the entire fall in the share from 37.0% to 27.5%. Within the sample, what moves the ratio is not safe-asset supply but equity valuation, which enlarges the denominator without enlarging the numerator and therefore pushes the share down: the equity share of the denominator explains between 55% and 67% of the ratio's variance, with a correlation of −0.82. On the transactions-versus-revaluation split, the denominator's growth was 79% transactions across the original window and 49% since, and 67% revaluation over 2022–25. The constancy held while the denominator behaved like a quantity, and failed once it began behaving like a valuation.
>
> What determines the safe-asset share is therefore not settled by this series, and we do not settle it here. Household safe-asset holdings show zero elasticity to wealth and unit elasticity to nominal income, which is inconsistent with the wealth-driven reading; the measured shadow price of Treasury collateralisability is half a basis point and the intermediary risk-appetite factor does not price equities, which is inconsistent with the collateral-driven reading at the aggregate steady state. Neither hypothesis is identified by the ratio, and neither can be, because the numerator lies inside the denominator. Identification requires variation that hits one side only.

### The question that is the better paper

**The headline ratio is not the invariant. The par-over-par ratio is.** Safe assets over the ex-equity denominator: **45.1% (2011:Q3) → 45.0% (2026:Q1)**, full-sample CV 5.3% against 7.7% for the headline — dead flat over the fifteen years in which the headline fell seven points. Be careful: **a CV of 5.3% is more stable, not constant, and it is not "the constant."** But it is the better candidate for a structural invariant than the number everyone cites, and **nobody has explained it.**

That is the publishable frame: *the famous constant is not the constant; here is the one that is more nearly so; we do not know why, and here is the design that would find out.* A sharp unanswered question, properly posed, is a paper. An overclaimed answer is a retraction.

---

## MUST RESOLVE BEFORE PUBLICATION

1. **Write to Gorton, Lewellen and Metrick** to confirm the denominator series. Without a reply, FL894194005 is an inference and must be worded as one.
2. **Retrieve the AER website appendix** (Tables A.5/A.6). Only the NBER WP appendix was read, and it itemises the numerator only — it never documents the denominator.
3. **Reconcile R1 vs R2 on the market-valued fraction** (31.1% vs 52.4% at 2026:Q1, and opposite long-run signs). Turns on whether DC pension entitlements, life reserves and direct-investment equity count. Levels are unpublishable until settled; the qualitative conclusion is robust to it.
4. **Reconcile the +0.509 complementarity against KVJ's −0.5 and GLM's own −0.466.** Sign flip. A referee will find it.
5. **Drop or rebuild the repo/Treasury multiplier.** Peak-start and mixed-basis.
6. **Correct "no in-sample variation in federal liabilities/GDP."** It varied 0.84 → 0.49 → 0.87. The claim is *no exogenous* variation.
7. **Replace the margin-debt figure** with FINRA's own release.
8. **Nothing here re-verified** the project's Gabaix–Koijen, KVJ or Fed FSR figures. Four researchers all disclaimed them. They are outside every lens run and must be checked before they appear alongside verified material.

**On the record:** the operator found in one reading an error that four research passes carried. His conclusion is right and his stated mechanism is not — and the corrected mechanism (numerator ⊂ denominator; a knife-edge unit elasticity; equity valuation moving the ratio *down*) is stronger than the one he proposed, because it requires no causal claim at all. That is the version to publish.