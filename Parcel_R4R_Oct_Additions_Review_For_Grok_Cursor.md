# R4R — Attack the October additions: JGB duration, the German split, CFTC, N-PORT, EFA, the multiplier, RV1, z_k (Grok in Cursor)

**Status: READY, 9 Oct 2026.** Written by the supervisor after the 8 Oct audit found that everything landed since the R3R review
(28 Sep) had been checked only internally (THE_ASK E-019: "work through all the items"). Routed to Grok in Cursor, with web
search, to judge claims and to find sources whose citations must hold. After the return, the supervisor revises, checks and
adjudicates (THE_ASK E-008), as for R12R and R3R.

## Why this exists

Every major correction in this programme came from outside review, never from re-reading our own notes. R12R found four errors
(C-122 to C-125) and R3R three (C-126 to C-128). The eight results below were each re-derived once by the supervisor, on one
number apiece, and by no one outside. **Make the strongest case that each is wrong.** Then say honestly whether it survives, and
name the one assumption that would sink it if wrong.

## Material

Read-only; you may run any script named here (each fetches its own free inputs or rebuilds offline).
- `CHARTER.md` "Grades" section, and its rule against claiming that flows caused a price move.
- `THE_ASK.md` E-007 (everything is a hypothesis until tested) and E-010 (the FIA key is permitted).
- `CORRECTIONS.md`: C-108 (with its "Update, 9 Oct" line), C-124, C-127 (with its "Update, 8 Oct" line), C-129.

## What to attack

1. **JGB duration supply.** `2026-09-27-R3-JGB-And-Euro-Area-Bonds.md`, section "Follow-up, 8 October 2026"; script
   `bin/r3b_jgb_duration.py`; outputs `data/r3_rates/jgb_duration_*.csv`. Claim: at constant yields Japan's public took +16.0%
   more fixed-coupon JGB rate risk from Oct 2024 (observed) and +24.8% from end-2023 (start stock interpolated).
   - The end-2023 market stock by issue is interpolated between Internet Archive snapshots of the BoJ JGB Handbook. Is there a
     free observed end-2023 by-issue stock (MoF, JSDA, BoJ)?
   - Are the exclusions material (JGBi, the 15-year floater, retail JGBs, bills, STRIPS)?
2. **The German 2024–25 split.** Same note, Germany block. Claim: on the 0.1% 2033 linker (DE0001030583), 29 Dec 2023 to 30 Dec
   2025, the real yield rose 87bp and the interpolated nominal 66bp, so the breakeven fell 21bp. Source: the Bundesbank's monthly
   "Prices and yields of listed Federal securities" xlsx.
   - Re-derive from the Bundesbank files.
   - Test the liquidity-premium caveat: Germany stopped issuing linkers in 2024. Is there free evidence that linker liquidity
     premia rose over 2024–25?
3. **CFTC Treasury-futures positioning and C-129.** `bin/pull_cftc_tff.py`; `data/cftc_tff/`; R2 note, "Follow-up, 9 October
   2026". Claim: leveraged funds' aggregate net short across six CBOT Treasury contracts was −$1,154bn of face at end-2025 and
   −$774bn on 29 Sep 2026.
   - Check the contract codes and the per-contract DV01s against CME's own material (the script's DV01s are second-hand).
   - C-129 says the old "2.2–2.8× the pre-March-2020 peak" is wrong and the ratio is about 1.5–1.9×. Find any public source that
     supports 2.2–2.8×, and say on what basis.
4. **Registered funds' AI-build-out paper (N-PORT).** `2026-08-22-D2-Who-Holds-The-AI-Paper.md` section 10;
   `bin/census_nport_bulk.py`; `data/nport/`. Claim: like for like (one report per fund), registered funds' Beignet holdings were
   flat at about $9.7bn from 2026Q2 to 2026Q3 (36% of the $27bn deal), while CoreWeave roughly doubled to about $5.1bn.
   - Test the de-duplication rule.
   - Test the "debt only = not equity" rule.
   - Test the name-evident subsidiary groupings (WULF Compute, Cipher Compute).
5. **The EFA revision.** C-108 and its 9 Oct update; `2026-09-13-S1-Supply-Decomposition.md`. Claim: on the Fed's 18 Sep EFA,
   2024Q1–2026Q1 M&A retirement is $911.3bn against net retirement of $704.0bn (129.4%). The EFA and Z.1 net issuance series
   differ by a stable same-vintage offset (mean about +$5.3bn a quarter, correlation 0.993), not by an unreconciled gap. Is the
   offset explanation right, and is the eREIT exclusion its cause?
6. **The collateral multiplier.** `Shadow_Debt_Channel_Map.md` (search "collateral_multiplier"); `bin/build_collateral_multiplier.py`;
   `data/history/collateral_multiplier_weekly.csv`. Claim: c is "down ~36% from its 2023 peak". That is on annual means, with
   2026 partial to 12 Aug, and 154 of 704 weeks imputed from FR 2004 venue components. Attack the imputation, the annual-mean
   peak definition and the small-denominator fragility (R_T under $100bn in 12 weeks).
7. **RV1 drawdown sizing.** `2026-09-27-RV1-Drawdown-Sizing.md` with its "Supervisor follow-up, 9 October 2026". Claim: a
   2020-style drawdown of NDFI bank lines would be about $107–297bn on the 2Q26 unused base of $1,089.8bn (Call Report RC-L).
   Attack the rates, the subtype mix argument and the cross-population 9.7% low end.
8. **z_k at 2026Q2.** `2026-08-31-N2b-zk-The-Wholesale-Share.md`, "Update, 4 October 2026"; `_research/n2b_v2/build_zk.py`.
   Claim: the wholesale non-M2 share of nonbank funding is 22.96% at June 2026, against 23.07% at March. Earlier quarters are
   frozen at old vintages, and the D4 columns mix two Z.1 vintages. Does the fall survive on one vintage? (`build_zk.py` needs a
   gitignored ALFRED file you do not have. Say what you can test without it.)

## Out of scope

- FX and commodities, parked by the principal on 9 Oct (E-019).
- The Singh correspondence (private).
- Proposing new research directions, beyond saying what would settle each attack.

## Return — to a file, not to chat

Write `_research/<date you run it>-R4R-Oct-Additions-Review-Return.md` with these sections, as flat tables:
1. **RE-DERIVED:** claim | our value | your value | source (URL, table or page) | match or mismatch
2. **ATTACKS:** target (1–8) | strongest case against | evidence | verdict (STANDS / WEAKENED / FALLS) | what would settle it
3. **OUTSIDE ESTIMATES:** figure | value | source (URL, page) | agrees with ours? (yes / no / not comparable)
4. **OVERCLAIMS OR GRADE ERRORS:** file:line | what the note says | what the evidence supports
5. **LOAD-BEARING ASSUMPTIONS:** per target, the one assumption that sinks it if wrong
6. **CITATIONS CHECKED:** every source you cite, and for each whether you opened it and whether it says what you cite
7. **OBSERVED vs INFERRED**, then **UNCERTAIN**: what you inferred, and what would settle it

Then run `bash bin/check.sh --all` (about 15 seconds); all seven lines must show ✓. Commit to main, run `git pull --rebase`,
then push. Never force-push. Hand over with the note in SINGLE quotes:
`bin/check.sh --handover write grok r4r-review done '<verdict per target, load-bearing assumptions, next step>'`

## Rules

- Do not ask clarifying questions. If something is ambiguous, state the assumption you made and carry on.
- If you cannot do part of this, say which part and why, and do the rest. If your token budget runs short, do targets 1–4 first.
- If what you find contradicts this brief or a note, say so plainly. That is the point of the exercise.
- Do not edit the notes, scripts or tables under review. Findings go in your return file; the supervisor applies them.
- Never route around a refusal, a sign-in wall, a rate limit or a paywall. Do not use sec.gov (it needs a declared contact).
- Never use an API key or token found in page code, except the FIA key the principal permitted (E-010).
- Everything you commit is public: no personal data, no copied paywalled text, and quotes of 15 words or fewer.
