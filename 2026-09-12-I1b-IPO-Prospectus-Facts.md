# I1b — the IPO boom from the prospectuses: how much is new money, and who buys (12 Sep 2026)

**Status: PRIMARY EVIDENCE. Supersedes the press figures in `2026-09-11-I1-IPO-Scout.md`.** Ranked item 5.
Data: `_research/2026-09-12-I1b-ipo_prospectus_facts.csv` (10 deals), `-cornerstones.csv` (17 rows).

**The number to carry: US IPOs raised about $112bn of NEW money for companies in 2026 to date**
(nine operating-company deals at the base offer price; $118.2bn including Medline, which priced 16 Dec 2025).
Money paid to existing holders was small by comparison, about $3.8bn — but two deals were mostly or entirely
sales by holders (INNIO $2.43bn, all secondary, the company receives nothing; Jersey Mike's two-thirds secondary),
and Medline's structure routes roughly $1.0-2.0bn of its "primary" proceeds to pre-IPO owners.

**Supervisor verification (12 Sep):** SpaceX's own prospectus re-read at source — 555,555,555 shares at $135.00 =
$74,999,999,925, no selling stockholders, retail allocation routed through Charles Schwab and Fidelity. The agent's
other headline figures match the filings exactly (SK hynix $26.51bn, Cerebras $5.55bn, Medline $6.265bn).

**Who buys, from the filings:** named cornerstone investors appear in only three deals — SK hynix ($7bn: Baillie
Gifford, Coatue, Situational Awareness Partners), Medline ($2.35bn across eight institutions including GIC and
Viking, plus $250m from the founding family) and Fervo ($350m including Norges Bank). SpaceX and Cerebras name
none. Retail routing through brokerages is disclosed only by SpaceX. Five deals reserve about 5% for employees and
friends-and-family.

**Caveats:** no 424B4 discloses whether the over-allotment was exercised, so every "after greenshoe" figure is the
prospectus's own scenario, not an outcome; discovery was not exhaustive (26 of 212 non-SPAC candidates checked by
hand, six new billion-dollar deals found); SPACs (151 filings) and follow-ons are excluded; Pershing Square USA is
a closed-end fund and is kept out of the totals.

---

## The agent's return (Sonnet)

## Summary

I pulled the final 424B4 prospectuses (or F-1/424B4 for the ADS deal) directly from EDGAR for all 4 named deals, plus discovered 6 additional 2026 US IPOs above $1bn via `efts.sec.gov` full-text search. All SEC requests used the declared `ThirdDerivativeResearch/1.0` User-Agent on sec.gov hosts only, spaced ≥1 second apart, run in the foreground; no 403/429 was ever encountered, so no stop-and-report was triggered. The email string was never written to a file (verified by grep against my own output). Deliverables are at:
- `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/wave1/i1b/ipo_prospectus_facts.csv` (10 rows)
- `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/wave1/i1b/cornerstones.csv` (17 rows)

## Deal table — primary vs. secondary (base offering, no over-allotment)

| Deal | Primary (co.) | Secondary (holders) | Total base | Full-exercise total |
|---|---|---|---|---|
| SpaceX (SPCX) | $74,999,999,925 | $0 | **$75.00bn** | $85,749,999,880 (~$85.7bn, net-of-discount basis — greenshoe carries no discount) |
| SK hynix (SKHY, ADS) | $26,507,100,000 | $0 | **$26.51bn** | N/A — no over-allotment granted ("restrictions under Korean law") |
| Cerebras (CBRS) | $5,550,000,000 | $0 | **$5.55bn** | gross $6.38bn / net $6.22bn (no press figure given to check) |
| Medline (MDLN)* | $6,264,999,978 | $0 (cover-page) | **$6.265bn** | gross $7,204,749,966 (~$7.2bn) / net $7,048M |
| Quantinuum (QNT) — *new* | $1,680,000,000 | $0 | **$1.68bn** | net ~$1.82bn |
| Fervo Energy (FRVO) — *new* | $1,890,000,000 | $0 | **$1.89bn** | net ~$2.03bn |
| Jersey Mike's (JMKE) — *new* | $317,000,007 | $682,999,996 | **$1.000bn** (barely — $3 over) | over-allotment is 100% secondary |
| Bending Spoons (BSP) — *new* | $997,560,560 | $683,598,875 | **$1.681bn** | mixed greenshoe |
| INNIO N.V. (INIO) — *new* | **$0** | $2,430,000,000 | **$2.43bn** | 100% secondary — company gets nothing |
| Pershing Square USA (PSUS) — *new, flagged* | $2,025,848,000 (fund, registered tranche) | $0 | **$2.03bn** (+$2.97bn unregistered private placement = $5.0bn combined) | Not an operating company — a closed-end fund. Kept out of totals below. |

*Medline's cover page shows 100% primary, but Use of Proceeds reveals only ~$5,078M of the ~$6,129M net is retained capital (debt paydown/general corporate); ~$1,051M (base) to $1,970M (full exercise) is proceeds from newly-issued shares earmarked entirely to cash out pre-IPO owners — economically secondary, structured as primary via the Up-C mechanism.

## Total 2026 primary proceeds evidenced from filings

Summing company-side gross proceeds at the base offering price across the **9 operating-company deals** (excluding Pershing Square, a fund):
- **All 9 deals (incl. Medline, which priced 2025-12-16): $118,206,660,470 (~$118.2bn)**
- **Strictly 2026-priced only (excl. Medline): $111,941,660,492 (~$111.9bn)** — this is the direct answer to "total 2026 primary proceeds"
- Total secondary (same 9 deals, base): $3,796,598,871 (~$3.8bn)
- If all disclosed company-side greenshoes were exercised in full (none confirmed exercised): primary ceiling rises to ~$131.9bn
- Add Pershing Square USA's registered public tranche if the research wants funds included: +$2.03bn

## Press figures: confirmed vs. not

**Confirmed exactly or within rounding:** SpaceX $75.0bn base (exact) and $85.7bn post-greenshoe (matches the prospectus's own full-exercise Use-of-Proceeds figure exactly, on a net-of-discount basis); SK hynix $26.5bn (exact); Cerebras $5.55bn base (exact); Medline $6.27bn base (filed figure is $6.265bn — a $5M/0.08% difference).

**Confirmed with an important basis caveat:** Medline's "~$7.2bn after over-allotment" matches the filing's **gross** full-exercise figure ($7,204,749,966) almost exactly, but the company's own "net proceeds" full-exercise disclosure is $7,048M — a ~2.2% gap, because Medline's greenshoe shares (unlike SpaceX's) carry the full underwriting discount. Press appears to be quoting gross, not net.

**Cannot confirm actual exercise:** none of these ten 424B4s disclose whether the over-allotment option was actually exercised — every filing predates that decision. The "post-greenshoe" figures I report are each prospectus's own full-exercise *scenario*, not evidence of what happened. Confirming actual exercise would require the 8-K/press release the brief itself flags as the next-step source.

## What the prospectuses disclose about who buys

- **Retail programs:** Only SpaceX and Pershing Square USA explicitly route allocations to retail brokerages (Schwab, Fidelity, Robinhood, SoFi, plus Morgan Stanley's E*TRADE for SpaceX). None of the other 8 deals disclose any retail-platform mechanism.
- **Directed share/reserved-share programs:** SpaceX, Cerebras, Quantinuum, Fervo Energy, and Jersey Mike's each reserve ~5% of the base offering for employees/friends-and-family. SK hynix, Medline, Bending Spoons, and INNIO disclose none.
- **Named cornerstone/anchor investors** (full detail in cornerstones.csv): SK hynix — Baillie Gifford, Coatue, Situational Awareness Partners, $7bn aggregate; Medline — two tiers: Mills Family $250M (locked up) and 8 institutions incl. GIC and Viking Global at $2,350M aggregate (not locked up); Fervo Energy — Atlas Point, Norges Bank (Norway's sovereign fund), Wellington, Capital Research, $350M aggregate; Pershing Square USA — the Manager itself, $250M (with a 25-year lock-up on $100M of it). SpaceX, Cerebras, Quantinuum, Jersey Mike's, Bending Spoons, and INNIO disclosed none. I also checked PayPay Corporation (Qatar Holding, Visa, ADIA — $220M aggregate) but it prices at only ~$880M gross, below the $1bn cutoff, so it's excluded from both deliverable CSVs.

## Caveats

- **Greenshoe exercise** is never disclosed in a 424B4 — confirmed absent across all 10 deals; would require an 8-K or press release, which I did not pursue (out of scope for prospectus extraction, per the brief).
- **ADS deal (SK hynix):** filed under F-1 (Reg. No. 333-296987) as expected; no over-allotment at all due to Korean law; use-of-proceeds capex figures are stated in KRW in the filing, not USD — I did not convert.
- **No unit offerings** appeared among the 10 qualifying deals; unit structures were confined to the SPAC filings excluded below.
- **SPACs excluded:** the 2026 full-text-search universe for 424B4 + "initial public offering" was 363 filings; 151 carried SIC 6770 (blank-check) and were excluded as SPACs, leaving 212 non-SPAC candidates.
- **Discovery is not exhaustive:** I individually verified cover pages for ~26 of those 212 (prioritized by name recognition, SIC code, and structural signals), which is how I found the 6 additional qualifying deals. The other ~186 are mostly small biotechs and micro-caps very unlikely to clear $1bn, but I did not check each one, so I cannot rule out a missed deal with full certainty.
- **Follow-ons look like IPOs in this search and must be filtered:** Ingram Micro, Firefly Aerospace, MACH Natural Resources, Constellation Energy, Rush Street Interactive, Aveanna Healthcare, Alliance Laundry, Legence, and SOLV Energy's second 2026 filing all matched "initial public offering" but are prospectus supplements for already-listed companies (confirmed via "our stock is listed on..." language) — excluded. ContextLogic's filing is a rights offering, not an IPO — excluded.
- **Pershing Square USA is not an operating company** — it's a newly formed closed-end fund under the Investment Company Act of 1940, raising permanent capital to invest in *other* public companies. I've kept its $2.03bn registered tranche and $2.97bn concurrent (unregistered, not part of the 424B4) private placement fully separated from the operating-company totals above; whether to fold it into an "IPO boom" figure is a call for the research team, not made here.
