# W2 — AI-paper composition (DRAFT, 22 Sep 2026)

**Status: DONE 23 Sep — drafted by Grok 22 Sep; revised, checked and adjudicated by the supervisor under E-008.** Principal routed to Grok 22 Sep. Composes settled D2/D9/F1; refreshes the money-like leg as a floor only.
**Do not promote verbs.** No causal claim about equity prices (C-077). D2 already asked this question — do not write "nobody has asked."

---

> **ADJUDICATED 23 Sep (Claude, under E-008: *"You revise, you check, you adjudicate"*).** Grok's draft was sound in method —
> the Aug refresh labelled a floor, D2's collateral figure carried rather than zeroed, C-053's 36% kept, open gaps named — and wrong
> in frame. What changed: **(1)** each leg is now set against AI-company debt, not against money-fund assets or the whole bond
> market; **(2)** bank credit, the one channel that creates deposits, is named *in* the verdict rather than after it; **(3)** the
> fragility sentence is graded HYPOTHESIS and pointed at its calendar slot; **(4)** the `cik` column is relabelled and the eleven
> names searched are recorded.
>
> **The check also changed the supervisor's own proposal.** The 23 Sep review proposed "bank credit is material, ~12%
> outstanding, ~37.5% committed" and "~$300bn of undrawn lines is the sharpest fragility candidate." Re-reading the primary
> source before adopting it — which D2 had cited with no URL and no copy, now archived at
> `data/vintages/chicagofed_ai_tail_risk_2026-02/` — showed the $450bn is exposure to AI-adjacent **industries**, a
> classification already at ~$250bn of commitments in **2015**, and that the $1.2trn denominator is a **JPMorgan analysts'
> estimate**. Both overreaches are removed below (**C-115**).

---

## Verdict

**AI-company debt is held mainly by long money; bank credit is a real channel but smaller than its headline; money-market
funds are negligible.** Three legs, each against JPMorgan analysts' ~$1.2trn estimate of AI-company-issued debt — an
estimate relayed by the Chicago Fed (Feb 2026), not a measurement of ours.

| Leg | Size | Against ~$1.2trn | Grade |
|---|---:|---:|---|
| **Long money** — insurers, pensions, bond funds, rest of world | the bulk of the bond stock (Z.1 holder split, D2 §2) | most | MEASURED at sector level; AI names are not a separate Z.1 line |
| **Bank credit** — creates deposits at origination | ~$150bn outstanding / ~$450bn committed, large banks, late 2025 | ~1/8 | MEASURED as **industry** exposure; build-out share unmeasured (C-115) |
| **Money-market funds** | ~$0.26bn direct CP + ~$4.0bn repo collateral (D2 census, Jul 2026) | ~0.35% | MEASURED (census); Aug refresh $0.116bn is a floor |

**Long money.** The marquee test is Beignet/Hyperion ($27bn): registered funds hold 36% (C-053) — daily-redeemable money is a
material minority of even the deal most exposed to it; the rest sits with separate accounts, pensions and private vehicles.

**Bank credit** is where the goal's *direct money creation* applies without qualification, and the only leg where the size is
in the hundreds of billions. But the Chicago Fed's figure covers C&I lending to AI software and infrastructure companies,
data-centre construction and loans secured by data centres, and that classification **already stood at ~$250bn of
commitments in 2015**. The AI-era increment is ~$200bn of commitments over a decade; the article gives no 2015 outstanding
figure. So credit to the build-out itself is **some smaller, unmeasured part of the $150bn**. Plus project packages such as
Oracle/Vantage ($38bn, press-sourced) in their pre-distribution months (D2 §3).

**Money-market funds** hold AI paper mostly as repo collateral, which finances **dealers' inventories of AI bonds**, not the
companies. A complete money-fund withdrawal is bounded at ~$4bn. The "money-like leg" in the narrow sense the question
was first posed in is a rounding error; money creation in the sense the goal means is not.

**Fragility.** An MMF run on AI paper is not a channel — it is bounded at ~$4bn. On the bank side the Chicago Fed puts
outstanding AI-adjacent exposure at ~0.8% of bank total assets and ~9% of tier 1 capital on average, with delinquencies in
line with the portfolio: modest on current data. The ~$300bn gap between commitments and outstanding is the one place
drawdown could create deposits at speed — but it too is industry-wide, and whether it matters is the N2c §7 question on
the calendar for 1 Oct. **HYPOTHESIS until that work is done.** D2's "fragility is duration and operating leverage" is carried
on the same footing.

---

## 1. Money-like leg

| Source | Direct AI CP / instruments | As repo collateral | Notes |
|---|---:|---:|---|
| D2 N-MFP3 filing census (Jul 2026 window) | **≈$0.26bn** | **≈$4.0bn** | Filing-by-filing; collateral-issuer field used. Carry this. |
| W2 aggregate refresh (Aug-2026 vintage on disk) | **$0.116bn** (AMZN 0.100, AAPL 0.012, MSFT 0.004) | **not observable in this file** | `data/w2/nmfp_ai_aug2026_totals.json`. Floor only. |

**Names searched** (supervisor re-run, 23 Sep, all 44,674 rows of the aggregate): Alphabet/Google, Amazon, Apple, Meta,
Microsoft, NVIDIA, Oracle, CoreWeave, Broadcom, AMD, Tesla. Only Amazon ($99.96m), Apple ($12.28m) and Microsoft ($4.15m)
appear — $116.39m, matching the draft exactly. So "floor" has two reasons: no collateral field, and the aggregate carries
only three of the eleven names.

**Reading.** Order of magnitude of the direct leg is unchanged (tenths of a billion). Do **not** replace D2's ~$4bn collateral figure with "zero" from the aggregate file — that would be a method error, not a finding.

---

## 2. Long-money leg (carried)

From D2 §2 / Z.1 M3s_Q 2026Q1, US corporate-and-foreign bonds **$17.2trn**: ROW ~$4.9trn, life insurers ~$3.9trn, mutual funds ~$2.6trn, pensions ~$1.6trn, MMFs **$22bn (0.13%)**. AI paper is a slice of that stock, not a separately published Z.1 line — holder inference is by instrument class plus deal-level census.

**Deal test — Beignet / Hyperion $27bn (C-053 full N-PORT):** registered funds hold **$9.81bn (~36%)**, of which PIMCO registered ≈$6.6bn. Daily-redeemable share is a material minority; the other ~64% remains outside that perimeter (separate accounts, pensions, private vehicles). Verdict in D2 §6 survives; the earlier sampling-based estimate of the separate-account share is dead (C-053).

---

## 3. The one money-creation channel

Folded into the verdict above, where it belongs. Source facts and their limits: `data/vintages/chicagofed_ai_tail_risk_2026-02/README.md`
and **C-115**.

---

## 4. Issuers as cash pools (S-D9 pointer)

The six AI-capex firms held ~**$630bn** cash and short-term investments at mid-2026 (D2), and ~**$146bn** of corporate debt securities inside those pools (S-D9). Whether they hold *each other's* AI paper is not disclosed at issuer level — a sized measurement gap, not a null. W2 does not reopen D9.

---

## 5. How this sits with F1 / ANSWER §3a

Hyperscaler **capex** is mostly self-funded from operating cash (five of six); the large financing stock that matters is **off-balance lease commitments**, not a money-fund bid for AI bonds. W2's holder picture is consistent with that: the bonds that do exist are long-money held; the money-like system is not the marginal buyer.

---

## 6. Still open (named, not worked tonight)

| Gap | Why it matters |
|---|---|
| Insurer Schedule D at issuer level | Would pin the non-registered share of Beignet-class deals |
| ROW issuer detail | TIC/Z.1 do not give AI-name splits |
| Private-credit / DDTL funding base | Form PF aggregates do not name issuers |
| Re-run Beignet N-PORT on next SEC bulk when posted (~early Oct for 2026Q3) | Calendar item; method proven |
| Collateral-side N-MFP refresh via filing XML (not aggregate CSV) | Needed before any claim that the ~$4bn collateral leg moved |

---

## 7. What not to say

- That MMFs "fund the AI buildout."
- That Beignet is "mostly separate accounts" without the C-053 36% registered share.
- Any scalar M linking this holder split to the equity multiple.
- "Nobody has asked" — D2 asked; W2 composes.
- That bank credit **to the AI build-out** is ~$150bn / ~$450bn — that is industry exposure, ~$250bn of it in place by 2015 (C-115).
- That the ~$1.2trn is a measurement — it is JPMorgan analysts' estimate.
- That ~$300bn of undrawn lines is "the sharpest fragility candidate" — HYPOTHESIS, and industry-wide.

---

## Pointers

- Parent census: `2026-08-22-D2-Who-Holds-The-AI-Paper.md` (S-D2)
- Reflexivity gap: `2026-08-24-D9-Does-The-AI-Complex-Fund-Itself.md` (S-D9)
- Refresh artifacts: `data/w2/nmfp_ai_aug2026.csv`, `data/w2/nmfp_ai_aug2026_totals.json`
- Brief: `_research/2026-09-22-W2-AI-Paper-Composition-Brief.md`
