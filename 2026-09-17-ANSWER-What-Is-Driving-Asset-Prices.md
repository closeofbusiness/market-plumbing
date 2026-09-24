# The answer — what is driving asset prices, and where the money came from (17 September 2026)

**Status: THE ANSWER as it stands. Supersedes [`2026-09-14-SYN-What-We-Can-Say.md`](2026-09-14-SYN-What-We-Can-Say.md), which is now a pointer.**
Serves the canonical goal in [`THE_ASK.md`](THE_ASK.md). Standard of evidence is **E-005**: a rough understanding with
bands, not proof to the last cent. We never pay for data. New to this repository? Its codes (C-, E-, P2a …) and abbreviations are
explained in the [README glossary](README.md#glossary).

> **This document restates almost no numbers on purpose.** Every figure below lives in one findings doc,
> named inline, and that doc is the authority. Three of this fortnight's corrections (C-081, C-089, C-092)
> were caused by a figure being copied into a second place and then going stale there. Read the pointer,
> not a copy. Run `bin/check.sh --latest` before quoting anything.

---

## The answer in one paragraph

**Prices rose mostly because earnings rose.** What the multiple added on top was held up by a *compressing
risk premium against rising real rates* — not by cheaper money. **On the money side the headline finding is a
measurement result, not an economic one:** the line everyone reads as "equity issuance" in the Financial
Accounts is mostly **ETF wrapper creation**. Strip the wrapper and US operating companies **retired** equity
over 2024:Q1–2026:Q2. So the money arriving met a **shrinking float** of operating-company equity. What we
**cannot** say is how much of the price move that money *caused*: four designs to measure it have now closed,
and we can say precisely why each one closed.

**Across the channels the goal names, the honest verdict is mostly negative, and that is a result.** The
shadow-money and collateral channels the original hypothesis centred on are **not where the equity money came
from over this window**: 2024 wholesale-repo growth was a handoff out of the Fed's reverse-repo facility, not
new cash, and collateral re-use intensity did not rise. The **AI build-out is funded mostly from operating cash
flow** — five of six hyperscalers out-earn their capex — with the real financing innovation sitting **off
balance sheet** in lease commitments. The **IPO boom** is two-thirds a single deal. See §3a.

---

## How to read every number in this document (E-007, 22 September)

The principal's ruling: *"Nothing here is certain if not clearly mathematically proven, thus everything needs to be
looked at as potential hypothesis that needs testing."*

**The default grade of every claim below is HYPOTHESIS.** A claim is only something stronger where it says so
explicitly. That inversion is the point: nothing here earns certainty by sitting in the authoritative document.

| Grade | What it means | What it does NOT mean |
|---|---|---|
| **IDENTITY** | Holds by construction, given its inputs. | That it says anything about the world. **An identity that sums exactly cannot fail, so the sum is not evidence** (C-098). |
| **MEASURED** | Observed on a stated universe with a stated denominator. | That the universe was the right one, or that the tags, coverage and survivorship are innocent. |
| **BOUNDED** | A ceiling or a floor exists — one side only. | An estimate. **Never quote a bound in the register of a point figure** (C-096). |
| **HYPOTHESIS** | Untested, or tested and survived. | Established. **Survival raises credence and proves nothing.** |

Three specific consequences, all of which have already bitten:

- **A residual is the weakest number in its table, not the strongest.** Solve for a term and it absorbs every error in
  every other term. Where the term can also be measured directly, measure it and **report the gap** — that gap is the
  only falsifiable thing in the exercise (C-098: a 0.073 log gap sat hidden inside one for a day).
- **Every term of an identity must be on the same universe** — same constituents, window, and per-share basis — or the
  mismatch silently becomes part of whichever term was solved for.
- **"It survived adversarial review"** is a statement about our attacks, not about the world. Every correction this
  programme has recorded was found by someone attacking a claim that had already survived.

---

## 1. What drove prices

- **Earnings did most of the work** — **71.0% to Dec-2025, 82.3% to Jun-2026** [MEASURED; the two endpoints P2a
  actually computes]. The "70–80%" this document carried until 22 Sep excluded P2a's own second row (**C-100**), and the
  Jun-2026 figure is partly tax-assisted (**C-098**, §6) → [`2026-09-11-P2a-Return-Decomposition.md`](2026-09-11-P2a-Return-Decomposition.md).
- **It survived a second test: it is mostly real profit, not buybacks.** Of the earnings contribution, per-share
  accretion from shrinking share counts is **at most roughly a tenth to a sixth** — **a ceiling, not an interval**
  [BOUNDED, one-sided]. The 7–13% spread is across **aggregation methods**, not endpoints and not statistical
  uncertainty, and C-093 finds survivorship pushes **every** member of it upward, so the truth sits below the band
  rather than inside it (**C-101**). The missing-mega correction is unsigned. The panel behind it is **not on disk**
  (**d3**) — [`2026-09-18-EPS-Split.md`](2026-09-18-EPS-Split.md).
- **It survived its disconfirming test.** Depreciation-life extensions explain only 5–11% of six megacaps'
  net-income growth → [`2026-09-13-E2-Earnings-Quality-Useful-Lives.md`](2026-09-13-E2-Earnings-Quality-Useful-Lives.md). Amazon reversed; the finding held.
- **The earnings yield barely moved while real yields rose** [MEASURED] — Dec-2023 → Jun-2026 real yields **rose 0.34
  points** while the earnings yield fell only 0.14, so the multiple held up. **That is the whole observation.**
  The "premium compressed ~49bp" restatement of it is **not a second fact** (**C-102**): the premium is *defined* as
  `E/P − real yield`, so **70.7% of that 48.59bp is the arithmetic mirror of the same 0.34-point rate rise**, and only
  the 29.3% earnings-yield leg is new information. The Shapley rate/premium split is an IDENTITY whose two legs are
  near-identical rescalings of one quantity (slopes −6.217 vs −6.195). Damodaran's −40bp and the SPF's −19bp move
  the same way for the same structural reason — **a bond leg rising faster than the equity leg in all three** (+34.35bp,
  +57bp, +34.52bp); in the SPF, equity expectations actually **rose**. Agreement, but not independence →
  [`2026-09-12-P2c-Rates-vs-Risk-Premium.md`](2026-09-12-P2c-Rates-vs-Risk-Premium.md).
  **Read that doc's C-078 header first:** the *window compression* survives, the *level/counterfactual* claim
  is dead. Do not quote a "% above a constant-premium counterfactual".
- **It arrived as drift, not as events.** Ordinary days carry the bulk; FOMC beats earnings head-to-head
  → [`2026-09-14-P5i-Event-Study-Result.md`](2026-09-14-P5i-Event-Study-Result.md).
- **What did NOT resolve:** whether the compression was cheaper risk or better growth expectations. The split
  is withdrawn (**C-082**) — the survey premium fell on its **bond** leg while equity expectations *rose*.

## 2. The supply side — the correction that reframes the money question

Z.1's "corporate equities" instrument **counts ETF shares as issuance**. Once that is classified
([`2026-09-15-ETF1-Identity-Net-Of-ETF.md`](2026-09-15-ETF1-Identity-Net-Of-ETF.md), **C-081/C-083**), the 2024:Q1–2026:Q2 issuance identity reads:
ETF share creation **+$3,603.8bn**, nonfinancial corporates **−$540.7bn**, total **+$3,243.1bn**, and
**net of the wrapper −$360.7bn** — which is a **derived** line, not an operating-company figure (**C-107**): it blends NFC
with foreign issuers (+$382.2bn) and other financial issuers. **The operating-company number is NFC alone, −$540.7bn.**
The Fed-native three-line identity is NFC + **Domestic financial sectors (+$3,401.6bn)** + RoW = total; that third line is
what contains the ETF series, and it is **not** the corroboration this section used to claim (**C-106**) — a row-sum
cannot fail. **The real corroboration is ICI Fact Book Table 13**, which matches Z.1 to under $0.1bn on 2024 and 2025,
total and bond columns alike.

**So net new operating-company equity supply over the window was negative.** *"Retired" does not mean "bought back"* — **the net retirement is predominantly M&A**, companies disappearing into
cash acquisitions. On the window this claim is about, **2024:Q1–2026:Q1** (all the Enhanced Financial Accounts covers):
**M&A retirement $858.0bn against net retirement $679.1bn — 126.3%**, so M&A more than accounts for the whole of it.
M&A retirement is a **published EFA line, not a residual** (re-checked 22 Sep: [`2026-09-13-S1-Supply-Decomposition.md`](2026-09-13-S1-Supply-Decomposition.md)
reads it from the Fed's quarterly CSV, sourced to LSEG SDC, and all five annual totals re-sum exactly).

> **What this section used to say, and why it is gone (C-108).** It supported the claim with a *decade* aggregate —
> repurchases $6.40trn against gross issuance $6.62trn, 2015–2026 — and called them near-equal. Both totals are real.
> But only **18.2%** of that issuance is identifiable public issuance (IPO $313.1bn + SEO $895.7bn = $1,208.7bn); the
> other **81.8% ($5,414.5bn) is unitemised private placement**. Against identifiable public issuance, repurchases are
> **5.3×** — the near-equality was manufactured by netting in money that never touched public float. It was also the
> wrong window for the claim. **Settled 23 Sep:** the Fed's own FEDS Note counts repurchases by *public* firms only, while its
> issuance series covers public and private firms — so the two were never like-for-like (C-108).

Either way, an NFC-wide aggregate cannot tell you what happened to S&P 500 share counts — see §6 item 1 and
[`_research/2026-09-18-EPS-Split-Spec.md`](_research/2026-09-18-EPS-Split-Spec.md). Roughly three-tenths of the
wrapper is *bond* ETFs — an equity-instrument line whose growth is partly a fixed-income product.

> **Denominator, because it bites.** P1's "≈93% of the rise is revaluation" describes the **$123.7trn stock
> of corporate equities held** at 2026:Q2 — **not listed market cap** — and that instrument contains the
> wrapper. [`2026-09-11-P1-Equity-Net-Buyers.md`](2026-09-11-P1-Equity-Net-Buyers.md) states this in its own header. Quote it with the denominator
> or not at all. **And it is an IDENTITY with nothing to check it against (C-109):** revaluation is `ΔLevel − Flow`,
> and series `893064105` appears in no Z.1 revaluation table — there is no independent Fed series at this aggregation
> that could disagree. And it is not pure revaluation: `ΔLevel − Flow` is revaluation **plus other volume
> changes** (series breaks and reclassifications), which the Fed publishes only per sector, never for the equity
> instrument (**C-119**). The sector "reconciliation gaps" this box flagged on 22 Sep ($318bn households, $322bn rest of
> world) turned out to be exactly that omitted term, not a disagreement between series — and they do not touch the
> §3 flow figures.

## 3. Who bought

- **ETF buying and mutual-fund selling offset by 81.6%** [MEASURED] — ETFs +$2,460.9bn against mutual funds
  −$2,009.0bn. **Consistent with rotation; not a measurement of it** (**C-111**). Sector netting cannot tell the same
  dollars switching wrapper from two unrelated flows that happen to offset, and Z.1 has no account-linked data, so
  this is **UNSETTLED on free data, permanently** → [`2026-09-13-S1-Supply-Decomposition.md`](2026-09-13-S1-Supply-Decomposition.md).
- **Pensions were net sellers** [MEASURED] — state/local DB −$463.9bn, federal −$67.8bn, private incl. 403(b)
  −$27.7bn, Z.1 holder side 2024:Q1–2026:Q2, all directly reported lines. **Do not pair this with the DC-contributions
  figure** (**C-112**): that is DOL/ICI administrative data, all asset classes, 2013–23, and RET1 says of its own number
  that it is *"NOT a measure of money entering or leaving the equity market"* and that both legs are contaminated by
  transfers → the RET1 return.
- **The household line is a computed residual**, not a measurement. Its **issuer** side is now attributed to
  the wrapper; its **holder** side is still unsplit by legal entity (**C-084**), and after the Private Fund
  Statistics scout there is **no free route** to split it
  → [`2026-09-14-HR-The-Household-Residual.md`](2026-09-14-HR-The-Household-Residual.md), [`_research/2026-09-15-PFS-Scout-Corporate-Equity-Line.md`](_research/2026-09-15-PFS-Scout-Corporate-Equity-Line.md).
- **Foreign flows are now instrumented.** TIC July landed 17 Sep off the new **CSLT** dataset (published
  21 May 2026, first use by us) — see [`CALENDAR.tsv`](CALENDAR.tsv) and [`data/series.tsv`](data/series.tsv).
- **Money creation is not the funding ceiling it was briefly claimed to be** (**C-089**): the deposit *stock*
  is several times the purchases, ETF creation is often in-kind, and the association is weak but positive
  → [`2026-09-14-A1-Money-Creation-Link.md`](2026-09-14-A1-Money-Creation-Link.md).

## 3a. The channels the goal names, one by one

*Added 17 Sep. The first version of this document named none of these five — it answered the equity-market
half of the goal and was checked against its own spine rather than against [`THE_ASK.md`](THE_ASK.md). Each verdict below
points at the doc that owns it.*

| goal channel | verdict over this window | owner |
|---|---|---|
| **Direct money creation** | Weak positive association with equity buying; **not** a funding ceiling — the deposit *stock* is several times the purchases (C-089) | [`2026-09-14-A1-Money-Creation-Link.md`](2026-09-14-A1-Money-Creation-Link.md) |
| **Shadow banking / shadow money creation** | **In 2024, a handoff, not fresh money** — the 2024 increase in wholesale repo came out of the Fed's reverse-repo facility (C-085). **Over the full 2024–26 window it is not ruled out** (**C-118**): N4 finds raw wholesale growth (~$1.8trn against ~$3.1trn of purchases) the same order of magnitude, and even stripped of the handoff about a quarter of purchases — a ceiling that stays in the picture. No share of equity purchases can be attributed to nonbank money — that number would be manufactured, since the purchases were wrapper purchases and the household mix is unsized | [`2026-09-15-N4-Scale-Timing-Bound.md`](2026-09-15-N4-Scale-Timing-Bound.md); [`2026-08-31-N2b-zk-The-Wholesale-Share.md`](2026-08-31-N2b-zk-The-Wholesale-Share.md) §8 |
| **The collateral channel** | Collateral **re-use intensity did not rise**; the dated step in the six-bank collateral stock is **H1 2026** — after most of the price rise | [`2026-09-15-N4-Scale-Timing-Bound.md`](2026-09-15-N4-Scale-Timing-Bound.md); [`2026-08-30-D10-Reuse-On-The-Measured-Chain.md`](2026-08-30-D10-Reuse-On-The-Measured-Chain.md) |
| **Passive bid / ETF creation** | **The dominant finding** — the wrapper *is* the issuance (§2); the bid is mostly rotation (§3) | [`2026-09-15-ETF1-Identity-Net-Of-ETF.md`](2026-09-15-ETF1-Identity-Net-Of-ETF.md) |
| **AI build-out funding** | **Mostly self-funded**: five of six hyperscalers generate more operating cash than their capex; **only Oracle cannot** (~$35bn shortfall). The financing that matters is **off balance sheet** — lease commitments signed but not yet commenced sum to **$1,122.9bn, about 4.9× the $228.3bn of guarantees contracted** — future against future; the "13×" this row carried until 23 Sep divided future leases by *live* guarantees only (**C-116**). **The AI debt that does exist is held mainly by long money** (W2): money funds hold ~$4bn, mostly as repo collateral that finances dealers rather than the companies, ~0.35% of JPMorgan analysts' ~$1.2trn *estimate* of AI-company-issued debt; large-bank C&I exposure to AI-adjacent industries is ~$450bn committed / ~$150bn outstanding, but that classification already stood at ~$250bn of commitments in 2015, so build-out lending is some smaller, unmeasured part of it (**C-115**) | [`2026-09-12-F1-Funding-Table.md`](2026-09-12-F1-Funding-Table.md); [`2026-08-22-Guarantee-Stack.md`](2026-08-22-Guarantee-Stack.md); [`2026-09-12-Oracle-RPO-And-Financing.md`](2026-09-12-Oracle-RPO-And-Financing.md); [`2026-09-22-W2-AI-Paper-Composition.md`](2026-09-22-W2-AI-Paper-Composition.md) |
| **IPO boom** | About **$112bn of new money** in 2026 to date, **two-thirds of it one deal** (SpaceX, $75bn); $36.9bn excluding it. **Who bought is not recoverable on free data** — cornerstones are named in 3 of 10 deals | [`2026-09-12-I1b-IPO-Prospectus-Facts.md`](2026-09-12-I1b-IPO-Prospectus-Facts.md); [`2026-09-14-I2-IPO-Allocation.md`](2026-09-14-I2-IPO-Allocation.md) |

**Read together, this is a real result about the original hypothesis, not a gap in it.** E-003 named these
channels as things to test — "potential" factors, in the principal's word. Over 2024–26 the money that bought
equities was mostly **already inside the system** (the deposit stock, and rotation between fund types) rather
than newly created through shadow or collateral channels, and the largest capex programme in the market was
funded mainly from **profits and leases** rather than from either. That does not make those channels
unimportant in general; it says they are **not what carried this repricing**.

**What this does not establish:** that shadow money or collateral played *no* role — N4 bounds rather than
zeroes them — and it says nothing about whether the off-balance-sheet lease stack is itself the next source of
fragility. That is a different question from the one the goal asks, and it is on the calendar (Oracle's
guarantee maturity and hyperscaler free cash flow, 30 Sep).

## 4. The bridge — closed, and each leg closed for a different, stated reason

The object was a credible **aggregate causal money→price** estimate. It is not recoverable here, and the
taxonomy matters more than the verdict — [`2026-09-16-TierB-E005-Resolution-Limit.md`](2026-09-16-TierB-E005-Resolution-Limit.md) (read its C-092 banner).

| leg | why it closed | number |
|---|---|---|
| **B5** sovereign mandate IV | data — bands never bound; monthly triggers unobservable | first stage weak, n=9 |
| **P4** Russell RD | data — free substitutes never assigned treatment (**C-086**) | first stage *F*≈2.6 |
| **B6** payment-day IV | **arithmetic, conditional on a borrowed multiplier** — ~2.5bp signal inside ~111bp of daily noise at Hartzmark–Solomon's M≈1.9 (**C-090/C-091/C-117**) | **~386 years** at M≈1.9; **16 years** at the envelope top (M=9.4), against 11.7 of free data |
| **JVZ** mega-firm test | resolution — 26 free N-PORT quarters (**C-092**) | MDE 1.097 vs 0.528 predicted, **0.48×** |

**B6 is the leg furthest from reopening, not a permanent closure** (**C-117**): at the central multiplier it needs ~386 years, but at the top of the published envelope it needs 16 against the 11.7 free data provides — so its re-open trigger is also a number, **about 2030**, if M sits at the envelope top. JVZ's re-open trigger is a number,
not a word: parity needs **~113 quarters, about 2048**. Coverage is not the constraint; it is already 40/40
megas. **We never borrowed a multiplier from the literature and applied it** — that approach died at C-077,
and C-080 killed the bound built on the wrong denominator.

## 5. What we cannot say

Any scalar **M**; any statement that flows *caused* a specific share of the repricing; any split of the
residual by wealth group or buyer type; that the passive bid is refuted (no design ever assigned it); that
the equity base *grew* without naming the wrapper; that money creation was too small to have funded the
buying. Each is a live ban pattern — `bin/check.sh --all` enforces them.

## 6. What would change this answer

1. **Buybacks inside the earnings number — TESTED 18 Sep, and the lead claim survives.** Grok split S&P 500 EPS
   growth using constituent-level diluted share counts from SEC ([`2026-09-18-EPS-Split.md`](2026-09-18-EPS-Split.md); method re-derived
   exactly on AAPL). **Per-share accretion is AT MOST ~7–13% of the price gain since 2015** (one-sided, C-101); **profit plus index
   composition ~69–75%** — which is the arithmetic complement of that band, `100 − 17.7 − accretion`, **not a second
   finding** (verified: 75.24 and 68.91 reproduce it exactly); **the multiple ~18%** (C-093 — carry the band, not the doc's 13.4% point, which is the top of
   its own weighting range and is pushed up further by survivorship). So **part of the price side's "earnings"
   *is* the money side's buybacks — roughly a tenth to a sixth of it — but most of it is real profit.**
   What remains untested is narrower than SYN1's list implied (**C-095**): the headline rests on **as-reported
   (GAAP)** earnings, in which stock-based compensation is already expensed, so it cannot inflate the series —
   and operating-vs-GAAP and R&D capitalisation are moot for the same reason. **The tax act is now measured** (W3, 21 Sep): across 412 S&P 500 firms the aggregate
   effective rate Σtax/Σpretax fell **27.4% → 19.6%** [MEASURED, 412 firms, 94.1% of 2015 mcap], worth
   **about a tenth** of Δlog EPS [MEASURED but basis-sensitive: **8.9%** on the panel's own basis, 9.5% against the carried
   index EPS — **C-098**]. Restating 2025 EPS at the 2015
   rate moves the earnings share of the price gain from **82.3% to 74.5%** — the unadjusted figure sits *above* the
   70–80% band and the restated one inside it, so the top of that band is tax-assisted →
   [`2026-09-21-W3-Tax-Decomposition.md`](2026-09-21-W3-Tax-Decomposition.md). Every scalar was re-derived and matches; the firm-level panel did not
   land, so the derivation is not auditable here (**C-097**). **And under E-007 the decomposition's third term is
   withdrawn (C-098):** "pre-tax profit is 74.2% of EPS growth" was never measured — it was solved for as the residual,
   which is why its "sum check" was exact. Measured directly from the same panel the term is **0.8603, not 0.7875** — a
   **0.073 log (7.6%)** gap, most plausibly survivorship in a panel of *current* constituents, but **that is a hypothesis
   and is untested**. What is still live: **revenue-recognition timing**
   (ASC 606, 2018).
2. **A free holder-side split of the household line**, which would convert the residual from a plug into a
   measurement. No route today.
3. **The premium reversing further.** It already gave back ~17bp in H1-2026; a sustained reversal changes the
   "what held the multiple up" story without touching the earnings result.
4. **N-PORT accumulating**, which reopens JVZ — but not before the 2040s.

## 7. Confidence

**Read this section under E-007: these are credences, not proofs, and none of them is a grade.** "Survived adversarial
attack" describes what we threw at a claim, not what is true — and C-098 was found in a parcel this section's own
standard had already passed, one day after the supervisor reported it verified.

**High** on the earnings share and on the wrapper reclassification — both survived adversarial attack from
outside and were re-derived from source. **But re-deriving a residual only re-runs the subtraction** (C-098): the
earnings share is MEASURED in its EPS and price terms and IDENTITY in its decomposition, and the split of the
earnings term between pre-tax business, tax and accretion is basis-sensitive by ~7%. **Medium** on the premium compression, and lower than it reads: three constructions agree on direction,
none on decomposition — and they agree **structurally**, because a bond leg outran the equity leg in each (C-102). **Low and explicitly bounded** on causation: we have no aggregate estimate
and have said why four times over.

**The honest summary is that the money side turned out to be a measurement question more than an economics
one.** The single most consequential thing we learned is that a headline series everybody reads as corporate
equity issuance is, over this window, mostly ETF plumbing — and it was sitting in our own files for two days
before an outside review caught it.
