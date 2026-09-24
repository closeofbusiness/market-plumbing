# D3 — Does institutional money demand scale with the asset-management complex?

*23 August 2026. **Version 1.2 — every figure pulled by us** from the Federal Reserve Z.1 CSV bundle
(11 Jun 2026 vintage), FRED mirrors of Z.1 and H.6, and — from v1.1 — the **OFR Hedge Fund Monitor
API** (Form PF aggregates, 4 Jun 2026 vintage), on 22–23 Aug. Gemini's D3 scouting return was located
on the Dropbox share root on 23 Aug (`_research/D3_Scouting_Return_gemini_ondisk.md`) and is
adjudicated in §7; the hedge-fund leg it pointed to is measured in §8; the CCP-margin leg is measured in §9
(evening, from the N3 return's verification). Only the securities-lending leg remains (SLATE, 29 Mar 2027). Serves **A12**, downstream of D1.*

---

## 0. The hypothesis

WP/11/289 §II: institutional money demand is a by-product of **reverse maturity transformation** —
asset managers holding long money must keep a slice short for mandates, derivatives overlays and
securities lending. If so, cash-pool demand should scale with the **size and structure of the
asset-management complex**, not with monetary policy. D1 measured US money-market fund assets
rising $3.0trn → $8.4trn (2013→2026). D3 asks: **how much of that is structure, and how much is
something else?**

## 1. Result in one paragraph

**Structure explains the level and the 2013–21 trend; it does not explain 2021–26.** From 2013 to
2021 the asset-management complex (mutual funds, ETFs, closed-end funds, pensions, life and P&C
insurers) grew **+66%** and money-market funds **+71%** — institutional MMFs **+80%** — so cash-pool
vehicles scaled with the complex, slightly faster. From 2021 to 2026Q1 the complex grew **+16%**
and MMFs **+59%**: retail MMFs **+122%**, institutional **+37%**. Corporate liquid assets, the
category-2 cash pool, track corporate balance sheets exactly — **22–24% of non-financial corporate
financial assets in every year since 2013** — and grew +16% since 2021, the same as the complex.
**The post-2021 surge is therefore not reverse maturity transformation. It is retail households
chasing 5% yields and, on the institutional side, ~$1.3trn above the structural norm that lines up
with the post-2023 flight from uninsured deposits** — a substitution between money forms, not
demand growth. Rates, again (Nagel), on top of structure.

## 2. The table — cash-pool vehicles against the asset-management complex, $bn

| | 2013 | 2016 | 2019 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026Q1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| Mutual funds (FL654090000) | 12,333 | 13,616 | 17,660 | 22,209 | 17,333 | 19,600 | 21,685 | 23,635 | 23,026 |
| ETFs (FL564090005) | 1,675 | 2,525 | 4,396 | 7,191 | 6,477 | 8,086 | 10,305 | 13,373 | 13,552 |
| Closed-end funds (FL624090005) | 1,591 | 1,957 | 2,323 | 2,605 | 2,409 | 2,611 | 2,900 | 3,443 | 3,443* |
| Pension funds, total (FL594090005) | 19,401 | 21,238 | 24,462 | 27,512 | 24,475 | 26,513 | 28,171 | 29,900 | 29,641 |
| Life insurers (FL544090005) | 6,702 | 7,420 | 8,718 | 9,957 | 8,947 | 9,713 | 10,326 | 11,039 | 10,975 |
| P&C insurers (FL514090005) | 2,064 | 2,224 | 2,688 | 3,100 | 2,980 | 3,299 | 3,519 | 3,823 | 3,816 |
| **Asset-management complex (sum)** | **43,766** | **48,980** | **60,247** | **72,574** | **62,621** | **69,822** | **76,906** | **85,213** | **84,453** |
| **MMF total financial assets** (FL634090005) | 3,047 | 2,955 | 4,002 | 5,205 | 5,223 | 6,358 | 7,243 | 8,190 | 8,290 |
| — retail MMF (H.6 `WRMFNS`, YE) | 910 | 947 | 1,313 | 1,361 | 1,614 | 2,239 | 2,647 | 2,998 | 3,018 |
| — institutional MMF (residual) | 2,137 | 2,008 | 2,689 | 3,844 | 3,609 | 4,119 | 4,596 | 5,192 | 5,272 |
| **MMF / complex** | 6.96% | 6.03% | 6.64% | 7.17% | 8.34% | 9.11% | 9.42% | 9.61% | **9.82%** |
| Institutional MMF / complex | 4.88% | 4.10% | 4.46% | 5.30% | 5.76% | 5.90% | 5.98% | 6.09% | **6.24%** |
| NFC liquid assets (FL104001005) | 3,352 | 4,014 | 5,241 | 7,307 | 6,364 | 7,137 | 7,899 | 8,749 | 8,506 |
| NFC liquid / NFC total financial assets | 21.7% | — | 21.8% | — | — | 22.7% | — | 23.9% | 22.5% |

*\*2025Q4 carried. Z.1 "total financial assets" per sector; MMFs excluded from the complex because
they are the object. Retail MMF from H.6 (the institutional series was discontinued in 2021, so
institutional is a residual). NFC = sector 10, liquid assets = checkable deposits + time and
savings deposits + MMF shares + repo + CP + Treasuries + agency + munis.*

## 3. Growth, two windows

| | Complex | MMF total | Institutional MMF | Retail MMF | NFC liquid |
|---|---:|---:|---:|---:|---:|
| **2013 → 2021** | +66% | +71% | **+80%** | +50% | +118% |
| **2021 → 2026Q1** | +16% | +59% | +37% | **+122%** | +16% |

**Counterfactual on the structural ratio.** Holding MMF/complex at its 2013–21 mean (6.70%),
structural MMF assets at 2026Q1 would be **$5.66trn** against **$8.29trn** actual — **$2.63trn
"excess."** On the institutional ratio alone (4.69%): structural **$3.96trn** vs **$5.27trn** actual
— **$1.32trn excess**. The rest of the excess (~$1.3trn) is retail.

## 4. Reading it

1. **Reverse maturity transformation is the right account of the *level* and of the pre-2021
   trend.** Institutional cash demand ran at ~4–5% of the complex for eight years, and corporate
   cash ran at ~22% of corporate financial assets throughout. Those are structural ratios.
2. **The 2021–26 surge is not structural.** Retail MMFs more than doubled while the complex grew
   16% — households moving deposits to 5% money funds, the deposit-beta story. Institutional MMFs
   rose ~$1.3trn above the norm, over exactly the window in which **uninsured deposits fell from
   $8.8trn (YE2021) to $7.2trn (mid-2024)** (D1 §2). That is one money form replacing another,
   not new demand from asset-management growth.
3. **So D1 and D3 say the same thing from two sides.** Bill supply did not shrink private money
   (D1); asset-management growth did not generate the post-2021 cash surge (D3); **the level of
   rates did both** — it pulled retail and institutional cash into government MMFs and out of
   deposits, and MMFs then rotated from the Fed's RRP into bills. Nagel's account, twice.
4. **For the nexus:** Pozsar's demand-side engine is real and quiet — it sets the baseline. The
   *variation* that matters for stability is policy-driven and fast. A reverse-maturity-
   transformation story explains why cash pools exist at $5trn; it does not explain why they are
   $8trn today, and it will not predict where they go when rates fall.

## 5. What v1 does not measure — the two legs Gemini located

| Leg | Status |
|---|---|
| **Derivatives-overlay margin demand** | **MEASURED 23 Aug evening — §9.** ~~FIA's CCP Tracker: "member dashboard, not a pullable feed"~~ **wrong (C-056): free, public JSON API, PQD 6.1.1 for 15 CCPs from 2015Q3.** Pulled; `bin/pull_series.py --only fia`. All eleven CCPs' own 2026Q1 files also on disk (`data/vintages/ccp_pqd_2026Q1/`). ISDA non-cleared survey still not pulled (annual PDF) |
| **Securities-lending cash collateral** | **Verified by us, 23 Aug:** SEC extended Rule 10c-1a — FINRA SLATE reporting to **28 Sep 2026**, public dissemination to **29 Mar 2027** (Sidley, Dechert). No official US on-loan / cash-collateral series exists until then; ISLA semi-annual is the open aggregate; RMA's survey is no longer public. Calendar row added |
| **Hedge-fund unencumbered cash** | **MEASURED 23 Aug — §8.** OFR Hedge Fund Monitor API (Form PF Q33/Q9 aggregates). ~$0.7trn; ratio to NAV fell 21% → 14% since 2013. Not a driver |
| **Gemini's full D3 return** | **FOUND 23 Aug** at the Dropbox share root (`smb://192.168.178.156/Dropbox/D3_Scouting_Return.md`, 33 KB, written 09:39), copied to `_research/D3_Scouting_Return_gemini_ondisk.md` (sha256 3dfa187b…). **Adjudicated in §7** (C-054). Pasted summary kept at `_research/D3_Scouting_Return_gemini_summary_pasted.md` |

## 6. Flagged (N5)

- **The rate-down test.** D1 and D3 both attribute the 2021–26 surge to the level of rates. When
  policy rates fall materially, structural MMF demand predicts ~$5.7–6trn, not $8.3trn. That is a
  falsifiable prediction with a number. **Pre-register it.**
- **Margin as a structural driver** — the unmeasured leg most likely to move the structural ratio.
- **Institutional ≠ cash pools.** "Institutional MMF" includes corporate treasurers and sec-lending
  reinvestment but also sweep vehicles; the residual construction is crude. A cleaner split needs
  N-MFP3 shareholder-type fields.

---

## 7. Gemini's D3 scouting return — adjudicated (23 Aug)

*File: `_research/D3_Scouting_Return_gemini_ondisk.md`, 4,576 words, ten IDs (M1–M3, SL1–SL2,
AM1–AM3, L1–L2), written 22 Aug 09:39 to the share root. Every row checked at the reference on
23 Aug. Register entry C-054.*

**Two defects that apply to the whole file before any row is read.** (i) It was written through a
shell that expanded `$1`, `$2`… as empty positional parameters, so **every dollar figure is mangled**
("$1.3trn" → ".3trn"; "$20trn–$25trn" → "trn–trn"). The "(seen, unverified — re-pull)" rule had
already kept those values out of the record; now they are unreadable as well. (ii) Its self-audit
ticks *"Every EXISTS row has a URL I opened / verified"* — two of the URLs 404 (the BoE LDI paper,
the SFOS page) and **every one of the five DOIs resolves to an unrelated paper.** C-051 holds: the
checklist is completeness, not truth.

| ID | Verdict on the row | What survives |
|---|---|---|
| **M1** CCP initial margin | Publishers right: FIA CCP Tracker exists (HTTP 200; member dashboard, not a feed), CPMI-IOSCO d125 is the PQD standard (verified), Clarus commercial. No official continuous aggregate — correct, and matches our own reading | Retrieval path. Not pulled |
| **M2** ISDA margin survey | Exists, annual, YE2016–YE2025 — consistent with what we know; values mangled | Retrieval path |
| **M3** collateral composition | PQD 6.2 / ISDA composition tables / SCOOS — real sources; the cash-vs-securities split claims are unverified | Retrieval path |
| **SL1** sec-lending stock | SLATE dates **correct** (28 Sep 2026 / 29 Mar 2027 — we verified independently before the file arrived); ISLA semi-annual, RMA discontinued, OFR WP 15-17 real | All usable |
| **SL2** cash-collateral reinvestment | "No open continuous series" — matches our own negative; N-PORT Item B.4 pointer is real | Usable as a negative |
| **AM1** complex size | Z.1 / ICI / SEC PFS tables — right publishers; Z.1 table numbers not checked (we use series codes, §2); values mangled | Nothing we did not already have |
| **AM2** fund cash buffers | ICI liquid-asset ratio (real, monthly), SEC Registered Fund Statistics (real) | Retrieval path for a future fund-buffer leg |
| **AM3** hedge-fund unencumbered cash | SEC PFS Table 33 + **OFR Hedge Fund Monitor** — right; the return **did not say the monitor has an open API** (`data.financialresearch.gov/hf/v1/…`, 497 mnemonics). Found by us 23 Aug and pulled — §8 | **The one row that changed what we know** |
| **L1** literature (12 items) | **9 of 12 carry constructed identifiers.** All five DOIs wrong (Graham–Leary → Gârleanu–Pedersen; Begenau–Palazzo → Ranaldo–Somogyi; Chernenko–Sunderam → Bottazzi et al.; "Jiang–Li–Sun" → Barber et al.; Ma–Xiao–Zeng → Van Doornik et al.). Journal/volume/pages constructed for Graham–Leary (real: RFS 31(11) 4288–4344, 2018), Begenau–Palazzo (real: *Firm Selection and Corporate Cash Holdings*, JFE 139(3) 697–718, 2021), Chernenko–Sunderam (real: NBER w22391, 2016, unpublished), "Jiang–Li–Sun JF 2021" (nearest real: Jiang–Li–Wang, JFQA 56(5) 1622–1652). "CGFS Papers No 69, *Derivatives Markets, Central Clearing and Liquidity*" — **No 69 is a housing-macroprudential paper.** "BoE Financial Stability Paper No 51 (LDI)" — URL 404, existence not established. d'Avernas–Vandeweyer titled "*Treasury Yields and Institutional Cash Pools*" — real paper is *Treasury Bill Shortages and the Pricing of Short-Term Assets*, JF 79(6) 4083–4141, 2024. Pozsar's cash-pools paper cited as **WP/11/289** — it is **WP/11/190**; 289 is Pozsar–Singh (the C-044 confusion, reversed). **Correct:** Ma–Xiao–Zeng RFS 35(10) 4674–4711; BCBS-CPMI-IOSCO d537 (2022); OFR WP 15-17; Pozsar FMII 22(5) 283–318 (2013) | The *papers* mostly exist and are the right literature; **no identifier from this file may be cited** — every citation re-derived from Crossref before use |
| **L2** direct test exists? | "DOES NOT EXIST" — four searches listed; consistent with our own search. The drivers it names (DSS 2017 deposits channel; Xiao 2020) are the right comparison set | Usable as a negative; **D3 is an open gap in the literature, which is the point** |
| §6 unrequested | Fed SFOS (real, at `federalreserve.gov/data/sfos/sfos.htm` — the URL given 404s), ECB SESFOD, CFTC TFF, ESMA derivatives report — all real | Retrieval paths |

**Net.** One row changed what we know (AM3, via a pointer the return did not itself make
explicit), three negatives are confirmed, and the literature list is the right literature wearing
the wrong identifiers. Same shape as C-050: retrieval right, construction in the identifiers —
and this time the parcel had *not* asked for identifiers (C-051 rule 4); the model supplied
them anyway. **Rule from here (C-054): identifiers that arrive unasked are treated as absent.**

## 8. The hedge-fund leg, measured — the OFR Hedge Fund Monitor (v1.1, 23 Aug)

*Source: `data.financialresearch.gov/hf/v1/series/full?mnemonic=…` — aggregated Form PF responses
of **Qualifying Hedge Funds** (≥$500m NAV, large advisers), quarterly, 2013Q1–2026Q1, OFR vintage
4 Jun 2026. Re-pull: `bin/pull_series.py --only ofr_hf`. Definitions: unencumbered cash = Form PF
Q33 over Q9 (NAV-weighted ratio per strategy × strategy NAV, summed over nine strategies);
collateral posted = Q43 — **"cash collateral" there includes Treasuries and agencies**, so it is
cash-like, not cash. Raw pull and derived table: `data/vintages/ofr_hf/`.*

### 8.1 Unencumbered cash — not a driver

| $bn, year-end | 2013 | 2016 | 2019 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026Q1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| QHF net assets | 2,388 | 2,733 | 3,221 | 4,182 | 3,778 | 3,962 | 4,211 | 4,835 | 4,918 |
| **Unencumbered cash** (Σ ratio × NAV) | **500** | 554 | 470 | **522** | 588 | 501 | 518 | 631 | **702** |
| — as % of NAV | 20.9 | 20.3 | 14.6 | 12.5 | 15.6 | 12.6 | 12.3 | 13.0 | 14.3 |

Hedge-fund cash is **~$0.7trn — 8% of MMF assets** — and it grew **+4% 2013→21** while QHF NAV
grew +75%, then **+$180bn (+34%) 2021→26Q1** while MMFs grew +$3.1trn. The ratio *fell* from
21% to 14%: funds hold less cash per dollar of net assets than they did. Managed-futures (51%)
and macro (36%) funds carry the high ratios; equity (15%), credit (5%), event (5%) the low ones.
**Adds to §4: the third institutional category after asset managers and corporates is also not the
post-2021 source.** The structural-ratio counterfactual in §3 stands.

### 8.2 What did double: collateral posted — the collateral leg, in one table

| $bn, year-end | 2013 | 2016 | 2019 | 2021 | 2023 | 2024 | 2025 | 2026Q1 | 2021→26Q1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **Collateral posted, total** (Q43) | 2,033 | 2,375 | 3,582 | **4,384** | 5,151 | 6,226 | 8,371 | **8,211** | **+87%** |
| — cash-like (cash + UST + agency) | 633 | 856 | 1,220 | 1,442 | 1,711 | 2,169 | 2,872 | 2,921 | +103% |
| — securities | 1,366 | 1,459 | 2,244 | 2,688 | 3,200 | 3,756 | 5,174 | 4,924 | +83% |
| **Secured borrowing, total** | 1,699 | 2,060 | 3,165 | **3,760** | 4,645 | 5,596 | 7,421 | **7,245** | **+93%** |
| — repo borrowing | 508 | 675 | 1,302 | 1,151 | 2,009 | 2,497 | 3,379 | **3,243** | **+182%** |
| — prime-brokerage borrowing | 926 | 1,090 | 1,413 | 1,975 | 2,088 | 2,500 | 3,259 | 3,221 | +63% |
| — other secured | 265 | 295 | 450 | 634 | 548 | 599 | 783 | 781 | +23% |
| Collateral posted − secured borrowing | 334 | 315 | 417 | 624 | 506 | 630 | 950 | **966** | +55% |
| Long UST exposure (cash + derivs) | 630 | 776 | 1,325 | 1,001 | 1,609 | 1,920 | 2,465 | 2,348 | +135% |
| Short UST exposure | 275 | 364 | 864 | 759 | 1,259 | 1,447 | 1,645 | 1,567 | +106% |
| Gross assets | 4,349 | 5,208 | 6,702 | 8,323 | 9,209 | 10,256 | 12,570 | 12,626 | +52% |

**Reading.** Qualifying hedge funds had **$8.2trn of collateral posted at 2026Q1, up from $4.4trn
at YE2021**, and the rise tracks secured borrowing almost one-for-one: repo borrowing ×2.8 to
$3.2trn, prime-brokerage borrowing ×1.6 to $3.2trn. The residual — collateral posted in excess of
secured borrowing, the nearest thing in Form PF to derivatives margin plus haircuts — is ~$1trn
and grew +55%, roughly with gross assets. **So the doubling is the basis trade and prime-brokerage
leverage, not overlay margin.** Long Treasury exposure $1.0trn → $2.3trn against short $0.8trn →
$1.6trn over the same window.

**For the nexus, this is the other end of D8's pipe.** MMF repo cleared at FICC rose $335bn →
$1,298bn (Jun-23 → Dec-25, D8); hedge-fund repo borrowing rose $1.2trn → $3.2trn. Cash pools lend
to FICC-sponsored dealers; dealers lend to hedge funds against Treasuries; hedge funds post the
Treasuries back. Money leg and collateral leg in one chain, measurable at both ends from open data
— the interlock of §1.0 as an instance, not a diagram. **Flagged, not folded: D10 in
RESEARCH_STATE §5.** Caveats: QHF only; Form PF aggregates are gross and self-reported; the
collateral-minus-borrowing residual is a construction, not a reported margin figure — the CCP PQD
leg (§5) is still the proper measurement.

### 8.3 What this changes in §1 and §4

Nothing in the verdict — it strengthens it. The three institutional holders of cash Pozsar named
(asset managers via reverse maturity transformation, corporates, and the leveraged complex) have now
each been measured against the 2021–26 surge and none of them scales with it. What *did* scale
since 2021 is the **collateral** side of the same institutions: $3.8trn more posted. The nexus
moved on the collateral leg while the money leg moved on rates.

## 9. The margin leg, measured — FIA CCP Tracker API (v1.2, 23 Aug evening)

*Source: `fiadataapi.azurewebsites.net/api/Data/GetInitialMargin` (public key embedded in fia.org/fia/initial-margin-combined),
PQD item 6.1.1 initial margin required, house net + client gross, USD, 15 derivatives CCPs, 43 quarters. Cross-checked
against CME's own 2026Q1 disclosure file (identical). Full adjudication and the CCP file inventory:
`2026-08-23-Parcel-N3-Collateral-Return.md` §2.1 / §3. Re-pull `bin/pull_series.py --only fia`. My afternoon claim that
the tracker was a member dashboard is dead — C-056.*

| $bn | 2015Q3 | 2016 | 2019 | 2021 | 2022 | 2023 | 2024 | 2025 | 2026Q1 |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| **CCP initial margin required, 15 CCPs** | 365 | 424 | 548 | **757** | 835 | 836 | 836 | 968 | **1,071** |
| Growth vs the §2 table | | | | 2016→21 **+79%** (complex +48%, MMF +76%) | | | | | 2021→26Q1 **+41%** (complex +16%, MMF +59%) |

**Reading.** Margin has outgrown the asset-management complex in both windows, so it *is* a second structural
driver in the sense §5 asked — but the post-2021 increment is **$314bn against a $3.1trn MMF increment**, and
what is posted is not mainly cash-pool money: CME's 6.2 for 2026Q1 (Base, $311.8bn held post-haircut) is 39%
cash at the central bank, 5% cash at commercial banks, **42% domestic sovereign bonds**, the rest other
sovereigns, gold, equities, corporates. FICC's Treasury-repo clearing fund ($66.5bn required, 2026Q1) is
outside the 15 and small. **The §1 verdict stands: the surge is rate-driven; margin is real, faster than AUM,
and an order of magnitude too small.** Remaining unmeasured: securities-lending cash collateral (SLATE) and
non-cleared margin (ISDA survey, annual PDF).

