# Spec: US state and local public pension systems' contributions, benefit payments and assets, survey years 2013-2025 (Census Annual Survey of Public Pensions) (spec author, 26 Oct 2026; rewritten to apply the supervisor rulings of rounds 1-3)

*Item 3 of `_research/2026-10-26-Grok-G11-Scoping.md` (supervisor's choice, 26 Oct). Page context: `docs/index.html` section 07
"Retirement money: the net is not a flow", its open item "Retirement flows after 2023", C-112 and `2026-09-12-Parcel-RET1-Retirement-Flows-Return.md`.
House style follows `_research/2026-10-25-MMF-NonUS-Banks-Spec.md`. Script `bin/census_public_pensions.py`, outputs
`data/census_public_pensions/`, check.sh guard **M25**. The rulings at the end are the record; this body applies them (round 1 O-1 to
O-6; round 2 R2-1 to R2-10, Option A on fix 7; round 3 R3-0 to R3-8). Where rounds conflict, the later one is applied.*

*"Observed" means seen by the spec author on 26 Oct 2026 between 05:43 and 05:54 UTC with the CLAUDE.md neutral User-Agent: 56 requests,
all GET, sequential, about 2 s apart, no redirect followed, no retry (2.7). This rewrite made no new request; every value below comes from
the spec author's cache unless marked "reviewer", meaning derived by the second reviewer from files the author did not hold (the 2018,
2019 and 2020 files). "Relayed" means taken from a project file, a review, the Grok returns or general knowledge, not re-read at source.
**What was seen of the answer before any build (SOURCES.md repeats this):** the spec author summed the national components for 2017,
2021 and 2022-2025 and read the summaries for 2013-2017 and 2021-2024. The second reviewer and Grok then computed the ratios themselves:
benefits per dollar of contributions about 1.313 (2023) and 1.328 (2025), a change of about +1.1%, and the three ratio revisions that
set the band (2.8). **Nothing in this spec is blind**, and no output carries a `blind` column.*

## 0. Goal, and what the result can and cannot say

- **Record** the national totals of contributions (employee, government), benefit payments, withdrawals, investment income,
  administrative and investment expenses, and cash and investments of US state- and locally-administered defined-benefit pension
  systems, survey years 2013-2025, with the published system counts.
- **Describe**, with rules fixed here, benefit payments per dollar of contributions and net cash flow (contributions minus benefits
  minus withdrawals) as a percent of the same survey's opening assets, with the years after 2023 (2024, 2025) set against 2017-2023.
- **Keep apart** from the project's private-plan measures (Form 5500, ICI) and from the Fed's Z.1 pension-sector equity transactions.

**It can say** how much these systems took in and paid out in each survey year, and how that compares with the cash and investments
they reported, on one survey's own definitions. Totals are MEASURED (Census estimates; sample years carry sampling error; every year can
be revised). Ratios and net cash flow are IDENTITY on MEASURED inputs. Nothing about the cash flows was pre-registered (ruling O-5), so
every pattern label is descriptive.

**It cannot say:**
- what the systems bought or sold. A benefit payment is not a sale of equities, and a contribution is not a purchase of them. A gap
  between payouts and contributions can be met from interest and dividends, from cash, or from selling any asset; ASPP does not show which;
- anything about asset classes after 2016. Census streamlined the asset categories with the 2019 release and refitted 2017 and 2018
  to the new schema (2024 methodology, observed), so the current files hold only cash and short-term versus long-term investments.
  **The equity-share question is therefore not asked** (2.5; the Quarterly Survey of Public Pensions is out of scope, ruling O-1);
- anything about private plans, defined-contribution plans or retiree health plans (out of the survey's scope, observed), or about
  any month or calendar year: a survey year is a set of fiscal years (2.2);
- anything about funding status or liabilities. The unit files carry actuarial items (`RP01`-`RP21`); this build does not read them.

**Required README sentence 3 (the one denial sentence, exempt from G14, verbatim):** "It records the pension systems' own accounts
only: a benefit payment is not a sale of equities, a contribution is not a purchase of them, and nothing here shows what the systems
bought or sold in markets."

## 1. Hard requirements

- **R1. Free public data only (E-005).** Host allowlist: `www2.census.gov` only. Refused before the request: every other host,
  explicitly including `api.census.gov` (every query now needs a key, whose sign-up asks for an email address; observed on the developer
  page; never used), `data.census.gov`, any host ending `sec.gov`, FRED or ALFRED, `www.nasra.org` and `www.federalreserve.gov` (the two
  reference constants of C16 and C17 are typed into the script with their citation, never fetched). No API key of any kind.
- **R2. User-Agent** exactly `Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)`; header
  `Accept-Encoding: identity`. The script asserts the UA holds no `@`. Never send an email address, a name, `SEC_UA` or `CLAUDE_CODE_USER_EMAIL`.
- **R3. Crawl conditions.** GET only, sequential, **at least 3 s between requests**, no redirect followed, **no retry of any kind**,
  timeout 120 s, at most **30 requests per run**, at most one run per calendar month. A run fetches the **20 file URLs of 2.4** plus one
  directory listing (`/programs-surveys/aspp/datasets/`, read only to print `NOTICE: new survey year folder <Y>` when a year above 2025
  appears; it fetches nothing more). Never fetched: `datasets/2020/aspp-historical-datasets/ASPP_Unit_File_2020.dsv` (a byte copy of
  2019, R2-1) and any unit file in the `datasets/2024/` root folder (stale, R3-6).
- **R3a. STOP latch (R2-2).** `data/vintages/census_public_pensions/STOP_census` is written only on an HTTP status other than 200
  (any 3xx included, since redirects are not followed), or a body that is empty or is HTML (starts, after whitespace, with `<!` or
  `<html`, case-insensitive). It is created exclusively (`open(..., "x")`) with five `name: value` lines: `status`, `utc_time`,
  `url_path`, `retry_after`, `body_head` (first 300 bytes, escaped). The fetch ends at once. **Only a person deletes a STOP file. No agent
  deletes, renames or overwrites one, the builder included.** With the latch present no request is made; the run prints `STOP present:
  <file>` and exits 2. **A timeout or connection error** prints `FAIL network <path>`, logs it, exits 3, writes no STOP and retries nothing.
- **R3b. Content tests (FAIL, not STOP).** Failures here are recorded as FAIL rows in `checks.csv` (C20) and the file is kept; the build
  still writes its outputs, and success requires no FAIL. Unit file: decodes (R8); every row has exactly 10 fields; the first field of
  every data row is the expected survey year; every item code is one of the **53 codes**: RJ01, RJ10, RJ11, RJ12, RJ20, RJ30, RJ31,
  RJ32; RP01 to RP21 (21 codes); RX01, RX10, RX11, RX12, RX20, RX30, RX40, RX50, RX51, RX52, RX60, RX61, RX62, RX70, RX71, RX72, RX73,
  RX80, RX90, RX91, RX92; RZ01, RZ10, RZ90 (as seen in the 2025 file and the layouts). Summary workbook: opens with `openpyxl`
  (`read_only=True, data_only=True`), has a row whose first cell is `Item`, and a column headed `State & Local` under `United States`.
- **R4. Cache.** A run writes into `data/vintages/census_public_pensions/partial/` (gitignored; the builder adds the rule), one file per
  URL under its own name, plus `manifest.csv` (`url_path, sha256, bytes, last_modified`). When all 20 files have landed, the folder is
  renamed to `<vintage>/`; if that vintage already exists complete, the run removes `partial/` by its exact path, prints `no change`, and
  exits 0. A partial folder is never built. Raw files are never committed (2.6).
- **R5. Vintage key (R3-4)** = the first 16 hex characters of the sha256 of the lines `url_path|last_modified_utc_iso|bytes\n` for all
  20 files, sorted by `url_path`. It is computed from the server's headers, never the wall clock. Each vintage also records
  `newest_unit_file_date` (the UTC date of the newest `Last-Modified` among unit files; 2026-05-14 for the current release, observed),
  and every pin below is stated for "the vintage whose `newest_unit_file_date` is 2026-05-14".
- **R6. Wording (G14).** No causal, flow-direction or motive wording in README.md except the one denial sentence. Flows and positions
  are never written as the cause of a price. Required wording avoids "flow from", "flow to" and "flow into", which `EXTRA_RX` catches.
- **R7. Code ownership.** `bin/census_public_pensions.py` is new, standard library plus `openpyxl` (already installed), and reads no
  project data file other than its own cache. No existing script changes, apart from a new warn-only guard M25 in `bin/check.sh`.
- **R8. Parsing and numbers (R2-2).** Unit files are parsed with the `csv` module (`delimiter="|"` for `.dsv`, `","` for `.csv`, default
  quoting honoured), **never by splitting on commas**: 244 lines of the 2024 file and 292 of the 2025 file quote a system name that
  contains a comma (observed). Decode as UTF-8 with BOM, and if that fails as cp1252 (the 2017 and 2021 `.dsv` files fail UTF-8 at a
  0x92 byte and have no BOM, observed), the encoding logged per file. A first row starting `SAMPLE_YEAR` is a header (2022-2025 files have
  one; 2017 and 2021 have none, observed); fields by position in the layout order `Year|Name|ID|State|Government Type|Item Code|Value|EIC|ISC|Weight`.
  Values and weights are `decimal.Decimal`, summed in Decimal; a blank value adds nothing (Census's convention: it reproduces the published
  totals). Unit-file values are whole dollars; summary workbooks are in **thousands of dollars** (observed: 2024 benefits 405,454,166 =
  $405.45bn); summary CVs are **fractions** (2024: contributions 0.0020546, benefits 0.0010266; ruling R3-0). Every money column is
  `_usd_mn` with 3 decimals (exact to the thousand dollars); per-dollar ratios 4; `pct`, `pp` and `change_pct` 3; CVs as published,
  7 decimals; system counts integers. Rounding (Python's default half-even) only at write time.
- **R9. Post-registration fixes** go in SOURCES.md "Builder decisions" with the old value kept beside the new, never in the README.
- **R10. No pairing across sources.** No output cell combines an ASPP figure with any other source, with one exception: the reference
  checks C15-C17 in `checks.csv`, which never reach the README's tables. A flow is divided only by assets from the same cache vintage
  key ("same release", R2-4): the previous survey year in the same schema (`_start`, primary) or the same survey year (`_end`, secondary).

## 2. Data

### 2.1 What ASPP is (observed)

The Census Bureau's survey of state- and locally-administered defined-benefit public pension systems (form F-11): revenues, expenditures,
financial assets and membership. A **census** (the README says "full-count year") of all systems in years ending in 2 and 7 (2017, 2022:
every weight is 1, observed); a **sample** in other years, with a weight per row so that "multiplying the values by weights and summing"
recreates the published national estimates (layout PDF, observed; reproduced to the thousand dollars for 2017, 2021 and the 2025 press
figures, and for 2018 and 2019 by the reviewer). Methodology (2024): response rate 77.0%; total-quantity response rate for cash and
investments 99.1%; nonrespondents imputed (flags `EIC`, `ISC`). The 2024 methodology calls the microdata public record (Title 13; relayed
from the second reviewer and Grok). Annual since 1957.

**System counts (R3-7, R2-10).** The layout says the number of systems is "not generated from unit file", so a unit-file row or unit
count is never written as a system count. `systems_published` comes from each year's summary workbook: 3,992 (2013), 3,972 (2014),
6,299 (2015), 6,276 (2016), 5,529 (2017), 5,302 (2021), 4,634 (2022), 4,566 (2023), 4,535 (2024) (observed; 2018-2020 read by the
build). "All systems" means this published count; the 2022 unit file holds 4,394 units. 2025 has no summary workbook, so the column is
blank; the 2025 publication's count (311 state and 4,061 local systems) is quoted in the README as text.

### 2.2 Timing: what "2025" means (observed, 2024 methodology)

"The survey year encompasses the fiscal year beginning July 1 of the previous survey year and June 30 of the current survey year."
Systems whose fiscal year ends after 30 June report their previous fiscal year. Exceptions: state systems in **Alabama and Michigan**
report October-September, **Texas** September-August. So survey year 2025 is mostly July 2024 to June 2025. **When holdings are measured
is not stated** in the publication, the layouts, the 2013 tables page or the 2024 methodology (author and reviewer, observed); the README
says so (ruling O-3) and the column name `assets_end_usd_mn` is marked as an assumption in the column dictionary (R2-8). The share of
assets in the three exception states is not computed (round 3, not adopted; it stays this note). **The README calls years "survey year
2025", never "2025" alone in a table header, and never sets them beside calendar-year or quarterly series.**

### 2.3 Items and schemas

**Current schema (survey years 2017-2025; item codes from the "2017-2024" and "2022-2025" layout PDFs, identical apart from the file
format sentence, observed).** Published lines and their item codes, literal:

| Column | Codes (layout's mapping) | Summary label (2020 source, cross-check elsewhere) |
|---|---|---|
| `contrib_employee_usd_mn` | RX51 + RX52 | `Employee contributions` |
| `contrib_government_usd_mn` | RX60 + RX70 | `Government contributions` |
| `contrib_total_usd_mn` | RX51 + RX52 + RX60 + RX70 | `Total Contributions` |
| `benefits_usd_mn` | RX40 | `Total Benefits Paid` |
| `withdrawals_usd_mn` | RX80 (refunds to members who leave) | `Withdrawals` |
| `earnings_ex_gains_usd_mn` | RX01 (= RX10 + RX20; excludes gains) | `Earnings on investments` |
| `gains_losses_usd_mn` | RX30, signed (8 negative rows in 2025, 24 in 2024) | `Gains/Losses on Investments` |
| `expenses_admin_invest_usd_mn` | RX90 (administrative and investment expenses; R2-7) | `Administrative Costs` |
| `assets_end_usd_mn` | RZ01 (= RZ10 + RZ90) | `Total cash and investments` |

Never added on top of these: RX50 (equals RX51 + RX52), RX61/RX62, RX71-RX73, RX91/RX92 (sub-lines), RJ (membership), RP (actuarial).
Sub-line identities are WARN only (C12): in 2023 RX60 exceeds RX61 + RX62 by 560.031 $mn (observed), so the published total line is used.

**Old schema (2013-2016, summary workbooks only).** Labels, literal: `Total Contributions`, `Employee contributions`, `Government
contributions`, `Benefits`, `Withdrawals`, `Earnings on investments`, `Total cash and investment holdings`, `Number of systems`. **Old
"Earnings on investments" includes gains** (2013: 374,337,076 thousand; Grok relays the 2015 brief's $168.7bn, down 68%), so it goes
to `earnings_old_schema_usd_mn`, never to `earnings_ex_gains_usd_mn`; `gains_losses_usd_mn` and `expenses_admin_invest_usd_mn` are blank.
The old 2013-2016 unit `.txt` files have no weight field (2013, observed) and are not used.

**Sign trap (observed):** 2023 and 2024 summaries print `Investment Losses` as a positive number (2023: gains 219,219,955 minus losses
135,427,585 = 83,792,371 net); the build never reads `Investment Gains` or `Investment Losses`, only the signed net line.

**Breaks inside the window (R3-3, R2-10).** (a) **2014 to 2015:** systems jump from 3,972 to 6,299; the 2015 brief (relayed via Grok,
`https://www.census.gov/content/dam/Census/library/publications/2016/econ/g15-aspp-sl.pdf`, not fetched by the author) says more than
2,200 local systems were added, that the data may include hybrid and other post-employment funds, and that 2012 and 2015 should be
compared only with caution. (b) **2016 to 2017:** schema, earnings definition and asset detail change. So **no change statistic is
computed within the old schema at all, and none spans 2016/2017** (G7). Old-schema years appear only as single-year rows.

### 2.4 Files (all on `https://www2.census.gov/programs-surveys/aspp/`; 20 files)

| Survey years | Path under the base | Role |
|---|---|---|
| 2013-2016 | `tables/<Y>/aspp-historical-tables/<Y>asppsummary.xlsx` (4 files) | old-schema national totals (all fetched by the author) |
| 2017, 2018, 2019, 2021, 2022, 2023 | `datasets/<Y>/aspp-historical-datasets/ASPP_Unit_File_<Y>.dsv` (6) | current-schema totals (2017, 2021, 2022, 2023 fetched; 2018, 2019 fetched by the reviewer) |
| 2024 | `datasets/2024/aspp-historical-datasets/ASPP_Unit_File_2024.csv` only (R3-6) | current-schema totals (fetched; `Last-Modified` 14 May 2026) |
| 2025 | `datasets/2025/aspp-historical-datasets/ASPP_Unit_File_2025.csv` | current-schema totals (fetched) |
| 2017-2023 | `datasets/<Y>/aspp-historical-datasets/ASPP_<Y>_Summary.xlsx` (7) | the **2020 totals** (R2-1); cross-check and CVs for the others (2017, 2021, 2022, 2023 fetched by the author) |
| 2024 | `datasets/2024/ASPP_2024_Summary.xlsx` (folder root) | cross-check, CVs (fetched) |
| 2025 | none posted as a workbook | CVs blank |

**2020 (R2-1, reviewer):** `datasets/2020/aspp-historical-datasets/ASPP_Unit_File_2020.dsv` has the same sha256 as the 2019 file
(`f7e0fb45…3382`) and every year field says 2019. It is never fetched; 2020 comes from `ASPP_2020_Summary.xlsx` (`source_kind = summary`).
**2024 (R3-6):** the root folder `datasets/2024/` holds same-named unit files (`.dsv`, `.xlsx`) dated 23 May 2025, before the revision;
they are never fetched (G19, C19). The two layout PDFs and `datasets/2024/ASPP 2024 methodology.pdf` were read once by the author and are
cited in SOURCES.md, not fetched by the build.

### 2.5 Asset classes: what ASPP lacks

The 2013-2016 summaries carry corporate stocks and other classes (2016 corporate stocks 1,350,618,217 thousand). From the 2017 schema on,
only RZ10 and RZ90 exist. Census points users wanting "granular asset details" to the redesigned Quarterly Survey of Public Pensions
(methodology, observed); it is out of scope (ruling O-1). No equity share is computed, and no ASPP figure is set beside a holding of
equities from any other source.

### 2.6 Licence

Census's citation page (observed) asks users who make their own estimates to "cite the Census Bureau as the source of the original data
only". The 2024 methodology treats the data as public record (relayed). Federal works carry no US copyright (17 U.S.C. 105; relayed; the
open-data policy page answered 301 and was not followed). Raw files stay in the gitignored cache as a house choice (size, about 70 MB per
release, and they name individual systems), not a licence requirement; committed files hold national totals only. Citation in every
CSV's `# source:` line and the README: U.S. Census Bureau, Annual Survey of Public Pensions, survey years 2013-2025, unit files and
summary tables, https://www.census.gov/programs-surveys/aspp.html, vintage `<key>` (newest unit file `<date>`).
`www2.census.gov/robots.txt` (observed) names only a few crawlers and disallows nothing for others.

### 2.7 Requests made by the spec author (goes to SOURCES.md, not the README)

`www.census.gov` (13): the three scoping URLs; `/programs-surveys/aspp/data/tables.html`, `/data/api.html`, `/data/datasets.html`,
`/data/historical_data.html`; `/programs-surveys/aspp/technical-documentation.html`; `/data/developers/data-sets/govspension.html`;
`/data/tables/2013/econ/aspp/aspp-historical-tables.html`; `/about/policies/citation.html`, all 200; `/about/policies/open-gov/open-data.html`
**301, not followed**; `/robots.txt` **404**. `www2.census.gov` (43), all 200: the two layout PDFs, the 2025 publication PDF, the 2024
methodology PDF, `/robots.txt`; directory listings of `datasets/`, `datasets/2013/`, `2016/`, `2017/`, `2021/`, `2022/`, `2024/`, `2025/`,
the `aspp-historical-datasets/` subfolders of 2013, 2016, 2017 (twice: an inadvertent repeat), 2018, 2019, 2020, 2021, 2022, 2023,
2024, 2025, and the file-layouts folder and its `2017-2024/`; files: unit files 2013 (`.txt`), 2017, 2021, 2022, 2023 (`.dsv`), 2024,
2025 (`.csv`); summaries 2013, 2014, 2015, 2016, 2017, 2021, 2022, 2023, 2024. No request to `api.census.gov` or `data.census.gov`.
Spec author's copy: `<session-scratchpad>/g11/aspp_raw/`, temporary, selftest fixture seed only, not a vintage. **Unverified figure
(R3-2):** Grok relayed $286.21bn as 2022 contributions from indexed text of the data.census.gov table `GOVSPENSIONTIMESERIES.GS00PENSION`,
which it could not render; SOURCES.md records it as unverified, and no data.census.gov fetch is added.

### 2.8 Release and revisions (observed unless marked)

- Release dates: survey year 2024 files posted 23 May 2025 (folder dates); survey year 2025 unit file and press release (CB25-TPS.31)
  on **14 May 2026**; the 7-page publication (G25-ASPP) in September-October 2026. The next release (survey year 2026) is not announced;
  May 2027 is expected on this pattern (relayed inference). **Survey year 2025 is a first release; the next release is expected to revise
  it, together with earlier years back to 2022** (R3-7).
- **Each release revises earlier years.** On 14 May 2026 the 2022, 2023 and 2024 unit files were re-posted; 2017-2021 files still carry
  23 May 2025. Against the 23 May 2025 summaries: 2022 contributions 282,833.491 to 287,958.518 $mn (+1.812%), 2022 gains -163,541.867
  to -115,465.262, 2024 benefits 405,454.166 to 404,460.423 (-0.245%), 2024 contributions -0.420%, 2023 contributions -0.037%. The
  ratio `benefits_per_contrib_usd` moved **-1.898% (2022, a census year), +0.102% (2023) and +0.176% (2024)** (author's cache, matching
  the reviewer). The press release's 2024 figures ($404.46bn, $5.98trn) are the revised ones.
- Handling (R3-2): every national row carries its source file's `Last-Modified` date. `revisions.csv` is regenerated on every build, never
  appended, from (a) each year's summary against its unit file where their dates differ, and (b) every adjacent pair of complete cached
  vintages. Where a same-vintage published total exists, C04 compares to its rounding; a different-vintage gap is a revision row, not a failure.
- Small published-rounding note: the press release says benefits rose 3.40% from 2024; the unit files give 3.409%. In SOURCES.md; not a check.

## 3. Method

1. **Fetch** (mode `fetch`): the 20 files of 2.4 under R3-R5; every request logged with status, bytes, sha256 and `Last-Modified`.
2. **Parse** each unit file under R8 and sum value x **that row's own weight** per item code. In 2023, 515 units carry a second weight
   on rows RX70-RX73; four of those rows are non-blank (RX71-RX73 sub-lines) and no summed total moves (observed, matching the reviewer).
   C12 prints the counts only, never unit IDs or values.
3. **Census-year rule:** in 2017 and 2022 every weight must be 1 (FAIL otherwise); in a sample year at least one weight must exceed 1 (WARN otherwise).
4. **Select by label or code, never position**, from the literal lists of R3b and 2.3. An unknown item code or a missing label is a FAIL
   listing every unknown together.
5. **National rows** (`national.csv`): exactly 13, one per survey year 2013-2025. 2013-2016 and 2020 from summaries (`source_kind =
   summary`); the other years from unit files (`source_kind = unit_file`). From each year's summary, where one exists: `systems_published`,
   and the CVs where the workbook prints them (`summary_file_date` = that workbook's date); CVs blank for 2025 and for census years.
   **CV scale (R3-0):** FAIL if any national sample-year CV read for contributions, benefits or assets is above 0.05 (C18), because that
   means the column has changed to percent. `net_cash_usd_mn` = contributions - benefits - withdrawals (negative when payouts exceed
   contributions; the data's sign, tested in G5).
6. **Ratios** (`ratios.csv`), each naming its denominator:
   - `benefits_per_contrib_usd` = benefits / total contributions;
   - `benefits_withdrawals_per_contrib_usd` = (benefits + withdrawals) / total contributions;
   - `net_cash_pct_of_assets_start` = 100 x net cash / the previous survey year's assets, same vintage, same schema (blank for 2013 and
     2017; ruling O-6 leaves 2012 unfetched) — **primary for Q3** (R2-4);
   - `net_cash_pct_of_assets_end` = 100 x net cash / the same survey year's assets — secondary;
   - `income_per_net_cash_gap_usd` = earnings excluding gains / (benefits + withdrawals - contributions); current schema; blank if the
     denominator is not positive;
   - `income_per_gap_after_expenses_usd` = earnings excluding gains / (benefits + withdrawals + expenses - contributions), expenses = RX90;
     current schema; blank if the denominator is not positive (R2-7);
   - `ratio_cv_bound_pct` = 100 x (CV of benefits + CV of contributions), CVs as fractions (R3-0): a ceiling on the sampling CV of
     `benefits_per_contrib_usd` under any correlation (BOUNDED); 0 in census years; blank where CVs are not posted (2025).
7. **Revision band (R2-3).** `revision_band_pct` = the largest absolute percent revision of `benefits_per_contrib_usd` between a year's
   summary and its unit file in the first build (expected 1.898, set by the 2022 census-year re-post); `revision_band_sample_years_pct` =
   the same over sample years only (expected 0.176; the two sample-year values are 0.102 and 0.176). After the first build the builder
   **hard-codes `FROZEN_BAND_PCT`** in the script, logs it in Builder decisions, and every later build uses that constant (the build is
   offline and byte-identical; R7 forbids reading the value from elsewhere).
8. **Change and pattern (R2-3, R3-1).** For a ratio change from year a to year b: `change_..._usd` = ratio_b - ratio_a (pattern `n_a`);
   `change_..._pct` = 100 x (ratio_b / ratio_a - 1), which alone carries a pattern: `above_band` if it exceeds +`FROZEN_BAND_PCT`,
   `below_band` if below -`FROZEN_BAND_PCT`, else `within_band`. Changes in pp get `n_a`. A description against one past revision, not a test.

## 4. Questions, fixed in advance (answers in `summary.csv`; levels in `national.csv` and `ratios.csv`)

**4.0 Scale of noise (C-090, C-092 discipline).** Descriptive; no test and no MDE claim. Two noises bound what can be read: sampling error
(published CVs of 0.04%-0.25% on the lines used in 2023-2024) and revisions, which have been larger (1.8% on 2022 contributions). The band
is set by one census-year re-post. Both the band and the 2023-2025 change (about +1.1% on the press-release figures) were seen before the
band was frozen. `within_band` means "smaller than one past revision", not "no change".

**Endpoints:** 2017 (first current-schema year, census), 2022 (census), **2023** (the last year with official private-plan flows on the
page), 2025 (latest).

- **Q1. Levels.** Every column of `national.csv`, survey years 2013-2025 (`national.csv` is the answer; no `summary.csv` rows).
- **Q2. Benefit payments per dollar of contributions.** Each survey year 2013-2025 (single-year rows, both schemas). Changes 2017 to 2023,
  2023 to 2024, 2024 to 2025 and **2023 to 2025**, each as `change_benefits_per_contrib_usd` (`n_a`) and `change_benefits_per_contrib_pct`
  (with pattern). **Primary row (the only `primary = yes`): `change_benefits_per_contrib_pct`, segment `current`, 2023 to 2025.**
  Everything else is exploratory.
- **Q3. Net cash flow as a percent of opening assets.** `net_cash_pct_of_assets_start` each year (current schema 2018-2025; old schema
  2014-2016) and its change 2018 to 2023 and 2023 to 2025 (`change_net_cash_start_pp`); `net_cash_pct_of_assets_end` each year and
  `change_net_cash_end_pp` for the same spans, secondary; `n_years_net_cash_negative` per segment. All pp changes `n_a`.
- **Q4. Investment income against the net cash gap** (current schema only): `income_per_net_cash_gap_usd` and
  `income_per_gap_after_expenses_usd` each year, 2023 and 2025 named. README wording: "interest, dividends and other investment income
  per dollar by which payouts exceeded contributions", given both without and with administrative and investment expenses, and the
  sentence that the table does not show which money paid which benefit.
- **Q5. Revisions.** `max_abs_revision_pct__<item>` for each of the eight items; `ratio_revision_pct` per revised year (2022, 2023, 2024);
  `revision_band_pct` and `revision_band_sample_years_pct` (frozen).
- **Q6. Sampling bound.** `ratio_cv_bound_pct` for 2023 and 2024 (2025 blank; the README says no 2025 CV file is posted on www2).
- **Not asked:** the equity share (2.5); any change within the old schema or across 2016/2017 (G7); any figure against Form 5500, ICI or Z.1.

**4.4 How it sits beside the project's other retirement measures (README item 7, plain words).**
- The page's private measures (Form 5500 and ICI, defined-contribution plans, plan years to 2023) cover different plans on different
  dates. ASPP does not extend them, and nothing here is added to, subtracted from or compared in one number with them. The extension of
  the private series is the 2024 Form 5500 file, a separate task (scoping note, REJECTED list).
- The Fed's Z.1 records state and local defined-benefit plans' net equity transactions (C-112: -$463.9bn, 2024:Q1-2026:Q2). That is a
  market-transactions measure on calendar quarters; ASPP is a cash account on fiscal years. They are never set side by side, and an
  ASPP benefit total is never described as selling. (C17 compares a Z.1 asset level with ASPP assets as a reference check only.)
- The page's sentence "Official flow data stops there; only levels run to 2025, and the two must never be paired" stays true of
  private plans. Whether the page gains a public-plan line is the supervisor's decision after the build.

### 4.5 The pre-registered statement (ruling O-5)

Nothing is registered about the cash flows themselves. **S1 is registered with its CALENDAR row:** "In the first Census release carrying
survey year 2026, the re-posted survey year 2025 `benefits_per_contrib_usd` differs from this build's 2025 value by less than
`FROZEN_BAND_PCT`." Scored on that release (expected May 2027; identified by a 2026 folder under `datasets/` and a new vintage key),
written as `s1_revision_2025_pct` (pattern `within_band` = HELD, otherwise not held). **Honesty note:** the band is the largest of three
past revisions, so on history S1 holds by construction; it checks that the after-2023 figures are stable enough to quote. A failed S1 is a
result and is written beside the old value. CALENDAR row (text): `2027-05-31`, "ASPP survey year 2026 release (expected May 2027, not
announced): run `python3 bin/census_public_pensions.py fetch` then `build`; read `revisions.csv` for 2022-2025; score S1 (HELD if the
2025 benefits-per-contribution revision is inside FROZEN_BAND_PCT in Builder decisions); add 2026 to the year table only through a logged spec change".

## 5. Outputs

**Script `bin/census_public_pensions.py`.** Modes `fetch`, `build` (offline, byte-identical on re-run), `selftest` (synthetic, no
network, under 20 s). Committed files in `data/census_public_pensions/`; each CSV begins with one `# source:` line (2.6 citation,
vintage key and newest unit-file date, retrieval date taken from `fetch_log.csv`).

**Header allowlist, canonical text.** One line per file, `<name>:<headers comma-joined, no spaces>`, each ending in LF, in this order.
The script holds `SPEC_ALLOW_SHA256`; **`bin/check.sh` holds its own literal copy of these seven lines** and never reads them from the
script. G12 and M25 skip the `# source:` line.

```
national.csv:survey_year,schema,year_kind,contrib_employee_usd_mn,contrib_government_usd_mn,contrib_total_usd_mn,benefits_usd_mn,withdrawals_usd_mn,net_cash_usd_mn,earnings_ex_gains_usd_mn,earnings_old_schema_usd_mn,gains_losses_usd_mn,expenses_admin_invest_usd_mn,assets_end_usd_mn,systems_published,cv_contrib_total,cv_benefits,cv_assets,summary_file_date,source_kind,source_file_date,vintage
ratios.csv:survey_year,schema,benefits_per_contrib_usd,benefits_withdrawals_per_contrib_usd,net_cash_pct_of_assets_start,net_cash_pct_of_assets_end,income_per_net_cash_gap_usd,income_per_gap_after_expenses_usd,ratio_cv_bound_pct,vintage
summary.csv:question,segment,from_year,to_year,statistic,value,unit,pattern,primary,vintage
revisions.csv:survey_year,item,source_prev,date_prev,value_prev_usd_mn,source_new,date_new,value_new_usd_mn,change_usd_mn,change_pct
checks.csv:check_id,description,expected,observed,status
vintages.csv:vintage,newest_unit_file,newest_unit_file_date,files,requests,manifest_sha256
fetch_log.csv:utc_time,host,path,status,bytes,sha256,last_modified
```

**sha256 of that text (1,072 bytes): `652a264d517b39f333a2a1270ca4abb4e140d40a1235c64ef98905c40a2bbdb9`** (computed by the spec author for this rewrite).
Superseded: `89c23bb9022dda49a9689fb43f693aa1fb8192ce4c9ddc6d9bd633a10900b22b` (first draft) and the reviewer's Option A block
`51d7c485959f3842a9c63cc55c7b614982c1a7e7b03478805da5b12bc4400ec3` (before R3-7 added `systems_published` and `cv_source_date` became
`summary_file_date`). A builder who needs a column changes this text and its hash first, logs it in Builder decisions, and tells the supervisor.

**Allowed values:** `schema` and `segment` in {old, current}; `year_kind` in {census, sample}; `source_kind` and `source_prev`/`source_new`
in {unit_file, summary}; `item` in {contrib_employee, contrib_government, contrib_total, benefits, withdrawals, earnings_ex_gains,
gains_losses, assets_end}; `question` in {Q1, Q2, Q3, Q4, Q5, Q6, S1}; `statistic` in {benefits_per_contrib_usd,
change_benefits_per_contrib_usd, change_benefits_per_contrib_pct, net_cash_pct_of_assets_start, net_cash_pct_of_assets_end,
change_net_cash_start_pp, change_net_cash_end_pp, n_years_net_cash_negative, income_per_net_cash_gap_usd,
income_per_gap_after_expenses_usd, max_abs_revision_pct__contrib_employee, max_abs_revision_pct__contrib_government,
max_abs_revision_pct__contrib_total, max_abs_revision_pct__benefits, max_abs_revision_pct__withdrawals,
max_abs_revision_pct__earnings_ex_gains, max_abs_revision_pct__gains_losses, max_abs_revision_pct__assets_end, ratio_revision_pct,
revision_band_pct, revision_band_sample_years_pct, ratio_cv_bound_pct, s1_revision_2025_pct}; `unit` in {usd_per_usd, pct, pp, count};
`pattern` in {above_band, below_band, within_band, n_a}; `primary` in {yes, no}. Key of `summary.csv` (question, segment, from_year,
to_year, statistic) unique; `from_year` blank for single-year rows.

- **`README.md`** (generated; G14 scans it), in this order, plain words, with glosses for "full-count year" (census year), "sample year",
  `segment`, `schema`, CV ("coefficient of variation: the sampling error as a share of the estimate"), `pp` and `within_band`:
  1. **Opening, verbatim (R2-8):** "This table shows how much US state and local government pension systems took in and paid out in each
     survey year from 2013 to 2025. These systems promise retirees a set benefit. Money in is what employees and governments paid in;
     money out is benefits to retirees and refunds to members who left. Beside it are the cash and investments the systems reported
     holding. The figures are the Census Bureau's national estimates from its Annual Survey of Public Pensions. Survey year 2025 covers
     the fiscal years that most systems ended on 30 June 2025. Census does not say on what date holdings are measured; we take it to be
     the end of each system's fiscal year."
  2. Sentence after the opening: the denial sentence of section 0.
  3. "Survey year 2025 is a first release, and the next release is expected to revise it and the years back to 2022." (R3-7)
  4. Timing: survey years, the 30 June rule, the Alabama, Michigan and Texas exceptions.
  5. What is counted: the nine lines; "net cash flow = contributions minus benefits minus withdrawals", which is neither the press
     release's gap of benefits minus contributions ($103.23bn in survey year 2025) nor NASRA's external cash flow (R3-5); investment income
     here excludes gains; administrative and investment expenses are a separate line.
  6. Full-count and sample years; sampling error; "no 2025 CV file is posted on www2" (R3-5, O-4); system counts as published (2.1);
     **the old years, in the 2015 brief's facts (R3-3):** more than 2,200 local systems were added in 2015, the data may include hybrid and
     other post-employment funds, 2012 and 2015 should be compared only with caution, and old "earnings on investments" include gains;
     then the 2016/2017 schema break, as the reason no change is computed in or across the old years.
  7. The other retirement measures (4.4), with the private-plan sentence "The project's figures for private defined-contribution plans
     stop at 2023 and cover different plans on different dates; nothing in this table is added to, subtracted from or compared in one
     number with them."
  8. Levels and ratios in plain tables; the primary row named first and the rest called exploratory; the band paragraph of 4.0 (set by one
     full-count-year re-post of 1.898%; sample-year revisions 0.102% and 0.176%; both band and change seen before freezing; `within_band`
     means smaller than one past revision, not no change); the Q3 sentence: "End-of-year assets include that year's investment gains
     ($493.6bn in survey year 2025), so net cash flow is a smaller share of end-of-year assets in years with large gains; the share of
     opening assets is the main measure for that reason." (R2-4)
  9. Revisions and vintages. 10. Column dictionary, every ratio with its denominator; `assets_end_usd_mn` marked as an assumption about
     timing (R2-8). 11. The Census citation. The questions of section 4 do not appear in the README.
- **`SOURCES.md`:** every URL with access date and status (2.7, the 301 and 404 included), the layout mappings, the label lists, the 53
  codes, the timing quote, the schema-change quote, the 2015 brief (relayed), the licence text, the unverified $286.21bn figure (R3-2),
  the citations of the C15-C17 constants, the disclosure paragraph of the header, and **Builder decisions** (encodings per file,
  `FROZEN_BAND_PCT`, new item codes, every post-registration fix with old and new values).

## 6. Leak and integrity rules

1. Committed: only the seven CSVs, README.md and SOURCES.md. No `.dsv`, `.xlsx`, `.txt`, `.pdf`, `.html`, `.zip`; no line containing
   `SAMPLE_YEAR`; no match anywhere in a line (no `^` anchor; R2-9) for the quote-aware raw-row pattern
   `(?<!\d)\d{4}(?:\|[^|\n]*\||,(?:"[^"]*"|[^,"\n]*),)\d{6}[|,][A-Z]{2}[|,]\d[|,]R[XZJP]\d\d[|,]`; no local path (`/Users/`,
   `/private/`, `~`); no `@`. On the author's cache this pattern matches every data row of the 2017, 2021, 2022, 2023, 2024 and 2025
   unit files, quoted names included, and none of the planned output rows. (The reviewer's version, `[^|,]*` in the name field, missed
   pipe-file rows whose names contain a comma: 184 of 181,563 in 2017.)
2. System names are tested only in the selftest, against a planted name list (G13); `check.sh` has no cache and does not try.
3. Nothing is written outside `data/census_public_pensions/` and the gitignored cache, apart from the `.gitignore` rule and a
   REPRODUCE.md paragraph (landing).

## 7. Selftests (synthetic only; each guard applies its own mutant, and an uncaught mutant fails the selftest)

**G14's literal patterns, both compiled with `re.I`** (pasted, not imported). `CAUSAL_RX`:

```
\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of)\b
```

`EXTRA_RX`:

```
\b(?:in|out)flows?\b|\bflows?\s+(?:into|out\s+of|from|to)\b|\bnet\s+(?:sell|buy)(?:ers?|ing)\b|\b(?:sell|sells|sold|selling|sale|sales|buy|buys|bought|buying|purchas(?:e|es|ed|ing))\s+(?:of\s+)?(?:equit(?:y|ies)|stocks?|shares|bonds|assets)\b|\bforced\s+(?:sell|sale)\w*|\bliquidat\w*|\bsell[- ]?off\b|\bbid\b|\bdrain\w*|\bdeplet\w*|\bunderfunded\b|\binsolven\w*|\bcrisis\b|\brunning\s+out\b|\bretirement\s+flows?\b
```

| Guard | Protects | Mutant that must be caught |
|---|---|---|
| G1 parsing | R8 | a header row summed as data; a header-less file's first data row skipped; cp1252 bytes decoded with `errors="ignore"` and the row count changing; a 9-field or 11-field row accepted; `,` used on a `.dsv`; **a split on `,` instead of the `csv` module** (fixture: a quoted name containing a comma) |
| G2 weights | method 2-3 | an unweighted sum; the unit's modal weight applied to all its rows; weight applied twice; a census-year fixture with one weight 1.5 accepted; C12 printing a unit ID or value instead of counts |
| G3 line mapping | 2.3 | RX50 added to RX51 + RX52; RX61/RX62 or RX71-RX73 added to their totals; RX30 added into `earnings_ex_gains`; RX91/RX92 added to RX90; RX90 counted as a payout in `net_cash`; substring code matching (`RX5` selecting RX50-RX52) |
| G4 labels and codes | method 4 | a 54th code accepted; a missing summary label filled with zero; unknowns reported one at a time instead of together; a summary column chosen by position (fixture with columns reordered) |
| G5 signs | 2.3, method 5 | `abs()` on RX30 (fixture with a -5 row); `net_cash` as benefits - contributions; withdrawals added instead of subtracted; `Investment Losses` read as a gain; the pin "2025 net cash negative" passing on a sign-flipped fixture |
| G6 units | R8 | a summary read as dollars (1,000 times too small); a unit file read as thousands; `$bn` written to a `_usd_mn` column |
| G7 breaks | 2.3 | any change row with both years in 2013-2016 (fixture: 2014 to 2015); a change row with `from_year` 2016 or earlier and `to_year` 2017 or later; old earnings in `earnings_ex_gains_usd_mn`; `_start` for 2017 computed from 2016; `income_*` written for an old-schema year |
| G8 numbers | R8 | floats summed (fixture of 10,000 cent-weighted rows whose float sum is off by more than 0.0005 $mn); rounding before dividing; wrong decimals in a column |
| G9 vintage key | R5 | key from the wall clock; key from the newest unit file alone (a fixture where only an older year's file changes must change the key); a size left out of the hashed lines; `Last-Modified` parsed in local time (a 23:30 GMT fixture landing on another day) |
| G10 revisions | 2.8 | `revisions.csv` appended rather than regenerated; a same-date summary differing by 5 thousand dollars accepted; a different-date gap written as FAIL instead of a revision row; the `partial/` folder treated as a vintage |
| G11 ratios and band | method 6-8 | `pct` not multiplied by 100; `_start` divided by the same year's assets; `_end` divided by the previous year's; **an absolute change (`usd_per_usd`) compared with the percent band**; a pattern on a pp change; `rose`/`fell` written; the band recomputed on a second vintage instead of `FROZEN_BAND_PCT`; `revision_band_sample_years_pct` including 2022; `income_per_gap_after_expenses_usd` without RX90; more than one `primary = yes` |
| G12 allowlists | 5 | an extra or renamed column; `SPEC_ALLOW_SHA256` not the sha256 of the canonical text; `# source:` compared as a header; an eighth CSV; **check.sh reading the header lines from the script**; a duplicate key in `summary.csv`; a `statistic` or `question` outside its list |
| G13 leak guard | 6 | **on a planted bad folder** with a raw `.dsv`, a unit-file row pasted into a `.csv`, **a quoted-name `.csv` row inside a Markdown table**, a planted system name from the selftest's name list, and a `/Users/` path in SOURCES.md, each reported; **on the clean folder it passes** |
| G14 wording | R6 | the patterns above, applied to README.md everywhere but the denial sentence (SOURCES.md is not scanned). The opening and the private-plan sentence pass; the denial sentence is exempt (it matches `sale of equities`); adding "pensions were net sellers" fails; "benefit payments drove equity sales" fails; "money flows out of stocks" fails; "a forced sale of assets" fails; "retirement flows after 2023" fails; "net cash flow from members" fails |
| G15 STOP latch | R3a | **AST scan**: a STOP path reached by `os.remove`, `os.unlink`, `os.replace`, `os.rename`, `shutil.rmtree`, `shutil.move`, `Path.unlink`, `Path.rename`, `Path.write_text`, `Path.write_bytes` or `open` in mode w or a (only `x` allowed); a delete over the cache root or by glob (removing `partial/` by exact path is allowed). Runtime: with a planted `STOP_census`, `fetch` makes no request, exits 2, file sha256 unchanged; fixture 301, 403, 404, 429, an empty body and an HTML body each write `STOP_census` with five fields; **a field-count or year failure writes no STOP** (FAIL row instead); **a timeout writes no STOP**, retries nothing and exits 3 |
| G16 fetch safety | R1-R3 | `api.census.gov`, `data.census.gov`, `www.nasra.org`, `www.federalreserve.gov`, `www.sec.gov` or `fred.stlouisfed.org` requested; `@` in the UA; a redirect followed; requests under 3 s apart; any retry; a 31st request; a URL not in 2.4; **the 2020 unit file requested** |
| G17 isolation | R7, R10 | **AST scan**: the script opens any path outside its cache and output folder (fixture: reading `data/series.tsv` or a Form 5500 file); an output column other than `checks.csv` C15-C17 combining ASPP with a constant from another source |
| G18 CV scale | method 5 (R3-0) | a fixture summary whose CV column is in percent (0.20546) accepted; the bound computed without the 100 x on fractions; a census-year CV other than blank |
| G19 2024 path | 2.4 (R3-6) | the 2024 unit file taken from `datasets/2024/` (root) instead of `datasets/2024/aspp-historical-datasets/ASPP_Unit_File_2024.csv`; a 2024 unit file whose `Last-Modified` is earlier than 2026-05-14 accepted on a vintage whose `newest_unit_file_date` is 2026-05-14 or later |

## 8. Pinned checks (`checks.csv`)

**Pin rules.** Values in $mn to three decimals (exact to the thousand dollars). Pins on files dated 2026-05-14 (2022-2025) FAIL on the
vintage whose `newest_unit_file_date` is 2026-05-14 and WARN on a later vintage with their `revisions.csv` rows. Pins on older files WARN
if `revisions.csv` has a row for that cell, else FAIL.

- **C01 Survey year 2025 (unit file, 2026-05-14, sha256 `ce8e85af…b1533e`):** contributions 315,020.924 = employee 78,232.942 +
  government 236,787.982; benefits 418,247.000; withdrawals 8,662.260; earnings excluding gains 123,246.347; gains 493,615.768; expenses
  32,488.230; assets 6,490,183.499. The publication shows $6,490,183,499,000, total earnings $123.2bn, withdrawals $8.7bn.
- **C02 Survey year 2024 (unit file, 2026-05-14):** contributions 304,507.314; benefits 404,460.423; withdrawals 8,485.325; expenses
  30,383.985; assets 5,984,012.295 (press release: assets up 8.46%).
- **C03 Survey year 2023 (unit file, 2026-05-14):** contributions 294,746.197; benefits 386,915.776; withdrawals 8,073.515; expenses
  26,164.033; assets 5,484,493.565.
- **C04 Same-vintage comparison, every year (R3-2), and the 2022 census pin.** Each year's weighted unit-file sum (contributions,
  benefits, withdrawals, assets) is compared with the published total of the same vintage wherever one exists: a summary with the same
  `Last-Modified` date, to the thousand dollars (2017, 2018, 2019, 2021: FAIL if off by more than 1 thousand), or for 2025 the press
  release, to its rounding (C15). Where the vintages differ (2022, 2023, 2024 against their 23 May 2025 summaries), the gap goes to
  `revisions.csv`, not to a failure. **2022 pin (unit file, 2026-05-14, census):** contributions 287,958.518; benefits 368,117.415; gains
  -115,465.262 (negative); expenses 27,858.658; assets 5,422,683.528; 4,394 units, every weight 1.
- **C05 Survey year 2017, census (unit file and summary both 2025-05-23):** contributions 200,567.477; benefits 297,948.620; withdrawals
  7,047.012; expenses 17,254.773; assets 4,077,278.537; 5,529 units, every weight 1; the file decodes only as cp1252.
- **C06 Survey year 2021, sample (both 2025-05-23):** contributions 247,844.543; benefits 352,030.838; expenses 25,378.773; assets 5,616,036.664.
- **C07 Old schema (summaries, 2018 files):** 2013 contributions 152,814.152, benefits 242,324.376, withdrawals 5,808.003, assets
  3,289,331.745, systems 3,992; 2016 contributions 190,647.517, benefits 283,350.356, withdrawals 6,123.396, assets 3,733,413.704,
  systems 6,276; systems 2014 3,972 and 2015 6,299.
- **C08 Revisions (2025-05-23 summary to 2026-05-14 unit file):** 2022 contributions 282,833.491 to 287,958.518 (+5,125.027); 2024
  benefits 405,454.166 to 404,460.423 (-993.743); ratio revisions -1.898% (2022), +0.102% (2023), +0.176% (2024); hence
  `revision_band_pct` 1.898 and `revision_band_sample_years_pct` 0.176 on the first build.
- **C09 Sign:** 2025 `net_cash_usd_mn` is negative; benefits - contributions = 103,226.076, Census's "minimum earnings to fill the gap"
  ($103.2bn, which leaves out withdrawals). 2025 has 8 negative RX30 rows and they stay negative.
- **C10 Census years:** every weight 1 in 2017 and 2022; at least one weight above 1 in every sample year read from a unit file.
- **C11 Fixed output:** a second `build` leaves every sha256 unchanged.
- **C12 Sub-lines and weights (WARN, counts only):** RX60 vs RX61 + RX62 and RX70 vs RX71-RX73 per year (2023: -560.031 and -12.930);
  the number of units with a second weight and the number of non-blank rows carrying it (2023: 515 and 4).
- **C13 Tamper check:** in every `national.csv` row, employee + government = total contributions and net cash = contributions minus benefits
  minus withdrawals, each within 0.002 $mn. These hold by construction; the check exists only to catch a hand-edited file.
- **C14 2018-2020 (reviewer, R2-1; not re-derived by the author):** 2018 (unit file, equal to its summary to the thousand): contributions
  218,847.610, benefits 311,712.813, withdrawals 7,141.871, assets 4,345,989.226. 2019 (unit file, equal to its summary): 226,284.675,
  322,701.634, 6,913.836, 4,442,571.521. 2020 (summary): 241,972.089, 336,659.802, 7,060.712, 4,597,361.334.
- **C15 C-press (FAIL, R3-8):** survey year 2025 contributions round to $315.02bn, benefits to $418.25bn, assets to $6.49 trillion, and
  2024 benefits to $404.46bn (press release CB25-TPS.31, 14 May 2026; constants typed in, with citation).
- **C16 C-NASRA (WARN, R3-8):** NASRA Public Fund Survey FY 2024, "$5.13 trillion" (relayed via Grok and the supervisor, not fetched),
  is between 80% and 95% of the build's survey year 2024 assets (author's cache: 85.7%). Different universe; a level check only.
- **C17 C-Z1 (WARN, R3-8):** Fed Z.1 table S129.3.s "Funded by assets", 2025:Q2, $6,541.4bn (relayed, not fetched), is within 3% of the
  build's survey year 2025 assets (author's cache: 0.8% above). A level check only; no Z.1 transaction series is read.
- **C18 CV scale (FAIL, R3-0):** every national sample-year CV read for contributions, benefits and assets is at most 0.05 (largest seen
  on any line of the author's cached summaries: 0.0334, 2013).
- **C19 2024 path and date (FAIL, R3-6):** the 2024 unit file came from `datasets/2024/aspp-historical-datasets/ASPP_Unit_File_2024.csv`
  and its `Last-Modified` is 2026-05-14 or later on this vintage.
- **C20 Content tests (FAIL):** no R3b failure in any file (listed together if any).

## 9. Success criteria

1. `python3 bin/census_public_pensions.py selftest` prints G1 to G19 with every mutant caught and exits 0.
2. `fetch` obeys R3-R5 (3 s spacing, no retry, at most 30 requests, all logged, the 2020 unit file and the 2024 root files never
   requested). If a STOP is written, the builder stops, tells the supervisor, and never deletes it.
3. `build` on the vintage whose `newest_unit_file_date` is 2026-05-14: C01-C11, C13-C15 and C18-C20 PASS. Acceptable WARNs: C12, C16 and
   C17 inside their ranges, and pins on a later vintage with revision rows. Every other WARN goes to the supervisor.
4. `national.csv` has exactly 13 rows, survey years 2013 to 2025, contiguous.
5. **A verifier re-derives by hand** from the cached 2025 unit file: the weighted sum of RX40 = 418,247,000,165.45 dollars and of RX51 +
   RX52 + RX60 + RX70 = 315,020,923,752.43 dollars (or the same vintage's re-posted values).
6. **M25** (warn-only, in `bin/check.sh --all`), with its own copy of the seven header lines: file names; headers (skipping `# source:`);
   no raw file, `SAMPLE_YEAR`, raw-row match, local path or `@`; no G14 pattern in README.md outside the denial sentence; C13's identities
   on every `national.csv` row (✗ if not); **no `summary.csv` change row within the old schema or spanning 2016/2017** (✗); `pattern` only
   from its four values (✗); no duplicate key (✗). On a scratch copy with a planted `.dsv`, a renamed header, a 2015-to-2018 change row and
   a `net_cash` with its sign flipped, M25 prints four ✗ lines; on the clean folder, ✓. It is shown failing on the planted copy before it lands.
7. **Supervisor hash step:** extract the allowlist block from this spec, take its sha256, and compare it with `SPEC_ALLOW_SHA256` in the
   script and with check.sh's literal block; all three must equal `652a264d517b39f333a2a1270ca4abb4e140d40a1235c64ef98905c40a2bbdb9`.
8. **README cold-reader test.** Three fresh agents read only the README: a non-specialist, a public-pension practitioner, and a third told
   to find the 2023-to-2025 primary row and say what it shows. **Pass** only if the first two can state the population (state and local
   defined-benefit systems), what a survey year covers, that sample years carry sampling error and figures get revised, and which single row
   is primary, and the third reports the percent change and its band label and does not read `within_band` as "no change". **Fail** if any
   reader believes the table shows pension systems selling equities, measures money leaving the stock market, or extends the private-plan figures.

**Landing (builder):** the `.gitignore` rule; a REPRODUCE.md paragraph; S1's CALENDAR row (registered, ruling O-5); `FROZEN_BAND_PCT` in
Builder decisions; a HANDOVER row. The builder commits nothing; the supervisor verifies and writes any findings text or page change.

## 10. OPEN questions

Closed by the rulings: O-1 (QSPP out of scope), O-2 (separate old segment, now with the 2015 brief's facts), O-3 (not stated; README says
so), O-4 (README wording per R3-5), O-5 (S1 registered), O-6 (2012 not fetched). Open:

- **O-7 README opening length.** R2-8 adopts the reviewer's seven-sentence opening; the house lesson asks for two plain sentences. The
  body applies R2-8 (the later ruling) verbatim; the supervisor may cut it.
- **O-8 C14 and the 2020 duplicate.** The 2018-2020 pins and the 2020 file's sha256 (`f7e0fb45…3382`, truncated as reported) come from
  the second reviewer; the author holds neither file and made no new request for this rewrite. The first build confirms or corrects them
  (logged under R9).
- **O-9 Old-schema `_start`.** `net_cash_pct_of_assets_start` for 2015 divides by 2014 assets across the 2014/2015 system-count jump; it
  is a single-year value, not a change, so G7 allows it, but the supervisor may blank 2015's `_start`.
- **O-10 2025 system count.** No 2025 summary exists; `systems_published` is blank and the README quotes the publication's 311 + 4,061 as
  text. The supervisor may prefer the publication's figure in the column, labelled by source.

## Supervisor rulings

*Appended here by the supervisor, newest last, all before any data run; they override the body.*

## Supervisor rulings, 26 Oct 2026 (before any data run)

- **O-1:** the Quarterly Survey of Public Pensions is out of scope (a separate future spec, never paired with these flows).
- **O-2:** 2013–2016 stay as a separate, labelled segment; no change across the 2016/2017 break; the README says the definitions are assumed comparable from their labels.
- **O-3:** the builder quotes Census's own wording on when assets are measured, or the README says it is not stated.
- **O-4:** the README says 2025 has no published sampling error.
- **O-5:** S1 (a revision statement) is registered with its CALENDAR row; nothing is registered about the cash flows themselves.
- **O-6:** the 2012 summary is not fetched.
- **Blindness:** the spec author summed components for several years before the build; the primary ratio is therefore not blind, and SOURCES.md says so.
- **Guard number:** **M25**.
## Supervisor rulings, round 2 (second review), 26 Oct 2026 — before any data run

All ten fixes are accepted, Option A on fix 7:
- **R2-1** The 2020 unit file on www2.census.gov is a byte copy of 2019 (same sha256, every year field 2019); it is not fetched, and 2020 comes from `ASPP_2020_Summary.xlsx` (`source_kind = summary`). Pins C14 for 2018, 2019 and 2020 as the reviewer derived them.
- **R2-2** `STOP_census` only on a non-200, a redirect, or an HTML or empty body; other content failures are FAILs in `checks.csv`; a timeout or connection error is FAIL and exit, no retry, no STOP. The 53 item codes are pasted in; parsing uses the `csv` module with quotes, never a split on commas.
- **R2-3** `pct_change = 100 × (ratio_to / ratio_from − 1)` carries the pattern and `primary = yes` (`change_benefits_per_contrib_pct`); the absolute change is printed with `pattern = n_a`; pp changes get `n_a`; `revision_band_pct` (the 2022 census-year revision, 1.898%) is printed beside `revision_band_sample_years_pct` (0.102% and 0.176%), and the README says the band is set by one census-year re-post; `FROZEN_BAND_PCT` is hard-coded after the first build and logged.
- **R2-4** Q3 uses `net_cash_pct_of_assets_start` (opening assets), with `_end` secondary and the README sentence on investment gains in end-of-year assets; "same release" means the same cache vintage key.
- **R2-5 / R2-6** The counts and cross-references are corrected; Q5 uses one statistic name per item; `question` values are enumerated.
- **R2-7 (Option A)** `national.csv` gains `expenses_admin_invest_usd_mn` (RX90) and `ratios.csv` gains `income_per_gap_after_expenses_usd`; new allowlist block and hash.
- **R2-8** The README opening is the reviewer's replacement text; `assets_end` is noted as an assumption in the column dictionary.
- **R2-9** The quote-aware raw-row regex without the `^` anchor and a quoted-name fixture; C11 prints counts only.
- **R2-10** The smaller points as listed, including the 2014→2015 system-count jump (no change joins 2013–2014 to 2015–2016), the 13-row criterion, and a third cold reader who reads the primary row.

## Supervisor rulings, round 3 (Grok attack), 26 Oct 2026 — before any data run

Grok (fenced, read + web; 34 fetches, no breaches, every cited URL fetched) said BUILD WITH CHANGES. I checked the 14 May 2026 Census release myself: $315.02bn contributions, $418.25bn benefits, $6.49 trillion assets, 2024 benefits $404.46bn. All four match.

- **R3-0 (overruled: CV scaling).** Grok says the summary CV is already a percentage, so `100 x` overstates the bound a hundredfold. In the workbooks the spec reads, it is a fraction: `ASPP_2024_Summary.xlsx`, Table 1, gives Total Contributions CV 0.0020546 and Total Benefits Paid CV 0.0010266, so the bound is about 0.31% as written. The formula stands. Add Grok's guard the other way round: FAIL if any national sample-year CV read from a workbook is above 0.05, because that means the column changed to percent.
- **R3-1 (accepted, on top of R2-3).** R2-3 already compares a percent change with a percent band. The ruling registered nothing about the cash flows, so the pattern labels are descriptive. Rename them `above_band` / `below_band` / `within_band`, not `rose` / `fell`. The README says the band and the 2023–2025 change (about +1.1% on the press-release figures) were both seen before the band was frozen, and that `within_band` means "smaller than one past revision", not "no change".
- **R3-2 (accepted, amended).** C04 compares each year's weighted unit-file sum with the published total of the *same vintage* wherever one exists: a summary workbook with the same `Last-Modified` as the unit file, or the press release for 2025, to the rounding shown. When vintages differ, the gap is reported as a revision in `revisions.csv`, not as a failure. The 2022 pin stays the measured 14 May 2026 weighted sum. Grok's third 2022 figure ($286.21bn, from indexed text of a data.census.gov table it could not render) is recorded in SOURCES.md as unverified. No data.census.gov fetch is added.
- **R3-3 (accepted).** The README replaces "the labels match" with the 2015 brief's facts: more than 2,200 local systems were added; the data may include hybrid and other post-employment funds; 2012 and 2015 should be compared only with caution; old "earnings on investments" include gains. Keep the 2016/2017 schema break and the separate earnings columns.
- **R3-4 (accepted).** The cache vintage key is a hash over every fetched file's `Last-Modified` and size, not the 2025 file alone.
- **R3-5 (accepted).** Write "no 2025 CV file is posted on www2", not "no sampling error was published". `RX90` stays its own column. The net-cash identity is named in the column dictionary as contributions − benefits − withdrawals, distinct from the press-release gap of benefits minus contributions ($103.23bn in 2025) and from NASRA's external cash flow. The denominator is opening assets (already R2-4).
- **R3-6 (accepted).** The 2024 unit file is fetched only from `datasets/2024/aspp-historical-datasets/ASPP_Unit_File_2024.csv` (14 May 2026). The same-named file at `datasets/2024/` dated 23 May 2025 is stale and never fetched; a guard checks the path and the date.
- **R3-7 (accepted).** Add the published system counts from the summaries, labelled as such (the layout says a unit-file row count is not a system count). Add one line: survey year 2025 is a first release, and the next release will revise it back through 2022.
- **R3-8 (new pre-registered reference checks).** C-press (FAIL): 2025 national sums round to $315.02bn, $418.25bn and $6.49 trillion, and 2024 benefits to $404.46bn. C-NASRA (WARN): NASRA's FY 2024 $5.13 trillion is 80–95% of the build's 2024 assets. C-Z1 (WARN): the Z.1 S129.3.s "funded by assets" figure at 2025:Q2 ($6,541.4bn) is within 3% of the build's 2025 assets. The aggregate-versus-median NASRA cash-flow comparison is dropped, because an aggregate and a median are not comparable.
- **Not adopted:** the state-level asset share for Alabama, Michigan and Texas (out of scope for a national build; it stays a note).

## Supervisor rulings, round 4 (open questions after the rewrite), 26 Oct 2026 — before any data run

- **R2-9 regex:** the author's corrected pattern is adopted. **Rename** `cv_source_date` to `summary_file_date`: adopted.
- **O-7 README opening:** house style wins. The opening is two plain sentences (what the table is and the headline 2023–2025 change, with its label meaning). The reviewer's remaining sentences go in the paragraph that follows, as definitions. No sentence of the reviewer's content is dropped.
- **O-8 2018–2020 pins:** the first build confirms the 2018 and 2019 pins from the unit files and the 2020 pins from the summary. The 2020 duplicate's sha256 is removed from the pins, because the file is never fetched. SOURCES.md records the duplicate as the second reviewer's observation.
- **O-9 2015 opening-asset ratio:** blank, with the reason in the row's note. Its denominator is 2014 assets, which cross the 2014→2015 jump in system count.
- **O-10 2025 system count:** taken from the 14 May 2026 publication if it prints a national count, with `source_kind = publication`; otherwise blank. It is never estimated.
