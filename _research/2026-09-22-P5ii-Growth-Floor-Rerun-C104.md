# P5(ii) growth-floor re-run against −17.4bp (C-104) — 22 Sep 2026

**Status: FOLDED LOOSE END, not a parcel.** Re-runs the growth floor in `2026-09-13-P5ii-Growth-Versus-Risk.md` against the fully FRED-consistent Damodaran restatement named in C-104. Does not reopen the 60.3% claim.

## Inputs (carried, not re-estimated)

| quantity | value | source |
|---|---:|---|
| Our trailing-residual compression Dec-2023→Jun-2026 | **48.59bp** ≈ **49bp** | P5ii |
| Damodaran ERP restated, project splice (T-Bond + FRED breakeven) | **−29.31bp** | P5ii / C-104 |
| Damodaran ERP restated, fully FRED-consistent | **−17.4bp** | C-104 |

## Arithmetic (denominator = our 48.59bp compression)

| basis | "risk" leg \|Damodaran\|/ours | growth residual (ours − \|Dam\|) | growth share |
|---|---:|---:|---:|
| Project splice (−29.31bp) | 29.31 / 48.59 = **60.3%** | 19.28bp | **39.7%** ≈ "at least ~40%" floor |
| Fully FRED (−17.4bp) | 17.4 / 48.59 = **35.8%** | 31.19bp | **64.2%** |

Re-derive check: `48.59 − 17.4 = 31.19`; `31.19 / 48.59 = 0.6419`.

## Verdict for the live §1 claim

1. **The "~60% survives as risk" point estimate does not survive C-104.** Across the two defensible bases the Damodaran-attributed share of our compression is **~36–60%**. Quote the range or neither; do not quote 60.3% alone.
2. **The growth floor strengthens, it does not break.** P5ii said growth-consistent share is **at least ~40% (19bp)** using the splice. On the FRED basis the growth residual is **~31bp (~64%)**. So the floor "≥ ~40% growth-consistent" still holds, and the FRED basis pushes *more* of the compression toward growth, not less.
3. **Honest §1 phrasing:** the gap between earnings yield and the real rate compressed; of that compression, a Damodaran-style forward ERP that nets growth leaves a **~36–60%** remainder that is *not* attributed to his growth input, while **≥ ~40%** (and ~64% on the FRED restatement) is growth-consistent. Interpretation remains unsettled; a third independent premium is still required (P5ii § "What would actually settle it").

## Do not say

- That C-104 falsifies the compression itself (direction and magnitude of *our* residual stand).
- That "mostly cheaper risk" is MEASURED (C-104 / C-102).
- Any scalar M.

Pointer: C-104; parent `2026-09-13-P5ii-Growth-Versus-Risk.md`.
