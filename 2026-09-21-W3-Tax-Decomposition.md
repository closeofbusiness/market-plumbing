# W3 — Tax decomposition of the earnings claim (+ W1 ceiling attack)

**Author:** Grok (executor). **Date:** 21 Sep 2026 (Europe/Berlin).
**Spec:** `_research/2026-09-20-W3-Tax-Decomposition-Spec.md`. **C-095 read first.**
**Panel:** `data/w3_tax/firm_tax_panel.csv`, `data/w3_tax/results.json`.
**machineId:** `56a83289-aaaa-453d-a7c7-aa768bd566bb`.

> **C-096 — the Task 2 VERDICT below is rescoped by the supervisor, 21 Sep. The arithmetic stands; the register does not.**
> `min(equity sale, debt acquisition)` is a **ceiling on one recycling route**, not a measurement of it. Life insurers bought
> $612.0bn of debt while selling $194.0bn of equity; P&C bought $364.5bn against $185.0bn — that is a balance sheet growing
> on premium inflow, not rotation out of equities. So the pairing shows what is **possible**, not what is likely. Both $938.4bn
> and ~$258bn are ceilings on the same quantity; **no floor has been established**, and debt is only one destination — netting
> MMF shares, deposits and repo would tighten it further. Read Task 2 as *the interval narrowed*, not as *W1 was 3–4× too big*.
> The measurement that would settle it: Z.1 benefits paid minus contributions received, per sector. **C-097:** the firm panel
> and the raw Z.1 pulls did not land — scalars reproduce, the source derivation is not auditable here.
> **C-098 (22 Sep, under E-007):** the decomposition's pre-tax term was **solved for, not measured**, so "sum check: exact" is arithmetic and not corroboration. Measured directly from this parcel's own panel it is **0.8603**, not 0.7875 — a **0.073 log (7.6%)** gap the identity was absorbing. "74.2%" is withdrawn. Task 1's conclusion holds; its
> precision does not.

---

## C-095 stance (precondition)

SBC, operating-vs-GAAP, and R&D capitalisation are **moot** on Shiller **as-reported (GAAP)** earnings. The live earnings-side inflator inside 2015→2025 is the **2017 tax act** (statutory 35%→21% from 2018). This note measures that term only. No M. No causal price claim (C-077). The tax effect is **real after-tax profit**; the question is how much of Δlog EPS is the rate change rather than the pre-tax business.

---

## Task 1 — tax decomposition

### Identity (accounting, per share)

`Δlog EPS = Δlog(pre-tax) + Δlog(1−ETR) − Δlog(diluted shares)`

| Term | Value | Source |
|---|---:|---|
| Δlog EPS | **1.0613** | Panel / P2a (Shiller as-reported), carried |
| Δlog shares | **-0.1726** | C-093, carried — **not recomputed** |
| Δlog(1−ETR) | **0.1012** | This parcel |
| Δlog(pre-tax) | ~~0.7875~~ → **0.8603** | **C-098** — 0.7875 was the RESIDUAL. Measured directly from this parcel's own panel sums it is **0.8603**; the **0.073 log (7.6%)** gap is real and was being absorbed here. |
| Sum check | 1.0613 | **TAUTOLOGICAL (C-098)** — the pre-tax term was solved for, so this cannot fail. |

Accretion contribution to EPS is `−Δlog shares = +0.1726`.

### Method

- **Universe / weights:** S&P 500 map + 2015 mcap weights from `data/eps_split/` (same universe so terms compose with C-093).
- **Endpoints:** FY2015 and FY2025 only (avoids 2017–18 transition-tax spikes).
- **Source:** SEC companyfacts (`data.sec.gov`), UA `ThirdDerivativeResearch/1.0`, sequential pulls.
- **Tags (consolidated only):** pre-tax `IncomeLossFromContinuingOperationsBeforeIncomeTaxesExtraordinaryItemsNoncontrollingInterest` (primary) / `…MinorityInterestAndIncomeLossFromEquityMethodInvestments` (fallback); tax `IncomeTaxExpenseBenefit`. **Never** Domestic/Foreign as pre-tax.
- **FY pick:** primary `fy==Y` latest period end; fallback Mar–Dec calendar end in Y on consolidated tag only (Visa-class). Jan/Feb ends excluded from fallback.
- **Aggregate ETR** = Σ tax / Σ pre-tax over firms with usable both-year data. **Not** the mean of firm ratios.

### Tag counts (ok panel, n=412)

| Pre-tax tag | FY2015 | FY2025 |
|---|---:|---:|
| `…ExtraordinaryItemsNoncontrollingInterest` | 238 | 376 |
| `…MinorityInterestAndIncomeLossFromEquityMethodInvestments` | 174 | 36 |
| Tax `IncomeTaxExpenseBenefit` | 412 | 412 |

Dom+For both exist: **320** firms; within 2% of consolidated for **258** (2015) and **304** (2025).

### Aggregate ETR

| | FY2015 | FY2025 |
|---|---:|---:|
| Σ pre-tax (USD) | $1069.6bn | $2528.4bn |
| Σ tax (USD) | $292.5bn | $495.9bn |
| **ETR = Σ tax / Σ pre-tax** | **27.35%** | **19.62%** |
| Denominator | Σ consolidated pre-tax, n=412 firms with both years | same |

- Δlog(1−ETR) = **0.1012**
- After-tax multiplier = **×1.106** (inside ×1.05–×1.25 sanity band)
- Positive-pre-tax-only: ETR 26.88%→19.40%; Δlog(1−ETR)=0.0974

### Share of Δlog EPS

| Component | Δlog | Share of 1.0613 |
|---|---:|---:|
| Pre-tax profit | ~~+0.7875~~ +0.8603 | ~~**74.2%**~~ **75.9%** |
| Tax rate (1−ETR) | +0.1012 | ~~**9.5%**~~ **8.9%** |
| Share accretion (−Δlog shares) | +0.1726 | ~~**16.3%**~~ **15.2%** |
| Total | ~~1.0613~~ **1.1341** | 100% |

> **Shares restated under C-098 (22 Sep).** The original column divided by the *carried* Δlog EPS 1.0613 while the pre-tax term came from this panel — two different universes. Dividing by the panel-consistent 1.1341 gives the figures shown. **The conclusion survives, the precision does not:** tax is about a tenth of EPS growth either way (8.9% vs 9.5%). Which basis is right is **untested** — the gap is most likely survivorship in a 412-firm panel of current constituents, but that is a hypothesis, not a finding.

**Tax is about one-tenth of EPS growth** over 2015→2025. Most of the earnings story is still pre-tax.

### Restated 2025 EPS at 2015 ETR — effect on the 70–80% claim

Scale 2025 after-tax by (1−ETR_2015)/(1−ETR_2025) = 0.9038:

| | Actual | Restated at 2015 ETR |
|---|---:|---:|
| EPS factor | 2.890 | 2.612 |
| Δlog EPS | 1.0613 | 0.9601 |
| EPS share of Δlog price (1.2892) | **82.3%** | **74.5%** |

Stripping the ETR decline moves the EPS-share-of-price from ~82% to ~74% — still inside a 70–80 band, but the upper end is tax-assisted. Tax is ~9.5% of EPS growth and ~7.8% of the price move.

Do **not** read this as “tax is not real earnings.” It is real after-tax profit. The decomposition only separates a one-time statutory-rate shift from pre-tax business growth.

### Firm sanity (spec priors)

| | ETR 2015 | ETR 2025 | After-tax mult | Spec prior |
|---|---:|---:|---:|---|
| **AAPL** | 26.37% | 15.61% | **×1.146** | ~26.4%→15.6%, ×1.146 |
| **MSFT** | 34.12% | 17.63% | **×1.250** | ~34.1%→17.6%, ×1.250 |

MSFT Dom+For = consolidated in both years. Aggregate ×1.106 sits below these internationally heavy names, as expected.

### Coverage and missing megas

| | |
|---|---|
| Map | 503 tickers |
| Ok both years | **412/500** |
| 2015-mcap coverage of weighted universe | **94.1%** of Σ 2015 mcap in the eps_split weight file |
| Status | `{'ok': 412, 'missing_year': 91}` |

**Missing megas:** ORCL (FY2025 consolidated pre-tax absent — only Dom+For; excluded); PG (FY2015 consolidated absent; excluded); AVGO (no FY2015 under Broadcom Inc successor CIK). **XOM** CIK overridden to classical `0000034088`.

### Threats (with direction)

1. **Loss-makers** — 35 neg 2015 / 18 neg 2025 / 52 either (of 412). Aggregate Σ first; positive-only path within ~0.5pp / ~0.004 Δlog.
2. **2017–18 contaminated** — endpoints FY2015 & FY2025 by design.
3. **Foreign mix** — could **over-attribute** ETR drop to the 2017 act.
4. **Survivorship** — current S&P 500 = survivors; **overstates** growth vs 2015-constituent panel.
5. **Coverage** — 412/500; 94% of 2015 mcap; missing ORCL/PG/AVGO.
6. **Tag / FY labeling** — fy-primary with Mar–Dec fallback; Dom+For check when both exist.

---

## Task 2 — attack on W1’s $938.4bn ceiling

**Doc:** `2026-09-20-W1-The-Leak-Objection.md`. Named weakness = rebalancing into bonds.

### Pairing: Z.1 debt-security acquisitions vs equity sales (2024Q1–2026Q2)

Debt = FRED `BOGZ1FU*4022*` (USD millions, quarterly; ÷1000 → $bn). Equity sales from W1 / netbuyers (holder role).

| Sector | Equity sales ($bn) | Debt securities net acquisition ($bn) | Rebal capped at equity sale ($bn) | Share of sector equity sales |
|---|---:|---:|---:|---:|
| State and local government employee defined benefit pension funds | 463.9 | **+267.2** | 267.2 | **57.6%** |
| Life insurance companies | 194.0 | **+612.0** | 194.0 | **100.0%** |
| Property-casualty insurance companies | 185.0 | **+364.5** | 185.0 | **100.0%** |
| Federal government pension funds | 67.8 | **+6.5** | 6.5 | **9.6%** |
| Private pension funds, including 403(b) plans | 27.7 | **+145.2** | 27.7 | **100.0%** |
| **Five-sector total** | **938.4** | **+1395.4** | **680.5** | |

**Rebalancing CEILING on the $938.4bn: 680.5 / 938.4 = 72.5%** — the sum of `min(equity sale, debt acquisition)`, which bounds this one route and does not measure it (C-096).

That is large. Say it plainly: **most of the named ceiling is consistent with portfolio rebalancing into bonds, not cash leaving the asset circuit.** Residual upper bound if every dollar of debt buying is rebalancing: **$257.9bn** (~27.5% of ceiling) — untested as consumption (no MPC, no PCE denominator).

Life and P&C bought **more** debt than they sold equities. Federal pensions: little rebalancing ($6.5bn debt vs $67.8bn equity sales).

Series (FU, not SAAR FA): `FU224022045`, `FU544022005`, `FU514022005`, `FU344022005`, `FU574022005`. Artifact: `data/w3_tax/w1_rebalance_attack.json`.

### What else is wrong / weak in W1

1. **Ceiling label without the pair** — after pairing the ceiling tightens from $938.4bn to **~$258bn**. It remains a ceiling (C-096); nothing here bounds it from below, and the one sector showing little bond recycling — **federal pensions, $6.5bn of debt against $67.8bn of equity sales** — sent its proceeds somewhere this pairing never looked.
2. **“Contractual payments to households” > flow identity** — Z.1 equity sales ≠ benefits paid.
3. **Mutual-fund / ETF wrapper point is right** — keep it (~55% seller-side mutual funds vs ETF buys).
4. **Arithmetic “cannot leak” issuance share** — fine; keep ahead of pension block.
5. **P&C role hygiene** — W1’s −185 uses holder (correct).
6. **No MPC / no goods denominator** — W1 already forbids; ban matters more after rebalancing cut.
7. **Stale §4 framing** — W1 already corrects (C-094).

**Verdict (rescoped, C-096):** the named weakness is **real and worth the parcel** — it narrows the interval, which is progress. But it replaces one ceiling with a tighter ceiling; it does not convert either into an estimate. State it as: the contractual channel’s seller-side flow over 2024Q1–2026Q2 is **$938.4bn**, and netting these sectors’ debt purchases tightens the ceiling to **~$258bn**. W1’s caution was right and stays — it is exactly the caution this verdict originally dropped.

---

## What this does / does not say

- **Does:** ~9.5% of 2015→2025 Δlog EPS is the ETR decline; restating 2025 EPS at 2015 ETR moves EPS-share-of-price from ~82% to ~74%. Up to 72.5% of W1’s $938.4bn **could** be bond rebalancing, tightening that ceiling to ~$258bn (C-096 — a bound, not an estimate).
- **Does not:** claim tax is fake; claim the tax cut *caused* prices (C-077); carry an M; reopen SBC / op-vs-GAAP / R&D (C-095).
- **Handover:** not written here — parent will.

---

## Artifacts

- `2026-09-21-W3-Tax-Decomposition.md` (this file, project root)
- `data/w3_tax/firm_tax_panel.csv` — firm-level pre-tax, tax, tags, Dom+For checks
- `data/w3_tax/results.json` — headline scalars
- `data/w3_tax/w1_rebalance_attack.json` — sector debt vs equity pair
- `data/z1_debt/*_BOGZ1FU*.csv` — raw FRED debt-security transactions
