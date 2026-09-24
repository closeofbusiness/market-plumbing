# LIT1 — the household residual is recategorized, not decomposed (15 September 2026)

**Status: RESULT.** Ranked item 2. The three Gemini leads, read at source. Gemini's 15 Sep
map itself was not on disk under `_research/`; the leads below are the ones
`RESEARCH_STATE.md` named. E-005: a directionally right estimate with a band is a result.
This pass does not produce a household operating-company purchase number (C-083).

> **Verdict.** A literature exists that *relabels* the Fed's household residual by tax status
> (Rosenthal–Mucciolo), that *subtracts nonprofits* (Holmquist), and that *distributes the
> leftover by wealth* (the DFA / Batty et al.). None of it sizes private-equity funds versus
> personal trusts versus natural persons inside the F51 corporate-equities household line.
> Gemini's claim that the residual **has been decomposed** treated a tax-policy recoding as
> an entity census. That over-read is C-084.

## The citation layer, first — because that is how this project fails

Gemini named **Rosenthal & Burke (2024), "Ownership of Total U.S. Corporate Equity."** That
title-author-year triple does not exist. Crossref query on author+title, 15 Sep 2026:

- The 2024 article is **Steven M. Rosenthal and Livia Mucciolo**, *"Who's Left to Tax?
  Grappling with a Dwindling Shareholder Tax Base,"* Tax Notes Federal, **1 April 2024**,
  SSRN `10.2139/ssrn.4797771`. **"Ownership of Total U.S. Corporate Equity" is a section
  heading**, not the title.
- **Theo Burke** coauthored the **2020** NYU working paper of the same family (PDF dated
  9 October 2020, on disk at `data/vintages/lit1_2026-09-15/rosenthal_burke_2020_whos_left_to_tax.pdf`).
- The TPC-hosted PDF (`taxpolicycenter.org/sites/default/files/publication/165884/ssrn-id4797771.pdf`)
  **403s to a scripted fetch** — the URL RESEARCH_STATE already flagged. Text below is from
  that PDF via a search renderer, cross-checked against the Tax Notes HTML extract, both
  saved under `data/vintages/lit1_2026-09-15/`.

This is the C-079 shape: one real paper, split or merged with another. The numbers in the
section heading survive. The claim that the paper *names the bodies inside the plug* does not.

## What Rosenthal–Mucciolo actually do

They start from the Fed's corporate-equities table, **look through** mutual funds / ETFs /
CEFs, strip S-corp and other pass-through *issuance*, add FDI, and **reassign holder
categories into tax buckets**: foreigners, retirement accounts (DB, DC, IRAs, life separate
accounts), government, nonprofits, taxable accounts. They "follow the same constraint as
the Fed: total equity issuances for tax must equal total equities held for tax" (2020
appendix, carried into 2024). The Fed's residual is the input they then split into IRAs,
529 plans, nonprofits, and a taxable leftover.

Headline shares, 2024 article, **their** reconstructed "total U.S. equity" (not Z.1's
instrument):

| | 1965 | 2022 |
|---|---:|---:|
| taxable accounts | **79%** | **27%** |
| tax-exempt retirement accounts | ~7% | **~27%** |
| foreign (incl. FDI) | (small) | **42%** at end-2022 |

Publicly-traded-only taxable share: 81% → 28% (their Table 7). The 2020 Burke paper had
foreign ~40%, taxable ~25%, retirement ~30% for 2019. Same family, updated vintage.

**What they leave inside "taxable."** Verbatim from the 2024 PDF extract:

> Hedge funds and private equity funds are partnerships, which are passthroughs for tax
> purposes. The Fed leaves stock that is held by domestic hedge and private equity funds
> in its household sector, the residual category. … In theory, we ought to reallocate the
> funds' holdings to the funds' owners … **but we lacked the data to do so.**

They estimate the foreign/domestic reallocation they cannot make would be "relatively
small, about 1 percent of publicly traded U.S. equity and 2 percent of total U.S. equity,"
from Fed table B.101.f line 17 and SEC Private Fund Statistics (9 Jan 2024). **That is an
admission, not a decomposition.** PE funds stay in the taxable bucket by construction.
S-corporation stock stays there too, on purpose.

**The hedge-fund half of that footnote is stale for the instrument we use.** F51.1.s line
53 (`LM623064105.Q`, "Hedge funds (domestic); corporate equities net of short sales") is a
named holder. It is first non-zero in **2012:Q4** ($288.5bn). The holder identity still
closes to $0.0bn with that line included (checked 2012:Q3, 2012:Q4, 2022:Q4, 2026:Q2 on the
2026:Q2 vintage). Current Z.1 table descriptions name **private equity funds and personal
trusts** as the unidentified entities in the household residual; hedge funds have their
own sector tables (S124.7) beginning 2012:Q4. At 2026:Q2 domestic HF equity is $906.2bn —
0.7% of the instrument, 1.7% of the household line. Rosenthal 2024 is citing the
*supplementary* B.101.f table, which the Fed still does not subtract from B.101. It is
already subtracted from F51.

**Do not quote 42% or 27% as Z.1 shares.** On the same 2026:Q2 vintage, 2022:Q4, the
instrument itself is household **39.4%**, rest-of-world **16.6%**, domestic hedge funds
**0.9%**. Rosenthal's 42% is FDI-inclusive, look-through, pass-through-stripped. Different
denominator. The 1965 taxable 79% is close to our raw household 81.8% because retirement
accounts and foreign holdings were then small; the two series have since diverged, and the
divergence *is* Rosenthal's recoding of IRAs and FDI.

IRAs live in the F51 household line. Rosenthal pulls them out with ICI/SOI, not by opening
the residual. That is the tax-status recategorization. It is real. It is not PE versus
persons versus trusts.

## Holmquist (2019) — the nonprofit split, already used

Elizabeth Holmquist, *"Household and Nonprofit Balance Sheets in the Financial Accounts of
the United States,"* FEDS Notes, 4 January 2019, doi `10.17016/2380-7172.2313`. Crossref
lists her as sole author. HTML vintage on disk.

B.101.n is built from IRS Form 990 / 990-PF plus BEA nonfinancials. B.101.h is **B.101
minus B.101.n**, with some instruments assigned wholly to households. Corporate equities
and mutual fund shares are **combined**. Nonprofits were ~6% of combined-sector net worth
as of 2018:Q3, "a share that has been quite stable." This is the source of HR's 5.5–8%
cross-concept nonprofit band. It is a split of the *sector*, not of the F51 equity
instrument, and it is itself residual:

> because B.101.h is calculated residually from B.101, which is itself calculated
> residually, any data issues that stem from residual calculation come to rest in B.101.h.
> In particular … hedge funds and other private equity funds.

Footnote 7 (January 2019): a hedge-fund sector was planned; until then they sit in both
B.101 and B.101.h. The F51 carve-out had already begun in 2012:Q4; the Note is about the
balance-sheet tables, not F51. **PE funds remain inside B.101.h.** Holmquist does not size
them.

## Smith, Zidar and Zwick (2023) — a wealth census, not a holder census

Matthew Smith, Owen Zidar and Eric Zwick, *"Top Wealth in America: New Estimates Under
Heterogeneous Returns,"* *Quarterly Journal of Economics* 138(1), 2023,
doi `10.1093/qje/qjac033` (published online 29 August 2022). Author PDF on disk
(`ericzwick.com/wealth/wealth.pdf`).

They capitalize tax-return flows with heterogeneous returns, scaling to Financial Accounts
aggregates through 2016. For C-corporation equity they weight dividends 0.9 and realized
capital gains 0.1, chosen to match SCF top equity-wealth shares. In 2016, C-corporation
equity is 34% of top-0.1% wealth and 53% of top-0.001% wealth. Sample ends **2016**. They
"do not assign residual wealth in the Financial Accounts to fixed income" — that residual
is SZ20's leftover *wealth*, not Z.1's household equity holder line.

This paper tells you how concentrated C-corp wealth is among tax units. It does not tell
you how much of `FU153064105` is a PE fund, a personal trust, or a brokerage account. The
DFA (Batty, Bricker, Briggs, Holmquist et al., FEDS 2019-017) is the same move at the Fed:
reconcile SCF to B.101.h and **distribute the aggregate**, including whatever PE and trusts
are inside it, as if they were household SCF holdings. SCF corporate-equity-plus-MF
averages about 106% of B.101.h — close enough to use as a distributional key, not a
carve-out.

## Independent check on our instrument (Z.1 2026:Q2 vintage)

Levels, $bn, F51.1.s. Computed `data/lit1/z1_holder_shares.csv`.

| | total | household | RoW | HF domestic | HH % | RoW % | HF % |
|---|---:|---:|---:|---:|---:|---:|---:|
| 1965:Q4 | 735 | 601 | 15 | 0 | 81.8 | 2.0 | 0 |
| 2019:Q4 | 53,326 | 19,536 | 8,129 | 591 | 36.6 | 15.2 | 1.1 |
| 2022:Q4 | 63,879 | 25,140 | 10,612 | 572 | 39.4 | 16.6 | 0.9 |
| 2026:Q2 | 123,687 | 52,119 | 22,211 | 906 | 42.1 | 18.0 | 0.7 |

Holder identity closes at each date listed. The household line is still the plug. It is
larger than Rosenthal's taxable 27% because it still contains IRAs, 529s, nonprofits, PE
funds, personal trusts, and — on this instrument — the ETF shares those bodies hold.

## What this does to the argument

- **C-084.** The residual has not been decomposed into the legal entities the Fed names as
  living in it. A tax recoding and a nonprofit subtraction are not that decomposition.
- **What HR already had, confirmed.** Private equity funds and personal trusts remain
  inside the F51 household line. Domestic hedge-fund *equity* does not, from 2012:Q4.
  Nonprofits are a mid-single-digit slice of the combined sector, not of this instrument.
- **What Rosenthal adds, and it is usable.** On a look-through, FDI-inclusive tax concept,
  taxable accounts were about a quarter of U.S. equity in 2022 and foreign holders about
  two-fifths. That is a statement about *who is taxed*, not about who bought the 2024–26
  ETF wrapper. Carry it with its denominator.
- **What this pass still cannot say.** The mix inside the plug — PE funds vs trusts vs
  persons, and ETF shares vs listed stocks vs closely-held — is not split on F51. Any
  household operating-company purchase number would still be an assumption about who
  holds the wrapper (C-083). N4 stays a separate item: this literature does not give it a
  buyer to trace to.

## Sources

- Rosenthal and Mucciolo, Tax Notes Federal, 1 April 2024. TPC PDF 403 to curl 15 Sep 2026;
  renderer extract and Tax Notes HTML extract in `data/vintages/lit1_2026-09-15/`. Crossref
  `10.2139/ssrn.4797771`.
- Rosenthal and Burke, NYU Tax Policy Colloquium working paper, 9 October 2020. PDF fetched
  from `law.nyu.edu`.
- Holmquist, FEDS Notes, 4 January 2019. HTML fetched from federalreserve.gov. doi
  `10.17016/2380-7172.2313`.
- Smith, Zidar and Zwick, *QJE* 138(1) 2023. Author PDF from ericzwick.com. doi
  `10.1093/qje/qjac033`.
- Batty et al., FEDS 2019-017. PDF from federalreserve.gov.
- Z.1 table descriptions, current release, fetched 15 Sep 2026; F51.1.s from
  `data/vintages/z1_equities_2026Q2/` (11 Sep 2026 vintage). Technical Q&A z13 (onshore
  hedge funds consolidated on B.101) is the *sector* treatment; F51 is the instrument
  carve-out.
