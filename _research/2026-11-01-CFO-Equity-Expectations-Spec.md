# Spec: does a second panel move the same way as the Philadelphia Fed forecasters on expected US equity returns, Q1 2024 to Q1 2026? The CFO Survey's expected S&P 500 return (spec author, 1 Nov 2026; amended to apply the supervisor's round 1, R1-1 to R1-15)

*Page context: `docs/index.html` §02, the sentence "... and in the survey, equity expectations actually rose" (the survey there is the Philadelphia Fed SPF,
STOCK10, Q1 2024 to Q1 2026, +15.4bp, `CORRECTIONS.md` C-082), and the §09 gap "What the multiple's resilience was made of" ("A third premium series that does
not share a bond leg would settle it"). Chosen in [`_research/2026-11-01-Grok-G15-Scoping.md`](2026-11-01-Grok-G15-Scoping.md) (candidate 1, ruled "take forward as
g15, reframed": the equity leg only, no premium). Attacked in
[`_research/2026-11-01-Grok-G15-CFO-Expectations-Attack.md`](2026-11-01-Grok-G15-CFO-Expectations-Attack.md). The 14 Sep reason for setting this source aside is in
`2026-09-14-P5iv-Third-Premium-Measure.md` ("Also on disk"): no matched bond expectation, so no premium can be built from it. That still holds. Lands as
`_research/2026-11-01-CFO-Equity-Expectations-Spec.md`. House style follows `_research/2026-10-30-Collateral-Reuse-History-Spec.md`, shortened because the build is
small. Script `bin/cfo_equity_expectations.py`, outputs `data/cfo_equity_expectations/`, vintages `data/vintages/cfo_survey/`, check.sh guard **M29**. Repository
read at `19dacee`. The rulings at the end are the record; this body applies round 1 (R1-1 to R1-15). Where the body and a ruling differ, the ruling wins.*

*"Observed" means seen by the spec author on 1 Nov 2026 in the repository. **This spec was written with no network access and with the workbook never opened:
every fact about the workbook below is a "supervisor fact" (layout and text, read by the supervisor on 1 Nov 2026, no value of any S&P column other than the four
pins) or "relayed".** **Blind:** the author computed and estimated no result of E1 or E2 and read no value of any S&P column. The only numbers used are C-082's SPF
figures and the four page values the supervisor passed on (pins). Where the author infers rather than reads, the text says UNCERTAIN or points to section 10.*

## 0. Goal, and what the result can and cannot say

- **Measure** the change in the CFO Survey's mean expected S&P 500 return between the first quarter of 2024 and the first quarter of 2026 (eight calendar quarters,
  the SPF window), on two horizons: **E1** the 10-year horizon (`sp_10yrexp_2`), mandatory; **E2** the 12-month horizon (`sp_12moexp_2`), secondary, README only.
  The statistic is **the change in the 1 November 2026 vintage of the survey's revised historical file**, never "first published". Each is registered (4.6) with a
  signed change in points (to two decimals in print) and a **sign** (RISE, FALL or ZERO, zone 0.10 point). **Nothing is registered against a yardstick and no
  verdict of agreement is registered** (R1-2, R1-3).
- **Describe** (not registered): the SPF's +0.1543 point beside E1 as a column `spf_direction` (SAME, OPPOSITE, FLAT; never AGREES or DISAGREES); the Duke-era range
  of eight-quarter changes (min, max, n, at most eight disjoint spans); a variant range from the current series itself (YC); the path of the four series used (local).
- **Why it is worth doing.** The §02 sentence claims a direction for "equity expectations" and rests on one panel. Whether a second panel moved the same way over the same
  quarters is the direct test of that claim. What the build must not do is turn it into a binary verdict that hides the size, the panel or the dates: the page sentence
  always gives both panels' changes as numbers, names both panels with their dates, and says "firms that follow the stock market".

**It can say** whether the CFO Survey's mean expected 10-year (and 12-month) S&P 500 return rose, fell or was unchanged to within 0.10 point between two quarters of the
named vintage, and whether the direction is the SPF's.

**It cannot say:**
- **anything about an equity premium.** One leg only; **no Treasury yield is subtracted and no premium is built.** This is why the source was set aside on 14 Sep; the
  reframing keeps that rule. The §09 gap stays open whatever the result;
- **anything about the discount rate.** For the 12-month horizon, expectations in this survey have been found to follow past returns (Greenwood and Shleifer 2014, relayed);
  for the 10-year horizon the evidence is weaker. Either way a change in either is not evidence about the discount rate;
- **anything about investors.** The respondents are financial decision-makers at firms (chief financial officers and others); the figures are stated expectations, not
  market prices;
- **anything across 2020.** The survey changed then (Duke only before, Duke with the Richmond and Atlanta Fed after; different question wording and outlier treatment), so
  **no level is compared across 2020 and no change spans it**;
- **whether the change is large or small against noise.** Sampling noise is not published (N is about 340-370 per quarter, from the pins); the 0.10 zone is a convention;
- **a result for any other horizon, country, group of respondents or series.**

**Required README sentences (verbatim; the guard checks them with `grep -F`):**
- **R-A:** "This build measures one leg only, the expected return on the S&P 500 from a panel of financial decision-makers at US firms who say they follow the stock market; it builds no equity premium and subtracts no Treasury yield."
- **R-B:** "Expectations of 12-month returns in this survey have been found to follow past returns (Greenwood and Shleifer 2014); for the 10-year horizon the evidence is weaker, so a change in either is not evidence about the discount rate."
- **R-C:** "The survey changed in 2020 (new sponsors, different question wording and outlier treatment), so levels are never compared across 2020; only changes within each series are."
- **R-D:** "The respondents are financial decision-makers at firms (chief financial officers and others), not investors; the figures are stated expectations, not market prices."

## 1. Hard requirements

- **R1. Free public data.** The registering input is the supervisor's 1 Nov 2026 workbook (sha256 `1b4e215c5626b741182b8a647c7a66d5c6d448616942d27138f18d37acec6bca`, 188,861 bytes), dropped by the
  supervisor into `data/vintages/cfo_survey/20261101/raw/current_historical_cfo_data.xlsx` (R1-9); the build writes a `MANIFEST.csv` for it with status `supplied`. The `fetch` mode stays for **later vintages**: one request, host
  `www.richmondfed.org`, the URL of 4.7. Any other host and any second request is refused before it is made. No key, no login.
- **R2. Fetch conventions.** GET only, no redirect followed, no retry, timeout 300 s, `Accept-Encoding: identity`, one fixed generic User-Agent string with no name, address, e-mail or contact. If a vintage for today's UTC
  date already holds a body whose sha256 matches its MANIFEST row, no request is made. **Only the supervisor runs the fetch mode and the registering build (`build --stage full --registering`).** The builder writes code and
  selftest and may run on the real workbook only `build --stage pre` (layout) and `--stage dry` (synthetic).
- **R3. Failures.** A **3xx is a FAIL with no STOP file** (exit 3). Any 403, 429 or other non-200, and a 200 body that is not an xlsx of 50,000 to 2,000,000 bytes, writes `data/vintages/cfo_survey/STOP_cfo` (exclusive, five
  lines `status`, `utc_time`, `url_path`, `retry_after`, `body_head`); with it present no request is made and the run exits 2. Only a person deletes it. A timeout prints `FAIL network`, exits 3, writes no STOP.
- **R4. Vintages.** `raw/` is gitignored and archived in the private companion; committed per vintage: `MANIFEST.csv` (`vintage,host,url_path,status,bytes,sha256,retrieved_utc,elapsed_s`). A later vintage rewrites every
  output **except `registered.csv`**, which is written by the first registering build only and never re-scored; its only later change is the supersede rule (P-S, 4.7).
- **R5. Frozen inputs.** The 4.6 block is the frozen rule set (sheets, columns, quarters, window, thresholds, pins, halting). It is not changed after any value is read.
- **R6. Wording.** No causal, price, speed or misconduct wording in README.md (the two G14-style patterns of 7). Say "expected return", "mean", "the CFO Survey", "the forecasters' survey", "firms that follow the stock
  market"; never "significant", "proves", "material", "because of", "drove", "comparable", "unusual", "agrees", "disagrees" or "confirms". The singular form states a change ("the mean expected 10-year return rose by 0.40 point").
- **R7. Code.** `bin/cfo_equity_expectations.py` is new, standard library only (the xlsx is read with `zipfile` and `xml.etree.ElementTree`: shared strings, cached cell values; a formula cell with no cached value is
  `endpoint_undefined`; hidden rows and columns are counted in the layout report). It reads no project file other than its own two folders and `bin/check.sh` (read-only, for the selftest's cross-check of M29's literal
  copies). No existing script changes, apart from the warn-only guard M29 in `bin/check.sh`.
- **R8. Numbers.** Cell text is parsed with `decimal`, precision 28, never float; missing is never zero, never interpolated, never carried. **Each cell is rounded half-even to 6 decimals; the statistic is the exact Decimal
  difference of the two rounded cells, with no further rounding** (R1-5). The sign comparison uses that difference.
- **R9. Post-registration fixes** go in README "Builder decisions" with the old value beside the new and, for a registered row, by P-S. No registered number changes otherwise.
- **R10. One source, derived statistics only (R1-15).** Every number comes from the one workbook. The SPF figure is fixed text in the 4.6 block and is never read from a file by the build. The pins enter `checks.csv` only.
  **Committed:** registered changes with their two endpoint values, the described yardstick min, max and n, the YC summary, checks and README. **`path.csv` (the full quarterly series) is local and gitignored**, like
  `data/vintages/cot_prices/derived/`. Each committed file credits "The CFO Survey (Duke Fuqua School of Business, Federal Reserve Banks of Richmond and Atlanta)" in its `# source:` line (README: first paragraph).

## 2. Data

### 2.1 The workbook (supervisor facts, 1 Nov 2026)

| Sheet | Content | Used |
|---|---|---|
| `through_Q1_2020` | Duke-era series, 74 rows, 2001Q4 to 2020Q1 consecutive; includes `sp_10_low`, `sp_10_exp`, `sp_10_high`, `sp_1_low`, `sp_1_exp`, `sp_1_high`; `sp_10_exp` and `sp_1_exp` are empty for 2019Q1 and 2020Q1, floats elsewhere | `sp_10_exp`, `sp_1_exp`: described range; path |
| `through_Q1_2020_dictionary` | defines `sp_10_exp` as "expected S&P return over the next 10 years" and `sp_1_exp` as the next year; the `sp_10_low` line carries the word "average" | text, printed into the README |
| `CFO_SP500` | current survey, 25 quarters, 2020Q3 to 2026Q3 (2020Q2 absent); `sp_12moexp_1/2/3`, `sp_10yrexp_1/2/3` (means), the same with suffix `_med`; no gaps in `sp_10yrexp_2` or `sp_12moexp_2` | `_2` columns: E1, E2, path |
| `from_Q2_2020on_dictionary` | under "Percent change (mean)": `_1`, `_2` ("expectation for S&P return over the next ..."), `_3` | text, printed into the README |
| `CFO_survey_dates` | open and close dates per quarter, 2020Q2 to 2026Q3 (2026Q3: 17 Aug to 4 Sep 2026) | `path.csv` dates; README |

"Dictionary text" means the two dictionary sheets. The median columns and the `_1`/`_3` bands exist but are **not used** (R1-10).

**Methods and results pages (supervisor, 1 Nov).** The methods PDF says the S&P items use the same wording as the Global Business Outlook Survey and that S&P 500 expectations data are winsorized at 2.5 and 97.5 percent; the
Q3 2026 results page says "winsorized at 5%". **Both are recorded, neither is resolved** (T3). The page figures (pins) are for firms that "closely follow the stock market", unweighted: Q3 2026 12-month 7.9% (N=336) and
10-year 9.6% (N=338); Q2 2026 12-month 7.8% (N=367) and 10-year 9.7% (N=372). A 25 March 2026 page said data from Q2 2020 to Q4 2025 were revised (relayed), which includes 2024Q1.

### 2.2 Series

- **Current series (E1, E2).** `CFO_SP500`, `sp_10yrexp_2` (CUR10) and `sp_12moexp_2` (CUR12), the cell as stored. The window is 2024Q1 to 2026Q1.
- **Described Duke-era range.** `sp_10_exp` (DUKE10) and `sp_1_exp` (DUKE12), eight-quarter changes over **2002-2020 (end quarters 2004Q1-2020Q1)**: the first end quarter is 2004Q1 (start 2002Q1), so no window uses the
  2001Q4 question form (R1-3). **65 nominal; the two empty quarters remove the windows ending 2019Q1 and 2020Q1; 63 defined.** Shown as min and max with n and "at most eight disjoint spans" (the 71 steps from 2002Q1 to
  2019Q4 hold eight disjoint eight-quarter spans; the ruling's draft said nine, see O-1). No rank, no label, no "comparable".
- **Described variant YC10 and YC12.** Eight-quarter changes inside the current series with end quarters 2022Q3 to 2026Q3 (17 nominal) minus the registered window (16 members), overlapping each other and the window (at most
  three disjoint spans). Summary only.
- **Quarter keys.** A key must parse to (year, quarter), be unique, and the keys must be consecutive within each sheet. Eight quarters before q is found by calendar arithmetic, never by row position.

### 2.3 Traps, and the rule that meets each

| # | Trap | Rule |
|---|---|---|
| T1 | The 2020 break joins different panels, wording and treatment | Nothing is compared across 2020; the registered statistic uses the current series only; the Duke range is described |
| T2 | The Duke-era scale may not fit the current panel | The range is context, never a test; it is printed with its n and the break |
| T3 | Winsorisation: 2.5/97.5 (methods PDF) against 5% (results page); the 2022 note used 2.5/97.5 (relayed); the annual revision touches 2024Q1 | A stated trap, not a halt. README records both, and the vintage and workbook sha256 are in the registered row |
| T4 | A fraction mistaken for a percent | The pins (a factor-5 error halts) and the `unit_odd` bound (-20 to 40) |
| T5 | The pins (2026Q2, 2026Q3) do not reach the window | README says so |
| T6 | Whether `sp_10_exp` is a mean and annualised | The dictionary is the source; the builder prints the dictionary lines verbatim into the README (at most 15 words each) (R1-11) |
| T7 | Quarter labels are not the same days as the SPF's | `path.csv` carries every current quarter's open and close dates; the README gives 2024Q1 and 2026Q1 beside the SPF deadlines **6 Feb 2024 and 2 Mar 2026** (supervisor-confirmed, R1-15; the 2026 date was delayed by a government shutdown) |
| T8 | Overlapping windows are not independent draws | At most eight (Duke) and three (YC) disjoint spans, said in the README |
| T9 | An xlsx read by hand can mis-assign shared strings, serial dates or hidden columns | Selftest G1-G2; a verifier re-reads cells with another parser after registration (criterion 8) |
| T10 | A filter the page names and the workbook may not | The page sentence says "firms that follow the stock market"; whether the workbook's `_2` columns carry the same filter is not on the sheets read (O-2) |

### 2.4 What was known before the build (the blind list)

- **KNOWN, relayed, not cell values of this workbook:** the SPF result (STOCK10 7.1513% to 7.3056%, +0.1543 point, C-082); the four pins; the layout of 2.1. **No CFO value appears in any repository file** (R1-1: the earlier
  extract named in `data/THIRD_PARTY_MANIFEST.tsv` is neither in git nor on disk; only its manifest row exists). No Q1 2024, Q1 2026 or Duke-era value was seen by anyone writing or briefing this spec. **`blind` is `full`** for
  E1 and E2; the README names the two pinned quarters, which sit after the window.

### 2.5 Licence and citation (R1-15)

The Richmond Fed's terms (read by the supervisor, 1 Nov) permit reproduction not for private or commercial gain and credited, and need written permission for republication or distribution otherwise. Ruling, on the ICE
precedent (E-025): commit derived statistics only; `path.csv` stays local. The raw workbook is not committed.

## 3. Method

- **3.1 Registering input and fetch.** The supervisor drops the workbook into the 20261101 vintage (R1); `fetch` is for later vintages (R1-R3) and prints status, bytes and sha256 only.
- **3.2 `build --stage pre`.** Reports layout only: sheet names, the key columns' names and format, row counts, the header row of each sheet, hidden rows and columns, the type of each S&P cell as `empty`, `numeric` or `text`
  **from the cell attributes, never by converting a value**, the consecutive-key test, the dictionary text, the CFO field dates of 2024Q1 and 2026Q1, and C01-C05. It prints and writes no number from an S&P column.
- **3.3 `build --stage dry --out <scratch>`.** Builds a synthetic workbook with the layout the pre stage reported and **the four pin values planted** (R1-9), runs the whole pipeline into `<scratch>` outside the repository's
  committed folders. The word SYNTHETIC appears only in each file's `# source:` line. It writes nothing under `data/`.
- **3.4 `build --stage full`** (the registering build adds `--registering`; supervisor only). Order: structural layout checks (HALT: exit 4, nothing registered); pins (UNIT_ERROR: exit 5, nothing registered); parse;
  `path.csv`; the described ranges; `registered.csv` (registering build only); `checks.csv`; README.md. A repeat build of the same vintage is byte-identical in every file.
- **3.5 Later vintages.** After the Q4 2026 survey release (expected late December, date unconfirmed, R1-13) a new vintage rebuilds every output but `registered.csv`; C12 compares the window values of the new vintage with the
  registered row and reports any revision.

## 4. Questions, fixed in advance

**4.0 Resolution.** No sampling error is published for the means, so nothing here is sized against noise; the zone of 0.10 point is the one-decimal resolution of the published pages, a convention fixed before data. The
signed change is always printed to two decimals beside the SPF's 0.15, so a same-direction move under 0.10 is visible as a number. The described Duke range has 63 defined windows from at most eight disjoint spans and covers
the post-2001 recovery, 2007-2009 and the 2010s, so it is wide.

- **Q1** The structure: counts, empties, keys, pins (`checks.csv`). **Q2** E1 and E2: the endpoint values, the signed change and the sign (`registered.csv`). **Q3** Is the CFO direction the SPF's (`spf_direction`, described)?
  **Q4** The described ranges. **Q5** The revision between vintages.
- **Not asked:** an equity premium; anything involving a Treasury yield; a level compared across 2020; any other survey; why expectations moved; whether a change is large against noise.

**What the page may say, fixed before data.** Every sentence names both panels, gives both changes as numbers, gives the dates (CFO field dates from the README; SPF deadlines 6 Feb 2024 and 2 Mar 2026) and says "firms that
follow the stock market" for the CFO Survey. The optional scale clause is "for scale, the Duke-era survey's eight-quarter changes over 2002-2020 ran from {min} to {max} points (n = 63; the question form and treatment differ
from 2020)".

| E1 outcome | The page may say (§02, in place of "in the survey, equity expectations actually rose") | The page must not say |
|---|---|---|
| **RISE** (`spf_direction` SAME) | "In the Philadelphia Fed forecasters' survey (responses due 6 Feb 2024 and 2 Mar 2026) the expected 10-year S&P 500 return rose 0.15 point from Q1 2024 to Q1 2026; in the CFO Survey (fielded {dates}), among firms that follow the stock market, it rose {+X.XX} points over the same quarters. This is the equity leg only: no premium is built, and neither survey is evidence about the discount rate." | "equity expectations rose" with no panel named; "confirms", "agrees" or "independent confirmation"; "proves"; "investors demanded a higher return" or "risk got dearer"; that the second panel settles the §09 gap; a percentage for a change in points |
| **FALL** (OPPOSITE) | "The two surveys moved in opposite directions. The forecasters' expected 10-year S&P 500 return rose 0.15 point from Q1 2024 to Q1 2026 ({SPF dates}); the CFO Survey's, among firms that follow the stock market, fell {-X.XX} points ({CFO dates}). The statement that equity expectations rose rests on the forecasters' survey alone." The sentence "in the survey, equity expectations actually rose" must not stand unqualified | "equity expectations rose" with no panel; averaging the two or calling the net "flat"; dismissing the CFO panel after the result because its respondents are not investors (R-D says it before the data); any sentence that keeps the §02 phrase unchanged. Whether C-082's wording needs a CORRECTIONS entry is the supervisor's call, not this build's |
| **ZERO** (FLAT) | "The CFO Survey's mean expected 10-year S&P 500 return, among firms that follow the stock market, changed by {signed X.XX} points over the same quarters, inside the 0.10-point zone this build treats as unchanged, so the second panel does not show the forecasters' rise of 0.15 point." | "confirms", "agrees" or "disagrees"; "did not rise" or "no change" without the zone and the number; treating FLAT as a point in either panel's favour |
| **VOID** | "The CFO Survey comparison could not be made ({reason in words}); the statement rests on the forecasters' survey alone." The panel is named in the §02 sentence anyway | any CFO Survey number; "no second panel confirms" |
| **E2** | README only (R1-10). The page does not use E2 unless the supervisor rules; if E1 and E2 differ in sign the README states both, with the horizon named | a sentence that merges the two horizons |

Every sentence is followed by "This is one leg of the premium, from a survey of financial decision-makers at firms; no premium is built and no Treasury yield is subtracted." The §09 gap sentence stays as it is: this build
is not a third premium series. A correction to a page or CORRECTIONS sentence goes only through `CORRECTIONS.md`, by the supervisor.

### 4.6 Registered statements (the script holds `SPEC_PREREG_SHA256` and refuses to write `registered.csv` if its constants do not reproduce this block byte for byte)

```
DEF|stat=exact_Decimal_difference_of_two_rounded_cells:_round_each_cell_half-even_to_6_decimals,_then_exp(end_quarter)-exp(start_quarter),_no_further_rounding|unit=percentage_points|exp=the_workbook_cell_as_stored_(percent,_not_fraction)|vintage=the_statistic_is_the_change_in_the_named_vintage_of_the_surveys_revised_historical_file,_never_first_published|quarter=calendar_quarter_label_YYYYQn|no_value_imputed_(missing_is_never_zero,_never_interpolated,_never_carried)|parsing=decimal_prec28,_never_float
CUR10|sheet=CFO_SP500|column=sp_10yrexp_2|era=current|quarters=2020Q3..2026Q3|n_expected=25|2020Q2_absent_and_not_invented
CUR12|sheet=CFO_SP500|column=sp_12moexp_2|era=current|quarters=2020Q3..2026Q3|n_expected=25|2020Q2_absent_and_not_invented
SIGN|RISE_if_stat>=0.10;FALL_if_stat<=-0.10;ZERO_if_abs(stat)<0.10|a_convention_equal_to_the_one-decimal_resolution_the_survey_publishes,_fixed_before_data,_not_a_noise_bound|the_signed_stat_is_always_printed_to_two_decimals_beside_the_SPF_figure
SPF|stat_pp=0.1543|sign=RISE|source=STOCK10_mean_Q1_2024_7.1513_percent_to_Q1_2026_7.3056_percent_(CORRECTIONS_C-082)|fixed_text_in_this_block_and_never_read_from_a_file_by_the_build
DIRECTION|described_column_spf_direction,_never_a_verdict|SAME_if_sign==RISE;OPPOSITE_if_sign==FALL;FLAT_if_sign==ZERO;none_if_VOID;na_for_E2|never_written_as_AGREES_or_DISAGREES|set_from_the_sign
VOID|order=endpoint_undefined,unit_odd|endpoint_undefined=either_endpoint_quarter_absent_or_its_cell_empty_or_not_numeric|unit_odd=any_numeric_cell_of_the_used_current_column_outside_-20..40|a_VOID_is_not_a_FAIL|a_VOID_row_carries_label_free_columns_void_reason,_a_sign_only_if_stat_is_defined_(else_none)_and_spf_direction=none
HALT|exit_4_only_for_structural_layout_faults:_a_missing_sheet_or_required_column,_duplicate_or_non-consecutive_quarter_keys,_row_counts_other_than_74_(through_Q1_2020)_and_25_(CFO_SP500)|nothing_is_registered_after_a_halt
PIN|source=Q3_2026_results_page_read_by_the_supervisor_on_1_Nov_2026|CUR12_2026Q2=7.8|CUR12_2026Q3=7.9|CUR10_2026Q2=9.7|CUR10_2026Q3=9.6|MATCH=abs(workbook-pin)<=0.05_for_all_four|NEAR=any_difference_above_0.05_and_no_unit_error_(a_WARN,_the_run_continues,_pins=near_is_written)|UNIT_ERROR=any_pin_off_by_a_factor_of_5_or_more_(workbook/pin>=5_or_<=0.2)|UNIT_ERROR=the_full_stage_halts_with_exit_5_before_any_registered_row_is_written|the_pins_are_never_used_in_a_statistic_and_do_not_reach_the_window
E1|horizon=10y|window=2024Q1..2026Q1|series=CUR10|registered=stat,sign|described=spf_direction|blind=full|mandatory=yes|order=VOID,sign
E2|horizon=12m|window=2024Q1..2026Q1|series=CUR12|registered=stat,sign|blind=full|mandatory=no|use=README_only|order=VOID,sign
```

**The one hash.** The convention: the sha256 of the **interior of the fence above** (the lines between the two ``` lines, UTF-8, LF line endings, with a final LF after the last line, nothing else). Value:
**`2324862de97a98ee2b6b9de9576b0a3c43d7e3042b24289d5d3b97f05d2b230a`** (2697 bytes, 11 lines). `registered.csv` carries it in `prereg_sha256`, and M29 holds its own literal copy. There is no other hash in this spec (R1-9): the former source/layout hash, the
header-allowlist hash and the M29 constant for them are cut. The supervisor verifies this hash before the build.

**In words.** The statistic is the later quarter's cell minus the earlier's after each is rounded to 6 decimals, in points. **Sign:** RISE if at least +0.10, FALL if at most -0.10, ZERO if inside. **`spf_direction`** (E1,
described): the SPF rose by 0.1543 point, a RISE under the same rule; SAME if the CFO sign is RISE, OPPOSITE if FALL, FLAT if ZERO, `none` if VOID, `na` for E2. **VOID**, tested first and in order: `endpoint_undefined`,
`unit_odd`; a VOID is not a FAIL. **E1 is mandatory.**

### 4.7 Other rules (not hashed; the script holds them as code and the selftest tests them)

- **Source:** `https://www.richmondfed.org/-/media/RichmondFedOrg/research/national_economy/cfo_survey/current_historical_cfo_data.xlsx`, host `www.richmondfed.org`, one request per fetch run. Scouting values (1 Nov): HTTP 200,
  188,861 bytes, sha256 as in R1. For the registering vintage a different sha256 is a **FAIL** (it is the supervisor's input); for later vintages a different size or sha256 is a WARN.
- **Layout (HALT, exit 4):** sheets `through_Q1_2020`, `through_Q1_2020_dictionary`, `CFO_SP500`, `from_Q2_2020on_dictionary`, `CFO_survey_dates`; required columns `sp_10_exp`, `sp_1_exp`, `sp_10yrexp_2`,
  `sp_12moexp_2` and the key columns; 74 and 25 rows; unique, consecutive keys 2001Q4-2020Q1 and 2020Q3-2026Q3. The Duke empties (2019Q1, 2020Q1) differing, or a gap in a current `_2` column, is a WARN (and a VOID if it hits an
  endpoint), not a halt.
- **Described Duke range:** the windows of 2.2; min and max of the defined changes; n nominal 65, defined 63 expected; a different count is reported (WARN). Nothing from the current series enters it.
- **P-S (supersede).** A bug found after registration: the old registered row is kept and marked `superseded = yes`, the corrected row is added with the next `version`, both appear in the README; only the supervisor runs a
  registering build.

## 5. Outputs

**Script `bin/cfo_equity_expectations.py`.** Modes `fetch` (supervisor only), `build --vintage YYYYMMDD --stage pre|dry|full [--out DIR] [--registering]` (offline; `dry` requires `--out`), `selftest` (synthetic, no network, under
30 s). Committed in `data/cfo_equity_expectations/`: `registered.csv`, `yardstick.csv`, `checks.csv` and README.md; local and gitignored: `path.csv`. In each `data/vintages/cfo_survey/<YYYYMMDD>/`: `MANIFEST.csv` only. Each CSV
begins with one `# source:` line.

**Header allowlist, canonical text** (not hashed). One line per file, `<name>:<headers comma-joined, no spaces>`, LF endings, in this order. **`bin/check.sh` holds its own literal copy of these four lines** and never reads
them from the script. M29 skips the `# source:` line.

```
registered.csv:statement_id,version,superseded,horizon,series,vintage,workbook_sha256,start_quarter,end_quarter,exp_start,exp_end,stat_pp,sign,void_reason,blind,pins,spf_stat_pp,spf_direction,prereg_sha256
path.csv:era,horizon,quarter,exp,status,survey_open,survey_close
yardstick.csv:yardstick,horizon,first_end_quarter,last_end_quarter,n_nominal,n_defined,min_change_pp,max_change_pp,max_disjoint_spans
checks.csv:check_id,description,expected,observed,status
```

**Allowed values.** `statement_id` in {E1, E2}; `version` a positive integer; `superseded` in {no, yes}; `horizon` in {10y, 12m}; `series` in {CUR10, CUR12}; `sign` in {RISE, FALL, ZERO, none} (`none` only on a VOID row whose
statistic is undefined); `void_reason` in {none, endpoint_undefined, unit_odd}; `blind` in {full, partial}; `pins` in {match, near}; `spf_stat_pp` 0.1543 for E1, empty for E2; `spf_direction` in {SAME, OPPOSITE, FLAT, none, na}
(described, outside the hashed block); `era` (path.csv) in {duke, current}; `status` (path.csv) in {ok, empty} and for a Duke row it covers the `exp` cell only; `survey_open` and `survey_close` filled for current quarters only;
`yardstick` in {Y10, Y12, YC10, YC12}; `status` (checks.csv) in {PASS, WARN, FAIL, INFO}; quarters are `YYYYQn`; `workbook_sha256` and `prereg_sha256` 64 hex digits. A VOID row has an empty `stat_pp` and empty endpoint values
only where the void reason is `endpoint_undefined`. Keys unique: `registered.csv` (statement_id, version); `path.csv` (era, horizon, quarter); `yardstick.csv` (yardstick); `checks.csv` (check_id). **No output carries
HELD, FALSIFIED, PROVEN, CAUSED, REFUTED or MATERIAL.** `path.csv` holds the four series used (DUKE10, DUKE12, CUR10, CUR12; an empty cell is `status = empty` with an empty value, never 0); expected rows: Duke 74 x 2 = 148,
current 25 x 2 = 50, **198 in all**. `yardstick.csv` has **4** rows (Y10 and Y12: first end 2004Q1, last 2020Q1, 65 nominal, 63 defined, `max_disjoint_spans` 8; YC10 and YC12: 2022Q3 to 2026Q3, 17 nominal, 16 defined, 3).
`registered.csv`: one non-superseded row for E1 and one for E2.

- **`README.md`** (generated; the wording guard scans it), plain words, in this order: (1) the credit line and two opening sentences: what was measured (the CFO Survey's mean expected S&P 500 return, 10-year and 12-month,
  Q1 2024 to Q1 2026, in the 1 November 2026 vintage) and the E1 result (the two endpoint values, the signed change to two decimals, the sign, the SPF's 0.15, `spf_direction`, `blind`); (2) R-A; (3) R-B, R-C and R-D;
  (4) E2 in one sentence; (5) the zone as a convention, not a noise bound, and that sampling noise is not published (N about 340-370 per quarter); (6) the described Duke range with n and "at most eight disjoint spans", and
  YC; (7) what was known before the build (2.4) and the pins' status (they do not reach the window; the annual revision touches 2024Q1); (8) the unknowns: the 2.5%/5% winsorisation conflict (T3), the filter (T10);
  (9) the CFO field dates of 2024Q1 and 2026Q1 beside the SPF deadlines 6 Feb 2024 and 2 Mar 2026; (10) the dictionary lines printed verbatim; (11) coverage: counts and empties; (12) any superseded row; (13) a column
  dictionary glossing "expected return", "mean", "percentage point", "vintage", "winsorized"; (14) citations: the workbook URL and date, the credit line, C-082, Greenwood and Shleifer (2014).

## 6. Leak and integrity rules

1. Committed: in `data/cfo_equity_expectations/` only `registered.csv`, `yardstick.csv`, `checks.csv` and README.md; in each vintage folder only `MANIFEST.csv`; never `path.csv`, an `.xlsx`, `.xls`, `.zip`, `.json`,
   `.html` or STOP file (R1-15). The dry stage writes only outside these folders.
2. No local path (`/Users/`, `/private/`, `~/`), no `@`, no name, e-mail or contact in any written file or in the request's headers.
3. **Blind order.** No human or agent opens the workbook, `path.csv` or `yardstick.csv` before the registering build has run once. After it, the first reading is of `registered.csv`.
4. **Attack parcels carry the blind rule.** Any outside review of the results must forbid computing a result from a public table or from the workbook before the labels are fixed.
5. **No premium, no yield.** The script reads no Treasury or yield series and no output column derives from one.

## 7. Selftests (synthetic only; each guard applies its own mutant, and an uncaught mutant fails the selftest; fixtures are two-sided)

The wording guard pastes the two G14 patterns of the g14 spec (`CAUSAL_RX` and `EXTRA_RX`, both compiled with `re.I`, exactly as in `_research/2026-10-30-Collateral-Reuse-History-Spec.md` section 7), and adds
`\bsince\s+(?:19|20)\d\d\b`, `\b(?:highest|lowest|record|peak|trough)\b`, `\bcomparable\b`, `\bunusual\b`, `\b(?:dis)?agrees?\b` and `\bconfirm\w*` to the second. A fixture workbook is generated in memory with `zipfile`.
Cut to the guards that the five M29 checks and the sign, VOID, rounding and halting rules need (R1-10).

| Guard | Protects | Mutant that must be caught |
|---|---|---|
| G1 parsing and rounding | R7, R8 | a value read through float; an empty cell read as 0; a text cell accepted as numeric; a formula cell with no cached value accepted; each cell not rounded to 6 decimals before the difference; the difference rounded again; a cell of 0.0999995 rounded wrongly (half-even to 6 decimals gives 0.100000) |
| G2 layout and keys | HALT | a missing sheet or required column, 73 or 75 Duke rows, 24 or 26 current rows, a duplicate quarter, a non-consecutive quarter, "2020Q3" parsed as 2020Q2: each exit 4 with nothing registered; a Duke empty at 2018Q4, or an empty current `_2` cell, wrongly halting instead of WARN or VOID |
| G3 sign | 4.6 `SIGN` | **+0.0999, +0.1000, -0.0999, -0.1000 points give ZERO, RISE, ZERO, FALL**; cells 9.6 and 9.7000000000000002 (binary noise) giving RISE exactly as 0.1000 does; the sign taken from anything but the difference |
| G4 VOID | 4.6 `VOID` | an empty endpoint writing FAIL instead of a VOID row; the order other than endpoint_undefined, unit_odd (a fixture with an empty endpoint and an out-of-bound cell reports `endpoint_undefined`); -20.0001 and 40.0001 not `unit_odd`, -20 and 40 flagged; a sign written on an `endpoint_undefined` row; `spf_direction` other than `none` on a VOID row |
| G5 direction | 4.6 `DIRECTION` | RISE gives SAME, FALL OPPOSITE, ZERO FLAT; the words AGREES or DISAGREES written anywhere; E2 given anything but `na`; the SPF value read from a file; SPF stat other than 0.1543 |
| G6 pins | 4.6 `PIN` | the dry fixture's four pin values give MATCH; +0.05 MATCH and +0.0501 NEAR with a WARN and no halt; a pin off by a factor of 5 (workbook/pin = 5, and 0.2) UNIT_ERROR with exit 5 and no `registered.csv`; a fraction (0.096 for 9.6) UNIT_ERROR; NEAR not writing `pins = near`; a pin used inside a statistic |
| G7 windows and break | 2.2, T1 | q-8 found by row position across a deleted row; end quarters **2003Q4 (out), 2004Q1 (in), 2020Q1 (in), 2020Q2 (out)**; n nominal other than 65 and defined other than 63 on the full fixture; YC with end quarters 2022Q2 (out), 2022Q3 (in), 2026Q3 (in), 17 nominal and 16 defined; a window from 2020Q1 to 2020Q3; a Duke level subtracted from a current level; the registered window left in YC; a current value entering the Duke range |
| G8 registered write-once | R4, P-S | `registered.csv` rewritten by a second vintage; a repeat build not byte-identical; a supersede that deletes the old row instead of marking it `superseded = yes`; a second non-superseded row for E1; the `prereg_sha256` differing from the hash of the 4.6 block as the convention defines it (the selftest recomputes it from the constants); a constant edited so the build does not refuse |
| G9 wording | R6 | the patterns applied to README.md: the template passes; "expectations rose because of the rally", "a significant rise", "the highest since 2001", "the surveys agree", "comparable two-year changes", "an unusual rise" and "driven by" each fail; a README that lacks R-A, R-B, R-C or R-D verbatim fails; a banned verdict word fails |
| G10 fetch safety | R1-R3 | a request to any host but `www.richmondfed.org`; a second request in one run; a redirect followed or retried; a 3xx writing STOP (must be FAIL, exit 3, no STOP); a User-Agent holding `@`, `http` or a digit-dotted address; a cached body for today's date re-requested; 403, 429, 500, an empty body, an HTML body and a non-zip 200 each write STOP with five fields; 49,999 and 2,000,001 bytes write STOP and 50,000 and 2,000,000 do not; a planted `STOP_cfo` blocks the request (exit 2); a timeout exits 3 and writes no STOP |
| G11 stages | 3.2-3.4 | a `pre` that converts an S&P cell to a number, prints one or writes one to any file; `--stage dry` without `--out`, writing under `data/`, or writing SYNTHETIC outside the `# source:` line; `--stage full` registering without `--registering`; a build mixing two vintages |
| G12 outputs and leak | 5, 6 | an extra or renamed column; `# source:` compared as a header; a fifth CSV; a duplicate key; `path.csv` written in a committed list; on a planted folder an `.xlsx`, a `.json`, a `/Users/` path or an `@` is reported; the clean folder passes; a committed file without the credit line |

## 8. Pinned checks (`checks.csv`)

Identifiers are stable.

- **C01 Workbook (FAIL):** a valid zip with `xl/workbook.xml`; its bytes and sha256 equal the `MANIFEST.csv` row; for the registering vintage they equal the scouting values (FAIL otherwise); for later vintages WARN.
- **C02 Layout (FAIL, HALT):** the five sheets, the required columns, 74 Duke rows and 25 current rows, unique consecutive keys, 2020Q2 absent.
- **C03 Duke empties and current completeness (WARN):** `sp_10_exp` and `sp_1_exp` empty exactly at 2019Q1 and 2020Q1 and numeric at the other 72 quarters; `sp_10yrexp_2` and `sp_12moexp_2` numeric at all 25.
- **C04 Pins (full stage; PASS on MATCH, WARN on NEAR, FAIL with exit 5 on UNIT_ERROR):** `observed` shows each workbook value beside its pin.
- **C05 Units (VOID, not FAIL):** every numeric cell of the two current `_2` columns lies in -20 to 40; a breach is reported and writes VOID `unit_odd`.
- **C06 Described-range counts (WARN):** 65 and 65 nominal, 63 and 63 defined for Y10 and Y12; 17 and 16 for YC.
- **C07 Hash (FAIL):** the constants reproduce the 4.6 hash; `prereg_sha256` in `registered.csv` equals it.
- **C08 Recompute (FAIL):** `stat_pp` equals the difference of the rounded `exp_start` and `exp_end` (and, where `path.csv` is present, of its cells); `yardstick.csv` min, max and n equal the windows recomputed from `path.csv`.
- **C09 Blind order (FAIL):** `pre` printed and wrote no S&P value; the dry stage wrote nothing under `data/`.
- **C10 No cross-break (FAIL):** every window of the described ranges lies within one era (Duke: start >= 2002Q1, end <= 2020Q1; YC: start >= 2020Q3); every registered window is inside 2020Q3-2026Q3.
- **C11 Field dates (INFO):** the open and close dates of 2024Q1 and 2026Q1.
- **C12 Revision between vintages (INFO):** for a vintage after the registering one, the window values and `stat_pp` against the registered row.
- **C13 Dictionary lines (INFO):** the lines for `sp_10_low`, `sp_10_exp`, `sp_10_high`, `sp_1_low`, `sp_1_exp`, `sp_1_high` and the S&P block of the current dictionary, verbatim.

### 8.1 M29 (specification for `bin/check.sh`; warn-only, function `cfo_leak_check`, called beside M28 in `--all`)

M29 types its own copy of the four allowlist lines and of the 4.6 hash (`PREREG_SHA`), never reading them from the script, and takes `CFO_DIR` and `CFO_VDIR` overrides. It prints at least one fail line per fault and a pass
line if none. Four checks (R1-10) and the leak rule of R1-15:
1. **Registered pin:** `registered.csv`'s `prereg_sha256` equals `PREREG_SHA`; a variable `REG_SHA` (empty at landing) holds the sha256 of `registered.csv` that the supervisor fills in after reading the registering build; once
   non-empty, a file that hashes differently is a fail line (a supersede changes it by design: the supervisor updates the pin in the same commit). Empty prints an INFO line.
2. **Headers:** each CSV's first non-`# source:` line equals its allowlist line.
3. **Required sentences:** R-A, R-B, R-C and R-D appear verbatim (`grep -F`) in README.md once it exists.
4. **No level across 2020:** every `yardstick.csv` row has `first_end_quarter` and `last_end_quarter` inside one era (Y: from 2004Q1 to 2020Q1; YC: from 2022Q3); every registered `start_quarter` >= 2020Q3; README.md matches none
   of `since (19|20)\d\d`, `highest|lowest|record|peak|trough`.
5. **Leak (R1-15):** no `path.csv`, `.xlsx`, `.xls`, `.zip`, `.json`, `.html` or `STOP*` file in `data/cfo_equity_expectations/` or a vintage folder (outside the gitignored `raw/`), none tracked in git, and no `/Users/`, `/private/`
   or `@` in a committed file. (A fifth item beyond the ruling's four checks, added because R1-15 says M29's leak check enforces the local `path.csv`.)

## 9. Success criteria (each with the command and the number that would disprove it)

1. `python3 -I bin/cfo_equity_expectations.py selftest` prints G1 to G12, each `caught`, and exits 0. **Disproved by** any `SURVIVED`, a missing guard, or a non-zero exit.
2. **Registering input:** `shasum -a 256 data/vintages/cfo_survey/20261101/raw/current_historical_cfo_data.xlsx` prints `1b4e215c5626b741182b8a647c7a66d5c6d448616942d27138f18d37acec6bca`, and `MANIFEST.csv` has **1** row, status
   `supplied`. **Disproved by** any other hash. For a later vintage fetched by the script: **1** row, host `www.richmondfed.org`, status 200, no STOP file.
3. **Safe order:** `build --stage pre` then `build --stage dry --out <scratch>` first: `grep -c ',FAIL$'` on the pre and the dry `checks.csv` prints **0**; the pre output matches `[0-9]+\.[0-9]{2,}` on **0** lines outside the
   dictionary text and the dates; nothing under `data/` is written by the dry stage. Only then `build --stage full --registering`, after which `grep -c ',FAIL$' data/cfo_equity_expectations/checks.csv` prints **0**.
   **Disproved by** any FAIL, a decimal in the pre output, or a dry file under `data/`.
4. **Counts:** `path.csv` has **198** data rows (local), `yardstick.csv` **4**, `registered.csv` **2** (E1, E2, `version` 1, `superseded` no); Y10 and Y12 show n_nominal 65 and n_defined 63 (C06). **Disproved by** a different count
   without a named cause.
5. **Sums close:** a `python3 -I -c` over `registered.csv` and `path.csv` reproduces `stat_pp` from `exp_start` and `exp_end`, and `yardstick.csv` min, max and n from the windows, exactly (0.000001 point difference disproves).
6. **Byte-identical rebuild:** the sha256 of every file in `data/cfo_equity_expectations/` other than `registered.csv` is unchanged by a second `build` of the same vintage.
7. **Hash step:** extract the 4.6 fence interior from this spec (UTF-8, LF, final LF); its sha256 equals `SPEC_PREREG_SHA256`, M29's `PREREG_SHA` and `2324862de97a98ee2b6b9de9576b0a3c43d7e3042b24289d5d3b97f05d2b230a`.
8. **Tie-out by a different method (after registration):** a verifier re-reads four cells (2024Q1 and 2026Q1 of `sp_10yrexp_2` and `sp_12moexp_2`) and two Duke cells named by the supervisor with a spreadsheet program or
   another parser and compares them with `path.csv` (equal to 1e-9). **Disproved by** any difference.
9. **M29** (warn-only, in `bin/check.sh --all`; 8.1): on a scratch copy with a changed registered byte, a renamed header, a README missing R-B, a `yardstick.csv` row that crosses 2020 and a planted `path.csv` in the committed
   folder, M29 prints **at least one line per planted fault**; on the clean folder, a pass. Shown failing on the planted copy before it lands.
10. **Spec before data:** `git log --diff-filter=A --format=%cI -- _research/2026-11-01-CFO-Equity-Expectations-Spec.md` is earlier than the first `MANIFEST.csv` commit.
11. **Registration:** `grep -c '^E1,' data/cfo_equity_expectations/registered.csv` prints **1** and stays 1 after a second vintage with the E1 row byte-identical. **Disproved by** a second row without a stated supersede or a changed row.
12. **Registration of the work (CLAUDE.md "four places") and landing:** a CALENDAR trigger row (re-run after the Q4 2026 survey release, expected late December, date unconfirmed); a `RESEARCH_STATE.md` §5 row; a HANDOVER row; the
    `.gitignore` rules `data/vintages/cfo_survey/*/raw/`, `data/vintages/cfo_survey/STOP_cfo` and `data/cfo_equity_expectations/path.csv`; a REPRODUCE.md paragraph; a `data/THIRD_PARTY_MANIFEST.tsv` row for the workbook (the earlier
    row for an extract that is not present is the supervisor's to keep or retire); M29. No findings document and no page edit until `registered.csv` exists.

## 10. OPEN questions (only where a ruling is still needed)

Closed by the rulings: the earlier extract (R1-1); the agreement label and FLAT (R1-2); the zone and the 56 floor (R1-3, R1-4); the winsorisation and population unknowns (recorded as traps, R1-7); mean or median of `sp_10_exp` (the
dictionary, R1-11); republication (R1-15); the next-vintage date (R1-13); redirects (a 3xx is a FAIL, R1-9); the SPF deadlines (R1-15).

- **O-1 Count of disjoint spans.** R1-3 quotes "at most nine disjoint spans". With end quarters 2004Q1-2020Q1 and the two empty quarters (2019Q1, 2020Q1), the usable levels run 2002Q1 to 2019Q4, which is 71 steps and holds **eight**
  disjoint eight-quarter spans (a chain from 2002Q1 would end on the empty 2020Q1). I wrote eight in the body. *Option:* the supervisor confirms eight, or says how nine arises.
- **O-2 The population filter.** The page quotes firms that follow the stock market; whether the workbook's `_2` columns carry the same filter is not on the sheets read. The pins test the values at two quarters only, and the page
  sentence says "firms that follow the stock market" on that basis. *Option:* the supervisor reads the logged dictionary text (C13) before the registering build and rules if it contradicts the filter.
- **O-3 The 12-month comparator.** No SPF figure for the 12-month horizon is in the repository, so E2 has `spf_direction = na`. *Option:* the supervisor names one.
- **O-4 The User-Agent.** A generic User-Agent with no contact may be refused by the host on a later fetch. *Option:* the supervisor says whether to add a contact string held outside any file.
- **O-5 `spf_direction` for a small move.** SAME, OPPOSITE and FLAT are set from the sign under the 0.10 zone, so a CFO move of +0.05 reads FLAT though positive. The two-decimal number is printed beside it (R1-4). *Option:* write
  SAME for any positive move and keep the zone for the registered sign only.

## Supervisor rulings

*Appended here by the supervisor, newest last, before any data run; they override the body.*

### Round 1 (supervisor, 1 Nov 2026), after Grok's attack (`_research/2026-11-01-Grok-G15-CFO-Expectations-Attack.md`) and the Sonnet second review

Supervisor re-fetched the methods PDF Grok cited (the_cfo_survey_methods.pdf, 1 Nov): it says the S&P items use the "exact language used in the Global
Business Outlook Survey" and that "S&P 500 expectations data are winsorized at 2.5 and 97.5 percent". The Q3 2026 results page says "winsorized at 5%".
Both are recorded; neither is resolved.

- **R1-1 (reviewer defect 1; closes O-1).** The earlier extract `data/p5_third_measure/richmond_duke_cfo_survey_sp500_expected_return.csv` is NOT in the
  repository: not in git, not on disk; only its manifest row (`data/THIRD_PARTY_MANIFEST.tsv`) exists. No CFO value appears in any repository file. Blind is
  **full** for 2024Q1 and 2026Q1. Remove every sentence that treats the extract as present, the cross-check against it in criterion 9, and the 98-vs-99 aside.
- **R1-2 (Grok 1, 5; reviewer 5).** **The agreement label is removed as a registered verdict.** Registered rows carry the signed change and its sign only.
  A described column `spf_direction` (SAME, OPPOSITE, FLAT) is written beside the SPF's +0.1543 point, never as AGREES/DISAGREES, and the page sentence
  always gives both panels' changes as numbers, with both panels named, their dates (R1-8) and the CFO filter (R1-6). I keep the comparison itself, against
  Grok's "fatal": the §02 sentence claims a direction for "equity expectations", and whether a second panel moved the same way over the same quarters is the
  direct test of that claim; what Grok rightly kills is a binary verdict that hides the size, the panel and the dates.
- **R1-3 (Grok 2, 4, 6; reviewer 5).** **The Duke-era range is described, not registered,** and "comparable" is deleted. It is shown as min and max of the
  eight-quarter changes with n and "at most nine disjoint spans"; no rank out of n. The yardstick starts with end quarter **2004Q1** (start 2002Q1), so no
  window uses the 2001Q4 question form: 65 nominal, **63 defined**. The current-series variant (YC) stays described. With nothing registered against a
  yardstick, `thin_yardstick` leaves the VOID list.
- **R1-4 (Grok 3; overruled in part).** The sign zone stays at **+-0.10 point**: it is the one-decimal resolution the survey publishes and was fixed before
  data. The signed change is always printed to two decimals beside the SPF's 0.15, so a same-direction move under 0.10 is visible as a number. README states
  that the zone is a convention, not a noise bound, and that sampling noise is not published (N about 340-370 per quarter, from the pins) (reviewer 8;
  delete "no sampling error to quote").
- **R1-5 (reviewer 2, 6).** Halting set: only structural layout faults (sheets, columns, quarter keys, row counts) FAIL and stop (exit 4). An empty or
  non-numeric endpoint writes a VOID row `endpoint_undefined`; any numeric cell of a used column outside -20..40 writes VOID `unit_odd`; a VOID is not a
  FAIL. Rounding: **round each cell half-even to 6 decimals; stat = the exact Decimal difference of the rounded cells; no further rounding.**
- **R1-6 (Grok 7, 9; reviewer).** Wording. R-A: "...the expected return on the S&P 500 from a panel of financial decision-makers at US firms who say they
  follow the stock market...". R-D: "The respondents are financial decision-makers at firms (chief financial officers and others), not investors; the figures
  are stated expectations, not market prices." R-B: "Expectations of 12-month returns in this survey have been found to follow past returns (Greenwood and
  Shleifer 2014); for the 10-year horizon the evidence is weaker, so a change in either is not evidence about the discount rate." Every page sentence says
  "firms that follow the stock market".
- **R1-7 (Grok 8; reviewer 4).** The statistic is "the change in the 1 November 2026 vintage of the survey's revised historical file"; never "first
  published". Pins: **hard stop only on a unit error** (any pin off by a factor of 5 or more); a difference above 0.05 is NEAR with a WARN, not a halt. The
  README says the pins (2026Q2, 2026Q3) do not reach the window and that the annual revision touches 2024Q1. The 2.5% vs 5% winsorisation conflict (above)
  is a stated trap, not a halt.
- **R1-8 (Grok 7).** Dates. `path.csv` carries the CFO open and close dates from `CFO_survey_dates` for every current quarter; the README and the page put the
  SPF survey deadlines beside them. SPF deadlines 6 Feb 2024 and 2 Mar 2026 are RELAYED from Grok (spf-release-dates.txt); the supervisor re-reads them
  before the page uses them.
- **R1-9 (reviewer 3, 7, 11-13; cuts).**
  - The dry fixture plants the four pin values.
  - SYNTHETIC is shown only in the `# source:` line, and `--out` is added.
  - **One hash only,** of the 4.6 block as amended. The spec author applies these rulings to the body, re-hashes, and the supervisor verifies the hash before the build.
  - The 4.7 hash and the 4.7 constant in M29 are cut.
  - Add `data/vintages/cfo_survey/*/raw/` and `STOP_cfo` to `.gitignore` in the landing list.
  - `registered.csv` carries `exp_start` and `exp_end`.
  - A 3xx is FAIL with no STOP.
  - The supervisor's 1 Nov workbook (sha256 1b4e215c...6bca) is the registering input, dropped into `data/vintages/cfo_survey/20261101/raw/` by the supervisor; fetch mode remains for later vintages.
- **R1-10 (reviewer cuts).**
  - Medians and the 10% bands are cut.
  - Criterion 12 (cold reader) is cut.
  - M29 keeps four checks: the registered.csv hash pin after registration, the header allowlist, the R-A to R-D sentences, and no level compared across 2020. Criterion 8 reads "at least one line per planted fault".
  - Selftests are cut to the guards those checks and the sign/VOID/rounding rules need, each with a mutant.
  - E2 stays registered, README only.
- **R1-11 (O-2).** Whether `sp_10_exp` is a mean and annualised: the dictionary is the source; the builder prints the dictionary lines verbatim into the README. A
  described-only yardstick no longer needs a ruling.
- **R1-12 (O-4, licence).** The raw workbook is not committed (gitignored, archived in the private companion). `path.csv` (the four series used, with
  attribution) is committed only if the supervisor finds nothing in the Richmond Fed's website terms barring it; checked before landing.
- **R1-13 (O-9).** CALENDAR: re-run after the Q4 2026 survey release (expected late December, date unconfirmed), as a trigger row.
- **R1-14 (minor 15-20).** SPF stat 0.1543 at full precision; drop `excluded_window`; a Duke row's status covers the `exp` cell only; define "dictionary text"
  as the two dictionary sheets; "supervisor flag" = `--registering`; the yardstick span is written "2002-2020 (end quarters 2004Q1-2020Q1)".
- **R1-15 (supervisor checks, 1 Nov; settles R1-8 and R1-12).** SPF deadlines re-read by the supervisor in spf-release-dates.txt: 2024 Q1 "2/6/24", 2026 Q1
  "3/2/26**" (delayed by a government shutdown); R1-8's dates are confirmed. Richmond Fed terms (/terms_and_conditions, read 1 Nov): reproduction is permitted
  if "not for the purpose of private and/or commercial gain" and credited; "republication or distribution" otherwise needs written permission. Ruling, on the
  ICE precedent (E-025, derived statistics only, non-commercial): **commit derived statistics only** (registered changes with their two endpoint values, the
  described yardstick min, max and n, the YC summary), each file crediting "The CFO Survey (Duke Fuqua School of Business, Federal Reserve Banks of Richmond
  and Atlanta)". **`path.csv` (the full quarterly series) is local and gitignored**, like `data/vintages/cot_prices/derived/`; M29's leak check enforces it.

### Round 2 (supervisor, 1 Nov 2026), after the amendment

- **R2-1 (O-1).** Eight disjoint spans is right: the usable levels 2002Q1-2019Q4 hold eight non-overlapping eight-quarter spans; the round-1 "nine" was the
  supervisor's error. The body stands.
- **R2-2 (O-2).** Whether the workbook's `_2` columns carry the "follow the stock market" filter is not stated in the workbook; it stays a stated trap. The
  page sentence names the filter as the results page states it, and the README says the workbook does not state it.
- **R2-3 (O-3, O-5).** Accepted as written: E2 has no SPF comparator; a positive move under 0.10 reads FLAT in `spf_direction` and is printed as a number.
- **R2-4 (O-4).** A refused later fetch is a STOP to report, never routed around; no contact is ever declared.
- **Supervisor verification.** The 4.6 block's sha256 was re-derived by the supervisor from this file: `2324862de97a98ee2b6b9de9576b0a3c43d7e3042b24289d5d3b97f05d2b230a`
  (2697 bytes, 11 lines). Round 2 changes no registered text.

## Rulings round 3 (supervisor, 1 Nov 2026, after the registering build and the independent verification)

The registering build ran on the 1 Nov vintage: E1 +0.135778 (RISE, spf_direction SAME), E2 -0.161693 (FALL), pins match on all four. An independent verifier re-derived every
number with its own parser (both statements, the four pins, all four yardstick rows, all 198 path rows) and found no mismatch. It found two wording defects in README.md.

- **R3-1.** The current-dictionary lines carried a "[section: ...]" tag taken from the last single-text row above them, which was a bucket label of the GDP-probability block
  ("16.0% or more"), not the S&P block's header. The tag is removed; the verbatim lines are unchanged.
- **R3-2.** The E1 sentence asserted "among firms that follow the stock market"; the workbook does not state that filter (O-2, T10). It now says the series is the one whose recent
  values the results pages give for that population (the four pins match), and points at "What is not known". R-A is fixed text from before the data and is left as written.
- **R3-3.** The verifier doubted "in this survey" in R-B. Overruled: Greenwood and Shleifer (2014) include the Graham-Harvey CFO survey among their series; R-B is fixed text.
- **R3-4.** Nothing had been committed, so instead of `--supersede` the first outputs were moved aside and the registering build re-run. registered.csv, yardstick.csv and path.csv
  are byte-identical to the first run (`cmp`); only README.md and the C13 line of checks.csv changed. REG_SHA in M29 is the sha256 of that registered.csv.
- **R3-5.** The older manifest row for `data/p5_third_measure/richmond_duke_cfo_survey_sp500_expected_return.csv` describes a file that is in neither git nor this disk (R1-1). It is
  left in place as a record and is not used by this build.
