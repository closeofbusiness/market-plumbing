# Commodities — dossier

**Status, 12 Oct 2026:** first measurement map done (E-021), nothing measured into the ANSWER beyond it yet. The programme had no
commodity work before 12 Oct; FX and commodities were parked by E-019 and taken up by E-021.

- **The map:** `2026-10-12-E021-Where-The-Money-Comes-From-Rates-FX-Commodities.md`. It covers gold, crude and copper: who buys,
  who sells, the funding, flow direction on free data, how to measure change, and the literature.
- **Raw agent return (full tables, series codes, latest values):** `_research/2026-10-12-E021-commodities-inhouse-return.md`.
- **Next builds:** a weekly COT ledger (gold, WTI, copper) on the CFTC disaggregated report, adapting `bin/pull_cftc_tff.py`; a
  gold tonnes ledger (IMF official, SAFE, GLD/IAU, LBMA) against the WGC aggregates; a crude physical ledger.
- **Free-data gaps:** commodity index investment (CFTC discontinued it in 2015), the WTI futures curve (EIA series ends Apr 2024),
  unreported central-bank gold buying.
