# Can a data centre's grid right be sold? The 16 November 2026 FERC filings, read

19 November 2026. Five grid operators filed their large-load proposals at FERC on 13-16 November 2026, answering the show-cause
orders in dockets EL26-67 (PJM), EL26-69 (NYISO), EL26-70 (MISO), EL26-71 (CAISO) and EL26-72 (ISO-NE). SPP (EL26-68) is due on
20 November. The question carried here since August ([the Parcel C note](../2026-08-22-Parcel-C-FERC-Return.md), section 6.4) is
whether any of them creates a large-load or flexible-load service whose rights can be **sold, assigned or traded** to another load.
Grok found the filings and read them first; its two returns are kept verbatim in
[the readings note](2026-11-19-FERC-Large-Load-Grok-Readings.md). Every finding marked "read" below was re-read by the supervisor
in the filed document itself, downloaded from the operator's own site (sha256 in the last section).

## The answer so far: no tradeable right in the three filings read; two are unread

| operator | filing | new service | can the right be sold or moved to another load? | read by |
|---|---|---|---|---|
| PJM | ER27-531, 16 Nov | Interim Network Integration Transmission Service; Firm and Non-Firm Contract Demand Transmission Service | **No.** Proposed tariff §701.4 bars use of the interim service for "sales of energy to loads other than" the load named in the agreement, and for "provision of transmission service ... to third parties"; the transmittal (p. 38) states the same for Contract Demand service. §711(a) lets a *successor customer* take over service to the same load under a new agreement; that changes who serves the load, not where the right is used | supervisor |
| NYISO | ER27-517, 16 Nov (Attachment LL); NYTOs ER27-529 | Firm and Non-Firm Withdrawal Service | **No, not on its own.** Attachment LL §44.7.1.3 allows a queue position to move to another entity "only if" it "acquires the specific Large Load Project", at the same point of interconnection. The transmission owners' cost-recovery agreement (§4.2) is "specific to a single Large Load Facility"; §9.7 allows assignment only with consent and with the other agreements | supervisor |
| CAISO | ER27-532, 16 Nov | Flexible Interim Load Interconnection (FILI): curtailable connection before upgrades are built | **Silent.** Tariff §25.7.2 provides FILI through a three-party agreement for one named Large Load, setting when it is curtailed; it has no resale, assignment or transfer provision. The participating transmission owners' own tariffs, which actually provide FILI, were not read | supervisor |
| MISO | ER27-527 (GRITS, the filed name of FLITS) and ER27-526, 16 Nov | Grid Responsive Integration Transmission Service; Interim NITS; Firm Service Step Up | **Not read.** FERC's file list for accession 20261116-5326 names the clean tariff (Tab B, 2.8 MB), but its download service answered a script with HTTP 401; MISO's own filings page lists no 16 Nov documents | — |
| ISO-NE | ER27-484, 13 Nov | Firm, Interim and Non-Firm Contract Demand Service | **Not read.** The filing's PDFs on iso-ne.com returned errors to Grok; FERC's download as for MISO | — |
| SPP | EL26-68, due 20 Nov | — | not yet filed; SPP's existing CHILLS service is non-transferable (read 12 Nov) | — |

Every operator proposes a *non-firm* or *curtailable* service alongside firm service. None read so far lets a data centre's
capacity right detach from the facility it was granted for.

## What this does to the three panel positions

The positions were registered against "a transferable class appears" (lenses A and C) and against "RTOs defend firm-service-only
tariffs" plus a GE Vernova order leg (lens D).

- **Lens D (cover): does not cover.** Its first leg needed operators to defend firm-only service. All five filers instead propose
  non-firm or curtailable services, so the leg did not fire, whatever GE Vernova's Q3 order book shows.
- **Lenses A and C: not fired on the three filings read, not yet resolved.** A tradeable right would have to be in the MISO or
  ISO-NE tariff text or in SPP's filing. The resolution is carried to the SPP row (21 November), with the two unread tariffs.

## What would change this

A clause in the MISO, ISO-NE or SPP tariffs permitting resale, reassignment or redirection of the new service to another load.
Comments and protests are due over the next 30-60 days (PJM asked for 60), and FERC's orders would follow; an order could add
transfer rights none of the filings proposes.

## Files read

| file | source | sha256 |
|---|---|---|
| PJM ER27-531 transmittal and tariff | pjm.com/-/media/DotCom/documents/ferc/filings/2026/20261116-er27-531-000.pdf | 4cb4a22cb514b072b5a8058a31c949e257f7fff7571ed3a8f6a32bc2b855007a |
| CAISO large-loads amendment | caiso.com/documents/nov-16-2026-tariff-amendment-large-loads-er27-532.pdf | d7c1b0f4febe6d25a498bc1d8b0b7ebd9409a157059e27c2e8139803ac5f7f45 |
| NYISO OATT Attachment LL (clean) | nyisoviewer.etariff.biz/ViewerDocLibrary/Filing/Filing5488/Attachments/Att%20VIII%20Clean%20OATT%20Att%20LL.pdf | 1c987df3808971ab1d6507607701dd3430a8af4be124b7a76c855a4785ab5cd5 |
| NYTOs pro forma Large Load Cost Recovery Agreement | nyisoviewer.etariff.biz/ViewerDocLibrary/Filing/Filing5490/Attachments/Att%20E%20Pro%20Forma%20LL%20CRA.pdf | 89d0812cfba6bbe2f59edd2946bd4c611cf138aa1de7be377852885e7d906a68 |
