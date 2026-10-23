# Spec: US-dollar international debt securities by issuer sector and residence, quarterly (BIS IDS; candidate X6; spec author, 23 Oct 2026; rewritten after rounds 2 and 3)

*Scoping: candidate X6 in `_research/2026-10-19-CGFS65-Dollar-Funding-Reading.md`; `dossiers/cross-border-and-fx.md`. House style follows
`_research/2026-10-19-UK-Gold-Exports-China-HK-Spec.md` and `_research/2026-10-19-FX-Hedged-Treasury-Yield-Spec.md`. The fetch code copies
the `Fetcher` and STOP latch of `bin/fx_rate_gap.py`, which already pulls `stats.bis.org` (WS_XRU). Proposed CALENDAR row: 2026-12-07 (section 7).*

*This text applies the supervisor's round-1 rulings, the round-2 rulings (second review) and the round-3 rulings (Grok attack), which stay at
the end as the record; where round 3 differs from round 2, round 3 is applied; the body is authoritative. "Observed" means seen by the spec
author on 23 Oct 2026 with the CLAUDE.md non-SEC User-Agent, one request per URL: 20 requests, 18 returning 200, one 301 (the www.bis.org
release calendar, which moved; the new URL was requested once on its own) and one **403** (`https://www.bis.org/statistics/secstats.htm`;
recorded, not routed around). "Relayed" means taken from a reviewer or Grok and not re-read here.*

***The comparison is not blind.*** *The second reviewer and Grok computed all five comparison rows on real data before the build (P1 75.56%,
P2 91.78%, P3 92.63%, P4 90.69%, N1 71.85%), and the spec author re-derived them from two requests for this rewrite (section 8, C14). The
window and the 65–85% band were not changed after that. The reading rule was changed after the values were seen (R3-1): it can only withhold a
`consistent` reading, never create one, and **the round-1 rule would have printed `consistent`** on today's vintage. SOURCES.md records both.*

## 0. Goal, and what the result can and cannot say

- **Measure** the face value outstanding and the net issues of international debt securities denominated in US dollars, quarterly, by issuer
  sector (government, financial corporations and their parts, non-financial corporations, international institutions) and by issuer
  residence (all countries, US residents, **non-US residents**, advanced economies, emerging economies, international organisations).
- **Set** the build's numbers beside the CGFS paper's statement (p 22) that about three fourths of the five-year increase in international
  US dollar funding took the form of debt securities, over the same window and with the paper's own definition, and show how far that match
  depends on how bank-loan growth is measured.

**It can say:** the face value of US-dollar international bonds, notes and money-market paper owed by each group of issuers at each
quarter-end, how much each group issued net of redemptions, and each sector's share of its group's stock (denominator named in every row).
Everything is MEASURED (BIS-published series on a stated perimeter) or IDENTITY (sums and differences of those series).

**It cannot say** who holds the securities, why they were issued, whether issuers swapped the dollars into another currency, or anything
about interest rates, spreads or the dollar's exchange rate. Flows and positions are never written as the cause of a price. A security is
"international" when at least one of its registration location, governing law or listing location differs from the issuer's residence
(BIS IDS overview, observed); a dollar bond that is registered, governed and listed in its issuer's own country is outside these figures.
Residence is where the issuer is incorporated, nationality where its parent is headquartered; a Cayman subsidiary of a US company is a
non-US resident. **Required README sentence 2:** "It measures amounts owed by issuers, not who holds the securities, and it does not show
why the securities were issued or any effect on interest rates or the dollar."

## 1. Hard requirements

- **R1. Free public data only (E-005).** Host allowlist in the script: `stats.bis.org` only. Any other host is refused before the request.
  No FRED, no sec.gov, no key. The release dates (2.4) and terms (2.5) are constants copied from this spec, not fetched by the script.
- **R2. User-Agent** exactly `Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)`. Assert no `@`; M10 clean. Never
  send an email address, a name, `SEC_UA` or `CLAUDE_CODE_USER_EMAIL`.
- **R3. Polite, refusal-safe fetches.** GET only, sequential, at least 2 s apart, at most 8 requests a run, no redirect followed. Any status
  other than 200, or a body that fails a hard content test (R3a), writes `data/vintages/bis_ids_dollar/STOP` and ends the run. **No retry and
  no route around it. Only a person deletes a STOP file; no agent deletes one, the builder included.** While STOP exists `fetch` makes no
  request, prints `STOP present: <file>` and exits 2. The STOP file holds, one per line: `status`, `utc_time`, `url_path`, `retry_after`
  (header or blank), `body_head` (first 300 bytes, escaped).
- **R3a. Content tests.** Hard (STOP): JSON or CSV fails to parse; the dataflow id, name or dimension order differ from 2.1; a CSV header
  differs from 2.3's literal; a row outside the requested key; `UNIT_MEASURE` ≠ `USD`, `UNIT_MULT` ≠ `6` or `OBS_CONF` ≠ `F`; a malformed
  `TIME_PERIOD`; a duplicate series-quarter; a **semantic label** of 2.2 changed. Soft (WARN in `checks.csv`, no STOP): a **descriptive label**
  of 2.2 changed (R2-10). A blank `OBS_VALUE` is absent, not an error.
- **R4. Cache.** Raw responses go to `data/vintages/bis_ids_dollar/<YYYY-MM-DD>/` (gitignored), one folder per pull, with `fetch_log.csv`
  rows `utc_time, host, path_and_query, status, bytes, sha256`.
- **R5. Dates come from the pull folder (R2-5).** Every date in an output (`vintage`, `ids_release`, `scored_on`, revision keys) is derived from
  the pull-folder name, never from the clock. Only `fetch_log.csv`'s `utc_time` records the fetch moment.
- **R6. No causal wording** anywhere generated (G12, literal pattern in 6.3); the paper is paraphrased and its causal verbs are not repeated.
- **R7. Code ownership.** `bin/bis_ids_dollar.py` is new, standard library only, modes `fetch`, `build` (offline, byte-identical on re-run) and
  `selftest` (synthetic, no network, under 20 s). No existing script changes, except a new warn-only `bin/check.sh` guard **M20**.
- **R8. Frozen rules.** The CGFS window, the LBS keys, the band, the R3-1 reading rule and the registered statement are constants that must
  equal this spec's text (G17). After the first real-data `build`, any change to a rule in sections 3–5 or 7 is a **post-registration fix**:
  logged in SOURCES.md "Build decisions" with date, reason, whether real data had been seen, and **the old rule and old output values kept
  beside the new**. The R3-1 change is the first such entry, written by the builder from the disclosure at the top of this spec.
- **R9. Build decisions live in SOURCES.md, never in the README.**

## 2. Data

### 2.1 BIS international debt securities (IDS), SDMX API

| Item | Observed 23 Oct 2026 |
|---|---|
| Dataflow | `WS_DEBT_SEC2_PUB`, name "International debt securities (BIS-compiled)", structure `BIS:BIS_DEBT_SEC2(1.0)`. Base `https://stats.bis.org/api/v2/data/dataflow/BIS/WS_DEBT_SEC2_PUB/1.0/<key>?startPeriod=...&format=csv` |
| Key (15 dims, in order) | `FREQ . ISSUER_RES . ISSUER_NAT . ISSUER_BUS_IMM . ISSUER_BUS_ULT . MARKET . ISSUE_TYPE . ISSUE_CUR_GROUP . ISSUE_CUR . ISSUE_OR_MAT . ISSUE_RE_MAT . ISSUE_RATE . ISSUE_RISK . ISSUE_COL . MEASURE` |
| Fixed values | `Q`; `ISSUER_BUS_ULT` `1`; `MARKET` `C`; `ISSUE_TYPE` `A`; `ISSUE_CUR_GROUP` `A`; `ISSUE_CUR` `USD`; maturities `A.A`; rate `A`; risk `A`; collateral `A` |
| Residence basis | `ISSUER_RES` = group, `ISSUER_NAT` = `3P`. Nationality memo: `ISSUER_RES` `3P`, `ISSUER_NAT` `US` |
| Measures | `I` amounts outstanding; `G` net issues (`C` gross issues exists, not used) |
| Market | The availability query for every USD series returned `MARKET` = `C` only: no domestic-market USD series exists in this dataflow |
| Units | US dollars, millions (`UNIT_MULT` 6), `DECIMALS` 0; **face value** ("Amounts are presented at face value", BIS IDS overview `https://data.bis.org/topics/IDS`, observed) |
| Compilation | "a security-by-security database built by the BIS using information from commercial data providers" (IDS overview, observed) |
| Coverage | 2013-Q4 present for every group; latest **2026-Q2** |

### 2.2 Codes and the label allowlist (content test R3a; literal, from the observed structure files)

**Semantic labels (a change is a STOP):** sectors (`ISSUER_BUS_IMM`, immediate issuer): `1` "All issuers" → ALL; `2` "General government" →
GOV; `B` "Financial corporations" → FIN; `E` "Private banks" → FIN_PRIV_BANK; `I` "Public banks" → FIN_PUB_BANK; `G` "Private other financial
institutions" → FIN_PRIV_OFI; `K` "Public other financial institutions" → FIN_PUB_OFI; `7` "Central bank" → FIN_CENTRAL_BANK; `J`
"Non-financial corporations" → NFC; `S` "International institutions" → INTL_INST. Residence: `3P` "All countries excluding residents" → ALL
(see below); `US` "United States"; `5R` "Advanced economies" → ADV; `4T` "Emerging market and developing economies" → EMDE; `1C`
"International organisations" → INTL_ORG. `MARKET C` "International markets"; `MEASURE I` "Amounts outstanding", `G` "Net issues";
`ISSUE_CUR USD` "US Dollar"; `ISSUE_CUR_GROUP A` "All currencies". LBS: `L_MEASURE S` "Amounts outstanding / Stocks", `F` "FX and break
adjusted change (BIS calculated)"; `L_POSITION C` "Total claims"; `L_INSTR G` "Loans and deposits"; `L_DENOM USD` "US dollar";
`L_CURR_TYPE A` "All currencies (=D+F+U)"; `L_REP_CTY 5A` "All reporting countries"; `L_CP_SECTOR A` "All sectors", `I` "Banks, related
offices"; `L_CP_COUNTRY 5J` "All countries", `US` "United States"; `L_POS_TYPE N` "Cross-border".
**Descriptive labels (a change is a WARN):** `ISSUE_TYPE A` "All issue types"; `ISSUE_OR_MAT`/`ISSUE_RE_MAT A` "Total (all maturities)";
`ISSUE_RATE A` "All interest rates"; `ISSUE_RISK A` "All credit ratings"; `ISSUE_COL A` "All issues"; `L_REP_BANK_TYPE A` "All reporting
banks/institutions (domestic, foreign, consortium and unclassified)"; `L_PARENT_CTY 5J` "All countries".

**The `3P` label is misleading in this dataflow, and the arithmetic decides.** At 2019-Q4, USD, all issuers, outstanding: `3P` 11,586,704 =
`5R` 8,986,838 + `4T` 2,021,599 + `1C` 578,267 exactly. The C04 leaf set (all F5 residence codes except `3P`, `5R`, `4T`, `3C`, `4Y`, `4W`,
`4U`) has 131 codes with values at 2019-Q4, US 1,453,406, `1C` 578,267 and `1Z` 321,211 among them, summing to 11,586,647: `3P` minus the
leaf sum is **+57**. So `3P` is the world total including US residents, and NON_US = ALL − US. An alphabetic leaf rule (two letters only)
would drop `1C` and `1Z` and leave a gap of +899,535; that is the R2-1 mutant.

**Sector arithmetic observed (2019-Q4, outstanding):** ALL: GOV 1,187,905 + FIN 8,116,957 + NFC 1,700,325 + INTL_INST 581,517 = 11,586,704;
FIN = 2,673,055 + 311,352 + 4,544,624 + 578,867 + central bank 9,059. US: GOV 3,535 + FIN 1,141,953 + NFC 307,918 = 1,453,406; FIN = 242,561 +
50 + 852,657 + 46,685 (no US central-bank or international-institution series exists). **Central banks sit inside FIN** (IDS overview:
financial corporations "include the following entities: central banks, banks and non-bank financial corporations").

**Absent series.** Some group-sector series do not exist (US central bank, US international institutions; INTL_ORG has only ALL and
INTL_INST), and some start later (ADV and EMDE INTL_INST absent at 2013-Q4, present at 2019-Q4). An absent series-quarter is blank,
never zero, except under the C05b rule of 3.3.

### 2.3 Requests made by `fetch` (6, all `stats.bis.org`; every key below was requested by the author and returned 200)

- **F1** `/api/v2/structure/dataflow/BIS/WS_DEBT_SEC2_PUB/1.0?references=all&detail=full` (JSON, 797,104 bytes).
- **F2** `/api/v2/structure/dataflow/BIS/WS_LBS_D_PUB/1.0?references=all&detail=full` (JSON, 522,223 bytes).
- **F3** IDS main: `/api/v2/data/dataflow/BIS/WS_DEBT_SEC2_PUB/1.0/Q.3P+US+5R+4T+1C.3P.1+2+B+J+S+E+I+G+K+7.1.C.A.A.USD.A.A.A.A.A.I+G?startPeriod=2013-Q4&format=csv`.
- **F4** Nationality memo: `/api/v2/data/dataflow/BIS/WS_DEBT_SEC2_PUB/1.0/Q.3P.US.1.1.C.A.A.USD.A.A.A.A.A.I+G?startPeriod=2013-Q4&format=csv`.
- **F5** All residences, total only, for C04: `/api/v2/data/dataflow/BIS/WS_DEBT_SEC2_PUB/1.0/Q..3P.1.1.C.A.A.USD.A.A.A.A.A.I?startPeriod=2013-Q4&format=csv`.
- **F6** LBS: `/api/v2/data/dataflow/BIS/WS_LBS_D_PUB/1.0/Q.S+F.C.G.USD.A.5J.A.5A.A+I.5J+US.N?startPeriod=2013-Q4&format=csv` (8 series).

IDS CSV header (literal): `FREQ,ISSUER_RES,ISSUER_NAT,ISSUER_BUS_IMM,ISSUER_BUS_ULT,MARKET,ISSUE_TYPE,ISSUE_CUR_GROUP,ISSUE_CUR,ISSUE_OR_MAT,ISSUE_RE_MAT,ISSUE_RATE,ISSUE_RISK,ISSUE_COL,MEASURE,DECIMALS,UNIT_MEASURE,UNIT_MULT,COLLECTION,TIME_FORMAT,TIME_PERIOD,OBS_VALUE,OBS_STATUS,OBS_PRE_BREAK,OBS_CONF`.
LBS CSV header (literal): `FREQ,L_MEASURE,L_POSITION,L_INSTR,L_DENOM,L_CURR_TYPE,L_PARENT_CTY,L_REP_BANK_TYPE,L_REP_CTY,L_CP_SECTOR,L_CP_COUNTRY,L_POS_TYPE,DECIMALS,UNIT_MEASURE,UNIT_MULT,AVAILABILITY,TITLE_GRP,TIME_FORMAT,COLLECTION,ORG_VISIBILITY,TIME_PERIOD,OBS_VALUE,OBS_STATUS,OBS_CONF,OBS_PRE_BREAK`.

**LBS is used only for the CGFS comparison.** Its stocks carry break flags (`OBS_STATUS` `B`, with `OBS_PRE_BREAK`): on the all-sector series
every quarter from 2015-Q1 to 2019-Q4 is flagged. Stock changes therefore include series breaks; the BIS-calculated `F` series is adjusted
for breaks and exchange rates. Both are reported, with the gap between them in dollars.

### 2.4 Release timing, vintages and revisions

- **Release calendar.** The IDS dates come from the **"International debt securities" line** of the BIS release calendar
  (`https://data.bis.org/release-calendar`; "Data are released no later than the specified date"), never from the "Debt securities
  statistics" (`DSS`) rows, which carry a different quarter on the same dates (R3-4). The static HTML holds no rows; they load from
  `https://data.bis.org/api/v0/releasecalendar`, whose `IDS` category is that line (observed): 2025-Q4 on 2026-03-16, 2026-Q1 on 2026-06-15,
  2026-Q2 on **2026-09-14**, **2026-Q3 on 2026-12-07**. Grok read the rendered page and saw the same 2026-Q3 date (relayed). LBS: 2026-Q2 on
  **2026-10-30**, an LBS revision on 2026-12-07.
- **Revision practice.** The calendar lists IDS releases only; the BIS documentation page refused this author (403). Revisions are
  **measured**: each pull is cached in a dated folder; `build` compares the newest pull with the newest earlier one and **appends** every
  changed cell to `revisions.csv`. Existing rows are never rewritten or reordered; a key already present is not written again; with no earlier
  pull one `baseline` row is written. A pull whose latest quarter is earlier than the previous pull's is a FAIL.
- **`ids_release`** = the latest IDS release date on or before the pull-folder date (a label only; scoring keys on quarters present, 7).
- **Pins are one-vintage checks.** IDS pins FAIL on a pull whose latest quarter is 2026-Q2 and WARN, with their `revisions.csv` rows, once
  2026-Q3 is in the file. LBS-dependent pins (C10, C11, C14) FAIL on a pull dated before 2026-10-30 and WARN after.

### 2.5 Licence (observed at `https://data.bis.org/help/legal`, 23 Oct 2026)

The BIS terms make use of the statistics "unrestricted, provided that" the BIS is cited when they are reproduced, and add conditions: a
translation must be marked unofficial; use must not mislead or imply endorsement; a commercial product may not charge extra for them; the BIS
gives no warranty; nothing is investment advice; no other use is permitted. The API terms concern the APIs themselves, which may not be
redistributed. The BIS stopped receiving data from Russian authorities after 28 February 2022.

**Handling (round-1 O-1 and R2-6):** the build commits the selected quarterly aggregates (`quarterly.csv`) and statistics derived from them,
each CSV headed by a `# source:` line citing "Bank for International Settlements, international debt securities statistics (and locational
banking statistics for cgfs_check.csv), retrieved <pull date>". Raw API replies stay in the gitignored cache. **SOURCES.md carries the full
text of the BIS terms**, copied by hand once from the page above at landing (the script never fetches it) and logged in "Build decisions".
The README's provenance paragraph says that BIS terms apply to these figures (not the repository's CC BY licence), that the BIS gives no
warranty, that nothing here is investment advice, and that the BIS does not endorse this work. The supervisor adds THIRD_PARTY_MANIFEST.tsv
rows at landing.

### 2.6 The CGFS paper (method reference; no fetch by the script)

BIS CGFS Papers No 65, "US dollar funding: an international perspective" (June 2020), fetched once by the author (200, 3,704,415 bytes).
- **p 22, section 3.4 (paraphrase):** over the past five years about three fourths of the increase in international US dollar funding was in
  marketable debt securities rather than bank lending. The paper's sentence uses causal wording, which the build does not repeat. The BIS press
  release of 18 June 2020 calls it three quarters "of the increase in the nominal stock" (relayed by Grok, accepted by the supervisor in round 3),
  so P1, a change in nominal stocks, is the paper's own measure.
- **Graph 10, note 1 (the definition used here):** cross-border loans by banks in all reporting countries including those in the United States,
  **including interoffice loans**; note 2: IDS "includes issuances by entities in the United States".
- **Graph 1, note 3 (a different convention):** US dollar cross-border loans by banks to counterparties in all countries, Q4 2019, **excluding
  interoffice claims** but including interbank claims. P3 follows this note.
- **p 4:** US dollar IDS plus cross-border loans "is $22.6 trillion as of Q4 2019".
- **So the paper's measure is global, US residents included; it is not "dollar funding to non-US residents".** The window is read as
  **2014-Q4 to 2019-Q4** (five years to the paper's data date; the paper does not print the start quarter; the reasoning is written in SOURCES.md).
- **Definition check (R3-5):** IDS ALL 2019-Q4 (11,586,704) + LBS all-sector US dollar cross-border loans (10,883,514.581) = **$22.47trn,
  0.57% below $22.6trn**; without related offices (4,317,263.445), $18.15trn, 19.7% below. P1 keeps interoffice positions.

## 3. Method

1. **Parse** F3–F6 after the content tests. Values stay in US$ millions (IDS integers; LBS 3 decimals as published).
2. **Groups.** ALL (`3P`), US, ADV (`5R`), EMDE (`4T`), INTL_ORG (`1C`) as published (`derived` = `source`); **NON_US = ALL − US** per sector,
   measure and quarter (`derived` = `identity`); US_NATIONALITY memo (sector ALL only, `basis` = `nationality`).
3. **NON_US blanks and C05b (round-1 O-6 as refined by R2-3).** NON_US is blank when the ALL cell is absent, or when a US series exists but
   that quarter is absent (`status` = `partial`). For the two sectors with no US series at all (FIN_CENTRAL_BANK, INTL_INST), the US value is
   taken as zero **only in quarters where C05b passes**, that is where US ALL = US GOV + FIN + NFC and US FIN = the sum of the published US FIN
   parts, each within 5 (US$ millions); such cells get `status` = `us_series_absent`. In a quarter where C05b fails, those NON_US cells are
   blank with `status` = `us_sum_mismatch`. The README names the rule.
4. **Change in outstanding** = outstanding(q) − outstanding(q−1), blank if either is blank. **`other_change_usd_m`** = change − net issues: a
   residual (C-098) holding reclassifications, coverage changes and rounding, with no independent measurement; never described as more.
   For dollar debt there is no exchange-rate revaluation (observed: ALL 2019-Q4 0; 2026-Q1 35; US 2019-Q4 1).
5. **C05 identities, every quarter:** ALL = GOV + FIN + NFC + INTL_INST; FIN = the five FIN parts; ALL(residence) = ADV + EMDE + INTL_ORG.
   Checked over present parts, printing the gap and the number of absent parts. **PASS** if the gap is at most 5; **FAIL** if it exceeds 5 with
   no absent part; **WARN** if it exceeds 5 with an absent part. **C05b** is the US-only version of 3.3, one `checks.csv` row per quarter.
6. **Shares** (`shares.csv`, 2019-Q1 to latest): GOV, FIN, NFC, INTL_INST and the five FIN parts as a percentage of **the same group's
   ALL-sector outstanding in the same quarter**; numerator, denominator value and denominator label in every row; blank if either is blank.
7. **Net-issue windows:** `2024`, `2025`, `2026_to_<L>` and `2024_to_<L>`, L = the latest quarter. Per group and sector: Σ net issues, Σ change,
   Σ other change; blank (with `quarters_blank` > 0) if any quarter is blank. `share_of_group_net_issues_pct` = sector Σ ÷ the group's
   ALL-sector Σ, **blank when that denominator is zero or negative**.
8. **CGFS comparison** (`cgfs_check.csv`). Share = IDS change ÷ (IDS change + LBS change) × 100, blank if the denominator ≤ 0. For every row:
   `lbs_flow_sum_usd_m` = Σ of the matching `F` series over the quarters after `first_quarter` up to `last_quarter`; `lbs_break_sum_usd_m` =
   LBS stock change − `lbs_flow_sum_usd_m` (an identity: the part of the stock change that BIS's adjusted flows do not count, mostly series
   breaks); `lbs_break_quarters` = quarters in the same range where any stock series used is flagged `B`.

   | Variant | Plain name (README and `plain_name`) | IDS change | LBS change |
   |---|---|---|---|
   | P1 | The paper's measure: change in published stocks | ALL outstanding 2019-Q4 − 2014-Q4 | stock `S`, sector `A`, country `5J`, 2019-Q4 − 2014-Q4 |
   | P2 | The same, using BIS break-adjusted flows | Σ ALL net issues 2015-Q1..2019-Q4 | Σ `F`, sector `A`, country `5J`, same quarters |
   | P3 | Without loans between offices of the same bank | as P1 | stock `A` − `I`, 2019-Q4 − 2014-Q4 |
   | P4 | Window one quarter earlier | ALL 2019-Q3 − 2014-Q3 | stock `A`, `5J`, 2019-Q3 − 2014-Q3 |
   | N1 | Borrowers outside the US only (not the paper's measure) | NON_US 2019-Q4 − 2014-Q4 | stock `A`, `5J` − `US`, 2019-Q4 − 2014-Q4 |

9. **Reading rule (R3-1, frozen; supersedes round 1).** With the band 65 ≤ share ≤ 85: **`consistent`** if P1 and P2 both lie inside it;
   **`mixed`** if one lies inside and the other outside; **`not_consistent`** if both lie outside; `undefined` if either share is blank. The
   reading is written on both the P1 and P2 rows (identical); P3, P4 and N1 get `described`. The P1 row's `note` says: "Reading rule changed
   after the reviewers saw P1 and P2 (round 3); the round-1 rule, P1 alone, would read consistent." On today's vintage the expected reading is
   `mixed` (P1 75.56 inside, P2 91.78 outside).
10. **Sign convention on real data (C06).** For ALL, every quarter 2014-Q1..L with |net issues| ≥ 5,000: sign(change) must equal sign(net
    issues) in at least 90% of them, else FAIL; each quarter's gap is listed.
11. **Units in prose:** the README converts to US$ billions (÷ 1,000, one decimal) or trillions (÷ 1,000,000, two decimals).

## 4. Descriptive questions, fixed in advance (answers in `summary.csv`)

No hypothesis is tested, so no minimum detectable effect applies (C-090); Q5 compares numbers with one published statement. Every answer gives
the path with its minimum and maximum quarter (C-070). **`blind` is `no`** for every Q5 row (the reviewers and the author computed them), for
any row that uses ALL, US or NON_US values from 2014-Q3 to 2019-Q4 or from 2025-Q4 to 2026-Q2, ALL or US sector values at 2019-Q3 or 2019-Q4,
or US_NATIONALITY at 2013-Q4 or 2019-Q4; otherwise `yes`.

- **Q1. Levels.** Outstanding by group and sector, 2019-Q1 to L: value at 2019-Q4 and at L, the change, and the minimum and maximum quarters.
- **Q2. Net issues 2024 to latest.** For each window of 3.7, by group and sector: Σ net issues, Σ other change, quarters with negative net issues.
- **Q3. Sector shares.** Each sector's share of its group's outstanding at 2019-Q4 and at L, and the change in percentage points; the same for
  the FIN parts. Denominator: the group's ALL-sector outstanding.
- **Q4. Residence and nationality (R3-2).** US-resident outstanding (issuer incorporated in the US) and US-nationality outstanding (issuer's
  parent headquartered in the US), all sectors, at 2019-Q4 and at L, published as **two separate totals**; no difference row is committed.
  The README describes their difference only as the net of two groups: issuers outside the US with a US parent (counted in the nationality
  total only) and issuers inside the US with a foreign parent (counted in the residence total only).
- **Q5. The CGFS statement beside the build.** Rows P1–P4 and N1 with their break sums and break quarters, and the R3-1 reading. A `mixed` or
  `not_consistent` reading is reported as such and not explained away.
- **Q6. Revisions.** At each new vintage: cells changed, the largest absolute and percentage change, and any change to a quarter before 2024.

## 5. Outputs (`data/bis_ids_dollar/`)

Every CSV begins with one `# source:` line. **Header allowlist, canonical text** (one line per file, `<name>:<headers comma-joined, no
spaces>`, LF after every line including the last, in this order). The script holds `SPEC_ALLOW_SHA256`; G11 and M20 skip the `# source:` line.

```
quarterly.csv:quarter,basis,issuer_group,sector,outstanding_usd_m,net_issues_usd_m,change_in_outstanding_usd_m,other_change_usd_m,status,derived,vintage,ids_release
shares.csv:quarter,issuer_group,sector,share_pct,numerator_usd_m,denominator_usd_m,denominator
net_issues_windows.csv:window,first_quarter,last_quarter,issuer_group,sector,quarters_n,quarters_blank,net_issues_usd_m,change_in_outstanding_usd_m,other_change_usd_m,share_of_group_net_issues_pct,denominator
cgfs_check.csv:variant,plain_name,definition,first_quarter,last_quarter,ids_change_usd_m,lbs_change_usd_m,lbs_measure,lbs_flow_sum_usd_m,lbs_break_sum_usd_m,lbs_break_quarters,ids_share_of_increase_pct,denominator,reading,note
summary.csv:question,window,issuer_group,sector,statistic,value,denominator,blind
revisions.csv:vintage_prev,vintage_new,quarter,basis,issuer_group,sector,measure,value_prev_usd_m,value_new_usd_m,change_usd_m,change_pct
registration_score.csv:registered_on,scored_on,vintage_prev,vintage_new,latest_quarter_new,cells_checked,largest_abs_change_pct,largest_cell,threshold_pct,result,note
checks.csv:check_id,description,expected,observed,status
fetch_log.csv:utc_time,host,path_and_query,status,bytes,sha256
```

**sha256 of that text (1,203 bytes): `c84601784c545b2722847ad58803ba906564f8325fabd580c7fb0d2ce86735af`** (computed by the spec author; the
round-1 text, `4a156e71…a03f9`, is superseded and kept here only as the record).

Values: `quarter` `YYYY-Qn` from 2014-Q3 (so P4 and 2014-Q4 changes exist) to L; `basis` ∈ {residence, nationality}; `issuer_group` ∈ {ALL,
US, NON_US, ADV, EMDE, INTL_ORG, US_NATIONALITY}; `sector` ∈ {ALL, GOV, FIN, FIN_PRIV_BANK, FIN_PUB_BANK, FIN_PRIV_OFI, FIN_PUB_OFI,
FIN_CENTRAL_BANK, NFC, INTL_INST}; `status` ∈ {ok, absent, partial, us_series_absent, us_sum_mismatch}; `derived` ∈ {source, identity};
`variant` ∈ {P1, P2, P3, P4, N1}; `lbs_measure` ∈ {stock_difference, break_adjusted_flows}; `reading` ∈ {consistent, mixed, not_consistent,
undefined, described}; `blind` ∈ {yes, no}; `result` ∈ {PENDING, HELD, FALSIFIED, VOID}. Percentages to 2 decimals; US$ millions as integers
(LBS-derived to 3 decimals).

The folder holds exactly these nine CSVs plus `README.md` and `SOURCES.md` (11 names). Cache (gitignored): `data/vintages/bis_ids_dollar/`.

- **`README.md`** (generated; G12 scans it), in this order, each term defined at first use:
  1. Two plain opening sentences: "This table shows the face value of US-dollar bonds and short-term paper that borrowers owe on securities
     issued outside their home markets, by type of borrower and by the country where the borrower is incorporated, each quarter since 2014,
     from the Bank for International Settlements (BIS). It measures amounts owed by issuers, not who holds the securities, and it does not show
     why the securities were issued or any effect on interest rates or the dollar." (O-11: the second reviewer's own opening sentence was not
     in the spec author's context; the supervisor substitutes it if it differs.)
  2. Definitions: face value; "international" as registration, governing law or listing outside the issuer's residence; residence versus
     nationality; and the sentence "The groups overlap, so do not add them up: ALL contains both US and NON_US, ADV, EMDE and INTL_ORG are a
     second split of ALL, and the US-nationality total cuts across both."
  3. The latest result: outstanding by group and sector at L and at 2019-Q4 in US$ billions; net issues for the windows of 3.7; shares with
     their denominator in the table header; the Q4 residence and nationality totals as two figures with the net-of-two-groups sentence.
  4. The CGFS comparison, by plain names: the paper's statement paraphrased, its definition (global, US residents and interoffice loans
     included), the window, the **P1–P4 table with break sums and break quarters**, N1 with "N1 is not the paper's measure", the reading, and
     the sentence that the reading rule was set after the values were seen and that the earlier rule would have read consistent. **Whenever
     P1's share lies inside 65–85, the README also prints the R2-2 sentence:** "P1 reproduces the paper's figure only on LBS stock changes,
     which contain BIS series breaks. 'Consistent' means one construction matches, not that the figure is robust." (O-12: the ruling quotes
     this sentence with an elision; the supervisor supplies the full text if it differs.)
  5. Blanks, `us_series_absent` and `us_sum_mismatch`; `other_change_usd_m` as a residual; LBS break flags.
  6. Column dictionary; one worked row (2019-Q4 ALL from its four sectors: 1,187,905 + 8,116,957 + 1,700,325 + 581,517 = 11,586,704).
  7. Provenance last, one paragraph: BIS citation, retrieval and release dates, BIS terms apply (not CC BY), no warranty, not investment
     advice, not endorsed by the BIS.
  The questions of section 4, the window reasoning and the build decisions are not in the README.
- **`SOURCES.md`:** F1–F6 with URLs; the full BIS terms (2.5); the label allowlist; the release dates and the `IDS`-not-`DSS` rule; the `3P`
  finding; the window reasoning (2.6); column provenance; that the second reviewer and Grok saw the comparison values before the build; and
  "Build decisions" (R8, R9), opening with the R3-1 entry: old rule (P1 alone, band 65–85), new rule (3.9), the values seen (P1 75.56, P2 91.78),
  and that the old rule would have printed `consistent`.

## 6. Leak and wording rules

1. Only the 11 names in the folder. A raw SDMX file is recognised by **any line** beginning `FREQ,ISSUER_RES` or `FREQ,L_MEASURE`, or a body
   containing `"dataStructures"`; none may sit anywhere in the repository outside the cache (R2-8).
2. No `@`, no local path (`/Users/`, `/private/`, `/tmp/`, `~/`) in any committed file.
3. **Causal wording**, case-insensitive, the literal pattern (`bin/hedged_ust_yield.py`'s pattern as it resolves today, plus "fuelled", R2-9):
   `\b(caus(?:e|ed|es|ing)|drove|driv(?:e|es|en|ing)|leaned?\s+against|because\s+of\s+(?:the\s+)?intervention|led\s+to|prompted|pushed|in\s+response\s+to|because\s+of|fuell?ed)\b`
   is copied into the script as a literal, not imported. No match is allowed in any generated file. Also banned: any row or README sentence
   labelling P1, P2, P3 or P4 as "funding to non-US residents".

## 7. Pre-registration (proposed CALENDAR row 2026-12-07)

**Why no market statement.** A forecast that 2026-Q3 net issues fall inside the last ten quarters' range has a base rate of about 82% (9 in 11)
for exchangeable draws, and a sign forecast is near-certain; neither tests anything this build is about (C-090). The honest statement available
is about the data: how far the BIS revises history at the next release, which decides how far the pins and the comparison hold across vintages.

**Proposed CALENDAR row text (the supervisor edits CALENDAR; the builder does not):** `2026-12-07 | BIS IDS 2026-Q3 release (no later than;
the "International debt securities" line of the BIS release calendar, checked 23 Oct). Run bin/bis_ids_dollar.py fetch and build; read
revisions.csv and registration_score.csv. PRE-REGISTERED 23 Oct 2026 (HYPOTHESIS about BIS revision practice, not about markets): between the
build's baseline pull from the 14 Sep 2026 release and the first pull whose latest quarter is 2026-Q3, no quarterly amount outstanding of
US-dollar international debt securities for ALL or US residents, sector ALL, 2019-Q4 to 2026-Q1 (52 cells), changes by more than 1.0%.
FALSIFIED if any cell does. PENDING until 2026-Q3 is in the file. VOID if no baseline pull exists. The 1.0% has no prior behind it.`

**Scoring (R2-4, R3-4):** baseline = the earliest pull with `ids_release` 2026-09-14; the score is computed only when the newest pull's latest
quarter is 2026-Q3 or later, otherwise PENDING, whatever the calendar date; `scored_on` is that pull's folder date. The script holds
`REGISTERED = ("2026-10-23", "2019-Q4", "2026-Q1", ("ALL", "US"), "ALL", 1.0, 52)`; G17 requires the CALENDAR row, when present, to contain
`52 cells`, `sector ALL` and `more than 1.0%` (C09).

## 8. Pinned checks (`checks.csv`) — re-derived by the spec author from the 23 Oct 2026 pulls (IDS release 14 Sep 2026; LBS release 31 Jul 2026)

- **C01 IDS ALL** outstanding: 2014-Q3 8,683,591; 2014-Q4 8,778,278; 2019-Q3 11,438,948; 2019-Q4 11,586,704; 2026-Q1 15,871,836; 2026-Q2
  16,274,316. Net issues: 2019-Q4 147,756; 2026-Q1 346,000; 2026-Q2 402,479.
- **C02 IDS US** outstanding: 2014-Q3 1,485,957; 2014-Q4 1,498,712; 2019-Q3 1,467,852; 2019-Q4 1,453,406; 2025-Q4 1,835,190; 2026-Q1
  1,878,256; 2026-Q2 1,952,509. Net issues 2019-Q4 −14,447; 2026-Q1 43,066.
- **C03 Sectors, 2019-Q4 outstanding:** ALL as in 2.2 (nine values); US GOV 3,535, FIN 1,141,953, NFC 307,918, FIN parts 242,561, 50, 852,657,
  46,685. Identities exact.
- **C04 `3P` includes the US (R2-1, signed).** Leaf set = all F5 residence codes except `3P`, `5R`, `4T`, `3C`, `4Y`, `4W`, `4U`; d = `3P` − Σ leaf,
  every quarter. **PASS** if |d| ≤ 0.1% of `3P` (2019-Q4: d = +57). **FAIL and STOP** only on the signature of a `3P` that excludes the US:
  d < 0 and |d + US| ≤ 10% of US. **WARN** otherwise (for example the alphabetic-rule gap of +899,535). Also ADV + EMDE + INTL_ORG = ALL
  (2019-Q4 exact). (O-13: the reviewer's exact wording of the signed test was not in the author's context; this is the author's rendering.)
- **C05 / C05b** as 3.5 and 3.3, every quarter (2019-Q3 and 2019-Q4 US: exact).
- **C06 Sign convention** as 3.10 (ALL 2019-Q4: change 147,756 = net issues; US 2019-Q4: change −14,446, net issues −14,447).
- **C07 Units:** every row USD, `UNIT_MULT` 6, `OBS_CONF` F; ALL outstanding in [5,000,000, 50,000,000] every quarter.
- **C08 Nationality memo:** US_NATIONALITY 2019-Q4 2,754,559; 2013-Q4 1,955,757, net issues 20,953.
- **C09 Calendar text** as section 7; absent, INFO.
- **C10 LBS stocks and flows:** `S A 5J` 2014-Q3 10,443,386.682; 2014-Q4 9,975,340.668; 2019-Q3 10,726,269.4; 2019-Q4 10,883,514.581 (`B`,
  pre-break 10,834,001.584). `S I 5J` 2014-Q4 3,632,452.557; 2019-Q4 4,317,263.445. `S A US` 2014-Q4 2,748,321.699; 2019-Q4 2,538,435.28.
  `F A 5J` 2019-Q4 107,732.184. `S A 5J` flagged `B` in 20 of 20 quarters 2015-Q1..2019-Q4.
- **C11 Paper level (R3-5):** IDS ALL + LBS `S A 5J` at 2019-Q4 within 3% of $22.6trn (observed 22,470,218.581, −0.57%).
- **C12 Coverage:** first quarter 2013-Q4 for ALL and US; latest ≥ 2026-Q2; all 10 sectors present for ALL; US_NATIONALITY exists.
- **C13 Fixed output:** a second `build` leaves every sha256 unchanged, `revisions.csv` included.
- **C14 Comparison rows (R2-2), 0.01 pp; WARN after 2026-10-30:**

  | Row | IDS change | LBS change | LBS flow sum | Break sum | Share % |
  |---|---|---|---|---|---|
  | P1 | 2,808,426 | 908,173.913 | 251,396.545 | 656,777.368 | **75.56** |
  | P2 | 2,808,425 | 251,396.545 | 251,396.545 | 656,777.368 | **91.78** |
  | P3 | 2,808,426 | 223,363.025 | 262,792.940 | −39,429.915 | **92.63** |
  | P4 | 2,755,357 | 282,882.718 | −154,270.545 | 437,153.263 | **90.69** |
  | N1 | 2,853,732 | 1,118,060.332 | 469,838.819 | 648,221.513 | **71.85** |

  All five equal the second reviewer's values; P1, P2 and the P1 break sum equal Grok's. Reading on this vintage: `mixed`.

## 9. Selftests (synthetic only; each guard applies its own mutant, and an uncaught mutant fails the selftest)

| Guard | Protects | Mutant that must be caught |
|---|---|---|
| G1 key | 2.1, 2.3 | `ISSUER_RES` and `ISSUER_NAT` swapped; `MARKET` `A` or `1`; `ISSUE_CUR_GROUP` `F`; `ISSUER_BUS_ULT` used as the sector; a 14-dimension key |
| G2 labels | 2.2, R3a | `MARKET C` reading "Domestic market" or `B` reading "Banks" accepted without STOP; a descriptive-label change raising STOP instead of WARN |
| G3 units | 2.1, C07 | `UNIT_MULT` 9 accepted; values divided by 1,000 before writing; README trillions computed ÷ 1,000 |
| G4 sign | 3.4, 3.10 | net issues negated; change taken as q−1 minus q; signs opposite in 3 of 10 large quarters passing C06 |
| G5 blanks, C05b | 2.2, 3.3 | an absent cell written 0; NON_US filled when a US quarter is absent but the series exists; **NON_US FIN_CENTRAL_BANK filled in a quarter where C05b fails** (fixture: US ALL ≠ GOV + FIN + NFC by 40); `us_series_absent` applied to a series that exists |
| G6 identities | 3.5 | central bank left out of FIN; INTL_INST counted twice; a 6-unit gap with no absent part passing; the same gap with an absent part giving FAIL instead of WARN |
| G7 non-US, C04 | 3.2, C04 | NON_US = ADV − US; NON_US = ALL; **the alphabetic leaf rule** (fixture with `1C` and `1Z` must not PASS); a fixture where `3P` excludes the US must FAIL and write STOP; a fixture with d = +899,535 must WARN, not STOP |
| G8 windows | 3.7 | 2023-Q4 inside `2024`; L dropped from `2026_to_<L>`; a share over a non-positive denominator |
| G9 shares | 3.6 | NON_US share divided by ALL's total; a FIN part divided by FIN; numerator and denominator from different quarters |
| G10 CGFS | 3.8, 3.9, 5 | P1 window 2015-Q1 to 2019-Q4; P1 without related offices; share = IDS ÷ LBS; **the round-1 rule (P1 alone) giving `consistent` on a fixture with P1 inside and P2 outside (must be `mixed`)**; P1 and P2 rows with different readings; a reading on P3; band 60–90; break sum computed as flows − stocks; N1 without its label; **a README with P1 inside the band that omits the P1–P4 table or the R2-2 sentence**; the disclosure note missing from P1 |
| G11 allowlists, folder | 5, 6.1 | an extra or renamed column; `SPEC_ALLOW_SHA256` ≠ sha256 of the canonical text; the round-1 hash accepted; a 12th file; the `# source:` line compared as a header; when the spec is in `_research/`, its fenced block hashing differently |
| G12 wording | R6, 6.3 | each alternative of the 6.3 pattern planted in a README fixture (including "fuelled" and "fueled"); "funding to non-US residents" applied to P1–P4; sentence 2 changed to "shows why"; the two opening sentences, the overlap sentence and the R2-2 sentence must pass |
| G13 fetch safety | R1–R3 | a non-allowlisted host; `@` in the UA; a redirect followed; requests under 2 s apart; a 429 retried; a 9th request; a POST |
| G14 STOP latch | R3 | static: `os.remove`, `os.unlink`, `os.replace`, `os.rename`, `shutil.rmtree`, `shutil.move`, `Path.unlink` or `Path.rename` applied to a STOP path. **Runtime:** with a planted STOP, `fetch` makes no request, exits 2, and the STOP file's sha256 is unchanged; a STOP written by a fixture 503 carries the five fields |
| G15 revisions | 2.4 | an existing row rewritten or reordered; a key appended twice; the previous vintage read from `quarterly.csv`; no `baseline` row on the first pull; an earlier latest quarter accepted |
| G16 leak guard | 6.1, 6.2 | **run on a planted bad folder** holding a raw F3 CSV, **the same CSV with a `# source:` line prepended**, a JSON structure file, a file containing `/Users/`, and a 12th name: each reported; the clean folder passes |
| G17 frozen rules | R8, 7 | `REGISTERED` edited (1.5, or 51 cells, or a sector other than ALL); the window, LBS keys, band or reading rule changed without a "Build decisions" entry holding the old values; the R3-1 entry missing from SOURCES.md |
| G18 blind | 4 | a Q5 row marked `blind = yes`; a Q1 row using 2019-Q4 ALL marked `yes` |
| G19 dates | R5 | a fixture pull folder `2026-09-20` built with the clock set to 2027-01-01: any output date other than 2026-09-20 (or its release 2026-09-14) |
| G20 calendar, scoring | 2.4, 7 | IDS release dates taken from the `DSS` rows; a pull dated 2026-12-07 whose latest quarter is 2026-Q2 scored HELD (must be PENDING); scoring against a pull other than the 14 Sep baseline |

## 10. Success criteria

1. `python3 bin/bis_ids_dollar.py selftest` prints G1–G20, every mutant caught, exit 0.
2. `fetch` makes 6 requests, all logged, no STOP. If a STOP is written, the builder stops and tells the supervisor; nothing is retried.
3. `build`: C01–C08 and C10–C14 PASS on a pull dated before 2026-10-30 whose latest quarter is 2026-Q2 (later pulls: C10, C11 and C14 may
   WARN with their `revisions.csv` rows; once 2026-Q3 is in the file, C01–C03 and C08 likewise); C04 may also WARN only with a stated
   reason; C09 PASS or INFO. Any other WARN goes to the supervisor. `cgfs_check.csv` reads `mixed` on P1 and P2 on today's vintage; any other
   reading on a pre-30-October pull is a defect to report. `summary.csv` holds a row for every question in section 4.
4. A verifier re-derives two numbers by hand from the cache: 2019-Q4 ALL = GOV + FIN + NFC + INTL_INST = 11,586,704; and P1's break sum,
   908,173.913 − 251,396.545 = 656,777.368.
5. `bin/check.sh --all`: the existing ✓ lines plus warn-only **M20** (`data/bis_ids_dollar/`: the 11 names, headers against the canonical text
   skipping `# source:`, no raw SDMX file by the any-line rule outside the cache, no `@`, no local path, no 6.3 match in the README). On a
   scratch copy with a planted raw F3 CSV carrying a `# source:` first line, a renamed header and a `/Users/` path it prints three ✗ lines;
   on the clean folder ✓.
6. **README cold-reader test:** two fresh agents, a non-specialist and a fixed-income practitioner, read only the README. A reader who comes
   away believing it shows who holds the bonds, that issuance moved rates or the dollar, that P1 measures funding to non-US residents, that the
   paper's figure is robust to how loan growth is measured, or that the groups can be added up, fails it.

**Landing (builder):** `.gitignore` rule for `data/vintages/bis_ids_dollar/`; the BIS terms copied into SOURCES.md by hand (2.5); a
REPRODUCE.md paragraph; a HANDOVER row; proposed (not edited) CALENDAR text of section 7 and a quarterly row (after each IDS release: `fetch`,
`build`, read `revisions.csv`). The builder commits nothing; the supervisor verifies, adds THIRD_PARTY_MANIFEST.tsv rows, edits CALENDAR and
writes any findings text.

## 11. OPEN questions

- **O-1 RULED (round 1):** commit the selected aggregates with the BIS citation; raw replies stay in the cache (2.5).
- **O-2 RULED (round 1):** window 2014-Q4 to 2019-Q4; P4 printed beside it without a reading.
- **O-3 RULED (round 1):** the paper's definition is the reading row; N1 is labelled "not the paper's measure".
- **O-4 OPEN: revision practice.** The documentation page returned 403 on 23 Oct (not retried); revisions are measured by `revisions.csv`.
- **O-5 OPEN: the `3P` label** says "excluding residents", but the arithmetic shows a world total including the US; C04 guards it.
- **O-6 RULED (round 1, refined by R2-3):** the zero treatment of a never-published US series applies only in quarters where C05b passes (3.3).
- **O-7 OPEN, not built:** nationality by sector (`ISSUER_BUS_ULT`), gross issues, single countries, and an INFO cross-check against the GLI
  debt-securities series (`WS_GLI` `Q.USD.3P.N.A.I.D.USD`).
- **O-8 CLOSED:** the IDS overview (observed 23 Oct) confirms the security-by-security database built from commercial data providers.
- **O-9 RULED (round 1, and kept in rounds 2 and 3):** the 65–85% band stands; the reading rule is R3-1's.
- **O-10 RULED:** the check.sh guard is M20.
- **O-11 OPEN: the reviewer's opening sentence** (round-2 README ruling) was not in the spec author's context; 5.1 is the author's text.
- **O-12 OPEN: the R2-2 sentence** is quoted in the ruling with an elision; 5.4 prints the two quoted parts only.
- **O-13 OPEN: wording "as the reviewer wrote it"** for the C04 signed test (R2-1), C05 (R2-3), Q4 and section 2.6 (R2-7) and the smaller
  points (R2-10, apart from the STOP-only-on-semantic-labels rule) was not in the spec author's context. Sections 3.3, 3.5, 2.6 and C04 are the
  author's renderings of the rulings (Q4 follows R3-2, which supersedes R2-7); the supervisor confirms or substitutes the reviewer's text.
- **O-14 OPEN: full BIS terms.** The spec paraphrases them; SOURCES.md must carry the full text (R2-6), copied by hand at landing.

## Supervisor rulings, 23 Oct 2026 (before any data run)

- **O-1:** BIS terms ("The use of the statistics is unrestricted, provided that" the BIS is cited) allow committing the selected quarterly aggregates with the citation; raw API replies stay in the gitignored cache.
- **O-2:** window 2014-Q4 to 2019-Q4 stands; the one-quarter-earlier variant is printed beside it without a verdict.
- **O-3:** the paper's definition is the verdict row; the non-US view is labelled "not the paper's measure".
- **O-6:** a series the BIS does not publish for the US (central bank, international institutions) is treated as zero in the non-US subtraction only where the US total equals the sum of the published US sectors (checked every build); otherwise the non-US cell is blank. The README names the rule.
- **O-9:** the 65–85% band stands.
- **O-10:** the check.sh guard is **M20**.
## Supervisor rulings, round 2 (second review), 23 Oct 2026 — before the build

The second reviewer computed the comparison rows on real data (P1 75.56%, P2 91.78%, P3 92.63%, P4 90.69%, N1 71.85%), so the comparison is no longer blind. The window (2014-Q4 to 2019-Q4) and the 65–85% band are NOT changed: changing them now would be choosing after seeing. Instead the sensitivity is forced into every output. All ten fixes are accepted:
- **R2-1** C04 leaf set (all F5 issuer codes except 3P, 5R, 4T, 3C, 4Y, 4W, 4U) and the signed test as the reviewer wrote it; STOP only on the signature of a 3P that excludes the US; mutant "alphabetic leaf rule".
- **R2-2** C14 pins the five comparison rows (0.01 pp; WARN after the 30 Oct 2026 LBS release). `lbs_break_sum_usd_m` (656,777 for P1) beside the quarter count. When P1 reads `consistent`, the README must print the P1–P4 table and the reviewer's sentence ("P1 reproduces the paper's figure only on LBS stock changes, which contain BIS series breaks … 'Consistent' means one construction matches, not that the figure is robust."), with a G10 mutant that omits it. SOURCES.md records that the reviewer saw these values before the build.
- **R2-3** C05 PASS/FAIL/WARN as written, C05b per quarter, NON_US blank where C05b fails, G5 mutant. This refines round-1 O-6.
- **R2-4** Score the 7 Dec registration only if the newest pull's latest quarter is 2026-Q3 or later, else PENDING; compare against the 14 Sep baseline pull; "sector ALL" (52 cells).
- **R2-5** All dates in outputs come from the pull-folder date, never the clock.
- **R2-6** Supervisor adds THIRD_PARTY_MANIFEST.tsv rows at landing; SOURCES.md carries the full BIS terms; README provenance says BIS terms apply (not CC BY), no warranty, not investment advice, not endorsed.
- **R2-7** Q4 and §2.6 wording as the reviewer wrote it, including both CGFS graph notes.
- **R2-8** G16 recognises a raw file by any line beginning `FREQ,ISSUER_RES` or `FREQ,L_MEASURE`; mutant with a `# source:` line prepended.
- **R2-9** The literal causal pattern is pasted in, plus "fuelled".
- **R2-10** Smaller points as listed; hard STOP only on the semantic labels.
- README: the reviewer's opening sentence; plain names for P1–P4 and N1; window reasoning in SOURCES.md; the "groups overlap, do not add them up" sentence.
## Supervisor rulings, round 3 (Grok attack, g10), 23 Oct 2026 — before the build

Grok reproduced the second reviewer's comparison exactly (IDS change 2,808,426; LBS stock change 908,174, every quarter break-flagged; break-adjusted flows 251,397; P1 75.56%, P2 91.78%; about $0.66trn of the loan-stock change is the gap between stock change and flows). The BIS press release of 18 June 2020 says "three-quarters of the increase in the nominal stock", so P1 (nominal stocks) is the paper's own measure.
- **R3-1 Reading rule (amends the round-1 verdict, disclosed).** P1 and P2 are both reported, with the break gap in dollars and in quarters. The reading is `consistent` only if P1 and P2 both fall inside 65–85%; `mixed` if they fall on opposite sides (the expected result on today's vintage: the paper's nominal-stock share is reproduced, the break-adjusted flow share is not); `not_consistent` if both fall outside. This change was made after both reviewers had computed P1 and P2; it can only withhold a "consistent" reading, never create one, and SOURCES.md records that the round-1 rule would have printed `consistent`. The README sentence of R2-2 stays.
- **R3-2 Q4** publishes the residence and nationality totals separately and describes their difference as the net of US-parent issuers outside the US and foreign-parent issuers inside it (supersedes the "definition, not an estimate" wording, as R2-7).
- **R3-3** The README says amounts are face value and that "international" means listed, registered or governed by law outside the issuer's home country (BIS IDS overview).
- **R3-4** The 7 Dec 2026 revision check is scored only when 2026-Q3 is in the file (as R2-4); the IDS release date is taken from the HTML calendar's "International debt securities" line, not the JSON `DSS` rows.
- **R3-5** P1 keeps interoffice positions (the paper's Graph 10 definition); C11 reference: IDS plus all-sector US-dollar cross-border loans 22.47trn against the paper's 22.6trn.

## Supervisor rulings, round 4 (spec author's open items), 23 Oct 2026 — before the build

The second reviewer's exact texts, which the author did not have:
- **O-11 README opening sentence:** "This folder shows how many US dollars borrowers owe on bonds and short-term paper sold outside their home markets, split by type of borrower and by where the borrower is based." The face-value and "international" definitions of R3-3 follow in the next sentences.
- **O-12 R2-2 sentence, in full:** "P1 reproduces the paper's figure only on LBS stock changes, which contain BIS series breaks (657bn of 908bn here). On break-adjusted flows, without related offices, or with the window moved one quarter, the share is 91–93%, outside the band. 'Consistent' means one construction matches, not that the figure is robust." Under R3-1 it is printed whenever P1 is inside the band, whatever the reading. The two numbers in it are generated, not hard-coded.
- **O-13 C04:** "F5 leaf codes = every ISSUER_RES in F5 except the aggregates 3P, 5R, 4T, 3C, 4Y, 4W, 4U (131 at 2019-Q4; `1C` and `1Z` are leaves). PASS if |3P − Σleaf| ≤ 0.1% of 3P and |(3P − Σleaf) + US| ≥ 0.9 × US. FAIL and write STOP only if the second leg fails." **C05:** "PASS if gap ≤ 5. FAIL if gap > 5 and no part is absent. WARN if gap > 5 and a part is absent." The author's renderings of R2-7 and R2-10 are accepted.
- **O-14 BIS terms:** SOURCES.md links https://data.bis.org/help/legal, quotes only the core condition (under 15 words) and summarises the rest in plain words (citation required; no warranty; not investment advice; no implied endorsement; the API itself is not redistributed). No full copy of the terms is committed.
- **Calendar source:** the JSON feed's "International debt securities" category is accepted as the same line as the rendered page.
