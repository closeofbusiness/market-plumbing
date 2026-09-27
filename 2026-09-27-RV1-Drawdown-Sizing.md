# RV1 sizing — what a 2020-type drawdown would take from today's undrawn bank lines (27 Sep 2026)

**Status: FINDING. Supervisor, 27 Sep. Grade: HYPOTHESIS**, because it applies a 2020 precedent to populations from 2025–26.
This note owns the sizing figures. The precedent figures come from Grok's RV1 return
(`_research/2026-10-01-RV1-Revolver-Drawdown-Return.md`, written 27 Sep despite the date in its name). The supervisor re-read at
source the four sources that carry the result; they are marked in the table below. The note serves the mission's "where the money is
coming from" at its fastest edge: undrawn committed lines are where bank money can be created within days.

## The answer

In a shock like March 2020, draws on today's undrawn lines would probably come to:
- **roughly $100–270bn** of the **$987bn** undrawn at nonbank financial institutions (NDFIs);
- **roughly $30–80bn** of the **~$300bn** undrawn at AI-adjacent industries, with outer bounds of $26bn and $117bn.

In 2020, most of the draws came within a month. Both totals are well below the ~$480bn rise in bank C&I loans over three weeks of
March 2020, which the banking system met.

The money a drawdown creates arrives during stress and is mostly held as cash: in 2020, deposits rose about $1trn, twice the new
lending. **So this channel bears on fragility and timing, not on what funded the 2024–26 run-up.** All of it is conditional on a
backstop like the Fed's of 23 March 2020, after which investment-grade firms stopped drawing.

## The precedent figures

| figure | value | population and denominator | source | supervisor re-read, 27 Sep |
|---|---|---|---|---|
| Draws on committed lines, March and April 2020 | $336.6bn of $1,243.9bn undrawn at end-2019 (27.1%); March alone $297.9bn (24.0%) | US nonfinancial SEC filers, S&P LCD matched to Capital IQ | Acharya and Steffen, NBER w27601, Table 4 (printed p. 46) | **yes.** The caption says billions, but the values are in millions |
| The same, by rating (March and April) | AAA-A 8.71%; BBB 33.00%; non-IG 39.14%; unrated 24.00% of undrawn | same | same | **yes** |
| Line utilization, 2020Q1 against normal quarters | REITs 28.36% → 47.91%; other NBFIs 34.76% → 41.18%; nonfinancials 21.66% → 32.90% | public firms (Capital IQ); firm averages; "normal" means the 2005–23 average | Acharya, Gopal, Jager and Steffen, NBER w33590, Table 1 Panel B (printed p. 45) | **yes** |
| Unfunded NDFI commitments, 3Q 2025 | $987bn, 42.9% of NDFI commitments (for all loans, 44.1% is unfunded) | all banks, Call Reports | FDIC, *Banking Issues in Focus*, February 2026, p. 5 | **yes** |
| Composition of funded NDFI loans, 3Q 2025 | $1.29trn at banks over $10bn: mortgage credit intermediaries 24.5%, business credit 24.6%, consumer credit 8.1%, private-equity funds 24.0% (mostly capital-call lines), other 18.7% | funded loans only | same, p. 4 | **yes** |
| Revolving utilization at large banks, 2020Q1 | +$224.0bn; end-2019 revolving commitments $3,554bn, 35% utilized | FR Y-14Q, large banks | Chodorow-Reich, Darmouni, Luck and Plosser, NBER w27945, Table 10; Fed FSR May 2020, Table A | no; taken from RV1 |
| H.8 and deposits, March 2020 | C&I loans +$470–483bn (11 Mar–1 Apr); NDFI loans +$82–92bn (4 Mar–1 Apr); deposits about +$1trn | all commercial banks | FRED and ALFRED; Li, Strahan and Zhang, NBER w27256 | no; taken from RV1 |

## How the ranges are built

**Share of the undrawn stock that was drawn.** A change in utilization converts to a share of the undrawn stock as
Δpp / (100 − baseline):
- REITs: 19.55 / 71.64 = 27.3%.
- Other NBFIs: 6.42 / 65.24 = 9.8%.
- Nonfinancials: 11.24 / 78.34 = 14.3%.

These rates carry two caveats: the baseline is the 2005–23 average rather than 2019Q4, and they are firm averages, not
dollar-weighted.

**Nonbanks, $987bn undrawn.**
- The low end is the other-NBFI rate, 9.8%, giving about $97bn. The high end is the REIT rate, 27.3%, giving about $269bn. REITs
  were the heaviest NBFI drawers in 2020.
- The mix points to the lower half. About half of the funded lending to these institutions is mortgage warehouse lines and
  capital-call lines to private funds. In 2020, warehouse-line usage stayed stable (Richmond Fed Economic Brief 25-33), and funds paid capital-call lines down
  (a vendor note only).
- The FDIC article does not break the **undrawn** $987bn down by type. Call Report schedule RC-L, item 1.e.(3), has reported it by
  subtype since December 2024, and would settle the weighting.
- Cross-check: H.8 loans to NDFIs rose by $82–92bn (+15%) in four weeks of March 2020, on a base of about $600bn.

**AI-adjacent industries, ~$300bn undrawn.** This is industry exposure, not lending to the build-out (C-115).
- The central range runs from 9.7% to 27.1%. The low end is the Y-14 aggregate: +$224bn on about $2,310bn undrawn at end-2019, a
  quarter-end snapshot (derived). The high end is the Acharya–Steffen public-firm rate. Together they give about $29bn to $81bn.
- The outer bounds come from the rating classes. If every borrower drew like an AAA-A firm (8.7%), the draw would be about $26bn;
  if every borrower drew like a non-investment-grade firm (39.1%), about $117bn.
- The industry spans AA-rated hyperscalers, which drew little in 2020-type episodes, and lower-rated or unrated data-centre
  developers. Its rating mix is not measured here.

## What would change it

- **No backstop.** The 2020 rates build in the Fed's 23 March facilities. Without them, investment-grade firms would have kept
  drawing. So these ranges are not ceilings for a worse shock: the outer bounds are BOUNDED only on the assumption of 2020-type
  behaviour.
- **Capital-call lines under investor stress.** They are about a quarter of funded NDFI lending. Their stress case, investors
  failing to fund capital calls, has no precedent in any official or academic source that RV1 found. RC-L item 1.e.(3)(c) would
  show it if it happened.
- **Covenants.** Roughly a third of unused capacity cannot be drawn under typical covenants. That estimate is model-based
  (Greenwald, Krainer and Paul), and the 2020 rates already include the effect.
- **Bank capacity.** Capital did not bind in 2020. The liquidity coverage ratio (LCR) already assumes a 40% outflow on unused NBFI
  lines and 10% on nonfinancial lines (Fed FSR May 2020).

## Monitor

A drawdown would show first in the H.8's weekly lines for C&I loans and loans to nondepository financial institutions (Federal
Reserve Board, about nine days' lag). After that it would show in the quarterly Call Report RC-L unused commitments, and in
senior loan officer survey (SLOOS) mentions of precautionary demand. Proposed monitor additions: the two weekly H.8 lines, taken
from the Fed's Data Download Program because FRED refuses scripts here (calendar, 9 Oct).

## Observed vs inferred

**Observed:** the figures in the precedent table. **Inferred by the supervisor:**
- the conversions to a share of the undrawn stock;
- applying 2020 rates to populations from 2025–26;
- the judgment that the nonbank draw falls in the lower half of its range;
- that drawn money would be held as cash, which is how firms behaved in 2020, not a law.
