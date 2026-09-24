# Parcel D1 — bill supply versus cash-pool demand · scouting commission for Gemini

*22 August 2026. First of the D-series parcels, one at a time. **Scouting only: Gemini locates,
Claude builds and verifies.** Written under C-045 and C-049 — no number is supplied for
confirmation, and no specific artefact is requested whose absence was just named.*

**Why this shape.** Today's three returns drew the line clearly: Gemini is reliable on
*existence and location* (which publisher, which table, has anyone built it) and unreliable on
*derivation and verification* (a $20trn error on household net worth; an invented set of FERC
filings with perfectly-formatted accession numbers). So this parcel asks for **retrieval paths**,
and treats any number it returns as a pointer to re-pull, never as a result.

**What the principal asked for, and how it is met.**
- *Output to a file* — the prompt mandates a single Markdown file with a fixed name and fixed
  section skeleton. If Gemini has a file tool it writes it to disk; if not, it emits the whole
  file as one fenced block to paste into `D1_Scouting_Return.md`. Either way, the deliverable is
  the file, not a chat answer.
- *A clear goal condition* — a numbered required-items list (S1–S16, L1–L6, P1–P4), one row per
  ID mandatory even when the answer is DOES NOT EXIST, and a self-audit checklist it must fill in
  before it is allowed to stop. "Plan → execute → audit" is the sequence.
- *Maximum effort* — expected length stated, a continuation marker for truncation, and the
  constraints repeated at the end (recency), which is standard Google guidance for long
  structured outputs.

---

```
ROLE. You are a research librarian and data scout for a quantitative study. Your job is to find
WHERE things are, not to compute results. The person reading your file will re-pull every series
from the source you name and run the test themselves. A retrieval path you did not check is
worth nothing; a number without a retrieval path is worth less than nothing.

GOAL. Produce ONE complete Markdown file named  D1_Scouting_Return.md  following the exact
skeleton in §OUTPUT below. You are finished only when every required ID in §REQUIRED has its own
row AND the §SELF-AUDIT checklist at the end is filled in truthfully. If you have a file-writing
tool, write the file to disk. If you do not, output the entire file contents in a single fenced
markdown block and nothing else after it.

Today is 22 August 2026. Use search. Go to issuing institutions. Expected length: 3,000–6,000
words. If you are cut off before the end, stop at a section boundary and write the line
<<CONTINUE>> — I will reply "continue" and you resume from that exact point without repeating.

────────────────────────────────────────────────────────────────────────────────────────────
## THE TEST THIS SCOUTING SERVES (context only — do not run it)

Pozsar (IMF WP/11/190, Aug 2011) argues shadow banking arose because INSTITUTIONAL CASH POOLS
outgrew the supply of short-term government-guaranteed instruments. He measures a "shortage" =
(institutional cash pools) − (short-term government-guaranteed instruments available to them,
net of foreign official holdings), and puts it at $1.1trn, $1.6trn, $1.6trn in 2005–07. His
policy conclusion is that Treasury BILL SUPPLY should be managed as a macroprudential tool,
because more bills means less private shadow money.

Since 2023 the US Treasury has issued bills at very large scale, and the Fed's ON RRP facility —
which Pozsar's 2014 OFR paper treats as part of the public-money supply — rose to ~$2.5trn and
then drained. The framework therefore PREDICTS that private shadow money should have shrunk.
We intend to test that from public data. You are finding the data and the prior work.

────────────────────────────────────────────────────────────────────────────────────────────
## THREE RULES THAT OVERRIDE EVERYTHING ELSE

R1. RETRIEVAL PATH OR NOTHING. For every series: issuing body → publication/table → series ID
    or line → URL → frequency → first available date → latest date you actually saw. If you saw
    a number, you may quote it, but label it "(seen, unverified — re-pull)". I will not use it.

R2. PROVENANCE CHAINS, NOT SOURCE COUNTS. If five sources report a figure and all cite one
    origin, that is ONE source — say so. If you found something second-hand and could not reach
    the origin, write "origin not reached" and give the nearest link.

R3. DO NOT INVENT REFERENCES. If a table, series ID, paper or URL does not exist, write DOES NOT
    EXIST and list what you checked. A clean negative is a complete, valuable answer. A
    plausible-looking reference that turns out to point elsewhere destroys the whole file's
    value, and I will check them.

────────────────────────────────────────────────────────────────────────────────────────────
## REQUIRED — one row per ID, no exceptions

### S · SERIES (the data to run the test)

DEMAND SIDE — the four institutional cash-pool categories (Pozsar's taxonomy):
S1  Liquidity tranche of FX reserves held in USD short-term instruments — IMF COFER, US TIC
    (foreign official holdings of bills / short-term Treasuries), Fed H.4.1 foreign repo pool.
    Which series, and can the "liquidity tranche" be separated from total reserves?
S2  Cash balances of global corporations — Z.1 nonfinancial corporate liquid assets (which
    table/lines), AFP Corporate Cash Indicators, any S&P/Moody's corporate cash aggregate.
S3  Centrally managed cash of institutional investors and large asset managers — is there ANY
    series? Candidates: ICI institutional MMF assets, OFR MMF Monitor by investor type, N-MFP
    shareholder-type fields, securities-lending cash pools. Be explicit if this category has no
    direct measure — that is Pozsar's own weak link and we need to know it is still weak.
S4  Securities lenders' cash-collateral reinvestment pools — RMA/ISLA surveys, N-MFP for
    fund-structured pools, OFR. Which publish the stock of cash collateral and its reinvestment
    composition?
S5  Any published AGGREGATE of institutional cash pools, any definition, post-2013 — if none,
    say so.

SUPPLY SIDE — short-term government-guaranteed instruments:
S6  Treasury bills outstanding, monthly, 2005→2026 — Monthly Statement of the Public Debt /
    Treasury Bulletin / SIFMA / FRED. Also bills as a share of marketable debt.
S7  Foreign official holdings of bills and short Treasuries (to net out, per Pozsar) — TIC.
S8  Fed ON RRP take-up, daily, 2013→2026 — FRBNY series; and the foreign repo pool separately.
S9  Agency discount notes outstanding — FHLB Office of Finance / Fannie / Freddie; any
    aggregate.
S10 Reserve balances at the Fed (public money, for completeness) — H.4.1.

THE OBJECT — private and public shadow money, Pozsar's 2014 categories, rebuildable to 2026:
S11 Uninsured demand deposits — FDIC QBP / Call Report RC-O; the exact item and whether
    "demand" is separable from "uninsured" at all.
S12 Overnight repo by collateral type (government vs private) — FR 2004 tables, OFR
    tri-party/GCF data, OFR NCCBR collection. Which give overnight × collateral-type × cash
    lender?
S13 MMF assets by type — prime vs government, institutional vs retail — ICI weekly, OFR MMF
    Monitor; and MMF HOLDINGS composition (bills, Fed RRP, private repo, CP, CDs) — OFR MMF
    Monitor / N-MFP. State the 2016 and 2023–24 rule-change breaks.
S14 Financial and asset-backed commercial paper outstanding — Fed CP release.
S15 Large time deposits — H.8 / Z.1, which line.
S16 Stablecoin stock and reserve composition (possible new category) — issuer attestations,
    any aggregator with a retrievable history.

### L · LITERATURE (has anyone run this test, or its components?)
L1  Sunderam (2015), "Money Creation and the Shadow Banking System" — exact citation, and what
    it establishes about private money responding to Treasury-bill supply.
L2  Krishnamurthy & Vissing-Jorgensen (2015), "The Impact of Treasury Supply on Financial Sector
    Lending and Stability" — citation and the mechanism claimed.
L3  Carlson, Duygan-Bump, Natalucci, Nelson, Ochoa, Stein, Van den Heuvel (2016), "The demand
    for short-term, safe assets and financial stability" — citation; is this the closest prior
    run of the Pozsar test?
L4  Greenwood, Hanson & Stein (2015), government debt maturity and private money — citation.
L5  ANYTHING 2022–2026 that tests whether the post-2023 bill surge or the ON RRP drain
    displaced private money-like claims. Fed notes, BIS, OFR, academic, sell-side (Pozsar's own
    later writing included). This is the most valuable item in the file. If nothing exists,
    that is a finding — say so explicitly.
L6  Any critique arguing bill supply does NOT crowd out private money (the opposing case).

### P · PRIOR PRECISION (so we build on Pozsar's definitions, not our memory of them)
P1  In WP/11/190, which instruments exactly count as "short-term government-guaranteed" for the
    shortage measure, and what maturity cut-off? Quote the definition (under 25 words).
P2  In WP/11/190, what is netted out and why (the foreign official holdings point)? Page/figure.
P3  In OFR WP 2014-04, the exact boundary between "public money", "public shadow money",
    "private shadow money" — which instrument sits in which cell, and the maturity cut (7 days
    / 1 year). Page references.
P4  Has Pozsar, or anyone citing him, published an UPDATED cash-pool or shortage figure after
    2014? (We believe not. Confirm or correct, with the check you ran.)

────────────────────────────────────────────────────────────────────────────────────────────
## OUTPUT — the exact skeleton of D1_Scouting_Return.md

# D1 Scouting Return — bill supply vs cash-pool demand
Prepared: <date> · Model: <your model name> · Word count: <n>

## 0. Plan (write this FIRST, before searching: 5–10 lines on how you will work through
##    S1–S16, L1–L6, P1–P4, and what you expect to be hardest)

## 1. Series — one subsection per ID S1…S16, each in this exact form:
### S<n> — <short name>
- Verdict: EXISTS / PARTIAL / DOES NOT EXIST / CANNOT DETERMINE
- Issuer & publication:
- Series ID / table & line:
- URL:
- Frequency · first date · latest date seen:
- Definition notes (what it includes/excludes; breaks):
- Provenance: (primary / secondary→origin / origin not reached)
- Value seen, if any: "(seen, unverified — re-pull)" or "none quoted"

## 2. Literature — one subsection per ID L1…L6:
### L<n> — <short name>
- Citation (authors, year, title, journal/series, link):
- What it establishes, in 2–4 sentences, your words:
- Relevance to the Pozsar test: direct / component / opposing
- Provenance:

## 3. Prior precision — P1…P4, each with page/figure reference and a ≤25-word quote where asked

## 4. What I could not find — every ID that came back DOES NOT EXIST or CANNOT DETERMINE,
##    with the searches you ran (query + site), so I do not repeat them

## 5. Things you noticed that I did not ask for — series, papers, breaks, a better test design.
##    Keep to items with a retrieval path.

## 6. SELF-AUDIT — fill in truthfully before you stop
- [ ] Every ID S1–S16 has a row (count: __/16)
- [ ] Every ID L1–L6 has a row (count: __/6)
- [ ] Every ID P1–P4 has a row (count: __/4)
- [ ] Every EXISTS row has a URL I actually opened
- [ ] Every quoted number is labelled "(seen, unverified — re-pull)"
- [ ] No reference in this file was constructed rather than found
- [ ] §4 lists the searches behind every negative
- [ ] If I was cut off, the last line is <<CONTINUE>>

────────────────────────────────────────────────────────────────────────────────────────────
## ONE WORKED EXAMPLE ROW, so the format is unambiguous

### S14 — Financial and asset-backed commercial paper outstanding
- Verdict: EXISTS
- Issuer & publication: Federal Reserve Board, Commercial Paper Rates and Outstanding Summary
- Series ID / table & line: "Commercial Paper Outstanding" release tables; FRED mirrors, e.g.
  ABCOMP (asset-backed), COMPOUT (total). Confirm the exact FRED IDs yourself.
- URL: https://www.federalreserve.gov/releases/cp/
- Frequency · first date · latest date seen: weekly · 2001 · <date you saw>
- Definition notes: seasonally and not-seasonally adjusted variants; financial vs nonfinancial
  vs ABCP split; data-collection change in 2006 (DTCC) — state it if you find it.
- Provenance: primary
- Value seen, if any: none quoted

────────────────────────────────────────────────────────────────────────────────────────────
## REMINDERS — read again before you write the file

- One row per required ID. Missing rows are the failure mode I am guarding against.
- Retrieval path or nothing. I will re-pull everything; your job is to make that possible.
- Do not invent references. DOES NOT EXIST is a good answer. A plausible wrong one is fatal.
- Do not summarise my project, do not evaluate the test, do not recommend conclusions.
- Plan first (§0), then execute (§1–§5), then audit (§6). Finish with the file, nothing after.
```
