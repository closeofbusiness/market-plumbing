# Spec: Japan's yield rise split into term premium and expected rates, on Nakajima's free decomposition (spec author, 19 Oct 2026; rewritten after rounds 2 and 3)

*CALENDAR.tsv row 2026-11-03 (revised 19 Oct); Grok batch g8, return 4, in `_research/2026-10-19-Grok-G8-Returns.md`. House style
follows `_research/2026-10-19-FX-Hedged-Treasury-Yield-Spec.md`. This text folds in the supervisor's rulings of 19 Oct: round 1
(O-3, O-4), round 2 (the second review's ten fixes, R2-1 to R2-10) and round 3 (Grok's attack, R3-1 to R3-8). They are recorded at
the end and the body is authoritative. "Observed" means seen on 19 Oct 2026 with one request per URL and the CLAUDE.md non-SEC
User-Agent: 11 requests, all HTTP 200, no redirects, nothing refused. "Relayed" means taken from Grok or the supervisor and not
re-read here. The spec author computed no shares. The shares quoted below were re-derived by the supervisor (round 3) or by the
second reviewer (round 2) from the cached files, and the builder reproduces them as pins.*

## 0. Goal, and what the result can and cannot say

- **Split** the change in Japan's 10-year government bond yield from December 2023 to September 2026 into the change in the expected
  path of short rates and the change in the term premium, as published by Jouchi Nakajima (`yield_M.csv`). Classify it with the
  CALENDAR rule as amended by R3-1, so that no share from 0.40 to 0.60 is given a "larger" label.
- **Repeat** the same split for 2, 5 and 20 years and over fixed sub-windows. **Set it beside** the author's own daily file, Japan
  Macro Advisors' file (in numbers) and the BoJ Review 2026-E-10 (in words, with no agree or disagree label).
- **Record** the vintage of every input, never mix vintages, and show how much one revision moves the answer.

**It can say:** on this model and this vintage, what share of the window's yield change is term premium. That share is s = dTP/dy,
where dy is the change in the monthly-average 10-year constant-maturity yield. It can also say how far s sits from one half, in basis
points of yield change, and how far the other estimates disagree. Grades (E-007):
- dy is MEASURED (MoF yields);
- dER is a MODEL ESTIMATE, HYPOTHESIS grade and model-dependent;
- dTP = dy − dER is a **residual** (C-098), so every error in the model's expected path lands in it;
- s is IDENTITY given dER and dy.

**It cannot say** why yields rose, or that purchases, flows or positions moved any price. It does not test the project's breakeven
split (C-126). That split divides the nominal yield into inflation compensation and the real yield, and this split cuts across it:
expected inflation sits inside expected nominal rates, and an inflation risk premium sits inside the term premium.

Model term premia depend on the model:
- the cited model holds the long-run short rate constant (R3-4, section 5);
- Japan Macro Advisors states that standard models "significantly overestimate the premium" (observed);
- the author's own monthly and daily files already disagree: second reviewer, full-window 10-year share 0.54 monthly against 0.44
  daily.

Required README sentence: **"This is one model's split of the yield change. Other models split it differently, and it does not show
why yields rose."**

## 1. Hard requirements

- **R1. Free public data only (E-005).** No FRED, no sec.gov, and no API key or token: GitHub's API is used unauthenticated.
  - Host allowlist for `bin/japan_term_premium.py`: `raw.githubusercontent.com`, `api.github.com`, `sites.google.com`,
    `takujiokubo.github.io`. Any other host is refused before the request.
- **R2. User-Agent** exactly `Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)`.
  - Assert there is no `@` in it, and it must pass `bin/check.sh` M10.
  - Never send an email address, a name, `SEC_UA` or `CLAUDE_CODE_USER_EMAIL`.
- **R3. Polite, refusal-safe fetches.**
  - GET only, sequential, at least 2 s apart, at most 15 requests per run (11 expected), and no redirect followed.
  - Any status other than 200, or a body that fails its content test (section 2), writes `<cache>/STOP` and ends the run.
  - **HTTP 403 or 429 from GitHub is reported as rate limiting, never as "file absent"** (R2-8). It still latches.
  - **Only a person deletes STOP.** No agent deletes it, even when the agent believes its own content test was wrong (the last build
    deleted its latch twice): the agent stops and reports. `fetch` refuses to start while STOP exists.
- **R4. Raw files stay outside the repository.**
  - Default cache `~/jgb_term_premium_cache/`. `--cache DIR` must resolve outside the repo root, or the script refuses (the ICE and
    DTCC precedent).
  - Nakajima's files are never committed, in any form or under any name.
  - Raw JMA files also stay in the cache.
- **R5. raw.githubusercontent.com URLs are commit-pinned** (`/<40-hex commit>/yield_M.csv`), never `/main/`, so a vintage cannot
  change under the build.
- **R6. One vintage per statistic.** Every committed row carries `vintage_id`. A statistic is computed from exactly one file version,
  and months are never filled from another vintage (section 3.6).
- **R7. No causal language** in README, SOURCES or printout (G13). The required sentence passes the guard.
- **R8. Stdlib only, new script.** The only edit to an existing file is the warn-only guard M16 in `bin/check.sh` (section 6; R2-3).
  The MoF file is read and never written.
- **R9. Post-registration fixes keep the old values.** A rebuild on the same vintage that changes a frozen value fails, unless it is
  run with `--amend "<reason>"`. That appends the new row and marks the old one `superseded`; it never deletes it (G18).
- **R10. Byte-identical rebuilds** (R2-6). Every timestamp in a committed file comes from the cache (`fetch_log.csv`, commit dates),
  never from the clock.

## 2. Data

| Source | Request (observed 19 Oct) | Fields, units | Timing, vintage | Observed |
|---|---|---|---|---|
| Nakajima monthly | `raw.githubusercontent.com/jouchinakajima/program/<sha>/yield_M.csv` | 14 columns; see "Parsing" below; percent | "updated every quarter. The past figures are subject to updates" (page) | 200, 38,153 bytes, 381 data rows 199501–202609, no blanks; sha256 `4455f00a…0538896`; git blob `c68b8d57f3deeb9528de62a15e1dbfb1216a3c8b` |
| Nakajima daily | same repo, `yield_D.csv` | same columns, first column `YYYYMMDD` | as above | 200, 784,130 bytes, 7,785 rows 19950104–20260930; sha256 `3f570a2a…7152456`; blob `372d5edb5279903aecf8a694859715e25bb78bbf` |
| Vintage list | `api.github.com/repos/jouchinakajima/program/commits?path=yield_M.csv&per_page=100` (and `path=yield_D.csv`) | `sha`, `commit.committer.date` | one commit per upload | 9 commits, the newest **2026-10-06T00:48:15Z `33118433fe95b51be374b5179a80978d59ac4ee9`** (list in 3.6) |
| Blob identity | `api.github.com/repos/jouchinakajima/program/contents/<file>?ref=<sha>` | `sha` | — | the listing's sha equals `git hash-object` of the raw bytes, for both files |
| Nakajima page | `sites.google.com/site/jnakajimaweb/yield` | text and hrefs | — | 200. "From 1995/Jan. to 2026/Sep. (updated in 2026/Oct.)", split across tags, so strip whitespace before matching. **The two links are `https://github.com/jouchinakajima/program/blob/main/yield_M.csv` and `.../yield_D.csv`** |
| Previous vintages | raw `yield_M.csv` at `80f7108a1637ac71d62a30fe97a7ce8a3bc88046` (2026-07-06) and `8f940a0141eefc0d63a426ae5b3a2f6c11e236d0` (2026-04-20) | as monthly | — | July vintage observed: 200, ends 202606; its 202312 row is identical to October's; 202606 TP10 1.072 and ER10 1.5821 (October: 1.0898 and 1.5643) |
| JMA curve | `takujiokubo.github.io/jma-data/jgb-yield-curve-main/data/curve-panel.csv` and the page `.../jgb-yield-curve-main/` | `YM` (YYYY-MM), `Type` (`actual` or `forecast`), `Yield_kY, RN_kY, TP_kY` for k = 2, 5, 10, 20, 30, 40; percent; **spot (zero-coupon) yields** | page: "Model vintage: October 2026, origin September 2026" | 200 without a login, 64,381 bytes, sha256 `23d7c109…f9dc42cf`; 327 rows: actual 2002-07 to 2026-09, then 36 forecast rows to 2029-09; 2026-09 Yield_10Y 3.0656, RN 2.3281, TP 0.7375 |
| MoF JGB yields (already cached) | read-only: `data/vintages/hedged_ust_yield/mof_jgbcme_all.csv` (the same bytes are in `data/vintages/fx_rate_gap/`); `--mof PATH` overrides | **constant-maturity yield, semiannual compounding, percent, `-` for missing** (MoF Q&A; R3-6); `Date` as `YYYY/M/D`; skip the title row | published the next business day | ends 2026/9/30; 10Y 3.057 on 30 Sep 2026; September 2026 mean 2.9922 (19 days); December 2023 mean 0.6861 (21 days) |
| BoJ Review 2026-E-10 (words only; the script does not fetch it) | `www.boj.or.jp/en/research/wps_rev/rev_2026/rev26e10.htm` and `.../data/rev26e10.pdf` | Chart 3, "cumulative chg. from Aug. 2024"; "Data are as of end-June 2026"; model Imakubo and Nakajima (2015); sources Bank of Japan, Bloomberg, Consensus Economics | Aug 2026 | both 200; from summer 2024 "both factors have contributed to roughly the same degree" |

**Parsing (R3-5).**
- The real header is quoted: `"YYYYMM","ShadowRate","TermPremium-2Y","TermPremium-5Y","TermPremium-7Y","TermPremium-10Y",
  "TermPremium-15Y","TermPremium-20Y","ExpectedRate-2Y","ExpectedRate-5Y","ExpectedRate-7Y","ExpectedRate-10Y","ExpectedRate-15Y",
  "ExpectedRate-20Y"`. The daily file's first field is `"YYYYMMDD"`.
- Read with the `csv` module, which removes the quotes, and look columns up **by name**.
- Cells may be in scientific notation, for example `-1e-04`. A cell is valid if Python's `float()` parses it. **A 4-decimal pattern
  test is a defect** (G8).
- The fitted-yield tolerances below assume values given to 4 decimals, and a scientific-notation cell such as `-1e-04` meets that.

**What the data turned out to be (re-derived; the builder pins it).**
- **TP + ER equals the MoF monthly-average constant-maturity yield.**
  - September 2026: TP10 + ER10 = 1.1768 + 1.8154 = 2.9922, the MoF September mean.
  - December 2023: −0.0583 + 0.7444 = 0.6861, the MoF December mean.
  - September 2026 at the other tenors, file sum against MoF mean: 2Y 1.8725 / 1.8724, 5Y 2.3232 / 2.3233, 7Y 2.5634 / 2.5634,
    15Y 3.5259 / 3.5259, 20Y 3.8185 / 3.8185.
  - So the units are percent, and each monthly value is a **monthly average, not a month-end**: the September month-end 10Y is
    3.057, a gap of 0.0648.
  - The published term premium is therefore the observed yield minus the model's expected path (inferred; O-1). The fitted-yield
    check has a gap of 0.0000 at 10Y on both dates. It confirms the basis and cannot test the model's fit.
- **The daily file is a separate estimate, not the monthly file at daily frequency.**
  - 30 Sep 2026: TP10 1.0082 + ER10 2.0488 = 3.0570, the MoF value that day.
  - The mean of the 19 daily TP10 values in September 2026 is 1.0090, against 1.1768 in the monthly file.
- **Vintages revise recent months.** Between the July and October 2026 vintages, 202606 TP10 moved +0.0178 and ER10 −0.0178;
  202312 did not change.
- **The Sites attachment question is settled.** The page links to the GitHub file on `main`, so the GitHub file is the page's file,
  and the vintage is the commit.
- **Not used:**
  - Krippner (LJKmfa): the workbook link was not recovered;
  - Ye: ends July 2022;
  - `trtms.csv`: undefined (relayed);
  - the BoJ purchase-effect regression contributions, which would put a flow next to a price.

**Licences (observed 19 Oct, plus R3-7).**
- **Nakajima.**
  - The page says: "Cite the below articles when using this dataset"; "estimated and released by J. Nakajima within his research
    activity"; "not the official view of the Bank of Japan". The database page says use is "at users' own risk".
  - **His GitHub repository has no stated licence**: the API's licence field is null (supervisor, 19 Oct). This repository's own CC BY 4.0 licence (`LICENSE`) does not extend to his file (R4-1).
  - Commit only derived statistics (section 6), with both citations:
    - Ichiue, H., and Y. Ueno (2013), "Estimating term premia at the zero bound: An analysis of Japanese, US, and UK yields", BoJ
      Working Paper 13-E-8;
    - Nakajima, J. (2025), "Impact of US monetary policy spillovers and yield curve control policy", Discussion Paper A.760,
      Institute of Economic Research, Hitotsubashi University.
- **JMA.** "free to use and reproduce with attribution to Japan Macro Advisors" (live page, re-fetched by the supervisor 19 Oct).
  "Details of the yield curve model are proprietary", and updated estimates are for paid users. The README says both. Raw files stay
  in the cache either way.
- **MoF.** PDL 1.0 (relayed from the hedged-yield spec).
- **BoJ Review.** Quoted in fewer than 15 words, with credit.

## 3. Method

### 3.1 Changes, the share and its distance from one half

For a variant v, a tenor k and a window w = (start month a, end month b), using the values in months a and b. **The base is the
first named month** (ruling O-3).
- d_tp = TP_k(b) − TP_k(a), and d_er = ER_k(b) − ER_k(a).
- **d_yield = d_tp + d_er** (IDENTITY). For M this equals the change in the MoF monthly-average yield (C05).
- tp_share s = d_tp / d_yield, computed unrounded and committed to 4 decimals. **`tp_share` is blank when the window is not
  classified** (R2-5).
- **distance_bp = (s − 0.5) × d_yield × 100**: basis points of yield change away from an even split (R3-1). Blank when `tp_share` is
  blank.
- `opposite_signs` = yes when d_tp and d_er have opposite signs; s then lies outside 0 to 1. The rule is applied literally.

### 3.2 The decision rule

Original text, CALENDAR row 2026-11-03: "window 2023-12 to 2026-09; dy = d(ExpectedRate-10Y + TermPremium-10Y); if dy < 0.25 do not
classify; s = dTP/dy: above 0.50 the larger part is term premium, below 0.50 expected rates, 0.40-0.60 flagged close to even."

**As amended by R3-1, before any data run. This is the rule the build applies:**

| Condition (checked in this order) | `classification` |
|---|---|
| dy < 0.25, including any negative dy (dy = 0.25 classifies) | `NOT_CLASSIFIED`, with `tp_share` and `distance_bp` blank |
| the BRIDGE window | `NOT_APPLICABLE` |
| 0.40 ≤ s ≤ 0.60, inclusive at both ends | **`CLOSE_TO_EVEN`**: no "larger" label inside the band |
| s > 0.60 | `TERM_PREMIUM_LARGER` |
| s < 0.40 | `EXPECTED_RATES_LARGER` |

- The registered row stays M-10Y-FULL.
- Under the original wording, the supervisor's October reading (s = 0.5356) was "term premium larger, close to even". Under the
  amended rule it is `CLOSE_TO_EVEN`, with distance_bp +8.2. The old reading is kept here for the record (R9).
- **Headline reading (R2-2):**
  - `close_to_even_and_model_dependent` when the monthly (M) and daily (D) 10-year FULL shares are both from 0.40 to 0.60;
  - the shared classification when M and D are both outside the band and agree;
  - otherwise `differs_between_monthly_and_daily_files`.

### 3.3 Windows (all fixed before any data run)

| window_id | a → b | Purpose | Role (variant M) |
|---|---|---|---|
| FULL | 202312 → 202609 | the registered window | `REGISTERED` at 10Y; `SAME_RULE` at 2Y, 5Y, 20Y |
| A | 202312 → 202407 | before the BoJ's "summer 2024" | `SUBWINDOW` |
| BRIDGE | 202407 → 202408 | the month between A and B; never classified; FULL = A + BRIDGE + B exactly | `BRIDGE` |
| B | 202408 → 202609 | to set beside the BoJ Review's "from summer 2024" (base 202408, ruling O-3). Straddles Y2024 and Y2025_26 | `SUBWINDOW` |
| BOJ_MATCH | 202408 → 202606 | same end as the BoJ chart (end-June 2026); Grok read it before the build | `CROSSCHECK_NONINDEPENDENT` |
| Y2024 | 202312 → 202412 | the path, first part (R3-2); Grok read it before the build | `CROSSCHECK_NONINDEPENDENT` |
| Y2025_26 | 202412 → 202609 | the path, second part; **FULL = Y2024 + Y2025_26 exactly** | `CROSSCHECK_NONINDEPENDENT` |

Required README label (R2-7): "The full-window result was read before this build. The sub-windows and the BoJ-matched window were
chosen after looking at the data." The README also says that window B straddles the two path windows.

| variant | Values | Role |
|---|---|---|
| M | `yield_M.csv`, tenors 2Y, 5Y, 10Y and 20Y | as in the window table |
| D | `yield_D.csv`: monthly mean of the month's daily rows; same tenors and windows | `SENSITIVITY`; reported beside M (R2-2); feeds the headline reading only, never the registered classification |
| JMA | `curve-panel.csv`, `Type = actual` rows only, `TP_kY` and `RN_kY` (RN is its expected-rate component, on a spot yield) | `CROSSCHECK` |

### 3.4 JMA label (R2-1; R3-3)

`jma_label = model_sensitive` if any of three arms fires. Each arm is strict and compares values rounded to 6 decimals:
- **ratio arm:** JMA's 10Y FULL d_tp is under half of M's, or over twice M's;
- **share arm:** |s_M − s_JMA| > 0.15;
- **side arm:** s_JMA is on the other side of 0.50 from s_M.

Otherwise the label is `not_flagged`. `jma_arms_fired` lists the arms that fired, joined with `+` (for example `share+side`).
Expectation stated now: R2-1's share arm is expected to fire, because Grok read JMA's share at about 0.29.

JMA's basis differs from Nakajima's:
- its yield is a spot (zero-coupon) yield;
- its 2026-09 Yield_10Y (3.0656) sits near the MoF month-end (3.057), not the monthly mean (2.9922), so it is probably a month-end
  value (inferred; O-5);
- it benchmarks its premia to their 2004–2012 averages (O-6).

### 3.5 BoJ Review: side by side, no label (R3-8)

- The README prints M's BOJ_MATCH 10Y share (about 0.64, supervisor) beside the Review's words "roughly the same degree", and gives
  **no agree or disagree label**.
- It says that reading "roughly the same degree" as 0.40 to 0.60 is this spec's convention, not the Bank's.
- It says the Bank used a different model (Imakubo and Nakajima 2015, anchored on Consensus Forecasts) and a window that Grok had
  already read.
- `verdict.csv` carries the share (`boj_match_tp_share`) and no comparison column.

### 3.6 Vintage rule

- **vintage_id** = `<commit date YYYY-MM-DD>_<first 12 hex of the commit sha>`. The expected value for `yield_M.csv` is
  `2026-10-06_33118433fe95`.
  - `yield_D.csv` has its own commit list and its own vintage_id.
  - JMA's vintage_id = `jma_<page vintage as YYYY-MM>_<first 12 of the sha256>`.
- **Commit list.** The 9 uploads of `yield_M.csv`: 2025-02-06, 04-04, 06-05, 09-24, 12-04 and 12-31, then 2026-04-20, 07-06 and
  10-06.
- **Fetch and window end.** `fetch` takes the newest commit of each file.
  - If its last month is before 202609, `build` stops and reports the vintage, with no classification.
  - If the file runs past 202609, FULL still ends at 202609.
- **The registered verdict is the first successful build.** Its `verdict.csv` rows are frozen.
  - A later vintage adds rows with `status = later_vintage` and never rewrites the registered rows.
  - If a classification changes, the README states both.
- **Revision table** (`vintage_revisions.csv`, 10Y only, changes only):
  - REV_2606 = 202312 → 202606, on the October and July vintages;
  - REV_2603 = 202312 → 202603, on the October, July and April vintages.
  - Each row uses one vintage only.
- **What size of revision matters (the stand-in for an MDE, C-090).** There is no sampling noise here; the noise is revision and
  choice of model.
  - At dy 2.3061 the registered share lies 0.149 pp of d_tp inside the band's upper edge (0.60) and 0.313 pp from its lower edge
    (0.40).
  - The one observed revision moved a single month's TP10 by 0.018 pp, which shifts s by about 0.008. A revision of that size cannot
    move the share out of the band.
  - A change of model can: the daily file reads 0.44 and JMA about 0.29 (reviewer).

### 3.7 Fitted-yield check (supervisor's item)

- **Gap.** For M at tenors 2, 5, 7, 10, 15 and 20: gap_m = TP_k(m) + ER_k(m) − the mean of the MoF daily k-year yields in month m.
  Only months with at least 10 non-missing MoF days count.
- **Scopes for M.**
  - `window` (202312–202609): **FAIL if any |gap| > 0.00015** (two 4-decimal roundings plus float error).
  - `full_history`: max and median |gap| and the count over the tolerance; INFO.
  - Basis `month_end`: the same comparison against the month's last MoF value; INFO. Expected to be clearly larger (0.0648 at 10Y in
    September 2026).
- **D.** The gap on each date present in both files, **tolerance 1e-6** (R2-9), over the window. Dates present in only one file are
  counted.
- **README.** States the gap, says it confirms the basis, and says it cannot test the model.

## 4. Questions answered (fixed now; no other statistic is reported)

- **Q1 (registered).** M, 10Y, FULL: classification, share and distance_bp, under 3.2.
- **Q2.** M at 2Y, 5Y and 20Y, FULL: the same rule, printed side by side with 10Y.
  - Supervisor values: 2Y 0.360, 5Y 0.442, 10Y 0.536, 20Y 0.615.
  - The README says the other tenors fall on both sides of one half.
- **Q3.** M over windows A and B at the four tenors: the same rule. BRIDGE is reported and not classified. Identity: FULL = A +
  BRIDGE + B.
- **Q4.** The path: Y2024 and Y2025_26 at the four tenors. Identity: FULL = Y2024 + Y2025_26. Supervisor values at 10Y: 0.055 and
  0.635.
- **Q5.** BoJ side by side (3.5). Supervisor values at 10Y: BOJ_MATCH 0.643, and B 0.581.
- **Q6.** JMA label and arms (3.4), and JMA's own shares at the four tenors over all seven windows.
- **Q7.** D beside M: the four FULL shares and classifications, and the headline reading (3.2).
- **Q8.** Revisions: s on REV_2606 and REV_2603 for each vintage.

## 5. Outputs

**Script `bin/japan_term_premium.py`.**
- Modes: `fetch`; `build` (offline, byte-identical on re-run); `selftest` (synthetic data, no network, under 20 s).
- Committed files sit in `data/japan_term_premium/`. Each CSV opens with a `# source:` line and a citation line.
- Changes and yields in pp to 4 decimals; shares to 4 decimals; distance_bp to 1 decimal.
- Headers contain no spaces (R2-10).

**Allowlists, kept outside the code.** The selftest parses the block below from the landed spec (default
`_research/2026-10-19-Japan-Term-Premium-Spec.md`, or `--spec PATH`) and requires it to equal the script's `ALLOW` exactly (G11).

```ALLOWLIST
decomposition.csv: vintage_id,variant,tenor,window_id,start_month,end_month,d_yield_pp,d_tp_pp,d_er_pp,tp_share,distance_bp,classification,opposite_signs,role
verdict.csv: verdict_id,vintage_id,tenor,d_yield_pp,tp_share,distance_bp,classification,tp_share_2y,tp_share_5y,tp_share_10y,tp_share_20y,d_variant_tp_share,d_variant_classification,headline_reading,jma_tp_share,jma_label,jma_arms_fired,boj_match_tp_share,status,superseded_by,vintage_retrieved_utc
vintage_revisions.csv: window_id,start_month,end_month,vintage_id,d_yield_pp,d_tp_pp,d_er_pp,tp_share,classification
fitted_check.csv: vintage_id,file,tenor,scope,basis,n_periods,max_abs_gap_pp,median_abs_gap_pp,n_over_tol,status
vintages.csv: vintage_id,source,file,commit_sha,commit_utc,blob_sha,sha256,first_period,last_period,n_rows,stated_update,retrieved_utc,role
pins.csv: vintage_id,source,series,period,value,unit
checks.csv: check_id,description,expected,observed,status
fetch_log.csv: utc_time,host,path,status,bytes,sha256
FILES: decomposition.csv,verdict.csv,vintage_revisions.csv,fitted_check.csv,vintages.csv,pins.csv,checks.csv,fetch_log.csv,README.md,SOURCES.md
```

**The files.**
- `decomposition.csv`: at most 84 rows per vintage set (M 28, D 28, JMA 28).
  - `variant` ∈ {M, D, JMA}; `tenor` ∈ {2Y, 5Y, 10Y, 20Y};
  - `window_id` ∈ {FULL, A, BRIDGE, B, BOJ_MATCH, Y2024, Y2025_26};
  - `classification` ∈ {CLOSE_TO_EVEN, TERM_PREMIUM_LARGER, EXPECTED_RATES_LARGER, NOT_CLASSIFIED, NOT_APPLICABLE}.
- `verdict.csv`: one row per tenor for the registered vintage, with all four tenors' shares on every row (R3-1).
  - `status` ∈ {registered, later_vintage, amended, superseded}.
  - `vintage_retrieved_utc` is taken from `fetch_log.csv` (R10).
- `vintage_revisions.csv`: 5 rows (3.6).
- `vintages.csv`: every commit listed, with role `used`, `revision` or `listed`, plus JMA.
- `pins.csv`, capped (section 6).
- `checks.csv`: section 7.
- `fetch_log.csv`: every request.

**`README.md`** (generated, and scanned by G13 and G20). Internal codes are spelled out: "monthly file" and "daily file", not M and
D; "full window, December 2023 to September 2026", not FULL.
1. **Two opening sentences.** "This folder splits the change in Japan's 10-year government bond yield from December 2023 to
   September 2026 into a term premium and an expected path of short-term rates, using one researcher's published model." Then the
   required sentence of section 0.
2. **The result.**
   - The registered reading, its share and its distance from an even split in basis points.
   - The four tenors side by side, with the sentence that they fall on both sides of one half.
   - The monthly and daily files side by side, and the headline reading.
   - The path windows, and the note that window B straddles them.
   - Every share names its denominator.
3. **The R2-7 label**, verbatim.
4. **Definitions:** term premium, expected rates, residual, monthly average, constant-maturity yield, vintage.
5. **Model caveat (R3-4), stated as a property of the cited model and not as a finding.** "The Ichiue–Ueno model holds the long-run
   short rate constant, so a rise in long-run expected rates can be recorded as term premium. Japan Macro Advisors makes this
   criticism of the standard model."
   - The builder confirms the constant long-run rate (ρ) from the 2013 paper, pp. 8–9, and records whether Nakajima (2025) keeps it.
   - If that is not established, the README says "not confirmed for the 2025 estimation".
   - Reading the papers is a manual step outside the script, with the neutral User-Agent and one request per file; it is recorded
     in the builder decisions.
6. **What it cannot say:** C-126, and model dependence. Then the JMA comparison (its label and arms, its spot yield, its
   proprietary model, later estimates for paid users) and the BoJ side by side (3.5).
7. **Why dy (monthly averages) differs from R3's +243bp**, which runs from 29 Dec 2023 to 24 Sep 2026 on daily values.
8. **The fitted-yield gap**, and what it does and does not show.
9. **Vintage and revisions.**
10. **Provenance:** both citations; "not the official view of the Bank of Japan"; Nakajima's repository has no stated licence; the
    JMA attribution.

No BoJ purchase-effect numbers appear anywhere.

**`SOURCES.md`:** every URL, commit sha, licence text and citation.

## 6. Licence and leak rules (R2-4)

1. **Nothing from `yield_M.csv` or `yield_D.csv` is committed except:**
   - changes over the listed windows;
   - shares and distances;
   - **at most four level points per vintage**, in `pins.csv` only.
2. **Pin caps.**
   - October vintage: TP10 and ER10 at 202312 and 202609.
   - July vintage: TP10 and ER10 at 202606.
   - April vintage, and every `yield_D.csv` vintage: none.
   - MoF: at most 4. JMA: at most 3.
3. **No other level in `checks.csv`.** Level checks beyond the pins (C04, C08) commit `match` or `mismatch` in `observed`, never the
   value. The expected values live in this spec.
4. **Months list.** The only months in any committed file are {202312, 202407, 202408, 202412, 202603, 202606, 202609}: the window
   ends, the revision ends and the pin months.
   - A window change combined with a pin of the same vintage implies a level at a listed month. That is accepted (ruling O-4), and
     the list is the bound on it.
   - No committed file has a column of monthly or daily levels, and no daily date is committed.
5. **The leak guard (G10, C13) must be shown to FAIL on planted bad files**, not only to pass on the good folder.
6. **`bin/check.sh` M16 (warn only; R8 permits this edit).**
   - `data/japan_term_premium/` holds only the FILES list.
   - No tracked file (`git ls-files`) contains the line `"YYYYMM","ShadowRate","TermPremium-2Y"` or `"YYYYMMDD","ShadowRate"`.
   - Pins are within their caps, and months are within the list.
   - On a scratch copy with a planted `yield_M.csv`, a renamed copy and a fifth October pin, it must print three ✗ lines.
     `JTP_DIR` points it at the copy.

## 7. Pinned checks (`checks.csv`)

- **C01 Page links (FAIL).**
  - The Sites page hrefs include `github.com/jouchinakajima/program/blob/main/yield_M.csv` and `.../yield_D.csv`.
  - The whitespace-stripped page text's last month (`2026/Sep.`) equals the file's last month.
  - The stated update (`2026/Oct.`) is recorded in `vintages.csv`.
- **C02 Blob identity (FAIL):** `git hash-object` of each raw body, as bytes, equals the contents API `sha` at that commit.
- **C03 Shape (FAIL).**
  - The quoted header, matched by name.
  - Every data cell parses with `float()`, scientific notation included.
  - Months consecutive from 199501; for the daily file, dates strictly increasing; no blank cell.
  - The monthly file has 381 rows to 202609 on the expected vintage.
- **C04 Level pins on vintage `2026-10-06_33118433fe95`.** FAIL on that vintage; WARN `new vintage` on any other.
  - Committed values: 202312 TP10 −0.0583 and ER10 0.7444; 202609 TP10 1.1768 and ER10 1.8154.
  - Checked but committed as `match` only:
    - 201609 ShadowRate −3.2823 (the sign holds in the negative-rate era);
    - daily file, 20260930: TP10 1.0082, ER10 2.0488;
    - daily file, mean September 2026 TP10: 1.0090 (19 rows).
- **C05 Fitted-yield identity (FAIL on the window; 3.7).**
  - MoF pins: 10Y December 2023 mean 0.6861 and September 2026 mean 2.9922, gap 0.0000; month-end gap September 2026 0.0648 (INFO).
  - The MoF file's sha256 and last date are recorded. The last date must be on or after 2026-09-30.
- **C06 Daily against monthly (INFO):** per tenor, the median |M − monthly mean of D| of TP over the window.
- **C07 Vintage.** The newest commit is expected to be `33118433fe95…`, dated 2026-10-06, with 9 commits listed. A different newest
  commit is a WARN.
- **C08 Revisions (INFO).**
  - 202312 is identical across the three vintages fetched (observed for July against October).
  - July 202606 TP10 1.072 and ER10 1.5821; these are the July vintage's two pins.
- **C09 JMA (FAIL on shape, INFO on values).**
  - 200 without a login.
  - The columns `YM, Type, Yield_kY, RN_kY, TP_kY` are present for k = 2, 5, 10 and 20.
  - `Type = actual` runs through 2026-09.
  - RN + TP = Yield within 0.0002 on every actual row.
  - 2026-09 values as in section 2; the page vintage text is recorded.
- **C10 Window months** present in every variant (FAIL).
- **C11 Supervisor and reviewer pins on the expected vintage.**
  - FAIL, at 4 decimals: M 10Y FULL d_tp 1.2351, d_er 1.0710, d_yield 2.3061, s 0.5356, distance_bp +8.2, `CLOSE_TO_EVEN`.
  - FAIL, at 3 decimals (round 3):
    - 10Y shares: Y2024 0.055, Y2025_26 0.635, B 0.581, BOJ_MATCH 0.643;
    - FULL shares: 2Y 0.360, 5Y 0.442, 20Y 0.615.
  - Reproduce within 0.005 or explain (round-2 reviewer values): D 10Y FULL 0.44; JMA 10Y FULL 0.29.
- **C12 Identities (FAIL).**
  - d_yield = d_tp + d_er: 1e-9 unrounded, 2e-4 committed.
  - FULL = A + BRIDGE + B, and **FULL = Y2024 + Y2025_26**, for each variant and tenor: 1e-9 unrounded.
- **C13 Leak guard (FAIL):** section 6, run on the committed folder.
- **C14 Fixed output:** a second `build` leaves every sha256 unchanged, even with the clock moved forward.
- **C15 Fetch:** at most 15 requests, all logged, and STOP absent.

## 8. Selftests (synthetic only; each guard applies its own mutant, and an uncaught mutant fails the selftest)

| Guard | Protects | Mutant that must be caught |
|---|---|---|
| G1 columns by name | header lookup | a fixture with the TP and ER columns swapped, read by position |
| G2 change direction | d = end − start | start − end (every change flips sign) |
| G3 share numerator | s = d_tp / d_yield | d_er / d_yield; d_tp / d_er |
| G4 rule and band | 3.2 as amended | dy 0.2499 classified, or 0.25 not classified; **s 0.5356, 0.40 or 0.60 given a "larger" label instead of CLOSE_TO_EVEN**; 0.3999 called CLOSE_TO_EVEN; 0.6001 not TERM_PREMIUM_LARGER; `tp_share` filled for a NOT_CLASSIFIED row; distance_bp computed without × d_yield |
| G5 opposite signs | literal rule | fixture d_tp −0.10, d_er +0.50 (expected: s −0.25, EXPECTED_RATES_LARGER, opposite_signs yes) computed on absolute values |
| G6 window additivity | base = first named month | B based on 202407 (counts the bridge twice); the bridge dropped; **Y2025_26 based on 202501, or Y2024 ending 202411**; FULL ≠ A + BRIDGE + B, or **FULL ≠ Y2024 + Y2025_26**, by more than 1e-9 |
| G7 vintage | R6, 3.6 | months filled from an older vintage; two vintages mixed in one statistic; a later vintage rewriting a registered row |
| G8 parsing | R3-5 | a fixture with the real **quoted header** and a **`-1e-04` cell** (expected −0.0001): a 4-decimal pattern test rejects the cell; quotes kept in the column names; "-0.0583" parsed as 0.0583; values scaled by 100 (fails C05 on the fixture) |
| G9 fitted identity | 3.7 | month-end used as the monthly basis (the fixture's 0.0648 gap must fail); TP − ER; MoF `-` read as 0; MoF title row read as data; daily tolerance loosened from 1e-6 |
| G10 leak guard | section 6 | planted in a scratch output folder: (a) a copy of a fixture `yield_M.csv`; (b) the same bytes as `x.csv`; (c) a `tp10_level` column; (d) a fifth October pin, or a pin for the April vintage; (e) a numeric column matching three consecutive raw monthly levels; (f) a month outside the seven-month list; (g) a level value in `checks.csv` beyond the pins. Each must FAIL, and the clean folder must PASS |
| G11 allowlist anchor | section 5 | an extra column in `ALLOW`; the spec block edited by one character; a file not in FILES |
| G12 fetch safety | R1–R5 | a host outside the list; a redirect not latched; a non-200 not latched; **a 429 or 403 reported as "absent" rather than "rate limited"**; `@` in the UA; a 16th request; pacing under 2 s; a `/main/` raw URL accepted; `fetch` running while STOP exists; **a static scan finds code that removes or renames STOP** (the mutant adds such a function) |
| G13 no causal text | R7, R4-5 | imports `CAUSAL_RX` from `bin/fx_rate_gap.py` unchanged and adds a local pattern for "led to", "prompted", "pushed", "in response to" (the union is applied); the required sentence passes; the same sentence with "driven by purchases" fails, and with "in response to purchases" fails |
| G14 JMA rows | actual rows only | a `forecast` row (2026-10) used as an end month |
| G15 JMA arms (R2-1) | 3.4, each arm strict; arms compare values rounded to 6 decimals, so float error cannot fire an edge | each fixture isolates one arm. **ratio** (equal shares): a JMA d_tp of 0.49 × M's fires and 0.50 × does not; 2.01 × fires and 2.00 × does not. **share** (both shares below 0.50, d_tp ratio 1): s_M 0.3000 with s_JMA 0.4501 fires; with 0.4500 (exactly 0.15) it does not. **side** (d_tp ratio 1): s_M 0.51 with s_JMA 0.49 fires. Mutants: ≤ in place of < in any arm; an arm dropped; `jma_arms_fired` missing an arm that fired; unrounded comparison (0.45 − 0.30 fires in floating point) |
| G16 cache location | R4 | a cache inside the repo accepted |
| G17 D aggregation | monthly mean of daily rows | the month-end daily value used; D fed into the registered classification; the headline reading ignoring D |
| G18 amendments | R9 | a rebuild with a changed frozen value overwrites silently; `--amend` deletes the old row |
| G19 blob identity | C02 | the blob comparison skipped, or computed on decoded text instead of bytes |
| G20 BoJ, no label | R3-8 | the README or `verdict.csv` carrying an agree or disagree verdict on the BoJ wording ("consistent with", "agrees", "disagrees", "contradicts", "confirms" near "Bank of Japan" or "BoJ"); the "this spec's convention" sentence missing |
| G21 timestamps | R10 | a committed timestamp taken from the clock (the mutant uses `datetime.now()`; a second build at a shifted clock must be byte-identical) |

## 9. Success criteria (exact)

1. `python3 bin/japan_term_premium.py selftest` prints G1–G21, each mutant caught, and exits 0.
2. `python3 bin/japan_term_premium.py fetch` makes at most 15 requests (11 expected), all logged, with no STOP.
3. `python3 bin/japan_term_premium.py build`:
   - C01–C05, C07 and C09–C15 PASS;
   - C04, C07 and C11 may be WARN only if the newest commit is not `33118433fe95`, which the builder reports;
   - C06 and C08 are INFO;
   - Q1–Q8 are written.
4. On vintage `2026-10-06_33118433fe95`:
   - C11 reproduces every supervisor pin;
   - the M 10Y FULL row reads `CLOSE_TO_EVEN`, s 0.5356, distance_bp +8.2;
   - the window 10Y fitted-yield gaps are all ≤ 0.00015;
   - the M 10Y FULL d_yield equals the MoF September 2026 mean minus the December 2023 mean (2.9922 − 0.6861) exactly;
   - both additivity identities hold.
5. A second `build` leaves every sha256 unchanged.
6. `bin/check.sh --all` shows:
   - the existing ✓ guard lines, `✓ no killed claims found`, `✓ page clean`, and M10 clean;
   - M16 clean on the real folder, and three ✗ on the planted scratch copy.
7. A verifier re-derives one number by hand from the cached file: the M 5Y FULL share (0.442), or any D row.
8. **README cold-reader test.** Two fresh agents with no context, a non-specialist trustee and a rates practitioner, read only the
   README.
   - Each must state that this is one model's split, not a cause, and not a test of the breakeven split.
   - Each must also state that the 10-year result is close to even and depends on the model.
   - A reader fails the README if they come away believing any of these: that the term premium was measured independently of a
     model; that the BoJ agrees or disagrees; a causal claim.

**Landing (builder).**
- A REPRODUCE.md paragraph.
- Proposed CALENDAR row text, not written: "quarterly, after a new Nakajima commit: `fetch`, `build`; a later vintage adds rows and
  never rewrites the registered verdict".
- A HANDOVER row.
- The builder commits nothing. The supervisor verifies and writes any findings text.

## 10. OPEN questions

- **O-1 What the published term premium is.** TP + ER reproduces the MoF monthly-average yield to 4 decimals at six tenors in two
  months, so TP looks defined as the observed yield minus the model's expected path. Ichiue and Ueno (2013) or Nakajima (2025)
  should confirm this; it decides how the README words the residual (C-098). *Settles:* the paper's definitions section, read in the
  same manual step as R3-4.
- **O-2 Why the monthly file is not the average of the daily file** (September 2026 TP10 1.1768 against 1.0090). Separate
  estimations on monthly and daily data are the likely reason. Which one the author treats as primary is unknown. The registered rule
  uses M, and the headline reading uses both (R2-2).
- **O-3 CLOSED (round-1 ruling):** the base 202408 stands for window B, with the BRIDGE row.
- **O-4 CLOSED (round-1 ruling):** derived statistics plus at most four level points per vintage, with both citations; the raw files
  stay outside the repo.
- **O-5 JMA month-end or monthly average.** Spot is stated; month-end is inferred from one date. *Settles:* a line on the JMA page,
  or a reply to its academic-enquiry offer. Writing to them is the principal's decision; no agent writes.
- **O-6 JMA's 2004–2012 benchmarking.** If it is an additive constant, changes are unaffected; if not, JMA's d_tp is not comparable.
  Unknown.
- **O-7 The BoJ chart's base.** "From Aug. 2024" may be the August average or a date in August. Either way the comparison is side by
  side with no label (R3-8).
- **O-8 Vintage cadence.** The page says "quarterly", but the commits show two uploads in December 2025 (4 and 31 Dec). The next is
  expected around January 2027, after the 3 November due date, so the registered build will probably run on the October vintage.
- **O-9 R3-4's constant long-run rate.** Whether Nakajima (2025) keeps the constant ρ of Ichiue and Ueno (2013). If not established,
  the README says "not confirmed for the 2025 estimation".

## Supervisor rulings, 19 Oct 2026 (before any data run)

- **O-3:** the 2024-08 base for the "2024-08 to 2026-09" window stands, with the bridge row so the pieces add back to the full window.
- **O-4:** committing derived statistics (window changes, shares) plus at most four level points per vintage, with both citations the page
  requests and the raw files kept in a local cache outside the repository, follows the rule already applied to sources without an open
  licence (the gold, comovement and FX builds). No ruling from the principal is needed.
## Supervisor rulings, round 2 (second review), 19 Oct 2026 — before any data run

All ten fixes from the second review are accepted:

- **R2-1 JMA label rule:** `model_sensitive` if JMA's 10-year term-premium change over the full window is under half or over twice Nakajima's, or |s_M − s_JMA| > 0.15, or JMA's share sits on the other side of 0.50; otherwise `not_flagged`.
- **R2-2 M and D side by side.** The monthly-file share (M) and daily-file share (D) are both reported; the headline reading is "close to even and model-dependent" when both fall in 0.40 to 0.60 (reviewer values: M 0.54, D 0.44, JMA 0.29).
- **R2-3 R8** permits the M16 edit to `bin/check.sh`; G13 copies CAUSAL_RX from the gate rather than restating it.
- **R2-4 Leak caps** made consistent: at most four level points per vintage, and C04 and `vintage_revisions` are cut to that cap.
- **R2-5 `tp_share` is blank** when the window is not classified.
- **R2-6 Timestamps** come from the cache, so a rebuild is byte-identical.
- **R2-7 README label:** "The full-window result was read before this build. The sub-windows and the BoJ-matched window were chosen after looking at the data."
- **R2-8** GitHub 403/429 is reported as rate limiting, not as absence.
- **R2-9** Daily-file tolerance 1e-6.
- **R2-10** Headers without spaces; internal codes spelled out in the README.
## Supervisor rulings, round 3 (Grok attack, g9), 19 Oct 2026 — before any data run

The supervisor re-derived Grok's figures from the cached `yield_M.csv` (commit 33118433fe95). All hold: 10Y shares 0.055 (202312→202412), 0.635 (202412→202609), 0.581 (202408→202609), 0.643 (202408→202606); full-window shares by tenor 0.360 (2Y), 0.442 (5Y), 0.536 (10Y), 0.615 (20Y).

- **R3-1 No winner inside the band.** A share from 0.40 to 0.60 inclusive is classified `CLOSE_TO_EVEN`, with no "larger" label. Every verdict row also prints the share, its distance from one half in basis points of yield change ((s − 0.5) × (dTP + dER) × 100), and the four tenors side by side. The registered row stays M-10Y-FULL; the README says the other tenors fall on both sides of one half.
- **R3-2 The path.** Two more windows are added: `Y2024` (202312 → 202412) and `Y2025_26` (202412 → 202609), so FULL = Y2024 + Y2025_26 exactly. Both are labelled `CROSSCHECK_NONINDEPENDENT` (Grok read them before the build). The README shows them, and says window B straddles both.
- **R3-3 JMA rule.** Grok's point (the "under half" test stays silent at shares 0.54 vs 0.29) is already met by round-2 rule R2-1, whose share-difference arm (|s_M − s_JMA| > 0.15) fires here. R2-1 stands; the "model_sensitive is likely" sentence becomes "R2-1's share arm is expected to fire (Grok read JMA's share at about 0.29)". JMA's yield is described as a spot (zero-coupon) yield.
- **R3-4 Model caveat.** The README says, as a property of the cited model and not as a finding: the Ichiue–Ueno model holds the long-run short rate constant, so a rise in long-run expected rates can be recorded as term premium; JMA makes this criticism of the standard model. The builder confirms the constant ρ from the 2013 paper (pp. 8–9) and records whether Nakajima (2025) keeps it; if not established, the README says "not confirmed for the 2025 estimation".
- **R3-5 Parsing.** The real header is quoted (`"YYYYMM","ShadowRate","TermPremium-2Y",…,"ExpectedRate-20Y"`); cells may be in scientific notation (`-1e-04`). The shape test accepts any float that Python's `float()` parses; a 4-decimal pattern test is a defect. G-fixtures include both.
- **R3-6 MoF series** is named "constant-maturity yield, semiannual compounding, percent, `-` for missing" from MoF's own Q&A; never "par yield".
- **R3-7 Licences.** Grok is RIGHT that the GitHub repo's licence field is null (supervisor re-checked the API on 19 Oct): the spec's "The repo's CC BY 4.0" is deleted; the repo has no stated licence. Grok is WRONG that the JMA page lacks a reuse sentence: the live page (re-fetched 19 Oct) reads "free to use and reproduce with attribution to Japan Macro Advisors". JMA's model is proprietary and later estimates are for paid users; the README says so. Raw files stay out of the repo either way.
- **R3-8 BoJ comparison.** The BOJ_MATCH share (about 0.64) is printed beside the Review's words "roughly the same degree" with no agree/disagree label. The README says that reading "roughly the same degree" as 0.40–0.60 is this spec's convention, not the Bank's.

## Supervisor rulings, round 4 (spec author's flags on the rewrite), 19 Oct 2026 — before any data run

- **R4-1 R3-7 corrected: the supervisor misread the spec.** The deleted sentence ("The repo's CC BY 4.0 does not extend to his file") meant *this* repository's CC BY 4.0 licence (confirmed in `LICENSE`), and it was right. Grok's null licence field concerns Nakajima's repository, which the spec already said had no licence file. Both statements now stand in section 2.
- **R4-2 Tolerances.** Any identity between 4-decimal published cells and a MoF yield (monthly or daily) uses 0.00015. 1e-6 applies only where the build recomputes a value from the same cells it already holds (for example the monthly mean of the daily rows, recomputed twice). G9's "loosened" mutant tests each tolerance at its own level.
- **R4-3 CALENDAR row 2026-11-03** is amended by the supervisor at commit: inside 0.40–0.60 the result is CLOSE_TO_EVEN with no winner. The amendment is made before any build, but after the full-window share had been read by the supervisor, both reviewers and Grok, and the row says so.
- **R4-4 Paper reading** (R3-4, O-9) is a manual step, as the author wrote: the builder fetches the two PDFs once each with the neutral User-Agent and records the finding and URL in its decisions. The script's allowlist is unchanged.
- **R4-5 Wording guard.** `CAUSAL_RX` is imported unchanged and a local pattern adds "led to", "prompted", "pushed" and "in response to". The guard is the union, so it is no weaker than the first draft.
