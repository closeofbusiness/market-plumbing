# Sources and terms for data/jp_life_foreign_bonds/

Each source below is public and free. Retrieval dates are in `fetch_log.csv`. The committed files are derived tables; the raw MoF files and the Bank of Japan statements are in a gitignored cache. These are recorded acquisitions and dispositions, redemptions included. They do not show why any investor acquired or disposed of bonds, or any effect on prices.

- **Ministry of Finance Japan, International Transactions in Securities.** https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/: `monthb3.csv` (long-term debt), `monthb1.csv` (total), `monthb2.csv` (equity and investment fund shares), `monthb4.csv` (short-term debt). Licence: the copyright page (https://www.mof.go.jp/about_mof/notice/index.html) puts site content under the Public Data License 1.0 unless marked otherwise; commercial use is allowed, numerical data are outside copyright, the source is to be cited, and processed content is to be labelled as such. Cite as: Source: Ministry of Finance Japan, "International Transactions in Securities" (designated reporters, monthly; monthb1-b4.csv), https://www.mof.go.jp/policy/international_policy/reference/itn_transactions_in_securities/, PDL1.0, retrieved 2026-10-19. Processed by the Third Derivative project (re-laid out and summed; values unchanged).
- **MoF English FAQ** (https://www.mof.go.jp/english/policy/international_policy/reference/itn_transactions_in_securities/faq_its_english.html): A1 scope, A5 redemptions of overseas government bonds are included in the disposition, A6 recording dates. Read once, not fetched by the build.
- **MoF pages read once** (not fetched by the build): the index, the data notes (`data.htm`), the terms (`terms.html`), the English release schedule (`schedule.htm`) and the notice of 27 December 2013 (`notice/notice20131227.pdf`).
- **Bank of Japan, Statement on Monetary Policy** (https://www.boj.or.jp/en/mopo/mpmdeci/): the twelve statements of `boj_dates.csv`. Only dates and phrases under 15 words are cited; copying with credit is allowed and commercial copying is excluded. Credit: Bank of Japan, Statement on Monetary Policy, with the decision date. The PDFs stay in the cache.
- **BoJ FAQ No. 14** (https://www.boj.or.jp/en/statistics/outline/exp/faqbpsm6.htm): the classification of investor types, cited for the investment trust column.

## Column provenance

- `monthly.csv`, `annual.csv`: MoF monthb1 to monthb4, re-laid out and summed; the amounts are the file's integers in ¥100 million. `file_total_net_100m_yen` is the file's own CY or FY Net cell.
- `questions.csv`: computed here from the monthly Net, acquisition and disposition cells, with exact fractions, rounded half away from zero when written.
- `boj_dates.csv`: the Bank of Japan statements named in its `url` column; `sha256` is of the cached PDF.
- `forecast_score.csv`: the rule registered in CALENDAR.tsv on 2026-10-19, applied to the monthb3 Net cell.
- `pins.csv`, `checks.csv`: values the spec pins and the tests run on them.

## The sign banner on MoF's English index page

The English index page still describes the convention used before January 2014. The file's Note 2 says plus is net acquisition and minus is net disposition, and the files confirm the identity Net = Acquisition − Disposition. The banner is recorded here as stale and is never used in the code.

## Related material, not an input

The life insurers' hedge ratios (the project's FX list, item F9) and the yen-hedged Treasury carry file (`data/hedged_ust_yield/yen_summary.csv`) are related material. No number from either is used here, and no statistic joins them to this series.

## Press reference points (information only)

- Nikkei, 21 Feb 2023, gives the 2022 figure for Japanese life insurers as "a bit over ¥11 trillion" (C14 in `checks.csv`).
- The Japan Times, 8 Dec 2022, gives ¥1.9 trillion for November 2022 (C14).

## Build decisions

Choices made where the specification left one open, and the fixes made after the first build.

- A later vintage of October 2026 adds a `forecast_score.csv` row with `of_record = no` and status `LATE_VINTAGE` (the spec says only that such a row is recorded and never re-scored; a scored word on it could be read as a second score).
- A STOP file makes the whole `fetch` command refuse, not only the MoF files (a MoF failure ends the run, and the BoJ part comes after the MoF part); STOP_BOJ blocks only the BoJ part.
- A failed C08 (the Bank of Japan checksums) is written to `checks.csv` and does not send the build to `_FAILED/`; every other FAIL does.
- In C04, C05 and C06 a gap above the spec's tolerance is a FAIL; the spec's observed maxima are descriptive pins, and a difference from them with the tolerance met is a WARN. C07 is exact and tested on monthb3 only; the other files' dash counts are listed beside it.
- Within-file additivity, annual sums and the sign identity are tested on all four files; the pinned values belong to monthb3.
- `questions.csv` keeps the rows of earlier runs (`run_label` names the vintage) beside the current run.
- `pins.csv` holds the 24 base Net cells of the registered rule and the nine life-insurer raw cells of C02.
- A zero in the denominator of a net ratio is reported as `exceeds_total`.
- The wording check runs over every cell of every committed file, not only over the named text fields.
- Fix after the first build (19 Oct 2026): check C07 first expected 324 dash cells in all, as the spec prints. The spec's own factorisation (108 rows x 3 fields x 4 sectors) is 1,296, and 324 is the count for one sector. The first build observed 1,296 (324 in each of the four sectors, none elsewhere) and failed on the literal 324; the pin is now 1,296.
- Fix after the first build (19 Oct 2026): the Q3 rows of `questions.csv` first named only the total in their `denominator` column; they now begin with the spec's label "share of reported gross contracts (dealer-inclusive)". No value changed. Nothing else was changed after the first build.
