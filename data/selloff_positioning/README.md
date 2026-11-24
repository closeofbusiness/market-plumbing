# Selloff Positioning Pre-Registration Runner

Implements the Version 2 pre-registered test in
`_research/2026-11-24-Selloff-Positioning-Preregistration.md`, which is the sole
authority for all windows, contracts, yardsticks, and scoring rules.

## Modes

- `python3 bin/selloff_positioning.py selftest` — runs offline synthetic-fixture
  guards and mutant checks (no network).
- `python3 bin/selloff_positioning.py fetch` — downloads raw CFTC TFF, Fed H.10
  yen/USD, and MoF weekly securities-flow files into `data/selloff_positioning/`.
- `python3 bin/selloff_positioning.py build` — offline build reading the raw
  files and writing deterministic `results.csv`, `registration_score.csv`, and
  `checks.csv` into `data/selloff_positioning/`.

## Sources

- CFTC Traders in Financial Futures (Futures Only, dataset `gpe5-46if`) for 11
  contracts (S&P 500, Nasdaq-100, Russell 2000, VIX, JPY, and 6 US Treasuries).
- Federal Reserve H.10 daily noon buying rate, yen per dollar (`H10/H10/RXI_N.B.JA`).
- Japan Ministry of Finance weekly securities transactions (`week.csv`, descriptive).
