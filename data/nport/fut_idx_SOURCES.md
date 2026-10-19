# Sources for the fund futures and index split build

Every source below was read by someone other than this script. The script makes no network request of any kind.

1. **SEC bulk N-PORT data sets.** Quarterly zip files of Form N-PORT filings, 2024q1 to 2026q3 (eleven files). Landing page
   https://www.sec.gov/dera/data/form-n-port-data-sets ; file pattern https://www.sec.gov/files/dera/data/form-n-port-data-sets/YYYYqQ_nport.zip .
   Terms: the SEC publishes these data sets for public use; its website policies at https://www.sec.gov/about/privacy-information apply, and SEC.gov
   requires automated requests to declare a contact. The zips are not redistributed here; only derived aggregates are.
   Citation: U.S. Securities and Exchange Commission, Division of Economic and Risk Analysis, Form N-PORT Data Sets, retrieved October 2026.
2. **SEC bulk Form N-CEN data sets.** Quarterly zip files of Form N-CEN annual reports, 2022q1 to 2026q3 (nineteen files). Landing page
   https://www.sec.gov/dera/data/form-ncen-data-sets . The page says the data sets do not include, at this time, N-CEN filings submitted in the schema
   version 3.1 introduced in EDGAR version 25.2. Terms and citation as for item 1; Form N-CEN, Item C.3, defines the type boxes.
3. **Federal Reserve Board, FEDS Notes.** Iorio, Li and Petrasek, "Why do mutual funds invest in Treasury futures?", 10 May 2024,
   https://www.federalreserve.gov/econres/notes/feds-notes/why-do-mutual-funds-invest-in-treasury-futures-20240510.htm and its accessible data page
   https://www.federalreserve.gov/econres/notes/feds-notes/why-do-mutual-funds-invest-in-treasury-futures-accessible-20240510.htm .
   Terms: Federal Reserve material is in the public domain. Used for the end-2023 anchor values only.
4. **CME Group and CBOT contract rules.** Treasury futures deliverable baskets, contract sizes and the conversion-factor formula, from the CBOT rulebook
   chapters 18, 19, 20, 21, 26, 39 and 40 and the CBOT conversion-factor article, as fetched and quoted by an outside reviewer; this build did not read
   cmegroup.com. Terms: CME Group's website terms; short factual rules only are used, no text is reproduced.
5. **U.S. Treasury, Fiscal Data.** Monthly Statement of the Public Debt, Table 3 (market value of marketable securities), record dates 2023-12-31,
   2024-12-31, 2025-12-31 and 2026-06-30, through https://fiscaldata.treasury.gov/ (cached by the companion cash build). Terms: U.S. government data.
6. **U.S. Treasury, Daily Treasury Par Yield Curve Rates and Real Yield Curve Rates**, 2023 to 2026, https://home.treasury.gov/ (cached by the cash
   build). Terms: U.S. government data. The fixed curve is that of 29 December 2023.
7. **The companion cash build.** bin/nport_treasury_duration.py and its outputs in data/nport/ (tsy_windows.csv, tsy_change.csv, tsy_file_stats.csv),
   which this build imports and reproduces; and bin/r2_duration_supply.py, the pricing functions it imports.

## Build decisions

Each was made where the specification was open or silent, taking the stricter reading on leaks and wording. No rule, threshold, window or label was changed. The last two entries record what was done after the first run.

1. A zero filed notional is treated as a missing one when the contract count is valid, so the line is sized as contracts times face (the specification names blank and zero together only for lines with no valid count).
2. Each text source is the concatenation of every filed field of every row of that table for the holding, in upper case with runs of spaces squeezed to one space (not removed).
3. Two or more different contracts named by different sources make a conflict; otherwise the first source that gives any answer, including a non-Treasury word, decides.
4. Treasury lines outside the interest-rate derivative category are kept in the net position and also counted separately; unresolved lines that had already expired are dropped as expired.
5. In the unclassified share of the futures result, the size of an unresolved or conflicting line is its filed notional, and the size of a line with no sign is its sized face.
6. A series counts in a group's series count at a period if it holds a non-zero cash amount at either end; empty cells are dropped, and cells under five series are merged into other_small.
7. The series group is taken over every window in which the series is a survivor, including windows in which it is a feeder whose amount is set aside.
8. Entrants are survivors at 2026Q2 that were not survivors at 2025Q4 and hold cash Treasuries at 2026Q2.
9. Feeders are found from the master's N-CEN filing: the FEEDER_FUNDS rows are joined through FUND_ID to the master's FUND_REPORTED_INFO row, because that table has no accession column.
10. The specification gives no thresholds for the four extra inconclusive clauses. Each is printed as a yes or no for whether the value would sit on a different side of the rule's bars than the headline share (above, below or between); these printed ratios are plain ratios, without the size bounds that the rule puts on the headline share.
11. The index-ETF-only and index-mutual-fund-only excess over the stock share restrict both the index and the active arm to the same ETF status, and use the matching stock share.
12. Anchors use funds whose cash Treasury value or gross futures face exceeds 1% of net assets in the 2023Q4 base survivors; futures in the anchors are those of that universe only, and the notes-and-bonds side is the cash build's coupon and TIPS lines of the same funds.
13. The heavy passes over the N-PORT zips run one zip at a time into a scratch directory outside the repository (stage A and stage B), so that no command outlasts a tool timeout; the final build reads those files and is otherwise unchanged.
14. The modelled cheapest-to-deliver shown per contract and window is that of the delivery month with the largest kept face in that window.
15. The remaining term of the 20-year bond future's deliverables uses the same quarter rounding as the other contracts, as stated in the rules; the word BOND is matched as a substring and BD as a whole word.
16. The unflagged group holds series with a type box ticked beside the not-applicable box, and series with no usable N-CEN row at all.
17. The per-contract median check on notional per face is run on the base vintage in every window; a contract and window with too few lines is skipped and counted, not passed.
18. The two real-data pins on the 2024q1 zip (the counts by category and unit, and the three notional-per-face medians) are printed as flags, not hard checks.
19. Series without any N-CEN row are kept in the ex-ETF anchors (they are not flagged as ETFs) and are counted separately.
20. The real column names differ from the specification in two places: the submission-type column is SUBMISSION_TYPE, and the feeder table links to the master through FUND_ID.
21. In the real data the index box carries only Y and blank, never N, and the only submission types are N-CEN and N-CEN/A, so the rule that ignores late-filing notices never fires.
22. The size of the unresolved share of futures face (the share that must stay at or under 10% at each end) was built as follows. Numerator: the unresolved lines and the conflicting lines, each at its filed notional (a line with no filed notional counts as zero), plus the Treasury lines with no long or short sign, each at its sized face. Denominator: that numerator plus the sized face of the kept lines. Expired lines, non-Treasury lines and Treasury lines with no usable size are in neither. This was fixed before the run and is recorded here after it; the label does not depend on it, since the share is about 3% at both ends against a 10% limit.
23. After the first futures run, with its numbers already printed, the builder expanded the README and verdict sentences so that they name the conditions that were not met, added three diagnostic rows to the file statistics (feeder series dropped, N-CEN records listing feeders, N-CEN series keys) and changed a default folder name. No computed number, rule, threshold or label changed.
24. After the independent check of the first results, the builder (a) counted the index-box and type-box check once per series row, not once per filing, (b) renamed the count of series without an N-CEN row to say that it covers the whole anchor universe, not only funds with futures, (c) rewrote the C-B7 and C-F8 notes and removed a column name from the README prose, (d) added boundary tests for the stale cutoff, the lower edge of the size-ratio band, the three share bars and the absolute values in the unclassified change, and (e) added complementary suppression: where a merged small cell is blanked, the smallest remaining amount cell of the same window or period is blanked too, so that a public total cannot give it back. No computed headline number, rule, threshold or label changed.
