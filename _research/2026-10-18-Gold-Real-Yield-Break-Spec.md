# Spec: gold against the US 10-year real yield, with HAC errors and a break date (spec author, 18 Oct 2026)

*E-021 build queue item 5 (`2026-10-12-E021-Where-The-Money-Comes-From-Rates-FX-Commodities.md`, "Builds, in order"). The earlier
design is Grok batch g4, Item 9, in `_research/2026-10-14-Grok-G4-Returns.md`. Grok's attack on it is batch g7 return 3. The
supervisor's rulings of 18 Oct on that attack outrank Grok wherever the two differ, and this spec follows the rulings. House style:
`_research/2026-10-15-ICE-Brent-COT-Spec.md`. The fetch and latch code to copy is `bin/pull_ice_brent_cot.py`; `bin/pull_series.py` (`_ddp`)
shows how the Fed Data Download Program is read.*

## 0. Goal, and what the result can and cannot say

- **Question.** Over 2006-2026, do gold's monthly moves run against moves in the US 10-year real yield, once the dollar is held
  fixed? And did that link change at one datable point?
- **Why now.** E-021 says gold's real-yield sensitivity "collapsed in 2024-25 and came back in 2026". It is labelled HYPOTHESIS, and
  so far it rests on windows of 7 to 9 observations. This build gives the long-sample estimate, its band, and a break test.
- **The result can say:** "In months when the 10y real yield rose 1 percentage point (pp) more, gold's monthly average price was
  about X% lower, holding the broad dollar fixed, with band [a, b]", and whether one coefficient break was found, when, and how
  sure the date is.
- **The result cannot say:** that real yields cause gold moves. Both respond to the same news, so this is a same-month association.
  It is not a forecast. It says nothing about daily or weekly horizons. It cannot place a break in 2026, because no trim can
  estimate one there (§3.5). And official gold buying is not in the regression, so the result neither shows nor rules out that
  buying explains anything.
- **A temporary two-year change in sensitivity is not tested by any confirmatory object.** P1 is the one confirmatory test (A1); the
  break scan B1 is descriptive.

## 1. Hard requirements

**R1. Licence: the gold price never enters the repository.** The World Bank's reuse terms for the Pink Sheet gold row are unclear.
The remainder terms of the Bank's dataset terms apply, and the workbook's own Description sheet names Bloomberg Finance L.P. and
Thomson Reuters Datastream among the gold sources. So:
- The workbook lives in a local cache outside the repository: default `~/gold_ry_cache/`, overridable with `--cache`. The script
  refuses any cache path inside the repository.
- No committed file (CSV, SVG, README, checks, script source, tests) may carry a gold price, log gold, a gold change, a fitted
  value, a per-month residual or a residual in sd units. Any one of those, together with the committed coefficients and the yield
  and dollar columns, gives back the gold series exactly.
- **Per-month values are not wholly absent, and the spec does not claim they are** (A3). The 213 rolling 36-month slopes at 4 dp,
  together with the coefficients and `monthly_inputs.csv`, rebuild monthly gold changes with correlation 0.83-0.95 (second
  reviewer's simulation). So the rolling slopes and bands are published at **2 dp**, which brings the correlation down to about
  0.35. They are the one named per-month exception (K08).
- What may be committed: coefficients, standard errors, intervals and test statistics, with the World Bank cited (ruled 18 Oct:
  these are not a copy of the data). Also break dates, the three-way residual label (§3.4), the 2-dp rolling table, and a sha256
  of the gold column.
- Local-only outputs (the monthly panel with gold, and the residual path) go to `<cache>/local_outputs/`.
- **What R1 is for.** Public GLD data already approximates the Pink Sheet series: the second reviewer measured a median monthly gap
  of 0.034% before 2025-06. So R1 is about the Bank's redistribution terms, not about secrecy. The README says this in those words.

**R2. Free public data only (E-005); FRED is not used.** FRED refuses scripts. The sources are the World Bank, Treasury
(home.treasury.gov) and the Federal Reserve Board's Data Download Program (DDP). Nothing else is fetched.

**R3. Fetches are polite and stop on refusal.**
- Host allowlist: `thedocs.worldbank.org`, `home.treasury.gov`, `www.federalreserve.gov`.
- Every request carries the CLAUDE.md non-SEC User-Agent, exactly
  `Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)`. Assert there is no `@` in it.
- GET only. No redirect is followed.
- Requests are sequential, at least 5 s apart, at most 12 per run. A full fetch needs 8 (§2).
- **STOP latch** at the fixed path `~/gold_ry_cache/STOP`, whatever `--cache` says. HTTP 401, 403 or 429, any 3xx, or a body that
  fails its content test (§2) writes the latch. While the latch exists nothing is fetched, and only a person deletes it.
- A 5xx or a socket fault ends the run without latching. It is logged, and nothing retries.
- `data/gold_real_yield/fetch_log.csv` records every request: `utc, host, path, status, bytes, sha256, outcome`.

**R4. Vintages.** Each fetched file is saved under `<cache>/vintages/<source>/` with its retrieval date and the first 8 hex digits
of its sha256 in the file name. The World Bank and Fed files are overwritten at their URLs, so a dated copy is the only way to
re-verify later.
- `vintages.csv` records, per file: the source, the published `Updated on` line (World Bank), the last observation, the sha256 and
  the bytes.
- When a newer vintage of the same file arrives, the build prints the largest revision over the months the two vintages share,
  per series. A revision above 0.5% (gold) or 0.0005 index points (dollar) prints WARN.

**R5. Official flows stay out.** The script never reads `data/gold/ledger_monthly.csv` or any tonnes series. A stock or a flow is
never written as the cause of a price.

**R6. One confirmatory test (P1), and everything else descriptive, B1 included (A1).** The registry of estimated objects is
fixed (§3.7). An object id outside it is a hard failure, which stops forking paths from being added quietly.

**R7. Dependencies:** standard library, `numpy` and `openpyxl`, all in requirements.txt. `statsmodels` is not in requirements and is
not required. Every estimator is written by hand and pinned by the selftest (§7).

## 2. Data (each URL checked by the spec author with ONE request, neutral User-Agent, 18 Oct 2026)

| # | Source | URL | Seen on 18 Oct |
|---|---|---|---|
| D1 | World Bank Pink Sheet monthly workbook | `https://thedocs.worldbank.org/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx` | 200, 586,099 bytes, xlsx; sha256 `ea1c350827878ea3bbe30e3cda16a13fd3bd5b409b8458940dc94a36b5a33154`; `Updated on October 02, 2026` |
| D2 | Treasury par real yield curve, 2003-2023 archive | `https://home.treasury.gov/system/files/276/par-real-yield-curve-rates-2003-2023.csv` | 200, 171,806 bytes, text/csv; 5,254 data rows (the file has no trailing newline, so `wc -l` shows 5,254 lines including the header), newest first, two-digit years (`12/29/23`) |
| D3 | Treasury par real yield curve, one file per year (2024, 2025, 2026) | `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{YYYY}/all?type=daily_treasury_real_yield_curve&field_tdr_date_value={YYYY}&page&_format=csv` | 200 for each year; 250, 249 and 199 data rows (2026 through 10/16/2026; no trailing newline); four-digit years; quoted header |
| D4 | Treasury MC-versus-HS overlap file | `https://home.treasury.gov/system/files/221/fy2021-mc-vs-hs-combined.csv` | 200, 47,599 bytes; 251 days, 2020-10-01 to 2021-09-30; columns `real_hs_cmt_10yr`, `real_mc_cmt_10yr` |
| D5 | Fed DDP, G.5 monthly indexes package | `https://www.federalreserve.gov/datadownload/Output.aspx?rel=H10&series=847be2166a425bda9b4d92465f797544&lastobs=&from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package` | 200, 9,099 bytes; series `H10/H10/JRXWTFB_N.M`, 2006-01 to 2026-09 |
| D6 | Fed DDP, H.10 daily indexes package (check only) | same as D5 with `series=122e3bcb627e8e53f1bf72a1a09cfb81` | 200, 201,840 bytes; `JRXWTFB_N.B`, 2006-01-02 to 2026-10-09, 212 `ND` days |

Pages read once each to settle the rules below: the Treasury real-yield TextView page for 2026 (the series-break footnotes), the
Treasury "Yield Curve Methodology Change Information Sheet" (which links D4), and the DDP `Choose.aspx?rel=H10` page (the package ids).

**D1, gold.**
- Location: sheet `Monthly Prices`. The column whose row-5 header is `Gold`, with units `($/troy oz)` in row 6. Months are written
  `YYYYMmm`. Values are integers for 2006-2026.
- Definition, from the `Description` sheet: "spot average of daily rates, from June 2025; previously (UK), 99.5% fine, London
  afternoon fixing, average of daily rates". **So the series changes definition inside the sample, at 2025-06** (§3.2).
- Release timing: early in the following month (September 2026 appeared on 2 Oct).
- Content test: the body is a zip (`PK\x03\x04`), the sheet and header exist, and the units cell matches.
- The `Mismatch Details` sheet lists cells revised since the previous upload. On this vintage it lists no gold row.

**D2-D3, real yield.**
- Field: `10 YR`, the 10-year Real Constant Maturity Treasury rate (R-CMT), in percent.
- Two method breaks, both from Treasury's footnotes:
  - From 12/01/2008 the TIPS curve uses the most recently auctioned TIPS as knot points. The 2 Sep-28 Nov 2008 prints use the old
    method and "remain official".
  - On 12/6/2021 Treasury switched from the quasi-cubic Hermite spline (HS) to a monotone convex spline (MC). Prints made under HS
    "remain official".
- The daily file has values for every day from 2003-01-02. No 10 YR cell was blank, and no date appeared twice across the four files.
- Content test: the fields parse with `csv`, and `Date` and `10 YR` are present. The header is quoted in D3 and unquoted in D2.

**D4, size of the 2021 seam.**
- Over Treasury's 251 overlap days, mean(`real_mc_cmt_10yr` − `real_hs_cmt_10yr`) = **+0.026614 pp** (sd 1.03 bp, range 0.0 to 5.0
  bp).
- The information sheet reports the same gap with the opposite sign: "−2.7 to −0.6 basis points" across the R-CMT points. So
  Treasury's convention is HS minus MC.
- No overlap file was found for the 2008 knot change (OPEN-1).

**D5-D6, dollar.**
- Series: the nominal broad dollar index, monthly, `JRXWTFB_N.M`. It equals 100.0000 in 2006-01.
- **The DDP header's `Unit:` cell says `Index:_1997_Jan_100`, but the values are based January 2006 = 100.** The build asserts the
  value and ignores the label.
- On 18 Oct, each monthly value equalled the mean of that month's non-`ND` daily values (D6) within 0.0001, in all 249 months.
- The release is the first business day of the following month (1 Oct 2026 for September).
- Content test: the `Unique Identifier:` row contains `H10/H10/JRXWTFB_N.M` (D5) or `H10/H10/JRXWTFB_N.B` (D6).

**Licence handling.**
- **D1:** cached locally only (R1).
- **D2-D4:** Treasury data is US government work (ruled 18 Oct), so committing the monthly averages is fine, with the source cited.
  The raw daily CSVs stay in the cache because the repository does not need them (the `swap_tape_ledger.py` precedent).
- **D5-D6:** the Fed's disclaimer page puts Board website information in the public domain, with citation. This is relayed by Grok
  (g7 return 3) and was not re-read here. Monthly values are committed, cited, and the raw packages stay in the cache.

**Sample, pre-registered.**
- Levels: **2006-01 to 2026-09** (T = 249). Changes: **2006-02 to 2026-09** (n = 248).
- The end month is fixed at 2026-09 whatever vintage is fetched later. Later months are re-runs, labelled as updates, and the
  verdict below is taken on 2026-09.
- Why 2006 and not 2003:
  - The regression holds the dollar fixed, and the broad index on the DDP starts in 2006-01 (first row seen).
  - A 2003 start means either dropping the dollar or splicing a discontinued index. Dropping the dollar biases the yield slope,
    because Δ real yield and Δ log dollar correlate +0.39 over 2006-2026 (regressor-only moment, §3.6). A spliced index is on
    another methodology and is not on the DDP.
  - The cost of starting in 2006: 36 fewer months (the standard error rises by about 7%), and the 2008-12 knot change falls before
    the 15% trim window. A known-date Chow test covers that date (D7 in §3.7), and a 2003-2026 run without the dollar is kept as a
    descriptive row.

## 3. Method

**3.1 Monthly variables.** For each month t:
- `g_t` = ln(Pink Sheet gold, $/troy oz).
- `r_t` = the business-day mean of the daily `10 YR` prints in the calendar month, in percent, **on the MC basis**. Every daily print
  dated before 2021-12-06 has +0.026614 pp added (the D4 mean, computed by the build from D4 itself, never typed in). Prints from
  2021-12-06 on are unchanged.
- `u_t` = ln(`JRXWTFB_N.M`).
- Changes are month on month: Δg, Δr, Δu.

All three series are averages of daily figures, so they are on the same basis. Averaging adds positive first-order autocorrelation
to the changes (the Working effect), which is one reason the HAC lag is long. There is no month-end variant: it was in the earlier
design, and dropping it removes one fork.

**3.2 Seams.**
- **2021-12-06.** Handled in the data, by the D4 adjustment. The constant shifts every pre-seam level equally, so it touches the
  changes only in 2021-12 (19 of the month's 22 days are MC) and 2022-01. Robustness rows: unadjusted official prints (D3 in §3.7),
  and impulse dummies (D4 in §3.7).
- **2008-12-01.** No overlap file, so it cannot be adjusted. It is covered by the descriptive Chow test and an impulse dummy in D4.
  This month is also the height of the 2008 crisis, so a method effect and a market effect cannot be told apart there.
- **Gold 2025-06.** The definition changes from the average of the London afternoon fixing to a spot average. No overlap exists in
  D1. A descriptive local cross-check against the GLD-implied LBMA PM price is in §6, and an impulse dummy is in D4.

**3.3 Primary test (P1).**
- Regression: OLS of Δg_t = a + b·Δr_t + c·Δu_t + e_t over 2006-02 to 2026-09 (n = 248).
- Newey-West HAC variance with the Bartlett kernel:
  - V = (X'X)⁻¹ S (X'X)⁻¹, with S = Γ₀ + Σ_{l=1..L} (1 − l/(L+1))(Γ_l + Γ_l′) and Γ_l = Σ_{t>l} x_t e_t e_{t−l} x_{t−l}′.
  - No degrees-of-freedom correction.
- **Lag:** L = max(12, floor(4·(n/100)^(2/9))). At n = 248 the rule of thumb gives 4, so L = 12. Both numbers are printed side by
  side.
- Units: b is in log points of gold per pp of real yield. Print 100·b (the approximate %) and 100·(e^b − 1) (the exact %); for
  example b = −0.202 gives −18.3%, not −20.2%. c is an elasticity: % gold per 1% dollar.
- **Critical value (A1): fixed-b**, the Kiefer-Vogelsang asymptotics for the Bartlett kernel with b = L/n = 12/248 = 0.0484. Test at
  α = 0.05, two-sided, with **cv = 2.105**:
  - The Kiefer-Vogelsang (2005) cubic for the Bartlett 97.5% quantile, cv(b) = 1.96 + 2.9694b + 0.4160b² − 0.5324b³, gives 2.1046. The
    spec author recalled these coefficients and did not re-read them.
  - The spec author's simulation of the fixed-b limit agrees: 2.104 (location model, N = 2,000, L = 97, 20,000 draws,
    `numpy.random.RandomState(20261018)`).
  - The build computes the cubic and prints the value. G4 checks it against a seeded simulation, within 0.02.
- The decision interval is b̂ ± 2.105·se_HAC (95%, fixed-b). The normal-z interval is not printed, so it cannot be mistaken for the
  precision statement.
- **Finite-sample size, checked by the spec author.** This used synthetic noise y only, with the real Δr and Δu, n = 248, L = 12,
  20,000 draws, RandomState(20261018). The rejection rate at cv 2.105 was 5.8% (iid y) and 6.1% (AR(0.2) y). At z = 1.96 it was 7.6%
  and 7.8%. The finite-sample 5% critical value with this X and iid y was 2.187. G28 and K09 hold the build to at most 6.5%.
- Classical standard errors are printed too, labelled "not the precision statement".

**3.4 Levels, only after cointegration (descriptive).**
- **Engle-Granger test (A4).**
  - **The gate is run on the fit sample, 2006-01 to 2021-11 (T = 191).** OLS of g_t on (1, r_t, u_t) over that sample. The same test
    over 2006-01 to 2026-09 (T = 249) is reported as INFO only, and never gates anything.
  - ADF regression on the residuals, with no constant: Δẑ_t = ρẑ_{t−1} + Σ_{j=1..p} φ_j Δẑ_{t−j}.
  - p is chosen by AIC over 0 to 12, on a common sample that starts at lag 12. Then the regression is re-run at that p on the
    longest sample.
  - Critical value: MacKinnon (2010, Queen's QED WP 1227, Table 2), τc, N = 3, 5%:
    C(T) = −3.74066 − 8.5631/T − 10.852/T² + 27.982/T³, where T is the number of observations in the cointegrating regression.
    That gives **−3.7858 at T = 191** (the gate) and −3.7752 at T = 249 (INFO).
  - The trend variant adds t to the regression and uses Table 3, τct, N = 3, 5%:
    −4.11890 − 11.8922/T − 19.031/T² + 77.332/T³. That gives −4.1817 at T = 191 and −4.1670 at T = 249.
  - Coefficients read from the PDF by the spec author on 18 Oct.
- **If and only if the τc statistic is below its critical value**, the build reports (descriptive):
  - the levels slopes, without and with a linear trend, with HAC intervals at lag 12, labelled "OLS on a cointegrating regression;
    the HAC interval is indicative only";
  - a full-sample fit with a step dummy 1{t ≥ 2021-12}, and the dummy's coefficient with a HAC interval;
  - the **same-month residual** from a fit over 2006-01 to 2021-11. Only its in-sample sd and a three-way `residual_label` are
    committed (A3). The label is `high` (2026-09 residual above +2 in-sample sd), `not_high` (absolute residual below 1 sd), or
    `inconclusive`. No residual number in sd units is committed. The per-month path goes to `<cache>/local_outputs/` only (R1).
- Otherwise every levels row says `suppressed_no_cointegration` with empty number cells, and no levels number is printed anywhere.

**3.5 Break scan (B1, DESCRIPTIVE since the second review; A1).**
- Model: the P1 regression, with all three coefficients allowed to change after month k (k is the last month of regime 1; q = 3).
- Statistic: the HAC Wald test of the three shift coefficients, computed on the unrestricted model at lag L = 12. Take the sup over
  candidate k (Andrews sup-F, on the Wald scale).
- Trims π₀ ∈ {0.05, 0.15, 0.25}. Candidates run from k = ⌈π₀·n⌉ to ⌊(1 − π₀)·n⌋ on the change sample. At n = 248 that is:

  | trim | candidate k (last month of regime 1) |
  |---|---|
  | 0.05 | 2007-02 to 2025-08 |
  | 0.15 | 2009-03 to 2023-07 (the pre-registered trim) |
  | 0.25 | 2011-03 to 2021-07 |

- The build prints this table and this sentence, verbatim, in `break.csv`'s README section and on stdout: "No trim can return a
  2026 break date: the latest candidate under any trim is 2025-08. A 2026 change in sensitivity is not testable as a break date on
  this sample."
- **Why B1 is not confirmatory.** On pure-noise y with the real Δr and Δu, the second reviewer found that the HAC (L = 12) sup-Wald
  against the asymptotic critical values rejects 41% of the time (iid y) and 46.5% (AR(0.2) y), at a nominal 5%. With the classical
  covariance it rejected 5.2%, so the code is sound and the HAC Wald is the problem.
- **p-value (the one printed as `p_value_boot`):** a stationary bootstrap (Politis-Romano):
  - B = 999 draws, X held fixed, geometric blocks with mean length 6, applied to the restricted (no-break) P1 residuals;
  - y* = Xβ̂ + e*, then the same HAC (L = 12), trim and candidate set;
  - p = (1 + #{sup* ≥ sup})/(B + 1), using RandomState(20261018).
- **Asymptotic table, printed beside it and never used for any label:** Andrews (2003, Econometrica 71(1):395-397, Table I), sup
  Wald. The spec author read it from a copy attached on the gretl users list, so check it against the DOI version.

  | | trim 0.05 | trim 0.15 | trim 0.25 |
  |---|---|---|---|
  | q = 1, 10/5/1% | 8.13 / 9.71 / 13.17 | 7.12 / 8.68 / 12.16 | 6.35 / 7.87 / 11.28 |
  | q = 3, 10/5/1% | 13.46 / 15.36 / 19.28 | 12.28 / 14.13 / 18.07 | 11.32 / 13.18 / 17.13 |

  The chi-square reference is never used for a searched date.
- **What the half-width implies (replaces the old SUPPORTS branch).**
  - For a shift in the slope only, δ = (0, s, 0), Bai's half-width is h = 11.03·Ω̂₂₂/(s²·Q̂₂₂²). So the smallest slope shift that a
    half-width h can date is s_min(h) = √(11.03·Ω̂₂₂/(h·Q̂₂₂²)), where Q̂₂₂ is the mean of Δr² and Ω̂₂₂ is the (2,2) element of the NW
    long-run variance of x_t ê_t.
  - `break.csv` prints s_min for h = 4, 6, 8, 12 and 18 months.
  - On the spec author's moment bound (σ̂² ≤ var Δg = 0.0390², Q̂₂₂ ≈ 0.1813², iid), h ≤ 8 months (an interval no wider than about
    17 months) needs a slope shift of about **0.25 log points per pp or more**.
  - A wide Bai interval therefore means the shift was too small to date. It does not mean nothing changed.
- If `ci_clipped`, every width and s_min statement uses the **unclipped** interval [k̂ − ⌈h⌉, k̂ + ⌈h⌉].
- **Break date:**
  - k̂ = the argmin of total SSR over the candidates (Bai's estimator). The sup-Wald argmax is printed beside it; if the two differ,
    both are kept.
- **Bai (1997) 95% interval:**
  - With δ̂ the 3-vector of shifts, Q̂ = X'X/n and Ω̂ the NW long-run variance of x_t ê_t (lag 12, broken-model residuals), the
    half-width is h = 11.03 · (δ̂′Ω̂δ̂)/(δ̂′Q̂δ̂)² months.
  - The interval is [k̂ − ⌈h⌉, k̂ + ⌈h⌉], clipped to the sample for display. Clipping is flagged, and widths use the unclipped bounds.
  - 11.03 is the anchor P(|ξ| ≤ 11.03) ≈ 0.95 of the argmax of W(s) − |s|/2.
  - This is the homogeneous-case interval: the regime residual variances are printed, and the interval is labelled approximate if
    they differ by more than 2×.
- **Dummy variant:** B1 is re-run with a non-breaking impulse dummy for 2021-12 (Grok change 7), at all three trims.

**3.6 Power, before any data is run (CLAUDE.md, C-090).**
- To size the test, the spec author computed only these marginal and regressor-only moments over 2006-02 to 2026-09:
  - sd(Δg) = 0.0390;
  - sd(Δr) = 0.1813 pp;
  - corr(Δr, Δu) = 0.388.
  No gold-yield or gold-dollar moment, and no regression, was computed.
- A conservative classical standard error, taking σ_e ≤ sd(Δg), is se(b) ≈ 0.0390 / (0.1813 · √(1 − 0.388²) · √248) = 0.0148. With a
  HAC inflation of 1.3 it is 0.0193.
- At the fixed-b 5% critical value with 80% power ((2.105 + 0.84) se = 2.945 se), the **minimum detectable effect is 0.044 to 0.057
  log points per pp**.
- The materiality line used below, **0.050 log points per pp (about 4.9%)**, therefore sits at the edge of what this sample can
  detect. It is below Torul's daily-change estimate of −7.8% per pp, which Grok relayed and which was not re-read here.
- The build prints the realised MDE (2.945 × se_HAC).
- **B1 cannot detect a slope break below about 0.17 per pp; an absent break is not evidence about the 2024-26 hypothesis.**

**3.7 Registry of estimated objects (fixed; R6).**
- **Confirmatory: `P1` only**, at α = 0.05 with the fixed-b critical value (§3.3). Since there is one test, no multiplicity
  correction applies.
- **Descriptive, labelled as such in every output:**
  - `B1`: the sup-Wald break scan at trims 0.05, 0.15 and 0.25, with and without the 2021-12 impulse dummy (§3.5).
  - `D1`: P1 without the dollar.
  - `D2`: 2003-02 to 2026-09 without the dollar (the longer TIPS sample).
  - `D3`: P1 on unadjusted official yields.
  - `D4`: P1 with impulse dummies for 2008-12, 2021-12, 2022-01 and 2025-06.
  - `D5`: P1 over three sub-periods: 2006-02 to 2021-11, 2021-12 to 2023-12, and 2024-01 to 2026-09.
    - Windows with n < 100 use the rule-of-thumb lag and are flagged `short_window`.
    - These periods were chosen after the rise had been seen, so they confirm nothing.
  - `D6`: rolling 36-month slopes.
    - Moving-block bootstrap of the (Δg, Δr, Δu) rows, block length **6 months**, B = 999, seed 20261018, percentile 2.5/97.5.
    - Window end months run from 2009-01 to 2026-09.
    - Published as a plot plus the slope table. **No window is counted**, for example how many intervals exclude zero.
  - `D7`: HAC Chow tests at known dates, with regime 2 starting 2008-12 and 2021-12 (q = 3, chi-square(3), since the date is fixed).
    - These are descriptive: 2021-12 was chosen after the post-2021 rise had been seen, and 2008-12 coincides with the crisis.
  - `D8`: the levels objects of §3.4, conditional on cointegration.
  - `D9`: checksums. These are the 2026 levels slope over 9 months, the 2026 changes slope over 8 months, and the levels slope over
    the 7 quarters 2025Q1-2026Q3. Quarterly gold is the equal-weight mean of three months; the quarterly yield is weighted by day.
    All use official yields. They are reproduction checks only.
- B1 carries no verdict. Its rows are descriptive, like D1-D9.

## 4. Decision rule (written 18 Oct 2026, before any regression was run)

**P1, the slope b, in log points per pp, with the 95% fixed-b HAC interval [lo, hi] = b̂ ± 2.105·se_HAC:**
- **SUPPORTS** a material same-month link: b ≤ −0.050 **and** hi < 0.
- **AGAINST** a material link: lo > −0.050. The interval excludes a slope of 0.050 log points per pp, and this case includes any
  zero or positive slope with a tight interval.
- **INCONCLUSIVE:** everything else. That covers an interval that includes both −0.050 and 0, and a negative interval whose point
  estimate is weaker than −0.050.
- The three regions are exclusive and exhaustive by construction. The selftest checks this on a grid.

**B1 (descriptive; no verdict).** The page may say only the following:
- "The break scan's bootstrap p-value is X at trim 0.15". The asymptotic table is quoted only as context.
- "The most likely break month is k̂, with a Bai interval of ±h months (unclipped). An interval that narrow would need a slope shift
  of at least s_min(h) per pp."
- When the interval is wide or the p-value is large: "no single break large enough to date was found; B1 cannot see a slope break
  below about 0.17 per pp, so this says nothing about 2024-26".
- The months found at trims 0.05 and 0.25, and the run with the 2021-12 dummy, are reported beside it.

The second reviewer's exact wording was not passed to the spec author. These sentences are written from the supervisor's ruling.

**Wording the page may use (descriptive objects):**
- D5 and D6 support only band statements of the form "in [window], the slope was X with band [a, b]".
  - "Collapsed and came back" stays HYPOTHESIS whatever D5 shows.
  - A 2026 break is never stated as a test result (§3.5).
- D8 residual label, only if cointegration holds on the fit sample:
  - `high`: "the pre-2022 fit leaves the later price high (same-month association)";
  - `not_high`: "the pre-2022 fit does not leave the later price unusually high";
  - `inconclusive`: nothing more is said.
- Official tonnes are never offered as the explanation.

## 5. Outputs

**Script:** `bin/gold_real_yield_break.py`. Modes:
- `fetch`: the 8 requests (D1, D2, D3 for each year from 2024 to the current year, D4, D5, D6). On later monthly runs, D2 and D4
  come from the cache.
- `build`: offline from the cache. A re-run is byte-identical. The retrieval dates in the outputs come from `fetch_log.csv`.
- `selftest`: synthetic data only, no network, under 30 s.
- `selftest --mutants`: runs each named mutant (§7) and requires every one to be caught.

All committed outputs go under **`data/gold_real_yield/`** (a new directory, so `data/gold/` and `build_gold_ledger.py` are
untouched). Every CSV starts with a `# source:` line naming the World Bank Pink Sheet (derived statistics only; the gold price is not
redistributed), Treasury and the Federal Reserve Board, with the retrieval dates. Then comes the header. Each file has an **exact
column allowlist**, and a header that differs from it is a hard failure.

| File | Columns, in order (exact allowlist) |
|---|---|
| `monthly_inputs.csv` (2003-01 to the end month; no gold) | `month, tips10_avg_pct_mc, tips10_avg_pct_official, tips10_days, tips10_mc_day_share, usd_broad_2006jan100, seam_flag` |
| `results.csv` (one row per registry object and coefficient) | `object_id, role, sample_start, sample_end, n, regressors, coef_name, coef, coef_unit, pct_approx, pct_exact, se_classical, se_hac, hac_lag, hac_lag_rule, crit_value, crit_basis, ci_level, ci_low, ci_high, r2, mde80, flag, verdict` (`verdict` filled for P1 only) |
| `cointegration.csv` | `test_id, role, sample_start, sample_end, T, adf_lags, adf_stat, cv_5pct, reject_5pct, levels_printed` (`role` = `gate` for 2006-01..2021-11, `info` for the full sample) |
| `break.csv` (3 trims × {none, imp_2021_12}; descriptive) | `trim, dummy_spec, first_candidate, last_candidate, n_candidates, sup_wald, p_value_boot, boot_draws, boot_mean_block, andrews_cv10, andrews_cv5, andrews_cv1, break_month_ssr, break_month_supwald, bai_ci_low, bai_ci_high, bai_halfwidth_months, ci_clipped, s_min_h4, s_min_h6, s_min_h8, s_min_h12, s_min_h18, resid_var_regime1, resid_var_regime2, hac_lag` |
| `chow_known_dates.csv` | `regime2_start, wald_hac, df, p_chi2, hac_lag, role` |
| `rolling36.csv` | `end_month, n, beta_ry, boot_lo, boot_hi, block_len, draws, seed`. `beta_ry`, `boot_lo` and `boot_hi` are written at **2 dp** (A3), and the SVG is drawn from the 2-dp values |
| `rolling36.svg` | A plot of the slope and band against end month, with a zero line. The caption names the block length and says "overlapping windows; not a count of tests" |
| `levels_summary.csv` | `object_id, fit_start, fit_end, coef_name, coef, ci_low, ci_high, hac_lag, resid_sd_in_sample, residual_label, status` |
| `checks.csv` | `check_id, description, expected, observed, status` (PASS, WARN, FAIL, INFO, SKIP) |
| `vintages.csv` | `source, file, retrieved_utc, sha256, bytes, published_updated_on, last_obs` |
| `fetch_log.csv` | `utc, host, path, status, bytes, sha256, outcome` |

- **Rounding:** coefficients and standard errors to 4 dp, except `rolling36.csv` at 2 dp; percents to 0.1; p-values to 3 dp.
- **Banned in any committed header**, as a second check alongside the allowlist: any cell containing `gold`, `ln_g`, `dln`,
  `fitted` or `price`, or starting `resid_`. The named exemptions are `resid_sd_in_sample` and `resid_var_regime1`/`resid_var_regime2`.
- `checks.csv` may record gold checks only as PASS/FAIL, as derived betas, or as the column sha256. It never records a gold value.
- **`README.md`** (A8):
  - It opens with one plain sentence: "This folder measures how gold's monthly average price moved with the US 10-year inflation-
    protected (real) Treasury yield from 2006 to September 2026, holding the dollar fixed, and checks whether that link shifted once."
  - Each term is defined at first use: real yield, log points, HAC standard error, fixed-b, cointegration, break scan, trim, Bai
    interval.
  - Then, in this order: the P1 result in words, with its band and verdict; the B1 description; the trim table and its sentence;
    "same-month association, not a cause or a forecast"; "a temporary two-year change in sensitivity is not tested by any
    confirmatory object"; the seam handling; the MDE; and which outputs are local only. That section states that public GLD data
    approximates the Pink Sheet series (median gap 0.034%), so the restriction follows the Bank's redistribution terms and is not
    about secrecy.
  - **Appendix:** the registry, and the decision text copied from §4.
- **`SOURCES.md`:**
  - each URL in §2 and what was taken from it;
  - the World Bank terms position (derived statistics only; the workbook names vendor sources);
  - the Treasury and Fed citations;
  - MacKinnon (2010) and Bai (1997);
  - Erb and Harvey (NBER w18706) and Torul (2026), as relayed by Grok.

## 6. Cross-checks the build runs on live data (each written to `checks.csv`)

**K01 Gold column.**
- The `Gold` header and the `($/troy oz)` units sit in the same column.
- 249 months, 2006M01 to 2026M09, no blanks.
- The sha256 of the lines `f"{YYYYMmm},{value:.4f}\n"` for 2006M01 to 2026M09 equals
  `c1ccb724d521450de7c283063c82ff619e40e94dc0b063738b8529f018a2798e` on the 2 Oct 2026 vintage. On another vintage a mismatch is
  WARN, with the revision report from R4.

**K02 Treasury dates and counts.**
- Two-digit years map to 20YY.
- 5,941 daily prints from 2003-01-02 to 2026-09-30, with no duplicates or blanks.
- September 2026: 21 days, sum 55.40, mean 2.6381 (official).
- January 2006: 20 days, sum 40.12.
- December 2021: 22 days, 3 of them before 6 Dec (−1.08, −1.03, −1.01).
- 2023-12-29 = 1.72. 2026-09-30 = 2.93.

**K03 Seam.**
- D4 mean gap = 0.026614 pp over 251 days.
- December 2021 MC-basis mean = (−21.85 + 3 × 0.026614)/22 = **−0.9896**. The official mean is −0.9932.
- January 2006 MC-basis mean = 2.0326.

**K04 Dollar.**
- 2006-01 = 100.0000, 2021-12 = 115.8045, 2025-12 = 120.1883, 2026-09 = 119.2152.
- The monthly value equals the mean of the daily values within 0.0001 in every month (WARN otherwise).
- The `Unit:` label mismatch is recorded as INFO.

**K05 Checksums (D9), each within 0.00005 (A6):**
- 2026 levels slope −0.20199;
- 2026 changes slope −0.31907;
- 2025Q1-2026Q3 quarterly levels slope −0.02101, with gold as the log of the equal-weight quarterly mean.
- The mean of the logs gives −0.02114, so the tolerance tells the two quarter definitions apart. A one-month misalignment of gold
  against the yield gives −0.16177 for the first checksum.
- The spec author reproduced all of these on 18 Oct from D1 and D3. They are published checksums, not P1 or B1.

**K06 Sample.** n = 248 changes. The rule-of-thumb lag is 4 and L = 12. The trim table is exactly as in §3.5.

**K07 Gold seam: LOCAL ONLY and descriptive.** It needs the gitignored sponsor file, so an outside reader's build always prints SKIP
here. That is expected, not a failure.
- If `data/vintages/gold/spdr_gld_archive.xlsx` exists, reuse `parse_gld()` from `bin/build_gold_ledger.py` to form the monthly mean
  of the GLD-implied LBMA PM price.
- Report the median absolute log gap to the Pink Sheet before and after 2025-06, and the change in mean gap at 2025-06. These are
  gap statistics only; no prices are written.
- WARN if the pre-2025-06 median gap is above **0.10%**. The second reviewer measured 0.034%. SKIP if the file is absent.

**K08 Leak scan: an explicit allowlist (A3).**
- The only files allowed under `data/gold_real_yield/` are the eleven named in §5, plus `README.md` and `SOURCES.md`.
- The only per-month files allowed are:
  - `monthly_inputs.csv`, which has no gold-derived column;
  - **`rolling36.csv`, the one named exception**, provided every `beta_ry`, `boot_lo` and `boot_hi` cell has at most 2 decimals.
- Any other file, any column outside its allowlist, or a third decimal in `rolling36.csv` is a FAIL.

**K09 P1 null size on the real X (regressor-only; no gold).** The build simulates 20,000 synthetic iid and AR(0.2) y on the real
Δr and Δu (RandomState(20261018)). The rejection rate of P1 at the fixed-b critical value must be at most 0.065. The spec author
observed 0.058 and 0.061.

## 7. Selftest: named guards, each with the mutant it must catch

The selftest uses synthetic series only: dates in 2030-2050, seeded, no World Bank values. `selftest --mutants` applies each mutant
in memory and must report it as caught.

| Guard | What it pins | Mutant that must fail it |
|---|---|---|
| G1 hac_lag_floor | L = max(12, rule); both printed | L = rule (4 at n = 248) |
| G2 hac_formula | Bartlett NW: the matrix and the explicit loop agree within 1e-12; L = 0 equals White HC0 | Weights 1 − l/L instead of 1 − l/(L+1) |
| G3 pct_exact | 100(e^b − 1): b = −0.202 gives −18.29 | pct_exact = 100b |
| G4 fixed_b_cv | The verdict uses the Kiefer-Vogelsang Bartlett cv at b = 12/248 (2.1046), within 0.02 of a seeded simulation of the fixed-b limit | z = 1.96, or the old 2.2414, in the verdict |
| G5 verdict_regions | On a grid of (b, lo, hi), exactly one of SUPPORTS, AGAINST or INCONCLUSIVE; the boundary cases are pinned | Grok's original overlapping wording (the AGAINST and INCONCLUSIVE regions overlap) |
| G6 andrews_table | The constants equal the Andrews (2003) Table I values in §3.5 (q = 1 and q = 3, all three trims, 10/5/1%); `p_value_boot` reproduces the seeded value on a synthetic series | The q = 3, trim 0.15 5% value replaced by the chi-square(3) 7.81 |
| G7 trim_ranges | The candidate ranges for n = 248 map to 2007-02/2025-08, 2009-03/2023-07 and 2011-03/2021-07 | Trim applied to the levels sample (T = 249), or an off-by-one in ⌈π₀n⌉ |
| G8 no_2026_break | The verbatim sentence is present; the max candidate month < 2026-01 | Candidates extended to n − 1 |
| G9 bai_interval | iid synthetic break, L = 0: h = 11.03·σ²/(δ′Qδ) within 1e-6; s_min(h) inverts h exactly; widths use the unclipped interval | 7.7 (the 90% anchor), a pointwise "dates not rejected" set, or a width taken from the clipped interval |
| G10 break_estimator | k̂ = the argmin SSR on a synthetic series with a break at a known month | k̂ taken from the first candidate whose Wald exceeds a chi-square line |
| G11 eg_critical | The gate is on 2006-01..2021-11; C(191) = −3.7858 and C(249) = −3.7752 (τc, N = 3); −4.1817 / −4.1670 (τct) | N = 2 coefficients (−3.336...), or the gate run on the full sample |
| G12 eg_behaviour | A seeded cointegrated pair rejects; two independent seeded random walks do not | ADF regression run on levels of g instead of the residuals |
| G13 levels_suppressed | When EG does not reject, every levels number cell is empty and status = `suppressed_no_cointegration` | Slope written regardless |
| G14 seam_adjust | The mean of a synthetic D4 (MC minus HS, known sign and size) is added only to dates < 2021-12-06; the synthetic December mean is pinned | Applied to ≤ 2021-12-06, to the whole month, or **with the sign flipped** (HS minus MC) |
| G15 two_digit_year | `1/2/03` → 2003-01-02 | `%y` replaced by a naive int (gives year 3) |
| G16 dollar_base | The base is asserted from the value (2006-01 = 100), not the `Unit:` label | Rebase to the label's 1997 |
| G17 gold_column | Header and units in the same column; synthetic workbook with a neighbour column | Column index off by one |
| G18 allowlist | Every output header equals its allowlist | Add `ln_gold` to `results.csv`, `n_excl_zero` to `rolling36.csv`, or `resid_last_sd_units` to `levels_summary.csv` |
| G19 leak_scan | K08's explicit file allowlist; rolling36 at 2 dp at most | Write the residual path to `data/gold_real_yield/`, or write `beta_ry` at 4 dp |
| G20 no_ledger | The script never opens `data/gold/ledger_monthly.csv`; no tonnes regressor | Add `official_change_cf_t` as a regressor |
| G21 registry | object_id ∈ the fixed registry | Add an unregistered `D10` |
| G22 block_bootstrap | Block length 6, B = 999 and the seed are written in every row; the seeded output is pinned | Block length 1 (iid bootstrap) |
| G23 cache_outside_repo | Refuses a `--cache` inside the repository | Accept `data/vintages/gold_ry/` |
| G24 stop_latch | Latch on 403, 429, 3xx and a bad body; no latch on 5xx or a socket fault; no fetch while STOP exists | Latch skipped on 403; or a fetch attempted with STOP present |
| G25 http_hygiene | Host allowlist, User-Agent exact and without `@`, GET only, no redirect, ≥ 5 s pacing, ≤ 12 requests | `fred.stlouisfed.org` allowed; a 4 s gap; a 13th request |
| G26 end_month | The decision sample ends 2026-09 even if the cache has later months | The end month taken from the latest vintage |
| G27 byte_identical | Two builds on the same cache give identical bytes | A wall-clock timestamp in an output |
| G28 null_size | On synthetic iid and AR(0.2) y, n = 248, with a real-shaped synthetic X (sd 0.18 and 0.013, correlation 0.39), P1's rejection rate at nominal 0.05 is ≤ 0.065. 20,000 draws, RandomState(20261018). The spec author's run of this exact design, with Gaussian X drawn first from the same seed, gave 5.8% (iid) and 5.1% (AR) at 2.1046 | The standard-normal cv (1.96) with L = 12: 7.5% (iid) and 6.9% (AR) on that synthetic X, and 7.6-7.8% on the real X |
| G29 supwald_stat | The vectorised sup-Wald equals an explicit-loop reference (per candidate: fit, HAC, Wald) on synthetic data, within 1e-9, at every candidate | The HAC covariance taken from the restricted model, or the candidate set shifted by one |
| G30 month_alignment | Gold, yield and dollar are joined on explicit `YYYY-MM` keys; on a synthetic panel with a known same-month slope the slope is recovered; the joined first and last months equal 2006-01 and the end month | Gold shifted one month against yield and dollar (on the real data, checksum 1 moves from −0.20199 to −0.16177) |

## 8. Success criteria (commands, and what they must print)

1. `python3 bin/gold_real_yield_break.py selftest` prints 30 guards PASS. `selftest --mutants` prints 30 of 30 mutants caught.
2. `python3 bin/gold_real_yield_break.py fetch` makes 8 requests or fewer. All return 200, are logged in `fetch_log.csv`, and leave no
   file from D1 inside the repository (`git status --porcelain` shows only `data/gold_real_yield/` and the script).
3. `python3 bin/gold_real_yield_break.py build` prints, in this order:
   - (a) the vintage line `World Bank workbook: Updated on October 02, 2026, sha256 ea1c3508…` (or a later vintage, with the revision
     report);
   - (b) the K01-K06 values above, each PASS: gold sha256 `c1ccb724…`, 5,941 Treasury days, Sep 2026 2.6381, D4 gap 0.026614 over
     251 days, December 2021 MC-basis −0.9896, dollar 100.0000 / 115.8045 / 119.2152, checksums −0.20199 / −0.31907 / −0.02101;
   - (c) `n = 248, HAC lag 12 (rule-of-thumb 4), fixed-b cv 2.105 (b = 0.0484)`, and K09's two sizes, each ≤ 0.065;
   - (d) the trim table and its sentence;
   - (e) the gate EG statistic on 2006-01..2021-11 against −3.7858 **before** any levels number (the full-sample INFO row against
     −3.7752);
   - (f) the P1 verdict with its numbers and the realised MDE, then the B1 description (bootstrap p, Andrews table, k̂, h, s_min),
     with no verdict.
4. `git diff` after a second `build` is empty (byte-identical).
5. A header scan of the CSVs only (the README is allowed to use the word "gold"), for example
   `for f in data/gold_real_yield/*.csv; do grep -v '^#' "$f" | head -1; done | grep -iE "gold|ln_g|dln|fitted|price|resid_(last|mean)"`,
   returns nothing. No `.xlsx` appears in the repository. K08 passes.
6. The supervisor re-derives one number independently: for example, the P1 slope by hand OLS from the cached files, or the December
   2021 MC-basis mean from D2 and D4.

## 9. Landing

- A `CALENDAR.tsv` row, MONTHLY, the third business day (after the Pink Sheet and H.10): `selftest`, then `fetch`, then `build`. The
  row says the verdict is pre-registered on 2026-09, so later months are updates. It also says: if `fetch` prints STOP, do not
  retry or route around it; tell the principal.
- A `.gitignore` rule for `CMO-Historical-Data-Monthly*.xlsx` anywhere. This is defensive, since the cache is outside the repository.
- A data note in REPRODUCE.md.
- The supervisor writes any findings text in E-021 after verification. A warn-only check.sh gate for `data/gold_real_yield/`
  headers is the supervisor's call.

## 10. Open questions

- **OPEN-1. The size of the 2008-12-01 knot change.** No overlap file was seen. It would be settled by a Treasury file of old-method
  and new-method R-CMTs for late 2008, if one exists: look on the methodology pages, or ask Treasury. Until then 2008-12 is handled
  only by D4 and D7.
- **OPEN-2. The size of the gold definition change at 2025-06.** The workbook gives no overlap. K07 measures it against the
  GLD-implied PM price where the local file exists. A World Bank note giving the spot vendor would settle what "spot" means.
- **OPEN-3. Size of the stationary-bootstrap B1 p-value.** The spec author did not verify it; it is a heavy simulation. Since B1 is
  descriptive, this matters only for how its p-value is worded. Running G28's design on B1 (500 synthetic series × B = 199) would
  settle it. The Andrews (2003) table was read from a third-party copy (§3.5), so check it against the DOI version. Hansen's
  response surface is no longer needed.
- **OPEN-4. RULED 18 Oct.** Coefficients and test statistics are not a copy of the data. They are published with the World Bank cited.
- **OPEN-5. Fed revisions to the pre-2022 dollar history.** These are not stated on the release page. The second monthly fetch
  settles it, through R4's revision report.
- **OPEN-6. RULED 18 Oct.** Treasury data is US government work, so committing the monthly averages is fine.
- **OPEN-8. The fixed-b cubic's coefficients.** The spec author recalled them (Kiefer and Vogelsang 2005, Econometric Theory) and did
  not re-read them. The simulation agrees to 0.001. Reading the paper's table settles it; G4 guards it either way.
- **OPEN-7. Erb and Harvey (NBER w18706) and Torul (2026).** The figures are as relayed by Grok and were not re-read by the spec
  author. They are context only and not inputs.

## Amendments, 18 Oct (second review)

The supervisor ruled on a second independent review. Every change is applied in the sections above. Commands were run in the
foreground. The spec author stayed blind: no P1 or B1 was computed on real gold. Only regressor-only simulations and the
already-published checksums were run.

- **A1. Test sizes (ruling 1).**
  - B1 is now descriptive. Its p-value is a stationary bootstrap (B = 999, X fixed, mean block 6, restricted residuals, same HAC and
    trim), with the Andrews table printed beside it and never used for a label (§3.5, §3.7, §4).
  - P1 is the one confirmatory test, at α = 0.05, with the fixed-b Bartlett critical value **2.105** at b = 12/248: the Kiefer-
    Vogelsang cubic gives 2.1046 and the spec author's simulation 2.104 (§3.3). The Bonferroni split and the 97.5% interval are gone.
  - New guard G28 null_size, and live check K09. With the real Δr and Δu the spec author measured a size of 5.8% (iid) and 6.1%
    (AR(0.2)) at 2.105, against the 6.5% limit.
  - G6 now pins the published Andrews (2003) Table I, fetched once: 5% q = 1 9.71/8.68/7.87 and q = 3 15.36/14.13/13.18 at trims
    0.05/0.15/0.25. All seeds use `numpy.random.RandomState`. The spec author's earlier `default_rng` simulation (q = 3 5%:
    15.34/14.06/13.08) and the reviewer's (15.05/13.94/12.93) both sit within 0.25 of Andrews.
- **A2. B1 decision text (ruling 2).** The SUPPORTS/AGAINST branches are replaced by wording about what the Bai half-width implies.
  The formula for s_min(h) is given, and `break.csv` prints it for h = 4 to 18. h ≤ 8 needs a slope shift of about 0.25 per pp.
  Widths use the unclipped interval. §3.6 now carries the ruled sentence on 0.17 per pp.
- **A3. Leak (ruling 3).** The claim that no per-month value is committed is withdrawn. `rolling36.csv` is published at 2 dp, as the
  one named exception. The two residual-in-sd columns are replaced by the three-way `residual_label`. K08 is now an explicit file
  and column allowlist. R1 and the README state that public GLD data approximates the Pink Sheet series (median gap 0.034%), so R1
  follows the Bank's redistribution terms and is not about secrecy.
- **A4. Cointegration gate (ruling 4).** The gate runs on 2006-01 to 2021-11 (T = 191). MacKinnon values were recomputed: τc
  −3.7858, τct −4.1817. The full sample (−3.7752, −4.1670) is INFO.
- **A5. §0 (ruling 5).** Added: "A temporary two-year change in sensitivity is not tested by any confirmatory object."
- **A6. Guards (ruling 6).**
  - New: G29 supwald_stat (explicit-loop reference) and G30 month_alignment (a one-month shift moves checksum 1 from −0.20199 to
    −0.16177).
  - Changed: G14 has a sign mutant on a synthetic D4. K05 is now at 5 dp within 0.00005 (equal-weight −0.02101 against mean-of-logs
    −0.02114). K07 warns at 0.10% and is marked local-only (SKIP for outside readers). G9's coverage claim is dropped.
- **A7. Row counts (ruling 7).** The files have no trailing newline. D2 has 5,254 data rows; D3 has 250 (2024), 249 (2025) and 199
  (2026). The 5,941-day count through 2026-09-30 is unchanged.
- **A8. README (ruling 8).** It opens with one plain sentence and defines terms at first use. The registry and decision text move to
  an appendix. Success criterion 5 scans CSV headers only.
- **A9. OPENs (ruling 9).** OPEN-4 is ruled: coefficients and statistics are published with the World Bank cited. OPEN-6 is ruled:
  Treasury monthly averages are committed. Added: OPEN-3 (bootstrap size) and OPEN-8 (the fixed-b cubic was recalled, not re-read).
- **New sources fetched once each (neutral User-Agent):** the Andrews (2003) corrigendum, from the copy attached on the gretl users
  list (`gretlml.univpm.it/.../andrewsCorrect.pdf`, 200, 40,266 bytes, 3 pages; the decimal points were lost in extraction and
  restored by column).
