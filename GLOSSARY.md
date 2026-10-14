# Glossary

Definitions for the roles, codes, market terms, and file-name patterns used in this repository.

## Roles

| Term | Meaning |
|---|---|
| the principal | The person who directs the work and rules on scope and the standard of evidence. Older files say the operator. The public byline is closeofbusiness. The working name is Third Derivative Research. |
| Claude and Grok | Claude and Grok are peers on the research. They are not in the folder at the same time. The principal routes the work ([THE_ASK.md](THE_ASK.md), E-006, 15 September 2026). [CLAUDE.md](CLAUDE.md) calls Grok by the name GrokBot. |
| the supervisor | Whichever of Claude or Grok is reviewing the other's work. That reviewer revises, checks, and adjudicates ([THE_ASK.md](THE_ASK.md), E-008). It is not a standing job title. |
| Gemini (Google) | Consulted for reading and online research. That lane is additional to the work Claude and Grok do. In-house Claude models, Sonnet and Haiku, do bounded tasks. |
| parcel | A self-contained brief written to be answered in one pass. Replies are dated notes ending in `-Return.md`, or files under `_research/`. |

## Codes

| Code | Meaning |
|---|---|
| E-*nnn* | One verbatim instruction in [THE_ASK.md](THE_ASK.md), numbered from E-000. |
| C-*nnn* | One retracted claim in [CORRECTIONS.md](CORRECTIONS.md): the claim, why it was withdrawn, and the wording now banned. Search a heading such as `## C-081`. `bash bin/check.sh --latest` prints the newest headings. |
| P2a, N2c, D8b | Work-item labels in [RESEARCH_STATE.md](RESEARCH_STATE.md) §5. The first note on an item usually carries the label in its file name. |
| Frame B0; P4; Tier B B3 | [RESEARCH_STATE.md](RESEARCH_STATE.md) uses Frame B0. It identifies the elasticity pilot as P4, also called Tier B B3. |
| Tier N, O, B, T, A2 | Groups of work in [RESEARCH_STATE.md](RESEARCH_STATE.md) §5: the nexus, outcome-side work, the bridge, tangents, and a persona capability that is pending a decision. |
| A-numbers | Rows of the table of asks in [RESEARCH_STATE.md](RESEARCH_STATE.md) §0. |
| d1, d2, d3, d4 | Defects from the September 2026 document audits, labelled in the order found. d1 and d2 mark a note that names a file that is not on disk. |
| the gate | `bash bin/check.sh --all`. Described in [REPRODUCE.md](REPRODUCE.md). |
| IDENTITY, MEASURED, BOUNDED, HYPOTHESIS | The four grades a claim can carry. The default is HYPOTHESIS. Definitions are in [CHARTER.md](CHARTER.md#grades). |

## Market terms

| Term | Meaning |
|---|---|
| nexus | The nonbank–bank nexus: nonbanks funding banks and dealers, and the collateral that moves between them (Pozsar and Singh, IMF Working Paper 11/289, December 2011). |
| z_k | The wholesale share: nonbank wholesale funding W as a share of W plus M2, so z_k = W / (W + M2). See [the N2b note](2026-08-31-N2b-zk-The-Wholesale-Share.md). |
| M, the multiplier | Dollars of market value per dollar of net buying. The programme has no central value for M. The published envelope is in the [P3 note](2026-09-11-P3-Price-Impact-Multiplier.md). |
| JVZ | Jiang, Vayanos and Zheng, 2025, *Review of Financial Studies*, on passive investing and mega-firms. See [the P5iii note](2026-09-13-P5iii-Concentration-And-JVZ.md). |
| Z.1, EFA | The Federal Reserve's Financial Accounts of the United States, and its Enhanced Financial Accounts. |
| NFC, RoW | Non-financial corporates; the rest of the world. Both are sectors in Z.1. |
| TIC, CSLT | Treasury International Capital data on cross-border flows. CSLT is a newer TIC securities dataset (Treasury notice of 21 May 2026). |
| N-PORT, N-MFP | SEC monthly holdings filings: N-PORT for registered funds, N-MFP for money-market funds. |
| ETF wrapper | A fund share layered on top of the securities the fund holds. Z.1 counts ETF share creation as equity issuance. |
| RRP | The Federal Reserve's overnight reverse repo facility. |
| ABCP | Asset-backed commercial paper. |
| RPO | Remaining performance obligations: revenue that has been contracted but not yet recognised. |
| MDE | Minimum detectable effect: the smallest effect a test could have seen. |
| IV, RD | Instrumental variables; regression discontinuity. |
| Shapley split | A way of dividing a change between factors so that the parts sum exactly. That makes it an identity, not evidence. |

## File patterns

File names and folders in this repository follow the patterns below.

| What you see | What it is |
|---|---|
| `2026-MM-DD-<code>-<Title>.md` | Findings notes, dated when written, at the repository root. The code in the name, such as P2a, N2c, or D8b, is the work item's label in [RESEARCH_STATE.md](RESEARCH_STATE.md) §5, and the title says what the note is about. A later note says so when it supersedes an earlier one. Dated notes with no work-item code are findings notes too, including filenames that contain Green, Guarantee-Stack, Oracle-RPO, or FERC-EL26. |
| `Parcel_*_For_Grok*.md`, `Parcel_*_For_Gemini*.md` | Parcels, as defined above. A reply is filed as a dated note ending in `-Return.md`, or under `_research/`. |
| `Review_Prompt_For_*.md` | Historical. Dated topic parcels superseded them. |
| [THE_ASK.md](THE_ASK.md) | The principal's instructions, verbatim. Each instruction is an E-number. |
| [RESEARCH_STATE.md](RESEARCH_STATE.md) | The live argument: what is settled, what is contested, the load-bearing assumptions, and the ranked open work. |
| [CHARTER.md](CHARTER.md) | The mission, the markets in scope, and the rules for grades. Definitions are at [CHARTER.md#grades](CHARTER.md#grades). |
| [CORRECTIONS.md](CORRECTIONS.md) | The register of retracted claims. Withdrawn claims stay in the register. |
| [CALENDAR.tsv](CALENDAR.tsv), [HANDOVER.tsv](HANDOVER.tsv) | `CALENDAR.tsv` holds dated obligations, including data releases and re-checks. `HANDOVER.tsv` is the agents' machine-written handover log. |
| [CLAUDE.md](CLAUDE.md) | The operating manual for the AI agents. |
| `Third_Derivative_*`, `Shadow_Debt_*`, `Collateral_*`, [Funding_Identity_First_Principles.md](Funding_Identity_First_Principles.md) | The two earlier workstreams this record grew out of. [Third_Derivative_Concept_Map.md](Third_Derivative_Concept_Map.md) is the concept map for the first, compiled 2 August 2026. [Where_The_Two_Workstreams_Meet.md](Where_The_Two_Workstreams_Meet.md) joins the two. |
| [answer/](answer/), [corrections/](corrections/) | Pointer folders. |
| [dossiers/](dossiers/) | One short file per channel. A file states its own status. |
| [monitor/](monitor/) | The series the live claims use, and when the next observation is released. |
| [docs/](docs/) | The source of [What Holds the Market Up](https://closeofbusiness.github.io/market-plumbing/). The file is `index.html`. GitHub Pages publishes this folder from `main`. |
| [data/](data/), [bin/](bin/) | Derived tables and the scripts that pull, compute, and check. [data/series.tsv](data/series.tsv) is the registry of series. |
| [_research/](_research/) | Working notes, replies, and extracted primary sources. |
| [Analysis/](Analysis/), [Report/](Report/) | Outputs of the earlier workstreams, including a forward-prediction register and HTML reports. |
| [LICENSE](LICENSE) | The licence for this repository's own write-ups: © closeofbusiness, CC BY 4.0. |
| [requirements.txt](requirements.txt) | Libraries for the spreadsheet scripts in `bin/` and the numpy scripts under `_research/`. |
| [.gitignore](.gitignore) | Paths kept out of git, including third-party inputs that are not redistributed. |
| [README.md](README.md) | The front page. |
| [GLOSSARY.md](GLOSSARY.md) | This glossary. |
| [REPRODUCE.md](REPRODUCE.md) | How to run the checks, recompute a figure, and read the page locally. |
