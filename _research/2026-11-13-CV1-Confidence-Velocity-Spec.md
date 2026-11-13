# CV1 — the confidence / capital-velocity channel: registration and build spec (13 Nov 2026)

**Status: REGISTERED, NOT BUILT.** Written before any outcome series below was read by this project. Serves A13
(where the money for the AI build-out and the capex comes from, and what drives earnings). Received from the principal
13 Nov 2026 as a thesis; held here as a hypothesis until each prediction is scored.

## The claim under test

AI acts on the economy first as a *catalyst for corporate capital commitment*, not as a productivity shock. Cheaper
analysis lowers managers' perceived (epistemic) uncertainty; that shrinks the real-option value of waiting on
irreversible commitments; firms then move idle cash and unused debt capacity into capex, acquisitions and inventory. The
result is a demand-side boom with flat firm-level productivity, and, because aleatory risk is unchanged, a later rise in
write-downs. In the terms of the goal, this is a **funding-source** claim: the money is said to come from corporate
balance sheets that were already full, not from new credit, money creation or the AI complex's own cash flow.

## What was already read before registration (so these predictions are not blind to it)

Three items were read at registration time, and the predictions below were written knowing them. None of them is one of
this note's own statistics.

- **The two survey claims the thesis cites, checked against the Atlanta Fed copies of the papers (supervisor read
  both PDFs, 13 Nov).** Baslandze et al. (NBER WP 34984; Atlanta Fed WP 2026-4): "enhance decision-making and
  management" is the **third** motive for 2025 AI spending (2.7 on a 0–4 scale), behind production efficiency (2.9) and
  labour productivity (2.7). It does rank ahead of cutting labour costs (2.0) and non-labour costs (1.8). The rating was
  asked only of firms that invested. Yotzov et al. (NBER WP 34836; Atlanta Fed WP 2026-3): 89% of executives in four
  countries report no AI effect on sales per employee over the past three years. The base is *all* firms, users and
  non-users, and the mean effect is +0.29%. The paper does not link that figure to capital spending. The thesis's
  "top motive" is therefore wrong as stated, and its "despite heavy capital deployment" is not in the source.
- **San Francisco Fed Economic Letter 2026-13 (Kalyani and Li, 18 May 2026; supervisor read it at source).** Among public firms, all capex
  growth since 2024Q1 came from firms whose earnings calls are AI-positive. "Other firms collectively had slightly
  negative growth." The largest AI-positive firms contributed 10 of the 11 points of AI-positive capex growth in 2025.
  That is prima facie evidence against stage 4's "old economy" leg. CV1-P1 and P2 re-measure it on our own free data, with a stated
  exclusion list, because the Letter's grouping is AI *sentiment*, not AI *use*, and its sample and method are not ours.
- **A Grok literature scout (13 Nov) reported Atlanta Fed SBU sales-growth uncertainty modestly lower year on year to
  October 2026 (UNVERIFIED by the supervisor).** For that reason the aggregate SBU series is *not* registered as a test
  of stage 2.

## Registered statements

Common definitions. **AI complex** (excluded from every "ex-AI" sample): SIC 3570–3579, 3670–3679, 4900–4991, 6798,
7370–7379, plus Amazon (CIK 1018724) and Tesla (CIK 1318605) by CIK. **Windows**: treatment 2022→2025 (calendar-year
XBRL frames CY2022, CY2025; quarterly series 2022Q4→latest), placebo 2016→2019 (CY2016, CY2019; 2015Q4→2019Q4).
**Scaling**: every growth rate is stated net of nominal GDP growth over the same window (BEA), so 2022's inflation does
not count as acceleration. **Labels**: SUPPORT / AGAINST / INCONCLUSIVE, by the thresholds given; a statistic exactly on a
threshold is INCONCLUSIVE. The bands are deliberately wide (E-005: a rough answer with a band is a result).

| id | stage | statement | statistic | SUPPORT if | AGAINST if |
|---|---|---|---|---|---|
| CV1-P1 | 4, exclusion | Business investment outside the AI build-out rose as a share of the economy | BEA nominal private nonresidential fixed investment minus information-processing equipment, minus software, minus Census C30 private "Data center" construction (SAAR), as a % of nominal GDP: change 2022Q4→latest quarter, annualised, minus the same over 2015Q4→2019Q4 | ≥ +0.15 pp of GDP per year | ≤ 0 |
| CV1-P2 | 4, exclusion | Listed firms outside the AI complex accelerated capex | Balanced panel of ex-AI filers with `PaymentsToAcquirePropertyPlantAndEquipment` in both end-years of a window; aggregate annualised growth minus nominal-GDP growth, treatment window minus placebo window | ≥ +2 pp/yr | ≤ 0 |
| CV1-P3 | 4, velocity | Corporate idle liquidity was drawn down | Z.1 nonfinancial corporate business: currency and checkable deposits + time and savings deposits + money-market fund shares + repo assets (series FL103020005, FL103030003, FL103034000, FL102051003; builder confirms each ID's description and records it), as % of nominal GDP: change 2022Q4→latest | ≤ −0.5 pp | ≥ 0 |
| CV1-P4 | 4, cash-hoard split | Cash-rich firms led the ex-AI acceleration | P2 panel split into terciles of cash/assets at the window start (`CashAndCashEquivalentsAtCarryingValue`/`Assets`); (top − bottom tercile aggregate annualised capex growth) in treatment minus the same in placebo | ≥ +3 pp/yr | ≤ 0 |
| CV1-P5 | 3, irreversibility split | The acceleration is larger where capex is harder to reverse | P2 panel; high-irreversibility = SIC 1000–1499, 2000–3999, 4000–4899 (all net of the AI complex); low = SIC 5000–5999, 7000–8999 (net of the AI complex); (high − low aggregate annualised growth) in treatment minus the same in placebo | ≥ +2 pp/yr | ≤ 0 |
| CV1-P6 | 1→4, cross-section | Sectors that use more AI accelerated capex more | Census BTOS Sector.xlsx, AI-use "Yes" share (question 7 or its successor), mean over the 2024–2025 cycles, by NAICS sector; against the P2 acceleration (treatment minus placebo growth) of ex-AI filers in the same sector, mapped SIC→NAICS sector by a table the builder states in the code; Spearman rank correlation over sectors with ≥ 20 filers in both windows | ≥ +0.30 | ≤ 0 |
| CV1-P7 | boundary, ex post | Acquisitions made in the boom are written down faster | Ex-AI filers with `PaymentsToAcquireBusinessesNetOfCashAcquired` > 0 in CY2024–2025: sum of `GoodwillImpairmentLoss` in CY2027–2028 over the sum of acquisition spend in CY2024–2025; against the same ratio for CY2015–2016 acquirers' CY2018–2019 impairments | ratio ≥ 1.25× the baseline | ratio ≤ 1.0× | 

**CV1-P7 is long-dated.** It is first scorable when CY2028 annual reports are in the frames, around April 2029 (CALENDAR).
**P1–P6 are scorable now** on the vintages current at build time; every vintage is recorded.

## What cannot be tested on free data, and why

- **Stage 2 at firm level (the mediator).** The free firm-level text-uncertainty file (Hassan et al.) ends in 2021. CRUX
  (Handley and Li) is not posted. Rebuilding a filing-text measure needs 10-K documents from `www.sec.gov`, which
  require a declared contact; the principal's address is approved for supervisor use only, and a corpus pull of that
  size has not been put to him. **Recorded as untested, pending his ruling** (it is his call, not a gap to fill).
- **Due-diligence duration, deal premiums and guidance-range width.** They need SDC, Refinitiv and I/B/E/S, which are paid
  (E-005: not raised, not costed). M&A *counts* from 8-K Item 2.01 via `data.sec.gov` submissions `items` are possible.
  That is an optional P8, added only after the builder shows it is feasible, and registered blind before any count is read.
- **The causal designs (staggered DiD on enterprise-AI access, the shift-share IV).** No free firm-level adoption-timing
  data exist. Occupation exposure (Felten–Raj–Seamans; Eloundou et al.) is free but static. P6 is the furthest the free
  data reach: a sector cross-section, which is descriptive.

## Build (for the builder; not started)

`bin/cv1_confidence_velocity.py` with `selftest`, `fetch` and `build`; outputs in `data/cv1_confidence_velocity/` (`registered.csv` in
the house format with a `prereg_sha256` of this file, `scores.csv`, a README with every source and vintage). Sources: BEA
`Section5All_xls.xlsx`, Census C30 `privsatime.xlsx`, Z.1 `FRB_Z1_csv.zip`, `data.sec.gov` frames, submissions (SIC), Census BTOS
`Sector.xlsx`. The neutral User-Agent is used for every host, **no contact address anywhere**, and `www.sec.gov` is never touched. The script
writes `registered.csv` from this table **before** it computes any statistic, and refuses to score if the hash of this file has changed. A gate is
registered in `bin/check.sh` as the next free g-number at landing.

Every statistic is reported with its denominator: filer counts in each panel and each tercile/sector, and the share of
2025 ex-AI capex they cover.
