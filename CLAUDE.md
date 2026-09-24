# Third Derivative & Shadow Debt — one project

> ## FIRST ACTION OF EVERY SESSION, BEFORE READING ANYTHING ELSE
>
> ```bash
> bin/check.sh --handover      # FIRST: integrity + what changed since the last parcel (~20 lines)
> bin/check.sh --goal
> bin/check.sh --latest        # newest ~5 corrections (was: head -40, always showed C-001..003)
> bin/check.sh --todo          # ranked open items (a query over RESEARCH_STATE §5), next 45 days, latest data vintages
> ```
>
> **These four commands are the whole entry path. They are queries, not documents** — together
> about sixty lines. Do not open `CORRECTIONS.md`, `RESEARCH_STATE.md` or the findings docs to
> find out where things stand; open a document only when you are about to work on what it covers.
> `--handover` prints what is overdue, so the old standalone CALENDAR awk line is gone.
>
> ## WHERE THINGS LIVE — from 24 Sep 2026 (`THE_ASK.md` E-009 to E-011)
>
> - **This repository is the research record**: public and CC BY 4.0, at https://github.com/closeofbusiness/market-plumbing.
>   Everything that can be public lives here, and it is authoritative.
> - **Anything not for the public domain lives in the private Dropbox companion**,
>   `~/Dropbox/31 - Claude Cowork/Work/2026.08 - Third Derivative Research/`. That holds `keys/secrets.env` (`SEC_UA`, `FIA_KEY`;
>   load with `set -a; source …; set +a`) and `private/`, kept at original repo-relative paths, where `private/MANIFEST.tsv` gives each
>   file's reason (paywalled originals, correspondence, inbox-derived, personas, third-party data, files too big for git).
> - **Before committing anything, ask whether it could be public.** Never commit personal data (scripts read the SEC contact string from
>   `SEC_UA`), paywalled or copyrighted full text, correspondence, or simulations of named real people. Attributed synthesis is fine (E-010).
> - **Commit only as the GitHub noreply identity, never a personal email.** This machine's default git email is personal, so set
>   `user.email` in every clone.
>
> ## TWO AGENTS WORK THIS FOLDER — Claude and GrokBot (`THE_ASK.md` E-006, 15 Sep 2026)
>
> **Peers on research, never simultaneous, routed by the principal** according to which token
> budget he has. There is no version control and no lock here; correctness comes from the
> handover, not from arbitration.
>
> - **Hand over after EVERY work parcel, not once a session.** On the way out:
>   `bin/check.sh --handover write <claude|grok> <parcel> <done|paused|blocked> <the next concrete step>`.
>   That one command is the whole protocol — it appends a row to `HANDOVER.tsv` and stamps the tree.
>   **Put the next-step text in SINGLE quotes.** Inside double quotes a money figure like `$1,453.8bn` expands
>   `$1` — on 18 Sep that injected a 25-line script into the log as 25 malformed rows. The command now strips
>   newlines and tabs and `--handover` flags any malformed line, but single quotes are the actual fix.
>   **When you rewrite a ranked item, rewrite only that item.** On 18 Sep a rewrite of item 8 consumed item 7
>   beneath it, silently deleting a HOLD with a live trigger. Check the item count before and after.
> - **`--handover` on the way in, before reading anything.** If integrity MISMATCHES, **stop**:
>   either Dropbox has not finished syncing or the last agent edited after stamping. The principal
>   never runs the two of you at once, but *Dropbox does not know that* — a tree half-synced over SMB
>   passes every other guard in `check.sh`, because each file is individually valid and only the set
>   is wrong. That is this project's signature failure: internally consistent and untrue (E-000, C-081).
> - **Re-derive one load-bearing number from source when you pick up another agent's thread.** One,
>   not all. C-081 stood for two days because an agent inherited its own summary of a row instead of
>   re-reading the row.
> - **When the two of you disagree, the principal adjudicates (E-006).** Write both positions into
>   `CORRECTIONS.md` with the observable that would settle them, and put it to him. Not the later
>   writer, and not the two of you between yourselves.
> - **Amended by E-008 (23 Sep):** when the supervisor *reviews a peer's parcel*, the supervisor revises, checks and
>   adjudicates — the principal's words were *"You revise, you check, you adjudicate"*. A finding that changes a
>   published claim against the peer's stated position is still reported to him, so he can overrule. Scope: `THE_ASK.md` E-008.
> - **Blind review on request, in both directions.** The reviewer reads the finding and the data,
>   **not** the author's `_research/` working notes. C-081 and C-082 — the two corrections that most
>   changed what this project believes — were both caught that way, and continuous folder access is
>   exactly what would quietly destroy it.
> - **Either agent may change `bin/`; neither should be the only one who ever tested it.** Announce a
>   gate change in the handover row, and the next agent verifies the new guard *fails* against the
>   pre-change tree. A guard that passes on the broken tree is worthless.
> - **Everything in the working rules binds both agents** — never pay for data (E-005); the SEC
>   User-Agent carrying the principal's address goes to **sec.gov hosts only**; never use an API key
>   found in page source; never defeat bot-detection; paid sources paraphrase-only with quotes of 15
>   words or fewer; FERC claims come from the PDFs on disk, never eLibrary lookups (C-048).
>
> **No database, deliberately.** SQLite was considered and rejected: a binary file on a syncing SMB
> share that Dropbox conflict-copies and whose locks are unreliable, and a derived second home for
> facts the text files already own. Revisit only if a query needs a real join across files or
> `data/series.tsv` passes ~50k rows — then read-only, derived, rebuilt on demand, never authoritative.
> The reasoning is in `bin/check.sh` above `handover_fields()`.
>
> **Numbers are data, not prose — since 23 Aug 2026.** Every load-bearing series is re-pulled from
> its *issuing* source by `bin/pull_series.py` (FiscalData, OFR MMF API, FDIC API, SEC XBRL, FRED
> mirrors) and appended with a `pulled_at` vintage to **`data/series.tsv`** (append-only, never
> rewritten — SMB mount, no SQLite). Full histories are cached in `data/history/*.csv`
> (disposable). A figure quoted in a findings document must exist as a row there; if it does not,
> the document is the only copy and it will vanish into the next rewrite. Before using any number
> older than a quarter, re-run the script and compare vintages. The pull code lives in the repo
> because it used to live only in a session transcript — which is the failure this paragraph exists
> to prevent.
>
> **The first command prints the goal.** It is first because on 22 August 2026 this project
> spent a day serving the wrong one while every document agreed with every other document —
> the goal was never *lost*, it was *wrong*, and the old gate never printed it at all. Reading
> the goal is now an action you take, not a thing you remember. If it fails, **stop and fix it
> before any research work**: a corrupted goal makes every downstream priority wrong while
> looking entirely reasonable.
>
> **You cannot validate the goal by recalling it.** On 22 Aug the principal asked the agent to
> restate the goal; it did so confidently, correctly *against the documentation*, and wrongly.
> The record is `THE_ASK.md` — the principal's own words, append-only, never paraphrased. If
> anything you are about to write restates the goal, derive it from there and cite the entry.
>
> Then read **`RESEARCH_STATE.md`** — **large; it exceeds the Read tool's single-call cap, so a whole-file read is silently truncated mid-§5.** Start from `bin/check.sh --todo`, then read the section you need by offset. **§0 is what was *asked*** — the lineage of
> every request and its status, so you can tell core work from a tangent. §1 is the animating
> question. §2–§5 are what we currently *believe*, as opposed to what we have *written*:
> settled, contested, load-bearing assumptions, and open questions.
>
> The first command prints claims that are **dead** — never restate one. The second prints
> dated obligations that have **come due** — resolve them before starting new work.
>
> **The bar is a rough understanding, not proof to the last cent** — the principal's ruling of
> 14 Sep 2026, `THE_ASK.md` entry **E-005**, and it changes how you work rather than what you know.
> A directionally right estimate with a wide band is a RESULT. Do not close a line of work because
> it misses a significance threshold; report the estimate, the band and your confidence. **We never
> pay for data** — settled, permanent, do not raise it. What this does NOT relax: verifying numbers
> against source, denominators on every figure, and the corrections register.
>
> **COMPUTE THE MINIMUM DETECTABLE EFFECT BEFORE COMMISSIONING A DESIGN, NOT AFTER (C-090, C-091).**
> State the effect size the hypothesis predicts, the noise it sits in, and the n required to see it at
> t=2 — *in the brief*, before any data is pulled. A pre-registered kill switch on an underpowered design
> is not a test: it fires whether the effect is real or absent, and the null it produces is uninformative.
> B6 cost a parcel this way, and its follow-up scout cost a second, because the check was skipped twice.
> The screening arithmetic is cheap: daily equity return noise is **~111bp**, so any design whose effect is
> a few bp on daily data needs decades-to-centuries of observations and is dead on a free decade of prices.
> This binds both agents and applies to outside parcels too.
>
> **AND COMPUTE THE MDE FROM A REALISED CLUSTERED STANDARD ERROR, NOT FROM σ/√N (C-092).** For any panel
> whose treatment is a period-level shock interacted with a cross-sectional characteristic, precision is
> governed by the number of **shock periods**, not the number of rows. The JVZ gate cleared at 0.451pp on
> 3,936 firm-quarters; the realised two-way-clustered SE gave 1.622pp — effective n was **304, not 3,936**,
> and a third uninformative null was produced and briefly written up as a refutation. **An effective n that
> is declared rather than demonstrated is not a gate.** Demonstrate it: run the specification once on
> randomised placebo treatment, take the clustered SE that comes back, and use 2·SE as the MDE.
>
> **EVERY CLAIM CARRIES A GRADE, AND ONLY ONE GRADE MEANS CERTAIN (E-007, 22 Sep).** *"Nothing here is certain if
> not clearly mathematically proven, thus everything needs to be looked at as potential hypothesis that needs
> testing."* Four grades, and the grade goes next to the number wherever the number is stated:
>
> * **IDENTITY** — true by construction given its inputs. **An identity that sums exactly is not evidence and cannot
>   fail.** It carries no information about the world by itself, and it launders the quality of its inputs.
> * **MEASURED** — observed on a **stated universe with a stated denominator**. Contingent on source, tag choices and
>   coverage. Can be wrong, and has been.
> * **BOUNDED** — only a ceiling or only a floor exists. **Never quote a bound in the register of an estimate** (C-096).
> * **HYPOTHESIS** — untested, or tested and survived. **Survival raises credence and establishes nothing.**
>
> **The residual rule, which is where this bites hardest (C-098).** In any identity `A = B + C + D` where one term
> is obtained as `A − B − C`, that term is **not a measurement** — it is definitionally whatever the others leave
> over, and **every error in every other term lands entirely inside it**. So the residual is the *least* secure
> number in the table, never the most. Where an independent measurement of that term is available, compute it and
> **report the gap**: the gap is a real quantity and it is the only part of the exercise that can be falsified.
> W3 reported `Δlog(pre-tax) = 0.7875` as a finding; the panel's own sums give **0.8603**, a **0.073 log (7.6%)** gap
> that the identity had absorbed silently.
>
> **Not every residual is dangerous, and residual-ness is not the variable (C-107, C-109, 22 Sep).** A solved-for term is
> a hidden-error risk **only where a second, independent measurement route exists that could disagree**. Z.1's "issuance net
> of ETF" has no such route — every component is measured — so its risk is **attribution** (it is not the operating-company
> number it was quoted as), not hidden error. And a gap between two series is not a defect until every term of the identity is in it: the household and
> Rest-of-World equity "reconciliation gaps" ($318bn, $322bn) that C-109 called structural disagreement were the
> other-volume-changes term the check left out (C-119). **In Z.1, change in level = flow + revaluation + other volume
> changes (FV); a check that omits FV finds gaps of hundreds of billions that are not errors.** Ask what could disagree
> with this number, not whether it was subtracted — and before calling a disagreement real, make sure the identity is complete.
>
> **Ban patterns catch phrasings. They do not catch methods (C-103, C-105).** C-078 killed a level/counterfactual claim, the
> gate went green every day after — and the identical method on CAPE earnings sat twelve lines below in the same file,
> unstruck, describing itself as "an even stronger verdict" than the number that was already dead. **When a claim is killed
> for a reason, grep the file for other applications of the REASON, not other instances of the wording.**
> **And the ban scan does not see `_research/` or `CALENDAR.tsv` at all** (`check.sh` line 306, by design). A killed ratio
> survived in `_research/` until a Python sweep found it (C-116, d4). When killing a claim, sweep the whole vault in Python.
>
> Mixing bases is what fills residuals. Before writing an identity, check that **every term is on the same universe**
> — same constituents, same window, same per-share basis. W3's three terms came from Shiller index EPS, a 412-firm
> survivor panel and a constituent-level share count. That is three universes in one equation.
>
> **The gate's own assumptions are claims too (C-113, 22 Sep).** Six code paths in `check.sh` matched `C-0[0-9]+`, so the
> moment C-100 was registered, M7, M8, `--latest` and the integrity stamp's count and max all went blind to every new
> correction — and every one of them kept printing ✓. It was caught by a stamp that looked wrong, not by a guard.
> **A threshold crossing cannot be caught by testing the current state.** When a counter nears a width boundary (C-999,
> E-010, a two-digit year), grep the tooling for the width first.
>
> Before shipping any document, run `bin/check.sh --all`. **Read its ✓ and ⚠ lines — never its exit code.** The
> script exits 0 *always*, by design, so `$?` is meaningless as evidence and so is the absence of a ✗: on 18 Sep a
> run reported as green carried a live killed-claim hit that only surfaced when the ✓ lines were printed. The pass
> condition is five ✓ guard lines **and** `✓ no killed claims found` **and** `✓ page clean` — a positive signal, not silence.
>
> **The published page ("What Holds the Market Up", claude.ai artifact) is a dated rendering OUTSIDE the gate.**
> `check.sh --all` never sees it, and it carried C-083's retracted "irreducibly unattributable" for four days before
> anyone looked. **It went stale a second time on 23 Sep:** three claims killed on 22–23 Sep stayed live because a
> pre-publish check only covers claims already dead at publish time — nothing re-scanned the page after a new kill.
> **Its source now lives at `_research/artifact/state-of-play.html`. Publish FROM that file**, and `check.sh --all` scans
> it on every run (the `page check` line). For a one-off, use `bin/check_page.py <html>`, not `bin/check.sh <html>`: the
> raw scan caught 2 of the 3 dead claims and missed C-116, whose phrase an HTML tag split. The answer document is the
> authority; the page must say so and must not be used as a source.
>
> **The housekeeping skill's link checker reports ~211 "unreachable" docs here. Ignore that half.** It looks
> for relative markdown links; this project navigates by the **read table below**, which lists filenames in
> backticks, not as links. `check.sh`'s M5 orphan guard is the authority and it enforces exactly that. The
> checker's other half — BROKEN LINKS — is real and should be none.
>
> **NEVER CITE A SESSION SCRATCHPAD PATH AS A DELIVERABLE. It has already been swept.** Checked 21 Sep:
> of 35 distinct `/private/tmp/claude-501/...` paths cited across vault documents, **33 no longer existed**,
> including deliverables named in P1, P2a, P2c, ATT0, F1, I1b, Oracle and N2c. Those thirteen docs survive
> because they *also* cite a durable path under `_research/`, `data/` or `bin/` — that second citation is the
> only reason the work is still reproducible. When a pass produces a table, a script or a CSV, land it in the
> vault and cite THAT. Re-check with **`python3 bin/check_scratchpad_refs.py`**, which names every affected
> document and whether it still has a durable copy. (The first inline one-liner written for this note
> over-reported by two — its pattern swallowed trailing punctuation. Tested, then replaced by the script.)
>
> **Reconstruct state by querying, never by recalling.** Every fact that changes —
> statuses, counts, what is open, what is due — lives in exactly one place and is read by
> running the commands above. This file carries *narrative and standing rulings only*; if
> you find a status or a count written here, it is a bug, not a source.
>
> **Landing a research pass includes registering it**, in four places, or the mechanisms
> above cannot see it: any *do-not-say* finding → `CORRECTIONS.md` (C-040); any dated
> obligation it surfaces → `CALENDAR.tsv` (the 17 Aug miss); any new findings document →
> the read table below; **and any new open item → `RESEARCH_STATE.md` §5 with the goal row it
> serves named** (C-041 — an item that cannot name one is a tangent, which is allowed, but must
> be labelled so it never silently outranks the goal).
>
> *Both exist because this project has already failed at exactly these two points: a
> 17 August trigger passed unwatched, and a refuted figure kept standing in two documents
> after the refutation was written down. Detection was never the problem. Propagation is.*

---

## The goal — and the difference between the goal and its output

**Amended 11 Sep 2026 by the principal (`THE_ASK.md` E-003): widened from the nonbank–bank nexus
to what drives asset prices and where the money comes from. Before that it was corrected on 22 Aug
(C-041), when this section wrongly named the essay as the goal.**

### The ultimate goal

> A fundamental, quantified understanding of what is driving asset prices higher and where the money is coming from — including the funding of the AI build-out and the IPO boom — across every channel: direct money creation, shadow banking and shadow money creation, the collateral channel, market-structure flows such as the passive bid and ETF creation, and any other driver the evidence reveals.

*Canonical string, verbatim from `THE_ASK.md`. `bin/check.sh --goal` fails if it drifts here,
there, or in `RESEARCH_STATE.md`. Do not reword it — not even to improve it.*

**The working description is `RESEARCH_STATE.md` §0.0 — read it, do not restate it here:** what is
being explained (asset prices; the AI build-out's funding; the IPO boom), the six candidate
drivers, the rules that make it answerable, and what done looks like. The Pozsar–Singh frame
(collateral is as critical as base money; IMF WP/11/289, December 2011) now governs channels
(b) and (c).

Everything else in this project flows from that. **Nothing is a tangent because it fails to
serve the essay; it is a tangent only if it fails to serve the goal.**

### The output, which is downstream

Insights good enough for **a Substack piece** — a side condition for a later date (E-003) — plus a standing flag on ideas
worth further investigation. This is an *outcome* of the understanding, **not the goal**, and
it does not get to set the research priority order. An agent that de-prioritises a mechanism
because it will not fit the essay has inverted the dependency.

### What binds every contributor either way

Every load-bearing number must be independently checkable by a hostile reader, and every claim
must survive a competent economist's first objection. A finding that only works if the reader
is friendly does not ship. This applies to every channel.

### The two legs of the nexus, and where we stand on each

The 2011 paper's mechanism has two legs, and **the nexus is that the same entities sit on both
of them** — asset managers are simultaneously the dominant source of demand for *non-M2 money*
and the source collateral **"mines"** from which banks fund themselves via re-use of pledged
collateral. Two mechanisms in most treatments; one interlock in theirs.

- **The collateral leg** — covered, and the finding is largely *negative*: reuse intensity is
  flat, the multiplier is down ~36% from its 2023 peak, and this is a permissive condition
  rather than a proximate source. See `Shadow_Debt_Channel_Map.md` (repo channel) and
  `2026-08-21-Singh-And-The-Two-Circuits.md`.
- **The money leg** — **not covered.** `2026-08-21-Safe-Asset-Share-Reexamined.md:179` states it
  outright: institutional cash pools, *"the actual marginal demanders in the Pozsar account,
  were not measured by anyone here."*
- **The interlock itself** — **not covered, and not currently visible in the structure.** The
  channel map is nine silos each asked *"is it money creation?"*; the place where the interlock
  actually surfaces is each channel's **"Double-counting risk"** section, where it is treated as
  a measurement nuisance to be netted out. Under Pozsar–Singh the interlock *is the phenomenon*.
  **Re-read those sections as findings, not as caveats.**

## The two workstreams

**A — Third derivative cascade analysis.** Where value accrues when a capacity overbuild
strands assets. Complete. Delivered: a nine-condition discriminating test, a 24-case
library, four investor-persona subagent primers, a pre-registered forward register, an HTML
report.

**B — The nonbank–bank nexus: shadow collateral and money creation.** *Renamed 22 Aug 2026
(C-041); it was "Shadow debt and the funding identity", scoped to a question that has since
been withdrawn.* **This is the workstream that carries the ultimate goal.** In progress.
Delivered: a first-principles funding-identity decomposition across nine economic traditions,
a nine-channel shadow-credit map, a measurement handbook with a build order, and a collateral-
reuse reconstruction.

> **A live instance of a dead framing was standing in this very file until 22 Aug.** The old
> wording — *"how a boom is funded when the household saving rate is falling"* — is the C-030
> framing, withdrawn on 22 August. `bin/check.sh` did not catch it: the C-030 pattern matches
> "funded **while** … saving rate" and the sentence said "funded **when**". One conjunction.
> The regex has been widened. **Assume the ban list has more holes of exactly this shape.**

**The join.** Workstream A's condition C1 — *forced recognition of loss plus transferable
operating control* — is an asset-level test. Workstream B measures whether the system can
execute that test at all. Both independently concluded the binding constraint is the same:
the loss sits with holders under no compulsion to mark it, and the transfer machinery is
balance-sheet constrained anyway. Read `Where_The_Two_Workstreams_Meet.md`.

> Naming note: the original brief said "Ken Griffith"; the subject is Kenneth C. Griffin.

---

## Agent initialisation — read by role, not by appetite

The corpus is roughly 4× a context window. An agent that reads everything wastes its budget;
an agent that reads nothing re-derives settled findings. Read **your role's column only**.

**The two nexus source documents are `always` for every role.** `2026-08-22-Nexus-WP11289-Read.md`
carries the mechanism read at source — reverse maturity transformation, the
asset-manager-to-bank claim, the `z_k` decomposition — plus the working IMF retrieval route
and the adjudication of the Gemini return. Read it before `Nexus-Primary-Sources.md`, whose
"framework from abstracts" caveat it supersedes.

**`2026-08-22-Nexus-Primary-Sources.md` is `always` for every role** despite being new and
small: it is the only document that reads the goal's primary sources rather than citing them,
and it carries the retrieval routes (which hosts serve PDFs and which 403), Pozsar's
inclusion test, and the net-vs-gross rule (C-042). Reading it costs 3k and prevents a repeat of
the improvised-channel problem. The extracted source text sits in
`_research/primary_sources/*.txt` — grep it, never read it whole.

| File | ~tok | Investigator | Verifier | Synthesist |
|---|---:|:---:|:---:|:---:|
| **`THE_ASK.md`** | **1k** | **always** | **always** | **always** |
| **`README.md`** | 1k | public front page — how to read the repo; points at the authorities | — | ✓ |
| **`CHARTER.md`** | 2k | public charter — the question, markets in scope, rules. It quotes the goal; the goal's authority is `THE_ASK.md` | — | ✓ |
| `answer/` | — | POINTER to `2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md` (E-011) | — | — |
| `corrections/` | — | POINTER to `CORRECTIONS.md` (E-011) | — | — |
| `dossiers/` | 12 files | public per-channel summaries; each points at the findings doc that owns its numbers | — | ✓ |
| `monitor/` | 1 file | public extract of `data/series.tsv` and `CALENDAR.tsv`; those win where they differ | — | — |
| `data/series.tsv` · `bin/pull_series.py` | — | **query** | **query** | **query** |
| `data/vintages/` (FINRA, ALFRED snapshots) · `Report/*.html` (outputs) | — | if vintage | if vintage | if presenting |
| `CORRECTIONS.md` | **query only — never whole** (exceeds the Read cap; `bin/check.sh --latest` for the newest, `grep -n '^## C-0'` to locate one) | **always** | **always** | **always** |
| `CALENDAR.tsv` | **query only** (`bin/check.sh --handover` for overdue, `--todo` for the next 45 days) | **always** | **always** | **always** |
| `HANDOVER.tsv` | **query only** (`bin/check.sh --handover`) — machine-written, append-only, one row per work parcel; never hand-edit | **always** | **always** | **always** |
| **`RESEARCH_STATE.md`** | **by section — never whole** (exceeds the Read cap; `bin/check.sh --todo` first) | **always** | **always** | **always** |
| **`2026-08-22-Nexus-WP11289-Read.md`** | **4k** | **always** | **always** | **always** |
| **`2026-08-22-Parcel-A-Interlock-Return.md`** | 3k | ✓ | ✓ | ✓ |
| **`2026-08-22-Parcel-B-Numbers-Return.md`** | 3k | ✓ | **✓** | ✓ |
| **`2026-08-22-Parcel-C-FERC-Return.md`** | 3k | if RTO/FERC | ✓ | ✓ |
| **`2026-08-22-Parcel-D1-Scouting-Return.md`** | 3k | if D1 | ✓ | ✓ |
| **`2026-08-22-D1-Bill-Supply-vs-Shadow-Money.md`** | **3k** | **✓** | **✓** | **✓** |
| **`2026-08-22-D2-Who-Holds-The-AI-Paper.md`** | **3k** | **✓** | **✓** | **✓** |
| **`2026-08-23-FT-Harvest-ABCP-Conduits-And-Equity-Repo.md`** | 2k | ✓ | ✓ | ✓ |
| **`2026-08-23-D3-Cash-Pools-vs-Asset-Management-Structure.md`** | **6k** | **✓** | **✓** | **✓** |
| **`2026-08-23-Parcel-N3-Collateral-Return.md`** | **5k** | **✓ (collateral leg: CCP IM, FICC sponsored, Singh Table 2, re-use negatives)** | ✓ | ✓ |
| **`2026-08-23-Parcel-D8-Clearing-Return.md`** | **4k** | **✓ (Treasury clearing: the 2026 sponsored plateau answered; mandate dates; CME/ICE status; Actrix; GSD monthly)** | ✓ | ✓ |
| **`2026-08-24-Parcel-D8b-Conduit-Return.md`** | **3k** | **✓ (verified sponsor→programme map; MMF conduit census 31 Jul; AIR TRF route)** | ✓ | ✓ |
| **`2026-08-24-D9-Does-The-AI-Complex-Fund-Itself.md`** | **3k** | **✓ (hyperscaler cash pools' corporate-bond holdings; no issuer detail exists)** | ✓ | ✓ |
| **`2026-08-29-D6-Stablecoins-Fifth-Cash-Pool.md`** | **2k** | **✓ (the fifth pool is the issuer; engine 5 stalled in 2026; C-062 scorecard)** | ✓ | ✓ |
| **`2026-08-29-N2c-The-Funding-Closure.md`** | **3k** | **✓ BUT READ §7 FIRST — the N2cR review overturned most of its conclusions (C-063/064/065); table survives, causal narrative retracted** | ✓ | ✓ |
| **`2026-08-25-N3-Singhs-Denominator-Reconciled.md`** | **3k** | **✓ BUT READ §8 — our velocity measurement is mechanism-signed (C-061) and Singh's figure is recorded as a named conflicting measurement; the source base grew substantially** | ✓ | ✓ |
| **`2026-08-30-D10-Reuse-On-The-Measured-Chain.md`** | **3k** | **✓ (the dealer re-use measurement and its review; §6 = D10R review; C-066/067 strikes)** | ✓ | ✓ |
| **`2026-08-30-N2a-Offshore-Dollar-Leg.md`** | **3k** | **✓ (the offshore dollar leg measurement: BIS LBS deposits, the Cayman repo hole triangulation, and the FX-swap layer; §7 = N2aR review, C-069 strikes)** | ✓ | ✓ |
| **`2026-08-31-N2b-zk-The-Wholesale-Share.md`** | **4k** | **✓ READ §7 THEN §8 — §7 is the C-070 correction (v1 headline struck), §8 is the v2 perimeter test that settles the wholesale-share measurement on the widest perimeter, passed adversarial review, carried by N4 15 Sep** | ✓ | ✓ |
| **`2026-08-31-N3v4-Singh-Reconciliation.md`** | **3k** | **✓ if Singh/velocity — his Figure-3 US panel rebuilt from the 2017 filings; numerator confirmed as the PERMITTED line; §2b carries the vintage rule (C-071) and the C-072/073 strikes** | ✓ | ✓ |
| `2026-08-30-FERC-EL26-Informational-Reports.md` | 2k | if RTO/FERC or D9 demand-side | ✓ | ✓ |
| `2026-08-30-Singh-Ask.md` | — | **PRIVATE since 24 Sep (E-011)** — not in this repo; the Dropbox companion's `private/2026-08-30-Singh-Ask.md` | — | — |
| `_research/D8b_D8c_conduit_sponsor_evidence_2026-08-24.md` | 1k | if re-checking a conduit sponsor | — | — |
| **`2026-08-22-Nexus-Primary-Sources.md`** | **3k** | **always** | **always** | **always** |
| **`2026-09-11-Green-Substack-And-Ep61-Synthesis.md`** | 9k | if channel (d), D-G or F1 — the entry point on Green | ✓ | ✓ |
| **`2026-09-11-Who-Buys-Treasuries-Synthesis.md`** | 7k | if channel (a), (c) or the term premium | ✓ | ✓ |
| **`2026-09-11-P1-Equity-Net-Buyers.md`** | 4k | if P attribution or any channel's net-buyer role | ✓ | ✓ |
| **`2026-09-11-P3-Price-Impact-Multiplier.md`** | 4k | if pricing any flow (the M decision) | ✓ | ✓ |
| **`2026-09-18-EPS-Split.md`** | 4k | if P2a / earnings share / buybacks — EPS split: 69% profit / 13% accretion / 18% multiple of price | ✓ | ✓ |
| **`2026-09-22-W2-AI-Paper-Composition.md`** | 4k | **READ ITS ADJUDICATION BANNER FIRST** — if AI debt / who funds the build-out / bank money creation. Long money holds the bulk; money funds ~$4bn; bank C&I is industry exposure, ~$250bn of it pre-dating the boom (C-115). Grok drafted, supervisor adjudicated (E-008) | ✓ | ✓ |
| **`2026-09-21-W3-Tax-Decomposition.md`** | 4k | **READ ITS C-096 BANNER FIRST** — if earnings / tax act / W1 leak. ETR 27.4%→19.6%; tax 9.5% of EPS growth; restated claim 74.5%. Task 1 stands; Task 2's verdict is rescoped to a tighter ceiling, and its panel did not land (C-097) | ✓ | ✓ |
| **`2026-09-20-W1-The-Leak-Objection.md`** | 2k | if the leak / two-circuits / who sold — the ceiling is the $3,643.7bn seller-side flow, and the pension+insurance channel is $938.4bn (C-094) | ✓ | ✓ |
| `2026-09-18-EPS-Split-POINTER.md` | <1k | pointer only, no figures — read the EPS-Split doc and its C-093 banner | — | — |
| **`2026-09-11-P2a-Return-Decomposition.md`** | 4k | if the fundamentals benchmark (e) or P attribution | ✓ | ✓ |
| **`2026-09-11-DG-Green-Numbers-Checked.md`** | 5k | if channel (d), D-G or F1 | ✓ | ✓ |
| **`2026-09-15-DG-Remainder-Leveraged-ETF-Flows.md`** | 5k | if D-G / Green leveraged ETFs (G-008..G-014) | ✓ | ✓ |
| `2026-09-11-I1-IPO-Scout.md` | 4k | if I (the IPO boom) | ✓ | — |
| **`2026-09-12-F1-AI-Funding-Filings.md`** | 5k | if F (AI funding) or channel (d) supply | ✓ | ✓ |
| **`2026-09-12-P2b-Top10-Earnings-vs-Weight.md`** | 4k | if concentration, channel (d) vs (e) | ✓ | ✓ |
| **`2026-09-12-I1b-IPO-Prospectus-Facts.md`** | 4k | if I (the IPO boom) — supersedes the scout's 2026 figures | ✓ | ✓ |
| **`2026-09-12-ATT0-First-Attribution.md`** | 5k | **always, before sizing any channel against prices** | ✓ | ✓ |
| **`2026-09-12-P2c-Rates-vs-Risk-Premium.md`** | 4k | **always, with ATT0 — what holds valuations up** | ✓ | ✓ |
| **`2026-09-12-F1-Funding-Table.md`** | 5k | if F (AI funding) — the closure table | ✓ | ✓ |
| **`2026-09-12-Parcel-RET1-Retirement-Flows-Return.md`** | 6k | if retirement flows or the passive bid — READ THE HEADER FIRST: the net flows are not market flows | ✓ | ✓ |
| **`2026-09-13-B0-The-Bridge-Frame.md`** | 4k | **always, with P2c — the money-to-price question and the bound on it** | ✓ | ✓ |
| **`2026-09-13-S1-Supply-Decomposition.md`** | 5k | if supply, issuance, buybacks or the AI build-out — the record issuance is PRIVATE | ✓ | ✓ |
| **`2026-09-13-P5ii-Growth-Versus-Risk.md`** | 4k | **always, with P2c — whether the compression is risk or growth is UNRESOLVED** | ✓ | ✓ |
| **`2026-09-13-P5iii-Concentration-And-JVZ.md`** | 4k | if concentration, the passive bid or Green — the pattern is there, the flow link is not | ✓ | ✓ |
| **`2026-09-13-E2-Earnings-Quality-Useful-Lives.md`** | 3k | if earnings quality or the 70-80% finding — 5-12%, main finding survives | ✓ | ✓ |
| **`2026-09-14-P5iv-Third-Premium-Measure.md`** | 4k | **always, with P2c and P5ii — the third measure; its SPLIT is dead (C-082), the direction is not** | ✓ | ✓ |
| **`2026-09-14-E1-European-Pensions-Scout.md`** | 4k | if European pensions, the long end or duration demand — the transition is a RELABELLING | ✓ | ✓ |
| **`2026-09-14-P5i-Event-Study-Result.md`** | 4k | **always, with P5ii and P5iv — 2024 accrued as DRIFT, not on news** | ✓ | ✓ |
| **`2026-09-14-HR-The-Household-Residual.md`** | 3k | **always — the household line is a PLUG; read ETF1 then LIT1 (C-081/C-083/C-084)** | ✓ | ✓ |
| **`2026-09-15-ETF1-Identity-Net-Of-ETF.md`** | 4k | **always, with SYN — issuance identity net of ETF shares; bond ETFs are 30% of the wrapper** | ✓ | ✓ |
| **`2026-09-15-LIT1-Residual-Literature.md`** | 4k | **always, with HR — tax recoding is not an entity census of the plug (C-084)** | ✓ | ✓ |
| **`2026-09-15-N4-Scale-Timing-Bound.md`** | 4k | **always, with SYN — 2024 wholesale expansion was the RRP handoff; C-085** | ✓ | ✓ |
| **`2026-09-15-P4-Russell-Elasticity-Pilot.md`** | 4k | **always, with B0/P3 — free-data Russell RD first stage fails; C-086** | ✓ | ✓ |
| **`2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md`** | 3k | **ALWAYS — START HERE. The answer as it stands; restates no numbers, points at each findings doc** | **always** | **always** |
| `2026-09-14-SYN-What-We-Can-Say.md` | <1k | SUPERSEDED — a pointer plus the record of four corrections written against it (C-081/082/084/089) | — | — |
| **`2026-09-14-A1-Money-Creation-Link.md`** | 3k | if money creation, deposits or the Fed — tested, WEAK, and too small on the recent window | ✓ | ✓ |
| **`2026-09-14-F1r-AI-Funding-Remainder.md`** | 4k | if AI build-out financing — NVIDIA's tables reconcile; 4 of 6 firms name no vehicle | ✓ | ✓ |
| **`2026-09-14-I2-IPO-Allocation.md`** | 4k | if the IPO boom or forward supply — 77-93% of proceeds go to unnamed buyers; lockup schedule | ✓ | ✓ |
| **`Parcel_SYN1_Attack_The_Synthesis_For_Grok_Cursor.md`** | 2k | if running the adversarial check on the synthesis | ✓ | ✓ |
| `Parcel_QE_Sentiment_25Sep_DRAFT_For_Grok.md` | 2k | **FINAL (filename says DRAFT) — routed to Grok in Cursor, which has live X search. Two runs: 25 Sep and 1 Oct, same queries; calls pre-registered against the 30 Sep prints** | — | — |
| **`_research/SYN1_return_2026-09-15.md`** | 2k | if SYN — Grok hostile return: earnings ok-amended; money-side assembly fails | ✓ | ✓ |
| **`_research/2026-09-15-PFS-Scout-Corporate-Equity-Line.md`** | 2k | if 6b/C-084 — PFS scout: QHF equity YES; PE equity line NO | ✓ | ✓ |
| **`Parcel_LIT1_Residual_Literature_For_Gemini_DeepResearch.md`** | 2k | if running the household-residual literature map | ✓ | ✓ |
| **`_research/2026-09-13-B5-FirstStage-Spec.md`** | 3k | if running or reading the Tier B first stage — pre-registered, read before touching results | ✓ | ✓ |
| **`_research/2026-09-14-P5i-EventStudy-Frame.md`** | 3k | if running or reading the 2024 event study — pre-registered frame and decision rule | ✓ | ✓ |
| **`_research/2026-09-14-N4-Frame.md`** | 2k | historical — restated questions answered in N4 (C-085); read if reconstructing why the percentage form died | ✓ | ✓ |
| **`Parcel_BR1_Multiplier_Census_For_Gemini_DeepResearch.md`** | 2k | if running the Tier B literature census | ✓ | ✓ |
| **`Parcel_BR2_Cross_The_Bridge_For_Grok_Cursor.md`** | 2k | if running the Tier B design challenge | ✓ | ✓ |
| **`_research/BR2_return_2026-09-15.md`** | 3k | if Tier B / BR2 — Grok return: payment-day IV; aggregate M subset only | ✓ | ✓ |
| **`2026-09-15-B6-Phase1-Payment-Day-Mechanism.md`** | 4k | if B6 — Phase 1 FAILS kill switch; mechanism absent on free calendar-true dates | ✓ | ✓ |
| **`_research/2026-09-16-NYSE-Payment-Date-Scout.md`** | 3k | if B6/Tier B — free NYSE pay-date scout VERIFIED NO | ✓ | ✓ |
| **`_research/2026-09-16-JVZ-MDE-Gate.md`** | 3k | if 6c/Tier B — Stage A CLEARS GATE (within-Q design); dead n≈42 fails | ✓ | ✓ |
| **`_research/2026-09-16-JVZ-StageB-Mechanism.md`** | 3k | if 6c/Tier B — Stage B INCONCLUSIVE free test; within-Q gate passed | ✓ | ✓ |
| **`_research/2026-09-16-JVZ-StageB-Sharpen.md`** | 3k | if 6c/Tier B — **UNINFORMATIVE, not a rejection (C-092)**: realised MDE 1.09pp vs predicted 0.53pp | ✓ | ✓ |
| **`_research/2026-09-16-JVZ-Gate-Rerun.md`** | 3k | if 6c — corrected placebo MDE gate FAIL (0.48× / 0.90×); no real-flow run | ✓ | ✓ |
| **`_research/2026-09-16-JVZ-Gate-Rerun-Spec.md`** | 2k | if 6c — C-092 corrected gate brief (200 placebos; no σ/√N) | ✓ | ✓ |
| **`2026-09-16-TierB-E005-Resolution-Limit.md`** | 4k | if Tier B / bridge / M — E-005 PERMANENTLY CLOSED (gate FAIL; JVZ underpower not rejection) | ✓ | ✓ |
| **`_research/2026-09-16-JVZ-MDE-Gate-Spec.md`** | 2k | if 6c — Stage A-only brief; MDE before measurement | ✓ | ✓ |
| **`2026-09-12-N2c-Closure-Refresh-2026Q2.md`** | 4k | if Treasury absorption or net equity supply | ✓ | ✓ |
| **`2026-09-12-Oracle-RPO-And-Financing.md`** | 3k | if F (AI funding), leases, or the backlog lenses | ✓ | ✓ |
| `Parcel_P3R_Multiplier_Review_For_Grok_Cursor.md` | 1k | if reviewing the M decision | — | — |
| **`2026-09-11-Green-Passive-Bid-Corpus-Dossier.md`** | 5k | if channel (d) or D-G | ✓ | ✓ |
| `_research/2026-09-11-Channel-Map-Gaps.md` | 2k | if re-planning | — | ✓ |
| `Where_The_Two_Workstreams_Meet.md` | 2k | ✓ | ✓ | ✓ |
| **2026-08-22-Guarantee-Stack.md** | 4k | if guarantees | ✓ | ✓ |
| **2026-08-22-Grok-External-Review.md** | 4k | — | ✓ | ✓ |
| **2026-08-21-Singh-And-The-Two-Circuits.md** | 6k | if circuit | ✓ | ✓ |
| **2026-08-21-Safe-Asset-Share-Reexamined.md** | 7k | if safe assets | ✓ | ✓ |
| **2026-08-21-Offshore-Dollar-And-Money-Like.md** | 11k | if offshore | ✓ | grep |
| `2026-08-21-Inbox-Harvest-And-Research-Plan.md` | — | **PRIVATE since 24 Sep (E-011)** — not in this repo; the Dropbox companion's `private/2026-08-21-Inbox-Harvest-And-Research-Plan.md` | — | — |
| `Review_Prompt_For_Gemini.md` | 3k | — | — | if reviewing |
| **`Review_Prompt_For_Gemini_Retrieval.md`** | 3k | **if retrieving** | — | if reviewing |
| `Review_Prompt_For_Grok.md` | 3k | historical — superseded by the dated topic parcels below | — | — |
| `Parcel_A_Interlock_For_Gemini.md` | 2k | if interlock | — | — |
| `Parcel_B_Essay_Numbers_For_Gemini.md` | 2k | if essay numbers | — | — |
| `Parcel_C_FERC_Dockets_For_Gemini.md` | 2k | if RTO/FERC | — | — |
| `Parcel_D1_BillSupply_Scouting_For_Gemini.md` | 3k | if D1 | — | — |
| `Parcel_D3_CashPool_Drivers_Scouting_For_Gemini.md` | 2k | if D3 | — | — |
| `Parcel_N3_CollateralLeg_Scouting_For_Gemini.md` | 3k | if N3/D10 | — | — |
| `Parcel_D8_TreasuryClearing_Scouting_For_Gemini.md` | 3k | if D8 | — | — |
| `Parcel_D8b_Conduits_For_Grok.md` | 3k | if D8/ABCP | — | — |
| `Parcel_D8c_Sponsors_For_Grok.md` | 3k | if D8/ABCP | — | — |
| `Parcel_N3R_Velocity_Review_For_Grok.md` | 2k | if N3 review | — | — |
| `Parcel_D6_Stablecoins_For_Gemini.md` | 3k | if D6/engine 5 | — | — |
| `Parcel_N2cR_Funding_Closure_Review_For_Grok.md` | 2k | if N2c review | — | — |
| `Parcel_N2a_Offshore_Scouting_For_Gemini.md` | 1k | if N2a/offshore | — | — |
| `Parcel_N2aR_Offshore_Review_For_Grok.md` | 2k | if N2a review | — | — |
| `Parcel_N2bR_zk_Review_For_Grok.md` | 2k | if N2b/z_k review | — | — |
| `Parcel_D10R_Reuse_Review_For_Grok.md` | 1k | if D10 review | — | — |
| `Parcel_SB1_Briefing_Verify_For_Grok_Cursor.md` | — | **PRIVATE since 24 Sep (E-011)** — not in this repo; the Dropbox companion's `private/Parcel_SB1_Briefing_Verify_For_Grok_Cursor.md` | — | — |
| `Parcel_SB2_Briefing_Verify_For_Grok_Cursor.md` | — | **PRIVATE since 24 Sep (E-011)** — not in this repo; the Dropbox companion's `private/Parcel_SB2_Briefing_Verify_For_Grok_Cursor.md` | — | — |
| `Parcel_ATT1_Premium_Attack_For_Grok_Cursor.md` | 1k | if attacking the premium finding | — | — |
| `Parcel_RET1_Retirement_Flows_For_Gemini_AGY.md` | 1k | if retirement flows (D-G remainder) | — | — |
| `Parcel_ZK2_DoubleCount_Lens_For_Gemini_AGY.md` | 2k | if z_k/double-count | — | — |
| `Personas/*.md` | 4k each (5 files) | if running the panel | — | if presenting |
| `Third_Derivative_Concept_Map.md` | 5k | if cascade | if cascade | ✓ |
| `Funding_Identity_First_Principles.md` | 11k | if funding | if funding | ✓ |
| `Shadow_Debt_Measurement_Handbook.md` | 10k | if measuring | if measuring | ✓ |
| `Collateral_State_of_Argument.md` | 1k | if workstream B | ✓ | ✓ |
| `Collateral_Open_Questions.md` | 1k | if workstream B | — | ✓ |
| `Collateral_Data_Inventory.md` | 2k | if measuring | — | — |
| `Third_Derivative_Case_Library.md` | 11k | if cascade | if cascade | grep |
| `Analysis/Panel_Synthesis.md` | 4k | — | ✓ | ✓ |
| `Analysis/Forward_Prediction_Register.md` | 10k | — | ✓ | ✓ |
| `Analysis/Panel_Individual_Reads.md` | 26k | — | grep | grep |
| `Analysis/Input_Substrate_Forward_Thinkers.md` | 28k | grep | grep | grep |
| **`Shadow_Debt_Channel_Map.md`** | **106k** | **NEVER whole — grep only** | **grep only** | **grep only** |
| `_research/**` | ~500k | **never** unless cited by id | sample | never |

A **synthesist** should be given a curated digest by the orchestrator, not sent to read.

## Anti-patterns — prohibitions, not guidance

1. **Never dispatch N agents with the same prompt and read agreement as confirmation.**
   Same question, different mandatory corpora and different lenses. Divergence is the datum.
   This has already produced false consensus three times: nine traditions "independently"
   confirming one accounting distinction, six of them citing the same 2011 BIS paper; and
   six research agents all missing the same 2024 review.
2. **Never paste one agent's output into another agent's prompt and then call the second
   agent independent.** Subagents already cannot see each other's transcripts — blinding is
   free and automatic. The orchestrator is the leak.
3. **Never write a number into a document without its source and vintage.** A number
   recorded without provenance is *permanently* unprovenanced; that is how C-001 happened.
4. **Never cite the same publication through two intermediaries and count it twice.**
5. **Never quote a figure from `_research/`** without checking it survived the verifier pass
   recorded in the same folder.

---

## Working rules

**The standard of evidence is a rough understanding, not proof to the last cent (E-005, 14 Sep).** A
directionally right estimate with a wide band is a result. Do not close a line of work because it misses a
significance threshold — report the estimate, the band and the confidence. This does NOT relax verification
of inputs against source, denominators, or the corrections register: being roughly right depends on the
inputs being actually right.

**We never pay for data (E-005, 14 Sep).** Permanent and settled. Do not raise it, do not frame a finding as
blocked on a purchase, do not cost one out. Free and online only.


- Answer directly. No disclaimers, no "consult an expert", no apology language.
- If you don't know, say "I don't know". **Never fill a gap with a plausible number.**
- If you made an error earlier, correct it explicitly — and append it to `CORRECTIONS.md`
  with every `file:line` where the dead claim still stands.
- Ask before answering when the question is genuinely ambiguous.
- **No policy or macroprudential recommendations.** Descriptive and quantitative only.
- **No trade recommendations.** The persona panel outputs positions as an analytical device
  to force divergence; that framing must travel with them.
- **The Hermes podcast corpus** (Martin's, private) is a lead source, never evidence: cite by episode id,
  paraphrase, quotes under 15 words, and name a speaker only where the episode roster binds the name.
  Its access recipe is deliberately NOT in this folder (Grok and Gemini read it): a Claude session has it in
  local memory (`hermes-corpus-research-access`); anyone else asks Martin. Raw transcripts never go here.
- **What may sit in this folder** (ruled by Martin 11 Sep, `THE_ASK.md` E-004): paraphrased notes of paid material
  (newsletters, transcripts, research notes) and attributed quotes of 15 words or fewer. Never raw transcripts,
  raw emails, account or personal emails, or corpus access details. Grok and Gemini read this folder.
- **SEC requests carry a declared contact** (ruled by Martin 12 Sep): `User-Agent: ThirdDerivativeResearch/1.0`
  for **sec.gov hosts only** — SEC's fair-access policy refuses undeclared tools on `www.sec.gov` (filing documents). Every
  other host gets `Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)` with NO address.
- **Traps that have already cost time here** (25 Aug): a **matching rule is a hypothesis** — the same census
  gave $2.78bn, $5.97bn and $7.16bn for one issuer depending on whether the name pattern caught `CHESHAM FIN`
  and whether the category filter admitted paper filers mis-tagged as Non-Financial CP (C-059). `cmegroup.com`,
  `dtcc.com`, `theocc.com`, `fitchratings.com` and `spglobal.com` bot-block curl — use the browser or a
  read-through renderer, and never quote a search snippet of a gated page as evidence. FERC's eLibrary
  `filelist?accession_number=` returns an identical shell for any input (C-048) — but the underlying API works (30 Aug): docket sheets need a browser (POST GetSingleDocketSheet returns empty DataList to curl), while `GET eLibraryWebAPI/api/File/GetFileListFromP8/<accession>` and `POST .../File/DownloadP8File` (body `{"fileidLst":["<GUID>"],"Islegacy":false,...}`) both work from curl — see the FERC pull in the 2026-08-30 FERC doc §0. `~/Dropbox` is an SMB mount:
  the Edit tool's atomic rename fails — write in place with python. **Overwrite-in-place releases must be vintaged on pull** (FINRA margin, Fed H.6): one URL, contents replaced each
  month, so a figure read today cannot be re-verified next month. Save a dated copy under `data/vintages/<src>/`
  at pull time — H.6 vintages live in `data/vintages/h6/`. And check the release date INSIDE the file before
  reading any column as current (C-068: `Publish/mfh.txt` serves HTTP 200 while frozen since Mar-2023). **A paywall is a property of the URL, not
  the article** (C-061): Risk.net and Central Banking are one publisher and cross-post — check the sibling site
  before recording a piece as gated. External returns can land as PRs on the WRONG repo (Grok-in-Cursor put a
  research return on hermes-core as PR #557) — if a promised return file is nowhere on disk, check `gh` before
  concluding it was not written.
- **Read the Notes on Data before reading a level change as a flow** (C-064): H.8's 2025 NDFI "surge" was
  64% reclassification, published in five dated notes on the same website as the series. **And a ratio's two
  windows are part of the claim** (C-063): publish both end-dates, recompute matched before it enters a doc.
- **Venue is not counterparty** (C-066): FR 2004 says WHERE dealer financing sits, OFR Brief 26-03 says WHO
  is on the other side — infer WHO from WHERE and the entity-typed census will break you. Use them as a pair.
- **External-seat routing, checked 3 Sep 2026 (re-check before relying on it — these rot in weeks).**
  **Grok 4.6** (released 12 Aug 2026) is a FLAGSHIP: Artificial Analysis index 61, level with GPT-5.6,
  just behind Opus 5 (63); it tops GDPval and Harvey Bench, i.e. professional document-against-source
  scrutiny. **Gemini 3.8 Flash** (2 Sep 2026) is a BUDGET tier — Google's third Flash in six weeks with
  no frontier release; strong on chart reasoning (CharXiv 86.2%) and long-horizon coding, priced at
  $0.75/$3.75 per Mtok. They are not peers, so "Grok or Gemini" is the wrong question: ask flagship or
  budget. **Our own evidence agrees with the benchmarks:** SB1 (Grok) caught a LOGIC error — an
  overstatement of what our evidence proved (C-073) — while ZK2 (Gemini) reproduced every figure
  exactly but its qualitative claims needed marking unverified. **Route judgement and
  overstatement-hunting to Grok; route arithmetic re-computation and structured extraction to Gemini.**
  **SEARCH vs READING is the sharper split, graded on our own nine returns.**
  *Gemini asked to SEARCH the web: unusable citation layer.* Six for six produced fabricated
  identifiers — C-050 (8 constructed references, over a self-audit asserting none), C-054 (9
  constructed identifiers, and every dollar figure destroyed in transit), C-055 (constructed URLs
  throughout, 2 invented papers), C-057 (every URL constructed, 2 invented papers), C-062 (a stale
  headline DESPITE live search: 168bn against 311bn live), and N2a-S (4 of 13 URLs constructed
  despite an explicit do-not-construct instruction). The SUBSTANCE layer in those same returns —
  dataset names, table structures, cadences, caveats — was near-perfect throughout. Google's own
  developer forum carries the identical complaint ("Hallucinated URLs with grounding": correct
  answers, fabricated sources), and published work finds reasoning models do WORSE at grounded
  summarization because they add inferences beyond the source. *Gemini NOT searching, reading files
  on disk (ZK2): flawless* — every figure reproduced to 4dp.
  *Grok asked to search and cite: reliable.* N3R 13/13, N2cR 25/25, D10R 13/13, N2aR ~19/20 with
  one mis-pull I caught by re-measuring, SB1 62 claims of which it correctly refuted 3 of mine.
  **Operational grade: Gemini search D, Gemini file-reading A, Grok search/research A-, Grok
  judgement A.** Never send Gemini to FIND a source; send it to READ one you name. Send Grok when
  the answer must arrive with citations that hold.

- **Compute a calibration EVERYWHERE it can be computed before calling it a convention** (C-074). This is the
  general rule; the one below is its time-series special case. A share, ratio or conversion factor inferred from a
  SINGLE observation is a coincidence until the others are run: the '32% of the cash-like bucket' that reproduced
  Singh's 2017 row exactly turned out to wander 32-71% across 2013-17. **And a caveat is not a substitute for
  running the check** — I wrote 'one year, one row, repeat before the letter goes' and let the headline stand anyway.
- **Plot the intermediate points before reporting a change between two dates** (C-070, and the third of a family:
  C-063 ratio windows, C-069 stacked windows). Two endpoints that agree are evidence of NOTHING until the path
  between them is seen — my 'z_k is flat' headline was two dates that coincided at 19.05% inside a 4.7pp range.
  Naming the risk in the review parcel did not stop me publishing it; only the intermediate series does.
- **State both perimeters in the same sentence** (C-067): a comparison whose two sides have different
  perimeters (US-six vs global top-20) is not a comparison. Name the panel before naming the ratio.
- **A correction is a claim.** It gets the same verification as a finding, and preferably by a *different
  method* from the one that produced the number it kills. On 24 Aug a register entry (C-058) killed a correct
  figure and propagated the wrong replacement to four places within an hour; see C-059. Corollary: **a matching
  rule — a name list, a category filter — is a hypothesis about how the data is written down.** Test it against
  raw text (pull everything once, filter locally, check a known-large name for spelling variants) before
  trusting its output.
- **External returns (Gemini, Grok, any model outside this repo).** File under `_research/` on
  receipt, never at top level (C-050). Ask for publisher + table + series *name*, never IDs, pages
  or quotes (C-051). **An identifier that arrives unasked is treated as absent** — re-derive every
  citation from author + title via Crossref, fetch every URL, before reading the return's summary
  of it (C-054: 9 of 12 citations constructed, 5 of 5 DOIs wrong, in a parcel that had not asked
  for them). Tell the model to write its file through a literal-safe path — a quoted heredoc or a
  file-write tool — or every `$` figure arrives empty (C-054). The self-audit is completeness, not
  truth (C-051). **Receipt procedure (C-055): fan the verification out — one agent per row group, every URL
  fetched, every file downloaded, every citation re-derived — before anything from the return is read as a
  finding; mandatory rows get filled with the same plausible filler (the N3 return gave eleven CCPs identical
  attributes). The full rule set lives in `CORRECTIONS.md` C-045, C-049–C-051, C-054–C-056.

## Analytical invariants

1. **Stock ≠ flow ≠ velocity.** Turnover is mostly rollover of an existing stock. Say which.
2. **Never sum across measurement bases.** One $100m unitranche loan appears in eleven
   statistical systems; the naive sum is 8–10× the loan. Measure credit once at the
   obligor's liability side, money once at the holder's asset side, and never add the two.
3. **Valuation is not money.** Market capitalisation is a price times a share count.
4. **Primary source only.** BIS, IMF, FSB, ECB, OFR, Fed, BoJ, NAIC, SEC directly.
5. **Check for revisions; note the vintage.** Economic data is restated years back.
   FRED-carried series have free point-in-time history in **ALFRED** — do not rebuild it.
   Only *capture-or-lose* sources (BIS full-dataset CSVs, OFR, ISLA, ICMA, vendor price
   boards, Fed FSR tables) need capturing, and there are ~25–40 of them.
6. **Steelman the counter-argument** rather than omitting it.
7. **The layer ordinal is indexical.** Every third order is some other case's first order.
   Fix a dated layer-1 event, or use the Input-Price Frame.
8. **A normalised statistic is not a quantity.** This project has made the same error twice
   in one day. A **ratio** (Gorton-Lewellen-Metrick's constant safe-asset *share*) says nothing
   about the level unless you know the denominator — C-017. A **net** coefficient (KVJ's
   −0.486, on short-term debt net of the sector's own Treasury holdings) says nothing about the
   gross quantity, and can net a whole channel to zero by construction — C-018. Before building
   on any published coefficient: **what is the dependent variable, exactly, and what does it
   net out?** Read the variable definition, not the abstract.
9. **Retrospective clarity is not prospective skill.** Any forward claim names what would
   falsify it, and by when — and that date goes in `CALENDAR.tsv` or it does not exist.

---

9. **A caveat that lives only in the document that raised it will be violated by the next
   document.** When a pass produces a *do-not-say* list, promoting it into `CORRECTIONS.md`
   is part of landing that pass. `bin/check.sh` can only guard what has been registered —
   see C-040, where our own 21 Aug list caught a defect that reached an external reviewer
   anyway because 14 of its 17 items were never promoted.

---

## Method

Both workstreams run the **step-ladder** protocol (`/step-ladder`): investigate on
independent lenses → verify load-bearing claims with fresh agents → spec → adversarial
review on two axes → supervisor re-spec → implement → supervisor verify. **No rung is
checked by whoever produced it.**

This is not ceremony. Round 1 of workstream A was returned `materially_flawed` by all three
verifiers — a third of entries duplicated, one fabricated citation returning zero search
results, a shale-gas figure wrong by an order of magnitude. None reached the report.

> **Both workstreams had their headline thesis die under attack, and the reframe underneath
> was the better argument each time.** A surviving original thesis is a sign the attack was
> too soft.

**On prediction scoring:** do not build it to measure calibration. At this cadence the score
is uninformative for years — detection power is ~24% at N=6 and needs N≈50–80. Predictions
are registered because *writing a claim in resolvable form is a hygiene device that fires at
registration time*, not because the score will mean anything.

---

## File structure

| Path | Contents |
|---|---|
| `RESEARCH_STATE.md` | **The live argument.** Settled / contested / load-bearing / open. The logic map |
| `CORRECTIONS.md` | **Dead claims.** Append-only. Read first, every session |
| `CALENDAR.tsv` | **Dated obligations.** Seeded from prose, not from the register |
| `Where_The_Two_Workstreams_Meet.md` | The join. Start here for orientation |
| `Third_Derivative_*.md` | Workstream A: framework, 24-case library |
| `Funding_Identity_First_Principles.md` | Workstream B: the identity, the residual, the illusion chain formalised |
| `Shadow_Debt_*.md` | Workstream B: nine-channel map, measurement handbook |
| `Collateral_*.md` | Workstream B: inherited state of argument, data inventory, open questions |
| `Personas/` | Four subagent primers + usage guide |
| `Analysis/` | Forward register, panel synthesis and reads, input substrate |
| `_research/` | Raw agent output and evidence. Not the deliverable |

**New findings files are date-prefixed** (`2026-08-21-Topic.md`) so a reader can tell
vintage from the filename without opening it. Existing files keep their names.

---

## Standing principles

- **The second order usually looks like a mistake while it is happening.**
- **The framework's main value is exclusion, not selection.** If the overbuild is competing
  output capacity in the market it was built to serve, the framework does not apply —
  forecast consolidation, not succession. Never use it to pick winners.
- **Value accrues to the holder of the scarce cospecialised complement**, not to whoever
  buys the asset.
- **The bubble is neither necessary nor characteristic** — four hyperscale third orders in
  the corpus were built with no bust.
- **Do not build hagiographies.** The personas encode the record, not the reputation.

## House style

Dense prose over bullet lists. Numbers with their vintage and unit attached. Every
quantitative claim traceable to a named series or paper. No filler transitions.

---

## Live items

See `bin/check.sh --todo` — the current ranked open items live in `RESEARCH_STATE.md` §5 and are queried from there, never copied here (this section itself used to be the second hand-written home; deleted 11 Sep 2026 housekeeping).
