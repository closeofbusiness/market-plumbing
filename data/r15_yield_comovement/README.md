# Do the four big 10-year yields move together more than they did in 2018-19?

This folder measures how much of the week-to-week movement in the 10-year government bond yields of the United States, Germany (the German federal government bond, the Bund), the United Kingdom (the gilt) and Japan (the Japanese government bond, JGB) is shared by all four, and tests one question registered in advance: was that shared part different in 2024 to date from what it was in 2018-19? Only derived statistics are published here. No yield level and no weekly change is.

## Result (as of 2026-10-18)

**Verdict: INCONCLUSIVE.** Share of the correlation matrix's trace taken by the common component of the four weekly changes: 0.779 in 2018-19 (102 of 104 weeks used) and 0.714 in 2024 to 2026-10-16 (146 of 146 weeks used). Change -0.064; 95% interval [-0.200, 0.071]; 90% interval [-0.178, 0.049]. Calibration: the historical placebo floor (47 pre-2018 window layouts; placebo spread 0.0690, bootstrap spread 0.0298, used 0.0690). Downgrade reasons: none fired; neither the SHIFT condition nor the equivalence condition holds. Grade: MEASURED for the shares, and a pre-registered test result for the shift.

The rule, written before any 2018-or-later statistic was computed: SHIFT if the 95% interval excludes zero and the change is at least 0.10; NO SHIFT AS LARGE AS 0.15 if the 90% interval lies inside plus or minus 0.15; otherwise INCONCLUSIVE (also when both hold, or when a stale series, heavy week loss, a near-flat series, a different answer at another block length, or a bad file seam undermines it).

The equivalence verdict (NO SHIFT AS LARGE AS 0.15) was reachable: it needs the used spread below 0.091, and it was 0.0690.

## Terms

- **Trace.** The sum of the diagonal of the correlation matrix. With one 1.0 per series it equals the number of series (4 here), so the share is the largest eigenvalue divided by 4.
- **Bootstrap spread.** The standard deviation of the change in the share when blocks of 8 consecutive weeks are resampled within each window, 2,000 times. It measures sampling noise inside these two windows only.
- **Layouts and placebo spread.** A layout is a pair of pre-2018 windows placed like the real pair: 104 weeks, a gap of 209 weeks, then 146 weeks. Starts are stepped by 13 weeks through 1997-2017, giving 47 layouts. The placebo spread is the root mean square, about zero, of the change in the share across those layouts: how far apart two windows this far apart typically differed before 2018. The layouts overlap heavily (at 47 layouts only 2 are mutually disjoint), so the placebo spread is itself imprecise.
- **Used spread.** The larger of the bootstrap spread and the placebo spread. Intervals are the change plus or minus 1.96 (95%) or 1.645 (90%) times it.
- **TIPS.** US Treasury Inflation-Protected Securities; the 10-year TIPS real yield enters only one descriptive set.

## How to read the number

- **Scale.** The share is 0.25 for four unrelated series and 1.0 for four moving in lockstep.
- **Noise floor.** In a finite sample, unrelated series still show some correlation, so their share sits about 0.31 at 104 weeks and 0.30 at 146 weeks, not 0.25 (synthetic: means over 4,000 draws of four independent t(5) series, spread 0.019 and 0.016).
- **Denominators.** The share is the largest eigenvalue of the correlation matrix divided by its trace, which is the number of series: 4 for the main set, 3 without Japan, 5 with the TIPS yield. Correlations, not covariances, so a series' scale does not matter. A two-series figure (for example 0.88) has denominator 2 and cannot be compared with these.
- **Weeks used.** 102 of 104 calendar weeks in 2018-19: every week needs a valid change in all four series (listwise). The JGB has no print in the week ending 2019-05-03 (Japan's Golden Week holidays), so that week is lost, and the change into the next week (ending 2019-05-10) is dropped because its earlier print is not in the immediately preceding week.
- **The verdict compares two realised regimes.** It asks whether 2024 to date differs from 2018-19 by more than windows this far apart differed in the history before 2018. It does not estimate a permanent parameter. A SHIFT says these two periods differed, not that the world changed for good.
- **The placebo changes are mostly positive, but the spread is measured about zero.** Across the 47 layouts the change in the share has minimum -0.021, median 0.040 and maximum 0.153, and 42 of 47 are above zero. The placebo spread (0.0690) is the root mean square about zero, not the standard deviation about their mean (which would be 0.0462, smaller), so history's own regime differences (1998, 2008, 2013, the 2016 cap on JGB yields) count as noise and the bar for a SHIFT is higher. Because the layouts overlap, it could be dominated by one episode (spec OPEN-4).

### This test cannot detect small changes

At the spread used here (0.0690) the smallest change the test would catch 80% of the time is about 2.8 x 0.0690 = 0.193. A true change smaller than that will usually come back INCONCLUSIVE, which does not mean nothing changed. A change in Japan's link to the other three is below it too (see the Japan note below).

## Descriptive results (intervals, no verdict)

| window | series set | weeks used / calendar | share | 95% interval | mean pairwise correlation | status |
|---|---|---|---|---|---|---|
| w2018_19 | nom4 | 102 / 104 | 0.779 | [0.734, 0.824] | 0.704 | ok |
| w2020_21 | nom4 | 105 / 105 | 0.739 | [0.689, 0.789] | 0.651 | ok |
| w2022_23 | nom4 | 104 / 104 | 0.682 | [0.628, 0.736] | 0.560 | ok |
| w2024_latest | nom4 | 146 / 146 | 0.714 | [0.677, 0.752] | 0.615 | ok |
| w2024_25 | nom4 | 104 / 104 | 0.722 | [0.678, 0.765] | 0.625 | ok |
| w2026_ytd | nom4 | 42 / 42 | 0.710 | [0.635, 0.785] | 0.609 | ok |
| full | nom4 | 457 / 459 | 0.699 | [0.672, 0.727] | 0.591 | ok |

- Without Japan (US, Bund, gilt; k = 3): 0.840 in 2018-19, 0.806 in 2024 to date; change -0.034, 95% interval [-0.136, 0.068], 90% interval [-0.120, 0.052].
- **Japan note.** The mean correlation of the JGB with the US, Bund and gilt was already 0.650 in 2018-19 and was 0.523 in 2024 to date: a change of -0.127, with a 95% interval of [-0.609, 0.355] (calibration: placebo_floor; placebo spread 0.2461). That interval is 0.965 wide and is too wide to say anything: this build cannot tell a fall in Japan's link to the others from no change, nor a rise. The smallest change in that correlation it could catch is about 2.8 x 0.2461 = 0.689. What the build can see is limited to the four-country share, which mostly reflects the US-Bund-gilt block (without Japan the share is 0.840 and 0.806); a change in Japan's correlation moves it by well under the smallest detectable change above.
- Other comparisons (2018-19 to 2022-23, 2022-23 to 2024-latest, 2024-25 to 2026 year to date, and the same pair with the TIPS yield added) are in `shift_test.csv`, role `descriptive`.
- The Bank of Japan capped the 10-year yield in part of the baseline window. No code depends on its dates.
- **Timing caveat.** The Japanese yield is the 3pm Tokyo close, which is about a trading day earlier than the other three. The descriptive set `nom4_jgb_lead1` moves it to the next Tokyo close; it and the euro-area-AAA variant `nom4_ecb` are robustness checks only.

## What this cannot say

- Which country drives the others. Correlation has no direction, and no lead-lag is estimated.
- That a "global term premium" or any flow caused a move. Nothing here is regressed on a flow or position.
- How much of a cumulative level move (for example the US rise since end-2023) is "global". A share of weekly-change variation does not split a level change.
- Anything from covariance or variance shares. They are not computed, because the four series are different objects: a par yield, a Svensson zero-coupon yield, a continuously compounded spot yield and a constant-maturity yield.
- Small changes (see above).

## Files

`windows.csv`, `pairs.csv`, `shift_test.csv`, `series_stats.csv`, `freshness.csv`, `checks.csv` (the pins, identities, seams and the checkpoint re-derivation), `fetch_log.csv`, `SOURCES.md`. Every CSV starts with a `# source:` line and has an exact column allowlist. `python3 bin/r15_yield_comovement.py selftest` needs no network; `fetch --archive` then `build` regenerates everything from the five issuers. The raw files live outside the repository (`~/r15_yield_cache/`) and are never committed.
