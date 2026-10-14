# Market Plumbing

What is holding asset prices up, and whose money is behind it?

Market Plumbing is an open research record on that question. It covers US equities first, and government bonds, currencies and commodities as the work reaches them. The current answer is the page [What Holds the Market Up](https://closeofbusiness.github.io/market-plumbing/). The page renders [the answer note](2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md), which is revised in place and is the authority wherever the two differ.

## How claims are handled

Every claim carries one of four grades, defined in [CHARTER.md](CHARTER.md#grades): IDENTITY, MEASURED, BOUNDED, or HYPOTHESIS. Most claims remain hypotheses until they are tested. Claims that fail are withdrawn and kept on record in [CORRECTIONS.md](CORRECTIONS.md), rather than deleted. The record uses free public data only.

## Who does the work

AI models do the research and the writing: Claude (Anthropic) and Grok (xAI) work as peers, and Gemini (Google) is consulted for reading and online research. One person directs the work and sets the standard of evidence.

## Using and citing it

The repository's own write-ups are © closeofbusiness and are licensed under CC BY 4.0. The licence text is in [LICENSE](LICENSE). Reuse requires attribution. Third-party data and paywalled text are summarised and cited, and they are not redistributed.

The working name is Third Derivative Research. The byline is closeofbusiness. Cite the answer note by its title and path: "The answer — what is driving asset prices, and where the money came from", [2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md](2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md). Cite the page [What Holds the Market Up](https://closeofbusiness.github.io/market-plumbing/) separately, as the rendering of that note.

Each file in [dossiers/](dossiers/) gives the current status of its line of work.

On 24 September 2026, nine private files (correspondence and draft briefings that should not have been public) were removed from the repository and its history; the owner's instructions for that day are recorded in [THE_ASK.md](THE_ASK.md), entries E-011 and E-013.

## Finding your way

- [What Holds the Market Up](https://closeofbusiness.github.io/market-plumbing/) is the one-page answer.
- [The answer note](2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md) is the document the page renders.
- [dossiers/](dossiers/) holds one short file for each channel and market.
- [CORRECTIONS.md](CORRECTIONS.md) is the register of withdrawn claims.
- [RESEARCH_STATE.md](RESEARCH_STATE.md) records what is settled, what is contested, and what is open.
- [GLOSSARY.md](GLOSSARY.md) defines the codes, the market terms, and the file-name patterns.
- [REPRODUCE.md](REPRODUCE.md) covers recomputing a figure, the checks, and the inputs that are not in the repository.
- [Where_The_Two_Workstreams_Meet.md](Where_The_Two_Workstreams_Meet.md) joins the two earlier lines of work this record grew out of.

## Checking the work

Scripts that call SEC EDGAR need a contact string.

```bash
export SEC_UA="Your Name you@example.com"
```

[REPRODUCE.md](REPRODUCE.md) explains how to recompute a figure, run the record's checks and obtain the inputs that are not redistributed.
