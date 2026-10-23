<!--
# source: International Energy Forum (IEF). Joint Organizations Data Initiative (JODI) Database. JODI Oil and Gas World Databases: www.jodidata.org, Accessed 23 October 2026. Derived statistics only; JODI reserves all rights; no JODI file is redistributed.
# source: U.S. Energy Information Administration (Oct 2026): STEO bulk file (release of 6 Oct 2026); Petroleum Supply Monthly series MCRSTUS1, MCESTUS1, MCSSTUS1, MCRFPUS2.
# vintage: see file_stats.csv and report.txt for the JODI files, their Last-Modified dates and the months covered. (These three lines are the acknowledgement every file in this folder begins with.)
-->
# JODI world oil ledger

This folder asks one question: is the line the US Energy Information Administration (EIA) uses to make world oil stocks add up, "other inventory draws and balance" in the Short-Term Energy Outlook (STEO), visible in the crude oil stocks that countries actually report to the JODI-Oil database (the Joint Organisations Data Initiative, run by the International Energy Forum)? To find out, it compares the month-to-month change in the closing crude stocks of a fixed list of countries outside the OECD (the Organisation for Economic Co-operation and Development) (nine of them at the registered build of 23 October 2026, and Saudi Arabia alone carries a little over half of the month-to-month variation) with that line, month by month from 2015. The sums are always over the same countries in every month; they are never world totals, because China, Russia and most Gulf states do not report stocks at all. The share of EIA's world crude production that JODI's reporters cover falls from about 0.97 in January 2015 (0.81 if the countries JODI flags "consult metadata" are left out) to about 0.67 in 2025 on JODI's 21 October 2026 file (0.59 on the September file, before JODI revised 2025), and that fall is countries that stopped reporting, not lower output.

**Result (registered build, 23 October 2026, on JODI's 21 October 2026 file, data to August 2026).** The nine-country panel's monthly stock draw moved only weakly with STEO's line: Pearson r = 0.14 over 137 months of changes (February 2015 to June 2026, each series demeaned by calendar month), with a 95% bootstrap interval of −0.08 to 0.29. The rule fixed on 18 October needed r of at least 0.25 with an interval above zero to support the idea, and r below 0.10 with an interval below 0.25 to count against it, so the verdict is INCONCLUSIVE: the test cannot tell whether STEO's balancing line contains stock change that these countries report. Saudi Arabia carries 57% of the panel's variation. Leaving out March to December 2020 and all of 2026 gives r = 0.15. The panel list was recorded and committed before the statistic was computed (sha256 in CALENDAR.tsv, row 2026-10-21), and an independent recomputation from the raw files by a second model family matched r, its interval and the concentration. July and August 2026 are preliminary and are not in the statistic.

## Words used here

- **CLOSTLV** is JODI's closing stock of crude oil at the end of a month, a level, in thousand barrels (KBBL). **STOCKCH** is JODI's reported stock change for the month, closing minus opening, in KBBL; a positive number is a build. JODI's own rule is `STOCKCH = CLOSTLV(t) - CLOSTLV(t-1)`.
- A **draw** is the negative of a stock change (positive = stocks fell), which is the sign STEO uses for its inventory withdrawals.
- A **reporter sum** is the total over whichever countries reported a number that month. The set of reporters changes from month to month, so a reporter sum is not a consistent series and is never published in barrels here.
- A **panel** is a fixed list of countries chosen by a rule and frozen for a vintage before the test runs. A barrel sum is published only for a panel, so no entry or exit of a country can be differenced out of it.
- **STEO's residual line** is `T3_STCHANGE_NOECD`, "Net Inventory Withdrawals, Total Non-OECD Crude Oil and Other Liquids", which STEO's Table 3a prints as "Other inventory draws and balance". It is a balancing item, not a measurement.

## What the files are

Every CSV starts with three lines that begin `#` (the JODI acknowledgement, the EIA acknowledgement, and the vintage: each JODI file with its Last-Modified date and the first 12 characters of its sha256, the latest month, the preliminary months). **Readers must skip lines that start with `#`.** An empty cell means "not applicable or not available". It never means zero. Numbers are in million barrels (mb) or million barrels a day (mb/d) to three decimals; coverage ratios are rounded to 0.01.

| File | One row per | What it holds |
|---|---|---|
| `panels.csv` | panel and member | the countries in each fixed panel (`panel`, `ref_area`, `oecd_member`, `months_usable`, `months_in_window`). No values. `months_usable` equals `months_in_window` for every member by construction. |
| `panel_aggregates.csv` | month, panel, flow | barrel sums over a fixed panel: `INDPROD` in mb/d for `panel_producers`; `CLOSTLV` (level) and `DCLOSTLV` (change, positive = build) in mb for `panel_nonoecd_stocks` and `panel_oecd_stocks_exspr`. Columns: `value`, `n_members` (members with a usable cell that month; the value is blank unless all are present), `n_code1`, `n_code3` (members whose cell has JODI assessment code 1 or 3), `data_status` (`final` or `preliminary`), `suppression` (`suppressed_diff_lt3` when the panel differs by one or two countries from another published panel). A panel with fewer than three members is not published. **In a DRY_RUN the `value` of every `panel_nonoecd_stocks` row (level and change) is blank and `suppression` is `withheld_dry_run`**; the counts stay. |
| `coverage_counts.csv` | month, reporter group, flow | counts only, for `reporters_all`, `reporters_oecd`, `reporters_nonoecd` and the flows `INDPROD` and `CLOSTLV`: reporters with code 1 or code 3, those with code 2 or 4 (excluded), those whose stock is zero in every month of the year file (`n_zero_reported`), cells that exist only in tonnes (`n_ktons_only`), those not reported, and the areas in that month's file. oecd + nonoecd = all in every column. |
| `steo_reconciliation.csv` | month | JODI against STEO. `steo_world_crude_mbd` is STEO's world crude oil production (mb/d), never total liquids. `coverage_reporters` is the INDPROD of the reporters with codes 1 and 3, divided by STEO's world crude; `coverage_reporters_allcodes` adds code 2; `coverage_panel` is the fixed producer panel divided by STEO. `steo_other_draws_balance_mb` is STEO's residual line times the days in the month (mb, positive = draw). `jodi_panel_nonoecd_draw_mb` is the non-OECD panel's draw (mb). `steo_residual_minus_panel_mb` is the first minus the second, month by month (there is no cumulative version). **In a DRY_RUN the draw and the residual-minus-draw columns are blank**; STEO's own line stays, since it is public. `seam_flag` marks a January whose change comes from JODI's STOCKCH. The last two columns compare the OECD panel (US less the Strategic Petroleum Reserve) with the change in STEO's OECD commercial inventory (mb): both rest on IEA data, so agreement is not independent evidence. |
| `primary_test.csv` | test or descriptive row | the one pre-registered test and its descriptive companions: Pearson r of the panel's draw against STEO's line on monthly changes demeaned by calendar month, a block-bootstrap 95% interval, Spearman rho, the house band 1.96/sqrt(n), the largest member's share of the panel's change variance, and a verdict from the decision rule. `run_status` is `REGISTERED` or `DRY_RUN`; in a DRY_RUN the statistic cells are blank. |
| `identity_checks.csv` | check, scope, code set | JODI's stock identity (does STOCKCH equal the change in CLOSTLV?), the December-to-January seams between year files, and the unit relation KBD x days = KBBL. The identity passes by construction for code-1 cells, so that pass rate describes the data and is not evidence. |
| `checkpoints.csv` | check | 22 rows (at most 30 are allowed): a handful of country-level values (US stocks against EIA, Saudi Arabia, Nigeria and Kuwait production against STEO, Japan, China, Russia). The only file with country-level values. STEO uses FIPS country codes, so Nigeria is compared with STEO's `COPR_NI`. |
| `file_stats.csv` | JODI year file | provenance: Last-Modified, bytes, sha256, rows, areas, first and latest period, counts of markers and of each assessment code. |
| `checks.csv` | check | every check with expected value, observed value and PASS, WARN, FAIL or INFO. |
| `fetch_log.csv` | request | every request the script has sent: UTC start, host, path, method, status, outcome, bytes, sha256, Last-Modified. |
| `report.txt` | | the build's report. It prints no reporter barrel sum; those appear in the terminal only. |
| `raw/` | | EIA's four Petroleum Supply Monthly workbooks (US government, public domain), `eia_steo_extract.csv` (the STEO series used, months 2014-12 to 2027-12), `eia_steo_release.txt` (the STEO entry of EIA's bulk manifest, which dates the release) and `pull_log.tsv`. |
| `SOURCES_JODI.md` | | citation, JODI's rights clause, what is cached and what is committed. |

## Groups, window and panels

- **Window.** From January 2015 to E, where E is the latest month of the vintage minus two (2026-06 at the registered build of 23 October 2026). The last two months are `preliminary`: published and flagged, never in a statistic. The start was chosen before any statistic was run: JODI coverage was near complete in 2015 and has fallen since, so a later start would add no members to a strict panel.
- **OECD** is the 38-member list for 2026, used for all months.
- **`panel_nonoecd_stocks`**: non-OECD areas with a usable closing stock (numeric, above zero, assessment code 1 or 3) in every month of the window. **`panel_oecd_stocks_exspr`**: OECD areas likewise, with the US figure taken as JODI's US stock less EIA's SPR (the US Strategic Petroleum Reserve) (JODI's US figure includes the SPR; see below). **`panel_producers`**: areas with a usable crude production figure in every month.
- **Reporter groups** (`reporters_*`) are every area with a usable cell that month. They appear only as counts and as coverage ratios.
- **Units.** JODI reports each number in five units that are one number re-expressed: KBD (thousand barrels a day), KBBL (thousand barrels), KL (thousand kilolitres), KTONS (thousand tonnes) and CONVBBL (the barrels-per-tonne factor JODI used). This build reads KBD for production and KBBL for stocks and never converts tonnes itself.
- **Assessment codes.** Codes 1 and 3 are used; code 2 ("use with caution") and code 4 ("under verification") are excluded and counted. The markers `-` (not reported), `x` (not applicable) and `..` (no factor) are missing, never zero.

## What the result can and cannot say

It can say what share of STEO's world crude production JODI's reporters cover, month by month; the reported crude stock changes of named, fixed panels; whether reported non-OECD crude stock changes move with EIA's residual line (after a registered build); and that JODI's US crude stocks include the SPR.

It cannot say anything about a world stock level or change, about product stocks, about prices (none enters this build: no price file, no price column, no regression), or about the present (every series is a revised vintage). It does not say that the residual is wrong if the test finds no link. Grades follow `CLAUDE.md`: a reporter sum is MEASURED on a stated panel; STEO's world withdrawal is BOUNDED and its residual line is a residual.

## The US Strategic Petroleum Reserve

JODI's US crude closing stock includes the SPR. Over 2025-01 to the last final month the median distance between JODI's US STOCKCH and the monthly change in EIA's total crude stock (MCRSTUS1) is 88 KBBL, against 1,950 KBBL for the change excluding the SPR, so the build prints `spr_included = yes`. The OECD panel therefore uses JODI's US figure less EIA's SPR (MCSSTUS1). Other OECD members' government stocks cannot be removed and remain. One month, 2025-03, differs by more than 2,000 KBBL (JODI -5,654 against an EIA rise of 3,549).

## Commands

```bash
python3 bin/build_jodi_oil_ledger.py selftest                    # synthetic rows, no network, a few seconds
python3 bin/build_jodi_oil_ledger.py fetch --all                 # JODI files to ~/jodi_oil/ (outside the repository), EIA files to raw/
python3 bin/build_jodi_oil_ledger.py check-vintage               # HEAD each annual file: which differ from the cache
python3 bin/build_jodi_oil_ledger.py build --panel-only          # writes panels.csv, prints its sha256
python3 bin/build_jodi_oil_ledger.py build --panel-sha <hex>     # the build proper; refuses if the panels now hash differently
```

The script sends one request at a time, at least 5.05 seconds apart, at most 20 per run, with the neutral User-Agent from `CLAUDE.md`, never follows a redirect, and writes `~/jodi_oil/STOP` on any status other than 200 or any unexpected body; while that file exists every fetch refuses, and only a person deletes it. `build` is offline and byte-identical on a re-run.

## Open items

- **US level offset.** JODI's US crude stock follows EIA's total (SPR included) change for change but sits 99 to 145 million barrels below EIA's level, and the gap grew between 2015 and 2025. Candidates: lease stocks, pipeline fill or Alaska in transit left out by the IEA definition. Settled by comparing the offset with EIA's stocks by type, or with the IEA stock definition.
- **Old-file vintages.** The year files for 2015 to 2024 were last modified on 21 October 2025 (2025 on 22 September 2026). On 21 October 2026 JODI regenerated the 2025 file but not 2015 to 2024, so a December-to-January seam can join two vintages (G09: 70 country-boundaries off at the registered build; January seams use the new file's reported stock change).
- **OECD membership over time.** The code uses the 2026 list for all months; whether STEO's OECD aggregate adds Colombia (2020) and Costa Rica (2021) at their accession dates is not stated in the bulk file.
- **Crude definitions.** Whether JODI's crude oil and STEO's crude oil both include lease condensate was not verified.
- **IEA terms for OECD history.** JODI's OECD months are IEA Monthly Oil Statistics. IEA's own licence was not re-read; only derived aggregates are committed.
- **Later builds.** The registered build of 23 October 2026 is the result. Later monthly rebuilds are descriptive updates and never replace it.
