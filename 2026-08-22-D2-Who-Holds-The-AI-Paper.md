# D2 — Who holds the AI paper? Money-like claims or long money

*22 August 2026. **Version 1 — every figure pulled by us from the issuing source on 22 Aug 2026**:
Federal Reserve Z.1 (table M3s_Q, 2026Q1 vintage 11 Jun 2026), SEC EDGAR full-text search over
Forms N-MFP3 and NPORT-P with the XML filings parsed directly, SEC XBRL company-facts API, and
one Chicago Fed publication fetched and read. Press-sourced facts are marked as such. Serves
**A12** — and it is the legitimate re-entry of A11's subject matter through A12's frame.*

---

## 0. The question, and why the answer decides which kind of risk this is

Under the nexus, the question about hyperscaler bonds, data-centre SPV notes, project loans and
neocloud debt is not *how much* but **who funds it and with what liability**. If it is held
against **money-like claims** — MMF shares, repo, uninsured deposits — it carries **run risk** and
belongs to the shadow-money story. If it is held by **long money** — insurers, pensions, bond
funds, foreign investors — it carries **duration and credit risk** and does not.

Nobody had asked. Four layers, each measured.

## 1. Result in one paragraph

**The AI debt stack is long-money funded at the security level.** Money-market funds hold
**$22bn of the $17.2trn** US corporate-and-foreign-bond stock (0.13%), and a filing-by-filing
census of every MMF that names an AI issuer finds **$0.26bn of direct commercial paper and
~$4.0bn as repo collateral** — against $8.4trn of MMF assets. The bond stock is held by the
rest of the world ($4.9trn), life insurers ($3.9trn), mutual funds ($2.6trn), pensions ($1.6trn),
ETFs and other funds (~$1.6trn), P&C insurers ($0.9trn), banks ($0.8trn). At the deal level the
largest off-balance-sheet financing — Meta's $27bn Beignet/Hyperion bonds — shows up in **1,497
registered-fund filings but only ~$0.7bn inside PIMCO's 108 registered funds**, so its reported
$18bn anchor sits overwhelmingly in separate accounts for insurers and pensions. **The one place
the original "money creation" intuition is literally true is bank lending**: large-bank
AI-adjacent C&I exposure of **~$450bn committed, ~$150bn outstanding** (late 2025) **[C-115: industry exposure; ~$250bn of those commitments already existed in 2015]**, plus the
$38bn Oracle/Vantage loan package — deposit creation at origination — against ~$1.2trn of
AI-company-issued debt. **And the issuers are themselves the cash pools**: the six largest AI
capex firms held ~**$630bn** of cash and short-term investments at mid-2026, up ~$240bn in two
years — Pozsar's category-2 institutional cash pools, on the other leg of the nexus.

## 2. Layer 1 — the money-like leg, measured

**2.1 Z.1 holder split, corporate and foreign bonds, 2026Q1 ($bn).** Source: Fed Z.1 CSV bundle,
table `M3s_Q`, series `FL..3063005.Q`, pulled 22 Aug.

| Holder | $bn | Share |
|---|---:|---:|
| **Total outstanding** (FL89) | **17,168** | 100% |
| Rest of the world (FL26) | 4,909 | 28.6% |
| Life insurers (FL54) | 3,928 | 22.9% |
| Mutual funds (FL65) | 2,581 | 15.0% |
| Pension funds, total (FL59) | 1,613 | 9.4% |
| ETFs, closed-end funds, ABS issuers, GSEs and other financial (residual of FL79) | ~1,641 | ~9.6% |
| P&C insurers (FL51) | 885 | 5.2% |
| US-chartered depository institutions (FL76) | 757 | 4.4% |
| Domestic nonfinancial sectors (FL38: households 193, state & local 317, other) | 534 | 3.1% |
| Foreign banking offices in US (FL75) | 139 | 0.8% |
| Funding corporations (FL50) | 89 | 0.5% |
| Broker-dealers (FL66) | 70 | 0.4% |
| **Money market funds (FL63)** | **22** | **0.13%** |

*MMFs cannot hold paper over 397 days, so this is by construction. The nexus question for MMFs
is therefore CP and repo collateral, not bonds.*

**2.2 N-MFP3 census, July 2026.** Method: SEC EDGAR full-text search (`efts`) for each issuer
name over Forms **N-MFP3** filed 1 Jul–22 Aug 2026 (559 filings in the window name "Treasury" —
the form is N-MFP3 now, not N-MFP2); every matching filing's `primary_doc.xml` parsed; holdings
split into **direct** (issuer name on the security) and **as-collateral** (issuer name on
`nameOfCollateralIssuer` inside a repo line); latest period per fund.

| Issuer | Direct holdings | As repo collateral | Lines |
|---|---:|---:|---|
| Amazon | $0.100bn (nonfinancial CP) | $0.836bn | 1 / 53 |
| Apple | $0.154bn (nonfinancial CP) | $0.665bn | 2 / 46 |
| Alphabet | — | $0.606bn | 0 / 37 |
| Meta | — | $0.575bn | 0 / 42 |
| Oracle | — | $0.490bn | 0 / 63 |
| NVIDIA | — | $0.298bn | 0 / 33 |
| Microsoft | $0.004bn | $0.226bn | 1 / 35 |
| Data-centre ABS names (Vantage, Aligned, Switch, CyrusOne, DataBank, Compass, Stack, DLR, EQIX) | — | $0.200bn | 0 / 40 |
| **CoreWeave** | — | **$0.091bn** | 0 / 15 |
| **Total** | **≈$0.26bn** | **≈$3.99bn** | |

MMF "repo backed by other assets" totalled **$169bn** in July 2026 (OFR), so the AI complex is
~2.4% of MMF private-collateral repo and ~0.05% of MMF assets. **The mechanism is real and
named** — e.g. *"COREWEAVE INC SR CV 144A NT 32"*, the 1.75% convertible due 2032, pledged as
collateral inside a BlackRock Master Trust money fund's repo with a dealer — and it is **de
minimis in size**. Cash-pool money lends overnight to dealers against AI paper; it does not hold
the paper.

## 3. Layer 2 — bank credit: where the intuition is literally true

> **[C-115, 23 Sep] Source now pinned and archived:** https://www.chicagofed.org/publications/chicago-fed-insights/2026/ai-tail-risk-for-banks
> (Chicago Fed Insights, **February 2026**, Cohen/Killen/Lau) — copy at `data/vintages/chicagofed_ai_tail_risk_2026-02/`. This section
> cited it with no URL. Re-reading it adds what this section omitted: the same concentration stood at **~9% of commitments,
> ~$250bn, in 2015** — so the $450bn/$150bn is industry exposure, not build-out lending — and the $1.2trn is **JPMorgan analysts'
> estimate**, relayed.

- **Chicago Fed Insights (2026), Wholesale Credit Risk Center** — fetched and read, 22 Aug:
  large-bank **AI-adjacent C&I commitments ~$450bn, ~$150bn outstanding, late 2025**; "AI-adjacent"
  = C&I and CRE loans to AI software and infrastructure companies, data-centre construction, and
  loans secured by data centres. JPMorgan analysts' estimate of **AI-company-issued debt ~$1.2trn**
  — "over double the large bank C&I commitments and eight times the outstanding balance." MSCI RCA:
  **$14.9bn** of bank lending for data centres in the year to 2025Q3. Average bank outstanding
  exposure ~**0.8% of total assets**; delinquency in line with the portfolio; tail risk flagged.
- **Oracle/Vantage, $38bn** — *press-sourced (Bloomberg via DCD, Sherwood, Investing.com)*:
  $23.25bn Texas + $14.75bn Wisconsin, four-year loans ~250bp over benchmark, led by JPMorgan and
  MUFG with Wells Fargo, BNP, Goldman, SMBC, SocGen; Bloomberg, Apr 2026: distribution "takes
  months to spread across the market." **For those months it is bank balance sheet, i.e. deposits
  created against data-centre loans.** That is the textbook sense of money creation, and it is
  the only place in the AI stack where it applies without qualification.

**Size it honestly:** ~$150bn outstanding against ~$1.2trn of AI-company debt and ~$400bn+/yr of
capex. Material, growing, and a minority channel.

## 4. Layer 3 — long money at the deal level: Beignet / Hyperion as the test case

> ⚠ **AMENDED 23 Aug 2026 (C-053) — the holder figures in this section were a sampling artefact.
> The full SEC bulk N-PORT census gives registered funds $9.81bn (36% of the deal), PIMCO Funds
> alone $6.23bn. See §9. The text below is preserved as written.**

- **Structure** — *Meta press release (primary) and trade press*: $27bn A+ rated, fully
  amortising notes due 2049, 6.58%, issued by **Beignet Investor LLC**; $2.5bn equity; Blue Owl
  funds 80% / Meta 20% of the JV; Morgan Stanley sole bookrunner; private placement. **PIMCO $18bn,
  BlackRock $3bn** anchors — *Bloomberg-sourced, secondary.*
- **What the filings show (primary, 22 Aug):** EDGAR full-text search finds **1,497 Form NPORT-P
  filings** (1 Apr–22 Aug 2026) naming Beignet — AB, Invesco, American Century, Aristotle, Apollo,
  Barings and hundreds more. Parsing **all 108 PIMCO registered-fund filings** (period 31 Mar
  2026): **$0.70bn** of Beignet 6.581% 2049 144A, CUSIP **076912AA2**, largest single position
  $73m at 3.8% of NAV (PIMCO Managed Accounts Trust). A 45-filing sample of non-PIMCO funds holds
  $0.08bn.
- **Reading:** if PIMCO's order was ~$18bn and its registered funds hold $0.7bn, **~96% of the
  PIMCO allocation sits in separately managed accounts and private vehicles** — insurance general
  accounts and pensions — not in daily-redeemable mutual funds. Extrapolating the sample, registered
  funds in total hold perhaps $2–4bn of the $27bn. **The Hyperion paper is long-money funded**, and
  the daily-redeemable slice is a minority.

*Caveat: NPORT-P is filed quarterly with a lag, so the latest public period is 31 Mar 2026; the
1,497 count includes funds holding tiny positions via index replication; "Hyperion" (477 hits) is
too generic a string to use.*

## 5. Layer 4 — the issuers as cash pools: the nexus inside the capex cycle

SEC XBRL company-facts, latest 10-Q/10-K instants, $bn:

| Firm | Cash & equivalents | Marketable securities (current) | Total liquid | Two years earlier |
|---|---:|---:|---:|---:|
| Alphabet (30 Jun 2026) | 55.9 | 186.6 | **242.5** | 100.7 |
| Amazon (30 Jun 2026) | 78.2 | 44.8 | **123.0** | 89.1 |
| Meta (30 Jun 2026) | 15.5 | 74.8 | **90.3** | 58.0 |
| Microsoft (30 Jun 2026) | 20.9 | 55.9 | **76.8** | 75.5 |
| NVIDIA (Apr/Oct 2026 mix) | 13.2 | 49.1 | **~62** | ~18 |
| Oracle (31 May 2026) | 31.3 | 0.6 | **31.9** | 10.7 |
| **Six-firm total** | | | **~$627bn** | **~$352bn** |

*(Apple, not an AI capex firm, holds a further ~$146bn.)* **These are Pozsar's category-2
institutional cash pools** — global corporate cash, managed for safety, parked in Treasuries,
agencies, CP, deposits and MMF shares. **The firms issuing the long bonds that insurers buy are
simultaneously the largest demanders of the short safe assets** the bill surge supplies. The same
entities on both legs of the nexus — which is the Pozsar–Singh definition of it.

## 6. Verdict

1. **Par-on-demand shadow money does not fund the AI paper.** ~$0.3bn direct, ~$4bn as repo
   collateral. The run-risk channel through MMFs is, on current evidence, not there.
2. **Bank credit is the one literal money-creation channel**, sized at ~$150bn outstanding /
   ~$450bn committed for large banks **[C-115: industry exposure; ~$250bn pre-dates the build-out]**, plus project packages like Oracle/Vantage's $38bn in their
   pre-distribution months. Real, growing, minority.
3. **The bond and SPV stock is long-money funded** — insurers, pensions, ROW, bond funds — and
   the daily-redeemable share of even the marquee SPV deal is a minority.
4. **Therefore the fragility, if it exists, is duration and operating leverage, not a banking
   run.** This is the same conclusion the 22 Aug essay framing reached from the filings side,
   now reached independently from the holder side. Two routes, one answer.
5. **And the most nexus-shaped fact is the inversion:** the capex firms are the cash pools.
   ~$630bn of their money-demand sits on the demand side of the bill market while their bonds sit
   in insurers' Schedule D.

## 7. What v1 does not do

| Gap | Status |
|---|---|
| Full N-PORT census for Beignet, Vantage, CoreWeave (all 1,497 / 1,114 / 3,285 filings) | Sample only; the method is proven and runs in the background. Would turn "$2–4bn" into a number |
| Insurer holdings at issuer level | NAIC Schedule D is not public in aggregate; NAIC Capital Markets Bureau special reports not yet checked |
| Private credit (Blue Owl, Blackstone/Magnetar DDTLs) and *their* funding base | Not traced; Form PF aggregates do not identify issuers |
| ROW holders ($4.9trn of corporate bonds) — how much AI paper | TIC does not give issuer detail |
| Hyperscaler cash composition — do they hold each other's bonds? | 10-K marketable-securities notes; not read. Flagged D9 |
| Name-matching | Subsidiaries and SPVs may escape the issuer strings used; the census is a floor |

## 8. Flagged, not folded (N5)

- **D9. The circuit closes on itself?** Alphabet's $187bn of marketable securities and Amazon's
  $45bn include corporate bonds. If the AI complex's cash pools hold the AI complex's bonds, the
  "who funds whom" question has a reflexive answer. Read the 10-K notes.
- **D2 full census** as a background job; **D8** (sponsored repo) and **D3** (cash-pool growth vs
  AUM) unchanged in rank.
- **Method worth keeping:** `efts` full-text search → filing list → XML parse gives an issuer-
  level holder census for MMFs (N-MFP3) and registered funds (NPORT-P) in under an hour. Nothing
  external required.


---

## 9. Amendment, 23 Aug 2026 — the full N-PORT census (C-053)

The SEC publishes a structured bulk N-PORT dataset each quarter. The 2026Q2 file (filings submitted
Apr–Jun 2026, periods ending ~31 Mar 2026; `FUND_REPORTED_HOLDING.tsv`, 5,347,869 rows) had been
downloaded on 21 Aug and was found during housekeeping. Scanned in full:

| Name (debt only for listed issuers) | Value held by registered funds | Filings | Registrants |
|---|---:|---:|---:|
| **Beignet Investor LLC** 6.581% 2049, CUSIP 076912AA2 | **$9.81bn** | 324 | 146 |
| CoreWeave (bonds, converts, loans) | $2.87bn | 506 | — |
| Vantage Data Centers (ABS, loans) | $1.09bn | 227 | — |
| Aligned Data Centers (loans, ABS) | $1.06bn | 123 | — |
| TeraWulf (debt) | $0.48bn | 100 | — |
| Hut 8 (debt) | $0.23bn | 66 | — |
| Cipher Mining (debt) | $0.005bn | 2 | — |

**Beignet by registrant:** PIMCO Funds $6,232m (one series $4,227m at 1.88% of NAV), BlackRock
Funds V $718m, Bridge Builder Trust $295m, Prudential Investment Portfolios 17 $258m, PIMCO ETF
Trust $177m, Advanced Series Trust $140m, Loomis Sayles Funds II $138m, Fidelity Rutland Square II
$116m, PIMCO VIT $104m, PIMCO Managed Accounts $87m … **PIMCO registered ≈ $6.6bn ≈ one-third of
its reported $18bn; BlackRock registered ≈ $0.86bn of its reported $3bn.**

**What changes.** The §4 claim that ~96% of PIMCO's allocation sits in separate accounts is
**dead**: the registered, daily-redeemable share of the Hyperion debt is **about one-third** — a
material minority, not "small." The verdict in §6 survives on the other ~64% (insurers' separate
accounts, pensions, private vehicles), and the run-risk frame still does not fit a 2049 amortising
A+ note held at 1–2% of NAV across 146 complexes — but the characterisation was wrong and is
corrected here, in RESEARCH_STATE S-D2, and in the 23 Aug briefing.

**Method note, binding:** EDGAR full-text search paginated to 400 of 1,497 hits missed the
filings that held 60% of the value. **A search sample is not a census; the bulk dataset is.** It is
free, quarterly, and ~440MB. The 15 Sep calendar row becomes: re-run on the 2026Q3 bulk file when
SEC posts it (~early Oct).
