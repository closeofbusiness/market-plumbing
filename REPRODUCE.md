# Reproduce

How to run the record's checks, recompute a figure, set the SEC contact string, and read the page locally.

## The record's checks

From the repository root, run `bash bin/check.sh --all`. It checks the record's bookkeeping, not its numbers, and runs in well under a minute. It always exits 0, so read its check-mark lines rather than the exit code.

The command checks the following.

- The goal statement is identical in [THE_ASK.md](THE_ASK.md), [CLAUDE.md](CLAUDE.md), and [RESEARCH_STATE.md](RESEARCH_STATE.md).
- Every top-level markdown file and every top-level folder has a row in the index in [CLAUDE.md](CLAUDE.md). The label on that check is M5; other top-level files are not checked.
- Every cited C-number has exactly one register entry. The labels on that check are M7 and M8.
- No numbered to-do sits outside the ranked list in [RESEARCH_STATE.md](RESEARCH_STATE.md). The label on that check is M6.
- Retracted wording is scanned in the notes outside `_research/` and on the page.
- No DTCC record sits under [data/swap_tape/](data/swap_tape/README.md): no field of 8 to 19 digits (a Dissemination Identifier) and no `CFTC_CUMULATIVE` file or zip. The label on that check is M9; like the others it warns and never blocks.
- Every User-Agent literal in `bin/*.py` is the one neutral string [CLAUDE.md](CLAUDE.md) sets for hosts other than sec.gov, or reads the SEC contact from the `SEC_UA` environment variable, and no User-Agent line carries an `@`. The label on that check is M10.
- No ICE record sits in the repository: no `COTHist*` file anywhere in it (in any letter case), no file outside `bin/` and `_research/` that holds ICE's header line (the first two column names of a COTHist file, run together), and no header in [data/ice_brent/](data/ice_brent/README.md) that names a gross position column (a long, short, spread or open-interest figure). The label on that check is M11; like the others it warns and never blocks.

- No JODI record sits in the repository: no file named `jodi_primary_*`, `primaryyear*` or `secondaryyear*` anywhere in it, no file outside `bin/` and `_research/` whose first line is JODI's CSV header, and no header in [data/jodi_oil/](data/jodi_oil/README.md) (other than `checkpoints.csv`) that holds `ref_area` together with a whole-word `month`, `period`, `time_period` or `date`. The label on that check is M12; like the others it warns and never blocks.

It works with macOS grep and with ugrep.

`bash bin/check.sh --latest` prints the newest correction headings.

## Recomputing a figure

Start with the page, or for the full trail with the answer note, [2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md](2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md). Beside each claim the note names the findings note behind it, and that note names its script in `bin/` and its table in `data/`.

For example, the earnings share of the S&P 500 gain recomputes from [data/p2a_decomposition/decomp_cumulative.csv](data/p2a_decomposition/decomp_cumulative.csv); the figure itself is stated in its findings note.

## Software and SEC_UA

The scripts run under Python 3. Most scripts use the standard library. [requirements.txt](requirements.txt) covers the five scripts in `bin/` that read spreadsheets. They use `xlrd` for `.xls`, `openpyxl` for `.xlsx`, and `pandas` for one of them. The file also covers the numpy scripts under `_research/`. Install the libraries with `pip install -r requirements.txt`.

Scripts that call SEC EDGAR need a contact string. Set it before the script runs.

```bash
export SEC_UA="Your Name you@example.com"
```

## Inputs not redistributed

Shiller's `ie_data.xls`, the FRED series DGS10 and DFII10, and Damodaran's `ERPbymonth.xlsx` are not redistributed. [.gitignore](.gitignore) keeps them out of the repository. Download them from their publishers to the path the script names.

US federal primary sources are kept under `_research/primary_sources/`.

The N-PORT Treasury-duration build, `bin/nport_treasury_duration.py`, reads the SEC bulk N-PORT zips (not redistributed; the landing page and file URL pattern are in the script's docstring, and the download needs the `SEC_UA` above) and R2's gitignored caches. Fill the caches with `python3 bin/r2_duration_supply.py`, then run `python3 bin/nport_treasury_duration.py --zip-dir <folder holding the zips>`; it runs its own tests first and, if a cache file is missing, prints the command that recreates it.
The gate is `data/nport/tsy_checks.csv`: read its FAIL count, not the exit code. A failed hard check writes the outputs to `data/nport/_FAILED/` and leaves the committed files alone.
The Z.1 tables it reconciles against are fetched once by `python3 bin/nport_fetch_z1.py` (Federal Reserve Board, public domain) and are committed under `data/vintages/z1_fund_tsy_20260911/`.

The swap-tape ledger's inputs are not redistributed either. [bin/swap_tape_ledger.py](bin/swap_tape_ledger.py) downloads DTCC's public price dissemination zips into `~/dtcc_ppd/`, outside the repository (the script refuses a cache inside it), and the Treasury CSVs into `data/vintages/swap_tape_ust/`, which `.gitignore` keeps out. The scripted DTCC download is non-commercial and rests on a ruling of the principal that goes against DTCC's website terms ([THE_ASK.md](THE_ASK.md), E-024): any refusal from the server ends the run and writes `~/dtcc_ppd/STOP`, which only a person deletes. `python3 bin/swap_tape_ledger.py selftest` needs no network. [data/swap_tape/README.md](data/swap_tape/README.md) has the commands, the columns and the caveats.

The ICE Brent positioning ledger's inputs are not redistributed either. [bin/pull_ice_brent_cot.py](bin/pull_ice_brent_cot.py) downloads ICE Futures Europe's Commitments of Traders history files into `~/ice_cot/`, outside the repository (the script refuses a cache inside it, and `.gitignore` keeps any `COTHist*.csv` out), and the EIA Brent spot file, which is public domain and is committed as `data/ice_brent/raw/eia_RBRTEd.xls`. The scripted ICE download is non-commercial and rests on a ruling of the principal that goes against ICE's website terms ([THE_ASK.md](THE_ASK.md), E-025, extending E-024): any refusal from either server ends the run and writes `~/ice_cot/STOP`, which only a person deletes. Only net positions and one share of open interest are published, never ICE's gross figures. `python3 bin/pull_ice_brent_cot.py selftest` needs no network, and `build` runs offline from the cache. [data/ice_brent/README.md](data/ice_brent/README.md) has the commands, the columns and the caveats.

The yen and euro rate-gap regression's inputs are not redistributed either. [bin/fx_rate_gap.py](bin/fx_rate_gap.py) downloads 19 files (U.S. Treasury par yields, the Japanese Ministry of Finance's JGB yields and intervention records, the ECB's euro yield-curve parameters and reference rates, the BIS daily exchange rates and one Bundesbank series for a data-quality check) into `data/vintages/fx_rate_gap/`, which `.gitignore` keeps out of the repository; a cache path inside the repository is refused unless git ignores it. The weekly panel built from them is kept there too, because from it a reader could rebuild yield levels, so only the regression statistics, the pre-registered decision, at most five pinned values per source, the intervention list, the checks and the request log are committed in [data/fx_rate_gap/](data/fx_rate_gap/README.md). Requests are sequential, at least two seconds apart, with the project's neutral identification string and no redirects; any refusal writes `data/vintages/fx_rate_gap/STOP`, which only a person deletes. `python3 bin/fx_rate_gap.py selftest` needs no network, and `build` runs offline from the cache. FRED is never used: it refuses scripts.
The four-country yield-comovement build's inputs are not redistributed either. [bin/r15_yield_comovement.py](bin/r15_yield_comovement.py) downloads the US Treasury par yield and real yield curves, the Bundesbank BBSIS 10-year Svensson series, the Bank of England nominal spot-curve zips, the Ministry of Finance Japan JGB rates and the ECB euro-area AAA curve into `~/r15_yield_cache/`, outside the repository (the script refuses a cache inside it, and `.gitignore` keeps `glc*.zip`, `latest-yield-curve-data.zip`, `jgbcme*.csv` and `*BBSIS*` out). The Bundesbank and Bank of England terms do not allow redistributing their series, so only derived statistics are published ([data/r15_yield_comovement/SOURCES.md](data/r15_yield_comovement/SOURCES.md)). Requests are sequential, at least 3 seconds apart, at most 50 per run, with the neutral User-Agent and no address; any status other than 200, a redirect or a body that fails its content test writes `~/r15_yield_cache/STOP`, which only a person deletes. `python3 bin/r15_yield_comovement.py selftest` needs no network; `fetch --archive` (46 requests, about 40 MB) then `build` regenerates every output byte for byte; `mde` re-runs the synthetic false-SHIFT and power tables. [data/r15_yield_comovement/README.md](data/r15_yield_comovement/README.md) has the result and the caveats.
The gold-versus-real-yield study's inputs are not redistributed either. [bin/gold_real_yield_break.py](bin/gold_real_yield_break.py) downloads the World Bank Pink Sheet workbook (the gold price), Treasury's daily real yield files and the Federal Reserve Board's broad dollar index into `~/gold_ry_cache/`, outside the repository (the script refuses a cache inside it, and `.gitignore` keeps any `CMO-Historical-Data-Monthly*.xlsx` out). The workbook's reuse terms are unclear and name commercial data vendors, so the gold price, its changes, fitted values and per-month residuals are never committed; only coefficients, standard errors, intervals, test statistics, break dates and a 2-decimal rolling-slope table are, with the World Bank cited. Any refusal from a server ends the run and writes `~/gold_ry_cache/STOP`, which only a person deletes. `python3 bin/gold_real_yield_break.py selftest` needs no network, and `build` runs offline from the cache. [data/gold_real_yield/README.md](data/gold_real_yield/README.md) has the result and the caveats.
The JODI world oil ledger's inputs are not redistributed either. [bin/build_jodi_oil_ledger.py](bin/build_jodi_oil_ledger.py) downloads the JODI-Oil World Database's annual primary CSV files into `~/jodi_oil/`, outside the repository (the script refuses a cache inside it, and `.gitignore` keeps any `jodi_primary_*.csv`, `primaryyear*.csv` or `secondaryyear*.csv` out), and four EIA Petroleum Supply Monthly workbooks and an extract of EIA's STEO bulk file, which are public domain and are committed under `data/jodi_oil/raw/`. JODI's terms say "All such rights are reserved", so only derived statistics are published and every output carries JODI's citation. The script takes at least 5.05 seconds between requests, at most 20 a run, follows no redirect, and any refusal from either server writes `~/jodi_oil/STOP`, which only a person deletes. `python3 bin/build_jodi_oil_ledger.py selftest` needs no network, and `build` runs offline from the cache. Monthly, on JODI's update days, run `fetch` and then `build`; the first build on a 2026 file last modified on or after 21 October 2026 is the registered one and needs `--panel-sha` from `build --panel-only`. [data/jodi_oil/README.md](data/jodi_oil/README.md) has the commands, the columns and the caveats.

The FX-hedged Treasury yield build's inputs are not redistributed either. [bin/hedged_ust_yield.py](bin/hedged_ust_yield.py) downloads the U.S. Treasury par yields, the Ministry of Finance Japan JGB yields, the ECB euro yield-curve parameters and euro short-term rate, the New York Fed's SOFR, EFFR and SOFR Index, the Bank of Japan's TONA, the Bundesbank 10-year series and a 118 MB panel of Du, Keerati and Schreger (of which only the yen and euro 3-month and 1-year rows are kept) into `data/vintages/hedged_ust_yield/`, which `.gitignore` keeps out of the repository; the daily panel and the yen monthly rows stay there too. The swap-tape cells come only from `data/swap_tape/monthly_short_tenor.csv`, which `python3 bin/swap_tape_ledger.py monthly` writes offline from the cached DTCC files (THE_ASK.md E-024); the hedged-yield script never reads DTCC files. Any HTTP status other than 200 (206 for the panel probe), or a body that is not the file asked for, ends the run and writes `data/vintages/hedged_ust_yield/STOP`, which only a person deletes. `python3 bin/hedged_ust_yield.py selftest` needs no network. [data/hedged_ust_yield/README.md](data/hedged_ust_yield/README.md) gives the columns, the terms and the Bank of Japan credit; yen appears there only as annual figures.

## Old scratchpad paths

Some older notes cite a path beginning `<session-scratchpad>/`. Before 9 October 2026 that path was `/private/tmp/claude-501/`. The workspace has been deleted. The durable copy is the repository path cited alongside it.

From the repository root, `python3 bin/check_scratchpad_refs.py` lists any path that still has the `/private/tmp/` form.

## Viewing the page locally

GitHub Pages publishes [docs/](docs/) from `main`. The page is online at [What Holds the Market Up](https://closeofbusiness.github.io/market-plumbing/).

To read the page locally, clone the repository and serve the `docs/` folder.

```bash
git clone https://github.com/closeofbusiness/market-plumbing.git
cd market-plumbing
python3 -m http.server 8000 --directory docs
```

Then open http://localhost:8000.
