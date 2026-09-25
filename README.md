# Market Plumbing

**What is driving asset prices, and where is the money coming from?** This repository is an open research record on that question: the current answer, the evidence behind it, every claim the work has since retracted, and the scripts that check it. The programme's own write-ups are licensed CC BY 4.0.

## Start here

1. **[What Holds the Market Up](https://closeofbusiness.github.io/market-plumbing/)**: the current answer on one page, with every claim graded. It is a dated rendering of the answer note, and its source is [`docs/index.html`](docs/index.html).
2. **[The answer note](2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md)** is the authority: where the page and the note disagree, the note wins. It restates almost no numbers on purpose. Each claim links to the findings note that owns it.
3. **[CHARTER.md](CHARTER.md)**: the mission (the standing goal), the markets in scope, the rules every file follows, and the four grades.
4. **[dossiers/](dossiers/)**: one short file per channel (passive and ETF flows, AI funding, shadow money, collateral, rates, and others). Each gives the hypothesis, its status, the evidence, and what would change it.
5. **[CORRECTIONS.md](CORRECTIONS.md)**: the register of retracted claims. It is long, so don't read it straight through. When a note cites, say, C-081, search the file for `## C-081`. `bash bin/check.sh --latest` prints the newest entries.

Equities are the furthest along. Rates, FX and commodities are in scope, and where their work has not been done, the files say so.

## Who does the work, and how

The research is done by AI models under the direction of one person. The newer files call that person **the principal**; older files say **the operator**, and some notes use the principal's first name. The principal sets the question and rules on scope and on standards of evidence.

- **Claude** (Anthropic) is the lead analyst. It writes the answer, and when it reviews or adjudicates another agent's work, the notes call it **the supervisor**.
- **GrokBot** (Grok, from xAI) is a second agent working in the same repository.
- **Gemini** (Google) is consulted too. Both outside models receive self-contained briefs called **parcels**.

Outside review is adversarial on purpose: a finding stands only while attacks on it keep failing.

Three conventions follow from this, and you will meet them everywhere:

- **The principal's instructions are recorded verbatim**, never paraphrased, in [THE_ASK.md](THE_ASK.md) as E-000, E-001, and so on. When a note cites a standard such as E-005 or E-007, that is where it is defined.
- **Every claim carries a grade**: IDENTITY, MEASURED, BOUNDED or HYPOTHESIS, defined in [CHARTER.md](CHARTER.md#grades). The default is HYPOTHESIS. Surviving a review raises confidence but does not settle a claim.
- **Retracted claims are registered, not deleted.** [CORRECTIONS.md](CORRECTIONS.md) numbers them C-001, C-002, and so on. It also bans their wording, so the checks catch a dead claim if it resurfaces.

## Finding your way around

The top level is flat, so GitHub's file list is long. It falls into these groups:

| What you see | What it is |
|---|---|
| `2026-MM-DD-<code>-<Title>.md` | Findings notes, dated when written. The code (P2a, N2c, D8b and so on) is the work item's label in `RESEARCH_STATE.md` §5, and the title says what the note is about. A later note says so when it supersedes an earlier one. |
| `Parcel_*_For_Grok*.md`, `Parcel_*_For_Gemini*.md` | Parcels: briefs sent to an outside model. Each reply is filed as a dated `…-Return.md` note or under `_research/`. |
| `Review_Prompt_For_*.md` | Standing prompts for outside review. |
| [`THE_ASK.md`](THE_ASK.md) | The principal's instructions, verbatim (the E-numbers). |
| [`RESEARCH_STATE.md`](RESEARCH_STATE.md) | The live argument: what is settled, what is contested, the load-bearing assumptions, and the ranked open work. |
| `CALENDAR.tsv`, `HANDOVER.tsv` | Dated obligations (data releases and re-checks), and the agents' machine-written handover log. You don't need either to read the findings. |
| [`CLAUDE.md`](CLAUDE.md) | The operating manual for the AI agents. It is long and written for them; you don't need it to read the findings. |
| `Third_Derivative_*`, `Shadow_Debt_*`, `Collateral_*`, `Funding_Identity_First_Principles.md` | The two earlier workstreams this question grew out of. See [Where this came from](#where-this-came-from). |
| [`answer/`](answer/), [`corrections/`](corrections/) | One-line pointers to the answer note and to `CORRECTIONS.md`. |
| [`dossiers/`](dossiers/), [`monitor/`](monitor/) | Per-channel summaries; the free data series the live claims use, and when each next prints. |
| [`docs/`](docs/) | The web page, which GitHub Pages publishes at https://closeofbusiness.github.io/market-plumbing/ |
| [`data/`](data/), [`bin/`](bin/) | Derived data (a registry of series in `data/series.tsv`, plus CSV tables) and the scripts that pull, compute and check. |
| [`_research/`](_research/) | Working notes, replies from outside models, and extracted primary sources. Evidence, not the deliverable. |
| [`Analysis/`](Analysis/), [`Report/`](Report/) | Outputs of the earlier workstreams: a forward-prediction register and HTML reports. |

## Where this came from

The programme runs under the working name Third Derivative Research, which is the name you will see on the page and in older notes. It began in August 2026 as two workstreams:

- **The "third derivative" framework.** A primary innovation first forces a reorganisation or an overcapacity, and later businesses capture most of the value ([Third_Derivative_Concept_Map.md](Third_Derivative_Concept_Map.md)).
- **Shadow-banking collateral and money creation.** A measurement of these on the Pozsar–Singh nonbank–bank nexus (the `Shadow_Debt_*` and `Collateral_*` files).

[Where_The_Two_Workstreams_Meet.md](Where_The_Two_Workstreams_Meet.md) joins the two. On 11 September 2026 the principal widened the goal to the question above ([THE_ASK.md](THE_ASK.md), E-003). The nexus work carries over as two of its channels.

## Glossary

| Term | Meaning |
|---|---|
| the principal | The person who directs the programme. Older files say **the operator**. |
| the supervisor | Claude, the lead AI analyst, when it reviews, checks or adjudicates another agent's work. |
| parcel | A self-contained brief sent to an outside model (Grok or Gemini), written so it can be answered in one pass. |
| E-*nnn* | An entry in [THE_ASK.md](THE_ASK.md): one of the principal's instructions, quoted verbatim. |
| C-*nnn* | An entry in [CORRECTIONS.md](CORRECTIONS.md): a retracted claim, why it died, and the wording now banned. |
| P2a, N2c, D8b, B0, ATT0 … | Work-item labels from the ranked list in `RESEARCH_STATE.md` §5. Search that file for the label; the first note on an item usually carries the label in its file name. B0 to B6 are the bridge designs, which try to measure how far buying moves prices. |
| Tier N, O, B, T, A2 | Groups of work in `RESEARCH_STATE.md` §5: the nexus, outcome-side work, the bridge, tangents, and a persona capability awaiting a decision. |
| A1 … A13 | Rows of the table of asks in `RESEARCH_STATE.md` §0. |
| d1, d2, d3, d4 | Defects found in the September document audits, labelled in the order found. For example, d1 and d2 mark a note that names a deliverable that is not on disk. |
| the gate | `bash bin/check.sh --all`. See [Checking the work](#checking-the-work). |
| nexus | The nonbank–bank nexus: nonbanks funding banks and dealers, and the collateral that moves between them (Pozsar and Singh, IMF Working Paper 11/289, 2011). |
| z_k | The wholesale share: nonbank wholesale funding W, as a share of W plus M2 ([the N2b note](2026-08-31-N2b-zk-The-Wholesale-Share.md)). |
| M, the multiplier | Dollars of market value per dollar of net buying. Published estimates range roughly from 2 to 9.4 (the "envelope"), and the programme has no central value for it. |
| JVZ | Jiang, Vayanos and Zheng (2025, *Review of Financial Studies*), on passive investing and mega-firms. The programme tested their mechanism on free data. |
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

## Checking the work

There are two kinds of check, and they answer different questions.

**The gate checks the record's bookkeeping, not its numbers.** Run it from the repository root:

```bash
bash bin/check.sh --all
```

It takes one to two minutes and checks five things (its own labels are in brackets):

- the goal statement is identical in its three homes (goal);
- every top-level file and folder is indexed in `CLAUDE.md` (M5);
- every C-number cited has exactly one entry in the register (M7, M8);
- no numbered to-do items sit outside the ranked list in `RESEARCH_STATE.md` (M6);
- no retracted claim's wording appears in the notes (outside `_research/`) or on the page (killed claims, page check).

Read its ✓ lines. The exit code is always 0 by design, so it proves nothing. It has been run with macOS's own grep and with ugrep.

**Reproducing a number means following its trail.** Each claim in the answer note names the findings note that owns it. That note names its script (in `bin/`) and its output tables (in `data/`). The derived tables are committed, so the arithmetic can be re-checked without downloading anything. For example, the earnings share of the S&P 500 gain recomputes from [`data/p2a_decomposition/decomp_cumulative.csv`](data/p2a_decomposition/decomp_cumulative.csv).

Re-running a script from raw inputs needs:

- **Python 3.** Most scripts use only the standard library; `pip install -r requirements.txt` covers the two that read spreadsheets.
- **An `SEC_UA` environment variable.** SEC EDGAR asks every automated request to identify its sender. Before running a script that calls it, run `export SEC_UA="Your Name you@example.com"`.
- **Third-party inputs, which are not redistributed here.** These include Shiller's `ie_data.xls`, FRED's DGS10 and DFII10 series, and Damodaran's `ERPbymonth.xlsx`. Download them from their publishers to the path the script names; `.gitignore` keeps them out of commits. US federal primary sources, which are public domain, are kept under `_research/primary_sources/`.

Some older notes cite paths beginning `/private/tmp/claude-501/`. That was an agent's temporary workspace at the time, and it has since been deleted. The durable copy is the repository path cited alongside it, and `python3 bin/check_scratchpad_refs.py` lists every such case.

## View the page

The page is online at **https://closeofbusiness.github.io/market-plumbing/**. GitHub Pages publishes it from `docs/` on `main`.

To view it locally, clone the repository and serve the folder:

```bash
git clone https://github.com/closeofbusiness/market-plumbing.git
cd market-plumbing
python3 -m http.server 8000 --directory docs
```

Then open http://localhost:8000. Opening `docs/index.html` directly in a browser also works. The page loads its fonts from Google Fonts; everything else is in the one file.

## Provenance and licence

The programme's own write-ups are © closeofbusiness under Creative Commons Attribution 4.0 International ([LICENSE](LICENSE)). Third-party and paywalled documents are summarised and cited, not copied, and quotations are kept short. Material that must not be public is kept outside this repository: the SEC contact string, paywalled originals, correspondence, simulations of named people, and third-party datasets.

On 24 September 2026 nine files that should not have been published were removed. The history was rewritten, and the repository was then deleted and recreated, so GitHub holds no copy of the old commits. Nothing else changed. [THE_ASK.md](THE_ASK.md), E-011 and E-013, records the details.
