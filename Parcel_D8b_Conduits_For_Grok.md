# Parcel D8b — the other conduit: securities-backed ABCP and equity financing · scouting spec for Grok

*23 August 2026. Sixth scouting parcel; first scouting parcel for Grok (its prior use here was adversarial
review). Chosen for Grok because the missing pieces are live-web and market-colour shaped: a sponsor→programme
mapping scattered across rating-agency publications, and 2025–26 funding-desk commentary. **Grok cannot read
our files, so this parcel is fully self-contained: every grounding fact is carried inline, and the header
table below records which project file each fact comes from, so the parcel itself is auditable.***

## For Martin — how to run it

- **Model:** Grok 4 with live search at the highest reasoning setting. One parcel at a time, as always.
- **Send:** the single fenced block below, nothing else.
- **Return path:** Grok has no disk access here — it must output the complete return as ONE fenced Markdown
  block named `D8b_Conduit_Scouting_Return.md`. Save that block verbatim to the Dropbox share root (or paste
  it to me); I file it under `_research/`, run the seven-agent verification fan-out (the C-055 receipt
  procedure), and adjudicate before anything is read as a finding.
- **Expectation, from five prior external returns (C-050, C-054, C-055, C-057):** publishers will be right,
  URLs/titles/identifiers will be partly constructed, and the self-audit proves completeness, not truth. The
  parcel's rules are written for that failure mode; the fan-out catches the rest.

## Grounding — where each fact inside the spec comes from

| Fact carried in the spec | Authoritative file in this repo |
|---|---|
| Ultimate goal (one line; context only) | `THE_ASK.md` E-002; `bin/check.sh --goal` |
| MMF holdings of named alt-ABCP programmes (USD 9.4bn: Chesham 7.2 / Bennington Stark 1.5 / Mountcliff 0.7; lower bound; Nearwater/Northcross/Guggenheim matched no issuer string) | `2026-08-23-FT-Harvest-ABCP-Conduits-And-Equity-Repo.md` §2 (our own N-MFP3 census) |
| ABCP outstanding 421bn (31 Dec 2025) → 488bn (19 Aug 2026) | `data/series.tsv` `abcp_outstanding_bn` (Fed CP release via FRED ABCOMP) |
| Press claims: Nangle 21 Aug 2026 (JPMorgan +~100bn YTD on DTCC basis; S&P Dec-2025 sponsor table: Nearwater, JPM, RBC, Guggenheim, Crédit Agricole, Northcross, BSN, BNP, SocGen, TD); Wigglesworth 29 Jun 2026 (record AXW-measured equity financing costs, Morgan Stanley) | `2026-08-23-FT-Harvest-ABCP-Conduits-And-Equity-Repo.md` §1 — **claims, not established** |
| Why this parcel exists (D8 status: Treasury-repo pipe instrumented; ABCP half open) | `RESEARCH_STATE.md` §5 D8; `2026-08-23-Parcel-D8-Clearing-Return.md` §1 |
| The rules in the spec (no identifiers; no dollar sign; no template rows; negatives are good; no confirmation of our numbers; X posts are colour not sources) | `CORRECTIONS.md` C-045, C-049–C-051, C-054–C-057; `CLAUDE.md` working rules, external returns |

---

```
ROLE. Research librarian and data scout with live search. You find WHERE things are published. You do not
compute, conclude, or advise. The reader re-pulls every series and re-reads every document from the
publisher you name. Locations are the deliverable.

GOAL. Output the COMPLETE return as ONE fenced Markdown code block, and nothing outside it, so it can be
saved verbatim as  D8b_Conduit_Scouting_Return.md . Done means: every required ID (P1–P4, E1–E3, X1, N)
has a row, P1 has one sub-row per sponsor (10), and the self-audit is filled in. State the date you ran.
Expected length 2,000–3,500 words. If cut off, end at a section boundary with <<CONTINUE>>.

## THE EIGHT RULES — read twice; they exist because five prior returns broke them

R1. A COMPLETE ROW IS: publisher · publication · table or dataset name · series or field NAME · URL of
    the page you opened · frequency · first and latest date seen. Nothing else is needed.
R2. NO IDENTIFIERS. No DOIs, no report numbers, no page numbers, no quotations, no ticker-level series
    codes. For documents: issuer, title, author surnames if shown, date, URL. Any identifier you add
    unasked will be deleted unread — it cannot help you and can only cost you.
R3. NO DOLLAR SIGN ANYWHERE. Write "USD 1.3trn". Search your output for the symbol before finishing.
R4. NO TEMPLATE ROWS. Every field must come from a page you opened for THAT entity. Ten sponsors with
    identical attributes will be treated as fabricated. A field you did not verify is CANNOT DETERMINE.
    Three verified fields beat seven plausible ones.
R5. DOES NOT EXIST / CANNOT DETERMINE is the EASY answer and often the finding. List the searches you ran
    for every negative.
R6. Provenance chains. If a fact is second-hand (a press summary of a rating-agency table), say so and
    name the origin; open the origin if you can reach it.
R7. X/SOCIAL POSTS ARE COLOUR, NOT SOURCES. In section X1 only: handle, date, link, one-line summary.
    Never carry a number from a post into any other section. A post is a claim by its author.
R8. DO NOT CONFIRM, REPEAT, OR EVALUATE the numbers in the context below. We have learned that an external
    model confirming a supplied number is the weakest possible verdict. The context tells you what the
    rows are FOR; it is not a questionnaire.

## CONTEXT (do not act on it)

We are building a comprehensive map of how collateral and money creation operate in the shadow banking
system. One channel under construction: money-market funds buying asset-backed commercial paper issued by
"alternative" (non-bank-sponsored, securities-backed) conduits, which fund prime-broker equity margin
lending — private money creation against equity collateral, bypassing the dealer balance sheet. From our
own SEC N-MFP3 census we hold money-fund positions in programmes NAMED Chesham, Bennington Stark and
Mountcliff (a lower bound: several sponsors named in press coverage — Nearwater, Northcross, Guggenheim —
matched NO issuer string in fund filings, so their programmes evidently issue under other names; that
mapping gap is exactly what P1 asks you to locate). Press coverage (Financial Times, June–August 2026)
attributes the growth of these conduits to Basel balance-sheet optimisation and cites an S&P sponsor
table (December 2025) naming: Nearwater, JPMorgan, RBC, Guggenheim, Crédit Agricole, Northcross, BSN,
BNP Paribas, Société Générale, TD. Equity financing costs are said to be at records as measured by CME's
adjusted-interest-rate total-return futures. We already hold and will NOT re-ask: the Federal Reserve CP
release aggregates, our own money-fund filing census route, FICC sponsored-repo data, and the primary-
dealer financing statistics.

## REQUIRED — one row per ID

### P · THE PROGRAMMES
P1  SPONSOR → PROGRAMME NAME mapping, one sub-row per sponsor, for: Nearwater; JPMorgan; RBC; Guggenheim;
    Crédit Agricole; Northcross; BSN; BNP Paribas; Société Générale; TD. Per sub-row: the ABCP
    programme/conduit NAME(s) as they appear on ISSUED PAPER (the issuer name a money fund would report
    holding); where that mapping is public — a rating-agency programme page or report, a sponsor page, an
    investor presentation, a prospectus notice; URL opened; and whether the programme is described as
    securities-backed / financial-asset-backed vs receivables multi-seller. CANNOT DETERMINE per sponsor
    is acceptable and useful — it tells us the mapping is private.
P2  The RECURRING rating-agency ABCP publications that list programmes with sponsor, type and size:
    Moody's, S&P Global Ratings, Fitch — exact publication name, cadence, free or paywalled, landing-page
    URL, latest edition seen. (These are the documents behind press sponsor tables.)
P3  Any official or public SERIES of ABCP outstanding BY PROGRAMME TYPE (bank multi-seller vs
    securities-backed / non-bank "alternative"): does the Federal Reserve CP release carry such a split;
    does DTCC publish CP issuance/outstanding data publicly; do S&P/Moody's publish an index table with a
    type split. Publisher, table name, URL, frequency, first/latest date — or DOES NOT EXIST.
P4  WHAT THE SECURITIES-BACKED CONDUITS HOLD: any public document describing the collateral of any
    programme from P1 (equity margin loans, total-return-swap receivables, repo claims): programme review,
    investor report, sponsor description. One entry per document found, with URL.

### E · EQUITY FINANCING
E1  CME's adjusted-interest-rate total-return futures on the S&P 500: the exact product name and code
    family as CME states it, the product page URL, and WHERE any financing-spread or basis data is
    published (CME pages, settlement files, any free series or chart; paywalled counts, say so).
    Frequency and first date visible.
E2  SIZE of the equity-financing market (prime-broker margin loans + total-return swaps + equity repo),
    2024–2026: official sources (any Federal Reserve, OFR, FSB, BIS table or report) and public dealer or
    industry research. Issuer, title, date, URL, and which components each covers.
E3  Press and research 2025–2026 WITH DATA on ABCP-funded equity financing and on equity-financing cost:
    the items behind and beyond the FT thread. Issuer, title, author surnames, date, URL. Retrievable
    items only.

### X · REAL-TIME COLOUR — Grok's edge, fenced by R7
X1  Since 1 June 2026: what funding-desk, money-market and repo practitioners on X have said about
    alternative/securities-backed ABCP, equity financing costs, or September quarter-end funding.
    Up to 10 posts, substance only: handle · date · link · one line. No numbers carried elsewhere.

### N · NEGATIVES
N   Every negative from P/E/X with the specific searches run (R5).

## OUTPUT — skeleton of D8b_Conduit_Scouting_Return.md

# D8b Conduit Scouting Return — securities-backed ABCP and equity financing
Prepared: <date run> · Model: <model> · Word count: <n>

## 0. Plan (5 lines, written before searching)
## 1. Programmes — P1 (10 sub-rows), P2, P3, P4
### P1 — <sponsor n of 10>
- Programme name(s) on issued paper:
- Securities-backed vs multi-seller:
- Mapping source (publisher · publication · URL opened):
- Frequency · latest edition/date seen:
- Notes / CANNOT DETERMINE fields:
## 2. Equity financing — E1…E3, each:
- Verdict: EXISTS / PARTIAL / DOES NOT EXIST / CANNOT DETERMINE
- Publisher · publication · table or dataset · series or field name:
- URL opened:
- Frequency · first date · latest date seen:
- Definition notes:
- Provenance:
- Value seen, if any: "(seen, unverified — re-pull)" or "none"
## 3. X colour — X1 (handle · date · link · one line each)
## 4. What I could not find — every negative with the searches run
## 5. Things you noticed that I did not ask for — only with a retrieval path
## 6. SELF-AUDIT (completeness only — the reader verifies truthfulness independently)
- [ ] Every ID has a row (__/9); P1 has one sub-row per sponsor (__/10)
- [ ] No identifiers; no dollar sign anywhere (I searched the output for it)
- [ ] No two sponsors share an identical attribute set unless I opened both pages and they match
- [ ] Every EXISTS row and every P1 mapping has a URL I opened
- [ ] Every number is labelled "(seen, unverified — re-pull)"
- [ ] No number from section 3 appears anywhere else in the file
- [ ] Every negative lists the searches behind it
- [ ] If cut off, last line is <<CONTINUE>>

## REMINDERS
Locations, not findings. "USD", never the symbol. CANNOT DETERMINE beats plausible. Do not evaluate the
channel, the FT thesis, or our numbers. One fenced block, nothing outside it. Plan → execute → audit.
```
