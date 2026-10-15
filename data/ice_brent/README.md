# ICE Brent positioning ledger

A weekly table of who is net long and net short ICE Brent crude futures, by trader class, built from the Commitments of Traders history files that ICE Futures Europe publishes. It sits beside the CFTC's NYMEX WTI ledger ([data/cftc_cot/](../cftc_cot/)) so that a sentence about funds adding length can name the benchmark and the report type. It measures positions. It does not say that any position moved any price, or who paid whom: a futures long funds nothing physical, only margin moves, and every long has a short.

Every figure here is derived from ICE Futures Europe, Commitments of Traders historical files (ice.com/publicdocs/futures), and any note or page that quotes a number from this folder must name ICE and the report type beside it (futures only, or futures and options combined). Only derived statistics are published: **net** positions (long minus short) per class, their changes, one share of open interest, and dollars at the EIA Brent spot. No ICE file, row or gross figure is in this repository. The use is non-commercial research, ruled by the principal in [THE_ASK.md](../../THE_ASK.md) (E-025, which extends E-024); the terms and the licence position are in [SOURCES_ICE.md](SOURCES_ICE.md). The script is [bin/pull_ice_brent_cot.py](../../bin/pull_ice_brent_cot.py); the specification, with the supervisor's amendments in section 10, is [the spec](../../_research/2026-10-15-ICE-Brent-COT-Spec.md).

## Reading the files

- Every CSV starts with a line that begins `# source:`. It names ICE and the retrieval dates. **Readers must skip lines that start with `#`.**
- Positions are as of Tuesday's close; the build treats a report as due on the Friday after. The ledger has one row per report date: 823 weeks from 2011-01-04 to 2026-10-06 at the 15 October 2026 build, one in every ISO week. Four report dates are Mondays: 2012-12-24, 2012-12-31, 2018-12-24 and 2018-12-31 (the build lists any others as a warning in `checks.csv`; the first two are not on the spec's list of known Mondays). They are kept as ICE dates them.
- `fo` is futures only. `co` (in the ledger) and `combined` (in the windows and lead-lag files) is futures and options combined. ICE's file says which in `FutOnly_or_Combined`; the market name does not decide it (in 2011 both types carry the same name).
- A **net** is long minus short for one class. Spreading (a trader's offsetting long and short, which ICE reports for swap dealers, managed money and other reportables) belongs on both sides and drops out of every net. A negative net is a net short.
- One contract is 1,000 barrels. The script asserts ICE's `Contract_Units` on every row.
- The classes are the ones in ICE's file, which follows the CFTC's disaggregated layout: `pm` producer, merchant, processor or user; `sw` swap dealers; `mm` managed money; `ot` other reportables; `nr` non-reportables. How traders are assigned to the classes is ICE's, and this build does not check it.
- Percentages are percentage points of open interest, rounded to 0.1. The build checks the written text and stops if a percent column has more than one decimal. It treats every column whose name contains `pct` or ends `_pp` as a percent column, so a new one cannot slip past; the only exceptions are the six lead-lag correlations, which carry `pct` because the price change is in percent and are written at 3 decimals as in WTI's `leadlag.csv`. The gap between ICE's own percentages and the levels is not a column anywhere: it is text in `checks.csv` (K03).
- An empty cell means "not applicable" (the first week has no change). It never means zero.

## Files

| File | One row per | What it holds |
|---|---|---|
| `brent_ledger.csv` | report date | nets by class in contracts and barrels, their weekly changes, managed money's share of open interest, the Brent price (with a flag on known-bad EIA prints) and dollars |
| `brent_windows.csv` | report type and window | the change in managed-money net over 4, 12 and 52 weeks and since the 2023-12-26 and 2025-12-30 reports |
| `brent_leadlag.csv` | report type | the same lead-lag test as WTI's `leadlag.csv`, same columns in the same order |
| `brent_file_stats.csv` | ICE year file | sha256, size, retrieval time, header facts, row counts, report-date span, identity maxima, and how many of ICE's percentages were checked. No position figure |
| `checks.csv` | check | every check in the build with its expected value, observed value and status (PASS, WARN, FAIL or INFO) |
| `fetch_log.csv` | request | every request the script has sent (time, host, path, status, bytes, sha256) and every cache file it adopted |
| `raw/eia_RBRTEd.xls` | | the EIA Europe Brent spot price file (US government, public domain), committed so the ledger rebuilds offline |
| `SOURCES_ICE.md` | | citation, terms and licence position, and what the published percentages let a reader back-calculate |

### `brent_ledger.csv`

| Column | Meaning |
|---|---|
| `report_date` | ICE's report date, from `As_of_Date_In_Form_YYMMDD`. |
| `price_date`, `price_lag_days` | The date of the Brent quote used and how many days it precedes the report date (0 on most weeks; the build stops above 5). |
| `price_usd_per_bbl` | EIA's Europe Brent spot price (FOB), dollars per barrel, on the report date or the last earlier trading day. |
| `usd_basis` | `EIA_Europe_Brent_spot_FOB_not_ICE_settlement`. It is a spot assessment, not the ICE Brent futures settlement. The two track closely but are not identical, and managed money holds the whole futures curve. |
| `price_flag` | Empty normally. `suspect_eia_print` when the EIA print used (the one dated `price_date`) is on the script's `KNOWN_SUSPECT_PRINTS` list: today the EIA prints of 2 to 6 October 2026, about $20 above ICE's settlement (`CALENDAR.tsv`, the crude row). The dollar figures on a flagged row are computed from that print as it stands, and are not to be relied on; the nets are ICE's and are not affected. At the 15 October 2026 build one row is flagged, 2026-10-06. |
| `fo_pm_net`, `fo_sw_net`, `fo_mm_net`, `fo_ot_net`, `fo_nr_net` | Net contracts by class, futures only. |
| `fo_pm_net_bbl` ... `fo_nr_net_bbl` | The same five in barrels (contracts x 1,000). |
| `fo_resid_net` | The sum of the five nets. Exactly 0 for futures only. |
| `fo_pm_net_chg` ... `fo_nr_net_chg` | This week's net minus last week's, in contracts. Empty in the first week. |
| `fo_mm_net_pct_oi` | Managed-money net as a percentage of open interest, to 0.1. |
| `fo_mm_net_usd_bn` | Managed-money net x 1,000 x the price, in $bn. A notional at market, not a cash outlay. |
| `co_...` | The same columns for futures and options combined. `co_resid_net` is small but not always 0 (see below). |

## What the checks prove, and what they do not

ICE leaves its total-reportable and change-in-position columns blank on every Brent row, so the identities are stated without them. At every row, before anything is written:

1. The five classes plus their spreading plus non-reportable equal open interest, on each side. Futures only: exactly. Combined: within 4 contracts a side (the CFTC script's bound). At the 15 October 2026 build the largest gap on any combined row is 3.
2. The five nets sum to zero. This follows from the first, since the sum of the nets is the long-side gap minus the short-side gap. Futures only: exactly; combined: within 8 (largest observed: 3).
3. ICE's own `Pct_of_OI_<class>_<side>_All` columns agree with the level divided by open interest to within 0.05 percentage point on every populated value, for all ten class and side pairs: producer/merchant, swap dealers, managed money, other reportables and non-reportables, each long and short. At the 15 October 2026 build all ten pairs are populated on all 1,646 rows (16,460 values) and the largest gap on any pair is 0.0500, at the edge of the tolerance, so some rounding ties go either way. `checks.csv` K03 gives the count and the largest gap for each pair, and warns if any pair is populated on fewer rows than there are rows, or on none.
4. Two reports never fall in the same ISO week, none is missing, and the seam between two year files is 6 to 8 days.

**What this proves (MEASURED):**

- Checks 1 and 2: that the cells, as read, add up as one set on each side. A figure read from the wrong side, or a class dropped or counted twice, would stop the build.
- Check 3: that each level agrees with ICE's own percentage in the column of the same name. This is the check that sees two classes exchanged on the same side (the producer long read as the swap-dealer long, say), which checks 1 and 2 cannot see because the side sums and the net sum do not change. The selftest exchanges pairs of columns inside the parser and requires the build to stop each time.
- The managed-money net on 2026-03-31, read from ICE's file before the script existed, is reproduced (futures only 382,072; combined 429,853) and recorded in `checks.csv`.

**What it does not prove:**

- That non-reportable is measured. ICE publishes no total-reportable column, so this build cannot tell whether non-reportable is a count or is defined as open interest minus the classes, as the CFTC defines it. If it is defined that way, check 1 holds by construction and cannot fail, and the `nr` column is then the least secure number in the table: every error in the other four lands in it (CLAUDE.md, the residual rule). Treat `nr` as a residual until ICE says otherwise.
- Check 3 is certain to see an exchange of two classes only if their shares of open interest differ by more than 0.10 percentage point (twice ICE's rounding bound); closer than that it can miss one.
- Check 3 does not cover the spreading columns. An exchange between two of them changes no net and so no published figure.
- Check 3 compares two columns of one ICE file by name. If ICE had mislabelled a class in both its level and its percentage, nothing here would see it. Only managed money has an outside check, the pinned March nets.

## Caveats

- **Combined is rounded.** The combined report converts options to futures equivalents, so its figures are whole contracts and its identities hold only to rounding. The cause is inferred from the size of the residuals (at most 3 contracts), not stated by ICE.
- **The price is EIA's spot, not ICE's settlement.** The EIA file's prints for 2 to 6 October 2026 (135.51, 125.51 and 125.44 dollars) are flagged in `CALENDAR.tsv` as a data error (ICE settled near $102), and the ledger marks the rows that rest on them with `price_flag`. The 2026-10-06 dollar figure and that week's price change rest on the 125.44, and that row carries the flag. The lead-lag result barely moves without that week (the Pearson same-week figures are 0.581 and 0.661 with it, 0.588 and 0.668 without).
- **Timing.** Positions are as of Tuesday's close; the EIA spot is a daily assessment with no stated time. Part of Tuesday's move can fall in the "next week" return, which blurs the same-week and next-week test.
- **Lead-lag is correlation, not cause.** Trend-following and price pressure cannot be separated. For independent weeks, a correlation above about 1.96/sqrt(n) in size (0.163 at n = 145) is distinguishable from zero at 5%.
- **Brent against WTI.** The two ledgers have the same n (145 same-week, 144 next-week) from 2024-01-02. Their report dates differ in one week: ICE's is Tuesday 2025-11-11 where the CFTC's is Monday 2025-11-10.
- **The Kemp check is relayed.** Kemp's 253 million barrels for the week ending 2 June 2026 (futures and options) was relayed, not read at source. The combined managed-money net on 2026-06-02 is within 1% of it (`checks.csv`, K10); a miss would only warn.
- **Open interest is not published, but it can be estimated.** See [SOURCES_ICE.md](SOURCES_ICE.md).

## Running it

```bash
python3 bin/pull_ice_brent_cot.py selftest                       # synthetic rows only, no network, under 5 seconds
python3 bin/pull_ice_brent_cot.py fetch                          # the report year's ICE file and the EIA file (the only network command)
python3 bin/pull_ice_brent_cot.py fetch --years 2012-2017        # older years, once; cached years are not requested again
python3 bin/pull_ice_brent_cot.py fetch --refresh-year 2026      # one cached past-year file again (the New-Year seam, below)
python3 bin/pull_ice_brent_cot.py build                          # offline; rewrites every output, byte-identical on re-run
```

- The ICE files live in `~/ice_cot/`, outside the repository (`--cache` overrides; a path inside the repository is refused). They are never committed: `.gitignore` has `COTHist*.csv`, and `bash bin/check.sh --all` (M11) looks in the whole repository for a COTHist file in any letter case, and for ICE's header line in any file outside `bin/` and `_research/`.
- `fetch` sends sequential GET requests at least 5.05 seconds apart, at most 20 per run, to `www.ice.com` and `www.eia.gov` only, with the project's neutral User-Agent. It follows no redirect. The time of the last request is kept at full precision in `~/ice_cot/.last_request`, and the run lock in `~/ice_cot/.fetch.lock`, beside `STOP` and not in the cache, so two runs with different `--cache` values are still paced against each other and cannot overlap.
- Any status other than 200, or a body that is not the expected file, writes `~/ice_cot/STOP` and ends the run; while that file exists no fetch runs, and only a person deletes it. The expected file is, for ICE, a CSV that passes the header test and, for EIA, an XLS that the build's own reader loads (tested on the `.part` file, before it replaces the file already saved). A socket fault ends the run without a latch. Files already in the cache from before the script are logged as `adopted_from_cache`, without a request.
- The weekly refresh asks for the year of the latest expected report Tuesday (the most recent Tuesday at least 3 days before today), so on Friday 1 January 2027 it asks for 2026, not 2027.
- **The New-Year seam.** If the run of 1 January was missed, the cached 2026 file may stop before 2026's last report, and from Friday 8 January the weekly refresh asks for 2027 and leaves the old file alone; `build` then stops on the seam between the two years. `fetch --refresh-year 2026` requests that one file again although it is cached, and nothing else (no EIA request, and it cannot be combined with `--years`). It is paced, capped and latched like any other request. Then `build`.
- If `fetch` prints STOP, do not retry or route around it: tell the principal (THE_ASK.md E-025).
- `selftest` switches each guard off in turn, and exchanges pairs of class columns inside the parser, and fails if nothing notices. The fifteen cases the spec names are among them.
