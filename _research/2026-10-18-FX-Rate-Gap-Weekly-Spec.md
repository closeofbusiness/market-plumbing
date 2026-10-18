# Spec: the yen and the euro against rate gaps, weekly regression (spec author, 18 Oct 2026)

*E-021 build queue item 4 (`2026-10-12-E021-Where-The-Money-Comes-From-Rates-FX-Commodities.md`, "Builds, in order"). The
earlier design and its pre-registered windows are Grok batch g4, item 4, in `_research/2026-10-14-Grok-G4-Returns.md`. Grok's
adversarial review of that design (batch g7, return 2) required eight changes. The supervisor accepted all eight with the rulings
quoted in section 3, and those rulings outrank Grok where the two differ. Modelled on `_research/2026-10-15-ICE-Brent-COT-Spec.md`
(house style) and on the fetch code of `bin/r1_treasury_decomposition.py` and `bin/r3_jgb_egb.py`.*

*Every web fact below was observed on 18 Oct 2026 with one request per URL, with the CLAUDE.md non-SEC User-Agent. "Relayed"
marks a fact taken from Grok's return or g4 and not re-fetched here.*

*Amended 18 Oct after a second independent review, which re-derived every pin (all matched). The supervisor accepted all
eleven of its fixes. The body below already carries them; the section "Amendments, 18 Oct (second review)" at the end lists
each change. Counts marked "expected" are the reviewer's and are recomputed by the builder before they are pinned.*

## 0. Goal, and what the result can and cannot say

- Measure how far weekly changes in the US-minus-Japan 2-year yield gap move with the yen per dollar after the Bank of Japan's
  19 March 2024 change of framework. Then measure what share of the yen's cumulative move over the non-intervention weeks the
  fitted gap term accounts for.
- Run the same regression, as description only, for the euro and for the 2018–2026 full sample and the three windows fixed
  in g4.
- One pre-registered test (section 3.6) and one decision rule, written before any FX or coefficient was computed (section 4).

**It can say:** whether, in non-intervention weeks from 29 Mar 2024 to 18 Sep 2026, the yen moved with the 2-year gap, at what
rate (change in log yen per dollar per percentage point of gap), and whether the weekly 2-year-gap-change term accounts for
at least half, or for less than a quarter, of the yen's cumulative log change over those same weeks, or points the other way.
All of this is association (grade MEASURED for the coefficient, IDENTITY for the share given the coefficient). The intercept
absorbs any level or carry channel: S = nα̂ + F, so a share near zero does not mean that the gap's level is irrelevant.
**It cannot say:** that rates (or flows, positions, or intervention) caused any move; anything about the intervention weeks
themselves, which are dropped; anything about real yields, policy rates or forecasting. Nor can it say that "rates do not
matter" if the power gate in 4.2 fails. W3 and the post-March-2024 sample were dated after the 2024–26 path had been tabulated
(g4, 14 Oct), so the primary is not a blind test. That is why the full-sample row is printed next to it every time.

## 1. Hard requirements

- **R1. Free public data only (E-005). No FRED** (it refuses scripts). Host allowlist: `home.treasury.gov`, `www.mof.go.jp`,
  `stats.bis.org`, `data-api.ecb.europa.eu`, `api.statistiken.bundesbank.de`. Any other host is refused before the request is made.
- **R2. User-Agent** exactly `Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)`. Assert no `@` in it.
  It must pass `bin/check.sh`'s M10. Never send an email address, a name, `SEC_UA` or `CLAUDE_CODE_USER_EMAIL`.
- **R3. Polite and refusal-safe fetches.** Requests are sequential and at least 2 s apart, with at most 30 per run. GET only, and
  no redirect is followed. Any status other than 200, or a body that fails its content test (section 2), writes
  `data/vintages/fx_rate_gap/STOP` and ends the run. Nothing retries, nothing routes around a refusal, and only a person deletes
  the latch. A socket fault ends the run without latching. `data/fx_rate_gap/fetch_log.csv` records `utc_time, host, path,
  status, bytes, sha256` for every request.
- **R4. Raw files and per-week series stay out of git.** The cache is `data/vintages/fx_rate_gap/`, with a `.gitignore` rule (the
  R1/R3 pattern). No committed file carries a per-week series from which a yield level can be rebuilt (jp2, jp10 or ea2_sa
  follow from us2 and a gap), so the weekly panel lives in the cache. Commit only the statistics, decision, pins and notes of
  section 5. Each output's first line is `# source:`, naming every publisher and the retrieval
  dates. The dates are read from `fetch_log.csv`, so an offline `build` is byte-identical.
- **R5. No causal language.** No output, README or printout says a flow, position or intervention caused, drove or "leaned
  against" a price. Guard G19 enforces it.
- **R6. Stdlib only.** Use 2×2 and 3×3 matrix algebra by hand. No numpy, so the selftest runs anywhere.

## 2. Data (all verified 18 Oct 2026; one request each unless stated)

| Leg | URL (exact) | Series / field | Units, convention | Release timing | Observed 18 Oct |
|---|---|---|---|---|---|
| US | `https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{Y}/all?type=daily_treasury_yield_curve&field_tdr_date_value={Y}&page&_format=csv`, Y = 2017–2026 (10 requests) | columns `2 Yr`, `10 Yr`, **read by header name** | percent, par yield, semiannual bond-equivalent; curve from bid quotes near 15:30 New York (Treasury methodology, relayed) | same day, usually by 18:00 ET (relayed) | 200, 16,229 bytes; rows to 10/16/2026 (2y 4.74, 10y 5.09); newest row first. The 2025–26 files carry an extra `1.5 Month` column, so the 2023–24 files have different column positions: a positional read of the 2023 file, using the 2026 positions, returned 4.01 (the 3-year) as the 2y and 4.20 (the 20-year) as the 10y for 12/29/2023 (true 4.23 and 3.88) |
| Japan | `https://www.mof.go.jp/english/policy/jgbs/reference/interest_rate/historical/jgbcme_all.csv` (1 request) | `2Y`, `10Y`; header on line 2; dates `Y/M/D` without zero padding; missing as `-`; trailing note lines | percent, semiannual compound, constant maturity, at 15:00 Tokyo (MoF Q&A, relayed) | 09:30 Tokyo the next business day (relayed). History file updated to the previous month-end | `jgbcme_all.csv` 200, 1,195,548 bytes, 1974/9/24 to 2026/9/30, which covers sample P (ends 18 Sep). The current-month `jgbcme.csv` (200, 1,249 bytes, 2026/10/1 to 2026/10/15) is **not fetched** by the build; G13's overlap rule is tested on a fixture only |
| Euro area | `https://data-api.ecb.europa.eu/service/data/YC/B.U2.EUR.4F.G_N_A.SV_C_YM.BETA0+BETA1+BETA2+BETA3+TAU1+TAU2+SR_2Y+SR_10Y+PY_2Y+PY_10Y?format=csvdata&startPeriod=2017-12-01` (1 request) | AAA Svensson parameters, spot and par | percent; the ECB's model is continuously compounded (ECB technical notes) | the notes say: released 12:00 CET each TARGET day, fitted to "gross price at the close of the previous business day", MTS data | SR to 2026-10-15. On 2026-09-18: SR_2Y 3.2152124072, SR_10Y 3.529753074, PY_2Y 3.2107329091, PY_10Y 3.5024674241, BETA0 1.608146049, BETA1 0.6677584932, BETA2 2.8889513654, BETA3 6.8503522231, TAU1 1.0445730922, TAU2 13.8644399107 |
| FX | `https://stats.bis.org/api/v2/data/dataflow/BIS/WS_XRU/1.0/D.JP+XM.JPY+EUR.A?startPeriod=2017-12-01&format=csv` (1 request) | `D.JP.JPY.A` yen per USD; `D.XM.EUR.A` euro per USD | foreign currency per 1 USD, daily | BIS weekly; current to 13 Oct on 18 Oct | 2026-10-12 158.59941 and 0.894374; 2026-10-13 158.124777 and 0.893815. No source or fixing-time attribute on the series (checked with `attributes=all`) |
| FX check | `https://data-api.ecb.europa.eu/service/data/EXR/D.JPY+USD.EUR.SP00.A?format=csvdata&startPeriod=2017-12-01` (1 request) | ECB euro reference rates | currency per EUR | ECB daily concertation, early afternoon CET | 2026-09-18: JPY 180.94, USD 1.1460. 180.94/1.1460 = **157.888307 = BIS yen**, and 1/1.1460 = **0.8726 = BIS euro**. So on that date the BIS daily rate is the ECB reference cross |
| Intervention, dated | `https://www.mof.go.jp/english/policy/international_policy/reference/feio/foreign_exchange_intervention_operations.csv` (1 request) | daily operations, April 1991 to June 2026 | 100 million yen, **CP932 (Shift-JIS) encoding**, thousands commas, quarter subtotal rows interleaved. The year is written only on the first day row after a subtotal row or a gap, and the month only when it changes: the 2022-10-24 row has both blank, so the parser carries year **and** month down | **Quarterly, with a lag**: the quarterly index lists Apr–Jun 2026 as the latest; that page was released 7 Aug 2026 (relayed), about 5.5 weeks after the quarter ended | 200, 43,477 bytes, 550 lines. Days since 2018: 2022-09-22 28,382; 2022-10-21 56,202; 2022-10-24 7,296; 2024-04-29 59,185; 2024-05-01 38,700; 2024-07-11 31,678; 2024-07-12 23,670; 2026-04-30 62,787; 2026-05-04 7,802; 2026-05-06 46,759. Zero in every 2018–2021, 2023 and 2025 quarter |
| Intervention, undated | `.../feio/monthly/20260731e.html`, `20260828e.html`, `20260930e.html` (3 requests) | "Total amount ... for the period from A through B ¥ X" | yen | monthly, about 2 days after each window | Jun 29–Jul 29 2026: ¥0. **Jul 30–Aug 26 2026: ¥15,399.3 billion, no day split.** Aug 27–Sep 28 2026: ¥0 |
| Check only | `https://api.statistiken.bundesbank.de/rest/data/BBSIS/D.I.ZST.ZI.EUR.S1311.B.A604.R02XX+R10XX.R.A.A._Z._Z.A?format=csv&lang=en&startPeriod=2017-12-01` (1 request) | Svensson yields for listed Federal securities, 2y and 10y | percent, 2 decimals; `.` for no value | last update 2026-10-16 12:13; data to 2026-10-16 (2y 3.08, 10y 3.48) | Used only in one data-quality correlation in `checks.csv` (section 6, C12). Not a regressor, because its compounding basis and observation time are OPEN (O-1). No Bundesbank value is committed |

**Not used.** The Fed H.10 rates through the Data Download Program are not used. The H.10 Choose page answered 200 and names the
"Daily rates" package `60f32914ab61dfab590e0e470153e3ae`, but `Output.aspx` for it returned HTTP 200 with an empty body on two
requests. That was not pursued further (O-3). Policy-rate gaps are not used either: no free series was named (Grok: FAILS).

**Licences and what is committed (O-6 ruled by the supervisor, 18 Oct).** No per-week series that rebuilds a yield level is
committed: the weekly panel, every raw download and every per-week level stay in the gitignored cache. The committed files are
the regression statistics, the decision, at most five pins per source (each with a `pin_date`), the intervention list, the
checks, the README and SOURCES.
- BIS: reuse with citation (data.bis.org/help/legal, relayed).
- ECB: reuse with "Source: ECB statistics", unmodified (relayed). The semiannual par yield in 3.2 is labelled a project
  computation from ECB parameters, not an ECB statistic.
- MoF yields and intervention data: Public Data License 1.0, with numerical data outside copyright (relayed). JSDA rights
  behind the yields: not read.
- Treasury: a US government work; the CC0 catalogue page was not read.
- Bundesbank: cited as "Source: Deutsche Bundesbank, time series BBSIS.D.I.ZST.ZI.EUR.S1311.B.A604.R02XX/R10XX"; its terms page
  was not read in this pass. Only a correlation and a list of dates derived from it are committed, no Bundesbank value.

**Vintages.** Every file's sha256 goes into `fetch_log.csv`. Pinned values (section 6) are WARN, not FAIL, on mismatch, with
the hint "source may have restated" (ECB says its series can be revised). Treasury and MoF history are not normally revised.

## 3. Method

### 3.1 Weeks and alignment (the time-zone rule)

- **Week end.** A week runs Monday to Friday. Its FX date `fx_date` is the last day of that week with an ECB reference rate
  (normally the Friday; Thursday on Good Friday or 1 May; 24 Dec 2025 in the week of 26 Dec). `week_end` is the calendar
  Friday. Weeks are keyed by ISO (year, week), and duplicates are a hard failure.
- **FX price.** BIS `D.JP.JPY.A` and `D.XM.EUR.A` on `fx_date`. Each must equal the ECB reference cross for that date
  (JPY/EUR ÷ USD/EUR, and 1 ÷ USD/EUR) within 1e-6 relative. A mismatch is a FAIL that names the dates, because it would mean
  BIS filled a day from another fixing time.
- **When each leg is observed, on a Friday** (times in GMT, winter/summer):
  - MoF JGB: 15:00 Tokyo = 06:00.
  - ECB reference fix: about 13:10 / 12:10.
  - ECB AAA curve: European close.
  - Treasury par: about 15:30 New York = 20:30 / 19:30.
- **Primary rule: no leg is observed after the FX price.**
  - Japan: the MoF yield on `fx_date`, or the last earlier MoF date.
  - United States and euro area: the last observation **strictly before** `fx_date` (normally Thursday's close).
  - This is Grok's "no regressor is a lead" applied inside the day. The same-calendar-Friday alternative would put 15:30 New
    York yields, observed about seven hours after the FX price, into the regressor. It would also put the 08:30 ET US data
    releases into the yield change one week before the FX change (in both seasons 08:30 ET falls after the fix).
- **The mismatch that remains, stated.** The FX change runs from fix to fix. The US and euro legs run from Thursday close to
  Thursday close, so their window ends about 16–17 hours before the fix. US and euro news in the Asian and London hours of
  Friday morning enters this week's FX change but next week's yield change. The JGB window ends about 7 hours before the fix.
  In the two to three weeks each March and October–November when US and European clock changes differ, an 08:30 ET release falls
  about 40 minutes before the fix.
- **Labelled check.** The conventional same-calendar-Friday version: the US leg on `fx_date` (or the last earlier date), the
  JGB leg as primary. It enters the decision rule only as a fragility check (4.3c).
- **Stale legs.** For each leg the pair uses, the span between its observation dates for weeks t−1 and t must be 4–10
  calendar days. Otherwise week t is dropped as `stale_leg` and listed in `event_weeks.csv`. The rule is per pair: a stale JGB
  leg drops a yen week, never a euro week. Japanese market closures produce the known cases. The reviewer found these in the
  yen sample: 2019-05-03 and 2019-05-10 (Golden Week 2019); 2020-01-03 and 2020-01-10, and 2025-01-03 and 2025-01-10 (New
  Year). In the New Year cases the JGB date for the week ending 3 Jan is 30 Dec, three days after the previous one, and the next
  span is 11 days.
- **Pinned alignment triples (fx_date / us_date / jp_date), guard C14:**
  - week ending 2024-03-29 (Good Friday): 2024-03-28 / 2024-03-27 / 2024-03-28;
  - 2025-01-03: 2025-01-03 / 2025-01-02 / 2024-12-30;
  - 2025-12-26: 2025-12-24 / 2025-12-23 / 2025-12-24;
  - 2026-01-02: 2026-01-02 / 2025-12-31 / 2025-12-30.

### 3.2 Gaps (consistent compounding)

- Both pairs are quoted as **foreign currency per US dollar**. Every gap is **US minus foreign**, in percentage points. A wider
  gap and a stronger dollar both raise the series, so the slope β is expected to be positive for both pairs.
- **Yen gaps.** Treasury par (semiannual bond-equivalent) minus MoF constant maturity (semiannual compound). Both legs are
  semiannual: `gap_jp2 = us2 − jp2` and `gap_jp10 = us10 − jp10`. The slope gap is
  `slope_gap_jp = (us10 − us2) − (jp10 − jp2) = gap_jp10 − gap_jp2`.
- **Euro gaps.** Treasury par minus the ECB AAA par yield **recomputed on the semiannual convention** from that date's Svensson
  parameters:
  - z(T) = β0 + β1·(1−e^{−T/τ1})/(T/τ1) + β2·[(1−e^{−T/τ1})/(T/τ1) − e^{−T/τ1}] + β3·[(1−e^{−T/τ2})/(T/τ2) − e^{−T/τ2}], in percent,
    continuous.
  - The discount factor is d(T) = exp(−z(T)·T/100).
  - The par yield is `ea{T}_sa = 200·(1 − d(T)) / Σ_{i=1}^{2T} d(i/2)`.
  - Two self-checks on every date: z(T) must reproduce published SR_2Y and SR_10Y within 1e-6. The continuous-coupon par
    (1 − d(T)) / ∫₀ᵀ d(t)dt (midpoint rule, 20,000 steps) must reproduce PY_2Y and PY_10Y within 1e-4.
  - On 2026-09-18 this gives `ea2_sa` 3.237019 and `ea10_sa` 3.533452. The published continuous-coupon par yields that day are
    3.2107 and 3.5025, and the zero yields 3.2152 and 3.5298. Subtracting a continuous zero yield from a semiannual par yield, as
    the g4 design did, is the error Grok's change 5 names.
  - "Euro area AAA" has a changing composition. A week in which the ECB changes the AAA set shows up as a jump: C12 compares it
    with the Bund.

### 3.3 Transformation and estimator

- `dln_jpy_t = ln(usdjpy_t / usdjpy_{t−1})` and `dln_eur_t = ln(eur_per_usd_t / eur_per_usd_{t−1})`, natural logs on
  consecutive kept-or-not weeks. Each gap change, `d_x_t = x_t − x_{t−1}`, is the change from week t−1's row to week t's row.
  There are no other leads or lags.
- OLS of `dln` on a constant and the gap change(s). Weekly changes, never levels: the spot is a unit-root series (Grok change 1).
- **Contribution.** The rate contribution is the sum over the sample of the fitted slope terms, `F = β̂·Σ d_x` (one per term),
  intercept excluded. The cumulative residual is not an output: with a constant it is zero by construction. Its sum is asserted
  to be zero within 1e-8 on every fit.
- **Standard errors.** HC3 is primary, Newey-West with lag 4 (Bartlett weights, no small-sample factor) is the check. The
  printed Hansen-Hodrick lag is 0: weekly changes do not overlap, so no overlap correction applies (Grok change 2).
  - HC3: (X'X)⁻¹ X' diag(e_i²/(1−h_ii)²) X (X'X)⁻¹.
  - p-values and intervals use the normal distribution (1.959964).
- No intervention amount, dummy or flow is ever a regressor (Grok change 7). The design matrix is exactly [1, d_x] or, for the
  descriptive joint row, [1, d_gap2, d_gap10].

### 3.4 Intervention weeks (Japan only)

- **Dated operations.** From the MoF CSV, plus later quarterly releases when they appear. Drop week t if any operation day d
  satisfies `fx_date_{t−1} ≤ d ≤ fx_date_t`. The **starting** day is included: a Friday operation after the fix (for example
  21 Oct 2022 or 12 Jul 2024) lands in the next week's change, so it drops two weeks.
- **Undated blocks.** A monthly window with a non-zero total and no published days drops every week whose
  [fx_date_{t−1}, fx_date_t] meets the window. A window with a zero total keeps its weeks.
- **Restored-weeks sensitivity.** The same fit with every intervention-dropped week put back, dated and block (4.3b). Stale
  weeks stay dropped, so in P the variant has n = 128.
- **When MoF publishes the July–September 2026 days** (expected early November, O-4), `build` replaces the block with the dated
  days automatically. Both runs are kept in `decision.csv` under their own `run_label`. The supervisor writes up any change, and
  the earlier run is never deleted.
- **What the drop rules produce.** In sample P the intervention rule drops exactly the weeks ending 2024-05-03, 2024-07-12,
  2024-07-19, 2026-05-01, 2026-05-08, 2026-07-31, 2026-08-07, 2026-08-14, 2026-08-21 and 2026-08-28 (10 of 130), and the stale
  rule drops 2025-01-03 and 2025-01-10: 118 kept. In W2 the intervention rule drops 2022-09-23, 2022-10-21 and 2022-10-28. The
  euro regressions drop no weeks for intervention.

### 3.5 Samples (fixed in g4 on 14 Oct; P added by the supervisor's ruling)

A sample is the set of weekly changes whose `week_end` lies in it.

| Sample | First `week_end` | Last `week_end` | Weeks | Yen weeks kept (expected) |
|---|---|---|---:|---:|
| FULL | 2018-01-05 | 2026-09-18 | 455 | 436 (13 intervention, 6 stale) |
| W1 | 2018-01-05 | 2021-12-31 | 209 | 205 (4 stale) |
| W2 | 2022-01-07 | 2023-12-29 | 104 | 101 (3 intervention) |
| W3 | 2024-01-05 | 2026-09-18 | 142 | 130 (10 intervention, 2 stale) |
| **P** | **2024-03-29** | **2026-09-18** | **130** | **118 (10 intervention, 2 stale)** |

- P starts with the first week whose starting row (22 Mar 2024) postdates the BoJ decision of Tue 19 Mar 2024, so the decision
  week is excluded.
- FULL is the full-sample descriptive regression that Grok's change 8 and the ruling require next to any split. The 6 Dec 2021
  change in Treasury's curve method does not start a window (Grok change 8).
- The "expected" column applies both rules. It is the reviewer's count: the builder recomputes every count from the cache
  before pinning, and a difference must be explained in the README.

### 3.6 The one primary test, and why the 2-year gap

- **Primary.** The pair is yen; the sample is P with intervention weeks dropped; the regression is
  `dln_jpy = α + β·d_gap_jp2 + e`. H0: β = 0, two-sided, 5%, HC3. This is the only confirmatory test in the build.
- **Separately labelled (role SEPARATE).** The same regression with `d_slope_gap_jp`, Grok's change 6.
- **Everything else is DESCRIPTIVE:**
  - 10y gap alone;
  - joint 2y+10y, with the VIF printed;
  - every other sample;
  - all euro rows.
  `regressions.csv` prints k, the number of descriptive rows. The README says that a reader who treats them as tests must use
  0.05/k.
- **Why the 2-year gap is primary and not the slope gap.** The supervisor ruled to pick one from change 6.
  1. **The slope gap cannot answer the question asked.** The question is how much of the cumulative move the gap accounts for.
     The slope gap's cumulative change over P is close to zero, so its share φ is close to zero for any β. From the levels on
     the end rows (regressor-only arithmetic; no FX was touched), the totals over all 130 P weeks are:
     - slope gap: +0.044pp (−0.906 to −0.862);
     - 2y gap: −1.593pp (4.414 to 2.821);
     - 10y gap: −1.549pp.
     The yields behind these: Treasury 21 Mar 2024 2y 4.62, 10y 4.27; 17 Sep 2026 2y 4.67, 10y 4.94. MoF 22 Mar 2024 2Y 0.206,
     10Y 0.762; 18 Sep 2026 2Y 1.849, 10Y 2.981. A regressor whose total is +0.044pp can attribute at most β×0.044 of a move of
     several log points. Its test would be a test of week-to-week co-movement only, and could not reach the "at least half"
     class in section 4.
  2. Since 19 Mar 2024 the BoJ's main tool is the short-term rate, with JGB buying continued (BoJ statement, relayed by Grok
     from boj.or.jp/en/mopo/mpmdeci/state_2024/k240319a.htm). The 2-year gap carries relative policy expectations. The 10-year
     JGB, and so the slope gap, still carries the BoJ's purchases (O-9).
  3. The rate-differential literature Grok fetched uses a short nominal differential (Lilley, Maggiori, Neiman and Schreger,
     NBER w26046: 3-month). The relative-slope result for the yen (Chen and Tsang, 2011) is about forecasting at monthly
     horizons, not attribution of a contemporaneous move.
  4. The slope gap equals gap10 minus gap2 exactly. A regression on it imposes equal and opposite effects of the two tenors,
     which is a restriction, not a cleaner measure.
- **The forking path, disclosed.** The choice between the 2-year gap and the slope gap was made after the spec author had seen
  how both regressors moved over P: the four end-point yields and the totals in reason 1. The FX path was not seen. A primary
  regressor chosen with knowledge of the regressors' own path is one fork of the garden, even when the outcome is unseen. The primary
  was chosen after tabulating the yield totals of three candidate gaps (+0.044, −1.593, −1.549 over P). No FX was used. The
  10-year alternative has the same X as the 2-year, so the choice does not change φ's arithmetic. The slope regression stays in
  every output as the SEPARATE row, and the README states this paragraph. (Supervisor, 18 Oct, from the second review.)

## 4. Decision rule (written 18 Oct 2026, before any FX series or coefficient was computed)

### 4.1 Quantities (sample P, kept weeks, n expected 118)

- S = Σ `dln_jpy`, the cumulative log change **over the kept weeks only**. This is the denominator of φ. It is not the yen's
  whole move: the README prints S_all over all 130 weeks and S_dropped, with S_all = S + S_dropped (IDENTITY). S_all is never
  the denominator (G20 mutant).
- X = Σ `d_gap_jp2` over the kept weeks (expected about −0.895pp), and F = β̂·X.
- **The intercept absorbs any level or carry channel: S = nα̂ + F** (IDENTITY, because the residuals sum to zero).
  `decision.csv` prints nα̂ beside F.
- φ = F / S. Leave it blank if |S| ≤ 0.01.
- **Which standard error is used where:**
  - the power gate uses SE_gate = max(placebo SD, SE_HC3);
  - the β and φ intervals of the primary, and its verdict, use SE_HC3;
  - variant (a) uses SE_NW4 for its interval, and prints a gate with max(placebo SD, SE_NW4);
  - variants (b) and (c) use their own SE_HC3 and their own placebo.
- The β interval is β̂ ± 1.959964·SE. The **φ interval** is the two endpoints β_lo·X/S and β_hi·X/S, **sorted**. X/S can
  be negative: X is negative over P, and if S > 0, then β > 0 gives φ < 0. A φ below zero means the weekly gap term pointed the
  other way from the yen's move.

### 4.2 Power gate (C-090, C-091, C-092), computed before β̂ is read

- **Placebo.** Re-estimate β on every circular shift of the kept `d_gap_jp2` series by k = 13 … n−13 weeks, so
  n_placebo = n − 25 (93 shifts at n = 118). This destroys the alignment and keeps the regressor's own autocorrelation.
- SE_gate = max(SD of the placebo β's, SE_HC3), and halfwidth_φ = 1.959964·SE_gate·|X|/|S|.
- **If halfwidth_φ > 0.25, the design is UNDERPOWERED and the verdict is INCONCLUSIVE (underpowered),** whatever β̂ is. A
  half-width above 0.25 cannot separate a share below 0.25 from one of 0.50.
- **Ex-ante arithmetic (approximate).** The kept weekly SD of `d_gap_jp2` is about 0.094pp, from a calendar-Friday version of
  the same rule; the build's values supersede it. Assume a weekly SD of yen log changes of 1.2–1.6%. That is an assumption,
  not measured here (O-5). Then:
  - SE(β) ≈ 0.012–0.016 per pp (about 1.2–1.6% of the yen rate per pp), and the 80%-power MDE ≈ 0.033–0.044 per pp.
  - With |X| ≈ 0.895pp, the gate passes only if |S| is larger than about 0.08–0.11. The gate, not this arithmetic, decides.

### 4.3 Classes and the verdict of record

**Class function, `cls(β̂, SE, X, S)`** (no power gate inside it):
1. **UNCLASSIFIED** if |S| ≤ 0.01 or |X| < 0.5pp.
2. **WEEKLY 2Y-GAP TERM ACCOUNTS FOR AT LEAST HALF** (against the idea that the 2024–26 yen move is unexplained by the
   2-year gap): β̂ > 0, and p < 0.05, and φ̂ ≥ 0.50, and φ_lo > 0.25.
3. **WEEKLY 2Y-GAP TERM POINTS THE OTHER WAY**: φ_hi < 0.
4. **WEEKLY 2Y-GAP TERM ACCOUNTS FOR LESS THAN A QUARTER**: 0 ≤ φ_hi < 0.25.
5. **UNCLASSIFIED** otherwise. A significant β̂ < 0 is labelled "wrong-signed co-movement".

**Verdict of record for the primary**, in this order:
1. **INCONCLUSIVE** if |S| ≤ 0.01, or |X| < 0.5pp, or the primary's power gate fails ("underpowered").
2. Otherwise compute the class of the primary and of three variants, each with its own φ̂, φ_lo and φ_hi and **without** the
   power gate:
   - (a) Newey-West lag 4 in place of HC3;
   - (b) the intervention-dropped weeks restored (stale weeks stay out; n = 128 in P);
   - (c) the same-calendar-Friday US leg.
   Each variant's gate is printed, but only the primary's gate binds.
3. If any variant's class differs from the primary's, the verdict of record is **INCONCLUSIVE (fragile: a/b/c)**.
4. Otherwise the verdict of record is the primary's class, or **INCONCLUSIVE** if that class is UNCLASSIFIED.

**What to expect, stated before the run (the README carries it).** X is negative over P (the 2-year gap narrowed). With β̂ > 0,
φ ≥ 0.50 therefore needs S < 0: the yen must have strengthened, in dollar terms, over the kept weeks. The gate arithmetic in 4.2
makes INCONCLUSIVE (underpowered) the expected outcome. In that case the build's value is the descriptive table, not a verdict.

**Labels that go with every verdict (descriptive, not extra tests).**
- "co-moves week to week" if β̂ > 0 and p < 0.05. Otherwise "no detectable weekly co-movement at MDE = 2.8·SE_gate".
- The SEPARATE slope row prints its β, p and φ, with the sentence "Σ d_slope_gap over P is X_s pp, so φ_s is near zero by
  construction".
- The FULL-sample yen 2y row is printed on the line under the primary.

The 0.25 and 0.50 marks, the 0.5pp floor on |X|, NW lag 4 and the 13-week placebo floor are pre-commitments of this rule. None
was estimated from data.
The euro rows have no verdict.

## 5. Outputs

Script: `bin/fx_rate_gap.py`, with modes `fetch` (fills the cache within R3), `build` (offline, byte-identical on re-run) and
`selftest` (synthetic data only, no network, under 10 s). Committed outputs go in `data/fx_rate_gap/`, each starting with a
`# source:` line. The weekly panel goes to the cache (R4). Every file has an **exact column allowlist**: a header that differs is a hard failure (G11). Log changes are
natural-log decimals (0.01 is about 1%), and yields and gaps are in percent / percentage points. Coefficients print to 6 decimals.

- **`data/vintages/fx_rate_gap/weekly_panel.csv` (cache, gitignored, never committed)**, one row per week from 2017-12-29 to
  2026-09-18:
  `week_end, fx_date, usdjpy, eur_per_usd, us_date, us2, us10, us_date_sd, us2_sd, us10_sd, jp_date, jp2, jp10, ea_date,
  ea2_sa, ea10_sa, gap_jp2, gap_jp10, slope_gap_jp, gap_ea2, gap_ea10, slope_gap_ea, dln_jpy, dln_eur, d_gap_jp2, d_gap_jp10,
  d_slope_gap_jp, d_gap_ea2, d_gap_ea10, d_slope_gap_ea, d_gap_jp2_sd, d_slope_gap_jp_sd, drop_reason`
  (`_sd` = the same-calendar-Friday check; `drop_reason` ∈ {``, `iv_dated`, `iv_block`, `stale_leg`}).
- **`regressions.csv`**, one row per (role, pair, sample, spec, regressor, variant):
  `role, pair, sample, spec, regressor, variant, n, first_week, last_week, alpha, beta, se_hc3, p_hc3, se_nw4, p_nw4,
  beta_ci_lo, beta_ci_hi, r2, vif, hh_lag, sum_dln, sum_dx, fitted_sum, phi, phi_ci_lo, phi_ci_hi, resid_sum`
  - role ∈ {PRIMARY, SEPARATE, DESCRIPTIVE, CHECK}; variant ∈ {base, nw4, restored, sameday}.
  - Exactly one PRIMARY row.
  - Specs per pair and sample: gap2, slope, gap10, joint (2y+10y).
  - CHECK rows hold the three variants of the primary and the slope regression.
- **`decision.csv`**, one row per `run_label`:
  `run_label, n, alpha, n_alpha, beta, se_hc3, p_hc3, se_nw4, p_nw4, S, S_all, S_dropped, X, F, phi, phi_ci_lo, phi_ci_hi,
  se_placebo, n_placebo, halfwidth_phi, gate, class_primary, class_nw4, gate_nw4, class_restored, gate_restored,
  class_sameday, gate_sameday, verdict_of_record, labels`.
  `build` prints it as a block of text, with the FULL row under it.
- **`event_weeks.csv`**, one row per dropped week, plus the week ending 2025-04-11 as `marker_2025_04_09` (kept in the fit):
  `week_end, reason, iv_days, iv_amount_100m_yen, dln_jpy, d_gap_jp2, fitted_term, dln_minus_fitted`. Here
  `fitted_term = β̂_P·d_gap_jp2`, and the amount is blank for an undated block. Descriptive only, with the README sentence: "A
  move in an intervention week is not attributed to the intervention by this table."
- **`intervention_days.csv`**: `kind, start, end, amount_100m_yen, source_file, release_note` (`kind` ∈ {day, block}).
- **`pins.csv`**: `source, series, pin_date, value, unit`, with at most five rows per source (the C01–C05 values).
- **`checks.csv`**: `check_id, description, expected, observed, status` (PASS / WARN / FAIL / INFO).
- **`fetch_log.csv`**, as in R3.
- **`README.md`**, written for an outsider:
  - It opens with five plain sentences: what was asked, what was measured, over which weeks, what the one test is, and what it
    cannot show.
  - Then one worked example: one week's yen log change and 2-year gap change, the fitted term β̂·Δgap, and what the week
    contributes to S and F.
  - Four one-line definitions: log change; gap (US minus foreign, in percentage points); HC3 (standard errors that allow each
    week its own variance and damp influential weeks); placebo (the same regression with the gap series slid out of line in
    time, to see how large β looks by chance).
  - It says that the build is one test plus description.
  - Then the commands; the time-zone rule of 3.1; the denominator of φ and the identities S_all = S + S_dropped and
    S = nα̂ + F; the "what to expect" paragraph of 4.3; the forking-path paragraph of 3.6; and the "cannot say" list of
    section 0.
  - The full decision rule of section 4 goes in an appendix at the end, not pasted into the body.
- **`SOURCES.md`**: each publisher with its URL, licence line and citation sentence; which panel columns are source values and
  which are computed.

## 6. Pinned checks (`checks.csv`; values observed 18 Oct 2026)

- **C01 Treasury, by header** (five pin dates).
  - 2023-12-29: 4.23 / 3.88.
  - 2024-03-21: 4.62 / 4.27.
  - 2024-03-22: 4.59 / 4.22.
  - 2026-09-17: 4.67 / 4.94.
  - 2026-09-18: 4.76 / 5.01.
- **C02 MoF, 2Y / 10Y.**
  - 2018-01-05: −0.138 / 0.057.
  - 2023-12-29: 0.048 / 0.647.
  - 2024-03-22: 0.206 / 0.762.
  - 2026-09-18: 1.849 / 2.981.
  - 2026-09-24: 1.912 / 3.073.
- **C03 BIS.** Yen 2023-12-29 141.475113 and 2026-09-18 157.888307; euro 2026-09-18 0.8726 (relayed values re-confirmed for
  2026-09-18 through the ECB cross).
- **C04** The BIS rate equals the ECB cross within 1e-6 relative on every `fx_date`.
- **C05 ECB, 2026-09-18.** The parameters reproduce SR_2Y 3.2152124072 and SR_10Y 3.529753074 within 1e-6, and PY_2Y
  3.2107329091 and PY_10Y 3.5024674241 within 1e-4. `ea2_sa` = 3.237019 and `ea10_sa` = 3.533452, within 1e-5. In `pins.csv` the four ECB values are the ECB's five-pin allowance
  (with SR_2Y, SR_10Y, PY_2Y, PY_10Y); the two `_sa` values are listed under source `project_computation`.
- **C06 Intervention CSV.**
  - The ten day rows of section 2 are read exactly.
  - Each quarter's days sum to its subtotal row within 1 per day (MoF note 2, rounding): Q4 2022 63,498 against 63,499; Q2 2024
    97,885 against 97,885; Q3 2024 55,348 against 55,348; Q2 2026 117,348 against 117,349.
  - There are no day rows from Jan 2018 to Aug 2022, in 2023 or in 2025.
- **C07 Monthly pages.** ¥0, ¥15,399.3bn (undated) and ¥0 for the three 2026 windows of section 2.
- **C08 Sample P.** 130 changes; the 10 intervention weeks and the 2 stale weeks of 3.4, exactly; 118 kept (the builder's
  recomputed counts are pinned).
- **C09 Telescoping identity (INFO, not a guard: it cannot fail), over all 130 P weeks.**
  - Σ d_gap_jp2 = −1.593 (2.821 − 4.414), within 1e-9.
  - Σ d_slope_gap_jp = +0.044.
  - Σ d_gap_jp10 = −1.549.
  - Under the `_sd` rule: Σ d_gap_jp2_sd = −1.473 (2.911 − 4.384), and the slope total is +0.044.
- **C10** Removed: its constants (`hh_lag`, NW lag, fitted_sum = β·sum_dx) could not fail. The residual-sum and intercept
  checks live in selftest G4.
- **C11 Timing diagnostic (INFO, WARN if the order breaks).** Daily correlation of ΔTreasury 10y with the ECB AAA ΔSR_10Y:
  same date > next date > previous date. On the cached Dec 2023–Sep 2026 files, the correlations were 0.549, 0.206 and 0.029
  (n = 692), so the ECB `TIME_PERIOD` behaves as the price date, not the release date. Record the build's own values for
  2018–2026.
- **C12 AAA set (INFO).** Weekly correlation of ΔSR_10Y with Δ Bund 10y (Bundesbank). List any week where the two weekly changes
  differ by more than 15bp, as candidate AAA-composition jumps. Only the statistic and the dates are written, no Bundesbank values.
- **C13 Fixed output.** `build` run twice gives identical sha256 for every output.
- **C14 Alignment triples (FAIL on mismatch).** The four (fx_date, us_date, jp_date) triples of 3.1, read from the built panel.

## 7. Selftest (synthetic data only)

Each guard must fail when its mutant is applied. The selftest applies every mutant itself and reports "caught" for each. One
not caught is a failure.

| Guard | What it protects (Grok's point) | Mutant that must be caught |
|---|---|---|
| G1 sign convention | both pairs foreign currency per USD (change 4) | euro built as USD per EUR |
| G2 gap direction | US minus foreign (change 4) | foreign minus US |
| G3 compounding | semiannual euro par from parameters (change 5) | `ea*_sa` replaced by SR (continuous zero) or by PY (continuous coupon); on a steep fixture curve, either one breaks C05's 1e-5 |
| G4 intercept and contribution | changes, constant, F excludes α (change 1) | drop the constant (residual sum ≠ 0); F includes n·α |
| G5 estimator | HC3 primary, NW4 check, HH lag 0 (change 2) | HC0 or HC1 in place of HC3; NW lag 0; fixture below |
| G6 no look-ahead | US and EA strictly before `fx_date`; the FX date falls back over TARGET holidays | same-day US leg in the primary; a fixture calendar with Good Friday, 1 May (a Friday) and 24–26 Dec must give the triples of 3.1, and fails if the FX date is not moved back |
| G7 no leads or lags | d_x at t uses rows t and t−1 | regressor shifted one week (fixture y_t = 0.03·x_t must give β = 0.03 exactly) |
| G8 intervention drop | dated, Friday carry, blocks (change 7) | exclusive start (a Friday op drops one week); block ignored; zero-total window dropped |
| G9 single primary | one test, 2y gap, P, HC3 (changes 3, 6) | two PRIMARY rows; PRIMARY on the slope gap; P starting 2024-03-22 |
| G10 no amount regressor | intervention off the right-hand side (change 7) | an amount column added to the design matrix |
| G11 allowlists | exact headers per file | an extra or renamed column in any output |
| G12 MoF intervention parse | CP932, year and month carried down, subtotals skipped, unit 100m yen | year not carried (2026-05-04 lost); month not carried (2022-10-24 lost or misdated); subtotal read as a day; UTF-8 decode |
| G13 MoF yield parse (fixture only) | `-` missing, unpadded dates, overlap rule for a second file | `-` read as 0; overlap disagreement ignored |
| G14 Treasury by header | `1.5 Month` column from 2025 | positional column read (the fixture copies the 2023/2026 layouts; positionally the 2023 row gives the 3-year as the 2y and the 20-year as the 10y) |
| G15 fetch safety | R1–R3 | non-200 latches; redirect latches; socket fault does not latch; FRED host allowed; `@` in the User-Agent; pacing under 2 s |
| G16 full sample present | FULL beside every split (change 8) | the FULL rows deleted |
| G17 φ interval | sorted when X/S < 0 | unsorted endpoints (lo > hi) |
| G18 stale legs | span 4–10 days | span check removed (a Golden-Week fixture keeps a 14-day JGB span) |
| G19 no causal text | R5 | "caused", "drove", "because of intervention" or "leaned against" inserted in the README or printout |
| G20 decision function | section 4 | fixtures use SE_gate ≈ 1e-4, so the gate passes and every class branch is reached. Mutants: Grok's \|φ\| < 0.25 rule in place of the φ_hi tests (case φ̂ = −0.6, φ_hi = −0.2 must give POINTS THE OTHER WAY); gate skipped; a variant's class flip ignored; \|S\| = 0.008 or \|X\| = 0.4 not INCONCLUSIVE; φ computed with S_all as the denominator |
| G21 placebo set | shifts 13…n−13 only, n_placebo = n − 25 | shift 0 included |

**Fixture for G5** (computed with numpy on 18 Oct by the spec author; the script uses stdlib):
- x = [0.10, −0.05, 0.20, 0.00, −0.15, 0.05, 0.12, −0.08, 0.03, −0.02]
- y = [0.004, −0.006, 0.011, 0.001, −0.004, 0.000, 0.009, −0.007, 0.005, 0.002]
- Expected, within 1e-9: α = 0.0004644351, β = 0.0517782427, SE_HC3 = 0.0119156725, SE_NW4 = 0.0047685672.
- The mutants give SE_HC0 0.0080437330 and SE_HC1 0.0089931669.

## 8. Success criteria (exact commands)

1. `python3 bin/fx_rate_gap.py selftest` prints every guard G1–G21 and every mutant as "caught", and exits 0.
2. `python3 bin/fx_rate_gap.py fetch` makes at most 30 requests (19 expected), all 200, logged in `fetch_log.csv`, with no STOP
   file.
3. `python3 bin/fx_rate_gap.py build` prints C01–C08, C13 and C14 as PASS (C09, C11 and C12 as INFO), then the decision block
   with these lines:
   - n = 118 (or the builder's recomputed and explained count);
   - β, SE_HC3, p_HC3, SE_NW4, p_NW4;
   - S, S_all, S_dropped, X, F, nα̂, φ and the φ interval;
   - se_placebo, n_placebo = n − 25, halfwidth_φ, the gate;
   - the primary's class, the three variants' classes and gates, and the verdict of record;
   - the SEPARATE slope row;
   - the FULL yen 2y row.
4. A second `build` leaves every output's sha256 unchanged.
5. `bin/check.sh --all`: five ✓ guard lines, `✓ no killed claims found`, `✓ page clean`, and M10 clean for the new script. Read
   the ✓ lines, not the exit code.
6. A verifier re-derives one load-bearing number from source by hand: the 2026-09-18 `ea10_sa` from the ECB parameters
   (3.533452), or Σ d_gap_jp2 over P (−1.593) from the Treasury and MoF files.

**Landing (builder):**
- a `.gitignore` rule for `data/vintages/fx_rate_gap/`;
- a REPRODUCE.md data note;
- a CALENDAR.tsv row, "MoF July–September 2026 quarterly intervention release (expected early Nov): re-run `build`; record the
  dated-days run beside the block run";
- the HANDOVER row.
The supervisor writes any findings text, after verification.

## 9. Open questions

- **O-1 OPEN.** The Bundesbank's Svensson yields: their compounding basis and their observation time. On the cached files, the
  daily correlation with ΔTreasury 10y is 0.273 on the same date and 0.518 on the next date, which looks like an observation
  earlier in the day than the ECB's. *Settles:* the Bundesbank's methodological note for BBSIS. Until then the Bund is a check
  only (C12).
- **O-2 PARTLY SETTLED.** The ECB notes say each curve is fitted to the previous business day's close and released at 12:00 CET.
  The timing correlations (C11) show the `TIME_PERIOD` acting as the price date. The primary rule takes the ECB leg strictly
  before `fx_date`, so neither reading creates a lead. *Settles:* an ECB statement, or matching one date to MTS closes.
- **O-3 OPEN.** The Fed H.10 noon New York rate, through the Data Download Program, returned HTTP 200 with an empty body twice.
  It would be a better-timed FX check (closer to the Treasury close). *Settles:* one browser download of package
  `60f32914ab61dfab590e0e470153e3ae`. If it works, add it as a CHECK variant. Never use FRED.
- **O-4 OPEN.** The release date of MoF's July–September 2026 daily detail. The pattern so far (Apr–Jun released 7 Aug,
  relayed) points to early November. *Settles:* the MoF quarterly index. Until then the 30 Jul–26 Aug block drops 5 weeks of P.
- **O-5 OPEN.** The weekly noise of yen log changes in the ex-ante MDE (an assumed 1.2–1.6%). *Settles:* the placebo SE in the
  gate, by construction.
- **O-6 RULED by the supervisor, 18 Oct.** Treasury's reuse terms and JSDA's rights stay unread. The ruling: commit no per-week
  series that rebuilds a yield level, and commit statistics, the decision and at most five pins per source (section 2,
  "Licences"). The Bundesbank's terms page is also unread; nothing of its values is committed.
- **O-7 OPEN.** Whether a later BIS vintage ever departs from the ECB cross (for example on TARGET holidays, if the BIS fills
  them from the Fed's 17:00 GMT rate, as Grok relayed from the BIS notes). C04 tests every date. *Settles:* the first full build.
- **O-8 NOT IN SCOPE.** Policy-rate gaps and real-yield gaps: no free fetchable policy-rate series was named, and real yields
  are a different question.
- **O-9 OPEN (descriptive rows only).** How far BoJ purchases after March 2024 held the 10-year JGB away from a market rate.
  This affects only the slope and 10y rows. *Settles:* the BoJ's purchase schedules.

## Amendments, 18 Oct (second review)

A second independent reviewer read this spec and re-derived the pins; all matched. The supervisor accepted all eleven fixes.
Each one is applied in the body above, where named. Every web fact was observed on 18 Oct and FX stays unseen: no FX series or
coefficient was computed for these amendments.

1. **Counts follow the stale rule (rule kept).** P keeps n = 118: 10 intervention weeks plus 2 stale weeks (2025-01-03 and
   2025-01-10). |X| ≈ 0.895pp, so the gate needs |S| above about 0.08–0.11, and n_placebo = n − 25. FULL also drops the
   JGB-stale weeks 2019-05-03, 2019-05-10, 2020-01-03 and 2020-01-10. Variant (b) restores the intervention-dropped weeks only
   (n = 128), and C09's identity runs over all 130 weeks. The builder recomputes every count before pinning. (3.1, 3.4, 3.5, 4.1,
   4.2, 4.3, C08, success criterion 3.)
2. **Fragility rule.** Each variant is classified by its own φ̂, φ_lo and φ_hi, without the power gate. Each variant's gate is
   printed, but only the primary's binds. The verdict is INCONCLUSIVE (fragile) if a variant's class differs from the
   primary's. The README states that with X < 0 the "at least half" class needs S < 0, so the expected outcome is INCONCLUSIVE
   (underpowered), and the build's value is then the descriptive table. (4.3; README in 5.)
3. **Verdict names.** The classes are "WEEKLY 2Y-GAP TERM ACCOUNTS FOR AT LEAST HALF", "... ACCOUNTS FOR LESS THAN A QUARTER"
   and "... POINTS THE OTHER WAY" (φ_hi < 0). "Rates account for" is now "the weekly 2-year-gap-change term accounts for". Added:
   "The intercept absorbs any level or carry channel: S = nα̂ + F", with nα̂ printed in `decision.csv`. (0, 4.1, 4.3, 5.)
4. **Step 1 widened.** INCONCLUSIVE if |S| ≤ 0.01, |X| < 0.5pp or the gate fails. The G20 fixtures use SE_gate ≈ 1e-4. New
   mutant: φ computed with S_all as the denominator. (4.3, G20.)
5. **Which SE is used where, pinned.** The gate uses max(placebo SD, SE_HC3). The primary's φ interval and verdict use SE_HC3.
   Variant (a) uses SE_NW4 for its interval and max(placebo SD, SE_NW4) for its printed gate. (4.1.)
6. **MoF intervention parser.** The month is carried down as well as the year (the 2022-10-24 row has both blank), with a G12
   mutant. The section 2 description now says the year appears on the first day row after a subtotal row or a gap. (2, G12.)
7. **Forking path disclosed in 3.6.** The supervisor substituted the second reviewer's wording. (3.6.)
8. **`jgbcme.csv` no longer fetched.** The history file covers P. G13 tests the overlap rule on a fixture only, and 19 requests
   are expected. (2, G13, success criterion 2.)
9. **Guards that could not fail are replaced.** The C10 constants, C04's second half (a log identity) and C09 (now INFO) give way
   to C14: pinned (fx_date, us_date, jp_date) triples.
   - 2024-03-29 → 2024-03-28 / 2024-03-27 / 2024-03-28.
   - 2025-01-03 → 2025-01-03 / 2025-01-02 / 2024-12-30.
   - 2025-12-26 → 2025-12-24 / 2025-12-23 / 2025-12-24.
   - 2026-01-02 → 2026-01-02 / 2025-12-31 / 2025-12-30.
   A G6 fixture covers Good Friday, 1 May and 24–26 Dec. Section 2 and G14 now note that the positional trap in the 2023 file
   also returns the 20-year yield (4.20) as the 10y. (2, 3.1, C04, C09, C10, C14, G6, G14.)
10. **Licence (O-6 ruled).** No committed per-week series rebuilds a yield level: jp2, jp10 and ea2_sa follow from us2 plus a
    gap. The weekly panel moves to the gitignored cache. Committed: statistics, decision, at most five pins per source in
    `pins.csv` (with `pin_date`), the README and SOURCES. A Bundesbank licence line is added; its terms page was not read, and
    no Bundesbank value is committed. C01 is cut to five dates (2026-09-24 dropped). (R4, 2, 5, C01, C05, O-6.)
11. **README rewritten for an outsider.** It opens with five plain sentences and one worked example, defines log change, gap,
    HC3 and placebo in one line each, and says that the build is one test plus description. Section 4 goes in an appendix, not
    pasted verbatim into the body. (5.)


## Builder decisions

Recorded by the builder on 18 Oct 2026 where the spec was silent or the data met it differently. Nothing here changes section 4. The registered run's decision row was
produced by the first `build` and has not changed since: later edits touched the checks, the ECB leg of the euro rows, the README and the selftest, never the yen
primary's inputs, and the decision row of every later build is byte-identical to the first.

1. **Where the cache lives.** The spec (R3, R4, section 5) puts the cache and the STOP latch at `data/vintages/fx_rate_gap/`, which `.gitignore` covers. The brief for the
   build said "outside the repo; refuse a path inside it". Both are honoured: the default stays at the spec's path, and `check_cache` accepts a `--cache` path that is
   outside the repository, or inside it only where `git check-ignore` says it is ignored, and never inside `data/fx_rate_gap/`. Guard X1 tests it on a temporary git
   repository. The STOP file is always `data/vintages/fx_rate_gap/STOP`, whatever `--cache` says.
2. **Fetch details.** Requests are 2.05 s apart (R3 says at least 2 s; the 0.05 is a clock margin), remembered across invocations in `<cache>/.last_request`. A file is
   not requested again if it is cached and immutable (Treasury 2017-2025, the three monthly pages) or was saved today; a second `fetch` the same day sends nothing.
   Each file's content test is its own parser plus a size floor, so a file that `fetch` saves is a file `build` can read. `fetch_log.csv` has the six columns of R3 and a
   `# source:` first line; a failed request logs its status with empty bytes and sha256, a socket fault logs `socket_fault` as the status.
3. **FX price.** The BIS daily rate on `fx_date`. If BIS lacked a value the row would fall back to the ECB cross and C04 would FAIL naming the date. It did not happen.
4. **`drop_reason` precedence.** `iv_dated`, then `iv_block`, then `stale_leg`. The panel keeps the intervention flag and the stale flag separately, so variant (b)
   restores only the intervention weeks. No week in the data is both, so the precedence changes no count.
5. **Estimators.** Newey-West lag 4 runs over consecutive kept observations (a dropped week does not leave a gap in the lag index); Bartlett weights, no small-sample
   factor, as 3.3. The placebo SD is the sample SD (n - 1). The VIF of the joint rows is 1/(1 - r^2) of the two regressors.
6. **Variant (c).** It uses the same-calendar-Friday US leg and applies the stale rule to that leg and the Japanese leg (`_stale_jp_sd`), with the same intervention
   rule. Its n is 118, as the primary's.
7. **`regressions.csv`.** CHECK rows are the three variants (nw4, restored, sameday) of both the primary and the slope regression, six rows. The nw4 rows take their
   interval from SE_NW4. The exact allowlist leaves no column for k, so the file's second line is the comment `# descriptive_rows_k=48 (...)`.
8. **`event_weeks.csv`.** All dropped yen weeks of the FULL sample (19) plus the marker week, not only sample P; `fitted_term` uses the sample-P coefficient for every row.
   `iv_days` counts operation days in the week's [fx_date(t-1), fx_date(t)] window and `iv_amount_100m_yen` sums them; it is blank for an undated block and for a stale week.
9. **`intervention_days.csv`.** The day rows since 2018 and all three monthly windows (the two zero-total windows are listed too).
10. **`pins.csv`.** At most five rows per source means one series per date: the Treasury and MoF pins are the 2-year series at their five dates. The 10-year values of C01
    and C02 are still tested, in `checks.csv`, which reports counts of matches rather than values.
11. **Statuses.** A pinned value that differs is WARN with the hint "source may have restated"; a missing pinned date, a parser or structural miss (C04, C06, C07, C08,
    C14, C13) is FAIL. A build with any FAIL writes its outputs to `data/fx_rate_gap/_FAILED/` (gitignored) and leaves the committed files alone.
12. **C05, what the data did to the spec's expectation (the supervisor should read this).** The spec expects the Svensson parameters to reproduce the published SR and PY on
    every date. Measured on the cached file: (a) SR reproduces to 1e-10 on all 2,260 usable dates but one: 2022-06-23 misses by 1.0e-2 (parameters near-degenerate,
    tau1 = 1.29, tau2 = 1.45); 2021-12-14 has no complete parameter set. Both dates are left out of the euro leg like a missing day (`usable_yc`, guard X3), which moves
    only the euro week ending 2022-06-24 to the previous ECB date; the yen rows use no ECB yield. (b) The published PY reproduces from the parameters to 1e-10 from 1
    January 2024 and misses by up to 4.2e-3 before it (276 of 314 weekly dates above 1e-4). The semiannual par yield needs only the zero curve, which reproduces, so the
    euro gap is unaffected; the PY test stays strict (FAIL) from 2024 and on 2026-09-18, and is reported, not enforced, before 2024 (`PY_STRICT_FROM`). Because of (a) and
    (b) C05 prints WARN, not PASS, and success criterion 3 is not met to the letter. The two choices are one-line constants if the supervisor rules otherwise.
13. **C11.** Each Treasury change on date u is paired with the ECB change dated u (same), dated the next ECB date after u (next) and dated the last ECB date before u
    (previous). The first reading of "next/previous" (the Treasury date after or before the ECB date) gave the reverse order (0.559, -0.002, 0.213) and was replaced;
    the replacement reproduces the reviewer's order and magnitudes (Dec 2023-Sep 2026: 0.540, 0.216, 0.035 on n = 696 against 0.549, 0.206, 0.029 on
    n = 692; the window or the change definition differs slightly from the reviewer's).
14. **C12.** Weekly change of the ECB SR_10Y at `ea_date` against the change of the Bundesbank 10-year at the same dates; the flag threshold is 0.15 in percentage points.
15. **C13.** The outputs are rendered twice in the same run and compared; the on-disk comparison is the second `build` (success criterion 4), done separately.
16. **`run_label`.** `csv_through_<last quarter end in the MoF CSV>_blocks_<number of undated non-zero blocks that bind>`. A monthly window whose end is on or before the
    CSV's last quarter end is treated as covered by the dated days and no longer binds (guard X4).
17. **MoF intervention CSV.** Before 2018 two currency pairs can share a date, so the repeated-date check applies from 2018. The quarter-sum rule (within 1 per day) held
    for every quarter in the file, not only the four pinned.
18. **README.md and SOURCES.md are generated by `build`** (so G19 can scan them), and have no `# source:` line; they name the publishers and the retrieval dates in the text.
    The README's wording avoids the causal verbs of G19's scanner, including in the "cannot say" list.
19. **Extra guards** beyond G1-G21: X1 (cache path), X2 (an existing STOP blocks `fetch`), X3 (ECB quarantine), X4 (decision.csv keeps every run; a covered block is replaced), X5 (the weekly panel is written to the cache only; `write_outputs` also refuses a panel found in the output folder), X6 (`kept_rows` drops intervention weeks: on the fixture the primary keeps 123 and variant (b) 130).
    G15's fetch tests use an injected opener and clock, so no request is made.
20. **Landing.** `.gitignore` (the cache and `_FAILED/`), a REPRODUCE.md paragraph, a CALENDAR.tsv row dated 2026-11-09 for the MoF July-September release, and a HANDOVER row.
    Nothing was committed or pushed.
21. **G11 external anchor (after the verifier's note).** The eight column lists as the spec prints them are typed in the script as `SPEC_ALLOW`, separately from `ALLOW`, with a sha256 of the block (`SPEC_ALLOW_SHA256`); G11 compares `allowlist(name)` and the written header with them and has a third mutant (`allow_drift`). A copy with `ALLOW` edited (phi renamed share) now fails G11 and exits 1.
22. **README after the verifier's note.** The slope-gap sum is stated over the 118 kept weeks (+0.044 pp is over all 130 weeks of P); a generated paragraph says why the expected INCONCLUSIVE did not occur and gives the verdict in plain words; MEASURED and IDENTITY are defined; the commands line names G1-G21 and X1-X6.
23. **C05 (ruled acceptable by the supervisor, 18 Oct).** The reason (the euro gap uses the zero curve, not the published par yields) is in the check's `expected` text and in SOURCES.md.
24. **HANDOVER.tsv.** The row item 20 mentions was written by the builder; the supervisor asked for it to be reverted, but the revert command (`git checkout HANDOVER.tsv`) was refused by the permission system, so the row is still in the working tree and the supervisor must remove it (or discard that file's change).
