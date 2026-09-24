# Parcel D8b — the conduit map: Grok's return adjudicated, and the census it unlocked

*24 August 2026. Return delivered by the principal at `_research/D8b_Conduit_Scouting_Return.md` (sha256
976f1147…, 3,627 words, 9 IDs, 10 sponsor sub-rows). **Verified the same morning by four fetch-and-report
agents** (saved pages under the session scratchpad; key documents archived below), and its sponsor→programme
map fed straight into a **full one-month N-MFP3 census** (325 of 325 filings, zero errors —
`bin/census_nmfp3.py`, results `data/vintages/nmfp3/`). Register: **C-058** (our own 23-Aug figure,
superseded). Rules applied: C-045, C-049–C-051, C-054–C-057.*

---

## 1. The adjudication: the first external return that substantially survives verification

**Scorecard.** Ten sponsor rows, four data rows, three press rows, one X row: **no constructed identifiers
found.** The Northcross roster is verbatim on the live site (all eight programmes, launch years, the
"short term securities financing agreements with highly rated major banks" line). Every bank mapping
checked out at a primary or archived source: JPM→Chariot/Falcon (Jupiter assigned into Falcon 23 Oct 2024,
per the PG&E exhibit), RBC→Thunder Bay (S&P profile via Wayback: sponsor Royal Bank of Canada, USD 25bn
limit), CA-CIB→LMA/Atlantic/La Fayette (own page), SG→Antalis (Fitch scorecard), BNP→Matchpoint+Starbird,
TD→Cabot Trail+GTA (Reliant Trust exiting, per the Corpay exhibit). The Mayer Brown decks carry exactly the
claimed taxonomy (bank vs aggregator, multi-seller vs CCP/repo; the **TRS-on-equity vehicle slide is in the
2024 deck only**) and exactly the claimed five aggregators: **Guggenheim, Nearwater, Mountcliff, Northcross,
Capitolis**. Grok's own CANNOT DETERMINEs were honest and mostly *resolvable in its favour*: Regatta **is**
Nearwater (S&P rating action: sole member Nearwater); the misspelled Generalfinance URL is the real URL.

**What verification added or corrected (not Grok errors — it had flagged these undetermined):**
- **Bennington Stark:** sponsor is **The Liberty Hampshire Company, LLC**; **Guggenheim Treasury Services is
  administrator** (Moody's, 14 Dec 2021: "Guggenheim's Bennington Stark…"). An S&P conduit profile of
  3 Oct 2023 exists (bot-blocked). GIOA/Moody's tracker (Sept 2020): Guggenheim Treasury administered
  **8 programmes, USD 36.0bn**; Northcross 3 / USD 11.6bn; **BSN Holdings 10 / USD 10.0bn** — all non-bank.
- **Chesham:** the 2 Mar 2022 Moody's action names **BSN as Investment Advisor** (originates and structures
  transactions), **BNY Mellon as administrator**; no sponsor wording. "BSN = sponsor" should not be written.
- **Ridgefield** (Guggenheim-administered) is typed **"Repo"** in the Moody's tracker — the only aggregator
  programme with an explicit repo type label in an opened document.
- Two weak spots: the 2008 Reuters factbox is dead (401, no archive) — unusable; the S&P *Resolute* new-issue
  URL has no independent index trace — treat as unconfirmed. S&P article bodies are bot-walled throughout, so
  the 2023 programme-name attributions rest on Grok's own read plus our independent corroboration per name.
- **E-section richer than claimed:** the CME family is **Adjusted Interest Rate (AIR) Total Return Futures**,
  six index sleeves (S&P 500 EFFR ASR/AST, S&P 500 SOFR ASPR/ASPT, Nasdaq-100 AQR/AQT, Russell 1000 ARR/ART,
  Russell 2000 A2R/A2T, DJIA ADR/ADT), quoted as a **TRF spread in basis points**, with **free daily files via
  CME DataMine** and a free QuikStrike term-structure tool. That is the equity-financing-cost series for the
  measurement handbook — the press shorthand "AXW" is not the CME code family. FINRA margin debit: Jul-26
  USD 1,417bn (their table; we snapshot it anyway). Crane Data (27 Jul 2026) paraphrases the JPM note; the
  analyst names come from the 13 Aug podcast and an unattributed FT Alphaville scrape — cite FT, not the scrape.

**Process note.** Five Gemini returns produced C-050/C-054/C-055/C-057. The first Grok return under the same
parcel design (R1–R8, with the no-template and no-identifier rules stated up front) produced zero register
entries against itself. One data point, not a law — the receipt procedure stays.

## 2. The census — corrected, and the correction of the correction

> **Read §2.0 first.** The figures published in this section this morning were wrong, and the register entry
> that produced them (**C-058**) has been **retracted**. What follows is the third and definitive pass.

### 2.0 What happened (C-059)

Three passes over the same 325 filings gave three answers. The **23-Aug** three-name figure ($9.4bn) had an
unrecorded method and looked least trustworthy. The **24-Aug morning** pass used a hand-written map of
programme names — and missed abbreviated spellings (`CHESHAM FIN` alongside `CHESHAM FINANCE`, worth $4.38bn
on that name alone) and every programme not already on the list; the list covered **41%** of MMF-held ABCP.
A second pass dropped the name filter but kept `investmentCategory == "Asset Backed Commercial Paper"` — and
missed the **$3.1bn** of the same programmes' paper that filers classify as *Non-Financial Company CP*.

The definitive pass imposes neither filter: **every position in every filing, 44,512 rows**
(`bin/census_nmfp3_all_positions.py`; data at `data/vintages/nmfp3/nmfp3_ALL_positions_2026-07-31…csv.gz`,
aggregated locally so a matching rule can be revised without re-fetching). At 31 July 2026:

| | 23 Aug claim | 24 Aug "correction" (C-058, retracted) | **Definitive** |
|---|---:|---:|---:|
| Chesham | $7.2bn | ~~$2.78bn~~ | **$7.159bn** |
| Bennington Stark | $1.5bn | $1.54bn | **$1.543bn** |
| Mountcliff | $0.7bn | $0.70bn | **$0.698bn** |
| **Three-name total** | **$9.4bn** | ~~$17.6bn aggregator~~ | **$9.400bn** |

**The 23-August figure was right to three decimal places. The correction was the error.** C-058 retracted;
method defect at C-059; the second-order lesson — *a correction is a claim and gets the same verification as
a finding* — is now a working rule in `CLAUDE.md`.

### 2.1 The market as it actually is: $101.2bn of ABCP in money funds, 139 issuers

Enumerating rather than matching changes the picture qualitatively. Money funds held **$101.2bn** of paper
categorised as ABCP at 31 July across **139 distinct issuers** — and the named-conduit universe below sums to
**$56.7bn**, three times what the press's five-sponsor framing implies. Sponsor and type were then established
per programme from **free sources only** (Moody's activity releases mirrored on Yahoo, Morningstar DBRS,
Fitch's public scorecard, sponsor sites, EDGAR credit-agreement exhibits), three Sonnet agents, ~$0 spent.
**The URLs behind every row are in `_research/D8b_D8c_conduit_sponsor_evidence_2026-08-24.md`**, together with
the dead ends not worth re-trying and the leads deliberately not promoted to conclusions:

| Programme family | $bn | Sponsor / adviser / administrator | Type |
|---|---:|---|---|
| **Chesham** | 7.16 | BSN Capital *investment adviser*; BNY Mellon administrator | securities-financing (PARTIAL) |
| **Verto Capital I** (A / C / D) | 5.57 | ADG Verto Capital Mgmt — Luxembourg FCP, compartments | CANNOT DETERMINE |
| **Ionic** (Funding LLC; Capital II/III Trust) | 5.21 | **Ionic Funding LLC is a wholly-owned subsidiary of Capitolis Inc.** (VERIFIED, from CLGM's own statements). *Capitolis Administrator LLC as Ionic's sponsor: NOT verified — no free source* | funds **Capitolis Liquid Global Markets**, whose book is **TRS referencing equity securities** + securities lending (VERIFIED) |
| **Northcross** (8 programmes) | 5.03 | Northcross Capital | securities-financing agreements (VERIFIED, own site) |
| **Concord Minutemen** (A/B/C) | 4.07 | **Liberty Hampshire** sponsor; **Guggenheim Treasury** administrator | multi-seller (VERIFIED) |
| Podium Funding Trust | 3.72 | Bank of Montreal (PARTIAL) | bank loan/guaranty conduit |
| **HQLA Funding** (Champlain, Huron, Tahoe) | 3.62 | **Capitolis Administrator LLC** — sponsor *and* administrator (VERIFIED, Fitch ×2); DBTCA trustee | **US Treasuries** via Dynamic Funding Markets repo / securities funding agreements |
| Paradelle Funding | 3.32 | Toronto-Dominion (PARTIAL) | bank conduit |
| **Nearwater** (incl. Columbia) | 3.29 | Nearwater Liquid Markets; DBTCA administrator | Treasuries via GMSLA + TRS (VERIFIED) |
| **Overwatch** Alpha / Bravo | 2.70 | unmapped | same fully-supported securities-financing template (PARTIAL) |
| **Ridgefield** + Guggenheim names | 2.29 | Guggenheim Treasury administrator | Ridgefield typed **"Repo"** in Moody's tracker |
| **Washington Morgan** | 1.98 | CANNOT DETERMINE *(Chicago address shared with Guggenheim — lead only)* | CANNOT DETERMINE |
| Lexington Parker | 1.76 | Liberty Hampshire; Guggenheim Treasury | multi-seller (VERIFIED) |
| Britannia | 1.72 | Nearwater (UNVERIFIED — S&P gated) | securities-backed/repo (UNVERIFIED) |
| Bennington Stark | 1.54 | Liberty Hampshire; Guggenheim Treasury | multi-seller (VERIFIED) |
| Intrepid | 1.37 | CANNOT DETERMINE | CANNOT DETERMINE |
| Mackinac | 0.87 | CANNOT DETERMINE | GMSLA / BNPP (UNVERIFIED) |
| Alinghi | 0.81 | Nearwater (UNVERIFIED) | MSLA (UNVERIFIED) |
| Mountcliff | 0.70 | 20 Gates Management | fully supported multi-seller (VERIFIED, DBRS) |
| **Total, named families** | **56.72** | *(24 Aug pm, after D8c)* non-bank-sponsored **$36.4bn** incl. Capitolis **$8.83bn**; **still unattributed $13.3bn** (Verto 5.57, Overwatch 2.70, Washington Morgan 1.98, Intrepid 1.37, Mackinac 0.87, Alinghi 0.81); bank-sponsored **$7.0bn** | |

*Bank multi-sellers make up most of the remaining ~$45bn of the $101.2bn: Victory and Gotham (MUFG), Liberty
Street (Scotiabank), Sheffield (Barclays), Ranger (BofA), Versailles (Natixis, CDS-linked hybrid), Atlantic /
LMA Americas (Crédit Agricole), Antalis / Barton (SocGen), Chariot / Falcon (JPM), Cabot Trail (TD), Starbird
(BNP), Thunder Bay / Old Line / Bedford Row (RBC), plus JPMorgan's Collateralized Commercial Paper V and
Barclays' own US Collateralized CP Notes — the latter classified by the SEC as Financial Company CP, not ABCP.*

### 2.1b Two months, like for like — the MMF-held conduit stock FELL in July

*Both months re-run with the definitive method after C-059 (the June figures first published on 24 Aug were
name-map derived and have been withdrawn from `data/series.tsv`). Identical groupings, all categories:*

| $bn | 30 Jun 2026 | 31 Jul 2026 | change |
|---|---:|---:|---:|
| **All ABCP-categorised holdings** | 104.47 | 101.22 | **−3.1%** |
| **The eight named families** | 52.98 | 49.69 | **−6.2%** |
| — Capitolis (Ionic + HQLA) | 10.51 | 8.83 | **−16.0%** |
| — Northcross | 7.26 | 5.03 | **−30.7%** |
| — Nearwater | 4.55 | 3.29 | −27.8% |
| — Chesham | 6.31 | 7.16 | **+13.5%** |
| — Liberty Hampshire / Guggenheim | 7.10 | 7.36 | +3.7% |
| — Guggenheim-administered (Ridgefield etc.) | 2.06 | 2.29 | +11.4% |
| — 20 Gates (Mountcliff) | 0.70 | 0.70 | 0.0% |
| — still unattributed | 14.50 | 15.03 | +3.7% |

**The divergence is the point.** Total ABCP *outstanding* rose over this period (Fed CP release: $421bn at
31 Dec 2025 → $488bn at 19 Aug 2026), while **money funds' holdings of it fell 3.1% in the month, and their
holdings of the securities-backed families fell 6.2%**. Whatever is funding the conduits' growth in 2026, at
the margin it is **not** money-market funds — the marginal buyer is some other cash investor, or the paper is
being placed elsewhere. Two observations do not make a trend; the September census (calendar) is the test.
Note also that the two biggest fallers are the two Treasury-repo shops (Northcross, Nearwater) while
**Chesham rose 13.5%** — composition is moving inside the aggregate, not just the level.

### 2.2 Capitolis is the mechanism the FT described — and it is the largest non-bank sponsor here

*Established by the D8c parcel (Grok) and verified independently the same day: two Fitch rating actions read
in full, and Capitolis's own SEC-broker-dealer financial statements. Roles are stated as the documents state
them, which is not how the press states them.*

**Capitolis stands behind both legs.** *"Capitolis Administrator LLC (Capitolis) is the program's sponsor and
administrator"* — Fitch, on **HQLA Funding**, in both the Champlain/Tahoe action (27 Sep 2024) and the Huron
action (2 Dec 2024). HQLA funds **US Treasuries**: Dynamic Funding Markets, as repo buyer, *"will purchase
issuance-specific baskets of DFIS in the form of U.S. treasuries"*, with Deutsche Bank Trust Company Americas
as issuer trustee. Separately, **Ionic Funding LLC is a wholly-owned subsidiary of Capitolis Inc.** and lends
into **Capitolis Liquid Global Markets (CLGM)**, whose business is *"total return swaps ('TRS') referencing
equity securities"* plus securities lending. **Money funds held $8.83bn of the two together at 31 July 2026
(Ionic $5.21bn, HQLA $3.62bn) — more than Chesham's $7.16bn, making Capitolis the largest non-bank ABCP
sponsor in US money-fund portfolios, and the only one running Treasuries and equities through one shop.**

**And the equity book itself is measurable, semi-annually, for free.** CLGM is an SEC-registered dealer and
publishes a *Statement of Financial Condition* every 31 January and 31 July at `capitolis.com/regulatory-disclosures`
(all five archived at `data/vintages/capitolis/`; series in `data/series.tsv`):

| $bn | 31 Jan 2024 | 31 Jul 2024 | 31 Jan 2025 | 31 Jul 2025 | **31 Jan 2026** | 2yr |
|---|---:|---:|---:|---:|---:|---:|
| CLGM total assets | 4.97 | 8.80 | 10.31 | 13.09 | **19.70** | **×4.0** |
| — funded by affiliate revolving loans | 4.88 | 8.51 | 9.79 | 12.31 | **18.09** | **×3.7** |

The January 2026 note names the lenders: *"IFLLC and HQLA provide funding through revolving loan advances in
support of the Company's trading activities."* **So the ABCP proceeds of both conduits fund one equity-TRS and
securities-lending book, and that book quadrupled in two years.** Against it, money funds hold $8.83bn of the
paper — roughly half the $18.1bn of affiliate funding, the remainder coming from cash investors outside the
money-fund complex.

**Why this matters for D8 and the nexus.** The August FT piece described prime brokers moving client equity
margin off balance sheet into conduits funded by money funds. This is that chain with names, roles and a
time series attached: **money fund → Ionic/HQLA commercial paper → revolving loan → CLGM → total-return swaps
on equities**, with no dealer balance sheet intermediating. It is private money creation against equity
collateral, and it is measurable at three points — the money-fund end (monthly, N-MFP3), the vehicle
(semi-annual, CLGM statements), and the market aggregate (weekly, Fed CP). **Flagged as the strongest single
instance of the D8 channel; not folded.**

**Kept honest.** Capitolis's own website names only CLGM — it publishes nothing about HQLA, Ionic or Capitolis
Administrator LLC, so the linkage rests on Fitch and on CLGM's statements, not on the sponsor's own account.
The specific claim that *Capitolis Administrator LLC* sponsors **Ionic** (as distinct from HQLA) is **not
verified** in any free source; what is verified is the Capitolis Inc. ownership. And **$13.3bn across Verto,
Overwatch, Washington Morgan, Intrepid, Mackinac and Alinghi still has no sponsor obtainable free** — for
Overwatch, Drexel Hamilton is confirmed as sponsor of an entity called *"Overwatch Funding Company"*, which is
not documentary evidence about *Overwatch Alpha Funding LLC* or *Overwatch Bravo Funding LLC*, and the two
were not merged.

## 3. What this changes in the record

- **C-058** — our own 23 Aug figure ("USD 9.4bn held by funds naming them: Chesham 7.2 / Bennington 1.5 /
  Mountcliff 0.7") is **superseded and unreproducible**: the single-month census puts Chesham at USD 2.8bn
  at 31 Jul; the old pass mixed July and August filings (June and July month-ends) with an unrecorded method
  (its script was lost to the scratchpad sweep before being archived). The FT-harvest doc carries the
  correction banner; the June-data census run now in progress will show whether June's Chesham stock
  explains part of the gap.
- **D8's ABCP half is measured at the MMF end** with a verified name map and a repeatable census; combined
  with the Treasury-repo pipe (D8/D10), both conduits now have instrumented ends. What remains for the
  channel's *total* size: the S&P *Inside Global ABCP* sponsor tables (gated; landings archived) or a paid
  DTCC feed. Flagged, not folded.
- **Measurement handbook additions:** CME AIR TRF spread (free DataMine daily files; the financing-cost
  series); FINRA margin debit (already vintaged); `bin/census_nmfp3.py` monthly.
- **Corrections to speech, not just documents:** say "BSN, investment adviser to Chesham"; "Guggenheim
  Treasury, administrator of Ridgefield and Bennington Stark (sponsor Liberty Hampshire)"; "Mountcliff,
  a 20 Gates programme". The press's "sponsors" flattens roles that the rating actions distinguish.
