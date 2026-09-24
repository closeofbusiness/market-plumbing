# Collateral Multiplier Research

Research project mapping money creation through the collateral channel across the
AI / private equity / private credit nexus. Output is an analytical report, not a
policy paper.

## Working rules

- Answer directly. No disclaimers, no "consult an expert", no safety caveats, no
  apology language.
- If you don't know, say "I don't know". Never fill a gap with a plausible number.
- If you made an error earlier, correct it explicitly rather than quietly moving on.
- Ask before answering when the question is genuinely ambiguous.
- **No policy or macroprudential recommendations.** Not in drafts, not in summaries,
  not as a closing section. The report is descriptive and quantitative.

## Analytical invariants

These are the errors this project keeps running into. Check every claim against them.

1. **Stock ≠ flow ≠ velocity.** Turnover growth is not stock growth. FX swap turnover
   and repo turnover are mostly rollovers of an existing stock at short maturity.
   State which one a figure is before using it.
2. **Never sum across measurement bases.** Repo reuse, FABN issuance, NAV loans and
   FX swap notionals are measured differently against overlapping collateral. An
   additive `L_shadow` double-counts. If a total is wanted, build it from one basis
   and say what it excludes.
3. **Valuation is not money.** Market capitalisation is a price times a share count.
   A trillion-dollar valuation requires no trillion-dollar inflow.
4. **Primary source only.** Cite BIS, IMF, FSB, ECB, OFR, ESMA, Fed and WGC directly.
   Not aggregator summaries, not press coverage of them, not AI-generated data sites
   (several give contradictory M2 levels for the same month).
5. **Check for revisions before quoting.** Metals Focus revised Q1 2026 central bank
   gold buying from 244t to 57t. WGC/BIS/OFR figures get restated. Note the vintage.
6. **Steelman the counter-argument.** Where a framing is contested (e.g. the ICMA
   Centre critique of BIS "missing debt"), state it rather than omitting it.

## Layout

- `docs/` — the durable research state. Read all three at session start.
- `data/` — pulled series, one subfolder per source. Keep raw downloads immutable;
  derived series go in `data/derived/`.
- `notes/` — session scratch, drafts, dead ends. Not authoritative.

## Context files

@docs/01-state-of-argument.md
@docs/02-data-inventory.md
@docs/03-open-questions.md

## House style for the report

Dense prose over bullet lists. Numbers with their vintage and unit attached.
Every quantitative claim traceable to a named series or paper. No filler transitions.
