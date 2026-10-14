# Swap-tape ledger

A daily table of three swap-market levels, built from the public price dissemination (PPD) that DTCC publishes under the CFTC's real-time reporting rules. It measures levels and gaps. It does not say that any flow moves any price.

- **USD SOFR OIS minus Treasury par** at 2, 5, 10 and 30 years (the "swap spread").
- **USD CPI zero-coupon swap rate minus the Treasury par breakeven** at 5, 10 and 30 years. This is a gap between two different instruments, not a breakeven.
- **The spread on the non-USD leg of OIS-versus-SOFR cross-currency swaps** (EUR/USD, JPY/USD, GBP/USD), per tenor from 1 to 5 years and pooled over 1 to 5 years.

Every figure here is derived from DTCC Public Price Dissemination, CFTC cumulative rates reports (pddata.dtcc.com), and any note or page that quotes a number from this folder must name that source beside it. Only statistics are published: medians, quartiles, counts and shares, under a count floor (below). No DTCC file, row or identifier is in this repository. The use is non-commercial research, ruled by the principal in [THE_ASK.md](../../THE_ASK.md) (E-024); the terms and the licence position are in [SOURCES.md](SOURCES.md). The build specification, with the supervisor's amendments at the end, is [the spec](../../_research/2026-10-14-Swap-Tape-Ledger-Spec.md). The script is [bin/swap_tape_ledger.py](../../bin/swap_tape_ledger.py).

## Reading the files

- Every CSV starts with a line that begins `# source:`. It names DTCC and the retrieval dates. **Readers must skip lines that start with `#`.**
- An empty cell means "not published" (the count floor) or "not applicable". It never means zero.
- Dates are UTC dates of the DTCC file. A trade belongs to the date it was executed (UTC), and the Treasury figure is the constant-maturity (CMT) yield for the same New York date.
- Rates are percent, to 6 decimals. Spreads, gaps and dispersions are basis points, to 3 decimals. Sizes are kB with one decimal.
- Only weekdays are in the ledger. A weekday with no cached DTCC file has a `date_status` row with status `no_file`; a weekday with no Treasury row (a holiday) has `no_ust` on its spread rows; a file that fails the header check has `schema_mismatch`; a failed internal assertion has `error`.

## The count floor

The same rule applies to every cell and every diagnostic.

| n (observations) | What is published |
|---|---|
| fewer than 5 | the count only |
| 5 to 9 | the count and the median (status `thin`) |
| 10 or more | also the quartiles, the IQR, IQR divided by the square root of n, and the shares (status `ok`) |

Two exceptions are stricter. A `sofr_ois` headline spread needs n of at least 10. A per-tenor cross-currency cell needs n of at least 10 and has no `thin` level; the pooled `pool1to5` cell follows the general floor. There is no minimum, no maximum and no notional-weighted median anywhere, because a minimum or maximum is a single trade's price.

## Files

| File | One row per | Columns |
|---|---|---|
| `ledger_YYYY.csv` | date, measure, pair, tenor | see below |
| `cells_YYYY.csv` | date, series, tenor, variant | the statistics behind the ledger |
| `funnel_YYYY.csv` | date, series, step, tenor | how many trades survive each filter |
| `diagnostics_YYYY.csv` | date, key | calibrations recomputed every date |
| `file_stats.csv` | DTCC file | provenance and denominators (hashes of the zip, row and action counts) |
| `ust_used.csv` | date | the Treasury CMT values that were joined (public domain) |
| `summary.csv` | key | cross-date statistics recomputed from the ledger at every build |
| `fetch_log.csv` | request | every request the script has sent: time, host, path, status, size, hash |
| `holes.csv` | date | dates DTCC no longer serves (a 404 more than 366 days old) |
| `SOURCES.md` | | citation, terms and licence position |

### `ledger_YYYY.csv`

| Column | Meaning |
|---|---|
| `date_utc` | The DTCC file date and the Treasury date. |
| `measure` | `swap_spread`, `cpi_zc_minus_ust_par_be`, `xccy_basis`, or `date_status`. |
| `pair` | `EURUSD`, `JPYUSD` or `GBPUSD` for `xccy_basis`; blank otherwise. |
| `tenor_y` | Tenor in years (2, 5, 10, 30 for swap spreads; 5, 10, 30 for the CPI gap; 1 to 5 for cross-currency) or `pool1to5`. |
| `n` | Trades in the headline cell. |
| `spread_quoted_bp` | **The headline swap spread**: the cell's median OIS fixed rate in bp minus the CMT par yield in bp, with no conversion, the way dealers quote it. Negative means the swap rate is below the Treasury yield. |
| `spread_bey_bp` | The same, with each trade's annual ACT/360 rate first converted to a semiannual bond-equivalent rate (its own accrual factor, expiry minus effective in days over 360 times the tenor) before the median. |
| `bey_adj_bp` | `spread_bey_bp` minus `spread_quoted_bp`. An identity; the build asserts its size is at most 3bp. |
| `gap_fisher_bp` | **The headline CPI gap**: the median zero-coupon swap rate (annual) minus the Fisher-consistent annualised par breakeven, ((1 + n/2) / (1 + r/2))^2 - 1, where n is the nominal CMT yield and r the TIPS real CMT yield at the same tenor. |
| `gap_simple_bp` | The sensitivity: the median zero-coupon swap rate minus (n - r). |
| `xccy_median_bp` | Median spread added to the non-USD risk-free-rate leg against flat SOFR, in bp. Negative is the conventional sign of a dollar premium; some of the literature uses the opposite sign. |
| `iqr_over_sqrt_n_bp` | The headline cell's IQR divided by the square root of n, in bp. It is a sampling-noise scale, not the ledger's precision (see "What the numbers can and cannot resolve"). |
| `swap_median_pct` | The cell's median rate in percent (swap spread and CPI rows). |
| `ust_par_pct`, `ust_real_pct` | The CMT par and TIPS real yields used, in percent. |
| `par_be_fisher_pct` | The Fisher-consistent par breakeven used for `gap_fisher_bp`, in percent. |
| `fullday_quoted_bp`, `n_fullday` | Variant: the quoted spread from the whole UTC day, BILT excluded, and its n. |
| `allplat_quoted_bp`, `n_allplat` | Variant: the quoted spread from the whole UTC day with BILT included, and its n. |
| `grade` | `MEASURED` (see CHARTER.md): a statistic of headline-filtered prints executed on the date, against the CMT of the date. `bey_adj_bp` and `par_be_fisher_pct` are IDENTITY. |
| `status` | `ok`, `thin`, `below_min_n`, `no_ust`, `no_file`, `schema_mismatch`, `error`. |

### `cells_YYYY.csv`, `funnel_YYYY.csv`, `diagnostics_YYYY.csv`

- `cells`: `series` is `sofr_ois`, `sofr_ois_bey` (the bond-equivalent conversion, headline only), `cpi_zc`, `xccy_eurusd`, `xccy_jpyusd` or `xccy_gbpusd`. `variant` is `headline`, `fullday`, `all_platforms` or (CPI only) `cmt_window`. `unit` is `pct` (median, q1, q3 in percent) or `bp`. `iqr_bp` and `iqr_over_sqrt_n_bp` are always bp. `share_pkg` is the share of trades flagged as part of a package; `share_gt10bp` is the share more than 10bp from the cell median.
- `funnel`: steps F0 to F9. F0 resolved trades of the series; F1 executed on the file date (UTC); F2 spot start (0 to 5 days); F3 no upfront payment; F4 not post-priced and not a non-standard term; F4s no strike price; F5 leg structure; F6 conventions; F6u plausible rate; F7 tenor bucket (expiry within 7 days of effective date plus N years); F8 platform is not BILT; F9 executed 14:30 to 16:30 New York. The steps differ a little for the CPI and cross-currency series (the spec section 6 lists them).
- `diagnostics`: `key`, `value`, and `n` (the count a statistic rests on). Keys include the BILT cluster (`bilt_n_T`, `bilt_median_dev_bp_T`), the count of non-BILT trades more than 10bp from the cell median (`gt10bp_nonbilt_T`), the hourly medians by New York hour where an hour has at least 10 trades (`hourly_median_pct_Ty_nyHH`), how many trades were corrected, dropped as errors or revived (`corr_applied`, `corr_changed_terms`, `eror_dropped`, `revived`, `modi_rate_changed`), the cross-currency spread notation codes seen, the top ten product labels that a series did not match (`unmatched_top10_*`), and `warn_*` keys for the checks listed in the spec (section 13). A warning is information about the tape, not a failure.

## What the headline is

- **Swap spread.** The headline cell is built from OIS prints executed from 14:30 to 16:30 New York time (daylight saving taken from the trade's date), which brackets the Treasury CMT's 15:30 snapshot. The BILT platform code is excluded from the headline and shown in the `all_platforms` variant, because on one date its 10-year prints sat about 62bp below the rest. What BILT denotes is believed to be off-facility execution and has not been read from the CFTC specification.
- **CPI gap.** The headline cell is the whole UTC day with BILT excluded (a two-hour CPI cell would almost never reach 5 trades). Part of any 30-year gap is the par-versus-zero curve-shape term: the swap is a zero-coupon instrument and the Treasury breakeven is a par figure.
- **Cross-currency.** No platform filter and no time window. Per-tenor cells are rarely at 10 trades on a single day; read `pool1to5`.

## What the numbers can and cannot resolve

- The CMT prints to 0.01 percentage points, so each spread carries up to 0.5bp of rounding and each day-on-day change up to 1bp.
- The smallest daily change in a liquid-tenor swap spread that this ledger can claim to resolve is about 2bp. That is the author's judgement (a HYPOTHESIS). `summary.csv` measures it over the back-fill: the standard deviation of day-on-day changes in the 10-year quoted spread on all dates, and beside it the same on days when the 10-year CMT moved 2bp or less.
- The CMT is a bid-side, fixed-maturity, indicative yield. Swap prints are executions. The ledger's spread differs by design from a desk spread against a benchmark bond.
- The file for date D holds what DTCC published on D (UTC). A trade executed on D and published later is not in D's row, and a correction published after D is not applied to it. The first landing reads the file of D only.
- Cross-currency prints sit on a 1/8bp grid, so the IQR is often zero at small n and `iqr_over_sqrt_n_bp` understates. Whether a swap is mark-to-market resetting cannot be told from the tape.
- Day-count code A004 is read as ACT/360 on the strength of a third-party code table and market convention. Spread notation 3 is read as a decimal fraction and 4 as basis points, from magnitudes; the PPD guide defines neither.

## What was left out of the first landing

The lone-package swap-spread series (a second route to the swap spread, with the Treasury leg inferred), the late-file window and `provisional` flag, `--reprobe`, capped-notional and duplicate-key counts, and the notional-weighted median. They are listed in the spec (section 17, A6).

## Running it

```bash
python3 bin/swap_tape_ledger.py selftest                                    # no network; fails if a mutant is not detected
python3 bin/swap_tape_ledger.py fetch-ust --years 2026                      # Treasury CSVs into data/vintages/swap_tape_ust/ (not committed)
python3 bin/swap_tape_ledger.py fetch --start 2026-10-05 --end 2026-10-09   # DTCC zips into ~/dtcc_ppd/ (never inside the repo)
python3 bin/swap_tape_ledger.py build --start 2026-10-05 --end 2026-10-09   # offline; upserts those weekdays' rows
```

The fetcher sends GET only, one request at a time at least 5 seconds apart, with a neutral User-Agent, to `pddata.dtcc.com` and `home.treasury.gov` only. Any HTTP status other than 200, or a body that is not what was asked for, writes `~/dtcc_ppd/STOP` and ends the run; later fetches refuse while that file exists, and only a person deletes it. `build` never touches the network and rewrites only the weekdays it is given. `bash bin/check.sh --all` carries a warn-only guard (M9) that looks for any 8 to 19 digit field or any DTCC file name or zip under this folder.

## Caveats added at landing (supervisor, 14 Oct 2026)

- **`pool1to5` mixes tenors.** The pooled cross-currency median takes every 1–5y trade of the day, so a day dominated by 1y
  trades and a day dominated by 5y trades are not like for like. Read it as a level, not as a change, until the per-tenor cells
  reach n ≥ 10.
- **The CPI gap uses the whole UTC day.** Unlike the swap-spread headline, it is not time-aligned with the Treasury snapshot,
  because CPI swaps trade too thinly inside the 14:30–16:30 New York window (n 0–5 on the dates checked). Treat a day-on-day
  change in it with care when Treasuries moved during the day.
- **Weekend files are not fetched.** A correction or cancellation reported on a Saturday for a Friday trade is therefore not
  applied. On 13 Oct 2026, applying every correction in the file moved the medians by at most 0.06bp.
- **Platform BILT is out of the headline.** On 13 Oct its 10y rows sat 61.7bp below the rest. `all_platforms` shows the effect
  of keeping it.

