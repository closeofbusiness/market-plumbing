# E1 — European pensions and the long end: the Dutch transition is a relabelling, not a sale (14 Sep 2026)

**Status: SCOUT COMPLETE, and it refutes the thesis it was sent to test.** Data
`data/e1_european_pensions/` (8 CSVs). Supervisor-verified 14 Sep.

## The thesis, and why it does not hold on current data

The premise was that the Dutch DB-to-DC transition removes long-duration demand — a forced seller of long
bonds, changing the term premium and feeding the discount rate in everything else we measure.

**At the moment of legal conversion the portfolio does not change.** Two independent official statistical
systems show it, and I verified the numbers myself.

**EIOPA, asset side, 2025:Q4 → 2026:Q1:** DB total assets €1,621.0bn → €1,085.8bn (**−€535.2bn**) while DC
rose €63.7bn → €602.3bn (**+€538.6bn**). A near-exact mirror in a single quarter, against a DC book that had
been creeping up €31.7bn → €35.4bn → €51.9bn → €63.7bn over the prior two years.

**And the newly-DC book is the old DB book wearing a different label.** Shares of investments, 2026:Q1,
recomputed by me from the EIOPA balance sheet:

| | DB | DC (newly converted) |
|---|---|---|
| bonds | 40.3% | **40.6%** |
| equities | 26.1% | 24.0% |
| derivatives | **−6.3%** | **−9.8%** |

The negative derivatives line is the swap-book signature of interest-rate hedging, and it **carries straight
across the conversion** — if anything larger in the converted book. ECB's independent liability-side series
shows the same reclassification, and its aggregate NL debt-securities holdings show no discontinuity through
the quarter.

**Consequence: any reduction in duration demand operates later and slowly** — through lifecycle glide-paths
shifting younger cohorts out of duration as their share of the pot grows, and through gradual unwinding of
collective hedging as funds settle into steady-state policy. Not as a one-time stock adjustment. The data
cannot yet quantify that slower channel because the earliest large converters are one or two quarters in.

## The schedule is correct and less solid than it looks

**1 January 2028 is right — but it is a moved deadline.** Wtp took effect 1 July 2023 with an original
deadline of **1 January 2027**. On **2 December 2025** the Eerste Kamer extended it by a year. **The same
bill relocated the deadline out of the primary statute into an AMvB** — a government administrative order —
explicitly so further extensions need no full parliamentary process. It has slipped once and the machinery
was deliberately loosened to let it slip again.

Progress: 30 funds by 1 Jan 2026 (~1/3 of assets); 34 funds and €589bn of €1,720bn (34.2%) by 30 Jun 2026.

## Natural-experiment verdict: usable, with a design constraint

Better than the fallback the brief expected. The size and timing **are** documented (DNB quarterly
transition updates), and there **are** two independent, free, quarterly flow counterparts (EIOPA IORP
balance sheet by scheme type; ECB PFBR pension entitlements) that corroborate each other.

**But the design must be keyed to each fund's own conversion quarter, not to a single date.** Funds convert
continuously to 2028, and the date has already moved. And what is observable so far is the **stock
reclassification**, not a rebalancing flow — because the evidence says the rebalancing has not started.
A design must track transitioned funds *forward* from their conversion quarter looking for drift, not assume
a level break at conversion.

**This is a materially better position than the sovereign-mandate design that died on 13 Sep.** There the
flows were unobservable at any frequency. Here they are observable quarterly from two sources; what is
missing is elapsed time.

## Three official sources disagree on the size of the system by 20%

Same quarter, three answers: **DNB €1,720bn** (30 Jun 2026, supervisory population), **EIOPA €1,688.1bn**
(31 Mar 2026, IORPs only), **ECB €1,960.9bn** (31 Mar 2026, ESA2010 sector S.129). A spread of about
**€330bn**. Never quote a size for the Dutch system without naming the source.

**Scale, for context:** the Netherlands is €1,688bn of an EU IORP total of €2,854bn — **59% of all EU
occupational-pension IORP assets.** (Caveat: EIOPA's framework excludes countries whose second pillar runs
through insurers, so this overstates the share of *all* EU occupational pensions.)

## Two practical notes worth more than they look

- **ECB dataflow `PFB` is discontinued** — it stops at 2019:Q4 for every country checked. The live series is
  **`PFBR`**, same item and structure codes. Using the dead one would silently produce an empty design.
- **UK comparison (Purple Book 2025, PPF, read at source):** £1,068.1bn DB/hybrid assets at 31 Mar 2025,
  **70.6% in bonds**, 15.1% equities, 12.9% annuities (a record). Cash and deposits are reported at
  **−7.9% of assets**, which PPF itself attributes to swap and repo collateral inside LDI — direct evidence
  of leveraged interest-rate hedging at sector scale.

## Gaps, stated

- **dnb.nl returns HTTP 403 to every scripted request** (Akamai WAF), reproducing the 13 Sep finding exactly.
  DNB figures here were read through a non-scripted fetch path, not parsed from raw HTML like the EIOPA and
  ECB numbers. No bypass was attempted.
- **The often-quoted "Dutch pensions hedge about half their interest-rate risk" could not be verified** at a
  current dated DNB primary source. It traces to older statements via secondary commentary. **Do not use the
  ~50% figure until someone sources it.**
- ONS's pension-flow-into-gilts series (MQ5) was discontinued after 2018:Q4.
