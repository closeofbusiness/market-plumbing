# Commodities — dossier

**Status, 12 Oct 2026:** first measurement map done (E-021), nothing measured into the ANSWER beyond it yet. The programme had no
commodity work before 12 Oct; FX and commodities were parked by E-019 and taken up by E-021.

- **The map:** `2026-10-12-E021-Where-The-Money-Comes-From-Rates-FX-Commodities.md`. It covers gold, crude and copper: who buys,
  who sells, the funding, flow direction on free data, how to measure change, and the literature.
- **Raw agent return (full tables, series codes, latest values):** `_research/2026-10-12-E021-commodities-inhouse-return.md`.
- **COT ledger built 12 Oct:** `bin/pull_cftc_cot.py`, outputs in `data/cftc_cot/` and `data/history/cftc_cot_*` (weekly row in CALENDAR.tsv).
- **Gold tonnes ledger built 12 Oct:** `bin/build_gold_ledger.py`, outputs in `data/gold/`. The IMF-reported official buying
  against the WGC estimate is a volatile gap, not a stable unreported-buying signal.
- **Next build:** a crude physical ledger.
- **Free-data gaps:** commodity index investment (CFTC discontinued it in 2015), the WTI futures curve (EIA series ends Apr 2024),
  unreported central-bank gold buying.
