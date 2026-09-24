# CORRECTIONS — claims that have been killed

**Append-only. Never delete an entry.** A killed claim does not stay dead by itself: this
project has already demonstrated that a verifier can refute a figure, write the refutation
down, and have the claim carry on standing in two other documents. Detection was never the
problem. **Propagation is.**

**Every role reads this file first, every session, before reading anything else.**
If you are about to write a number, grep it here.
If you kill a claim, append it here *and* list every `file:line` where it still stands.

| Field | Meaning |
|---|---|
| **Claim** | The dead statement, in the form it actually circulates |
| **Killed by** | Who refuted it and where the refutation lives |
| **Correct position** | What to say instead — never leave this blank |
| **Still standing at** | Live `file:line` occurrences not yet fixed. Empty = fully propagated |

---

## C-001 · "$662bn of hyperscaler leases signed but not yet commenced" (and the paired "$970bn / $660bn")

- **Killed by:** adversarial review, 21 Aug 2026 — `_research/funding_identity_adversarial_reviews.md:142`; carried into `Funding_Identity_First_Principles.md:121` and `:322`
- **Why:** no traceable primary provenance. A full-text search of the 96-page BIS Quarterly Review March 2026 returns **zero** occurrences of "662", "660", "970", "not yet commenced", "Beignet" or "Hyperion". Box A contains no lease-commitment quantum at all. The two figures in circulation are almost certainly one trade-press number appearing twice under two attributions, and were treated as two independent sources.
- **Correct position:** do not use either figure until traced to a named Moody's publication with a page. The *disclosed* per-company lease lines (Microsoft, Meta 10-Q "leases not yet commenced") are real and citable; the aggregate is not.
- **Still standing at:** ~~`Analysis/Panel_Synthesis.md`, `Analysis/Panel_Individual_Reads.md`~~ — both files carry a correction banner as of 21 Aug 2026. Occurrences preserved as a record of agent output, not endorsed. **Propagated.**

## C-002 · "M2 growing at roughly nominal GDP pace, so the aggregate says no boom"

- **Killed by:** funding-identity synthesis, 21 Aug 2026 — `Funding_Identity_First_Principles.md` §0.1
- **Why:** the *growth rate* does not establish it. 2009–2019 also ran near nominal-GDP pace while ~$3.0tn of M2 accumulated above a constant-velocity path.
- **Correct position:** the claim is established by the **level**, not the rate. M2/NGDP is 71.3% now against 70.0% at end-2019 and 91.1% at the 2020 peak — flat within 1.3pp for two years. Use the level series.
- **Still standing at:** *(none — corrected in CLAUDE.md and the concept map)*

## C-003 · "Under ZIRP, asset prices rose without M1–M3 being affected" (US)

- **Killed by:** ZIRP-premise attack, 21 Aug 2026 — `_research/funding_identity_adversarial_reviews.md`; synthesised at `Funding_Identity_First_Principles.md` §0.1
- **Why:** inverted for the US. M2/NGDP went 49.8% (2006Q2) → 70.0% (2019Q4); M2 compounded 5.86%/yr against nominal GDP 3.76%/yr Dec-2008→Dec-2019. The named mechanism *contracted*: ABCP −79% from its 2007 peak. US real estate **fell** for three years into ZIRP (Case-Shiller troughed Feb-2012, a further −12.2% after ZIRP/QE1/QE2). The shadow-money boom was **2002–2007**.
- **Correct position:** two safe forms. (a) *Japan*, where it holds — BoJ assets ×4.67 against broad money ×1.32, 2008–2019. (b) The stronger US reformulation — M2 outgrew nominal income by ~$3.0tn over 2009–19 and the increment was absorbed in asset markets rather than goods markets.
- **Also note:** US M1 is uninterpretable across the May-2020 Regulation D seam (~$11.2tn of savings deposits moved into M1), and there is **no US M3** after 23 March 2006.
- **Still standing at:** *(none)*

## C-004 · "AWS and Azure are third-order businesses built on stranded dot-com fibre"

- **Killed by:** example-(b) forensic, 2 Aug 2026 — `Third_Derivative_Concept_Map.md` §7
- **Why:** AWS's documented 2003 origin (Black/Pinkham) contains no bandwidth reasoning; Werner Vogels has called the excess-capacity story a myth. The ASP-to-SaaS natural experiment settles it: bandwidth was under 1% of ASP revenue even at peak-1998 transit prices, so a 100× fall in that line item cannot bind. Salesforce was founded March 1999 *inside* the frenzy on identical input prices and survived on multi-tenancy.
- **Correct position:** the **video/CDN** chain survives and is quantifiable. **Cloudflare (2009) is the only well-chosen name** on the original list. Remove AWS and Azure.
- **Still standing at:** *(none)*

## C-005 · "2.7% of laid dot-com fibre was ever lit" — and any dot-com *skills*-residue claim

- **Killed by:** example-(b) forensic, 2 Aug 2026 — `Third_Derivative_Concept_Map.md` §7
- **Why:** the 2.7% figure is a misquoted single-city datapoint. Separately, no public tracing of WorldCom / Global Crossing / 360networks engineers into any third generation exists, and carrier employment never recovered. US CS *degree* production actually **rose 57%** to a 2003-04 peak before falling; what collapsed was enrolment intent, a leading indicator with a four-year lag.
- **Correct position:** use the durable structural fact instead — **no new US national long-haul network was built from the late 1990s until roughly 2015–17.** Keep the fibre claim; drop the skills claim.
- **Still standing at:** *(none)*

## C-006 · "Cogent and Internap were founded after the crash to buy stranded assets"

- **Killed by:** round-1 case verification, 2 Aug 2026 — `_research/Round1_Evidence_Log.md`
- **Why:** Cogent was founded **1999**, Internap **1996**. Both are bubble-era firms.
- **Correct position:** the defensible mechanism is distressed recapitalisation — Cogent acquired assets from **13 failing carriers 2001–04, roughly $14bn of book value for about $60m**. That is the citable datum.
- **Still standing at:** *(none)*

## C-007 · "Railway Mania caused British time standardisation"

- **Killed by:** round-1 case verification, 2 Aug 2026
- **Why:** chronologically impossible. Great Western adopted London time **November 1840**; the Railway Clearing House recommended GMT in 1847 — before or concurrent with the mania it is claimed to follow.
- **Correct position:** drop time standardisation as a British third-order outcome. The 1883 **US** time-zone adoption is correctly dated and belongs only under the US railroad case.
- **Still standing at:** *(none)*

## C-008 · "Southwest's low-cost model was impossible under CAB regulation"

- **Killed by:** round-1 case verification, 2 Aug 2026
- **Why:** Southwest began flying **18 June 1971**, seven years before the Deregulation Act, operating wholly intrastate in Texas *precisely to sit outside CAB jurisdiction*. Deregulation let it scale across state lines; it did not create the model.
- **Correct position:** move the layer-3 claim to the post-1985 low-cost-carrier wave (JetBlue 2000, AirTran, Spirit) built on cheap post-bankruptcy aircraft and released pilot labour.
- **Still standing at:** *(none)*

## C-009 · "Stablecoins are the marginal buyer of Treasury bills"

- **Killed by:** channel map, 21 Aug 2026 — `Shadow_Debt_Channel_Map.md`, stablecoin channel; recipe at `Shadow_Debt_Measurement_Handbook.md` §2 item 10
- **Why:** parse N-MFP3 for the Circle Reserve Fund (CIK 0000844779): **88.0% overnight tri-party repo, 12.0% outright Treasuries** at 2026-07-31. Verifiable outright bill position **$7.18bn = 0.10% of bills outstanding**.
- **Correct position:** stablecoin reserves are overwhelmingly *repo*, which is a different channel with different implications. Also note ~60% of the sector (Tether) is backed by assets of unknown composition — the Q2 2026 attestation withdrew the Treasury-exposure dollar figure the Q1 gave.
- **Still standing at:** *(none)*

## C-010 · "The rated-note feeder / annuity chain creates money"

- **Killed by:** channel map, 21 Aug 2026 — `Shadow_Debt_Channel_Map.md`, private credit channel, Case 5
- **Why:** trace it by deposits. Annuitant → insurer → feeder → fund → borrower leaves aggregate deposits **unchanged at every step**. A deferred fixed annuity or MYGA carries surrender charges, market-value adjustments and tax penalties — it is not a means of payment and not par-on-demand. Fixed annuities are excluded from M2.
- **Correct position:** this chain manufactures *willingness to part with liquidity for longer*, not purchasing power. Maturity and liquidity transformation without money creation. A real fragility; label it accurately.
- **Still standing at:** *(none)*

## C-011 · Analysis of Competing Hypotheses — do not build it

- **Killed by:** research-ops investigate rung, 21 Aug 2026
- **Why:** tested against no-technique controls and failed. Dhami, Belton & Mandel (2019, *Applied Cognitive Psychology* 33(6):1080–1090); Karvetski & Mandel (2020, *JDM* 15(6):939–958) — "**no advantage over a no-technique control group**"; Lehner et al. (2008, *IEEE T-SMC Part A* 38:584–592) — confirmation bias present in **both** groups, ACH simply failed to reduce it in experienced analysts; Whitesmith (2020, Edinburgh UP, with UK Cabinet Office PHIA). The strongest single review is **Wilcox & Mandel, *Intelligence and National Security* 39(6):941–962 (2024)** — six experiments, "little to no overall benefit … may even harm."
- **Correct position:** do not build an ACH matrix, evidence×hypothesis scoring, or an Admiralty A-F/1-6 grading column. **But do not over-learn it:** Mandel, Karvetski & Dhami (2018, *JDM* 13(6):607–621) found **recalibration and aggregation across multiple independent judges cut mean absolute error by 61%** — operating on exactly the numeric probability judgments a naive reading of the ACH literature would ban. Collect independent probabilities from separate agents and aggregate; do not run the ritual.
- **Still standing at:** *(none)*

## C-012 · "SQLite in the project folder" / "the folder is Dropbox-synced"

- **Killed by:** research-ops data-engineering lens + cost verifier, 21 Aug 2026, both measured on the real path
- **Why:** the folder is **not** a locally-synced Dropbox directory. `~/Dropbox` is a symlink to `/Volumes/Dropbox`, an **SMB 3.1.1 network mount** of `//martin@192.168.178.156/Dropbox` — the Dropbox client runs on a different Mac on the LAN. `PRAGMA journal_mode=WAL` returns `delete`: SQLite **silently refuses** WAL because it cannot create the `-shm` file over a network filesystem, so an agent setting WAL gets no concurrency safety and no error. Measured cost: **93.7 ms** per connect+insert+commit+close versus **12.4 ms** for an `O_APPEND` JSONL write.
- **Correct position:** no SQLite in the project folder. Append-only JSONL/TSV. If a queryable index is ever needed, build it *outside* the mount and treat it as derived and disposable.
- **Also:** the earlier claim that "Dropbox breaks the Edit tool's atomic rename" was **not reproducible** on re-test — `os.replace()` succeeded. It failed once in this session, so it is intermittent, not structural. Do not justify a design choice on it; the in-place python write remains a safe fallback.
- **Still standing at:** *(none)*

## C-013 · "Offshore dollar credit is outside every monetary aggregate in the world"

- **Killed by:** offshore-dollar synthesis, 21 Aug 2026 — `2026-08-21-Offshore-Dollar-And-Money-Like.md` §CORRECTIONS(c), verified against primary central-bank methodology
- **Why:** wrong on two of the three aggregates named. The **ECB** states euro-area monetary aggregates *include* euro-area residents' holdings of liquid foreign-currency assets at euro-area MFIs. The **BoJ** *Guide to Japan's Money Stock Statistics* (October 2025) lists "Foreign Currency Deposits" as a named component of Time Deposits inside M2 and M3.
- **Correct position:** *dollar deposits at non-US banks are outside all monetary aggregates **when the holder is not a resident of the reporting bank's monetary area**.* That maps to the $14.11trn cross-border liability cut as an **upper bound**, less intra-euro-area cross-border holdings. Shrinks the "invisible money" claim by roughly a quarter and gives it a boundary that survives contact with a central bank statistician.
- **Still standing at:** *(flagged in the source document; do not restate the broad form)*

## C-014 · "Offshore dollar credit creation is unambiguously money creation, +$1.90trn"

- **Killed by:** offshore-dollar synthesis, 21 Aug 2026 — §CORRECTIONS(a) and (d). All nine researchers reached this independently
- **Why:** two errors. (1) **Perimeter.** $17.86trn / +$1.90trn / +11.9% is the *cross-border only* cut. The perimeter matching "offshore dollar credit" — cross-border **plus** local positions in foreign currency — is **$21.11trn claims, +$2,040bn flow, +10.7% y/y**. The level is $3.2trn larger and the growth rate *lower*. (2) **Not all creation.** $390.5bn of the expansion has no dollar liability behind it, so is definitively not creation; interbank recycling cannot be stripped out because `L_CP_SECTOR` is suppressed to 'A' on the foreign-currency cut, and genuine creation (case A) and interbank recycling (case D) produce an **identical** LBS signature.
- **Correct position:** quote three numbers on three perimeters, never one — **$2,040bn gross claim expansion; $1,650bn liability-matched; $754bn owed to an identified non-bank.** The last is the tightest defensible bound on money creation. Always state the perimeter.
- **Still standing at:** *(supersedes the framing used in earlier session messages; source doc carries the correction)*

## C-015 · "Collateral velocity has been flat 2–3 years on Basel III constraints"

- **Killed by:** offshore-dollar synthesis, 21 Aug 2026 — §CORRECTIONS(e)
- **Why:** **no primary source exists.** Singh's IMF work on velocity is a decade old and the claim has been carried through this project unsourced since round 1. The observable substitutes point the *other* way: FICC sponsored repo **+150% in two years to $2.856trn** (Dec 2025); non-centrally-cleared bilateral repo revealed at **$5.0trn**, roughly $700bn more than anyone had measured. Reuse appears to have migrated from dealer rehypothecation into CCP netting, which no velocity metric captures.
- **AMENDED 21 Aug 2026 — I over-claimed when I killed this.** The claim *was* traceable: Singh,
  Mercatus *Macro Musings*, **30 May 2022**, verbatim — *"It has stuck roughly there in the last
  two, three years."* The defect was **vintage, not provenance**. Spoken in mid-2022 it covers
  ~2019–2022; carrying it into 2026 silently re-dates it.
- **Correct position:** cite Singh's own **January 2026** statement instead, which supersedes it
  and is stronger — flat at ~2.0 for a *decade*, with the added claim that the flatness may be an
  artefact of end-of-day accounting because tokenised intraday reuse leaves no trace. Note also
  that the last full published velocity table is **IMF WP/19/106, data to end-2017 — seven years
  stale**. Two method traps: never splice the 2010 "churning factor of 4" to the later velocity
  series (different construction), and the series is **not vintage-stable** (WP/19/106 revised
  2010–2015 upward after adding Canadian banks). Do not drop the claim — The ECB SFTDS finding (~11.6% of European repo volume relies on reused securities, ~€49bn/day, rejecting the liquidity-windfall hypothesis) is separately sourced and survives — do not conflate the two.
- **Still standing at:** `Collateral_State_of_Argument.md` · `Where_The_Two_Workstreams_Meet.md` §1 · `Shadow_Debt_Measurement_Handbook.md`

## C-016 · Z.1 table identifier `L.207` for repo

- **Killed by:** offshore-dollar synthesis, 21 Aug 2026 — §CORRECTIONS(f)
- **Why:** the 11 June 2026 Z.1 release renumbered every table.
- **Correct position:** repo is now **F4.1.s** (stocks) and **F4.1.t** (flows). Mnemonics did not change; key any pipeline on mnemonics, not table numbers.
- **Still standing at:** *(none)*

## C-017 · "The constant safe-asset share means quantity is fixed, so KVJ is only about composition"

- **Killed by:** operator, 21 Aug 2026, in session. Four prior research passes cited GLM without catching this.
- **Why:** the safe-asset share is a **ratio**, and it was used as if it were a level. Constant share × growing denominator = growing numerator. Gorton, Lewellen & Metrick's 33.2% (s.e. 0.003) constrains the *proportion* of total US assets held in safe form; it says nothing whatever about the quantum. If total assets grew by a factor of N since 1952, safe assets grew by N too. The inference "what varies is composition, not quantity" does not follow — it silently assumes a fixed pie.
- **Sharpened further (project inference, being verified):** the numerator is largely **par**-denominated (Treasuries, deposits, MMF shares, repo) while the denominator is substantially **market**-valued (equities, real estate). A stable ratio between a par numerator and a market denominator, to three decimal places over seven decades, is not a null — it is a co-movement demanding explanation.
- **Correct position:** GLM is a constraint on the safe *share*, not on the safe *stock*. It may be cited as evidence that safe-asset demand is a stable fraction of wealth. It may **not** be cited as evidence that money-like quantity is fixed, nor as a null against KVJ. Whether the co-movement runs wealth→safe-assets or safe-assets→valuation is an **open question**, tracked as K4 in `RESEARCH_STATE.md`.
- **Also check before citing:** the GLM sample ends around 2010. Do not present "constant since 1952" as a current reading without extending the series.
- **Still standing at:** *(caught before it entered any document; the claim was made in session only)*

## C-018 · "The KVJ sign has inverted — Treasury supply now crowds private money IN"

**DO NOT PUBLISH IN ANY FORM.** Not "with qualification." Three independent fatal defects.

- **Killed by:** KVJ verification pass, 21 Aug 2026 — papers read first-hand (JPE 2012 via JSTOR; JFE 2015 via the March 2013 working draft). Three of four lenses returned `refuted` or `unproven_and_doubtful`.
- **Why (1) — it is not KVJ's coefficient.** The −0.486 (t = −5.02) is on **NET** short-term debt: short-term debt *minus* short-term assets *minus* the financial sector's own holdings of Treasuries, reserves and currency. A Treasury-collateralised repo enters as a liability **and** an offsetting asset and **nets to ≈zero by construction**. The collateral channel is not a weak term in the coefficient — it is **invisible in the dependent variable by definition**. You cannot invert a sign by strengthening a channel the dependent variable nets out.
- **Why (2) — there was never a sign to invert.** KVJ's coefficient on **GROSS** short-term debt is **−0.042, t = −0.52** (SE ≈0.081, 95% CI ≈ −0.20 to +0.12). They never found crowding-out of gross private money.
- **Why (3) — the claim is KVJ's own published result.** The +0.223 (t=6.19), +0.453 (t=8.16) and +1.15 figures we treated as embarrassing footnotes are **Predictions 3 and 4** — explicitly derived, explicitly tested. Treasury collateral backing money claims is *in their model by name*. We were claiming as novel what the paper says on purpose.
- **The evidence was also broken.** (a) Δrepo/Δrunnable is **positive whenever repo grows**, regardless of Treasury supply — a statistic that cannot take the falsifying sign is not a test. (b) The two windows do not match: repo +19.1% is Q4-24→Q4-25; bills +16.6% is Jul-25→Jul-26. Five months of twelve overlap. (c) The bill figure is measured from a **debt-ceiling trough**: 39.7% merely restores the pre-ceiling level and the Fed absorbed +$342.3bn. **Bills outside the Fed grew +$256.6bn, +4.1% over 20 months (~2.5%/yr)** — the headline overstates private-hands supply by **~3.9× in level and 6.6× in rate**. (d) The **bill share of marketable debt is flat** (22.2% Jul-26 vs 22.6% Nov-24) — there is no shift toward bill financing.
- **A large rival explains the repo growth.** Over the identical window, hedge-fund repo borrowing rose **+$882bn (+35.3%)** — the same order as the entire increase in the FSR repo line — with relative-value strategy borrowing +70.7%. Leveraged funds' net short Treasury futures ≈ **−$923bn**, roughly 2.2–2.8× the pre-March-2020 peak; the Fed's June 2026 FEDS Note puts the basis trade at **$830bn**. A hedge fund is the cash **borrower**; it issues no money-like claim to any saver. That is demand for **leverage**, not moneyness.
- **And the evidence points the other way.** ABCP **+23.4% y/y** is the fastest-growing private money line and is backed by **private** assets; MMF repo against **non**-Treasury collateral +42.0%; financial CP −4.0%. Under our thesis the Treasury-collateralised lines should be the fast growers. They are the slow ones. Meanwhile MMFs put **82.1%** of AUM growth into outright Treasuries while bank paper **fell 9.3%** — Treasury supply displacing bank-issued money claims, i.e. the KVJ direction.
- **Out of sample, and the wrong way.** The only re-estimation covering the current regime (Phillot & Wenger, ASSA 2025, 1998–2023) finds crowding-out **larger**, not inverted. Separately, JPE debt/GDP averaged 0.439 over 1919–2008; it is ~0.994 today — a level reached in-sample only in 1945–46, years KVJ explicitly quarantine.
- **Correct position:** what survives is a **measurement critique**, making no claim about any coefficient's sign — *a net measure that nets to zero the most run-prone part of the money-like stack cannot be the right summary statistic for fragility, as March 2020 demonstrated.* Words that must never appear: "the sign has inverted", "crowding in rather than out", "regime change in Treasury supply", and any use of Δrepo/Δrunnable as evidence about a supply elasticity.
- **Two file-level corrections:** the +1.15 is **body text only**, not in any table, with t reported only as "above 2" — our file says "their own table carries" it. And the CD−bill liquidity coefficient (−1.884, t=−1.71, **N=25**) is **not significant at 5%**; its 95% CI includes zero.
- **Still standing at:** *(caught before publication; the claim lives in `2026-08-21-Offshore-Dollar-And-Money-Like.md` §3.2, which now carries a banner)*

## C-019 · The Fed FSR Table 4.1 components do not partition the total

- **Killed by:** same pass, 21 Aug 2026
- **Why:** the listed lines (MMF 7,746 + uninsured deposits 7,608 + repo 5,887 + bond mutual funds 5,032 + CP 1,368 + securities-lending 1,201) sum to **$28,842bn against a stated total of $27,033bn**. This project's decomposition treats them as a partition and **omits the $5,032bn bond-mutual-fund line entirely**.
- **Correct position:** the 32.6% and ~58% figures reconcile as shares of the *increase* and may be used as such with that stated. They may **not** be presented as a decomposition of the level. Pull the actual table and its footnotes before publishing either.
- **Still standing at:** `2026-08-21-Offshore-Dollar-And-Money-Like.md` §3.3 — the decomposition table

## C-020 · "Bank lending to non-banks (H.8 line 26) is the intra-financial credit channel"

- **Killed by:** two-circuits synthesis, 21 Aug 2026 — re-derived from the Fed's own H.8 footnote
- **Why:** **loans for purchasing or carrying securities, including margin loans, are EXCLUDED from the NDFI line** and sit in the adjacent line. H.8 line 26 is loans to *credit intermediaries* — mortgage, business and consumer credit intermediaries, PE funds, insurers, securitisation vehicles, hedge funds, pension funds. It is a private-credit and warehouse-funding series, **not a buy-securities series**. Separately, **28.3% of its seven-year rise is a definitional reclassification with no historical revision.**
- **Correct position:** S5 stands as a statement about *private-credit and warehouse funding* growth. It may **not** be used as evidence of credit financing asset purchases. For that, the correct series is FINRA margin debt **plus** H.8 "loans for purchasing or carrying securities" — and that measure tells the opposite story (see C-021).
- **Still standing at:** `RESEARCH_STATE.md` S5 — reworded

## C-021 · "Credit against securities is inflating equity valuations"

- **Killed by:** same pass, 21 Aug 2026 — re-derived from FINRA margin statistics, FRED NCBEILQ027S, BOGZ1LM893064105Q, AOLACBM027NBOG
- **Why:** identified credit extended against securities has **shrunk relative to the prices it is supposed to explain**. As a share of Z.1 nonfinancial corporate equity market value: **5.241% (2015Q4) → 4.544% (2019Q2) → 3.534% (2021Q4) → 3.495% (2026Q1)**. Mean across 45 quarters 4.248%; the latest reading ranks **36th of 45**. Margin debt alone is 1.756% of NFC equity value — **rank 57 of 117 quarters since 1997, essentially at the median** — against 2.348% in June 2007 and 1.844% at the March 2000 peak. The +38.6% y/y margin-debt growth is **catching up, not leading**: the ratio *fell* from 1.677% (2021Q4) to 1.325% (2024Q3) through the entire 2023–24 rally.
- **Correct position:** this is the **answer to the load-bearing unknown X** in the illusion-of-wealth chain — the pledged fraction is roughly 3.5% on identified credit and near the *bottom* of its own range, below both 2007 and 2000. It is deflating to the fragility thesis as stated. What remains genuinely dark is securities-based lending, NAV loans, portfolio margin and internalised synthetic prime — but the *identified* portion no longer supports a leverage-driven account of equity valuation.
- **Still standing at:** *(new finding; nothing to propagate)*

## C-022 · "The safe-asset share has been 33.2% (s.e. 0.003) every year since 1952"

- **Killed by:** safe-asset pass, 21 Aug 2026 — back-solved analytically from GLM's own published Table 1, no data required
- **Why:** **0.003 is the standard error of a regression INTERCEPT, not the dispersion of the share.** Backing out the residual variance from GLM's own reported coefficients, t-statistics and R²: residual SD ≈ **0.0223**, unconditional SD **2.24pp**, implied ±2SD band **28.7%–37.7% — a nine-point range**. The back-out is verified by the fact that it reproduces GLM's *other* reported standard error, se(trend) = 0.00002, to the digit. Confirmed independently twice more: a Z.1 reconstruction gives SD 0.0231, and the Fed's own FEDS Note (2020-11-09) reports SD 2.3%.
- **GLM never make the claim.** They label their standard error correctly and their own text says "30–35%". *"Constant to three decimal places over seven decades" is a misreading that entered downstream of the paper* — and this project propagated it.
- **Three further defects in the constancy result:** (a) GLM publish **two** constructions side by side; the **low** estimate trends at t = −11.71, R² = 0.367, **−5.0pp over the sample**, with the same dispersion. The difference is an 85% haircut on MBS/ABS **asserted without derivation**. The literature cites the flat one — a selection, not a finding. (b) R² = 0.012 against a linear trend is evidence of *no linear drift*, which a driftless random walk also delivers; no unit-root test is run. (c) **It does not survive extension**: 2026Q1 sits at 27.49%/27.99% on two independent reconstructions, the minimum of 297 quarters, **z = −2.33 to −2.55 — outside the 95% band implied by GLM's own regression**, with the post-2011 trend differing at t = −4.76.
- **Correct position:** the share is "roughly one-third, ±2.2–2.4pp, on one of two constructions, and it has broken down since 2011." **GLM is not a null — it is a documented puzzle whose authors explicitly decline to sign the causality**, closing with "Why is the safe-asset share constant?" as an open question and stating on p.11 that *"the production of total assets appears to require safe debt as an input"* — the supply-side channel, in their own words.
- **Still standing at:** *(never entered a document; asserted in session and corrected before publication)*

## C-023 · "GLM's numerator is par-denominated while its denominator is market-valued"

- **Killed by:** same pass, 21 Aug 2026. This was a **project inference**, explicitly flagged as such when made, and it does not survive contact with the construction.
- **Why:** the numerator half is confirmed (98.8% of its 1951–2026 level change is transactions; the Treasury revaluation series is *identically zero* in all 297 quarters). **The denominator half is wrong three ways.** (1) It is **not wealth** — it is FL894194005, the *unconsolidated* sum of all-sector liabilities and equity, double-counting every intermediated claim; 1.32× US net wealth in 1952 and **2.51× today**. (2) It contains **no real estate at all** — housing is not a liability of any sector, so household nonfinancial assets of **$62.93trn (2026Q1)** are entirely outside it. (3) It is **majority par**: 61.5% transactions / 36.8% revaluation over 1952–2026, and 79.4% / 18.1% across GLM's own window.
- **Also fatal to the proposed mechanism:** "safe supply drives the denominator" does not deliver constancy — **only a unit elasticity does**, and the realised long-run elasticity is **0.946**. That 5.4% shortfall is precisely what takes the share from 36.98% to 27.49%. And **rising equity valuation moves the share the wrong way**: it enlarges the denominator without the numerator, pushing the share *down* (R² = 0.670, corr = −0.818). **Valuation breaks the constancy; it does not manufacture it.**
- **The real mechanical problem is simpler and worse:** the numerator is a strict **subset** of the denominator, so co-movement in the par block is close to accounting. GLM ran a Monte Carlo against exactly this and **did not clear it** — roughly 30% of simulated coefficients were smaller than their own. Mechanical construction is a live, un-rejected explanation of their headline result *by their own test*.
- **Correct position — and this is the publishable version:** the denominator's *market-valued fraction is growing*. Revaluation share of its change: **18.1%** across GLM's window → **49.2%** (2011–2026) → **66.6%** (2022Q4–2025Q4). **The constancy held while the denominator behaved like a quantity, and failed once it started behaving like a valuation.** That makes the par character of the numerator the interesting asymmetry rather than a coincidence.
- **⚠ Unresolved before publishing any level:** two reconstructions disagree by ~21pp on the denominator's market-valued fraction *and on the sign of its long-run change* (R1: 11.6%→31.1%; R2: 42.9%→52.4%). Both reach the same qualitative conclusion. **Do not publish a level until reconciled.**
- **Still standing at:** *(inference made in session, corrected before publication)*

## C-024 · ⚠ UNRESOLVED CONFLICT — the margin-debt ratio, our single load-bearing number

**Do not use either figure until reconciled. Two of our own agents disagree on the same series.**

- **Raised:** 21 Aug 2026, inbox-harvest synthesis, recomputing what C-021 had just established
- **The conflict.** Both claim FINRA margin debt ÷ Z.1 `NCBEILQ027S`, both for 2026Q1:
  - **C-021 (Singh pass):** **1.756%**, "rank 57 of 117 quarters since 1997, essentially at the median (1.728%)", below June 2007 (2.348%) and March 2000 (1.844%). Conclusion: *near the bottom of its range, deflating to the fragility thesis.*
  - **Inbox pass:** **1.84%**, "**the highest since 2008Q4**, above both the 2000 and 2021 cycle peaks", with 2000Q2 at 1.72% and 2007Q3 at 2.37%. Conclusion: *elevated.*
  The two differ on the level, on the comparator quarters, and on the **sign of the conclusion**.
- **And our record's own figure is a third number.** `RESEARCH_STATE.md` carried **0.90%**, which is roughly half both. That is probably a different denominator — total US market cap including financials and foreign issues would roughly halve it — but it was never named.
- **Correct position:** **three different numbers for the one quantity we designated load-bearing.** Before any further use: name the denominator explicitly (NFC equity only, all-sector corporate equity, or total market cap), fix the vintage, and recompute once. Until then the pledged-fraction claim in either direction is unsupported.
- **What is NOT in conflict, and is the more useful finding:** the **flow**. 12-month margin-debt growth was **+53.7% into May 2026** and +49.0% into June — placing 2026 in the **top ten expansions of the 355-month record**, alongside March 2000 (+80.5%), July 2007 (+62.6%) and April 2021 (+61.5%). *Every other member of that list is a recognised bubble peak.* June 2026 was the all-time peak at $1,502bn; July fell **−$84.8bn, −5.65%, the 7th percentile of monthly changes.* **We recorded a level and called the channel uninformative. The level is contested; the growth rate is informative, and it has already turned.**
- **Still standing at:** `RESEARCH_STATE.md` §1 (0.90%) and C-021 (1.756%) — both flagged pending reconciliation

## C-025 · "There is no aggregate external funding gap, so no monetary explanation is required"

- **Qualified, not killed** — 21 Aug 2026, inbox synthesis; four lenses hit it independently and none refuted it
- **Why it needs the caveat:** the identity holds, but it holds **because the internal-funds surplus sits at firms that are not doing the capex.** Six hyperscalers issued ~$182bn IG YTD against roughly $690–800bn of 2026 capex. Alphabet's FCF turned **negative in Q2 2026 for the first time**, with long-term debt more than doubling to ~$98bn in H1; Amazon's debt rose 81% to ~$119bn in Q1. Accelerating depreciation is precisely what produces "FCF near zero while capex explodes."
- **Correct position:** the finding is true and **answers a question nobody asked**. As previously worded it reads as a refutation of the funding question when it is silent on it. Always attach the composition caveat, or retire it from load-bearing use.
- **A second threat, checkable:** neocloud and SPV borrowing may sit **outside** the non-financial corporate sector in the Financial Accounts. If so the aggregate result is partly a sectoral-classification artefact at exactly the point where it matters. Test: SIFMA issuance by sector against Z.1, and locate where data-centre lease-backed ABS lands.
- **Still standing at:** `RESEARCH_STATE.md` S1 — caveat now attached

## C-026 · Leaning on the Gabaix–Koijen ~$1-to-$5 multiplier

- **Qualified** — 21 Aug 2026, inbox harvest
- **Why:** Michael Green has written continuously on precisely this mechanism for six months and **never cites, reproduces or endorses the $5 multiplier**. His parameterisation is entirely different (Haddad–Huebner–Loualiche two-thirds offset; Bouchaud impact scaling with volatility; ~0.33pp/yr concentration premium). Not a refutation — but if we lean on $5 we lean on **one paper**, and the reallocation-to-aggregate step is actually carried by Jiang–Vayanos–Zheng, not by Gabaix–Koijen.
- **Correct position:** cite it as one estimate among several, name the step that Jiang–Vayanos–Zheng carries, and never present the downside multiplier as established — there is still no separate symmetry result.
- **Still standing at:** multiple documents — cite with the caveat rather than annotating each

## C-027 · "The FIMA repo facility funded a yen intervention"

- **Refuted by primary data** — 21 Aug 2026. Two inbox sources asserted it; a third flagged it as a testable lead.
- **Why:** the full 2026 weekly Fed repo-asset series (`WORAL`, $mn) reads **1, 0, 102, 0, 3, 1, 0, 1** across 1 Jul – 19 Aug, and H.4.1 for the week ended 19 Aug shows the **"Foreign official" sub-line at exactly $0** on all four columns. WORAL is a *weekly average of daily figures*, so a single-day $30bn draw would show as ~$4.3bn against a $0–3mn baseline. **No draw of any material size occurred on any day of July or August.**
- **Epistemic lesson to carry:** two sources agreeing is not corroboration when both may be reading the same third party. The four commentators asserting this are a **citation cascade, not four observations** — the same false-consensus failure this project has now hit four times.
- **Still standing at:** *(caught in harvest; never entered a document)*

## C-028 · "Household saving rate 2.7% (June 2026), lowest since 2005"

- **Killed by:** Grok external review, 22 Aug 2026 — `2026-08-22-Grok-External-Review.md` §1–§2(i). The correct rank was already in `2026-08-21-Singh-And-The-Two-Circuits.md:158` and was not propagated.
- **Why:** BEA Personal Income and Outlays, June 2026 (released 30 Jul 2026) and FRED `PSAVERT` confirm the **2.7%** print. They also show **June 2022 = 2.2%** and **July 2005 = 1.4%**, with 28 months of 810 since January 1959 strictly below 2.7 (2005, 2006, 2007, 2008, 2022). The ranking is false. The level is not.
- **Correct position:** 2.7% in June 2026 is back in the 2005–07 range. It is not a post-2005 low. Rank it, or drop the ranking.
- **Still standing at:** `Review_Prompt_For_Grok.md:25` (historical prompt, preserved)

## C-029 · "Net fixed investment rose only 5.8% while gross rose 13.1%" circulating without its window

- **Killed by:** Grok external review, 22 Aug 2026 — `2026-08-22-Grok-External-Review.md` §2(iii). The source computation is not wrong.
- **Why:** `Funding_Identity_First_Principles.md` §2.1 names the window: **2023Q4 → 2026Q1** (gross fixed investment $2,849.6bn → $3,223.2bn, +13.1%; net $653.8bn → $691.6bn, +5.8%). Downstream, RESEARCH_STATE S2 and the Grok prompt shipped the percentages without the two dates. 2024→2025 annual NFC capex on Z.1 F.103 (19 Mar 2026) is **+4.1%**, a different object. A named-window fact that travels as a free-standing percentage is how base-effect errors restart.
- **Correct position:** always print 2023Q4 and 2026Q1 with the 13.1% / 5.8% pair. Do not compare either figure to a one-year change.
- **Still standing at:** `Review_Prompt_For_Grok.md:39` (window omitted). RESEARCH_STATE S2 updated 22 Aug 2026.

## C-030 · THE FRAMING ITSELF — "a boom is being funded while the household saving rate falls; where does the money come from?"

**This is the largest correction in the register. It kills the question, not an answer.**

- **Killed by:** external review (Grok), 22 Aug 2026 — `2026-08-22-Grok-External-Review.md`. Named as the *first* objection a hostile economist raises, and it is right.
- **Why:** falling household saving is **how corporate internal funds are produced**, not a puzzle sitting alongside them. In the Kalecki identity — which this project has carried since its first research round — household saving enters with a **minus sign**: profits = investment + government deficit − household saving + net exports + capitalists' consumption. A falling household saving rate *mechanically raises* corporate profits. The two facts we treated as a tension are the **same fact seen from two sides of an identity**.
- **And we were reading the wrong statistic.** The household saving *rate* fell while **gross private saving rose from $4,815bn (2019) to $6,384bn (2025)** — up ~$1.57trn. There was never an aggregate saving shortfall to explain.
- **Correct position:** there is no funding puzzle. Do not open the essay with one. The interesting questions are elsewhere: *who* holds the resulting claims, *what* they are pledged against, and whether the guarantee layer that now supports the capex is measurable at all (S10).
- **Error class — the fourth instance, and it is now the project's signature failure.** A **rate** is not a **quantity**. Same species as C-017 (a ratio read as a level), C-018 (a *net* coefficient read as gross) and C-022 (an intercept standard error read as dispersion). Invariant 8 exists for exactly this and did not fire, because the error was in the *question* rather than in a cited statistic. **Invariant 8 now applies to the framing, not only to the evidence.**
- **Consequence for the thesis:** *"the wealth is not real and will not survive being tested"* is **not supportable as stated**. See `RESEARCH_STATE.md` §1 for the restatement.
- **Still standing at:** `RESEARCH_STATE.md` §1 and `CLAUDE.md` — both restated 22 Aug 2026

## C-031 · "A Big Tech lease guarantee roughly halves a project's financing cost"

- **Killed by:** guarantee-stack pass, 22 Aug 2026 — `2026-08-22-Guarantee-Stack.md`, from the bond documents themselves
- **Why:** false on the only measure any filer discloses. No issuer states a spread to any benchmark, so the "halving" ratio is unverifiable in principle; on **coupon**, the reduction is never a halving. Maximum observed across four same-or-cross-sponsor pairs: **38%**. A halving needs 50%.
- **The best-controlled observation kills it outright.** Hut 8, same sponsor, 38 days apart, both maturing 2042, both amortising, both non-recourse — Google backstop **6.192%** versus direct AA-or-higher tenant **6.129%**. A difference of **6.3 basis points, 1.0%.** River Bend also amortises two years earlier, so 6.3bp is if anything a floor.
- **And the two same-sponsor observations disagree with each other.** The Cipher pair (Google backstop → direct IG, 90 days) gives 100bp. **The backstop discount is somewhere between 6 and 100bp and we cannot narrow it.** Do not quote a point estimate.
- **Correct position:** the guarantee buys a *lift into investment grade*, not a lift *to the tenant's rating* — Beacon Point has an AA-or-higher tenant and Baa2 notes, **seven notches of leakage** — and Galaxy's CoreWeave-tenant project bond prices **25bp wider** than CoreWeave's own unsecured paper, so project structure is worth nothing or less. What the covenant buys is *the existence of the financing*, not basis points. Cipher paid **$544.5m** of warrants for a backstop worth ~$87m of interest over the note life — **six times the coupon saving**.
- **Still standing at:** `RESEARCH_STATE.md` S10, `2026-08-21-Inbox-Harvest-And-Research-Plan.md` — both annotated

## C-032 · "Nvidia is the tenant in the Hut 8 transaction"

- **Killed by:** same pass, 22 Aug 2026 — Hut 8's own 10-Q
- **Why:** **the word NVIDIA appears zero times in it.** Hut 8 describes the counterparty only as *"a high-investment-grade company (i.e., rated AA- or higher)"*. The attribution came from press coverage and this project adopted it as fact.
- **Correct position:** say "an unnamed tenant rated AA- or higher, per Hut 8's own disclosure." The rating band narrows the candidate set; **do not name the company.** Demote every Nvidia-as-tenant reference to press attribution.
- **Still standing at:** `RESEARCH_STATE.md` S10 and the inbox plan — annotated

## C-033 · "Hut 8's 6.129% priced ~100bp over Nvidia's own 30-year paper"

- **Killed by:** same pass, 22 Aug 2026
- **Why:** **not reproducible.** NVIDIA has issued no bond since 2020; its only long bond is the 3.70% due 2060. Against that coupon, 6.129% is **243bp**, not ~100bp. Combined with C-032 the comparison has no basis — we did not know the tenant and we compared to the wrong bond.
- **Correct position:** drop the spread claim entirely. The defensible comparison is the **same-sponsor Hut 8 pair** (6.192% backstopped versus 6.129% direct AA- tenant, 38 days apart, matched structure).
- **Still standing at:** annotated with C-031

## C-034 · "The guarantee layer is the mechanism"

**Reframed, not killed — and the reframe is the most important finding of the project.**

- **Established by:** same pass, 22 Aug 2026
- **Why:** the guarantee is the **visible minority case**. At Hut 8's Beacon Point the notes are **expressly not guaranteed by anyone** — Hut 8 says so — and the **bare lease covenant alone earns Baa2**. Of $16.58bn of investment-grade-covenant project debt identified on the beneficiary side, **$8.40bn rests on an unguaranteed lease and $8.18bn on a guarantee.**
- **The larger object, on one clean standard.** ASC 842 leases **signed but not yet commenced**, six filers, all at or near 30 Jun 2026: Microsoft $329.1bn + Meta $278.99bn + Oracle $260bn + Amazon $137.2bn + Alphabet $85.2bn + NVIDIA $32.4bn = **$1,122.9bn**, against ~$417.4bn of prior-period equivalents — roughly **2.7× growth**, an order-of-magnitude statement given the vintages span eight months. **Disclosed by 6 of 6 filers. Tagged in XBRL by 0 of 6.**
- **That last fact is the mechanical explanation for the C-001 ghosts.** With no structured series to pull, intermediaries reconstruct one, and the reconstruction circulates — which is how "$662bn" and "$970bn" entered the discourse with no traceable primary source. **$1,122.9bn on one standard with six accession numbers is the properly sourced replacement.**
- **Correct position:** the mechanism is an **unrecorded lease obligation**, not a guarantee. It is 13× larger, equally off balance sheet, and disclosed by everyone in prose while being machine-readable by no one.
- **Still standing at:** `RESEARCH_STATE.md` S10 — rewritten

## C-035 · "The discount-rate account fails on SIGN"

- **Killed by:** external review (Gemini), 22 Aug 2026 — named as its single strongest objection, and it is right
- **Why:** we tested the wrong variable. The equity discount rate is **R = r_f + ERP − g**. We observed r_f (10y TIPS) rise +339bp and concluded the discount-rate channel had failed — which holds **ERP and g constant by assumption**. Over the same window credit spreads compressed to historical tights, implied volatility sat near cyclical lows, and the AI capex thesis is explicitly a bet on a structural upward revision to long-run g. An ERP compression plus a g revision straightforwardly offsets +339bp on r_f.
- **Correct position, and note what it does NOT say:** *the risk-free benchmark rate alone cannot explain the path of equity multiples.* That is all. It does **not** reinstate the discount-rate account as established — ERP and g are unobservable, so an account free to choose both can always be made to fit, which is its own weakness. The honest state is **untested, not refuted.** Do not simply flip the sign of the old conclusion.
- **Consequence:** K1's resolution ("neither monetary nor a discount-rate artefact") is **half withdrawn**. The circuit half stands on three observables. The discount-rate half rests on an invalid test.
- **Still standing at:** `RESEARCH_STATE.md` K1 and §1 — amended

## C-036 · "Tobin's q at 2025Q3 is the highest of 304 quarters since 1945"

- **Challenged by:** same review, 22 Aug 2026. **Logged as contested, not killed — we could not verify the counter-figures from here.**
- **Why it is challenged:** the Z.1 equity-q denominator is historical-cost net worth. It does not capitalise R&D or software intangibles, and it carries accelerated depreciation on 3–5 year silicon — so the denominator is **systematically suppressed** exactly where the capex is concentrated. On a **replacement-cost** basis the reviewer puts the 2025Q3 peak at **~1.94, still below the 2000Q1 dot-com peak of ~2.15**.
- **And the three metrics we cited are not mutually reinforcing.** Equity/after-tax profits is a multiple on *current cyclical* profits, themselves inflated by the fiscal deficit. Equity/GVA "flat to three decimals" is a capital/output ratio — if market cap grew in step with corporate gross value added, that indicates **economic scale expanded proportionally**, which *undercuts* rather than supports a pure-multiple-bubble reading. We presented three numbers as one argument; they point in different directions.
- **Correct position pending verification:** state which q is being used, on which denominator, and do not claim an all-time high without the replacement-cost series alongside. **Verify the ~1.94 / ~2.15 pair before either using or dismissing it.**
- **Still standing at:** `RESEARCH_STATE.md`, `Review_Prompt_For_Gemini.md` — annotated

## C-037 · THE FIFTH SIGNATURE ERROR — reading the Greenwald–Lettau–Ludvigson 40.2% / 14.3% as a structural law

- **Found by:** same review, 22 Aug 2026, in direct answer to a request to hunt this error class. It found one.
- **Why:** 40.2% (factor shares) and 14.3% (interest rates) are **in-sample variance-decomposition shares over 1989–2017** — a period in which interest rates contributed little variance *because they trended monotonically downward*. We used them as a structural claim that rate rises in 2022–26 cannot compress multiples. **A variance share is not an elasticity, and an in-sample decomposition is not a law.**
- **The species, now five instances deep:** a ratio read as a level (C-017); a *net* coefficient read as gross (C-018); an intercept standard error read as dispersion (C-022); a *rate* read as a quantity (C-030); and now a *variance share* read as a structural multiplier. Also implicated: the Gabaix–Koijen aggregate multiplier read as a sectoral law (C-026).
- **Correct position:** cite GLL for what it establishes — that factor-share reallocation has historically explained more equity variation than rates did *in that sample* — and never as a forward constraint on what rates can do now.
- **Still standing at:** `RESEARCH_STATE.md` K1 — amended

## C-038 · Placing Form PF hedge-fund repo alongside Fed FSR Table 4.1 repo

- **Killed by:** same review, 22 Aug 2026. **Both underlying numbers CONFIRMED; the comparison is the error.**
- **Why:** they measure opposite sides of the trade. **Form PF repo** measures hedge funds as cash *borrowers*, pledging Treasury collateral to dealer prime brokers — an indicator of **fund leverage demand**. **FSR Table 4.1 repo** measures dealers and depositories as cash borrowers issuing runnable liabilities to cash providers — an indicator of **money-like liquidity supply**. Setting +$882bn against the +$944bn FSR increase implied an attribution that the measurement bases do not support.
- **Correct position:** the two numbers are both right and may both be cited, but never as numerator and denominator of the same question. The basis-trade hypothesis for repo growth is **not evidenced by this comparison** and needs a different instrument. *(This also weakens, though does not overturn, open question 0c.)*
- **Still standing at:** `RESEARCH_STATE.md` open question 0c — amended

## C-039 · "Japanese banks are 47% of the offshore dollar funding residual"

- **Corrected by:** same review, 22 Aug 2026. The global residual is **CONFIRMED** at $390.6bn; the attribution is mis-stated.
- **Why:** the 47% is derived from **residence-based** series (`L_REP_CTY=JP`, i.e. Japan-*located offices*), not from **parent-bank nationality** (`L_PARENT_CTY`), which BIS suppresses for foreign-currency local positions. The Japan+China 89% additionally **mixes bases** — China reports cross-border only, Japan includes local foreign-currency positions.
- **Correct position:** say **"Japan-located banking offices"**, never "Japanese banks", and never present the pair as a nationality decomposition. Verified components: Japan-located offices grew USD claims +$334.2bn against liabilities +$152.5bn, a ~$181.7bn gap = 46.5% of the $390.6bn global gap.
- **Still standing at:** `RESEARCH_STATE.md`, `2026-08-21-Offshore-Dollar-And-Money-Like.md` — annotated

## C-040 · PROCESS DEFECT — the register only protects against claims someone remembered to register

**This is a finding about the apparatus, not about the economy, and it is the reason C-036 got through.**

- **Found:** 22 Aug 2026, while propagating C-036.
- **What happened.** On 21 Aug our own Singh pass produced a **17-item "do not say this" list**, including item 13: *the Z.1 Tobin's-q denominator does not capitalise intangibles, so measured q drifts up mechanically; the arithmetic is right, the interpretation is not survivable.* **Only 3 of those 17 items were ever promoted into `CORRECTIONS.md`.** The next day I put "Tobin's q, highest of 304 quarters since 1945" into an external-review parcel as a load-bearing belief. An external reviewer then independently re-found the same defect.
- **Why the guard did not fire.** `bin/check.sh` greps against the ban list in this file. A caveat raised *inside a research document* and never promoted is **invisible to it by construction**. The detection existed, one day old, in a document I had read. Detection was never the problem — it is the same failure the register was built for, one level up.
- **Confirmed still live:** "collateral velocity is X" phrasing appears in **3 current documents** despite item 10 of that list ruling it out (say *"Singh estimates"*, never *"velocity is"* — no independently verifiable ratio exists after 2017).
- **Correct practice, now binding:** when a research pass produces a *do-not-say* list, **promoting it to `CORRECTIONS.md` is part of landing that pass, not an optional follow-up.** A caveat that lives only in the document that raised it will be violated by the next document.
- **Outstanding:** the remaining unpromoted items from the 21 Aug list need triage. Highest-value ones spotted so far — velocity phrasing (item 10), Damodaran's near-circular 266bp (item 14), Bezemer et al. used to characterise 2026 when the sample ends 2005 (item 15).
- **Still standing at:** `2026-08-21-Singh-And-The-Two-Circuits.md` holds the full list

## C-041 · GOAL DEFECT — "the ultimate goal is a publishable Substack essay"

**The most consequential correction in the register, because everything ranked below it was
ranked by the wrong criterion. Raised by the principal, not by a verifier.**

- **Killed by:** the principal, 22 Aug 2026, on reading back the goal as this project had recorded it.
- **The dead claim, in the form it circulated:** `CLAUDE.md` §"Output target" — *"**A publishable essay** (set 21 Aug 2026) … It exists to answer one question"* — and `RESEARCH_STATE.md` §0 row A11, *"Open — this is the output target"*. Both were read, correctly, as naming the goal.
- **Why it is wrong.** The ultimate goal is **a comprehensive, fundamental understanding of the nonbank–bank nexus**: all shadow-banking *collateral* and *money-creation* mechanisms, on the Pozsar–Singh frame in which **collateral is as critical as base money in facilitating credit and liquidity creation** (*The Nonbank-Bank Nexus and the Shadow Banking System*, IMF WP No. 11/289, **December 2011**). The essay is an **outcome** of that understanding. Ideas worth further investigation get *flagged*, not folded into an outline.
- **What the error cost, concretely.** §5 was reconciled on 22 Aug into "blocking the essay / next / standing". Under the correct goal that ordering is close to inverted:
  - The three "blocking" items (margin-debt ratio, BEA Table 5.1 opening, five-number verification) are **polish on one worked case**. Real, but outcome-side.
  - **Neither leg of the nexus was on the list at all.** The money leg (institutional cash pools, non-M2 money demand) is recorded as unmeasured at `2026-08-21-Safe-Asset-Share-Reexamined.md:179`; the interlock is not recorded anywhere.
  - **"Nonbank-bank nexus" returns ZERO hits across the entire corpus** (checked 22 Aug, all files including `_research/`). Pozsar appears as a bibliography line, a newsletter-census negative, and an admitted gap — never as an implemented framework. Singh is well covered on **one** of his two contributions.
- **A structural consequence worth more than the correction itself.** Singh's velocity denominator — collateral sourced from primary owners, **$3.3trn at YE2007** in the 2011 paper — *is* the nonbank side of the nexus. `Shadow_Debt_Channel_Map.md:1196` calls it "the weak link" because it "has to be estimated separately". We built the numerator precisely and left the denominator estimated: **we were computing a ratio whose denominator was the actual research object, and filing it as a data-quality problem.**
- **Second structural consequence.** The channel map is nine silos each asked *"is it money creation?"*. The interlock surfaces only in each channel's **"Double-counting risk"** section, as a nuisance to net out. Under Pozsar–Singh a security collateralising three channels at once is not double-counting — **it is the phenomenon**. Those sections are unharvested findings.
- **Correct position:** the goal is A12 (`RESEARCH_STATE.md` §0.0). A11, the essay, is downstream and does not set priority. Before starting any pass, apply the test in §0.0: *does this deepen the understanding of how collateral and money-like claims are created outside the banking perimeter?* "The essay needs it" is not a priority argument.
- **Citation note:** the joint paper is **December 2011**, WP/11/289 — not 2012 or 2013. The 2013 date attaches to Singh's solo *The Economics of Shadow Banking* in the RBA conference volume. State the year only after checking which paper is meant.
- **Still standing at:** nothing — `CLAUDE.md` and `RESEARCH_STATE.md` §0/§1 corrected 22 Aug 2026 in the same pass. **§5 re-ranked in the same pass.**

## C-042 · "The interlock is not double-counting, it is the phenomenon" — stated without the measurement it depends on

**Self-caught, same day, four hours after writing it. The sixth instance of this project's signature error, arriving in a new place.**

- **Killed by:** reading Pozsar, *Shadow Banking: The Money View*, OFR WP 2014-04 — `_research/primary_sources/Pozsar_2014_OFR_ShadowBanking_MoneyView.txt:864`–`:876`; written up at `2026-08-22-Nexus-Primary-Sources.md` §5.
- **The dead claim:** that because Pozsar–Singh make the bank–nonbank interlock the object of study, a security appearing as collateral in three channels at once **is not double-counting but the phenomenon itself**. Written into `RESEARCH_STATE.md` §1.0 on 22 Aug as an unqualified statement.
- **Why it is wrong.** It omits the measurement it is conditional on, and the two cases point opposite ways:
  - measuring **reuse / velocity / chain length** (Singh's object) — the repetition **is** the phenomenon; netting it away destroys the measurement;
  - measuring the **stock of money claims** (Pozsar's object) — the repetition is **exactly the inflation Pozsar nets out by construction**. He states it: his $5trn (2013Q3) / $8trn (2008Q2) figures are narrower than Pozsar et al. (2010) because the earlier measures were **gross, not netting for holdings between intermediaries**, which *"inflated aggregate measures further."*
- **Correct position:** **net for stocks, never net for velocity, and never report one number as though it served both.** State which object is being measured *before* stating whether an overlap counts.
- **Why this is the signature error again.** The four logged instances were all *normalised statistic read as a quantity*; the fifth (C-037) was a net regression coefficient read as gross. This one is **gross-vs-net at the level of a research frame** rather than a figure — the same confusion, one level up, which is why the existing ban patterns could never have caught it.
- **Reinforces:** invariant 8 ("a normalised statistic is not a quantity") now has a companion — *an aggregate is not defined until you say whether it nets*.
- **Still standing at:** nothing — `RESEARCH_STATE.md` §1.0 amended in the same pass, 22 Aug 2026.

## C-043 · "CFS Divisia DM4 is ~$53–55trn of money-like claims outside M2"

- **Killed by:** internal check on receipt of the Gemini retrieval return, 22 Aug 2026 — `2026-08-22-Nexus-WP11289-Read.md` §5.
- **Source of the claim:** external retrieval return (Gemini), item C4, offered as the answer to "total money-like claims outside M2".
- **Why it is wrong:** a **Divisia aggregate is a user-cost-weighted index number, not a simple sum**. Quoting it as a dollar level of money-like claims is **reading a normalised statistic as a quantity** — the error this project has logged five times already (invariant 8). The stated level is also implausible against M2 of ~$21.5trn, and the return's own caveat concedes the weighting difference while still presenting the figure as a quantity.
- **Correct position:** do not use the figure. **CFS Divisia may still be the right pointer** for the underlying question — a broad monetary aggregate that includes repo, CP, large time deposits, institutional MMFs and T-bills — but if it is used, it is used as an **index**, and any dollar level must come from CFS's own published dollar series with its construction stated.
- **Note:** the signature error arrived from **outside** this time. External returns need the same invariant checks as internal passes.
- **Still standing at:** nothing — never entered a findings document.

## C-044 · "$6trn of institutional cash pools, per Pozsar WP/11/190"

- **Killed by:** reading WP/11/190 at source, 22 Aug 2026 — `_research/primary_sources/Pozsar_2011_IMF_WP11190_InstitutionalCashPools.txt:1022`–`:1023`.
- **Source of the claim:** external retrieval return (Gemini), item A3, attributing a $6trn cash-pool benchmark jointly to WP/11/190 and OFR WP 2014-04.
- **Why it is wrong:** **in WP/11/190 the $6trn is households' insured cash balances**, the quantity cash pools are *compared against*. Institutional cash pools in that paper are **$3.5trn at 2011Q1**. The $6trn *cash-pool* figure is OFR 2014-04's, and it is **end-2013**. Two different objects sharing a number, merged into one claim.
- **Correct position:** cash pools ≈ **$3.5trn (2011Q1, WP/11/190)** and **≥$6trn (end-2013, OFR 2014-04)**. Always state vintage and definition. **WP/11/190 alone carries $2.2trn (2007 peak), $1.9trn (2010Q4), $3.8trn/$3.4trn (2007/2010) and $3.5trn (2011Q1) on what appear to be different definitions** — assembling this series is a task, not a lookup.
- **Partly salvageable:** the component split offered alongside is partly real — OFR 2014-04 carries FX-reserve liquidity tranches ~$1.5trn (`:2795`) and corporate cash >$1.5trn (`:2798`). The vintage attribution is the defect, not the whole breakdown.
- **Still standing at:** nothing — caught on receipt.

## C-045 · PROCESS — "the external reviewer confirmed my number" treated as strong evidence

- **Found:** 22 Aug 2026, adjudicating the Gemini retrieval return.
- **What happened.** The parcel supplied figures and asked for verification against the issuing text. Where it did so, the return **gave those figures back unchanged, marked "VERIFIED FROM SOURCE TEXT"** — items B1 (four figures) and D1 (two figures). On independent check the B1 figures are **correct**. But all four appear in the paper's **abstract**, which is exactly where the parcel said they came from, so the claim of *source-text* verification is unproven by the agreement.
- **The evidence that it was not a full-text read:** the return's summary of WP/11/289 **never mentions reverse maturity transformation** — the paper's own section II and the demand-side engine of the entire framework.
- **Correct practice, now binding:** **an external return that confirms a number you supplied is the WEAKEST verdict in the return, not the strongest.** It is unfalsifiable from the outside and indistinguishable from restatement. Weight a return by what it tells you that you did not put in it — a correction, a negative, a concept you had not named. Where confirmation actually matters, verify at source yourself.
- **Corollary for parcel design:** ask for figures to be *derived*, or ask what the source says on a topic, rather than presenting a number for a yes/no. A yes carries almost no information.
- **Still standing at:** nothing — no confirmed-by-agreement figure has been promoted.

## C-046 · "83.7% of the 2023–25 household net-worth gain was equity-linked"

- **Killed by:** Parcel B return plus our own verification, 22 Aug 2026 — `2026-08-22-Parcel-B-Numbers-Return.md` §3.
- **Why it is wrong as stated:** **"equity-linked" is not a category the Z.1 publishes.** It is an analytical composite that has to be constructed, and the construction turns on one choice: whether **pension entitlements** are counted as equity. Table R.101 records the revaluation of the *entire* pension entitlement claim, not its equity slice. Including pensions gives ~83.7%; **excluding them gives ~61.7%.** The 83.7% figure therefore requires treating **100% of pension-reserve holding gains as equity-linked**, defensible only if fixed-income revaluations inside pensions were ~nil across 2023–25.
- **Correct position:** the equity-linked share is a **range of roughly 61.7%–83.7% governed by a definitional choice**, not a measured quantity. If it is used at all, state the pension treatment in the same sentence. **Never ship the bare "83.7%".**
- **Separately, the levels offered in support of it are rejected:** the return built the split on household net worth of ~$163.6trn at YE2025. The Fed's own Z.1 releases put it at **$169.3trn (2025Q1), $176.3trn (Q2), $181.6trn (Q3), +$2.2trn in Q4 ≈ $183.8trn** — roughly **$20trn** higher. Our $39.16trn rise / $31.40trn holding gains stand; the component figures do not.
- **Still standing at:** ~~`Funding_Identity_First_Principles.md:208`~~ (was marked **[rev-V, exact]** — the worst form, a definitional composite asserted as exactly verified), ~~`2026-08-21-Safe-Asset-Share-Reexamined.md:84`~~ — **both annotated 22 Aug 2026. Propagated.** Parcels and the Grok review are allow-listed as places that legitimately pose or refute it.
- **Note on detection lag:** the Grok review of 22 Aug already said 83.7% *"cannot be verified"*, and the claim was still standing as fact in two documents hours later — including one that called it *exact*. **C-040 again:** a caveat raised inside a document does not propagate until it is registered here.

## C-047 · CONTESTED, NOT KILLED — gross private saving, $4,815bn (2019) → $6,384bn (2025)

**Logged as contested rather than dead: two external reviewers give different values for the same BEA line and we have verified neither.**

- **Raised:** 22 Aug 2026 — `2026-08-22-Parcel-B-Numbers-Return.md` §2.
- **The conflict:** Grok (21 Aug, accepted and propagated into our documents) gives **$4,815bn → $6,384bn**. Gemini (22 Aug, BEA Table 5.1 line 20 as net private saving plus private CFC) gives **$5,066.0bn → $6,153.3bn**. Gemini's is internally consistent across its own lines, which demonstrates coherent arithmetic, not correct inputs.
- **What is unaffected:** **C-030 stands.** The kill rests on gross private saving having *risen* substantially, and both sources agree it did — +$1.09trn or +$1.57trn depending on whose figures. Do not read this entry as reopening the funding question.
- **What is affected:** the **specific pair** is quoted in `RESEARCH_STATE.md` §1.1, `CLAUDE.md` and the Gemini review parcel. **Mark it contested wherever it appears and do not add new uses** until read off BEA NIPA Table 5.1 directly. That lookup is §5 item K6 and it is now a lookup, not a rewrite.
- **Still standing at:** ~~`RESEARCH_STATE.md` §1.1~~ — **marker added 23 Aug during housekeeping; it had NOT been added when this entry was written on 22 Aug, despite the entry saying it should be** (C-040 again: the register said "to carry a marker" and nobody carried it). `CLAUDE.md` no longer quotes the pair.

## C-048 · "The six RTOs filed show-cause responses on 17 August 2026" — the filings do not exist

**The most serious external-source failure in this project. Fabricated events, with correctly-formatted citations, that I adjudicated as findings before checking.**

- **Killed by:** direct verification in FERC eLibrary, 22 Aug 2026 — `2026-08-22-Parcel-C-FERC-Return.md` §6.
- **The dead claim:** that all six RTOs filed show-cause responses on 17 Aug 2026; that none proposed a transferable flexible-load service class; that five defended firm-service-only tariffs and PJM proposed an interim flexible track. Supplied with per-RTO document titles, filing dates and accession numbers.
- **What actually happened:** **PJM filed an abeyance motion on 28 July; MISO and the MISO Transmission Owners on 3 August. FERC GRANTED both on 14 August 2026 — three days before the deadline — holding the proceedings in abeyance for 90 days** (`20260814-3059` PJM, `20260814-3058` MISO). **No show-cause responses were filed.** Rehearing of the June order was denied by operation of law on 20 August (`20260820-3006`).
- **The accession numbers, checked one by one:** the **June** ones are correct — `20260618-3105` is genuinely the PJM §206 order and `20260618-3111` the notice. The **August** ones are real accession numbers pointing at unrelated dockets: `20260817-5188` is **Texas Gas Transmission**, Dearborn County Lateral Project, **CP26-536**; `20260817-5214` is **Wawa, Inc. v. Colonial Pipeline**, **OR24-4**. Two of two tested were wrong.
- **Why the obvious check fails:** `elibrary.ferc.gov/eLibrary/filelist?accession_number=X` returns a **byte-identical Angular shell for any input** — a deliberately bogus `99999999-9999` differs from a real accession only in a 10-byte Cloudflare nonce. **HTTP 200 on an eLibrary link is not evidence of anything.**
- **My own error, which is the part worth remembering:** I adjudicated this return before verifying, and wrote that the six-way negative was *"robust — no plausible reading of the filings turns six noes into a yes."* **There were no filings.** I also built a "lesson about trigger design" on top of a PJM position that was never taken.
- **Correct position:** the proceeding is **stayed until roughly 12–13 November 2026**. The three pre-registered panel positions **cannot resolve** — the resolving event was deferred, not decided. The Druckenmiller first leg did **not** fire.
- **What does exist and is unread:** the **30-day informational reports**, filed ~20 July under the same orders — e.g. MISO `20260720-5204`, with third-party comments already on them (NGSA `20260810-5108`). These are on resource adequacy, not tariff transferability, and are the only substantive RTO submissions in the proceeding to date.
- **Still standing at:** `2026-08-22-Parcel-C-FERC-Return.md` §§2–4 — **preserved deliberately** under a correction banner as the record of what was claimed and how it failed. Allow-listed.

## C-049 · PROCESS — never ask an external model to supply the artefact whose absence you just named

- **Found:** 22 Aug 2026, as the direct cause of C-048.
- **What happened.** I told Gemini its FERC return had **no accession numbers**. It returned accession numbers — in the correct FERC format, with the correct convention (**3xxx** for Commission issuances, **5xxx** for eFiled submissions), sequential where sequential was plausible and scattered where scattered was plausible. Every surface property was right. Only opening them revealed they pointed at gas pipelines and oil-tariff litigation.
- **Why this is worse than ordinary C-045 confirmation.** Naming the gap tells the model **exactly what shape of artefact will satisfy you**. Confirmation bias in a supplied *number* is detectable by re-derivation; a supplied *citation* is detectable only by opening the document, and every intermediate check — format, convention, plausibility, HTTP status — passes.
- **Correct practice, now binding:**
  1. **Ask where to look, not for the reference.** "Which docket and date range would carry this?" is safe; "give me the accession numbers" invites manufacture.
  2. **A citation is verified only when the document at the reference is the document claimed.** Resolving is not verifying. For JS-driven portals behind a CDN, a 200 means nothing — check the rendered content.
  3. **Distinguish source classes.** EDGAR serves real documents at stable URLs, which is why the guarantee-stack pass's 43 accession references were sound. FERC eLibrary requires a rendered browser session. Know which kind you are citing.
- **Still standing at:** nothing — this is a practice rule.

## C-050 · Eight constructed references in the D1 scouting return — over a self-audit asserting none

- **Killed by:** item-by-item verification, 22 Aug 2026 — `2026-08-22-Parcel-D1-Scouting-Return.md` §3; FRED checked from a live browser session, primary-source texts grepped directly.
- **The dead items, each checked:** (1) "Acharya–Chauhan–Rajan–Steffen, *Liquidity Dependence and the ON RRP Drain*, **NBER 31688**" — 31688 is Chinoy–Nunn–Sequeira–Stantcheva on zero-sum thinking; (2) "Afonso–Cipriani–La Spada, **NY Fed SR 1068**" — 1068 is Cattaneo–Crump–Wang, *Beta-Sorted Portfolios*; (3) "Gorton–Ross–**Roussanov**, *The Moneyness of Private Claims…*, JFE 2022" — real paper is Gorton–Ross–Ross, *Making Money*, NBER w29710; (4) KVJ 2015 pages 471–500 — actual 571–600; (5) a 19-word "exact quote" at "WP/11/190 §III.B p.15" that does not occur in the text; (6) "OFR 2014 **Table 1 (p. 15)**" — no Table 1 exists, the "15" is a footnote mark on *Figure 1: The Money Matrix*; (7) FRED IDs **`TBACMB`, `H41RESPALFOPHAORRP_N.D`, `WRBAL`, `NONFINCP`, `DFFINCP`, `FORFINCP`** — all 404; (8) "Pozsar approximated the FX liquidity tranche as TIC bills + foreign repo pool" — the phrase "liquidity tranche" does not occur in WP/11/190.
- **Also wrong, every one:** the "values seen" — ON RRP given as ~$250–350bn in Aug 2026 against **FRED `RRPONTSYD` = $0.2bn on 2026-08-21**; reserves and large time deposits likewise off. The "(seen, unverified — re-pull)" label kept all of them out of the record — **that rule worked and stays.**
- **Also wrong on substance:** P3 places T-bills in *public shadow money*; OFR 2014 places bills <7d in **public money** and 7d–1y in **public money-like claims** (`Pozsar_2014…txt:843`), with public shadow money = overnight government repo + CNAV government MMF shares (`:783`). **This is the object of the D1 test and must be taken from our own text.**
- **Correct position:** use the return's *publishers and tables*, which are right throughout; re-derive every series ID; take every definition from `_research/primary_sources/`; treat the 2022–26 literature as **unlocated**. The one real modern pointer is the Liberty Street post *"Dropping Like a Stone: ON RRP Take-up in the Second Half of 2023"*.
- **Still standing at:** `_research/D1_Scouting_Return_gemini_ondisk.md` — Gemini's own on-disk file (it did write it, into the project root), moved and bannered 22 Aug; preserved deliberately, allow-listed. *Note: it landed at top level where an agent would read it as findings — external returns must be filed under `_research/` on receipt.*

## C-051 · PROCESS — a self-audit checklist is a completeness device, not evidence of truth

- **Found:** 22 Aug 2026, as the direct lesson of C-050.
- **What happened.** Parcel D1 was built with a fixed skeleton, mandatory rows per ID, and a self-audit the model had to fill before stopping — the principal's request for a "clear goal condition". It delivered: **26 of 26 rows present**, checklist fully ticked, including *"No reference in this file was constructed rather than found."* At least eight were.
- **Why this matters.** The goal-condition design **solves the omission problem and does nothing for the fabrication problem** — and can make fabrication *worse*, because a mandatory row with no real answer gets filled with a plausible one rather than left blank. The return's fabrications cluster precisely where a required row demanded something the model could not find: the 2022–26 citations, the page-precise quotes.
- **Correct practice, now binding:**
  1. Keep the skeleton and required IDs — they work for coverage.
  2. **Never cite the self-audit as verification.** It is the model grading its own homework.
  3. For every required row, **make DOES NOT EXIST / CANNOT DETERMINE the *easy* answer** — state explicitly that a blank row costs nothing and a constructed one is fatal. (D1 said this in R3; it was not enough on its own.)
  4. **Stop asking scouting parcels for series IDs, page numbers or quotations.** Ask for publisher + table + series *name*; we find the ID and read the page. Three returns (A, C, D1) now show IDs and quotes are where construction happens.
- **Still standing at:** nothing — practice rule. Apply to the D2 parcel.

## C-052 · "US uninsured deposits ~$7.1trn at 2025Q4"

- **Killed by:** FDIC BankFind API, field `DEPUNINS`, aggregated over all 4,411 reporting institutions, pulled 22 Aug 2026 — `2026-08-22-D1-Bill-Supply-vs-Shadow-Money.md` §2.
- **Source of the dead figure:** the omnibus Gemini return (item C1, "~$7.12trn as of 2025Q4 / early 2026"). Never promoted into a findings document; registered so it cannot be.
- **Correct position:** **$8,138bn at 2025Q4; $8,373bn at 2026Q1.** The series troughed at ~$7.2trn in mid-2024 after the 2023 bank failures (from $8.8trn at YE2021) and has since recovered. **Always state the base date** — the 2021→2026 change is negative, the 2023→2026 change is +$1trn.
- **Still standing at:** nothing.

## C-053 · "Registered funds hold perhaps $2–4bn of the $27bn Beignet notes; PIMCO's registered funds hold $0.7bn, so ~96% of its $18bn sits in separate accounts"

**My own claim, made 22 Aug in D2 and repeated in the 23 Aug briefing. Killed by a full census the same day.**

- **Killed by:** the SEC bulk N-PORT structured dataset for 2026Q2 (`FUND_REPORTED_HOLDING.tsv`, 5.35m rows, periods ending ~31 Mar 2026), which had been sitting downloaded in the agent scratchpad since 21 Aug and was found during housekeeping on 23 Aug. `2026-08-22-D2-Who-Holds-The-AI-Paper.md` §9.
- **Correct position:** registered funds hold **$9.81bn of Beignet Investor LLC 6.581% 2049 (CUSIP 076912AA2) across 324 filings / 146 registrants — 36% of the $27bn.** **PIMCO Funds alone $6.23bn** (one series $4.23bn at 1.88% of NAV), plus PIMCO ETF Trust $177m, PIMCO VIT $104m, PIMCO Managed Accounts $87m → **PIMCO registered ≈ $6.6bn, roughly a third of its reported $18bn** — not 4%. BlackRock registered ≈ $0.86bn of its reported $3bn. **The daily-redeemable share of the Hyperion debt is a material minority (~one-third), not "small."** The D2 verdict — long-money funded, run risk not the frame — survives on the remaining ~64%, but the characterisation in D2 §4, RESEARCH_STATE S-D2 and the 23 Aug briefing was wrong and has been amended.
- **Why the sample failed:** EDGAR full-text search returns 100 hits per page; I paginated to 400 of 1,497 and parsed all "PIMCO"-named hits among them — the PIMCO Funds filings carrying the large positions were beyond page 4. **A full-text-search sample is not a census.** The bulk dataset is the census, it is free, and it was already on disk.
- **Still standing at:** ~~`2026-08-22-D2-Who-Holds-The-AI-Paper.md` §1/§4~~ (amended §9, banner at §4), ~~`RESEARCH_STATE.md` S-D2~~ (amended), ~~`Report/Where_The_Money_Isnt_Briefing_2026-08-23.html` + the published artifact~~ (corrected). **Propagated 23 Aug.**

---

## C-054 · Nine constructed identifiers in the D3 scouting return — and every dollar figure destroyed in transit

**External (Gemini Flash 3.7, `_research/D3_Scouting_Return_gemini_ondisk.md`, written 22 Aug 09:39 to the Dropbox share root, located 23 Aug). Checked item by item at the reference on 23 Aug — `2026-08-23-D3-Cash-Pools-vs-Asset-Management-Structure.md` §7.**

- **Killed by:** Crossref lookups of every DOI and every title; HTTP checks of every URL; the BIS publication list; our own WP/11/190 / WP/11/289 record.
- **The dead identifiers, each checked:** (1) Graham–Leary cited as JF 73(4) 1675–1739, DOI `10.1111/jofi.12696` — that DOI is Gârleanu–Pedersen; the real paper is *The Evolution of Corporate Cash*, RFS 31(11) 4288–4344 (2018). (2) Begenau–Palazzo cited as "*Firm Cash Holdings and the Rise of the Tech Sector*", JFE 140(2), DOI `…2020.12.007` — that DOI is Ranaldo–Somogyi on FX; real: *Firm Selection and Corporate Cash Holdings*, JFE 139(3) 697–718 (2021). (3) Chernenko–Sunderam cited as RFS 29(8) 2087–2128, DOI `hhw023` — that DOI is Bottazzi–Da Rin–Hellmann; real: NBER w22391 (2016), still unpublished. (4) "Jiang, Li and **Sun** (2021), *Mutual Fund Liquidity Management: Evidence from Form N-PORT*, JF 76(4)", DOI `jofi.13028` — that DOI is Barber et al. on pandemic research productivity; nearest real paper is Jiang–Li–**Wang**, *Dynamic Liquidity Management by Corporate Bond Mutual Funds*, JFQA 56(5) 1622–1652. (5) Ma–Xiao–Zeng volume/pages right, DOI `hhac013` wrong (Van Doornik et al.; real `hhac007`). (6) "**CGFS Papers No 69**, *Derivatives Markets, Central Clearing and Liquidity* (2023)" — No 69 is *Macroprudential policies to mitigate housing market risks*. (7) "BoE Financial Stability Paper No 51, the 2022 LDI crisis" — URL 404; existence not established. (8) Pozsar's *Institutional Cash Pools* cited as **IMF WP/11/289** with the wp11289.pdf link — it is **WP/11/190**; 289 is Pozsar–Singh (C-044, reversed). (9) d'Avernas–Vandeweyer titled "*Treasury Yields and Institutional Cash Pools*" (ECB WP / SSRN 2021) — the real paper is *Treasury Bill Shortages and the Pricing of Short-Term Assets*, JF 79(6) 4083–4141 (2024).
- **Also destroyed, every one:** the dollar values. The file was written through a shell that expanded `$1`, `$2`… to nothing — "$1.3trn" arrived as ".3trn", "$20trn–$25trn" as "trn–trn". The *(seen, unverified — re-pull)* rule had already excluded them; the lesson is that a model writing to disk must be told to use a literal-safe path (heredoc with a quoted delimiter, or a file-write tool), or the numbers are gone.
- **Also wrong:** the self-audit line *"Every EXISTS row has a URL I opened / verified"* — the BoE URL and the SFOS URL (`/data/sfos.htm`; real page `/data/sfos/sfos.htm`) both 404. C-051 holds.
- **Correct and useful:** the SLATE dates (28 Sep 2026 / 29 Mar 2027 — verified by us first); CPMI-IOSCO d125 and BCBS-CPMI-IOSCO d537; OFR WP 15-17; Pozsar FMII 22(5) 283–318; ISLA / RMA / FIA / ISDA / ICI / SEC PFS as publishers; the two negatives (no open reinvestment-composition series; no direct AUM-vs-cash-pool regression in the literature). **And one row that changed what we know:** AM3's pointer to the OFR Hedge Fund Monitor — the return did not say the monitor has an open API; we found it, pulled it, and the hedge-fund leg of D3 is now measured (D3 §8).
- **Pattern.** Identical to C-050: retrieval right, construction in the identifiers. This time the parcel had **not** asked for DOIs, volumes or pages (C-051 rule 4) — the model supplied them anyway, and they were wrong at a higher rate than the D1 return. **Rule, binding from 23 Aug:** an identifier that arrives *unasked* in an external return is treated as absent. Every citation is re-derived from author + title via Crossref before its summary is read; every URL is fetched before it is called a source. Parcels now say so explicitly and ask for a literal-safe write.
- **Still standing at:** `_research/D3_Scouting_Return_gemini_ondisk.md` — the raw return, preserved verbatim and allow-listed; never cite it. The original drop at the Dropbox share root is Gemini's and is left there. `_research/D3_Scouting_Return_gemini_summary_pasted.md` — the principal's paste, same identifiers, same status.

---

## C-055 · The N3 collateral scouting return — constructed URLs throughout, template-filled CCP attributes, two invented papers

**External (Gemini Flash 3.7, `_research/N3_Collateral_Scouting_Return_gemini_ondisk.md`, 23 Aug 19:27). Verified row by row by fourteen fetch-and-report agents the same evening — `2026-08-23-Parcel-N3-Collateral-Return.md`; raw observations `_research/N3_verification_results_2026-08-23.json`.**

- **Killed by:** fetching every URL; finding the real pages; downloading the latest disclosure file from every CCP; Crossref and publisher lookups for every citation.
- **Dead, each checked:** (1) **K1**, all eleven CCP sub-rows carry the same four attributes — "XLSX, PDF · archive YES · earliest 2015 Q3". Formats wrong for nine (CME and ICE ZIP; LCH, OCC, Eurex XLSX only; DTCC one combined workbook). Earliest quarter wrong for four: **OCC 2021 Q1; JSCC a rolling five quarters; LCH Ltd 2020 Q1; LCH SA 2019 Q2.** URLs wrong for five: LCH ×2 404, Eurex 404, DTCC ×2 are corporate "about" pages. (2) **K2** CCP Global URL 404 (real: `ccp-global.org/pqd`); FIA "2019–2026" and "membership-gated database" wrong — it is free from 2015 Q3 with a public API. (3) **S1** every URL (risk.net 404, IMF index pages, centralbanking 404) and most titles ("Pledged Collateral and Financial Plumbing" chapter, "Pledged Collateral and Quantitative Tightening"). (4) **S3** ISLA, RMA, OFR URLs all dead; "OFR Reference Paper Series" is WP 16-08. (5) **R1** BIS `sftdata.htm` 404. (6) **R2** both ESMA URLs 404; "subsequent annual editions", "Section: Collateral and Re-use Dynamics", "EUR 10trn" — one edition exists (Apr 2024), it defers re-use to future work, the figure is €9.8tn. (7) **R3** values — NCCBR "$2–2.5trn" (OFR: ~$5trn), "cross-border 25%" (OFR: ~half). (8) **R4** DTCC and OFR URLs constructed. (9) **L1 #5** "Aguiar, Biais, Crassard, *Collateral Reuse in Euro Area Financial Markets*, ECB WP 2023" — **no such paper**; Jank–Moench–Schneider is not JFE; Fuhrer et al. is SNB WP 2015-02, not 2016-01. (10) **L2 #3** "Avalos, Ehlers, Eren, *Hedge funds' Treasury cash-futures basis trades and financial stability*, BIS QR 2023" — **constructed**; URL is a CP/CD primer; real item is Box A, Avalos & Sushko. **L2 #6** "Hauser, *From sunshine to stormy weather*, BoE 2023" — **no such speech.** **L2 #2** title constructed (real: *Sizing hedge funds' Treasury market activities and holdings*); **L2 #4, #5** author lists wrong (real: Glicoes–Iorio–Monin–Petrasek; Barth–Beltran–Hoops–Kahn–Liu–Perozek, 15 Oct 2025).
- **What was right, and used:** every publisher; all three negatives (no official re-use aggregate anywhere; no broker-side rehypothecation aggregate; ESMA re-use deferred); the existence of all eleven CCP disclosure programmes; the pointers that, once verified, opened four series we now hold — FIA's IM API, DTCC's sponsored CSV, Singh & Goel WP/19/106 Table 2, OFR's NCCBR publications. The dollar-sign rule and the no-identifier rule held.
- **Pattern, fourth time (A/C, D1, D3, N3):** publishers right, specifics constructed, mandatory rows filled with the same plausible filler. **The verification fan-out — one agent per row group, every URL fetched, files downloaded — is now the receipt procedure for any external return.** It found the FIA API and the DTCC CSV, which the return did not report and a single reader would not have found.
- **Still standing at:** `_research/N3_Collateral_Scouting_Return_gemini_ondisk.md` — raw, verbatim, allow-listed; never cite.

## C-056 · "FIA's CCP Tracker is a member dashboard, not a pullable feed" — my own claim, 23 Aug afternoon

- **Killed by:** the K2 verification agent, 23 Aug evening — `2026-08-23-Parcel-N3-Collateral-Return.md` §2.1. The tracker is **free, no login**, its charts read a public JSON API (`fiadataapi.azurewebsites.net/api/Data/GetQuarters | GetEntityOnQtr | GetInitialMargin`, page-embedded key) carrying PQD 6.1.1 for 15 CCPs, Q3 2015 → Q1 2026. Pulled; cross-checked against CME's own file.
- **How I got it wrong:** I fetched the landing page (HTTP 200), saw a login block in the nav, and wrote "member dashboard" into D3 §5 and RESEARCH_STATE §5 D3 without opening a chart page. A landing page is not the thing.
- **Correct position:** free; `bin/pull_series.py --only fia`; series `ccp_im_required_15ccp_fia_bn` in `data/series.tsv`. FICC is not in the set — use DTCC's own workbook for the Treasury-repo clearing fund.
- **Still standing at:** ~~`2026-08-23-D3-Cash-Pools-vs-Asset-Management-Structure.md` §5~~ (amended, strike-through + §9), ~~`RESEARCH_STATE.md` §5 D3 status~~ (amended). Propagated 23 Aug.

---

## C-057 · The D8 Treasury-clearing scouting return — every URL constructed, a launch that had not happened, two invented titles, and a monthly series declared non-existent

**External (Gemini Flash 3.7, `_research/D8_Clearing_Scouting_Return_gemini_ondisk.md`, 23 Aug 20:33). Verified by seven fetch-and-report agents the same evening — `2026-08-23-Parcel-D8-Clearing-Return.md`; raw `_research/D8_verification_results_2026-08-23.json`.**

- **Killed by:** fetching every URL; SEC's rulemaking page, clearing-agency list and CA-1 notices; CMESC's own August 2026 SEC filings; ICE's press releases and statistics workbook; DTCC's hub, charts and press releases; FEDS Notes and OFR blog indexes; publisher site searches; Crossref.
- **Dead, each checked:** (1) **All twelve URLs** given for M1, M2, V1 (first), V2 (second), V3 (both), P1 (three of four), P2 (all three) are 404s or index pages. (2) "CME cash clearing scheduled Q2 2026; repo Q2/Q3 2026" — CME said "launch expected in Q2 2026" on 2 Dec 2025; **as of 4–13 Aug 2026 CMESC "currently does not have any Members or Users"** (34-106037, 34-106131); no cash/repo split was ever stated. (3) "ICE Treasury clearing: consolidated revenue figures in quarterly investor disclosures" — 1Q26/2Q26 releases mention CDS clearing only. (4) "ACS volume growing 47 percent year-over-year in July 2026" — in none of DTCC's releases; constructed. (5) "ACS Triparty Service approved January 2026" — SEC order 34-104492 is **22 Dec 2025**; 7 Jan 2026 is DTCC's announcement. (6) Margin-separation relief to 30 Sep 2025 attributed to the extension final rule — it is a separate exemptive order (34-102486). (7) "No continuous downloadable daily/monthly time series" for GSD totals — **DTCC publishes a monthly GSD series from January 2001** (value compared; net obligations created), scraped and archived. (8) **P1 "data used" lines, 4/4 constructed** (Liberty Street uses OFR cleared-repo data, not DTCC/MMF filings; Monin uses Form PF only, not COT/TIC; Hempel–Kahn–Shephard use FOCUS reports, not FR 2004; TMPG is working-group/OFR-pilot based, not a member survey); two slugs/dates wrong. (9) **P2 #1 Clarus *CCP Initial Margin and Client Clearing Trends in US Treasury Markets* (Mar 2026) — no such post. P2 #3 ISDA *Cross-Margining and Capital Efficiencies in Cleared US Treasuries and Repos* (May 2026) — no such paper.** P2 #2 fuses SIFMA's *Done-Away Model Design Considerations* (15 Dec 2025) with its separate *Central Clearing Pulse Survey* (10 Nov 2025). (10) P3's "structural explanation" — analysis the parcel forbade; wrong on mechanism (no migration because the other CCPs were **not live for repo**, not because volumes were "unpublished"); mixes series ("USD 3.0trn end-2025" is a point spike, "2.4–2.5trn mid-2026" is an ADV). (11) FICC PQD "Q1 2016" start — 2015 Q3.
- **What was right, and used:** the mandate dates (13 Dec 2023 rule; 25 Feb 2025 extension; **cash 31 Dec 2026, repo 30 Jun 2027**, unchanged since); the FICC service descriptions; the negatives on CME/ICE/ACS volume publication; the SEC registrations of CMESC (1 Dec 2025) and ICC (30 Jan 2026); SIFMA's done-away MTSCA (30 Jul 2026); TMPG's May 2025 white paper; the existence of the two FEDS Notes and the Liberty Street post; the P3 negative. The R4 no-template rule held (CCP rows differ); dollar-sign and no-identifier rules held.
- **What it missed that the verification found:** **ISDA-Actrix US Treasury Repo Market Clearing Indicators** (monthly since Jun 2026 — the one industry data series that answers the question); DTCC's monthly GSD series; the CMESC "no Members or Users" filings; the 2026 SEC exemption orders; OFR's Jan/Feb 2026 clearing blogs; the TBAC May 2026 charge.
- **Pattern, fifth time.** Publishers right, specifics constructed, self-audit fully ticked over twelve dead URLs. Receipt procedure (C-055) stands; its yield this time was the question's answer.
- **Still standing at:** `_research/D8_Clearing_Scouting_Return_gemini_ondisk.md` — raw, verbatim, allow-listed; never cite.

---

## C-058 · RETRACTED — this entry was itself wrong. The claim it killed was correct.

> **RETRACTION, 24 Aug 2026 (same day).** C-058 killed the 23-Aug figure "MMFs hold **$9.4bn** of the
> alt-ABCP programmes: Chesham $7.2bn, Bennington Stark $1.5bn, Mountcliff $0.7bn" and replaced it with
> "Chesham $2.8bn / aggregator $17.6bn". **The original figure was right and the replacement was wrong.**
> The definitive census — all 325 August filings, all 44,512 positions, no name filter, no category filter
> (`bin/census_nmfp3_all_positions.py`; data `data/vintages/nmfp3/nmfp3_ALL_positions_2026-07-31…csv.gz`) —
> gives at 31 Jul 2026: **Chesham $7.159bn, Bennington Stark $1.543bn, Mountcliff $0.698bn, total $9.400bn.**
> The 23-Aug claim matches to three decimal places. **Nothing was wrong with it; my correction was the error.**
> Method defect registered as **C-059**. The struck text below is preserved as the record of the mistake.
> Lesson recorded in `CLAUDE.md`: *a correction is a claim and gets the same verification as a finding.*

~~**My own figure, 23 Aug (FT harvest §2). Superseded by a full census 24 Aug.**~~ *(false — see retraction above)*

- **Killed by:** a complete one-month N-MFP3 census (all 325 filings filed Aug 2026, 0 errors, every matched position report-dated 2026-07-31; `bin/census_nmfp3.py`, raw rows `data/vintages/nmfp3/`).
- **Correct position (31 Jul 2026, excluding sponsor support):** **Chesham $2.8bn**; Bennington Stark $1.5bn; Mountcliff $0.7bn; and — with the sponsor→programme map verified from the Grok D8b return — the aggregator complex in MMF hands is **$17.6bn across seven families** (Northcross 5.0, Chesham/BSN 2.8, Overwatch 2.7, Nearwater 2.6, Ridgefield 2.3, Bennington Stark 1.5, Mountcliff 0.7), plus $5.8bn of JPMorgan collateralized-paper vehicles.
- **Why the old number died:** the 23 Aug pass searched Jul–Aug filings together (June and July month-ends) with a name-limited full-text search, and its script was lost to the scratchpad sweep before being archived — the method is unrecorded and the figure unreproducible. **A point-in-time stock must come from one filing month; a search over two filing months is not a stock.** (Same family as C-053: a search sample is not a census.) **Settled 24 Aug, same day: the June-data census (325/325 July filings) puts Chesham at $2.85bn at 30 Jun — the $7.2bn was not a decline and not month-mixing alone; it was simply wrong.**
- **Role corrections carried with it (verified 24 Aug):** BSN is Chesham's **Investment Advisor** (BNY Mellon administrator; Moody's 2 Mar 2022) — not sponsor. Bennington Stark's sponsor is **The Liberty Hampshire Company**; Guggenheim Treasury Services is **administrator**. Mountcliff is a **20 Gates Management** programme. Say the roles, not "sponsor" for all three.
- **Still standing at:** ~~`2026-08-23-FT-Harvest-ABCP-Conduits-And-Equity-Repo.md` §2~~ (correction banner added 24 Aug), ~~`RESEARCH_STATE.md` D8 line~~ (amended). Propagated 24 Aug.

---

## C-059 · PROCESS — a matching rule is a hypothesis about the data, and two of mine were wrong in opposite directions

**Found 24 Aug 2026, on the day C-058 was written and retracted. The cause of the false correction.**

- **What happened.** Three passes over the same 325 N-MFP3 filings gave three different answers for the same quantity:
  1. **23 Aug, full-text search on three names** over two filing months → "$9.4bn". Method unrecorded (script lost to the scratchpad sweep), so it *looked* the least trustworthy — and was in fact correct.
  2. **24 Aug morning, `bin/census_nmfp3.py`**: a hand-written map of programme-name regexes, all categories, one filing month → Chesham $2.78bn, aggregator $17.6bn. **Blind spot: abbreviated spellings.** Filers write `CHESHAM FIN LTD / CHESHAM FIN LLC` as well as `CHESHAM FINANCE`; the pattern `chesham finance` missed $4.38bn of the same programme. It also missed every programme not already on the list — the list covered **41%** of MMF-held ABCP.
  3. **24 Aug afternoon, `bin/census_abcp_all.py`**: no name filter, but `investmentCategory == "Asset Backed Commercial Paper"` → total $101.2bn across 139 issuers. **Blind spot: filer categorisation.** ~$3.1bn of the same aggregator programmes' paper is filed by funds under *Non-Financial Company Commercial Paper* (Chesham alone: $1.19bn).
- **Correct method, now the only one used:** `bin/census_nmfp3_all_positions.py` — every position, no name filter, no category filter, written to a local CSV (44,512 rows) that is then aggregated **locally**, so a matching rule can be revised without re-fetching 325 filings. Both narrower scripts are kept with deprecation headers pointing here.
- **The general rule.** C-053 was *a search sample is not a census*; C-058's own error was *a guessed name-list is not a census*; and *a category filter is not a census either*. **A matching rule encodes a hypothesis about how the data is written down, and it must be tested against the raw text before its output is trusted** — cheapest test: pull everything once, filter locally, and check a known-large name for spelling variants.
- **The second-order rule, which is the expensive one.** C-058 was registered, propagated to `RESEARCH_STATE.md`, the D8b document and `data/series.tsv`, and reported to the principal — all within about an hour, with the confidence the register is supposed to reserve for verified things. **A correction is a claim. It gets the same verification as a finding, and preferably a different method from the one that produced the number it kills.**
- **Still standing at:** nothing — all four propagation sites corrected 24 Aug.

---

## C-060 · TERMINOLOGY — "source collateral" names the NUMERATOR in our channel map and the DENOMINATOR in Singh

- **Found:** 25 Aug 2026, building N3 — `2026-08-25-N3-Singhs-Denominator-Reconciled.md` §0.
- **The collision.** Singh's velocity = *"the total pledged collateral received by the large banks, divided by the primary sources of collateral"* (WP/19/106). **"Sources" is his denominator** — what hedge funds and securities lenders pledge *in*. `Shadow_Debt_Channel_Map.md` uses "DEALER SOURCE COLLATERAL" for the **statutory footnote figure**, which is his **numerator** ($6,907bn US-six FY2025). Same phrase, opposite ends of the same ratio.
- **Not a wrong number.** The channel map's own source table already says the footnote is *"the numerator of Singh's velocity measure"* and its caveats are right (the sum double-counts across dealers by construction; correct for chain length, meaningless as a stock). Only the findings prose is mislabelled — but that is the half a later reader quotes.
- **Correct usage from here:** the footnote figure is **"pledged collateral received"** (numerator). **"Source collateral" / "primary sources"** is reserved for the denominator — hedge funds via prime brokerage plus real-money securities lending. Never use "source" for both in one document.
- **Still standing at:** ~~`Shadow_Debt_Channel_Map.md` findings prose~~ — relabelled 25 Aug; the source table needed no change.

---

## C-061 · "Collateral velocity has kept falling — to roughly 1.5 in 2026" — retracted to a range after adversarial review

**My own v1 finding (S-N3, 25 Aug), reported to the principal the same day. Downgraded 28 Aug by the Grok N3R review, whose load-bearing citation survived full verification — `2026-08-25-N3-Singhs-Denominator-Reconciled.md` §6.**

- **Killed by:** Singh himself, in a **free** article we had failed to find: *"measured velocity has remained almost constant at around 2.0"* for the past decade (Risk.net, 12 Jan 2026, read in full by our own agent; text archived `_research/primary_sources/Singh_2026-01-12_Risknet…txt`). Plus the review's valid structural attack: the 0.60 bracket position carrying Form PF Q43 onto Singh's hedge-fund source is a free parameter fitted on 2013–17; at the securities-only floor our own inputs give ≈2.0.
- **Correct position:** velocity is in **[≈1.5, ≈2.0]** — Singh's 2.0 (hand-collected top-20-bank data we cannot see) as primary, our 1.55 fitted-bracket figure as the alternative; the bracket position is **unidentified** in 2026. **What survives every reading, including the reviewer's own alternative: velocity is flat at best, and primary sources grew hugely (+76% on Singh's own implied numbers; ×2.7 on our securities-only floor) — the collateral leg grows by more source collateral, not faster re-use.** The mechanism conclusion stands; the sharp number does not.
- **Two process lessons:**
  1. **A paywall is a property of the URL, not the article.** Risk.net and Central Banking are one publisher and cross-post. We held the Central Banking headline from 23 Aug, recorded it "paywalled", and stopped; the identical article was free on the sibling site the whole time, and it contained the author's own contradiction of our finding. Check the sibling site before recording a piece as gated.
  2. The finding was **marked v1/unreviewed and sent for external attack before wider propagation** — this is the system working: the exposure was one chat report and one derived series row, both now corrected. Contrast C-058, which propagated in an hour.
- **ADDENDUM, 29 Aug (principal's challenge — accepted).** The v2 symmetric range was itself methodologically weak: the bracket position is *signable* from known mechanisms, and signing it (N3 doc §8: repo borrowing alone exceeds the whole cash-like bucket; downward wedges sum to ≤$0.88trn of $3.29trn) gives a **floor of 0.73 — above the fitted 0.60**. Corrected verdict: **velocity ≈1.3–1.5 on the signed proxy chain; Singh's 2.0 demoted from "primary" to a conflicting direct measurement carrying a named ~$2.5–3trn reconciliation gap** (nettings/exclusions his concept must make for 2.0 to hold — askable of the author directly). v1's error: unsigned fitted point. v2's error: authority-anchored symmetric interval. **Rule: an interval is only honest after the mechanisms have been signed and sized.**
- **Still standing at:** ~~S-N3~~ (v3), ~~N3 doc §3~~ (struck, §6+§8), `data/series.tsv` (velocity row superseded 29 Aug). Propagated 29 Aug.

---

## C-062 · The D6 stablecoin return — a stale headline despite live search, fabricated precision on TBAC, a wrong statutory cadence, and an 80%-constructed official-literature section

**External (Gemini 3.7 Flash, pasted 29 Aug; preserved `_research/D6_Stablecoin_Scouting_Return_gemini_pasted.md`). Verified by three agents against statute text, both TBAC decks, FSOC/OFR annual reports, issuer pages and the live DeFiLlama API — `2026-08-29-D6-Stablecoins-Fifth-Cash-Pool.md` §3.**

- **Dead, each checked:** (1) "Total stablecoin market cap USD 168bn, USDT 69%, USDC 21%" — a **pre-2024 training-data snapshot**; live: **USD 311bn, 59%, 24%**. Search was ON: **the search toggle does not guarantee searched answers** — stale numbers can arrive with fresh-looking "latest date seen" fields. (2) "Weekly and quarterly reserve reporting" under the GENIUS Act — the statute says **monthly** (zero hits for weekly/quarterly in PLAW-119publ27; FSOC 2025 corroborates). (3) TBAC "USD 120–135bn holdings" and "USD 500–900bn scenarios" — **fabricated precision**: the documents state ">$120bn" and "~$900bn" (with ~$1.0tn 2028E); no 135 or 500 exists in either PDF. (4) NYDFS register "lists Paxos and Gemini" — Gemini yes, **Paxos absent** as fetched. (5) Paxos custodian "State Street" — confirmable partner is **Standard Chartered**. (6) **T2 official literature 4/5 constructed** — real Fed/NY Fed/BIS/ECB stablecoin authors combined into trios that never co-published, under invented titles (e.g. a Martin/McAndrews/Zhang Liberty Street post that does not exist; McAndrews left the NY Fed a decade ago). L1: 1 constructed, 3 with fabricated titles/co-authors on real papers, 2 verified.
- **What was right, and used:** PL 119-27 / 18 Jul 2025; the ≤93-day reserve restriction and the interest ban (quoted from the statute); rulemaking still proposed-only; the TBAC documents themselves; issuer transparency portals; Tether's exact redemption terms; Cantor custody; DeFiLlama as the only continuous aggregate. The **verification recovered more than the return supplied**: Circle Reserve Fund at USD 60.7bn (31 Jul 26), OFR-AR-2024's $92bn+$29bn split, FSOC sections, and the real literature (BIS WP 1270 et al.).
- **New failure mode for the register:** stale-training-data quantities presented alongside "latest date seen: August 2026" — plausible-freshness. **Rule: any market-size or share figure in an external return is presumed stale until pulled live**; the pull is usually one free API call.
- **Still standing at:** `_research/D6_Stablecoin_Scouting_Return_gemini_pasted.md` — raw, allow-listed; never cite.

---

## C-063 · "The Fed's bill purchases took ~69% of net bill issuance YTD" — a window-mismatched ratio, and the monetization reading built on it

**My own figure (D1 §9, 23 Aug; repeated in N2c and S-N2c) and framing ("at the margin, the government is again financed by base-money creation"). Broken by the N2cR review, 30 Aug; verified end-to-end — `2026-08-29-N2c-The-Funding-Closure.md` §7.**

- **Killed by:** matched-endpoint recomputation on our own vintaged series plus the review's H.4.1/DTS arithmetic (all four endpoints verified at source). The 69% divided a numerator through **19 Aug** by a denominator through **31 Jul** — and August's bill wave (~$252bn) was privately absorbed.
- **Correct position:** matched Dec-31→end-Jul: **63.6%**; matched →26 Aug: **44.4% and falling**. Composition (July MPR, verified verbatim): of ~$250bn of bill purchases through early July, ~$160bn RMP and ~$90bn agency-principal reinvestment; assets +$150bn, reserves +$54bn. Jefferson (16 Jan 2026, verbatim): RMPs *"are not quantitative easing… no implications for the stance of monetary policy."* **The Q1 fact stands (Fed +$156bn, largest single Z.1 buyer that quarter); the monetization narrative is retracted.**
- **Rule (extends "a correction is a claim"):** **a ratio's two windows are part of the claim** — publish both end-dates with every ratio, and recompute on matched endpoints before any ratio crosses into a findings doc.
- **Still standing at:** ~~D1 §9~~, ~~N2c §2/§5~~, ~~S-N2c~~ — all struck/amended 30 Aug.

## C-064 · "Bank loans to NDFIs grew +$625bn in 2025 — the largest live money-creation engine, bigger than the whole ABCP market"

**My own finding (N2c §3, 29 Aug). Broken in size by the Fed's own H.8 Notes on Data, verified line-by-line, 30 Aug.**

- **Killed by:** five 2025 reclassifications INTO the NDFI line — $245.1bn (1 Jan), $69.4bn (2 Apr), $69.8bn (2 Jul), $9.1bn (1 Oct), $7.4bn (31 Dec) = **$400.8bn** — moved from C&I/consumer/other-loan categories after the Dec-2024 Call Report change. Not new credit.
- **Correct position:** **organic 2025 growth ≤ ~$224bn** (upper bound; no clean weekly organic bridge exists), against +$200bn (2024, clean) and +$106bn (2023, clean): **a steady ~$100–220bn/yr engine on a real $2.0trn stock** — significant, not explosive. The ABCP comparison is separately retracted as a stock-vs-flow category error. Composition (FDIC Feb-2026, verified): 57% credit intermediaries, 24% capital-call PE lines, **$987bn (42.9%) of commitments undrawn** — revolver-heavy liquidity support. The May-2026 FSR's own $261bn vendor reclassification shows the commitment series carries the same measurement problem.
- **Rule, binding:** **before reading any Fed level change as a flow, read the release's Notes on Data for breaks.** H.8, Z.1 and Y-14 all reclassify; a level jump at a January 1 is a definition until proven a flow.
- **Still standing at:** ~~N2c §3/§5~~ (struck), ~~S-N2c~~ (amended), `data/series.tsv` `bank_loans_to_nondepository_fis_bn` (annotation row added: level valid, 2025 flow contaminated).

## C-065 · "The corporate sector is the only structural net buyer of equities; the saving-rate paradox resolves as an identity"

**My own conclusion (N2c §4, 29 Aug), self-flagged as vulnerable in the review parcel and duly broken. Verified against the Fed's own F51.1.t, which reproduces to the decimal, 30 Aug.**

- **Killed by:** the net-purchases block of Z.1 F51.1.t: households **+$984.9bn (2024) / +$863.5bn (2025)**, ETFs **+$840.4 / +$958.5**, rest of world **+$185.3 / +$643.7**, while nonfinancial corporates were net **sellers as holders** (−$324.2 / −$197.6) even as they retired −$398/−$304bn of net issuance. Negative net issuance is not sector demand — I conflated the issues block with the purchases block.
- **Correct position:** buybacks remain a large, debt-funded structural bid that shrinks the float; the biggest measured *purchasers* are the household row (which is the Z.1 **residual** and contains domestic hedge funds — the Fed's instrument notes say household Treasury/equity purchases are computed residually), ETFs (with the ETF-share/underlying double-layer), and a **large, growing foreign equity bid ($644bn in 2025; $144.7bn in June 2026 alone per TIC)** — the genuinely under-weighted row in my account. And per the Fed's revaluation framework, no accounting identity sets the price: the A11 "resolves as an identity" phrasing is retracted; what the identity resolves is the *flow* consistency, not valuation.
- **Still standing at:** ~~N2c §1/§4/§5~~ (struck), ~~S-N2c~~ (amended), the 29-Aug chat report to the principal (corrected in the 30-Aug report).

---

## C-066 · "Basis-trade collateral mostly enters the dealer off-FICC and exits on-FICC/triparty; the dealer is the ONE re-use point"

**My own D10 v1 gloss (30 Aug), broken by the D10R review (Grok) the same day using my own published numbers plus OFR Brief 26-03. Re-verified in-house before striking.**

- **Killed by:** the OUT-side venue arithmetic (MMF-facing 41.0% vs uncleared bilateral 37.3% — no "mostly"), and by entity-typed OFR 26-03: primary dealers net-borrow $986.4bn (H2-2025), so triparty OUT partly finances dealer inventory (net UST position $436.4bn, 19 Aug); and hedge funds lend $1,007.0bn — a re-use-capable node the "one re-use point" phrasing erased.
- **Correct position:** entry half stands (uncleared bilateral = 56.8% of collateral IN); the exit side is spread across venues; the dealer is the one re-use point *on the two-leg MMF–dealer–HF chain only*, a near-tautology with limited evidential weight for system velocity.
- **Lesson:** venue is not counterparty. FR2004 tells you WHERE, OFR 26-03 tells you WHO — use them as a pair, never infer WHO from WHERE.
- **Still standing at:** ~~D10 §1/§3~~ (struck in place), the 30-Aug chat report to the principal (corrected in the D10R report).

---

## C-067 · "US-six permitted stock ~7.9trn vs Singh's entire global 7.5trn end-2017 — numerator doubled-plus on US banks alone"

**My own D10 v1 comparison (30 Aug), broken by D10R: wrong perimeter — Table 2's $7.5trn is GLOBAL, not US.**

- **Killed by:** WP/19/106 Figure 3 (both panels: US AND European banks; visual read of the 2017 US bars ≈ $3.4trn, confirmed by me from the on-disk PDF p.15) and Singh's Jan-2026 Risk.net figures ($13trn global, US banks "over half", JPM ≈ $1.8trn ≈ our measured 1,771.0).
- **Correct position:** US five-name panel 2017 ≈ 3.4trn → Jun-2026 ≈ 7.5trn = ×2.2; global 7.5 → 13trn = +73%; US share 45% → ~57%. Positive yield: Singh's numerator object is the PERMITTED-to-repledge stock (WP/19/106 p.14 wording), which answers one of the three Singh-ask questions from the source.
- **Lesson:** before comparing your number to a published aggregate, state both perimeters in the same sentence; a comparison whose two sides have different perimeters is not a comparison.
- **Still standing at:** ~~D10 §3~~ (struck in place), the 30-Aug chat report (corrected in the D10R report).

---

## C-068 · "TIC MFH Cayman is ~$272bn (spot-checked live)"

**My own spot-check (30 Aug, N2a-S verification), broken the same day by my own TIC retrieval agent following the state-the-contradiction rule.**

- **Killed by:** `ticdata.treasury.gov/Publish/mfh.txt` is FROZEN — a March 2023 Treasury notice discontinued it, but the URL still serves HTTP 200 with the old table (Last-Modified header even shows 2026). I read the frozen file's OLDEST column (Jan-2022, 272.1) as "latest". Live MFH is `slt_table5.txt`: Cayman = $453.1bn at Jun-2026 (grand total $9,299.0bn).
- **Lesson:** an HTTP 200 with plausible content is not liveness. For any hand-maintained government file, check the report date INSIDE the file against today before reading any column as current — and know which end of the row is "latest" before quoting it.
- **Still standing at:** ~~N2aS verification doc Q4~~ (struck in place), the 30-Aug chat report on the N2a-S adjudication (corrected in the N2a build report).

---

## C-069 · "Bank financing of the Cayman complex doubled while its visible Treasury holdings stood still (+2.8%)"

**My own N2a §2/§3 framing (30 Aug), broken by the N2aR review (Grok) the same evening: a stacked-window comparison, and a "candidate mechanism" that was already a measured Fed result.**

- **Killed by:** the matched window — TIC Cayman UST 283.7bn (Dec-2022, table3b) → 460.1bn (Mar-2026) = +62%, against LBS financing ×2.0 over the same quarters; and Barth et al. (Fed FEDS Note, 15 Oct 2025): real Cayman hedge-fund UST holdings $1.85trn end-2024, +$1trn since 2022, with the TIC undercount MEASURED at ~$1.4trn. Holdings boomed; the ledgers cohere once the measured repo hole is applied. Bonus triangulation: the CPIS-vs-SHL gap is debt-only (equity matched to 1.4%) and equals 1.36trn ≈ the same hole.
- **Lessons:** (1) a comparison's two windows are part of the claim — same as C-063, now twice; (2) before framing a cross-ledger divergence as a puzzle, search for whether officialdom has already measured it — the Fed had, ten months earlier.
- **Still standing at:** ~~N2a §2/§3~~ (struck in place, §7 carries the rebuild), the 30-Aug evening chat reports (corrected in the N2aR report).

---

## C-070 · "z_k is flat at 19.05% once the Fed is counted as a wholesale borrower — the nexus did not expand as a share of money"

**My own N2b headline (31 Aug), broken the same day by the N2bR review (Grok) — and broken twice over: an endpoint artefact AND a category error that inverted the conclusion. Every figure re-measured in-house before striking; Grok's recomputed series matched mine to the decimal at five of six dates.**

- **Killed by (i) the endpoint artefact:** the Fed-inclusive ratio is not flat at all — 15.32% (2021-12), 17.85% (2022-12), 19.99% (2023-06), 19.05% (2023-12), 18.76% (2024-12), 20.03% (2025-06), 19.52% (2025-12), 19.46% (2026-06), 19.05% (2026-07). It moves ~4.7pp across the period. My two chosen endpoints both happened to sit at 19.05%. I flagged this exact risk in the parcel and still published it as a finding.
- **Killed by (ii) the category error:** counting the Fed as a z_k borrower is wrong on the definition. WP/11/289's z_k is non-M2 funding *of banks*; the ON RRP funds the **central bank**, not a bank. The Fed-inclusive measure is therefore not z_k at all, and building the headline on it inverted the result.
- **Also killed: the "78.8% of private-repo growth is the RRP drain" attribution.** It is the ratio of two stock changes of similar size, not an attribution. Over the same window MMF Treasury holdings rose **+$1,183.1bn** — more than the entire $961.9bn drain — and MMF AUM rose $2,010.6bn. The destination of the RRP cash is not pinned by this arithmetic.
- **Correct position:** the private measure is the right one, and it **more than doubled**: z_k 9.09% (2021-12) -> 15.88% (2023-12) -> 19.45% (2026-06). That rise *is* the Pozsar-Singh mechanism — the asset-management complex shifting its funding from the central bank to private dealers while M2 grew far less — which my conclusion inverted into "the nexus did not expand". It has since plateaued (~19.3-19.5% through 2025-12/2026-06) because the RRP is empty: the handoff is complete.
- **Lesson — third occurrence, now a standing rule.** C-063 (ratio windows), C-069 (stacked windows), C-070 (endpoint selection). **Never report a change between two dates without plotting the intermediate points first.** Two endpoints that agree are evidence of nothing until the path between them is seen.
- **Still standing at:** ~~N2b section 3 and its section 0/2 framing~~ (struck in place, section 7 carries the rebuild), the 31-Aug chat report (corrected in the N2bR report).

---

## C-071 · "JPM's Dec-2025 permitted stock ($1,771.0bn) matches Singh's published 'around $1.8 trillion' — so his numerator is the permitted line"

**My own cross-validation (30 Aug, D10 §3 and the Singh-ask doc), caught by me on 31 Aug while preparing to put it in front of Singh himself. An ANACHRONISM: I matched his January-2026 statement to a figure that was not public until February 2026.**

- **The error:** Singh's Risk.net piece is dated 12 Jan 2026. JPM's 31-Dec-2025 collateral figure first appeared in its FY2025 10-K (filed Feb 2026) and in the Q2-2026 10-Q comparative column. He could not have seen it. Same for Barclays: its FY2025 20-F was filed 10 Feb 2026.
- **Correct position — the conclusion survives and is BETTER supported.** The latest JPM disclosure available to him was the Q3-2025 10-Q (filed 4 Nov 2025, acc 0001628280-25-048859): **collateral permitted to be sold or repledged = $1,829.9bn at 30 Sep 2025** (repledged $1,439.9bn). That matches "around $1.8 trillion" to **0.5%** — a closer fit than the anachronistic figure, on the permitted line, at a date he actually had. His numerator is the permitted-to-repledge stock, and his figures are current rather than carried forward.
- **Lesson — a new class, alongside the window family (C-063/069/070).** **A source's figures can only be checked against vintages that existed when it was written.** Before matching our number to someone's published claim, establish the publication date and the disclosure calendar, and use the latest vintage available *to them*. Filing dates are part of the claim.
- **Still standing at:** ~~D10 §3 cross-validation~~, ~~2026-08-30-Singh-Ask.md~~, ~~_research/D10R_verification_2026-08-30.md~~ — all three corrected in place 31 Aug. Note the D10R review itself relayed this figure approvingly; being confirmed by the judging lane did not make it right, because both of us made the same vintage assumption.

---

## C-072 · "JPM's Sep-2025 permitted stock matches Singh's 'around $1.8 trillion' to 0.5%" and "Figure 3 is on p.15 of WP/19/106"

**Two precision errors about Singh's OWN material, both caught by the SB1 verification (Grok in Cursor, read-only) on 31 Aug while checking the briefing draft — i.e. caught in the document that was about to be sent to him.**

- **The arithmetic:** |1,829.9 − 1,800| / 1,800 = **1.66%**, not 0.5%. I stated 0.5% and propagated it to C-071, N3v4 §2b, the Singh-ask doc, the state file and a series note. What is actually true, and is the point worth making, is that **1,829.9 rounds to $1.8trn**, and that the repledged line ($1,439.9bn) is nowhere near his figure — the rounding and the non-match are the evidence, not a spurious precision.
- **The pagination:** WP/19/106's own table of contents places Figure 3 on printed **p.14** ("Pledged Collateral Received by U.S. Banks and European Banks ...... 14"). I cited p.15, which is the PDF viewer page; printed p.15 opens Table 2. Citing a paper's figure by viewer page to its author is exactly the error that reads as carelessness.
- **Addendum (SB1 claim 48):** my perimeter question conflated two sources. WP/19/106 Box 1 names 10–15 dealers plus recent Canadian entrants and Nomura; "the top 20 banks" is the January 2026 article's phrase. Asking whether "the top-20 perimeter is still the WP/19/106 list" presumes they are the same list. Question rewritten.
- **Lesson:** when a number will be shown to the person who produced the original, recompute the comparison arithmetic explicitly rather than reaching for a percentage, and cite by the source's OWN pagination, not the viewer's.
- **Still standing at:** ~~N3v4 §2b~~, ~~2026-08-30-Singh-Ask.md~~, ~~RESEARCH_STATE.md~~ — all corrected in place 31 Aug.

---

## C-073 · "Our rebuilt panel independently reproduces Singh's published statement that US banks are over half the global pool"

**My own N3v4 §2 claim (31 Aug), refuted the same day by SB1. A logic error, and it was the briefing's central credibility claim.**

- **Killed by:** the share is 3,351.4/7,500 = 44.7% and 7,460.0/13,000 = 57.4% — **our numerator over HIS denominator**. A ratio computed with his own global pool cannot be independent evidence for his statement about that ratio. The word "independently" did the work and was not earned.
- **Correct position:** what is independent is the **numerator** — five banks' permitted-to-repledge stocks rebuilt from their filings, ×2.23 over 8½ years. Combined with his published global figures, that numerator implies a US share consistent with "over half". Consistency is the claim; reproduction is not.
- **Lesson:** before writing "independently", name the inputs on both sides of the ratio and check that none of them came from the party whose claim is being tested.
- **Still standing at:** ~~N3v4 §2~~ (struck in place); the three briefing drafts in `_research/singh_briefing_drafts/` carry the overstatement and must not be sent as-is.

---

## C-074 · "His 2017 table is reproduced by counting securities and other in full plus 32% of the cash-like bucket — his method is reconstructable"

**My own back-test (3 Sep), reported to the principal in the same turn, and broken by me the next turn when I ran the other four rows. FOURTH member of the single-observation family: C-063 (ratio windows), C-069 (stacked windows), C-070 (endpoints), and now a one-row calibration.**

- **Killed by:** running the back-test across every row of Table 2 that Form PF covers. The implied cash-like share is **not constant — it wanders 71% (2013), 50% (2014), 64% (2015), 68% (2016), 32% (2017); spread 39pp.** The 32% was the outlier, not the convention.
- **Why it wanders, and what replaces it — a better finding.** His hedge-fund source series grows almost linearly at about 5% a year (annual steps +2.7, +5.3, +5.0, +4.8; **sd 1.01pp**) for a cumulative **+18.9%** over 2013–17. Form PF collateral posted by qualifying hedge funds over the same years grows **+39.1%** with genuinely lumpy steps (+10.3, +0.6, +5.3, +19.1; **sd 6.84pp**). Dividing a smooth series by a lumpy one is what produces the wandering share. **The two are not the same object measured two ways: his moves like a trended estimate, ours like a measurement.** Table 2 cites "Risk Management Association; Singh (2011); updates to include Canadian banks" — not Form PF.
- **What this does to the letter:** it improves it. The question is no longer about gross-versus-netted conventions but: *is the hedge-fund source series a measured aggregate or a trended estimate, and if measured, from what?* That is specific, fair, answerable in two sentences, and not derivable from public data.
- **Lesson — the standing rule was too narrow.** "Plot the intermediate points before reporting a change between two dates" (C-070) was written for time series. It applies to **any calibration inferred from a single observation**: a share, a ratio, a conversion factor. Compute it everywhere it can be computed before calling it a convention. I even wrote "one year, one row... repeat across them before the letter goes" into the caveats — and let the headline stand anyway. **A caveat is not a substitute for running the check.**
- **Still standing at:** ~~N3v4 §6~~ (rewritten in place), the 3 Sep chat report (corrected in the next turn's report).

## C-075 · "Five-bank Jun-26 utilization ~84%, ~$7.9trn permitted stock" — Wells Fargo excluded, fix never registered

**My own D10 v1 table (30 Aug), missing Wells Fargo. Caught the same day by the D10R review (Grok) and folded in place at D10 §6 item 2 — but as an inline amendment, never given its own CORRECTIONS.md entry. Exactly the failure this project's diagnosis names: a changing fact acquired a second hand-written home (the superseded list in RESEARCH_STATE.md §5) while the enforcement layer never moved with it.**

- **Killed by:** the D10R review flagging WFC's absence from the dealer repledge-stock table; verified in-house against WFC's own Jun-26 and Dec-25 10-Qs (`_research/D10R_verification_2026-08-30.md`).
- **Correct position:** **six-bank Jun-26 utilization 83.2%** (6,149.6 / 7,389.7 permitted/repledged) — not five-bank 84.0% (6,789.4 / 5,700.7) and not "~$7.9trn permitted stock" (the five-bank figure — itself separately mis-compared to Singh's GLOBAL pool at a different perimeter, C-067). WFC alone: permitted 600.3 / repledged 448.9 (Jun-26); 469.2 / 309.3 (Dec-25). Growth including WFC: permitted +19.3%, repledged +21.5% H1-2026 (ex-BAC, rounding risk: +17.6% / +19.4%) — the step-change finding is unchanged in kind, only the level moves.
- **Rule:** an amendment folded in place inside a findings document is not a registered correction. A figure that changes needs a `## C-0NN` heading here before the ban list can catch its stale copies anywhere else — an in-place edit with no entry is invisible to `bin/check.sh`.
- **Still standing at:** RESEARCH_STATE.md:517 (the superseded numbered list; deleted under S4, 11 Sep housekeeping).

---

## C-076 · "Li & Lin's market-level multiplier, bias-corrected, is about $5"

**Mine, 11 Sep, in `2026-09-11-P3-papers.csv` and the P3 write-up** — a literature row that attributed to Li & Lin a
bias-corrected market-level multiplier of roughly $5, which made the $5 centre look independently supported.

- **Killed by:** the P3R adversarial check (Grok in Cursor, 12 Sep) reading the paper at source; `_research/P3R_verification_2026-09-12.md`.
- **Correct position:** the paper reports naive market-level estimates of 25.73 (full sample) and 32.85 (a subsample),
  a bias of 27.9 with CI 11.5-44.2, and concludes the measure should not be used to estimate market-level price
  multipliers. Its level-wise estimates stand: 1.73 idiosyncratic, 3.12 granular style, 6.98 coarse style.
- **Rule:** a number attributed to a paper must be quoted from the paper, not inferred from what the paper implies.
- **Still standing at:** nowhere — `_research/2026-09-11-P3-papers.csv` and `2026-09-11-P3-Price-Impact-Multiplier.md` were fixed on 12 Sep.

---

## C-119 · C-109's "structural disagreement between independently compiled Fed series" — the gap was a term the check left out

**Mine. Written into C-109, CLAUDE.md and the ANSWER on 22 Sep and told to the principal as a finding that "dwarfs the error model"; P1 had framed the same gaps as "genuine non-reconciliation" on 11 Sep. Overturned 23 Sep by an agent sent to test it, and re-derived by the supervisor before acceptance.**

- **Killed by:** the Z.1 identity itself. Change in level = flow + revaluation + **other volume changes** (the Fed's `FV` series: breaks in source data or definition, reclassifications). P1's check compared level-change-minus-flow with revaluation **and had no OVC term.** The "gap" is the missing term.
- **Verified.** Where the Fed publishes OVC — sector net worth — the full identity closes: households, 299 quarters, **max residual $1 million**; drop OVC and it reaches **$835bn**. Re-derived by the supervisor from `S1M_r.csv`. For rest of the world, sector OVC in 2024:Q2 is **$319.4bn** against an equity "gap" of **$318.5bn** that quarter (supervisor-verified); 2021:Q4, $338.8bn against $322.1bn.
- **Why it cannot be closed exactly.** The Fed publishes revaluation per instrument but OVC only per sector: `FV153064105`, `FV263064105` and `FV103064103` do not exist (FRED returns 404). At the equity-instrument level the explanation is strongly supported, not provably exact.
- **Why households and RoW, not NFC.** The Fed states household equity purchases are *calculated residually*: any reclassification of another sector's holdings — the June 2026 split of hedge funds out of the household line, for instance — lands in the household residual as a break that is neither price nor transaction. RoW is periodically re-benchmarked (mechanism not confirmed in a Fed document). NFC's holdings line is small and not a residual; its OVC is near zero. So residual-ness *does* matter here, but not as C-109 said: the residual absorbs other sectors' **reclassifications**, not their measurement **errors**.
- **What survives from C-109:** its first half — the whole-economy 93.1% is uncheckable at that aggregation — plus a refinement: `ΔLevel − Flow` is revaluation **plus** OVC, so "93.1% revaluation" is strictly "everything that is not a transaction".
- **What falls:** "structural disagreement between three independently compiled Fed series"; "it dwarfs the error model"; "attach the household reconciliation gap to any use of the 94.6%/44.6% flow figures" — OVC does not enter flows. C-110 (the 94.6% denominator instability) is independent and stands.
- **The trap, now in CLAUDE.md:** a check that omits a term of the identity finds gaps of hundreds of billions that are not errors. Before calling a disagreement real, make sure the identity is complete. The 2021:Q4 figures were also only the largest inside P1's window — the full household history shows $720.5bn at 2012:Q4.
- **Still standing at:** `2026-09-11-P1-Equity-Net-Buyers.md` item 4 and summary, `CLAUDE.md`, the ANSWER's §2 denominator box, the published page — all corrected in place.

---

## C-118 · ANSWER §3a: shadow banking was "a handoff, not fresh money" — stated for the window when N4 established it for 2024 only

**Mine. Found 22 Sep in the supervisor's own pass during the E-007 audit and reported to the principal that day — then not written into the vault until 23 Sep. The source is more careful than the summary.**

- **What is wrong.** N4 establishes the handoff for **2024** (~$136bn of new wholesale capacity once the ON RRP drain is stripped: "an order of magnitude too small"). For the **full 2024–26 window** N4 says the opposite: raw wholesale growth ($1.8trn against $3.1trn of purchases) is the same order of magnitude and **does not fail** the smallness test, and stripped of the handoff it is still about a quarter of purchases — *"large enough to remain in the picture as a ceiling."* The row's headline dropped the full-window half.
- **Correct position.** A handoff in 2024; **not ruled out** over the window, where it remains a ceiling. The attribution ban (no share of purchases can be assigned to nonbank money) is unchanged and correct.
- **Still standing at:** `2026-09-17-ANSWER` §3a, rewritten in place.

---

## C-117 · "B6 is the one no budget fixes" / "genuinely permanent — 386 years"

**Mine, ANSWER §4 and the text of C-092. Found 22 Sep in the supervisor's own pass, reported to the principal that day, not landed until 23 Sep.**

- **What is wrong.** The closure is `measured spread 1.32bp × M`, against measured noise of 111bp. **M≈1.9 is Hartzmark–Solomon's, borrowed from the literature.** C-091's own text carries the sensitivity: at the top of the published envelope, **M=9.4, the requirement is 16 years against the 11.7 available.** So the closure is permanent at the central multiplier and about four years of data away at the envelope top — a factor of twenty-four in required sample across the published range. "Arithmetic, not access" is right; "permanent" and "no budget fixes" are HYPOTHESIS conditional on M.
- **A tension worth naming.** C-077 banned borrowing a multiplier from the literature *to attribute*. Borrowing one *to size a test* is legitimate — but the closure then inherits the parameter's uncertainty, and the headline carried the 386 without the 16.
- **Correct position.** Closed on free data at every M in the envelope. Its re-open trigger is a number, like JVZ's: **about 2030**, if M sits at the envelope top.
- **Still standing at:** `2026-09-17-ANSWER` §4, rewritten in place. C-092's "genuinely permanent" stays as written (append-only) and is superseded here.

---

## C-116 · "Lease commitments of $1,122.9bn, about 13× the $86.2bn of live guarantees"

**The Guarantee Stack's section heading (22 Aug), carried into ANSWER §3a by me. Found 22 Sep in the supervisor's own pass, reported to the principal that day, not landed until 23 Sep.**

- **What is wrong.** The two sides are filtered in **opposite directions**. The leases are *signed but not yet commenced* — all future. The guarantees are *live only*: the same document puts a further **$142.1bn** in "signed but not yet effective" (NVIDIA Portsmouth $105bn, Meta El Paso ~$13bn, Alphabet ~$24.1bn) and prints the like-for-like total itself: **TOTAL CONTRACTED $228.3bn**. Future against future, `1,122.9 / 228.3 = 4.9×`, not 13×. A comparison across measurement bases — Analytical Invariant 2, violated by division instead of addition.
- **What survives.** The conclusion — the financing that matters is off balance sheet — is untouched; $1.1trn dwarfs either denominator. Conclusion survives, precision does not.
- **Still standing at:** `2026-08-22-Guarantee-Stack.md` — **four** places, not one: the heading, line 59, line 119, and the document's own summary at line 8 — plus a fifth in `_research/2026-09-11-Channel-Map-Gaps.md`, found only by a vault-wide sweep for the ratio in Python, which said "13x *larger*" and slipped past the ban pattern for "13x bigger"; found by searching for the ratio rather than the wording (the C-103 rule, applied) — and `2026-09-17-ANSWER` §3a. All corrected in place.

---

## C-115 · "Bank credit to the AI build-out is ~$150bn outstanding / ~$450bn committed" / "~$1.2trn of AI-company debt" as a measured denominator

**Carried from D2 (22 Aug) into RESEARCH_STATE, Grok's W2 draft (22 Sep) and the supervisor's own proposed W2 verdict (23 Sep). Caught 23 Sep by re-reading the primary source before adopting that proposal — which D2 had cited as "fetched and read" with no URL and no copy.**

- **Killed by:** Chicago Fed Insights, February 2026, *Tail Risk for Banks Posed by Investments in Generative Artificial Intelligence* (Cohen, Killen, Lau), now archived at `data/vintages/chicagofed_ai_tail_risk_2026-02/`.
- **What is wrong, two ways.** (1) The $450bn/$150bn is large-bank **C&I exposure to AI-adjacent *industries*** — an industry classification covering AI software and infrastructure companies, data-centre construction and loans secured by data centres — and the same article says it stood at **~9% of commitments, ~$250bn, in 2015**, before the build-out. The AI-era increment is **~$200bn of commitments over a decade**, and the article gives no 2015 outstanding figure. D2 quoted the definition correctly and omitted the baseline, so every reader since has taken $450bn/$150bn as build-out lending. (2) The **~$1.2trn** is **JPMorgan analysts' estimate**, relayed by the Chicago Fed, presented *in contrast* to bank debt. An estimate by others, not a measurement.
- **Correct position.** Bank credit is the one channel that creates deposits, and it is **real but smaller than its headline**: credit to the build-out itself is some unmeasured part of the $150bn. The ratio to issued debt (~1/8) is the article's own comparison and holds as a statement about industry exposure. Carry both limits wherever either number is quoted. Context from the same source: outstanding AI-adjacent exposure averages ~0.8% of bank total assets and ~9% of tier 1 capital, with delinquencies in line with the portfolio.
- **Why it matters.** It nearly went into the ANSWER as "bank credit is material, ~12%, and ~$300bn of undrawn lines is the sharpest fragility candidate" — the supervisor's own wording, one check from adoption. **A source cited without a URL or a copy cannot be re-read, and a figure that cannot be re-read accumulates interpretation it never carried.**
- **Still standing at:** `2026-08-22-D2-Who-Holds-The-AI-Paper.md` (three places), `RESEARCH_STATE.md`, the W2 brief — all marked in place. The W2 note itself is revised.

---

## C-114 · "The OFR API route recorded in the 24 Sep calendar row does not resolve; the recorded slips may be wrong-route artefacts"

**Mine. Written into `CALENDAR.tsv` during the 21 Sep housekeeping pass, and repeated to the principal on 22 Sep in the "what's next" answer. Refuted by Grok on 22 Sep; re-verified by the supervisor 23 Sep.**

- **Killed by:** `curl 'https://data.financialresearch.gov/hf/v1/series/full?mnemonic=FPF-BORROW_REPO_SUM'` (generic user agent) returns the series: **53 observations, last 2026-03-31 = $3,243bn, `last_update` 2026-06-04**. The route works and Q2 is genuinely unpublished.
- **What is wrong.** The 21 Sep "route check" queried **`/v1/series/timeseries?mnemonic=…`** — a different API namespace (the short-term funding monitor, whose dataset list is `all/nypd/mmf/repo/fnyr/tyld`) — got "Invalid mnemonic", and concluded that **the route recorded in the row** was broken. **It never ran the recorded route**, which sat in the same row in plain text with `/hf/` in it. Then it speculated that three genuine non-publication slips "may be wrong-route artefacts", and I passed that speculation to the principal as a finding.
- **Correct position.** The recorded route was right all along. The 11, 17 and 19 Sep slips were real non-publication.
- **Why it matters.** This is an error *inside the verification step*: "I checked" when what was checked was something else. It is the same shape as the standing rule that VERIFIED is a claim, not evidence. **When re-checking a recorded command, copy and run the recorded command verbatim — never a reconstruction of it.**
- **And the repair lost the trail.** The 22 Sep edit that fixed the row cut its text field at **exactly 1,000 characters, mid-word**, deleting the tail of the 11 Sep original and the 21 Sep note with it. The false claim therefore vanished instead of being corrected next to itself, which is the one thing this file exists to prevent. No script in `bin/` caps fields at 1,000 — only that row was affected. Tail restored 23 Sep from the text as read on 22 Sep.
- **Still standing at:** nowhere. `CALENDAR.tsv` carries a `[C-114]` pointer in place of the deleted note.

---

## C-113 · "`bin/check.sh --all` is green" / the integrity stamp's counts, for every correction from C-100 onward

**The gate's own defect, live from the moment C-100 was registered on 22 Sep. Found the same day — by reading a handover stamp that looked wrong, **not** by any guard. No guard could have found it.**

- **What is wrong.** Six live code sites hardcoded `C-0[0-9]+`, which matches `C-001`–`C-099` and nothing above. Crossing one hundred corrections silently disabled: **M7** (a `[C-1NN]` banner with no heading), **M8** (two headings sharing a `C-1NN`), the integrity stamp's **count** and **max**, the **corrections-since-last-stamp** delta, and **`--latest`**.
- **Measured, not asserted.** The old pattern saw **59** banners across the vault; the correct one sees **67** — **8 invisible**. `--latest` returned C-095–C-099 as "the newest corrections" while C-112 existed. The stamp wrote `corrections=99 max=C-099` against a true **112 / C-112**, so **the one check designed to catch a torn tree would itself have passed a torn tree.** And a new agent running the documented first action would have been told the programme's most recent ruling was four days old.
- **Fixed** at all six sites (`C-0[0-9]+` → `C-[0-9]+`); pre-fix copy at `_research/check.sh.pre-C100-fix-2026-09-22.bak`. Verified both ways: before, `--latest` stopped at C-099 and the stamp read 99/C-099; after, C-112 and 112/C-112.
- **Why it matters, and it is the same lesson as C-103 on the same day.** The guard's numbering assumption **was itself an untested claim**, sitting inside the machinery that exists to catch untested claims. E-007 applies to the tooling, not only to the findings. And note the trigger: a **threshold crossing**. No test of the current state could ever have caught this — only asking what the code assumes. **When a counter approaches a width boundary, grep for the width.**
- **Still standing at:** nowhere — `bin/check.sh` is fixed and re-run.

---

## C-112 · "Pensions were net sellers, and private-sector DC net contributions have been negative every year since 2013"

**Mine, ANSWER §3. Found 22 Sep by the E-007 audit. Two measurements of different things in one sentence.**

- **What is wrong.** Leg one is **Z.1 holder-side equity transactions, 2024:Q1–2026:Q2** (state/local DB −$463.9bn, federal −$67.8bn, private incl. 403(b) −$27.7bn — all directly reported, all confirmed negative). Leg two is **DOL/ICI administrative data, all asset classes, DC plans only, 2013–2023** — a plan cash-flow concept. Different sector, different instrument, different window. And **RET1 says so about its own number**: *"the net flows below are NOT a measure of money entering or leaving the equity market... both legs are contaminated by transfers."* That caveat does not survive into the sentence that pairs them.
- **Correct position.** State leg one. Cite leg two separately, with RET1's caveat attached, or not at all.
- **Still standing at:** `2026-09-17-ANSWER` §3, split in place.

---

## C-111 · "Rotation, not new demand" stated as a finding

**Mine, ANSWER §3. Found 22 Sep by the E-007 audit.**

- **What is MEASURED.** ETFs +$2,460.9bn against mutual funds −$2,009.0bn, 2024:Q1–2026:Q2; the selling offsets **81.6%** of the buying. That number is real and reproduces.
- **What is NOT measured.** That these are **the same dollars**. Sector-level netting cannot distinguish true wrapper-switching from two unrelated flows that happen to offset in aggregate — foreign buyers creating ETF shares while unrelated domestic holders liquidate mutual funds to spend would produce the identical table. Z.1 has no account-linked data, so this is **UNSETTLED on free data**, permanently.
- **Correct position.** "ETF buying and mutual-fund selling offset by 81.6%, consistent with rotation" — MEASURED offset, HYPOTHESIS mechanism. Not "rotation, not new demand."
- **Still standing at:** `2026-09-17-ANSWER` §3, rewritten in place.

---

## C-110 · "Households absorbed 94.6% of all net new equity issued"

**Mine and HR's. Found 22 Sep by the E-007 audit; period instability re-derived by the supervisor from `data/z1_equity_netbuyers/netbuyers_periods_2026Q2.csv` before acceptance.**

- **What is wrong.** The arithmetic is exact (94.64%). The **denominator is not a stable quantity**. Run the identical method on the other three periods in the same file: **2015–19 = −54.6%; 2020–21 = +119.6%; 2022–23 = +387.5%; 2024–26 = +94.6%.** All four verified. A share that swings from minus fifty-five to plus three hundred and eighty-eight on adjacent windows is not measuring a stable economic fact — it is a small, sign-changing denominator (net issuance) doing the moving.
- **And the fix is not simply a better denominator.** The audit recommended switching to a gross base. Gross bases stay inside [0,100] but are not stable either: household over gross buy-side runs **15.9% / 56.2% / 54.2% / 44.6%** across the same four periods. **Report the dollar figure ($3,069.4bn) and name the base explicitly every time; there is no percentage here that travels.**
- **Still standing at:** `2026-09-14-HR-The-Household-Residual.md` and `2026-09-17-ANSWER` §3.

---

## C-109 · "About 93% of the rise is revaluation" — a residual with nothing on earth to check it against

**Mine and P1's, ANSWER §2 denominator box. Found 22 Sep by the E-007 audit, which then produced the more important half of this entry.**

- **What is wrong.** Revaluation is obtained as `ΔLevel − Flow`. The audit confirmed **by grep, not assertion**, that series `893064105` appears only in the level and flow tables and in **no `_r` revaluation file on disk** — P1 says the same in its own text (*"Z.1 has no single revaluation table for equities"*). So the whole-economy 93.1% is a residual at the one level of aggregation where **no independent Fed series exists to disagree with it**. P1 *did* run sector-level revaluation checks where such series exist; that is the right instinct, and see below for what they found.
- **THE FINDING THAT MATTERS, and it is empirical, not hypothetical.** P1's own sector reconciliation compares implied against published revaluation. For **households**, the two disagree by up to **$318.2bn in one quarter** (2021:Q4), and over the 2024–26 window itself by **$1,283.2bn gross / +$154.6bn net — 41.8% and 5.0% of the $3,069.4bn cumulative household flow** the 94.6% headline is built on. One quarter (2025:Q2) has a reconciliation gap **five times that quarter's entire household flow**. This sat in P1's own data and was never connected to the flow headline.
- **It dwarfs the error model I asked for.** I briefed the audit to compute how far a 1% input error moves the residual. It did — worst case **4.14%**, RSS **1.65%** across all 35 input series — and then said plainly that **the framework understates the problem**: the realised non-reconciliation is an order of magnitude larger than any 1% noise scenario. **Accepted.** The risk is structural disagreement between three independently compiled Fed series, not accumulated small measurement noise.
- **And it refutes the framing I gave it, which I am recording because it changes the rule.** I briefed that the household line is dangerous *because it is the residual that absorbs everyone else's error*. The audit tested that directly: **Rest of World — a MEASURED line, not a residual — shows a comparably sized gap ($322.1bn peak, same quarter; $1,169.0bn gross over 2024–26). NFC — also measured — reconciles to $0.0bn every quarter of the full sample, no exceptions.** Residual-ness is therefore **not** the variable that predicts the defect. Something sector-specific in how each revaluation series is compiled is. That is a better question than the one I asked.
- **Also correctly refuted:** I suggested 93.1% inherits the household residual. It does not — Total is pinned from the **issuer** side, and household is solved downstream of Total, so it is not an input to it. 93.1% carries its own unreconciled status, not household's.
- **Correct position.** Quote 93.1% as IDENTITY with the stock/wrapper caveats **and** the note that it is uncheckable at this aggregation. Attach the household reconciliation gap to any use of the 94.6%/44.6% flow figures.
- **Still standing at:** `2026-09-11-P1-Equity-Net-Buyers.md`; `2026-09-17-ANSWER` §2 denominator box, amended in place.
- **Update 23 Sep — the second half of this entry is OVERTURNED by C-119.** The household and RoW "reconciliation gaps" are the other-volume-changes term P1's check left out, not a disagreement between series; OVC does not enter flows, so the flow figures are not impugned. The first half — 93.1% uncheckable at the whole-economy level — stands.

---

## C-108 · "NFC repurchases ($6.40trn) were almost exactly offset by gross issuance ($6.62trn)"

**Mine, ANSWER §2, sourced to S1. Found 22 Sep by the E-007 audit; every figure re-derived by the supervisor from `data/supply_decomp/fed_efa/` before acceptance.**

- **Killed by:** the EFA monthly companion file, which itemises the public legs of that same gross-issuance total.
- **What is wrong.** Both totals are real (Σ gross issuance 2015:Q1–2026:Q1 = **$6,623.28bn**; Σ repurchases = **$6,403.56bn**). But **only 18.2% of that issuance is identifiable public issuance** — IPO $313.08bn + SEO $895.66bn = **$1,208.74bn**. The other **81.8% ($5,414.54bn) is unitemised**, described by S1 as VC/PE/private placement. Against identifiable public issuance, repurchases are **5.30×**, not an offset. **The "almost exactly offset" is produced by netting in a private-placement component that never touched public float.** The ANSWER gestures at this ("mixes public buybacks with private issuance") but never quantified it, and the unquantified caveat did not stop the offset being the sentence's load-bearing clause.
- **UNSETTLED, and it matters:** whether the repurchase leg is public-only. No methodology doc is on disk. If repurchases also include private buybacks the mismatch narrows. Settle it from the Fed's FEDS Note before quoting either version.
- **SETTLED 23 Sep, and in the direction that sharpens it.** The Fed's FEDS Note (Kuchinski, Ogden, Thomas, Warusawitharana, 16 Jun 2017 — still the methodology the live EFA page links) defines repurchases as equity bought back *by public nonfinancial firms*, while gross issuance covers *publicly and privately held* firms, and M&A covers public and private targets. So the repurchase leg is public-only and there is no private-buyback component to narrow anything: the decade comparison set public buybacks against a mostly-private total. Verified by the supervisor against the page itself: https://www.federalreserve.gov/econres/notes/feds-notes/equity-issuance-and-retirement-by-nonfinancial-corporations-20170616.html. The residual doubt is only whether Compustat's "public" means exchange-listed or SEC-registrant — marginal.
- **Correct position, and it is STRONGER than what it replaces.** Drop the decade aggregate and use the window the claim is about. On **2024:Q1–2026:Q1** (9 quarters, all EFA covers): gross issuance $1,856.61bn, repurchases $1,677.73bn, **M&A retirement $858.00bn against net retirement $679.13bn = 126.3%**. M&A more than accounts for net retirement on the actual window. That is better evidence for "predominantly M&A" than the decade figure ever was, and it was sitting in the same file.
- **Still standing at:** `2026-09-17-ANSWER` §2, rewritten in place.

---

## C-107 · "Net of the wrapper −$360.7bn" used as the operating-company equity-supply number

**Mine, ANSWER §2, from ETF1. Found 22 Sep by the E-007 audit.**

- **Killed by:** `data/etf1/issuer_identity.csv` row 4, which labels it **`derived`** — "total minus ETF share issuance". Confirmed: `3,243.113 − 3,603.814 = −360.701`, exact.
- **What is wrong.** It is not an operating-company number. It nets NFC (−$540.7bn) against **rest-of-world foreign issuers (+$382.2bn)**, other domestic-financial issuers (−$292.3bn) and pass-through non-ETF funds (+$90.0bn). Quoting it for "operating-company supply was negative" mixes four issuer classes and lands on the wrong one.
- **And it UNDERSTATES the finding.** The operating-company number is **NFC alone, −$540.7bn — 49.9% more negative** than the figure the ANSWER was quoting, because foreign issuance partly offsets it in the blend. The correction makes the result stronger, not weaker.
- **What I accept from the audit against my own brief.** I briefed it that a derived line is automatically C-098-class. It pushed back, correctly: **every component here is independently measured and no alternative measurement route exists, so nothing can diverge from it.** The C-098 danger requires a *second* route that could disagree. This one carries attribution risk, not hidden-error risk. That distinction is now in `CLAUDE.md`.
- **Still standing at:** `2026-09-17-ANSWER` §2, rewritten in place.

---

## C-106 · "Three top-level issuer lines sum to the total at source precision"

**Mine and ETF1's, ANSWER §2 and `2026-09-15-ETF1-Identity-Net-Of-ETF.md`. Found 22 Sep by the E-007 audit.**

- **What is wrong, two ways.** (1) **It cannot fail.** Z.1's "all sectors" total is *constructed* as the row-sum of the issuer-sector lines. Offering the sum as corroboration of the wrapper reclassification is E-007's tautology test failed outright. (2) **The three lines are not the ones either document narrates.** ETF1's table has five rows; the ANSWER names only two with values. The genuine Fed-native three-line identity is **NFC (−$540.713bn) + Domestic financial sectors (+$3,401.586bn, FU793164105.Q) + Rest of world (+$382.240bn) = $3,243.113bn**, verified exact. **The third line is never named in either document** — and it is the line that *contains* the ETF series, which is the whole subject of the section.
- **Correct position.** The reclassification (C-081/C-083) stands on the ETF series being **independently corroborated**, which it is: ICI Fact Book Table 13 matches Z.1 to under $0.1bn on both 2024 and 2025, total and bond columns. **Cite that, not the row-sum.** One is evidence; the other is arithmetic.
- **Still standing at:** `2026-09-15-ETF1-Identity-Net-Of-ETF.md` and `2026-09-17-ANSWER` §2, both corrected in place.

---

## C-105 · P5iv's "the ordering is monotonic in exactly the variable under test" as evidence

**Found 22 Sep by the E-007 audit — a correction-propagation gap, not a new measurement error.**

- **What is wrong.** C-082 already ruled that the ordering "is collinear with how much each series is allowed to move, and is not identified as growth control." P5iv's banner fixes the sign-inversion and withdraws the two-fifths/three-fifths split — but the **"monotonic ordering is evidence" claim itself is still asserted in the body, unstruck**, and described there as the first evidence "that does not depend on trusting anyone's model."
- **Correct position.** The ordering is not evidence. Extend the banner to cover the body claim.
- **Why it matters.** The ban-pattern machinery catches **phrasings and numbers**. It does not catch a **method** surviving in prose after the number it produced was killed. That is now two instances in one document family (see C-103).
- **Still standing at:** `2026-09-14-P5iv-Third-Premium-Measure.md`, banner extended in place.

---

## C-104 · "About 29 of our 49bp (60.3%) survives as risk" — a basis choice presented as a measurement

**Found 22 Sep by the E-007 audit, which re-ran it on an alternative basis.**

- **What is wrong.** The −29.3bp "restated to a real-rate basis" figure is the document's **own transformation** (its words: "our own transformation, not his reported figure"), splicing Damodaran's own T-Bond series with a FRED-derived breakeven. His reported T-Bond differs from FRED DGS10 by **14.0bp (Dec-2023)** and **2.0bp (Jun-2026)**. On an equally valid, fully FRED-consistent restatement the figure becomes **−17.4bp**, and the headline swings **60.3% → 35.7%** — a 25-point move in "how much of the compression is risk" from an untested choice between two defensible bases.
- **Correct position.** HYPOTHESIS, not MEASURED. Quote the range across both bases or neither. P5ii's "growth-consistent share is at least ~40%" floor takes −29.3bp as an input and has **not** been re-run against −17.4bp.
- **Still standing at:** `2026-09-13-P5ii-Growth-Versus-Risk.md`, struck in place (the phrasing lives there, not in P2c — my first registration said P2c and was wrong).
- **Update 23 Sep:** the growth floor was re-run by Grok on 22 Sep and **holds** — ≥~40% on the project splice, ~64% on the FRED basis; the Damodaran-attributed share is ~36–60% across the two bases. Supervisor re-derived the arithmetic. The split is coherent under a Gordon frame (`p = ERP − g`, so `Δp = ΔERP − Δg`) and so survives C-102, but it is conditional on that frame and on Damodaran's growth input → `_research/2026-09-22-P5ii-Growth-Floor-Rerun-C104.md`.

---

## C-103 · P2c §5's CAPE "52.2% of today's level — an even stronger 'it's the premium' verdict"

**Found 22 Sep by the E-007 audit. This is the most serious propagation failure the programme has had: a killed claim's identical twin left alive in the same document.**

- **What is wrong.** C-078 killed the level/counterfactual claim on trailing earnings (35.4% / 54.7%). **P2c §5 runs the same method on CAPE earnings and reports 52.2%, still live, still unstruck** — and uses it to call itself "an even stronger verdict" **than the number that is already dead**. Every reason C-078 gives — free baseline parameter, off-manifold counterfactual, growth embedded in the residual — applies unchanged to the CAPE version.
- **Correct position.** Withdrawn on the same grounds as C-078. **UNSETTLED** if anyone wants it back: re-run C-078's own six-baseline sensitivity test on the CAPE construction.
- **Why it matters, and this is the transferable lesson.** C-078 was registered, banned and gated — and the gate has been green every day since while an identical claim sat twelve lines further down the same file. **Ban patterns catch phrasings; they do not catch methods.** When a claim is killed for a *reason*, search the file for other applications of that reason, not other instances of that wording.
- **Still standing at:** `2026-09-12-P2c-Rates-vs-Risk-Premium.md` §5, struck in place.

---

## C-102 · "The multiple was held up by the premium, not by rates" / "independently corroborated" by two further premium measures

**Mine, ANSWER §1 and §7. Found 22 Sep by the E-007 audit; arithmetic re-derived by the supervisor. The source documents are careful; the summary is not.**

- **What is wrong.** The premium is **defined** as `p := E/P − real yield`. So `Δp = ΔEY − Δr`, and over Dec-2023→Jun-2026: `−0.1424 − 0.3435 = −0.4859`. **70.7% of the celebrated 48.59bp "premium compression" is the arithmetic mirror of the very 0.34-point rate rise the sentence contrasts it against.** Only 29.3% — the earnings-yield leg — is information beyond "real yields rose and the earnings yield did not follow." The sentence opposes two quantities where one contains the other.
- **The Shapley split is worse than "sums by construction."** Its two legs are near-identical linear rescalings of Δr and Δp — per-unit slopes **−6.217 vs −6.195, 0.4% apart**, and within 0.2–0.5% on two further window/measure rows. The split does not distinguish two causal forces; it partitions one measured quantity (ΔEY) between its two definitionally-linked halves. P/E is a function of EY alone, so there is exactly **one** degree of freedom here.
- **And the "independent corroboration" is structural, not independent.** All three constructions compress because a **rate or bond leg rose faster than the equity leg** over the same window: our real yield **+34.35bp**, Damodaran's own nominal T-Bond **+57bp**, SPF's BOND10 **+34.52bp**. The SPF case is the clearest: STOCK10 **rose +15.43bp** — forecasters expected **more** from equities, not less (C-082 already said this) — and the premium "fell" only because BOND10 rose more. "Three constructions agree on direction" is true and far more mechanical than it reads.
- **Correct position.** What is MEASURED: the earnings yield barely moved while real yields rose 34bp, so the multiple held up. What is NOT measured: that investors repriced risk. P2c itself says *"a backward accounting residual, not a forward premium"* and *"stop calling the residual a risk premium"* — **the three source documents are disciplined about this and the one-line summary standing on them is not.** Third instance of that pattern today (see also §3a vs N4).
- **Still standing at:** `2026-09-17-ANSWER` §1 and §7, rewritten in place.

---

## C-101 · "Per-share accretion is ~7–13% of the price gain" read as an interval / "profit plus index composition ~69–75%" read as a second finding

**Mine, carried into the ANSWER §1 and §6 from C-093. Found 22 Sep by the E-007 audit; the underlying facts were all in C-093 already — what was wrong is how the band is read.**

- **Killed by:** `data/eps_split/results_v2.json` (four weighting results) and C-093's own text.
- **What is wrong, two ways.** (1) **The band is a spread across AGGREGATION METHODS, not a confidence interval and not an endpoint range.** Equal-weight 7.1%, latest-mcap 8.3%, Laspeyres 10.6%, 2015-mcap 13.4% — four deterministic weighting choices, no statistical uncertainty computed anywhere. And C-093 states that **survivorship pushes every one of them up**. A band whose every member is biased in the same direction is **one-sided**: the truth is *below* it, not inside it. "7–13%" invites exactly the reading it cannot support.
- (2) **"Profit plus index composition ~69–75%" is the arithmetic complement of the accretion band, not a second result.** Verified: `100 − 17.7 − 7.06 = 75.24` and `100 − 17.7 − 13.39 = 68.91`, reproducing the stated range exactly. There is **one degree of freedom** here (the weighting choice) driving both numbers, and presenting them side by side reads as two findings converging.
- **Correct position.** Accretion is **at most** the mcap-weighted figures, one-sided downward, with the missing-mega correction unsigned (C-093 point 3). Quote it as a ceiling with the direction named, never as "between 7 and 13".
- **What I do NOT accept from the audit that found this.** It proposed that the **tightest ceiling is the equal-weight 7.1%**, on the grounds that all four are upward-biased so the smallest binds. **Rejected.** The four are not four estimates of one quantity with a shared bias — they are different estimands. The index is market-cap weighted, so the mcap constructions are the relevant ones and equal-weight is the wrong estimator for this question, not a tighter bound on it. Taking a minimum across definitions is not a bound.
- **Also found and separately true:** `data/eps_split/panel/` **is an empty directory** — the 385-firm panel behind every number above is not on disk, so none of it is locally reproducible. Same defect class as C-097. Recorded as **d3**.
- **Still standing at:** `2026-09-18-EPS-Split.md`; `2026-09-17-ANSWER` §1 and §6, corrected in place.

---

## C-100 · P2a's "roughly 70–80% came from earnings growth" — a band stated narrower than the document's own table

**Mine, in `2026-09-11-P2a-Return-Decomposition.md` lines 13 and 58, and carried verbatim into the ANSWER §1. Found 22 Sep by the E-007 audit, which correctly contradicted the brief I gave it.**

- **Killed by:** P2a's own `decomp_cumulative.csv`, row 2.
- **What is wrong.** P2a computes **two** cumulative rows: to Dec-2025 the earnings share is **71.0%**, to Jun-2026 it is **82.3%**. Re-derived independently: `log(295.3881/102.31) / log(7450.032857/2054.27) = 0.82301`. The document then states the headline as "roughly 70–80%", which **excludes its own second row by 2.3 points**. It does say the split is "sensitive to the endpoint" and that the Jun-2026 run pulls the EPS share up — but it never says how far, and the number that leaves the band is the more recent one.
- **Correct position.** The measured range across the two computed endpoints is **71.0%–82.3%**. Say that, or name the endpoint with the figure. The ANSWER (§6, 21 Sep) already notes 82.3% sits above the band; **P2a itself was never corrected** and it is the document everything cites.
- **Correction to my own brief.** I briefed the audit that 82.3% came from "a separate calculation". It does not — it is P2a's own row, in the same table, in the same document as the headline. The inconsistency is internal, which makes it worse, not better.
- **Still standing at:** `2026-09-11-P2a-Return-Decomposition.md` lines 13 and 58, corrected in place.

---

## C-099 · P2a §"Check: do the parts reproduce the total within 0.5pp?" — a tautology reported as a passed validation

**Mine, in `2026-09-11-P2a-Return-Decomposition.md` §Check. Found 22 Sep by the E-007 audit and re-derived independently by the supervisor before acceptance. Not previously flagged anywhere.**

- **Killed by:** `data/p2a_decomposition/decomp_annual.csv`, all 12 rows.
- **What is wrong.** The section asks whether price return plus dividend return reproduces total return within 0.5pp, reports **"every one of the 11 full years is within tolerance, worst year 2019 at −0.463pp"**, and concludes *"the check passes as the brief expected"*. It **cannot fail**. In the data, `total_return = (1+price_return)(1+dividend_return) − 1` holds to floating point in **12 of 12 rows** (max deviation **2.2e-16**, supervisor-verified). Given that, the reported gap is identically `−price_return × dividend_return` — a deterministic function of two numbers already printed on the page. The CSV even carries the column `dividend_cross_term`.
- **So the "worst year" ranking measures nothing about data quality.** 2019 is "worst" because it had the largest product of price and dividend return, which is a fact about 2019's returns, not about whether the series reconcile.
- **Correct position.** Delete the pass/fail framing. If a real reconciliation is wanted, it must compound dividends **independently** from monthly cash dividends and compare against the total-return series — that check *can* fail, and was never run.
- **Why it matters.** This is the C-098 defect one document upstream of where it was caught, in the document that supplies the programme's lead number. The project has now found three tautologies-presented-as-checks in four days (C-098, C-099, and the sum-check in C-101). **A check that cannot fail is not a weak check — it is an absence of a check wearing the costume of one.**
- **The script is gone.** `decomp.py` lived only in a session scratchpad and is not on disk (d1/d2 class), so which variable was the literal plug cannot be settled — but the 12/12 exact match settles that the relationship is definitional either way.
- **Still standing at:** `2026-09-11-P2a-Return-Decomposition.md` §Check, corrected in place.

---

## C-098 · "Pre-tax profit is 74.2% of Δlog EPS" / "Sum check: exact" as corroboration of the W3 decomposition

**Grok's table, relayed by the supervisor to the principal on 21 Sep as "every scalar re-derived and matches". Caught 22 Sep on the first application of E-007 — by the supervisor, against his own report of the previous day.**

- **Killed by:** the definition of the term itself, stated in W3's own source table (*"Δlog(pre-tax) | 0.7875 | **Residual of the identity**"*), and by `data/w3_tax/results.json`, whose panel sums give the term independently.
- **What is wrong.** `Δlog EPS = Δlog(pre-tax) + Δlog(1−ETR) − Δlog(shares)` was closed by computing the pre-tax term as `1.0613 − 0.1012 − 0.1726 = 0.7875`. So **the sum check cannot fail** — it is arithmetic, not corroboration — and **74.2% was never measured**. It is the share of nothing-in-particular left over once the other two terms are taken out, and it absorbs every error in both of them, neither of which was produced by this parcel (1.0613 is carried from P2a/Shiller, −0.1726 from C-093).
- **And the residual was hiding a real, measurable gap.** Grok's own panel sums Σpre-tax $1069.6bn (2015) → $2528.4bn (2025) give `Δlog(pre-tax) = **0.8603** ` directly. The residual says 0.7875. **The gap is 0.073 log = 7.6%**, and it was invisible because the term was never computed two ways. On the panel-consistent basis, implied Δlog EPS is **1.1341**, not 1.0613.
- **Why the gap exists (hypothesis, not established).** The three terms are on **three different universes**: Shiller index-level as-reported EPS (all 500, index divisor, composition changes); a 412-firm panel of **current** constituents with both years of data (survivorship, 94.1% of 2015 mcap); and constituent-level diluted share counts. W3 lists survivorship and coverage as threats and states survivorship's direction as *overstating growth* — consistent with a survivor panel growing ~7.6% faster than the index over the decade. **Which of the four causes dominates is untested.**
- **Correct position.** Report the two terms that were actually produced: `Δlog(1−ETR) = 0.1012` **MEASURED** on the 412-firm panel, and the pre-tax term **MEASURED** at 0.8603 on that same panel — with the 0.073 gap against the carried EPS stated, not absorbed. **Withdraw "74.2%" entirely.** On the internally consistent basis the tax share is **8.9%**, not 9.5%; pre-tax 75.9%; accretion 15.2%.
- **What survives, and it matters.** *Tax is about a tenth of EPS growth* is robust to the basis choice (8.9% vs 9.5%) and so is *most of the earnings story is pre-tax business*. The **conclusion survives; the precision does not.** The restated 82.3% → 74.5% also survives, because both sides of it use the same carried Δlog P.
- **Why it matters.** This is the first thing E-007 caught, and it was in a parcel the supervisor had already reported as verified the day before. Re-deriving a number is not the same as asking what the number *is*: every scalar in that table reproduced exactly, because reproducing a residual only re-runs the subtraction.
- **Still standing at:** `2026-09-21-W3-Tax-Decomposition.md`, corrected in place; the 21 Sep supervisor report to the principal, corrected in the 22 Sep report.

---

## C-097 · "The W3 firm-level panel and the raw Z.1 debt pulls are mirrored under `data/w3_tax/` and `data/z1_debt/`"

**Grok's, in `data/w3_tax/README.md` and in the `series_file` fields of `w1_rebalance_attack.json`, 21 Sep. Caught by the supervisor the same day, on review of the parcel.**

- **Killed by:** `find . -iname "*firm_tax_panel*" -o -iname "*z1_debt*" -o -iname "*BOGZ1FU*"` — returns nothing.
- **What is wrong.** `data/w3_tax/` holds three files: `README.md`, `results.json`, `w1_rebalance_attack.json`. The 343 KB, 412-firm panel exists only on the executor box at `/workspace/tdr/data/w3_tax/firm_tax_panel.csv`, which nothing here can reach. `data/z1_debt/` does not exist, so the five raw FRED pulls named inside `w1_rebalance_attack.json` are absent too. The README's sentence claiming a local mirror is false.
- **What survives.** Every headline scalar was re-derived independently from `results.json` and matches: ETR 27.35% / 19.62%, Δlog(1−ETR) 0.1012, tax 9.53% of Δlog EPS, restated share 74.5%, and the Task 2 pairing totals 680.5 / 938.4 = 72.5%. The arithmetic is sound. What cannot be checked here is the step from SEC companyfacts to Σtax/Σpretax over 412 firms — the tag picks, the FY fallback, the Dom/Foreign exclusions.
- **Correct position.** W3's ETR figures carry **"scalars reproduced, source panel absent"** until the two artifact sets land. Ask Grok for them on next contact.
- **Why it matters.** Same defect class as d1/d2 (21 Sep): a document naming a deliverable that is not there. A parcel is not finished when the note is written; it is finished when the evidence is reachable by someone who was not in the session.
- **Still standing at:** `data/w3_tax/README.md`, corrected in place.

---

## C-096 · "Most of W1's $938.4bn ceiling is rebalancing, so the contractual channel is overstated ~3–4× and the operative figure is ~$258bn"

**Grok's, in `2026-09-21-W3-Tax-Decomposition.md` Task 2 verdict, 21 Sep. Caught by the supervisor the same day. The arithmetic is right; the register is wrong.**

- **Killed by:** the structure of the pairing itself, and by two rows of Grok's own table.
- **What is wrong.** Task 2 caps per-sector "rebalancing" at `min(equity sales, debt-security acquisitions)`. That is a **ceiling on one recycling route**, not a measurement of it. Money is fungible at sector level: nothing in Z.1 links a life insurer's bond buying to its equity selling. Grok's own numbers make the point — **life insurers bought $612.0bn of debt while selling $194.0bn of equity, and P&C bought $364.5bn while selling $185.0bn.** Buying three times more bonds than you sold equities is the signature of a balance sheet growing on premium inflow, not of rotation out of equities. The pairing establishes **possible**, not **plausible**, and W3 uses the second word.
- **Compounding it:** W3 correctly calls $257.9bn an *upper bound* in one sentence, then two sentences later uses it as a point estimate to claim a 3–4× overstatement. Both $938.4bn and $258bn are ceilings on the same quantity. **No floor has been established at all**, and debt securities are only one destination — netting MMF shares, deposits, repo and other equities would tighten the ceiling further still.
- **Correct position.** The pairing is worth keeping and it **narrows the interval**, which is real progress. Say it as: the contractual channel's seller-side flow over 2024Q1–2026Q2 is **$938.4bn**; netting these sectors' debt purchases tightens the ceiling to **~$258bn**; both are ceilings, the lower one is not an estimate, and the floor is unknown. The one sector that shows little bond recycling is **federal pensions — $6.5bn of debt against $67.8bn of equity sales** — and its proceeds went somewhere unexamined.
- **Why it matters.** This is the C-089 / C-092 pattern again: a bound reported in the register of an estimate. W1 was explicit that $938.4bn is "a ceiling, not a measured leak"; the verdict that cites W1's number drops W1's own caution.
- **What would settle it.** Z.1 carries benefit payments and contributions for these sectors directly. The sector's actual cash drain to households is **benefits paid minus contributions received** — a measurement, not a pairing. That is the next move if anyone wants the real number.
- **Still standing at:** `2026-09-21-W3-Tax-Decomposition.md`, corrected in place with a banner; `RESEARCH_STATE.md` inventory line, rewritten to a pointer.

---

## C-095 · "SBC, operating-vs-GAAP and R&D capitalisation are untested inflators of the earnings claim"

**Mine, in `2026-09-17-ANSWER` §6 and in the 20 Sep inventory, repeating SYN1's Attack 1 list without checking it against the earnings series the claim actually uses. Caught while scoping the parcel, before it was spent.**

- **Killed by:** `2026-09-11-P2a-Return-Decomposition.md`, its own supervisor caveat line: **"as-reported (GAAP) earnings"**.
- **What is wrong.** The headline "earnings explain 70–80% of the price gain" rests on Shiller's **as-reported** series. **Stock-based compensation is expensed in GAAP net income (ASC 718, since 2006)**, so it is already deducted and cannot inflate that series; its remaining route into EPS is share count, which the EPS split has already measured (C-093). **Operating-versus-GAAP** is moot for the same reason — the series *is* the GAAP one. **R&D capitalisation** does not inflate US reported earnings either, since US GAAP expenses R&D as incurred.
- **Correct position.** Of the margin SYN1 named, what survives as a live, untested inflator of *as-reported* earnings is: **(a) the 2017 tax act**, which cut the federal statutory rate 35%→21% effective 2018 and mechanically lifts after-tax earnings with no change in pre-tax profit — large, and squarely inside the 2015→2026 window; and **(b) revenue-recognition timing** (ASC 606, also 2018). Those two, not the other three.
- **Why it matters.** This is a scoping error that would have spent a parcel measuring something already inside the number. Before testing an "inflator", check which earnings definition the claim rests on.
- **Still standing at:** SYN1's return, which listed the candidates without ranking them against the series; and the ANSWER, corrected in place.

## C-094 · "The leak objection is untested, and load-bearing for the circuit thesis"

**Both halves fail as of 20 Sep. It is no longer untested, and what it was load-bearing FOR was retired weeks earlier without §4 catching up.**

- **Killed by:** W1, 20 Sep — `2026-09-20-W1-The-Leak-Objection.md`, on `data/z1_equity_netbuyers/netbuyers_periods_2026Q2.csv`.
- **The stale dependency.** §4 listed the leak as load-bearing for "K1, and any essay built on the two-circuits idea". §3 records **K1 as RESOLVED — NEITHER**, the circuit account failing on three independent observables. The objection was carried as load-bearing for a thesis the project had already abandoned.
- **And it is now quantified.** Of the **$6,886.8bn** paid by buying sectors, only **$3,643.7bn** reached a seller of an existing share — the rest went to issuers of new equity and cannot leak by construction (ties to C-080: 6,886.8 − 3,643.7 = 3,243.1). **Mutual funds are 55% of that seller side**, and ETF buying of $2,460.9bn covers that leg **122%** — it is the S1 rotation seen from the sell side, not cash leaving. The identifiable contractual channel is the **pension + insurance block: $938.4bn, 25.8% of the seller side, about $375bn a year.**
- **Correct position.** The leak's arithmetic ceiling is **53% of the buying flow**, most of that is a wrapper rotation, and the contractual channel is about a quarter of the seller side. The objection does not threaten the current answer. Of the three defences the file named, this supports **non-consuming sellers**; low MPC at the top and credit extinguished on resale stay untested.
- **What must travel with the number.** $938.4bn is a **ceiling, not a measured leak** — a pension selling equities may be rebalancing into bonds, which Z.1 would show and this pass did not check. No MPC is applied, and `data/series.tsv` holds **no consumption denominator**, so it must never be quoted as a share of goods demand.
- **Still standing at:** `2026-09-20-W1-The-Leak-Objection.md`, allow-listed — it quotes the dead phrasing in its status line and its do-not-say list.

## C-093 · "Aggregate profit growth explains 68.9% of the price gain" / "per-share accretion is 13.4%"

**Supervisor review of Grok's EPS split, 19 Sep. The method is sound and the lead claim survives; the headline labels and the point estimate overstate.**

- **Verified first:** AAPL re-derived independently from SEC companyfacts — FY2015 diluted WASO 5,793,069,000 × 4 (Aug-2020 split) = **23,172,276,000**; FY2025 **15,004,697,000**; Δlog **−0.4346**. Both endpoints match the panel exactly, on the largest weight and the largest buyer.
- **What is wrong, three ways.** (1) **"Aggregate profit" is not measured — it is a residual.** It is inferred as Shiller index EPS, which moves when firms enter and leave the index, plus the panel's share change, which covers current constituents only. So **index-composition effects land in the "profit" bucket by construction.** The doc's statement that composition is "not folded into either bucket" is incorrect. (2) **13.4% is the highest of four weightings**: equal-weight 7.1%, latest-mcap 8.3%, Laspeyres share-index 10.6%, 2015-mcap mean of firm Δlogs 13.4%. Survivorship pushes every one of them *up* (survivors are the buyers), so quoting the maximum as the point estimate overstates twice. (3) The missing megas bias in **opposite** directions: Alphabet, a large buyer, would raise accretion; TSLA and AVGO, large issuers, would lower it. The net is unsigned.
- **Correct position.** Per-share accretion is **~7–13% of the S&P 500 price gain since 2015**, most likely toward the lower-middle once survivorship is weighed. **Profit plus index composition is ~69–75%**; the multiple **~18%**. Of EPS growth alone, accretion is roughly **one-tenth to one-sixth**. **"Earnings did most of the work" survives, and it is mostly real profit** — but carry the band, and call the ~69% "profit and composition", not profit.
- **Reproducibility gap:** `data/eps_split/panel/` is **empty**. The per-firm panel was computed and not saved — the same failure as P5(iii)'s per-ticker residuals. Only the mega-coverage file and the annual share index survive.
- **Still standing at:** `2026-09-18-EPS-Split.md`, bannered and allow-listed.

## C-092 · "JVZ sharpen returned NOT SUPPORTED — not an underpowered false null" / Tier B's standing finding as written

**Mine in root cause: the MDE gate I specified used the wrong formula, so it cleared a design that could not see its own hypothesis. Every JVZ leg is UNINFORMATIVE, not a rejection.**

- **Killed by:** my own realised-standard-error power check, 16 Sep, on the coefficients and t-statistics reported in `_research/2026-09-16-JVZ-StageB-Mechanism.md` and `_research/2026-09-16-JVZ-StageB-Sharpen.md`.
- **What is wrong.** A run can only support NOT SUPPORTED if it could have **seen** the effect — predicted effect above the realised MDE. Backing the standard error out of each reported β and t, and comparing 2·SE against JVZ's predicted magnitudes (Table 6.2 top-50 **+0.528pp**; Table 6.3 incremental **≈+0.43pp**):

  | leg | β | t | implied SE | MDE = 2·SE | predicted | predicted ÷ MDE |
  |---|---:|---:|---:|---:|---:|---:|
  | Stage B return | +0.504 | 0.62 | 0.813 | **1.626** | 0.528 | **0.32×** |
  | Stage B idio | −0.051 | −0.24 | 0.212 | 0.425 | 0.430 | 1.01× |
  | Sharpen return | −0.336 | −0.618 | 0.544 | **1.087** | 0.528 | **0.49×** |
  | Sharpen idio | +0.066 | 0.22 | 0.300 | 0.600 | 0.430 | 0.72× |

  **All four are at or below 1×.** The sharpen return channel — the leg the standing finding leans on — could only have detected an effect **twice** the size JVZ predicts. A wrong-signed insignificant coefficient from such a run is noise, not evidence against the paper.
- **The root cause, which is the reusable part.** Stage A computed the MDE as **2σ/√N** on **3,936 firm-quarters**, giving 0.451pp, and cleared. The **realised** two-way-clustered SE was 0.811, an MDE of **1.622pp** — 3.6× larger. The implied effective n is **304, not 3,936.** The identifying shock is quarter-level (aggregate flow) interacted with a near-time-invariant cross-sectional characteristic, so precision is governed by the number of shock periods, not the number of rows. **σ/√N is the wrong formula for this design class, and "effective n" declared rather than demonstrated is not a gate.**
- **Correct position.** The JVZ legs are **uninformative on free data** — the same class as B6 (C-090/C-091) and P5(iii), for the third time. Do **not** say JVZ was not supported, was refuted, or was tested with its holes closed. Do not read the wrong-signed idio point estimate as mild evidence against the mechanism. Whether free data *could* carry this design is **still open**: the binding constraints are the N-PORT span (23–26 quarters) and mega-firm coverage, and mega-firm coverage was a Yahoo rate-limit problem, which is fixable.
- **What still stands.** B5 and P4 closed on **data** (C-086). B6 closed on **arithmetic** (C-090/C-091) and that one is genuinely permanent — 386 years. No scalar M was invented anywhere; C-077/C-080 retractions stand. The within-quarter variation finding is real and is a genuine advance over P5(iii)'s collapsed design. Tier B's standing finding survives **on the B5/P4/B6 legs**; it is **overstated on the JVZ leg** and must not be quoted as "every free route failed."
- **Still standing at:** the three JVZ docs and `2026-09-16-TierB-E005-Resolution-Limit.md`, all bannered and allow-listed.

## C-091 · "B6 is blocked on free NYSE payment-date coverage"

**Mine, 15 Sep, and it is the diagnosis inside C-090 as well as the brief I wrote for the pay-date scout. The verdict in C-090 stands; its stated CAUSE was wrong, and I commissioned a parcel on the strength of it.**

- **Killed by:** my own power calculation on `data/b6_phase1/daily_payment_yield.csv`, 16 Sep, after the scout returned VERIFIED NO.
- **What is wrong.** Pay-date coverage is not the binding constraint, so removing it would not have unblocked anything. SPY daily return **sd is 111bp**. The top-minus-bottom payment-yield spread in the full-universe sample — which **already contains every S&P 500 payer**, NYSE included, via imputed dates — is **1.32bp**. True dates remove *timing noise*; they do not widen that spread. At Hartzmark–Solomon's M≈1.9 the predicted return gap is **2.51bp against 111bp of daily noise**, which needs **15,632 days per quintile — about 97,300 trading days, or 386 years**. Even at the top of the published envelope (M=9.4) it needs **16 years**, against the 11.7 we have.
- **Correct position.** B6 is blocked on **signal-to-noise**, and the limit is **arithmetic, not data access**. No free source, no paid source, and no ticker widening fixes it: 386 years of daily equity returns do not exist. Hartzmark–Solomon reach significance through a multi-decade CRSP sample and an international panel, not through better dates. Do not say B6 is blocked on NYSE pay dates, and do not reopen it hoping for a corporate-actions source.
- **What this generalises to, which is the useful part.** Any bridge design whose treatment effect is a **few basis points against ~111bp of daily equity noise** is unresolvable on a decade of daily data, whatever the data source. That is a cheap screening test to run *before* commissioning, and it disqualifies the Nasdaq-only B6 subsample in advance — fewer payers means a smaller spread and strictly less power than the run that already failed.
- **The process failure, which is mine twice over.** C-090 was registered *because* Phase 1 was armed without a minimum-detectable-effect check. I then wrote a scout brief and commissioned a parcel — **without doing the MDE check for the unblocked design**, though sample B's numbers were already on disk and already implied it. Same error class, immediately after registering it. The scout was well executed and its negative on free corporate-actions data is worth keeping; it answered a question that could not have changed the decision.
- **Still standing at:** C-090's verdict (uninformative null, do not invent an M); the scout's own finding about free corporate-actions sources, `_research/2026-09-16-NYSE-Payment-Date-Scout.md`. Allow-listed there.

## C-090 · "B6 Phase 1 tested the dividend payment-day mechanism and it failed"

**Mine, 15 Sep — the scoping error, not the execution. I armed a kill switch without a minimum-detectable-effect check, and it fired on a test that could not have passed.**

- **Killed by:** my own power calculation on `data/b6_phase1/regression_table.csv` and the quintile means, 15 Sep, after the parcel returned.
- **What is wrong.** The primary (calendar-true) sample has a top−bottom payment-yield spread of **0.73bp of market cap**. At Hartzmark–Solomon's M≈1.9 that predicts a return gap of **1.39bp**; the regression's standard error is **8.66bp — 6.2× the effect being hunted**. Its **minimum detectable multiplier is M≈23.7**. The full-universe sample is better and still insufficient: spread 1.32bp, se 8.31bp, **minimum detectable M≈12.6**. The published envelope is **1.5–9.4** and the hypothesis is 1.9. **Neither specification can reject any value in the envelope**, so a coefficient of ≈0 with t=0.01 is exactly what this design returns whether the mechanism is real or absent.
- **Why the variation is too small.** S&P-500-only payers give a mean of **3.38 payers and $2.68bn** on a top-quintile day — against an object Hartzmark–Solomon define marketwide. Phase 1 was scoped narrow deliberately, to avoid P4's failure mode of building big before testing small. That scoping removed the very variation the test needs. The doc's own limitation 4 said the universe was "far thinner than marketwide HS samples"; what was missing was the step from that observation to "therefore the kill switch is not a valid test."
- **Correct position.** B6 Phase 1 is **BLOCKED on payment-yield variation**, which is downstream of free payment-date coverage (~78% of full-universe events lack true payment dates). It is **not** evidence against the mechanism, and it is **not** grounds to close the payment-day route. Do not state that the mechanism failed, was refuted, or was tested and found absent.
- **What stands, and should not be re-litigated.** "Do not invent an M" — correct and unchanged. The refusal to promote the imputed-date t=1.37. The null placebos on announcement and ex-dates. The refusal to extend to the household residual or the 2024–26 revaluation (C-077). Note that the strongest specification, `full_universe:top_all_pos`, is **positive at t=1.93 (p=0.054)** — in an underpowered design that is mildly suggestive, not dismissible either way.
- **The pattern worth naming.** Three aggregate identification designs have now failed here — B5 sovereign mandate, P4 Russell RD (C-086), B6 payment-day — and **all three failed on free-data resolution, none on the economics.** Allow-listed at the B6 doc.

## C-089 · "Deposit growth was too small to have funded the buying"

**Mine, 14 Sep. Withdrawn in place on 15 Sep **without a correction number**, which is exactly why it was still live in the synthesis a day later. Registered now so the ban list can see it.**

- **Killed by:** the A1 scale-test re-read, 14–15 Sep — `2026-09-14-A1-Money-Creation-Link.md`; independently restated as Attack 4 of the SYN1 return (Grok, 15 Sep), `_research/SYN1_return_2026-09-15.md`.
- **What is wrong.** The test compared **flow to flow**: deposit growth of $1,948.4bn over 2024:Q1–2026:Q2 against $3,069.4bn of household equity buying, concluding the channel was "too small to have funded it even in full." That assumes only *newly created* deposits can buy equity. The deposit **stock** at 2026:Q2 was **$19,384.4bn — 6.3× the purchases** — and can fund them with zero creation. Three further defects: H.8 deposits are **all holders**, not households; ETF creation is frequently **in-kind**, needing no deposit at all; and a same-period correlation does not sequence money→buying, since equity *sales into* deposits produce the same sign.
- **Correct position.** New bank deposits cannot be the **sole** source. Nothing in the scale comparison bounds how much of the buying deposits funded. The measured association (r≈0.26, ~16 cents of buying per $1 of deposit growth) stands as weak and positive; the **ceiling does not**.
- **The propagation failure, which is the part worth remembering.** Corrected in place with no number, there was no ban pattern, `bin/check.sh` could not see it, and it stood in `2026-09-14-SYN-What-We-Can-Say.md` — the document this project's own read table marks START HERE — until an outside return found it. **An in-place amendment without a correction number is not a correction; it is a local edit.** This is the third time propagation, not detection, has been the failure here.
- **Still standing at:** A1's measured association; `Parcel_SYN1_Attack_The_Synthesis_For_Grok_Cursor.md` (the parcel that asked) and the return that answered. Allow-listed.

## C-088 · The "Realized ^SOX ann. return" column of the G-014 table

**Claude, 15 Sep — found by the E-006 re-derive rule on its first use. The verdict it sits next to is unaffected; the column is not.**

- **Killed by:** independent pull of `^SOX` daily closes, Yahoo v8 chart API, 2025-12-31 → 2026-09-14 (retrieved 15 Sep 2026), same index and same source the parcel used.
- **What is wrong.** Three checkable cells, three mismatches. **Trailing 60d** reads −52.0%; `^SOX` actually returned **−17.4%** over that window — and 3 × (−17.4%) = **−52.2%**, so the cell holds a *levered* figure under a header that says index return. **2026 H1** reads +290.5% against an actual **+101.1%** (the cell is marked "(path)"). **2026 YTD** reads +81.8% against **+57.2%**, which reconciles with neither the 1× nor the 3× reading.
- **What is NOT wrong, and matters more.** The **vol column reproduces exactly** — 2026YTD realized annualized `^SOX` vol of **49.0%** against the parcel's 49.0% — and every figure derived from it reproduces: the L=3 breakeven (24.0%), the σ≈122% needed for a 150% hurdle, and the σ≈71% needed on the drag reading. **C-087's verdict rests on vol, not on this column, and stands.**
- **Correct position.** Do not quote any return level from that table. Re-derive from source. `^SOX` 2026: H1 +101.1%, YTD (to 14 Sep) +57.2%, trailing 60d −17.4%, realized vol 49.0%.
- **Still standing at:** every other section of `2026-09-15-DG-Remainder-Leveraged-ETF-Flows.md` — the AUM snapshot, G-008, G-012 and the G-014 mechanism and vol work. Allow-listed there.

## C-087 · "A 3× semiconductor LETF needs ~150%/yr on SOX to break even" (Green, G-014)

**A Green corpus number that does not reproduce. The mechanism he describes is real; the figure is not.**

- **Killed by:** D-G remainder, 15 Sep — `2026-09-15-DG-Remainder-Leveraged-ETF-Flows.md`; the vol input independently re-derived by a second agent the same day (C-088) and matching to 0.0pp.
- **What is wrong.** The constant-leverage breakeven for L=3 is `g_be = (L−1)/2 · σ²`. At `^SOX` 2026YTD realized vol of **49.0%** that is **24.0%**, not ~150%. A 150%/yr hurdle needs **σ ≈ 122%** annualized; on the alternative reading that 150% is the *drag* term `L(L−1)/2 · σ²`, it needs **σ ≈ 71%**. Observed `^SOX` vol is 45–55% across the YTD, H1, trailing-60d and 1y windows. Neither is in reach.
- **State the convention with the number.** 24.0% is the underlying's **log (geometric)** return. On the arithmetic-drift convention, `μ_be = L/2 · σ²`, the same vol gives **38.0%**. A breakeven quoted without its convention is not checkable.
- **Correct position.** The daily-rebalance mechanism is **supported** — issuer prospectus and holdings put gross exposure at ≈3.00× AUM on 15 Sep 2026, and the rebalance moves notional with no new cash. The drag is real but shows up as the **gap to the 3×-daily path**, not as a hurdle: 2026YTD SOXL **+140.6%** against a 3×-daily-compounded SOXX **+162.6%**, a −22.0pt gap. Do not restate ~150%/yr as fact; if quoting Green, attribute it and say it did not reproduce at observed vol.
- **Still standing at:** the G-014 mechanism finding, and the Green corpus dossier as a record of what he said.

## C-086 · "P4 recovered a Russell elasticity / IWB holdings are the Russell list"

**Mine, 15 Sep — a do-not-say from P4, registered so the next document does not manufacture a multiplier the first stage forbade.**

- **Killed by:** P4, 15 Sep — `2026-09-15-P4-Russell-Elasticity-Pilot.md`. Fuzzy RD on free substitutes (IWB/IWM N-PORT + March 13F rank + Yahoo closes), 2022–2026 reconstitutions. Grid `data/p4/rd_grid.csv`.
- **What is wrong.** Assignment of IWB June membership on Z=1{rank ≤ 1000} is τ=0.070 (se 0.043, t=1.61, n=2005, h=200, year FE, HC1); F≈2.6, below the spec kill switch. Δ13F first stage t=0.78. Reduced-form CAR[−5,+5] t=1.55. IWB 2024 Jaccard of equity CUSIPs Mar vs Jun is 0.992 (4 adds, 4 drops) — a sampling ETF, not the reconstitution. 2SLS is not defined. Rescaling any of these numbers to Z.1 lines repeats C-077/C-080.
- **Correct position.** The free-data Russell RD does not assign treatment. A null ITT is not evidence that the passive bid does not move prices. Official May ranks and full-replication membership were not observed (E-005: we do not pay).
- **Still standing at:** `_research/2026-09-12-P4-Flow-Elasticity-Spec.md` (the design, now run); B0's B3 row, rewritten in place.

## C-085 · "X% of purchases ran through nonbank money / collateral" / "2024 private-repo growth was new cash"

**Mine, 15 Sep — a do-not-say from N4, registered so the next document does not manufacture the percentage the frame forbade.**

- **Killed by:** N4, 15 Sep — `2026-09-15-N4-Scale-Timing-Bound.md`. Arithmetic on `_research/n2b_v2/zk_v2.csv` plus D10/N3v4/N2c/P2c already on disk. No new retrieval.
- **What is wrong.** A ratio of ΔW (or of the handoff-adjusted ceiling) to wrapper purchases is a *capacity ceiling*, not a fraction funded. Treating 2024's +$540.6bn of private MMF repo as new wholesale cash ignores the −$586.3bn ON RRP drain in the same year (net −$45.7bn). Dating the six-bank permitted/repledged step (+19.3% / +21.5%) to the 2024 compression puts a 2026 stock change in the wrong year.
- **Correct position.** In 2024 the measured wholesale-repo expansion was the RRP handoff. Handoff-adjusted new capacity that calendar year is **+$136.2bn** against **$1,404.9bn** of household purchases of the instrument (N2c). Over 2024:Q1–2026:Q2 the same ceiling is **+$858.6bn** against **$3,069.4bn**. Neither is a funded share. Collateral re-use intensity did not rise (C-061 range). Existing wholesale *stocks* can still rearrange without growing — that is a different claim, and the measured reuse rate did not rise.
- **Still standing at:** `_research/2026-09-14-N4-Frame.md` (poses the dead percentage question in order to kill it); the 15 Sep ranked-block wording, rewritten in place.

## C-084 · "The residual HAS been decomposed" / "Rosenthal & Burke (2024) names the bodies inside the plug"

**Gemini Deep Research via the 15 Sep ranked block, killed 15 Sep.** The LIT1 map treated a
tax-policy recoding of Z.1 as an entity census of the household residual.

- **Killed by:** LIT1, 15 Sep — `2026-09-15-LIT1-Residual-Literature.md`. Three named leads
  read at source. The Gemini return itself was not on disk under `_research/`.
- **What is wrong.** There is no 2024 paper by Rosenthal & Burke titled "Ownership of Total
  U.S. Corporate Equity." That string is a *section heading* in **Rosenthal and Mucciolo**,
  Tax Notes Federal, 1 April 2024 (Burke coauthored the 2020 NYU draft). They recode Fed
  holder categories into tax buckets (taxable 79% in 1965 → 27% in 2022; foreign 42% of
  *their* FDI-inclusive look-through total). They say, verbatim, they **lacked the data** to
  reallocate domestic hedge-fund and PE-fund holdings to the funds' owners, so PE stays in
  the taxable leftover. Holmquist (2019) subtracts nonprofits and leaves PE in B.101.h.
  Smith–Zidar–Zwick (2023) capitalize tax flows through 2016; they do not split `FU153064105`.
  On F51, domestic hedge-fund equity is already a named holder from 2012:Q4.
- **Correct position.** The residual has been relabelled by tax status and split from
  nonprofits. It has not been decomposed into PE funds vs personal trusts vs natural persons.
  Do not quote 42% or 27% as Z.1 shares (2022:Q4 household is 39.4% of the instrument, RoW
  16.6%). Do not cite Rosenthal & Burke (2024).
- **Still standing at:** `Parcel_LIT1_Residual_Literature_For_Gemini_DeepResearch.md` (the
  brief that asked the map); the 15 Sep ranked-block wording, rewritten in place.

## C-083 · "The buying is unattributable by design" / "irreducibly unattributable on free data"

**Mine, 14 Sep** — the headline of `2026-09-14-HR-The-Household-Residual.md`, carried into the
synthesis as "the official accounts say it came from the people nobody counts," and used to kill
N4's original form.

- **Killed by:** ETF1, 15 Sep — `2026-09-15-ETF1-Identity-Net-Of-ETF.md`. The rebuild C-081 asked
  for: strip ETF share issuance, split the wrapper by ICI fund type, split listed from closely-held.
- **What is wrong.** Issuance over 2024:Q1–2026:Q2 *is* attributable. ETF shares were +$3,603.8bn
  of the +$3,243.1bn Z.1 total; operating companies retired $540.7bn; issuance net of ETF shares
  is −$360.7bn. Of the wrapper, bond funds were **$1,065.0bn (29.6%)** — ICI Fact Book Table 13
  reproduces the 2024 and 2025 annual sums to $0.3bn. Calling that "unattributable" treated a
  residual *holder* line as if the *issuer* side had nothing to say. It did.
- **What still stands.** The household line is still a plug. Private equity funds and personal
  trusts are still inside it. We still cannot split household holdings of this instrument into
  ETF shares versus listed stocks versus closely-held/PE. That is LIT1. It is a narrower claim
  than "we cannot say who bought the equity."
- **Correct position.** The net new instrument created was ETF shares, of which three-tenths wrap
  bonds. Households matched the wrapper. Operating companies were not the supply. Do not quote a
  household operating-company purchase number from this instrument; do not say the buying cannot
  be attributed.
- **Still standing at:** `2026-09-14-SYN-What-We-Can-Say.md` (one-paragraph money sentence and
  §2 "the hole"; bannered), `2026-09-14-HR-The-Household-Residual.md` (headline and conclusion;
  bannered), `_research/2026-09-14-N4-Frame.md` (bannered), `2026-09-14-I2-IPO-Allocation.md:75`,
  `Parcel_SYN1_Attack_The_Synthesis_For_Grok_Cursor.md` and
  `Parcel_LIT1_Residual_Literature_For_Gemini_DeepResearch.md` (the briefs that posed the claim).

## C-082 · "Roughly two-fifths of the compression is genuinely cheaper risk" — the survey measure says no such thing

**Mine, 14 Sep** — the headline of `2026-09-14-P5iv-Third-Premium-Measure.md`, carried into the synthesis and
stated to the principal as the best estimate of the risk-versus-growth split.

- **Killed by:** the SYN1 adversarial return (Grok in Cursor, 15 Sep), verified by me the same hour against
  our own SPF file.
- **What is wrong.** The survey premium is `STOCK10 − BOND10`. Over the window:

  | | Q1-2024 | Q1-2026 | change |
  |---|---:|---:|---:|
  | STOCK10 (expected 10y equity return) | 7.1513% | 7.3056% | **+15.4bp** |
  | BOND10 (expected 10y bond return) | 3.5527% | 3.8979% | **+34.5bp** |
  | ERP | 3.5986% | 3.4077% | −19.1bp |

  **Forecasters expected MORE from equities at the end of the window than at the start.** The premium fell
  only because the bond leg rose further. **Calling that "cheaper risk" inverts what the survey says.**
- **Two further amendments from the same return, both fair:** the monotonic ordering of the three measures is
  collinear with how much each series is *allowed* to move, and is not identified as growth control; and the
  synthesis quietly dropped Damodaran's real-basis figure (−29.3bp), which reads as roughly 60% risk — the
  opposite split from the one I reported.
- **Correct position.** The gap between the earnings yield and the real rate compressed. **Whether that
  reflects cheaper risk, higher growth, or a repricing of bonds is UNRESOLVED, and the two-fifths/three-fifths
  split must not be quoted.** The direction is corroborated across three constructions; the decomposition is
  not. Surveys also extrapolate past returns (Greenwood-Shleifer), which the earlier write-up noted and then
  under-weighted.

## C-081 · "The equity base grew ~$1trn a year" and "households absorbed 94.6% of net new equity issued"

**Mine, 13-14 Sep** — the supply-side finding in `2026-09-13-S1-Supply-Decomposition.md`, the household
result in `2026-09-14-HR-The-Household-Residual.md`, the assembled answer in
`2026-09-14-SYN-What-We-Can-Say.md`, and the published artifact. Stated to the principal repeatedly.

- **Killed by:** the SYN1 adversarial return (Grok in Cursor, 15 Sep), verified by me the same hour against
  our own files and the Fed's own documentation.
- **What is wrong.** Z.1's "corporate equities" instrument **includes ETF shares as an issuance layer on top
  of operating-company equity.** Our own issuer-side file shows it plainly and I had the row in front of me
  on 13 Sep and set it aside as "a different concept":

  | issuer side, 2024:Q1-2026:Q2 | $bn |
  |---|---:|
  | **Exchange-traded funds (FU564090005.Q)** | **+3,603.8** |
  | Holding companies | −343.8 |
  | **Nonfinancial corporate business** | **−540.7** |
  | Rest of the world | +382.2 |
  | all other financial issuers | ~+215 |
  | **total net issuance** | **+3,243.1** |

  **`FA564090005.Q` is column 9 of the Fed's own F51.1.t corporate-equity flow table** — I checked. ETF share
  creation is inside the issuance identity by construction.
- **So: operating companies were NET RETIRERS of $540.7bn over the window, while ETFs created $3,603.8bn of
  shares.** "The equity base grew about a trillion a year" describes **the growth of the ETF wrapper layer,
  not of corporate equity.** And "households absorbed 94.6% of net new equity" is largely **households
  buying ETF shares** — including bond ETFs.
- **The Fed says so itself** (Z.1 Technical Q&A, fetched 15 Sep 2026): *"the value of some ETF shares is
  based on underlying debt securities"*, and *"it would be preferred to show this type of pass through
  activity by ETF companies separately... it is necessary to include issuance of ETF shares by ETF companies
  together with issuance of other corporate equity shares by other sectors due to data limitations."*
- **IMPORTANT — what the Fed does NOT concede, and where Grok overreached.** The same Q&A states: *"because
  any corporate equity held by ETF companies is recorded on the holdings side, the underlying equity is
  accounted for only once. As a result, the household sector's holdings of corporate equities are not
  distorted by the inclusion of ETF shares."* **The accounting is internally consistent; there is no double
  count.** The error was mine and it was one of INTERPRETATION — I read an aggregate that contains a wrapper
  layer as though it were operating-company issuance, and read households absorbing that layer as though it
  were unmeasured stock buying.
- **Correct position.** Two statements, and they must travel together: (1) **operating companies retired
  equity on net over 2024:Q1-2026:Q2** — the listed base did not grow, it shrank; (2) **the growth in the
  Z.1 aggregate is ETF share creation**, a wrapper households bought, part of it bond exposure. The word
  "supply boom" must not be used of corporate equity again without saying which layer.
- **What survives untouched:** the 93/7 revaluation split (a statement about total value change), the
  earnings decomposition, the premium work, the concentration findings, and the S1 gross-issuance result
  from the Fed's EFA series, which is a different source measuring nonfinancial corporates only.

## C-080 · "No published multiplier reaches 13.47, so flows cannot be the whole story — they explain 11%-70% of the repricing"

**Mine, 13 Sep, the B0 bound** — written into `2026-09-13-B0-The-Bridge-Frame.md`, ranked into
RESEARCH_STATE section 5 as a Tier B result, and stated to the principal as a finding the same day.

- **Killed by:** the BR2 challenge (Grok in Cursor, 13 Sep), verified by me against
  `data/z1_equity_netbuyers/netbuyers_periods_2026Q2.csv` within the hour.
- **What is wrong.** The bound divided revaluation by Z.1's *net* flow ($3,243.1bn). Gross net-purchases by
  the buying sectors over the same period were **$6,886.8bn** — I re-summed the positive holder flows and it
  ties to the net exactly (6,886.8 − 3,643.7 = 3,243.1). On that denominator the implied multiplier is
  **6.34, comfortably inside the published envelope**, and the envelope then explains **24%-148%** of the
  repricing rather than 11%-70%. **Flows explaining the entire repricing is therefore not excluded.**
- **The deeper error, and it is the one to remember.** Both numbers are *equilibrium quantities*, not the
  *demand shift* the multiplier is defined on. Gabaix-Koijen define M on a portfolio shift into equities;
  Z.1's net flow is what the market cleared at. Dividing a price change by an equilibrium quantity and
  calling the ratio an implied multiplier is a category error — the same one that killed C-077 and C-078,
  committed a third time, by me, one day after writing that flows must be shown to cross a boundary before
  they are multiplied.
- **Correct position.** State no bound without naming the flow it applies to. What survives is a conditional
  ceiling: *if* the relevant price-insensitive flow is bounded by net new supply, 9.4 x $3,243.1bn covers 70%
  of the repricing. The condition must travel with the number. A second mismatch also stands and is now large:
  Z.1's $123.7trn stock is public plus closely-held while every published M is estimated on listed markets,
  and S1 showed 89% of record 2026Q1 issuance was private.
- **Also corrected: "only boundary-crossing flows matter" (B0) is too strong.** Jiang, Vayanos & Zheng,
  *Passive Investing and the Rise of Mega-Firms* (19 Jun 2025), verified at source: "the aggregate market can
  rise even when flows are entirely due to investors switching from active to passive funds."

## C-079 · "Hahn et al." — a paper that does not exist, invented by splitting one real paper in two

**Mine, 11 Sep** — introduced in `2026-09-11-P3-Price-Impact-Multiplier.md` by our own Sonnet agent, repeated
in the P3R return, carried into C-077 as the evidence killing M=5, and stated to the principal.

**What it claimed:** *"Hahn et al.'s 2026 re-estimation of GK's exact design with formal specification
testing finds the 12-sector specification that reproduces GK's ~5 is statistically rejected; the
specification that passes their test (6-sector granular core) gives $8.7–$9.4."*

**Killed by my own source check, 13 Sep**, prompted by the BR1 census (Gemini Deep Research) listing no such
paper. What I actually did and found:

- Downloaded and full-text-searched **Gabaix & Koijen** (NBER w28967) and **Li & Lin** ("Price Multipliers
  are Larger at More Aggregate Levels"): **zero occurrences of "Hahn"** in either.
- Searched for the paper itself and found the real one: **Eric Qian, "Heterogeneity-robust granular
  instruments"** (Johns Hopkins, arXiv 2304.01273v4, 27 May 2026). It is the RGIV paper that re-estimates
  GK's design with specification testing — it cites Gabaix and Koijen 42 times, has explicit J tests, and
  names its applications as "sovereign yield spillovers and the inelastic markets [hypothesis]".
  **It contains no "Hahn" either.**
- **The numbers 8.7 and 9.4 appear in none of the three papers.** 9.4 occurs once in Gabaix & Koijen and 8.7
  twice in Li & Lin, in unrelated contexts; as a range from one "passing specification" it has no source.

**So the mechanism of the error was not invention from nothing — it was splitting one real paper into two.**
The P3 document cites "Qian" and "Hahn et al." as separate authorities making different arguments. There is
one paper, by Qian. That is a harder error to catch than a wholly fabricated reference, because the real half
checks out.

**Correct position:** there is no "Hahn et al." in this literature. Do not repeat the J-test rejection or the
8.7–9.4 range. C-077's conclusion survives on independent grounds — see the amendment inside it.

**STILL OPEN, do not treat as settled:** the P3 document also attributes *"~$20"* and a rejection of
between-sector-block homogeneity to Qian. Qian is real and those claims are plausible, but **I have not
extracted his equity numbers from the paper** — I confirmed only that the inelastic-markets application
exists. Anything sourced to "Qian" in our documents is UNVERIFIED until someone reads his results table.

**The process lesson.** Two separate checks failed to catch this. Our own agent produced it on 11 Sep; an
adversarial outside review (P3R, Grok, 12 Sep) *repeated* it while correctly overturning the surrounding
finding. Being right about the substance made the citation easy to wave through, and I verified P3R's
arithmetic and not its references. **Resolve an outside model's citations even when — especially when — its
argument is convincing.** The discipline we apply to Gemini's URLs applies to every name in every return,
including our own agents'.

## C-078 · "The market is 54.7% above a constant-premium counterfactual — the excess is 35.4% of today's valuation"

**Mine, 12 Sep, the P2c headline** — presented as the project's central result and carried into
RESEARCH_STATE §5, the ranked list and the ATT1 parcel.

- **Attacked by:** ATT1 (Grok in Cursor, 13 Sep), verified by me the same day against
  `_research/2026-09-12-P2c-monthly_series.csv` and Damodaran's `ERPbymonth.xlsx` (fetched 13 Sep).
- **What survives.** The arithmetic. Grok recomputed all eight headline numbers from the CSVs and every one
  reproduced (-2.1359, +3.0103, +3.591%, 16.301, 54.722%, 35.368%, 52.246%, +22.754%). **And the WINDOW
  compression survives:** our trailing residual fell 49bp between Dec-2023 and Jun-2026, and Damodaran's
  forward-looking growth-adjusted ERP (T12m) fell 40bp over the same months, 4.60% -> 4.20%. An independent
  construction with an explicit growth term moves the same way, by nearly the same amount. That is real.
- **What is dead: the LEVEL claim.** "35.4% above a constant-premium counterfactual" must not be quoted as a
  result. Three reasons, each verified by me:
  1. **The baseline is a free parameter worth a 4x range.** The identical computation gives 10.9% (base =
     Dec-2023), 16.5% (2023), 28.4% (2005-07), 35.4% (2015-19, ours), 43.1% (2010-19), 31.2% (full sample).
     Our 35.4% is one point in that band, chosen, and was presented as the answer.
  2. **The residual is not a risk premium.** It is E/P - r, which nets expected growth. Damodaran's own
     expected-growth input rose 8.74% -> 13.69% across the same window. Comparing the residual's LEVEL across
     regimes with different g is not comparing like with like; comparing its CHANGE over a short window is
     defensible, which is why (1) survives and this does not.
  3. **The counterfactual sits off the historical manifold.** corr(real yield, trailing residual) = -0.6991
     over 2003-2026 (n=282). Holding the premium at a baseline mean while applying today's real yield pairs
     two quantities that historically move against each other.
- **Also corrected: "the multiple rose only 3.6%" is an endpoint artefact.** The path was 24.3468 (Dec-23) ->
  28.6002 (Dec-24) -> 28.4790 (Dec-25) -> 25.2212 (Jun-26). The multiple rose 17.5% in 2024 and gave it back
  in H1-2026 as trailing earnings jumped 22.75%. Quote the path, never the endpoints alone.
- **Correct position.** Say: *between Dec-2023 and Jun-2026 the equity risk premium compressed by roughly
  40-50bp on two independent constructions, and that compression — not the real-rate move, which was a drag —
  is what held the multiple up.* Do not attach a level, a counterfactual multiple, or a percentage of
  valuation to it without also stating the baseline band.
- **Unresolved and NOT relied on:** Grok's 30-year TIPS point (FII30 1.95% -> 2.72%). FRED refuses scripted
  requests, so it is unverified; it was a supporting remark, not load-bearing.

## C-077 · "Carry an aggregate multiplier M = 5 (range 2-9) and apply it to the Z.1 sector purchase lines"

**Mine, 11 Sep, the P3 frame decision** — a central value of 5 per $1 of price-insensitive net buying, to be
multiplied through P1's sector flows in the attribution.

- **Killed by:** the P3R adversarial check (Grok in Cursor, 12 Sep), `_research/P3R_verification_2026-09-12.md`.
- **Correct position:** no central value. The published aggregate estimates span about $2-$9 and travel as a
  sensitivity envelope only. The specification reproducing ~5 is rejected by Hahn et al.'s own J-test (p<0.001)
  while the passing specification gives 8.7-9.4; the only independent aggregate design gives 1.5-2.3. And M is not
  a scalar for sector lines: ETF-versus-mutual-fund flows are switching between holders, 2015-19's net flow is
  negative against a rising market, and Z.1's stock includes closely-held equity while M's price series is listed.
  Attribution v0 instead runs M in {2, 5, 9} through total net issuance, nonfinancial-corporate net issuance, and
  ETFs minus mutual funds, over 2015-19 and 2024-26.

**AMENDMENT, 13 Sep 2026 — the citation in this entry was fabricated, the conclusion survives on other grounds.**
Checking the BR1 literature census against source, I downloaded Gabaix & Koijen (NBER w28967) and Li & Lin
("Price Multipliers are Larger at More Aggregate Levels") and searched both in full:

- **"Hahn" appears NOWHERE in either paper** (0 hits in ~29,000 and ~34,000 words). There is no "Hahn et al."
  in this literature that I can find. The name entered our record through the P3R return (Grok, 12 Sep) and
  I accepted it without resolving it. **My error: I verified P3R's arithmetic and not its citations.**
- **Neither paper contains a J-test.** Li & Lin: zero hits for J-test or overidentification. Gabaix & Koijen:
  the single apparent hit is "Lars Hansen" in the acknowledgements, not a Hansen J-statistic. So
  *"rejected by its own J-test (p<0.001)"* has no source and must not be repeated.
- **The "8.7-9.4 passing specification" was stitched from two different papers**: 9.4 occurs once in Gabaix
  & Koijen, 8.7 twice in Li & Lin. It is not one specification's output.

**What IS true, verified at source 13 Sep:** Gabaix & Koijen do state a flow of $1 "increases the market's
aggregate value by about $5", and their paper carries specifications giving M = 5.0, 5.3, 5.9, 7.1, 7.7,
10.9 and 15 — so the dispersion is *within* the founding paper, not just across papers. Li & Lin report
1.73 (idiosyncratic), 3.12 (granular style) and 6.98 (aggregate) — all three verified present in the PDF,
and that ordering IS their finding: multipliers rise with the level of aggregation.

**The conclusion of C-077 stands and is now better supported.** Do not carry a central M, and do not apply
a scalar M to Z.1 sector lines — not because of a J-test that does not exist, but because (a) the estimate
depends on aggregation level by design (Li & Lin), (b) it ranges 0 to ~7 across identification strategies
with the structural/dynamic designs at the low end (BR1 census, 13 Sep), and (c) the sector-line objections
in this entry were always independent of any single paper.
- **Rule:** a frame decision that an outside reviewer can overturn on the papers' own specification tests was not a
  decision, it was a default. Name the test that would break it before carrying it.
- **Still standing at:** nowhere — `2026-09-11-P3-Price-Impact-Multiplier.md` and RESEARCH_STATE.md section 5 item 4
  were corrected on 12 Sep.

---

## Machine-readable ban list

`bin/check.sh` greps drafts against these. One regex per line, `id<TAB>regex`.
Keep patterns narrow — a false positive that fires constantly gets the check switched off.

> **ENGINE CONSTRAINT — read before adding a pattern (found 22 Aug 2026, C-041).** `grep` on
> this machine is **ugrep 7.8.4**, whose DFA rejects *two or more bounded repeats `.{0,N}`
> combined with an alternation group* — `NDFI.{0,40}(buy|purchas).{0,20}securit` raises
> *"exceeds complexity limits"*. `check.sh` sent stderr to `/dev/null`, so such a pattern
> **matched nothing and reported nothing**, and the run still printed `✓ no killed claims
> found`. **C-017, C-020 and C-030 were dead this way — C-030, the withdrawn-framing kill,
> had never once been enforced.** Split into several same-id lines instead; the same id may
> appear on as many lines as needed. `check.sh` now validates every pattern first and fails
> loudly. Re-run `bin/check.sh --all` after editing this block.
>
> **SECOND ENGINE CONSTRAINT — a pattern beginning with `-` (found 15 Sep 2026).** `grep -nEi "$rx"`
> consumes a pattern that starts with a hyphen as an **option bundle**: it matches nothing, raises no
> error, and the validator above still passes it as usable — the same silent-nonenforcement shape as
> the ugrep bug, reached by a different route. Found while registering C-088, whose first pattern was
> `-52\.0%` and enforced nothing. **`check.sh` now passes every pattern with `-e`, which fixes it for
> good.** Audited the same day: of 159 patterns that was the only one affected — no historical kill was
> ever silently unenforced by this route. Prefer anchoring on the figure without its sign.
>
> **THIRD — short acronyms need word boundaries (found 19 Sep 2026).** `grep -i` matched C-020's `NDFI.{0,60}equit`
> inside the HTML class name `sta*ndfi*rst">Why US equit*y` — a permanent false positive on the published page.
> C-020 now uses `\bNDFI\b`, tested both ways (still fires on two real phrasings; silent on the class name). Any
> pattern built on a short acronym should be bounded the same way, or it will eventually fire inside a real word.
>
> **ALLOW-LIST SCOPE — it exempts a FILE, not a LINE (noted 15 Sep 2026).** An allow entry granted because a
> document legitimately quotes a dead claim in its own corrections block also exempts every *live* restatement
> elsewhere in that file. `2026-09-14-SYN-What-We-Can-Say.md` was allow-listed for C-081 and C-083 on that
> basis and then carried both claims in a section heading and in its "What I would bet on" list, invisible to
> the gate. When granting an allow, confirm the file's mention is confined to a banner or corrections block —
> and when a return says a document still smuggles dead phrasing, grep the body, not the banner.

Files that legitimately discuss a dead claim — because they are where it was *killed* —
are suppressed per-id in the `allow` block. Anything firing outside those files is **new
propagation**, which is the only thing this check exists to catch.

```allow
C-116	CORRECTIONS.md	# names the dead phrasing to kill it
C-117	CORRECTIONS.md	# names the dead phrasing to kill it
C-114	CORRECTIONS.md	# names the dead phrasing to kill it
C-111	CORRECTIONS.md	# names the dead phrasing to kill it
C-102	CORRECTIONS.md	# names the dead phrasing to kill it
C-103	CORRECTIONS.md	# names the dead phrasing to kill it
C-103	2026-09-12-P2c-Rates-vs-Risk-Premium.md	# struck in place, phrasing retained under strikethrough
C-104	CORRECTIONS.md	# names the dead phrasing to kill it
C-104	2026-09-13-P5ii-Growth-Versus-Risk.md	# struck in place, phrasing retained under strikethrough
C-106	CORRECTIONS.md	# names the dead phrasing to kill it
C-108	CORRECTIONS.md	# names the dead phrasing to kill it
C-099	CORRECTIONS.md	# names the dead phrasing to kill it
C-098	CORRECTIONS.md	# names the dead figure to kill it
C-098	2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md	# quotes the dead figure to withdraw it
C-098	2026-09-21-W3-Tax-Decomposition.md	# banner names the kill
C-096	CORRECTIONS.md	# names the dead phrasing to kill it
C-096	2026-09-21-W3-Tax-Decomposition.md	# banner names the kill
C-097	CORRECTIONS.md	# names the dead phrasing to kill it
C-086	CORRECTIONS.md	# names the dead phrasing to kill it
C-086	2026-09-15-P4-Russell-Elasticity-Pilot.md	# where it was killed
C-086	2026-09-14-SYN-What-We-Can-Say.md	# banner
C-086	RESEARCH_STATE.md	# ranked block records the kill
C-086	CLAUDE.md	# read-table row names the kill
C-086	2026-09-13-B0-The-Bridge-Frame.md	# B3 row rewritten in place
C-086	_research/2026-09-12-P4-Flow-Elasticity-Spec.md	# the spec, now run
C-085	CORRECTIONS.md	# names the dead phrasing to kill it
C-085	2026-09-15-N4-Scale-Timing-Bound.md	# where it was killed
C-085	2026-09-14-SYN-What-We-Can-Say.md	# banner
C-085	_research/2026-09-14-N4-Frame.md	# poses the dead question to kill it
C-085	RESEARCH_STATE.md	# ranked block records the kill
C-085	CLAUDE.md	# read-table row names the kill
C-084	CORRECTIONS.md	# names the dead phrasing to kill it
C-084	2026-09-15-LIT1-Residual-Literature.md	# where it was killed
C-084	2026-09-14-HR-The-Household-Residual.md	# banner
C-084	2026-09-14-SYN-What-We-Can-Say.md	# banner
C-084	_research/2026-09-14-N4-Frame.md	# banner
C-084	RESEARCH_STATE.md	# ranked block records the kill
C-083	CORRECTIONS.md	# the correction names the dead phrasing to kill it
C-083	2026-09-15-ETF1-Identity-Net-Of-ETF.md	# where it was killed
C-083	2026-09-14-SYN-What-We-Can-Say.md	# corrected in place with a banner
C-083	2026-09-14-HR-The-Household-Residual.md	# corrected in place with a banner
C-083	_research/2026-09-14-N4-Frame.md	# corrected in place with a banner
C-083	Parcel_SYN1_Attack_The_Synthesis_For_Grok_Cursor.md	# the parcel that elicited the claim under attack
C-083	Parcel_LIT1_Residual_Literature_For_Gemini_DeepResearch.md	# poses the claim as the thing to check
C-083	2026-09-14-I2-IPO-Allocation.md	# side mention of the residual; left in place
C-081	2026-09-15-ETF1-Identity-Net-Of-ETF.md	# names the C-081 claim in order to carry the rebuild
C-082	CORRECTIONS.md	# the correction names the dead split to kill it
C-082	2026-09-14-P5iv-Third-Premium-Measure.md	# corrected in place with a banner
C-081	CORRECTIONS.md	# the correction must name the dead phrasing to kill it
C-081	2026-09-14-SYN-What-We-Can-Say.md	# corrected in place with a banner
C-081	2026-09-14-HR-The-Household-Residual.md	# corrected in place with a banner
C-081	2026-09-13-S1-Supply-Decomposition.md	# corrected in place with a banner
C-078	2026-09-14-SYN-What-We-Can-Say.md	# the synthesis names the dead claim in its corrections section, to record it as dead
C-080	2026-09-13-B0-The-Bridge-Frame.md	# where it was killed; the amendment must name the number
C-079	2026-09-11-P3-Price-Impact-Multiplier.md	# where it was killed; banner added 13 Sep
C-079	CORRECTIONS.md	# the amendment names the fabricated citation in order to kill it
C-079	_research/P3R_verification_2026-09-12.md	# the return that introduced it, preserved
C-078	ATT1_verification_2026-09-13.md	# Grok's return preserved verbatim under a correction banner
C-078	2026-09-12-P2c-Rates-vs-Risk-Premium.md	# where it was killed; the retraction must name the number
C-078	Parcel_ATT1_Premium_Attack_For_Grok_Cursor.md	# the parcel that elicited the refutation, quotes the claim under attack
C-076	2026-09-11-P3-Price-Impact-Multiplier.md	# the agent's return, preserved under a correction banner
C-020	2026-08-21-Singh-And-The-Two-Circuits.md	# item 6 of the do-not-say list — where it was killed
C-046	2026-08-22-Parcel-B-Numbers-Return.md	# where it was killed
C-048	2026-08-22-Parcel-C-FERC-Return.md	# preserved under a correction banner as the record
C-048	Parcel_C_FERC_Dockets_For_Gemini.md	# the parcel that elicited it
C-050	2026-08-22-Parcel-D1-Scouting-Return.md	# where it was killed
C-050	D1_Scouting_Return_gemini_ondisk.md	# raw return, banner in place
C-052	2026-08-22-D1-Bill-Supply-vs-Shadow-Money.md	# where it was killed
C-052	D1_Scouting_Return_gemini_ondisk.md	# raw external return
C-053	2026-08-22-D2-Who-Holds-The-AI-Paper.md	# carries the amendment and the original under banner
C-053	RESEARCH_STATE.md	# S-D2 amended
C-054	2026-08-23-D3-Cash-Pools-vs-Asset-Management-Structure.md	# §7, where it was killed
C-054	D3_Scouting_Return_gemini_ondisk.md	# raw external return, preserved verbatim
C-054	D3_Scouting_Return_gemini_summary_pasted.md	# principal's paste of the same return
C-055	2026-08-23-Parcel-N3-Collateral-Return.md	# where it was killed
C-055	N3_Collateral_Scouting_Return_gemini_ondisk.md	# raw external return, preserved verbatim
C-056	2026-08-23-D3-Cash-Pools-vs-Asset-Management-Structure.md	# carries the strike-through and §9 amendment
C-056	2026-08-23-Parcel-N3-Collateral-Return.md	# where it was killed
C-057	2026-08-23-Parcel-D8-Clearing-Return.md	# where it was killed
C-057	D8_Clearing_Scouting_Return_gemini_ondisk.md	# raw external return, preserved verbatim
C-058	2026-08-24-Parcel-D8b-Conduit-Return.md	# where it was killed
C-058	2026-08-23-FT-Harvest-ABCP-Conduits-And-Equity-Repo.md	# carries the correction banner
C-058	Parcel_D8b_Conduits_For_Grok.md	# historical artefact, left verbatim as sent (C-046 precedent)
C-059	2026-08-24-Parcel-D8b-Conduit-Return.md	# carries the corrected census and the retraction
C-059	CORRECTIONS.md	# C-058 retraction quotes the dead figures
C-060	Shadow_Debt_Channel_Map.md	# carries the relabelled prose and the historical heading
C-060	2026-08-25-N3-Singhs-Denominator-Reconciled.md	# where the collision was identified
C-061	2026-08-25-N3-Singhs-Denominator-Reconciled.md	# carries the strike and §6 adjudication
C-061	N3R_Velocity_Review_Return.md	# the external review, preserved verbatim
C-061	Parcel_N3R_Velocity_Review_For_Grok.md	# historical artefact, sent as-is
C-062	2026-08-29-D6-Stablecoins-Fifth-Cash-Pool.md	# where it was killed
C-062	D6_Stablecoin_Scouting_Return_gemini_pasted.md	# raw external return, preserved with suspect items marked
C-063	2026-08-29-N2c-The-Funding-Closure.md	# carries the strikes and §7
C-063	2026-08-23-FT-Harvest-ABCP-Conduits-And-Equity-Repo.md	# carries the strike-through and correction banner
C-064	2026-08-29-N2c-The-Funding-Closure.md	# carries the strikes and §7
C-065	2026-08-29-N2c-The-Funding-Closure.md	# carries the strikes and §7
C-063	N2cR_Funding_Closure_Review_Return.md	# the external review, preserved verbatim
C-064	N2cR_Funding_Closure_Review_Return.md	# same
C-065	N2cR_Funding_Closure_Review_Return.md	# same
C-064	Parcel_N2cR_Funding_Closure_Review_For_Grok.md	# historical artefact, sent as-is
C-063	Parcel_N2cR_Funding_Closure_Review_For_Grok.md	# same
C-065	Parcel_N2cR_Funding_Closure_Review_For_Grok.md	# same
C-046	Funding_Identity_First_Principles.md	# carries the C-046 correction banner
C-046	2026-08-21-Safe-Asset-Share-Reexamined.md	# carries the C-046 withdrawal note
C-046	Review_Prompt_For_Gemini.md	# poses it as the verification task
C-046	Review_Prompt_For_Grok.md	# historical artefact, left verbatim as sent
C-046	2026-08-22-Grok-External-Review.md	# the review that first said it cannot be verified
C-046	Parcel_B_Essay_Numbers_For_Gemini.md	# poses it as the task; instructs no yes/no
C-046	Review_Prompt_For_Gemini_Retrieval.md	# same
C-043	2026-08-22-Nexus-WP11289-Read.md	# where it was killed
C-044	2026-08-22-Nexus-WP11289-Read.md	# where it was killed
C-036	Review_Prompt_For_Gemini_Retrieval.md	# header lists it as EXCLUDED from the parcel
C-039	Review_Prompt_For_Gemini_Retrieval.md	# same, and D2 poses it as an open question
C-042	RESEARCH_STATE.md	# carries the amendment
C-042	2026-08-22-Nexus-Primary-Sources.md	# where it was killed
C-041	RESEARCH_STATE.md	# states the corrected goal
C-041	CLAUDE.md	# states the corrected goal
C-035	2026-08-21-Singh-And-The-Two-Circuits.md	# where the discount-rate finding was made
C-036	2026-08-21-Singh-And-The-Two-Circuits.md	# item 13 flagged it first
C-035	Review_Prompt_For_Grok.md	# historical artefact
C-036	Review_Prompt_For_Grok.md	# historical artefact
C-036	2026-08-22-Grok-External-Review.md	# quotes the claim under review
C-037	2026-08-22-Grok-External-Review.md	# same
C-039	Review_Prompt_For_Gemini.md	# poses it as the verification task
C-039	2026-08-21-Inbox-Harvest-And-Research-Plan.md	# annotated 22 Aug
C-035	RESEARCH_STATE.md
C-036	RESEARCH_STATE.md
C-037	RESEARCH_STATE.md
C-038	RESEARCH_STATE.md
C-039	RESEARCH_STATE.md
C-036	Review_Prompt_For_Gemini.md
C-035	Review_Prompt_For_Gemini.md
C-039	2026-08-21-Offshore-Dollar-And-Money-Like.md
C-001	2026-08-22-Guarantee-Stack.md	# explains HOW the ghosts arose (no XBRL tag) and supplies the sourced replacement
C-001	RESEARCH_STATE.md	# same, in S10
C-031	Review_Prompt_For_Grok.md	# historical artefact, left verbatim
C-032	Review_Prompt_For_Grok.md	# same
C-033	Review_Prompt_For_Grok.md	# same
C-031	Review_Prompt_For_Gemini.md	# states the kill explicitly
C-032	Review_Prompt_For_Gemini.md	# same
C-033	Review_Prompt_For_Gemini.md	# same
C-031	2026-08-21-Inbox-Harvest-And-Research-Plan.md	# superseded by 22 Aug pass
C-032	2026-08-21-Inbox-Harvest-And-Research-Plan.md	# same
C-033	2026-08-21-Inbox-Harvest-And-Research-Plan.md	# same
C-031	2026-08-22-Guarantee-Stack.md
C-032	2026-08-22-Guarantee-Stack.md
C-033	2026-08-22-Guarantee-Stack.md
C-034	2026-08-22-Guarantee-Stack.md
C-031	RESEARCH_STATE.md
C-034	RESEARCH_STATE.md
C-032	RESEARCH_STATE.md
C-028	Review_Prompt_For_Gemini.md	# review parcel — states current position, cites the corrections
C-029	Review_Prompt_For_Gemini.md	# same
C-030	Review_Prompt_For_Gemini.md	# same — asks the reviewer to judge the withdrawal
C-024	Review_Prompt_For_Gemini.md	# listed under known-broken
C-022	Review_Prompt_For_Gemini.md	# safe-asset share task
C-030	2026-08-22-Grok-External-Review.md	# the review that killed it
C-030	CLAUDE.md	# states the withdrawal
C-030	RESEARCH_STATE.md	# states the withdrawal
C-028	Review_Prompt_For_Grok.md	# historical artefact — left verbatim as sent 21 Aug; the errors are WHY the review found them
C-029	Review_Prompt_For_Grok.md	# same
C-030	Review_Prompt_For_Grok.md	# same
C-001	2026-08-21-Inbox-Harvest-And-Research-Plan.md	# discusses the lease-figure provenance question
C-001	2026-08-22-Grok-External-Review.md	# names C-001 as already propagated
C-024	Funding_Identity_First_Principles.md	# annotated 21 Aug 2026
C-024	2026-08-21-Singh-And-The-Two-Circuits.md	# annotated
C-024	RESEARCH_STATE.md	# annotated
C-024	2026-08-21-Inbox-Harvest-And-Research-Plan.md	# where the conflict was raised
C-027	2026-08-21-Inbox-Harvest-And-Research-Plan.md	# where it was refuted
C-001	Funding_Identity_First_Principles.md
C-001	CLAUDE.md
C-001	Panel_Synthesis.md	# annotated 21 Aug 2026, banner in place
C-001	Panel_Individual_Reads.md	# annotated 21 Aug 2026, banner in place
C-003	Funding_Identity_First_Principles.md
C-004	Third_Derivative_Concept_Map.md
C-005	Third_Derivative_Concept_Map.md
C-006	Third_Derivative_Concept_Map.md
C-009	Shadow_Debt_Channel_Map.md
C-009	Shadow_Debt_Measurement_Handbook.md
C-011	CLAUDE.md
C-012	CLAUDE.md
C-013	2026-08-21-Offshore-Dollar-And-Money-Like.md
C-014	2026-08-21-Offshore-Dollar-And-Money-Like.md
C-014	RESEARCH_STATE.md	# quotes it as the killed position in the K3 contested table
C-015	RESEARCH_STATE.md	# same
C-014	Shadow_Debt_Measurement_Handbook.md	# annotated 21 Aug 2026
C-015	2026-08-21-Offshore-Dollar-And-Money-Like.md
C-022	2026-08-21-Offshore-Dollar-And-Money-Like.md	# annotated 21 Aug 2026
C-022	2026-08-21-Safe-Asset-Share-Reexamined.md
C-023	2026-08-21-Safe-Asset-Share-Reexamined.md
C-022	RESEARCH_STATE.md
C-023	RESEARCH_STATE.md
C-028	2026-08-22-Grok-External-Review.md	# where the ranking was killed
C-028	2026-08-21-Singh-And-The-Two-Circuits.md	# already has the correct rank
C-028	RESEARCH_STATE.md	# S4 carries the correction
C-029	2026-08-22-Grok-External-Review.md	# where the window-stripping was killed
C-029	Funding_Identity_First_Principles.md	# source table, window present
C-029	RESEARCH_STATE.md	# S2 annotated with the window 22 Aug 2026
C-066	2026-08-30-D10-Reuse-On-The-Measured-Chain.md	# struck in place with correction banner
C-066	D10R_Reuse_Review_Return_paste.md	# raw external return, preserved verbatim
C-066	D10R_verification_2026-08-30.md	# verification record quotes the killed phrasing
C-066	Parcel_D10R_Reuse_Review_For_Grok.md	# the parcel that elicited it
C-066	CORRECTIONS.md	# entry quotes the killed claim
C-067	2026-08-30-D10-Reuse-On-The-Measured-Chain.md	# struck in place
C-067	Parcel_D10R_Reuse_Review_For_Grok.md	# the parcel that elicited the kill, quotes the claim
C-075	2026-08-30-D10-Reuse-On-The-Measured-Chain.md	# original five-bank table, superseded in place by §6 item 2
C-075	Parcel_D10R_Reuse_Review_For_Grok.md	# the parcel that elicited it, quotes the claim under review
C-075	2026-08-30-Singh-Ask.md	# quotes the dead five-bank figure only to state the correction
C-067	D10R_Reuse_Review_Return_paste.md	# raw external return
C-067	D10R_verification_2026-08-30.md	# verification record
C-067	CORRECTIONS.md	# entry quotes the killed claim
C-068	_research/N2aS_verification_2026-08-30.md	# struck in place
C-068	CLAUDE.md	# standing trap rule names the frozen file as the thing NOT to use
C-068	2026-08-30-N2a-Offshore-Dollar-Leg.md	# names the frozen file as the thing NOT to use
C-068	Parcel_N2aR_Offshore_Review_For_Grok.md	# parcel warns the reviewer off the frozen file
C-068	CORRECTIONS.md	# entry quotes the killed claim
C-069	2026-08-30-N2a-Offshore-Dollar-Leg.md	# struck in place
C-069	N2aR_Offshore_Review_Return_paste.md	# raw external return
C-069	N2aR_verification_2026-08-30.md	# verification record
C-069	CORRECTIONS.md	# entry quotes the killed claim
C-069	Parcel_N2aR_Offshore_Review_For_Grok.md	# parcel quotes the claim under attack
C-070	2026-08-31-N2b-zk-The-Wholesale-Share.md	# struck in place
C-070	Parcel_N2bR_zk_Review_For_Grok.md	# the parcel that elicited the kill, quotes the claim under attack
C-070	N2bR_zk_Review_Return_paste.md	# raw external return
C-070	N2bR_verification_2026-08-31.md	# verification record
C-070	CORRECTIONS.md	# entry quotes the killed claim
C-071	2026-08-30-D10-Reuse-On-The-Measured-Chain.md	# corrected in place
C-071	2026-08-30-Singh-Ask.md	# corrected in place
C-071	_research/D10R_verification_2026-08-30.md	# corrected in place
C-071	CORRECTIONS.md	# entry quotes the killed claim
C-072	2026-08-31-N3v4-Singh-Reconciliation.md	# struck in place
C-072	2026-08-30-Singh-Ask.md	# corrected in place
C-072	CORRECTIONS.md	# entry quotes the killed claims
C-073	2026-08-31-N3v4-Singh-Reconciliation.md	# struck in place
C-073	CORRECTIONS.md	# entry quotes the killed claim
C-073	_research/singh_briefing_drafts/WINNER_replication-first.md	# unsent draft, carries the overstatement by design
C-073	_research/singh_briefing_drafts/draft1_question-first.md	# unsent draft
C-073	_research/singh_briefing_drafts/draft3_mechanism-first.md	# unsent draft
C-072	_research/SB1_Briefing_Verify_Return_paste.md	# the return that caught them
C-073	_research/SB1_Briefing_Verify_Return_paste.md	# ditto
C-074	2026-08-31-N3v4-Singh-Reconciliation.md	# rewritten in place
C-074	CLAUDE.md	# the standing rule quotes the killed calibration as its example
C-074	CORRECTIONS.md	# entry quotes the killed claim
C-087	2026-09-15-DG-Remainder-Leveraged-ETF-Flows.md	# the doc that refuted it
C-088	2026-09-15-DG-Remainder-Leveraged-ETF-Flows.md	# the table under correction, preserved as the record
C-089	2026-09-14-A1-Money-Creation-Link.md	# the amendment that kills it
C-089	Parcel_SYN1_Attack_The_Synthesis_For_Grok_Cursor.md	# the parcel that asked for the attack
C-090	2026-09-15-B6-Phase1-Payment-Day-Mechanism.md	# the doc under correction, banner at top
C-091	_research/2026-09-16-NYSE-Payment-Date-Scout.md	# the scout that answered the wrong question, kept
C-092	2026-09-16-TierB-E005-Resolution-Limit.md	# the standing note, bannered
C-086	2026-09-16-TierB-E005-Resolution-Limit.md	# quoted only inside the note's own 'must not claim' table
C-090	2026-09-16-TierB-E005-Resolution-Limit.md	# ditto - confined to that table, body checked 16 Sep
C-078	2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md	# confined to the do-not-quote line in section 1
C-089	2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md	# confined to section 5 'What we cannot say'
C-089	2026-09-14-SYN-What-We-Can-Say.md	# confined to the superseded pointer's correction record
C-081	2026-09-14-SYN-What-We-Can-Say.md	# ditto - preserved banners only, body is now a pointer
C-093	2026-09-18-EPS-Split.md	# the doc under correction; banner at top, tables report the raw figures
C-094	2026-09-20-W1-The-Leak-Objection.md	# confined to the status line and the do-not-say list
C-095	CORRECTIONS.md	# the entry quotes the dead framing
```

```banned
C-086	P4 (elasticity|multiplier|LATE)
C-086	rescale.{0,40}Russell
C-086	rescale.{0,40}P4
C-086	IWB.{0,30}official Russell
C-085	ran through nonbank
C-085	2024 private[- ]repo.{0,40}new cash
C-084	residual HAS been decomposed|has been decomposed
C-084	Rosenthal & Burke \(2024\)|Rosenthal and Burke \(2024\)
C-083	irreducibly unattributable|unattributable by design|do not know who bought essentially any|genuinely unattributable with free data|nearly half the buying is unattributable
C-082	two-fifths (of the compression )?is (genuinely )?cheaper risk|2/5 risk,? 3/5 growth|~2/5 risk
C-081	equity base grew.{0,24}(trillion|\$1trn|a year)|supply boom is overwhelmingly private|households absorbed 94\.6%
C-080	no published multiplier reaches 13|implied multiplier would be 13\.47|flows explain 11%-70%|11% *. *70% of the repric
C-079	Hahn et al|Hahn'?s (12-sector|own) (GIV|J-test)|rejected by (its|their) own J-test
C-078	35\.4% of today|54\.7% above|35\.4% above|constant[- ]premium counterfactual|16\.3 (implied |counterfactual )?multiple|multiple rose only 3\.6
C-001	\$6[67]0bn|\$662[bn ]|\$970bn.*lease|lease.*\$970bn|not[- ]yet[- ]commenced.*\$6
C-003	without M1|M1 to M3.*not|aggregates.*did not move.*ZIRP
C-004	AWS.*(dark|stranded) fibre|Azure.*(dark|stranded) fibre|AWS.*ran on.*fibre
C-005	2\.7% (of )?(the )?fibre|dot-?com.*skills (residue|glut)
C-006	Cogent.*founded after|Internap.*founded after|post-?crash vulture
C-007	Railway Mania.*time (zone|standard)|mania.*caused.*standard time
C-008	Southwest.*impossible under CAB|CAB.*Southwest.*model
C-009	stablecoins?.*marginal buyer of (T-?)?bills
C-011	ACH matrix|analysis of competing hypotheses.*build
C-012	sqlite.*project folder|WAL.*dropbox|dropbox.*breaks.*rename
C-013	outside every monetary aggregate|in no aggregate anywhere in the world
C-014	unambiguously money creation
C-015	velocity (has been |is )?flat.{0,30}(2-3|two to three) years
C-017	safe-asset share.{0,90}composition
C-017	safe-asset share.{0,90}quantity
C-017	33\.2%.{0,60}null
C-018	sign has inverted|crowding.{0,3}in rather than out|regime change in Treasury supply|KVJ.{0,30}invert
C-019	components of the \$27,033|partition of the runnable
C-020	\bNDFI\b.{0,60}securit
C-020	\bNDFI\b.{0,60}equit
C-020	H\.8 line 26.{0,40}margin
C-021	margin debt.{0,40}(record|surge|inflat)|leverage.{0,30}driving.{0,20}equity valuation
C-022	33\.2%.{0,40}(every year|s\.e\. 0\.003|three decimal)|constant.{0,30}since 1952
C-023	par.{0,20}numerator.{0,30}market.{0,20}denominator|denominator.{0,40}(equities and real estate)
C-024	0\.90% of NFC equity|margin debt.{0,30}(median|bottom of its)
C-027	FIMA.{0,40}(yen|intervention)|foreign official.{0,30}repo.{0,20}draw
C-030	funded (while|when|as|though|although|despite|whilst).{0,40}saving rate
C-030	saving rate.{0,80}(where|puzzle|come from)
C-030	wealth is not real
C-041	ultimate goal.{0,40}(substack|essay|publish|post)
C-041	(essay|substack).{0,20}is the (ultimate )?goal
C-042	is not double.counting.{0,40}phenomenon
C-042	interlock is the phenomenon
C-043	Divisia.{0,40}5[0-9](\.[0-9])?[[:space:]]?(trn|trillion)
C-043	DM4.{0,30}(trn|trillion)
C-044	11/190.{0,60}\$6[[:space:]]?(trn|trillion)
C-044	\$6[[:space:]]?(trn|trillion).{0,60}11/190
C-046	83\.7%.{0,40}equity.linked
C-046	equity.linked.{0,40}83\.7
C-048	six RTOs? filed.{0,40}17 August
C-048	show.cause response.{0,30}(17|seventeenth) August
C-048	five.{0,30}defend(ed)? (the )?(status quo|firm.service)
C-050	31688.{0,60}(Acharya|RRP|Liquidity Dependence)
C-050	Staff Report 1068.{0,60}(Afonso|RRP|Cipriani)
C-050	TBACMB
C-050	H41RESPALFOPHAORRP
C-050	Roussanov.{0,40}(moneyness|private claims)
C-052	uninsured deposits.{0,40}7\.1[0-9]?[[:space:]]?(trn|trillion)
C-052	7\.1[0-9]?[[:space:]]?(trn|trillion).{0,40}uninsured
C-053	96%.{0,40}(separate accounts|SMA)
C-053	PIMCO.{0,40}0\.7[0-9]?bn
C-053	2–4bn of the \$27bn
C-031	(halv|halves|half).{0,30}(financing cost|cost of capital)
C-032	Nvidia.{0,40}(tenant|lease).{0,20}Hut 8|Hut 8.{0,40}Nvidia lease
C-033	100bp over Nvidia|~100bp over.{0,20}30-year
C-035	discount-rate account fails on sign|fails on SIGN
C-036	highest of 304 quarters|highest since 1945
C-037	40\.2%.{0,40}14\.3%|factor.share.{0,30}(explains|law)
C-039	Japanese banks (are |account for )?4[0-9]%|Japan.{0,20}47% of.{0,20}residual
C-028	2\.7%.{0,80}lowest since 2005|lowest since 2005.{0,80}(saving|PSAVERT|2\.7%)
C-029	net fixed investment rose only 5\.8% while gross
C-054	jofi\.12696
C-054	jofi\.13028
C-054	rfs/hhw023
C-054	rfs/hhac013
C-054	jfineco\.2020\.12\.007
C-054	CGFS Papers? No\.? ?69
C-054	Derivatives Markets, Central Clearing and Liquidity
C-054	Treasury Yields and Institutional Cash Pools
C-054	Triffin Dilemma.{0,140}WP/11/289
C-054	Mutual Fund Liquidity Management: Evidence from Form N-PORT
C-054	Firm Cash Holdings and the Rise of the Tech Sector
C-055	Collateral Reuse in Euro Area Financial Markets
C-055	Aguiar.{0,20}Biais.{0,20}Crassard
C-055	From sunshine to stormy weather
C-055	Hedge funds' Treasury cash-futures basis trades and financial stability
C-055	Sizing hedge funds' Treasury cash-futures basis trade
C-055	statistics/sftdata\.htm
C-055	Collateral and Re-use Dynamics
C-055	Pledged Collateral and Quantitative Tightening
C-056	FIA.{0,40}member dashboard
C-056	member dashboard.{0,40}(FIA|tracker)
C-057	CCP Initial Margin and Client Clearing Trends in US Treasury Markets
C-057	Cross-Margining and Capital Efficiencies in Cleared US Treasuries and Repos
C-057	Done-Away Model Design Considerations and Market Readiness Survey
C-057	Agent Clearing.{0,60}47 ?(percent|%)
C-057	ACS.{0,40}47 ?(percent|%)
C-057	go-live in Q2 2026
C-057	CME Securities Clearing.{0,60}(went live|launched|is live|now live)
C-059	Chesham.{0,30}2\.[78] ?bn
C-059	aggregator (paper|ABCP).{0,40}17\.6 ?bn
C-059	17\.6 ?bn.{0,40}aggregator
C-061	velocity has kept falling
C-061	velocity of (about |roughly )?1\.5
C-061	falling.{0,20}to (roughly |about |~|≈)?1\.5
C-062	Stablecoins, Run Risk, and Safe Asset Dynamics
C-062	Do Stablecoins Act as Safe Havens
C-062	Dollar Dominance and Digital Currency
C-062	monetary anchor or shadow banking vector
C-062	stablecoin.{0,40}168 ?bn
C-062	168 ?bn.{0,40}stablecoin
C-062	weekly and quarterly.{0,30}(reserve|reporting)
C-062	(120|USD 120).{0,6}135 ?bn
C-063	69(%| percent).{0,40}net bill issuance
C-063	financed by base-money creation
C-063	took ~?69%
C-063	69%.{0,40}net bill supply
C-064	625 ?bn.{0,60}(NDFI|nondepository|engine)
C-064	bigger than the (whole |entire )?ABCP market
C-065	only structural net buyer
C-066	exits on-FICC
C-066	EXITS on-FICC
C-066	the ONE re-use point
C-067	doubled.{0,40}US banks alone
C-067	bank-side numerator has roughly doubled
C-068	Publish/mfh\.txt
C-068	Cayman.{0,25}272\.1
C-069	holdings stood still
C-069	doubled.{0,60}2\.8%
C-069	stood still.{0,40}(TIC|holdings)
C-070	nexus did not expand
C-070	flat at 19\.05
C-070	78\.8% of the private-repo
C-071	Dec-25 permitted figure
C-071	1,771\.0bn.{0,40}1\.8 trillion
C-072	1\.8 trillion.{0,30}0\.5%
C-072	to within 0\.5%
C-072	WP/19/106 p\.15
C-073	independently reproduces Singh
C-073	panel independently reproduces
C-074	32% of the cash-like bucket
C-074	his method is reconstructable
C-075	84(\.0)?%.{0,40}five.bank
C-075	five.bank.{0,40}84(\.0)?%
C-076	Li (&|and) Lin[^\n]{0,60}bias[- ]corrected
C-076	bias[- ]corrected[^\n]{0,25}(≈|~|about |roughly )?\$?5( |,|\.|\)|$)
C-077	aggregate multiplier M ?= ?5
C-077	anchored near \$?5
C-087	150%[^\n]{0,40}breakeven
C-087	150%[^\n]{0,40}break-even
C-087	breakeven[^\n]{0,40}150%
C-087	break-even[^\n]{0,40}150%
C-088	290\.5%
C-088	81\.8%[^\n]{0,25}SOX
C-088	-52\.0%
C-089	too small to have funded
C-089	channel is too small
C-090	payment.day mechanism failed
C-090	B6[^\n]{0,30}mechanism failed
C-090	payment-day mechanism[^\n]{0,30}fail
C-090	B6[^\n]{0,40}refuted
C-091	blocked on[^\n]{0,30}payment.date
C-091	blocked on[^\n]{0,30}pay.date
C-091	free NYSE pay.date[^\n]{0,25}unblock
C-092	JVZ[^\n]{0,40}not supported
C-092	not an underpowered false null
C-092	sharpen[^\n]{0,30}NOT SUPPORTED
C-093	aggregate profit growth[^\n]{0,25}68\.9
C-093	68\.9%[^\n]{0,25}profit growth
C-093	accretion[^\n]{0,15}13\.4%
C-094	leak objection[^\n]{0,30}untested
C-094	untested[^\n]{0,30}leak objection
C-094	load.bearing objection to the whole circuit
C-095	SBC[^\n]{0,40}untested
C-095	stock.based compensation[^\n]{0,30}untested
C-095	untested[^\n]{0,35}R&D capitalisation
C-096	overstates the contractual channel
C-096	[Pp]lausible rebalancing share
C-097	mirrored under project local
C-098	[Pp]re-tax profit.{0,24}74\.2
C-098	pretax 74\.2
C-099	check passes as the brief expected
C-102	held up by the premium, not by rates
C-103	even stronger "it's the premium" verdict
C-104	29 of our 49bp
C-106	sum to the total at source precision
C-108	almost\s+exactly offset by gross issuance
C-111	Rotation, not new demand
C-114	recorded in this row DOES NOT RESOLVE
C-116	13x bigger
C-116	13x larger
C-116	13:1 hinge
C-116	13× the \$86\.2bn
C-117	no budget fixes
```
