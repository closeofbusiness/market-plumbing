# P4 — spec: how to size price-insensitive demand without a borrowed multiplier (12 Sep 2026)

**Status: RAN 15 Sep — RESULT is a failed first stage (C-086).** Findings `2026-09-15-P4-Russell-Elasticity-Pilot.md`. Spec text below is historical.
Successor to the approach refuted in `2026-09-12-ATT0-First-Attribution.md` (a constant multiplier on Z.1 sector
lines: wrong sign in 2015-19, no single value fits both windows, C-077).

**Supervisor decision (12 Sep).** The spec recommends a regression discontinuity at the Russell 1000/2000
reconstitution cutoff. It is achievable on free data in about an agent-week and would give the project its OWN
falsifiable elasticity for one named price-insensitive mechanism — a real repair of the defect the outside review
found. But by the spec's own statement it yields a stock-level local estimate that does NOT rescale to the market
and cannot size the run-up. Our goal needs dollars at the market level. So: do not start it yet. Re-decide when
the rates-versus-premium split reports — if higher real yields explain most of the multiple, the flow channel's
remaining room is small and a cheaper design (the spec's option (c), mandated and mechanical flows, as a
calibration) is the proportionate next step; if a compressed risk premium is doing the work, the demand-system
route (option (a)) becomes worth its cost and this RD is the right pilot for it.
**Trigger to revisit:** the P2c return, or Martin overruling.

**Access facts established while writing the spec (all checked live, 12 Sep):** SEC's bulk 13F data sets and
N-PORT data sets are free and reachable (200) — quarterly zips through 2026; S&P DJI's announcements page refuses
scripted access (403), as does DOL's and ICI's (a bot block, not a paywall — a browser reaches them). No free
substitute exists for CRSP's delisting-adjusted returns or for Morningstar's assets-by-benchmark tables.

---

## The spec (Sonnet, planning agent)

# Specification: Estimating Price-Insensitive Demand and Its Suppliers (successor to the refuted scalar multiplier)

ATT0 and P3R killed one thing specifically: a constant multiplier M applied to Fed Z.1 sector-flow lines. The sign fails in 2015–19, no M fits both windows, and the load-bearing assumption named in P3R — "that a dollar of price-insensitive net buying in P1 is the same shock M was estimated on" — was never true. A successor must produce its own elasticity, from its own data, with its own falsification test, not borrow a literature number.

## 1. Four candidate designs

**(a) Koijen-Yogo-style demand system (13F + N-PORT holdings).** Models each institution's portfolio weight on a stock as a function of characteristics plus latent demand, aggregates across institutions to a market-clearing price equation, instruments with characteristics of stocks held by similarly-exposed investors. Can identify elasticities **by holder type** (index fund vs. active vs. pension) and aggregate them to a market elasticity — the only design here that natively answers both "how much" and "which holders" together. Cannot identify retail/household demand (13F/N-PORT don't cover them — the same Z.1 plug problem, one level down), cannot see shorts or non-13(f) securities, and full structural estimation (nonlinear GMM, thousands of stocks × managers) is a multi-month project, not an agent-week.

**(b) Index-event design (additions/deletions/reconstitution).** Compares abnormal return and abnormal institutional ownership around a mechanical, price-blind assignment rule (classically the Russell 1000/2000 cutoff). Gives a genuinely causal **stock-level** elasticity and, since the buyer is index funds by construction, answers "which holders" for that one mechanism. Cannot give a market-level number: single-stock demand is far more elastic than aggregate demand (close substitutes exist for one stock, not for equities as an asset class) — rescaling a reconstitution elasticity by market weight is not valid.

**(c) Flow-shock design (mandated/mechanical flows).** 401(k)/target-date rebalancing follows a published, fixed glide path; leveraged-ETF rebalancing is fully deterministic from published leverage and NAV. Both are price-insensitive by construction — the cleanest identification available. But the aggregate dollars are small relative to a $47trn 2024-26 rise, so this design is best used to **calibrate an elasticity parameter**, not to explain the run-up's size directly.

**(d) Fed sector data without a scalar.** Two variants: (i) re-estimate (not import) an elasticity via a granular-instrument/GIV regression on the project's own extended Z.1 panel (2015-2026, already pulled for P1) — fast and free, but inherits the exact specification-fragility (sector grouping, over-identification sensitivity) that sank the borrowed M, so a null here largely reconfirms ATT0; (ii) use Z.1 purely as accounting — net switching against actual issuance/buybacks to test **sign and co-movement only**, attaching no magnitude claim. Cheap, safe, but answers less.

## 2. Data sources (verified live this session, correct SEC UA, ≥1s spacing)

| Design | Data needed | Free source | Verified | Coverage limit |
|---|---|---|---|---|
| (a) | 13F info tables (holder×stock×$/shares, quarterly) | `sec.gov/data-research/sec-markets-data/form-13f-data-sets` — quarterly zips, 2013Q2–2026 (latest window 01Mar–31May2026, ~99MB) | **200 OK**, zip links confirmed | Long-only, managers >$100m, US 13(f) securities only, 45-day lag |
| (a) | Registered-fund holdings (monthly/quarterly) | `sec.gov/data-research/sec-markets-data/form-n-port-data-sets` — quarterly zips through 2026Q2 | **200 OK**, zip links confirmed (project's own D2/C-053 pass used this: 5.3M-row `FUND_REPORTED_HOLDING.tsv`) | Registered funds only — no pensions, insurers, hedge funds, SMAs |
| (a)/(b) | Shares outstanding, fundamentals | SEC XBRL companyfacts/frames API | Not re-fetched (established project convention) | Standardized post-~2009 only |
| (b) | Index membership/effective dates | Provider PDFs (S&P DJI, FTSE Russell); free substitute: issuer 8-Ks + diffing N-PORT holdings of a full-replication ETF (IWB/IWM/IVV) | S&P DJI announcements page: **403 — confirmed bot-blocked**, matching CLAUDE.md's existing spglobal.com note | Provider methodology and float weights are proprietary; only approximable |
| (b) | Daily prices/volume | Stooq bulk CSV, Nasdaq historical (free, no key) | Not fetched this session (time-boxed) | No CRSP-grade delisting/adjustment discipline |
| (c) | 401(k) flows, glide paths | DOL Form 5500 datasets; ICI factbook; TDF 485BPOS prospectuses (EDGAR) | DOL and ICI pages: **403 to plain curl** (WAF-style block, not a real paywall — needs browser); EDGAR 485BPOS unaffected | Aggregate size small vs. the valuation change |
| (c) | LETF rebalancing notional | Issuer prospectuses (ProShares, Direxion) | Not fetched; publicly documented mechanics | Tiny in aggregate dollars |
| (d) | Z.1 sector flow/level/revaluation | `federalreserve.gov/releases/z1` bulk CSV | Already confirmed working (P1, 11 Sep) | Same specification fragility as the refuted M |

**No free full substitute exists** for CRSP (delisting-adjusted returns; Stooq/Nasdaq get partway) or Morningstar's AUM-by-benchmark tables (no comprehensive free "total dollars indexed to X" figure exists — only the largest ETFs' own disclosed AUM).

## 3. Recommended first estimation

**I recommend (b): a fuzzy regression-discontinuity design at the Russell 1000/2000 reconstitution cutoff.** It is the only design that is both fully achievable on confirmed-free data in one agent-week and produces an own-sample, re-testable elasticity tied to a named holder class — directly repairing the defect P3R identified, rather than re-running into it.

**Sample:** Russell 3000 constituents ranked 800–1200 by end-May market cap, for the June 2026 reconstitution, pooled with 2022-2025 (year fixed effects) for power.

**First stage:** ΔOwnership_i = α + β·1{Rank_i ≤ 1000} + f(Rank_i − cutoff) + ε_i, where ΔOwnership is the change in combined 13F+N-PORT institutional ownership share from the pre- to post-reconstitution filing quarter.

**Reduced form:** CAR_i[−5,+5] = γ + δ·1{Rank_i ≤ 1000} + f(Rank_i − cutoff) + η_i, cumulative abnormal return around the effective date (last Friday of June), market-model benchmarked from free daily prices.

**Estimate:** δ/β via 2SLS — dollars of price impact per dollar of mechanically assigned, price-insensitive index-fund demand, local to the cutoff.

**Identification:** rank near the cutoff is "as-if random" with respect to unobserved return determinants — the standard RD continuity argument.

**Falsification:** (i) placebo cutoffs (rank 700, 1300) — should show no discontinuity; (ii) McCrary density test for rank manipulation; (iii) pre-period placebo (no discontinuity the quarter before); (iv) report the full bandwidth/window sensitivity grid rather than one favorable window (Chinco-Sammon found −39.2 vs. −1.1 depending on window alone).

**A null result:** no discontinuity distinguishable from zero once placebo/bandwidth checks are applied, or an estimate that flips sign or halves across windows — mirroring ATT0's own finding of an unstable scalar, and consistent with a documented attenuation of the index effect as more capital anticipates it.

## 4. What this would, and would not, let the project say

It would give a **first-party, falsifiable elasticity** for one real, identifiable price-insensitive mechanism (index-fund rebalancing) in the current market, with named holders and a confidence interval, replacing a borrowed number. It would **not** give the dollar size of the 2024-26 run-up explained by flows (reconstitution flows are small in aggregate), **not** a market-level elasticity (stock-level LATEs do not rescale to the market — the elasticity-puzzle trap), and **not** an answer for the other channels (households, foreign buyers, buybacks) untouched by this event.

## 5. Traps

**Look-ahead:** 13F/N-PORT are filed 45-60 days after period-end; never classify a stock's *historical* index status using *today's* membership. **13F coverage:** long-only, US-listed 13(f) securities, managers >$100m — retail, shorts, and foreign-only holders are structurally invisible, and building a holder-type classifier from filer names is itself "a matching rule as hypothesis" (this project's own C-059 lesson) requiring validation against raw text, not assumed. **One stock ≠ the market:** an RD elasticity is a LATE for stocks near one cutoff, not the market's aggregate elasticity — the two differ because substitutability differs. **Switching is not new money:** any ownership increase at one holder must be netted against the seller and against actual share issuance/buybacks, or the design repeats ATT0's exact error of confusing a reallocation for new demand.

**The single assumption that would sink this design:** that a firm's rank near the cutoff is uncorrelated with unobserved return-relevant characteristics — i.e., no anticipatory arbitrage or rank manipulation. If capital already trades the reconstitution well before the effective date (well documented as the effect has attenuated over time), the measured discontinuity understates or erases the true elasticity without the effect being absent, and this design cannot tell those two cases apart.

### Critical Files for Implementation
- `RESEARCH_STATE.md` (item 4/P3 next-step plan; §0.0 answerability rules)
- `CLAUDE.md` (SEC User-Agent rule, bot-block list, model-routing rules)
- `2026-09-12-ATT0-First-Attribution.md` and `_research/P3R_verification_2026-09-12.md` (what was refuted, and why)
- `2026-09-11-P1-Equity-Net-Buyers.md` and `bin/z1_equity_netbuyers.py` (existing Z.1 pull to extend for design (d))
- `_research/2026-09-11-P3-papers.csv` (the reconstitution/demand-system papers already read at source: Pavlova-Sikorskaya, Chinco-Sammon, Parker-Schoar-Sun)
