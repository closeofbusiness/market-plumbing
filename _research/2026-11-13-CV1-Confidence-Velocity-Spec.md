# CV1 — the confidence / capital-velocity channel: registration and build spec (13 Nov 2026)

**Status: REGISTERED (v2, amended blind 13 Nov), NOT BUILT.** Written before any outcome series below was read by this project. Serves A13
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

## Registered statements — version 2 (amended 13 Nov after the Grok attack, still blind)

Version 1 (commit 6aea2c8) is superseded in full. The attack (`_research/2026-11-13-Grok-CV1-Attack.md`) found every
v1 statement could read SUPPORT while the hypothesis was false, and named the load-bearing flaw: no aggregate or
firm-level capex gap identifies a fall in *managerial uncertainty*. 2022–2025 also contains the CHIPS 25% credit
(from 2023), the IRA clean-energy credits, the restoration of 100% bonus depreciation (property acquired after 19 Jan
2025), AI-adjacent power and factory construction, and acquisition arithmetic. The supervisor accepts this. **v2
labels are therefore asymmetric.** Stage 4 *requires* an acceleration of committed capital outside the AI complex and a
drawdown of liquidity. A clean AGAINST on P1–P3 refutes stage 4 on free data. A SUPPORT says only "consistent, not
identified": it is never written as evidence that AI lowered uncertainty.

Supervisor rulings on the attack: Grok's amendments to P1, P2, P4 and P7 are adopted in substance. P3 is adopted with
one change. P5 is renamed (it no longer claims to test irreversibility). P6 is demoted to description. **Overruled:**
(i) Grok's call to add a contact mailbox to `data.sec.gov` requests. The house rule (12 Sep) is the declared tool name
`ThirdDerivativeResearch/1.0` with no address. `data.sec.gov` answered the inventory scout with HTTP 200, and no
address is ever sent. (ii) P3's automatic INCONCLUSIVE whenever the SOI benchmark year precedes 2025. The benchmark
always lags, so that rule would make P3 unscorable by construction. Instead the readout states the benchmark year,
and the quarterly movement comes from the Census QFR.

**Common definitions.**
- **Windows:** treatment 2022Q4→2025Q4 (XBRL CY2022→CY2025); placebo 2015Q4→2019Q4 (CY2016→CY2019 for the panel).
  Fixed. "Latest quarter" is not used.
- **GDP:** BEA Table 1.1.5 nominal, Table 1.1.6 real (Section 1 workbook).
- **AI complex**, excluded from every ex-AI sample: SIC 3559, 3570–3579, 3661, 3663, 3669, 3670–3679, 4812, 4813,
  7370–7379. Amazon (CIK 1018724), Alphabet (1652044), Meta (1326801), Microsoft (789019), Oracle (1341439), Nvidia
  (1045810) and Tesla (1318605) are excluded by CIK.
- **Separate strata, reported but not in the headline:** utilities SIC 4900–4991 and REITs SIC 6798. Finance (SIC
  6000–6799) is excluded from P2–P5.
- **Panel:** `us-gaap` USD annual frames, 10-K or 10-K/A facts only (joined to submissions), fiscal year-end November,
  December or January. Common firms are those present in all four years CY2016, CY2019, CY2022 and CY2025. A firm is
  dropped from a window if `PropertyPlantAndEquipmentNet` rose more than 25% in a year with
  `PaymentsToAcquireBusinessesNetOfCashAcquired` > 0. SIC is taken from the submissions file and recorded with its
  fetch date. The SIC history is not reconstructed (a known limit).
- **Capex is worldwide consolidated.** GDP is domestic. This is a known limit, stated in every readout.

| id | statement | statistic | SUPPORT (consistent) if | AGAINST (refutes stage 4 leg) if |
|---|---|---|---|---|
| CV1-P1 | Business investment outside the AI build-out and the subsidised factory/power build rose as a share of the economy | Table 5.3.5 nominal private nonresidential fixed investment minus computers and peripherals, communication equipment, software, manufacturing structures, power and communication structures, and mining exploration, shafts and wells; over Table 1.1.5 GDP. Annualised pp change over the treatment window minus over the placebo window. Same object in real terms (Tables 5.3.6 / 1.1.6, as a ratio of chained quantities, labelled approximate). Census C30 "Data center" is a memo line only | both nominal and real gaps ≥ +0.15 pp/yr | both gaps ≤ 0 |
| CV1-P2 | Listed firms outside the AI complex accelerated capex | Common-firm panel: median of firm annualised capex growth minus annualised nominal GDP growth, treatment minus placebo; plus the capex-weighted aggregate of the same | median gap ≥ +2 pp/yr and weighted gap > 0 | median gap ≤ 0 and weighted gap ≤ 0 |
| CV1-P3 | Corporate liquidity was drawn down | Z.1 nonfinancial corporate business: FL104001105 (core liquid assets) + FL103061103 + FL103061703 + FL103069100 (builder confirms each description at build and records it; a mismatch stops the build), over Table 1.1.5 GDP; Q4-to-Q4 change over the treatment window minus over the placebo window | difference ≤ −0.5 pp **and** the nominal dollar stock fell 2022Q4→2025Q4 | difference ≥ 0 **or** the nominal stock rose by more than nominal GDP |
| CV1-P4 | Cash-rich firms led the ex-AI capex change | P2 panel; cash = `CashAndCashEquivalentsAtCarryingValue` (else `CashCashEquivalentsRestrictedCashAndRestrictedCashEquivalents`, never both) over `Assets`, from instant frames CY2015Q4I and CY2021Q4I (the year-end before each window's base year); terciles within 2-digit SIC; tercile growth weighted by base-year capex; statistic (top − bottom) treatment minus (top − bottom) placebo | ≥ +3 pp/yr **and** the top tercile's own treatment growth net of GDP > 0 | ≤ 0 |
| CV1-P5 | Manufacturing, mining and non-utility transport capex growth exceeded trade and services (renamed: **not** an irreversibility test) | P2 panel; high = SIC 1000–1499, 2000–3999, 4000–4899; low = 5000–5999, 7000–8999; trimmed by removing SIC 1311, 1381, 1382, 1389, 2911, 3711, 3721 from high (reported separately); (high − low median) treatment minus placebo | trimmed gap ≥ +2 pp/yr (if only the untrimmed gap clears it: INCONCLUSIVE) | trimmed gap ≤ 0 |
| CV1-P6 | **Descriptive only, no label.** Sector AI use vs sector capex change | BTOS "AI Core Questions (Original)" table, stem "in producing goods or services", "Yes" share averaged over unsuppressed cycles 2024–2025 ending before 17 Nov 2025, no filling of 202521–202523, nothing from the 4 Dec 2025 new series; vs P2 median gap by sector, SIC→NAICS by the Census 1987-SIC→2002-NAICS concordance mapped to NAICS 2-digit, the table hashed before the build; sectors with ≥ 20 common firms; Spearman and leave-one-sector-out range. The question measures production use, not decision support, which is the thesis's own channel. That is stated | — | — |
| CV1-P7 | Boom-cohort acquirers write down a larger fraction within three years | Ex-AI 10-K filers with acquisition spend > 0 in CY2024 or CY2025: Σ `GoodwillImpairmentLoss` CY2026–CY2028 (a missing tag stored as zero) over max(Σ cash acquisition spend, Σ increase in `Goodwill`) CY2024–25; firms that stop filing removed from both sides and counted; baseline = median of the same ratio for the cohorts 2012–13, 2013–14, 2014–15 over the three fiscal years starting two years after each cohort. Recorded caveat: ASU 2017-04 (one-step impairment test) separates the baseline from the treatment; see attack, not verified at FASB | ≥ 1.25× baseline median | ≤ 1.0× |

P1–P5 are scored once at build on the vintages then current. P7 is first scorable around April 2029 (CALENDAR).

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
`Section1All_xls.xlsx` and `Section5All_xls.xlsx`, Census C30 `privsatime.xlsx`, Z.1 `FRB_Z1_csv.zip`, `data.sec.gov` frames, submissions (SIC), Census BTOS
`Sector.xlsx`. `data.sec.gov` gets `ThirdDerivativeResearch/1.0` and every other host the neutral User-Agent; **no contact address anywhere**, and `www.sec.gov` is never touched. The script
writes `registered.csv` from this table **before** it computes any statistic, and refuses to score if the hash of this file has changed. A gate is
registered in `bin/check.sh` as the next free g-number at landing.

Every statistic is reported with its denominator: filer counts in each panel and each tercile/sector, and the share of
2025 ex-AI capex they cover.
