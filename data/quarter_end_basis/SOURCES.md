# Sources, terms and build decisions

## Source and terms

Derived from DTCC Public Price Dissemination, CFTC cumulative rates reports (pddata.dtcc.com), through the project's swap-tape ledger (`data/swap_tape/`; its specification is `_research/2026-10-14-Swap-Tape-Ledger-Spec.md`). Use is non-commercial research, ruled in THE_ASK.md as E-024: statistics only, nothing raw committed, no per-trade value, no file name, row or identifier. A pooled daily median enters only where the ledger published it (5 or more trades) and a tenor median only where it published one (10 or more). The CC BY 4.0 licence covers this project's computation only. This build downloads nothing and reads nothing outside the repository.

## Ledger files read

The specification read the ledger as committed at b22f51a (cells to 2026-10-21). The files read in this build, with their sha256 and ranges, are in `inputs.csv`. The closed-year files are pinned in `checks.csv` (C01): `cells_2024.csv` 8a93cb1c7dfc542c2f15454550c25989fd0c0d0ded85b9f4b6692b3952584bd2 and `cells_2025.csv` fef068669d757fff0ae26611f662de9864a6b6f54dd687d697192b2e06a7a11b.

## BIS CGFS Papers No 65 (June 2020)

https://www.bis.org/publications/cgfs-paper-65-us-dollar-funding-international-perspective.pdf, sha256 `0a1d5ce92b9fec5756c729c449e01e9df5ab5db7f90111ef8119d7e3c5a2c504` (3,704,415 bytes, observed 23 Oct 2026). "Brief excerpts may be reproduced or translated provided the source is stated" (CGFS 65, p ii). The quarter-end passages are on printed pages 28, 35, 44 and 73. CGFS 65 p 35: "US repo rates may spike and spill over to short-dated FX swaps". The paper sizes no quarter-end move in 1-5-year basis swaps.

## Papers relayed, not re-read

Relayed by the round-3 attack and marked as such: Du, Tepper and Verdelhan, NBER WP 23170 (one-week contracts, 30 to 40 bp); Georgievska, Karner and Syrstad 2026, preliminary (4 to 5 bp at three months, "very small" at five years). Neither was read for this build.

## Prior work

`_research/2026-10-15-ST1-Swap-Spreads-Inflation-Gap-And-Basis.md` examined basis levels from the same ledger. This build adds the quarter-end comparison and does not revise those levels.

## Leg convention and corrections

CFTC orders the two floating legs alphabetically by underlier, and the JPY, EUR and GBP legs all sort before USD, so the ledger's foreign-leg-first reading holds for these pairs. No side (payer or receiver) is disseminated: each daily value is a median of traded spreads, not a mid. Package share and correction handling are as the ledger specification defines; this build adds no filtering of its own.

## In-sample values

The in-sample differences of check C13 (JPY and EUR, seven quarter-ends each) were computed by the second reviewer on the committed tape before the build. The spec author re-derived all fourteen exactly, and this build recomputes and pins them. Round 3 of the supervisor's rulings re-scoped the build to a descriptive table.

## Build decisions

1. Inputs. Only `cells_YYYY.csv`, `diagnostics_YYYY.csv` and `monthly_short_tenor.csv` are opened. The ledger's `date_status` rows live in `ledger_YYYY.csv` and are not read: a weekday absent from the cells inside the covered range is covered but not liquid (2.3). `tape_last_date` is the largest date in the cells files, whatever the series, and the first date likewise; every weekday between them is covered. Nothing reads a wall clock except the staleness line printed to stdout.
2. Liquid days. A weekday is liquid for a pair when its pooled cell has status ok or thin, a non-blank median, and no `warn_f0_low_<series>` row for that date. A blank median is never read as zero.
3. Anchors. Quarter-end anchors are the last weekday on or before each calendar quarter-end from 2024-12-31 whose anchor date is on or before `tape_last_date`. Month-end anchors are the last weekday of January, February, April, May, July, August, October and November that fall on the tape (the first, 2024-10-31, is `incomplete`). A placebo is any other covered weekday and is written only when it is in the band.
4. `in_sample`. yes for every anchor dated on or before 2026-09-30, of any type, since the band was also examined before the build; no after.
5. Window geometry. j is the index of the last liquid day on or before the anchor and k = j + 1. `post_first` is L[k]. Window fields (dates, gap_days, on_date, span, counts) are printed whenever the days exist, including on `incomplete`, `gap` and `low_n` rows, so a reader can see why a row is not complete; medians, D, ranks and mean tenors are printed only on `complete` rows.
6. Zones and the band. Exclusion zones are [q - 21 days, q + 7 days] for the calendar quarter-ends 2024-09-30 to 2027-12-31. A stretch is the calendar quarter that holds the anchor date. Percentiles are nearest rank, rank ceil(q x k), with q an exact fraction. The reference pick is the band anchor at position ceil(m/2), counted from 1 in date order, in each stretch. The reference median is the usual median (the mean of the two middle values when the count is even). The standard deviation is the population one, computed on exact fractions and square-rooted at 60 digits.
7. Band roles. While the tape ends before 2026-11-27 each pair has one `provisional` row (asof = `tape_last_date`). From 2026-11-27 each pair has an `of_record` row, copied unchanged from the committed `band.csv` when it holds one and computed otherwise, and a `recomputed` row cut at the same asof (2026-11-27) from the current files, so that a difference can only come from a revised input. Both rows are written on every build from then on, which keeps a rebuild byte-identical. Ranks use the values recomputed at asof 2026-11-27; the counts at or below band P5 in Q2 and Q3 use the same values.
8. Mix. The limit is the 95th percentile (nearest rank) of the absolute tenor difference over the band windows. A row is flagged when its absolute difference is above the limit (strictly). Mean tenor weights each tenor by the ledger's per-tenor trade counts, which are always published.
9. Per-tenor D. Rows are written for quarter-end, month-end and reference anchors on the anchor's own window and control days, using days where that tenor's own median is published. `complete` needs at least 2 window days and 3 days in each control.
10. Questions. Q4 uses anchors for which a window exists; `warn_f0_low` days are counted among the 10 calendar days ending on the anchor. Q2 and Q3 print no standard error or test statistic. By a supervisor ruling (round 5) the dependence caveat names each pair's own count instead of the specification's "about eight": "overlapping windows from N stretches; not independent draws" (N = 8, 8, 5 for JPY, EUR, GBP) and "one window per stretch; N values"; the same ruling writes "1 day" for the singular in "a window ending N days before the quarter-end".
11. Rounding. Ledger medians are Decimals parsed from their strings; D, ranks and comparisons are exact; text is rounded half away from zero at 3 decimals. A value that rounds to -0.000 is printed 0.000.
12. Allowlist (round 4, O-4). `post_in_zone_days` was added to `anchors.csv` after `pre_in_zone_days`. The canonical allowlist text is now 1,096 bytes and its sha256 is `3f54fbeb17c65e257af8acd41c1f2b0b2398b432ca18b3bed4f60c1c5e2445e4` (it was 1,078 bytes, `479678adef66bcd7aa9ca5e3f90a89d7b0e1ffebc90d6e97921dd8f76f0c2ed6`). The spec's block and its printed hash were updated to match before the build, and the hash is held in the script and in `bin/check.sh`.
13. Pinned checks. C05-C08 and C13-C15 are evaluated on the tape truncated at 2026-10-21 and on monthly rows to 2026-09. Only C01, C07 and C09 can WARN on a difference; any other mismatch is FAIL. C03b fails if the median of the JPY liquid-day medians is not negative or is not the pinned value. C10 is a second in-process render with the first render's `band.csv` standing in for the committed one. C09 reads `CALENDAR.tsv` and C12 is stdout only.
14. Fixes made after the first build, which showed two pinned checks failing on formatting alone: the median of a count (check C08) was written 14.500 and is now written 14.5 (a count median prints without trailing zeros), and the complete per-tenor cells of check C15a were listed in alphabetical order of pair and are now listed in the order JPYUSD, EURUSD, GBPUSD, then by date and tenor. No computed value changed.
15. Round 5 fixes (verifier): the year-end sentence of the README now gives the observed reason (most holiday days were not liquid); the README defines the tape, the ledger, bp and the exclusion zone at first use and states the observed range of pre-control days in a zone; `post_in_zone_days` is pinned in C14post (JPY 0, 2, 2, 2, 0, 0, 0; EUR 2, 2, 2, 1, 0, 0, 2, in quarter-end order); the selftest replaces the wall clock globally for the rebuild test and has guards for the counts at or below band P5, the sample-or-population standard deviation, the in-sample end date, the 10-day warn window, the per-tenor control minimum and the README text at a gap of 1 day.
16. The values of C13 were computed by the second reviewer on the committed tape before the build and re-derived by the spec author; this build recomputes them and pins them. The specification's other values (3.8 table, C06, C14, C15) are pinned in the same way.
