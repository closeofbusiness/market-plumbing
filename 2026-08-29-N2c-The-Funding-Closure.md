# N2c — The funding closure: who is the marginal buyer of everything, and what creates their purchasing power

*29 August 2026, **v1**. Raised by the principal ("we still don't understand what is driving the massive
demand… the actual money creation or collateral creation"). Built the same day from primary packages pulled
fresh: the full Fed **H.8** series package (28 Aug vintage) and the full **Z.1** all-series package
(11 Jun 2026 release), raw extracts archived `data/vintages/z1_closure/`. Every cell below is a Z.1 flow
(FU series, quarters summed) or an H.8 level change; internal check: summed sector absorption equals issuer
liability to the dollar. Serves **A12** — this is the money-creation half of the goal posed as an identity.
Result promoted as **S-N2c**.*

---

## 1. The answer in one paragraph

**There is no single "someone." The financing regime has rotated three times in four years, and the honest
answer is a sequence: 2023 was paid for by *reallocation* (money funds draining the ON RRP and hedge funds
levering); 2024–25 by *foreigners, banks and the long-only complex*; and 2026, with every buffer spent, by
*new money* — the Fed back in the market and, above all, banks creating deposits by lending to nonbank
financial institutions: +$625bn in 2025 alone, $2.0trn outstanding.** Meanwhile the equity market's only
structural net buyer is the corporate sector itself — net issuance **−$304bn to −$611bn a year** — funded in
the same credit expansion. Money creation, collateral creation and valuation are one circuit: deficits and
data-centre capex issue the paper; banks and the Fed create the money that absorbs it; the collateral so
created (N3: sources ×3) is levered to absorb more of it; and corporates convert credit into equity demand.

## 2. The closure table — US Treasury absorption, flows, $bn

| Buyer (Z.1 flows) | 2023 | 2024 | 2025 | 2026Q1 |
|---|---:|---:|---:|---:|
| **Net issuance (= all-sector absorption, check passes)** | **2,382** | **1,913** | **1,930** | **572** |
| Money market funds | **1,205** | 725 | 523 | **−91** |
| Households + nonprofits *(incl. hedge funds — the levered bid)* | **814** | 147 | 276 | 50 |
| Rest of world | 728 | 609 | 510 | 129 |
| **Federal Reserve** | **−741** | −515 | −83 | **+156** |
| Banks (private depository) | −100 | 197 | 203 | 95 |
| Mutual funds + ETFs + closed-end | 102 | 207 | 270 | 96 |
| Insurers + pensions (incl. S&L retirement) | 241 | 303 | 133 | 72 |
| Broker-dealers | 124 | 126 | 57 | **109** |
| State & local govts, GSEs, corporates, other | 105 | 177 | 66 | 3 |

**Read the columns as regimes.** *2023:* the ON RRP drain let money funds absorb half the issuance and
hedge funds (inside "households") took another third — **existing money, reallocated and levered; nothing
new needed.** *2024–25:* that engine fades (MMFs 1,205→523), and the slack is taken by the rest of the
world (~$0.5–0.6trn/yr), banks turning buyers, and the long-only complex. *2026Q1:* the buffers are gone —
MMFs are net **sellers**, and the marginal buyers are the **Fed (+$156bn, the largest single buyer in Q1 —
~~its reserve-management bill purchases took ~69% of net bill issuance YTD~~ **[C-063: window-mismatched
ratio; corrected on matched endpoints: 63.6% Dec-31→end-Jul, falling to 44.4% by 26 Aug as August's issuance
wave was privately absorbed; and per the July MPR only ~$160bn of ~$250bn of bill buying was RMP, the rest
agency-principal reinvestment]**), dealers warehousing (+$109bn), and banks.** The Fed's four-year swing,
−741 → +156/quarter, stands as a Q1 fact — but ~~at the margin, the government is again financed by
base-money creation~~ **[C-063: the monetization reading is retracted — Jefferson, verbatim: RMPs "are not
quantitative easing… These purchases do not have any implications for the stance of monetary policy"; the
Fed's share was falling into August; see §7]**.

## 3. The line nobody in our map had measured: banks lending the shadow system its money

Fed H.8, item 1030, all commercial banks — **loans to nondepository financial institutions**:

| | Dec-15 | Dec-19 | Dec-21 | Dec-23 | Dec-24 | Dec-25 | **Jul-26** |
|---|---:|---:|---:|---:|---:|---:|---:|
| Level, $bn | 384 | 581 | 805 | 1,002 | 1,202 | 1,827 | **2,005** |
| Annual flow | | | | **+106** | **+200** | **+625** | +178 (7mo) |

This is genuine deposit creation — bank credit — flowing to exactly the sector doing the private-credit,
PE and data-centre warehouse lending. **The 2025 flow (+$625bn) exceeds the entire ABCP market ($488bn),
exceeds that year's MMF Treasury absorption, and rivals the Fed's whole bill-buying programme.** Set beside
the channels we spent the week measuring: the conduits create tens of billions; this creates hundreds.
It is the largest money-creation channel in the map, and as of this morning it is in the data layer
(`bank_loans_to_nondepository_fis_bn`, monthly from 2015). **Scope, per C-020 (and it makes the point
stronger):** the H.8 NDFI line covers loans to *credit intermediaries* — private credit, mortgage/consumer
intermediaries, PE lending vehicles, warehouses — and **excludes loans for purchasing or carrying
securities**, which sit in an adjacent H.8 line. So the $2.0trn is the credit-machine channel alone; the
banks' securities-carry lending to nonbanks is *additional* bank credit on top of it, not inside it.

## 4. The equity side has no outside buyer — the credit machine buys the stock market

Z.1, nonfinancial corporate net equity issuance (FU103164105): **−$611bn (2023), −$398bn (2024), −$304bn
(2025)**, +$31bn in 2026Q1 (the first positive quarter — worth watching). Corporate & foreign bond net
issuance, all sectors: 505 / 728 / 705, and **$335bn in 2026Q1 alone — annualising ~$1.3trn**, the
data-centre wave visible in the aggregate. The structure: ~~**households and institutions are net sellers of equities; the corporate sector, borrowing in
the bond market, is the only structural net buyer.**~~ **[C-065: BROKEN — refuted by the Fed's own F51.1.t
net-purchase rows, verified to reproduce exactly: households +$984.9bn (2024) / +$863.5bn (2025), ETFs
+$840.4bn / +$958.5bn, rest of world +$185.3bn / +$643.7bn, while the corporate sector was a net SELLER as
holder (−$324.2bn / −$197.6bn) even as it retired net issuance. Negative net issuance is not sector demand.
Caveats cut both ways: the household row is the Z.1 residual (and holds domestic hedge funds), and F51.1.t
counts household ETF-share purchases and ETF stock purchases as two layers. See §7.]** Rising
valuations therefore do not require new outside money — they require the credit machine of §3 and §5 to
keep funding issuers who retire their own shares. This is the A11 intuition ("saving falls while
valuations rise") resolved as an identity rather than a paradox.

## 5. So what "creates the liquidity"? The five engines, sized

| Engine | 2023 | 2025 | 2026 run-rate | Status |
|---|---|---|---|---|
| 1. Reallocation + leverage of existing money (ON RRP drain; HF repo via MMF cash) | dominant (~$2trn) | fading | **exhausted** (ON RRP $0.2bn; MMFs net sellers) | settled (D1/D3/N3) |
| 2. **Bank money creation to nonbanks** (H.8 item 1030) | +106 | **+625** | ~+300 | **measured today; largest live engine** |
| 3. **Central bank** (Fed RMPs) | −741 (QT) | −83 | **+156/qtr** | measured; the marginal Treasury buyer |
| 4. Foreign inflow (RoW) | +728 | +510 | ~+500/yr | measured; steady, not rising — and TIC *understates* the levered bid ($1.4trn Cayman correction, verified) |
| 5. New money-like instruments (stablecoins) | +76 (2024) | **+101** | **+2 YTD — stalled** | **measured 29 Aug (D6): outstanding $309bn; bill/repo-bound by statute; TBAC ">$120bn" of bills held; the 2024–25 flow was ~4–5% of net issuance** |

**And the collateral loop closes the circuit:** the deficits of §2 issue the very collateral (N3: hedge-fund
sources ×3 since 2017) that is levered through repo (MMF cash via FICC) to buy the next deficit, while the
corporate bond issuance of §4 funds the equity bid. Nothing here requires the system to find pre-existing
savings; it requires the engines of lines 2–3 to keep running. **The fragility question this reframes:**
what stops line 2 — bank capital, examiners, or a credit event in private credit — is now the sharpest
"what breaks it" candidate in the whole programme.

## 6. What v1 does not close

- ~~**Stablecoins (engine 5)** — D6 parcel, queued.~~ **Closed 29 Aug** — see the row above and `2026-08-29-D6-Stablecoins-Fifth-Cash-Pool.md`. The 2026 stall completes the pattern: every private engine plateaued the year the Fed returned.
- **Who exactly is behind "households +$276bn"** — in Z.1 that cell contains hedge funds and the residual;
  Form PF says hedge-fund cash Treasuries reached $2trn (OFR, 19 Aug 2026) — the split is partly derivable.
- **The NDFI loan book's composition** — H.8 gives one line; the FR Y-14/call-report split (private credit
  vs REITs vs BDCs vs warehouse) exists in Fed research (e.g., FEDS work on bank–nonbank links) — locate.
- **2026Q1 equity issuance turning positive (+$31bn)** — one quarter; if buybacks are rolling over while
  the credit machine runs, the equity bid changes character. Watch at the Z.1 Q2 release (~11 Sep).
- **RoW composition** — official vs private, and the Cayman correction applied quantitatively.

---

## 7. Adjudication of the adversarial review (Parcel N2cR) — 30 Aug

*Return at `_research/N2cR_Funding_Closure_Review_Return.md` (retrieved from the agent VM via Downloads).
Verification: three agents + a local recompute from our own vintaged series — **25 of 25 citations verified,
several verbatim**, including the Fed's H.8 Notes, F51.1.t, the July MPR, H.4.1 and DTS endpoints, FDIC,
the May 2026 FSR, BIS QR Dec-2025, and the IMF Fiscal Monitor. The second consecutive fully-clean Grok
judging return. Registered: C-063 (Fed ratio), C-064 (the nondepository loan flow), C-065 (the equity-buyer claim).*

### 7.1 What died, and what stands in its place

**Conclusion 3 (NDFI engine) — broken in size, alive in substance.** $400.8bn of 2025's +$625bn was
reclassification into the line (five dated notes, verified). The corrected picture: **organic growth
≤ ~$224bn in 2025, i.e. a steady ~$100–220bn/yr engine since 2023, on a real $2.0trn stock** — genuine and
large, but no explosion, and no valid comparison to the ABCP stock (category error, retracted). Composition
(FDIC, verified): 57% credit intermediaries, 24% capital-call-secured PE lines, **42.9% of commitments
($987bn) undrawn** — a revolver-heavy liquidity backstop as much as a credit firehose. The May 2026 FSR's
own $261bn vendor reclassification shows the commitment series has the same measurement problem.

**Conclusion 4 (equities) — broken as worded.** F51.1.t, reproduced exactly: the biggest net *purchasers*
were households (+985/+864), ETFs (+840/+959) and the rest of the world (+185/**+644** in 2025); the
corporate sector was a net *seller as holder* even while retiring stock. What survives, restated honestly:
**buybacks are a large, debt-funded structural bid (net issues −$304 to −$611bn/yr), and they shrink the
float — but they are not "the only buyer", and the identity does not set the price.** Symmetric caveat kept:
the household row is the Z.1 residual (it contains domestic hedge funds and measurement error, per the Fed's
own instrument notes), and F51.1.t layers ETF-share and underlying-stock purchases — so nobody, including
the reviewer, can name the ultimate equity financier from this table. The **foreign equity bid ($644bn in
2025, TIC June: $144.7bn of US equities in one month) is the genuinely under-weighted row in our original
account.**

**Conclusions 1/2/5 (regimes, exhaustion, monetization) — the causal narrative is retracted; the rows
stand.** The Fed's own FWTW page: the core accounts *"are not designed to reveal… From-Whom-to-Whom
relationships"* — an absorption table cannot say who funded whom, and my "engines" are accounting layers
that can double-count one financed position (bank loan → NDFI → Treasury → repo). The plateau observations
survive as series; the *inference* of exhausted private capacity does not (BIS: the swap-spread trade, upper
bound $631bn, drove hedge-fund Treasury growth after the basis trade stalled in early 2024 — activity
migrates across venues). On the Fed: C-063 — matched ratios 63.6% (→Jul) / 44.4% (→26 Aug), **falling** as
private buyers took the August wave; ~$160bn of it RMP; Jefferson's stance-neutrality position quoted and
archived. "Re-monetized" is retracted; what remains defensible: **the Fed stopped draining and became a
large, stance-neutral bill buyer while reserves rose $54bn — a necessary accommodation of its own balance
sheet, not demonstrated fiscal financing.**

### 7.2 The corrected answer to the principal's question

Who finances the deficits and the asset issuance? On verified evidence: **a broad private-domestic absorption
— the IMF's number is almost $5trn of US public debt taken by domestic private investors (funds, hedge funds,
NBFIs) since 2022 — intermediated through layers our accounts cannot causally separate: MMF rotation (2023),
foreign inflow (steady ~$0.5trn/yr in Treasuries plus a large and growing equity bid), leveraged relative-
value strategies migrating between basis and swap-spread trades, a steady ~$100–220bn/yr of bank credit to
nonbank intermediaries on a $2trn stock, and — in 2026 — a stance-neutral but balance-sheet-expanding Fed.**
The honest headline is not "the Fed is monetizing" or "banks are printing for the shadow system"; it is that
**every layer is leverage-intensive intermediation of a savings pool nobody can locate in the accounts — the
FWTW gap is the finding.** The two sharpest live questions this leaves: the foreign equity bid's persistence,
and what stops the NDFI revolvers ($987bn undrawn) from being drawn all at once.

### 7.3 Process

The review was run against a parcel that had itself been adversarially revised (residual row, recompute-the-
ratio, per-year equity flows) — and every one of those revisions is what made the attacks land cleanly.
Verification cost three agents and one local recompute; the review's UNCERTAIN section correctly pre-named
its own weakest joints. This is the judging lane working exactly as designed, twice in a row.

