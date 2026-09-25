# Quarter-end funding sentiment — X search, two runs (Grok in Cursor)

**Status: FINAL — routed to Grok in Cursor by the principal, 19 Sep 2026.** **[C-121] Grok in Cursor cannot read X:** its
browser stops at X's sign-in wall, and the first RUN 1 attempt (24 Sep) read zero posts. RUN 1 needs a lane that reads X,
or the principal's OK to switch both runs to public web sources. Rewritten by
Claude from Grok's own 19 Sep draft; the filename still says DRAFT only to avoid a rename on the SMB mount.
**Runs:** **RUN 1 on 25 Sep** (expectations, before the turn) and **RUN 2 on 1 Oct** (what happened at the turn).
Same searches both times — the comparison is the finding.

## Why this exists

The FT/D8 work flagged deleveraging risk at quarter-ends for conduit-funded equity leverage (ABCP → equity
total-return swaps / sponsored repo). **June 2026's quarter-end did not show that stress, so the base rate is
"quiet".** September is the next test. Chatter is the lead indicator; the 30 Sep prints are the test. This is
practitioner sentiment — it never substitutes for a print and it measures nothing on its own.

## Read the numbers from the vault, do not paste them

Take the latest vintage of each key from `data/series.tsv` on the day you run: `finra_margin_debit_balances_bn`,
`ficc_sponsored_total_bn`, `actrix_sponsored_share_of_cleared_pct`, `abcp_outstanding_bn`, `hf_repo_borrowing_bn`.
OFR's Q2 hedge-fund data is still unpublished — **do not read its absence as a finding.**

## Four questions, each pre-registered against the print that tests it

| # | question | the print that scores it (30 Sep / 1 Oct) |
|---|---|---|
| 1 | Quarter-end repo: squeeze, specials, or sponsored-versus-bilateral migration? | SOFR and GC at the turn; `ficc_sponsored_total_bn`; `actrix_sponsored_share_of_cleared_pct` |
| 2 | Equity financing — stock loan, total-return, margin: stress, step-ups, or quiet? | CME AXW total-return futures basis (30 Sep calendar row); `finra_margin_debit_balances_bn` |
| 3 | ABCP / conduits pulling back from equity-TRS or HQLA-repo legs? | `abcp_outstanding_bn` |
| 4 | Versus June 2026: tighter, similar or easier? | all of the above against their 30 Jun values |

**RUN 1 ends with a one-word call per question — TIGHTER, SIMILAR or EASIER than June.** That is what RUN 2 and
the prints score. A run that ends without calls cannot be tested.

## Method — this is what decides whether the return is usable

- **Search neutral terms, not outcome terms.** A search for "repo squeeze" returns squeeze claims by construction,
  and someone on X is always saying funding is tight. Use neutral queries — e.g. `quarter-end repo`, `quarter end
  funding`, `SOFR quarter-end`, `month-end repo`, `TRS funding`, `stock loan quarter end`, `ABCP`. **Record the
  exact query strings and reuse them unchanged in RUN 2.** Do not widen the search mid-run to find more stress.
- **Report the balance, not the highlights.** For each question: posts read, and how many say stress / quiet /
  mixed / off-topic.
- **State the denominator.** Distinct accounts, and each item's apparent role: desk practitioner, strategist,
  commentator, or unknown. Three loud accounts are not "the market says".
- **Every item carries a direct post URL and its date. An item without a URL is dropped** — not kept "where
  possible". This project has twice had perfectly formatted sources that did not exist (C-048, C-079); the URL is
  what lets a claim be checked. The supervisor will open a sample.
- **Paraphrase.** Quotes of 15 words or fewer, attributed.
- **Keep what you observed and what you infer in separate sections.**

## Return — to a file, not to chat

- RUN 1 → `_research/2026-09-25-QE-Sentiment-Run1.md`
- RUN 2 → `_research/2026-10-01-QE-Sentiment-Run2.md`, with a table setting each RUN 1 call against what RUN 2 and
  the prints show: **right / wrong / unscoreable**.

## Do not

- Present chatter as a print, or as a measure of stress.
- Treat the missing OFR Q2 data as a finding.
- State any scalar multiplier, or any claim about what drove prices (C-077).
- Change the queries between runs.

## Rules

- If what you find contradicts this parcel, say so explicitly — the base rate here is itself an assumption.
- Never route around a refusal or a block; say which part and why, and do the rest.
- **Hand over with the note in SINGLE quotes** (a `$` figure in double quotes expands):
  `bin/check.sh --handover write grok qe-sentiment-run1 done 'Q1 SIMILAR, Q2 ..., n accounts ...'`
