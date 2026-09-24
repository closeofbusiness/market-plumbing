# D-G Remainder - Leveraged ETF rebalancing flows + passive-share model remainder (15 Sep 2026)

**Status: MEASURED where marked; remainder of ranked item D-G / Green numbers.**  
**Parcel:** D-G remainder (leveraged-ETF issuer holdings + passive-model remainder).  
**Data:** `data/dg_remainder/` (AUM snapshot, SOXL/MUU holdings, rebalance scenarios, vol-drag).  
**Evidence bar:** E-005 bands, free sources only. No paid data. Dead corrections C-077-C-086 not revived.

> **[C-087]** Green's ~150%/yr 3× breakeven does **not** reproduce. At `^SOX` 2026YTD realized vol of 49.0% the L=3 breakeven is **24.0%** (log convention; 38.0% on the arithmetic-drift convention). A 150% hurdle needs σ≈122%, or σ≈71% on the drag reading. The daily-rebalance **mechanism stands**; do not restate ~150%/yr as fact.
>
> **[C-088]** The **"Realized ^SOX ann. return" column** in the G-014 table below is wrong in all three checkable cells — trailing-60d reads −52.0% but `^SOX` returned −17.4% (3× that is −52.2%, so the cell holds a levered figure); H1 reads +290.5% against +101.1%; YTD reads +81.8% against +57.2%. **The vol column and every breakeven derived from it reproduce exactly (49.0%), so C-087's verdict is unaffected.** Do not quote return levels from that table; re-derive from source.

## Verdicts (one place)

| Claim | Verdict | One-line why |
|---|---|---|
| **G-008** ($1 in -> ~$2 invested in levered ETFs) | **SUPPORTED (mechanism / 2x case)** | Creation of a 2x product funds ~$2 of underlying exposure per $1 NAV; 3x is ~$3. Distinct from *daily rebalance*, which needs no new cash. |
| **G-012** (~$300M/day passive bid vs ~$3B/day Micron peak from leveraged semi ETFs) | **$3B Micron peak: FOUND, order of magnitude (band); $300M/day: BLOCKED-ON-PROPRIETARY** | Free LETF identity + issuer AUM bounds peak MU mechanical flow at ~$1.3-2.9B on 2026-05-26 / 2026-07-30 melt-up days (MUU+SOXL+/-MULL). Exact $300M Tier1 "passive bid" not reconstructible from free data. |
| **G-013** (~50% of daily price move in melt-up names from mechanical flow) | **BLOCKED-ON-PROPRIETARY** | Requires Tier1 Alpha's impact / attribution model. Free data only shows mechanical dollars can be large vs a normal day and material vs MU ADV (~$35B median), not a 50% attribution share. |
| **G-014** (~150%/yr SOX return needed for 3x LETF breakeven at observed vol; daily rebalance forces buy/sell with no new cash) | **MECHANISM SUPPORTED; ~150% figure NOT reproduced at 2026 SOX vol** | Daily constant-leverage rebalance is real (issuer prospectus + holdings). Continuous vol-drag breakeven for L=3 is mu~sigma^2: with 2026YTD SOX sigma~49%, mu_be~24%, not ~150%. ~150% would need sigma~122% ann. |
| **G-001 remainder** ("his own" passive-share model beyond ICI/Z.1) | **BLOCKED-ON-PROPRIETARY** | Free interviews state estimates (~45-47%, later ~54%) and cite elasticity / Krishnan-Sturm work, but no free reproducible ownership-share methodology beyond denominators already checked in first batch. |

---

## Method

1. **Largest US equity LETFs (free AUM):** Direxion daily holdings CSVs (shares outstanding + holdings % -> AUM) and ProShares product-page net-assets snapshots.
2. **Holdings window:** SOXL and MUU holdings as of **2026-09-15** (issuer files). Daily prices from Yahoo Finance chart API (free). No Morningstar Direct / Compustat.
3. **Rebalance identity (two conventions reported):**
   - Brief / parcel formula: `flow ~ (L - 1) x AUM x r`
   - Standard continuous/futures identity: `flow ~ L(L - 1) x AUM x r`
   - Single-name slice for SOXL: weight x fund-level rebalance (MU weight from issuer file ~ **6.24%** of SOXL AUM).
4. **G-014:** Realized ann. vol of `^SOX` / SOXX / SMH over 2026YTD, H1, trailing 60d/20d, 1y; breakeven mu for zero expected 3x LETF return ~ sigma^2 (L=3). Path check: SOXL cum vs 3x daily-compounded SOXX.
5. **E-006 re-derive:** Algebraic reconstruction of first-batch ICI-derived 63.3% from live Fact Book Fig 2.6 shares (19% index / 11% active of US stocks -> 19/(19+11)).
6. **SEC:** Not required for this parcel (issuer sites + Yahoo). User-Agent rule unused for sec.gov.

**Denominator note:** "AUM" = fund net assets (NAVxshares), **not** gross notional. SOXL holdings confirm equity+swap gross exposure ~ **3.00x** AUM on 2026-09-15.

---

## Load-bearing free numbers

### LETF AUM snapshot (retrieved 2026-09-15)

| Ticker | Leverage | AUM | As-of / source |
|---|---:|---:|---|
| TQQQ | +3x | **$34.75B** | ProShares netAssets snapshot (page date refs 2026-09-14) - https://www.proshares.com/our-etfs/leveraged-and-inverse/tqqq |
| SOXL | +3x | **$17.48B** | Direxion holdings 2026-09-15 (173,250,060 shares; holdings-% implied AUM) - https://www.direxion.com/holdings/SOXL.csv |
| SPXL | +3x | **$6.93B** | Direxion holdings 2026-09-15 - https://www.direxion.com/holdings/SPXL.csv |
| TECL | +3x | **$5.56B** | Direxion holdings 2026-09-15 |
| UPRO | +3x | **$5.32B** | ProShares netAssets - https://www.proshares.com/our-etfs/leveraged-and-inverse/upro |
| MUU | +2x MU | **$3.37B** now | Direxion holdings 2026-09-15 (119,750,020 shares). Peak during melt-up cited ~**$5.4B** (ETF.com feature, free article). |
| TNA | +3x | **$1.23B** | Direxion holdings 2026-09-15 |

SOXL top cash equities on 2026-09-15 (share of **AUM**, not of index): NVDA 6.55%, AMD 6.26%, **MU 6.24% (~$1.09B stock)**, AVGO 5.06%, INTC 4.02%. Swaps supply the remaining leverage; gross equity+swap ~ 3.00x AUM.

### G-008 - $1 -> ~$2

- At **creation**, a constant-leverage bull fund targets Lx exposure: **$1 NAV => ~$L notional**. Green's spoken "$1 come in and $2 gets invested" matches **L=2** exactly; for SOXL/TQQQ (L=3) the analogous figure is **~$3**.
- **Daily rebalance** is a separate channel: after a day-`r` move, the fund must buy/sell ~ `(L-1)Ar` or `L(L-1)Ar` **with no new investor cash** (prospectus: Direxion SOXL 497K / product page - daily repositioning).
- Verdict: **SUPPORTED** as qualitative leverage amplification; do not treat "$2" as the 3x creation multiple.

### G-012 / G-013 - Micron $3B/day and 50% of the move

**Implied MU mechanical flow on melt-up days** (from `mu_rebalance_scenarios.csv`):

| Scenario | MU day | Identity | Implied MU flow |
|---|---|---|---:|
| AUM-now (SOXL $17.5B + MUU $3.4B + MULL ~$0.53B) | 2026-05-26 (+19.3% MU, +5.5% SOX) | brief `(L-1)Ar` | **~$0.87B** |
| same | same | academic `L(L-1)Ar` | **~$1.87B** |
| Peak MUU $5.4B + MULL $0.78B + SOXL now | 2026-05-26 | brief | **~$1.31B** |
| same | same | academic | **~$2.75B** |
| Upper band SOXLx1.5 + peak MUU/MULL | 2026-05-26 | academic | **~$2.93B** |
| Peak stack | 2026-07-30 (+18.4% MU, +8.2% SOX) | academic | **~$2.81B** |

**Band vs Green's ~$3B:** under the academic identity and peak single-stock LETF AUM, **~$2.7-2.9B** lands inside E-005 "order of magnitude / rough band" of $3B. The brief `(L-1)` identity lands ~**$1.3B** - still same order, factor ~2 below. **SOXL alone cannot print $3B into MU** (MU slice only tens-low hundreds of $M even on big SOX days); the **2x single-stock MU products (MUU, MULL)** are the load-bearing channel for a Micron-specific $B flow.

**Context vs tape:** MU median dollar ADV over the last ~3 months ~ **~$35B/day** (Yahoo volumexclose). A ~$3B mechanical buy is ~**8-9% of median ADV** - large enough to matter, not by itself a proof of "50% of the price move."

**$300M/day "overall passive bid":** Tier1 Alpha proprietary flow database (claim text). No free reconstruction attempted beyond noting it is a *different* channel (broad price-insensitive bid) than LETF rebalance. **Blocked-on-proprietary.**

**G-013 ~50%:** same - attribution elasticity is the proprietary object. **Blocked-on-proprietary.** Do not claim we measured Tier1's model.

### G-014 - 150%/yr breakeven and forced rebalance

| Window | ^SOX ann. sigma | mu_be for E[3x LETF]=0 (~sigma^2) | Realized ^SOX ann. return |
|---|---:|---:|---:|
| 2026YTD (to 2026-09-14) | **49.0%** | **24.0%** | +81.8% |
| 2026H1 | 47.8% | 22.8% | +290.5% (path) |
| Trailing 60d | 54.2% | 29.4% | -52.0% |
| 1y | 45.2% | 20.4% | +84.6% |

- To get mu_be ~ **150%** under the standard L=3 formula needs sigma ~ **122%** annualized - far above observed SOX/SOXX vol in these windows.
- Alternate reading (if Green meant the *drag term* `L(L-1)/2*sigma^2 ~ 150%`): still needs sigma ~ **71%**, above realized ~45-55%.
- Path check: 2026YTD SOXL +114% vs 3x daily SOXX +134% vs SOXX +59% - leverage works in a strong trend; drag shows in the gap vs pure 3x compound, not as a 150% hurdle.
- **Mechanism** (daily rebalance with no new cash): **SUPPORTED** (issuer + identity). **~150% number:** **NOT FOUND** at observed vol - treat as possibly a specific high-vol subsample, mis-spoken annualization, or a different breakeven definition; not reproduced here.

### Passive-share model remainder (G-001)

- First batch already: **DIFFERENT DENOMINATOR** vs ICI/Z.1 stock-market measures.
- Free follow-up (Excess Returns transcript / Substack): Green publicly cites ~**54%** passive "by market share" in a later interview and discusses Krishnan-Sturm / Lowe-style **elasticity thresholds** (~75-83% outer limit) - still **no free, step-by-step ownership census** that reconstructs 45-47% or 54% from public holdings.
- Chinco-Sammon (already used) remains the best free *market-cap* passive estimate (33.5% in 2021, broader than disclosed index funds).
- **Close this leg as blocked-on-proprietary** unless Tier1 / Green publishes the ownership algorithm.

---

## E-006 - one prior number re-derived against source

**Target:** first-batch derived figure "index share of domestic-equity **fund** assets = **63.3%** (YE2025)" from ICI Fact Book 2026 Fig 2.6 market-cap shares.

**Live source (retrieved 2026-09-15):** ICI *2026 Investment Company Fact Book* PDF  
https://www.ici.org/system/files/2026-04/2026-factbook.pdf  

Quote (Fig 2.6 discussion): index domestic-equity MF+ETF hold **19%** of US stocks; actively managed domestic-equity MF+ETF hold **11%** (YE2025).

**Re-derive:** 19 / (19+11) = 0.633 => **63.3%**.  

**Match:** exact match to `_research/2026-09-11-DG2-passive_share.csv` `derived_calc` row (63.3).  

**Also live-confirmed:** Fig 2.5 index MF+ETF = **52%** of long-term fund assets YE2025 (same PDF) - matches first-batch primary row.

---

## What survives / fails / blocked

| Survives | Fails / not reproduced | Blocked-on-proprietary |
|---|---|---|
| LETF daily rebalance mechanism; creation leverage ~Lx | G-014's **~150%/yr** SOX hurdle at observed vol | G-012 **$300M/day** passive bid |
| G-008 amplification idea (2x->$2; 3x->$3) | SOXL-alone path to **$3B/day into MU** | G-013 **~50%** price-move attribution |
| G-012 **$3B MU peak** as E-005 band when MUU/MULL+SOXL stacked on >=15-19% MU days | Reconstructing Green's **own** passive % model from free data | Tier1 flow database / impact model |
| Issuer holdings as free primary for weights/AUM | | |

---

## Free sources (URL + retrieval date)

| Source | URL | Retrieved |
|---|---|---|
| Direxion SOXL daily holdings CSV | https://www.direxion.com/holdings/SOXL.csv | 2026-09-15 |
| Direxion MUU / SPXL / TECL / TNA holdings | https://www.direxion.com/holdings/{TICKER}.csv | 2026-09-15 |
| Direxion SOXL product page (daily rebalance disclosure) | https://www.direxion.com/product/daily-semiconductor-bull-bear-3x-etfs | 2026-09-15 |
| ProShares TQQQ / UPRO net assets | https://www.proshares.com/our-etfs/leveraged-and-inverse/tqqq (and `/upro`) | 2026-09-15 |
| Yahoo Finance daily chart API (SOXL, SOXX, ^SOX, MU, peers) | `query1.finance.yahoo.com/v8/finance/chart/...` | 2026-09-15 |
| ICI Fact Book 2026 (Fig 2.5 / 2.6) | https://www.ici.org/system/files/2026-04/2026-factbook.pdf | 2026-09-15 |
| ETF.com feature on MUU crossing ~$5B (peak AUM bound) | https://www.etf.com/sections/features/muu-becomes-fourth-single-stock-etf-cross-5-billion | 2026-09-15 |
| Green claims register | `_research/2026-09-11-Green-Claims.tsv` | on disk |
| First-batch check | `2026-09-11-DG-Green-Numbers-Checked.md` | on disk |

---

## Deliverables on disk

- This file: `2026-09-15-DG-Remainder-Leveraged-ETF-Flows.md`
- `data/dg_remainder/letf_aum_snapshot.csv`
- `data/dg_remainder/soxl_holdings_2026-09-15.csv`
- `data/dg_remainder/muu_holdings_2026-09-15.csv`
- `data/dg_remainder/mu_rebalance_scenarios.csv`
- `data/dg_remainder/soxl_rebalance_last20d.csv`
- `data/dg_remainder/g014_vol_drag.csv`
- `data/dg_remainder/prices_*.csv` (on executor box at /workspace/dg_remainder/; orchestrator may copy)
- Series append fragment: `data/vintages/series_append_2026-09-15-dg_remainder.tsv` (orchestrator should append into `data/series.tsv`)

---

## What to measure next (handover suggestion)

1. **Historical MUU/SOXL AUM path through May-Jul 2026** from free issuer archives / N-PORT if needed, to tighten the $3B peak band (replace "peak $5.4B article" with dated AUMxr).
2. Optional: pull GraniteShares **MULL** holdings/AUM from a free issuer page (Direxion path 404'd) to harden the peer stack.
3. Do **not** spend further free-data cycles trying to reverse-engineer Tier1's $300M/day or 50% attribution - mark closed unless Green publishes method.
4. Orchestrator: register this findings doc in RESEARCH_STATE / check script if required; append vintage series rows; **do not** run `bin/check.sh --handover write` from this parcel.

**check.sh --all:** recommended **after** orchestrator registers the findings + series append (not run by this executor).
