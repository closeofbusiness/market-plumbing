# W3 tax panel location

Full firm-level panel (343 KB CSV, 412 ok firms) is on the executor box at:

`/workspace/tdr/data/w3_tax/firm_tax_panel.csv`

**NOT mirrored here (C-097, 21 Sep).** This folder holds only `README.md`, `results.json` and `w1_rebalance_attack.json`. `data/z1_debt/` does not exist either, so the five raw FRED pulls named in the `series_file` fields of `w1_rebalance_attack.json` are also absent. Every headline scalar was re-derived from `results.json` and matches; the step from SEC companyfacts to Σtax/Σpretax over 412 firms cannot be checked here until the panel lands.

Headline scalars: `results.json` (this folder).
W1 rebalance pair: `w1_rebalance_attack.json` (this folder).
Deliverable note: project root `2026-09-21-W3-Tax-Decomposition.md`.

Panel columns include: ticker, cik10, pretax_2015/2025, tax_2015/2025, pretax_tag_2015/2025, tax_tag, dom_for match flags, status.
