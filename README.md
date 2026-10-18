# Market Plumbing

What is holding asset prices up, and whose money is behind it?

Market Plumbing is an open research record on that question. It covers US equities first. Government bonds are covered as first passes, and currencies and commodities have a first measurement map and four tests. The current answer is the page [What Holds the Market Up](https://closeofbusiness.github.io/market-plumbing/), which is the authoritative overview. The evidence behind each of its claims is set out in [the answer note](2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md) and the findings notes it names.

*As at 18 October 2026. Personal opinion, not investment advice, and published for academic and entertainment purposes only. See the [disclaimer](DISCLAIMER.md).*

## How claims are handled

Every claim carries one of four grades, defined in [CHARTER.md](CHARTER.md#grades):

- **IDENTITY**: true by construction, given its inputs, so it says nothing about the world.
- **MEASURED**: observed on a stated universe with a stated denominator.
- **BOUNDED**: a ceiling or a floor, one side only, never a point estimate.
- **HYPOTHESIS**: untested, or tested and still standing, which is not the same as established.

Most claims remain hypotheses until they are tested. Claims that fail are withdrawn and kept on record in [CORRECTIONS.md](CORRECTIONS.md), rather than deleted. The record uses free public data only.

## Who does the work

AI models do the research and the writing: Claude (Anthropic) and Grok (xAI) work as peers, and Gemini (Google) is consulted for reading and online research. One person directs the work and sets the standard of evidence.

## Using and citing it

Three names appear on this work. Market Plumbing is the project and this repository. Third Derivative Research is the working name of the research series, and the name to cite. closeofbusiness is the byline.

The repository's own write-ups are © closeofbusiness and are licensed under CC BY 4.0. The licence text is in [LICENSE](LICENSE). Reuse requires attribution. Paywalled text is summarised and cited, not copied. Some third-party data and documents are included so results can be rebuilt; they keep their owners' terms and are listed in [data/THIRD_PARTY_MANIFEST.tsv](data/THIRD_PARTY_MANIFEST.tsv).

Cite the page: Third Derivative Research, "What Holds the Market Up", https://closeofbusiness.github.io/market-plumbing/, with the date shown on the page. For a single claim, cite the findings note named beside it in [the answer note](2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md).

## Finding your way

- [What Holds the Market Up](https://closeofbusiness.github.io/market-plumbing/) is the one-page answer and the authority.
- [The answer note](2026-09-17-ANSWER-What-Is-Driving-Asset-Prices.md) sets out the evidence behind the page, claim by claim.
- [dossiers/](dossiers/) holds one short file for each channel and market, giving the current status of that line of work.
- [CORRECTIONS.md](CORRECTIONS.md) is the register of withdrawn claims.
- [RESEARCH_STATE.md](RESEARCH_STATE.md) records what is settled, what is contested, and what is open.
- [GLOSSARY.md](GLOSSARY.md) defines the codes, the market terms, and the file-name patterns.
- [REPRODUCE.md](REPRODUCE.md) covers recomputing a figure, the checks, and the inputs that are not in the repository.
- [Where_The_Two_Workstreams_Meet.md](Where_The_Two_Workstreams_Meet.md) joins the two earlier lines of work this record grew out of: Third Derivative, which asked who captures the value when a capacity overbuild strands assets, and Collateral Multiplier, which asked where the money in the AI, private-equity and private-credit nexus comes from and whether the plumbing can absorb a reversal.

## Checking the work

Scripts that call SEC EDGAR need a contact string.

```bash
export SEC_UA="Your Name you@example.com"
```

[REPRODUCE.md](REPRODUCE.md) explains how to recompute a figure, run the record's checks and obtain the inputs that are not redistributed.

## Disclaimer

This project is the personal opinion of the person who directs it, has nothing to do with any employer, and is not investment, financial, legal, accounting or tax advice. It is published for academic and entertainment purposes only, AI models write it, and errors are expected, so take your own professional advice before acting on anything here. Read the full [DISCLAIMER.md](DISCLAIMER.md).
