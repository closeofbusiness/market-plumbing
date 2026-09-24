# N2b: `z_k` — the wholesale share of nonbank funding, built
**Date: 2026-08-31. Status: BUILT v1, then ADVERSARIALLY REVIEWED the same day (N2bR, Grok). The v1 headline FELL — C-070, an endpoint artefact plus a category error that inverted the conclusion. Strikes in place; §7 carries the rebuilt finding, which is larger than the one it replaces.**
**All sources free and in-house. Every component traced to a named series in `data/series.tsv`.**

## 0. What `z_k` is, and why it is the object

Pozsar & Singh (WP/11/289 `:715`–`:728`, read at `2026-08-22-Nexus-WP11289-Read.md` §3) extend
Shin's leverage identity by splitting the funding share `z` into **`z_h`** — funding the bank
receives from households as M2 — and **`z_k`** — funding it receives from *other nonbanks* that
is *not* M2. Their claim: the banking system can lever up **with M2 stable**, through the
portfolio choices of the asset-management complex. `z_k` is where that happens, and it is the
one estimable object the framework offers.

Note the layering the definition deliberately allows: if a household holds a retail money-fund
share (inside M2) and that fund lends to a dealer via repo, the *bank/dealer* receives its
funding from a **nonbank**, in an instrument that is **not M2**. That is `z_k`, and the
household's M2 claim is a separate rung. The framework counts the rung the bank actually faces.

## 1. Construction, and the perimeter I can defend

**z_k = W / (W + M2)**, where `W` is measured non-M2 nonbank wholesale funding of the US
banking/dealer system, and M2 is the `z_h` base (H.6, seasonally adjusted).

`W` is built **lender-side** — enumerating who provides the funding — because the N2aR review's
standing rule forbids adding ledgers that measure the same object from opposite sides (a money
fund's repo lending *is* a dealer's repo borrowing; counting both double-counts).

Components, all US perimeter:
- **Private MMF repo** = MMF repo against Treasury + agency + other collateral, **less repo with
  the Fed** (N-MFP3 via OFR). Excluding the Fed leg is essential: the ON RRP is not private
  funding, and at end-2023 it was $968.7bn.
- **MMF bank-related assets** — bank CDs, bank CP, bank deposits held by money funds (N-MFP3).
- **Large time deposits** (>$100k), all commercial banks.

Two bounds on the overlap between the last two (money-fund CDs *are* large time deposits, but
the "bank-related" line also contains bank CP that is not):
- **W_low** treats all MMF bank paper as sitting inside large time deposits (subtract it once).
- **W_high** adds them gross.
The truth is between; both are reported everywhere below.

## 2. The result

$bn, and z_k in per cent:

| date | private MMF repo | MMF bank paper | large time dep. | W_low | W_high | M2 | **z_k low** | **z_k high** |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| 2023-12 | 1,697.2 | 483.5 | 2,225.1 | 3,922.3 | 4,405.8 | 20,779.9 | **15.88%** | 17.49% |
| 2024-12 | 2,237.8 | 464.5 | 2,341.9 | 4,579.7 | 5,044.2 | 21,487.6 | **17.57%** | 19.01% |
| 2025-12 | 2,921.8 | 451.8 | 2,428.8 | 5,350.6 | 5,802.4 | 22,355.3 | **19.31%** | 20.61% |
| 2026-06 | 3,067.8 | — | 2,521.7 | — | — | 23,155.2 | **19.45%** | — |
| 2026-07 | 2,918.4 | 467.4 | 2,537.6 | 5,456.0 | 5,923.4 | 23,218.0 | 19.03% | 20.33% |

**Endpoint note (added post-review, C-070):** 2026-07 is a *soft* endpoint — OFR's repo-with-Fed
line is unpublished for July and June's $6.8bn was carried forward. **2026-06 is the reported
endpoint**; the full private series is in §7. The v1 text below this table reads the 2023-12 →
2026-07 change in isolation, which is exactly the error C-070 records.

Over the window: M2 **+11.7%**, W_low **+39.1%**, private MMF repo **+72.0%**, and
z_k **+3.15pp** (low) / +2.83pp (high). On its face: the wholesale share of nonbank funding rose
by about a fifth.

## 3. ~~The finding: almost all of that rise is the Fed handing back its counterparty role~~ [STRUCK — C-070]

**This section's claim — that z_k is flat at 19.05% once the Fed is counted as a wholesale
borrower, and therefore "the nexus did not expand as a share of money" — is withdrawn.** It
failed on two independent grounds, both found by the N2bR review and both re-measured by me:

1. **Endpoint artefact.** The Fed-inclusive ratio is not flat. Measured at nine dates it runs
   15.32% (2021-12), 17.85% (2022-12), 19.99% (2023-06), 19.05% (2023-12), 18.76% (2024-12),
   20.03% (2025-06), 19.52% (2025-12), 19.46% (2026-06), 19.05% (2026-07) — a ~4.7pp range. My
   two chosen dates both happen to sit at 19.05%. I named this risk in the review parcel and
   published the finding anyway.
2. **Category error.** Counting the Fed as a `z_k` borrower is wrong on the definition: `z_k`
   is non-M2 funding *of banks*, and the ON RRP funds the **central bank**. The Fed-inclusive
   measure is not `z_k`.
3. The **"78.8% of private-repo growth is the RRP drain"** attribution also falls: it compares
   two stock changes of similar size. Over the same window MMF Treasury holdings rose
   **+$1,183.1bn** — more than the entire $961.9bn drain — and MMF AUM rose $2,010.6bn. The
   destination of the RRP cash is not pinned by that arithmetic.

The corrected finding is in §7.

## 4. Cross-validation

My N-MFP3-derived private MMF repo at 2025-12 is **$2,921.8bn**. OFR Brief 26-03's entity-typed
repo census — an independent collection, different method — puts money-fund lending at
**$2,927.5bn** for H2-2025. A **0.19%** difference between two unrelated sources on the largest
component of `W`.

## 5. What `W` excludes — the honest perimeter

`W` is a **lower bound on a partial perimeter**, and the trend in §2–§3 is conditional on it.
Known non-M2 nonbank funding NOT in `W`:

- **Hedge funds' cash lending: $1,007.0bn** (OFR 26-03, H2-2025) — hedge funds are net borrowers
  overall but lend over a trillion gross, and that is nonbank funding of dealers (the C-066
  lesson: they are not a terminal node).
- **Non-primary broker-dealers lend $1,086.8bn** (same source).
- **Securities-lending cash collateral** reinvested into bank paper (ISLA measures the on-loan
  side, not the reinvestment destination).
- **Offshore USD deposits from nonbanks** — $7.6trn all-country (N2a §1), but that is a *global
  banks* perimeter, not US banks, and cannot be added to a US-perimeter W without the exact
  double-count the N2aR rule forbids.
- **ABCP outside money-fund holdings**, and direct corporate/pension wholesale deposits beyond
  the large-time-deposit line.

Adding the two OFR segments alone at 2025-12 would put `W` near $7.4trn and z_k near 25%. I do
**not** report that as the number: those are H2-2025 averages on a different collection, with no
comparable series at my other dates, so they can size the gap but cannot carry the trend.

**Therefore:** the *level* of z_k here (≈19–20%) is a floor, and the *direction* (flat once the
Fed is included) is the finding that carries — but it is established on the MMF-plus-large-time-
deposit perimeter only, and a wider perimeter could move it. That is the first thing an
adversarial review should attack.

## 6. Open, after the review

1. **Add the hedge-fund lending leg and recompute** — the decisive perimeter test. Use OFR
   Hedge Fund Monitor Form PF reverse repo (`FPF-ASSETCLASS_REPO_REVERSEREPO_SUM`, already in
   `data/series.tsv`: $1,040bn 2023Q4 → $1,399bn 2026Q1) at every overlapping quarter-end from
   2021Q4, and report whether the doubling in §7 survives. **Not** the non-primary-dealer leg:
   dealers are not `z_k` "other nonbanks" (C-070 amendment).
2. **Rebuild the denominator.** M2 is not `z_h`: it contains currency, retail money-fund shares
   and corporate deposits, none of which is household funding of banks. H.8 deposit liabilities
   less large time, or Z.1 household checkable-plus-small-time, would be defensible. Expected to
   raise the level at every date; the direction should be unaffected — which is itself worth
   testing rather than assuming.
3. **FHLB advances** as an omitted non-M2 bank-funding leg ($583.5bn 2023Q4 → $462.5bn 2026Q1,
   relayed unverified) — it *shrank*, so including it slightly damps the rise.

## 7. Review outcome and the rebuilt finding (N2bR, Grok, 31 Aug)

Claim 3 fell (C-070). Claims 1, 2, 4, 5 stand with amendments. Grok's independently recomputed
Fed-inclusive series matched mine **to the decimal at five of six dates** (the sixth differs by
0.03pp, an M2 vintage difference between the ALFRED and current-H.6 releases).

### The corrected result: `z_k` more than doubled, then plateaued

Using the **private** measure — the correct one, since the Fed is not a bank:

| date | z_k (private) | note |
|---|---:|---|
| 2021-12 | **9.09%** | ON RRP still filling |
| 2022-12 | 9.70% | |
| 2023-06 | 13.66% | RRP at its peak, beginning to drain |
| 2023-12 | 15.88% | |
| 2024-12 | 17.57% | |
| 2025-06 | 18.88% | |
| 2025-12 | 19.31% | |
| 2026-06 | **19.45%** | last month with every OFR line published |

**The wholesale share of nonbank funding more than doubled in four and a half years**, and the
path is monotonic — not two endpoints that happen to rhyme. This *is* the Pozsar–Singh
mechanism running in the open: the asset-management complex moved its funding from the central
bank onto private dealers' balance sheets while M2 grew far less. The v1 conclusion inverted it.

It has now **plateaued** (19.31 → 19.45% over the last three observations) for a mechanical
reason: the ON RRP is empty, so there is nothing left to hand back. The handoff is complete,
and any further rise in `z_k` would have to come from genuinely new wholesale funding rather
than from re-intermediation.

### Amendments folded

- **The July 2026 endpoint is soft.** OFR's "repo with Fed" line is unpublished for July; v1
  carried June's $6.8bn forward without saying so. **2026-06 is now the reported endpoint**,
  the last month where every component exists. (With Fed = 0 in July, z_k_low is 19.05%, not
  19.03%.) H.8 large time deposits are 2,538.1 on the current vintage, not 2,537.6.
- **The M2 denominator is not `z_h`** (Claim 1 amendment, accepted): M2 contains currency and
  retail money-fund shares, neither of which is bank funding, plus ~$1.9–2.4trn of
  nonfinancial-corporate deposits. A stricter denominator would *raise* z_k at every date. The
  direction of the corrected finding does not depend on it, but the levels do — flagged, not
  yet rebuilt.
- **Non-primary broker-dealers are dealers, not "other nonbanks"** — they should never have
  been in the §5 sketch of what to add. Removed from that reasoning.
- **A real time series exists for the hedge-fund leg**, which v1 said it lacked: OFR Hedge Fund
  Monitor Form PF reverse repo (`FPF-ASSETCLASS_REPO_REVERSEREPO_SUM`), $1,040bn (2023Q4) →
  $1,399bn (2026Q1) — already in `data/series.tsv`. Adding it moves the ratio materially, so
  **the perimeter question in §5 is now answerable rather than merely flagged**: that is the
  first thing N2b v2 should do. Perimeter caveat: Form PF is a global qualifying-hedge-fund
  population, not OFR 26-03's US repo census (1,335 vs 1,007 at end-2025), so it cannot simply
  be summed into a US-perimeter W.
- **Cross-validation narrowed** (Claim 4): the 0.19% agreement is between a 2025-12 month-end
  N-MFP3 snapshot and an H2-2025 daily average with the Fed excluded — close on the same
  object, but it validates *that month only*, not 2023-12 or 2026-07.
- **New omitted leg found:** FHLB advances to US depositories, $583.5bn (2023Q4) → $462.5bn
  (2026Q1) — non-M2 bank funding that *shrank*, so including it would slightly damp the rise.

## 8. v2 — the perimeter test (31 Aug, three adversarial lenses)

v1 measured `z_k` on money-fund repo plus large time deposits and flagged its own perimeter as
the first thing to attack. v2 adds the leg v1 said it lacked — **hedge funds' cash lending**
(OFR Hedge Fund Monitor, Form PF `FPF-ASSETCLASS_REPO_REVERSEREPO_SUM`, quarterly from 2013) —
and tests three stricter denominators. Every quarter-end is computed and shown; no two-endpoint
claims (the C-070 rule).

**Perimeters.** W1 = private money-fund repo (Treasury + agency + other collateral, less repo
with the Fed) + large time deposits. **W2 = W1 + hedge-fund reverse repo.**
**Denominators.** M2; M2 less currency less retail money funds; H.8 total deposits less large
time; Z.1 household deposits.

| quarter | W1/M2 | W2/M2 | W2/(M2 ex curr,rMMF) | W2/(H.8 dep ex LTD) | W2/(Z.1 hh dep) |
|---|---:|---:|---:|---:|---:|
| 2021-12 | 9.14% | 13.10% | 15.24% | 16.42% | 17.58% |
| 2022-06 | 8.47% | 12.36% | 14.45% | 15.57% | 16.53% |
| 2022-12 | 9.75% | 13.37% | 15.82% | 16.95% | 18.11% |
| 2023-06 | 13.65% | 17.11% | 20.57% | 21.89% | 23.02% |
| 2023-12 | 15.94% | 19.33% | 23.40% | 24.73% | 25.87% |
| 2024-06 | 17.02% | 20.42% | 24.82% | 26.16% | 27.54% |
| 2024-12 | 17.63% | 20.98% | 25.59% | 26.91% | 28.36% |
| 2025-06 | 18.87% | 22.49% | 27.49% | 28.69% | 30.29% |
| 2025-12 | 19.37% | 23.07% | 28.25% | 29.35% | 31.20% |
| 2026-03 | 19.24% | 23.07% | 28.21% | 29.22% | 31.05% |

*Last quarter with every input is 2026-03 (Form PF and Z.1 both end there). The H.8 vintage
pulled 31 Aug differs from v1's FRED-mirror input by up to $19bn — a benchmark revision — so
v1's 15.88% at 2023-12 reads 15.94% here.*

### What the wider perimeter does

**The rise survives, and dilutes.** W1 grows 2.10× over the window; W2 grows **1.76×**, because
the hedge-fund leg was already $1,078bn in 2021-12 and grew only ~30% (to $1,399bn),
while the money-fund-plus-deposit leg grew 2.5×. Hedge funds make the *level* higher everywhere
and the *slope* shallower — they do not reverse it.

**The direction is robust to every choice made.** All twelve (perimeter × denominator) pairs are
higher at 2026-03 than at 2021-12 and trace the same shape: trough mid-2022, steep climb through
2023, plateau from mid-2025. On the strictest bank-funding denominator — H.8 deposits less large
time — `z_k` runs **16.42% → 29.22%**.

### The three lenses

| lens | verdict | what it did |
|---|---|---|
| endpoint artefact | **stands** | recomputed all 216 cells independently; max deviation 0.00005pp; tested every start quarter |
| denominator | **stands** | recomputed two denominators from raw inputs; direction unchanged, only levels move |
| double-count | **stands-with-amendment** | see below (run on a flat-fee seat; `_research/ZK2_verification_2026-08-31.md`) |

### Amendments folded from the double-count lens

1. **The Form PF perimeter is global; every other input is US.** Form PF covers qualifying hedge
   funds worldwide ($1,335bn at 2025-12) while OFR Brief 26-03's US repo census puts US
   hedge-fund lending at $1,007bn — 75.4%. Rescaling the leg uniformly by that factor moves
   `z_k(W2,M2)` at 2025-12 from **23.07% to 22.19%, a level change of 0.88pp**, and leaves the
   path monotonic (12.16% → 18.53% → 22.19% at 2021-12 / 2023-12 / 2025-12). **The finding is
   robust to the perimeter; the level is not, to within about a point.** Carried: the 75.4%
   ratio is benchmarked only at H2-2025 and assumed constant earlier.
2. **`W` is a lower bound, and the size of the understatement is known.** Money funds' bank paper
   is treated as sitting inside large time deposits and never added. That is right for the CD
   portion and wrong for the bank commercial paper portion, which is nonbank funding of banks that
   `W` misses. Maximum understatement = the whole bank-related line: $301.6bn (2021-12),
   $483.5bn (2023-12), $451.8bn (2025-12). The CD/CP split is not disaggregated in the source.
3. **No lender double-count.** Money funds and hedge funds are disjoint reporting populations,
   and the load-bearing fact is verified verbatim from OFR Brief 26-03 on disk: *"Money funds are
   exclusively lenders"*, borrowing $0.0bn. A hedge fund therefore cannot be lending to a money
   fund in the reverse-repo line, so the two legs cannot double-count the same dollar.

**Relayed unverified** (regulatory assertions, not measurements): that Form PF classifies a hedge
fund's money-fund holding under Question 33 rather than as reverse repo; that Rule 2a-7 restricts
money-fund repo counterparties to dealers, banks and FICC; and that peer-to-peer hedge-fund repo
is "non-existent". The last is the weakest link in the not-a-bank check.

### Status

`z_k` has now survived a perimeter widening, three denominators and three adversarial lenses.
**It is ready to carry the N4 synthesis**, with two standing caveats: the level is
perimeter-sensitive to about a point, and `W` is a floor by the bank-CP share.
