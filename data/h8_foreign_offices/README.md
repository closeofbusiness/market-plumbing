# Net due to related foreign offices, weekly: the Federal Reserve's H.8 release ("Assets and Liabilities of Commercial Banks in the United States")

This table shows, at each Wednesday close, the net amount that US branches and agencies of foreign banks, with Edge Act and agreement corporations, owe to their own offices abroad and to related institutions in the US, from the Federal Reserve's H.8 release. The figure nets those positions and includes unremitted profits, capital and reserve accounts and, from April 2022, allowances for credit losses.

It records balances at Wednesday closes only; it does not show why they changed, and a change in a balance is not a measure of money moved.

**Terms.** H.8 is the Federal Reserve Board's weekly statistical release on the balance sheets of commercial banks in the United States. Edge Act and agreement corporations are US subsidiaries chartered to do international banking. An IBF is an international banking facility; the H.8 treats IBFs as foreign offices. NSA means not seasonally adjusted: the raw weekly level, without the correction for regular seasonal patterns. The weekly figures are estimates. The Fed benchmarks them, that is re-bases them, to Call Reports, the quarterly balance-sheet reports that banks file with US regulators, and re-estimates them when new Call Report data arrive. In the tables, `usd_mn` is millions of US dollars, `FRI` is the foreign-related institutions of the opening sentence (US branches and agencies of foreign banks with Edge Act and agreement corporations), `DOM` is domestically chartered commercial banks and `ALL` is all commercial banks in the United States. A vintage is the data as published on one release date; the Board overwrites its files at each release, so each vintage is kept in a local git-ignored cache when it is fetched.

## The sign, and the trap

Positive means the US offices owe their related foreign offices, net. Negative means they are owed, net. **The line for domestically chartered banks is negative (-483.6 $bn on 2026-10-07, vintage 2026-10-23) and is not the foreign banks' line.** Read the `FRI` rows for the foreign banks. The foreign-related line was itself negative on 755 weeks of its history from 1973-01-03, the last on 2011-06-15, so the sign alone does not tell a reader which group a number belongs to. The groups are told apart by the series group code (which the script asserts on every series) and by domestic line 40 being larger than foreign-related line 40 on every week; the accounting identity below holds for both groups and does not tell them apart.

The Board's footnote 24 says: "Excludes the due-from position with related foreign offices which is included in line 38." The line is the balance-sheet residual of the liabilities side: line 38 = line 40 (total liabilities) - (line 34 deposits + line 37 borrowings + line 39 other liabilities). Worked example, foreign-related institutions, NSA, 2026-10-07 (vintage 2026-10-23, usd_mn): 3,642,173 - (1,612,007 + 981,596 + 211,710) = 836,860. Domestically chartered banks on the same date: 19,900,845 - (18,130,824 + 1,374,789 + 878,790) = -483,558.

## What the line contains

On the reporting form FR 2644 (item 9.a, page LI-7 of the April 2024 instructions) a branch or agency reports one net position against its own foreign offices, its Edge and agreement subsidiaries, its IBFs, its own head office and other related depository institutions in the US. The instructions say the position should include "unremitted profits, any statutory or regulatory capital requirement, any reserve accounts, and any allowance for credit losses". A net due-from position is reported as an asset (item 5.a), and the H.8 carries it into line 38 as a negative. **Line 38 is therefore not pure lending between offices.** From 6 April 2022 the allowance for credit losses of foreign-related institutions is inside the line (release footnote 20); its size is not published. These weekly changes are not flows of funds, and the table does not test window dressing or any other motive.

## Breaks

The paths are split at every published break: 6 April 2022 (allowances moved into the line) and each week of the Board's Notes on Data that names the line. Break weeks since 2004-06-02, FRI: 2008-02-06, 2008-04-02, 2010-03-31, 2017-11-29, 2019-10-02, 2022-04-06. DOM: 2004-12-29, 2006-10-04, 2007-03-07, 2008-08-20, 2011-01-05, 2016-03-02, 2018-04-04. ALL takes the union of both. `segment_start` in `weekly.csv` is the first week of each row's segment; the change that ends on a break week is left blank and `note_flag` marks the week. No change, minimum or maximum is taken across a break. `notes.csv` lists the stated amounts (signed, usd_mn), group by group.

## Endpoints of the multi-year changes

Multi-year changes run between named ordinary Wednesdays: the Wednesday between the 8th and the 14th of February or August, each at least 39 days from any quarter-end day. The endpoints are 2024-02-14, 2025-02-12, 2026-02-11, 2026-08-12. The reason: the weeks around quarter-ends swing, so an endpoint on such a week would put a quarter-end move into a multi-year change. `Lo`, the latest Wednesday at least 7 days from every quarter-end day and not a break week, is 2026-10-14; it is printed in `summary.csv` and never used as an endpoint.

## Quarter-ends

Only quarter-end days that are themselves Wednesdays count as observations; since 2019 there are five. Each is one row, in usd_mn: the level at that Wednesday close, the change ending that Wednesday and the change ending the next Wednesday. No average, count or test is taken across them.

| quarter | quarter-end day | FRI level | FRI change into | FRI change out of | DOM level | DOM change into | DOM change out of |
|---|---|---:|---:|---:|---:|---:|---:|
| 2020Q3 | 2020-09-30 | 178,366.0 | 3,149.0 | -13,628.0 | -182,639.0 | -9,995.0 | 4,981.0 |
| 2021Q1 | 2021-03-31 | 145,720.0 | 33,566.0 | -20,422.0 | -328,851.0 | -66,516.0 | 34,170.0 |
| 2021Q2 | 2021-06-30 | 162,131.0 | -31,818.0 | 16,178.0 | -301,253.0 | -60,621.0 | -23,707.0 |
| 2025Q4 | 2025-12-31 | 869,545.0 | 24,169.0 | -36,596.0 | -387,307.0 | 20,389.0 | -40,117.0 |
| 2026Q3 | 2026-09-30 | 855,694.0 | -22,212.0 | -18,834.0 | -502,585.0 | 25,170.0 | 19,027.0 |

Wednesday levels cannot show a position that is not held at a Wednesday close. When the quarter-end day falls before the Wednesday (a negative offset in `quarter_ends.csv`), the day sits in the change that ends one week after that Wednesday, so the table below gives both changes and marks which one contains the quarter-end day. Two quarters, 2019Q3 and 2022Q1, have a change that ends on a break week.

The other frozen-set quarters (2019Q1 to 2026Q3), usd_mn: the change that contains the quarter-end day, the other change beside it, and whether either ends on a break week.

| quarter | quarter-end day | Wednesday | offset | FRI containing | FRI other | FRI break | DOM containing | DOM other | DOM break |
|---|---|---|---:|---:|---:|---|---:|---:|---|
| 2019Q1 | 2019-03-31 | 2019-04-03 | 3 | -32,928.0 | -32,701.0 | no | -10,971.0 | 13,630.0 | no |
| 2019Q2 | 2019-06-30 | 2019-07-03 | 3 | -13,773.0 | 53,597.0 | no | -64,933.0 | 10,102.0 | no |
| 2019Q3 | 2019-09-30 | 2019-10-02 | 2 |  | -8,878.0 | yes | -17,936.0 | 37,631.0 | no |
| 2019Q4 | 2019-12-31 | 2020-01-01 | 1 | 26,821.0 | -11,322.0 | no | -33,413.0 | 15,985.0 | no |
| 2020Q1 | 2020-03-31 | 2020-04-01 | 1 | 161,004.0 | -27,609.0 | no | 108,849.0 | 56,504.0 | no |
| 2020Q2 | 2020-06-30 | 2020-07-01 | 1 | 4,876.0 | -43,640.0 | no | -21,833.0 | 21,726.0 | no |
| 2020Q4 | 2020-12-31 | 2020-12-30 | -1 | -13,097.0 | 31,539.0 | no | -57,560.0 | -29,239.0 | no |
| 2021Q3 | 2021-09-30 | 2021-09-29 | -1 | -18,802.0 | 14,698.0 | no | 31,406.0 | -62,376.0 | no |
| 2021Q4 | 2021-12-31 | 2021-12-29 | -2 | 48,291.0 | -49,708.0 | no | -62,013.0 | 3,766.0 | no |
| 2022Q1 | 2022-03-31 | 2022-03-30 | -1 |  | 19,247.0 | yes | -6,017.0 | -37,530.0 | no |
| 2022Q2 | 2022-06-30 | 2022-06-29 | -1 | 88,596.0 | 12,847.0 | no | -4,781.0 | -3,500.0 | no |
| 2022Q3 | 2022-09-30 | 2022-09-28 | -2 | 80,505.0 | 18,966.0 | no | 14,187.0 | -10,490.0 | no |
| 2022Q4 | 2022-12-31 | 2022-12-28 | -3 | 27,191.0 | -42,383.0 | no | -39,315.0 | -333.0 | no |
| 2023Q1 | 2023-03-31 | 2023-03-29 | -2 | -57,982.0 | 52,552.0 | no | -8,060.0 | -18,203.0 | no |
| 2023Q2 | 2023-06-30 | 2023-06-28 | -2 | -38,585.0 | 54,989.0 | no | 2,156.0 | -26,068.0 | no |
| 2023Q3 | 2023-09-30 | 2023-09-27 | -3 | -40,743.0 | -23,737.0 | no | -7,208.0 | 9,615.0 | no |
| 2023Q4 | 2023-12-31 | 2024-01-03 | 3 | -6,510.0 | 17,424.0 | no | -15,988.0 | -35,014.0 | no |
| 2024Q1 | 2024-03-31 | 2024-04-03 | 3 | -51,457.0 | -15,685.0 | no | -15,931.0 | 14,444.0 | no |
| 2024Q2 | 2024-06-30 | 2024-07-03 | 3 | 11,180.0 | 20,879.0 | no | -20,382.0 | 3,023.0 | no |
| 2024Q3 | 2024-09-30 | 2024-10-02 | 2 | -15,395.0 | -9,566.0 | no | -36,341.0 | 22,966.0 | no |
| 2024Q4 | 2024-12-31 | 2025-01-01 | 1 | 23,827.0 | 85,274.0 | no | -1,464.0 | -42,023.0 | no |
| 2025Q1 | 2025-03-31 | 2025-04-02 | 2 | -61,797.0 | 61,436.0 | no | 28,314.0 | 71.0 | no |
| 2025Q2 | 2025-06-30 | 2025-07-02 | 2 | -121,760.0 | 75,975.0 | no | -3,365.0 | -12,685.0 | no |
| 2025Q3 | 2025-09-30 | 2025-10-01 | 1 | -43,294.0 | 14,602.0 | no | 537.0 | 35,672.0 | no |
| 2026Q1 | 2026-03-31 | 2026-04-01 | 1 | -27,820.0 | 40,540.0 | no | -8,069.0 | 4,772.0 | no |
| 2026Q2 | 2026-06-30 | 2026-07-01 | 1 | 893.0 | 10,076.0 | no | -13,878.0 | 38,100.0 | no |

A blank cell is a change that ends on a break week: it spans the break (2 October 2019 for 2019Q3, 6 April 2022 for 2022Q1), so no change is shown; the `break` column says yes for that quarter.

## Latest levels

Latest week 2026-10-14, vintage 2026-10-23 (usd_mn; the share is line 38 as a percentage of the same group's line 40, total liabilities, on the same Wednesday).

| group | line 38 | line 40 | share of line 40 (%) |
|---|---:|---:|---:|
| FRI | 827,769.0 | 3,646,607.0 | 22.70 |
| DOM | -469,256.0 | 20,004,547.0 | -2.35 |
| ALL | 358,513.0 | 23,651,154.0 | 1.52 |

Changes between the named Wednesdays (usd_mn; the share is the change as a percentage of the group's line 40 on the starting Wednesday):

| group | window | start | end | change | share of start line 40 (%) | minimum to maximum inside the window |
|---|---|---:|---:|---:|---:|---|
| FRI | 2024-02-14 to 2025-02-12 | 704,646.0 | 849,074.0 | 144,428.0 | 4.43 | 597,393.0 (2024-05-01) to 870,138.0 (2025-02-05) |
| FRI | 2025-02-12 to 2026-02-11 | 849,074.0 | 809,580.0 | -39,494.0 | -1.20 | 736,353.0 (2025-10-29) to 1,007,566.0 (2025-07-23) |
| FRI | 2026-02-11 to 2026-08-12 | 809,580.0 | 798,035.0 | -11,545.0 | -0.34 | 798,035.0 (2026-08-12) to 924,371.0 (2026-04-08) |
| DOM | 2024-02-14 to 2025-02-12 | -360,685.0 | -400,102.0 | -39,417.0 | -0.22 | -445,311.0 (2024-10-02) to -341,174.0 (2024-12-25) |
| DOM | 2025-02-12 to 2026-02-11 | -400,102.0 | -417,299.0 | -17,197.0 | -0.10 | -442,060.0 (2025-03-26) to -331,894.0 (2025-11-19) |
| DOM | 2026-02-11 to 2026-08-12 | -417,299.0 | -466,102.0 | -48,803.0 | -0.26 | -507,294.0 (2026-07-01) to -386,424.0 (2026-02-18) |
| ALL | 2024-02-14 to 2025-02-12 | 343,961.0 | 448,972.0 | 105,011.0 | 0.50 | 198,414.0 (2024-05-01) to 468,465.0 (2025-02-05) |
| ALL | 2025-02-12 to 2026-02-11 | 448,972.0 | 392,281.0 | -56,691.0 | -0.27 | 371,890.0 (2025-10-01) to 626,138.0 (2025-07-23) |
| ALL | 2026-02-11 to 2026-08-12 | 392,281.0 | 331,933.0 | -60,348.0 | -0.27 | 318,986.0 (2026-07-01) to 472,820.0 (2026-04-29) |

## Seasonal adjustment, revisions and vintages

Every table here uses the not seasonally adjusted weekly level (NSA), because seasonal adjustment would remove part of any pattern around quarter-ends, and because the Board's About page says the seasonally adjusted foreign-related data are "derived as residuals" from other groups. The seasonally adjusted foreign-related line (857,297.1 usd_mn on 2026-10-14, against 827,769.0 NSA) is in `weekly.csv` as context so that a reader can match Table 10 of the release; no figure in `summary.csv` or `quarter_ends.csv` is taken from it.

The weekly figures use weights carried forward from the latest Call Reports. When new Call Report data arrive the weights are updated, which the Fed calls benchmarking, and the change is interpolated over the previous quarter; seasonal factors are updated once a year and affect only the seasonally adjusted series. For example, a project note records $834.4 bn for the week of 5 Aug 2026 from the 14 Aug 2026 release (taken from that note, not re-read at the source); vintage 2026-10-16 has 839,732 usd_mn, and vintage 2026-10-23 has 839,732. Each fetch saves the 20-series subset of its vintage in a git-ignored cache, and `revisions.csv` is regenerated on every build from all adjacent pairs of cached subsets (vintages so far: 2026-10-16, 2026-10-23; `vintages.csv` lists them with the zip hash). The release XML file is the primary source. If it cannot be fetched, the build can run from the Board's Data Download Program (DDP) packages instead, the route is then `ddp_fallback`, and the vintage is keyed by the fetch date.

## Column dictionary

| file | columns |
|---|---|
| weekly.csv | `week_wed` Wednesday; `group` FRI, DOM or ALL; `sa` NSA or SA (SA only for FRI); `series_id` H.8 identifier; `usd_mn` line 38; `change_usd_mn` level minus the previous Wednesday's level, blank on a break week; `total_liabilities_usd_mn` line 40; `pct_of_total_liabilities` 100 x line 38 / line 40; `qe_quarter`, `qe_role` (`qe` on the Wednesday nearest the quarter-end day, `after_qe` one week later, else `none`) and `qe_offset_days` (Wednesday minus quarter-end day); `segment_start` first week of the segment; `note_flag` `note`, `footnote` or both on a break week; `vintage`. |
| quarter_ends.csv | `quarter`, `qe_date` quarter-end day, `qe_wed` Wednesday nearest it, `offset_days`, `on_date` yes when the quarter-end day is the Wednesday; `group` FRI or DOM (NSA); `level_qe_wed_usd_mn`; `delta_qe_wed_usd_mn` change ending that Wednesday; `delta_next_usd_mn` change ending the next one; `qe_day_in_window` yes when the quarter-end day falls in the first of the two changes; `straddles_break` yes when either change ends on that group's break week, and that change is then left blank; `frozen_set` yes for the 31 quarters 2019Q1 to 2026Q3; `blind` yes when the spec author had not seen the values; `vintage`. |
| notes.csv | `note_week`, `group`, `line38_effect_usd_mn` the Board's stated amount, `kind` note or footnote, `paragraph_index` (0 is the first paragraph of the entry), `text_head` the item clause that carries the amount. |
| revisions.csv | Cells whose value differs between two adjacent cached vintages: `vintage_prev`, `vintage_new`, `series_id`, `week_wed`, the two values and the change, all usd_mn. |
| vintages.csv | One row per cached vintage: `route` xml or ddp_fallback; the XML `Prepared` timestamp, `Last-Modified` time and zip sha256; `ddp_status` ok, ddp_partial or ddp_unavailable; `latest_week`; `rows_fri_nsa`. |
| summary.csv | `question` is the block label (Q1 paths by segment, Q2 changes between the named Wednesdays and `Lo`, Q3 the five Wednesday quarter-ends, Q4 the FRI and DOM changes side by side with the ALL = DOM + FRI gap, Q6 revisions); `window`, `group`, `statistic`, `value`, `unit`, and `blind` (yes when the values had not been seen when the build was specified). |
| checks.csv | `check_id`, `description`, `expected`, `observed`, `status` PASS, WARN, FAIL or N/A. |
| fetch_log.csv | One row per request the script made: time, host, path, status, bytes, sha256. |

## Provenance

Source: Board of Governors of the Federal Reserve System, "Assets and Liabilities of Commercial Banks in the United States - H.8" (https://www.federalreserve.gov/releases/h8/), release of 2026-10-23 (vintage 2026-10-23). The Board's website policy says: "Unless otherwise indicated, information on Board's website is in the public domain and may be copied and distributed without permission. Please cite to the Board as the source of the information." The Board has announced that its Data Download Program is being retired, with the "Build Your Package" feature to be removed in the week of 9 November 2026; the XML files on the release pages remain. Method, sources and the choices made in building this folder are in [SOURCES.md](SOURCES.md).
