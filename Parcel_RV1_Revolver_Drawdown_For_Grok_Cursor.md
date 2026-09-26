# RV1 — What draws committed credit lines all at once? (Grok in Cursor)

**Status: READY, 26 Sep 2026.** The principal approved it on 25 Sep (THE_ASK E-015) and said to go ahead on 26 Sep (E-016).
It is routed to Grok in Cursor, with web search, to find sources whose citations must hold, and was written by the supervisor.
It does not decay; send it by 1 Oct.

## Why this exists

Undrawn committed bank lines are one of the few places where money can be created fast: a draw turns a commitment into a loan,
and a deposit, the same day. Two undrawn stocks are the programme's live fragility candidates:

- **Bank lines to nonbank financial institutions (NDFIs).** FDIC data put 42.9% of NDFI commitments, $987bn, undrawn, and 24%
  of NDFI lending is capital-call lines secured on private-fund investors' commitments (`2026-08-29-N2c-The-Funding-Closure.md`
  §7). Bank lending to NDFIs is a stock of about $2.0trn on a different series. Do not combine the two.
- **Large-bank C&I lines to AI-adjacent industries.** About $450bn committed and $150bn outstanding, so about $300bn undrawn
  (Chicago Fed, February 2026). This is an industry classification, **not lending to the build-out itself**, and about $250bn of
  those commitments already existed in 2015 (C-115; `2026-09-22-W2-AI-Paper-Composition.md`).

The question the programme cannot yet answer: **what draws such lines all at once, how fast, and how much of the undrawn stock
went in the one modern precedent?** Your job is to find that evidence, with citations that hold. Setting today's exposures against
it is the supervisor's job, not yours.

## Material

Read-only:
- `2026-08-29-N2c-The-Funding-Closure.md` §7 (the NDFI stock and its composition)
- `2026-09-22-W2-AI-Paper-Composition.md` (bank credit and the fragility paragraph)
- `CORRECTIONS.md` C-115 (search for `## C-115`), on how the AI-adjacent figure may and may not be described
- `data/vintages/chicagofed_ai_tail_risk_2026-02/` (the archived Chicago Fed article)

You may write only the return file named below, and your handover row.

## Questions

1. **The March 2020 precedent.** How much did US firms draw on committed credit lines in March and April 2020, in dollars and as
   a share of undrawn commitments? Who drew (by rating, size and industry), how fast, and when did it stop or reverse? What did
   bank C&I loans do in the Fed's weekly H.8 release over those weeks?
2. **How NDFI lines behave.** What is known about draws on bank lines to nonbanks in March 2020 or any other stress episode? That
   covers credit intermediaries, private funds' capital-call lines, REITs, BDCs, nonbank mortgage lenders and broker-dealers.
   Include Fed, FDIC, OCC, BIS or academic work on drawdown rates by facility type.
3. **Triggers.** Under what conditions do many borrowers draw at once? These are candidates to test, not to assume:
   - a market-wide dash for cash;
   - a commercial-paper freeze that forces draws on backup lines;
   - downgrades toward "fallen angel";
   - fear that the bank will cut the line;
   - covenant or borrowing-base triggers;
   - for capital-call lines, investors failing to fund capital calls.
   For each, is there evidence that it operated, and where?
4. **What stops it.** What limits a mass drawdown? Candidates are covenants and MAC clauses, banks cutting or repricing lines,
   central-bank facilities (the 2020 CPFF, PMCCF and others), and bank capital. Give evidence, not theory.
5. **What free data would show a drawdown starting.** Public series that would reveal draws in near real time or with a lag.
   Examples to check:
   - H.8 lines for C&I loans and for loans to nondepository financial institutions;
   - Call Report schedule RC-L, unused commitments (FFIEC);
   - Shared National Credit reviews;
   - the Fed's Financial Stability Reports and senior loan officer survey (SLOOS);
   - the FDIC Quarterly Banking Profile.

   For each, give the issuer, URL, frequency, lag, and what a drawdown would look like in it.

**Starting points. These are candidates to verify, not facts.** Confirm each exists and says what you cite before using it.
- Li, Strahan and Zhang (2020), "Banks as Lenders of First Resort: Evidence from the COVID-19 Crisis", *Review of Corporate
  Finance Studies*.
- Acharya and Steffen (2020), on the corporate "dash for cash" and fallen-angel risk, *Review of Corporate Finance Studies*.
- Chodorow-Reich, Darmouni, Luck and Plosser (2022), "Bank Liquidity Provision across the Firm Size Distribution", *Journal of
  Financial Economics*.
- Greenwald, Krainer and Paul, "The Credit Line Channel", Federal Reserve Bank of San Francisco working paper.
- Kashyap, Rajan and Stein (2002), "Banks as Liquidity Providers", *Journal of Finance*: the theory linking lines and deposits.

## Method

- **Primary sources and papers first.** Every number needs a URL and a location (page, table or figure). Use abstracts and
  freely available versions such as working-paper PDFs and Fed notes. Never get past a paywall or sign-in wall.
- **Verify that every citation exists and says what you attribute to it.** This programme has twice had well-formatted sources
  that did not exist (C-048, C-079). The supervisor will open a sample.
- **State the denominator for every rate.** Say what the draw is a share of (undrawn commitments, total commitments or loans
  outstanding), for which population and over which window.
- **Grade each number** MEASURED, BOUNDED or HYPOTHESIS, as defined in `CHARTER.md` under "Grades".
- **Keep what you read and what you infer in separate sections.**

## Out of scope

- Applying a precedent's drawdown rate to today's $987bn or ~$300bn. Report each rate with its population; the supervisor does
  any application.
- Describing the AI-adjacent figure as lending to the build-out (C-115).
- Claims about what moved asset prices (C-077), and any price-impact multiplier.
- Paid data (E-005). If the only source for a number is paid, say so and leave the number out.

## Return — to a file, not to chat

Write `_research/2026-10-01-RV1-Revolver-Drawdown-Return.md`, dated the day you run it. Use these sections, as flat tables:

1. **PRECEDENT, March–April 2020**: claim | number | denominator and population | window | source (URL, page or table) | grade
2. **DRAWDOWN RATES BY FACILITY TYPE**: facility type | population | undrawn before | drawn in the episode | rate | window | source | grade
3. **TRIGGERS**: trigger | mechanism | evidence that it operated (episode, magnitude) | source
4. **WHAT STOPS IT**: brake | evidence | source
5. **FREE SERIES FOR A DRAWDOWN MONITOR**: series | issuer | URL | frequency | lag | what a drawdown would look like
6. **CITATIONS CHECKED**: every source cited, and for each whether you opened it and whether it says what you cite
7. **OBSERVED vs INFERRED**, then **UNCERTAIN**: what you inferred, and what would settle it

Then run `bash bin/check.sh --all`; all seven lines must show ✓. Commit to main, run `git pull --rebase`, then push. Never
force-push. Hand over with the note in SINGLE quotes:
`bin/check.sh --handover write grok rv1-revolver-drawdown done '<the precedent rate and its denominator, n sources, next step>'`

## Rules

- Do not ask clarifying questions. If something is ambiguous, state the assumption you made and carry on.
- If you cannot do part of this, say which part and why, and do the rest.
- If what you find contradicts this brief, say so explicitly.
- Never route around a refusal, a sign-in wall or a paywall.
- Everything you commit is public: no personal data, no copied paywalled text, and quotes of 15 words or fewer.
