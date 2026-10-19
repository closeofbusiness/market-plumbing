# Spec: Japanese life insurers' acquisitions and dispositions of foreign long-term debt, monthly (test A; spec author, 19 Oct 2026; rewritten after rounds 2 and 3)

*CALENDAR rows 2026-11-02 (build test A) and 2026-11-10 (the October 2026 forecast, registered 19 Oct). Scoping: Grok g8 parcel 1 in
`_research/2026-10-19-Grok-G8-Returns.md`; the supervisor's checks at the top of that file outrank Grok. House style follows
`_research/2026-10-19-FX-Hedged-Treasury-Yield-Spec.md` and `_research/2026-10-18-FX-Rate-Gap-Weekly-Spec.md`. The MoF parsing and fetch
code are modelled on `bin/fx_rate_gap.py` (`Fetcher`, `parse_feio`, the STOP latch).*

*This text folds in the supervisor's rulings of round 1, round 2 (second review) and round 3 (Grok attack), which stay at the end as the
record; the body is authoritative. "Observed" means seen by the spec author on 19 Oct 2026, one request per URL, with the CLAUDE.md non-SEC
User-Agent (26 requests, all HTTP 200, no redirect, no refusal). "Supervisor" means fetched by the supervisor on 19 Oct (MoF FAQ).
"Relayed" means taken from Grok or an earlier spec and not re-read. The window statistics in C13 were computed by the second reviewer
from the 8 Oct vintage before the build, and re-derived by the spec author from the cached copy of that vintage during this rewrite; they
are descriptive pins, and no rule of section 4 or 5 was changed after they were seen. No data were fetched for this rewrite.*

## 0. Goal, and what the result can and cannot say

- **Measure** Japanese life insurers' monthly acquisitions, dispositions and net acquisition of foreign long-term debt securities, as
  reported to the Ministry of Finance (MoF) by designated reporters, from January 2005 to the latest month, with non-life insurers, banks,
  trust accounts, investment trusts and the total of all designated reporters beside them. Mark the Bank of Japan (BoJ) policy dates.
- **Answer** six descriptive questions fixed in section 4, and **score** the October 2026 forecast registered in CALENDAR row 2026-11-10,
  on the 10 Nov file, without changing its rule.
- **Keep** every vintage of the file and record each revision of the committed sectors.

**Words.** The object is **net acquisition** (plus) or **net disposition** (minus). Disposition is the file's term for a decrease in
holdings: sales, and also redemptions of overseas government bonds, which MoF's FAQ A5 says "are included in the disposition"
(supervisor); redemptions of other bonds may be included too (O-9). Generated text never says "sold" or "net sales" for this series; it
says "net disposition" or "negative net". ("Sales" appears only inside the gloss of disposition.)

**It can say:** the sign, size and timing of reported contracts by investor type, and how life insurers' recent months compare with
earlier years and with other designated reporters. These are MEASURED. Annual and fiscal-year totals are IDENTITY sums.

**It cannot say:**
- why any investor acquired or disposed of bonds, or any effect on a yield, spread or exchange rate;
- how much of a disposition was a sale and how much a redemption;
- anything about US Treasuries alone, about currency, or about hedged against unhedged bonds (the file mixes all three);
- anything about holdings (these are flows of contracts);
- anything about bonds held through funds (since 2014 fund shares sit with equities in monthb2, with no bond/equity split).

**Required sentence (README and printout):** "These are recorded acquisitions and dispositions, redemptions included. They do not show why
any investor acquired or disposed of bonds, or any effect on prices."

## 1. Hard requirements

- **R1. Free public data only (E-005). No FRED, Bloomberg or sec.gov.** Host allowlist for `bin/jp_life_foreign_bonds.py`:
  `www.mof.go.jp`, `www.boj.or.jp`. Any other host is refused before the request. Every request is one of the exact URLs of section 2.
- **R2. User-Agent** exactly `Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)`. Assert no `@`. Never send an
  email address, a name, `SEC_UA` or `CLAUDE_CODE_USER_EMAIL`.
- **R3. Polite, refusal-safe fetches** (the fx_rate_gap rules). GET only, sequential, at least 2 s between request starts, at most 20 per
  run (16 expected on the first run, 4 after), no redirect followed. Nothing retries. `fetch_log.csv` records
  `utc_time, host, path, status, bytes, sha256`.
  - **Order:** the four MoF CSVs first, then the BoJ PDFs.
  - **Two latches.** A MoF failure (any status other than 200, or a body failing 2.4) writes `data/vintages/jp_life_foreign_bonds/STOP`
    and ends the run. A BoJ failure writes `data/vintages/jp_life_foreign_bonds/STOP_BOJ` and ends only the BoJ part. **STOP_BOJ never
    gates a MoF fetch, a build or the scoring**; STOP gates MoF fetches only (`build` stays offline and runnable).
  - **Only a person deletes either file.** An agent that meets a latch reports it and stops; it never deletes, renames or edits it,
    even when its own content test caused the latch (the hedged-yield builder deleted STOP twice; that must not recur).
- **R4. Cache.** Raw CSVs and PDFs go to `data/vintages/jp_life_foreign_bonds/` (gitignored). A `--cache` path inside the repository is
  refused unless git reports it ignored (as `fx_rate_gap.check_cache`). Committed files follow section 6.
- **R5. No causal language** (G15), over every committed text field. The required sentence is the one exemption.
- **R6. Code.** `bin/jp_life_foreign_bonds.py` is new, Python 3 standard library only. It may import helpers from `bin/fx_rate_gap.py`
  read-only (`render_csv`, the `Fetcher` pattern, `CAUSAL_RX`) or copy them; it changes no existing script except the optional M16 guard
  in `bin/check.sh` (section 9).
- **R7. The registered forecast is frozen.** The rule, point and range of CALENDAR row 2026-11-10 are constants in the code and must equal
  the row's text (G12). Any change after 19 Oct is a post-registration change: it goes in this spec's log with the old values kept, and
  the scoring of record still uses the registered values.
- **R8. Exact arithmetic.** File values are integers in ¥100 million. Sums, order statistics and comparisons use those integers; means,
  medians, shares and ¥ billion values use exact rationals (`fractions.Fraction`). Rounding happens only when text is written, **half away
  from zero**, never Python's `round()` (G10). ¥ billion = ¥100m ÷ 10, one decimal; shares in percent, two decimals.

## 2. Data

### 2.1 Requests (all observed 19 Oct, HTTP 200)

Base `https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/`:

| File | Title (English header line) | Observed |
|---|---|---|
| `monthb3.csv` | Purchases and Sales of Foreign Securities by Residents by Types of Investors(Long-term debt securities) | 113,821 bytes, sha256 `5c70e53f3c95d5c7cdb5041195d386cec46e67860cd142e6f3f825bb72d26cc1`, Last-Modified Wed 07 Oct 2026 22:50:46 GMT, "Final Update  October 8, 2026" |
| `monthb1.csv` | ...(Total) | 116,077 bytes, `f9d96ca4553ff7dbe211fbc2d2667276dc25e027cc8f54906ca8290602d28584` |
| `monthb2.csv` | ...(Equity and investment fund shares) | 96,214 bytes, `eb8570560c63c0ae5721e5cf38b6c005fad1dbc4b3b6ff125c3cb7b4f0dad7f6` |
| `monthb4.csv` | ...(Short-term debt securities) | 84,610 bytes, `751df62b428c5632546b37c2219de83e7e67f881f52b63f23b1f7e8fa51036d6` |

BoJ statements, `https://www.boj.or.jp/en/mopo/mpmdeci/{path}.pdf`, fetched once each after the MoF files and cached as immutable (12
requests on the first run only). Each row was read by the spec author with `pdftotext`; the build checks the sha256, not the text.

| Decision | Path | Effective | What the statement says (short phrase) | sha256 (first 16) | Bytes |
|---|---|---|---|---|---|
| 2013-04-04 | `mpr_2013/k130404a` | - | introduces "Quantitative and Qualitative Monetary Easing" | `808a67d9016cf22e` | 157,105 |
| 2016-01-29 | `mpr_2016/k160129a` | - | "negative interest rate of minus 0.1 percent" | `604f4b9bb33f1318` | 30,533 |
| 2016-09-21 | `mpr_2016/k160921a` | - | introduces "Yield Curve Control" | `c15180b02d80fd86` | 44,389 |
| 2022-12-20 | `mpr_2022/k221220a` | - | 10-year band widened to "around plus and minus 0.5 percentage points" | `7d97749ccc1e3a3b` | 207,453 |
| 2023-07-28 | `mpr_2023/k230728a` | - | fixed-rate purchases "at 1.0 percent" | `fd3f4c4232ee8b71` | 465,135 |
| 2023-10-31 | `mpr_2023/k231031a` | - | "upper bound of 1.0 percent" as a reference | `575d056d656bd909` | 462,610 |
| 2024-03-19 | `mpr_2024/k240319a` | 2024-03-21 | call rate "around 0 to 0.1 percent" | `e07e26da39f4428b` | 474,660 |
| 2024-07-31 | `mpr_2024/k240731a` | 2024-08-01 | "around 0.25 percent" | `bbe8f2154393224c` | 482,007 |
| 2025-01-24 | `mpr_2025/k250124a` | 2025-01-27 | "around 0.5 percent" | `6924980a4aea9899` | 469,888 |
| 2025-12-19 | `mpr_2025/k251219a` | 2025-12-22 | "around 0.75 percent" | `bcef45990da1895d` | 228,103 |
| 2026-06-16 | `mpr_2026/k260616a` | 2026-06-17 | "around 1.0 percent" | `93fe8f756750d1b3` | 190,988 |
| 2026-09-18 | `mpr_2026/k260918a` | 2026-09-24 | "around 1.25 percent" | `36d7aa63ff283e25` | 208,861 |

Full sha256 values are in `.../scratchpad/g9/dl_testA/boj/` (supervisor's scratch; the builder records its own and must match the first
16 characters). Completeness for 2024-2026: the BoJ release index pages for 2024, 2025 and 2026 (observed) list policy-change documents
only for the six dates above. Pre-2024 rows are markers for the long chart, not a complete list. The build does not fetch index pages.

Read once, not fetched by the build: `index.htm`, `data.htm`, `terms.html`, the English `schedule.htm`, the 2013 methods notice
`notice/notice20131227.pdf` (918,019 bytes), the MoF copyright page `https://www.mof.go.jp/about_mof/notice/index.html` (all observed);
MoF's English FAQ `https://www.mof.go.jp/english/policy/international_policy/reference/itn_transactions_in_securities/faq_its_english.html`
(supervisor: A1 scope, A5 redemptions, A6 recording dates); the English index page (relayed: its sign banner is stale, 2.3); BoJ FAQ No. 14
`https://www.boj.or.jp/en/statistics/outline/exp/faqbpsm6.htm` (relayed: investor-type classification).

### 2.2 Layout of the four CSVs (identical in shape and labels; observed)

- **Encoding CP932**, comma-separated, 329 lines on 19 Oct. Unit line "（Unit: 100 mil Yen）" (¥100 million). Thousands commas inside quotes.
- **Header rows** (0-based rows 0-10): titles, unit, sector names in Japanese and English, and the Acquisition / Disposition / Net row.
  **The "Final Update" cell is column 18 in b1-b3 and column 19 in b4**, so it is found by text, never by position.
- **Columns**: 0 year (written only on January), 1 Japanese month, 2 English month (`Jan`...`Dec`), then 17 blocks of three
  (Acquisition, Disposition, Net).
- **Block labels (R2-2).** For each block's first column (3 + 3k), take the first non-empty cell of 0-based header rows 7 and 8 whose
  text, after Unicode NFKC normalisation and stripping of surrounding whitespace, begins with an ASCII character; match it by **exact
  equality** against the "NFKC label" column. Never by fixed index, never by substring ("Banks" is inside "Trust Banks", "Other" inside
  three labels). The raw cells use full-width characters; the fixtures of G1 use these raw strings.

| # | Raw cell (row) | NFKC label | Code |
|---|---|---|---|
| 1 | `（a+b+c+ｄ)` (7) | `(a+b+c+d)` | `designated_reporters_total` |
| 2 | ` Public Sector` (7) | `Public Sector` | `public` |
| 3 | `Central Bank (a)` (8) | `Central Bank (a)` | `central_bank` |
| 4 | `General Government (ｃ)` (8) | `General Government (c)` | `general_govt` |
| 5 | `Deposit-taking Corporations (b)` (7) | `Deposit-taking Corporations (b)` | `deposit_taking` |
| 6 | `Banks（Banking Accounts)` (8) | `Banks(Banking Accounts)` | `banks_banking` |
| 7 | `Trust Banks(Banking Accounts）` (8) | `Trust Banks(Banking Accounts)` | `trust_banks_banking` |
| 8 | `Other Sectors （d)` (7) | `Other Sectors (d)` | `other_sectors` |
| 9 | `Other Financial Corporations` (8) | same | `other_financial` |
| 10 | `Banks and Trust banks（Trust Accounts）` (8) | `Banks and Trust banks(Trust Accounts)` | `trust_accounts` |
| 11 | `Banks（Trust Accounts）` (8) | `Banks(Trust Accounts)` | `banks_trust` |
| 12 | `Trust Banks（Trust Accounts）` (8) | `Trust Banks(Trust Accounts)` | `trust_banks_trust` |
| 13 | `Financial Instruments Firms` (8) | same | `fi_firms` |
| 14 | `Life Insurance Companies` (8) | same | `life` |
| 15 | `Non-Life Insurance Companies` (8) | same | `nonlife` |
| 16 | `Investment Trust Management Companies` (8) | same | `inv_trust` |
| 17 | `Others` (8) | same | `others` |

  (Rows 7 and 8 also hold Japanese cells, for example 銀行等（信託勘定） above block 11; the ASCII-leading rule skips them.)
- **Month rows**: 2005-01 to 2026-12 (264 rows); 2026-10 to 2026-12 are **blank** (not published) and are never a month of any series,
  window or count. The month is taken from the **English column only**; the Japanese column (full-width digits such as `１月` from 2023) is
  ignored, and the output must follow the English column when the two disagree (G2).
- **Missing marker `-`**: central bank, general government, banks (trust accounts) and trust banks (trust accounts) are `-` in every row
  2005-01 to 2013-12 (324 cells). `-` is missing, never zero. No other cell of a published month is blank or `-`.
- **Total rows** after the months: `...2005CY` to `...2025CY`, then `...2005FY` to `...2025FY` (Japanese fiscal year, April to March,
  labelled by its starting year). No 2026CY row yet. Then notes (備考 and Notes 1-4).

### 2.3 Definitions, sign and breaks

- **Long-term debt**: bonds issued with an original maturity of more than one year (issue to maturity), including yen-denominated foreign
  bonds (terms.html, observed). **Classified by the residence of the issuer**, not the currency (2013 notice, weekly-table Note 2; O-4
  closed). Acquisition and disposition are increases and decreases of assets (terms.html).
- **Disposition includes redemptions** of overseas government bonds held by residents (FAQ A5, supervisor). Purchases and sales are
  recorded on the execution date, redemptions on the redemption date (FAQ A6). Redemptions of other bonds are not addressed (O-9).
- **Reporters**: designated major investors (banks, financial instruments firms, insurers, investment trust and asset management
  companies, securities finance and money-market dealers) named by the Finance Minister. The survey is narrower than balance-of-payments
  portfolio investment and released earlier: the month after, against the month after next (index.htm, observed; FAQ A1, supervisor). The
  total block is therefore `designated_reporters_total`, never "all residents".
- **Sign.** The file's own: Note 2, plus is net acquisition, minus is net disposition. data.htm and the 2013 notice: before January 2014
  the published tables used the opposite sign, and MoF recompiled **only the sign of the net** for earlier months. **The file confirms it:**
  Net = Acquisition − Disposition in every non-missing cell of all four files, within 1 unit from 2014 and within 4 before (monthb3: 0 of
  2,601 post-2014 cells and 17 of 1,404 pre-2014 cells differ by more than 1; largest gap 4). The English index page's banner, which still
  describes the pre-2014 convention, is recorded in SOURCES.md as stale and is never coded (R3-6). G6 tests the identity on every build.
- **Net is a cell, not a subtraction.** MoF rounds each cell separately, so Net can differ from Acquisition − Disposition by 1 (2026-09
  life: 5,487 − 8,374 = −2,887; the Net cell is −2,886). Every series, window and score uses the Net cell.
- **Break at January 2014 (not restated).** The 2013 notice: from 2014 open-end contractual investment trusts, previously in long-term
  debt, are counted in "Equity and investment fund shares", and the five-sector split is not applied to earlier months. Every monthly row
  carries `basis` (`old_to_2013` or `new_from_2014`); section 4 uses 2014 onward only.
- **Break at October 2007** (Note 3): "securities companies" and "investment trust companies" became financial instruments firms and
  investment trust management companies; months to September 2007 use the old categories.
- **Labels the README must carry.** `inv_trust` is "investment trust management companies, including asset management companies" (file
  Note 4); the README points to BoJ FAQ No. 14 for the classification. `trust_accounts` is "trust accounts of banks and trust banks".
  Neither column is ever called "pensions" (O-5, O-10).
- **March 2024.** The 19 March 2024 decision took effect on 21 March, so most of March 2024 is before it. W2 starts in March 2024 as
  registered; W2b, from April 2024, leaves it out (R3-5).

### 2.4 Content test for each fetched body

MoF (fail = STOP): CP932 decodes; line 2 contains the expected English title of 2.1; a label cell normalises to
`Life Insurance Companies`; a cell matches `Final Update\s+([A-Z][a-z]+ \d{1,2}, \d{4})`; the unit line contains `100 mil Yen`; at least
250 month rows parse with 54 cells each. BoJ (fail = STOP_BOJ): starts with `%PDF`, at least 20,000 bytes, sha256 equal to 2.1.

### 2.5 Release timing, vintages and revisions

- **Release**: 08:50 JST, "subject to change" (English schedule.htm, observed). September 2026 was released 8 Oct 2026; **October 2026 on
  10 Nov 2026**; November 2026 on 8 Dec 2026; December 2026 on 12 Jan 2027.
- **Vintage** = the file's own "Final Update" date. `fetch` saves a body only when its sha256 differs from every cached vintage of that
  file, as `monthbN_<final_update YYYY-MM-DD>_<sha256 first 12>.csv`. The 8 Oct vintage of monthb3 is pinned (2.1).
- **Capture deadline.** The 10 Nov file is overwritten at the 8 Dec release. It must be fetched **before 8 Dec 2026 08:50 JST (7 Dec
  23:50 UTC)**; otherwise the score cannot be of record (section 5). The supervisor puts this deadline in CALENDAR row 2026-11-10.
- **Revisions.** index.htm says no corrections are currently published; no revision calendar was found. **The first observable revision
  check is the 10 Nov vintage.** `build` diffs each pair of consecutive cached vintages, cell by cell, over month and total rows of all
  four files, **for the six committed sectors only**, and writes each difference to `revisions.csv` with old and new values. A month that
  goes from blank to a number is `new`, not `revised`.
- **If the 8 Oct vintage is missing from the cache** (the builder starts after 10 Nov), C10 uses the 24 pins of section 8 and says so, and
  C15 diffs the pins against the earliest cached vintage as INFO.

### 2.6 Licence (observed)

- **MoF**: the copyright page puts site content under the Public Data License 1.0 (PDL1.0) unless marked otherwise; the CSVs carry no other
  marking. PDL1.0 (Digital Agency page): copying, public transmission and adaptation allowed, commercial use included; numerical data are
  outside copyright; cite the source, and when content is edited or processed say so and by whom, and never present it as unprocessed
  government data.
- **Commit decision (ruled, O-2):** commit the derived tables of section 6 with the citation and processing statement; raw vintages stay in
  the gitignored cache; `revisions.csv` keeps old and new values for the committed sectors.
- Citation line (every committed file and README): `Source: Ministry of Finance Japan, "International Transactions in Securities"
  (designated reporters, monthly; monthb1-b4.csv), <URL>, PDL1.0, retrieved <dates>. Processed by the Third Derivative project (re-laid
  out and summed; values unchanged).`
- **BoJ**: only dates and phrases under 15 words are cited; the PDFs stay in the cache. Copying with credit is allowed and commercial
  copying excluded (relayed). Credit: "Bank of Japan, Statement on Monetary Policy, <date>".
- **Press reference points** (C14): quotes of 15 words or fewer, in SOURCES.md only.

## 3. Method

1. **Parse** (G1-G5, G7): header rows found by text; blocks mapped by the NFKC labels of 2.2; year carried down; month from the English
   column; `-` and blank are missing; blank months dropped; total rows recognised by `(\d{4})(CY|FY)$` and never entering the monthly series.
2. **Validate** each vintage (G6, G8, G9). Each check prints its observed maximum; a gap above tolerance is a FAILED build (outputs to
   `data/jp_life_foreign_bonds/_FAILED/`, exit 1).
   - Sign identity (2.3): tolerance 1 from 2014, 4 before.
   - Within-file additivity, net column: `other_financial` = `trust_accounts` + `fi_firms` + `life` + `nonlife` + `inv_trust` (observed
     max 2); `designated_reporters_total` = `public` + `deposit_taking` + `other_sectors` (max 1); from 2014 `trust_accounts` =
     `banks_trust` + `trust_banks_trust` (max 1). Tolerance 3.
   - **Cross-file additivity (R2-1):** b1 = b2 + b3 + b4 for every sector, every field and every month. **Tolerance 4 over all 17 sectors**
     (observed max 4: `other_financial` acquisition 2007-01 and disposition 2010-03); **tolerance 2 over the six committed sectors**
     (observed max 1). The four files are compared **only when their Final Update dates are equal**; otherwise the check is WARN, not FAIL.
   - Annual sums: the 12 months against the file's CY and FY cells, all sectors and fields; observed max 7 (CY) and 6 (FY), both in
     `other_financial`; tolerance 12.
3. **Monthly table**: six sectors (`designated_reporters_total`, `banks_banking`, `trust_accounts`, `life`, `nonlife`, `inv_trust`) x four
   instruments (`ltd` = b3, `equity_funds` = b2, `std` = b4, `all` = b1) x every published month of the latest vintage: **6,264 rows at the
   8 Oct vintage** (6 x 4 x 261).
4. **Annual table**: calendar and fiscal years 2005-2025 summed from months, with the file's total cell and the difference beside it, and a
   `basis`: `old_to_2013` (CY to 2013, FY to 2012), `new_from_2014` (CY and FY from 2014), `mixed_2013_2014` (FY2013 only: nine old-basis
   months and three new), `mixed_2007` (CY2007 and FY2007: old and new investor categories). The README annual table starts at CY2014.
   Year-to-date rows for the current period, where L is the latest published month: `CY_YTD` = January to L of L's year, written only when
   L is not December; `FY_YTD` = April to L of the fiscal year containing L (when L is January to March, April of the previous calendar
   year to L), written only when L is not March. At L = 2026-09: CY_YTD 2026-01..09, FY_YTD FY2026 = 2026-04..09.
5. **BoJ table**: the 12 rows of 2.1 with the month of each decision.
6. **Questions** (section 4) and the **forecast score** (section 5).

## 4. Descriptive questions, fixed before the build

Instrument `ltd` unless named. Windows (2014 onward only, because of the 2014 break; published months only):
- **W0** 2014-01 to 2018-12 (60 months, context); **W1** 2019-01 to 2023-12 (60 months; it contains 2022 and 2023);
- **W2** 2024-03 to L (31 months at L = 2026-09); **W2b** 2024-04 to L (30 months; sensitivity, without March 2024, see 2.3).

For each window and each of the six sectors, `questions.csv` holds: months, sum of net, mean monthly net, median monthly net, months with
net disposition (net < 0), mean monthly acquisitions, mean monthly dispositions. Each value names its unit (¥ billion, one decimal, or
percent) and its denominator (months in the window, or the named total).

- **Q1. Life insurers' sign and size, W2 against W1 and W0.** Mean, median and the share of months with net disposition, **always reported
  together**, with the window sums, the note that W1 contains 2022 and 2023, and the note that dispositions include redemptions of
  overseas government bonds. Notable (unchanged from registration): W2 mean monthly net below W1's.
- **Q2. Acquisitions or dispositions.** Δ(mean net) W1→W2 = Δ(mean acquisitions) − Δ(mean dispositions), IDENTITY, both terms reported.
  Notable: the larger of the two terms in absolute value is named (no reason is given). Dispositions include redemptions (2.3).
- **Q3. Share of the designated-reporter total.** Labelled "**share of reported gross contracts (dealer-inclusive)**": life insurers'
  acquisitions over `designated_reporters_total` acquisitions, and dispositions over dispositions, window sums (denominators always
  positive). The dealers' (`fi_firms`) share of the same totals is reported beside it, and the README names it. Life and total nets side
  by side. A net ratio is reported only when both nets have the same sign and |ratio| ≤ 1; otherwise the statistic is the word
  `opposite_sign` or `exceeds_total`, never a negative or oversized share.
- **Q4. Comparators.** The Q1 statistics for non-life insurers, banks (banking accounts), trust accounts and investment trusts. Notable: any
  comparator whose W2 mean monthly net has the opposite sign to life insurers'.
- **Q5. Sign of the rolling 12-month net.** The rolling 12-month sum of life insurers' net, from 2014-12. Report every month where it
  changes sign, the latest change to negative and whether it stayed negative through L, and the month and value of its minimum. No BoJ
  dates are printed beside it.
- **Q6. Fund shares beside long-term debt.** Life insurers' `equity_funds` net (monthb2: equities plus all investment-fund shares, no
  bond/equity split) in W1 and W2, printed beside the `ltd` net. No offset reading and no notable flag.

**Context is not an input.** The life insurers' hedge ratios (FX list F9) and the yen-hedged Treasury carry
(`data/hedged_ust_yield/yen_summary.csv`) appear in SOURCES.md only, as related material, with no number and no statistic joining them to
this series. No text may say insurers acquired or disposed of bonds because of the carry or the hedge ratio.

## 5. The October 2026 forecast (CALENDAR row 2026-11-10; registered 19 Oct, before the print)

- **Object.** The Net cell of life insurers' `ltd` (monthb3) for October 2026: net acquisition or net disposition, redemptions included. It
  is a frozen rule on this net, **not a forecast of sales**; the README and the `note` of every `forecast_score.csv` row say so (R3-1).
- **Rule (frozen):** the Net cells for the 24 months 2024-10 to 2026-09, sorted ascending; point = median (mean of the 12th and 13th);
  range = 3rd to 22nd order statistics. Registered values in file units: **point −782, low −2,886, high +746** (¥ billion −78.2, −288.6,
  +74.6). A print equal to an edge is inside.
- **Reproduction (C10, FAILED build if not exact):** from the 8 Oct vintage (or the pins), recompute and match all three integers. The code
  holds `REGISTERED = (-2886, -782, 746)`, and G12 parses the CALENDAR row text and requires equality.
- **Scoring.** The print is the October **Net cell**, never acquisition minus disposition.
  - `PENDING` while no cached monthb3 vintage has October published.
  - If a cached vintage with Final Update **2026-11-10** has October published, its row has `of_record = yes` and status `INSIDE`
    (−2,886 ≤ print ≤ 746), `BELOW` or `ABOVE`.
  - If the first cached vintage with October published has any other Final Update date (a late capture, for example after the 8 Dec
    release), status `LATE_VINTAGE`, `of_record = no`, print recorded, and the scoring is left to the supervisor.
  - Later vintages add rows with `of_record = no`; a revised October print is recorded, never re-scored.
- **Revised base months:** if the 10 Nov vintage revises any of the 24 base months, the band is recomputed on it as INFO
  (`band_recomputed_*`); the score of record still uses the registered band.
- The builder writes no outcome text and does not edit CALENDAR; the supervisor does.

## 6. Outputs

**Script `bin/jp_life_foreign_bonds.py`.** Modes: `fetch` (the only network mode), `build` (offline, byte-identical on re-run),
`selftest` (synthetic data, no network, under 20 s). Committed files in `data/jp_life_foreign_bonds/`; each opens with a `# source:` line
carrying the citation of 2.6, and its **header is the first line that does not start with `#`**. Each header is an exact allowlist held
twice: `ALLOW` in code and `SPEC_ALLOW`, typed separately from this section (G14). Amounts are integers in ¥100 million unless the column
says `_bn`.

- `monthly.csv`: `month, instrument, sector, acquisition_100m_yen, disposal_100m_yen, net_100m_yen, basis` (6,264 rows at the 8 Oct vintage)
- `annual.csv`: `period_type, period, basis, instrument, sector, months, acquisition_100m_yen, disposal_100m_yen, net_100m_yen,
  file_total_net_100m_yen, diff_100m_yen` (`period_type` ∈ {CY, FY, CY_YTD, FY_YTD}; `basis` as 3.4; file total blank for YTD)
- `boj_dates.csv`: `decision_date, effective_date, month, action, phrase, url, sha256`
- `questions.csv`: `run_label, question, window, instrument, sector, statistic, value, unit, denominator, notable`
- `forecast_score.csv`: `registered_on, target_month, vintage_final_update, vintage_sha256, point_100m_yen, low_100m_yen,
  high_100m_yen, print_100m_yen, status, of_record, band_recomputed_low, band_recomputed_point, band_recomputed_high, note`
  (`status` ∈ {PENDING, INSIDE, BELOW, ABOVE, LATE_VINTAGE})
- `vintages.csv`: `file, final_update, retrieved_utc, bytes, sha256, months_published, last_month`
- `revisions.csv`: `file, vintage_from, vintage_to, row_label, sector, field, old_value, new_value, kind` (`sector` ∈ the six committed
  sectors; `kind` ∈ {revised, new, removed})
- `checks.csv`: `check_id, description, expected, observed, status`; `pins.csv`: `source, series, pin_date, value, unit`; `fetch_log.csv`.
- `README.md` (generated; G15 scans it):
  1. Two plain opening sentences: "Japanese life insurers' monthly acquisitions and dispositions of foreign bonds issued with an original
     maturity of more than one year, as reported to the Ministry of Finance by designated major investors, with other investor types
     beside them." Then the required sentence.
  2. Coverage in one sentence: designated major investors only; narrower than balance-of-payments portfolio investment; released earlier.
  3. The annual table for life insurers from CY2014 (CY and FY, ¥ billion, with `basis`), and the forecast status with the sentence that
     the October rule is a frozen rule on this net, redemptions included, not a forecast of sales.
  4. Defined terms: acquisition; **disposition** ("sales, redemptions and other reductions in holdings (the file's term); redemptions of
     overseas government bonds are included, MoF FAQ A5"); net acquisition and net disposition; recorded at contract (execution date;
     redemptions on the redemption date); long-term debt; designated reporters; dealers (`fi_firms`) and their share of gross contracts;
     trust accounts; investment trusts (Note 4, BoJ FAQ No. 14); fiscal year. Neither trust accounts nor investment trusts are called
     pensions.
  5. Limits of section 0, the two breaks (2007, 2014) and the March 2024 note (2.3), in plain words.
  6. One real worked row: **March 2024, life insurers: 11,783 − 13,790 = −2,007** (¥100 million), with the note "MoF rounds each cell
     separately, so Net can differ from the subtraction by 1".
  7. Column dictionary.
  8. Provenance at the end: the citation and processing statement, the BoJ credit, the vintage list.
  The questions of section 4 appear in `questions.csv`, not as prose claims.
- `SOURCES.md`: each URL with licence and citation; the column provenance; the stale English-index sign banner (2.3); the related material
  of section 4 (F9 hedge ratios, the carry file) with no numbers; the press reference points of C14 with quotes of 15 words or fewer.

**Not committed:** raw CSVs and PDFs (cache), any `_FAILED/` output, either STOP file.

## 7. Selftests (synthetic fixtures only)

Each guard is mutated by the selftest itself, run on its named fixture, and **must FAIL**; a mutant under which the guard still passes is
a selftest failure. The unmutated guard must pass on the clean fixture.

| Guard | Protects | Mutants (each must make the guard FAIL) |
|---|---|---|
| G1 blocks by label | 2.2 NFKC exact match | fixture with the **real full-width raw strings** of 2.2 and blocks reordered: (a) fixed index 42 for `life`; (b) **substring match** (maps `Banks(Trust Accounts)` onto block 10 or 12, `Others` onto block 8); (c) no NFKC (block 1 and 4 not found); (d) "Final Update" read at column 18 on a b4-style fixture (column 19) |
| G2 month column | English month governs | fixture whose Japanese and English month cells **disagree** (`３月` beside `Apr`): the output must say April; the mutant reading the Japanese column changes the output |
| G3 year carry | year on January only | year not carried: February-December rows dropped or given year None |
| G4 missing marker | `-` and blank are missing | `-` read as 0 (pre-2014 central bank becomes 0 instead of blank) |
| G5 unpublished months | blank rows never enter anything | blank October read as 0 (the forecast fixture must say PENDING; the mutant says INSIDE); fixture with three trailing blank rows: W2 months must stay 31 and its mean unchanged |
| G6 sign | Net = Acq − Disp (≤1 from 2014, ≤4 before) | (a) fixture with pre-2014 nets on the old sign (plus = disposition): the mutated guard (identity check disabled or sign test inverted) must FAIL to flag it, so the selftest fails; (b) acquisition and disposition columns swapped |
| G7 total rows | CY/FY rows excluded from months | a `2005CY` row read as a month |
| G8 annual sums and YTD | CY Jan-Dec, FY Apr-Mar by start year; 3.4 YTD rule | FY taken as Jan-Dec; FY labelled by end year; a gap above 12 passes; FY_YTD at L = 2027-02 starting in April 2027 instead of April 2026; a `basis` other than `mixed_2013_2014` for FY2013 |
| G9 additivity | 3.2 tolerances | a one-column offset passes; cross-file gap of 5 in a non-committed sector passes; gap of 3 in a committed sector passes; files with different Final Update dates give FAIL instead of WARN |
| G10 band and rounding | order statistics, Fraction, half away from zero | 2nd/23rd used; window shifted one month either way; median of 23; float ¥bn (fixture where it changes the median by 1 unit); Python `round()` on a fixture value of −2.5 ¥100m (must print −0.3 ¥bn, not −0.2) |
| G11 scoring | Net cell, edges inclusive, ¥100m units | **net recomputed as acquisition minus disposition** (fixture: acq − disp = −2,887, Net cell −2,886: must be INSIDE); strict inequality (print −2,886 must be INSIDE); print in ¥bn against ¥100m edges (print −2,000 must be INSIDE) |
| G12 frozen registration | R7, section 5 | `REGISTERED` edited (−2,885); CALENDAR text not matched; band recomputed from a revising vintage and used for the score of record; a later vintage re-scoring October; **`of_record = yes` given to a vintage with Final Update 2026-12-08** (must be LATE_VINTAGE) |
| G13 vintages and revisions | 2.5 | a changed cell missed in a total row; blank→number labelled `revised`; an unchanged sha256 saved as a new vintage; a revision in `fi_firms` (not committed) written to `revisions.csv` |
| G14 allowlists | section 6 | an extra or renamed column (including `basis` missing from `annual.csv`); `ALLOW` drifting from `SPEC_ALLOW`; header taken from the `# source:` line |
| G15 wording | R5, section 0 words | `fx_rate_gap.CAUSAL_RX` extended with: because, due to, in response to, led to, prompted, pushed, as a result of, reaction, reflecting, amid, owing to, thanks to, on the back of, weighed, and `as\b.{0,40}\b(rose|fell|rising|falling)`; plus a separate ban on `\bsold\b` and `\bnet sales\b` in generated text (the disposition gloss "sales, redemptions and other reductions" must pass). Run over the README, SOURCES.md and every committed text field (`notable`, `note`, `phrase`, `description`, `observed`, `statistic`, `action`). The required sentence passes; it plus "because the hedged carry fell" fails; "as hedging costs rose" fails; a `note` saying "life insurers sold" fails |
| G16 fetch safety | R1-R3 | non-200 latches; redirect latches; 200 with a wrong title latches; non-allowlisted host (FRED, sec.gov) allowed; `@` in the UA; pacing under 2 s; 21 requests; **a BoJ failure writes STOP instead of STOP_BOJ, or STOP_BOJ blocks a MoF fetch or the scoring**; BoJ fetched before MoF; **a code path that deletes, renames or writes over either latch file** (the selftest scans its own source for remove/unlink/rename/replace/open-for-write on either path outside the latch writer) |
| G17 commit folder | section 6, leaks | a scratch copy of the committed folder with (a) a planted raw `monthb3.csv`, (b) a file not on the name list, (c) a raw PDF, (d) a `checks.csv` cell containing `/Users/`, (e) a `pins.csv` cell containing `/private/tmp`, (f) any committed file containing `@`: the guard must FAIL on each planted copy and pass on the clean folder |
| G18 windows | section 4 | W2 starting 2024-04 as primary; a pre-2014 month entering any window; a blank month counted (W2 = 34 instead of 31) |
| G19 shares | Q3 | a net ratio printed when the nets have opposite signs (fixture gives a negative share); a ratio above 1 printed instead of `exceeds_total`; the denominator taken from `other_financial` instead of `designated_reporters_total`; the dealer share missing |

## 8. Pinned checks (`checks.csv`; real data, 8 Oct vintage)

- **C01 vintage**: monthb3 8 Oct vintage sha256 and bytes as in 2.1; Final Update "October 8, 2026"; 261 published months, 2005-01 to
  2026-09; 2026-10 to 2026-12 blank; `monthly.csv` 6,264 rows.
- **C02 raw cells, life (¥100m, acquisition / disposition / net)**: 2026-09 5,487 / 8,374 / −2,886; 2024-03 11,783 / 13,790 / −2,007;
  2005-01 5,271 / 9,384 / −4,113; file cell 2022CY net −114,641; file cells 2025FY 95,993 / 108,098 / −12,105; 2025CY net cell −6,727
  (its 12 monthly Net cells sum to −6,726).
- **C03 comparators, 2026-09 (¥100m)**: designated-reporter total 494,609 / 508,869 / −14,260; banks (banking accounts) net −24,856;
  trust accounts 54,154 / 42,200 / 11,953; investment trusts net −2,001; non-life 0 / 5 / −5. These catch a block swap that additivity
  cannot.
- **C04 sign identity** (2.3): monthb3 post-2014 cells off by more than 1: 0 of 2,601; pre-2014: 17 of 1,404, max 4. Each file checked.
- **C05 additivity** (3.2): within monthb3, net: 2 / 1 / 1. Cross-file, all fields: 17 sectors max 4 (`other_financial` acquisition
  2007-01: 77,174 against 17,018 + 55,041 + 5,111; disposition 2010-03: 80,523 against 17,995 + 58,654 + 3,870); six committed sectors max
  1; net field alone max 3.
- **C06 annual**: max |sum of months − file cell| 7 (CY) and 6 (FY), all 17 sectors and fields, in `other_financial` (net alone 4 and 3).
- **C07 missing pattern**: `-` in exactly 324 cells (108 rows x 3 fields x 4 sectors: `central_bank`, `general_govt`, `banks_trust`,
  `trust_banks_trust`), 2005-01 to 2013-12; published from 2014-01; no other blank or `-` in a published month.
- **C08 BoJ**: 12 PDFs, sha256 prefixes as in 2.1. A mismatch writes STOP_BOJ and makes C08 FAIL; it does not stop the build.
- **C09 calendar text**: CALENDAR row 2026-11-10 contains `POINT -¥78.2bn; RANGE -¥288.6bn to +¥74.6bn`. PASS if present and matching;
  FAIL if present and different; **WARN if the row is absent** (moved or resolved after a recorded outcome).
- **C10 band** (FAILED build if not exact): the 24 base Net cells, 2024-10 to 2026-09, ¥100m:
  `746, −1970, −1964, −2128, −2163, −2501, −762, 5309, −46, −1993, 809, 326, −385, −649, −2543, 402, −6187, −6384, −802, 179, −413, −106, −1373, −2886`.
  Sorted: 3rd = −2,886 (2026-09), 12th and 13th = −802 and −762, median −782, 22nd = +746 (2024-10). Sum −27,484 (−¥2,748.4bn);
  2026-01..09 −17,570; 18 months of net disposition and 6 of net acquisition (CALENDAR corrected from 19, O-1).
- **C11 fixed output**: a second `build` leaves every sha256 unchanged.
- **C12 staleness (WARN)**: the end of the latest published month is more than **45 days** before the run date (a missed release).
- **C13 window statistics (computed by the second reviewer from the 8 Oct vintage before the build; re-derived by the spec author from the
  cached copy; ¥100m, one decimal, half away from zero).** PASS if the build reproduces each value on the 8 Oct vintage; on a later vintage
  the comparison is INFO and differences are listed.
  - Life net, W0 / W1 / W2 / W2b: sum +190,365 / −142,291 / −38,408 / −36,401; mean +3,172.8 / −2,371.5 / −1,239.0 / −1,213.4; median
    +1,937.5 / −815 / −1,237 / −1,019.5; months with net disposition 18 of 60 / 39 of 60 / 23 of 31 / 22 of 30.
  - Q1 flag: does not fire (W2 mean −1,239.0 is above W1 −2,371.5), while W2's median is lower and its share of net-disposition months
    higher (74.19% against 65.00%); this is why Q1 reports all three together.
  - Q2, W1→W2: Δ mean acquisitions −3,177.7; Δ mean dispositions −4,310.3; Δ mean net +1,132.5.
  - Q3, life share of gross contracts (acquisitions / dispositions): W0 4.98% / 3.96%; W1 2.92% / 3.57%; W2 2.06% / 2.38%. Dealer
    (`fi_firms`) share of acquisitions 62.9% / 63.5% / 63.9%. Total nets +444,594 / +390,290 / +83,347; net ratio W0 0.43, W1 and W2
    `opposite_sign`.
  - Q4: trust accounts are the opposite-sign comparator in W2 (mean +7,332.6).
  - Q5: one sign change, to negative at 2020-06 (−2,091), negative since; minimum −131,051 at 2023-02; latest (2026-09) −21,147.
  - Q6: life `equity_funds` net W1 +41,328, W2 +2,102.
- **C14 press reference points (INFO)**: 2022 life net: CY cell −114,641, monthly Net cells sum −114,640, against Nikkei (21 Feb 2023) "a
  bit over ¥11 trillion" for the year; December 2022 −22,466 against its December figure; November 2022 −19,269 against the Japan Times
  (8 Dec 2022) ¥1.9 trillion. Quotes in SOURCES.md only.
- **C15 pins against the cache (INFO)**: when C10 runs from the pins, the pins are diffed against the earliest cached monthb3 vintage and
  every difference is listed.

## 9. Success criteria (exact)

1. `python3 bin/jp_life_foreign_bonds.py selftest` prints G1-G19, every mutant making its guard FAIL, exit 0, no network.
2. `python3 bin/jp_life_foreign_bonds.py fetch`: at most 20 requests, MoF first, all logged, neither latch; on the first run 16 (4 CSVs,
   12 PDFs).
3. `python3 bin/jp_life_foreign_bonds.py build`: C01-C07, C10, C11 and C13 PASS on the 8 Oct vintage (after 10 Nov: against it if
   cached, otherwise C10 from the pins, C01 and C13 WARN or INFO, C15 listed); C08 PASS; C09 PASS or WARN; C12 PASS or WARN; C14 INFO;
   `monthly.csv` has 6,264 rows at the 8 Oct vintage; `forecast_score.csv` says PENDING before 10 Nov.
4. A second `build` is byte-identical (C11).
5. **After 10 Nov and before 8 Dec 2026 08:50 JST:** `fetch` then `build` caches the vintage with Final Update 2026-11-10, writes
   `revisions.csv` (possibly with zero `revised` rows, printed as "no revisions") and one `forecast_score.csv` row with `of_record = yes`
   and status INSIDE, BELOW or ABOVE. A capture after the deadline gives LATE_VINTAGE and is reported to the supervisor.
6. `bin/check.sh --all`: the existing ✓ guard lines, `✓ no killed claims found`, `✓ page clean`, M10 clean; read the ✓ lines.
7. **M16 (optional, warn-only, in `bin/check.sh`, after the M15 pattern):** `data/jp_life_foreign_bonds/` holds only the 12 committed names;
   exact headers (first non-`#` line); no `.csv` whose second line is a MoF title; no `/Users/`, `/private/tmp` or `@` in any committed
   file. On a scratch copy with a planted raw `monthb3.csv`, a renamed header, an extra file and a planted `/Users/` path it must print four
   ✗ lines.
8. A verifier re-derives by hand from the cached CSV: life insurers' 2025 calendar year, where the 12 monthly Net cells sum to −6,726 and the
   file's CY cell reads −6,727 (a rounding difference, inside tolerance); and the C10 median.
9. **README cold-reader test:** two fresh agents with no context (a non-specialist trustee and a fixed-income practitioner) read only the
   README and state what the series is and is not. The supervisor checks them against section 0. A reader who comes away with a causal
   claim, a reading of dispositions as sales, a US-only reading, or "pension funds" for trust accounts or investment trusts fails the
   README.

**Landing (builder):** `.gitignore` rule for `data/vintages/jp_life_foreign_bonds/` and `data/jp_life_foreign_bonds/_FAILED/`; a REPRODUCE.md
paragraph; proposed text (not an edit) for a CALENDAR row "monthly, the day after each MoF monthly release: `fetch`, `build`" and for the
capture deadline in row 2026-11-10; a HANDOVER row. The builder commits nothing; the supervisor verifies, edits CALENDAR (including the
"net disposition" rewording of row 2026-11-10, R3-1) and writes any findings text and the 10 Nov outcome.

## 10. OPEN questions

- **O-1 CLOSED (ruled):** CALENDAR row 2026-11-10 corrected to 18 of 24 months, old wording kept; reworded to "net disposition" when the
  spec is committed (R3-1).
- **O-2 CLOSED (ruled):** derived tables committed, raw vintages in the cache.
- **O-3 OPEN: bonds held through funds.** Since 2014 they sit in monthb2 with equities and all other fund shares; the file cannot separate
  them, and Q6 makes no offset reading. *Settles:* a life-insurer breakdown of fund holdings (BoJ Flow of Funds or company accounts), not in
  scope.
- **O-4 CLOSED:** classification is by residence of the issuer (2013 notice, weekly-table Note 2).
- **O-5 CLOSED (ruled):** the trust-account column is never called "pensions".
- **O-6 OPEN: pre-2014 tolerance.** Seventeen pre-2014 cells in monthb3 miss the sign identity by 2-4 units, against 0 after 2014. Rounding
  in the recompiled old series is the likely reason; the notice does not say. Section 4 starts in 2014.
- **O-7 OPEN: release-day timing.** The scoring run must start after 08:50 JST on 10 Nov (23:50 UTC on 9 Nov) and before 08:50 JST on 8 Dec.
  If MoF moves the release date, a vintage with another Final Update date is LATE_VINTAGE and the supervisor scores it.
- **O-8 CLOSED (R3-1):** 処分 (disposition) includes redemptions of overseas government bonds held by residents (MoF FAQ A5); purchases and
  sales are recorded on the execution date and redemptions on the redemption date (A6).
- **O-9 OPEN: other redemptions and their size.** FAQ A5 does not address redemptions of non-government bonds, and the file does not show
  how much of life insurers' dispositions are redemptions. *Settles:* an MoF statement, or a maturity profile of life insurers' foreign
  bonds; not in scope.
- **O-10 OPEN: what the investment-trust column holds.** Note 4 says it includes asset management companies; the BoJ classification that
  MoF cites (FAQ No. 14, relayed) also places other entities in that investor type. Whether that applies to this file is unsettled. The
  README names Note 4 and the BoJ FAQ and calls the column nothing else.

## Supervisor rulings, 19 Oct 2026 (before any data run)

- **O-1:** done - CALENDAR row 2026-11-10 now says 18 of 24 months were net sales, with the old wording kept; the rule, point and range are
  unchanged.
- **O-2:** the commit decision stands: derived tables with the PDL1.0 citation and a processing statement are committed; raw vintages stay in
  the gitignored cache (consistent with the other builds), and revisions.csv keeps old and new values.
- **O-5:** accepted - the trust-account column is never called "pensions".
## Supervisor rulings, round 2 (second review), 19 Oct 2026 — before any data run

All nine correctness findings and the wording fixes are accepted, with these rulings:

- **R2-1 Cross-file additivity:** tolerance 4 for the 17-sector check (observed maximum 4, `other_financial` acquisition 2007-01 and disposition 2010-03), 2 for the six committed sectors. Files are compared only when their Final Update dates match; otherwise WARN.
- **R2-2 Labels:** NFKC + whitespace strip, first non-empty ASCII-leading cell of header rows 7 and 8, exact equality. G1 fixtures use the real full-width strings and include a substring-match mutant.
- **R2-3 G2** becomes the Japanese/English month-disagreement fixture; the output follows the English column.
- **R2-4 Blank months** never enter a window: W2 = 31 months at the 8 Oct vintage, W2b = 30. Success criterion: `monthly.csv` has 6,264 rows at that vintage. The scored value is the Net cell, never acquisition minus disposition (G11 mutant at −2,887 vs −2,886).
- **R2-5 Scoring vintage:** `of_record = yes` only if Final Update = 2026-11-10; otherwise `LATE_VINTAGE`, print recorded, scoring left to the supervisor. Capture deadline before 8 Dec 2026 08:50 JST; the CALENDAR row says so.
- **R2-6 `basis` column** in `annual.csv` (`old_to_2013`, `new_from_2014`, `mixed_2013_2014`, `mixed_2007`); the README annual table starts at CY2014.
- **R2-7 Separate `STOP_BOJ`;** MoF CSVs fetched first; a BoJ latch never gates MoF fetching or scoring.
- **R2-8 C12** at 45 days; C09 WARN when the CALENDAR row is absent after a recorded outcome.
- **R2-9 Small points:** exact rational arithmetic, round half away from zero; FY_YTD defined for January to March; G6/G17 phrased as mutate-and-must-FAIL; pins diffed against the earliest cached vintage as INFO; success criterion 8 says the 12 monthly cells sum to −6,726 and the CY cell reads −6,727.
- **R2-10 Window statistics were computed by the second reviewer** from the 8 Oct vintage before the build. They are descriptive and pinned as checks; the Q1 flag rule is not changed (that would be post hoc). Q1 reports mean, median and share of negative months together and says W1 contains 2022 to 2023.
- **R2-11 Hedging wording:** hedge ratios and the carry file move to SOURCES.md; no BoJ markers beside Q5; Q5 renamed "Sign of the rolling 12-month net"; G15 regex extended (reflecting, amid, owing to, thanks to, on the back of, as … rose/fell, weighed) and run over every committed text field. Generated text says "net disposition" or "negative net", never "sold". New open question O-8: does 処分 include redemptions at maturity? Unresolved, and the README says so.
- **R2-12 Shares:** labelled "share of reported gross contracts (dealer-inclusive)"; README names the dealer share; net ratio only when |ratio| ≤ 1, else `exceeds_total`.
- **R2-13 Leak and paths:** `revisions.csv` restricted to the six committed sectors; G17 scans committed files for `/Users/`, `/private/tmp` and `@`; committed header = first non-`#` line. O-4 closed by the 27 Dec 2013 notice (residence of issuer).
- **R2-14 README:** "bonds issued with an original maturity of more than one year"; worked row 2024-03 (11,783 − 13,790 = −2,007) plus the rounding note; "disposition" glossed.
## Supervisor rulings, round 3 (Grok attack, g9), 19 Oct 2026 — before any data run

Grok's integers match the second review and the spec (September 2026 life 5,487 / 8,374 / −2,886; the 24 base nets; band −2,886 / −782 / +746).

- **R3-1 Redemptions are in disposition. O-8 is CLOSED.** The supervisor fetched MoF's English FAQ on 19 Oct. Its A5 says redemptions of overseas government bonds held by residents "are included in the disposition". A6 says purchases and sales are recorded on the execution date and redemptions on the redemption date. Redemptions of other bonds are not addressed. The README, Q1, Q2 and the forecast note therefore name the object "net acquisition / net disposition", and say that disposition includes redemptions of overseas government bonds (and may include others). They never say "sold" or "net sales". The registered October rule is unchanged: it is a frozen rule on this net, redemptions included, and the README says it is not a forecast of sales. The CALENDAR row's context "18 of 24 months of net sales" is reworded to "net disposition" when the spec is committed. This is a wording correction, not a rule change.
- **R3-2 Denominator name.** `all_residents` becomes `designated_reporters_total`. The README says the survey covers designated major investors only, is narrower than balance-of-payments portfolio investment, and is released earlier.
- **R3-3 Q6.** The sentence that fund-share flows "could offset" long-term debt sales is deleted. `monthb2` is equities plus all investment-fund shares, with no bond/equity split. Q6 prints the two series side by side with no offset reading.
- **R3-4 Labels.** `inv_trust` carries file Note 4 ("includes asset management companies"). The README points to BoJ FAQ No. 14 for the classification and does not call trust accounts or investment trusts "pensions".
- **R3-5 March 2024.** The windows stay as registered (W2 from 2024-03, W2b from 2024-04). The README says the 19 March 2024 decision took effect on 21 March, so March 2024 is mostly before it, and W2b leaves it out. W2 is not re-based: the second reviewer computed both before this ruling.
- **R3-6 Labels and sign.** Matched by R2-2 (NFKC folding). The file's own sign is used (CSV Note 2: plus = net acquisition, confirmed by the 2005 identity). The English index banner, which still says plus is net sales, is recorded in SOURCES.md as stale and is never coded.
- **R3-7 Reference points** become INFO checks: the 2022 calendar-year life net (−114,641 in the CY cell; monthly cells sum to −114,640) against Nikkei's "a bit over ¥11 trillion", December 2022 (−22,466), and November 2022 (−19,269) against the Japan Times' ¥1.9 trillion. Quotes go in SOURCES.md only, each under 15 words.
