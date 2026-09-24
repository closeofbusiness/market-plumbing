# market-plumbing

Public research on what moves asset prices and where the money comes from — equities, Treasuries, JGBs, euro-area government bonds, FX, and commodities. Each update decomposes the price move, measures who bought against net supply, then sizes the funding channels, including the ones that fail. Free data only. Hypotheses until tested.

## What's here

- `marketplumbing/` — reusable primitives.
  - `decompose.py` — split a total return into **price** and **income (carry)** channels (step 1 of every update).
  - `data.py` — thin free-data access layer (Yahoo Finance + FRED).
- `examples/decompose_demo.py` — end-to-end demo that pulls free data and decomposes a move.
- `tests/` — deterministic unit tests (no network).

## Setup

Requires Python 3.10+ (developed on 3.12). The one-command bootstrap creates a
virtualenv and installs pinned dependencies:

```bash
bash .cursor/install.sh
source .venv/bin/activate
```

This is the same script the Cloud Agent environment (`.cursor/environment.json`)
runs, so local and remote setups match.

## Usage

Run the end-to-end demo (needs network for the free data pull):

```bash
python examples/decompose_demo.py --ticker SPY --start 2024-01-01
```

Use the primitives directly:

```python
from marketplumbing import decompose_total_return, summarize_decomposition
from marketplumbing.data import fetch_prices

prices = fetch_prices("SPY", start="2024-01-01")
decomp = decompose_total_return(prices)
print(summarize_decomposition(decomp))
```

## Tests

```bash
pytest
```

Unit tests use synthetic data and do not touch the network.
