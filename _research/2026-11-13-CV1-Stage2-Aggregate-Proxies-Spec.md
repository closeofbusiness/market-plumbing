# CV1 stage 2 — did managers' perceived uncertainty fall? Aggregate proxies: registration (13 Nov 2026)

**Status: REGISTERED v2 (amended blind 13 Nov after the Grok attack; the v1 table below is superseded), NOT BUILT.** Companion to `_research/2026-11-13-CV1-Confidence-Velocity-Spec.md`
(stages 3–4), which this file does not amend. The principal ruled on 13 Nov that stage 2 should be tested on cheap free
aggregate proxies, rather than on a firm-level 10-K corpus pulled from `www.sec.gov`. Source inventory: a Sonnet scout
on 13 Nov, which read shape only; the supervisor spot-checked the SBU sheet and column names and the Dallas file type.

## What these tests can and cannot show

Stage 2 says AI lowered managers' **epistemic** uncertainty (not knowing the facts), not aleatory uncertainty (the future
itself). An aggregate time series cannot attribute a fall to AI: post-pandemic normalisation, the rate cycle and
ordinary expansion maturity all lower measured uncertainty too. The labels are therefore **asymmetric**, as in the v2
companion. Stage 2 *requires* perceived uncertainty, net of policy and market uncertainty, to be lower after generative
AI spread than before. **AGAINST refutes stage 2 in the aggregate. SUPPORT means "consistent, not attributed".**

The 2025 tariff episode raised policy uncertainty sharply. Every statement therefore nets out policy and market
uncertainty with controls fixed here, so a tariff spike is not read as AI failing, and a calm market is not read as AI
working.

**Already seen, so not blind:** a Grok literature scout reported that the SBU sales-uncertainty series fell modestly
from October 2025 to October 2026. No statement below uses October 2025 to October 2026 as its comparison window, and
S1's treatment window ends in December 2025. The scout says it glimpsed some BTOS and NFIB values, and repeated none of
them. Neither source carries a labelled statement here.

**Windows (fixed).** Baseline: Jan 2015 – Dec 2019 where the series exists, otherwise from its first month. Treatment:
Jan 2023 – Dec 2025. The 2020–2022 pandemic years are excluded from both windows and from every control regression.

**Controls (fixed).** Monthly means of the log daily Baker–Bloom–Davis EPU (`All_Daily_Policy_Data.csv`) and of the log
CBOE VIX close (`VIX_History.csv`). "Residual" means the residual from an OLS regression of the monthly series on a
constant, log EPU and log VIX. The regression is estimated on the baseline and treatment months pooled, and the window
means of the residuals are then compared. **Effect size:** (treatment mean residual − baseline mean residual) ÷ the
standard deviation of the series' baseline residuals.

| id | proxy | statistic | SUPPORT (consistent) if | AGAINST (refutes stage 2, aggregate) if |
|---|---|---|---|---|
| CV1-S1 | Atlanta Fed SBU: firms' own subjective uncertainty about 12-month sales growth | `SalesRevGrowthUnc_percent`; smoothed sheet from Dec 2016, `Historical Data for Research` for Jan 2015 – Nov 2016 (same columns; the builder checks the overlap months, if any, agree); effect size | ≤ −0.5 | ≥ 0 |
| CV1-S2 | Fed Beige Book, all editions and Districts: uncertainty in business contacts' reports that is **not** tied to policy or markets | Sentences containing `uncertain`, `uncertainty` or `uncertainties` (case-insensitive) and **none** of the policy/market list below, per 1,000 sentences, pooled over the edition's 12 District texts (the national summary is excluded); one value per edition; edition months mapped to calendar months; the EPU/VIX residual taken on edition months | ≤ −0.5 | ≥ 0 |
| CV1-S3 | Dallas Fed Texas manufacturing and services surveys: "How has uncertainty regarding your company's outlook changed?" | `Uncr` (net: % increased − % decreased) from the TMOS and TSSOS index files, averaged across the two surveys; baseline Jan 2018 – Dec 2019 (the series starts in 2018); effect size. This is a *change* question, so a negative mean residual means uncertainty kept falling, month on month, more than at baseline | ≤ −0.5 | ≥ 0 |
| CV1-S4 | Boundary (epistemic ≠ aleatory): SBU confidence against realised dispersion | Ratio of `SalesRevGrowthUnc_percent` to the realised cross-firm sales-growth spread (`RealizedSalesGrowth_p90` − `_p10`, sheet `Distrib. of Realized Sales Gr.`, observed rows only, never the projected ones), window means compared directly (no controls; both sides move with the cycle). The thesis's boundary says perceived uncertainty falls *relative to* realised dispersion | treatment ratio ≤ 0.9 × baseline ratio | treatment ratio ≥ baseline ratio |
| CV1-S5 | **Descriptive, no label.** UK cross-check | Bank of England DMP `Subjective uncertainty`, sales, 3-month average, Jan 2017 – Dec 2019 vs Jan 2023 – Dec 2025; reported with the UK figures beside the US ones | — | — |
| CV1-S6 | **Descriptive, no label.** Census BTOS Q20, the share of firms rating their next six months "difficult" or "very difficult to forecast", 2023–2026, beside Q7 (AI use). There is no pre-AI baseline, so it can only show co-movement and cannot test anything | — | — |

**S2 policy/market exclusion list** (a sentence is policy- or market-linked if it contains any of these case-insensitive
stems; fixed before any text is read): `tariff`, `trade`, `polic`, `election`, `government`, `shutdown`, `regulat`, `tax`,
`fiscal`, `federal reserve`, `interest rate`, `rates`, `geopolit`, `war`, `conflict`, `sanction`, `immigra`, `pandemic`,
`covid`, `virus`, `stock market`, `financial market`, `volatil`, `brexit`, `debt ceiling`, `legislat`, `congress`,
`administration`. Sentences split on `.`, `?` and `!` followed by whitespace. The builder reports the count of all
uncertainty sentences and of policy-linked ones, edition by edition, and S2 is also reported (described, not labelled)
**with** the policy-linked sentences included.

**Not used, with reasons:**
- **EDGAR full-text counts.** The search returns documents, not filings: exhibits match, and SIC filters are silently
  ignored, so there is no clean denominator.
- **CFO Survey.** It has no continuous uncertainty series across the 2020 break.
- **NFIB.** The host returned 403 and no free machine-readable series was found.
- **Regional surveys other than Dallas.** None has an uncertainty variable.

## Version 2 (amended 13 Nov after the Grok attack, still blind) — supersedes the table and rules above

Attack: `_research/2026-11-13-Grok-CV1-Stage2-Attack.md`. Accepted:
- S3's question measures a month-on-month *change*, not a level, and S2's substring stems match inside ordinary words
  ("war" in "toward", "rates" in "moderates", "trade" in "retail trade"); the Beige Book was redesigned on
  18 Jan 2017, inside the baseline.
- S4's denominator moves with cross-firm heterogeneity and common inflation.
- The pooled residual is not the partial window effect.
- The daily EPU file is unfit for multi-year comparison, and its authors use the monthly 10-paper index instead.
- Inflation uncertainty is inside nominal-sales uncertainty and was uncontrolled.
- Smoothing and instrument changes split the SBU baseline.
- The BTOS question numbers were wrong.

**Overruled:** Grok's rule that "S1 alone cannot refute stage 2". S1 is the only free series that measures the right
object, an activity-weighted mean of firms' own subjective standard deviations. If S1 is AGAINST after the controls below,
stage 2 has failed its one necessary-condition test on free data, and the note says so. Also overruled: the call to
winsorize firm-level standard deviations, because only the published aggregate is free.

**Labelled statements (only these two).**

| id | statistic | SUPPORT (consistent, not attributed) if | AGAINST if |
|---|---|---|---|
| CV1-S1 v2 | From one frozen, hashed SBU workbook, take the **unsmoothed** sales-revenue subjective-uncertainty series, `Index Values (unsmoothed) `, `SalesRevGrowthUnc_percent`, Dec 2016 – Dec 2019 and Jan 2023 – Dec 2025 (December 2016 is the first full month after the September 2016 instrument change; earlier months are dropped). OLS: Y = a + b1·log(monthly 10-paper EPU, `Main News Index`) + b2·log(monthly mean VIX close) + b3·log(SPF one-year CPI forecast dispersion, Philadelphia Fed) + d·Treatment + e. Effect size = d ÷ the standard deviation of the residuals in baseline months. If the SPF dispersion series cannot be fetched free and scripted, the builder stops S1 and reports, and does not substitute a series | effect size ≤ −0.5 | effect size ≥ 0 |
| CV1-S4 v2 | Same workbook. Numerator: the unsmoothed `SalesRevGrowthUnc_percent`. Denominator: `RealizedSalesGrowth_p90` − `RealizedSalesGrowth_p10` (observed rows only; if the sheet has no observed/projected flag, keep only months at least 12 months before the vintage date). Months whose four-quarter look-back overlaps 2020–2022 are dropped, which removes all of 2023. R = (window mean of numerator) ÷ (window mean of denominator). Baseline Dec 2016 – Dec 2019; treatment Jan 2024 – Dec 2025. Both means are printed beside R. **Labelled only if S1 v2 is SUPPORT** (the thesis's boundary presupposes stage 2); otherwise it is reported unlabelled | R_T ≤ 0.9 × R_B | R_T ≥ R_B |

**Descriptive only (no label; none may be read as supporting or weakening stage 2):**
- **S2 v2, Beige Book.** Per edition, uncertainty sentences per 1,000 sentences under two dictionaries:
  - (a) a whole-word match on `uncertain|uncertainty|uncertainties`;
  - (b) the same, dropping a sentence only if it contains a whole word from {tariff, tariffs, election, elections,
    shutdown, regulation, regulations, regulatory, tax, taxes, fiscal, geopolitical, sanctions, immigration, pandemic,
    covid, brexit, congress, legislation} or one of the phrases {federal reserve, interest rate, interest rates, debt
    ceiling, stock market, financial market, financial markets}.

  The national summary is excluded by a fixed list of District headings. The sentence splitter must not break on
  "U.S." or "St." Editions are dated by release month. The 18 Jan 2017 format change is marked on the chart. No
  residualising.
- **S3 v2, Dallas Fed.** The not-seasonally-adjusted balance `uncri − uncrd`, reported separately for TMOS and TSSOS from
  the frozen vintage, captioned "negative = more firms said uncertainty fell this month than rose". Not averaged, not
  residualised, and not compared with 2018–2019 as a level.
- **S5 v2, Bank of England DMP.** Only if the free monthly workbook has the column "average within-firm standard deviation
  of expected sales growth" (sheet `Subjective uncertainty`): the ratio of its Jan 2023 – Dec 2025 mean to its Jan 2017 –
  Dec 2019 mean, with the caveat that the comparison mixes Brexit, the energy shock and carried-forward answers. If the
  column is absent, the readout says "not in the free monthly file".
- **S6 v2, Census BTOS.** The share answering "difficult" or "very difficult to forecast", for the question whose text
  begins "Thinking about the future performance of this business". Census's original AI series, its series from 4 Dec
  2025, and the "Super Intelligence" wording from 19 Oct 2026 are plotted as separate lines. Never spliced, never
  correlated, never referred to by question number.

## Build (not started; after the attack)

`bin/cv1_stage2_uncertainty.py` (`selftest`, `fetch`, `build`), with outputs in `data/cv1_stage2_uncertainty/`:
`registered.csv` carrying a `prereg_sha256` of this file, `scores.csv`, and a README. Raw downloads and Beige Book text
stay in the ignored vintages folder and are never committed (Fed text is public domain, but the folder carries
derived statistics only, as for every other build). User-Agents follow house rules; no host gets a contact address.
