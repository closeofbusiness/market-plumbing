# Spec: comovement of 10-year government yields, US, Germany, UK, Japan (r15; 18 Oct 2026, amended after second review)

*Spec author's draft for the supervisor. E-021 build queue item 6; E-021 note, item 15. The earlier design is
`_research/2026-10-14-Grok-G4-Returns.md`, Item 15; Grok's attack on it is the g7 return 4. The supervisor's rulings of 18 Oct
outrank Grok wherever the two differ, and they are applied throughout. Section 11 maps each ruling to the section that carries it;
section 12 lists the second-review amendments. Every URL in section 2 was requested once by the spec author on 18 Oct 2026, with the
neutral User-Agent. No real-data statistic about 2018 or later was computed, except the published 30-week g4 checkpoint (8.4) and
counts of which weeks have prints (for the d2 budget). The calibration in section 4.5 uses synthetic data only.*

## 0. Goal

1. Measure how much of the weekly movement in the US, German, UK and Japanese 10-year yields is common to all four. The measure is
   the first-eigenvalue share of their correlation matrix.
2. Test one pre-registered question: did that share differ between the 2018–19 window and the 2024–latest window?
3. Report everything else (other windows, pairs, robustness variants) as description, with intervals.

**The verdict compares two realised regimes.** It asks whether the 2024–latest window differs from the 2018–19 window by more than
windows this far apart typically differed in the history before 2018 (section 3.5). It does not estimate a permanent parameter.
A SHIFT says these two periods differed. It does not say the world changed for good.

**What the result can be used to say.** "Weekly changes in the four 10-year yields shared a common component worth X of the
correlation matrix's trace (k = 4), and between 2018–19 and 2024–latest that share rose, fell, did not move by as much as 0.15,
or the data cannot tell." Grade: MEASURED for the shares, and a pre-registered test result for the shift.

**What it cannot be used to say.**
- Which country drives the others. Correlation has no direction, and no lead-lag is estimated.
- That a "global term premium" or any flow caused a move. Nothing here is regressed on a flow or position.
- How much of a cumulative level move (for example the US +113bp since end-2023) is "global". A share of weekly-change variation
  does not split a level change.
- Anything from covariance or variance shares. Those are not computed, because the four series are different objects (2.1).
- Small changes. The test cannot see a change in the share smaller than its minimum detectable effect (4.5). That includes the
  likeliest change, Japan's yield moving with the others again.

## 1. Hard requirements

**R1. Raw files stay outside the repository.**
- Cache: `~/r15_yield_cache/`. It can be overridden with `--cache`, but any path inside the repository is refused.
- Every downloaded file, and the weekly panel built from them (`~/r15_yield_cache/derived/weekly_panel.csv`), lives there.
- No yield level and no weekly change is ever written under the repository: not in `data/`, not in `bin/`, not in a test
  fixture. Fixtures are synthetic.

**R2. Only derived statistics are committed.** That means shares, correlations, standard deviations, intervals, counts, dates,
and the pins in section 8. Each output has an exact column allowlist (section 6). A header that differs from it is a hard failure.

**R3. Sources are cited.**
- Every CSV output starts with a `# source:` line naming all five issuers, with retrieval dates taken from `fetch_log.csv`. The
  offline build is therefore byte-identical on re-run.
- `SOURCES.md` quotes each licence line from 2.3, and says that the project's CC BY 4.0 covers only the computation.

**R4. Fetches are polite.**
- Requests are sequential, at least 3 s apart, and at most 50 per run (a full fetch is 46; 2.2).
- User-Agent: `Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)`. Assert that it contains no `@`.
- Host allowlist: `home.treasury.gov`, `api.statistiken.bundesbank.de`, `www.mof.go.jp`, `www.bankofengland.co.uk`,
  `data-api.ecb.europa.eu`.
- GET only. Redirects are not followed.

**R5. Stop on refusal.**
- The latch is at the fixed path `~/r15_yield_cache/STOP`, whatever `--cache` says. No fetch happens while it exists.
- These write the latch: any status other than 200, a redirect, or a body that fails its content test (2.2).
- Nothing retries, and only a person deletes the latch. A socket fault ends the run without latching.
- `fetch_log.csv` gets one row per request.

## 2. Data

### 2.1 Series (the four primary series are different objects; only correlations are used)

| Short name | Issuer, exact series | What it is | Units | Release timing seen 18 Oct | Daily history |
|---|---|---|---|---|---|
| `us_nom` | US Treasury daily par yield curve, column `10 Yr` | 10-year **par** yield, semiannual bond-equivalent, end of day New York | percent | 16 Oct row present on 18 Oct | from 1990-01-02 (U1, 1990 file) |
| `bund_nom` | Bundesbank BBSIS `D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A` | **Svensson** fitted spot (zero-coupon) yield, listed Federal securities, 10.0 years residual maturity (a smooth curve fitted to bond prices) | percent (`Prozent`); compounding not stated (OPEN-3) | `Stand vom 16.10.2026 12:13:05`, last value dated 2026-10-16 | from 1997-08-07; month-end only before that (file comment) |
| `gilt_nom` | Bank of England nominal curve, sheet `4. spot curve` (`4. nominal spot curve` before 2005), the column whose maturity header is `10` | 10-year **continuously compounded spot** yield, fitted, London close | percent | latest-month zip modified 16 Oct 10:21 GMT, last row 2026-10-15 (T+1) | from 1979-01-02 |
| `jgb_nom` | Ministry of Finance JGB interest rate, column `10Y` | 10-year **semiannual constant-maturity** yield, **3pm Tokyo close** (MoF Q&A, relayed by Grok) | percent | `jgbcme.csv` modified 15 Oct 23:30 GMT, last row 2026/10/15 (T+1) | from 1986-07-05 |
| `us_real` (descriptive only) | US Treasury daily par real yield curve, column `10 YR` | 10-year TIPS par real yield | percent | 16 Oct row present on 18 Oct | not needed before 2017 |
| `ea_aaa` (robustness only) | ECB YC `B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y` | euro-area AAA Svensson spot. **Not the Bund** | percent per annum | last row 2026-10-15 | not needed before 2017 |

**No unit conversions.** Compounding conventions differ, but a convention change rescales a weekly change by about 1/(1+y), and a
correlation does not depend on scale. So the series are not converted, and no covariance share or level comparison is computed.
**No breakeven series exists in this build.** `us_real` enters only the descriptive set `nom4_usreal`, which never also holds a
nominal-minus-real column (Grok change 7).

**Timing is not negligible for the JGB leg.** The 3pm Tokyo close is 06:00 GMT, before that day's European and US sessions. So the
JGB "week" ends about one trading day before the other three weeks do. If news arrived evenly through the week, a weekly window
shifted by one of five days shares about four-fifths of its days with the unshifted window. That can pull JGB correlations down by
up to about a fifth. The descriptive set `nom4_jgb_lead1` (3.3) moves the JGB print to the next Tokyo close after the Friday US
close, and it is part of the robustness flag (4.2). The Bund's own timing is OPEN-1.

### 2.2 URLs and what one request each returned (18 Oct 2026, neutral User-Agent)

| # | URL | Status, size | Observed |
|---|---|---|---|
| U1 | `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{Y}/all?type=daily_treasury_yield_curve&field_tdr_date_value={Y}&page&_format=csv` (Y = 2026, 2019, 2018 and 1990 requested once each) | 200 each; 2026: 16,229 B | **The header differs by year.** 2026 has `"1.5 Month"` and `10 Yr` is the 13th field; the 2023 file (R1 cache) has no `1.5 Month`; the 1990 file has `Date,"3 Mo","6 Mo",…,"10 Yr","30 Yr"`. **The parser selects by name.** Rows are newest first; the 1990 file's oldest row is 01/02/1990. 10/16/2026 = 5.09 |
| U2 | same path with `type=daily_treasury_real_yield_curve` (2026) | 200 | Header `Date,"5 YR","7 YR","10 YR","20 YR","30 YR"`. 10/16/2026 = 2.74; 09/18/2026 = 2.68 |
| U3 | `https://api.statistiken.bundesbank.de/rest/data/BBSIS/D.I.ZST.ZI.EUR.S1311.B.A604.R10XX.R.A.A._Z._Z.A?format=csv` (the supervisor's URL) | 200, 234,788 B | **German format**: `;` separator, decimal comma (`3,48`), 9 header lines ending `Stand vom 16.10.2026 12:13:05 Uhr`. Rows are calendar-daily; weekends and holidays are `.` with flag `Kein Wert vorhanden`. First value 1997-08-07, last 2026-10-16 = 3,48; 7,411 numeric rows. Values for 2023-12-01..2026-09-25 equal the r3 cache (`lang=en`, 27 Sep) on all 714 dates. Grok's "ends 3 Aug" came from a different (StatisticDownload) URL |
| U4 | `https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv` | 200, 1,195,548 B, Last-Modified 1 Oct 2026 23:30 GMT | Two title lines, then `Date,1Y,…,10Y,…,40Y`. `10Y` is `-` before 1986/7/5 and has no gaps from 2017. Last row 2026/9/30 = 3.057. Dates are `YYYY/M/D` |
| U5 | `https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/jgbcme.csv` | 200, Last-Modified 15 Oct 2026 23:30 GMT | Title `Interest Rate (October 2026)`, same columns, rows 2026/10/1..2026/10/15. Ends with a blank row and a non-ASCII footer line, which the parser skips |
| U6 | `https://www.bankofengland.co.uk/-/media/boe/files/statistics/yield-curves/glcnominalddata.zip` | **one ranged GET of the last 64 KiB**: 206; full size 39,192,649 B; Last-Modified 2 Oct 2026 15:36:54 GMT | Central directory lists eight workbooks, `GLC Nominal daily data_1979 to 1984.xlsx` … `_2016 to 2024.xlsx`, `_2025 to present.xlsx`. The tail bytes are identical to a 7 Oct copy already on this Mac, so the member checksums match; the workbook facts below were read from that copy |
| U7 | `https://www.bankofengland.co.uk/-/media/boe/files/statistics/yield-curves/latest-yield-curve-data.zip` | 200, 325,932 B, Last-Modified 16 Oct 2026 10:21 GMT | Holds `GLC Nominal daily data current month.xlsx` plus the inflation, real and OIS files. Nominal 10y spot covers 2026-10-01..2026-10-15 |
| U8 | `https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A.SV_C_YM.SR_10Y?format=csvdata&detail=dataonly&startPeriod=2017-12-01` | requested 18 Oct with `startPeriod=2018-01-01`: 200, 2,243 lines | `TIME_PERIOD`,`OBS_VALUE`. 2018-01-02 = 0.5376153700264279; 2026-10-01 = 3.5921733451. The build uses 2017-12-01, so that the first 2018 week has a prior print |

**Content tests (R5),** run on each body before it replaces a cached file:
- U1, U2: the first line starts `Date,` and contains `"10 Yr"` or `"10 YR"`;
- U3: the first line contains the series key, and the header holds `Stand vom` or `last update`;
- U4, U5: a line `Date,1Y,` that contains `10Y`;
- U6, U7: zip magic `PK\x03\x04`, and a member name starting `GLC Nominal daily data`;
- U8: a header containing `OBS_VALUE`.

**BoE workbook layout,** read 18 Oct from all eight archive members and from U7's nominal file:
- **Sheet.** Use the sheet named exactly `4. spot curve` (2005 onward and U7) or `4. nominal spot curve` (1979–2004 members), and
  never a sheet whose name contains `fwd`. `2. fwd curve` has the same layout with different numbers (instantaneous forwards).
- **Column.** Row 4 is the maturity header: A4 = `years:`, then 0.5 … 40. Read the 10-year column as **the column whose row-4 value
  equals 10**; assert exactly one exists. It is index 20 (column U) in every member, but it is never hard-coded.
- **Rows.** Column A is a datetime, every weekday has a row, and UK holidays have an empty 10-year cell (2016–24 member: 2,348 date
  rows, 2,273 values). A `Refresh` or `#VALUE!` row 5 and many blank rows exist; skip any row whose column A is not a date.
- **Joining.** The archive member `2025 to present` ends 2026-09-30 and U7 starts 2026-10-01. Join them under the seam rule (2.4).
- **Provenance.** The `info` sheet says "Sources: Bloomberg Finance L.P., Tradeweb and Bank calculations", and it records past
  revisions.
- **Reader.** `openpyxl` with `read_only=True, data_only=True` (already in `requirements.txt`).

**Years fetched.**
- US nominal: 1997 through the current year. 1997–2016 serve the placebo (3.5), 2017 gives the first 2018 change, and 2020 and 2021
  are included.
- US real: 2017 through the current year.
- Request count. A full fetch is 30 + 10 + U3 + U4 + U5 + U6 + U7 + U8 = 46 requests. The default refresh is the current US year
  (2), plus U3, U4, U5, U7 and U8: 7 requests. U6 (39 MB) is fetched only with `fetch --archive`.

### 2.3 Licence handling (checked 18 Oct, one request each)

| Issuer | Terms seen | Handling |
|---|---|---|
| US Treasury | US Government work; 17 USC 105 (Grok, fetched 14 Oct) | Redistributable. Cached outside the repo anyway, so one rule (R1) covers all |
| Bundesbank | Website conditions (`https://www.bundesbank.de/en/homepage/user-information/conditions-for-the-general-use-of-the-website-764706`, 200): "free to save, forward or reproduce … for your personal or professional use"; must "not be altered"; cite "Source: Deutsche Bundesbank" | **Not clearly redistributable** under CC BY 4.0, which permits alteration. Cache only; commit derived statistics; cite |
| Bank of England | `https://www.bankofengland.co.uk/legal` (200): Resources are for personal or internal non-commercial use; reuse of third-party material needs that party's approval; the workbook names Bloomberg and Tradeweb | Cache only; commit derived statistics (supervisor ruling) |
| MoF Japan | `https://www.mof.go.jp/about_mof/notice/index.html` (200): PDL1.0 applies unless marked otherwise. That PDL1.0 allows commercial reuse is relayed by Grok, not re-read | Redistributable; cached outside the repo anyway |
| ECB | not re-read; Grok relayed "must be accurate, and the ECB must be cited" | Cache only; robustness use only |

Pins (section 8) quote at most five single values per source, as verification checkpoints. No series is reproduced.

### 2.4 Vintages, as-of date, staleness, seams

- **Vintages.** Each refetch keeps the previous cached file as `<name>.<sha8>.prev`. `build` compares overlapping dates between the
  two vintages, per series, and writes the count of dates revised by more than 0.005pp and the largest revision in bp to
  `checks.csv` K20. This is INFO; the BoE revises (`info` sheet).
- **As-of date.** It is the UTC date of the newest successful row in `fetch_log.csv`, never the clock.
- **Partial final week.** A week is included only if its Friday is on or before the as-of date. `weeks_calendar` is computed from
  the as-of date: it counts the Fridays f with window start ≤ f ≤ min(window end, as-of). With as-of 2026-10-18,
  `w2024_latest` has 146 calendar weeks; with as-of Thursday 2026-10-15, it has 145.
- **Business days** are Monday to Friday, with no holiday calendar.
- **Staleness (each source; Grok change 4).** `lag_bdays` counts the business days after a series' last valid print, up to and
  including the as-of date. A series with `lag_bdays > 5` is `stale`.
  - Expected lags, observed 18 Oct: Treasury 0, Bundesbank 0, BoE 1, MoF 1.
  - A stale primary series gives `w2024_latest` and `w2026_ytd` the status `stale_end`, and makes the primary verdict INCONCLUSIVE
    (d1).
  - Windows end at the **latest common week**: the latest included week in which all four primary series have a valid print.
- **Seams** are where BoE archive meets BoE latest, and where MoF `_all` meets current. Each seam is written to `freshness.csv`
  with one of these statuses:
  - `overlap_agree` (PASS): the two files share dates and agree within 0.0005pp;
  - `overlap_disagree` (FAIL; the date is named): they share dates and differ;
  - `no_overlap`: they share no dates. That is the 18 Oct state of both seams. It is recorded with a **continuity check**:
    - `continuous` (INFO) if the first date of the newer file is the next weekday after the older file's last date, and the
      one-day change across the seam is within the 99.9th percentile of absolute daily changes over the preceding 500 prints;
    - `seam_gap` (WARN) if weekdays are missing between the two files;
    - `seam_jump` (WARN) if the seam change is outside that percentile.
  - `seam_gap` or `overlap_disagree` inside a primary window triggers d5. `seam_jump` is a warning only.
  - `build` prints `ARCHIVE STALE: run fetch --archive` on a BoE `seam_gap`.

## 3. Method

**3.1 Weekly sampling (non-overlapping; Grok changes 1 and 3; gap rule amended in the second review).**
- **Weeks.** A week is an ISO week, Monday to Sunday. It is labelled `week_ending`, the Friday of that ISO week, even when the last
  print is earlier in the week.
- **Prints and changes.** For each series, take the last valid print dated inside the week. The change for week t is
  (print in t − print in t−1) × 100, in basis points.
- **Gap rule.** Drop a change only if the earlier print's ISO week is not the immediately preceding ISO week. Test it as "the two
  weeks' Mondays are exactly 7 days apart", which handles week 53 and the turn of the year.
  - A Golden-Week-type skip drops the change. In 2019 the JGB has no print in the week ending 3 May, so the change into the week
    ending 10 May is dropped.
  - A Thursday print followed by the next Friday's print is kept. Good Friday 2026 is one case: the Bund's last print that week
    is Thursday 2 Apr.
- Each daily print enters at most one change. Nothing is estimated on levels.
- **Listwise deletion.** A week enters a series set only if every series in the set has a valid change that week. The counts
  dropped are reported per window.
- **d2 budget, re-estimated under this rule.** Counting only which weeks have prints:
  - `w2018_19` loses 2 of 104 weeks (both JGB, Golden Week 2019);
  - `w2024_latest` loses 0 of 146.

  The old ">5 business days" rule would have lost 7 and 13 weeks, including the Good Friday and Juneteenth weeks, and would have
  broken checkpoint 8.4: it gave 26 weeks, not 30. The d2 budget is now 5% (4.1).

**3.2 Windows (pre-registered; week_ending inclusive; every end is capped at the latest common week).**

| Window | week_ending from | to | Calendar weeks at as-of 2026-10-18 | Role |
|---|---|---|---|---|
| `w2018_19` | 2018-01-05 | 2019-12-27 | 104 | **primary, baseline** |
| `w2020_21` | 2020-01-03 | 2021-12-31 | 105 (includes ISO 2020-W53, week ending 2021-01-01) | descriptive |
| `w2022_23` | 2022-01-07 | 2023-12-29 | 104 | descriptive |
| `w2024_latest` | 2024-01-05 | latest | 146 | **primary, comparison** |
| `w2024_25` | 2024-01-05 | 2025-12-26 | 104 | descriptive (the partner of `w2026_ytd`) |
| `w2026_ytd` | 2026-01-02 | latest | 42 | descriptive |
| `full` | 2018-01-05 | latest | 459 | descriptive |

**3.3 Series sets.**
- `nom4` = us_nom, bund_nom, gilt_nom, jgb_nom. This is the **only** set in the primary test.
- Descriptive sets:
  - `nom3_ex_jgb` (k = 3), used for interpretation;
  - `nom4_ecb`, with ea_aaa in place of bund_nom, robustness;
  - `nom4_usreal` (k = 5).
- `nom4_jgb_lead1`, robustness:
  - **The lead print.** For the week ending Friday F, the JGB value is the first JGB print dated after F. That is Monday, or
    Tuesday when Monday is a Japanese holiday, or the next print after that. It must fall within 4 business days of F; otherwise
    that week's JGB value is missing.
  - **Changes** are taken between consecutive weeks' lead values.
  - **End of sample.** The latest week enters this set only if its lead print is dated on or before the as-of date. So this set can
    end one week before `nom4`.
- **Singularity guard.** No set may hold a series that is a linear combination of other members. Assert that the smallest
  eigenvalue of every correlation matrix is above 1e-6.

**3.4 The statistic (Grok change 2; one pre-committed statistic).**
- R is the k×k Pearson correlation matrix of weekly changes on a window's listwise-complete weeks. `lambda1` is its largest
  eigenvalue, and `lambda1_share` = lambda1 / k.
- **The denominator is k**, the trace of R. Assert |trace − k| < 1e-8 and |Σ eigenvalues − k| < 1e-8.
- **Scale, one line:** the share is 0.25 for four unrelated series and 1.0 for four moving in lockstep.
- **Noise floor.** In a finite sample, unrelated series still show some correlation, so their share sits about **0.31 at n = 104**
  and **0.30 at n = 146**, not 0.25. Those are synthetic means over 4,000 draws of four independent t(5) series, with SD 0.019 and
  0.016.
- With all pairwise correlations equal to ρ, the share is (1 + (k−1)ρ)/k; for k = 4, a share of 0.55 means ρ = 0.40. The g4
  two-series figure, (1 + 0.76)/2 = 0.88, has denominator 2 and is not comparable.
- `rho_mean` is the mean of the k(k−1)/2 off-diagonal correlations. No covariance share is computed (Grok change 6).
- **Pre-registered descriptive row `jgb_mean_rho`.** This is the mean of the three JGB-to-others correlations (us, bund, gilt) in
  nom4. Its change from `w2018_19` to `w2024_latest` is reported with the same calibration as the primary (3.5), so a
  Japan-specific change is visible on its own.

**3.5 Intervals and calibration (replaces the earlier bare k_infl = 1.25).**
- **Block bootstrap.** Resample runs of consecutive weeks, not single weeks. Within a window, the rows are its listwise-complete
  weeks in time order. Draw ceil(n/b) block starts uniformly from 0..n−b, take b rows from each, and truncate to n.
  - b = 8 for the decision, with b = 4 and b = 12 as checks.
  - B = 2,000 draws, numpy `default_rng(20261018)`.
  - For a window difference, resample each window independently in every draw: Δ* = share*(to) − share*(from).
  - `boot_sd` is the SD of the B values of Δ*.
- **Historical placebo, the primary calibration.**
  - **What it is.** The same Δ, computed on pairs of windows laid out exactly like the primary pair, using history **before 2018
    only**. Each layout is a 104-week window, a 209-week gap (the gap between `w2018_19` and `w2024_latest`), then an n_C-week
    window, where n_C is the realised length of `w2024_latest` (146 at as-of 18 Oct). That is 459 weeks.
  - **Span.** The four series' common daily span starts with the Bund's daily data (1997-08-07). Layouts therefore lie within the
    weeks ending 1997-08-15 to 2017-12-29: 1,064 weeks.
  - **Layouts.** Starts are stepped by 13 weeks, which gives **47 layouts** at n_C = 146. They overlap heavily; only 2 are
    mutually disjoint. So `placebo_sd` is itself imprecise, and the README says so. The same gap rule, listwise rule and d2 budget
    apply to each layout. A layout that fails d2 is excluded and does not count.
  - **Spread.** `placebo_sd` is the root mean square of the placebo Δs about **zero**, not about their mean. History's real regime
    differences (1998, 2008, 2013, the 2016 cap on JGBs) therefore count as noise. That is deliberate: a SHIFT must exceed what
    history shows between windows this far apart.
  - **Used SD.** `boot_sd_used = max(boot_sd, placebo_sd)`, computed separately for each block length. Intervals are Δ ± z ×
    `boot_sd_used`, with z = 1.96 (95%) or 1.645 (90%), and no inflation factor.
  - **Other rows.** The same placebo procedure calibrates `jgb_mean_rho`, `nom3_ex_jgb` and the robustness rows. Descriptive
    window intervals use `boot_sd` alone, labelled descriptive.
- **Fallback, pre-registered now.**
  - **When it applies.** If fewer than **N = 20** placebo layouts survive (a source's history fails to load, or d2 excludes too
    many), the interval is Δ ± z × k_infl × `boot_sd`. `shift_test.csv` records which path was used.
  - **The value of k_infl.** It is the smallest value on the grid {1.0, 1.25, …, 4.0} that holds the false-SHIFT rate at or
    below 0.05 in every scenario of the grid:
    - ρ ∈ {0.3, 0.5};
    - factor-volatility persistence φ ∈ {0, 0.90, 0.97};
    - stationary log-volatility SD ∈ {0.3, 0.6};
    - t(5) shocks, with the 4.1 rule including d4.

    The spec author's run (400 replications per scenario, B = 300; 4.5) gives **k_infl = 3.0**. `mde` re-runs it with 1,000
    replications. If `mde` gives a larger value, the larger one is used. This is fixed before any real-data build and is never
    revised after one.

## 4. Decision rule (written 18 Oct 2026, before any real-data statistic for 2018 onward was computed)

### 4.1 The one primary test

Δ = `lambda1_share`(nom4, `w2024_latest`) − `lambda1_share`(nom4, `w2018_19`). It is two-sided, uses b = 8, and its intervals use
`boot_sd_used` (3.5).

| Verdict | Condition |
|---|---|
| **SHIFT** (comovement differed; the sign gives the direction) | the 95% interval excludes 0 **and** abs(Δ) ≥ 0.10 |
| **NO SHIFT AS LARGE AS 0.15** | the 90% interval lies entirely inside [−0.15, +0.15]. This is an equivalence test; 0.15 in the share is about 0.20 in average pairwise correlation |
| **INCONCLUSIVE** | neither condition holds; **or both hold (reason `overlap`)**; or any downgrade below |

**NO SHIFT AS LARGE AS 0.15 is reachable only if `boot_sd_used` < 0.091,** because 1.645 × 0.091 = 0.15. If the placebo spread is
wider than that, the only possible verdicts are SHIFT and INCONCLUSIVE, and the README says so.

**Downgrades to INCONCLUSIVE.** Each is named in `downgrade_reasons`:
- (d1) a primary series is stale (2.4);
- (d2) listwise deletion drops more than **5%** of calendar weeks in either window (more than 5 of 104, or more than 7 of 146);
- (d3) any nom4 series has weekly-change SD below 1.0bp in either window (the JGB was policy-capped in part of 2018–19);
- (d4) b = 4 or b = 12 gives a different verdict category from b = 8;
- (d5) `seam_gap` or `overlap_disagree` inside a primary window, or fewer used weeks than the floor (`w2018_19` 90, `w2024_latest`
  125).

### 4.2 Everything else is descriptive

Descriptive outputs carry intervals and no verdict, and the word "test" is not used for them. They are:
- the other windows, pairs and comparisons (`w2018_19→w2022_23`, `w2022_23→w2024_latest`, `w2024_25→w2026_ytd`);
- the full-sample share;
- `jgb_mean_rho`, `nom3_ex_jgb`, `nom4_usreal`.

**Robustness flag.** If `nom4_ecb` or `nom4_jgb_lead1` moves the primary Δ by 0.05 or more, the README says so beside the verdict.
The verdict itself does not change.

### 4.3 Interpretation rule (pre-written; descriptive)

- If the primary is SHIFT and the `nom3_ex_jgb` 90% interval lies inside ±0.15, the README says: "the change in the four-country
  share is carried by the JGB leg; the US, Bund and gilt share did not move by as much as 0.15."
- If both clear SHIFT's condition with the same sign, it says: "the change is not only Japan's."
- Otherwise it gives both numbers with no sentence.
- The `jgb_mean_rho` change is always printed beside them.
- Context, not evidence: the Bank of Japan capped the 10-year yield in part of the baseline. No code depends on its dates.

### 4.4 What a result does and does not license

- **SHIFT** licenses "the common share of weekly 10-year moves in these four markets was higher (or lower) in 2024–latest than in
  2018–19", graded MEASURED, with the interval and the calibration path.
- It does not license "global factors drove US yields", any statement about levels, any causal reading, or "the regime changed
  for good".
- **NO SHIFT AS LARGE AS 0.15** licenses exactly that sentence.
- **INCONCLUSIVE** is reported with its reason.

### 4.5 Minimum detectable effect (synthetic, 18 Oct, before any real-data run; reproduced by `mde`)

**Design.** Four series: x_i = √ρ · σ_t · f_t + √(1−ρ) · e_i, with f and e unit-variance t(5) shocks. log σ_t is AR(1) with
persistence φ and stationary SD `sdlog`; φ = 0 is a constant σ. There is no market data in the simulation.

**False-SHIFT rate at the null** (equal ρ in both windows; n = 104 and 146; the 4.1 rule with d4 and the 0.10 floor; 400
replications, so about ±0.011 at 0.05):

| Scenario | k = 1.0 | 1.5 | 2.0 | 2.5 | 3.0 | 4.0 |
|---|---|---|---|---|---|---|
| φ = 0, ρ 0.3 / 0.5 | 0.050 / 0.087 | 0.007 / 0.013 | 0 / 0.003 | 0 / 0.003 | 0 / 0 | 0 / 0 |
| φ 0.90, sdlog 0.6, ρ 0.3 / 0.5 | 0.255 / 0.210 | 0.102 / 0.080 | 0.040 / 0.035 | 0.005 / 0.010 | 0 / 0 | 0 / 0 |
| φ 0.97, sdlog 0.3, ρ 0.3 | 0.258 | 0.098 | 0.037 | 0.015 | 0.003 | 0 |
| φ 0.97, sdlog 0.6, ρ 0.3 / 0.5 | 0.472 / 0.450 | 0.250 / 0.265 | 0.142 / 0.158 | 0.072 / 0.090 | 0.037 / **0.048** | 0.018 / 0.007 |
| φ 0.99, sdlog 0.6 (outside the grid) | 0.573 / 0.552 | 0.370 / 0.388 | 0.242 / 0.268 | 0.160 / 0.175 | 0.102 / 0.107 | 0.045 / 0.050 |

The second reviewer, on its own design, found 0.13 / 0.33 / 0.48 at φ = 0.90 / 0.97 / 0.99 with k = 1. Both runs say the same
thing: **an uncalibrated block bootstrap reports regime differences as shifts.** That is why the placebo floor is primary, and why
the fallback k_infl is 3.0.

**Power (SHIFT rate, 300 replications):**

| True Δ | k = 1, φ = 0 | k = 1, φ 0.97 | k = 3, φ = 0 | k = 3, φ 0.97 |
|---|---|---|---|---|
| 0.15 | 0.62 | 0.64 | 0.01 | 0.09 |
| 0.25 | 0.97 | 0.74 | 0.14 | 0.22 |
| 0.35 | 1.00 | 0.92 | 0.74 | 0.51 |

**MDE.**
- On the placebo path, the MDE at 80% power is about 2.8 × `boot_sd_used`. That is about 0.17 if `boot_sd_used` is near 0.06 (the
  bootstrap alone, φ = 0), and 0.28 if it is 0.10.
- On the fallback path (k_infl = 3), the MDE is about 0.35 or more.
- `mde` passes every synthetic verdict through the same function as the build, including d1–d5. d1, d2, d3 and d5 receive
  synthetic inputs that cannot fire them, and one scenario each sets them, to confirm the downgrade.

**The test is weak on the likeliest change.** Suppose the US, Bund and gilt correlate among themselves at 0.5–0.7, and the JGB goes
from unrelated (0) to fully integrated (0.6). The four-country share then rises by **about 0.14–0.16**: 0.163 at block correlation
0.5, 0.150 at 0.6, 0.138 at 0.7 (exact eigenvalues). That is below the MDE even in the best case. The four-country share mostly
reflects the US–Bund–gilt block. A Japan-specific change shows up far more clearly in `jgb_mean_rho` (descriptive), which is why
that row is pre-registered.

## 5. Script

`bin/r15_yield_comovement.py`. It uses numpy and openpyxl (both in `requirements.txt`); everything else is stdlib. Modes:
- `fetch [--archive]`;
- `build`: offline, and byte-identical on re-run;
- `selftest`: synthetic, no network, under 30 s;
- `mde`: synthetic, prints the 4.5 tables and the fallback k_infl, under 15 minutes.

**Parsers.**
- **Treasury.** Select columns by name (`10 Yr`, `10 YR`). Dates are `MM/DD/YYYY`. Blank or `N/A` is missing.
- **Bundesbank.** Detect the format from the header: German (`Stand vom`, `;`, decimal comma; U3) or English (`last update`, `,`;
  the r3 cache). `.` is missing.
- **MoF.** The date is column 1 when it matches `YYYY/M/D`. `-` or blank is missing. Skip title, blank and footer lines. Decode as
  UTF-8 with `errors="replace"`.
- **BoE.** As in 2.2.
- **ECB.** `TIME_PERIOD`, `OBS_VALUE`.

**Pre-registered constants.** The script holds the block below as its single source for these values. `selftest` renders it from
the script's constants and compares its sha256 with the anchor printed here. When the spec file is present at its landed path, it
also hashes the block in the spec.

**The anchor.** It is the sha256 of the lines strictly between the two marker lines. Each line ends with `\n`, and the text is UTF-8:
`8ecbe5c0af92f9f7e43b2a407490900f5c9d4d17fe1173c9b12dd618c81fe097`.

```
R15-CONSTANTS-BEGIN
windows=w2018_19:2018-01-05:2019-12-27|w2020_21:2020-01-03:2021-12-31|w2022_23:2022-01-07:2023-12-29|w2024_latest:2024-01-05:latest|w2024_25:2024-01-05:2025-12-26|w2026_ytd:2026-01-02:latest|full:2018-01-05:latest
primary=nom4:w2018_19->w2024_latest:lambda1_share:two_sided
gap_rule=previous_print_iso_week_immediately_preceding(mondays_7_days_apart)
week_included_if=friday<=asof
block_len=8;block_checks=4,12;boot_draws=2000;seed=20261018
z95=1.96;z90=1.645;shift_floor=0.10;equivalence_margin=0.15;overlap=INCONCLUSIVE
placebo=span:1997-08-15..2017-12-29;layout:104+209+n_C;step_weeks:13;spread:rms_about_zero;min_layouts:20
boot_sd_used=max(boot_sd,placebo_sd)
fallback_k_infl_grid=1.0..4.0:0.25;fallback_k_infl_author=3.0;fallback_target_false_shift=0.05
fallback_scenarios=rho:0.3,0.5;phi:0,0.90,0.97;sdlog:0.3,0.6;shocks:t5
d1_stale_bdays=5;d2_max_drop=0.05;d3_min_sd_bp=1.0;d5_min_weeks=w2018_19:90,w2024_latest:125
robustness_flag_delta=0.05;robustness_sets=nom4_ecb,nom4_jgb_lead1
jgb_lead1=first_jgb_print_after_friday_within_4_bdays;last_week_requires_lead_print<=asof
R15-CONSTANTS-END
```

## 6. Outputs (all under `data/r15_yield_comovement/`; every CSV starts with the `# source:` line, then the header)

Shares, correlations and intervals are written to 3 decimals, SDs to 0.1bp.

**Leak guard.** No committed CSV has more than 80 data rows, and no committed column other than those named below holds dates.

- **`windows.csv`:** `window, series_set, k, asof, first_week, last_week, weeks_calendar, weeks_used, dropped_gap, dropped_missing,
  lambda1, lambda1_share, rho_mean, rho_min, rho_max, share_ci95_lo, share_ci95_hi, block_len, boot_draws, status`.
  `status` is one of `ok`, `stale_end`, `low_n`, `low_sd`, `seam_fail`.
- **`pairs.csv`:** `window, series_set, pair, n, rho, ci95_lo, ci95_hi`. Sets `nom4` and `nom4_usreal`.
- **`shift_test.csv`:** `comparison, role, statistic, series_set, window_from, window_to, value_from, value_to, delta, boot_sd,
  placebo_sd, placebo_layouts, boot_sd_used, calibration, inflation_k, ci95_lo, ci95_hi, ci90_lo, ci90_hi, block_len,
  boot_draws, verdict, downgrade_reasons`.
  - `statistic` is `lambda1_share` or `jgb_mean_rho`.
  - `calibration` is `placebo_floor` or `fallback_k`.
  - `role` is `primary` (exactly one row), `block_check` (b = 4 and 12), `interpretation` (`nom3_ex_jgb`, `jgb_mean_rho`),
    `robustness` (`nom4_ecb`, `nom4_jgb_lead1`) or `descriptive`.
  - `verdict` is filled only on primary and block_check rows, and reads `descriptive` elsewhere.
- **`series_stats.csv`:** `window, series, n_changes, sd_bp, dropped_gap, missing_weeks`.
- **`freshness.csv`:** `source, series, last_obs, asof, lag_bdays, max_lag_bdays, status, seam, seam_status`.
- **`checks.csv`:** `check_id, description, pin_date, expected, observed, status` (PASS, WARN, FAIL or INFO). It holds the pins
  (at most five per source, `pin_date` filled), the 3.4 identities, the seams, K20 and K30–K32.
- **`fetch_log.csv`:** `utc, host, path, status, bytes, sha256, note`.
- **`README.md`** must contain, in plain words:
  1. the verdict and the calibration path;
  2. the one-line scale (0.25 unrelated, 1.0 lockstep);
  3. the noise floor (about 0.31 at 104 weeks, 0.30 at 146);
  4. the denominators;
  5. "the verdict compares two realised regimes";
  6. "one share mostly reflects the US–Bund–gilt block; Japan's full integration (0 → 0.6) moves it about 0.14, below what this
     test can detect";
  7. a paragraph headed **"This test cannot detect small changes"**, giving the MDE and saying that a change below it will
     usually come back INCONCLUSIVE, which does not mean nothing changed;
  8. the "cannot say" list of section 0.
- **`SOURCES.md`:** sections 2.1–2.3 in brief, the licence lines, and "Source: Deutsche Bundesbank".

## 7. Selftest (synthetic fixtures; each guard must FAIL when its mutant is applied)

| Guard | What it asserts | Mutant that must make it fail |
|---|---|---|
| G1 non-overlap | Changes come from last-in-week prints; consecutive changes share no daily print | 5-day rolling changes on daily data |
| G2 changes, not levels | On four independent random walks, the nom4 share is in [0.20, 0.40] | estimator fed levels |
| G3 denominator | A population equicorrelation of 0.40 gives a share of 0.55 ± 1e-9; trace and eigenvalue sum = k | share = lambda1/2 (Grok's 0.88 error) |
| G4 correlation, not covariance | Multiplying one series by 100 leaves the share unchanged | covariance-matrix share |
| G5 gap rule (Good Friday fixture) | Treasury prints Fri 2026-04-03 and the Bund does not (Bund's last print is Thu 04-02): the Bund change into the week ending 04-10 is **kept**. Treasury is closed Fri 06-19 and Fri 07-03 while the Bund prints: both Treasury changes are **kept**. A fixture week with no print drops itself and the next change. 8.4 is reproduced: 30 weeks, +56/+25, 0.76/0.88/0.72 | the old ">5 business days" rule (it drops the Good Friday and Juneteenth changes, leaving 26 weeks) |
| G6 years | The fetch plan covers US 1997..current; the panel has weeks in 2020 and 2021 | g4's year list |
| G7 staleness | bund_nom 8 business days behind gives `stale_end` and INCONCLUSIVE (d1) | staleness check removed |
| G8 no breakeven / singularity | A set holding nominal, real and nominal−real is refused | `us_bei` added to `nom4_usreal` |
| G9 decimal comma | `2026-10-16;3,48;` parses to 3.48; `.` is missing | split on `,`, or `.` read as 0 |
| G10 BoE sheet and column | A synthetic xlsx with the 10-year column moved, a `2. fwd curve` sheet with different values, and a second file using `4. nominal spot curve`: both return the spot 10y | hard-coded index 20, reading `2. fwd curve`, or accepting only `4. spot curve` |
| G11 Treasury by name | 1990-, 2023- and 2026-style headers all give `10 Yr` | positional column |
| G12 missing markers | `.`, `-`, `N/A`, blank and an empty cell are missing, never 0 | any read as 0 |
| G13 seams | An overlap differing by 0.001pp is `overlap_disagree` (FAIL); no overlap with a next-weekday start is `no_overlap`+`continuous`; a missing weekday is `seam_gap` and triggers d5 | `no_overlap` reported as PASS, or the continuity check removed |
| G14 block bootstrap | Resampled indices form runs of exactly b (a truncated last run allowed); the same seed gives identical draws | i.i.d. resampling |
| G15 constants anchor | The rendered constants block hashes to the sha256 printed in section 5 (and to the landed spec's block when present) | any constant altered |
| G16 leak guard | No committed CSV has more than 80 rows or an unlisted date column | weekly panel written to `data/r15_yield_comovement/` |
| G17 allowlists | Each output header equals its allowlist exactly | an extra `us_nom_level` column |
| G18 fetch fence | Host allowlist; no `@` in the User-Agent; latch on non-200, on a redirect and on a failed content test; no latch on a socket fault; in-repo cache refused; at least 3 s pacing; at most 50 requests | each rule removed in turn |
| G19 listwise | A week with one series missing is absent from nom4, and present in a set without that series | pairwise deletion |
| G20 one primary | Exactly one `role=primary` row; descriptive rows read `verdict=descriptive` | a second primary row |
| G21 decision rule | Fixture (Δ, `boot_sd_used`) pairs map as in 4.1. That includes the 0.10 floor; **overlap** (Δ = 0.11, sd 0.02: both conditions hold, so INCONCLUSIVE with reason `overlap`); each of d1–d5; `boot_sd_used` = max(boot, placebo); and the fallback path below 20 layouts | the overlap branch removed, the 95% interval used for equivalence, or `boot_sd` used without the placebo floor |
| G22 week 53 / year turn | Prints on 2020-12-28..12-31 sit in ISO 2020-W53, labelled 2021-01-01, inside `w2020_21`. Its change from week ending 2020-12-25 and the change into week ending 2021-01-08 are both kept | ISO week numbers compared as integers (53 → 1 treated as a skip), or labels by calendar year |
| G23 partial week and lead1 end | With as-of Thursday 2026-10-15, the week ending 2026-10-16 is excluded and `weeks_calendar(w2024_latest)` = 145. A JGB lead print dated after the as-of date removes that week from `nom4_jgb_lead1` only | Friday ≤ as-of check removed |

## 8. Success criteria (run from the repository root)

1. `python3 bin/r15_yield_comovement.py selftest` prints `23/23 guards PASS` and that every mutant was caught.
2. `fetch --archive`, then `build`: at most 46 requests are logged, and no STOP is written. `build` run twice is byte-identical
   (`shasum` printed both times).
3. **Pins** (`checks.csv`, with `pin_date`; FAIL if off by more than 0.005pp, except BoE and Bundesbank, which are WARN with "may
   have revised"):
   - us_nom: 2023-12-29 3.88, 2026-01-02 4.19, 2026-07-31 4.75, 2026-09-18 5.01, 2026-10-16 5.09;
   - us_real: 2023-12-29 1.72, 2026-09-18 2.68, 2026-10-16 2.74;
   - bund_nom: 2018-01-02 0.50, 2023-12-29 2.06, 2026-01-02 2.96, 2026-07-31 3.21, 2026-10-16 3.48;
   - jgb_nom: 2018-01-04 0.052, 2023-12-29 0.647, 2026-09-30 3.057, 2026-10-13 3.019, 2026-10-15 2.948;
   - gilt_nom: 2018-01-02 1.3498, 2023-12-29 3.5803, 2026-07-31 5.1040, 2026-09-30 5.4028, 2026-10-15 5.3435;
   - ea_aaa: 2018-01-02 0.5376, 2026-10-01 3.5922.
4. **g4 re-derivation** (K30–K32), on weeks ending 2026-01-09..2026-07-31 under the 3.1 gap rule. The spec author reproduced all of
   it on 18 Oct from U1, U2 and U3:
   - 30 changes each for us_nom, us_real and bund_nom;
   - sums +56bp (us_nom), +53bp (us_real) and +25bp (bund_nom);
   - correlations us_nom–bund_nom 0.76, us_nom–us_real 0.88, us_real–bund_nom 0.72.

   A mismatch is FAIL.
5. **Week counts.** At as-of 2026-10-18, `windows.csv` has `weeks_calendar` = 104 (`w2018_19`), 104 (`w2022_23`) and 146
   (`w2024_latest`). `dropped_*` totals 2 for nom4 in `w2018_19` and 0 in `w2024_latest`; a different count is WARN, with the
   weeks listed. Every nom4 row has |trace − 4| < 1e-8.
6. **Placebo.** `shift_test.csv` shows `placebo_layouts` = 47 at n_C = 146 (fewer only if d2 excluded some, and those are listed
   in `checks.csv`), and `calibration = placebo_floor`.
7. **Verdict.** There is exactly one primary row. Its verdict follows mechanically from `delta`, `boot_sd_used`, the block_check
   rows and `downgrade_reasons` under 4.1; the verifier recomputes it.
8. **`mde`** prints the 4.5 tables. The fallback k_infl is ≥ 3.0. False-SHIFT ≤ 0.05 holds at that k in every grid scenario.
9. **Clean tree.** `git status --porcelain` shows no cache file. `bin/check.sh --all` prints the new warn-only guard (next free M
   number; M12 when written) clean. That guard flags tracked `glc*.zip`, `latest-yield-curve-data.zip`, `jgbcme*.csv` or
   `*BBSIS*` files, and any header in `data/r15_yield_comovement/` outside the allowlists.

## 9. Landing

- Commit `bin/r15_yield_comovement.py`, `data/r15_yield_comovement/` (section 6 only), the gate guard, and a REPRODUCE.md note.
- Add defensive `.gitignore` patterns for the raw names in 8.9.
- Add a MONTHLY `CALENDAR.tsv` row after the BoE archive refresh (about the 3rd business day): `selftest`, `fetch --archive`,
  `build`. If `fetch` prints STOP, do not retry or route around it; tell the principal.
- The supervisor writes any findings text after verification, including the E-021 item-15 row and any `data/series.tsv` rows.

## 10. Open questions

- **OPEN-1. Bund timing.** The 16 Oct value was published at 12:13 on 16 Oct, which suggests a midday price basis. *Settled by:*
  the Bundesbank's BBSIS methodology note. If the basis is midday, add a descriptive `nom4_bund_lead1`.
- **OPEN-2. Month seams.** It is not known what U5 and U7 hold in a month's first business days. The seam rule and the gap rule
  protect the build. *Settled by:* fetching U4–U7 on 2 and 3 Nov 2026 and recording each file's span.
- **OPEN-3. Compounding** of the Bund series. It does not matter for correlation shares; `SOURCES.md` should state it. *Settled by:*
  the series documentation.
- **OPEN-4. Placebo precision.** The 47 layouts overlap; only 2 are disjoint. `placebo_sd` could be dominated by one historical
  episode, such as 2008. *Settled by:* `build` writes the placebo Δ quantiles (min, median, max) to `checks.csv` as INFO. The
  supervisor reads them before reading the primary Δ.
- **OPEN-5. Licence reading.** Is Bundesbank's "must not be altered" compatible with publishing derived statistics under CC BY 4.0?
  This spec assumes yes for derived statistics and no for the series. *Settled by:* the principal's ruling, as for E-024 and E-025.
- **OPEN-6. MoF release time** ("9:30 the next business day") is relayed from Grok. It affects only the expected-lag note.
  *Settled by:* one request to the MoF Q&A page.

## 11. Where each supervisor ruling sits

| Ruling | Section |
|---|---|
| Sources current (Bundesbank to 16 Oct, BoE zip 200, MoF both files) | 2.2 U3–U7 |
| Licences: BoE cache-only; Bundesbank and MoF checked and recorded | 1 R1–R2, 2.3, OPEN-5 |
| Grok 1: non-overlapping weekly changes; no break test on levels | 3.1 (Bai–Perron dropped), G1, G2 |
| Grok 2: one pre-committed statistic, λ1/4 of nom4 | 3.4, 4.1–4.2, G20 |
| Grok 3: include 2020–21; gap rule | 2.2, 3.1 (amended, A1), 3.2, G5, G6, G22 |
| Grok 4: staleness per source | 2.4, d1, G7 |
| Grok 6: correlation shares only | 2.1, 3.4, G4 |
| Grok 7: no breakeven beside nominal and real | 2.1, 3.3, G8 |
| Grok 5 superseded: reading the UK 10y spot | 2.2 BoE layout, G10 |
| Pre-registered windows, shift size, block-bootstrap interval | 3.2, 3.5, 4.1, 4.5 |

## 12. Amendments, 18 Oct (second review)

- **A1. Gap rule (3.1, G5).** A change is dropped only if the earlier print's ISO week is not the immediately preceding one, tested
  as Mondays exactly 7 days apart. G5 now uses the Good Friday / Juneteenth / 3 July fixture. The old rule gave 26 weeks on
  checkpoint 8.4; the new one reproduces 30 weeks, +56/+25 and 0.76/0.88/0.72, verified on 18 Oct. The d2 budget was re-estimated
  from print availability (2 of 104 and 0 of 146 weeks lost) and cut from 10% to 5%.
- **A2. Partial final week (2.4, G23).** A week counts only if its Friday is on or before the as-of date. `weeks_calendar` depends
  on the as-of date, and `asof` was added to `windows.csv`.
- **A3. Calibration (3.5, 4.5).** The bare k_infl = 1.25 is gone.
  - Primary path: `boot_sd_used = max(boot_sd, placebo_sd)`, with `placebo_sd` the RMS about zero of Δ over 104+209+n_C layouts
    before 2018, stepped 13 weeks (47 layouts; spans per source in 2.1, with US 1990 and the BoE pre-2005 sheet name verified on
    18 Oct).
  - Fallback below N = 20 layouts: k_infl = 3.0, from a pre-registered grid that includes φ = 0.97 and sdlog 0.6. The false-SHIFT
    tables are added, the reviewer's figures are quoted, and the "two realised regimes" statement is in 0 and the README.
- **A4. Verdicts (4.1–4.5, G21).**
  - "NO MATERIAL SHIFT" is renamed "NO SHIFT AS LARGE AS 0.15".
  - Overlap (both conditions hold) is INCONCLUSIVE with reason `overlap`.
  - `mde` runs through d1–d5.
  - The README states that the share mostly reflects the US–Bund–gilt block and that Japan's full integration is Δ ≈ 0.14–0.16,
    below the MDE.
  - A descriptive `jgb_mean_rho` change row was added, with the same calibration.
- **A5. Time zone (2.1, 3.3, 4.2).** "Negligible" now applies only to unit conversion, and the JGB timing offset is explained.
  `nom4_jgb_lead1` (the next Tokyo close after Friday, so Tuesday when Monday is a holiday, within 4 business days) joins the
  robustness flag. An end-of-sample rule was added.
- **A6. Seams, ECB, anchor, pins (2.2, 2.4, 5, 6, G13, G15, G22).**
  - Seams record `no_overlap` with a continuity check, never PASS.
  - The ECB fetch starts at `startPeriod=2017-12-01`.
  - G15 checks the sha256 of the constants block printed in section 5.
  - `pin_date` was added to `checks.csv`, with at most five pins per source.
  - G22 is the week-53 / year-turn test (2020-12-28..2021-01-03).
  - The request cap is now 50, because US history from 1997 is needed for the placebo.
- **A7. README plainness (3.4, 6).** The README now carries the one-line scale, the noise floor (0.31 at n = 104, 0.30 at n = 146;
  synthetic, verified 18 Oct) and a "This test cannot detect small changes" paragraph.

## Builder decisions

Recorded by the builder (19 Oct session, 18 Oct as-of) where the spec is silent or ambiguous. None changes a pre-registered constant: the constants block still hashes to the anchor, and `build` refuses to run if it does not.

- **B1. U3 content test.** The spec says "the first line contains the series key, and the header holds `Stand vom`". The test is applied to the header block (the first 15 lines), because a false latch cannot be undone by the script and the first line's exact content was not observed before the fetch. The real file's first line does hold the key, so the stricter reading also passes.
- **B2. "At most five pins per source"** is read per series (us_nom 5, us_real 3, bund_nom 5, jgb_nom 5, gilt_nom 5, ea_aaa 2), as in 8.3. Treasury therefore has 8 pins across two series. ECB pins FAIL (not WARN) on a mismatch; only BoE and Bundesbank are WARN ("may have revised").
- **B3. `pairs.csv` size.** Seven windows times 6 nom4 pairs is 42 rows; the full 10 pairs of `nom4_usreal` would add 70 and break the 80-row leak guard. `nom4_usreal` therefore lists only the 4 pairs that involve `us_real` (28 rows); its other six pairs are the nom4 pairs on a slightly different listwise sample and are not repeated.
- **B4. Number formats.** Shares, correlations and intervals to 3 decimals (6.4 rule). The three SDs of a share (`boot_sd`, `placebo_sd`, `boot_sd_used`) to 4 decimals, because the 0.091 threshold for the equivalence verdict sits between 3-decimal steps; `sd_bp` to 0.1bp; `inflation_k` to 2 decimals.
- **B5. Intervals.** `boot_sd` is the sample SD (ddof 1) of the B bootstrap differences. Every interval is estimate plus or minus z times an SD (normal form), including `share_ci95_*` in `windows.csv` (one-window bootstrap SD, labelled descriptive by the column) and the pair correlations in `pairs.csv` (clipped to [-1, 1]). The bootstrap uses a fresh `default_rng(20261018)` per comparison and draws the "from" window first and the "to" window second, so the two windows are resampled independently; rows that share a pair share the index draws.
- **B6. Calibration of the descriptive comparisons.** A comparison other than the primary pair (`w2018_19->w2022_23`, `w2022_23->w2024_latest`, `w2024_25->w2026_ytd`) is calibrated by the same placebo procedure with a layout matched to its own geometry (window length, gap, window length), pre-2018 history only. `nom4_ecb` and `nom4_usreal` have no pre-2018 data (the ECB fetch starts 2017-12-01 by spec; TIPS from 2017), so every layout is excluded and they take the fallback path (`calibration = fallback_k`).
- **B7. Fallback multiplier.** `mde` (1,000 replications, B = 300, seed 20261018) gave k_infl = 3.25: at 3.0 the worst in-grid false-SHIFT rate was 0.052 (rho 0.5, phi 0.97, sdlog 0.6). Per 3.5 the larger value is used; it is the `build` default (`K_INFL_FROM_MDE`) and applies only to the rows that take the fallback path. The primary used the placebo path, so k_infl does not enter the verdict.
- **B8. Added modes and flags.** `calibrate` (offline, pre-2018 history only; reads only which weeks have prints after 2017 to size the n_C-week window) was added so the placebo could be read before any 2018-or-later statistic existed. `fetch --missing-only` skips files already cached (see B20).
- **B9. Weeks dropped.** For a set, a calendar week is `dropped_missing` if any series has no print that week, otherwise `dropped_gap` if any series has a print but none in the immediately preceding ISO week; so the two columns sum to calendar weeks minus used weeks. The series-level columns in `series_stats.csv` count the same way per series.
- **B10. `status` precedence in `windows.csv`:** `stale_end` (a window that ends at "latest", including `full`, when any nom4 series is stale), then `seam_fail`, `low_n` (fewer than 20 usable weeks, a d2 breach, or below the d5 floor where one exists), `low_sd` (a series in the set with weekly SD under 1.0bp, or fewer than 3 changes), else `ok`. The d1 to d5 flags for the primary use only the two primary windows.
- **B11. Seams.** First and last "row dates" of each file define the seam (BoE rows exist for every weekday, with an empty cell on a UK holiday; MoF rows exist for business days only, so a Japanese holiday at a month start would show as `seam_gap`, as the spec's rule says). A seam is "inside a primary window" if its first newer date lies from six days before the window's first Friday to its last Friday. Where files overlap, the newer file wins on shared dates.
- **B12. Primary rows.** `block_check` rows carry the base 4.1 category at that block length (their own `downgrade_reasons` is `overlap` or `none`); the d4 flag is computed from the three categories and applies to the primary row only. `downgrade_reasons` is `none` when nothing fired, including when the verdict is INCONCLUSIVE because neither condition holds.
- **B13. G1 wording.** "Consecutive changes share no daily print" is implemented as: each daily print ends at most one change, every change ends on the last print of its ISO week, and the spans (start, end] of consecutive changes do not overlap (a print is the end of one change and the start of the next, which is what a non-overlapping weekly difference is).
- **B14. G5 fixture.** Synthetic weekly changes are engineered so the 30 weeks 2026-01-09..2026-07-31 reproduce +56/+53/+25bp and 0.76/0.88/0.72 exactly; the missing days are Bund Fri 2026-04-03 and Fri 2026-05-01, Treasury Fri 2026-06-19 and Fri 2026-07-03. The superseded ">5 business days" rule then gives 26 weeks (four changes dropped), as the spec records.
- **B15. Leak guard.** A column "holds dates" if at least half its non-empty cells are pure dates; free text that mentions a date (the weeks listed in a WARN, the placebo start weeks) is not a date column. The committed `fetch_log.csv` is the latest row per URL (46 rows); the cache keeps every request.
- **B16. README.** `data/r15_yield_comovement/README.md` is generated by `build` from the build's own numbers (byte-identical on re-run). `SOURCES.md` is hand-written.
- **B17. Mutants.** Production code carries named hooks; a mutant is a hook switched on. G9 has two mutants, G12 four (".", "-", "N/A", blank), G18 eleven (each fence rule removed in turn, plus the content test itself), G21 three, G22 two ("ISO week numbers as integers" and "week keyed by calendar year"), G23 two. In total 48 mutants against 25 guards (the 23 of section 7 plus G24 and G25, B21).
- **B18. `mde` details.** Power uses base rho 0.3 and raises the later window's rho so the population share rises by the stated true change; scenarios phi = 0 and phi = 0.97 (sdlog 0.6). The two phi = 0.99 rows are printed but excluded from the k_infl rule (outside the grid).
- **B19. Other edits.** `Accept: */*` is sent beside the neutral User-Agent. `.gitignore`, a REPRODUCE.md paragraph, M12 in `bin/check.sh` (second, independent copy of the header allowlists) and a monthly CALENDAR.tsv row (due 2026-11-03) were added per section 9. No findings text, E-021 row or `data/series.tsv` row was written.
- **B20. Incident.** While testing a flag, the builder started a full `fetch --archive` against a scratch cache by mistake (34 of 46 requests, all 200, no STOP) and stopped it. Because the cache had no repository path and the requests were within the allowlist, the directory was moved to `~/r15_yield_cache/` and the fetch resumed with `--missing-only` for the remaining 12 requests, so the log holds exactly 46 requests and no URL was requested twice.
- **B21. Supervisor's review fixes (18 Oct).** G24 asserts the placebo spread is the RMS about zero (mutant: SD about the mean; on the real layouts it would be 0.0462, not 0.0690). G16 now asserts the literal row limit 80 and a literal copy of the section 6 allowlists (mutants `max_rows_800` and `allow_extra`), and plants an 81-row CSV. G25 asserts a build refused by the leak guard leaves nothing in the output folder: `build` now stages the outputs in a sibling directory, runs the guard there, and only then moves the files in (mutant `leave_leak`). Success criterion 1 therefore reads `25/25 guards PASS`. The README was rewritten per the review: terms defined, 102 of 104 weeks explained, the placebo changes' sign noted, and the Japan scenario replaced by what the data show.
