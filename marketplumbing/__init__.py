"""market-plumbing: tools for decomposing asset price moves using free data.

The research question is always the same three steps:

1. Decompose the price move into its components (price vs. income / carry).
2. Measure who bought against net supply.
3. Size the funding channels, including the ones that fail.

This package currently provides the primitives for step 1 plus a thin
free-data access layer so updates can be reproduced from public sources.
"""

from .decompose import decompose_total_return, summarize_decomposition

__all__ = ["decompose_total_return", "summarize_decomposition"]
__version__ = "0.1.0"
