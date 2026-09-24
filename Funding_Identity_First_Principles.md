# The Funding of the AI Trade — a first-principles decomposition

Nine traditions analysed independently, three adversarial reviews, one synthesis.
Figures marked `[own]` were pulled and computed from FRED/BEA/Census primary endpoints
on 21 August 2026; `[rev-V]` verified by a named reviewer; `[unver]` secondary and unverified.

---

# THE FUNDING OF THE AI TRADE — A FIRST-PRINCIPLES DECOMPOSITION

*Synthesis of nine traditions and three adversarial reviews. Every figure below is either (a) pulled and computed by me from FRED/Census/BEA primary endpoints on 21 Aug 2026, marked **[own]**; (b) verified by a named reviewer against a primary source, marked **[rev-V]**; or (c) secondary and unverified, marked **[unver]**. Nothing else is asserted.*

---

## 0. THREE THINGS THAT MUST BE SAID BEFORE THE ANALYSIS

### 0.1 Your ZIRP reference case is inverted for the United States

Your premise contains three separable claims. Two are false for the US and one is true for Japan.

**(a) "Without M1 to M3 being affected." False, by a wide margin.** M2 as a share of nominal GDP **[own, FRED M2SL ÷ GDP]**:

| | M2/NGDP |
|---|---|
| 1995Q1 | 46.4% |
| 2006Q2 | 49.8% |
| 2008Q4 | 56.2% |
| 2019Q4 | **70.0%** |
| 2020Q2 | 91.1% (peak) |
| 2023Q4 | 73.1% |
| **2026Q2** | **71.3%** |

M2 compounded 5.86%/yr against nominal GDP 3.76%/yr from Dec-2008 to Dec-2019 **[rev-V, Review 3]** — roughly **$3.0tn of M2 accumulated above a constant-velocity path**. That is the largest sustained divergence of broad money from nominal income in the post-Volcker record. Two measurement traps you may have fallen into: the May-2020 Regulation D amendment moved ~$11.2tn of savings deposits into M1, so any M1 chart spanning 2009–2021 is uninterpretable across that seam; and there is no US M3 for the ZIRP period at all — the Fed ceased publication 23 March 2006.

**(b) "Money creation in the financial sector." Your own named mechanism contracted throughout ZIRP.** ABCP outstanding: $1,190bn (Jun-2007) → $329bn (Dec-2011) → $247bn (Dec-2019), down ~79% from peak and still falling through the decade. Money-fund assets did not durably exceed their 2008Q4 level until 2018–19 **[rev-V, Review 3]**. The shadow-money boom you are remembering is **2002–2007**. You have back-dated the mechanism of the pre-crisis credit boom onto the post-crisis discount-rate boom.

**(c) "Real estate up." It fell for three years into ZIRP.** Case-Shiller national troughed Feb-2012 at 133.99, a further −12.2% *after* ZIRP, QE1 and QE2. Household mortgage debt fell 12.4% from its 2008Q1 peak and did not regain it nominally until 2020Q3. The broad-money-creating channel into US housing ran in **reverse** for the entire ZIRP decade **[rev-V, Review 3]**. What moved was the real discount rate: 10y TIPS 2.17% (Dec-08) → −0.60% (Jul-12).

**Where you are right: Japan.** BoJ assets ×4.67 against broad money ×1.32, 2008–2019. If you want an "asset prices without broad money" precedent, cite Japan, not ZIRP generally. Given where you sit, that is probably where the intuition was formed, and it is defensible there.

**The reformulation that is stronger than what you said, and that you should adopt:** *US M2 outgrew nominal income by ~$3.0tn over 2009–2019 and velocity fell; the increment was absorbed in asset markets rather than goods markets.* This is arithmetically true, it is the Bridges–Thomas monetarist arithmetic run inside the Bank of England, and it concedes only that the aggregate moved while arguing about *where the money went* — a far harder position to dislodge than "the aggregate didn't move."

**And note what the level series does to the present question.** M2/NGDP is 71.3% now against 70.0% at end-2019 and 91.1% at the 2020 peak. It has moved within 1.3pp for two years. The monetary level shift happened in 2008–2021 and is over; the COVID overhang has been absorbed by nominal GDP growth, not by monetary contraction. **Nothing monetary analogous to your ZIRP case is happening now.** This also repairs a prior in your own file. "M2 +5.5% y/y, roughly nominal GDP pace, the aggregate says no boom" is not established by the growth rate — 2009–2019 also ran near NGDP pace while $3tn accumulated. It *is* established by the level series, which is flat. Use the level, not the rate.

### 0.2 The nine traditions are not nine pieces of evidence

Six of them assert "investment requires finance, not prior saving," and **five cite the same modern source to do it** (Borio–Disyatat, BIS WP 346, 2011). That is one accounting distinction restated in six vocabularies with one shared citation, not six independent confirmations **[rev-V, Review 2]**. Likewise: "forced saving" appears four times as four discoveries, when Hayek's 1932 *QJE* note — cited inside the package — is literally the paper establishing that Bentham, Thornton, Ricardo, Malthus, Mill, Wicksell, Mises and Schumpeter are restating one doctrine with a single genealogy. "M2 is the wrong instrument" appears seven times. And every tradition that states the illusion-of-wealth point hands the quantification to the same single paper (Gabaix–Koijen), while four of them explicitly say they cannot derive it themselves.

Treat the package as **four findings, not nine**: a funding identity (Godley/Kalecki), a financing-vs-saving distinction (Wicksell/BIS), an incidence result (Cantillon/Thornton), and a collateral asymmetry (Fisher). Everything else is vocabulary or restatement.

### 0.3 One adversarial correction is itself wrong, and I have to say so

Review 2's finding **E3** — that the Minsky report's leverage ratios (16.9% now, 25.6% in 2019, 59.8% in 2009Q1) are "internally impossible" — is incorrect. Those are the Fed's own published series **[own, FRED NCBCMDPMVCE = Z.1 FL104104016]**: 2026Q1 **16.86%**, 2019Q4 **25.58%**, 2009Q1 **59.78%**, 2000Q1 25.08%. The reviewer recomputed the ratio from `BCNSDODNS ÷ NCBEILQ027S` (which gives 20.79%) and treated the difference as an error. It is a different construction, not an error. The criticism that *survives* is narrower and real: the report paired the Fed-published market-value ratio (16.9%) with a self-computed current-cost ratio (`BCNSDODNS ÷ TNWMVBSNNCB` = **37.82%**, **[own]**), so the headline "spread" is not like-for-like. Same rule you already have: never sum or difference across measurement bases — including when the reviewer does it.

---

## 1. THE FUNDING IDENTITY

### 1.1 Statement — three levels, never mixed

**Level A — the closed system.** I ≡ S ex post, for the world, always. This is satisfied by the income the investment itself generates. It is unviolatable and therefore uninformative. Any claim that "investment exceeded saving" is either wrong or is using "saving" to mean something other than the national-accounts residual. Do not spend time here.

**Level B — the sector. This is the level that answers your question.** For any sector, in any period, with no free parameters:

```
Capital expenditure
  ≡  Gross saving  (undistributed profits + IVA + consumption of fixed capital
                    + foreign earnings retained abroad)
   + Net capital transfers received
   + Net incurrence of liabilities  (debt securities + loans + trade payables + equity issued)
   − Net acquisition of financial assets
   + Net sales of existing real assets to other sectors
```

Nine terms. Exhaustive. Every one is published quarterly in Z.1. **There is nowhere else for the money to come from.** Review 1 verified this identity closes to the dollar (residual 0.000) on all nine quarters tested — it is not a fitted result **[rev-V]**.

**Level C — the firm.** The same identity with the sector's internal netting undone. Circular and vendor financing lives *only* here, because it nets to zero at Level B by construction.

Two further operations change the *measurement* without changing resource use, and both matter enormously here:

- **Reclassification.** Lease instead of own; hold the asset in an SPV classified in a different sector. The concrete, copper, transformers and electricians are consumed identically; the capex leaves the sector.
- **Depreciation policy.** Changes net investment, reported profit and tax cash flow. Changes nothing real. Not a funding source — but, as shown below, the single largest term in the identity.

### 1.2 Allocation — US nonfinancial corporate business, trailing four quarters (2025Q2–2026Q1)

All **[own]**, from FRED Z.1 series, computed by me:

| Term | $bn SAAR, 4Q avg |
|---|---:|
| **Internal funds** (FA106000105, gross saving less net capital transfers paid) | **3,410.0** |
| — of which consumption of fixed capital (FA106300003) | **2,459.8 = 72.1%** |
| — of which undistributed profits + IVA + foreign retained (residual) | ~950.2 |
| **Capital expenditure** (FA105050005) | **3,084.3** |
| **Financing gap** (FA105005305) = capex − internal funds | **−325.7** |

The published financing gap by quarter: 2024Q4 +6.3; 2025Q1 +142.1; **2025Q2 −249.8; 2025Q3 −252.8; 2025Q4 −164.4; 2026Q1 −634.9.** Negative in **four consecutive quarters**. (Review 1's "five of the last six" is one quarter generous; the substance is identical.)

Supporting terms:

- **Net equity issuance** (NCBCEBQ027S): 2026Q1 **+$124.4bn SAAR — the first positive quarter since 2021Q2**, and the 15th positive quarter since 2000. Trailing four quarters remain net retirement. *(Three of the nine reports date this wrong — "2021Q1", "first time", "over a decade." Only the Cantillon report has it right. You would have read three concurring reports as corroboration; they were not concurring.)*
- **NFC debt** (BCNSDODNS): $14,453.8bn at 2026Q1, **+4.64% y/y**, against nominal GDP **+6.07% y/y**. Corporate credit grew **1.43pp slower** than nominal income over the year. On an annualised-quarterly basis it grew faster (+9.13% vs +5.76%) — one quarter, and comparing a y/y rate to an annualised-quarterly rate is precisely the base error your rules forbid, which the Wicksell report committed.
- **Foreign saving:** BEA current account −$226.8bn in 2026Q1 ≈ 2.8% of GDP annualised **[own, IEABC]**; Review 1 gets 3.3% on a Z.1 basis. The two constructions differ by ~$160bn/yr and I have not reconciled them. Both agree on direction: **down from ~4.1% in 2024.** Foreign funding of the US *fell* through the AI build.
- **Fiscal counterpart:** general government net lending −$2,955.2bn SAAR at 2026Q1; −$2,293.5bn average across 2025, 7.5% of GDP **[own, AD01RC]**.
- **Household saving rate:** 2.7% June 2026 **[own, PSAVERT]** — in the 2005–07 range, not a post-2005 low (C-028; June 2022 was 2.2%). Your premise that saving rates are not up is correct and understated: they have fallen.

### 1.3 The allocation in plain words

Rank the terms by size and the puzzle changes shape:

1. **Consumption of fixed capital — $2,460bn/yr, 72% of internal funds.** The AI capex boom is overwhelmingly financed by the *return of capital previously invested*. Nobody abstains, no claim is created, no money moves, no aggregate registers anything. This is the largest single funding term in the entire identity and it is not "saving" in any behavioural sense.
2. **Undistributed profits — ~$950bn/yr**, of which roughly half has a government-net-borrowing counterpart. This is where your missing saving actually is: it is corporate, not household, and its proximate source is the deficit.
3. **A one-off fiscal capital transfer to business in 2026Q1** — the IEEPA tariff refunds ordered by the Supreme Court in February 2026, recorded by BEA as a capital transfer. Real cash to firms; not in GDP, not in profits, not in M2 **[rev-V, both Review 1 and the Kalecki report, on different series]**. Magnitude disputed: $559bn SAAR (Z.1, NFC) vs ~$673bn SAAR (BEA, domestic business); ~$140–168bn actual cash in the quarter. **This is the single cleanest documented instance of purchasing power invisible to every monetary aggregate that exists anywhere in this package.** It also inflates the 2026Q1 surplus, so the Minsky report's "largest in the post-war record" must be discounted for it — a reconciliation that report does not make.
4. **Net debt issuance** — positive, but growing slower than nominal income over the year.
5. **Net equity issuance** — still net retirement on a trailing-year basis; one positive quarter.
6. **Foreign saving** — shrinking.

### 1.4 What is *not* measurable, stated as such

- **SPV/JV data-centre capex.** If the vehicle is classified as a financial entity, its capex never enters NFC capex at all. I do not know the magnitude and neither does anyone in the package. **Direction of bias is known: my headline understates externally-funded capex.** This is the single most important hole.
- **Intra-sector circular and vendor financing.** Nets to zero at Level B by construction. A signature is visible (NFC trade receivables +$877bn SAAR in 2026Q1 **[rev-V, Review 1]**) but a signature is not a measurement. The sector accounts are *structurally incapable* of testing the circular-financing thesis.
- **Off-balance-sheet lease and offtake obligations.** The two figures in circulation — "$970bn hyperscaler lease commitments, ~$660bn unrecognised" and "$662bn signed but not yet commenced" — have **no verified primary provenance**. A text search of the full 96-page BIS Quarterly Review March 2026 returns **zero** occurrences of "662", "660", "970", "not yet commenced", "Beignet" or "Hyperion"; Box A contains no lease-commitment quantum at all **[rev-V, Review 2]**. These are almost certainly one trade-press number appearing twice under two attributions, and the package treats them as two sources. **Do not use either until traced to a Moody's publication.**
- **The measurement-error floor.** NFC capital-account and financial-account net lending differ by $133–224bn *per quarter* **[rev-V]**. **Any claimed funding channel smaller than roughly $0.7tn annualised is inside the discrepancy and is not identifiable in the flow of funds.** That floor disqualifies most of the channels the nine reports propose — including the entire off-balance-sheet construction, the promoter's-profit tally, and the ~$82bn/yr share-based-compensation channel. No report applies it to any report but its own.

---

## 2. THE RESIDUAL

**On the published US accounts through 2026Q1, the residual requiring a money-creation explanation is zero. The non-financial corporate sector funds 100% of its capital expenditure from internal funds and has $325.7bn/yr left over. It is a net lender. No external saving is required, therefore no money creation is required to supply it.**

That is the honest answer and you should take it seriously before anything else in this document.

Four qualifications, none of which reverses it:

**(i) "Zero" means "zero within ±$0.7tn/yr."** The flow-of-funds discrepancy is the floor. A genuine money-creation channel of, say, $400bn/yr would be entirely invisible in this identity. That is not a small band.

**(ii) The aggregate cannot see reclassification or circularity.** Both biases run the same way — they understate external funding. Neither is quantified by anyone.

**(iii) The average is not the margin.** Oracle, CoreWeave and the neoclouds are plainly externally funded and levered. They are small against a $3.1tn sector. The aggregate result and the firm-level stress are both true and not in conflict; the error is to let either one stand for the other.

**(iv) The regime is dated to change, and that is the real question.** The three markers, with their provenance quality stated:
- Aggregate hyperscaler free cash flow crossing zero around Q3 2026 (Epoch AI, from SEC XBRL) **[unver — Review 2 could not verify; a Microsoft crossing dated Q3 2028 is four quarters beyond any disclosed guidance and is a projection wearing the precision of a measurement]**.
- Incremental debt rising from 9% of capex (FY24) to 32% LTM (FactSet) **[unver]**.
- The two Z.1 series that *are* verified: NFC debt issuance roughly tripling to $1,249bn SAAR in 2026Q1, and net equity issuance flipping positive **[own]** — one quarter each, subject to revision.

**So the correct question is not "where is the funding gap" but "when does one open, and how fast."** Stop looking for a hidden residual today. Put a quarterly tripwire on the Z.1 financing gap (FA105005305) and on the external-funding share of hyperscaler capex from the 10-Q cash-flow statements. Those are the two numbers that matter and both are published.

### 2.1 The finding inside the residual that nobody in the package foregrounded

Between 2023Q4 and 2026Q1 **[own]**:

| | Gross fixed investment | Consumption of fixed capital | **Net fixed investment** |
|---|---:|---:|---:|
| 2023Q4 | 2,849.6 | 2,195.8 | **653.8** |
| 2026Q1 | 3,223.2 | 2,531.6 | **691.6** |
| change | **+373.6 (+13.1%)** | +335.8 (+15.3%) | **+37.8 (+5.8%)** |

**Ninety percent of the increase in gross capital expenditure was absorbed by faster depreciation.** The marginal asset is a 4–6 year GPU, not a 30-year structure. *In net capital-accumulation terms the AI boom is barely visible in the sector accounts.* Two consequences follow:

- An investment boom with net accumulation this small cannot generate the aggregate funding stress the narrative implies. The gross number is what fills newspapers; the net number is what the economy actually accumulates.
- **The entire thing is decided by a depreciation assumption.** Reported useful lives are 4–6 years against an annual product cadence. Goldman's sensitivity puts cumulative 2026–31 depreciation at ~$3tn on a five-year life versus ~$4tn on three **[unver]**. That $1tn is an unrecognised write-down sitting inside a footnote assumption, and it is the closest thing anywhere in the accounts to a quantified illusion. It is disclosed, auditable, and changes with a single line in a 10-K.

### 2.2 What the residual analysis does *not* dissolve — the real resource transfer

The funding question dissolves. The **incidence** question does not, and it is measurable. From the Census C-30 workbook, June 2026 release, pulled and computed by me **[own]**:

| $mn SAAR | Jun 2025 | Jun 2026 | y/y |
|---|---:|---:|---:|
| Total private construction | 1,702,574 | 1,622,458 | **−4.7%** |
| Private office | 100,575 | 115,808 | +15.1% |
| — of which **data centre** | 46,850 | **68,297** | **+45.8%** |
| Office **ex** data centre | 53,725 | 47,511 | **−11.6%** |
| **Total private construction ex data centre** | 1,655,724 | 1,554,161 | **−6.1%** |

Data centres are **59.0% of all private office construction** (55.6% in April). *(The Schumpeter report's "$50.7bn SAAR April 2026, ~52%" is stale by roughly three quarters and understates the effect; the correct April figure is $61.9bn and 55.6%.)*

This is the cleanest single empirical object in the entire exercise: **US private construction ex-data-centres is contracting at 6.1% y/y while data centres grow at 45.8%.** No aggregate shows it — total private construction is simply down 4.7%. It is pure within-aggregate reallocation: real resources — concrete, electrical contractors, switchgear, interconnection queue positions — being bid away from every other use. That is forced saving with an address, and it requires no money creation whatsoever to occur. Pair it with the power-price series (PPI industrial electric power +15.0% since Jan-2024; CPI household electricity +43.5% since Jan-2019 against headline CPI +32.2% **[unver, from the Cantillon report]**; PJM base residual capacity $28.92 → $329.17/MW-day) and you have the transfer, the mechanism and the incidence.

---

## 3. FOUR THINGS CALLED "MONEY CREATION INVISIBLE TO M1–M3"

Your question fuses four mechanisms that have different plumbing, different measurement, and different verdicts. Separated:

| | Mechanism | Creates purchasing power? | Visible in M2? | **Operative now?** |
|---|---|---|---|---|
| **(a)** Near-money issued outside the banking perimeter | Non-bank issues a par-redeemable, information-insensitive claim | Yes, functionally | No, by construction | **No** |
| **(b)** Credit that funds spending without creating deposits | Closed-end fund lends *existing* deposits | No — transfers it | No, **in principle** | **Yes — this is the cycle** |
| **(c)** Collateral-based purchasing power | Asset re-rates → holder borrows against it | Yes, if the lender is a bank | Only the bank part | **Partially; small where measured** |
| **(d)** Discount-rate revaluation | Lower discount rate raises PV of unchanged cash flows | **No — none at all** | Not a transaction | **Dominant in the wealth data** |

**(a) Near-money outside the banking system — the Gurley–Shaw point. NOT operative, and the tradition's own metrics say so.** Commercial paper, the classic private money factory, shrank 2.4% y/y to June 2026. The safe-asset share of total US assets has been band-stable at 31.1% ± 2.3% since 1952. The deposit share of private safe financial debt moved from 27% pre-crisis to ~35% by 2020 — *toward* banks, the wrong direction for the thesis. The one apparent wedge (Divisia M4 +6.8% vs simple-sum M2 +5.4%) rests on 6.1 of its 6.8pp coming from a +25.6% y/y jump in demand deposits against −1.1% in other liquid deposits: that is the signature of a **reclassification**, not of money creation, and it has not been reconciled against the Feb-2021 H.6 restructuring or the 2026 IRA/Keogh netting change **[rev-V, Review 2]**. Hold everything downstream of it. This is a strong negative finding and it should be reported as one.

**(b) Credit that funds spending without creating deposits. Operative, growing, and the correct description of this cycle.** When a closed-end private credit fund lends, it moves an existing deposit from the fund's investor to the borrower. No money is created. The boom is invisible to M2 **in principle, not merely in practice**. Outstanding private credit to AI-related firms has gone from near zero to >$200bn, ~8% of total private credit, with >$40bn originated in 2025 against ~$3bn in 2010 **[rev-V verbatim, BIS Bulletin 120]**. NBFI grew +9.4% in 2024, roughly double the banking sector.

**The point at which this re-enters genuine money creation is bank lending to non-banks**, and it is the only such point in the chain **[own, FRED LNFACBM027SBOG / H.8 line 26]**:

| | $bn |
|---|---:|
| Jul 2019 | 546.3 |
| Jul 2024 | 1,091.9 |
| Jul 2025 | 1,674.7 |
| **Jul 2026** | **2,005.5 (+19.75% y/y)** |

Against total bank credit **+6.21%** and total loans and leases **+7.24%** **[own]**. From 4.0% to 10.1% of US bank credit in seven years. And it is *definitionally excluded* from the BIS credit-to-GDP gap, which measures the private **non-financial** sector. Two disciplines: **nobody has decomposed how much of it is AI** — it also funds mortgage REITs, BDCs, consumer finance and insurers, and the honest position is "I do not know"; and the caveat one report attaches (a 2026 margin-loan reclassification breaking the series) could not be substantiated in the H.8 release notes, which carry only an April-2022 break **[rev-V, Review 2]**. Resolve that either way before using the series, and note that a second report uses the same series with no caveat at all.

**(c) Collateral-based purchasing power. This is the mechanism you are actually describing.** An asset re-rates; nothing is created; but the holder can now borrow against it. This is Kiyotaki–Moore, Geanakoplos and Brunnermeier–Pedersen, not any of the nine traditions. Where measurable, it is **not currently large**: broker-dealer receivables due from customers $622.2bn at 2026Q1 against $476.9bn a year earlier, **+30.5% y/y** against M2 +5.5% **[own]** — a fast growth rate on a level that is **0.90% of NFC equity market value, below the 0.95% of 2021Q4**. Securities-based lending, NAV loans, portfolio margin and bilateral repo are unmeasured. The honest statement: **the growth differential is the signal, the level is not alarming, and the unmeasured part is genuinely unmeasured — which is not the same as large.** The Soddy report's response to this failure ("the unmeasured part is exactly what a FIG structurer can see and public data cannot") is an appeal to unavailable evidence. It is also, in your specific case, a correct statement about where you should look with your own prime-brokerage data.

**(d) Pure discount-rate revaluation. No purchasing power created at all.** This is where the wealth actually came from, and it is measured by the Fed quarterly. Of the $39.16tn increase in US household net worth over 2023–25, **$31.40tn (80.2%) was net holding gains** ⚠ **[C-046, 22 Aug 2026: the "83.7% equity-linked" that stood here was marked *exact* and is not. "Equity-linked" is not a Z.1 category; it is a composite whose value turns on whether pension entitlements count as equity. Including them ≈83.7%, excluding them ≈61.7%. State the pension treatment or omit the figure. The $31.40tn / 80.2% parent figures are unaffected and stand.]** Cumulatively since 1995Q4, personal saving plus corporate retained earnings total $36.6tn against a $152.9tn rise in net worth — **24%**. Fagereng–Holm–Moll–Natvik reach the same order on Norwegian administrative panel data by a completely different route: "saving by holding" explains up to 80% of the rise in Norway's wealth-to-income ratio from ~4 to ~7. Rachel–Smith attribute ~300bp of the 450bp secular fall in global real rates to **non-monetary** factors.

**And the correction has already begun in the data.** Household net worth rose only **+$113.1bn** in 2026Q1 against **+$711.7bn of transactions** — implying revaluation plus other volume changes of **about −$599bn** **[own, TNWBSHNO and BOGZ1FU152090005Q]**. The mechanism is not hypothetical; it is running in reverse right now, in the latest published quarter.

**Verdict on your question as asked:** what is happening is (b) for the credit, (c) at the margin and small where measurable, and (d) for the valuations. (a) is not happening. **The illusion is real but it is a discount-rate artefact, not a monetary one** — and that is a *harder* problem, not a softer one, because a discount-rate revaluation can reverse without any sector defaulting on anything, and no monetary aggregate will move on the way down either.

---

## 4. THE ILLUSION-OF-WEALTH MECHANISM, FORMALISED

Ten links. **[E]** = established in the literature; **[C]** = contested; **[I]** = your inference, unmeasured.

**L1 [E, definitional].** Market capitalisation is the marginal transaction price multiplied by the entire inframarginal stock. It is realisable at that price only for the marginal holder. The gap between paper valuation and realisable value is not a measurement error — it is what the number means.

**L2 [E for the aggregate; NOT established for sectors; symmetry NOT established].** Gabaix–Koijen: $1 of net equity flow moves aggregate market capitalisation by ~$5 (NBER w28967). Three disciplines. (i) **There is no separate symmetry result.** Symmetry is a property of a linear model, not an estimated finding; if anything, funding constraints, dealer-capacity contraction and correlated redemptions argue the downside multiplier is *larger*, but that is a conjecture. (ii) **The estimate is aggregate-only.** The paper's logic is that aggregate demand is inelastic *because there is no substitute for the market*; a sector has substitutes, so the transfer is not licensed and the sign of the error is arguable. **No number of the form (ΔAI market cap) = 5 × (AI net outflow) is supported by the cited paper.** (iii) The one thing that partially rescues sectoral application is concentration: when the AI complex is a large fraction of index weight, index flows *are* AI flows. That is an argument, not an estimate.

**L3 [E — one accounting point, six vocabularies].** Aggregate realisation at posted prices is impossible. Inside financial assets net to zero across the private sector (Tobin 1969); revaluation is not a transaction (Godley); the exchange gives the individual but not the community the chance to revise (Keynes, GT p.135); the paradox of liquidity (Durand); "the capital does not exist twice over" (Marx III). Same proposition. Count it once. Scale: household equity plus mutual fund holdings ~$58.3tn against household money-like assets ~$20.5tn and M2 of $23.2tn — roughly **2.8× the money in which realisation would have to occur**.

**L4 [E — the discipline that most accounts omit].** **Non-realisability is not fragility.** An *unpledged* overvaluation deflates and hurts sentiment; nobody's covenant breaks. Household net worth was 615% of GDP in 2021Q3 and nothing broke. A ratio is context for a mechanism, never a substitute for one.

> ⚠ **C-024 — UNRESOLVED. The margin-debt ratio below is one of THREE conflicting figures for
> the same quantity** (0.90%, 1.756%, 1.84%), produced by three passes of this project, all
> claiming FINRA margin debt ÷ Z.1 NCBEILQ027S for 2026Q1, and disagreeing on the *sign of the
> conclusion*. Name the denominator and recompute once before using it. What is NOT in dispute:
> 12-month margin-debt growth hit **+53.7% into May 2026**, a top-ten expansion in a 355-month
> record whose other members are all bubble peaks — and it turned in July.

**L5 [E in structure; UNMEASURED in magnitude].** The conversion of a valuation into an obligation happens at **pledging**. The load-bearing quantity is: *what fraction of the relevant market capitalisation has been pledged, at what haircut, to lenders who will re-mark it?* That fraction is the part of the illusion that has been made contractual. Public reading (margin only): **0.90% of NFC equity market value**. Everything else is dark. **This is the one place where your desk sees something the public data cannot, and it is the highest-value measurement available to you.**

**L6 [E — Fisher 1933].** Debt is rigid and marked at face; collateral is state-contingent and marked at the margin. **They do not net in the state of the world where it matters.** This is the indispensable link and it is invisible to any representative-agent framework, because the mechanism is distributional — it runs through *which* balance sheets hold the loss and how levered they are, not through how large the loss is.

**L7 [C — genuinely contested].** Price decline → forced sale → further decline. The endogenous-haircut spiral is *not* settled: Krishnamurthy–Nagel–Orlov (JF 2014) find repo against private collateral was small pre-crisis and read 2008 as a dealer credit crunch, not a run; Gorton–Metrick reply that over half the repo market is unobserved. Neither side can close it. And von Peter's BIS model, built to reproduce Fisher's features, finds debt-deflation **stable** under large shocks and widespread default *provided unlevered agents will buy*. **Collapse is a conditional outcome, not an entailment.**

**L8 [E — but as mainstream corporate finance, not as Austrian capital theory].** The specificity wedge: realisable value falls below even the reduced market price for purpose-built assets, and the gap widens with specificity. A gigawatt single-tenant campus in rural Louisiana has a going-concern value that is a function of one counterparty's offtake and a liquidation value close to the shell plus the interconnect. The citations with actual estimated discounts are Williamson (1988), Shleifer–Vishny (1992), Benmelech–Bergman, Pulvino (10–20% for distressed aircraft), Campbell–Giglio–Pathak (~27% foreclosed homes), Mitchell–Pulvino (~10% on convertibles normally mispriced under 2%). Lachmann supplies the word "specificity"; these papers supply the number.

**L9 [E in structure; aggregate UNVERIFIED].** Residual value guarantees, offtake commitments and lease backstops are **written puts on collateral value**. They are the precise mechanism converting a private-credit mark into a cash call on an investment-grade balance sheet. Meta's 16-year RVG on Hyperion (~$27bn asset, ~90% LTV, rated one notch below Meta) is the disclosed reference case **[unver]**. The aggregate notional is not established — see §1.4 on the $662bn/$970bn provenance failure.

**L10 [E as identity; causal direction is a behavioural claim, not established].** The profit flow that validates the debt is itself roughly half a fiscal counterpart. In Kalecki's identity, a fiscal consolidation, a capex pause or a rise in household saving cuts profits one-for-one. **So the trigger need not be a sale.** The funding source and the funded asset are the same accounting object; that is what makes the structure reflexive rather than merely levered. Caveat: the identity is true by construction and cannot supply the counterfactual. dProfits/dDeficit = 1 is arithmetic, not a forecast.

### 4.1 Your sentence, made testable

This is the deliverable, and it was buried in an ideology-flag list in one of the nine reports rather than presented as the answer:

> **Conditional on X% of the relevant market capitalisation pledged at haircut H, a Y% price decline forces Z dollars of sales into a market of elasticity E, producing a further decline of Z/E.**

Every one of X, H, Y, Z, E is estimable. As written — "if someone actually pulled money out, valuations would collapse" — it has no threshold, no horizon and no counterfactual, and is worth nothing. Note also the accounting correction: **in aggregate nobody can pull money out.** Every seller has a buyer; the stock of securities and the stock of deposits are both conserved through the transaction. What is not conserved is the **price at which the marginal trade clears**. Reformulate around the price elasticity of the marginal clearing trade, not around the existence of exit liquidity.

### 4.2 Falsifiers, stated in advance

- **Von Peter's stability condition.** If the AI complex draws down ≥20% and haircuts across *unrelated* collateral classes do not widen, unlevered natural buyers were present and this was an expensive market, not a Fisher moment. **Observable within weeks of the event.**
- **The Jordà–Schularick–Taylor band.** Equity bubble × high credit = −13.1pp cumulative real GDP per capita over five years; equity × low credit = −7.9pp (insignificant); housing × high credit = −29.6pp **[rev-V]**. If an AI drawdown of >40% is followed by a path in the **−4 to −8pp** band, the credit channel was **not** load-bearing and the whole apparatus was applied to the wrong asset class. JST's crisis logit already says equity-bubble × credit is statistically insignificant post-WW2 (−0.07), while housing-bubble × credit loads 0.54***. Borio's own words: *"equity prices can be a distraction."*
- **The refinancing date.** Private credit maturities to AI borrowers average 4.7 years; hyperscaler 2025 issuance (>$100bn gross) was mostly beyond five years **[rev-V]**. The mechanical stress date is **2030–31, not 2026–27**. The constraint binds at refinancing, not on demand.

---

## 5. WHICH OLD MASTER EARNS HIS PLACE

Criterion: does it explain something the mainstream does not, that is measurable, and that is currently operative? Ruthlessly:

### Tier 1 — earns its place

**1. Kalecki.** The most useful tradition in the exercise and the only one that dissolves the puzzle rather than dramatising it. The profit equation explains why the household saving rate can be 2.7% while corporates fully self-fund: **the deficit is the saving.** Government net borrowing of ~$2.3tn/yr — 7.5% of GDP — appears in *no* monetary aggregate, *no* credit aggregate, *no* collateral-velocity measure and *no* FX-swap stock. Every one of your project's established null findings (M2 at NGDP pace, flat collateral velocity, ECB SFTDS against the liquidity windfall, FX-swap growth in hedging) is consistent with a very large funding flow existing, because none of those instruments would see it. And it supplies L10, the reflexivity. **Honest limit:** the identity is not a theory, the causal direction is a contestable behavioural assumption, and "capitalists' consumption" is unmeasured in the modern accounts so every applied version does something the original did not authorise.

**2. Godley (SFC accounting and the revaluation account).** Second because it tells you what is *not* happening, with the best data in the package. It supplies: the exhaustive Level-B identity that makes the question answerable at all; ΔNW = NetLending + Revaluation + OtherVolume, where the revaluation term is not a transaction and is unbounded relative to saving — the formal home of "wealth without saving"; the sectoral-balance falsifier (private domestic sector in surplus at +3.7% of GDP ⇒ this is not privately credit-financed); and the **measurement-error floor** that disciplines every other tradition's proposed channel. A tradition that supplies a floor below which nobody may claim to measure anything is worth more than a tradition that supplies a story.

**3. Wicksell — but only in its BIS descendant form (Borio–Disyatat–Juselius).** Two genuinely load-bearing contributions. (i) The saving/financing distinction, which is the correct answer to your premise and which loanable funds assumes away by construction — noting this is **one finding with one citation** shared by five traditions. (ii) The **leverage gap** (WP 569): during booms asset prices run ahead of credit, so the gap goes *negative* even as credit-to-GDP rises, and *"this also makes borrowers look deceptively solid in the boom phase."* That is exactly your collateral intuition stated as econometrics, and it is non-obvious. **Three hard caveats.** WP 569's estimated object is household+corporate credit against **real estate**, not NFC credit against an equity-inclusive index; rebuilding it on different variables and quoting the −10%/−20% thresholds transfers coefficients across a change of variable, and it matters *specifically here* because equity is the wrong asset class on JST's own evidence. The tradition's early-warning apparatus is currently **green** (US credit-to-GDP gap −11.5pp; debt-service ratio 14.1% and falling). And **Wicksell's own model contains no bust at all** — close the rate gap and the system rests at permanently higher prices. **The Wicksellian null for the AI trade is "valuations settle at a permanently higher level and nothing breaks," and the burden is on the collapse story to supply the extra mechanism.** State that null to yourself before every conversation about this.

**4. Fisher (not Soddy).** One indispensable link, L6. Rigid nominal claim against state-contingent, marginally-marked collateral; they do not net where it matters. Not in any representative-agent framework, and it is precisely your collateral-call intuition. **Limits:** Fisher has no theory of the boom — over-indebtedness is an asserted initial state, so anyone using him to date the top is using him for something he does not contain. And his transmission runs through the general price level via a quantity-theory link that is not operative in a fiat system with an elastic central-bank balance sheet. **Minsky's substitution of asset prices for the price level is the version that applies.**

### Tier 2 — earns one genuine observable each

**5. Schumpeter.** Contributes the correct reformulation — *"the AI trade is claim creation, of which money creation is a minority component"* — plus **autodeflation** (a boom invisible on the way up can still contract the aggregate on the way down, because repayment destroys deposits), plus the best single tracking ratio in the package (external-funding share of capex, from the 10-Q cash-flow statements). **Deductions:** he has no theory of asset prices and says so; no theory of rollover or refinancing; the headline test has an undefined 35–50% band with no completion criterion and no date; and his proposed aggregate — "claims-to-resources per unit of current output" summing SPV debt, undiscounted lease minimums, purchase obligations, guarantee notionals and undrawn commitments, divided by a flow — sums five measurement bases and divides by a sixth. That is the exact operation your rules forbid; any trend in it is a trend in the instrument mix.

**6. Cantillon and Thornton.** Earns one thing, and it is live and verified: **point of entry determines which prices move**, and this cycle's entry point is a narrow set of physically inelastic inputs. My Census computation in §2.2 is the demonstration. Thornton's specific addition beyond Cantillon is the correct disposal of your M2 question — money is a continuum with no natural boundary, the boundary is chosen by the statistician, and the relevant magnitude is *the flow of payments, not the stock of the thing.* **Deduction:** the modern version of the injection-point result is HANK and the QE portfolio-rebalance literature, and this tradition's best evidence is all modern papers. What the pedigree buys is the *negative* result — Cantillon states the neutrality condition explicitly and says it almost never holds — which is a corrective to a quantity-theoretic null nobody now defends.

### Tier 3 — vocabulary

**7. Mises and Hayek.** The composition-of-investment insight is correct and important: a dollar of 4-year GPU is not a dollar of 30-year structure, and duration determines both discount-rate sensitivity and recoverability. But **that result is delivered by my §2.1 arithmetic with no Austrian apparatus at all.** Against it: the one formal test the tradition has (stage-of-processing relative prices) **failed with the wrong sign** (Lester & Wolff, RAE 2013). Its own stated composite falsifier requires two measurements, **neither of which has been made** — so on the tradition's own rules it carries zero weight today. The "specificity wedge" is Williamson/Shleifer–Vishny/Benmelech–Bergman with estimated discounts; Lachmann supplies the vocabulary. And praxeological a priorism is a licence to ignore every test in the field.

**8. Gurley–Shaw / Tobin / Kaldor — split three ways.** **Tobin promotes:** q as the two-price gap, and the argument that when money's own rate is pinned the entire adjustment to any supply or preference change must run through other assets' prices. That is the correct account of 2009–2019 and it requires no money creation. Aggregate q **[own]**: NCBEILQ027S ÷ TNWMVBSNNCB = **1.819** at 2026Q1, against 1.943 at the 2025Q3 all-time high, 1.47 at the dot-com peak and a 1945–95 median of 0.66. *(Note: the Marxian report's proposed series MVEONWMVBSNNCB is discontinued at 2017Q4 and cannot be used — two sections reaching for the same object without noticing.)* **Gurley–Shaw earns a disconfirmation**, which is valuable: on its own metrics the near-money-manufacture story fails today (§3a). **Kaldor earns nothing here:** "loans create deposits" establishes direction, not quantity, and the horizontalist accommodation claim is unfalsifiable — Tobin's own 1963 constraint (agents have limited demand for bank liabilities) has never been answered by the accommodationists.

**9. Marx, Hilferding and fictitious capital.** Earns the least, and the report's own author says so: Ch. 29 *is* the Williams/Gordon dividend discount model, *"the alarm is not in the mathematics; it is in the adjective."* Promoter's profit is the marketability discount, priced daily in the private-versus-public multiple and formalised in DLOM practice; worse, the proposed computation (post-money valuation × founder ownership, minus capital contributed) marks an illiquid common stake at the price of the marginal *preferred* round and ignores liquidation preferences — the exact marking error the section elsewhere warns against. "The capital does not exist twice over" is standard sectoral consolidation. The one genuinely useful proposal — **chain double-counting**, supply-chain enterprise value over consolidated *external end-customer* revenue — is a look-through revenue test measured entirely with mainstream instruments (ASU 2022-04 supplier-finance disclosure, ASC 606 principal-vs-agent, related-party disclosure). Marx supplies the suspicion; GAAP supplies the measurement. Do the test; drop the framework.

**10. Soddy.** Should be a footnote to Fisher, and his equal billing is an artefact of how the brief was partitioned. Thermodynamics is a metaphor when applied to exchange value; the 100%-reserve platform is a policy platform, not a finding; "market capitalisation is a price, not a fund" is elementary and already stated in the same package by Tobin, Godley, Keynes and Durand. His one original contribution — pledging capacity — is Geanakoplos and Brunnermeier–Pedersen, and at the only point where it is measured it **fails** (margin loans 0.90% of equity market value, *below* 2021Q4).

### 5.1 The missing master, and the answer to your meta-question

**Kiyotaki–Moore (1997) is cited nowhere in nine reports built around the collateral loop.** The canonical model of exactly the mechanism you described — valuation → borrowing base → real spending → valuation, with collateral constraints and a formal amplification factor — is 1997 mainstream macro. So are Geanakoplos's leverage cycle, Adrian–Shin's procyclical leverage, Brunnermeier–Pedersen's margin spirals, Shleifer–Vishny's industry-equilibrium fire sales. **That absence is the strongest single piece of evidence against the premise that the older tradition has more purchase here.**

**So: does the older tradition have more purchase than the modern one? Yes, but asymmetrically, and the asymmetry is the finding.**

- **On the funding question — yes, decisively.** Kalecki and Godley beat the loanable-funds frame outright, and the modern restatement (Borio–Disyatat's financing-versus-saving) is Schumpeter 1911 in flow-of-funds language. The mainstream consensus genuinely does not have a place to record a $2.3tn/yr fiscal flow arriving on the corporate income statement, and it genuinely does treat prior saving as the constraint when the constraint is financing.
- **On the incidence question — yes, narrowly.** Cantillon and Thornton give you the point-of-entry result, and the data (§2.2) are unambiguous. The modern literature has rediscovered it, but the old statement is sharper because Cantillon states the neutrality condition negatively and says it never holds.
- **On the valuation and collateral question — no.** The modern literature owns it: Gabaix–Koijen for the multiplier, Kiyotaki–Moore and Geanakoplos for the loop, Shleifer–Vishny and Pulvino for the fire-sale discount with estimated magnitudes. **Four of the nine traditions explicitly say they cannot supply it** — Schumpeter ("weakest here and should not be stretched"), Wicksell ("has no theory of this"), Kalecki ("nothing to say about valuation"), Mises ("belongs to inelastic-markets work, not to the Austrians"). Four traditions honestly declining to answer your central question is not four traditions answering it.

---

## 6. WHAT THE EVIDENCE ACTUALLY SUPPORTS, IN ORDER OF CONFIDENCE

1. **There is no US corporate funding gap today.** Internal funds exceed capex by $325.7bn/yr; the sector is a net lender; the financing gap has been negative four consecutive quarters. Confidence: high, within a ±$0.7tn/yr measurement floor. **[own]**
2. **72% of the funding is depreciation, and 90% of the increase in gross capex was absorbed by depreciation.** The AI boom is small in net capital-accumulation terms and the whole thing turns on a useful-life assumption in a footnote. **[own]**
3. **The real resource reallocation is large, real, and invisible to every aggregate.** Private construction ex-data-centres is contracting 6.1% y/y while data centres grow 45.8%. **[own]**
4. **The wealth is a discount-rate artefact, not a monetary one.** 80.2% of the 2023–25 net worth increase was holding gains; the reversal has already printed (−$599bn of revaluation and other volume changes in 2026Q1). **[own + rev-V]**
5. **The credit channel is non-bank intermediation of existing deposits, re-entering money creation only through H.8 line 26** — $2,005.5bn, +19.75% y/y, undecomposed by everyone who uses it. **[own]**
6. **The illusion becomes an obligation only at pledging, and the pledged fraction is 0.90% where public data can see it and unknown everywhere else.** This is where your own desk data is worth more than the entire published literature. **[own]**
7. **The mechanical stress date is 2030–31, not 2026–27** — set by the maturity ladder, not by the technology cycle. **[rev-V]**
8. **BIS Bulletin 120's own stated conclusion, which five of the nine reports mine for figures and none reports:** *"While macroeconomic and financial stability risks from the AI boom appear moderate, the boom's sustainability hinges on AI firms meeting high earnings expectations."* And, four lines from a passage two reports do quote: the AI investment *rise* is *"half as large as the rise in IT investment during the dot-com boom of the 1990s."* **[rev-V, verbatim]**

**The honest bottom line: your puzzle partly dissolves, and the part that survives is sharper than the part that dissolves.** The funding question has a complete answer with no residual — depreciation, plus corporate retained earnings manufactured by a 7.5%-of-GDP deficit, plus a shrinking contribution from foreign saving. No money creation is required and none is observed. The valuation question is a separate question with a separate answer, because **a valuation is a price and prices do not require funding** — no quantity of saving is needed to mark $80tn of equity up or down, only the marginal trade. Conflating the two produces a search for a monetary residual that is not there. Separate them, drop the ZIRP scaffolding, and the thesis you are left with — inelastic markets, pledged collateral, rigid nominal claims against marginally-marked specific assets, and a profit flow whose source is fiscal — is both more defensible and more alarming than the one you started with.

---

## APPENDIX — CORRECTIONS APPLIED

| Claim in the source reports | Correction | Source |
|---|---|---|
| Net equity issuance "first positive since 2021Q1" / "first time" / "over a decade" | **First positive since 2021Q2**; 15 positive quarters since 2000 | **[own]** |
| Data-centre construction "$50.7bn SAAR Apr-2026, ~52% of office" | **$61,859mn Apr-2026 (55.6%); $68,297mn Jun-2026 (59.0%), +45.8% y/y** | **[own, Census C-30]** |
| Total bank credit "+6.5% y/y" | **+6.21%** | **[own]** |
| NFC debt "9.13% annualised, first quarter credit outran nominal GDP (+6.07% y/y)" | Bases mixed. Like-for-like **y/y: debt +4.64% vs GDP +6.07% — credit underran.** Annualised-quarterly: 9.13% vs 5.76% | **[own]** |
| `MVEONWMVBSNNCB` proposed as Foley's q | **Discontinued at 2017Q4.** Use NCBEILQ027S ÷ TNWMVBSNNCB = **1.819** | **[own]** |
| "$662bn signed-but-not-commenced leases (BIS via Moody's)"; "$970bn / $660bn (Moody's 2026)" | **No BIS provenance; zero hits in the full QR March 2026.** Almost certainly one trade-press figure under two attributions | [rev-V, R2] |
| MMF assets "~$7.93tn" | **$8,289.6bn (Z.1, 2026Q1).** $7.93tn matches no observation | **[own]** |
| Review 2's E3: leverage ratios "internally impossible" | **Review 2 is wrong.** 16.9%/25.6%/59.8% are the Fed's published FL104104016. Surviving error: pairing it with a self-computed 37.9% on a different numerator basis | **[own]** |
| H.8 NDFI "broken by a 2026 margin-loan reclassification" | **Unsubstantiated** — the release carries only an April-2022 break note. Resolve before use; a second report uses the series with no caveat | [rev-V, R2] |
| Gabaix–Koijen "5×, symmetric on the way down," applied to the AI complex | **No symmetry result in the paper** (symmetry is a model property). **Aggregate-only.** No sectoral number is licensed | [rev-V, R2] |
| Minsky: 2026Q1 NFC surplus "largest in the post-war record" | True on the series, but **inflated by the one-off IEEPA tariff-refund capital transfer** the Kalecki report flags for the identical quarter. Unreconciled between the two | [rev-V, R1+R2] |

**Not verified and not used as evidence anywhere above:** FactSet 9%→32% external funding share; Epoch AI firm-level FCF crossing dates; the $1.65tn Nikkei off-balance-sheet tally; Morgan Stanley's $2.9tn buildout decomposition; BDC gate percentages (ASIF 14.4%, HPS 13.3%) — the primary SC TO-I/A filings on EDGAR exist and nobody read them; stablecoin float ~$308bn; Goldman's $3tn/$4tn depreciation sensitivity.