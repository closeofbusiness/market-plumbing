# The fair-value share of collateral re-used at JPMorgan Chase and Goldman Sachs

This is the fair-value share of the collateral they may re-use that JPMorgan Chase and Goldman Sachs report having re-used, at every quarter-end from June 2010 to June 2026, as first reported in the original 10-Q or 10-K of each period (vintage 20261030).
Three statements were registered before any value was read; each has a sign (RISE, FALL or ZERO, the zone being 0.1 point) and a range label that are separate, and the label only says whether the change was unusual against the yardstick of earlier eight-quarter changes, never whether the share rose.

- Between December 2021 and December 2023 the share rose 1.462 points, inside the range of 2011-2019 two-year changes.
- Between December 2023 and December 2025 the share rose 2.572 points, inside the range of 2011-2019 two-year changes.
- On 31 December 2023 the level was 80.015%, 0.650 points below the 2017-2019 median of 80.665%, so the sign is FALL; the range label says it was inside the 2017-2019 range, so not unusual against that yardstick.

How to read the table that follows:

- **S3, S1, S2**: the three statements registered before any value was read. S3 is the change from December 2021 to December 2023, the years before the price rise (the 2024-26 rise in US equity prices, as the project overview at docs/index.html describes it); S1 is the change from December 2023 to December 2025; S2 is the level on 31 December 2023 against the levels of 2017-2019.
- **sign**: RISE if the change is at least 0.1 point up, FALL if at least 0.1 point down, otherwise ZERO; for S2 it is the sign of the level against the median of the 2017-2019 levels.
- **range label**: whether the change was unusual against the yardstick, the earlier two-year changes of 2011-2019. WITHIN_RANGE never means that the share did not rise.
- **rank**: the position of the statistic among the yardstick members plus itself; rank 1 is the largest, so 3 of 24 means two members are larger.
- **n in yardstick**: the number of earlier changes (for S2, earlier levels) the statistic is compared with.
- **blind**: full means no value for the dates involved was known to the author before the build; partial means some were (see What was known before the build).
- **VOID**: no statement can be made; the reason is given in the void reason column. recast, one of those reasons, means a bank later restated a value at one of the two dates by more than 1%.
- **C-135**: the project's correction C-135, in CORRECTIONS.md, which says a share at a date is not a speed.

| statement | window | sign | range label | statistic | yardstick lowest to highest | rank | n in yardstick | blind | void reason |
|---|---|---|---|---|---|---|---|---|---|
| S3 | 31 Dec 2021 to 31 Dec 2023 | RISE | WITHIN_RANGE | 1.462 points | -7.446 to 7.836 | 15 of 24 | 23 | full | none |
| S1 | 31 Dec 2023 to 31 Dec 2025 | RISE | WITHIN_RANGE | 2.572 points | -7.446 to 7.836 | 13 of 24 | 23 | partial | none |
| S2 | level on 31 Dec 2023 | FALL | LEVEL_WITHIN_RANGE | 80.015% | 78.907 to 82.532 | 10 of 13 | 12 | partial | none |

- **S3.** From 31 Dec 2021 to 31 Dec 2023 the fair-value share of collateral re-used at JPMorgan Chase and Goldman Sachs rose, by +1.462 points, inside the range of the comparable two-year changes in the 2011-2019 yardstick (-7.446 to 7.836 points). This is a share at a date for two banks, not a speed (C-135), and says nothing about prices or money.
- **S1.** From 31 Dec 2023 to 31 Dec 2025 the fair-value share of collateral re-used at JPMorgan Chase and Goldman Sachs rose, by +2.572 points, inside the range of the comparable two-year changes in the 2011-2019 yardstick (-7.446 to 7.836 points). This is a share at a date for two banks, not a speed (C-135), and says nothing about prices or money.
- **S2.** On 31 Dec 2023 the fair-value share was 80.015%, inside its 2017-2019 range (78.907% to 82.532%). That is 0.650 points below the 2017-2019 median of 80.665%, so the sign is FALL; the range label says the level was not unusual against 2017-2019. This is a share at a date for two banks, not a speed (C-135), and says nothing about prices or money.

S3 is the statement for the years before the price rise (blind: full). S1 covers the window of the price rise itself and ends before the first half of 2026 (blind: partial). S2 is a level against the 2017-2019 range (blind: partial). A WITHIN_RANGE label states the signed change and never means that the share did not rise.

## What this is not

A bank's re-pledged share is the part of the collateral it may re-use that it reports having re-used: it is a share at a date, not a speed, and nothing here says it moved any price or any flow of money.

The perimeter is two banks. The page (the project overview at docs/index.html) gives 81.7% (December 2025) and 83.2% (June 2026), which are the six-bank share of JPMorgan, Goldman, Morgan Stanley, Bank of America, BNY and Wells Fargo; the six-bank share before 2025 stays unmeasured, and this two-bank history is a separate object reported in a separate sentence.

Left out: a speed or chain length; prices; money; intraday or off-quarter re-use (the quarter-end note does not show it); the Treasury repo alone (the lines cover every collateral class, derivatives and prime brokerage included); the other banks. Both legs are fair values, so a price move in the collateral can move the share with no new re-use; this is why the statistic is called a fair-value share.

## The yardstick

The yardstick Y is the set of eight-quarter changes in the share (percentage points) that end between 31 Dec 2011 and 31 Dec 2019, with the share defined at both dates and the window not spanning the caption change below: 33 nominal, 31 defined, 8 excluded for the caption change, 23 members (23 expected; a statement is VOID below 20). The robustness yardstick YR (ends from 31 Dec 2013) has 17 members (17 expected; VOID below 14). The level yardstick YL is the share at the quarter-ends 31 Mar 2017 to 31 Dec 2019: 12 of 12 defined (VOID below 10).

The yardstick is thin: the usable levels run 2010-06-30 to 2016-12-31 (three disjoint spans) and 2017-03-31 to 2019-12-31 (one span), so it holds at most four independent draws. A simulation shows what chance alone would give: if the share moved at random with no change in behaviour (standard-normal quarterly increments, 200,000 replications, seed 14), a new change would exceed the yardstick's maximum about 11% of the time (roughly one in nine) and fall outside it on either side about 22% of the time; for the robustness yardstick the figures are 14% and 28%. A RISE_OUTSIDE_RANGE label would therefore still appear roughly one time in nine with no change in behaviour at all.

JPMorgan's numerator caption widened in the first quarter of 2017; windows that span that change are excluded from the yardstick.

## The path of the share

| quarter-end | two-bank share (%) | JPMorgan (%) | Goldman Sachs (%) |
|---|---|---|---|
| 2010-12-31 | 76.108 | 79.588 | 72.423 |
| 2011-12-31 | 71.091 | 69.505 | 72.979 |
| 2012-12-31 | 69.107 | 66.223 | 73.510 |
| 2013-12-31 | 74.424 | 74.790 | 73.987 |
| 2014-12-31 | 76.943 | 78.351 | 75.242 |
| 2015-12-31 | 77.762 | 77.609 | 77.941 |
| 2016-12-31 | 80.216 | 81.676 | 78.114 |
| 2017-12-31 | 79.344 | 80.027 | 78.479 |
| 2018-12-31 | 81.166 | 80.165 | 82.995 |
| 2019-12-31 | 80.203 | 78.012 | 84.451 |
| 2020-12-31 | 76.086 | 71.564 | 83.680 |
| 2021-12-31 | 78.553 | 75.511 | 82.786 |
| 2022-12-31 | 78.380 | 75.685 | 82.116 |
| 2023-12-31 | 80.015 | 75.374 | 86.050 |
| 2024-12-31 | 82.221 | 78.413 | 87.882 |
| 2025-12-31 | 82.587 | 80.542 | 85.347 |
| 2026-06-30 | 83.235 | 79.848 | 88.395 |

Every quarter-end is in samples.csv and quarters.csv. The split of each registered change into a within-bank part and a weight-shift part is in decomposition.csv. The split is exact: each bank's within part is the change in its own share times the average of its start and end weights, and its weight-shift part is the change in its weight times the average of its start and end shares (a Shapley split); the weights are each bank's permitted collateral over the two banks' total.

| statement | total (points) | within banks | weight shift | weight shift dominates |
|---|---|---|---|---|
| S3 | 1.462 | 1.313 | 0.149 | no |
| S1 | 2.572 | 2.643 | -0.071 | no |

## Sensitivities and variants (never registered; n is the number of earlier changes in the sample's own yardstick)

| sample | basis | S3 | S1 | S2 |
|---|---|---|---|---|
| primary | own_filing | RISE WITHIN_RANGE (n=23) | RISE WITHIN_RANGE (n=23) | FALL LEVEL_WITHIN_RANGE (n=12) |
| primary | latest_filed | RISE WITHIN_RANGE (n=24) | RISE WITHIN_RANGE (n=24) | FALL LEVEL_WITHIN_RANGE (n=12) |
| sens_stt | own_filing | - VOID (n=0) | - VOID (n=0) | - VOID (n=7) |
| sens_wfc | own_filing | - VOID (n=0) | - VOID (n=0) | - VOID (n=7) |
| sens_jpm | own_filing | FALL WITHIN_RANGE (n=23) | RISE WITHIN_RANGE (n=23) | FALL LEVEL_BELOW_RANGE (n=12) |
| sens_gs | own_filing | RISE WITHIN_RANGE (n=31) | FALL WITHIN_RANGE (n=31) | RISE LEVEL_ABOVE_RANGE (n=12) |
| sens_eqw | own_filing | RISE WITHIN_RANGE (n=23) | RISE WITHIN_RANGE (n=23) | FALL LEVEL_WITHIN_RANGE (n=12) |
| sens_noflag | own_filing | RISE WITHIN_RANGE (n=19) | RISE WITHIN_RANGE (n=19) | FALL LEVEL_WITHIN_RANGE (n=12) |

A sensitivity gives a different label from the primary for: S2 sens_jpm on own_filing, S2 sens_gs on own_filing. A sensitivity is VOID (too few earlier changes, or an undefined endpoint) for: S3 sens_stt on own_filing, S1 sens_stt on own_filing, S2 sens_stt on own_filing, S3 sens_wfc on own_filing, S1 sens_wfc on own_filing, S2 sens_wfc on own_filing.

The names: **primary** is the two banks together (sum of re-used over sum of permitted); **sens_jpm** and **sens_gs** are one bank alone; **sens_eqw** gives the two banks equal weight (the mean of their shares); **sens_noflag** drops every quarter flagged recast or jump; **sens_stt** adds State Street; **sens_wfc** adds State Street and Wells Fargo if its counts qualify. **own_filing** takes each value from the original 10-Q or 10-K of its period; **latest_filed** takes the latest filing that reports it.

Where a bank's own change differs in sign from the pooled change: over 2021-2023 JPMorgan's own share fell and Goldman's rose; over 2023-2025 JPMorgan's own share rose and Goldman's fell. The pooled change is not a statement about each bank.

Why sens_stt and sens_wfc are VOID for S3 and S1: State Street has 51 own-filing quarters (its first year-end, 2013-12-31, exists only as a comparative in later filings, a supervisor decision), 30 of them are usable and 21 fall outside the unit band of 1e9 to 1e13 dollars and are excluded, so its shares start in 2014. After the eight windows that span JPMorgan's caption change are removed, 0 earlier changes remain in their yardstick, fewer than the 10 the spec requires.

The unrestricted 2011-start yardstick (it keeps the windows that span the caption change) holds 31 windows; its S3 label is WITHIN_RANGE and its S1 label is WITHIN_RANGE. It gives the same range labels as the registered yardstick.

## Captions

The caption classes are the filers' own wording of each line, read from the company label linkbase: JN1 is JPMorgan's numerator "sold or repledged", JN2 its wider numerator "sold, repledged, delivered or otherwise used"; JD1 is JPMorgan's denominator, "permitted to be sold or repledged, delivered or otherwise used"; GN1 is Goldman's numerator "delivered or repledged" and GD1 its denominator "permitted to deliver or repledge". A statement is VOID if a class differs between its two dates.

| bank | 10-K for | line | class | wording |
|---|---|---|---|---|
| JPM | 2011 | N | JN1 | Assets accepted by the Firm as collateral that the Firm has sold or repledged |
| JPM | 2011 | D | JD1 | Assets accepted by the Firm as collateral that it could sell or repedge, deliver or otherwise use at fair value |
| JPM | 2013 | N | JN1 | Assets accepted by the Firm as collateral that the Firm has sold or repledged |
| JPM | 2013 | D | JD1 | Assets accepted by the Firm as collateral that it could sell or repedge, deliver or otherwise use at fair value |
| JPM | 2019 | N | JN2 | Collateral sold, repledged, delivered or otherwise used |
| JPM | 2019 | D | JD1 | Collateral permitted to be sold or repledged, delivered, or otherwise used |
| JPM | 2021 | N | JN2 | Collateral sold, repledged, delivered or otherwise used |
| JPM | 2021 | D | JD1 | Collateral permitted to be sold or repledged, delivered, or otherwise used |
| JPM | 2023 | N | JN2 | Collateral sold, repledged, delivered or otherwise used |
| JPM | 2023 | D | JD1 | Collateral permitted to be sold or repledged, delivered, or otherwise used |
| JPM | 2025 | N | JN2 | Collateral sold, repledged, delivered or otherwise used |
| JPM | 2025 | D | JD1 | Collateral permitted to be sold or repledged, delivered, or otherwise used |
| GS | 2011 | N | GN1 | Financial instruments received as collateral which the firm delivered or repledged |
| GS | 2011 | D | GD1 | Fair value of financial instruments received as collateral by the firm that it was permitted to deliver or repledge |
| GS | 2013 | N | GN1 | Financial instruments received as collateral which the firm delivered or repledged |
| GS | 2013 | D | GD1 | Fair value of financial instruments received as collateral by the firm that it was permitted to deliver or repledge |
| GS | 2019 | N | GN1 | Financial instruments at fair value received as collateral which the firm delivered or repledged |
| GS | 2019 | D | GD1 | Financial instruments at fair value received as collateral by the firm that it was permitted to deliver or repledge |
| GS | 2021 | N | GN1 | Financial instruments at fair value received as collateral which the firm delivered or repledged |
| GS | 2021 | D | GD1 | Financial instruments at fair value received as collateral by the firm that it was permitted to deliver or repledge |
| GS | 2023 | N | GN1 | Collateral that was delivered or repledged |
| GS | 2023 | D | GD1 | Collateral available to be delivered or repledged |
| GS | 2025 | N | GN1 | Collateral that was delivered or repledged |
| GS | 2025 | D | GD1 | Collateral available to be delivered or repledged |

The recast flag at 2016-12-31, per bank: JPM no, GS no.

## What was known before the build

The repository already held some filing-note values for these two banks (nine bank-date pairs, listed in SOURCES.md, and some shares). They shaped no choice of window, threshold, label or bank set, and they are used only as tie-out pins. The author also formed, without recording a figure, an impression that the two-bank share was in the low 80s percent at the end of 2024 and 2025. So S3 is blind in full, while S1 and S2 are blind in part: the `blind` column says which.

## Later filings

| bank | bank-quarter-tag rows | flagged recast (more than 1% apart) | rows with any difference |
|---|---|---|---|
| JPM | 132 | 2 | 5 |
| GS | 132 | 0 | 0 |
| STT | 104 | 2 | 2 |
| WFC | 134 | 2 | 4 |

recast: the latest-filed value differs from the first-reported one by more than 1% on either tag (a recast at an end of S1 or S3 voids that statement). jump: either tag moved by more than 30% from the previous quarter-end. amended: an amendment exists for the period. Flags are prompts to look; they remove nothing from the primary sample.

## Coverage

| bank | tag | role | period-ends | calendar | off calendar | own filing | first | last | quarters outside the unit band |
|---|---|---|---|---|---|---|---|---|---|
| JPM | N | primary | 66 | 66 | 0 | 65 | 2009-12-31 | 2026-06-30 | 0 |
| JPM | D | primary | 66 | 66 | 0 | 65 | 2009-12-31 | 2026-06-30 | 0 |
| GS | N | primary | 66 | 66 | 0 | 65 | 2009-12-31 | 2026-06-30 | 0 |
| GS | D | primary | 66 | 66 | 0 | 65 | 2009-12-31 | 2026-06-30 | 0 |
| STT | N | sens_stt | 52 | 52 | 0 | 51 | 2013-12-31 | 2026-09-30 | 21 |
| STT | D | sens_stt | 52 | 52 | 0 | 51 | 2013-12-31 | 2026-09-30 | 21 |
| WFC | N | sens_wfc | 67 | 67 | 0 | 65 | 2009-12-31 | 2026-09-30 | 0 |
| WFC | D | sens_wfc | 67 | 67 | 0 | 65 | 2009-12-31 | 2026-09-30 | 0 |

Expected: 66 period-ends and 65 in own filing for each primary bank and tag (2010-06-30 to 2026-06-30), 2010-03-31 absent, 2009-12-31 only a comparative, none off calendar. For State Street: 52 period-ends and 51 in own filing (2013-12-31 only a comparative, a supervisor decision), from 2014-03-31 on. A quarter outside the unit band (a value below 1e9 or above 1e13 dollars) is excluded from every sample.

## Columns

- **fair-value share**: the fair value of collateral reported as re-used divided by the fair value of collateral permitted to be re-used, in percent, summed over the banks of the sample.
- **permitted to be re-used**: collateral received that the bank is allowed to sell or repledge.
- **re-pledged**: the part it has sold, repledged, delivered or otherwise used, as the filing words it.
- **first reported**: the value in the original 10-Q or 10-K of that period, not a later restated one.
- **quarter-end**: 31 March, 30 June, 30 September or 31 December.
- **yardstick**: the earlier eight-quarter changes (2011-2019) against which a change is compared.
- **percentage point**: a difference between two percentages.
- **vintage**: the date the SEC files were read.

## Citation

US Securities and Exchange Commission, EDGAR XBRL API (companyconcept) on data.sec.gov, vintage 20261030. Caption pins: company label linkbase of the filing, read by the supervisor on 2026-10-30. Specification: _research/2026-10-30-Collateral-Reuse-History-Spec.md (commit ccacee1). See SOURCES.md.
