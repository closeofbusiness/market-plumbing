# Sources and terms for data/swap_tape/

Derived from DTCC Public Price Dissemination, CFTC cumulative interest-rate reports (pddata.dtcc.com). Statistics only; no DTCC record is
reproduced. Non-commercial research (THE_ASK.md E-024).

- **DTCC.** The inputs are the daily CFTC cumulative interest-rate files that DTCC publishes under the CFTC's real-time reporting rules
  (https://pddata.dtcc.com). The principal chose to script the downloads despite DTCC's website terms (THE_ASK.md E-024, "(a)"), on
  these conditions: non-commercial use; no raw DTCC file or row is committed or redistributed; only derived statistics (medians,
  quartiles, counts, shares) are published, under a count floor (fewer than 5 observations: the count only; 5 to 9: count and median;
  10 or more: quartiles as well); and every table cites DTCC. The raw files are kept outside the repository and are never
  committed. Requests are sequential and paced, carry a neutral project User-Agent without a name or address, and any refusal
  ends the run. `fetch_log.csv` records every request; `holes.csv` records dates DTCC no longer serves.
- **U.S. Treasury.** Daily Treasury Par Yield Curve Rates and Daily Treasury Real Yield Curve Rates (home.treasury.gov), the constant-maturity
  (CMT) series. U.S. Government work, public domain. `ust_used.csv` holds the values joined to each date, with the sha256 of the file and
  the date it was fetched.
- **Licence.** CC BY 4.0 (the repository's LICENSE) covers only this project's computation and write-up. It does not extend to DTCC or to
  any data of DTCC; the use of DTCC's data is non-commercial under THE_ASK.md E-024 and nothing in this folder licenses anyone else to
  use DTCC's data commercially.
- **Retrieval dates.** Every CSV starts with a `# source:` comment line naming the source and the retrieval dates. Readers must skip lines
  that start with `#`. Per-file retrieval dates are in `file_stats.csv` (`retrieved_utc`) and `fetch_log.csv`.
- **Nothing here says a flow moves a price.** The ledger measures levels and gaps. See README.md for the columns and the caveats.
