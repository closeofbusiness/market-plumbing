# Spec: front page and About line for market-plumbing

Binding notes: `verified_facts_and_constraints.md` wins where a lens disagrees. Items marked UNCERTAIN are not stated in the source files. Do not add a personal name. The byline is the organisation closeofbusiness. The working name is Third Derivative Research. The repository title stays Market Plumbing.

## 1. GOAL

The front page is for a central-bank or IMF economist who may brief the result, a financial journalist who may quote it, and a researcher who may rerun a figure. After the first screen (file lines 1–25 of `README.md`, defined in section 7), each of them must be able to state what the work says is holding prices up, what it says about whose money, that the price effect of that money is unmeasured, the date 17 September 2026, and which document is the authority. The tone is plain institutional. Three rules for the writer: put the result in the answer section immediately under the question, in the answer note’s words and no stronger; do not answer a mistake the reader has not made (do not write “on purpose”, “not to confirm”, “proves nothing”, “nothing else changed”, or “you don’t need”); use the public names closeofbusiness, Third Derivative Research, Claude, Grok, and Gemini, and leave file nicknames to `GLOSSARY.md`.

## 2. ABOUT LINE

Implement this GitHub About description. It is a noun phrase. Hand count: 134 characters including the final period. The pass test is a machine count under 160, not the hand count.

Research record on what holds asset prices up: earnings and the risk premium, not cheaper money, and a shrinking float of US equities.

Alternative, if the owner rejects a finding in a field that cannot carry a grade. Hand count: 127 characters including the final period. Do not implement this unless the primary is rejected. Do not revive any earlier About line. Its full text is not in the source folder. Lens L1 says that earlier line treated unfinished bond markets as coverage; why it was rejected is UNCERTAIN.

Research record on what holds asset prices up and whose money is behind it, across equities, bonds, currencies and commodities.

The About line and the README answer must agree. The About line carries the finding because the current line reports record-keeping rather than a result. It is not a second sentence, and it does not say “really”, “free”, “graded”, or “retraction”.

## 3. OUTLINE

Write `README.md` in this order. No tables. At most one fenced code block (the `SEC_UA` example). Keep each paragraph as one source line. Do not hard-wrap. Visible-word budgets exclude fenced code, raw URLs, and markdown link syntax; count the visible anchor text. Section ceilings sum to 900. The file ceiling is lower only in the sense that unused room in one section is not a reason to spend it in another: each section still stops at its own ceiling.

Total budget: 900 visible words, 85 source lines. The answer section must end by source line 25.

### Opening

- Heading text: `# Market Plumbing` (the title, not a section heading). No other heading before the answer.
- Purpose: ask the question both visitors came with, and say what the repository is.
- Draft the writer starts from:

```markdown
# Market Plumbing

What is holding asset prices up, and whose money is behind it?

Market Plumbing is a public research record on that question. It follows equities, government bonds, currencies and commodities.
```

- Must contain: that question, without “actually” or “really”; “public research record”; the four markets named as equities, government bonds, currencies, and commodities.
- Leave out: a result (the next section states it), the licence, “free”, “notebook”, “that question” as the only description of the work, and any grade word.
- Word budget: 45. Line budget: 6 source lines.

### The answer so far

- Heading text: `## The answer so far`
- Purpose: give the current answer in words, dated, with the authority rule and the grade legend, on the first screen.
- Draft: use the sentences in section 4 verbatim.
- Must contain: everything section 4 lists.
- Leave out: every item section 4 forbids, plus per-sentence grade tokens the answer note does not print.
- Word budget: 260. The heading and the whole section end at or before source line 25.

### Scope and how to cite

- Heading text: `## Scope and how to cite`
- Purpose: say how far each market has got, and give the citation a reuser should print.
- Must contain, in this substance:
  - Equities are the furthest along. Rates have externally reviewed first passes. Foreign exchange and commodities have a first measurement map dated 12 October 2026, reviewed on 13 October 2026.
  - The repository is Market Plumbing. The page carries the working name Third Derivative Research. The byline is closeofbusiness.
  - This citation, verbatim: `Third Derivative Research (closeofbusiness), "What Holds the Market Up", answer note of 17 September 2026, updated in place, https://closeofbusiness.github.io/market-plumbing/.`
  - One licence sentence: written work in the repository is © closeofbusiness, CC BY 4.0, in `LICENSE`.
- Leave out: a second explanation of the two names, “JGBs”, “euro-area”, any claim that rates, foreign exchange, or commodities are finished, and a personal author.
- Word budget: 90.

### Start here

- Heading text: `## Start here`
- Purpose: three doors, then two references.
- Must contain:
  1. The page [What Holds the Market Up](https://closeofbusiness.github.io/market-plumbing/). Source file `docs/index.html`. One local command: `python3 -m http.server 8000 --directory docs`, then http://localhost:8000.
  2. The answer note `2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md`, named as the authority.
  3. `dossiers/`: one short file per channel. A file states its own status. The folder does not use one template of hypothesis, status, evidence, and what would change the claim.
  - Then `CHARTER.md` for the mission, the markets, and the grade rules, and `CORRECTIONS.md` as the register of retracted claims.
- Leave out: “don’t read it straight through”, a `C-081` search lesson, `bash bin/check.sh --latest`, “shadow money” as an undefined list item, “and others”, and a second local-view method.
- Word budget: 80.
- The page URL appears here and in the answer section, and nowhere else in the README. `docs/index.html` appears only here.

### Evidence

- Heading text: `## Evidence`
- Purpose: one short paragraph on where a number lives and what a reuser may take.
- Must contain: the answer note points each claim to the findings note that calculates it; that note names a script in `bin/` and a table in `data/`; those tables are in the repository; the record uses free, public data only; retracted claims stay in `CORRECTIONS.md`; the path for recomputing a figure is `REPRODUCE.md`.
- Leave out: a copied percentage, the earnings-share CSV path (that path lives in `REPRODUCE.md`), a count of corrections, “owns”, and “free” worn as a slogan in the opening. “Free, public data only” is allowed once, in this section.
- Word budget: 60.

### Who did the work

- Heading text: `## Who did the work`
- Purpose: disclose AI authorship without a cast list.
- Must contain, in this substance: AI models do the research. One person directs it and sets the standard of evidence. Claude and Grok work as peers. Gemini (Google) is consulted for reading and online research. Smaller Claude models do bounded tasks.
- Leave out: principal, operator, supervisor, parcel, lead analyst, xAI, Anthropic, GrokBot, “from outside”, “break the findings”, “not to confirm”, job titles, and “never simultaneous”. Those operating facts that remain true go to `GLOSSARY.md`, as specified in section 5.
- Word budget: 55.

### Where the files are

- Heading text: `## Where the files are`
- Purpose: five lines, one destination each.
- Must contain exactly these five points:
  1. Dated findings notes at the repository root. A later note says when it supersedes an earlier one.
  2. `dossiers/`, one file per channel.
  3. `data/` (including `data/series.tsv`) and `bin/`: tables and scripts.
  4. `CORRECTIONS.md`: retracted claims, kept.
  5. `RESEARCH_STATE.md`: what is settled, what is contested, and what is open. `_research/` is working evidence. Link `GLOSSARY.md` for file-name patterns.
- Leave out: the old file table, an apology for a flat folder, parcels, `CLAUDE.md`, `CALENDAR.tsv`, `HANDOVER.tsv`, `answer/`, `corrections/`, “you don’t need”, and “deliverable”.
- Word budget: 70.

### Where this came from

- Heading text: `## Where this came from`
- Purpose: two earlier streams, in readable sentences, then the date the question became the goal.
- Must contain:
  - The work began in August 2026 as two streams.
  - The first stream: a major innovation first forces a reorganisation, or builds more capacity than present demand uses, and later firms capture most of the value. Link `Third_Derivative_Concept_Map.md`. The compilation date 2 August 2026 may be included.
  - The second stream measured shadow-banking collateral and money creation on the Pozsar–Singh nonbank–bank nexus, IMF Working Paper 11/289, December 2011. Link the `Shadow_Debt_*` and `Collateral_*` files by that description, not by dumping filenames into a slogan.
  - `Where_The_Two_Workstreams_Meet.md` joins the two streams.
  - On 11 September 2026 the question at the top of this page became the goal. Link `THE_ASK.md`.
- Leave out: “the principal”, “E-003”, “channels” as insider shorthand, “these” with no antecedent, and a diary of nicknames.
- Word budget: 80.

### Checking the work

- Heading text: `## Checking the work` (this string is exact; scripts point at it).
- Purpose: the gate command, the exit-code fact, and the `SEC_UA` instruction. Everything longer goes to `REPRODUCE.md`.
- Must contain:

The bookkeeping gate is `bash bin/check.sh --all`. It checks bookkeeping, not numbers, and takes about 15 seconds. It always exits 0. Read the check-mark lines.

Before a script calls SEC EDGAR, set a contact string:

```bash
export SEC_UA="Your Name you@example.com"
```

`REPRODUCE.md` says how to recompute a figure, what the gate checks, and which inputs are not in the repository.

- Leave out: the five check names, M5–M8, ugrep, scratchpad paths, `requirements.txt`, the clone recipe, “proves nothing”, and “one to two minutes”. “Your Name you@example.com” is the existing placeholder, not a byline.
- Word budget: 90, excluding the fenced block.

### Provenance and licence

- Heading text: `## Provenance and licence`
- Purpose: the 24 September 2026 removal, discoverable in one sentence, plus the redistribution limit.
- Must contain, verbatim for the first sentence:

On 24 September 2026 nine files that should not have been published were removed, the history was rewritten, and the repository was recreated. The record of that day is in [THE_ASK.md](../THE_ASK.md) at E-011 and E-013.

- Must also contain: third-party data and paywalled text are summarised and cited, not redistributed. The SEC contact string, correspondence, simulations of named people, and third-party datasets stay outside the repository.
- Leave out: “Nothing else changed”, the 404 mechanics, the commit id `e2d0f8a`, the 90-day retention policy, a second CC BY sentence (that sentence is in Scope), and any story about what the nine files were.
- Word budget: 70.

## 4. HOW THE ANSWER APPEARS

Lens L1 wants the result and one figure on the first screen. Constraint 1 forbids restating a figure outside the note that owns it: C-081, C-089, and C-092 were copied figures that went stale. The README states the answer in words. It does not carry a figure. Dates that are already part of the answer paragraph may stay. Percentages, census fractions, and counts that can move may not.

The page https://closeofbusiness.github.io/market-plumbing/ (“What Holds the Market Up”) is a dated rendering of the answer note. Where they disagree, the note wins. The README does not say the page was “reviewed from outside on 13 October”, and it does not say the note is “not yet reviewed from outside”. Those two phrases are the stale pair. The 13 October 2026 review that the README may mention is only the review of the foreign-exchange and commodities measurement map, in Scope.

The writer uses the following sentences. They may correct grammar and may not add verbs such as “proved”, “showed”, or “established”, and may not add a number. No per-sentence grade token is printed unless the writer copies a token that is already printed on that claim in `2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md`. The materials in this folder do not print those tokens. That absence is UNCERTAIN relative to the note. The caps below are ceilings: if the note’s token is weaker, the writer keeps the draft sentence (it is already the note’s wording) and does not add a stronger label.

| What the README states | Ceiling | Date in the sentence | Link |
|---|---|---|---|
| As of 17 September 2026, updated in place. The answer note is the authority. The page What Holds the Market Up is a dated rendering of that note; where they disagree, the note wins. | Not a market claim. | 17 September 2026; updated in place. | `2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md` and https://closeofbusiness.github.io/market-plumbing/ |
| Prices rose mostly because earnings rose. What the multiple added was held up by a compressing risk premium against rising real rates, not by cheaper money. | The note’s own wording. Do not add the shares 71.0% or 82.3%. If the note grades the split as an identity, the writer may add only: “The split holds by construction and is not, by itself, evidence about the world.” Do not call the risk-premium clause established. | 17 September 2026. Do not add Dec-2025 or Jun-2026. | The answer note. |
| The money-side result is a measurement, not a cause. In the Financial Accounts (Z.1), the line that is read as equity issuance is mostly ETF wrapper creation. Strip the wrapper and US operating companies retired equity over 2024:Q1–2026:Q2. The money that arrived met a shrinking float. The price effect of that buying is unmeasured. | Measurement, not an economic result. Do not give the price effect a number. “(Z.1)” is the accounts’ name from the glossary, not a new figure. | Window 2024:Q1–2026:Q2 on the retirement sentence only. | The answer note. |
| Across the channels the goal names, the verdict is mostly negative, and that is a result. The shadow-money and collateral channels are not where the equity money came from over this window. Wholesale-repo growth in 2024 was a handoff out of the Federal Reserve's reverse-repo facility, not new cash, and collateral re-use did not rise. | Do not extend the year 2024 onto the collateral clause. Do not add “overnight”. | 2024 on the repo clause only. “This window” stays unqualified. | The answer note. |
| The AI build-out is funded mostly from operating cash flow. The answer note records who does not fit that pattern. The financing that is new sits in off-balance-sheet leases. | “Mostly” stays. Do not add “three of the five”, Amazon, Oracle, NVIDIA, or C-134. The second sentence is a guard so “mostly” is not read as “all”. UNCERTAIN: “who does not fit that pattern” is a gloss of the note’s firm list, not the note’s wording. | The answer note’s date. | The answer note. |
| The IPO boom is largely one deal (SpaceX). The census is §3a of the answer note. | Do not add “half”, “two-thirds”, or a percentage. | 17 September 2026. | The answer note. Do not invent a GitHub anchor for §3a. |
| Grades come from the answer note: identity (true by construction, not evidence about the world), measured, bounded, or hypothesis (the default). A review does not settle a claim. Definitions are in CHARTER.md. | This is the grade apparatus. It is not a finding. | None. | `CHARTER.md#grades` |

Attempts to measure the price effect “have closed” may be one clause after “unmeasured”, without the count “four”. Prefer that clause. It is the note’s status, not a weekly count.

## 5. MOVES

### Glossary

The glossary leaves `README.md`. It goes to a new top-level file, `GLOSSARY.md`.

Update the answer note. It now links to `README.md#glossary`. Change that target to `GLOSSARY.md`. Keep the visible link text. Search the repository for `README.md#glossary` and for links whose target is the README glossary, including `docs/index.html`. Retarget each in-repo hit to `GLOSSARY.md`. Whether `docs/index.html` contains such a link is UNCERTAIN; the search decides.

Add `GLOSSARY.md` to `CLAUDE.md`’s read table (constraint 3). The column layout of that table is UNCERTAIN. The filename `GLOSSARY.md` must appear. Copy the neighbouring row’s columns. Description cell: `Roles, file codes, market terms, and file-name patterns. The answer note links here.`

`GLOSSARY.md` outline:

1. `## Roles`
   - the principal: the person who directs the work and rules on scope and the standard of evidence. Older files say the operator. The public byline is closeofbusiness. Do not add a personal name.
   - Claude and Grok are peers on the research. They are not in the folder at the same time. The routing is the principal’s (`THE_ASK.md`, E-006, 15 September 2026). Claude is not the lead analyst.
   - the supervisor: whichever of Claude or Grok is reviewing the other’s work. That reviewer revises, checks, and adjudicates (`THE_ASK.md`, E-008). It is not a standing job title.
   - Gemini (Google) is consulted for reading and online research. That lane is additional. In-house Claude models (Sonnet, Haiku) do bounded tasks.
   - parcel: a self-contained brief written to be answered in one pass. Replies are dated notes ending in `-Return.md`, or files under `_research/`. Do not describe Grok or Gemini as brought in from outside.
2. `## Codes`
   - E-nnn: one verbatim instruction in `THE_ASK.md`. The series includes E-000 and E-001 and continues at least through E-021.
   - C-nnn: one retracted claim in `CORRECTIONS.md`. Search a heading such as `## C-081`. `bash bin/check.sh --latest` prints the newest headings. Do not write a count of entries.
   - Work-item labels such as P2a, N2c, and D8b are in `RESEARCH_STATE.md` §5. Do not write that B0 to B6 are the bridge designs. The only B-labels these materials verify are Frame B0 and Tier B B3, which is the elasticity pilot, also called P4. Copy no broader B-list than `RESEARCH_STATE.md` states.
   - Tiers N, O, B, T, and A2 in `RESEARCH_STATE.md` §5 group the nexus, outcome-side work, the bridge, tangents, and a persona capability that is pending a decision. What “persona capability” means beyond that phrase is UNCERTAIN; do not expand it.
   - A-numbers are rows of the table of asks in `RESEARCH_STATE.md` §0. The series does not end at A13. A14 is present. Do not write “A1 … A13” as the full set.
   - d1, d2, d3, and d4 are defects from the September 2026 document audits, labelled in the order found. d1 and d2 mark a note that names a file that is not on disk.
   - the gate: `bash bin/check.sh --all`, described in `REPRODUCE.md`.
3. `## Market terms` — carry forward, with the corrections in section 6: nexus (Pozsar and Singh, IMF Working Paper 11/289, December 2011); z_k = W / (W + M2), link `2026-08-31-N2b-zk-The-Wholesale-Share.md`; M, the multiplier, with no central value and the corrected envelope; JVZ (Jiang, Vayanos and Zheng, 2025, *Review of Financial Studies*), link `2026-09-13-P5iii-Concentration-And-JVZ.md`, and do not state the test’s outcome; Z.1 and EFA; NFC; RoW; TIC; CSLT (Treasury notice of 21 May 2026); N-PORT; N-MFP; ETF wrapper (Z.1 counts ETF share creation as equity issuance); RRP; ABCP; RPO; MDE; IV; RD; Shapley split, including the sentence “That makes it an identity, not evidence.”
4. `## File patterns` — the old README table, corrected, and not described as a complete index. Include dated findings notes and the supersession sentence; parcel filenames; `Review_Prompt_For_*.md` as historical, superseded by the dated topic parcels; `THE_ASK.md`; `RESEARCH_STATE.md`; `CALENDAR.tsv`; `HANDOVER.tsv`; `CLAUDE.md`; the two earlier workstreams; `dossiers/`; `monitor/` (series the live claims use, and when the next observation is released); `docs/`; `data/`; `bin/`; `_research/`; `Analysis/` and `Report/` as earlier-workstream outputs, including a forward-prediction register and HTML reports, without saying that is all they contain; `LICENSE`; `requirements.txt`; `.gitignore`. Dated notes with no work-item code are findings notes too, including filenames containing Green, Guarantee-Stack, Oracle-RPO, or FERC-EL26. Do not summarise those notes. Their contents are UNCERTAIN from these materials.

Leave out of `GLOSSARY.md`: the sentence “B0 to B6 are the bridge designs”, the range “2 to 9.4”, “A1 … A13” as a closed list, “standing prompts for outside review”, “one-line pointers”, and “lead analyst”.

### Reproduction

The long check-and-recompute material leaves the README and goes to a new top-level file, `REPRODUCE.md`. The README keeps the heading `## Checking the work` and the `SEC_UA` block, so a script that only points at that heading, or only says the README explains `SEC_UA`, stays true.

Add `REPRODUCE.md` to `CLAUDE.md`’s read table. Description cell: `How to run the gate, recompute a figure, set SEC_UA, and read the page locally.`

`REPRODUCE.md` outline:

1. `## The gate` — `bash bin/check.sh --all` from the repository root. About 15 seconds. Bookkeeping, not numbers. Always exits 0; read the check-mark lines; the exit code is not the result. The five checks, in corrected form: the goal statement is identical in `THE_ASK.md`, `CLAUDE.md`, and `RESEARCH_STATE.md`; every top-level markdown file is indexed in `CLAUDE.md` (the script’s label is M5; this is not a check of every file and folder); every cited C-number has exactly one register entry (M7, M8); no numbered to-do sits outside the ranked list in `RESEARCH_STATE.md` (M6); retracted wording is scanned in the notes outside `_research/` and on the page. One sentence: the script has been run with macOS grep and with ugrep. `bash bin/check.sh --latest` prints the newest correction headings.
2. `## Recomputing a figure` — follow the answer note to the findings note, then to a script in `bin/` and a table in `data/`. The earnings share of the S&P 500 gain is recomputed from `data/p2a_decomposition/decomp_cumulative.csv`. Do not print 71.0% or 82.3%. The figure stays in the findings note that calculates it.
3. `## Software and SEC_UA` — Python 3. Most scripts use the standard library. `requirements.txt` covers the five scripts in `bin/` that read spreadsheets (`xlrd` for `.xls`, `openpyxl` for `.xlsx`, and `pandas` for one of them) and the numpy scripts under `_research/`. Repeat the `SEC_UA` export.
4. `## Inputs not in this repository` — Shiller’s `ie_data.xls`, FRED DGS10 and DFII10, and Damodaran’s `ERPbymonth.xlsx` are not redistributed. `.gitignore` keeps them out. Download them from their publishers to the path the script names. US federal primary sources are kept under `_research/primary_sources/`. Do not write “public domain”. Whether that folder is only OFR PDFs is UNCERTAIN; do not claim a complete inventory.
5. `## Old scratchpad paths` — some older notes cite `<session-scratchpad>/`. Before 9 October the path was `/private/tmp/claude-501/`. That workspace has been deleted. The durable copy is the repository path cited alongside it. `python3 bin/check_scratchpad_refs.py` lists any path that still has the `/private/tmp/` form. The year 2026 on “9 October” is UNCERTAIN; it is the default because the surrounding record is 2026.
6. `## Read the page locally` — GitHub Pages publishes `docs/` from `main`. The clone block:

```bash
git clone https://github.com/closeofbusiness/market-plumbing.git
cd market-plumbing
python3 -m http.server 8000 --directory docs
```

Then http://localhost:8000. Do not say that opening `docs/index.html` directly also works. Do not mention fonts.

Leave out of `REPRODUCE.md`: the 24 September git postmortem, the 90-day policy, and the 404 note. Those stay in `THE_ASK.md`.

### Script and link text that must change

Run:

```bash
grep -n -E 'README|SEC_UA|Checking the work|glossary' bin/* docs/* *.md
```

Rules for each hit:

- `bin/decomp_sp500_shiller.py` points at the README section “Checking the work”. The heading remains. Leave that pointer.
- A hit that says the README explains `SEC_UA`: leave it. The export remains under that heading.
- A hit that says the README contains the five gate checks, `requirements.txt`, the scratchpad linter, ugrep, third-party download paths, or the local-server recipe: replace that pointer with `See REPRODUCE.md.`
- A hit of `README.md#glossary`: replace the target with `GLOSSARY.md`.

The names of the scripts other than `bin/decomp_sp500_shiller.py` are UNCERTAIN. The grep is the list. Do not change a script’s arithmetic.

### What does not move into a new file

Do not create `CITATION.cff`. The citation sentence in the README is the citation. Do not add a wiki. Do not edit the answer note except for the glossary link. Do not edit `CHARTER.md`, `CORRECTIONS.md`, or the page’s findings.

## 6. FACT FIXES

Corrected forms the new text does state:

| Stale or false statement | Where the corrected form goes | Corrected wording |
|---|---|---|
| “It is a dated rendering of the answer note,” read as if the page and the note had the same review status. Grade in lens L3: STALE. | README answer, first paragraph. | “The page What Holds the Market Up is a dated rendering of that note; where they disagree, the note wins.” |
| “Each [dossier] gives the hypothesis, its status, the evidence, and what would change it.” FALSE. `commodities.md` does not use that template. | README Start here. | “`dossiers/` is one short file per channel. A file states its own status. The folder does not use one template of hypothesis, status, evidence, and what would change the claim.” |
| “Claude (Anthropic) is the lead analyst. It writes the answer and, as the supervisor, checks and rules.” FALSE. | README Who, and `GLOSSARY.md` Roles. | “Claude and Grok work as peers. Claude is not the lead analyst. The reviewer of a given piece revises, checks, and adjudicates; the files call that reviewer the supervisor.” The README sentence stops before “supervisor”. |
| “Brought in from outside.” STALE. | `GLOSSARY.md` Roles only. | “Claude and Grok are peers in this repository (`THE_ASK.md`, E-006, 15 September 2026). Gemini (Google) is consulted for reading and online research.” |
| “`Review_Prompt_For_*.md` are standing prompts for outside review.” STALE. | `GLOSSARY.md` File patterns. | “`Review_Prompt_For_*.md` files are historical. Dated topic parcels superseded them.” |
| “A1 … A13” as the rows of `RESEARCH_STATE.md` §0. STALE. A14 is present. | `GLOSSARY.md` Codes. | “A-numbers are rows of the table of asks in `RESEARCH_STATE.md` §0. The series does not end at A13. A14 is present.” |
| Published multiplier estimates “roughly from 2 to 9.4”. STALE. The 8.7–9.4 range appears in no paper checked. “No central value” remains true. | `GLOSSARY.md` Market terms, linked to `2026-09-11-P3-Price-Impact-Multiplier.md`. | “The programme has no central value for M. The envelope adopted in the 11 September 2026 P3 note is about $2 to $9.” |
| “B0 to B6 are the bridge designs, which try to measure how far buying moves prices.” FALSE. | `GLOSSARY.md` Codes. | “Do not describe B0 to B6 as the bridge designs. `RESEARCH_STATE.md` uses Frame B0, and it identifies the elasticity pilot as P4, also called Tier B B3.” |
| “Every top-level file and folder is indexed in `CLAUDE.md` (M5).” FALSE. The check finds top-level `*.md` files. | `REPRODUCE.md` The gate. | “Every top-level markdown file is indexed in `CLAUDE.md`. This check does not cover every file and folder.” |
| The gate “takes one to two minutes.” The script’s older timing is not the fact. Verified fact: about 15 seconds. | README Checking the work, and `REPRODUCE.md`. | “It takes about 15 seconds.” |
| “Nothing else changed.” FALSE. The same day also rewrote the README and moved the page. | README Provenance. | The verbatim sentence in section 3. It points at E-011 and E-013 for the rest of that day, including the README rewrite and the page move. |

“Grok (xAI)” is UNVERIFIABLE in lens L3, not graded false. The new text names Grok and does not add xAI.

These stale or false statements do not appear in the new text at all: “It restates almost no numbers on purpose”; “their job is to break the findings, not to confirm them”; “`answer/` and `corrections/` are one-line pointers”; “US federal primary sources, which are public domain” (the public-domain half is UNCERTAIN; drop the whole clause’s public-domain words); “The page loads its fonts from Google Fonts” (UNCERTAIN; drop it). `answer/` and `corrections/` are omitted. `answer/LIVE.md` calls itself a pointer, and the rest of those folders is UNCERTAIN, so the omission is the default.

## 7. SUCCESS CRITERIA

The supervisor runs these. A miss on any one is a fail.

**SC-1. Cold reader.** Personas: (a) a central-bank or IMF economist, (b) a financial journalist who might cite the work, (c) a researcher who might rerun a figure. The reader sees only the specified lines and does not open a link. Pass threshold: every question below is answered from those lines, and the string checks match.

Lines 1–25, persona (a), all four:

1. What is holding prices up? The text contains “earnings” and “risk premium”.
2. Is the money-side result a cause, and is the price effect measured? The text contains “measurement, not a cause” and “unmeasured”.
3. What is the date? The text contains “17 September 2026”.
4. Which document wins if the page disagrees? The text contains “the note wins”.

Lines 1–25, persona (b), all three:

1. Quote one sentence. The text contains “not by cheaper money”.
2. What is new about the money? The text contains “ETF wrapper” and “shrinking float”.
3. Where is the one-page version? The text contains `https://closeofbusiness.github.io/market-plumbing/` and `2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md`.

Full README, all three personas, all five:

1. Byline and working name: `closeofbusiness` and `Third Derivative Research`.
2. Licence: `CC BY 4.0`.
3. Unfinished markets: equities “furthest along”; rates’ “externally reviewed first passes”; foreign exchange and commodities dated “12 October 2026” and “13 October 2026”.
4. Retractions: a link to `CORRECTIONS.md`.
5. Who worked: “Claude and Grok work as peers” and “Gemini (Google)”. Persona (c) can also point to the heading `Checking the work` and to `REPRODUCE.md`.

**SC-2. First screen.** First screen means source lines 1–25 of `README.md`, counted with `sed -n '1,25p'`. The heading `## The answer so far` is inside those lines. The heading `## Scope and how to cite` is at line 26 or later. Case-insensitive search of lines 1–25 finds none of these tokens, as whole words unless the token is a pattern: `principal`, `operator`, `supervisor`, `parcel`, `parcels`, `gate`, `house rules`, `GrokBot`, `xAI`, `Anthropic`, `lead analyst`, `on purpose`, `E-` followed by a digit, `C-` followed by a digit, `d1`, `d2`, `d3`, `d4`, `session-scratchpad`, `/private/tmp`, `ugrep`, `M5`, `M6`, `M7`, `M8`, `deliverable`, `you don't need`, `Nothing else changed`, `9.4`, `one to two minutes`, `public domain`, `actually`, `notebook`, `really`. Pass: zero matches.

**SC-3. Length.** Strip fenced code blocks. Replace each markdown link with its anchor text. Drop heading marks. Count whitespace-separated words. Pass: that count is at most 900, the answer section is at most 260, no section exceeds its budget in section 3, and `wc -l README.md` is at most 85.

**SC-4. Links and anchors.** For every markdown link in `README.md`, `GLOSSARY.md`, and `REPRODUCE.md`: a `http://localhost` target is documentation and is not fetched; `https://closeofbusiness.github.io/market-plumbing/` and `https://github.com/closeofbusiness/market-plumbing.git` are the known-good URLs from the 14 October 2026 check; any other `https://` URL is out of scope for this rewrite and must not be introduced; a repository path exists; a `#anchor` matches a heading slug in the target file. These README headings must exist, with these slugs: `the-answer-so-far`, `scope-and-how-to-cite`, `start-here`, `evidence`, `who-did-the-work`, `where-the-files-are`, `where-this-came-from`, `checking-the-work`, `provenance-and-licence`. `CHARTER.md#grades` still resolves. Pass: no broken path and no broken anchor. The old README anchor `#glossary` is allowed to be absent, because the glossary file replaced it.

**SC-5. Gate.** From the repository root, run `bash bin/check.sh --all`. Exit code 0 is not a pass; the script always exits 0. Pass: the check-mark lines do not report `GLOSSARY.md` or `REPRODUCE.md` as unindexed, and they do not report a killed-claim hit, or a broken C-number citation, in `README.md`, `GLOSSARY.md`, or `REPRODUCE.md`. About 15 seconds is expected and is not itself the pass test.

**SC-6. About line.** The implemented description is the primary sentence in section 2. Pass: it is under 160 characters by a machine count of the stripped string, it contains one period and that period is the last character, it contains no `?` and no `!`, and it contains none of `really`, `free`, `graded`, `retraction`, `notebook`, `principal`.

**SC-7. Forbidden strings in `README.md`.** Pass: none of these appear: `Nothing else changed`, `on purpose`, `almost no numbers`, `lead analyst`, `one to two minutes`, `9.4`, `8.7`, `public domain`, `xAI`, `one-line pointer`, `B0 to B6`, `you don't need`, `proves nothing`, `brought in from outside`, `house rules`, `the principal`, `the supervisor`, `the operator`, `GrokBot`, `/private/tmp`, `Google Fonts`, `71.0`, `82.3`, `C-134`, `three of the five`, `half and two-thirds`, `not yet reviewed`, `reviewed from outside on 13 October`. The last of those may appear only if it is clearly attached to the foreign-exchange and commodities map. The safer pass is that the phrase “reviewed from outside” does not appear at all.

**SC-8. Required survivors.** Pass: `README.md` contains `bash bin/check.sh --all`, `about 15 seconds`, `export SEC_UA=`, the heading `## Checking the work`, `E-011`, `E-013`, `24 September 2026`, `GLOSSARY.md`, and `REPRODUCE.md`. The answer note contains `GLOSSARY.md` and does not contain `README.md#glossary`. `CLAUDE.md` contains the filenames `GLOSSARY.md` and `REPRODUCE.md`. `GLOSSARY.md` contains `about $2 to $9`, `no central value`, `A14`, and `not the lead analyst`, and does not contain `2 to 9.4` or `B0 to B6 are the bridge designs`.

**SC-9. Names.** Pass: the only human surnames in `README.md`, `GLOSSARY.md`, and `REPRODUCE.md` are Pozsar, Singh, Jiang, Vayanos, Zheng, Shiller, and Damodaran. SpaceX may appear in the README answer. `Your Name you@example.com` may appear only as the `SEC_UA` placeholder.

## 8. OPEN QUESTIONS

Each item is unresolved from the source folder. The default is what the writer implements.

1. Per-claim grade tokens are not in `answer_one_paragraph.md`. UNCERTAIN what the answer note prints on each sentence. Default: print no per-sentence token; print the legend in section 4; if the note prints a token, copy it and do not raise the wording above section 4’s ceiling. If the note marks a draft sentence as retracted, delete that sentence and stop.
2. The GitHub slug for §3a is unknown. Default: link the answer-note filename and write “§3a” in the sentence. Do not guess an anchor.
3. The exact wording inside `bin/` scripts, other than the pointer in `bin/decomp_sp500_shiller.py` and the fact that several scripts mention the README’s `SEC_UA` explanation, is unknown. Default: the grep rules in section 5.
4. The column layout of `CLAUDE.md`’s read table is unknown. Default: make the filename appear, and copy the neighbouring row’s columns.
5. Whether any file other than the answer note links to `README.md#glossary` is unknown. Default: the repository search in section 5; update every in-repo hit; leave links outside the repository alone.
6. The contents of `answer/` and `corrections/`, beyond `answer/LIVE.md` calling itself a pointer, are unknown. Lens L3 grades “one-line pointers” false. Default: omit both directories from the README and from `GLOSSARY.md`.
7. Whether a draft phrase such as “not by cheaper money” matches a killed-wording pattern is unknown. The patterns are in `CORRECTIONS.md`, which is not in this folder. Default: if the gate flags a phrase taken from the answer paragraph, stop and report the pattern. Do not invent a replacement finding.
8. The GitHub homepage field is unknown, and no `CITATION.cff` decision is in the verified facts. Default: do not change the homepage field and do not add `CITATION.cff`.
9. The previous About line’s full text is not in the folder. Why the owner rejected it is UNCERTAIN. Default: do not revive it.
10. Whether the reverse-repo facility in the answer should be called “overnight” is unknown. The glossary defines RRP as overnight; the answer paragraph says “the Fed's reverse-repo facility”. Default: “the Federal Reserve's reverse-repo facility”, without “overnight”.

---

## 9. SUPERVISOR RE-SPEC (14 Oct 2026, after two adversarial reviews) — THIS SECTION OVERRIDES SECTIONS 2–8 WHERE THEY DIFFER

Both reviews (fidelity; reader and upkeep) returned "does not survive". Accepted:
- The section 4 sentences paraphrase the answer note and come out stronger than it ("not a cause", "largely one deal",
  a premium sentence the page lists as retracted, a shadow-money negative wider than C-118 allows). A paraphrase on the
  front page is a second source of truth: the C-081/C-089/C-092 failure moved from figures into sentences.
- The primary About line puts ungraded findings in a field that cannot carry a grade.
- Ten sections and 900 words rebuild the manual; dated stage lines ("reviewed 13 October") need monthly edits.

**Overruled, stated plainly:** lens L1 asked for the result on the first screen. The README will not restate findings at
all. Constraint 1 is binding, and both reviews showed that a front-page paraphrase drifts stronger than its source. The
answer is one click from line 3 instead.

**Found in passing (fidelity review), fixed in the same landing:** the answer note's own one-paragraph answer still says the
multiple was "held up by a compressing risk premium against rising real rates — not by cheaper money", which its §1 (C-102)
and the page ("adds less than it seems"; ledger row "The premium, not rates, held the multiple up — Retracted") have moved
past, and that the shadow-money channel is "not where the equity money came from over this window", where its own table
says the full 2024–26 window is "not ruled out" (C-118). Rewrite those two sentences to match the page's current wording
and register C-143 with ban patterns.

### 9.1 About line
Ship the alternative: "Research record on what holds asset prices up and whose money is behind it, across equities, bonds,
currencies and commodities." No finding, no grade words.

### 9.2 README.md — a door, about 350–450 visible words, at most 60 source lines, no tables, no restated findings
1. `# Market Plumbing`, then the question on its own line: "What is holding asset prices up, and whose money is behind it?"
2. One paragraph: what this is (an open research record on that question, covering US equities first, and government bonds,
   currencies and commodities as the work reaches them) and where the answer is: the one-page answer
   (https://closeofbusiness.github.io/market-plumbing/, "What Holds the Market Up") and the answer note it renders,
   which is the authority where the two differ. No findings, no dates of findings, no counts.
3. `## How claims are handled` — two or three sentences: every claim carries one of four grades (link CHARTER.md#grades);
   most are hypotheses until tested; claims that fail are withdrawn and kept on record in CORRECTIONS.md rather than deleted.
   Free public data only (said once, plainly). No sermon, no "a review does not settle".
4. `## Who does the work` — two sentences: AI models do the research and writing: Claude (Anthropic) and Grok (xAI) work as
   peers, and Gemini (Google) is consulted for reading and online research. One person directs the work and sets the
   standard of evidence. (Vendor names are allowed here: they are public facts that make the disclosure meaningful.)
5. `## Using and citing it` — the licence (own write-ups CC BY 4.0, © closeofbusiness; third-party data and paywalled
   text are not redistributed); a citation for the note by its title and path, and the page separately as its rendering;
   the working name Third Derivative Research; "each market's file in dossiers/ states how far the work has got" (no stage
   list, no dates); one sentence on the 24 September 2026 removal with a pointer to THE_ASK.md (E-011, E-013).
6. `## Finding your way` — a short list of links with one plain clause each: the page; the answer note; dossiers/;
   CORRECTIONS.md; RESEARCH_STATE.md (what is settled, contested, open); GLOSSARY.md (codes, terms and file names);
   REPRODUCE.md (recomputing figures, the checks, inputs not in the repository); Where_The_Two_Workstreams_Meet.md
   (the two earlier lines of work this grew out of).
7. `## Checking the work` — kept because bin/ scripts point at the README for it: two sentences and the SEC_UA block —
   "Scripts that call SEC EDGAR need a contact string" + the export line; "How to recompute a figure, run the record's
   checks and fetch the inputs that are not redistributed is in REPRODUCE.md."
Banned in README: principal, operator, supervisor, parcel, gate, house rules, GrokBot, lead analyst, E-/C-/d-numbers except
"E-011" and "E-013" in the removal sentence, "on purpose", "proves nothing", "you don't need", "deliverable", "notebook",
"actually", "really", any percentage, any count of corrections, "reviewed from outside", "simulations of named people".

### 9.3 GLOSSARY.md (new) — the old glossary and file table, corrected
Keep the old entries with section 6's fact fixes, and these changes: no copied figures (the multiplier entry says "no
central value; the published envelope is in the P3 note" and links 2026-09-11-P3-Price-Impact-Multiplier.md, without
the numbers); roles entry per section 5 (Claude and Grok peers, E-006; the reviewer of a given piece is called the
supervisor, E-008); Review_Prompt files historical; A-numbers open-ended; no B0–B6 claim; answer/ and corrections/ as
"pointer folders". Title: "# Glossary". One line under it saying what the file is for.

### 9.4 REPRODUCE.md (new) — the old "Checking the work" material, corrected
Sections: the record's checks (`bash bin/check.sh --all`; checks bookkeeping, not numbers; runs in well under a minute;
always exits 0, so read its check-mark lines; M5 covers top-level markdown files and top-level folders, not other files);
recomputing a figure (note → script in bin/ → table in data/; the S&P 500 example path, no percentage); software and
SEC_UA; inputs not redistributed (Shiller, FRED DGS10/DFII10, Damodaran; .gitignore; no "public domain" claim); old
scratchpad paths; viewing the page locally. No timing in seconds.

### 9.5 Edits outside the three files (the supervisor makes these, not the writer)
- Answer note: glossary link → GLOSSARY.md; the two headline sentences per C-143.
- CLAUDE.md read table: rows for GLOSSARY.md and REPRODUCE.md; README row description updated.
- bin/decomp_sp500_shiller.py comment: point the download instructions at REPRODUCE.md.
- Recursive search of every in-repo .md and .html for `README.md#glossary`, `#checking-the-work` and README pointers.

### 9.6 Success criteria (replace section 7)
- SC-A: README ≤ 60 lines and 350–450 visible words; no tables; the page link and the answer-note link both appear in the
  first 8 source lines.
- SC-B: README contains none of the banned tokens in 9.2, no digit outside dates, the CC BY 4.0 licence name, E-011/E-013,
  the SEC placeholder and URLs.
- SC-C: About line under 160 characters, contains no "earnings", "premium", "float", "cheaper".
- SC-D: every link and anchor in README.md, GLOSSARY.md, REPRODUCE.md and the edited answer note resolves; no in-repo
  `README.md#glossary` remains.
- SC-E: the repository's checks show all check-mark lines, no orphan, no killed-claim hit (including the new C-143 patterns).
- SC-F: cold-reader test — two fresh readers (an IMF economist; a financial journalist) see README.md only and must answer:
  what question the project asks; where its current answer is and which document is authoritative; how a reader can tell
  how solid a claim is and what happens to claims that fail; who or what did the work; how to cite it and under what
  licence. Pass: all five answered correctly by both, and neither names a sentence that reads as written by an amateur;
  each also quotes the weakest sentence, which the supervisor fixes or justifies.

*Amendment, 14 Oct (principal):* the 24 September removal sentence is taken off the README. Constraint 7 above was the supervisor's own rule, not a ruling; the record stays in THE_ASK.md (E-011, E-013).
