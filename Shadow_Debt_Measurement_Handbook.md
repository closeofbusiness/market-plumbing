# The Measurement Handbook

How to derive the numbers on shadow credit creation: what can be built, in what order,
and what cannot be built at all. Nine channels mapped independently, three infrastructure
reviews, one synthesis. *Vintage: 21 August 2026.*

---

# THE MEASUREMENT HANDBOOK
## How to derive the numbers on shadow credit creation — what can be built, in what order, and what cannot be built at all

**Vintage of this document: 21 August 2026.** Figures carry the vintage of their source. Five quantities in §1 and §3 I re-derived myself in this session from primary files rather than taking them from the channel notes; those are flagged **[verified here]** with the arithmetic shown in §6.

---

## §0. THE RULE THAT GENERATES THE DASHBOARD

There is one rule and everything else follows from it.

> **Measure credit once, at the obligor's liability side. Measure money once, at the holder's asset side. Never add the two, and never add a wrapper to the thing it wraps.**

Applied to your nine channels this partitions cleanly, and the partition is the deliverable:

| What the channel does | Channels | Where it is measured |
|---|---|---|
| **Creates bank money** (loan → deposit) | subscription/NAV/portfolio lines; warehouse lines; broker-dealer bank borrowing; SBL at banks; offshore eurodollar lending | Bank asset side. Deposit counterpart already inside M2 — the *credit* is misattributed, not the money |
| **Creates near-money** (converts a non-spendable safe asset into a spendable one) | fiat-backed stablecoins (outright-bill leg only); FABN/FABCP/FABR; institutional MMF shares | Holder asset side, outside M2 |
| **Creates credit without money** | direct lending funded by drawn LP capital; ABS/CLO true sale; borrower LBO leverage | Obligor liability side |
| **Creates capacity, not claims** | SRT (manufactures regulatory capital); collateral reuse (relaxes the collateral constraint); rated-note feeders and annuities (extend willingness to hold illiquid claims) | Ratios and bp of CET1 — never dollars in a credit column |
| **Economises on money** | inter-firm trade credit; reverse factoring | Velocity, not stock |

A single "total shadow money" number requires summing across all five rows. It cannot be done. §2.1 of the critique traces one $100m unitranche loan through eleven statistical systems; nine of them are legitimate measurements of different balance sheets, and the naive sum is 8–10× the loan.

**One headline number is defensible, on one basis, and it is not a shadow-money total.** See §1.8.

---

## §1. THE DASHBOARD

Seven panels. Each panel is internally additive; **no two panels may be added.** For each series: what it measures, unit, frequency, and — the part everyone omits — what it excludes.

### PANEL A — Near-money held outside the banking perimeter *(the Pozsar object)*

| Series | Measures | Unit | Freq | Latest | Excludes |
|---|---|---|---|---|---|
| **Fed FSR Table 4.1, "Runnable money-like liabilities"** | Pay-on-demand uninsured private claims: MMFs 7,746 + uninsured deposits 7,608 + repo 5,887 + CP 1,368 + sec-lending cash collateral 1,201 + "other" 3,223 | $bn stock | Semiannual, 4–5 mo lag | **$27,033bn, 2025:Q4; +12.0% y/y vs +5.4% 2003–25 average; 86% of GDP** | LGIPs, total return swaps, private liquidity funds, tender option bonds, bankers' acceptances, puttable long bonds other than VRDOs. **Bond mutual funds ($5,032bn) are a memo, not in the total.** |
| **Institutional MMF shares outside M2** | Par-on-demand claims held by money-holding sectors and definitionally excluded from M2 (only *retail* MMF is in M2) | $bn stock | Weekly/monthly | ≈**$5.26trn**, up ≈94% since 2019:Q4 vs M2 +50.8% | Derived by subtraction from two incompatible bases — see build note in §2 item 4. Use the OFR MMF Monitor split, not Z.1-minus-H.6 |
| **BoJ "Broadly-defined liquidity (L)" vs M3** | The only official aggregate anywhere broader than M3 | ¥trn stock | Monthly, ~6 wk lag | L ¥2,338.4trn (+4.4% y/y) vs M3 ¥1,641.2trn (+1.4%). **L−M3 = ¥697.2trn, 70% of it pecuniary trusts** | Money-holders are NFCs, households and local government **only** — financial institutions, central government and non-residents excluded. **Repo was deliberately removed in the 2008 revision.** BoJ states L "relies more on estimations" than M1–M3 |

**Three warnings on Panel A.** (1) The runnables series is **internally basis-mixed** — the Fed sums Call Report uninsured deposits, Z.1 repo, ICI/SEC MMF assets, RMA securities lending, Bloomberg VRDOs, staff-estimated FABS and DeFiLlama stablecoins. It violates the rule in §0. Quote it as *the Fed's number*, never as yours. (2) **You cannot rebuild it** — four of the seven inputs are paid. (3) It is **definitionally non-stationary**: VRDOs entered in 2019:Q1, stablecoins entered recently, and history was restated. Do not compare a 2026-vintage level to a pre-2019 published level; the 2015 FEDS Note chart sat near 60% of GDP where the 2026 report reads 86% and calls it mid-range.

### PANEL B — Bank money creation into the non-bank chain *(the only genuinely additive money-creation sleeve)*

| Series | Measures | Unit | Freq | Latest | Excludes |
|---|---|---|---|---|---|
| **H.8 line 26, loans to NDFIs**, five panels | Drawn bank loan principal to non-depository financial institutions | $bn stock, SA | **Weekly**, 9-day lag | **[verified here]** All commercial banks **$2,016.1bn (w/e 5 Aug 2026)**; domestically chartered $1,493.8bn; foreign-related institutions $522.1bn (NSA) | Thrifts; **all lending by non-US banks from non-US offices**; undrawn commitments. Not decomposable — bundles mortgage warehouses, PE subscription lines, hedge fund financing, insurers, GSEs, securitisation vehicles and banks' own trust departments |
| **Call Report RC-C Pt I item 9.a and M.10.a–e** + **RC-L 1.e.(3)(a)–(e)** | Drawn *and* undrawn, split five ways | $bn stock | Quarterly, ~45 d | Q3 2025, banks >$10bn: 10.a $315.8 / 10.b $317.3 / **10.c $308.9** / 10.d $105.0 / 10.e $241.4; undrawn to all NDFIs **$987bn = 42.9% of commitments** | Banks <$10bn do not file the memoranda. **The mapping trap: private credit funds and BDCs are in 10.b, not 10.c. 10.c is capital-call lines to funds >50% equity — PE and VC.** 10.e's instruction list names private debt funds too, so 10.b/10.e allocation is filer discretion |
| **Z.1 FL663168005** broker-dealer borrowing from depositories | The deposit-creating funding leg of the margin/PB book | $m stock | Quarterly, ~10 wk | **$589,456m at 2026:Q1**, from $404,207m a year earlier (+45.8%) | Not additive to margin receivables — it *funds* them |
| **Z.1 FL613168005** finance-company borrowing from depositories | Best free proxy for **drawn** warehouse capacity | $m stock | Quarterly | $289.8bn at 2026:Q1 vs $235.3bn end-2023 | PPPLF is still inside the definition. Finance-company sector ≠ the non-bank mortgage originator universe |

**Panel B is the answer to "how does the money get created."** Each of these is a bank writing a loan asset and a deposit liability. The deposit is inside M2 already. **What is invisible is not the money — it is that the counterpart asset is a claim on a financial intermediary rather than on a household or a firm.**

**The utilisation discipline:** utilisation on facilities to private credit vehicles has run 50–65% (OFR, Y-14). Undrawn is *contingent* creation. Quoting a committed figure beside a drawn figure from a different source is a factor-of-two error and it is the single most common one in circulation — five published estimates of the same US bank-to-private-credit exposure span $54bn to $650bn, and the spread is definitional, not measurement error.

### PANEL C — Offshore dollar creation *(the ZIRP analogue, and the strongest single finding in the map)*

| Series | Measures | Unit | Freq | Latest | Excludes |
|---|---|---|---|---|---|
| **BIS LBS, break-and-FX-adjusted flow**, `Q.F.C.A.USD.F.5J.A.5A.A.5J.N` | New offshore dollar credit extended by banks located outside the US | $bn flow | Quarterly, ~4 mo | **+$1.90trn over the four quarters to 2026:Q1; +11.9% y/y**, fastest since March 2020 and, before that, pre-GFC | No counterparty sector and no counterparty country in the foreign-currency residence cut. **Singapore, Indonesia, Saudi Arabia, Malaysia return NaN under confidentiality.** Chinese banks structurally understated |
| Companion stocks (same grammar, `L_MEASURE=S`) | Cross-border USD claims $17.86trn / liabilities $14.11trn of banks outside the US | $trn stock | Quarterly | 2026:Q1 | **Never difference the stocks** — they carry `OBS_STATUS='B'` break flags in most years and are unadjusted for dollar-index moves |

This is the one channel that unambiguously creates money, at scale, and appears in **no monetary aggregate anywhere in the world** — not US M2 (excluded by definition), not euro-area M3 (euro-denominated, resident-based), not Japanese M3. It is also the mechanism that actually transmitted Japanese ZIRP into asset prices. If the operator wants his 2013–16 pattern in current data, it is here — not in private credit and not in stablecoins.

### PANEL D — Credit outstanding at the obligor *(the denominator that cannot double-count)*

| Series | Measures | Unit | Freq | Latest |
|---|---|---|---|---|
| **Z.1 table D3.s**, debt outstanding by sector | Principal obligations at the ultimate obligor | $bn stock | Quarterly | Nonfinancial corporate **$14,454bn (2026:Q1)**; households $21,069; federal $34,473; **domestic financial sectors $26,108** |
| Derived: NFC debt/GDP | Leverage relative to income | % | Quarterly | **44.2% (2009:Q4) → 49.6% (2019:Q4) → 51.2% (2021:Q4) → 45.4% (2026:Q1)** |

**Domestic financial sectors' own debt is a separate line precisely so that you do not add it to nonfinancial debt.** Every intra-financial claim in your nine channels — bank NDFI lending, warehouse lines, subscription lines, NAV loans, prime brokerage, repo, SRT protection, FABN — belongs here and nowhere else.

**And the empty box you must show the operator:** Z.1 table F4.6.s (*Other loans and advances*, ex-L.216) enumerates every holder of every non-mortgage non-depository loan to US nonfinancial corporates. There is **no line for private credit funds, BDCs, private debt funds or credit interval funds.** The Fed's own FSR sizes US private credit at ~$1.4trn from Preqin, LSEG and PitchBook and then uses Z.1 for the denominator. **The numerator is not inside the denominator.** Two candidate hiding places, both derivable: `FL263069500` rest-of-world loans to US nonfinancial business, **$830.8bn (2019:Q4) → $1,192.4bn (2026:Q1), +43.5%**; and `FL103193005` NFC unidentified miscellaneous liabilities, **$12,101.9bn** — larger than the entire measured NFC debt stock.

### PANEL E — Capital manufacture, not money *(SRT)*

| Metric | Unit | Freq | Latest | Why it is not a dollar figure |
|---|---|---|---|---|
| Protected loan pool | € stock | Annual, three incompatible bases | ~€800bn (BIS, 44-bank Pillar 3, end-2024); >€700bn (IACPM, duration-derived); ~€750bn (BCBS supervisory) | **100% overlap with published bank credit aggregates.** These loans never leave the bank and are already in MFI loans, AnaCredit and Call Reports |
| **Capital relief, bp of CET1** | basis points | Annual | **~43bp average across 44 banks, >100bp in a few** (BIS); 47bp for the average listed EU/UK/Swiss bank (Autonomous, Q4 2024) | This is the correct unit. It measures the constraint that governs how much money the system can create |
| Implied balance-sheet effect | ratio | One-off | **A €525m SRT is associated with ~€570m of additional assets**; Tier 1 *ratio* shows no significant change (Osberghaus & Schepens, AnaCredit + COREP + SHSS) | Banks hold the ratio constant and grow assets. The causal step is erased from every statistic |

**The circular leg — the closest thing in the entire map to capital created ex nihilo:** a loan to an SRT investor binds ~€230k of bank capital and frees ~€5m, stripping the system of ~€4.77m per average debt-financed deal. Current scale is modest and must be stated as such: SRT financing associated with ~10% of the outstanding global market (UK PRA supervisory sample); ~€10bn of total leverage outstanding (BIS, built on stacked assumptions). **BCBS: "Data on the scale of such financing activities are not available."**

### PANEL F — Money economisation *(the largest candidate anyone surfaced, and it is not monetary)*

| Series | Measures | Unit | Freq | Latest |
|---|---|---|---|---|
| **Z.1 `FA103170005`** (F81.t) | Net change in NFC trade payables | $bn SAAR **flow** | Quarterly | **$895.5bn SAAR at 2026:Q1**; FY2025 $407.8bn; FY2024 $81.7bn; four preceding quarterly SAARs $691.0 / $318.8 / $291.2 / $330.3 |
| **Z.1 `FL103170005`** | Stock of NFC trade payables | $bn stock | Quarterly | $4,523.2bn, +11.3% y/y |
| **us-gaap:SupplierFinanceProgramObligation** (XBRL) | Reverse factoring, name by name | $bn stock | Quarterly | ~$74.9bn across 122 CIKs (dedupe required) — a **subset** of the $4,523.2bn, never an addition |
| **FR 2004C collateral multiplier** c = SO/(SO−SI) | Reuse intensity, Treasuries, primary dealers | ratio | **Weekly**, 8-day lag | Annual means: 7.57 (2019) → 14.21 (2023) → 10.63 (2025) → **9.08 (2026 YTD)**. Singh's independent measure ~2.0, flat for a decade |

Inter-firm trade credit creates a claim without creating a deposit; a given M2 supports more real transactions. That is velocity. **It is invisible to M1–M3 by construction because it never touches a bank** — which is exactly the operator's phenomenology, arrived at without any money creation. Caveats that must travel with it: the Z.1 trade credit table fails to reconcile by **−$889.3bn** (~9% of stock), both sides derive from Census QFR and IRS SOI, and SOI runs through 2023 only. Never quote one quarter's SAAR as a trend.

**And reuse intensity is falling, not rising.** The growth is in the *stock* of collateral and the *reach* of the plumbing — sponsored repo went 7.6× in four years to $1,081bn (2026 YTD mean) and from 2.5% to 15.0% of primary-dealer Treasury financing legs. That is a supply-of-collateral story, not a velocity story, and it points at Treasury issuance and basis trades rather than at this channel.

### PANEL G — The price row *(free of every double-counting problem, because a price is not a quantity)*

| Observable | Source | Freq | Cost | Current reading |
|---|---|---|---|---|
| Fed central bank liquidity swaps | H.4.1 | Weekly | free | **$123mn — standing weekly test operations only. No dollar funding stress.** |
| SOFR / GC repo vs IORB | NY Fed, OFR repo release | Daily | free | — |
| FICC sponsored repo & reverse repo outstanding | OFR HF Monitor, `dataset=ficc` | Daily | free | $1,049.8bn / $1,408.4bn (9 Jul 2026) |
| CP–bill, AAA–Treasury, swap spreads (KVJ convenience yield) | H.15, FRED | Daily | free | — |
| Cross-currency basis | **No primary series exists anywhere** | Daily | **paid** | Construct from free OIS (SOFR/€STR/TONA/SONIA) + vendor forward points. BIS's own charts are sourced to Bloomberg |
| Secondary PE price as % of NAV | Jefferies/Lazard/Evercore/PJT | Semiannual | free | All strategies 87%, buyout 91%, venture 79%, real estate 68% (H1 2026). Correct for a 2–3 quarter stale reference NAV and for 26% of deals carrying deferrals |
| Listed PE trust discount to NAV | AIC / RNS | **Daily** | free | The only continuous, exchange-cleared, unmediated vote on private marks |

### §1.8 — THE ONE HEADLINE NUMBER THAT IS DEFENSIBLE

**Drawn bank credit to non-depository financial institutions: $2,016.1bn, all US commercial banks, seasonally adjusted, week ending 5 August 2026. [verified here]**

One balance sheet (US commercial banks). One basis (drawn loan principal). One obligor class. Weekly. Free. It reconciles internally: domestically chartered $1,493.8bn + foreign-related institutions in the US $522.1bn ≈ the total, and the domestically-chartered leg is consistent with the FDIC's Call Report aggregate of ~$1.48trn at Q1 2026 to within vintage and adjustment differences.

**What it means, stated precisely:** roughly $2.0trn of the US commercial banking system's loan book — and therefore roughly $2.0trn of the counterpart asset behind the deposit stock — is a claim on a financial intermediary rather than on a household or a firm. That is a **composition statement about M2**, and it is what "money creation invisible to M1–M3" reduces to once the mysticism is stripped out. The money is not invisible. The credit counterpart is misattributed.

**Its exclusions, in full:** thrifts; every dollar lent by a non-US bank from a non-US office (FSB records Japanese banks increasing lending to North American private credit lenders and gives no number); undrawn commitments, which were 42.9% of total NDFI commitments at Q3 2025; and any decomposition whatsoever — the line bundles mortgage warehouses, PE subscription lines, hedge fund financing, insurers, GSEs, securitisation vehicles and banks' own trust departments.

**And the trap in its own construction:** the H.8 *percent changes* are break-adjusted for structure activity ≥$5bn and for FAS 166/167 and CECL. **The levels are not.** Differencing the levels — which is what every chart in circulation does — counts reclassification as credit growth, and $193.2bn of C&I plus $140.6bn of consumer loans were reclassified into NDFI-and-n.e.c. through September 2025. Use the Fed's own percent-change series.

**This is not "the size of shadow banking." Do not let it be quoted as such.**

---

## §2. THE BUILD ORDER

Ranked by information gained per unit of effort. Time estimates assume one competent analyst with Python and no vendor licences.

### Tier 1 — build this week. Free. Highest ratio in the exercise.

**1. Fed FSR Table 4.1 + Figure 4.1. — 30 minutes. Free.**
Open `federalreserve.gov/publications/files/financial-stability-report-20260508.pdf`, p.36. Transcribe six rows and the total. Compute the residual yourself: 27,033 − (7,746+7,608+5,887+1,368+1,201) = **$3,223bn "other"** — that is where FABS, VRDOs, private liquidity funds, offshore MMFs, LGIPs and stablecoins live, and it is where a new instrument will first appear. Compute the growth gap: **12.0% actual vs 5.4% long-run**. Semiannual; set a calendar reminder for the November release.

**2. H.8 line 26, five panels, using the Fed's percent changes. — 1 hour. Free.**
FRED: `LNFACBW027SBOG` (all CB, SA, weekly), `LNFDCBW027SBOG` (domestically chartered), `LNFFRIW027NBOG` (foreign-related, NSA), plus the monthly `LNFACBM027NBOG`. Verified live in this session. Chart the level for scale; chart the **Fed-published percent change** for growth. Table 10 (foreign-related) is your only free weekly read on foreign bank participation.

**3. The NFC financing gap, on two bases. — 2 hours. Free. This is the test of his premise.**
Download `federalreserve.gov/releases/z1/current/z1_csv_files.zip`, open `csv/S11_1_t.csv` (note: headers carry a `.Q` suffix; the table was renumbered from F.103 in June 2026 but **mnemonics are unchanged**). Take:
- line 6 `FA106006065.Q` foreign earnings retained abroad
- line 7 `FA105440005.Q` net capital transfers paid
- line 8 `FA106000105.Q` gross saving incl. FERA less NCT paid
- line 10 `FA105050005.Q` total capital expenditures
- line 58 `FA105005305.Q` financing gap (published — but recompute it as a check)
- line 14 `FA105000005.Q` net lending, financial account

Identity: `gap = capex − (gross saving − FERA)`. **[verified here]** it holds to the dollar in every quarter 2019:Q4–2026:Q1. Then publish the **ex-capital-transfer basis**: `capex − (gross saving − NCT_received − FERA)`. Note that FRED does **not** carry `FA105440005` — the Z.1 mirror is incomplete; take it from the release package.

**4. Institutional MMF outside M2. — 2 hours. Free.**
Use the **OFR Money Market Fund Monitor's retail/institutional split**, not the Z.1-minus-H.6 subtraction. The subtraction mixes an NSA end-quarter total-assets measure against an SA monthly-average holdings measure and will be wrong by an unstable amount. The ≈$5.26trn figure is the right order of magnitude and the wrong construction.

**5. BoJ L vs M3. — 1 hour. Free.**
`boj.or.jp/en/statistics/money/ms/` monthly PDF. Seven components of L−M3. Give it to the operator as his own precedent, with both disqualifiers attached: financial-institution holders are excluded, and repo was deliberately removed in 2008.

**6. BIS LBS break-adjusted eurodollar flow. — 2 hours. Free.**
`https://stats.bis.org/api/v2/data/dataflow/BIS/WS_LBS_D_PUB/1.0/Q.F.C.A.USD.F.5J.A.5A.A.5J.N?format=csv`. The trick that makes the whole thing work: `L_DENOM=USD` **and** `L_CURR_TYPE=F` mechanically excludes US-located offices, so `L_REP_CTY=5A` *is* "banks outside the United States." Use `L_MEASURE=F` (flow) and `G` (growth). **Never `S` differenced.**

### Tier 2 — build this month. Free but heavy.

**7. Z.1 valuation decomposition, every financial sector. — 1 day. Free. This is the sanity filter on everything else.**
For each sector: `residual = (Level_end − Level_start) − Σ FU`, levels from `csv/*_s.csv`, unadjusted transactions from `csv/*_t_tu.csv`. Result: of the $84,260.7bn increase in domestic financial sectors' total financial assets 2009:Q4→2026:Q1, **$30,090.3bn (35.7%) is not transactions.** Mutual funds 99.6%. Households' equity holdings 86.8%. And the instruments that matter monetarily carry **zero**: MMFs 0.0%, mREITs −0.2%, ABS issuers −1.1%. **A price-inflated measure of shadow banking and a credit-creation measure of shadow banking are close to disjoint sets.** State the limit of the method: the residual is revaluation *plus* other changes in volume, and other-changes-in-volume is exactly where reclassification lands. Only three Z.1 tables (S11.1.r, S11.2.r, S1M.r) publish FR and FV separately.

**8. Call Report NDFI panel with utilisation. — 1–2 days. Free.**
FFIEC CDR bulk download or FDIC BankFind API. Resolve MDRM codes from `federalreserve.gov/apps/mdrm/` — **do not guess them**; both RCON and RCFD variants exist. Validate every filer against the instruction identity: item 9.a = Σ M.10.a…e for banks ≥$10bn. Pull the matching RC-L 1.e.(3)(a)–(e). Compute utilisation = drawn/(drawn+undrawn) per subcategory. **Start the series at 2025Q2** — best-efforts reporting through 2025Q1, comprehensive only from June 2025.

**9. FR 2004C collateral multiplier. — 2–3 days. Free.**
NY Fed API. **Do not use the `-UTSETTOT` totals** — 33 of 53 weeks suppressed in 2025. Build the total from the 21 (SBN2022) or 24 (SBN2024) venue×maturity components, which are almost never suppressed, interpolate the sparse `*` cells, and validate against the weeks where the total *is* published (mean error +0.044% on securities-out, +0.005% on securities-in). Then `c = SO/(SO−SI)`. **Publish `R_T = SO−SI` alongside `c`** — the denominator is ~8% of SO, so a 0.5% error in either leg moves `c` by ~6%. Use a 4- or 13-week moving average; never a single week. Free bonus: the CBSP+TRISP components give you the sponsored share of dealer Treasury financing legs.

**10. N-MFP3 parser for the Circle Reserve Fund. — 1 day. Free.** Small payoff, but it definitively settles one heavily-mis-stated claim. CIK 0000844779, filter `nameOfSeries = 'Circle Reserve Fund'`. Bucket `investmentCategory` on "Repurchase". Result: **88.0% overnight tri-party repo / 12.0% outright Treasuries at 2026-07-31.** Circle's verifiable outright bill position is **$7.18bn = 0.10% of bills outstanding.** The "stablecoins are the marginal buyer of bills" story does not survive this file.

### Tier 3 — build this quarter, if the question warrants it.

**11. Dealer ASC 860-30-50 collateral panel. — 1 week. Free.** EDGAR full-text search on `"permitted to deliver or repledge"`, `"sell or repledge"`, `"sold or repledged"`, `"resold or repledged"`, forms 10-K/20-F. Set a User-Agent with a contact address. Record fiscal year-end with every observation (Jefferies 30 Nov, Nomura 31 Mar). US-six source collateral **$6,907bn FY2025 vs $5,574bn FY2024, +23.9%**. **Never present the sum as a stock of securities** — it counts claims along chains, which is the point if you are measuring chain length and fatal otherwise. Coverage defect: Citigroup discloses source ($1,064bn) but not repledged; BAC rounds to $0.1tn.

**12. BDC bottom-up from EDGAR. — 2–4 weeks. Free.** Universe from Form N-54A filings (definitive; do not use SIC codes). Parse the Consolidated Schedule of Investments for name, investment type, spread, cash vs PIK coupon, fair-value level, non-accrual flag; parse the debt footnote for lender, commitment, drawn, rate, maturity. **BDCs do not file N-PORT**, so there is no structured feed — this is genuine parsing work. It is how OFR reconstructed $195bn of BDC borrowings that Y-14 misses because BDCs borrow through SPVs, often one per lender.

**13. SRT capital relief from Pillar 3. — 3–4 weeks. Free but brutal.** EBA Pillar 3 Data Hub for EU institutions (templates EU SEC1/SEC3/SEC4/SEC5); hand-read PDFs for the rest of the 44-bank sample. Compute `CET1_bp_relief = RWA_relief × requirement / CET1 × 10,000`. **State your pre-SRT risk-weight assumption explicitly — the answer is highly sensitive to it.** Benchmark to BIS's ~43bp. **Do not use the EU-wide Transparency Exercise: discontinued June 2025.**

### Paid — what each licence actually buys

| Licence | Buys | Substitutable? |
|---|---|---|
| ICMA European Repo Survey | The only European repo size estimate | No |
| IACPM Global SRT Bank Survey | The only cross-border SRT issuance time series, 2016–2024, on two bases | No |
| Preqin / PitchBook / LSEG BDC Collateral | Every private credit AUM and origination number in existence, including the Fed's own | No — **and OFR documents that the largest, most reputable managers are systematically absent, because they do not need to list for fund discovery** |
| S&P Global Securities Finance | On-loan, lendable, utilisation, and separately-identified cash-reinvestment revenue | No |
| NAIC statutory data | Schedule D-1-1/D-1-2, Schedule BA, Schedule S Part 3 Sec 1, Schedule DL | Partially — some insurers post statements on IR pages |
| A.M. Best | FHLB funding agreements on the correct Note 11 basis; offshore cession shares | Rebuildable from statutory filings at high cost |
| Bloomberg / LSEG | **Cross-currency basis and FX forward points** | **No. There is no primary-source basis series anywhere** |

### Impossible — do not put these on a plan

NAV lending stock. Subscription lines to private credit funds specifically. Fund portfolio financing totals in any jurisdiction. Rated-note feeder issuance. Annual private credit origination from any official source. FABN by issuer (earliest possible March 2027). Tokenised deposit outstanding. Internalised synthetic prime exposure. Total US securities-based lending. CFO outstandings. GP-stakes volumes. Litigation finance aggregates. BNPL outstanding stock. Drawn warehouse capacity outside the Z.1 finance-company sector. US collateral reuse as an ongoing series. Global trade finance since 2011.

---

## §3. THE FOUR NUMBERS THAT WOULD SETTLE IT

The question is: **is the boom funded by created purchasing power, or by reallocated saving?** Four quantities answer it. All four are obtainable today, free.

### Number 1 — The nonfinancial corporate financing gap, on two bases. **Obtainable. Free. [verified here]**

`Z.1 S11.1.t`, lines 6, 7, 8, 10, 14, 58.

| Quarter | Gap as printed ($m SAAR) | Gap ex-net-capital-transfers | Net lending, financial account |
|---|---|---|---|
| 2019:Q4 | −85,539 | −39,349 | +260,882 |
| 2021:Q4 | +93,953 | +99,823 | −960,478 |
| 2024:Q4 | +6,284 | +33,951 | +598,421 |
| 2025:Q2 | −249,844 | −251,750 | −700,259 |
| 2025:Q3 | −252,822 | −256,123 | −681,091 |
| 2025:Q4 | −164,438 | −198,522 | +610,069 |
| **2026:Q1** | **−634,910** | **−75,977** | **+969,568** |

**Read it correctly and it is decisive.** The headline −$635bn is 88% one non-operating capital transfer of $558,933m — the sixteen preceding quarters of that line run between −$47,889m and +$103,700m. But the ex-transfer basis is **negative in four of the last five quarters**, and 2025:Q2 and Q3 were −$252bn and −$256bn on *both* bases. Gross saving is $3,978,741m against capex of $3,199,548m. **The US nonfinancial corporate sector is funding its own capital expenditure out of internal funds and lending the surplus onward.** There is no aggregate external funding gap requiring a monetary explanation.

*What it cannot tell you:* it is a sector aggregate. The AI/data-centre capex is concentrated in a handful of firms and partly booked at SPV, JV and offshore level where this table does not see it. One live signal in the same file: NFC equity liability `FA103164105` turned **positive (+$124,412m)** in 2026:Q1 — the first net equity issuance after a long run of net retirement, including −$496,556m in 2025:Q1.

### Number 2 — Saving composition, not the saving rate. **Obtainable. Free.**

| | 2019:Q4 | 2026:Q1 |
|---|---|---|
| US gross saving, % of GDP | 18.8% | **17.2%** |
| Personal saving rate (PSAVERT) | 6.2% (Dec 2019) | **2.7% (Jun 2026)** |
| NFC gross saving, $bn SAAR | 2,366 | **3,979 (+68%)** |

**This is the direct answer to "aggregate savings rates are not up."** They are not up because one sector's saving replaced another's. The household saving rate more than halved; corporate gross saving rose 68%. Aggregate flat, composition transformed. **No monetary innovation is required to fund a capex boom that the capex-doers are financing themselves out of retained earnings.**

### Number 3 — Growth of runnable money-like liabilities against trend, and its residual. **Obtainable semiannually. Free to read, impossible to rebuild.**

**$27,033bn at 2025:Q4, +12.0% y/y against a +5.4% 2003–2025 average — 2.2× trend — while M2 grew ~5–6%.** Plus the **$3,223bn** unlisted residual.

This is the strongest published evidence *for* the operator's intuition. It says the stock of pay-on-demand private claims is growing at twice its long-run rate while the official aggregate is not. But four disciplines must travel with it: it is basis-mixed (§1); it is a *stock of claims*, so most of the 12% is reallocation between claim types, not creation; the historical series was restated when new components were added; and **the largest single component, MMFs at $7,746bn, carries zero revaluation in the Z.1 — so its growth is real flow, not price.**

### Number 4 — Break-adjusted offshore dollar credit creation. **Obtainable quarterly. Free.**

**+$1.90trn over the four quarters to 2026:Q1, +11.9% y/y.** Bank loan, bank deposit, brand-new dollar claim, in no aggregate anywhere.

> ⚠ **Superseded 21 Aug 2026 — see `CORRECTIONS.md` C-013/C-014.** Quote three numbers on
> three perimeters, never one: **$2,040bn** gross claim expansion (cross-border *plus* local FX),
> **$1,650bn** liability-matched, **$754bn** owed to an identified non-bank. The last is the
> tightest defensible bound. And it is outside monetary aggregates only where the holder is
> non-resident in the reporting bank's monetary area — ECB M3 and BoJ M2/M3 both include
> resident foreign-currency deposits.

This is the only quantity in the entire nine-channel map that is unambiguously money creation, unambiguously large, and unambiguously outside every monetary statistic in the world. It is also the mechanism that actually transmitted Japanese ZIRP. **If exactly one number is going to change the operator's mind, it is this one.**

*What it cannot tell you:* you cannot attribute any part of it to FX swaps specifically. The LBS has no sector or counterparty-country dimension in the foreign-currency residence cut. No data apportions it, and no apportionment should be invented.

### The fifth, diagnostic rather than decisive

**Drawn bank credit to NBFIs: $2,016.1bn (5 Aug 2026), growing faster than any nonfinancial credit aggregate** — with `FL663168005` (broker-dealer borrowing from banks) at +45.8% y/y as the fastest sub-component. This tells you *where* in the chain deposits are being created, and its growth rate is the honest measure of how fast the intra-financial leg is expanding. It is not additional credit to the real economy and must never be added to Number 1's counterpart.

### And the number that would settle it definitively, which does not exist

**The counterfactual.** Osberghaus and Schepens establish that banks redeploy SRT-freed capital into new lending; they cannot establish what those banks would otherwise have lent. No dataset, public or supervisory, supports it. The "credit created by X" figure the question implicitly asks for cannot be constructed. What can be stated is the size of the constraint relaxation and the empirical fact that the capital ratio does not rise. **That is the honest limit and it should be printed as such.**

---

## §4. THE HONEST GAP REGISTER

Ranked by how much the gap matters to *this* question. For each: fillable by a bottom-up sample, and at what coverage.

| # | Gap | Fillable? | Sample and coverage |
|---|---|---|---|
| 1 | **Look-through from any wrapper to the ultimate obligor** | **No.** Form PF has none; AIFMD stops at the first layer; SFT-2 has no provenance field; ESRB records that many private loans and ABS carry no ISIN or LEI at all | Nothing. This single absence is why no total exists, and it is not a collection lag — it is a design choice repeated across four regimes |
| 2 | **Where AI/data-centre capex is actually booked** — SPV, JV, offshore | **Partially.** Hyperscaler 10-K unconsolidated-VIE, JV and purchase-commitment notes + a hand-built data-centre ABS/CMBS deal register | Deal register: 88 transactions / $48.69bn cumulative through May 2025 (KBRA), rising to ~$61bn outstanding YTD 2026. Coverage of the *external* financing gap: ~10% (Morgan Stanley puts ABS+CMBS at ~$150bn of a ~$1.5trn external need). Coverage of JV equity commitments: near zero |
| 3 | **Non-US banks' lending into US private credit and fund finance** | **No.** Y-14 under-represents them; H.8 Table 10 gives foreign-related institutions in aggregate ($522.1bn) with no decomposition; BIS LBS is residency-based and cannot identify private credit. FSB notes Japanese banks increasing exposure and gives no number | For a Japanese mega-bank this is the most personally relevant gap on the list. Only a bank's own book fills it |
| 4 | **Drawn vs committed, and facility type, on bank lines to funds** | **Partially, US only.** Call Report RC-C M.10 × RC-L 1.e.(3) gives utilisation by subcategory | Banks ≥$10bn only, from 2025Q2 only. **Facility type is nowhere** — no free series distinguishes a subscription line from a NAV line in any jurisdiction; only confidential FR Y-14Q could |
| 5 | **NAV lending stock** | **No.** Rede Partners, the most active surveyor of the lender base, declines to publish one and explains why. Haynes Boone states there is no global database | The "$100–150bn rising to $600–700bn by 2030" figure saturating 2026 commentary is a recycled vendor projection with no reproducible construction. It should not appear in any serious document |
| 6 | **US collateral reuse, current** | **Partially.** FR 2004C multiplier (Treasuries, 24 primary dealers, weekly) + the ASC 860-30-50 dealer panel | Multiplier: excludes derivatives collateral and **excludes UK broker-dealer subsidiaries of US BHCs**, which is where reuse is least constrained — so it is a lower bound by an unknown amount. Footnote panel: numerator unavailable for ~$1.1trn of source collateral (Citi, Jefferies). The 65% benchmark is nine voluntary dealers on three days in June 2022 and has never been repeated |
| 7 | **Intraday and tokenised collateral** | **No — invisible by construction.** A repo opened and closed within the day is flat at every reporting instant, so it enters no 10-Q footnote, no end-of-day tri-party statistic and no reuse numerator | Singh puts the intraday netting benefit at >$200bn per major bank. As tokenisation scales, **measured velocity falls while economic velocity rises.** Unbounded from public data |
| 8 | **Internalisation in synthetic prime** | **No.** No regulator anywhere collects the offset between a dealer's synthetic longs and shorts | Archegos calibrates the upper bound of invisibility: $160bn gross at peak, ~0% in FINRA margin debt, sub-5% per issuer in 13F by deliberate design, and one-twelfth visible to any single counterparty. It was a **family office** and filed no Form PF. That exemption is unchanged |
| 9 | **Trade credit reconciliation** | **No.** Z.1 payables $8,933.6bn vs receivables $9,822.8bn, **discrepancy −$889.3bn**, persistently negative and widening | The largest credit aggregate in this map has a measurement error larger than most of the channels people write about |
| 10 | **US bank SRT** | **Partially.** RC-S/HC-S items 1–6 are confined to sale-accounting securitisations and SRT never qualifies — it is *definitionally* absent. Proxy: HC-L item 7 purchased-vs-sold protection asymmetry in banking-book maturity buckets, plus direct CLN issuance disclosures and Reg Q reservation-of-authority approvals | Coverage unknown, and it misses **directly-issued CLNs entirely** — the structure displacing SPVs (SPV usage fell from two-thirds in 2019 to 15% in 2024) |
| 11 | **Tokenised deposit outstanding** | **No.** Not in JPMorgan's 10-Q, not FR Y-9C, not FFIEC 031/041, not H.8 | Every circulating figure is a press rendering of an executive remark, is a flow, and reconciles to no filing. Upper bound is the sponsoring banks' total deposits — which tells you the series is uninformative |
| 12 | **Tether reserve composition** | **No, and it degraded in 2026.** The Q2 attestation withdrew the Treasury-exposure dollar figure the Q1 gave | ~60% of the stablecoin sector is backed by assets of unknown composition. Every sector-level "stablecoins hold $X of Treasuries" statement, including in BIS and Fed work, rests on issuer self-description |
| 13 | **SRT financing of protection providers** | **No.** BCBS: data not available | The whole public record is ~10% of the market (one PRA supervisory sample) and ~€10bn (BIS, stacked assumptions). This is the leg that creates capital from nothing and it is the least measured thing in the map |
| 14 | **Z.1 unidentified miscellaneous** | **No.** $23,532,650m of assets, $18,636,711m of liabilities, unreconciled by **$4.9trn**; asset side grew $1.88trn in one year | This is the single best defensible upper bound on how much of the US financial system the flow of funds cannot identify, and NFC alone carries $12.1trn of it on the liability side |
| 15 | **Private credit at the obligor in Z.1** | **Not today.** The Form PF private-credit strategy category has been deferred three times to 1 Oct 2026 and the April 2026 SEC/CFTC re-proposal merely *asks* whether to define it | **Do not architect a pipeline that assumes this category will exist** |

**The coverage gap, quantified, and it is the finding:** FSB member jurisdictions, using their own official statistical and regulatory reporting, could identify approximately **$0.5trn** of private credit for the 2025 Global Monitoring Report. Commercial estimates for the same period are **$1.5–2.0trn**. The official sector can see roughly a quarter to a third of the market it supervises.

---

## §5. THE LEADING INDICATOR SET

The collateral-call scenario runs: a Level 3 mark falls → LTV breaches → facilities are drawn or pulled → collateral is called → forced sales. **In this architecture the mark moves last**, because only 10% of NAV facilities saw an independent appraisal in 2025 (down from 22% in 2024) and 85.5% of PE fund assets under a fair-value hierarchy are Level 3. So do not monitor marks. Monitor funding and redemptions.

### Tier 1 — same day to T+2

| Series | Source | Why first | Cost |
|---|---|---|---|
| **Cross-currency basis** | Bloomberg/LSEG (no primary series) | The price of the balance-sheet constraint. Moves before any quantity | paid |
| **SOFR / GC repo vs IORB** | NY Fed | Secured funding stress, T+1 | free |
| **Fed H.4.1 central bank liquidity swaps** | H.4.1 | Currently **$123mn = test operations only.** Any print above that is unambiguous | free (weekly) |
| **FICC sponsored repo & reverse repo outstanding** | OFR HF Monitor `dataset=ficc`, daily | Money funds withdrawing from the sponsored channel and hedge funds losing sponsorship both show here first. It went 7.6× in four years — a *contraction* would be the signal | free |
| **Stablecoin outstanding, daily** | DeFi Llama `/stablecoincharts/all` | A run redeems within hours. **Already amber: the stock is 4.1% below its 17 May 2026 peak, and net flow decelerated from +$107.7bn to +$32.8bn y/y** | free |
| **CP–bill, FRA-OIS, AAA–Treasury** | H.15 / FRED | The KVJ convenience-yield dual. Compresses when shadow supply outruns demand; blows out when a channel jams | free |

### Tier 2 — T+4 to one month

| Series | Source | Signal | Cost |
|---|---|---|---|
| **Perpetual non-traded BDC Form 8-K: requests vs accepted, and the proration factor** | EDGAR, 4 business days | **The single fastest published *quantity* in the entire map, and the only one attached to a redemption right.** Already amber: Q1 2026 was the first quarter accepted redemptions exceeded inflows since the vehicle type was created; several funds received requests well above 5% of NAV and most managers capped at 5% | free |
| **Circle weekly reserve disclosure, mint and burn** | circle.com/transparency | The only gross-flow series in the stablecoin channel. Reserves already fell 2.5% over H1 2026 and the reserve fund shrank 8.6% in four months | free |
| **FR 2004C securities out / securities in** | NY Fed API, weekly, 8-day lag | Build the total from venue components (§2 item 9). A collapse in `SI` with `SO` held is a dealer refusing to re-lend collateral | free |
| **H.8 line 26, percent change** | Weekly, 9-day lag | A *jump* is drawdown of committed lines — the collateral call arriving at the banks — not new lending | free |
| **FINRA margin debt** | Monthly, ~3 weeks | Already amber: Jun 2026 $1,502,072mn → Jul 2026 $1,417,225mn, **−$84,847mn in one month.** **FINRA overwrites one file at one URL with no vintage archive**, so this cannot currently be classified as deleveraging or restatement. Snapshot the file yourself every month starting now — that is a five-minute fix and there is no other way to get it |
| **ICI weekly MMF flows** | Weekly | Flight into government funds is the classic tell | free |

### Tier 3 — quarterly, confirmatory not predictive

Call Report **utilisation** = drawn/(drawn+undrawn) on M.10.b and M.10.c — rising utilisation on a flat commitment base is the arithmetic signature of a drawdown. SCOOS net diffusion on hedge fund leverage and credit terms (2026:Q2 readings: leverage use 0.0, credit terms +5.0, collateral terms 0.0 — dealers report neither tightening nor loosening while the underlying stocks grow 30–50% a year, which is itself informative). Haynes Boone NAV facilities in workout or material uncured default (2% in 2025, 4% in 2024) and appraisal frequency (**a sharp *rise* in appraisal frequency is the stress signal, not the LTV**).

### Too slow to be a monitoring instrument — state this plainly

Fed FSR runnables (semiannual, 4–5 month lag). FSB GMR (annual, 12-month lag). Z.1 (10 weeks nominal — but state-and-local financial assets are extrapolated from a **2021:Q2** Census benchmark, hedge funds run a quarter behind the rest of the release, and IRS SOI inputs run through 2023). BMA Bermuda (16 months). Form PF (2–3 quarters, and PE advisers file **annually**, so the quarterly series is a stale rolling panel whose step-changes are refresh artefacts). BIS OTC derivatives (5 months, plus an unquantifiable triennial coverage break: USD-leg forwards and swaps jumped +15.9% at 2025-S1 and there is no reporting-jurisdiction dimension with which to decompose it).

**Three readings are already amber as of today: the stablecoin stock is below peak and decelerating; perpetual-BDC redemptions exceeded inflows for the first time; and margin debt fell $84.8bn in a month with no vintage archive to interpret it.** None of the Tier 1 price indicators is stressed — the H.4.1 swap line stands at $123mn, i.e. test operations only. The current configuration is quantity softening at the retail redemption margin with no funding stress at the wholesale core.

---

## §6. VERIFICATIONS AND CORRECTIONS TO CARRY

**Verified by me in this session (21 Aug 2026):**
- **NFC financing gap identity**, from `z1csv/csv/S11_1_t.csv` of the 11 June 2026 release. `capex − (gross saving − FERA) = published gap` holds to the dollar for every quarter 2019:Q4–2026:Q1. 2026:Q1: 3,199,548 − (3,978,741 − 144,283) = **−634,910**. Ex-net-capital-transfer basis: 3,199,548 − (3,978,741 − 558,933 − 144,283) = **−75,977**. Full history in §3.
- **H.8 NDFI loans, live from FRED**: `LNFACBW027SBOG` **$2,016.08bn**, `LNFDCBW027SBOG` **$1,493.84bn**, `LNFFRIW027NBOG` **$522.13bn**, all week ending 5 Aug 2026; monthly `LNFACBM027NBOG` $2,009.73bn (Jul 2026, NSA).
- **FRED's Z.1 mirror is incomplete**: `BOGZ1FA105440005Q` and `BOGZ1FL634090005Q` both return HTML 404 pages, not data. Supplementary-table series are not reliably mirrored. Take Z.1 from the release package, not FRED.
- **Z.1 CSV header format**: mnemonics carry a `.Q` suffix (`FA105005305.Q`). Table numbers changed in June 2026; **mnemonics did not**. Key your pipeline on mnemonics.

**Corrections that must travel with the channel notes:**
1. `FL624123035` (hedge fund prime-brokerage borrowing) **does not exist** — deleted in the 2026q1 code changes when repo was folded into loans. The live series is **`FL624135035`**, $774,026m at 2025:Q4. It is not on FRED.
2. `FL153069803` is **"Households and nonprofit organizations; *syndicated* loans to nonfinancial corporate business"** — the unallocated end of the Shared National Credit estimate. It is **not** where the Z.1 parks private credit. At $131.0bn it is far too small and is not intended to.
3. Any code beginning `x4023005` / `x4123005` is **dead**; successors `x4035005` / `x4135005` include repo and are a broader concept. Re-baseline before comparing.
4. Z.1 **does** carry offshore reinsurance cession, on a **reserve-credit basis** (`FL543076035` = $1,125,345m at 2026:Q1). What it misses is modco and funds-withheld — a basis limitation, not an absence, and it is precisely why the Z.1 flow printed −$23.0bn in 2025 against a record commercial deal year.
5. **H.6, 28 July 2026: M2 did not move** (M2SL 2026-05: 23,052.3 → 23,055.6, +0.01%). The *components* moved by up to 670% — small time deposits +46.9%, retail MMF +33.0%, restated to 1962 and 1974. Implied IRA/Keogh netting item ≈**$1,233.0bn** at May 2026, with no FRED identifier yet; derive it by ALFRED vintage diff.
6. **H.8 percent changes are break-adjusted; H.8 levels are not.**
7. **Unresolved contradiction, do not average:** FSB GMR 2025 gives EF5 growth as **4.3%** in the Table 0-1 composition table and **6.6%** in Graph 1-6. Cite one and name it.
8. The FSB narrow measure is **not** a shadow-banking measure. It is built pre-mitigant, it explicitly does not exclude entities individually subject to Basel-equivalent regulation, 76.1% of it is EF1 (dominated by money market and fixed-income funds), and **private credit funds are excluded from it by construction.** Anyone quoting $76.3trn as "the size of shadow banking" is quoting a figure that includes SEC-registered money funds and excludes the entire private credit industry.

---

## THE ONE-PARAGRAPH ANSWER

Nothing in this map supports a single "shadow money" total, and the reason is structural rather than a collection failure: money is a property of a claim relative to a holder, the holder sectors of the various aggregates do not nest, and there is no look-through anywhere in the supervisory perimeter with which to net the chain. What can be defended is a dashboard of seven separately-based panels plus one headline on one basis — **$2,016.1bn of drawn US bank credit to non-bank financial intermediaries**, which measures not hidden money but the *misattribution of M2's credit counterpart*. And the operator's premise, tested against the only series that can test it, does not hold as stated: the US nonfinancial corporate sector's internal funds exceed its capital expenditure, its financing gap has been negative in four of the last five quarters on the transfer-adjusted basis, it is a net lender of nearly a trillion dollars at an annual rate, and its debt-to-GDP has fallen 5.8 points since end-2021. Aggregate saving looks flat because the household saving rate halved while corporate gross saving rose 68% — a composition shift, not a monetary one. The genuine money creation that is invisible to every aggregate on earth is not in private credit, securitisation or stablecoins; it is **+$1.90trn of break-adjusted offshore dollar credit in the four quarters to 2026:Q1**, which is the same eurodollar mechanism that carried Japanese ZIRP into asset prices, and which he can pull from the BIS SDMX API in an afternoon.