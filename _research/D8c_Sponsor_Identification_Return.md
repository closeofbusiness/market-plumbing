# D8c Sponsor Identification Return
Prepared: 24 August 2026 - Model: Grok 4.6 (Cursor session, live web) - Word count: 2510

## 0. Plan (5 lines, written before searching)
Open Fitch public rating actions and the named firms' own sites first (ADG, Drexel, Capitolis), because those pages have returned bodies to this fetcher. Treat S&P and moodys.com as gated unless a GET actually yields a programme table; record HEAD status either way. Re-open Luxembourg LEI and a free RCS mirror for ADG Verto; do not treat an address as a sponsor. For Britannia / Alinghi / Mackinac, confirm or refute Nearwater per vehicle, never by resemblance. For Ionic, keep Funding LLC, the Capital trusts, and Capitolis the firm on separate lines.

## 1. Vehicles

### V1 - Verto Capital I (compartments A, C, D)
- Sponsor: CANNOT DETERMINE as a labelled ABCP sponsor. The FCP is managed by ADG Verto Capital Management S.a r.l. The UK adviser in the same group, ADG Verto Advisers LLP, is a wholly owned subsidiary of ADG Corporate Ltd.
- Administrator / manager: ADG Verto Capital Management S.a r.l. is the manager of VERTO CAPITAL I, a Luxembourg fonds commun de placement. Historical LEI lines carried the fund c/o that manager.
- Investment adviser (if distinguished): ADG Verto Advisers LLP (England and Wales; FCA-authorised). The opened UK disclosure does not say that this LLP is the AIFM or the originator of the FCP's assets.
- Programme type and collateral: ADG's Verto page describes a funding platform for institutional counterparties / global financial institutions. Named assets and named originators: CANNOT DETERMINE. The UK MIFIDPRU text (ADG Verto Advisers LLP exposed to a single client with a broad base of underlying GSIB clients) describes the UK adviser, not the FCP's asset originators.
- URL OPENED (and HTTP status): https://adgcorporate.com/adg-verto/ (HEAD 200); https://adgcorporate.com/wp-content/uploads/2025/09/ADG-Group-Public-Discloure-non-SNI-2025.pdf (HEAD 200; year ending 31 March 2025); https://lei-luxembourg.lu/informations-detaillees/36694529/894500Q1DK36MAW5F773/verto-capital-i/ (HEAD 200); https://www.pappers.lu/en/company/adg-verto-capital-management-sa-rl-B260026 (HEAD 200). CSSF AIFM list: no page opened that names this FCP or this manager.
- Document date: Verto site undated (opened 24 August 2026); MIFIDPRU 2025; LEI last update 11 September 2025; Pappers incorporation 13 October 2021.
- Outstanding, if stated (with as-of date): CANNOT DETERMINE.
- Confidence: PARTIAL
- Searches run, if CANNOT DETERMINE: CSSF AIFM / RAIF; Luxembourg press; Yahoo / Moody's; Fitch. Pappers officers and parent of the Luxembourg SARL are blank; UK LLP ownership is not copied onto the SARL. Address matches are leads only (section 2).

### V2 - HQLA Funding LLC (series Champlain, Huron, Tahoe)
- Sponsor: Capitolis Administrator LLC. Fitch states that this firm is the programme's sponsor and administrator.
- Administrator / manager: Capitolis Administrator LLC (administrator). Deutsche Bank Trust Company Americas is issuer trustee for HQLA Funding LLC and custodian and servicer for Dynamic Funding Markets LLC.
- Investment adviser (if distinguished): not distinguished on the Fitch pages opened. Not the same role as Capitolis Advisors LLC on the Ionic Capital trusts (V7).
- Programme type and collateral: Delaware SPV issuing series-specific notes and certificates. Proceeds go to Dynamic Funding Markets LLC (revolving loan or equity). DFM buys US Treasuries via repurchase / securities funding agreements, hedged when the Treasuries mature after the notes. Fully supported by series-specific counterparties. Champlain and Tahoe: Fitch 27 September 2024. Huron: Fitch 2 December 2024, same roles and collateral path.
- URL OPENED (and HTTP status): https://www.fitchratings.com/research/structured-finance/fitch-assigns-ratings-to-two-series-of-hqla-funding-llc-27-09-2024 (HEAD 200); https://www.fitchratings.com/research/structured-finance/fitch-rates-hqla-funding-llc-series-huron-notes-02-12-2024 (HEAD 200). S&P Series Saranac landing HEAD 403, title only, unused. HQLAx (https://hqla-x.com/) is a different person.
- Document date: 27 September 2024 (Champlain, Tahoe); 2 December 2024 (Huron).
- Outstanding, if stated (with as-of date): CANNOT DETERMINE on the Fitch pages (ratings, not a size).
- Confidence: VERIFIED for sponsor, administrator, trustee/servicer, programme type, and Treasury/repo collateral on Champlain, Huron, and Tahoe.

### V3 - Washington Morgan Capital Company LLC
- Sponsor: CANNOT DETERMINE
- Administrator / manager: CANNOT DETERMINE
- Investment adviser (if distinguished): CANNOT DETERMINE
- Programme type and collateral: appears as an issuer of short-term paper on an N-PORT holdings tape (issuer, not sponsor). Programme type and collateral CANNOT DETERMINE.
- URL OPENED (and HTTP status): https://inv-info.com/ (HEAD 200) is a Guggenheim CP login that does not name this vehicle. Yahoo, Fitch, and S&P searches produced no opened body for this legal name.
- Document date: n/a
- Outstanding, if stated (with as-of date): CANNOT DETERMINE
- Confidence: CANNOT DETERMINE
- Searches run: Yahoo with the full legal name; Fitch; DBRS; EDGAR as Conduit Lender (no exhibit opened); inv-info.com. No inference from the Guggenheim login, the name, or an address.

### V4 - Intrepid Funding Company LLC
- Sponsor: CANNOT DETERMINE
- Administrator / manager: CANNOT DETERMINE
- Investment adviser (if distinguished): CANNOT DETERMINE
- Programme type and collateral: S&P title Intrepid Funding Co. LLC ABCP Notes Assigned Rating is visible; body not opened. Appears as an issuer on an N-PORT holdings tape. Not the Jacksonville Beach mutual-fund complex Intrepid Capital Management / Intrepid Capital Funds (opened https://intrepidcapitalfunds.com/ — unrelated).
- URL OPENED (and HTTP status): https://www.spglobal.com/ratings/en/regulatory/article/-/view/type/HTML/id/3262547 (HEAD 403; title only; not used as a finding). Yahoo Finance search hit Intrepid Income Institutional, a mutual fund, not this LLC.
- Document date: S&P title undated on the gated landing.
- Outstanding, if stated (with as-of date): CANNOT DETERMINE
- Confidence: CANNOT DETERMINE
- Searches run: Yahoo / Moody's activity; Fitch; DBRS; EDGAR as Conduit Lender; S&P (403). Nothing free named a sponsor or administrator.

### V5 - Overwatch Alpha Funding LLC and Overwatch Bravo Funding LLC
- Sponsor: CANNOT DETERMINE for these two LLC names. Drexel Hamilton's own site states that Drexel Hamilton serves as the Sponsor and exclusive Referral Agent for the Overwatch Funding Company (different legal style; not Alpha, not Bravo, not LLC). That page is not treated as identity of Alpha or Bravo (R7: no inference from a name).
- Administrator / manager: CANNOT DETERMINE for the two LLCs. Drexel page does not name an administrator.
- Investment adviser (if distinguished): CANNOT DETERMINE
- Programme type and collateral: Drexel describes Overwatch Funding as specialty finance via commercial paper; it does not name Treasuries, equities, receivables, or loans. S&P Bravo new-issue landing HEAD 403, title only, unused.
- URL OPENED (and HTTP status): https://www.drexelhamilton.com/overwatch-funding-company/ (HEAD 200); https://www.drexelhamilton.com/our-services/ (same blurb). S&P Bravo: https://www.spglobal.com/ratings/en/research/pdf-articles/240515-new-issue-overwatch-bravo-funding-llc-13096381 (HEAD 403).
- Document date: Drexel undated (opened 24 August 2026). S&P Bravo URL date 15 May 2024; body not opened.
- Outstanding, if stated (with as-of date): CANNOT DETERMINE
- Confidence: PARTIAL (Drexel verified for Overwatch Funding Company only). Alpha LLC and Bravo LLC remain CANNOT DETERMINE.

### V6 - Britannia Funding Company LLC, Alinghi Funding Company LLC, Mackinac Funding Company LLC

Treat as one row, three sub-lines. Nearwater only where an opened page names it.

#### V6a - Britannia Funding Company LLC
- Sponsor: Nearwater Liquid Markets LLC. GET of the S&P ABCP conduit profile produced a Programme Overview table with that sponsor, and a legal section stating that Nearwater is the sole equity member of Britannia and of NLMCC LLC (AssetCo). HEAD to the same URL returned 403 and a register overlay sat at the footer of the GET document. Recorded as opened GET HTML, with the 403 disclosed.
- Administrator / manager: Deutsche Bank Trust Co. Americas (administrator, depositary, custodian on that table).
- Investment adviser (if distinguished): not distinguished. NLMCC LLC is the lender/AssetCo that buys Treasuries; it is not labelled investment adviser.
- Programme type and collateral: single-seller, fully supported ABCP. Proceeds fund intercompany loans to NLMCC LLC, which purchases US Treasuries in the open market and lends/sells them under a global master securities lending agreement and a master repurchase agreement with Barclays Bank PLC, plus hedge agreements. Support provider on the table: Barclays Bank PLC.
- URL OPENED (and HTTP status): https://www.spglobal.com/ratings/en/research/articles/220127-britannia-funding-co-llc-abcp-conduit-profile-12174588 (HEAD 403; GET HTML contained the table described above).
- Document date: 27 January 2022
- Outstanding, if stated (with as-of date): none stated (fully supported; no programme limit on the table).
- Confidence: PARTIAL (gated S&P; GET body observed). Not copied onto V6b or V6c.

#### V6b - Alinghi Funding Company LLC
- Sponsor: CANNOT DETERMINE. Same-day S&P conduit-profile URL for Alinghi opened as a purchase-only RatingsDirect gate (HEAD 403). No sponsor field was on the page. Nearwater is not inferred from Britannia or from the name.
- Administrator / manager: CANNOT DETERMINE
- Programme type and collateral: CANNOT DETERMINE on an opened free page.
- URL OPENED (and HTTP status): https://www.spglobal.com/ratings/en/research/articles/220127-alinghi-funding-co-llc-abcp-conduit-profile-12192627 (HEAD 403; purchase gate; title only).
- Document date: title date 27 January 2022
- Outstanding: CANNOT DETERMINE
- Confidence: CANNOT DETERMINE
- Searches run: Fitch; Yahoo / Moody's; DBRS; Nearwater's own site (https://nearwatercapital.com/ is an enter-gate; https://www.nearwatercapital.com/overview opened and does not name conduits).

#### V6c - Mackinac Funding Company LLC
- Sponsor: CANNOT DETERMINE. No S&P conduit-profile body opened. GlobalCapital article titled Nearwater sets up third US Treasury conduit with Barclays (14 October 2020) returned HEAD 200 but a gift/subscriber overlay; the visible title does not name Mackinac, Alinghi, or Britannia. Snippet-only, unverified; not used as an answer.
- Administrator / manager: CANNOT DETERMINE
- Programme type and collateral: CANNOT DETERMINE on an opened free page.
- URL OPENED (and HTTP status): https://www.globalcapital.com/securitization/article/28mucv2tbv7l92nf9hyww/abs/nearwater-sets-up-third-us-treasury-conduit-with-barclays (HEAD 200; body gated). Nearwater overview as under V6b.
- Document date: 14 October 2020 (title)
- Outstanding: CANNOT DETERMINE
- Confidence: CANNOT DETERMINE
- Searches run: Fitch; Yahoo / Moody's; DBRS; S&P by legal name; Nearwater site. Neither confirmed nor refuted as Nearwater.

### V7 - Ionic Funding LLC versus Ionic Capital II Trust and Ionic Capital III Trust
- Sponsor: Ionic Funding LLC — Capitolis Administrator LLC is the programme's sponsor and administrator (Fitch, 25 November 2024). Ionic Capital II Trust and Ionic Capital III Trust — aum13f's Capitolis Advisors LLC firm page (source labelled IAPD) lists both as Form D funds of Capitolis Advisors LLC (II dated 7 July 2020; III dated 12 July 2021). That is an adviser/private-fund listing, not Fitch's sponsor label. The two trusts are not the same legal person as Ionic Funding LLC.
- Administrator / manager: Ionic Funding LLC — Capitolis Administrator LLC; U.S. Bank Global Fund Services (servicer); US Bank Trust Company NA (trustee). Ionic Capital II Trust (aum13f): US Bank National Association and US Bank Trust Company NA as director/custodian. Ionic Capital III Trust: statutory trust, legal address c/o U.S. Bank Trust National Association. Headquarters address unused (R7).
- Investment adviser (if distinguished): Capitolis Advisors LLC is the Form D / IAPD firm on the two trusts. Fitch does not name Capitolis Advisors LLC as adviser of Ionic Funding LLC. Capitolis Liquid Global Markets LLC Statement of Financial Condition (unaudited, 31 July 2024) states that Ionic Funding LLC is a wholly owned subsidiary of Capitolis Inc. (the Parent) and lends to CLGM under loan agreements whose duration corresponds to CLGM's total-return-swap transactions.
- Programme type and collateral: Ionic Funding LLC issues series notes/certificates; proceeds fund CLGM, which buys equity baskets and enters TRS and/or securities lending. Ionic Capital II / III Trust are Form D private funds of Capitolis Advisors LLC; collateral CANNOT DETERMINE. Same family, different legal forms.
- URL OPENED (and HTTP status): https://www.fitchratings.com/research/structured-finance/fitch-assigns-final-ratings-to-ionic-funding-llc-series-ii-25-11-2024 (HEAD 200); https://capitolis.com/wp-content/uploads/2024/08/Capitolis-Liquid-Global-Markets-LLC-%E2%80%93-July-31-2024-Statement-of-Financial-Condition.pdf (HEAD 200); https://aum13f.com/firm/capitolis-advisors-llc (HEAD 200); https://aum13f.com/fund/ionic-capital-ii-trust (HEAD 200); https://americanlei.com/detailed-information/35439283/254900X889N3JUSUDE39/ionic-capital-iii-trust/ (HEAD 200). Risk.net: HEAD 200, body gated; unused.
- Document date: Fitch 25 November 2024; CLGM SOFC as of 31 July 2024, issued 29 August 2024; Form D dates as above.
- Outstanding, if stated (with as-of date): CLGM revolving loan from Ionic Funding LLC, USD 8.5bn as of 31 July 2024 (affiliate loan, not ABCP size).
- Confidence: VERIFIED for Ionic Funding LLC roles, equity/TRS path, and Parent ownership. PARTIAL for the two trusts (IAPD scrape, not an opened Form ADV PDF). Same family; not the same vehicle.

### V8 - Capitolis (the firm)
- Sponsor: Capitolis Administrator LLC is named by Fitch as sponsor and administrator of Ionic Funding LLC and of HQLA Funding LLC (V2, V7). Capitolis Inc. is Parent of Capitolis MAPS LLC, which owns Capitolis Liquid Global Markets LLC; Ionic Funding LLC is a wholly owned subsidiary of the Parent.
- Administrator / manager: Capitolis Administrator LLC (those two programmes). Deutsche Bank Trust Company Americas (HQLA trustee / DFM servicer). U.S. Bank Global Fund Services and US Bank Trust Company NA (Ionic Funding LLC servicer and trustee).
- Investment adviser (if distinguished): Capitolis Advisors LLC — IAPD/Form D firm for Ionic Capital II Trust and Ionic Capital III Trust. Distinct from Capitolis Administrator LLC.
- Programme type and collateral: Ionic Funding LLC funds equity baskets via CLGM TRS/securities lending. HQLA Funding LLC funds US Treasuries via DFM repo (Champlain, Huron, Tahoe). Homepage (Capital Marketplace / Portfolio Optimization) lists no ABCP names. GET of the 20 Gates press (HEAD 403) says Capitolis agreed to acquire 20 Gates Management's US Secured Financing Platform; it names no conduit. Mayer Brown March 2024 (GET PDF; HEAD 403) lists Capitolis among aggregators without legal names.
- URL OPENED (and HTTP status): https://capitolis.com/ (HEAD 403; GET body opened); CLGM SOFC and Fitch as V2/V7; https://capitolis.com/capitolis-to-acquire-20-gates-managements-u-s-secured-financing-platform-to-expand-its-capital-marketplace/ (HEAD 403; GET opened); Mayer Brown PDF GET opened, HEAD 403; aum13f firm page HEAD 200.
- Document date: homepage opened 24 August 2026; Fitch 2024; SOFC 31 July 2024; Mayer Brown March 2024.
- Outstanding, if stated (with as-of date): Ionic-to-CLGM loans USD 8.5bn as of 31 July 2024. ABCP outstanding: CANNOT DETERMINE.
- Confidence: VERIFIED for the two Fitch programmes and CLGM/Ionic ownership. Homepage does not sponsor-list vehicles.

## 2. Anything I found that you did not ask for - only with a URL you can open
- Dynamic Funding Markets LLC sits between HQLA Funding LLC and the Treasury SFA counterparties (Fitch, V2).
- Ionic MTN Funding LLC appears in titles of later CLGM SOFCs on capitolis.com; the opened 31 July 2024 SOFC does not name it. Those later PDFs were not opened.
- Aquitaine Funding Co. LLC S&P profile (GET HTML, HEAD 403), 27 January 2022: sponsor Nearwater Liquid Markets LLC; administrator Deutsche Bank Trust Co. Americas. URL: https://www.spglobal.com/ratings/en/research/articles/220127-aquitaine-funding-co-llc-abcp-conduit-profile-12192153 . Not copied onto V6b or V6c.
- LEI address 68 S Service Rd Ste 120, Melville NY appears for Overwatch Alpha, Overwatch Bravo, and Ionic Capital III Trust. Lead only; not used as sponsor.
- Overwatch Charlie Funding LLC on the same LEI neighbourhood table. Not asked; not attributed.

## 3. SELF-AUDIT (completeness only - the reader verifies truthfulness independently)
- [x] Every vehicle has a row (8/8)
- [x] No identifiers; no dollar sign anywhere (I searched the output for it)
- [x] Every VERIFIED row names a page I actually opened, with its HTTP status
- [x] No snippet from a gated page is presented as a finding (S&P GET tables are labelled PARTIAL and 403; GlobalCapital and Risk.net bodies not used; S&P titles without bodies not used)
- [x] No sponsor inferred from a name, an address, or a resemblance
- [x] No two vehicles share an identical answer shape unless the sources genuinely say so
- [x] Every CANNOT DETERMINE lists the searches behind it
- [x] If cut off, last line is <<CONTINUE>>
