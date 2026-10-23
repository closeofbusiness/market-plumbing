# US-dollar international debt securities by type of borrower and borrower country (BIS)

This folder shows how many US dollars borrowers owe on bonds and short-term paper sold outside their home markets, split by type of borrower and by where the borrower is based. It measures amounts owed by issuers, not who holds the securities, and it does not show why the securities were issued or any effect on interest rates or the dollar.

Amounts are face value: the principal the issuer owes at maturity, not a market price. A security counts as international when at least one of its registration location, the law that governs it and its listing location lies outside the issuer's home country (BIS international debt securities overview); a dollar bond registered, governed and listed in its issuer's own country is outside these figures. Issuers are grouped by residence, the country where the issuer is incorporated; one memo series groups them by nationality, the country where the issuer's parent is headquartered, so a Cayman subsidiary of a US company is a non-US resident with US nationality. Central banks count inside the financial corporations (FIN).

The groups are: ALL (all countries including the United States); US (issuers resident in the United States); NON_US (ALL minus US (computed here)); ADV (advanced economies); EMDE (emerging market and developing economies); INTL_ORG (the residence group of international organisations, whose issuers are in the sector INTL_INST); US_NATIONALITY (issuers whose parent is headquartered in the United States, wherever the issuer is incorporated (memo, sector ALL only)). The groups overlap, so do not add them up: ALL contains both US and NON_US, ADV, EMDE and INTL_ORG are a second split of ALL, and the US-nationality total cuts across both.

The sectors are: ALL (all issuers); GOV (general government); FIN (financial corporations (the five parts below, central banks included)); FIN_PRIV_BANK (private banks); FIN_PUB_BANK (public banks); FIN_PRIV_OFI (private other financial institutions (OFI), the non-bank financial firms); FIN_PUB_OFI (public other financial institutions (OFI)); FIN_CENTRAL_BANK (central banks); NFC (non-financial corporations); INTL_INST (international institutions).

## The latest result

The data run to 2026-Q2. The pull (the download of the BIS data) is dated 2026-10-23, which is the vintage of every row; the latest BIS release on or before that date is dated 2026-09-14 (the BIS publishes "no later than" that date). An amount outstanding, or stock, is the face value owed at a quarter end; net issues are a flow, issues minus redemptions during the quarter. Amounts in this README are US$ billions (US$ millions divided by 1,000, one decimal); the csv files are in US$ millions. A blank is a value the BIS does not publish. A window named for a year, such as 2026 to the latest quarter, covers only the quarters reported so far.

**Outstanding at 2026-Q2, US$ billions**

| Sector | ALL | US | NON_US | ADV | EMDE | INTL_ORG |
|---|---|---|---|---|---|---|
| ALL | 16,274.3 | 1,952.5 | 14,321.8 | 12,527.3 | 2,894.8 | 852.3 |
| GOV | 1,870.3 | 2.0 | 1,868.3 | 304.4 | 1,565.8 | blank |
| FIN | 11,328.6 | 1,539.7 | 9,788.9 | 10,703.7 | 624.9 | blank |
| FIN_PRIV_BANK | 3,571.4 | 213.0 | 3,358.4 | 3,291.8 | 279.6 | blank |
| FIN_PUB_BANK | 171.7 | 0.1 | 171.6 | 120.4 | 51.3 | blank |
| FIN_PRIV_OFI | 6,931.7 | 1,253.3 | 5,678.4 | 6,735.0 | 196.7 | blank |
| FIN_PUB_OFI | 626.1 | 73.3 | 552.8 | 528.9 | 97.2 | blank |
| FIN_CENTRAL_BANK | 27.7 | blank | 27.7 | 27.6 | 0.2 | blank |
| NFC | 2,220.8 | 410.8 | 1,809.9 | 1,518.2 | 702.6 | blank |
| INTL_INST | 854.7 | blank | 854.7 | 1.0 | 1.4 | 852.3 |

**Outstanding at 2019-Q4, US$ billions**

| Sector | ALL | US | NON_US | ADV | EMDE | INTL_ORG |
|---|---|---|---|---|---|---|
| ALL | 11,586.7 | 1,453.4 | 10,133.3 | 8,986.8 | 2,021.6 | 578.3 |
| GOV | 1,187.9 | 3.5 | 1,184.4 | 209.7 | 978.2 | blank |
| FIN | 8,117.0 | 1,142.0 | 6,975.0 | 7,602.4 | 514.6 | blank |
| FIN_PRIV_BANK | 2,673.1 | 242.6 | 2,430.5 | 2,447.9 | 225.1 | blank |
| FIN_PUB_BANK | 311.4 | 0.1 | 311.3 | 242.0 | 69.4 | blank |
| FIN_PRIV_OFI | 4,544.6 | 852.7 | 3,692.0 | 4,402.2 | 142.4 | blank |
| FIN_PUB_OFI | 578.9 | 46.7 | 532.2 | 502.8 | 76.0 | blank |
| FIN_CENTRAL_BANK | 9.1 | blank | 9.1 | 7.4 | 1.7 | blank |
| NFC | 1,700.3 | 307.9 | 1,392.4 | 1,172.6 | 527.7 | blank |
| INTL_INST | 581.5 | blank | 581.5 | 2.2 | 1.1 | 578.3 |

**Net issues (issues minus redemptions), US$ billions, all sectors, by group and window**

| Group | 2024 | 2025 | 2026_to_2026-Q2 | 2024_to_2026-Q2 |
|---|---|---|---|---|
| ALL | 861.5 | 1,325.1 | 748.5 | 2,935.1 |
| US | 98.3 | 221.4 | 117.3 | 437.1 |
| NON_US | 763.2 | 1,103.7 | 631.2 | 2,498.0 |
| ADV | 681.8 | 1,029.8 | 585.4 | 2,296.9 |
| EMDE | 124.5 | 215.5 | 139.6 | 479.6 |
| INTL_ORG | 55.2 | 79.8 | 23.5 | 158.5 |
| US_NATIONALITY | 481.9 | 578.1 | 283.2 | 1,343.2 |

**Net issues, US$ billions, group ALL, by sector and window**

| Sector | 2024 | 2025 | 2026_to_2026-Q2 | 2024_to_2026-Q2 |
|---|---|---|---|---|
| ALL | 861.5 | 1,325.1 | 748.5 | 2,935.1 |
| GOV | 73.0 | 186.8 | 107.4 | 367.1 |
| FIN | 660.8 | 941.7 | 550.9 | 2,153.5 |
| FIN_PRIV_BANK | 146.5 | 218.0 | 248.4 | 613.0 |
| FIN_PUB_BANK | -17.0 | -20.1 | 0.2 | -36.9 |
| FIN_PRIV_OFI | 536.7 | 728.9 | 297.0 | 1,562.6 |
| FIN_PUB_OFI | -9.3 | 6.6 | 1.1 | -1.6 |
| FIN_CENTRAL_BANK | 4.0 | 8.3 | 4.2 | 16.4 |
| NFC | 73.3 | 118.5 | 67.2 | 259.0 |
| INTL_INST | 54.4 | 78.1 | 23.0 | 155.5 |

**Sector shares, percent.** Each share is the sector's outstanding divided by the same group's ALL-sector outstanding in the same quarter (denominator: the group's ALL-sector outstanding, so the shares of GOV, FIN, NFC and INTL_INST add to about 100 within a group, and the five FIN parts add to the FIN share).

| Sector | ALL 2019-Q4 | ALL 2026-Q2 | US 2019-Q4 | US 2026-Q2 | NON_US 2019-Q4 | NON_US 2026-Q2 |
|---|---|---|---|---|---|---|
| GOV | 10.25 | 11.49 | 0.24 | 0.10 | 11.69 | 13.04 |
| FIN | 70.05 | 69.61 | 78.57 | 78.86 | 68.83 | 68.35 |
| NFC | 14.67 | 13.65 | 21.19 | 21.04 | 13.74 | 12.64 |
| INTL_INST | 5.02 | 5.25 | blank | blank | 5.74 | 5.97 |
| FIN_PRIV_BANK | 23.07 | 21.94 | 16.69 | 10.91 | 23.99 | 23.45 |
| FIN_PUB_BANK | 2.69 | 1.05 | 0.00 | 0.00 | 3.07 | 1.20 |
| FIN_PRIV_OFI | 39.22 | 42.59 | 58.67 | 64.19 | 36.43 | 39.65 |
| FIN_PUB_OFI | 5.00 | 3.85 | 3.21 | 3.75 | 5.25 | 3.86 |
| FIN_CENTRAL_BANK | 0.08 | 0.17 | blank | blank | 0.09 | 0.19 |

**US residence and US nationality, two separate totals.** US-resident outstanding (issuer incorporated in the US), all sectors: US$ 1,453.4bn at 2019-Q4 and US$ 1,952.5bn at 2026-Q2. US-nationality outstanding (issuer's parent headquartered in the US), all sectors: US$ 2,754.6bn at 2019-Q4 and US$ 4,849.6bn at 2026-Q2. The difference between the two totals is only the net of two groups: issuers outside the US with a US parent (counted in the nationality total only) and issuers inside the US with a foreign parent (counted in the residence total only).

## Comparison with BIS CGFS Paper 65

Paper No 65 of the BIS Committee on the Global Financial System (CGFS), "US dollar funding: an international perspective" (June 2020), says in section 3.4 that about three fourths of the increase over the past five years in international US dollar funding was in marketable debt securities rather than bank lending (paraphrase). The paper's measure is global: it counts the international debt securities of every issuer, issuers in the United States included, and cross-border bank loans of all reporting countries including those in the United States (from the BIS locational banking statistics, LBS, which record banks' claims across borders by the counterparty's country), with loans between offices of the same bank (related offices) included. P1 to P4 therefore count borrowers everywhere, the United States included; N1 alone keeps securities of issuers outside the United States against loans to counterparties outside the United States. Here the window is 2014-Q4 to 2019-Q4, twenty quarters ending at the paper's data date. The share is the securities increase divided by the sum of the securities increase and the loan increase.

| Variant | Plain name | Window | Securities increase, US$ tn | Loan increase, US$ tn | Break sum, US$ bn | Break quarters | Share, % |
|---|---|---|---|---|---|---|---|
| P1 | The paper's measure: change in published stocks | 2014-Q4 to 2019-Q4 | 2.81 | 0.91 | 656.8 | 20 of 20 | 75.56 |
| P2 | The same, using BIS break-adjusted flows | 2014-Q4 to 2019-Q4 | 2.81 | 0.25 | 656.8 | 20 of 20 | 91.78 |
| P3 | Without loans between offices of the same bank | 2014-Q4 to 2019-Q4 | 2.81 | 0.22 | -39.4 | 20 of 20 | 92.63 |
| P4 | Window one quarter earlier | 2014-Q3 to 2019-Q3 | 2.76 | 0.28 | 437.2 | 20 of 20 | 90.69 |
| N1 | Borrowers outside the US only (not the paper's measure) | 2014-Q4 to 2019-Q4 | 2.85 | 1.12 | 648.2 | 20 of 20 | 71.85 |

A series break is a change in who reports or how they report, which moves a published stock without any new lending; the BIS flags such quarters, and its own flow series (adjusted for breaks and exchange rates) leaves them out. The break sum is the loan stock change minus the sum of the BIS break-adjusted flows over the same quarters: the part of the stock change that the adjusted flows do not count, mostly series breaks; break quarters are the quarters in the window in which a loan stock used is flagged as a series break. In P2 the loan increase is the sum of the adjusted flows, so P2's break sum is the stock change of P1 minus that sum. N1 is not the paper's measure: it keeps only issuers and borrowers outside the United States.

**Reading on this vintage: mixed.** The rule: `consistent` only if the P1 and P2 shares both lie inside 65–85%, `mixed` if one lies inside and the other outside, `not_consistent` if both lie outside, `undefined` if either is blank; P3, P4 and N1 are described without a reading. A `mixed` or `not_consistent` reading is reported as it stands. The reading rule was set after the reviewers had seen the P1 and P2 values; the earlier rule, which looked at P1 alone, would have read consistent.

P1 reproduces the paper's figure only on LBS stock changes, which contain BIS series breaks (657bn of 908bn here). On break-adjusted flows, without related offices, or with the window moved one quarter, the share is 91–93%, outside the band. 'Consistent' means one construction matches, not that the figure is robust.

## Blanks, derived series and flags

A blank cell means the BIS publishes no value for that series and quarter (some series start later, and a few never exist, such as a US central-bank series); it is never zero. NON_US is ALL minus US. It is blank when the ALL value is blank, or when a US series exists but that quarter is missing (`partial`). For the two sectors with no US series at all, FIN_CENTRAL_BANK and INTL_INST, the US value is taken as zero only in quarters where the US total equals the sum of its published sectors and the US financial total equals the sum of its published parts, each within 5 (US$ millions); those cells carry `us_series_absent`. The test is applied to each measure separately (outstanding, net issues): where the US values it needs are present but do not add up, the cells of that measure are blank with `us_sum_mismatch`; where a US value it needs is absent, they are blank with `us_value_absent`. `other_change_usd_m` is a residual, change minus net issues: it holds reclassifications, coverage changes and rounding, and it is not a measurement of any of them; for US-dollar debt there is no exchange-rate revaluation. The loan statistics' stocks carry series-break flags (20 of 20 quarters in P1's window), so a stock change includes breaks; the BIS-calculated flows adjust for breaks and exchange rates, and both are shown with the gap between them in dollars.

In 2026-Q2 the US government net-issue value is absent, so the NON_US net-issue cells of FIN_CENTRAL_BANK and INTL_INST are blank with `us_value_absent`, while their outstanding cells are filled.

## Columns

| File | Column | Meaning |
|---|---|---|
| quarterly.csv | quarter | Calendar quarter, YYYY-Qn, from 2014-Q3. |
| quarterly.csv | basis | residence (where the issuer is incorporated) or nationality (where its parent is headquartered). |
| quarterly.csv | issuer_group | ALL, US, NON_US, ADV, EMDE, INTL_ORG, or US_NATIONALITY; the groups overlap. |
| quarterly.csv | sector | ALL, GOV, FIN, the five FIN parts, NFC or INTL_INST. |
| quarterly.csv | outstanding_usd_m | Face value outstanding at quarter end, US$ millions. |
| quarterly.csv | net_issues_usd_m | Issues minus redemptions in the quarter, US$ millions. |
| quarterly.csv | change_in_outstanding_usd_m | Outstanding minus the previous quarter's outstanding; blank if either is blank. |
| quarterly.csv | other_change_usd_m | Change minus net issues: a residual, with no independent measurement. |
| quarterly.csv | status | ok, absent, partial, us_series_absent, us_value_absent or us_sum_mismatch (see Blanks). |
| quarterly.csv | derived | source (published by the BIS) or identity (computed here from published series). |
| quarterly.csv | vintage | Date of the pull folder the row was built from. |
| quarterly.csv | ids_release | Latest BIS international debt securities release date on or before the pull date. |
| shares.csv | share_pct | numerator_usd_m as a percentage of denominator_usd_m, two decimals. |
| shares.csv | numerator_usd_m / denominator_usd_m / denominator | The sector's outstanding, the same group's ALL-sector outstanding in the same quarter, and its label. |
| net_issues_windows.csv | window, first_quarter, last_quarter | 2024; 2025; 2026 to the latest quarter; 2024 to the latest quarter. |
| net_issues_windows.csv | quarters_n, quarters_blank | Quarters in the window; quarters in which net issues, change or other change is blank. |
| net_issues_windows.csv | net_issues_usd_m, change_in_outstanding_usd_m, other_change_usd_m | Sums over the window; blank if any quarter is blank. |
| net_issues_windows.csv | share_of_group_net_issues_pct / denominator | The sector's sum of net issues over the group's ALL-sector sum; blank when that sum is zero or negative. |
| cgfs_check.csv | variant, plain_name, definition | P1 to P4 and N1, with their plain names and definitions. |
| cgfs_check.csv | first_quarter, last_quarter | The two quarters whose levels are differenced (P2: the first quarter is the level before the first flow). |
| cgfs_check.csv | ids_change_usd_m, lbs_change_usd_m, lbs_measure | Securities increase and loan increase, and whether the loan figure is a stock difference or BIS break-adjusted flows. |
| cgfs_check.csv | lbs_flow_sum_usd_m, lbs_break_sum_usd_m, lbs_break_quarters | Sum of the BIS break-adjusted flows; stock change minus that sum; quarters flagged as series breaks. |
| cgfs_check.csv | ids_share_of_increase_pct, denominator, reading, note | Securities increase over the sum of the two increases; the sum; the reading under the rule in the comparison section; a note. |
| summary.csv | question .. blind | The descriptive questions Q1 to Q6, fixed in advance; blind is no where the reviewers or the author had already seen those values before the build, and yes otherwise. |
| revisions.csv | vintage_prev .. change_pct | Every cell that changed between two pulls, appended and never rewritten; one baseline row for the first pull. |
| registration_score.csv | all columns | A statement registered in advance (23 Oct 2026) about how far the BIS revises history at its next release, not about markets; PENDING until 2026-Q3 is in the file. |
| checks.csv | check_id .. status | Every check with its expected and observed text; PASS, FAIL, WARN or INFO. |
| fetch_log.csv | all columns | One row per request to stats.bis.org. |

Worked row (2019-Q4, group ALL, sector ALL): general government + financial corporations + non-financial corporations + international institutions = 1,187,905 + 8,116,957 + 1,700,325 + 581,517 = 11,586,704 US$ millions.

## Provenance

Source: Bank for International Settlements (BIS), international debt securities statistics and, for the comparison, locational banking statistics, retrieved 2026-10-23 from the BIS statistics service at stats.bis.org; the latest release on or before the last pull is dated 2026-09-14. The BIS terms of use apply to these figures, not this repository's CC BY licence; the BIS gives no warranty; this is not investment advice; and the BIS does not endorse this work. The request log, the label allowlist, the window reasoning and the build decisions are in [SOURCES.md](SOURCES.md).
