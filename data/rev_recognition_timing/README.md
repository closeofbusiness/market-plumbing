# Revenue-recognition timing and the growth in S&P 500 net income, fiscal 2023 to fiscal 2025 (SEC XBRL data)

This is a ceiling for the tagged balances under assumption A1, not an estimate: if every dollar by which a firm's contract balances moved beyond what its revenue growth would give is counted as profit, with no cost and no tax, the timing of revenue against billing in those balances is at most 11.01% of the change in their net income for the 274 non-financial firms (S1, label SHARE_10_TO_25: 10% to 25%), and at most 25.51% of the change in their net income if only the firms where the timing was positive are counted (S1P, label SHARE_ABOVE_25: above 25%). A change in contract assets or contract liabilities relative to revenue is a balance-sheet accrual: it shows when revenue was booked against billing, not why, and nothing here says it moved any price or any flow of money. These labels rest on a few firms: removing any one of Boeing Co (BA), Dell Technologies Inc. (DELL), General Electric Co (GE) and General Dynamics Corp (GD) takes S1 below 10%, 6 of the 13 samples give a different label, and the same-filing basis (each prior year as restated in the later report), added after the result was seen, gives 9.99%.

The numbers come from the SEC's structured filing data on data.sec.gov (company facts, submissions and frames), vintage 20261028 (the UTC date the download began). The rule (samples, tags and thresholds) was fixed in a specification committed on 28 October 2026 before any data were fetched. An independent check on 28 October 2026 recomputed all 274 firms from the raw SEC files and matched them to the dollar; it also supplied the same-filing sample, after the result was seen.

## What was measured

**The firms.** The 500 distinct SEC registrants behind the 503 tickers of the S&P 500 as this project's earlier tax work (workstream W3) holds them in `data/w3_tax/firm_tax_panel.csv`: the 2026 members, so firms that left the index are absent. Each registrant is identified by its CIK, the SEC's ten-digit Central Index Key. 98 are financial firms and are excluded; the primary sample is the 274 non-financial firms with every needed number stated, and they hold 62.6% of the 500 firms' fiscal 2025 net income (that denominator covers 455 of the 500: 45 state no fiscal 2025 NetIncomeLoss fact, 10 of them financial firms and 35 not).

**The measure.** A contract asset is revenue a firm has booked but cannot yet bill; a contract liability is billing or cash received before the revenue is booked (deferred revenue). N, the net contract position, is contract assets minus contract liabilities, and r is N divided by the year's revenue. If revenue grows, N would grow in step at last year's r; the excess accrual in a year is the part of the change in N beyond that: N this year minus last year's r times this year's revenue. A firm's T_i is its excess accrual in fiscal 2025 minus its excess accrual in fiscal 2023 (the base year), and T is the sum of the T_i over the firms. T in days is T divided by fiscal 2025 revenue times 365.

**S1 and S1P.** The change in net income is fiscal 2025 minus fiscal 2023, summed over the firms. S1 is the size of T as a share of that change; S1P is the sum of the positive T_i as a share of the same change, so no firm's offset is netted. A label sorts the share: SHARE_BELOW_10 (below 10%), SHARE_10_TO_25 (10% to 25% inclusive), SHARE_ABOVE_25 (above 25%), or VOID when fiscal 2023 net income is not positive or the change is below 2% of it. The thresholds, 10% and 25%, were fixed in advance by the project, are not calibrated, and were not moved after the placebo windows (earlier periods used as a yardstick, described below) were seen. Direction is reported beside the label: with_growth when T is above zero, against_growth when it is below.

**Fiscal years.** A firm's fiscal year Y is the year of its original 10-K whose report date lies from 1 April of Y to 31 March of Y+1, whatever label the firm gives it.

## What the number is

Two assumptions frame it. There is no A2: the first draft's second assumption, about the reference year, was dropped because that year's excess accrual is now measured. (A1) Every dollar of excess accrual is counted as profit, with no cost and no tax. Because booked revenue carries costs and tax in practice, only part of it reaches net income, so |T| is at least as large as the effect on net income and the share is a ceiling on size for the tagged balances, not an estimate of the effect. (A3) Timing in balances that are not tagged is invisible here. The SEC's company-facts feed carries only numbers tagged with the standard US accounting labels and not split by segment, product or other dimension; a balance reported only by segment (a dimensioned one), or under a company-made label outside the standard list (an extension), is absent.

N moves for ordinary explanations: milestone billing, contract mix, a large contract near year-end. Stock-funded acquisitions, spin-offs and other disposals, and currency translation can also move N with no change in recognition, and are not screened (sensitivities drop firms with large acquisitions or with discontinued-operations income). A large T is a reason to look, not a finding.

## What is left out

- **Trade receivables** are billed consideration awaiting cash: they measure collection, not recognition, and sit outside N (reported apart below).
- **Capitalized contract costs** can move profit with N unchanged; the measure ignores them (reported apart below).
- **Stock-funded acquisitions, spin-offs and currency translation** are not screened (see above).
- **Dimensioned and extension balances** are absent from the SEC's company-facts feed (A3).
- **Financial firms** (SIC 6000 to 6799) and firms with no SIC code are excluded; see the coverage section.

## The result and the sensitivities

Under A1, T is $26.1bn (0.86 days of revenue). The direction is with_growth: T is above zero, so the timing added to reported growth. Its size relative to revenue is inside the range of the placebo windows (the placebo windows, earlier periods used as a yardstick, are explained below).

By side, the contract-asset part of T is -$2.4bn and the contract-liability part is $28.5bn (the two add up to T): relative to revenue, contract liabilities (billing or cash received before revenue is booked) built up less in fiscal 2025 than in fiscal 2023. 66 of the 274 firms show a contract asset other than zero in any year from fiscal 2022 to 2025.

Each row recomputes S1 and S1P on another sample or definition. Every row but the first is a sensitivity: it changes one rule to see whether the label survives.

| Sample | Firms | T | T in days of revenue | S1: T / change in net income | S1 label | S1P: positive T_i / change | S1P label | Direction | What it is |
|---|---|---|---|---|---|---|---|---|---|
| primary | 274 | $26.1bn | 0.86 | 11.01% | SHARE_10_TO_25 | 25.51% | SHARE_ABOVE_25 | with_growth | all non-financial firms with every needed number stated (status in_scope) |
| mega | 7 | $9.8bn | 1.80 | 4.98% | SHARE_BELOW_10 | 5.11% | SHARE_BELOW_10 | with_growth | the nine largest of the 500, Alphabet, Amazon, Meta, Microsoft, Oracle, NVIDIA, Apple, Broadcom and Tesla, those of them in scope |
| s2_subset | 202 | $21.9bn | 0.99 | 12.04% | SHARE_10_TO_25 | 27.99% | SHARE_ABOVE_25 | with_growth | primary firms that S2 will cover (fiscal year-end from 30 November to 15 February) |
| sens_gap0 | 327 | $31.7bn | 0.94 | 11.07% | SHARE_10_TO_25 | 25.27% | SHARE_ABOVE_25 | with_growth | adds firms that tag a contract balance in some years only, the missing years set to zero |
| sens_acq | 163 | $28.7bn | 1.41 | 23.00% | SHARE_10_TO_25 | 41.07% | SHARE_ABOVE_25 | with_growth | drops firms whose cash paid for acquisitions over fiscal 2023-2025 exceeds 2% of fiscal 2023 revenue |
| sens_disc | 248 | $19.5bn | 0.69 | 9.52% | SHARE_BELOW_10 | 25.48% | SHARE_ABOVE_25 | with_growth | drops firms with income from discontinued operations (for example a spin-off) in a needed year |
| sens_trim | 270 | $28.8bn | 0.96 | 12.23% | SHARE_10_TO_25 | 25.10% | SHARE_ABOVE_25 | with_growth | drops firms whose N exceeds a year's revenue in size (|N / revenue| above 1) in a needed year |
| sens_unbilled | 274 | $26.2bn | 0.87 | 11.03% | SHARE_10_TO_25 | 25.69% | SHARE_ABOVE_25 | with_growth | adds unbilled receivables to contract assets for firms with no contract-asset tag |
| sens_r2only | 201 | $6.2bn | 0.32 | 4.99% | SHARE_BELOW_10 | 20.75% | SHARE_10_TO_25 | with_growth | drops firms whose revenue comes from the broad Revenues tag (rev_fallback) |
| sens_parts | 274 | $25.2bn | 0.83 | 10.61% | SHARE_10_TO_25 | 25.10% | SHARE_ABOVE_25 | with_growth | uses the tagged current plus noncurrent parts instead of a tagged total wherever the parts exist at every year |
| sens_latest | 274 | $6.9bn | 0.23 | 2.93% | SHARE_BELOW_10 | 23.50% | SHARE_10_TO_25 | with_growth | takes every value from the latest filing that reports it, so restated figures replace first-reported ones, instead of the year's own 10-K |
| sens_leave1 | 273 | $10.0bn | 0.33 | 4.31% | SHARE_BELOW_10 | 19.09% | SHARE_10_TO_25 | with_growth | drops the single largest positive contributor |
| sens_samefiling | 274 | $23.7bn | 0.79 | 9.99% | SHARE_BELOW_10 | 24.51% | SHARE_10_TO_25 | with_growth | takes the prior year's ratio r from the same 10-K as the current year (its comparative column, restated where the firm recast it), falling back to first-reported values where that 10-K does not tag the comparative. Added after the result was seen, by an independent check on 28 October 2026; it is not part of the rule set in advance |

Samples whose S1 or S1P label differs from the primary sample's: mega, sens_disc, sens_r2only, sens_latest, sens_leave1, sens_samefiling (6 of the 13 samples). On the same-filing basis T is $23.7bn and S1 is 9.99%; the next 10-K restates a comparative of 20 of the 274 firms, and for 6 firms it does not tag the comparative, so the first-reported value stands.

**Flags** appear on firms in the tables below and in contributions.csv:

- `acq2`: cash paid for acquisitions over fiscal 2023-2025 exceeds 2% of fiscal 2023 revenue.
- `disc_ops`: the firm reports income from discontinued operations (a disposal such as a spin-off) in a needed year.
- `rev_fallback`: revenue comes from the broad Revenues tag because the contract-revenue tags are not stated in every year.
- `total_gt_parts`: the tagged total is larger than its tagged current and noncurrent parts in some year, so the total was used.
- `extreme_r`: N exceeds a year's revenue in size (|N / revenue| above 1) in a needed year.
- `near_end`: some figure is stated for a date 1 to 7 days from the 10-K's period end.
- `gap_10k`: no single original 10-K for a needed year.
- `gap_n`: a contract balance is tagged in some needed years only.
- `gap_rev`: no revenue tag is stated in every needed year.
- `gap_ni`: net income is not stated in every needed year.
- `gap0_imputed`: a missing contract balance was set to zero (sens_gap0 only).
- `unbilled_added`: unbilled receivables were added to contract assets (sens_unbilled only).

## How much rests on a few firms

A leave-one-out check removes one firm at a time from the primary sample and rescores (descriptive; it registers nothing). S1 falls below 10% when any one of these 4 of the 274 firms is removed: Boeing Co (BA), with S1 at 4.31%; Dell Technologies Inc. (DELL), with S1 at 8.20%; General Electric Co (GE), with S1 at 8.76%; General Dynamics Corp (GD), with S1 at 9.73%. S1P falls below 25% when any one of 17 firms is removed.

## Contributors

**Largest positive contributions (shares of gross positive T, the sum of the positive T_i)**, by ticker; names are in contributors.csv:

| Rank | Ticker | T_i | Share of the side | Flags |
|---|---|---|---|---|
| 1 | BA | $16.07bn | 26.57% | rev_fallback |
| 2 | DELL | $6.88bn | 11.38% | rev_fallback |
| 3 | AMZN | $5.56bn | 9.20% | none |
| 4 | GE | $5.26bn | 8.69% | disc_ops|rev_fallback |
| 5 | MSFT | $3.98bn | 6.58% | none |
| 6 | GD | $3.11bn | 5.14% | none |
| 7 | PFE | $1.93bn | 3.19% | acq2|disc_ops|rev_fallback |
| 8 | NRG | $1.54bn | 2.55% | total_gt_parts |
| 9 | FSLR | $1.19bn | 1.96% | rev_fallback |
| 10 | CSCO | $1.04bn | 1.71% | acq2 |

**Largest negative contributions (shares of gross negative T)**, by ticker; names are in contributors.csv:

| Rank | Ticker | T_i | Share of the side | Flags |
|---|---|---|---|---|
| 1 | CPAY | -$3.65bn | 10.61% | rev_fallback|extreme_r |
| 2 | CVX | -$3.02bn | 8.77% | none |
| 3 | CCL | -$2.47bn | 7.19% | none |
| 4 | CRM | -$1.92bn | 5.57% | acq2 |
| 5 | CVS | -$1.87bn | 5.44% | acq2|rev_fallback |
| 6 | LMT | -$1.85bn | 5.38% | rev_fallback |
| 7 | HPE | -$1.43bn | 4.16% | acq2|rev_fallback |
| 8 | NCLH | -$1.36bn | 3.96% | none |
| 9 | LYV | -$1.25bn | 3.63% | rev_fallback |
| 10 | LIN | -$1.21bn | 3.51% | acq2|total_gt_parts |

A large contributor is not a finding about that firm. Concentration, as statistics and not verdicts: the five largest firms hold 62.41% of gross positive T, 37.58% of gross negative T and 34.32% of contract liabilities at fiscal 2025.

## The placebo windows: an earlier yardstick

The same statistic T, computed for earlier periods that need no fiscal 2023-or-later number, shows what ordinary movement in these balances looks like. "Placebo" here means only that: earlier windows used as a yardstick, not a test of anything.

| Window | Inputs | Firms | T | T / end-year revenue | Fiscal 2020 an endpoint |
|---|---|---|---|---|---|
| fiscal 2020 to 2022 | FY2019..FY2022 | 238 | $66.63bn | 0.753% | yes |
| fiscal 2020 to 2021 | FY2019..FY2021 | 259 | $36.30bn | 0.442% | yes |
| fiscal 2021 to 2022 | FY2020..FY2022 | 277 | -$56.13bn | -0.574% | no |

NB1 (noise band 1) is |T| over end-year revenue for the only one-year window that does not start from fiscal 2020, fiscal 2021 to 2022: 0.574%. NB2 (noise band 2) is the same for the two-year window, fiscal 2020 to 2022: 0.753%. Medians over all windows of each length: 0.508% (one year) and 0.753% (two years). S1 and S1P read within_pre_window_range when |T| over fiscal 2025 revenue is at most NB2, and outside_pre_window_range otherwise; S2 and S2P are read against NB1. The band rests on three windows, two of them with fiscal 2020 as an endpoint, so it is thin. The fiscal 2021 to 2022 window uses fiscal 2020 balances as the prior-year input to its fiscal 2021 excess accrual. The band is frozen from the first full vintage and is not recomputed.

## Descriptive tables (not registered)

**Trade receivables, collection and not recognition (descriptive).** Receivable days are receivables divided by revenue times 365, from the AccountsReceivableNetCurrent tag only, over the primary firms that tag it at every year:

| Fiscal year | Firms | Receivables | Revenue | Receivable days |
|---|---|---|---|---|
| 2022 | 205 | $730.3bn | $6,783.9bn | 39.30 |
| 2023 | 205 | $764.0bn | $6,802.1bn | 41.00 |
| 2024 | 205 | $821.9bn | $7,159.9bn | 41.90 |
| 2025 | 205 | $926.8bn | $7,685.7bn | 44.02 |

The same T construction on receivables gives $7.5bn (0.36 days of revenue) for 205 firms; this is a collection measure and is not added to T.

**Capitalized contract costs (descriptive).** "Costs in days" is the capitalized contract costs divided by revenue times 365; "N in days" is N divided by revenue times 365 (negative when contract liabilities exceed contract assets), over the firms that tag the costs at every year: fiscal 2022: costs 9.09 days, N -42.09 days; fiscal 2023: costs 9.94 days, N -45.53 days; fiscal 2024: costs 11.03 days, N -48.48 days; fiscal 2025: costs 11.50 days, N -49.84 days.

**Remaining performance obligations (descriptive).** Contracted revenue not yet recognised, billed or not, over the primary firms that report all four years: fiscal 2022: $1,734.0bn, 309.60 days of revenue; fiscal 2023: $1,976.3bn, 342.48 days of revenue; fiscal 2024: $2,037.3bn, 335.74 days of revenue; fiscal 2025: $2,503.2bn, 370.08 days of revenue.

**Cash-flow cross-check (descriptive).** It recomputes T with each year's change in N taken from the cash-flow statement's change items instead of the balance sheet (signs set on fiscal 2019 to 2022, see SOURCES.md). 51 firms tag the needed items; T from them is $39.6bn, against $34.1bn from the balance sheets for the same firms. The balance-sheet figure for these 51 firms differs from the headline $26.1bn because the other 223 primary firms, which do not tag the items, net to -$8.0bn; the cash-flow figure differs from the balance-sheet one because the statement's change items need not equal the difference between two balance-sheet dates.

## S2 and S2P

S2 and S2P repeat S1 and S1P on fiscal 2025 to 2026 for the firms whose fiscal 2026 year-end falls between 30 November 2026 and 15 February 2027, a period no one can have seen when the specification was committed. A firm is eligible when the fiscalYearEnd field of its SEC submissions file (the month and day its fiscal year ends, for example 1231) lies from 30 November to 15 February and it is in scope on fiscal 2024 and 2025. S2 and S2P are scored once, on the first full build on or after 1 May 2027, and read PENDING until then. If fewer than 70% of the 249 eligible firms have filed a fiscal 2026 10-K (0 have, counting only a 10-K whose period end lies inside the window), they read PENDING_THIN (pending: too few filers yet) and are run again each month, and VOID after 1 August 2027 if still thin. They are reported beside s2_subset, the S1 statistic on the same firms: T $21.9bn, 12.04% of the change in net income (label SHARE_10_TO_25). Status on vintage 20261028: S2 PENDING, S2P PENDING.

| Status for S2 | Firms |
|---|---|
| fiscal 2026 10-K with its period end inside the window (counted) | 0 |
| fiscal 2026 10-K with its period end outside the window (end_mismatch: never counted, never scored) | 1 |
| two or more original 10-Ks in the fiscal 2026 window (fy_ambiguous: never counted, never scored) | 0 |
| no fiscal 2026 10-K yet (stays in the denominator) | 248 |

AMCR: the submissions file says fiscalYearEnd 1231, but its latest original 10-K covers the year to 30 June 2026 and no 10-KT (transition report) has been filed; the data do not show a completed change of year-end.

## Coverage and exclusions

| Status | CIKs | Meaning |
|---|---|---|
| no_sec_record | 0 | the SEC has no submissions or company-facts file for the CIK |
| financial_sic | 98 | the SEC's industry code (SIC) is 6000 to 6799: banks, insurers, brokers and similar; excluded because ASC 606 does not cover their main income |
| no_sic | 0 | the SEC file carries no industry code, so the firm cannot be classed as financial or not |
| fy_ambiguous | 2 | two or more original 10-Ks fall in one fiscal-year window, so the year-end is not unique |
| end_mismatch | 0 | a needed number is stated only for a date 1 to 7 days from the 10-K's period end, not for the date itself |
| year_gap | 126 | a needed input (the 10-K, revenue, net income or a complete contract-balance tag set) is missing in some year; the firm is dropped because its excess accrual cannot be computed from reported numbers, and filling a gap with zero would invent data (sens_gap0 shows that variant) |
| tiny_revenue | 0 | revenue below $100 million in a needed year, where ratios turn unstable |
| in_scope | 274 | every needed input is stated in every needed year: the primary sample |

Financial firms (SIC 6000 to 6799) are excluded; 98 of the 500 CIKs are in that range. ASC 606 leaves financial instruments, leases and insurance contracts out of its scope, and a bank's receivables are loans. The SIC range is not the boundary of ASC 606: it also drops exchanges, brokers and insurance brokers, whose fees are under ASC 606, and keeps card networks and processors under other codes. A firm with no contract-balance tag at any needed year has N equal to zero at every year and stays in scope. `coverage.csv` counts the 500 CIKs with a fact in each frame; the frames are used for coverage and checks only.

## Words

- **Vintage**: the UTC date a set of downloads began. **Trade receivable**: billed consideration awaiting cash. **Remaining performance obligation**: contracted revenue not yet recognised.
- **Operating cash flow**: cash generated by operations, the statement that reports the year's change in these balances. **ASC 606**: the US accounting standard for revenue from contracts with customers.
- **Latest-filed values**: for each number, the figure in the most recent filing that reports it, so restatements replace first-reported figures.
- Columns ending _usd are whole dollars, _pct percent, _days days of revenue. The aggregates in headline.csv and registered.csv are sums of the whole-dollar cells in contributions.csv.

The fifteen CSV files: firms, firm_years, firm_tags, panel, contributions, headline, registered, contributors, placebo, receivables, coverage, checks, vintages, fetch_log and revisions. SOURCES.md lists every request, the rules and the builder's decisions.

## Citations

US Securities and Exchange Commission, EDGAR XBRL APIs (companyfacts, submissions, frames) on data.sec.gov, vintage 20261028 (US government works, 17 U.S.C. 105). The project's specification and its rulings are in [the spec](../../_research/2026-10-28-Revenue-Recognition-Timing-Spec.md). How the numbers were fetched, the checks and the builder's decisions are in [SOURCES.md](SOURCES.md).
