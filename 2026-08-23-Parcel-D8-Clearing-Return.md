# Parcel D8 — Treasury clearing: the sponsored pipe, Gemini's return adjudicated, and the question answered

*23 August 2026, evening. Return received 20:33 at the Dropbox share root (`D8_Clearing_Scouting_Return.md`, 3,817
words, 9 IDs), filed as `_research/D8_Clearing_Scouting_Return_gemini_ondisk.md` (sha256 62ff3839…). **Verified row by
row the same evening by seven fetch-and-report agents** (raw: `_research/D8_verification_results_2026-08-23.json`), the
primary documents archived under `_research/primary_sources/treasury_clearing/`, and the question the parcel was built
for answered from those documents and our own DTCC series. Register: **C-057**. Rules: C-045, C-049–C-051, C-054–C-056.*

---

## 1. The question, answered: is the 2026 decline in FICC sponsored repo shrinkage or migration?

**Neither, in the strong sense. It is a year-end spike unwinding into a plateau — and the next step-change is on the
calendar, not in the market.** Four independent sources, none from the return's text:

**(a) Our DTCC series, read as monthly averages, not point values.** The "−$664bn from the December peak" in the N3 doc
was mostly the 31 December spike. Monthly averages of total sponsored activity (`data/history/ficc_sponsored_total_bn.csv`):

| $bn, monthly average | Mar-25 | Jun-25 | Sep-25 | Oct-25 | Nov-25 | **Dec-25** | Jan-26 | Feb-26 | Mar-26 | Apr-26 | May-26 | Jun-26 | Jul-26 | Aug-26 (to 20th) |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Total sponsored | 1,799 | 2,044 | 2,237 | 2,402 | 2,592 | **2,672** | 2,516 | 2,498 | 2,499 | 2,430 | 2,422 | 2,505 | 2,429 | **2,336** |
| — sponsored repo (hedge funds borrowing) | 747 | 870 | 1,012 | 1,116 | 1,209 | **1,248** | 1,104 | 1,112 | 1,093 | 1,057 | 1,017 | 1,104 | 1,070 | **1,032** |
| — sponsored reverse repo (MMFs lending) | 1,051 | 1,175 | 1,225 | 1,286 | 1,383 | **1,425** | 1,411 | 1,387 | 1,406 | 1,373 | 1,404 | 1,402 | 1,359 | **1,304** |

A plateau at ~$2.5trn through June, drifting to $2.34trn in August: **−12% from the December average, −17% on the
hedge-fund side, −8% on the money-fund side.** Still +12% on August 2025 (June on June: +23%).

**(b) OFR, 20 August 2026 — *Central Clearing in Treasury Repos Plateaued in Q1 2026* (Cenicola & Mann), from OFR's own
cleared and non-cleared collections, 1 Jul 2025–23 Apr 2026.** Share of all Treasury repo cleared peaked at **53%** around
year-end and fell to **~46%**; of the in-scope subset (non-affiliate, fixed-term) **72% → ~62%**, still 7pp above July 2025.
**The decline is concentrated in G-SIBs: 55% cleared in December → 45%, "approximately how much G-SIB repo was cleared in
September 2025"** — the G-SIB surcharge is measured at year-end and clearing reduces it; **non-G-SIBs rose steadily 40% →
55%.** MMFs clear less than half their activity (FICC's new Collateral-in-Lieu service may lower their cost); hedge-fund
*reverse* repo is cleared far less than hedge-fund repo (netted packages, no balance-sheet gain from clearing); 37% of
in-scope repo is still uncleared. Footnote: FICC is **"the only U.S. Treasury repo Covered Clearing Agency currently
operating."** And: as of May 2026 the SEC will not require affiliate repo to be cleared if the affiliate clears everything
else — a 2026 relief the return's M1 missed.

**(c) Migration to another CCP was not possible.** CME Securities Clearing was registered on **1 Dec 2025** (SEC order
34-104281) with "launch expected in Q2 2026"; its own SEC filings of **4 and 13 August 2026** (34-106037, 34-106131) state
*"CMESC currently does not have any Members or Users"* — no margin policy adopted until a 22 Jul 2026 filing, no fee
schedule filed, no launch press release; trade press puts go-live in Q3. ICE Clear Credit's Treasury registration was
granted **30 Jan 2026** (34-104762); its cash service was declared "operationally live" on 3 Feb 2026 — **repo is planned for
Q4 2026** — and **no Treasury-clearing volume figure is published anywhere** (ice.com, report centre, monthly statistics
workbook, 1Q/2Q26 earnings: CDS only). The SEC clearing-agency list (10 Feb 2026) shows FICC, CMESC and ICC as the three
Treasury CCAs; the only other 2024–26 Form CA-1s are Paxos (a CSD) and Cboe Clear US (binary options). No LCH, Eurex or
Euroclear application exists.

**(d) ISDA-Actrix US Treasury Repo Market Clearing Indicators** — a monthly series that began in June 2026, built from
OFR, DTCC, OFR MMF and NY Fed primary-dealer data (PDF at `data/vintages/isda_actrix/`). June 2026: **total cleared repo
ADV $6.5trn (+1.2% m/m)**; bilateral $4.5trn, triparty $2.0trn; **sponsored $2.5trn = 38.6%** (bilateral 1.7, triparty
0.8); direct $4.0trn. **YTD: sponsored −6%, direct −1%; y/y: sponsored +23%, direct +9%.** Our DTCC December→June
average is −6.3% — the two agree to the decimal. **The whole cleared market is flat year-to-date, not just the sponsored
pipe**, and it is a fifth larger than a year ago.

**Supporting:** TBAC Charge 1, May 2026, *Central Clearing Implementation* (`_research/primary_sources/treasury_clearing/`):
sponsored DVP+GC **$2.856trn on 30 Dec 2025, +150% in two years**; notes the CME and ICE approvals and end-user cross-
margining. DTCC, 27 Jul 2026: **>$1.2trn of Treasury cash cleared daily, $300–400bn still to move** before the cash
deadline; sponsored +771% since Sept 2022. NY Fed's Perli, 9 Jul 2026, *Repo Market Structure and Monetary Policy
Implementation*. **Mandate, as in force and unchanged (SEC implementation page, reviewed 10 Aug 2026; Uyeda, 7 Aug 2026):
cash 31 Dec 2026, repo 30 Jun 2027** — original dates 31 Dec 2025 / 30 Jun 2026 extended by the 25 Feb 2025 final rule
(34-102487); margin-separation relief to 30 Sep 2025 was a separate order (34-102486).

**For D8 and the nexus.** The repo leg of the conduit channel now has a measured middle (sponsored, daily), a measured
cleared total (Actrix, monthly; GSD gross, monthly since 2001 — §3), a measured hedge-fund end (Form PF) and MMF end (OFR),
and an official account of its first plateau. The growth was mandate-anticipation plus year-end regulatory optimisation;
the plateau is those incentives at rest. **What moves it next is dated: 31 Dec 2026 and 30 Jun 2027.** Calendar rows set.
D8's open work is now the *other* conduit — alternative ABCP funding equity leverage (FT harvest) — and the FR 2004 venue
split; the Treasury pipe is instrumented.

## 2. Scorecard for the return

| | Rows | Existence right | URL right | Details right | Changed what we know |
|---|---:|---:|---:|---:|---|
| **M1–M2** mandate, FICC access | 2 (+3 §5 items) | yes | **0/9** (SEC ×2, DTCC ×4, SIFMA, SEC, DTCC) | dates right; margin-relief mis-attributed; ACS "47% YoY" unsupported; ACS triparty "Jan 2026" is 22 Dec 2025 | no — but the verification surfaced the 2026 SEC exemption orders |
| **V1–V4** other CCPs, FICC totals | 4 | mostly | 2/8 | CME "scheduled Q2 2026" stale (not live, no members, Q3); ICE "revenue in investor disclosures" unsupported; "no continuous monthly GSD series" **wrong** — monthly since 2001 exists | **yes — the GSD monthly series; the CMESC filings** |
| **P1** official publications | 4 | 4/4 | 1/4 | every "data used" line constructed (4/4); two dates/slugs wrong | the real items are useful (below) |
| **P2** industry | 3 | 1/3 | 0/3 | Clarus and ISDA titles **constructed**; SIFMA fuses two real documents | **missed ISDA-Actrix entirely** |
| **P3** decline/plateau | 1 | negative holds | — | "structural explanation" is analysis the parcel forbade, and wrong on mechanism (not "unpublished" — not live) | — |

The no-template rule (R4) held for the CCP rows this time (CME, ICE, others differ), the dollar-sign and no-identifier rules
held. The self-audit again ticked "every EXISTS row has a URL I opened" over twelve dead URLs. Same shape as C-050/C-054/C-055.

## 3. What is now pullable that was not this morning

| Series | Publisher / route | Cadence | In the data layer |
|---|---|---|---|
| FICC sponsored repo / reverse repo / DVP / GC / total | DTCC `data/SponsoredVolume.csv` | daily, rolling 5y | `bin/pull_series.py --only dtcc` (since N3) |
| **FICC GSD total value compared; net obligations created** | DTCC chart `charts/previous-12-months-volume-for-gsd` (+ `?id=YYYY` archive); Cloudflare blocks curl — browser scrape | **monthly, 2001-01 → 2026-07** | `data/history/ficc_gsd_monthly_*.csv`; vintage rows; re-scrape by browser |
| **ISDA-Actrix clearing indicators** (total / direct / sponsored / bilateral / triparty cleared repo ADV) | isda.org, monthly PDF (+ interactive page) | monthly from Apr 2026 edition (Jun 2026) | June values as vintage rows; PDF archived |
| GCF repo index par value (Treasury, MBS) | DTCC `data/gcfindex.csv` | daily, 1y | archived `data/vintages/dtcc/` |
| Cleared share of Treasury repo (all / in-scope / by counterparty / G-SIB vs non) | OFR blog 20 Aug 2026, figures only | one-off (OFR collections) | numbers in §1 |
| DTCC hub tiles (sponsored members, ADV, GSD ADV) | `dtcc.com/ustclearing` | live | press-release figures in §1 |

Not pullable: any CME Securities Clearing volume (none exists); any ICE Treasury volume (none published); any Agent Clearing
Service series (DTCC publishes none; combined sponsored+ACS buy-side peak $3.1trn on 31 Dec 2025 in a 7 Jan 2026 press
release is the only ACS-inclusive figure).

## 4. Row-by-row — the short form

**M1.** Both SEC URLs dead; real home `sec.gov/rules-regulations/2025/02/s7-23-22` with 34-99149 (13 Dec 2023, 406pp) and
34-102487 (25 Feb 2025, effective 4 Mar 2025). Original dates 31 Mar 2025 (CCA rules) / 31 Dec 2025 (cash) / 30 Jun 2026
(repo) confirmed in the release; extended to 31 Dec 2026 / 30 Jun 2027. Margin-separation relief to 30 Sep 2025 is order
34-102486, not the final rule. No later date change; 2026 actions are exemption orders (captive-sub relief granted 18 Jun
2026, others). **M2.** All four DTCC URLs dead; real: `/clearing-and-settlement-services/ficc-gov/sponsored-membership`,
`…/agent-clearing-service`, hub `/ustclearing` (tiles: 2,850+ sponsored members, 65 jurisdictions, $2.4trn sponsored ADV,
$12trn GSD ADV, +28% y/y); cross-margining exists only as FAQ/deck PDFs off `/ustclearing/risk-management`. ACS triparty:
SEC order 34-104492 of **22 Dec 2025**, announced 7 Jan 2026. SIFMA *2026 Master Treasury Securities Clearing Agreement —
Done-Away* published **30 Jul 2026** (verified). "ACS +47% y/y July 2026" — in none of DTCC's releases; constructed.

**V1.** CME page is `/solutions/clearing/cme-securities-clearing.html` (future tense, subscribe-for-updates); Form CA-1
filed **13 Dec 2024** (notice 15 Jan 2025), registration **1 Dec 2025**; not live as of Aug 2026 (§1c). **V2.** ICE:
`ice.com/clear-credit` (banner "ICE launches U.S. Treasury clearing"; tables CDS-only); registration 30 Jan 2026; press
release 3 Feb 2026; repo Q4 2026; no volumes. **V3.** Both SEC URLs dead; the clearing-agency list and the CA-1 notices
page are the real records (§1c). **V4.** `/legal/policy-and-compliance` is the PQD archive (verified in N3); the GSD
monthly chart exists and was scraped; record-volume press releases 14 Apr 2025 (>$11trn), 2 Jul 2025 ($11.8trn; sponsored
$2.48trn on 30 Jun), 7 Jan 2026 ($13.2trn on 1 Dec 2025), 27 Jul 2026.

**P1.** Real, with corrections: Copeland & Kahn, *The Rise of Sponsored Service for Clearing Repo*, Liberty Street, 8 Oct
2025 — uses OFR cleared-repo data (not DTCC/MMF filings). **Monin, *Decomposing Hedge Funds' U.S. Treasury Exposures*,
FEDS Notes, 22 Jun 2026** — Form PF only: gross Treasury exposure $4.0trn (long 2.4 / short 1.6, Sept 2025), repo cash
borrowing $3.0trn, **basis trade ~$830bn (35%), swap-spread arbitrage ~$305bn** — a D10 datum. **Hempel, Kahn & Shephard,
*The $12 Trillion US Repo Market*, FEDS Notes, 11 Jul 2025** — FOCUS reports of 156 dealers 2014–24: gross US repo $11.9trn
in 2024, **~38% ($4.6trn) NCCBR**, dealers run matched books. TMPG white paper on NCCBR and indirect clearing: consultative
26 Feb 2025, **final 22 May 2025**, with updated Best Practices. Added by the verifiers: OFR blogs 22 Apr 2025 (clearing
rule and SOFR), 29 Jan 2026 (clearing impact), 19 Feb 2026 (client clearing); FEDS Note Kahn & McCormick, *Proportionate
margining for repo transactions*, 14 Feb 2025. **P2.** Clarus: nearest real *Record Q1 2026 CCP IM disclosures* (30 Jun
2026: DTCC GSD counterparty count +34% y/y to 1,445). SIFMA: *Done-Away Model Design Considerations* (with EY, 15 Dec 2025)
and the separate *US Treasury Central Clearing Pulse Survey* (10 Nov 2025). ISDA: no May 2026 paper; real items
derivatiViews 26 Jan 2026 and **ISDA-Actrix** (§1d). **P3.** Negative holds in ~8 searches; growth-framed items only
(Risk.net headlines on record MMF cleared repo, Jun–Aug 2026).
