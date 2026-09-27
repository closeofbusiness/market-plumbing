# R3R — Attack R3, the first findings on JGBs and euro-area government bonds (Grok in Cursor)

**Status: READY, 27 Sep 2026.** The principal ruled on 27 Sep that the next work goes ahead (THE_ASK E-017). R3 was built the
same day. This is an adversarial review routed to Grok in Cursor, with web search, to judge claims and to find sources whose
citations must hold. It was written by the supervisor. After the return, the supervisor revises, checks and adjudicates
(THE_ASK E-008), as it did for R1 and R2 (R12R).

## Why this exists

Every major correction in this programme came from outside review, never from re-reading our own notes. The R12R review of
R1 and R2 found four real errors in one pass (C-122 to C-125). R3 has had no outside review. **Make the strongest case that it
is wrong.** Then say honestly whether it survives, and name the one assumption that would sink it if wrong.

## Material

Read-only; you may run the script.
- `2026-09-27-R3-JGB-And-Euro-Area-Bonds.md`: what moved the 10-year JGB and Bund yields, end-2023 to 24 Sep 2026, and who
  bought. Script: `bin/r3_jgb_egb.py`. Tables: `data/r3_rates/`.
- Context:
  - `CHARTER.md`: its "Grades" section, and the rule against claiming that flows caused a yield move.
  - `THE_ASK.md` E-007: everything is a hypothesis until tested.
  - `CORRECTIONS.md` C-124 (search for `## C-124`): nested sectors counted twice in a buyer table, and offshore hedge funds
    hidden in a residual. R3's two buyer tables are exposed to both.
  - `2026-09-27-R1-Treasury-10y-Decomposition.md` and `2026-09-27-R2-Treasury-Duration-Supply-And-Holders.md`, as corrected.

The script fetches its free inputs itself: the Ministry of Finance's yields and auction history, the JSDA's reference prices,
the BoJ's Flow of Funds API, the Bundesbank's API, and the ECB's Data Portal and programme histories. The JSDA rate-limits
scripted requests (HTTP 429); wait and retry rather than working around it. You may use any other free source. You may write
only the return file named below, and your handover row.

## What to attack

**Japan:**
1. **Re-derive the levels independently of our script.** The 10-year JGB from 0.647% to 3.073% and the 2-year from 0.048% to
   1.912% (Ministry of Finance, 29 Dec 2023 and 24 Sep 2026). Cross-check against any other free source.
2. **The breakeven, R3's main Japanese claim:** real yields about +145bp, breakeven about +97bp.
   - Re-derive the JGBi real yields from the JSDA prices and the Ministry's coupons (issues #28 to #31).
   - Check the method against the Ministry's own breakeven chart (`mof.go.jp/jgbs/topics/bond/10year_inflation-indexed/bei.pdf`)
     for any date you can match, including archived copies.
   - Test the deflation floor, the choice of the newest issue, the compounding convention and the half-year maturity gap.
   - Does "inflation compensation did about two-fifths of the rise" survive?
3. **The Flow of Funds buyer table.**
   - Re-derive the 2024Q1–2026Q2 transactions from the BoJ API, and check that the rows partition the holders. Securities
     investment trusts are taken to sit beside "other financial intermediaries"; public pensions inside general government.
   - Check public pensions' +¥32.3trn against GPIF and other public-fund disclosures.
   - Compare with the BoJ's own estimate (Bank of Japan Review 2026-E-10, Chart 8) and the Ministry's holder breakdown.
4. **The holder's return:** −13.9% for a constant-maturity 10-year JGB against +1.6% for the 1-year. Check it against any free
   JGB total-return index or fund return for the window.

**Euro area:**
5. **Re-derive the levels:** the Bund 10-year from 2.06% to 3.62% and the 2-year from 2.35% to 3.30% (Bundesbank), the ECB
   AAA curve, and the Italy–Germany and France–Germany spreads.
6. **The survey-based real split, R3's main euro-area claim:** the Bund's rise was almost all real.
   - Is the Bundesbank's expected real rate (the average Bund yield minus Consensus inflation forecasts) a fair stand-in for a
     market real yield?
   - Find any free market measure: German or French inflation-linked bond yields, or inflation-swap-based expectations
     published by the ECB or the Bundesbank. Does "almost all real" survive?
7. **The holdings table.**
   - Check the partition: "other financial institutions" is taken to contain the investment funds.
   - Check the rest-of-the-world residual: total outstanding (CSEC, nominal value, all currencies) minus euro-area holders (SHSS,
     face value). Do the scopes and valuations match? Does leaving out Bulgaria matter?
   - Compare the Eurosystem's share (31.1% to 21.1%) with the ECB's own figures, and banks' +€725bn and the rest of the world's
     +€830bn with ECB or national central bank statements.
   - Does the rest of the world hide euro-area investors routed through offshore funds, as C-124 found for US Treasuries?

**Both:**
8. **The term premium.** Find published 2024–26 estimates of the 10-year term premium for JGBs and Bunds, with values. Does
   any contradict R3's statements: not measured here; "roughly the same degree" (BoJ); "fairly stable since" late 2023 (ECB)?
9. **The common pattern.** R3's item 8 says central banks shrank while banks, pension funds and foreign investors absorbed the
   supply in all three markets. Attack it.
10. **Causation and grades.** Is anything phrased as if flows or central-bank selling caused a yield move? Is any claim graded
    above its evidence?

## Out of scope

- US Treasuries (R1 and R2, already reviewed).
- Duration supply for JGBs or euro-area bonds, which R3 says it does not measure. Say only whether that omission changes a
  conclusion.
- Proposing new research directions, beyond saying what would settle each attack.

## Return — to a file, not to chat

Write `_research/<date you run it>-R3R-JGB-EGB-Review-Return.md` with these sections, as flat tables:
1. **RE-DERIVED:** claim | our value | your value | source (URL, table or page) | match or mismatch
2. **ATTACKS:** target (1–10) | strongest case against | evidence | verdict (STANDS / WEAKENED / FALLS) | what would settle it
3. **OUTSIDE ESTIMATES:** figure | value | source (URL, page) | agrees with R3? (yes / no / not comparable)
4. **OVERCLAIMS OR GRADE ERRORS:** file:line | what the note says | what the evidence supports
5. **LOAD-BEARING ASSUMPTIONS:** Japan: the assumption that sinks it if wrong; euro area: the same
6. **CITATIONS CHECKED:** every source you cite, and for each whether you opened it and whether it says what you cite
7. **OBSERVED vs INFERRED**, then **UNCERTAIN**: what you inferred, and what would settle it

Then run `bash bin/check.sh --all`; all seven lines must show ✓. Commit to main, run `git pull --rebase`, then push. Never
force-push. Hand over with the note in SINGLE quotes:
`bin/check.sh --handover write grok r3r-review done '<verdicts for Japan and the euro area, the load-bearing assumptions, next step>'`

## Rules

- Do not ask clarifying questions. If something is ambiguous, state the assumption you made and carry on.
- If you cannot do part of this, say which part and why, and do the rest.
- If what you find contradicts this brief or the note, say so plainly. That is the point of the exercise.
- Do not edit R3, its script or its tables. Findings go in your return file; the supervisor applies them.
- Never route around a refusal, a sign-in wall, a rate limit or a paywall.
- Everything you commit is public: no personal data, no copied paywalled text, and quotes of 15 words or fewer.
