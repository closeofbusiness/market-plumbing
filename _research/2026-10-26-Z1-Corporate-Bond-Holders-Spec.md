# Spec: net acquisition of US corporate and foreign bonds by holder sector, 2024Q1-2026Q2 against 2017-2019 (Fed Z.1 table F3.5, formerly F.213/L.213): a descriptive ledger (spec author, 26 Oct 2026; rewritten to apply the supervisor rulings of round 1)

*CALENDAR row `2026-11-20` ("SPEC, then a first run ... who bought US corporate bonds in the AI-era issuance wave"). Page context:
`docs/index.html` §04, row "AI build-out funding", bullet *Bonds*, and the claims-ledger row on long money (C-139). Feeds
`2026-08-22-D2-Who-Holds-The-AI-Paper.md` and `Funding_Identity_First_Principles.md`. House style follows
`_research/2026-10-26-Census-Public-Pensions-Spec.md`. Script `bin/z1_corporate_bond_holders.py`, outputs `data/z1_corporate_bond_holders/`,
vintages `data/vintages/z1_corporate_bond_holders/`, check.sh guard **M26**. The rulings at the end are the record; this body applies
round 1 (R1-1 to R1-11). Where the body and a ruling differ, the ruling wins.*

*"Observed" means seen by the spec author on 26 Oct 2026 (5 requests between 19:43 and 19:47 UTC, 2.10; this rewrite made no request)
or in the repository at that time. "Relayed" means taken from a ruling, a review, a project file or general knowledge, not re-read at
source by the spec author. **The blind rule was broken during review (2.11). Nothing about holder shares is tested; the only registered
statements are about revision (4.6).***

## 0. Goal, and what the result can and cannot say

- **Record** the Fed's quarterly transactions (net acquisition) in corporate and foreign bonds by every holder sector of table F3.5.t,
  the issuer side (net issuance) of the same table, and the level table F3.5.s, 2017Q1 to the latest quarter, per Z.1 release (vintage).
- **Describe**, with rules fixed here, issuer and holder shares of the all-sector net in the window 2024Q1-2026Q2 (`wave`), against
  2017Q1-2019Q4 (`pre1719`), with dollars beside every share, the calendar-year path, level shares, and how far the wave shares move
  between releases. These are reported statistics, not verdicts (R1-1): the wave shares were seen during review.
- **Register** three statements about revision only (SREV, SREV-F, SREV-R; 4.6), scored on the 10 Dec 2026 release, which nobody has seen.

**The plain answer to the practitioner claim (R1-3; a claim, not ours, that US insurers are the main source of take-up of the AI-era
investment-grade supply; never named or cited).** What Z.1 can say: over 2024Q1-2026Q2, US insurers' net acquisition of corporate and
foreign bonds was about a third of the all-sector net (33.26% of 2,228,428 $mn on the unadjusted basis, relayed from the supervisor's
check; the build recomputes it), behind registered funds and the rest of the world. What Z.1 cannot say: the instrument is all corporate
and foreign bonds (investment grade and high yield, financial issuers, private-label ABS and MBS, and foreign bonds held by US residents),
so a share of it says nothing about who took the AI issuers' bonds, which were a few percent of the denominator (supervisor's statement in
R1-3; not computed by this build; O-10).

**It can say** which holder sectors, in the Fed's own sector accounts, took the net increase in the whole corporate and foreign bond market
in 2024Q1-2026Q2, and what was issued, net, by nonfinancial companies, financial companies and foreign issuers whose bonds US residents
acquired. Flows and levels are MEASURED (Fed estimates on Fed definitions; revised every release). Shares are IDENTITY on MEASURED inputs.
The household line is a residual (C-098) and the least secure number in every table.

**It cannot say:**
- **anything about the AI companies' bonds as such.** Z.1 has no issuer-name line; "wave" means the calendar window and nothing else;
- **who bought any deal, or a composition of buyers.** A flow is purchases minus sales minus redemptions. A sector can take a whole new
  issue and still show a small or negative net flow. Shares of a net can be negative or above 100% (R1-4);
- **the full insurance-group position (R1-7).** Only uncollateralised coinsurance moves the bonds to the reinsurer, which is in the rest of
  the world if it is offshore. Under funds withheld and modified coinsurance the US insurer keeps investing the assets, and US captives are
  brought into the life sector (Board FEDS Note, 12 Oct 2018; relayed). The size of each structure is unknown, so **the insurer line may be
  understated by an unknown amount**. Bonds held through funds sit in the fund sectors;
- **why anyone acted, or anything about spreads or prices.** No flow is described as a cause.

**Required README sentence 2 (the one denial sentence, exempt from G14, verbatim):** "These are flows for the whole US corporate and
foreign bond market; Z.1 has no line for the AI companies' bonds, so nothing here shows who holds AI debt or who bought any deal, and a
net acquisition is purchases minus sales and redemptions, not purchases."

**Required disclosure sentence (README section 3 and SOURCES.md, verbatim, R1-1):** "The wave-window shares were seen during review,
before this spec was committed, so they are reported, not tested."

## 1. Hard requirements

- **R1. Free public data only (E-005).** Host allowlist: `www.federalreserve.gov` only. Refused before the request: every other host,
  explicitly any host ending `sec.gov`, FRED/ALFRED, `home.treasury.gov` and `ticdata.treasury.gov` (TIC is typed constants, R1-5). No API key.
- **R2. User-Agent** exactly `Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)`; header
  `Accept-Encoding: identity`. The script asserts the UA holds no `@`. Never send an email address, a name, `SEC_UA` or `CLAUDE_CODE_USER_EMAIL`.
- **R3. Crawl conditions.** GET only, no redirect followed, **no retry of any kind**, timeout 300 s. Mode `fetch --release YYYYMMDD`
  makes exactly **1 request** (the release's `z1_csv_files.zip`); at most 2 runs per calendar day, at least 3 s apart. The release landing
  page is never fetched (`/releases/z1/20260911/default.htm` answered 404 to the spec author, 2.10).
- **R3a. STOP latch and "not yet posted" (R1-10).** **A 404 on a release zip** prints `NOT POSTED <path>`, exits 3, writes no STOP and
  retries nothing (the 10 Dec URL is inferred, O-6). **Any other non-200** (any 3xx included), or a 200 body that is empty, HTML (starts,
  after whitespace, with `<!` or `<html`, case-insensitive) or not a zip (first four bytes not `PK\x03\x04`), writes
  `data/vintages/z1_corporate_bond_holders/STOP_z1cb`, created exclusively (`open(..., "x")`) with five `name: value` lines: `status`,
  `utc_time`, `url_path`, `retry_after`, `body_head` (first 300 bytes, escaped). With the latch present no request is made; the run prints
  `STOP present: <file>` and exits 2. **Only a person deletes a STOP file. No agent deletes, renames or overwrites one, the builder
  included.** A timeout or connection error prints `FAIL network <path>`, exits 3, writes no STOP and retries nothing.
- **R3b. Content tests (FAIL rows in `checks.csv`, not STOP).** The zip holds the 14 members of R4; every series code of 2.2 is in its
  file's header; each code's dictionary line number and text match 2.2 (C03). The build still writes its outputs; success requires no FAIL.
- **R4. Vintages and zip handling.** Members are read **by exact name** with `ZipFile.read(name)` and written to fixed file names; the
  script never calls `extractall` and never builds a path from an archive member name. Each release is cached as
  `data/vintages/z1_corporate_bond_holders/<YYYYMMDD>/`: `F3_5_t_tu.csv`, `F3_5_t.csv`, `F3_5_s.csv`, `S1281_1_t_tu.csv`, `S1281_1_s.csv`,
  `S1281_2_t_tu.csv`, `S1281_2_s.csv`, the seven matching `data_dictionary/*.txt`, and `provenance.csv` (each member's sha256 and bytes;
  the zip's sha256, bytes and `Last-Modified`). Committed, as `data/vintages/z1_fund_tsy_20260911/` already is; the zip is not kept.
- **R5. Release key** = the dated folder in the zip URL (`20260911`); FAIL if it differs from the zip's `Last-Modified` date by more than 3 days.
- **R6. Wording (G14).** No causal, motive or flow-direction wording in README.md except the denial sentence. The README says "net
  acquisition", "net acquired" or "took", never "bought", "buyer(s)" or "demand"; "the 2024Q1-2026Q2 window", never "the AI bond wave";
  and never calls the net shares a composition of buyers (R1-4).
- **R7. Code ownership.** `bin/z1_corporate_bond_holders.py` is new, standard library only, and reads no project file other than its own
  cache and vintages. No existing script changes, apart from a new warn-only guard M26 in `bin/check.sh`.
- **R8. Parsing and numbers (R1-8 fix 5).** CSVs read with the `csv` module, UTF-8 with BOM tolerated. Columns are selected **by series
  code (with its `.Q` suffix) from the header row, never by position**. Dates are `YYYY:QN`. `ND` or blank is missing, never zero (C09).
  Values are millions of dollars, read as `decimal.Decimal` in a context of **precision 28**, summed in Decimal. **Every comparison with a
  threshold or tolerance uses the unrounded Decimal**; half-even rounding happens only at write time: `_usd_mn` 3 decimals, `_pct` and
  `_pp` 3, `offset_ratio` 4.
- **R9. Post-registration fixes** go in SOURCES.md "Builder decisions" with the old value beside the new, never in the README.
  **No registered number changes after round 1 (R1-11).**
- **R10. No pooling across sources.** No output cell combines a Z.1 figure with another source, with one exception: check CREF2 in
  `checks.csv`, which sets typed TIC constants beside the build's rest-of-world flows and never reaches a share table.

## 2. Data

### 2.1 What F3.5 is (observed unless marked)

Z.1 table **F3.5.t** "Corporate and foreign bonds" (transactions) and **F3.5.s** (levels), the old F.213 and L.213 (`z1_table_mapping.csv`
in `data/vintages/z1_equities_2026Q2/`, observed). `F3_5_t_tu` carries FU codes, "transactions, not seasonally adjusted" (quarterly
flows); `F3_5_t` FA codes, "transactions at a seasonally adjusted annual rate"; `F3_5_s` levels, "amounts outstanding end of period, not
seasonally adjusted". **Level valuation (R1-8 fix 7):** the dictionary says "market value" for every LM code; for FL codes it states no
valuation basis, so they are labelled `fl_unspecified`, never "book" or "par". Each file has 305 data rows, 1945:Q4 to 2026:Q2, in the 11
Sep 2026 release. Liabilities (issuers) are lines 1-12, assets (holders) lines 13-53; F3_5_s adds line 54, instrument discrepancies.
Life insurers' general and separate accounts are in the sector tables `S1281_1` and `S1281_2`, line 8 of each.

### 2.2 Every series used (R1-8 fix 4; all codes carry the `.Q` suffix; FA codes are the FU codes with `FA` for `FU`, same lines)

| Line | FU code | Level code | Sector (dictionary wording, shortened) | Role | Group |
|---|---|---|---|---|---|
| 1 | FU893163005.Q | FL893163005.Q | All sectors; liability | issuer_total | `iss_total` |
| 2 | FU103163005.Q | FL103163005.Q | Nonfinancial corporate business; corporate bonds | issuer | `iss_nfc` |
| 3 | FU793163005.Q | FL793163005.Q | Domestic financial sectors (= lines 4-11) | issuer | `iss_domfin` |
| 4 | FU763163005.Q | FL763163005.Q | US-chartered depository institutions | issuer_detail | `iss_dom_banks` |
| 5 | FU673163005.Q | FL673163005.Q | Issuers of asset-backed securities | issuer_detail | `iss_dom_abs` |
| 6 | FU613163005.Q | FL613163005.Q | Finance companies | issuer_detail | `iss_dom_finco` |
| 7 | FU643163075.Q | FL643163075.Q | Mortgage REITs, excluding FHLB advances | issuer_detail | `iss_dom_mreit` |
| 8 | FU453163003.Q | FL453163003.Q | Business development companies; corporate bonds | issuer_detail | `iss_dom_bdc` |
| 9 | FU663163003.Q | FL663163003.Q | Security brokers and dealers | issuer_detail | `iss_dom_bd` |
| 10 | FU733163005.Q | FL733163005.Q | Holding companies | issuer_detail | `iss_dom_hc` |
| 11 | FU503163003.Q | FL503163003.Q | Other financial business (proceeds down-streamed to broker-dealer subsidiaries) | issuer_detail | `iss_dom_ofb` |
| 12 | FU263163005.Q | LM263163005.Q | Rest of the world; bonds; liability (foreign bonds held by US residents) | issuer | `iss_row` |
| 13 | FU893063005.Q | FL893063005.Q | All sectors; asset | holder_total | `total` |
| 14 | FU153063005.Q | LM153063005.Q | Households and nonprofit organizations | holder | `hh_residual` |
| 15 | FU123063003.Q | LM123063003.Q | Equity REITs | holder | `other` |
| 16 | FU313063005.Q | FL313063005.Q | Federal government | holder | `other` |
| 17 | FU213063003.Q | LM213063003.Q | State and local governments | holder | `other` |
| 18 | FU713011525.Q | FL713011525.Q | Central bank; other US reserves, foreign securities | holder | `other` |
| 19 | FU763063005.Q | LM763063005.Q | US-chartered depository institutions incl. IBFs | holder | `banks` |
| 20 | FU763063605.Q | LM763063605.Q | of which private MBS and CMOs | subline | `none` |
| 21 | FU763063095.Q | LM763063095.Q | of which excluding private MBS and CMOs | subline | `none` |
| 22 | FU753063005.Q | LM753063005.Q | Foreign banking offices in the US incl. IBFs | holder | `banks` |
| 23 | FU743063005.Q | LM743063005.Q | Banks in US-affiliated areas | holder | `banks` |
| 24 | FU473063005.Q | LM473063005.Q | Credit unions | holder | `banks` |
| 25 | FU473063605.Q | LM473063605.Q | of which MBS and other ABS | subline | `none` |
| 26 | FU473063095.Q | LM473063095.Q | of which excluding MBS and other ABS | subline | `none` |
| 27 | FU513063005.Q | LM513063005.Q | Property-casualty insurers incl. US residual-market reinsurers | holder | `ins_pc` (in `ins`) |
| 28 | FU513063605.Q | LM513063605.Q | of which MBS and other ABS | subline | `none` |
| 29 | FU513063095.Q | LM513063095.Q | of which excluding MBS and other ABS | subline | `none` |
| 30 | FU543063005.Q | LM543063005.Q | Life insurers | holder | `ins_life` (in `ins`) |
| 31 | FU543063675.Q | LM543063675.Q | of which general-account MBS and other ABS incl. US captive reinsurers | subline | `none` |
| 32 | FU543063095.Q | LM543063095.Q | of which excluding MBS and other ABS | subline | `none` |
| S1281_1 l.8 | FU543063075.Q | LM543063075.Q | Life insurers, general accounts | subline | `ins_life_ga` |
| S1281_2 l.8 | FU543063085.Q | LM543063085.Q | Life insurers, separate accounts | subline | `ins_life_sa` |
| 33 | FU573063005.Q | LM573063005.Q | Private pension funds | holder | `pen_private` (in `pen`) |
| 34 | FU343063005.Q | LM343063005.Q | Federal government pension funds | holder | `pen_federal` (in `pen`) |
| 35 | FU223063045.Q | LM223063045.Q | State and local DB pension funds | holder | `pen_sl` (in `pen`) |
| 36 | FU633063005.Q | FL633063005.Q | Money market funds | holder | `other` |
| 37 | FU653063005.Q | LM653063005.Q | Mutual funds | holder | `funds_mutual` (in `funds`) |
| 38 | FU553063003.Q | LM553063003.Q | Closed-end funds | holder | `funds_cef` (in `funds`) |
| 39 | FU563063003.Q | LM563063003.Q | Exchange-traded funds | holder | `funds_etf` (in `funds`) |
| 40 | FU463063005.Q | LM463063005.Q | Interval and tender-offer funds | holder | `funds_interval` (in `funds`) |
| 41 | FU623063005.Q | LM623063005.Q | Hedge funds (domestic), net of short sales | holder | `hedge_funds` (in `private_funds`) |
| 42 | FU443063000.Q | LM443063000.Q | Private debt funds | holder | `private_debt_funds` (in `private_funds`) |
| 43 | FU403063005.Q | LM403063005.Q | Government-sponsored enterprises | holder | `gse_bd` |
| 44 | FU403063605.Q | LM403063605.Q | of which MBS and other ABS | subline | `none` |
| 45 | FU403063095.Q | LM403063095.Q | of which excluding MBS and other ABS | subline | `none` |
| 46 | FU613063003.Q | LM613063003.Q | Finance companies | holder | `other` |
| 47 | FU643063073.Q | LM643063073.Q | Mortgage REITs | holder | `other` |
| 48 | FU663063005.Q | LM663063005.Q | Security brokers and dealers (net) | holder | `gse_bd` |
| 49 | FU733063003.Q | LM733063003.Q | Holding companies | holder | `other` |
| 50 | FU503063005.Q | FL503063005.Q | Other financial business incl. financial stabilization programs | holder | `other` |
| 51 | FU263063005.Q | LM263063005.Q | Rest of the world; US corporate bonds; asset | holder | `row` |
| 52 | FU263063603.Q | LM263063603.Q | of which US MBS and other ABS | subline | `none` |
| 53 | FU263063095.Q | LM263063095.Q | of which US corporate bonds excluding MBS and other ABS | subline | `none` |
| 54 | (none) | LM903063003.Q | Instrument discrepancies (level only) | discrepancy | `discrepancy` |

That is 53 FU codes, 53 FA codes, 54 level codes, and four S1281 codes (observed in the dictionaries). The **28 leaf holder lines**
(14-19, 22-24, 27, 30, 33-43 except sub-lines, 46-51) each belong to exactly one of nine groups: `ins`, `pen`, `funds`, `row`, `banks`,
`hh_residual`, `private_funds`, `gse_bd`, `other`. Sub-lines are never added to a group or a total; they are used for identities and,
for GA and SA only, printed under the life line (R1-9). Issuer details (lines 4-11) are printed under `iss_domfin`, never added to it.
The derived row `hh_plus_private_funds` is `hh_residual` plus `private_funds`, printed beside them, never counted in the nine.

### 2.3 Identities (observed on 2017Q1-2019Q4; the build checks every quarter from 1990:Q1, FAIL from 2017:Q1, WARN before; R1-8 fix 6)

- Flows (both bases): the 28 leaves sum to line 13 within 1 $mn; line 1 = line 13 exactly; lines 2 + 3 + 12 = line 1; lines 4-11 =
  line 3; each sub-line pair sums to its parent exactly (19 = 20 + 21; 24 = 25 + 26; 27 = 28 + 29; 30 = 31 + 32; 43 = 44 + 45; 51 = 52 + 53);
  general + separate accounts = line 30 exactly.
- **Levels (R1-8 fix 3):** the 28 leaf levels sum to **line 13** within 1 $mn, and **line 54 = line 1 - line 13** exactly (re-checked by the
  spec author for this rewrite on the cached 11 Sep file, 2017Q1-2019Q4). Line 1 minus line 13 was -290,252 (2017Q4), +357,667 (2018Q4)
  and -599,833 (2019Q4) $mn. **The first draft wrongly said line 13 is not the sum of the leaves**; the level-share denominator is that
  sum (`holders_total_usd_mn`, equal to line 13 within rounding), and line 54 is printed beside it.
- Bases: over each calendar year 2017-2019, sum(FA)/4 equals sum(FU) within 3 $mn on all 53 lines; they differ only within a year.

### 2.4 Units and bases

FU (unadjusted, millions per quarter) is the basis of every headline and registered statement. FA/4 (`fa_div4`) is printed beside it in
`quarterly.csv`, `windows.csv` and `comparisons.csv` (descriptive only; the T1S sensitivity test is dropped, R1-6). A level change minus
the window's flow is revaluation **plus other volume changes** (C-119), written `change_minus_flow_usd_mn`, never called revaluation alone.

### 2.5 Which lines the Fed estimates (relayed; OPEN O-1)

Relayed: insurers come from statutory statements, banks from Call Reports, pensions from Form 5500 and surveys, registered funds from ICI
data, domestic hedge funds and private debt funds from Form PF (whose lag makes the latest one or two quarters Fed projections), rest of
the world largely from TIC. The 2026Q2 mutual-fund Treasury stock "was an estimate in the 11 Sep vintage" (CALENDAR row 2026-12-10; not
checked for line 37). **Households and nonprofits are the residual** (relayed Z.1 convention, consistent with the exact identity of 2.3):
line 14 absorbs every error in the other 27 lines plus holders the Fed cannot place, possibly offshore funds that custody-based TIC
reporting misattributes (C-124, on Treasuries). Domestic hedge funds and private debt funds are their own lines (41, 42).

### 2.6 TIC: typed constants in one check, never fetched (R1-5, R1-6)

Background (observed by the spec author on Treasury pages, 2.10): TIC Form S ended in 2023; monthly foreign transactions now come from the
CSLT dataset, which combines SLT reports with Federal Reserve Board staff estimates, the same inputs and staff behind Z.1's rest-of-world
line; and TIC "corporate bonds include those issued by ... state and local governments (including municipal bonds)", which Z.1 line 51
excludes. So TIC is not independent of Z.1 and a gap is expected. **The build fetches nothing from Treasury.** CREF2 (section 8) types
in the Treasury TIC press-release figures for foreign net purchases of US corporate bonds, private plus official: **304.5 $bn (2024) and
392.4 $bn (2025)**, from release sb0662 (verified verbatim by the supervisor, relayed; not read by the spec author).

### 2.7 (retired by R1-6: the N-PORT deal sentence is removed; no N-PORT figure appears in any output or the README)

### 2.8 Release schedule and revisions

First build: the 11 Sep 2026 release (zip `Last-Modified` 11 Sep 2026 16:00:19 GMT, observed). Next, carrying 2026Q3: Thursday 10 Dec 2026
(relayed, CALENDAR row 2026-12-10); zip URL inferred as `/releases/z1/20261210/z1_csv_files.zip` (O-6; a 404 there means "not yet
posted", R3a). Z.1 revises history at every release; the `wave` window stays **2024Q1-2026Q2** in every later release, and 2026Q3 enters
only `wave_ext`.

### 2.9 Licence

US government works (17 U.S.C. 105; relayed). Citation in every CSV's `# source:` line and the README: Board of Governors of the Federal
Reserve System, Financial Accounts of the United States (Z.1), release <YYYYMMDD>, tables F3.5 and S1281; CREF2 also cites Treasury release sb0662.

### 2.10 Requests (goes to SOURCES.md, not the README)

**By the spec author, first draft, 26 Oct 2026** (5 requests, all GET, sequential, at least 2.5 s apart, User-Agent as R2,
`Accept-Encoding: identity`, no redirect followed, no retry, no 403 or 429). **This rewrite made no request.**

| UTC | URL | Status | Bytes | Note |
|---|---|---|---|---|
| 19:43:08 | `https://www.federalreserve.gov/releases/z1/20260911/z1_csv_files.zip` | 200 | 8,336,582 | sha256 `b63af9755437df0fb88b7cf346f8f9eaeb22bf1aa2b5df1709334135c43de4b6`; 616 members |
| 19:45:22 | `https://home.treasury.gov/data/treasury-international-capital-tic-system` | 200 | 78,207 | read for the Form S and CSLT notes; not used by the build |
| 19:45:25 | `https://ticdata.treasury.gov/resource-center/data-chart-center/tic/Documents/cslt.zip` | 200 | 8,910,770 | metadata only read; not used by the build (R1-6) |
| 19:46:30 | `https://www.federalreserve.gov/releases/z1/20260911/default.htm` | **404** | 82,134 | not retried; never fetched by the build |
| 19:46:33 | `https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FA653063005&t=F.213` | 200 | 73,549 | body is the Financial Accounts Guide's "Error" page; not retried (O-1) |

**By others during review (relayed from the round-1 rulings, not logged by the spec author):** Grok read the published F3.5.t table on
federalreserve.gov; the supervisor read the cached 11 Sep zip and verified Treasury release sb0662. No request by anyone went to sec.gov or FRED.

### 2.11 What was seen of the answer before any build, and by whom (SOURCES.md repeats this)

- **Grok (attack parcel, which carried no blind clause):** read the published seasonally adjusted F3.5.t table and reported wave shares
  of about 32% (life plus P&C insurers), 47% (registered funds), 41% (rest of the world) and -35% (household residual), and rest-of-world
  2024 net acquisition of 298.8 $bn on the SA table.
- **The supervisor:** confirmed from the cached 11 Sep zip, unadjusted FU sums: insurers 33.26% of 2,228,428 $mn over the ten wave
  quarters; 2024 37.12% (224,689 + 70,237 of 794,490); 2025 35.67% (221,483 + 65,834 of 805,405).
- **The second reviewer (Sonnet):** stayed blind on 2024-26 and computed 2017-2019 shares: funds 39.98%, insurers 34.36%, rest of the world
  31.23% of 1,329,619 $mn (recorded in SOURCES.md as observed during review).
- **The spec author:** no holder share for any window and no 2024-26 value, in the first draft or this rewrite. Read: the dictionaries; the
  2.3 identity residuals on 2017Q1-2019Q4 (and, for this rewrite, the leaf-versus-line-13 and line-54 residuals on the same quarters);
  the FA/4-versus-FU annual gaps for 2017-2019; the flows of lines 18, 41, 42 and 50 for 2020Q1-2021Q4; a count of `ND` cells (zero);
  CSLT metadata only. The first draft's priors (the 50% line) are not blind either.
- **Already in the project before this spec (relayed from the repo):** D2 §2.1 level shares at 2026Q1 (rest of the world 28.6%, life
  22.9%, P&C 5.2%, mutual funds 15.0%, pensions 9.4%); N2c §4 and `data/series.tsv`, all-sector net issuance (FU893163005.Q) $505bn
  (2023), $728bn (2024), $705bn (2025), $335bn (2026Q1), June 2026 release.

**Consequence (R1-1):** no holder-share statement can be scored as pre-registered. The only registered statements (4.6) concern the
10 Dec release, which nobody had seen when they were fixed.

## 3. Method

0. **Spec first (R1-8 fix 8).** This spec, with the rulings, is committed under `_research/` before the first `fetch`; SOURCES.md cites that
   commit, and success criterion 11 checks the order.
1. **Fetch** (`fetch --release 20260911`, later `--release 20261210`) under R1-R5; every request logged.
2. **Parse** the seven CSVs under R8; select the codes of 2.2 by header; map each to (line, table, role, group) from a literal table in the
   script (pasted from 2.2, never inferred from dictionary text).
3. **Quarterly ledger** (`quarterly.csv`): every flow code of 2.2, every quarter 2017:Q1 to the latest, bases `fu` and `fa_div4`.
   **Levels** (`levels.csv`): every level code, same quarters, `valuation` = `lm_market` for LM codes, `fl_unspecified` for FL codes.
4. **Windows** (inclusive, whole quarters):

| window | from | to | n | use |
|---|---|---|---|---|
| `wave` | 2024:Q1 | 2026:Q2 | 10 | headline and registered statements; fixed in every release |
| `pre1719` | 2017:Q1 | 2019:Q4 | 12 | pre-wave comparison (README) |
| `pre2223` | 2022:Q1 | 2023:Q4 | 8 | CSVs only, not in the README (R1-6, O-8) |
| `wave_ext` | 2024:Q1 | latest | 11 on 10 Dec | exploratory; not written on the 11 Sep release |
| `y2017` ... `y2025` | Q1 | Q4 | 4 | path (C-070) |
| `y2026h1` | 2026:Q1 | 2026:Q2 | 2 | path |

   **Why these windows.** 2017-2019: the last full stretch before 2020, with no pandemic issuance surge or Fed credit facilities. 2020 is
   out (dash for cash, record issuance, the corporate credit facilities); so is 2021 (the secondary-market facility sold its bonds during
   2021, relayed). 2022-2023 had low net issuance, so its shares rest on a small denominator.
5. **Shares of the net.** For each window, basis and side: `flow_usd_mn` = the sum of the group's quarterly flows; `avg_per_quarter_usd_mn`
   = that sum / `n_quarters` (R1-8 fix 10); `share_of_total_pct` = 100 x the group's window sum / the total line's window sum (line 13 for
   holders, line 1 for issuers; equal by 2.3). **A window share is always a ratio of window sums, never a mean of quarterly shares**
   (G6 mutant). Negative group flows stay negative; the nine holder groups (three issuer groups) sum to 100 (C13). No share is written if
   the window total is not positive (`stability_flag = void_nonpositive_total`).
6. **Shares of the positive flows (R1-4).** `positive_total_usd_mn` = the sum over the nine holder groups (three issuer groups) of each
   group's window flow where positive. `share_of_positive_pct` = 100 x flow / `positive_total_usd_mn` for every row whose window flow is
   positive (members and sub-lines included, same denominator); blank where the flow is zero or negative (O-9).
7. **Offset ratio and stability flag.** `offset_ratio` = |sum of the total line| / sum over the 28 leaves of |leaf window sum|; below 0.5
   every share in that window gets `stability_flag = offsetting`, else `ok`.
8. **Headline** (`headline.csv`, R1-1, fu basis, `wave` only): `ins_share_wave_pct`; `group_share_wave_pct` for each of the nine groups and
   `hh_plus_private_funds`; `iss_share_wave_pct` for `iss_nfc`, `iss_domfin`, `iss_row`; `rank_wave` for each of the seven ranked groups
   (`ins`, `pen`, `funds`, `row`, `banks`, `hh_residual`, `private_funds`, by window flow, 1 = largest). No verdict word is written anywhere.
9. **Level shares** (`level_shares.csv`) at 2016:Q4, 2019:Q4, 2021:Q4, 2023:Q4 and the latest quarter: each group's level over the sum of
   the 28 leaf levels, line 54 beside it. **Level change** (`level_change.csv`): per window, the group level at the quarter before the window
   starts and at its end, the window flow, and `change_minus_flow_usd_mn`.
10. **Comparisons** (`comparisons.csv`): `wave` minus `pre1719` and minus `pre2223`, every group, both bases, in pp. Descriptive.
11. **Revisions** (`revisions.csv`): regenerated on every build, never appended, from every adjacent pair of cached release folders, for every
    window present in both, every group, both bases. **Registered statements** (`registered.csv`): 4.6.

## 4. Questions, fixed in advance (answers in `headline.csv`, `windows.csv`, `comparisons.csv`, `level_shares.csv`, `registered.csv`)

**4.0 Noise.** No sampling error is published for Z.1 and nothing about shares is tested, so there is no MDE to state (C-090). What bounds
any reading is revision (step 11), estimation of individual lines (2.5) and the residual (C-098). The 2.0 pp threshold of 4.6 has **no
measured prior** and is not calibrated (R1-11).

- **Q1** Levels and ledger (`quarterly.csv`, `levels.csv`).
- **Q2 Issuance first (R1-3):** nonfinancial corporate, domestic financial (with its eight details) and rest-of-world (foreign bonds US
  residents acquired) net issuance in `wave`, in $mn, per quarter and as shares of the net.
- **Q3 Holder shares in `wave`:** the nine groups and their members, dollars, per-quarter average, share of the net, share of the positive
  flows, offset ratio; `ins_share_wave_pct` and `rank_wave`. Reported, not tested (R1-1).
- **Q4 Life insurers:** general and separate accounts printed separately under the life line (R1-9).
- **Q5 Against `pre1719`** (`comparisons.csv`); `pre2223` in the CSVs only.
- **Q6 The path:** calendar years 2017-2025 and 2026H1; no README sentence compares two windows unless the yearly rows between them are in
  the same table (C-070).
- **Q7 Level shares** at five quarter-ends; level change minus flow.
- **Q8 Reference checks:** CREF1 and CREF2 (section 8).
- **Q9 Revisions** between releases, and the three registered statements (4.6).
- **Not asked:** any figure for named issuers or deals; any holder-share verdict; anything about spreads or prices.

### 4.6 Registered statements (fixed by ruling R1-2, 26 Oct 2026; scored on the first release carrying 2026:Q3)

**Canonical text** (the script holds `SPEC_PREREG_SHA256` and refuses to write `registered.csv` if its own constants do not reproduce this
text byte for byte; one line per statement, LF endings):

```
SREV|group=ins|num=FU543063005.Q+FU513063005.Q|den=FU893063005.Q|window=2024:Q1..2026:Q2|basis=fu|base=20260911|new=first_release_with_2026:Q3|STABLE=abs_delta<2.0pp|MOVED=abs_delta>=2.0pp|PENDING=no_new_release|compare=unrounded_decimal_prec28
SREV-F|group=funds|num=FU653063005.Q+FU553063003.Q+FU563063003.Q+FU463063005.Q|den=FU893063005.Q|window=2024:Q1..2026:Q2|basis=fu|base=20260911|new=first_release_with_2026:Q3|STABLE=abs_delta<2.0pp|MOVED=abs_delta>=2.0pp|PENDING=no_new_release|compare=unrounded_decimal_prec28
SREV-R|group=row|num=FU263063005.Q|den=FU893063005.Q|window=2024:Q1..2026:Q2|basis=fu|base=20260911|new=first_release_with_2026:Q3|STABLE=abs_delta<2.0pp|MOVED=abs_delta>=2.0pp|PENDING=no_new_release|compare=unrounded_decimal_prec28
```

**sha256 of that text: `e4e306b4731b97f94b5e5d5a0acab38ee1287a684ecb9e438352663f0e621f99`** (755 bytes).

In words: on the first release carrying 2026:Q3 (expected 10 Dec 2026), each group's wave share (100 x window sum of its codes / window
sum of FU893063005.Q, 2024:Q1-2026:Q2, unadjusted) is compared with the same share on the 11 Sep 2026 release. **SREV: "insurers' wave
share moves by less than 2.0 pp between the 11 Sep and 10 Dec 2026 releases"**; SREV-F the same for registered funds (lines 37-40);
SREV-R for the rest of the world (line 51). `STABLE` if |delta| < 2.0 pp, `MOVED` if >= 2.0 pp, on unrounded Decimals; `PENDING` until
that release is cached. A `MOVED` is a result, written beside the old value; it voids nothing.

**CALENDAR row (text, for the builder to add at landing):** `2026-12-10`, "Z.1 2026Q3 release: python3 bin/z1_corporate_bond_holders.py
fetch --release 20261210 (a 404 means not yet posted: retry on a later day, by hand), then build; read registered.csv (SREV, SREV-F,
SREV-R: STABLE or MOVED) and revisions.csv for window wave; the window stays 2024Q1-2026Q2".

## 5. Outputs

**Script `bin/z1_corporate_bond_holders.py`.** Modes `fetch --release YYYYMMDD`, `build` (offline, byte-identical on re-run, over every
cached release), `selftest` (synthetic, no network, under 20 s). Committed files in `data/z1_corporate_bond_holders/`; each CSV begins with
one `# source:` line (2.9 citation, releases used, retrieval dates from `fetch_log.csv`).

**Header allowlist, canonical text.** One line per file, `<name>:<headers comma-joined, no spaces>`, each ending in LF, in this order.
The script holds `SPEC_ALLOW_SHA256`; **`bin/check.sh` holds its own literal copy of these twelve lines** and never reads them from the
script. G12 and M26 skip the `# source:` line.

```
quarterly.csv:release,quarter,series_code,line,table,role,group,basis,value_usd_mn
levels.csv:release,quarter,series_code,line,table,role,group,valuation,level_usd_mn
windows.csv:release,window,from_quarter,to_quarter,n_quarters,side,role,group,basis,flow_usd_mn,avg_per_quarter_usd_mn,share_of_total_pct,total_usd_mn,share_of_positive_pct,positive_total_usd_mn,offset_ratio,stability_flag
level_shares.csv:release,quarter,group,level_usd_mn,share_of_holders_pct,holders_total_usd_mn,discrepancy_usd_mn
level_change.csv:release,window,group,level_start_usd_mn,level_end_usd_mn,flow_usd_mn,change_minus_flow_usd_mn
headline.csv:release,statistic,window,basis,group,flow_usd_mn,value,unit
registered.csv:statement_id,group,window,basis,release_base,release_new,share_base_pct,share_new_pct,abs_delta_pp,threshold_pp,label
comparisons.csv:release,side,group,basis,window_a,window_b,share_a_pct,share_b_pct,change_pp
revisions.csv:release_prev,release_new,window,side,group,basis,flow_prev_usd_mn,flow_new_usd_mn,share_prev_pct,share_new_pct,change_pp
checks.csv:check_id,description,expected,observed,status
vintages.csv:release,url_path,sha256,bytes,last_modified,retrieved_utc
fetch_log.csv:utc_time,host,path,status,bytes,sha256,last_modified
```

**sha256 of that text (1,243 bytes, 12 lines): `da0c7635f50184f044c8ebc04f2affceef805fb7d015ef023a4ca530c52860f9`** (computed by the spec author for this rewrite).
Superseded: `2244b2fdf5d703d7f1ef14868fd08e0dccad9b717f94c61bc2a73d74214f424f` (first draft, with `tests.csv` and `tic_check.csv`). A
builder who needs a column changes this text and its hash first, logs it in Builder decisions, and tells the supervisor.

**Allowed values.** `role` in {issuer_total, issuer, issuer_detail, holder_total, holder, member, derived, subline, discrepancy} (`member`
for a group's members such as `ins_life` in `windows.csv`; `derived` for `hh_plus_private_funds`); `side` in {holder, issuer}; `basis` in
{fu, fa_div4}; `valuation` in {lm_market, fl_unspecified}; `table` in {F3.5, S1281_1, S1281_2}; `group` in {total, ins, ins_life, ins_pc,
ins_life_ga, ins_life_sa, pen, pen_private, pen_federal, pen_sl, funds, funds_mutual, funds_cef, funds_etf, funds_interval, row, banks,
hh_residual, private_funds, hedge_funds, private_debt_funds, hh_plus_private_funds, gse_bd, other, discrepancy, none, iss_total, iss_nfc,
iss_domfin, iss_dom_banks, iss_dom_abs, iss_dom_finco, iss_dom_mreit, iss_dom_bdc, iss_dom_bd, iss_dom_hc, iss_dom_ofb, iss_row} (`none`
only in `quarterly.csv` and `levels.csv`); `window` in {wave, pre1719, pre2223, wave_ext, y2017 ... y2025, y2026h1}; `stability_flag`
in {ok, offsetting, void_nonpositive_total}; `statistic` in {ins_share_wave_pct, group_share_wave_pct, iss_share_wave_pct, rank_wave};
`unit` in {pct, rank}; `statement_id` in {SREV, SREV-F, SREV-R}; `label` in {STABLE, MOVED, PENDING}; `status` in {PASS, WARN, FAIL,
INFO}. Keys unique: `windows.csv` (release, window, side, group, basis); `headline.csv` (release, statistic, group); `registered.csv`
(statement_id, release_new). **No output carries HELD, FALSIFIED, NOT_HELD, INSIDE_BAND, ABOVE_BAND or BELOW_BAND** (R1-1).

- **`README.md`** (generated; G14 scans it), plain words, in this order:
  1. **Opening (R1-1):** two sentences: what the table is ("which kinds of holders took the net increase in US corporate and foreign bonds
     from 2024Q1 to 2026Q2, in the Federal Reserve's financial accounts") and the result: US insurers' share of the net
     (`ins_share_wave_pct`) and their rank among seven groups (`rank_wave`), behind the groups that rank above them, named.
  2. The denial sentence of section 0.
  3. The disclosure sentence of section 0, then one line on what is registered (4.6) and when it is scored.
  4. **What the net was made of, before any holder (R1-3):** nonfinancial corporate, domestic financial and rest-of-world issuance (foreign
     bonds US residents acquired) as dollars and shares of the net, and the sentence that the instrument includes investment grade and high
     yield, financial issuers, private-label ABS and MBS and foreign bonds, so a share says nothing about the AI issuers' bonds, which were a
     few percent of the denominator (supervisor's estimate, round 1; not computed here).
  5. The wave holder table: nine groups and members, $bn, per-quarter average, share of the net, share of the positive flows; general and
     separate accounts printed under life insurers (R1-9); the one-sentence explanation (R1-4, R1-8 fix 11): "A share can be below zero or
     above 100% because the total is a net: groups that reduced their holdings count as negative, so the rest add to more than 100%."
  6. `pre1719` and the yearly path 2017-2025 and 2026H1 in one table (Q6 rule). `pre2223` does not appear.
  7. The insurer line and reinsurance, in R1-7's words: only uncollateralised coinsurance moves bonds to the reinsurer; under funds withheld
     and modified coinsurance the US insurer keeps investing the assets; US captives are in the life sector; the insurer line may be
     understated by an unknown amount. Holdings through funds sit in funds.
  8. The household line as a residual, beside hedge funds and private debt funds and their sum (2.5).
  9. Level shares and level change minus flow ("price changes and other changes in volume").
  10. Revisions and the three registered statements (labels glossed: STABLE, MOVED, PENDING).
  11. Column dictionary, every share with its denominator, and glosses (R1-8 fix 10): "net acquisition" ("purchases minus sales and
      redemptions over the period"), "net issuance", "residual", "seasonally adjusted", "per-quarter average", "pp", "release", "Z.1".
  12. Citations. No N-PORT or TIC figure appears in the README (TIC stays in `checks.csv`).
- **`SOURCES.md`:** every URL with access date and status (2.10, the 404 and the Guide error page included), the dictionary wording of every
  code, the identities of 2.3 (and the first draft's error), the disclosure of 2.11 including the second reviewer's 2017-2019 shares, the
  FEDS Note citation of R1-7, release sb0662 for CREF2, and **Builder decisions**.

## 6. Leak and integrity rules

1. Committed: in `data/z1_corporate_bond_holders/` only the twelve CSVs, README.md and SOURCES.md; in the vintages folder only R4's release
   folders; never a `.zip`, `.json`, `.html` or STOP file.
2. No CUSIP-shaped token (`\b[0-9]{3}[0-9A-Z]{5}[0-9]\b` passing the check digit) in any output; no local path (`/Users/`, `/private/`,
   `~/`); no `@`. Nothing written outside the two folders except landing's `.gitignore`, REPRODUCE.md and CALENDAR lines.

## 7. Selftests (synthetic only; each guard applies its own mutant, and an uncaught mutant fails the selftest)

**G14's literal patterns, both compiled with `re.I`** (pasted, not imported). `CAUSAL_RX`:

```
\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of)\b
```

`EXTRA_RX` (R1-8 fix 9: catches bought, buyer(s) and demand; the denial sentence is exempt):

```
\b(?:in|out)flows?\b|\bflow(?:s|ed|ing)?\s+(?:into|out\s+of|from|to)\b|\bnet\s+(?:sell|buy)(?:ers?|ing)\b|\bbought\b|\bbuyers?\b|\bdemand\b|\b(?:sell|sells|sold|selling|sale|sales|buy|buys|buying|purchas(?:e|es|ed|ing))\s+(?:of\s+)?(?:equit(?:y|ies)|stocks?|shares|bonds|assets)\b|\bforced\s+(?:sell|sale)\w*|\bliquidat\w*|\bsell[- ]?off\b|\bbid\b|\bdrain\w*|\bdeplet\w*|\bcrisis\b|\b(?:fund|funds|funded|funding|financ\w+)\s+(?:of\s+)?(?:the\s+)?AI\b|\bAI(?:-era)?\s+(?:bond\s+)?(?:wave|boom|bonds?|debt|paper|issuance|supply)\b|\bcomposition\s+of\b
```

| Guard | Protects | Mutant that must be caught |
|---|---|---|
| G1 parsing | R8 | a column chosen by position (fixture with columns reordered); a code matched without its `.Q`; `ND` read as 0; a float sum; a `YYYYQN` date accepted; a BOM breaking the first header |
| G2 line mapping | 2.2 | a sub-line (20, 21, 25, 26, 28, 29, 31, 32, 44, 45, 52, 53, GA, SA) added to its group or a total; an issuer detail (4-11) added to `iss_domfin`; line 54 added to holders; `hh_plus_private_funds` counted among the nine; a leaf in two groups or none; FU453163003.Q missing from the line-3 identity |
| G3 identities | 2.3 | 28 leaves missing line 13 by 5 $mn in 2018 passing C04 (must FAIL); the same in 2005 written as FAIL (must WARN); levels tested as leaves + 54 = line 13 (must be leaves = 13 and 54 = 1 - 13); GA + SA not checked |
| G4 windows | 3.4 | a window off by one quarter (2024:Q2 start); `wave` extended to 2026:Q3 on a December fixture; `fa_div4` not divided by 4; `wave_ext` written on the September fixture; `avg_per_quarter_usd_mn` divided by 4 instead of `n_quarters` |
| G5 shares | 3.5-3.7 | denominator = sum of positive flows in `share_of_total_pct`; a negative group flow clipped to 0; shares not summing to 100 over the nine groups; `share_of_positive_pct` written for a negative flow; `positive_total_usd_mn` over leaves instead of groups; `offset_ratio` on group sums; flag not set at 0.4999 |
| G6 headline | 3.8, R1-1 | **a window share computed as the mean of quarterly shares** (fixture where the two differ by more than 1 pp; R1-8 fix 13); any verdict word (HELD, FALSIFIED, INSIDE_BAND, NOT_HELD, ABOVE_BAND, BELOW_BAND) written to any CSV; `rank_wave` ranking `other` or `gse_bd`; `headline.csv` on basis `fa_div4` |
| G7 levels | 3.9, 2.1 | level share over line 1; line 54 dropped; an FL code labelled `lm_market` or "book" |
| G8 level change | 3.9 | start level taken at the window's first quarter instead of the quarter before; the residual labelled revaluation |
| G9 revisions | 3.11 | `revisions.csv` appended; a release compared with itself writing rows; `wave` on a December fixture computed over 11 quarters |
| G10 registered statements | 4.6, R8 | a statement scored on the September release alone (must be PENDING); a delta of 1.9996 pp rounded to 2.000 and labelled MOVED (must be STABLE on the unrounded Decimal); 2.0000 labelled STABLE; SREV-F without interval funds; **a constant edited so the canonical text's sha256 changes** (build refuses `registered.csv`) |
| G11 zip handling | R4 | AST scan: `extractall` called, or a write path built from a member name; a fixture zip whose member is named `../x.csv` causing any write outside the cache |
| G12 allowlists | 5 | an extra or renamed column; `SPEC_ALLOW_SHA256` not the hash of the canonical text; `# source:` compared as a header; a thirteenth CSV (fixture: `tic_check.csv` or `tests.csv`); **check.sh reading the header lines from the script**; a duplicate key; `fl_book` in `valuation` |
| G13 leak guard | 6 | on a planted bad folder: a `.zip`, a `.json`, a valid CUSIP in a CSV, a `/Users/` path in SOURCES.md, each reported; on the clean folder it passes |
| G14 wording | R6 | the patterns above applied to README.md except the denial sentence; the opening template and the R1-3, R1-4 and R1-7 template sentences pass; "insurers were the main buyers" fails; "foreign demand rose" fails; "US residents bought foreign bonds" fails; "pensions funded the AI build-out" fails; "money flowed into credit funds" fails; "the composition of holders" fails; "spreads fell because of insurers" fails |
| G15 STOP latch | R3a | AST scan: a STOP path reached by `os.remove`, `os.unlink`, `os.replace`, `os.rename`, `shutil.rmtree`, `shutil.move`, `Path.unlink`, `Path.rename`, `Path.write_text`, `Path.write_bytes`, or `open` in mode w or a; runtime: with a planted `STOP_z1cb`, `fetch` makes no request and exits 2, file sha256 unchanged; fixture 301, 403, 429, 500, empty, HTML and non-zip bodies each write STOP with five fields; **a 404 writes no STOP, prints `NOT POSTED` and exits 3**; a timeout writes no STOP and exits 3 |
| G16 fetch safety | R1-R3 | a request to `www.sec.gov`, `fred.stlouisfed.org`, `home.treasury.gov`, `ticdata.treasury.gov` or `/releases/z1/<d>/default.htm`; `@` in the UA; a redirect followed; any retry; a second request in one `fetch` |
| G17 isolation | R7, R10 | AST scan: the script opens a path outside its two folders (fixture: `data/nport/nport_2026Q3.csv`); a CREF2 TIC constant used outside `checks.csv` |
| G18 units | R8, 2.4 | an FA (annual-rate) value summed undivided; a level read as a flow; `$bn` written to a `_usd_mn` column |

## 8. Pinned checks (`checks.csv`)

**Pin rules.** Pins on the 20260911 release FAIL on that release and WARN on a later one (the value then goes to `revisions.csv`).
Structural checks FAIL on every release, except C04 and C05 before 2017:Q1 (WARN).

- **C01 Release file (20260911):** zip sha256 `b63af9755437df0fb88b7cf346f8f9eaeb22bf1aa2b5df1709334135c43de4b6`, 8,336,582 bytes,
  `Last-Modified` 2026-09-11 16:00:19 GMT, 616 members; F3_5_t_tu.csv 67,645 bytes, F3_5_t.csv 73,944, F3_5_s.csv 82,820 (observed).
- **C02 Shape:** F3_5_t_tu and F3_5_t have 53 series columns, F3_5_s 54; data rows from 1945:Q4; on 20260911, 305 rows ending 2026:Q2.
- **C03 Dictionary:** every code of 2.2 sits on the line and table stated there and its dictionary text contains the sector name (FAIL lists
  every mismatch together; a renumbered line is a FAIL, never silently followed).
- **C04 Flow identities (2.3), both bases:** each within 2 $mn; FAIL from 2017:Q1, WARN 1990:Q1-2016:Q4.
- **C05 Level identities (2.3):** 28 leaf levels = line 13 within 2 $mn and line 54 = line 1 - line 13 within 2 $mn; FAIL from 2017:Q1,
  WARN before. Pins (20260911): line 1 - line 13 = -290,252 (2017:Q4), 357,667 (2018:Q4), -599,833 (2019:Q4).
- **C06 Annual bases:** for every complete calendar year 2017-latest and every line, sum(FA)/4 - sum(FU) within 4 $mn (observed max 3 for
  2017-2019); WARN on a later release.
- **C07** retired (R1-6: the 2020-21 pins are dropped).
- **C08 Window lengths:** `wave` 10, `pre1719` 12, `pre2223` 8 quarters, on every release.
- **C09 No missing cells:** no `ND` or blank in any 2.2 code, 2017:Q1-latest (observed none on F3_5_t_tu to 2026:Q2).
- **C10 Fixed output:** a second `build` leaves every output sha256 unchanged.
- **C11 Statement hash:** the constants reproduce the 4.6 sha256 (FAIL blocks `registered.csv`).
- **C12 Release key** within 3 days (R5).
- **C13 Tamper:** per window, basis and side, the nine holder (three issuer) group shares of the net sum to 100 within 0.01, and the
  positive shares sum to 100 within 0.01 over the groups with positive flow; `ins` = `ins_life` + `ins_pc` and `ins_life` = GA + SA within
  0.002 $mn. True by construction; catches a hand edit.
- **C14, C16** retired (R1-6: TIC fetch and gap). **C15 Content tests:** no R3b failure (listed together).
- **C17 Cache integrity (R1-8 fix 8):** every cached member's sha256 and size equal its `provenance.csv` row, and `provenance.csv`'s zip
  sha256 equals the `vintages.csv` row of that release (FAIL; a mismatch means the cache was edited or partly copied).
- **CREF1 (WARN, R1-5; review-derived, 20260911 only):** on the fu basis, `ins` share of the net = 37.12% for `y2024` (224,689 + 70,237 of
  794,490 $mn), 35.67% for `y2025` (221,483 + 65,834 of 805,405) and 33.26% for `wave` (of 2,228,428), each within 0.005 pp of the
  unrounded value, and the six dollar figures exact to 1 $mn. A WARN is reported to the supervisor, never fixed by editing the constant.
- **CREF2 (R1-5):** (a) WARN unless the build's rest-of-world line-51 net acquisition for `y2024` on `fa_div4` rounds to 298.8 $bn (Grok's
  SA figure); (b) status INFO, never PASS or FAIL: the TIC press-release constants 304.5 $bn (2024) and 392.4 $bn (2025) (sb0662) beside the
  build's line-51 `y2024` and `y2025` fu sums, with the gap (TIC minus Z.1) in $bn. The description says the gap is expected (TIC includes
  municipal bonds) and the two are not independent.

## 9. Success criteria (each with the command and the number that would disprove it)

1. `python3 bin/z1_corporate_bond_holders.py selftest` prints G1 to G18, each `caught`, and exits 0. **Disproved by** any line containing
   `SURVIVED`, a missing G-number, or a non-zero exit.
2. `python3 bin/z1_corporate_bond_holders.py fetch --release 20260911`: `fetch_log.csv` gains exactly **1** row, status 200, host
   `www.federalreserve.gov`, sha256 equal to C01. **Disproved by** a second row, another host, or a different sha256 (the Fed has re-posted
   the file: stop and tell the supervisor).
3. `python3 bin/z1_corporate_bond_holders.py build`, then `grep -c ',FAIL$' data/z1_corporate_bond_holders/checks.csv` prints **0**.
   Acceptable non-PASS rows: CREF2(b) INFO; CREF1, CREF2(a), C06 or C04/C05 before 2017 as WARN, each reported to the supervisor.
4. `grep -rlE 'HELD|FALSIFIED|INSIDE_BAND|ABOVE_BAND|BELOW_BAND' data/z1_corporate_bond_holders/ | wc -l` prints **0**, and
   `headline.csv` has exactly one `ins_share_wave_pct` row for release 20260911.
5. **Hand re-derivation by a verifier** from `data/vintages/z1_corporate_bond_holders/20260911/F3_5_t_tu.csv`, without the script: 100 x the
   sum over 2024:Q1-2026:Q2 of (FU543063005.Q + FU513063005.Q) / the sum of FU893063005.Q equals `ins_share_wave_pct` to 3 decimals and
   CREF1's 33.26 to 2. **Disproved by** a difference above 0.0005 against the build or 0.005 against 33.26.
6. A `python3 -I -c` sum over `windows.csv`: for every (release, window, side, basis) the nine holder (three issuer) shares of the net sum to
   100.000 +/- 0.01. **Disproved by** any set outside that range.
7. **M26** (warn-only, in `bin/check.sh --all`), with its own copy of the twelve header lines: the fourteen file names; headers (skipping
   `# source:`); no `.zip`, `.json` or STOP in git; no CUSIP, local path or `@`; no G14 pattern in README.md outside the denial sentence;
   **no verdict word of criterion 4 in any CSV (✗)**; `registered.csv` labels only STABLE, MOVED or PENDING (✗); `wave` rows have
   `n_quarters = 10` (✗); C13's sums (✗); no duplicate key (✗). **On a scratch copy** with a planted `.zip`, a renamed header, a `HELD`
   cell in `headline.csv` and a `wave` row with `n_quarters = 11`, M26 prints **four** ✗ lines; on the clean folder, ✓. Shown failing on
   the planted copy before it lands.
8. **Supervisor hash step:** extract the allowlist block from this spec and take its sha256; it must equal `SPEC_ALLOW_SHA256` in the script,
   check.sh's literal block, and `da0c7635f50184f044c8ebc04f2affceef805fb7d015ef023a4ca530c52860f9`. The same for the 4.6 block against `SPEC_PREREG_SHA256` and `e4e306b4731b97f94b5e5d5a0acab38ee1287a684ecb9e438352663f0e621f99`.
9. **10 Dec run:** after `fetch --release 20261210` and `build`, `registered.csv` holds three rows (SREV, SREV-F, SREV-R) for release_new
   20261210 with label STABLE or MOVED, and `revisions.csv` has `wave` rows for every group on both bases. **Disproved by** a PENDING label
   once that release is cached, a missing statement, or a `wave` row with 11 quarters. A 404 before then is not a failure (R3a).
10. **README cold-reader test.** Three fresh agents read only the README: a non-specialist, a fixed-income practitioner, and one told to
    report the insurer share and rank. **Pass** only if the first two can say what "net acquisition" is, that shares of a net can exceed
    100%, that households are a residual, that the insurer line may be understated by reinsurance structures, that nothing here identifies
    holders of AI companies' bonds, and that the shares were seen before the spec; and the third reports the share, the rank and the groups
    ahead. **Fail** if any reader thinks the table shows who bought the AI deals, that it tests the practitioner claim, or that insurers caused anything.
11. **Spec before build (step 0):** `git log --diff-filter=A --format=%cI -- _research/<this spec's file>` is earlier than the first
    `utc_time` in `fetch_log.csv`. **Disproved by** a later commit time, or no commit.

**Landing (builder):** `.gitignore` rule, REPRODUCE.md paragraph, the CALENDAR row of 4.6, M26, a HANDOVER row; commits nothing.

## 10. OPEN questions

Closed by the rulings: O-2 (R1-11: not calibrated), O-6 (R1-10: a 404 means not yet posted), O-8 (R1-6: `pre2223` stays in the CSVs,
out of the README). O-4 is replaced by R1-7's wording. Open:

- **O-1 Estimated lines.** 2.5 is relayed; the one Guide URL tried returned an error page. The supervisor may name the Guide's current
  address or the release notes so SOURCES.md quotes the Fed for lines 14 and 37-42.
- **O-3 Private placements.** Relayed: Z.1 corporate bonds include privately placed bonds, a large life-insurer holding. Not checked at source.
- **O-5** retired with the TIC fetch (R1-6).
- **O-7 Where the Beignet notes sit in Z.1** (nonfinancial corporate, ABS issuer or other) is unknown; kept only as a reason Z.1 cannot speak to one deal.
- **O-9 Share of the positive flows (R1-4).** The ruling does not fix the denominator. This rewrite uses the positive window flows of the
  nine holder groups (three issuer groups); positive leaf flows would give a larger denominator. The supervisor may choose.
- **O-10 "A few percent".** R1-3's figure for the AI issuers' share of the denominator has no source in the spec; the README attributes it to
  the supervisor. A cited computation (e.g. from the D2/F1 issuance tallies, on the same window) would let it stand as MEASURED.
- **O-11 The 404 rule's scope.** R1-10 speaks of the inferred 10 Dec URL; this rewrite applies "404 = not yet posted, exit 3, no STOP" to
  every release zip, since `fetch` requests nothing else. The supervisor may restrict it.
- **O-12 Code count.** Fix 4 speaks of 25 missing codes; against the first draft the spec author counted 19 FU codes (lines 4, 6-11, 20, 21,
  25, 26, 28, 29, 31, 32, 44, 45, 52, 53) and 39 level codes not written out. 2.2 now writes every FU, level and S1281 code, so the count no
  longer matters, but the reviewer's list was not seen.

## Supervisor rulings

*Appended here by the supervisor, newest last, all before any data run; they override the body.*

## Supervisor rulings, round 1 (Sonnet second review and Grok attack), 26 Oct 2026 — before any build

**Disclosure first: the blind rule was broken during review.** The Grok attack parcel carried no blind clause. Grok read the published F3.5.t table on federalreserve.gov and reported the wave result: on the seasonally adjusted basis, life plus P&C insurers about 32% of all-sector net acquisition over 2024Q1–2026Q2, registered funds about 47%, rest of the world about 41%, and the household residual about −35%. The supervisor then confirmed from the cached 11 Sep 2026 zip (unadjusted FU sums): insurers 33.26% of 2,228,428 $mn over the ten quarters; 2024 37.12% (224,689 + 70,237 of 794,490); 2025 35.67% (221,483 + 65,834 of 805,405). The second reviewer stayed blind on 2024–26 but computed 2017–2019 shares: funds 39.98%, insurers 34.36%, rest of the world 31.23% of 1,329,619 $mn. The spec author's priors in 2.11 are also not blind. **No holder-share statement in this spec can be scored as pre-registered.**

- **R1-1 (reframe; replaces T1, T1S and T2 as tests).** The build is a descriptive ledger. T1 and T2 become reported statistics, not verdicts, under the names `ins_share_wave_pct` and `rank_wave`. No HELD/FALSIFIED or BELOW/ABOVE_BAND label is printed for them. The README opening states the share, the rank and the denial sentence. SOURCES.md and the README carry the disclosure above in one sentence: "The wave-window shares were seen during review, before this spec was committed, so they are reported, not tested."
- **R1-2 (what stays pre-registered).** SREV stays: "insurers' wave share moves by less than 2.0 pp between the 11 Sep and 10 Dec 2026 releases". It is scored on the 10 Dec release, which nobody has seen. Add the same statement for the funds and rest-of-world shares (SREV-F, SREV-R). The 2.0 pp has no measured prior; a move larger than 2.0 pp is a result, written beside the old value. Labels: `STABLE`, `MOVED`, `PENDING`.
- **R1-3 (the answer to the practitioner claim, stated plainly).** The README says what Z.1 can say: over 2024Q1–2026Q2, US insurers' net acquisition of corporate and foreign bonds was about a third of the all-sector net, behind registered funds and the rest of the world. It says equally plainly what Z.1 cannot say: the instrument is all corporate and foreign bonds (investment grade and high yield, financial issuers, private-label ABS and MBS, and foreign bonds held by US residents), so a share of it says nothing about who took the AI issuers' bonds, which were a few percent of the denominator. Print nonfinancial issuance, foreign bonds bought by US residents, and financial issuance as dollar shares of the net, ahead of any holder share (Grok).
- **R1-4 (shares of a net flow).** Dollars go beside every share. Also print each group's share of the positive holder flows (Grok). Shares outside 0–100 are allowed and explained in one sentence (Sonnet fix 11). The README never calls the net shares a composition of buyers.
- **R1-5 (review-derived checks, WARN).** C-REF1: the 2024 and 2025 unadjusted annual insurer shares are 37.12% and 35.67%, and the wave share is 33.26%, on the 11 Sep vintage. C-REF2: the rest-of-world 2024 net acquisition (Grok: 298.8 $bn on the SA table) is set beside the Treasury TIC press-release corporate bonds, private plus official: 304.5 $bn in 2024 and 392.4 $bn in 2025 (sb0662, verified verbatim by the supervisor). These are typed constants and are not fetched; the gap is expected (TIC includes municipal bonds) and the two are not independent.
- **R1-6 (drop).** The TIC fetch mode, the CSLT JSON and its guards; ex-ABS groups; the coverage ratio; the N-PORT sentence; the 2020–21 pins in C07; and T1S. The 2022–23 window stays in the CSVs but leaves the README (O-8).
- **R1-7 (offshore reinsurance, Grok change 4).** Replace the offshore sentence. Only uncollateralised coinsurance moves the bonds to the reinsurer, which is in the rest of the world if it is offshore. Under funds withheld and modified coinsurance the US insurer keeps investing the assets, and US captives are brought into the life sector (Board FEDS Note, 12 Oct 2018). The size of each structure is unknown, so the README says the insurer line may be understated by an unknown amount.
- **R1-8 (accepted from the Sonnet review).**
  - Fix 3: the level identity (the 28 leaves equal line 13; line 54 = line 1 − line 13).
  - Fix 4: add the 25 missing codes, including issuer FU453163003 (Grok change 5); state the `.Q` suffix.
  - Fix 5: compare unrounded Decimals, precision 28.
  - Fix 6: C04/C05 FAIL from 2017:Q1, WARN before.
  - Fix 7: FL/LM wording, and rename `fl_book` to `fl_unspecified`.
  - Fix 8: C17 cache integrity, and step 0 (spec committed first).
  - Fix 9: the ban list catches bought/buyer(s)/demand, with the denial sentence exempt.
  - Fix 10: README glosses, and a per-quarter average beside the window totals.
  - Fix 13: the mutant for the mean of quarterly shares.
  - Read zip members by name; never use `extractall`.
- **R1-9.** Print general account and separate account separately, under the life line (Grok).
- **R1-10 (O-6).** A 404 on the inferred 10 Dec zip URL means "not yet posted": it exits 3 without writing STOP. Any other non-200 writes STOP.
- **R1-11 (O-2).** The band is not calibrated. No registered number changes from now on.
- **Guard number stays M26.** The second reviewer's 2017–2019 shares are recorded in SOURCES.md as observed during review.

## Supervisor rulings, round 2 (open questions after the rewrite), 26 Oct 2026 — before any build

- **O-10:** "a few percent" is dropped. The README may cite one context figure, BIS Quarterly Review (16 Mar 2026), that hyperscalers' gross bond issuance was "topping $100 billion in 2025", and must say it is gross issuance by five firms. It is not comparable with a net flow, so no ratio is computed or printed. The sentence that remains: "Z.1 has no line for the AI issuers, so this table cannot say who took their bonds."
- **O-9:** adopted; the positive-flow denominator is the positive window flows of the nine holder groups.
- **O-11:** adopted; the 404 rule applies to every release zip.
- **O-12:** moot; every code is written out.
- **New INFO status for CREF2:** adopted.
