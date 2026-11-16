# AV1: are share prices ahead of AI earnings? Registered blind, 16 November 2026 (version 1)

**Status: registered before any multiple, market value or earnings figure by industry was read by the supervisor or any agent for
this test.** The supervisor has opened the Damodaran files only to list sheet names, column headers, industry names and each file's
"Date updated" cell. The hash of this file is pinned at landing; a builder must refuse to score if it changes. Amendments after an
attack are allowed while still blind and are recorded as a new version.

**What the supervisor already knows, declared.** From this project's own work: the S&P 500's price-to-earnings multiple rose in 2024
and fell in 2025 and the first half of 2026, and since 2015 most of the index's gain has been earnings growth
([`fundamentals-benchmark.md`](../dossiers/fundamentals-benchmark.md)). From general reporting: chip makers' and the largest software
firms' share prices and earnings both rose steeply after 2022. No industry figure in these files has been opened. This prior knowledge
is why the labels are mechanical and fixed here.

## Why this exists

Thesis T6 in [`dossiers/ai-theses.md`](../dossiers/ai-theses.md): "Equity prices already capitalise AI gains that earnings have not yet
delivered" (proposed E-029, confirmed E-030; the principal chose it on 16 Nov 2026). If prices are ahead of earnings in the AI
industries, the price-to-earnings multiple of those industries should have risen since the start of 2023 by more than the multiple
of other industries, and by more than those same industries' multiples changed before AI. If earnings kept pace with prices, the
multiples did not diverge.

## Data (free, no key, no registration, no contact details)

Aswath Damodaran's US industry datasets (NYU Stern), January of each year, US-listed firms grouped into 94 industries plus two
totals. Price-to-earnings: `pedata.xls` (current) and `pc/archives/pedataYY.xls`. **File years lag the data by one: `pedata22.xls` is
dated 5 January 2023 and the current `pedata.xls` 5 January 2026** (read from each file's "Date updated" cell on 16 Nov 2026).
Dollar values (market capitalisation, net income): `DollarUS.xls` (current) and `pc/archives/DollarUSYY.xls`, archived from
`DollarUS19.xls` only. Files are cached, hashed and gitignored (`data/vintages/av1/raw/`).

| point | PE file | dollar file |
|---|---|---|
| January 2017 | `pedata16.xls` | none |
| January 2020 | `pedata19.xls` | `DollarUS19.xls` |
| January 2023 | `pedata22.xls` | `DollarUS22.xls` |
| January 2024 | `pedata23.xls` | `DollarUS23.xls` |
| January 2026 | `pedata.xls` (current) | `DollarUS.xls` (current) |

The build checks each file's "Date updated" cell against this table and stops on a mismatch. On HTTP 403 or 429, or a body that is
not the expected file, it stops; the decision goes to the principal.

## Measure

For industry i at date t, `m(i,t) = ln(Aggregate Mkt Cap / Net Income (all firms))`, Damodaran's column of that name: the industry's
total market value over its total net income, so money-losing firms count. **Δm_post = m(Jan 2026) - m(Jan 2023)**, three years
from just after ChatGPT's release; **Δm_pre = m(Jan 2020) - m(Jan 2017)**, the three years before the pandemic. An industry is dropped
if the column is missing, non-numeric or non-positive (aggregate losses) at any of the four dates, and listed. Damodaran re-sorts firms
between industries from year to year; industry names present at all four dates are used, and a name missing at any date is dropped
and listed ("Retail (Online)" is absent from the current file; "Retail (REITs)" is absent from the earlier ones).

## The AI group, fixed before any figure is read

**AI complex (7 industries):** Semiconductor; Semiconductor Equip; Software (System & Application); Software (Internet); Computer
Services; Computers/Peripherals; Telecom. Equipment. These make, design or run the chips, networks, software and services AI is
built from. Every other industry, except the two total rows and "Diversified", is the comparison group.

**AI build-out (reported, not labelled):** Power; Utility (General); Electrical Equipment; Engineering/Construction (the power and
construction suppliers of data centres).

## Statements

| id | statement | statistic | SUPPORT | AGAINST |
|---|---|---|---|---|
| AV1-P1 | The multiple rose more after January 2023 in the AI complex than in other industries | mean Δm_post of the AI complex minus mean Δm_post of the comparison group (equal weight per industry) | one-sided permutation p ≤ 0.05 (AI complex higher) and the difference stays positive when any one AI-complex industry is left out | one-sided permutation p ≤ 0.05 (AI complex lower) and the difference stays negative when any one AI-complex industry is left out |
| AV1-P2 | ...relative to how the same industries' multiples moved in 2017-20 | the same on Δm_post - Δm_pre | same rule | same rule |

Otherwise INCONCLUSIVE. Permutation: the AI-complex label is reassigned at random to 7 of the kept industries, 100,000 times, seed
20261116, p = (1 + k) / 100,001; a p within two Monte Carlo standard errors of 0.05 is INCONCLUSIVE.

**Asymmetry, stated with every result.** SUPPORT says prices of the AI complex rose faster than its earnings, relative to other
industries: the pattern T6 predicts. It does not show the market is wrong; a higher multiple can be a correct forecast of earnings
still to come, or a lower discount rate for those firms. AGAINST says the AI complex's earnings kept pace with or outran its prices
over the window: the gains were being delivered, not only priced. Neither speaks to the level of the multiple, only to its change.
Aggregate net income is GAAP and includes one-off items; an industry whose earnings fell to near zero at one date has an extreme
multiple at that date.

**Reported, not labelled:**
- The AI complex pooled into one aggregate from the dollar files: Δln(total market capitalisation) and Δln(total net income),
  January 2023 to January 2026, and the same for all other industries pooled, so the price and earnings legs are shown separately.
- Δm on January 2024 to January 2026 (the window starting a year after ChatGPT).
- The money-making-firms multiple ("Aggregate Mkt Cap/ Trailing Net Income (only money making firms)") in place of the all-firms one.
- Leave-one-out range of the difference; the AI build-out group against the comparison group.
- The number of firms in each AI-complex industry at each date (re-sorting check).
- A Spearman correlation of each industry's BTOS sector AI use (CV1-P6 sector means; the mapping is in `detail.csv`) with Δm_post,
  for comparison with AF1, AJ1 and AP1.

**Not tested here, and why.** Forward earnings: Damodaran's forward PE is a simple average of money-making firms, not an aggregate,
and is reported only. Prices after January 2026: the free industry files are annual. Firm-level tests (a fixed list of AI firms with
SEC earnings and market values) need a price source and the SEC route, and are a candidate AV2.

## Build

`bin/av1_ai_valuation.py` with `selftest`, `fetch` and `build`; outputs in `data/av1_ai_valuation/` (`registered.csv` written before any
statistic, `scores.csv`, `detail.csv`, README). Industries are matched by exact name (whitespace normalised); the header row is found
by the "Industry" cell and columns by exact header text. A gate is registered in `bin/check.sh` at landing. Every statistic carries
its denominator (industries kept and dropped, dates used).
