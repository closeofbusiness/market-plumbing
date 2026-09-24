# Parcel A return — the interlock, adjudicated

*22 August 2026. Return from the first of the three single-purpose parcels. **The format change
worked**: this return is materially better than the omnibus — sourced to methodology documents
rather than summaries, and it answers the question actually asked. Recorded because the parcel
design is now evidence-backed, not a hunch.*

---

## 1. The finding that changes our own position

**The net-vs-gross problem has a resolution better than the rule I wrote this morning.**

C-042 established: *net for stocks, never for velocity, never report one number as serving both.*
That rule is not wrong, but it is a counsel of care. The statistical literature has a
constructive answer instead — **the "from-whom-to-whom" approach**: build a fully populated N×N
bilateral matrix of who holds whose claims, and you can **mechanically switch** between a
consolidated (netted) view for credit creation and an unconsolidated (gross) view for network
and contagion analysis. You stop choosing.

Attributed to BIS Irving Fisher Committee, *IFC Bulletin No. 36* (Feb 2013), and Castrén &
Kavonius, ECB Working Paper No. 1682 (2014). **Both unverified by us — check before citing.**

**Why this matters beyond tidiness.** Our channel map is a set of nine sector aggregates, and
the claim in the literature is that aggregate sector tables are *structurally unable* to
distinguish real credit creation from intermediation layering. If that holds, no amount of care
with our nine silos fixes the problem — the fix is a different data structure. **This is a
candidate re-architecture of the measurement work, and it should be decided deliberately rather
than drifted into.**

> **C-042 is amended, not killed.** The rule stands as a discipline for anything we publish. The
> who-to-whom construction is the better long-run answer and is now a named option.

## 2. The vocabulary we were missing — partially confirmed

**"Financial layering", from Raymond Goldsmith, *Financial Structure and Development* (Yale,
1969).** The layering ratio: intra-financial-sector assets over total financial assets.

**Verified by us, 22 Aug:** the concept is genuinely Goldsmith's — he distinguishes *layering
among major economic groups* from *layering within major sectors*, i.e. financial
interrelations among units inside a sector. **Real, and a 57-year-old literature we did not know
existed.**

**Overclaimed:** Gemini called it *"the official SNA/ESA term"* for the phenomenon. That
standardisation claim did **not** verify — the term surfaces in academic discussion *of*
Goldsmith's method rather than as a codified national-accounts standard. **Use the concept and
the citation; do not assert it is the official term.**

> **Possibly an estimable object for us.** A layering ratio — intra-financial assets over total
> financial assets — looks constructible from Z.1. If so it is a direct, published-data measure
> of exactly the thing this project has been circling. **Candidate Tier-1 build; verify
> constructibility before committing.**

The return also gives two other terms of art, which we should use as search keys: *collateral
velocity / collateral multiplier / collateral chains* (Singh; Infante et al.), and *gross vs net
intermediation / "pyramiding of claims"* (Adrian–Ashcraft–Boesky–Pozsar; Mehrling).

## 3. The netting conventions — usable, with one correction to an earlier return

| Publisher | Verdict returned | Note |
|---|---|---|
| **Z.1 Financial Accounts** | **GROSS**, unconsolidated across sectors | Only netting is what comes in from source reports under GAAP (ASC 210-20 / FIN 41 matched-book repo) |
| **FSB narrow measure** | **MIXED** | Gross of inter-NBFI cross-holdings; **nets** entities prudentially consolidated into banking groups |
| **BIS LBS** | **GROSS** | And **intragroup positions are included gross** — deliberate double-counting of funds routed through international hubs |
| **OFR repo collections** | **GROSS**, trade-level | No netting of borrowing against lending, or collateral received against delivered |
| **IMF GFSR NBFI** | **GROSS** | With a stated rationale: netting distorts run-risk analysis because calls operate on gross contractual positions |

**This corrects the earlier omnibus return.** Its item A4 said the FSB narrow measure does
**not** net, full stop. The correct answer is **mixed** — it does net bank-consolidated
entities. The refinement matters: it means the FSB measure is neither a clean gross figure nor a
consolidated one, and it cannot be treated as either.

**The IMF's rationale is the most useful sentence in the table**, and it generalises: *gross is
the right basis when the question is what happens under stress, because margin and collateral
calls run on contractual positions, not net economic exposure.* That is a principled rule for
when to prefer gross, and we did not have one.

## 4. The BIS LBS point bears directly on our offshore-dollar numbers

LBS is gross **and includes intragroup positions**. Our offshore work rests on three figures on
three perimeters — $2,040bn gross claim expansion, $1,650bn liability-matched, $754bn owed to an
identified non-bank. **If a material share of the gross figure is inter-office transit rather
than credit to end-users, the gross number is measuring something other than what we have used
it for.**

**The number offered for this is NOT usable.** The return attributes a **30–45%** overstatement
of global dollar liquidity from double-counted inter-office loops to Avdjiev, Hardy, McGuire &
von Peter, *"Using BIS statistics to understand global liquidity and double counting in
cross-border banking"*, **Economic Policy 33(96), Oct 2018, pp. 657–706**.

**Verified by us, 22 Aug: two searches failed to surface that title in that journal, and the
30–45% figure is unattached to anything reachable.** The four authors are real and work on
precisely this problem, so this is **"origin not reached"**, not "fabricated" — but the figure
is load-bearing and **must not be used until the paper is in hand.** *This is now the highest-
value verification task outstanding, because it bears on a conclusion we have already published
internally.*

## 5. Documented overlaps — real, but note what happened

Nine overlaps returned, each with a citation. **Five are new to us** and worth having:
offshore reinsurance ModCo / funds-withheld duplication across the US statutory balance sheet and
the Bermuda reinsurer; PE NAV-loan leverage stacked over portfolio-company debt against the same
cash flows; FX-swap dollar borrowing off-balance-sheet while the asset is on it; private-credit
AUM against bank subscription and NAV facilities; and prime-brokerage margin.

**But four of the nine are the four I supplied in the prompt, all confirmed.** By C-045 that is
the weakest part of the return — I asked "confirm, refute, or add", and got 4/4 confirmation.
Unlike a number, each is a structural claim with a citation, so they are checkable; **treat them
as leads with sources, not as established.**

> **One overlap bears directly on Parcel B, already sent.** Row 9 claims prime-brokerage margin
> loans to hedge funds appear in **FINRA margin-debt statistics** *and* on the dealer's Call
> Report simultaneously. If FINRA margin debt includes hedge-fund prime-brokerage balances, that
> materially changes what the margin-debt ratio measures — which is exactly Parcel B task 1.
> **Cross-check the two returns against each other when B comes back.** They were sent as
> independent parcels and this is a live opportunity for a genuine consistency test.

## 6. The high-value negative

**No consolidated, unduplicated measure of non-bank credit or money-like claims exists** across
these channels. Nobody has built it — and the **G20 Data Gaps Initiative (DGI-2/DGI-3)**
reportedly names the absence of a consolidated global non-bank balance sheet as an unresolved
statistical gap.

This is the third such negative in two days, after A1 (no extension of Pozsar's aggregate) and
A2 (no satellite accounts). **The pattern is now the finding:** the measurement apparatus for the
nexus does not exist, and its absence is documented by the bodies who would have built it. That
is a stronger and more defensible claim than anything we were going to say about a specific
number, and it belongs in the essay.

## 7. What this changes

- **C-042 amended** — who-to-whom is the better answer; the rule remains the publishing discipline.
- **New verification task, top of the list:** obtain the Avdjiev et al. paper and settle the
  30–45%. It bears on a conclusion we already hold.
- **New candidate build:** Goldsmith layering ratio from Z.1. Check constructibility first.
- **New candidate re-architecture:** from-whom-to-whom, versus nine sector silos. A real
  decision, not a refinement.
- **Parcel B cross-check queued** — FINRA margin debt and prime brokerage, §5 above.
- **Parcel A itself is answered.** N4's internal re-read is unaffected and still unstarted.
