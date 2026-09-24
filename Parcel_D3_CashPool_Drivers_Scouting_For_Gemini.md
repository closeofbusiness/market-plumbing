# Parcel D3 — shadow-money demand vs asset-management structure · narrow scouting for Gemini

*22 August 2026. Third scouting parcel. **Location only, narrow by design, written under C-051:**
publisher + publication + table + series *name*. No series IDs, no page numbers, no quotations —
three returns have shown those are where construction happens. A blank row costs nothing; a
constructed reference is fatal. We will re-pull every series from the source ourselves.*

**Why it is narrow.** The core of D3 — institutional cash-pool growth against the growth of the
asset-management complex — we build from Z.1 and OFR data we already reach. What we cannot easily
locate is the *margin and collateral* side of money demand (derivatives initial margin,
securities-lending cash collateral), fund cash-buffer aggregates, and the 2015–26 literature on
what drives institutional cash demand. That is what this parcel asks for, and only that.

---

```
ROLE. Research librarian and data scout. You find WHERE things are. You do not compute, quote, or
establish results. The reader re-pulls every series from the publisher you name.

GOAL. Produce ONE Markdown file named  D3_Scouting_Return.md  in the skeleton below. Done means:
every required ID (M1–M3, SL1–SL2, AM1–AM3, L1–L2) has a row, and the self-audit is filled in.
If you have a file tool, write it to disk; otherwise output the whole file as one fenced block.
Today is 22 August 2026. Expected length 2,000–3,500 words. If cut off, end at a section boundary
with <<CONTINUE>>.

## THE FOUR RULES

R1. PUBLISHER · PUBLICATION · TABLE · SERIES NAME · URL · FREQUENCY · FIRST/LATEST DATE SEEN.
    That is a complete row. Do NOT give series IDs, page numbers or quotations — I will find the
    ID and read the page. If you saw a number, you may note it as "(seen, unverified — re-pull)";
    I will not use it.
R2. DOES NOT EXIST / CANNOT DETERMINE is the EASY answer and a good one. List what you checked.
R3. Provenance chains, not source counts. Second-hand → say so and give the origin if reached.
R4. Do not invent references. Every return so far has contained constructed citations in exactly
    the places where a required row had no real answer. Leave the row with DOES NOT EXIST instead.

## CONTEXT (do not act on it; it tells you what the series are for)

Pozsar & Singh (2011) derive institutional money demand from "reverse maturity transformation":
asset managers holding long-term savings must keep a portion short for mandates, derivatives
overlays, and securities lending. If so, institutional cash-pool demand should scale with the
SIZE AND STRUCTURE of the asset-management complex — AUM, margin requirements, securities-lending
activity, fund liquidity buffers — rather than with monetary policy. We have measured US money-
market fund assets rising from ~$3.0trn (2013) to ~$8.4trn (mid-2026). We now need the
structural drivers located.

## REQUIRED — one row per ID

### M · MARGIN / COLLATERAL DEMAND
M1  Initial margin (and variation margin if separately reported) held by central counterparties,
    aggregated across CCPs over time — the CPMI-IOSCO Public Quantitative Disclosures and any
    body that SUMS them into a usable time series (FIA, ISDA, Clarus, BIS, a central bank).
    Which publisher, which publication, how far back, how often.
M2  Margin for NON-cleared derivatives — the ISDA Margin Survey: years available, what the
    headline aggregates are called, and whether a consistent series exists across years.
M3  Collateral composition of margin — cash vs securities, and by currency — who publishes it,
    for cleared and for non-cleared.

### SL · SECURITIES LENDING
SL1 US securities-lending on-loan stock and the cash-collateral share — FINRA's SLATE facility
    under SEC Rule 10c-1a (status: live? what does it publish, at what granularity, since when),
    ISLA's market reports, OFR, the Fed, and whether the RMA survey is still published and
    public.
SL2 Cash-collateral REINVESTMENT composition (repo / bills / CP / MMF) — anyone public.

### AM · ASSET-MANAGEMENT STRUCTURE
AM1 Official measures of the asset-management complex's size — which Federal Reserve Z.1
    tables carry total financial assets for mutual funds, ETFs, pension funds, insurers; the ICI
    Fact Book totals; SEC Private Fund Statistics for hedge funds and private funds (which
    table gives gross/net assets). Publisher and table names only.
AM2 Fund cash/liquidity BUFFER aggregates — the ICI liquid-asset ratio for equity funds (is it
    still published monthly, how far back), and any N-PORT-derived aggregate of fund cash
    holdings (SEC DERA, OFR, a central bank).
AM3 Hedge-fund cash and unencumbered cash — which table in SEC Private Fund Statistics, and the
    OFR Hedge Fund Monitor's equivalent.

### L · LITERATURE (publisher, title, authors, year — NO page numbers)
L1  Empirical work 2015–2026 on the DRIVERS of institutional cash demand: corporate cash
    holdings (the Bates–Kahle–Stulz lineage and successors), mutual-fund liquidity management
    (Chernenko & Sunderam and successors), margin-driven cash demand (the BIS/CGFS review of
    margining practices after March 2020; the UK LDI episode), and anything on institutional
    cash pools specifically after Pozsar.
L2  Anything that DIRECTLY tests cash-pool or money-fund growth against asset-management AUM or
    margin growth. If nothing exists, say so — that is a finding.

## OUTPUT — skeleton of D3_Scouting_Return.md

# D3 Scouting Return — drivers of institutional cash demand
Prepared: <date> · Model: <model> · Word count: <n>

## 0. Plan (5 lines, written before searching)

## 1. Margin / collateral — M1…M3, each:
### M<n> — <name>
- Verdict: EXISTS / PARTIAL / DOES NOT EXIST / CANNOT DETERMINE
- Publisher · publication · table · series name:
- URL:
- Frequency · first date · latest date seen:
- Definition notes:
- Provenance:
- Value seen, if any: "(seen, unverified — re-pull)" or "none"

## 2. Securities lending — SL1…SL2, same form
## 3. Asset-management structure — AM1…AM3, same form
## 4. Literature — L1…L2: publisher, title, authors, year, link; 2–3 sentences on what it
##    establishes; relevance (direct / component / opposing)
## 5. What I could not find — every negative with the searches run
## 6. Things you noticed that I did not ask for — only with a retrieval path
## 7. SELF-AUDIT (completeness only — I will verify truthfulness independently)
- [ ] Every ID has a row (__/10)
- [ ] No series IDs, page numbers or quotations anywhere in this file
- [ ] Every EXISTS row has a URL I opened
- [ ] Every number is labelled "(seen, unverified — re-pull)"
- [ ] Every negative lists the searches behind it
- [ ] If cut off, last line is <<CONTINUE>>

## REMINDERS
One row per ID. Publisher + table + series name, not IDs. DOES NOT EXIST is a good answer.
Do not summarise or evaluate the test. Plan → execute → audit. Finish with the file.
```
