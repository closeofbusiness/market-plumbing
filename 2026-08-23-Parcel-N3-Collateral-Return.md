# Parcel N3 — the collateral leg: Gemini's return, adjudicated, and what it unlocked

*23 August 2026. Return received 19:27 at the Dropbox share root (`N3_Collateral_Scouting_Return.md`,
2,940 words, 11 IDs, 11 CCP sub-rows), filed as `_research/N3_Collateral_Scouting_Return_gemini_ondisk.md`
(sha256 e92e4990…). **Verified row by row the same evening by fourteen independent fetch-and-report agents**
(one per CCP group and per section; raw results `_research/N3_verification_results_2026-08-23.json`), then
re-pulled by us where the verification opened a series. Register: **C-055** (the return), **C-056** (my own
FIA claim). Rules applied: C-045, C-049–C-051, C-054 — every URL fetched, every citation re-derived, every
identifier ignored.*

---

## 1. Scorecard

| | Rows | Publisher / existence right | URL right | Attributes right | Changed what we know |
|---|---:|---:|---:|---:|---|
| **S** sources | 3 (+4 Singh entries) | 7/7 | **0/7** (two 404, two IMF index pages, ISLA/RMA/OFR dead) | mostly | **Yes — S1 #2** |
| **R** official re-use | 4 (+3 negatives) | 4/4 negatives hold | 3/9 | values wrong (3 of 4) | **Yes — R3, R4** |
| **K1** CCP files | 11 | **11/11 exist with 6.1.1 and 6.2** | 6/11 (LCH ×2, Eurex 404; DTCC ×2 corporate pages) | **format wrong 9/11; "earliest 2015 Q3" wrong 4/11** | Yes — 11 files now on disk |
| **K2** aggregators | 3 | 3/3 | 2/3 (CCP Global 404) | FIA coverage/access wrong | **Yes — FIA is free, with an API** |
| **L1** re-use literature | 5 | 4/5 | **0/5** | venue wrong 2/4; #5 constructed | — |
| **L2** basis-trade literature | 6 | 3/6 | 1/6 | authors wrong 3; title wrong 1; #3, #6 constructed | — |

The K1 block is the clearest case yet of C-051's mechanism: eleven mandatory sub-rows, each filled with the
same four attributes ("XLSX, PDF · archive YES · earliest 2015 Q3"). Where a CCP really does start in 2015 Q3
(CME, ICE ×3, Eurex) the filler is right by coincidence; where it does not (OCC 2021 Q1, JSCC a rolling five
quarters, LCH Ltd 2020 Q1, LCH SA 2019 Q2) it is wrong; the formats are wrong almost everywhere (CME ZIP,
ICE ZIP, LCH/OCC/Eurex XLSX only, DTCC one combined workbook for FICC+NSCC). The dollar-sign rule held (0 in
the file); the no-identifier rule held; the self-audit ticked "every URL opened" over ~20 dead or generic URLs.

## 2. What changed what we know — four things, all now pulled by us

### 2.1 CCP initial margin, 2015 Q3 → 2026 Q1 — the D3 margin leg, measured

FIA's CCP Tracker is **free** and sits on a public JSON API (`fiadataapi.azurewebsites.net/api/Data/…`,
page-embedded key) carrying PQD item 6.1.1 — initial margin required, house net / client net / client
gross, USD — for 15 derivatives CCPs, 43 quarters. Pulled 23 Aug; `data/history/ccp_im_required_15ccp_fia_bn.csv`
and one file per CCP; re-pull `bin/pull_series.py --only fia`. Cross-check: FIA's CME Q1 2026 (house $67.8bn,
client gross $266.4bn) equals CME's own 2026Q1 file (Base + IRS: 57.6+10.2 / 236.2+30.3). **This kills my own
D3 §5 line of this afternoon — "FIA tracker: member dashboard, not a pullable feed" — C-056.**

| $bn, house net + client gross, 15 CCPs | 2015Q3 | 2016Q4 | 2019Q4 | 2021Q4 | 2022Q4 | 2023Q4 | 2024Q4 | 2025Q4 | 2026Q1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **CCP initial margin required** | 365 | 424 | 548 | **757** | 835 | 836 | 836 | 968 | **1,071** |

*CCPs: ASX, CME, Eurex, HKEX, ICE Clear Credit/Europe/US, JSCC, LCH Ltd/SA, LME, Nasdaq, OCC, SGX, TMX.
**Not FICC** — Treasury-repo clearing fund is in DTCC's own file: GSD 6.1.1 $66.5bn, post-haircut IM held
$77.8bn at 2026-03-31. House-net + client-gross is FIA's display convention and mixes gross/net client
reporting across CCPs; treat as an index, not a stock.*

**Against the D3 table (§2 of the D3 doc):** 2016→2021 CCP IM **+79%** vs complex +48%, MMFs +76%;
2021→2026Q1 CCP IM **+41%** vs complex +16%, MMFs +59%. Margin has grown faster than the asset-management
complex in both windows — so it *is* a second structural driver in the sense D3 §5 asked — but the post-2021
increment is **$314bn against a $3.1trn MMF increment**, and what is posted is not mainly cash-pool money:
CME's 6.2 for 2026Q1 (Base, post-haircut, $311.8bn held) is 39% cash at the central bank, 5% cash at
commercial banks, **42% domestic sovereign bonds**, the rest other sovereigns, gold, equities, corporates.
**Margin growth is real, is faster than AUM, and is too small and too securities-heavy to be the post-2021
cash surge.** D3's verdict stands with its last unmeasured leg now measured; the sec-lending leg waits for
SLATE (29 Mar 2027).

### 2.2 FICC sponsored repo, daily — the middle of the D8/D10 pipe

DTCC publishes a daily CSV (`dtcc.com/data/SponsoredVolume.csv`, behind `dtcc.com/charts/membership`),
rolling five years from 16 Aug 2021, **from the sponsored member's perspective**: "repo" = sponsored members
borrowing cash (the hedge-fund side), "reverse repo" = sponsored members lending cash (the money-fund side).
Pulled 23 Aug; `bin/pull_series.py --only dtcc`; `data/history/ficc_sponsored_*.csv`.

| $bn, last business day | Dec-21 | Dec-22 | Jun-23 | Dec-23 | Dec-24 | Jun-25 | Dec-25 | Jun-26 | 20 Aug 26 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Sponsored **repo** (members borrow cash — hedge funds) | 171 | 252 | 308 | 476 | 909 | 1,140 | **1,384** | 1,303 | 1,031 |
| Sponsored **reverse repo** (members lend cash — MMFs) | 245 | 273 | 464 | 638 | 1,107 | 1,315 | **1,576** | 1,559 | 1,265 |
| Total sponsored | 416 | 525 | 772 | 1,114 | 2,016 | 2,455 | **2,960** | 2,862 | 2,296 |

The three ends of one chain, each from open data, at end-2025: **MMF repo cleared at FICC $1,298bn** (OFR
MMF monitor, D8) ≈ **sponsored reverse repo $1,576bn** (DTCC; MMFs plus other cash lenders); **sponsored repo
$1,384bn** (DTCC) against **hedge-fund repo borrowing $3,379bn** (Form PF, D3 §8) — so roughly **40% of
hedge-fund repo borrowing is FICC-sponsored**, the rest bilateral (the OFR NCCBR collection, §2.4). Cash pools →
FICC → hedge funds, measured at each joint. Note the 2026 decline: total sponsored −$664bn from the Dec-25
peak to 20 Aug *(point values; on monthly averages it is −12% — see `2026-08-23-Parcel-D8-Clearing-Return.md` §1, which answers this)* — consistent with OFR's 20 Aug 2026 blog "*Central Clearing in Treasury Repos Plateaued in
Q1 2026*". Worth a calendar row; it is the reverse of the D8 story and we should know which.

### 2.3 Singh's denominator, extended to 2017 at the primary source (N3)

Singh & Goel, *Pledged Collateral Market's Role in Transmission to Short-Term Market Rates*, IMF WP/19/106
(17 May 2019) — PDF now at `_research/primary_sources/IMF_WP19106_…pdf`, read by us — **Table 2 "Sources of
Pledged Collateral, Volume of Market, and Velocity"**, $trn:

| | 2007 | 2010 | 2011 | 2012 | 2013 | 2014 | 2015 | 2016 | 2017 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Hedge funds | 1.7 | 1.3 | 1.4 | 1.8 | 1.85 | 1.9 | 2.0 | 2.1 | **2.2** |
| Securities lending | 1.7 | 1.1 | 1.05 | 1.0 | 1.0 | 1.1 | 1.1 | 1.2 | **1.5** |
| **Sources, total** | 3.4 | 2.4 | 2.5 | 2.8 | 2.85 | 3.0 | 3.1 | 3.3 | **3.7** |
| Pledged collateral received | 10.0 | 6.0 | 6.3 | 6.1 | 6.0 | 6.1 | 5.8 | 6.1 | **7.5** |
| Velocity | 3.0 | 2.5 | 2.5 | 2.2 | 2.1 | 2.0 | 1.9 | 1.8 | **2.0** |

*Sources line in the paper: "Risk Management Association; Singh (2011); updates to include Canadian banks."
Footnote 13: non-hedge-fund lenders (pension, insurers, official sector, asset managers) had $1.5trn on loan
at end-2017; hedge funds AUM $3.0trn.* This is the 2007/2010 benchmark in RESEARCH_STATE N3, carried to 2017
by Singh himself. No later Singh IMF paper exists (ten WPs 2018–22, none after); the Jan 2026 *Central Banking*
piece ("roughly $13trn", velocity "around 2.0") is the only later number and is paywalled.

**The N3 build this opens.** Form PF Q43 "collateral posted" by qualifying hedge funds (D3 §8) is the
*fund-side* measure of Singh's hedge-fund source. Against his Table 2: 2013 **2.03 vs 1.85**; 2014 2.24 vs 1.9;
2015 2.26 vs 2.0; 2016 2.38 vs 2.1; 2017 **2.83 vs 2.2**. It tracks to within ~15% through 2016 and diverges
in 2017 — then runs to **$8.2trn at 2026Q1**. ISLA's market-data page gives the sec-lending source: **€3.9tn on
loan at 31 Mar 2026** (lendable €40.6tn), with an "on-loan by client type" split. A naive 2026 extension of
Table 2 would read sources ≈ $8.2trn + ~$4.2trn against a pledged market of "roughly $13trn" — velocity
near 1, not 2. **That is a concept mismatch to be resolved, not a finding:** Form PF Q43 counts Treasuries
posted in repo (which Singh may net differently), and ISLA counts loans to non-dealer borrowers. It is
exactly the reconciliation N3 exists to do, and it can now be done from three open series plus one table.

### 2.4 Official re-use and the NCCBR collection — what exists, precisely

- **FSB / BIS: no aggregate re-use series anywhere.** BIS hosts the SFT aggregator (`bis.org/statistics/sft/submitsft.htm`
  — methodology only; "potential dissemination"); the FSB *Global Monitoring Report on NBFI 2025* (16 Dec 2025)
  has **zero** hits for re-use/rehypothecation; the one FSB document quoting re-use rates since 2017 is
  *Vulnerabilities in Government Bond-backed Repo Markets* (4 Feb 2026, §3.1.3) and it cites **third-party**
  work — Bundesbank (Jank et al.) 50–90% for euro-area government collateral; **65%** of collateral received
  rehypothecated by nine US intermediaries (Hempel et al. 2024, OFR); **~85%** of incoming US Treasuries re-used
  (Infante et al. 2020) — and records that as of Sept 2025 only **five jurisdictions** (Australia, Canada, Japan,
  Mexico, UK) report repo data to the FSB/BIS at all. Our channel map's line — "no published series for the
  stock of reused collateral in the United States" — holds, and now has the global counterpart.
- **ESMA:** one edition of the *EU SFT Markets* report (9 Apr 2024; total SFT exposure **€9.8tn** Sept 2023, repo
  €6.7tn, government bonds 87% of collateral); it uses SFTR Tables 1–2 only and **defers re-use (Tables 3–4) to
  "future work"**. No later edition found. Gemini's "EUR 10trn", "subsequent annual editions", "Collateral and
  Re-use Dynamics section" — all constructed.
- **OFR NCCBR — real and productive:** five blogs and two briefs from the collection since Aug 2025 — *Are
  Zero-Haircut Repos as Common as Advertised?* (12 Aug 2025: 56% zero / 34% positive / 10% negative haircut;
  hedge funds 65% zero-haircut), *Sizing the U.S. Repo Market* (4 Dec 2025: **NCCBR ~$5trn**, not the $2–2.5trn
  in the return), clearing impact (29 Jan 2026), *Sizing the U.S. Cross-Border Repo Market* (9 Apr 2026: ~half
  cross-border, not 25%), *Central Clearing in Treasury Repos Plateaued in Q1 2026* (20 Aug 2026); Briefs 26-03
  *Who Participates in Repo* and 26-05 *A Closer Look at the U.S. NCCBR Market* (PDF saved). Aggregates live in
  charts and tables, **no downloadable series**, and the Short-Term Funding Monitor API still has no NCCBR or
  sponsored mnemonics (164 series: DVP/GCF/tri-party only — our prior belief, confirmed).
- **Sponsored repo in official work:** Copeland & Kahn, *The Rise of Sponsored Service for Clearing Repo*,
  Liberty Street, 8 Oct 2025 (NY Fed Staff Report 1140): sponsored lending $244bn (15.9%) / sponsored
  borrowing $209bn (13.6%) / interdealer $1,086bn of $1,540bn average daily Treasury repo, Jan 2020–Jun 2024.

## 3. Row-by-row — the short form (full observations in the JSON)

**S1 Singh.** All four works real; every URL and most titles/sections constructed. (1) *Collateral Markets and
Financial Plumbing*, 3rd ed., Risk Books, March 2020 (retitled; riskbooks.com, not risk.net). (2) WP/19/106 Singh &
Goel — §2.3 above, the one that matters. (3) *Why fears about quantitative tightening are overblown*, Central
Banking, 18 Jul 2022 (paywalled; not "Pledged Collateral and QT"). (4) WP/2022/206 Armas & Singh, *Digital Money
and Central Banks Balance Sheet*, 28 Oct 2022 — no collateral split, as the return said. Extra: WP/18/62
*Leverage — A Broader View* (Singh & Alam) and WP/18/228 *The Morning After* (Turing & Singh) carry velocity text,
no source table. Jan 2026: *Collateral velocity is disappearing behind a digital curtain* (13 Jan 2026).
**S2** negative holds (SEC DERA's June 2025 *Broker-Dealer Activity in the United States* has FOCUS aggregates,
nothing on rehypothecation; the FINRA URL is constructed). **S3** ISLA URL dead → `islagroup.org/securities-lending-market-data/`
(quarterly snapshot with client-type split) and the *24th Edition, H2 2025* report; RMA merged into ProSight in
2024, survey gone; OFR item is **WP 16-08** *A Pilot Survey of Agent Securities Lending Activity* (23 Aug 2016),
not a "reference paper".

**K1.** Real pages: CME `/solutions/clearing/cpmi-iosco-reporting.html` (ZIP 2019Q3→, XLSX before; 2015Q3→2026Q1);
ICE `ice.com/clear-{credit,us,europe}/regulation#quantitative-disclosures` (one ZIP per quarter via a JSON
filter API; 43/43/48 quarters from 2015Q3); LCH `lseg.com/en/post-trade/clearing/clearing-resources/ccp-disclosures`
(Ltd and SA tabs, XLSX only; Ltd from 2020Q1, SA from 2019Q2 with a six-quarter listing gap); DTCC
`dtcc.com/legal/policy-and-compliance` (one combined workbook FICC-GSD/MBSD + NSCC, XLSX+PDF from 2016Q4,
PDF-only 2015Q3–2016Q3); OCC `theocc.com/risk-management/pfmi-disclosures` (XLSX, **2021Q1→**); Eurex
`eurex.com/ec-en/find/about-us/regulatory-standards` (XLSX, 2015Q3→2026Q1, 43 files); JSCC `jpx.co.jp/jscc/en/company/fmi-pdf2.html`
(XLSX+PDF, **rolling five quarters only**). All eleven 2026Q1 files are in `data/vintages/ccp_pqd_2026Q1/`.
cmegroup, dtcc and theocc bot-block curl — a browser session was needed. **K2.** CCP Global at `ccp-global.org/pqd`
(free PDFs: *PQD Quarterly Trends Report* 2022Q1–2026Q1 covering 63 CCPs; *Newsflash* 2018Q1–2025Q1; no
machine-readable aggregate); FIA — §2.1; Clarus — paid, with a free quarterly blog (latest *Record Q1 2026 CCP IM
disclosures*, 30 Jun 2026).

**L1.** Real: Infante–Press–Strauss, *The Ins and Outs of Collateral Re-use*, FEDS Notes, 21 Dec 2018;
Jank–Moench–Schneider, *Safe asset shortage and collateral reuse*, Bundesbank DP 39/2021 (**not** JFE);
Fuhrer–Guggenheim–Schumacher, *Re-use of collateral in the repo market*, SNB WP 2015-02 → JMCB 48(6) 2016;
Infante–Vardoulakis, *Collateral Runs*, RFS 34(6) 2021. **Constructed:** "Aguiar–Biais–Crassard, *Collateral Reuse
in Euro Area Financial Markets*, ECB WP 2023" — no such paper; the real ECB work is Alexiou–Pereira–Rodrigues-Gomes,
*Repo collateral reuse and liquidity windfalls*, ECB WP 3147 (2025). Added by the verifiers: Infante–Press–Saravay
(AEA P&P 2020); Infante–Saravay (FEDS Notes 2020, COVID re-use); Inhoffen–van Lelyveld (DIW DP 2050, 2023);
Luu–Napoletano–Barucca–Battiston (J. Fin. Stability 2021); Lewis (JFE 2023).

**L2.** Real: Barth–Kahn, *Hedge Funds and the Treasury Cash-Futures Disconnect*, OFR WP 21-01 (1 Apr 2021;
"JFE" and "TRACE" unsupported). Title wrong: Banegas–Monin–Petrasek is *Sizing hedge funds' Treasury market
activities and holdings*, FEDS Notes, 6 Oct 2021. Authors wrong: *Quantifying Treasury Cash-Futures Basis Trades*
is Glicoes–Iorio–Monin–Petrasek, 8 Mar 2024; *The Cross-Border Trail of the Treasury Basis Trade* is
Barth–Beltran–Hoops–Kahn–Liu–Perozek, **15 Oct 2025** (TIC undercounts Cayman hedge funds' Treasuries by
~$1.4trn). **Constructed:** "Avalos–Ehlers–Eren, BIS QR Sept 2023" — the URL is a CP/CD primer; the real item is
Box A *Margin leverage and vulnerabilities in US Treasury futures*, Avalos & Sushko, BIS QR 18 Sep 2023;
"Hauser, *From sunshine to stormy weather*, BoE 2023" — no such speech. Added: Barth–Kahn–Mann, *Recent Developments
in Hedge Funds' Treasury Futures and Repo Positions*, FEDS Notes 30 Aug 2023; Banegas–Monin, *Hedge Fund Treasury
Exposures, Repo, and Margining*, 8 Sep 2023; Berg–Stemp, *Hedge Funds' Cash Treasury Holdings Reach $2 Trillion*,
OFR blog, **19 Aug 2026** (7% of marketable debt at end-2025).

## 4. What this does to the open work

- **D3** — margin leg measured (§2.1); verdict unchanged; only the sec-lending leg remains (SLATE). D3 doc §9 amendment.
- **D8 / D10** — the pipe now has three measured joints (§2.2). The 2026 sponsored decline is a new question.
- **N3** — benchmark carried to 2017 at source; the fund-side series (Form PF Q43) and the sec-lending series (ISLA)
  are located; the reconciliation with Singh's concepts is the build (§2.3). No longer "blocked by N1 for method".
- **Process** — C-055 (the return), C-056 (my FIA claim). Fourth external return in a row with the same shape.
  The verification fan-out (14 agents, ~28 minutes, every URL fetched) is now the standard receipt procedure for
  any external return: it found what one agent reading the file would not have — the FIA API, the DTCC CSV, the
  OCC/JSCC archive depth, the two constructed papers.
