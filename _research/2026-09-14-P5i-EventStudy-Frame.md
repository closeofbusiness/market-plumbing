# P5(i) — the 2024 event study: the frame, decided before anyone measures (14 Sep 2026)

**SUPERVISOR work, not delegated.** Pre-registered like the B5 first stage, for the same reason: with a free
hand after seeing results I would try event windows until one produced a clean answer.

## What has to be explained

The multiple rose **17.5% during 2024** (trailing P/E 24.3468 at Dec-2023 → 28.6002 at Dec-2024), then gave
it back by Jun-2026 (25.2212) as earnings caught up. Virtually all the net compression in our window sits in
that single year. **Why 2024?**

## The frame decision, and it is the whole contribution here

The ranked item listed five candidates: the rate path, AI earnings revisions, foreign buying, retail and
options, and the buyback-to-issuance turn. **Most of those are not events.** They are continuous processes,
and an event study cannot see them. Forcing all five into one method would produce a confident answer to a
question the method cannot address.

So the work splits by the shape of the candidate, not by the candidate:

| candidate | dateable? | method |
|---|---|---|
| AI earnings revisions | **YES** — scheduled megacap earnings dates | event study, daily |
| Monetary policy | **YES** — FOMC announcement dates | event study, daily |
| Foreign buying | no, continuous monthly | time-series, not event study |
| Retail / options | no, continuous | out of scope: no free daily series |
| Buyback-to-issuance turn | no, quarterly | already measured in S1; not an event |

**Only the first two are event studies. Say so rather than pretending otherwise.**

## The discriminating test — why this is worth running at all

P5(ii) could not separate whether the compressed residual is **cheaper risk** or **higher expected growth**.
Two measures cannot identify three components. But the *timing* of the 2024 expansion can discriminate where
the levels cannot:

- **If the expansion clusters on megacap earnings and guidance dates** → the market was repricing expected
  GROWTH. That is the growth reading of the residual.
- **If it clusters on FOMC dates and rate moves** → the market was repricing the DISCOUNT RATE. That is the
  risk/discount reading.
- **If it clusters on neither** → it accrued on ordinary days, which is itself the most interesting outcome,
  because a drift with no news attached is where a flow story would live.

**This is the only route we have left to the risk-versus-growth question**, since the direct level comparison
failed and the flow-attribution designs died on data frequency. That is why it ranks.

## Pre-registered specification

- **Dependent variable:** daily change in the S&P 500's trailing P/E. Prices daily; trailing earnings move
  only at quarter boundaries, so within a quarter this is a price change — **state that, do not disguise it**.
- **Event set A:** quarterly earnings release dates for the 2024 top-10 constituents, taken from the named
  list already vetted in `2026-09-13-P5iii-Concentration-And-JVZ.md`. Announcement date, not period end.
- **Event set B:** the eight scheduled FOMC announcement dates in 2024.
- **Windows:** [-1, +1] trading days primary; [0] and [-1, +5] as robustness. Fix these now.
- **The statistic:** share of 2024's total P/E change that accrues inside event windows, against the share of
  trading days those windows represent. A window covering 12% of days that carries 40% of the move is a
  result; one carrying 13% is not.
- **Both event sets get the same treatment**, and the comparison between them is the finding.

## Decision rule, fixed in advance

| outcome | reading |
|---|---|
| earnings windows carry a disproportionate share, FOMC windows do not | growth repricing — supports the growth reading of the residual |
| FOMC windows disproportionate, earnings not | discount-rate repricing — supports the risk reading |
| both disproportionate | both channels; report the split, claim neither as dominant |
| **neither disproportionate** | the move accrued on ordinary days. **Report that plainly** — it is evidence for a drift mechanism (flows) and against a news mechanism, and it is the outcome most likely to be explained away if not fixed in advance |

## What this cannot do, stated now

It cannot measure flows — we have no free daily flow series, which is the constraint that killed two designs
already. A "neither" result is *consistent with* a flow story, not evidence of one. And a daily P/E change is
a price change; attributing it to a premium rather than to earnings expectations is exactly the ambiguity
under test, so the write-up must not quietly assume its own conclusion.

## Deviations

**14 Sep — A FLAW IN THIS SPEC, found by the executing agent and confirmed by me.** The spec named the
dependent variable as "daily change in the trailing P/E" and noted that within a quarter this is a price
change. **What it failed to anticipate is the quarter BOUNDARIES.** Holding trailing earnings constant
within a quarter forces a discrete, mechanical jump in P/E on the first trading day of each quarter when E
steps to its next level. Recomputed by me from the daily series: E stepped 191.39 -> 196.76 -> 200.27 ->
210.17, producing dPE of -0.8030, -0.4134 and -1.6110, **summing to -2.83 points against a total measured
2024 change of +3.20** — an accounting artefact 88% the size of the headline, pointing the wrong way.
**Ex-artefact the price-driven move is +6.03 points.** The agent disclosed this rather than reporting the
contaminated total, which is the behaviour the pre-registration was for. Anyone rebuilding this should use
daily log PRICE changes and handle the earnings level separately.

**14 Sep — execution choices logged by the agent, all reasonable:** the `top10_2023` snapshot used as the
2024 constituent proxy (the spec did not pin which of three dated snapshots); two SEC dates excluded after
reading the 8-K text rather than trusting item codes — Tesla's production-and-deliveries release (no income
statement) and a J&J filing that restated Q1 EPS for a litigation reserve rather than announcing results.

- **2026-09-14, execution notes (not deviations from window/statistic/event-set, but judgment calls the spec
  left open, recorded per the instruction not to silently substitute):**
  1. **Top-10 snapshot used for "2024 top-10":** the P5iii named list has three dated snapshots
     (2015/2023/2025). Used `top10_2023` (2023-06-30) -- this is the one P5iii itself already labelled the
     start-of-window-2 (2024) proxy, so it is the natural, non-cherry-picked reading of "2024 top-10", chosen
     before any event-study result was seen.
  2. **Earnings-step (E) convention:** "trailing earnings constant within a quarter" admits two step
     conventions (each quarter uses its own end-of-quarter E, vs. carries the prior quarter's E). Used the
     former (own-quarter E) because it is the only one that reconciles to this file's stated Dec-2024 endpoint
     (28.6002); the latter would leave Q4 2024 priced off Q3's earnings level and miss the endpoint by
     construction.
  3. **Day-0 for after-hours announcements:** AAPL/MSFT/GOOGL/AMZN/META/NVDA/TSLA report after market close,
     so day 0 = next trading day (first session that can react). UNH/JNJ report before the open, so day 0 =
     report date. BRK.B releases by Saturday press release, so day 0 = the following Monday. Weekends/holidays
     generally roll forward to the next trading day.
  4. **Two earnings-date exclusions**, both verified by reading the primary 8-K text, not assumed from item
     codes: TSLA's early-month "production & deliveries" 8-K (no income statement; the later "Quarterly
     Update" release is the actual earnings announcement) and JNJ's 2024-05-01 8-K (a restatement of Q1 EPS
     for a litigation reserve, not a new quarterly announcement).
  5. **Found, not assumed -- a large modeling artifact:** the own-quarter-E step convention (#2) creates a
     mechanical, non-price jump in daily P/E on the first trading day of each 2024 quarter (Jan 2, Apr 1, Jul
     1, Oct 1). None of these 4 days falls inside any Event-Set-A or Event-Set-B window at any window size
     (checked for all 6 set x window combinations), so they land entirely in "neither" -- and they sum to
     -2.834 P/E points, i.e. -88.6% of the whole year's +3.198-point change, in the opposite direction of the
     year's net rise. Reported as a separate, explicit line rather than left to inflate "neither" silently
     (data/p5i_event_study/09_neither_bucket_decomposition.csv).
  6. **Found, not engineered -- event-set overlap:** 3 of the 8 FOMC dates (Jan 31, May 1, Jul 31) land on the
     exact same effective trading day as a megacap earnings reaction (GOOGL, AMZN, MSFT respectively), growing
     to 25 of 56 FOMC [-1,+5] window-days at the widest window. Both the full (non-exclusive) shares and an
     overlap-excluded ("exclusive") version of each set's share are reported so this confound is visible
     rather than hidden (data/p5i_event_study/07_overlap_between_event_sets.csv,
     data/p5i_event_study/08_exclusive_shares.csv).
