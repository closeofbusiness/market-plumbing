# Spec: the 1-5-year cross-currency basis around quarter-ends, a descriptive table (X4; spec author, 23 Oct 2026; rewritten after rounds 2 and 3)

*Candidate X4 of `_research/2026-10-19-CGFS65-Dollar-Funding-Reading.md`; FX dossier `dossiers/cross-border-and-fx.md`. House style follows
`_research/2026-10-19-JP-Life-Insurers-Foreign-Bonds-Spec.md` and `_research/2026-10-19-Japan-Term-Premium-Spec.md`. The input is the
project's own swap-tape ledger (`data/swap_tape/`, spec `_research/2026-10-14-Swap-Tape-Ledger-Spec.md`), read as committed at `b22f51a`
(cells to 2026-10-21). This build downloads nothing. Committed path of this spec: `_research/2026-10-23-Quarter-End-Basis-Spec.md`.*

*This text applies the supervisor's rulings of rounds 1, 2 and 3, which stay at the end as the record; the body is authoritative. **Round 3
re-scoped the build to a descriptive table: there is no registered test and no verdict at any anchor.** What was seen on real data before
the build: the spec author saw the tape inventory, daily counts and window dates, three sign/unit cells and the placebo band to 21 Oct
2026; the second reviewer then computed the in-sample differences (JPY and EUR, seven quarter-ends each), pinned below as C13; the spec
author re-derived all fourteen exactly in this rewrite, and also the reference set and per-tenor day counts of C14-C15. ST1
(`2026-10-15-ST1-...md`) had already examined basis levels. "Observed" means one request per URL on 23 Oct 2026 with the CLAUDE.md
non-SEC User-Agent (two requests, both HTTP 200); none was made for this rewrite.*

## 0. Goal, and what the result can and cannot say

- **Describe**, for every quarter-end on the tape and for JPY/USD, EUR/USD and GBP/USD, the difference D between the median 1-5-year
  cross-currency basis printed in the last five liquid days before the quarter-end and the median on matched days before and after it.
- **Place** each D beside two references: an overlapping band of mid-quarter windows (context only) and a non-overlapping reference set
  of one window per stretch between quarter-ends. Print a per-tenor D wherever a tenor's own medians are published.
- **Add** each new quarter-end when its days post (31 Dec 2026 first; CALENDAR row proposed for 2027-01-29). Nothing is scored.

**Why descriptive (round 3).** A 1-5-year swap spans every quarter-end whatever day it is struck. The published quarter-end effect sits in
short contracts that span the reporting date (Du, Tepper and Verdelhan, NBER WP 23170: one-week contracts, 30-40bp; Georgievska, Karner and
Syrstad 2026, preliminary: 4-5bp at three months, "very small" at five years; relayed by the round-3 attack, not re-read here). On a pooled
1-5-year spread the expected effect is about 1bp or less, inside this design's band (JPY P5 -3.470bp). The tape holds no contract of a week
to three months that could be read daily.

**Words.** "Basis" is the ledger's `xccy` series: the spread on the yen, euro or sterling overnight-rate leg of a floating-for-floating swap
against flat SOFR, in bp. **Negative is the conventional sign of a dollar premium** (`data/swap_tape/README.md`); some literature uses the
opposite sign. D < 0 means the basis was more negative in the window than around it.

**It can say:** for each quarter-end, how the median printed 1-5-year basis in the window compared with the days around it, and where that
difference sits among mid-quarter windows (MEASURED, on the ledger's universe: US-reported OIS-versus-SOFR basis swaps).

**It cannot say:**
- anything about short-dated FX swaps or repo, where CGFS 65 places quarter-end pressure: "US repo rates may spike and spill over to
  short-dated FX swaps" (p 35). The tape is the CFTC cumulative RATES file only; a small or absent D is not evidence against that paper;
- **who traded or why.** Neither identifies the counterparties or the reason. A D below the band does not show that banks adjusted balance
  sheets, that any investor hedged, or that any flow moved a price;
- anything about 31 Dec itself when the window ended earlier: in 2024 and 2025 the JPY window ended 8 days before 31 Dec because no JPY
  trade printed from 24 Dec to 2 Jan. Such a row describes "a window ending 8 days before the quarter-end";
- whether a swap resets its notional, its exact start date beyond "spot" (0-5 days), or trades reported only outside the US;
- anything general: the band rests on about eight stretches, and ranks against it are not independent draws.

**Grades.** D, ranks and band percentiles are MEASURED. No row is a test outcome.

**Required sentence (README, printout, every `note`):** "These are medians of reported 1-5-year cross-currency swap prices around
quarter-ends. A difference at a quarter-end does not show who borrowed dollars, why, or that any flow moved a price."

## 1. Hard requirements

- **R1. Offline, committed derived inputs only (E-005, E-024).** `bin/quarter_end_basis.py` reads only `data/swap_tape/cells_YYYY.csv`,
  `diagnostics_YYYY.csv` and `monthly_short_tenor.csv`. It imports no network module (`urllib`, `http`, `socket`, `ssl`, `requests`), opens
  no DTCC zip and never reads `~/dtcc_ppd/`. No FRED, no sec.gov. It sends no request, so it needs no User-Agent; it must still pass M10.
- **R2. Latches belong to people.** The ledger's `~/dtcc_ppd/STOP` may stop the weekly tape run; this build then shows `incomplete`
  anchors. No code path here names, deletes, renames or writes any STOP file (G11).
- **R3. Derived-only, under the ledger's count floor (E-024).** Every committed number is a statistic of published ledger statistics. A
  pooled daily median enters only if published (n >= 5); a tenor median only if published (n >= 10). No per-trade value, minimum or
  maximum, DTCC file name, row or identifier is written. Medians and D are written only for `complete` rows (3.7).
- **R4. Committed files** are exactly the ten names of section 6 in `data/quarter_end_basis/`. Every CSV and `columns.tsv` opens with one
  `# source:` line; the header is the first line not starting with `#`. Headers equal the canonical allowlist text of section 6, whose
  sha256 is anchored there and held in code as `SPEC_ALLOW_SHA256` (G9, M22).
- **R5. Wording.** No causal or attribution wording (the literal regex of G10) and no verdict wording (G15) in README, SOURCES.md or any
  committed text field. Exemptions: the required sentence verbatim; in SOURCES.md, lines carrying a page-cited CGFS reference.
- **R6. Exact arithmetic.** Ledger medians are parsed as `decimal.Decimal` from their strings; means of two values, D, ranks and all
  comparisons are exact; mean tenors use `fractions.Fraction`. Rounding only when text is written: 3 decimals (bp, years), half away from
  zero (`ROUND_HALF_UP` on Decimal), never Python's `round()`.
- **R7. Frozen design.** The constants of section 3 are held in code as `DESIGN` and as the literal `DESIGN_TEXT` (3.10); G8 requires them
  to match this spec. A change after 23 Oct 2026 is appended to the log at the end with the old values kept, and the old-rule rows are
  kept beside the new ones.
- **R8. The band of record is written once (context only).** The first build with `tape_last_date` >= 2026-11-27 writes an `of_record`
  band row per pair (`asof` 2026-11-27); later builds copy it unchanged from the committed `band.csv` and add a `recomputed` row. A
  difference is a WARN with both rows kept.
- **R9. The only clock is `tape_last_date`** (the last date in the cells files). No wall-clock value enters any committed file; rebuilds on
  the same inputs are byte-identical (G14). Staleness (C12) is printed to stdout only.
- **R10. Code.** New script, Python 3 standard library only; it may copy `render_csv` from `bin/fx_rate_gap.py` and `q7` from
  `bin/swap_tape_ledger.py`. It edits no existing file except the warn-only M22 guard in `bin/check.sh`.

## 2. Data

### 2.1 What the tape holds (inventory at `b22f51a`)

- **Daily** cells, every weekday 2024-10-14 to 2026-10-21 (528 weekdays, contiguous, no `date_status` rows), for `xccy_jpyusd`,
  `xccy_eurusd`, `xccy_gbpusd`, tenors 1-5 years and `pool1to5`, variant `headline`. Tenor bucket: expiry within 7 days of effective date
  plus N years; spot start 0-5 days; no platform filter or time window (ledger spec section 6).
- **Per-tenor daily medians are rare:** they need n >= 10, with no `thin` level. Days published of 528: JPY 41 / 97 / 40 / 8 / 136 (1y to
  5y), EUR 31 / 50 / 24 / 9 / 115, GBP 2 / 6 / 2 / 0 / 27. Per-tenor n is always published.
- **`pool1to5` is the main series.** Status ok / thin / below_min_n: JPY 395 / 49 / 84; EUR 422 / 60 / 46; GBP 226 / 166 / 136. Median
  daily n: JPY 18, EUR 17.5, GBP 9. It mixes tenors, hence the mix measure (3.6); the same-day JPY 5y-minus-2y median is about -7.75bp
  (57 days, reviewer), about 2.6bp per year of tenor, so mix matters for JPY.
- **No daily sub-1-year cross-currency cell exists.** The only short tenor is monthly (`monthly_short_tenor.csv`, JPY and EUR, 3m and 1y,
  2024-10 to 2026-09): JPY 3m 404 trades in 24 months (median 14.5 a month on 7 days; 19 months published), EUR 3m 545 (median 19 on 9
  days; 21 published) - about two a day. Q6 reports these counts only.
- **Thin days.** The ledger's `warn_f0_low_<series>` (F0 below half its trailing 20-date median): JPY 77 days, EUR 56, GBP 71; 21 / 21 /
  15 of them still carry a published pool median.
- **Year-ends are the thinnest days.** JPY pool n was 0 on 25 Dec 2025 and every weekday 29 Dec 2025 to 2 Jan 2026, and every weekday 27 Dec
  2024 to 3 Jan 2025. Hence windows counted in liquid days (3.1).

### 2.2 Fields read

- `cells_YYYY.csv` (header `date_utc,series,tenor_y,variant,unit,n,median,q1,q3,iqr_bp,iqr_over_sqrt_n_bp,share_pkg,share_gt10bp,status`):
  the three xccy series, `variant = headline`; `date_utc`, `tenor_y`, `n`, `median` (bp, 3 decimals), `status`.
- `diagnostics_YYYY.csv` (`date_utc,key,value,n`): presence of `warn_f0_low_xccy_jpyusd`, `..._eurusd`, `..._gbpusd`.
- `monthly_short_tenor.csv` (`month,series,tenor,n,median,q1,q3,iqr,status,n_days_with_trades`): xccy rows; `n`, `status`,
  `n_days_with_trades` only.
- Lines starting with `#` are skipped; each header must equal the one above exactly, or the build stops (G13).

### 2.3 Timing, vintages, holes and revisions

- The weekly tape run fetches to the Wednesday, so Thursday's file arrives a week later. A ledger date is a UTC execution date.
- A weekday with a ledger `date_status` row, or absent from the cells inside the covered range, counts as **covered but not liquid**.
  "The tape covers date X" means `tape_last_date` >= X.
- The ledger upserts only the weekdays it is given. `inputs.csv` records each input's sha256, rows and dates. **`inputs_sha256`** (band.csv)
  is the sha256 of UTF-8 lines, one per covered weekday <= `asof` in date order, each `date,pool_n,pool_median,n1,n2,n3,n4,n5,warn` + LF,
  where `pool_median` is the cells string verbatim (empty if blank) and `warn` is 1 or 0.
- `cells_2024.csv` sha256 `8a93cb1c7dfc542c2f15454550c25989fd0c0d0ded85b9f4b6692b3952584bd2`; `cells_2025.csv`
  `fef068669d757fff0ae26611f662de9864a6b6f54dd687d697192b2e06a7a11b` (closed years; C01).

### 2.4 Licence, citation and conventions

- **DTCC:** derived from DTCC Public Price Dissemination, CFTC cumulative rates reports (pddata.dtcc.com), through the project's ledger;
  non-commercial research under THE_ASK.md E-024; statistics only; CC BY 4.0 covers this project's computation only.
- **BIS CGFS Papers No 65** (June 2020): "Brief excerpts may be reproduced or translated provided the source is stated" (p ii). Quotes of 15
  words or fewer, page-cited. URL and sha256 in 2.5.
- **Leg convention and corrections (R3-6, SOURCES.md):** CFTC orders the two floating legs alphabetically by underlier, and JPY, EUR and
  GBP all sort before USD, so the ledger's foreign-leg-first reading holds for these pairs. No side (payer or receiver) is disseminated:
  each daily value is a median of traded spreads, not a mid. Package share and correction handling are as the ledger spec defines; this
  build adds no filtering of its own.

### 2.5 URLs observed (23 Oct 2026, one request each)

- `https://pddata.dtcc.com/` - 200, text/html, 7,000 bytes, "Public Price Dissemination Dashboard". Citation only.
- `https://www.bis.org/publications/cgfs-paper-65-us-dollar-funding-international-perspective.pdf` - 200, application/pdf, 3,704,415 bytes,
  sha256 `0a1d5ce92b9fec5756c729c449e01e9df5ab5db7f90111ef8119d7e3c5a2c504`. Quarter-end passages: printed pp 28, 35, 44, 73. The paper
  sizes no quarter-end move in 1-5-year basis swaps.

## 3. Method

### 3.1 Liquid days (per pair)
A weekday is **liquid** for a pair if its `pool1to5` cell has status `ok` or `thin` (published median, n >= 5) and the diagnostics hold no
`warn_f0_low_<pair>` row for it. `L` = the pair's liquid days in date order.

### 3.2 Anchors
- **quarter_end:** the last weekday on or before each calendar quarter-end from 2024-12-31 on, as far as the tape reaches. `in_sample` =
  yes for 2024-12-31 to 2026-09-30 (seen before the build), no after.
- **month_end:** the last weekday of Jan, Feb, Apr, May, Jul, Aug, Oct, Nov.
- **placebo:** every other weekday. Only placebos in the band (3.5) are written.

### 3.3 Window and controls (counted in liquid days)
For anchor `a`: `j` = index in `L` of the last liquid day on or before `a`; `k` = index of the first liquid day after `a`.
- **Window** `L[j-4..j]`; **pre-buffer** `L[j-7..j-5]` (unused); **pre-control** `L[j-17..j-8]` (10 days).
- **Post-buffer** `L[k..k+2]` (unused); **post-control** `L[k+3..k+12]` (10 days).
- **Tolerance:** `a - L[j]` <= 10 calendar days and `L[k] - a` <= 10, else `gap`. `gap_days` = `a - L[j]`; `on_date` = yes when
  `gap_days` = 0. Text for any other row says "a window ending N days before the quarter-end" (or month-end).
- **If `j - 17 < 0`** (too little history) the status is `incomplete`; indices never wrap (G2).
- The window never holds a day after `a`. `weekdays_window_span` = weekdays from `window_first` to `window_last` inclusive.
- `pre_in_zone_days` = how many of the 10 pre-control days fall in any exclusion zone `Z_q` (3.5).
- `post_in_zone_days` (round 4, O-4) = how many of the 10 post-control days `L[k+3..k+12]` fall in any exclusion zone `Z_q`; descriptive, like `pre_in_zone_days`.

### 3.4 The difference D
`D = median(window daily medians) - (median(pre-control medians) + median(post-control medians)) / 2`, bp. A median of ten is the mean of
the 5th and 6th values. The symmetric control removes a linear trend exactly; a pre-only control would not (G4).
**Spike or plateau.** For an ordinary quarter-end, 6-8 of the 10 pre-control days lie in `Z_q` (JPY 2025-03, 2025-06, 2026-03, 2026-06:
6, 7, 6, 8; EUR 2025-03: 8). A level shift spread over the whole zone is seen in D at about half its size; a move confined to the five
window days is seen whole. `pre_in_zone_days` is printed so a reader can tell which case a row is closer to.

### 3.5 Band (context) and reference set
- **Exclusion zones** `Z_q = [q - 21 days, q + 7 days]` for every calendar quarter-end q from 2024-09-30 to 2027-12-31.
- **Band:** placebo anchors that are `complete`, whose span (first pre-control day to last post-control day) touches no `Z_q`, whose last
  post-control day is <= `asof`, deduplicated by `(j, k)` (earliest date kept). **No month-end anchor can pass the zone test:** its span
  always touches some `Z_q` (none did for JPY, EUR or GBP), so the band holds only mid-quarter-month windows and `in_band` is "no" for
  every month-end.
- **Stretch:** the interval between two consecutive calendar quarter-ends; a band anchor belongs to the stretch holding its date.
- **Percentiles, nearest rank:** P_q is the value at 1-based rank `ceil(q x k)` of the k band values sorted ascending (q an exact
  Fraction), q = 0.05, 0.25, 0.50, 0.75, 0.95. `sd_bp`: population SD (exact variance, then square root). **Leave-one-stretch-out P5:**
  P5 recomputed with each stretch removed in turn; its min and max are printed (information only).
- **Reference set (non-overlapping):** in each stretch, the band anchor at position `ceil(m/2)` in date order (m = band anchors in that
  stretch). Spans from different stretches are separated by a zone, so reference windows never overlap. `in_ref` marks them.
- **Ranks:** `rank_band` = number of band values <= D, of `k_band`; `rank_ref` = number of reference values <= D, of `k_ref`. Every rank's
  text carries the caveat "overlapping windows from about eight stretches; not independent draws" (band) or "one window per stretch;
  about eight values" (reference).
- **Band roles:** `provisional` (asof = `tape_last_date`, before the tape covers 2026-11-27), `of_record` (asof 2026-11-27, written once,
  R8), `recomputed`. Ranks use `of_record` when it exists, else `provisional`; `band_role` names which.

### 3.6 Tenor mix and per-tenor D
- Mean tenor of a day set = sum of `t x n_t` over days and t = 1..5, divided by the sum of `n_t` (pool n equals the sum on 1,584 of 1,584
  pair-days, C04). `d_mean_tenor_y` = window minus the 20 control days. **Mix limit** = P95 (nearest rank) of `|d_mean_tenor_y|` over the
  band. Above it, `mix_flag` = yes and every text on that row says "tenor mix shifted; not read as a basis move" (G15).
- **Per-tenor D** (`anchors_tenor.csv`, for quarter-end, month-end and reference anchors): on the anchor's own window and control days,
  using only days where tenor t's median is published. `complete` needs at least 2 window days and 3 days in each control; otherwise
  `too_few_days`, values blank. Anchors not `complete` give `anchor_not_complete`.

### 3.7 Status
In this order: `incomplete` (history short, `j - 17 < 0`, or the tape does not reach `L[k+12]`); `gap` (tolerance failed); `low_n` (window n
< 25, pre-control n < 50 or post-control n < 50, n = trades summed over the days' pool cells); `complete`. Only `complete` rows carry
medians, D, ranks and mean tenors.

### 3.8 What sizes stand out (context; data to 2026-10-21, C07)

| Pair | k band | stretches | P5 | P50 | SD | P5 leave-one-stretch-out | k_ref | ref min / median / max | Mix limit |
|---|---:|---:|---:|---:|---:|---|---:|---|---:|
| JPY/USD | 52 | 8 | -3.470 | +0.469 | 2.390 | -3.470 to -2.789 | 8 | -3.033 / +1.234 / +4.469 | 0.663y |
| EUR/USD | 68 | 8 | -1.391 | +0.063 | 0.945 | -1.406 to -0.938 | 8 | -1.266 / +0.445 / +1.688 | 0.730y |
| GBP/USD | 26 | 5 | +0.016 | +0.391 | 0.666 | -0.110 to +0.078 | 5 | +0.219 / +0.625 / +1.875 | 1.061y |

All bp unless marked. The three lowest JPY band values all come from the February 2026 stretch, which is why dropping it moves P5 to
-2.789: the band's lower tail rests on one episode. An effect of about 1bp, the size the literature implies for this tenor range, sits well
inside the band and cannot be told from noise here.

### 3.9 Thin trading
Q4 reports, per anchor type, median window n, median `gap_days` and `warn_f0_low` days in the 10 calendar days to the anchor.

### 3.10 `DESIGN_TEXT` (one line: the lines below joined with single spaces; G8 compares it with this spec)
`X4-DESIGN v2 descriptive | pool1to5 | liquid = published median, no warn_f0_low | window 5, buffer 3, control 10+10 | tolerance 10 days |
j-17<0 incomplete | floors 25/50/50 | zone -21/+7 | band asof 2026-11-27, dedupe (j,k), nearest rank | ref = ceil(m/2) per stretch |
mix limit P95 | tenor D 2/3/3 | spec is the authority`

## 4. CALENDAR (proposal only; the builder edits nothing)

One descriptive row, no scoring row:
- `2027-01-29` - "X4 quarter-end basis (descriptive, no verdict): after the weekly swap-tape run, run `python3 bin/quarter_end_basis.py
  selftest` and `build`; the 31 Dec 2026 anchor joins `anchors.csv` when its post-control days have posted (status `complete`); if it is
  still `incomplete`, re-run after the next weekly run. Spec `_research/2026-10-23-Quarter-End-Basis-Spec.md` at commit <hash>; the spec
  is the authority." Post-controls at the two earlier JPY year-ends ended 2025-01-28 and 2026-01-22, so 29 Jan may be early.

## 5. Questions (fixed now; descriptive; no verdict, no "notable" flag, no binomial probability)

All rows go to `questions.csv` with a unit and a denominator; every `note` carries the required sentence, and every rank its caveat (3.5).
`in_sample` rows add "examined before the build".
- **Q1. Each quarter-end, each pair:** status, D, `on_date` or "a window ending N days before the quarter-end", `pre_in_zone_days`,
  `rank_band` of `k_band`, `rank_ref` of `k_ref`, `d_mean_tenor_y` and the mix flag; and the per-tenor D cells that are `complete`.
  Pinned row: JPY 2025-06-30, D = 0.234 (the README's worked anchor).
- **Q2. Over complete quarter-ends, each pair:** m, mean D, median D, the count at or below band P5 and the count at or below the reference
  minimum, each with the caveat. No standard error, t-statistic or probability.
- **Q3. Month-ends:** the Q2 statistics for complete `month_end` anchors, beside the quarter-end ones; descriptive only (none is in the band).
- **Q4. Thin trading** (3.9); for each year-end, the window's first and last dates.
- **Q5. Tenor mix and tenors:** per quarter-end, `d_mean_tenor_y` against the limit; the number of complete per-tenor cells per tenor.
- **Q6. Short-tenor availability:** the monthly counts of 2.1.

## 6. Outputs

**Script `bin/quarter_end_basis.py`.** Modes: `build` (offline, byte-identical on re-run) and `selftest` (synthetic fixtures in a temp dir,
under 20 s). `verdict.csv` of round 1 is gone; its per-anchor content is folded into `anchors.csv`, and `insample.csv` is renamed
`questions.csv` because it now covers every quarter-end. Committed names (ten): `README.md`, `SOURCES.md`, `columns.tsv`, and the CSVs below.

**Header allowlist, canonical text.** One line per file, `<name>:<headers comma-joined, no spaces>`, each ending in LF (the last one too),
in this order. `columns.tsv` holds the same as `file<TAB>columns` with columns joined by `|`, after its `# source:` line. G9 and M22 parse
this fenced block (the first after this paragraph), skip `# source:` lines and compare.

```
anchors.csv:pair,anchor_date,anchor_type,in_sample,in_band,in_ref,status,window_first,window_last,gap_days,on_date,weekdays_window_span,post_first,pre_in_zone_days,post_in_zone_days,n_window,n_pre,n_post,med_window_bp,med_pre_bp,med_post_bp,d_bp,band_role,rank_band,k_band,rank_ref,k_ref,mean_tenor_window_y,mean_tenor_ctrl_y,d_mean_tenor_y,mix_limit_y,mix_flag
anchors_tenor.csv:pair,anchor_date,anchor_type,tenor_y,days_window,days_pre,days_post,med_window_bp,med_pre_bp,med_post_bp,d_bp,status
band.csv:pair,band_role,asof,tape_last_date,k_anchors,stretches,p5_bp,p25_bp,p50_bp,p75_bp,p95_bp,sd_bp,p5_leave_one_stretch_out_min_bp,p5_leave_one_stretch_out_max_bp,k_ref,ref_min_bp,ref_median_bp,ref_max_bp,mix_limit_y,inputs_sha256
questions.csv:question,pair,anchor_type,anchor_date,statistic,value,unit,denominator,note
short_tenor_availability.csv:series,tenor,first_month,last_month,months,months_published,n_total,n_month_median,days_with_trades_month_median
inputs.csv:file,sha256,rows,first_date,last_date
checks.csv:check_id,description,expected,observed,status
columns.tsv:file,columns
```

**sha256 of that text (1,096 bytes): `3f54fbeb17c65e257af8acd41c1f2b0b2398b432ca18b3bed4f60c1c5e2445e4`** (round 4: `post_in_zone_days` added to `anchors.csv` after `pre_in_zone_days`; the earlier text was 1,078 bytes with sha256 `479678adef66bcd7aa9ca5e3f90a89d7b0e1ffebc90d6e97921dd8f76f0c2ed6`; the new hash was computed by the builder, per ruling O-4 of round 4). It is
anchored here, outside the code. A builder who needs a column changes this text and its hash first and tells the supervisor.

Value sets: `anchor_type` in {quarter_end, month_end, placebo}; `status` in {complete, incomplete, gap, low_n} (anchors) and {complete,
too_few_days, anchor_not_complete} (tenor rows); `band_role` in {provisional, of_record, recomputed}; yes/no flags are `yes` or `no`.

**`README.md`** (generated; G10 and G15 scan it):
1. **Opening paragraph (reviewer's wording, adapted):** "Banks and investors swap yen, euros or pounds for dollars. The price of that swap
   shows how scarce dollars are. This folder asks whether that price, on swaps of one to five years, looked different in the last days
   before each quarter-end than on the days around it. A swap of that length spans every quarter-end whatever day it is struck. Studies
   place the quarter-end effect in currency contracts of a week to three months, and this data holds none of those, so a small or absent
   difference here says nothing against those studies." Then the required sentence.
2. Sign convention in one line at the top of the results: negative means dollars cost more.
3. The quarter-end table (pair, quarter-end, window dates, `on_date` or "window ending N days before", D, ranks with caveats, mix flag).
4. Defined terms, four only: basis and its sign; window; D; band (and reference set). Everything else goes to SOURCES.md.
5. Worked anchor: **JPY 2025-06-30, D = 0.234**, from its three medians in `anchors.csv`.
6. Limits: the band comes only from mid-quarter-month windows in about eight stretches, and its lower tail rests on one episode (3.8);
   "Neither identifies the counterparties or the reason."; spike versus plateau (3.4).
7. Column dictionary; provenance (DTCC citation, E-024, ledger commit, input hashes).

**`SOURCES.md`:** DTCC citation and E-024 conditions; ledger files and hashes; the CGFS paper (URL, sha256, excerpt notice, pp 28, 35, 44,
73); the two papers relayed by round 3, marked "relayed, not re-read"; ST1 as prior work on levels; the leg-convention and correction notes
of 2.4; that the C13 in-sample values were computed by the second reviewer before the build; and every build decision (liquid days, buffers,
zone, dedupe, nearest rank, floors, reference pick, tenor-D minimums), none of which go in the README.

## 7. Leak guard M22 (`bin/check.sh`, warn-only)

Prints one ✗ line per breach and ✓ when clean; never blocks. `QEB_DIR` (default `data/quarter_end_basis`) and `QEB_SPEC` (default
`_research/2026-10-23-Quarter-End-Basis-Spec.md`) override the paths.
1. The folder holds only the ten names of section 6.
2. The fenced block of section 6 hashes to the pinned sha256; `columns.tsv` and every CSV header (first non-`#` line) equal it.
3. No file named `CFTC_CUMULATIVE_*`, no `.zip`, no header holding `Dissemination Identifier`, `Event timestamp`, `UPI FISN` or
   `Notional currency-Leg 1`.
4. No field that is a whole string of 8-19 digits; no `/Users/`, `/private/tmp` or `@` in any committed file.
5. No row in `anchors.csv`, `anchors_tenor.csv` or `questions.csv` whose status is not `complete` (or whose `n_window` < 25) carrying a
   median, D or rank.
6. No G10 or G15 match in README.md, SOURCES.md or a `note`, outside the exemptions of R5.

**Shown to fail:** on scratch copies with (a) a planted `CFTC_CUMULATIVE_RATES_2026_10_14.csv`, (b) a `Dissemination Identifier` header,
(c) a 12-digit cell, (d) a `/Users/` path, (e) an extra file, (f) a `low_n` row carrying `d_bp` in each of `anchors.csv`, `anchors_tenor.csv`
and `questions.csv`, (g) a README line "because banks window-dressed", (h) a README line "the 2026 year-end SUPPORTS a widening", it prints
a ✗ line for each, and ✓ on the clean folder.

## 8. Selftests (synthetic fixtures; each guard runs its own mutants; a mutant that passes is a selftest failure)

| Guard | Protects | Mutants (each must make the guard FAIL) |
|---|---|---|
| G1 liquid days | 3.1, 2.3 | a `warn_f0_low` day counted liquid; a blank median read as 0; `thin` (n 5-9) days dropped; a hole weekday counted liquid, or counted as not covered |
| G2 window and controls | 3.3 | window of 4 or 6; buffers 0; controls of 9; controls counted in weekdays; the window holding the first liquid day after the anchor; **`j - 17 < 0` wrapping to the end of `L` instead of `incomplete`** |
| G3 tolerance | 3.3 | gap of exactly 10 flagged `gap`; gap of 11 accepted; post side unchecked; `on_date` set when `gap_days` = 1 |
| G4 difference | 3.4 | pre-only control (linear-trend fixture, true D exactly 0); mean instead of median; median of ten as the 5th value; Python `round()` on -0.0625 (must print -0.063); **float arithmetic** (fixture where D equals a band value exactly in Decimal but not in float, so the rank changes) |
| G5 sign | 2.4 | fixture whose window is 6bp more negative than its controls must give D = -6 and `rank_band` 1; D computed as control minus window; the C03 sign check inverted |
| G6 band | 3.5 | linear-interpolated percentiles; a span touching `Z_q` kept; `Z_q` written as [q-7, q+21]; duplicate `(j, k)` kept; a quarter-end or month-end in the band; a planted extreme placebo after `asof` changing the `of_record` band; leave-one-stretch-out dropping one anchor instead of one stretch |
| G7 status and mix | 3.6, 3.7 | `low_n` tested before `gap`; floors tested on the window only; n counting days instead of trades; signed instead of absolute `d_mean_tenor_y` for the limit; mix limit at P90 |
| G8 frozen design | R7, R8 | any `DESIGN` constant changed; `DESIGN_TEXT` differing from 3.10; the `of_record` row rewritten by a later build; a differing `recomputed` row not reported as WARN |
| G9 allowlists | R4 | an extra or renamed column; `SPEC_ALLOW_SHA256` not the sha256 of the canonical text; `columns.tsv` drifting from it; the `# source:` line read as a header |
| G10 causal wording | R5 | see the literal regex below. The required sentence passes verbatim; "Neither identifies the counterparties or the reason." passes verbatim; the README opening passes; required sentence + "Prices widened because banks window-dressed." fails; a `note` "Japanese banks borrowed dollars" fails; a `pushed` anywhere fails |
| G11 offline and latches | R1, R2 | the selftest scans its own source: an inserted `import urllib.request`, `import socket`, or a path containing `dtcc_ppd` or `STOP` fails it |
| G12 commit folder | section 7 | the planted copies (a)-(h): the guard fails on each and passes on the clean folder |
| G13 inputs | 2.2 | header read from the `#` line; a cells file with an extra column accepted; pool n not the sum of tenor n accepted; a non-headline variant read |
| G14 rebuild and clock | R9 | a second build changes any sha256; **the build run under two different fake wall clocks gives different bytes** (any `date.today()`/`datetime.now()` in a committed value) |
| G15 descriptive wording | R3-1, R3-3, R3-4 | any of `SUPPORTS`, `AGAINST`, `INCONCLUSIVE`, `PENDING` (case-sensitive) or "statistically significant", "significance", "p-value", "reject the null" in committed text; a `mix_flag = yes` row whose text lacks "tenor mix shifted; not read as a basis move"; a row with `gap_days` > 0 described as "at the quarter-end" instead of "a window ending N days before the quarter-end"; a rank printed without its caveat; a binomial probability printed |
| G16 reference set and tenors | 3.5, 3.6 | two reference anchors from one stretch; a reference pick other than `ceil(m/2)`; overlapping reference windows; a per-tenor D using a day whose tenor median is blank (read as 0) or using a pooled median; `complete` with 1 window day; a rank counting `<` instead of `<=`, or over `k + 1` |

**G10 literal regex** (Python, compiled with `re.I`; the base is `bin/fx_rate_gap.py` `CAUSAL_RX`, with "because of the intervention"
widened to "because", plus the round-1 list; copied, not imported):

```
\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because|due\s+to|in\s+response\s+to|led\s+to|prompted|pushed|as\s+a\s+result\s+of|reflect(?:s|ed|ing)?|amid|owing\s+to|on\s+the\s+back\s+of|window[- ]dress(?:ed|es|ing)?|borrowed|borrowing\s+by|demand\s+for\s+dollars|hedging\s+demand)\b
```

**G15 literal regex** (no `re.I` on the first group): `\b(SUPPORTS|AGAINST|INCONCLUSIVE|PENDING)\b|(?i:\b(statistically\s+significant|significance|p-value|reject(?:s|ed)?\s+the\s+null)\b)`.
The spec author ran both on the required sentence (one exempt `borrowed`), the "Neither ..." sentence and the README opening (no match),
and on the three bad texts above (matches).

## 9. Pinned checks (`checks.csv`)

**C05-C08 and C13-C15 are evaluated on the tape truncated at 2026-10-21 and on `monthly_short_tenor.csv` rows with month <= 2026-09**, so
they stay valid after later weekly runs.
- **C01 inputs:** `cells_2024.csv`, `cells_2025.csv` sha256 as in 2.3 (WARN if changed); 2026 file INFO.
- **C02 calendar:** 528 weekdays 2024-10-14 to 2026-10-21 at that vintage; later weekdays absent from the cells are listed (WARN; covered,
  not liquid).
- **C03 sign and unit:** `pool1to5` 2026-10-15 JPY n 26, -21.875bp; 2026-10-13 EUR n 26, -3.875bp; 2026-10-13 GBP n 24, +2.438bp. The
  median of all JPY liquid-day medians is -33.125 (FAIL if not negative).
- **C04 identity:** pool n = sum of tenor n on 1,584 of 1,584 pair-days.
- **C05 liquid days:** JPY 423, EUR 461, GBP 377 of 528; `warn_f0_low` days 77 / 56 / 71.
- **C06 windows:** JPY 2024-12-31: window 2024-12-12 to 2024-12-23, gap 8, n 89, first post 2025-01-06, post-control ends 2025-01-28. JPY
  2025-12-31: 2025-12-17 to 2025-12-23, gap 8, n 128, first post 2026-01-05, ends 2026-01-22. EUR 2025-12-31: 2025-12-19 to 2025-12-31,
  n 62. `gap`: EUR 2024-12-31 (12 days), GBP 2024-12-31 and 2025-12-31. `incomplete`: JPY and GBP 2026-09-30. `on_date` = yes for every
  other JPY and EUR quarter-end except JPY 2025-09-30 (gap 1); GBP 2025-03-31 has gap 3.
- **C07 band:** the table of 3.8 (k, stretches, P5, P50, SD, leave-one-stretch-out min/max, k_ref, ref min/median/max, mix limit), plus
  JPY P25 -1.064, P75 +2.657, P95 +4.281; EUR P25 -0.531, P75 +0.547, P95 +1.828; GBP P25 +0.328, P75 +1.063, P95 +2.000. Month-ends in
  the band: 0 for every pair.
- **C08 short tenor:** the counts of 2.1; 1y 24 of 24 months published, totals 1,667 (JPY) and 1,750 (EUR).
- **C09 CALENDAR text:** the 2027-01-29 row contains `_research/2026-10-23-Quarter-End-Basis-Spec.md`: PASS if present, WARN if absent.
- **C10 rebuild:** a second build leaves every sha256 unchanged.
- **C11 band of record:** after 2026-11-27 is covered, `recomputed` equals `of_record` (PASS) or differs (WARN, both kept).
- **C12 staleness (stdout only, not committed):** `tape_last_date` more than 10 days before the run date.
- **C13 in-sample D (computed by the second reviewer before the build; re-derived exactly by the spec author; half-away rounding of the exact
  value):** JPY 2024-12 -0.740; 2025-03 +3.468; 2025-06 +0.234; 2025-09 +3.375; 2025-12 -3.499; 2026-03 -4.329 (exact -4.3285, a rounding
  discriminator); 2026-06 +2.172. EUR 2025-03 +0.719; 2025-06 +0.828; 2025-09 -0.547; 2025-12 -0.156; 2026-03 -2.688; 2026-06 -0.438;
  2026-09 +0.578.
- **C14 `pre_in_zone_days`:** JPY 2024-12 0, 2025-03 6, 2025-06 7, 2025-09 0, 2025-12 2, 2026-03 6, 2026-06 8; EUR 2025-03 8, 2025-06 6,
  2025-09 8, 2025-12 4, 2026-03 8, 2026-06 7, 2026-09 8. `post_in_zone_days` (round 4, pinned by the verifier), in quarter-end order: JPY 0, 2, 2, 2, 0, 0, 0; EUR 2, 2, 2, 1, 0, 0, 2.
- **C15 per-tenor availability:** `complete` tenor cells at complete quarter-ends: JPY 2025-06-30 5y; 2026-03-31 2y and 5y; 2026-06-30 5y;
  EUR 2026-03-31 5y; GBP none. Every other tenor cell is `too_few_days`. Reference dates: JPY 2024-11-15, 2025-02-12, 2025-05-14,
  2025-08-13, 2025-11-12, 2026-02-09, 2026-05-14, 2026-08-07; EUR 2024-11-12, 2025-02-11, 2025-05-14, 2025-08-08, 2025-11-12, 2026-02-10,
  2026-05-12, 2026-08-11.

## 10. Success criteria (exact)

1. `python3 bin/quarter_end_basis.py selftest` prints G1-G16, every mutant making its guard fail; exit 0; no network; under 20 s.
2. `python3 bin/quarter_end_basis.py build` on the tape at `b22f51a` or later: C01-C08, C10, C13-C15 PASS (C01 and C07 may WARN after a
   ledger rebuild, differences listed); C09 WARN until the row exists; `band.csv` holds `provisional` rows until 2026-11-27 is covered,
   then `of_record` rows; no committed file contains a verdict word (G15).
3. A second `build` is byte-identical, including under a different wall clock.
4. `bin/check.sh --all`: the existing ✓ guard lines, `✓ no killed claims found`, `✓ page clean`, M10 clean, M22 ✓; and M22 prints the ✗
   lines of section 7 on the planted copies. Read the ✓ lines, never the exit code.
5. A verifier re-derives by hand from `cells_2025.csv` the D of JPY 2025-06-30 (0.234) from the window and control dates in `anchors.csv`,
   and the JPY band P5 (the 3rd lowest of 52 at the truncation).
6. README cold-reader test: two fresh agents with no context (a non-specialist trustee and a rates practitioner) read only the README. A
   reader who comes away believing it measures FX swaps, that it tested or found a year-end effect, that it shows who traded dollars, or
   that a row describes 31 Dec when its window ended earlier, fails the README.

**Landing (builder):** a REPRODUCE.md paragraph; the CALENDAR text of section 4 as a proposal; a HANDOVER row. The builder commits nothing.
The supervisor verifies, adds the guard as M22, adds the CALENDAR row and writes any findings text.

## 11. OPEN questions

- **O-1 Is the 1-5-year basis the right object?** The literature and CGFS 65 place the effect in contracts of a week to three months; the
  tape has none daily. *Settles:* a free daily short-dated FX-swap or forward-implied basis; none found free.
- **O-2 Year-end windows are holiday windows.** The JPY windows of 2024 and 2025 ended 23 Dec. No band window is a holiday window
  (Christmas lies in a zone).
- **O-3 The band is short and clustered.** About eight stretches; its lower tail rests on February 2026. The reference set has eight values.
  Neither supports a probability statement, and none is printed.
- **O-4 Post-control in zone.** Resolved by the round-4 ruling: `post_in_zone_days` is added beside `pre_in_zone_days` in `anchors.csv` (descriptive), and pinned in C14. The first post-control days can fall before q + 7, so the two counts together show how much of each control sits in an exclusion zone.
- **O-5 Daily 3-month cell.** The ledger's guard M4 keeps 3-month prints out of the pool on purpose; a pooled weekly 3-month cell needs its
  own ledger spec.
- **O-6 Mark-to-market resetting** is not visible on the tape; a shift in its share near quarter-ends would move the median unseen.
- **O-7 GBP.** Five stretches and a skewed band (P5 above zero); GBP rows are printed with the same caveats and no special reading.

## Log of design changes after 23 Oct 2026

- **Round 3 re-scope (23 Oct 2026, before the build).** Old: a registered test at 2026-12-31 (JPY primary, EUR secondary; SUPPORTS if
  D <= P5 of the band frozen at 2026-11-27, AGAINST if D >= P50, else INCONCLUSIVE; `REG_TEXT` "X4-REG v1"); round 1 added 2027-03-31 as
  a second registered observation. New: descriptive table, no verdict, no registration (R3-1, R3-5). Window, buffers, controls,
  tolerance, floors, zone, band rule and mix limit are unchanged; the band is context only.

## Supervisor rulings, 23 Oct 2026 (before any data run)

- **O-1 / O-7:** accepted as limits; the README says in its opening paragraph that the tape has no short-dated FX swaps, so a null here is not evidence against the CGFS paper.
- **O-3:** the 5th percentile stands.
- **O-4:** accepted. The same frozen rule is applied to 31 Mar 2027 (Japan's fiscal year-end) as a second registered observation, with its own CALENDAR row; each quarter-end is scored on its own and never pooled after the fact.
- **Guard number:** **M22**.
## Supervisor rulings, round 2 (second review), 23 Oct 2026 — before the build

The second reviewer computed the in-sample differences on the committed tape (JPY and EUR, seven quarter-ends each). The in-sample set was always descriptive; it is now also seen, and the spec header's "not seen" statement is amended to say so. The registered observations (31 Dec 2026, 31 Mar 2027) are unaffected, and the rule is NOT changed after seeing these values. All ten fixes are accepted:
- **R2-1** The window is the last five liquid days; in 2024 and 2025 the JPY window ended 8 days before 31 Dec. A verdict is about that window, not 31 Dec itself. `verdict.csv` gains `window_first, window_last, gap_days`; AGAINST reads "in that window".
- **R2-2** Detectable-size limits stated: the 5bp/2bp figures hold for a spike confined to the window; a plateau across the zone is seen at about half size, so AGAINST rules out a spike, not a plateau. `anchors.csv` gains `pre_in_zone_days`; `band.csv` gains leave-one-stretch-out P5 min and max (information only; JPY −3.470 and −2.789 today). The README says the band comes only from mid-quarter-month windows (about eight stretches) and the 5% threshold rests on one episode.
- **R2-3** The month-end sentence is corrected: no month-end anchor can be in the band; Q3 is descriptive only.
- **R2-4** "Neither identifies the counterparties or the reason"; a G10 test that the meaning text passes verbatim.
- **R2-5** The only clock is `tape_last_date`, as the reviewer wrote it; C12 to stdout only; wall-clock mutant.
- **R2-6** Pinned checks evaluated on the tape truncated at 2026-10-21 and monthly rows to 2026-09; j − 17 < 0 is `incomplete`; G2 mutant.
- **R2-7** The listed mutants are added, including the Decimal-equality fixture and thin-row planting in `verdict.csv` and `insample.csv`.
- **R2-8** Anchor status renamed `low_n`; `QEB_SPEC` defaults to `_research/2026-10-23-Quarter-End-Basis-Spec.md`; `columns.tsv` carries a `# source:` line; `inputs_sha256` serialization pinned; a hole weekday counts as covered but not liquid; the no-FX-swaps sentence goes in the README's opening paragraph; `REG_TEXT` and the CALENDAR rows carry the spec's commit hash and the 26 Feb 2027 deadline, and say the spec is the authority.
- **R2-9** The README worked anchor is JPY 2025-06-30 (D = 0.234), also pinned in Q1.
- **R2-10** The reviewer's plain opening is adopted; the defined-terms list is cut to basis and sign, window, D and band; the rest goes to SOURCES.md; the sign convention is stated once at the top of the results.
- **C13** pins the reviewer's in-sample values (half-away rounding of the exact value), with SOURCES.md recording that they were computed by the reviewer before the build.
## Supervisor rulings, round 3 (Grok attack, g10), 23 Oct 2026 — before the build

Grok's central point is accepted: the published quarter-end effect sits in short contracts that span the reporting date (Du, Tepper and Verdelhan, NBER WP 23170: one-week contracts, 30–40bp; Georgievska, Karner and Syrstad 2026, preliminary: 4–5bp at three months, "very small" at five years). On a pooled 1–5-year par spread the expected effect is about 1bp or less, against this design's detection edge of about 3.5bp (JPY). A registered SUPPORTS/AGAINST would therefore be close to foregone, and would still be read as a statement about year-end dollar funding. So:
- **R3-1 Re-scoped to a descriptive build (supersedes the registered test, round 1 O-4 and R2-1's verdict wording).** No SUPPORTS / AGAINST / INCONCLUSIVE verdict at any anchor. The build publishes, for every quarter-end anchor, D, its rank against the reference set, `gap_days`, the liquid-day counts and the mix measure, with the README's opening paragraph saying that a 1–5-year swap spans every quarter-end whatever day it is struck, that the literature places the effect in contracts of a week to three months, and that the tape has none of those.
- **R3-2 Reference set:** non-overlapping anchors, one per stretch between quarter-ends, reported beside the overlapping band; the dependence caveat is attached to every rank and to Q2 (no binomial probability is printed).
- **R3-3 Tenors:** a per-tenor D is printed wherever that tenor's own medians are published; the pooled D carries the mix measure; no pooled D is called a basis move when the mix measure exceeds its limit.
- **R3-4 Anchor-in-window:** `gap_days` = 0 is flagged `on_date`; any other anchor is described as "a window ending N days before the quarter-end".
- **R3-5 CALENDAR:** no scoring rows. One descriptive row (late January 2027) to add the 31 Dec 2026 anchor to the table when its days post; no 31 Mar 2027 registration.
- **R3-6 Leg convention and corrections:** SOURCES.md records that CFTC orders two floating legs alphabetically by underlier (JPY, EUR and GBP legs all sort before USD, so the ledger's foreign-leg-first convention holds for these pairs), that no side is disseminated (a median of traded spreads, not a mid), and that the ledger's package share and correction handling are as the ledger spec defines; this build adds no new filtering.
- The noise band and its freeze are kept only as context, not as a decision threshold.

## Supervisor rulings, round 4 (spec author's open items), 23 Oct 2026 — before the build

- **O-4:** add `post_in_zone_days` beside `pre_in_zone_days` in `anchors.csv` (descriptive); update the allowlist text and hash accordingly before the build, and record the new hash in the builder's decisions.
- Dropping Q2's standard error with the binomial is accepted.
