# Spec: registered funds' Treasury futures in 10-year equivalents, and the index/active split of their cash Treasury duration (spec author, 19 Oct 2026; rewritten after supervisor rulings rounds 1-3)

*R2b's next step (`2026-10-15-R2b-Who-Took-The-Duration-Registered-Funds.md`). CALENDAR row 2026-11-12 (test B). Scoping: Grok g7 return 6
(`_research/2026-10-18-Grok-G7-Spec-Attacks.md`, fund futures, accepted by the supervisor) and Grok g8 parcel 2
(`_research/2026-10-19-Grok-G8-Returns.md`, N-CEN). The cash build this extends: `_research/2026-10-14-NPORT-Treasury-Duration-Spec.md`,
`bin/nport_treasury_duration.py`. House style follows `_research/2026-10-19-FX-Hedged-Treasury-Yield-Spec.md`.*

*This text folds in the supervisor's rulings of 19 Oct: the first round (B1-B4, F1, F3) and rounds 2 and 3 (R23-1 to R23-19). Both are
kept verbatim at the end as the record. **The body is authoritative and agrees with them.** Where a later ruling supersedes an earlier one,
the body says so: F3 is rescinded by R23-7 (§3.7), and B2 is merged into §4.1 by R23-10. "Observed" means seen by the spec author on 19 Oct
2026: one request per URL with the CLAUDE.md non-SEC User-Agent (four requests in all), or a read of the 2024q1 N-PORT zip in the Dropbox
companion (streamed, never copied). "Relayed" means taken from Grok, the second reviewer or the supervisor, and not re-read here. No sec.gov
URL was fetched by the spec author. ΔF and q were not computed on real data. The only real-data figures below are schema counts, units, signs
and coverage on the 2024q1 zip (all three of its report months), the tenor-map factors on the fixed curve, and the reviewer's indicative
sign figures (R23-1).*

## 0. Goal, what the result can and cannot say, and where this spec departs from its inputs

- **Part 1 (futures).** Measure registered funds' net Treasury-futures position in 10-year equivalents at each N-PORT window, and its change
  ΔF from the 2023Q4 window to the 2026Q2 window, on the cash build's survivors, lag and fixed end-2023 curve. One magnitude test: |ΔF| against $100bn.
- **Part 2 (test B).** Split R2b's measured cash arm (ΔS = $162.1bn of 10-year equivalents in 2026H1) into index funds and active funds with
  the N-CEN index flag. Test whether the index funds' share of the change is large, above their stock share, and rising.
- **It can say:** how large funds' Treasury-futures exposure is and how its net amount changed (MEASURED, with a stated conversion). It can
  also say what share of the funds' cash Treasury duration change sits in series flagged "Index Fund" on Form N-CEN (MEASURED on a stated
  classification).
- **It cannot say** what moved yields or term premia. Both parts are holder measurements. Futures are in zero net supply, so ΔF is never added
  to cash ΔS, never divided by the public's ΔP ($3,218.3bn), and never judged against R2b's $460bn line. `IS_INDEX` says a fund tracks *some*
  index. It does not say the index is the Bloomberg Aggregate, is market-cap weighted, or is a bond index. Closet indexers are coded active.
  **Required sentence (README and verdict files): "These are holdings measurements. They do not show what moved Treasury yields."**

**Departures and settled readings, each fixed before any data run:**
1. **The 3-year note future has a $200,000 face, not $100,000.** The supervisor frame said "$200,000 for the 2-year, $100,000 otherwise".
   Observed in the 2024q1 zip: on 14 US 3-year lines, NOTIONAL_AMOUNT / (contracts × $100,000) = 2.075-2.108. At $200,000 the ratio is
   about 1.04, in line with the other contracts. (Australian and Korean 3-year bond futures sit at 0.67-0.81; the currency condition of §3.2
   excludes them.) The face table is TU and Z3N $200,000, all others $100,000. A data guard (C-F4, §6) tests every face.
2. **N-CEN "fund type N/A" alone is the active case. CONFIRMED (B1).** The supervisor read Form N-CEN Item C.3 on sec.gov: an ordinary
   active fund is none of the listed types. N/A beside another type box is unclassified. The flag order is R23-9's (§4.1); it removes the
   earlier draft's contradiction between this departure and G12.
3. **No free dated CTD file exists** (CME's page refused the spec author's curl: observed 403). The pre-registered tenor map (§3.4) is the
   headline. The comparison uses a *modelled* cheapest-to-deliver from R2's own MSPD security master and curves (§3.5), labelled modelled.
   Basket rules follow the CBOT rulebook as Grok quoted it (R23-6, F1).
4. **Grok's extra inconclusive clauses for test B** (ETF-only gap, `IS_INDEX_EXCLUSIVE`, levered funds crossing a bar, stable-vs-all gap)
   are printed flags only (B3).
5. **Superseded rulings.** F3 (a mutual-funds-only anchor) is **RESCINDED** by R23-7: the anchors stay on all registered funds (§3.7). B2
   (the backfilled flag) is **MERGED** into §4.1 by R23-10. Its strict variant is now called `q_strict`; the earlier name `q_backfill` is withdrawn.
6. **Reading of R23-5 for the synthetic tenor map (for the supervisor to confirm).** The 1/8-per-cent coupon rounding applies to the real
   deliverables of the modelled CTD (§3.5). Their coupons are already multiples of 1/8, so it changes nothing there except the guard. The
   synthetic par bond of the tenor map keeps its unrounded par-yield coupon, so the eight factors that the second reviewer re-derived
   (TY $78,153.01) stand as pins (C-F2). Rounding the synthetic coupon would move each factor by tens of dollars and would need new pins.

## 1. Hard requirements

- **R1. No network I/O in the build.** `bin/nport_futures_index.py` is stdlib only and makes no request of any kind. The N-PORT zips are
  already on disk. The N-CEN zips are fetched once **by the supervisor** with the declared SEC contact (§2.3); no agent sends `SEC_UA`.
- **R2. Bulk data stays on Dropbox, read in place.** Zips are read from the companion with `zipfile` as streams, never extracted, never copied
  to the Mac's disk. Nothing needs clean-up, because nothing is copied.
- **R3. Same selection and pricing as R2b, imported, not copied (R23-17).** Load `bin/nport_treasury_duration.py` with its own `load_by_path`
  pattern and call by name: `discover_zips`, `make_windows`, `load_zip_filings`, `scan_zip_holdings`, `select_vintage`, `assign_windows`,
  `drop_content_duplicates`, `check_unique_survivors`, `stream_survivor_lines`, `read_debt`, `build_mspd`, `decide_kind`, `Pricer`,
  `r2_fixed_curve`, `Ctx`, `Ctx.add` and `Ctx.process_lines`. A subclass of `Ctx` is allowed: per-series S, `q_M1` and A2's
  notes-and-bonds DV01 may need one. So is a new futures pass over holdings lines ending `\tFUT`. Any copied block carries a comment naming
  the function it copies. Hard check C-X1 proves the path (§6).
- **R4. Futures never touch cash.** No output column holds S + F, F / ΔP, F against $460bn, or a Z.1-scaled F. Part 1 takes no Z.1 input.
- **R5. Aggregates only.** No output header contains CUSIP, HOLDING_ID, ACCESSION_NUMBER, SERIES_ID, SERIES_NAME, REGISTRANT_NAME, LEI or
  CIK. No output exceeds 2,000 rows. No fund or registrant name appears in any output or the README (G9 mechanism). Cells covering fewer than
  five series or funds are merged or blanked (§5, R23-16). Exact column allowlists (§5) are transcribed into the committed
  `data/nport/fut_idx_columns.tsv`, one row per file: `file`, then `columns` with `|` separators. The code reads that file for header order
  and holds no copy of its own (G10 mechanism).
- **R6. Failure handling.** A hard-check FAIL writes all outputs to `data/nport/_FAILED_fut_idx/`, leaves committed files untouched and exits 2.
  A refusal (missing input, failed pre-flight) exits 1 and writes nothing. Nobody but the supervisor deletes `_FAILED_fut_idx/`.
- **R7. Determinism.** `math.fsum` for every aggregate; $bn and ratios to 6 dp; rows sorted; no wall-clock time in any file. Two runs give
  identical sha256 for every output.
- **R8. No causal wording** in the README, verdict files or printout (G14 list).
- **R9. Post-registration fixes** are recorded in a "Builder decisions" section of this spec, with the old values kept beside the new.

## 2. Data

### 2.1 N-PORT (both parts)

- **Files:** the eleven zips `2024q1_nport.zip` ... `2026q3_nport.zip` at
  `/Volumes/Dropbox/31 - Claude Cowork/Work/2026.08 - Third Derivative Research/private/data/vintages/nport_zips/` (observed: 11 files,
  406-507 MB each). Source: `https://www.sec.gov/files/dera/data/form-n-port-data-sets/YYYYqQ_nport.zip` (cash build docstring). sha256 pins
  are the cash build's `tsy_file_stats.csv`; C-X2 compares them.
- **Tables and headers** (observed; identical in 2024q1 and 2026q3):
  - `FUND_REPORTED_HOLDING`: `ASSET_CAT`, `DERIVATIVE_CAT` (last column), `BALANCE`, `UNIT`, `CURRENCY_CODE`, `CURRENCY_VALUE`,
    `PAYOFF_PROFILE`, `ISSUER_NAME`, `ISSUER_TITLE`, `ISSUER_CUSIP`, `HOLDING_ID`, `ACCESSION_NUMBER`.
  - `FUT_FWD_NONFOREIGNCUR_CONTRACT`: `HOLDING_ID, PAYOFF_PROFILE, EXPIRATION_DATE, NOTIONAL_AMOUNT, CURRENCY_CODE, UNREALIZED_APPRECIATION`.
  - `DESC_REF_OTHER`: `HOLDING_ID, DESC_REF_OTHER_ID, ISSUER_NAME, ISSUE_TITLE, CUSIP, ISIN, TICKER, OTHER_IDENTIFIER, OTHER_DESC`.
  - `DESC_REF_INDEX_BASKET`: `HOLDING_ID, INDEX_NAME, INDEX_IDENTIFIER, NARRATIVE_DESC`.
  - `DESC_REF_INDEX_COMPONENT`: `HOLDING_ID, ..., NAME, CUSIP, ISIN, TICKER, OTHER_IDENTIFIER, OTHER_DESC, NOTIONAL_AMOUNT, ...`.
  - `IDENTIFIERS` (292 MB uncompressed in 2024q1; stream it against the futures ID set): `HOLDING_ID, IDENTIFIERS_ID, IDENTIFIER_ISIN,
    IDENTIFIER_TICKER, OTHER_IDENTIFIER, OTHER_IDENTIFIER_DESC`.
  - `NONFOREIGN_EXCHANGE_SWAP` (`NOTIONAL_AMOUNT`, `CURRENCY_CODE`) and `SWAPTION_OPTION_WARNT_DERIV` (`PRINCIPAL_AMOUNT`, `SHARES_CNT`,
    `CURRENCY_CODE`): read only to print the excluded notional.
- **What the 2024q1 zip shows** (observed, whole zip, all report months; counts are lines):
  - DIR lines by `DERIVATIVE_CAT`: SWP 25,065, FUT 11,331, SWO 4,747, OPT 1,542, FWD 4.
  - Every `FUT_FWD` row is a FUT line. Of 26,824 rows, 11,331 are DIR, 8,348 DCO, 6,214 DE, 838 DFE, 53 DO and 35 OTHER. Lines whose text
    reads as a US Treasury future: 6,564 DIR, 18 OTHER, 15 DCO, 6 DE.
  - `UNIT` on FUT lines: NC (number of contracts) 11,329 of 11,331; OU 2.
  - Holding-level `PAYOFF_PROFILE` on FUT lines: N/A 10,176, blank 804, Long 193, Short 158. The sign lives on `FUT_FWD.PAYOFF_PROFILE`
    (Long 15,728, Short 10,148, N/A 948 of 26,824).
  - On USD Treasury-future lines (first-pass classifier, 6,852 lines): Long with BALANCE and NOTIONAL both positive 3,969; Short with both
    negative 2,494; some sign conflict 389 (Short with both positive 182; Short with BALANCE − and NOTIONAL + 119; Short with BALANCE + and
    NOTIONAL − 87; Long with BALANCE − 1). The second reviewer found the conflicts concentrated in large lines. On the whole 2024q1 zip,
    net F was $133.1bn with the PAYOFF sign and $199.9bn with the BALANCE sign, and implied futures duration was 3.07 against 4.01 years.
    These are indicative figures, not window values (relayed; R23-1).
  - `NOTIONAL_AMOUNT` / (|BALANCE| × face), median: TU 1.021, FV 1.067, TY 1.098, TN 1.136, US 1.168, UB 1.224. This is trade-date contract
    value (price × face), as the form says (relayed, Item C.11.d.iv). It confirms that BALANCE is a contract count.
  - `CURRENCY_VALUE` equals `UNREALIZED_APPRECIATION` (within 1% or $1) on 89% of these lines; median |UA| / |notional| is 2.0%. It is the
    mark, not the position.
  - Coverage: all 11,331 FUT IDs have an `IDENTIFIERS` row; 14,409 `DESC_REF_OTHER` rows and 3,074 `DESC_REF_INDEX_BASKET` rows attach to
    them; none attach in `DESC_REF_INDEX_COMPONENT`.
  - A first-pass classifier left 260 of 8,791 USD FUT lines unresolved (generic text such as "FUTURE" with only a Bloomberg FIGI). That is
    0.74% of the |notional| of Treasury-plus-unresolved lines, on a partial `DESC_REF_OTHER` join. Foreign bond futures (Euro-Bund,
    Australian and Korean 3-year, JGB) and SOFR futures often carry `CURRENCY_CODE` USD. A USD currency is therefore necessary but not
    sufficient (§3.2).

### 2.2 R2 caches and committed files (both parts)

Read-only, as the cash build reads them: `--r1-cache data/vintages/r1_treasury` (daily nominal and real curves); `--r2-cache
data/vintages/r2_treasury` (MSPD Table 3 at 2023-12-31, 2024-12-31, 2025-12-31, 2026-06-30, 2026-07-31, 2026-08-31, and the SOMA files);
committed `data/nport/tsy_windows.csv` and `tsy_change.csv` (the C-X1 targets). Observed: each MSPD row carries `security_class1_desc`, the
CUSIP in `security_class2_desc`, `interest_rate_pct`, `issue_date` and `maturity_date`, one row per tranche; 830 rows at 2023-12-31. Original
term = maturity minus the earliest `issue_date` of the CUSIP.

### 2.3 N-CEN (Part 2): the supervisor fetches

- **Landing page** (SEC; the supervisor read it on 19 Oct): Form N-CEN Data Sets, `https://www.sec.gov/dera/data/form-ncen-data-sets`.
  It says the data sets "do not include, at this time, N-CEN filings submitted in the schema version 3.1 introduced in EDGAR version 25.2"
  (relayed from the supervisor). So 2025-26 flags can be stale or missing (§4.1, `stale_flag`).
- **Files: 2022q1 to 2026q3, 19 zips.** File names were observed on 19 Oct in the data.gov catalogue page
  `https://catalog.data.gov/dataset/form-n-cen-data-sets` (HTTP 200, 213,226 bytes; its CKAN API path returned 404). All sit under
  `https://www.sec.gov/files/dera/data/form-n-cen-data-sets/`:
  - `2022q1_ncen.zip` ... `2023q4_ncen.zip` (8 files);
  - `2024q1_ncen_0.zip`, `2024q2_ncen_0.zip`, `2024q3_ncen_0.zip`, `2024q4_ncen_0.zip`, `2025q1_ncen_0.zip`, `2025q2_ncen_0.zip`;
  - `2025q3_ncen.zip`, `2025q4_ncen.zip`, `2026q1_ncen.zip`, `2026q2_ncen.zip`;
  - the 2026q3 name is resolved by the supervisor from the SEC page when fetching (B4).

  Where the SEC page shows a different name, the SEC page wins, and the name is recorded in `fut_idx_file_stats.csv`.
- **Span.** The earliest N-PORT report date in use is November 2023. The 2022q1 start gives at least 18 months of earlier filings for every
  window. A period older than the earliest zip cannot be seen; a series whose only earlier filing is older counts as having none (§4.1). A
  backfilled flag (§4.1) can only come from filings up to the 2026q3 zip, so backfill for the 2025Q4 and 2026Q2 windows is truncated by the
  data, not by the rule. The README says so.
- **Fetch rules (supervisor):** `SEC_UA` from the companion's `keys/secrets.env`; www.sec.gov only; sequential, at least 1 s apart, GET only.
  Any status other than 200 writes `ncen_zips/STOP` and ends the fetch; only the supervisor deletes it. Store the files as published in
  `.../private/data/vintages/ncen_zips/` on the Dropbox companion. Add one `private/MANIFEST.tsv` row: "SEC bulk N-CEN, kept out of git for
  size; derived aggregates only are committed".
- **Tables and fields** (relayed from the N-CEN readme via Grok and R23-9/R23-12). C-B1 checks every name on the real headers and refuses
  on a missing one. The builder reports any name that differs (R9):
  - `SUBMISSION`: `ACCESSION_NUMBER`, the submission-type column, `FILING_DATE`, `REPORT_ENDING_PERIOD`;
  - `REGISTRANT`: `CIK`;
  - `FUND_REPORTED_INFO`: `ACCESSION_NUMBER`, `SERIES_ID`, `IS_ETF`, `IS_ETMF`, `IS_INDEX`, `IS_MULTI_INVERSE_INDEX`, `IS_INTERVAL`,
    `IS_FUND_OF_FUND`, `IS_MASTER_FEEDER`, `IS_MONEY_MARKET`, `IS_TARGET_DATE`, `IS_UNDERLYING_FUND`, `IS_FUND_TYPE_NA`,
    `IS_INDEX_AFFILIATED`, `IS_INDEX_EXCLUSIVE`;
  - `FEEDER_FUNDS`: `REGISTERED_SERIES_ID`, in the master's filing.

  `MASTER_FUNDS` is not used (R23-12).
- **Timing:** N-CEN is annual, due 75 days after fiscal year-end, plus up to 15 days on Form 12b-25 (relayed). The zip is quarterly by
  filing date.

### 2.4 Anchor and contract sources

- **FEDS Note, Iorio, Li and Petrasek, 10 May 2024**, and its accessible data page,
  `https://www.federalreserve.gov/econres/notes/feds-notes/why-do-mutual-funds-invest-in-treasury-futures-accessible-20240510.htm`
  (observed 200, 98,632 bytes; the note page 200, 105,026 bytes). Federal Reserve material is public domain.
  - **Figure 5** ("Treasury Funds" = mutual funds with more than 1% of their portfolio in Treasury securities or Treasury futures), 2023Q4:
    - Treasury-futures net notional 3.13779E+11; notes-and-bonds net notional 5.81853E+11.
    - DV01: futures 117,752,385.4; notes and bonds 388,686,063.2. The table is headed "Millions of $", which the arithmetic contradicts.
      The ratios do not depend on the unit.
    - Derived: DV01 ratio 0.3030; implied futures duration 117,752,385.4 / (3.13779E+11 × 1e-4) = 3.753 years (reviewer 3.7528);
      notes and bonds 6.680 years.
  - **Figure 3 and text** (printed comparison only): mutual funds' long 2- and 5-year futures exposure is about $370bn at end-2023, and 10-
    and 30-year about $100bn; the text says "roughly $500 Billion". Together about $470-500bn of long exposure.
  - The note's sources include N-CEN and J.P. Morgan Markets durations.
- **CME/CBOT contract rules** (deliverable baskets, faces, conversion factor): the spec author's request to `cmegroup.com` returned 403. Grok
  fetched CBOT rulebook chapters 18, 19, 20, 21, 26, 39 and 40 and the CBOT conversion-factor article, and the supervisor ruled on them
  (R23-5, R23-6; F1). Where the 2024 CME explainer disagrees with the rulebook, the rulebook wins. The README names the explainer text that
  disagreed: the earlier draft measured the TU and Z3N remaining terms from the last day of the delivery month and omitted TY's original-term limit.

## 3. Method, Part 1: futures

### 3.1 Universe

The cash build's survivors per window and vintage (base: every zip, FILING_DATE ≤ REPORT_DATE + 62 days; matched: zips up to the home zip),
one report per fund per window, same fund key. Keep a holding line when `DERIVATIVE_CAT` = FUT (any `ASSET_CAT`) and the classifier of §3.2
names a US Treasury contract. Non-DIR Treasury lines are counted separately as `non_dir_tsy_lines`. Drop lines whose `EXPIRATION_DATE` is
before the REPORT_DATE, and count them as `expired_lines`.

### 3.2 Classifier (a matching rule is a hypothesis, C-059; R23-4)

**Step 0, a necessary condition:** `FUT_FWD.CURRENCY_CODE` = USD, or blank with a US exchange marker in any text source (`CBT`, `CBOT`,
`CHICAGO BOARD`, `BOARD OF TRADE`, `XCBT`, `CME`). Otherwise the line is non-Treasury (`non_usd`).

Text sources, in order: (a) holding `ISSUER_NAME` + `ISSUER_TITLE`; (b) `DESC_REF_OTHER` `ISSUE_TITLE`, `ISSUER_NAME`, `TICKER`, `OTHER_DESC`;
(c) `DESC_REF_INDEX_BASKET` `INDEX_NAME`, `NARRATIVE_DESC`; (d) `IDENTIFIERS` `IDENTIFIER_TICKER`, `OTHER_IDENTIFIER`, `OTHER_IDENTIFIER_DESC`.
Upper-case each source and collapse its spaces. Then, for each source in turn:
1. **Non-Treasury first.** Any of `SOFR`, `EURODOLLAR`, `EURO` (with or without a hyphen), `FED FUND`, `30 DAY`, `BUND`, `BOBL`, `SCHATZ`,
   `BUXL`, `FGBX`, `FGBL`, `FGBM`, `FGBS`, `OAT`, `BTP`, `GILT`, `JGB`, `JPN`, `OSAKA`, `AUST`, `KOREA`, `CAN 10`, `CANADA`, an equity-index,
   commodity or crypto name, `OPTION`, `OPTN`, `\bPUT\b` or `\bCALL\b` → non-Treasury.
2. **Ticker root** `\b(TU|3Y|FV|TY|UXY|TN|TWE|US|WN|UB)[FGHJKMNQUVXZ]\d{1,2}\b` → that contract (3Y = Z3N; UXY = TN; WN = UB). The root
   `UB` counts only when `FUT_FWD.CURRENCY_CODE` is USD; blank is not enough.
3. **Text**, only if a US marker is present (`\bUS\b`, `U.S.`, `UST`, `TREASURY`, `CBT`, `CBOT`, `CHICAGO BOARD`, `BOARD OF TRADE`, `XCBT`).
   **Tenor is tested before `BOND|BD`.**
   - With `ULTRA`: tenor 10 (`\b10\s*-?\s*(YR|YEAR|Y)\b` or `ULTRA 10`) → TN; tenor 30 → UB; then `BOND|BD` → UB; then `NOTE` → TN.
   - Without `ULTRA`: tenor 2 (or `TWO YEAR`) → TU; 3 → Z3N; 5 → FV; 10 → TY; 20 → TWE; 30 → US; then `LONG BOND|T-BOND|TREASURY BOND`
     → US.
   - A tenor n matches `\bn\s*-?\s*(YR|YEAR|Y)\b`.
4. The first source that resolves decides. Two sources that resolve to different contracts → `unresolved_conflict`. When nothing resolves,
   the line is `unresolved` if its text holds a US marker or a generic word (`FUTURE`, `GOVERNMENT`), else non-Treasury.

**Fixtures (G2; with the digits the zips carry; currency USD unless stated):**
- TU: "US 2YR NOTE (CBT) Mar24".
- Z3N: "US 3YR NOTE (CBT) MAR24"; "FUTURE" with IDENTIFIERS ticker "3YH4".
- FV: "US 5YR NOTE (CBT) FUT MAR24 FVH4"; "U.S. TREASURY 5 YEAR NOTE".
- TY: "US 10YR NOTE (CBT)MAR24"; "FUTURE" with IDENTIFIERS ticker "TYH4".
- TN: "US 10YR ULTRA FUT MAR24"; "UST 10YR FUT ULTRA UXYH4 03-19-24"; "U.S. TREASURY 10 YEAR ULTRA BONDS" with ticker UXYH4.
- UB: "US ULTRA BOND CBT MAR24"; "U.S. TREASURY 30 YEAR ULTRA BONDS".
- US: "US LONG BOND(CBT) MAR24".
- Non-Treasury:
  - "10 Year Treasury Bond Futures", ASX, currency AUD (fails step 0);
  - Euro-Buxl with ticker "UBH4", currency EUR (fails step 0; UB needs USD);
  - "US 10YR FUT OPTN JAN24P 110" (OPTN);
  - "AUST 3YR BOND"; "KOREA 3YR BND FUT MAR24"; "THREE-MONTH SOFR"; "EURO-BUND";
  - "NYMEX HENRY HUB NATURAL EUROPEAN STYLE OPTION";
  - currency blank with no US exchange marker.
- Unresolved: "FUTURE" with only "BBG00XXXXXXX".
- Passes step 0: currency blank with "CBT" in the title.

### 3.3 Sign and size (never both measures on one line; R23-1, R23-3)

- **Sign (primary)** = +1 if `FUT_FWD.PAYOFF_PROFILE` is Long, −1 if Short. N/A or blank → `sign_na`: excluded from F, counted, |notional| printed.
- **Sign (comparison, R23-1):** on the same kept lines, sign(BALANCE) where BALANCE ≠ 0, else the PAYOFF sign. This gives ΔF_bal, and with
  it G_s (§4.3). The notional of lines whose two signs disagree is printed as a share of kept |notional|. A1-A3 are also printed under the
  BALANCE sign (§3.7). PAYOFF stays primary, as registered.
- **Contracts** = |BALANCE| when `UNIT` = NC and |BALANCE| is a whole number ≥ 1 (within 1e-6): a "valid count".
- **Face per contract:** TU $200,000; Z3N $200,000; FV, TY, TN, TWE, US, UB $100,000.
- **Basis per line**, first rule that fits:
  1. valid count and |NOTIONAL_AMOUNT| within 1% of |BALANCE|: the notional field holds a contract count. Face basis, counted as
     `notional_field_is_count`.
  2. valid count and NOTIONAL blank, or |NOTIONAL_AMOUNT| / (contracts × face) in [0.5, 2.0]: face basis (contracts × face).
  3. valid count and that ratio outside [0.5, 2.0]: notional basis (|NOTIONAL_AMOUNT| as the face proxy), counted as `unit_suspect`.
  4. no valid count and NOTIONAL non-blank and non-zero: notional basis.
  5. no valid count and NOTIONAL blank or zero: excluded, counted as `no_size`.
  Lines and $ by basis are printed.
- `CURRENCY_VALUE` and `UNREALIZED_APPRECIATION` never size a position (G4).

### 3.4 Headline conversion: the pre-registered tenor map

Each contract is represented by a synthetic deliverable at the shortest remaining term of its basket, measured from the first day of the
delivery month. With yields below the 6% conversion coupon, the cheapest-to-deliver sits at the short end of the basket. The synthetic
deliverable is a par bond on the fixed curve (2023-12-29, d10 = 8.2233). Its coupon is the curve's par yield at T, unrounded (Departure 6).
Its CF comes from §3.5's formula at that coupon and T, rounded to 4 dp. Per contract:
`tenyeq = face × par_mod_duration(y_T, n=T) / CF / d10`, with unrounded duration and d10 (R23-5). Expiry is never added to T.

| Contract | T (years) | face | y_T % | duration | CF | 10y-eq per contract ($) |
|---|---|---|---|---|---|---|
| TU | 1.75 | 200,000 | 4.3700 | 1.6673 | 0.9732 | 41,667.39 |
| Z3N | 2.75 | 200,000 | 4.0650 | 2.5772 | 0.9515 | 65,875.55 |
| FV | 4 2/12 | 100,000 | 3.9108 | 3.8107 | 0.9239 | 50,157.56 |
| TY | 6.5 | 100,000 | 3.8700 | 5.6986 | 0.8867 | 78,153.01 |
| TN | 9 5/12 | 100,000 | 3.8800 | 7.8254 | 0.8511 | 111,810.44 |
| US | 15 | 100,000 | 4.0400 | 11.1675 | 0.8079 | 168,094.85 |
| TWE | 19 2/12 | 100,000 | 4.1733 | 13.1048 | 0.7946 | 200,557.12 |
| UB | 25 | 100,000 | 4.1150 | 15.5236 | 0.7575 | 249,209.94 |

(Spec author, with R2's `interp_curve` and `par_mod_duration` on the real fixed curve; all eight re-derived by the second reviewer. CF uses
n = whole years and z = months rounded down, to whole months for TU, Z3N and FV and to quarters for the others. The builder reproduces each
to $0.01, C-F2.) F at a window = Σ sign × contracts × factor, in $bn. For a notional-basis line the term is |NOTIONAL_AMOUNT| / face × factor.

### 3.5 Comparison conversion: the modelled CTD (R2-date windows only; R23-5, R23-6)

- **Delivery month** = the month of `EXPIRATION_DATE`. FDM = its first day. **Every term runs from FDM.**
- **Basket** at window date d (2023-12-31, 2024-12-31, 2025-12-31, 2026-06-30), from MSPD Table 3 at record date d. Classes Notes and Bonds
  only, so principal and coupon are fixed; no TIPS, FRNs or bills. Remaining term from FDM is rounded down to a whole month for TU, Z3N and
  FV, and to a whole quarter for the others, before testing. Original term is in whole months, rounded down. Rules (CBOT rulebook, as Grok
  quoted it):

  | Contract | Classes | Original term | Remaining term from FDM |
  |---|---|---|---|
  | TU | Notes | ≤ 5y3m | ≥ 1y9m and ≤ 2y |
  | Z3N | Notes | ≤ 7y | ≥ 2y9m and ≤ 3y |
  | FV | Notes | ≤ 5y3m | ≥ 4y2m |
  | TY | Notes | ≤ 10y | ≥ 6y6m and < 8y |
  | TN | Notes | ≤ 10y | ≥ 9y5m and ≤ 10y |
  | TWE | Notes and Bonds | — | ≥ 19y2m and ≤ 19y11m |
  | US | **Bonds only** | — | ≥ 15y and < 25y |
  | UB | **Bonds only** | — | ≥ 25y |

- **CF** (CBOT, at 6%):
  - c = the coupon rounded to the nearest 1/8 per cent, ties up: c = floor(8 × coupon_pct + 0.5) / 8 / 100.
  - n whole years and z months from FDM to maturity, z rounded down as above.
  - v = z if z < 7, else z − 6.
  - a = 1.03^(−v/6); b = (c/2)(6 − v)/6.
  - k = 1.03^(−2n) if z < 7, else 1.03^(−(2n+1)); d = (c/0.06)(1 − k).
  - CF = round(a(c/2 + k + d) − b, 4).

  Fixtures:
  - 6% at z = 0 or z = 6 → 1.0000; 6% at any other z → 0.9999 (the earlier "any term → 1.0000" fixture is deleted);
  - 4%, 4y3m (month rounding) → 0.9259; 4.5%, 15y0m → 0.8530; 2%, 6y6m (quarter rounding) → 0.7873;
  - a coupon of 4.0625% rounds to 4.125% (a tie goes up).
- **CTD** = argmin over the basket of P_own / CF. P_own is R2's `coupon_price_duration` clean price at T from FDM, on the curve of
  `on_or_before(d)`. Ties go to the shorter maturity, then the lower coupon. Carry and delivery options are ignored, which is why it is
  labelled modelled.
- `tenyeq` per contract = face × P_fixed/100 × D_fixed / CF / d10, with the CTD priced on the fixed curve at T from FDM. An empty basket
  falls back to the tenor map and is counted as `ctd_fallback_lines`; this happens when new issues are missing from the record date.

### 3.6 Printed beside, never in F, never a decision input (R23-8)

- Per window: gross |notional| of DIR interest-rate swaps; DIR options and swaptions (`PRINCIPAL_AMOUNT`, else `SHARES_CNT` as a count
  only); non-Treasury interest-rate futures (SOFR, fed funds); foreign and non-USD bond futures; unresolved futures; sign-N/A futures.
- DV01 by contract: tenor-map 10-year equivalents × d10 × 1e-4, in $mn per bp.
- The ΔF split into continuing funds (a survivor at both ends), entrants (2026Q2 only) and leavers (2023Q4 only), per period.
- The sign-disagreement notional share, and A1-A3 under the BALANCE sign (§3.3).

### 3.7 Anchors at 2023Q4 (decision inputs; F3 RESCINDED by R23-7)

**F3 is rescinded.** The first-round ruling put the anchors on mutual funds only. That needs N-CEN's `IS_ETF`, which `futures` mode does not
have, and the FEDS note does not say that ETFs are excluded. The anchors therefore cover **all registered funds**.

Universe "Treasury funds": base-vintage 2023Q4 survivors whose clean cash Treasury value, or whose gross Treasury-futures face, exceeds 1% of
NET_ASSETS.
- **A1** net Treasury-futures face in [$250bn, $380bn] (FEDS: 313.8).
- **A2** futures DV01 / notes-and-bonds DV01 in [0.20, 0.45] (FEDS: 0.303).
  - Futures DV01 = F_tenor × d10 × 1e-4.
  - Notes-and-bonds DV01 comes from the cash build's coupon and TIPS lines in the same universe (a `Ctx` subclass may supply it, R3).
  - At 2023Q4 the fixed curve is that date's own curve.
- **A3** implied futures duration, F_tenor × d10 / net face, in [3.0, 4.5] years (FEDS: 3.75).
- **Printed beside, not decision inputs:**
  - A1-A3 under the BALANCE sign;
  - when N-CEN is present (`idx` mode), A1-A3 ex-ETF, where ex-ETF = `IS_ETF` ≠ Y, with series that have no N-CEN row counted separately;
  - **A4**: all-fund gross long face against the FEDS Figure 3 reading of about $470-500bn.

## 4. Method, Part 2: test B

### 4.1 Flag per series per window (B2 MERGED here by R23-10; R23-9, R23-11, R23-12)

- **Filings.** Keep `N-CEN` and `N-CEN/A`; ignore `NT` notices. For each (SERIES_ID, REPORT_ENDING_PERIOD) keep the latest FILING_DATE, then
  the highest accession. An amendment restates the whole form.
- **Primary flag source (B2, merged).** For an N-PORT survivor with REPORT_DATE r:
  - use the latest kept N-CEN with REPORT_ENDING_PERIOD ≤ r;
  - if the series has no such filing (for example a fund launched after its last earlier N-CEN), use its **first later** N-CEN (the
    earliest REPORT_ENDING_PERIOD > r) with FILING_DATE ≤ r + 15 calendar months, labelled `flag_backfilled`;
  - otherwise the series is `unflagged`.
- **Strict variant `q_strict`** (formerly `q_backfill`; a printed sensitivity, never the primary): the same rule with no backfill.
- **CIK-keyed N-PORT funds** (no SERIES_ID) join to an N-CEN `FUND_REPORTED_INFO` row with blank SERIES_ID only when the registrant CIK has
  exactly one such row in that filing; otherwise `unflagged`.
- **Flag value, in exactly this order (R23-9):**
  1. `mmf` if IS_MONEY_MARKET = Y;
  2. else `unflagged` if IS_FUND_TYPE_NA = Y and any of IS_ETF, IS_ETMF, IS_INDEX, IS_MULTI_INVERSE_INDEX, IS_INTERVAL, IS_FUND_OF_FUND,
     IS_MASTER_FEEDER, IS_TARGET_DATE, IS_UNDERLYING_FUND = Y;
  3. else `levinv` if IS_MULTI_INVERSE_INDEX = Y;
  4. else `index` if IS_INDEX = Y;
  5. else `active`.

  N/A alone is therefore active (B1). Any IS_INDEX value other than Y (N, blank) is not an index flag.
- **Stale flag (R23-11).** A series that is a survivor at the 2026Q2 window gets `stale_flag` if its flag there comes from an N-CEN period
  ending more than 15 months before 2026-06-30, that is before 2025-03-30. This is the schema-3.1 omission.
- **Feeders (R23-12).** Feeders are identified only through `FEEDER_FUNDS.REGISTERED_SERIES_ID` in the master's flag-source filing for that
  window. A feeder series that is a survivor in the same window as its master has its cash Treasury S set to zero in that window. The
  removed amount forms the `feeder_dropped` group. `MASTER_FUNDS` is not used.

### 4.2 Groups, q and the decision rule (fixed now)

- **Windows:** the R2-date windows 2023Q4, 2024Q4, 2025Q4 and 2026Q2, base vintage (R2b's M0). S is the series' cash 10-year equivalents on
  the fixed curve, exactly as R2b computes it (C-X1). A series absent from a window has S = 0 there.
- **Series group**, one per series, taken over the windows where it is a survivor. First that fits:
  1. `mmf` if any window says mmf;
  2. `levinv` if any says levinv;
  3. `unflagged` if any window is unflagged;
  4. `stale_flag` (§4.1);
  5. `index_stable` or `active_stable` if every window gives the same flag (backfilled flags count as flags);
  6. otherwise `switcher`.

  Entrants and leavers are stable if their present windows agree. An entrant is a series absent at 2025Q4 and present at 2026Q2.
- **Periods:** 2024 = 2023Q4→2024Q4; 2025 = 2024Q4→2025Q4; 2026H1 = 2025Q4→2026Q2.
- **Base, re-derived from `data/nport/tsy_change.csv` (M0) on 19 Oct:** 2026H1 ΔS = 1,936.986234 − 1,774.882741 = **162.103494**; 2024
  203.17863; 2025 183.958587; full 549.24071. The partition identity (C-B3) ties every period to these.
- **q_p, bounded (R23-13).** q_p = ΔS(index_stable) / [ΔS(index_stable) + ΔS(active_stable)]. It is defined only if all three hold:
  - ΔS(index_stable) ≥ 0;
  - ΔS(active_stable) ≥ 0;
  - their sum is at least 25% of that period's M0 ΔS: $50.79bn for 2024, $45.99bn for 2025, $40.53bn for 2026H1.

  Otherwise that period is undefined. Printed beside it: the index share of all groups' ΔS.
- **s0** = S(index_stable, 2023Q4) / [S(index_stable, 2023Q4) + S(active_stable, 2023Q4)].
- **Unclassified 2026H1:** U = |ΔS(unflagged)| + |ΔS(switcher)| + |ΔS(stale_flag)|, each over 2026H1. Every entrant with no earlier and no
  backfilled flag is in `unflagged`, so unflagged entrants feed U through that group. Their part is printed as its own component, as is
  each term. **The U cap is the literal $16.2bn (R23-14).**
- **Pre-run input from the cash build alone (R23-11).** `futures` mode writes `idx_prerun.csv`: the number of entrants and their 2026H1 ΔS.
  `idx` mode adds how many of them are unflagged and how many are backfilled. If unflagged-entrant change plus stale-flag change exceeds
  $16.2bn, the verdict is INCONCLUSIVE by construction, and the README says so.
- **Rule, evaluated in this order:**
  1. **INCONCLUSIVE** if U > $16.2bn, or if q_2024, q_2025 or q_2026H1 is undefined.
  2. **SUPPORTS** if q_2026H1 ≥ **0.60**, q_2026H1 − s0 ≥ **0.15**, q_2026H1 − q_2024 ≥ **0.10** and q_2026H1 − q_2025 ≥ **0.10**. The
     verdict sentence: "Series flagged 'Index Fund' on Form N-CEN (any index, not only Treasury indexes) took a much larger and rising share
     of registered funds' classified cash Treasury duration change."
  3. **AGAINST** if q_2026H1 ≤ **0.40** and q_2026H1 − s0 ≤ **0**.
  4. Otherwise **INCONCLUSIVE**.

  Bounds are inclusive. With U = 0 and the whole base classified, 60% is $97.26bn and 40% is $64.84bn of $162.10bn.
- **The 0.15 bar (R23-15)** is a pre-registered hurdle, taken from a different object (R2b's 29.2% − 14.5% excess of funds over their
  share of the public stock) after that object was measured. It is not a sampling bound.
- **Resolution, in place of an MDE (C-090):** this is a measurement, not a test against noise. At the U cap, unclassified change could move
  q by about ±10 points, so a q within 10 points of a bar is fragile. The README says so.
- **Printed flags, not in the rule:**
  - q_all (switchers by their 2026Q2 flag); q_strict (no backfill); q_levinv_in (levinv added to the index arm); q_M1 (matched vintage);
  - the index share of all groups' ΔS;
  - the `IS_ETF` × arm cross-tab; index-ETF-only and index-mutual-fund-only excess over s0;
  - the `IS_INDEX_EXCLUSIVE` share of the index change;
  - Grok's extra clauses, each as a yes/no flag (B3).

### 4.3 Part 1 decision rule (fixed now)

ΔF = F(2026Q2) − F(2023Q4), tenor map, base vintage, PAYOFF sign.
- **U_F** = |notional| of unresolved, conflicting and sign-N/A Treasury-candidate lines / |notional| of kept plus those lines, at each endpoint.
- **G_v** = |ΔF(base) − ΔF(matched)|.
- **G_c** = |ΔF(tenor) − ΔF(CTD)|.
- **G_s** = |ΔF(PAYOFF sign) − ΔF(BALANCE sign)| (R23-1).

The labels:
- **LARGE** if |ΔF| ≥ **$100bn**, A1-A3 pass, U_F ≤ 10% at both endpoints, G_v ≤ **$20bn**, G_c ≤ **$50bn** and G_s ≤ **$20bn**.
- **SMALL** if |ΔF| < $100bn, with the same conditions.
- **INCONCLUSIVE** otherwise.

The sign of ΔF and the half-year values are printed; they are not a second test. The relayed $120bn and the $10.3bn scaled-arm gap are not
thresholds.

## 5. Outputs (all under `data/nport/`; exact headers in this order)

| File | One row per | Columns |
|---|---|---|
| `fut_windows.csv` | window × vintage | `window, quarter_end, vintage, funds_in_window, funds_with_tsy_fut, tsy_fut_lines, contracts_long, contracts_short, face_long_bn, face_short_bn, face_net_bn, notional_tradedate_net_bn, tenyeq_tenor_bn, tenyeq_tenor_balsign_bn, tenyeq_ctd_bn, unrealized_abs_bn, lines_basis_face, lines_basis_notional, notional_field_is_count_lines, unit_suspect_lines, no_size_lines, non_usd_lines, unresolved_lines, unresolved_conflict_lines, sign_na_lines, sign_disagree_lines, sign_disagree_notional_share, expired_lines, non_dir_tsy_lines, ctd_fallback_lines, unresolved_share` |
| `fut_contracts.csv` | window × contract (base) | `window, contract, funds_n, lines, contracts_net, face_net_bn, tenyeq_tenor_bn, tenyeq_ctd_bn, dv01_tenor_mn, tenor_factor_usd, ctd_factor_usd, ctd_maturity, ctd_coupon_pct, ctd_cf, notional_over_face_median` |
| `fut_change.csv` | variant × period | `variant_id, description, period, f_start_bn, f_end_bn, d_f_bn` (T0 tenor base; T1 tenor matched; C0 CTD base; B0 tenor base with the BALANCE sign; periods full/2024/2025/2026H1) |
| `fut_split.csv` | period × group (T0) | `period, group, funds_n, d_f_bn` (groups continuing/entrant/leaver) |
| `fut_other_deriv.csv` | window × category (base) | `window, category, lines, notional_abs_bn` |
| `fut_verdict.csv`, `idx_verdict.csv` | key | `key, value` (keys from §3.7, §4.2 and §4.3; the first key is `required_sentence`) |
| `idx_prerun.csv` | key | `key, value` (entrants_n, entrants_ds_2026h1_bn, u_cap_bn; `idx` mode adds entrants_unflagged_n, entrants_backfilled_n) |
| `idx_split.csv` | period × group | `period, group, series_n, s_start_bn, s_end_bn, d_s_bn` (periods 2024/2025/2026H1/full) |
| `idx_coverage.csv` | window × flag | `window, flag, flag_backfilled_n, series_n, s_bn` |
| `idx_crosstab.csv` | period × is_etf × arm | `period, is_etf, arm, series_n, s_start_bn, d_s_bn` |
| `fut_checks.csv`, `idx_checks.csv` | check | `check_id, label, ours, reference, threshold, result, hard, note` |
| `fut_idx_file_stats.csv` | key | `tag, key, value` (zip names, sha256, sizes, header lists, counts by reason) |

**Small cells (R23-16; applied to `idx_split.csv`, `idx_crosstab.csv`, `idx_coverage.csv`, `fut_contracts.csv`, `fut_split.csv` and
`idx_prerun.csv`).** `tsy_top_funds.csv` names series, so a small cell could be matched to one of them.
- Any row whose `series_n` (or `funds_n`) is below 5 is merged into one `other_small` row per period, window or file. The merged row carries
  the summed counts and amounts; per-contract CTD fields are blank there.
- If `other_small` itself covers fewer than 5, its amounts are blanked and only its count is shown.
- In `idx_prerun.csv`, an entrant count below 5 blanks the ΔS.
- C-B3 and every decision input are computed in memory before suppression. The verdict keys are aggregates over at least the 25%-of-base
  denominator, so they are not suppressed.

**`fut_idx_README.md` (generated; R23-19), in this order:**
1. Two plain opening sentences: what was measured, and the required sentence.
2. **Definitions, before any result:** 10-year equivalent; Treasury future and contract face; net change in funds' futures; tenor map;
   conversion factor; modelled cheapest-to-deliver; Form N-CEN and the "Index Fund" box; stable sample; unclassified change.
3. The futures verdict as a full sentence stating its claim, in words. For example: "The net change in registered funds' Treasury futures
   from end-2023 to mid-2026 was [large / small / not established], at $X bn of 10-year equivalents against a $100bn line." Then why futures
   are not added to cash holdings.
4. The test-B verdict as a full sentence (the SUPPORTS sentence of §4.2, or its AGAINST or INCONCLUSIVE counterpart), with dollar figures
   and denominators.
5. What the "Index Fund" box cannot tell (any index; not market-cap or Aggregate; closet indexers count as active).
6. The schema-3.1 omission: flags for 2025-26 can be stale or missing, and if unflagged-entrant plus stale-flag change exceeds $16.2bn the
   verdict is inconclusive by construction.
7. The CME explainer text that disagreed with the rulebook (§2.4).
8. Provenance last.

No symbol (q, s0, U, ΔF, G_v, G_c, G_s) appears in README prose; column names appear only in a dictionary at the end. `fut_idx_SOURCES.md`:
every source of §2 with URL, terms and citation. Both files pass G14.

## 6. Checks (`fut_checks.csv`, `idx_checks.csv`)

**Hard (FAIL → `_FAILED_fut_idx/`, exit 2):**
- **C-X1** the imported selection and pricing reproduce `tsy_windows.csv` `tenyeq_fixed_bn` at the four R2 windows, base and matched, within
  1e-5 (2023Q4 base 1,387.745524; 2026Q2 base 1,936.986234), and `funds_in_window` exactly (12,609 and 13,799 base).
- **C-X2** each N-PORT zip's sha256 equals the cash build's `tsy_file_stats.csv`; each N-CEN zip's sha256 is recorded.
- **C-X3** `check_unique_survivors` PASS for both vintages.
- **C-X4** headers equal `fut_idx_columns.tsv` exactly; no forbidden header; no file > 2,000 rows; the G9 name scan is clean; no cell
  below the small-cell floor.
- **C-F1** fixed curve 2023-12-29 and d10 8.2233 ± 0.0001; the CF fixtures of §3.5 exact.
- **C-F2** the eight tenor factors of §3.4 within $0.01, computed with unrounded duration and d10 and CF rounded to 4 dp (R23-5).
- **C-F3** the classifier fixtures of §3.2 all correct.
- **C-F4 (R23-2)** for each contract and window, using every line with a valid integer contract count, before the basis fallback of §3.3
  (excluding `notional_field_is_count` lines and blank NOTIONAL): median NOTIONAL / (contracts × face) in [0.85, 1.35]. Applied when the
  contract has at least 5 such lines for TU and Z3N (the pinned $200,000 faces) or at least 20 for the others.
- **C-F5** sign convention: on kept lines with BALANCE ≠ 0, sign(BALANCE) agrees with `FUT_FWD.PAYOFF_PROFILE` on ≥ 90% of lines (2024q1
  observed, first-pass classifier: 6,582 of 6,852, 96.1%). Agreement in 10-year-equivalent dollars is reported beside it (R23-1); it is
  not part of the hard test, because G_s carries that risk into the verdict.
- **C-B1** every N-CEN column of §2.3 present; no quarter claimed by two zips.
- **C-B3** partition identity: per period, the sum of every group's ΔS (including `mmf`, `levinv`, `stale_flag`, `feeder_dropped`) equals
  M0 ΔS within 1e-5.
- **C-B4** no N-PORT report has two N-CEN flags after the amendment rule; every backfilled flag carries `flag_backfilled`.

**Decision inputs (never a build failure):** A1-A3; U_F; G_v; G_c; G_s; U; the q bounds of R23-13.

**Flags (printed):**
- C-F6 Σ|UA| / Σ|notional| on kept lines < 5%.
- C-F7 in the ≥ 90%-Treasury universe, |F_tenor| ≤ 15% of that universe's cash 10-year equivalents at both endpoints.
- C-F8 counts by `ASSET_CAT` and by basis.
- C-B5 the share of Part C rows with no type box checked and IS_FUND_TYPE_NA ≠ Y (expected near 0, because N/A is the "none" box, B1), and
  the IS_INDEX value counts (Y, N, blank).
- C-B6 the age distribution of each flag's N-CEN period, and the backfilled count by window.
- C-B7 series and S lost to the schema-3.1 omission: series with an N-CEN before 2025 and none after, and `stale_flag` series and S.

## 7. Selftest (synthetic only; `python3 bin/nport_futures_index.py selftest`)

The script runs `bin/test_nport_treasury_duration.py` and its own selftest before any build; either failing exits 1. **Every guard is a
mutation test (R23-18): mutate X, run on fixture Y, and the guard must FAIL. An uncaught mutant fails the selftest.** Each guard also passes
on the unmutated fixture.

| Guard | Mutate X | Run on fixture Y | Must FAIL because |
|---|---|---|---|
| G1 face | Z3N face → $100,000; separately TU → $100,000 | 6 Z3N lines with notional/(contracts × $200k) ≈ 1.04; 6 TU lines likewise | C-F4 median 2.08 is outside [0.85, 1.35] |
| G2 classifier | (a) drop step 0; (b) drop `OPTN`; (c) test `BOND` before tenor; (d) let `UB` pass on blank currency; (e) reverse the source order; (f) resolve a conflict silently | the §3.2 fixture list | ASX AUD → TY; Euro-Buxl UBH4 → UB; OPTN line → TY; "U.S. TREASURY 10 YEAR ULTRA BONDS" → UB; conflict line not `unresolved_conflict` |
| G3 sign | take the primary sign from BALANCE; use holding-level PAYOFF; keep a sign-N/A line | a Short line with BALANCE +; a line with PAYOFF N/A | fixture F differs from the expected value |
| G4 size | add contracts × face and notional on one line; size by CURRENCY_VALUE; skip rule 1 of §3.3 | a line whose NOTIONAL equals its contract count; a line with a $3m mark | F off by the notional or the mark; the count line moves to notional basis |
| G5 tenor map | add expiry to T; drop CF; take d10 from the report date | TY on the fixed curve | factor 69,298.27 or another value ≠ 78,153.01 |
| G6 CF | no 1/8 rounding; z to quarters for FV; discount at 3% annual; old "any term" fixture | §3.5 fixtures | 4.0625% gives a different CF; 6% at z = 3 gives 1.0000, not 0.9999 |
| G7 CTD | argmax; TY basket measured from the last day of the month; TIPS admitted; a Note admitted to US | a 5-issue synthetic basket | a different CTD is chosen |
| G8 no cash mixing | write a column equal to S + F, F / 3,218.3, or a cell holding the whole token `460` or `FIRST-ORDER` | a synthetic fut_* output | whole-token match fires (`4600` and `1,460.2` do not, R23-18) |
| G9 leak | plant: a file with a `SERIES_ID` header; a 2,001-row file; a cell containing a fixture fund name; a README line containing a registrant name; a 4-series cell | a scratch output folder | the hygiene check reports FAIL on each plant |
| G10 allowlist | add a column; rename a column; edit the TSV while the code writes the old header; paste a literal tuple of output column names into a copy of the script source | fixture TSV, outputs and script copy | header ≠ TSV row; the source scan finds an allowlist copy |
| G11 flag timing | use a later N-CEN filed more than 15 months after the position date; leave a backfilled flag unlabelled; use an NT notice; let an older N-CEN/A beat a later N-CEN for the same period | a series with filings before and after r | the wrong flag, or a missing `flag_backfilled` label |
| G12 flag order | apply `index` before the N/A-beside-type test; code N/A alone as unflagged; apply levinv before mmf | rows: N/A + IS_INDEX = Y; N/A alone; mmf + levinv | expected unflagged / active / mmf not returned |
| G13 groups | put a switcher in index_stable; count an unflagged entrant as stable; keep feeder lines while the master is present; drop stale_flag from U | a 6-series panel over the 4 windows | group sums or U differ from expected |
| G14 wording | insert "caused", "drove", "driven", "because of", "led to", "pushed", "in response to" or "moved yields" into the README or a verdict; insert a symbol (q, s0, U, G_s) into README prose | generated README | the wording scan fires; the required sentence passes |
| G15 decision rules | swap rule order (SUPPORTS before U); use U cap 16.210; drop G_s; drop the q bounds | boundary fixtures: q 0.60 → SUPPORTS, 0.5999 → INCONCLUSIVE; U 16.2 → not triggered, 16.21 → INCONCLUSIVE; ΔS(active_stable) −0.1 → undefined; classified sum 24.9% of base → undefined; ΔF 100.0 → LARGE, 99.99 → SMALL; G_c 50.01, G_v 20.01, G_s 20.01 → INCONCLUSIVE | the wrong label |
| G16 failure path | write to `data/nport/` after a hard FAIL; exit 0 after a FAIL | a forced C-X1 mismatch | committed folder touched, or exit code ≠ 2 |
| G17 no network | import `urllib`, `http.client` or `socket` | the script source, plus a run with `socket.socket` patched to raise | the source scan or the patched socket fires |
| G18 small cells | disable the merge | a split with a 3-series group | a committed row with series_n < 5 |

**G9 mechanism (the fund-name scan).**
- Collect the name set from the inputs read in that run: every `SERIES_NAME` and `REGISTRANT_NAME` of the N-PORT survivors and, in `idx`
  mode, the N-CEN series and registrant names.
- Normalise each: upper-case, punctuation to spaces, spaces collapsed. Keep names of at least 8 characters and two words that are not in a
  fixed vocabulary list (contract names, group labels, the words of the required sentence).
- Normalise every cell of every output CSV and every README and SOURCES line the same way. A name that appears as a whole-word substring
  is a FAIL naming the file and row, never the name.
- The selftest uses a synthetic name set ("ALPHA TEST TREASURY FUND", "BETA TRUST SERIES").

**G10 mechanism (no allowlist copy in code).**
- Headers are read at run time from `fut_idx_columns.tsv`.
- The guard parses the script with `ast` and finds every list, tuple or set literal of string constants. If any literal shares 3 or more
  members with the column list of any one output file in the TSV, it is a FAIL ("allowlist copy in code").
- A written header that differs from its TSV row is a FAIL.
- The verifier diffs the TSV against §5 by hand.

## 8. Success criteria

1. Both selftests pass with every mutant caught; `bin/test_nport_treasury_duration.py` still passes.
2. `python3 bin/nport_futures_index.py futures --zip-dir <companion>/nport_zips` exits 0, with every hard check PASS. C-X1 reproduces
   1,387.745524 and 1,936.986234. A1-A4, U_F, G_v, G_c and G_s are printed, and `idx_prerun.csv` is written. `idx` mode does the same with
   `--ncen-dir`, and adds the ex-ETF anchors and the backfill and stale counts.
3. Real-data pins the builder must reproduce or explain, on 2024q1:
   - the DIR × DERIVATIVE_CAT counts and the `UNIT` counts of §2.1;
   - the TU, FV and TY notional-per-face medians within ±0.005 of 1.021, 1.067 and 1.098, computed over the whole zip;
   - the tenor factors of §3.4.
4. A second run of each mode leaves every sha256 unchanged.
5. `bash bin/check.sh --all`: five ✓ guard lines, `✓ no killed claims found`, `✓ page clean`.
6. A verifier re-derives one number independently: the 2023Q4 net Treasury-futures face (A1), or the 2026H1 ΔS of the stable index arm.
7. README cold-reader test: two fresh agents (a trustee and a rates practitioner) read only the README. Each must state:
   - that futures are not added to cash holdings;
   - that "Index Fund" means any index, not the Aggregate;
   - that nothing here explains yields.

**Landing (builder hands back; the supervisor lands):**
- `.gitignore` for `data/nport/_FAILED_fut_idx/`;
- a REPRODUCE.md paragraph;
- a CALENDAR row: "re-run with the 2026q4 N-PORT zip and the 2026q4 N-CEN zip (about January 2027)";
- the handover row.

The builder commits nothing.

## 9. OPEN questions

- **OPEN-F1 CLOSED (F1, R23-6):** the rulebook terms in §3.5 come from Grok's fetch of the CBOT chapters, and the README names the explainer
  text that disagreed.
- **OPEN-F2:** generic Bloomberg-FIGI lines stay unresolved. OpenFIGI could map them for free, but it is a new host and its terms are
  unread. Not used unless U_F binds.
- **OPEN-F3 RESCINDED (R23-7):** the anchors are on all registered funds; the ex-ETF values are printed only.
- **OPEN-F4:** the FEDS DV01 table is headed "Millions of $" but reads as dollars. Only the ratios are used.
- **OPEN-B1 CLOSED (B1):** N/A alone means none of the listed types.
- **OPEN-B2 CLOSED (B2 merged, R23-10):** backfill is primary; `q_strict` is the sensitivity.
- **OPEN-B3 CLOSED (B3):** Grok's extra clauses are printed flags only.
- **OPEN-B4 CLOSED (B4):** the supervisor resolves the 2026q3 file name. Whether the `_0` files differ from earlier postings is recorded by
  their sha256 in `fut_idx_file_stats.csv`.
- **OPEN-B5 (after the run):** `IS_INDEX` includes Treasury-only index ETFs and T-bill indexes, so a high index share may be Treasury index
  funds rather than Aggregate funds. Splitting them needs the index name, which no N-CEN or N-PORT bulk field carries.
- **OPEN-R1 (for the supervisor; spec author's reading):** R23-2's "pinned-face contract" is read as TU and Z3N, the two $200,000 faces fixed
  by the frame and Departure 1. If it means all eight contracts, the floor is 5 lines for every contract.
- **OPEN-R2 (for the supervisor; spec author's reading):** R23-5's 1/8 rounding is not applied to the synthetic tenor-map coupon
  (Departure 6), so the reviewer-verified pins stand.

## Supervisor rulings, 19 Oct 2026 (before any data run)

- **B1 confirmed:** Form N-CEN Item C.3 (fetched by the supervisor from sec.gov) asks whether the fund "is any one of the types listed
  below" and to "check all that apply"; an ordinary active fund is none of the listed types. "N/A" alone = active; N/A beside another type =
  unclassified, as specified.
- **B2 ruled:** primary flag = the latest N-CEN or N-CEN/A whose report period ends on or before the N-PORT report date; for a series with
  no such filing (a fund launched after its last earlier N-CEN), the primary uses its FIRST later N-CEN filed within 15 months of the
  position date, labelled `flag_backfilled`. The strict rule (no backfill) is reported beside it as a sensitivity. Fixed before any data run.
- **B3:** Grok's extra inconclusive clauses stay printed flags only; the decision rule is as specified.
- **F3 ruled:** the Fed-note anchor check (2023Q4 net futures notional $313.8bn, DV01 ratio 0.303) is computed on mutual funds only
  (excluding ETFs), to match the note's universe; the build's own measure covers all registered funds as specified. Fixed now.
- **F1:** the CME deliverable rules, contract faces and conversion-factor formula are checked by the outside review (Grok) before the build;
  if CME's pages stay unreadable to scripts, the supervisor reads them in a browser.
- **B4:** the supervisor resolves the 2026q3 N-CEN file name when fetching.

## Supervisor rulings, rounds 2 and 3 (second review and Grok attack g9), 19 Oct 2026 — before any data run

The second reviewer re-derived all eight tenor factors (TY $78,153.01), the M0 base (2026H1 ΔS 162.103494) and the FEDS Figure 5 values (DV01 ratio 0.3030; futures duration 3.7528 years), streaming the 2024q1 zip. Grok fetched the CME rule chapters 18, 19, 20, 21, 26, 39 and 40 and the CBOT conversion-factor article. The supervisor fetched SEC's N-CEN data-sets page on 19 Oct. It says the data sets "do not include, at this time, N-CEN filings submitted in the schema version 3.1 introduced in EDGAR version 25.2".

**Part 1 (futures)**
- **R23-1 Sign gap is a decision input.** C-F5 also reports agreement in 10-year-equivalent dollars. New input G_s = |ΔF(PAYOFF sign) − ΔF(BALANCE sign, on lines where it exists)|; LARGE or SMALL requires G_s ≤ $20bn. A1–A3 computed with the BALANCE sign are printed beside the primary ones. (On 2024q1, net F was $133.1bn with the PAYOFF sign and $199.9bn with the BALANCE sign, and A3 was 3.07 against 4.01. These are the reviewer's indicative figures, not window values.) PAYOFF stays primary as registered. The sign-disagreement notional is also printed as a share of kept notional.
- **R23-2 C-F4** uses every line with a valid integer contract count, before the 0.5–2.0 fallback; minimum 5 lines for a pinned-face contract, 20 otherwise.
- **R23-3 Notional holding a count.** If |NOTIONAL| is within 1% of |BALANCE|, the notional field holds a contract count. Keep the face basis and count the line as `notional_field_is_count`. A line with no valid count and a blank NOTIONAL is excluded and counted as `no_size`.
- **R23-4 Classifier.**
  - Add a necessary condition: `FUT_FWD.CURRENCY_CODE` = USD (or blank with a US exchange marker).
  - Step 1 adds `EURO` (no hyphen), `FGBX`, `FGBL`, `FGBM`, `FGBS`, `OPTN`, `\bPUT\b`, `\bCALL\b`.
  - Ticker roots: replace `3YR|Z3N` with `3Y`. `UB` counts only with USD currency.
  - Step 3 tests the tenor (10, 30) before `BOND|BD`, so ULTRA + 10 goes to TN before ULTRA + BOND goes to UB.
  - G2 adds the ASX "10 Year Treasury Bond Futures" (AUD), Euro-Buxl "UBH4" (EUR), "US 10YR FUT OPTN JAN24P 110", "3YH4" and "U.S. TREASURY 10 YEAR ULTRA BONDS" with ticker UXYH4 → TN.
- **R23-5 Conversion factor.** The coupon is rounded to the nearest 1/8 per cent, ties up. Fixture: 6% at 0 or 6 whole months → 1.0000; at other z → 0.9999 (the "any term" fixture is deleted). C-F2 uses unrounded duration and d10 with CF rounded to 4 dp.
- **R23-6 Baskets follow the CBOT rulebook** (Grok's quotes; the rulebook wins over the 2024 explainer). All terms run from the first day of the delivery month. Round down to a month for TU, Z3N and FV, and to a quarter for the others, before testing. TY requires original term ≤ 10 years and remaining ≥ 6y6m and < 8y. US and UB baskets take Bonds only. Notes and Bonds classes only, so fixed principal and coupon. The README says which explainer text disagreed.
- **R23-7 Anchors. F3 is RESCINDED.** A mutual-funds-only anchor needs N-CEN `IS_ETF`, which `futures` mode does not have, and the FEDS note does not say ETFs are excluded. A1–A3 stay on all registered funds, as in §3.7; ex-ETF values are printed beside them when N-CEN is present (ex-ETF = `IS_ETF` ≠ Y; series with no N-CEN row are counted separately). A printed, non-decision row compares all-fund long face with the FEDS Figure 3 reading (about $470–500bn: "roughly $500 Billion").
- **R23-8 Printed beside, not decision inputs:** DV01 by contract; the continuing-fund versus entrant split of ΔF.

**Part 2 (test B)**
- **R23-9 Flag order** (fixes the contradiction with Departure 2, B1 and G12): `mmf` if IS_MONEY_MARKET = Y; else `unflagged` if IS_FUND_TYPE_NA = Y and any of IS_ETF, IS_ETMF, IS_INDEX, IS_MULTI_INVERSE_INDEX, IS_INTERVAL, IS_FUND_OF_FUND, IS_MASTER_FEEDER, IS_TARGET_DATE, IS_UNDERLYING_FUND = Y; else `levinv` if IS_MULTI_INVERSE_INDEX = Y; else `index` if IS_INDEX = Y; else `active`. The builder confirms these column names against the N-CEN readme and reports any that differ.
- **R23-10 B2 merged into the body.** The primary flag is B2's, with `flag_backfilled` for a series that has no earlier filing. `q_backfill` is renamed `q_strict` (no backfill), as a sensitivity. G11's mutant becomes "a later N-CEN more than 15 months after the position date used", plus "a backfilled flag not labelled". §4.1, §4.2, OPEN-B2 and G11 are rewritten to agree.
- **R23-11 Stale and missing flags (schema 3.1).** A series whose flag comes from an N-CEN period ending more than 15 months before 2026-06-30 is `stale_flag`. |ΔS| for 2026H1 of stale-flag series is added to U. Pre-run decision input, from the cash build alone: ΔS of series absent at 2025Q4 and present at 2026Q2 (entrants), with how many are unflagged. The README says SEC omits schema-3.1 N-CEN filings, so 2025–26 flags can be stale or missing, and that if entrant and stale change exceeds the U cap the verdict is INCONCLUSIVE by construction.
- **R23-12 Feeders** are identified only through `FEEDER_FUNDS.REGISTERED_SERIES_ID` in the master's filing. `MASTER_FUNDS` is not used for the join. The builder confirms the columns in the readme.
- **R23-13 q, bounded.** q_p is defined only if ΔS(index_stable) ≥ 0, ΔS(active_stable) ≥ 0, and their sum is at least 25% of the M0 ΔS for that period; otherwise that period is undefined and the verdict is INCONCLUSIVE. Printed beside: the index share of ALL groups' ΔS. The SUPPORTS sentence names "series flagged 'Index Fund' on Form N-CEN" (any index, not only Treasury indexes).
- **R23-14 U cap** is the literal $16.2bn.
- **R23-15 The 0.15 bar** is labelled a pre-registered hurdle taken from a different object after that object was measured. It is not a sampling bound.
- **R23-16 Small cells.** In `idx_split.csv` and `idx_crosstab.csv`, cells with `series_n` < 5 are merged into an `other_small` row or blanked, because `tsy_top_funds.csv` names series.

**Build mechanics**
- **R23-17 Imports.** R3's list names `Ctx.add`, `process_lines`, `decide_kind` and `stream_survivor_lines` explicitly. A subclass or a new futures pass (lines ending `\tFUT`) is allowed. `q_M1` and A2's notes-and-bonds DV01 may need a subclass, and that is allowed.
- **R23-18 Guards.** G8 matches whole tokens. G9's fund-name detection and G10's allowlist copy get explicit mechanisms written by the spec author. Every guard is phrased "mutate X, run on fixture Y, must FAIL".
- **R23-19 README.** Definitions come first. Each verdict is a full sentence stating its claim. No symbols (q, s0, U, G_v, G_c, G_s) appear in prose. LARGE/SMALL is described as the "net change" in funds' futures. The README says these are holdings, not a cause of yields.

## Supervisor rulings, round 4 (spec author's readings), 19 Oct 2026 — before any data run

- **OPEN-R1 CLOSED:** "pinned-face contract" means TU and Z3N (the two $200,000 faces), as the author read it.
- **OPEN-R2 CLOSED:** the 1/8 coupon rounding applies to real deliverables only. The synthetic tenor-map bond is not a deliverable, so its coupon stays the curve's par yield and the eight pinned factors stand. The README says so.
