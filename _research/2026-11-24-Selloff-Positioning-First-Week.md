# The November 2026 sell-off in the futures data: the first week (10 to 17 November)

24 November 2026, corrected 26 November after an audit (the Treasury paragraph was one-sided, and the S&P 500 change was
mostly new longs, not short-covering; the scores are unchanged). This scores the secondary-window lines of the
pre-registration ([version 2](2026-11-24-Selloff-Positioning-Preregistration.md), committed before the data was pulled).
Script: `bin/selloff_positioning.py`; outputs in `data/selloff_positioning/`. The supervisor re-read the S&P 500 and VIX
rows from the CFTC API, and they matched. The primary window (10 to 24 November) is scored on 30 November.

"Percentile" below is the rank of the week's change among all one-week changes since 2018 (462 weeks). The P4 line alone
is ranked against the 356 weeks with no VIX settlement, as registered.

## What the futures data shows for the first week

The first week covers the start of the fall, not its worst days (18 to 20 November).

| line | change, contracts | rank since 2018 | prediction | result |
|---|---|---|---|---|
| P1s Leveraged Funds, E-mini S&P 500 net | **+68,082** (net short from −303,060 to −234,978) | 91st percentile, High | sold (Low) | **wrong**: they bought |
| P3s Leveraged Funds, E-mini Nasdaq-100 net | **−24,895** | 1st percentile, Low | sold (Low) | **right** |
| P4 Leveraged Funds, VIX futures gross short | **+30,886** (96,310 to 127,196) | the largest one-week rise since 2018 among weeks with no VIX settlement | short cut (Low) | **wrong**: they added short volatility |

**Who sold, and who bought, in the first week:**
- **Nasdaq-100.** Leveraged Funds sold, mostly by adding shorts (gross short +19,568, 98th percentile; gross long −5,327).
  Asset Managers (+10,115, 93rd percentile), Non-Reportables (+5,878, 94th) and Dealers (+10,421, 81st) bought.
- **S&P 500.** The broad index went the other way. Leveraged Funds' net rose by 68,082, mostly through new longs (gross
  long +52,078, 96th percentile); they covered 16,004 of gross short. Dealers (−52,087, 11th percentile) and Asset Managers
  (−19,081, 29th) cut, neither unusually.
- **Pattern.** This class sold the technology index and bought the broad one. That is the shape of a trade against
  technology stocks relative to the market, not a general cut in equity risk. It is one class's futures book; it says
  nothing about cash shares, ETFs or options.
- **The VIX.** Leveraged Funds sold volatility while the VIX rose (close 19.46 on 10 November, 25.46 on 17 November; Cboe's
  daily file). Their net position went from −34,762 to −72,916 (0.2nd percentile). Dealers (+24,547, 99th percentile) and
  Asset Managers (+16,550, 93rd) took the other side.
  - That left a large short-volatility position in place before 20 November, when the VIX touched 40.03 during the day and
    closed at 35.89.
  - Whether it was then covered is not visible yet. The 24 November report will show the position, but it gives no P4
    verdict: the November VIX contract settled on 18 November, inside that window, and the pre-registration bars a
    verdict there.
  - Four VIX settlements since 2018 were moved to a Tuesday by a holiday. Scoring against the actual settlement dates gives
    the same result (largest of 356); that line is in `results.csv` as `secondary_no_vx_actual`.

**Treasuries (no verdict for this window).** Leveraged Funds moved their short along the curve. Whether the position grew
depends on the measure.

| contract | gross short, change in contracts | percentile |
|---|---|---|
| 2-year | −249,314 | 0.4th, Low |
| 5-year | −47,044 | 23rd |
| 10-year | +134,007 | 98th, High |
| Ultra 10-year | −9,809 | 27th |
| Bond | −21,823 | 11th |
| Ultra Bond | +54,928 | 99.6th, High |

- **In face value** the six-contract net short shrank, from $891.0bn to $864.3bn, a larger fall than in 90% of weeks.
- **In 10-year equivalents** (which weight long bonds more) the gross short rose from $811.0bn to $818.2bn, an ordinary
  week (74th percentile). The net short rose from $633.0bn to $650.2bn, a larger rise than in 92% of weeks.
- These three lines are in `results.csv` under `UST_ALL6`, window `secondary`.
- **Reading.** Shorts were cut at the 2-year and added at the 10-year and the ultra bond, in a week when yields rose
  (2-year 4.73% to 4.80%, 10-year 4.98% to 5.10%, Treasury's daily curve). The position became smaller in face value and
  larger in interest-rate risk: a shift toward long-dated shorts. This does not identify a basis trade; the class mixes
  trend followers and arbitrage books.

**Yen.** No sign of an unwind:
- Leveraged Funds' yen net: −6,935, 20th percentile. They added to gross yen shorts (+10,954, 92nd percentile), the
  opposite of covering.
- The H.10 yen rate: 158.76 per dollar on 10 November, 159.27 on 17 November, 158.76 again on 20 November. Through
  20 November the yen did not strengthen, which is what a yen-funded unwind would need. P5a is scored on the 24 November
  rate.
- The rate is read from the H.10 release's own historical table for the yen, in place of the DDP download the
  pre-registration names. The two were not compared date by date.

**Japan's weekly flows (Ministry of Finance, descriptive).** In the week of 8 to 14 November, Japanese residents:
- were small net buyers of foreign equity (¥363bn);
- were small net sellers of foreign long-term bonds (¥441bn).

This is no sign of repatriation. The week of 15 to 21 November was not yet in the file on 26 November.

## What this changes

- **The equity seller in futures is not the broad "leveraged amplifier" first proposed (P1s wrong).** In the first week,
  Leveraged Funds:
  - sold the Nasdaq-100;
  - bought the S&P 500;
  - sold volatility.

  In this class's futures book the first week looks like a bet against technology stocks, not a general de-risking.
- **The short-volatility build-up is the new finding.** It is a plausible amplifier of 19 to 20 November, if those shorts
  had to be bought back. It is untested. The 24 November report can describe the position, not test it, because the
  expiry falls inside the window.
- **Every line reads futures only, by trader class.** Positions in cash shares, ETFs and options are not seen.

## Next

On 30 November, after the CFTC release (3:30 p.m. ET) and the H.10 (4:15 p.m. ET): run `fetch`, then `build`, and score
P1, P2, P3, P5a, P5b, P6 and the seller rule. A primary-window miss on P1, P3, P5a, P5b or P6 is INCONCLUSIVE, as
pre-registered, and is not scored right or wrong.
