# Spec: JODI world oil ledger (CALENDAR.tsv row dated 2026-10-20)

*Spec author: g7 spec agent, 18 Oct 2026. Builder: implement `bin/build_jodi_oil_ledger.py` and `data/jodi_oil/` from this file alone.
Model scripts: `bin/build_crude_ledger.py` (EIA/STEO parsing, report style) and `bin/pull_ice_brent_cot.py` (out-of-repo cache, STOP latch,
pacing, allowlists, selftest with mutants). Outside review: Grok return 5 (g7). Supervisor rulings (18 Oct) outrank Grok and are applied
throughout. Everything under "Observed" was seen by the spec author on 18 Oct with the neutral User-Agent, one request per URL.*

**Pre-registration note.** On 18 Oct the spec author read three JODI annual files (2015, 2025, 2026) for coverage counts, unit relations,
identity rates and the US checkpoint. The primary statistic (section 3.4) was NOT computed. The decision rule (section 4) is fixed now.
The second review (18 Oct) also stayed blind on r(D, R). Its 13 accepted fixes are applied in the body and listed at the end (A1-A13).

**Terms.** CLOSTLV: a country's closing stock of crude at month end (a level). STOCKCH: JODI's reported stock change for the month, closing
minus opening (positive = stocks rose). Reporter sum: the total over whichever countries reported a cell that month (membership changes).
Panel: a fixed list of countries, chosen by a rule (3.2) and frozen for the vintage before the test runs.

## 0. Goal

1. Build a monthly ledger of country-reported crude oil production and closing stocks from the JODI-Oil World Database: barrel sums
   for fixed panels, and coverage ratios with counts for the changing set of reporters; never world totals. [A10]
2. Reconcile it with EIA's STEO: production against STEO's world crude line, stocks against STEO's OECD commercial levels, and the
   non-OECD reported stock change against STEO's residual line "other inventory draws and balance".
3. Answer one question with a pre-registered test: is any of EIA's residual line visible in stocks that countries actually report?

**Can say:** what share of STEO world crude production JODI reporters cover, month by month; reported crude stock changes for named,
fixed panels; whether reported non-OECD crude stock changes move with EIA's residual line; that JODI's US crude stocks include the SPR.
**Cannot say:** a world stock level or world stock change (China, Russia and most of the Gulf do not report stocks; section 2.1); anything about
product stocks; anything about prices (no price enters this build); anything in real time (all series are revised vintages).
Grades (CLAUDE.md): reporter sums are MEASURED on a stated panel; STEO's world withdrawal is BOUNDED and its residual line is a residual
(C-098); the JODI-to-STEO gap is the falsifiable quantity.

## 1. Hard requirements

**R1. Licence.** JODI's terms: "All such rights are reserved" (terms-of-use.aspx, Intellectual Property). Raw JODI CSVs live only in the
cache `~/jodi_oil/` (override `--cache`; refuse any path whose realpath is inside the repository, as `check_cache` in
`pull_ice_brent_cot.py`). Cached names: `jodi_primary_<YYYY>_<sha12>.csv` (first 12 hex of the sha256), so every vintage is kept [A1]. `.gitignore` gains `jodi_primary_*.csv`, `primaryyear*.csv`,
`secondaryyear*.csv`. No committed file may let a reader rebuild JODI's country-by-month table (R6, G15, G23).

**R2. Acknowledgement.** Every output (each CSV, report.txt, README, SOURCES) begins with these lines (CSV: as `#` comment lines):
- `# source: International Energy Forum (IEF). Joint Organizations Data Initiative (JODI) Database. JODI Oil and Gas World Databases:
  www.jodidata.org, Accessed <D Month YYYY>. Derived statistics only; JODI reserves all rights; no JODI file is redistributed.`
  (wording from JODI's user guide, "How to Cite JODI Data"; the access date is the retrieval date of the newest JODI file in `fetch_log.csv`,
  so an offline rebuild is byte-identical).
- `# source: U.S. Energy Information Administration (Oct 2026): STEO bulk file (release of 6 Oct 2026); Petroleum Supply Monthly series
  MCRSTUS1, MCESTUS1, MCSSTUS1, MCRFPUS2.`
- `# vintage: JODI files <year>:<Last-Modified date>:<sha256 first 12> ...; max TIME_PERIOD <YYYY-MM>; preliminary months <list>.`

**R3. Fetching.** GET or HEAD only [A7]; no redirect followed (a redirect latches); hosts `www.jodidata.org` and `www.eia.gov` only; User-Agent
`Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)` (assert no `@`); sequential, at least 5 s between request
starts (`.last_request` beside the latch); at most 20 requests per run. Latch at the fixed path `~/jodi_oil/STOP`: any status other than 200, or a
body that fails its check (JODI CSV: first line exactly `REF_AREA,TIME_PERIOD,ENERGY_PRODUCT,FLOW_BREAKDOWN,UNIT_MEASURE,OBS_VALUE,ASSESSMENT_CODE`;
EIA .xls: magic D0CF11E0; STEO zip: magic PK03 04 and member `STEO.txt`; downloads page: contains `annual-csv/primary/`) writes STOP; nothing
retries; a socket fault ends the run without latching. If STOP is written, print it and stop: do not retry or route around it; tell the principal.

**R4. Vintage.** `fetch_log.csv` records per request: UTC start, host, path, status, bytes, sha256, the `Last-Modified` header. `build` refuses a
cached file with no log row of the same sha256. `file_stats.csv` (section 5) records each file's vintage and max TIME_PERIOD.

**R5. No price.** No price file is fetched, no price column is written, no regression of any kind is run, no p-value is printed.

**R6. Disclosure control [A10].** Barrel sums are published only for fixed panels (membership constant over the window, so no month-to-month
entry or exit can be differenced out). The changing reporter groups are published only as coverage ratios rounded to 0.01 (one point is
about 0.79 mb/d of STEO world crude, which blurs any single entrant below that size) and as counts; never as barrel sums or barrel changes.
A panel with fewer than 3 members is not published. Partition identity, asserted per month and flow: reporters_oecd + reporters_nonoecd =
reporters_all (counts and in-memory sums), and each panel's members are a subset of the matching reporters group. For nested panels whose
membership differs by 1 or 2 countries, the larger is blanked (`suppressed_diff_lt3`). Country-level values appear only in `checkpoints.csv`,
whose rows are the fixed list in section 5 (at most 30 rows). Reporter barrel sums (as in C3) are printed to the terminal only, never written.

## 2. Data

### 2.1 JODI-Oil World Database, primary annual CSVs (cached locally, never committed)

- Discovery: `https://www.jodidata.org/oil/database/data-downloads.aspx` (one request per fetch run; parse the `annual-csv/primary/` links).
- Files: `https://www.jodidata.org/_resources/files/downloads/oil-data/annual-csv/primary/<YYYY>.csv` for past years and
  `.../primary/primaryyear<YYYY>.csv` for the current year (2026). Window needs 2015 to 2026: 12 files.
- Columns: `REF_AREA` (ISO 3166-1 alpha-2), `TIME_PERIOD` (YYYY-MM), `ENERGY_PRODUCT`, `FLOW_BREAKDOWN`, `UNIT_MEASURE`, `OBS_VALUE`, `ASSESSMENT_CODE`.
- Used: `ENERGY_PRODUCT=CRUDEOIL` only (not TOTCRUDE, NGL, OTHERCRUDE; never the secondary file). Flows: `INDPROD` (production),
  `TOTIMPSB` (imports), `TOTEXPSB` (exports), `CLOSTLV` (closing stocks, end-month level), `STOCKCH` (stock change; identity checks and January seams [A6]). Imports and exports are parsed and unit-checked but not published: as reporter sums they would be barrel sums of a changing group, and they have no coverage denominator [A10].
- Units (JODI item-names guide, Sept 2017): KBD thousand barrels/day; KBBL thousand barrels; KL "thousand kilolitres"; KTONS thousand metric
  tons; CONVBBL "Conversion factor barrels/ktons". **Observed on all CRUDEOIL cells of the 2026 file:** KBD = KBBL / days in month (2,137 cells,
  worst gap 0.00005 KBD); KL = KBBL × 0.158987 (1,867 cells, none off); CONVBBL = 1000 × KBBL / KTONS (1,867 cells, none off by more than 1), e.g.
  7,400 bbl per kt for the US (7.40 bbl/t). So the five units are one reported number re-expressed; CONVBBL is the barrels-per-thousand-tonnes
  factor JODI used (country notes: Japan reports in tonnes and JODI converts with IEA factors; Saudi Arabia reports barrels; the US reports
  both and the factor is computed each month). **Rule:** KBBL for CLOSTLV and its changes, KBD for INDPROD/TOTIMPSB/TOTEXPSB; divide by 1,000
  for mb and mb/d. Never convert KTONS yourself: 364 crude cells in the 2026 file are numeric in KTONS with KBBL `-` and CONVBBL `..`
  (e.g. HK, all flows); they are counted as `n_ktons_only`, not used.
- Markers: `-` not reported; `x` not applicable (KBD of CLOSTLV and STOCKCH); `..` (only in CONVBBL rows) no factor. All are missing, never zero.
  A reported `0.0000` is a value, but a country whose CLOSTLV is 0 in every month of a window is classed `zero_reported` (8 such countries
  in each 2026 month, e.g. ID and KW, both producers): excluded from coverage counts and panels.
- Assessment codes (guide): 1 reasonable comparability; 2 consult metadata/use with caution; 3 not assessed; 4 under verification. The
  downloads page lists only 1 blue, 2 yellow, 3 white. **Observed:** codes 1, 2, 3 only in the 2015, 2025 and 2026 files; code 3 on about half of
  numeric cells (2026 file: 29,200 code 1, 558 code 2, 32,299 code 3 numeric). **Rule:** store the code; "comparable" totals use codes 1 and 3;
  codes 2 and 4 are excluded and counted; any other code is a hard failure.
- Sign: STOCKCH = CLOSTLV(t) − CLOSTLV(t−1), positive = build (US 2026-02: 705,664 − 676,671 = 28,993 = STOCKCH).
- Release: first update each month at noon London (2026 schedule PDF, `/_resources/files/downloads/jodi-update-schedule-2026.pdf`):
  **October's is Wednesday 21 October, not the 20th**; supplementary updates follow when late submissions arrive. Submission deadline M-2;
  for OECD members JODI history (all but the latest month) is IEA Monthly Oil Statistics; the US latest month is from EIA weekly reports and
  history from EIA monthly data (JODI country notes).
- Coverage facts (observed, 22 Sep 2026 vintage): 2026 file 96 areas; 2015 and 2025 files 118 areas (22 Latin American areas, incl. BR, AR,
  CO, TT, are absent from the 2026 file: absent is missing, not zero). Reporter-sum crude production: 2015-01 73.96 mb/d from 95 reporters;
  2025 mean 46.79 mb/d (59-62 reporters); 2026-07 40.49 mb/d (47). In 2025 and 2026 RU, IQ, IR, AE, AO, QA, OM and BR have no numeric crude
  production or stocks; CN reports production but CLOSTLV is `-` (country note: no closing stocks ever; crude stock change stopped
  October 2020); IN's last numeric month is 2026-03. A reporter sum is therefore not a consistent series over time; only fixed panels are.
- Old files are older vintages: `2015.csv` Last-Modified 21 Oct 2025; `2025.csv` and `primaryyear2026.csv` 22 Sep 2026.
- Licence handling: cache only (R1). Acknowledge (R2). Commit derived statistics only.

### 2.2 EIA (public domain, 17 U.S.C. 105; committed under `data/jodi_oil/raw/`, with `data/THIRD_PARTY_MANIFEST.tsv` rows)

- STEO bulk: `https://www.eia.gov/opendata/bulk/STEO.zip` (manifest `https://www.eia.gov/opendata/bulk/manifest.txt`: last_updated
  2026-10-06T16:02:16-04:00; 5,449,396 bytes). One JSON series per line in member `STEO.txt`; one vintage with full history. Used series
  (all monthly): `STEO.COPR_WORLD.M` world crude oil production, mb/d (from 1993-01); `STEO.PAPR_WORLD.M` total liquids (for the guard only);
  `STEO.T3_STCHANGE_NOECD.M` named "Net Inventory Withdrawals, Total Non-OECD Crude Oil and Other Liquids", mb/d, positive = draw, from 2003-02:
  this is the line STEO Table 3a prints as "Other inventory draws and balance" (2025-12 value −1.714 equals `other_draws_and_balance_mbd` in
  `data/crude/world_monthly_balance.csv`); `STEO.T3_STCHANGE_WORLD.M`, `STEO.T3_STCHANGE_US.M`, `STEO.T3_STCHANGE_OOECD.M`;
  `STEO.PASC_OECD_T3.M` OECD end-of-period commercial crude oil and other liquids, mb (from 2003-01); `STEO.PASC_US.M`; `STEO.COPR_SA.M`,
  `STEO.COPR_NI.M`, `STEO.COPR_KU.M` (checkpoints; STEO uses FIPS codes: NI = Nigeria, KU = Kuwait; FIPS NG is Niger). Commit only an extract,
  `raw/eia_steo_extract.csv` (series_id, name, units, month, value; 2014-12 to 2027-12), and log the zip's sha256. The zip stays in the cache.
  Flag months after STEO's last historical month (2026-09 in the Oct release) as `forecast`; they are never used.
- Petroleum Supply Monthly, `https://www.eia.gov/dnav/pet/hist_xls/<ID>m.xls`, thousand barrels (kb) or kb/d, sheet `Data 1`:
  `MCRSTUS1` US ending stocks of crude oil (incl. SPR), `MCESTUS1` excl. SPR, `MCSSTUS1` SPR, `MCRFPUS2` US field production (kb/d).
- Cross-check: STEO bulk values for 2022-01 to 2027-12 equal the committed `data/crude/raw/eia_STEO_m.xlsx` (same Oct release) within 0.001.

### 2.3 Observed on 18 Oct (one request each)

| URL | Status, size | Seen |
|---|---|---|
| JODI data-downloads.aspx | 200, 32,660 B | annual primary links 2002-2025 as `<YYYY>.csv`, 2026 as `primaryyear2026.csv`; "1 for blue, 2 for yellow and 3 for white" |
| `.../primary/primaryyear2026.csv` | 200, 5,542,684 B | Last-Modified Tue 22 Sep 2026 07:18:47 GMT; sha256 909a7330…ca5e2; 134,400 data rows; 96 areas; 2026-01..2026-07 |
| `.../primary/2025.csv` | 200, 11,575,254 B | Last-Modified 22 Sep 2026 07:18:22 GMT; sha256 5726e6e7…4870b; 283,200 rows; 118 areas |
| `.../primary/2015.csv` (HEAD, then GET) | 200, 11,856,506 B | Last-Modified 21 Oct 2025 18:35:00 GMT; sha256 08d761f3…cab4f; 283,200 rows; 118 areas |
| `jodi-oil-wdb-item-names-ver2017.pdf` | 200, 606,233 B | unit and code definitions quoted above |
| `jodi-oil-country-note.xlsx` | 200, 54,791 B | US, JP, SA, CN, RU, PH notes used above |
| `oil/support/user-guide.aspx` | 200 | citation sentence (R2) renders in full |
| `terms-of-use.aspx` | 200 | "All such rights are reserved"; no scripted-access clause |
| `jodi-update-schedule-2026.pdf` | 200 | October update Wed 21 Oct, noon London |
| `opendata/bulk/manifest.txt` (after a 301 from api.eia.gov), `STEO.zip` | 200 | as in 2.2 |
| `hist_xls/MCRSTUS1m.xls`, `MCESTUS1m.xls`, `MCSSTUS1m.xls`, `MCRFPUS2m.xls` | 200 each, XLS magic | values in section 7 |

## 3. Method

### 3.1 Cell reading

Parse every file with the header test (R3). Key cells by (area, month, flow, unit). For each CRUDEOIL cell keep value (float or None), code, and
a status: `ok`, `not_reported` (`-`, or area absent from that year's file), `not_applicable` (`x`), `code2_excluded`, `zero_reported`, `ktons_only`.
Assert one row per key; assert KBD×days = KBBL within 0.01 KBD wherever both are numeric (unit guard). Seam check: for each year boundary,
CLOSTLV(Jan, new file) − CLOSTLV(Dec, old file) against STOCKCH(Jan, new file), per country; count mismatches beyond max(1% of the change,
100 KBBL) and WARN with the count (old files are older vintages).

### 3.2 Groups (fixed in code, printed with members in `panels.csv`)

- OECD list (38 members, 2026): AU AT BE CA CL CO CR CZ DK EE FI FR DE GR HU IS IE IL IT JP KR LV LT LU MX NL NZ NO PL PT SK SI ES SE CH TR GB US.
- `reporters_all`, `reporters_oecd`, `reporters_nonoecd`: each month, every area with a usable cell for that flow. Published only as counts
  and as INDPROD coverage ratios (3.3) [A10]. **No barrel sum, level or change is published for any reporters_* group** (membership changes
  would make a level a pseudo-world total and a change an entrant's value; Grok change 1).
- Window W = 2015-01 to E, where E = max TIME_PERIOD of the vintage − 2 months. Months after E are `preliminary` (published, flagged, never in
  any statistic; Grok change 7).
- Panels are a rule, frozen per vintage [A3]: `build --panel-only` writes `panels.csv` and prints its sha256; the supervisor records that
  sha256 in `CALENDAR.tsv` before the primary is computed; `build` recomputes the panels and refuses to compute the primary if the sha256
  differs from the one passed as `--panel-sha <hex>`.
- `panel_nonoecd_stocks`: non-OECD areas with CLOSTLV usable (numeric, > 0, code 1 or 3) in every month of W.
- `panel_oecd_stocks_exspr`: OECD areas with CLOSTLV usable in every month of W; the US value is JODI US CLOSTLV minus EIA `MCSSTUS1` for the
  same month (JODI US includes the SPR; section 7, C5). Other members' government stocks cannot be removed and remain.
- `panel_producers`: areas with INDPROD usable (code 1 or 3) in every month of W.
- Nested pairs for R6: panel_nonoecd ⊂ reporters_nonoecd ⊂ reporters_all; panel_oecd ⊂ reporters_oecd ⊂ reporters_all; panel_producers ⊂ reporters_all.

### 3.3 Reconciliation (descriptive)

Units: stocks and stock changes in mb per month; flows in mb/d; STEO mb/d × days → mb. Draw = −ΔCLOSTLV (positive = stocks fell),
matching STEO's withdrawal sign.
- Production [A5]: `coverage_reporters` = reporters_all INDPROD, codes 1 and 3 ÷ STEO.COPR_WORLD; `coverage_reporters_allcodes` = the same
  with code 2 included (code 2 can be large: RU 2015-01, 10,110 kb/d, is code 2); `coverage_panel` = panel_producers INDPROD ÷ STEO.COPR_WORLD.
  Ratios rounded to 0.01 (R6). Never against PAPR_WORLD (total liquids; Grok change 4).
- OECD stocks: panel_oecd_stocks_exspr level and change against PASC_OECD_T3 level and change. The comparison is crude (JODI) against crude
  and other liquids (STEO), and OECD history in JODI is IEA data, which also feeds STEO: agreement here is not independent evidence. Report
  Pearson r of monthly changes over W only (no level ratio [A11]), labelled "shared source". Never compare a JODI stock change with
  T3_STCHANGE_WORLD (Grok change 5).
- Residual line: `steo_residual_minus_panel_mb` = STEO "other draws and balance" (mb) − panel_nonoecd draw (mb), monthly only; no
  cumulative version [A11].
- STEO world withdrawal (424.4 mb over Jan-Sep 2026, of which 145.9 mb is the residual line; section 7, C9) is printed for context, unmatched.

### 3.4 The one pre-registered test

- D(t) = −Σ over panel_nonoecd_stocks of [CLOSTLV(t) − CLOSTLV(t−1)] / 1000, mb; R(t) = STEO.T3_STCHANGE_NOECD(t) × days(t), mb.
  Seams [A6]: for every January, D(Jan) = −Σ STOCKCH(Jan, new file) / 1000 over the panel when every member's STOCKCH is numeric; otherwise
  the month is flagged `seam_unresolved`, excluded and counted (December and January come from files of different vintages).
- Months t = 2015-02 to E (one-month, non-overlapping changes; no multi-month horizon anywhere in the build; no levels).
- Demeaning [A2]: subtract from D its mean over the same calendar month (all Januaries, all Februaries, ...) within the test sample; the same
  for R. The primary statistic is Pearson r on the demeaned D and R; r on the raw series is printed as descriptive.
- Statistic: Pearson r(D*, R*) on the demeaned series; n = number of months. 95% CI [A9]: demean once on the full sample, then a moving-block
  bootstrap of the n index positions 0..n−1 in time order. Block length L = 12; k = ceil(n / 12) blocks per resample; each block start is
  `rng.randrange(n − L + 1)` (starts 0..n−12 inclusive), drawn in order with `rng = random.Random(20261020)` created once; the k blocks are
  concatenated and truncated to the first n positions; B = 10,000 resamples drawn in sequence; Pearson r on each resample's pairs. A resample
  with zero variance in either series is a hard failure, not a redraw. Sort the B values ascending: lower = value at 0-based index 250,
  upper = value at index 9,749. Also print the house band 1.96/√n (literal 1.96) and Spearman ρ on the demeaned series.
- Concentration [A3]: report the largest member and its share of panel change variance, share_i = Cov(d_i, D) / Var(D) on the test months
  (d_i is member i's draw; shares sum to 1). The second reviewer counts Saudi Arabia at about 59%.
- Runs only if the panel has at least 5 members and a mean level over W of at least 100 mb, and n ≥ 100; else the verdict is INCONCLUSIVE
  (`panel_too_thin` or `too_few_months`). Spec-author observation (not a pin), corrected [A13]: 13 non-OECD areas (AZ BG BH BN DZ HR NG PG
  RO RS SA TH TW) meet the panel rule over 2025-01..2026-06 alone, with a summed level of 241.9-281.8 mb (the earlier "290-340" was the sum of
  all non-OECD reporters, not of a panel); SA is 144 mb of it at 2026-06.
- Descriptive only, no CI, no verdict (role `descriptive` in `primary_test.csv`): raw (not demeaned) r; demeaned r excluding 2020-03..2020-12;
  excluding 2026; excluding both (this one also feeds the SUPPORTS condition in section 4); starting 2018-01; panel restricted to code-1
  cells; the OECD shared-source r (3.3).

### 3.5 Window choice

Jan 2015 is kept. (a) JODI coverage was near complete then (reporter sum 73.96 mb/d against STEO 75.95 mb/d in 2015-01, 0.974) and has fallen
since (0.592 in 2025), so a later start would not add members to a strict panel and an earlier start would remove members that started late.
(b) STEO's one-vintage bulk history reaches back to 2003, so STEO does not bind. (c) 2015-02 to 2026-05 gives about 136 monthly changes,
enough for a block bootstrap with 12-month blocks. (d) The window contains two large shocks (2020, 2026); the primary keeps them and the
descriptive rows show their weight. The start was chosen before the primary statistic was computed.

## 4. Decision rule (fixed 18 Oct, before the primary statistic is run)

Hypothesis H: part of STEO's residual line is stock change that non-OECD reporters measure.
- **SUPPORTS H:** r ≥ 0.25 and bootstrap CI lower bound > 0, and r ≥ 0.10 on the demeaned series with 2020-03..2020-12 and all of 2026
  removed [A2]. If the first two hold and the third fails, the verdict is **SUPPORTS (episode-driven)**.
- **AGAINST H:** r < 0.10 and bootstrap CI upper bound < 0.25.
- **INCONCLUSIVE:** anything else, or the run conditions in 3.4 fail.
Registration [A1]: a build is REGISTERED if and only if `file_stats.csv` shows `last_modified` of `primaryyear2026.csv` on or after
2026-10-21T00:00Z and its `max_period` ≥ 2026-08 (decided from the file, never from the clock; the Sep file reads 2026-09-22 07:18 GMT and
2026-07). Otherwise the build is a DRY_RUN: the primary row's statistic cells (pearson_r, ci95_lo, ci95_hi, spearman_rho, verdict) are blank,
the descriptive r rows are blank too, and D and R are never correlated in that run (the selftest proves the code path does not call the
correlation). The first REGISTERED build's verdict is the result; later monthly rebuilds are descriptive updates.
Wording allowed for SUPPORTS: "reported non-OECD crude stock changes (a fixed panel of N countries, mean X mb, of which <largest member>
carries <share>% of the change variance) move with EIA's 'other inventory draws and balance' line, r = …, n = …". For SUPPORTS
(episode-driven) the words "move with the line" are not allowed; write "co-moved during <episodes>, not outside them". Not allowed under any verdict: "world stocks", "China's stocks", "the residual is
measured", any price or causal wording. AGAINST means the residual line is not visible in reported non-OECD crude stocks; it does not mean
the residual is wrong.

Build-level conditions (checks, not the test): any FAIL in section 6 G-checks stops the build; a changed vintage turns section 7 pins into
WARN with "JODI may have revised" and the new values are recorded.

## 5. Outputs

Script `bin/build_jodi_oil_ledger.py`, stdlib plus `xlrd` (EIA .xls; already in requirements.txt). Modes: `fetch [--years Y1,Y2 | --all]`
(default: current and previous year, plus the downloads page and the EIA files), `check-vintage` (HEAD each annual file, report which differ
from the cache; paced and capped like fetch), `build` (offline, byte-identical on re-run), `selftest` (synthetic rows only, no network, < 10 s).
Every CSV: the R2 lines, then the header. A header that differs from its allowlist is a hard failure. Numbers: mb and mb/d to 3 decimals;
ratios and r to 3 decimals.

- `data/jodi_oil/panel_aggregates.csv` [A10]: `month, panel, flow, unit, value, n_members, n_code1, n_code3, data_status, suppression`.
  Fixed panels only; flow ∈ {INDPROD (panel_producers), CLOSTLV, DCLOSTLV (stock panels)}; unit `mb` or `mb_per_day`; data_status
  `final`|`preliminary`; suppression ``|`suppressed_diff_lt3`.
- `data/jodi_oil/coverage_counts.csv` [A10]: `month, group, flow, n_reporters, n_code1, n_code3, n_code2_excluded, n_zero_reported,
  n_ktons_only, n_not_reported, n_areas_in_file, data_status`. Counts only, reporters_* groups, flows INDPROD and CLOSTLV.
- `data/jodi_oil/panels.csv`: `panel, ref_area, oecd_member, months_usable, months_in_window`. No values.
- `data/jodi_oil/steo_reconciliation.csv`: `month, data_status, steo_basis, steo_world_crude_mbd, jodi_panel_producers_crude_mbd,
  coverage_reporters, coverage_reporters_allcodes, coverage_panel, steo_other_draws_balance_mb, jodi_panel_nonoecd_draw_mb,
  steo_residual_minus_panel_mb, n_panel_nonoecd, seam_flag, steo_oecd_commercial_change_mb, jodi_panel_oecd_crude_exspr_change_mb`
  [A5, A6, A10, A11].
- `data/jodi_oil/primary_test.csv`: `role, label, run_status, window_first, window_last, n_months, n_seam_excluded, n_panel, panel_sha256,
  panel_mean_level_mb, largest_member, largest_member_var_share, demeaned, pearson_r, ci95_lo, ci95_hi, spearman_rho, band_1p96_sqrt_n,
  verdict`. run_status `REGISTERED`|`DRY_RUN`. Exactly one `primary` row; ci95_* and a verdict only on it; descriptive rows carry
  `descriptive` as verdict. The cumulative sums are dropped [A11].
- `data/jodi_oil/identity_checks.csv`: `check, scope, code_set, n, n_pass, pass_rate, n_exact, note`. check ∈ {stock_identity, seam,
  unit_kbd_kbbl}; identity = |STOCKCH − ΔCLOSTLV| ≤ max(1% of |ΔCLOSTLV|, 100 KBBL); denominator n = country-months with all three cells numeric.
  code_set values: `all` (any of 1-3), `1_3`, and `all_three_code1` (STOCKCH, CLOSTLV(t) and CLOSTLV(t−1) all code 1) [A8].
  The note states that code-1 cells pass by construction (assessment includes the identity), so the rate is a data descriptor, not evidence.
- `data/jodi_oil/checkpoints.csv`: `id, ref_area, month, flow, unit, jodi_value, jodi_code, comparator, comparator_value, difference, status`.
  Fixed rows: US CLOSTLV KBBL at 2015-01, 2025-12, E and max month vs MCRSTUS1 (difference = offset); US STOCKCH at 2026-04, -05, -06 vs
  ΔMCRSTUS1 and Δ(MCRSTUS1 − MCSSTUS1) (two rows each); US INDPROD KBD at 2025-12 and max month vs MCRFPUS2; SA INDPROD at 2015-01, 2025-06 and
  max month vs COPR_SA; NG INDPROD (vs COPR_NI) and KW INDPROD (vs COPR_KU) at max month; SA CLOSTLV at 2015-01 and max month; JP CLOSTLV at max
  month; CN CLOSTLV status at max month; RU last numeric CRUDEOIL month (value blank). At most 30 rows.
- `data/jodi_oil/file_stats.csv`: `file, url, retrieved_utc, last_modified, bytes, sha256, rows, n_areas, first_period, max_period, n_dash,
  n_x, n_dotdot, n_code1, n_code2, n_code3, n_code4, header_ok`.
- `data/jodi_oil/checks.csv` (`id, check, expected, observed, status` with PASS/WARN/FAIL/INFO), `fetch_log.csv`, `report.txt`.
- `data/jodi_oil/raw/`: `eia_MCRSTUS1m.xls`, `eia_MCESTUS1m.xls`, `eia_MCSSTUS1m.xls`, `eia_MCRFPUS2m.xls`, `eia_steo_extract.csv`, `pull_log.tsv`.
- `data/jodi_oil/README.md` [A12]: opens with one plain paragraph, before anything else: what the test asks (is EIA's balancing line
  visible in stocks countries report?); that the panel is mostly Saudi Arabia; that reporter sums are not world totals; and that the fall in
  coverage from 0.97 to 0.59 is countries that stopped reporting, not lower output. Then defines CLOSTLV, STOCKCH, panel and reporter sum at
  first use, then what each file is, every column's unit and denominator, the groups, the window, what the result can and
  cannot say (section 0) and the SPR finding; OPEN items (US level offset, old-file vintages) go in a final section.
- `data/jodi_oil/SOURCES_JODI.md`: first line names JODI with the citation; JODI's rights clause quoted; what is cached and what is committed;
  that CC BY 4.0 covers only the project's computation; the disclosure rule (R6); the IEA origin of OECD history.

Landing: `CALENDAR.tsv` row updated to "after 21 Oct 11:00 UTC: selftest, fetch --all, build --panel-only, record panel sha256 here, build
--panel-sha <hex>"; a monthly row on JODI update days for
`fetch` then `build`; REPRODUCE.md note; `.gitignore` rules (R1); warn-only gate in `bin/check.sh` (next free M number) that flags any tracked
file whose first line is JODI's header, any `jodi_primary_*`/`primaryyear*` file present in the repository, and any `data/jodi_oil/` header
other than `checkpoints.csv` that has `ref_area` together with any of `month`, `period`, `time_period` or `date` [A10]. The supervisor writes findings text after verification.

## 6. Selftest guards (each mutant must make the selftest fail)

Synthetic fixture: 6 areas (3 OECD incl. "US", 3 non-OECD), months 2030-01..2031-06, all five units, codes 1-3, `-`, `x`, `..`, one
zero-reported area, one KTONS-only cell, one area absent from the second year's file, synthetic STEO and EIA series.

| Guard | Catches (Grok item) | Mutant |
|---|---|---|
| G1 missing_stays_missing | blanks summed as zero (1) | parse `-`/`x`/`..`/absent area as 0 |
| G2 no_world_stock_total | world total published (1) | write a CLOSTLV row for `reporters_all`, or a group named `world*` |
| G3 crude_primary_only | products or TOTCRUDE as crude (2) | include TOTCRUDE rows; or accept a file with no CRUDEOIL rows or a URL without `/primary/` (the two files share one header) [A13] |
| G4 single_unit | unit mixing, wrong thousand (3) | read KL or KTONS for a series; divide by 1e6; skip the KBD×days check |
| G5 assessment_codes | code 2/4 in comparable totals (6) | include code 2; accept code 5 silently |
| G6 vintage_recorded | undated file (7) | drop Last-Modified or max_period from file_stats; build a cache file with no log row |
| G7 preliminary_lag | look-ahead on latest months (7) | E = max month instead of max − 2 |
| G8 steo_crude_line | liquids vs crude (4) | use PAPR_WORLD for coverage |
| G9 oecd_commercial_only | world draw matched to stocks (5) | compute a gap against T3_STCHANGE_WORLD |
| G10 no_price | price regression (8) | a header containing price, usd, brent, wti, p_value, pvalue, t_stat or beta |
| G11 changes_not_levels | spurious levels | correlate CLOSTLV levels |
| G12 non_overlapping | overlapping windows | use 3-month rolling changes |
| G13 one_primary | multiple testing | two `primary` rows, or a verdict on a descriptive row |
| G25 dry_run_blind | registration [A1] | DRY_RUN fixture (Last-Modified before 2026-10-21 or max < 2026-08) calls the correlation or fills a statistic cell; registration read from the clock |
| G26 demeaned | seasonality [A2] | primary on raw D, R; or SUPPORTS without the episode condition |
| G27 panel_frozen | panel shopping [A3] | primary computed with a panel whose sha256 differs from `--panel-sha` |
| G28 seam_stockch | seam [A6] | January D from Dec/Jan levels across files instead of STOCKCH |
| G29 bootstrap_spec | [A9] | block starts from randrange(n), or no truncation to n, or other percentile indices (fixture CI pinned) |
| G30 partition | disclosure [A10] | oecd + nonoecd ≠ all in a fixture month; a barrel sum for a reporters_* group in any output |
| G14 sign | draw/build sign | D = +ΔCLOSTLV |
| G15 disclosure | rebuildable country table (R6) | publish a 2-reporter group, or nested groups differing by one area |
| G16 fips_map | country-code mix | map NG to STEO `COPR_NG` |
| G17 spr_removed | SPR in OECD commercial comparison | skip the MCSSTUS1 subtraction |
| G18 zero_reported | zeros as coverage | count the all-zero area as a reporter |
| G19 seam | revised December at a file seam | remove the seam check (fixture has one revised December) |
| G20 acknowledgement | missing JODI/EIA credit (R2) | drop the JODI line from one output |
| G21 column_allowlist | extra column | add `ref_area` to panel_aggregates |
| G22 bootstrap | non-reproducible CI | change or drop the seed (fixture CI pinned to 4 decimals); r on a series with known r = 0.6 off by > 0.01 |
| G23 no_country_table | JODI table rebuilt (R1) | write more than 30 checkpoint rows, or a checkpoint for an unlisted area/month |
| G24 fetch_rules | R3 | latch on 404, on a 301, on a bad body; no latch on socket fault; pacing < 5 s; host outside allowlist; 21st request; in-repo cache; fetch while STOP exists |

## 7. Success criteria (commands and the numbers they must print)

Run: `python3 bin/build_jodi_oil_ledger.py selftest` (all guards PASS, every mutant caught, exit 0); then `fetch --all`; then `build`; then
`build` again and `shasum` every output (identical). Pins below are for the 22 Sep 2026 vintage; on a later vintage each prints WARN with the
new value, except C5's verdict and C7, which must hold on any vintage.

- C1 Files. `primaryyear2026.csv`: 134,400 rows, 96 areas, max 2026-07, sha256 909a73300584b877b122659d549033f1eebab9f93d1131157e47ba0d142ca5e2.
  `2025.csv`: 283,200 rows, 118 areas, sha256 5726e6e7319bbb72cf051b2bbdb3ea436ae32a3e0370cea60e04f9472e54870b. `2015.csv`: 283,200 rows,
  118 areas, Last-Modified 2025-10-21. No code 4 in these three files. E = 2026-05 (Sep vintage) or 2026-06 if max is 2026-08.
- C2 Units. KBD = KBBL/days on every crude cell where both are numeric (2026 file: 2,137 cells); CONVBBL for US INDPROD 2026-07 = 7400.
- C3 Coverage [A5] (terminal print; committed ratios at 0.01). 2015-01 against STEO 75.95: all codes 95 reporters, 73.96 mb/d, 0.974; codes 1
  and 3 only 85 reporters, 61.34 mb/d, 0.808 (RU is code 2). 2025 mean of monthly all-code sums 46.79 mb/d, 0.592 against STEO's 2025 mean
  78.99; 2026-07 40.49 mb/d (47 reporters, preliminary).
- C4 Identity. 2025-01..2026-07, KBBL, all codes: n 974, pass 901 (0.925), exact (≤ 0.5 kb) 712; all three cells code 1: 702 of 702. 2015:
  961/894 (0.930); all three cells code 1: 441/441 [A8].
- C5 SPR. JODI US CRUDEOIL CLOSTLV 2026-07 = 568,729 KBBL; EIA MCRSTUS1 = 713,343, MCSSTUS1 = 304,810. US STOCKCH 2026-05 = −64,114 against
  ΔMCRSTUS1 −64,113 and Δ(excl. SPR) −24,970; 2026-04: −23,547 vs −23,552 and −3,251; 2026-06: −54,279 vs −54,277 and −21,082. Verdict printed
  `spr_included = yes` when, over 2025-01..E, median |STOCKCH − ΔMCRSTUS1| < 0.1 × median |STOCKCH − Δ(MCRSTUS1 − MCSSTUS1)| [A4]; the build
  lists every month where |STOCKCH − ΔMCRSTUS1| exceeds 2,000 KBBL (2025-03 must be among them: JODI −5,654 against EIA +3,549).
  Level offset MCRSTUS1 − JODI: 99,121 kb (2015-01), 135,979 (2025-01), 144,612 (2025-12), 144,614 (2026-07): printed, unexplained (OPEN-2).
- C6 Checkpoints. US INDPROD 2026-07 13,817.3871 kb/d vs MCRFPUS2 13,948; SA INDPROD 2026-07 8,135.0968 vs COPR_SA 7.83 mb/d; NG 1,505.0 vs
  COPR_NI 1.42; KW 1,971.0 vs COPR_KU 1.77 (difference printed, no pass/fail).
- C7 Gaps. CN CLOSTLV `-` in every 2026 month; no numeric RU crude cell in the 2025 or 2026 files; IQ, IR, AE: none in 2025-2026.
- C8 STEO. COPR_WORLD 2015 mean 76.86, 2025 mean 78.99, 2026 mean 75.44 (incl. forecast months, printed only); PASC_OECD_T3 2025-12 =
  2,831.603; T3_STCHANGE_NOECD 2025-12 = −1.714; bulk equals `eia_STEO_m.xlsx` within 0.001 on overlapping months.
- C9 Context. Σ (T3_STCHANGE_WORLD × days) over 2026-01..09 = 424.4 mb (H1 252.3); Σ residual line 2026-01..09 = 145.92 mb from the bulk
  file's full-precision values (145.94-145.95 from the 3-decimal STEO workbook values; pin 145.94 ± 0.05) [A13], 2026-01..07 = 42.6 mb.
- C10 Primary. `primary_test.csv` has one primary row with n ≥ 100, the CI, and a verdict from section 4; report.txt prints the verdict
  sentence with n, N panel members, the mean level and the largest member's variance share; on a DRY_RUN the statistic cells are blank and the
  report says DRY_RUN. No output contains a price column, a p-value, or any barrel sum for a reporters_* group.
- C11 Hygiene. No JODI file under the repository (gate passes); every output's first line names JODI; the build's own commit touches only the
  section 5 files plus `CALENDAR.tsv`, `.gitignore`, `bin/check.sh`, `REPRODUCE.md` and `data/THIRD_PARTY_MANIFEST.tsv`, committed by explicit
  path (the checkout is shared: other sessions' changes may also show in `git status`) [A13].

## 8. Open questions

- **OPEN-1 Run date. RULED 18 Oct [A1].** JODI's schedule puts the update on Wed 21 Oct, noon London. Registration is decided from the file
  (section 4), not the date: a build on the 22 Sep vintage is a blind DRY_RUN.
- **OPEN-2 US level offset.** JODI US crude stocks track EIA's total incl. SPR change for change, but sit 99-145 mb below EIA's level, and the
  gap grew between 2015 and 2025. The 9 mb rise between 2025-01 and 2025-06 is one month: in 2025-03 JODI's STOCKCH is −5,654 KBBL while
  EIA's total rose 3,549 [A4]. Candidates: lease stocks, pipeline fill or Alaska
  in-transit excluded by the IEA definition. Settled by comparing the offset with EIA PSM crude stocks by type (refinery, tank farms and
  pipelines, lease, SPR, in transit) month by month, or by IEA's MOS stock definition.
- **OPEN-3 Old-file vintages.** `2015.csv` was last modified 21 Oct 2025; whether JODI regenerates older annual files when IEA revises OECD
  history is unknown. Settled by `check-vintage` after the 21 Oct update and the seam-check counts.
- **OPEN-4 OECD membership over time.** The code uses the 2026 list for all months; whether STEO's OECD aggregate adds Colombia (2020) and Costa
  Rica (2021) from their accession dates is not stated in the bulk file. Both hold little crude in stock; settled by EIA's STEO definitions page.
- **OPEN-5 Crude definitions.** Whether JODI CRUDEOIL and STEO "crude oil" both include lease condensate was not verified (the JODI manual
  link returned errors to Grok; not retried). Settled by the JODI Oil manual's crude definition and EIA's international crude definition.
- **OPEN-6 IEA terms for OECD history.** JODI's OECD months are IEA Monthly Oil Statistics; IEA's own licence for that content was not
  re-read. Only derived aggregates are committed, so the build does not depend on it; settled by reading iea.org/terms before any
  country-level OECD figure is published beyond the checkpoints.

## Amendments, 18 Oct (second review)

All 13 fixes accepted by the supervisor; each is applied in the body, tagged [An]. The spec author stayed blind on r(D, R) while amending.
- **A1 Blind dry run.** REGISTERED iff `primaryyear2026.csv` Last-Modified ≥ 2026-10-21T00:00Z and max TIME_PERIOD ≥ 2026-08, read from
  `file_stats.csv`, never the clock; otherwise DRY_RUN with blank statistic cells and no correlation computed (G25). Cache names carry
  `_<sha12>`. OPEN-1 ruled. (Sections 1 R1, 4, 8.)
- **A2 Demeaning and the episode condition.** Primary r on calendar-month-demeaned D and R; raw r descriptive. SUPPORTS also needs r ≥ 0.10
  without 2020-03..2020-12 and 2026, else "SUPPORTS (episode-driven)" and "moves with the line" is disallowed. Wording names the largest
  member's share. (3.4, 4; G26.)
- **A3 Frozen panel.** `build --panel-only` writes panels.csv; its sha256 goes into CALENDAR.tsv; the primary refuses a different panel
  (`--panel-sha`). Largest member's variance share, Cov(d_i, D)/Var(D), reported. (3.2, 3.4, 5; G27.)
- **A4 SPR rule and OPEN-2.** Median rule replaces RMS; months with |STOCKCH − ΔMCRSTUS1| > 2,000 KBBL listed. The "9 mb step" is the single
  month 2025-03 (JODI −5,654 vs EIA +3,549, re-checked by the spec author). (C5, OPEN-2.)
- **A5 Coverage by code.** `coverage_reporters` (codes 1, 3) and `coverage_reporters_allcodes`; C3 corrected: all codes 95 / 73.96 / 0.974,
  codes 1 and 3 85 / 61.34 / 0.808, RU code 2 (re-checked). (3.3, 5, C3.)
- **A6 Seams.** January D from −ΣSTOCKCH in the new file when numeric for every member, else `seam_unresolved`, excluded, counted. (3.4; G28.)
- **A7 R3.** "GET or HEAD" (check-vintage uses HEAD).
- **A8 Identity code set.** `all_three_code1`: 702/702 (2025-01..2026-07), 441/441 (2015). (5, C4.)
- **A9 Bootstrap.** Starts `rng.randrange(n − 11)`, k = ceil(n/12) blocks truncated to n, one `random.Random(20261020)`, B = 10,000, sorted
  indices 250 and 9,749; zero-variance resample is a hard failure. (3.4; G29.)
- **A10 Disclosure.** Barrel sums only for fixed panels; changing reporter groups only as coverage ratios at 0.01 and counts; partition
  identity asserted; `aggregates_monthly.csv` split into `panel_aggregates.csv` and `coverage_counts.csv`; gate keys on
  month|period|time_period|date. (R6, 3.2, 5; G30.)
- **A11 Renames and drops.** `gap_residual_mb` → `steo_residual_minus_panel_mb`; no cumulative gap; no OECD level ratio (and the two
  cumulative sums leave primary_test.csv, since they give the cumulative gap). (3.3, 5.)
- **A12 README.** Opens with the plain paragraph (test, Saudi-heavy panel, not world totals, 0.97→0.59 is lost reporters); terms defined at
  first use (also added to the top of this spec); OPEN items last. (Top, 5.)
- **A13 Pins and checks.** C9 residual: 145.92 at full precision, 145.94-145.95 from 3-decimal values, pin 145.94 ± 0.05. Panel level
  re-checked: 241.9-281.8 mb over 2025-01..2026-06 for the 13 members (my 290-340 summed all non-OECD reporters). C11 allows CALENDAR.tsv,
  .gitignore, bin/check.sh, REPRODUCE.md and the manifest in a shared checkout. G3 tests for CRUDEOIL rows and a `/primary/` URL, not the header.
- **A14 Blindness extends to every output (supervisor, 18 Oct, after the build).** In a DRY_RUN no written file may carry D, the non-OECD panel's monthly stock change, or anything from which D can be derived month by month: the `panel_nonoecd_stocks` rows of `panel_aggregates.csv` (level and change) are written with a blank `value` and `suppression` = `withheld_dry_run`; `jodi_panel_nonoecd_draw_mb` and `steo_residual_minus_panel_mb` in `steo_reconciliation.csv` are blank. STEO's own line R may stay. A registered build fills them. Guard `dry_run_no_d` (mutant: a DRY_RUN that writes D must fail) and build check G10 (a scan of every written table and report.txt for the panel's monthly level, change and draw). This overrides section 5's column list for a DRY_RUN. The STEO release date comes from EIA's bulk manifest, fetched once per run (A14b).

## Builder decisions

*Builder, 18 Oct 2026. Where the spec was silent or two parts pulled apart, this is what `bin/build_jodi_oil_ledger.py` does. Nothing below weakens a pin, a guard or a rule.*

1. **File name.** Section 5 names `data/jodi_oil/SOURCES_JODI.md`; the build brief said `SOURCES.md`. The spec wins: the file is `SOURCES_JODI.md`.
2. **README and the R2 lines.** R2 says every output begins with the three lines; A12 says the README opens with one plain paragraph. Both hold: the three lines sit in an HTML comment on the README's first lines (invisible when rendered, present for the gate and for anyone reading the raw file), and the plain paragraph follows at once. `SOURCES_JODI.md` starts with the three lines as visible plain text. Both are hand-written, so `checks.csv` row C11c WARNS when their JODI and EIA lines no longer match the newest fetch (the access date changes with a new fetch).
3. **The fetch log's vintage line.** The log is written before any file is parsed, so its `# vintage:` line lists the files with Last-Modified date and sha prefix and says "max TIME_PERIOD and preliminary months: see file_stats.csv". Every other output carries the full R2 text. The log has two columns beyond the spec's list, `method` and `outcome` (`saved`, `unchanged`, `head`, `STOP:...`).
4. **EIA bulk manifest.** `fetch` requests `https://www.eia.gov/opendata/bulk/manifest.txt` once (it answered 200 on 18 Oct, no redirect), saves the body in the cache and writes the STEO entry's `last_updated` (2026-10-06T16:02:16-04:00) to `raw/eia_steo_release.txt`. The R2 phrase "release of 6 Oct 2026" and "(Oct 2026)" are built from that date (the build reads it; the default is 6 Oct 2026 when the file is absent). The manifest is a 20th-or-earlier request (a full `fetch --all` is 19 requests).
5. **max TIME_PERIOD** (registration, E, `max_period`) is the largest period among rows whose OBS_VALUE is a number, not among all rows. The two agree on the three files the spec read; the difference matters only if JODI ever pads a file with empty rows for months that have not happened.
6. **zero_reported** is decided per annual file: an area whose numeric CLOSTLV cells in that file are all exactly 0 (and at least one is numeric). That reproduces "8 such countries in each 2026 month, e.g. ID and KW" (CY EE ID IS KW LU LV SI). It applies to CLOSTLV only; an INDPROD of 0 is a value.
7. **Stock identity scope (C4).** A country-month counts when both month t and month t-1 lie inside the scope, whichever file holds t-1. That is the reading that reproduces the pins (974/901/712 and 702/702 for `2025-01..2026-07`; 961/894 and 441/441 for `2015`, where January has no December in the scope).
8. **Seams.** A January's D uses STOCKCH from the new file only when every member's STOCKCH is numeric with assessment code 1 or 3 (the usable set used everywhere else); otherwise `seam_unresolved`. `identity_checks.csv` carries one `seam` row per year boundary (code set `all`) and three aggregate rows; `checks.csv` G09 WARNS with the count (70 country-boundaries of 693 on the 22 Sep vintage).
9. **panels.csv lists members only.** `months_usable` therefore equals `months_in_window` on every row by construction; the columns stay so that a future rule that admits partial members can show them. The panel sha256 is the sha256 of the written file, including its three lines, so it is tied to the vintage.
10. **file_stats.csv** has one row per year: the file the build read, which is the newest logged GET whose sha256 matches a cached file. Older vintages stay in the cache and in the log.
11. **Unit relations.** Only KBD x days = KBBL (0.01 KBD) is a hard failure, as the spec says. KL = KBBL x 0.158987 and CONVBBL = 1000 x KBBL / KTONS hold to rounding in the 2026 file but not to the spec's tolerance in older files (KL is reported as an integer by some countries; CONVBBL is off by more than 1 in 13 cells of the older files), so they are counted in `checks.csv` G02b, not enforced.
12. **Coverage columns** `coverage_reporters`, `coverage_reporters_allcodes` and `coverage_panel` are all written to 0.01 (R6 beats the general 3-decimal rule); `coverage_reporters_allcodes` includes codes 2 and 4.
13. **Preliminary months.** A panel total is written only when every member has a usable cell that month; otherwise `value` is blank and `n_members` says how many were present. A forecast STEO month (after STEO's last historical month, read from the crude ledger's copy of the same release, falling back to the end of COPR_SA) carries no ratio and no residual.
14. **DRY_RUN content (A14).** The primary row keeps `n_months`, `n_seam_excluded`, `n_panel`, `panel_mean_level_mb`, `largest_member`, `largest_member_var_share` and `band_1p96_sqrt_n` (single numbers; none involves STEO's line and none gives D month by month); `pearson_r`, `ci95_*`, `spearman_rho` and `verdict` are blank, every descriptive correlation is blank, and descriptive rows keep the label `descriptive`. All correlation functions raise `Blind` during a DRY_RUN. D itself is withheld from every written file (see 21).
15. **Run conditions.** When the panel is too thin or the sample too short the primary row's verdict is `INCONCLUSIVE` and no statistic is computed; the reason (`panel_too_thin`, `too_few_months`) is in `report.txt`.
16. **Descriptive "panel restricted to code-1 cells"** keeps the members whose CLOSTLV is code 1 in every month of W. On the 22 Sep vintage no member qualifies (0 of 9), so that row is blank.
17. **Pins and statuses.** `checks.csv` ids: `G..` are build-time integrity checks (a FAIL stops the build before anything is written), `C..` are the section 7 pins. A pin on a vintage whose three file hashes differ from the 22 Sep ones is WARN, except C5's verdict (`C5v`), C7, C10 and the G checks, which FAIL on any vintage. A FAIL in a C row does not stop the build.
18. **Selftest.** Mutants are in-process switches `on("<name>")`, not edited copies of the file. 47 switches map to the spec's 30 guards (`SPEC_GUARDS` in the script). The fixture has 12 areas (4 OECD, 8 non-OECD) rather than 6, because the statistic path needs a non-OECD panel of at least 5 members; every special case in the spec's fixture is in it. Expected values come from plain arithmetic on the fixture's own arrays; the bootstrap and the primary statistic are pinned to an independent numpy run.
19. **Fetch semantics.** `fetch` always requests the downloads page first (one request). A past-year file already in the cache is not requested again; a year named with `--years` is, unless it was fetched today; the current-year file (linked as `primaryyear<YYYY>.csv`) is requested unless fetched today. A changed file is saved beside the old one (its sha12 is in its name). `check-vintage` sends the page (GET) and a HEAD for each linked year from 2015 to the current one, and compares Last-Modified and Content-Length with the newest logged GET.
20. **Gate.** `bin/check.sh` M12 is warn-only like M9 to M11; it flags a file named `jodi_primary_*`, `primaryyear*` or `secondaryyear*` anywhere, a file whose first line is JODI's header outside `bin/` and `_research/`, and a `data/jodi_oil/` header (other than `checkpoints.csv`) with `ref_area` and a whole-word `month`, `period`, `time_period` or `date`. It was run against four bad trees and each was flagged.
21. **D withheld in a DRY_RUN (supervisor's amendment A14).** `aggregate_rows` and `recon_rows` take `blind`: in a DRY_RUN the non-OECD stock panel's CLOSTLV and DCLOSTLV `value` cells are blank with `suppression` = `withheld_dry_run` (`n_members` and the code counts stay), and `jodi_panel_nonoecd_draw_mb` and `steo_residual_minus_panel_mb` are blank. The OECD ex-SPR and producer panels are not D and stay. `checks.csv` G10 scans every written table (and report.txt) for the 3-decimal form of the panel's level, change and draw in every month, both signs, skipping only cells that hold a different series (OECD and producer panel values, STEO's columns), because three-decimal numbers collide by chance; a hit stops the build. A scan of the 18 Oct outputs without any exemption found 3 cell coincidences, all other series (OECD change 2019-08 twice, STEO's Nigeria production 1.435), and no cell of D. Guard `dry_run_no_d`: with it off, selftest fails in `parse` (the blind rows are not blank) and in `build_dry` (G10 stops the build).
22. **Git identity.** The clone's `user.email` was already set to a personal address when the build started; the builder neither set nor used it and did not commit.
