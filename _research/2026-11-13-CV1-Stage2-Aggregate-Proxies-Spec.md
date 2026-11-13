# CV1 stage 2 — did managers' perceived uncertainty fall? Aggregate proxies: registration (13 Nov 2026)

**Status: REGISTERED v1, NOT BUILT, not yet attacked.** Companion to `_research/2026-11-13-CV1-Confidence-Velocity-Spec.md`
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

## Build (not started; after the attack)

`bin/cv1_stage2_uncertainty.py` (`selftest`, `fetch`, `build`), with outputs in `data/cv1_stage2_uncertainty/`:
`registered.csv` carrying a `prereg_sha256` of this file, `scores.csv`, and a README. Raw downloads and Beige Book text
stay in the ignored vintages folder and are never committed (Fed text is public domain, but the folder carries
derived statistics only, as for every other build). User-Agents follow house rules; no host gets a contact address.
