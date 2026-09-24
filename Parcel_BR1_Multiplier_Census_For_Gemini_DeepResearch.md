# Parcel BR1 — census of published price-multiplier estimates (Gemini DEEP RESEARCH)

ROUTING: Gemini Deep Research. This is the one task the mode is genuinely best at — mapping a literature we
do not know the shape of. It is ALSO the mode with the worst measured citation validity (13.3% hallucinated
URLs), so the return is treated as a map, never as a source: every URL gets resolved by me before any row is
used. Tier B item B1.

HANDOFF:
1. gemini.google.com, select Deep Research. Search is inherent to the mode — no toggle needed.
2. Paste everything below the line. Expect a long return; use "continue" if it truncates.
3. Copy the table back verbatim. I will resolve every URL before a single row is believed.

---

You are a research librarian building a census. Map every published estimate of how much aggregate asset
prices move when money flows into the market — the "price multiplier" or "aggregate demand elasticity" of
equities.

BACKGROUND YOU NEED
The inelastic markets hypothesis (Gabaix and Koijen) claims $1 of net flow into equities raises aggregate
market value by $M, with M far above 1. Published estimates disagree by roughly six-fold. I want to know
WHY they disagree, which means I need what each estimate is an estimate OF — not just the number.

TASK
Find every published estimate you can, 2018 to today, in economics and finance. For each, record:
- the number (point estimate, and range if given)
- the identification strategy (granular instrumental variables, index reconstitution, fund-flow induced
  trading, fire sales, demand system estimation, natural experiment, other)
- the flow variable actually used (retail fund flows, institutional purchases, index demand, issuance,
  sector-level flows from national accounts, something else)
- the horizon the estimate applies to (days, quarters, years, permanent)
- the market segment (individual stocks, the aggregate market, a country, a sector)
- the sample period
- any stated caveat by the authors themselves about what the estimate does NOT apply to
- whether it has been challenged in print, and by whom

Include the critical literature explicitly — papers arguing the multiplier is small, mismeasured, or that
the identification fails. A census with only supportive papers is a failed census.

METHOD NOTE
Search terms worth trying: "inelastic markets hypothesis", "price multiplier", "aggregate demand
elasticity of the stock market", "micro elasticity macro elasticity", "flow-driven asset prices",
"demand system asset pricing".

OUT OF SCOPE
Do not evaluate which estimate is right. Do not summarise the theory. Do not produce narrative — the table
is the deliverable. Do not cover bond or FX markets.

RETURN EXACTLY THIS — one flat table, one row per estimate:
| # | authors | year | title | M or elasticity | identification | flow variable | horizon | segment | sample | authors' own caveat | challenged by | URL |

Then three lines:
SMALLEST AND LARGEST: the two extreme estimates and, in one sentence each, what differs between them.
CRITICAL PAPERS: list any paper arguing the multiplier is small or mismeasured.
WHAT I COULD NOT FIND: state plainly.

RULES
- Do not ask clarifying questions. If something is ambiguous, state the assumption you made and answer anyway.
- **Give ONLY: authors, year, title, and a URL that opens. Do NOT supply DOIs, working-paper numbers,
  volume or page numbers, or any other identifier.** I did not ask for them, and unasked identifiers are the
  field most often constructed. An identifier I did not request will cause me to discard the whole row.
- Every URL must be one you actually retrieved, not one you reconstructed from a pattern. If you have the
  paper but not a URL you retrieved, write NO URL RETRIEVED — that is a useful and acceptable answer.
- Mark anything you inferred rather than read as UNCERTAIN, and say what would settle it.
- If you cannot answer part of this, say which part and why, and answer the rest.
- Do not assert that you have verified your references. I will verify them; a self-audit is not evidence.
