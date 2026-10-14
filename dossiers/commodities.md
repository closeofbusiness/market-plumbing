# Commodities — dossier

**Status, 13 Oct 2026:** first measurement map done (E-021) and reviewed from outside (Grok K1): gold's attribution away from futures
fell outright (C-141), and crude's fund-length comparison and its physical-only reading were withdrawn after being weakened (C-142). Nothing measured onto the page beyond it yet. The programme had no
commodity work before 12 Oct; FX and commodities were parked by E-019 and taken up by E-021.

- **The map:** `2026-10-12-E021-Where-The-Money-Comes-From-Rates-FX-Commodities.md`. It covers gold, crude and copper: who buys,
  who sells, the funding, flow direction on free data, how to measure change, and the literature.
- **Raw agent return (full tables, series codes, latest values):** `_research/2026-10-12-E021-commodities-inhouse-return.md`.
- **COT ledger built 12 Oct:** `bin/pull_cftc_cot.py`, outputs in `data/cftc_cot/` and `data/history/cftc_cot_*` (weekly row in CALENDAR.tsv).
- **Gold tonnes ledger built 12 Oct:** `bin/build_gold_ledger.py`, outputs in `data/gold/`. The IMF-reported official buying
  against the WGC estimate is a volatile gap, not a stable unreported-buying signal.
- **Crude physical ledger built 13 Oct:** `bin/build_crude_ledger.py`, outputs in `data/crude/`. US weekly balance asserted;
  SPR −130 mb in 2026; world draw 424 mb Jan–Sep (STEO). EIA's Brent print of 2 Oct ($135.5) is a data error: ICE Brent settled about $102 (Grok check, 13 Oct).
- **Free-data gaps:** commodity index investment (CFTC discontinued it in 2015), the WTI futures curve (EIA series ends Apr 2024),
  unreported central-bank gold buying.
- **Other free oil sources (Grok search, 13 Oct, `_research/2026-10-13-Grok-Oct-Checks-and-Oil-Sources-Return.md`):**
  - **JODI Oil World Database:** country stocks and trade, free CSV, verified. This is the next build.
  - **OPEC MOMR appendix tables.**
  - **Census and China Customs crude imports.**
  - **World Bank monthly Brent.**
  - **No free daily futures curve:** ICE end-of-day data is paid; CME's page errors.
