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
