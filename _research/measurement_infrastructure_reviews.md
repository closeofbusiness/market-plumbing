# Infrastructure reviews — flow of funds, shadow aggregates, critiques

## Fed Z.1 and sectoral balances

## Z.1 FINANCIAL ACCOUNTS — WORKING GUIDE
**All figures verified by direct download of the current release package on 2026-08-21. Vintage: Z.1 released 11 June 2026, data through 2026:Q1. Units are $ millions unless stated. Every series ID below was confirmed present in the release's own data dictionary; every arithmetic identity below was recomputed, not asserted.**

---

## 0. THE THING THAT WILL BREAK YOUR PIPELINE FIRST

Effective with the **11 June 2026 release**, every Z.1 table was renumbered from the old sequential system (F.103, L.133, B.101) to **SNA alphanumeric codes** (S11.1.t, S2.s, S1M.b). The Board's own words, from `introductory_text.htm`:

> "Effective with this release, all Z.1 Financial Accounts of the United States release tables have been renumbered to more closely align with the System of National Accounts (SNA) classification hierarchies for sectors and instruments... (for example, table F.133 is now S2.t, and table L.133 is now S2.s)."

**The complete crosswalk is a 205-line CSV**: `https://www.federalreserve.gov/releases/z1/current/z1_table_mapping.csv` (columns: `new,old,title`). Download it once and hard-code it.

Three further changes in the same release that matter more than the renumbering:

1. **Repo was folded into loans.** "The Federal funds and security repurchase agreements instrument (tables F4.1.t and F4.1.s) has been reclassified as a subcategory of total loans (tables F4.t and F4.s)." Consequently the loan instrument code changed from `x4023005` / `x4123005` (asset/liability, loans excluding repo) to **`x4035005` / `x4135005`** (total loans *including* security repurchase agreements). This is a definitional break, not a rename. `FL894123005` (all sectors, total loans, liability) was **deleted**; `FL894135005` is the successor and is a broader concept. Confirmed in `z1_code_changes.txt`: 96 code changes in 2026q1, of which 41 outright deletions, nearly all of them the old loans aggregates.
2. **"Levels" is now "stocks outstanding."** Table suffix `.s`. Cosmetic but it breaks text parsers.
3. **"Monetary authority" is now "central bank"** (S121). Eight NIPA-derived tables were **discontinued** entirely: old F.2 (Distribution of GDP), F.3 (Distribution of national income), F.4 (Saving and investment by sector), F.5 (Net capital transfers), F.4.g, F.4.c, F.4.f, L.4.s. The *series* survive and remain downloadable; the *tables* do not.

Note also `z1_code_changes.txt` (857 KB, 6,484 rows, back to 2009q4) is a permanent per-quarter log of every mnemonic added, deleted or renumbered. It is the only honest revision-of-definition record. `https://www.federalreserve.gov/releases/z1/current/z1_code_changes.txt`

---

## 1. HOW TO GET THE DATA — THREE PATHS, ALL TESTED

**(a) The whole release as CSV + dictionary — the only path I recommend for a production pipeline.**
```
https://www.federalreserve.gov/releases/z1/current/z1_csv_files.zip   (8.08 MB, HTTP 200)
```
Unpacks to `csv/` (286 files, one per table, wide format: `date` column plus one column per series mnemonic, periods `1945:Q4`…`2026:Q1`, missing = `ND`) and `data_dictionary/` (286 tab-delimited files: `mnemonic \t description \t "Line n" \t table \t units`). Table names in the zip replace dots with underscores: `S11.1.t` → `csv/S11_1_t.csv`.

**(b) Vintage archive — this is how you do revision analysis.** Prior releases live at a stable path:
```
https://www.federalreserve.gov/releases/z1/YYYYMMDD/z1_csv_files.zip
```
Confirmed live vintages: `20260611` (current), `20260319`, `20260109`, `20250911`, `20250612`, `20250313`, `20241212`, `20240912`, … Snapshot each one; the Fed does not publish a vintage database and FRED's ALFRED coverage of Z.1 is partial.

**(c) FRED mirror for single-series work.** ID = `BOGZ1` + mnemonic + frequency letter, e.g.
```
https://fred.stlouisfed.org/graph/fredgraph.csv?id=BOGZ1FL103163005Q
```
Verified: returns 8,036,583 for 2026-01-01, identical to the release package. **But the mirror is incomplete** — `BOGZ1FL624135035Q` (hedge fund prime-brokerage borrowing) returns an HTML 404. Supplementary-table series are not reliably mirrored. Do not build on FRED alone.

The Board's Data Download Program (`/datadownload/Output.aspx?rel=Z1&series=…`) requires its own opaque series key, not the mnemonic; passing `FL103163005.Q` returns HTTP 400. Ignore it.

---

## 2. ANATOMY OF A SERIES MNEMONIC

Verified against `https://www.federalreserve.gov/apps/fof/SeriesStructure.aspx` and cross-checked empirically across all 286 dictionaries.

`FA` `10` `5005305` `.Q` → prefix (2) + **sector (2 digits)** + type/instrument (5) + asset-liability and detail digits + frequency.

**Prefix table (published, exact):**

| Prefix | Meaning | Derivation |
|---|---|---|
| `FL` | Stock outstanding, NSA | `FL[t-1] + FU + FR + FV` |
| `LM` | Stock at market value / current cost, NSA | `LM[t-1] + FU + FR + FV` |
| `LA` | Stock, seasonally adjusted | `LA[t-1] + FA/4 + FR + FV` |
| `FA` | **Transactions, SAAR** | `(FU + FS) × 4` |
| `FU` | Transactions, NSA (quarterly amount) | `FL − FL[t-1] − FR − FV` |
| `FR` | **Revaluation** (holding gains) | `FL − FL[t-1] − FU − FV` |
| `FV` | Other changes in volume (breaks, definitional shifts) | `FL − FL[t-1] − FU − FR` |
| `FC` | Change in unadjusted stock | `FL − FL[t-1]` |
| `FS` | Seasonal factor | `FA/4 − FU` |
| `FG` | Growth rate, SA | `FA / LA[t-1] × 100` |
| `FI`, `PC` | Index, % change in index | |

**This is the single most important discipline in the whole system:** `FC = FU + FR + FV`. A change in a stock is *not* a flow. Corporate equity, mutual fund shares and anything carried at market value move mostly through `FR`. If you difference `FL` and call it credit creation you have counted a price change as money. Household net worth rose $0.1tn in 2026:Q1 (`FL152090005` = 182,979,889) — almost entirely revaluation, with equity revaluation *negative* $1.8tn offset by real estate.

**Sector codes (first two digits), derived by exhaustive scan of the release dictionaries — this is the sector inventory of the entire US financial system as the Fed sees it:**

| | | | |
|---|---|---|---|
| 10 Nonfinancial corporate business | 11 Nonfinancial noncorporate | 12 Equity REITs | 14 Nonfinancial business |
| 15 Households & nonprofits | 16 Nonprofits | 17 Personal sector | 18 Corporate farm |
| 21 State & local govt | 22 S&L employee pensions | 26 **Rest of the world** | 31 Federal government |
| 34 Federal pension funds | 36 General government | 38 Domestic nonfinancial | 40 GSEs |
| 41 Agency/GSE mortgage pools | 47 Credit unions | 50 **Other financial business** | 51 P&C insurers |
| 52 Insurance companies | 54 Life insurers | 55 Closed-end funds | 56 ETFs |
| 57 Private pension funds | 59 Pension funds | 61 Finance companies | **62 Hedge funds** |
| 63 Money market funds | 64 Mortgage REITs | 65 Mutual funds | 66 Broker-dealers |
| 67 ABS issuers | 70 Private depositories | 71 Central bank | 73 Holding companies |
| 74 Banks in US-affiliated areas | 75 Foreign banking offices in US | 76 US-chartered depositories | 79 Domestic financial |
| 88 All domestic sectors | 89 All sectors | **90 Instrument discrepancies** | |

**Digit 4 of the nine-digit code is the asset/liability flag: `0` = asset, `1` = liability.** Verified across 1,536 asset-side and 745 liability-side series; the pairing is exact — `103065005` (NFC total mortgages, asset) ↔ `103165005` (liability); `103070005` (trade receivables) ↔ `103170005` (trade payables).

**Table-number grammar** (published): prefix `M` matrix / `D` debt / `S` sector / `F` instrument, then the SNA code, then suffix `t` transactions, `s` stocks, `b` balance sheet, `r` changes in net worth, `g` growth rates, `e` equity/debt detail, `i.a`/`i.q` Integrated Macroeconomic Accounts annual/quarterly, `t.c`/`s.c` coded matrices.

---

## 3. THE NONFINANCIAL CORPORATE TABLE AND THE FINANCING GAP

**Table: `S11.1.t` (old F.103), transactions, SAAR. Companion stock table `S11.1.s` (old L.103), balance sheet `S11.1.b` (old B.103), net-worth changes `S11.1.r` (old R.103), IMA `S11.1.i.q`/`S11.1.i.a` (old S.5.q/S.5.a).**

Line map of `S11.1.t` (58 lines) — the ones that matter:

| Line | Mnemonic | Content |
|---|---|---|
| 6 | `FA106006065` | Foreign earnings retained abroad (FERA) |
| 7 | `FA105440005` | Net capital transfers **paid** |
| 8 | `FA106000105` | **Gross saving incl. FERA less net capital transfers paid** |
| 9 | `FA105090005` | Gross investment |
| 10 | `FA105050005` | **Total capital expenditures** |
| 11 | `FA105019005` | Gross fixed investment |
| 14 | `FA105000005` | **Net lending (+) / borrowing (−), financial account** |
| 39–46 | `FA104122005`, `FA103163005`, `FA104135005`, `FA103168005`, `FA103169005`, `FA103165005` | debt securities / corporate bonds / total loans / depository loans n.e.c. / other loans and advances / mortgages, all liability |
| 47 | `FA103170005` | Trade payables |
| 55 | `FA103164105` | Corporate equities, liability (**negative = net buybacks**) |
| 57 | `FA107005005` | **Sector discrepancy** |
| 58 | `FA105005305` | **Financing gap** |

**The financing gap is published; you do not have to construct it.** But construct it anyway as a check, because the identity is exact:

```
financing gap = line 10 − (line 8 − line 6)
             = capital expenditures − (gross saving incl. FERA less NCT paid − FERA)
```

Recomputed for the last ten quarters, the identity holds to ±$1m (rounding) in every quarter. Recent values, $m SAAR:

| | capex (10) | gross saving (8) | FERA (6) | NCT paid (7) | **gap (58)** | net lending (14) | sector disc (57) |
|---|---|---|---|---|---|---|---|
| 2024:Q4 | 2,936,715 | 3,108,975 | 178,544 | −27,667 | **6,284** | 598,421 | −426,161 |
| 2025:Q1 | 3,165,153 | 3,075,644 | 52,615 | −28,252 | **142,124** | 375,394 | −464,903 |
| 2025:Q2 | 2,993,219 | 3,071,355 | −171,707 | 1,907 | **−249,844** | −700,259 | 778,396 |
| 2025:Q3 | 3,042,531 | 3,227,901 | −67,451 | 3,302 | **−252,822** | −681,091 | 866,462 |
| 2025:Q4 | 3,101,771 | 3,361,815 | 95,607 | 34,085 | **−164,438** | 610,069 | −350,025 |
| 2026:Q1 | 3,199,548 | 3,978,741 | 144,283 | −558,933 | **−634,910** | 969,568 | −190,375 |

Annual averages of the quarterly SAAR gap: 2019 −13,531; 2020 −140,001; 2021 −168,164; 2022 +265,020; 2023 +7,749; 2024 +97,749; 2025 −131,245.

**Read this carefully before you use it, because the headline is a trap.** The 2026:Q1 gap of −$635bn (internal funds exceeding capex by that much) is dominated by a single line: net capital transfers *received* of $558,933m SAAR. The preceding sixteen quarters of that series run between −$47,889m and +$103,700m. Strip the capital transfer out and the underlying gap is:

```
3,199,548 − (3,419,808 − 144,283) = −75,977
```

i.e. roughly −$76bn, not −$635bn. **Eighty-eight percent of the apparent 2026:Q1 internal-funding surplus is one non-operating capital transfer.** Report the gap on both bases or you will mislead. Similarly, the negative 2025:Q2–Q3 gaps are driven by *negative* FERA (−171,707 and −67,451), which is a repatriation/accounting artefact, not operating cash flow.

**Second identity, also exact:** `sector discrepancy = gross saving (8) − gross investment (9)` and `gross investment (9) = capex (10) + net lending, financial account (14)`. Verified 2026:Q1: 3,978,741 − 4,169,116 = −190,375 = `FA107005005`. This is worth internalising: for the corporate sector the flow-of-funds measure of borrowing and the NIPA measure of the saving-investment balance disagree by **$190bn to $866bn SAAR quarter to quarter**. The sector discrepancy table is `S0.t` (old F.7), 21 lines, one per sector.

**For the operator's puzzle, the relevant facts from this table, 2026:Q1:** NFC corporate bonds outstanding `FL103163005` = 8,036,583 ($8.04tn, from $7.80tn a year earlier); total loans liability `FL104135005` = 5,510,767; depository institution loans n.e.c. `FL103168005` = 1,184,780 (from 1,061,735 — +11.6% y/y); other loans and advances `FL103169005` = 2,850,427. Net equity issuance `FA103164105` turned **positive** at +124,412 SAAR in 2026:Q1 after eight straight quarters of net retirement (−646,776 in 2024:Q1). Domestic nonfinancial business debt grew **7.0% SAAR** in 2026:Q1, nonfinancial corporate alone **8.8%**, against household debt at **2.6%**.

---

## 4. SECTORAL FINANCIAL BALANCES (GODLEY)

There are **two** net-lending measures per sector and they are not the same number. You must state which one you are using.

### 4a. Capital-account basis (IMA) — the Godley identity proper

Source table **`S1.2.i.q` / `S1.2.i.a`** ("Selected aggregates for total economy and sectors", old S.2.q / S.2.a). Lines 38–46:

| Sector | Capital-account net lending |
|---|---|
| All domestic sectors | `FU885000985` |
| Households & nonprofits | `FU155000905` |
| Nonfinancial noncorporate | `FU115000905` |
| Nonfinancial corporate | `FU105000905` |
| Domestic financial | `FU795000995` |
| Federal government | `FU315000995` |
| State & local | `FU215000995` |
| **Rest of the world** | `FU265000905` |
| GDP statistical discrepancy | `FU087005995` |

**The identity closes exactly on annual data.** Recomputed (`.A` series, $m):

| Year | Σ domestic | ROW | statistical discrepancy | **residual** |
|---|---|---|---|---|
| 2019 | −511,185 | 454,148 | 57,037 | **0** |
| 2020 | −691,299 | 570,717 | 120,582 | **0** |
| 2021 | −914,347 | 876,515 | 37,832 | **−1** |
| 2022 | −1,001,838 | 1,002,240 | −401 | **+1** |
| 2023 | −1,271,195 | 945,340 | 325,857 | **+2** |
| 2024 | −1,473,428 | 1,177,132 | 296,296 | **0** |
| 2025 | −1,364,010 | 1,134,388 | 229,623 | **+1** |

So: **Σ(domestic sector balances) + ROW balance + GDP statistical discrepancy = 0**, to rounding. Note the sign convention: `FU265000905` positive means the *rest of the world* is a net lender, i.e. the US runs a current-account deficit. And note that the statistical discrepancy is **not** a rounding term — it was $326bn in 2023 and $296bn in 2024. It is a full sector in magnitude.

**Quarterly it does not close**, and you need to know why before you publish a quarterly chart. Recomputed 2025 quarters (`.Q`, NSA quarterly amounts): residuals +22,140 / −21,033 / −22,831 / +21,726 — **summing to +2 over the year.** The quarterly non-closure of roughly ±$22bn is purely an artefact of how the discrepancy is allocated across quarters in seasonal adjustment. The Board says so directly: "differences in seasonal adjustment procedures sometimes result in quarterly discrepancies that partially or completely offset each other in the annual data." Do the Godley decomposition on **four-quarter sums or annual data**, never on a single quarter.

Latest annual, 2025: government (federal + S&L) −$1,116bn combined on this basis (`FU315000995` −$1,908bn-scale figures are quarterly; the 2025 annual federal balance is the dominant term), private domestic in surplus, ROW +$1,134bn. 2026:Q1 quarterly detail: HH +284,721; nonfinancial noncorp +66,557; NFC +72,606; domestic financial +169,513; federal −602,672; state & local −54,729; ROW +231,062; statistical discrepancy −133,080.

### 4b. Financial-account basis — and why it is worse

Source: the flow-of-funds matrix `M3.t` (files `csv/M3t_Q.csv`, `csv/M3t_A.csv`), or each sector's own `.t` table, line "net lending (+) or borrowing (−) (financial account)": `FA155000005` (HH), `FA145000005` (nonfinancial business, combined — the matrix does **not** carry `FA105000005` and `FA115000005` separately), `FA315000005` (federal), `FA215000005` (S&L), `FA795000005` (domestic financial), `FA265000005` (ROW), `FA895000005` (all sectors), `FA905000005` (instrument discrepancies).

Recomputed, $m SAAR:

| | HH | Nonfin bus | Federal | S&L | Domestic fin | ROW | **All sectors** | **Instrument disc** |
|---|---|---|---|---|---|---|---|---|
| 2019:Q4 | 2,298,846 | 162,921 | −1,127,623 | −404,070 | 78,614 | 206,154 | 1,214,842 | −1,214,842 |
| 2024:Q4 | 1,478,965 | 505,423 | −2,454,832 | −295,850 | −52,652 | 1,125,620 | 306,674 | −306,674 |
| 2025:Q3 | 1,695,997 | −767,717 | −2,163,708 | −389,398 | 386,915 | 1,459,399 | 221,487 | −221,487 |
| 2025:Q4 | 434,850 | 526,509 | −1,593,949 | −375,933 | 127,729 | −344,155 | −1,224,949 | +1,224,949 |
| 2026:Q1 | 2,246,009 | 980,680 | −2,670,491 | −334,250 | 947,742 | 1,057,846 | 2,227,535 | −2,227,535 |

**The identity that closes here is `FA895000005 + FA905000005 = 0` — every sector's financial-account balance summed, plus the instrument discrepancy, is zero by construction.** The instrument discrepancy is running **$0.2tn to $2.2tn SAAR**. That is not noise around a well-measured system; it is the honest statement that the Fed cannot reconcile who lent to whom by roughly one to two trillion dollars a year.

**Where the non-closure lives** — table `F0.t` (old F.8), 14 lines, 2026:Q1 SAAR:

| Component | 2025:Q4 | 2026:Q1 |
|---|---|---|
| `FA903090005` **Total miscellaneous assets** | **+2,612,575** | **−3,046,125** |
| `FA902050005` Fed funds and repo | −1,049,788 | +575,905 |
| `FA903078005` Taxes receivable | −422,547 | −219,998 |
| `FA904010005` Interbank | +75,412 | +189,017 |
| `FA907005005` Total discrepancy | +995,518 | −2,514,576 |

Two of the three largest discrepancies in the entire US financial accounts are **miscellaneous claims** and **repo**. Both are exactly where the operator's question lives.

---

## 5. WHERE THE NBFI SECTORS SIT, AND HOW COARSE THEY ARE

Sector tables in the current release, with the old numbers:

| New | Old | Sector |
|---|---|---|
| `S123.s/.t` | L.121/F.121 | Money market funds |
| `S124.1` | L.122/F.122 | Mutual funds |
| `S124.2` | L.123 | Closed-end funds |
| `S124.3` | L.124 | ETFs |
| `S124.4` | L.129 | Mortgage REITs |
| **`S124.7.b`** | **B.101.f** | **Hedge funds — balance sheet only, no transactions table** |
| `S125s1.1` | L.125 | GSEs |
| `S125s1.2` | L.126 | Agency/GSE mortgage pools |
| `S125s1.3` | L.127 | **Issuers of ABS** |
| `S125s2.1` | L.128 | **Finance companies** |
| `S125s3` | L.130 | **Security brokers and dealers** |
| `S125s5.s` | L.132.c | Central clearing counterparties |
| `S127.1` | L.131 | Holding companies |
| **`S127.2`** | **L.132** | **"Other financial business"** |
| `S1281`, `S1281.1`, `S1281.2` | L.116, L.116.g, L.116.s | Life insurers, general and separate accounts |
| `S1282.1` | L.115 | P&C insurers |
| `S129.*` | L.117–L.120 | Pension funds, DB/DC split |

### What does not exist, stated flatly

I scanned all 286 data dictionaries — every series description in the release — for the strings *private equity*, *private credit*, *business development*, *private fund*. **Zero hits.** There is no private equity sector, no private credit sector, no BDC sector, no interval-fund sector, and no direct-lending instrument anywhere in the Z.1. Anyone who tells you to "check Z.1 for private credit" has not checked Z.1.

**Derivatives are effectively absent.** The same scan for *derivativ* returns exactly six series across four concepts:
- `FL263098013` / `FL263198013` — Rest of the world, financial derivatives **gross at fair value**, asset $1,967,834 and liability $1,959,210 at **2025:Q4** (one quarter stale)
- `FL623098003` — Hedge funds, total long exposure financial derivatives
- `FL664169305` — Broker-dealers, "derivatives, commodities, and other miscellaneous sold short," a *combined* liability line

There is no notional anywhere, no interest-rate or FX category, no counterparty structure, no gross-vs-net presentation. The $148.65tn FX derivatives book and the $846tn global OTC total have no representation in the US financial accounts at all.

### The hedge fund table, and a correction

`S124.7.b` is a 34-line **balance sheet**, quarterly, built from **SEC Forms PF and ADV**, and the release states its data run **through 2025:Q4** — one quarter behind everything else in a 2026:Q1 release. Values at 2025:Q4: total financial and nonfinancial assets `FL622000623` = 3,596,778; total financial assets `FL624090005` = 3,442,787; total loans liability `FL624135005` = 1,098,114.

**Correction for the margin/prime-brokerage channel:** the mnemonic in circulation, `FL624123035`, **does not exist in the current release** (it was one of the 2026q1 deletions when repo was folded into loans). The correct current series is **`FL624135035`, "Hedge funds; loans, total secured borrowing via prime brokerages (margin accounts); liability" = 774,026 at 2025:Q4**, up from 536,466 at 2024:Q4 (+44.3%). The domestic/foreign split `FL623167003` / `FL623169533` is unchanged and correct. Note this series is **not on FRED**.

### "Other financial business" (S127.2) is not the catch-all people assume

Total financial assets `FL504090005` = **1,529,292** at 2026:Q1 (up from 1,324,646 a year earlier). But read the 31 line descriptions before using it as a residual: they name *central clearing counterparties*, *COVID-19 Municipal Liquidity Facility*, *TALF I/II LLC*, *PPIP funds*, *Main Street Facilities LLC*, *Exchange Stabilization Fund equity in Federal Reserve credit facility LLCs*, and *corporate bonds where the proceeds are down-streamed to broker-dealer subsidiaries by investment banks that are holding-company parents*. Its "other loans and advances; asset" line `FL503069005` is **99,278** — under $100bn. This sector is crisis-facility plumbing and CCP infrastructure. It is not where private credit hides. The release itself says: "Estimates are largely residual, derived from other sectors' data."

### Where nonbank corporate credit actually sits: table `F4.6` (old L.216/F.216), "Other loans and advances"

This 66-line instrument table is the most useful single page in the Z.1 for the shadow-credit question. 2026:Q1 stocks, NFC as issuer, from the FWTW cut (§7):

| Holder of NFC "other loans and advances" ($2,850,427 total) | $m |
|---|---|
| **Rest of the world** (`FL263069500`) | 1,192,393 |
| Finance companies (`FL613069505`) | 706,410 |
| ABS issuers (`FL673069803` syndicated + `FL673069505` securitised business loans) | 361,947 |
| Federal government | 259,538 |
| **Households and nonprofits** (`FL153069803`) | **130,993** |
| Mutual funds (`FL653069803`) | 103,444 |
| Broker-dealers (`FL663069803`) | 58,740 |
| Life insurers, general accounts (`FL543069873`) | 36,766 |
| Other financial business (`FL503069805`) | 10,155 |

**Correction to a claim in circulation:** `FL153069803` is *not* a generic household residual for private credit. Its published title is **"Households and nonprofit organizations; syndicated loans to nonfinancial corporate business; asset"** — a specifically defined line within the syndicated-loan block (lines 45–51 of `F4.6`), sitting alongside identical syndicated-loan lines for life insurers, mutual funds, ABS issuers, broker-dealers and other financial business. It is the *unallocated* end of the shared-national-credit syndicated loan estimate, not a catch-all for direct lending. At $130,993 it is far too small to carry a $1.4tn private credit book, and it is not intended to. The correct statement is that direct lending by nonbank funds is **absent**, not misclassified.

**Broker-dealer funding leg**, `S125s3` (old L.130): `FL663168005`, "Security brokers and dealers; depository institution loans n.e.c.; liability" = **589,456** at 2026:Q1, from 404,207 a year earlier (+45.8%). Margin receivables: `FL663067005` (customers and noncustomers) and `FL663067003` (customers only), both in `F4.6` lines 35–36.

**Finance-company warehouse proxy:** `FL613168005`, "Finance companies; depository institution loans n.e.c., including loans through the Paycheck Protection Program Liquidity Facility (PPPLF); liability" — note the PPPLF is still inside the definition.

---

## 6. REST OF THE WORLD (`S2.s` / `S2.t`, old L.133 / F.133) — 53 lines

The single most under-used table for this project. Selected 2026:Q1 stocks:

- `FL263069563` **"Rest of the world; U.S. nonfinancial business loans held by CLOs; asset"** = **658,951** (from 633,188 a year earlier). This is the offshore-CLO collateral pool — Cayman-issued vehicles holding US corporate loans.
- `LM263163063` **"Rest of the world; bonds: collateralized loan obligations; liability"** = **598,112** (from 550,468). This is the *other side of the same vehicles* — US residents' holdings of the notes those CLOs issued. **`FL263069563` and `LM263163063` are the asset and liability sides of one balance sheet. Never add them.**
- `FL263140005` "Rest of the world; life insurance reserve credit from non-U.S. reinsurers; liability" = **140,215** — the ROW mirror of the US cedant's `FL543076035` = **1,125,345** (life insurers' reserve credit reinsured to non-US reinsurers).
- `FL263098013` / `FL263198013` — the only derivatives in the accounts, 2025:Q4.

**On offshore reinsurance: the common claim that Z.1 "misses offshore cessions entirely" is wrong and should be corrected.** Z.1 carries them explicitly, on a **reserve-credit basis** (`FL543076035`, `FL543141905`, `FL543151905`, `FL263140005`, `FL263150005`, `FL263176005`). What it misses is *modco and funds-withheld coinsurance*, because reserve-credit accounting does not recognise them. That is a basis limitation, not an absence, and it is exactly why the Z.1 cession flow printed **negative in 2025** while commercial sources reported a record deal year. State the basis and the contradiction resolves into a known measurement difference rather than an unexplained gap.

---

## 7. WHO OWES WHAT TO WHOM: THE FWTW FILE

The Z.1 proper gives you sector-by-instrument, not sector-to-sector. The Board's **Issuer-to-Holder (From-Whom-to-Whom)** Enhanced Financial Account closes that:

```
https://www.federalreserve.gov/releases/efa/fwtw.htm
https://www.federalreserve.gov/releases/efa/fwtw_data.csv    (77.8 MB, 921,121 rows, verified)
https://www.federalreserve.gov/releases/efa/fwtw_templates.xlsx
```
Columns: `Instrument Name, Instrument Code, Holder Name, Holder Code, Issuer Name, Issuer Code, Date, Level`. Coverage 1945Q4 through 2026Q1, updated 18 June 2026.

**Read the methodology caveat and repeat it every time you use the file.** From the Board's own page: "FWTW relationships for a given instrument begin with underlying Accounts detail where both the issuer and holder are identified, and then **the remaining issuance for that instrument is split proportionally across holders**." It is levels only — "FWTW estimates for transactions, revaluations, and other volume changes are under development." So the identified portion is observed; the remainder is a proportionality assumption. It aggregates exactly to the published Z.1 totals by construction, which means agreement with Z.1 is not evidence of accuracy.

Worked example, holders of nonfinancial corporate business liabilities at 2026:Q1 ($m):

| Instrument | Total | Largest holders |
|---|---|---|
| Corporate & foreign bonds | 8,036,583 | **Rest of world 3,094,914**; life insurers 1,508,358; mutual funds 1,122,251; pensions 637,988; ETFs 612,278; P&C 392,818; US banks 291,056 |
| Unidentified misc. financial claims | **12,101,882** | NFC itself 7,436,191; nonfin noncorp 4,201,860; pensions 1,425,434 |
| Trade credit | 4,523,214 | NFC 3,234,897; nonfin noncorp 813,270; ROW 345,670 |
| Other loans and advances | 2,850,427 | ROW 1,192,393; finance cos 635,014; ABS 361,947 |
| Commercial mortgages | 1,202,775 | US banks 672,042; ABS 155,440; life 153,513 |
| Depository loans n.e.c. | 1,184,780 | US banks 921,600; **foreign banking offices in US 252,417** |

Other EFA projects worth knowing (all at `/releases/efa/`): **Funding Agreement-Backed Securities** (updated 18 June 2026 — the FABS series the insurance channel runs on), **Hedge Funds**, **Money Market Funds holdings detail by month**, **Equity Issuance and Retirement**, **Syndicated Loan Portfolios of Financial Institutions** (last updated **20 September 2024** — stale, flag it), Depository Institutions consolidated and **off-balance-sheet items** (16 January 2026), Distributional Financial Accounts.

---

## 8. LIMITATIONS — STATED WITHOUT HEDGING

**What Z.1 nets.** The release is candid that "the source data for a sector cannot disentangle issuance and holdings, and only the difference is available" for a number of instruments — which is why FWTW levels can go negative. Broker-dealer repo is on a **US GAAP ASC 210-20 offset basis**, not gross: the Z.1 dealer repo liability is a small fraction of the OFR's gross $12.5tn market measure. Broker-dealer "unidentified miscellaneous" runs **negative** (`FL663193005` = −439,865; `FL663093005` = −351,250) because the sector is a residual against FOCUS aggregates.

**What Z.1 cannot see, quantified.** This is the number to give the operator:

| 2026:Q1 | $m |
|---|---|
| All sectors, **unidentified miscellaneous assets** `FL893093005` | **23,532,650** |
| All sectors, **unidentified miscellaneous liabilities** `FL893193005` | **18,636,711** |
| Instrument discrepancy, total miscellaneous assets `FL903090005` | **−4,895,939** |

**$23.5tn of assets and $18.6tn of liabilities in the US financial accounts are labelled "unidentified," and the two sides fail to reconcile by $4.9tn.** Of the liability side, nonfinancial corporate business alone carries $12,101,882 and nonfinancial noncorporate $4,434,951. Table `F89.3c` (old L.235) lists all 40 lines. If you want a single defensible upper bound on how much of the US financial system the flow of funds cannot identify, this is it — and it grew $1.88tn on the asset side in one year (from 21,649,093 at 2025:Q1).

**Three known deviations from SNA**, stated by the Board: consumer durables are treated as investment not consumption; nonfinancial noncorporate business is a separate sector rather than being folded into households; **some debt securities are carried at book value rather than market value**.

**Residual sectors.** Two of the most-cited sectors are explicitly residuals: households and nonprofits ("Estimates are largely residual, derived from other sectors' data") and other financial business ("Estimates are largely residual"). Any measurement error anywhere else in the system lands in the household sector.

**Revisions.** "There is no specific revision schedule; rather, data are revised on an ongoing basis." Seasonal factors are recalculated **only with the December release of third-quarter data**, using X-13-ARIMA on the most recent 10 years. There is no vintage database — you must snapshot `/releases/z1/YYYYMMDD/z1_csv_files.zip` yourself.

**Lag, and the source-data lag behind the lag.** The release is published "about 10 weeks following the end of each calendar quarter," second week of March/June/September/December. **That schedule broke recently:** 2025:Q3 data were released **9 January 2026**, not December 2025. Verified release sequence: 20250313 (2024:Q4), 20250612 (2025:Q1), 20250911 (2025:Q2), **20260109 (2025:Q3)**, 20260319 (2025:Q4), 20260611 (2026:Q1).

The headline lag understates the real one. From the release's own "Description of Most Recent Data Available":

| Sector | Actual source vintage in the 11 June 2026 release |
|---|---|
| Nonfinancial corporate | Census QFR through 2026:Q1; **IRS/SOI through 2023** |
| Nonfinancial noncorporate | **IRS/SOI through 2023**; farm data through 2024 |
| Households / nonprofits | Largely residual; **IRS/SOI 501(c)(3-9) through 2022**; private foundations **through 2021** |
| **Hedge funds (S124.7.b)** | **SEC Forms PF and ADV through 2025:Q4** |
| State & local governments | Census total financial assets **through 2021:Q2**; asset detail from CAFRs **through 2019:Q2** |
| Private pension funds | **Form 5500 through 2023**; BEA actuarial through 2024:Q4 |
| S&L pensions | Annual survey **through 2024:Q2** |
| Other financial business | Residual; CCP data annually through 2025:Q4 |
| Rest of the world | TIC through 2026:Q1; **IIP and ITA through 2025:Q4** |
| Life / P&C insurers | 2026:Q1, **NJ-domiciled firms extrapolated** |

So "2026:Q1 state and local government financial assets" is an extrapolation from a 2021 Census benchmark. **The nominal 10-week lag is real for banks, the central bank, MMFs and Treasury; it is a fiction for households, noncorporate business, pensions and state and local government.**

---

## 9. CHECKLIST FOR THE OPERATOR'S QUESTION

1. **Z.1 is a money-and-credit *stock* system, not a money system.** It does not contain M1–M3 and it does not measure "money creation." What it does uniquely is close the who-owes-what-to-whom loop — and the size of the failure to close (`FA905000005`, $0.2–2.2tn SAAR; unidentified miscellaneous, $23.5tn vs $18.6tn) is the honest measure of how much shadow credit sits outside the frame.
2. **Use `FA` for flows, `FL`/`LM` for stocks, and decompose any stock change as `FC = FU + FR + FV` before calling anything credit.** Valuation is `FR`.
3. **Do sectoral balances annually on the capital-account basis** (`FU*000905`/`*000995` from `S1.2.i.a`), where the identity closes to ±$2m. Quarterly it misses by ~±$22bn purely from seasonal allocation.
4. **Publish the financing gap two ways** — as printed (`FA105005305`) and net of net capital transfers. In 2026:Q1 that is the difference between −$635bn and −$76bn.
5. **Do not look for private credit, private equity, BDCs, NAV lending, subscription lines, SRT, FX swaps or derivatives notionals in Z.1. They are not there.** The nearest observable proxies are `FL613168005` (bank loans to finance companies), `FL663168005` (bank loans to broker-dealers, +45.8% y/y), `FL263069563` (offshore CLO loan collateral), and `FL624135035` (hedge fund prime-brokerage borrowing, one quarter stale). Everything else routes to H.8 line 26, Call Report RC-C M.10.a–e, and FR Y-14 — which is another channel's territory.
6. **Any code beginning `x4023005` or `x4123005` in an existing pipeline is dead as of 11 June 2026**, and its successor `x4035005` / `x4135005` includes repo. Re-baseline before comparing.

**Files retained locally for the parent agent:**
- `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/z1csv/` — full unpacked 11 June 2026 release (286 CSVs + 286 dictionary files)
- `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/z1_table_mapping.csv` — old→new table crosswalk
- `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/z1_code_changes.txt` — full mnemonic change log, 2009q4–2026q1
- `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/fwtw_data.csv` — FWTW issuer-to-holder, 921,121 rows through 2026Q1

---

## Published shadow-money aggregates

## EVERY PUBLISHED ATTEMPT AT A SHADOW-MONEY / NEAR-MONEY AGGREGATE

**Verification status.** WebSearch budget was exhausted at the first call, so everything below was obtained by direct WebFetch/curl against primary URLs and, where the fetcher returned raw PDF, by local `pdftotext -layout` extraction. Every figure marked ✔ was read off the primary document in this session. Items marked ✖ I could not reach (403/404) and I give no numbers for them. Local extracts are at `/tmp/pozsar.txt`, `/tmp/fsr.txt`, `/tmp/fsb.txt`, `/tmp/gorton.txt`, `/tmp/gabor.txt`, `/tmp/xiao2.txt`, `/tmp/boj.txt`, `/tmp/bojms.txt`, `/tmp/cfs.txt`, `/tmp/kvj.txt`.

---

## PART 1 — THE CATALOGUE

### 1. Pozsar, "Shadow Banking: The Money View", OFR WP 14-04, 2 July 2014 ✔
`https://www.financialresearch.gov/working-papers/files/OFRwp2014-04_Pozsar_ShadowBankingTheMoneyView.pdf`

**Definition.** A 2×2 *Money Matrix* (Figure 1, p.15) over two axes: assets backing the claim (public vs private) and backstop (public vs private). Four cells:
- **Public money** — currency, reserves, T-bills.
- **Insured money** (private-public) — insured bank deposits.
- **Public shadow money** (public-private) — overnight repo collateralised by Treasuries/agency debt/agency RMBS issued by dealers' *government* desks, plus CNAV shares of government-only money funds.
- **Private shadow money** (purely private) — repo collateralised by credit-risky private securities issued by dealers' *credit* desks, prime-fund CNAV shares, **and uninsured bank deposits**.

Cross-cut by tenor: *par on demand* (PD0–PD3) vs *par at maturity* (PM0–PM3). He proposes those eight cells as the template for extending the Fed's aggregates.

**Measurement, Q3 2013** ✔ (Charts 1 and 2, sourced to Haver / FRB / FRBNY / FDIC / US Treasury — *not* to Z.1):
- Par-on-demand: private shadow money **$3.2trn** (uninsured demand deposits + o/n private repo + prime CNAV); public money ~**$2.6trn**; public shadow money **$2.3trn**; insured money **$1.4trn**.
- Par-at-maturity: insured **$6trn**; public **>$2.3trn**; private shadow **>$1.2trn** (mostly large TDs); public shadow **~$0.8trn**.
- **Core of the shadow banking system: just under $5trn at Q3-2013, down from over $8trn at Q2-2008.** Explicitly *net* of intermediary cross-holdings, and explicitly narrower than Pozsar et al (2010)'s ~$20trn gross figure — he says the earlier numbers were "gross, not netting for holdings between intermediaries."
- Institutional cash pools: **at least $6trn** under management at end-2013.

**Maintained?** No. One-off working paper. Pozsar left OFR. **No successor series exists.**
**Replicable?** Partially. Charts 2 note explicit netting ("netted for large time deposits, term repos and Treasuries held by money funds") but the netting rule is not specified line-by-line, and the "uninsured demand deposits" input is FDIC noninterest-bearing transaction accounts >$250k, a series that has changed since TAG expired. Rebuilding it is a research project, not a pipeline.
**What it actually measures:** a **liability-side** stock of money claims, restricted to the *net supply to outside investors*. This is the only entry in the catalogue whose perimeter matches the question the operator is asking.

---

### 2. Gabor & Vestergaard, "Towards a theory of shadow money", INET, 2016 ✔
`https://www.ineteconomics.org/uploads/papers/Towards_Theory_Shadow_Money_GV_INET.pdf`

**Definition (verbatim from the abstract):** "we define shadow money as **repo liabilities supported by tradable collateral**." Four claimed properties: (a) repo is nearer settlement money than ABCP or MMF shares, because an "intricate collateral valuation mechanism" — haircuts, mark-to-market, margin calls — maintains at-par exchange; (b) *banks* issue shadow money, to economise on deposits and reserves; (c) it relies on the state supplying the tradable base asset; (d) repos create and destroy liquidity lower in the hierarchy.

**Has anyone operationalised it? Effectively no, and the paper explains why.** The paper itself constructs **no aggregate**; it borrows others' figures (US repo "~USD 10trn by mid-2008", Singh & Aitken; European repo EUR 7trn outstanding 2015). Its footnote 14 is the decisive measurement point: LCH Clearnet SA cleared **EUR 13trn of repo per month in 2015 against EUR 7trn outstanding in the whole European market**, and it warns that CCP multilateral netting means "balance sheet data … may significantly underestimate gross repos on banks' balance sheets." Their Table 1 shows LCH Clearnet SA with EUR 246,066m of repos receivable against EUR 246,066m payable — a pure gross-up that nets to zero in any consolidated statistic.

That is the fatal operationalisation problem: on the Gabor-Vestergaard definition the aggregate you want is *gross* repo liabilities to outside holders, but every available statistic is either GAAP-netted (Z.1 broker-dealer repo), CCP-netted, double-counted across both legs (FICC DVP), or gross-of-both-legs from a rotating survey panel (ICMA).

**Downstream attempts I could identify (OpenAlex, verified metadata only):**
- Murau (2017), *Review of International Political Economy* 24(5), DOI 10.1080/09692290.2017.1325765 ✔ (abstract): treats **three** forms of shadow money — MMF shares, overnight repo, ABCP — and traces which were absorbed into the public money supply by 2007-14 backstops. Qualitative/institutional; no aggregate.
- Murau & Pforr, "Private Debt as Shadow Money? Conceptual Criteria, Empirical Evaluation and Implications for Financial Stability", SSRN 4264552 (2020) ✖ — **full text not retrievable this session** (SSRN 403). This is the closest thing to a published operationalisation and it should be run down before you conclude none exists. I will not characterise its criteria from memory.
- Michell, "Do Shadow Banks Create Money?", *Metroeconomica* (2016), DOI 10.1111/meca.12149 ✔ (abstract): argues bank and shadow-bank credit creation are *symbiotic*, not additive — the circuit "operates in a perverse form in which household debt is stored on the balance sheets of shadow banks." Theory; no aggregate. Full text ✖ (UWE eprints DNS failure).

---

### 3. Sunderam, "Money Creation and the Shadow Banking System", *RFS* 28(4), 2015 ✔ (abstract only; PDF ✖)
DOI 10.1093/rfs/hhu083.

**What it is not:** it is not an aggregate. Per the abstract: "This paper assesses a **key premise** of this argument: that investors actually treated short-term debt issued by shadow banks as a money-like claim." It builds a model in which the financial sector and the central bank *jointly* respond to money demand, generating joint predictions on **prices and quantities of T-bills, reserves and shadow bank debt** (the instrument is ABCP), and tests them.

**Use for this project:** it is the empirical warrant for treating a shadow-bank liability as money — a *test of moneyness*, not a *measure of money*. Cite it for the claim "these instruments are money-like"; do not cite it for a level.

---

### 4. Krishnamurthy & Vissing-Jorgensen ✔
"The Demand for Treasury Debt", NBER WP 12881 (Jan 2007), published as "The Aggregate Demand for Treasury Debt", *JPE* 120(2), 2012.
`https://www.nber.org/system/files/working_papers/w12881/w12881.pdf`

**The aggregate they construct is a supply variable and a price, not a money stock.** Supply = log(US **Debt/GDP**). The "money-likeness" is measured as a **convenience yield**: the AAA–Treasury spread, the CP–bill spread, swap spreads, BAA–Treasury. They trace a downward-sloping demand curve for convenience and estimate its elasticity; disaggregated demand curves come from **Flow of Funds holder sectors**. Magnitudes: a one-standard-deviation change in Debt/GDP moves the relevant spread by ~**1.5bp to 4.25bp** per unit in the reported specifications.

**This is routinely mis-cited.** KVJ did *not* build an aggregate of money-like assets. The companion paper that *does* construct a financial-sector short-term-debt quantity from the Flow of Funds is "Short-Term Debt and Financial Crises: What we can learn from U.S. Treasury Supply" (2012 WP; *JFE* 2015) — OpenAlex has no OA copy and I could not verify its construction ✖. Do not attribute a quantity series to KVJ 2012.

**Practical use:** the convenience yield is the *price* dual of the quantity you cannot measure. If shadow money supply is expanding faster than demand, safety/liquidity premia compress. That is a live, cheap, daily observable and it is the single best cross-check on any quantity story.

---

### 5. Gorton, Lewellen & Metrick, "The Safe-Asset Share", NBER WP 17777 / *AER P&P* 102(3), 2012 ✔
`https://www.nber.org/system/files/working_papers/w17777/w17777.pdf`

**Definition:** assets "used in an information-insensitive fashion, i.e. as money" — bank deposits, MMF shares, CP, fed funds and repo, short-term interbank loans, Treasuries, agency debt, munis, securitised debt, and high-grade financial-sector corporate debt. The last five are included *because they are repo collateral at zero haircut pre-crisis*.

**Method:** total safe debt ÷ total liabilities-and-equity of all sectors (proxy for total assets), from the Flow of Funds. Adjustments: strip intra-governmental holdings; reclassify non-MBS agency debt from financial to government; remove taxes payable, REIT mortgages, mutual fund shares, life insurance reserves, pension reserves; **apply a flat 85% haircut to MBS, ABS and long-term financial debt**; produce a "high" and a "low" estimate.

**Result:** the safe-asset share is a **constant ~33%** (high estimate regression constant 0.332, s.e. 0.003; low 0.310), Q1 1952 – Q3 2011, with an economically trivial time trend. Bank deposits fell from ~80% of safe *financial* debt in the 1950s–60s to **27% on the eve of the crisis**, 32% at end-2010.

**Replicable? Yes — uniquely so.** The Appendix (pp.13–15 of the WP) is a **line-by-line Z.1 series-identifier table** with Y/N/85%/X flags for both the high and low estimates. It names every series: FL794190005.Q, FL792150005.Q, FL663167005.Q, FL673169105.Q, FL423161705.Q, FL313161105.Q, FL213162005.Q, etc.

**Two cautions.** (a) The 85% haircut is an assumption with no empirical basis stated and it does the analytical work of turning long-term securitised debt into "money"; (b) **every identifier in that appendix is dead**. Per the June-2026 Z.1 renumbering to SNA alphanumeric codes noted by the private-credit and securitisation researchers, the L-tables were renumbered with the 11 June 2026 release and a mapping CSV sits on the Z.1 release page. Anyone rebuilding GLM in 2026 must remap first.

**What it measures:** a **ratio**, not a level, and it deliberately includes long-duration collateral. It answers "has the economy's demand for information-insensitivity changed?" — the answer is no — and it does not answer "how much purchasing power was created."

---

### 6. Xiao, "Monetary Transmission through Shadow Banks", *RFS* 33(6), 2020 ✔ (full text via the SED 2018 conference PDF)
`https://red-files-public.s3.amazonaws.com/meetpapers/2018/paper_616.pdf`

**Definition of shadow money — narrow and explicit:** "shadow money, namely **liquid deposits created by shadow banks**"; "**Shadow banking deposits include retail MMF shares and institutional MMF shares.**" The money aggregate is **MZM**; commercial-bank deposits are demand + savings.

**This is the single most useful footnote in the entire literature for your invariant** (fn. 2, p.2 of the WP): "Other types of shadow banking liabilities, such as **repos and asset-backed commercial paper, are generally not included in the aggregate money supply** because first, they are less liquid than MMF shares, and second, **they are generally held within the shadow banking system rather than being held by households and businesses. Including these short-term shadow banking liabilities in money supply would double count the amount of funds that go into the shadow banking system.**"

**Finding:** shadow money *expands* when the Fed tightens; MMF deposit creation offsets **35 cents** of every dollar of commercial-bank deposit contraction. Data: iMoneyNet (MMF, monthly), Call Report (banks), SCF 2013, FRED, Financial Accounts for household T-bill holdings, 1987–2012.

**Maintained?** No — and note that his aggregate is now partly unbuildable: **MZM and the institutional money fund level series were casualties of the H.6 revision** (see §9).

---

### 7. Bao, David & Han, "The Runnables", FEDS Notes, 3 Sept 2015 → **Federal Reserve Financial Stability Report, Table 4.1** ✔
This is **the only maintained official near-money aggregate anywhere in the world that spans banks and non-banks.**

Origin note ✔: `https://www.federalreserve.gov/econresdata/notes/feds-notes/2015/the-runnables-20150903.html` — runnables are "pay-on-demand" claims that are defaultable private (or state/local) promises without federal insurance. Components and sources as given there: uninsured deposits (Call Reports); MMFs (Z.1 FL634090005.Q); repo (Z.1 FL892150005.Q less adjustments); CP (Z.1 FL893169105.Q); securities lending cash collateral (RMA); fed funds; VRDOs (SIFMA); FABS (Bloomberg + staff estimation). Explicit exclusions: LGIPs, total return swaps, private liquidity funds, tender option bonds, bankers' acceptances, and put-bearing long bonds other than VRDOs.

**Current vintage — Fed FSR, May 2026, Table 4.1, data to 2025:Q4** ✔
(`https://www.federalreserve.gov/publications/files/financial-stability-report-20260508.pdf`, p.36):

| Item | $bn, 2025:Q4 | Growth 2024:Q4–2025:Q4 | Avg annual growth 1997–2025 |
|---|---|---|---|
| **Total runnable money-like liabilities** | **27,033** | **+12.0%** | +5.4% (from 2003:Q1) |
| Domestic MMFs | 7,746 | +13.0% | +6.7% |
| — Government | 6,375 | +13.1% | +15.2% |
| — Prime | 1,220 | +13.1% | +3.7% |
| — Tax exempt | 151 | +11.1% | −0.4% |
| Uninsured deposits | 7,608 | +7.7% | +10.6% |
| Repurchase agreements | 5,887 | +19.1% | +6.1% |
| Commercial paper | 1,368 | +12.2% | +2.9% |
| Securities lending (cash-collateralised only) | 1,201 | +13.8% | +7.5% |
| *(memo, NOT in the total)* Bond mutual funds | 5,032 | +7.7% | +8.0% |

Total = **86% of GDP at end-2025** (Figure 4.1). The note states the total *exceeds* the listed components; the unlisted residual is VRDOs, fed funds, **funding-agreement-backed securities, private liquidity funds, offshore MMFs, short-term investment funds, LGIPs, and stablecoins**. **My arithmetic:** 27,033 − (7,746+7,608+5,887+1,368+1,201) = **$3,223bn in "other"**. Figure-4.1 sources now include **DeFiLlama** — the Fed has formally admitted stablecoins into its near-money measure.

**This is your headline finding for the operator.** A maintained official series says the US stock of runnable money-like liabilities grew **12.0%** in the year to end-2025 against a **5.4%** long-run average — i.e. **2.2× trend** — while M2 grew ~5–6%. Separately, FSR p.42 ✔: life insurers' **nontraditional liabilities** (FABS + FHLB advances + securities-lending and repo cash) = **$531bn at 2025:Q4, +15% in real terms y/y**.

**Vintage caution.** The 2015 note's chart peaked at roughly 80% of GDP in 2008 and sat near 60% through 2015; the 2026 FSR reads 86% and calls it "the middle of their historical range." Those two statements are not reconcilable unless the historical series was restated when VRDOs (Bloomberg, from 2019:Q1), FABS, stablecoins and the fund categories were added. **Treat the runnables series as definitionally non-stationary and do not compare a 2026-vintage level to a pre-2019 published level.**

**Replicable?** Partly. MMFs, repo and CP come from Z.1 series (renumbered June 2026). Uninsured deposits from Call Reports. But securities lending is RMA + S&P (paid), private liquidity funds from SEC Private Fund Statistics, offshore MMFs from iMoneyNet (paid), VRDOs from Bloomberg (paid). **You cannot rebuild Table 4.1 from free data.**

---

### 8. FSB Global Monitoring Report on NBFI 2025 (P161225, 16 Dec 2025, data to end-2024) ✔
`https://www.fsb.org/uploads/P161225.pdf` — 29 jurisdictions, >90% of global GDP.

**Narrow measure at end-2024: $76.3trn, +12.7%, 15.4% of total global financial assets** (Table 0-1):

| EF | Typical entities | $trn | Share | 2024 change |
|---|---|---|---|---|
| EF1 collective investment vehicles susceptible to runs | MMFs, fixed income funds, mixed funds, credit hedge funds, mREITs | 58.1 | 76.1% | +15.1% |
| EF2 lending dependent on short-term funding | finance/leasing/factoring/consumer credit companies | 6.1 | 8.0% | +5.5% |
| EF3 market intermediation dependent on short-term funding | broker-dealers, custodial accounts, securities finance companies | 4.9 | 6.4% | +5.8% |
| EF4 facilitation of credit intermediation | credit insurers, financial guarantors, monolines | 0.1 | 0.2% | +2.5% |
| EF5 securitisation-based credit intermediation | securitisation/structured finance vehicles, ABS | 5.3 | 7.0% | +4.3% |
| Unallocated | other financial auxiliaries | 1.7 | 2.3% | +4.5% |

**Critical for your purposes: this is an ASSET-side measure of ENTITIES, net of prudential consolidation into banking groups. It is not a money aggregate and it is not a liability aggregate.** Annex 5 ✔ confirms the two-step funnel and that step 1 excludes **$164.5trn** of ICs/PFs/auxiliaries/OFIs not classified into any EF (including $34.9trn of equity funds and $20.3trn of captives and money lenders), and step 2 excludes anything prudentially consolidated into a banking group, including self-securitisation.

**And the FSB says in terms** ✔ (Box, p. ~19): "Private credit funds are **not well captured** within the narrow measure … they do not rely on short-term wholesale funding for their activity, which means that they are **not classified into EF1 or EF2 (or any other economic function)**. As to the rest of private finance, it is **excluded from the narrow measure by definition**." Jurisdictions could identify only **~$0.5trn** of private credit against commercial estimates of $1.5–2.0trn.

Note also an internal inconsistency: Table 0-1 gives EF5 growth of **4.3%**, while the securitisation researcher reports Graph 1-6 showing **6.6%**. Flag it; do not average.

---

### 9. Official monetary aggregates broader than M3

**Japan — Bank of Japan, "Broadly-defined liquidity" (L). The only major-economy official aggregate that is genuinely broader than M3, and it is live.** ✔
Definition (Guide to Japan's Money Stock Statistics, Oct 2025, p.1-1, `https://www.boj.or.jp/en/statistics/outline/exp/data/exms01.pdf`):

> **L = M3 + pecuniary trusts + investment trusts + bank debentures + straight bonds issued by banks + commercial paper issued by financial institutions + government securities + foreign bonds**

Latest release ✔ (Money Stock, preliminary July 2026, released 12 Aug 2026, `https://www.boj.or.jp/en/statistics/money/ms/ms2607.pdf`), average amounts outstanding, ¥trn:

| | July 2026 | y/y |
|---|---|---|
| M2 | 1,297.0 | +2.2% |
| M3 | 1,641.2 | +1.4% |
| **L** | **2,338.4** | **+4.4%** |
| — pecuniary trusts | 487.5 | +11.8% |
| — investment trusts | 126.0 | +13.1% |
| — bank debentures | 2.8 | +4.2% |
| — straight bonds issued by banks | 0.3 | +68.2% |
| — CP issued by financial institutions | 0.0 | +166.7% |
| — government securities | 47.2 | +18.8% |
| — foreign bonds | 33.3 | +6.1% |

**My arithmetic: L − M3 = ¥697.2trn, of which pecuniary trusts are 70%. L is growing at 3.1× the rate of M3.** This is exactly the diagnostic the operator is reaching for, and it exists for Japan and nowhere else.

**Two disqualifying caveats he must know.** (i) L's money-holder sector is **non-financial corporations, households and local governments only** — financial institutions, central government and non-residents are excluded. Institutional cash pools are therefore *outside* L by construction. (ii) The 2008 revision **deliberately removed "repurchase agreements and securities lending with cash collateral"** from the former broadly-defined liquidity (Guide, p.1-9). Japan's broadest official aggregate consciously dropped the Gabor-Vestergaard object. And the BoJ itself states ✔ that "figures for broadly-defined liquidity (L) rely more on estimations than do M1, M2, and M3 due to the limitations in data availability."

**Euro area — ECB. No aggregate broader than M3, but M3 already contains shadow money.** ✔ (`https://www.ecb.europa.eu/stats/money_credit_banking/monetary_aggregates/html/index.en.html`) M3 = M2 + **repurchase agreements + MMF shares/units + debt securities with maturity up to two years issued by MFIs**. Money-holding sector = euro area residents other than MFIs and central government. Longer-term liabilities are excluded as "portfolio instruments rather than … a means of carrying out transactions." So a euro-area analyst comparing M3 to US M2 is comparing a measure that *includes* MFI repo and institutional MMF to one that excludes both.

**United States — M3 discontinued.** ✔ (`https://www.federalreserve.gov/releases/h6/discm3.htm`) Announced 10 Nov 2005 (revised 9 Mar 2006), last published **23 March 2006**. Dropped: large-denomination time deposits, RPs, eurodollars, institutional MMFs. Stated reason: M3 "does not appear to convey any additional information about economic activity that is not already embodied in M2."

**And the US measurement base has degraded further since.** ✔ Per the CFS release (p.2) and the H.6 Technical Q&A: the 23 Feb 2021 H.6 overhaul merged savings deposits into "Other liquid deposits" inside M1, ended the commercial-bank/thrift split, moved to monthly publication, ended weekly SA data, and **"announced that the levels of Institutional Money Market Funds will be discontinued."** US government deposits and deposits due to foreign banks were also dropped. **The Fed no longer publishes the single most important non-M2 near-money line in its own money release.** A further live change: from the **28 July 2026** H.6, IRA and Keogh balances are no longer netted from the small-time-deposit and retail-MMF components but netted directly from M2, restated back to series start ✔.

Current H.6 (released 28 July 2026, June 2026, SA, $bn) ✔: M1 19,831.5; M2 23,155.2; currency 2,376.6; demand deposits 7,056.5; other liquid deposits 10,398.5; small-denomination time deposits 1,506.1; retail MMFs 3,047.2; less IRA/Keogh 1,229.7 (estimated).

**My arithmetic, same date (2025:Q4 / Dec-2025):** FSR total domestic MMFs **$7,746bn** vs H.6 retail MMFs **$2,981.4bn** ⇒ roughly **$4.76trn of MMF assets sit outside M2.** (Caveat: the FSR figure is total fund assets from ICI/SEC; H.6 retail MMF is a seasonally adjusted, money-holder-restricted holdings measure. The difference is close to, but is not exactly, institutional MMF.)

**Center for Financial Stability, Divisia M4 — private, monthly, the only broad Divisia series in existence.** ✔ (`https://centerforfinancialstability.org/amfm_data.php`; latest release `amfm/Divisia_Jun26.pdf`, June 2026 data, released 3 Aug 2026, next release 31 Aug 2026.)

Component ladder ✔ (Figure 6/10): DM1 = currency + demand deposits + other liquid deposits; **+DM2** retail MMFs, small time deposits; **+DM3** institutional MMFs, large time deposits, **repurchase agreements**; **+DM4−** commercial paper; **+DM4** T-bills.

June 2026 y/y: DM4 **+6.8%**, DM4− +6.4%, DM3 +6.5%, DM2 +6.1%, DM1 +6.6% (vs DM4 +3.9% a year earlier). Growth-rate weights in DM4: other liquid deposits 37.0%, demand deposits 29.2%, currency 9.9%, large time deposits 7.6%, T-bills 4.6%, small time 4.6%, institutional MMFs 2.4%, **repo 2.3%**, retail MMFs 1.8%, CP 0.8%.

**Three disqualifiers for using this as a shadow-money quantity.** (i) It is an **index, not a level** — "Levels are normalized to equal 100 in Jan. 1967" (Figure 4). DM4 = 2,504.1 is an index number; it is not dollars and cannot be. (ii) It is a **monetary service flow**, weighted by user cost — by construction repo enters at 2.3% weight, so a doubling of repo moves DM4 by ~2%. It answers "how much money-service is the economy getting," not "how much purchasing power exists." (iii) It contains **no eurodollars, no securities-lending cash collateral, no FABS, no GSE debt, no stablecoins**, and its institutional-MMF and repo inputs must now be sourced outside H.6 — CFS does not document the substitute source in the release. Ask them before you build on it.

**Not verified this session** ✖: Bank of England M4/M4ex and Divisia (all BoE URLs returned 403); RBI NM1–NM3 and liquidity aggregates L1–L3; RBA broad money; IMF GFSR Oct 2014 Ch. 2 (entity-based vs "noncore liabilities" measures) and IMF WP 14/10 Errico et al. global flow-of-funds mapping (imf.org 403 with and without UA spoofing); ESRB NBFI Monitor. The BoJ's own cross-country comparison table (Guide, p.1-15) does list a UK category "Liquid assets outside M4" (Channel Islands/IoM deposits, deposits at BIS-area banks, foreign-currency deposits, non-residents' sterling deposits, sterling T-bills ≤6m, local-government temporary debt ≤1y, certificates of tax deposit) and a UK "Divisia money" line — but I could not confirm from the BoE that either is currently published, and the BoJ table may be historical.

---

## PART 2 — WHY THESE CANNOT BE COMBINED

Sort them by what is on the measuring instrument, not by what they are called:

| Measure | Object | Side of balance sheet | Unit |
|---|---|---|---|
| Pozsar money matrix | net money claims to outside investors | liability | $ stock |
| Gabor–Vestergaard | gross repo liabilities on tradable collateral | liability | $ stock (unmeasurable) |
| Gorton–Lewellen–Metrick | information-insensitive debt ÷ total assets | liability, ratio | dimensionless |
| KVJ | convenience yield | neither | basis points |
| Sunderam | comovement of ABCP price/quantity with bills | neither | test statistic |
| Xiao | MMF shares inside MZM | liability | $ stock |
| Fed FSR runnables | pay-on-demand uninsured private claims | liability | $ stock |
| FSB narrow measure | assets of run-prone credit intermediaries | **asset** | $ stock |
| BoJ L | liquid claims held by non-financial money holders | liability, holder-restricted | ¥ stock |
| CFS Divisia M4 | monetary service flow | liability, user-cost weighted | **index** |

Four of the ten are not quantities at all. Two are asset-side. Two are holder-restricted in ways that exclude the wholesale sector entirely. And the two that are directly comparable in principle — Pozsar and the FSR runnables — differ by a decade and by whether uninsured deposits and government-MMF shares are netted against the repo they fund.

Concrete overlaps you would hit immediately if you tried to add:
- **Runnables ⊃ M2 in part, not in whole.** Uninsured deposits ($7,608bn) and retail MMFs are inside M2; institutional and government MMFs and repo are not. "Runnables plus M2" double-counts roughly $10trn.
- **FSB EF1 ($58.1trn of fund assets) is the asset side of claims whose liability side is partly the runnables total.** The same MMF appears as $7,746bn of runnable liability and as part of $58.1trn of EF1 assets.
- **Repo appears three times** across the map: as $5,887bn of FSR runnable liability, as ~2.3% of a Divisia index, and as the object of the Gabor-Vestergaard definition — and the repo channel researcher's $12.5trn OFR gross measure, $3,040.7bn Z.1 GAAP-netted measure and EUR 13,651.1bn ICMA measure are three further incompatible readings of the same trades.
- **FABS sit inside the FSR "other" residual, inside Z.1 L.127/S125s1.3.s line 13, and inside NAIC Exhibit 7** — three balance sheets, one instrument.
- **Xiao's footnote 2 is the general theorem**: shadow-bank short-term liabilities are largely held *by other shadow banks*, so summing them counts the same outside dollar once per rung of the chain.

---

## PART 3 — THE JUDGEMENT

**A single shadow-money aggregate is not coherent, and the reason is structural, not a data gap that better collection would close.**

Three independent arguments.

**(1) Money is a property of a claim relative to a holder, and the holder sectors do not nest.** Every official aggregate defines a money-*holding* sector and counts claims held by it: M2 excludes depositories and the federal government; euro-area M3 excludes MFIs and central government; BoJ L excludes financial institutions entirely. Pozsar's whole point is that "for institutional cash pools, money begins where M2 ends" — the pools are *outside* every official holder sector. So the moment you add a wholesale instrument (repo, institutional MMF, FABS) to a retail-holder aggregate, you have added claims held by an excluded sector to claims held by an included one. The sum has no holder. It is not a stock of anything's money.

**(2) The chain double-counts by construction and there is no look-through to net it.** A T-bill funds a repo; the repo funds a dealer inventory; the CNAV fund shares issued against that repo are held by a cash pool; the cash pool is a corporate treasury. Pozsar's $5trn is *net* of intermediary cross-holdings and is therefore roughly a quarter of the gross figures then in circulation — he says so explicitly. Xiao excludes repo and ABCP from money on exactly these grounds. Michell's result is that bank and shadow-bank creation are symbiotic, not additive. Gabor & Vestergaard's own LCH table shows EUR 246bn of repos receivable against EUR 246bn payable. **Every serious author who has looked at this has concluded that the gross sum is meaningless and the net sum requires look-through that no dataset provides** — and the nine channel notes in front of you independently document the absence of look-through in Form PF, AIFMD, SFT-2, and the ASC 860-30-50 footnote.

**(3) The measurement bases are not convertible, and the conversion factors are unpublished.** GAAP-netted vs gross vs one-sided vs both-legs vs notional vs fair value vs index. The repo researcher lists six bases for repo alone, none convertible into another "without adjustments nobody publishes." The insurance researcher lists three valuation regimes for offshore cession. That is not a defect of any one dataset; it is what happens when twelve collection regimes were built for twelve different supervisory purposes.

**Therefore the honest output is a dashboard, and the dashboard is more useful than a total would be.** A single number would answer a question nobody can act on. A dashboard of separately-based channel measures, each with its own base and vintage, answers the question the operator actually has: *which channel is doing the work right now, and is the price of that channel's constraint tightening or loosening?*

I would build it as **four panels plus a price row**, and I would refuse to draw a total line:

**Panel A — the maintained near-money stock (liability side, outside investors).**
Fed FSR Table 4.1 runnables: $27,033bn, +12.0% y/y vs +5.4% trend, 86% of GDP, 2025:Q4. Semiannual, free, one page, official. This is the closest thing to Pozsar's aggregate that anyone maintains. Track the *growth gap to trend* and the *"other" residual* ($3,223bn, my arithmetic) — the residual is where FABS and stablecoins live and it is where new instruments will first appear.

**Panel B — the credit-intermediation stock (asset side).**
FSB narrow measure $76.3trn / EF1–EF5, annual each December, free, and the explicit statement that private credit is outside it. Read this **against** Panel A, never added to it: A is liabilities to outside holders, B is assets of intermediaries.

**Panel C — the Japan diagnostic, because it is his own precedent.**
BoJ L vs M3, monthly, free, complete component detail. L−M3 = ¥697.2trn and growing at 3.1× M3. It is the only official aggregate in the world that will show him the phenomenon he remembers — and its two exclusions (financial-sector holders; repo since 2008) tell him precisely how much of today's version it would still miss.

**Panel D — the channel-by-channel money-creation sleeve, on bank balance sheets only.**
The one thing across all nine channel notes that is unambiguously money creation on Tobin/BoE mechanics and unambiguously additive *within itself* because it is one balance sheet: **drawn bank credit to non-bank financial intermediaries**. H.8 line 26 ($2,005.0bn, July 2026); Call Report RC-C M.10.a–e; Z.1 broker-dealer borrowing from depositories (FL663168005, $541.8bn at 2025:Q4, +53.5% y/y); Z.1 depository loans to finance companies (FL613168005, $289.8bn at 2026:Q1). Everything else in the nine notes — LP capital, annuity premia, rated notes, SRT, repo reuse, FX swap notionals, trade credit — is intermediation, capital relief, collateral reuse, or money economisation, and belongs in a *separate* column labelled as such.

**Price row — the KVJ dual.** Convenience yields and spreads: AAA–Treasury, CP–bill, cross-currency basis, GC repo vs IORB, the FABN new-issue spread. Free or near-free, daily, and *not* subject to any of the double-counting problems above, because a price is not a quantity. If the quantity story is real and the constraint is slack, these compress; if a channel is jamming, they blow out. This is the only part of the dashboard that will warn him in real time.

**One thing the dashboard should say in a box.** His premise — savings flat, other assets not sold, capex funded — is answered by the nine channel notes in a way that is *not* primarily monetary: the largest single candidate any of the researchers surfaced is inter-firm trade credit, running at $895.5bn SAAR for non-financial corporates at 2026:Q1 (Z.1 F81.t), which creates a claim without creating a deposit and shows up as velocity, not money. The second is bank capital relief via SRT (~€800bn protected, ~43bp of CET1, and Osberghaus–Schepens' finding that banks hold the capital ratio constant and grow assets), which creates ordinary bank money whose *cause* is erased from the statistics. Neither is shadow money. Both are invisible to M1–M3 for the reason he suspects — but the reason is that monetary aggregates measure a restricted holder sector's claims on banks, not that a new money instrument is hiding.

---

**Sources:** [OFR WP 14-04 (Pozsar)](https://www.financialresearch.gov/working-papers/files/OFRwp2014-04_Pozsar_ShadowBankingTheMoneyView.pdf) · [Fed FSR May 2026](https://www.federalreserve.gov/publications/files/financial-stability-report-20260508.pdf) · [Bao/David/Han, The Runnables](https://www.federalreserve.gov/econresdata/notes/feds-notes/2015/the-runnables-20150903.html) · [FSB GMR 2025 (P161225)](https://www.fsb.org/uploads/P161225.pdf) · [Gorton/Lewellen/Metrick NBER 17777](https://www.nber.org/system/files/working_papers/w17777/w17777.pdf) · [Krishnamurthy/Vissing-Jorgensen NBER 12881](https://www.nber.org/system/files/working_papers/w12881/w12881.pdf) · [Gabor & Vestergaard, INET](https://www.ineteconomics.org/uploads/papers/Towards_Theory_Shadow_Money_GV_INET.pdf) · [Xiao, Monetary Transmission through Shadow Banks](https://red-files-public.s3.amazonaws.com/meetpapers/2018/paper_616.pdf) · [BoJ Guide to Money Stock Statistics](https://www.boj.or.jp/en/statistics/outline/exp/data/exms01.pdf) · [BoJ Money Stock, July 2026](https://www.boj.or.jp/en/statistics/money/ms/ms2607.pdf) · [ECB monetary aggregates](https://www.ecb.europa.eu/stats/money_credit_banking/monetary_aggregates/html/index.en.html) · [Fed H.6 current release](https://www.federalreserve.gov/releases/h6/current/default.htm) · [Fed M3 discontinuance](https://www.federalreserve.gov/releases/h6/discm3.htm) · [CFS Divisia](https://centerforfinancialstability.org/amfm_data.php), [June 2026 release](https://centerforfinancialstability.org/amfm/Divisia_Jun26.pdf)

---

## Critiques and measurement traps

# THE CRITIQUES AND THE MEASUREMENT TRAPS

**Adversarial pass. All figures retrieved and computed 21 August 2026. Every number below is either (a) read from a primary file I downloaded in this session, or (b) computed by me from such files, with the arithmetic shown. Nothing is recalled from memory. Where I could not verify, I say so.**

---

## 0. THE FIVE FINDINGS, STATED FIRST

1. **The FSB narrow measure is not a shadow-banking measure and the FSB says so.** It is built "on a conservative and inclusive basis… on a pre-mitigant basis. **Consequently, the narrow measure may overestimate the degree to which NBFI gives rise to financial stability risks**" (GMR 2025, Introduction). 76.1% of it is EF1, whose typical entities are MMFs and fixed-income funds. Entities individually subject to Basel-equivalent regulation are explicitly **not** excluded (fn 75). $11.1trn is excluded for bank consolidation; $164.5trn of NBFI is excluded from the narrow measure entirely.

2. **The double-counting rule is: measure credit on the obligor's liability side, money on the holder's asset side, and never sum the two.** Everything else in your nine-channel map — CLO collateral, fund AUM, BDC assets, insurer Schedule D, bank NDFI loans, SRT reference pools, repo collateral, footnote collateral — is a *holder-side or wrapper-side* re-observation of a claim already counted once, or an intra-financial claim that nets to zero against the real economy. I trace one loan through eleven statistical systems below.

3. **The valuation trap is severe and I have quantified it.** Of the $84,260.7bn increase in total financial assets of US domestic financial sectors from 2009:Q4 to 2026:Q1, **$30,090.3bn — 35.7% — is not transactions at all**. For US mutual funds the figure is **99.6%**. The FSB's own 2024 numbers: equity funds grew 22.4% with **">85% of the increase in AUM"** attributable to valuation. FSB growth rates are FX-adjusted and explicitly **"have not been otherwise adjusted (e.g. for the appreciation or depreciation of asset prices)."**

4. **The H.6 change of 28 July 2026 did not move M2. It moved the components, by up to 670%.** I diffed ALFRED vintages: M2SL at 2026-05 went 23,052.3 → 23,055.6 (+0.01%, seasonal noise). Small time deposits went 1,026.1 → 1,507.4 (**+$481.3bn, +46.9%**), retail MMF 2,275.3 → 3,027.0 (**+$751.7bn, +33.0%**), restated back to 1962 and 1974 respectively. **The implied IRA/Keogh netting item is ≈$1,233.0bn at May 2026** and is not yet published as a standalone FRED series — you must derive it exactly as I just did.

5. **The ZIRP premise fails in the US and holds in Japan, and neither supports the current thesis.** US 2009-12→2019-12: M2 +6.08%/yr against nominal GDP +4.12%/yr. Money grew *faster* than income; the aggregates moved. Japan 2012-12→2017-01: BOJ assets +31.36%/yr, M2 +3.71%/yr, Nikkei +15.99%/yr — that *is* your pattern, and it is a price/portfolio-rebalancing story, not a hidden-money story. **The window where your puzzle actually lives is 2021:Q4→2026, where M2 grew 1.66%/yr against nominal GDP 6.16%/yr.** And the answer there is not monetary: **US nonfinancial corporate gross saving is $3,979bn SAAR at 2026:Q1 against total capex of $3,200bn — a financing gap of −$635bn.** The corporate sector is funding its own capex out of retained earnings and lending the surplus to everyone else.

---

## 1. THE STRONGEST PUBLISHED CRITIQUES

### 1.1 "The FSB narrow measure over-counts by including regulated entities"

This critique is correct, and the FSB concedes most of it in its own text. Source: **FSB, *Global Monitoring Report on Non-Bank Financial Intermediation 2025*, P161225, 16 December 2025** (https://www.fsb.org/uploads/P161225.pdf — I downloaded and text-extracted this).

Composition of the narrow measure, end-2024 (Table 0-1, as extracted):

| EF | Typical entities | Size (USD trn) | Share | 2024 growth |
|---|---|---|---|---|
| EF1 collective investment vehicles with run features | MMFs, fixed income funds, mixed funds, credit hedge funds, mREITs | 58.1 | 76.1% | 15.1% |
| EF2 lending dependent on short-term funding | finance, leasing, factoring, consumer credit cos | 6.1 | 8.0% | 5.5% |
| EF3 market intermediation dependent on short-term funding | broker-dealers, custodial accounts, securities finance cos | 4.9 | 6.4% | 5.8% |
| EF4 facilitation of credit intermediation | credit insurers, financial guarantors, monolines | 0.1 | 0.2% | 2.5% |
| EF5 securitisation-based credit intermediation | SFVs, ABS | 5.3 | 7.0% | **4.3%** |
| Unallocated | other financial auxiliaries | 1.7 | 2.3% | 4.5% |
| **Total** | | **76.3** | **100%** | **12.7%** |

Three specific over-count mechanisms, all documented in the report itself:

**(a) Regulated entities are in by design.** Footnote 75: *"Non-bank entities that are not prudentially consolidated into banking groups, but are individually subject to Basel-equivalent regulation, are not excluded from the narrow measure."* So a Basel-regulated standalone broker-dealer is in EF3. A 2a-7 or MMFR money market fund is in EF1. MMF assets alone were $12.1trn at end-2024 (+15.0%), i.e. **roughly a fifth of EF1 is the single most heavily prescribed fund vehicle in the world.**

**(b) The pre-mitigant convention.** *"this classification is done on a conservative and inclusive basis, reflecting the assumption that policy measures and/or risk management tools have not been exercised (i.e. on a pre-mitigant basis). Consequently, the narrow measure may overestimate…"* Redemption gates, swing pricing, leverage caps, LMTs — all assumed absent.

**(c) The perimeter is a jurisdictional artefact, which makes the level non-comparable and the growth rate partly a reporting variable.** $11.1trn of classified assets were excluded at end-2024 because they are prudentially consolidated into banking groups (including self-securitisation). **60.9% of total broker-dealer assets are bank-consolidated and therefore outside EF3 entirely** — so EF3's $4.9trn measures roughly 39% of the world's broker-dealer balance sheet, and which 39% depends on each country's group structure, not on economics. A further $1.8trn of national-accounts statistical residual (0.7% of NBFI) is excluded "given uncertainty about the actual entities/activities included."

**The symmetric under-count, which is the more damaging half.** $164.5trn of NBFI assets sit outside the narrow measure, including **captive financial institutions and money lenders $20.3trn** and **equity funds including equity ETFs $34.9trn**. And private credit is excluded *by construction*: *"Many private credit investment funds are closed-end and typically have low levels of leverage themselves… They also do not rely on short-term wholesale funding for their activity, which means that they are not classified into EF1 or EF2 (or any other economic function)."*

**Net verdict for your operator:** the narrow measure is a *run-risk* proxy, not a credit-creation measure, and it is over-inclusive on entity type and under-inclusive on the activity he actually cares about. **Anyone using $76.3trn as "the size of shadow banking" is quoting a number that simultaneously includes SEC-registered money funds and excludes the entire private credit industry.**

### 1.2 "Shadow money is a category error"

The pro-shadow-money position, stated at its strongest, is **Pozsar, "Shadow Banking: The Money View", OFR Working Paper 14-04, 2 July 2014** (verified, downloaded). Its core claim is a *hierarchy of moneyness* organised around one attribute: *"money always trades at par on demand."* Pozsar's argument is that "for cash pools, money begins where M2 ends," because institutional balances are too large for deposit insurance, so the relevant money is repo, Treasury bills, and MMF shares — instruments ranked by "the strength of these promises of par on demand and par at maturity, respectively, in all states of the world."

The category-error critique, applied against that framework, has three limbs and each survives:

**(i) Par-on-demand is not the same as means of payment.** A repo claim, an FABN, a BDC share, a rated note and an LP interest are all *stores of value with varying liquidity*. None of them settles a transaction. The correct genus is **near-money in the Gurley-Shaw sense**, and the correct measurement is *not* a monetary aggregate but a **liquidity-transformation ratio** — which the NAIC in fact computes for the FABN/FHLB book (3.4× the life industry's cash and cash equivalents; see your insurance channel). That ratio is the honest metric and it does not require calling anything money.

**(ii) The test that discriminates is elasticity, not liquidity.** BIS AER 2026 Chapter III applies exactly this to stablecoins: a cash-in-advance issuance model cannot expand supply to meet payment demand, therefore it is not money. Apply the same test across your map and it partitions cleanly: bank subscription/NAV/warehouse lines are elastic (loans create deposits, on demand, at the point of need); FABNs, rated notes, LP interests, annuities and fiat-backed stablecoins are inelastic (each requires a prior dollar).

**(iii) The empirical version of the error is that "shadow money" measures are gross positions, and money is a net concept.** M2 is a liability aggregate of one sector held by another. Repo outstanding of $12.5trn (OFR, H2 2025 daily average) is a gross bilateral position that nets to a far smaller quantum of purchasing power; $2.1trn of it is affiliate repo between entities of the same parent. **A gross figure cannot be a monetary aggregate.**

**Where the critique fails, and you should concede it:** it does not dispose of the *institutional MMF* case. Those shares are par-on-demand, same-day, held by money-holding sectors, and **excluded from M2 by definition** (only retail MMF is in M2). Derivable magnitude: Z.1 money market funds' total financial assets FL634090005 = **$8,289.6bn at 2026:Q1** against H.6 retail MMF (new basis) of $3,027.0bn at 2026-05, i.e. **≈$5.26trn of par-on-demand claims sitting outside M2**, up from ≈$2.71trn at 2019:Q4 (**+94% in 6.25 years, versus M2 +50.8%**). *Basis caveat: Z.1 is NSA end-quarter total assets, H.6 is SA monthly average of daily shares outstanding; for a clean build use the OFR Money Market Fund Monitor's retail/institutional split instead of my two-source subtraction.* This is the single most defensible "money outside the aggregates" number in your entire map, and it is intermediation, not creation.

### 1.3 "NBFI growth is reclassification and migration, not net creation"

Partly true, and quantifiable in three places.

**Migration, documented at source.** Adrian & Ashcraft, *Shadow Banking: A Review of the Literature*, FRBNY Staff Report 580, October 2012 (verified, downloaded), records the post-crisis migration *into* banks: *"the financial crisis led, perhaps paradoxically, to a migration of independent shadow banking activity into BHCs,"* citing Cetorelli (2012): BHCs controlled ~38% of the largest insurers' assets, 41% of MMF assets and 93% of the largest brokers and dealers as of 2011. The subsequent reversal is the enhanced-prudential-standards effect they predicted: *"Tighter capital and liquidity requirements will arguably lead to an increased incentive for some forms of credit intermediation to migrate out of BHCs."* **This is a relocation of a given quantum of intermediation across a regulatory boundary. It shows up as NBFI growth and bank-share decline with no change in credit to the real economy.** The FSB's own EF3 perimeter (60.9% bank-consolidated and excluded) means a single reorganisation that deconsolidates a broker-dealer would print as NBFI "growth."

**Reclassification, quantified in US bank data.** From your channel researchers, all traceable to FDIC *Banking Issues in Focus* No. 1 (Feb 2026) and H.8: **$193.2bn of C&I and $140.6bn of consumer loans were reclassified into NDFI-and-n.e.c. at domestically chartered banks through Sep-2025.** Call Report NDFI subcategories were best-efforts for Dec-2024 and Mar-2025 and comprehensive only from Jun-2025. The Fed FSR revised commitments to "PE, BDCs and private credit" **up by $261bn in Q4 2025** on a vendor-data reclassification out of three other buckets. **Any NDFI growth rate spanning 2024:Q3–2025:Q3 is contaminated, and the Fed's own private-credit commitment level is a classification artefact as much as a measurement.**

**And the H.8 has the fix built in, which almost nobody uses.** From the H.8 "About" page (verified): *"All percent changes have been adjusted to remove the effects of nonbank structure activity of $5 billion or more, as well as the effects of accounting rule changes, such as the initial consolidation of off-balance-sheet vehicles (FAS 166/167) and the adoption of the Current Expected Credit Loss (CECL) standard (ASU 2016-13)."* **The published percent changes are break-adjusted; the published levels are not.** If you difference H.8 levels to get a growth rate — which is what every chart in circulation does — you are counting structure activity as credit growth. Use the Fed's own percent-change series.

**Where the critique fails:** it does not explain EF1. MMF assets carry **zero revaluation** in the Z.1 (amortised cost, $1 NAV) — I verified this: money market funds' change in total financial assets from 2019:Q4 to 2026:Q1 is $4,287.1bn and the transaction total is identical to the penny, residual 0.0%. So the $3,084.1bn increase in US MMF assets since 2021:Q4 is neither price nor reclassification. It is a real reallocation of real balances. That is a genuine, measured, non-artefactual flow.

---

## 2. THE DOUBLE-COUNTING PROBLEM, CONCRETELY

### 2.1 One $100m unitranche loan, eleven statistical systems

| # | Where it appears | System / table / line | Basis |
|---|---|---|---|
| 1 | Borrower's obligation | Z.1 **S11.1.s** (ex-L.103) FL103169005 "other loans and advances; liability" — **or nowhere at all**, see §2.3 | principal, obligor side |
| 2 | Direct-lending fund's asset | SEC Form PF Q9/Q16; SEC Private Fund Statistics Tables 2.x | GAV, confidential |
| 3 | Bank subscription / NAV / portfolio facility to that fund | Call Report **RC-C Pt I M.10.b/10.c**; H.8 line 26; FR Y-14Q Sch H.1 | drawn balance + commitment |
| 4 | Deposit created by (3) | H.6 M2 | monetary liability |
| 5 | CLO collateral, if securitised | Z.1 **F4.6.s** FL673069803 (ABS issuers) or **S2.s** (ex-L.133) line 15 for offshore CLOs | principal, wrapper side |
| 6 | CLO note held by an insurer | NAIC Schedule D-1-1 / D-1-2; Z.1 **S1281.1.s** (ex-L.116.g) | BACV |
| 7 | Rated-note feeder held by the insurer | NAIC Schedule D or Schedule BA | BACV |
| 8 | Funding agreement backing an FABN | Z.1 **S125s1.3.s** (ex-L.127) line 13 FL673090543; Fed EFA FABS | principal |
| 9 | FABN held by an institutional MMF | SEC N-MFP3; OFR MMF Monitor — **and not in M2** | amortised cost |
| 10 | The bank's synthetic hedge on the same exposure | COREP **C 14.00** (confidential); the loan simultaneously stays in AnaCredit and in MFI loan aggregates | reference notional |
| 11 | The CLN repo'd back to a bank | OFR repo NCCBR; dealer 10-K **ASC 860-30-50** collateral footnote | cash value / fair value |

Nine of these eleven are legitimate measurements of *different* balance sheets. Summing them yields roughly 8–10× the loan. **The FSB does the same thing internally and states its own rule (fn 72): where an entity is classified into more than one economic function, "an entity's assets are proportionately allocated between the economic functions… so as to only count once."** No such discipline exists across the vendor and regulatory sources your channel researchers used.

### 2.2 The rule

**Build two aggregates. Only two. Each on one side of one balance sheet. Never sum them.**

**(A) CREDIT — measure at the ultimate obligor's liability side.**
One obligation counts once regardless of how many times the claim is repackaged, tranched, insured, hedged or repo'd. For the US this is **Z.1 table D3.s** (renamed from D.3 in June 2026), *Debt outstanding by sector*. For the world, BIS total credit to the non-financial sector.

Verified levels, US$bn, Z.1 vintage 11 June 2026:

| | 2009:Q4 | 2019:Q4 | 2021:Q4 | 2026:Q1 |
|---|---|---|---|---|
| Domestic nonfinancial sectors (LA384104005) | 36,547 | 55,251 | 66,532 | 81,855 |
| — Nonfinancial corporate (LA104104005) | 6,478 | 10,886 | 12,696 | **14,454** |
| — Households & NPO (LA154104005) | 14,003 | 16,081 | 18,204 | 21,069 |
| — Federal government (LA314104005) | 8,883 | 19,040 | 25,304 | 34,473 |
| Domestic **financial** sectors (LA794104005) | 18,471 | 18,684 | 22,401 | 26,108 |

NFC debt/GDP: **44.2% (2009:Q4), 49.6% (2019:Q4), 51.2% (2021:Q4), 45.4% (2026:Q1)**. Corporate leverage relative to income has *fallen 5.8pp since end-2021*.

**(B) MONEY / NEAR-MONEY — measure at the holder's asset side**, restricted to claims that are (i) fixed in nominal value, (ii) redeemable at or near par on demand or at very short notice, (iii) held by a money-holding sector (non-bank, non-central-government resident). M2 + institutional MMF shares + non-bank repo lending + stablecoins.

**The three screening questions for any candidate addend:**

1. **Is the counterparty a financial institution?** If yes it is intra-financial and belongs in neither (A) nor (B). Bank NDFI lending, warehouse lines, subscription lines, NAV loans, prime brokerage, SRT protection and repo are *all* intra-financial. They are diagnostic of *how* credit is funded and of *where money is created*, not additions to credit outstanding. **The domestic financial sectors' own debt (LA794104005, $26,108bn) is the correct home for all of it, and it is a separate line from nonfinancial debt precisely so you do not add them.**
2. **Is it a limit or a balance?** Utilisation on bank facilities to private credit vehicles has run 50–65% (OFR, Y-14); 42.9% of total NDFI commitments were undrawn at 2025:Q3. Quoting a committed figure beside a drawn figure is a factor-of-two error.
3. **What is the measurement basis — notional, AUM, market value, or principal balance?** Only principal balances of actual obligations are addable, and only within one basis. $113.5tn of USD-leg FX forwards and swaps is a gross settlement exposure; $2.2trn of private credit AUM includes dry powder; $69.5trn of NFC corporate equity liability is a price times a share count.

**The only additions I would defend in the entire nine-channel map:**
- Form PF fund borrowings + BDC borrowings (statutorily disjoint universes; OFR makes this addition explicitly).
- Within a single Z.1 instrument table at a single date, holder lines sum to the instrument total by construction — e.g. **F4.6.s lines 46–51 (households residual $131.0bn + life GA $36.8bn + mutual funds $103.4bn + ABS issuers $358.1bn + brokers $58.7bn + other financial business $10.2bn) sum to exactly FL103169803 $698.2bn, the NFC syndicated-loan liability, at 2026:Q1.** Even here the trade credit table fails to reconcile by −$889.3bn.

**The instrument to use if you want to do this properly:** Z.1 tables **M3.s / M3.t**, the financial accounts matrix (from-whom-to-whom). Note the vintage hazard: the Fed announced on 12 June 2026 that *"Due to a technical error, the Z.1 PDF that was originally posted at noon on June 11, 2026, contained incorrect data on table M3.s."*

### 2.3 The finding that breaks the rule, and you must state it

**Z.1's obligor side does not contain private credit, and I can show you the empty box.**

Table **F4.6.s** (*Other loans and advances*, ex-L.216) at 2026:Q1 enumerates every holder of every non-mortgage, non-depository loan to US nonfinancial corporates. The complete holder list for syndicated loans is the six lines above, totalling $698.2bn. Finance-company loans to NFCs add $635.0bn (FL103169535). US government loans $259.5bn. **There is no line — none — for loans held by private credit funds, business development companies, private debt funds or credit interval funds.** The Fed's own FSR sizes US private credit at ~$1.4trn from Preqin, LSEG and PitchBook, and then uses Z.1 for the denominator. **The numerator is therefore not inside the denominator.** Every "private credit is X% of nonfinancial corporate debt" ratio in circulation, including the Fed's own, is built that way.

Two candidate hiding places, both derivable and both worth your operator's attention:
- **F4.6.s line 66, FL263069500, "Rest of the world; U.S. nonfinancial business loans; asset": $830.8bn (2019:Q4) → $1,192.4bn (2026:Q1), +43.5%.** Cayman-domiciled CLOs and offshore lending vehicles land here. This is the single largest unexplained non-bank corporate loan line in the US accounts.
- **S11.1.s line 44, FL103193005, "Nonfinancial corporate business; unidentified miscellaneous liabilities": $9,422.8bn (2019:Q4) → $12,101.9bn (2026:Q1).** A $12.1trn residual on the obligor side — *larger than the entire $14.45trn measured debt stock*. Any borrowing the Fed cannot identify either sits here or is missing. **This is the honest limit of my own rule in §2.2 and it must be stated whenever the rule is used.**

**Correction to your private-credit and residual-channel researchers:** FL153069803 is not a general private-credit plug. Its Z.1 label is *"Households and nonprofit organizations; **syndicated** loans to nonfinancial corporate business; asset"* — the household-residual share of the *syndicated* loan market specifically. Its $131.0bn cannot be read as "where the Z.1 parks private credit."

---

## 3. THE VALUATION TRAP, QUANTIFIED

### 3.1 The derivation, exactly

Z.1 publishes levels (`FL`/`LM` prefixes) and transactions (`FA` seasonally adjusted annual rate, `FU` unadjusted quarterly) for the same series code. Therefore, for any window:

**Revaluation + other changes in volume = (Level_end − Level_start) − Σ(FU over the window)**

Reproduce: download `https://www.federalreserve.gov/releases/z1/current/z1_csv_files.zip` (8.08 MB, verified 200). Levels are in `csv/*_s.csv`, unadjusted transactions in `csv/*_t_tu.csv`, series-to-line mapping in `data_dictionary/`. Old-to-new table crosswalk: `https://www.federalreserve.gov/releases/z1/current/z1_table_mapping.csv`.

### 3.2 Results (my computation, Z.1 vintage 11 June 2026, US$bn)

| Sector | Window | Δ Level | Transactions | Residual | Residual % |
|---|---|---|---|---|---|
| **Domestic financial sectors, total fin. assets** (FL794090005) | 2009:Q4→2019:Q4 | 36,667.3 | 20,794.8 | 15,872.4 | **43.3%** |
| | 2019:Q4→2021:Q4 | 26,987.5 | 17,086.1 | 9,901.5 | **36.7%** |
| | 2021:Q4→2026:Q1 | 20,605.9 | 16,289.5 | 4,316.4 | **20.9%** |
| | 2009:Q4→2026:Q1 | 84,260.7 | 54,170.4 | 30,090.3 | **35.7%** |
| Mutual funds (LM654090000) | 2009:Q4→2026:Q1 | 15,229.4 | **68.1** | 15,161.3 | **99.6%** |
| Exchange-traded funds (LM564090005) | 2009:Q4→2026:Q1 | 12,775.1 | 8,165.0 | 4,610.2 | **36.1%** |
| Money market funds (FL634090005) | 2019:Q4→2026:Q1 | 4,287.1 | 4,287.1 | 0.0 | **0.0%** |
| Mortgage REITs (FL644090075) | 2009:Q4→2026:Q1 | 538.6 | 539.8 | −1.2 | **−0.2%** |
| Issuers of ABS (FL674090005) | 2021:Q4→2026:Q1 | 492.1 | 497.5 | −5.4 | **−1.1%** |
| Life insurance companies (FL544090005) | 2009:Q4→2026:Q1 | 5,665.8 | 3,352.9 | 2,312.9 | **40.8%** |
| Households & NPO, corporate equities (LM153064105) | 2009:Q4→2026:Q1 | 37,510.7 | 4,947.3 | 32,563.4 | **86.8%** |

For households, Z.1 publishes the split directly — table **S1M.r** (ex-R.101), series FC/FU/FR/FV — so you do not need the residual method:

| Window | Δ net worth | Transactions | **Revaluation (FR)** | Other vol. chg (FV) | Reval % |
|---|---|---|---|---|---|
| 2009:Q4→2019:Q4 | 54,173.3 | 14,370.6 | **36,118.8** | +3,683.8 | 66.7% |
| 2019:Q4→2021:Q4 | 35,926.9 | 6,009.7 | **30,158.8** | −241.7 | 83.9% |
| 2021:Q4→2026:Q1 | 31,382.0 | 9,289.1 | **22,597.9** | −505.0 | 72.0% |

### 3.3 What this does and does not do to the thesis

**It kills the wide measure and mostly spares the narrow one.** The instruments whose growth is price are exactly the ones with the *least* claim to be shadow money: mutual funds (99.6% price), household equity holdings (86.8% price), life insurers' book (40.8% price). The instruments that matter monetarily are measured at amortised cost or book and carry **zero** revaluation: MMFs 0.0%, mREITs −0.2%, ABS issuers −1.1%, brokers −1.4% since 2021:Q4. **A price-inflated measure of shadow banking and a credit-creation measure of shadow banking are close to disjoint sets.**

**The FSB confirms the same partition on its own data.** GMR 2025: equity funds grew 22.4% in 2024 with valuation *"accounting for over 85% of the increase in assets under management"*; fixed income funds grew 13.0% *"primarily driven by investor inflows, which accounted for over 85% of the increase."* Graph 1-4 publishes the flow/valuation split by fund type and jurisdiction — **that graph is the single most useful free artefact for this question and nobody cites it.** Critically, **equity funds including equity ETFs ($34.9trn) are already excluded from the narrow measure**, so the valuation critique bites the wide NBFI measure ($256.8trn, +9.4% in 2024) far harder than the narrow one.

**Methodological warning on FSB growth rates:** *"Some exchange rate effects have been corrected when presenting growth rates by applying a constant end-2024 exchange rate across all past years… Growth rates have not been otherwise adjusted (e.g. for the appreciation or depreciation of asset prices)."* Two consequences: (a) no valuation adjustment at all; (b) **the FX rebasing is done afresh each year, so every historical growth rate in the 2025 report differs from the same historical growth rate in the 2024 report.** That is a silent annual restatement of history.

**And the limit of my own method, which must be stated whenever it is used:** the residual is revaluation **plus other changes in volume**, and *other changes in volume is exactly where reclassifications land*. For households the published FV was **+$3,683.8bn over 2009-2019 — 6.8% of the total change** — and −$505.0bn since 2021:Q4. **Sections 3 and 4 of this brief are not independent problems. They are the same residual.** Only three Z.1 tables (S11.1.r, S11.2.r, S1M.r) publish FR and FV separately; for every financial sector you get one lump.

---

## 4. THE RECLASSIFICATION / BREAK REGISTER

### 4.1 H.6, 28 July 2026 — verified and quantified

The release states: *"starting with today's H.6 publication, the Federal Reserve has discontinued the netting of individual retirement account and Keogh account balances held at depository institutions and at money market funds from the small-denomination time deposit and retail money market fund components"*; they become *"a separate component of the M2 monetary aggregate that is netted directly from the aggregate,"* applied backward across the whole history.

I tested this against ALFRED vintages (`https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=<ID>&vintage_date=<YYYY-MM-DD>`), vintage 2026-07-01 vs 2026-08-15:

| Series | Date | Old vintage | New vintage | Change |
|---|---|---|---|---|
| **M2SL** | 2026-05 | 23,052.3 | 23,055.6 | **+3.3 (+0.01%)** |
| M2SL | 2009-12 | 8,512.2 | 8,510.6 | −1.6 (−0.02%) |
| **STDSL** small time deposits | 2026-05 | 1,026.1 | 1,507.4 | **+481.3 (+46.9%)** |
| STDSL | 2021-12 | 90.6 | 697.3 | **+606.7 (+669.6%)** |
| STDSL | 2000-01 | 963.2 | 1,205.1 | +241.9 (+25.1%) |
| **RMFSL** retail MMF | 2026-05 | 2,275.3 | 3,027.0 | **+751.7 (+33.0%)** |
| RMFSL | 2019-12 | 993.9 | 1,294.0 | +300.1 (+30.2%) |
| WRMFSL (discontinued Feb 2021) | 2021-02 | 1,053.7 | 1,429.1 | +375.4 (+35.6%) |

**Practical rules that follow.**
- **M2 itself is unaffected.** The 560 revised observations in M2SL are ordinary seasonal-factor revisions, all under 0.03%. Anyone who tells you M2 was restated in July 2026 is wrong.
- **Any pre-July-2026 series for small time deposits or retail MMF is unusable**, restated back to 1962-03 (STDSL) and 1974-02 (RMFSL). At 2021:Q4 the small-time-deposit series is wrong by a factor of 7.7×.
- **Even discontinued series were rewritten.** WRMFSL ended in Feb 2021 and was still restated. Do not assume a dead series is a frozen series.
- **The new IRA/Keogh component has no FRED identifier yet** — I probed IRAKSL, IRAKEOGH, M2IRAK, IRASL, WIRAK; all 404. **Derive it as I did: (STDSL_new − STDSL_old) + (RMFSL_new − RMFSL_old) = $481.3bn + $751.7bn ≈ $1,233.0bn at May 2026**, or take it from the H.6 table directly once you have the release.

### 4.2 Other breaks of the same kind in the series this project uses

**Verified in this session:**

1. **H.6, May 2020 — Regulation D savings-deposit reclassification.** M1SL: 2020-04 = 4,856.4 → 2020-05 = **16,312.5**, a jump of **+$11,456.1bn (+235.9%) in one month**, entirely definitional. SAVINGSL and OCDSL both terminate at 2020-04 on FRED. **Any M1 series spanning April/May 2020 is meaningless.** M2 was unaffected.
2. **H.6, February 2021 — M1/M2 restructuring and weekly-series discontinuation.** Evidenced by WRMFSL terminating at 2021-02. (I did not retrieve the release wording this session; verify before quoting.)
3. **Z.1, 11 June 2026 — full SNA renumbering.** Crosswalk verified live at `.../z1/current/z1_table_mapping.csv`. Confirmed mappings: S11.1.s←L.103, S11.1.r←R.103, S122.1.s←L.111, S123.s←L.121, S124.1.s←L.122, S124.3.s←L.124, S124.4.s←L.129, S125s1.3.s←L.127, S125s2.1.s←L.128, S127.1.s←L.131, S127.2.s←L.132, S1281.s←L.116, **S2.s←L.133**, D3.s←D.3. **Series mnemonics (FL/FA/FU/LM codes) are unchanged; only table numbers moved.** So a pipeline keyed on mnemonics survives; a pipeline keyed on table numbers is dead.
4. **Z.1, 12 June 2026 — one-day bad vintage.** The 11 June noon PDF carried incorrect data on table M3.s and was reposted. If you cached the matrix table that day, recache.
5. **H.8 — break adjustment is in the percent changes, not the levels** (verbatim quote in §1.3). Seasonal factors updated once a year; the "largest 25 domestically chartered" panel is re-ranked at each Call Report benchmark; small-bank figures are derived as residuals and *"may occasionally result in negative seasonally adjusted levels."*
6. **FSB GMR — constant end-2024 FX applied retroactively to all past years.** History is silently rebased annually.
7. **FSB GMR internal inconsistency, unresolved.** The Table 0-1 composition table I extracted gives EF5 2024 growth of **4.3%**. Your residual-channel researcher reports Graph 1-6 giving **6.6%** and recommends citing the table. I read the table and it says 4.3%. **Two of the report's own exhibits disagree; state which one you took and do not average.**

**Carried from your channel researchers, not independently verified by me — flag as such:**
8. Call Report NDFI subcategories best-efforts Dec-2024/Mar-2025, comprehensive from Jun-2025; $193.2bn C&I + $140.6bn consumer reclassified into NDFI through Sep-2025.
9. Fed FSR: +$261bn reclassification into "PE, BDCs and private credit" in Q4 2025, plus a prior revision in April 2025.
10. BIS OTC derivatives: triennial coverage break; USD-leg forwards and swaps +15.9% at 2025-S1, of which an unpublished share is the 30-plus additional jurisdictions and 1,000-plus dealers entering the interpolation. There is **no reporting-jurisdiction dimension** in the FX outstandings, so a consistent-coverage series cannot be built.
11. BIS LBS: use the break-and-FX-adjusted flow series, never level differences.
12. SIFMA discontinued US ABS outstanding after 2021 ($1,585.3bn); EBA discontinued the EU-wide Transparency Exercise from June 2025.
13. Form PF: compliance date deferred three times to 1 Oct 2026; April 2026 SEC/CFTC re-proposal; region/country tables withdrawn from 2024:Q2 under Release IA-6279.
14. G.19 and Z.1 finance companies benchmark to the quinquennial FR 3033s survey and interpolate between; the 2021 US EF2 jump in the FSB data is a re-benchmarking artefact.
15. FINRA margin debt overwrites one file at one URL with no vintage archive; the Jun→Jul 2026 fall of $84,847mn cannot be classified as deleveraging or restatement.
16. DeFi Llama restates history silently with no revision log.

---

## 5. THE ZIRP EVIDENCE

All rates below are compound annual, computed by me from FRED CSVs pulled 21 August 2026.

### 5.1 United States

| | 2009-12 → 2019-12 | 2019-12 → 2021-12 | 2021-12 → 2026-06 |
|---|---|---|---|
| M2 (M2SL) | **+6.08%** | +18.35% | **+1.66%** |
| M1 (M1SL) | +9.03% | +125.40% *(definition break)* | −0.65% |
| Monetary base (BOGMBASE) | +5.39% | +36.81% | −3.40% |
| Nominal GDP | **+4.12%** | +6.36% | **+6.16%** |
| Bank credit (TOTBKCR) | +4.69% | +9.04% | +3.99% |
| Bank loans & leases (TOTLL) | +4.55% | +3.58% | **+5.80%** |
| C&I loans (BUSLOANS) | +6.42% | +2.44% | +3.55% |
| Nasdaq composite | +14.74% | +32.05% | +12.15% |
| Case-Shiller national | +3.76% | +14.56% | +4.20% |

M2 / monetary base: **8.94** (Dec 2007) → **4.20** (Dec 2009) → **2.98** (Dec 2014) → **4.48** (Dec 2019) → **3.35** (Dec 2021) → **4.22** (Jun 2026).

### 5.2 Japan

| | Dec 1998 → Mar 2006 | Mar 2006 → Dec 2012 | Dec 2012 → Jan 2017 |
|---|---|---|---|
| M2 (MYAGM2JPM189S) | +2.15% | +2.33% | +3.71% |
| BOJ total assets (JPNASSETS) | +6.58% | +1.33% | **+31.36%** |
| Nikkei 225 | +2.92% | −7.08% | **+15.99%** |

### 5.3 Verdict, in three parts

**(a) The premise is false for the US in 2009-2019.** M2 grew at 6.08%/yr against nominal GDP at 4.12%/yr — two full points of excess money growth per year, every year, for a decade. M2/GDP rose from roughly 58% to 70%. **Money did move.** What did not move was velocity (M2V fell throughout) and the multiplier (8.94 → 2.98). The correct characterisation of that decade is *money grew faster than income and slower than asset prices*, which is a portfolio-preference story about term premia and risk premia, not a hidden-aggregate story.

**(b) The premise is true for Japan 2013-2016, and that is the operator's actual memory.** BOJ assets +31.36%/yr, M2 +3.71%/yr, Nikkei +15.99%/yr. Base money exploded, broad money barely moved, asset prices went up 16% a year. The transmission was portfolio rebalancing and the yen-funded carry trade — a *price* effect on discount rates plus an *offshore currency* effect. **Note that the offshore leg of that mechanism is the one channel in your map that unambiguously creates money and is in no aggregate anywhere: BIS LBS cross-border USD claims of banks located outside the US, growing +$1.90tn break-adjusted in the four quarters to 2026:Q1, +11.9% y/y.** If your operator wants the ZIRP analogue in current data, it is the eurodollar leg, not private credit and not stablecoins.

**(c) 2020-21 is the opposite of a hidden channel.** M2 +18.35%/yr, fully visible, fully inside the aggregate, driven by fiscal transfers monetised through banks. Nothing about that episode supports an invisible-money thesis.

### 5.4 The window that actually matters — and the answer

Since 2021:Q4: **M2 +1.66%/yr against nominal GDP +6.16%/yr.** Money is shrinking sharply relative to income while the Nasdaq compounds at 12.15%/yr and a capex boom proceeds. That is the operator's real question, and there are three answers in the data, in descending order of size:

**(1) The aggregate saving *rate* is not up, but the saving *composition* has shifted violently — and that is the whole answer.**

| | 2019:Q4 | 2026:Q1 |
|---|---|---|
| US gross saving, % of GDP (GSAVE/GDP) | 18.8% | **17.2%** |
| Personal saving rate (PSAVERT, monthly) | 6.2% (Dec 2019) | **2.7% (Jun 2026)** |
| NFC gross saving, SAAR $bn (Z.1 FA106000105) | 2,366 | **3,979 (+68%)** |
| NFC total capex, SAAR $bn (FA105050005) | 2,152 | 3,200 (+49%) |
| **NFC financing gap** (FA105005305) | **−86** | **−635** |
| NFC net lending (FA105000005) | +261 | **+970** |

**The US nonfinancial corporate sector's internal funds exceed its total capital expenditure by $635bn at an annual rate, and it is a net lender of $970bn SAAR.** There is no aggregate external funding gap to explain. The household saving rate collapsed from 6.2% to 2.7%; corporate gross saving rose 68%. Aggregate saving looks flat because one sector's saving replaced another's. **No monetary innovation is required to fund a capex boom that the capex-doers are funding themselves.** Historical context so this is not over-read: the financing gap was −21 (2013:Q4), −86 (2019:Q4), +94 (2021:Q4), −3 (2023:Q4), +6 (2024:Q4), −250 (2025:Q2), −164 (2025:Q4), −635 (2026:Q1) — quarterly SAAR is noisy, but the trend is *more* self-funded, not less.

**(2) The money that exists is being reallocated out of M2 into instruments outside it.** MMF total assets +$3,084.1bn since 2021:Q4, with **0.0% revaluation** — pure flow. Institutional MMF outside M2 has roughly doubled to ≈$5.26trn. This depresses M2 growth without destroying purchasing power, and it recycles into repo and bills. **A falling M2/GDP ratio in this configuration is a measurement artefact of the aggregate's perimeter, not monetary tightening.**

**(3) There is genuine, bounded, measurable bank money creation in the intra-financial leg — and it is small relative to the boom.** Domestic financial sectors' own debt securities and loans: $22,401bn (2021:Q4) → $26,108bn (2026:Q1), +$3,707bn. Within that, the deposit-creating rungs your researchers identified — drawn bank facilities to private credit vehicles ($54–264bn depending on perimeter), broker-dealer borrowing from banks ($541.8bn), warehouse lines to finance companies ($289.8bn) — are real and fast-growing. They are also, in total, a fraction of one year's nonfinancial corporate gross saving.

**The residual honest statement:** the AI/data-centre capex specifically is concentrated in a small number of firms and financed partly at SPV, JV and offshore level, where the US nonfinancial corporate sector table does not see it. Candidate hiding places, all derivable: FL263069500 (ROW loans to US nonfinancial business, $1,192.4bn, +43.5% since 2019:Q4); FL103193005 (NFC unidentified miscellaneous liabilities, $12,101.9bn); and the eurodollar stock in the BIS LBS. **Those three lines are where I would spend the next research budget, and none of them is private credit, securitisation or stablecoins.**

---

## 6. WHAT I DID NOT VERIFY, AND WHAT I REFUSE TO PRODUCE

**Not verified this session (do not present as established):**
- IMF WP/14/25 (Claessens & Ratnovski) — imf.org returned 403 to both WebFetch and curl. The activity-vs-entity critique is real and widely cited; I could not open the document, so I have not quoted it.
- H.6 February 2021 restructuring wording — inferred from series termination dates only.
- FINRA margin-debt series break history and the NYSE→FINRA transition.
- G.19 benchmark revision magnitudes.
- The FSB EF5 discrepancy (4.3% in Table 0-1 vs 6.6% reported from Graph 1-6): I read the composition table only. Unresolved.
- My web-search budget for this session was exhausted, so §1's literature coverage rests on the two documents I could download (FRBNY SR 580; OFR WP 14-04) plus the FSB report. Named-but-unfetched works that belong in a fuller critique set: Claessens & Ratnovski (IMF WP/14/25), Gabor & Vestergaard on shadow money, Michell contra, Moreira & Savov, Sunderam, Ricks, IMF GFSR Oct 2014 Ch 2.

**What I will not produce:**
- A single "total shadow money" or "total shadow debt" number. The measurement bases do not permit it, and §2.1 shows why any such number is 8–10× an honest one.
- A grossed-up estimate of the IRA/Keogh component for dates other than those I diffed. Diff the vintages yourself for each date you need.
- Any decomposition of the Z.1 residual into "price" versus "reclassification" for sectors where the Fed does not publish FR and FV separately. Only S11.1.r, S11.2.r and S1M.r do.
- Any statement that the private credit / securitisation / stablecoin complex explains the capex boom. On the obligor side — the only basis that cannot double-count — **US nonfinancial corporate debt/GDP has fallen 5.8 points since end-2021 and the sector's financing gap is −$635bn SAAR.** Whatever the story is, it is not that US corporates are borrowing more relative to income.

---

**Reproduction paths (all verified live, 21 Aug 2026):**
- Z.1 full CSV package: `https://www.federalreserve.gov/releases/z1/current/z1_csv_files.zip` (8,075,952 bytes)
- Z.1 old→new table crosswalk: `https://www.federalreserve.gov/releases/z1/current/z1_table_mapping.csv`
- FRED series: `https://fred.stlouisfed.org/graph/fredgraph.csv?id=<ID>`
- ALFRED vintages (the only way to detect the H.6 restatement): `https://alfred.stlouisfed.org/graph/alfredgraph.csv?id=<ID>&vintage_date=<YYYY-MM-DD>`
- FSB GMR 2025: `https://www.fsb.org/uploads/P161225.pdf`
- FRBNY SR 580: `https://www.newyorkfed.org/medialibrary/media/research/staff_reports/sr580.pdf`
- OFR WP 14-04: `https://www.financialresearch.gov/working-papers/files/OFRwp2014-04_Pozsar_ShadowBankingTheMoneyView.pdf`
- H.6 current release and notes: `https://www.federalreserve.gov/releases/h6/current/default.htm`
- H.8 methodology: `https://www.federalreserve.gov/releases/h8/about.htm`

Working files retained at `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/` (Z.1 package unzipped at `z1/`, FSB text at `fsb.txt`, ALFRED vintage pairs at `alf_*.csv`, computation scripts at `/tmp/z1calc.py`, `/tmp/z1r.py`, `/tmp/vint.py`, `/tmp/macro.py`).