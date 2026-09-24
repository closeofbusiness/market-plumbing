# THE ASK — what the principal actually said, verbatim

**APPEND-ONLY. NEVER EDIT AN EXISTING ENTRY. NEVER PARAPHRASE INTO THIS FILE.**

This file exists because on 22 August 2026 this project served the wrong goal for a day while
every document agreed with every other document. Nothing was lost in compaction; the recorded
goal was simply *wrong*, and the apparatus faithfully propagated it.

**The rule that follows from that:** every goal statement anywhere in this project must be
derivable from a quoted entry below, and must cite it. Paraphrase is where corruption enters,
so this file holds **only** the principal's own words. If you find yourself improving the
wording, stop — that is the failure this file prevents.

---

## THE CANONICAL GOAL

`bin/check.sh --goal` verifies this exact string appears in `CLAUDE.md` and `RESEARCH_STATE.md`.
Changing it here without changing it there — or the reverse — fails the check.

```goal
A fundamental, quantified understanding of what is driving asset prices higher and where the money is coming from — including the funding of the AI build-out and the IPO boom — across every channel: direct money creation, shadow banking and shadow money creation, the collateral channel, market-structure flows such as the passive bid and ETF creation, and any other driver the evidence reveals.
```

**Derived from entry E-003 below (11 Sep 2026), which widens E-002; the agent's additions in it were confirmed in E-004.** If you believe the canonical string no longer matches the
verbatim record, **do not rewrite it** — raise it with the principal and append a new entry.

---

## E-012 · 24 September 2026 — can a stranger read the repository, and can the page live in it

Given in one message, after the history rewrite was reported done.

> *"Ok, is the Github understandable for third parties? Also, this artifact, can we have this as local http in the Github: https://claude.ai/artifact/QiSp2xPb2Xx5jkAvNDApZk"*

**Reading notes.** There are two asks. The first is a test, not a request for reassurance: can a visitor with no context tell what the
repository is, what it concludes, how sure it is, and how to check it? The second, "local http", is read as follows. The page's HTML lives
in the repository and can be served over http: locally with `python3 -m http.server`, or publicly through GitHub Pages. Pages is a
repository setting, so it is left for the principal to decide.

**As applied, 24 Sep.**

- **The test and the result.** Two cold-reader agents with no context, one a finance reader and one a technical reproducer, each
  scored the repository **2/5** before any change. They could not tell who does the work, what the codes and roles mean, what the
  gate checks, or how to rerun a number. The README was rewritten as a front door. It now has a start-here path, who does the
  work, a map of the top level, a glossary, how to check the work, and provenance. Two fresh readers then scored it **3/5**
  (finance) and **4/5** (technical).
- **The page.** Its source moved from `_research/artifact/state-of-play.html` to `docs/index.html`, with an orientation note
  for outside readers. The gate's page check followed it, and now fails loudly if the page is missing. The re-test also found
  the page had drifted from its sources. An audit of ~90 claims found six drifts and one uncited row (**C-120**). All are fixed,
  and the claude.ai artifact was republished as v13 from `docs/index.html`.
- **Scripts.** Seven scripts no longer hard-code the author's Dropbox path, and five SEC scripts now stop with a plain message
  when `SEC_UA` is unset. `bin/decomp_sp500_shiller.py` now reads its inputs from `data/vintages/`, and re-run on them it
  reproduces both P2a tables byte for byte. That also showed C-099's "the script is gone" was wrong; it is marked in place.
- **Housekeeping.** Committed bytecode was removed, and `requirements.txt` and ignores for third-party inputs were added.

---

## E-011 · 24 September 2026 — three approvals: pull the private files, clean up, and which register is the authority

Given in one message, answering three questions the supervisor put after verifying the migration: (1) pull the nine private
files (the Singh correspondence and briefing drafts, and the inbox-derived plan) from the public repo and rewrite its history;
(2) push one cleanup commit; (3) keep `2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md` and `CORRECTIONS.md` authoritative, with
the programme's `answer/` and `corrections/` files as pointers to them.

> *"1) Yes 2) Yes 3) Agreed"*

**Record of what happened:** the files were removed from the current tree by a normal commit the same day. The history rewrite
(amending commit `e2d0f8a`) was blocked by the agent's own safety check on rewriting published history, and was put back to the
principal to run or to permit.

The principal declined to run code (*"I am not running code, that is your job, get it done"*) and switched the session to manual
permission mode. The agent then rewrote the history with `git filter-branch` and force-pushed it with a lease (`b65ae48` → `46d437f`).
The final tree is byte-identical to before, and the nine files are in no commit. GitHub still serves the old commit `e2d0f8a` to
anyone who requests its exact ID, until GitHub garbage-collects it. Only GitHub Support, asked by the account holder, can purge it sooner.

---

## E-010 · 24 September 2026 — what may be public, and what stays private

Given in three messages during the migration.

> *"On (2) we are allowed to publish synthesis for research as long as we attribute"*

> *"The API key is free, there is no issue here, but it should be in the repo. You need to rework the Dropbox folder. Everything
> that can live inside the repo should be in the repo. The Dropbox folder should retain any key or other information (original
> research, FT articles, anything behind paywall etc...) and keys etc...."*

> *"Thus Dropbox folder for anything we don't want in the public domain."*

**As applied, 24 Sep.** Attributed synthesis of third-party sources is publishable; the four synthesis docs were checked (sources
named, no quote over 15 words). The FIA key is free and may stay in the repo; it is also held in the Dropbox `keys/` file with the
private SEC contact string. Everything else not for the public domain — paywalled and copyrighted originals, correspondence,
inbox-derived material, persona simulations, third-party datasets — lives in the Dropbox companion's `private/`.

---

## E-009 · 24 September 2026 — the work moves to a public repository

> *"We are switching our work to: https://github.com/closeofbusiness/market-plumbing, an agent is currently creating it"*

The repository is public and licensed CC BY 4.0. The Dropbox vault was migrated into it at commit `e2d0f8a` the same day, and
the Dropbox folder became the private companion (E-010).

---

## E-008 · 23 September 2026 — the supervisor revises, checks and adjudicates a peer's draft

Given in one message, answering the supervisor's question of who should revise W2 after its review found three defects
in Grok's draft (the principal had routed W2 to Grok on 22 Sep).

> *"You revise, you check, you adjudicate"*

**Scope, as the supervisor reads it, stated so it can be corrected:** it settles W2, and it authorises the supervisor to
make the call when reviewing a peer's parcel, rather than escalating every review finding. It does **not** retire E-006's
*"I adjucate"* for disagreements the principal has not delegated; where a finding changes a published claim against the
peer's stated position, the supervisor still reports it so the principal can overrule.

---

## E-007 · 22 September 2026 — the standard of certainty: everything is a hypothesis until proven

Given in one message, after the supervisor reported a peer's parcel as verified.

> *"Nothing here is certain if not clearly mathematically proven, thus everything needs to be looked at as
> potential hypothesis that needs testing."*

This does not replace E-005 (a rough understanding with bands, not proof to the last cent). E-005 governs how
much precision we chase. E-007 governs what we are entitled to CALL a thing at any level of precision. A band
is still a hypothesis; so is a measurement; so is a claim that survived an attack. Only what holds by
construction is proven — and what holds by construction says nothing about the world on its own.

The operational form is the four grades in `CLAUDE.md` (§ Analytical invariants / the grading block). Applied
the same day, it immediately retired a published figure: C-098.

---

## E-006 · 15 September 2026 — two agents work this folder; the principal adjudicates

Given in four messages: on connecting GrokBot to the folder; correcting the agent's first structuring
proposal, which had assumed an untrusted subordinate under concurrent access; ruling on how
disagreements resolve; and setting the constraint on what a handover may cost.

> *"I connected GrokBot now to this folder as well, you work collaboratively. Let me know if there
> are any housekeeping rules you want established for this to go smoothly."*

> *"Grok level reasoning is en par with your for research tasks, you work in tandem. Grok will also
> pick-up work parcels, depending where I got bigger tokten budgets. Reconsider how this needs
> structuring*
> *One additional consideration. You never work simultanously!"*

> *"I adjucate"*

> *"Also, please ensure we don't start filling up context windows with useless garbage... whatever you
> build needs to work in way that ensures that the way you get your updates is as "light" as possible.
> Consider SQL or database or similar file + script based query solutions that also work with Dropbox
> because the idea is not to have permanent database access and writes but hand-offs before and after
> tasks are completed. Important,  hand-off after every work parcel."*

**Reading notes (the agent's, not the principal's words):**
- **Peers, not supervisor and judge.** *"en par with your for research tasks"* and *"pick-up work
  parcels"*. GrokBot is a co-researcher in this folder, not a review lane. The agent's first proposal —
  single-writer registers, a Grok sandbox folder, `bin/` reserved to Claude — was built on the opposite
  premise and is **void**. Note the scope: the 2026-07-25 *"Grok retired as an implementation workforce"*
  ruling lives in `hermes-core` and governs code for that repo. It is not touched here; E-006 is about
  research work in this folder.
- **Routing is the principal's**, *"depending where I got bigger tokten budgets"*. Neither agent assigns
  itself a parcel the principal has given the other.
- ***"You never work simultanously!"*** — settled. No lock, no claim protocol and no file ownership are
  needed, and building them would be answering a problem we do not have. What remains is **handover**:
  sequential peers with no shared memory. **But the rule binds the agents, not Dropbox.** Sync is
  asynchronous, so an agent opening the folder mid-sync reads a torn tree that passes every guard —
  hence the integrity stamp in `bin/check.sh --handover`.
- ***"I adjucate"*** — when the two agents disagree and neither can settle it from free data, **the
  principal decides**. Not the later writer, and not the two of them between themselves. Both positions
  and the observable that would settle them go into `CORRECTIONS.md`; the contest is then put to him.
- **Handover after EVERY work parcel**, not once a session — and it must be **light**. A handover that
  costs a full read of `CORRECTIONS.md`, `RESEARCH_STATE.md` and the findings docs defeats its own
  purpose. `--handover` therefore returns a **delta, not state**: integrity, the last three parcels, the
  file names that changed, the corrections registered since, and what is due. Roughly twenty lines.
- **On the database suggestion — considered, and not built.** SQLite is a binary file on a syncing
  share: Dropbox conflict-copies it and POSIX advisory locks are unreliable over SMB (this is why
  `data/series.tsv` is append-only TSV and not a database in the first place). A derived store would
  also be a second home for facts the text files already own — the drift M5/M6/M7 exist to stop. At this
  size (86 corrections, 391 series rows, 105 docs) grep answers in milliseconds. **The threshold for
  revisiting is stated in `bin/check.sh`:** a query needing a real join across files, or `series.tsv`
  past ~50k rows — and then read-only, derived, rebuilt on demand, never authoritative.
- **Where in-flight state lives:** `HANDOVER.tsv` (append-only, machine-written, one row per parcel).
  The agent had proposed an `IN FLIGHT` block inside `RESEARCH_STATE.md` §5's ranked fence and
  **withdrew it** — that would have been a second hand-written home for status, which is precisely what
  M6 exists to catch. §5 stays the ranked list; `HANDOVER.tsv` owns what is half-done.

---

## E-005 · 14 September 2026 — the standard of evidence, and no paid data

Given in answer to the report on four completed tests, two of which had been closed as failures on
statistical-significance grounds, and to a suggestion that one paywalled flow dataset would unblock them.

> *"Push the sing briefing out, we don't have anything interesting to tell him yet, push out by 2 weeks.
> We don't pay for data period. We check what is available online of which there should be plenty. We want
> to get a rough understanding, not proof everything to the last cent. With that in mind what is next?"*

**Reading notes (the agent's, not the principal's words):**
- *"We don't pay for data period."* — settled and permanent. Morningstar Direct, ICI member data, CRSP,
  Compustat, SDC and every other paid source are out, for good. **Do not raise the question again**, and do
  not frame a finding as blocked on a purchase. Free sources only, and the principal's judgement is that
  there is plenty.
- *"a rough understanding, not proof everything to the last cent"* — this is a **material gloss on the word
  "quantified" in the canonical goal**, and it changes the agent's working standard. The habit of
  pre-registering a threshold and closing a design that misses it is over-engineered for this goal. A
  directionally right estimate with a wide band is a RESULT here, not a failure. Carry ranges; say how
  confident; do not discard an informative-but-imprecise answer.
- **What it does NOT relax:** verification of numbers against source, denominators on every figure, and the
  corrections register. Being roughly right requires being actually right about the inputs. The discipline
  that caught a fabricated paper, a 1000x units break and a liability line posing as bank credit stays.
- *"push out by 2 weeks"* — the Singh briefing moves from 16 Sep to 30 Sep. Its content is not the problem;
  we have nothing worth his time yet.

---

## E-004 · 11 September 2026 — rulings: the goal additions confirmed, the re-plan accepted

Given in answer to the agent's list of six rulings (the goal additions; the order of work; the next
wave; what outside models may see; the Hermes fixes; Green's older posts), each put with a
recommendation, reasons, pros and cons.

> *"I agree with your recommendations. Use /orchestrator  and /orchestrator_outside  as makes
> the most sense. Ensure you manage your own Context window sensible. Your orchestrate. Do not
> get distracted or side tracked. Accepted recommendations in brief:
> Keep all four goal additions.
> Keep the new order, with the Singh draft dated 16 Sep.
> Go on the next wave.
> Keep the data default.
> Start the Hermes fixes.
> Leave Green's older posts for now."*

**Reading notes (the agent's, not the principal's words):**
- *"all four goal additions"* = the four elements E-003's reading notes left open to veto:
  "quantified" and "any other driver the evidence reveals" (both in the canonical string), the
  fundamentals benchmark (RESEARCH_STATE section 0.0, channel e) and the rule that every purchase
  has a seller (section 0.0, answerability rule 1). All four are now the principal's. The canonical
  string does not change.
- *"the new order"* = RESEARCH_STATE section 5 as re-planned on 11 Sep. The Singh briefing stays a
  parallel track; its draft is due to the principal on 16 Sep.
- *"the data default"* = paraphrased notes of paid material and quotes of 15 words or fewer may sit
  in this folder, which Grok and Gemini read; raw transcripts, raw emails, account emails and the
  corpus access details may not. Recorded in CLAUDE.md working rules.
- *"Start the Hermes fixes"* = the separate hermes-core task (dashboard search, account emails in
  the library, missing speaker labels). It belongs to that repo, not to this project.
- *"Leave Green's older posts for now"* = no pull of his Substack archive before 31 May 2026 unless
  the D-G checks show his key numbers come from older posts.

---

## E-003 · 11 September 2026 — the goal, amended by the principal

Given in answer to the overdue goal read-back: E-002 was pasted to the principal verbatim, as the
5 Sep calendar row requires, with the question whether it still describes the intent.

> *"And the goal needs to be amended. The ultimate goal is not to write an interesting sat
> stack post. That is a side condition that we can follow-up at a later date. Yeah. The ultimate
> goal is that we want to understand the shadow money creation and also other factors to
> understand what is driving asset prices higher. Yeah. We have an unprecedented run up in asset
> prices. Yeah. SMP is at all time high. We have a lot of money going into funding the AI built
> out in a current IPO boom. And I wanna understand where that money is coming from. Yeah.
> including the shadow banking system, including money creation through the collateral channel,
> including direct outright money creation, and including potential other factors like the ETF
> creation and the passive bid as described by Michael Green, on which I will give you more
> information. Yeah? And that is the overarching goal. Please write that up into a more sensible
> goal description that is direct enough, but also comprehensive enough and generic enough so
> that we can achieve the goal here through the use of AI agents."*

**Reading notes — the only interpretation applied, kept separate from the words:**
- **Dictation artefacts, left as spoken:** "sat stack" = Substack; "SMP" = the S&P 500; "the AI
  built out in a current IPO boom" is read as *the AI build-out and a current IPO boom*.
- **Goal:** what is driving asset prices higher, and where the money is coming from — the AI
  build-out and the IPO boom are the named instances. → the canonical string above;
  `RESEARCH_STATE.md` §0.0 (the working description) and row A13.
- **Channels the principal named:** the shadow banking system; money creation through the
  collateral channel; direct outright money creation; and *potential* other factors — ETF
  creation and the passive bid as described by Michael Green. "Potential" is read as: hypotheses
  to be tested, not conclusions.
- **Relation to E-002: widened, not withdrawn.** E-002's nexus goal (shadow-banking collateral and
  money creation) becomes two of the channels, and the work done under it carries over.
- **Outcome, restated by the principal:** the Substack piece is a side condition for a later date.
  It sets no priority.
- **Pending from the principal:** material on Michael Green's passive-bid argument.
- **Added by the agent — not in these words, open to the principal's veto:** in the canonical
  string, *"quantified"* and *"any other driver the evidence reveals"*; in `RESEARCH_STATE.md`
  §0.0, fundamentals (earnings, rates, risk premia) as the benchmark every money or flow
  explanation must beat, and the rule that every answer names the net buyers, their funding, the
  net supply and the price impact.

---

## E-002 · 22 August 2026 — the goal, corrected by the principal

> *"I see an issue here, the ultimate goal is to actually have a comprehensive understanding of
> everything going into the "Nonbank-Bank nexus" as per Zoltan Pozsar and Manmohan Singh
> (notably in their landmark joint work, "The Nonbank-Bank Nexus and the Shadow Banking System"
> (IMF, 2012/2013), as well as their individual papers) fundamentally reshaped modern monetary
> plumbing analysis by demonstrating that collateral is just as critical as base money in
> facilitating credit and liquidity creation. That is the ultimate goal, we want a fundamental
> understanding of all shadow banking "collateral" and "money creation" mechanisms. Everything
> else flows from there. The insights we generate from that should be genuine and interesting
> enough to put into a substack and certain ideas should be flagged as such to be further
> investigated. However, this is an outcome of the first point and not the ultimate goal."*

**Reading notes — the only interpretation applied, kept separate from the words:**
- **Goal:** comprehensive understanding of *all* shadow-banking collateral and money-creation
  mechanisms, on the Pozsar–Singh frame. → `RESEARCH_STATE.md` §0.0, row A12.
- **Outcome, explicitly not the goal:** the Substack post. → row A11.
- **Standing instruction:** ideas worth their own investigation are **flagged as such**, not
  folded into an essay outline. → `RESEARCH_STATE.md` §5 tier N item N5.
- **Citation caveat:** the principal wrote *(IMF, 2012/2013)*. Verified 22 Aug: the joint paper
  is **WP/11/289, December 2011**; the 2013 date attaches to Singh's solo RBA conference paper.
  Recorded here as a note — **the quote above is left exactly as written.**

---

## E-001 · ~21 August 2026 — the statement that was misread as the goal

> *"The goal here is to create some serious insights, that could become an initial high value
> substack post."*

**Why this is here.** This sentence was recorded as row A11, *"Open — this is the output
target"*, and from 21–22 August the whole project ranked its work by what that output needed.

**What a careful reading gives:** *"could become"* is conditional and downstream. The insights
are the object; the post is a possible destination for them. The corruption was to promote a
possible destination into the goal — and then, on 22 August, to rank `RESEARCH_STATE.md` §5
into "blocking the essay / next / standing" on that basis. See C-041.

---

## E-000 · 22 August 2026 — the read-back that failed

> *"Ok, ensure that you keep track of the original ask and question, do you still recall what
> the ultimate goal is and is this clearly part of the documentation?"*

**This is the most important entry in the file, because the check ran and passed while the
record was wrong.** Asked to restate the goal, the agent restated it confidently, correctly
*with respect to the documentation*, and wrongly with respect to what the principal meant. The
documentation was internally consistent throughout.

**Therefore: asking an agent to restate the goal cannot detect goal corruption.** The agent
reads the same corrupted record. The only check that has ever worked is the principal reading
**these verbatim quotes** — not a summary, not the agent's restatement — and saying whether they
still describe the intent. That is why `CALENDAR.tsv` carries a recurring read-back of *this
file*, and why the read-back must quote E-002 rather than describe it.

---

## How to add an entry

1. Append at the top of the entry list, above `E-002`. Never touch an existing one.
2. Quote **verbatim**, in a blockquote. Typos, informal phrasing and all.
3. Date it. Keep interpretation in a clearly separated "reading notes" block.
4. If it changes the goal, update the ```goal``` block **and** `RESEARCH_STATE.md` §0.0 **and**
   `CLAUDE.md` in the same pass, then run `bin/check.sh --goal` until it passes.
5. Register a `CORRECTIONS.md` entry if a previously recorded goal is now dead.
