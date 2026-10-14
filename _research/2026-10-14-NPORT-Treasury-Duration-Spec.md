# N-PORT Treasury duration: build specification (who took the duration, registered funds)

*14 Oct 2026. Spec rung of the step ladder for E-021 item 7, serving R2's open line "Which buyers took the duration is not measured"
(`2026-09-27-R2-Treasury-Duration-Supply-And-Holders.md`, the closing open line). Status: SPEC, amended by §10 (the supervisor's
amendments N1–N13 after two adversarial reviews) and applied through §§0–9 on 14 Oct so that spec and code agree. Where §10 and an
earlier section disagree, §10 governs and the earlier section has been edited to match. Nothing in this file is a finding.*

**Where the numbers come from.** Three investigation lenses (schema, linkage, prior art) ran on 14 Oct over the 11 bulk zips on disk.
Their scratch files sat under `<session-scratchpad>/nport/{schema,lk,priorart}/` and did not survive the session. Two tags are used:
- **[S]**: re-derived by the spec author on 14 Oct from the zips and the R2 caches, with a script independent of the lenses'.
- **[L]**: reported by a lens and not re-derived here. Per N13, an [L] anchor that the build cannot reproduce is not a hard check; it
  is listed as unverified in `tsy_checks.csv` (result N/A).

Every count states its denominator.

## 0. Where this spec contradicts the brief or the Grok spec (read first)

1. **The endpoint is 30 Jun, not 31 Aug.** "+$3.4trn" is `public_10yeq_fixed_bn` from 2023-12-31 to 2026-08-31: 9,539.1 → 12,943.0, a rise of 3,403.9 [S, `data/r2_rates/duration_supply.csv`].
   - No N-PORT report reaches 31 Aug. The latest REPORT_DATE on disk is 2026-07-31 [L], and an August report would cover family C only, about 36% of S [L].
   - The endpoint that N-PORT can match is 30 Jun: **ΔP = 12,757.4 − 9,539.1 = 3,218.3bn** [S].
   - The brief's 2026-07-31/08-31 snapshot cannot be computed. The build reports it as absent.
2. **One report date covers about half the funds.** The public file holds one report per fund per *fiscal* quarter, so each zip spans three report months.
   - The 2026q3 zip holds 14,066 filings. By report date: 2026-05-31 2,516, 2026-06-30 7,063, 2026-07-31 4,195 [S].
   - Clean Treasury value at 2026-06-30 alone is $1,394.8bn on 30,257 lines. The three-month window, one report per fund across 13,907 funds, gives $2,596.4bn on 55,687 lines [S]. The single date is 53.7% of the window.
   - The brief's test, "market value at 2026-06-30 within a band of Z.1's 2,550.8bn", is therefore set on the 2026Q2 **window**.
   - Matching on the strict date also drops the 838 filings dated 2023-12-29, because 31 Dec 2023 was a Sunday [S, 2024q1 SUBMISSION, 12,576 filings].
3. **Grok's filter `ISSUER_TYPE=UST & ASSET_CAT=DBT` drops 13.2% of Treasury value at 2026-06-30.** It keeps $1,210.3bn of $1,394.8bn [L]. It misses bills filed as STIV, Vanguard's TIPS funds filed as SN, and TIPS typed USGA.
4. **Grok's weighting is not R2's basis.** Grok multiplies fair value by par-bond bucket factors. R2 prices each CUSIP's par at its own coupon on the fixed curve. On ΔP, Grok's weighting gives 14.0% where R2's basis gives 16.9% [L]. Only line-level pricing on R2's basis is comparable.
5. **DV01 sign differs by filer, so DV01 is a magnitude cross-check only.**
   - The USD rows at 2026-06-30, for funds with any clean Treasury line, split 600 positive, 684 negative and 4 zero [L].
   - The readme defines DV01 as the "change in value of the portfolio resulting from a 1 basis point change in interest rates" and gives no direction.
   - Grok's plan sums the 10-year key rate across funds with a Treasury share above 50%. That nets opposite signs and takes in funds that park collateral in Treasuries.
   - Here DV01 is a per-fund magnitude cross-check (§4.4, a hard check on |reported| / computed, N6). The sign split is printed as filed and DV01 is never summed.
6. **Two population claims are unsupported.**
   - "N-PORT includes BDCs" (Grok): none of 8 named BDCs is a registrant [L]. The readme says N-PORT covers "registered investment companies and exchange-traded funds … other than money market funds".
   - "Z.1 mutual funds are ICI reporters": no Z.1 page fetched says so [L]. The claim is not used here.
7. **Amendments cross zips.** The census survivor rule (`bin/census_nport_bulk.py`, function `survivors`) works inside one zip. For the report date 2023-12-31, 144 NPORT-P/A filings sit in five later zips [L]. The rule here keys on (fund, report month) across all zips (§3.1), refuses to let a zero-line amendment replace a non-empty original, and removes content duplicates filed under different fund keys (N3).
8. **Runtime is minutes, and nothing is downloaded by the build.** Grok estimated 30–45 minutes plus a 5GB download. All 11 zips are already on disk and the build fetches nothing. One zip's holdings stream plus the DEBT join took 7.1 s [S, 2026q3, warm cache]. (The one-off Z.1 fetch is a separate script, §2.)
9. **The census has no asserts** [L]; its checks only print. The hard checks in this spec set a non-zero exit status (§6) and divert the outputs to `data/nport/_FAILED/` (N11).
10. **New: MSPD as the security master.** R2's cached MSPD Table 3 files cover six record dates and 789 distinct 912 CUSIPs [S].
    - They classify 97.44% of the 2026Q2 window's Treasury value directly by CUSIP: Notes 51.42%, Bonds 19.23%, TIPS 13.06%, Bills 12.51%, FRN 1.22%.
    - Bill prefixes add 1.80% and STRIPS prefixes 0.75%. That leaves 2 lines, $0.00bn [S, denominator $2,596.4bn].
    - MSPD flags $339.20bn as TIPS. A name regex finds $337.28bn, all of it inside the MSPD set [S].
    - So the TIPS flag stops being a lower bound, ANNUALIZED_RATE units stop mattering, and coupon, maturity and the TIPS index ratio become *R2's own inputs*.

## 1. Goal and decision rule (fixed before any build output exists; replaced by N1)

**Question.** The public's Treasury 10-year equivalents at the fixed end-2023 curve rose by ΔP = 3,218.3bn from 2023-12-31 to 2026-06-30. How much of that rise sits with US registered funds that file N-PORT, measured on the same basis (ΔS)?
- ΔS is the headline. r = ΔS/ΔP is descriptive.
- The basis is 10-year equivalents at the fixed end-2023 curve.
- Every figure names its weighting (C-122).
- Scope: **cash Treasuries only** (§3.2). The futures sensitivity is deferred (N5) and prints as "not measured in this landing". It is never folded into S.

**Lines.** They are in dollars, as the E-021 item 7 brief of 14 Oct wrote them, before any N-PORT file was opened: "about $0.5trn or more (one-seventh of R2's $3.4trn) makes retail/ETF a first-order duration sink. Below about $0.1trn, funds are bystanders".
- First-order line: **$460bn** of 10-year equivalents (ΔP/7 on the 30 Jun endpoint, 3,218.3/7 = 459.8). The item's rounder "$0.5trn" is printed beside it and does not decide the verdict.
- Bystander line: **$100bn**.
- The relative rule of the first draft (r₁ = 1/7 against the funds' own starting share s₀) is withdrawn. It equals the funds' starting share, and it was set after provisional numbers had been seen.

**Verdict, computed separately for two arms** and written to `tsy_verdict.csv`:
- the **measured arm**: N-PORT's own lines on the base of §3.1 (variant M0);
- the **Z.1-scaled arm**: the band [min, max] of ΔS over P1 and P2 (§4.5).

For each arm: FIRST-ORDER SINK if ΔS ≥ $460bn (for the Z.1-scaled arm, if the band's low end is ≥ $460bn); BYSTANDER if ΔS < $100bn (the band's high end); PARTICIPANT otherwise. If the two arms give different labels, the published verdict is "NOT ESTABLISHED" and both rows are printed.

**Pro-rata, per arm.** Against that arm's own starting share s₀ = S(2023Q4)/P(2023-12-31): excess = r − s₀, in pp, and ΔS − s₀·ΔP, in $bn. If the two arms' signs differ, the text says "sign not established". For the Z.1-scaled arm the sign is reported only if P1 and P2 agree.

**Resolution, in place of a minimum detectable effect (C-090).** This is a measurement, not a test against noise; its error comes from choices of method and population. The lines are $360bn apart (11.2pp of ΔP). The base, the matched vintage (M1), the alternative curve (M8) and the two Z.1 scalings (P1, P2) are printed with their own labels as sensitivity. A result whose arms straddle a line is pre-registered as "not established", not as a null.

**Disclosure.** The spec author and a reviewer saw the lens's provisional results before the build [L]: base r 16.9%, method arm 16.5–18.0%, population arm 13.5–14.1%, stress floor 8.3%, s₀ 14.5%. The dollar lines predate both of them (they were written on 14 Oct in the research item, before any measurement). The builder's numbers are not checked against the provisional values (the lens cross-check C15 is dropped, N13).

**Outside the result in both directions.**
- r is a holder share, not a price effect. Nothing here says the funds' purchases moved yields or term premia (CHARTER:58).
- P − S is a residual (C-098). It is not "the share of unregistered holders" until it is measured.
- Do not use the result against C-124: these funds already sit inside the Z.1 funds row.

## 2. Script, inputs, outputs

**Script.** `bin/nport_treasury_duration.py`, stdlib only, with no network I/O of any kind.
- Follow the house style of `bin/census_nport_bulk.py`.
- The module docstring carries the usage line and the numbered matching rules, "listed rather than hidden". It states that inputs are not redistributed, lists the outputs, cites the correction ids (C-059, C-098, C-122, C-124), and carries the SEC landing page, the URL pattern, the sha256 list and the cache prerequisites (N12).
- Before it builds anything it runs its own test file as pre-flight (N11). A failing test exits 1 and writes nothing.

```
python3 bin/nport_treasury_duration.py [--zip-dir ~/nport] [--r1-cache data/vintages/r1_treasury]
        [--r2-cache data/vintages/r2_treasury] [--z1-dir data/vintages/z1_fund_tsy_20260911]
        [--etf-dir data/vintages/z1_etf1_2026Q2] [--anchors data/nport/tsy_anchors.csv] [--out data/nport]
```

**Inputs.** All are read-only.
- `--zip-dir`: the zips, **discovered by glob** (`*q[1-4]_nport.zip`) and the windows derived from them (N8). Today `2024q1_nport.zip` … `2026q3_nport.zip` (11 zips, 11 windows). Refuse if none is found or if the quarters have a gap. Read them with `zipfile` as streams and never extract them.
- `--r1-cache`: `daily_treasury_yield_curve_{2023..2026}.csv` and `daily_treasury_real_yield_curve_{2023..2026}.csv`.
- `--r2-cache`: the explicit list (N7), not a glob: `mspd_table3_{2023-12-31, 2024-12-31, 2025-12-31, 2026-06-30, 2026-07-31, 2026-08-31}_p1.json`, `soma_asofdates_list.json` and `soma_tsy_{2023-12-27, 2024-12-31, 2025-12-31, 2026-06-24}.json`.
  - Both caches are gitignored and are written by `bin/r2_duration_supply.py`.
  - The builder may point both flags at the shared checkout's copies, read-only, or at a copy of them.
  - A missing file is named in the refusal together with the exact command that recreates it.
- `--z1-dir` (N10): the Z.1 release of 11 Sep 2026, tables S.124.1 (mutual funds) and S.124.2 (closed-end funds), levels from the `_s` tables and unadjusted flows from the `_t_tu` tables, written by `bin/nport_fetch_z1.py`.
  - The fetch script contacts www.federalreserve.gov only, with the CLAUDE.md non-SEC User-Agent (no address), by the route `bin/build_closure_2026Q2.py` uses, and records the release zip's sha256 in `z1_provenance.csv`.
  - The extracted CSVs and data dictionaries are committed: Fed data is public domain.
- `--etf-dir` (N10): the S.124.3 ETF row (levels and flows) is read from the committed `data/vintages/z1_etf1_2026Q2/`.
- `--anchors` (N8): the committed `data/nport/tsy_anchors.csv`, one row per anchor (scope, key, value, tolerance, source) with "N/A (no anchor)" where a zip or window has none.
- `data/r2_rates/duration_supply.csv`, which is committed.

**No-network guarantee.** First check that every expected cache file exists, naming each missing one in the refusal with the command that recreates it. Then import R2 with `importlib` from `bin/r2_duration_supply.py`, replace `r2.fetch` with a function that returns when the cached file exists and raises SystemExit when it does not (N7), and point `r2.R1RAW` and `r2.RAW` at the cache flags. The guard has its own test.

**Outputs.** All go under `--out`; on any hard FAIL they go under `--out/_FAILED/` instead and the committed files are left untouched (N11).
- Written with `csv.DictWriter(lineterminator="\n")` in UTF-8.
- $bn and ratios are rounded to 6 dp, rows are sorted deterministically, and every aggregate is a `math.fsum` (N12).
- **No file carries a wall-clock time or run timestamp.** Timing goes to stderr, so a re-run is byte-identical.
- Aggregates only: no holding row, no CUSIP-level line and no HOLDING_ID is written. A hard check (C18) enforces that no header contains CUSIP, HOLDING_ID or ACCESSION_NUMBER and that no file exceeds 2,000 rows.

| File | One row per | Columns |
|---|---|---|
| `tsy_windows.csv` | window × vintage | window, quarter_end, vintage (base/matched), months, funds_in_window, funds_m_minus1, funds_m0, funds_m_plus1, funds_with_tsy, tsy_lines, tsy_value_bn, tsy_value_series_bn, tsy_value_noseries_bn, tsy_par_bn, tenyeq_fixed_bn, tenyeq_fixed_alt_bn (M8 curve), tenyeq_own_bn, pardur_fixed_bn_yrs, dv01_own_mn, strips_tenyeq_fixed_bn, short_value_bn, unpriced_lines, unpriced_value_bn, tips_orig_lines, tips_orig_par_added_bn, tips_orig_tenyeq_fixed_bn (N4: what reading original-face TIPS at adjusted value adds), z1_mf_bn, z1_etf_bn, z1_cef_bn, z1_sum_bn, nport_over_z1, r2_public_10yeq_fixed_bn, share_of_public_fixed |
| `tsy_buckets.csv` | window × kind × bucket (base vintage) | window, kind (bills/coupons/tips/frn/strips/unpriced), bucket (0-1, 1-2, 2-3, 3-5, 5-7, 7-10, 10-20, 20+ years remaining), lines, value_bn, par_bn, tenyeq_fixed_bn, eff_factor (tenyeq/par, descriptive only), public_tenyeq_fixed_bn (R2 dates only; blank otherwise and for strips), share_of_public |
| `tsy_change.csv` | variant × period | variant_id, arm (base/method/population/diagnostic), grade, description, comparator (R2 column), period (full/2024/2025/2026H1), s_start, s_end, d_s, p_start, p_end, d_p, r, s0, excess_pp, excess_bn, label |
| `tsy_verdict.csv` | key | key, value (the keys are listed under §1 and written in §3 of the findings note: both arms, ΔS, r, s₀, excess in pp and $bn, the published verdict, the futures line "not measured in this landing", and `scope` = "cash Treasuries only") |
| `tsy_dv01_check.csv` | window × universe | window, universe (tsy90_usd/tsy90_usd_no_dir/any_tsy), n_funds, n_pos, n_neg, n_zero (signs of the reported DV01 as filed, over the funds with a USD row), median_ratio, p25_ratio, p75_ratio, tsy_value_covered_bn, tsy_value_bn. For any_tsy n_funds counts every fund with a clean Treasury line and tsy_value_covered_bn is the value in those with a USD row |
| `tsy_top_funds.csv` (≤ 70 rows) | list × rank | rank_by (s_<end>/d_s/registrant_d_value), rank (1–25; 1–20 for registrants), fund_key (SERIES_ID or CIK), series_name, registrant_name, s_<start>, s_<end>, d_s, value_<start>_bn, value_<end>_bn, where start and end are the first and last windows that sit on R2 dates (today 2023Q4 and 2026Q2) |
| `tsy_checks.csv` | check | check_id, scope, label, ours, reference, threshold, result (PASS/FAIL/FLAG/N/A), hard (Y/N), note |
| `tsy_file_stats.csv` | key | tag, key, value |

**Keys in `tsy_file_stats.csv`.**
- Per zip (tag `2024Q1` … `2026Q3`, the quarter of the zip): zip, zip_sha256, holding_rows, filings_total, filings_NPORT-P, filings_NPORT-P/A, report_date_min/max, filing_date_min/max, tsy_lines_kept, tsy_value_kept_bn, excluded lines and $bn by reason, value_check_lines, value_check_bad, unit_ns_lines, short_lines, and (survivor lines only) debt_rows_joined, $bn by kind rule (1)–(6), coupon source counts (mspd/rate/rate_x100/none), TIPS index-ratio counts (N4).
- Global (tag `ALL`): every cache file name with its sha256, mspd_union_cusips, fixed_curve_date, d10_fixed, z1_release_zip_sha256, the survivor and content-duplicate counts (N3), the partial-amendment count, and the list of unverified [L] anchors.

## 3. Selection

### 3.1 Filings, funds, windows, vintages
- **Tables.** Load SUBMISSION, FUND_REPORTED_INFO and REGISTRANT from all zips, only the columns needed (N9). They are one-to-one on ACCESSION_NUMBER: 14,416 rows each in 2026q2 [L]. Dates are DD-MON-YYYY; parse them with the census `pdate`.
- **Fund.** A fund is ("S", SERIES_ID), or ("C", registrant CIK) when SERIES_ID is blank (the census `survivors` function).
- **Report month.** The (year, month) of REPORT_DATE. Keying by month keeps the filers dated 2023-12-29.
- **Survivor rule (N3).** For each (fund, report month), across every zip in the vintage, keep the filing with the largest key (not a stub, FILING_DATE, SUB_TYPE == "NPORT-P/A", ACCESSION_NUMBER), where a **stub** is an NPORT-P/A with zero holding lines (any ASSET_CAT, counted in the holdings stream). A stub never replaces a non-empty filing. In every same-day tie the lens saw, the highest accession was also the P/A [L].
- **Content-duplicate check (N3).** After the survivor rule, survivors that share CIK, REPORT_DATE, NET_ASSETS (> 0) and a clean Treasury line count (> 0) under different fund keys are one filing seen twice. Keep the latest by the survivor key and report the count of removed filings and their Treasury $bn.
- **Guard.** `check_unique_survivors()` returns PASS when no (fund, report month) is selected twice. It is called on the final selection of every vintage, and tested directly on a hand-built duplicate map (§7). Production code carries no switch to turn the de-duplication off.
- **Windows.** The windows are the quarter-end months m₀, one per zip: the zip of calendar quarter q (filings made in q) holds the report months of q−1, so its window is the quarter-end of q−1 (2024q1 → 2023-12, … 2026q3 → 2026-06). With the 11 zips on disk the 11 windows are 2023Q4 … 2026Q2. Each fund contributes its survivor for m₀ if there is one, else for m₀−1, else for m₀+1. Funds by that order, matched vintage, §3.1 rule before the content-duplicate step:

  | Window (zip) | Funds | m₀ | m₀−1 | m₀+1 |
  |---|---:|---:|---:|---:|
  | 2026Q2 (2026q3) [S] | 13,907 | 7,034 | 2,686 | 4,187 |
  | 2023Q4 (2024q1) [S] | 12,126 | 6,416 | 2,505 | 3,205 |

- **Home zip.** A window's home zip is the zip of the following calendar quarter: 2023Q4 → 2024q1, …, 2026Q2 → 2026q3. Cut by zip rather than by FILING_DATE, because the readme sends documents filed after 5:30pm EST on the quarter's last business day to the next posting.
- **Vintage "base" (N2).** Every zip on disk, with a filing-lag cut at both ends: a filing is eligible only if FILING_DATE ≤ REPORT_DATE + 62 days. The cut is applied at every window, so the 2023Q4 endpoint, which could otherwise collect two years of later amendments, and the 2026Q2 endpoint, which cannot, are read at the same lag.
- **Vintage "matched" (M1).** Zips up to and including the home zip, no lag cut: both endpoints carry a first-posting vintage. It is a variant, not the base.
- 2026Q2 stays provisional until the 2026q4 zip (§8).
- **Partial-amendment flag.** For every superseding NPORT-P/A, compare its count of holding lines with that of the filing it replaces. Count those below 50%. This is a FLAG, not a FAIL.

### 3.2 Treasury cash lines (FUND_REPORTED_HOLDING)
Stream the table through a substring prefilter (`"\tUST\t"`, `"\tUSGA\t"`, `"\t912"`). Split each surviving line on tab, and refuse on a column-count mismatch (census `main`).

**Keep a line when all four hold:**
1. ISSUER_TYPE is UST, or ISSUER_TYPE is USGA with a 912 CUSIP.
2. The CUSIP starts with "912".
   - ISIN recovery (`isin[2:11]` when the ISIN starts with US912) is **deferred** (N5). In the whole 2026q3 zip, 126 UST lines in the cash categories lack a 912 CUSIP ($2.311bn), and three of them ($1.792bn) carry a US912 ISIN [S]. The build counts the non-912 UST lines and their $ and does not recover them. Variant D6, "ISIN recovery switched off", is therefore the base itself.
3. ASSET_CAT is one of DBT, STIV, SN, OTHER.
4. CURRENCY_CODE is USD. The 2026q3 zip has no non-USD line with a 912 CUSIP [S], but count them anyway.

**Exclusions, each counted with its $ by reason (first reason that fits, in this order):**
- 912-CUSIP lines in the cash categories whose ISSUER_TYPE is neither UST nor USGA (CORP and the like; 99 lines and $0.22bn in the 2026q3 zip, builder's count). Equity lines whose CUSIP merely starts "912" (US Foods, Uniti) are not Treasury look-alikes and are not counted.
- Non-912 UST lines (this also catches fund shares typed UST).
- ASSET_CAT DIR: derivatives (the futures leg is deferred, N5).
- ASSET_CAT RA: repo. UST collateral in REPURCHASE_COLLATERAL is never added.
- ASSET_CAT ABS-MBS (any ABS*).
- Other ASSET_CAT.
- Non-USD currency.
- A blank CURRENCY_VALUE or BALANCE: guard `float('')` and count the lines.
- USGA lines without a 912 CUSIP are agency paper, not Treasuries: counted as lines only.

**Line handling:**
- Shorts stay signed: if PAYOFF_PROFILE is Short and BALANCE > 0, negate par.
- A CUSIP that appears on two lines of one filing is summed, never de-duplicated. There are 67 such pairs at 2026-06-30 [L].
- UNIT is not filtered, because lines with UNIT=NS behave as principal [L].

### 3.3 Security master and joins
- **MSPD union.** Build it from the explicit MSPD list in `--r2-cache`: CUSIP → (class, maturity_date, interest_rate_pct), taking the first occurrence in file-name order. For TIPS the per-record-date index ratio is kept too (below).
- **Kind map from the MSPD class:** Bills Maturity Value → bills; Notes and Bonds → coupons; Inflation-Protected Securities → tips; Floating Rate Notes → frn.
- **Kind precedence.** Apply the first rule that fits, and count lines and $ by rule:
  1. the MSPD class;
  2. prefix 912795, 912796 or 912797 → bills;
  3. prefix 912803, 912820, 912821, 912833 or 912834, or "STRIP" in the title or name → strips;
  4. COUPON_TYPE Floating or Variable → frn;
  5. title or name matching `INFL|TIPS|\bTII\b|INDEX|PROTECT|LINKED` → tips;
  6. otherwise coupons.
- **Coupon.**
  - When the CUSIP is in MSPD, use its `interest_rate_pct`. That is R2's own source (`cusips_from_table3`).
  - Otherwise use DEBT_SECURITY.ANNUALIZED_RATE, multiplied by 100 when 0 < rate < 0.1.
  - In the 2026Q2 window, measured against MSPD [S]: 35,524 lines equal, 4,407 equal only after ×100, 8,020 other.
  - In the whole zip, 7,975 of the 8,042 "other" lines are within 0.01pp, which is rounding. 67 differ by more, for example by 1/8pp. Lines that match only after ×100 total $298.8bn.
- **Maturity.**
  - When the CUSIP is in MSPD, use the MSPD maturity (R2's own).
  - Otherwise use DEBT_SECURITY.MATURITY_DATE, joined on HOLDING_ID within the zip (DEBT_SECURITY is streamed against the set of HOLDING_IDs of the kept lines, N9). The ids are unique and do not overlap across zips [L].
  - Otherwise use the modal maturity of the same CUSIP in the window.
  - Otherwise the line is unpriced; count it and report its $.
  - DEBT against MSPD in the 2026Q2 window [S]: 53,783 agree, 2 disagree ($0.01bn), 3 blank, 114 with no DEBT row.
- **TIPS par and the index ratio (N4).**
  - The MSPD index ratio of a CUSIP at a record date is Σ(issued + inflation_adj − redeemed) / Σ(issued − redeemed) over its tranche rows. At a report date it is read by linear interpolation in days between the bracketing MSPD record dates that list the CUSIP, flat outside them.
  - R2's basis is the inflation-adjusted principal. A TIPS line's BALANCE is **original face** when CURRENCY_VALUE is nearer, in log terms, to the value the line would have if BALANCE were original face than to the value it would have if BALANCE were adjusted: ln(CURRENCY_VALUE / (BALANCE × price_model/100)) > ½·ln(ratio), where price_model is R2's TIPS clean price at the report date's own real curve, per 100 of adjusted principal. The model price only chooses between the two discrete readings. **Par is never back-solved from it.**
  - Detection applies only when ratio > 1.05 (below that the two readings cannot be told apart and the adjustment is immaterial); otherwise BALANCE is taken as filed. On the 2026q3 and 2024q1 zips the statistic ln(CURRENCY_VALUE / (BALANCE × price_model/100)) / ln(ratio) is bimodal, about 0 for 71–79% of the TIPS lines and about 1 for 21–26%, with under 1.1% of lines between 0.25 and 0.75 (builder's check, 14 Oct), so the ½·ln(ratio) cut falls in the gap.
  - Where BALANCE is original face, par = BALANCE × ratio. The count of such lines and the par added are reported.

## 4. Pricing, buckets, cross-checks

### 4.1 Identical to R2 because it is imported, not copied
**Imports** from `bin/r2_duration_supply.py`, cited by name (N7): `par_mod_duration`, `interp_curve`, `bill_price_duration`, `coupon_price_duration`, `price_one` (FRN price 100 and duration 0.02 are inside it), plus `curve_points`, `on_or_before`, `NOM_MATURITIES`, `REAL_MATURITIES`, `FIXED_CURVE_DATE`, `load_curve`, `load_mspd_table3`, `cusips_from_table3`, `load_soma_dates`, `load_soma_holdings`, `soma_securities` and `aggregate`.

**Fixed curve.** Built as `main` in R2 builds it: the nominal and real rows on or before 2023-12-31, which resolve to 2023-12-29. d10_fixed = `par_mod_duration(10y, n=10)` = 8.2233 [S].

**Per line:**
- T = max((maturity − REPORT_DATE).days / 365.25, 0), as in R2's `compute_date` and `soma_securities`.
- par = BALANCE / 1e9, in $bn (× the index ratio where §3.3 says BALANCE is original face).
- (price, dur) = `price_one(kind, coupon, T, F_NOM, F_REAL)`.
- Strips are semiannual zeros: `coupon_price_duration(0.0, interp_curve(F_NOM, T), T)`.
- **tenyeq_fixed = par × price/100 × dur / d10_fixed** (R2 `aggregate`).

**Other measures from the same line:**
- tenyeq_own: the same calculation on the report date's own curves (`on_or_before(REPORT_DATE)`, with its own d10).
- tenyeq_fixed_alt (M8): the same on the alternative fixed curve (the 2026-06-30 curve).
- pardur_fixed: par × dur_fixed.
- dv01_own: par × price_own/100 × dur_own × 0.1, in $mn per bp (R2 `compute_date`).

**Market value and par.**
- BALANCE is par, adjusted for original-face TIPS only as §3.3 says. CURRENCY_VALUE/BALANCE medians are 0.977 for notes and bonds, 0.995 for bills and 0.465 for strips [L].
- CURRENCY_VALUE is USD fair value. It is used only for the value check, the Z.1 reconciliation, the 90%-of-NAV universe and the TIPS detection.

### 4.2 R2 replication check (hard)
**The rebuild.** At each R2 date in {2023-12-31, 2024-12-31, 2025-12-31, 2026-06-30}, rebuild R2's public holdings by kind and remaining-maturity bucket from the caches, using R2's own functions:
- take the total from `cusips_from_table3(load_mspd_table3(d), d)`, priced on the fixed curve;
- subtract `soma_securities(load_soma_holdings(on_or_before(load_soma_dates(), d)), asof)`, priced the same way.
- R2's `securities_for` is a closure inside `compute_date`, so its ten lines are copied here with a comment naming the R2 function (N7). C10 guards the copy.

**The test.** The sum over buckets must equal `public_10yeq_fixed_bn` within 0.1bn, the CSV's rounding. The linkage lens reproduced 9,539.1 and 12,757.4 this way [L].

**What it buys.**
- It proves that the import path is R2's.
- It fills `public_tenyeq_fixed_bn` in `tsy_buckets.csv`.
- The same machinery gives ΔP under the alternative fixed curve of M8.

### 4.3 Buckets
- Buckets are for reporting only. Every bucket figure is a sum of line-level values, and eff_factor = tenyeq/par is printed.
- No bucket factor is ever multiplied into dollars. Fair value times par-bond factors gave 14.0% against 16.9% [L].
- Bucket sums equal window totals. That is an IDENTITY and a hard check, not evidence.

### 4.4 Fund-level DV01 cross-check (INTEREST_RATE_RISK), a hard check on magnitude (N6)
- **Join** on ACCESSION_NUMBER, taking the CURRENCY_CODE = USD row only. Units of the non-USD rows are unverified [L].
- **Reported DV01** = the sum of the five key-rate DV01s (3m, 1y, 5y, 10y, 30y), in $ per bp, taken as filed. The sign split of the reported values is printed as filed.
- **Universe `tsy90_usd`:** base-vintage window funds whose clean Treasury value is at least 90% of NET_ASSETS and that have a USD row.
  - Computed DV01 = Σ par × price_own/100 × dur_own × 1e-4 over the fund's Treasury lines.
  - ratio = |reported| / |computed|.
  - Print n, the signs, the median and the quartiles.
  - **Check C12 (hard):** the median lies in [0.85, 1.15] at both endpoint windows.
  - The stricter universe `tsy90_usd_no_dir` (the same funds with no DIR line at all) is printed beside it as a sensitivity.
- **Universe `any_tsy`:** coverage only, the share of Treasury value in funds with a USD row. At 2026-06-30 that was 1,290 of 1,675 funds and $1,384.2bn of $1,394.8bn [L].
- Never sum DV01 across funds.

### 4.5 Variants (first landing, N5)
Each variant is compared with the R2 column on its own basis. ΔP is in brackets where it differs from the base [S].

| id | arm | change from base |
|---|---|---|
| M0 | base | base vintage (all zips, FILING_DATE ≤ REPORT_DATE + 62 days); T from the fund's own REPORT_DATE; MSPD class, coupon and maturity; TIPS par per §3.3; strips as zeros; shorts signed; fixed curve of 2023-12-29 (ΔP 3,218.3) |
| M1 | method | matched vintage (zips up to the home zip, no lag cut) |
| M8 | method | fixed curve of 2026-06-30 in place of 2023-12-29, with ΔP rebuilt per §4.2 (the other endpoint's curve; M8a and M8b are deferred) |
| P1 | population | S at each end × (Z.1 three-row sum / N-PORT window value); the gap carries the funds' own maturity mix |
| P2 | population | series funds only, × (Z.1 mutual funds + ETFs / N-PORT series-fund value) |
| D6 | diagnostic | ISIN recovery switched off (identical to the base, because recovery is deferred) |

**Deferred (N5), not computed in this landing:** the futures leg (§4.6), M2–M7, M9, M10, B1, B2, D1–D5 and ISIN recovery. Their definitions in the earlier draft are withdrawn rather than kept as promises.

**Grades.** M0, M1, M8 and D6 are MEASURED (the universe is the window survivors, and the denominator is stated). P1–P2 are HYPOTHESIS, because they rest on an untested assumption about the gap's mix.

**Labels.** `tsy_change.csv` carries the §1 label for the full period of every variant. For M8 the two dollar lines are scaled by ΔP(M8)/ΔP(base), which keeps them at the same fractions of ΔP.

**The path, not just two endpoints (C-070).** Period rows (2024, 2025, 2026H1 and the full period) are computed for every variant at the R2 dates only. S for all 11 windows is in `tsy_windows.csv`.

### 4.6 Futures leg: DEFERRED (N5), "not measured in this landing"
The design of the earlier draft (DIR lines with DERIVATIVE_CAT = FUT joined to FUT_FWD_NONFOREIGNCUR_CONTRACT on HOLDING_ID, contracts × face by tenor, 10-year equivalents at representative maturities) is not built. The reasons it would stay out of S when built still stand: futures are in zero net supply, so S + F is a risk-exposure sensitivity with its own label, and shares of P built from it do not add up across holders. The verdict file says "not measured in this landing".

## 5. Population reconciliation against Z.1 (printed, never forced)
**What is printed, per window.** The N-PORT Treasury value (both vintages; series funds and no-series filers separately) against the Z.1 levels at the quarter-end, $m ÷ 1,000: LM653061105 (mutual funds, S.124.1), LM563061103 (ETFs, S.124.3) and LM553061103 (closed-end funds, S.124.2). Every code is checked against the data dictionary text of its table before use.

**The endpoints**, re-read on 14 Oct:

| Quarter | Mutual funds | ETFs | Closed-end | Total |
|---|---:|---:|---:|---:|
| 2023Q4 | 1,389.7 | 502.3 | 2.1 | 1,894.0 |
| 2026Q2 | 1,741.2 | 807.6 | 2.0 | 2,550.9 |

- The ETF row is read from the committed `data/vintages/z1_etf1_2026Q2/S124_3_s.csv`: 502,261 and 807,612 $m.
- The totals above are the unrounded sums (1,894.036 and 2,550.863); the first draft's 1,894.1 and 2,550.8 were sums of rounded components.
- The other two rows come from the Fed's S.124.1 and S.124.2 tables, fetched by `bin/nport_fetch_z1.py`.

**Flows.** Also print Δ(N-PORT par) against the sum of the unadjusted Z.1 flows FU653061105 + FU563061103 + FU553061103 over 2024Q1–2026Q2. Grok's sum, built on seasonally adjusted annual rates, is 640.0 [L].

**Known differences**, stated in the output note:
- Z.1's ETF row includes commodity pools, which do not file N-PORT.
- Z.1 tables interval and tender-offer funds (S.124.6) and BDCs (S.124.5) separately, with no Treasury line.
- N-PORT has no ETF/mutual-fund flag, and Vanguard ETFs are share classes inside mutual-fund series, so the MF/ETF split cannot be reproduced.
- No-series filers ($4.4bn at the 2023Q4 matched window [S]) map loosely to closed-end plus interval funds.

**Coverage and the gap.** On the all-zip vintage, N-PORT is 95.4% of Z.1 at 2023Q4 and 101.8% at 2026Q2, and its value rose +788.0 against Z.1's +656.7 [L]. The matched vintage puts 2023Q4 at 1,776.0/1,894.0 = 93.8% [S]. That gap of roughly 131bn is unexplained, and it is the binding constraint on the Z.1-scaled arm (§9).

## 6. Checks and falsifiable success criteria

**Hard checks.** A FAIL sets exit status 2. The outputs are written to `data/nport/_FAILED/` and must not be landed (N11). The real gate is `tsy_checks.csv`: the handover quotes its FAIL count, not the exit code.

| id | criterion | reference |
|---|---|---|
| C1 | sha256 of every zip is recorded; each is compared with the previously committed `tsy_file_stats.csv` when one exists and with the pins in `tsy_anchors.csv`. Pins (bootstrap only): 2026q3 = `2f5ee059234d2e28f16d0451d9fcb405aab3dad5d92cded74c8ea9ffc4b66c38`; 2026q2 = `077cc836a978a593b29012219395fbe9c303d5e930f5be3b5f4353c3b02296fc`; 2024q1 = `7f391a05a71cec3fde5ce382e8ca8af9b11606ae85c465f99d98846e2d695254` | [S] for 2026q3 and 2024q1; 2026q2 from the committed census stats; the others have "N/A (no anchor)" |
| C2 | no (fund, report month) has more than one survivor in either vintage (`check_unique_survivors`) | the guard behind the must-fail test |
| C3 | 2026q3 SUBMISSION: 14,066 filings; REPORT_DATE 2026-06-30 7,063, 2026-07-31 4,195, 2026-05-31 2,516 | [S] |
| C4 | 2024q1 SUBMISSION: 12,576 filings; 2023-12-31 5,602, 2023-12-29 838 | [S] |
| C5 | 2023Q4 matched window, §3.1 rule before the content-duplicate step: 12,126 funds; Treasury value $1,776.0bn ± 0.1 (no ISIN recovery) | [S] |
| C6 | 2026Q2 window, the same basis: 13,907–13,910 funds; value $2,596.4bn ± 0.5 | [S]; the range allows for the 3 early May filings in 2026q2 [L] |
| C7 | kind rules (1)–(3) classify ≥ 99.9% of each window's Treasury value (base) | 2026Q2: 99.99% [S] |
| C8 | bucket sums equal window totals within 1e-6 $bn (IDENTITY) | — |
| C9 | fixed curve resolves to 2023-12-29; d10_fixed = 8.2233 ± 0.0001; fixed-curve par-bond factors 10y 1.0000, 2y 0.2309, 30y 2.1059 (± 0.0001) | [S] |
| C10 | §4.2: rebuilt public 10yeq within 0.1bn of `duration_supply.csv` at four dates (9,539.1; 11,003.6; 12,201.3; 12,757.4) | [S] csv |
| C11 | unpriced value ≤ 0.5% of window value (every window) | lens: 110–114 lines, $1.3–1.4bn [L] |
| C12 | N6: median of |reported DV01| / computed DV01 in [0.85, 1.15] at 2023Q4 and 2026Q2 (universe `tsy90_usd`) | the reviewer measured 0.999 on 350 funds |
| C13 | N-PORT window value / Z.1 sum in [0.90, 1.10] at 2023Q4 and 2026Q2 (FLAG at the other windows) | the band catches the two documented gross errors (DBT-only −13%, single date −46%) and passes the lens's 95.4% and 101.8% |
| C18 | no output header contains CUSIP, HOLDING_ID or ACCESSION_NUMBER, and no output file exceeds 2,000 rows (N12) | — |

**Flag checks.** They are printed with their numbers and explained in the build note. They do not affect the exit status.

| id | criterion | reference |
|---|---|---|
| C14 | CURRENCY_VALUE differs from PERCENTAGE/100 × NET_ASSETS by more than $5 + 0.01% on ≤ 1% of Treasury lines | 37 of 30,257 at 2026-06-30 [L] |
| C16 | MSPD and DEBT maturities agree on ≥ 99.9% of lines that have both | 53,783 of 53,785 [S] |
| C17 | count of partial amendments (§3.1) | — |
| C19 | content duplicates removed (N3), zero-line amendments ignored, TIPS lines read as original face (N4): counts, $ and the effect on ΔS | — |
| C20 | Z.1 reconciliation, printed and never forced (§5): change in N-PORT par and value against the sum of the unadjusted Z.1 flows and the Z.1 level change | Grok's seasonally adjusted sum 640.0 [L] |

**Dropped and listed as unverified (N13).** C15 (|r(M1) − 16.9%| ≤ 1.0pp against the lens's own implementation) rested on an [L] value the build cannot reproduce. It appears in `tsy_checks.csv` with result N/A so the omission is visible. The same holds for every [L] anchor not named in a hard check above.

**Re-run identity.** Run the script twice. `shasum -a 256 data/nport/tsy_*.csv` must be identical across the two runs.

## 7. Tests: `bin/test_nport_treasury_duration.py`
**Setup.** stdlib `unittest` on synthetic data only: zips built under `tempfile` with the real header lines hard-coded in the test (SUBMISSION 7 columns, REGISTRANT 12, FUND_REPORTED_INFO 47, FUND_REPORTED_HOLDING 22, DEBT_SECURITY 9, INTEREST_RATE_RISK 13). No real holding row is used, and the tests call the script's functions, not its CLI. The script runs this file as pre-flight (N11).

**Tests:**
1. **Must fail on broken input (C2).** `check_unique_survivors()` is called directly on a hand-built map in which one (fund, report month) appears twice: it must return FAIL, and it must return PASS on a clean map. If it returned PASS on the duplicate, the guard would be worthless and the test fails. No flag in production code switches de-duplication off (PR14).
2. **The amendment de-duplication.** One fund and one report month, with an NPORT-P and a later NPORT-P/A in the next zip: the selection returns one survivor, carrying the amendment's accession. (Run against a scratch copy with the de-duplication removed, this test fails.)
3. A synthetic file named `2026q3_nport.zip` makes C1 FAIL against a previously committed stats file with another sha256.
4. Month keying: a filing dated 2023-12-29 lands in the 2023Q4 window, and a fund with m₀−1 and m₀+1 but no m₀ gets m₀−1.
5. A cross-zip amendment supersedes the original, a same-day P/A beats the P, a zero-line P/A never replaces a non-empty original, and two survivors with the same CIK, REPORT_DATE, NET_ASSETS and line count under different fund keys collapse to the later filing.
6. The filter keeps a STIV bill, an SN TIPS and a USGA-912 TIPS. It excludes an RF/STIV fund share (typed UST, non-912), a DIR future, an RA repo, a non-912 UST and a blank-value line. A Short line keeps negative par.
7. Pricing: a coupon line priced by the script equals `r2.price_one` called directly; a 10-year par bond on the fixed curve has factor 1.0 within 1e-9; a strip has duration T/(1+y/2).
8. Coupon normalisation: a rate of 0.02125 with no MSPD match becomes 2.125.
9. TIPS: the index ratio from hand-built MSPD rows is (issued + adj − redeemed)/(issued − redeemed); a line whose CURRENCY_VALUE sits at the original-face reading is detected and its par multiplied; a line at the adjusted reading is not.
10. Buckets sum to the total, and the DV01 ratio uses magnitudes, so a fund with a negative sign gives the same ratio as its positive twin.
11. The no-network guard (N7): the replaced `fetch` returns when the cache file exists and raises SystemExit, naming the file, when it does not.
12. The verdict rule: ΔS 459 → PARTICIPANT, 460 → FIRST-ORDER SINK, 99 → BYSTANDER; two arms with different labels give "NOT ESTABLISHED".

## 8. Runtime and run plan
**Measured** [S, warm cache]: 2026q3 from metadata through the holdings stream, the DEBT join and the MSPD load, 7.1 s; 2024q1 metadata and holdings, 4.4 s; sha256 of two zips, 2.3 s. Builder, 14 Oct, whole build over the 11 zips: pass A (metadata and line counts) 63 s, the full run 136 s end to end.

**Design for memory (N9).** Small tables load only the columns they need. DEBT_SECURITY is streamed against an ID set. Each zip's holdings are streamed twice: once for the per-filing line counts that the survivor rule needs, and once, after the global survivors are known, for the lines of surviving filings only, which are priced and discarded before the next zip. No member over 10 MB goes through `list(DictReader)`.

Run every command in the foreground.

1. In the clone: run `git pull --ff-only` and `bin/check.sh --handover`. Set the GitHub noreply `user.email` (CLAUDE.md) before any commit.
2. Fetch the Z.1 tables once with `python3 bin/nport_fetch_z1.py` and keep the output (it records the release zip's sha256).
3. Run `python3 bin/test_nport_treasury_duration.py`. All tests pass.
4. Run `python3 bin/nport_treasury_duration.py --r1-cache <cache> --r2-cache <cache>`. Read every line of `tsy_checks.csv`, not the exit code.
5. Re-run and compare the sha256s.
6. Run `bash bin/check.sh --all`. Pass means the five ✓ guard lines, `✓ no killed claims found` and `✓ page clean`.
7. Hand back to the supervisor. Landing is the supervisor's rung after review, not the builder's. It covers:
   - the findings note and its read-table row;
   - `data/series.tsv` rows;
   - a RESEARCH_STATE §5 update that names its goal row;
   - the CALENDAR row (added by the builder: it re-runs R2, then this script, when the 2026q4 zip posts around January 2027, dated before the census row);
   - the handover row.

   This parcel makes no change to the page.

## 9. Open questions (none may be closed by assumption in the build)
- **OPEN 1 (binding): the change gap between N-PORT and Z.1.** In value, N-PORT rose +788.0 against Z.1's +656.7; in par, N-PORT rose +799.9 against flows of about 640 [L]. The gap's maturity mix decides how far the Z.1-scaled arm sits below the measured arm. The build prints Δvalue for the top 20 registrants (`tsy_top_funds.csv`) so the supervisor can test candidate explanations; it does not adjust for them.
- **OPEN 2:** each fund's convention for TIPS BALANCE, adjusted face or original face. N4 reads it line by line against CURRENCY_VALUE and counts the result; the rule cannot tell the two apart when the index ratio is below 1.05, and a mis-read line is still possible near the threshold. The count and par are reported, not assumed.
- **OPEN 3:** representative maturities for the futures. Deferred with the futures leg (N5). Cheapest-to-deliver durations need the exchange's contract specifications, and cmegroup.com blocks curl (CLAUDE.md).
- **OPEN 4:** the sign of DV01. The readme gives no direction. Whether the form's instructions do was not re-read here. The check uses magnitudes.
- **OPEN 5:** whether every NPORT-P/A is a complete restatement. C17 measures line counts only.
- **OPEN 6:** an MF/ETF split needs Form N-CEN, which is an sec.gov fetch for the supervisor only.
- **OPEN 7:** r per quarter needs R2 at quarter-ends. R2's DATES holds five dates, and this spec does not extend them.
- **OPEN 8:** the 2026Q3 window (August to October reports) arrives with the 2026q4 zip. R2 has no 2026-09-30 row.

**Candidate do-not-say items**, to be registered only if the build confirms them:
- that a single N-PORT report date gives registered funds' Treasury stock;
- summing N-PORT DV01 across funds;
- reading "+$3.4trn" against a 30 Jun N-PORT endpoint.

## 10. Supervisor amendments, 14 Oct (after two adversarial reviews; these OVERRIDE anything above)

The builder applies these to sections 1–9 first, so that the spec and the code agree, then implements. "CR" refers to the
correctness review and "PR" to the practicality review.

**N1. The decision rule is replaced (CR1, CR2).**
- §1's relative rule (r₁ = 1/7 against s₀) is withdrawn. It equals the funds' starting share, and it was set after provisional
  numbers had been seen.
- The verdict uses the lines in the research item, which were written on 14 Oct before any measurement:
  - first-order duration sink if ΔS ≥ $460bn of 10-year equivalents (one-seventh of ΔP = $3,218.3bn, end-2023 to 30 Jun 2026);
  - the item's rounder "$0.5trn" is printed beside it;
  - bystander if ΔS < $100bn;
  - participant in between.
- The verdict is computed separately for two arms:
  - the **measured arm**: N-PORT's own lines, on the base defined in N2;
  - the **Z.1-scaled arm** (P1/P2).
- If the arms give different labels, the published verdict is "not established", and both rows are printed.
- Pro-rata is reported per arm against that arm's own starting share: excess = r − s₀, in pp and in $bn. If the two arms' signs
  differ, the text says "sign not established".
- The notes state that the spec author and a reviewer saw provisional numbers before the build. The verdict lines predate both.
- The verdict row says "cash Treasuries only". The futures sensitivity is deferred (N5), and it is printed as "not measured in
  this landing", never folded into S.

**N2. Base vintage (CR3).**
- Use all zips, with a filing-lag cut at both ends: FILING_DATE ≤ REPORT_DATE + 62 days.
- The matched-vintage figures become a variant.

**N3. Survivor key (CR4).**
- Add a content-duplicate check: same CIK, REPORT_DATE, NET_ASSETS and Treasury line count under different fund keys. Keep the
  latest filing and report the count.
- A zero-line NPORT-P/A never replaces a non-empty original.
- Test `check_unique_survivors()` directly on a hand-built duplicate map, with no test hook in production code (PR14).

**N4. TIPS (CR5).**
- Where BALANCE is original face, apply the MSPD index ratio (issued + inflation_adj − redeemed) / (issued − redeemed) at the
  report date.
- Detect original face by comparing BALANCE × the ratio against CURRENCY_VALUE (state the rule).
- Never back-solve par from a modelled price.

**N5. Scope for the first landing (PR3).**
- Keep:
  - the base, M1, M8 (one alternative curve), P1 and P2, D6;
  - the Z.1 reconciliation;
  - `tsy_buckets` (the maturity table this item is named for), `tsy_top_funds` (≤70 rows; it serves OPEN 1), the verdict file,
    `tsy_checks` and `tsy_file_stats`;
  - checks C1–C11 and C13.
- Defer:
  - the futures leg;
  - M2–M7, M9, M10, B1, B2 and D1–D5;
  - ISIN recovery (optional; it moves $1.79bn).

**N6. DV01 cross-check (CR9).**
- Keep it as a HARD check on magnitude only, and print the sign split as filed.
- It covers funds with Treasuries ≥ 90% of NAV and a USD row. The median of |reported DV01| / computed DV01 must lie within
  0.85–1.15. The reviewer measured 0.999 on 350 funds.

**N7. R2 as a library (PR1, PR5).**
- The fetch guard raises only if the cached file is absent. Add a test for that guard.
- `securities_for` is a closure, so copy its roughly 10 lines with a comment naming the R2 function. C10 guards them by
  rebuilding R2's public totals at the four R2 dates to within 0.1bn.
- Define the expected cache set explicitly, as a list, not a glob.
- Cite functions by name, not line numbers.

**N8. Refresh (PR2).**
- Discover zips by glob and derive the windows from them.
- Move the anchors and pins to a committed `data/nport/tsy_anchors.csv`, with "N/A (no anchor)" for windows that have none. C1
  compares against the previously committed `tsy_file_stats.csv`, with the pins as bootstrap only (PR11).
- Add a `CALENDAR.tsv` row, dated before the existing 2027-01-10 N-PORT row: "refresh R2 (delete the 2026 curve caches first),
  then re-run `bin/nport_treasury_duration.py`".

**N9. Memory (PR4).**
- Small tables load only the columns they need.
- DEBT_SECURITY and IDENTIFIERS are streamed against an ID set.
- Each zip's lines are discarded after use.
- Never `list(DictReader)` a member over 10 MB.

**N10. Z.1 inputs (PR6).**
- Add `bin/nport_fetch_z1.py`. It fetches S.124.1 and S.124.2 from www.federalreserve.gov only, with the CLAUDE.md non-SEC
  User-Agent, and records the sha256.
- Commit the two extracted CSV tables: they are public domain.
- The S.124.3 ETF row is read from the committed `data/vintages/z1_etf1_2026Q2/`.

**N11. Failure handling and gate (PR8, PR9).**
- On any hard FAIL, write outputs to `data/nport/_FAILED/` and leave the committed files untouched. Exit 2.
- The script runs its own test file as pre-flight.
- The real gate is `tsy_checks.csv`, and the handover quotes its FAIL count.

**N12. Reproducibility (PR10, PR12, PR13).**
- The docstring carries the SEC landing page, the URL pattern, the sha256 list and the cache prerequisites.
- A missing cache prints the exact command to run.
- Add a three-line N-PORT paragraph to REPRODUCE.md.
- Use `math.fsum` for every aggregate.
- Hard check: no output header contains CUSIP, HOLDING_ID or ACCESSION_NUMBER, and no output exceeds 2,000 rows.

**N13. Anchors (PR7).**
- The spec's [L] anchors that the build cannot reproduce are dropped from the hard checks, and listed as unverified.
- The independent verifier's re-derived numbers are recorded in the findings note.

## 11. Builder's choices where §§1–10 were silent or ambiguous (14 Oct; for the reviewers)

These are implementation decisions, listed so that nobody has to infer them from the code. Each can be reversed in `bin/nport_treasury_duration.py`.

1. **N2, "a filing-lag cut at both ends."** Read as "at both endpoints", and applied to every window so that the 11 windows are one series. Matched vintage (M1) has no lag cut, as in the first draft.
2. **Which arm is which (N1).** The measured arm is M0 alone. The Z.1-scaled arm is the band [min, max] of ΔS over P1 and P2, and its label uses the band (FIRST-ORDER only if the low end clears $460bn, BYSTANDER only if the high end is under $100bn). M1 and M8 are printed as sensitivities and do not enter the published verdict.
3. **M8** uses the 2026-06-30 curve (the other endpoint's). Its dollar lines are scaled by ΔP(M8)/ΔP(base). The M8a/M8b variants are deferred with the rest of N5.
4. **Comparator.** For M0, M1, P1, P2 and D6 the R2 column is `public_10yeq_fixed_bn` as published (so ΔP = 12,757.4 − 9,539.1 = 3,218.3). C10 checks the in-script rebuild against that column to 0.1bn. M8's comparator is the rebuild on the 2026-06-30 curve.
5. **TIPS (N4).** The arbiter between "BALANCE is adjusted" and "BALANCE is original face" is R2's own TIPS clean price at the report date's real curve, used only to choose between two discrete readings (§3.3); par is never back-solved from it. Threshold 1.05. The index ratio between MSPD record dates is interpolated linearly in days.
6. **Stub (N3).** "Zero-line" means zero rows of FUND_REPORTED_HOLDING of any kind, counted in the first holdings pass. It is why each zip's holdings are streamed twice.
7. **C5/C6** are evaluated on the matched vintage under the §3.1 rule *before* the content-duplicate step, because that is the basis of the [S] anchors. On this data the step removes nothing (the lag cut has already removed the later filing of each content-duplicate pair), so the two bases coincide.
8. **C1 and re-run identity.** The comparison with the previously committed `tsy_file_stats.csv` is printed to stderr and fails the check on a mismatch, but the CSV row does not say how many zips were compared, so the output does not depend on whether a previous file existed.
9. **DV01 universe (N6)** is "Treasuries ≥ 90% of NET_ASSETS and a USD row". The stricter "and no DIR line in the filing" is printed beside it and is not the hard check.
10. **Exit codes.** 0 all hard checks pass; 2 a hard check failed (outputs under `_FAILED/`); 1 a refusal (missing input, failed pre-flight tests).
