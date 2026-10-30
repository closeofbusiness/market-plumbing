# Sources: collateral re-use history

## Source

US Securities and Exchange Commission, EDGAR XBRL API (companyconcept) on data.sec.gov, vintage 20261030. US government works (17 U.S.C. 105). Caption pins: company label linkbase of the filing (wording only), read by the supervisor on 2026-10-30; the file is captions_pin.csv.

## Requests (data.sec.gov, vintage 20261030)

| URL | date (UTC) | HTTP status |
|---|---|---|
| https://data.sec.gov/api/xbrl/companyconcept/CIK0000019617/us-gaap/FairValueOfSecuritiesReceivedAsCollateralThatHaveBeenResoldOrRepledged.json | 2026-10-30 | 200 |
| https://data.sec.gov/api/xbrl/companyconcept/CIK0000019617/us-gaap/FairValueOfSecuritiesReceivedAsCollateralThatCanBeResoldOrRepledged.json | 2026-10-30 | 200 |
| https://data.sec.gov/api/xbrl/companyconcept/CIK0000886982/us-gaap/FairValueOfSecuritiesReceivedAsCollateralThatHaveBeenResoldOrRepledged.json | 2026-10-30 | 200 |
| https://data.sec.gov/api/xbrl/companyconcept/CIK0000886982/us-gaap/FairValueOfSecuritiesReceivedAsCollateralThatCanBeResoldOrRepledged.json | 2026-10-30 | 200 |
| https://data.sec.gov/api/xbrl/companyconcept/CIK0000093751/us-gaap/FairValueOfSecuritiesReceivedAsCollateralThatHaveBeenResoldOrRepledged.json | 2026-10-30 | 200 |
| https://data.sec.gov/api/xbrl/companyconcept/CIK0000093751/us-gaap/FairValueOfSecuritiesReceivedAsCollateralThatCanBeResoldOrRepledged.json | 2026-10-30 | 200 |
| https://data.sec.gov/api/xbrl/companyconcept/CIK0000072971/us-gaap/FairValueOfSecuritiesReceivedAsCollateralThatHaveBeenResoldOrRepledged.json | 2026-10-30 | 200 |
| https://data.sec.gov/api/xbrl/companyconcept/CIK0000072971/us-gaap/FairValueOfSecuritiesReceivedAsCollateralThatCanBeResoldOrRepledged.json | 2026-10-30 | 200 |

## Specification and rules

The specification is `_research/2026-10-30-Collateral-Reuse-History-Spec.md`, committed at ccacee1 with the supervisor's rulings of rounds 1 and 2 and the caption pins, before any value was read. The own-filing rule (P8): the primary value of a quarter-end is a fact of the original 10-K or 10-Q of that period, in which the end equals the end implied by the filing's own fiscal year and period, the filing date is 0 to 100 days after the end, and the end is the latest end among that filing's facts for the tag; the numerator and the denominator must be facts of the same accession. First reported means that value; a later restated value appears only in revisions.csv and in the latest_filed basis.

## What was known before the build

| bank | date | re-pledged (bn) | permitted (bn) |
|---|---|---|---|
| JPM | 2017-12-31 | 775.3 | 968.8 |
| JPM | 2024-12-31 | 1,210.7 | 1,544.0 |
| JPM | 2025-09-30 | 1,439.9 | 1,829.9 |
| JPM | 2025-12-31 | 1,426.4 | 1,771.0 |
| JPM | 2026-06-30 | 1,741.8 | 2,181.4 |
| GS | 2017-12-31 | 599.6 | 764.0 |
| GS | 2024-12-31 | 912.863 | 1,038.740 |
| GS | 2025-12-31 | 1,119.825 | 1,312.079 |
| GS | 2026-06-30 | 1,265.704 | 1,431.870 |

Also known as shares: JPM 78.2% (Jun 2025) and 79.8% (Jun 2026), GS 85.2% and 88.4%; JPM 80.0% at 31 Dec 2017; the four-name share 80.4% at 31 Dec 2017; 77.8% at FY2019 and 79.2% at FY2025 for the four US dealers disclosing both legs; the four-bank 82.6% (Jun 2025) and 84.0% (Jun 2026); the six-bank 81.7% (Dec 2025) and 83.2% (Jun 2026). They enter the build only as tie-out pins.

## Builder decisions

1. Supervisor decision, 30 Oct 2026, after the pre stage on vintage 20261030 (metadata only, no values): State Street's first year-end, 2013-12-31, is in later filings only (comparative-only), like JPM's and GS's 2009-12-31. C01 expects 52 period-ends with 51 in own filing, and C02 expects own filing from 2014-03-31 with 2013-12-31 comparative-only. This corrects the supervisor's own pin in ruling R1-10; it touches no hashed block, and sens_stt starts at 2014-03-31 under P8.
2. In the pre stage a quarter is `ok` when it is present in one filing for both tags; conflict, unit_odd and ratio_gt_1 need values and are assigned from the dry stage on (R1-7, C11).
3. quarters.csv has a row for every calendar quarter-end from a bank's first to its last, so the absent 2010-03-31 appears with status missing_n; an off-calendar end gets a row with status off_calendar; if both tags are absent the status is missing_n, if only the denominator is absent missing_d.
4. Wells Fargo enters sens_wfc iff both tags have a 10-K or 10-Q period-end at every one of the 51 quarter-ends 2013-12-31..2026-06-30 (counts and dates only, P3); P8 then decides which dates are usable.
5. C01 counts period-ends up to 2026-06-30 for JPM and GS (up to 2026-09-30 for State Street), so a later vintage with a Q3 2026 filing does not fail it. concept_extract.csv lists the facts that end on or after 2009-12-31.
6. A VOID statement carries label VOID and a blank sign (the sign is tested after the VOID reasons); the statistic, the yardstick extremes, the rank and the gap are still written when defined.
7. gap_to_extreme = min(stat - min, max - stat) of the yardstick, unrounded and written to 6 decimals: positive or zero when the label is WITHIN, negative when it is outside.
8. rank = 1 + the number of yardstick members above the statistic; rank_of = members + 1; ties share the better rank.
9. mix_dominates keeps the 'mix and within nonzero' words of the hashed 4.6 text on top of the same sign and larger size (round-2 ruling O-1).
10. sens_latest takes, per tag, the fact with the latest filing date (ties to the largest accn); if the two tags' latest accessions differ the row's status is own_filing_lacks_tags (the nearest listed status).
11. A timeout is logged in vintages.csv as a row with status 0 so that every request is one row; the next successful request of the same path replaces it. It writes no STOP.
12. A q/q jump is judged only against the immediately preceding calendar quarter-end of the same basis when that row is ok; a missing neighbour gives no flag.
13. The caption-change exclusion applies to every sample that holds JPMorgan Chase (primary and the State Street, Wells Fargo, JPM-only, equal-weight and no-flag samples); the Goldman-only sample has none (variant d).
14. changes.csv writes level rows with an empty start_end and share_start_pct; role registered is used only for the primary sample on the own_filing basis; every sample and basis carries its own yardstick rows.
15. samples.csv flags are the union of the banks' flags; sens_eqw's share is the mean of the banks' ratios, so C05 and C08 recompute it that way and the other samples as sum N over sum D.
16. C08 recomputes registered rows only when the vintage in registered.csv is the vintage in headline.csv; a row from an earlier vintage is left alone (INFO).
17. The dry stage writes headline.csv (count_ statistics only) and checks.csv, to the folder given by --out; the checks it writes carry no value (C03 reports only that the pins are within tolerance).
18. SPEC_COMMIT is ccacee1, the commit that holds the spec, the rulings and captions_pin.csv.
19. The decomposition file has one row per bank and one ALL row; its window column is the two dates joined by two dots.
20. A fact without a val is treated as absent (never zero); a non-numeric val is a data error. Dollar values are quantized to whole dollars (half-even) when a bank-quarter row is made; the unit bounds are tested on the unrounded value.
21. Any bank (including Wells Fargo) whose file has a unit key other than exactly USD, or a fact key outside the P7 list, stops the build with a data error.
22. The tie-out pins use the primary own_filing rows; a pin for a date without a usable value is reported as a failure of C03.
23. registered.csv is written once, by the first full build; it is kept byte-identical afterwards. `build --stage full --supersede` is the P19 route: old rows are marked superseded = yes and the corrected rows are added with the next version.
24. --stage has no default; the stage must be named. The dry stage reads vintages.csv and registered.csv from the committed folder (--committed, default data/collateral_reuse) and writes only to --out, which may not be that folder.
25. The headline.csv sample column holds the sample a statistic belongs to; count statistics sit under `primary`; variants a to c sit under `primary` and variant d under `sens_gs`.
26. A full build in which any check FAILs writes checks.csv and nothing else (no registered.csv, no README), so a registered row can never come from a failed run; WARN and INFO rows do not block.
27. The State Street and Wells Fargo samples start their yardsticks at 2015-12-31 (P2); the spec's exclusion of the eight caption-spanning windows then leaves 9 members, below the n = 10 floor of P18, so their S3 and S1 are VOID on any data. This is the spec's arithmetic, not a defect.
28. The probes.csv verdict is counts_only when the file for both tags is absent (404), otherwise enters or does_not_enter, the same on both tag rows.
