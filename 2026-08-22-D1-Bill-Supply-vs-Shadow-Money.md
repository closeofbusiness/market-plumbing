# D1 — Bill supply versus shadow money, 2013–2026: the Triffin test run forwards

*22 August 2026. **Version 1 — every number below was pulled by us from the issuing source on
22 Aug 2026** (FiscalData MSPD Table 1; OFR MMF Monitor API, N-MFP based; FDIC BankFind API;
FRED mirrors of Fed H.4.1 / H.8 / CP release). Nothing here comes from an external model. Serves
**A12**. Hypothesis H1 carried from `2026-08-22-Parcel-D1-Scouting-Return.md` §4.3.*

---

## 0. The question, and the prediction being tested

Pozsar (IMF WP/11/190, 2011) argues shadow banking arose because institutional cash pools
outgrew the supply of short-term government-guaranteed instruments, and concludes that **Treasury
bill supply should be managed as a macroprudential tool** — more bills, less private shadow
money. His own table (`Pozsar_2011_IMF_WP11190…txt:500–524`) shows the "deficit of safe, liquid,
short-term products" closing from **$1.5trn (2007) to ~$0 (2009)** as short-term government
supply rose $1.65trn.

Since mid-2023 the US has run the experiment at scale. **Prediction under test: private shadow
money should have shrunk as bills surged.** Competing hypothesis **H1**: the surge was absorbed by
the Fed's ON RRP facility — a public-money buffer that did not exist in 2007 — and private money
was untouched.

## 1. Result in one paragraph

**The prediction fails; H1 holds on magnitudes; and the demand side grew faster than the supply
side.** From June 2023 to July 2026 bills rose **$2.52trn**. Over the same window the Fed's ON
RRP fell **$2.03trn** to effectively zero, money-market funds' holdings of Treasuries rose
**$2.21trn**, and MMFs' repo with the Fed fell **$1.90trn** — the cash-pool vehicle rotated
almost one-for-one out of the Fed facility into bills. **Every private money-like component we
can measure rose**: uninsured deposits +$1.04trn, large time deposits +$0.58trn, ABCP +$0.20trn,
MMF private-collateral repo +$0.10trn, financial CP flat. The four issuer-side private components
together went from **$10.2trn to $12.0trn (+18%)** while bills went up 56%. Over the long run,
2013→2025, bills rose **$5.0trn and the same private stack rose $5.0trn**. There is no crowd-out
visible at the aggregate level in either window.

## 2. Data — the long view, year-end, $bn

| Series (source) | 2013 | 2016 | 2019 | 2021 | 2022 | 2023 | 2024 | 2025 | Latest |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Treasury bills outstanding** (MSPD T.1, total) | 1,592 | 1,818 | 2,417 | 3,770 | 3,697 | 5,676 | 6,187 | 6,547 | **6,989** Jul-26 |
| Fed ON RRP (`RRPONTSYD`) | 198 | 468 | 64 | 1,905 | 2,554 | 1,018 | 473 | 106 | **0.2** 21-Aug-26 |
| Reserve balances (`WRESBAL`) | 2,474 | 1,953 | 1,652 | 4,116 | 3,018 | 3,446 | 3,247 | 2,957 | 2,935 Aug-26 |
| MMF total investments (OFR) | 3,050 | 2,923 | 4,016 | 5,229 | 5,212 | 6,401 | 7,253 | 8,305 | **8,412** Jul-26 |
| — of which Treasuries | 547 | 851 | 1,123 | 1,822 | 1,067 | 2,270 | 2,995 | 3,518 | 3,453 |
| — repo **with the Fed** | 163 | 403 | 47 | 1,740 | 2,340 | 969 | 382 | 73 | **7** Jun-26 |
| — repo cleared at **FICC** (sponsored) | — | 0 | 272 | 97 | 110 | 447 | 865 | **1,298** | 1,076 |
| — repo backed by **other (private) assets** | 79 | 37 | 61 | 53 | 50 | 69 | 106 | 143 | 169 |
| — bank-related assets (CP/CDs/TDs) | 836 | 270 | 522 | 302 | 362 | 483 | 465 | 452 | 467 |
| **Uninsured deposits** (FDIC `DEPUNINS`, all insts) | 4,071 | 5,067 | 5,874 | **8,804** | 8,169 | 7,224 | 7,607 | 8,138 | **8,373** Mar-26 |
| Large time deposits (H.8 NSA) | 1,591 | 1,494 | 1,818 | 1,394 | 1,649 | 2,225 | 2,342 | 2,429 | 2,538 Jul-26 |
| Financial CP (`FINCP`) | 609 | 451 | 566 | 580 | 683 | 683 | 558 | 584 | 623 Aug-26 |
| ABCP (`ABCOMP`) | 255 | 240 | 247 | 269 | 293 | 304 | 336 | 421 | **488** Aug-26 |

*MMF rows are the MMF's **asset** side; deposit, CP and bills rows are the **issuer** side. They
are never summed across that line — a CD held by an MMF is in both "bank-related assets" and
"large time deposits" (C-042).*

## 3. The window: June 2023 → latest, $bn change

| | Jun-23 | Latest | Δ |
|---|---:|---:|---:|
| **Bills outstanding** | 4,467 | 6,989 (Jul-26) | **+2,522** |
| **ON RRP** | 2,034 | 0.2 (Aug-26) | **−2,034** |
| MMF repo with the Fed | 1,906 | 7 (Jun-26) | **−1,899** |
| MMF Treasuries | 1,244 | 3,453 (Jul-26) | **+2,209** |
| MMF total | 5,919 | 8,412 | **+2,493** |
| MMF Treasury repo, all counterparties | 2,613 | 1,798 | −815 |
| → implied Treasury repo with *non-Fed* counterparties | 707 | 1,791 | **+1,084** |
| MMF FICC-cleared (sponsored) repo | 335 | 1,076 | **+741** |
| MMF agency repo / agency securities | 553 / 755 | 958 / 1,215 | +405 / +460 |
| MMF private-collateral repo | 67 | 169 | +102 |
| Uninsured deposits | 7,330 | 8,373 (Mar-26) | **+1,043** |
| Large time deposits | 1,963 | 2,538 (Jul-26) | **+575** |
| Financial CP | 597 | 623 | +26 |
| ABCP | 289 | 488 | **+199** |
| Reserve balances | 3,172 | 2,935 | −237 |
| Treasury General Account (`WTREGEN`) | 391 | 954 | +563 |
| Foreign-official RRP (`WLRRAFOIAL`) | 327 | 373 | +47 |

**The plumbing arithmetic closes.** Bills +2.52trn ≈ ON RRP −2.03trn + reserves −0.24trn +
TGA +0.56trn drawdown of private balances, with MMFs as the vehicle: their Fed repo −1.90trn and
Treasuries +2.21trn. Pozsar's lever pulled hard and hit **the Fed's own liability**, not private
money.

## 4. Verdicts

- **H1 — "bills displaced ON RRP, not private money": CONFIRMED on magnitudes.** The ON RRP is
  gone ($0.2bn); MMFs rotated $1.9trn of Fed repo into $2.2trn of bills.
- **Pozsar's prediction — "more bills, less private shadow money": REJECTED for 2023–26.** Every
  private component rose; the issuer-side stack +$1.8trn. *And* rejected in the long run: 2013–25
  bills +$5.0trn, private stack +$5.0trn.
- **The opposing literature's prediction is the one that held.** Nagel's point — the near-money
  premium is governed by the *level of rates* (opportunity cost of holding money), not by supply
  quantities — fits a window in which policy rates sat at 4–5% and private near-money expanded
  regardless of record bill issuance. *(Nagel 2016, QJE — the one L6 citation that verified.)*
- **Pozsar's in-sample 2007–09 closing is confounded and should not be used as a clean
  precedent.** Bills rose $0.79trn (1,004→1,793) while ABCP fell $0.74trn from its Aug-2007 peak
  (1,226→487 by YE2009) and financial CP $0.28trn. That private contraction was a **run**, not a
  substitution into bills. Supply and crowd-out moved together, and the table cannot separate
  them.

## 5. What this says about the nexus (A12)

1. **The demand side outgrew everything.** MMF assets — the cash-pool vehicle Pozsar's taxonomy
   is built around — rose **$2.5trn in three years and $5.3trn since 2013**. Reverse maturity
   transformation (WP/11/289 §II) predicts exactly this: institutional money demand scales with
   the asset-management complex, not with policy. **D3 is promoted from candidate to next.**
2. **A public-money buffer absorbed the shock that in 2007 had to be absorbed privately.** The
   ON RRP did not exist in Pozsar's sample. From here it is **zero**, so any further bill surge
   meets private money and cash-pool growth directly — the cleaner test is *ahead of us*, not
   behind.
3. **Where the cash-pool money went instead of the Fed: to dealers and levered funds.** MMF
   Treasury repo with non-Fed counterparties **+$1.08trn**, of which **FICC-sponsored repo +$0.74trn
   to a $1.30trn peak**. That is cash pools funding the dealer–hedge-fund complex through a
   cleared conduit — **the money leg and the collateral leg touching in one instrument.** It is
   also the strongest candidate yet for the E2 "missing channel" that two external passes failed
   to name: sponsored repo is not on our nine-channel list as a channel in its own right. **Flagged
   as D8, not folded.**
4. **Uninsured deposits are the largest private component and the most misread.** $8.8trn at
   YE2021 → $7.2trn trough (mid-2024, post-SVB) → **$8.4trn at 2026Q1**. Measured from the June-2023
   start the window shows +$1.0trn; measured from YE2021 it shows −$0.4trn. **State the base.** The
   omnibus return's "~$7.1trn at 2025Q4" is wrong — FDIC says $8.14trn (C-052).

## 6. What v1 does not do — stated, with the size of each hole

| Gap | Why it matters | Size / status |
|---|---|---|
| **Foreign-official bills not netted out** (Pozsar's TIC term) | His 2009 netting was 17.5% of supply | Today foreign-official holdings of *bills* are a small share of a $7trn stock; TIC short-term series not yet located. Bound, not fatal |
| **Uninsured deposits are total, not demand-only** | Pozsar's private shadow money is par-on-demand | FDIC RC-O reports uninsured in total; demand split needs an RC-E heuristic. Direction of result unaffected |
| **Prime vs government MMF split not shown** | The rotation inside MMFs is the mechanism | OFR API gives portfolio composition, not fund type; ICI blocked our fetch. Composition already tells the story |
| **Primary-dealer repo by collateral ends Dec-2021** in the OFR feed | Issuer-side private repo post-2021 | Use FR 2004 directly, or NCCBR. MMF-side private repo (+$102bn) is the lower bound used |
| **Cash-pool demand side not rebuilt** (S3/S5 do not exist) | Pozsar's deficit needs both sides | We tested the *object* (private money) instead of the *deficit*. The deficit cannot be reconstructed from public data in 2026 — that is itself a D1 finding |
| **Short coupons ≤1yr remaining not added to bills** | Pozsar's supply term | ~$180–200bn in his sample; second-order |
| **Gross/net** | C-042 | MMF-side and issuer-side shown separately; never summed |

## 7. Flagged for separate investigation (N5 — flag, do not fold)

- **D8. FICC-sponsored repo as a nexus channel in its own right.** +$741bn of MMF money into a
  cleared conduit to dealers/hedge funds during a bill surge. Is this the missing channel?
- **D3, promoted.** Cash-pool growth vs AUM / overlay / sec-lending growth — the demand-side
  engine, now with a measured $5.3trn MMF expansion to explain.
- **The counterfactual.** What would the private stack have done had the ON RRP not existed?
  The 2007–09 episode is confounded; the next bill surge will not be.
- **Refresh cadence.** Re-pull the table quarterly — 15 minutes from the same four endpoints.


---

## 9. Amendment, 23 Aug 2026 — the Fed is a bill buyer again, and ABCP has a mechanism

- **Fed SOMA T-bill holdings** (FRED `WSHOBL`): $272bn (Jun-23) → $234bn (YE2025) → **$538bn
  (19 Aug 2026)**. Over the 2023–25 window the Fed was a small net *seller* of bills (−$38bn), so
  §3–§4 stand as written. ~~**In 2026 the Fed's reserve management purchases absorbed ~$304bn of
  bills against ~$442bn of net issuance** — ~69%.~~ **[C-063, 30 Aug: window-mismatched ratio (numerator to 19 Aug, denominator to 31 Jul). Matched endpoints: 63.6% Dec-31→end-Jul, 44.4% →26 Aug and falling; only ~$160bn of ~$250bn of bill buying through early July was RMP (July MPR), the rest agency-principal reinvestment.]** §5.2's "any further bill absorption must come
  from private money or cash-pool growth" is **wrong for 2026**: net bill supply to private cash
  pools this year is ~$140bn. Add SOMA bills to the netting terms in §6 alongside foreign official.
- **ABCP's +$199bn now has a mechanism**: non-bank-sponsored conduits funding prime-brokerage
  equity margin, per the FT/JPMorgan account verified in part at
  `2026-08-23-FT-Harvest-ABCP-Conduits-And-Equity-Repo.md`. It is private shadow money created to
  fund leverage against equity market value.
