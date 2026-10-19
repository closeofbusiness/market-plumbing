# Registered funds' Treasury futures and the index split of their cash Treasury duration

This folder measures how much US registered funds changed their net Treasury futures positions between end-2023 and mid-2026, in 10-year equivalents, and how much of the change in their cash Treasury duration sits in series that Form N-CEN flags as index funds. These are holdings measurements. They do not show what moved Treasury yields.

## Definitions

- **10-year equivalent.** A holding restated as the amount of a 10-year par Treasury note that would react to a rate change by the same number of dollars, on one fixed yield curve (29 December 2023). Cash holdings and futures are both stated this way, always on that one curve.
- **Treasury future and contract face.** A standard contract on a Treasury note or bond. Eight are used: the 2-, 3-, 5- and 10-year notes, the Ultra 10-year note, the 20-year bond, the classic bond and the Ultra bond. Face per contract is $200,000 for the 2- and 3-year notes and $100,000 for the others; a fund's position is its contract count times that face.
- **Net change in funds' futures.** Long positions less short positions, in 10-year equivalents, at the end of the second window less the first, across the registered funds the cash build keeps for each window.
- **Tenor map.** The headline conversion. Each contract is represented by a par bond at the shortest remaining term of its deliverable basket, priced on the fixed curve, and scaled by the contract's conversion factor. The eight resulting dollar values per contract are fixed before any fund data is read.
- **Conversion factor.** The exchange's number that makes deliverable bonds of different coupons comparable: the price at a 6% yield of a bond with that coupon and term, per dollar of face, with the coupon rounded to the nearest eighth of a per cent.
- **Modelled cheapest-to-deliver.** For comparison only: from the Treasury's list of outstanding notes and bonds on each window's date, the deliverable with the lowest price per unit of conversion factor on that date's curve, ignoring carry and delivery options. It is a model, not an observed delivery.
- **Form N-CEN and the "Index Fund" box.** Form N-CEN is the annual report of a registered fund. Item C.3 asks the fund to tick every type that applies, including "Index Fund". A fund that ticks none of the types, and marks "not applicable", is an ordinary active fund here.
- **Stable sample.** The series that carry the same flag, index or active, in every window in which they appear. The split is measured on this sample.
- **Unclassified change.** The change in cash Treasury duration held by series that are unflagged, switch flags, or whose flag is out of date; it is reported separately and capped at $16.2bn for the split to count as established.

## Futures: what the result says

The net change in registered funds' Treasury futures from end-2023 to mid-2026 was not established, at $157.9bn of 10-year equivalents against a $100bn line, because two conditions were not met: the anchor comparing futures risk with cash bond risk at end-2023 was 0.10, outside its band of 0.20 to 0.45; and the readings of the net change using the filed long-or-short sign and using the sign of the filed contract count differ by $27.5bn against a $20bn limit.

The net position was $131.1bn of 10-year equivalents at end-2023 (12,609 funds in the window) and $289.0bn at mid-2026 (13,799 funds), a change of $157.9bn. By period it was $54.6bn in 2024, $90.3bn in 2025 and $13.0bn in the first half of 2026. Using the matched vintage the change is $157.0bn, using the modelled cheapest-to-deliver $163.3bn, and taking the sign from the filed contract count $130.3bn.

Checks against the Federal Reserve note's end-2023 figures, over the 2,735 registered funds in the cash build's end-2023 survivors whose cash Treasuries or gross futures face exceed 1% of net assets (1,523 of them hold futures): the end-2023 net futures face was $353.5bn (accepted range $250bn to $380bn); the anchor comparing futures risk with cash bond risk was 0.10 (accepted range 0.20 to 0.45; the Federal Reserve note's own value is 0.30); the implied futures duration was 3.00 years (accepted range 3.0 to 4.5; the note's value is 3.75). The gross long futures face of all registered funds at end-2023 was $553.0bn, against the note's reading of about $470bn to $500bn for mutual funds. The conditions and gaps that decide the label are: unresolved, conflicting and sign-less lines were 3.2% of futures face at end-2023 (limit 10%) (met); unresolved, conflicting and sign-less lines were 3.3% of futures face at mid-2026 (limit 10%) (met); the base and matched vintages differ by $0.8bn (limit $20bn) (met); the tenor map and the modelled cheapest-to-deliver differ by $5.5bn (limit $50bn) (met); the filed long-or-short sign and the sign of the filed contract count differ by $27.5bn (limit $20bn) (not met).

That anchor fails because the end-2023 comparison group covers all registered funds, exchange-traded and closed-end funds included, a choice the supervisor ruled on before the run, while the Federal Reserve note's own value of 0.30 is for mutual funds only, so the cash bond side here is far larger. With exchange-traded funds removed the value is 0.151, which also falls outside the band.

Futures are not added to cash holdings. A future has a long side and a short side, so across all holders it nets to zero; it is not a stock of securities that someone has to hold. This build therefore never adds the futures figure to the cash figure, never divides it by the public's change in cash holdings, and never sets it against the cash line of the companion cash study.

## Index split: what the result says

The split of registered funds' cash Treasury duration change between series flagged 'Index Fund' on Form N-CEN (any index, not only Treasury indexes) and the rest is not established: the index funds' share of the classified change was 67.6% in 2024, 52.2% in 2025 and 41.4% in the first half of 2026, against 56.9% of the classified stock at end-2023. The share in the first half of 2026 lies between the two bars (at least 60%, with the required margins, to support the finding; at most 40%, and no higher than the stock share, to count against it), close to the lower bar.

In the first half of 2026 the cash Treasury duration held by registered funds changed by $162.1bn of 10-year equivalents. Of that, the stable index series took $65.5bn and the stable active series $92.7bn; the unclassified change was $4.0bn against the $16.2bn cap. The index share of the classified change was 67.6% in 2024, 52.2% in 2025 and 41.4% in the first half of 2026, against an index share of the classified stock at end-2023 of 56.9%. The bar for a result that is large and rising is a share of at least 60% in the first half of 2026, at least 15 points above the stock share, and at least 10 points above each of the two earlier periods. The 15-point bar is a hurdle fixed in advance, taken from a different object (the funds' excess over the public stock in the cash study) after that object had been measured; it is not a sampling bound.

This is a measurement, not a test against noise. With unclassified change at its cap, the share could move by about ten points either way, so a share within ten points of a bar is fragile.

## What the "Index Fund" box cannot tell

The box says only that a fund tracks some index. It does not say the index is the Bloomberg US Aggregate or any bond index, that it is weighted by market value, or that it is an index of Treasuries; it covers equity and other indexes too. A fund that follows an index closely without ticking the box is counted as active. Index funds that hold only Treasuries or T-bills are inside the index group, and the bulk files carry no field that separates them.

## Flags can be out of date or missing for 2025 and 2026

The SEC's Form N-CEN data sets do not include, at this time, filings submitted in the newer schema version, so the flags for 2025 and 2026 can be out of date or missing. Series whose latest usable filing ended before 30 March 2025 are set aside as stale, entrants with no earlier filing are unflagged, and both count as unclassified. If the unflagged entrants' change plus the stale series' change exceeds $16.2bn, the split is inconclusive by construction. In this build the unflagged entrants' change was $0.3bn and the stale series' change $3.5bn (148 entrants, of which 106 unflagged and 0 flagged from a later filing).

## Where the exchange's explainer disagreed with its rulebook

An earlier draft of the contract rules followed the CME's 2024 explainer. It measured the remaining term of the 2-year and 3-year note futures from the last day of the delivery month, and left out the 10-year note future's limit on original term. The CBOT rulebook, as quoted from its chapters, measures every term from the first day of the delivery month and limits the 10-year note's original term to ten years. The rulebook is used.

## Provenance

Built by bin/nport_futures_index.py from the SEC bulk N-PORT zips (eleven files, 2024q1 to 2026q3) read in place as streams, the SEC bulk Form N-CEN zips (nineteen files, 2022q1 to 2026q3, fetched by the supervisor), the companion cash build's committed files and its cached Treasury curves and Statement of the Public Debt tables. The script imports the cash build's survivor selection and pricing; the cash build's own totals are reproduced at the four report dates before anything else is reported. The script makes no network request. Sources are in fut_idx_SOURCES.md; file hashes and counts are in fut_idx_file_stats.csv; the checks are in fut_checks.csv and idx_checks.csv.

Build decisions, including two edits made after the first run, are listed in [fut_idx_SOURCES.md](fut_idx_SOURCES.md).

## Column dictionary

- `fut_windows.csv`:
  - `window`: the quarter-end month of the report window, such as 2023Q4
  - `quarter_end`: the last day of that quarter
  - `vintage`: base = every zip with a filing within 62 days of the report date; matched = zips up to the window's home zip
  - `funds_in_window`: survivor filings assigned to the window by the cash build's rule
  - `funds_with_tsy_fut`: funds with at least one kept Treasury-futures line
  - `tsy_fut_lines`: kept Treasury-futures lines
  - `contracts_long`: contracts held long (effective count)
  - `contracts_short`: contracts held short (effective count)
  - `face_long_bn`: face of the long contracts, $bn
  - `face_short_bn`: face of the short contracts, $bn
  - `face_net_bn`: long face less short face, $bn
  - `notional_tradedate_net_bn`: net trade-date contract value from the filed notional field, $bn, lines whose notional is a genuine value
  - `tenyeq_tenor_bn`: net 10-year equivalents on the tenor map, $bn (the headline measure)
  - `tenyeq_tenor_balsign_bn`: the same with the sign taken from BALANCE where it is not zero, $bn
  - `tenyeq_ctd_bn`: net 10-year equivalents on the modelled cheapest-to-deliver, $bn (base vintage, the four R2 dates only)
  - `unrealized_abs_bn`: sum of the absolute filed marks on kept lines, $bn
  - `lines_basis_face`: kept lines sized as contracts times face
  - `lines_basis_notional`: kept lines sized from the filed notional
  - `notional_field_is_count_lines`: lines whose notional field holds the contract count (face basis kept)
  - `unit_suspect_lines`: valid-count lines whose notional is far from contracts times face (notional basis)
  - `no_size_lines`: Treasury lines with no usable size, excluded
  - `non_usd_lines`: futures lines failing the USD condition
  - `unresolved_lines`: futures lines whose text names no contract
  - `unresolved_conflict_lines`: lines whose sources name different contracts
  - `sign_na_lines`: Treasury lines with no long or short sign, excluded
  - `sign_disagree_lines`: kept lines whose two signs disagree
  - `sign_disagree_notional_share`: face of those lines over the face of kept lines
  - `expired_lines`: Treasury-candidate lines that expired before the report date, dropped
  - `non_dir_tsy_lines`: kept Treasury lines whose asset category is not interest-rate derivative
  - `ctd_fallback_lines`: kept lines priced on the tenor map because the modelled basket was empty
  - `unresolved_share`: face of unresolved, conflicting and sign-less lines over the face of kept plus those lines
- `fut_contracts.csv`:
  - `window`: the quarter-end month of the report window, such as 2023Q4
  - `contract`: TU 2-year note, Z3N 3-year note, FV 5-year note, TY 10-year note, TN Ultra 10-year note, TWE 20-year bond, US classic bond, UB Ultra bond
  - `funds_n`: funds with a kept line (a count of funds)
  - `lines`: kept lines, or lines in the category
  - `contracts_net`: long less short contracts
  - `face_net_bn`: long face less short face, $bn
  - `tenyeq_tenor_bn`: net 10-year equivalents on the tenor map, $bn (the headline measure)
  - `tenyeq_ctd_bn`: net 10-year equivalents on the modelled cheapest-to-deliver, $bn (base vintage, the four R2 dates only)
  - `dv01_tenor_mn`: net 10-year equivalents times the fixed-curve duration times 0.0001, $mn per basis point
  - `tenor_factor_usd`: 10-year-equivalent dollars of one contract on the tenor map
  - `ctd_factor_usd`: the same on the modelled cheapest-to-deliver of the largest delivery month
  - `ctd_maturity`: maturity of that modelled deliverable
  - `ctd_coupon_pct`: its coupon, per cent
  - `ctd_cf`: its conversion factor
  - `notional_over_face_median`: median filed notional over contracts times face
- `fut_change.csv`:
  - `variant_id`: T0 tenor map base; T1 tenor map matched; C0 modelled cheapest-to-deliver base; B0 tenor map base with the BALANCE sign
  - `description`: what the variant is
  - `period`: full = 2023Q4 to 2026Q2; 2024; 2025; 2026H1
  - `f_start_bn`: net 10-year equivalents at the start of the period, $bn
  - `f_end_bn`: at the end, $bn
  - `d_f_bn`: the net change, $bn
- `fut_split.csv`:
  - `period`: full = 2023Q4 to 2026Q2; 2024; 2025; 2026H1
  - `group`: the group the amount belongs to
  - `funds_n`: funds with a kept line (a count of funds)
  - `d_f_bn`: the net change, $bn
- `fut_other_deriv.csv`:
  - `window`: the quarter-end month of the report window, such as 2023Q4
  - `category`: swap_dir, option_dir, swaption_dir, ir_fut_nontsy, bond_fut_foreign, other_fut_nontsy, unresolved, sign_na
  - `lines`: kept lines, or lines in the category
  - `notional_abs_bn`: gross absolute notional, $bn (options: principal amount where filed)
- `fut_verdict.csv`: columns key, value; one value per row.
- `idx_verdict.csv`: columns key, value; one value per row.
- `idx_prerun.csv`: columns key, value; one value per row.
- `idx_split.csv`:
  - `period`: full = 2023Q4 to 2026Q2; 2024; 2025; 2026H1
  - `group`: the group the amount belongs to
  - `series_n`: series (a count of series)
  - `s_start_bn`: cash 10-year equivalents at the start of the period, $bn
  - `s_end_bn`: at the end, $bn
  - `d_s_bn`: the change, $bn
- `idx_coverage.csv`:
  - `window`: the quarter-end month of the report window, such as 2023Q4
  - `flag`: mmf, levinv, unflagged, index, active or feeder_dropped
  - `flag_backfilled_n`: series whose flag came from the first later N-CEN filing
  - `series_n`: series (a count of series)
  - `s_bn`: cash 10-year equivalents, $bn
- `idx_crosstab.csv`:
  - `period`: full = 2023Q4 to 2026Q2; 2024; 2025; 2026H1
  - `is_etf`: Y or N from the N-CEN ETF box
  - `arm`: index or active (stable series only)
  - `series_n`: series (a count of series)
  - `s_start_bn`: cash 10-year equivalents at the start of the period, $bn
  - `d_s_bn`: the change, $bn
- `fut_checks.csv`:
  - `check_id`: the check's name
  - `label`: what is checked
  - `ours`: the value this build found
  - `reference`: what it is compared with
  - `threshold`: the pass condition
  - `result`: PASS, FAIL, FLAG or N/A
  - `hard`: Y if a FAIL stops the build
  - `note`: detail
- `idx_checks.csv`:
  - `check_id`: the check's name
  - `label`: what is checked
  - `ours`: the value this build found
  - `reference`: what it is compared with
  - `threshold`: the pass condition
  - `result`: PASS, FAIL, FLAG or N/A
  - `hard`: Y if a FAIL stops the build
  - `note`: detail
- `fut_idx_file_stats.csv`:
  - `tag`: the file or window the row is about
  - `key`: the name of the value
  - `value`: the value
