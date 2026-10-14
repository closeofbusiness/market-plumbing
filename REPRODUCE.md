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

It works with macOS grep and with ugrep.

`bash bin/check.sh --latest` prints the newest correction headings.

## Recomputing a figure

Start with the answer note, [2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md](2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md). Beside each claim it names the findings note behind it, and that note names its script in `bin/` and its table in `data/`.

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
