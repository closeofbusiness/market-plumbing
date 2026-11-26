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

- CFTC Traders in Financial Futures (futures only, dataset `gpe5-46if`) for 11 contracts: E-mini S&P 500 (`13874A`),
  E-mini Nasdaq-100 (`209742`), E-mini Russell 2000 (`239742`), VIX (`1170E1`), Japanese yen (`097741`) and six
  US Treasury contracts. The consolidated codes `13874+` and `20974+` are not used (their unit changed in May 2023).
- Federal Reserve H.10 daily noon buying rate, yen per dollar, read from the H.10 historical table for Japan
  (`releases/h10/hist/dat00_ja.htm`). It is the same series as DDP `H10/H10/RXI_N.B.JA`.
- Japan Ministry of Finance weekly securities transactions (`week.csv`, descriptive).

## Reading the outputs

- `registration_score.csv`: one row per registered line. `status` is PENDING until the end-date rows are in the file.
  A primary-window miss on a position line (P1, P3, P5b, P6) has status INCONCLUSIVE and outcome `n/a`; the prediction
  stays in `detail`. P5a (the yen rate) is scored FIRED or NOT_FIRED.
- `results.csv`: every contract, class and field, with its change, percentile, sample size and Low/High flag. The window
  `secondary_no_vx` is the registered P4 line. `secondary_no_vx_actual` is the same line against actual VIX settlement
  dates (four were moved to a Tuesday by a holiday); it carries no verdict.
- `checks.csv`: input checks. The build stops before writing anything if `raw_tff.csv` holds a duplicate row or a
  negative position.
