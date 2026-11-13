# CV1 scoping: what the cited evidence says, and what was known before (13 Nov 2026)

Inputs: two fenced Grok parcels (web; every cited URL fetched; fence held; 13 and 31 successful fetches), a Gemini 4
Hydrogen read of the two Atlanta Fed working-paper PDFs (7 items, 3 absent-fact traps, all correct against the text
layer), and a Sonnet free-data inventory (shape only, blind to outcomes). Supervisor checks: both survey quotes and the
SF Fed Letter's three load-bearing sentences were read at source. Feeds the registration
`_research/2026-11-13-CV1-Confidence-Velocity-Spec.md`.

## The two survey claims the thesis rests on

**"Decision-making is firms' top motive for AI spending": wrong as stated.** Baslandze, Edwards, Graham, McClure, Sparks,
Meyer, Waddell and Weitz, *Artificial Intelligence, Productivity, and the Workforce: Evidence from Corporate
Executives*, NBER WP 34984 = Atlanta Fed WP 2026-4 (March 2026; Richmond Fed revision 27 May 2026). The source is The CFO
Survey, fielded Nov–Dec 2025, about 750 executives, plus an FEI supplement. 58.5% of 723 firms invested in AI in 2025, and
only those firms rated the motives (0–4 scale). Figure 4 means: production efficiency 2.88, decision-making 2.71, labour
productivity 2.71, customers 2.36, products 2.30, workforce skills 2.01, labour costs 2.01, non-labour costs 1.80,
physical capital 1.69. The text calls decision-making "the third most important motive". It does beat the two cost
motives. The paper's Table 3 links a high decision-making rating to *reported* labour-productivity gains, not to
revenue-based productivity. The survey asks how AI changed the book value of PP&E: +0.3% to +1.1% by size class.

**"About 90% of firms report zero productivity gains despite heavy capital deployment": half right.** Yotzov, Barrero,
Bloom, Bunn, Davis and others, *Firm Data on AI*, NBER WP 34836 = Atlanta Fed WP 2026-3 (March 2026). The surveys are the
US SBU (November 2025), the UK DMP, the Bundesbank BOP-F and Australia's BOSS. The text: "89% report no impact of AI on
their labor productivity" (sales per employee, past three years). The base is all respondent firms, users and non-users.
The mean effect is +0.29% over three years, and firms expect +1.4% over the next three. Employment: "more than 90%"
report no impact. The paper does not measure capital spending against that figure; "despite heavy AI-era capital
deployment" is the thesis's addition. The later summer-2026 wave (current NBER abstract) adds that AI spending is
concentrated: 2% of firms account for over half of it.

**Neither paper reports anything on AI reducing uncertainty, on M&A, or on cash holdings.** Hydrogen answered all three
traps "not in the papers", and a grep of the text layer agrees. The thesis's stage 2 therefore has no direct survey support
in its own sources. The nearest item is a "cash management" helpfulness rating.

## Prior art, by stage

- **Stage 3 (uncertainty delays irreversible investment): well supported.** Bloom, Bond and Van Reenen (REStud 2007):
  high uncertainty halves the first-year investment response. Gulen and Ion (RFS 2016): doubling policy uncertainty goes
  with about 8.7% lower investment, more so where investment is irreversible. Julio and Yook (JF 2012): investment is 4.8%
  lower in election years. Kellogg (AER 2014): Texas drillers respond to volatility close to the real-options optimum.
  Bonaime, Gulen and Ion (JFE 2018): the same holds for M&A. All of this is about *uncertainty in general*. None of it
  shows AI lowering uncertainty.
- **Stage 2 (AI lowers managers' uncertainty): almost untested.** Babina, Fedyk, He and Hodson (AEA P&P 2025) find
  pre-generative AI hiring goes with lower *realised* volatility of ROA and cash flow. That is realised volatility, not
  perceived uncertainty. No fetched paper tests guidance width, forecast dispersion or deal speed against AI adoption.
- **Stage 4 (idle cash is deployed): history runs the other way.** Bates, Kahle and Stulz (JF 2009): cash/assets rose
  129% from 1980 to 2004 for precautionary reasons. Harford (JF 1999) and Malmendier and Tate (JFE 2008): cash-rich and
  overconfident acquirers make value-destroying deals. That supports the thesis's *ex-post* boundary claim, not its
  boom claim.
- **The strongest evidence against the thesis.** Kalyani and Li, FRBSF Economic Letter 2026-13 (18 May 2026): among
  listed firms, all capex growth since 2024Q1 came from AI-positive firms, and "other firms collectively had slightly
  negative growth". The four hyperscalers dominate the largest firms' contribution. St. Louis Fed (Kalyani, Ozkan and
  others, October 2024): after ChatGPT, AI-positive call sentiment stopped predicting capex.

## Free-data reach (Sonnet inventory, shape only)

Strong: SEC XBRL frames and submissions via `data.sec.gov` (firm-quarter capex, cash, acquisitions, goodwill impairment,
SIC; 2009–2026Q3), Fed Z.1 (to 2026Q2), Census BTOS AI-use questions (biweekly from 2023), Census C30 data-centre
construction, BEA section 5 workbook, BEA–BLS KLEMS productivity (to 2024).

Weak or blocked:
- Firm text uncertainty after 2021 (Hassan et al. ends in 2021; CRUX not posted).
- SBU microdata (needs a request form).
- BLS hosts (403).
- Census and BEA APIs (key needed; the bulk files work).
- HSR counts (no machine-readable file).
- Any deal-timing data (paid).
