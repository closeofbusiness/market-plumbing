# W3 tax panel

Firm-level SEC companyfacts tax panel backing `2026-09-21-W3-Tax-Decomposition.md`.

## Files

- `firm_tax_panel.csv` — 503 rows (412 `status=ok`); landed 24 Sep 2026 from executor `/workspace/tdr` (C-097).
- `results.json` — headline scalars. Re-derived from the ok rows: ETR 2015 27.351%, ETR 2025 19.615%, Δlog(1−ETR) 0.10119, after-tax multiplier 1.10649. Matches this file.
- `w1_rebalance_attack.json` — W1 rebalance pair.

## Schema (`firm_tax_panel.csv`)

| column | meaning |
|---|---|
| ticker | equity ticker |
| cik10 | zero-padded CIK |
| status | `ok` if both-year pretax+tax usable; else reason |
| missing_fields | fields absent when not ok |
| pretax_tag / tax_tag | XBRL tags used |
| pretax_tag_2015 / pretax_tag_2025 / tax_tag_2015 / tax_tag_2025 | year-specific tags |
| pretax_2015 / tax_2015 / pretax_2025 / tax_2025 | USD as reported |
| pretax_end_2015 / pretax_end_2025 / tax_end_2015 / tax_end_2025 | period end dates |
| has_domestic / has_foreign | tag presence flags |
| dom_for_match_2015 / dom_for_match_2025 | domestic+foreign equals consolidated |
| dom_plus_for_2015 / dom_plus_for_2025 | domestic+foreign sums |
| dom_for_vs_consol_2015 / dom_for_vs_consol_2025 | difference vs consolidated |
| n_pretax_tags / consol_candidates | tag inventory |
| pretax_frame_2015 / pretax_frame_2025 | frame / calendar-year fallback marker |

Do not re-fetch without `SEC_UA` already set in the environment. Never invent a User-Agent containing a personal email.
