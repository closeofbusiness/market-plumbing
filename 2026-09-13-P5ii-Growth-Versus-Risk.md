# P5(ii) — is the compression cheaper risk, or higher expected growth? (13 Sep 2026)

**Status: THE TEST RAN AND DID NOT RESOLVE IT. That is the result.** Ranked item 1. Data
`data/p5_growth_vs_risk/`. Supervisor-verified 13 Sep.

## Why this was the load-bearing test

Our central finding is that a compressed premium held the market up while real rates were a drag. But our
premium is **E/P minus the real yield** — a residual with no growth term. If investors expect faster growth,
that lands in the residual and looks identical to cheaper risk. C-078 registered the principle; this test was
meant to quantify it.

## What the comparison gives

Damodaran's ERP is forward-looking with an explicit growth input. **Verified structurally by me:
`ERP(T12m) = Expected Return − T.Bond Rate` holds on 216 of 216 dated rows, zero failures** — so his measure
genuinely nets growth by construction, which is what makes the comparison meaningful.

Over Dec-2023 → Jun-2026:

| measure | change | denominator |
|---|---|---|
| our trailing residual | **−48.59bp** (2.2718% → 1.7859%) | our own Dec-2023 level |
| Damodaran ERP, nominal | −40.00bp (4.60% → 4.20%) | his reported figure |
| Damodaran ERP, restated to a real-rate basis | **−29.31bp** (6.7845% → 6.4914%) | our breakeven-inflation transform |
| Damodaran's expected-growth input | **+495bp** (8.74% → 13.69%) | his reported figure |

> **[C-104, 22 Sep] THE 60.3% IS A BASIS CHOICE, NOT A MEASUREMENT.** The −29.31bp is this project's own transform (splicing Damodaran's T-Bond with a FRED breakeven), and his T-Bond differs from FRED DGS10 by 14.0bp at Dec-2023. On an equally valid, fully FRED-consistent restatement the figure is **−17.4bp and the headline becomes 35.7%** — a 25-point swing. Quote the range across both bases or neither. **The “at least ~40%” growth floor below takes −29.31bp as an input and has NOT been re-run against −17.4bp.**

~~**The direct reading: ≈29 of our 49bp (60.3%) survives as compression Damodaran's model does not attribute
to growth.** That leans toward genuinely cheaper risk.~~ **[C-104 — the NUMBER is withdrawn, 22 Sep.** The section
below is right that 60% is a ceiling rather than a finding; what it does not say is that **the ceiling's own value is a
basis choice**. On a fully FRED-consistent restatement it is **−17.4bp, i.e. 35.7%**, not 60.3%. Carry the range across
both bases. The growth floor was re-run 22 Sep (Grok) and **holds** — ~64% growth-consistent on the FRED basis → `_research/2026-09-22-P5ii-Growth-Floor-Rerun-C104.md`.**]

## Why that 60% is a ceiling and not a finding — three reasons, all verified

1. **It requires trusting a model we cannot inspect.** The 60% holds only if Damodaran's multi-stage model
   fully nets out a growth revision this large. His explicit-phase length and terminal growth rate are not in
   the file. Unverifiable, and load-bearing.
2. **The 2015-19 control period inverts the relationship.** There, ours fell 22.43bp while his real-basis
   measure fell 55.87bp — a ratio of **249%**, against 60% in the main window. And his growth input *fell*
   162bp in the control against *rising* 495bp in the main window (**both verified exactly by me**). The sign
   flip is consistent with an omitted-growth story; the **five-fold difference in implied sensitivity is not
   consistent with anything stable.**
3. **Applying the control window's own sensitivity to the main window flips the sign of the answer** — it
   implies growth did more than all the work and the real risk premium *widened* ~54bp. I do not believe that
   as a point estimate (n=2 windows, different regimes), but its internal consistency means **the data cannot
   rule out "mostly or entirely growth."**

The agent also tested and correctly rejected the obvious shortcut: capitalising the growth change 1:1 through
a single-stage Gordon model implies a −495bp effect, **10.2× the entire observed move** — proof that a
near-term explicit-phase growth number cannot be treated as a perpetual growth rate.

## The defensible bounds

**The growth-consistent share of our 49bp compression is at least ~40% (19bp), and on a logically consistent
but less defensible extrapolation could exceed 100%.** A clean three-way split into risk, growth and
construction difference **is not achievable from these two files**, and saying otherwise would be false
precision.

## A sub-finding that matters on its own: the compression has already reversed

Splitting our own window: Dec-2023 → Dec-2025 earnings grew 25.05%; then **Dec-2025 → Jun-2026 earnings
jumped 22.75% against prices +8.71%, and our premium measure WIDENED by +17.36bp** — reversing direction.
Verified against our monthly series (1.6123% at Dec-2025 → 1.7859% at Jun-2026). Virtually all the net
compression is concentrated in 2024, reconfirming P2c's "front-loaded" finding from a different angle, and
meaning **the compression is not an ongoing process we are describing in the present tense.**

## What would actually settle it

Two measures cannot identify three components. **This needs a third, independently constructed premium** —
one built on forward earnings we can inspect, or a survey-based expected return, or the New York Fed's own
implied-ERP model. That is the concrete next step, and it is a data-acquisition task, not a modelling one.

## Data-quality notes on Damodaran's file, found and verified

- **2026-03-01 expected growth reads 0.83%, between 10.80% (Feb) and 12.13% (Apr)** — an evident data error
  in the source. **It does not touch either window endpoint**, so no number above is affected. Flagged, not
  corrected.
- One row (2024-09-01) is stored as text rather than a date; one cell uses a comma decimal. Neither is used
  in a headline figure.

## Consequence for how we speak about the finding

**Stop calling the residual a "risk premium" without qualification.** The honest phrasing is *"the gap
between the earnings yield and the real rate compressed"*, plus the open question of what that gap is made
of. The compression is real and independently corroborated in direction; **its interpretation is not
settled, and this test is the evidence that it is not.**

> **[C-104 re-run, 22 Sep]** Growth floor vs −17.4bp: see `_research/2026-09-22-P5ii-Growth-Floor-Rerun-C104.md`. Floor ≥~40% **holds** (FRED basis → ~64% growth-consistent). Risk share is a **36–60% range**, not 60.3%.
