# Oracle's backlog and how it is being financed (12 Sep 2026) — the 15 Sep calendar check, done early

**Status: PRIMARY EVIDENCE.** From the fiscal Q1 2027 10-Q filed 11 Sep 2026 (accession 0001193125-26-389274) and
the FY2026 10-K (0001193125-26-277521). Data: `_research/2026-09-12-Oracle-RPO-facts.csv` (44 rows). Serves
explanandum F and the standing lenses in `Analysis/Panel_Synthesis.md`.

**The numbers that matter**
- **Backlog: $664bn** of remaining performance obligations at 31 Aug 2026, against $455bn a year earlier (+46%),
  and $638bn at 31 May 2026 (+$26bn in the quarter). Only **13% is expected to be recognised as revenue in the
  next twelve months**; 37% in months 13-36; 34% in months 37-60.
- **Off the balance sheet: $288bn of additional lease commitments**, "substantially all related to data center
  arrangements", commencing between fiscal 2027's second quarter and fiscal 2029, for terms of fifteen years and
  more ($260bn at 31 May). This dwarfs everything Oracle has raised in equity or bonds and is the largest single
  funding leg the project has found for the build-out.
- On balance sheet: operating lease liabilities $34.6bn (from $30.2bn), finance leases $9.2bn (from $7.7bn).
- Unconditional purchase obligations **$34.15bn** (from $13.3bn a quarter earlier), for cloud components and
  data-centre power.
- Quarterly capex $28.5bn against $8.5bn a year earlier; equity raised $19.9bn on a fully used $20bn ATM; no new
  debt in the quarter.

**Customer concentration: not disclosed in this filing.** The 10-Q contains no concentration, credit-risk,
single-customer or related-party language at all; it points back to the 10-K, whose risk factor says only that
certain cloud offerings are "more concentrated among a number of large customers", unquantified and unnamed. The
10-K's notes state that no customer reached 10% of total revenues in FY2024, FY2025 or FY2026 — which is
consistent with a backlog that has not yet converted to revenue, and is not evidence either way about who the
backlog is with.

**Supervisor verification (12 Sep).** RPO "$664 billion and $455 billion as of August 31, 2026 and 2025" read
verbatim in the filing; the $288bn sentence read verbatim in the lease note; the lease and purchase-obligation
tables reconcile ($48,050m operating lease payments less $13,429m imputed interest = $34,621m). A process note
against myself: my first three searches for the $288bn figure found nothing because the filing splits the number
across lines — the agent was right and my check was wrong until I read the note itself.

**Also noted for the 30 Sep calendar row:** the $3.3bn guarantee of a lessor's borrowing that the FY2026 10-K
disclosed as maturing in September 2026 is not mentioned anywhere in this 10-Q.

---

## The agent's return (Sonnet)

Both filings were fetched successfully (one request each, 1-second spacing, no 403/429). Findings below; full sourced detail is in the CSV.

**Deliverable:** `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/wave2/oracle/oracle_rpo.csv` (44 data rows: item, value, period, source filing+section, note). No .md files written.

**1. RPO**
- As of Aug 31, 2026 (Q1 FY2027, the 10-Q under review): RPO = **$664 billion**. Filing's own stated prior-year comparative: $455 billion as of Aug 31, 2025 (+46% YoY, both figures stated together in one sentence).
- Recognition timing (Aug 31, 2026): 13% next 12 months, 37% months 13-36, 34% months 37-60, remainder thereafter (16%, my arithmetic — the filing itself never states that last percentage).
- As of May 31, 2026 (FY2026 10-K, accession 0001193125-26-277521): RPO = **$638 billion** (vs. $138 billion a year earlier, per that filing). Timing: 12% / 34% / 34% / remainder(20%, derived).
- **Quarter-on-quarter (my calculation, not filing language): $638B → $664B = +$26 billion, +4.1%.**
- Composition commentary is limited to that timing schedule only — see "not disclosed" below.

**2. Customer concentration**
- The Q1 FY2027 10-Q itself contains **zero** occurrences of "concentration," "credit risk," "single customer," or "related party." Item 1A and Item 3 both explicitly decline to restate anything and point back to the 10-K.
- The FY2026 10-K does address it: a risk factor says Oracle is "more concentrated among a number of large customers" (10 words quoted) in certain OCI offerings — unquantified, no customer named. Separately, its financial-statement notes disclose (paraphrased, since the verbatim sentence runs 18 words): no customer reached a 10% share of total revenues in FY2026, FY2025, or FY2024. Credit-risk mitigation is described only qualitatively (credit evaluations, short payment terms, diversified base) — no customer-specific quantification anywhere in either document.

**3. Financing the backlog**
- Capex (cash): $28,499M for Q1 FY2027 vs. $8,502M Q1 FY2026; $55,663M full FY2026 vs. $21,215M FY2025. Unpaid capex: $6,247M (Aug 31, 2026) vs. $4,010M (May 31, 2026).
- Leases (data centers/real estate): on-balance-sheet operating lease liabilities $34,621M (Aug 31, 2026) vs. $30,190M (May 31, 2026); finance leases $9,185M vs. $7,701M. Off-balance-sheet additional lease commitments: **$288 billion** (Aug 31, 2026, 15-19yr terms) vs. $260 billion (May 31, 2026).
- Unconditional purchase obligations: **$34,150M** (Aug 31, 2026) vs. $13,309M (May 31, 2026) — roughly 2.6x in one quarter.
- Equity financing this quarter: $19.9B raised via a now-fully-utilized ATM program. No new debt issuance disclosed in Q1 FY2027 (only $4,202M of repayments); the $43.0B of senior notes issued was in fiscal 2026, not this quarter.
- No related-party or named-vendor arrangement tied to the backlog in either filing.

**Explicitly NOT disclosed (things a reader might assume are there):**
- No cloud-vs-license or contract-length breakdown of the RPO balance itself — only the four-bucket recognition-timing schedule exists.
- No customer-concentration or credit-risk language of any kind in the Q1 FY2027 10-Q — it is 10-K-only, and the 10-Q doesn't even summarize it.
- No guarantee of any kind appears in the Q1 FY2027 10-Q. The FY2026 10-K disclosed a specific $3.3 billion guarantee of a lessor's borrowing (maturing September 2026, i.e., right after this 10-Q's period) plus a generic customer-indemnification "Guarantees" note — neither is mentioned in the newer filing.
- No named customer, vendor, or related party tied to RPO/backlog in either filing (the only related-type item is an unrelated 15%-owned TikTok USDS Joint Venture investment).

Source files retained in scratch for audit: `submissions.json`, `orcl-20260831.htm`/`.clean.txt` (10-Q), `orcl-20260531.htm`/`.clean.txt` (10-K), and `build_csv.py` used to generate the CSV — all in the same `oracle/` directory as the deliverable.
