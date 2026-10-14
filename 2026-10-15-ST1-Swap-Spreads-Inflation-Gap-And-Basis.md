# ST1: US swap spreads, the inflation-swap gap and the cross-currency basis, from the public swap tape (15 Oct 2026)

**Status: FINDING. Supervisor, 15 Oct.** A first daily ledger, built from public price reports of US-reported interest-rate swaps.
The principal ruled that the files may be scripted despite DTCC's site terms (THE_ASK.md E-024). The conditions: the use is
non-commercial; no DTCC file or record is published; only derived statistics are published, and they cite the source.

- **How it was built.**
  - Grok batch g4, item 3, set the question.
  - Three investigation lenses, a spec, and two adversarial reviews (correctness and practicality).
  - The supervisor re-specified it after the reviews; then a builder agent built it.
  - An independent verifier re-derived every headline number for 13 Oct 2026 with its own code, and all of them matched.
  - The spec, with the review amendments as section 17:
    [`_research/2026-10-14-Swap-Tape-Ledger-Spec.md`](_research/2026-10-14-Swap-Tape-Ledger-Spec.md).
- **Script:** [`bin/swap_tape_ledger.py`](bin/swap_tape_ledger.py), stdlib only.
  - `selftest` runs 184 checks and three deliberately broken builds, and each broken build must fail a check.
  - `build` checks the New York trading window at the start of every run.
- **Tables:** `data/swap_tape/`, with a column dictionary in its README and the source statement in its SOURCES file.
- **Source:** DTCC Public Price Dissemination, CFTC cumulative rates reports (pddata.dtcc.com).
  - 522 weekday files, from 14 Oct 2024 to 13 Oct 2026, all retrieved on 14 Oct 2026.
  - 521 of them came through the logged fetcher, sequentially and at least five seconds apart, with no refusals and no date
    missing. The 13 Oct 2026 file was fetched earlier the same day, during the access check, and is not in the log.
  - The raw files stay outside the repository.
- **Treasury yields:** the US Treasury's daily par and real yield curves (public domain).

## What is measured, and how

- **Swap spread.** The median SOFR overnight-index swap rate on trades executed between 14:30 and 16:30 New York time, minus the
  Treasury par yield of the same maturity.
  - The window brackets the Treasury's 15:30 snapshot. The whole-day 10-year figure differs from the windowed one by 0.4bp on
    13 Oct. Over the 484 days with both figures the difference has a standard deviation of 1.8bp and reaches 7.8bp, on
    18 Dec 2024.
  - It is quoted the way dealers quote it: the raw rate difference. A bond-equivalent version is published beside it, and is
    1–2bp less negative.
  - Negative means the Treasury yields more than the swap.
- **Inflation-swap gap.** The median zero-coupon CPI swap rate, minus the Treasury par breakeven put on the same compounding
  basis. It is the gap between two different instruments, not a second breakeven.
  - It uses the whole day, because CPI swaps trade too thinly inside the window.
- **Cross-currency basis.** The spread on the euro, yen or sterling leg of a 1–5-year floating-for-floating swap against flat
  SOFR. Negative means a premium to borrow dollars.
  - It is published as a pooled 1–5-year median. A single tenor is published only on days with at least ten trades in it.
- **Publication floor (E-024).**
  - Fewer than five trades: only the count is shown.
  - Five to nine trades: the count and the median.
  - Ten or more: quartiles as well.
  - Minima, maxima and notional-weighted figures are never shown.

## The answer

**1. US swap spreads are negative at every maturity, least so at the short end. They are about 4–16bp less negative than two
years ago. Their most negative single days were in April 2025.** *MEASURED.*

| | 2y | 5y | 10y | 30y |
|---|---:|---:|---:|---:|
| 13 Oct 2026 (trades in the window) | −13.0bp (12) | −27.8bp (32) | −38.9bp (35) | −65.2bp (23) |
| Monthly median, 14–31 Oct 2024 | −20 | −33 | −47 | −82 |
| Monthly median, Apr–Jul 2025 | −22 to −24 | −36 to −38 | −54 to −55 | −86 to −88 |
| Most negative day | −29.5 (8 Apr 2025) | −42.2 (8 Apr 2025) | −58.5 (21 Apr 2025) | −93.4 (21 Apr 2025) |
| Monthly median, 1–13 Oct 2026 | −14 | −28 | −39 | −66 |

- **The narrowing began in October 2025, and it was not one-way.**
  - The 10-year monthly median went −53 (Sep 2025), −47 (Oct), −44 (Nov), −40 (Dec), −37 (Jan 2026).
  - It then widened back to −47 in March 2026, its October 2025 level. The 30-year went past its October level: −80 against
    −75.
  - It is −39 now.
  - The widest monthly medians were July 2025 for the 10-year (−55) and May 2025 for the 30-year (−88).
  - The single-day extremes in the table sit within the ledger's resolution of about 2bp.
- **Timing only.** The change to the banks' leverage ratio was optional from 1 Jan 2026 and effective from 1 Apr 2026. The dates
  are from the speech quoted in the g4 returns, item 13. The narrowing started before that rule, and the re-widening in
  February and March fell before its effective date. This ledger measures the spread, not why it moved.
- **Noise.**
  - Day-to-day changes in the 10-year spread have a standard deviation of 1.2bp (469 adjacent pairs), and 0.9bp on days when
    the 10-year Treasury moved 2bp or less.
  - No day-to-day change reached 10bp.
  - A residual timing effect remains. On average the 10-year spread moves −0.08bp for each 1bp the Treasury moves, so a 10bp
    Treasury day shifts it by about 0.8bp.
- **Coverage.**
  - The 10-year headline has at least ten trades on 97.2% of Treasury trading days (498).
  - The 30-year spread was negative on every one of the 481 days with a 30-year figure.

**2. Inflation swaps price inflation above the Treasury breakeven: about +13bp at 10 years now, within +12 to +22bp by month
over two years.** *MEASURED for the gap; the reasons for it are not measured here.*

| Monthly median | 5y | 10y | 30y |
|---|---:|---:|---:|
| 14–31 Oct 2024 | +26 | +20 | +17 |
| 1–13 Oct 2026 | +16 | +13 | +11 |
| Range of monthly medians | −4 to +26 | +12 to +22 | +10 to +23 |

- **The 5-year gap swings with the calendar.** It is low from January to April and high from June to October, in both years
  (−3 in March 2025 and −4 in March 2026; +22 in August–October 2025). That fits the seasonality of the consumer price index in
  shorter inflation swaps, but it is not tested here (HYPOTHESIS). Do not read a month-to-month change in the 5-year gap as a
  change in financing conditions.
- The 30-year gap rests on thin trading: 240 days have a figure.

**3. The dollar-borrowing premium against the yen has roughly halved, and against the euro and sterling it is near zero.** *MEASURED,
pooled 1–5 years.*

| Monthly median, pooled 1–5y | EUR/USD | JPY/USD | GBP/USD |
|---|---:|---:|---:|
| 14–31 Oct 2024 | −5bp | −48bp | 0bp |
| Apr 2025 | −4 | −44 | −1 |
| Jan 2026 | 0 | −28 | +5 |
| 1–13 Oct 2026 | −4 | −22 | +2 |

- **The yen move is not a change in the mix of maturities.**
  - The average maturity traded stayed between 2.5 and 3.6 years by month.
  - Each maturity narrowed on its own, on days with at least ten trades:
    - 1 year: about −39bp to −20bp;
    - 3 years: about −49bp to −23bp, to September 2026;
    - 5 years: about −53bp, its first cell on 21 Nov 2024, to −27bp.
  - The 1- and 3-year starting values each rest on a single day.
  - The path was not one-way. The basis widened again in April 2025, March 2026 and July 2026. It first reached half its
    October 2024 level in September 2026.
- **Hedging cost.** The basis is one part of what a yen- or euro-based investor pays to hedge dollar assets. The other, larger
  part is the gap between the two currencies' short rates, and that is not in this ledger. A smaller yen basis means a smaller
  premium on top of that gap. It does not show that hedging got cheap, or that Japanese investors hedged more.

## What this does and does not establish

- **It fills the free-data gap for the basis, one part of hedging cost.** E-021 listed the cross-currency basis as not
  measurable on free data. It is now measured, as public swap prints.
- **It does not identify who traded, or why.** The tape carries no party identity. Nothing here says that a flow caused a spread
  to move.
- **It is US-reported swaps only.** Trades reported to other regulators' repositories are not in it.
- **Caveats.** The README lists four:
  - the pooled basis mixes maturities;
  - the inflation gap is not time-aligned;
  - weekend correction files are not fetched, which moved medians by at most 0.06bp on 13 Oct;
  - one trading platform is excluded from the headline.

## Observed vs inferred

- **Observed:** every spread, gap and basis figure, as medians of public trade reports against public Treasury yields.
- **Inferred:**
  - the seasonal reading of the 5-year inflation gap (HYPOTHESIS);
  - any link between the swap-spread narrowing and bank regulation (not claimed; timing only).
