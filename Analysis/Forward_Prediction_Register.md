# PRE-REGISTERED FORWARD PREDICTION REGISTER
## Applying the discriminating test to six live capacity events
**Registered: 2 August 2026, 00:00 UTC. Registrant: Claude Opus 5. No outcome in any window below is known to the registrant.**

---

## 0. REGISTRATION DISCIPLINE

**Frame.** Every registration below follows the Input-Price Frame: a named metered input `P(t)` with a quotable published series; a build-justifying price `P*` recovered from documents; a threshold downstream business class at a stated NAICS level with a customer set distinct from the builders'; and a PASS/FAIL scorecard on C1–C9 — all fixed **before** the outcome window. Nothing scored after an outcome is admissible as evidence *for* the framework.

**Data vintage.** `[V]` = verified by direct fetch on 2 Aug 2026, source named. `[E]` = registrant estimate at knowledge cutoff (May 2026); the scorer **must** pin the true value from the named document before scoring, and any prediction whose sign depends on an `[E]` value is void if the true value differs materially.

**Standing rule adopted from the test.** Where the candidate residue is *competing output capacity in the market it was built to serve*, the framework does not apply and the correct forecast is Klepper consolidation. I apply this ruthlessly below and it disqualifies more of the AI buildout than it admits.

**Verified anchor prices, 2 August 2026:**

| Series | Value | Source `[V]` |
|---|---|---|
| H100 SXM, on-demand median | **$3.34/GPU-hr** (avg $3.95, 142 listings) | getdeploying.com/reference/cloud-gpu/nvidia-h100 |
| H100 SXM, spot average | **$1.83/GPU-hr** (55 listings, floor $0.38) | ibid. |
| H100 SXM, custom-contract average | **$1.89/GPU-hr** (6 listings) | ibid. |
| H200, entry price | **$1.20/GPU-hr**, 33 providers | ibid. |
| B200, on-demand average | **$6.85/GPU-hr** (37 listings) | getdeploying.com/reference/cloud-gpu/nvidia-b200 |
| B200, spot / custom-contract average | **$3.77 / $3.49/GPU-hr** | ibid. |
| Polysilicon N-type dense, China | **32.5 RMB/kg** (stable); outside China $17.50/kg | energytrend.com/solar-price.html, 29 Jul 2026 |
| PV module 182mm TOPCon | **0.67 RMB/W ≈ $0.093/W** (−1.47% w/w) | ibid.; wafer inventories >28 GW |
| DDR5 16Gb spot avg | **$50.97**; DDR4 16Gb contract avg $42, **+5.00%** | trendforce.com/price/dram, 31 Jul 2026 |
| AI capex state of play | Amazon capex tracking **$220bn/yr**, driven by AI *memory* costs; AWS fastest growth since 2021; enterprise cloud infra $143bn in Q2 2026, 11th consecutive growth quarter; **no oversupply or lease-termination signals in the trade press** | datacenterdynamics.com, 30–31 Jul 2026 |
| Biotech | 15 IPOs YTD 2026; reverse-merger surge; argenx/Forte $2.2bn (27 Jul); J&J option on Sail ~$2.6bn | biopharmadive.com, 2 Aug 2026 |

**Critical context for the whole register: as of today there has been no cessation event in AI. This is a registration written at the top of the boom, which is the only time a pre-registration is worth anything.**

---

## 1. HEADLINE VERDICTS (one line each, before the detail)

| # | Event | Verdict on the discriminating test | Predicted outcome |
|---|---|---|---|
| **AI-1** | Accelerator fleets ($/GPU-hr) | **FAILS C3, C4, C5** | No third order. Klepper consolidation. Distressed silicon confers zero durable advantage. |
| **AI-2** | Power, interconnection, shells ($/MW-yr) | **PASSES C2–C6; FAILS C8 today; C1 split; C9 FAIL** | The only durable residue. But **incumbent capture** — utilities and existing DC platforms, not a new cohort. |
| **AI-3** | Tokens ($/M at fixed capability) | **PASSES C2, C3, C6, C8; C1 ABSENT; C5 FAILS at ~7×/yr** | A real, large input-price reset **with no bust and no write-down**. The framework's mechanism is not merely rare here — it is *absent from the most important case of the decade*. |
| **B1** | Chinese solar + battery | **PASSES C2, C3, C6, C8, C9; FAILS C1 as written** | **The framework's highest-priority live falsifier, and I predict it falsifies C1's necessity by 2029.** |
| **B2** | Post-2022 biotech / lab-space collapse | **PASSES C1, C4, C5, C6, C7, C8, C9. C2 split, C3 passes on the CDMO fork only** | **Best-scoring case in the register — better than AI.** Non-obvious. |
| **B3** | US office CRE | **PASSES C1, C4, C5, C6, C8, C9; FAILS C2** | Mostly ordinary fire-sale destruction, with a narrow residential-conversion residue. |
| **B4** | LEO constellations round two | **FAILS C3, C4, C5** | **Cannot repeat Iridium — precisely because launch got cheap.** Spectrum transfers; satellites go to zero. |
| **B5** | European electrolysers | **FAILS C2, C4, C5** | Cleantech 1.0 replayed. Total loss, no residue. |

---

## 2. REGISTRATION AI-1 — ACCELERATOR FLEETS

**Metered input P.** Primary: *custom/committed-contract average $/GPU-hour*, as published at `getdeploying.com/reference/cloud-gpu/nvidia-{h100,b200}`, read on the first business day of each calendar quarter and archived to the Wayback Machine that day. Secondary confirmation series: *on-demand average* on the same page. Fixed six-vendor sub-basket for index-drift control: RunPod, Lambda, CoreWeave, Vast.ai, Nebius, Together — 8×GPU on-demand list price, US region.

**P\*, recovered from documents (declare now, verify against filings).**
- H100: $50k all-in capitalised cost per GPU (system + network + share of shell/power); 5-yr straight-line; 85% utilisation (44,676 billable GPU-hours); 13% blended cost of capital reflecting GPU-backed private credit; opex $0.22/hr. → **P\*(H100) = $2.60/hr.** At 6-yr life, $2.20/hr. `[E — pin from CoreWeave/Nebius/Crusoe 10-K depreciation notes and from GPU-backed ABS offering documents]`
- B200/GB200: $85k all-in per GPU; same assumptions. → **P\*(B200) = $4.75/hr.** `[E]`

**T0 (date P crosses below P\* and stays).**
- H100, committed series: $1.89 < $2.60 → **already crossed.** Registrant asserts T0(H100) fell between Q3 2024 and Q2 2025; **for scoring, T0(H100) := 1 January 2025** unless archive snapshots show otherwise.
- B200, committed series: $3.49 < $4.75 → **already crossed.** Registrant asserts **T0(B200) := 1 April 2026**; pin from archives.
- On-demand series: H100 at $3.34 has **not** crossed; B200 at $6.85 has **not** crossed.

**Threshold business class.** *Not nameable at a distinct-customer NAICS level.* The buyers of GPU-hours are AI labs and AI-application companies — the same buyers the builders are already fighting over. **This is the C3 failure and it is dispositive.**

### Scorecard AI-1

| Cond. | Score | Basis |
|---|---|---|
| **C1** alienable control | **SPLIT** | Hyperscaler-owned fleet (majority): **FAIL** — funded from retained cash flow and IG debt, carried at book, no forced write-down mechanism. *This is the Japanese-bank pattern, not the US-telecom pattern.* Neocloud/private-credit fleet: **PASS** — GPU-backed loans, ABS, SPV project debt with ratings and LTV triggers held by mark-to-market and ratings-sensitive holders. |
| **C2** output-demand survival | **PASS** | Physical inference volume grows through any financing shock. |
| **C3** cross-market input | **FAIL** | Competing output capacity in the market of the build. |
| **C4** substrate/overlay | **FAIL** | Accelerators, fabric optics and generation-specific cooling are pure overlay. |
| **C5** reset persistence | **FAIL, catastrophically** | Real replacement cost per unit of delivered capability deflating ~30–60%/yr on hardware. Threshold is 5%/yr. |
| **C6** metered service | **PASS** | Perfectly metered. Per Finding 3 this predicts **utility returns to asset owners**. |
| **C7** labour recombination | **PASS (US)** / FAIL in enforcing jurisdictions |
| **C8** completion | **PARTIAL** | Deployed fleet commissioned; announced fleet is not. |
| **C9** shared-asset incompatibility | **FAIL** | Cannot name an incompatible shared asset for AWS/Azure/GCP selling cheap inference. **Predict incumbent capture.** |

### Predictions AI-1

**1a.** B200/GB200 on-demand average crosses below $4.75/hr by **31 Dec 2027**.
→ *Falsified if* the getdeploying B200 on-demand average is above $4.75/hr on 1 Jan 2028.

**1b.** H100 on-demand median crosses below $2.60/hr by **30 June 2027**.
→ *Falsified if* above $2.60 on 1 Jul 2027.

**1c. (C5 — the central claim.)** **No company founded after 1 January 2026 whose principal productive asset is distressed-acquired pre-Blackwell silicon (A100/H100/H200) will reach $1bn annualised revenue by 31 December 2032.**
→ *Falsified by one counterexample.* This is the direct Cleantech-1.0 analogue: a distressed 2028 buyer of 2025 silicon is in the position of a distressed 2011 buyer of 2010 solar modules.

**1d. (C1 — the Japanese/US split, checkable now.)** At least **two** of {Microsoft, Alphabet, Amazon, Meta, Oracle} will *shorten* a reported server/network useful life **or** book an AI-infrastructure impairment or restructuring charge of **≥$2bn** in a fiscal quarter ending between **1 Oct 2026 and 31 Dec 2029**; and the first-order consequence will be an accounting adjustment, **not** an asset transfer.
→ *Falsified if* fewer than two do so by 31 Dec 2029, **or** if any of them instead transfers operating control of ≥500MW of AI capacity to an unaffiliated buyer at a disclosed price below 50% of cost in that window.

**1e. (C1 — where forced recognition actually happens.)** At least **three** US or European GPU-lessor / "neocloud" entities with **≥$500m of debt** enter Chapter 11, administration, or a distressed out-of-court restructuring that **extinguishes equity**, between **1 Jan 2027 and 31 Dec 2029**.
→ *Falsified if* fewer than three by 31 Dec 2029.

**1f. (C3 — Klepper, not succession.)** By **31 Dec 2030** the count of independent US/EU GPU-cloud providers with ≥100MW deployed falls **≥50%** from its 2026 peak, and the survivors are predominantly the **earliest and largest** entrants, not post-2026 de novo entrants.
→ *Falsified if* two or more of the top five independent providers by deployed MW on 31 Dec 2030 were founded after 1 Jan 2026.

**1g. THE NAMED ESCAPE HATCH (register it, do not hide it).** DRAM contract prices are **rising 5% month-on-month as of end-June 2026** `[V]`, and an accelerator is substantially a memory asset. If HBM/DRAM scarcity persists, the substrate fraction of an accelerator is larger than I have scored and C5 partially passes.
→ **1g-falsifier of my own C4/C5 scoring:** if, on **31 Dec 2029**, brokered secondary-market prices for used H100 SXM boards exceed **$5,000/GPU** (i.e. >15% of original), my overlay classification of accelerators is wrong and prediction 1c is materially weakened. I am registering this as the most likely way I am wrong about AI-1.

---

## 3. REGISTRATION AI-2 — POWER, INTERCONNECTION, SHELLS

**Metered input P.** Primary: *CBRE North America Data Center Trends, "average asking rate, 250–500 kW requirement, Northern Virginia," in $/kW/month*, semi-annual. Secondary: PJM Base Residual Auction RTO clearing price in $/MW-day (results posted 1 Aug 2025 for DY2026/27; 17–18 Dec 2025 for DY2027/28; DY2028/29 in process as of 12 May 2026) `[V, pjm.com/markets-and-operations/rpm]`.

**P\*.** Build at $10–12M/MW of shell-plus-power capex, unlevered yield-on-cost 8–10% → **P\*(colo) = $140/kW-month nominal.** `[E]`

**Observed P.** Registrant's estimate is **$170–220/kW-month** for large blocks in Tier-1 US markets, with primary-market vacancy near 1–2%. `[E — pin from CBRE H1 2026]` **P is far ABOVE P\*, and rising.**

**→ T0 HAS NOT OCCURRED. The power and shell layer is in shortage, not overbuild.** Everything below is conditional.

**Threshold business class (named ex ante, distinct customer set).** NAICS 221118 / 221121 / 237130 — *dispatchable generation, transmission and large-load interconnection services sold to industrial and municipal buyers who are not AI companies.* Electricity is the general-purpose input par excellence; the buyer of a substation is not the buyer of a GPU-hour. **C3 PASS.**

### Scorecard AI-2

| Cond. | Score | Basis |
|---|---|---|
| **C1** | **MIXED — read the documents now** | Shell + substation under project finance: **PASS** (NextWave pattern). Interconnection queue positions and large-load ISAs containing re-study triggers or non-assignment on change of site/configuration: **FAIL** (German UMTS pattern). PPAs with change-of-control termination: **FAIL**. |
| **C2** | **PASS** — the most robust series in the register |
| **C3** | **PASS** |
| **C4** | **PASS** — highest substrate fraction in the cycle |
| **C5** | **PASS** — transformers, turbines, HV cable, trenching and skilled electrical labour are **flat to rising in real terms**. Registered deflation rate: **negative** (i.e. inflating). |
| **C6** | **PASS** — metered as $/kW-month and $/MWh; a small set of natural aggregators exists |
| **C8** | **CURRENTLY FAIL — the binding condition today** |
| **C9** | **FAIL** — no incompatible shared asset prevents regulated utilities and existing DC platforms from capturing this. **Predict incumbent capture.** |

### Predictions AI-2

**2a.** The metered price of energised, interconnected Tier-1 US datacentre capacity **does not fall below $130/kW-month (2026 dollars)** at any point before **31 December 2029**.
→ *Falsified by* a CBRE, JLL or datacenterHawk published quarterly/semi-annual average asking rate for 250kW+ requirements in Northern Virginia below $130/kW-month before that date.

**2b. (C8 — announced ≠ installed.)** Of AI-datacentre capacity announced between 1 Jan 2024 and 1 Aug 2026 with a stated in-service date on or before 31 Dec 2027, **fewer than 60% will be energised and accepting production load by 31 December 2027.**
→ *Falsified by* an independent commissioning census (DC Byte, datacenterHawk, Synergy) showing ≥60% on-time delivery.

**2c. (C1 document read — the highest-value action available today.)** In **PJM and MISO**, large-load interconnection service agreements and queue positions are **not freely assignable** to a new operator without re-study when the project's configuration or owner changes, and this materially delays reuse of stranded capacity.
→ *Falsified by* the first documented case, 2027–2030, of a defaulted AI datacentre's executed ISA transferring to an unaffiliated buyer **without re-study and without more than 90 days' delay.**

**2d.** Heavy-duty gas turbine lead times **do not normalise before 2029**.
→ *Falsified if* GE Vernova, Siemens Energy or Mitsubishi Power publicly quote available heavy-duty frame slots inside 24 months at any point before 1 Jan 2029, or if large power transformer lead times fall below 100 weeks.

**2e. (C4 — the headline structural claim.)** **Substrate fraction of the 2023–2027 AI capex is 25–35%; the fibre buildout of 1997–2001 was 70–80%.** Therefore this cycle leaves roughly **one third the durable residue per dollar**, and the residue is *power and buildings*, not compute.
→ *Falsified by* a credible bottom-up decomposition (project-finance models, depreciation schedules, construction contracts) showing IT equipment below 55% of total AI-campus project cost for liquid-cooled builds.
→ **Note carefully: this is not a prediction of a bust. It holds even if every dollar earns its return.** Overlay obsolescence and malinvestment are different things, and the framework routinely conflates them.

**2f. (C9 — who captures.)** If a cessation event occurs, the durable substrate is captured by **regulated utilities, existing datacentre platforms (Equinix, Digital Realty, Vantage, Aligned, QTS/Blackstone, CyrusOne/KKR) and infrastructure funds (Brookfield, DigitalBridge, KKR, GIP/BlackRock)** — i.e. **incumbents, not a new cohort.**
→ *Falsified if,* among the ten largest AI-datacentre distressed acquisitions 2027–2031 by MW, **four or more** acquirers were founded after 1 Jan 2023.

---

## 4. REGISTRATION AI-3 — TOKENS, AND THE WRIGHT'S LAW INSTRUMENT

**Metered input P.** Two series, registered separately because **they move in opposite directions and conflating them is the single most common error in this domain**:

- **P_cap** = cheapest blended (3:1 in:out) $/M tokens for any model at or above a **fixed, ex-ante capability threshold**. Threshold definitions locked now: *"GPT-4-class" := ≥ the Artificial Analysis Intelligence Index score attained by GPT-4o as of 1 Jan 2025.* *"Frontier-2026-class" := ≥ the AA index score of the highest-scoring model on 1 Aug 2026 (the Claude Opus 5 / GPT-5.6-Sol tier)* `[V, artificialanalysis.ai/models]`.
- **P_task** = $ per *completed task* at frontier capability, for three named tasks (below). This series falls far more slowly than P_cap, because reasoning budgets are rising as fast as per-token prices fall.

**Fitted rate for P_cap (the Farmer–Lafond / Nagy-Farmer-Bui-Trancik instrument, used within its licence).** Anchors: Mar-2023 GPT-4 blended $37.5/M → Nov-2023 GPT-4-Turbo $15/M → May-2024 GPT-4o $7.5/M → Jul-2024 GPT-4o-mini $0.26/M → 2025 $0.10–0.15/M → **Aug-2026 ≈ $0.05/M `[E — pin from AA archive]`**.
- **Central estimate: 0.85 log₁₀ per year (≈ 7× per year). Registered 80% interval: 0.40 to 1.20 log₁₀/yr (2.5× to 16×/yr).**
- Per Sahal's conjecture (Nagy et al. 2013): with cumulative token production growing exponentially, the Wright and Moore forms are observationally near-identical here, so the time-based fit is used and the Wright form is not claimed to add information.
- **What this licenses and nothing more:** a calibrated cost bound on a *named* artefact. It says nothing about which application, which firm, or who captures the value.

### 4.1 Crossing dates for P_cap (from $0.05/M on 1 Aug 2026)

| Threshold | Central date | 80% interval |
|---|---|---|
| $0.01/M blended, GPT-4-class | **Q2 2027** | Q1 2027 – Q2 2028 |
| $0.001/M | **Q3 2028** | Q1 2028 – Q4 2030 |
| $0.0001/M | **Q4 2029** | Q1 2029 – Q1 2033 |

→ *Falsified if* realised prices fall outside the 80% interval on more than 20% of the registered checkpoints, checked quarterly against the Artificial Analysis archive.

### 4.2 Which applications are genuinely PRICE-blocked (the framework's whole domain here)

**Most "AI will do X" claims are not price-blocked and the framework must say nothing about them.** Classifying the blocker is the discipline:

| Blocker | Examples | Framework says |
|---|---|---|
| **PRICE-blocked** | continuous video understanding; exhaustive (not sampled) inspection of very-high-N streams; long-horizon agents; per-capita tutoring/monitoring in low-income markets; translation of *all* voice traffic | **Applies. Predictions below.** |
| **RELIABILITY-blocked** | autonomous SWE to merged-PR standard; unsupervised clinical decisions | Silent |
| **LIABILITY-blocked** | legal advice, diagnosis, financial advice, driving | Silent; value goes to whoever absorbs liability |
| **DATA-ACCESS-blocked** | claims, EHR, banking core, industrial telemetry | Silent; value goes to data holders |
| **DISTRIBUTION-blocked** | consumer assistants | Silent; value goes to OS/handset/seat holders |
| **POWER-blocked** | new frontier training runs pre-2029 | See AI-2, C8 |

### 4.3 Three named price-blocked applications, with thresholds and dates

**T1 — Adjudicate one insurance claim with attachments.** NAICS **524114 / 524126 / 524292** (health and P&C carriers, third-party administrators) — customer set distinct from GPU buyers, **C3 PASS**. Token load ≈ 200k with reasoning. Incumbent cost $2–6/touch (health), $30–80 (P&C). Threshold at 10% COGS ≈ **$0.20/claim → $1.00/M blended at frontier-reasoning tier.** Today frontier-reasoning blended $6–20/M → $1.20–4.00/claim.
→ **Crossing: Q4 2027 (80%: Q2 2027 – Q1 2029).** *Falsified if* no frontier-tier model is available at ≤$1.00/M blended by 31 Dec 2029.

**T2 — Continuous video understanding, per camera.** NAICS **561621** (security systems services). Incumbent monitoring $15–40/camera/month (US). Threshold at 30% of price: **$5/camera/month = $60/yr.**
- *Event-triggered, ~0.1 fps* → 1.1×10⁹ tokens/camera-yr → needs **$0.055/M**. **Crossing now or already crossed.**
- *Continuous 1 fps* → 1.1×10¹⁰ tokens/camera-yr → needs **$0.0055/M**. → **Crossing Q4 2027 (80%: Q2 2027 – Q3 2029).**
→ **This is my single most confident price-unblocking prediction: persistent per-camera video understanding priced competitively against human monitoring, deployed at ≥1 million US cameras, by 31 December 2028.** *Falsified if* no vendor offers continuous (≥1 fps) AI monitoring at ≤$5/camera/month with ≥1m cameras under contract by that date.

**T3 — Autonomous multi-step software engineering ticket.** Threshold at 15% COGS on a $150–600 ticket = $25–90; at 10M frontier-reasoning tokens and $10/M that is ~$100/ticket. **Crossing imminent for the cheap end.**
→ **But T3 is registered as RELIABILITY-blocked, not price-blocked, and the framework is therefore silent on it.** Recording this refusal is part of the test.

### 4.4 Scorecard AI-3 — and the finding that should most update the operator

| Cond. | Score |
|---|---|
| **C1** forced loss recognition | **ABSENT AND UNNECESSARY.** Token prices are falling because of algorithmic and hardware progress, not because anyone's capital was written down. |
| C2 | PASS |
| C3 | PASS (named NAICS above) |
| C5 | **FAIL at ~7×/yr — meaning nobody gets a durable cost-basis advantage. Everyone gets the reset simultaneously.** |
| C6, C7, C8 | PASS |

**AI-3a. THE MOST IMPORTANT PREDICTION IN THIS REGISTER.** *The largest input-price reset of this decade is happening with no bubble, no bust, no write-down and no asset transfer.* This is the Alibaba/Tencent-cloud, India-Stack, M-PESA, Pix pattern — a hyperscale third order with **no L2 cessation event** — and it is now the fifth such case in the corpus.
→ **Registered claim:** the token-price-enabled downstream businesses arrive on the schedule in §4.1 **whether or not there is an AI capex bust**, and a bust would advance the crossing dates by **less than 12 months**.
→ *Falsified if* a capex cessation event occurs and P_cap shows a **>3× step-decline within 6 months** of it that is not attributable to a named algorithmic or architectural release.
→ **If this survives, the operator should treat it as strong evidence against the framework's centrality, not for it.**

**AI-3b. Frame-void condition.** If a GPT-4o-2024-class model runs locally on a shipping consumer phone SoC at ≥20 tok/s, the metered-input frame loses its referent and this registration is **void, not falsified**. Registrant expects this by **31 December 2028.**

---

## 5. WHAT TRANSFERS, TO WHOM, AT WHAT DISCOUNT

Conditional on a cessation event in the window 2027–2031. Recovery is stated **as a fraction of original installed cost**.

| Asset | Class | Transfers? | To whom | Recovery | Window |
|---|---|---|---|---|---|
| Interconnection rights + **executed, assignable** ISA | Substrate | **Yes** | Utilities; Equinix/DLR/Vantage/Aligned/QTS/CyrusOne; Brookfield, DigitalBridge, KKR, GIP | **100–200%+ (appreciates in use)** | 2027–31 |
| Queue position **without** ISA, or with re-study trigger | Non-alienable | **No — lapses** | nobody | **0%** | German UMTS pattern |
| Substations, HV transformers, switchgear, transmission upgrades | Substrate | Yes | utility or next site owner | **70–110%** | 2027–31 |
| Land + water rights + fibre laterals in constrained markets | Substrate | Yes | same | **100%+** | ongoing |
| Powered shell rated ≥50 kW/rack, liquid-ready | Substrate | Yes | DC platforms, infra funds | **50–80%** | 2027–31 |
| Behind-the-meter / dedicated generation, nuclear PPAs | Substrate | Yes | Constellation, Vistra, NRG, Talen, IPPs, infra funds | **60–100%** | 2027–31 |
| New long-haul + metro fibre built 2024–27 for AI | Substrate | Yes | Lumen, Zayo, Cologix, infra funds | **30–70%** | 2028–32 |
| Chillers, CDUs, cooling towers, UPS, busway | Mid-life | Partially | secondary market, next tenant | **25–50%** | 2027–31 |
| Rack/manifold architecture specific to one accelerator generation | Overlay | Mostly no | scrap | **5–15%** | — |
| 400G/800G optics, fabric-generation switches | Overlay | Partially | secondary market | **10–25%** | — |
| **A100 (Ampere)** | Overlay | Marginal | brokers, academia | **<5% by 2028** | — |
| **H100/H200 (Hopper)** | Overlay | Yes, deeply discounted | Vast.ai-style brokers, second-tier clouds, sovereign and academic buyers where export rules permit | **10–25% in 2028; <10% by 2030** | 2028–30 |
| **B200/GB200 (Blackwell)** | Overlay | Yes | same | **20–40% in 2029; <20% by 2031** | 2029–31 |
| **HBM stacks harvested as components** | **Contested** | Possibly | memory brokers | **>25% if the DRAM shortage persists — the named escape hatch (1g)** | 2027–30 |
| Model weights of failed labs | Overlay | Rarely separately | acqui-hirer | **~0%** | — |
| Trained researchers and infra staff | Human, C7 PASS in CA/WA/NY | **Yes** | hyperscalers, surviving labs | acqui-hire | 2026–30 |
| **Announced-but-unenergised MW** | Nothing | N/A | N/A | **0% — C8 FAIL** | — |

**Master transfer prediction (AI-5a).** In every AI-datacentre distressed disposal 2027–2031 where both a shell-with-interconnection and an accelerator fleet are sold, **the shell-with-interconnection clears at a higher fraction of original cost than the accelerator fleet, in at least 9 of the first 10 observed cases.**
→ *Falsified by* 2 or more counterexamples in the first 10.

---

## 6. CAPITAL THAT WILL SIMPLY BE DESTROYED, WITH NO RESIDUE

Stated specifically and with willingness to be wrong.

1. **Pre-Blackwell accelerators held past 2028.** Terminal recovery <10% by 2029; residue seeds nothing. *Falsified by prediction 1g's $5,000/GPU test.*
2. **Accelerator-generation-specific liquid-cooling and rack infrastructure.** Recovery <20%. This is Solyndra's CIGS line: the building transferred, the chemistry-specific tooling did not.
3. **Fabric-generation-specific optics and switching.**
4. **"AI-native" application companies holding no scarce cospecialised complement.** Registered: **of US venture-backed companies founded 2023–2025 that raised ≥$20m and whose product is primarily an LLM interface with no proprietary data rights, no installed base and no workflow lock-in, ≥70% will have shut down, been acqui-hired below total capital raised, or taken a ≥50% down round by 31 December 2029.** *Falsified by* a PitchBook/Crunchbase cohort study showing <70%.
5. **Sovereign "AI factory" programmes in jurisdictions with non-transferable licences, state ownership and no domestic downstream industry.** German UMTS crossed with the Soviet case. Registered: **≥3 announced national sovereign-compute programmes of ≥100MW or ≥$1bn (announced 2024–2026) will be cancelled, indefinitely delayed, or running below 30% utilisation on 31 December 2029.** *Falsified if* fewer than three. **I am least confident in this one and most willing to be wrong.**
6. **Speculative shells built without interconnection.** C1 and C8 both fail.
7. **Bitcoin-miner-to-AI conversions where power is interruptible and the site lacks water, fibre or latency.** The interconnect is substrate and transfers; the air-cooled mining shell does not. Registered: **fewer than 40% of announced ≥50MW miner-to-AI conversions (announced 2024–2026) will be hosting production AI load by 31 December 2028.** *Falsified by* a DC Byte / datacenterHawk conversion census showing ≥40%.

**Not on this list, deliberately:** power, land, interconnection, generation, fibre and shells. Those are the residue, and there will be roughly $450–750bn of it globally on a $1.5–2.5tn cycle `[E]` — enough to matter, and about a third the residue-per-dollar that fibre left.

---

## 7. REGISTRATION B1 — CHINESE SOLAR AND BATTERY OVERCAPACITY
### *The framework's highest-priority live falsifier. I predict it falsifies C1.*

**P.** 182mm TOPCon module, EnergyTrend weekly quote, RMB/W; and LFP cell ex-works China, $/kWh.
**Observed 29 Jul 2026 `[V]`:** module **0.67 RMB/W ≈ $0.093/W**, −1.47% w/w; polysilicon N-type dense 32.5 RMB/kg, stable; wafer inventories **>28 GW**; prices declining since mid-2025 on inventory pressure.
**P\*.** Full cost including depreciation and financing for 2022–23-vintage integrated capacity: **$0.15/W** modules; **$60/kWh** LFP cells. `[E]`
**T0.** Module price fell durably below $0.15/W in H2 2024 → **T0(China solar) := 1 July 2024.**

**Threshold business class, named ex ante.** NAICS **221114 / 325120-adjacent / 33441**: *unsubsidised, off-grid or behind-the-meter, curtailment-tolerant industrial and residential load in high-irradiance, high-grid-tariff jurisdictions where grid connection is not the alternative.* Customer set — Pakistani textile mills, Gulf desalination and process heat, Indian and Nigerian C&I self-generators, Brazilian and Chilean mining — is entirely distinct from the utility-scale developers the Chinese fabs were built to serve. **Registered exemplar: Pakistan.** **C3 PASS.**

### Scorecard B1

| Cond. | Score |
|---|---|
| **C1** | **FAIL as written** — no forced loss recognition, no alienable control transfer; local-government and bank forbearance plus 2025–26 "anti-involution" supply discipline. **PASS only under the realised-input-price restatement, which the test itself warns is tautologising.** |
| C2 | **PASS** — global installed GW still growing |
| C3 | **PASS** on the off-grid/industrial fork; FAIL on the utility-scale fork |
| C4 | **FAIL** for manufacturing capacity (TOPCon lines cannot make tandem/perovskite — Solyndra at national scale); PASS only for polysilicon plants with captive cheap power in Xinjiang/Inner Mongolia/Yunnan |
| C5 | **SPLIT** — FAIL for buyers of solar *manufacturing* assets; PASS for downstream buyers of *modules*, because module is now <30% of installed system cost and BOS/land/labour dominate |
| C6 | **PASS, maximally** — the most fungible, most metered industrial good in the world |
| C8 | **PASS** — the fabs are built and running |
| C9 | **PASS, and nameable:** incumbent utilities cannot capture the off-grid third order because their shared asset — the regulated volumetric tariff that recovers network cost — is precisely what the off-grid buyer is escaping |

### Predictions B1

**B1-a.** 182mm TOPCon module price **does not exceed 0.85 RMB/W on a 3-month moving average before 31 December 2028** (i.e. anti-involution supply discipline fails to raise price durably).
→ *Falsified by* a 3-month MA above 0.85 RMB/W on the EnergyTrend series.

**B1-b.** At least one non-EU/US importing country records **off-grid or behind-the-meter solar exceeding 25% of national grid peak demand by 31 December 2028**; registered exemplar **Pakistan**.
→ *Falsified if* no such country crosses 25% per IEA-PVPS or Ember.

**B1-c. (C1's necessity, the falsifier proper.)** By **31 December 2029**: (i) the downstream off-grid/behind-the-meter industrial solar class in importing countries exceeds **$50bn/yr** of equipment plus installation revenue, **and** (ii) **no more than two** of the top-10-by-2023-shipments Chinese module makers has undergone a control-transferring insolvency.
→ **If both hold, C1's necessity is FALSIFIED** and the framework must restate C1 at the level of realised input price — accepting the tautology cost the test names. **If a wave of control-transferring Chinese insolvencies occurs first, C1 survives.**
→ This is the single most decisive scheduled observation in the whole register.

**B1-d.** LFP cell ex-works China falls below **$45/kWh on a quarterly average before 31 December 2028**; and BESS attach rate on new utility-scale solar in India, Saudi Arabia and Pakistan exceeds **40% of new GW by 2029**.
→ *Falsified* on either leg.

**B1-e. (Teece / Finding 3 — who captures.)** Value accrues to importing-country distributors and EPC/installers, industrial self-generators, inverter and BOS firms with installed-base service relationships, and firming providers — **not** to the module makers and **not** to buyers of distressed module plants.
→ *Falsified if* any Chinese module maker records **ROIC >15% for two consecutive years before 2030.**

---

## 8. REGISTRATION B2 — POST-2022 BIOTECH / LIFE-SCIENCE LAB SPACE
### *Best-scoring case in the register. This is the surprise.*

**P.** Primary: *Cambridge/Boston Class A lab asking rent, $/sf NNN* (CBRE, JLL or Newmark quarterly Boston life-science report). Secondary: reverse-merger implied $ per clinical-stage asset.
**P\*.** Development pro formas 2021–22 underwritten at **$85/sf NNN** on $1,000–1,500/sf construction. `[E]`
**Observed.** ~$60–75/sf asking with heavy concessions; effective rents lower; vacancy >30%. `[E — pin from CBRE Boston Q2 2026]`
**T0 := Q3 2024.**

**Threshold business class.** NAICS **325414 / 541714** — *contract development and manufacturing (CDMO) and GMP biologics/cell-therapy suites serving large pharma, GLP-1 fill-finish, ADC and cell-therapy sponsors* — a customer set distinct from the venture-backed discovery companies the buildings were financed for. **C3 PASS on this fork only.**

### Scorecard B2

| Cond. | Score |
|---|---|
| **C1** | **PASS** — CMBS and construction loans marked to market; foreclosures, deed-in-lieu, note sales at 30–60¢. Genuine forced recognition with control transfer. |
| **C2** | **SPLIT — this is the gate.** FAIL for generic wet-lab bench space (headcount and company counts fell); **PASS for GMP biomanufacturing suites**. |
| **C3** | PASS on the CDMO fork; FAIL for bench-space-as-bench-space |
| **C4** | **PASS (~55–65% substrate)** — shell, floor-to-floor height, structural loading, MEP risers, air-change capacity, vibration criteria are 20–40yr substrate; casework and cleanrooms are overlay |
| **C5** | **PASS — strongest C5 pass in the register.** Lab/GMP construction cost is flat to **rising**. A 2025 buyer at $300–500/sf against $1,000–1,500/sf replacement holds a durable basis. |
| **C6** | PASS — metered $/sf/month; natural aggregators exist (Alexandria, Blackstone, Longfellow, IQHQ, Breakthrough, specialist CDMOs) |
| **C7** | **PASS strongly** — Massachusetts non-competes largely unenforceable since 1 Oct 2018; California never enforced. Massive 2022–26 layoffs released experienced CMC, clinical and regulatory operators into non-enforcing jurisdictions. |
| **C8** | PASS — buildings are built |
| **C9** | **PASS, nameable:** incumbent life-science REITs cannot lease at the new clearing price without triggering mark-to-market across the whole rent roll and breaching covenants — a named, specific, incompatible shared asset. Predicts capture by **new-basis owners and CDMOs**, not incumbent REITs. |

### Predictions B2

**B2-a.** By **31 December 2029**, at least **three** US CDMOs or clinical-stage platform companies operate at scale out of buildings acquired 2024–2028 at **<40% of replacement cost**, and at least one exceeds **$500m annual revenue**.
→ *Falsified if* fewer than three.

**B2-b. (F1(c) reset test.)** Cambridge lab market-wide average asking rent **does not return to $100/sf NNN before 31 December 2029**.
→ *Falsified by* any CBRE/JLL/Newmark quarterly print ≥$100/sf NNN before that date. If it does recover, the episode was an ordinary inventory cycle in a technological costume.

**B2-c.** Count of US-listed biotechs trading **below net cash falls below 50 by 31 December 2027** — i.e. the reset resolves through recapitalisation and reverse merger rather than asset transfer. *The 2026 evidence already points this way: 15 IPOs YTD, a reverse-merger surge, argenx/Forte $2.2bn on 27 July, J&J/Sail ~$2.6bn* `[V]`.
→ *Falsified if* above 50 on 31 Dec 2027. **Note this prediction cuts against the framework: it is Finding 1(a) — different cost basis, same people.**

**B2-d. (Klepper identity test, run properly.)** Of the ten largest US biotechs by market cap on **31 December 2031, zero will have been founded after 1 January 2023.**
→ *Falsified by one.*

**B2-e. (C7 natural experiment — runnable now.)** New biotech formation per laid-off scientist will be **materially higher in MA and CA (non-enforcing) than in NJ and PA (enforcing)** over 2024–2029, controlling for cluster size.
→ *Falsified if* the MA/CA formation rate is not statistically distinguishable from NJ/PA at conventional significance. This is the Babina / Marx / Fallick design and it is the cleanest C7 test available anywhere in the register.

---

## 9. REGISTRATION B3 — US COMMERCIAL REAL ESTATE (OFFICE)

**P.** Green Street CPPI office sub-index; and $/sf traded price for Class B/C CBD office.
**P\*.** Replacement cost **$400–600/sf** in major CBDs. Observed distressed trades 2023–26 at **$50–200/sf** in San Francisco, Chicago, downtown LA, St. Louis, Baltimore. `[E]`
**T0 := 1 January 2023.**

### Scorecard B3

| Cond. | Score |
|---|---|
| **C1** | **PASS, strongest in the register** — CMBS special servicing, foreclosure, note sales, deed-in-lieu. Control moves. |
| **C2** | **FAIL.** Physical demand for office square-footage did *not* survive: occupied square feet peak-to-peak+5 is **negative**. Per the test, this is Ramey–Shapiro territory — ordinary fire-sale value destruction. |
| **C3** | **PASS only on the residential fork** (NAICS 5311, distinct customer set), and only for buildings with <45ft window-to-core depth, replaceable curtain wall, and by-right conversion. FAIL for datacentre conversion on physical grounds (floor loading, power density, cooling, floorplate). FAIL for lab conversion — that wave *was* the malinvestment (see B2). |
| **C4** | **PASS** — frame, foundation, cores and utility feeds are 50–100yr substrate |
| **C5** | **PASS** — urban construction cost rising 3–6% nominal; a 2024 buyer at $100/sf against $500/sf holds a durable basis |
| **C6** | PASS |
| **C8** | PASS |
| **C9** | **PASS, nameable:** office REITs cannot convert because debt covenants, appraisal-based NAV and an existing rent roll make the write-down unacceptable, and their operating platform is commercial leasing, not multifamily |

### Predictions B3

**B3-a.** Cumulative US office-to-residential conversion **completions** for 2024–2029 inclusive land between **90,000 and 220,000 units** (RentCafe/Yardi/CBRE conversion trackers).
→ *Falsified below 90,000* (the residential fork failed) *or above 220,000* (my C2 FAIL scoring was too pessimistic).

**B3-b.** **No** US office building above 40 storeys built before 1990 is converted to a production AI datacentre of **≥20MW IT load and energised by 31 December 2030.**
→ *Falsified by one.* This tests the popular office-to-datacentre claim, which I predict fails on floor loading, power and cooling.

**B3-c. (F1(c).)** Green Street's office CPPI **does not regain its 2022 peak before 31 December 2032.**

**B3-d. (C9 / the only defensible identity test.)** Of the twenty largest US office-to-residential conversions completed 2024–2030 by unit count, **fewer than four** are executed by the institutional owner that held the asset at the 2022 peak.
→ *Falsified by* four or more.

---

## 10. REGISTRATION B4 — LEO CONSTELLATIONS, ROUND TWO
### *Cannot repeat Iridium, precisely because launch got cheap.*

**P.** $/Gbps-month of LEO capacity to a fixed/maritime terminal; upstream, **$/kg to LEO** on a commercially quoted dedicated basis.
**The decisive registered fact:** $/kg to LEO fell from ~$10,000–20,000 (Ariane 5 / Atlas V era) to ~$1,500–2,700 (Falcon 9) and is heading lower. `[E]` **Real replacement cost of a constellation is deflating at perhaps 20–30%/yr.**

The test records that **Iridium passed C5 only because "pre-reusable-launch, constellation replacement cost was flat to rising, so the $25m basis stayed advantaged for over a decade."** That condition is now reversed.

### Scorecard B4

| Cond. | Score |
|---|---|
| C1 | **PASS** for Eutelsat/OneWeb, Telesat, AST, Globalstar and Chinese/European operators. **FAIL** for Starlink and Kuiper — retained inside balance sheets that will not force recognition (the Japanese pattern again). |
| C2 | PASS |
| **C3** | **FAIL for broadband** — competing output capacity sold into the same consumer/enterprise broadband market. Klepper, not succession. **PASS narrowly for direct-to-device sold to MNOs** (NAICS 517312), a genuinely distinct customer set. |
| **C4** | **Satellites are OVERLAY** (5–7yr design life, deorbit, high customisation). **The substrate is spectrum, orbital slots, ITU filings and market-access licences** — maximum durability, zero customisation. Exactly the NextWave pattern. |
| **C5** | **FAIL for satellites and launch. PASS for spectrum.** |
| C6 | PASS — metered in Gbps-month |
| C8 | MIXED — Starlink complete; Kuiper partial; Telesat Lightspeed and Chinese constellations partial; several announced only |
| **C9** | **FAIL** — MNO incumbents face no incompatible shared asset with D2D; they will partner, not be displaced. **Predict incumbent capture.** |

### Predictions B4

**B4-a.** At least one of {Telesat Lightspeed, AST SpaceMobile, Globalstar, a Chinese or European LEO operator with ≥$1bn raised} undergoes a **control-transferring restructuring, state rescue, or acquisition below invested capital by 31 December 2030.**
→ *Falsified if none.*

**B4-b.** In any such transaction, the acquirer's disclosed rationale centres on **spectrum rights and market-access licences, not the in-orbit hardware.**
→ *Falsified by* a transaction whose stated rationale is the satellites.

**B4-c. THE ANTI-IRIDIUM PREDICTION.** **No LEO broadband constellation acquired out of distress after 1 January 2026 reaches positive free cash flow within five years of acquisition** — because, unlike Iridium, replacement cost is falling and a competitor can outbuild the distressed basis.
→ *Falsified by one counterexample.*

**B4-d.** Commercially quoted dedicated $/kg to LEO falls **below $1,000 by 31 December 2029.**
→ If it does **not**, C5 partially passes for constellations and B4-c weakens accordingly.

---

## 11. REGISTRATION B5 — EUROPEAN ELECTROLYSER AND GREEN HYDROGEN CAPACITY (short)

**P.** €/kW installed alkaline/PEM electrolyser; and €/kg delivered green hydrogen.
**Scorecard:** **C2 FAIL** — output demand for green hydrogen at the announced prices never materialised; announced European electrolyser manufacturing capacity vastly exceeded orders and manufacturers entered distress from 2025. **C4 FAIL** — stack manufacturing lines are chemistry- and format-specific overlay, Solyndra exactly. **C5 FAIL** — stack cost still deflating. **C8 FAIL** — most announced GW never built.
**Verdict: the cleanest predicted null in the register. Total capital destruction, no residue, no third order.**
**B5-a.** **No European electrolyser or green-hydrogen third-order business exceeding €500m annual revenue emerges from assets acquired out of 2025–2029 distress, by 31 December 2032.**
→ *Falsified by one.*
**B5-b.** The residue that *does* transfer will be **the grid connections and industrial land**, not the stacks — the same substrate/overlay split as everywhere else.

---

## 12. CROSS-CUTTING TESTS, SIDE BETS, AND THE MASTER CALENDAR

### 12.1 F3 mechanism tests (both must pass or the framework is indistinguishable from a fire sale)

**F3(i) Post-transfer utilisation (Bernstein–Colonnelli–Iverson design).** For each transfer scored above, physical utilisation must **rise** after transfer.
- Registered: rises for AI shells/substations (2027–31); rises for B2 lab-to-GMP conversions; rises for B3 office-to-residential; **falls or stays flat for distressed accelerators**; **falls for LEO satellites**.
- → *Falsified if* utilisation of transferred AI shells does not exceed pre-transfer utilisation within 24 months in a majority of observed cases.

**F3(ii) Insider-premium sign (Ramey–Shapiro λ_insider).** The framework requires λ **negative** (outsiders pay more) in the cases it claims.
- Registered: λ negative for B3 office-to-residential (multifamily operators outbid office REITs) and for B2 lab-to-GMP (CDMOs outbid discovery tenants); **λ positive for accelerators** (surviving compute providers outbid outsiders), which is *consistent with the framework because AI-1 fails C3 and the framework does not claim it.*
- → *If λ is uniformly positive across all six registrations, the mechanism claim should be abandoned regardless of how F1 performs.*

### 12.2 INADMISSIBLE SIDE BETS (segregated on purpose)

Per "what the framework cannot do" #1, the framework has **exclusion power, not selection power** (Li & Neffke: 3.36% vs a 2.68% base rate). Anything below is a personal pick and is **inadmissible as evidence for the framework** in either direction:
> After inference prices collapse, value accrues to holders of scarce cospecialised complements, in this ranked order: **(1) contractually-locked distribution** (OS defaults, handset and browser placement, enterprise seat relationships); **(2) regulated or non-scrapable data** (claims, EHR, banking core, legal dockets, industrial telemetry); **(3) system-of-record workflow lock-in**; **(4) firm dispatchable power and interconnection**; **(5) liability-absorption capacity in regulated professions.** Explicitly **not**: model labs per se, GPU owners, or neoclouds.
→ *Framework-admissible version of this:* **if, on 31 December 2031, three or more of the ten largest AI-revenue companies are pure compute providers earning >20% ROIC, Finding 3 (utility returns to asset owners) fails.**

### 12.3 MASTER FALSIFIER CALENDAR

| Date | Observation due | Kills |
|---|---|---|
| **31 Dec 2027** | Commissioning census: <60% of announced 2024–26 AI capacity energised | AI-2b |
| **31 Dec 2027** | B200 on-demand avg still >$4.75/hr | AI-1a |
| **30 Jun 2027** | H100 on-demand median still >$2.60/hr | AI-1b |
| **31 Dec 2027** | US-listed biotechs below net cash still >50 | B2-c |
| **31 Dec 2028** | 182mm TOPCon 3-mo MA >0.85 RMB/W | B1-a |
| **31 Dec 2028** | No country at 25% off-grid solar share | B1-b |
| **31 Dec 2028** | LFP cells still >$45/kWh | B1-d |
| **31 Dec 2028** | No 1-million-camera continuous AI monitoring at ≤$5/cam/month | T2 |
| **31 Dec 2028** | ≥40% of miner-to-AI conversions hosting production load | §6.7 |
| **31 Dec 2029** | <2 hyperscaler life-shortenings or ≥$2bn impairments | AI-1d |
| **31 Dec 2029** | <3 neocloud equity-extinguishing restructurings | AI-1e |
| **31 Dec 2029** | Used H100 SXM >$5,000/GPU | **AI-1g — my own most likely error** |
| **31 Dec 2029** | Cambridge lab rents back to $100/sf NNN | B2-b |
| **31 Dec 2029** | **$50bn off-grid solar class + ≤2 Chinese insolvencies** | **C1's necessity — the decisive one** |
| **31 Dec 2029** | Tier-1 colo below $130/kW-month at any point | AI-2a |
| **31 Dec 2030** | Independent ≥100MW GPU clouds not down 50%, or new entrants in top 5 | AI-1f |
| **31 Dec 2030** | A 40+ storey pre-1990 office converted to ≥20MW AI datacentre | B3-b |
| **31 Dec 2030** | No LEO operator control-transfer | B4-a |
| **31 Dec 2031** | ≥4 of top-10 AI-DC distressed acquirers founded post-2023 | AI-2f |
| **31 Dec 2031** | Any post-2023 founder in top-10 US biotech | B2-d |
| **31 Dec 2032** | A $1bn-revenue company built on distressed pre-Blackwell silicon | **AI-1c** |
| **31 Dec 2032** | A €500m European hydrogen third order | B5-a |

### 12.4 SELF-SCORING PRIOR (registered so it cannot be revised)

Of the ~34 dated predictions above, I expect **roughly 60–70% to resolve in my favour**, and I expect the failures to concentrate here, in descending order of likelihood:
1. **AI-1g, the memory escape hatch.** DRAM contract prices rose 5% month-on-month at end-June 2026 `[V]` and server demand is crowding out consumer supply. If HBM scarcity persists, my flat classification of accelerators as pure overlay is wrong and predictions 1c and the recovery-rate table are too harsh.
2. **§6.5, sovereign AI programmes.** Weakest evidentiary basis; stated anyway because a register that only contains safe bets is worthless.
3. **B3-a's unit range.** Conversion accounting is inconsistent across trackers and the range may be unfalsifiable in practice; the scorer should fix the tracker now (RentCafe/Yardi) and not switch.
4. **B1-a.** Chinese "anti-involution" supply discipline may work better than I expect; polysilicon has already stopped falling.

And the one thing I would most like the operator to notice: **the largest input-price reset now in progress — token cost at fixed capability, falling ~7× a year — involves no bubble, no bust, no write-down and no asset transfer. On the framework's own accounting that makes five such cases (Alibaba/Tencent, India Stack, M-PESA, Pix, and now inference). The framework describes one route among at least four, and in the defining capacity event of this decade its central mechanism is not rare. It is absent.**

---

**Sources verified 2 August 2026:** [getdeploying H100](https://getdeploying.com/reference/cloud-gpu/nvidia-h100) · [getdeploying B200](https://getdeploying.com/reference/cloud-gpu/nvidia-b200) · [EnergyTrend solar prices](https://www.energytrend.com/solar-price.html) · [TrendForce DRAM](https://www.trendforce.com/price/dram) · [Data Center Dynamics](https://www.datacenterdynamics.com/en/news/) · [BioPharma Dive](https://www.biopharmadive.com/) · [PJM RPM](https://www.pjm.com/markets-and-operations/rpm) · [Artificial Analysis](https://artificialanalysis.ai/models)