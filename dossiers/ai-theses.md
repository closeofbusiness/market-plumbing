# AI theses

This is the register of claims about what AI is doing to the economy and to markets, and of the numbers that track AI
adoption. The mission asks for it (THE_ASK E-028, E-029). Every thesis here is a hypothesis until a registered test scores
it. A thesis that fails is kept, with its result, so that it is not quietly re-asserted later.

How a thesis enters: write it as one sentence that could be wrong, name the free data that could test it, then register the
test blind before reading the data that decides it (the house method). How it leaves: never. Its status changes.

## The theses

| id | thesis | where it came from | test | status |
|---|---|---|---|---|
| T1 | The AI build-out is paid for by new money, shadow credit or a broad bond bid, rather than by the spenders' own operating cash | the original ask | [`ai-funding.md`](ai-funding.md) | **Sized: mostly self-funded**; leases and guarantees are the off-balance-sheet leg to watch |
| T2 | AI lowers managers' uncertainty, so firms outside the AI complex move idle cash into capex | the principal, Nov 2026 | CV1 ([`data/cv1_confidence_velocity/`](../data/cv1_confidence_velocity/README.md)), stages 2-4 | **AGAINST on free data** (P1-P5); P6 (AI use by industry against the capex change) shows no link |
| T3 | AI is raising the formation of new companies | the principal (E-028), citing Apollo's "The AI Entrepreneurship Boom", 15 Nov 2026 | AF1 ([`data/af1_ai_formation/`](../data/af1_ai_formation/README.md)) | **Mixed**: national applications still rising (+7.3%, 2025 on 2024); across 14 industries, the speed-up since 2017-19 is larger where AI use is higher (SUPPORT on one of four labelled tests), but not after removing information and professional services. The pattern is not evidence of cause |
| T4 | AI is raising productivity and profit margins in the industries that use it | proposed by the agent (E-029), confirmed by the principal (E-030) | not yet registered. Candidate data: BLS labor productivity by industry, BEA industry gross output and operating surplus, BTOS AI use | open |
| T5 | AI creates more jobs than it displaces | Apollo's note ("the job-creating effect of AI is far bigger"); proposed (E-029), confirmed (E-030) | AJ1 ([`data/aj1_ai_jobs/`](../data/aj1_ai_jobs/README.md)) | **No displacement pattern in employment; openings result does not last.** Across 19 industries, employment growth 2023-25 is not linked to AI use (rank correlation -0.23, INCONCLUSIVE; against the 2017-19 trend -0.26, INCONCLUSIVE). Job openings fell in all 15 JOLTS industries from 2023 to 2025 and fell least where AI use is higher (+0.80, SUPPORT), but the link is gone in 2024-25 (+0.01) and in the latest twelve months (-0.09): openings fell most in 2023-25 in construction, manufacturing, wholesale trade and transport, which use little AI, and that gap has since closed. No label measures the economy-wide net |
| T6 | Equity prices already capitalise AI gains that earnings have not yet delivered | proposed by the agent (E-029), confirmed (E-030); links the AI theses to the asset-price question | not yet registered. Candidate data: the fundamentals benchmark ([`fundamentals-benchmark.md`](fundamentals-benchmark.md)) split into AI and non-AI firms | open |

## The AI metrics we track

| metric | source (free) | frequency | latest reading we hold |
|---|---|---|---|
| Share of US firms using AI to produce goods or services | Census BTOS, original question (to Oct 2025); the new-wording series from Dec 2025 is a separate series | every two weeks | 10.0% of firms, cycle 202520 (collected 22 Sep to 5 Oct 2025), original wording |
| Share expecting to use AI within six months | Census BTOS | every two weeks | 14.0%, same cycle |
| AI use by industry | Census BTOS by sector | every two weeks | information 20.9%, professional services 16.2%, accommodation and food 1.9% (2024-25 means) |
| New business applications | Census Business Formation Statistics | monthly, weekly | 478,332 a month in Jan-Nov 2025, +7.3% on 2024 (not seasonally adjusted) |
| Employment and job openings by industry | BLS CES and JOLTS (API v1) | monthly | AJ1 build of 16 Nov 2026: CES to Oct 2026, JOLTS to Sep 2026 |
| Hyperscaler capex and its funding | company filings | quarterly | [`ai-funding.md`](ai-funding.md) |

To add: the new-wording BTOS AI series (from Dec 2025) as a separate line, and AI's share of venture funding if a free source
is found.
