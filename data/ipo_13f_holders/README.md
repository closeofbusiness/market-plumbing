# Who held the 2026 IPOs: Form 13F holdings at the first quarter-end

This table counts the shares of the eight US IPOs of 2026 that raised about $1bn or more, set out in the deal list, that investment managers reported holding on Form 13F at the first calendar quarter-end after each listing. Form 13F is the quarterly holdings report that managers with at least $100 million in US-listed stocks file with the Securities and Exchange Commission, and each count is set against the shares the company had outstanding at that same quarter-end.

Form 13F shows what each manager held at the quarter-end, not what it was allocated in the offering or when or at what price it bought, so none of these figures is an IPO allocation. The part of the listed class not counted here is not a group of holders, and this table does not say who holds it.

## Which deals are measured

5 of the 8 deals have their first quarter-end on 30 June 2026 and are measured here: SpaceX (SPCX), Cerebras (CBRS), Quantinuum (QNT), Fervo Energy (FRVO), INNIO (INIO). Their primary base proceeds to the company, $84,119,999,925, are 75.146% of the $111,941,660,492 that the deal list sums to (secondary sales excluded; SpaceX alone is 89.158% of the measured proceeds).

Bending Spoons (BSP), SK hynix (SKHY), Jersey Mike's (JMKE) have a first quarter-end of 30 September 2026. Managers must file within 45 days of the quarter-end, which is 16 November 2026 for that date, and the SEC publishes the filings in its next data set, expected around mid-December 2026. Those deals wait for it and have no figures here.

All measured companies filed a quarterly report for the period ended 30 June 2026, so every measured deal has a percentage against the shares outstanding at that date.

## Shares reported on Form 13F, deal by deal

Counts of shares of the listed class (the class that trades; see the dual-class section) that 13F filers reported at the quarter-end, summed over all filers as filed in the SEC data set (vintage `13f_to_2026-08-31`). A filer here is a filer number, not a manager group.

| Deal | Quarter-end | Filers | Shares reported (sh_13f) | of which sole discretion | Reported by filers flagged as pre-listing holders (hypothesis) |
|---|---|---|---|---|---|
| SpaceX | 2026-06-30 | 1,744 | 3,668,807,223 | 2,137,533,475 | 1,370,072,045 |
| Cerebras | 2026-06-30 | 412 | 88,739,770 | 54,899,707 | 0 |
| Quantinuum | 2026-06-30 | 174 | 34,003,849 | 11,685,718 | 0 |
| Fervo Energy | 2026-06-30 | 183 | 185,569,018 | 121,464,276 | 69,955,689 |
| INNIO | 2026-06-30 | 148 | 454,603,514 | 389,970,139 | 334,867,308 |

The sole-discretion column is a floor that no double report by two managers can inflate. The flagged column is a floor on holdings by investors who owned the company before it listed, judged by the builder from notes on Schedule 13D/13G filings (filings by holders of more than 5% of a class) and public descriptions; it is a hypothesis.

These counts are not comparable with the table above: they are shares of any class that a Schedule 13D/13G filer is deemed to own, including Class B shares that can convert into the listed class, so for SpaceX one holder's block of mostly Class B shares makes the total larger than the whole listed class.

| Deal | Quarter-end | Schedule 13D/13G shares, any class, holders with no 13F row (not comparable; can exceed the listed class) |
|---|---|---|
| SpaceX | 2026-06-30 | 7,660,179,395 |
| Cerebras | 2026-06-30 | 125,634,550 |
| Quantinuum | 2026-06-30 | 405,211,851 |
| Fervo Energy | 2026-06-30 | 140,910,868 |
| INNIO | 2026-06-30 | 646,500,000 |

The column counts shares as typed on Schedule 13D/13G filings by reporting persons for which no 13F filer with a row in this deal is matched. It is beneficial ownership: it overlaps across the filings of one group and is never added to a 13F figure or to any percentage of the listed class.

## Against the shares outstanding at the quarter-end

| Deal | Listed class outstanding at the quarter-end (first 10-Q) | As of | 10-Q item | sh_13f as % of that count (pct_of_listed) | IPO shares as % of that count | sh_13f as % of all classes | sh_13f as % of IPO shares (memo) |
|---|---|---|---|---|---|---|---|
| SpaceX | 7,607,000,000 | 2026-06-30 | qe_balance_sheet | 48.229% | 7.303% | 27.845% | 660.4% |
| Cerebras | 103,220,568 | 2026-06-30 | qe_balance_sheet | 85.971% | 29.064% | 38.886% | 295.8% |
| Quantinuum | 36,134,196 | 2026-06-30 | qe_balance_sheet | 94.104% | 77.489% | 12.934% | 121.4% |
| Fervo Energy | 286,869,000 | 2026-06-30 | qe_balance_sheet | 64.688% | 24.401% | 62.979% | 265.1% |
| INNIO | 750,000,000 | 2026-06-30 | qe_balance_sheet | 60.614% | 12.000% | 60.614% | 505.1% |

The prospectus count is a different quantity: for Cerebras it counts only the 30,000,000 Class A shares sold, because every earlier share was then Class B and converted afterwards; the prospectus-based percentage is in holdings.csv for comparison only and can exceed 100.

The first 10-Q gives the count either in the financial statements at the period end (`qe_balance_sheet`) or on its cover page at a later date (`qe_cover`); the table says which. SpaceX's count at the quarter-end is stated in millions of shares in its financial statements and Fervo Energy's in thousands (shown as issued, with no treasury stock at that date), so both are rounded to the unit stated. Cerebras's primary count is its 30 June figure for Class A, not its cover figure. A high percentage can consist mostly of shares held by investors who owned the company before it listed. The IPO-shares column shows how small the offering can be against the listed class. The last column is a memo that exceeds 100 wherever pre-listing holders file on Form 13F.

For SpaceX the 555,555,555 shares sold in the offering are 7.3% of the listed class at the quarter-end, mostly pre-listing stock that converted into Class A at the listing, so the percentage above says who held the listed class, not who took the offering.

Pooled over the measured deals that have a quarterly report, 13F filers reported 4,431,723,374 shares against 8,783,223,764 shares in the listed classes at the quarter-end, a pooled 50.457% (without SpaceX: 762,916,151 shares against 1,176,223,764, 64.861%).

A proceeds-weighted mean of the deal percentages is 52.005% with SpaceX and 83.059% without it: SpaceX carries 89.158% of the weight, INNIO carries a weight of 0 because the company received no proceeds from its offering, and 3 of the 8 deals are not yet measured. The unweighted median of the deal percentages is 64.688% (range 48.229% to 94.104%; without SpaceX 75.329%, range 60.614% to 94.104%).

## Concentration, registration numbers and options

| Deal | Largest filer, % of sh_13f | Ten largest filers, % of sh_13f | Ten largest filers, % of the listed class at the quarter-end |
|---|---|---|---|
| SpaceX | 15.0% | 67.4% | 32.5% |
| Cerebras | 12.9% | 59.3% | 51.0% |
| Quantinuum | 13.4% | 51.0% | 48.0% |
| Fervo Energy | 19.3% | 60.0% | 38.8% |
| INNIO | 73.7% | 86.6% | 52.5% |

Filers are filer numbers, not manager groups: two numbers of one manager count twice.

Each report's cover page may declare an SEC file number. Its prefix is a registration status, not an investor type: 801- registered investment adviser, 802- exempt reporting adviser, 8- broker-dealer, another prefix, or no number declared. Share of sh_13f by status:

| Deal | 801- (registered investment adviser) | 802- (exempt reporting adviser) | 8- (broker-dealer) | another prefix | no number declared |
|---|---|---|---|---|---|
| SpaceX | 20.0% | 7.5% | 0.0% | 19.2% | 53.4% |
| Cerebras | 38.2% | 15.4% | 0.0% | 1.7% | 44.7% |
| Quantinuum | 30.3% | 1.3% | 0.6% | 1.9% | 66.0% |
| Fervo Energy | 14.3% | 0.2% | 0.0% | 23.0% | 62.5% |
| INNIO | 8.0% | 0.8% | 0.0% | 0.3% | 90.9% |

Options are shares underlying call and put positions as filed, including rows filed under the Official List's separate call and put identifiers of the same issuer. They are never added to or subtracted from sh_13f.

| Deal | Shares underlying calls | as % of sh_13f | Shares underlying puts | as % of sh_13f | Filers with calls / puts |
|---|---|---|---|---|---|
| SpaceX | 107,926,977 | 2.94% | 85,625,675 | 2.33% | 99 / 104 |
| Cerebras | 11,695,109 | 13.18% | 7,084,800 | 7.98% | 33 / 23 |
| Quantinuum | 547,902 | 1.61% | 233,800 | 0.69% | 8 / 6 |
| Fervo Energy | 1,135,900 | 0.61% | 252,400 | 0.14% | 10 / 6 |
| INNIO | 0 | 0.00% | 0 | 0.00% | 0 / 0 |

## Filers that also filed a Schedule 13D or 13G, and the prospectus investors

Share of sh_13f reported by filers that the builder matched to a Schedule 13D/13G reporting person on the same issuer (the two filings use different legal tests and are not expected to reconcile; the gaps are in `overlap_i2.csv`):

| Deal | % of sh_13f |
|---|---|
| SpaceX | 29.4% |
| Cerebras | 32.7% |
| Quantinuum | 0.0% |
| Fervo Energy | 37.7% |
| INNIO | 73.7% |

Fervo Energy: investors the prospectus named as having indicated an interest in buying up to $350,000,000 of shares (a ceiling), 12,962,962.96 shares at the $27.00 offer price. The filers the builder matched to them reported 13,638,503 shares at the quarter-end, 105.2% of that ceiling. An indication of interest is not a holding.

## Coverage of the data set

| Quarter-end | Zip | 13F-HR filers | 13F-NT filers | Confidential holdings omitted | as % of 13F-HR filers | Restatements | New-holdings amendments | Repeating an identifier* | Orphan amendments | Duplicate amendments* | Filed after the due date |
|---|---|---|---|---|---|---|---|---|---|---|---|
| 2026-03-31 | 01jun2026-31aug2026_form13f | 130 | 4 | 0 | 0.000% | 53 | 30 | 0 | 0 | 0 | 130 |
| 2026-06-30 | 01jun2026-31aug2026_form13f | 8857 | 1936 | 83 | 0.937% | 108 | 35 | 7 | 0 | 0 | 162 |
| 2025-12-31 | 01mar2026-31may2026_form13f | 207 | 22 | 1 | 0.483% | 59 | 27 | 0 | 76 | 0 | 207 |
| 2026-03-31 | 01mar2026-31may2026_form13f | 8741 | 1907 | 89 | 1.018% | 106 | 21 | 0 | 0 | 0 | 169 |

*Counted over the deals' rows only. A manager's confidential holdings are invisible here.

## Kinds of holder

Kind, judged by the builder from public descriptions (a hypothesis): among the ten largest filers of each deal, the count by kind is in `kind_hypothesis.csv`. 13F itself has no holder-type field and no manager files a kind.

| Deal | Ten largest filers by kind (hypothesis) |
|---|---|
| SpaceX | asset_manager 3, corporate_strategic 2, hedge_fund 1, pension_endowment_sovereign 1, venture_or_pre_ipo 3 |
| Cerebras | asset_manager 7, bank_broker 2, venture_or_pre_ipo 1 |
| Quantinuum | asset_manager 9, hedge_fund 1 |
| Fervo Energy | asset_manager 4, bank_broker 2, corporate_strategic 1, insurer 1, pension_endowment_sovereign 1, venture_or_pre_ipo 1 |
| INNIO | asset_manager 5, bank_broker 1, hedge_fund 2, other 1, venture_or_pre_ipo 1 |

## Dual-class issuers in plain words

A company with more than one class of common stock lists one class. Only that class is a Section 13(f) security, so Form 13F reports it and nothing else. Shares held before the listing in another class (Class B at SpaceX, Cerebras, Quantinuum and Fervo Energy) are not in the 13F figure unless they were converted into the listed class. Percentages here are against the listed class; `pct_of_all_classes` is printed beside them and is not the measure.

## Column dictionary

| Column | Meaning |
|---|---|
| sh_13f | Shares of the listed class reported on Form 13F at the quarter-end, summed over filers after one report per filer and quarter is chosen (original, later restatement, added new-holdings amendments); a filer is counted only if its reported shares are positive |
| sh_13f_sole | The same over rows with sole investment discretion |
| sh_pre_ipo_flagged | sh_13f of filers flagged as pre-listing holders (a floor; a hypothesis) |
| sh_13dg_holders_without_13f | Typed Schedule 13D/13G share counts of reporting persons with no matched 13F row (beneficial ownership; never added to sh_13f) |
| pct_of_listed | 100 times sh_13f over the listed class outstanding at the quarter-end (first 10-Q); blank where no 10-Q exists |
| pct_of_listed_prosp | The same over the listed class outstanding after the offering in the 424B4 (a variant) |
| pct_of_all_classes | The same over all common classes on the same 10-Q item |
| ipo_shares_pct_of_listed | 100 times the shares sold in the offering (base case) over the listed class at the quarter-end |
| pct_of_ipo_shares | 100 times sh_13f over the shares sold in the offering (memo) |
| top1_pct_of_13f, top10_pct_of_13f, top10_pct_of_listed | Largest filer and ten largest filers, as a share of sh_13f and of the listed class |
| sh_calls, sh_puts | Shares underlying call and put rows; never netted |
| sh_name_match_other_cusip | Shares in rows whose issuer name matches the deal but whose identifier is not the mapped one; reported, not added |
| median_implied_price_usd, implied_to_offer_ratio | Median over filers of reported value over reported shares, and its ratio to the offer price; some filers report value in thousands, so this is a check on units |
| status | measured, or awaiting_next_zip when the first quarter-end's filings are not yet in a data set |
| den_listed_10q_item | qe_balance_sheet (financial statements at the period end) or qe_cover (cover page, later date) |

## Identifiers and source

Securities are named by ticker and issuer name. The committed files carry no CUSIP, ISIN, FIGI, filer number or accession number: CUSIP Global Services allows its numbers to be collected from public sources for non-commercial use, and this repository's licence would let others reuse a committed number commercially. Filer names appear only where the builder's review marked the name as an organisation's public name; otherwise `withheld`.

Source: U.S. Securities and Exchange Commission, "Form 13F Data Sets", 01jun2026-31aug2026_form13f.zip, 01mar2026-31may2026_form13f.zip (vintage `13f_to_2026-08-31`); the issuers' prospectuses (Form 424B4) and first quarterly reports (Form 10-Q). Method, inputs and every build decision: `SOURCES.md`.
