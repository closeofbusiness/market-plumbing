# Spec: US money market funds' holdings of claims on non-US banks, by parent country and instrument, month-ends from 2011 (OFR MMF Monitor) (spec author, 25 Oct 2026; rewritten after rounds 2 and 3)

*Candidate X3 of `_research/2026-10-19-CGFS65-Dollar-Funding-Reading.md`; dossier `dossiers/cross-border-and-fx.md`. House style follows
`_research/2026-10-23-H8-Foreign-Offices-Spec.md` and `_research/2026-10-23-BIS-IDS-Dollar-Spec.md`. Script `bin/mmf_nonus_banks.py`,
outputs `data/mmf_nonus_banks/`, check.sh guard **M23**. The rulings at the end are the record; this body applies them (E-027 and the
fourteen round-2 fixes, numbered F1-F14 where applied).*

*"Observed" means seen by the spec author on 25 Oct 2026 between 14:06 and 14:25 UTC, with the CLAUDE.md non-SEC User-Agent and one
request per URL: 32 requests (27 to `www.financialresearch.gov`, 3 to `data.financialresearch.gov`, 1 to `www.bis.org`, 1 to
`catalog.data.gov`), 31 returning 200 and one 403 (SOURCES.md list, section 2.7). The rewrite made no new request; every pin and
figure below was re-derived from the spec author's cache. "Relayed" means taken from a project file, a review, a web search result or
general knowledge and not re-read at source. The OFR release current then was "Updated October 15, 2026 with data through September
30, 2026". **What was seen of the answer before any build:** the spec author saw the pinned node levels (section 8) and, from the OFR
API, the aggregate "repo with foreign financial institutions" series, including its 2011-16 noise and its 2017Q1-2026Q2 dip spread
(section 4.0, recomputed for F4 without printing the mean). The second reviewer computed that aggregate's calendar and Canadian-fiscal
dips and S1's history on it (9 of 9). No country-group statistic has been computed. The `blind` marks in section 4 follow from this.*

## 0. Goal, and what the result can and cannot say

- **Record** month-end holdings by US money market funds (MMFs) of claims on financial institutions whose ultimate parent is
  headquartered outside the US: by parent country, by instrument (repo by collateral, CDs, CP, other) and by fund type, monthly from
  31 Jan 2011, from the OFR U.S. Money Market Fund Monitor (built from SEC Form N-MFP).
- **Describe**, with rules fixed here, whether holdings fall below the neighbouring month-ends at calendar quarter-ends, per country
  group, against a noise reference and against Australia/New Zealand; Japan's March fiscal year-end and Canadian banks' fiscal
  quarter-ends separately. **The single primary measure is `secured` (repo) on `ALL_NONUS`, calendar basis, post-reform window (F14).
  Every other measure, group and basis is exploratory and labelled so.**
- **Set beside** two points of BIS CGFS Papers No 65 (June 2020), descriptively (section 4.4).

**It can say** how much US MMFs held at each month-end in claims on non-US-parented financial institutions, by country and instrument,
and how quarter-end month-ends compare with their neighbours. Levels are MEASURED (filers' reports, mapped by the OFR to parents and
countries). Sums across nodes are IDENTITY. The quarter-end comparison is MEASURED on month-ends; any pattern is HYPOTHESIS as to cause.

**It cannot say:**
- why holdings changed, whether a bank chose to borrow less, or whether any of it relates to a price, a basis or a rate;
- anything about tenor by country (OFR does not publish it; section 2.5) or about positions between month-ends;
- where a non-US bank's FICC-cleared repo sits: N-MFP reports the counterparty of a cleared repo as FICC, which the OFR maps to the USA
  (observed: "FICC" is a USA financial-institution parent, 909.8 $bn in government funds on 2026-09-30). The build therefore carries a
  **memo line `MEMO_FICC`** beside the country lines (F3), outside every non-US total.

**Required README sentences.** Sentence 3: "It records month-end holdings only; it does not show why they changed, and a change in
holdings is not a measure of money moved." In the country-basis item: "A fall in a country line may be offset by a rise in the FICC
line shown next to it."

**Nationality, not residence, and why.** The OFR maps every issuer and every repo counterparty to an *ultimate parent* and assigns the
country of "the address of the ultimate parent's headquarters, or if different, the country where source materials suggest the ultimate
parent has its most substantial operations or marketing presence" (monitor footnote, observed). A US branch of a Japanese bank is Japan.
It is the only basis the OFR offers, and it fits the question: CGFS 65 analyses dollar funding by bank nationality, and quarter-end
reporting is done by the parent group. A residence cut is not available from OFR and is not attempted.

## 1. Hard requirements

- **R1. Free public data only (E-005).** Host allowlist: `www.financialresearch.gov` and `data.financialresearch.gov`. No sec.gov
  (any host ending `sec.gov`), no FRED or ALFRED, no API key. Every other host is refused before the request.
- **R2. User-Agent** exactly `Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)`. The script asserts it
  holds no `@`. Never send an email address, a name, `SEC_UA` or `CLAUDE_CODE_USER_EMAIL`.
- **R3. Crawl conditions (E-027).** GET only, sequential, **at least 2 s between requests**, no redirect followed, **no retry of any
  kind**. **`/money-market-funds/data/mmf_data.zip` is never requested** (it returned 403 to the spec author; the link is commented out
  of the live chart script). At most **one crawl per monthly release**: `fetch` first reads `updated.json`; if a complete vintage with
  that key is cached, it stops there and exits 0. Budget: at most **3,000 requests per vintage**, counted across resumed runs.
- **R3a. STOP latches.** HTTP 403 or 429, any other non-200, or a body failing its content test (R3b) writes
  `data/vintages/mmf_nonus_banks/STOP_ofr` (monitor files) or `STOP_api` (API); exceeding the budget writes `STOP_budget`. Each is
  created exclusively (`open(..., "x")`) with five `name: value` lines: `status`, `utc_time`, `url_path`, `retry_after`, `body_head`
  (first 300 bytes, escaped). That source's fetch ends at once. **Only a person deletes a STOP file. No agent deletes, renames or
  overwrites one, the builder included.** With a latch present, no request is made and the run prints `STOP present: <file>` and exits 2.
  A missing child file (a drill path the OFR does not serve) may answer 403 and so latch; that is intended, and the supervisor decides.
- **R3b. Content tests.** Monitor JSON parses; has keys `datatable` and `highcharts`; the `datatable` column titles after `Date` equal the
  `highcharts` names in order; every series has the same dates. `asof.json` / `updated.json`: one key, a date like "September 30, 2026".
  API: top key equals the mnemonic; `timeseries.aggregation` is a list of `[YYYY-MM-DD, number]`.
- **R3c. Resumable fetch (F12).** A crawl writes into `<cache>/<key>.partial/`, appending each file's `url_path, sha256, bytes` to its
  `manifest.csv` as it lands. A later run with the same key resumes, skipping every path already in that manifest. When the frontier is
  empty, `updated.json` is fetched again: if its date is unchanged, the folder is renamed `<cache>/<key>/` (complete); if it changed,
  that one `.partial` folder is removed by its exact path, the run prints `release changed during crawl` and exits 2, and the next run
  starts the new key. A partial crawl is never built.
- **R4. Cache.** `data/vintages/mmf_nonus_banks/` (gitignored; the builder adds the rule). One file per node, named by the sha256 of its
  URL path, plus `manifest.csv`. The vintage key is the `updated.json` date as ISO (e.g. `2026-10-15`), read from the data, never the
  clock. Kept for size and licence (2.6); never committed.
- **R5. Wording (G15).** No causal, flow or motive wording, except in the one README denial sentence (README item 4). Flows and positions
  are never written as the cause of a price.
- **R6. Code ownership.** `bin/mmf_nonus_banks.py` is new, standard library only, reads no other project data file. No existing script
  changes, apart from a new warn-only `bin/check.sh` guard M23.
- **R7. Post-registration fixes** go in SOURCES.md "Builder decisions" with the old value kept beside the new, never in the README.
- **R8. Numbers (F7).** Money is parsed from JSON as `decimal.Decimal` (`json.loads(..., parse_float=Decimal)`) and summed in Decimal;
  rounding happens only at write time. Log changes are computed from the unrounded Decimal sums converted to float. Decimals per column:
  `usd_mn` and `*_usd_mn` 1; `pct_of_*` 3; `*_chg_pct`, `below_nbrs_pct` and every sd, se, mean, median or noise column 4; `pp` 3;
  counts as integers. `pct_of_mmf_total` = 100 × value / total investments of all US MMFs at the same month-end; `pct_of_nonus_fi` =
  100 × value / the headline `ALL_NONUS` total; `pct_of_lineage_total` uses the same fund lineage's total. A "percent change" here is
  100 × the natural log of the ratio (`_chg_pct`), close to the ordinary percent change for small moves.
- **R9. Dates.** Every output date comes from the data (OFR timestamps, `asof.json`, `updated.json`) or the pull folder. The only
  wall-clock value written is `utc_time` in `fetch_log.csv`; no computed output depends on it, and `build` is offline and byte-identical
  on re-run.

## 2. Data

### 2.1 The monitor's JSON tree (observed)

- **Base:** `https://www.financialresearch.gov/money-market-funds/data/`. The page script `ofr_optimized_highchart.js` loads
  `<base><dir_path>data.json`; `dir_path` is the chart's root folder plus one segment per drill choice. A segment is the child's display
  name, lower-cased, every whitespace character (including U+00A0) replaced by `_`, then percent-encoded as JavaScript's
  `encodeURIComponent` (Python: `urllib.parse.quote(seg, safe="-_.!~*'()")`). Observed 200 for
  `credit_risks_country/government_(fees_%26_gates)/data.json` and `…/france/financial_institution/natexis_%2B_natixis/data.json`.
  Two siblings that map to the same segment are a FAIL (G1).
- **Root `credit_risks_country`** (chart "U.S. MMFs' investments by fund category"). Drill levels (page metadata, observed): Category
  (MFS002) → Region (MFS019) → Country (MFS009) → Sector (MFS006) → Credit, i.e. ultimate parent (MFS008) → Asset Type (MFS005). Measure
  MFS015, "Assets under management", USD.
- **Each file** holds the full history of its children: `highcharts` (`{name, data:[[epoch_ms, usd], …]}`) and `datatable` (same values,
  dates `MM-DD-YYYY`). Epoch values are UTC midnight of the calendar month-end (2011-01-31 = 1296432000000); convert in UTC. All 189 root
  dates are calendar month-ends, 2011-01-31 to 2026-09-30. `datatable` equals `highcharts` in all 13 node files fetched.
- **Month-ends.** N-MFP reports holdings at the close of the month's last business day; an overnight repo entered then spans the calendar
  month-end, so a quarter-end falling on a weekend is still observed (O-6).
- **Category names change at two dates** (observed nonzero months at the root):

| Lineage | Names and nonzero months |
|---|---|
| prime | `Prime` 2011-01..2016-03 (63); `Prime Institutional`, `Prime Retail` 2016-04..2026-09 (126 each) |
| government | `Government` 2011-01..2016-03 and 2024-06..2026-09 (91); `Government (No Fees & Gates)`, `Government (Fees & Gates)` 2016-04..2024-05 (98) |
| tax_exempt | `Tax Exempt` 2011-01..2016-03 (63); `Tax Exempt Institutional`, `Tax Exempt Retail` 2016-04..2026-09 (126) |

  A drill file carries only its category's months (91 dates under `government/`). A missing month is zero only if the category is zero
  at the root that month; otherwise FAIL.
- **Identities (observed, exact to the cent):** the nine categories sum to `MMF-MMF_TOT-M` on 2026-09-30 and 2011-01-31; government
  regions sum to the category and Europe's countries to the region; the seven French financial-institution parents in government funds
  sum to the sector; BNP Paribas's asset types sum to the parent.
- **Sectors seen:** `Financial Institution`, `Government`, `Non-Financial Corporate`. Only `Financial Institution` enters the build.
- **Asset-type labels seen** (BNP Paribas node): Treasury Repurchase Agreement; Government Agency Repurchase Agreement; Other Repurchase
  Agreement; Certificate of Deposit; Financial Company Commercial Paper; Asset Backed Commercial Paper; Other Note; Other Instrument;
  Non-Financial Company Commercial Paper; U.S. Treasury Debt; Government Agency Debt. **Likely further labels, relayed (N-MFP
  investment categories, not seen in OFR JSON):** Non-Negotiable Time Deposit → `time_deposit`; Variable Rate Demand Note, Other
  Municipal Security, Tender Option Bond, Insurance Company Funding Agreement, Investment Company, Other Asset Backed Securities,
  Non-U.S. Sovereign, Sub-Sovereign and Supra-National Debt → `misc`. Each relayed label, if seen, is mapped as listed and C13 WARNs.
- **Country labels seen:** Austria, Belgium, Denmark, France, Germany, Luxembourg, Netherlands, Norway, Spain, Sweden, Switzerland, UK,
  China, India, Israel, Japan, Singapore, South Korea, Canada, USA; regions South America, Supranational, Australia, Asia, Europe, North
  America.
- **Parent mapping is imperfect (observed):** `Natexis + Natixis` and `Groupe BPCE` are separate parents; so are `Northwestern Mutual`
  and `Northwestern Mutual Life Insurance Company`. The build never re-maps OFR parents.
- **Small issuers:** a child named exactly "Aggregated small issuers" (none seen) is not drilled; its value goes to `unallocated`; C10 WARNs.

### 2.2 The API (observed)

`https://data.financialresearch.gov/v1/series/full?mnemonic=<m>` for `MMF-MMF_TOT-M` (denominator check), `MMF-MMF_RP_wFFI-M` (repo with
foreign financial institutions; C09), and, per F3, `MMF-MMF_RP_wFICC-M` (repo cleared by FICC; C14) and `MMF-MMF_RP_wDFI-M` (repo with
US financial institutions; context). The last two are in the observed mnemonic list but were not fetched by the spec author. Unit USD,
magnitude 0; `vintage_approach` "Monthly Revisions - Complete Series". The dataset's 42 mnemonics (observed) include none by country.

### 2.3 Crawl rule (what is fetched)

Breadth-first, per category: (1) root, then each category with a nonzero month; (2) every region with a nonzero month; (3) every country
with a nonzero month, USA included; (4) the sector file of every non-US country; (5) the `Financial Institution` file of every non-US
country; (6) the asset-type file of every non-US financial-institution parent with a nonzero month; (7) **for FICC (F3):** for each
category with a nonzero month, `…/north_america/usa/financial_institution/data.json` (about 9 files), read for the `FICC` child only.
Plus `asof.json`, `updated.json` (twice) and the four API series. **No US parent is drilled**, FICC included, and no non-financial
sector is drilled. Estimate 1,000-2,000 requests, 35-70 minutes at 2 s; the real count goes to `vintages.csv`.

### 2.4 Release, revisions, vintages

- Monthly. The 15 Oct 2026 release carried data through 30 Sep 2026. The 2026-11 release (data through 30 Nov) is expected in mid-
  December 2026 and the 2026-12 release in mid-January 2027; dates are not published in advance and are read from `updated.json`.
- The API says each release revises the complete series; the monitor JSON is overwritten in place. Each complete crawl is a vintage.
  `revisions.csv` is regenerated on every build from all adjacent pairs of complete cached vintages, never appended, never read from
  committed files. Same key with a different manifest sha256 is a FAIL; an `asof` earlier than the previous vintage's is a FAIL.
- **Spec author's copy:** 13 node files plus `asof.json` and `updated.json` (vintage 2026-10-15) in `…/scratchpad/g10/mmfraw/json/`;
  temporary; selftest fixture seed only, not a vintage.

### 2.5 Tenor: what OFR lacks (out of scope, ruling O-5)

The monitor has no maturity level and the API's tenor series are not by country, so tenor by country is not answered here. The SEC's
N-MFP data sets would supply it (page `https://www.sec.gov/data-research/sec-markets-data/dera-form-n-mfp-data-sets`; file names
relayed from the data.gov catalog, e.g. `…/form-n-mfp-data-sets/20260810-20260908_nmfp.zip`; for June 2024 onward the 27 files
`20240610-20240709_nmfp.zip` … `20260810-20260908_nmfp.zip`), with a country crosswalk still to design. A separate future spec; the
supervisor fetches those files. The builder of this spec never contacts sec.gov. The project's N-MFP3 census (`data/vintages/nmfp3/`)
has no country, maturity or LEI field.

### 2.6 Licence

OFR Legal Notices (observed): "No copyright may be claimed for any work on this website that was created by a federal employee in the
course of his or her duties. However, credit is requested". The monitor footnote says the parent and country mapping draws on
"regulatory filings, company disclosures and commercial data", so raw JSON stays in the gitignored cache; committed files are derived
aggregates and the OFR's parent names with countries (`parents.csv`), each citing: Office of Financial Research, "OFR Money Market Fund
Monitor", refreshed monthly, https://www.financialresearch.gov/money-market-funds/. `robots.txt` (observed) does not disallow
`/money-market-funds/` or `/assets/`. The OFR API page asks for no more than one pull a day (relayed from the rulings); R3's one crawl
per release is within that.

### 2.7 Requests made by the spec author (goes to SOURCES.md, not the README)

`www.financialresearch.gov`: `/money-market-funds/`, its three chart pages, `/robots.txt`, `/about/policies/`, `/legal-notices/`,
`/short-term-funding-monitor/datasets/mmf/`, three `/assets/js/mmf/` scripts, `asof.json`, `updated.json` and 13 node files (two of them
the encoding tests of 2.1), all 200; **`/money-market-funds/data/mmf_data.zip`: 403 `AccessDenied` (CloudFront/S3, 111 bytes), not
retried.** `data.financialresearch.gov`: the mnemonic list, `MMF-MMF_TOT-M`, `MMF-MMF_RP_wFFI-M`, all 200. `www.bis.org`: the CGFS 65
PDF, 200. `catalog.data.gov/dataset/form-n-mfp-data-sets`: 200.

## 3. Method

1. **Fetch** (mode `fetch`): the crawl of 2.3 under R3-R3c, every request logged with sha256.
2. **Kinds first** (mode `kinds`, offline): writes `parents.csv` only, for the supervisor's review (method 7). No quarter-end figure.
3. **Select by name, never position.** Lineage, region, country, sector and asset-type maps are literal tables in the script. **Unknown
   labels are collected over the whole vintage and reported together** (F11): one FAIL listing every unknown category, country, sector
   and asset-type label with the node where it appeared (C13). The builder adds them, logs them in Builder decisions and tells the
   supervisor.
4. **Node identities on every node and month:** children sum to the parent's value in the parent's file (tolerance 1.00 USD); the nine
   categories sum to `MMF-MMF_TOT-M` (1.00 USD); `datatable` equals `highcharts`. Any breach is a FAIL.
5. **Country groups (literal, by OFR label):**
   - `EA`: Austria, Belgium, Bulgaria, Croatia, Cyprus, Estonia, Finland, France, Germany, Greece, Ireland, Italy, Latvia, Lithuania,
     Luxembourg, Malta, Netherlands, Portugal, Slovakia, Slovenia, Spain (2026 membership for all dates, ruled O-7);
   - `FR` (France, also inside EA); `JP` Japan; `CA` Canada; `UK` UK; `CH` Switzerland; `NORDIC` Sweden, Norway, Denmark;
   - `AUNZ`: every country under region `Australia`; `OTHER_ASIA`: every other country under region `Asia`;
   - `OTHER`: every other non-US country; region `Supranational` is excluded from every non-US total;
   - `ALL_NONUS` = EA + JP + CA + UK + CH + NORDIC + AUNZ + OTHER_ASIA + OTHER;
   - `MEMO_FICC`: the `FICC` parent in the USA `Financial Institution` file, summed over categories; measure `headline` only; in no total.
6. **Measures.** `headline`: the `Financial Institution` sector of non-US countries, all asset types, all lineages. Instrument groups
   (literal): `repo_treasury`, `repo_agency`, `repo_other`; `cd`; `time_deposit`; `fin_cp`; `other_note` (Other Note, Other Instrument);
   `abcp`; `misc` (Non-Financial Company CP, U.S. Treasury Debt, Government Agency Debt, and the relayed `misc` labels); `unallocated`.
   `secured` = the three repo groups (the README says "repo"); `unsecured` = cd + time_deposit + fin_cp + other_note; `abcp` and `misc` as
   named. **Identity: secured + unsecured + abcp + misc + unallocated = headline** (C16). ABCP sits under the sponsoring bank's parent
   in OFR's mapping and stays in the headline (ruled O-8).
7. **`kind` and the bank-only measure (F10).** Every non-US financial-institution parent gets `kind` ∈ {bank, insurer, other_fin}. A
   **bank** is a deposit-taking institution or a bank holding company; broker-dealer parents (e.g. Nomura) are `other_fin`; insurers
   are `insurer`. The builder sets kinds in mode `kinds` and lists them in Builder decisions; the supervisor reviews `parents.csv` (which
   carries no quarter-end figure) and sets the constant **`KIND_TABLE_SHA256`** = sha256 of the lines `parent|country|kind\n` sorted by
   parent. `build` exits 2 before writing any output if the current table's sha256 differs, or if any parent lacks a kind.
8. **Quarter-end statistics.** For a group's monthly level L of a measure (all lineages):
   - `chg_in_pct` = 100·ln(L(q)/L(q−1)); `chg_out_pct` = 100·ln(L(q+1)/L(q)); `below_nbrs_usd_mn` = L(q) − ½(L(q−1) + L(q+1)).
   - **Two-sided** (`stat_kind = two_sided`), bases `calendar` (q = Mar, Jun, Sep, Dec; every group), `jp_march` (JP, Mar), `jp_other`
     (JP, Jun, Sep, Dec): `below_nbrs_pct` = 100·[ln L(q) − ½(ln L(q−1) + ln L(q+1))] = ½(chg_in − chg_out).
   - **One-sided** (`stat_kind = one_sided`, F2), basis `ca_fiscal` (CA, q = Jan, Apr, Jul, Oct): `below_nbrs_pct` = −`chg_out_pct`,
     using only the clean next month (Feb, May, Aug, Nov). `level_prev_usd_mn`, `chg_in_pct` and `below_nbrs_usd_mn` are blank.
   - **Rule: no basis other than `calendar` may use a calendar quarter-end month as a neighbour.**
   - A zero level leaves the affected cells blank (`n_blank`). Until L(q+1) is published, a row carries `chg_in_pct` only.
9. **Noise reference.** The sample sd (ddof = 1) of the group's month-on-month log changes Jan→Feb, Apr→May, Jul→Aug, Oct→Nov (the only
   changes touching no calendar quarter-end month) in the same window: `noise_clean_sd_pct` = that sd ÷ √2 for two-sided rows, and the
   sd itself for one-sided rows. `noise_n` is the count of changes.
10. **Summary per (basis, window, group, measure):** n (non-blank), mean, median, `n_negative`, sd (ddof = 1), `se_mean` = sd/√n, the
    noise reference, and `pattern`: `insufficient` if n < 8; else `lower` if mean ≤ −2·se_mean, `higher` if mean ≥ +2·se_mean, else
    `neither`. A sample description, not a test of a cause.
11. **Paired difference against AUNZ (F14).** For every group other than AUNZ, same basis, window and measure: over quarters where both
    are non-blank, d(q) = below_g(q) − below_AUNZ(q); report n, mean and se = sd/√n. AUNZ is the CGFS paper's own contrast (4.4).

## 4. Questions, fixed in advance (answers in `summary.csv`, `quarter_ends.csv`, `qe_summary.csv`)

**4.0 Predicted effect and MDE (F4).** Precision is set by the number of quarter-ends: n = 38 in the frozen window. On the OFR
repo-with-foreign-institutions aggregate, 2017Q1-2026Q2, realised 2·se_mean was 2.05 and the clean-month figure 4.40 against a realised
dip sd of 6.31; negative correlation of d_in and d_out (−0.55) makes dip noise larger, so the MDE of record is the realised 2·se_mean
(re-derived by the spec author from its cache: sd 6.31, 2·se 2.05, clean sd 6.22 ÷ √2 = 4.40, correlation −0.55; the mean was not
printed). **Predicted effect (HYPOTHESIS, set before the build):** for the primary measure, a mean fall below the neighbouring months of
**5 percent or more** (`mean below_nbrs_pct` ≤ −5). Basis: CGFS 65's "significantly reduce" (p 35) and the 2011-16 aggregate, whose
changes touching a quarter-end month were far larger than clean ones (robust sd 24.6 against 6.47). Against an MDE near 2 it is
detectable if true. Country groups are noisier; their realised 2·se_mean is their MDE.

**Windows.** `post_reform` (frozen): calendar quarters **2017Q1-2026Q2 (38)**, after the 14 Oct 2016 prime-fund reform. `transition`:
2016Q3-Q4, written as rows and in no summary (F8). `pre_reform`: 2011Q1-2016Q2 (22). `after_freeze`: 2026Q3 onward, `frozen_set = no`;
2026Q3 carries `chg_in_pct` only until the 31 Oct 2026 month-end is published. `ca_fiscal` rows take the window of the calendar quarter
holding the fiscal month (Jan 2017 to Apr 2026 frozen: 38). `jp_march` 10, `jp_other` 28.

**`blind` (F8).** On `quarter_ends.csv` rows: `no` if the window is `pre_reform`, `transition` or `after_freeze`; `no` if any of the
row's months is 2026-06 or later; `no` on every `ALL_NONUS` row of measures `secured` and `headline` (the aggregate proxy was seen);
otherwise `yes`. The question rows of Q1, Q2, Q6 and Q7 are `no`. A `qe_summary.csv` or `summary.csv` row is `yes` only if every row
it is built from is `yes`.

**Named endpoints:** mid-quarter month-ends only: **February** of each year and **2026-08-31**. README reason: a quarter-end month may
swing, so an endpoint there would put a quarter-end move into a multi-year change.

- **Q1. Levels and shares since 2011.** Per group, measure and lineage: the level on each February 2011-2026 and on 2026-08-31, with
  `pct_of_mmf_total` and `pct_of_lineage_total`. Per-country monthly levels in `levels_country.csv`.
- **Q2. Change over 2024-26.** Per group and measure: 2024-02-29 → 2025-02-28 → 2026-02-28 → 2026-08-31, in $mn, `chg_pct`, and as the
  change in `pct_of_mmf_total` (pp).
- **Q3. Quarter-ends, calendar basis.** Every group (MEMO_FICC included) and measures headline, bank_only, secured, unsecured: rows in
  `quarter_ends.csv`, the summary of method 10 and the paired difference of method 11 per window. **Primary:** `secured`, `ALL_NONUS`,
  `calendar`, `post_reform` (`primary = yes`); every other row `primary = no`.
- **Q4. Japan's fiscal year-end:** `jp_march` beside `jp_other`; n = 10 is small and the README says so.
- **Q5. Canadian fiscal quarter-ends:** CA `ca_fiscal` (one-sided) beside CA `calendar`. Dates ruled (O-3): 31 Jan, 30 Apr, 31 Jul, 31 Oct.
- **Q6. Revisions.** Per vintage pair: cells changed, the largest absolute change with month and country, and whether any month more
  than 12 months old changed.
- **Q7. S1 historical hit rate** (4.5).

### 4.4 The CGFS 65 points, set beside the data (the paper's words, printed page numbers)

- The paper does **not** single out Japanese and Canadian banks as MMF-dependent. It says the 2016 reform cut prime funds by about
  $1 trillion and that non-US banks "now obtain less funding from US MMFs" (p 20; tenor "has shortened considerably", p 27). It singles
  out French banks: they raise dollars "mainly via overnight repos from US MMFs" (p 67), and US MMFs "have become the most important repo
  counterparties to French banks" (pp 67-68). Its MMF charts (Graph 14, p 28) use Crane Data, which is not free.
- Quarter-ends: "some non-US banks significantly reduce their matched book repo activity at quarter-ends", linked to the leverage ratio
  (p 35; also p 28); no country named. Australian banks "are not subject to the quarter- or year-end balance sheet constraints" (p 73):
  hence AUNZ as contrast.
- The README may set Q1 and Q3 beside these sentences in a two-column table, with no verdict word such as "confirms". Reporting
  conventions by jurisdiction are relayed knowledge and enter no rule.

### 4.5 A pre-registered statement for 31 Dec 2026 (F5)

**S1.** "For `ALL_NONUS`, measure `secured`: `chg_in_pct`(2026-12) ≤ −N", where N is the clean-month sd (method 9, before ÷ √2) of
`ALL_NONUS` `secured` in the `post_reform` window **as computed by the first build, frozen there and recorded in Builder decisions**
(the proxy gives 6.22). It needs only the November and December month-ends and is scored on the first release with data through
31 Dec 2026 (mid-January 2027). **Historical hit rate:** the share of the 9 frozen year-ends (2017-2025) on which the same rule held for
`secured` (`summary.csv`, Q7). **Registration:** S1 stands only if (a) the historical hit rate is at least 8 of 9, and (b) its CALENDAR row
is committed **before the 2026-11 release** (data through 30 Nov 2026, expected mid-December 2026, identified by `updated.json`);
otherwise it is void and the reason is recorded. **Honesty note:** the second reviewer saw 9 of 9 on the aggregate proxy; at 9 of 9 a
HELD is near-certain, so S1 checks that a known pattern persists and carries little information. Proposed CALENDAR row (text only):
`2027-01-18`, "Score S1 on the first OFR MMF release with data through 31 Dec 2026: fetch and build; read `quarter_ends.csv` 2026Q4
ALL_NONUS secured chg_in_pct; HELD if ≤ −N (frozen value in Builder decisions)". A failed S1 is a result.

## 5. Outputs

**Script `bin/mmf_nonus_banks.py`.** Modes `fetch`, `kinds`, `build` (offline, byte-identical on re-run), `selftest` (synthetic, no
network, under 20 s). Committed files in `data/mmf_nonus_banks/`; each CSV begins with one `# source:` line naming the OFR monitor, the
vintage's `updated` and `asof` dates, the retrieval date from `fetch_log.csv`, and the citation of 2.6.

**Header allowlist, canonical text.** One line per file, `<name>:<headers comma-joined, no spaces>`, each ending in LF, in this order.
The script holds `SPEC_ALLOW_SHA256`; **`bin/check.sh` holds its own literal copy of these ten lines** and never reads them from the
script. G13 and M23 skip the `# source:` line.

```
levels_country.csv:month_end,country,country_group,instrument_group,usd_mn,pct_of_mmf_total,pct_of_nonus_fi,vintage
levels_group.csv:month_end,country_group,fund_lineage,measure,usd_mn,pct_of_mmf_total,pct_of_lineage_total,vintage
quarter_ends.csv:quarter,qe_month,basis,stat_kind,country_group,measure,level_prev_usd_mn,level_qe_usd_mn,level_next_usd_mn,chg_in_pct,chg_out_pct,below_nbrs_pct,below_nbrs_usd_mn,window,frozen_set,primary,blind,vintage
qe_summary.csv:basis,stat_kind,window,country_group,measure,n_quarters,n_blank,mean_below_nbrs_pct,median_below_nbrs_pct,n_negative,sd_below_nbrs_pct,se_mean_below_nbrs_pct,noise_clean_sd_pct,noise_n,pattern,paired_n_vs_aunz,paired_mean_diff_vs_aunz_pct,paired_se_vs_aunz_pct,primary,blind,vintage
parents.csv:parent,country,country_group,kind,first_month,last_month,usd_mn_latest,vintage
summary.csv:question,window,country_group,measure,from_month,to_month,statistic,value,unit,primary,blind
revisions.csv:vintage_prev,vintage_new,month_end,country,instrument_group,usd_mn_prev,usd_mn_new,change_usd_mn
vintages.csv:vintage,ofr_updated,ofr_asof,requests,nodes,manifest_sha256,api_total_check,kind_table_sha256
checks.csv:check_id,description,expected,observed,status
fetch_log.csv:utc_time,host,path,status,bytes,sha256
```

**sha256 of that text (1,273 bytes): `07dc8c29cbd4971ada14f2f638cc600f857756dee7f97518cac5b3f189fccf4f`** (computed by the spec author; superseded hash
`15e3acd47f3a7859937b515753e0561bd8c0618ebf84cd75fe9c7f7814f9f77e`). A builder who needs a column changes this text and its hash
first, logs it in Builder decisions, and tells the supervisor.

**`summary.csv` grammar (F8):** one statistic per row; `measure`, `from_month` and `to_month` blank where not applicable; `statistic` ∈
{level, pct_of_mmf_total, pct_of_lineage_total, change_usd_mn, change_chg_pct, change_pp, hit_rate, cells_changed, max_abs_change_usd_mn,
old_month_revised}; key (question, window, country_group, measure, from_month, to_month, statistic) unique.

**Allowed values:** `country_group` ∈ {EA, FR, JP, CA, UK, CH, NORDIC, AUNZ, OTHER_ASIA, OTHER, ALL_NONUS, MEMO_FICC}; `fund_lineage` ∈
{all, prime, government, tax_exempt}; `measure` ∈ {headline, bank_only, secured, unsecured, abcp, misc}; `instrument_group` ∈
{repo_treasury, repo_agency, repo_other, cd, time_deposit, fin_cp, other_note, abcp, misc, unallocated, total}; `basis` ∈ {calendar,
jp_march, jp_other, ca_fiscal}; `stat_kind` ∈ {two_sided, one_sided}; `window` ∈ {post_reform, transition, pre_reform, after_freeze};
`kind` ∈ {bank, insurer, other_fin}; `pattern` ∈ {lower, higher, neither, insufficient}; `frozen_set`, `primary`, `blind` ∈ {yes, no};
`unit` ∈ {usd_mn, chg_pct, pp, pct, count, share, yes_no}. `levels_country.csv`: non-US countries, nonzero cells, one `total` row per
country-month. Duplicate keys in any file are a FAIL.

- **`README.md`** (generated; G15 scans it), in this order, plain words throughout ("percent change", "fall below the neighbouring
  months", "repo"; never "log point" or "dip"):
  1. **Opening, two sentences (F13), verbatim:** "This table shows how much US money market funds held at each month-end since January
     2011 in claims on banks and other financial institutions whose ultimate parent, the company at the top of the group, is
     headquartered outside the United States, by that parent's home country and by type of instrument. The figures come from the funds'
     own monthly holdings reports to the Securities and Exchange Commission, called Form N-MFP, as compiled by the Treasury's Office of
     Financial Research (OFR), which assigns each security's issuer, or for a repurchase agreement (repo) the firm on the other side of
     the trade, called the repo counterparty, to its ultimate parent."
  2. Sentence 3, from section 0.
  3. **Country basis:** nationality, with the US-branch example; FICC; the sentence "A fall in a country line may be offset by a rise in
     the FICC line shown next to it."; the parent-mapping caveats.
  4. **What is counted:** the financial-institution sector; repo, unsecured, ABCP and other, with "repo + unsecured + ABCP + other =
     total"; then the one denial sentence: "These month-end changes are not flows of funds, and the table does not test window dressing
     or any other motive."
  5. Levels and shares (named Februaries and 2026-08-31), then the 2024-26 changes, in plain tables; the endpoint reason.
  6. **Quarter-ends:** how far a quarter-end month falls below the neighbouring months, in percent; the noise reference; the comparison
     with Australia/New Zealand; the windows; the single primary row named first and everything else called exploratory; `pattern` as a
     sample description; Japan (n = 10) and Canada (next month only, why).
  7. The CGFS 65 table, if used. 8. Tenor not available. 9. Revisions and vintages. 10. Column dictionary. 11. The OFR citation and
     copyright statement. The questions of section 4 do not appear in the README.
- **`SOURCES.md`:** every URL with access date and status (the 403 line of 2.7 here), the drill levels, the literal maps, the relayed
  labels, the licence text, the CGFS quotes with pages, the disclosure paragraph of the header, and **Builder decisions** (build choices,
  the `kind` table and its review date and sha256, new labels, the frozen S1 noise N, every post-registration fix with old and new values).

## 6. Leak and integrity rules

1. Committed: only the ten CSVs, README.md and SOURCES.md. No `.json`, `.zip`, `.html`, `.pdf`; no file whose first non-comment line
   starts `{"datatable"` or `{"highcharts"`; no local path (`/Users/`, `/private/`, `~`); no `@`.
2. Nothing is written outside `data/mmf_nonus_banks/` and the gitignored cache, apart from the `.gitignore` rule and a REPRODUCE.md
   paragraph (landing).

## 7. Selftests (synthetic only; each guard applies its own mutant, and an uncaught mutant fails the selftest)

**G15's literal patterns, both compiled with `re.I`** (pasted, not imported). `CAUSAL_RX`:

```
\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of)\b
```

`EXTRA_RX`:

```
\b(?:in|out)?flows?\b|window[- ]dressing|\b(?:head\s+offices?|parents?)\s+(?:fund|funds|funded|funding|push|pushes|pushed|pull|pulls|pulled|drain|drains|drained)\b|\b(?:dollar\s+)?(?:shortage|squeeze)\b|\bpull(?:ed|ing|s)?\s+(?:back|out)\b|\bretreat(?:ed|ing|s)?\b|\bruns?\s+on\b|\bflight\b|\blog[- ]points?\b|\bdips?\b
```

| Guard | Protects | Mutant that must be caught |
|---|---|---|
| G1 path encoding | 2.1 | `quote_plus`; `+` or `&` or `,` left raw; parentheses encoded; only the first space replaced; U+00A0 not replaced; **two siblings mapping to one segment accepted**. Pins: `Natexis + Natixis` → `natexis_%2B_natixis`; `Government (Fees & Gates)` → `government_(fees_%26_gates)`; `Société Générale` → `soci%C3%A9t%C3%A9_g%C3%A9n%C3%A9rale`; `Loop Capital\xa0Holdings, LLC.` → `loop_capital_holdings%2C_llc.` |
| G2 node identities | 3.4 | a dropped child; a child counted twice; a 5 USD breach; `datatable` ≠ `highcharts` in one cell |
| G3 category lineage | 2.1 | `Government` treated as pre-2016 only; `Government (Fees & Gates)` omitted; old and new names both nonzero in one month accepted; a missing month filled with zero while the root category is nonzero |
| G4 total cross-check | 3.4 | categories ≠ `MMF-MMF_TOT-M` by 0.1% accepted; the API total used as denominator without the check |
| G5 country map | 3.5 | an unknown label accepted; UK in EA; USA or FICC counted as non-US; Supranational counted; substring selection; FR or MEMO_FICC added into ALL_NONUS |
| G6 sector | 3.6 | a non-US `Government` or `Non-Financial Corporate` sector counted (fixture: a Japan `Government` child) |
| G7 instruments | 3.6 | an unknown label accepted; ABCP or misc in `unsecured`; repo counted as unsecured; the C16 identity broken; unknown labels reported one at a time instead of together (F11) |
| G8 numbers | R8 | floats summed instead of Decimal (fixture of 10,000 cents-valued children whose float sum is off by more than 0.005); values read as thousands; $bn in a `_usd_mn` column; rounding before summing; logs taken on rounded `usd_mn`; wrong decimals in a column |
| G9 dates | 2.1 | epoch converted in local US time (2011-01-31 → 2011-01-30); `MM-DD-YYYY` read day-first; a non-month-end date accepted |
| G10 quarter-end arithmetic | 3.8-3.10 | pins: levels (100, 90, 110) → `below_nbrs_pct` −15.3016; (100, 80, 100) → −22.3144, and a fixture of such quarters gives `lower`. Mutants: two-sided from `chg_in` only; neighbours taken as the previous quarter-end; **a series with a calendar-only fall returns anything but `neither` for `ca_fiscal`**; `ca_fiscal` computed two-sided; a non-calendar basis using a calendar quarter-end neighbour; `jp_march` not March; ±inf instead of blank; a clean change touching a quarter-end month; √2 omitted on two-sided or applied on one-sided noise; **sd with ddof = 0**; **a threshold using sd instead of se**; n < 8 not giving `insufficient`; the paired AUNZ se computed unpaired |
| G11 windows and blind | 4 | 2016Q3-Q4 in a summary; a post-2026Q2 row with `frozen_set = yes`; a pre_reform, transition, after_freeze, Q1, Q2, Q6, Q7 or ALL_NONUS secured/headline row with `blind = yes`; a summary row `yes` built from a `no` row; more than one `primary = yes` row in `qe_summary.csv` |
| G12 endpoints | 4 | a quarter-end month used as a multi-year endpoint |
| G13 allowlists | 5 | an extra or renamed column; `SPEC_ALLOW_SHA256` ≠ sha256 of the canonical text; `# source:` compared as a header; an 11th CSV; **check.sh reading the header lines from the script**; a duplicate key in `summary.csv` |
| G14 leak guard | 6 | **on a planted bad folder** with a raw node JSON, a node JSON renamed `.csv`, and a `/Users/` path in SOURCES, each reported; **on the clean folder it passes** |
| G15 wording | R5 | the patterns above, applied to README.md everywhere but the denial sentence (SOURCES.md is not scanned: it quotes reviews). The opening, sentence 3 and the FICC sentence pass; adding "because of quarter-end window dressing" fails; a second sentence with "flows" fails; "banks pulled back from money funds" fails; "a dip of 5 log points" fails |
| G16 STOP latch | R3a | **AST scan**: a STOP path reached by `os.remove`, `os.unlink`, `os.replace`, `os.rename`, `shutil.rmtree`, `shutil.move`, `Path.unlink`, `Path.rename`, `Path.write_text`, `Path.write_bytes` or `open` in mode w or a (only `x` allowed); a delete or rmtree over the cache root or by glob (removing one `<key>.partial` by exact path is allowed). Runtime: with planted `STOP_ofr`, `fetch` makes no request, exits 2, sha256 unchanged; fixture 403 and 429 each write `STOP_ofr` with five fields; request 3,001 writes `STOP_budget` |
| G17 fetch safety | R1-R3c | a non-allowlisted host (`www.sec.gov`, `fred.stlouisfed.org`); `mmf_data.zip` requested; `@` in the UA; a redirect followed; requests under 2 s apart; any retry; a US parent drilled (FICC included); a non-financial sector drilled; the USA financial-institution file fetched for a category with no nonzero month; a second crawl for a key already complete; a resumed run re-fetching a path in the partial manifest; a crawl kept after `updated.json` changed |
| G18 vintages and revisions | 2.4 | `revisions.csv` built incrementally differs from the one regenerated from all cached pairs; same key with a different manifest sha256 accepted; a `.partial` folder treated as a vintage; key from the wall clock; an earlier `asof` accepted |
| G19 kind | 3.7 | a parent without kind accepted; an insurer (`Axa SA`) or a broker-dealer (`Nomura`) counted in `bank_only`; `build` run with a kind table whose sha256 ≠ `KIND_TABLE_SHA256`; `parents.csv` written with a quarter-end column |
| G20 shares and sums | R8 | a `pct_` value outside 0-100; the nine groups not summing to ALL_NONUS in any month, measure or lineage; `pct_of_nonus_fi` on bank_only |

## 8. Pinned checks (`checks.csv`)

**Pin rules (as H8).** Values in USD to the cent, vintage 2026-10-15, re-derived from the spec author's cache. Recent pins (months within
12 of `asof`) FAIL on vintage 2026-10-15 and WARN on later vintages with their `revisions.csv` rows. Stable pins WARN if `revisions.csv`
has a row for that cell in this vintage pair, else FAIL.

- **C01 Total and API:** sum of the nine root categories 2026-09-30 **8,396,822,287,018.74**, 2011-01-31 **3,011,802,131,036.00**; each
  equals `MMF-MMF_TOT-M` that date.
- **C02 French financial institutions, government funds, 2026-09-30:** **216,102,500,879.82** = BNP Paribas **119,064,967,826.42** +
  Credit Agricole **51,474,585,053.40** + Societe Generale **26,237,948,000.00** + Natexis + Natixis **19,325,000,000.00** (Axa SA,
  Credit Mutuel, Groupe BPCE zero). BNP Paribas = Treasury repo **86,062,527,564.34** + agency repo **33,002,440,262.08**.
- **C03 Government-fund country totals (all sectors), 2026-09-30:** Japan **113,982,689,785.25**; Canada **237,451,088,980.92**; USA
  **6,179,508,927,720.00**; region Europe **335,544,661,517.19**. Stable: France 2016-03-31 **55,610,766,012.58**, 2024-06-30
  **183,349,026,908.53**.
- **C04** French financial institutions, government funds, 2026-06-30: **209,083,190,057.81**.
- **C05 Prime and mid-era (F6), stable except the first:** Prime Institutional / Europe 2026-09-30 **97,894,050,668.11**; Prime / Europe
  2011-01-31 **885,581,940,544.21** and 2016-03-31 **481,729,017,251.35**; Prime Institutional / Europe 2016-04-30
  **530,959,993,340.79**; Government (Fees & Gates) / Europe 2016-04-30 **63,230,004,856.22**; Government (Fees & Gates) / North America
  2020-03-31 **4,528,754,694.53**.
- **C06 FICC:** government / North America / USA / Financial Institution / `FICC`, 2026-09-30 **909,754,515,958.22**; in MEMO_FICC,
  never in a non-US total.
- **C07 Lineage coverage:** nonzero month counts 63, 126, 126, 91, 98, 98, 63, 126, 126 (2.1).
- **C08 Dates:** 189 root months to `asof` at this vintage, all calendar month-ends, no gaps.
- **C09 Repo cross-check (WARN):** non-US `secured` against `MMF-MMF_RP_wFFI-M` (2026-09-30: 890,163,548,540.15) every month; gap printed.
- **C10 Unallocated (WARN):** any "Aggregated small issuers" child.
- **C11 Derived:** `levels_group.csv` FR / government / headline / 2026-09-30 = 216,102.5 $mn (both fees-and-gates categories are zero then).
- **C12 Fixed output:** a second `build` leaves every sha256 unchanged.
- **C13 Labels:** no unknown label (FAIL, all listed together); relayed labels seen (WARN, listed).
- **C14 FICC cross-check (WARN):** MEMO_FICC against `MMF-MMF_RP_wFICC-M` every month; gap printed.
- **C15 Kind gate:** current kind table sha256 = `KIND_TABLE_SHA256`, with the review date in Builder decisions.
- **C16 Measure identity:** secured + unsecured + abcp + misc + unallocated = headline for every group, month and lineage (1.00 USD).

## 9. Success criteria

1. `python3 bin/mmf_nonus_banks.py selftest` prints G1 to G20 with every mutant caught and exits 0.
2. `fetch` obeys R3-R3c (2 s spacing, no retry, ≤ 3,000 requests per vintage, all logged, `mmf_data.zip` never requested). If a STOP is
   written, the builder stops, tells the supervisor, and never deletes it.
3. `kinds` then supervisor review then `build`: C01-C08, C11-C13, C15 and C16 PASS. Acceptable WARNs: recent pins on a later vintage,
   stable pins with a revision row, C09, C10, C13 relayed labels, C14. Every other WARN goes to the supervisor.
4. **A verifier re-derives by hand** from the cached vintage: France / Financial Institution / government funds on 2026-09-30 = the sum of
   its parents = 216,102,500,879.82 USD, and BNP Paribas's two repo lines sum to its parent (or the same vintage's revised values).
5. **M23** (warn-only, in `bin/check.sh --all`), with its own copy of the ten header lines: file names; headers (skipping `# source:`);
   no raw file, local path or `@`; no G15 pattern in README.md outside the denial sentence; **on every month, measure and lineage** of
   `levels_group.csv`, the nine groups sum to ALL_NONUS (✗ if not); **no duplicate key** in any file (✗). On a scratch copy with a
   planted node JSON, a renamed header, a doubled FR row and **ALL_NONUS inflated by FR**, M23 prints four ✗ lines; on the clean folder,
   ✓. It is shown failing on the planted copy before it lands.
6. **Supervisor hash step (F9):** extract the allowlist block from this spec, take its sha256, and compare it with `SPEC_ALLOW_SHA256`
   in the script and with the sha256 of check.sh's literal block; all three must match `07dc8c29cbd4971ada14f2f638cc600f857756dee7f97518cac5b3f189fccf4f`.
7. **README cold-reader test.** Two fresh agents read only the README: a non-specialist and a money-market practitioner. **Pass** only if
   each can state the population, the country basis (ultimate parent), that values are month-ends, that FICC-cleared repo is in a
   separate line, and which single row is primary. **Fail** if either believes the table measures money moved, that a quarter-end fall
   shows window dressing, or that it gives tenor by country.

**Landing (builder):** the `.gitignore` rule; a REPRODUCE.md paragraph; a proposed monthly CALENDAR row as text (after each OFR release:
`fetch`, `build`, read `revisions.csv` and the newest quarter rows); the S1 row only under 4.5's registration rule; a HANDOVER row. The
builder commits nothing; the supervisor verifies and writes any findings text.

## 10. OPEN questions

- **O-2 C09/C14 definitions.** Whether the API's counterparty typing (foreign, FICC) matches the monitor's parent-country mapping is
  undocumented; both checks are WARN until the first build shows the gaps.
- **O-6 Report date.** N-MFP's last-business-day convention and the OFR's month stamp are taken as stated in 2.1; the OFR reference guide
  (`/briefs/files/OFRbr_2016-07_Money-Market-Fund-Monitor.pdf`) was not read.
- **O-9 MEMO_FICC instruments.** FICC is not drilled (no US parent is), so MEMO_FICC carries `headline` only, assumed to be repo. The
  supervisor may allow one asset-type file per category for FICC (about 9 requests) if C14's gap is large.
- **O-10 Country spellings.** Several euro-area labels (Italy, Ireland, Finland and others) have not been seen in OFR JSON; a different
  spelling surfaces through C13 on the first build.
- **O-11 S1's information.** With 9 of 9 seen on the proxy, S1 is close to certain; the supervisor may prefer to register nothing.
- **O-12 Predicted effect.** The 5 percent prediction (4.0) rests on qualitative wording and pre-2016 behaviour; the supervisor may set
  another before the build.

## Supervisor rulings, 25 Oct 2026 (before any data run)

- **O-1 HOLD on the data route.** The OFR "Complete Dataset" zip returned HTTP 403. Crawling the monitor's per-chart `data.json` files instead (1,000–2,000 requests a month) would obtain the same data by another route, and the project's rule is to stop on a refusal and never route around it. robots.txt (checked 25 Oct) does not disallow the monitor paths, and the OFR's API carries no country split (42 series; only an aggregate "repo with foreign financial institutions"). This is put to the principal for a ruling, like E-024 and E-025. **No build runs until he rules.** Reviewers may read the OFR's terms of use and the monitor page to inform the ruling, but must not request the zip again.
- **O-3:** the Canadian banks' fiscal quarter-end dates must be verified from the banks' own published reports before the build; until then the Canada rows are descriptive only.
- **O-5:** tenor by country is out of scope (a separate future spec needing SEC files the supervisor fetches).
- **O-7:** the 2026 euro-area list for all dates stands, disclosed.
- **O-8:** asset-backed commercial paper stays in the headline as the OFR assigns it, and is printed separately where the OFR tree gives it.
- **S1:** the conditional registration stands; the 8-of-9 year-end gate is computed by the build, not by anyone beforehand, and the rows the author saw (the aggregate repo with foreign institutions, Aug–Sep 2026) are marked not blind.
- **Guard number:** **M23**.

## Supervisor rulings, rounds 2 and 3 (second review and Grok, g10), 25 Oct 2026 — before any data run

- **O-1 RESOLVED by the principal (E-027, 25 Oct): crawl the monitor's chart files politely.** Pace requests (at least 2 s apart), the neutral User-Agent, STOP latch on any 403 or 429 and never retry; derived statistics only; `mmf_data.zip` is never requested. Supporting facts for the record: the zip link in the OFR's live chart script is commented out (both reviewers); the monitor pages say the data are downloadable and the chart button writes the on-screen series to CSV (Grok); robots.txt allows the paths; the OFR's API page asks for no more than one pull a day, so the build crawls at most once per monthly release. The second reviewer's `OFR_ROUTE_CLEARED` file is not needed.
- **O-3 RESOLVED:** the Canadian banks' fiscal quarters end on 31 January, 30 April, 31 July and 31 October (Grok, from the banks' own investor pages; Scotiabank states it in one sentence).
- **All fourteen fixes of the second review are accepted otherwise:** the `ca_fiscal` one-sided statistic and the "no calendar quarter-end month as a neighbour" rule (fix 2); the FICC memo line and the two extra API series (fix 3); the MDE paragraph with the realised 2·se of record and a stated predicted effect size (fix 4); S1 registered only if its CALENDAR row is committed before the 2026-11 release, the clean noise frozen from the first build, the hit rate computed on `secured` and called "historical hit rate", with the statement that 9 of 9 makes HELD near-certain (fix 5); the mid-era pins (fix 6); the extra fixtures and mutants, minimum n and `insufficient` (fix 7); the `summary.csv` grammar, `blind` definition and `transition` value (fix 8); the M23 planted cases and spec-hash supervisor step (fix 9); the `kind` definition and `KIND_TABLE_SHA256` gate (fix 10); unknown labels collected and reported (fix 11); a resumable fetch that never re-crawls a complete vintage, re-reads `updated.json`, and latches `STOP_budget` (fix 12); README definitions inside the verbatim opening, the 403 line moved to SOURCES.md, plain words ("percent change", "fall below the neighbouring months", "repo") (fix 13); a paired dip difference against Australia/New Zealand with its standard error, and `secured` on ALL_NONUS named the single primary measure, the rest exploratory (fix 14).
- **Disclosure:** the second reviewer saw the aggregate repo-with-foreign-institutions series (2017–2026) and computed its calendar and Canadian-fiscal dips; S1's history on that proxy (9 of 9) is therefore seen. SOURCES.md records it.

## Supervisor rulings, round 4 (spec author's open items), 25 Oct 2026 — before any data run

- **O-9:** the FICC memo line stays total-only; no extra drill.
- **O-10:** euro-area spellings are settled by the first build's label report; the builder maps any mismatch in the open and records it.
- The column renames (`chg_in_pct`, `chg_out_pct`, `below_nbrs_pct`) and the README-only wording scan are accepted.
- The KIND_TABLE_SHA256 gate: the builder runs `kinds`, sends the parent list in its report, and the supervisor sets the constant before `build` runs.
