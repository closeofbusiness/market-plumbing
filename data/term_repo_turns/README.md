# Term repo at the month-end turn

Written by `python3 bin/term_repo_turns.py build --stage describe` from the data vintage 20261103. Do not edit by hand.

## What the numbers show

Take the last business day before a month-end. A tri-party repo loan (a loan against securities, with a clearing bank between lender and borrower) that starts that day in the 2-7 day bucket lasts more than one business day, so every such loan is still open on the month-end. An overnight loan that starts the same day is not. That is the one start date on which the two buckets differ in exactly that respect.

The gap S is the 2-7 day rate minus the overnight/open rate, in basis points (one basis point is one hundredth of a percentage point). The difference E is the gap on that day minus the median gap on ordinary days of the same month, the control days. The median is the middle value, or the mean of the middle two. The columns dB and dO are the 2-7 day rate and the overnight rate on the day, each minus its own median over the control days. A median of differences is not a difference of medians, so dB minus dO need not equal E.

At the 8 of eight ordinary month-ends that could be assessed, E ran from -5.00 to +8.00 basis points.

The eight ordinary month-ends, in basis points:

| month-end | gap S on the day before | median gap on control days | E | dB | dO |
|---|---|---|---|---|---|
| 2025-10-31 | +13.00 | +5.00 | +8.00 | -8.00 | -16.00 |
| 2025-11-28 | +1.00 | +6.00 | -5.00 | +5.00 | +11.00 |
| 2026-01-30 | +3.00 | +5.50 | -2.50 | -1.00 | +1.00 |
| 2026-02-27 | +4.00 | +4.00 | 0.00 | +1.00 | +2.00 |
| 2026-05-29 | +6.00 | +5.00 | +1.00 | +3.00 | +2.00 |
| 2026-07-31 | +5.00 | +5.00 | 0.00 | +4.00 | +4.00 |
| 2026-08-31 | +4.00 | +4.00 | 0.00 | +1.00 | 0.00 |
| 2026-10-30 | +3.00 | +5.00 | -2.00 | +4.00 | +6.00 |

dB and dO are measured against control days that can lie on the other side of a Fed rate move, so in such a month they mostly show the move (September 2025 and September 2026 among the quarter-ends below, October 2025 here, where the step falls on the day itself). Read them with the Fed dates beside them. E is much less exposed, as the move is in both rates.
The top of the range is set by 2025-10-31 alone (+8.00; the next highest is +1.00). Only the top decides ABOVE, so one month sets that bar.

The five quarter-ends that have passed (September 2025 to September 2026): 0 of the 5 assessed have an E above the largest of the eight. This is a count and not a test.

| month-end | gap S on the day before | median gap on control days | E | dB | dO | E above the largest of the eight |
|---|---|---|---|---|---|---|
| 2025-09-30 | +6.00 | +4.00 | +2.00 | -21.00 | -24.00 | no |
| 2025-12-31 | +8.00 | +6.00 | +2.00 | +6.00 | +4.00 | no |
| 2026-03-31 | +4.00 | +5.00 | -1.00 | -1.00 | 0.00 | no |
| 2026-06-30 | +5.00 | +5.00 | 0.00 | 0.00 | 0.00 | no |
| 2026-09-30 | +5.00 | +4.00 | +1.00 | +23.00 | +23.00 | no |

The three months left out of the comparison, described only (August 2025 was the first month of the bucket; at the end of April 2026 the Fed decision took effect inside the loan; 27 November 2026 is a recommended early close): 2025-08-29 E 0.00, 2026-04-30 E -0.50, 2026-11-30 PENDING.

The queued December statement (T-1 = 30 December 2026) is PENDING. It is filled in by the first fetch on or after 2027-01-05T20:00Z and written once to registered.csv.

The checks file has 11 PASS, 0 WARN, 0 FAIL, 2 INFO.
The revisions file lines up 33 values from two vintages or from the final and preliminary series.

## What this cannot say

- It does not say why the gap on the day was wider or narrower than usual. A wider gap can come from the overnight rate falling as well as from the 2-7 day rate rising (both legs are always shown), from a shift in the kinds of collateral (both series pool every class), or from which dealers borrowed; the series has no counterparty detail.
- It does not say whether lenders asked for more to lend across the date, and no number here is described that way.
- It makes no comparison with SOFR or the other reference rates: the OFR says these averages do not allow direct comparison with those rates.
- The overnight figure is not a pure overnight rate. It includes open repo, which can be closed before the date.
- It does not describe the turn on the last day itself as a 2-7 day spread. The loan that spans this year-end most directly, from Thursday 31 December to Monday 4 January, is one business day long and sits in the overnight bucket. That is why the overnight rate on the day itself is shown on its own, in the column ot.
- It says nothing about dates before 13 August 2025, nothing about other repo (cleared or bilateral), and nothing about year-ends in general: there is one December and none of the eight comparison months is a year-end.
- INSIDE means inside a range of eight, in one spread, on one day. A lender who declines to lend across the date leaves no print, so a quiet spread is not a finding that nothing happened.
- Trades on the effective date of a Fed decision may have been agreed before the announcement the previous afternoon. Only trade-level timestamps would settle it, and this file has none.
- Volumes include affiliate repo and rates do not, so a volume is context and not the sample behind the rate; it is never used as a weight.
- A missing value means no trading or a disclosure edit. It is never read as zero and never as evidence about activity.
- Preliminary prints lag by two business days and are revised. The January fetch decides the registered reading and the comparison months alike; the revisions file shows how far the numbers moved.

Why these eight: four months with no Fed decision near the month-end (November 2025, February, May and August 2026) and four where the day before is itself the effective date of the decision, so no decision falls inside the loan (October 2025, January, July and October 2026). Under exchangeability, a December above all eight has probability 1 in 9; the months are not independent, so that is a guide and not a test.

## How to rerun

Source: Office of Financial Research, tri-party repo rates excluding Federal Reserve trades, preliminary vintage, free public data from data.financialresearch.gov, no key. The OFR says the rates are not intended to be referenced in contracts.

1. `python3 bin/term_repo_turns.py fetch` (supervisor only; nine GETs at least 3 seconds apart; before 2027-01-05T20:00Z it stops at 23 December 2026).
2. `python3 bin/term_repo_turns.py build --vintage YYYYMMDD --stage pre` (layout and coverage; prints no rate and no spread).
3. `python3 bin/term_repo_turns.py build --vintage YYYYMMDD --stage dry` (the rule engine over the real dates with every value hidden).
4. `python3 bin/term_repo_turns.py build --vintage YYYYMMDD --stage describe` (writes this folder, except registered.csv).
5. On or after 2027-01-05T20:00Z, with a vintage fetched then: `python3 bin/term_repo_turns.py build --vintage YYYYMMDD --stage register`. It writes registered.csv once; a second run exits 5; exit 6 means the December print is not in yet and nothing was written.
6. `python3 bin/term_repo_turns.py selftest` (synthetic data, no network) and `bash bin/check.sh --all` (guard M30).
