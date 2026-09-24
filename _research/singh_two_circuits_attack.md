# Adversarial pass — Singh / two circuits

## ADVERSARIAL VERIFICATION — FINDINGS

**Headline: one lens's central finding reverses under re-derivation, and it is the finding that would have closed the project.** Lens 6's "ZERO multiple expansion (−1.3%)" — the claim that removes the explanandum both rival theories exist to explain — is a basis mismatch. Corrected, the residual is 40.7% of the log move and the discount-rate account cannot claim it.

---

## (1) FALSE CONSENSUS

**A. The multiple-expansion reversal — mismatched bases (CRITICAL).**
Lens 6 divides `NCBEILQ027S` (**non**financial corporate equity) by `CPATAX` (**all** corporate profits after tax, including financial corporations and rest-of-world receipts). Both are "without IVA and CCAdj", so sector coverage is the *only* difference. Re-derived from FRED against the matched series `NFCPATAX` (BEA A466RC, NIPA Table 1.14):

| 2021Q4→2025Q4 | Lens 6 (mismatched) | Matched |
|---|---|---|
| Equity | +32.43% | +32.43% |
| Profits | +34.13% | **+18.12%** |
| **Multiple** | **−1.26%** | **+12.12%** |

Log split on matched bases: profits 59.3%, **multiple expansion 40.7%** (reconciles exactly, 0.28091). CPATAX grew 34.1% while nonfinancial profits grew 18.1%; that 16pp wedge is financial-sector and foreign profit, and it flows entirely into a spurious "prices tracked profits" result. Lens 6's arithmetic is internally correct at every step (I reproduced 20.19, 14.98, 9.68, 19.93, 19.18 to the decimal) — the error is the denominator. **This violates the project's own "never sum across measurement bases" rule.**

Steelman preserved: Lens 6's *deeper* point survives and is strengthened. The multiple rose 12.1% into a **+339bp** real-rate normalisation. A discount-rate account predicts a sharp fall. So the residual is both larger than Lens 6 said *and* unavailable to the discount-rate story.

**B. Collateral velocity ≈ 2.0 is one man's unreplicable estimate, cited by three lenses.** Lenses 1, 2 and 3 all report it. Lens 3's entire 2007–2017 series is a single table (WP/19/106 Table 2). All three concede the denominator (source collateral) is not observable from any primary source. Three lenses reporting the same number is not triangulation.

Worse, Lens 2's headline — *"flat on every measurement system with a defensible denominator"* — mixes three incommensurable objects: Singh's chain-length-like ratio (2.0), the ECB's **share of transaction volume** on reused securities (11.63%), and a dealer **single-step repledge share** (79.2%). A 79.2% single-step repledge rate implies a naive geometric chain of ~4.8, not 2.0. The ECB's own chain length (2.95/3.05) is *higher* than Singh's 2.0 and its authors say chains have **rebounded to pre-Lehman levels** — which contradicts "flat," rather than confirming it.

**C. Lens 1 and Lens 2's dealer aggregates are the same 10-K footnotes read twice, and the headline rests on one bank.** Lens 2 states it "independently reproduces the register's $6,907bn / +23.9% claim exactly" — that is reproducing the register, not an independent source. Both lenses label a sample "four dealers" and report **opposite signs**:

- Lens 1 (JPM+GS+MS+**BAC**): 84.0% → 82.7%, **down 1.3pp**
- Lens 2 (JPM+**WFC**+GS+MS): 78.6% → 79.2%, **up 0.6pp**

Both are reconcilable — the whole down-move is Bank of America (95.3% → 90.9%). Remove BAC and reuse intensity **rises**. And BAC is the one firm Lens 1 flags as disclosing only to 1dp in trillions (~$1.1trn, ±$50bn). That rounding alone swings BAC's ratio ~8pp and the five-firm ratio ~1.3pp — **larger than the 0.5pp change being reported**. Lens 2 quotes BAC as "$1,100.0bn" inside a "$6,906.97bn" total: false precision to the nearest $10mn on a figure known to ±$50bn.

**D. Gabaix–Koijen $5 applied three times to overlapping flows.** Lenses 4, 5 and 6 each multiply a different flow by the same single coefficient from one paper. GK estimate it on **aggregate net equity flow**; margin-financed purchases, buybacks and NBFI-funded buying are all *components* of that flow. Lens 5 multiplies margin (~33%) and buybacks (~27%) separately and adds to 60% — **double-counting through one elasticity**. Add Lens 4's NDFI channel and you exceed 100% of the market-cap gain.

The apparent range "11%–33%" is a denominator artefact, not uncertainty: Lens 4 uses $15.8trn (all domestic corporate equities, 4 quarters); Lens 5 uses $4.243trn (nonfinancial only, 3 quarters). Same method, 3x different answer.

**E. GLL + Farhi–Gourio.** Lenses 3 and 6 both cite the same GLL table (40%/14%) as if independent. The claim "discount rates were never the main story" — the pivot of the whole synthesis — rests on essentially two papers, and GLL's own credible set for the risk-price term spans zero.

**F. The paywalled Risk.net piece.** Lenses 1 and 2 both cite it, neither read the body, and both offer the *same* JPM $1.8trn cross-check as evidence of faithful extraction. They also give different titles ("vanishing" vs "disappearing") — neither opened it.

---

## (2) NUMBER CHECK — seven re-derived

**❌ FALSE — personal saving rate (Lens 5, marked `verified_this_session`).** Claim: "2.7% Jun-2026, **third-lowest** of 810 monthly observations — the only lower readings are 2005-07."
FRED `PSAVERT`, full history: **28 of 810 months are strictly lower; three more are equal. It ranks joint 29th, not third.** Lower readings occur in 2005 (11), 2006 (5), 2007 (7), **2008 (2)** and **2022 (3)**.
This does not merely dent the number — **it destroys the inference.** June 2022 was **2.2%**, materially lower, during a goods-inflation spike with equities down ~19%. A low saving rate coincided with *falling* asset prices. That is a direct counter-example to reading the saving rate as a wealth-effect leak, and Lens 5's headline evidence for the leak is the "only the previous asset boom was lower" framing, which is false.

**⚠️ CONFIRMED BUT BROKEN BY A REPORTING BREAK — NDFI lending.** FRED `LNFACBM027NBOG`: Jul-2019 $548.3bn → Jul-2026 $2,009.7bn; y/y **+19.68%** (operator: +19.75% ✓).
But the H.8 notes (federalreserve.gov/releases/h8/h8notes.htm) document a Dec-31-2024 reporting clarification, phased through 2025, reclassifying **$113.5 + $53.9 + $41.7 + $9.1 = $218.2bn into NDFI**, with **no historical adjustment** — an explicit discontinuity from 2025-01-01. So **$218.2bn (14.9%) of the $1,461bn seven-year rise is reclassification, not lending.** The y/y survives largely intact (~$9.1bn contaminated); the 2019→2026 level comparison and the "4.0%→10.1% of bank credit" claim need a ~15% haircut.
**Lens 4's CANNOT ESTABLISH #8 explicitly says "The 2019Q1-to-2026Q2 comparison, which is the one I lean on, spans no known break." That is now falsified.**

**⚠️ OVERSTATED — Lens 4's 40.9%.** Lens 4 built "other loans and leases" as a **residual** (+$472.3bn) when the direct NDFI series exists. Direct: NDFI grew **$330.4bn = 28.6%** of marginal bank credit, not 40.9%. Using a residual and headlining the larger number, when the published series was available, is the first thing a hostile reviewer will find. (Also mixes SA `LOANINV` with NSA NDFI.)

**✅ VERIFIED — Tobin's q (Lens 5).** `NCBEILQ027S/TNWMVBSNNCB`: 2025Q3 **1.9429**, 2026Q1 **1.8188**, 2021Q4 **1.7007**, 2000Q1 **1.4673**. All match to 4dp. *But see §6 for why the interpretation fails.*

**✅ VERIFIED — FINRA margin debt.** Jul-2026 $1,417,225mn, **+38.6% y/y**, series max $1,502,072mn. Independently confirmed.

**✅ VERIFIED — ECB WP 3147.** Confirmed at ecb.europa.eu: 11.6% of European repo volume on reused securities, >€49bn/day, and **"contrary to the liquidity windfalls hypothesis, dealers do not seem to systematically obtain extra liquidity through collateral reuse in repos."** Lens 2 reported this accurately. It is the best evidence in the corpus.

**⚠️ SAMPLE ENDS 2005 — Bezemer, Ryan-Collins, van Lerven & Zhang.** Confirmed: **1973–2005**, 17 economies, credit/GDP 60%→100%, business share 60%→40%. It is cited in the project's *core established facts* to characterise 2026 — a **21-year extrapolation**. And the shift they document is toward **real estate and household credit**. The operator's phenomenon is **equities** (83.7% of holding gains). The entire "debt shift" evidence base (Bezemer et al; JST "Great Mortgaging"; Favara–Imbs elasticity 0.12) measures mortgages. It does not transfer to equities.

---

## (3) THE LEAK OBJECTION — not met, and now positively refuted

Only Lens 5 engages, and it **concedes** the leak. Judged harshly, its three pieces of evidence are:
1. **$841bn/yr** = a transplanted 3.2c MPC × a stock. An assumption times a stock, self-flagged as "a scaling exercise, not an estimate."
2. **The saving rate** — now shown false as stated, and with a 2022 counter-example running the wrong way.
3. **Core services +30.3% vs core goods +16.2%** — consistent with the leak, equally consistent with shelter and wage catch-up. No counterfactual.

**The decisive number Lens 5 could not retrieve, I retrieved.** CBO (publication 58914): realised capital gains peaked at **8.7% of GDP in 2021**, projected to a long-run **3.7% of GDP**. At $32.5trn GDP that is **~$1.2–2.8trn per year** of holding gains converted to cash in taxable accounts — against ~$10.5trn/yr of net holding gains, a **12–27% annual realisation rate**, an order of magnitude above the wealth-effect estimate. CBO explicitly attributes raised individual income tax projections to higher asset values driving realisations.

**So the claim that circuit money "is never anyone's income and never becomes anyone's income" is factually wrong.** Realised gains *are* income, are taxed as income, and the Treasury collects on the leak. The objection is not met by anyone in the corpus, and the primary evidence runs against a sealed circuit.

**Additionally, the premise is wrong for the stated period.** "Financial assets inflate while goods prices do not" does not describe 2021–2026: US headline CPI peaked at 9.1% in June 2022 and core goods rose 16.2% since Dec-2019 (against roughly flat 1995–2019). The puzzle exists for 2009–2019 — where Lens 3 found the collateral circuit ran *backwards* — and possibly 2023–2026, a ~3-year window with nothing identified.

---

## (4) THE DISCRIMINATING TEST — nobody supplied one, and the thesis has a built-in excuse

**No lens supplied an observation that separates the two accounts.** Every US number in the corpus is composition or co-movement; the only identified estimate (Favara–Imbs, 0.12/0.2) is housing, 1994–2005.

Worse, the natural experiment **has been run and returned null**: the Reg T margin-requirement literature finds no economically significant effect of margin regulation on stock prices or volatility. And the literature's own explanation for the null is **substitution** — investors move to unregulated leverage channels.

That is fatal in a specific way. The circuit thesis can absorb *any* null result by invoking migration — exactly as register C-015 invokes migration into CCP netting to explain flat velocity, and exactly as Singh's Jan-2026 "digital curtain" invokes intraday tokenised reuse to explain why the metric no longer works. **A theory whose central quantity is unmeasurable in principle and which explains every negative result by measurement migration is unfalsifiable.**

**Recommendation: do not publish a financial-circuit causal claim.** What *can* be published is the corrected §1A measurement finding, which is genuinely new and does not require the circuit thesis.

Tests that would discriminate, none yet run:
- **Cross-section on pledgeability**, holding cash flows fixed — identical credit risk in repo-eligible vs non-eligible wrappers. The circuit account predicts divergence; the discount-rate account predicts none. This is the only Singh-sanctioned route (the pledgeability premium, WP/21/94) and it predicts effects on **government bonds**, not equities.
- **Financing-capacity shocks orthogonal to rates**: the April-2020 SLR exemption and its March-2021 expiry; the Treasury clearing mandate. Prices moving on capacity news with no rate move would give the circuit account content.
- **The level-persistence test**: does the multiple fall when financing capacity is withdrawn, controlling for rates? 2022 is not clean — margin debt and rates moved together.

---

## (5) WERNER — the lens got the conclusion right and the evidence base badly wrong

I obtained and read Clavero (2017, MPRA 76657) in full. Three findings:

**A. "The QTC literature" is one author.** Lens 4 presents Clavero's Table 3 as *"Inverse velocities reported across the QTC literature… Mean 0.585."* Every one of the seven rows has **Werner as an author**: Werner (1997), Voutsinas & Werner (2011), Werner (2012), Lyonnet & Werner (2012) **×2 rows from the same paper**, Ryan-Collins Werner & Castle (2016), Werner (2014). Seven rows = **six papers, three countries, one author.** The Czech study is Bezemer & **Werner** (2009). There are **no independent replications** of the QTC's parameter. And a 0.432–0.709 spread (64%) in a parameter the theory says is stable is not a consensus — it is the diagnostic failing.

**B. Clavero's "additional empirical support" is an accounting identity.** He averages Werner's own estimates to ~0.6, then argues C_R/nGDP = 0.6 ≤ C/nGDP because C_R ⊂ C, and concludes "Fig. 3 shows that this relationship is not violated in the data, which provides additional empirical support for the quantity theory of credit." **This cannot fail by construction.** A competent economist will destroy it on sight. Do not cite it.

**C. Clavero's own verdict undercuts Lens 4's use of him, and cuts both ways.** He concludes the theory "is in the stage of maturation, and there is a long way to go," and hopes future work will "eventually get to velocities that oscillate mildly around a constant trend line" — conceding they currently **do not**. He also says proxy construction is "arduous and open-ended" and that **mortgage lending should be included** in the real circuit. That means Lens 4's "Werner-faithful proxy that EXCLUDES real-estate lending" is *not* Werner-faithful on the literature's own reading, and Lens 4's headline that "Werner's own falsification test fails on US data" is weaker than presented — you cannot cleanly falsify a test whose proxy nobody knows how to construct. Lens 4 half-concedes this in the mechanism section but states it as clean in the hook.

**D. Confirmed: no one has ever estimated the asset-price leg.** Clavero defines C_F only as a residual (C_R = C − C_F) and estimates no asset-price equation; asset prices appear solely in literature-review prose. Lens 4's CANNOT ESTABLISH #1 is correct and should be promoted to the headline. The defensible result is the **nominal-GDP leg only**, and even that rests on six Werner-authored papers on three countries. The independent work (Bezemer, Grydaki & Zhang 2016) confirms the **growth** asymmetry, not the asset-price leg.

---

## (6) PUBLICATION RISK — claims that would not survive

**Would not survive, must be fixed or dropped:**

1. **"Zero multiple expansion / the residual is close to zero"** (Lens 6). Basis mismatch; reverses to +12.1% and a 40.7% residual. *Highest-severity item in the corpus.* Any economist with FRED will find this in ten minutes.
2. **"Third-lowest saving rate since 1959, only 2005-07 lower"** (Lens 5). False; joint-29th; 2022 is a counter-example that inverts the inference.
3. **"40.9% of marginal bank credit"** (Lens 4). Residual used where a direct series exists; correct figure 28.6%. Plus SA/NSA mixing.
4. **"The 2019Q1–2026Q2 comparison spans no known break"** (Lens 4). Falsified by the Dec-2024 H.8 reclassification; $218.2bn.
5. **Margin-debt and buyback contributions summed to ~60%** (Lens 5). Double-counts one elasticity across overlapping components of the same flow.
6. **"Inverse velocities across the QTC literature, mean 0.585"** (Lens 4). It is one author's six papers. Reword or drop.
7. **Tobin's q "highest of 304 quarters since 1945"** (Lens 5) — arithmetic correct, interpretation not survivable. The Z.1 denominator **does not capitalise intangibles**, so measured q drifts up mechanically as intangible capital grows. Lens 5 cites Gutierrez–Philippon on intangibles explaining a third of the investment gap **in the same report** and then treats an intangibles-uncorrected q as evidence of record overvaluation. The project's own established facts point the same way: 72% of internal funds being depreciation, and 90% of gross capex growth absorbed by faster depreciation, is the signature of a shift to short-lived intangible/IT capital. The Minsky puzzle ("q of 1.94 should call forth investment; it doesn't") is largely answered by mismeasurement.
8. **"$6,906.97bn"** (Lens 2). False precision — one of six components is known only to ±$50bn.
9. **Bezemer et al. used to characterise 2026.** Sample ends 2005; measures mortgages, not equities.
10. **Damodaran's "required return rose 266bp"** (Lens 6). Near-circular: his terminal growth is hard-coded to r_f, so the terminal value is near-invariant to parallel r/g shifts and a rate rise mechanically lifts the implied discount rate. Lens 6 flags this in CANNOT ESTABLISH #1 but headlines the number anyway. The caveat must travel with the claim or the claim must go.

**Would survive:**
- ECB WP 3147's null on liquidity windfalls — verified at source, correctly characterised, and a genuine direct test.
- Singh's zero hits for "asset price" across five papers, and his LM-curve placement (output, not valuation).
- The ZIRP-window direction: collateral contracted 39% and velocity fell 40% while the S&P rose 52%.
- FINRA margin debt +38.6%; NDFI +19.68% y/y; Tobin's q arithmetic; the dealer 10-K footnote levels.
- The corrected §1A finding — **that** is the publishable result.

**One scope correction the synthesis should carry:** the ECB null kills *collateral-reuse-as-money-creation* (Singh/Infante free-cash wedge). It says nothing about *bank-credit-to-NBFI-as-asset-demand* — which is the version Lens 4 actually specified and which the NDFI data speaks to. Lens 2 over-claims when it calls the windfall test "the mechanism the financial-circuit thesis would need." The corpus has refuted one mechanism and **never tested the other**.

---

### Bottom line on the assignment's central question

The prior synthesis's "discount-rate artefact, not a monetary one" **needs qualifying, but not in the direction the operator expected.** The corrected data says the 2021–2025 move was ~59% profits and ~41% multiple expansion, and the multiple expanded *into* a 339bp real-rate rise — so the discount-rate account fails on sign. That residual is real and is larger than any lens reported. But nothing in six lenses establishes that a collateral or credit circuit occupies it: the collateral-reuse mechanism has been directly tested and found absent, the credit-to-NBFI mechanism has never been tested, the leak is measured in federal tax data at $1.2–2.8trn/yr, and no discriminating observation has been proposed. **Publish the measurement. Do not publish the mechanism.**

Working files: `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/` (`psavert.csv`, `LNFACBM027NBOG.csv`, `nfcpatax.csv`, `CPATAX.csv`, `NCBEILQ027S.csv`, `TNWMVBSNNCB.csv`, `clavero.txt`)

Sources: [FRED PSAVERT](https://fred.stlouisfed.org/graph/fredgraph.csv?id=PSAVERT) · [FRED LNFACBM027NBOG](https://fred.stlouisfed.org/series/LNFACBM027NBOG) · [FRED NFCPATAX](https://fred.stlouisfed.org/series/NFCPATAX) · [Fed H.8 notes](https://www.federalreserve.gov/releases/h8/h8notes.htm) · [ECB WP 3147](https://www.ecb.europa.eu/pub/pdf/scpwps/ecb.wp3147~6c60cabb50.en.pdf) · [Clavero MPRA 76657](https://mpra.ub.uni-muenchen.de/76657/) · [Bezemer et al., SER 21(1)](https://academic.oup.com/ser/article/21/1/437/6329985) · [CBO 58914](https://www.cbo.gov/publication/58914) · [FINRA Margin Statistics](https://www.finra.org/rules-guidance/key-topics/margin-accounts/margin-statistics)