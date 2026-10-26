# Spec: who held the 2026 IPOs at their first quarter-end after listing, from the SEC Form 13F data sets (spec author, 26 Oct 2026; rewritten after rounds 2 and 3)

*Item 2 of `_research/2026-10-26-Grok-G11-Scoping.md`, taken forward by the supervisor on 26 Oct. It extends `2026-09-14-I2-IPO-Allocation.md`
and `data/i2_ipo_allocation/`. House style follows `_research/2026-10-25-MMF-NonUS-Banks-Spec.md` and `_research/2026-10-23-H8-Foreign-Offices-Spec.md`.
Script `bin/ipo_13f_holders.py`, outputs `data/ipo_13f_holders/`, check.sh guard **M24**. The rulings at the end are the record; this body
applies them, and where round 3 differs from rounds 1 or 2, round 3 is applied (R3-1 reverses O-3 and R2-1's primary denominator).*

*"Observed" means seen by the spec author on 26 Oct 2026 between 05:43 and 05:46 UTC with the CLAUDE.md non-SEC User-Agent, one request
per URL, no redirect followed: 7 requests (section 2.7). **No sec.gov or data.sec.gov host was contacted;** the rewrite made no request.
"Relayed" means taken from a project file, a review, the rulings or general knowledge and not re-read at source. **What was seen of the
answer before any build:** the eleven hand-read 13F rows in `data/i2_ipo_allocation/i2_13F_sample_holdings.csv` (two pre-IPO SpaceX holders
at 171,826,745 and 120,801,820 shares), i2's 13G/13D rows and full-text filing counts; and, in the round-2 and round-3 rulings, the SpaceX
listed-class count at the first 10-Q (about 7.70bn) and third-party aggregate 13F sums for SPCX and CBRS at 30 Jun 2026 (R3-9). Those let a
reader estimate SpaceX's primary percentage, so SPCX is not blind. The build has computed nothing.*

## 0. Goal, and what the result can and cannot say

- **Record**, for each 2026-priced operating-company IPO in the project's deal list, the shares of the listed class reported on Form 13F at
  the first calendar quarter-end strictly after the pricing date, summed over all filers. Deal-level share counts lead every output (R3-3).
- **Set** each sum against the listed-class shares outstanding **at that quarter-end**, from the issuer's first 10-Q (R3-1); describe how
  concentrated the reported holdings are, which registration number filers declare, and how much is options.

**It can say** how many listed-class shares 13F filers reported at the quarter-end and what percentage of the quarter-end listed class that
is. The sums are MEASURED on a stated universe (13F filers, as filed); ratios and weights are IDENTITY given the inputs. Any holder-type
label is HYPOTHESIS and sits in a separate file (R3-8).

**It cannot say:**
- who was allocated shares in the offering, at what price or when a holder bought: 13F is a quarter-end holdings snapshot, and a holder may
  have bought on day two in the market, which raised the company nothing (I2's point, which stands);
- who holds the part of the listed class that 13F does not show. `100 − pct_of_listed` is not a holding category and is never described as
  one (R3-2): it mixes shares outside 13F, shares two managers both reported, confidential treatment and denominator error;
- whether a high `pct_of_listed` reflects the IPO at all: for SpaceX the IPO's 555,555,555 shares are about 7.2% of a listed class of about
  7.70bn, mostly pre-IPO stock converted at listing (round 2), so the measure says who held the listed class, not who took the IPO;
- why anyone held, or whether holdings moved a price. Flows and positions are never written as the cause of a price.

**Required README sentence 3 (the denial sentence, verbatim):** "Form 13F shows what each manager held at the quarter-end, not what it was
allocated in the offering or when or at what price it bought, so none of these figures is an IPO allocation."

## 1. Hard requirements

- **R1. No network at all.** The script makes no request and starts no process (G14 bans the modules and calls). Every SEC file and every
  first-trading date is supplied by the supervisor (2.6). **The builder never contacts sec.gov or data.sec.gov, and never sends an email
  address, a name, `SEC_UA` or `CLAUDE_CODE_USER_EMAIL` anywhere.** No FRED. Free public data only (E-005).
- **R2. Inputs and STOP.** `--zip-dir` points at the supervisor's folder of SEC 13F zips in the private Dropbox companion
  (`private/data/vintages/form13f_zips/`). If it holds a file named `STOP`, every mode except `selftest` prints `STOP present: <path>` and
  exits 2. **Only a person deletes a STOP file; no agent deletes, renames, truncates or overwrites one, the builder included** (G14). The
  script refuses a `--zip-dir` or `--cache` inside the repository.
- **R3. Cache outside the repository** (`--cache`, default `~/ipo13f_cache/`; this satisfies O-1's "gitignored cache" without a
  `.gitignore` rule): filtered rows, candidate lists, the stamp of method 2, and the two private reviewed tables (`cusip_map.csv`,
  `filer_review.csv`). Never committed. The raw zips hold signatory names, phone numbers and addresses; **the script never opens
  `SIGNATURE.tsv` and never reads an address, phone or signature column** (G12).
- **R4. No CUSIP, ISIN, FIGI or issuer fragment of one in any committed file** (O-1 ruled). Securities are named by ticker and issuer name.
- **R5. No CIK, no accession number and no personal identifier in any committed file** (R2-8). A filer appears only under a name that
  `filer_review.csv` marks `name_public = yes` (an organisation); otherwise `withheld`. i2 holder labels come only from reviewed public
  names; an i2 reporting person of type `IN` is `individual (withheld)`.
- **R6. Wording (G15).** No causal, flow, allocation, motive or residual-as-holder wording in README.md, except the one denial sentence.
- **R7. Code ownership.** `bin/ipo_13f_holders.py` is new, standard library only. It reads the zips, its cache, the supervisor's 10-Q,
  424B4 and Official List copies only through `deal_inputs.csv` and `cusip_map.csv`, and these committed files:
  `data/i2_ipo_allocation/i2_deal_master_summary.csv`, `i2_holders_13g_13d_full_detail.csv`, `i2_13F_sample_holdings.csv`,
  `_research/2026-09-12-I1b-cornerstones.csv`. No existing script changes, apart from the new warn-only `bin/check.sh` guard M24.
- **R8. Numbers.** Shares are parsed and summed as `decimal.Decimal` (R2-8); a non-integral value is kept and counted (C17). Money is
  Decimal. Ratios are computed unrounded and rounded at write time: `pct_*` 3 decimals, `*_ratio` 4, `*_usd` 2, `weight_pct_of_measured` 3.
  Every percentage column names its denominator, and every `summary.csv` row carries a `denominator` cell.
- **R9. Dates come from the data.** Quarter-ends, due dates and the vintage are computed from the pricing date, the filings' own
  `PERIODOFREPORT` and `FILING_DATE`, and the zip names. Vintage = the newest zip's window end, e.g. `13f_to_2026-08-31`. No output depends
  on the wall clock; `build` is byte-identical on re-run. The `# source:` line carries no retrieval date (R2-9).
- **R10. Post-registration fixes** go in SOURCES.md "Builder decisions" with the old value kept beside the new, never in the README.
- **R11. Readme first (O-6, O-7, R3-6, R3-7).** Before writing code that depends on a field name, an amendment value, a date format or a
  file-number prefix, the builder reads the supervisor's copy of the 2026 SEC 13F readme and records each definition in SOURCES.md.

## 2. Data

### 2.1 The deals (committed, observed)

`data/i2_ipo_allocation/i2_deal_master_summary.csv`: `ticker`, `issuer`, `ipo_date`, `base_proceeds_to_company_usd` (primary base proceeds
to the company; secondary sales excluded), `counts_toward_112bn_operating_co_total`. The eight 2026-priced `True` rows sum to
**111,941,660,492 USD** (the page's "about $112bn"); SpaceX **74,999,999,925**; without it **36,941,660,567**. Medline and Pershing Square
USA are out of scope on every path (O-2, R3-8).

**Dates (O-4, O-5, R2-1).** The builder reads each pricing date from the 424B4 and records it in `deal_inputs.csv`; the supervisor supplies
each first trading day with its free public source (exchange or company notice). Both go to `deals.csv`; any difference from the deal
master's `ipo_date` (for example Jersey Mike's: master 2026-07-31, i2 breadth file 2026-07-30) is noted in SOURCES.md. **The pricing date
drives `first_qe`: the first calendar quarter-end strictly after it.** On the master's dates:

| Ticker | pricing (master) | first_qe | Zip holding it | Status |
|---|---|---|---|---|
| CBRS, FRVO | 2026-05-13 | 2026-06-30 | 01jun2026-31aug2026 | measured |
| INIO | 2026-06-03 | 2026-06-30 | same | measured (weight 0: all shares sold by holders) |
| QNT | 2026-06-04 | 2026-06-30 | same | measured |
| SPCX | 2026-06-11 | 2026-06-30 | same | measured |
| BSP | 2026-06-30 | 2026-09-30 | 01sep2026-30nov2026 | awaiting_next_zip (priced on the quarter-end day) |
| SKHY | 2026-07-09 | 2026-09-30 | same | awaiting_next_zip |
| JMKE | 2026-07-31 | 2026-09-30 | same | awaiting_next_zip |

Five deals, **84,119,999,925 USD = 75.146% of 111,941,660,492**, can be measured now; without SpaceX **9,120,000,000 = 24.688% of
36,941,660,567**. SpaceX is **89.158%** of the measured proceeds (IDENTITY on the master).

### 2.2 The 13F data sets (supervisor fetches; layout relayed until R11)

- **Landing page** `https://www.sec.gov/data-research/sec-markets-data/form-13f-data-sets`. File names observed in the data.gov catalogue
  (`https://catalog.data.gov/dataset/form-13f-data-sets`, HTTP 200, 281,068 bytes): quarterly zips by **filing date**
  (`01jun2026-31aug2026_form13f.zip`), the newest under `/files/datastandardsinnovation/data/form-13f-data-sets/`, older ones under
  `/files/structureddata/data/form-13f-data-sets/`. Catalogue: "Dataset Last Updated September 14, 2026", accrual `R/P3M`, licence
  `https://www.usa.gov/government-copyright`, temporal end `2026-08-31`; the data are "presented without change from the as-filed
  submissions" and the SEC "cannot guarantee the accuracy of the data sets" (observed).
- **Fields used (relayed; R11 and C14 confirm them, all missing names reported together):** `SUBMISSION.tsv` `ACCESSION_NUMBER`,
  `FILING_DATE`, `SUBMISSIONTYPE` (13F-HR, 13F-HR/A, 13F-NT, 13F-NT/A), `CIK`, `PERIODOFREPORT`; `COVERPAGE.tsv` `ACCESSION_NUMBER`,
  `ISAMENDMENT`, `AMENDMENTTYPE` (RESTATEMENT, NEW HOLDINGS), `CONFDENIEDEXPIRED`, `REPORTTYPE`, `FILINGMANAGER_NAME` (cache only),
  `SECFILENUMBER`; `SUMMARYPAGE.tsv` `ACCESSION_NUMBER`, `ISCONFIDENTIALOMITTED`; `INFOTABLE.tsv` `ACCESSION_NUMBER`, `NAMEOFISSUER`,
  `TITLEOFCLASS`, `CUSIP`, `VALUE`, `SSHPRNAMT`, `SSHPRNAMTTYPE` (SH, PRN), `PUTCALL`, `INVESTMENTDISCRETION`, `OTHERMANAGER`. Dates like
  `30-JUN-2026` (relayed); the parser accepts only `DD-MON-YYYY` with an English month table (G6).
- **Units and signs, tested (R3-7).** `VALUE` is whole US dollars (the 2023 amendments; i2's SpaceX rows imply $170.86 a share). If the
  readme still says thousands, that is reported in SOURCES.md, never rescaled. `SSHPRNAMT` is shares for `SH`, shares underlying for an
  option row. 13F reports long positions only: no amount is negative, and a put is never subtracted from shares (G4).
- **Timing.** A 13F-HR is due 45 days after the quarter-end (relayed): **14 Aug 2026** for 30 Jun; 14 Nov 2026 is a Saturday, so
  **16 Nov 2026** for 30 Sep. The Jun-Aug zip holds on-time 30 Jun filings; later filings and amendments land in the Sep-Nov zip, **expected
  around mid-December 2026** (the Jun-Aug record was updated 14 Sep, two weeks after its window closed; not pre-announced).
- **Revisions.** Filings are never revised in place; later zips add amendments. `revisions.csv` is regenerated from all cached vintages.

### 2.3 Denominators (R3-1; supervisor fetches the documents, builder transcribes, supervisor checks)

`deal_inputs.csv` is hand-entered by the builder from the supervisor's local copies and committed (numbers, dates and quotes of at most 25
words; no CUSIP, CIK or accession; a document is named by form, issuer and filing date). Items:
- `qe_balance_sheet`: each common class outstanding **at the first quarter-end**, from the first 10-Q's balance sheet or statement of
  equity at the period end;
- `qe_cover`: each class on the 10-Q cover, with its as-of date in `asof`;
- `after_offering_base`: each class "outstanding after this offering", base case, from the 424B4's "The Offering";
- `ipo_shares_base`: shares sold in the offering, base (primary + secondary), from the 424B4 cover;
- `pricing_date` and `first_trade_date` (date in `asof`, `shares` blank; the second from the supervisor's source).

**Primary denominator `den_listed_10q_sh`:** the listed class's `qe_balance_sheet` if the 10-Q states one, else its `qe_cover`, with
`den_listed_10q_item` saying which and `den_listed_10q_asof` its date. **A deal without a filed 10-Q gets a blank `den_listed_10q_sh` and a
blank `pct_of_listed`; it is counted and named (C20) and never filled from the prospectus.** The variant `den_listed_prosp_sh` is the listed
class's `after_offering_base` and feeds `pct_of_listed_prosp` only. `den_all_classes_10q_sh` sums all common classes on the same 10-Q item.
`is_listed_class = yes` marks the class whose CUSIP is mapped. The supervisor verifies every row and sets **`DEAL_INPUTS_SHA256`**; `build`
exits 2 if the file differs.

**No class size is ever inferred from a 13D or 13G percentage (R3-0).** Rule 13d-3(d)(1)(i) puts each filer's own convertible shares in
both numerator and denominator, so those percentages do not give a class count. C18 compares typed share counts only.

**Dual-class issuers (SpaceX and every "Class A" issuer).** Only the listed class is a Section 13(f) security, so 13F reports the listed
class only. `pct_of_listed` is the measure; `pct_of_all_classes` is printed beside it and is never the measure. Pre-IPO shares converted
into the listed class sit inside the numerator; `ipo_shares_pct_of_listed` (= 100·ipo_shares_base/den_listed_10q_sh) is printed beside
`pct_of_listed` so the reader sees how small the IPO can be against the class (R2-3).

### 2.4 Holder information available, and what is not

- **13F has no holder-type field.** The only filer-declared classifier is `SECFILENUMBER`, used **only if the 2026 readme defines it as the
  regulatory file number** (R3-6); otherwise `reg_category.csv` is not produced and SOURCES.md says why. Prefixes are matched longest
  first: `801-` registered investment adviser, `802-` exempt reporting adviser, `8-` broker-dealer (meanings relayed until R11); any other
  prefix `other_prefix`; blank `none`, described in the README as "no number declared" (R2-13). It is a registration status, not an
  investor type.
- **Self-declared type exists only on Schedule 13G/13D** (`type_of_reporting_person`), for holders above 5%, already in i2.
- **Kinds are a hypothesis and leave the measured tables (R3-8).** The top 10 filers per deal get a `holder_kind` ∈ {asset_manager,
  hedge_fund, bank_broker, insurer, pension_endowment_sovereign, corporate_strategic, venture_or_pre_ipo, other}, `kind_basis` ∈ {13g_type,
  name_review}, reviewed by the supervisor, written only to `kind_hypothesis.csv`.
- **`sh_pre_ipo_flagged` (R2-3):** `sh_13f` of filers that `filer_review.csv` flags as pre-IPO holders (an i2 13G/13D note, or the filer's
  own public description). A floor on pre-IPO holdings inside 13F, and a hypothesis.
- **N-PORT is not used;** it would count registered funds twice (O-9).

### 2.5 Licence

SEC catalogue licence `https://www.usa.gov/government-copyright` (observed); the SEC FAQ says EDGAR filings are free to reuse (relayed
via Grok). Raw zips stay in the private companion (size; personal data in SIGNATURE and COVERPAGE). **CUSIP:** CUSIP Global Services'
licence-fee FAQ (observed, `https://www.cusip.com/services/license-fees.html`) allows collecting CGS data from public sources for
"non-commercial use, provided that the source of such information permitted the reproduction and use of such information"; the
repository's CC BY 4.0 would let others reuse a committed CUSIP commercially, hence R4 (ruled O-1). The reference figures of C19 are a
third party's published aggregates, used as two expected values in `checks.csv` only. `# source:` line: U.S. Securities and Exchange
Commission, "Form 13F Data Sets", <zip names>.

### 2.6 What the supervisor fetches or supplies (www.sec.gov only, `SEC_UA`, sequential, at least 1 s apart, GET only)

Any status other than 200 writes `form13f_zips/STOP` (five lines: status, utc_time, url_path, retry_after, body_head) and ends the fetch.
Store as published in `private/data/vintages/form13f_zips/` and `private/data/ipo_13f_holders/docs/`; one `private/MANIFEST.tsv` row "SEC
bulk Form 13F and issuer filings, kept out of git for size and personal data; derived statistics only". After the spec is committed:
1. `https://www.sec.gov/files/datastandardsinnovation/data/form-13f-data-sets/01jun2026-31aug2026_form13f.zip` (30 Jun holdings).
2. `https://www.sec.gov/files/structureddata/data/form-13f-data-sets/01mar2026-31may2026_form13f.zip` (31 Mar holdings, for C04).
3. `https://www.sec.gov/files/form_13f_readme.pdf` (R11).
4. The 424B4s: `https://www.sec.gov/Archives/edgar/data/1181412/000162828026042639/spaceexplorationtechnologi.htm` (SPCX),
   `https://www.sec.gov/Archives/edgar/data/2021728/000162828026035214/cerebras-424b4.htm` (CBRS),
   `https://www.sec.gov/Archives/edgar/data/2110105/000162828026041003/quantinuum-424b4.htm` (QNT),
   `https://www.sec.gov/Archives/edgar/data/1853868/000162828026034849/fervoenergy-424b4.htm` (FRVO),
   `https://www.sec.gov/Archives/edgar/data/2109150/000119312526256992/liberty_-_424b4.htm` (INIO).
5. The five issuers' first 10-Qs for the period ended 30 Jun 2026, from the EDGAR filing index (CIKs 1181412, 2021728, 2110105, 1853868,
   2109150). An issuer with no 10-Q is recorded as such; its primary percentage stays blank.
6. The SEC Official List of Section 13(f) Securities for the quarter ended 30 Jun 2026 (R3-4), the list governing the June reports; file
   name resolved on the SEC site.
7. First trading days of the eight deals, each with its free public source.
8. **For the September quarter (later):** the landing page from 7 Dec 2026 for `01sep2026-30nov2026_form13f.zip` (its folder may differ);
   the 424B4s of SKHY, JMKE, BSP (`.../2120882/000119312526299963/d32785d424b4.htm`, `.../2127043/000119312526326453/project_70_424b4.htm`,
   `.../2004711/000110465926079884/tm2613674-14_424b4.htm`, under `https://www.sec.gov/Archives/edgar/data/`); their first periodic reports;
   the Official List governing the September reports; SK hynix's ADS count (O-12, supervisor).

### 2.7 Requests made by the spec author (goes to SOURCES.md)

`catalog.data.gov/dataset/form-13f-data-sets` 200 (281,068 bytes). `www.cusip.com`: `/terms-of-use.html`, `/about/license-fees.html`,
`/robots.txt` each 303 to `/index.html` (not followed); `/index.html` 200 (94,800); `/services/license-fees.html` 200 (111,955).
`experience.cusip.com/license-fees-faq` 200 (924 bytes, a shell).

## 3. Method

1. **First scan** (mode `scan`, one zip per run): stream each TSV with `csv` (tab, `QUOTE_NONE`); keep SUBMISSION, COVERPAGE (named fields
   only), SUMMARYPAGE, and INFOTABLE rows whose `NAMEOFISSUER` matches a deal pattern or whose normalised CUSIP is a candidate. CUSIPs are
   normalised by stripping whitespace and upper-casing; a value not 9 characters long after that is listed, never padded (O-13). Patterns
   (literal, `re.I`): SPCX `SPACE\s*EXPLORATION|SPACEX`; CBRS `CEREBRAS`; QNT `QUANTINUUM`; FRVO `FERVO`; INIO `INNIO`; SKHY `SK\s*HYNIX`;
   JMKE `JERSEY\s*MIKE`; BSP `BENDING\s*SPOONS`. An accession seen in two zips is a FAIL (C11).
2. **Review** (mode `review`, writes to the cache only): (a) each distinct (ticker, CUSIP, NAMEOFISSUER, TITLEOFCLASS) with row and filer
   counts and check-digit validity; (b) rows with a candidate CUSIP and a non-matching name (C-059: a matching rule is a hypothesis);
   (c) the top 25 filers per deal by shares, with `SECFILENUMBER` prefix and any i2 name match. **No ratio to shares outstanding is printed.**
   The supervisor sets **`CUSIP_MAP_SHA256`** (one listed-class CUSIP per deal; evidence `official_list_2026q2` or `filer_consensus`;
   rejects listed with reasons, e.g. i2's "SK HYNIX INC KRW 5000.0" row, the Korean ordinary share). **Then a second `scan` runs with the map
   and stamps the cache with that hash; `build` refuses a cache whose stamp differs from the current `CUSIP_MAP_SHA256`** (R2-2).
3. **Reviewed tables:** `cusip_map.csv` (cache); `filer_review.csv` (cache: `cik, name, name_public, holder_kind, kind_basis, pre_ipo_flag,
   i2_holder_match, cornerstone_match`) → `FILER_REVIEW_SHA256`; `deal_inputs.csv` (committed) → `DEAL_INPUTS_SHA256`. `build` exits 2 on
   any missing or mismatched constant.
4. **One report per filer and quarter.** Per (CIK, PERIODOFREPORT): base = latest-filed 13F-HR original (several originals: latest wins,
   listed); a later `RESTATEMENT` replaces the base (latest wins); `NEW HOLDINGS` amendments filed after the base are added. **Orphans**
   (an amendment with no original in the zips read: a restatement becomes the base, a new-holdings amendment stands alone) and
   **duplicates** (two amendments with identical rows) are listed and counted (R2-5). A `NEW HOLDINGS` amendment repeating a CUSIP already
   in its base is flagged and counted in `n_new_holdings_repeat_cusip` (R3-8); its rows are still added under this rule (O-15). An unknown
   `AMENDMENTTYPE` is a FAIL listing all of them. 13F-NT carries no holdings. Ties break on accession.
5. **Numerator.** `sh_13f` = Σ `SSHPRNAMT` over consolidated rows with the mapped CUSIP, `SSHPRNAMTTYPE = SH`, blank `PUTCALL`; all
   discretion types. `sh_13f_sole` = the same over `INVESTMENTDISCRETION = SOLE` rows: a floor that no shared-discretion double report can
   inflate (R2-3). Calls and Puts go to `sh_calls` / `sh_puts` (shares underlying), never netted. `PRN` rows are excluded and counted.
   Rows with a blank `VALUE` count in the shares and are excluded from the implied price (`n_rows_value_blank`, R2-7).
   `sh_name_match_other_cusip` = shares in rows whose name matches the deal but whose CUSIP is not mapped (reported, not added; R2-2).
6. **Ratios.** `pct_of_listed` = 100·sh_13f/den_listed_10q_sh (blank if no 10-Q); `pct_of_listed_prosp` = 100·sh_13f/den_listed_prosp_sh;
   `pct_of_all_classes` = 100·sh_13f/den_all_classes_10q_sh; `ipo_shares_pct_of_listed` as 2.3; `pct_of_ipo_shares` = 100·sh_13f/
   ipo_shares_base (a memo that includes pre-IPO holders and can exceed 100). Implied price per filer = Σ`VALUE`/Σ`SSHPRNAMT` on its
   shares rows with a value; `median_implied_price_usd` over filers; `implied_to_offer_ratio` against the offer price.
7. **13D/13G holders without a 13F row (R3-2).** From i2's full-detail file, per reporting person on the issuer, the latest filing with an
   event date on or before the quarter-end; if `filer_review.csv` maps that person to no 13F filer with a row for the deal that quarter, its
   typed `shares_beneficially_owned` goes into `sh_13dg_holders_without_13f`. Typed counts only, never a percentage; a separate column,
   never added to `sh_13f` (O-17 on convertible shares).
8. **Pooled and weighted (R2-4, R3-3).** Pooled: Σ sh_13f / Σ den_listed_10q_sh over measured deals with a non-blank primary, with and
   without SpaceX. Weighted: `w_d` = primary base proceeds_d / Σ over measured deals (INNIO 0); `weighted_pct_of_listed` = Σ w_d ·
   pct_of_listed_d over deals with a non-blank primary, weights renormalised among them (O-16), with and without SpaceX; beside it the
   unweighted median and range of `pct_of_listed`. The weight identity Σ w_d = 1 is tested on unrounded Decimal weights (|Σ − 1| < 1e-12).
9. **Concentration.** Rank filers by `sh_13f` (ties by CIK, internally). `top1_pct_of_13f`, `top10_pct_of_13f`, `top10_pct_of_listed`.
   Filers are filer numbers, not manager groups (O-10 ruled; stated in the README).
10. **Overlap with i2.** Filers mapped to an i2 13G/13D reporting person on the same issuer: summed `sh_13f`; per holder the i2 shares,
    13F shares, gap and `has_13f_row`. Different legal tests; gaps reported, not reconciled (i2's Atreides: 10,543,836 against 3,810,086).
11. **Cornerstones (R2-12).** For FRVO now (SKHY later), from `_research/2026-09-12-I1b-cornerstones.csv`: the indicated interest, up to
    (a ceiling), in shares at the offer price (FRVO: 350,000,000/27 = 12,962,962.96 shares, aggregate across Atlas Point, Norges Bank,
    Wellington and Capital Research) against the mapped filers' `sh_13f`. Aggregate rows where no per-investor split is disclosed.
12. **Coverage.** Per quarter-end: 13F-HR and 13F-NT filers, filers with `ISCONFIDENTIALOMITTED = Y` (count and percent of 13F-HR filers),
    restatements, new-holdings amendments, repeats, orphans, duplicates, and reports filed after the due date.

## 4. Questions, fixed in advance (answers in `summary.csv` and the named files)

**No statistical test is run.** n is five deals now and eight after the next zip; comparisons across deals are descriptive; no MDE applies.

- **Q1. Coverage of the $112bn.** Measured and awaiting deals; measured proceeds as a share of 111,941,660,492 and, without SpaceX, of
  36,941,660,567; SpaceX's weight; deals with a blank primary, named.
- **Q2. Deal-level counts (lead).** `sh_13f`, `n_filers`, `sh_13f_sole`, `sh_pre_ipo_flagged`, `sh_13dg_holders_without_13f`; then
  `pct_of_listed` (primary, quarter-end), `pct_of_listed_prosp`, `pct_of_all_classes`, `ipo_shares_pct_of_listed`, `pct_of_ipo_shares`.
- **Q3. Pooled and weighted.** The pooled ratio with and without SpaceX; `weighted_pct_of_listed` with and without SpaceX, always stated
  with SpaceX's weight (89.158), INNIO's zero weight and the count of unmeasured deals; the unweighted median and range.
- **Q4. Concentration.** top-1 and top-10 shares of `sh_13f`; top-10 as a share of the quarter-end listed class.
- **Q5. Registration number.** `sh_13f` and filers by `reg_category` (if R3-6 allows it); the kinds in `kind_hypothesis.csv`.
- **Q6. Options.** `sh_calls` and `sh_puts` as percentages of `sh_13f` and of the listed class; filer counts.
- **Q7. The i2 holders.** Share of `sh_13f` held by filers that also filed a 13G/13D on the issuer; per-holder gaps.
- **Q8. Cornerstones.** Mapped cornerstone filers' `sh_13f` as a percentage of their indicated interest, up to.
- **Q9. What 13F cannot see.** The coverage counts of method 12 only. The gap to 100 is not described.
- **Q10. Revisions (next zip).** For each 30 Jun deal, `sh_13f` from the Jun-Aug zip against the same with the Sep-Nov zip added.
- **Q11. Reference check (R3-9, WARN).** C19.

### 4.1 Pre-registered statement for the next zip (S1 dropped by ruling O-8)

- **S2.** "Adding `01sep2026-30nov2026_form13f.zip` changes `sh_13f` at 2026-06-30 by less than 2% in absolute value for each of the five
  measured deals." It tests how far a first 13F vintage can be trusted; it cannot see holdings still under confidential treatment (R2-6). A
  failure is a result.
- **Registration rule:** S2 stands only if its CALENDAR row is committed before that zip appears on the SEC page (the supervisor records the
  page-check date). Proposed rows (text only): `2026-12-15` "13F IPO HOLDERS: check the SEC Form 13F data-sets page for
  01sep2026-30nov2026_form13f.zip; if posted, supervisor fetches it, builder runs scan/review/scan/build; score S2 (each 30 Jun deal's
  sh_13f moves less than 2% in absolute value); add the 30 Sep deals; else re-date one week"; and `2027-03-16` "13F IPO HOLDERS: Dec
  2026-Feb 2027 zip (late 30 Sep filings and amendments); rebuild and read revisions.csv".

## 5. Outputs

**Script `bin/ipo_13f_holders.py`.** Modes `selftest` (synthetic, under 30 s), `scan`, `review`, `build` (offline, byte-identical on
re-run). Committed files in `data/ipo_13f_holders/`; each CSV except `deal_inputs.csv` and `checks.csv` begins with one `# source:` line.

**Header allowlist, canonical text** (one line per file, LF-terminated, in this order). The script holds `SPEC_ALLOW_SHA256`;
**`bin/check.sh` holds its own literal copy of these thirteen lines** and never reads them from the script. Guards skip `# source:`.

```
deal_inputs.csv:ticker,class_label,is_listed_class,item,shares,asof,doc_form,doc_filing_date,doc_section,quote
deals.csv:ticker,issuer,pricing_date,first_trade_date,first_trade_source,in_112bn,proceeds_usd,weight_pct_of_measured,offer_price_usd,ipo_shares_base,first_qe,status,den_listed_10q_sh,den_listed_10q_item,den_listed_10q_asof,den_listed_prosp_sh,den_all_classes_10q_sh,vintage
holdings.csv:ticker,quarter_end,n_filers,sh_13f,sh_13f_sole,sh_pre_ipo_flagged,sh_13dg_holders_without_13f,pct_of_listed,pct_of_listed_prosp,pct_of_all_classes,ipo_shares_pct_of_listed,pct_of_ipo_shares,top1_pct_of_13f,top10_pct_of_13f,top10_pct_of_listed,sh_calls,sh_puts,n_filers_calls,n_filers_puts,sh_name_match_other_cusip,median_implied_price_usd,implied_to_offer_ratio,n_rows_value_blank,vintage
reg_category.csv:ticker,quarter_end,reg_category,n_filers,sh_13f,pct_of_13f,pct_of_listed,vintage
top_filers.csv:ticker,quarter_end,rank,filer_label,filed_13g_13d,sh_13f,pct_of_13f,pct_of_listed,vintage
kind_hypothesis.csv:ticker,quarter_end,rank,filer_label,holder_kind,kind_basis,vintage
overlap_i2.csv:ticker,quarter_end,i2_holder_label,i2_form,i2_type,i2_event_date,i2_shares,has_13f_row,sh_13f_matched,gap_sh,vintage
cornerstones.csv:ticker,cornerstone_label,indicated_usd_up_to,offer_price_usd,indicated_sh_up_to_at_offer,quarter_end,n_mapped_filers,sh_13f_mapped,pct_of_indicated_up_to,vintage
coverage.csv:quarter_end,zip_name,n_hr_filers,n_nt_filers,n_conf_omitted,pct_conf_omitted_of_hr,n_restatements,n_new_holdings,n_new_holdings_repeat_cusip,n_amend_orphans,n_amend_duplicates,n_filed_after_due,vintage
summary.csv:question,scope,ticker,quarter_end,statistic,value,unit,denominator,vintage
revisions.csv:vintage_prev,vintage_new,ticker,quarter_end,sh_13f_prev,sh_13f_new,change_sh,change_pct_of_prev
zips.csv:zip_name,window_start,window_end,bytes,sha256,n_submissions,n_infotable_rows,role,vintage
checks.csv:check_id,description,expected,observed,status
```

**sha256 of that text (1,958 bytes): `ee8cb56e1611e5586421bc59d7b2a87766937889bfb386d862f89a69323c8b65`** (computed by the spec author; superseded
hash `35aa6035dca6850ce021756a98a3a4556f6889456a4908585ecc6e6ab177db50`). A builder who needs a column changes this text and its hash first,
logs it in Builder decisions, and tells the supervisor.

**Allowed values.** `status` ∈ {measured, awaiting_next_zip}; `item` ∈ {qe_balance_sheet, qe_cover, after_offering_base, ipo_shares_base,
pricing_date, first_trade_date}; `den_listed_10q_item` ∈ {qe_balance_sheet, qe_cover, blank}; `reg_category` ∈ {ria_801, era_802, bd_8,
other_prefix, none}; `holder_kind` as 2.4; `kind_basis` ∈ {13g_type, name_review}; `role` ∈ {first_qe, pre_listing_control}; `scope` ∈
{deal, measured_all, measured_ex_spcx}; `unit` ∈ {shares, pct, usd, ratio, count}; `in_112bn`, `is_listed_class`, `filed_13g_13d`,
`has_13f_row` ∈ {yes, no}. A blank primary is an empty cell, never 0. Duplicate keys in any file are a FAIL.

- **`README.md`** (generated; G15 scans it), in this order, each technical term glossed in one line where first used (R2):
  1. **Opening, two sentences, verbatim:** "This table counts the shares of the eight US IPOs of 2026 that raised about $1bn or more, set out
     in the deal list, that investment managers reported holding on Form 13F at the first calendar quarter-end after each listing. Form 13F
     is the quarterly holdings report that managers with at least $100 million in US-listed stocks file with the Securities and Exchange
     Commission, and each count is set against the shares the company had outstanding at that same quarter-end."
  2. Sentence 3, the denial sentence (section 0), then verbatim: "The part of the listed class not counted here is not a group of holders,
     and this table does not say who holds it." (R3-2)
  3. Which deals are measured and which wait for the December zip, with the permitted deadline wording "managers must file within 45 days
     of the quarter-end"; deals with no 10-Q named, with "no percentage is shown because the company had not filed a quarterly report".
  4. **Deal-level share counts first** (R3-3); then `pct_of_listed` with `ipo_shares_pct_of_listed` beside it and the sentence, verbatim: "A
     high percentage can consist mostly of shares held by investors who owned the company before it listed." (R2-3); the pooled ratio; any
     weighted figure only in a sentence that also gives SpaceX's weight, INNIO's zero weight and the number of deals not yet measured.
  5. Concentration (by filer number, not manager group); registration numbers ("no number declared" for `none`; not an investor type);
     options; i2 overlap; cornerstones in the permitted wording "investors the prospectus named as having indicated an interest in buying up
     to $X of shares (a ceiling)"; coverage counts. Kinds appear only as "kind, judged by the builder from public descriptions (a hypothesis)".
  6. Dual class in plain words; the column dictionary; identifiers (tickers only; one sentence on why no CUSIP); the SEC citation. No
     question labels, no build decisions, no description of the gap to 100.
- **`SOURCES.md`:** every URL with access date and status (2.6, 2.7); the readme definitions as read (R11), including what it says about
  `VALUE` units and `SECFILENUMBER`; the deal patterns; the three gate hashes, review dates and the cache stamp; the CGS quote; the
  disclosure paragraph of this spec's header; the pricing and first-trading dates against the deal master; and **Builder decisions** (CUSIP
  rejects by reason without the CUSIP, new labels, the Cerebras price-split resolution, every post-registration fix with old and new values).

## 6. Leak and integrity rules (R2-8)

1. Committed: only the thirteen CSVs, README.md and SOURCES.md. No `.tsv`, `.zip`, `.htm`, `.pdf`; no column named like `cusip`, `isin`,
   `figi`, `cik` or `accession`.
2. No CUSIP-shaped token (8 alphanumerics with at least one letter, then a valid check digit) in any file; in README.md and SOURCES.md also
   no bare 9-digit token with a valid check digit (numbers in prose are comma-grouped); in CSVs the all-digit test applies to every column
   except share, count, money and date columns. No ISIN shape `[A-Z]{2}[0-9A-Z]{9}[0-9]`, no FIGI shape `BBG[0-9A-Z]{9}`. When the cache map
   is present: no mapped CUSIP, its first 8 characters or its 6-character issuer prefix anywhere.
3. No accession shape `\d{10}-\d{2}-\d{6}`; no CIK (a 1-10 digit number in a filer column, or a filer's CIK from the cache anywhere); no
   filer name unless `name_public = yes`; no i2 holder of type `IN` named; no local path (`/Users/`, `/private/`, `~`); no `@`.
4. Nothing is written outside `data/ipo_13f_holders/` and the cache, apart from a REPRODUCE.md paragraph at landing.

## 7. Selftests (synthetic only; each guard applies its own mutant, and an uncaught mutant fails the selftest)

**G15's literal patterns, all compiled with `re.I`** (pasted into the script and into check.sh, not imported). `CAUSAL_RX`:

```
\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of)\b
```

`EXTRA_RX`:

```
\b(?:in|out)?flows?\b|\ballocat(?:e|ed|es|ing|ion|ions)\b|\b(?:ipo\s+)?buyers?\b|\bbought\b|\bpurchas(?:e|ed|es|ing)\b|\bdemand\b|\bappetite\b|\bsmart\s+money\b|\bpiled?\s+in(?:to)?\b|\bsnapped\s+up\b|\bdump(?:ed|ing|s)?\b|\bretail\b|\bunderpric(?:e|ed|ing)\b
```

`RESIDUAL_RX` (R3-2):

```
\b(?:rest|remainder|remaining|residual|balance)\b[^.]{0,80}\b(?:held|holds|owned|owns|belongs?|retail|insiders?|non-?filers?)\b
```

Synthetic CUSIP fixtures (valid check digits, not real securities): `TSTA01102`, `TSTB02108`, `ZZZZZZ104`.

| Guard | Protects | Mutant that must be caught |
|---|---|---|
| G1 amendments | 3.4 | an amendment summed with its original; a `NEW HOLDINGS` dropped; an older `RESTATEMENT` beating a newer one; a `NEW HOLDINGS` filed before the latest restatement kept; two originals both counted; an orphan dropped or not listed; a duplicate amendment counted twice; a repeated CUSIP in a `NEW HOLDINGS` not flagged; an unknown `AMENDMENTTYPE` accepted |
| G2 numerator | 3.5 | a Put or Call counted as shares; a `PRN` row counted; a name-match row with an unmapped CUSIP added to `sh_13f` (it belongs in `sh_name_match_other_cusip`); another period counted; a blank-`VALUE` row dropped from shares or used in the implied price; `sh_13f_sole` > `sh_13f`; shares parsed as float |
| G3 CUSIP | 3.1-3.2 | `tsta01102 ` not normalised; an 8-character value padded; `TSTA01103` (bad check digit) accepted; a name match used without the map; `build` on a cache stamped with an old map hash; a mapped CUSIP with a non-matching name not listed |
| G4 signs and units | 2.2 | a negative `SSHPRNAMT` or `VALUE` accepted; `VALUE` rescaled to thousands (also when a fixture readme says thousands); puts subtracted from shares; a filer 2% off the deal's median implied price not listed; a deal median outside 0.2-5× the offer price not failing |
| G5 quarter-ends | 2.1 | pricing 2026-06-30 → 2026-06-30 (must be 2026-09-30); 2026-05-13 → anything but 2026-06-30; `first_trade_date` used instead of the pricing date; due date for 2026-09-30 not 2026-11-16 |
| G6 dates | R9 | `30-JUN-2026` parsed under a locale; day-first misread; a wall-clock vintage or `# source:` date; a vintage not equal to the newest zip's window end |
| G7 denominators | 2.3 | the prospectus count used for `pct_of_listed`; a blank primary filled from the prospectus or written as 0; `qe_cover` used when `qe_balance_sheet` exists; all classes used as the listed class; a class size inferred from a 13D/13G percentage; `build` with `DEAL_INPUTS_SHA256` mismatched |
| G8 pooled and weights | 3.8 | INNIO given weight; a blank-primary deal in the pooled or weighted figure; weights tested after rounding; the ex-SpaceX rows including SPCX; median or range missing beside a weighted figure |
| G9 identities | 3.9, C16 | `reg_category` not summing to `sh_13f`; top-10 < top-1; unstable tie order |
| G10 duplicates | C09 | two CIKs with identical (CUSIP, shares ≥ 10,000) at one period not flagged |
| G11 cross-zip | C11 | one accession in two zips accepted; `revisions.csv` appended rather than regenerated |
| G12 personal data | R3, R5 | `SIGNATURE.tsv` opened (AST string scan and runtime open-hook); an address column read; an unreviewed filer name, any CIK or accession written; an `IN` holder named; an i2 label not from a reviewed public name |
| G13 | — | moved to the supervisor hash step, success criterion 6 (R2-10) |
| G14 network, STOP, paths | R1-R2 | an import of `urllib`, `urllib3`, `http`, `httpx`, `aiohttp`, `requests`, `socket`, `ssl`, `ftplib`, `webbrowser`, `subprocess` or `pty`, or a call to `os.system`, `os.popen` or `os.exec*`; any `os.remove`, `os.unlink`, `os.rename`, `os.replace`, `os.truncate`, `shutil.rmtree`, `shutil.move`, `shutil.copy*`, `Path.unlink`, `Path.rename`, `Path.replace`, `Path.touch`, `Path.write_*` or write-mode `open` reaching a path named `STOP` (AST scan); **runtime: with a planted `STOP`, `scan`, `review` and `build` each exit 2 and its sha256 is unchanged**; a cache or zip folder inside the repo accepted |
| G15 wording | R6 | README with the opening, the denial sentence and the two other verbatim sentences passes; "IPO buyers piled in" fails; "demand for SpaceX drove the price" fails; "funds were allocated 20%" outside the denial sentence fails; "retail held the rest" fails; "the remaining 52% is held by non-filers" fails; a heading "Builder decisions" in README fails |
| G16 leak guard | 6 | **on a planted bad folder:** a CSV with `TSTA01102`; README prose with `999999105`; an ISIN shape; a `BBG` shape; an accession shape; a CSV column `cik`; a `.tsv` file; a `/Users/` path; an unreviewed filer name; each reported; **on the clean folder it passes**, and a share count `171826745` in an `sh_` column does not trip it |
| G17 registration number | 2.4 | `8-` matched before `801-`; `reg_category.csv` written when the readme flag says the column is not the regulatory file number |

## 8. Pinned checks (`checks.csv`; no CIK or accession is written there, pins are named by i2 sample row)

- **C01 Deal master (IDENTITY, FAIL):** eight 2026 `True` rows = 111,941,660,492; measured {SPCX, CBRS, QNT, FRVO, INIO} = 84,119,999,925
  (75.146%); ex-SpaceX 9,120,000,000 of 36,941,660,567 (24.688%); `weight_pct_of_measured` SPCX 89.158, CBRS 6.598, FRVO 2.247, QNT 1.997,
  INIO 0.000; ex-SpaceX CBRS 60.855, FRVO 20.724, QNT 18.421.
- **C02 Accession pins (FAIL; relayed from `i2_13F_sample_holdings.csv`; listed here by accession, written to `checks.csv` by row number):**
  the accession's own shares rows for the mapped CUSIP, before consolidation: SPCX `0001140361-26-032507` 171,826,745 (VALUE 29,358,317,651),
  `0001104659-26-096768` 120,801,820 (VALUE 20,640,198,965); CBRS `0000919574-26-005478` 7,011,028, `0000904454-26-000433` 145,700 (VALUE
  16,340,805), `0001777813-26-000009` 3,810,086, `0001193125-26-352454` 794,467 (VALUE 175,577,207); QNT `0000919574-26-005126` 145,071; FRVO
  `0001420506-26-001756` 20,000 (VALUE 584,600). **The Cerebras implied prices disagree (112.15 against 221.00); the builder reads both
  filers' rows in the zip and records the resolution in Builder decisions before `build`; the Cerebras pins may FAIL until then** (R2-7).
  Any other mismatch goes to the supervisor with both values and is not "fixed" in code.
- **C03 Units:** SPCX row 1's VALUE/SSHPRNAMT = 170.86 (FAIL); each deal's median implied price within 0.2-5× the offer price (FAIL);
  filers more than 1% from their deal's median implied price listed (WARN, R2-7; O-14).
- **C04 Pre-listing rows (WARN, R3-5):** rows of a mapped CUSIP with `PERIODOFREPORT` before the pricing date, in any zip read, listed.
  Neither this check nor C07 changes a CUSIP or a denominator.
- **C05 Name and CUSIP (WARN):** mapped CUSIP with non-matching name, listed; `sh_name_match_other_cusip` above 1% of `sh_13f` (R2-2).
- **C06 Check digits (FAIL):** every mapped CUSIP valid. **C07 Bounds (WARN, R3-5):** `pct_of_listed` or `top10_pct_of_13f` above 100, listed.
- **C08 BSP at 30 Jun (WARN):** count of 2026-06-30 rows of BSP's CUSIP; they enter no measure.
- **C09 Duplicate suspects (WARN):** CIK pairs with identical shares ≥ 10,000 of one CUSIP at one period, listed by rank, not removed.
- **C10 Amendment anomalies (WARN, listed):** several originals, orphans, duplicates, repeated CUSIPs in new-holdings amendments.
- **C11 Accessions unique across zips (FAIL).** **C12 Fixed output:** a second build leaves every sha256 unchanged.
- **C13 Gates (FAIL):** the three constants match and the cache stamp equals `CUSIP_MAP_SHA256`, with review dates in Builder decisions.
- **C14 Headers and readme (FAIL):** every field of 2.2 present (all missing names listed); the readme definitions of R11 recorded.
- **C15 Coverage (INFO):** 13F-HR filers per period. **C17 Excluded rows (INFO):** PRN, option, blank-VALUE, non-integral rows per deal.
- **C16 Identities (FAIL):** Σ `reg_category.sh_13f` = `holdings.sh_13f`; Σ top-10 ≤ `sh_13f`; `sh_13f_sole` ≤ `sh_13f`; unrounded weights
  sum to 1 within 1e-12.
- **C18 Typed counts (WARN):** the listed class's quarter-end 10-Q count against its prospectus `after_offering_base`; gap over 15% listed.
  Typed share counts only (R3-0).
- **C19 Reference aggregates (WARN, R3-9):** `sh_13f` at 2026-06-30 within 2% of SPCX **3,685,578,550** and CBRS **88,744,964**
  (PortfolioSavvy, 30 Jun 2026, relayed from the round-3 ruling). A miss is reported with its likely cause (amendments after the zip
  cut-off; option rows); nothing is tuned to meet it.
- **C20 Blank primary (INFO):** count and tickers of measured deals with no 10-Q. **C21 Official List (WARN):** each mapped CUSIP appears in
  the Official List for the quarter ended 30 Jun 2026 (R3-4); the supervisor's reading is recorded in `cusip_map.csv` evidence.

## 9. Success criteria

1. `python3 bin/ipo_13f_holders.py selftest` prints G1-G12 and G14-G17 with every mutant caught and exits 0.
2. `scan`, `review`, the supervisor's CUSIP map, the second `scan`, and the filer and deal-input reviews run with no network. If a STOP is
   present, the builder stops and reports; it never deletes it.
3. `build`: C01, C02 (Cerebras pins excepted until resolved), C03's FAIL parts, C06, C11-C14 and C16 PASS. Acceptable WARNs: C03 outliers,
   C04, C05, C07, C08, C09, C10, C18, C19, C21, each with its list in SOURCES.md. Every other WARN goes to the supervisor.
4. **A verifier re-derives FRVO and SPCX by hand** (R2-11) from the Jun-Aug zip with an independent script (INFOTABLE filtered by the mapped
   CUSIP, `SH`, blank `PUTCALL`, joined to SUBMISSION, `PERIODOFREPORT = 30-JUN-2026`): the raw sum before consolidation, the difference to
   `sh_13f` explained accession by accession, then `pct_of_listed` from `deal_inputs.csv`. The verifier also checks both mapped CUSIPs
   against the SEC Official List for the quarter ended 30 Jun 2026.
5. **M24** (warn-only, in `bin/check.sh --all`), with its own literal copy of the thirteen header lines: file names; headers; no raw file,
   local path, `@`, forbidden column, CUSIP, ISIN, FIGI or accession shape; no G15 pattern in README.md outside the denial sentence;
   `reg_category` sums to `holdings.sh_13f` per deal (✗ if not); `pct_of_listed` above 100 (⚠); no duplicate key. **On a scratch copy with
   a planted `TSTA01102` in a CSV, a renamed header, a `reg_category` row inflated by 1,000 shares and the README sentence "IPO buyers piled
   in", M24 prints four ✗ lines; on the clean folder, ✓.** Shown failing on the planted copy before it lands.
6. **Supervisor hash step (absorbs G13, R2-10):** extract the allowlist block from this spec, take its sha256, and compare it with
   `SPEC_ALLOW_SHA256` in the script and with the sha256 of check.sh's literal block; all three equal
   `ee8cb56e1611e5586421bc59d7b2a87766937889bfb386d862f89a69323c8b65`. Then run `build` on a copy with one extra column and one renamed column
   in a CSV, and confirm both are refused.
7. **README cold-reader test.** A non-specialist and an equity capital-markets practitioner read only the README. **Pass** only if each can
   state that the figures are quarter-end holdings by 13F filers, that they are not allocations, which deals are missing and why, that a
   high percentage can be mostly pre-IPO holders, and that the uncounted part is not a group of holders. **Fail** if either believes the
   table shows who received IPO shares, that a holding moved the price, that a kind is filed by the manager, or that the uncounted part is
   retail or any other named group.

**Landing (builder):** a REPRODUCE.md paragraph (supervisor fetches, `--zip-dir`, modes, gates, the second scan); the two proposed CALENDAR
rows as text only, under 4.1's rule; a HANDOVER row. The builder commits nothing; the supervisor verifies, writes any findings text, and
changes the page sentence "Who was allocated the shares is not recoverable on free data" only if the result warrants it.

## 10. OPEN questions

Ruled and closed: O-1 to O-12 (see the rulings). Open after the rewrite:
- **O-12 SK hynix ADSs** (September quarter): the supervisor supplies the ADS count; whether a quarter-end count exists is unknown.
- **O-13 CUSIP normalisation (R2-2).** Applied as strip and upper-case, with wrong-length values listed and never padded. If the reviewer
  meant more (for example restoring dropped leading zeros), the supervisor says so.
- **O-14 The ±1% implied-price check (R2-7).** Applied as each filer against its deal's median implied price. The reviewer's reference
  point is not in the rulings.
- **O-15 Repeated CUSIPs in `NEW HOLDINGS` (R3-8).** "Flagged and counted" is applied as counted in `coverage.csv`, with the rows still
  added. The alternative is to exclude them from `sh_13f`.
- **O-16 Blank primary in pooled and weighted figures.** Applied as excluded, with weights renormalised among the rest and the excluded
  deals named. The alternative is to print no weighted figure while any measured deal lacks a 10-Q.
- **O-17 `sh_13dg_holders_without_13f` (R3-2).** A 13D/13G typed count is beneficial ownership and may include unlisted shares
  convertible into the listed class, so the column can exceed the holder's listed-class shares. Which i2 filings count (latest event date on
  or before the quarter-end) is the spec author's rule. i2's file holds filings found by 14 Sep only.
- **O-18 R2-5 to R2-13 "as the reviewer wrote them".** The reviewer's text is not in this file; the body applies the rulings' summaries.
  The supervisor should check them against the review.
- **O-19 `pct_of_ipo_shares`** is kept as a memo (no ruling removed it); it exceeds 100 wherever pre-IPO holders file 13F.
- **O-20 The round-1 placeholder heading** "Supervisor rulings ... (none yet ...)" below is stale; left unchanged because the ruling sections
  are the record.

## Supervisor rulings

*(appended below by the supervisor, newest last, all before any data run)*

## Supervisor rulings, 26 Oct 2026 (before any data run)

- **O-1:** CUSIPs are NOT committed; outputs carry tickers and issuer names only. The CUSIP map stays in the gitignored cache.
- **O-2:** Medline is left out (no memo deal, no extra zip).
- **O-3:** the primary denominator is the prospectus post-offering listed-class count for every deal (one consistent basis); the first-10-Q count is printed beside it as a variant.
- **O-4:** "strictly after pricing" stands; BSP moves to the September quarter.
- **O-5:** the builder takes each listing date from the 424B4 and the first trading day reported by the exchange or the company, records both, and the deal master's discrepancy is noted in SOURCES.md.
- **O-6 / O-7:** the builder verifies field names, amendment values, date formats and file-number prefixes against the SEC's 13F readme before writing code that depends on them.
- **O-8:** S1 is dropped (with five June deals the range is likely wide enough to make it near-certain). S2 (late filings and amendments move the June figures by less than 2%) stands, scored on the Sep–Nov 2026 zip.
- **O-9 / O-10:** N-PORT stays out; the top-10 is by filer number, stated.
- **O-11 / O-12:** the supervisor resolves the Official List file name and SK hynix's ADS count when the September-quarter files are fetched.
- **Guard number:** **M24**. The supervisor fetches the SEC files (items 1, 2, 4, 6–10 and the five issuers' first 10-Qs) after the spec is committed.
## Supervisor rulings, round 2 (second review), 26 Oct 2026 — before any data run

All thirteen fixes are accepted. The load-bearing one: for SpaceX the listed class (about 7.70bn Class A shares at the first 10-Q) is mostly pre-IPO stock converted at listing; the IPO's 555.6m shares are about 7.2% of it, and two pre-IPO funds alone hold 292.6m shares (52.7% of the IPO shares). So `pct_of_listed` measures who held the listed class, not who bought the IPO.
- **R2-1** The body, columns and guards are rewritten to the round-1 rulings: prospectus `after_offering_base` count primary, 10-Q variant in `den_listed_10q_sh`, `den_listed_10q_asof`, `pct_of_listed_10q`; `weight_pct_of_measured`; Medline and S1 removed everywhere; the cache lives outside the repo (as R3 and 6.3 say); the supervisor supplies first-trading dates, and the pricing date drives `first_qe`. New allowlist block and hash in three places.
- **R2-2** A second `scan` after `CUSIP_MAP_SHA256` is set; `build` refuses a cache not stamped with the current map hash; CUSIPs normalised; name-match-other-CUSIP shares reported, WARN above 1%.
- **R2-3** `holdings.csv` gains `sh_13f_sole` and `sh_pre_ipo_flagged` (a floor and a hypothesis). The README prints, per deal and beside `pct_of_listed`, the IPO shares as a share of the listed class (SpaceX about 7.2%), and says plainly that a high `pct_of_listed` can mostly be pre-IPO holders.
- **R2-4** Weights are primary base proceeds to the company (INNIO 0; secondary parts excluded), with an unweighted median and range beside the weighted figure; the weight identity is tested on unrounded weights.
- **R2-5 to R2-13** as the reviewer wrote them: amendment duplicates and orphans; S2 as an absolute change under 2% that cannot see confidential treatment; VALUE blanks excluded and counted, the ±1% implied-price check, and the Cerebras Brown/AMD price split resolved before the build (C02's Cerebras pins may fail until then); the leak guard extended (all-digit CUSIPs in prose, ISIN and BBG patterns, 6-character issuer fragments; no CIKs or accessions committed; overlap labels only from reviewed public names; Decimal shares); no retrieval date in the `# source:` line; G13 moved to the supervisor step and the G14 ban list extended with a runtime STOP test; SpaceX in the verifier's required set plus a CUSIP cross-check against the SEC's Official List; cornerstone columns renamed to "indicated interest, up to" (a ceiling); `reg_category` `none` described as "no number declared".
- README: the plain universe sentence ("the eight US IPOs of 2026 that raised about $1bn or more, set out in the deal list"), a shorter opening, one-line glosses, and permitted wording for cornerstones and the filing deadline.

## Supervisor rulings, round 3 (Grok attack), 26 Oct 2026 — before any data run

Grok (fenced, read + web; 16 fetches, no breaches) said BUILD WITH CHANGES. I checked its SpaceX figures on the PortfolioSavvy page myself: 3,685,578,550 shares across 1,761 managers at 30 Jun 2026, a stored count of 7,769,200,455, and a 13D row of 6,418,547,515 shares at 48%.

- **R3-0 (overruled in part).** Grok reads the 48% 13D row as a second, contradictory class count (about 13.4bn). It is not. A 13D percentage counts the filer's convertible shares in both numerator and denominator (Rule 13d-3(d)(1)(i)), so a holder of convertible Class B shows a large percentage of Class A without changing the Class A count. The same page's Google row, 551,189,500 shares at 7.2%, implies about 7.66bn Class A, which agrees with the second review's 7.70bn. The build must not use any 13D/13G percentage to infer a class size (already ruled), and C18 compares only typed share counts.
- **R3-1 (accepted; reverses O-3 and R2-1's primary choice).** The numerator is a quarter-end position, so the primary denominator is the listed-class shares outstanding at that quarter-end: from the first 10-Q's balance sheet or equity statement at the period end where it states one, else the 10-Q cover count with its as-of date in `den_listed_10q_asof`. The prospectus `after_offering_base` count becomes the variant column `pct_of_listed_prosp`. A deal without a filed 10-Q has a blank primary percentage, counted and named, never filled from the prospectus. Revise O-3, section 2.3, method 3.6, the header list and its hash together; the README times "shares outstanding" to the quarter-end.
- **R3-2 (accepted, reasoning amended).** `100 − pct_of_listed` is not a holding category and is never described as one. Keep the denial sentence; drop the list of who the rest are. The residual mixes shares outside 13F (a controlling person's block, holdings under the omission threshold, non-filers), shares two managers both reported, confidential treatment, and denominator error. Beside the 13F sum print, per deal, the Class A shares in 13D/13G filings by holders with no 13F row for that quarter, typed counts only, as a separate column.
- **R3-3 (accepted).** Lead with deal-level share counts. Any proceeds-weighted mean appears in the same sentence as SpaceX's weight (about 89%), INNIO's zero weight and the count of unmeasured deals. Add one pooled ratio: sum of 13F shares over sum of quarter-end denominators, with and without SpaceX.
- **R3-4 (accepted).** The CUSIP cross-check uses the SEC Official List for the quarter ended 30 Jun 2026 (the list governing the June reports), not the third-quarter list. The supervisor fetches it.
- **R3-5 (accepted).** C04 (pre-IPO period for a mapped CUSIP) and C07 (percentage above 100) become WARN with the rows listed; neither changes a CUSIP or denominator.
- **R3-6 (accepted).** The filer-type classification reads the column definitions from the 2026 readme the supervisor supplies; prefix matching is longest-first; if the readme does not define the column as the regulatory file number, the classification is dropped, not guessed.
- **R3-7 (accepted).** Values stay in whole dollars (the 2023 amendments; the C02 pins match to the dollar). If a readme still says thousands, that is a readme to report, not a rescale.
- **R3-8 (accepted).** `holder_kind` leaves the measured table; a new-holdings amendment repeating a CUSIP already in the base report is flagged and counted; every Medline path is deleted.
- **R3-9 (new pre-registered reference check, WARN not FAIL).** The June share sums should fall within 2% of the published aggregates: SPCX 3,685,578,550 and CBRS 88,744,964 (PortfolioSavvy, 30 Jun 2026). A miss is reported as a result with the likely cause (amendments after the zip cut-off; option rows), never tuned away.

## Supervisor rulings, round 4 (open questions after the rewrite), 26 Oct 2026 — before any data run

- **O-13, O-14, O-15, O-16:** the author's interpretations are adopted as written.
- **O-17:** `sh_13dg_holders_without_13f` is labelled in the README as beneficial ownership that may include convertible or unlisted shares. It is never added to `sh_13f` or to any percentage of the listed class.
- **O-18:** the ruling summaries govern; there is no separate reviewer text for the builder to look for.
- **O-19:** `pct_of_ipo_shares` stays as a memo column. The README says it exceeds 100 wherever pre-IPO holders file 13F, and no prose leads with it.
- **O-20:** the placeholder line is reworded; the heading stays.
- **C02 Cerebras price split:** resolved by the supervisor from the fetched zip before the build. Until then a failing C02 for CBRS is expected and is not a builder defect.
