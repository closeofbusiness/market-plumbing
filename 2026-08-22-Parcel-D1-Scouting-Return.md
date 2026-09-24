# Parcel D1 return — bill supply vs cash-pool demand, adjudicated

*22 August 2026. Raw return preserved verbatim at
`_research/D1_Scouting_Return_gemini_ondisk.md` (Gemini's own file, written into the project root and moved). **The skeleton-and-audit format delivered
completeness — 26 of 26 rows present — and did nothing for truthfulness: the self-audit ticked
"no reference in this file was constructed rather than found" over at least five constructed
references.** Read §1 for what is usable and §4 for the two things that actually move D1.*

---

## 1. Scorecard, by section

| Section | Usable | Defective | Net |
|---|---|---|---|
| **S — series** | Issuers, publications and tables are right throughout; the structural negatives (S3 no direct measure, S5 no aggregate, S11 uninsured×demand not separable) are correct and valuable | FRED series IDs **~50% wrong** (§2); two real IDs mis-described; every "value seen" off, one by ~$300bn (§2) | **Good map, bad coordinates** — use the tables, re-derive every ID |
| **L — literature** | L1 Sunderam, L3 Carlson et al., L4 GHS, L6 Nagel: real, correctly placed | **L5 two of four citations fabricated; L6 one of two fabricated; L2 page numbers wrong** (§3) | The canonical pre-2016 literature is right; **the 2022–26 work — the item that mattered most — is not established by this return** |
| **P — primary precision** | P2 netting logic correct; P4 negative probably right | **P1 "verbatim quote" is a paraphrase in quotation marks with a page number; P3 mis-assigns T-bills to the wrong cell and cites a non-existent Table 1** (§3) | Do not use any P item without our own text |

## 2. Series — verified against FRED from a live browser session, 22 Aug

| Claimed ID | Exists? | Note |
|---|---|---|
| `COMPOUT`, `ABCOMP`, `FINCP` | ✅ | Correct; latest 2026-08-19 |
| `NONFINCP`, `DFFINCP`, `FORFINCP` | ❌ 404 | Do not exist |
| **`TBACMB`** (the headline bills series) | ❌ 404 | **Fabricated.** Bills outstanding must come from MSPD / SIFMA, or the correct FRED ID found by search |
| `WTREGEN` | ✅ but **wrong object** | This is the **Treasury General Account** ($954bn), offered as a bills series |
| `RRPONTSYD` | ✅ | Correct — and see the value below |
| `WLRRAL`, `WLRRAFOIAL` | ✅ | Total RRP ($374bn) and foreign-official RRP ($373bn) — these two are near-identical, which is itself a finding (below) |
| `H41RESPALFOPHAORRP_N.D` | ❌ 404 | Fabricated format; `WLRRAFOIAL` is the real foreign-pool series |
| `WRBAL` | ❌ 404 | `WRESBAL` (✅, $2.94trn) is the real one |
| `TOTRESNS`, `LTDACBM027NBOG` | ✅ | Correct |
| `FDHBFIN` | ✅ but **wrong object** | Total foreign holdings of federal debt, quarterly ($9.27trn) — not bills |

**Values "seen, unverified" versus FRED, same day:** ON RRP claimed ~$250–350bn → **FRED `RRPONTSYD` = $0.2bn on 2026-08-21**. Reserves claimed ~$3.20–3.35trn → `WRESBAL` $2.94trn. Large time deposits claimed ~$2.15–2.30trn → `LTDACBM027NBOG` $2.54trn. **Every number checked was wrong; the labelling discipline worked exactly as designed and is the only reason none of them entered the record.**

## 3. Fabrications, each checked individually

1. **L5 #1** — "Acharya, Chauhan, Rajan, Steffen, *Liquidity Dependence and the ON RRP Drain*, NBER WP 31688". **NBER 31688 is Chinoy, Nunn, Sequeira & Stantcheva, *Zero-sum Thinking and the Roots of US Political Differences*.** Title and number both wrong.
2. **L5 #2** — "Afonso, Cipriani, La Spada, *Banks' Intraday Liquidity, the ON RRP, and Reserve Distribution*, NY Fed SR 1068". **SR 1068 is Cattaneo, Crump & Wang, *Beta-Sorted Portfolios*.** The real pointer for these authors on this topic is the Liberty Street post *"Dropping Like a Stone: ON RRP Take-up in the Second Half of 2023"* (Dec 2023) — which the return did not cite.
3. **L6 #2** — "Gorton, Ross, Roussanov (2022), *The Moneyness of Private Claims and Information Insensitivity*, JFE 144(3)". **The real paper is Gorton, Ross & Ross, *Making Money*, NBER w29710, forthcoming J. Finance.** Wrong third author, wrong title, wrong journal.
4. **L2** — KVJ 2015 given as JFE 118(3) **471–500**; actual **571–600**. Small, but it is the kind of error that makes a citation look checked when it was not.
5. **P1** — a 19-word "exact definition quote" with "Section III.B, p. 15". **The string does not appear in WP/11/190.** The actual definition is a table footnote: *"Includes Treasury bills and Treasury securities with a remaining maturity of one year or less; includes agency discount notes"* (`:522`). Substance right, quotation fabricated.
6. **P3** — cites "Figure 1 ('The Money Hierarchy') and Table 1 (p. 15)". **There is no Table 1; Figure 1 is titled *The Money Matrix*; the "15" is a footnote superscript** (`:512`) read as a page number. And the cell assignment is wrong: the return puts T-bills in **public shadow money**; the text puts bills under seven days in **public money** and bills of 7 days–1 year in **public money-like claims** (`:843`); public shadow money is overnight *government repo* and CNAV government MMF shares (`:783`).
7. **S1** — "Pozsar (WP/11/190) approximated the liquidity tranche by summing TIC bills + the foreign repo pool". **"Liquidity tranche" occurs zero times in WP/11/190** (it is OFR 2014 vocabulary), and the shortage table nets foreign official holdings of short-term *Treasury and agency securities* only — no repo pool.
8. **P4** — "checked all 68 issues of Credit Suisse *Global Money Notes*". Paywalled proprietary research; the claim of having checked them is not credible. The negative is probably right anyway.

**Pattern:** the fabrications cluster exactly where the task shifted from *locate* to *establish* — the 2022–26 literature that would have pre-answered the test, and the page-precise quotations that would have let us skip reading. The canonical, heavily-cited material came back clean.

## 4. The two things that actually move D1 — both found by us, not by the return

**4.1 The in-sample forward test is already in Pozsar's own table.** WP/11/190 `:500–:524`, *"Sources of Institutional Demand for Treasury Bills and Agency Discos"*:

| $bn | 2005 | 2006 | 2007 | 2008 | 2009 |
|---|---|---|---|---|---|
| Short-term Treasury + agency supply | 1,714 | 1,662 | 1,752 | **2,812** | **3,402** |
| less foreign official | 328 | 303 | 261 | 403 | 596 |
| less cash pools (avg of two estimates) | 2,445 | 2,927 | 3,034 | 2,650 | 2,818 |
| **= Deficit** | **(1,059)** | **(1,568)** | **(1,543)** | **(241)** | **(12)** |

**When bill supply surged in 2008–09, the shortage closed from $1.5trn to ~zero.** That is the Triffin test, run forwards, inside the source — and it is the template for the 2013–2026 extension. The construction is fully specified: supply (bills + Treasuries ≤1yr remaining + agency discos) − foreign official − cash pools. Sources named: TIC, SIFMA, CapitalIQ, RMA, ICI, BIS.

**4.2 The ON RRP is gone.** FRED, 21 Aug 2026: `RRPONTSYD` = **$0.2bn**; total Fed RRP ≈ foreign-official RRP ≈ $373bn. The domestic facility that absorbed the 2023–24 bill surge — per the (unverifiable) L5 narrative — has **fully drained**. So from here, **any further bill absorption must come from private money-like claims or from cash-pool growth itself.** The test is sharper now than it was in 2024: the public-money buffer that would confound it no longer exists.

**4.3 The hypothesis to carry, not the finding.** L5's substantive claim — *the post-2023 bill surge displaced public shadow money (ON RRP) roughly 1-for-1 and left private shadow money largely unaffected* — is **plausible, widely discussed, and not established by anything in this return**, because the papers it rests on do not exist as cited. Carry it as **H1**, to be tested against re-pulled S6/S8/S12/S13/S14 data. If H1 holds, Pozsar's policy lever worked on the Fed's facility and not on the thing he wanted it to shrink — which is a genuinely interesting result either way.

## 5. What we learned about the instrument — registered as C-050/C-051

- **Completeness and truthfulness are different axes.** The skeleton + required-IDs + self-audit design produced 26/26 rows and a ticked checklist. It also produced at least eight constructed references, over a checkbox asserting none. **A self-audit is a completeness device, not evidence.** Keep it for the former, never cite it for the latter.
- **The "(seen, unverified — re-pull)" rule is the only thing that held.** Every number checked was wrong and none of them entered the record. That rule stays.
- **Where to draw the line, now with three data points (Parcels A–C, D1):** reliable on *which publisher / which table / does a standing series exist*; unreliable on *IDs, quotes, page numbers, post-2020 citations, and any value*. The next scouting parcel should **stop asking for IDs and quotes at all** — ask only for publisher + table + the name of the series, and we find the ID.

## 6. What changes on the list

- **D1 scouting is done enough to build on.** Series map (§2 corrected), construction template (§4.1), and H1 (§4.3) are in hand. **Next step is ours:** re-pull S6/S7/S8/S12/S13/S14 from the named tables and extend Pozsar's shortage table from 2010 to 2026.
- **L5 is reopened** — the 2022–26 literature on bill supply vs private money is unlocated. The one real pointer is the Liberty Street "Dropping Like a Stone" post. **Ask for it by topic and publisher next time, not by citation.**
- **Calendar:** nothing dated added; the build is not date-gated.
