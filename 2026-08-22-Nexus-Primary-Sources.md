# The nexus, from the primary sources — N1 opening pass

*22 August 2026. Written immediately after the goal correction (C-041) established the
nonbank–bank nexus as the ultimate goal (`RESEARCH_STATE.md` §0.0). This is the **first** pass
in this project to read the frame's primary sources rather than cite them.*

**Status: partial.** Two of four sources retrieved and read; one blocked; one not yet tried.
Everything below is from the retrieved text, with line references into
`_research/primary_sources/*.txt` so any claim here can be re-checked in one command.

---

## 0. What was actually retrieved, and what is still blocked

| Source | Status |
|---|---|
| Pozsar, *Shadow Banking: The Money View*, **OFR WP 2014-04** | **Retrieved**, 23,499 words, text-extracted |
| Adrian, Ashcraft, Boesky & Pozsar, *Shadow Banking*, **NY Fed Staff Report 458** | **Retrieved**, 15,357 words, text-extracted |
| Pozsar & Singh, *The Nonbank-Bank Nexus and the Shadow Banking System*, **IMF WP/11/289, Dec 2011** | **BLOCKED — `imf.org` returns HTTP 403.** Framework summary below is from search-result abstracts, **not** from the paper. Flagged accordingly |
| Pozsar, *Institutional Cash Pools and the Triffin Dilemma*, **IMF WP/11/190** | **BLOCKED — 403.** Not attempted via other hosts |

**Retrieval note for the next agent:** `financialresearch.gov` and `newyorkfed.org` serve PDFs
to a normal browser user-agent over `curl -L`. `imf.org`, `rba.gov.au` and `papers.ssrn.com` all
returned 403 to both `WebFetch` and `curl`. `pdftotext -layout` is installed and works. Do not
re-try the IMF direct URLs; find another host or another route.

**Citation correction:** the joint Pozsar–Singh paper is **December 2011, WP/11/289** — not
2012 or 2013. The 2013 date attaches to Singh's *solo* *The Economics of Shadow Banking* in the
RBA conference volume. Both exist; they are different papers. (C-041.)

---

## 1. The finding that matters most: Pozsar already specified the accounts we have been improvising

He calls for three satellite accounts to supplement the Financial Accounts —
**Flow of Collateral, Flow of Risk, Flow of Eurodollar**
(`Pozsar_2014_OFR_ShadowBanking_MoneyView.txt:66`, `:110`, `:137`, `:3088`–`:3107`).

Set that against what this project built independently, without reference to it:

| Pozsar's proposed account | What we built | Verdict |
|---|---|---|
| Flow of Collateral | The repo/collateral channel, the FR 2004C multiplier reconstruction, the ASC 860-30-50 footnote series | **Unwitting partial implementation** |
| Flow of Eurodollar | `2026-08-21-Offshore-Dollar-And-Money-Like.md`, the BIS LBS work | **Unwitting partial implementation** |
| Flow of Risk | — | **Nothing.** Not attempted, not on any list |

**This is not a coincidence to note and move past.** It means the measurement handbook has been
reinventing a specified structure, channel by channel, without the organising schema — which is
exactly why it came out as nine silos with a double-counting problem instead of a set of
articulated accounts. **Do not start a fourth improvised channel. Read §3088–3110 first and
adopt the schema.**

---

## 2. The money leg, which we had recorded as unmeasured, is fully specified in the source

Our own text conceded institutional cash pools were *"the actual marginal demanders in the
Pozsar account"* and *"were not measured by anyone here"*
(`2026-08-21-Safe-Asset-Share-Reexamined.md:179`). The source defines them precisely.

**The definitional statement** (`:100`): for institutional cash pools, **money begins where M2
ends**. M2 measures *household* money demand and was built on a transactional-liquidity
hierarchy. Cash pools are too large to be deposit-insurance eligible, so they rank claims by
**safety — proximity to government — first**, and transactional liquidity second.

**The four categories of institutional cash pool** (`:987`–`:990`):

1. the liquidity tranche of **FX reserves**
2. the cash balances of **global corporations**
3. the centrally managed cash balances of **institutional investors and the largest asset managers**
4. the **cash-collateral reinvestment accounts of securities lenders**

**Scale** (`:992`–`:994`): at least **$6trn** under management at end-2013; average balance
~$10bn; **$1bn** is the qualifying threshold. Mandate is *"do not lose"* (`:1002`).

**Why they matter for the nexus:** cash pools hold money claims for *financial-economy*
transactions — FX peg fixing, corporate cash safekeeping, derivatives-overlay and
securities-lending liquidity — not real-economy ones (`:996`–`:1000`). **This is the direct
answer to the "leak objection"** standing as §5 item 8: money held by cash pools is not
income-like and is not going to be spent on goods, by mandate and by purpose. That item can now
be worked rather than speculated about.

---

## 3. The shadow-money taxonomy — a four-cell classification where we have a per-channel binary

Our channel map asks each of nine channels *"is it money creation?"* and records
`creates_near_money` / `creates_credit_not_money` / `contested`. Pozsar classifies on two axes
instead: **par on demand vs par at maturity**, crossed with **public / private / insured**.

**Par ON DEMAND money claims, end-2013** (`:719`–`:786`), largest first:

| Rank | Category | Size | Composition |
|---|---|---|---|
| 1 | **Private shadow money** | **$3.2trn** | Uninsured demand deposits; overnight private repo from dealers' *credit* desks; constant-NAV prime MMF shares |
| 2 | **Public money** | ~**$2.6trn** | Fed liabilities just under $2.5trn (ex-currency) + Treasuries with <7 days remaining, >$100bn |
| 3 | **Public shadow money** | **$2.3trn** | Overnight *government* repo (Treasuries, agency debt, RMBS) from dealers' government desks; constant-NAV government-only MMF shares |
| 4 | **Insured money claims** | **$1.4trn** | Insured demand deposits |

**Par AT MATURITY money-like claims** (`:843`–`:852`): largest is savings plus small and large
time deposits at banks; then **public money-like claims** (T-bills and notes, 7 days to 1 year)
at >$2.3trn; then **private shadow money-like claims**, mostly banks' large deposits, >$1.2trn;
smallest is **public shadow money-like claims**, term government repo, ~$800bn.

**The headline comparison** (`:854`–`:856`): at 2013Q3 the shadow banking system issued
**more than $3.8trn** of par-on-demand money claims — **$800bn MORE than retail and wholesale
banks' $3trn of demand deposits.** On par-at-maturity claims the Treasury outsupplied the shadow
system, and both were dwarfed by bank time deposits.

**Core system size** (`:861`–`:862`): just under **$5trn** at 2013Q3, down from a peak of over
**$8trn at 2008Q2**.

> **These are 2013 figures and they are the whole point of quoting them: nobody in this project
> has built the 2026 equivalent.** That is the money leg, and it is now a specified,
> implementable task rather than an acknowledged hole.

---

## 4. Pozsar's discriminating test — sharper than ours, and it disciplines the channel map

> *"if lending without money creation does not qualify as banking, neither should capital market
> lending without money market funding qualify as shadow banking"* (`:874`–`:876`).

The test is **money-market funding**, not money creation in the abstract. His $5trn/$8trn
figures are deliberately **narrower** than the Pozsar et al. (2010) estimates for two stated
reasons (`:864`–`:872`):

1. they **net** holdings between intermediaries, where the earlier measures were **gross**; and
2. they **exclude all capital-market lending not funded in the money market**.

Both earlier choices *"inflated aggregate measures further."*

**Apply this to our nine channels and several verdicts look unsafe.** Any channel funded by
long-dated or locked-up capital rather than by money-market instruments fails Pozsar's test for
inclusion, whatever our binary said. Private credit, PE fund-level leverage and securitisation
are the obvious candidates for re-examination. **This does not make them unimportant — it makes
them a different object**, and mixing the two is the category error this project keeps making.

---

## 5. A correction to something I wrote earlier today

In `RESEARCH_STATE.md` §1.0 I wrote that a security collateralising three channels at once *"is
not double-counting — it is the phenomenon."* **That is half right, and stated as though it were
wholly right.** Precisely:

- When measuring **reuse, velocity or chain length** (Singh's object), the repeated appearance
  of one security **is** the phenomenon, and netting it away destroys the measurement.
- When measuring the **stock of money claims** (Pozsar's object), the repeated appearance is
  **exactly the inflation he nets out by construction**, and failing to net it overstates the
  system.

Same fact, two measurements, opposite handling. **The rule is: net for stocks, never net for
velocity — and never report one number as though it served both.** This is the same
gross-versus-net failure mode already logged four times in this project, arriving in a new
place. §1.0 has been amended.

---

## 6. What this pass changes on the list

- **N1 is partially unblocked**, not done. Two sources read; **WP/11/289 itself is still
  unread** and it is the paper that names the nexus. The framework summary in §0 of this file
  is from abstracts and is **not** primary-source-verified — do not cite it as though it were.
- **N2 is now specified** — the four cash-pool categories and the money-claim taxonomy give a
  build target and a 2013 benchmark to extend to 2026.
- **N4 gains a schema** — harvest the double-counting sections *into* Flow of Collateral / Flow
  of Risk / Flow of Eurodollar, and net or don't-net according to §5 above.
- **§5 item 8, the leak objection, is answerable** from §2 rather than speculative.
- **New:** the channel verdicts need re-examination against §4's inclusion test.

## 7. Flagged as separately investigable, per the principal's instruction

Not folded into anything; recorded here as candidates in their own right.

1. **The Flow of Risk account has no counterpart anywhere in this project.** Pozsar names three
   satellite accounts; we have partial versions of two and nothing at all for the third.
2. **Shadow money peaked at $8trn in 2008Q2 and was $5trn in 2013Q3.** Nobody has drawn the
   series forward. The 2026 level is unknown to us and is a first-order fact about the nexus.
3. **The dealer as the pivot.** `:146` and `:184` put dealers as the intermediaries between cash
   pools and levered fixed-income investors, and tie dealer balance-sheet growth to cash-pool
   proliferation. Our channel map has no dealer-centric view; it is organised by instrument.
4. **Securities lenders' cash-collateral reinvestment accounts are simultaneously a cash pool
   (category 4) and a collateral source.** That is the nexus in a single institution, and it is
   the sharpest available test case for the interlock.
