# N2c closure, refreshed on the Z.1 2026Q2 release (12 Sep 2026) — and a turn in net equity supply

**Status: DATA, with one structural finding.** The 12 Sep calendar obligation, done. Script
`bin/build_closure_2026Q2.py`; data `_research/2026-09-12-N2c-closure_2026Q2.csv`, `-revisions.csv`.

**The three watch items, answered:**
- **The Fed is still a net buyer of Treasuries:** +$97.8bn in 2026Q2 after +$156.2bn in Q1 — about two-thirds the
  pace, but a continuation of the reversal from -$741bn (2023), -$515bn (2024) and -$83bn (2025).
- **Money funds are still net sellers, and selling harder:** -$144.9bn in Q2 after -$91.4bn in Q1.
- **Nonfinancial corporations have turned net ISSUERS of equity:** +$51.3bn in Q1 (revised up from +$31bn) and
  **+$153.2bn in Q2** — two consecutive positive quarters after years in which buybacks exceeded issuance
  (-$603bn in 2023, -$397bn in 2024, -$348bn in 2025). Net supply has changed sign.

**Why that third item matters.** The project's charter asks who the net buyers are and what net supply they meet.
For a decade the answer was that companies retired stock; the market's buyers were absorbing shrinking supply.
Two quarters of positive net issuance, alongside the AI-related equity raises read from the filings
(`2026-09-12-F1-AI-Funding-Filings.md`), is the first direct evidence for the hypothesis that the build-out is now
asking the market to absorb new shares. It is two quarters; it is not yet a trend.

**Supervisor verification (12 Sep):** the Fed line (FU713061103.Q: +156.222 in Q1, +97.817 in Q2) and the
nonfinancial-corporate equity issuer line (+51.267, +153.209) were read directly from the release files and from
our own P1 tables, independently of the agent's table.

**Method caveats the agent flagged, and they matter for reuse:** the June vintage's broker-dealer series no longer
exists (a like-for-like replacement was used); the combined insurers line is now annual only (property-casualty and
life were substituted); hedge funds now have their own Treasury line, folded back into households to preserve the
original definition; and the original doc's catch-all "other" row was never documented, so it is reconstructed to
within $5-10bn a year and applied identically to both vintages. Revisions between vintages are large in places —
households' Treasury line for 2024 was revised down $103bn.

---

## The agent's return (Sonnet)

## Funding closure table refreshed — Z.1, 2026Q2 vintage (release of 11 Sep 2026)

**Release confirmed live:** fetched `https://www.federalreserve.gov/releases/z1/` — release date **September 11, 2026**, vintage **2026:Q2** (matches the brief). 2 HTTP requests total (landing page, 120,825 bytes; single bulk `z1_csv_files.zip`, 8,336,582 bytes), User-Agent as specified, no email, ≥0.6s apart. Zip downloaded once; extracted locally: `F3_2_t_tu.csv` (Treasury securities, cross-sector), `S122_t_tu.csv` (private depository institutions), `S129_t_tu.csv` (pension funds) — all NSA quarterly flow ("_tu") tables, $millions, converted to $bn.

### Treasury absorption table (all figures: Z.1 flow, $bn, NSA — annual columns are 4-quarter calendar-year sums; 2026Q1/Q2 are single-quarter)

| Buyer | 2023 | 2024 | 2025 | 2026Q1 | 2026Q2 |
|---|---:|---:|---:|---:|---:|
| Money market funds | 1,205.5 | 725.4 | 523.0 | −91.4 | **−144.9** |
| Households + nonprofits (incl. hedge funds) | 781.8 | 43.7 | 245.5 | −13.5 | 182.9 |
| Rest of world | 728.2 | 630.2 | 545.0 | 128.8 | 21.4 |
| **Federal Reserve** | −740.9 | −515.3 | −82.8 | **156.2** | **97.8** |
| Banks (private depository) | −100.1 | 197.4 | 202.7 | 95.4 | −4.7 |
| Mutual funds + ETFs + closed-end | 117.4 | 205.8 | 256.3 | 133.6 | 44.4 |
| Insurers + pensions (incl. S&L retirement) | 252.2 | 279.1 | 172.8 | 103.6 | −4.6 |
| Broker-dealers | 108.0 | 130.2 | 71.2 | 81.2 | −51.3 |
| State/local govts, GSEs, corporates, other | 111.0 | 282.0 | 52.2 | −4.0 | 88.5 |
| **Net issuance (= all-sector absorption, check passes)** | **2,381.6** | **1,912.9** | **1,930.2** | **571.9** | **236.7** |
| [diagnostic] sum of 9 buyer rows | 2,463.1 | 1,978.5 | 1,985.9 | 589.9 | 229.5 |

### Equity side (Z.1 F51.1.t, $bn NSA flow; reused from already-pulled, supervisor-verified project data, re-aggregated to calendar years — no new HTTP fetch)

| Row | 2023 | 2024 | 2025 | 2026Q1 | 2026Q2 |
|---|---:|---:|---:|---:|---:|
| All sectors, total net issuance | 33.5 | 905.0 | 1,163.8 | 443.7 | 730.5 |
| Nonfinancial corporate business (issuer, buybacks) | −602.9 | −397.0 | −348.2 | **51.3** | **153.2** |
| Households + nonprofits (holder) | 448.7 | 1,404.9 | 824.0 | 490.0 | 350.5 |
| ETFs (holder) | 400.2 | 840.4 | 958.4 | 269.0 | 393.1 |
| Rest of world (holder) | 50.1 | 178.7 | 646.7 | −21.7 | 410.2 |
| Mutual funds (holder) | −319.3 | −514.6 | −1,073.8 | −197.6 | −223.0 |
| Hedge funds, domestic (holder) | −81.9 | −1.3 | −15.1 | −31.6 | −3.1 |

### The three watch items, with numbers

**(a) Fed net Treasury buying past Q1's +$156bn:** continues positive — **+$97.8bn in 2026Q2** (Z.1 flow, NSA), down from +$156.2bn in Q1 (Q1 itself essentially unrevised, see below). Still the pattern the doc flagged (Fed as net buyer), but at roughly 63% of Q1's pace.

**(b) Do MMFs stay net sellers:** yes — **−$144.9bn in 2026Q2**, deepening from −$91.4bn in Q1 (also essentially unrevised). Selling intensified quarter over quarter.

**(c) NFC net equity issuance now:** the doc reported +$31bn for 2026Q1 as "the first positive quarter — worth watching." The September vintage **revises Q1 up to +$51.3bn** (+$20.3bn revision) and shows **2026Q2 at +$153.2bn** — a second consecutive positive quarter, and a much larger one. Reporting the fact only, per scope.

### Revisions, June (2026Q1 vintage) → September (2026Q2 vintage) — full list in `revisions.csv` (26 data rows)

Largest: **Households + nonprofits** (Treasury row) revised down every period — 2023 814.5→781.8 (−32.7), 2024 147.0→43.7 (**−103.3**), 2025 276.2→245.5 (−30.7), 2026Q1 50.1→−13.5 (**−63.6**). Confirmed this is a genuine residual revision, not the newly-separated hedge-fund line (that line is <$20bn every period; added it into this row to preserve the doc's own "incl. hedge funds" definition — see caveats).

Single largest component revision: **nonfinancial corporate business, as a Treasury holder**, 2024: 11.0 → 107.9 (**+96.9bn**) — this alone drives most of the "State/local/GSE/other" row's +105.4bn 2024 revision.

Other notable: NFC net **equity** issuance 2025 −304.0→−348.2 (−44.2); household holder (equity) 2025 863.5→824.0 (−39.5); Insurers+pensions (Treasury) 2025 133.8→172.8 (+39.0); Mutual funds+ETFs+CEF 2026Q1 95.3→133.6 (+38.3); Rest of world (Treasury) 2025 509.6→545.0 (+35.4); Broker-dealers 2026Q1 109.4→81.2 (−28.2).

**Not revised** (worth flagging precisely because these feed watch items a/b): Federal Reserve row (−740.9/−515.3/−82.8/156.2 — matches the doc to rounding in all four periods) and Money market funds row (1,205.5/725.4/523.0/−91.4 — same). The Q1→Q2 comparisons above are on a clean, unrevised base.

### What I could not reproduce exactly, and why

1. **Broker-dealers code changed.** June doc's `FU663061103.Q` does not exist anywhere in the 11-Sep-2026 release's data dictionaries. Only `FU663061105.Q` ("Security brokers and dealers; Treasury securities; asset") exists (in both F3.2.t and S125s3.t). Used it as the like-for-like replacement, confirmed by description text.
2. **Insurers line discontinued quarterly.** June doc's combined `FU523061105.Q` ("Insurers") is not in any quarterly table in this release's bulk CSV package — only in `S128.i.a`, an **annual** integrated-account table. Substituted Property-casualty (`FU513061105.Q`) + Life insurers (`FU543061105.Q`), both genuinely quarterly.
3. **"Banks" and "Pensions" aggregates aren't in the Treasury table at all.** F3.2.t only carries their sub-components; the aggregate lines live in the sector-specific tables `S122.t` and `S129.t` (same codes both vintages — a sourcing detail, not a comparability gap).
4. **The catch-all "other" row cannot be reproduced exactly, and this is inherited, not new:** the original June-vintage doc's own 9 published rows do not sum to its own published total (gaps of $25–96bn/yr, worst in 2023 and Q1 2026) — the exact code list behind that row was never documented anywhere in the project. My 6-code reconstruction (GSEs, NFC, state/local govts, other-financial-business CCP-held Treasuries, ABS issuers, holding companies) matches the June-vintage published figures to within ~$5–10bn/yr, applied identically to both vintages so the revisions above are apples-to-apples.
5. A newly-separate **"Hedge funds (domestic)" Treasury line** (`FU623061103.Q`) appears this release; it didn't exist separately in June (was inside the household residual then). Folded into "Households + nonprofits" per the doc's own definition; confirmed numerically it does not explain that row's much larger revision.
6. Equity-side revision checking is limited to the 4 series/periods where the project already has a documented June-vintage comparator (`data/series.tsv`, 2026-09-11 entries): NFC issuance (2025, 2026Q1), rest-of-world holder (2025), household holder (2025). I did not fabricate comparators for ETFs, mutual funds, or domestic hedge funds as equity holders.

### Deliverables (scratch directory only — project folder untouched)
- `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/wave2/n2c/closure_2026Q2.csv`
- `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/wave2/n2c/revisions.csv`
- `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/wave2/n2c/build_closure_2026Q2.py` (the script; docstring documents method + both substitutions)
- `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/wave2/n2c/validate_june_vintage.py` (pre-flight check: reproduces the published June-vintage table from the raw pull before touching new data)
- `/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/wave2/n2c/raw/` (fetched evidence: release page HTML, the one bulk zip, extracted tables)

No summary/report .md files were written, per instructions.
