# F1 — what the AI build-out is actually funded with: the filings behind the numbers (12 Sep 2026)

**Status: PRIMARY EVIDENCE.** Serves explanandum F (ranked item 7) and item 3 (Green's claims). Data:
`_research/2026-09-12-F1-filings_read.csv` (25 rows), `-tranches.csv` (84 tranches).
**Supervisor verification (12 Sep), read at source in the filings:**
- Alphabet 8-K of 4 Jun 2026: a securities purchase agreement with a Berkshire Hathaway affiliate for
  14,212,035 Class A shares at ~$351.8 plus Class C shares, **$10bn gross, a private placement**.
- Alphabet 424B5 (Series B): proceeds are for "general corporate purposes, including capital expenditures
  to scale AI infrastructure and global compute"; the **$40bn ATM** is for "an administrative change in how
  we meet the tax obligation[s]" of vesting employee awards, not capex; and Alphabet guides **2026 capex to
  $180-190bn, with 2027 significantly higher**.
**What this changes:**
- Alphabet's H1 2026 equity (~$49.6bn) is four instruments, not one: ~$20.5bn underwritten common,
  $10bn placed privately with Berkshire, and two 6.25% mandatory convertible preferred series (~$19bn).
  So the new supply was NOT simply handed to index funds: a named active investor took a fifth of it, and
  mandatory convertibles are typically bought by convertible-arbitrage funds that hedge by shorting the
  common. That cuts against the simplest form of "the passive bid must absorb new issuance" (channel d).
- Oracle fully used a $20bn at-the-market programme ($19.9bn net, 141m shares) with generic use of
  proceeds, and separately sold $5bn of 6.50% mandatory convertible preferred in Feb 2026. Its quarterly
  capex is $28.5bn against $8.5bn a year earlier, with $34.15bn of unconditional purchase obligations and
  operating-lease right-of-use assets up ~$4.3bn in one quarter — leases and purchase commitments are a
  funding leg in their own right.
- **Every bond prospectus across all four issuers says only "general corporate purposes"** — the AI purpose
  is stated in the EQUITY documents, not the debt ones. Do not attribute bond proceeds to capex by assumption.
- **New leg to price: bank credit.** Amazon took a $17.5bn delayed-draw term loan (June 2026) that is not a
  registered security and so is invisible to any prospectus-based count — a direct link from channel (a)
  bank lending to the build-out, and a lead for item 8 (A1).
- Two filing-level discrepancies are recorded, not smoothed: Alphabet's CAD notes 8-K totals C$9.5bn while
  its itemised tranches sum to C$8.5bn; Oracle's two registered 2026 bond deals ($43bn) fall ~$3bn short of
  its fiscal-year XBRL debt proceeds (~$46.1bn).

---

## The filings agent's return (Sonnet)

All three tasks are complete. No SEC request hit a 403/429; every fetch went through the declared User-Agent to sec.gov/data.sec.gov only, with a 1-second pause after each request, run sequentially in the foreground. Deliverables are at `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/wave1/dg1b/filings_read.csv` (25 rows) and `tranches.csv` (84 tranche rows). Denominators are stated in every cell (currency suffixes: USDbn/EURbn/GBPbn/CADbn — none of the non-USD figures were converted by me).

**Task 1 — Alphabet's equity (correcting a gap in the prior finding).** The prior note said no S-3/424B4/424B7 equity prospectus was found for 2026. There is one — it's just a 424B5, not a 424B4/424B7, filed under a new shelf (S-3ASR, File No. 333-296395, filed 2026-06-01). Reading the 8-Ks of 2026-06-04 (accession 0001193125-26-257724) and 2026-06-05 (0001193125-26-259830) and the Series B 424B5 (0001193125-26-257702) shows the $30.499bn "common stock" and $19.063bn "convertible preferred" XBRL lines are actually **four separate instruments priced 2026-06-02 to 06-05**:
- 6.25% Series A and 6.25% Series B Mandatory Convertible Preferred Stock (via depositary shares), $9.5bn net each (full over-allotment exercised) = ~$19.0bn combined, matching the $19.063bn figure. Liquidation preference $1,000/share, dividends quarterly from 2026-08-15, mandatory conversion ~2029-05-15 into a range of common shares (2.252–2.816 per Series A preferred share; 2.274–2.842 for Series B), each series paired with a "capped call" to limit dilution.
- An underwritten public "Stock Offering" of Class A + Class C common, ~$20.5bn net with over-allotment.
- A **private placement to a Berkshire Hathaway affiliate**, named explicitly in the 8-K: $10bn gross, Section 4(a)(2) exempt, disclosed under Item 8.01 rather than Item 3.02 (consistent with the "no Item 3.02" finding — Alphabet's share count here falls under the 1%-of-shares safe harbor).
$20.5bn + $10bn ≈ $30.5bn, matching the $30.499bn figure. A separate **at-the-market program** does exist (entered 2026-06-01, up to $40bn, GS/JPM/MS as managers) — but the filing states its net proceeds are earmarked "primarily to facilitate...an administrative change in how we meet tax obligations associated with vesting of employee equity awards," ~$30bn of it for 2026 tax withholding, not stated as AI-capex-directed. The equity offerings' own use-of-proceeds language, by contrast, explicitly cites "capital expenditures to scale AI infrastructure and global compute," and states Alphabet "expect[s] that capital expenditures in 2026 will be in the range of $180 billion to $190 billion."

**Task 2 — Oracle's $19.909bn.** Confirmed directly in the fiscal Q1 2027 10-Q (accession 0001193125-26-389274), Note 7: "we fully utilized the ATM Program and issued 141 million shares of common stock...for net proceeds of $19.9 billion." The ATM ($20bn ceiling) was established 2026-02-02 and expanded to 17 additional sales agents on 2026-06-23 (424B5, accession 0001193125-26-278585) — no underwritten deal, no named investors. Stated use: generic "general corporate purposes, which may include capital expenditures, repayment of indebtedness, future investments or acquisitions and payment of cash dividends on or repurchases of our common stock" — not AI-specific. Same 10-Q: capex $28,499m for the quarter vs $8,502m a year earlier; "operating and finance leases...primarily relate to our data centers and real estate facilities" (operating lease ROU assets grew from $29.69bn to $33.97bn in the single quarter); unconditional purchase obligations of $34.15bn "primarily related to long-term supply arrangements for purchasing components for cloud infrastructure assets and power supply arrangements for data centers." Incidentally, on 2026-02-05 Oracle also closed a $5.0bn 6.50% Series D Mandatory Convertible Preferred Stock offering (100M depositary shares, 1/2,000th interest each) — a third capital instrument, outside the $19.909bn figure, included in filings_read.csv for completeness.

**Task 3 — Bonds.** Alphabet and Amazon each had three 2026 deals; **Oracle had only two and Meta only one** — I did not find a third for either, which contradicts the brief's assumption, so I'm flagging it rather than forcing a count. All bond deals across all four issuers use generic "general corporate purposes" boilerplate — none mention AI/data-center capex specifically, a sharp contrast with Alphabet's equity documents. One data-quality finding worth flagging: Alphabet's 2026-05-11 8-K states its Canadian-dollar notes total "C$9.5 billion," but the four itemized tranches it lists sum to only C$8.5bn (confirmed against the exhibit count, which lists exactly 4 CAD note forms) — a ~$1bn unexplained gap in the filing itself, noted in filings_read.csv rather than silently corrected. Also found: Amazon has a separate $17.5bn delayed-draw term loan (bank debt via Citibank, June 2026) that isn't a registered security and isn't in tranches.csv, but is relevant financing context. For Oracle, the two bond deals I found ($18bn Sept-2025 + $25bn Feb-2026 = $43bn) fall about $3bn short of the previously-established ~$46.1bn fiscal figure; I did not find a third SEC-registered offering to close that gap.

All CSVs were checked for the declared User-Agent/email string — clean, neither appears in either file.
