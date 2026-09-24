# Retrieval parcel — for Gemini Flash 3.7 (high)

*Written 22 August 2026. **This is not a review parcel.** `Review_Prompt_For_Gemini.md` was an
adversarial review and it has been run; this one is a **retrieval commission**, sent to Gemini
for search capacity rather than judgement. Do not merge the two.*

**Why it is shaped this way.**

1. **It serves A12, not A11.** First external parcel written under the corrected goal
   (`THE_ASK.md` E-002, C-041). Every task below serves the nonbank–bank nexus. Nothing in it
   asks whether the essay is publishable.
2. **The lead question is "has this already been built?"** Group A alone could save months. We
   have been reconstructing series by hand that a standing body may already publish — and we
   only discovered Pozsar had *specified* the accounts we were improvising by finally reading
   him on 22 August.
3. **The main hazard of a strong search model is the citation cascade**, which is this project's
   most-repeated failure mode — four logged instances of treating N sources that all cite one
   paper as N confirmations. A model optimised for search will surface eight sources for a
   number that has one origin. The prompt therefore demands **provenance chains, not source
   counts**, and makes that the first instruction rather than a footnote.
4. **Dead claims are excluded.** Checked against `CORRECTIONS.md` (42 entries) before sending:
   no "highest of 304 quarters" (C-036), no "Japan 47%" as nationality (C-039), no "velocity is
   X" (C-015/C-040 — "Singh estimates"), no funding-puzzle framing (C-030), no GLL-as-law
   (C-037). Where a dead claim appears below it is **marked dead and posed as a question**.

---

```
You are running a RETRIEVAL commission, not a review. I do not want your opinion of my argument.
I want sources, series, and numbers located — or a clear statement that they do not exist.

Today is 22 August 2026. Use search aggressively. Go to issuing institutions and primary
documents. I would rather have "this does not exist publicly, here is what I checked" than a
plausible answer.

## THE ONE INSTRUCTION THAT MATTERS MOST

**Give me provenance chains, not source counts.**

My project has four logged instances of treating several sources as independent confirmation
when all of them cited one underlying paper. You are a strong search model and this is exactly
the error you are most likely to hand me at scale.

So for every number you return:
- name the **issuing body and the specific table, series ID, or page** it comes from;
- if you found it in a secondary source, **follow it back** and tell me the origin;
- if six sources report it and all six trace to one paper, tell me it is **ONE source**;
- if you cannot reach the origin, say **"origin not reached"** and give me the nearest link.

"Cannot verify" and "does not exist publicly" are complete, valuable answers. A confident wrong
number is worse to me than an admitted gap.

## WHAT THE PROJECT IS

A study of the **nonbank–bank nexus** in the sense of Pozsar & Singh, *The Nonbank-Bank Nexus
and the Shadow Banking System* (IMF WP/11/289, December 2011): the mechanisms by which
**collateral and money creation operate outside the banking perimeter**, on the premise that
collateral does work analogous to base money in facilitating credit and liquidity creation.

The frame has two legs, and the point is that the same entities sit on both — asset managers
are simultaneously the dominant source of demand for **non-M2 money** and the source collateral
**"mines"** from which dealers and banks fund themselves through re-use of pledged collateral.

**Where we actually are.** We have done the collateral leg and found it largely negative: reuse
intensity is not the growth story. We have **not** done the money leg at all. We are now trying
to build the 2026 equivalent of Pozsar's shadow-money measurement — and before we spend months
on it, I need to know whether somebody already has.

## GROUP A — HAS THIS ALREADY BEEN BUILT? (HIGHEST PRIORITY — DO THIS FIRST)

If you only complete one group, complete this one. Each question is: does the series exist, who
maintains it, what is the latest value and date, and is it downloadable?

**A1. Pozsar's shadow-money aggregate, extended past 2013.** In *Shadow Banking: The Money View*
(OFR WP 2014-04) Pozsar constructs monetary aggregates for money and money-like claims issued by
the shadow banking system, putting the core at just under **$5trn at 2013Q3**, down from a peak
over **$8trn at 2008Q2**. **Has anyone carried that series forward?** Pozsar himself, the OFR,
a central bank, an academic, a sell-side desk. If it exists I want the 2025 or 2026 value and
the source. If it stops in 2014, say so — that is a finding.

**A2. The three satellite accounts.** In the same paper Pozsar calls for **Flow of Collateral,
Flow of Risk and Flow of Eurodollar** satellite accounts to supplement the US Financial
Accounts. Has any statistical agency, central bank or researcher actually built any of the
three? The Flow of Risk one especially — I have found nothing resembling it anywhere.

**A3. Institutional cash pools.** Pozsar puts them at **at least $6trn under management at
end-2013**, in four categories: the liquidity tranche of FX reserves; global corporate cash;
centrally managed balances of institutional investors and large asset managers; and securities
lenders' cash-collateral reinvestment accounts. **Has anyone updated this?** Is there a current
estimate of aggregate institutional cash pool size, on any definition? Who publishes it?

**A4. How does the FSB's "narrow measure" relate to Pozsar's aggregate?** The FSB Global
Monitoring Report on Non-Bank Financial Intermediation publishes a narrow measure of NBFI. Is it
measuring the same object as Pozsar's shadow-money aggregate, a different one, or an overlapping
one? Specifically: does the FSB narrow measure **net** for holdings between intermediaries, and
does it require money-market funding for inclusion? This matters enormously to me and I want it
answered on the basis of the FSB's stated methodology, not by inference.

**A5. Singh's collateral-reuse series.** Singh has hand-collected pledged-collateral and reuse
figures from roughly 20 dealer banks for about 17 years. **What is his most recent published
figure, and where?** Give me the publication, date, the pledged-collateral stock and the reuse
rate he states. I need this cited as *"Singh estimates"* with a date — I am not looking for an
independently verifiable ratio and do not present one as though it were.

## GROUP B — PRIMARY SOURCES I CANNOT REACH

These are freely published working papers. My fetcher gets HTTP 403 from imf.org, ssrn.com and
rba.gov.au. I am not asking you to defeat a paywall — I am asking where else these public
documents are hosted, or for their substance if you can read them.

**B1.** Pozsar & Singh, *The Nonbank-Bank Nexus and the Shadow Banking System*, **IMF WP/11/289,
Dec 2011**. This is the paper that names my research object and I have still not read it. If you
can read it: what exactly is the nexus, what does "collateral mining" mean mechanically, and how
do the money leg and collateral leg connect into one mechanism rather than two? Their headline
figures as I understand them second-hand — collateral mined from asset managers **$3.3trn
(YE2007)** and **$2.4trn (YE2010)**; shadow banking up to **$25trn (YE2007)** and **$18trn
(YE2010)** — are from abstracts, NOT from the paper. Confirm or correct them against the text.

**B2.** Pozsar, *Institutional Cash Pools and the Triffin Dilemma*, IMF WP/11/190. Same request.

**B3.** Singh, *The Economics of Shadow Banking*, RBA 2013 Conference Volume.

## GROUP C — WHERE THE 2026 MONEY-LEG NUMBERS LIVE

I want to rebuild Pozsar's classification on current data. For each, name the **series ID and
issuing table**, or tell me it is not publicly separable. His end-2013 categories, par on demand:
private shadow money $3.2trn (uninsured demand deposits, overnight private repo from dealers'
credit desks, constant-NAV prime MMF shares); public money ~$2.6trn; public shadow money $2.3trn
(overnight government repo, constant-NAV government-only MMF shares); insured money claims
$1.4trn.

**C1.** Uninsured US bank deposits, current. FDIC or Call Report series, quarterly, latest value.

**C2.** Constant-NAV MMF shares split **prime vs government-only**, current. Is the constant-NAV
distinction still meaningful post-2016 reform, and does it survive the 2023–24 rule changes? If
the category has been legislated out of existence, that is the answer and I need to know.

**C3.** Overnight repo issued by dealers, split between **credit desks and government desks** —
i.e. private-collateral versus government-collateral repo. Is that split published anywhere, by
anyone? OFR repo collection, tri-party data, FR 2004, DTCC. If it is not separable in public
data, say so plainly.

**C4.** Is there any current published estimate of **total money-like claims outside M2**, on
any methodology? I am looking for whoever is closest to Pozsar's object today.

## GROUP D — SPECIFIC CONTESTED NUMBERS

**D1. Replacement-cost Tobin's q.** I have a Z.1-based equity q and a claim that a
replacement-cost q behaves differently, with counter-figures of roughly **1.94 versus 2.15**
around 2000Q1 attributed to a replacement-cost series. I cannot verify those. **Which named,
published q series exist, what do they report at 2000Q1 and at the latest available date, and
do they use the same denominator?** A key part of my problem is that the Z.1 denominator does
not capitalise intangibles, which biases measured q upward over time. Tell me which published
series address that and how.

**D2. BIS locational banking statistics — a structural question, not a number.** In the LBS,
can the **nationality/parent** dimension be crossed with the **currency** dimension in the
published cube? I previously attributed a share of an offshore USD funding residual to Japanese
banks on a *nationality* basis; I have since restated it as **residence of the reporting office**
because I do not believe the two dimensions intersect publicly. **Confirm or refute that the
intersection is unavailable**, and if it is available, say exactly which table serves it.

**D3. An instrument for repo attribution.** I want to know what share of repo growth is
Treasury basis-trade leverage rather than money demand. I previously compared Form PF hedge-fund
repo borrowing with the Fed Financial Stability Report repo line — that comparison is **dead**,
because those are opposite sides of the same trade and not a like-for-like basis. **What
measurement could actually attribute repo growth to the basis trade?** Existing published series
preferred; a stated methodology is acceptable; "no public instrument exists" is a real answer.

**D4. Bank lending to NBFIs, decomposed.** US bank loans to non-depository financial
institutions are large and published as one line. Call Report schedule RC-C memoranda are said
to break this into roughly five borrower-type buckets from 2025Q2 onward. **Confirm the exact
memorandum item numbers, when they began, and whether the data is publicly downloadable.**

## GROUP E — WHAT IS MOVING THAT I DO NOT HAVE

**E1. Successor literature.** Who has extended, tested or seriously challenged the Pozsar–Singh
collateral framework since roughly 2015? I want the strongest **critique** as much as the
strongest extension. Name the papers and what each actually establishes.

**E2. The missing channel.** I have covered: bank credit, offshore dollars, repo and collateral
reuse, money-like liabilities, private credit, securitisation, insurance and annuities, FX
swaps, stablecoins, margin and prime brokerage, contingent guarantees, and off-balance-sheet
lease commitments. **What mechanism is materially moving in 2025–26 that is not on that list?**
If your answer is a channel I have listed, do not give it to me — give me the one I have missed.

**E3. Tokenised collateral.** Singh's argument is that intraday tokenised repo settles within
the day, so it never appears in end-of-day disclosures and measured collateral velocity falls
while true velocity rises. **Is anyone measuring intraday or tokenised collateral volumes?** Any
platform disclosure, central-bank study, or BIS work that puts a number on it.

## HOW TO ANSWER

Work in the group order given: **A first**, then B, C, D, E. If you run short, stop and tell me
where you stopped — a complete Group A is worth more to me than thin coverage of all five.

Per item, keep it this tight:

- **Verdict:** EXISTS / DOES NOT EXIST / PARTIAL / CANNOT DETERMINE
- **Source:** issuing body, document or table, series ID, date. A link.
- **Value:** the number, with its as-of date and units, where the item asks for one.
- **Provenance:** where it originates if you found it second-hand. Say "origin not reached" if so.
- **Caveat:** definitional mismatches, breaks, restatements, discontinued series.

Do not summarise my project back to me. Do not tell me the work is thorough. Do not offer
recommendations about what I should conclude — that is my job, and the value you add here is
finding what exists.
```
