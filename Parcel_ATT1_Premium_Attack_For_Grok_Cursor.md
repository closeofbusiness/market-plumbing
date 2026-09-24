# Parcel ATT1 — attack the premium-compression finding (Grok in CURSOR, read-only; web allowed for free sources)

ROUTING: Grok in Cursor. This is the project's current central claim, and it was reached by our own arithmetic on
two datasets — exactly the case where an outside opinion is worth a message. Grok's sanctioned lane here is
judging, not building. READ-ONLY in the folder; web search allowed to open free sources (FRED, Shiller, Damodaran,
NBER).

HANDOFF (before pasting):
1. Open Cursor on the FOLDER `~/Dropbox/31 - Claude Cowork/Work/2026.08 - Third Derivative Research`
   — NOT on hermes-core or any git repo.
2. Select the Grok model. Paste everything below the line. Decline any offer to apply edits.
3. Copy the returned table and the four closing lines back to Claude verbatim.

---

You are a hostile referee. Make the strongest possible case that the claim below is wrong, then say honestly
whether it survives.

THE CLAIM UNDER ATTACK (read these two first):
  2026-09-12-P2c-Rates-vs-Risk-Premium.md — between end-2023 and mid-2026 the S&P 500's multiple rose only 3.6%,
  but that nets a real-rate effect of -2.14 P/E points against a risk-premium effect of +3.01 points; holding the
  premium at its 2015-19 average and applying today's real yield implies a multiple of 16.3 against an actual
  25.2, so the market is 54.7% above that counterfactual and the excess is 35.4% of today's valuation (52.2% on
  cyclically-adjusted earnings).
  2026-09-12-ATT0-First-Attribution.md — the attribution that preceded it, and what it refuted.
SUPPORTING DATA (all on disk): data/p2a_decomposition/, _research/2026-09-12-P2c-*.csv,
data/vintages/shiller_2026-09-02/ (Shiller's file and the two FRED yield series), bin/rates_vs_premium.py.

TASK
1. Recompute the headline numbers from the CSVs — the -2.14/+3.01 split, the 16.3 counterfactual multiple, the
   35.4% share. Say whether each reproduces, and to what precision.
2. Attack the construction. The candidates we already know of, which you should press hardest on: the premium is a
   TRAILING residual with no growth term, so "compression" may be growth expectations rather than risk pricing;
   the 2015-19 baseline is a choice, and a different baseline moves the answer; trailing earnings jumped 22.75% in
   H1 2026, which mechanically moves the earnings yield; the identity earnings yield = real yield + residual
   guarantees the split sums, so agreement is not evidence. Add any failure we have not named.
3. Say what the finding would look like if it were an artefact rather than a fact, and which observable
   distinguishes the two.
4. Judge the use we intend: that this residual is the part "where the money comes from" must explain. Is that a
   legitimate bridge from money and flows to prices, or a category error?

RETURN EXACTLY THIS
| # | number recomputed | reproduces? | your value | note |
ATTACK: <the strongest case against, 200 words or fewer>
SURVIVES?: <yes / partly / no — one line>
LOAD-BEARING ASSUMPTION: <one line>
WHAT WOULD SETTLE IT: <one line, an observable>

RULES
- Do not ask clarifying questions. If something is ambiguous, state the assumption you made and answer anyway.
- Mark anything you inferred rather than read as UNCERTAIN, and say what would settle it.
- If you cannot do part of this, say which part and why, and do the rest.
- Cite a link and date for every external factual claim. Free sources only.
- Read-only: create, edit, move or delete nothing in the folder.
