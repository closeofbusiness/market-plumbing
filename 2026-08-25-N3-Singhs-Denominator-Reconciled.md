# N3 — Singh's denominator: the collateral leg, reconciled and carried to 2026

*25 August 2026, **v2 — amended 28 Aug after adversarial review (§6)**. The v1 point estimate "velocity ≈1.5"
is retracted to a range; the mechanism conclusion survives. Original v1 text below is kept with strikes where the
review overturned it.*

*Original v1 header:* The reconciliation the N3 parcel identified as the method question
(`2026-08-23-Parcel-N3-Collateral-Return.md` §2.3), now performed. Every figure either read from the primary
source we hold or computed from a series in `data/history/`. Serves **A12** — this is the collateral half of
the nexus, and the half the project has been weakest on. Result promoted to RESEARCH_STATE §2 as **S-N3**.*

---

## 0. What Singh's measure actually is

From WP/19/106 (Singh & Goel, 17 May 2019), read from the PDF we hold, and WP/17/113 Annex II:

> *"the ratio of the total pledged collateral received by the large banks, divided by the primary sources of
> collateral, is the velocity of collateral"*

- **Numerator** — collateral received by the 10–15 core dealer banks *"that could be onward re-pledged in
  their own name"*. This comes straight from the statutory footnote (US GAAP ASC 860-30-50 / IFRS 7.15) that
  we already reconstruct firm by firm. **$7.5trn at end-2017**, per the paper.
- **Denominator** — *"two primary sources that pledge collateral to the banking system: hedge funds and other
  financial intermediaries"*. Footnote 13 pins both legs at end-2017: **hedge funds $2.2trn** (against hedge
  fund AUM of $3.0trn) and **$1.5trn of securities on loan** by *"pension, insurers, official sector and asset
  managers"*, explicitly *"without secondary market churning"* — **total $3.7trn**, velocity **2.0**.

**A naming trap in our own corpus, fixed today (C-060).** `Shadow_Debt_Channel_Map.md` calls the *footnote*
figure "dealer source collateral". In Singh's usage "sources" is the **denominator** — what nonbanks pledge in
— while the footnote is the **numerator**. Same words, opposite ends of the ratio. The channel map's own
source table gets this right (*"the numerator of Singh's velocity measure"*), but the findings prose does not,
and the collision is exactly how a velocity gets computed upside down. Terminology corrected there.

## 1. The hedge-fund leg — a bracket that holds for five years, then breaks

Singh's hedge-fund source cannot be pulled from a database; it is his estimate. But **Form PF Q43 collateral
posted** by qualifying hedge funds (OFR Hedge Fund Monitor, in `data/history/hf_collateral_posted_*.csv`)
brackets it from both sides: *securities* posted is a lower bound (excludes cash-like margin), *all collateral
posted* is an upper bound (includes cash, CCP margin, and QHFs only). **In all five overlapping years Singh's
figure lies strictly inside that bracket:**

| Dec | Form PF securities | **Singh HF source** | Form PF all collateral | position in bracket |
|---|---:|---:|---:|---:|
| 2013 | 1.37 | **1.85** | 2.03 | 0.73 |
| 2014 | 1.52 | **1.90** | 2.24 | 0.53 |
| 2015 | 1.49 | **2.00** | 2.26 | 0.67 |
| 2016 | 1.46 | **2.10** | 2.38 | 0.70 |
| 2017 | 1.82 | **2.20** | 2.83 | 0.38 |

*$trn. Mean position 0.60, range 0.38–0.73.* Carried forward on that mean:

| 2026Q1 | Form PF securities | **implied Singh-equivalent** | Form PF all collateral |
|---|---:|---:|---:|
| hedge-fund source | 4.92 | **≈ 6.9** *(range 6.1–7.3)* | 8.21 |

**The hedge-fund leg has roughly tripled since end-2017** — $2.2trn → ~$6.9trn — which is the same fact D3 §8
found from the other side (collateral posted $4.4trn at YE2021 → $8.2trn at 2026Q1, tracking secured borrowing
one-for-one as the basis trade scaled).

## 2. The real-money leg — bounded, not yet measured

Singh's second leg is *securities on loan by pension funds, insurers, official accounts and asset managers,
excluding churn*: **$1.5trn at end-2017**. The live free analogue is ISLA's market-data page (read at source
25 Aug; data as of **31 March 2026**): **global on-loan €3.9tn**, lendable €40.6tn, equities on-loan €1.8tn.

That is an **upper bound, not the leg**: ISLA's figure is all lender types (hedge funds and banks included),
all borrowers (not only the core dealers), and includes the churn Singh excludes. The page does publish
*"Securities On-Loan by Client Type (%)"* sourced to DataLend — which is precisely the split needed — but it
renders as a JavaScript chart and is not in the HTML. **Reading that chart in a browser is the single cheapest
remaining step in N3, and it closes the denominator.** Until then the leg is *somewhere between $1.5trn
(Singh's 2017 level) and roughly the euro-converted ISLA total*, and no conversion is asserted here.

## 3. Where that leaves velocity — and the tension worth stating plainly

| | end-2007 | end-2017 | **2026** |
|---|---:|---:|---:|
| Numerator: pledged collateral received | 10.0 | 7.5 | ~13 *(Singh, Jan 2026, round)*; **US-six alone 6.9 (FY2025, ours)** |
| Denominator: sources | 3.4 | 3.7 | **≥6.9 from hedge funds alone**, plus a real-money leg ≥1.5 |
| Velocity | 3.0 | 2.0 | ~~**~1.5 on those inputs**~~ **[C-061: retracted to a RANGE — ≈1.5 at the fitted bracket position, ≈2.0 at the securities-only floor and per Singh's own Jan-2026 statement; see §6]** |

**The tension.** Singh's own January 2026 published pair — *"roughly $13 trillion"* pledged, velocity
*"around 2.0"* — implies **total sources of about $6.5trn**. Our hedge-fund leg alone is ~$6.9trn. The two
cannot both be right. Either the round figures in a paywalled column are approximations carried forward, or
**the composition has shifted so far toward hedge funds that the 2017 partition (59% hedge funds / 41% real
money) no longer describes the market.** Both readings point the same way: **sources have grown faster than
the pledged pool, so collateral velocity has kept falling — to roughly 1.5, from 2.0 in 2017 and 3.0 in
2007.** That is the opposite of the "collateral is being re-used ever harder" intuition, and it is consistent
with what our own FR 2004C reconstruction already said (`Shadow_Debt_Channel_Map.md`: reuse intensity flat to
falling; the growth is in the *stock* of collateral and the *reach* of the pipes).

**For the nexus.** The collateral leg is not accelerating; it is being *fed*. Hedge funds now pledge roughly
three times what they pledged in 2017, and that is where the growth in the pledged pool comes from — not from
each security being turned more times. Pozsar–Singh's claim that collateral is as critical as base money
survives; the mechanism in 2026 is **more source collateral, not faster re-use**.

## 4. What v1 does not settle

| | Status |
|---|---|
| Real-money leg | **Bounded, not measured** — needs the ISLA client-type chart read in a browser (§2). Cheapest next step in the whole build |
| Numerator on a like-for-like perimeter | Ours is **US-six** ($6.9trn FY2025); Singh's is 10–15 global banks. Jefferies and Nomura are already in the channel map; the European names are not. Building the global perimeter would make the ratio directly comparable |
| Singh's own 2026 inputs | His $13trn / 2.0 pair is from a **paywalled column**; we have the headline only, and no budget. Treated as an approximate external cross-check, never as our denominator |
| Churn | Singh excludes secondary-market churning from the real-money leg; Form PF Q43 does not exclude anything analogous on the hedge-fund side. This asymmetry is unquantified |

---

## 6. Adversarial review (Parcel N3R, Grok) — outcome, 28 Aug

*Return at `_research/N3R_Velocity_Review_Return.md` (retrieved from the PR branch it landed on — see §6.3).
Verified by three agents: every load-bearing citation checked at the source. Register: **C-061**.*

### 6.1 The review's scorecard — the strongest external return this project has received

**Verdict delivered: VULNERABLE. Accepted in part.** Citation audit: the Risk.net article — the load-bearing
counter — is real, **free to read** (we had recorded its Central Banking twin as paywalled and stopped), and
says verbatim: *"the collateral velocity has remained near 2.0 for the past decade"*; *"roughly $13 trillion
global market"*; JPM and Barclays *"each offering around $1.8 trillion"*; US banks over half. All six
secondary citations verified exactly (ISDA YE2025 $423.5bn CCP IM; CCP Global Q4-25 $1.52trn; OFR 24-07 65%
rehypothecation; OFR 26-03 hedge funds >$1.8trn net repo borrow; ECB WP 3147 reuse 11.6% / chain length 2.95;
BoE gilt re-use 3.5% — a stock ratio, different construction). All five dealer footnote values match ours;
the review's "uncertain sixth" is Wells Fargo $469.2bn, closing the sum at our $6.907trn exactly. One URL
error (BAC value cited from the Q1-26 10-Q rather than the FY25 10-K; value identical). PDFs archived at
`_research/primary_sources/collateral_reuse/`; the Singh article text at
`_research/primary_sources/Singh_2026-01-12_Risknet…txt`.

### 6.2 What falls, what survives

**Falls — the point estimate.** "Velocity ≈1.5" rested on carrying the 0.60 bracket position (fitted 2013–17)
into 2026. The review's Attack 2 is right that the position is a free parameter with no structural anchor, and
the metric's author — with seventeen years of hand-collected top-20-bank data cross-checked with investor
relations and hedge funds, none of which we can see — states *"measured velocity has remained almost constant
at around 2.0"* in the same January 2026 piece. At the securities-only floor our own inputs give
13/(4.92+1.5) ≈ 2.0. **Corrected claim: velocity is in [≈1.5, ≈2.0], with Singh's 2.0 as the primary point
and our 1.55 as the fitted-bracket alternative; the bracket position is unidentified in 2026.**

**Survives — the mechanism, under every reading including the review's own alternative.** No reading has
velocity *rising*. And sources grew massively in all of them: Singh's own pair implies total sources
~$6.5trn vs $3.7trn at end-2017 (+76%); our securities-only floor has the hedge-fund leg ×2.7. The review's
alternative reading says it outright: *"both primary sources and the pledged pool grew roughly in
proportion."* **The load-bearing conclusion stands: the collateral leg grows by more source collateral, not
faster re-use.** What changed is that the growth split between the two is now stated as a range, not a point.

**Also noted:** the review's Attacks 2 and 4 pull in opposite directions (position →0 recovers Singh;
position →1.0 per the basis-trade argument pushes velocity below 1.5). Jointly they establish
*unidentified*, not *2.0*. And position 0 specifically is hard to credit: Singh's 2013–17 values never sat on
the securities-only bound, and the cash-like bucket that bound excludes contains the basis-trade Treasuries.

**New primary-source detail the review surfaced:** Singh's 2026 method statement — denominator = collateral
sourced via *"reverse repos, securities lending, prime brokerage and uncleared derivatives"*, perimeter
*"top 20 banks"*. So his source concept is wider than securities-posted and narrower than all-Q43 (cleared/CCP
margin out; uncleared-derivatives margin in), and our US-six numerator is roughly half his bank perimeter.
**The settling test stands as Attack 3 framed it:** a Form PF collateral split by counterparty type
(prime-broker vs repo vs cleared) — which OFR does not publish; type aggregates only. Until something like it
exists, the range is the honest answer.

### 6.3 Process notes

The parcel was routed to the chat window but run in **Grok-in-Cursor against `hermes-core`**; the return
landed as draft PR closeofbusiness/hermes-core#557 and existed nowhere on this project's disk until retrieved
from the PR branch. Recommendation to the principal: close #557 unmerged; the content lives here now.
And the free-twin lesson (C-061): Risk.net and Central Banking are the same publisher and cross-post —
**a paywall is a property of the URL, not the article**; check the sibling site before recording a piece as
gated. We had the Central Banking headline in hand since 23 Aug and never looked sideways.

---

## 7. N3b — the real-money leg, measured at the top (29 Aug, browser read of the ISLA charts)

*The client-type split the v1 doc flagged as "the cheapest remaining step" is now read: the ISLA page's
Chart.js instances carry the data (source DataLend; as of 31 Mar 2026; archived
`data/vintages/isla/isla_market_data_2026-03-31_read_2026-08-29.json`).*

**Securities on-loan by client type:** Pension plans **21%**, Government/SWFs **17%**, Insurance **3%**,
Collective investment vehicles **20%**, Banks/broker-dealers **16%**, Undisclosed/Other **23%**.

**The Singh real-money set — pensions + official + insurers + asset managers — is 61% of global on-loan**
(84% ceiling if all of Undisclosed/Other belongs to it; banks/broker-dealers are intermediaries, not
sources). On the €3.9trn on-loan total: **€2.38trn ≈ USD 2.74trn** at the ECB 31-Mar rate (1.1498),
range 2.4–3.3 EURtrn. Against Singh's end-2017 leg of $1.5trn: **roughly ×1.8**, in line with the
hedge-fund leg's growth direction, though slower.

**Still an upper bound, and the residual uncertainty is now precisely named:** ISLA counts all borrowers
(not only the top-20 dealer perimeter) and includes the churn Singh excludes. So the leg is
**≤ ~$2.7trn and ≥ some dealer-share fraction of it**; at a two-thirds dealer share it reproduces
Singh's ~$1.5–2.0trn scale.

**Effect on the velocity range (C-061 unchanged in structure, tightened in content):**
13 / (4.92 + 2.7) ≈ **1.7** at the securities-only hedge-fund floor with the full ISLA-based real-money leg;
13 / (6.89 + 1.6) ≈ **1.5** at the fitted bracket with a dealer-share haircut. The band **[≈1.4, ≈2.0]**
persists, but note the asymmetry: **taking the new measured real-money leg at face value pushes even the
most conservative reading below Singh's 2.0.** The unidentified quantities are now exactly two — the Form PF
bracket position, and the dealer-share/churn haircut on agency lending. Singh's 2.0 remains primary per
C-061 (his data, unlike ours, observes the dealer perimeter directly), but the weight of open-data readings
sits below it.

**Two by-products worth their own lines:**
- **The D5 pool is sized:** cash collateral received against securities loans = **€1.24trn (33%)** of
  €3.75trn total collateral received (weekly series, 26 Mar 2026) — the first free number this project has
  for the securities-lending cash-reinvestment pool (D5, cash-pool category 4). Non-cash 67% — the re-use
  channel SLATE will eventually illuminate.
- **On-loan by asset class:** equities 45%, government bonds 39%, corporate debt 9% — the sources are
  roughly half equity, unlike the Treasuries-dominated hedge-fund leg.

---

## 8. Re-derivation under challenge (29 Aug) — the bracket position is signable, and the range was lazy

*The principal challenged §6's "the position is unidentified in 2026, so the range is the honest answer" as
unscientific: the regime changes between the fitting window and today — end of ZIRP, Covid, the basis trade,
the growth of the shadow system — are known mechanisms, and known mechanisms can SIGN a drift even when they
cannot pin a level. He is right. §6 stopped at an interval where a first-principles decomposition was
available. Here it is, from series we already hold.*

**What is actually inside the disputed bucket.** The bracket's whole uncertainty is how much of Form PF's
"cash-like" collateral bucket belongs in Singh's source concept. Per the OFR definition, that bucket contains
**US Treasuries and agencies** as well as cash — and hedge-fund **repo borrowing ($3.24trn at 2026Q1) alone
exceeds the entire bucket ($2.92trn)**. Repo collateral is overwhelmingly UST, and repo'd UST is the most
Singh-includable collateral there is: title-transferred, dealer-reusable, the defining flow of the era. The
bucket cannot be mostly true cash. The repo-to-bucket ratio has risen from ~0.8 (2013–21) to **1.11** (2026Q1)
— the bucket got *more* Treasury-heavy, not less.

**Sizing the only downward wedges, generously, from sources on our disk:** margin trapped at CCPs rather
than reusable by dealers — FICC GSD initial margin **$78bn** (its own 2026Q1 PQD file); a **$300bn ceiling**
on the hedge-fund share of global CCP margin (ISDA YE2025: $423.5bn required IM at major CCPs from *all*
participants); a **$500bn** allowance for genuine cash margin at prime brokers. Total **$0.88trn** against a
$3.29trn bucket *[11 Sep clarification: this "bucket" is the whole bracket width — all collateral 8.21 minus securities 4.92 = cash-like 2.92 + other 0.37 — not the $2.92trn cash-like bucket above; the arithmetic is unchanged]* → **mechanism floor on the bracket position: 0.73 — above the 0.60 fitted on 2013–17.**

**Therefore:** hedge-fund source ≥ **$7.3trn**; with the measured real-money leg (§7, $1.6trn dealer-share
haircut to $2.7trn full), our proxy chain gives **velocity ≈ 1.30–1.46**. Grok's Attack 2 ("position 0
recovers Singh's 2.0") is hereby **rejected with numbers, not an aside**: position 0 requires excluding the
basis-trade Treasuries themselves. And the numerator perimeter mismatch cuts the same way — $13trn is global
top-20 while our denominator omits every non-US hedge fund, so if anything the true ratio is lower still.

**The corrected verdict (C-061 addendum):** the band is **asymmetric and mechanism-weighted:
velocity ≈ 1.3–1.5 on the signed proxy chain.** Singh's 2.0 is no longer "primary"; it is a
**direct measurement in open conflict with the signed proxies**, and the conflict now has a size and a name:
for 2.0 to hold, his source concept must net out roughly **$2.5–3trn** of what Form PF grosses up — netted
repo packages, sponsored/cleared legs he may exclude, churn — or his round figures are carried forward.
That is a specific, falsifiable question, and its cheapest resolution is not a database: **he answers
questions — the principal could ask him directly (he posts publicly, "no paywall", on LinkedIn) how his
source figures treat gross Form PF-style posting.**

**What the challenge does not reopen:** the mechanism conclusion (sources grew ×3; re-use did not
intensify) was common to every reading and stands. **What the episode teaches (both directions):** v1's sin
was an unsigned fitted point; v2's sin was retreating to a symmetric range anchored on authority.
**An interval is only honest after the mechanisms have been signed and sized — "unidentified" is a statement
about effort, not about the world.**

