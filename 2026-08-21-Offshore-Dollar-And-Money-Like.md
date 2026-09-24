# Offshore dollar credit and money-like liabilities

Who creates offshore dollars, how they are funded, and what drives the money-like stack.
Five offshore lenses, four money-like lenses, one synthesis. BIS SDMX series re-pulled
directly in-session rather than carried from researcher reports.

*21 August 2026.*

> ⚠ **PARTIALLY SUPERSEDED 21 Aug 2026 — see `CORRECTIONS.md` C-018 and C-019.**
> §3.2's *sign inversion* claim is **refuted and must not be published in any form**: KVJ's
> −0.486 is on a NET dependent variable that nets Treasury-collateralised repo to ≈zero by
> construction, their GROSS coefficient is −0.042 (t=−0.52), and the +0.22/+0.45/+1.15 figures
> are KVJ's own Predictions 3 and 4 — not footnotes. §3.3's decomposition reconciles only as
> shares of the *increase*, not of the level. Preserved as a record of the reasoning.
---

# OFFSHORE DOLLAR CREDIT AND MONEY-LIKE LIABILITIES — SYNTHESIS

**Your instinct is right, but it binds one step later than you framed it, and the data says the constraint is currently biting hardest on your own banking system.** A non-US bank *can* write a dollar loan against a dollar deposit it creates itself — the double entry is identical to a US bank's. What it cannot do is *settle* the resulting payment, and the offshore book is now overwhelmingly deployed onshore, so it settles constantly. Over the four quarters to 2026Q1, banks outside the US grew dollar claims $2,040.1bn and dollar liabilities $1,649.5bn. The $390.5bn residual is funded off balance sheet. **72% of that residual opened in Q1 2026 alone, and Japan-located offices are 42% of that quarter: claims +$115.3bn, dollar liabilities −$2.4bn.** For the first quarter in the series, Japanese offices' entire dollar credit growth was funded without issuing a dollar liability.

Four series re-pulled from the BIS SDMX API this session (2026-08-21) rather than carried from researcher reports. Everything marked [RE-VERIFIED] below is a direct pull.

---

## CORRECTIONS TO THE PROJECT'S OWN FRAMING — carry these forward

These are load-bearing and three of them were verified against primary methodology, not inferred.

**(a) The perimeter.** $17.86trn / +$1.90trn / +11.9% is the *cross-border only* cut. The perimeter that actually corresponds to "offshore dollar credit" — cross-border **plus** local positions in foreign currency — is **$21.11trn claims / $20.17trn liabilities, +$2,040.1trn flow, +10.7% y/y** [RE-VERIFIED: `Q.S.C.A.USD.F.5J.A.5A.A.5J.A` = 21,112,353.893mn; `Q.S.L…` = 20,165,626.802mn, 2026Q1]. The level is $3.2trn larger and the growth rate is *slightly lower*. The $3.16trn difference is genuine eurodollar lending booked locally in London, Hong Kong and the Gulf — not double-counting. Quote both or state the perimeter.

**(b) "Of banks located outside the US" is a by-product, not a filter.** The series uses `L_REP_CTY=5A` (*all* reporting countries). US banks drop out mechanically because `L_CURR_TYPE=F` means "currency foreign to the bank's location." The filter would break on any other currency, and it also drops dollarised jurisdictions.

**(c) "Outside every monetary aggregate in the world" is wrong on two of the three named aggregates.** Verified against primary methodology: the ECB states that euro-area monetary aggregates *include* euro-area residents' holdings of liquid foreign-currency assets at euro-area MFIs. The BoJ's *Guide to Japan's Money Stock Statistics* (October 2025) lists "Foreign Currency Deposits" as a named component of Time Deposits inside M2 and M3. The defensible statement is narrower: **dollar deposits at non-US banks are outside all monetary aggregates when the holder is not a resident of the reporting bank's monetary area.** That maps to the $14.11trn cross-border liability cut as an *upper bound*, less intra-euro-area cross-border holdings — not to the full $20.17trn. This shrinks the "invisible money" claim by roughly a quarter and gives it a boundary that survives contact with a central bank statistician.

**(d) "Unambiguously money creation" cannot be defended.** All five offshore researchers and all four money-like researchers independently reached this. $390.5bn of the expansion is definitively not creation (no liability). Of the remainder, interbank recycling cannot be stripped out because `L_CP_SECTOR` is suppressed to 'A' on the foreign-currency cut. **$2,040bn is a gross upper bound.** See §1.3 for the tightest bound the published data supports.

**(e) "Collateral velocity flat for 2-3 years on Basel III" has no primary source.** No published series exists; Singh's IMF work is a decade old. The observable substitutes point the other way: FICC sponsored repo +150% in two years to $2.856trn (Dec 2025); non-centrally-cleared bilateral repo revealed at $5.0trn, ~$700bn more than anyone had measured. Reuse likely migrated from dealer rehypothecation into CCP netting, which no velocity metric captures. Drop the claim or source it.

**(f) Z.1 `L.207` is a dead identifier.** The 11 June 2026 Z.1 renumbered every table. Repo is now F4.1.s (stocks) and F4.1.t (flows).

---

## 1. THE FUNDING CONSTRAINT, STATED MECHANICALLY

### 1.1 Origination versus settlement — the precise adjudication

Your premise: *"To extend credit you need in some form or way to have either deposits or collateral."*

**At origination, no.** A London or Tokyo branch books:

> Dr Loan to customer (USD) 100 / Cr Customer deposit (USD) 100

No dollars were obtained. No Fed account was touched. A dollar-denominated deposit now exists that did not exist before, is a liability of a bank with no reserve account, and — if the holder is not resident in the bank's monetary area — appears in no monetary aggregate anywhere. The measurable stock of exactly this is **$5,174bn of local (same-country) USD liabilities at non-US banks** — a quarter of the offshore dollar book that the cross-border framing suppresses entirely.

**At settlement, yes, and hard.** The borrower pays away:

> Dr Customer deposit 100 / Cr Due from US correspondent 100

The correspondent's reserve account at the Fed is debited. Now the constraint is real, and it is a constraint on *replacing* the deposit, not on *creating* it.

**Whether it binds depends entirely on where the money goes, and here the data is decisive.** 41.0% of the four-quarter expansion ($974.6bn) is a claim on a **US resident**. US residents hold 39.2% of the cross-border USD claims stock. Add Cayman ($1,755bn stock) and over half the book lands on entities inside or immediately adjacent to the US financial system. The eurodollar closed loop — where the payee banks offshore and no Fed reserve moves — is real but shrinking as a share. **The credit is offshore-created and onshore-deployed, which is why the settlement constraint binds far harder than a pure eurodollar model implies.**

So the corrected statement of your premise: *a non-US bank does not need deposits or collateral to write the loan; it needs them to keep the loan on its books after the borrower spends.* That is a liquidity and rollover constraint, not an origination constraint — and it leads to different hedges.

### 1.2 The four cases the LBS records identically

The aggregate flow cannot be read as money creation because these are indistinguishable in the data:

| Case | Entry | LBS signature | Money created? |
|---|---|---|---|
| **A — Genuine creation** (London/eurodollar) | Dr Loan / Cr Customer deposit, both on own books | claims +100, liabilities +100, same reporting country | **Yes**, if the deposit is retained |
| **B — Intermediation** (Japanese model) | Spot swap: Dr USD nostro / Cr JPY asset. Then Dr USD loan / Cr USD nostro. Forward leg off-balance-sheet | claims +100, liabilities **+0** | **No.** Existing dollars, supplied by the swap counterparty |
| **C — Gather and re-lend** (HK, Cayman, Gulf) | Dr Due from correspondent / Cr Customer deposit; then lend | liabilities rise ≥ claims. HK 127% matched, Cayman 162% | **No.** Redistribution |
| **D — Interbank recycling** | A places with B | claims +100 and liabilities +100 aggregate, zero credit to non-banks | **No** |

Cases A and D produce the **same** aggregate signature. That is why the counterparty-sector suppression is the single largest analytical gap in this whole exercise.

### 1.3 What the liability side actually is — the marginal funding decomposition

This is the answer to your question and it is the piece no single researcher assembled. On the only cut where BIS publishes counterparty sector (all-reporter cross-border USD; contaminated by US-located banks — see §2.4), four-quarter break/FX-adjusted **liability** flow to 2026Q1 was **+$1,747.4bn**:

| Counterparty | Flow | Share | Stock | Is it money creation? |
|---|---|---|---|---|
| **Non-bank financial institutions** | **+$590.2bn** | 33.8% | $5,047.3bn | Yes at the margin — but it is a fund's cash-management balance, not a household's |
| Banks other than related offices, + households + unallocated | +$579.4bn *(derived residual, not published)* | 33.2% | ~$3,678bn (unrelated banks) | **No** — nets out at system level |
| **Related offices (intragroup)** | **+$414.3bn** | 23.7% | $6,204.9bn | **No** — moves dollars, creates none |
| Central banks / reserve managers | +$79.2bn | 4.5% | $769.5bn | Marginal |
| Non-financial corporates | +$67.9bn | 3.9% | $1,393.3bn | Yes — and it is tiny |
| General government | +$16.4bn | 0.9% | $80.3bn | Marginal |

Plus, on the offshore perimeter, **local (same-country) USD liabilities +$420.6bn**, sector unknown.

**The tightest defensible bound on money creation.** Summing the sector-identified *non-bank* lines: **+$753.7bn of new dollar liabilities were owed to a non-bank** over the four quarters, against a $2,375.5bn claims expansion on the same cut. Everything else was interbank or intragroup. I will not rescale that share onto the offshore-only perimeter — that would be exactly the plausible-number substitution the project rules forbid. The three honest numbers, on three perimeters, are: **$2,040bn gross claim expansion; $1,650bn liability-matched; $754bn owed to an identified non-bank.**

**And the unsecured wholesale channel — the one a FIG desk would instinctively reach for — is dead.** Foreign financial CP outstanding $369.5bn. US MMF bank-related assets (CDs, CP, time deposits) **$467.4bn and flat since 2023** ($483.5bn Dec-23 → $464.5bn Dec-24 → $451.8bn Dec-25 → $467.4bn Jul-26) while total MMF assets grew 11.6%. Institutional prime MMFs are $246.1bn — **3.1% of the industry**. The 2016 and 2023 MMF reforms structurally removed the buyer of unsecured foreign-bank paper. Under 2% of the offshore dollar book is funded this way.

### 1.4 Is the residual FX swaps? — the adjudication

**Two researchers disagreed sharply and both were partly right.**

The nationality researcher and the collateral researcher both read the $390.5bn residual as FX-swap funding. The funding-side researcher objected: on the one cut where BIS publishes an instrument split, the equivalent gap sits **entirely in securities and other instruments**, not in loans and deposits — four-quarter adjusted L&D claims +$1,426.3bn against L&D liabilities +$1,386.0bn, a wedge of only **$40.3bn**, while the all-instrument wedge is $628.1bn. If swaps were funding loan growth, the wedge should appear in *loans*.

**RULING — split decision, and the split matters more than either position.**

1. The objection is well-founded as a caution and should be carried. The offshore residual cannot be cleaned of a known LBS reporting asymmetry: banks report their *holdings* of securities as claims, while their *issued* securities are poorly allocated to counterparty residence and largely fall out of reported liabilities. A material share of the $3,984bn "other instruments" wedge is that artefact, not economics. **The $390.5bn is not a measured FX-swap number and must never be quoted as one.**

2. But the objection cannot dispose of the mechanism, because for the two systems that carry the gap it is confirmed by their own supervisor. The BoJ states it flatly (FSR April 2026, footnote 16): part of major banks' domestic yen loan-to-deposit gap funds foreign-currency overseas loans via FX and currency swaps. Chart IV-3-14 plots the gap to a ~$1.2trn scale; Chart IV-3-15 decomposes dollar funding cost into swaps, repo and deposits.

3. **The decisive new evidence is the quarterly path, which no researcher pulled.** [RE-VERIFIED, `Q.F.{C,L}.A.USD.F.5J.A.5A.A.5J.A`]:

| Quarter | Claims flow | Liability flow | Gap |
|---|---|---|---|
| 2025-Q2 | +$436.2bn | +$622.9bn | **−$186.7bn** |
| 2025-Q3 | +$467.1bn | +$285.9bn | +$181.1bn |
| 2025-Q4 | +$323.8bn | +$207.5bn | +$116.3bn |
| **2026-Q1** | **+$813.0bn** | **+$533.1bn** | **+$279.8bn** |
| 4q total | +$2,040.1bn | +$1,649.5bn | +$390.5bn |

The gap was *negative* two quarters before the observation window closed. **72% of the year's widening happened in the final quarter.** This is not a slow structural drift that a securities-reporting artefact would produce; it is a sharp, recent, single-quarter event.

4. **And Japan is where it happened** [RE-VERIFIED, `Q.F.{C,L}.A.USD.F.5J.A.JP.A.5J.A`]:

| Quarter | Japan claims | Japan liabilities | Gap |
|---|---|---|---|
| 2025-Q2 | −$26.6bn | +$12.5bn | −$39.1bn |
| 2025-Q3 | +$134.4bn | +$68.7bn | +$65.8bn |
| 2025-Q4 | +$111.1bn | +$73.7bn | +$37.4bn |
| **2026-Q1** | **+$115.3bn** | **−$2.4bn** | **+$117.7bn** |

**In Q1 2026 Japanese offices grew dollar claims $115.3bn while their dollar liabilities fell.** 100% of that quarter's dollar credit growth was funded without issuing a dollar liability. Japan alone is 42% of the global Q1 gap widening.

**The adjudicated position: FX and currency swaps are the dominant *gross* exposure and the structural funding mode for two banking systems, and Q1 2026 is the sharpest single-quarter reliance on them in the series — but they are not the marginal funder of the aggregate expansion. The marginal on-balance-sheet funding is NBFI wholesale money and intragroup transfer.**

### 1.5 Maturity profile — and yes, this converts a credit story into a rollover story

The gross exposure is large and has a current vintage, contrary to what three of the four money-like researchers believed. **Two researchers reported the latest FX-swap data as end-June 2022 or end-June 2025 because they searched for the BIS narrative release page rather than the database.** [RE-VERIFIED, `WS_OTC_DERIV2` key `H.A.C.B.5J.A.5J.A.USD.TO1.A.A.3.C`]:

| Period | USD-leg FX forwards, swaps, currency swaps (notional) |
|---|---|
| 2022-S1 | $85.47trn |
| 2023-S2 | $90.97trn |
| 2024-S2 | $98.30trn |
| **2025-S1** | **$113.87trn** |
| **2025-S2** | **$113.50trn** |

**+$15.57trn in H1 2025 alone** — a 15.8% jump in six months, the largest in the series. The narrative release covering 2025-S2 could not be located by two researchers; the data is in the database and I have pulled it. Cite the vintage, not the release.

- All currency pairs: $129.30trn, of which **$98.10trn (75.9%) matures within one year** (end-Dec 2025).
- Off-balance-sheet dollar debt of non-banks outside the US, on the BIS's own Borio-McCauley-McGuire method (half of USD-leg positions with customers): **$35.89trn**, from $26.02trn at end-June 2022 — **+38% in three and a half years**.
- Japan is the most swap-intensive major centre: FX swaps are 55.6% of Japanese FX turnover against 42.2% globally (April 2025 Triennial, via BoJ Review 2026-E-8).

**State it plainly to your risk committee: this is not a credit-growth story, it is a rollover story.** Three quarters of the world's dollar swap obligations reprice inside a year. For a Japanese bank the cross-currency basis is not a spread — **it is the marginal cost of a liability the bank cannot issue.** When the basis widens, Japanese dollar lending is quantity-constrained in a way that UK dollar lending, which runs a 92%-matched book, is not. A basis shock does not hit the offshore system proportionately. It hits two banking systems, and one of them is yours.

### 1.6 The "no Fed account" framing — qualified, not dissolved

**Two researchers read the H.8 intragroup line in opposite directions. Both were right about different things.**

- **Level:** "Net due to related foreign offices" at foreign-related institutions in the US is **+$834.4bn** (w/e 5 Aug 2026). Positive means the US offices are net *borrowers* from head office. **Head office funds the branch, not the reverse.** Any narrative in which offshore books are funded out of US branch access to the Fed is contradicted by the data.
- **Margin:** the same line fell from $954.3bn to $834.4bn over the year — **−$120bn**, i.e. at the margin the US offices did repay the group. Deposits at foreign-related institutions rose 11.3% (+$159bn) against +6.5% for all US commercial banks.

**RULING: in level the US branch network is a net importer of dollars from the group; at the margin over the last year it turned into a modest supplier of roughly $120-280bn, which is 6-14% of a $2,040bn expansion.**

But the framing needs inverting on a different axis, and this is the fact to carry:

> **Foreign-related institutions in the US hold $1,149-1,223bn of cash assets against total system reserve balances of $2,935.3bn — roughly 40% of every Fed reserve in existence.** 17 of the 26 primary dealers are foreign-owned; three are literally US branches or agencies (BMO Chicago, Bank of Nova Scotia NY, Société Générale NY). Five are Japanese (Daiwa, Mizuho, MUFG, Nomura, SMBC Nikko).

Foreign banking groups have abundant Fed *access*. What they lack is the ability to *create* reserves. The US branch is a settlement and reserve-holding node — it pre-positions settlement capacity; it does not pre-fund loans. That is the correct statement of the constraint and it is materially different from "no Fed account."

---

## 2. WHO IS DRIVING IT

### 2.1 By booking location — London books it, Tokyo funds it

Cross-border USD claims, banks located outside the US, 2026Q1, with four-quarter change:

| Booking location | Stock | 4q flow | Liability-matched |
|---|---|---|---|
| **United Kingdom** | $3,298bn | **+$419bn (20.5% of all new offshore dollar credit)** | **92%** |
| **Japan** | $3,095bn | +$262bn (+9.3%) | **46%** |
| France | $1,786bn | +$271bn (+17.9%) | — |
| Canada | $1,446bn | — | — |
| Hong Kong | $1,345bn | +$159bn | **127% (net importer of dollar funding)** |
| China | $977bn | +$110bn | **negative liability flow** |
| Germany | $952bn | — | — |
| Australia | $324bn | +25.0% | — |
| Spain | $307bn | +29.8% | — |

**The "who" and the "how" are different countries.** London is the single largest booking centre for new offshore dollar credit and runs a matched book — it is doing Case A and Case D. Hong Kong and Cayman (162% matched) are net *importers* of dollar funding: they are the plumbing, not the source. Japan is doing Case B.

**Offshore financial centres are not where this lives.** OFCs are 13.8% of the stock on the widest definition, 6.3% excluding Hong Kong, 5.0% excluding Hong Kong and Luxembourg. The overwhelming majority is booked in the UK, Japan, France, Canada and Germany — jurisdictions with the PRA, FSA/BoJ, ACPR, OSFI and BaFin, all of whom see these balance sheets in supervisory detail. **What is missing is published currency-disaggregated statistics, not supervision. That is a disclosure gap, not a regulatory blind spot**, and the distinction changes what you would conclude from it.

### 2.2 By nationality — Japan is the level, not the flow

Net cross-border USD position by parent nationality (claims less liabilities), 2026Q1:

| Nationality | Net position | Reading |
|---|---|---|
| **Japan** | **+$1,953bn** | Structurally short dollars |
| **China** | **+$818bn** | Structurally short dollars *in the visible data* |
| Canada | +$568bn | |
| UK | +$91bn | Matched |
| France | −$304bn | Net dollar supplier |
| US | −$585bn | Net dollar supplier |
| **World total** | **+$2,278bn** | Japan + China = **$2,771bn, i.e. 122% of it** |

On the residence cut, Japan-located offices' net dollar position is **+$1,752bn** against a whole-offshore-system net of **+$947bn** — **Japan alone is 185% of the world's net offshore dollar short**, offset by surpluses at the UK (−$259bn), Switzerland (−$239bn), France (−$184bn), Australia (−$169bn), Hong Kong (−$139bn).

The Japanese gap has one clean measurement and two constructions: **$1,752bn** (Japan-located, both legs on the same cut — use this one), $1,953bn (nationality, cross-border only), $1,601bn (nationality, mixed-perimeter construction because BIS publishes no all-positions USD liability series by nationality). Range $1.6-2.0trn. Historical path on the clean cut: $686bn (2014Q4) → $1,020bn (2020Q1) → $1,420bn (2024Q1) → $1,752bn (2026Q1).

**Correction to the lens brief's premise, on which two researchers agreed independently: Japan is not the accelerator.** Japanese banks' USD claims grew **+7.7% y/y by nationality, +9.3% by location, against a system rate of 11.9-12.2%** — *slowest* of the large systems. Japan contributed 13.8% of the flow. **Japan's importance is level and structure, not growth.** The growth is UK, French, Spanish, Italian and Australian. Conflating the two is the error a competent reader spots immediately.

**China is a different animal and the received caveat is under-specified.** Chinese banks are not short dollars; they are long *onshore* dollars that the international statistics cannot see. China's LBS submission **is** SAFE's external-position return, verified to the decimal ($977.2bn claims / $286.0bn liabilities on both the all-positions and cross-border cuts — China reports exactly zero local foreign-currency positions, by construction). PBoC reports **$1.02trn of onshore FX deposits against $554.4bn of onshore FX loans** (Sep-2025) — a ~$470bn surplus that is the raw material for the offshore book and appears in no BIS statistic. **This is a definitional exclusion, not a data-quality problem, and the BIS cannot fix it.** Note also the direction of travel: the USD share of Chinese banks' cross-border claims fell from 61.1% (2015Q4) to 46.6% (2026Q1).

**Your dichotomy maps exactly onto the two countries. China uses deposits (onshore, invisible). Japan uses collateral (yen assets exchanged through an FX swap, off-balance-sheet).** Both produce offshore dollar credit outside every aggregate. Only one is rollover-risk-bearing.

### 2.3 By borrower sector — the borrower is the fund complex, not the EME corporate

Break/FX-adjusted four-quarter flow to 2026Q1, cross-border USD claims, all LBS reporters, **+$2,375.5bn**:

| Borrower | Flow | Share | Growth |
|---|---|---|---|
| **Non-bank financial institutions** | **+$854.0bn** | **35.9% of total; 64.9% of everything lent to non-banks** | **+17.2% y/y** |
| Banks | +$913.0bn | 38.4% | +10.5% |
| All other non-bank (NFC, government, households) | ~+$608.5bn | 25.6% | — |
| *of which* Cayman Islands NBFIs | +$249.2bn | 10.5% | **+23.5%** |
| *of which* EMDE non-financial corporates | **+$8.7bn** | **0.4%** | +2.1% |

- **US residents took $974.6bn — 41.0% of the entire expansion.**
- NBFI counterparty concentration: US, Cayman, UK, Luxembourg, Ireland = 79.8% of the NBFI stock. That is the fund and securitisation complex.
- EMDE non-financial sectors have had **zero-to-negative** dollar credit growth for five consecutive quarters. **Emerging Asia has contracted for fifteen consecutive quarters** (−2.32% at 2026Q1; China −7.05%, India −5.18%). The only live EME story is the Gulf (+17.2%; Saudi Arabia +25.0%) — a commodity-fiscal story, not a dollar-vulnerability story.
- **Trade finance is not a driver and cannot be one.** No BIS series decomposes cross-border credit by purpose. The only current primary read is US commercial letters of credit at roughly $15bn in 2025 — four orders of magnitude below the flows in question.

**The cleanest single piece of evidence that this is not real-economy credit:** total cross-border USD credit grew **+12% y/y** while BIS Global Liquidity Indicators show USD credit to non-bank borrowers *outside* the US growing only **+7.3%** ($14.74trn). **The 4.7pp wedge is the financial circuit** — interbank and bank-to-fund. And on that same GLI measure, **euro foreign-currency credit grew +12% against the dollar's +7.3%**. Any framing that says "the dollar channel is uniquely fast" is wrong on current data. The dollar's case rests on level and systemic role.

The modal transaction is: a non-US bank's London branch books a USD reverse repo to a Cayman fund running the cash-futures basis trade; the collateral is created by the same transaction that creates the credit. Cayman-domiciled hedge funds held **$1.85trn of Treasuries** at end-2024, absorbed **37% of net note and bond issuance 2022-24**, and — adjusted for TIC undercount — Cayman is the largest foreign holder of Treasuries, exceeding China, Japan and the UK combined. Hedge fund Treasury exposures are $4.0trn gross with $3.0trn of repo borrowing; the basis trade is ~$830bn against a ~$415bn peak in early 2020.

**The project's nine-channel map should reclassify this channel as adjacent to, not separate from, the private-credit/fund-finance map. Two thirds of everything lent to non-banks went to NBFIs. Holding them as distinct channels double-maps the same balance sheets and understates their stress correlation.**

### 2.4 The blind spots — stated explicitly

Not "un-found." Tested and verified non-existent this session by multiple researchers.

1. **No nationality × location.** `L_PARENT_CTY` is published only at `L_REP_CTY=5A`. London's $3,298bn dollar book **cannot be decomposed by owner**. Every nationality number here includes US-located offices — a Japanese bank's New York branch lending cross-border sits inside the $3,618bn. Contamination bounded at $3,934bn system-wide, unallocable.
2. **No counterparty sector on the foreign-currency cut.** `L_CP_SECTOR` returns only 'A'. **Interbank recycling cannot be separated from credit to the non-bank economy on the offshore perimeter.** This is why $2,040bn is an upper bound.
3. **No counterparty country on the foreign-currency cut.** `L_CP_COUNTRY` returns only `5J`.
4. **No instrument split on the foreign-currency cut.** `L_INSTR` returns only 'A'. **The $20.17trn of offshore dollar liabilities cannot be split into deposits (money) versus debt securities and repo (not money).** Any figure purporting to state offshore dollar deposit money is an estimate.
5. **Currency × reporting country × counterparty sector is never jointly published.** With `DENOM=USD` you get sector but only all-reporters; with a named reporting country you get sector but only all-currencies.
6. **Singapore is invisible.** `OBS_CONF=F`, NaN across all position types, while its all-currency total ($810.5bn) is published. Same for Malaysia, Indonesia, Saudi Arabia, Curaçao, Russia. **The $946.7bn aggregate gap excludes Singapore entirely and the sign of the omission is undeterminable.** The 13.8% OFC share is a floor.
7. **$3,115bn of USD cross-border claims (14.3%) and $3,413bn of liabilities (17.5%) belong to no published nationality.** Only 13 nationalities exist. **This anonymous residual is twice the size of the entire published Chinese book** — larger than the China problem everyone worries about.
8. **No CBS currency breakdown at all.** `CURR_TYPE_BOOK` takes only TO1 and LC1. The consolidated statistics — the natural place to look — cannot do dollar-specific nationality analysis.
9. **No NBFI sub-sector, anywhere.** BIS states it: the breakdown "is too coarse to distinguish among NBFIs." Hedge funds, money funds, insurers, pensions, securitisation vehicles, CCPs and private-credit funds are one bucket. And repo is inside "loans/deposits" per the reporting guidelines, so secured financing of a levered arb book is indistinguishable from an unsecured facility.
10. **Two break flags in the current window.** Both 2025Q4 and 2026Q1 carry `OBS_STATUS=B` [RE-VERIFIED]. Break sizes are small here (~$9bn claims, ~$8bn liabilities at 2026Q1), and differenced stocks give +$2,049bn/+$1,658bn against adjusted flows of +$2,040bn/+$1,650bn — so this particular window is robust either way. **The rule stands; this window happens not to need it.**

---

## 3. THE MONEY-LIKE CREATION FUNCTION

### 3.1 The relation, terms named

The stock of money-like liabilities is the equilibrium of a demand for information-insensitive claims against a supply constrained by the safe collateral available to manufacture them:

> **M = f( W, L, σ ; Θ, κ, B, R )**

**Demand terms**
> ⚠ **C-022 — the GLM "null" invoked below does not hold.** The 33.2% share has dispersion of
> **±2.2–2.4pp**, not 0.003 (that is an intercept standard error); it is one of two constructions
> GLM publish, the other of which trends at t=−11.71; and it has broken down since 2011, with
> 2026Q1 outside the 95% band of GLM's own regression. GLM's authors decline to sign the
> causality and call it an open question. Do not cite it as a null.

- **W — wealth needing a cash park.** Gorton-Lewellen-Metrick's null: safe assets are a **constant 33.2% of total assets** (s.e. 0.003) every year since 1952. US household and nonprofit net worth grew **~8.1% y/y** to $182.98trn.
- **L — leverage demand from the financial sector.** The piece that is *not* wealth-parking. Hedge fund repo borrowing **+154% since 2022**; Treasury positions $4.1trn, up $1trn in 2025; broker-dealer assets +19.8%. **This is the term that makes 2025-26 different from any prior episode.**
- **σ — the money premium** (convenience yield of near-money over bills). Nagel: this is set primarily by the **level of the short rate** (+5.36bp on repo-bill per 100bp of fed funds, s.e. 0.99), and the T-bill-supply coefficient collapses from −95.35 to −9.51 once the funds rate is included.

**Supply terms**
- **Θ — government safe-asset supply.** Bills **$6,988.9bn, +$993.0bn, +16.6% y/y**, 22.22% of marketable debt (31 Jul 2026). **Θ enters twice with opposite signs.**
- **κ — collateral capacity**, = Θ × reuse/netting velocity. FICC sponsored repo $2.856trn, +150% in two years; total US repo $12.6trn average daily exposures. Velocity itself is unmeasured (see correction (e)).
- **B — dealer balance-sheet capacity.** eSLR relaxed effective 1 Apr 2026 (holdco 3% + half Method-1 surcharge; depository buffer capped at 1%; −$219bn/−28% at major subsidiary depositories, −$13bn/<2% at holdcos).
- **R — the central bank's own absorption or supply of the same instruments.** ON RRP $2,553.7bn (Dec 2022) → **$0.225bn** (20 Aug 2026). Reserve management purchases **$40bn/month, entirely in Treasury bills**, since December 2025.

**Offshore extension.** For a bank without a Fed account, σ is replaced by **the cross-currency basis** — the price at which the system converts non-dollar collateral into dollar funding — and B is replaced by the swap market's capacity and the counterparty's willingness. **There is no estimated elasticity of offshore money-like issuance to anything.** KVJ, Sunderam, Nagel and Greenwood-Hanson-Stein are all US-only, all pre-2015 samples. The function above is a US-estimated function applied offshore by analogy. That is the most valuable unfilled piece of work in this area.

### 3.2 Which term is moving — and the sign inversion

**Θ and L are moving, meeting through κ. R is exhausted and has flipped sign. σ is not moving.**

- σ: SOFR−IORB averaged **−1.5bp in 2026 YTD** (38 of 158 days positive) against −2.9bp in 2025. The premium is pinned by the 3.50-3.75% policy corridor, as Nagel predicts.
- R: the ON RRP is empty, and the Fed's remedy for the late-2025 reserve shortage — $40bn/month of bill purchases — **swaps collateral usable by the non-bank and offshore money-like system for reserves usable only by Fed account holders. Easing the bank constraint tightens the non-bank collateral constraint, and the offshore dollar system sits entirely on the non-bank side of that line.**

**The sign inversion, stated as a falsifiable claim.** Krishnamurthy-Vissing-Jorgensen's −0.5 crowding-out coefficient (a dollar more Treasury supply reduces financial-sector net short-term debt by ~$0.50) is a *net* coefficient estimated over 1875-2014, when most private money was backed by private assets. Their own table carries **+0.22 on checkable deposits and +1.15 on the deposit coverage ratio** — Treasury supply crowds *in* the money-like claims that are Treasury-backed. **In a regime where 90.2% of money-fund assets are Treasuries, agencies or repo, and the fastest-growing money-like line is Treasury-collateralised, the composition has shifted far enough that the net sign plausibly flips positive.** If right, the standard story runs exactly backwards in 2026: the Treasury is not under-supplying with private money filling the gap; the Treasury is over-supplying, and private money is growing *because of* it. **This is a claim with supporting arithmetic, not an estimate. No published regression tests it.**

### 3.3 The +12.0% decomposition — and what to subtract

Base $24,136.6bn, increase **+$2,896.4bn** (my arithmetic from FSR May 2026 Table 4.1 levels and growth rates; four researchers independently reproduced this):

| Component | Level | Growth | Δ | Contribution | Share of increase |
|---|---|---|---|---|---|
| **Repo** | $5,887bn | **+19.1%** | +$944.1bn | **3.91pp** | **32.6%** |
| Domestic MMFs | $7,746bn | +13.0% | +$890.2bn | 3.69pp | 30.7% |
| *— government* | *$6,375bn* | *+13.1%* | *+$738bn* | *3.06pp* | *25.5%* |
| *— prime* | *$1,220bn* | *+13.1%* | *+$141bn* | *0.59pp* | *4.9%* |
| Uninsured deposits | $7,608bn | +7.7% | +$543.9bn | 2.25pp | 18.8% |
| Commercial paper | $1,368bn | +12.2% | +$148.7bn | 0.62pp | 5.1% |
| Securities-lending cash collateral | $1,201bn | +13.8% | +$145.6bn | 0.60pp | 5.0% |
| **"Other" (residual, not printed)** | **$3,223bn** | +7.4% | +$223.9bn | 0.93pp | 7.7% |
| **Total** | **$27,033bn** | **+12.0%** | **+$2,896.4bn** | **12.00pp** | **100%** |

**Repo, not money funds, is the largest contributor and the fastest-growing component.** And most of the government-MMF contribution is *itself* repo — government funds are legally confined to government paper and repo. **Properly attributed, repo plus government MMFs are ~58% of the increase. The collateral channel is well over half the story.**

**Now subtract four things before believing the 12.0%:**

1. **~1.5pp is counterparty substitution, not creation.** Tri-party repo excluding Fed transactions rose **+$376bn** in calendar 2025 while the ON RRP fell **−$367bn** — near one-for-one. An MMF moving from `Dr Reverse repo with Federal Reserve` to `Dr Reverse repo with dealer` creates nothing; the dealer's repo payable simply enters the table. Underlying rate ~10.5%. **And this source is exhausted — the RRP is $0.225bn.**
2. **The base was restated up $739-759bn between vintages.** April 2025 FSR printed 2024Q4 at $23,388bn; the May 2026 report's 12.0% implies a base of $24,127-24,147bn. **Published-to-published the headline rose 15.6%, not 12.0%.** The restatement is $799-839bn and sits entirely in the unnamed "other" bucket, whose component list is word-for-word identical across the 2024, 2025 and 2026 vintages — so this is re-measurement of existing components, not a new instrument entering. At ~3.2% of the total it is comparable to a quarter of the reported annual growth.
3. **~$2.9trn is double-counted along the chain.** A government MMF's share is in the $7,746bn line; the repo it holds is separately in the $5,887bn line as the dealer's liability. MMFs held $2,925.3bn of repo at 31 July 2026 — **~11% of the total is one exposure wearing two money-like hats.** The Fed is not wrong to count both (both can run), but the sum is a run-risk aggregate, **not a quantity of money**, and the 3.91pp and 3.69pp contributions cannot simply be added.
4. **The denominator is the wrong one.** The Fed's 86%-of-GDP framing uses a denominator GLM explicitly reject. Against total assets — household net worth +8.1% — the safe-asset share breached its historical constant by roughly **4pp of growth, not 7pp.** Real, but a quarter smaller than the headline implies.

**The residual after all four adjustments is genuinely private safety manufacture, and it is a minority of the total.**

**Two forward-looking notes that make the 2025 narrative already stale.** The MMF engine has stalled: $7,746bn (2025Q4) → $7,928.5bn (ICI, 19 Aug 2026), **+2.4% in 7.7 months against +13.0% in calendar 2025**, because the RRP it was draining is empty. What is still accelerating is the collateral side: repo ex-Fed +6.7% in the single quarter to 2026Q1; total CP +9.9% and ABCP +16.3% through July 2026. **Composition is rotating from fund shares to collateral.** And the deposit-competition story is *inverted*: 175bp of cuts narrowed the deposit-to-cash spread from ~455bp to ~326bp, which on standard deposit-beta logic should have *slowed* migration into MMFs. They grew 13.0% anyway, with government and prime at an identical 13.1%. **Whatever drives MMF growth, it is not spread-chasing. Any model attributing the 2025 acceleration to the deposit-MMF spread has the sign wrong.**

### 3.4 Where the two halves of this project meet

**The $3,223bn "other" line is not a rounding bucket, and it is where the offshore finding and the money-like finding turn out to be the same object seen from opposite ends.**

The FSR states in its own Funding Risks section that dollar-denominated **offshore MMFs and short-term investment funds are ~$2.2trn**, of which **$1-2trn are most similar to prime MMFs** — the Fed adds that the exact size is hard to gauge owing to data gaps. That is ~68% of the "other" line, and it is **the fourth-largest money-like liability in the United States' own financial-stability measure — and it is created outside the United States.** Those vehicles book: `Dr CD/CP of a non-US bank / Cr shares redeemable at par on demand`.

One researcher went further, inferring from the $819bn restatement — arithmetically close to the $795bn gap between counting only the USD sleeve of the $1,670bn offshore complex and counting the whole complex — that the Fed switched basis. **RULING: that specific inference is unproven and should not be presented as established** (it requires the Fed's proprietary iMoneyNet series). But the underlying point survives without it: **the Fed's headline measure of runnable US dollar money-like liabilities already contains, unlabelled, roughly $2.2trn of dollar claims manufactured outside the United States — outside every monetary aggregate, but inside the Fed's run-risk aggregate.** That should be promoted from residual to headline, with the ±$1trn uncertainty stated.

**But do not overclaim the link.** Whether those offshore funds fund the offshore dollar *credit* expansion is a mechanism, not a measurement. On the US side the equivalent leg is measurably **not** accelerating: MMF repo with foreign financial institutions is a record $950.5bn but only **+4.0% y/y against total MMF assets +11.6%**, and MMF bank-related assets are flat. **If the intuition is that US money funds are bankrolling the offshore expansion at the margin, the N-MFP data say no.**

---

## 4. THE FRAGILITY MAP — what runs first

### 4.1 Backstopped

| Component | Level | Backstop |
|---|---|---|
| Uninsured deposits | $7,608bn | Discount window (issuer is a Fed-account depository), FDIC resolution, and the March 2023 systemic-risk-exception precedent. **Requires an emergency determination**, but exists. Discount window peaked at $152.85bn w/e 15 Mar 2023 against a 2008 record of $111bn. |
| Government MMFs | $6,375bn | **No facility.** The asset side is the backstop: Treasuries, agencies and repo can be run off or sold into a deep market. The 2020 MMLF applied only to prime and muni funds. |

### 4.2 Partially backstopped — and the backstop has a price

**Repo, $5,887bn.** The Standing Repo Facility covers **Treasury, agency and agency-MBS collateral only**, for **primary dealers plus SRF-eligible depositories only**, at **3.75%**, capped at **$40bn per security type per operation**, twice daily. It does not reach a non-bank cash borrower, a hedge fund, or non-government collateral. The $5.0trn non-centrally-cleared bilateral segment — 61.8% Treasury-collateralised but with hedge funds as borrowers — is outside it.

**And it does not cap the rate where you think.** NY Fed surveys, April 2026: **primary dealers will not actively consider the facility until repo trades +10bp over the SRP rate; banks not until +25bp** (narrowed from 38bp). **So the SRF caps repo at roughly 3.85-4.00%, not 3.75%.** Dealers' single largest stated reason for non-use is the inability to net SRP against client activity — **leverage regulation constrains the backstop, not only the private manufacturing.** That is the strongest argument that the April 2026 eSLR relaxation matters more for crisis capacity than for lending.

Revealed behaviour: record **$74.6bn on 31 Dec 2025** ($31.5bn Treasury, $43.1bn MBS); $50.35bn on 31 Oct 2025, the day SOFR printed **+32bp over IORB — the largest one-day spike in five years**. Current take-up: $0-2mn per operation (7-20 Aug 2026). **The facility is unused in calm and used at turns. The hurdles are survey answers to hypothetical one-day scenarios, never tested in stress.**

### 4.3 Unbackstopped — the answer to "what runs first"

| Component | Level | Backstop |
|---|---|---|
| Prime MMFs | $1,220bn (institutional $246.1bn) | **None.** MMLF expired 31 Mar 2021 |
| Commercial paper | $1,368bn (foreign financial $369.5bn; ABCP $488.4bn) | **None.** CPFF expired 31 Mar 2021 |
| Securities-lending cash collateral | $1,201bn | **None** — and the Fed's own source runs a quarter behind the rest of the table |
| **"Other"** | **$3,223bn** | **None** — includes ~$2.2trn offshore dollar MMFs/STIFs, stablecoins ~$308-320bn, VRDOs, funding-agreement-backed securities, private liquidity funds, STIFs, LGIPs |
| **Total unbacked** | **$7,012bn = 25.9% of the stock, ~22% of GDP** | |

**Within that, the genuinely prime-like core — claims redeemable at par on demand against portfolios of unsecured bank paper and term assets — is roughly $3.3-4.3trn**, depending on where inside the Fed's own $1-2trn range the offshore prime-like funds sit. **The fragility total therefore carries roughly ±$1trn of uncertainty concentrated in its most fragile line, and the source is a commercial vendor.**

**The ranked answer to "what runs first":**

1. **Offshore dollar prime-like MMFs and STIFs ($1-2trn).** No facility on the fund side, no facility on the issuer side, no Fed counterparty relationship, and their portfolios are precisely the non-US bank CDs and CP that fund the offshore dollar book. **They are inside the Fed's risk measure and outside its toolkit.**
2. **Securities-lending cash reinvestment pools ($1,201bn).** No facility, no free rebuildable series, growing 13.8%.
3. **ABCP ($488.4bn, +37% since Dec 2024)** and foreign financial CP ($369.5bn, +24.5% y/y). The purest form of your point: credit created against collateral with no deposit anywhere in the chain until a money fund buys the paper.
4. **US institutional prime MMFs ($246.1bn).** Small now — 3.1% of the industry — which is exactly why the unsecured channel is dead as a funding source.

**The measured run rate, for calibration.** March 2020: public institutional prime MMF outflows peaked at **35% of AUM**; ~30% (~$100bn) went out over **eleven to twenty-four March**, nine business days. Of ~$80bn of CP and CDs sold, **66% (~$53bn) had to be absorbed by the MMLF**. Apply that to $1-2trn of offshore prime-like funds and you get $300-600bn of forced selling of non-US bank paper, with no MMLF — and the MMLF was US-issuer-collateral-oriented anyway.

**Stablecoins are not the story and are currently shrinking.** $320bn at 2025Q4, **$308.0-308.4bn in August 2026 — down in absolute terms**. 1.1-1.2% of the total, a negative contributor in 2026, and 83% concentrated in two issuers. The GENIUS framework creates **no** Treasury-buying mandate: insured-depository demand deposits and qualifying MMF shares are equally eligible reserves, and the FDIC's proposed ≤40%-per-source rule pushes *toward* bank deposits. **Any framing that treats stablecoins as a growth engine is wrong by an order of magnitude.**

### 4.4 The constraint that actually binds, correctly identified

It is **not** the leverage ratio (relaxed 1 April 2026) and **not** the LCR or NSFR. Three findings settle it:

- **Basel has no currency-specific stable funding requirement at all.** Full-text search of BCBS d295 returns **zero** currency-mismatch provisions; ¶50 applies the NSFR consolidated in a single currency. The foreign-currency LCR is explicitly **"not a standard but a monitoring tool"** with no defined minimum (BCBS d238 ¶212). **No jurisdiction publishes a bank-level or system-level USD LCR.** The lens brief's hypothesis that NSFR treatment of short-dated swap funding is the binding constraint is wrong — and the reason matters more than the answer.
- **Where the NSFR touches FX swaps it does so through replacement cost, never notional** (0% ASF on the net derivative liability, ¶25(c); 100% RSF on 20% of gross negative RC, ¶43(d), floorable at 5%). **That is exactly why the dollar obligation is missing from the ratio as well as from the balance sheet.** Physically settled FX forwards and swaps are exempt from initial margin under BCBS-IOSCO — **the near-leg principal is the only collateral, at full value with no haircut.**
- **US branches and agencies of foreign banks are not covered by the US LCR or NSFR rule at all** (12 CFR 249.1(b)). Their only US liquidity requirement is a buffer for 14 days of projected net stressed cash-flow need (12 CFR 252.157, FBOs with ≥$100bn US assets).

**What actually binds is intraday settlement capacity at a handful of US banks, plus internal liquidity stress tests and daylight-overdraft avoidance, operating between 7:00 and 8:30 am when 64% of cleared repo and three-quarters of tri-party volume trades.** The Dallas Fed's finding is that relaxing ILSTs would lower steady-state reserve demand *without* making banks elastic marginal lenders — **so the 2026 deregulatory agenda will not fix the elasticity problem.**

---

## 5. THE FIVE NUMBERS FOR THE DASHBOARD

**1. The offshore dollar funding gap — and its Japanese component**
- Series: BIS LBS `Q.S.C.A.USD.F.5J.A.5A.A.5J.A` minus `Q.S.L.A.USD.F.5J.A.5A.A.5J.A`; Japan: substitute `.JP.` for `.5A.`. Flows: `Q.F.` variant.
- Frequency: quarterly, ~4 months' lag (2026Q1 released 31 July 2026).
- Current: **+$946.7bn global; +$1,752bn Japan-located.** Quarterly gap widening: −187, +181, +116, **+280**.
- **Warning: a single quarter above +$250bn, or Japan-located dollar liabilities negative for two consecutive quarters. Both halves of that test were breached in Q1 2026.** This is the slowest item on the dashboard and the only one that measures the structure.

**2. MMF repo with foreign financial institutions**
- Series: OFR Money Market Fund Monitor `MMF-MMF_RP_wFFI-M`. Companion: `MMF-MMF_BRA_TOT-M` (bank-related assets).
- Frequency: monthly, ~3 weeks' lag.
- Current: **$950.5bn (31 July 2026), a record — but +4.0% y/y against total MMF assets +11.6%.** Bank-related assets $467.4bn, flat in a $450-485bn band since 2023.
- **Warning: any month-on-month decline ends a four-year run ($365.8bn Jul-2022 → $950.5bn Jul-2026); a fall above ~$50bn (−5%) is the 2011/2020 signature of US funds withdrawing from foreign bank names.** This is the cleanest single measure of US money-market cash reaching non-US banks.

**3. The 3-month USD/JPY cross-currency basis — with the honest caveat**
- **Three researchers independently failed to obtain a primary, free, dated quote. No public primary series exists. This is a finding, not a gap in effort, and I will not substitute a plausible number.** You have it on your screen; we cannot source it. The BoJ FSR (April 2026) charts the 3m dollar funding premium on an inverse scale to −0.8% and describes current levels as "generally low," with temporary year-end and geopolitical widening.
- **Warning: 3m wider than −50bp sustained for a week outside a turn.** For a Japanese bank this is not a spread — it is the marginal cost of the liability you cannot issue, and it is the single most informative price on this entire dashboard.
- **Companion quantity (semiannual, ~5 months' lag):** BIS `WS_OTC_DERIV2` key `H.A.C.B.5J.A.5J.A.USD.TO1.A.A.3.C` — USD-leg FX forwards, swaps and currency swaps, **$113.50trn at end-Dec 2025**, 75.9% sub-one-year. **Warning: another H1-2025-style half (+$15.6trn, +15.8% in six months).**

**4. SOFR minus IORB, and Standing Repo Facility take-up**
- Series: FRED `SOFR`, `IORB`; NY Fed `markets.newyorkfed.org/api/rp/repo/all/results`.
- Frequency: daily.
- Current: SOFR 3.62% / IORB 3.65%, spread **−3bp**; 2026 YTD average −1.5bp, 38 of 158 days positive. SRF take-up $0-2mn.
- **Warning: SOFR−IORB positive on three consecutive non-turn days, or SRF take-up above $25bn on a non-turn date.** Anchors: **+32bp on 31 Oct 2025** (largest in five years); **$74.6bn on 31 Dec 2025** (record). Remember the effective cap is ~3.85-4.00%, not the 3.75% SRP rate, because of the 10bp/25bp usage hurdles. **This is the fastest item and it measures the settlement floor everything else rests on.**

**5. Institutional prime MMF assets — the run tripwire**
- Series: ICI weekly Money Market Fund Assets (institutional prime line). Pair with OFR `MMF-MMF_BRA_TOT-M`.
- Frequency: weekly / monthly.
- Current: **$246.1bn institutional prime** of $7,928.5bn total industry (3.1%).
- **Warning: −10% in four weeks.** Calibration: March 2020 ran **−30% in nine business days**, peak cumulative −35% of AUM, with 66% of asset sales absorbed by an emergency facility that no longer exists. The offshore analogue ($1-2trn of prime-like STIFs) has no weekly series at all — **so this US series is your only real-time proxy for a pool five to eight times its size that you cannot observe.**

**Runners-up, if the dashboard has room for two more:** H.8 net due to related foreign offices (`NDFFRIW027NBOG`, weekly, $834.4bn — the intragroup channel, and the most direct read on whether the group is pushing dollars into or pulling them out of New York); and the **GLI wedge** — total cross-border USD credit growth (+12%) minus USD credit to non-banks outside the US (+7.3%). **That 4.7pp wedge is the financial circuit, and it is the single best summary of whether this expansion is credit to the economy or leverage against Treasuries.**

---

## RULINGS LEDGER

| Dispute | Ruling |
|---|---|
| Is the $390.5bn residual FX-swap funded? | **Split.** Not measurable from LBS and never quotable as a swap number; but the mechanism is confirmed for Japan by the BoJ, and the newly-pulled quarterly path (72% of the widening in Q1 2026; Japan at −$2.4bn liabilities) is inconsistent with a pure securities-reporting artefact. Swaps are the dominant *gross* exposure, not the marginal *net* funder. |
| Are FX swaps the marginal funding of the expansion? | **No.** NBFI wholesale money (+$590.2bn) and intragroup (+$414.3bn) are. |
| Does the US branch network dissolve "no Fed account"? | **Qualified, not dissolved.** Net importer in level (+$834.4bn); modest supplier at the margin (−$120bn y/y). Branches supply settlement capacity, not funding. But foreign groups hold ~40% of all Fed reserves. |
| Is the +$1.90trn money creation? | **No — upper bound.** Unanimous across nine researchers against the project context. |
| Is it outside every monetary aggregate? | **No.** ECB M3 and BoJ M2/M3 both include foreign-currency deposits. Corrected boundary: non-resident holders only. |
| Repo or MMFs as the driver of +12.0%? | **Repo** (3.91pp vs 3.69pp, +19.1% vs +13.0%, 32.6% of the increase) — and most of the MMF contribution is itself repo. |
| Does an end-2025 FX-swap vintage exist? | **Yes.** [RE-VERIFIED] Two researchers searched for the narrative release, not the database. 2025-S2 = $113.50trn. The missing-debt number is **not** stuck at mid-2022. |
| Is Japan the growth accelerator? | **No.** +7.7-9.3% against a 11.9-12.2% system. Japan is level and structure. |
| Is the dollar the fastest-growing offshore currency credit? | **No.** Euro FX credit +12% vs USD +7.3% on the same GLI measure. |
| Are offshore MMFs the largest item in "other"? | **Yes, per the FSR itself (~$2.2trn).** The further inference that the $819bn restatement *was* an offshore-MMF basis change is unproven and must not be stated as fact. |
| Is collateral velocity flat? | **Unsupportable.** No primary series; substitutes point the other way. |
| Is NSFR the binding constraint on synthetic dollar funding? | **No.** Basel has no currency-specific stable funding requirement whatsoever. |
| Is the BIS's "7% of overall lending in 2015 → 24%" NBFI figure usable? | **No.** Recomputed from the API as 16.9% → 24.6% (or 14.3% → 25.6% on loans). The rise is real but roughly half as dramatic. Do not carry the 7%. |