# Gold against the US 10-year real yield

This folder measures how gold's monthly average price moved with the US 10-year inflation-protected (real) Treasury yield from 2006 to September 2026, holding the dollar fixed, and checks whether that link shifted once.

Sources are the World Bank (Commodity Price Data, "the Pink Sheet"), the US Department of the Treasury (par real yield curve rates) and the Board of Governors of the Federal Reserve System (the nominal broad dollar index, Data Download Program). Details and citations are in [SOURCES.md](SOURCES.md). The script is [bin/gold_real_yield_break.py](../../bin/gold_real_yield_break.py); the specification, with its amendments and the builder's decisions, is [the spec](../../_research/2026-10-18-Gold-Real-Yield-Break-Spec.md). Every CSV starts with a line that begins `# source:`; **readers must skip lines that start with `#`.**

## Terms, as they are used here

- **Real yield.** The 10-year Treasury yield after allowing for expected inflation, read off Treasury's daily inflation-protected (TIPS) curve, in percent. A change of one **percentage point (pp)** is a change of 1.00 in that number.
- **Log points.** The change in the natural logarithm of a price. Small log changes are close to percent changes (0.05 log points is about 5%), but the exact percentage is `100(e^b - 1)`: a slope of -0.202 is -18.3%, not -20.2%. Both are printed.
- **HAC standard error.** A standard error that allows the regression's errors to be correlated from month to month and to vary in size (heteroskedasticity and autocorrelation consistent; here Newey-West with a Bartlett kernel and 12 monthly lags). The classical standard error is printed too, labelled "not the precision statement".
- **Fixed-b.** The way the 95% band is built. A long HAC lag against a modest sample makes the t statistic fatter-tailed than a normal one, so the band uses the Kiefer-Vogelsang fixed-b critical value, 2.105 at 12 lags over 248 months, not 1.96. The build checks by simulation that this test rejects a true zero at most 6.5% of the time (it measured 6.0% and 6.2%).
- **Cointegration.** Two trending series are cointegrated if a combination of them stays put even though each wanders. The levels objects below are reported only if the **Engle-Granger test** finds this on the fit sample: it regresses gold's level on the yield and the dollar, then tests whether the leftover (the residual) wanders like a random walk, which means no cointegration, or keeps returning to zero.
- **SSR.** The sum of squared residuals: how much of the monthly gold changes the fitted line leaves unexplained. Smaller is a better fit.
- **Wald statistic.** A number that measures how far estimated coefficients are from a hypothesised value (here, zero change) in units of their own uncertainty; large means unlikely to be chance. The HAC version uses the HAC covariance.
- **Break scan.** A search over every possible date for the one date at which the regression's coefficients changed. It is descriptive here, and it carries no verdict. Its statistic is the **sup-Wald**: the HAC Wald statistic for "all three coefficients changed after this month", computed for every candidate month, then the largest taken. The most likely break month is the candidate that leaves the smallest SSR.
- **Chow test.** The same Wald statistic for a break at one date chosen in advance (so no search, and a plain chi-square(3) p-value).
- **Trim.** The share of the sample kept clear of each end when scanning for a break: 0.05, 0.15 or 0.25. Trim 0.15 was the pre-registered one.
- **Bai interval.** Bai's (1997) 95% interval for the break date: the estimated break month plus and minus a half-width `h`. It gets wide when the shift is small against the noise.

## What the data say

**P1, the one confirmatory test** (written down before any regression was run): the monthly change in the log gold price on the monthly change in the 10-year real yield, with the change in the log broad dollar index as a second regressor, February 2006 to September 2026, 248 months.

- In months when the 10-year real yield rose 1 pp more, gold's monthly average price was about **7.7% lower** (exact; -0.0796 log points per pp), holding the broad dollar fixed. The 95% fixed-b band is -0.1116 to -0.0476 log points, which is **4.6% to 10.6% lower**. HAC standard error 0.0152; classical 0.0126. The dollar coefficient is -0.80 (a 1% rise in the dollar goes with a 0.8% lower gold price; band -1.31 to -0.28). R-squared 0.29.
- **Verdict under the pre-registered rule: SUPPORTS** (the slope is at or below the -0.050 log-points materiality line, and the whole band is below zero). One caveat the rule does not show: the band's upper end, -0.0476, sits just above the -0.050 line, so the sample does not rule out a slope slightly weaker than the line.
- The smallest effect this sample could reliably detect (80% power) is 0.0448 log points per pp, which is why the line was set at 0.050: it is at the edge of what 248 months can see.
- It is a **same-month association, not a cause or a forecast**. Both gold and the real yield respond to the same news. It says nothing about daily or weekly horizons, and official gold buying is not in the regression, so the result neither shows nor rules out that buying explains anything.

**B1, the break scan** (descriptive; no verdict). The regression is re-fitted with all three coefficients allowed to change after each candidate month, and the largest HAC Wald statistic is taken. The p-value is a stationary bootstrap (999 draws, mean block 6 months) because a plain HAC sup-Wald against asymptotic tables rejected a true no-break series 41% to 46% of the time in an independent reviewer's test. The asymptotic Andrews table is printed beside it and used for nothing.

| trim | candidate break months (last month of the first regime) | bootstrap p | most likely break month | Bai half-width |
|---|---|---|---|---|
| 0.05 | 2007-02 to 2025-08 | 0.009 | 2007-03 | 3.4 months |
| **0.15 (pre-registered)** | **2009-03 to 2023-07** | **0.188** | **2021-12** | **37.2 months (+-38, unclipped)** |
| 0.25 | 2011-03 to 2021-07 | 0.052 | 2021-03 | 41.9 months |

Re-run with a one-month dummy for 2021-12 (the month Treasury changed its yield curve method) the pre-registered trim gives p = 0.202 and a most likely month of 2021-10. The month where the sup-Wald is largest at trim 0.15 is 2020-12, which differs from the most likely (lowest-SSR) month; both are in `break.csv`. The trim 0.05 row is dominated by a first regime of only 14 monthly changes against a 12-lag HAC, which makes that statistic extreme (226); it is the statistic as specified, and nothing rests on it.

What this may be read to say, and no more: the bootstrap p-value at trim 0.15 is 0.188. The most likely break month is 2021-12, but the date is poorly pinned down: the Bai interval is +-38 months, from late 2018 to early 2025. The width is what a slope shift of about 0.12 per pp produces against this much noise; to date a break to within +-8 months, the shift would have to be about 0.26 per pp or more (`break.csv` prints that shift for half-widths of 4, 6, 8, 12 and 18 months: 0.37, 0.30, 0.26, 0.21, 0.17). Because the interval is wide and the p-value large: **no single break large enough to date was found; B1 cannot see a slope break below about 0.17 per pp, so this says nothing about 2024-26.**

A note on dates, because two numbers carry "2021-12" and mean different things. In the break scan a month is the **last month of the first regime**: "most likely break month 2021-12" means the first regime runs to 2021-12 and the second starts in 2022-01. In the Chow test below, "regime 2 from 2021-12" means the second regime **starts** in 2021-12, so the first regime ends in 2021-11. The two are one month apart.

**No trim can return a 2026 break date: the latest candidate under any trim is 2025-08. A 2026 change in sensitivity is not testable as a break date on this sample.**

**A temporary two-year change in sensitivity is not tested by any confirmatory object.** P1 is the one confirmatory test; the break scan is descriptive.

**Sub-periods and rolling slopes (descriptive; chosen after the rise had been seen, so they confirm nothing).** Same regression, with the band built as above:

| window | months | slope on the real yield, log points per pp | 95% band |
|---|---|---|---|
| 2006-02 to 2021-11 | 190 | -0.1018 | -0.1407 to -0.0630 |
| 2021-12 to 2023-12 | 25 | -0.0292 | -0.0806 to +0.0223 |
| 2024-01 to 2026-09 | 33 | -0.0396 | -0.1706 to +0.0913 |

The two short windows use the rule-of-thumb lag (2 and 3) and are flagged `short_window`; their bands include both zero and the long-sample slope. "Gold's real-yield sensitivity collapsed in 2024-25 and came back in 2026" therefore **stays a HYPOTHESIS**. The 213 rolling 36-month slopes (window ends 2009-01 to 2026-09, moving-block bootstrap with 6-month blocks) are in `rolling36.csv` and `rolling36.svg`. They overlap, so no window is counted and no share of them is quoted.

**Known-date Chow tests (descriptive; here the named month is the first month of regime 2).** Regime 2 from 2008-12: HAC Wald 2.09, p = 0.55. From 2021-12: Wald 20.90, p about 0.0001. The date 2021-12 was chosen after the post-2021 rise had been seen, and it is also the month of the curve-method change, so this is a description of the sample, not a test.

**Levels, only after cointegration.** The Engle-Granger test on the fit sample (2006-01 to 2021-11, 191 months) gives -2.80 against a 5% critical value of -3.79: no cointegration. Every levels row in `levels_summary.csv` therefore says `suppressed_no_cointegration` and carries no number, and no levels number is printed anywhere. (The full-sample test, -1.11 against -3.78, is information only and gates nothing.)

## The seams in the data

- **2021-12-06 (Treasury).** Treasury changed the curve's spline from a Hermite (HS) to a monotone-convex (MC) one. Treasury's own overlap file shows MC higher than HS by 0.026614 pp on average over 251 days. That gap is added, computed by the build from the overlap file and never typed in, to every daily print dated before 6 December 2021, so the whole series is on the MC basis. It touches the monthly changes only in 2021-12 and 2022-01. The unadjusted version (D3) gives the same slope to four decimals (-0.0796); a version with one-month dummies for 2008-12, 2021-12, 2022-01 and 2025-06 (D4) gives -0.0814 (band -0.1152 to -0.0475). The dummies' HAC errors are not meaningful for a one-month regressor and are flagged.
- **2008-12 (Treasury).** From 1 December 2008 the curve uses the most recently auctioned TIPS as knot points. Treasury published no overlap file, so it cannot be adjusted; December 2008 is also the crisis. It is covered by the Chow test above and by a dummy, and an effect of the method cannot be told from an effect of the market in that month. The earliest break candidate under the 0.15 trim is 2009-03, after it.
- **2025-06 (the gold series).** The World Bank describes its gold series as the London afternoon fixing before June 2025 and a spot average from June 2025, with no overlap month. A dummy for 2025-06 is in D4. A local cross-check against the GLD-implied London PM price needs a file that is not in the repository, so an outside reader's build prints SKIP for that check; that is expected.
- **The dollar index.** The Fed's file labels its unit as a January 1997 base, but its values are January 2006 = 100. The build asserts the value and ignores the label. The index starts in 2006-01, which is why the sample does; a 2003 start without the dollar is kept as a descriptive row (D2: -0.0965, band -0.1195 to -0.0735), and dropping the dollar changes the slope because the yield and the dollar move together (D1: -0.1021).

## Outputs that stay on this computer

The World Bank's reuse terms for the gold row are unclear, and its workbook names commercial data vendors among the gold sources. So the workbook is kept in a cache outside the repository (`~/gold_ry_cache/`; the script refuses a cache inside the repository), and no committed file carries a gold price, a log gold price, a gold change, a fitted value, a per-month residual or a residual in standard-deviation units. Coefficients, standard errors, intervals, test statistics and break dates are published, with the World Bank cited; they are not a copy of the data. The monthly panel with gold and the residual path (if a levels fit were reported) are written to `~/gold_ry_cache/local_outputs/` only.

**This follows the Bank's redistribution terms; it is not about secrecy.** Public GLD data already approximates the Pink Sheet series: an independent reviewer measured a median monthly gap of 0.034% before June 2025 (that figure was relayed, and this build cannot recompute it without the local sponsor file).

One per-month file does depend on gold: `rolling36.csv`, the rolling slopes and bands. At four decimals those would, with the coefficients and `monthly_inputs.csv`, let a reader rebuild monthly gold changes closely (the reviewer's simulation: correlation 0.83 to 0.95). They are therefore published at **two decimals** (reviewer's simulation: correlation about 0.35), and the leak scan allows exactly that exception. The scan (check K08) lists the only files allowed in this folder and the exact columns of each, and fails on a third decimal in the rolling file.

## Files

| file | content |
|---|---|
| `monthly_inputs.csv` | 2003-01 to 2026-09: monthly mean 10-year real yield (MC basis and official), number of days, share of days on the MC basis, the broad dollar index (2006-01 = 100), seam flags. No gold. |
| `results.csv` | One row per registry object and coefficient: P1, D1 to D5, and the D9 checksums. |
| `cointegration.csv` | The Engle-Granger tests (fit sample is the gate; the full sample is information). |
| `break.csv` | The break scan: 3 trims, with and without the 2021-12 dummy. |
| `chow_known_dates.csv` | HAC Chow tests at 2008-12 and 2021-12. |
| `rolling36.csv`, `rolling36.svg` | Rolling 36-month slopes and bootstrap band, 2 decimals. |
| `levels_summary.csv` | The levels objects (suppressed here). |
| `checks.csv` | Cross-checks K01 to K09. |
| `vintages.csv`, `fetch_log.csv` | The file versions used, and every request made. |

Commands: `python3 bin/gold_real_yield_break.py selftest` (30 guards, no network), `... selftest --mutants` (each guard must fail on its mutant), `... fetch` (at most 12 requests, 8 for a full fetch; any refusal writes `~/gold_ry_cache/STOP` and ends the run, and only a person deletes it), `... build` (offline from the cache; a re-run is byte-identical). The verdict is registered on the 2026-09 sample; later months are updates and do not change it.

## Appendix

**Registry of estimated objects** (fixed; an object id outside it is a hard failure). Confirmatory: `P1` only, at alpha = 0.05 with the fixed-b critical value. Descriptive: `B1` the sup-Wald break scan at trims 0.05, 0.15 and 0.25 with and without the 2021-12 dummy; `D1` P1 without the dollar; `D2` 2003-02 to 2026-09 without the dollar; `D3` P1 on unadjusted official yields; `D4` P1 with dummies for 2008-12, 2021-12, 2022-01 and 2025-06; `D5` P1 over three sub-periods; `D6` rolling 36-month slopes; `D7` HAC Chow tests at known dates; `D8` the levels objects, conditional on cointegration; `D9` reproduction checksums.

**Decision rule** (written 18 October 2026, before any regression was run). P1's slope `b`, in log points per pp, with the 95% fixed-b HAC interval `[lo, hi] = b +- 2.105 se_HAC`:

- SUPPORTS a material same-month link: `b <= -0.050` and `hi < 0`.
- AGAINST a material link: `lo > -0.050`. The interval excludes a slope of 0.050 log points per pp, and this case includes any zero or positive slope with a tight interval.
- INCONCLUSIVE: everything else. That covers an interval that includes both -0.050 and 0, and a negative interval whose point estimate is weaker than -0.050.

B1 carries no verdict. The page may say only: the bootstrap p-value at trim 0.15; the most likely break month with its Bai interval and the slope shift an interval that narrow would need; and, when the interval is wide or the p-value large, that no single break large enough to date was found and that B1 cannot see a slope break below about 0.17 per pp. The months at trims 0.05 and 0.25, and the run with the 2021-12 dummy, are reported beside it. Official tonnes are never offered as the explanation.
