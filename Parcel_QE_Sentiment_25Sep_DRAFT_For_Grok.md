# Quarter-end funding sentiment — public web sources, two runs (Grok in Cursor)

**Status: FINAL.** The principal routed this to Grok in Cursor on 19 Sep 2026. It was switched from X to public web sources
by the principal on 25 Sep (THE_ASK E-015), because no lane we have reads X (C-121: the first RUN 1 attempt, 24 Sep, stopped at
X's sign-in wall). The filename still says DRAFT only because renaming it would break the references to it.
**Runs:** **RUN 1 as soon as possible, and before the 30 Sep turn** (expectations), and **RUN 2 on 1 Oct** (what happened at
the turn). Both runs use the same searches, the same tool and the same rules. The comparison between them is the finding.

## Why this exists

The FT/D8 work flagged a risk that funds borrowing against equities through conduits (ABCP funding equity total-return swaps
or sponsored repo) would have to deleverage at a quarter-end. **June 2026's quarter-end did not show that stress, so the base
rate is "quiet".** September is the next test. Commentary is the lead indicator and the 30 Sep prints are the test. This is
sentiment: it never substitutes for a print, and it measures nothing on its own.

## Read the numbers from the repository, do not paste them

Take the latest vintage of each key from `data/series.tsv` on the day you run: `finra_margin_debit_balances_bn`,
`ficc_sponsored_total_bn`, `actrix_sponsored_share_of_cleared_pct`, `abcp_outstanding_bn`, `hf_repo_borrowing_bn`.
OFR's Q2 hedge-fund data is still unpublished. **Do not read its absence as a finding.**

## Four questions, each pre-registered against the print that tests it

| # | question | the print that scores it (30 Sep / 1 Oct) |
|---|---|---|
| 1 | Quarter-end repo: squeeze, specials, or a shift between sponsored and bilateral repo? | SOFR and GC at the turn; `ficc_sponsored_total_bn`; `actrix_sponsored_share_of_cleared_pct` |
| 2 | Equity financing (stock loan, total-return swaps, margin): stress, step-ups, or quiet? | CME AXW total-return futures basis (30 Sep calendar row); `finra_margin_debit_balances_bn` |
| 3 | ABCP and conduits: pulling back from equity-swap or HQLA-repo funding? | `abcp_outstanding_bn` |
| 4 | Versus June 2026: tighter, similar or easier? | all of the above against their 30 Jun values |

**Each run ends with a one-word call per question: TIGHTER, SIMILAR or EASIER than June.** That is what RUN 2 and the
prints score. A run that ends without calls cannot be tested.

## Method — this decides whether the return is usable

- **Search with Cursor's web search, using exactly these seven strings, and nothing else.** Search neutral terms, not
  outcome terms: a search for "repo squeeze" finds squeeze claims by construction. Record the tool and any date or recency
  setting you used, so RUN 2 can repeat it.
  1. `quarter-end repo`
  2. `quarter end funding`
  3. `SOFR quarter-end`
  4. `month-end repo`
  5. `TRS funding`
  6. `stock loan quarter end`
  7. `ABCP`
- **Date windows.** RUN 1 keeps items published from 10 Sep 2026 to the day it runs. RUN 2 keeps items published from the
  day after RUN 1 to 1 Oct. Drop undated items. For each query, read down the results until you have read 30 items or reach
  items older than the window, whichever comes first, and count every item you read.
- **What counts.** Public web pages: news articles, public research notes, newsletters, blogs, forums, and X posts **only**
  when a search result shows a direct `x.com/.../status/...` link with readable text. Never log in to anything, and never use
  a tool or mirror to get past a sign-in wall or paywall. For a paywalled article, use only the headline and the visible
  opening. Official releases and data (the Fed, the New York Fed, OFR, Treasury) are prints, not sentiment: list them
  separately and keep them out of the counts.
- **Report the balance, not the highlights.** For each question, give the items read and how many say stress, quiet or
  mixed, and how many are off-topic.
- **State the denominator.** Give the number of distinct sources (outlets or authors), and each one's role: desk
  practitioner, strategist, journalist, commentator or unknown. Three loud sources are not "the market says".
- **Every item carries a direct URL and its date. An item without a URL is dropped**, not kept "where possible". This project
  has twice had perfectly formatted sources that did not exist (C-048, C-079); the URL is what lets a claim be checked. The
  supervisor will open a sample.
- **Paraphrase.** Quotes of 15 words or fewer, attributed.
- **Keep what you observed and what you infer in separate sections.**

## Return — to a file, not to chat

- RUN 1: add a section headed **"RUN 1 — public web sources (E-015)"** to `_research/2026-09-25-QE-Sentiment-Run1.md`.
  Keep the blocked X attempt above it: it is part of the record.
- RUN 2: `_research/2026-10-01-QE-Sentiment-Run2.md`, with a table that sets each RUN 1 call against what RUN 2 and the
  prints show: **right / wrong / unscoreable**.

## Do not

- Present commentary as a print, or as a measure of stress.
- Treat the missing OFR Q2 data as a finding.
- State any scalar multiplier, or any claim about what drove prices (C-077).
- Change the queries, the tool or the rules between runs.

## Rules

- If what you find contradicts this parcel, say so explicitly: the base rate here is itself an assumption.
- Never route around a refusal, a block, a sign-in wall or a paywall. Say which part and why, and do the rest.
- Everything you commit is public: no personal data, and no copied paywalled text.
- **Hand over with the note in SINGLE quotes** (a `$` figure in double quotes expands):
  `bin/check.sh --handover write grok qe-sentiment-run1 done 'Q1 SIMILAR, Q2 ..., n sources ...'`
