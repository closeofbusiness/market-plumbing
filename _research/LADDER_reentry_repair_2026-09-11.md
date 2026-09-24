# Step-ladder on the re-entry infrastructure — state (session scratchpad; promote to tier 2 after rung 1)
Started 2026-09-11. Folder: ~/Dropbox/31 - Claude Cowork/Work/2026.08 - Third Derivative Research

## Falsifiable criterion (fixed BEFORE any change)
A fresh Sonnet agent, given only the folder, answers 8 state questions. BASELINE = cold-read run 1
(in flight). After improvements, cold-read run 2 must score STRICTLY better against the key below.

## Answer key — committed before seeing any agent answer
Q1 goal: "A comprehensive, fundamental understanding of the nonbank-bank nexus: every mechanism by
   which collateral and money creation operate in the shadow banking system."
Q2 top open task: Singh thread — the sec-lending leg of the back-test is untested (N3v4 s6
   caveats), then the Singh BRIEFING (ranked 1: only item with a person waiting; decays).
   TRAP: ranked block lists finished "0. back-test DONE" above it.
Q3 Singh: his HF source series is SMOOTH (+18.9% 2013-17, annual steps sd 1.01pp) vs Form PF
   collateral LUMPY (+39.1%, sd 6.84pp) => not a Form PF aggregate. Ask: "measured aggregate or
   trended estimate, and from which collection?" (N3v4 s6; C-074 killed the one-row 32% claim)
Q4 z_k: non-M2 funding of banks from other nonbanks (Pozsar-Singh). v2 widest perimeter: 13.10%
   -> 23.07% on M2; 16.42% -> 29.22% on H.8 deposits less large time; 2021-12 -> 2026-03; three
   lenses passed; READY to carry N4. (N2b doc s8)
Q5 routing: Grok to FIND (citations hold); Gemini to READ named sources (fabricates citations when
   searching; flawless reading). Deep Research: highest hallucination rate measured. (CLAUDE.md +
   ~/.claude/skills/orchestrator_outside)
Q6 latest correction: C-074 — killed "32% of the cash-like bucket reproduces his method" (one row).
   Lesson: compute a calibration everywhere before calling it a convention; a caveat is not a
   substitute for running the check.
Q7 must-not-send: the 3 drafts in _research/singh_briefing_drafts/ (C-073 "independently
   reproduces"). TRAP: the ask doc's REWRITE SPEC still carries the OLD gross-vs-netted question,
   superseded by N3v4 s6.
Q8 due/overdue at 2026-09-11: 05 Sep goal read-back; 08 Sep Actrix; 10 Sep N-MFP3 census;
   10 Sep OFR HF Q2. (12 Sep Z.1 tomorrow.)

## Rung status
1 Investigate — IN FLIGHT: cold-read | mechanism(read order) | contradictions | prior-art/template
2 Verify  3 Spec  4 Review  5 Re-spec  6 Implement (snapshot docs first; python in-place writes)
7 Verify  8 Land = gate (check.sh --all, --goal) + cold-read run 2 beats baseline

## BASELINE RESULT (cold-read run 1, graded against the key above)
8/8 substantively correct; Q2 partial (missed sec-lending leg as a gate before the briefing).
BUT it succeeded by reading AROUND the prescribed tools, 24 tool calls. Defects it found:
 F1 check.sh --todo pattern-matches bolded tier headers (**N#, **D#); the real ranking is in a
    fenced block => the "what's next" command returns mostly-CLOSED items. bin/check.sh ~L45-51.
 F2 prescribed `head -40 CORRECTIONS.md` shows C-001..003 (oldest, irrelevant); load-bearing
    C-070..074 are at the bottom of an append-only 1076-line file.
 F3 read-table gating ("if Singh/velocity") only legible in hindsight.
 S1 CLAUDE.md "Live items" is stale + self-contradicting: says CALENDAR row 1 (17 Aug RTO) OVERDUE
    (it is done, C-048); says C-001 unpropagated (register says Propagated 21 Aug); frozen
    "19 days old" day-count. Violates CLAUDE.md's own no-status rule.
 S2 Singh-Ask read-table row has no "original questions superseded" warning.
## REFINED CRITERION for cold-read run 2 (8/8 is ceiling, cannot discriminate):
 (a) the PRESCRIBED commands alone surface the correct top priority AND the latest correction;
 (b) cold reader reports ZERO stale/self-contradicting status lines in CLAUDE.md;
 (c) fewer tool calls than 24 to reach all 8 answers.

## LENS: prior-art — returned. CORROBORATES cold-read F1 and S1 independently (different method).
 NEW P1 7 of 62 top-level .md have ZERO mention in CLAUDE.md: Parcel_D10R, _N2aR, _N2a, _N2bR, _SB1,
    _ZK2, Review_Prompt_For_Grok. Table stopped being maintained ~30 Aug; CLAUDE.md edited to 4 Sep.
 NEW P2 ~95-100 of 445 CLAUDE.md lines (~21%) are CHANGING facts that should be pointers:
    L96-114 legs status (interlock "not visible" superseded by z_k), L118-129 Delivered lists,
    findings embedded in read-table rows, L280-306 model routing w/ benchmark numbers, L434-446 Live items.
 NEW P3 no "## Re-entry" section with a stopping point; 14 top-level sections undelineated.
 NEW P4 C-040 "Outstanding: unpromoted do-not-say items need triage" (22 Aug) may have fallen off.
 NEW P5 two list items both numbered "9." (L359, L364) - editorial rot.
 PATTERN (6 instances): a fact gets a 2nd hand-written home; nothing detects drift. The ENFORCEMENT
    layer drifts too (check.sh --todo written against an old structure).
 prior-art TOP3: (1) give the ranked block a stable fenced marker like ```goal and point --todo at it;
    (2) delete Live items -> pointer; (3) orphan check: fail when a root .md has no CLAUDE.md mention.
## still out: mechanism (read-order trace), contradictions sweep

## RUNG 1 COMPLETE — all 4 lenses in. Supervisor-verified the 2 load-bearing claims myself.
CROSS-LENS AGREEMENT (the signal):
 A1 CLAUDE.md "Live items" false (row1 overdue=done; C-001 unpropagated=propagated; 19d=40d) — 4/4 lenses
 A2 check.sh --todo returns OLD tier list, 0 current-priority markers — 3 lenses + MY RUN (mechanism
    lens said "correct output" = ran without error; wrong on the question that matters. verifier wins)
 A3 7 orphan parcels absent from CLAUDE.md — 2 lenses, same 7 files
UNIQUE, HIGH VALUE:
 U1 KILLED CLAIM DEFEATS THE GUARD — FT-Harvest.md:40 "The Fed took ~69% of 2026's net bill supply"
    = C-063. Regex `69(%| percent).{0,40}net bill issuance` misses (word order reversed). Not
    allow-listed. REQUIRED READING x3 (CLAUDE.md:179). check.sh --all = green. VERIFIED BY ME.
 U2 RESEARCH_STATE.md:517 dead D10 figures (84%, five banks, 7.9trn) — and NO C-entry exists for the
    five->six-bank error (it was folded as an "amendment", never registered)
 U3 gross private saving CONTESTED in RS §1.1 but "High confidence settled" in RS §2 S4 — and RS §7
    tells reviewers "do not re-derive anything in §2"
 U4 RS Tier-N never reconciled: N2 "we have nothing", N2a/N2b un-started — all built+reviewed. An OLD
    numbered list survives below the re-set block. No S-N2b settled row for corrected z_k.
 U5 mandatory "always" read stated ~13k tok, actual ~54k; Verifier floor ~124k, Synthesist ~150k tok
    = 60-75% of a 200k context before any conditional row. CORRECTIONS 13.9x under-stated.
 U6 filename vintage unreliable: 13/29 dated files modified after filename date (up to +8d)
 U7 check.sh --all takes ~2 min on the SMB mount
DIAGNOSIS (prior-art named it; contradictions lens REFINED my framing):
 Not missing knowledge. Facts acquire a 2nd hand-written home and drift; the ENFORCEMENT layer drifts
 with them. KEY CORRECTION TO MY BRIEF: most drift is NOT paraphrase evading a regex — it is status
 prose never touched after the fact changed, WITH NO CORRECTION ENTRY AT ALL. Widening regexes cannot
 fix that. The fix is structural: fewer copies, and oracles that fail loudly when their target moves.
CONTRADICTS WHAT I TOLD MARTIN: my 3 Sep housekeeping said "all five hold, checks green". The checks
 were green on a live killed claim in required reading, and CLAUDE.md carried false statuses.
NEXT: rung 2 verify is largely done (both collapse-points verified by me). Spec next.

## RUNG 2 — effectively done (supervisor verified both collapse-points by one command each).
## RUNG 3 — SPEC WRITTEN: _research/SPEC_reentry_infrastructure_2026-09-11.md (81 lines, durable tier 2)
   MUST M1 --todo reads ```ranked fence + fails loud | M2 corrections show newest | M3 delete Live items
        M4 kill C-063 in FT-Harvest + regex that FAILS on pre-fix tree | M5 orphan check (7 -> 0)
   SHOULD S1 RS:517 dead D10 | S2 register five->six bank | S3 gross-saving contested | S4 Tier-N
        reconcile + S-N2b | S5 strip findings from table rows | S6 re-baseline budgets
   CRITERIA C1..C6 (C6 = cold-read run 2 beats baseline on the REFINED criterion)
## RUNG 4 — IN FLIGHT: reviewer A correctness (fix vs relocate) | reviewer B cost/practicality (noise)
## NEXT: rung 5 re-spec (MINE) once both land; then snapshot -> rung 6 implement.

## RUNG 4 — reviewer A (CORRECTNESS) returned: survives-with-changes
 LOAD-BEARING FLAW: C1-C6 test PRESENCE, never FIDELITY. Diagnosis = "present but wrong"; criteria only
   check the right thing EXISTS. None catches a fact that is present and false.
 M1 = symptom fix: fails loud on fence ABSENCE, never on staleness or a SECOND COPY — and a 2nd copy
   ALREADY EXISTS at RS:507-522 directly below the fence, carrying the dead D10 figures.
 M4 = ineffective as a class guard: "Treasury" inserted / word order flipped / "percent" spelled out all
   evade the new pattern (reviewer ran grep). Speed bump only.
 M5 blind spot: -maxdepth 1 misses Personas/; "mentioned anywhere" satisfied by the File Structure table
   (not read order).  S6 relocates: a hand-typed number that will drift again.
 REQUIRED: (1) M1 also rejects a numbered/status list OUTSIDE the fence; (2) promote S4 (delete dup list)
   to MUST + criterion; (3) label M4 a speed bump honestly; (4)(5) M5 recurse + require a read-TABLE ROW;
   (6) MECHANISM: flag any [C-0NN] strike banner lacking a matching "## C-0NN" in CORRECTIONS;
   (7) ROOT FIX PILOT: data/status.tsv as the single queried home for one class of status fact, rendered
       by both the fence and --todo => a second home becomes structurally impossible for that class.
 EXPECTED CONFLICT for rung 5: reviewer B (cost) likely says orphan check = noise; A says make it STRICTER.

## RUNG 4 — reviewer B (COST) returned: survives-with-changes. M1 contradicts check.sh:2-4 doctrine
   "warn never block / exit 0 always" (--goal exits 0 even on drift, proven). M5 self-flags CLAUDE.md.
   S1/S4 edit the same text. Noise LOW: ~1 orphan per 2-4 months -> signal. No breakage. --all = 89s.
## RUNG 5 — DONE. Spec amended in place (section at end). OVERRULED my M1 non-zero exit (doctrine).
   SCOPED OUT data/status.tsv (trigger recorded). ADDED M6 second-home detector, M7 unregistered-
   correction detector. S4 -> MUST, S1 dropped. Criteria C1-C8, each guard must FAIL on pre-fix tree.
## NEXT: rung 6 — SNAPSHOT touched files to _research/snapshot_2026-09-11/ FIRST, then builder agent.

## RUNG 6 — IN FLIGHT. Snapshot at _research/snapshot_2026-09-11/ with MD5SUMS.txt (the rollback).
   Builder (Sonnet) scope: M1-M7 + S4 + S2. PHASE A = add guards, run on UNCHANGED docs, must FIRE;
   if any does not fire -> STOP. PHASE B = apply fixes, re-run. Out of scope: S3, S5, S6, S-N2b,
   Tier-N pointers, Parcels/ move.
## RUNG 7 CHECKLIST (mine): (1) each guard FIRED on pre-fix tree per Phase A output — verify by
   re-running a guard against the SNAPSHOT copy myself; (2) diff every changed file vs snapshot;
   (3) any existing check weakened? (4) diff matches the rung-5 spec, no drift; (5) M7 mismatches
   reviewed by hand; (6) goal + all still pass.
## RUNG 8: gate + cold-read run 2 against the REFINED criterion C8.

## RUNG 6 — DONE (builder). M1-M7 + S4 + S2 (new C-075). All guards fired on pre-fix, pass post-fix.
## RUNG 7 — DONE (supervisor, independent, vs SNAPSHOT): M1 fires (exit 0) | M4 old pattern [0]/new [1][1]
   | M6 flags 507-522 exact, no Tier-N | M7 NOT vacuous (17 banners/10 ids) | 130->134 patterns, 0 removed
   | exit-0 doctrine held. ONE CATCH: builder allow-listed D10 for C-075 while D10 §2 carried LIVE unstruck
   five-bank/84% text = silenced a guard. FIXED: annotated all 3 sites with [C-075] banners -> allow honest.
   Deviations accepted: M5=8 (Personas/ legit); M6 scoped to Tier O (verified it discriminates).
## RUNG 8 — GATE GREEN: --goal pass; --all: 0 orphans, 0 second-home, all banners registered, 0 killed
   claims. C1: --todo 21 current-priority markers (was 0). Cold-read run 2 IN FLIGHT vs criterion C8.
