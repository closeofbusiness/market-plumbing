# Spec: weekly ICE Brent Commitments-of-Traders ledger (supervisor, 15 Oct 2026)

*Written by the supervisor after reading one ICE file (COTHist2026.csv, fetched 15 Oct 2026). It is modelled on
`bin/pull_cftc_cot.py`. The earlier outside spec is Grok batch g4, item 2, in `_research/2026-10-14-Grok-G4-Returns.md`.*

*Sections 0-9 were amended by the builder on 15 Oct so that they agree with section 10 (the supervisor's amendments, kept below as the
record). Where a sentence in 0-9 changed, the amendment that changed it is named in square brackets. Section 11 lists what the builder
decided where the spec was silent.*

## 0. Goal

Crude sentences on the page and in E-021 have to name both the benchmark and the report type (C-142; g4 item 2).
- Today only NYMEX WTI positioning is measured, from the CFTC.
- ICE Futures Europe publishes the same disaggregated Commitments of Traders for Brent, but its site terms forbid automated
  retrieval. The principal ruled to script it on E-024's terms (THE_ASK.md E-025).
- This build adds a weekly Brent ledger beside the WTI one, so that "funds added length" can be stated for both benchmarks, by
  report type.

## 1. E-025 conditions (hard requirements)

**R1. Raw files stay outside the repository.**
- Cache: `~/ice_cot/` (override `--cache`, but refuse any path inside the repository).
- Files: `COTHist{YYYY}.csv` from `https://www.ice.com/publicdocs/futures/`, 2011 through the report year (the year of the latest expected
  report Tuesday, A9; 16 files in October 2026).
- Never committed, never copied into the repository. Add a .gitignore rule for `COTHist*.csv` anywhere.

**R2. Only derived statistics are published.**
- The committed outputs carry, per week and report type:
  - net positions (long − short) per trader class, in contracts and in barrels, for all five classes [A15];
  - their changes;
  - managed-money net as a share of open interest, rounded to 0.1 percentage point [A5];
  - dollar exposure at the EIA Brent spot price.
- They NEVER carry ICE's gross long, short, spreading or open-interest columns, or any per-trader-class gross figure.
- Every output file has an exact column allowlist, and a file whose header differs from it is a hard failure [A10]. This replaces the
  earlier blacklist. As a second, independent look, the gate (M11, A13) flags any header cell that is a banned gross name: a cell whose
  `_`-separated words include `long`, `short`, `spread`, `spreading` or `gross`, or that contains `open_interest`, or that has the word
  `oi` other than inside `pct_oi`.

**R3. ICE is cited.**
- Every output starts with a `# source:` line: "ICE Futures Europe, Commitments of Traders historical files (ice.com/publicdocs/futures), derived statistics only;
  non-commercial research (THE_ASK.md E-025)", plus the retrieval dates. The dates come from `fetch_log.csv`, so an offline build is
  byte-identical [A9].
- `data/ice_brent/SOURCES_ICE.md` says that CC BY 4.0 covers only the project's computation, and discloses what the published
  percentages allow a reader to back-calculate [A5].

**R4. Fetches are polite.**
- Requests are sequential, at least 5 s apart, and at most 20 per run.
- Use the CLAUDE.md non-SEC User-Agent, `Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)` [A16]. Allowed
  hosts are `www.ice.com` and `www.eia.gov` [A9]; assert no `@` in the agent.
- GET only; no redirect is followed [A9].
- The weekly refresh fetches only the report year's file, plus the EIA price file. The report year is the year of the most recent
  Tuesday at least 3 days before today, so on Fri 1 Jan 2027 it is 2026, not 2027 [A9].

**R5. Stop on refusal.**
- The latch is at the fixed path `~/ice_cot/STOP`, whatever `--cache` says. No fetch happens while it exists [A9].
- Any HTTP status other than 200 (a redirect is a status like any other), or a body that is not the expected file, writes the latch on
  either host. For ICE the expected body is a CSV that passes the header test (A3); for EIA it is an XLS (magic bytes D0CF11E0) [A3, A9].
  Nothing retries. Only a person deletes the latch.
- A socket fault ends the run without latching.
- `data/ice_brent/fetch_log.csv` records every request: UTC time, host, path, status, bytes, sha256 [A9].

## 2. Script

`bin/pull_ice_brent_cot.py`.
- Stdlib only, except `xlrd` for the EIA .xls, which is already in requirements.txt and used by `pull_cftc_cot.py`.
- Modes:
  - `fetch`, with `--years` (default: the report year) and the EIA Brent price file;
  - `build` (offline from the cache, byte-identical on re-run);
  - `selftest` (synthetic fixture rows only, never ICE rows).
- All outputs go under `data/ice_brent/`, never `data/cftc_cot/`, so that `pull_cftc_cot.py`'s `check_public()` is untouched [A2]. The
  EIA Brent file is public domain and is committed as `data/ice_brent/raw/eia_RBRTEd.xls`, with a row in
  `data/THIRD_PARTY_MANIFEST.tsv`. No ICE file is ever placed under `data/` [A2].

## 3. Parsing

- **Rows.** `Market_and_Exchange_Names` starts with `ICE Brent Crude Futures`. The report type comes from `FutOnly_or_Combined`
  (`FutOnly` → `fo`, `Combined` → `combined`). In 2011 both rows are named `ICE Brent Crude Futures`, so the name never decides
  the type.
- **Header test** [A3]. Strip a BOM. The first column must be `Market_and_Exchange_Names`, and a required set of named columns must
  be present (by name, in every year's file). Accept the `Swap_` and `Swap__` spellings. Ignore extra or unnamed trailing columns, and
  log them. A file that fails this test writes the latch; a file that passes is never latched over cosmetic differences.
- **Dates.** Read `As_of_Date_In_Form_YYMMDD` first. The other date field mixes `01/06/2026` and `1/13/2026`; it is read only to
  cross-check.
  - Key weeks by (ISO year, ISO week) [A12]. Assert exactly one report per week per type, with none missing inside each year's span.
  - Check the seams between year files: consecutive report dates are 6-8 days apart, or 13-15 days apart over a known holiday gap [A12].
  - Print any report date that is not a Tuesday. The known Monday report dates (2018-12-24, 2018-12-31) are allowed; any others are
    printed and recorded as a warning [A12].
- **Field names.** Accept both `Swap_Positions_Short_All` and `Swap__Positions_Short_All` (and the same for `Spread`). Log any
  column added or removed between years.
- **Units.** `Contract_Units` must read `(CONTRACTS OF 1,000 BARRELS)`. Assert it on every row. 1 contract = 1,000 barrels.
- **Code.** `CFTC_Commodity_Code` is `B`, and `CFTC_Contract_Market_Code` is blank in 2026. Record what earlier years show; do
  not rely on it.

## 4. Identities (asserted on raw rows, in memory, before anything is written) [A1]

ICE leaves `Tot_Rept_Positions_*` and the `Change_in_*` columns blank on every Brent row (blank in 2011, 2018 and 2026). So, unlike
`pull_cftc_cot.py`, the identities are stated without the reported totals:
1. Per side, the five classes plus their spreading plus non-reportable equal open interest.
2. The five class nets sum to zero. The build publishes `resid_net` per type: 0 for futures-only, small for combined.
3. Independent check: ICE's own `Pct_of_OI_M_Money_Long_All` and `Pct_of_OI_M_Money_Short_All` agree with the levels divided by open
   interest within 0.05pp on every populated value.

- **Futures-only:** exact.
- **Combined:** to rounding. Use the CFTC script's bounds: at most 4 contracts per side and 8 on the net sum. Print the observed
  maxima.
- If an identity fails, stop and name the week. Do not repair it.
- A blank total is not an error (a total, if ICE ever fills it in, is checked). A blank class figure is.
- These checks run on ICE's gross figures, which are never written out (R2).
- What they prove: that the cells were read from the right columns and add up as one set, and (check 3) ICE's internal percentage
  consistency for managed money. What they do not prove: that non-reportable is a residual. ICE publishes no total-reportable
  column, so this build cannot tell whether non-reportable is measured or is defined as open interest minus the classes. If it is
  defined that way, the sum-to-open-interest identity holds by construction and cannot fail (CLAUDE.md, the residual rule). The
  independent evidence for the managed-money columns is check 3 and the pinned 31 March nets in section 6.

## 5. Outputs (all under `data/ice_brent/`) [A2]

Every CSV starts with a `# source:` line (R3), then the header. Readers skip lines that start with `#`. Every file has an exact column
allowlist; a header that differs is a hard failure [A10]. Every percent column is rounded to 0.1pp, and the build checks the written text:
a percent column with more than one decimal is a hard failure [A5].

**`brent_ledger.csv`.** One row per report date. Columns, in order:
- `report_date`, `price_date`, `price_lag_days` (asserted at most 5), `price_usd_per_bbl`, and `usd_basis` =
  `EIA_Europe_Brent_spot_FOB_not_ICE_settlement`, mirroring the WTI ledger's label [A8];
- for each of `fo` (futures only) and `co` (futures and options combined; the prefixes the WTI ledger uses):
  - `{t}_pm_net`, `{t}_sw_net`, `{t}_mm_net`, `{t}_ot_net`, `{t}_nr_net` (contracts);
  - the same five in barrels, `{t}_pm_net_bbl` ... `{t}_nr_net_bbl` (1 contract = 1,000 barrels) [A15];
  - `{t}_resid_net`, the sum of the five nets [A1];
  - the weekly change in each net, `{t}_pm_net_chg` ... `{t}_nr_net_chg`;
  - `{t}_mm_net_pct_oi` (0.1pp);
  - `{t}_mm_net_usd_bn`, at the EIA Brent spot (`RBRTEd.xls`, Europe Brent Spot Price FOB) on the report date or the last earlier
    trading day.

**`brent_windows.csv`.** The change in managed-money net, in contracts and barrels, for each report type, over the last 4, 12 and 52
weeks and since the 2023-12-26 report ("since end-2023"), to match `windows.csv` for WTI [A6]. Plus "since end-2025 (new)", from the
2025-12-30 report, which WTI's file does not have. Columns follow `windows.csv` (`contract`, `report_type`, `window`, `weeks`,
`from_date`, `to_date`, `mm_net_from`, `mm_net_to`, `mm_net_chg`, `mm_net_chg_bbl`, `mm_net_pct_oi_from`, `mm_net_pct_oi_to`).

**`brent_leadlag.csv`.** The same test as `leadlag.csv` for WTI, with the same columns in the same order, including `first_week`,
`last_week` and `pearson_*_abs` [A7]:
- weekly change in managed-money net against the percent change in the Brent spot, P[t]/P[t-1] - 1 on report-date prices;
- same week, next week and previous week;
- report dates from 2024-01-01 to the latest week;
- Pearson and Spearman, with n and the 5% band 1.96/sqrt(n);
- the price lag is asserted at most 5 days; the build prints n beside WTI's and says why if it differs.

**`brent_file_stats.csv`.** Per year file: sha256, bytes, retrieval time, header facts (spelling, unnamed columns, columns added and
removed since the previous year), Brent row counts by type, first and last report dates, non-Tuesday dates, the codes and market names
seen, and the observed identity maxima and the percent-agreement maximum. No position figure.

**`checks.csv`.** One row per check in sections 4 and 6, with expected value, observed value and status (PASS, WARN, FAIL or INFO),
including the pinned 31 March nets [A4].

**`fetch_log.csv`.** Written by `fetch` [A9].

**`SOURCES_ICE.md`** and **`README.md`.** Per R3 and A5.

## 6. Cross-checks (with the expected values) [A4, A12, A14]

- **31 Mar 2026** (report date 2026-03-31), managed-money net, from the ICE file:
  - futures-only: 382,072;
  - combined: 429,853.
  The supervisor read both from COTHist2026.csv on 15 Oct. They are recorded as a pinned check in `checks.csv`. A mismatch prints
  WARN, plus the hint "ICE may have restated", and does not stop the build. No gross ICE figure appears in code, tests, outputs or
  notes.
- **External, relayed (warn only):** Kemp's "253 million barrels" for the week ending 2 Jun 2026 is futures and options. The
  combined `mm_net_bbl` at the 2026-06-02 report should be within +-1% of it. Print the result; do not fail on it.
- **The ledger's last report date** equals the last date in the current year's file, and equals the latest expected report Tuesday as
  of the file's retrieval date (a shortfall is a warning: ICE may not have published yet).
- **No output header** is outside its allowlist or carries a banned gross name (R2, A10).
- **Percent columns** carry at most one decimal in the written text (A5).
- **Re-run:** builds byte-identical outputs.

## 7. Selftest [A11]

- Synthetic rows only (dates in 2030-2031, never ICE rows), no network, under 5 seconds.
- Each of the following cases must make the selftest fail when its guard is removed:
  - blank totals accepted;
  - BOM header;
  - `Swap__` spelling;
  - a Monday report date;
  - 2011 same-name rows split by type;
  - latch on a non-200 response;
  - latch on a non-CSV body;
  - no latch on a socket fault;
  - pacing at least 5 s;
  - host allowlist;
  - refusal of an in-repo cache;
  - percent precision;
  - column allowlist (a gross-long column written to an output);
  - an identity off by 1 in futures-only;
  - a duplicate week.
- The build adds: a missing `Contract_Units` match, a blank class figure, the A9 year derivation, the XLS magic-byte check, the
  request cap and the STOP latch blocking a fetch.

## 8. Landing

- One clause added to the existing WEEKLY Friday COT row in `CALENDAR.tsv`: `python3 bin/pull_ice_brent_cot.py selftest`, then
  `fetch` (current report year), then `build` [A17].
- A data note in REPRODUCE.md.
- A `.gitignore` rule for `COTHist*.csv` anywhere.
- A warn-only M11 in `bin/check.sh`, in the M9 style: it flags any `COTHist*` file tracked or present anywhere in the repository,
  and any `data/ice_brent/` header carrying a banned gross column name [A13].
- A row for the EIA file in `data/THIRD_PARTY_MANIFEST.tsv` [A2].
- The supervisor writes any findings text after verification.

## 9. Open questions (marked)

- O-1: whether ICE files for earlier years carry the same columns. The build logs it. ANSWERED 15 Oct (section 11, F1): yes.
- O-2: whether ICE report dates are always Tuesdays (the CFTC's are not). ANSWERED (F2): no, four are Mondays.
- O-3: whether the 2011 file starts in January. The build records the first date. ANSWERED (F3): yes, 2011-01-04.

## 10. Supervisor amendments, 15 Oct (after the adversarial review; these OVERRIDE sections 0–9)

The builder applies these to sections 0–9 first, so that spec and code agree, then implements. "RV" refers to the review.

**A1. Identities, restated (RV1).** ICE leaves `Tot_Rept_Positions_*` and the `Change_in_*` columns blank on every Brent row.
They are blank in 2011, 2018 and 2026.
- Per side: the five classes plus their spreading plus non-reportable equal open interest.
  - Futures-only: exact.
  - Combined: within the template's bounds (4 per side, 8 on the net sum).
- The five class nets sum to zero. Publish `resid_net` per type, which is 0 for futures-only and small for combined.
- Independent check: ICE's own `Pct_of_OI_M_Money_Long_All` and `Pct_of_OI_M_Money_Short_All` agree with the levels ÷ OI within
  0.05pp on every populated value.
- State in the code and the README what these prove: the column mapping, and ICE's internal percentage consistency.
- State what they do not prove: that non-reportable is a residual.
- A blank total is not an error. A blank class figure is.

**A2. Separate output directory (RV2).**
- All outputs go under `data/ice_brent/`, never `data/cftc_cot/`, so `pull_cftc_cot.py`'s `check_public()` is untouched.
- The EIA Brent file is public domain. It is committed as `data/ice_brent/raw/eia_RBRTEd.xls`, with a row in
  `data/THIRD_PARTY_MANIFEST.tsv` in that file's format.
- No ICE file is ever placed under `data/`.

**A3. Header test (RV3).**
- Strip a BOM.
- The first column must be `Market_and_Exchange_Names`, and a required set of named columns must be present.
- Accept `Swap_` and `Swap__` spellings.
- Ignore extra or unnamed trailing columns, and log them.
- A file that fails this writes the latch. A file that passes is never latched over cosmetic differences.

**A4. Cross-checks state nets only (RV4).**
- 31 Mar 2026: futures-only 382,072, combined 429,853.
- They are recorded as a pinned check in `checks.csv`. A mismatch prints WARN, plus the hint "ICE may have restated", and does
  not stop the build.
- No gross ICE figure appears anywhere in code, tests, outputs or notes.

**A5. Precision and disclosure (RV5).**
- Every percent column in every output is rounded to 0.1pp. The build checks the written text: a percent column with more than
  one decimal is a hard failure.
- `SOURCES_ICE.md` discloses that open interest can be back-calculated from `mm_net` and the rounded percent to about ±0.6%
  (median), and that gross longs and shorts cannot be.

**A6. Windows match `windows.csv` (RV6).**
- 4, 12 and 52 weeks, plus "since end-2023" (the 2023-12-26 report).
- Add "since end-2025" (2025-12-30), labelled as new.

**A7. Lead-lag matches `leadlag.csv` exactly (RV7).**
- Same columns, in the same order, including `first_week`, `last_week` and `pearson_*_abs`.
- Report dates from 2024-01-01. Percent change P[t]/P[t−1] − 1 on report-date prices.
- Assert price lag ≤ 5 days. Print the n beside WTI's, and print why if it differs.

**A8. Price columns (RV8).**
- `price_usd_per_bbl`, `price_date`, `price_lag_days` (assert ≤ 5).
- `usd_basis` = `EIA_Europe_Brent_spot_FOB_not_ICE_settlement`, mirroring the WTI ledger's `usd_basis` label.

**A9. Fetch and latch rules, as in `bin/swap_tape_ledger.py` (RV9, RV10).**
- The latch is at the fixed path `~/ice_cot/STOP`, whatever `--cache` says. No fetch while it exists.
- GET only, and no redirects followed: a redirect latches.
- Host allowlist: `www.ice.com` and `www.eia.gov`.
- An XLS magic-byte check (D0CF11E0) on the EIA file.
- Any failure on either host latches. A socket fault ends the run without latching.
- `data/ice_brent/fetch_log.csv`: UTC time, host, path, status, bytes, sha256. The `# source:` retrieval dates come from it, so
  the offline build is byte-identical.
- The weekly refresh takes its year from the latest expected report Tuesday: the most recent Tuesday at least 3 days before today.
  On Fri 1 Jan 2027 that requests the 2026 file, not 2027.

**A10. Exact column allowlist per output file (RV12).** This replaces the blacklist. A file whose header differs from its
allowlist is a hard failure.

**A11. Selftest mutants (RV11).** Synthetic rows only. Each case must make the selftest fail when its guard is removed:
- blank totals accepted;
- BOM header;
- `Swap__` spelling;
- a Monday report date;
- 2011 same-name rows split by type;
- latch on a non-200 response;
- latch on a non-CSV body;
- no latch on a socket fault;
- pacing ≥ 5 s;
- host allowlist;
- refusal of an in-repo cache;
- percent precision;
- column allowlist;
- an identity off by 1 in futures-only;
- a duplicate week.

**A12. Dates (RV15).**
- Key weeks by (ISO year, ISO week).
- Check the seams between year files: consecutive report dates are 6–8 days apart, or 13–15 days apart over a known holiday
  gap.
- Allow the known Monday report dates (2018-12-24, 2018-12-31), and print any others.
- The last-date check compares the ledger's last date with the latest expected report Tuesday.

**A13. Gate (RV13).**
- Add a warn-only M11 to `bin/check.sh`, in the M9 style. It flags any `COTHist*` file tracked anywhere, and any `data/ice_brent/`
  header carrying a banned gross column name.
- Show it fires on a plant in a scratch copy.

**A14. Kemp check (RV14).** Within ±1%, warn only, against combined `mm_net_bbl` on 2026-06-02.

**A15. Barrels per class (RV16).** Every class net is also published in barrels.

**A16. User-Agent.** Use the CLAUDE.md canonical non-SEC string:
`Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)`.

**A17. Calendar.** The WEEKLY Friday COT row gains one clause:
`python3 bin/pull_ice_brent_cot.py selftest`, then `fetch` (current report year), then `build`.

## 11. Builder notes (15 Oct, after the build; not supervisor text, the supervisor may overrule any item)

Observed with `bin/pull_ice_brent_cot.py` on the 16 files in `~/ice_cot/` (2011 to 2026; 823 report dates, 2011-01-04 to 2026-10-06, two report
types), and the EIA file of 15 Oct. Numbers here are counts, dates and nets only.

**Where the spec was silent, the builder decided:**
- D1. Ledger column prefixes are `fo_` and `co_`, the WTI ledger's, not `combined_`, so that the two ledgers join by name. The report-type
  value in the windows and lead-lag files is `combined`, as in WTI's.
- D2. Three of the 16 files (2011, 2018, 2026) were in the cache before the script existed, so no request logged them. `fetch` adopts any cache
  file whose content the log does not know, with no request, as an `adopted_from_cache` row stamped with the file's modification time (all
  2026-10-15). `build` refuses a cache file with no log row of the same sha256.
- D3. The header test (A3) latches in `fetch`, where a failing body is a refusal. `build` is offline: a cached file that fails the test is an
  error that stops the build, and it writes no latch.
- D4. The ten Pct_of_OI_<class>_<side>_All columns (pm, sw, mm, ot, nr x long, short), the CFTC code columns and the second date field are
  optional in the header test (used where present; all are present in all 16 files), so that a file is never latched over them (A3). The
  required set is the name, date, units, type, open interest and the 14 class columns.
- D5. `Tot_Rept_Positions_*`, if ICE ever fills them in, are checked against the classes (A1's "a blank total is not an error"). They are
  blank on every row today.
- D6. The last-date check (A12) compares with the latest expected report Tuesday as of the newest file's retrieval date, not as of the clock,
  so that an offline re-run stays byte-identical. A shortfall is a WARN (ICE may not have published); a surplus is a FAIL.
- D7. The window "since end-2025" is labelled `since end-2025 (new)` in the `window` column, so that a join with `windows.csv` on the label cannot
  pair it with anything.
- D8. `checks.csv` carries a fourth status, INFO, for facts that are neither pass nor fail (the open-interest back-calculation, the column sets).
- D9. A header cell is banned if its words include long, short, spread, spreading or gross, or it contains open_interest, or it has the word oi
  outside `pct_oi`. The same rule is in the script and in M11.
- D10. The lead-lag function starts at the first report date from 2024-01-01 but never before the second week, which changes nothing on the
  real data. It reproduces WTI's `leadlag.csv` exactly (all 19 columns, both report types) when given the WTI series.

**What the build found:**
- F1 (O-1). All 16 files carry the same named columns. The only differences are cosmetic: the short and spread columns of swap dealers are
  spelled `Swap__` in 2011-2020 and `Swap_` in 2021-2026, and the 2018 file has one unnamed trailing column. No column was added or removed.
- F2 (O-2). ICE's report dates are Tuesdays except four Mondays: 2012-12-24, 2012-12-31, 2018-12-24 and 2018-12-31. A12 lists only the 2018
  pair, so the 2012 pair is printed and recorded as a WARN (checks.csv K06). The CFTC dates the same four weeks as Mondays. Since 2011 the two
  ledgers' report dates differ in exactly four other weeks, where the CFTC has a Monday and ICE the Tuesday: 2017-07-03/04, 2020-12-21/22,
  2023-07-03/04 and 2025-11-10/11.
- F3 (O-3). The 2011 file starts on 2011-01-04.
- F4. `CFTC_Contract_Market_Code` is blank in all 16 files and `CFTC_Commodity_Code` is `B` in all 16 (the spec said blank in 2026 only).
- F5. No 13-15 day gap exists: every ISO week from 2011-W01 to 2026-W41 has one report, so `KNOWN_HOLIDAY_GAPS` is empty.
- F6. The identities hold on all 1,646 rows. Futures only: exact. Combined: at most 3 contracts a side and 3 on the net sum.
- F7. ICE's own percentages agree with level over open interest within 0.0500pp on all 16,460 populated values of the ten class/side pairs
  (1,646 of each pair, none blank): the bound is met at its edge (rounding ties), and no value is outside it. The first build checked
  managed money only (3,292 values); the other eight pairs were added after the verification review (X1).
- F8. The A5 estimate "about +-0.6% (median)" is the median half-width of the rounding interval (measured +-0.57%); the realised median error
  is 0.27%, the 90th percentile 0.65% and the worst week 12.0%, in a week when the share was near zero.
- F9. The EIA Brent prints for 2, 5 and 6 October 2026 are the ones CALENDAR.tsv flags as a data error. The ledger's last price (2026-10-06)
  is the 125.44 print. Dropping that week moves the same-week Pearson figures from 0.581 to 0.588 (futures only) and 0.661 to 0.668 (combined).
- F10. A1 says the identities prove the column mapping. That is too much, for two reasons. (a) The identities hold by construction if ICE
  defines non-reportable as open interest minus the classes, as the CFTC does, and then prove nothing about any column. (b) Even if
  non-reportable is measured, they cannot see two classes exchanged on the SAME side (pm_long read as sw_long and the reverse): the side sums
  and the net sum do not change. What they do show is that the cells add up as one set on each side, so a figure read from the wrong side, or a
  class dropped or counted twice, would stop the build. The mapping rests on the percentage agreement of check 3, which since X1 covers all
  ten class/side pairs and so sees a same-side exchange (certain only where the two shares differ by more than 0.10pp, twice ICE's rounding
  bound), and for managed money on the pinned 31 March nets (both reproduced). Check 3 does not cover the spreading columns (an exchange
  between two of them changes no net, so no published figure) and compares two columns of one file by name (a class mislabelled in both its
  level and its percentage would pass). The README and the script say so in these terms.
- F11. The net-sum bound of 8 cannot bind on its own: the sum of the five nets equals the long-side gap minus the short-side gap, so a
  bound of 4 on each side implies 8 on the sum. It is kept as stated.

**Fixes after verification (15 Oct).** The verification review found these; each is in the script, the README or `checks.csv`:
- X1. Column mapping. The percentage agreement of A1's third check is now a hard check on all ten class/side pairs, within 0.05pp, with n and
  the largest gap per pair in `checks.csv` K03. The selftest exchanges pairs of columns inside the parser (pm_long/sw_long, sw_short/pm_short,
  mm_long/ot_long, ot_short/nr_short, pm_long/nr_long, mm_short/nr_short) and requires each to be noticed; it also shows that the identities
  alone do not see a same-side exchange and do see a cross-side one. See F10.
- X2. Pacing and lock. `.last_request` and `.fetch.lock` sit beside the fixed STOP path (`~/ice_cot/`), not in `--cache`; the time is written at
  full precision; the floor between request starts is 5.05 s (A9's 5 s plus a margin).
- X3. Percent precision. `agree_max_dev_pp` is gone from `brent_file_stats.csv` (a percent column at 3 decimals); the statistic is text in K03.
  The precision guard treats any column whose name contains `pct` or ends `_pp` as a percent column; the six lead-lag correlation columns
  (`pearson_*_pct`, `spearman_*_pct`, which carry `pct` because the price change is in percent) are the one named exemption.
- X4. Selftest blind spots. Pinned: every window row against the ledger it came from (weeks, both dates, both nets, both shares, the change); the
  lead-lag numbers against an independent recomputation (same, next and prev shifts, n, the three correlations, the band 1.96/sqrt(n) with the
  literal 1.96); the start of the lead-lag sample on a series that straddles 2024-01-01; the price at four decimals.
- X5. K03 is WARN when any percentage pair is populated on fewer rows than there are rows, or on none.
- X6. K15 and K16 report what was observed (the files verified and the header cells counted; the percent cells counted and the most decimals
  found), not constants.
- X7. `fetch` validates the EIA body by loading it (`load_eia_brent`) from the `.part` file before it replaces the saved one. xlrd's errors become
  `DataError`. A body that does not load latches like any other bad body and leaves the saved file untouched.
- X8. The gate is M11, because another session landed an M10 (the User-Agent check) upstream. It also catches COTHist file names in any letter
  case and ICE's header line in any file outside `bin/` and `_research/`.
- X9. `brent_ledger.csv` has `price_flag` (empty, or `suspect_eia_print` for a report date whose EIA print is in `KNOWN_SUSPECT_PRINTS`, initially
  2-6 Oct 2026; `CALENDAR.tsv`'s crude row says those prints are about $20 above ICE's settlement). The USD figures stay as computed; the nets
  are not touched.
- X10. `CALENDAR.tsv`'s Brent clause says that if `fetch` prints STOP, do not retry or route around it: tell the principal.
- X11. `fetch --refresh-year YYYY` requests one cached past-year file again (paced, capped, latched; no EIA request; not with `--years`). The README
  explains the New-Year seam case.
- X12. `SOURCES_ICE.md` begins with a line that names ICE.
