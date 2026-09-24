# SPEC — re-entry infrastructure repair (step-ladder rung 3)
**Author: supervisor, 2026-09-11. Status: AMENDED at rung 5 after two adversarial reviews (correctness, cost). APPLIED 11 Sep 2026 (rung 8 gate green: `_research/LADDER_reentry_repair_2026-09-11.md`; open remainder in RESEARCH_STATE.md section 5). Rung-5 decisions are in the section at the END — read it; it overrides the body where they differ.**

## Goal (one sentence)
A fresh agent reaches correct current state THROUGH the prescribed tools rather than around them,
and the project's guards fail loudly when the thing they watch moves.

## Diagnosis this spec acts on (rung 1, four independent lenses + supervisor verification)
The knowledge survives; the retrieval machinery does not. Root cause: **a changing fact acquires a
second hand-written home, and the enforcement layer drifts along with the prose it polices.** Most
drift is NOT a killed claim evading its regex — it is status prose never updated after the fact
changed, **with no correction entry ever created**. A better regex cannot fix that. So the fix is
structural: fewer copies, and oracles that fail loudly. Verified collapse-points:
- `check.sh --todo` prints the superseded tier list; 0 current-priority markers (supervisor run).
- `check.sh --all` reports green while C-063's killed claim sits in required reading
  (FT-Harvest.md:40, word order defeats the regex; supervisor verified all four facts).

## Constraints (project bindings)
- NOT a git repo: no worktree. **Snapshot every file to be touched before rung 6** into
  `_research/snapshot_2026-09-11/`; that is the rollback.
- `~/Dropbox` is an SMB mount: the Edit tool fails; write in place with python.
- The real gate: `bin/check.sh --goal` and `bin/check.sh --all`. Both must pass after.
- Append-only files stay append-only: `data/series.tsv`, `CORRECTIONS.md` entries.

## Changes — MUST (the success criteria depend on these)

**M1. `--todo` reads a fenced, named block and fails loudly if it is missing.**
Change the ranked block's opening fence in RESEARCH_STATE.md from ```` ``` ```` to ```` ```ranked ````.
Rewrite `--todo` to extract exactly that block (same awk shape as `goal_check`) and exit non-zero with
a message if absent or empty. Keep the CALENDAR next-45-days view.

**M2. The corrections orientation shows the NEWEST entries.** CLAUDE.md's first-action block runs
`head -40 CORRECTIONS.md`, which surfaces C-001..003. Replace with a `check.sh --latest` (or an inline
command) printing the highest-numbered ~5 `## C-0NN` headings.

**M3. Delete CLAUDE.md "Live items" (≈L434-446).** Two of four bullets are false, one is 2× stale,
and it violates CLAUDE.md's own no-status rule. Replace with one line pointing at `check.sh --todo`.

**M4. Kill the surviving C-063 claim AND make the guard catch it.** (a) Add a ban pattern that
matches the FT-Harvest phrasing (e.g. `took ~?69%`, or `69%.{0,40}net bill supply`); (b) **prove it
FAILS on the current tree** (check.sh must flag FT-Harvest.md:40 before any fix); (c) strike the line
in FT-Harvest with a `[C-063]` banner and allow-list the file.

**M5. Orphan check.** Add to `check.sh --all`: fail when a top-level `*.md` has no mention anywhere
in CLAUDE.md. **Prove it lists the 7 known orphans on the current tree.** Then add read-table rows for
the six review parcels (or mark them historical like `Review_Prompt_For_Grok.md`) and for `Personas/`.

## Changes — SHOULD (correct live falsehoods)
**S1.** RESEARCH_STATE.md:517 — replace the dead D10 figures (84%, five banks, 7.9trn) with 83.2%,
six banks, $7,389.7bn, and point at D10 §6.
**S2.** Register the five→six-bank error as a CORRECTIONS entry (it was folded as an "amendment" and
never registered — the exact failure the diagnosis names). Add a ban pattern for "five banks".
**S3.** Resolve gross private saving: it is CONTESTED in RS §1.1 but "High confidence settled" in RS §2
row S4, and RS §7 forbids re-deriving §2. Mark S4 contested to match §1.1.
**S4.** Reconcile RS Tier-N: N2/N2a/N2b still read as un-started though built and reviewed; delete the
superseded numbered list surviving below the ranked block; add an S-N2b settled row for corrected z_k.
**S5.** Strip findings summaries out of read-table rows (they are copies that drift): each row states
what the doc IS and WHEN to read it, and points to its own status line. Keep "READ §N FIRST" pointers.
**S6.** Re-baseline read-table token estimates (always-set is ~54k, stated ~13k); mark CORRECTIONS.md
and CALENDAR.tsv "query only — never whole" in the row itself, as Shadow_Debt_Channel_Map already is.

## COULD (defer, with trigger)
- Filename-vintage caveat (45% of dated files modified after their filename date): document, do not
  rename. - `check.sh --all` takes ~2 min on SMB: accept.

## Falsifiable success criteria (exact command → expected result)
- **C1** `bin/check.sh --todo` output contains `SINGH` and `N4` (the current ranked items). Positive signal.
- **C2** Temporarily rename the ```` ```ranked ```` fence → `bin/check.sh --todo` exits non-zero. Restore.
- **C3** On the PRE-fix tree the new C-063 pattern makes `check.sh --all` FLAG FT-Harvest.md:40; after
  strike+allow it passes. (A guard that passes on the broken tree is worthless.)
- **C4** Orphan check lists **7** on the pre-fix tree and **0** after.
- **C5** `bin/check.sh --goal` and `--all` both pass after all changes.
- **C6** Cold-read run 2 (fresh Sonnet, same 8 questions, same key): (a) the PRESCRIBED commands alone
  surface the top priority and latest correction; (b) ZERO stale status lines found in CLAUDE.md;
  (c) fewer than the baseline's 24 tool calls.

## Open questions (marked, not guessed)
- Q1: Should S5 strip ALL findings from table rows, or keep a one-clause pointer? Stripping is cleaner
  but costs the reader a hop; this is exactly what reviewers should attack.
- Q2: Is there any other script or doc that parses the ranked block's plain ``` fence and would break
  when it becomes ```ranked? (Must be checked before M1 lands.)


---

## RUNG 5 — SUPERVISOR RE-SPEC (2026-09-11). Overrides the body above where they differ.

Both reviews: **survives-with-changes.** Both re-derived their numbers; the 7 orphans, the 0 SINGH
markers in `--todo`, and the green `check.sh` on FT-Harvest.md:40 were independently reproduced by each.

### The flaw both reviews exposed, and what changes because of it
**Every original criterion (C1–C6) tested PRESENCE, never FIDELITY** (correctness review). The
diagnosis is "present but wrong"; the criteria only checked that the right thing exists. And the
failure M1 guarded against — the fence *vanishing* — has never happened here, while the failure it
ignored — **a second copy appearing** — has happened twice in one file and is live today at
RESEARCH_STATE.md:507–522. Two fidelity mechanisms are therefore added (M6, M7).

### Overrules, stated plainly
- **OVERRULED: M1's non-zero exit and criterion C2.** `bin/check.sh` lines 2–4 are a documented
  prior decision — "Warn (never block)… Exit 0 always. A blocking gate gets reworded around; a
  warning leaves a trail." — and the cost review proved it is enforced (`--goal` returns exit 0
  even on a printed GOAL DRIFT). The defect was never that `--todo` fails to block; it is that it is
  **silently wrong**. It will now WARN LOUDLY and keep exit 0. The header comment then stays true.
- **SCOPED OUT, not overruled: `data/status.tsv`** (correctness review #7) — the genuine root fix,
  making a second hand-written home structurally impossible by rendering status from one queried
  table, as `data/series.tsv` already does for numbers. It restructures how the whole project
  records status, which is larger than this run should decide alone. **Trigger:** the next time a
  status fact is found in two places with different values, build it for that class first.

### Amended MUST list
- **M1 (amended)** `--todo` extracts the ```` ```ranked ```` block. Fence MISSING → print `✗` and
  explain. Fence present but EMPTY → print a neutral "no ranked items — caught up, or not yet
  ranked?" (not a failure). Exit 0 in all cases.
- **M2** unchanged — newest corrections, not oldest. (Correctness review: the one durable fix.)
- **M3** unchanged — delete CLAUDE.md "Live items", point at `--todo`.
- **M4 (relabelled)** Kill the FT-Harvest C-063 instance and add a pattern for its phrasing. **This
  is a speed bump against one observed phrasing, not a fix for the class** — the correctness review
  showed "Treasury" inserted, word order flipped, or "percent" spelled out all evade it. Keep it,
  describe it honestly.
- **M5 (amended)** Orphan check: (a) **exclude CLAUDE.md itself** (it never contains its own name —
  otherwise a permanent false positive); (b) top-level docs must appear as a **row in the read
  table**, not merely be mentioned (the File Structure table is not the read order); (c) recurse into
  subfolders at **folder** granularity — each subfolder needs a read-table row, not each file.
- **M6 (NEW — second-home detector)** In RESEARCH_STATE.md §5, flag any numbered list item
  (`^[0-9]+\. `) that sits OUTSIDE the ```` ```ranked ```` fence. Must flag the live duplicate at
  :507–522 on the pre-fix tree, and must NOT flag the Tier-N item headers (`**N2.` form).
- **M7 (NEW — unregistered-correction detector)** Flag any `[C-0NN]` banner in a findings doc whose
  `## C-0NN` heading does not exist in CORRECTIONS.md. Catches the correction that was applied but
  never registered. (It cannot catch one that was never applied at all — stated as a limit.)
- **S4 → MUST** Delete the superseded numbered list at RESEARCH_STATE.md:507–522 **and** the
  "Settled, not blocked (25 Aug)" paragraph after it (cost review #5). **S1 is DROPPED** — its target
  line is inside the list S4 deletes (both reviews).

### Amended SHOULD list
S2 (register the five→six-bank error) · S3 (mark gross-saving S4 row contested) · S4-residual:
Tier-N keeps its DESCRIPTIONS (what each item is — durable) but its status clauses become pointers
to the ranked block · S5 (strip findings from read-table rows; keep "READ §N FIRST" pointers) ·
**S6 (amended)** mark CORRECTIONS.md and CALENDAR.tsv "query only — never whole" in the row, and
**do not restate token counts** (a hand-typed number drifts; correctness review) · add an S-N2b
settled row for the corrected z_k.
COULD: move `Parcel_*.md` into `Parcels/` (cost review #7) — 6 of the 7 orphans are parcels.

### Amended falsifiable criteria (each guard must FAIL on the pre-fix tree)
- **C1** `check.sh --todo` output contains `SINGH` and `N4`.
- **C2 (replaces the overruled one)** Rename the ```` ```ranked ```` fence → `--todo` prints a `✗`
  line naming the missing block. Restore.
- **C3** Pre-fix: the M4 pattern flags FT-Harvest.md:40. Post-fix: passes.
- **C4** Pre-fix: M5 lists the 7 orphans and does NOT list CLAUDE.md. Post-fix: 0.
- **C5** Pre-fix: M6 flags RESEARCH_STATE.md:507–522 and no Tier-N header. Post-fix: 0.
- **C6** M7 run on the pre-fix tree reports every banner/heading mismatch it finds; supervisor
  reviews each by hand (no expected count is assumed — that is what this run discovers).
- **C7** `check.sh --goal` and `--all` still print their pass lines (regression).
- **C8** Cold-read run 2: (a) the PRESCRIBED commands alone surface the top priority and latest
  correction; (b) ZERO stale status lines found in CLAUDE.md; (c) fewer than 24 tool calls.
