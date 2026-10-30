# The two Fed series for non-financial net equity issuance: what separates them (Grok, 30 Oct 2026)

Grok 4.7 via Cursor, fenced to read and web only; 402 s, 17 fetch calls, no blocked or unexpected tool, every cited URL fetched (three malformed tool calls errored before running).

**Supervisor check (30 Oct):** the Fed's Series Analyzer pages for FA103164155 and FA103164115 were re-fetched and the equations found as quoted: FA103164155 = FA103164113 + FA103164123 (public and closely held equity, "excluding eREITs"); FA103164115 = FA103164113 + FA123164113 (adds equity REITs' public equity). The 11 Sep 2026 Z.1 bulk CSV package prints neither the eREIT equity series (123164113, 123164123) nor 103164155 in any table, so the split cannot be measured from the published tables.

**Reading.** The ledger's gap is FU103164105 (Z.1 table, unadjusted, including equity REITs) minus FA103164155 / 4 (the EFA file's net, seasonally adjusted, excluding equity REITs). By the Fed's own definitions it equals equity REITs' net equity issuance plus the seasonal-adjustment term of the excluding-eREIT series. That identifies the cause by definition (C-130 called the eREIT explanation unproven); the size of each part is not measured, because neither is published in a table. The two series still belong in separate tables.

## Return

**FU103164105**
- DESCRIPTION: Nonfinancial corporate business; corporate equities; liability
- TABLE/LINE: Not printed as FU. The same series number is printed as FA on S11.1.t line 56, “Corporate equities” (under line 55, “Net equity issues”), and on F51.1.t line 2, “Nonfinancial corporate business” (under line 1, “Net issues”). The guide also lists FA103164105.Q on S11.t line 49, S1S.t line 62, S11.1.i.a line 75, and S11.1.i.q line 67.
- URL: https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FU103164105&t= ; tables https://www.federalreserve.gov/releases/z1/current/html/S11_1_t.htm and https://www.federalreserve.gov/releases/z1/current/html/F51_1_t.htm

**FA103164105**
- DESCRIPTION: Nonfinancial corporate business; corporate equities; liability
- TABLE/LINE: S11.1.t line 56, “Corporate equities”; F51.1.t line 2, “Nonfinancial corporate business.” S11.1.t is the current name of former table F.103. In the March 19, 2026 release the same series is F.103 line 55, “Corporate equities,” and F.224 line 2, “Nonfinancial corporate business.”
- URL: https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FA103164105&suf=Q&t= ; https://www.federalreserve.gov/releases/z1/current/html/S11_1_t.htm ; https://www.federalreserve.gov/releases/z1/current/html/F51_1_t.htm

**FA103164155**
- DESCRIPTION: Nonfinancial corporate business; corporate equities; liability (excluding eREITs)
- TABLE/LINE: None. The guide lists no table, and the code is not on S11.1.t or F51.1.t.
- URL: https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FA103164155&t=

**FU103164155**
- DESCRIPTION: Nonfinancial corporate business; corporate equities; liability (excluding eREITs)
- TABLE/LINE: None. Same as FA103164155; the guide lists no table.
- URL: https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FU103164155&t=

**DIFFERENCE BY DEFINITION**

Root 103164105 includes equity-REIT corporate-equity liabilities. Root 103164155 excludes them. Both roots include public and closely held equities of other nonfinancial corporations. The gap is the eREIT piece only.

The guide’s equations:

- FA103164155 = FA103164113 + FA103164123, described as public and closely held corporate equities “excluding eREITs.”
- FA103164105 = FA103164115 + FA103164125.
- FA103164115 = FA103164113 + FA123164113, and FA123164113 is “Equity real estate investment trusts; public corporate equities; liability.”
- FA103164125 = FA103164123 + FA123164123, and FA123164123 is “Equity real estate investment trusts; closely held corporate equities; liability.”

So 103164105 = 103164155 + those two equity-REIT liability series. The same addition holds for the FU codes. Quoted from https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FA103164155&t= , https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FA103164115&t= , and https://www.federalreserve.gov/apps/fof/SeriesAnalyzer.aspx?s=FA103164125&t= .

The equity-issuance file uses the excluding-eREIT root: “Net equity issuance of domestic nonfinancial corporations, excluding eREITs. Defined as gross equity issuance less gross retirements. Data are reported in billions of dollars at a quarterly rate. Equals series FA103164155.Q … divided by 4.” https://www.federalreserve.gov/releases/efa/equity-issuance-retirement-quarterly-historical.txt

Sector placement, from the mortgage-REIT table description: “equity REITs, which invest in and own properties, are included in the nonfinancial corporate business sector (tables S11.1.t, S11.1.s, S11.1.b, and S11.1.r).” “In the December 7, 2023 release … equity REITs were moved into the nonfinancial corporate business sector … while mortgage REITs remain within the domestic financial sectors.” https://www.federalreserve.gov/releases/Z1/current/html/table_desc_sectors.htm . Mortgage REITs are a separate line on F51.1.t (line 10, FA643164105). Foreign direct investment equity is also a separate line (S11.1.t line 57, FA103192105). Holding-company equity is F51.1.t line 14, FA733164105.

**PREFIX MEANING**

Yes. On https://www.federalreserve.gov/apps/fof/SeriesStructure.aspx : “The prefix letters indicate the series type. For example, ‘FA’ indicates transactions at a seasonally adjusted annual rate.” The table rows are:

- FA: “Transactions at a seasonally adjusted annual rate (SAAR).” Derivation: “(FU + FS) * 4”.
- FU: “Transactions, not seasonally adjusted (NSA).” Derivation: “FA/4 - FS” (also the level identity).
- FS: “Seasonal Factor.” Derivation: “FA / 4 - FU”.

The page’s words for FU are “Transactions, not seasonally adjusted (NSA),” which is the unadjusted quarterly flow. FA/4 equals that flow plus the seasonal factor. The equity-issuance file’s “FA103164155.Q … divided by 4” is therefore the seasonally adjusted quarterly rate, not FU103164155, unless the seasonal factor is zero. Whether that factor is zero for this series is not stated on the pages fetched.
