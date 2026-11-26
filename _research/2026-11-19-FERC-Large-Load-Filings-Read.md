# Can a data centre's grid right be sold? The 16 November 2026 FERC filings, read

19 November 2026, updated 21 November. Five grid operators filed their large-load proposals at FERC on 13-16 November 2026, answering the show-cause
orders in dockets EL26-67 (PJM), EL26-69 (NYISO), EL26-70 (MISO), EL26-71 (CAISO) and EL26-72 (ISO-NE). SPP (EL26-68) filed on
18-19 November. The question carried here since August ([the Parcel C note](../2026-08-22-Parcel-C-FERC-Return.md), section 6.4) is
whether any of them creates a large-load or flexible-load service whose rights can be **sold, assigned or traded** to another load.
Grok found the filings and read them first; its three returns are kept verbatim in
[the readings note](2026-11-19-FERC-Large-Load-Grok-Readings.md). Every finding below was re-read by the supervisor in the filed document itself, downloaded from the operator's own site or from
FERC eLibrary (sha256 in the last section).

## The answer: no filing that was read creates a tradeable right

| operator | filing | new service | can the right be sold or moved to another load? | read by |
|---|---|---|---|---|
| PJM | ER27-531, 16 Nov | Interim Network Integration Transmission Service; Firm and Non-Firm Contract Demand Transmission Service | **No.** Proposed tariff §701.4 bars use of the interim service for "sales of energy to loads other than" the load named in the agreement, and for "provision of transmission service ... to third parties"; the transmittal (p. 38) states the same for Contract Demand service. §711(a) lets a *successor customer* take over service to the same load under a new agreement; that changes who serves the load, not where the right is used | supervisor |
| NYISO | ER27-517, 16 Nov (Attachment LL); NYTOs ER27-529 | Firm and Non-Firm Withdrawal Service | **No, not on its own.** Attachment LL §44.7.1.3 allows a queue position to move to another entity "only if" it "acquires the specific Large Load Project", at the same point of interconnection. The transmission owners' cost-recovery agreement (§4.2) is "specific to a single Large Load Facility"; §9.7 allows assignment only with consent and with the other agreements | supervisor |
| CAISO | ER27-532, 16 Nov | Flexible Interim Load Interconnection (FILI): curtailable connection before upgrades are built | **Silent.** Tariff §25.7.2 provides FILI through a three-party agreement for one named Large Load, setting when it is curtailed; it has no resale, assignment or transfer provision. The participating transmission owners' own tariffs, which actually provide FILI, were not read | supervisor |
| MISO | ER27-527 (GRITS, the filed name of FLITS), 16 Nov | Grid Responsive Integration Transmission Service: firm and non-firm, to the customer's point(s) of delivery | **Silent; resale routed elsewhere.** The clean tariff (Tab B) has no assignment, reassignment or resale provision for GRITS. §37B.7 requires a GRITS customer to "use Point-To-Point Transmission Service" for any third-party sale outside the MISO region. The operating agreement (Attachment G-1) has no transfer clause. The companion ER27-526 (Interim NITS, Firm Service Step Up) was not read | supervisor |
| ISO-NE | ER27-484, 13 Nov | Firm, Interim and Non-Firm Contract Demand Service | **Silent; tied to a named project.** Part II.J (§II.57) and the service agreement (Attachment S) have no assignment, resale or transfer clause; the agreement names the project, location and points of delivery, and resuming service after termination needs a new application. The tariff's resale and reassignment provisions (Schedule 20B, Attachment H-1) cover point-to-point service only. The study agreement (Attachment U §14.1) needs ISO consent to assign; it covers the study, not the service | supervisor |
| SPP | ER27-578, 19 Nov (Price Adaptive Load Service, "related to" EL26-68); also ER27-559 (18 Nov) and ER27-577 (19 Nov), which create no service | Price Adaptive Load Service (PALS): non-firm, curtailable, price-adaptive, one to ten years, any commercial or industrial load | **No.** Proposed tariff §54.5: "PALS is not available for resale, redirection, reassignment, or transfer of service under this Tariff." The service agreement (Attachment BG, §14.0) "may not be assigned, resold, or transferred by either Party." SPP's existing CHILLS is likewise non-transferable | supervisor (added 21 Nov) |

Every operator proposes a *non-firm* or *curtailable* service. PJM, NYISO, MISO and ISO-NE pair it with firm service; CAISO's is
an interim connection and SPP's new service is non-firm only. No filing that was read lets a data centre's capacity right detach from the
facility it was granted for: three bar it (PJM, NYISO, SPP), three are silent and tie the service to a named load or project
(CAISO, MISO, ISO-NE). Silence is not a bar, and two documents were not read: the CAISO transmission owners' own tariffs, which
provide the CAISO service, and MISO's companion filing ER27-526.

## What this does to the three panel positions

The positions were registered against "a transferable class appears" (lenses A and C) and against "RTOs defend firm-service-only
tariffs" plus a GE Vernova order leg (lens D).

- **Lens D (cover): does not cover.** Its first leg needed operators to defend firm-only service. All six filers instead propose
  non-firm or curtailable services, so the leg did not fire, whatever GE Vernova's Q3 order book shows.
- **Lenses A and C: did not fire at any of the six operators.** Decline-to-answer and size zero stand. SPP, the last leg, filed
  its new service on 19 November with an express bar on transfer (added 21 November).

## What would change this

Nothing filed so far. Comments and protests are due over the next 30-60 days (PJM asked for 60), and FERC's orders on the six
proposals would follow; an order could add transfer rights that none of the filings asks for.

## Files read

| file | source | sha256 |
|---|---|---|
| PJM ER27-531 transmittal and tariff | pjm.com/-/media/DotCom/documents/ferc/filings/2026/20261116-er27-531-000.pdf | 4cb4a22cb514b072b5a8058a31c949e257f7fff7571ed3a8f6a32bc2b855007a |
| CAISO large-loads amendment | caiso.com/documents/nov-16-2026-tariff-amendment-large-loads-er27-532.pdf | d7c1b0f4febe6d25a498bc1d8b0b7ebd9409a157059e27c2e8139803ac5f7f45 |
| NYISO OATT Attachment LL (clean) | nyisoviewer.etariff.biz/ViewerDocLibrary/Filing/Filing5488/Attachments/Att%20VIII%20Clean%20OATT%20Att%20LL.pdf | 1c987df3808971ab1d6507607701dd3430a8af4be124b7a76c855a4785ab5cd5 |
| NYTOs pro forma Large Load Cost Recovery Agreement | nyisoviewer.etariff.biz/ViewerDocLibrary/Filing/Filing5490/Attachments/Att%20E%20Pro%20Forma%20LL%20CRA.pdf | 89d0812cfba6bbe2f59edd2946bd4c611cf138aa1de7be377852885e7d906a68 |
| MISO GRITS clean tariff (Tab B, accession 20261116-5326) | FERC eLibrary | 607586ea9676ab2c37cd2703b37fb4e64d34ed8b345f6183fbfda77f9f16aacd |
| ISO-NE clean tariff, ISO files (accession 20261113-5007) | FERC eLibrary | 98e3829ab1944d92344d788a30116ed0734a7d6519f0e29e41733e541227449c |
| ISO-NE clean tariff, transmission-owner files (same accession) | FERC eLibrary | be854c08b8bf28c323fa22a747446e2e42a228f5aab51a86fa1695dc11e05dc0 |
| SPP ER27-578 transmittal and tariff (Price Adaptive Load Service) | spp.org/documents/78398/ | 108f9650ab0a08a57054e8dcc5ca1500dac8250d9a2ca1c090f896924b28629c |

The MISO and ISO-NE files came through FERC eLibrary's public download, the request its file-list page makes (the principal
approved the download). An earlier "401" from that service was the supervisor's malformed request, not a refusal.
