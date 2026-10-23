# The 1-5-year cross-currency basis around quarter-ends

*A descriptive table. It carries no verdict and tests nothing.*

Banks and investors swap yen, euros or pounds for dollars. The price of that swap shows how scarce dollars are. This folder asks whether that price, on swaps of one to five years, looked different in the last days before each quarter-end than on the days around it. A swap of that length spans every quarter-end whatever day it is struck. Studies place the quarter-end effect in currency contracts of a week to three months, and this data holds none of those, so a small or absent difference here says nothing against those studies.

These are medians of reported 1-5-year cross-currency swap prices around quarter-ends. A difference at a quarter-end does not show who borrowed dollars, why, or that any flow moved a price.

## Results

**Sign: negative means dollars cost more.** D below zero means the basis was more negative in the window than around it. The ledger is this project's daily table of swap prices, built from DTCC's public price dissemination ([data/swap_tape](../swap_tape/README.md)); the tape is the run of days it covers, here 2024-10-14 to 2026-10-21. A bp is a basis point, one hundredth of a percentage point. An exclusion zone is the span from 21 days before to 7 days after a quarter-end; "Days in zone" counts how many of the ten days before the window, and of the ten after the anchor, fall inside one. Quarter-ends on or before 2026-09-30 were examined before the build. A row says "on_date" when the window ends on the quarter-end, and otherwise names how many days before it the window ended.

| Pair | Quarter-end | Status | Window | Position | D (bp) | Rank among mid-quarter windows | Rank among reference windows | Days in zone, pre / post | Mix |
|---|---|---|---|---|---|---|---|---|---|
| JPYUSD | 2024-12-31 | complete | 2024-12-12 to 2024-12-23 | a window ending 8 days before the quarter-end | -0.740 | 17 of 52 (overlapping windows from 8 stretches; not independent draws) | 2 of 8 (one window per stretch; 8 values) | 0 / 0 | no |
| JPYUSD | 2025-03-31 | complete | 2025-03-25 to 2025-03-31 | on_date | 3.468 | 45 of 52 (overlapping windows from 8 stretches; not independent draws) | 7 of 8 (one window per stretch; 8 values) | 6 / 2 | no |
| JPYUSD | 2025-06-30 | complete | 2025-06-24 to 2025-06-30 | on_date | 0.234 | 21 of 52 (overlapping windows from 8 stretches; not independent draws) | 3 of 8 (one window per stretch; 8 values) | 7 / 2 | no |
| JPYUSD | 2025-09-30 | complete | 2025-09-16 to 2025-09-29 | a window ending 1 day before the quarter-end | 3.375 | 44 of 52 (overlapping windows from 8 stretches; not independent draws) | 7 of 8 (one window per stretch; 8 values) | 0 / 2 | no |
| JPYUSD | 2025-12-31 | complete | 2025-12-17 to 2025-12-23 | a window ending 8 days before the quarter-end | -3.499 | 2 of 52 (overlapping windows from 8 stretches; not independent draws) | 0 of 8 (one window per stretch; 8 values) | 2 / 0 | no |
| JPYUSD | 2026-03-31 | complete | 2026-03-24 to 2026-03-31 | on_date | -4.329 | 2 of 52 (overlapping windows from 8 stretches; not independent draws) | 0 of 8 (one window per stretch; 8 values) | 6 / 0 | no |
| JPYUSD | 2026-06-30 | complete | 2026-06-24 to 2026-06-30 | on_date | 2.172 | 33 of 52 (overlapping windows from 8 stretches; not independent draws) | 5 of 8 (one window per stretch; 8 values) | 8 / 0 | no |
| JPYUSD | 2026-09-30 | incomplete | 2026-09-24 to 2026-09-30 | on_date | - | - | - | - | - |
| EURUSD | 2024-12-31 | gap | 2024-12-13 to 2024-12-19 | a window ending 12 days before the quarter-end | - | - | - | 0 / 1 | - |
| EURUSD | 2025-03-31 | complete | 2025-03-25 to 2025-03-31 | on_date | 0.719 | 56 of 68 (overlapping windows from 8 stretches; not independent draws) | 6 of 8 (one window per stretch; 8 values) | 8 / 2 | no |
| EURUSD | 2025-06-30 | complete | 2025-06-24 to 2025-06-30 | on_date | 0.828 | 56 of 68 (overlapping windows from 8 stretches; not independent draws) | 6 of 8 (one window per stretch; 8 values) | 6 / 2 | no |
| EURUSD | 2025-09-30 | complete | 2025-09-24 to 2025-09-30 | on_date | -0.547 | 16 of 68 (overlapping windows from 8 stretches; not independent draws) | 1 of 8 (one window per stretch; 8 values) | 8 / 2 | no |
| EURUSD | 2025-12-31 | complete | 2025-12-19 to 2025-12-31 | on_date | -0.156 | 24 of 68 (overlapping windows from 8 stretches; not independent draws) | 2 of 8 (one window per stretch; 8 values) | 4 / 1 | no |
| EURUSD | 2026-03-31 | complete | 2026-03-25 to 2026-03-31 | on_date | -2.688 | 0 of 68 (overlapping windows from 8 stretches; not independent draws) | 0 of 8 (one window per stretch; 8 values) | 8 / 0 | no |
| EURUSD | 2026-06-30 | complete | 2026-06-24 to 2026-06-30 | on_date | -0.438 | 20 of 68 (overlapping windows from 8 stretches; not independent draws) | 2 of 8 (one window per stretch; 8 values) | 7 / 0 | no |
| EURUSD | 2026-09-30 | complete | 2026-09-24 to 2026-09-30 | on_date | 0.578 | 53 of 68 (overlapping windows from 8 stretches; not independent draws) | 5 of 8 (one window per stretch; 8 values) | 8 / 2 | no |
| GBPUSD | 2024-12-31 | gap | 2024-12-16 to 2024-12-20 | a window ending 11 days before the quarter-end | - | - | - | 0 / 1 | - |
| GBPUSD | 2025-03-31 | complete | 2025-03-21 to 2025-03-28 | a window ending 3 days before the quarter-end | 0.797 | 17 of 26 (overlapping windows from 5 stretches; not independent draws) | 3 of 5 (one window per stretch; 5 values) | 5 / 1 | no |
| GBPUSD | 2025-06-30 | complete | 2025-06-18 to 2025-06-30 | on_date | 2.406 | 25 of 26 (overlapping windows from 5 stretches; not independent draws) | 5 of 5 (one window per stretch; 5 values) | 0 / 1 | no |
| GBPUSD | 2025-09-30 | complete | 2025-09-23 to 2025-09-30 | on_date | 0.813 | 17 of 26 (overlapping windows from 5 stretches; not independent draws) | 3 of 5 (one window per stretch; 5 values) | 6 / 0 | no |
| GBPUSD | 2025-12-31 | gap | 2025-12-15 to 2025-12-19 | a window ending 12 days before the quarter-end | - | - | - | 0 / 1 | - |
| GBPUSD | 2026-03-31 | complete | 2026-03-25 to 2026-03-31 | on_date | -1.781 | 0 of 26 (overlapping windows from 5 stretches; not independent draws) | 0 of 5 (one window per stretch; 5 values) | 8 / 0 | no |
| GBPUSD | 2026-06-30 | complete | 2026-06-24 to 2026-06-30 | on_date | -0.641 | 0 of 26 (overlapping windows from 5 stretches; not independent draws) | 0 of 5 (one window per stretch; 5 values) | 8 / 0 | no |
| GBPUSD | 2026-09-30 | incomplete | 2026-09-24 to 2026-09-30 | on_date | - | - | - | - | - |

Status: `complete` rows carry D. `incomplete` means too little history, or that the days after the quarter-end have not all posted yet. `gap` means the nearest liquid day was more than 10 days from the quarter-end. `low_n` means fewer trades than the floors (25 in the window, 50 in each control). Only `complete` rows carry a median, D or a rank. Month-ends and the per-tenor differences are in `anchors.csv` and `anchors_tenor.csv`.

## Defined terms

- **Basis.** The ledger's `xccy` series: the spread, in bp, on the yen, euro or sterling overnight-rate leg of a floating-for-floating swap against flat SOFR. Negative is the conventional sign of a dollar premium; some of the literature uses the opposite sign.
- **Window.** The last five liquid days on or before the anchor. A liquid day is a weekday on which the pooled 1-5-year cell has a published median (5 or more trades) and the ledger raises no low-count warning for that pair.
- **D.** The median of the five window medians, minus the mean of two medians: that of the ten liquid days before the window (after a three-day gap) and that of the ten liquid days after the anchor (after a three-day gap).
- **Band, and reference set.** The band is D computed the same way on mid-quarter-month windows, which sit clear of every exclusion zone, one per distinct window. The reference set is one band window per stretch between quarter-ends: the middle one in date order.

## Worked anchor

**JPY 2025-06-30, D = 0.234.** From its row in `anchors.csv`: the median of the five window days is -38.375 bp, the median of the ten days before is -39.5625 bp and the median of the ten days after is -37.656 bp. D = -38.375 - (-39.5625 + -37.656) / 2 = 0.234 bp. The medians are written here exactly; the columns of `anchors.csv` round them to three decimals, and a median of ten can have a fourth, so a hand calculation from the rounded columns can differ from D in the third decimal.

## Limits

- **What the data cannot say.** A difference in these medians, or its rank among the band windows, says nothing about who traded or why. Neither identifies the counterparties or the reason. A difference at a quarter-end is a difference between reported prices, nothing more. Nothing here covers short-dated FX swaps or repo, where the dollar-funding literature places quarter-end pressure; the tape holds no contract of a week to three months that can be read daily.
- **The band is short and clustered.** It comes only from mid-quarter-month windows, in 8 (JPYUSD), 8 (EURUSD), 5 (GBPUSD), so a rank against it is not a draw from a known distribution. Its lower tail rests on few episodes: JPYUSD: the three lowest band values come from 2026-Q1, and leaving out one stretch at a time moves P5 between -3.470 and -2.789 bp; EURUSD: the three lowest band values come from 2025-Q1, and leaving out one stretch at a time moves P5 between -1.406 and -0.938 bp; GBPUSD: the three lowest band values come from 2025-Q1 and 2025-Q4 and 2026-Q3, and leaving out one stretch at a time moves P5 between -0.110 and 0.078 bp.
- **A row describes its window, not necessarily the quarter-end.** Year-end windows can end earlier: over the holidays most days were not liquid (fewer than 5 trades, or the ledger's low-count warning). On this tape: JPYUSD 2024-12-31 (a window ending 8 days before the quarter-end); JPYUSD 2025-12-31 (a window ending 8 days before the quarter-end); EURUSD 2024-12-31 (a window ending 12 days before the quarter-end); GBPUSD 2024-12-31 (a window ending 11 days before the quarter-end); GBPUSD 2025-12-31 (a window ending 12 days before the quarter-end).
- **Spike or plateau.** Across the 19 complete quarter-ends in the table, between 0 and 8 of the ten days before the window lie inside an exclusion zone (0 to 8 where the window ends on the quarter-end). A level shift spread over the whole zone shows in D at about half its size; a move confined to the five window days shows whole. `pre_in_zone_days` and `post_in_zone_days` are printed so that a reader can tell which case a row is closer to.
- **Tenor mix.** The pooled series mixes tenors, and the mean tenor differs by day. A row above the mix limit says "tenor mix shifted; not read as a basis move".
- **Not general.** The ledger covers US-reported OIS-versus-SOFR basis swaps only. Whether a swap resets its notional is not visible, and trades reported only outside the US are not in it. The ranks are descriptive and are not tests.

## Column dictionary

**`anchors.csv`**

| Column | Meaning |
|---|---|
| `pair` | JPYUSD, EURUSD or GBPUSD; the non-dollar leg is named first. |
| `anchor_date` | The anchor weekday: the last weekday on or before a quarter-end or month-end, or a placebo weekday that is in the band. |
| `anchor_type` | quarter_end, month_end or placebo. A placebo row is written only when its window is in the band. |
| `in_sample` | yes when the date is on or before 2026-09-30, a period examined before the build. |
| `in_band` | yes for a mid-quarter window that is in the band. |
| `in_ref` | yes for the band window picked as the reference window of its stretch. |
| `status` | complete, incomplete (too little history, or the days after the anchor have not all posted), gap (the nearest liquid day was more than 10 days away) or low_n (fewer trades than the floors: 25 in the window, 50 in each control). |
| `window_first, window_last` | First and last of the five window days. |
| `gap_days` | Calendar days from the last liquid day on or before the anchor to the anchor. |
| `on_date` | yes when gap_days is 0. |
| `weekdays_window_span` | Weekdays from window_first to window_last inclusive. |
| `post_first` | The first liquid day after the anchor. |
| `pre_in_zone_days, post_in_zone_days` | How many of the ten pre-control days, and of the ten post-control days, fall in an exclusion zone. |
| `n_window, n_pre, n_post` | Trades summed over the pooled cells of the window days, the ten pre-control days and the ten post-control days. |
| `med_window_bp, med_pre_bp, med_post_bp` | Medians of the daily pooled medians over the window, the pre-control and the post-control days. |
| `d_bp` | D in bp: med_window_bp minus the mean of med_pre_bp and med_post_bp. |
| `band_role` | Which band the ranks use: provisional, or of_record once the tape covers 2026-11-27. |
| `rank_band, k_band` | How many band values are at or below D, of k_band band windows. Quarter-end and month-end rows only. Read it with its caveat: overlapping windows from N stretches; not independent draws (N is `stretches` in band.csv, and is different for each pair). |
| `rank_ref, k_ref` | The same against the reference windows. Read it with its caveat: one window per stretch; N values (N is `k_ref` in band.csv). |
| `mean_tenor_window_y, mean_tenor_ctrl_y, d_mean_tenor_y` | Trade-weighted mean tenor in years of the window days, of the 20 control days, and the difference. |
| `mix_limit_y, mix_flag` | The 95th percentile of the absolute tenor difference over the band, and yes when this row is above it. |

**`anchors_tenor.csv`**

| Column | Meaning |
|---|---|
| `pair, anchor_date, anchor_type` | As in anchors.csv. Rows are written for quarter-end, month-end and reference anchors. |
| `tenor_y` | The tenor, 1 to 5 years. |
| `days_window, days_pre, days_post` | Days among the anchor's own window and control days on which this tenor's own median is published (at least 10 trades). |
| `med_window_bp, med_pre_bp, med_post_bp, d_bp` | As in anchors.csv, on those days only. |
| `status` | complete (at least 2 window days and 3 days in each control), too_few_days, or anchor_not_complete. |

**`band.csv`**

| Column | Meaning |
|---|---|
| `pair, band_role, asof, tape_last_date` | The band's role, the date it is cut at, and the last date on the tape. |
| `k_anchors, stretches` | Band windows and the quarters they come from. |
| `p5_bp to p95_bp, sd_bp` | Nearest-rank percentiles and the population standard deviation of the band's D values. |
| `p5_leave_one_stretch_out_min_bp, p5_leave_one_stretch_out_max_bp` | The 5th percentile recomputed with each stretch left out in turn: lowest and highest. |
| `k_ref, ref_min_bp, ref_median_bp, ref_max_bp` | The reference set: one window per stretch. |
| `mix_limit_y` | The tenor-mix limit. |
| `inputs_sha256` | sha256 of one line per covered weekday up to asof: the ledger's pooled and tenor counts and the pooled median, verbatim. |

**`questions.csv`**

| Column | Meaning |
|---|---|
| `question, pair, anchor_type, anchor_date` | Q1 each quarter-end; Q2 quarter-end statistics; Q3 month-end statistics; Q4 thin trading; Q5 tenor mix and tenors; Q6 short-tenor availability. |
| `statistic, value, unit, denominator` | What is reported, its value, its unit, and what it is out of. |
| `note` | The required sentence, and the caveat that goes with each rank. |

**`short_tenor_availability.csv`**

| Column | Meaning |
|---|---|
| `series, tenor` | The ledger's monthly 3-month and 1-year cells. |
| `first_month, last_month, months, months_published` | Months on the file, and months whose median is published. |
| `n_total, n_month_median, days_with_trades_month_median` | Trades in all months, median trades a month, median days with trades a month. |

**`inputs.csv`**

| Column | Meaning |
|---|---|
| `file, sha256, rows, first_date, last_date` | Each ledger file read, its hash, its data rows and its first and last date or month. |

**`checks.csv`**

| Column | Meaning |
|---|---|
| `check_id, description, expected, observed, status` | The pinned checks of the spec. Status is PASS, WARN, FAIL or INFO. |

**`columns.tsv`**

| Column | Meaning |
|---|---|
| `file, columns` | The header of every file, columns joined by a vertical bar. |

## Provenance

Derived from DTCC Public Price Dissemination, CFTC cumulative rates reports (pddata.dtcc.com), through the project's swap-tape ledger in [data/swap_tape](../swap_tape/README.md). Only statistics are published, under the ledger's count floor, as ruled in THE_ASK.md (E-024) for non-commercial research; the CC BY 4.0 licence of this repository covers this project's computation only. Inputs: the ledger's derived files, whose sha256 and date ranges are in `inputs.csv` (the specification read the ledger as committed at b22f51a). The script is [bin/quarter_end_basis.py](../../bin/quarter_end_basis.py); the specification is [_research/2026-10-23-Quarter-End-Basis-Spec.md](../../_research/2026-10-23-Quarter-End-Basis-Spec.md) and is the authority. Choices the specification left open are listed in [SOURCES.md](SOURCES.md).
