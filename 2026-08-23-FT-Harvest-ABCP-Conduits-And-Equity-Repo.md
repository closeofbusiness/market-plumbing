# FT harvest, 23 Aug 2026 — alternative ABCP conduits and the equity-repo squeeze

*Two FT Alphaville pieces read in full from `~/Downloads`: Toby Nangle, "How money-market funds
are providing stock market rocket fuel" (21 Aug 2026) and Robin Wigglesworth, "'The risk of a
deleveraging event is rising'" (29 Jun 2026). **Paid content, paraphrased; no chart reproduced;
quotes under 15 words.** Both cite sell-side notes (JPMorgan — Ho, Vohra, Herckis; Morgan
Stanley; Bank of America) and S&P Global Ratings — **claims, not evidence**, per the inbox-harvest
rule. What we could verify from data we hold is in §2. Serves A12.*

---

## 1. What the pieces claim

**Nangle (21 Aug).** ABCP outstanding has grown ~$100bn year-to-date on DTCC data (JPMorgan),
~$60bn of it in the last two months, driven by non-bank-sponsored "alternative" programmes —
conduits collateralised with financial securities rather than receivables. S&P attributes their
growth to G-SIBs optimising balance sheets under Basel: a prime broker, rather than fund a
client's equity margin loan on its own balance sheet, pledges the collateral to an ABCP conduit,
which issues paper to money-market funds and other cash investors. JPMorgan's note says such
structures can give banks off-balance-sheet funding and *"potentially favorable accounting
treatment."* The causal direction Alphaville proposes: more margin trading → higher equity
financing cost → more conduit lending against equity collateral → more ABCP. Top sponsors shown
(S&P, Dec 2025): Nearwater, JPM, RBC, Guggenheim, CA, Northcross, BSN, BNP, SocGen, TD.

**Wigglesworth (29 Jun).** Morgan Stanley: *"Record equity financing costs, measured by AXW
futures"* — CME's adjusted-interest-rate total-return futures on the S&P 500 — reflect demand for
levered long equity exposure outrunning dealer balance-sheet capacity, concentrated in AI and
semiconductor names; G-SIB surcharge management into quarter-end makes prime brokers conservative;
risk of a deleveraging event at the June quarter-end "has risen." Treasury repo meanwhile
well-behaved, helped by the Fed's reserve management purchases. BofA: equity financing risks
crowding out dealer fixed-income funding capacity. (Nangle's August piece notes nothing had
broken by then.)

## 2. What we verified ourselves, 23 Aug

| Claim | Our check | Result |
|---|---|---|
| ABCP up ~$100bn YTD (DTCC basis) | FRED `ABCOMP`, Fed CP release | **$421bn (31 Dec 2025) → $488bn (19 Aug 2026): +$67bn YTD**; +$52bn in Q2 alone; **+$199bn since Jun-2023**. Same direction, different basis |
| MMFs buy the alt-ABCP paper **[CONFIRMED 24 Aug by definitive census: Chesham $7.159bn, Bennington Stark $1.543bn, Mountcliff $0.698bn — $9.400bn, exact. A same-day attempt to correct this row (C-058) was itself wrong and has been RETRACTED; see C-059 and `2026-08-24-Parcel-D8b-Conduit-Return.md` §2. Note the aggregator universe is far larger than these three names: $41.8bn non-bank-sponsored.]** | N-MFP3 census, Jul–Aug 2026, programme names | **$9.4bn** held by funds naming them: Chesham $7.2bn, Bennington Stark $1.5bn, Mountcliff $0.7bn — *lower bound; programme↔sponsor mapping unverified; Nearwater/Northcross/Guggenheim strings matched no issuer line, so their programmes trade under other names* |
| Fed "reserve management purchases" | FRED `WSHOBL`, SOMA T-bill holdings | **$234bn (YE2025) → $382bn (Mar) → $486bn (Jun) → $538bn (19 Aug 2026)** — **+$304bn YTD**, against +$442bn of net bill issuance YTD (MSPD). ~~The Fed took ~69% of 2026's net bill supply~~ **[C-063: window-mismatched ratio — matched-endpoint recomputation gives 63.6% Dec-31→end-Jul, falling to 44.4% by 26 Aug as August's issuance wave was privately absorbed; per the July MPR only ~$160bn of the ~$250bn of bill buying was RMP, the rest agency-principal reinvestment. See the N2c retraction, §7.]** |
| Equity financing cost at records (AXW) | Not checked — CME data not pulled | Unverified. Measurable; add to handbook |
| Top-sponsor league table | S&P Global Ratings, secondary | Not verified; Nearwater's ~$50bn+ is the number that matters and we found $2.2bn of its likely programmes in MMFs — the rest is elsewhere or under other names |

## 3. What this changes

**3.1 D1 gets its mechanism.** D1 recorded ABCP as the fastest-growing private money-like
component (+69% Jun-23→Aug-26) and could not say why. **Now it can: equity-margin financing via
conduits.** MMF → ABCP conduit → prime broker → levered equity long. That is private shadow money
created to fund leverage against equity market value — precisely the "valuation-as-collateral
channel" of the original brief, funded by the cash of investors who will not buy the equities
themselves.

**3.2 The "missing channel" is not an instrument. It is the bypass.** Two conduits now identified
that connect cash pools to levered accounts *around* dealer balance sheets:
- **FICC-sponsored repo** — Treasury collateral — MMF-side +$741bn Jun-23→Jul-26 (D1 §5.3);
- **Alternative ABCP** — equity/securities collateral — +$67–100bn YTD 2026.
Both are Pozsar–Singh "collateral mining via prime brokerage" rebuilt for Basel III: the dealer
intermediates but does not carry. **D8 is broadened from "sponsored repo" to "conduits."** This is
the strongest answer yet to E2, and it came from a newspaper, not from a retrieval model.

**3.3 The equity/Treasury bifurcation is dealer capacity binding.** Treasury repo calm, equity repo
expensive, G-SIB surcharge the constraint — Duffie's argument, and direct support for **D4**, the
dealer-first re-cut of the channel map. The AXW basis is a **price of dealer balance sheet for
equity leverage** and belongs in the measurement handbook as a series.

**3.4 A Parcel B / C-024 caveat.** If conduits lend *directly* to the levered client (JPMorgan's
"intermediate transactions with a counterparty"), that credit sits **outside FINRA margin debt**.
The margin-debt ratio we just reconciled may understate equity-collateralised credit by the size
of the conduit channel. Same family as "internalised synthetic prime" on the dark-corners list.

**3.5 D1's 2026 window is confounded; 2023–25 is clean.** With the ON RRP at zero, I wrote that
"any further bill absorption must come from private money or cash-pool growth." **Wrong for 2026:
the Fed re-entered as a bill buyer.** Net bill supply to private cash pools in 2026 is ~$140bn,
not $442bn. The 2023–25 result stands (SOMA bills *fell* $38bn over that window); the 2026
extension must net SOMA purchases. D1 §6 amended.

## 4. Source hygiene

FT Alphaville, both pieces, are journalism about sell-side research. Nothing here is promoted to
§2 settled on their say-so; what is promoted (§2 above) is what we re-pulled. The S&P sponsor
chart and JPMorgan's DTCC figure remain unverified claims.

## 5. Registered

- D8 broadened → "conduits: sponsored repo + alternative ABCP" (RESEARCH_STATE §5).
- D1 amended: Fed SOMA bill purchases as a netting term; 2026 window flagged confounded.
- Measurement handbook candidates: CME AXW total-return futures basis; S&P ABCP by sponsor type;
  DTCC CP data; N-MFP3 ABCP holdings by programme.
- Calendar: 30 Sep 2026 quarter-end — observe equity financing cost and ABCP outstanding; the
  June prediction of a deleveraging event did not materialise, the September one is the next test.
