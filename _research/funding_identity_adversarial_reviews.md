# Adversarial reviews — accounting, crankery, ZIRP premise

## Review 1

## VERDICT: THE RESIDUAL IS ZERO. THERE IS NOTHING FOR A MONEY-CREATION STORY TO EXPLAIN.

The puzzle as posed is not a funding puzzle. On the published accounts, US non-financial corporate business funds **100% of its capital expenditure out of internal funds and has a surplus left over**. It is a net *lender*. No external saving is required, so no money creation is required to supply it.

All figures below are from primary sources I pulled and checked myself, not from the project material: Federal Reserve **Z.1 Financial Accounts, release 2026-06-11 (data through 2026:Q1)**, table S.11.a, downloaded as `z1_csv_files.zip` and parsed from the CSV; and BEA NIPA via FRED. Working files at `/tmp/fof/`.

---

## 1. THE EXHAUSTIVE FUNDING SET, QUANTIFIED

The sector constraint is an identity with no free parameters:

```
Capital expenditure  =  Gross saving (internal funds)
                      + Net capital transfers received
                      + Net incurrence of liabilities
                      − Net acquisition of financial assets
```

**US non-financial corporate business, trailing 4 quarters (2025:Q2–2026:Q1), $bn SAAR:**

| Source | $bn |
|---|---:|
| Retained earnings (undistributed profits after tax and dividends) | **928** |
| + Depreciation add-back (capital consumption allowance) | **2,445** |
| + Foreign earnings retained abroad | 0 |
| + Inventory valuation adjustment | −93 |
| + Net capital transfers **received** | **130** |
| **= INTERNAL FUNDS** | **3,410** |
| + Net equity issuance | **−149** *(still net retirement)* |
| + Net debt securities | 271 |
| + Net loans | 369 |
| **USE: gross fixed investment** | **3,135** |
| **Internal funds less gross fixed investment** | **+275** |
| …excluding the one-off capital transfer | **+145** |
| **Net lending (+) / borrowing (−)** | **+50** |

The Z.1 "financing gap" line (FA105005305) is **negative** in five of the last six quarters: −250, −253, −164, −635 SAAR. Internal funds have exceeded capex since 2025:Q2.

I verified the identity closes exactly, quarter by quarter, to the dollar (residual 0.000 on all nine quarters tested). This is not a fitted result.

**Foreign saving does not enter.** The current account deficit is $1,065bn SAAR in 2026:Q1 — **3.3% of GDP, down from 4.1% in 2024**. Foreign saving as a share of GDP has *fallen* through the AI capex build. Rest-of-world purchases of US corporate equities were $119bn SAAR in 2026:Q1, versus $1,275bn in 2025:Q2 — noise, not a funding trend.

---

## 2. ADJUDICATION OF THE FIVE CHANNELS

**(a) Kalecki / fiscal deficit — this is the whole answer, and it is not a residual.** Federal current deficit 5.6% of GDP; general government gross saving −$1,146bn SAAR. Kalecki does not *close a gap*; it explains why the $928bn of retained earnings and $2,704→$3,164bn of pre-tax profits exist at all with a 2.7% household saving rate. The deficit arrives on the corporate income statement as revenue and is retained. **The government's balance sheet expanded so the corporate sector's did not have to.**

I found a sharper instance than the project has recorded. In **2026:Q1 the NFC sector received a net capital transfer of $559bn SAAR** (~$140bn in-quarter) — a line that has been ~zero for a decade. I confirmed the mirror entry: **federal government net capital transfers paid jumped from ~$100bn to $763bn SAAR** in the same quarter. This is a direct, one-off fiscal transfer to corporations, and it is $559bn of the $1,085bn rise in internal funds since 2023. *I could not confirm what policy caused it* — the magnitude and treatment resemble the 2017:Q4 TCJA deemed-repatriation entry (+$866bn, opposite sign), which suggests a retroactive tax provision, but that attribution is my inference, not verified.

**(b) Mian–Straub–Sufi — does no work here, and I would drop it.** The saving-glut-of-the-rich literature is about the *supply of saving and the demand for safe assets*, i.e. why r\* is low. It is not a corporate funding channel. Since the corporate sector requires no external funding at all, the distribution of household saving is irrelevant to this question. Invoking it would be borrowing authority from a paper that does not address the point.

**(c) Foreign funding — dissolves nothing; it is moving the wrong way.** See above: CA deficit down 0.8pp of GDP since 2024.

**(d) Buyback→capex reallocation — real, and larger than it looks.** Net equity issuance ran −$611bn (2023), −$398bn (2024), −$304bn (2025), and turned **positive +$124bn in 2026:Q1** — a ~$735bn swing in the sector's net external equity position. Even so, the trailing-year figure is still −$149bn: the sector is *still* net-retiring equity while fully funding capex. Capital return was reduced, not reversed. **Caveat: the +124 is a single quarter and should not be treated as a trend.**

**(e) Depreciation and useful lives — quantitatively the biggest thing in the data, and it cuts against the boom narrative.**

Using *economic* consumption of fixed capital (FU106300003.Q, not the tax-basis CCA):

| | Gross fixed inv. | Economic CFC | **Net investment** |
|---|---:|---:|---:|
| 2023:Q4 | 2,871 | 2,196 | **675** |
| 2026:Q1 | 3,240 | 2,532 | **708** |

**Gross fixed investment +12.9%; net fixed investment +4.9%.** Roughly 90% of the increase in gross capex is absorbed by faster depreciation, because the marginal asset is a 3–6 year GPU/server rather than a 20–40 year structure. In net capital-accumulation terms the AI boom is barely visible in the sector accounts. Separately: information-processing equipment plus software account for **+$585bn of the +$701bn rise in all private non-residential fixed investment since 2023 (83%)**.

**One correction to my own first read, which I flag because it would have been a false finding.** The tax-basis CCA jumps discontinuously at 2025:Q1 (+$317bn in one quarter) while NIPA economic CFC is perfectly smooth (+$36bn) — so the Z.1 line is tax depreciation and the step is almost certainly bonus depreciation. I initially read this as a large cash windfall inflating internal funds. **It is not.** Pre-tax profits fall by an almost exactly offsetting −$348bn, and internal funds actually *declined* $33bn across that quarter. The net cash effect is only the ~$40bn tax saving. Accelerated depreciation is close to neutral in this identity.

---

## 3. WHAT I CANNOT CONFIRM, AND THE STRONGEST COUNTER-ARGUMENT

I am obliged to state where this could be wrong.

1. **The sector aggregate cannot see intra-sector circularity.** Nvidia taking equity in a customer that buys its chips nets to zero inside S.11.a. The vendor-financing signature is nonetheless visible: **trade receivables +$877bn SAAR** in 2026:Q1. The accounts I used are structurally incapable of testing the circular-financing thesis. This is the real hole.

2. **SPV/JV-owned data centres may be out of scope entirely.** If a hyperscaler data centre is held in a private-credit-funded vehicle classified as a financial entity, its capex never enters NFC capex. I checked non-financial *non-corporate* business as a possible home (capex $625bn, near-self-funded, no anomaly) but I could not verify the sector classification of the large 2025–26 JV structures. If material, my headline understates externally-funded capex.

3. **The 2026:Q1 financial account is dominated by an opaque residual.** Of the $4,014bn SAAR financial-asset acquisition, **$2,691bn is "total miscellaneous assets."** That single line carries the quarter. It limits how much weight 2026:Q1 can bear, which is why I report the trailing four quarters as the headline.

4. **2026 is one quarter of Z.1 data**, subject to revision.

5. The sector aggregate says nothing about the **marginal** AI borrower. Oracle, CoreWeave and the neoclouds are plainly externally funded. They are small against a $3.1tn sector. The aggregate result and the firm-level stress are both true and not in conflict.

**Project figures I independently checked and confirm:** M2 = $23,155.2bn (June 2026), **+5.53% y/y** — exact. Personal saving rate **2.7%** (June 2026), near the 2005–07 all-time lows — the operator's premise that saving rates are not up is correct, and understated: they have fallen.

---

## 4. THE PUZZLE IS MISPOSED

The operator has fused two questions that the accounts keep separate:

- **"How is the capex funded?"** — Answered, fully, with no residual. Retained earnings plus depreciation, underwritten by a 5.6%-of-GDP fiscal deficit. No money creation needed.
- **"How are the valuations sustained?"** — A different question with a different answer, because **valuation is a price, not a flow, and prices do not require funding.** Gabaix–Koijen is a statement about the price elasticity of a stock, not about saving. No quantity of saving is needed to mark $80tn of equity up or down; only the marginal trade is.

The operator's intuition that "if someone actually pulled money out, valuations would collapse" is correct — and it is correct *for reasons that have nothing to do with how the capex was funded*. Conflating the two produces a search for a money-creation residual that does not exist.

**The most useful thing I can tell him: stop looking for the funding gap. There isn't one.** The interesting object is the collateral chain and the price elasticity of the stock — where his existing FX-swap stock finding (>$80tn outstanding, ~$25–26tn off-balance-sheet) and Gabaix–Koijen already point. Those survive this review. The money-creation hypothesis does not, and the ECB SFTDS result the project already has is consistent with that.

---

## Review 2

## ADVERSARIAL REVIEW OF THE NINE TRADITION REPORTS

I re-derived four blocks of claims from primary sources. Everything below marked **[V]** I checked myself; **[U]** I could not confirm within this session and it should not be quoted as verified.

---

## 0. WHAT SURVIVED VERIFICATION (stated first, so the criticism is credible)

**[V] Schumpeter's TIPS counter-test is exactly right, including the date.** TreasuryDirect auction records: the 23 July 2026 10-year TIPS auction cleared at a high yield of **2.4380%**. Filtering all 139 auctions of 10-year-original TIPS back to 1997, the last one to clear above that level was **8 October 2008 at 2.8500%**. "Highest at auction since October 2008" is correct to the month. (Note the secondary-market series DFII10 did print 2.52% on 25 Oct 2023, so the claim is true *at auction* and false *in the secondary market* — the researcher's wording is precise and should be preserved exactly as written.)

**[V] BIS WP 569 is quoted accurately throughout.** From the PDF: the cointegrating vector coefficient is `5.54***`; the text reads "a 1 percentage point reduction in the average lending rate allows borrowers to service an additional 5.5 percentage points of debt for the same income in the long run"; "This also makes borrowers look deceptively solid in the boom phase" is verbatim; "private sector expenditure drops by around 3 percentage points in the long run after a −10% leverage gap"; troughs of "−11% in 1987 and −20% in 2006"; "would explain around half of estimated post-crisis output losses." All six checks pass.

**[V] BIS Bulletin 120 is quoted accurately throughout.** Spreads 6.2 vs 6.1pp; maturity 4.7 vs 4.8 years; secured 46% vs 48%; average loan $169m vs $90m; outstanding "over $200 billion"; "$300–600 billion by 2030"; originations ">$40 billion in 2025, compared with about $3 billion in 2010"; "approximately 20% of all private credit funds … up from 5% in 2010"; "about 5% of total volumes" for the average fund; 1% of GDP for data centres + IT manufacturing; total IT investment 5% of GDP "exceeding its previous peak … in 2000"; 0.4pp average contribution to growth; "0.8 and 1.3% of GDP, up from 0.5% today"; "leverage does not disappear by being out of sight"; footnote 6 confirms the spread difference "remains insignificant when accounting for differences in loan terms … and borrower characteristics." All pass.

**[V] The macro series check out.** M2SL June-26 = 23,155.2 (+5.53% y/y); LNFACBM027SBOG Jul-26 = 2,005.5 (+19.75% y/y, vs 546.3 Jul-19 and 1,091.9 Jul-24); H.8 line 26 at 5 Aug 26 = 2,016.1; TOTLL 5 Aug 26 = 13,956.4 (+7.24%); BCNSDODNS 2026Q1 = 14,453.8; NCBEILQ027S = 69,511.6; TNWMVBSNNCB = 38,219.0 (so Tobin's q = **1.819**, and the 2025Q3 peak of **1.943** is correct); TNWBSHNO = 182,979.9 with a +$113.1bn Q1 change and a $39,164.8bn 2023–25 increase (both exact); W274RC 2026Q1 = 1,244.2; AD01RC 2026Q1 = −2,955.2 and 2025 average −2,293.5; PSAVERT = 2.7; HY OAS 19 Aug 26 = 2.73; MMMFFAQ027S = 8,289.6; RMFSL = 3,047.2. **The Kalecki section is the most numerically reliable of the nine — every NIPA and Z.1 figure I tested was exact.**

---

## 1. FACTUAL AND ATTRIBUTIONAL ERRORS

**E1 — [V] Census data-centre construction is wrong by ~18%, and the correct number is more supportive than the one used.** Schumpeter's observable states "$50.7bn SAAR April 2026, ~52% of the private office category." From the Census C-30 workbook (`privsa.xlsx`, June 2026 release): private data-centre construction was **$61,859mn SAAR in April 2026**, and **$68,297mn in June 2026 (+45.8% y/y)**. Total private office was $111,220mn (Apr) and $115,808mn (Jun), so the data-centre share is **55.6%** and **59.0%**, not 52%. $50.7bn corresponds to roughly Q3 2025 — a stale figure carrying a wrong date. The *qualitative* claim is confirmed and is stronger than stated: office ex-data-centre fell from $53,725mn (Jun-25) to $47,511mn (Jun-26), **−11.6% y/y**, while total office rose +15.1%. The within-category substitution the Austrian and Cantillon sections predict is visible; the number attached to it is not.

**E2 — [V] Four reports, three different answers, on one series.** Fed `NCBCEBQ027S` (NFC net equity issuance) is positive in 2020Q3, 2021Q1, **2021Q2**, then 2026Q1. Therefore:
- Cantillon: "first positive quarter since 2021Q2" — **correct**.
- Soddy/Fisher: "first positive quarter since 2021Q1" — wrong.
- Minsky/Godley: "turned POSITIVE … for the first time" and "since 2021:Q1" — wrong twice.
- Kalecki: "the first positive print in over a decade" — wrong; it is five years, and the Cantillon section correctly notes there have been 15 positive quarters since 2000.

This series is the load-bearing "funding-source flip" in three separate sections. The operator will read three concurring reports as corroboration. They are not concurring; they disagree, and two-thirds are wrong.

**E3 — [V] The Minsky/Godley leverage ratios are internally impossible.** The section states NFC debt is "16.9% of equity market value, down from 25.6% in 2019", and "37.9% against net worth at current cost", and that in 2009Q1 "the two readings were 59.8% and 47.6%". Using the section's own cited levels: 14,453.8 / 38,219.0 = **37.82%** — the current-cost ratio checks out exactly, which pins the numerator to `BCNSDODNS`. That same numerator over the section's own equity level gives 14,453.8 / 69,511.6 = **20.79%**, not 16.9%. Historical checks: 2019Q1 = 33.0%, 2019Q4 = 31.0% (not 25.6%); 2009Q1 = 68.9% (not 59.8%). The argument — that the market-value denominator flatters leverage and the ordering inverts in a bust — survives; the spread is **17.1pp, not 21.0pp**, and the 2019 comparison is off by 5–7pp.

**E4 — [V] The $662bn lease-commitment figure has no BIS provenance.** The Austrian section writes that "the BIS reports (via Moody's) roughly $662bn of signed-but-not-yet-commenced datacentre lease commitments," cited to BIS QR March 2026. I fetched and text-searched the full 96-page Quarterly Review (`r_qt2603.pdf`): **zero occurrences** of "662", "660", "970", "not yet commenced", "Beignet" or "Hyperion". The only Moody's citations in the issue concern bank significant-risk-transfer methodology. Box A (Eren/Krohn/Todorov) is 1.5 pages and contains **no lease-commitment quantum at all** — it describes the SPV structure qualitatively and gives only the ">$100bn 2025 gross bond issuance" figure. Separately, the Gurley–Shaw section's "Moody's (2026): ~$970bn of lease commitments, ~$660bn unrecognised" is an uncorroborated secondary number. These are almost certainly the *same* underlying trade-press figure appearing twice under two attributions, and the package treats them as two sources.

**E5 — [V] `MVEONWMVBSNNCB` is discontinued.** The Marxian section proposes it as "Foley's measurable version of the gap" and flags "verify before use". Verified: the series ends at **2017Q4**. It cannot be used. The live construction is exactly what the Minsky section already does (NCBEILQ027S ÷ TNWMVBSNNCB), which is another instance of two sections reaching for the same object without noticing.

**E6 — [V] Total bank credit growth.** Schumpeter: "total bank credit $19,780.8bn (+6.5%)." Actual: 19,780.8 / 18,623.7 = **+6.21%**. Wicksell's +6.2% is right.

**E7 — [V] Money-fund assets.** Gurley–Shaw uses "~$7.93tn"; Wicksell, Soddy and Minsky all use $8,289.6bn (Z.1, 2026Q1). $7.93tn matches no observation in the series (2025Q3 = 7,774.1; 2025Q4 = 8,190.2). Unreconciled.

**E8 — [U/likely wrong] The H.8 reclassification caveat cannot be substantiated.** Schumpeter attaches a caveat that a "2026 reporting reclassification (margin loans moved to 'all other loans and leases')" breaks the NDFI series and that "+20.4% is not clean." The current H.8 release contains exactly one series-break note, dated **April 2022**, about foreign-related institutions and loan-loss allowances. Nothing about margin loans or 2026. In the current table, line 26 (NDFI, 2,016.1) plus line 27 (loans n.e.c., 1,288.3) sums **exactly** to line 25 (all other loans and leases, 3,304.4) — margin loans sitting inside the parent aggregate is structural, not a change. Either the caveat needs a citation or it should be withdrawn. This matters because it is the *only* caveat attached to the package's single claimed money-creation channel, and the Wicksell section uses the same series with no caveat at all.

**E9 — [V] The Wicksell "quarterly tripwire" compares two measurement bases, in violation of the project's own rule.** "NFC debt … growing at a 9.13% annualised quarterly rate … the first quarter this cycle in which corporate credit clearly outran nominal GDP (+6.07% y/y)." On a like-for-like y/y basis, NFC debt grew **+4.64%** (14,453.8 / 13,813.4) against nominal GDP +6.07% — i.e. credit *underran* GDP. On a like-for-like annualised-quarterly basis, nominal GDP grew 5.79% ((31,865.7/31,422.5)^4−1) against debt's 9.24%, so the conclusion survives. The comparison as printed does not, and it is exactly the error the brief forbids.

**E10 — [V] Selective citation from the same page of BIS Bulletin 120.** Five sections mine the Bulletin. None reports its stated Key Takeaway: *"While macroeconomic and financial stability risks from the AI boom appear moderate, the boom's sustainability hinges on AI firms meeting high earnings expectations."* Two sections quote "total IT investment at 5% of GDP, exceeding the 2000 peak" while omitting the sentence four lines later: the AI investment *rise* is "similar in size to the US shale boom of the mid-2010s and **half as large as the rise in IT investment during the dot-com boom of the 1990s**." Those are a level and a change — different objects — and only the alarming one is reported. (The "over five times as large" for Japan/Australia **[V] checks out verbatim**, though BIS itself is internally inconsistent on the Australian dates: prose says 2010s, chart legend says 2000s, notes say 2005–12. Schumpeter picked one side without flagging.)

**E11 — [V] Gabaix–Koijen is misused in two ways by six sections.** The NBER w28967 abstract reads: "investing $1 in the stock market increases the market's aggregate value by about $5." (i) There is **no symmetry result**. "Symmetric on the way down" appears in the project's established-findings list and is repeated by six sections as though estimated. It is an assumption. (ii) Four sections apply the **aggregate-market** multiplier to a **sector** ("the AI complex", "AI-related equity"). The whole logic of the paper is that aggregate elasticity is small *because there is no substitute for the market*; within-market sectoral elasticity is much higher and the 5× has no claim on it. Any number of the form (AI market-cap decline) = 5 × (AI net outflow) is unsupported by the cited paper.

**E12 — [V] The Wicksell leverage-gap construction is specified on the wrong variables.** The section instructs: "regress log(NFC credit-to-GDP) on log(aggregate asset price index) imposing unit elasticity." WP 569's own Annex 1 defines the data-based leverage gap as "**the ratio of credit to real estate assets of households and non-financial corporations**" (footnote 35: similar using total non-financial assets). The estimated object is household+corporate credit against **property**, not NFC credit against an equity-inclusive index. Rebuilding it on different variables and then quoting WP 569's coefficients and −10%/−20% thresholds transfers coefficients across a change of variable. And it matters *specifically here*, because the same section correctly reports JST's result that equity-bubble × credit is insignificant while housing-bubble × credit is 0.54***. The section calls this "the single most decision-relevant construction in this report." As specified it would produce a number the quoted coefficients do not describe.

---

## 2. OVERREACH RELATIVE TO EVIDENTIARY STRENGTH

**Austrian.** Credit where due: this is the most self-critical of the nine, and it does the honest thing on the one formal test the tradition has — Lester & Wolff's adverse sign on stage-of-processing prices. But three overreaches remain.

1. It offers eleven observables and concedes it constructed **none** of them, could not verify the NIPA levels ("FRED blocked the fetch"), and could not verify the $662bn (which E4 shows is misattributed anyway). What is delivered is a research programme presented at the length of a body of evidence.
2. The tradition's own composite falsifier — "if BOTH the FD-ID stage relative prices AND aggregate cash-flow duration are flat through 2026, the tradition has no surviving observable here and should be dropped" — is stated, and **neither has been measured**. On the project's own rules the tradition should therefore carry zero weight today. The word count does not reflect that.
3. The "specificity wedge" (Lachmann) is claimed as the distinctive Austrian contribution to the collateral question. It is standard corporate finance: Williamson (1988) on redeployability and debt capacity, Shleifer–Vishny (1992) industry-equilibrium fire sales, Benmelech–Bergman on aircraft. The Soddy section cites Shleifer–Vishny and Pulvino for the *same* object with actual estimated discounts (10–20% aircraft, ~27% foreclosed homes). Austrian capital theory contributes vocabulary here; the measurement already exists elsewhere in the same package.

**Soddy.** The section is honest that the thermodynamics is a metaphor and the reform platform is a platform. It then does something worse than overreach: it makes Soddy load-bearing for a proposition he does not supply. "Aggregate market capitalisation is a price, not a fund" is (i) elementary, (ii) already stated in this same package by Tobin, Godley, Durand and Keynes (GT p.135), and (iii) quantified only by Gabaix–Koijen, which is not Soddy. Strip the metaphor and the platform and what remains is the claim/thing distinction, which is Fisher's and, before Fisher, Thornton's. The section's one genuinely original contribution is the **pledging-capacity** argument — broker-dealer receivables +30.5% y/y as purchasing power manufactured out of a price with no deposit created — and that is Geanakoplos and Brunnermeier–Pedersen, both cited in the section. Soddy is not carrying it.

Worse: at the only point where the pledging story is measured, it fails. Margin loans are 0.90% of NFC equity market value, **below** the 0.95% of 2021Q4. The section says so, then keeps the story on the grounds that "the unmeasured part is exactly the part a FIG structurer can see and the public data cannot." That is an appeal to unavailable evidence. Recommendation: Soddy should be a footnote to the Fisher section. His equal billing is an artefact of how the brief was partitioned, not a finding about the literature.

**Schumpeter.** Two specific overreaches. (a) "Genuine deposit creation enters through the bank lines that fund those vehicles, visible in H.8 loans to NDFIs" — the section then concedes nobody has decomposed that line, which also funds mortgage REITs, BDCs, consumer finance and insurers. A $2.0tn stock growing 20% is attributed to the AI chain on the strength of a plausibility argument, and it is then used as the headline money-creation channel. (b) **[U]** The two most decision-relevant numbers in the section — FactSet's 9%→32% external funding share, and Epoch AI's five firm-specific FCF crossing quarters out to Q3 2028 — are secondary and I could not verify either. A crossing date for Microsoft in Q3 2028 is four quarters beyond any disclosed guidance; that is a projection presented with the precision of a measurement.

**Kalecki.** Presented at roughly the right strength. One overreach: "a return to a 3%-of-GDP deficit would … cut after-tax corporate profits by up to ~41%" is a partial derivative taken on an identity whose terms are jointly determined. The section says "holding household net lending and the external balance constant"; it should say that this makes the figure arithmetic rather than a forecast, and that an identity cannot supply the counterfactual — which is precisely what the section's own ideology flag (1) says.

---

## 3. FALSE CONVERGENCE — the biggest structural defect in the package

**C1. Six traditions, one proposition, one modern source.** Schumpeter, Wicksell/BIS, Mises/Hayek, Marx/Durand, Kalecki/Keynes and Minsky/Godley all assert "investment requires finance, not prior saving," and **five of the six cite Borio–Disyatat WP 346 to do it**. That is not six independent confirmations. It is one accounting distinction (a stock of finance versus a flow of saving, plus the ex-post identity S≡I), restated in six vocabularies with one shared modern citation. The operator should be told this is **one finding with one citation**, not convergent evidence.

And the six do not agree on what follows, which the package never adjudicates:
- Schumpeter requires the created claim to be validated by innovation profit.
- **Wicksell requires nothing to break at all** (ch. 9B: permanent level shift, no bust). The Wicksell section states this plainly and the other eight ignore it.
- Mises requires a real subsistence-fund shortage.
- **Kalecki, on his own verified 2026Q1 numbers, says the AI trade is not yet credit-financed** — business gross saving covers 110.5% of business gross investment.
- **Godley, on the same accounts, says the private domestic sector is in surplus (+3.7% of GDP)** and that if the AI trade were funded by private net borrowing this balance would be in deficit. It is not.

So two of the nine traditions, using the highest-quality data in the package, reach the conclusion that the operator's premise is not yet operative. The package presents this as complementary rather than as the direct contradiction it is.

**C2. "Forced saving" appears four times as four discoveries.** Schumpeter (crediting Mises), Mises/Hayek, Thornton/Cantillon and Wicksell all present it. Hayek's 1932 QJE note — cited in the Cantillon section — is literally the paper establishing that Bentham, Thornton, Ricardo, Malthus, Mill, Wicksell, Mises and Schumpeter are all restating one doctrine with a single genealogy. Presenting it four times manufactures the appearance of independent triangulation on a proposition with a documented single lineage.

**C3. "M2 is the wrong instrument" appears seven times.** Schumpeter (HEA clearing system), Wicksell (endogenous residual), Mises (relative prices), Marx (deposit reuse), Gurley–Shaw (administrative boundary), Minsky (position-making velocity), Kalecki (stock vs flow). One proposition. The differences are decorative.

**C4. The "illusion of wealth" convergence is the most illusory of all.** Marx's "the capital does not exist twice over," Tobin's "inside assets net to zero," Godley's revaluation account, Soddy's "price not a fund," Durand's "paradox of liquidity," Keynes GT p.135 — one accounting observation. Every section that states it then hands quantification to **the same place: Gabaix–Koijen**. So the package has one measured number (5×, aggregate-only, one paper, no symmetry result, contested elasticity literature) dressed as six traditions agreeing. And four of the six explicitly disclaim the ability to derive it: Schumpeter "is weakest here and should not be stretched"; Wicksell "has no theory of this and should not be made to supply one"; Kalecki "has nothing to say about valuation"; Mises "belongs to inelastic-markets work, not to the Austrians." **Four traditions honestly saying they cannot answer the operator's central question is not four traditions answering it.**

**C5. The genuine divergences are buried.** Three real, testable disagreements are present and none is surfaced as such: (i) Kalecki/Godley versus Schumpeter/Wicksell on whether external finance is yet the marginal funder — a dated, falsifiable disagreement about the *same* Z.1 tables, and the most operationally useful thing in the nine reports; (ii) Wicksell's null (permanent level shift, no collapse) versus every other tradition's collapse machinery; (iii) Gurley–Shaw's finding that the deposit share of private safe financial debt has moved **the wrong way for the thesis** since 2008 (27% pre-crisis → 35% by 2020) and that the safe-asset share is band-stable at 31.1% ± 2.3% — a direct disconfirmation of the near-money-manufacture story that appears nowhere else in the package.

---

## 4. UNFALSIFIABLE AS STATED

**U1. The BIS apparatus, taken as a whole.** The credit-to-GDP gap is −11.5pp (green) and the debt-service ratio is falling. On the tradition's own early-warning apparatus there is no US boom. The section's response is to propose constructing a *different* gap that goes **negative** in booms — so a positive leverage reading now indicates danger and a negative one also indicates danger. Unless the leverage gap is published with a stated threshold and horizon **before** it is computed, that is unfalsifiable by construction. (The section flags "excess elasticity" for exactly this defect; the flag should be applied one level up.)

**U2. Schumpeter's headline test has a hole in it.** "If this ratio stalls below ~35% … the mechanism was never the operative one. If it passes 50%, the mechanism is load-bearing." 35–50% is undefined, and "the build-out completes" has no completion criterion. Two fixes: name the band's meaning and put a date on it.

**U3. Schumpeter's proposed reformulation is not a quantity.** "Newly created claims-to-resources per unit of current output, aggregating SPV debt, lease and purchase commitments, guarantees, and bank commitments to NBFIs" sums face value, undiscounted future minimum payments, undiscounted purchase obligations, guarantee notionals and undrawn commitments, then divides by a flow of output. That is five measurement bases summed and divided by a sixth — the exact operation the project's rules forbid. Any trend in it is a trend in the instrument mix, not in claims intensity.

**U4. Minsky's flip indicator has no threshold and currently points the wrong way.** "The flip to deficit is the single most informative leading indicator available for the AI trade" — no threshold, no horizon, and the current reading is a record surplus. Compounding this: the Kalecki section says that same 2026Q1 surplus is inflated by a one-off ~$168bn IEEPA tariff-refund capital transfer (W020RC spiking to $807.9bn SAAR). The Minsky section, using the identical quarter, does not mention it and calls it "the largest in the post-war record." Same quarter, one flagged artefact, no reconciliation between the two reports.

**U5. The operator's own sentence.** The Soddy section is right that "if someone actually pulled money out, valuations would collapse" has no threshold, horizon or counterfactual, and right that it becomes testable only as: *conditional on X% of market cap pledged at haircut H, a Y% decline forces Z of sales into a market of elasticity E.* That paragraph is the most useful single thing in the nine reports and it is buried in an ideology-flag list rather than presented as the deliverable.

**U6. "Claim creation, of which money creation is a minority component, and the share is rising on a measurable schedule."** Clause one is definitionally true of any investment not funded in cash. Clause two is not measured. Clause three rests on the FactSet/Epoch series I could not verify.

---

## 5. WHERE THE MAINSTREAM ALREADY DOES THE WORK

**Fictitious capital versus DCF — the test case, and the Marxian section concedes it.** Its own ideology flag (1) reads: Marx Ch.29 "is the Williams/Gordon dividend discount model … the alarm is not in the mathematics; it is in the adjective." That is correct and it settles the main question. Assessing the three claimed residuals:

- **Promoter's profit.** Claimed as a category mainstream finance lacks. It does not lack it: the gap between an income stream held illiquid and the same stream once marketable is the marketability/liquidity discount — priced daily in the private-versus-public multiple, formalised in DLOM valuation practice, and studied as IPO underpricing. Hilferding's one addition is that it is once-only, which is also what the mainstream says. **No insight added; the arithmetic is identical.** Worse, the section's proposed computation — "post-money valuation × founder ownership minus cumulative capital contributed" — is not promoter's profit at all. It is unrealised paper gain computed by marking an illiquid common stake at the price of the marginal *preferred* round, ignoring liquidation preferences. It is precisely the marking error the section elsewhere warns against.
- **Duplication ("does not exist twice over").** The section's own flag (4) concedes this is standard sectoral consolidation. Nothing added.
- **Chain double-counting.** Genuinely useful and genuinely under-used — but not Marxian. It is a look-through revenue test, and every measurement instrument the section proposes for it (ASU 2022-04 supplier-finance disclosure, IAS 7/IFRS 7, related-party disclosure, ASC 606 principal-vs-agent) is mainstream accounting standards. The tradition supplies the suspicion; GAAP supplies the measurement.

**Verdict: this is the clearest case in the package of vocabulary rather than insight, and the author says so.** Where the section does add something — the insistence that fictitious capital funds nothing directly and works *only* through the collateral channel — that is also mainstream: **Kiyotaki–Moore (1997), Geanakoplos's leverage cycle, Adrian–Shin's procyclical leverage.** Note that **Kiyotaki–Moore is cited nowhere in any of the nine reports.** The canonical model of exactly the loop the operator described — valuation → borrowing base → real spending → valuation, with collateral constraints and a formal amplification factor — is missing from a package built around that loop. That absence is the strongest single indictment of the "older tradition has more purchase" premise.

**Cantillon/Thornton.** The strongest old claim — injection point determines which prices move — is now a mainstream empirical literature (Auclert 2019, Kaplan–Moll–Violante HANK, and the QE portfolio-rebalance work the section itself relies on via Selgrad and Carpenter et al.). The section's best evidence is all modern papers. What the pedigree buys is the *negative* result: Cantillon states the neutrality condition and says it almost never holds. That is a useful corrective to a quantity-theoretic null nobody now defends.

**Wicksell.** Partial exception in the tradition's favour: the neo-Wicksellian mainstream identifies the gap off inflation, so a quiet CPI *mechanically* implies no gap. That is a genuine identification failure the older Wicksell does not share. But the working content is the BIS extension — thirty years old, published by a central bank, and mainstream in every sense except that it disagrees with the FOMC. The section says this.

**Gurley–Shaw.** The measurement critique survived; the impotence thesis did not. The live content is Barnett's Divisia and Gorton's information-insensitivity, both modern. And the section's flagship wedge is fragile: DM4 6.8% versus M2 5.4% rests on **6.1 of 6.8pp coming from a +25.6% y/y jump in demand deposits against −1.1% in other liquid deposits**. A 25.6% surge in demand deposits with a matching fall in savings balances is the signature of a **reclassification**, not of money creation. The section flags this and says it must be reconciled against the Feb-2021 H.6 restructuring and the 2026 IRA/Keogh netting change before use. It has not been. Everything downstream of that wedge should be held.

---

## 6. CROSS-REPORT INCONSISTENCIES THE OPERATOR WILL MISREAD AS CORROBORATION

- **MMF assets:** $8,289.6bn (three sections) vs ~$7.93tn (one). Unreconciled.
- **Netting discipline applied inconsistently:** Wicksell subtracts Z.1 total MMF assets from H.6 retail MMF balances to get "$5.2tn," having stated one sentence earlier that they are different bases; Soddy explicitly refuses the identical subtraction ("DO NOT NET THESE"). Same operation, opposite rulings, same project.
- **Nested categories presented as additive:** MMF shares, repo claims and "T-bills held as cash equivalents" are listed as three separate categories of purchasing power outside M2 (Soddy and Gurley–Shaw). MMFs *hold* the repo and the bills. Any summation double-counts, and both sections invite it.
- **2026Q1 NFC internal-funds surplus:** "largest in the post-war record" (Minsky) vs "inflated by tariff refunds" (Kalecki). Same quarter.
- **H.8 NDFI:** broken by a 2026 reclassification (Schumpeter) vs used clean as the second-ranked observable (Wicksell). Neither substantiated.
- **Net equity issuance:** four sections, three answers, one correct.

---

## 7. WHAT THE PACKAGE ACTUALLY RESTS ON

Strip the redundancy and four things carry it:

1. **BIS Bulletin 120 and BIS QR Box A** — both verified verbatim, and both markedly more cautious than the use made of them ("risks appear moderate"; "half as large as the dot-com rise").
2. **Gabaix–Koijen's 5×** — one paper, aggregate-only, no symmetry result, routinely applied to sectors.
3. **H.8 NDFI** — undecomposed by everyone who uses it, and with a disputed break.
4. **The Z.1 flow of funds** — verified, and read straight it says the AI capex has so far been internally funded, the private domestic sector is in surplus, and NFC debt has grown *slower* than nominal GDP over the last four quarters.

Item (4) contradicts the framing of (1)–(3). It is the highest-quality evidence in the package and it is the least alarming. That should be stated to the operator in exactly those terms.

**One discipline nobody applies.** The Godley section establishes a measurement-error floor: capital-account and financial-account net lending for NFCs differ by **$133–224bn per quarter**, so "any claimed funding channel smaller than ~$0.7tn annualised is inside the discrepancy and is not identifiable in the flow of funds." Applied consistently, that floor disqualifies most of the channels the other eight sections propose to measure — including the entire off-balance-sheet lease/offtake construction, the promoter's-profit tally, and the equity-funded wage bill (~$82bn/yr). No section applies it to any section but its own.

---

**Sources checked directly (curl/WebFetch, 21 Aug 2026):** [FRED series CSV endpoint](https://fred.stlouisfed.org/graph/fredgraph.csv) (M2SL, LNFACBM027SBOG, TOTBKCR, TOTLL, BCNSDODNS, NCBEILQ027S, NCBCEBQ027S, TNWBSHNO, TNWMVBSNNCB, MMMFFAQ027S, RMFSL, PSAVERT, BAMLH0A0HYM2, GDP, DFII10, BOGZ1FL892090005Q, W274RC1Q027SBEA, AD01RC1Q027SBEA, MVEONWMVBSNNCB) · [TreasuryDirect auction API](https://www.treasurydirect.gov/TA_WS/securities/search?format=json&type=TIPS) · [BIS Working Paper 569](https://www.bis.org/publ/work569.pdf) · [BIS Bulletin 120](https://www.bis.org/publ/bisbull120.pdf) · [BIS Quarterly Review March 2026](https://www.bis.org/publ/qtrpdf/r_qt2603.pdf) and [Box A chapter](https://www.bis.org/publ/qtrpdf/r_qt2603a.pdf) · [Federal Reserve H.8, current release](https://www.federalreserve.gov/releases/h8/current/default.htm) · [Census C-30 private construction, seasonally adjusted](https://www.census.gov/construction/c30/xlsx/privsa.xlsx) · [NBER WP 28967 abstract](https://www.nber.org/papers/w28967)

---

## Review 3

## VERDICT: CONFLATION — and in the one place it matters most (the US), the premise is inverted, not merely imprecise

The operator's sentence contains three claims. Two are false for the US, one is true for Japan, and the mechanism he names is the opposite of what the record shows. He should not build on it as stated.

---

### 1. "Without M1 to M3 being affected" — false for the US, by a wide margin

FRED M2SL (`/private/tmp/claude-501/.../scratchpad/m2sl.csv`, pulled directly):

| | Dec-2008 | Dec-2019 | CAGR |
|---|---|---|---|
| US M2 (SA, $bn) | 8,203.0 | 15,351.5 | **5.86%** |
| US nominal GDP ($bn) | 14,608.2 | 21,933.2 | **3.76%** |
| M2 / NGDP | 56.2% | 70.0% | — |

Broad money grew **2.1pp/yr faster than nominal income for eleven consecutive years**. Had M2 tracked NGDP, Dec-2019 M2 would have been ~$12.3tn against an actual $15.35tn — roughly **$3.0tn of "excess" broad money accumulated during ZIRP**. That is not "unaffected." It is the single largest sustained divergence of M2 from nominal income in the post-Volcker record.

**He is likely conflating three distinct episodes.** Two contaminating facts:

- **The M1 series has a definitional break exactly where he may be looking.** Verified against the Fed's own H.6 technical Q&A: following the 24 April 2020 Regulation D amendment removing the six-transfer limit, savings deposits were reclassified as transaction accounts effective **May 2020**. The Fed states the change increased M1 "by the size of the industry total of savings deposits, which amounted to approximately **$11.2 trillion**," while "leaving the M2 monetary aggregate unchanged." My data confirm it: M1SL Apr-2020 = $4,856.4bn → May-2020 = $16,312.5bn. Any M1 chart spanning 2009–2021 is uninterpretable across that seam.
- **US M3 does not exist for the ZIRP period.** The Fed announced discontinuation 10 Nov 2005; last publication 23 March 2006, on the stated grounds that M3 "does not appear to convey any additional information about economic activity that is not already embodied in M2." Any "US M3" series he has seen for 2009–2019 is a reconstruction or the OECD harmonised series — and note that OECD `MABMM301USM189S` prints $15,320.7bn for Dec-2019 against Fed M2SL $15,351.5bn, i.e. it *is* essentially M2 wearing an M3 label. Flagging under the project's own measurement-basis rule.

**Where he is right: outside the US.** OECD broad money, Dec-2008 → Dec-2019 CAGR:

| Euro area | 2.97% (and only **1.00%/yr** 2008–2012) |
|---|---|
| Japan | **2.58%** |
| UK | 2.74% |
| US | 5.86% |

Japan is the clean natural experiment and it goes his way: BoJ total assets ¥122.8tn (Dec-2008) → ¥573.1tn (Dec-2019), **4.67x**, against broad money **1.32x**. If his mental model was formed on Japan or the euro periphery, it is defensible there. It is not defensible for the jurisdiction whose asset prices he is actually asking about.

### 2. The mechanism is backwards — QE's *first* effect is broad money, not a bypass of it

His model is "financial-sector money creation that never touches the aggregates." The canonical reference says the opposite. From McLeay, Radia & Thomas, *Money creation in the modern economy*, BoE QB 2014 Q1 (downloaded and read directly), on the Bank buying gilts from a pension fund:

> "**QE boosts broad money without directly leading to, or requiring, an increase in lending.**"

> "The start of that transmission is the creation of bank deposits on the asset holder's balance sheet in the place of government debt… Importantly, the reserves created in the banking sector do not play a central role… **banks cannot directly lend out reserves.**"

He is right that reserves ≠ broad money and that the multiplier is a myth. He is wrong that this means broad money is bypassed. Deposit creation depends on *who sells*, and the Bank deliberately bought "mainly from non-bank financial companies" precisely **to** create deposits.

**The quantification is the part he most needs.** Butt, Domit, McLeay, Pezzini & Yates (BoE QB 2012 Q4), Table A — measured on M4ex:

| | QE1 | QE2 |
|---|---|---|
| Direct effect of purchases | £200bn | £125bn |
| less corporate substitution to capital markets | 16 | 8 |
| less purchases of bank debt/equity | 62 | 0 |
| less purchases of non-resident assets | 0 | 16 |
| less bank sales of government debt | 0 | 31 |
| **Net impact on broad money** | **£122bn** | **£70bn** |
| **as % of purchases** | **61%** | **56%** |
| Actual broad money flow | +13 | +31 |
| **Implied counterfactual flow** | **−109** | **−38** |

That last line is the correction that reframes his whole question. Broad money *looked* subdued during QE not because QE bypassed it, but because **QE was offsetting an ongoing contraction**. Counterfactual broad money flow was strongly negative. Bridges & Thomas (BoE WP 442, 2012) run the same arithmetic forward: QE "boosted the broad money supply by £122 billion or 8%," which "may have pushed down on yields by an average of around 150 basis points in 2010 and increased asset values by approximately 20%."

Note what that is: **the BoE quantifying asset-price effects explicitly inside the older monetarist tradition, and running the causation *through* broad money rather than around it.** His instinct that the older tradition has purchase here is correct. His specific claim contradicts what that tradition actually found.

### 3. Documented transmission is a duration/discount channel, not a money-quantity channel

Read directly from source PDFs:

- **Krishnamurthy & Vissing-Jorgensen (2011)**, event study, cumulative two-day changes across five QE1 dates: 10y Treasury **−107bp**, 10y Agency **−200bp**, 30y Agency **−144bp**, 30y Agency MBS **−107bp**. Their headline finding is that "effects on particular assets depend critically on which assets are purchased" — MBS purchases, not Treasury purchases, drove mortgage and corporate spreads. A quantity-of-money story cannot generate that asset-specificity; a preferred-habitat/segmentation story can.
- **Gagnon, Raskin, Remache & Sack (FRBNY SR 441, 2010)**: longer-term rates fell "by up to 150 basis points," attributed principally to term-premium compression rather than signalling.
- **D'Amico & King (FEDS 2010-52)**: on the $300bn Treasury programme, a **3.5bp** per-operation flow effect and a stock effect of "as much as 50 basis points," with coefficient patterns supporting "segmentation or imperfect substitution."

**And the adversarial check on all of it:** Fabo, Jancokova, Kempf & Pástor, *Fifty Shades of QE* (NBER w27849): "central bank papers find QE to be more effective than academic papers do… Central bank researchers who report larger QE effects on output experience more favorable career outcomes." Three of my four transmission sources above are central-bank-authored. Treat the effect sizes as an upper bound.

**Most damaging to a monetary reading of the secular move:** Rachel & Smith (BoE WP 571). Global long real rates fell ~450bp over 30 years; they attribute ~400bp, of which ~300bp is *non-monetary* — demographics 90bp, within-country inequality 45bp, EM precautionary saving 25bp, falling relative price of capital 50bp, lower public investment 20bp, risk-free/actual spread 70bp — plus ~100bp from slower trend growth. Central bank money creation accounts for essentially none of the secular trend. The bond bull market he attributes to financial-sector money creation is mostly a savings-investment phenomenon.

### 4. Real estate — this is where the premise fully inverts

He says money creation drove real estate up during ZIRP. Case-Shiller national NSA (`CSUSHPINSA`) and Z.1 household mortgage debt (`HHMSDODNS`), computed from source:

- 2006 bubble peak: **July 2006, 184.61**
- ZIRP begins Dec 2008: 152.54
- **Trough: February 2012, 133.99 — a further −12.2% AFTER three years of ZIRP, QE1 ($1.25tn MBS) and QE2**
- Nominal 2006 peak regained: **January 2017**
- **Real (CPI-deflated) 2006 peak regained: March 2021**
- Household mortgage debt: peak **2008Q1 $10,648bn** → trough **2015Q1 $9,328bn (−12.4%)** → 2019Q4 **$10,391bn, still 2.4% below the 2008 peak**. The nominal 2008 peak was not regained until **2020Q3**.

So: the actual broad-money-creating channel into US housing — mortgage credit — **ran in reverse for the entire ZIRP decade**, and house prices fell for the first three years of it. This is not a money effect. Meanwhile the 10y TIPS real yield (`DFII10`, monthly averages) went 2.17% (Dec-08) → −0.60% (Jul-12) → 0.14% (Dec-19), and the 30y mortgage rate 5.29% → 3.55% → 3.72%. A ~200bp fall in the real discount rate on a perpetual-duration asset is sufficient on its own, and requires **no money creation whatsoever**.

**And his own mechanism was contracting, not expanding.** "Money creation in the financial sector" — private money-like claims — over the same window (`ABCOMP`, `MMMFFAQ027S`):
- ABCP outstanding: **$1,190bn (Jun-2007) → $734bn (Dec-2008) → $487bn (Dec-2009) → $329bn (Dec-2011) → $247bn (Dec-2019)**. Down ~79% from peak and *still falling through the ZIRP decade*.
- MMF total financial assets: peak $3,832bn (2008Q4) → trough **$2,785bn (2012Q2)** → $3,120bn (2017Q4). Did not durably exceed the 2008 level until ~2018–19.

The shadow-money boom he is describing is **2002–2007, not 2009–2019**. He has back-dated the mechanism of the pre-crisis credit boom onto the post-crisis discount-rate boom.

---

## What this means for the project

**Do not build on the analogy as stated.** The chain "ZIRP → off-aggregate money creation → asset prices" is wrong for the US on every link: the aggregate did move, the mechanism was the discount rate not the money stock, and private money-like claims contracted.

**But his conclusion survives — via a better route, and the project already has it.** The claim that matters ("valuations are an illusion that collapses if anyone actually withdraws") is a *price-elasticity* claim, not a monetary one. Gabaix–Koijen's ~$1:$5 multiplier requires no money creation at all: it says market capitalisation is set by marginal flow against an inelastic supply curve, symmetric on the way down. **That is the mechanism he wants, and it is strictly cleaner than the money-creation framing because it does not require an aggregate to hide anything.** Recommend he drop the ZIRP-money scaffolding entirely; it weakens a thesis that stands better without it.

**Two reformulations that are defensible and that he could actually use:**
1. *US M2 outgrew nominal income by ~$3.0tn over 2009–2019 and velocity fell; the excess was absorbed in asset markets rather than goods markets.* This is a **stronger** version of his intuition than the one he stated, it is arithmetically true, and it is exactly the Bridges–Thomas monetarist channel. It concedes that the aggregate moved and argues about *where the money went* — a much harder argument to dismiss.
2. *Japan is the case where his stated mechanism holds* — BoJ balance sheet 4.67x against broad money 1.32x. If he wants an "asset prices without broad money" precedent, that is the one to cite, and he should cite it as Japan, not as ZIRP generally.

**One challenge back at the project's own priors:** the established note reads "M2 +5.5% y/y — roughly nominal GDP pace. The aggregate says no boom." That inference is weaker than it looks. During 2009–2019 M2 also ran only ~2pp above NGDP and the aggregate "said no boom" then too, while $3tn accumulated. A y/y rate roughly at NGDP pace tells you the *stock/income ratio is stable*, not that no monetary expansion is occurring. If the 2026 M2/NGDP ratio is at or near the elevated 70%+ post-ZIRP plateau rather than the 56% pre-crisis level, the level statement and the growth-rate statement point in different directions. Worth checking before that line is treated as settled.

---

### Marked as not independently verified
- Euro-area and Japanese nominal GDP for 2008–2019 — I did not pull them, so I cannot say whether EA/JP broad money outgrew nominal income as US M2 did. The EA and JP CAGRs above are broad money only.
- Euro-area and Japanese house-price and equity paths during ZIRP. I did not test the money-vs-discount-rate decomposition outside the US; the section 4 finding is a US finding.
- OECD `MABMM301*` is OECD's harmonised broad-money concept, **not** ECB M3, not BoJ M3, and not the discontinued Fed M3. Cross-country comparison of the CAGRs is valid; treating any of them as "M3" in the operator's sense is not.
- My attribution of the US housing recovery to the discount-rate channel is an inference from three verified facts (prices fell three years into ZIRP; mortgage credit contracted 12.4%; real 10y fell ~200bp), not a citation to a formal decomposition. Duca–Muellbauer–Murphy would be the source to check it against; I did not.
- WebSearch budget for this session was exhausted (200/200) before I started, so all sourcing above is direct FRED CSV pulls and direct PDF downloads, not search-mediated. Downloaded PDFs are in `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/`: `money-creation-in-the-modern-economy.pdf`, `what-can-the-money-data-tell-us-about-the-impact-of-qe.pdf`, `the-impact-of-qe-on-the-uk-economy-some-supportive-monetarist-arithmetic.pdf`, `kvj.pdf`, `gagnon.pdf`, `damicoking.pdf`, `fifty.pdf`, `rachel_smith.pdf`.