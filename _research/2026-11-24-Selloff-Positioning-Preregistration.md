# Who sold in the November 2026 tech sell-off, and was it a yen-funded unwind? Pre-registration

Written 24 November 2026, 13:10 UTC. It was committed before any futures positions for November 2026 in the contracts below,
and any November 2026 dollar-yen rate, had been pulled or read. The commit time is the evidence for that. Version 1.

## The episode

US stocks fell for seven sessions, from Thursday 12 November to Friday 20 November 2026. On the 20th the S&P 500 fell 3.7%
and the Nasdaq Composite 5.3%; the VIX closed at 35.89 (28.44 the day before; Cboe's daily file); Treasury yields fell
(10-year 5.04% to 4.92%, Treasury's daily curve). The selling started in Asian technology stocks before New York opened, on
the day Japanese inflation data lifted expectations of a December Bank of Japan rate rise (CNBC live blog, 20 November).
The question is the goal's own: for this flow, name the seller. Two candidate sellers are tested here, and one candidate
funding channel.

## What the supervisor already knew when writing this

- The index moves, the VIX and the Treasury yields above.
- CNBC's live blog: gold's fall that week was put down partly to "a stronger U.S. dollar"; a 72% probability of a December
  BoJ rate rise; SoftBank's worst day since August 2024.
- The Treasury-futures positions to 17 November (already in the repo): leveraged funds net short about $864bn of face
  across six contracts.
- Nothing about positions in equity-index, VIX or yen futures in 2026, and no 2026 dollar-yen rate.

The yen prediction below is written knowing that the dollar was described as stronger. That makes it a weaker test.

## Data

- **CFTC Traders in Financial Futures, futures only** (dataset gpe5-46if, free, no key). The contracts, by CFTC code:
  - S&P 500 consolidated 13874+
  - Nasdaq-100 consolidated 20974+
  - Russell 2000 E-mini 239742
  - VIX futures 1170E1
  - Japanese yen 097741
  - The six Treasury contracts already pulled by `bin/pull_cftc_tff.py`
- **Classes:** leveraged funds, asset managers and dealers. Net = long minus short, excluding spreads.
- **Dollar-yen:** the Federal Reserve's H.10 daily noon buying rate, yen per dollar (DDP series H10/H10/RXI_N.B.JA).
- **Release date:** positions at Tuesday 24 November are due on Friday 27 November. Thanksgiving falls on the 26th, so
  the CFTC may publish on Monday 30 November instead; the release schedule decides.

## Windows and the yardstick

- **The window:** the report of Tuesday 10 November to the report of Tuesday 24 November, two report weeks. It spans the
  whole seven-day fall, which began on the 12th.
- **Sub-windows:** 10 to 17 November and 17 to 24 November are reported, but carry no verdict.
- **The yardstick:** each series' change over the window is set against the same series' two-week changes from the first
  report of 2018 to 10 November 2026. Overlapping two-week changes are used, every report week.
- **z** = the window's change divided by the standard deviation of those two-week changes. No mean is subtracted.
- Its percentile among those changes is also reported.
- **Units:**
  - Futures are in contracts.
  - Dollar-yen is the log change between the H.10 rate on 10 November and on 24 November, or the last date published by
    the time the build runs, which must be stated.
  - If either date has no H.10 rate, the nearest earlier business day is used and named.

## Hypotheses, predictions and the rule that scores each

Each prediction carries the supervisor's credence that it comes true.

| id | hypothesis | the test | prediction | credence |
|---|---|---|---|---|
| P1 | Leveraged funds (hedge funds, trend followers) sold S&P 500 futures | leveraged funds' S&P 500 net, z ≤ −1.0 | **fires** | 60% |
| P2 | Asset managers (pensions, insurers, mutual funds) did not sell S&P 500 futures on the same scale | asset managers' S&P 500 net, z > −1.0 | **holds** (no large sale) | 55% |
| P3 | The same in the Nasdaq-100, where the AI stocks weigh most | leveraged funds' Nasdaq-100 net, z ≤ −1.0 | **fires** | 55% |
| P4 | Short-volatility positions were covered | leveraged funds' VIX net, z ≥ +1.0 (less short, or more long) | **fires** | 55% |
| P5 | A yen-funded unwind: the yen rose and the short-yen position was covered | both legs: dollar-yen log change z ≤ −1.0 (yen stronger) **and** leveraged funds' yen net z ≥ +1.0 | **does not fire** | 60% |
| P6 | The Treasury-futures short behind the basis trade was not unwound | leveraged funds' six-contract Treasury net, in 10-year equivalents, z < +1.0 | **holds** | 70% |

**Scoring:** each line is scored on its own rule, as fired or not fired, and the prediction is right or wrong on that.

**Russell 2000:** reported for every class, with no verdict.

**P5's split verdicts:** if only one leg fires, P5 has not fired, and the note says which leg fired. A yen that weakened (z ≥ 0)
rejects the unwind story for this episode, whatever the positions show.

**Weekly positions from Japan's Ministry of Finance** (the weekly international securities transactions report, Japanese
residents' net purchases of foreign securities, weeks to 14 and 21 November): reported descriptively if a free file is found.
They carry no verdict, because the file has not been checked yet.

## What each outcome would mean for the page

- **P1 or P3 fires, and P2 holds:** the futures data names leveraged funds as the futures seller in this episode. This would
  be the first measured seller on the equity side. It says nothing about who sold shares in the cash market.
- **P2 fails (asset managers sold too):** real money sold in futures as well. The "leveraged amplifier" reading weakens.
- **None of P1, P3 or P4 fires:** futures show no unusual de-risking. Friday's mechanical-selling story then rests only on
  price behaviour (gold, bitcoin and equities falling together, Treasuries rising) and stays a hypothesis.
- **P5 fires:** the Japan link becomes a measured candidate; it is not shown to be the cause.
- **P6 fails:** a Treasury-basis unwind happened alongside the equity sale. That would contradict the calm-credit reading of
  20 November.

## Known weaknesses, stated before the data

- **Futures only.** Shares, ETFs and options are not covered. A fund can sell stock and leave its futures alone.
- **Tuesday snapshots.** The 24 November report comes after the low of the 20th; the VIX fell back to 26.62 on the 23rd.
  Positions may have been rebuilt by the Tuesday, which would bias every line towards not firing. The sub-windows are
  reported to show this.
- **Contracts, not dollars.** Contract counts ignore the price change, and a fall in the index shrinks the dollar value of an
  unchanged position. A dollar version (contracts × multiplier × index level) is reported beside each line but carries no
  verdict.
- **Leveraged funds are a mixed class.** It holds basis traders, macro funds and trend followers, and their trades can cancel
  out. A net figure can hide large gross moves, so gross long and short are reported too.
- **Roll weeks.** December equity-index futures roll in the second week of December, so the window does not touch the
  roll. The September roll falls in the yardstick sample, which widens the standard deviation and makes firing harder.
- **The yen prediction was written knowing the dollar had been reported as stronger** (see above).

## Not to be changed after the data

The thresholds, the window, the yardstick and the predictions are fixed. A version 2 is allowed only before any November 2026
data in these series has been pulled or read. Any later change is a new test, under a new name, reported beside this one.
