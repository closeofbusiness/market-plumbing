# README rewrite, step ladder with Grok agents — the returns (14 Oct 2026)

*Every rung's agent was Grok 4.7 through the fenced Cursor lane (read and web only; no breaches, no blocked attempts). The spec, with the supervisor's re-spec in its section 9, is [2026-10-14-README-Rewrite-Spec.md](2026-10-14-README-Rewrite-Spec.md); the writer's draft is not kept separately because the supervisor's edits to it are in the commit. Quotes over 15 words are cut to twelve.*

**Outcome.** Both reviewers found that the first spec would not survive: its answer section paraphrased the answer note more strongly than the note, and its About line carried ungraded findings. The re-spec made the README a door that restates no findings. The fidelity review also found the answer note's own headline paragraph lagging its body and the page (C-143). Cold readers on the final draft answered all five comprehension questions; the second economist found no sentence that read as amateur.


---

## Rung 1 lens: the editor's diagnosis of the old README

I'll read the published README and both About lines, then judge them as a central-bank economist and as a journalist who might cite the work.The front page reads as a private operating manual. It teaches nicknames, file rules, and self-checks, and it never says what the research found. The question in line 3 is the one sentence both visitors need. It is not answered anywhere in this file.

Assumption: the first screen is lines 1–25, through the introduction of the “house rules.” The answer note and the web page are not in this folder. The README asserts that an answer exists and also says the answer note “restates almost no numbers on purpose.” What that answer actually says is UNCERTAIN. Reading `2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md` would settle it.

## FAULTS

A running habit makes the voice sound young: the page keeps correcting an imaginary naive reader. “On purpose,” “not to confirm them,” “not deleted,” “not its numbers,” “not the deliverable,” “proves nothing,” “not copied,” and “Nothing else changed” are one tic. Both.

| Where | Quoted text | Fault | Persona |
|---|---|---|---|
| L3 | What is actually holding asset prices up, and whose money is behind it? | “Actually” is blog emphasis on an otherwise good question | a |
| L5 | Market Plumbing is an open research notebook on that question. | “Notebook” plus “that question” is a school-project label | both |
| L5 | It follows the money through equities, government bonds, currencies and commodities using free public data. | Slogan; “free” worn as a badge | a |
| L5 | Alongside the current answer it publishes the evidence, the scripts that reproduce it, and every claim it has since withdrawn. | Inventory of virtues; the answer itself is missing | both |
| L5 | The written work is licensed CC BY 4.0. | Licence placed before any result | a |
| L9 | the current answer on one page, with every claim graded. It is a dated rendering of the answer note, and its source is [`docs/index.html`](../docs/index.html). | “Graded” is undefined; the HTML path is file genealogy | both |
| L10 | The answer note is the authority: where the page and the note disagree, the note wins. It restates almost no numbers on purpose. Each claim links to the findings note that owns it. | Defensive precedence rule; “on purpose” explains a hole; “owns” is a private metaphor | b |
| L11 | the mission (the standing goal), the rules every file follows, and the four grades. | Parenthesis talks down; process listed as a place to start | both |
| L12 | passive and ETF flows, AI funding, shadow money, collateral, rates, and others | List fragment; “shadow money” and “and others” are undefined | b |
| L13 | It is long, so don't read it straight through. When a note cites, say, C-081, search the file for `## C-081`. `bash bin/check.sh --latest` prints the newest entries. | Talks down, then a search tutorial and a shell command | both |
| L15 | Rates, FX and commodities are in scope, and where their work has not been done, the files say so. | Planner jargon, then a reassurance | a |
| L19 | The research is carried out by AI models and directed by one person, called **the principal** in the files (older ones say *the operator*). | No name a visitor can cite; nickname plus archaeology of an older nickname | both |
| L19 | The principal sets the questions and the standard of evidence. | Grand and empty | a |
| L21 | Claude (Anthropic) is the lead analyst. It writes the answer and, as **the supervisor**, checks and rules on the other agents' work. | Cast list with play-acted titles, bolded like a textbook | a |
| L22 | Grok (xAI) and Gemini (Google) are brought in from outside. They work from self-contained briefs called **parcels**, and their job is to break the findings, not to confirm them. | “From outside” is a fake externality; “parcels” is coined jargon; the rest is a slogan | both |
| L24 | A finding stands only for as long as those attacks fail. Three house rules follow from that: | Contest language; “house rules” do not follow from that sentence | both |
| L26 | The principal's instructions are recorded verbatim, never paraphrased, in THE_ASK.md as E-000, E-001, and so on. When a note cites a standard such as E-005 or E-007, that is where it is defined. | Over-explained internal codes the visitor has not seen | both |
| L27 | Every claim carries a grade: IDENTITY, MEASURED, BOUNDED or HYPOTHESIS, defined in CHARTER.md. | Shouted labels with the meaning postponed. The next sentence, on review not settling a claim, is clear and can stay | both |
| L28 | Retracted claims are registered, not deleted. CORRECTIONS.md numbers them C-001, C-002, and so on. It also bans their wording, so the checks catch a dead claim if it resurfaces. | Motto, then slang (“bans,” “dead,” “the checks”) | both |
| L32 | The top level is flat, so GitHub's file list is long. It falls into these groups: | Apology for the author’s own layout | both |
| L36 | The code (P2a, N2c, D8b and so on) is the work item's label in `RESEARCH_STATE.md` §5, and the title says what the note is about. A later note says so when it supersedes an earlier one. | Explains the obvious; “and so on”; awkward reassurance | both |
| L37–38 | Parcels: briefs sent to an outside model. / Standing prompts for outside review. | Jargon repeated; fragments | both |
| L41 | Dated obligations (data releases and re-checks), and the agents' machine-written handover log. You don't need either to read the findings. | Debris, then a pat on the head | both |
| L42 | The operating manual for the AI agents. It is long and written for them; you don't need it to read the findings. | Same pat, second time | both |
| L44 | One-line pointers to the answer note and to `CORRECTIONS.md`. | A shortcut to a shortcut | both |
| L45 | Per-channel summaries; the free data series the live claims use, and when each next prints. | Two folders spliced; “prints” is insider rhythm | b |
| L48 | Working notes, replies from outside models, and extracted primary sources. Evidence, not the deliverable. | “Deliverable” is corporate; the fragment is a scold | a |
| L53 | The programme runs under the working name Third Derivative Research, which is the name you will see on the page and in older notes. | Two public names, explained as a mishap | b |
| L55 | A primary innovation first forces a reorganisation or an overcapacity, and later businesses capture most of the value | A theory crushed into jargon a visitor cannot parse | both |
| L56 | A measurement of these on the Pozsar–Singh nonbank–bank nexus (the `Shadow_Debt_*` and `Collateral_*` files). | “These” has no antecedent; a measurement with no result | both |
| L58 | On 11 September 2026 the principal widened the goal to the question above (THE_ASK.md, E-003). The nexus work carries over as two of its channels. | Diary of a goal change; “channels” is insider | both |
| L64–66 | the principal / the supervisor / parcel | The glossary canonizes the nicknames | both |
| L68 | a retracted claim, why it died, and the wording now banned | Cute mortuary language | both |
| L69 | Search that file for the label; the first note on an item usually carries the label in its file name. B0 to B6 are the bridge designs, which try to measure how far buying moves prices. | Another search lesson; “bridge” is a private metaphor parked on the only plain research aim in this row | both |
| L70 | Groups of work in `RESEARCH_STATE.md` §5: the nexus, outcome-side work, the bridge, tangents, and a persona capability awaiting a decision. | Kanban leaked onto the public page; the last phrase is unparseable | both |
| L71 | Rows of the table of asks in `RESEARCH_STATE.md` §0. | Means nothing here | both |
| L72 | Defects found in the September document audits, labelled in the order found. For example, d1 and d2 mark a note that names a deliverable that is not on disk. | Airing the project’s own missing-file bugs | both |
| L73 | the gate / `bash bin/check.sh --all` | A shell command given a nickname | both |
| L75 | The wholesale share: nonbank wholesale funding W, as a share of W plus M2 | Symbol before any result | b |
| L76 | Published estimates range roughly from 2 to 9.4 (the "envelope"), and the programme has no central value for it. | Someone else’s range, a cute nickname, and a confessed non-answer | both |
| L77 | Jiang, Vayanos and Zheng (2025, *Review of Financial Studies*), on passive investing and mega-firms. The programme tested their mechanism on free data. | Name-drop; the test has no outcome; “free data” again | both |
| L87 | Instrumental variables; regression discontinuity. | Bare expansion; useless to one visitor and redundant to the other | both |
| L92 | There are two kinds of check, and they answer different questions. | Teacherly tease | a |
| L100–106 | its own labels are in brackets / the goal statement is identical in its three homes (goal) / indexed in `CLAUDE.md` (M5) / no numbered to-do items sit outside the ranked list (M6) / killed claims, page check | Bookkeeping codes presented as if they were the method; “three homes” and “killed claims” are slang | both |
| L108 | Read its ✓ lines. | Cute imperative | both |
| L109 | The exit code is always 0 by design, so it proves nothing. It has been run with macOS's own grep and with ugrep. | The advertised check cancels itself; the grep line is a tool boast | both |
| L111 | Reproducing a number means following its trail. Each claim in the answer note names the findings note that owns it. | Precious metaphor; “owns” again | a |
| L111 | the earnings share of the S&P 500 gain recomputes from [`data/p2a_decomposition/decomp_cumulative.csv`](../data/p2a_decomposition/decomp_cumulative.csv) | The only concrete result on the page, with the number left out; “recomputes” is an awkward verb | b |
| L114 | `pip install -r requirements.txt` covers the five in `bin/` that read spreadsheets (`xlrd` for `.xls`, `openpyxl` for `.xlsx`, and `pandas` for one of them) and the numpy scripts under `_research/`. | Over-counted toolchain | both |
| L118 | Some older notes cite paths beginning `<session-scratchpad>/` (before 9 Oct, `<session-scratchpad>`). That was an agent's temporary workspace at the time, and it has since been deleted. The durable copy is the repository path cited alongside it. | A private temp path, an apology, and a tangled sentence | both |
| L122 | GitHub Pages publishes it from `docs/` on `main`. | Deploy trivia above the work | both |
| L131 | Opening `docs/index.html` directly in a browser also works. | A second method no visitor needed | both |
| L132 | The page loads its fonts from Google Fonts; everything else is in the one file. | Font hosting on a research front page | both |
| L136 | Third-party and paywalled documents are summarised and cited, not copied, and quotations are kept short. | Plagiarism protest no one asked for | both |
| L136 | simulations of named people | Alarming category, unexplained. What it refers to is UNCERTAIN; the removed-files note or THE_ASK would settle it | both |
| L138 | On 24 September 2026 nine files that should not have been published were removed. The history was rewritten, and the repository was then deleted and recreated, so GitHub no longer serves the old commits (they return 404). GitHub keeps a deleted repository for 90 days, visible only to organisation owners (E-013, "Limits"). Nothing else changed. | A git postmortem; “Nothing else changed” is a defensive shrug; the 90-day policy is pedantry | both |
| L138 | THE_ASK.md, E-011 and E-013, records the details. | Awkward appositive that sends the reader to code numbers | both |

These glossary rows are plain and fine, and they are in the wrong place: nexus, Z.1, TIC, N-PORT, NFC, RRP, ABCP, RPO, and the ETF-wrapper and Shapley sentences. The Shapley line (“That makes it an identity, not evidence.”) is the sharpest sentence in the file, buried under nicknames.

## FIRST SCREEN

**(a) Central-bank or IMF economist.** Missing: any result on what holds prices up and whose money it is; whether that answer is an accounting identity or a causal claim; one named dataset; a date stated in a sentence (17 September 2026 appears only inside a filename); a person or institution that can be briefed; a literature anchor (Pozsar–Singh and Jiang–Vayanos–Zheng turn up much later, still without a result). Surplus: the CC BY sentence, the HTML source path, the rule that the note wins, the boast that the note withholds numbers on purpose, CHARTER as a starting stop, the C-081 search and the bash command, and the cast (principal, operator, supervisor, parcels).

**(b) Financial journalist.** Missing: a sentence that can be quoted; a figure; a human name; what is new; one retracted claim, which is the news the page itself advertises. Surplus: the same navigation lesson, “don’t read it straight through,” `docs/index.html`, and model vendors with job titles. The licence is wanted, but only beside a name and a date.

## STRUCTURE

Target length: about half of the current 138 lines, roughly 60–80 lines. The page should be readable in two minutes. This is a judgment about length, not a word count.

1. **Question, then the current answer** — dated, in plain words, with what is measured and what is still a hypothesis, one figure, and what is open. Both visitors decide here.
2. **Scope and how to cite** — equities furthest along; rates, FX, and commodities incomplete; one byline, one date, CC BY, one link. The only byline in these files is the handle closeofbusiness.
3. **Three doors** — the one-page answer, the answer note, the dossiers. CHARTER and the corrections register are references, not the tour.
4. **Evidence, one short paragraph** — name the public sources, say that a number points to a script and a committed table, and that retractions stay in one register.
5. **Who did the work** — three lines, after the result. The AI fact belongs; the org chart does not.
6. **A five-line map** — findings notes, dossiers, data and scripts, corrections. One line each.

Move out, with a single link left behind:

- The nickname and code glossary (principal, parcel, gate, E-, C-, d1–d4, tiers, asks) belongs in CHARTER or CLAUDE.md. Market definitions can live in a separate glossary. ETF-wrapper and Shapley belong inside the answer.
- “Checking the work,” the package inventory, the scratchpad linter, and the ugrep note belong in a reproduction note.
- Local serving and Google Fonts collapse to one line under the page link.
- The two-workstream origin belongs after the answer, in a short background, once “third derivative” is a readable sentence.
- The 24 September removal becomes one sentence and a link. The 404 mechanics and the 90-day retention policy leave this page.

## ABOUT LINES

**Current.** The live line is calm, grammatical, and specific about markets and about keeping retractions. It still reports hygiene rather than a finding, and “really” plus “every claim graded” are the same emphasis and the same insider word the README overuses.

**Previous.** Its middle sentence is the best description in either file: each update decomposes the move, measures who bought against net supply, then sizes the funding channels. It then collapses into stickers (“Free data only. Hypotheses until tested.”) and names JGBs and euro-area bonds as coverage while the README says unfinished markets stay marked unfinished. Why the owner rejected it is UNCERTAIN; these two files only say he disliked it.

## TOP THREE

1. **Put the result on the first screen and give the syllabus the door.** State what holds prices up, whose money, what is solid, what is still a hypothesis, one number, the date, and one link. Lines 1–25 now fail both the thirty-second test and the citation test.
2. **Remove the private dialect from the public page.** Principal, operator, supervisor, parcel, gate, house rules, E- and C- and d-numbers, tiers, banned wording, and “you don’t need this” are the fourteen-year-old register. One adult sentence can carry the real standard: grade every claim, and keep retractions on the record.
3. **Move the workings off this page.** The file table, the code glossary, the gate, the temp-path apology, the font note, and the September git story are the passages where a careful project sounds as if it is still assembling itself.

---

## Rung 1 lens: how respected research repositories present themselves

**Cited but not fetched (not relied on):** https://tracktherecovery.org; https://tracktherecovery.org/

I’ll look up how established research and data repositories write their GitHub descriptions and READMEs, then compare that with GitHub’s own guidance. First I’ll confirm the search and fetch tools, then pull the front pages.Search results point to several official research repos. I’ll fetch those front pages and GitHub’s own docs next, and look for a Fed, BIS or IMF example plus a replication package.The GitHub pages returned the short descriptions but not the README bodies. I’ll fetch the raw READMEs and the public repository metadata so the descriptions and section order are taken from the pages themselves.The one-line descriptions below are the GitHub About field. README wording is from the default-branch README. Where a sentence runs past 15 words, the quote stops at word 15. Lengths are approximate word counts of the fetched README, made by eye. An exact count would need a word counter on those files.

## EXAMPLES

| Repository | URL fetched | Description | Opening sentence | Length | Section order | Purpose and audience | Licence and citation | Tone |
|---|---|---|---|---|---|---|---|---|
| owid/covid-19-data | https://github.com/owid/covid-19-data | "Data on COVID-19 (coronavirus) cases, deaths, hospitalizations, tests • All countries • …" (first 15 of 17) | "This repository has been archived and is no longer maintained" | About 250 words, one screen | Archive caution, title, Project structure, Documentation, Contribute | Splits "people interested in consuming the data" from people inspecting or contributing to the code | No licence or citation in the README. GitHub reports no detected licence | Blunt and operational |
| fivethirtyeight/data | https://github.com/fivethirtyeight/data | "Data and code behind the articles and graphics at FiveThirtyEight" | "See the index for a list of the data and code we've published and their" (first 15) | About 70 words, under one screen | No headings: index, update status, licence and contact | Implied readers of the published stories. Ends with a contact address | CC BY 4.0 for data and MIT for code, "Unless otherwise noted." No citation format | Terse and practical |
| TheEconomist/big-mac-data | https://github.com/TheEconomist/big-mac-data | "Data and methodology for the Big Mac index" | "This repository contains the data behind The Economist’s Big Mac index, and code that shows" (first 15) | About 1,200–1,600 words, several screens. UNCERTAIN exact count | Download, Methodology changes, Source data, Output data and codebook, Calculating, Licence | People who want the files, or who want to rerun the calculation | MIT for Economist software. CC BY 4.0 for Economist-generated data. Third-party data and Economist content excluded. No academic citation | Explanatory and instructional |
| FRBNY-TimeSeriesAnalysis/Nowcasting | https://github.com/FRBNY-TimeSeriesAnalysis/Nowcasting | "Nowcasting" | "This code implements the nowcasting framework described in Macroeconomic Nowcasting and Forecasting with Big Data" (first 15) | About 250 words, one screen | Paper citation, data-limit note, Download instructions, File and folder description, Required software | Code for a named New York Fed staff report. Says the examples do not reproduce the weekly nowcast | README cites the paper and does not state a code licence. GitHub reports BSD 3-Clause | Formal and cautious |
| bis-med-it/BIS_Multisector_Model | https://github.com/bis-med-it/BIS_Multisector_Model | "This repository accompanies our paper, “The BIS Multisector Model: A Multi-Country Environment for Macroeconomic Analysis”" (first 15) | Same sentence as the description | About 500 words, two to three screens. UNCERTAIN exact count | What the model is, How to Run, Data Sources, Licence Note, Disclaimer | A toolbox for policymakers and researchers, with a link to the paper | Apache 2.0 for the repository. External data excluded, with attribution required. Authors named. Warranty disclaimer | Institutional and formal |
| OpportunityInsights/EconomicTracker | https://github.com/OpportunityInsights/EconomicTracker | "Download data from the Opportunity Insights Economic Tracker — https://tracktherecovery.org/" | "The Opportunity Insights Economic Tracker (https://tracktherecovery.org) combines anonymized data from leading private companies" (first 13; the sentence continues) | About 550 words, two to three screens. UNCERTAIN exact count | Download, what it is, reuse rules, Reference Documents, Privacy and Integrity Statement | To inform the public, policymakers, and researchers. "Anyone is welcome to use this data," with two conditions | No detected software licence. Names the citation to use and requires data-provider credit | Careful and public-spirited |
| QuantEcon/QuantEcon.py | https://github.com/QuantEcon/QuantEcon.py | "A community based Python library for quantitative economics" | "A high performance, open source Python code library for economics" | About 450 words, about two screens. UNCERTAIN exact count | Pitch, example, badges, Installation, Usage, Examples, funding, Downloading, Citation, Star History | A Python library for quantitative economics, described as community based, with lectures and docs linked | MIT in the README. GitHub agrees. Asks readers to cite it and gives BibTeX | Practical and inviting |
| owid/etl | https://github.com/owid/etl | "A compute graph for loading and transforming OWID's data" | "The compute graph for Our World in Data's data processing." | About 80 words, one short screen | Badge, one-line pitch, status table, Documentation, Libraries, tagline | OWID’s own data processing, plus two published Python libraries. Use is documented off-site | README states neither licence nor citation. GitHub reports MIT | Dry and minimal |

The HTML front pages returned the About line and omitted the README body, so the README text was read from the raw default-branch file for each repository. An IMF-owned research repository did not turn up as a page fetched here. The BIS Monetary and Economic Department repository stands in for an official international-financial producer.

## AI tools and named roles

None of these eight descriptions or READMEs says that an AI tool did the work. That is limited to the fetched front matter. A line in a commit, a paper PDF, or another file would not show up here. A repository search for an authorship phrase would settle it.

None lists job roles. Named people appear as authors of a paper or library:

- BIS names the paper’s authors: "authored by Matthias Burgert, Giulio Cornelli, Burcu Erik, Benoit Mojon, Daniel Rees and Matthias Rottner."
- The New York Fed README names the staff-report authors: "by Brandyn Bok, Daniele Caratelli, Domenico Giannone, Argia M. Sbordone, and Andrea Tambalotti."
- Opportunity Insights prints a suggested citation "by Raj Chetty, John Friedman, Nathaniel Hendren, Michael Stepner, and the Opportunity Insights Team."
- QuantEcon puts a long author list in BibTeX, calls the library community based, and notes Sloan Foundation support.

The others speak as "we" or as the institution.

## GITHUB GUIDANCE

Fetched pages: [Creating a new repository](https://docs.github.com/en/repositories/creating-and-managing-repositories/creating-a-new-repository), [REST API endpoints for repositories](https://docs.github.com/en/rest/repos/repos), [GraphQL repository reference](https://docs.github.com/en/graphql/reference/repos), and [About the repository README file](https://docs.github.com/en/repositories/managing-your-repositorys-settings-and-features/customizing-your-repository/about-readmes).

On the description, GitHub’s user docs call it "an optional description." The create-from-URL table says the description parameter accepts "Any string." The REST and GraphQL docs both call it "A short description of the repository." The GraphQL field `shortDescriptionHTML` takes a `limit` argument: "How many characters to return. Default: 200." That is how many characters a shortened rendering returns, and it is not written as a storage maximum. The same creating-a-repository page does set a number for the name: "The repository name must not exceed 100 characters."

No fetched GitHub page states a maximum stored length for the description. A non-GitHub page in search results claimed 350 characters. That page was not fetched, so it is not treated as GitHub guidance. The repository-details form, or an OpenAPI `maxLength` on the description property, would settle it.

On the README, GitHub says you add one "to tell other people why your project is useful." It says README files typically include what the project does, why it is useful, how to get started, where to get help, and who maintains it. It also says a README sits with "a repository license, citation file," contribution guidelines, and a code of conduct. "A README should only contain information necessary for developers to get started using and contributing." "Longer documentation is best suited for wikis." Rendered README content "beyond 500 KiB will be truncated."

## RULES

1. Make the description a noun phrase that says what the repository is. FiveThirtyEight uses "Data and code behind the articles and graphics at FiveThirtyEight," The Economist "Data and methodology for the Big Mac index," OWID etl "A compute graph for loading and transforming OWID's data," and QuantEcon "A community based Python library for quantitative economics." The New York Fed description is the single word "Nowcasting."

2. Keep that line to a single breath. Six of these eight are under about a dozen words. The BIS description is a paper sentence and is still listing authors after 15 words. GitHub calls the field "A short description of the repository," and its shortened HTML rendering defaults to 200 characters.

3. Open the README with the same fact, in one sentence. etl and QuantEcon do this under the title. The New York Fed and BIS open by tying the code to a named paper. FiveThirtyEight opens by pointing at the index of stories.

4. Name the audience in ordinary roles. Opportunity Insights says the data is there to inform the public, policymakers, and researchers, and that anyone is welcome to use it. BIS addresses policymakers and researchers. OWID’s COVID README separates people who want the data from people who want the code.

5. Say what a visitor should do first, then point to the rest. OWID separates `public/data` from `scripts`. The Fed lists folders and the MATLAB version it tested. QuantEcon starts from installation. The Economist sends people to the latest release before the setup. Opportunity Insights leads with a ZIP download.

6. Keep the front page to about one screen when the long version can live elsewhere. etl, the COVID README, and FiveThirtyEight do this and link to docs, data, or an index. That matches GitHub’s instruction that a README should contain what is needed to get started, with longer documentation in a wiki. The Big Mac README is the long version: methodology, a codebook, and a full install path on the front page.

7. State the licence in the README, and separate your work from other people’s data. FiveThirtyEight and The Economist use CC BY 4.0 for their data and MIT for code, with an "unless otherwise noted" or a third-party carve-out. BIS releases the code under Apache 2.0 and tells users to attribute OECD, ADB, BEA, and BLS data. The New York Fed and etl leave the licence out of the README even though GitHub has detected BSD 3-Clause and MIT.

8. Give reusers the citation you want, in the form you want. Opportunity Insights prints the sentence to cite and asks for the data provider’s name. QuantEcon gives a BibTeX entry and asks people to cite the library. The Fed and BIS cite the paper in the opening sentence. GitHub lists a citation file alongside the README and the licence.

9. Say what this release does not include, and whether it is still updated. The Fed says the examples do not reproduce the weekly nowcast because the full data cannot be redistributed. OWID opens by saying the COVID repository is archived and where current data lives. FiveThirtyEight says sports forecasts stopped being updated on 13 June 2023.

10. Put authors in the citation, and put the paper or the public site in the homepage field. BIS, the Fed, Opportunity Insights, and QuantEcon name authors there. Fetched homepages point at the BIS paper, the FiveThirtyEight data site, the Big Mac page, the QuantEcon docs, and the two OWID sites. None of these front pages discloses AI authorship or a team roster with job titles.

---

## Rung 1 lens: fact-check of the old README

**Cited but not fetched (not relied on):** http://localhost:8000; https://api.github.com/repos/closeofbusiness/market-plumbing/contents/CLAUDE.md; https://api.github.com/repos/closeofbusiness/market-plumbing/contents/CORRECTIONS.md; https://github.com/closeofbusiness/market-plumbing.git; https://raw.githubusercontent.com/closeofbusiness/market-plumbing/e2d0f8a/README.md

I'll fact-check the published README against the repository files, starting with the local front page and the top-level listing.The front page and listing are in hand. Next I’ll fetch the charter, the ask log, the research state, and the corrections register and check each README claim against them.The charter, the ask log, and the check script are in. I’ll now check the answer note, the dossiers, and the files the README treats as the map of the repository.The README in this folder was checked against files fetched from `main` on 14 October 2026. The local README was treated as the published front page. Grades are against those files.

## CLAIMS

| README section | Claim | Grade | Evidence URL | Quote from the evidence |
|---|---|---|---|---|
| Opening | "What is actually holding asset prices up, and whose money is behind it?" | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CHARTER.md | "what is driving asset prices and where the money is coming from" |
| Opening | It follows equities, government bonds, currencies and commodities on free public data. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CHARTER.md | "also rates, FX and commodities" / "Free data only." |
| Opening | It publishes the evidence, the scripts, and withdrawn claims. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CLAUDE.md | "This repository is the research record" |
| Opening | "The written work is licensed CC BY 4.0." | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/LICENSE | "Copyright 2026 closeofbusiness" / "Attribution 4.0 International" |
| Start here | The page is the current answer, "with every claim graded." | TRUE | https://closeofbusiness.github.io/market-plumbing/ | "every claim carries one of four grades" |
| Start here | "It is a dated rendering of the answer note." | STALE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md | "not yet reviewed from outside" |
| Start here | Same claim, against the page. | STALE | https://closeofbusiness.github.io/market-plumbing/ | "reviewed from outside on 13 October" |
| Start here | "its source is docs/index.html" | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/docs/index.html | "Its source now sits in the public repository as docs/index.html" |
| Start here | "where the page and the note disagree, the note wins." | TRUE | https://closeofbusiness.github.io/market-plumbing/ | "where this page and that document disagree, the document wins" |
| Start here | "It restates almost no numbers on purpose." | FALSE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md | "71.0% to Dec-2025, 82.3% to Jun-2026" |
| Start here | "Each claim links to the findings note that owns it." | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md | "that doc is the authority" |
| Start here | CHARTER holds the mission, the markets, the rules, and the four grades. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CHARTER.md | "IDENTITY" "MEASURED" "BOUNDED" "HYPOTHESIS" |
| Start here | dossiers/ is one short file per channel, including passive and ETF, AI funding, shadow money, collateral, and rates. | TRUE | https://api.github.com/repos/closeofbusiness/market-plumbing/contents/dossiers | "passive-and-etf.md" "ai-funding.md" "rates.md" |
| Start here | "Each gives the hypothesis, its status, the evidence, and what would change it." | FALSE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/dossiers/commodities.md | "Status, 13 Oct 2026: first measurement map done" |
| Start here | CORRECTIONS.md is the register of retracted claims, and it is long. | TRUE | https://api.github.com/repos/closeofbusiness/market-plumbing/contents/CORRECTIONS.md | "size":299376 |
| Start here | Search a citation such as C-081 as `## C-081`. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/bin/check.sh | "grep -E '^## C-[0-9]+'" |
| Start here | `bash bin/check.sh --latest` prints the newest entries. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/bin/check.sh | "newest corrections (query, not a copy)" |
| Start here | "Equities are the furthest along." | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CHARTER.md | "A commodity physical-balance and curve decomposition is not." |
| Start here | Rates, FX and commodities are in scope, and undone work is labeled in the files. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/monitor/DATA.md | "Explicitly absent" "commodity inventories" |
| Who does the work | One person, called the principal, sets the questions and the standard of evidence. Older files say the operator. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/THE_ASK.md | "what the principal actually said, verbatim" |
| Who does the work | Older files say "the operator." | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/Third_Derivative_Concept_Map.md | "The operator's two illustrations" |
| Who does the work | "Claude (Anthropic) is the lead analyst. It writes the answer and, as …" | FALSE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CLAUDE.md | "Peers on research, never simultaneous" |
| Who does the work | Same bullet, on who writes findings. | FALSE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/RESEARCH_STATE.md | "Grok drafted; supervisor revised and adjudicated" |
| Who does the work | "Grok (xAI)" | UNVERIFIABLE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CLAUDE.md | "Grok 4.6" is named; "xAI" was not in the files fetched |
| Who does the work | "Gemini (Google)" | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CLAUDE.md | "Google's third Flash in six weeks" |
| Who does the work | They are "brought in from outside" and work from parcels. | STALE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/THE_ASK.md | "I connected GrokBot now to this folder" |
| Who does the work | "their job is to break the findings, not to confirm them." | FALSE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/RESEARCH_STATE.md | "in-house Sonnet agents plus a Gemini (agy) research lane" |
| Who does the work | "A finding stands only for as long as those attacks fail." | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CHARTER.md | "Survival of a review raises credence. It does not settle" |
| Who does the work | Instructions are verbatim in THE_ASK.md as E-000, E-001, and so on. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/THE_ASK.md | "NEVER PARAPHRASE INTO THIS FILE." |
| Who does the work | E-005 and E-007 are defined there. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/THE_ASK.md | "E-005" "E-007" both present |
| Who does the work | Grades are IDENTITY, MEASURED, BOUNDED or HYPOTHESIS. The default is HYPOTHESIS. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md | "The default grade of every claim below is HYPOTHESIS." |
| Who does the work | Surviving a review raises confidence and does not settle a claim. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CHARTER.md | "It does not settle the claim." |
| Who does the work | Retracted claims stay numbered C-001, C-002, and so on, and their wording is banned. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CORRECTIONS.md | "Append-only. Never delete an entry." |
| File guide | `2026-MM-DD-<code>-<Title>.md` notes, with the code in RESEARCH_STATE.md §5. | TRUE | https://api.github.com/repos/closeofbusiness/market-plumbing/contents/ | "2026-09-11-P2a-Return-Decomposition.md" exists |
| File guide | A later note says so when it supersedes an earlier one. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md | "Supersedes 2026-09-14-SYN-What-We-Can-Say.md" |
| File guide | `Parcel_*_For_Grok*.md` and `Parcel_*_For_Gemini*.md` are outside briefs. Replies are dated `…-Return.md` notes or under `_research/`. | TRUE | https://api.github.com/repos/closeofbusiness/market-plumbing/contents/ | "Parcel_A_Interlock_For_Gemini.md" and "2026-08-22-Parcel-A-Interlock-Return.md" |
| File guide | `Review_Prompt_For_*.md` are standing prompts for outside review. | STALE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CLAUDE.md | "historical — superseded by the dated topic parcels" |
| File guide | THE_ASK.md is the verbatim E-numbers. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/THE_ASK.md | "only the principal's own words" |
| File guide | RESEARCH_STATE.md is the live argument: settled, contested, assumptions, ranked open work. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/RESEARCH_STATE.md | "The live argument, what holds it up" |
| File guide | CALENDAR.tsv and HANDOVER.tsv are dated obligations and a machine-written handover log. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CLAUDE.md | "machine-written, append-only, one row per work parcel" |
| File guide | CLAUDE.md is the long operating manual for the agents. | TRUE | https://api.github.com/repos/closeofbusiness/market-plumbing/contents/CLAUDE.md | "size":69177 |
| File guide | `Third_Derivative_*`, `Shadow_Debt_*`, `Collateral_*`, and Funding_Identity_First_Principles.md are the two earlier workstreams. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CLAUDE.md | "The two workstreams" |
| File guide | `answer/` and `corrections/` are "One-line pointers." | FALSE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/answer/LIVE.md | "this file is a pointer" |
| File guide | dossiers/ and monitor/ are per-channel summaries, and the series the live claims use, with the next print. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/monitor/DATA.md | "Next print is from CALENDAR.tsv" |
| File guide | docs/ is the page GitHub Pages publishes. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/THE_ASK.md | "Pages now serves docs/ from main" |
| File guide | data/ and bin/ hold series.tsv, CSV tables, and the pull, compute, and check scripts. | TRUE | https://api.github.com/repos/closeofbusiness/market-plumbing/contents/data/p2a_decomposition | "decomp_cumulative.csv" |
| File guide | `_research/` is evidence, not the deliverable. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CLAUDE.md | "Raw agent output and evidence. Not the deliverable" |
| File guide | Analysis/ and Report/ are a forward-prediction register and HTML reports. | TRUE | https://api.github.com/repos/closeofbusiness/market-plumbing/contents/Analysis | "Forward_Prediction_Register.md" |
| File guide | Significant names absent from the table. | TRUE as a gap | https://api.github.com/repos/closeofbusiness/market-plumbing/contents/ | `requirements.txt`, `LICENSE`, `.gitignore`, and dated notes with no work-item code, including the Green notes, Guarantee-Stack, Oracle-RPO, and FERC-EL26. Analysis/ also holds `Input_Substrate_Forward_Thinkers.md`. |
| Where this came from | The working name is Third Derivative Research, "the name you will see on the page." | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/docs/index.html | "Third Derivative Research · the answer so far" |
| Where this came from | It began in August 2026 as two workstreams. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/Third_Derivative_Concept_Map.md | "Compiled: 2 August 2026." |
| Where this came from | A primary innovation first forces a reorganisation or an overcapacity, and later businesses capture most of the value. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/Third_Derivative_Concept_Map.md | "It first forces a reorganisation or builds an overcapacity" |
| Where this came from | Shadow-banking collateral and money creation are measured on the Pozsar–Singh nexus. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CHARTER.md | "Pozsar–Singh nonbank–bank nexus" |
| Where this came from | Where_The_Two_Workstreams_Meet.md joins the two. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CLAUDE.md | "The join." |
| Where this came from | On 11 September 2026 the principal widened the goal (E-003). The nexus work carries over as two channels. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/THE_ASK.md | "E-003 · 11 September 2026 — the goal, amended" |
| Glossary | the supervisor is Claude when it reviews another agent's work. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/THE_ASK.md | "You revise, you check, you adjudicate" |
| Glossary | A parcel is a one-pass brief to Grok or Gemini. | TRUE | https://api.github.com/repos/closeofbusiness/market-plumbing/contents/ | Parcel files for both models exist |
| Glossary | E-nnn and C-nnn are THE_ASK and CORRECTIONS entries. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/THE_ASK.md | "E-000" through "E-021" |
| Glossary | "B0 to B6 are the bridge designs, which try to measure how …" | FALSE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/RESEARCH_STATE.md | "Frame B0" and "P4 — the elasticity pilot (= Tier B B3)" |
| Glossary | Tiers N, O, B, T, A2 are nexus, outcome-side work, the bridge, tangents, and a persona capability awaiting a decision. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/RESEARCH_STATE.md | "pending a decision (Tier A2)" |
| Glossary | "A1 … A13" are the rows in RESEARCH_STATE.md §0. | STALE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/RESEARCH_STATE.md | "A14" "Done: the mission above." |
| Glossary | d1–d4 are September audit defects. d1 and d2 mark a note that names a deliverable that is not on disk. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/RESEARCH_STATE.md | "d1 Four docs cite scratchpad deliverables that are GONE" |
| Glossary | the gate is `bash bin/check.sh --all`. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/bin/check.sh | "bin/check.sh --all" |
| Glossary | The nexus is Pozsar and Singh, IMF Working Paper 11/289, 2011. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/THE_ASK.md | "WP/11/289, December 2011" |
| Glossary | z_k is nonbank wholesale funding W as a share of W plus M2. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-08-31-N2b-zk-The-Wholesale-Share.md | "z_k = W / (W + M2)" |
| Glossary | Published multiplier estimates run "roughly from 2 to 9.4," and there is no central value. | STALE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-11-P3-Price-Impact-Multiplier.md | "The 8.7-9.4 range appears in no paper checked." |
| Glossary | "the programme has no central value for it." | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-11-P3-Price-Impact-Multiplier.md | "carry NO central value." |
| Glossary | JVZ is Jiang, Vayanos and Zheng (2025, Review of Financial Studies), tested on free data. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-13-P5iii-Concentration-And-JVZ.md | "Jiang, Vayanos & Zheng (2025 RFS)" |
| Glossary | CSLT is a newer TIC securities dataset, Treasury notice of 21 May 2026. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/_research/2026-09-17-TIC-July-2026.md | "Treasury 21 May 2026 notice" |
| Glossary | Z.1 counts ETF share creation as equity issuance. Shapley split is an identity. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md | "counts ETF shares as issuance" |
| Checking the work | The gate checks bookkeeping. It takes one to two minutes. | UNVERIFIABLE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/bin/check.sh | "about 195 s of the 197 s a full --all run took" |
| Checking the work | The goal is identical in its three homes. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/bin/check.sh | "identical in THE_ASK.md, CLAUDE.md, RESEARCH_STATE.md" |
| Checking the work | "every top-level file and folder is indexed in CLAUDE.md (M5)" | FALSE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/bin/check.sh | "find . -mindepth 1 -maxdepth 1 -name '*.md'" |
| Checking the work | Every cited C-number has exactly one register entry (M7, M8). | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/bin/check.sh | "every correction number is used once." |
| Checking the work | No numbered to-do sits outside the ranked list (M6). | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/bin/check.sh | "outside the ranked fence" |
| Checking the work | Retracted wording is scanned in the notes outside `_research/` and on the page. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/bin/check.sh | "not -path './_research/*'" |
| Checking the work | "The exit code is always 0 by design, so it proves nothing." | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/bin/check.sh | "Exit 0 always." |
| Checking the work | "It has been run with macOS's own grep and with ugrep." | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/bin/check.sh | "ugrep rejects >1 bounded repeat" |
| Checking the work | A number is reproduced from the findings note, its script in bin/, and tables in data/. The earnings-share example is decomp_cumulative.csv. | TRUE | https://api.github.com/repos/closeofbusiness/market-plumbing/contents/data/p2a_decomposition | "decomp_cumulative.csv" |
| Checking the work | Python 3; most scripts are standard library; requirements.txt covers five spreadsheet scripts in bin/ plus numpy under `_research/`. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/requirements.txt | "Five scripts in bin/ read spreadsheets" |
| Checking the work | SEC EDGAR scripts need `SEC_UA`. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CLAUDE.md | "scripts read the SEC contact string from SEC_UA" |
| Checking the work | Shiller `ie_data.xls`, FRED DGS10 and DFII10, and Damodaran `ERPbymonth.xlsx` are not redistributed; `.gitignore` keeps them out. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/.gitignore | "this repository does not redistribute" |
| Checking the work | "US federal primary sources, which are public domain, are kept under `_research/primary_sources/`." | UNCERTAIN | https://api.github.com/repos/closeofbusiness/market-plumbing/contents/_research/primary_sources | The folder holds OFR PDFs. No fetched file says "public domain." |
| Checking the work | Older notes cite `<session-scratchpad>/`; before 9 Oct the path was `<session-scratchpad>`, since deleted. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CLAUDE.md | "35 distinct `<session-scratchpad>` paths" |
| Checking the work | `python3 bin/check_scratchpad_refs.py` lists remaining `/private/tmp/` paths. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/bin/check_scratchpad_refs.py | "SCRATCH = re.compile" matches "/private/tmp/claude-" |
| View the page | The page is online, published from docs/ on main. | TRUE | https://closeofbusiness.github.io/market-plumbing/ | "What Holds the Market Up" |
| View the page | "The page loads its fonts from Google Fonts." | UNCERTAIN | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/docs/index.html | CSS names "IBM Plex Sans" and Spectral. The converted fetch did not show a fonts URL. |
| View the page | "everything else is in the one file." | TRUE | https://api.github.com/repos/closeofbusiness/market-plumbing/contents/docs | only "index.html" |
| Provenance | Own write-ups are © closeofbusiness, CC BY 4.0. Third-party text is summarised, not copied. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CHARTER.md | "Do not republish verbatim copyrighted or paywalled" |
| Provenance | The SEC contact string, paywalled originals, correspondence, simulations of named people, and third-party datasets stay outside the repo. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/THE_ASK.md | "paywalled and copyrighted originals, correspondence" |
| Provenance | On 24 September 2026 nine files were removed, history was rewritten, and the repo was deleted and recreated. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/THE_ASK.md | "The principal deleted the repository. It was recreated" |
| Provenance | Old commits return 404. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/e2d0f8a/README.md | "404 Not Found" |
| Provenance | "GitHub keeps a deleted repository for 90 days, visible only to organisation owners." | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/THE_ASK.md | "keeps the deleted repository for 90 days" |
| Provenance | "Nothing else changed." | FALSE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/THE_ASK.md | "The README was rewritten as a front door." |
| Provenance | THE_ASK.md E-011 and E-013 record the details. | TRUE | https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/THE_ASK.md | "E-011" and "E-013" both dated 24 September 2026 |

Assumption: "one to two minutes" was not timed. The script's own 9 October note records about 197 seconds before the speed rewrite now in the file. Running `bash bin/check.sh --all` would settle it. "Public domain" would be settled by a sentence in the repo that those primary-source files are public domain. The Google Fonts claim would be settled by a `fonts.googleapis.com` link in the head of `docs/index.html`. "xAI" would be settled by that string in a repository file.

## LINKS

| Link text | Target | Exists? |
|---|---|---|
| What Holds the Market Up | https://closeofbusiness.github.io/market-plumbing/ | yes |
| docs/index.html | docs/index.html | yes |
| The answer note | 2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md | yes |
| CHARTER.md | CHARTER.md | yes |
| CHARTER.md#grades | CHARTER.md#grades | yes |
| dossiers/ | dossiers/ | yes |
| CORRECTIONS.md | CORRECTIONS.md | yes |
| THE_ASK.md | THE_ASK.md | yes |
| RESEARCH_STATE.md | RESEARCH_STATE.md | yes |
| CLAUDE.md | CLAUDE.md | yes |
| Where this came from | #where-this-came-from | yes |
| Checking the work | #checking-the-work | yes |
| answer/ | answer/ | yes |
| corrections/ | corrections/ | yes |
| monitor/ | monitor/ | yes |
| docs/ | docs/ | yes |
| data/ | data/ | yes |
| bin/ | bin/ | yes |
| _research/ | _research/ | yes |
| Analysis/ | Analysis/ | yes |
| Report/ | Report/ | yes |
| Third_Derivative_Concept_Map.md | Third_Derivative_Concept_Map.md | yes |
| Where_The_Two_Workstreams_Meet.md | Where_The_Two_Workstreams_Meet.md | yes |
| the N2b note | 2026-08-31-N2b-zk-The-Wholesale-Share.md | yes |
| decomp_cumulative.csv | data/p2a_decomposition/decomp_cumulative.csv | yes |
| LICENSE | LICENSE | yes |
| clone URL | https://github.com/closeofbusiness/market-plumbing.git | yes |
| localhost | http://localhost:8000 | not checked |

## MUST KEEP

1. Authority order. The answer note wins where the page disagrees. Each figure's findings note owns the number. `CORRECTIONS.md` is the register. `THE_ASK.md` holds the principal's words verbatim.
2. The question, the mission, and the scope: US equities, AI funding, the IPO boom, rates, FX, and commodities. Free data only. Own write-ups are CC BY 4.0, © closeofbusiness. Paywalled text is summarised. The SEC contact string, correspondence, persona simulations, and third-party datasets stay out.
3. The four grades and the default, HYPOTHESIS. A review raises credence and does not settle a claim. An identity is not evidence.
4. How to use the record. Search `## C-081`. `bash bin/check.sh --latest` prints the newest headings. `bash bin/check.sh --all` checks bookkeeping, including the page, and its exit code is always 0. The live page is https://closeofbusiness.github.io/market-plumbing/ and its source is `docs/index.html`.
5. Who actually works. The principal sets questions and adjudicates disagreements. Claude and Grok are peers in this repository. Claude, as supervisor, checks and adjudicates a delegated review. Grok and Gemini also scout and attack. In-house Sonnet agents run research too. Gemini's online-research lane is additional, not a substitute.
6. The start-here path: the page, the 17 September answer note, `CHARTER.md`, `dossiers/`, `CORRECTIONS.md`.
7. The map a reader needs: dated findings notes, `RESEARCH_STATE.md` §5 labels, parcels, `data/series.tsv`, `bin/`, and `_research/` as evidence rather than the deliverable. Equities are furthest along. Rates have reviewed first passes. FX and commodities have a 12 October measurement map, reviewed 13 October, and the files still name what is open.
8. Reproduction. Follow the findings note to `bin/` and `data/`. `requirements.txt` names the five spreadsheet scripts. Set `SEC_UA` before EDGAR calls. Shiller, Damodaran, and FRED DGS10/DFII10 are gitignored. Scratchpad paths under `<session-scratchpad>` are dead. `bin/check_scratchpad_refs.py` lists any that remain.
9. The 24 September 2026 provenance: nine private files removed, history rewritten, repository deleted and recreated, old commit `e2d0f8a` returns 404, and E-011 and E-013 are the record. The same day also rewrote this README and moved the page.
10. Glossary entries a citer needs: E- and C- numbers, the grades, z_k as W/(W+M2), the ETF wrapper, IMF WP/11/289 (2011), CSLT's 21 May 2026 Treasury notice, and no central multiplier. The adopted envelope in P3 is about $2 to $9.
11. The working name on the page: Third Derivative Research.

## REDUNDANT

- The mission sentence is already the canonical block in `THE_ASK.md`, `CHARTER.md`, `CLAUDE.md`, and `RESEARCH_STATE.md` §0.0.
- The four grades and the default are in `CHARTER.md`, the answer note, `answer/LIVE.md`, `CLAUDE.md`, and the page.
- "The note wins" and "dated rendering" are already on the page and in `CLAUDE.md`.
- "Restates almost no numbers" is repeated in the answer header, the `RESEARCH_STATE.md` ranked fence, the page, and `CLAUDE.md`. The answer body does not follow it.
- How to search corrections, and `--latest`, are already in `corrections/REGISTER.md` and the first-action block of `CLAUDE.md`.
- The principal, the supervisor, and the parcel are defined again in the glossary after "Who does the work." The page has its own, shorter cast list.
- CC BY 4.0 is in the opening, the provenance section, `LICENSE`, and the page footer.
- The page URL is given in Start here, the file-guide row for `docs/`, and View the page.
- The 24 September purge is told in full in E-011 and E-013. The README retells it and then adds "Nothing else changed," which E-012 contradicts.
- The two workstreams and their join are in `CLAUDE.md` under "The two workstreams" and in `Where_The_Two_Workstreams_Meet.md`. The third-derivative definition is the opening of `Third_Derivative_Concept_Map.md`.
- The gate's five checks, the exit code, and "read the check marks" are in `bin/check.sh` and again in `CLAUDE.md`.
- "No central multiplier" is the supervisor decision in the P3 note, answer §5, and the page ledger.
- What a dossier contains is the heading structure of the dossier files themselves. `commodities.md` does not use that four-part structure.

---

## Rung 4 review A: fidelity

I'll review the spec against the binding constraints and the repository files, starting with the local materials and the remote sources the spec depends on.The spec’s draft sentences and the About line need to be checked against the answer note’s grades and the corrections register. I’ll fetch those sources next.The answer note’s own later sections already narrow several sentences the spec would publish. I’ll check the ban list, the multiplier envelope, and the review dates those sentences depend on.The spec does not survive. Its file moves are usable. The sentences it would actually publish are not: they restore a summary the 13 October page has already marked retracted, and the success test requires that summary.

ATTACKS:

| item | spec section | what is wrong | evidence | severity | fix |
|---|---|---|---|---|---|
| About line states an ungraded finding | §2 primary; constraint 4 and constraint 1 | The field cannot carry a grade or a link. The primary sentence still states a result: earnings and the risk premium, not cheaper money, and a shrinking float of US equities. Constraint 1 allows the README to state the answer in words and requires any number to be dated and linked to its owner. It does not allow a second, undated, unlinked copy in the About field. The fundamentals dossier grades that explanatory claim a hypothesis. The live page retracts the premium attribution. “US equities” also drops the wrapper. Operating companies retired equity. The fund layer grew. | `dossiers/fundamentals-benchmark.md`: “Sized for the recent US equity window, and still a hypothesis under the charter.” Page ledger: “The premium, not rates, held the multiple up \| Retracted.” Page: “what grew was the fund layer on top of company stock, not company stock itself.” https://closeofbusiness.github.io/market-plumbing/ | blocking | Implement the alternative noun phrase, or a record-keeping line with no finding. Do not put “risk premium,” “not cheaper money,” or “shrinking float” in the About field. |
| Risk-premium sentence is the retracted summary | §4 row 2; SC-1 | The draft says the multiple “was held up by a compressing risk premium … not by cheaper money.” The page’s own diagnosis is that one-line summaries outran their sources, and it names the premium as one of those four. The same page now says calling it a compressing risk premium “adds less than it seems,” grades “Cheaper risk versus better growth” as Hypothesis, and says it would not state that the premium was “cheaper risk.” The answer note’s §1 agrees: the premium is defined as earnings yield minus the real yield (C-102), and the cheaper-risk versus growth split is withdrawn (C-082). The identity caveat is optional, and SC-1 does not require it. SC-1 does require “not by cheaper money.” C-035’s correct position is that the risk-free rate alone cannot explain multiples, and that the discount-rate account is untested, not refuted. | Answer note §1 and the one-paragraph, https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md. Page: “Calling that a ‘compressing risk premium’ adds less than it seems” and “Summaries stronger than their sources … the shadow-money verdict, the premium.” https://closeofbusiness.github.io/market-plumbing/ | blocking | Publish the measured observation only: earnings did most of the rise; the earnings yield barely moved while real yields rose. Point the premium reading at the answer note. Delete “not by cheaper money” from SC-1. |
| Shadow-money negative covers the whole window | §4 row 4 | “Are not where the equity money came from over this window” drops “the original hypothesis centred on” and leaves “this window” unqualified. The dossier and the page limit the failure to 2024 and keep a ceiling over 2024–26 (C-118). | `dossiers/shadow-money-and-wholesale-repo.md`: “Failed as the 2024 source of the equity bid. Re-test as a …” Page: “shadow money did not in 2024 — though over the whole window …” | blocking | Say the 2024 wholesale-repo increase was a reverse-repo handoff, and that the full window is not ruled out. |
| “Collateral re-use did not rise” | §4 row 4 | Intensity did not rise. The permitted stock grew. Volume and intensity are different claims. | `dossiers/collateral-reuse.md`: “The permitted stock grew about 24%, so the growth is in volume, not intensity.” Page channel table: “Collateral re-use intensity did not rise.” | blocking | Keep the word “intensity.” |
| “A measurement, not a cause” | §4 row 3; SC-1 | The note says “a measurement result, not an economic one,” and that the price effect is unmeasured. The page adds that the closed designs do not show that “money did not move prices.” “Not a cause” reads as that denial. SC-1 requires the stronger phrase. | Answer note, one-paragraph. Page bridge section: “so ‘money did not move prices’ is not what this shows either.” | blocking | Use “measurement result, not an economic one” and “the price effect is unmeasured.” Change SC-1 to those words. |
| “The IPO boom is largely one deal” | §4 row 6 | The note’s range is half to two-thirds, depending on the census. Half is not “largely.” The dossier grades the claim Hypothesis. The spec drops both the range and the census dependence, which is how a figure is smuggled back in as a stronger word. | Answer note §3a: “two-thirds of it one deal … On Renaissance Capital’s broader census … …” `dossiers/ipo-boom.md`: “Status … Hypothesis.” | blocking | Do not characterize the share. Say the answer note’s §3a compares two censuses, and give no adjective for the size. |
| Citation names the page as the answer note | §3 Scope | The verbatim citation calls “What Holds the Market Up” the answer note and sends the reader to the page. That title is the page. The note is “what is driving asset prices, and where the money came from,” dated 17 September 2026. The spec’s own rule is that the two can disagree and the note wins. | Answer note title, fetched above. Page: “A dated rendering of 2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md, which is the authority.” https://closeofbusiness.github.io/market-plumbing/ | blocking | Cite the note by its title and repository path. Cite the page separately, as a rendering. |
| M5 description is false | §6 fact-fix; `REPRODUCE.md` outline | The “corrected” sentence says the check does not cover every file and folder, and that it only indexes top-level markdown. The script checks every top-level `*.md` file and every top-level directory. It does not check other top-level files. | `bin/check.sh`: `find . -mindepth 1 -maxdepth 1 -name '*.md'` and `find . -mindepth 1 -maxdepth 1 -type d`; success line “every top-level doc and folder has a read-table row.” https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/bin/check.sh | blocking | Say M5 checks top-level markdown files and top-level folders, and does not check other top-level files. |
| Shiller script pointer becomes false | §5 “Leave that pointer” | `decomp_sp500_shiller.py` points at README “Checking the work” for where to download Shiller and FRED, not for the gate. Those download instructions move to `REPRODUCE.md`. Leaving the pointer keeps a path that no longer says what the script says it says. The same section’s other rule would replace a third-party-download pointer with `REPRODUCE.md`. The exception overrides that rule for the one script that needs it. | Script docstring: “download them to this folder first — README, ‘Checking the work’.” https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/bin/decomp_sp500_shiller.py | blocking | Change that comment to `REPRODUCE.md`. Do not treat “the heading still exists” as keeping the pointer true. |
| Envelope dated 11 September | §6 Market terms | The 11 September decision was a central value of 5, and it was retracted. The “$2 to $9” envelope is the 12 September revision. The glossary would also be a second copy of a figure, which is the C-081 pattern. The page already carries “$2–$9 published (C-077).” | P3 note: “REVISED 12 Sep” and “The 11 Sep decision — M = 5 as the centre … is retracted.” “span roughly $2 to $9.” https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/2026-09-11-P3-Price-Impact-Multiplier.md | should fix | Leave the number in the P3 note. If a glossary phrase is kept, date it 12 September 2026 and link that note. |
| “11 September 2026 … became the goal” | §3 Where this came from | The charter says the standing goal text was asked for on 25 September 2026 (E-015) and confirmed on 26 September (E-016), built from earlier wording including E-003. “Became the goal” on 11 September dates the canonical goal too early. | `CHARTER.md`: “the principal asked for it on 25 September 2026 … confirmed this …” https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/CHARTER.md | should fix | Say E-003 amended the goal on 11 September, and the standing wording was fixed on 25–26 September. Link `THE_ASK.md`. |
| AI sentences are a gloss the spec already flags | §4 row 5 | “Who does not fit that pattern” and “the financing that is new” are not the note’s words. The dossier’s status is “Hypothesis,” while “mostly” is the note’s word. “That is new” adds a novelty claim. The page says “the real financing innovation.” | Spec §4 marks the gloss UNCERTAIN and still orders it published. `dossiers/ai-funding.md`: “Mostly self-funded. Hypothesis.” | should fix | Keep “funded mostly from operating cash flow” and “off-balance-sheet lease commitments.” Delete the two gloss sentences. |
| “Have closed” omits C-117 | §4 last paragraph | The page retracts “closed for good, at any budget.” One leg is the furthest from reopening, not a permanent closure. | Page ledger: “The payment-day test is closed for good, at any budget \| Retracted.” | should fix | If the clause stays, say the designs have closed for stated reasons and that one is not a permanent closure, with no count. |
| 13 October review is a dated status with the outcome stripped off | §3 Scope | A review on that date is real. The sentence groups foreign exchange and commodities and stops at “reviewed.” The page says the rates and FX claims of that map were reviewed the same day and one fell (C-136); commodities claims were reviewed the same day, one fell (C-141), two were corrected (C-142). The rates dossier also has externally reviewed first passes from 27 September, plus an 11 October review of the 8 October additions. “First passes” remains true and is already incomplete. | Page, “The honest gaps.” `dossiers/rates.md`: “first pass done and reviewed (R1, R2, 27 Sep 2026).” `dossiers/cross-border-and-fx.md` records the 12 October map and its status is still “Open.” | should fix | Name the map, the date, and that the review withdrew or corrected claims. Point at the dossiers for what still stands. |
| Link search does not cover the tree the gate scans | §5 grep | `bin/* docs/* *.md` misses `dossiers/`, `answer/`, `corrections/`, `monitor/`, `Analysis/`, and `Report/`. The answer note is top-level, so its `README.md#glossary` link is in scope, and that retarget is specified. `bin/*` does see every script. Whether a glossary link sits in a missed directory is UNCERTAIN. `Shadow_Debt_*` and `Collateral_*` are not resolvable link targets. SC-4 requires a real path. | Answer note: “explained in the [README glossary](../README.md#glossary).” `bin/check.sh` scans `find . -maxdepth 2 -name '*.md'`. | should fix | Search all in-repo markdown and HTML. Link concrete filenames, or name the two streams without a glob link. |
| “Calculates” | §3 Evidence | The note points claims at the findings note that owns them. Not every claim is a calculation. | Answer note header: “that doc is the authority.” | should fix | Say “owns,” or “the findings note named beside the claim.” |
| Page URL is required in three places | §3 Start here, §3 Scope citation, §4 | Start here says the page URL appears there and in the answer section and nowhere else. The verbatim citation in Scope contains the same URL. | Spec §3 and §4. | minor | Allow the citation URL, or make the citation a repository path and keep a single page URL. |
| Optional answer clauses can break the 260-word ceiling | §3 answer budget; §4 | The seven mandatory sentences fit. Adding the preferred “have closed” clause, the optional identity sentence, and the heading words goes past 260. | Counted from the draft sentences in §4. | minor | Raise the answer ceiling or drop the optional sentences from the first screen. |
| “A major innovation” | §3 Where this came from | The concept map says “a primary innovation or shock,” then retracts pieces of the value-capture story in that same file. | `Third_Derivative_Concept_Map.md` §1 and §3 (R1–R3). https://raw.githubusercontent.com/closeofbusiness/market-plumbing/main/Third_Derivative_Concept_Map.md | minor | Quote the map’s opening clause and say the map records its own retractions. |
| “Smaller Claude models” | §3 Who did the work | The binding line is that in-house Claude subagents, Sonnet and Haiku, do bounded tasks. “Smaller” is not that fact. | `verified_facts_and_constraints.md`, Roles. | minor | Say in-house Claude models do bounded tasks. |

Constraint 1, planned text that copies a figure, a count, or a dated status:

- The About line. No date and no owner link. It is already behind the 13 October page. It goes stale again at the next in-place edit of the note, and the window fact moves with the next Financial Accounts release, which the page dates at about 11 December 2026.
- `2024:Q1–2026:Q2` on the retirement sentence. Same release, about 11 December 2026. The page already says non-financial corporates turned to net issuing in the first half of 2026, so the cumulative “shrinking” result is eroding inside the current window.
- “Reviewed on 13 October 2026” for foreign exchange and commodities. The date is a real event. As a description of where that work stands, it is already missing C-136, C-141, and C-142, and it goes stale at the next outside review. The page’s calendar runs from late October to about 11 December.
- “Rates have externally reviewed first passes.” Undated. Still true of R1–R3, and already behind the 11 October review of the 8 October additions. Incomplete at the next rates pass.
- “About $2 to $9” in the glossary. A copied envelope. The previous centre was retracted one day after it was set. Stale at the next multiplier correction.
- “About 15 seconds,” written into both the README and `REPRODUCE.md`. The script’s 9 October note records a prior full run of about 197 seconds before the rewrite. The new duration will drift as the scanned tree grows. Weeks, not a fixed date.
- “Have closed,” with no count. C-117 has already softened one leg. A further reopening is not imminent. The page’s reopen trigger for that leg is years out.

Not copied, and that part is right: 71.0%, 82.3%, the corrections count (the page currently shows 142), “three of the five,” and “half” / “two-thirds” as numerals.

Constraint 2 and 3: `GLOSSARY.md` and `REPRODUCE.md` both get a `CLAUDE.md` read-table row. No new top-level file is left unindexed. The answer-note glossary retarget is specified. The miss is the Shiller pointer above, plus the non-recursive search. UNCERTAIN: any `README.md#glossary` link under `dossiers/`, `answer/`, `corrections/`, or `monitor/`.

Killed wording: `CORRECTIONS.md` was fetched. The return ends in C-060. `bin/check.sh` reads the ban list from a ` ```banned ` fence, which was past that truncation, so the exact regexes are UNCERTAIN. The live page’s retraction ledger is enough for the sentences at issue. The spec would republish “held up by a compressing risk premium … not by cheaper money,” which that ledger lists as retracted. Open question 7 tells the writer to wait for the gate instead of checking. SC-7 does not forbid those phrases, so the spec’s own pass test would accept them.

RE-DERIVED: First-screen source lines through the planned answer. The draft opening is 5 source lines. The seven §4 sentences, one source line each, with a blank line between paragraphs, end on source line 20. Adding the optional identity sentence as its own paragraph ends on line 22. Spec’s ceiling is line 25. The line budget holds. The About-line hand count was also recomputed: spec 134 characters including the period; recount 134. The alternative’s 127 also matches.

VERDICT: Does not survive. The glossary move, the reproduce move, the index rows, and the refusal to copy percentages or the corrections count are sound, but executing §2, §4, and SC-1 would publish a retracted premium attribution, a false collateral sentence, a window-wide shadow-money negative the note’s own C-118 rejects, and an About line that states those findings with no grade and no owner.

LOAD-BEARING ASSUMPTION: The one-paragraph is the note’s current graded answer, so copying it, and compressing it into the About line, cannot be stronger than the note.

---

## Rung 4 review B: reader experience and upkeep

I'll read the spec and the binding notes in this folder, then judge the front page they would produce for readers and for upkeep.The spec does not survive as written. It would put a real answer on the page, and it would still misquote that answer, bury it under apparatus, and make the owner keep a second copy.

Assumption used throughout: a careful reader covers about 125 words in 30 seconds, and GitHub shows the About line plus the top of `README.md` before any scroll. The spec’s “first screen” is source lines 1–25 with wrapping forbidden, so those lines can hold the whole answer. Viewport height is UNCERTAIN; the word position of each claim is not.

## READER

**(a) Central-bank economist, 30 seconds.**

Takeaway from what is actually in front of them: a four-market question, then a label, then a citation rule, then the earnings sentence. “Unmeasured” is about word 150 of the defined first screen (opening 32 + heading 4 + authority 34 + earnings 26 + the money paragraph through its last word). The shrinking-float sentence sits just before that. Both are past a half-minute read. Equities are the furthest along only from line 26 onward, after the opening has already named bonds, currencies, and commodities. The citeable working name sits in that same later section.

What still grates: the result is not the first thing under the question. The spec’s own opening is:

> Market Plumbing is a public research record on that question. It follows equities, government bonds, currencies and commodities.

Then the answer is required to begin:

> As of 17 September 2026, updated in place. The answer note is the authority. The page What Holds the Market Up is a dated rendering of that note; where they disagree, the note wins.

“On that question” is the school-project label with “notebook” swapped out. “Updated in place” makes “as of 17 September 2026” a date that is not the revision date. The grade sermon is on this same screen, with no grade printed beside any claim:

> Grades come from the answer note: identity (true by construction, not evidence about the world), measured, bounded, or hypothesis (the default). A review does not settle a claim.

Fix: the first words under the question should be the earnings sentence and the money paragraph through “unmeasured,” in the answer note’s wording. Move the authority rule, the grade legend, and the four-market status off that screen. Say in the opening sentence that the priced result is the equity result.

**(b) Journalist who might quote it.**

Takeaway: the About line, which GitHub prints above the README. They can lift “not cheaper money” and “a shrinking float of US equities” as what holds prices up, with no date and no “unmeasured.” If they reach the README, the sentence that wants quoting is usable: “What the multiple added was held up by a compressing risk premium …” The sentences they will also quote are the glosses.

What still grates. The note says the money-side headline “is a measurement result, not an economic one,” and that the price effect cannot be sized. The spec substitutes:

> The money-side result is a measurement, not a cause.

The note says the IPO boom “is between half and two-thirds a single deal, depending on the census (SpaceX).” The spec substitutes:

> The IPO boom is largely one deal (SpaceX).

The note names who breaks the “mostly” on AI funding. The spec substitutes a tease, which it marks UNCERTAIN as a gloss:

> The answer note records who does not fit that pattern.

“Largely” and “not a cause” are stronger than the note, and they are the quotable versions. Lower on the page, this stays available to quote with no explanation:

> simulations of named people

The tone rules do not remove the owner’s complaint. They ban a phrase list (“on purpose”, “not to confirm”, “proves nothing”, “nothing else changed”, “you don’t need”) and a nickname list. The habit those phrases came from is still required copy: correcting a reader who has not spoken. The new page still mandates “A review does not settle a claim,” “It always exits 0. Read the check-mark lines,” and:

> The folder does not use one template of hypothesis, status, evidence, and what would change the claim.

A new visitor has never seen that template. The voice moves from clubhouse slang to a press office that pre-empts the objection, withholds the exception, and explains the grading system before it shows a grade.

Fix: quote the note, or link it. Do not print “largely,” “not a cause,” or “who does not fit.” Keep “simulations of named people” out of the README.

## LENGTH AND ORDER

900 words and 85 lines are the wrong target. They are large enough to pass a line-count test while rebuilding the manual. The ceilings sum to 900, and the required sentences already total about 790 (UNCERTAIN only in the sense that the writer could add a few words of connective tissue). About 540 of those words come after the answer. Lines 1–25 are an accounting screen: with hard-wrapping forbidden, seven long paragraphs fit in the line budget and still read as a full page. The old page’s fault was jobs, not only line count.

| Section | Verdict | Why |
|---|---|---|
| Opening | Keep, cut the second paragraph | The question is the right first line. “Public research record on that question” spends the first screen on a label and implies all four markets share one result. |
| The answer so far | Keep a short version; cut the lead and the legend | Authority-first order spends the half-minute on “the note wins.” The grade legend explains tokens the page does not print. Earnings, risk premium, ETF wrapper, shrinking float, and “unmeasured” are the section. |
| Scope and how to cite | Keep, merge licence and the one removal sentence into it | This is the citation, the byline, and the “equities are furthest along” warning the first screen currently omits. “The repository is Market Plumbing” repeats the title. |
| Start here | Keep the three doors; cut the command and the template denial | The page, the answer note, and `dossiers/` are the doors. `docs/index.html`, the local server, and the sentence about a template the reader has not met are the old navigation lesson. |
| Evidence | Merge into Start here as one sentence | It restates the same trail: note, script, table, `CORRECTIONS.md`, `REPRODUCE.md`. |
| Who did the work | Keep two sentences; cut the rest | AI authorship belongs. “One person directs it and sets the standard of evidence” is the empty grandeur with the nickname deleted. “Smaller Claude models do bounded tasks” is an operating note. |
| Where the files are | Cut | Five destinations already covered by Start here, Evidence, and `GLOSSARY.md`. “A later note says when it supersedes an earlier one” explains the obvious. `dossiers/` and `CORRECTIONS.md` would appear again. |
| Where this came from | Cut | The required theory sentence is still unreadable: “a major innovation first forces a reorganisation, or builds more capacity than …” The second stream is still a measurement with no result. The 11 September goal-change is a diary. |
| Checking the work | Cut from the README after the one script pointer moves | “The bookkeeping gate,” “It always exits 0,” and “Read the check-mark lines” are the self-cancelling check in formal clothes. It is on this page so `bin/decomp_sp500_shiller.py` can keep a heading. The spec already retargets other pointers to `REPRODUCE.md`. |
| Provenance and licence | Cut as a section; keep one removal sentence inside Scope | The 24 September fact can be one sentence and a link. The second licence discussion splits CC BY away from the heading that says “licence.” The E-numbers are the file nicknames section 1 says belong in `GLOSSARY.md`. |

What would remain: question, equity answer in the note’s words, one citation block (names, how far the other markets have got, CC BY, one removal sentence), three links. That is a page a visitor can finish.

## UPKEEP

The spec avoids the weekly correction count and the moving percentages. It then copies the living answer. The note is “updated in place,” and the verified facts say the correction count changes often. Any month the answer paragraph or a market’s stage changes, this README has to change too. Inferred rate, UNCERTAIN, from the October record (a map on 12 October, a review on 13 October, corrections changing often): **1–2 README edits in a month when the work is moving, plus the GitHub About field on the same commits.** A quiet month can be zero. That is not near zero over a year.

| Sentence the spec would lock in | What forces an edit | Edits per month (UNCERTAIN) | How to avoid it |
|---|---|---|---|
| “As of 17 September 2026, updated in place.” | A new answer file. In-place edits do not force a change, so the quoted date goes stale while the prose moves. | 0, and that is the defect | Do not put “as of” on a file that is revised in place. Point at the note. |
| Earnings, risk premium, “not by cheaper money.” | Any change to that result, or a new ban that hits the sentence (the spec’s own open question 7). | 0–1, bundled with any answer revision | Leave it only in the note. |
| “measurement, not a cause”; ETF wrapper; “2024:Q1–2026:Q2”; shrinking float; “unmeasured”; “have closed.” | A new Z.1 quarter extends the window. A new price-effect design reopens “have closed.” A measured effect retires “unmeasured.” | The window alone is about one edit a quarter; the status clauses move when that work moves | “The note’s money-side measurement” with no window and no status adverb. |
| “The verdict is mostly negative… Wholesale-repo growth in 2024… collateral re-use did not rise.” | A later window, or a channel that stops being negative. “Across the channels the goal names” also goes false when FX or commodities get a positive result the sentence never mentioned. | 0–1 | Delete. The note owns it. |
| “funded mostly from operating cash flow” / “who does not fit that pattern” / “off-balance-sheet leases.” | The exception set changes. The gloss can stay true while becoming more misleading, so it may not be edited when it should. | 0–1 | Delete the gloss. |
| “largely one deal (SpaceX).” | The census share changes, or SpaceX stops being the deal that dominates it. | 0–1 | Delete. |
| Grade legend. | A change to the grade names or to “a review does not settle a claim.” | Near 0 | `CHARTER.md` only. |
| “Equities are the furthest along. Rates have externally reviewed first passes. Foreign …” | The next review, the next map, or another market catching up. These dates were already born and revised on consecutive days. | 1 in an active month | “Each market file states how far it has got.” No stage, no date. |
| Citation naming the 17 September 2026 note, and the filename in Start here. | A replacement note. | Near 0 under update-in-place | One link, no restated date. |
| “about 15 seconds.” | The script gets slower. This timing has already gone stale once (“one to two minutes”). | Near 0, then a surprise | Say it only in `REPRODUCE.md`, or do not say it. |
| About line: “earnings and the risk premium, not cheaper money, and a shrinking float of US equities.” | Any of those three claims moving. Same trigger as the answer, second place to edit. | Same as the answer block | Use the alternative line, which has no finding. |

Sentences that can sit still: the question, the licence, the 24 September removal, the August and 11 September origin (if kept), the file map, the SEC contact placeholder, and “Claude and Grok work as peers,” unless the roster changes.

Near-zero version: the README is a door. It asks the question, names the note and the page as the only answer, gives the citation and the licence, and links `REPRODUCE.md`. Market progress lives in the dossiers, which the spec already says state their own status. The owner then edits the note, not a paraphrase of the note.

## ABOUT LINE

**Primary** (“Research record on what holds asset prices up: earnings and the risk …”). Hand count 134 matches a recount, including the period, and it is under 160. A visitor under the repo title reads a finished conclusion. “Shrinking float” is placed in the “what holds prices up” slot. The answer the spec itself requires says that buying met a shrinking float and that the price effect is unmeasured. The risk-premium clause is missing the part that makes it economics: the premium compressed against rising real rates. There is no “mostly,” no date, and no grade. Section 2 says this line and the README answer must agree. They do not. It is also the line a journalist can quote without opening the file.

**Alternative** (“Research record on what holds asset prices up and whose money is …”). Hand count 127 matches a recount. A visitor reads a question and four markets. Nothing there can be quoted as a cause. Nothing there has to be edited when the equity result moves. It still says “research record,” so it does not brief the result. That is what a field this short can honestly hold.

Ship the alternative. The primary is a finding in a slot that cannot carry the note’s hedges, which is the rejection test the spec already wrote down.

## RE-DERIVED

Counted the draft answer the writer is told to use verbatim: heading text plus the seven sentences in the section 4 table. Method is the spec’s own: drop the hashes, count whitespace-separated words, no extra link text beyond those sentences. The preferred “have closed” clause and the optional identity sentence are extra.

| Piece | Words |
|---|---|
| Heading “The answer so far” | 4 |
| Authority and date | 34 |
| Earnings and risk premium | 26 |
| Money side through “unmeasured” | 54 |
| Channels, repo, collateral | 55 |
| AI funding | 29 |
| IPO | 16 |
| Grade legend | 32 |
| **Mandatory total** | **250** |
| Spec’s ceiling | **260** |
| Preferred clause “attempts to measure the price effect have closed” | +8 → **258** |
| Optional “The split holds by construction…” | +14 → **264**, or **272** with both extras |

The mandatory draft fits by 10 words. The path the spec prefers if the note calls the split an identity does not fit. Opening, counted the same way, is 32 words against a budget of 45.

## VERDICT AND LOAD-BEARING ASSUMPTION

It does not survive. Moving the glossary and the reproduction essay, deleting the cast list, and refusing copied percentages are the right repairs. The page those rules actually specify is still a ten-section manual, the first screen still opens with a label and a precedence rule, and the sentences a journalist will quote are already stronger than the answer note.

Load-bearing assumption: **section 4’s sentences are the answer note’s words and no stronger, so they are safe to put where they will be quoted and safe to leave standing while that note is updated in place.** That assumption is already false on the drafts (“not a cause,” “largely one deal,” the About line’s float-as-support). If it stays false, the front page is a second source of truth, which is the failure C-081, C-089, and C-092 already recorded, moved from figures into sentences.

---

## Rung 7 cold reader: economist (first draft)

I'll read only `README.md` and answer from that page.1. "What is holding asset prices up, and whose money is behind it?" It starts with US equities, then government bonds, currencies and commodities.
2. The current answer is the page "What Holds the Market Up". It renders `2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md`, which "is the authority wherever the two differ."
3. Each claim is graded IDENTITY, MEASURED, BOUNDED, or HYPOTHESIS, as defined in `CHARTER.md`. "Most claims remain hypotheses until they are tested." Failed claims "are withdrawn and kept on record in CORRECTIONS.md, rather than deleted."
4. "AI models do the research and the writing: Claude (Anthropic) and Grok …" "One person directs the work and sets the standard of evidence." That person is not named. The working name is Third Derivative Research; the byline is closeofbusiness.
5. The write-ups are © closeofbusiness, under CC BY 4.0 (`LICENSE`); reuse requires attribution. Cite the note as "The answer — what is driving asset prices, and where the money came from", `2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md`. Cite the page "What Holds the Market Up" separately, as the rendering of that note.
6. Yes.
"Each file in [dossiers/](../dossiers/) states how far its line of work has got."
"How to recompute a figure, run the record's checks and fetch the …"
7. "On 24 September 2026 nine files that should not have been published …" It admits the archive was rewritten and files were removed, but does not say what those files were or why.
8. Yes, I would treat the front page as serious record-keeping of unfinished work: it states a question, grades claims, keeps a corrections file and names an authoritative note, and it also says that AI models do the research and the writing under one unnamed person and that the repository history was rewritten on 24 September 2026.

---

## Rung 7 cold reader: journalist (first draft)

**Cited but not fetched (not relied on):** https://closeofbusiness.github.io/market-plumbing/

I'll read only `README.md` and judge the project from that front page.1. The project asks: "What is holding asset prices up, and whose money is behind it?" It starts with US equities and extends to government bonds, currencies, and commodities as the work reaches them.

2. The current answer is the page "What Holds the Market Up" (https://closeofbusiness.github.io/market-plumbing/). That page renders the answer note `2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md`, "which is revised in place and is the authority wherever the two differ."

3. Each claim is graded IDENTITY, MEASURED, BOUNDED, or HYPOTHESIS, with the definitions in `CHARTER.md`. "Most claims remain hypotheses until they are tested." Claims that fail "are withdrawn and kept on record in CORRECTIONS.md, rather than deleted." The record uses free public data only.

4. "AI models do the research and the writing: Claude (Anthropic) and Grok …" The working name is Third Derivative Research. The byline is closeofbusiness.

5. The repository's own write-ups are "© closeofbusiness" and "licensed under CC BY 4.0" (text in `LICENSE`). "Reuse requires attribution." Cite the answer note by title and path: "The answer — what is driving asset prices, and where the money came from", `2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md`. Cite the page "What Holds the Market Up" separately, "as the rendering of that note." Third-party data and paywalled text are summarised and cited, and they are not redistributed.

6. None.

7. "On 24 September 2026 nine files that should not have been published …" It admits a rewritten history and removed files without saying what they were or why they should not have been published.

8. The front page is serious in form — a named question, an authoritative note, claim grades, a corrections register, and a citation rule — but it is not quotable as established fact, because it says most claims are still hypotheses, the editor is an unnamed person, and the repository history was rewritten.

---

## Rung 7 cold reader: economist (after fixes)

**Cited but not fetched (not relied on):** https://closeofbusiness.github.io/market-plumbing/

I'll read only `README.md` and judge the project from that front page.1. “What is holding asset prices up, and whose money is behind it?” The answer note’s title puts it differently: “what is driving asset prices, and where the money came from.”

2. The current answer is the page “What Holds the Market Up” (https://closeofbusiness.github.io/market-plumbing/). It renders `2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md`, which “is revised in place and is the authority wherever the two differ.”

3. Every claim is graded IDENTITY, MEASURED, BOUNDED, or HYPOTHESIS; the definitions are in `CHARTER.md`, not here. “Most claims remain hypotheses until they are tested.” “Claims that fail are withdrawn and kept on record in CORRECTIONS.md, rather than deleted.” The record uses free public data only.

4. “AI models do the research and the writing: Claude (Anthropic) and Grok …” That person is not named. The working name is Third Derivative Research; the byline is closeofbusiness.

5. Cite the note as “The answer — what is driving asset prices, and where the money came from”, `2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md`. Cite the page “What Holds the Market Up” separately, as the rendering of that note. “The repository's own write-ups are © closeofbusiness and are licensed under CC BY 4.0.” Reuse requires attribution. Third-party data and paywalled text are summarised and cited, and they are not redistributed.

6. No. None.

7. “On 24 September 2026 nine private files (correspondence and draft briefings that …” It is missing the comma after the date, and E-011 and E-013 are undefined on this page.

8. Yes: the page states a question, one authoritative note, claim grades, a corrections file, a citation form and CC BY 4.0, and it discloses the model authors and a removal of private files.
