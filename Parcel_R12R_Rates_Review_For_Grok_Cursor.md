# R12R — Attack R1 and R2, the first rates findings (Grok in Cursor)

**Status: RETURNED and ADJUDICATED, 27 Sep 2026.** The return and the supervisor's adjudication are in
`_research/2026-09-27-R12R-Rates-Review-Return.md`; the corrections are C-122 to C-125. **Was: READY, 27 Sep 2026.** The principal asked for R1 and R2 to be documented for Grok to take. This is an adversarial
review routed to Grok in Cursor, with web search, to judge claims and to find sources whose citations must hold. It was written
by the supervisor. After the return, the supervisor revises, checks and adjudicates (THE_ASK E-008).

## Why this exists

Every major correction in this programme came from outside review, never from re-reading our own notes. R1 and R2 are the first
rates findings, and they were built in one day. **Make the strongest case that they are wrong.** Then say honestly whether they
survive, and name the one assumption in each that would sink it if wrong.

## Material

Read-only; you may run the scripts.
- `2026-09-27-R1-Treasury-10y-Decomposition.md`: what moved the US 10-year yield, end-2023 to 18 Sep 2026. Script:
  `bin/r1_treasury_decomposition.py`. Tables: `data/r1_rates/`.
- `2026-09-27-R2-Treasury-Duration-Supply-And-Holders.md`: how much duration the public absorbed, and who bought. Script:
  `bin/r2_duration_supply.py`. Tables: `data/r2_rates/`, including `checks.csv`.
- Context:
  - `CHARTER.md`: its "Grades" section, and the rule against claiming that flows caused a yield move.
  - `THE_ASK.md` E-007: everything is a hypothesis until tested.
  - `CORRECTIONS.md` C-102 (search for `## C-102`), the equity-premium lesson that R1 leans on.
  - `2026-09-12-N2c-Closure-Refresh-2026Q2.md`: the Z.1 buyer table R2 uses.

Both scripts fetch their free inputs themselves: Treasury par curves, the New York Fed ACM and SOMA data, the Fed Board's
Kim-Wright file, the Treasury's MSPD and the Philadelphia Fed SPF. You may re-run them. You may also use any other free source,
including FRED if it is reachable from your environment. You may write only the return file named below, and your handover row.

## What to attack

**R1, prices:**
1. **Re-derive the headline numbers from source, independently of our script.** Take the 10-year par yield from 3.88% to 5.01%,
   the 10-year TIPS yield from 1.72% to 2.68%, and the breakeven. Check the window endpoints, 29 Dec 2023 and 18 Sep 2026.
2. **The two models.** Check that they are read correctly: ACM `ACMY10 = ACMRNY10 + ACMTP10`; Kim-Wright
   expected = `THREEFY1000 − THREEFYTP1000`. Check whether mixing their fitted zero-coupon yields with par yields distorts
   anything.
3. **The survey check.** This carries R1's main negative: models and survey disagree in sign over February 2024 to February 2026.
   Test it hard:
   - Is SPF `BILL10`, a 10-year average of the three-month bill, a fair comparator for the models' expected average short rate?
   - Find the actual SPF first-quarter survey deadlines for 2024, 2025 and 2026, and redo the comparison on those dates instead of
     our approximate 14 February.
   - Does the finding survive with `BOND10`, or with any other free survey or market measure of expected rates?
   - Kim-Wright uses survey data in estimation. Does that weaken the comparison?
4. **The holder-return approximation.** R1 gives about +3.3% for a constant-maturity 10-year against about +12.2% for bills, from
   summed monthly income, roll-down and price change. Check it against any free Treasury total-return index or published return
   for the window, and say whether compounding or the roll-down method changes the conclusion.

**R2, supply and buyers:**
5. **Re-derive the supply totals.** Check MSPD total marketable and bills against MSPD Table 1 at 31 Dec 2023 and 31 Aug 2026, and
   the Fed's holdings against the H.4.1.
6. **The 10-year-equivalent method.** Attack the duration formulas, pricing on par curves, TIPS treated as nominal duration,
   floating-rate notes at 0.02 years, and the bill convention.
   - **Attack the constant-price measure hardest.** Pricing later securities on the end-2023 curve values higher-coupon bonds at
     a premium, and it includes ageing.
   - Does "duration outgrew face value (+36% against +26%)" survive another quantity measure? Examples: par-weighted duration on
     each date's own curve, or both dates of each period priced on their average curve.
7. **"About 96% from Treasury issuance, about 4% from the Fed."**
   - Is the change in the Fed's 10-year equivalents the right measure of quantitative tightening's contribution?
   - Build the alternative: the duration Treasury had to refinance because the Fed did not reinvest maturing securities.
   - Say whether the split changes.
8. **The buyer table.** Consider Z.1 vintage revisions, the nine rows' $132bn overlap, and the assumption that money-market funds
   took bills. Check the funds' actual Treasury composition (bills, floating-rate notes, coupons) in 2024–26 from the OFR money
   fund monitor or N-MFP data. Check also whether the "rest of the world" (which includes offshore hedge funds) overlaps the
   household residual (which includes domestic hedge funds).
9. **Outside estimates.** Find published figures to compare with R2, each with a URL and page:
   - the New York Fed's SOMA annual reports, which state the portfolio in 10-year equivalents;
   - Treasury Borrowing Advisory Committee charges on duration supply or 10-year equivalents;
   - Fed or academic estimates of duration held by the public in 2024–26.

   Do they agree in magnitude and direction?
10. **Causation.** Is anything in R1 or R2 phrased as if flows or supply caused the yield move? The charter forbids that.

## Out of scope

- JGBs and euro-area bonds (that is R3).
- Price-impact multipliers (C-077).
- Proposing new research directions, beyond saying what would settle each attack.

## Return — to a file, not to chat

Write `_research/<date you run it>-R12R-Rates-Review-Return.md` with these sections, as flat tables:
1. **RE-DERIVED:** claim | our value | your value | source (URL, table or page) | match or mismatch
2. **ATTACKS:** target (1–10) | strongest case against | evidence | verdict (STANDS / WEAKENED / FALLS) | what would settle it
3. **OUTSIDE ESTIMATES:** figure | value | source (URL, page) | agrees with R1 or R2? (yes / no / not comparable)
4. **OVERCLAIMS OR GRADE ERRORS:** file:line | what the note says | what the evidence supports
5. **LOAD-BEARING ASSUMPTIONS:** R1: the assumption that sinks it if wrong; R2: the same
6. **CITATIONS CHECKED:** every source you cite, and for each whether you opened it and whether it says what you cite
7. **OBSERVED vs INFERRED**, then **UNCERTAIN**: what you inferred, and what would settle it

Then run `bash bin/check.sh --all`; all seven lines must show ✓. Commit to main, run `git pull --rebase`, then push. Never
force-push. Hand over with the note in SINGLE quotes:
`bin/check.sh --handover write grok r12r-rates-review done '<verdicts for R1 and R2, the load-bearing assumptions, next step>'`

## Rules

- Do not ask clarifying questions. If something is ambiguous, state the assumption you made and carry on.
- If you cannot do part of this, say which part and why, and do the rest.
- If what you find contradicts this brief or the notes, say so plainly. That is the point of the exercise.
- Do not edit R1, R2, their scripts or their tables. Findings go in your return file; the supervisor applies them.
- Never route around a refusal, a sign-in wall or a paywall.
- Everything you commit is public: no personal data, no copied paywalled text, and quotes of 15 words or fewer.
