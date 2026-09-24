# Grok external review — 22 August 2026

Independent attack on the eight load-bearing claims in `Review_Prompt_For_Grok.md`.
Today is 22 August 2026. Live sources named. A first pass against the 19 March 2026
Z.1 HTML was compared with the project's June 11 2026 vintage and reversed where
the older print had been treated as current. That error is recorded in §2 rather
than silently dropped.

No policy or trade recommendations. Agreement is omitted.

---

## 1. The hostile economist's first objection

**Falling household saving is not a funding puzzle. In the Kalecki–Levy identity and in NIPA Table 5.1 it is a source of corporate internal funds.**

The essay's opening sentence treats "a capex and valuation boom funded while the US aggregate household saving rate falls" as a mystery. Household saving is one sector's saving. Gross private saving rose from $4,815bn (2019) to $6,384bn (2025) (BEA via FRED `A126RC1A027NBEA`, annual, updated 28 May 2026). Domestic business saving rose from $3,023bn to $4,423bn (`W997RC1A027NBEA`, updated 9 Apr 2026). The composition shifted toward firms; the private-sector saving pool did not shrink. Lower household saving raises consumption, raises profits, raises internal funds, and makes the Z.1 financing gap more negative. The two facts presented as in tension are the same fact.

`Funding_Identity_First_Principles.md` already has this (Kalecki as the tradition that "dissolves the puzzle"; S4 as composition-not-level). The Grok prompt, and therefore the essay premise it is written to serve, still opens as if it does not. A competent economist who is not answered on this in paragraph one stops. What remains after the identity is answered is a *price* question — why valuations rose — not a funding-flow question.

Secondary stop, same paragraph: **"lowest since 2005" is false.** BEA Personal Income and Outlays, June 2026 (released 30 July 2026): personal saving $646.1bn, saving rate 2.7%. FRED `PSAVERT` confirms June 2026 = 2.7. It also shows June 2022 = 2.2 and July 2005 = 1.4, with many months in 2005–07 and spring 2022 below 2.7. The 2.7% print is real. The ranking is not. `2026-08-21-Singh-And-The-Two-Circuits.md` already has the correct rank (29th of 810 months, 28 strictly lower). The dead ranking still stands at `Funding_Identity_First_Principles.md:104`. Kill it. Say: back in the 2005–07 range, not a post-2005 low. (C-028.)

---

## 2. Five numbers that carry weight

### (i) Personal saving rate 2.7%, "lowest since 2005"

**Checked against:** FRED `PSAVERT` through June 2026 (updated 30 Jul 2026); BEA `pi0626.pdf`.

**Verdict:** 2.7% confirmed. "Lowest since 2005" false. See §1 and C-028.

### (ii) Financing gap negative four consecutive quarters; surplus ~$326bn/yr

**Checked against:** FRED `BOGZ1FA105005305Q` (updated 11 Jun 2026): 2025Q2 −$249,844mn, 2025Q3 −$252,822mn, 2025Q4 −$164,438mn, 2026Q1 −$634,910mn, all SAAR. Z.1 F.103, 19 March 2026 HTML, agrees on sign through 2025Q4 (Q2 −249.8, Q3 −253.4, Q4 −186.0; the June 11 vintage revises Q4).

**Verdict:** sign and four-quarter streak confirmed. $325.7bn is the 2026Q1 four-quarter-average identity in `Funding_Identity_First_Principles.md` §1.2 (internal funds $3,410.0bn − capex $3,084.3bn), not a free-standing flow. Averaging the four SAAR prints gives ~$326bn and is arithmetically the four-quarter sum of quarterly flows. **The average is pulled by 2026Q1 (−$635bn SAAR).** Drop that quarter and the remaining three average ~$222bn. The same section already flags a 2026Q1 capital-transfer (IEEPA tariff refunds) that inflates the surplus. Do not let "$326bn/yr" travel without the quarter and the transfer caveat.

The financing-gap definition (F.103 note 6) is capex minus (gross saving less net capital transfers paid **less foreign earnings retained abroad**). For US MNCs building abroad, that exclusion is not a rounding error.

### (iii) 72% of internal funds is CFC; gross +13.1% vs net +5.8%

**Checked against:** Z.1 F.103 and the named-window table in `Funding_Identity_First_Principles.md` §1.2 and §2.1.

**Verdict:** 72% is **2026Q1 SAAR**, not a 2025 annual. Internal funds `FA106000105` $3,410.0bn, CFC `FA106300003` $2,459.8bn = 72.1%. Confirmed on that date. The 2025 *annual* on the 19 March 2026 F.103 is different: capital consumption allowance $2,420.3bn / gross saving $3,163.6bn = 76.5%. Do not mix the two. The 72% figure is a single-quarter SAAR; 2026Q1 is also the quarter of the tariff-refund capital transfer.

Gross +13.1% and net +5.8% are **2023Q4 → 2026Q1** in the source table: gross fixed investment $2,849.6bn → $3,223.2bn (+13.1%); CFC $2,195.8bn → $2,531.6bn (+15.3%); net $653.8bn → $691.6bn (+5.8%). Ninety percent of the *increase* absorbed by faster depreciation follows from those three rows. The Grok prompt, and RESEARCH_STATE S2, stripped the window. 2024→2025 annual capex on the March F.103 is +4.1% ($2,956.1bn → $3,078.3bn) — a different object. **The computation is not from a cycle trough; it is from a nine-quarter window that the downstream documents stopped naming.** That is C-029: a named-window fact circulating as a free-standing percentage.

### (iv) Household net worth +$39.16trn 2023–25, $31.40trn (80.2%) holding gains

**Checked against:** Z.1 R.101, two vintages.

The 19 March 2026 HTML (2025Q4 release) prints change in net worth 2023+2024+2025 = $12,333.2 + $13,538.5 + $14,486.4 = **$40.36trn**, net holding gains $10,061.0 + $10,792.1 + $11,809.5 = **$32.66trn** (80.9%). A first pass treated this as current and called $39.16trn stale. That was the wrong vintage.

The **11 June 2026** release (2026Q1), which is the vintage the project actually used, revises 2025 down. `_research/old_masters_traditions.md` transcribes S.1.M.r: 2023 +$12,577bn / holding gains $10,087bn; 2024 +$13,482bn / $10,760bn; 2025 +$13,106bn / $10,549bn. Sum: **$39.17trn / $31.40trn = 80.2%**. `_research/safe_asset_lenses.md` reproduces the same on FL152090005 $143.702trn (2022Q4) → $182.867trn (2025Q4).

**Verdict:** direction and 80% share confirmed on the June 11 2026 vintage. Levels move ~$1.2trn across one quarterly revision. Cite the release date and series (`FC152090005`, `FR152090005`). A hostile reader who opens the March HTML will get a different number; that is not a kill, it is why vintage sits on the number.

83.7% "equity-linked" **cannot be verified** from R.101 line 11 alone. Direct corporate-equity holding gains plus mutual-fund-share holding gains on the March HTML are ~$22.9trn, about 70% of that vintage's holding gains, not 83.7%. Reaching 83.7% requires a defined bundle (pension entitlements, life-insurance reserves, equity in noncorporate business — say which). Do not ship 83.7% without the line numbers.

The 1995–onwards $36.6trn saving-plus-retained-earnings against $152.9trn net-worth rise: **cannot verify** from live FRED in this pass (thirty-year sum, own computation). Order of magnitude is plausible against household net worth rising from the mid-1990s to ~$183trn at 2025Q4 on the June vintage. Not a kill; not confirmed either.

### (v) 10-year TIPS −1.04% → +2.35%, +339bp; valuations did not revert

**Checked against:** FRED `DFII10` 20 August 2026 = 2.35% (updated 21 Aug 2026). −1.04 to +2.35 is +339bp. The 31 December 2021 print of −1.04 is the project's re-derived starting point (`2026-08-21-Singh-And-The-Two-Circuits.md`); this pass confirms the live end-point and the arithmetic, not the December 2021 tick from a full daily file.

**Verdict:** the yield move is confirmed. It does **not** kill a Gordon-model discount-rate account by itself. *P = D / (r − g)*: r rose, expected *g* can rise with it. Current profits are a bad proxy for expected *g* in an AI capex cycle. The three "did not revert" ratios are three different objects:

- Equity / four-quarter after-tax profits 27.42 → 29.57 (+7.9%) — a P/E.
- Equity / NFC GVA 4.277 → 4.276 ("flat to three decimals") — a capital/output ratio. Flat P/output with rising P/E is a profits boom, not a valuation boom.
- Tobin's q 1.7007 (2021Q4) → 1.8188 (2026Q1), +6.9%, with 2025Q3 at 1.9429 "highest of 304 quarters since 1945." This is Z.1 **equity q** (market value of equities / net worth), matching FRED `NCBCEPNW` 2025Q3 = 237.99% versus 2000Q1 = 165.84%. On *that* series 2025Q3 is a post-1945 high. Public-market Tobin's q as compiled by YCharts (market cap / replacement cost) is 1.943 at 2025Q3 and below the ~2.15 peak around 2000. **Name the series.** Shipping "Tobin's q, highest since 1945" against a reader who opens a replacement-cost q is how this number dies in the first referee report. `2026-08-21-Singh-And-The-Two-Circuits.md` already notes that the Z.1 denominator does not capitalise intangibles, so measured q drifts up as capital shortens. The arithmetic can be right and the overvaluation reading still not survivable.

### Other load-bearing figures, checked because they sit under the five

**Alphabet Q2 2026 FCF −$5.855bn.** Confirmed, SEC exhibit 99.1 (OCF $39,069mn − PP&E $44,924mn). Trailing-twelve-month FCF still **+$53,273mn**. Same quarter: **$49.6bn equity** (Class A, Class C, mandatory convertible preferred) plus **$20.3bn** senior notes. One negative quarter is not a regime change. The $49.6bn SEO is larger than the FCF hole and is the opposite of float retirement. Claim 1's caveat and claim 3's mechanism collide in the same 10-Q.

**Fed FSR runnable money-like liabilities $27,033bn, +12.0% y/y, 5.4% long-run average, repo +19.1%.** Confirmed, Financial Stability Report May 2026, Table 4.1, data through 2025Q4. Repo $5,887bn. Implied 2024Q4 repo ≈ $4,943bn (+$944bn); implied total 2024Q4 ≈ $24,137bn (+$2,896bn); 944/2,896 = 32.6% of the increase. Confirmed. Bond mutual funds ($5,032bn) are a memo line, not in the $27,033bn total — the table already says so.

**Hut 8 Beacon Point.** Base-term contract value $19.6bn over 15 years, $50.2bn if renewal options are exercised: confirmed, Hut 8 press release 20 July 2026. Notes: **$4.25bn** 6.129% senior secured due 2042, Moody's Baa2, non-recourse to the parent. "~$4.3bn" is fine. **Nvidia as tenant is Financial Times, 28 July 2026, five people; neither company has confirmed.** Do not write it as fact. S10 currently does.

**Meta RVG language.** Confirmed verbatim, 10-Q through 31 March 2026: "RVG payments are not probable, and therefore no liability has been recorded to date." Also disclosed on the same footnote, and more useful than Hut 8: maximum exposure to that VIE **$45.99bn** at 31 March 2026, RVG threshold **~$28bn**, aggregate initial lease commitment **$12.31bn**, leases commence 2029. Contingent guarantees are invisible in Z.1. They are not unmeasurable. Meta has printed the number.

**Greenwald–Lettau–Ludvigson 40.2% / 14.3%.** The *JPE* 2025 (133(4):1083–1132) abstract rounds to **40%** factor-share and **14%** interest rates, for **1989–2017**. 40.2 / 14.3 is likely an unrounded table cell; the window is not. Importing a 1989–2017 *contribution share* as the 2021–26 mechanism is failure mode (b). The same abstract gives **21%** to a lower risk price. That term is the natural candidate for "why multiples did not compress when real yields rose," and it is omitted.

**Net equity issuance −$1.90trn, 2022Q1–2025Q4.** FRED `NCBCEBA027N` (annual): 2022 −$584bn, 2023 −$611bn, 2024 −$398bn, 2025 −$304bn. Sum **−$1.897trn**. Confirmed as a four-calendar-year sum. The series includes cash-financed M&A retirements, not only buybacks. F.103 line 54 (net equity issues, including FDI equity) is already **+$141.3bn in 2025Q4**. The 2026Q1 print in the funding-identity note is **+$124.4bn SAAR**, first positive quarter since 2021Q2. Alphabet's $49.6bn SEO is 2026Q2. If −$1.90trn is a mechanism for 2023–25, it needs a stop date.

**"$182bn IG YTD against $690–800bn of 2026 capex."** Fitch H1 2026 list circulating as $182bn is Amazon, Alphabet, Nvidia, Meta, Oracle, **SpaceX** — Microsoft absent; SpaceX and Nvidia are not hyperscalers in the capex sense used for the denominator. Goldman Sachs / Reuters: about **$194bn through 7 July 2026** for Amazon, Alphabet, Meta, Oracle; Goldman full-year hyperscaler capex ~$750bn; Moody's six-firm (adding Oracle and Nvidia) ~$785bn. Firm set and YTD cutoff mismatch. Treat $182bn as a Fitch H1 print with a named issuer list, not "six hyperscalers YTD."

**Singh velocity 3.0 (2007) → 1.8 (2015).** Confirmed, IMF WP/17/113 Table 1 (end-2015 velocity 1.8; 2007 = 3.0). The ZIRP-window sign test (velocity down, S&P up) is the better attack. A string-search for "asset price" / "equity price" / "stock price" across five PDFs was not re-run in this pass. WP/17/113 discusses equities as collateral and long-term rates as set in the pledged-collateral market. Do not rest "Singh does not carry the collateral-velocity story" on a string-search.

**Gorton–Lewellen–Metrick intercept 0.332, s.e. 0.003.** Confirmed, *AER* 2012 Table 1, 239 quarters, R² = 0.012 on the high estimate. The standard-error critique is right: 0.003 is the intercept's, not the share's dispersion. Current share 27.5%: **cannot verify** (own reconstruction; two internal reconstructions already disagree by ~21pp on the market-valued fraction of the denominator). The publishable residue named in K4 — revaluation as a share of the denominator's change, 18.1% → 49.2% → 66.6% — does not need 27.5% to stand.

**BIS +$2,040bn claims / +$1,650bn liabilities / $391bn residual, Japan 47%.** **Cannot verify** from the published BIS July 2026 narrative release, which gives Q1 2026 USD credit **+$793bn**, not a multi-year stock residual. Keep only with a dated SDMX query a hostile reader can rerun. Drop from the essay until then.

**Hedge-fund repo +$882bn; relative-value +70.7%.** **Cannot verify** the exact figures from public tables in this pass. Dallas Fed (28 May 2026): hedge-fund *net* repo roughly $1.8trn by end-2025, more than double since the start of 2024 — same *order* as the FSR repo increase. Form PF and FSR Table 4.1 are different bases. Already flagged internally as not an attribution share. Keep the flag.

---

## 3. Failure modes in the prompt itself

**(a) Reading a normalised statistic as a quantity.** GLL's 40.2% is a contribution share on 1989–2017, used as if it measured 2023–25. GLM 27.5% "outside the band" is a ratio on a reconstructed share, then asked to speak to a safe-asset *shortage*. Repo +19.1% and 32.6% of the *increase* are growth-contribution shares; those are labelled more carefully than GLL.

**(b) Category errors.** Household saving rate, corporate internal funds, and gross private saving are three objects under one "puzzle." Equity/profits, equity/GVA, equity-q (`NCBCEPNW`), and replacement-cost q are four valuation objects under one "did not revert." Fitch $182bn "hyperscalers" mixes SpaceX and Nvidia and drops Microsoft. Internal funds (`FA106000105`), F.103 gross saving, and financing-gap internal funds (which exclude foreign earnings retained abroad) are three denominators for "72%." 2026Q1 SAAR versus 2025 annual is a fourth.

**(c) Citation cascade.** Not new in this block. "Singh's five papers never say asset price" plus "the formal model puts collateral in the LM curve" is one framework, not five independent confirmations that Singh is silent on asset prices.

**(d) A refuted figure still circulating.** "Lowest since 2005" will be the essay's first sentence if C-028 is not propagated. The 5.8%/13.1% pair will float free of 2023Q4–2026Q1 (C-029). C-001 ($662bn leases) is marked propagated; do not revive an aggregate lease figure from Hut 8 plus Meta footnotes. Sum company-level lines, or do not sum.

The composition hole inside claim 1 is already self-flagged and still underweighted. Z.1 S11 NFC capex misses SPV/JV build (Blue Owl / Chirisa / PowerHouse for CoreWeave; Meta Hyperion VIE). If that capex is classified financial, "no aggregate funding gap" is a sectoring artefact. Direction of bias is known. Magnitude is still unknown. That is the assumption that inverts S1.

---

## 4. A live mechanism not on the list

The listed set is bank credit, offshore dollars, repo and reuse, money-like liabilities, private credit, securitisation, insurance and annuities, FX swaps, stablecoins, margin and prime, contingent guarantees.

Two channels materially moving in 2025–26 that are not on that list:

**Public dissaving as the counterpart of the private surplus.** NIPA: private saving − investment ≈ (T−G) + current account. The fiscal deficit is the on-balance-sheet residual of "where did the funding come from." FSR Table 4.1 government MMFs $6,375bn, +13.1% y/y, are largely a Treasury-bill demand story. `Funding_Identity_First_Principles.md` already has general government net lending −$2,293.5bn average across 2025. The Grok prompt's channel list does not. A hostile reader will insert it.

**Project-finance JVs booked outside NFC.** The SPV hole, now live in 2025–26 issuance: Blue Owl / Chirisa / PowerHouse construction loans and lease-backed paper for CoreWeave; Meta/Blue Owl Hyperion. Same economic object as claim 6, in a sector that never hits F.103 capex. This is not a new *idea*. It is the 2025–26 quantity that S1 is waiting on.

Not missed, mis-sized: created creditworthiness is already in 10-K footnotes. Meta's $45.99bn maximum VIE exposure is public. Skipping the footnote stack for Form-PF-dark corners is the retreat §5 names.

Equity SEO (Alphabet $49.6bn) is a 2026 flow that reverses float retirement. If the essay uses −$1.90trn as a 2023–25 mechanism, it needs a 2026 stop date.

---

## 5. Verdict on the thesis

**"The wealth is not real and will not survive being tested" is not supportable as stated.**

What is supportable: most of the 2023–25 net-worth *change* is holding gains — $31.40trn of $39.16trn on the 11 June 2026 vintage. That is how wealth is measured in Z.1. "If a large fraction were sold, prices would fall" is Gabaix–Koijen inelastic markets, and it was true in 2019. It is not an illusion finding. Revaluation is not fake money. It is a price.

Identified credit against listed equity is not the fragility. Agreed. That is a negative result. Leave it as a negative result.

The remaining list — securities-based lending, NAV loans against model-marked private assets, portfolio margin, internalised synthetic prime — is exactly the set public data cannot size. **Yes: that is a retreat to the unmeasurable after the measurable did not cooperate**, unless the next pass actually sizes the footnote stack that *is* measurable (RVGs, VIEs, leases not commenced, remaining performance obligations, take-or-pay GPU offtake). Contingent guarantees are not "invisible by construction" once Meta has printed $45.99bn of maximum exposure. Invisible in Z.1 is not unmeasurable.

One well-documented Hut 8 lease is a mechanism illustration, not a system. Nvidia as tenant is still an FT report. Meta's VIE footnote is the start of a dataset.

The honest sentence the essay can currently defend: *most of the recent rise in household net worth is a revaluation; identified leverage against listed equities does not look like the 2000 or 2007 pledged-fraction story; the new credit-like object is rented investment-grade creditworthiness sitting in lease, offtake and residual-value footnotes; whether that object is large enough to be the test of the wealth is a 10-K summing exercise that has not been done.* That is narrower than the operator's original sentence. It is also not a retreat.

---

## 6. What to measure next (all public)

1. **BEA Table 5.1**, 2019–2026Q2: household, business, and government gross saving. Kills or reframes the opening sentence. Thirty minutes.
2. **Named-window recompute of F.103** on the 11 June 2026 vintage: CFC share (state whether 2026Q1 SAAR or 2025 annual), gross versus net fixed investment (print 2023Q4 and 2026Q1), financing gap with and without 2026Q1. Thirty minutes.
3. **Hyperscaler 10-K/10-Q footnote stack** — VIE maximum exposure, RVG thresholds, leases not commenced, remaining performance obligations / committed capex. Company-level. No aggregate without provenance. This is S10 done as a dataset rather than an anecdote. Meta's $45.99bn is the template.
4. **Name the q series** (`NCBCEPNW` / Z.1 equity q versus replacement-cost q) and recompute 2021Q4 → 2025Q3 against 2000Q1. One series, one sentence.
5. **GLL out of sample, 2018–2026.** Do not import 1989–2017 shares into a 2023–25 paragraph. If it cannot be done cleanly, drop GLL from that paragraph. Keep the 21% risk-price term if any decomposition is used.
6. **Form PF repo at the two FSR dates** (OFR Hedge Fund Monitor), labelled as a different basis from Table 4.1. Order-of-magnitude only.
7. **Call Report RC-C M.10** borrower split of the bank-to-NBFI line. Already on the internal list; still the right next credit measurement.

The overdue `CALENDAR.tsv` row (17 August RTO filings) is not closed by this review.
