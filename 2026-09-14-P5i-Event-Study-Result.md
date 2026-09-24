# P5(i) — when did the 2024 expansion actually arrive? (14 Sep 2026)

**Status: RESULT, and the pre-registered "neither" outcome is the headline.** Run against
`_research/2026-09-14-P5i-EventStudy-Frame.md`. Data `data/p5i_event_study/`. Supervisor-verified 14 Sep.

## First: a flaw in my own specification

The spec's dependent variable — daily change in trailing P/E — carries a mechanical artefact at quarter
boundaries, where trailing earnings step to a new level. **Three steps in 2024 (E: 191.39 → 196.76 → 200.27
→ 210.17) produce dPE of −0.803, −0.413 and −1.611, summing to −2.83 points against a total measured change
of +3.20.** An accounting artefact 88% the size of the headline, pointing the wrong way. **Ex-artefact, the
price-driven move is +6.03 points.** Recomputed by me; the agent found it and disclosed it rather than
reporting the contaminated total. Recorded in the spec's Deviations block.

## The head-to-head: FOMC beats earnings, robustly

Denominator: 252 trading days in 2024; total measured ΔP/E +3.198 points.

| event set | window | days | share of days | share of ΔP/E |
|---|---|---|---|---|
| earnings (40 events) | [0] | 30 | 11.9% | **−54.6%** |
| FOMC (8 events) | [0] | 8 | 3.2% | −10.1% |
| earnings | **[−1,+1]** | 66 | 26.2% | **−34.7%** |
| FOMC | **[−1,+1]** | 24 | 9.5% | **+25.6%** |
| earnings | [−1,+5] | 114 | 45.2% | +42.4% |
| FOMC | [−1,+5] | 56 | 22.2% | +48.4% |

Three FOMC dates share an effective trading day with a megacap reaction. **Stripping shared days, the FOMC
effect survives and strengthens** — 5.95% of days carrying 40.1% of the change, a 6.7× ratio — while
earnings stay negative at the tight windows and merely proportional at [−1,+5].

**Read narrowly this is decision-rule row 2: FOMC disproportionate, earnings not → discount-rate repricing,
which supports the RISK reading over the growth reading.**

## But the larger fact is that neither channel explains it

At the primary window, **67.9% of trading days sit outside both event sets** and carry, gross, 94.6% of the
year's change. Net of the quarter-boundary artefact, **ordinary days alone carry +183% of the total move.**

That is the spec's flagged **"neither"** outcome, and the spec warned in advance that it is the result most
likely to be explained away in favour of the cleaner-sounding horse race. So it is the headline:
**most of 2024's multiple expansion happened on days carrying neither scheduled earnings news nor a Fed
decision.** It accrued as drift.

## What this does and does not license

**Drift is where a flow mechanism would live** — a continuous, price-insensitive bid does not wait for news.
But the spec is explicit and it holds: **this cannot measure flows** (no free daily flow series), so a
"neither" result is *consistent with* a flow story, not evidence of one. And on "neither" days a daily P/E
change is a price change whose risk-versus-growth composition is exactly the ambiguity under test.

## How it sits with this week's other results

- **P5(iv), the survey premium:** roughly two-fifths of the compression is risk, three-fifths growth.
- **This test:** of the part that arrived on *scheduled news*, the Fed channel dominates the earnings
  channel — which leans risk, consistent with the above.
- **Both:** the dominant share arrived on neither. **Three independent routes this week have now pointed at
  something continuous rather than news-driven, and all three stop at the same wall — we cannot observe
  flows at the frequency required to test the obvious next hypothesis.**

## Endpoint reconciliation, as required

The agent's monthly average of daily closes matches P2c's to ~3×10⁻⁷ percent at both endpoints — same
underlying series. The daily-close basis gives +3.198 points (24.787 → 27.985, +12.98%) against the frame's
monthly-average basis of +4.253 points (+17.46%); the gap is fully explained by Dec-2023's year-end rally
(+1.81% close over average) and Dec-2024's post-FOMC selloff (−2.15%). Not a wrong series.
