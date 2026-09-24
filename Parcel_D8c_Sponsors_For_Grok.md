# Parcel D8c — who sponsors these eight conduits? · targeted identification for Grok

*24 August 2026. Seventh scouting parcel; second for Grok. **Narrow by design and unusually specific:** eight
named vehicles, one question each — who stands behind it, and what does it fund? Written after our own agents
exhausted the obvious free routes; the parcel tells Grok exactly what was already tried so it does not repeat it.*

## Why Grok, and why this

Our N-MFP3 census (all 325 August filings, every position — no name filter, no category filter) established
what US money funds actually hold. Eight vehicles in that census, holding **USD 17.4bn of money-fund money
between them**, have **no sponsor we can establish from any free source**. Two of our four "aggregator"
sponsors were originally found only because a live-search model surfaced a law-firm slide — this is the same
shape of problem, and it is the last thing standing between us and a complete map of the channel.

**Standing constraint: no budget. Nothing paywalled.** S&P Global (spglobal.com, disclosure.spglobal.com) and
moodys.com return 403 to every fetcher we have; their article titles are visible in search indexes but bodies
are not. A gated source is a dead end to be reported, never a source to quote from a snippet.

## What we already tried, so the parcel does not re-ask it

| Route | Result |
|---|---|
| Moody's ABCP activity releases **mirrored free on finance.yahoo.com** | **The single best route.** Gives sponsor, administrator, "fully supported", collateral mechanics and often an outstanding figure. Worked for Columbia, Concord Minutemen, Lexington Parker, Gotham |
| Morningstar DBRS research pages | Free and worked (Mountcliff → 20 Gates Management) |
| Bloomberg LEI records (lei.bloomberg.com) | Free; gives registered address — which produced *address-match leads only*, not facts |
| SEC EDGAR full-text search + credit-agreement exhibits | Works; conduits appear as named "Conduit Lender/Purchaser" alongside their bank group |
| Fitch public ABCP Scorecard | Free but qualitative, undated, and covers bank conduits only — none of the eight |
| S&P articles, Moody's own site | **403 / gated. Titles only. Do not quote snippets as findings** |
| Sponsor websites | Northcross publishes its roster; the others do not |

---

```
ROLE. Research librarian and entity scout with live search. You establish WHO stands behind a named legal
vehicle, from sources you can actually open. You do not compute or conclude. Locations and attributions only.

GOAL. Output the COMPLETE return as ONE fenced Markdown code block and nothing outside it, so it can be saved
verbatim as  D8c_Sponsor_Identification_Return.md . Done means every vehicle (V1-V8) has a row and the
self-audit is filled in. State the date you ran. Expected length 1,500-2,500 words. If cut off, end at a
section boundary with <<CONTINUE>>.

## THE EIGHT RULES

R1. A COMPLETE ROW IS: vehicle - sponsor - administrator/manager - investment adviser (if distinguished) -
    programme type - the URL you OPENED - the document's date. Roles are often three different firms and the
    distinction matters: one known case is "sponsored by The Liberty Hampshire Company, managed by Guggenheim
    Treasury Services"; another is "BSN as Investment Advisor, BNY Mellon as administrator". Do not flatten
    these into "sponsor".
R2. NO IDENTIFIERS. No DOIs, report numbers, page numbers, quotations, CUSIPs or series codes. Issuer, title,
    date, URL. Identifiers you add unasked are deleted unread.
R3. NO DOLLAR SIGN ANYWHERE. Write "USD 1.3bn".
R4. A PAGE YOU DID NOT OPEN IS NOT A SOURCE. Search-engine snippets of gated pages are NOT evidence: report
    them, if at all, as "snippet only, unverified", never as the answer. State the HTTP status you got.
R5. NO TEMPLATE ROWS. Eight vehicles with the same shape of answer will be treated as fabricated. A field you
    did not verify is CANNOT DETERMINE.
R6. CANNOT DETERMINE is the expected answer for several of these and is worth as much as a hit. Say what you
    searched. We have already failed on all eight; you are not expected to solve all eight.
R7. Do not infer a sponsor from a vehicle's NAME, its ADDRESS, or its resemblance to another vehicle. Address
    matches are leads to state as leads, not conclusions. (We have two such leads and we are not using them.)
R8. Do not evaluate, summarise or comment on the research this serves.

## CONTEXT (do not act on it)

US money-market funds buy commercial paper issued by conduits. Some conduits are bank multi-sellers funding
trade receivables; a growing set are non-bank "aggregator" vehicles funding financial assets - Treasuries via
repo or securities-lending agreements, or total-return swaps over equities. We are mapping which is which. The
five aggregator sponsors named in trade press and law-firm material are Guggenheim, Nearwater, Mountcliff
(20 Gates), Northcross and Capitolis. The eight vehicles below are ones we cannot attribute to anyone.

## REQUIRED - one row per vehicle

V1  Verto Capital I - compartments A, C, D. A Luxembourg fonds commun de placement whose manager is
    ADG Verto Capital Management. WHO IS BEHIND ADG Verto Capital Management, and who originates the assets?
    Luxembourg registry filings, RAIF/AIFM registers, Luxembourg press, and the CSSF list are all fair game.
V2  HQLA Funding LLC, including series named Champlain, Huron and Tahoe. Sponsor unknown.
V3  Washington Morgan Capital Company LLC. Sponsor unknown.
V4  Intrepid Funding Company LLC. Sponsor unknown; nothing found at all.
V5  Overwatch Alpha Funding LLC and Overwatch Bravo Funding LLC. Structured on the same fully-supported
    securities-financing template as the Nearwater vehicles, but the sponsor is not established.
V6  Britannia Funding Company LLC, Alinghi Funding Company LLC, Mackinac Funding Company LLC - treat as one
    row with three sub-lines. Each is *suspected* to be a Nearwater or bank-counterparty securities-financing
    vehicle; none is confirmed. Confirm or refute per vehicle.
V7  Ionic Funding LLC (series exist) versus Ionic Capital II Trust and Ionic Capital III Trust. Capitolis
    Advisors is confirmed as investment adviser of Ionic Capital II Trust. Is Ionic Funding LLC the same
    family, and does Capitolis stand behind it? What does each fund?
V8  Capitolis itself - the firm. Which ABCP or note programmes does it sponsor, advise or manage, under what
    names, per its own site, its regulatory filings, its investor announcements, or press it participated in?

## ALSO USEFUL, IF AND ONLY IF FREE AND OPENED
- For any vehicle above: an OUTSTANDING amount with an as-of date.
- Any statement of what the vehicle's collateral actually is (Treasuries, equities, receivables, loans).

## OUTPUT - skeleton of D8c_Sponsor_Identification_Return.md

# D8c Sponsor Identification Return
Prepared: <date run> - Model: <model> - Word count: <n>

## 0. Plan (5 lines, written before searching)
## 1. Vehicles - V1...V8, each:
### V<n> - <vehicle>
- Sponsor:
- Administrator / manager:
- Investment adviser (if distinguished):
- Programme type and collateral:
- URL OPENED (and HTTP status):
- Document date:
- Outstanding, if stated (with as-of date):
- Confidence: VERIFIED (I opened a page stating it) / PARTIAL / CANNOT DETERMINE
- Searches run, if CANNOT DETERMINE:
## 2. Anything I found that you did not ask for - only with a URL you can open
## 3. SELF-AUDIT (completeness only - the reader verifies truthfulness independently)
- [ ] Every vehicle has a row (__/8)
- [ ] No identifiers; no dollar sign anywhere (I searched the output for it)
- [ ] Every VERIFIED row names a page I actually opened, with its HTTP status
- [ ] No snippet from a gated page is presented as a finding
- [ ] No sponsor inferred from a name, an address, or a resemblance
- [ ] No two vehicles share an identical answer shape unless the sources genuinely say so
- [ ] Every CANNOT DETERMINE lists the searches behind it
- [ ] If cut off, last line is <<CONTINUE>>

## REMINDERS
Roles are distinct: sponsor, administrator, adviser. Open the page or say you could not. CANNOT DETERMINE is
a real answer here and several of these probably have it. "USD", never the symbol. One fenced block.
```
