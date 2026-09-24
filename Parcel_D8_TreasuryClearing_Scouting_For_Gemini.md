# Parcel D8 — Treasury clearing: is the sponsored pipe shrinking or moving? · narrow scouting for Gemini

*23 August 2026. Fifth scouting parcel. **Location only.** Written under C-051, C-054 and C-055: publisher +
publication + table + series *name*; no identifiers; no dollar signs; and — new, from the N3 return — **no
template-filled rows**: if you did not open the page, the field is CANNOT DETERMINE, and rows for different
entities must differ where the facts differ. Eleven CCP rows with identical attributes is how a return dies.*

**Why this parcel exists.** DTCC's daily sponsored-service file shows FICC sponsored activity peaking at
about USD 3.0trn at end-2025 and falling by about a fifth to 20 August 2026, and OFR wrote on 20 August that
central clearing of Treasury repo "plateaued in Q1 2026". That file covers FICC only. If CME's or ICE's
Treasury clearing services took volume in 2026, the "decline" is migration between CCPs; if bilateral
(NCCBR) grew instead, it is a retreat from clearing. We hold: the DTCC sponsored CSV, OFR's repo data
release and NCCBR blogs/briefs, the FR 2004 primary-dealer venue lines, the Form PF hedge-fund repo series,
and the NY Fed sponsored-repo staff report. What we cannot easily locate is where the *other* CCPs publish
their Treasury-clearing volumes, the mandate calendar as it now stands, and the official/industry
publications of 2025–26 on the transition. That is what this asks — and only that.

**Send it** as the fenced block below. Ask Gemini to write the file to disk; it lands at the Dropbox share
root. One parcel at a time.

---

```
ROLE. Research librarian and data scout. You find WHERE things are. You do not compute, quote, or
establish results. The reader re-pulls every series from the publisher you name.

GOAL. Produce ONE Markdown file named  D8_Clearing_Scouting_Return.md  in the skeleton below. Done means:
every required ID (M1–M2, V1–V4, P1–P3) has a row, and the self-audit is filled in. Write it to disk with a
file tool; if through a shell, use a quoted heredoc (cat > file <<'EOF' … EOF). Today is 23 August 2026.
Expected length 1,800–3,000 words. If cut off, end at a section boundary with <<CONTINUE>>.

## THE SIX RULES — read twice

R1. A COMPLETE ROW IS: publisher · publication · table or dataset name · series or field NAME ·
    URL of the page you opened · frequency · first and latest date seen. Nothing else.
R2. NO IDENTIFIERS. No DOIs, volume/issue/page, working-paper or staff-report numbers, rule or docket
    numbers, series codes, mnemonics, page numbers or quotations. For documents: issuer, title, date,
    URL. Anything else is deleted unread.
R3. NO DOLLAR SIGNS ANYWHERE IN THE FILE. Write "USD 1.3trn". Numbers you saw are noted only as
    "(seen, unverified — re-pull)"; I will not use them.
R4. NO TEMPLATE ROWS. Every field you fill must come from a page you opened for THAT entity. If you
    did not open it, write CANNOT DETERMINE in that field. Identical attribute sets across different
    entities will be treated as constructed. It is better to return three verified fields than
    seven plausible ones.
R5. DOES NOT EXIST / CANNOT DETERMINE is the EASY answer and a good one. List the searches you ran.
R6. Provenance chains, not source counts. Second-hand → say so and name the origin if reached.

## CONTEXT (do not act on it; it tells you what the rows are for)

US Treasury repo is moving into central clearing under an SEC mandate. Money-market funds lend cash
into FICC's sponsored service; hedge funds borrow through it; dealers sponsor both. We can measure the
FICC leg daily. We need to know whether OTHER clearing houses now clear Treasury cash or repo, where
they publish volumes, what the mandate's compliance dates are as currently amended, and which official
and industry publications of 2025–26 describe the transition with data.

## REQUIRED — one row per ID

### M · THE MANDATE
M1  The SEC's Treasury clearing rule: the SEC page for the final rule (December 2023) AND every later
    SEC action that changed the compliance dates (extensions, exemptive orders, 2025–26). For each: issuer,
    title, date, URL. Then state, as currently in force, the compliance date for CASH Treasury
    transactions and for REPO — each with the URL of the SEC document that sets it. If you cannot find
    the current dates on an SEC page, say CANNOT DETERMINE; do not infer from press.
M2  FICC's access models for indirect participants — Sponsored Service, Agent Clearing Service, and any
    "done-away" or cross-margining arrangements: the DTCC/FICC page describing each, and whether DTCC
    publishes VOLUME or MEMBER-COUNT statistics for the Agent Clearing Service separately from the
    sponsored service (we have the sponsored CSV at dtcc.com/charts/membership — do not re-find it).

### V · VOLUMES AT THE OTHER CCPs
V1  CME Group's Treasury clearing service (CME Securities Clearing or successor name): launch date for
    cash and for repo; the page where CME publishes its cleared-Treasury VOLUMES or open positions (daily,
    monthly, or only in PQD); file format; first date visible. If no volume page exists, say so.
V2  ICE's Treasury clearing service (ICE Clear Credit or successor): same fields as V1.
V3  Any other clearing house approved or applying to clear US Treasuries (e.g. LCH, Eurex, a new entrant):
    name, status (approved / applied / announced), the regulator's page that says so, and whether any
    volume is published.
V4  FICC's own TOTAL cleared Treasury volumes beyond the sponsored CSV — DTCC statistics or press pages
    with GSD daily/monthly cleared volume (DVP, GCF, sponsored, agent-cleared), and whether a time series
    is downloadable. Publisher, publication, table name, frequency, first/latest date.

### P · PUBLICATIONS 2025–26 ON THE TRANSITION (issuer, title, date, URL, and what DATA each uses)
P1  OFR, Federal Reserve Board and Banks (incl. Liberty Street), and the US Treasury / TMPG: anything
    from January 2025 to date on Treasury clearing volumes, the sponsored service, agent clearing,
    done-away trading, or the shift between cleared and non-centrally-cleared bilateral repo. Titles,
    dates, URLs, data used. We already hold OFR's NCCBR blogs (Aug 2025 – Aug 2026) and the NY Fed
    sponsored-repo staff report (Oct 2025) — list anything ELSE.
P2  Industry and market-infrastructure publications with DATA (not opinion): DTCC, CME, ICE, SIFMA, ISDA,
    Clarus, FIA, ICMA — reports or data posts 2025–26 on Treasury clearing volumes and the mandate.
P3  Anything that explicitly addresses a 2026 DECLINE or PLATEAU in sponsored or cleared Treasury repo,
    or a migration between clearing houses or to bilateral: issuer, title, date, URL. If nothing exists
    beyond OFR's 20 August 2026 blog, say so — that is a finding.

## OUTPUT — skeleton of D8_Clearing_Scouting_Return.md

# D8 Clearing Scouting Return — mandate, other CCPs, transition publications
Prepared: <date> · Model: <model> · Word count: <n>

## 0. Plan (5 lines, written before searching)

## 1. Mandate — M1, M2, each:
### M<n> — <name>
- Verdict: EXISTS / PARTIAL / DOES NOT EXIST / CANNOT DETERMINE
- Publisher · publication · table or dataset · series or field name:
- URL opened:
- Frequency · first date · latest date seen:
- Definition notes:
- Provenance:
- Value seen, if any: "(seen, unverified — re-pull)" or "none"

## 2. Volumes at other CCPs — V1…V4, same form (one row per CCP; fields differ where facts differ)
## 3. Publications — P1…P3: issuer, title, date, URL; one line on the data used; relevance
## 4. What I could not find — every negative with the searches run
## 5. Things you noticed that I did not ask for — only with a retrieval path
## 6. SELF-AUDIT (completeness only — I will verify truthfulness independently)
- [ ] Every ID has a row (__/9)
- [ ] No identifiers of any kind; no dollar sign anywhere (search the file before finishing)
- [ ] No two entities share an identical attribute set unless I opened both pages and they are identical
- [ ] Every EXISTS row has a URL I opened
- [ ] Every number is labelled "(seen, unverified — re-pull)"
- [ ] Every negative lists the searches behind it
- [ ] If cut off, last line is <<CONTINUE>>

## REMINDERS
Locations, not findings. "USD", never "$". CANNOT DETERMINE beats a plausible field. Do not explain
the mandate or judge the decline. Plan → execute → audit. Finish with the file written to disk.
```
