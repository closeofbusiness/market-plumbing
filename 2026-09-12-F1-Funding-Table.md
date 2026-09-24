# F1 — the AI build-out funding table, first closure (12 Sep 2026)

**Status: PRIMARY EVIDENCE, with the residual honestly negative.** Ranked item 7. Data:
`_research/2026-09-12-F1-funding_table.csv` (125 rows, long format), `-gaps.csv`. Six companies: Alphabet,
Amazon, Meta, Microsoft, Oracle and NVIDIA (the consistent sixth in this project's own earlier passes, and
structurally unlike the others — capital-light, and a financier of other firms' build-outs rather than a big
spender itself).

**The headline numbers (mixed fiscal periods — NOT a synchronised cross-section; see the table for each basis):**
capex about **$594bn** over the latest twelve months against identified funding legs of about **$1,166bn**, so
every company's flow residual is negative. That is not over-funding: capex is accelerating faster than a trailing
window captures (Alphabet alone guides 2026 to $180-190bn against $132bn trailing), and several 2026 raises are
new instruments being set against a trailing period that predates them.

**What the table actually establishes**
- **Only Oracle cannot fund its own capex from operations:** internal cash $40.8bn against capex $75.7bn, a ~$35bn
  shortfall. The other five generate more than they spend — which is why they have been able to fund the build-out
  from cash flow and still pay for the rest with bonds and, newly, equity.
- **The biggest commitments are not on any balance sheet.** Purchase obligations and guarantees are stocks and
  contingent ceilings, not this period's cash, so the agent deliberately kept them OUT of the residual — the right
  call, and both versions are in the CSV. Their size: Alphabet $811bn of purchase commitments; NVIDIA a $366bn
  forward commitment schedule; Meta $279bn; Microsoft $194bn plus $35bn of construction; Amazon $130bn; Oracle
  $34bn (plus its separate $288bn of not-yet-commenced data-centre leases, `2026-09-12-Oracle-RPO-And-Financing.md`).
- **NVIDIA guarantees $105bn of its own customer's build-out.** Verified by the supervisor at source in NVIDIA's
  10-Q: guarantees "capped at a total of $105 billion" providing credit support on a land, power and shell
  build-out with affiliates of SB Energy Corp., on behalf of an affiliate of OpenAI Group PBC, for about 4.25
  gigawatts at the PORTS Technology Campus in Pike County, Ohio, under 20-year leases, each guarantee effective as
  a phase commences (from fiscal 2029). With $3.5bn pre-existing, NVIDIA's guarantee book is $108.5bn. This is the
  filed, quantified version of the "circular financing" claim the project had only as an assertion.
- **Bank credit is the weakest-sourced leg.** Amazon's $17.5bn term loan was still UNDRAWN at 30 June and its
  single-draw window closes 30 Sep 2026 (now a calendar row); Meta discloses no facility at all; Oracle shows a
  small net repayment without the facility behind it.

**Disagreements recorded, not smoothed:** Microsoft's buybacks are $22.271bn in the cash-flow statement against
$16.7bn in its own commentary; Oracle's itemised 2026 bond deals ($43bn) still fall ~$3bn short of its XBRL debt
proceeds; Alphabet's Canadian-dollar notes total C$9.5bn in the 8-K's text but C$8.5bn across its listed tranches;
and NVIDIA's purchase obligations only appear to halve — the tag changed, while the prose schedule more than
doubled in a quarter ($119bn to $279bn).

**Supervisor verification (12 Sep):** the NVIDIA guarantee read at source, wording as quoted above. The other
cells are the agent's, each marked SOURCED with its tag or filing, or NOT AVAILABLE — none estimated.

---

## The agent's return (Sonnet)

## Summary

Built the AI build-out funding table for the six companies most consistently grouped in this project's own prior work (Alphabet, Amazon, Meta, Microsoft, Oracle, **NVIDIA** as the supported sixth — see rationale below). All SEC access used the declared `ThirdDerivativeResearch/1.0` User-Agent to sec.gov hosts only, ≥1s between the 18 requests made (6 XBRL company-facts pulls + 12 filing-index/document fetches), all in the foreground, all HTTP 200 — no 403/429 encountered, so no stop-and-report was triggered. Reading actual filing prose (not just XBRL) closed several gaps the project's prior passes had flagged as blocked or missing (Microsoft's entire purchase-obligation disclosure, Amazon's stale purchase-obligation tag, Alphabet's and Amazon's bank-credit-facility draw status, NVIDIA's bond issuance and the exact SB Energy/OpenAI guarantee).

**Deliverables:**
- `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/wave2/f1/funding_table.csv` (125 data rows, long format)
- `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/wave2/f1/gaps.csv` (9 gap rows)
- Supporting raw filings/XBRL and the two build scripts are in the same folder (`raw/`, `extract.py`, `build_csv.py`) for provenance — not deliverables themselves, no .md report written.

**NVIDIA as the sixth company:** it's the consistent 6th name across this project's own D9, Guarantee-Stack, and DG passes. Flagging explicitly: NVIDIA is structurally unlike the other five — a capital-light chip/IP designer, not a data-center operator. Its own capex is tiny, but it is a major *financier/guarantor* of others' buildouts (see below).

## The table (compact; $bn; fiscal basis stated per company)

| Company | Fiscal basis | Capex (latest 12mo/actual) | 2026 guidance | Op CF (12mo) | Internal cash | New equity | New bonds | Bank debt | Lease additions | **Legs (flow) total** | **Residual** |
|---|---|---:|---|---:|---:|---:|---:|---:|---:|---:|---:|
| Alphabet | CY, TTM to 30 Jun 26 | 132.4 | 180–190 | 185.7 | 158.4 | 49.6 | 89.4 (+24.8 not yet in XBRL) | 1.3 (of 11.7 facility) | 8.2 | 306.8 | **−174.4** |
| Amazon | CY, TTM to 30 Jun 26 | 173.0 | NOT AVAILABLE | 161.4 | 161.4 | 0 (NA) | 81.9 | 0 drawn (17.5 committed, undrawn, window closes 30 Sep 26) | 28.9 | 272.3 | **−99.2** |
| Meta | CY, TTM to 30 Jun 26 | 89.3 | NOT AVAILABLE | 130.3 | 121.6 | 0 | 54.8 | NOT AVAILABLE | 7.6 (FY25 basis, not TTM) | 184.1 | **−94.7** |
| Microsoft | FYE 30 Jun, FY2026 actual | 115.9 | NOT AVAILABLE (FY closed) | 182.9 | 134.2 | 2.0 | 0 (confirmed) | 0 (confirmed) | 29.2 | 165.4 | **−49.4** |
| Oracle | FYE 31 May, TTM to 31 Aug 26 | 75.7 | NOT AVAILABLE | 46.9 | 40.8 | 25.1 | 46.1 (vs 43 itemized) | −0.8 (net repayment, latest qtr) | 25.3 | 136.5 | **−60.8** |
| NVIDIA | FYE ~25 Jan, TTM to 26 Jul 26 | 7.4 | NOT AVAILABLE | 134.4 | 72.3 | 0 | 24.9 (new; $33.5bn total o/s) | NOT AVAILABLE | 3.8 (op. only) | 100.9 | **−93.6** |
| **TOTAL** | mixed periods — not a synchronized cross-section | **593.7** | n/a (only Alphabet gives one) | — | **688.6** | **76.7** | **297.1** | **+0.5** (not meaningful as a sum) | **103.0** | **1,166.0** | **−572.3** |

**Stocks kept OUT of the residual** (purchase obligations and off-balance-sheet guarantees are all-future-years balances/contingent ceilings, not period cash inflows — see "where I deviated from the brief" below): Alphabet $811.0bn purchase commitments + ~$51.4bn live guarantees (+$24.1bn not-yet-effective); Amazon $130.1bn (total commitments incl. debt/leases $650.0bn); Meta $279.0bn + ~$28bn live/~$13bn unbuilt (El Paso) guarantee; Microsoft $194.1bn purchases + $34.6bn construction (grand total everything $743.8bn) + nil guarantee; Oracle $34.2bn + $3.3bn guarantee (expires Sept 2026); NVIDIA $22.7bn balance-sheet / $366bn full forward-commitment schedule + **$108.5bn guarantee** ($3.5bn pre-existing + **$105.0bn capped guarantee for SB Energy Corp.'s PORTS Technology Campus buildout on behalf of OpenAI**, entered Aug 2026, explicitly **unbuilt** — effective only on phased lease commencement starting FY2029).

## Residual, and what it implies

Every company's flow residual is **negative** — identified funding legs exceed trailing-12-month capex everywhere, total −$572.3bn. This is not "overfunding" so much as: capex is accelerating faster than a trailing measure captures (Alphabet's own 2026 guidance of $180–190bn is ~40% above its TTM actual), and some 2026 raises are point-in-time-new instruments being compared against a trailing window that predates them. The one real cross-company asymmetry: **Oracle is the only one of the six whose internal cash alone ($40.8bn) falls short of its own capex ($75.7bn)** — a genuine ~$35bn operating shortfall the other five don't have, consistent with its credit-stress narrative elsewhere in this project. NVIDIA's story is different in kind: capex is trivial relative to its cash generation, and its $24.9bn new bond and $108.5bn guarantee book show it funding *other companies'* buildout, not its own.

**Where I deviated from the brief:** the brief asks for residual = capex minus *all* the bulleted legs, including purchase obligations and off-balance-sheet vehicles. I did not fold those in, because they are stock/contingent figures (all-future-years commitments or contingent guarantee ceilings), not cash that funded this period's capex — mixing them in produces a number that looks like it means something but doesn't (e.g., Alphabet's residual would balloon to roughly −$1,037bn, dominated by a decade-plus of supply commitments). Both figures are in the CSV; flagging this explicitly rather than silently picking one.

## Three biggest unsourced gaps

1. **Bank debt is the weakest leg across the board.** Meta: zero mentions of any credit facility anywhere in its 10-Q (genuinely absent or just below disclosure threshold — can't tell which). Amazon: $17.5bn term loan confirmed *undrawn* as of 30 Jun 26, with its single-draw window closing **30 Sep 2026** — time-sensitive and unresolved. Oracle: a small net-negative "short-term financing related to capex" line was found, but not the facility behind it. *Settle it:* an 8-K after 30 Sep for Amazon; Oracle's debt note in full; an EDGAR full-text sweep for Meta.
2. **No named off-balance-sheet vehicle for 4 of 6 companies.** Only Meta (Louisiana Venture/El Paso) and NVIDIA (SB Energy/PORTS) have an identifiable SPV. Alphabet's own 10-Q points at unconsolidated VIEs and cross-references "Note 10" for guarantees, which I did not open this pass. *Settle it:* read that Note 10 directly; EDGAR full-text search for "Special Purpose Entity"/"Venture" for Amazon, Microsoft, Oracle.
3. **NVIDIA's own guarantee/commitment disclosures don't fully reconcile with each other** — $108.5bn (XBRL) does equal $3.5bn + $105.0bn cleanly, but a separate prose table ("Additional Commitments," $56bn) doesn't obviously map onto either. This is the single largest off-balance-sheet number in the entire table. *Settle it:* read Notes 8 and 10 in full rather than the excerpts pulled this pass.

## Where two sources disagree

- **Microsoft buybacks, same filing:** cash-flow-statement tag = $22.271bn (FY2026, all repurchases) vs MD&A prose = $16.7bn ("36 million shares... through our share repurchase program"). ~$5.6bn gap, most likely tax-withholding share settlements included in one and not the other — not confirmed from the text.
- **Oracle bonds:** itemized registered deals sum to ~$43bn face vs FY2026 XBRL debt-proceeds of $46.093bn — a ~$3bn gap first flagged in this project's F1 pass, still open.
- **Alphabet's CAD notes:** the 8-K's own intro sentence says C$9.5bn; its four itemized tranches sum to C$8.5bn (F1 finding, restated here since it feeds the bond total).
- **NVIDIA purchase obligations look like they halved** ($45.774bn Jul-25 → $22.7bn Jan-26) but this is an XBRL tag-scope change (old tag "PurchaseObligation" discontinued, replaced by "UnrecordedUnconditionalPurchaseObligationBalanceSheetAmount"), not a real decline — the much larger, fresher prose table shows supply commitments alone *more than doubling* in one quarter ($119bn → $279bn).
- **NVIDIA's guarantee, resolved not contradicted:** the prior pass's preliminary $105bn (from an 8-K) is now confirmed and exactly reconciled in the audited 10-Q ($105.0bn + $3.5bn = $108.5bn), naming OpenAI as tenant for the first time.
