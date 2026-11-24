# Who sold in the November 2026 tech sell-off, and was it a yen-funded unwind? Pre-registration

Version 2, written 24 November 2026, before any futures positions for November 2026 in the contracts below, and any
November 2026 dollar-yen rate, had been pulled or read. Version 1 was committed at 13:10 UTC (97c6402). Grok reviewed it under
a blind rule and found ten faults, the first checked by the supervisor (below). Version 2 replaces version 1. The commit times
are the evidence that both came before the data.

## The episode

US stocks fell for seven sessions, from Thursday 12 November to Friday 20 November 2026. On the 20th the S&P 500 fell 3.7% and
the Nasdaq Composite 5.3%; the VIX closed at 35.89 (28.44 the day before; Cboe's daily file); Treasury yields fell (10-year
5.04% to 4.92%, Treasury's daily curve). The selling started in Asian technology stocks before New York opened, on the day
Japanese inflation data lifted expectations of a December Bank of Japan rate rise (CNBC live blog, 20 November). By Monday
the 23rd the VIX was back to 26.62.

The question is the goal's own: for this flow, name the seller. Futures can name a seller only among futures traders, and
only by CFTC class.

## What the supervisor already knew when writing this

- The index moves, the VIX and the Treasury yields above.
- CNBC's live blog: gold's fall that week was put down partly to "a stronger U.S. dollar"; a 72% probability of a December
  BoJ rate rise; SoftBank's worst day since August 2024.
- The Treasury-futures positions to 17 November (already in the repo): leveraged funds net short about $864bn of face across
  six contracts.
- Nothing about positions in equity-index, VIX or yen futures in 2026, and no 2026 dollar-yen rate.

## Data

- **CFTC Traders in Financial Futures, futures only** (dataset gpe5-46if, free, no key).
- **Classes**, by the CFTC's names, all five reported:
  - Dealer/Intermediary
  - Asset Manager/Institutional
  - Leveraged Funds
  - Other Reportables
  - Non-Reportables
- **The CFTC classifies traders, not trades**, by each trader's predominant activity. "Leveraged Funds" mixes hedge funds,
  CTAs and arbitrage books.

| contract | CFTC code | used for |
|---|---|---|
| E-mini S&P 500 | 13874A | P1, P2, seller rule |
| E-mini Nasdaq-100 | 209742 | P3 |
| E-mini Russell 2000 | 239742 | reported, no verdict |
| VIX futures (Cboe) | 1170E1 | P4 |
| Japanese yen (CME) | 097741 | P5b |
| UST 2Y | 042601 | P6 |
| UST 5Y | 044601 | P6 |
| UST 10Y | 043602 | P6 |
| Ultra 10Y | 043607 | P6 |
| UST Bond | 020601 | P6 |
| Ultra Bond | 020604 | P6 |

- **The consolidated codes 13874+ and 20974+ are not used.** From the 2 May 2023 report they changed unit. Open interest in
  13874+ was 453,159 on 25 April 2023 and 2,304,633 on 2 May 2023, while the E-mini code 13874A barely moved (2,265,794 to
  2,276,183). The supervisor re-read both rows from the CFTC API.
- **P6 weights** are the primary DV01 set in `bin/pull_cftc_tff.py`, held constant: $34, $42, $63, $91, $137 and $215 per
  basis point per contract. They convert to 10-year equivalents at a fixed modified duration of 8.176, as that script does.
- **Dollar-yen:** the Federal Reserve's H.10 daily noon buying rate, yen per dollar (DDP series H10/H10/RXI_N.B.JA).
- **Release dates:**
  - CFTC: positions at Tuesday 24 November are due on **Monday 30 November** (the CFTC schedule marks it delayed for the
    holiday).
  - H.10: the 24 November rate is due Monday 30 November at 4:15 p.m. ET.

## The yardstick

- **Changes** are taken between report dates, in contracts. Dollar-yen is a log change between H.10 rates on report Tuesdays.
- **Two-week windows** are kept in the yardstick only when the two as-of dates are 13 to 15 days apart.
- **One-week windows** are kept only when the two as-of dates are 6 to 8 days apart.
  - That keeps the CFTC's Monday-dated holiday reports, and drops gaps such as the late-2018 lapse and the early-2023 delays.
- **Sample:** every qualifying window from the first report of 2018 to the window ending 10 November 2026. Windows overlap.
- **The score** is the percentile of the observed change among the yardstick changes: the share of yardstick changes less than
  or equal to it.
  - **"Low"** means at or below the 10th percentile.
  - **"High"** means at or above the 90th.
  - This is a description of rank, not a p-value; overlapping windows are not independent.
- **No standard deviation is used to score.** It is still reported.

## Windows

- **Primary:** the report of Tuesday 10 November to the report of Tuesday 24 November. The yardstick is two-week windows.
- **Secondary:** 10 to 17 November. The yardstick is one-week windows.
  - This window ends before the worst days (18 to 20 November). It is scored separately and never combined with the primary.
- **Why a miss on the primary is not evidence of no selling:** positions sold in the fall and rebuilt by Tuesday the 24th
  cancel out. A miss on the primary is recorded as **INCONCLUSIVE**, not as "no unusual de-risking".
- **Scoring needs the rows.** Nothing on the primary window is scored until the 24 November report is in the file. A run
  before then records PENDING.

## Hypotheses, predictions and scoring rules

Credence is the supervisor's, written before the data.

| id | test (window) | rule | prediction | credence |
|---|---|---|---|---|
| P1 | Leveraged Funds, E-mini S&P 500 net (primary) | change is Low | fires | 50% |
| P1s | the same (secondary) | change is Low | fires | 55% |
| P2 | Asset Managers against Leveraged Funds, E-mini S&P 500 net (primary) | the Asset Manager change is greater than the Leveraged Funds change (it fell less, or rose) | holds | 55% |
| P3 | Leveraged Funds, E-mini Nasdaq-100 net (primary) | change is Low | fires | 45% |
| P3s | the same (secondary) | change is Low | fires | 50% |
| P4 | Leveraged Funds, VIX futures **gross short** (secondary only) | change is Low (short reduced) against one-week windows that contain no VIX settlement Wednesday | fires | 45% |
| P5a | dollar-yen, H.10 (primary) | log change is Low (yen stronger) | does not fire | 60% |
| P5b | Leveraged Funds, yen net (primary) | change is High (short yen covered, or long yen added) | does not fire | 55% |
| P6 | Leveraged Funds, six-contract Treasury **gross short** in 10-year equivalents (primary) | change is Low (short reduced) | does not fire | 70% |

**The seller rule** (stated, not a prediction): the futures data names Leveraged Funds as **the** E-mini S&P 500 seller in the
primary window only if the Leveraged Funds net change is the largest decline in contracts among all five classes.

**P4** is not scored on any window containing Wednesday 18 November 2026, the November VX settlement, because an expiring
short leaves the aggregate without being bought back.

**P5a and P5b** are scored separately. "Consistent with a yen-funded unwind" needs both to fire; if only one fires, the note
says which. Other Reportables' yen net (where central banks and corporate treasuries sit) is reported on the same percentile,
with no verdict.

**A P6 fire** means this mixed class reduced its Treasury short. It does not by itself show a basis-trade unwind. Falling
yields would also lead trend followers to cover shorts.

**Gross long and gross short** for every class and contract are reported beside the nets, with percentiles and no verdict.

**Reported descriptively, no verdict:**
- the Russell 2000 E-mini lines;
- the Ministry of Finance's weekly figures (`week.csv`, Japanese residents' net purchases of foreign securities, weeks to 14
  and 21 November).

## What each outcome would mean for the page

- **P1 or P1s fires, P2 holds and the seller rule is met:** Leveraged Funds are the measured futures seller in this episode.
  This is the first named seller on the equity side. It says nothing about the cash market.
- **P2 fails:** Asset Managers cut more than Leveraged Funds in contracts. The "leveraged amplifier" reading weakens.
- **Every equity line misses:** a primary miss is INCONCLUSIVE (the rebuild problem). A secondary miss says that in the first
  week (10 to 17 November) futures show no unusual selling by this class.
- **P5a and P5b both fire:** the yen link becomes a measured candidate, not a cause.
- **P6 fires:** Leveraged Funds cut their Treasury short in the sell-off. The note must then weigh trend-following against a
  basis unwind; neither is shown by this test.

## Known weaknesses, stated before the data

- **Futures only.** Shares, ETFs and options are not covered. A fund can sell stock and leave its futures alone.
- **Classes are by trader, not by trade.** A reclassification moves a whole book in one week. The CFTC's announcement page is
  checked for one in November 2026 before scoring.
- **Contracts, not dollars.** E-mini S&P 500 and E-mini Nasdaq-100 contracts differ in dollar size, so P1 and P3 are not
  compared with each other.
- **The yardstick holds the 2018, 2020 and 2022 stresses.** That is wanted: the question is whether November 2026 ranks with
  them.
- **The prediction for P5a was written knowing the dollar had been described as stronger.**
- **Grok's search results showed November 2026 figures in snippets.** Grok did not use them, and they never reached the
  supervisor.

## Not to be changed after the data

The thresholds, the windows, the yardstick, the rules and the predictions are fixed from this version. Any later change is a
new test, under a new name, reported beside this one.

## Changes from version 1

- Consolidated codes replaced by E-mini codes (the 2023 unit change).
- The score is a percentile rank, not a standard-deviation ratio.
- P2 is a cross-class comparison, and a seller rule is added.
- A primary miss is INCONCLUSIVE.
- P4 moves to gross short on the secondary window, away from the VIX expiry.
- P5 is split into two legs, and the rule that a weaker yen rejects the story is deleted.
- P6 names its contracts and weights and moves to gross short.
- The CFTC's class names are used.
- The dollar-value column is dropped.
- Windows are kept only when the as-of dates are the right distance apart.
- The release date is corrected to 30 November.
