# P5(iv) — a third premium measure, and what it says about risk versus growth (14 Sep 2026)

> **[C-082] CORRECTED 15 Sep 2026.** The headline split below is withdrawn. The survey premium fell because
> the BOND leg rose (+34.5bp) by more than the equity leg (+15.4bp) — **forecasters expected MORE from
> equities at the end of the window, not less.** Calling that "cheaper risk" inverts what the survey says.
> The direction of the compression is corroborated across three constructions; the two-fifths/three-fifths
> decomposition is not, and must not be quoted. See C-082.
>
> **[C-105, 22 Sep] THIS BANNER NOW ALSO COVERS THE BODY.** The claim that the **monotonic ordering is evidence** — described below as the first evidence "that does not depend on trusting anyone's model" — is withdrawn on C-082's own stated grounds: the ordering *"is collinear with how much each series is allowed to move, and is not identified as growth control."* The banner previously fixed the sign inversion and the split number and left the method standing.



**Status: RESULT. The third measure exists, and it sharpens P5(ii) without fully settling it.**
Data `data/p5_third_measure/`. Supervisor-verified 14 Sep.

## Two candidates I ranked highest are dead — corrections to my own brief

- **The New York Fed equity risk premium (Duarte-Rosa) is not maintained.** Published once, covering
  1960-2013; the Liberty Street "equity risk premium" tag carries a single post dated 2014-05-14 and nothing
  since. There is no data file. I ranked this first in the brief; it does not exist as a usable series.
- **The Cleveland Fed publishes no equity premium at all.** Both of its "risk premium" products are
  Treasury/TIPS-market quantities.

## What does exist: a survey-elicited premium from a single panel

**Philadelphia Fed Survey of Professional Forecasters**: `STOCK10` (expected 10-year annualised S&P 500
return) and `BOND10` (expected 10-year annualised Treasury bond return), **asked of the same forecasters, in
the same survey, over the same horizon**. Their difference is an equity risk premium with **no model in it
at all** — no dividend-discount machinery, no yield arithmetic, no growth assumption to trust. That is what
makes it genuinely independent of both measures we hold.

Annual, Q1 only, 1992-2026. The differencing step is mine, not the agent's.

## The result: three measures, ordered by how much growth they control for

| measure | construction | change, main window |
|---|---|---|
| ours | E/P − real yield; **no growth term** | **−48.6bp** |
| Damodaran, nominal | DDM with an **explicit** growth input | −40.0bp |
| Damodaran, real basis | same, restated | −29.3bp |
| **SPF survey** | **direct elicitation, no model** | **−19.1bp** |

**The ordering is monotonic in exactly the variable under test.** The more completely a measure accounts for
growth expectations, the less compression it reports. That is the signature of a residual partly made of
growth, and it is the first evidence for it that does not depend on trusting anyone's model.

**Survey compression is 39% of ours.** Read as a decomposition: roughly **two-fifths of the compression is
genuine risk-premium compression, three-fifths is growth expectations plus construction difference.** That
lands on P5(ii)'s independently derived bound — "growth-consistent share at least 40%" — by a completely
different route, which is the strongest thing about it.

## What it does NOT settle, stated plainly

- **The control window does not validate it, and the answer depends on an endpoint choice.** Q1-2015 →
  Q1-2019 gives −7.0bp against our −22.4bp, a ratio of 31% — close to the main window's 39% and encouraging.
  But Q1-2015 → Q1-2020 gives **+147.8bp, the wrong sign entirely.** The Q1-2020 survey was fielded in early
  February 2020 with the bond leg already collapsing (3.91% → 2.81%). **Picking 2019 because 2020 gives an
  inconvenient answer would be post-hoc, so both are reported.** The control is not clean either way.
- **The window does not match.** SPF is Q1-only, so this compares Feb-2024 to Feb-2026, missing both the
  front of our window and the H1-2026 reversal.
- **Survey expectations are sticky and extrapolative** — a well-documented property. A survey premium is not
  a market-implied premium, and the gap between them is itself contested in the literature.
- **The survey premium is nominal**; ours nets a real yield.

## Where this leaves the question

Three independent constructions now agree the gap compressed, and they disagree about *how much* in a way
that is systematic rather than random — ordered by growth treatment. **The best current estimate is that
roughly a third to two-fifths of the compression is risk and the rest is growth**, with the honest caveat
that no window validates this cleanly and n is small.

That is a real advance on P5(ii), which could not distinguish "mostly risk" from "entirely growth". It is
not a resolution.

## Also on disk, and worth knowing about

- **Richmond Fed / Duke CFO Survey**, quarterly 2001-2026, 98 observations of CFOs' expected S&P return —
  longer and higher-frequency on the equity leg, but with **no matched bond expectation from the same panel**,
  so it cannot be differenced into a premium without importing a yield from elsewhere and reintroducing the
  construction problem.
- **Yale/Shiller confidence indices** (443 monthly obs) and the **NY Fed Survey of Consumer Expectations**
  stock module (159 monthly obs): genuinely independent, but they report *shares of respondents* and
  *probabilities*, not return magnitudes. They can corroborate the direction of a change; they cannot stand
  in as a third level.
- Yale holds a quantitative expected-return cut that is **not on the free page** — obtainable by emailing the
  institute. Out of scope as briefed, but it is the one clearly-identified path to a monthly survey premium.
