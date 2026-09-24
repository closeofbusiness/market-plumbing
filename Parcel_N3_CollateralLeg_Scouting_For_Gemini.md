# Parcel N3 — the collateral leg: sources, re-use, and the CCP sink · narrow scouting for Gemini

*23 August 2026. Fourth scouting parcel; first for the collateral leg of the nexus, which is the
least-served part of the project. **Location only, narrow by design, written under C-051 and
C-054:** publisher + publication + table + series *name*. No identifiers of any kind; no dollar
signs. We re-pull every series ourselves. Two returns (D1 → C-050, D3 → C-054) had the publishers
right and the identifiers constructed — the D3 return carried five DOIs, all wrong, in a parcel that
had not asked for DOIs. So this one says it outright: **any identifier is deleted unread.***

**Why it is narrow.** We already hold, and will not re-ask: the FR 2004C primary-dealer financing
series; the OFR repo data release; the OFR NCCBR collection's *design* (no re-use field, no public
microdata); the dealers' 10-K collateral-received footnotes (note locations verified); NAIC Schedule
DL; the OFR Hedge Fund Monitor (pulled 23 Aug); Singh's January 2026 *Central Banking* remarks. What
we cannot easily locate is **(a)** any post-2018 estimate of pledged collateral *by source* — hedge
funds through prime brokers, real money through securities lending — **(b)** any *official* re-use
aggregate anywhere in the world, **(c)** where each large CCP's quantitative disclosures actually
live as files, and **(d)** the 2016–26 literature on measuring re-use. That is what this asks.

**Send it** as the fenced block below. Tell Gemini to write the file to disk (it will land at the
Dropbox share root — look there first). One parcel at a time.

---

```
ROLE. Research librarian and data scout. You find WHERE things are. You do not compute, quote, or
establish results. The reader re-pulls every series from the publisher you name.

GOAL. Produce ONE Markdown file named  N3_Collateral_Scouting_Return.md  in the skeleton below.
Done means: every required ID (S1–S3, R1–R4, K1–K2, L1–L2) has a row, and the self-audit is filled
in. Write it to disk with a file tool. If you write through a shell, use a quoted heredoc
(cat > file <<'EOF' … EOF). Today is 23 August 2026. Expected length 2,000–3,500 words. If cut
off, end at a section boundary with <<CONTINUE>>.

## THE FIVE RULES — read twice

R1. A COMPLETE ROW IS: publisher · publication · table or dataset name · series or field NAME ·
    URL of the page you opened · frequency · first and latest date seen. Nothing else.
R2. NO IDENTIFIERS. No DOIs, no journal volume/issue/page, no working-paper numbers, no series
    codes or mnemonics, no page numbers, no quotations. For literature: author surnames, title,
    publisher or journal name, year — that is all. Any identifier you include will be deleted
    unread, so it cannot help you and can only cost you. I find the identifier; you find the thing.
R3. NO DOLLAR SIGNS ANYWHERE IN THE FILE. Write "USD 1.3trn", never "$1.3trn". (The last file
    written this way lost every figure to shell expansion.) If you saw a number you may note it
    as "(seen, unverified — re-pull)"; I will not use it.
R4. DOES NOT EXIST / CANNOT DETERMINE is the EASY answer and a good one. List the searches you
    ran. A blank row costs nothing. A constructed reference ends the usefulness of the whole file.
R5. Provenance chains, not source counts. If a figure or dataset is second-hand, say so and name
    the origin if you reached it.

## CONTEXT (do not act on it; it tells you what the rows are for)

Pozsar and Singh (IMF, 2011) argue that collateral is as critical as base money in facilitating
credit and liquidity: dealers fund themselves by re-using collateral they receive from (i) hedge
funds, through prime-brokerage margin and repo, and (ii) "real money" (pensions, insurers, funds,
sovereign funds), through securities lending. The chain is: primary-source collateral → dealer →
re-use (repo, sec lending, derivative margin) → ultimately parked at a CCP, a central bank, or
another dealer. We have measured the DEALER end (collateral received and re-pledged, from filings)
and the HEDGE-FUND end (collateral posted, repo borrowing, from Form PF aggregates). What is
missing is the SOURCE split, any OFFICIAL measure of re-use, and the CCP SINK as files we can read.

## REQUIRED — one row per ID

### S · SOURCES OF PLEDGED COLLATERAL
S1  Singh's own work AFTER 2018 — IMF working papers, books, BIS/central-bank pieces, industry
    press — that carry an estimate of pledged collateral BY SOURCE (hedge funds vs securities
    lenders / real money) and of re-use velocity. Title, publisher, year, URL for each; whether
    each one actually contains a source split (yes / no / cannot tell without access).
S2  Hedge-fund collateral delivered to prime brokers and the share re-hypothecated — any aggregate
    from any regulator or body (SEC broker-dealer aggregate data, FINRA, FSB, OFR, BoE, ESMA).
    We know Form PF's "collateral posted" aggregate; we want the BROKER side or a re-hypothecation
    share, if anyone publishes one.
S3  Securities lending BY BENEFICIAL-OWNER TYPE — on-loan or lendable balances split by pension /
    insurer / mutual fund / sovereign or central bank / other: ISLA's reports, S&P Global (formerly
    IHS Markit / DataLend) public summaries, the OFR–Fed–SEC pilot collection write-ups, any
    central bank. Which publication carries the split and how often.

### R · OFFICIAL RE-USE MEASURES
R1  The FSB's collateral re-use measures (from its 2017 work on re-hypothecation and re-use and the
    global SFT data standards): has ANY aggregate re-use figure been PUBLISHED by the FSB or BIS
    since — in the Global Monitoring Report on NBFI, a BIS statistics release, or elsewhere?
    Publication name, edition, whether re-use is a series or a one-off box.
R2  ESMA / EU under SFTR: any published statistics on collateral re-use or re-use rates — the
    annual EU securities financing markets report, TRV articles, ESMA statistical releases.
    Publication name, first edition, latest edition, whether re-use is a tabulated field.
R3  OFR's non-centrally cleared bilateral repo (NCCBR) collection (reporting began December 2024):
    has OFR published ANY aggregate from it — a blog, a brief, a data series, a chart? Name and
    date of each publication, and whether it carries volumes by counterparty type.
R4  FICC sponsored repo — the DTCC or FICC publication that carries sponsored-member activity or
    balances (daily / monthly), and the OFR or New York Fed publications that tabulate it.
    Publisher, publication, table name, frequency, first date seen.

### K · THE CCP SINK — public quantitative disclosures as FILES
K1  For EACH of: CME Clearing; ICE Clear Credit; ICE Clear US; ICE Clear Europe; LCH Ltd; LCH SA;
    DTCC / FICC; DTCC / NSCC; OCC; Eurex Clearing; JSCC — the URL of the page where that CCP posts
    its CPMI-IOSCO public quantitative disclosures; the file format (xlsx / csv / pdf / web table);
    whether an ARCHIVE of past quarters is kept on that page; and the earliest quarter visible.
    One sub-row per CCP. A CCP you cannot locate gets CANNOT DETERMINE and the searches run.
K2  Any FREE aggregation of CCP disclosures across CCPs over time — CCP12 / CCP Global, FIA's
    public summaries (as opposed to its member tracker), BIS, a central bank, an academic dataset.
    Publisher, publication, what it aggregates, how far back, free or not.

### L · LITERATURE — author surnames, title, publisher or journal, year, URL. NOTHING ELSE.
L1  Measurement of collateral re-use and velocity, 2016–2026: central-bank and academic work that
    builds a re-use or velocity measure from data (repo chains, SFTR, FR 2004, dealer filings,
    Swiss / German / euro-area SFT data), and the OFR / Federal Reserve pieces on Treasury re-use
    and the "ins and outs" of re-use. 2–3 sentences each on what it measures and with which data.
L2  Official and central-bank work 2021–2026 on hedge-fund Treasury leverage and the cash-futures
    basis trade (OFR, Federal Reserve Board and Banks, BIS, IMF, BoE): title, publisher, year,
    URL, and what DATA each uses. This is the literature that sits on the hedge-fund end of our
    chain; we need the list, not the findings.

## OUTPUT — skeleton of N3_Collateral_Scouting_Return.md

# N3 Collateral Scouting Return — sources, re-use, CCP sink
Prepared: <date> · Model: <model> · Word count: <n>

## 0. Plan (5 lines, written before searching)

## 1. Sources — S1…S3, each:
### S<n> — <name>
- Verdict: EXISTS / PARTIAL / DOES NOT EXIST / CANNOT DETERMINE
- Publisher · publication · table or dataset · series or field name:
- URL opened:
- Frequency · first date · latest date seen:
- Definition notes:
- Provenance:
- Value seen, if any: "(seen, unverified — re-pull)" or "none"

## 2. Official re-use measures — R1…R4, same form
## 3. CCP sink — K1 (one sub-row per CCP), K2
## 4. Literature — L1…L2: surnames, title, publisher/journal, year, URL; 2–3 sentences on what
##    it measures and with which data; relevance (direct / component / opposing)
## 5. What I could not find — every negative with the searches run
## 6. Things you noticed that I did not ask for — only with a retrieval path
## 7. SELF-AUDIT (completeness only — I will verify truthfulness independently)
- [ ] Every ID has a row (__/11); K1 has one sub-row per CCP (__/11)
- [ ] No DOIs, volume/issue/page numbers, working-paper numbers, mnemonics or quotations
- [ ] No dollar sign anywhere in the file (search the file for it before finishing)
- [ ] Every EXISTS row has a URL I opened
- [ ] Every number is labelled "(seen, unverified — re-pull)"
- [ ] Every negative lists the searches behind it
- [ ] If cut off, last line is <<CONTINUE>>

## REMINDERS
One row per ID. Publisher + table + series name, not identifiers. "USD", never "$". DOES NOT
EXIST is a good answer. Do not summarise or evaluate the nexus. Plan → execute → audit. Finish
with the file written to disk.
```
