# A1 — did new bank money fund the equity buying? (14 September 2026)

**Status: RESULT, and it is mostly a negative.** Ranked item 3. Data `data/a1_analysis/`; script
`bin/a1_money_vs_equity.py`. Supervisor-verified 14 Sep — the scale figures and the Fed quarters reproduce
exactly on an independent recompute.

## The scale test is the finding, and it cuts against the story

Over **2024:Q1–2026:Q2** — the window our whole attribution covers:

| | $bn |
|---|---:|
| growth in commercial bank deposits | **+1,948.4** |
| household net purchases of corporate equity | **+3,069.4** |
| ratio | **0.63** |

**Household equity buying outran deposit growth by about 1.6 times.** Even under the most generous possible
assumption — that every single new dollar of deposits went straight into equities and nothing else —
**deposit creation could not have funded it.**

The comparison flatters the story more on longer windows and that is worth stating honestly: over the full
2015–2026 sample the ratio is 1.38 (deposits comfortably larger), and since 2020 it is 1.01 (almost exactly
matched, a coincidence of scale and nothing more). **But it gets worse, not better, as you narrow to the
period the goal is actually asking about.**

## [SYN1 AMENDMENT, 15 Sep] The scale test proves less than I claimed

Grok's attack is fair and I verified it. The test compared deposit GROWTH ($1,948.4bn) against household
equity buying ($3,069.4bn) and concluded deposits "could not have funded it." **That assumes only NEWLY
CREATED deposits can fund a purchase.** The deposit **stock** at 2026:Q2 was **$19,384.4bn — 6.3 times the
purchases.** Existing balances can fund $3.07trn with no money creation at all. Two further points, both
correct: H.8 deposits are all holders, not households; and ETF creation done in-kind requires no deposits.

**Correct position:** new bank deposits cannot be the *sole* source. "Too small to have funded it" does not
follow and is withdrawn. The weak positive association below stands.

## The association is real, positive, and small

Quarterly changes, 2015:Q2–2026:Q2, n=45:

| money variable | r | R² | slope, per $1 |
|---|---:|---:|---:|
| Deposits, all commercial banks | 0.263 | 6.9% | **16 cents** |
| Bank credit, all commercial banks | 0.239 | 5.7% | 28 cents |
| SOMA Treasuries | 0.188 | 3.5% | 14 cents |
| SOMA MBS | 0.198 | 3.9% | 34 cents |
| SOMA total | 0.198 | 3.9% | 11 cents |

**All five signs positive; all five weak.** None reaches conventional significance (deposits closest, p≈0.07
on a rough normal approximation — the machine has no scipy, so treat that as a gut-check not a test).
Roughly **10–30 cents of household equity buying per dollar of quarterly money growth.**

Under E-005 this is a result rather than a null: a consistently positive, small association is informative
about magnitude even where it is not distinguishable from noise.

## It is NOT a pandemic artefact — the opposite of what I expected

| sample | n | r (deposits) | slope |
|---|---:|---:|---:|
| pre-2020 | 19 | 0.186 | 39c |
| 2020 onward | 26 | 0.213 | 9c |
| **pandemic only, 2020–21** | 8 | **−0.264** | **−10c** |
| **excluding 2020–21** | 37 | **0.286** | 33c |

Isolated to the pandemic quarters the sign **flips negative**; drop 2020–21 entirely and the correlation is
slightly *stronger* than the full sample. So the relationship does not rest on the money-creation episode
everyone would reach for first. SOMA MBS is the one series with no stable sign at all (−0.06 / +0.13 / −0.16
across cuts) — no relationship there.

## The Fed has turned net Treasury buyer, confirmed

SOMA Treasury holdings fell every quarter from 2024:Q3 through 2025:Q3, then: **+$26.6bn (2025:Q4),
+$147.3bn (2026:Q1), +$113.0bn (2026:Q2)**. Verified by me against the H.4.1 data directly. The premise
holds; the link to equity buying does not follow from it.

## What this does not establish, stated plainly

A same-period correlation between two aggregates is consistent with at least four unlike stories: new
deposits flowing into equities; both rising because incomes rose; the Fed's asset purchases mechanically
creating deposits that coincide with unrelated buying; or **people selling equities into deposits**, which
produces the same sign with the causation running backwards. Nothing here distinguishes them. No multiplier
was computed and none should be (C-077, C-080).

## Where it leaves the channel

**Direct money creation is now tested and comes out weak.** There is a real but small positive association,
it is not concentrated in the obvious pandemic episode, and **on the recent window the channel is too small
to cover what it would need to explain.** That is a genuine narrowing: one of the goal's named channels can
be moved from "untested" to "tested, and probably not the answer on its own."

The residual remains unattributed. This rules out one candidate source for it rather than finding one.
