# Parcel RET1 — retirement contributions versus withdrawals (Gemini in ANTIGRAVITY, reading named documents)

ROUTING: Gemini, because the job is to READ documents we name and pull tables out of them — its strongest lane.
Our scripts cannot fetch these sources (ici.org and dol.gov refuse scripted requests; a browser reaches them
fine), so this is a retrieval we genuinely cannot do in-house. NOT a search task: every document is named below.

HANDOFF (before pasting):
1. Download these into one folder (a browser opens them; our scripts get 403):
   - ICI, "The US Retirement Market" — the latest quarterly release (tables of defined-contribution and IRA assets)
     from ici.org/research/stats/retirement
   - ICI Investment Company Fact Book (latest edition), the retirement chapter — icifactbook.org
   - US Department of Labor, EBSA, "Private Pension Plan Bulletin — Abstract of Form 5500 Annual Reports", the
     latest edition and the one five years earlier — dol.gov/agencies/ebsa/researchers/statistics
2. Open Antigravity on that folder and select Gemini. If Antigravity is inconvenient, use the Gemini web chat and
   ATTACH the files — do not paste their text, and turn search OFF: everything needed is in the documents.
3. Paste everything below the line. Copy the returned tables back to Claude verbatim.

---

You are a careful data extractor. Read only the attached documents. Do not search the web, and do not fill any
gap from memory — a missing cell must come back as NOT IN THESE DOCUMENTS.

WHY: we are testing a specific published claim — that America's retirement system is shifting from contributing
to withdrawing, and that this reverses a long-standing automatic bid for equities. We need the flows, not the
asset levels, and we need them with their denominators.

RETURN EXACTLY THESE THREE TABLES, and nothing else.

TABLE 1 — Defined-contribution plan flows, one row per year, most recent ten years available:
| year | total contributions | total distributions/withdrawals | net flow | plan types covered | document + page |

TABLE 2 — IRA flows, same shape:
| year | contributions | withdrawals | rollovers in | net flow | document + page |

TABLE 3 — What share of those assets is in equities, and how it is invested:
| year | DC assets total | share in equity funds | share in target-date funds | share in index funds if stated | document + page |

RULES
- Do not ask clarifying questions. If a table in the documents uses a different definition than the one asked for,
  return what the document actually says and name the difference in the "document + page" cell.
- Every number must carry the page or table number it came from. If two documents disagree, give both rows and say so.
- Every page or table number must be the one printed in the document you are reading. If you cannot locate
  it, write PAGE UNKNOWN. Do not estimate, reconstruct or infer a page, table or exhibit number — an
  approximate citation is worse than none, because it cannot be checked.
- Mark anything you inferred rather than read as UNCERTAIN.
- If a table cannot be built from these documents, say which one and what document would contain it.
- No commentary, no interpretation, no forecast. Tables only.
