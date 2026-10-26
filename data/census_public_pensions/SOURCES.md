# Sources, requests and builder decisions: Census Annual Survey of Public Pensions, national totals 2013-2025

Built by `bin/census_public_pensions.py` from the spec `_research/2026-10-26-Census-Public-Pensions-Spec.md` (committed at 104218d, with its rulings of rounds 1 to 4). Vintage `1e8f842133376a6b`; newest unit file ASPP_Unit_File_2025.csv (2026-05-14).

## What was seen of the answer before any build

Before any build, the spec author summed the national components for 2017, 2021 and 2022-2025 and read the summaries for 2013-2017 and 2021-2024. The second reviewer and Grok then
computed the ratios themselves: benefits per dollar of contributions about 1.313 (2023) and 1.328 (2025), a change of about +1.1%, and the three ratio revisions that set the band.
Nothing in the spec is blind, and no output carries a `blind` column. The builder did not look at any headline value before the selftest passed in full.

## Files requested by the build

Host `www2.census.gov` only; GET only; at least 3 seconds apart; no redirect followed; no retry; neutral User-Agent with no address; the 2020 unit file and the stale 2024 root files are never requested. One row per request, from `fetch_log.csv`:

| UTC time | Path | Status | Bytes | sha256 (first 12) | Last-Modified (UTC) |
|---|---|---|---|---|---|
| 2026-10-26T07:02:19Z | /programs-surveys/aspp/datasets/ | 200 | 20787 | ddf915916aeb | 2026-10-26T07:02:20Z |
| 2026-10-26T07:02:22Z | /programs-surveys/aspp/tables/2013/aspp-historical-tables/2013asppsummary.xlsx | 200 | 80510 | 5c380279f804 | 2018-08-06T19:04:22Z |
| 2026-10-26T07:02:25Z | /programs-surveys/aspp/tables/2014/aspp-historical-tables/2014asppsummary.xlsx | 200 | 80637 | 5e8e52e12d7b | 2018-08-06T19:04:02Z |
| 2026-10-26T07:02:28Z | /programs-surveys/aspp/tables/2015/aspp-historical-tables/2015asppsummary.xlsx | 200 | 88301 | 5ae7b33a4e55 | 2018-08-06T19:02:49Z |
| 2026-10-26T07:02:31Z | /programs-surveys/aspp/tables/2016/aspp-historical-tables/2016asppsummary.xlsx | 200 | 88055 | 3fbd45a949c9 | 2018-08-06T18:59:15Z |
| 2026-10-26T07:02:34Z | /programs-surveys/aspp/datasets/2017/aspp-historical-datasets/ASPP_Unit_File_2017.dsv | 200 | 12944671 | 02a9421bc88f | 2025-05-23T17:00:31Z |
| 2026-10-26T07:02:37Z | /programs-surveys/aspp/datasets/2018/aspp-historical-datasets/ASPP_Unit_File_2018.dsv | 200 | 4584477 | 8bb5f2dd3c52 | 2025-05-23T17:00:32Z |
| 2026-10-26T07:02:40Z | /programs-surveys/aspp/datasets/2019/aspp-historical-datasets/ASPP_Unit_File_2019.dsv | 200 | 7605304 | f7e0fb453aa9 | 2025-05-23T17:00:32Z |
| 2026-10-26T07:02:43Z | /programs-surveys/aspp/datasets/2021/aspp-historical-datasets/ASPP_Unit_File_2021.dsv | 200 | 7003313 | 0ff3408a543b | 2025-05-23T17:00:32Z |
| 2026-10-26T07:02:46Z | /programs-surveys/aspp/datasets/2022/aspp-historical-datasets/ASPP_Unit_File_2022.dsv | 200 | 16140954 | cca4556bd31d | 2026-05-14T15:15:31Z |
| 2026-10-26T07:02:49Z | /programs-surveys/aspp/datasets/2023/aspp-historical-datasets/ASPP_Unit_File_2023.dsv | 200 | 7585272 | f14067a9c86d | 2026-05-14T15:15:31Z |
| 2026-10-26T07:02:52Z | /programs-surveys/aspp/datasets/2024/aspp-historical-datasets/ASPP_Unit_File_2024.csv | 200 | 6969155 | 4d25da894335 | 2026-05-14T15:15:32Z |
| 2026-10-26T07:02:55Z | /programs-surveys/aspp/datasets/2025/aspp-historical-datasets/ASPP_Unit_File_2025.csv | 200 | 6750534 | ce8e85af5917 | 2026-05-14T15:15:32Z |
| 2026-10-26T07:02:58Z | /programs-surveys/aspp/datasets/2017/aspp-historical-datasets/ASPP_2017_Summary.xlsx | 200 | 35163 | 74fda1f30fce | 2025-05-23T17:00:31Z |
| 2026-10-26T07:03:01Z | /programs-surveys/aspp/datasets/2018/aspp-historical-datasets/ASPP_2018_Summary.xlsx | 200 | 56882 | 2cd469837e0b | 2025-05-23T17:00:32Z |
| 2026-10-26T07:03:05Z | /programs-surveys/aspp/datasets/2019/aspp-historical-datasets/ASPP_2019_Summary.xlsx | 200 | 56421 | 4d040eed8ca2 | 2025-05-23T17:00:32Z |
| 2026-10-26T07:03:08Z | /programs-surveys/aspp/datasets/2020/aspp-historical-datasets/ASPP_2020_Summary.xlsx | 200 | 60415 | 1be359863191 | 2025-05-23T17:00:32Z |
| 2026-10-26T07:03:11Z | /programs-surveys/aspp/datasets/2021/aspp-historical-datasets/ASPP_2021_Summary.xlsx | 200 | 56774 | dd8c08c9e44e | 2025-05-23T17:00:32Z |
| 2026-10-26T07:03:14Z | /programs-surveys/aspp/datasets/2022/aspp-historical-datasets/ASPP_2022_Summary.xlsx | 200 | 35351 | f5ce7cbe9a26 | 2025-05-23T17:00:33Z |
| 2026-10-26T07:03:17Z | /programs-surveys/aspp/datasets/2023/aspp-historical-datasets/ASPP_2023_Summary.xlsx | 200 | 59223 | 8f16519d2e3b | 2025-05-23T17:00:33Z |
| 2026-10-26T07:03:20Z | /programs-surveys/aspp/datasets/2024/ASPP_2024_Summary.xlsx | 200 | 58353 | 5629586c25a2 | 2025-05-23T16:45:31Z |

## Requests made by the spec author (before the build)

The spec author's 56 requests of 26 Oct 2026 (05:43 to 05:54 UTC, about 2 seconds apart, neutral User-Agent, no redirect followed, no retry), before any build:
`www.census.gov` (13): the three scoping URLs; `/programs-surveys/aspp/data/tables.html`, `/data/api.html`, `/data/datasets.html`, `/data/historical_data.html`;
`/programs-surveys/aspp/technical-documentation.html`; `/data/developers/data-sets/govspension.html`; `/data/tables/2013/econ/aspp/aspp-historical-tables.html`;
`/about/policies/citation.html`, all 200; `/about/policies/open-gov/open-data.html` **301, not followed**; `/robots.txt` **404**. `www2.census.gov` (43), all 200: the two layout PDFs,
the 2025 publication PDF, the 2024 methodology PDF, `/robots.txt`; directory listings of `datasets/`, `datasets/2013/`, `2016/`, `2017/`, `2021/`, `2022/`, `2024/`, `2025/`, the
`aspp-historical-datasets/` subfolders of 2013, 2016, 2017 (twice: an inadvertent repeat), 2018, 2019, 2020, 2021, 2022, 2023, 2024, 2025, and the file-layouts folder and its
`2017-2024/`; files: unit files 2013 (`.txt`), 2017, 2021, 2022, 2023 (`.dsv`), 2024, 2025 (`.csv`); summaries 2013, 2014, 2015, 2016, 2017, 2021, 2022, 2023, 2024. No request to
`api.census.gov` or `data.census.gov`. The spec author's copy was a temporary selftest-fixture seed, not a vintage.

An unverified figure (R3-2): Grok relayed $286.21bn as 2022 contributions from indexed text of the data.census.gov table `GOVSPENSIONTIMESERIES.GS00PENSION`, which it could not render. It is recorded here as unverified; the build holds $287.96bn from the 2022 unit file, and no data.census.gov request is made.

## Layout mappings, labels and codes

Item codes come from the 2017-2024 and 2022-2025 layout PDFs (identical apart from the file-format sentence). Fields by position: year, name, identifier, state, government type, item code, value, value flag, source flag, weight.

| Column | Codes | Summary label (2017 on) |
|---|---|---|
| contrib_employee_usd_mn | RX51 + RX52 | Employee contributions |
| contrib_government_usd_mn | RX60 + RX70 | Government contributions |
| contrib_total_usd_mn | RX51 + RX52 + RX60 + RX70 | Total Contributions |
| benefits_usd_mn | RX40 | Total Benefits Paid |
| withdrawals_usd_mn | RX80 | Withdrawals |
| earnings_ex_gains_usd_mn | RX01 (= RX10 + RX20; excludes gains) | Earnings on investments |
| gains_losses_usd_mn | RX30, signed | Gains/Losses on Investments |
| expenses_admin_invest_usd_mn | RX90 | Administrative Costs |
| assets_end_usd_mn | RZ01 (= RZ10 + RZ90) | Total cash and investments |

Never added on top: RX50 (equals RX51 + RX52), RX61 and RX62, RX71 to RX73, RX91 and RX92 (sub-lines), RJ (membership), RP (actuarial). Old-schema summary labels (2013-2016): `Total Contributions`, `Employee contributions`, `Government contributions`, `Benefits`, `Withdrawals`, `Earnings on investments`, `Total cash and investment holdings`, `Number of systems`. The summaries print `Investment Losses` as a positive number, so the build reads only the signed net line.

The 53 item codes: RJ01, RJ10, RJ11, RJ12, RJ20, RJ30, RJ31, RJ32, RP01, RP02, RP03, RP04, RP05, RP06, RP07, RP08, RP09, RP10, RP11, RP12, RP13, RP14, RP15, RP16, RP17, RP18, RP19, RP20, RP21, RX01, RX10, RX11, RX12, RX20, RX30, RX40, RX50, RX51, RX52, RX60, RX61, RX62, RX70, RX71, RX72, RX73, RX80, RX90, RX91, RX92, RZ01, RZ10, RZ90.

## Timing, schema change and the 2015 brief

Timing (2024 methodology): "The survey year encompasses the fiscal year beginning July 1 of the previous survey year and June 30 of the current survey year." Systems whose fiscal year ends after 30 June report the previous fiscal year; Alabama and Michigan state systems report October to September and Texas September to August. When holdings are measured is not stated in the publication, the layouts, the 2013 tables page or the methodology.

Schema change (2024 methodology, observed): Census streamlined the asset categories with the 2019 release and refitted 2017 and 2018 to the new schema, so the current files hold only cash and short-term versus long-term investments. Census points users who want granular asset detail to the Quarterly Survey of Public Pensions, which is out of scope here.

The 2015 brief (relayed via Grok, not fetched: `https://www.census.gov/content/dam/Census/library/publications/2016/econ/g15-aspp-sl.pdf`) says that more than 2,200 local systems were added, that the data may include hybrid and other post-employment funds, and that 2012 and 2015 should be compared only with caution.

The second reviewer observed that `ASPP_Unit_File_2020.dsv` on www2 has the same sha256 as the 2019 file and that every year field in it says 2019. It is never requested; 2020 comes from `ASPP_2020_Summary.xlsx`. The press release says benefits rose 3.40% from 2024; the unit files give 3.409%. That is a rounding note, not a check.

## Licence

Census's citation page asks users who make their own estimates to "cite the Census Bureau as the source of the original data only". The 2024 methodology treats the data as public record (relayed). Federal works carry no US copyright (17 U.S.C. 105; relayed; the open-data policy page answered 301 and was not followed). Raw files stay in the gitignored cache as a house choice (size, and they name individual systems), not as a licence requirement. `www2.census.gov/robots.txt` names a few crawlers and disallows nothing for others.

## Reference constants typed into the script (C15 to C17; never fetched)

- C15 (press release): U.S. Census Bureau, CB25-TPS.31, 14 May 2026: survey year 2025 contributions $315.02bn, benefits $418.25bn, cash and investments $6.49 trillion; survey year 2024 benefits $404.46bn (typed in; the supervisor checked them against the release).
- C16 (NASRA): NASRA Public Fund Survey, FY 2024, $5.13 trillion; relayed via Grok and the supervisor, not fetched (nasra.org is never requested). A different universe; a level check only.
- C17 (Z.1): Federal Reserve Z.1, table S129.3.s, "Funded by assets", 2025:Q2, $6,541.4bn; relayed, not fetched (federalreserve.gov is never requested). A level check only; no Z.1 transaction series is read.

## Builder decisions

1. **Encodings per unit file (R8):** 2017 cp1252, 2018 cp1252, 2019 cp1252, 2021 cp1252, 2022 utf-8-sig, 2023 utf-8-sig, 2024 utf-8-sig, 2025 utf-8-sig.
2. **FROZEN_BAND_PCT (R2-3):** the first build measured the largest absolute revision of `benefits_per_contrib_usd` between a year's summary and its unit file as 1.898% (`revision_band_pct`), and the largest over sample years as 0.176% (`revision_band_sample_years_pct`). Both are hard-coded in the script as `FROZEN_BAND_PCT = Decimal("1.898")` and `FROZEN_SMP_BAND_PCT = Decimal("0.176")`, and every later build uses those constants. In this build the constants in the script are 1.898 and 0.176.
3. **New item codes:** none outside the 53 listed in R3b were found (C20).
4. **The directory listing is a web page (R3a).** R3a latches STOP on any body that starts with `<!` or `<html`, but the one listing request (`/programs-surveys/aspp/datasets/`, an Apache index, observed to start with a DOCTYPE) is a web page by construction. The listing therefore gets its own content test: a non-200 status or an empty body latches STOP as for every request, and so does a page whose title is not `Index of /programs-surveys/aspp/datasets` (a refusal page). The 20 file requests use the R3a test as written. The listing is requested first, so a refusal stops the run before any file is downloaded.
5. **Body over the cap, and slices.** A body above 100 MB is not a refusal; it ends the run with exit 3 and no STOP. A run may take several invocations (`fetch --max-files N`): the folder `partial/` keeps `manifest.csv`, `requests.txt` (the run's request count, cap 30 across the invocations) and `notice.txt`; a saved file is never requested again; at most one run per calendar month is enforced from `fetch_log.csv`.
6. **O-10 (round 4), the 2025 system count.** The ruling asks for the count from the 2025 publication with `source_kind = publication`. The publication is not among the 20 files of the table and `source_kind` allows only `unit_file` and `summary`; taking it would need a request outside the table and a changed allowlist. The stricter reading is used: `systems_published` is blank for survey year 2025 and the README quotes the publication's 311 + 4,061 as text. Nothing is estimated.
7. **O-2 against R3-3.** O-2 says the README states that the old and current definitions are assumed comparable from their labels; R3-3 (later) replaces that with the 2015 brief's facts. The later ruling is applied and the README does not call the segments comparable.
8. **O-7 (round 4):** the README opening is two plain sentences; the second names the primary row and what its label means; the reviewer's remaining sentences follow the one denial sentence in the paragraph after the opening.
9. **O-9:** `net_cash_pct_of_assets_start` for 2015 is blank (its opening assets are 2014 assets, across the jump in the number of systems); the reason is in the README, because `ratios.csv` has no note column.
10. **C16 and C17** are PASS inside their stated ranges and WARN outside; C12 is WARN whenever a sub-line identity or a second weight is non-zero (as the spec observed for 2023), PASS if every identity holds. C12's sign is (sub-lines) minus (total line). C04 is split into C04 (same-vintage comparison) and C04p (the 2022 pin).
11. **Unit counts and second weights.** A unit is a distinct value of the unit identifier; `second weight` means a weight other than the unit's most common weight (ties: the smaller). Counts only are printed.
12. **C11 (fixed output)** compares a second, independent compute-and-render of every file except `checks.csv` with the first; the byte-identical re-run on disk is a separate step. **C21** is a check added by the builder: the folder guards (nine names, exact headers, no raw file, raw-row pattern, local path, at sign, banned wording, a real system name from the cache) run on the rendering.
13. **Percent change on a negative base** (`revisions.csv`, gains): 100 x (new - prev) / |prev|, so an improvement reads positive; the maximum absolute value is unaffected.
14. **Summary rows with no defined value are not written** (a ratio whose denominator is not positive). `n_years_net_cash_negative` carries the first and last year of its segment as `from_year` and `to_year`; `max_abs_revision_pct__<item>` carries the first and last year with a revision row.
15. **`ratio_cv_bound_pct` is 0 in full-count years** and blank where no CV is published (2025, and any year whose workbook prints none).
16. **Outputs of a build with a FAIL** are written to `data/census_public_pensions/_FAILED/` (gitignored), as in the house builds, and the committed files are left alone.
17. **Wording:** the README is scanned for the two G14 patterns outside the one denial sentence, and also for the direction verbs `rose` and `fell` (R3-1); the two G14 patterns are applied to the CSV files as well, which is stricter than the spec.
18. **S1** is written (`s1_revision_2025_pct`) only when two complete vintages are cached and the newest one's listing showed a survey-year folder above 2025; there is no such row yet.
19. **Spec prose against its own figures (C12).** The spec says that in 2023 RX60 exceeds RX61 + RX62 by 560.031 $mn, and lists the two differences as -560.031 and -12.930. This build finds, in survey year 2023, (RX61 + RX62) - RX60 = 560.031 and (RX71 + RX72 + RX73) - RX70 = 12.930: the magnitudes agree and the sub-lines are the larger side, so the spec's prose direction looks reversed; the published total line is used either way. The counts (515 units with a second weight, 4 non-blank rows carrying it) are read with the definition in item 11.
20. **C18 reads three lines only.** The largest CV on contributions, benefits and assets is 0.0020875 (survey year 2015). The spec's 0.0334 (2013) is the largest on any line of the summaries, which this build does not read.
21. **Listing reply.** The directory listing's `Last-Modified` is the time of the request itself, so its logged date is the retrieval time and is not part of any vintage key.
