# B6 Phase 1 — Payment-Day Mechanism Test

**Date:** 2026-09-15  
**Parcel:** B6 Phase 1 only (BR2 design)  
**machineId:** 56a83289-aaaa-453d-a7c7-aa768bd566bb  
**Object:** Days-horizon temporary price-pressure LATE / mechanism presence  
**Explicit:** This is NOT a multiplier for the household residual / 2024–26 revaluation.

> **[C-090]** **The kill switch tripped on a test with no power, and the null below is uninformative.** Against the effect this design was hunting — Hartzmark-Solomon M≈1.9 applied to the measured payment-yield spread — the calendar-true sample's standard error is **6.2× the predicted effect**, so its minimum detectable multiplier is **M≈23.7**; the full-universe sample's is **M≈12.6**. The published envelope is **1.5–9.4**. Neither specification can reject *any* value in it. Read the result as **BLOCKED on payment-yield variation** (S&P-500-only gives 3–10 payers a day against a marketwide object), **not** as the mechanism failing. The scoping error is the supervisor's: Phase 1 was armed with a kill switch and no minimum-detectable-effect check. Everything else in this document stands — the execution, the placebos, the refusal to promote the imputed t=1.37, and "do not invent an M", which remains correct.

## Verdict

**FAILS KILL SWITCH**

Kill switch (BR2 iv / E-005 rough): **TRIPS**.

Why: On the better-identified sample — S&P500 dividend events with **true Nasdaq-calendar payment dates** — the top−bottom payment-yield-day SPY return gap is **wrong-signed in the raw means** and **indistinguishable from zero after DOW / month / lagged-VIX controls** (controlled top dummy coef = 0.000007, t = 0.01). Do **not** invent an M.

A full-universe build that imputes payment dates for NYSE names (median ex→pay lag) shows a weak positive controlled gap (coef = 0.001141, t = 1.37). That result is **not** treated as mechanism presence: ~78% of events lack true payment dates, so timing error can manufacture a false positive. Primary weight stays on calendar-true dates.

Hartzmark–Solomon (NBER w30688; AER Sept 2025) report market-level M ≈ 1.9 and top-quintile payment-day returns ~4× bottom — **cited only; not re-derived from paid CRSP data**.

## Design (Phase 1 — not widened)

| Item | Choice |
|------|--------|
| Universe | Current S&P500 constituents (Wikipedia / datasets mirror), n=503 tickers |
| Window | 2015-01-01 → 2026-09-15 |
| Payment yield | Σ(DPS × shares_approx) on payment date t / lagged S&P mcap proxy |
| Sort | Positive-yield days → quintiles by payment yield |
| Outcome | Value-weighted market return ≈ SPY close-to-close (GSPC reported) |
| Controls | Day-of-week + month dummies + lagged VIX |
| Placebos | Announcement-date and ex-date cash intensity quintiles (when dates exist) |

### Survivorship (UNCERTAIN)

No free historical S&P500 membership reconstruction was on disk under `data/p4` (P4 has IWB/IWM holdings / Russell panel only). **Current constituents only** — survivorship bias caveat stated.

### Free-data stack

- **DPS + ex-dates:** Yahoo Finance chart API `events=div` (same family as P4).
- **Payment / announcement dates:** Nasdaq `api/calendar/dividends` (true payment dates for names the calendar covers — effectively Nasdaq-listed; NYSE largely absent).
- **Shares / mcap:** Nasdaq quote summary MarketCap / PreviousClose snapshot (applied to all history — level bias).
- **Mcap path:** Σ current constituent mcaps × SPY_t / SPY_now, lagged one day.
- **VIX:** Yahoo `^VIX` chart.
- **Specials filter:** drop DPS > 5% of price or amount > $25.
- **NYSE payment dates:** imputed as ex-date + ticker/global median lag (median lag = 18 days) for full-universe robustness only.

Yahoo chart dividend **event dates are ex-dates**, not payment dates — not used as the payment-yield day key.

## E-006 re-derive (one prior free number)

| Field | Value |
|-------|-------|
| SPY last close (Yahoo chart) | 757.2200 on 2026-09-15 |
| SPY shares outstanding (Yahoo quote, earlier same day before 429) | 917782016 |
| SPY AUM approx | $695.0bn |
| SPY holdings cross-check | SSGA holdings-daily xlsx as of 14-Sep-2026, n=505 lines |

## Results

### A. Calendar-true payment dates only (PRIMARY for kill switch)

n positive-yield days = 1705; top/bot n = 341/341.

| Quintile | n | Mean SPY ret | Mean pay yield | Mean cash $bn | Mean #payers |
|----------|---|--------------|----------------|---------------|--------------|
| 1 | 341 | 0.000975 | 0.000002 | 0.066 | 1.12 |
| 2 | 341 | -0.000007 | 0.000005 | 0.202 | 1.66 |
| 3 | 341 | 0.001163 | 0.000011 | 0.389 | 2.14 |
| 4 | 341 | 0.000781 | 0.000023 | 0.851 | 2.85 |
| 5 | 341 | 0.000362 | 0.000075 | 2.678 | 3.38 |

- Raw top−bottom gap: **-0.000612** (se ≈ 0.000842; t = -0.73, p = 0.468)
- Controlled top dummy (top vs bottom only, HC1): **0.000007** (t = 0.01, p = 0.994, n = 682)
- Continuous payment yield (bps of mcap): coef = 0.000275 (t = 0.24)

**Kill switch:** TRIPS on this sample.

### B. Full universe (calendar + imputed lag) — robustness only

Calendar share of events: 22.4%; imputed: 77.6%.  
n events = 411 tickers with Yahoo dividends; 17,593 regular cash events after filters.

| Quintile | n | Mean SPY ret | Mean pay yield | Mean cash $bn | Mean #payers |
|----------|---|--------------|----------------|---------------|--------------|
| 1 | 473 | 0.000660 | 0.000004 | 0.156 | 1.50 |
| 2 | 472 | 0.001107 | 0.000014 | 0.528 | 2.80 |
| 3 | 472 | 0.000034 | 0.000033 | 1.239 | 4.62 |
| 4 | 472 | -0.000490 | 0.000067 | 2.478 | 6.63 |
| 5 | 473 | 0.001266 | 0.000136 | 4.672 | 10.05 |

- Raw top−bottom gap: **0.000605** (t = 0.81)
- Controlled top dummy (top vs bottom): **0.001141** (t = 1.37, n = 946)
- Continuous py_bps: coef = 0.000397 (t = 0.81)

Weak positive after controls (**t ≈ 1.37**) — **not** promoted to MECHANISM APPEARS given timing imputation and conflict with calendar-true sample.

### C. Falsifications

| Placebo | Controlled top coef | t | Note |
|---------|---------------------|---|------|
| Announcement-date yield | 0.000155 | 0.22 | ≈0 |
| Ex-date yield | 0.000167 | 0.29 | ≈0 |

Placebos are null (consistent with “not news / not ex-drop”), but the **payment-day** object itself fails the kill switch on true payment dates.

## Limitations (honest)

1. **Survivorship:** current S&P500 only (UNCERTAIN).
2. **Payment-date coverage:** free Nasdaq calendar does not deliver NYSE payment dates at scale; ~78% of full-universe events use lag imputation.
3. **Shares/mcap:** current snapshot × SPY path — not CRSP historical shares; attenuates / biases levels; quintile **ranking** of days is the object.
4. **Universe narrow vs HS:** S&P500 payers only, not full CRSP; mean payers/day on top quintile ≈ 3–10, far thinner than marketwide HS samples.
5. **No scalar M:** Phase 1 stops at mechanism presence; applying any M to 2024–26 revaluation would repeat C-077.

## Kill-switch decision

| Question | Answer |
|----------|--------|
| Gap ≈0 or wrong sign after seasonality+VIX on best payment dates? | **Yes → FAIL** |
| Invent M anyway? | **No** |
| Next | **Stop** Phase 1 mechanism claim; do not extend to multiplier / household residual bridge |

## Files

- Findings: `2026-09-15-B6-Phase1-Payment-Day-Mechanism.md` (this file)
- Data: `data/b6_phase1/` — `daily_payment_yield.csv`, `positive_yield_days_quintiles.csv`, `dividend_events_payment.csv`, `quintile_means.csv`, `regression_table.csv`, `summary.json`
- Vintage scalars: `data/vintages/2026-09-15-b6-phase1-scalars.tsv`
- Working copy: `/workspace/b6_phase1/`

## Sources / citations

- Design: `_research/BR2_return_2026-09-15.md`
- Hartzmark–Solomon: NBER w30688; AER Sept 2025 (cite only)
- Yahoo chart / Nasdaq calendar & summary (free); SSGA SPY holdings 14-Sep-2026; Wikipedia S&P500 list
