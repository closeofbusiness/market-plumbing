# Swap-tape ledger: build specification (v2, 14 Oct 2026, amended by §17)

*Status: SPEC, amended after two adversarial reviews, and BUILT on 14 Oct 2026 (§18 records the build). It serves the goal row "rates, FX and commodities" (E-021; RESEARCH_STATE §5
build queue, item "swap-tape ledger"; Grok g4 item 3). It is written under E-024, which binds every section below. The author re-derived the
load-bearing 13 Oct 2026 figures independently, with stdlib code against the cached zip; figures marked (lens) are relayed from the three
investigation lenses and were not re-derived. Figures marked (pre-A) were computed before the §17 amendments and describe the old
full-day, converted-spread headline; they are context, not targets. Sections 0-16 were edited on 14 Oct to agree with §17 (the
supervisor's amendments, kept below as the record of what changed); §18 lists what the builder decided where §17 was silent.
Nothing here says a flow moves a price: the ledger measures levels and gaps.*

## 0. What the ledger is

A daily table, from the DTCC public price dissemination (PPD) CFTC cumulative interest-rate files, of:
(1) USD SOFR OIS fixed rates minus Treasury par (CMT) yields at 2, 5, 10, 30y ("swap spread"), headline taken from prints executed in the
two hours around the CMT's 15:30 New York snapshot and **quoted** the way dealers quote it (no conversion), with a bond-equivalent
conversion published beside it;
(2) USD CPI zero-coupon swap rates against the Treasury par breakeven (par minus TIPS par real) at 5, 10, 30y, stated as a **gap
between two different instruments**, never as one breakeven;
(3) the spread on the non-USD leg of OIS-versus-SOFR cross-currency swaps, EUR/USD, JPY/USD and GBP/USD, per tenor 1-5y and pooled over
1-5y (`pool1to5`), published only above a count floor.
The lone-package swap-spread series that the schema lens found (swap-against-Treasury packages, a second route to (1)) is **deferred**
(A6): it is not built in the first landing.

## 1. Contradictions to the brief and to the earlier outside spec (read first)

1. **`Product name`, `Underlier ID-Leg 1/2` and `Underlier ID source-Leg 1` are blank in 25,885 of 25,885 rows.** Products are identified by
   `UPI FISN` and `UPI Underlier Name`. The outside spec's "abort if the chosen label has n=0" would abort on every file.
2. **`Action type == NEWT` is not a trade filter.** On 13 Oct, NEWT = 22,662 rows: Event type TRAD 17,858, COMP 4,642, NOVA 91, EXER 71.
   Keep NEWT with Event type TRAD, drop errors (EROR), substitute corrections (CORR) (§5).
3. **The fixed leg is not always Leg 1.** In the 13 Oct OIS rows that pass F0-F4 and the tenor bucket (§6), before the day-count and platform
   filters, the fixed rate sits on Leg 2 in 2/149, 8/252, 13/399, 7/169 rows at 2/5/10/30y (pre-A). The USD leg of a cross-currency swap is
   Leg 1 in 3/72 EUR/USD TRAD rows (lens). Identify legs by which fixed rate is filled and by `Notional currency-Leg 1/2`, never by position.
   For 11 of the 1,732 rows that pass F0-F4, the fixed-rate leg's day-count and payment-frequency columns are blank and the other leg's
   carry them (A5, CR5): the build reads the convention from either leg.
4. **The outside spec's conversion assertion is false.** It said the bond-equivalent minus raw gap stays within 0 to +5bp for rates of 0-10%.
   Computed: +1.89bp at 3%, +1.16 at 4.5%, +0.89 at 4.8%, +0.68 at 5%, 0.00 at 5.556%, −0.65 at 6%, −10.59 at 10% (365/360 accrual
   factor). The sign flips at r = 4·5/360 = 5.556%. Under A2 the conversion is not the headline: the quoted spread is.
5. **"EUR/USD 1y basis negative" is not a valid success criterion.** EUR/USD has printed positive at 2-5y (ING, 14 Nov 2024: +1/+2/+3/+3bp,
   lens) and on 13 Oct sits at −3.25bp at 1y on n=6 (pre-A). Only JPY/USD's sign is robust across the evidence the lenses read. §12 replaces
   the sign check with a count and a date-specific value.
6. **A uniform "blank `Other payment amount`" filter would drop most cross-currency trades.** Their other payments are principal exchanges
   (`PEXH`): 24 of the 26 bucketed EUR/USD rows and 24 of 24 GBP/USD rows on 13 Oct carry one. Only `UFRO` (upfront) is excluded there.
7. **Minimum and maximum are single trades' rates.** The outside spec published `min_raw`/`max_raw`. E-024 allows medians, quartiles and
   counts; min and max are dropped from every committed output, and the publication floor of A4 applies everywhere (n < 5: the count only;
   5 <= n < 10: count and median; n >= 10: also quartiles).
8. **Classifying package-spread units by testing the implied Treasury against the CMT is circular** (the schema lens did so): it forces the
   route to agree with the CMT. The package series is deferred (A6); when it is built, units are set by magnitude and agreement with the
   CMT route is a test, not an input.
9. **HEAD is not supported** on `pddata.dtcc.com/ppd/api/...` (edge 503 on 14 Oct; lens). GET only; the script never sends HEAD (A8). The API
   sends no Content-Length, ETag or Last-Modified on large files and ignores Range.
10. **"The archive starts 14 Oct 2024" (E-021 note, item 3) is not established.** 2024-10-11 is 404 and 2024-10-14 is 200; 2024-10-12/13
    were not probed, and 2024-10-14 is exactly 730 days before 14 Oct 2026, so a rolling two-year window fits as well as a fixed start (§11).
    The guide's "366 days" describes the dashboard listing, not the API, which served 2024-10-15 through 2025-10-15 (lens).
11. **The file for date D holds what was published on D (UTC), not everything executed on D.** 331 of 22,662 NEWT in the 13 Oct file were
    executed earlier (42 on 12 Oct, 35 on 9 Oct; lens), so trades executed on D also arrive in later files. The first landing reads the
    file of D only (the D+1...D+K late-file machinery is deferred, A6): a trade executed on D and published after D is absent from D's
    ledger row, and a correction published after D is not applied to it.
12. **Neutral User-Agent strings disagreed across the repo.** `bin/pull_series.py` sent `ThirdDerivativeResearch/1.0 (market-plumbing)`;
    `bin/r1_treasury_decomposition.py` sends `Mozilla/5.0 (research; free public data)`; CLAUDE.md's working rules name
    `Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)` for every non-SEC host. A13 settles it: this build uses
    the CLAUDE.md string and asserts it contains no `@`.
13. **Archive facts (A15; the archive lens, relayed).** The DTCC dashboard listing holds 366 entries; 9 of them were published more than
    60 minutes late; the 2026-09-29 file has 27,133 rows (the listing's rowCount, an independent count); the S3 ETag of a large file equals
    the md5 of the zip (so a cached zip that matches the ETag is DTCC's object); and 2024-10-11 returns 404.

## 2. E-024 conditions as hard requirements

| # | Requirement | How the build enforces it |
|---|---|---|
| R1 | Non-commercial use | Stated in `data/swap_tape/SOURCES.md`, in the README and in the script docstring |
| R2 | No raw DTCC file or row committed or redistributed | Zips live only in the cache (default `~/dtcc_ppd/`, override `DTCC_PPD_CACHE`); the script refuses a cache whose realpath is inside the repo; zips are read in memory, never extracted to disk; `.gitignore` gains `CFTC_CUMULATIVE_RATES_*`; outputs hold only medians, quartiles, counts and shares, under the A4 floor; no min/max; no weighted median; every output writer refuses any field that is a whole string of 8 to 19 digits (a Dissemination Identifier, legacy ids included), and file sizes are written in kB with a decimal point for that reason; `bin/check.sh` carries a warn-only guard M9 (A9) |
| R3 | Derived statistics cite DTCC | `data/swap_tape/SOURCES.md` (written by the script, deterministic text): "Derived from DTCC Public Price Dissemination, CFTC cumulative interest-rate reports (pddata.dtcc.com). Statistics only; no DTCC record is reproduced. Non-commercial research (THE_ASK.md E-024)." plus the Treasury source; every CSV under `data/swap_tape/` starts with a `# source:` comment line naming DTCC and the retrieval dates (A10) |
| R4 | Sequential, paced requests | One request at a time; at least 5 seconds between request starts (`--sleep`, default 5, refused below 5), measured with `time.monotonic()` inside an invocation and persisted across invocations in `<cache>/.last_request`; at most `--max-requests` per invocation (default 60, hard cap 100); a lock file `<cache>/.fetch.lock` (O_EXCL) stops two fetchers running at once, is removed in a `finally`, and a stale lock (dead pid or older than six hours) is detected and replaced |
| R5 | Any technical refusal ends the run | §4 stop rules; a `STOP` file is written at the fixed path `~/dtcc_ppd/STOP` (whatever `--cache` says) with the reason, and every later `fetch` and `fetch-ust` refuses to run while it exists. Only a human deletes it. No retry, ever |
| R6 | Neutral User-Agent, no address | `UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"` hardcoded (A13); asserted at import to contain no `@` and not to contain the values of `SEC_UA` or `CLAUDE_CODE_USER_EMAIL` when set (compared, never printed); headers are exactly `User-Agent` and `Accept-Encoding: identity`; no cookie handling; redirects are not followed and count as a refusal |
| R7 | Ruling's scope only | Allowed hosts: `pddata.dtcc.com` (path prefix `/ppd/api/report/cumulative/cftc/`) and `home.treasury.gov` (path prefix `/resource-center/data-chart-center/interest-rates/`). Any other host, and any `sec.gov` host, raises. The S3 host and ICE are not used |

## 3. Script and command line

One file, `bin/swap_tape_ledger.py`, Python 3 standard library only (csv, zipfile, io, hashlib, http.client, datetime, zoneinfo, math,
argparse). House style follows `bin/census_nport_bulk.py` (streamed read, aggregate outputs, a provenance file with sha256) and
`bin/pull_cftc_cot.py` (network fetch separated from an offline, byte-identical rebuild).

```
python3 bin/swap_tape_ledger.py fetch --dates 2025-04-09,2026-09-29 | --start D --end D  [--cache DIR] [--sleep 5] [--max-requests 60]
python3 bin/swap_tape_ledger.py fetch-ust --years 2024,2025,2026   # Treasury par and real CSVs into data/vintages/swap_tape_ust/
python3 bin/swap_tape_ledger.py build --start D --end D [--cache DIR] [--out data/swap_tape] [--ust-dir DIR]   # never touches the network
python3 bin/swap_tape_ledger.py selftest                           # synthetic fixture, mutants, stop logic; no network, no DTCC rows
```

`fetch` takes weekdays only, skips dates already cached or recorded as holes (no request), and does not request a date later than today
(UTC) minus 2 days. `build` is an upsert (A12): it rewrites the rows of the weekdays it is given in every output and leaves other dates alone.
A weekday with no cached file gets a `no_file` status row; one with no CMT row gets `no_ust`; a file that fails the header check gets
`schema_mismatch`; a failed assertion gets `error`. It goes on to the next date and never fetches. Treasury files:
`https://home.treasury.gov/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{y}/all?type={t}&field_tdr_date_value={y}&page&_format=csv`
with `t` in {`daily_treasury_yield_curve`, `daily_treasury_real_yield_curve`} (the R1 route), saved as `{t}_{y}_fetched-{YYYYMMDD}.csv`;
`build` uses the newest copy per year and records its sha256. `.gitignore` gains `CFTC_CUMULATIVE_RATES_*` and `data/vintages/swap_tape_ust/` (as R1 does).

## 4. Fetch rules

URL: `https://pddata.dtcc.com/ppd/api/report/cumulative/cftc/CFTC_CUMULATIVE_RATES_{YYYY}_{MM}_{DD}.zip`. GET only (never HEAD), timeout 120s,
body cap 50MB. Written to `<cache>/<name>.zip.part`, checked, then renamed. A body is accepted only if it starts with `PK\x03\x04`,
`zipfile.testzip()` returns None, and it holds exactly one member named `CFTC_CUMULATIVE_RATES_{YYYY}_{MM}_{DD}.csv` for the requested date.

| Response | Outcome |
|---|---|
| 200 and an accepted zip | `saved` |
| any HTTP status other than 200 (including 401, 403, 407, 429, 451, any 3xx, any 5xx), a 200 that is not an accepted zip (an HTML page, a wrong member, a body over the cap) | **STOP**: write `~/dtcc_ppd/STOP`, log, exit non-zero |
| 404 for a date more than 366 days old | `hole`: recorded in `data/swap_tape/holes.csv` with its reason; does not latch; later `fetch` runs skip it (the older year is undocumented by DTCC, so its 404s are holes, not refusals) |
| a socket fault (timeout, reset, TLS error) | the invocation ends without latching; nothing is retried |
| date later than today (UTC) minus 2 days | `not_yet`: no request is sent (files appear about 00:15 UTC on D+1, median 15 min, nine of 366 more than an hour late, some Saturdays on D+2; lens) |
| date before 2024-10-11, the first date probed | `before_archive`: no request is sent |

Weekend dates are not requested. Every request appends one row to `data/swap_tape/fetch_log.csv` (§9). Treasury requests follow the same
pacing, lock and stop rules, and the same latch file; a Treasury body is accepted only if it is a CSV whose header has a `Date` column.

## 5. Parsing and one price per executed trade

Read the member through `io.TextIOWrapper(encoding="utf-8-sig", newline="")` and `csv.reader`. **Header check (A11):** the build requires only
the columns it uses (listed in the script as `REQUIRED`), matched by name and not by order, after a rename map for known version changes
(empty in v1). The 110 names of the 13 Oct 2026 file are frozen as `HEADER_V1` only to log the names added and removed (diagnostics
`header_added`, `header_removed`). A date whose file lacks a required column gets the ledger status `schema_mismatch` and nothing else
(no guessing; 2024-10-15 and 2025-04-15 also have 110 columns, names not compared; lens). Assert `Dissemination Identifier` is unique within each file.

**Files per ledger date D:** the file of D only. The late-file window (D+1...D+K) and the `provisional` flag are deferred (A6).

**Resolution (exact).** Children of a row are the rows whose `Original Dissemination Identifier` equals its id, self-references ignored.
Starting from each row with `Action type == NEWT` and `Event type == TRAD`:
1. Discard children that themselves have an `EROR` child.
2. If the current version has an `EROR` child and no `REVI` child with a later `Event timestamp` than the latest of those `EROR` rows, the trade is dropped.
3. If it has `CORR` children, the current version becomes the latest by (`Event timestamp`, then the larger `Dissemination Identifier`, compared
   as integers); repeat from 1, at most 10 steps. (The tie-break is arbitrary but deterministic: A5, CR12.)
4. Every field is read from the final version, except Event type, which is the NEWT's (CORR rows carry a blank Event type).
`MODI`, `TERM` (ETRM, CLRG, NOVA, EXER, CLAL) and `NOVA`/`EXER`/`COMP` NEWT rows are not price observations and are ignored; they are
counted. **Counts on 13 Oct (builder's run, corrected wording, CR13).** Of the 3,223 rows that carry an Original Dissemination Identifier:
1,804 point to a parent in the same file (CORR→NEWT 810, MODI→NEWT 403, TERM→NEWT 378, EROR→NEWT 210, REVI→NEWT 3); 39 point to themselves
(TERM 28, CORR 8, EROR 2, MODI 1; ignored); and 1,380 name a parent that is not in the file (earlier days' trades). There are no
CORR→CORR or EROR→EROR pairs to a different row on this date. For USD SOFR (the F0 labels of §6.1), 4,399 NEWT/TRAD rows carry the two labels; 34 of them are dropped because an EROR child cancels them, which leaves the 4,365 that the funnel shows at F0 (builder's run, reproducing the author's figure).

## 6. Series, filters and variants

**Common steps, in order, each a funnel row (§9):**
F0 resolved trades of the series; F1 execution date (UTC, first 10 characters of `Execution Timestamp`, which ends in `Z`) equals D, which
also drops the placeholder rows stamped `2000-01-01T00:00:00Z` (31 rows in the 13 Oct file: 23 NEWT, all TRAD, of which 21 survive the EROR rule, and 8 MODI; lens, confirmed by the builder); F2 spot start: 0 <= `Effective Date` − execution date <= 5 days
(13 Oct SOFR lags: 0d 59, 1d 58, 2d 1,794, 3d 16; lens); F3 no upfront (series-specific, below); F4 `Post-priced swap indicator` not `true`
and `Non-standardized term indicator` not `TRUE` (case-insensitive); **F4s `Strike Price` blank (option-exercise swaps are dropped, A5)**;
F5 leg structure; F6 conventions (the convention columns are read from either leg when the rate leg's are blank, A5); **F6u rate plausible:
an OIS fixed rate above 0.25, a percent-unit row, is dropped and counted (A5); the assertion is on the cell median, not on every row**;
F7 tenor bucket: `Expiration Date` within ±7 calendar days of `Effective Date` plus N years (29 Feb + N years → 28 Feb); F8
`Platform identifier` ≠ `BILT`; **F9 execution time in the CMT window, 14:30 <= t < 16:30 America/New_York, with DST taken from the
trade's date via `zoneinfo` (A1)**. Numbers: strip `,`; a trailing `+` marks a capped notional (notionals are not used in v1).

### 6.1 USD SOFR OIS (`sofr_ois`; tenors 2, 5, 10, 30)
F0: `UPI FISN == "NA/Swap OIS USD"` and `UPI Underlier Name` in {`USD-SOFR-OIS Compound`, `USD-SOFR-COMPOUND`} (two spellings of one
index). Excluded and counted (top 10 unmatched labels per date in diagnostics): `USD-SOFR` (12 resolved trades on 13 Oct), Fed Funds labels,
`NA/Swap Flt Flt OIS USD`, swaption labels.
F3: `Other payment amount` blank (on 13 Oct every non-blank one is type `UFRO`, 1,888 of 4,508 resolved OIS rows, pre-A).
F5: exactly one of `Fixed rate-Leg 1/2` filled; that leg is L. F6: day count of the fixed leg `== A004` (ACT/360) and
(payment-frequency period, multiplier) in {(`YEAR`,`1`), (`MNTH`,`12`)}, each read from leg L and, if leg L's cell is blank, from the other leg;
rows with blank conventions on both legs are dropped. Rate = `Fixed rate-Leg L`, a decimal fraction (13 Oct spot range 0.0222-0.0706; lens).

**Variants (A1, the only three in the first landing):**
`headline` = F0-F9 (the 14:30-16:30 New York window, BILT excluded); minimum n for a headline cell is 10; `fullday` = F0-F8 (the whole UTC
day, BILT excluded); `all_platforms` = F0-F7 (the whole UTC day, BILT included). The old `trim`, `ex_pkg`, `pkg_only` and `cmt_window`
variants are dropped: `cmt_window` is now the headline.
*Why BILT:* on 13 Oct the BILT rows at 10y (65 of 391 all-platform rows, pre-A) have a median 61.7bp below the rest; at 2/5/30y BILT sits
within 1bp of the rest (n 10/12/8). This is one cluster on one day (C-074 risk), so `all_platforms` and `fullday` are always published
beside the headline, and the diagnostics report the BILT deviation per tenor every day. That BILT denotes off-facility execution is
believed, not read (O-2).
*Timing check:* diagnostics report, per date and tenor, the hourly medians of the `fullday` set by New York hour, where the hour has n >= 10.

### 6.2 USD CPI zero-coupon (`cpi_zc`; tenors 5, 10, 30)
F0: `UPI FISN == "NA/Swap Infl Idx USD"` and `UPI Underlier Name == "USA-CPI-U"` (`NA/Swap Infl Idx Flt USD` excluded). F3: `Other payment
amount` blank: essential here, because 452 of 514 backdated CPI swaps carry an upfront and are off-market packages (lens). F5 as 6.1.
F6: zero-coupon shape: fixed payment frequency (`EXPI`, `1`) or (`YEAR`, m) with m a whole number, read from either leg as in 6.1; F7 also
requires m == the bucket's tenor N when the period is `YEAR`. Day count is not used (`A020`, undecoded; O-3).
Variants: `headline` = F0-F8 over the whole UTC day with BILT excluded (A1's window applies to `sofr_ois`; a two-hour CPI cell would almost never
reach n = 5); `all_platforms` = F0-F7; `cmt_window` = F0-F9, in the cells file only.

### 6.3 Cross-currency (`xccy_eurusd`, `xccy_jpyusd`, `xccy_gbpusd`; tenors 1, 2, 3, 4, 5, and the pooled cell `pool1to5`)
F0: `UPI FISN` in {`NA/Swap Flt Flt EUR USD`, `NA/Swap Flt Flt JPY USD`, `NA/Swap Flt Flt GBP USD`}; `UPI Underlier Name`, upper-cased,
contains `SOFR` and the pair's RFR (`EUROSTR`, `TONA`, `SONIA`) and not `IBOR` (EURIBOR rows carry 2-3.5% spreads on both legs; lens).
Unmatched labels are counted and their top 10 logged (product labels, not trade rows). F3: no `UFRO` token in `Other payment type`
(split on `;`); `PEXH` is kept. F5: one leg's `Notional currency` is `USD` (U) and the other is the pair currency (X); both fixed rates blank.
F6: U's spread blank or 0, X's spread filled; units from `Spread notation-Leg X`: `3` → ×10,000 (decimal fraction), `4` → as printed (bp),
anything else dropped; per-currency caps |spread| <= 50bp for EUR and GBP and <= 100bp for JPY (A5). Rows with a spread on U only are counted
as `usd_leg_only` and not used (13 Oct: 0 rows). No platform filter and no time window apply to the cross-currency headline (the 13 Oct
funnel of the earlier run ends at F7).
**Value and sign:** the spread added to the non-USD RFR leg against flat SOFR, in bp. Negative is the conventional sign of a dollar premium
(BIS QR Dec 2025, lens); some literature uses the opposite sign (Fed IFDP 1427; lens). The ledger states the formula, not a reading.
**Publication (A4):** a per-tenor cell is published only when n >= 10; the pooled `pool1to5` cell (all five tenor buckets of the pair, one
UTC day) is always published under the general floor (n < 5: the count only; 5-9: count and median; >= 10: also quartiles). Daily xccy cells are
thin (13 Oct n <= 8 per cell, JPY/USD has no spot trade at 1-4y), so `pool1to5` is the series to read.

### 6.4 Lone-package swap spread: deferred (A6)
Not built in the first landing, with S6, the `pkg_*` columns and O-5. The idea, for the record: rows in the `sofr_ois` headline cell with
`Package indicator == TRUE` and `Package transaction spread` filled, whose (`Execution Timestamp`, `Platform identifier`,
`Package transaction spread`, `Package transaction price`) group has size 1, with units set by magnitude and not by the CMT. The
identification (the printed spread is swap minus a specific Treasury, not the CMT) is a HYPOTHESIS: the Treasury leg is not in the file.

## 7. Conventions

**Swap spread, quoted (headline, A2).** `spread_quoted_bp` = the cell's median swap rate (decimal × 10,000) minus the CMT par yield
(percent × 100). There is no conversion: this is how dealers quote it. Sign: swap minus Treasury, so negative means the swap rate is
below the Treasury yield (BIS, Tradition, American Academy of Actuaries, all lens). CMT is bid-side, indicative, and fixed-maturity
(Treasury methodology page; lens), so the ledger's spread differs by design from a desk spread against a benchmark bond.
**Swap spread, converted (`spread_bey_bp`).** Treasury CMT par yields are semiannual bond-equivalent; the OIS fixed rate is annual ACT/360.
Each trade's rate r (decimal) goes to a semiannual bond-equivalent rate with its own accrual factor
`a = (Expiration Date − Effective Date in days) / (360 × N)`, N the bucket's tenor in years: `bey = 2 * (sqrt(1 + r * a) - 1)`. The median is taken
after the conversion; `spread_bey_bp` = median(bey) × 10,000 − CMT × 100. (The earlier uniform factor 365/360 is the special case `a = 365/360`
and is used by the pure checks of §13.) The conventions lens bootstrapped the 14 Oct par curve and found the 365/360 conversion within
+0.05 to +0.19bp of a full par-swap repricing at 2-30y (≤0.10bp on four synthetic curves); leap-year accrual, calendars and T+2 vs T+1
settlement are not modelled. `bey_adj_bp` = `spread_bey_bp` − `spread_quoted_bp` (IDENTITY; |bey_adj_bp| <= 3 is asserted). Notes and the
page quote `spread_quoted_bp` and say so.

**Inflation gap, one basis (A3).** Measure key `cpi_zc_minus_ust_par_be`. `par_breakeven_simple = n − r` (IDENTITY; n the nominal CMT par
yield and r the TIPS real CMT par yield at the same tenor; no 2y, as the real curve starts at 5y). Headline `gap_fisher_bp` = (median ZC swap rate,
annual, as printed − ((1 + n/2)/(1 + r/2))² + 1) × 10,000, the Fisher-consistent annualised par breakeven; sensitivity `gap_simple_bp` =
(median ZC rate − (n − r)) × 10,000. Every output that carries this gap calls it "the gap between two different instruments: the CPI
zero-coupon swap rate minus the Treasury par breakeven", never "the breakeven". The conventions lens computed zero-coupon minus par
breakevens of −0.3/+0.2/−6.4bp at 5/10/30y on 14 Oct, so part of any 30y gap is the par-versus-zero curve-shape term, listed as a caveat in the README.

**Treasury date.** The CMT for NY date D is paired with UTC ledger date D. The headline window (14:30-16:30 New York) brackets the CMT's ~15:30
snapshot and lies inside UTC day D in both EDT and EST. No CMT row (weekend, Columbus Day 12 Oct 2026): spreads blank, status `no_ust`.

## 8. Statistics

Per (date, series, tenor, variant): `n`; `median`; `q1`, `q3` by linear interpolation (type 7: h = (n−1)p, x⌊h⌋ + (h−⌊h⌋)(x⌊h⌋+1 − x⌊h⌋));
`iqr_bp`; `iqr_over_sqrt_n_bp`; `share_pkg` (share of rows with `Package indicator == TRUE`); `share_gt10bp` (share of rows more than 10bp from
the cell median).
**Publication floor (A4), the same for every cell and every diagnostics value:** n < 5: publish n only (status `below_min_n`); 5 <= n < 10: publish
n and the median (status `thin`); n >= 10: also q1, q3, iqr, iqr/sqrt(n) and the shares (status `ok`). Exceptions, both stricter: the
`sofr_ois` headline spread needs n >= 10 (A1); a per-tenor cross-currency cell needs n >= 10 and has no `thin` level (A4). No notional-weighted
median, no min or max, ever. Rates in percent, 6 decimals; spreads and dispersions in bp, 3 decimals; formatting with
`format(x, ".6f")`/`".3f"`, so that reruns are byte-identical.

## 9. Outputs (all under `data/swap_tape/`, sorted by date and then in generation order, `lineterminator="\n"`; every CSV starts with a
`# source:` line, A10; readers must skip lines that start with `#`)

| File | Columns |
|---|---|
| `ledger_YYYY.csv` | `date_utc, measure, pair, tenor_y, n, spread_quoted_bp, spread_bey_bp, bey_adj_bp, gap_fisher_bp, gap_simple_bp, xccy_median_bp, iqr_over_sqrt_n_bp, swap_median_pct, ust_par_pct, ust_real_pct, par_be_fisher_pct, fullday_quoted_bp, n_fullday, allplat_quoted_bp, n_allplat, grade, status` |
| `cells_YYYY.csv` | `date_utc, series, tenor_y, variant, unit, n, median, q1, q3, iqr_bp, iqr_over_sqrt_n_bp, share_pkg, share_gt10bp, status` |
| `funnel_YYYY.csv` | `date_utc, series, step, tenor_y, n_after` (steps F0, F1, F2, F3, F4, F4s, F5, F6, F6u, F7, F8, F9 as in §6; tenor blank before F7) |
| `diagnostics_YYYY.csv` | `date_utc, key, value, n` (below) |
| `file_stats.csv` | `file_date, zip_name, zip_kb, zip_sha256, zip_md5, csv_kb, csv_sha256, rows, header_ok, n_NEWT, n_CORR, n_MODI, n_TERM, n_EROR, n_REVI, n_other_action, newt_TRAD, newt_COMP, newt_NOVA, newt_EXER, newt_other_event, newt_exec_on_file_date, newt_exec_earlier, newt_exec_placeholder, newt_exec_other, self_refs, orphan_children, retrieved_utc, retrieved_src` |
| `ust_used.csv` | `date_utc, par_2y, par_5y, par_10y, par_30y, real_5y, real_10y, real_30y, par_csv_sha256, real_csv_sha256, par_fetched, real_fetched` (public-domain values; committed, A7) |
| `summary.csv` | `key, value, n` (the cross-date statistics of A1 and A14, recomputed from the ledger files at every build) |
| `fetch_log.csv` | `seq, requested_at_utc, host, path, http_status, outcome, kb, sha256, elapsed_ms` (append-only; written by `fetch` and `fetch-ust` only, so `build` stays byte-identical) |
| `holes.csv` | `date_utc, http_status, reason, recorded_utc` (written by `fetch`; A8) |
| `SOURCES.md` | R3 and A10 text, written by `build` |
| `README.md` | column dictionary and caveats (hand-written; A10, PR19) |

`measure` ∈ {`swap_spread` (`spread_quoted_bp` headline; `spread_bey_bp`; `bey_adj_bp`; `fullday_quoted_bp` and `allplat_quoted_bp` with their n),
`cpi_zc_minus_ust_par_be` (`gap_fisher_bp`, `gap_simple_bp`, `par_be_fisher_pct`), `xccy_basis` (`xccy_median_bp`; `pair` ∈ EURUSD, JPYUSD, GBPUSD;
`tenor_y` ∈ 1-5 or `pool1to5`), `date_status` (one row for a date with no usable file; `status` says why)}.
Diagnostics keys (each a calibration that the C-074 rule says must be recomputed on every date, not assumed): `bilt_n_{T}`,
`bilt_median_dev_bp_{T}`, `gt10bp_nonbilt_{T}`, `hourly_median_pct_{T}y_ny{HH}`, `corr_applied`, `corr_changed_terms`, `eror_dropped`, `revived`,
`modi_rate_changed`, `placeholder_rows`, `header_added`, `header_removed`, `xccy_notation_{3,4,other}`, `xccy_usd_leg_only`,
`unmatched_top10_{series}`, and `warn_*` keys for the §13 warnings. A value that is a statistic of fewer than 5 rows is blank.
The cross-date `summary.csv` holds, over all dates present in the ledger files: the share of dates whose headline 10y cell has n >= 10; the share
of dates with a 30y `spread_quoted_bp` below zero; the share of day-on-day |Δ| of the 10y quoted spread under 10bp, with the outliers listed;
the standard deviation of the day-on-day changes of the quoted spread at each tenor (all dates, and for the 10y also the subset of days when the 10y CMT
moved <= 2bp); and the OLS slope of the day-on-day change in the headline quoted spread on the day-on-day change in the CMT, per tenor, each with its n (A1).

## 10. Resolution, stated before any back-fill is pulled

On 13 Oct (author's run, pre-A: full-day headline with the converted spread), `iqr_over_sqrt_n` = 0.247/0.217/0.160/0.138bp at 2/5/10/30y
(n 135/235/326/159); under normality the median's standard error is about 0.93 × IQR/√n. That is not the ledger's precision. Three larger terms
sit on top:
(a) **CMT rounding**: yields print to 0.01pp, so each spread carries up to ±0.5bp and each day-on-day change up to ±1bp from rounding alone;
(b) **time of day**: 10y hourly medians (NY hours with n >= 5, ex-BILT, pre-A) ranged 4.787-4.833% (4.6bp), and the window median minus the
full-day median was +0.98/+0.91/+0.39/+0.43bp at 2/5/10/30y (window n 12/29/31/22). A1 makes the window the headline for that reason; the two
hours still differ from the 15:30 snapshot by whatever moves inside the window;
(c) **filter choice**: the six pre-A `sofr_ois` variant medians at 10y ranged 4.8039-4.8213% (1.7bp); `ex_pkg` minus `pkg_only` was +0.9 to
+1.5bp at 2/5/10y.
**So the smallest daily change in a liquid-tenor swap spread this ledger can claim to resolve is about 2bp (HYPOTHESIS, the author's
judgement).** The back-fill must measure it, and A1 says on all dates, not only quiet ones: `summary.csv` reports the standard deviation of
day-on-day changes in the 10y `spread_quoted_bp` on all dates, and beside it the same on days when the 10y CMT moved <= 2bp, before any
series is read for change. Cross-currency prints sit on a 1/8bp grid, so IQR is often 0 at small n and `iqr_over_sqrt_n` understates; daily
xccy cells are indicative, and `pool1to5` is the series to read.

## 11. Run plan

**Phase 0, offline (no request).** `selftest`; then `build --start 2026-10-13 --end 2026-10-13` from the cached zip. Check S0-S2, S5 (the
Treasury inputs for S3 and S4 come in phase 1).
**Phase 1, the three dates.** `fetch-ust --years 2025,2026`; `fetch --dates 2025-04-09,2026-01-15,2026-09-29`; `build` those dates and
2026-10-13. Check S3, S4, S7, S10-S13. (2026-01-15 is the EST date, A14.)
**Phase 2, the start of the archive (A8).** The back-fill covers every available weekday from 14 Oct 2024; the older year is undocumented by DTCC
and its 404s are holes (`holes.csv`), not refusals. Fetch it now, while it is served: whether the window rolls (O-1) is settled by the back-fill itself,
because a rolling window loses one file at the start per day of delay (about 0.71 weekday ledger dates per day). The re-probe is deferred (A6).
**Phase 3, back-fill, oldest first**, in slices of <= 60 requests at >= 5s (hard cap 100): 730 files (522 weekdays) is >= 9 invocations of 60
and >= 44 minutes of pacing; ~0.5-0.75GB compressed (lens). `fetch-ust --years 2024` first. Oldest-first makes the at-risk files the first fetched.
**Phase 4, weekly (A12).** On Fridays: `fetch-ust --years <current>`; `fetch --start <Monday> --end <Thursday of the week>` (and the previous
Friday); `build` the same range. The CALENDAR WEEKLY row carries it. Per-day fetching is not needed because `build` is an upsert.

## 12. Falsifiable success criteria (each a command and the number that proves it)

All numbers below are the author's independent stdlib run on the cached file unless marked; "exact" means the builder must match it or
explain the gap through a funnel row before anything is accepted. Numbers marked (pre-A) are the old full-day, converted basis and are
not targets under A1-A5; the builder states the new ones in §18.
- **S0** `python3 bin/swap_tape_ledger.py selftest` prints PASS for every check and `DETECTED` for each of the three mutants (`noconv`, `noeror`, `nowindow`).
- **S1** (`build … 2026-10-13`) `file_stats.csv`: zip_sha256 `efdf50870f1083cae307c3ba55f31f09e6b6c7186516b12086d8bbc3a285da3f`,
  zip_md5 `d966303f26482459c4f5cc26ebdd7d88` (equal to the S3 ETag the archive lens recorded, so the cache is DTCC's object), rows 25,885;
  NEWT 22,662, CORR 1,171, MODI 1,135, TERM 671, EROR 241, REVI 5; NEWT/TRAD 17,858, COMP 4,642, NOVA 91, EXER 71. Exact.
- **S2** `sofr_ois` funnel: F0 4,365, F1 4,326, F2 1,927, F3 1,758, F4 1,732 (exact); `all_platforms` (pre-A, which kept the day-count rule only on the rate
  leg and had no strike or percent-unit steps) n 145/247/391/167; the fullday ex-BILT set (pre-A `headline`) n 135/235/326/159 and
  medians 4.6507/4.7133/4.8174/4.9040% (±0.1bp) at 2/5/10/30y. Under A5 (conventions from either leg, strike rows dropped) the counts differ,
  and the builder's run explains every gap through a funnel row (§18.2). The schema lens's hand figure for 10y was 4.8174% (trimmed, n 344,
  without the day-count filter) and 4.8175% (ex-BILT, n 332): the `fullday` 10y median must lie within 0.2bp of both.
- **S3** `swap_spread` against CMT 4.79/5.00/5.21/5.56 (13 Oct): the builder states the new `spread_quoted_bp` and `spread_bey_bp` (A14) in §18.
  Pre-A values were value −12.90/−27.71/−38.39/−64.82bp, alt −13.93/−28.67/−39.26/−65.60, bey_adj +1.03/+0.97/+0.87/+0.78.
  **The 30y quoted spread is negative.** `iqr_over_sqrt_n_bp` < 0.5 at all four tenors where n >= 10.
- **S4** `cpi_zc` headline (full UTC day, ex-BILT) n 29/28/6 and medians 2.49125/2.45375/2.37425% (pre-A); `gap_fisher_bp` and `gap_simple_bp` against par
  breakevens 2.33/2.33/2.28: the builder states them in §18 (pre-A simple-basis gaps +16.13/+12.38/+9.43bp). The 30y cell has n < 10, so it is `thin`.
- **S5** `xccy` (pre-A per-tenor, headline = F7): EUR/USD 1y n 6 −3.250, 2y n 8 −3.750, 3y n 3, 4y n 2, 5y n 7 −4.500; GBP/USD 1y n 7 +2.500,
  2y n 4, 3y n 2, 4y n 6, 5y n 5; JPY/USD 1-4y n 0, 5y n 1. Funnels F0/F1/F2/F4/F7: EUR/USD 63/63/46/39/26, JPY/USD 39/23/16/14/1, GBP/USD 47/46/35/34/24.
  Under A4 no per-tenor cell reaches n >= 10, so none is published; the `pool1to5` n (the sum of the five n above, less any cap drops) is the check.
  This replaces "EUR/USD 1y negative" (§1.5).
- **S6** deferred with the package series (A6).
- **S7** Determinism: build the four test dates into two empty output directories (twice, from the same inputs); `diff -r` prints nothing, and
  the sha256 of every output file is identical across runs.
- **S8** Leak guards (A9): `grep -rEn '(^|,)[0-9]{8,19}(,|$)' data/swap_tape/` prints nothing; no header in any output contains `min` or `max`;
  `git ls-files data/swap_tape | grep -iE 'CFTC_CUMULATIVE|\.zip$'` prints nothing; the script refuses `--cache` pointing inside the repo; the
  warn-only M9 guard of `bin/check.sh` fires on a file planted in a scratch copy of the clone (never in the clone).
- **S9** `bin/check.sh --all`: the six ✓ guard lines (goal, M5, M6, M7, M8, M9), `✓ no killed claims found`, `✓ page clean` (read the lines, not the exit code).
- **S10** Four dates: `file_stats` rows for 2026-09-29 = 27,133 (the DTCC listing's rowCount, an independent count; lens); `header_ok` on
  2025-04-09, 2026-01-15 and 2026-09-29; the four `sofr_ois` headline cells with n >= 10 and `iqr_over_sqrt_n_bp` < 0.5 on 2026-09-29 (the builder states
  any cell below the floor); 30y `spread_quoted_bp` < 0 on all dates; `ust_used` equal to 3.91/4.06/4.34/4.72 (2025-04-09) and 4.89/5.06/5.26/5.59
  (2026-09-29), as relayed in the g4 return (a mismatch is reported, never overridden).
- **S11** `fetch_log` shows consecutive request starts >= 5s apart (Treasury and DTCC alike).
- **S12 (A14)** `nowindow` moves the 13 Oct 10y `spread_quoted_bp` by more than 1bp. If it does not, the window does nothing on that date and the
  builder says so.
- **S13 (A14)** 2026-01-15 (EST) builds with the window correctly offset (UTC 19:30-21:30 in winter, 18:30-20:30 in summer).
- **Back-fill acceptance (A14)**, from `summary.csv`: at least 95% of CMT dates have a headline 10y cell with n >= 10; the 30y quoted spread is
  negative on at least 95% of dates; the day-on-day |Δ| of the 10y quoted spread is under 10bp on at least 99% of dates, with the outliers listed.
- **Pre-registered expectations, not pass/fail (HYPOTHESIS):** on 2025-04-09, the 10y fullday IQR exceeds 13 Oct's (2.89bp, pre-A) and
  |headline − fullday| at 10y exceeds 13 Oct's. Either failing is information about the tape, not a bug.

## 13. Assertions and the selftest

**Runtime asserts in `build`** (a failure stops the date and records `error`, never silently passes): the required columns are present; ids unique
per file; the zip member name matches the date; every published `sofr_ois` and `cpi_zc` cell median lies in (0, 0.25); |`bey_adj_bp`| <= 3 for every
cell (the formula gives −2.5 to +1.8bp over 2-7%); the Fisher and simple par breakevens differ by less than 0.1 percentage point; no statistic
on n < 5; output writers refuse any field that is a whole string of 8 to 19 digits. **Warnings** (printed and written to diagnostics, not fatal):
30y `spread_quoted_bp` >= 0; spreads outside 2y [−35, +5], 5y [−50, −5], 10y [−70, −15], 30y [−110, −40] (bands from the conventions lens's level
table, its judgement); 10y headline IQR > 5bp; `gap_fisher_bp` outside [−10, +60]; JPY/USD `pool1to5` >= 0; EUR or GBP |basis| > 30; a series'
F0 n below half its trailing 20-date median (at least five prior dates in the funnel files, A5).

**`selftest`** builds a synthetic tape in memory (HEADER_V1 columns, ids `T0001`…, dates in 2030, no DTCC content) of about 150 rows: NEWT/TRAD
OIS rows on Leg 1 and Leg 2; a convention-on-the-other-leg row; a COMP row; an EROR on a NEWT; a CORR chain of depth 2; an EROR on a CORR; a MODI
changing the rate; a backdated row; a forward-start row; an upfront row; a strike row; a percent-unit row; a BILT off-market row; post-priced and
non-standard rows; a placeholder 2000-01-01 row; an A001 row; out-of-window rows; CPI rows; xccy rows with USD on each leg, notation 3 and 4, a PEXH and
a UFRO row, a EURIBOR label and a cap breach. It asserts the exact funnel and medians, and these pure checks: `bey(0.048)` at the 365/360 factor
minus 0.048 = +0.885bp (±0.001), `bey(0.05556)` within 0.01bp of 0.05556, `bey(0.10) − 0.10 = −10.585bp`; type-7 quartiles of [1, 2, 3, 4] are 1.75/2.5/3.25;
the anniversary bucket (+7 days in, +8 out; 2028-02-29 + 2y → 2030-02-28); the 14:30-16:30 window in EDT and in EST; the publication floor; the
Treasury parser on a 2024-style and a 2025-style header; the 404 zones (a recent 404 latches, an old one is a hole) and every STOP class through an
injected fake opener and a fake clock (no network), the 5-second spacing across two invocations, the lock and its stale detection; the UA and host
allow-list (`www.sec.gov` raises); refusal of a cache inside the repo; two builds of the fixture byte-identical.
**Mutants** (A6; each must make at least one fixture assertion fail; `selftest` FAILS if any mutant passes): `noconv` (the conversion replaced by
identity: the fixture's 10y converted spread moves by about −0.9bp), `noeror` (EROR resolution removed: the errored rows re-enter the cells),
`nowindow` (the time window removed: the headline becomes the full-day median).

## 14. Grades

`swap_spread`, `cpi_zc_minus_ust_par_be`, `xccy_basis`: MEASURED, on the stated universe (headline-filtered SDR prints executed on D, against the CMT
of D); denominators are the `n` columns. `bey_adj_bp`, `par_be_fisher_pct`: IDENTITY. The resolution claim in §10: HYPOTHESIS until the back-fill measures it.

## 15. Open questions (marked; not guessed)

- **O-1** Rolling or fixed archive start; the back-fill settles it (§11). The `--reprobe` that would test it directly is deferred (A6).
- **O-2** What `BILT` and `XOFF` denote; believed to be off-facility and off-exchange codes, not read from the CFTC technical specification.
- **O-3** Day-count codes: A004 = ACT/360 rests on a third-party code table and market convention (the ISO page returned 403, lens); A020, A006,
  A008 are undecoded. Only A004 is load-bearing.
- **O-4** `Spread notation` 3 = decimal and 4 = bp are inferred from magnitudes; the PPD guide v2.8 defines no codes (lens).
- **O-5** Deferred with the package series (A6).
- **O-6** How many trades executed on D arrive after D, and the CFTC block-delay rules that govern it (not read). The first landing does not
  measure it (the late-file window is deferred).
- **O-7** Whether a published file is ever regenerated (one file compared, eight minutes apart; lens). Deferred with `--reprobe`.
- **O-8** Whether the 2024-25 files carry the same names, not just the same count. The header check answers it per date (`header_added`, `header_removed`, `schema_mismatch`).
- **O-9** CMT is bid-side; swap prints are executions. The bid/mid gap is not modelled.
- **O-10** Mark-to-market resetting versus non-resetting cross-currency swaps are not distinguishable on the tape.
- **O-11** DTCC's general legal page was not fetched (lens); E-024 rules regardless.
- **O-12** Closed by A8 and A13: HEAD is never sent, and one neutral User-Agent (CLAUDE.md's) is used for both hosts.
- **O-13** Whether JPY/USD has enough spot OIS-vs-SOFR trades on any day for `pool1to5` to reach n >= 5.

## 16. Landing (supervisor's rungs)

Commit `bin/swap_tape_ledger.py`, `data/swap_tape/*` and the two `.gitignore` lines, as the GitHub noreply identity, after the §12 criteria.
Any findings note that quotes the ledger cites `data/swap_tape/` and the script, never a scratchpad path, and names the DTCC source beside the
number (A10); it gets a read-table row, a RESEARCH_STATE §5 update, a CALENDAR row for the 2025-04-09 expectations, and a handover row. The
CALENDAR WEEKLY row (A12) and the M9 guard (A9) are part of the build.

## 17. Supervisor amendments, 14 Oct (after two adversarial reviews; these OVERRIDE anything above)

The builder applies these to the sections above first, so that the spec and the code agree, then implements. "CR" refers to the
correctness review and "PR" to the practicality review.

**A1. Time alignment is the headline (CR1).**
- The headline `sofr_ois` cell is built from prints executed **14:30–16:30 New York time**, with DST from the trade's date (use
  `zoneinfo("America/New_York")`). That window brackets the Treasury CMT's 15:30 snapshot.
- Minimum n for a headline cell is 10. The full-UTC-day median and the all-platform median are published as variants `fullday`
  and `all_platforms`. No other `sofr_ois` variants in the first landing.
- `diagnostics` reports, per date and tenor, the hourly medians (n≥10) as a timing check.
- Over the back-fill it reports the OLS slope of the day-on-day change in the headline spread on the day-on-day change in the
  CMT, with its n.
- Resolution (§10) is measured on all dates, not only quiet ones.

**A2. Quoted convention is the headline (CR2).**
- `spread_quoted_bp` = median swap rate (decimal × 10,000) minus CMT (percent × 100). There is no conversion; this is how
  dealers quote it.
- `spread_bey_bp` is the converted version. Each trade's annual ACT/360 rate goes to a semiannual bond-equivalent rate using an
  accrual factor of (Expiration − Effective in days) / (360 × N years), not 365/360 (CR3). The median is taken after conversion.
- Both columns are always published. Notes and the page quote `spread_quoted_bp` and say so.
- S6 (the package cross-check) is deferred with the package series (A6).

**A3. Inflation is one basis (CR7, PR16).**
- The measure key is `cpi_zc_minus_ust_par_be`.
- Headline: `gap_fisher_bp` = median ZC swap rate (annual) minus the Fisher-consistent annualised par breakeven,
  ((1 + n/2) / (1 + r/2))² − 1, where n is the nominal CMT and r the real CMT at the same tenor.
- Sensitivity: `gap_simple_bp` = median ZC rate minus (n − r).
- Every note and the page call this "the gap between two different instruments", never "the breakeven".
- The remaining par-versus-zero curve-shape term is listed as a caveat in the README.

**A4. Publication floor (PR1, CR14), replacing R2 and §8.**
- n < 5: publish n only.
- 5 ≤ n < 10: publish n and the median.
- n ≥ 10: also q1, q3, iqr and iqr/sqrt(n).
- No notional-weighted median, and no min or max, ever.
- The same floor applies to every diagnostics cell.
- Cross-currency: publish the per-tenor cell only when n ≥ 10. Always publish a pooled 1–5y cell (`pool1to5`) under the same
  floor.

**A5. Filters, local fixes.**
- Read the convention columns from either leg when the rate leg's are blank (CR5).
- Drop rows with Strike Price filled (option-exercise swaps). Keep BILT excluded from the headline; `all_platforms` shows it (CR6).
- Rows whose rate is in percent units (an OIS fixed rate > 0.25) are dropped and counted. The assertion is on the cell median,
  not on every row (CR9).
- Per-currency cross-currency caps: |spread| ≤ 50bp for EUR and GBP, ≤ 100bp for JPY (CR15).
- CORR tie-break: latest Event timestamp, then the larger id. Document it (CR12). Fix the §5 count wording (CR13).
- Log the top 10 unmatched FISN and underlier names per series per date. Warn when a series' F0 n is below half its trailing
  20-date median (PR9).

**A6. Scope cut for the first landing (PR13).**
- Defer: the lone-package series (§6.4, S6, `pkg_*`, O-5), the K=2 late-file and `provisional` machinery, `--reprobe`,
  `n_capped`, `n_dupkey` and the notional-weighted median.
- Keep three mutants in the selftest: `noconv` (BEY conversion removed), `noeror` (EROR resolution removed) and `nowindow`
  (time window removed). Each must make a check fail.

**A7. Treasury inputs (CR8, PR17, PR18).**
- Parse the Treasury par and real CSVs **by header name, case-insensitively**. Assert on a 2024 row and a 2025 row.
- Ledger dates are the dates with a CMT row. Weekend files are not fetched.
- `ust_used.csv` (the CMT values joined, per date and tenor) is committed. It is public domain and makes the join reproducible.

**A8. Fetch rules (PR2, PR3, PR4, PR15).**
- Weekdays only. Never send HEAD.
- 5 s minimum spacing, persisted across invocations in a last-request file.
- `--max-requests` default 60, hard cap 100. The lock is removed in `finally`, with stale-lock detection by pid and age.
- The STOP latch lives at the fixed path `~/dtcc_ppd/STOP`, whatever `--cache` says.
- STOP is set on any HTTP status other than 200, and on any body that is not a zip. One exception: a 404 for a date more than 366
  days old is recorded in `data/swap_tape/holes.csv` with its reason and does not latch.
- A socket fault (timeout, reset, TLS) ends the invocation without latching.
- The back-fill covers every available weekday from 14 Oct 2024. The older year is undocumented by DTCC, so its 404s are holes,
  not refusals. Fetch it now, while it is served.

**A9. Leak guards (PR5, CR10).**
- S8 becomes `grep -rEn '(^|,)[0-9]{8,19}(,|$)' data/swap_tape/`, which must print nothing. The digits are anchored to a whole
  field, and the range covers the legacy 8–18-digit ids too.
- The zip check is `git ls-files data/swap_tape | grep -iE 'CFTC_CUMULATIVE|\.zip$'`, which must print nothing.
- Add a warn-only M9 check to `bin/check.sh` running both, in that file's existing style. Show that it fires on a planted file in
  a scratch copy, then remove the plant.

**A10. Citation (PR6).**
- Every CSV under `data/swap_tape/` starts with a `# source:` comment line naming "DTCC Public Price Dissemination, CFTC
  cumulative rates reports (pddata.dtcc.com)" and the retrieval dates. Readers must skip `#` lines.
- `data/swap_tape/SOURCES.md` says that CC BY 4.0 covers only the project's computation, and that the use is non-commercial
  under THE_ASK E-024.
- `data/swap_tape/README.md` carries the column dictionary (PR19).
- Any note or page that states a ledger number names the DTCC source.

**A11. Header check (PR8).**
- Require only the columns the build uses, matched by name and not by order.
- Keep a rename map for versions. Log added and removed names.
- A date whose file fails the check gets a `status` row in the ledger (`schema_mismatch`), not silence.

**A12. Cadence (PR7).**
- The landing adds a WEEKLY (Friday) `CALENDAR.tsv` row: fetch the week's weekday files, then `build` with upsert semantics.
- `build` rewrites the rows for the dates it is given, and leaves the others alone.

**A13. User-Agent (PR14).**
- Use the CLAUDE.md canonical non-SEC string, `Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)`.
- Assert it contains no `@`.
- Allowed hosts: `pddata.dtcc.com` and `home.treasury.gov`.
- No absolute home paths in any output: print `~`.

**A14. Success criteria, strengthened (CR11, PR19).**
- Keep S0–S5 and S7–S11, recomputed under A1–A5. The builder states the new 13 Oct numbers, and the supervisor re-derives two
  of them independently.
- Add: `nowindow` must move the 10y quoted spread on 13 Oct by more than 1bp. If it does not, the window does nothing on that
  date and the builder says so.
- Add: one winter (EST) date, 2026-01-15, builds with the window correctly offset.
- Back-fill acceptance:
  - at least 95% of CMT dates have a headline 10y cell with n ≥ 10;
  - the 30y quoted spread is negative on at least 95% of dates;
  - the day-on-day |Δ| of the 10y quoted spread is under 10bp on at least 99% of dates, with the outliers listed.

**A15. Archive facts (PR11).**
- The archive lens's derived facts go into §1 of this spec, which lands in `_research/`. They are: 366 listing entries; 9 files
  more than 60 minutes late; 27,133 rows for 2026-09-29; the ETag equals the zip md5; and the 2024-10-11 404.

## 18. Builder's decisions and findings, 14 Oct (where §17 was silent, and what the build found)

Built by `bin/swap_tape_ledger.py` (stdlib only). Everything below was observed in the builder's own runs on 14 Oct 2026 against the cached
13 Oct zip and the three files the script then fetched (2025-04-09, 2026-01-15, 2026-09-29); the supervisor re-derives two of the 13 Oct numbers
independently (A14).

### 18.1 Decisions where §17 was silent
1. **Two floors, one reading.** A1 puts the minimum n of a `sofr_ois` headline cell at 10 and A4 publishes a median at 5 <= n < 10. Both hold:
   `cells` publishes the median of a `thin` cell; the `ledger` publishes a headline spread only at n >= 10 (status `below_min_n` otherwise, and
   `swap_median_pct` blank). The `fullday` and `all_platforms` spreads in the ledger follow the general floor (a median at n >= 5).
2. **Variants.** `fullday` = F0-F8 (whole UTC day, BILT out); `all_platforms` = F0-F7 (whole UTC day, BILT in); `headline` = F0-F9. For `cpi_zc` the headline is
   the whole UTC day with BILT out (a two-hour cell almost never reaches 5), and `cmt_window` is kept in `cells` only. A1's window is stated for `sofr_ois`.
3. **Cross-currency headline** has no platform filter and no time window (the author's 13 Oct counts, which §12 S5 reproduces, end at F7); BILT is not
   excluded there.
4. **File sizes are written in kB with one decimal.** A9's grep (`(^|,)[0-9]{8,19}(,|$)`) would flag a bare byte count of 8 digits: the 13 Oct CSV member
   is 15,103,273 bytes. The same rule is enforced by every writer in the script, so a size, a count or a hash can never look like an identifier.
5. **Day-on-day** (A1, A14) means two adjacent Treasury dates that are both in the ledger; a gap in the ledger makes no pair. A weekday with a DTCC file
   but no Treasury row (a holiday) is kept with status `no_ust` rather than dropped, so that the file's presence stays visible (A7 says ledger dates are
   dates with a CMT row; `summary.csv` counts both, as `ledger_dates` and `cmt_dates_in_ledger`).
6. **Extra files and columns:** `summary.csv` (the cross-date numbers of A1 and A14), `holes.csv` (A8), `ust_used.csv` carries the fetch dates of the two
   Treasury files, `file_stats.csv` carries `csv_sha256`, `newt_exec_other` and `retrieved_utc`/`retrieved_src` (the retrieval date comes from
   `fetch_log.csv`, else from the zip's modification time, for the zip that was cached before the script existed), `diagnostics` carries `n`.
7. **Fetch.** A date is requested only if it is a weekday, is not cached, is not a recorded hole, is not before 2024-10-11 (the first date probed) and is
   not later than today (UTC) minus 2 days. A 404 for a date within 366 days latches, as A8 says; one older than 366 days is a hole.
8. **M9** lists tracked and untracked files (`git ls-files -co data/swap_tape`), not only tracked ones, so a zip dropped in before `git add` is caught;
   `-o` without `--exclude-standard` also lists files that `.gitignore` hides.
9. **Assertions added:** the Fisher and simple par breakevens must differ by less than 0.1 percentage point; the F0 warning needs at least 5 prior dates.
10. **Phase 0 had no Treasury file**, as the order of work required: the 13 Oct build before `fetch-ust` has all four spread rows `no_ust` and every cell,
    funnel and diagnostic intact. The numbers below are from the rebuild after `fetch-ust`.
11. **`--mutant`** exists on `build` for the A14 `nowindow` measurement; it refuses the repository's own `data/swap_tape`.

### 18.2 What the build found (corrections to the spec's own text, applied above)
- **§5 counts (CR13).** The "pairs" TERM→TERM 28, CORR→CORR 8, EROR→EROR 2 and MODI→MODI 1 are the 39 rows that reference themselves, not pairs; the same-file
  pairs are CORR→NEWT 810, MODI→NEWT 403, TERM→NEWT 378, EROR→NEWT 210, REVI→NEWT 3 (1,804 rows), and 1,380 more children name a parent that is not in the file.
- **The author's F0-F4 funnel and pre-A counts are exact.** F0 4,365, F1 4,326, F2 1,927, F3 1,758, F4 1,732. With the strike filter and the convention
  fallback switched off the build gives `all_platforms` 145/247/391/167 and ex-BILT 135/235/326/159 (the author's S2 figures). The A5 changes then move them:
  the strike filter removes 27 rows at F4s (1,732 → 1,705) and, within a tenor bucket, 1/2/20/3 `all_platforms` rows at 2/5/10/30y (ex-BILT: 0/0/0/3); the
  convention fallback adds 0/3/5/2 rows. Result: `all_platforms` 144/248/376/166, `fullday` (ex-BILT) 135/238/331/158. 11 rows had the rate leg's convention blank
  and the other leg's filled.
- **Placeholder rows:** 31 rows in the 13 Oct file carry `2000-01-01T00:00:00Z`: 23 NEWT (all TRAD, 21 after the EROR rule) and 8 MODI.
- **Labels outside F0 (diagnostics `unmatched_top10_sofr_ois`).** On 13 Oct 55 resolved trades are filed as `NA/Swap Fxd Flt USD` with the underlier
  `USD-SOFR-COMPOUND` and 38 with `USD-SOFR CME Term`; they are outside F0 by rule. Of the 55 only 4 are spot starts in a tenor bucket on the day. Whether such
  labels should join the OIS set is the supervisor's call; the diagnostic will show if the count grows.
- **Cross-currency per-tenor figures of S5 are reproduced exactly** by a diagnostic run (EUR/USD 1y n 6 −3.250, 2y n 8 −3.750, 3y n 3 −4.125, 4y n 2 −4.250, 5y n 7
  −4.500; GBP/USD 1y n 7 +2.500, 2y n 4 +2.625, 3y n 2 +2.438, 4y n 6 +2.125, 5y n 5 +1.500; JPY/USD 5y n 1 −26.0), and the funnels F0/F1/F2/F4/F7 are
  EUR/USD 63/63/46/39/26, JPY/USD 39/23/16/14/1, GBP/USD 47/46/35/34/24. Under A4 none of those per-tenor cells is published (all n < 10); only `pool1to5` is.

### 18.3 The builder's 13 Oct 2026 numbers (A14), CMT par 4.79/5.00/5.21/5.56

`sofr_ois` headline (14:30-16:30 New York, BILT out). All figures from `data/swap_tape/ledger_2026.csv` and `cells_2026.csv`; source DTCC Public Price Dissemination, CFTC cumulative rates reports (pddata.dtcc.com).

| tenor | n | median % | spread_quoted_bp | spread_bey_bp | bey_adj_bp | iqr/sqrt(n) bp | fullday quoted (n) | all_platforms quoted (n) |
|---|---|---|---|---|---|---|---|---|
| 2y | 12 | 4.660500 | -12.950 | -11.298 | 1.652 | 0.137 | -13.930 (135) | -14.139 (144) |
| 5y | 32 | 4.722375 | -27.763 | -26.545 | 1.217 | 0.145 | -28.650 (238) | -28.650 (248) |
| 10y | 35 | 4.821500 | -38.850 | -37.594 | 1.256 | 0.103 | -39.243 (331) | -39.999 (376) |
| 30y | 23 | 4.908500 | -65.150 | -64.020 | 1.130 | 0.065 | -65.600 (158) | -65.600 (166) |

`cpi_zc` headline (whole UTC day, BILT out), the gap between two different instruments (CPI zero-coupon swap minus Treasury par breakeven):

| tenor | n | swap median % | par / real CMT % | gap_fisher_bp | gap_simple_bp | status |
|---|---|---|---|---|---|---|
| 5y | 29 | 2.491250 | 5.00 / 2.67 | 17.873 | 16.125 | ok |
| 10y | 28 | 2.453750 | 5.21 / 2.88 | 14.364 | 12.375 | ok |
| 30y | 6 | 2.374250 | 5.56 / 3.28 | 11.846 | 9.425 | thin |

`xccy_basis` pooled over 1-5y (`pool1to5`), bp, spread on the non-USD RFR leg against flat SOFR:

| pair | n | median bp | iqr/sqrt(n) bp | status |
|---|---|---|---|---|
| EURUSD | 26 | -3.875 | 0.116 | ok |
| JPYUSD | 1 | - | - | below_min_n |
| GBPUSD | 24 | 2.438 | 0.083 | ok |

The `nowindow` mutant (A14) moves the 13 Oct quoted spread by −0.980/−0.887/−0.393/−0.450bp at 2/5/10/30y (headline −12.950/−27.763/−38.850/−65.150 → whole-day, BILT out, −13.930/−28.650/−39.243/−65.600): **it does not move the 10y by more than 1bp, so on 13 Oct the window does little at the 10y** (and nowhere more than 1bp). On 2025-04-09 the headline-minus-fullday gap at the 10y is +2.306bp.

### 18.4 The other three dates (10y and 30y; the full set is in the ledger)

| date | CMT 10y / 30y | 10y n | 10y quoted bp | 10y bey bp | 30y n | 30y quoted bp | 30y bey bp |
|---|---|---|---|---|---|---|---|
| 2025-04-09 | 4.34 / 4.72 | 82 | -51.850 | -50.016 | 46 | -85.615 | -83.766 |
| 2026-01-15 | 4.17 / 4.79 | 59 | -34.562 | -32.730 | 40 | -62.626 | -60.942 |
| 2026-09-29 | 5.26 / 5.59 | 43 | -38.491 | -37.285 | 46 | -66.234 | -65.123 |

| date | cpi 10y n | gap_fisher / gap_simple bp | cpi 30y n | gap_fisher / gap_simple bp | xccy pool1to5 EUR/USD (n) | JPY/USD (n) | GBP/USD (n) |
|---|---|---|---|---|---|---|---|
| 2025-04-09 | 11 | 11.063 / 10.000 | 5 | 9.289 / 7.750 | -7.000 (43) | -50.000 (55) | -2.500 (15) |
| 2026-01-15 | 23 | 14.876 / 14.030 | 3 | - / - | 0.375 (29) | -23.750 (39) | 6.750 (24) |
| 2026-09-29 | 9 | 12.054 / 10.025 | 7 | 11.492 / 9.050 | -2.750 (37) | -24.500 (17) | 2.500 (15) |

The pre-registered expectations hold: on 2025-04-09 the 10y `fullday` IQR is 5.776bp against 2.898bp on 13 Oct, and |headline − fullday| at the 10y is 2.306bp against 0.393bp. The 2025-04-09 10y headline IQR (6.145bp) is above the 5bp warning level, so the build printed `warn_iqr_10y_gt_5bp` for that date and wrote it to the diagnostics; no other warning fired.

### 18.5 The success criteria of §12 as run (builder's observations)

| # | Result | Observed |
|---|---|---|
| S0 | PASS | `selftest`: 180 checks, 0 failures; `DETECTED` for `noconv` (2 checks fail), `noeror` (21), `nowindow` (7). Sabotaging the mutants (none detectable) makes `selftest` exit 1. |
| S1 | PASS (exact) | `file_stats.csv` 2026-10-13: zip_sha256 `efdf5087…da3f`, zip_md5 `d966303f26482459c4f5cc26ebdd7d88`, rows 25,885; NEWT 22,662, CORR 1,171, MODI 1,135, TERM 671, EROR 241, REVI 5; NEWT/TRAD 17,858, COMP 4,642, NOVA 91, EXER 71. |
| S2 | PASS | Funnel F0-F4 = 4,365 / 4,326 / 1,927 / 1,758 / 1,732 (exact), then F4s 1,705, F5 1,705, F6 1,496, F6u 1,496. `fullday` n 135/238/331/158, medians 4.6507/4.7135/4.8176/4.9040% (author 4.6507/4.7133/4.8174/4.9040: within 0.02bp); 10y within 0.02bp of the hand figures 4.8174/4.8175. Gaps to the author's n are the strike filter and the convention fallback (§18.2). |
| S3 | PASS | `spread_quoted_bp` −12.950/−27.763/−38.850/−65.150 (30y negative); `spread_bey_bp` −11.298/−26.545/−37.594/−64.020; `iqr_over_sqrt_n_bp` 0.137/0.145/0.103/0.065 (all < 0.5). n 12/32/35/23. |
| S4 | PASS | `cpi_zc` headline n 29/28/6 and medians 2.49125/2.45375/2.37425% (exact); `gap_fisher_bp` +17.873/+14.364/+11.846 and `gap_simple_bp` +16.125/+12.375/+9.425 (author, simple basis: +16.13/+12.38/+9.43). 30y is `thin`. |
| S5 | PASS (exact) | Per-tenor n and medians, funnels F0/F1/F2/F4/F7 as in §18.2. Published under A4: `pool1to5` EUR/USD n 26 −3.875, GBP/USD n 24 +2.438, JPY/USD n 1 (below the floor). |
| S6 | deferred | package series (A6) |
| S7 | PASS | The four dates built into two empty directories: `diff -r` prints nothing; a third build in reverse date order also matches; rebuilding the clone twice leaves the sha256 of all 14 files in `data/swap_tape/` unchanged. |
| S8 | PASS | `grep -rEn '(^\|,)[0-9]{8,19}(,\|$)' data/swap_tape/` and `grep -rEl '[0-9]{19}' data/swap_tape` print nothing; no CSV header row contains `min` or `max`; `git ls-files data/swap_tape \| grep -iE 'CFTC_CUMULATIVE\|\.zip$'` and the `-co` variant print nothing; `git status --porcelain \| grep -i '\.zip'` prints nothing; `fetch` and `build` with `--cache` inside the repo exit 5 with "refused"; M9 fires on a zip and a 19-digit field planted in a scratch copy of the clone (and on a `git add -f` zip), and returns to ✓ when the plants are removed. |
| S9 | PASS | `bash bin/check.sh --all`: ✓ goal, ✓ M5, ✓ M6, ✓ M7, ✓ M8, ✓ M9 (six guard lines), `✓ no killed claims found`, `✓ page clean against all 270 ban patterns`. |
| S10 | PASS | 2026-09-29 rows 27,133; `header_ok` 1 on 2025-04-09 (38,481 rows), 2026-01-15 (27,285) and 2026-09-29; 2026-09-29 headline n 20/53/43/46 with `iqr_over_sqrt_n_bp` 0.206/0.088/0.126/0.215; 30y quoted spread −85.615 / −62.626 / −66.234 (and −65.150 on 13 Oct); `ust_used` 3.91/4.06/4.34/4.72 (2025-04-09) and 4.89/5.06/5.26/5.59 (2026-09-29), equal to the g4 relay. |
| S11 | PASS | `fetch_log.csv`: 7 requests, all HTTP 200; gaps between consecutive request starts 5.01, 5.009, 5.001, 17.226, 5.01, 5.004 s (minimum 5.001). |
| S12 | FAIL as written | `nowindow` moves the 13 Oct 10y quoted spread by −0.393bp, not more than 1bp. Per A14: on that date the window does little at the 10y (it moves the 2y by 0.98bp, the 5y by 0.887bp, the 30y by 0.45bp). |
| S13 | PASS | 2026-01-15 (EST): headline n 15/44/59/40, equal to a count of the same trades by the raw UTC text of the timestamp in [19:30, 21:30); with the summer offset the counts would be 13/41/45/32. 13 Oct (EDT): 12/32/35/23 from [18:30, 20:30). |
| Back-fill acceptance (A14) | not run | Only four non-adjacent dates are built: `summary.csv` reports 0 day-on-day pairs and the shares over 4 dates (headline 10y n >= 10 on 4 of 4; 30y negative on 4 of 4). |
| Pre-registered (HYPOTHESIS) | both held | 2025-04-09 10y `fullday` IQR 5.776bp against 2.898bp on 13 Oct; |headline − fullday| at the 10y 2.306bp against 0.393bp. |
