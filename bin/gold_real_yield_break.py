#!/usr/bin/env python3
"""Gold against the US 10-year real yield: monthly changes, HAC errors, a break scan. Python 3 standard library plus numpy and
openpyxl (both in requirements.txt). statsmodels is NOT used; every estimator is written by hand and pinned by the selftest.

  python3 bin/gold_real_yield_break.py fetch [--cache DIR] [--out DIR] [--sleep 5.05]   # the only network command; at most 12 requests, 8 for a full fetch
  python3 bin/gold_real_yield_break.py build [--cache DIR] [--out DIR]                  # offline from the cache; byte-identical on re-run
  python3 bin/gold_real_yield_break.py selftest [--mutants]                             # synthetic data only; no network

Specification: _research/2026-10-18-Gold-Real-Yield-Break-Spec.md (with its Amendments section, and its "Builder decisions" section where the
spec is silent). E-021 build queue item 5. P1 is the ONE confirmatory test; every other object is descriptive (registry in REGISTRY).

LICENCE (R1). The World Bank Pink Sheet gold price never enters the repository. The workbook lives in the cache (default ~/gold_ry_cache/,
which the script refuses to place inside the repository). No committed file carries a gold price, a log price, a gold change, a fitted
value, a per-month residual or a residual in sd units. The ONE per-month file that depends on gold is rolling36.csv, published at 2 decimals
(A3). The monthly panel with gold and the residual path go to <cache>/local_outputs/ only. Public GLD data already approximates the Pink
Sheet series (second reviewer: median monthly gap 0.034%), so the restriction follows the World Bank's redistribution terms; it is not about
secrecy.

WHAT TOUCHES THE NETWORK. Only `fetch`. Hosts: thedocs.worldbank.org, home.treasury.gov, www.federalreserve.gov (nothing else, FRED never).
GET only; one request at a time; at least 5 s between request starts (5.05 s, persisted in ~/gold_ry_cache/.last_request beside the fixed
STOP path); at most 12 requests per run; the CLAUDE.md non-SEC User-Agent (no address, no name); redirects are NOT followed. HTTP 401, 403,
429, any 3xx, or a body that fails its content test writes ~/gold_ry_cache/STOP and ends the run. While STOP exists nothing is fetched and
only a person deletes it. A 5xx or a socket fault ends the run without latching. No retry, ever. Every request is one row of
data/gold_real_yield/fetch_log.csv.

THE POLICY ON OFFICIAL GOLD FLOWS (R5). This script never reads data/gold/ledger_monthly.csv or any tonnes series. A stock or a flow is never
written as the cause of a price.
"""
import argparse
import builtins
import contextlib
import csv
import datetime as dt
import hashlib
import http.client
import io
import math
import os
import re
import sys
import tempfile
import time
import zipfile
from functools import lru_cache
from urllib.parse import urlsplit

import numpy as np

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT_DEFAULT = os.path.join(ROOT, "data", "gold_real_yield")
CACHE_DEFAULT = "~/gold_ry_cache"
STOP_PATH = os.path.expanduser("~/gold_ry_cache/STOP")        # fixed, whatever --cache says (R3)
SEED = 20261018

UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
HEADERS = {"User-Agent": UA, "Accept-Encoding": "identity"}
WB_HOST, TR_HOST, FED_HOST = "thedocs.worldbank.org", "home.treasury.gov", "www.federalreserve.gov"
HOSTS = (WB_HOST, TR_HOST, FED_HOST)
MIN_SLEEP = 5.05
MAX_REQUESTS = 12
TIMEOUT = 120
BODY_CAP = 40 * 1024 * 1024

WB_RX = re.compile(r"/en/doc/[0-9a-f]{32}-[0-9]+/related/CMO-Historical-Data-Monthly\.xlsx")
WB_PATH = "/en/doc/74e8be41ceb20fa0da750cda2f6b9e4e-0050012026/related/CMO-Historical-Data-Monthly.xlsx"
D2_PATH = "/system/files/276/par-real-yield-curve-rates-2003-2023.csv"
D3_FMT = ("/resource-center/data-chart-center/interest-rates/daily-treasury-rates.csv/{y}/all?type=daily_treasury_real_yield_curve"
          "&field_tdr_date_value={y}&page&_format=csv")
D3_RX = re.compile(re.escape(D3_FMT).replace(r"\{y\}", r"(20[0-9]{2})"))
D4_PATH = "/system/files/221/fy2021-mc-vs-hs-combined.csv"
DDP_FMT = ("/datadownload/Output.aspx?rel=H10&series={sid}&lastobs=&from=&to=&filetype=csv&label=include&layout=seriescolumn&type=package")
D5_SID, D6_SID = "847be2166a425bda9b4d92465f797544", "122e3bcb627e8e53f1bf72a1a09cfb81"
D5_PATH, D6_PATH = DDP_FMT.format(sid=D5_SID), DDP_FMT.format(sid=D6_SID)
FED_IDS = {"D5": "H10/H10/JRXWTFB_N.M", "D6": "H10/H10/JRXWTFB_N.B"}

# ----------------------------------------------------------------------------------------------------------------------------------
# configuration: the pre-registered sample. The selftest builds with a synthetic copy (dates in 2030-2050).
# ----------------------------------------------------------------------------------------------------------------------------------
REAL_CFG = dict(
    name="real", live=True,
    first_level="2006-01", end="2026-09", fit_end="2021-11", d2_start="2003-01",
    seam_date=dt.date(2021, 12, 6), seam_month="2021-12", knot_month="2008-12", gold_def_month="2025-06",
    impulse=(("2008-12", "d_2008_12"), ("2021-12", "d_2021_12"), ("2022-01", "d_2022_01"), ("2025-06", "d_2025_06")),
    subperiods=(("2006-02", "2021-11"), ("2021-12", "2023-12"), ("2024-01", "2026-09")),
    chow=("2008-12", "2021-12"),
    boot_B=999, roll_B=999, roll_first_end="2009-01", roll_window=36, block_roll=6, boot_block=6, ci_dummy_month="2021-12",
    sd_draws=20000,
)
SYN_CFG = dict(
    name="synthetic", live=False,
    first_level="2030-01", end="2042-09", fit_end="2038-11", d2_start="2027-01",
    seam_date=dt.date(2035, 12, 6), seam_month="2035-12", knot_month="2032-12", gold_def_month="2039-06",
    impulse=(("2032-12", "d_2008_12"), ("2035-12", "d_2021_12"), ("2036-01", "d_2022_01"), ("2039-06", "d_2025_06")),
    subperiods=(("2030-02", "2038-11"), ("2038-12", "2040-06"), ("2040-07", "2042-09")),
    chow=("2032-12", "2035-12"),
    boot_B=9, roll_B=9, roll_first_end="2033-01", roll_window=36, block_roll=6, boot_block=6, ci_dummy_month="2035-12",
    sd_draws=500,
)

TRIMS = (0.05, 0.15, 0.25)
PRE_REG_TRIM = 0.15
HAC_FLOOR = 12
MATERIAL = -0.050                      # log points of gold per pp of real yield (the materiality line, §3.6)
Z80 = 0.84
BAI_ANCHOR = 11.03
S_MIN_H = (4, 6, 8, 12, 18)
NO_2026_SENTENCE = ("No trim can return a 2026 break date: the latest candidate under any trim is 2025-08. "
                    "A 2026 change in sensitivity is not testable as a break date on this sample.")

# fixed registry of estimated objects (R6): an object id outside it is a hard failure
REGISTRY = ("P1", "B1", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9")
CONFIRMATORY = ("P1",)

# Andrews (2003, Econometrica 71(1):395-397, Table I), sup Wald, 10/5/1 percent
ANDREWS = {
    (1, 0.05): (8.13, 9.71, 13.17), (1, 0.15): (7.12, 8.68, 12.16), (1, 0.25): (6.35, 7.87, 11.28),
    (3, 0.05): (13.46, 15.36, 19.28), (3, 0.15): (12.28, 14.13, 18.07), (3, 0.25): (11.32, 13.18, 17.13),
}
# MacKinnon (2010, Queen's QED WP 1227): C(T) = c0 + c1/T + c2/T^2 + c3/T^3, 5 percent, N = 3 (tau_c Table 2, tau_ct Table 3)
MACK_TAUC = (-3.74066, -8.5631, -10.852, 27.982)
MACK_TAUCT = (-4.11890, -11.8922, -19.031, 77.332)
MACK_TAUC_N2 = (-3.33613, -6.1101, -6.823, 0.0)       # N = 2: used only by the selftest mutant


# ----------------------------------------------------------------------------------------------------------------------------------
# mutants: every mutant is a small deviation behind mut("<name>"); only the selftest ever switches one on, in this process
# ----------------------------------------------------------------------------------------------------------------------------------
_MUT = set()


def mut(name):
    return name in _MUT


@contextlib.contextmanager
def mutant(*names):
    added = [n for n in names if n not in _MUT]
    _MUT.update(added)
    try:
        yield
    finally:
        for n in added:
            _MUT.discard(n)


class Refused(Exception):
    """A request, path or setting this script will not honour (host list, cache inside the repo, spacing, cap)."""


class MaxRequests(Refused):
    """The per-run request cap was reached: an orderly end, not a refusal by a server."""


class Latched(Exception):
    """A technical refusal: ~/gold_ry_cache/STOP was written (or already existed); the run ends."""


class SocketFault(Exception):
    """Timeout, reset, TLS error or a 5xx: the invocation ends without latching."""


class DataError(Exception):
    """A hard check on the data failed. The build stops."""


# ----------------------------------------------------------------------------------------------------------------------------------
# small helpers
# ----------------------------------------------------------------------------------------------------------------------------------
def tilde(p):
    home = os.path.expanduser("~")
    return str(p).replace(home, "~") if home and home != "~" else str(p)


def f(v, nd):
    """Fixed-decimal text, '' for None, no negative zero, no scientific notation (byte-stable outputs)."""
    if v is None:
        return ""
    s = format(round(float(v), nd), ".%df" % nd)
    return s[1:] if s.startswith("-") and float(s) == 0 else s


def sha256_of(b):
    return hashlib.sha256(b).hexdigest()


def month_add(m, k):
    y, mo = int(m[:4]), int(m[5:7])
    t = y * 12 + (mo - 1) + k
    return "%04d-%02d" % (t // 12, t % 12 + 1)


def month_diff(a, b):
    return (int(a[:4]) * 12 + int(a[5:7])) - (int(b[:4]) * 12 + int(b[5:7]))


def month_range(a, b):
    return [month_add(a, i) for i in range(month_diff(b, a) + 1)]


def assert_ua(ua=UA):
    if "@" in ua:
        raise Refused("User-Agent contains an address")
    for var in ("SEC_UA", "CLAUDE_CODE_USER_EMAIL"):
        v = os.environ.get(var, "").strip()
        if v and (v in ua or ua in v):
            raise Refused("User-Agent contains a configured contact value (not printed)")


assert_ua()


def pct_exact(b):
    """100(e^b - 1): b = -0.202 gives -18.29 (G3)."""
    return 100.0 * b if mut("g3_pct_exact_lin") else 100.0 * (math.exp(b) - 1.0)


def chi2_sf3(x):
    """Survival function of chi-square with 3 degrees of freedom (closed form)."""
    if x <= 0:
        return 1.0
    return math.erfc(math.sqrt(x / 2.0)) + math.sqrt(2.0 * x / math.pi) * math.exp(-x / 2.0)


# ----------------------------------------------------------------------------------------------------------------------------------
# estimators (hand written): OLS, Newey-West HAC with the Bartlett kernel, fixed-b critical value, Wald
# ----------------------------------------------------------------------------------------------------------------------------------
def rule_lag(n):
    """The rule-of-thumb lag floor(4 (n/100)^(2/9)); 4 at n = 248."""
    return int(math.floor(4.0 * (n / 100.0) ** (2.0 / 9.0)))


def hac_lag(n):
    """L = max(12, rule) for the primary design (G1). Windows with n < 100 use the rule-of-thumb lag (D5)."""
    r = rule_lag(n)
    if mut("g1_lag_rule"):
        return r
    return max(HAC_FLOOR, r) if n >= 100 else max(1, r)


def bart_w(l, L):
    """Bartlett weight 1 - l/(L+1) (G2)."""
    return 1.0 - l / float(L) if mut("g2_weights_L") else 1.0 - l / (L + 1.0)


def nw_S(Z, L):
    """Z = x_t e_t (n x k). S = Gamma_0 + sum_{l=1..L} w_l (Gamma_l + Gamma_l'), Gamma_l = sum_{t>l} z_t z_{t-l}'. No dof correction."""
    S = Z.T @ Z
    for l in range(1, L + 1):
        G = Z[l:].T @ Z[:-l]
        S = S + bart_w(l, L) * (G + G.T)
    return S


def nw_S_loop(Z, L):
    """The same matrix by explicit loops, with the weights written out (the G2 reference; never mutated)."""
    n, k = Z.shape
    S = np.zeros((k, k))
    for t in range(n):
        S += np.outer(Z[t], Z[t])
    for l in range(1, L + 1):
        G = np.zeros((k, k))
        for t in range(l, n):
            G += np.outer(Z[t], Z[t - l])
        S += (1.0 - l / (L + 1.0)) * (G + G.T)
    return S


def ols(X, y):
    XtXi = np.linalg.inv(X.T @ X)
    beta = XtXi @ (X.T @ y)
    return beta, y - X @ beta, XtXi


def hac_V(X, e, L, XtXi=None):
    if XtXi is None:
        XtXi = np.linalg.inv(X.T @ X)
    S = nw_S(X * e[:, None], L)
    return XtXi @ S @ XtXi


def kv_cubic(b):
    """Kiefer-Vogelsang (2005) cubic for the Bartlett 97.5% quantile of the fixed-b t limit."""
    return 1.96 + 2.9694 * b + 0.4160 * b ** 2 - 0.5324 * b ** 3


def p1_cv(n, L):
    """The critical value the P1 verdict uses: the cubic at b = L/n, rounded to 3 dp (2.105 at b = 12/248)."""
    if mut("g4_z196") or mut("g28_z196"):
        return 1.96
    if mut("g4_old_cv"):
        return 2.2414
    return round(kv_cubic(L / float(n)), 3)


def fit(y, X, L, names=None):
    """OLS with classical and Newey-West HAC covariance."""
    n, k = X.shape
    beta, e, XtXi = ols(X, y)
    ssr = float(e @ e)
    s2 = ssr / (n - k)
    V = hac_V(X, e, L, XtXi)
    tss = float(((y - y.mean()) ** 2).sum())
    return dict(beta=beta, e=e, XtXi=XtXi, V=V, n=n, k=k, ssr=ssr, se_cls=np.sqrt(s2 * np.diag(XtXi)), se_hac=np.sqrt(np.diag(V)),
                r2=1.0 - ssr / tss if tss > 0 else float("nan"), L=L)


def wald(delta, V):
    return float(delta @ np.linalg.solve(V, delta))


def verdict_regions(b, lo, hi):
    """Each rule is written on its own (§4); the selftest checks that exactly one holds on a grid (G5)."""
    out = set()
    if b <= MATERIAL and hi < 0:
        out.add("SUPPORTS")
    if lo > MATERIAL or (mut("g5_overlap") and b > MATERIAL):
        out.add("AGAINST")
    if lo <= MATERIAL and (hi >= 0 or b > MATERIAL):
        out.add("INCONCLUSIVE")
    return out


def verdict(b, lo, hi):
    r = verdict_regions(b, lo, hi)
    if len(r) != 1:
        raise DataError("verdict regions are not exclusive and exhaustive at b=%r lo=%r hi=%r: %s" % (b, lo, hi, sorted(r)))
    return next(iter(r))


def t_hac_batch(X, Y, L, j=1):
    """Coefficient j and its HAC standard error for many y vectors at once (rows of Y), X fixed. For the simulations."""
    XtXi = np.linalg.inv(X.T @ X)
    A = XtXi @ X.T
    beta = Y @ A.T
    E = Y - beta @ X.T
    c = X @ XtXi[j]
    Q = E * c[None, :]
    V = (Q * Q).sum(1)
    for l in range(1, L + 1):
        V = V + 2.0 * bart_w(l, L) * (Q[:, l:] * Q[:, :-l]).sum(1)
    return beta[:, j], np.sqrt(V)


def null_size(X, Y_iid, Y_ar, L, cv):
    out = []
    for Y in (Y_iid, Y_ar):
        b, se = t_hac_batch(X, Y, L)
        out.append(float((np.abs(b / se) > cv).mean()))
    return tuple(out)


def sim_noise(rs, N, n, rho=0.2, burn=100):
    iid = rs.randn(N, n)
    eps = rs.randn(N, n + burn)
    y = np.zeros((N, n + burn))
    y[:, 0] = eps[:, 0]
    for t in range(1, n + burn):
        y[:, t] = rho * y[:, t - 1] + eps[:, t]
    return iid, y[:, burn:]


@lru_cache(maxsize=None)
def fixed_b_limit(N=1000, L=48, draws=20000, seed=SEED):
    """Seeded simulation of the fixed-b Bartlett limit of the t statistic in the location model (the G4 reference). Returns the 97.5% quantile
    of |t|. L/N = 0.048, close to the P1 design b = 12/248 = 0.0484."""
    rs = np.random.RandomState(seed)
    abs_t = []
    chunk = 2000
    for _ in range(draws // chunk):
        y = rs.randn(chunk, N)
        e = y - y.mean(1, keepdims=True)
        V = (e * e).sum(1)
        for l in range(1, L + 1):
            V = V + 2.0 * (1.0 - l / (L + 1.0)) * (e[:, l:] * e[:, :-l]).sum(1)
        abs_t.append(np.abs(y.sum(1) / np.sqrt(V)))
    return float(np.quantile(np.concatenate(abs_t), 0.95))


# ----------------------------------------------------------------------------------------------------------------------------------
# trims, candidates, sup-Wald scan, Bai interval, stationary bootstrap
# ----------------------------------------------------------------------------------------------------------------------------------
def cand_range(n, pi):
    """k = ceil(pi n) .. floor((1-pi) n): k is the number of change observations in regime 1 (G7)."""
    n_eff = n + 1 if mut("g7_trim_levels_T") else n
    lo = math.ceil(round(pi * n_eff, 9))
    if mut("g7_ceil_off_by_one"):
        lo = math.floor(round(pi * n_eff, 9))
    hi = math.floor(round((1.0 - pi) * n_eff, 9))
    if mut("g8_cands_to_n_minus_1"):
        hi = n - 1
    return int(lo), int(hi)


def candidate_months(change_months, pi):
    lo, hi = cand_range(len(change_months), pi)
    return change_months[lo - 1], change_months[hi - 1]


def trim_table(change_months):
    return [(pi,) + candidate_months(change_months, pi) for pi in TRIMS]


def scan(Y, X0, extra, cands, L):
    """Sup-Wald scan, vectorised over the rows of Y and the candidates. X0 (n x 3) are the regressors that shift; `extra` (n x m or None) do not.
    Per candidate k the model is [X0, extra, X0 * 1{t > k}] by OLS; the HAC covariance (lag L) comes from that unrestricted model; the Wald tests
    the three shift coefficients. Returns wald (B x nc), ssr (B x nc), delta (B x nc x 3), residual-variance parts are recomputed by callers."""
    Y = np.atleast_2d(Y)
    B, n = Y.shape
    base = X0 if extra is None else np.hstack([X0, extra])
    if mut("g29_hac_restricted"):
        A0 = np.linalg.inv(base.T @ base) @ base.T
        E0 = Y - (Y @ A0.T) @ base.T
    W_all = np.empty((B, len(cands)))
    S_all = np.empty((B, len(cands)))
    D_all = np.empty((B, len(cands), 3))
    idx = np.arange(n)
    for ci, k in enumerate(cands):
        kk = k + 1 if mut("g29_cand_shift") else k
        Xk = np.hstack([base, X0 * (idx >= kk)[:, None]])
        XtXi = np.linalg.inv(Xk.T @ Xk)
        beta = Y @ (XtXi @ Xk.T).T
        E = Y - beta @ Xk.T
        R = XtXi[-3:, :]
        P = Xk @ R.T
        Escore = E0 if mut("g29_hac_restricted") else E
        Wt = Escore[:, :, None] * P[None, :, :]
        S = np.matmul(Wt.transpose(0, 2, 1), Wt)
        for l in range(1, L + 1):
            G = np.matmul(Wt[:, l:, :].transpose(0, 2, 1), Wt[:, :-l, :])
            S = S + bart_w(l, L) * (G + G.transpose(0, 2, 1))
        d = beta[:, -3:]
        W_all[:, ci] = np.einsum("bi,bi->b", d, np.linalg.solve(S, d[:, :, None])[:, :, 0])
        S_all[:, ci] = (E * E).sum(1)
        D_all[:, ci, :] = d
    return W_all, S_all, D_all


def scan_reference(y, X0, extra, cands, L):
    """One candidate at a time by explicit loops: fit, HAC, Wald (G29 reference; never mutated)."""
    base = X0 if extra is None else np.hstack([X0, extra])
    n = len(y)
    out = []
    for k in cands:
        post = (np.arange(n) >= k).astype(float)
        Xk = np.hstack([base, X0 * post[:, None]])
        beta = np.linalg.lstsq(Xk, y, rcond=None)[0]
        e = y - Xk @ beta
        S = nw_S_loop(Xk * e[:, None], L)
        XtXi = np.linalg.inv(Xk.T @ Xk)
        V = XtXi @ S @ XtXi
        d = beta[-3:]
        out.append(float(d @ np.linalg.solve(V[-3:, -3:], d)))
    return np.array(out)


def pick_break_ssr(wald_row, ssr_row, cands):
    """Bai's estimator: the argmin of total SSR over the candidates (G10)."""
    if mut("g10_first_wald_over_chi2"):
        for i, w in enumerate(wald_row):
            if w > 7.81:
                return i
        return int(np.argmax(wald_row))
    return int(np.argmin(ssr_row))


def bai_halfwidth(delta, Omega, Q):
    """h = 11.03 (d'Omega d)/(d'Q d)^2 months (G9)."""
    anchor = 7.7 if mut("g9_anchor_7_7") else BAI_ANCHOR
    num = float(delta @ Omega @ delta)
    den = float(delta @ Q @ delta)
    return anchor * num / den ** 2


def s_min(h, omega22, q22):
    """The smallest slope-only shift a half-width of h months can date: sqrt(11.03 Omega22 / (h Q22^2))."""
    return math.sqrt(BAI_ANCHOR * omega22 / (h * q22 ** 2))


def bai_interval(khat, h, n, ssr_row=None, cands=None):
    """[k - ceil(h), k + ceil(h)] unclipped, plus the clipped display bounds. Returns (lo, hi, lo_c, hi_c, clipped, width_unclipped)."""
    c = int(math.ceil(h))
    lo, hi = khat - c, khat + c
    if mut("g9_pointwise") and ssr_row is not None:
        ssr_min = float(np.min(ssr_row))
        ok = [k for k, s in zip(cands, ssr_row) if s <= ssr_min * (1.0 + 3.84 / n)]
        lo, hi = min(ok), max(ok)
    lo_c, hi_c = max(1, lo), min(n, hi)
    clipped = (lo != lo_c) or (hi != hi_c)
    width = (hi_c - lo_c) if mut("g9_clipped_width") else (hi - lo)
    return lo, hi, lo_c, hi_c, clipped, width


def stationary_idx(rs, n, B, mean_block):
    """Politis-Romano stationary bootstrap indices: circular, geometric blocks with the given mean length."""
    start = rs.randint(0, n, size=(B, n))
    new = rs.rand(B, n) < 1.0 / mean_block
    new[:, 0] = True
    idx = np.empty((B, n), dtype=np.int64)
    idx[:, 0] = start[:, 0]
    for t in range(1, n):
        idx[:, t] = np.where(new[:, t], start[:, t], (idx[:, t - 1] + 1) % n)
    return idx


def mbb_idx(rs, n, block, B):
    """Moving-block bootstrap row indices, B draws of length n, blocks of `block` consecutive rows (G22)."""
    blk = 1 if mut("g22_block_len_1") else block
    nb = int(math.ceil(n / float(blk)))
    starts = rs.randint(0, n - blk + 1, size=(B, nb))
    idx = (starts[:, :, None] + np.arange(blk)[None, None, :]).reshape(B, nb * blk)[:, :n]
    return idx


def andrews_cv(q, pi, level_index):
    """level_index 0, 1, 2 = 10%, 5%, 1% (G6)."""
    if mut("g6_chi2_7_81") and q == 3 and abs(pi - 0.15) < 1e-12 and level_index == 1:
        return 7.81
    return ANDREWS[(q, round(pi, 2))][level_index]


# ----------------------------------------------------------------------------------------------------------------------------------
# Engle-Granger test (descriptive gate) and MacKinnon critical values
# ----------------------------------------------------------------------------------------------------------------------------------
def mack_cv(T, trend=False):
    c = MACK_TAUCT if trend else (MACK_TAUC_N2 if mut("g11_N2") else MACK_TAUC)
    return c[0] + c[1] / T + c[2] / T ** 2 + c[3] / T ** 3


def adf_noconst(z, p):
    """dz_t = rho z_{t-1} + sum_{j=1..p} phi_j dz_{t-j}, no constant, t = p+1..T-1. Returns (tau, rho, N, ssr, k)."""
    return _adf(z, p, p + 1)


def _adf(z, p, t0):
    z = np.asarray(z, dtype=float)
    T = len(z)
    dz = np.concatenate([[np.nan], np.diff(z)])
    ts = np.arange(t0, T)
    y = dz[ts]
    cols = [z[ts - 1]] + [dz[ts - j] for j in range(1, p + 1)]
    X = np.column_stack(cols)
    beta, e, XtXi = ols(X, y)
    N, k = X.shape
    ssr = float(e @ e)
    se = math.sqrt(ssr / (N - k) * XtXi[0, 0])
    return beta[0] / se, beta[0], N, ssr, k


def eg_test(g, X, trend=False, pmax=12):
    """Engle-Granger on a sample: OLS of g on X (X includes the constant; a trend is added if `trend`), then the ADF with AIC lag over 0..pmax on
    a common sample that starts at lag pmax, re-run at the chosen lag on the longest sample. Returns (stat, p, T)."""
    T = len(g)
    Xr = X if not trend else np.column_stack([X, np.arange(T, dtype=float)])
    if mut("g12_adf_on_levels"):
        z = np.asarray(g, dtype=float)
    else:
        z = ols(Xr, g)[1]
    best, bp = None, 0
    for p in range(0, pmax + 1):
        _, _, N, ssr, k = _adf(z, p, pmax + 1)
        aic = N * math.log(ssr / N) + 2 * (p + 1)
        if best is None or aic < best:
            best, bp = aic, p
    tau = adf_noconst(z, bp)[0]
    return tau, bp, T


# ----------------------------------------------------------------------------------------------------------------------------------
# dates and parsing
# ----------------------------------------------------------------------------------------------------------------------------------
def parse_us_date(s):
    """'1/2/03' -> 2003-01-02; '12/29/2023' -> 2023-12-29 (G15). Two-digit years map to 20YY."""
    m = re.fullmatch(r"\s*(\d{1,2})/(\d{1,2})/(\d{2}|\d{4})\s*", s)
    if not m:
        raise DataError("unparseable date %r" % s)
    mo, d, y = int(m.group(1)), int(m.group(2)), m.group(3)
    year = int(y) if mut("g15_naive_year") else (2000 + int(y) if len(y) == 2 else int(y))
    return dt.date(year, mo, d)


def parse_treasury(raw):
    """[(date, 10 YR in percent)]; a blank 10 YR cell is an error. Header quoted (D3) or not (D2)."""
    text = raw.decode("utf-8-sig")
    rd = csv.reader(io.StringIO(text))
    header = None
    for row in rd:
        if row and any(c.strip() for c in row):
            header = [c.strip() for c in row]
            break
    if header is None or "Date" not in header or "10 YR" not in header:
        raise DataError("Treasury file: header lacks Date / 10 YR")
    i_d, i_10 = header.index("Date"), header.index("10 YR")
    out = []
    for row in rd:
        if not row or not any(c.strip() for c in row):
            continue
        v = row[i_10].strip()
        if v == "":
            raise DataError("Treasury file: blank 10 YR on %s" % row[i_d])
        out.append((parse_us_date(row[i_d]), float(v)))
    return out


def parse_d4(raw):
    """(mean of MC minus HS in pp, number of days) from Treasury's overlap file."""
    text = raw.decode("utf-8-sig")
    rows = list(csv.reader(io.StringIO(text)))
    hdr = [c.strip() for c in rows[0]]
    if "real_hs_cmt_10yr" not in hdr or "real_mc_cmt_10yr" not in hdr:
        raise DataError("D4: columns real_hs_cmt_10yr / real_mc_cmt_10yr not found")
    ih, im = hdr.index("real_hs_cmt_10yr"), hdr.index("real_mc_cmt_10yr")
    diffs = []
    for r in rows[1:]:
        if not r or len(r) <= max(ih, im):
            continue
        a, b = r[ih].strip(), r[im].strip()
        if a == "" or b == "":
            continue
        diffs.append(float(b) - float(a))
    if not diffs:
        raise DataError("D4: no overlap rows")
    return sum(diffs) / len(diffs), len(diffs)


def parse_fed(raw, want_id, base_month=None, monthly=True):
    """Fed DDP package: header block, then 'YYYY-MM[-DD],value' rows. Returns (unit_label, {period: value}). The base (value 100.0000 at
    base_month) is asserted from the VALUE, never from the Unit: label (G16). ND / NA / blank are skipped."""
    text = raw.decode("utf-8-sig")
    rows = list(csv.reader(io.StringIO(text)))
    hdr = {r[0].strip(): r[1:] for r in rows[:8] if r}
    ids = [x.strip() for x in hdr.get("Unique Identifier:", [])]
    if want_id not in ids:
        raise DataError("Fed package: unique identifier %s not found" % want_id)
    i = ids.index(want_id)
    mult = float(hdr.get("Multiplier:", ["1"])[i])
    unit = hdr.get("Unit:", [""])[i].strip()
    out = {}
    for r in rows:
        if r and re.fullmatch(r"\d{4}-\d{2}(-\d{2})?", r[0].strip()):
            v = r[i + 1].strip()
            if v in ("", "ND", "NA"):
                continue
            out[r[0].strip()] = float(v) * mult
    if monthly and base_month is not None and not mut("g16_base_label"):
        if base_month not in out or abs(out[base_month] - 100.0) > 1e-6:
            raise DataError("Fed dollar index: the value at %s is %r, not 100.0000 (the base is asserted from the value; the label says %r)"
                            % (base_month, out.get(base_month), unit))
    return unit, out


def find_gold_column(rows, header_rows=14):
    """rows: list of tuples of the first rows of 'Monthly Prices'. The column whose header is 'Gold' with units '($/troy oz)' in the same
    column in the next rows (G17). Returns (column index, header row index)."""
    for ri, row in enumerate(rows[:header_rows]):
        for ci, v in enumerate(row):
            if isinstance(v, str) and v.strip() == "Gold":
                for rj in range(ri + 1, min(ri + 4, len(rows))):
                    u = rows[rj][ci] if ci < len(rows[rj]) else None
                    if isinstance(u, str) and u.strip() == "($/troy oz)":
                        return ci + 1 if mut("g17_col_off_by_one") else ci, ri
    raise DataError("Monthly Prices: no 'Gold' column with units ($/troy oz) in the same column")


def parse_gold(raw):
    """(gold {YYYY-MM: float}, updated_on text, last month). Content test is the same function."""
    import openpyxl
    if raw[:4] != b"PK\x03\x04":
        raise DataError("World Bank file is not a zip/xlsx")
    wb = openpyxl.load_workbook(io.BytesIO(raw), read_only=True, data_only=True)
    if "Monthly Prices" not in wb.sheetnames:
        raise DataError("sheet 'Monthly Prices' not found")
    rows = [tuple(r) for r in wb["Monthly Prices"].iter_rows(values_only=True)]
    ci, ri = find_gold_column(rows)
    updated = ""
    texts = [c for r in rows[:6] for c in r if isinstance(c, str)]
    if "Description" in wb.sheetnames:
        texts += [c for r in wb["Description"].iter_rows(values_only=True) for c in r if isinstance(c, str)]
    for t in texts:
        m = re.search(r"Updated on\s+([A-Za-z]+ \d{1,2}, \d{4})", t)
        if m:
            updated = m.group(1)
            break
    gold = {}
    for r in rows[ri + 1:]:
        if not r or not isinstance(r[0], str):
            continue
        m = re.fullmatch(r"\s*(\d{4})M(\d{2})\s*", r[0])
        if not m or ci >= len(r):
            continue
        v = r[ci]
        if isinstance(v, (int, float)):
            gold["%s-%s" % (m.group(1), m.group(2))] = float(v)
    if not gold:
        raise DataError("no gold values parsed")
    return gold, updated, max(gold)


# ----------------------------------------------------------------------------------------------------------------------------------
# the monthly panel
# ----------------------------------------------------------------------------------------------------------------------------------
def monthly_tips(daily, gap, seam_date):
    """{month: dict(mc, off, days, mc_days)}. mc = mean over the month's prints of print + gap if dated before the seam (G14)."""
    g = -gap if mut("g14_sign_flip") else gap
    acc = {}
    for d, v in daily:
        m = "%04d-%02d" % (d.year, d.month)
        pre = (d <= seam_date) if mut("g14_le_seam") else (d < seam_date)
        if mut("g14_whole_month") and (d.year, d.month) == (seam_date.year, seam_date.month):
            pre = True
        a = acc.setdefault(m, [0.0, 0.0, 0, 0])
        a[0] += v + (g if pre else 0.0)
        a[1] += v
        a[2] += 1
        a[3] += 0 if d < seam_date else 1
    return {m: dict(mc=a[0] / a[2], off=a[1] / a[2], days=a[2], mc_days=a[3], sum_off=a[1]) for m, a in acc.items()}


def decision_end(cfg, months_available):
    """The decision sample ends at cfg['end'] even when the cache holds later months (G26)."""
    if mut("g26_end_from_latest"):
        return max(months_available)
    return cfg["end"]


class Panel:
    """Monthly levels and changes on explicit YYYY-MM keys (G30)."""

    def __init__(self, cfg, gold, tips_m, usd):
        end = decision_end(cfg, list(gold))
        self.cfg, self.end = cfg, end
        self.months = month_range(cfg["first_level"], end)          # levels sample
        self.dmonths = month_range(cfg["d2_start"], end)             # long yield sample (D2)
        gm = dict(gold)
        if mut("g30_gold_shift"):
            gm = {m: gold.get(month_add(m, -1), gold[m]) for m in gold}      # each month carries the previous month's price
        miss = [m for m in self.dmonths if m not in gm or m not in tips_m]
        if miss:
            raise DataError("missing gold or yield months: %s ..." % miss[:3])
        miss_u = [m for m in self.months if m not in usd]
        if miss_u:
            raise DataError("missing dollar months: %s ..." % miss_u[:3])
        self.g_all = np.array([math.log(gm[m]) for m in self.dmonths])
        self.r_mc_all = np.array([tips_m[m]["mc"] for m in self.dmonths])
        self.r_off_all = np.array([tips_m[m]["off"] for m in self.dmonths])
        self.u = np.array([math.log(usd[m]) for m in self.months])
        self.tips_m = tips_m
        self.gold_raw = gold
        self.usd = usd
        off = month_diff(cfg["first_level"], cfg["d2_start"])
        self.off = off
        self.g = self.g_all[off:]
        self.r = self.r_mc_all[off:]
        self.r_off = self.r_off_all[off:]
        self.cmonths = self.months[1:]                                # change sample
        self.dg, self.dr, self.du = np.diff(self.g), np.diff(self.r), np.diff(self.u)
        self.dr_off = np.diff(self.r_off)
        self.n = len(self.dg)
        self.dcmonths = self.dmonths[1:]
        self.dg_long, self.dr_long = np.diff(self.g_all), np.diff(self.r_mc_all)

    def ci(self, month, long=False):
        return (self.dcmonths if long else self.cmonths).index(month)

    def csl(self, a, b, long=False):
        return slice(self.ci(a, long), self.ci(b, long) + 1)

    def lsl(self, a, b):
        return slice(self.months.index(a), self.months.index(b) + 1)

    def X(self, sl=None, dollar=True, r="mc"):
        sl = slice(None) if sl is None else sl
        dr = self.dr if r == "mc" else self.dr_off
        cols = [np.ones(self.n), dr] + ([self.du] if dollar else [])
        return np.column_stack(cols)[sl]

    def impulse(self, month):
        v = np.zeros(self.n)
        if month in self.cmonths:
            v[self.cmonths.index(month)] = 1.0
        return v


# ----------------------------------------------------------------------------------------------------------------------------------
# outputs: exact column allowlists, source lines, verification of the written text (K08 / G18 / G19)
# ----------------------------------------------------------------------------------------------------------------------------------
INPUTS_COLS = ["month", "tips10_avg_pct_mc", "tips10_avg_pct_official", "tips10_days", "tips10_mc_day_share", "usd_broad_2006jan100", "seam_flag"]
RESULTS_COLS = ["object_id", "role", "sample_start", "sample_end", "n", "regressors", "coef_name", "coef", "coef_unit", "pct_approx", "pct_exact",
                "se_classical", "se_hac", "hac_lag", "hac_lag_rule", "crit_value", "crit_basis", "ci_level", "ci_low", "ci_high", "r2", "mde80",
                "flag", "verdict"]
COINT_COLS = ["test_id", "role", "sample_start", "sample_end", "T", "adf_lags", "adf_stat", "cv_5pct", "reject_5pct", "levels_printed"]
BREAK_COLS = ["trim", "dummy_spec", "first_candidate", "last_candidate", "n_candidates", "sup_wald", "p_value_boot", "boot_draws", "boot_mean_block",
              "andrews_cv10", "andrews_cv5", "andrews_cv1", "break_month_ssr", "break_month_supwald", "bai_ci_low", "bai_ci_high",
              "bai_halfwidth_months", "ci_clipped", "s_min_h4", "s_min_h6", "s_min_h8", "s_min_h12", "s_min_h18", "resid_var_regime1",
              "resid_var_regime2", "hac_lag"]
CHOW_COLS = ["regime2_start", "wald_hac", "df", "p_chi2", "hac_lag", "role"]
ROLL_COLS = ["end_month", "n", "beta_ry", "boot_lo", "boot_hi", "block_len", "draws", "seed"]
LEVELS_COLS = ["object_id", "fit_start", "fit_end", "coef_name", "coef", "ci_low", "ci_high", "hac_lag", "resid_sd_in_sample", "residual_label", "status"]
CHECKS_COLS = ["check_id", "description", "expected", "observed", "status"]
VINT_COLS = ["source", "file", "retrieved_utc", "sha256", "bytes", "published_updated_on", "last_obs"]
LOG_COLS = ["utc", "host", "path", "status", "bytes", "sha256", "outcome"]
ALLOW = {"monthly_inputs.csv": INPUTS_COLS, "results.csv": RESULTS_COLS, "cointegration.csv": COINT_COLS, "break.csv": BREAK_COLS,
         "chow_known_dates.csv": CHOW_COLS, "rolling36.csv": ROLL_COLS, "levels_summary.csv": LEVELS_COLS, "checks.csv": CHECKS_COLS,
         "vintages.csv": VINT_COLS, "fetch_log.csv": LOG_COLS}
ALLOWED_FILES = tuple(sorted(list(ALLOW) + ["rolling36.svg", "README.md", "SOURCES.md"]))
BANNED_HDR = re.compile(r"gold|ln_g|dln|fitted|price")
HDR_EXEMPT = ("resid_sd_in_sample", "resid_var_regime1", "resid_var_regime2")
TWO_DP = ("beta_ry", "boot_lo", "boot_hi")
SOURCE_MAIN = ("# source: World Bank Commodity Price Data (the Pink Sheet), monthly workbook retrieved {wb} (derived statistics only; the gold "
               "price is not redistributed); US Department of the Treasury, par real yield curve rates, retrieved {tr}; Board of Governors "
               "of the Federal Reserve System, Data Download Program, H.10 nominal broad dollar index, retrieved {fed}")
SOURCE_LOG = ("# source: request log for the World Bank, US Treasury and Federal Reserve Board files read by bin/gold_real_yield_break.py; "
              "each row carries its own UTC time")


def source_line(name, retrieved):
    if name == "fetch_log.csv":
        return SOURCE_LOG
    line = SOURCE_MAIN.format(wb=retrieved["wb"], tr=retrieved["tr"], fed=retrieved["fed"])
    return line + (" (built %s)" % dt.datetime.now().isoformat()) if mut("g27_timestamp") else line


def check_header_allowed(name, header):
    if name not in ALLOW:
        raise DataError("no column allowlist for output file %s" % name)
    if list(header) != ALLOW[name]:
        extra = [h for h in header if h not in ALLOW[name]]
        raise DataError("%s: header differs from its allowlist (not allowed: %s; missing: %s)"
                        % (name, ", ".join(extra) or "-", ", ".join(h for h in ALLOW[name] if h not in header) or "-"))
    bad = [h for h in header if h not in HDR_EXEMPT and (BANNED_HDR.search(h) or h.startswith("resid_"))]
    if bad:
        raise DataError("%s: banned header cell: %s" % (name, ", ".join(bad)))


def render_table(header, rows, source):
    out = io.StringIO()
    out.write(source + "\n")
    w = csv.writer(out, lineterminator="\n")
    w.writerow(header)
    w.writerows(rows)
    return out.getvalue()


def split_table(text):
    lines = text.split("\n")
    rd = list(csv.reader(io.StringIO("\n".join(l for l in lines if not l.startswith("#")), newline="")))
    return lines[0], rd[0], [r for r in rd[1:] if r]


def dec_places(s):
    return len(s.split(".")[1]) if "." in s else 0


def verify_text(name, text):
    """The written text is checked, not the rows it came from: source line, exact allowlist, banned cells, 2 dp on the rolling slopes."""
    first, header, body = split_table(text)
    if not first.startswith("# source:"):
        raise DataError("%s: the first line is not a `# source:` line" % name)
    if name != "fetch_log.csv" and not all(w in first for w in ("World Bank", "Treasury", "Federal Reserve")):
        raise DataError("%s: the source line must name the World Bank, Treasury and the Federal Reserve Board" % name)
    check_header_allowed(name, header)
    if name == "rolling36.csv":
        for c in TWO_DP:
            j = header.index(c)
            for r in body:
                if dec_places(r[j]) > 2:
                    raise DataError("rolling36.csv: %s has %r, more than 2 decimals" % (c, r[j]))
    home = os.path.expanduser("~")
    if home != "~" and home in text:
        raise DataError("%s: an absolute home path would be published" % name)
    return header, body


def write_text(path, text):
    os.makedirs(os.path.dirname(path), exist_ok=True)
    tmp = path + ".tmp"
    with open(tmp, "w", encoding="utf-8", newline="") as fh:
        fh.write(text)
    os.replace(tmp, path)


def read_table(path, header=None):
    if not os.path.exists(path):
        return []
    with open(path, encoding="utf-8", newline="") as fh:
        lines = [ln for ln in fh.read().splitlines(True) if not ln.startswith("#")]
    rd = list(csv.reader(io.StringIO("".join(lines))))
    if not rd:
        return []
    if header is not None and list(rd[0]) != list(header):
        raise DataError("unexpected header in " + tilde(path))
    return rd[1:]


def leak_scan(out_dir):
    """K08 (G19): the explicit file and column allowlist. Returns a list of problems (empty = pass)."""
    probs = []
    if not os.path.isdir(out_dir):
        return ["output directory missing"]
    for nm in sorted(os.listdir(out_dir)):
        if nm not in ALLOWED_FILES:
            probs.append("file not on the allowlist: " + nm)
    for nm in sorted(ALLOW):
        p = os.path.join(out_dir, nm)
        if not os.path.exists(p):
            continue
        try:
            with open(p, encoding="utf-8") as fh:
                verify_text(nm, fh.read())
        except DataError as e:
            probs.append(str(e))
    for root, _, files in os.walk(out_dir):
        for nm in files:
            if nm.lower().endswith((".xlsx", ".xls", ".zip")):
                probs.append("spreadsheet/zip under the output directory: " + nm)
    return probs


# ----------------------------------------------------------------------------------------------------------------------------------
# analysis: P1 and the descriptive objects
# ----------------------------------------------------------------------------------------------------------------------------------
REG_NAMES = "const;d_ry;d_ln_usd"
UNITS = {"a_const": "log points", "b_ry": "log points per pp of real yield", "c_usd": "elasticity: % per 1% dollar"}


def regressors_text(names):
    names = list(names)
    if mut("g20_tonnes_regressor"):
        names = names + ["official_change_cf_t"]
    return ";".join(names)


def coef_rows(obj, role, s0, s1, y, X, cnames, regs, L=None, flag="", hac=True):
    n = len(y)
    if L is None:
        L = hac_lag(n)
    fp = fit(y, X, L)
    b = L / float(n)
    cv = p1_cv(n, L) if obj == "P1" else round(kv_cubic(b), 3)
    rows = []
    for i, nm in enumerate(cnames):
        c, se = float(fp["beta"][i]), float(fp["se_hac"][i])
        bcv = 1.96 if mut("g4_band_196") else cv                  # the band must use the same critical value the row prints
        lo, hi = c - bcv * se, c + bcv * se
        isb = nm == "b_ry"
        unit = UNITS.get(nm, "log points")
        pct = nm.startswith("d_") or isb
        rflag = flag + ("; hac_se_degenerate_for_one_month_dummy" if nm.startswith("d_") and obj == "D4" else "")
        row = dict(object_id=obj, role=role, sample_start=s0, sample_end=s1, n=n, regressors=regs, coef_name=nm, coef=f(c, 4), coef_unit=unit,
                   pct_approx=f(100 * c, 1) if pct else "", pct_exact=f(pct_exact(c), 1) if pct else "",
                   se_classical=f(fp["se_cls"][i], 4), se_hac=f(se, 4), hac_lag=L, hac_lag_rule=rule_lag(n), crit_value=f(cv, 3),
                   crit_basis="fixed_b_KV2005_b=%s" % f(b, 4), ci_level="0.95", ci_low=f(lo, 4), ci_high=f(hi, 4), r2=f(fp["r2"], 4),
                   mde80=f((cv + Z80) * se, 4) if isb else "", flag=rflag, verdict="")
        if obj == "P1" and isb:
            row["verdict"] = verdict(c, lo, hi)
        rows.append(row)
    return rows, fp


def simple_slope(x, y):
    X = np.column_stack([np.ones(len(x)), x])
    beta, e, XtXi = ols(X, y)
    return float(beta[1]), math.sqrt(float(e @ e) / (len(y) - 2) * XtXi[1, 1])


def bootstrap_scan(y, X0, extra, cands, L, B, block, seed):
    """Stationary-bootstrap Wald paths under the restricted (no-break) model: X fixed, y* = X beta + e*, then the same HAC, trim and candidates."""
    base = X0 if extra is None else np.hstack([X0, extra])
    beta0, e0, _ = ols(base, y)
    rs = np.random.RandomState(seed)
    idx = stationary_idx(rs, len(y), B, block)
    Ystar = (base @ beta0)[None, :] + e0[idx]
    return scan(Ystar, X0, extra, cands, L)[0]


def run_b1(P, cfg, B=None, seed=SEED):
    """The break scan (descriptive, A1): 3 trims x {none, impulse dummy}. Returns (rows, detail)."""
    B = cfg["boot_B"] if B is None else B
    n, L = P.n, HAC_FLOOR
    X0, y = P.X(), P.dg
    lo_k, hi_k = cand_range(n, min(TRIMS))
    cands = list(range(lo_k, hi_k + 1))
    rows, detail = [], {}
    for spec in ("none", "imp_" + cfg["ci_dummy_month"].replace("-", "_")):
        extra = None if spec == "none" else P.impulse(cfg["ci_dummy_month"])[:, None]
        base = X0 if extra is None else np.hstack([X0, extra])
        W, S, D = scan(y, X0, extra, cands, L)
        Wb = bootstrap_scan(y, X0, extra, cands, L, B, cfg["boot_block"], seed)
        for pi in TRIMS:
            a, b_ = cand_range(n, pi)
            sel = slice(a - lo_k, b_ - lo_k + 1)
            sub = cands[sel]
            sup = float(W[0, sel].max())
            supb = Wb[:, sel].max(1)
            p = (1.0 + float((supb >= sup).sum())) / (B + 1.0)
            iS = pick_break_ssr(W[0, sel], S[0, sel], sub)
            iW = int(np.argmax(W[0, sel]))
            kS, kW = sub[iS], sub[iW]
            ci = sel.start + iS
            delta = D[0, ci]
            idx_ = np.arange(n)
            Xk = np.hstack([base, X0 * (idx_ >= kS)[:, None]])
            beta_k, e_k, _ = ols(Xk, y)
            Omega = nw_S(X0 * e_k[:, None], L) / n
            Q = X0.T @ X0 / n
            h = bai_halfwidth(delta, Omega, Q)
            lo_u, hi_u, lo_c, hi_c, clipped, width = bai_interval(kS, h, n, S[0, sel], sub)
            smin = [s_min(hh, Omega[1, 1], Q[1, 1]) for hh in S_MIN_H]
            v1 = float((e_k[:kS] ** 2).sum()) / kS
            v2 = float((e_k[kS:] ** 2).sum()) / (n - kS)
            ac = [andrews_cv(3, pi, j) for j in range(3)]
            row = dict(trim=f(pi, 2), dummy_spec=spec, first_candidate=P.cmonths[a - 1], last_candidate=P.cmonths[b_ - 1], n_candidates=len(sub),
                       sup_wald=f(sup, 3), p_value_boot=f(p, 3), boot_draws=B, boot_mean_block=cfg["boot_block"], andrews_cv10=f(ac[0], 2),
                       andrews_cv5=f(ac[1], 2), andrews_cv1=f(ac[2], 2), break_month_ssr=P.cmonths[kS - 1], break_month_supwald=P.cmonths[kW - 1],
                       bai_ci_low=P.cmonths[lo_c - 1], bai_ci_high=P.cmonths[hi_c - 1], bai_halfwidth_months=f(h, 1),
                       ci_clipped="yes" if clipped else "no", resid_var_regime1=f(v1, 6), resid_var_regime2=f(v2, 6), hac_lag=L)
            for hh, sm in zip(S_MIN_H, smin):
                row["s_min_h%d" % hh] = f(sm, 4)
            rows.append(row)
            detail[(pi, spec)] = dict(sup=sup, p=p, kS=kS, kW=kW, h=h, width=width, clipped=clipped, delta=delta, smin=smin, v=(v1, v2),
                                      unclipped=(P.cmonths[max(lo_u, 1) - 1] if lo_u >= 1 else "<start", hi_u),
                                      cv5=ac[1], n_cands=len(sub), lo_u=lo_u, hi_u=hi_u, s_actual=s_min(h, Omega[1, 1], Q[1, 1]),
                                      omega22=float(Omega[1, 1]), q22=float(Q[1, 1]))
    return rows, detail


def run_chow(P, cfg):
    rows = []
    y, X0 = P.dg, P.X()
    for m in cfg["chow"]:
        k = P.cmonths.index(m)
        W, _, _ = scan(y, X0, None, [k], HAC_FLOOR)
        w = float(W[0, 0])
        rows.append(dict(regime2_start=m, wald_hac=f(w, 3), df=3, p_chi2=f(chi2_sf3(w), 3), hac_lag=HAC_FLOOR, role="descriptive"))
    return rows


def run_rolling(P, cfg, B=None, seed=SEED):
    B = cfg["roll_B"] if B is None else B
    win, blk = cfg["roll_window"], cfg["block_roll"]
    e0 = P.cmonths.index(cfg["roll_first_end"])
    rs = np.random.RandomState(seed)
    X = P.X()
    rows = []
    for e in range(e0, P.n):
        sl = slice(e - win + 1, e + 1)
        Xw, yw = X[sl], P.dg[sl]
        beta = ols(Xw, yw)[0]
        idx = mbb_idx(rs, win, blk, B)
        Xb, yb = Xw[idx], yw[idx]
        XtX = np.matmul(Xb.transpose(0, 2, 1), Xb)
        Xty = np.matmul(Xb.transpose(0, 2, 1), yb[:, :, None])
        bb = np.linalg.solve(XtX, Xty)[:, 1, 0]
        lo, hi = np.percentile(bb, [2.5, 97.5])
        rows.append(dict(end_month=P.cmonths[e], n=win, beta_ry=f(beta[1], 4 if mut("g19_beta_4dp") else 2), boot_lo=f(lo, 2), boot_hi=f(hi, 2),
                         block_len=blk, draws=B, seed=seed))
    return rows


def gate_info(P, cfg):
    """The Engle-Granger gate runs on the fit sample (A4, G11). Returns (slice, first month, last month, T)."""
    if mut("g11_fullsample_gate"):
        sl, a, b = slice(None), P.months[0], P.months[-1]
    else:
        sl, a, b = P.lsl(cfg["first_level"], cfg["fit_end"]), cfg["first_level"], cfg["fit_end"]
    return sl, a, b, len(P.months[sl])


def levels_analysis(P, cfg):
    """D8: Engle-Granger test, then (only if it rejects) the levels objects. Returns (coint rows, levels rows, residual path or None, info)."""
    one = np.ones(len(P.months))
    Xl = np.column_stack([one, P.r, P.u])
    gsl, ga, gb, _ = gate_info(P, cfg)
    fsl = P.lsl(cfg["first_level"], cfg["fit_end"])
    full = slice(None)
    specs = [("EG_tauc_fit", "gate", gsl, ga, gb, False), ("EG_tauc_full", "info", full, P.months[0], P.months[-1], False),
             ("EG_tauct_fit", "info", fsl, cfg["first_level"], cfg["fit_end"], True),
             ("EG_tauct_full", "info", full, P.months[0], P.months[-1], True)]
    coint, gate_reject, ginfo = [], False, None
    for tid, role, sl, a, b, trend in specs:
        tau, p, T = eg_test(P.g[sl], Xl[sl], trend)
        cvv = mack_cv(T, trend)
        rej = tau < cvv
        if tid == "EG_tauc_fit":
            gate_reject, ginfo = rej, (tau, cvv, T, p)
        coint.append(dict(test_id=tid, role=role, sample_start=a, sample_end=b, T=T, adf_lags=p, adf_stat=f(tau, 4), cv_5pct=f(cvv, 4),
                          reject_5pct="yes" if rej else "no", levels_printed=""))
    for r in coint:
        r["levels_printed"] = ("yes" if gate_reject else "no") if r["role"] == "gate" else "n/a"
    names = [("D8_levels", cfg["first_level"], cfg["fit_end"], ["b_ry", "c_usd"]),
             ("D8_levels_trend", cfg["first_level"], cfg["fit_end"], ["b_ry", "c_usd", "trend"]),
             ("D8_levels_step", P.months[0], P.months[-1], ["b_ry", "c_usd", "step"]),
             ("D8_residual", cfg["first_level"], cfg["fit_end"], ["resid_last"])]
    lev, path = [], None
    suppressed = (not gate_reject) and not mut("g13_slope_regardless")
    compute = gate_reject or mut("g13_slope_regardless")
    out = {}
    if compute:
        T_fit = len(P.months[fsl])
        Xf, gf = Xl[fsl], P.g[fsl]
        bf, ef, _ = ols(Xf, gf)
        sd_in = math.sqrt(float(ef @ ef) / (T_fit - 3))
        Xt = np.column_stack([Xf, np.arange(T_fit, dtype=float)])
        step = np.array([1.0 if m >= cfg["seam_month"] else 0.0 for m in P.months])
        Xs = np.column_stack([Xl, step])
        fits = {"D8_levels": (fit(gf, Xf, HAC_FLOOR), ["b_ry", "c_usd"], [1, 2], T_fit),
                "D8_levels_trend": (fit(gf, Xt, HAC_FLOOR), ["b_ry", "c_usd", "trend"], [1, 2, 3], T_fit),
                "D8_levels_step": (fit(P.g, Xs, HAC_FLOOR), ["b_ry", "c_usd", "step"], [1, 2, 3], len(P.months))}
        res_last = float(P.g[-1] - Xl[-1] @ bf)
        label = "high" if res_last > 2 * sd_in else ("not_high" if abs(res_last) < sd_in else "inconclusive")
        path = [(m, float(P.g[i] - Xl[i] @ bf), float((P.g[i] - Xl[i] @ bf) / sd_in)) for i, m in enumerate(P.months)]
        out = dict(fits=fits, sd_in=sd_in, label=label, res_last=res_last)
    for oid, a, b, cn in names:
        if oid == "D8_residual":
            if compute:
                lev.append(dict(object_id=oid, fit_start=a, fit_end=b, coef_name="residual_label", coef="", ci_low="", ci_high="", hac_lag="",
                                resid_sd_in_sample=f(out["sd_in"], 4), residual_label=out["label"], status="reported"))
            else:
                lev.append(dict(object_id=oid, fit_start=a, fit_end=b, coef_name="residual_label", coef="", ci_low="", ci_high="", hac_lag="",
                                resid_sd_in_sample="", residual_label="", status="suppressed_no_cointegration"))
            continue
        for j, nm in enumerate(cn):
            if compute:
                fp, _, ix, T = out["fits"][oid]
                c, se = float(fp["beta"][ix[j]]), float(fp["se_hac"][ix[j]])
                cvv = round(kv_cubic(HAC_FLOOR / float(T)), 3)
                lev.append(dict(object_id=oid, fit_start=a, fit_end=b, coef_name=nm, coef=f(c, 4), ci_low=f(c - cvv * se, 4), ci_high=f(c + cvv * se, 4),
                                hac_lag=HAC_FLOOR, resid_sd_in_sample="", residual_label="", status="reported"))
            else:
                lev.append(dict(object_id=oid, fit_start=a, fit_end=b, coef_name=nm, coef="", ci_low="", ci_high="", hac_lag="",
                                resid_sd_in_sample="", residual_label="", status="suppressed_no_cointegration"))
    info = dict(gate_reject=gate_reject, gate=ginfo, out=out, suppressed=suppressed)
    return coint, lev, path, info


def checksums_d9(P, daily):
    """D9 reproduction checks (official yields): 2026 levels slope over 9 months, 2026 changes slope over 8 months, quarterly levels slope over
    2025Q1-2026Q3 (gold = log of the equal-weight quarterly mean; yield = mean of the daily prints in the quarter)."""
    m26 = [m for m in P.months if m.startswith("2026-")]
    i0 = P.months.index(m26[0])
    s1, _ = simple_slope(P.r_off[i0:i0 + len(m26)], P.g[i0:i0 + len(m26)])
    c0 = P.cmonths.index("2026-02")
    s2, _ = simple_slope(P.dr_off[c0:], P.dg[c0:])
    gq, rq = [], []
    for y in (2025, 2026):
        for q in range(1, 5):
            ms = ["%04d-%02d" % (y, 3 * (q - 1) + k) for k in (1, 2, 3)]
            if not all(m in P.gold_raw and m <= P.end for m in ms):
                continue
            gq.append(math.log(sum(P.gold_raw[m] for m in ms) / 3.0))
            vals = [v for d, v in daily if (d.year, (d.month - 1) // 3 + 1) == (y, q)]
            rq.append(sum(vals) / len(vals))
    s3, _ = simple_slope(np.array(rq), np.array(gq))
    return s1, s2, s3, len(gq)


# ----------------------------------------------------------------------------------------------------------------------------------
# the cache: vintages, loading, revision report
# ----------------------------------------------------------------------------------------------------------------------------------
FID_SRC = {"D1": "worldbank", "D2": "treasury", "D4": "treasury", "D5": "fed", "D6": "fed"}
VN_RX = re.compile(r"(D[1-6](?:-\d{4})?)_(\d{8})_([0-9a-f]{8})\.(xlsx|csv)")


def fid_source(fid):
    return FID_SRC.get(fid, "treasury")


def vint_name(fid, date_s, sha):
    ext = "xlsx" if fid == "D1" else "csv"
    return "%s_%s_%s.%s" % (fid, date_s.replace("-", ""), sha[:8], ext)


def list_vintages(cache):
    out = []
    base = os.path.join(cache, "vintages")
    if not os.path.isdir(base):
        return out
    for src in sorted(os.listdir(base)):
        d = os.path.join(base, src)
        if not os.path.isdir(d):
            continue
        for nm in sorted(os.listdir(d)):
            m = VN_RX.fullmatch(nm)
            if m:
                ds = m.group(2)
                out.append(dict(fid=m.group(1), source=src, path=os.path.join(d, nm), name=nm, date="%s-%s-%s" % (ds[:4], ds[4:6], ds[6:]),
                                sha8=m.group(3)))
    return out


def latest_of(vs, fid, nth=0):
    c = sorted((v for v in vs if v["fid"] == fid), key=lambda v: (v["date"], v["name"]), reverse=True)
    return c[nth] if len(c) > nth else None


def read_bytes(path):
    with open(path, "rb") as fh:
        return fh.read()


def check_cache(cache):
    real = os.path.realpath(os.path.expanduser(cache))
    root = os.path.realpath(ROOT)
    if not mut("g23_accept_repo_cache") and (real == root or real.startswith(root + os.sep)):
        raise Refused("the cache must be outside the repository (the World Bank workbook is never committed)")
    return real


def revision_lines(old, new, label, tol, relative):
    """Largest revision over the months two vintages share; WARN above tol."""
    shared = sorted(set(old) & set(new))
    if not shared:
        return ["%s: no shared months between the two vintages" % label], False
    if relative:
        d = max((abs(new[m] / old[m] - 1.0), m) for m in shared)
    else:
        d = max((abs(new[m] - old[m]), m) for m in shared)
    warn = d[0] > tol
    return ["%s revision: largest over %d shared months is %s at %s%s" % (label, len(shared), ("%.4f%%" % (100 * d[0])) if relative else "%.5f" % d[0], d[1],
                                                                          "  WARN" if warn else "  ok")], warn


def load_inputs(cache, cfg):
    vs = list_vintages(cache)
    need = ["D1", "D2", "D4", "D5", "D6"] + ["D3-%d" % y for y in range(2024, int(cfg["end"][:4]) + 1)]
    pick = {}
    for fid in need:
        v = latest_of(vs, fid)
        if v is None:
            raise DataError("%s is not in the cache %s; run `fetch` first" % (fid, tilde(cache)))
        pick[fid] = v
    raw = {fid: read_bytes(v["path"]) for fid, v in pick.items()}
    gold, upd, last = parse_gold(raw["D1"])
    daily = parse_treasury(raw["D2"])
    for fid in need:
        if fid.startswith("D3-"):
            daily += parse_treasury(raw[fid])
    seen = set()
    for d, _ in daily:
        if d in seen:
            raise DataError("duplicate Treasury date %s across the files" % d)
        seen.add(d)
    daily.sort()
    gap, nd4 = parse_d4(raw["D4"])
    label, usd = parse_fed(raw["D5"], FED_IDS["D5"], base_month=cfg["first_level"], monthly=True)
    _, usd_d = parse_fed(raw["D6"], FED_IDS["D6"], monthly=False)
    tips_m = monthly_tips(daily, gap, cfg["seam_date"])
    rev, warns = [], []
    for fid, parser in (("D1", lambda b: parse_gold(b)[0]), ("D5", lambda b: parse_fed(b, FED_IDS["D5"], monthly=False)[1])):
        prev = latest_of(vs, fid, 1)
        if prev is not None and prev["sha8"] != pick[fid]["sha8"]:
            old, new = parser(read_bytes(prev["path"])), (gold if fid == "D1" else usd)
            lines, w = revision_lines(old, new, "gold column" if fid == "D1" else "dollar index", 0.005 if fid == "D1" else 0.0005, fid == "D1")
            rev += lines
            warns.append(w)
    retrieved = {"wb": pick["D1"]["date"], "fed": pick["D5"]["date"],
                 "tr": max(v["date"] for fid, v in pick.items() if fid_source(fid) == "treasury")}
    return dict(gold=gold, gold_updated=upd, gold_last=last, gold_sha=sha256_of(raw["D1"]), gold_bytes=len(raw["D1"]), daily=daily, d4_gap=gap, d4_n=nd4,
                tips_m=tips_m, usd=usd, usd_label=label, usd_daily=usd_d, retrieved=retrieved, revisions=rev, rev_warn=any(warns), vintages=vs, cache=cache)


def vintage_rows(inputs, cache, out_dir):
    log = read_table(os.path.join(out_dir, "fetch_log.csv"), LOG_COLS)
    by_sha = {r[5]: r[0] for r in log if r[6] == "saved"}
    rows = []
    for v in inputs["vintages"]:
        raw = read_bytes(v["path"])
        sha = sha256_of(raw)
        upd, last = "", ""
        if v["fid"] == "D1":
            g, upd, last_m = parse_gold(raw)
            last = last_m
        elif v["fid"] in ("D5", "D6"):
            _, d = parse_fed(raw, FED_IDS[v["fid"]], monthly=False)
            last = max(d)
        elif v["fid"] != "D4":
            last = max(parse_treasury(raw))[0].isoformat()
        rows.append([v["source"], v["name"], by_sha.get(sha, v["date"]), sha, len(raw), upd, last])
    rows.sort()
    return rows


# ----------------------------------------------------------------------------------------------------------------------------------
# the analysis driver
# ----------------------------------------------------------------------------------------------------------------------------------
def analyse(P, cfg, inputs):
    A = {}
    n = P.n
    X, y = P.X(), P.dg
    L = hac_lag(n)
    rows = []
    r1, fp = coef_rows("P1", "confirmatory", P.cmonths[0], P.cmonths[-1], y, X, ["a_const", "b_ry", "c_usd"], regressors_text(REG_NAMES.split(";")), L=L)
    rows += r1
    A["p1_fit"], A["p1_L"], A["p1_cv"] = fp, L, p1_cv(n, L)
    b, se = float(fp["beta"][1]), float(fp["se_hac"][1])
    A["p1"] = dict(b=b, se=se, lo=b - A["p1_cv"] * se, hi=b + A["p1_cv"] * se, cls=float(fp["se_cls"][1]), c=float(fp["beta"][2]),
                   c_se=float(fp["se_hac"][2]), verdict=r1[1]["verdict"], mde=(A["p1_cv"] + Z80) * se, r2=fp["r2"], n=n, rule=rule_lag(n))
    d1, _ = coef_rows("D1", "descriptive", P.cmonths[0], P.cmonths[-1], y, X[:, :2], ["a_const", "b_ry"], "const;d_ry")
    rows += d1
    off = P.dcmonths.index(P.cmonths[0]) if P.cmonths[0] in P.dcmonths else 0
    yl = P.dg_long
    Xl2 = np.column_stack([np.ones(len(yl)), P.dr_long])
    d2, _ = coef_rows("D2", "descriptive", P.dcmonths[0], P.dcmonths[-1], yl, Xl2, ["a_const", "b_ry"], "const;d_ry", flag="no_dollar_longer_sample")
    rows += d2
    d3, _ = coef_rows("D3", "descriptive", P.cmonths[0], P.cmonths[-1], y, P.X(r="official"), ["a_const", "b_ry", "c_usd"], REG_NAMES, flag="unadjusted_official_yields")
    rows += d3
    imp = [(m, nm) for m, nm in cfg["impulse"]]
    Xd = np.column_stack([X] + [P.impulse(m) for m, _ in imp])
    d4, _ = coef_rows("D4", "descriptive", P.cmonths[0], P.cmonths[-1], y, Xd, ["a_const", "b_ry", "c_usd"] + [nm for _, nm in imp],
                      REG_NAMES + ";" + ";".join(nm for _, nm in imp), flag="impulse_dummies")
    rows += d4
    for a, b_ in cfg["subperiods"]:
        sl = P.csl(a, b_)
        nw = len(y[sl])
        d5, _ = coef_rows("D5", "descriptive", a, b_, y[sl], X[sl], ["a_const", "b_ry", "c_usd"], REG_NAMES, flag="short_window" if nw < 100 else "")
        rows += d5
    if cfg["live"]:
        s1, s2, s3, nq = checksums_d9(P, inputs["daily"])
        A["d9"] = (s1, s2, s3, nq)
        for nm, s, nobs in (("b_levels_2026_9m", s1, 9), ("b_changes_2026_8m", s2, 8), ("b_levels_quarterly_7q", s3, nq)):
            rows.append(dict(object_id="D9", role="descriptive", sample_start="", sample_end="", n=nobs, regressors="const;yield", coef_name=nm, coef=f(s, 4),
                             coef_unit="log points per pp (reproduction check)", pct_approx="", pct_exact="", se_classical="", se_hac="", hac_lag="",
                             hac_lag_rule="", crit_value="", crit_basis="", ci_level="", ci_low="", ci_high="", r2="", mde80="", flag="checksum", verdict=""))
    if mut("g21_D10"):
        rows.append(dict(rows[0], object_id="D10"))
    A["results"] = rows
    A["b1_rows"], A["b1"] = run_b1(P, cfg)
    A["chow"] = run_chow(P, cfg)
    A["roll"] = run_rolling(P, cfg)
    A["coint"], A["levels"], A["path"], A["linfo"] = levels_analysis(P, cfg)
    return A


def band_problems(rows):
    """Every results.csv row: ci_low and ci_high equal coef -/+ crit_value x se_hac, up to the rounding of the printed cells (each cell is
    rounded to 4 dp, so the allowed gap is 0.00005 x (2 + crit))."""
    bad = []
    for r in rows:
        if r.get("ci_low", "") == "" or r.get("se_hac", "") == "" or r.get("crit_value", "") == "":
            continue
        c, se, cv = float(r["coef"]), float(r["se_hac"]), float(r["crit_value"])
        tol = 5e-5 * (2.0 + cv) + 1e-9
        if abs(float(r["ci_low"]) - (c - cv * se)) > tol or abs(float(r["ci_high"]) - (c + cv * se)) > tol:
            bad.append("%s %s %s..%s: band [%s, %s] is not %s -/+ %s x %s" % (r["object_id"], r["coef_name"], r["sample_start"], r["sample_end"],
                                                                         r["ci_low"], r["ci_high"], r["coef"], r["crit_value"], r["se_hac"]))
    return bad


def stdout_band_problems(lines, rows):
    """The P1 band on the printed report equals the P1 b_ry band in results.csv."""
    row = [x for x in rows if x["object_id"] == "P1" and x["coef_name"] == "b_ry"][0]
    want = "[%s, %s]" % (row["ci_low"], row["ci_high"])
    got = [ln for ln in lines if "fixed-b interval" in ln]
    if not got or want not in got[0]:
        return ["stdout P1 band %r is not results.csv's %s" % (got[0].strip() if got else "(missing)", want)]
    return []


def validate_ids(A):
    bad = sorted({r["object_id"] for r in A["results"]} - set(REGISTRY))
    bad += sorted({r["object_id"].split("_")[0] for r in A["levels"]} - set(REGISTRY))
    if bad:
        raise DataError("object id(s) outside the registry: " + ", ".join(bad))


def inputs_rows(P, cfg, inputs):
    rows = []
    flags = {cfg["knot_month"]: "tips_knot_change", cfg["seam_month"]: "hs_to_mc_spline", cfg["gold_def_month"]: "pink_sheet_series_definition"}
    for m in P.dmonths:
        t = inputs["tips_m"][m]
        rows.append([m, f(t["mc"], 4), f(t["off"], 4), t["days"], f(t["mc_days"] / float(t["days"]), 4), f(inputs["usd"][m], 4) if m in inputs["usd"] else "",
                     flags.get(m, "")])
    return rows


def rolling_svg(rows, block, draws, seed):
    W, H, ml, mr, mt, mb = 900, 430, 62, 20, 24, 96
    xs = [i for i in range(len(rows))]
    vals = [float(r["beta_ry"]) for r in rows] + [float(r["boot_lo"]) for r in rows] + [float(r["boot_hi"]) for r in rows]
    lo, hi = math.floor(min(vals + [0.0]) * 10) / 10.0 - 0.1, math.ceil(max(vals + [0.0]) * 10) / 10.0 + 0.1
    X = lambda i: ml + (W - ml - mr) * i / max(1, len(rows) - 1)
    Y = lambda v: mt + (H - mt - mb) * (hi - v) / (hi - lo)
    out = ['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 %d %d" width="%d" height="%d" role="img" aria-label="Rolling 36-month slope of the monthly '
           'change in the price of gold on the monthly change in the 10-year real yield, with a bootstrap band">' % (W, H, W, H),
           '<title>Rolling 36-month slope, monthly changes, dollar held fixed</title>',
           '<rect width="%d" height="%d" fill="#ffffff"/>' % (W, H)]
    t = lo
    while t <= hi + 1e-9:
        out.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#e5e5e5"/>' % (ml, Y(t), W - mr, Y(t)))
        out.append('<text x="%d" y="%.1f" font-family="sans-serif" font-size="11" fill="#444444" text-anchor="end">%s</text>' % (ml - 6, Y(t) + 4, f(t, 1)))
        t += 0.1 if hi - lo <= 1.5 else 0.2
    pts_hi = " ".join("%.1f,%.1f" % (X(i), Y(float(r["boot_hi"]))) for i, r in enumerate(rows))
    pts_lo = " ".join("%.1f,%.1f" % (X(i), Y(float(r["boot_lo"]))) for i, r in reversed(list(enumerate(rows))))
    out.append('<polygon points="%s %s" fill="#9ecae1" fill-opacity="0.55" stroke="none"/>' % (pts_hi, pts_lo))
    out.append('<line x1="%d" y1="%.1f" x2="%d" y2="%.1f" stroke="#222222" stroke-width="1.2"/>' % (ml, Y(0), W - mr, Y(0)))
    out.append('<polyline points="%s" fill="none" stroke="#08519c" stroke-width="1.8"/>' % " ".join("%.1f,%.1f" % (X(i), Y(float(r["beta_ry"]))) for i, r in enumerate(rows)))
    last_year = None
    for i, r in enumerate(rows):
        yr, mo = r["end_month"][:4], r["end_month"][5:]
        if mo == "01" and int(yr) % 2 == 1:
            out.append('<line x1="%.1f" y1="%d" x2="%.1f" y2="%d" stroke="#888888"/>' % (X(i), H - mb, X(i), H - mb + 4))
            out.append('<text x="%.1f" y="%d" font-family="sans-serif" font-size="11" fill="#444444" text-anchor="middle">%s</text>' % (X(i), H - mb + 17, yr))
    out.append('<text x="14" y="%d" font-family="sans-serif" font-size="11" fill="#444444" transform="rotate(-90 14 %d)" text-anchor="middle">log points per pp of real yield</text>'
               % ((mt + H - mb) // 2, (mt + H - mb) // 2))
    cap = ["Rolling 36-month slope of gold's monthly change on the 10-year real-yield change, dollar held fixed (window end month on the axis).",
           "Band: moving-block bootstrap, block length %d months, %d draws, seed %d, percentile 2.5 to 97.5. Overlapping windows; not a count of tests." % (block, draws, seed),
           "Values at 2 decimals. Sources: World Bank Pink Sheet (derived), US Treasury, Federal Reserve Board."]
    for j, c in enumerate(cap):
        out.append('<text x="%d" y="%d" font-family="sans-serif" font-size="11.5" fill="#222222">%s</text>' % (ml, H - mb + 40 + 16 * j, c.replace("&", "&amp;")))
    out.append("</svg>")
    return "\n".join(out) + "\n"


def stamp_free(text):
    return text


def write_outputs(P, cfg, inputs, A, out_dir, local_dir, cache):
    """Writes every committed file except checks.csv (written by the caller after K08). Returns the paths."""
    validate_ids(A)
    ret = inputs["retrieved"]
    tabs = {
        "monthly_inputs.csv": (INPUTS_COLS, inputs_rows(P, cfg, inputs)),
        "results.csv": (RESULTS_COLS, [[r[c] for c in RESULTS_COLS] for r in A["results"]]),
        "cointegration.csv": (COINT_COLS, [[r[c] for c in COINT_COLS] for r in A["coint"]]),
        "break.csv": (BREAK_COLS, [[r[c] for c in BREAK_COLS] for r in A["b1_rows"]]),
        "chow_known_dates.csv": (CHOW_COLS, [[r[c] for c in CHOW_COLS] for r in A["chow"]]),
        "rolling36.csv": (ROLL_COLS, [[r[c] for c in ROLL_COLS] for r in A["roll"]]),
        "levels_summary.csv": (LEVELS_COLS, [[r[c] for c in LEVELS_COLS] for r in A["levels"]]),
        "vintages.csv": (VINT_COLS, vintage_rows(inputs, cache, out_dir) if inputs.get("vintages") is not None else []),
    }
    if mut("g18_add_ln_gold"):
        h, r = tabs["results.csv"]
        tabs["results.csv"] = (h + ["ln_gold"], [x + ["0"] for x in r])
    if mut("g18_add_n_excl_zero"):
        h, r = tabs["rolling36.csv"]
        tabs["rolling36.csv"] = (h + ["n_excl_zero"], [x + ["0"] for x in r])
    if mut("g18_add_resid_last"):
        h, r = tabs["levels_summary.csv"]
        tabs["levels_summary.csv"] = (h + ["resid_last_sd_units"], [x + ["0"] for x in r])
    paths = []
    for nm, (h, rows) in tabs.items():
        text = render_table(h, rows, source_line(nm, ret))
        verify_text(nm, text)
        write_text(os.path.join(out_dir, nm), text)
        paths.append(nm)
    rr = A["roll"]
    write_text(os.path.join(out_dir, "rolling36.svg"), rolling_svg(rr, cfg["block_roll"], cfg["roll_B"], SEED))
    # local-only outputs (R1): the monthly panel with gold, and the residual path
    ldir = out_dir if mut("g19_residual_path_in_repo") else local_dir
    os.makedirs(ldir, exist_ok=True)
    with open(os.path.join(ldir, "local_panel.csv"), "w", encoding="utf-8", newline="") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["month", "gold_usd_per_oz", "ln_gold", "tips10_mc", "tips10_official", "ln_usd"])
        for i, m in enumerate(P.months):
            w.writerow([m, "%.4f" % P.gold_raw[m], "%.6f" % P.g[i], "%.6f" % P.r[i], "%.6f" % P.r_off[i], "%.6f" % P.u[i]])
    if A["path"] is not None:
        with open(os.path.join(ldir, "local_levels_residual_path.csv"), "w", encoding="utf-8", newline="") as fh:
            w = csv.writer(fh, lineterminator="\n")
            w.writerow(["month", "fit_residual_log_points", "fit_residual_sd_units"])
            for m, e, z in A["path"]:
                w.writerow([m, "%.6f" % e, "%.4f" % z])
    return paths


# ----------------------------------------------------------------------------------------------------------------------------------
# live cross-checks K01-K09 (real data only)
# ----------------------------------------------------------------------------------------------------------------------------------
GOLD_SHA = "c1ccb724d521450de7c283063c82ff619e40e94dc0b063738b8529f018a2798e"
SPEC_TRIMS = [(0.05, "2007-02", "2025-08"), (0.15, "2009-03", "2023-07"), (0.25, "2011-03", "2021-07")]


def ck(cid, desc, expected, observed, status):
    return dict(check_id=cid, description=desc, expected=str(expected), observed=str(observed), status=status)


def status_of(cond, bad="FAIL"):
    return "PASS" if cond else bad


def gld_cross_check(P, cfg):
    p = os.path.join(ROOT, "data", "vintages", "gold", "spdr_gld_archive.xlsx")
    if not os.path.exists(p):
        return ck("K07", "Gold series seam at 2025-06 against the GLD-implied PM price (local only)", "median gap before 2025-06 <= 0.10%",
                  "file absent: SKIP (expected for an outside reader)", "SKIP")
    try:
        import importlib.util
        sp = importlib.util.spec_from_file_location("build_gold_ledger", os.path.join(ROOT, "bin", "build_gold_ledger.py"))
        mod = importlib.util.module_from_spec(sp)
        sp.loader.exec_module(mod)
        gld = mod.parse_gld()
        acc = {}
        for d, v in gld.items():
            acc.setdefault(d[:7], []).append(v["price"])
        gaps = {m: math.log(sum(v) / len(v)) - math.log(P.gold_raw[m]) for m, v in acc.items() if m in P.gold_raw and m >= cfg["first_level"] and m <= P.end}
        pre = [abs(g) for m, g in gaps.items() if m < cfg["gold_def_month"]]
        a_pre = [g for m, g in gaps.items() if m < cfg["gold_def_month"]]
        a_post = [g for m, g in gaps.items() if m >= cfg["gold_def_month"]]
        med = sorted(pre)[len(pre) // 2] if pre else float("nan")
        post = sorted(abs(g) for g in a_post)
        medp = post[len(post) // 2] if post else float("nan")
        chg = (sum(a_post) / len(a_post) - sum(a_pre) / len(a_pre)) if a_post and a_pre else float("nan")
        return ck("K07", "Gold series seam at 2025-06 against the GLD-implied PM price (local only; gap statistics only)", "median absolute gap before 2025-06 <= 0.10%",
                  "median abs gap before %.3f%%, after %.3f%%; change in mean gap at the seam %+.3f%%" % (100 * med, 100 * medp, 100 * chg), "PASS" if med <= 0.0010 else "WARN")
    except Exception as e:                                                                   # a local-only check never stops the build
        return ck("K07", "Gold series seam at 2025-06 against the GLD-implied PM price (local only)", "median gap <= 0.10%", "could not run: %s" % type(e).__name__, "SKIP")


def live_checks(P, cfg, inputs, A):
    c = []
    daily = inputs["daily"]
    gold = inputs["gold"]
    # K01
    mlist = month_range(cfg["first_level"], cfg["end"])
    blank = [m for m in mlist if m not in gold]
    lines = "".join("%sM%s,%.4f\n" % (m[:4], m[5:], gold[m]) for m in mlist if m in gold)
    sha = sha256_of(lines.encode())
    c.append(ck("K01a", "Gold header and ($/troy oz) units sit in the same column", "same column", "same column (parse_gold)", "PASS"))
    c.append(ck("K01b", "Gold months 2006M01 to 2026M09, no blanks", "249 months, 0 blank", "%d months, %d blank" % (len(mlist) - len(blank), len(blank)),
                status_of(len(mlist) == 249 and not blank)))
    same = inputs["gold_updated"] == "October 02, 2026"
    c.append(ck("K01c", "sha256 of the gold column lines (2 Oct 2026 vintage)", GOLD_SHA, sha, "PASS" if sha == GOLD_SHA else ("FAIL" if same else "WARN")))
    # K02
    upto = [(d, v) for d, v in daily if d <= dt.date(2026, 9, 30)]
    c.append(ck("K02a", "Treasury 10 YR prints, 2003-01-02 to 2026-09-30, no duplicates or blanks", "5941 prints, 2003-01-02, 2026-09-30",
                "%d prints, %s, %s" % (len(upto), upto[0][0], upto[-1][0]), status_of(len(upto) == 5941 and upto[0][0] == dt.date(2003, 1, 2) and upto[-1][0] == dt.date(2026, 9, 30))))
    t = inputs["tips_m"]
    s9 = t["2026-09"]
    c.append(ck("K02b", "September 2026 (official): days, sum, mean", "21 days, sum 55.40, mean 2.6381",
                "%d days, sum %.2f, mean %.4f" % (s9["days"], s9["sum_off"], s9["off"]), status_of(s9["days"] == 21 and abs(s9["sum_off"] - 55.40) < 0.005 and abs(s9["off"] - 2.6381) < 5e-5)))
    j6 = t["2006-01"]
    c.append(ck("K02c", "January 2006: days, sum", "20 days, sum 40.12", "%d days, sum %.2f" % (j6["days"], j6["sum_off"]), status_of(j6["days"] == 20 and abs(j6["sum_off"] - 40.12) < 0.005)))
    dec = [(d, v) for d, v in daily if (d.year, d.month) == (2021, 12)]
    pre3 = [v for d, v in sorted(dec, reverse=True) if d < dt.date(2021, 12, 6)]          # the spec lists them in the file's order, newest first
    c.append(ck("K02d", "December 2021: days, and the three prints before 6 Dec (newest first, as the file lists them)", "22 days; -1.08, -1.03, -1.01",
                "%d days; %s" % (len(dec), ", ".join("%.2f" % v for v in pre3)),
                status_of(len(dec) == 22 and [round(v, 2) for v in pre3] == [-1.08, -1.03, -1.01])))
    dd = dict(daily)
    c.append(ck("K02e", "Spot prints 2023-12-29 and 2026-09-30", "1.72, 2.93", "%.2f, %.2f" % (dd[dt.date(2023, 12, 29)], dd[dt.date(2026, 9, 30)]),
                status_of(abs(dd[dt.date(2023, 12, 29)] - 1.72) < 1e-9 and abs(dd[dt.date(2026, 9, 30)] - 2.93) < 1e-9)))
    # K03
    gap = inputs["d4_gap"]
    c.append(ck("K03a", "Treasury overlap file: mean MC minus HS over the overlap days (pp)", "0.026614 over 251 days", "%.6f over %d days" % (gap, inputs["d4_n"]),
                status_of(abs(gap - 0.026614) < 5e-7 and inputs["d4_n"] == 251)))
    d21 = t["2021-12"]
    c.append(ck("K03b", "December 2021 mean: MC basis and official", "-0.9896; -0.9932", "%.4f; %.4f" % (d21["mc"], d21["off"]), status_of(abs(d21["mc"] + 0.9896) < 5e-5 and abs(d21["off"] + 0.9932) < 5e-5)))
    c.append(ck("K03c", "January 2006 mean, MC basis", "2.0326", "%.4f" % j6["mc"], status_of(abs(j6["mc"] - 2.0326) < 5e-5)))
    # K04
    u = inputs["usd"]
    want = {"2006-01": 100.0, "2021-12": 115.8045, "2025-12": 120.1883, "2026-09": 119.2152}
    c.append(ck("K04a", "Broad dollar index (2006-01=100): 2006-01, 2021-12, 2025-12, 2026-09", "100.0000 / 115.8045 / 120.1883 / 119.2152",
                " / ".join("%.4f" % u[m] for m in want), status_of(all(abs(u[m] - w) < 5e-5 for m, w in want.items()))))
    dsum = {}
    for d, v in inputs["usd_daily"].items():
        a = dsum.setdefault(d[:7], [0.0, 0])
        a[0] += v
        a[1] += 1
    worst = max((abs(u[m] - dsum[m][0] / dsum[m][1]), m) for m in u if m in dsum and m <= cfg["end"])
    c.append(ck("K04b", "Monthly index equals the mean of the month's daily values", "within 0.0001 in every month", "largest gap %.5f at %s" % worst, "PASS" if worst[0] <= 1.0e-4 else "WARN"))
    c.append(ck("K04c", "The Unit: label in the Fed file is not trusted; the base is asserted from the value", "label says a 1997 base; values are 2006-01 = 100",
                "label %r" % inputs["usd_label"], "INFO"))
    # K05
    s1, s2, s3, nq = A["d9"]
    for cid, nm, s, w in (("K05a", "2026 levels slope over 9 months", s1, -0.20199), ("K05b", "2026 changes slope over 8 months", s2, -0.31907),
                          ("K05c", "levels slope over the 7 quarters 2025Q1-2026Q3 (log of the equal-weight quarterly mean)", s3, -0.02101)):
        c.append(ck(cid, nm + " (official yields; a published checksum)", "%.5f +- 0.00005" % w, "%.5f" % s, status_of(abs(s - w) <= 5e-5)))
    c.append(ck("K05d", "Number of quarters in the quarterly checksum", "7", str(nq), status_of(nq == 7)))
    # K06
    tt = trim_table(P.cmonths)
    okt = all(abs(a - b[0]) < 1e-12 and x == b[1] and y_ == b[2] for (a, x, y_), b in zip(tt, SPEC_TRIMS))
    c.append(ck("K06", "Sample and lags: n changes, rule-of-thumb lag, L; trim table as the spec", "n=248, rule 4, L=12; 2007-02/2025-08, 2009-03/2023-07, 2011-03/2021-07",
                "n=%d, rule %d, L=%d; %s" % (P.n, rule_lag(P.n), hac_lag(P.n), ", ".join("%s/%s" % (x, y_) for _, x, y_ in tt)),
                status_of(P.n == 248 and rule_lag(P.n) == 4 and hac_lag(P.n) == 12 and okt)))
    c.append(gld_cross_check(P, cfg))
    # K09
    rs = np.random.RandomState(SEED)
    iid, ar = sim_noise(rs, cfg["sd_draws"], P.n)
    s_iid, s_ar = null_size(P.X(), iid, ar, HAC_FLOOR, A["p1_cv"])
    A["k09"] = (s_iid, s_ar)
    c.append(ck("K09", "P1 null size on the real regressors (%d synthetic iid and AR(0.2) y; no gold), rejection rate at the fixed-b cv" % cfg["sd_draws"], "each <= 0.065",
                "iid %.4f, AR(0.2) %.4f" % (s_iid, s_ar), status_of(max(s_iid, s_ar) <= 0.065)))
    if inputs["revisions"]:
        c.append(ck("I01", "Revision report against the previous vintage", "no revision above 0.5% (gold) or 0.0005 (dollar)", " | ".join(inputs["revisions"]), "WARN" if inputs["rev_warn"] else "PASS"))
    v1, v2 = [float(r["resid_var_regime1"]) for r in A["b1_rows"][1:2]] + [float(r["resid_var_regime2"]) for r in A["b1_rows"][1:2]]
    ratio = max(v1, v2) / min(v1, v2) if min(v1, v2) > 0 else float("inf")
    c.append(ck("I02", "B1 at trim 0.15: regime residual variances (the Bai interval is labelled approximate if they differ by more than 2x)", "ratio <= 2",
                "ratio %.2f" % ratio, "INFO" if ratio <= 2 else "WARN"))
    return c


def k08(out_dir, extra_ok=True):
    probs = leak_scan(out_dir)
    return ck("K08", "Leak scan: explicit file and column allowlist; rolling36.csv at most 2 decimals; no spreadsheet under the output directory",
              "no problems", "; ".join(probs) if probs else "no problems", "FAIL" if probs else "PASS")


def finish(out_dir, checks, retrieved):
    """Writes checks.csv with K08 evaluated on the directory as it stands, then re-verifies the final directory."""
    rows = [c for c in checks if c["check_id"] != "K08"]
    kk = k08(out_dir)
    rows.append(kk)
    rows.sort(key=lambda r: r["check_id"])
    text = render_table(CHECKS_COLS, [[r[c] for c in CHECKS_COLS] for r in rows], source_line("checks.csv", retrieved))
    verify_text("checks.csv", text)
    write_text(os.path.join(out_dir, "checks.csv"), text)
    final = leak_scan(out_dir)
    return rows, final


# ----------------------------------------------------------------------------------------------------------------------------------
# fetching: the only network code. One request at a time, paced, GET only, STOP latch (R3, R4)
# ----------------------------------------------------------------------------------------------------------------------------------
def check_target(host, target):
    """Host allowlist plus exact paths (G25). Returns nothing or raises Refused."""
    hosts = HOSTS + (("fred.stlouisfed.org",) if mut("g25_fred_allowed") else ())
    h = (host or "").lower()
    if h not in hosts:
        raise Refused("host %s is not on the allowlist (%s)" % (host, ", ".join(HOSTS)))
    if h == "fred.stlouisfed.org":
        return
    ok = ((h == WB_HOST and WB_RX.fullmatch(target)) or (h == TR_HOST and (target in (D2_PATH, D4_PATH) or D3_RX.fullmatch(target)))
          or (h == FED_HOST and target in (D5_PATH, D6_PATH)))
    if not ok:
        raise Refused("path outside the files the spec names: %s%s" % (host, target[:80]))


def real_opener(host, target, headers, timeout, cap):
    """GET https://host/target. Returns (status, body); body is None when it exceeds `cap`. No redirect is followed (a 3xx comes back as a status
    and latches), no cookies, the only verb is GET. Socket-level faults raise SocketFault."""
    conn = http.client.HTTPSConnection(host, timeout=timeout)
    try:
        conn.request("GET", target, headers=dict(headers))
        resp = conn.getresponse()
        status = resp.status
        if status != 200:
            return status, b""
        chunks, total = [], 0
        while True:
            b = resp.read(1 << 16)
            if not b:
                break
            total += len(b)
            if total > cap:
                return status, None
            chunks.append(b)
        return status, b"".join(chunks)
    except (OSError, http.client.HTTPException) as e:
        raise SocketFault(type(e).__name__)
    finally:
        conn.close()


def body_problem_xlsx(body):
    try:
        parse_gold(body)
    except Exception as e:                                       # any failure of the content test is a refused body
        return "World Bank body failed its content test (%s)" % type(e).__name__
    return None


def body_problem_treasury(body):
    try:
        rd = csv.reader(io.StringIO(body.decode("utf-8-sig")))
        header = next(r for r in rd if r and any(c.strip() for c in r))
        header = [c.strip() for c in header]
        if "Date" not in header or "10 YR" not in header:
            return "Treasury body lacks Date / 10 YR"
    except Exception as e:
        return "Treasury body failed its content test (%s)" % type(e).__name__
    return None


def body_problem_d4(body):
    try:
        header = [c.strip() for c in next(csv.reader(io.StringIO(body.decode("utf-8-sig"))))]
        if "real_hs_cmt_10yr" not in header or "real_mc_cmt_10yr" not in header:
            return "Treasury overlap body lacks real_hs_cmt_10yr / real_mc_cmt_10yr"
    except Exception as e:
        return "Treasury overlap body failed its content test (%s)" % type(e).__name__
    return None


def body_problem_fed(key):
    def test(body):
        try:
            head = body.decode("utf-8-sig").splitlines()[:10]
        except Exception as e:
            return "Fed body failed its content test (%s)" % type(e).__name__
        if not any("Unique Identifier" in ln and FED_IDS[key] in ln for ln in head):
            return "Fed body lacks the Unique Identifier %s" % FED_IDS[key]
        return None
    return test


class Fetcher:
    """All requests go through here. Injectable opener, clock, sleeper and STOP path make it testable without a network."""

    def __init__(self, cache, out_dir, sleep=MIN_SLEEP, max_requests=MAX_REQUESTS, opener=real_opener, wall=time.time, mono=time.monotonic,
                 sleeper=time.sleep, stop_path=STOP_PATH, now_utc=None):
        min_sleep = 4.0 if mut("g25_gap_4s") else MIN_SLEEP
        if sleep < min_sleep:
            raise Refused("--sleep must be at least %.2f seconds" % MIN_SLEEP)
        if max_requests > MAX_REQUESTS or max_requests < 1:
            raise Refused("--max-requests must be between 1 and %d" % MAX_REQUESTS)
        self.cache = check_cache(cache)
        self.out_dir = out_dir
        self.sleep = float(sleep)
        self.max_requests = 13 if mut("g25_13th_request") else max_requests
        self.opener, self.wall, self.mono, self.sleeper = opener, wall, mono, sleeper
        self.stop_path = stop_path
        self.now_utc = now_utc or (lambda: dt.datetime.now(dt.timezone.utc))
        self.requests = 0
        self._last_mono = None
        self._last_file = os.path.join(os.path.dirname(stop_path), ".last_request")
        self.log_path = os.path.join(out_dir, "fetch_log.csv")
        self.logged = []

    def _stop_check(self):
        if not mut("g24_fetch_with_stop") and os.path.exists(self.stop_path):
            with open(self.stop_path, encoding="utf-8") as fh:
                why = fh.read().strip().replace("\n", " ")[:200]
            raise Latched("STOP exists at %s (%s); a human must inspect and delete it" % (tilde(self.stop_path), why))

    def __enter__(self):
        self._stop_check()
        os.makedirs(self.cache, exist_ok=True)
        os.makedirs(os.path.dirname(self.stop_path), exist_ok=True)
        return self

    def __exit__(self, *exc):
        return False

    def _pace(self):
        gap = 4.0 if mut("g25_gap_4s") else self.sleep
        wait = 0.0
        try:
            with open(self._last_file, encoding="utf-8") as fh:
                last = float(fh.read().strip())
            wait = max(wait, min(gap, gap - (self.wall() - last)))
        except (OSError, ValueError):
            pass
        if self._last_mono is not None:
            wait = max(wait, gap - (self.mono() - self._last_mono))
        if wait > 0:
            self.sleeper(wait)

    def _stamp(self, ts):
        return dt.datetime.fromtimestamp(ts, dt.timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ")

    def _log(self, ts, host, path, status, nbytes, sha, outcome):
        rows = read_table(self.log_path, LOG_COLS)
        rows.append([self._stamp(ts), host, path, str(status), str(nbytes), sha, outcome])
        text = render_table(LOG_COLS, rows, SOURCE_LOG)
        verify_text("fetch_log.csv", text)
        write_text(self.log_path, text)

    def _latch(self, reason):
        os.makedirs(os.path.dirname(self.stop_path), exist_ok=True)
        with open(self.stop_path, "w", encoding="utf-8") as fh:
            fh.write("%s UTC  %s\n" % (self.now_utc().strftime("%Y-%m-%dT%H:%M:%S"), reason))
        raise Latched(reason)

    def get(self, host, target, body_test=None):
        """One request. Returns (body, started, status) on a good 200. Raises Latched, SocketFault, MaxRequests or Refused."""
        check_target(host, target)
        self._stop_check()
        if self.requests >= self.max_requests:
            raise MaxRequests("request cap reached (%d)" % self.max_requests)
        self._pace()
        started = self.wall()
        self._last_mono = self.mono()
        with open(self._last_file, "w", encoding="utf-8") as fh:
            fh.write("%r\n" % started)
        self.requests += 1
        try:
            status, body = self.opener(host, target, HEADERS, TIMEOUT, BODY_CAP)
        except SocketFault as e:
            self._log(started, host, target, "", "", "", "socket_fault:" + str(e))
            raise
        if status >= 500:
            self._log(started, host, target, status, "", "", "server_error_no_latch")
            raise SocketFault("http_%d" % status)
        if status != 200:
            self._log(started, host, target, status, "", "", "STOP:http_%d" % status)
            if not (mut("g24_skip_latch_403") and status == 403):
                self._latch("HTTP %d for %s%s" % (status, host, target[:60]))
            raise Latched("HTTP %d (not latched: guard off)" % status)
        reason = "body larger than the cap" if body is None else (body_test(body) if body_test else None)
        if reason:
            self._log(started, host, target, status, "", "", "STOP:bad_body")
            self._latch("%s (%s%s)" % (reason, host, target[:60]))
        return body, started, status

    def save(self, fid, host, target, body_test):
        body, started, status = self.get(host, target, body_test)
        sha = sha256_of(body)
        date_s = dt.datetime.fromtimestamp(started, dt.timezone.utc).strftime("%Y-%m-%d")
        d = os.path.join(self.cache, "vintages", fid_source(fid))
        os.makedirs(d, exist_ok=True)
        path = os.path.join(d, vint_name(fid, date_s, sha))
        with open(path + ".part", "wb") as fh:
            fh.write(body)
        os.replace(path + ".part", path)
        self._log(started, host, target, status, len(body), sha, "saved")
        return "saved"


def d3_complete(vs, year):
    v = latest_of(vs, "D3-%d" % year)
    if v is None:
        return False
    try:
        last = max(parse_treasury(read_bytes(v["path"])))[0]
    except Exception:
        return False
    return last >= dt.date(year, 12, 24)


def fetch_all(fe, cur_year, say=print):
    vs = list_vintages(fe.cache)
    plan = [("D1", WB_HOST, WB_PATH, body_problem_xlsx)]
    if latest_of(vs, "D2") is None:
        plan.append(("D2", TR_HOST, D2_PATH, body_problem_treasury))
    for y in range(2024, cur_year + 1):
        if y == cur_year or not d3_complete(vs, y):
            plan.append(("D3-%d" % y, TR_HOST, D3_FMT.format(y=y), body_problem_treasury))
    if latest_of(vs, "D4") is None:
        plan.append(("D4", TR_HOST, D4_PATH, body_problem_d4))
    plan.append(("D5", FED_HOST, D5_PATH, body_problem_fed("D5")))
    plan.append(("D6", FED_HOST, D6_PATH, body_problem_fed("D6")))
    for fid, host, target, test in plan:
        say("%s: %s" % (fid, fe.save(fid, host, target, test)))
    say("requests sent: %d" % fe.requests)
    return fe.requests


# ----------------------------------------------------------------------------------------------------------------------------------
# build wrapper and report
# ----------------------------------------------------------------------------------------------------------------------------------
def build(cache, out_dir, cfg=REAL_CFG, inputs=None, local_dir=None):
    cache_real = cache
    if inputs is None:
        cache_real = check_cache(cache)
        inputs = load_inputs(cache_real, cfg)
    if local_dir is None:
        local_dir = os.path.join(cache_real, "local_outputs")
    P = Panel(cfg, inputs["gold"], inputs["tips_m"], inputs["usd"])
    P.daily = inputs["daily"]
    A = analyse(P, cfg, inputs)
    bp = band_problems(A["results"])
    if bp:
        raise DataError("results.csv bands disagree with coef -/+ crit_value x se_hac: " + "; ".join(bp[:3]))
    write_outputs(P, cfg, inputs, A, out_dir, local_dir, cache_real)
    checks = live_checks(P, cfg, inputs, A) if cfg["live"] else []
    checks.append(ck("K10", "Every results.csv row: ci_low and ci_high equal coef -/+ crit_value x se_hac (to printed rounding); the P1 band on stdout equals results.csv's",
                     "0 rows disagree", "0 of %d rows disagree" % sum(1 for r in A["results"] if r.get("ci_low")), "PASS"))
    rows, final = finish(out_dir, checks, inputs["retrieved"])
    return dict(P=P, A=A, checks=rows, final=final, inputs=inputs, cfg=cfg, out_dir=out_dir)


def report(res):
    P, A, cfg, inputs = res["P"], res["A"], res["cfg"], res["inputs"]
    L = []
    say = L.append
    say("World Bank workbook: Updated on %s, sha256 %s…" % (inputs["gold_updated"], inputs["gold_sha"][:8]))
    for ln in inputs["revisions"]:
        say("  " + ln)
    if not inputs["revisions"]:
        say("  (no earlier vintage of the workbook or the dollar file in the cache: no revision report)")
    say("")
    say("Cross-checks K01-K07 (published values the spec pins):")
    for c in res["checks"]:
        if c["check_id"][:3] in ("K01", "K02", "K03", "K04", "K05", "K06", "K07"):
            say("  %-5s %-5s %s: %s" % (c["check_id"], c["status"], c["description"], c["observed"]))
    p1 = A["p1"]
    say("")
    say("n = %d, HAC lag %d (rule-of-thumb %d), fixed-b cv %.3f (b = %.4f)" % (p1["n"], A["p1_L"], p1["rule"], A["p1_cv"], A["p1_L"] / float(p1["n"])))
    k09 = [c for c in res["checks"] if c["check_id"] == "K09"]
    if k09:
        say("K09 null size on the real regressors (limit 0.065): %s  [%s]" % (k09[0]["observed"], k09[0]["status"]))
    say("")
    say("Break-scan candidates by trim (change sample, k = last month of regime 1):")
    for pi, a, b in trim_table(P.cmonths):
        say("  trim %.2f: %s to %s%s" % (pi, a, b, "   (the pre-registered trim)" if abs(pi - PRE_REG_TRIM) < 1e-12 else ""))
    say("  " + NO_2026_SENTENCE)
    say("")
    say("Engle-Granger cointegration test (descriptive gate for the levels objects), tau_c, N = 3, 5%:")
    for r in A["coint"]:
        if r["test_id"] in ("EG_tauc_fit", "EG_tauc_full"):
            say("  %s %s..%s T=%s lags=%s stat %s vs cv %s -> %s%s" % (r["role"].upper(), r["sample_start"], r["sample_end"], r["T"], r["adf_lags"], r["adf_stat"],
                                                                         r["cv_5pct"], "reject" if r["reject_5pct"] == "yes" else "do not reject",
                                                                         "  (INFO only, gates nothing)" if r["role"] == "info" else ""))
    say("  levels objects: %s" % ("reported" if A["linfo"]["gate_reject"] else "suppressed_no_cointegration (no levels number is printed anywhere)"))
    say("")
    say("P1 (the one confirmatory test), OLS of the monthly change in ln(gold) on the change in the 10y real yield (pp) and in ln(dollar), %s to %s:" % (P.cmonths[0], P.cmonths[-1]))
    say("  b = %.4f log points per pp (%.1f%% approx, %.1f%% exact)   HAC se %.4f   classical se %.4f (not the precision statement)" % (
        p1["b"], 100 * p1["b"], pct_exact(p1["b"]), p1["se"], p1["cls"]))
    say("  95%% fixed-b interval [%.4f, %.4f] (cv %.3f)   c (dollar elasticity) = %.4f (HAC se %.4f)   R2 %.4f" % (p1["lo"], p1["hi"], A["p1_cv"], p1["c"], p1["c_se"], p1["r2"]))
    sb = stdout_band_problems(L, A["results"])
    if sb:
        raise DataError("; ".join(sb))
    say("  VERDICT: %s   (rule: SUPPORTS if b <= -0.050 and hi < 0; AGAINST if lo > -0.050; otherwise INCONCLUSIVE)" % p1["verdict"])
    say("  realised MDE at 80%% power: %.4f log points per pp (%.3f x se_HAC); materiality line -0.050" % (p1["mde"], A["p1_cv"] + Z80))
    say("")
    say("B1 break scan (DESCRIPTIVE, no verdict; stationary bootstrap p-value, B = %d, mean block %d):" % (cfg["boot_B"], cfg["boot_block"]))
    for r, key in zip(A["b1_rows"], A["b1"]):
        d = A["b1"][key]
        say("  trim %s %-12s sup-Wald %8s  boot p %s  Andrews 10/5/1%% %s/%s/%s  k_SSR %s (k_supWald %s)  Bai +-%sm -> [%s, %s]%s" % (
            r["trim"], r["dummy_spec"], r["sup_wald"], r["p_value_boot"], r["andrews_cv10"], r["andrews_cv5"], r["andrews_cv1"], r["break_month_ssr"],
            r["break_month_supwald"], r["bai_halfwidth_months"], r["bai_ci_low"], r["bai_ci_high"], " clipped" if r["ci_clipped"] == "yes" else ""))
    d = A["b1"][(PRE_REG_TRIM, "none")]
    r15 = [r for r in A["b1_rows"] if r["trim"] == "0.15" and r["dummy_spec"] == "none"][0]
    say("  The break scan's bootstrap p-value is %s at trim 0.15. Asymptotic Andrews 5%% value %s is context only." % (r15["p_value_boot"], r15["andrews_cv5"]))
    say("  The most likely break month is %s, with a Bai interval of +-%d months (unclipped, h = %.1f). An interval that narrow would need a slope shift of at least %.3f per pp." % (
        r15["break_month_ssr"], math.ceil(d["h"]), d["h"], d["s_actual"]))
    say("  s_min(h) by half-width h = %s months: %s per pp" % (", ".join(str(h) for h in S_MIN_H), ", ".join(r15["s_min_h%d" % h] for h in S_MIN_H)))
    say("  Regime residual variances (trim 0.15): %s and %s" % (r15["resid_var_regime1"], r15["resid_var_regime2"]))
    say("  If the interval is wide or the p-value large: no single break large enough to date was found; B1 cannot see a slope break below about 0.17 per pp,")
    say("  so this says nothing about 2024-26.")
    say("")
    say("Descriptive objects (labelled as such; none is a test):")
    for r in A["results"]:
        if r["coef_name"] == "b_ry" and r["object_id"] != "P1":
            say("  %-3s %s..%s n=%s L=%s%s: b = %s [%s, %s]" % (r["object_id"], r["sample_start"], r["sample_end"], r["n"], r["hac_lag"],
                                                               (" " + r["flag"]) if r["flag"] else "", r["coef"], r["ci_low"], r["ci_high"]))
    last = A["roll"][-1]
    say("  D6  rolling 36-month slopes: %d windows (ends %s to %s) are in rolling36.csv and rolling36.svg; none is counted. Last window %s: %s [%s, %s]" % (
        len(A["roll"]), A["roll"][0]["end_month"], last["end_month"], last["end_month"], last["beta_ry"], last["boot_lo"], last["boot_hi"]))
    for r in A["chow"]:
        say("  D7  Chow, regime 2 from %s: Wald %s, chi2(3) p = %s (descriptive; date known, chosen with hindsight)" % (r["regime2_start"], r["wald_hac"], r["p_chi2"]))
    lab = [r for r in A["levels"] if r["object_id"] == "D8_residual"][0]
    say("  D8  levels: %s%s" % (lab["status"], ("; residual label: " + lab["residual_label"]) if lab["status"] == "reported" else ""))
    say("")
    bad = [c for c in res["checks"] if c["status"] in ("FAIL",)]
    warn = [c for c in res["checks"] if c["status"] == "WARN"]
    say("checks: %d rows; FAIL %d, WARN %d.  K08 leak scan: %s" % (len(res["checks"]), len(bad), len(warn), [c for c in res["checks"] if c["check_id"] == "K08"][0]["status"]))
    for c in bad + warn:
        say("  %s %s: expected %s, observed %s" % (c["status"], c["check_id"], c["expected"], c["observed"]))
    return L


# ----------------------------------------------------------------------------------------------------------------------------------
# synthetic inputs (selftest only): dates in 2027-2050, seeded, no World Bank values
# ----------------------------------------------------------------------------------------------------------------------------------
def month_days(m):
    y, mo = int(m[:4]), int(m[5:7])
    d = dt.date(y, mo, 1)
    while d.month == mo:
        if d.weekday() < 5:
            yield d
        d += dt.timedelta(days=1)


def synth_inputs(cfg, seed=11, mode="changes", extra=3, b=-0.15, c=-0.8, a=0.002, noise=0.03, d4_gap=0.03):
    """A synthetic panel with a KNOWN same-month slope b on the change in the yield and c on the change in ln(dollar)."""
    rs = np.random.RandomState(seed)
    months = month_range(cfg["d2_start"], month_add(cfg["end"], extra))
    daily, lvl = [], 2.0
    for m in months:
        for d in month_days(m):
            lvl += 0.04 * rs.randn()
            daily.append((d, round(lvl, 2)))
    tips_m = monthly_tips(daily, d4_gap, cfg["seam_date"])
    r = np.array([tips_m[m]["mc"] for m in months])
    dr = np.diff(r)
    du = 0.013 * (0.4 * dr / 0.18 + math.sqrt(1 - 0.16) * rs.randn(len(dr)))
    u = np.concatenate([[0.0], np.cumsum(du)])
    if mode == "changes":
        dg = a + b * dr + c * du + noise * rs.randn(len(dr))
        g = np.concatenate([[math.log(1000.0)], math.log(1000.0) + np.cumsum(dg)])
    else:
        s = np.zeros(len(r))
        for t in range(1, len(r)):
            s[t] = 0.6 * s[t - 1] + noise * rs.randn()
        g = math.log(1000.0) + 0.3 + b * r + c * u + s
    off = month_diff(cfg["first_level"], cfg["d2_start"])
    usd = {m: 100.0 * math.exp(u[i] - u[off]) for i, m in enumerate(months) if i >= off}
    gold = {m: math.exp(g[i]) for i, m in enumerate(months)}
    return dict(gold=gold, gold_updated="", gold_last=max(gold), gold_sha="0" * 64, gold_bytes=0, daily=daily, d4_gap=d4_gap, d4_n=251, tips_m=tips_m, usd=usd,
                usd_label="synthetic", usd_daily={}, retrieved={"wb": "2030-01-01", "tr": "2030-01-01", "fed": "2030-01-01"}, revisions=[], rev_warn=False,
                vintages=[], cache="")


# ----------------------------------------------------------------------------------------------------------------------------------
# selftest: 30 named guards on synthetic data; every guard has the mutant(s) it must catch (§7)
# ----------------------------------------------------------------------------------------------------------------------------------
def _tmp():
    d = tempfile.mkdtemp(prefix="gry_selftest_")
    real, root = os.path.realpath(d), os.path.realpath(ROOT)
    if real == root or real.startswith(root + os.sep):
        raise Refused("the selftest's temporary directory is inside the repository")
    return real


class FakeClock:
    def __init__(self, t0=1.8e9):
        self.t = t0

    def wall(self):
        return self.t

    def mono(self):
        return self.t

    def sleep(self, s):
        self.t += s


class FakeNet:
    def __init__(self, clock, script):
        self.clock, self.script, self.calls = clock, list(script), []

    def __call__(self, host, target, headers, timeout, cap):
        self.calls.append((self.clock.t, host, target, dict(headers)))
        item = self.script.pop(0) if len(self.script) > 1 else self.script[0]
        if isinstance(item, Exception):
            raise item
        return item


def _fetcher(net, clock, sleep=MIN_SLEEP, max_requests=MAX_REQUESTS, stop=None, tmp=None):
    tmp = tmp or _tmp()
    return Fetcher(os.path.join(tmp, "cache"), os.path.join(tmp, "out"), sleep=sleep, max_requests=max_requests, opener=net, wall=clock.wall,
                   mono=clock.mono, sleeper=clock.sleep, stop_path=stop or os.path.join(tmp, "stopdir", "STOP")), tmp


_SYN = {}


def syn_build(mode="changes", **kw):
    key = (mode, tuple(sorted(_MUT)), tuple(sorted(kw.items())))
    if key not in _SYN:
        inp = synth_inputs(SYN_CFG, mode=mode, **kw)
        out, loc = _tmp(), _tmp()
        res = build("n/a", out, cfg=SYN_CFG, inputs=inp, local_dir=loc)
        res["loc"] = loc
        _SYN[key] = res
    return _SYN[key]


_SIM = {}


def sim_fixture():
    if "x" not in _SIM:
        rs = np.random.RandomState(SEED)
        n = 248
        z = rs.randn(n, 2)
        dr = 0.18 * z[:, 0]
        du = 0.013 * (0.39 * z[:, 0] + math.sqrt(1 - 0.39 ** 2) * z[:, 1])
        X = np.column_stack([np.ones(n), dr, du])
        iid, ar = sim_noise(rs, 20000, n)
        _SIM["x"] = (X, iid, ar)
    return _SIM["x"]


def _row(lst, name, cond, detail=""):
    lst.append((name, bool(cond), detail))


def g01():
    r = []
    _row(r, "L = 12 at n = 248 and the rule of thumb is 4", hac_lag(248) == 12 and rule_lag(248) == 4, "L=%s rule=%s" % (hac_lag(248), rule_lag(248)))
    _row(r, "a large n lets the rule exceed the floor", hac_lag(10 ** 7) == rule_lag(10 ** 7) and hac_lag(10 ** 7) > 12, str(hac_lag(10 ** 7)))
    res = syn_build("changes")
    lines = report(res)
    _row(r, "both numbers are printed side by side", any(("HAC lag %d (rule-of-thumb %d)" % (12, rule_lag(res["P"].n))) in ln for ln in lines))
    row = [x for x in res["A"]["results"] if x["object_id"] == "P1" and x["coef_name"] == "b_ry"][0]
    _row(r, "results.csv carries hac_lag 12 and the rule", row["hac_lag"] == 12 and row["hac_lag_rule"] == rule_lag(res["P"].n))
    return r


def g02():
    r = []
    rs = np.random.RandomState(1)
    Z = rs.randn(60, 3)
    for L in (0, 1, 5, 12):
        d = float(np.abs(nw_S(Z, L) - nw_S_loop(Z, L)).max())
        _row(r, "matrix and explicit loop agree at L=%d" % L, d < 1e-12, "max diff %.2e" % d)
    z = np.array([[1.0], [2.0], [3.0]])
    _row(r, "hand example: Gamma0 = 14, Gamma1 = 8, w1 = 1/2 gives 22", abs(nw_S(z, 1)[0, 0] - 22.0) < 1e-12, str(nw_S(z, 1)[0, 0]))
    X = np.column_stack([np.ones(60), rs.randn(60), rs.randn(60)])
    y = X @ np.array([0.1, -0.3, 0.2]) + rs.randn(60)
    beta, e, XtXi = ols(X, y)
    hc0 = XtXi @ (X.T @ np.diag(e ** 2) @ X) @ XtXi
    d = float(np.abs(hac_V(X, e, 0, XtXi) - hc0).max())
    _row(r, "L = 0 equals White HC0", d < 1e-12, "max diff %.2e" % d)
    return r


def g03():
    r = []
    _row(r, "b = -0.202 gives -18.29", round(pct_exact(-0.202), 2) == -18.29, "%.4f" % pct_exact(-0.202))
    _row(r, "b = 0 gives 0 and b = 0.1 gives 10.52", pct_exact(0.0) == 0.0 and round(pct_exact(0.1), 2) == 10.52)
    res = syn_build("changes")
    b = res["A"]["p1"]["b"]
    row = [x for x in res["A"]["results"] if x["object_id"] == "P1" and x["coef_name"] == "b_ry"][0]
    _row(r, "results.csv pct_exact is 100(e^b - 1), pct_approx is 100b", row["pct_exact"] == f(100 * (math.exp(b) - 1), 1) and row["pct_approx"] == f(100 * b, 1))
    return r


_FB_TARGET = 2.1046


def g04():
    r = []
    c = kv_cubic(12 / 248.0)
    _row(r, "the Kiefer-Vogelsang cubic at b = 12/248 gives 2.1046", abs(c - _FB_TARGET) < 5e-4, "%.5f" % c)
    _row(r, "the verdict's critical value is 2.105", p1_cv(248, 12) == 2.105, str(p1_cv(248, 12)))
    sim = fixed_b_limit()
    _row(r, "the cubic is within 0.02 of a seeded simulation of the fixed-b limit", abs(c - sim) < 0.02, "cubic %.4f, simulation %.4f" % (c, sim))
    # the committed band must be the printed critical value times the printed se (a wrong band once passed every other guard)
    inp = synth_inputs(SYN_CFG)
    P = Panel(SYN_CFG, inp["gold"], inp["tips_m"], inp["usd"])
    rows, _ = coef_rows("P1", "confirmatory", P.cmonths[0], P.cmonths[-1], P.dg, P.X(), ["a_const", "b_ry", "c_usd"], REG_NAMES)
    bp = band_problems(rows)
    _row(r, "every coefficient row's ci_low/ci_high equal coef -/+ crit_value x se_hac", not bp, "; ".join(bp[:2]))
    rows_b = [dict(x) for x in rows]
    rows_b[1]["ci_high"] = f(float(rows_b[1]["ci_high"]) + 0.01, 4)
    _row(r, "the band checker flags a planted wrong band", len(band_problems(rows_b)) == 1)
    try:
        res = syn_build("changes")
        n, L = res["P"].n, res["A"]["p1_L"]
        row = [x for x in res["A"]["results"] if x["object_id"] == "P1" and x["coef_name"] == "b_ry"][0]
        _row(r, "the P1 row's critical value is the cubic at b = L/n, rounded", row["crit_value"] == f(round(kv_cubic(L / n), 3), 3), row["crit_value"])
        _row(r, "every results.csv row of a full build passes the band check", not band_problems(res["A"]["results"]))
        _row(r, "the P1 band on stdout equals results.csv's", not stdout_band_problems(report(res), res["A"]["results"]))
    except Exception as e:
        _row(r, "a full build and its report complete with consistent bands", False, "%s: %s" % (type(e).__name__, str(e)[:120]))
    return r


def g05():
    r = []
    bad, n = [], 0
    for b in (-0.30, -0.10, -0.06, -0.05, -0.049, -0.02, 0.0, 0.03):
        for h in (0.0005, 0.01, 0.03, 0.05, 0.2):
            n += 1
            if len(verdict_regions(b, b - h, b + h)) != 1:
                bad.append((b, h))
    _row(r, "exactly one region on a grid of %d (b, lo, hi)" % n, not bad, str(bad[:3]))
    pins = [((-0.05, -0.06, -0.001), "SUPPORTS"), ((-0.06, -0.08, 0.0), "INCONCLUSIVE"), ((-0.04, -0.05, 0.01), "INCONCLUSIVE"),
            ((-0.04, -0.0499, 0.01), "AGAINST"), ((-0.04, -0.06, -0.01), "INCONCLUSIVE"), ((0.02, 0.001, 0.04), "AGAINST"),
            ((-0.07, -0.09, -0.0001), "SUPPORTS"), ((-0.049, -0.09, -0.001), "INCONCLUSIVE")]
    for args, want in pins:
        got = sorted(verdict_regions(*args))
        _row(r, "boundary %s -> %s" % (args, want), got == [want], str(got))
    return r


_ANDREWS_SPEC = {(1, 0.05): (8.13, 9.71, 13.17), (1, 0.15): (7.12, 8.68, 12.16), (1, 0.25): (6.35, 7.87, 11.28),
                 (3, 0.05): (13.46, 15.36, 19.28), (3, 0.15): (12.28, 14.13, 18.07), (3, 0.25): (11.32, 13.18, 17.13)}
PIN_G6 = (0.7, 22.300879598533093)      # seeded p_value_boot and sup-Wald on the synthetic series (regression pin recorded at the first run)


def g06():
    r = []
    bad = [(q, pi, j) for (q, pi), v in _ANDREWS_SPEC.items() for j in range(3) if andrews_cv(q, pi, j) != v[j]]
    _row(r, "the constants equal Andrews (2003) Table I (q = 1 and 3, three trims, 10/5/1%)", not bad, str(bad[:2]))
    rs = np.random.RandomState(5)
    n = 70
    X0 = np.column_stack([np.ones(n), rs.randn(n), rs.randn(n)])
    y = X0 @ np.array([0.0, -0.2, 0.1]) + 0.5 * rs.randn(n)
    lo, hi = cand_range(n, 0.15)
    cands = list(range(lo, hi + 1))
    W = scan(y, X0, None, cands, 12)[0]
    Wb = bootstrap_scan(y, X0, None, cands, 12, 49, 6, SEED)
    p = (1 + float((Wb.max(1) >= W.max()).sum())) / 50.0
    _row(r, "p_value_boot and the sup-Wald reproduce the seeded values on a synthetic series",
         PIN_G6 is None or (abs(p - PIN_G6[0]) < 1e-12 and abs(float(W.max()) - PIN_G6[1]) < 1e-9 * PIN_G6[1]), "p=%r supW=%r" % (p, float(W.max())))
    return r


def _stub(first, last):
    class S:
        months = month_range(first, last)

        def lsl(self, a, b):
            return slice(self.months.index(a), self.months.index(b) + 1)
    return S()


def g07():
    r = []
    cm = month_range("2006-02", "2026-09")
    _row(r, "n = 248 change months", len(cm) == 248, str(len(cm)))
    got = [(a, b) for _, a, b in trim_table(cm)]
    _row(r, "ranges map to 2007-02/2025-08, 2009-03/2023-07, 2011-03/2021-07", got == [("2007-02", "2025-08"), ("2009-03", "2023-07"), ("2011-03", "2021-07")], str(got))
    _row(r, "k bounds are 13..235, 38..210, 62..186", [cand_range(248, p) for p in TRIMS] == [(13, 235), (38, 210), (62, 186)], str([cand_range(248, p) for p in TRIMS]))
    return r


def g08():
    r = []
    want = ("No trim can return a 2026 break date: the latest candidate under any trim is 2025-08. "
            "A 2026 change in sensitivity is not testable as a break date on this sample.")
    _row(r, "the verbatim sentence is the constant", NO_2026_SENTENCE == want)
    cm = month_range("2006-02", "2026-09")
    latest = max(b for _, _, b in trim_table(cm))
    _row(r, "the latest candidate month is before 2026-01", latest < "2026-01", latest)
    _row(r, "the latest candidate under every trim is 2025-08 or earlier", all(b <= "2025-08" for _, _, b in trim_table(cm)), str(trim_table(cm)))
    try:
        res = syn_build("changes")
        _row(r, "the sentence is printed by the report", any(want in ln for ln in report(res)))
    except Exception as e:
        _row(r, "the build and report run", False, "%s: %s" % (type(e).__name__, e))
    return r


def g09():
    r = []
    rs = np.random.RandomState(9)
    n = 200
    X0 = np.column_stack([np.ones(n), rs.randn(n), rs.randn(n)])
    Q = X0.T @ X0 / n
    delta = np.array([0.0, 0.5, 0.2])
    sig2 = 0.8
    h = bai_halfwidth(delta, sig2 * Q, Q)
    _row(r, "h = 11.03 sigma^2/(d'Qd) when Omega = sigma^2 Q", abs(h - 11.03 * sig2 / float(delta @ Q @ delta)) < 1e-6, "%.8f" % h)
    k0 = 100
    y = X0 @ np.array([0.1, -0.2, 0.05]) + (X0 * (np.arange(n) >= k0)[:, None]) @ delta + rs.randn(n) * math.sqrt(sig2)
    Xk = np.hstack([X0, X0 * (np.arange(n) >= k0)[:, None]])
    beta, e, _ = ols(Xk, y)
    dh = beta[-3:]
    Om = (X0 * e[:, None]).T @ (X0 * e[:, None]) / n
    h2 = bai_halfwidth(dh, Om, Q)
    _row(r, "L = 0 end to end: h = 11.03 (d'Om d)/(d'Q d)^2 within 1e-6", abs(h2 - 11.03 * float(dh @ Om @ dh) / float(dh @ Q @ dh) ** 2) < 1e-6, "%.6f" % h2)
    ok = True
    for hh in S_MIN_H:
        s = s_min(hh, Om[1, 1], Q[1, 1])
        ok &= abs(bai_halfwidth(np.array([0.0, s, 0.0]), Om, Q) - hh) < 1e-9
    _row(r, "s_min(h) inverts h exactly for h = 4, 6, 8, 12, 18", ok)
    cands = list(range(10, 191))
    ssr_row = np.array([1.0 + 0.00002 * (k - 100) ** 2 for k in cands])
    lo, hi, lo_c, hi_c, clipped, width = bai_interval(3, 10.2, n, ssr_row, cands)
    _row(r, "interval is k +- ceil(h), unclipped: [-8, 14], width 22, flagged clipped", (lo, hi, clipped, width) == (-8, 14, True, 22), str((lo, hi, clipped, width)))
    lo, hi, lo_c, hi_c, clipped, width = bai_interval(100, 6.2, n, ssr_row, cands)
    _row(r, "an interior interval is [93, 107] with width 14", (lo, hi, clipped, width) == (93, 107, False, 14), str((lo, hi, clipped, width)))
    return r


def g10():
    r = []
    rs = np.random.RandomState(10)
    n, k0 = 120, 60
    X0 = np.column_stack([np.ones(n), rs.randn(n), rs.randn(n)])
    y = X0 @ np.array([0.0, -0.1, 0.0]) + (X0 * (np.arange(n) >= k0)[:, None]) @ np.array([0.0, 0.8, 0.0]) + 0.3 * rs.randn(n)
    lo, hi = cand_range(n, 0.15)
    cands = list(range(lo, hi + 1))
    W, S, _ = scan(y, X0, None, cands, 12)
    i = pick_break_ssr(W[0], S[0], cands)
    _row(r, "k-hat is the argmin of total SSR", i == int(np.argmin(S[0])), str(cands[i]))
    _row(r, "k-hat lies within 3 months of the known break at %d" % k0, abs(cands[i] - k0) <= 3, str(cands[i]))
    return r


def g11():
    r = []
    st = _stub("2006-01", "2026-09")
    sl, a, b, T = gate_info(st, REAL_CFG)
    _row(r, "the gate runs on 2006-01..2021-11 (T = 191)", (a, b, T) == ("2006-01", "2021-11", 191), str((a, b, T)))
    _row(r, "tau_c critical values -3.7858 (T=191) and -3.7752 (T=249)", (round(mack_cv(191), 4), round(mack_cv(249), 4)) == (-3.7858, -3.7752),
         "%.4f %.4f" % (mack_cv(191), mack_cv(249)))
    _row(r, "tau_ct critical values -4.1817 and -4.1670", (round(mack_cv(191, True), 4), round(mack_cv(249, True), 4)) == (-4.1817, -4.1670),
         "%.4f %.4f" % (mack_cv(191, True), mack_cv(249, True)))
    return r


def g12():
    r = []
    rs = np.random.RandomState(12)
    T = 191
    rc = ri = 0
    N = 100
    for _ in range(N):
        x = np.cumsum(rs.randn(T, 2), axis=0)
        s = np.zeros(T)
        for t in range(1, T):
            s[t] = 0.5 * s[t - 1] + rs.randn()
        g = 1.0 + 0.5 * x[:, 0] + 0.3 * x[:, 1] + s
        X = np.column_stack([np.ones(T), x])
        tau, p, _ = eg_test(g, X)
        rc += tau < mack_cv(T)
        g2 = np.cumsum(rs.randn(T))
        tau2, p2, _ = eg_test(g2, X)
        ri += tau2 < mack_cv(T)
    _row(r, "a seeded cointegrated pair rejects (>= 90 of %d)" % N, rc >= 90, str(rc))
    _row(r, "independent seeded random walks do not (<= 15 of %d reject)" % N, ri <= 15, str(ri))
    return r


def _levels_rows(res):
    return [x for x in res["A"]["levels"]]


def g13():
    r = []
    res = syn_build("changes")
    lv = _levels_rows(res)
    sup = not res["A"]["linfo"]["gate_reject"]
    _row(r, "the non-cointegrated synthetic series does not reject", sup)
    _row(r, "every levels number cell is empty and status = suppressed_no_cointegration",
         all(x["status"] == "suppressed_no_cointegration" and x["coef"] == "" and x["ci_low"] == "" and x["ci_high"] == "" and x["resid_sd_in_sample"] == "" and
             x["residual_label"] == "" for x in lv))
    _row(r, "no residual path is produced", res["A"]["path"] is None)
    res2 = syn_build("levels")
    _row(r, "a cointegrated synthetic series rejects and reports levels", res2["A"]["linfo"]["gate_reject"] and all(x["status"] == "reported" for x in _levels_rows(res2)),
         str(res2["A"]["linfo"]["gate"]))
    _row(r, "the residual label is one of the three allowed words", [x for x in _levels_rows(res2) if x["object_id"] == "D8_residual"][0]["residual_label"] in ("high", "not_high", "inconclusive"))
    return r


def g14():
    r = []
    seam = dt.date(2040, 12, 6)
    days = [(dt.date(2040, 12, 3), 1.0), (dt.date(2040, 12, 4), 1.0), (dt.date(2040, 12, 5), 1.0), (dt.date(2040, 12, 6), 2.0), (dt.date(2040, 12, 7), 2.0)]
    t = monthly_tips(days, 0.05, seam)["2040-12"]
    _row(r, "synthetic December mean pinned at 1.43 (gap added to the 3 pre-seam prints only)", abs(t["mc"] - 1.43) < 1e-12, "%.6f" % t["mc"])
    _row(r, "the official mean is untouched (1.40)", abs(t["off"] - 1.40) < 1e-12)
    body = b"date,real_hs_cmt_10yr,real_mc_cmt_10yr\n2040-10-01,1.00,1.05\n2040-10-02,2.00,2.05\n"
    gap, nd = parse_d4(body)
    _row(r, "a synthetic D4 with MC above HS by 0.05 gives +0.05 (MC minus HS)", abs(gap - 0.05) < 1e-12 and nd == 2, "%.6f" % gap)
    return r


def g15():
    r = []
    _row(r, "1/2/03 -> 2003-01-02", parse_us_date("1/2/03") == dt.date(2003, 1, 2), str(parse_us_date("1/2/03")))
    _row(r, "12/29/23 -> 2023-12-29 and 12/29/2023 -> 2023-12-29", parse_us_date("12/29/23") == parse_us_date("12/29/2023") == dt.date(2023, 12, 29))
    body = b"Date,5 YR,10 YR\n1/2/03,1.0,2.5\n1/3/03,1.0,2.6\n"
    d = parse_treasury(body)
    _row(r, "a two-digit-year file parses to 2003", d[0][0] == dt.date(2003, 1, 2) and d[0][1] == 2.5, str(d[0][0]))
    return r


def g16():
    r = []
    good = b'"Series Description","Nominal Broad"\n"Unit:","Index:_1997_Jan_100"\n"Multiplier:","1"\n"Currency:","NA"\n"Unique Identifier: ","H10/H10/JRXWTFB_N.M"\n"Time Period","JRXWTFB_N.M"\n2030-01,100.0000\n2030-02,101.5000\n'
    unit, d = parse_fed(good, FED_IDS["D5"], base_month="2030-01")
    _row(r, "accepted when the VALUE at the base month is 100.0000, whatever the label says", d["2030-01"] == 100.0 and "1997" in unit)
    bad = good.replace(b"100.0000", b"123.4000")
    try:
        parse_fed(bad, FED_IDS["D5"], base_month="2030-01")
        _row(r, "refused when the value at the base month is not 100", False, "no error raised")
    except DataError:
        _row(r, "refused when the value at the base month is not 100", True)
    return r


def _wb(cols, units, rows, upd="Updated on October 02, 2030."):
    import openpyxl
    wb = openpyxl.Workbook()
    ws = wb.active
    ws.title = "Monthly Prices"
    ws.append(["World Bank Commodity Price Data (The Pink Sheet)"])
    ws.append([upd])
    ws.append([])
    ws.append([])
    ws.append([""] + cols)
    ws.append([""] + units)
    for rw in rows:
        ws.append(rw)
    bio = io.BytesIO()
    wb.save(bio)
    return bio.getvalue()


def g17():
    r = []
    raw = _wb(["Silver", "Gold", "Platinum"], ["($/troy oz)"] * 3, [["2030M01", 11.0, 2001.0, 901.0], ["2030M02", 12.0, 2002.0, 902.0]])
    gold, upd, last = parse_gold(raw)
    _row(r, "the Gold column is read, not its neighbours", gold == {"2030-01": 2001.0, "2030-02": 2002.0}, str(gold))
    _row(r, "the Updated on line and the last month are read", upd == "October 02, 2030" and last == "2030-02", "%r %r" % (upd, last))
    raw2 = _wb(["Silver", "Gold", "Platinum"], ["($/troy oz)", "($/mt)", "($/troy oz)"], [["2030M01", 11.0, 2001.0, 901.0]])
    try:
        parse_gold(raw2)
        _row(r, "a Gold header without the units in the same column is refused", False, "no error")
    except DataError:
        _row(r, "a Gold header without the units in the same column is refused", True)
    return r


def g18():
    r = []
    res = syn_build("changes")
    out = res["out_dir"]
    for nm, cols in ALLOW.items():
        p = os.path.join(out, nm)
        if os.path.exists(p):
            with open(p, encoding="utf-8") as fh:
                first, header, _ = split_table(fh.read())
            _row(r, "%s header equals its allowlist" % nm, header == cols)
    for nm, extra in (("results.csv", "ln_gold"), ("rolling36.csv", "n_excl_zero"), ("levels_summary.csv", "resid_last_sd_units")):
        try:
            verify_text(nm, render_table(ALLOW[nm] + [extra], [], source_line(nm, {"wb": "x", "tr": "x", "fed": "x"})))
            _row(r, "an added column %s is refused" % extra, False, "accepted")
        except DataError:
            _row(r, "an added column %s is refused" % extra, True)
    return r


def g19():
    r = []
    res = syn_build("levels")
    out, loc = res["out_dir"], res["loc"]
    _row(r, "K08 passes on the synthetic output directory", leak_scan(out) == [], str(leak_scan(out)))
    _row(r, "the local panel and the residual path are not in the output directory", not any(n.startswith("local_") for n in os.listdir(out)), str(os.listdir(out)))
    _row(r, "the local panel and the residual path are in the local directory", {"local_panel.csv", "local_levels_residual_path.csv"} <= set(os.listdir(loc)))
    d2 = _tmp()
    for n_ in os.listdir(out):
        with open(os.path.join(out, n_), "rb") as a, open(os.path.join(d2, n_), "wb") as b:
            b.write(a.read())
    with open(os.path.join(d2, "levels_residual_path.csv"), "w") as fh:
        fh.write("month,x\n")
    _row(r, "a residual-path file in the output directory fails K08", leak_scan(d2) != [])
    try:
        verify_text("rolling36.csv", render_table(ROLL_COLS, [["2030-01", 36, "-0.2012", "-0.30", "-0.10", 6, 9, SEED]], source_line("rolling36.csv", {"wb": "x", "tr": "x", "fed": "x"})))
        _row(r, "beta_ry at 4 dp fails", False, "accepted")
    except DataError:
        _row(r, "beta_ry at 4 dp fails", True)
    rows = [x for x in read_table(os.path.join(out, "rolling36.csv"), ROLL_COLS)]
    _row(r, "every rolling36 slope and band cell has at most 2 decimals", all(dec_places(c) <= 2 for x in rows for c in x[2:5]))
    return r


def g20():
    r = []
    opened = []
    real_open = builtins.open

    def spy(file, *a, **k):
        opened.append(str(file))
        return real_open(file, *a, **k)
    builtins.open = spy
    try:
        key = ("rec", tuple(sorted(_MUT)))
        inp = synth_inputs(SYN_CFG)
        out, loc = _tmp(), _tmp()
        res = build("n/a", out, cfg=SYN_CFG, inputs=inp, local_dir=loc)
    finally:
        builtins.open = real_open
    _row(r, "the build never opens data/gold/ledger_monthly.csv", not any("ledger_monthly" in p or "data/gold/" in p for p in opened))
    regs = {x["regressors"] for x in res["A"]["results"] if x["object_id"] == "P1"}
    _row(r, "P1 regressors are exactly the constant, the yield change and the dollar change", regs == {"const;d_ry;d_ln_usd"}, str(regs))
    bad = [x["regressors"] for x in res["A"]["results"] if re.search(r"tonne|official_change|ledger|_cf_t", x["regressors"])]
    _row(r, "no tonnes regressor anywhere", not bad, str(bad[:1]))
    return r


def g21():
    r = []
    res = syn_build("changes")
    ids = {x["object_id"] for x in res["A"]["results"]}
    _row(r, "every object id is in the registry", ids <= set(REGISTRY), str(sorted(ids - set(REGISTRY))))
    _row(r, "the registry is the fixed list P1, B1, D1-D9", REGISTRY == ("P1", "B1", "D1", "D2", "D3", "D4", "D5", "D6", "D7", "D8", "D9"))
    try:
        validate_ids({"results": [{"object_id": "D10"}], "levels": []})
        _row(r, "an unregistered D10 is a hard failure", False, "accepted")
    except DataError:
        _row(r, "an unregistered D10 is a hard failure", True)
    return r


PIN_G22 = 629604                        # sum of the seeded moving-block index array (regression pin recorded at the first run)


def g22():
    r = []
    res = syn_build("changes")
    rows = [x for x in res["A"]["roll"]]
    _row(r, "every rolling row carries block 6, B and the seed", all(x["block_len"] == 6 and x["draws"] == SYN_CFG["roll_B"] and x["seed"] == SEED for x in rows))
    rs = np.random.RandomState(SEED)
    idx = mbb_idx(rs, 36, 6, 999)
    _row(r, "block length 6: consecutive rows inside each block", bool((np.diff(idx[:, :6], axis=1) == 1).all() and (np.diff(idx[:, 6:12], axis=1) == 1).all()))
    s = int(idx.sum())
    _row(r, "the seeded index array is pinned", PIN_G22 is None or s == PIN_G22, "sum=%d" % s)
    _row(r, "B = 999 and block 6 are the registered settings", REAL_CFG["roll_B"] == 999 and REAL_CFG["block_roll"] == 6 and REAL_CFG["boot_B"] == 999 and REAL_CFG["boot_block"] == 6 and SEED == 20261018)
    return r


def g23():
    r = []
    for p in (os.path.join(ROOT, "data", "vintages", "gold_ry"), ROOT, os.path.join(ROOT, "x", "..", "data")):
        try:
            check_cache(p)
            _row(r, "a cache inside the repository is refused: %s" % os.path.relpath(p, ROOT), False, "accepted")
        except Refused:
            _row(r, "a cache inside the repository is refused: %s" % os.path.relpath(p, ROOT), True)
    t = _tmp()
    link = os.path.join(t, "lnk")
    os.symlink(os.path.join(ROOT, "data"), link)
    try:
        check_cache(link)
        _row(r, "a symlink into the repository is refused", False, "accepted")
    except Refused:
        _row(r, "a symlink into the repository is refused", True)
    try:
        check_cache(t)
        _row(r, "a directory outside the repository is accepted", True)
    except Refused:
        _row(r, "a directory outside the repository is accepted", False)
    _row(r, "the default cache is ~/gold_ry_cache, outside the repository", os.path.realpath(os.path.expanduser(CACHE_DEFAULT)).startswith(os.path.realpath(ROOT) + os.sep) is False)
    return r


def _latch_case(status_or_exc, body=b"", expect_latch=True, test=None):
    clock = FakeClock()
    net = FakeNet(clock, [(status_or_exc, body)] if not isinstance(status_or_exc, Exception) else [status_or_exc])
    fe, tmp = _fetcher(net, clock)
    got = None
    with fe:
        try:
            fe.get(WB_HOST, WB_PATH, test)
        except (Latched, SocketFault) as e:
            got = type(e).__name__
    return os.path.exists(fe.stop_path), got, tmp


def g24():
    r = []
    for st in (403, 429, 301, 302, 401):
        stop, got, _ = _latch_case(st)
        _row(r, "HTTP %d writes the STOP latch" % st, stop and got == "Latched", "stop=%s got=%s" % (stop, got))
    stop, got, _ = _latch_case(200, b"not a workbook", test=body_problem_xlsx)
    _row(r, "a 200 with a body that fails its content test writes the latch", stop and got == "Latched")
    for what in (500, 503, SocketFault("timeout")):
        stop, got, _ = _latch_case(what)
        _row(r, "%s does not latch" % (what if not isinstance(what, Exception) else "a socket fault"), (not stop) and got == "SocketFault", "stop=%s got=%s" % (stop, got))
    clock = FakeClock()
    net = FakeNet(clock, [(200, b"x")])
    tmp = _tmp()
    stopdir = os.path.join(tmp, "stopdir")
    os.makedirs(stopdir)
    with open(os.path.join(stopdir, "STOP"), "w") as fh:
        fh.write("test latch\n")
    fe, _ = _fetcher(net, clock, tmp=tmp)
    refused = False
    try:
        with fe:
            fe.get(WB_HOST, WB_PATH)
    except Latched:
        refused = True
    _row(r, "no fetch while STOP exists", refused and not net.calls, "calls=%d" % len(net.calls))
    return r


def g25():
    r = []
    for host, path in (("fred.stlouisfed.org", "/graph/fredgraph.csv?id=DFII10"), ("www.sec.gov", "/x"), (WB_HOST, "/en/doc/other.xlsx"), (TR_HOST, "/some/other.csv")):
        try:
            check_target(host, path)
            _row(r, "refused: %s%s" % (host, path[:24]), False, "accepted")
        except Refused:
            _row(r, "refused: %s%s" % (host, path[:24]), True)
    for host, path in ((WB_HOST, WB_PATH), (TR_HOST, D2_PATH), (TR_HOST, D3_FMT.format(y=2026)), (TR_HOST, D4_PATH), (FED_HOST, D5_PATH), (FED_HOST, D6_PATH)):
        try:
            check_target(host, path)
            _row(r, "allowed: %s" % host, True)
        except Refused as e:
            _row(r, "allowed: %s" % host, False, str(e))
    exact = HEADERS["User-Agent"] == "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
    no_address = "@" not in UA
    _row(r, "the header string is exact and carries no address", exact and no_address)
    clock = FakeClock()
    net = FakeNet(clock, [(200, b"ok")])
    fe, _ = _fetcher(net, clock)
    with fe:
        for i in range(4):
            fe.get(WB_HOST, WB_PATH)
    gaps = [b[0] - a[0] for a, b in zip(net.calls, net.calls[1:])]
    _row(r, "every gap between request starts is at least 5 s", all(g >= 5.0 for g in gaps), str(gaps))
    _row(r, "every request carries the exact User-Agent", all(c[3].get("User-Agent") == UA for c in net.calls))
    try:
        _fetcher(net, clock, sleep=4.0)
        _row(r, "a 4 s sleep setting is refused", False, "accepted")
    except Refused:
        _row(r, "a 4 s sleep setting is refused", True)
    clock = FakeClock()
    net = FakeNet(clock, [(200, b"ok")])
    fe, _ = _fetcher(net, clock)
    n = 0
    stopped = False
    with fe:
        try:
            for i in range(13):
                fe.get(WB_HOST, WB_PATH)
                n += 1
        except MaxRequests:
            stopped = True
    _row(r, "12 requests are allowed and the 13th is refused", n == 12 and stopped, "n=%d" % n)
    try:
        _fetcher(net, clock, max_requests=13)
        _row(r, "a --max-requests above 12 is refused", False, "accepted")
    except Refused:
        _row(r, "a --max-requests above 12 is refused", True)
    # the fetch plan: a full fetch is 8 requests, a second one reuses D2, D4 and the complete past-year D3 files
    import random
    clock = FakeClock()
    tre = lambda y: ("Date,5 YR,10 YR\n12/29/%d,1.0,2.0\n" % y).encode()
    bodies = {D2_PATH: b"Date,5 YR,10 YR\n12/29/23,1.0,2.0\n", D4_PATH: b"date,real_hs_cmt_10yr,real_mc_cmt_10yr\n2021-01-04,1.0,1.03\n",
              D3_FMT.format(y=2024): tre(2024), D3_FMT.format(y=2025): tre(2025), D3_FMT.format(y=2026): b"Date,5 YR,10 YR\n10/16/2026,1.0,2.0\n",
              D5_PATH: b'"Unique Identifier: ","H10/H10/JRXWTFB_N.M"\n2006-01,100.0\n', D6_PATH: b'"Unique Identifier: ","H10/H10/JRXWTFB_N.B"\n2006-01-02,100.0\n',
              WB_PATH: _wb(["Gold"], ["($/troy oz)"], [["2030M01", 2000.0]])}

    class Router(FakeNet):
        def __call__(self, host, target, headers, timeout, cap):
            self.calls.append((self.clock.t, host, target, dict(headers)))
            return 200, bodies[target]
    tmp = _tmp()
    net = Router(clock, [])
    fe, _ = _fetcher(net, clock, tmp=tmp)
    with fe:
        n1 = fetch_all(fe, 2026, say=lambda *_: None)
    log1 = read_table(fe.log_path, LOG_COLS)
    net2 = Router(clock, [])
    fe2, _ = _fetcher(net2, clock, tmp=tmp)
    with fe2:
        n2 = fetch_all(fe2, 2026, say=lambda *_: None)
    _row(r, "a full fetch makes 8 requests, all logged as saved", n1 == 8 and len(log1) == 8 and all(x[6] == "saved" and x[3] == "200" for x in log1), "n=%d log=%d" % (n1, len(log1)))
    _row(r, "the next fetch makes 4 (D1, the current-year D3, D5, D6); D2, D4 and complete past years come from the cache", n2 == 4, "n=%d" % n2)
    _row(r, "the saved vintages carry the date and 8 hex digits of the sha256", all(VN_RX.fullmatch(v["name"]) for v in list_vintages(fe.cache)) and len(list_vintages(fe.cache)) == 8)
    import inspect
    src = inspect.getsource(real_opener)
    _row(r, "the only HTTP verb is GET and no redirect is followed", 'conn.request("GET"' in src and "POST" not in src and "Location" not in src)
    return r


def g26():
    r = []
    res = syn_build("changes", extra=3)
    P = res["P"]
    _row(r, "the cache holds later months than the decision end", max(res["inputs"]["gold"]) > SYN_CFG["end"], max(res["inputs"]["gold"]))
    _row(r, "the decision sample ends at the registered month", P.months[-1] == SYN_CFG["end"] and P.cmonths[-1] == SYN_CFG["end"], P.months[-1])
    row = [x for x in res["A"]["results"] if x["object_id"] == "P1"][0]
    _row(r, "results.csv sample_end is the registered month", row["sample_end"] == SYN_CFG["end"], row["sample_end"])
    return r


def _read_all(d):
    out = {}
    for nm in sorted(os.listdir(d)):
        with open(os.path.join(d, nm), "rb") as fh:
            out[nm] = fh.read()
    return out


def g27():
    r = []
    a = syn_build("changes")
    inp = synth_inputs(SYN_CFG)
    out2, loc2 = _tmp(), _tmp()
    b = build("n/a", out2, cfg=SYN_CFG, inputs=inp, local_dir=loc2)
    fa, fb = _read_all(a["out_dir"]), _read_all(out2)
    time.sleep(1.1)
    out3, loc3 = _tmp(), _tmp()
    build("n/a", out3, cfg=SYN_CFG, inputs=synth_inputs(SYN_CFG), local_dir=loc3)
    fc = _read_all(out3)
    _row(r, "two builds on the same inputs give identical bytes (%d files)" % len(fa), fa == fb and fb == fc, str([k for k in fa if fa[k] != fc.get(k)][:2]))
    return r


def g28():
    r = []
    X, iid, ar = sim_fixture()
    cv = p1_cv(248, 12)
    s_iid, s_ar = null_size(X, iid, ar, 12, cv)
    _row(r, "P1 rejection rate at nominal 0.05 (iid y) is at most 0.065", s_iid <= 0.065, "%.4f" % s_iid)
    _row(r, "P1 rejection rate at nominal 0.05 (AR(0.2) y) is at most 0.065", s_ar <= 0.065, "%.4f" % s_ar)
    rs = np.random.RandomState(3)
    Xs = X
    ok = True
    for _ in range(3):
        y = rs.randn(248)
        b, se = t_hac_batch(Xs, y[None, :], 12)
        fp = fit(y, Xs, 12)
        ok &= abs(b[0] - fp["beta"][1]) < 1e-12 and abs(se[0] - fp["se_hac"][1]) < 1e-12
    _row(r, "the vectorised t statistic equals the explicit fit", ok)
    return r


def g29():
    r = []
    rs = np.random.RandomState(29)
    n = 80
    X0 = np.column_stack([np.ones(n), rs.randn(n), rs.randn(n)])
    y = X0 @ np.array([0.0, -0.1, 0.1]) + (X0 * (np.arange(n) >= 40)[:, None]) @ np.array([0.0, 0.4, 0.0]) + 0.4 * rs.randn(n)
    cands = list(range(12, 69))
    for extra in (None, (np.arange(n) == 30).astype(float)[:, None]):
        W = scan(y, X0, extra, cands, 12)[0][0]
        ref = scan_reference(y, X0, extra, cands, 12)
        d = float((np.abs(W - ref) / np.abs(ref)).max())
        _row(r, "vectorised sup-Wald equals the explicit-loop reference at every candidate (%s)" % ("no dummy" if extra is None else "with a dummy"), d < 1e-9, "max rel diff %.2e" % d)
    return r


def g30():
    r = []
    res = syn_build("changes", extra=3)
    P, inp = res["P"], res["inputs"]
    _row(r, "joined first and last months equal the registered ones", P.months[0] == SYN_CFG["first_level"] and P.months[-1] == SYN_CFG["end"])
    ok = all(abs(P.g[P.months.index(m)] - math.log(inp["gold"][m])) < 1e-12 for m in ("2030-01", "2033-07", "2042-09"))
    _row(r, "gold is joined on its own YYYY-MM key", ok)
    b = res["A"]["p1"]["b"]
    _row(r, "a known same-month slope (-0.15) is recovered", abs(b - (-0.15)) < 0.07, "b=%.4f" % b)
    c = res["A"]["p1"]["c"]
    _row(r, "and the dollar elasticity (-0.8)", abs(c - (-0.8)) < 0.5, "c=%.4f" % c)
    return r


GUARDS = [
    ("G1", "hac_lag_floor", g01, [["g1_lag_rule"]]),
    ("G2", "hac_formula", g02, [["g2_weights_L"]]),
    ("G3", "pct_exact", g03, [["g3_pct_exact_lin"]]),
    ("G4", "fixed_b_cv", g04, [["g4_z196"], ["g4_old_cv"], ["g4_band_196"]]),
    ("G5", "verdict_regions", g05, [["g5_overlap"]]),
    ("G6", "andrews_table", g06, [["g6_chi2_7_81"]]),
    ("G7", "trim_ranges", g07, [["g7_trim_levels_T"], ["g7_ceil_off_by_one"]]),
    ("G8", "no_2026_break", g08, [["g8_cands_to_n_minus_1"]]),
    ("G9", "bai_interval", g09, [["g9_anchor_7_7"], ["g9_pointwise"], ["g9_clipped_width"]]),
    ("G10", "break_estimator", g10, [["g10_first_wald_over_chi2"]]),
    ("G11", "eg_critical", g11, [["g11_N2"], ["g11_fullsample_gate"]]),
    ("G12", "eg_behaviour", g12, [["g12_adf_on_levels"]]),
    ("G13", "levels_suppressed", g13, [["g13_slope_regardless"]]),
    ("G14", "seam_adjust", g14, [["g14_le_seam"], ["g14_whole_month"], ["g14_sign_flip"]]),
    ("G15", "two_digit_year", g15, [["g15_naive_year"]]),
    ("G16", "dollar_base", g16, [["g16_base_label"]]),
    ("G17", "gold_column", g17, [["g17_col_off_by_one"]]),
    ("G18", "allowlist", g18, [["g18_add_ln_gold"], ["g18_add_n_excl_zero"], ["g18_add_resid_last"]]),
    ("G19", "leak_scan", g19, [["g19_residual_path_in_repo"], ["g19_beta_4dp"]]),
    ("G20", "no_ledger", g20, [["g20_tonnes_regressor"]]),
    ("G21", "registry", g21, [["g21_D10"]]),
    ("G22", "block_bootstrap", g22, [["g22_block_len_1"]]),
    ("G23", "cache_outside_repo", g23, [["g23_accept_repo_cache"]]),
    ("G24", "stop_latch", g24, [["g24_skip_latch_403"], ["g24_fetch_with_stop"]]),
    ("G25", "http_hygiene", g25, [["g25_fred_allowed"], ["g25_gap_4s"], ["g25_13th_request"]]),
    ("G26", "end_month", g26, [["g26_end_from_latest"]]),
    ("G27", "byte_identical", g27, [["g27_timestamp"]]),
    ("G28", "null_size", g28, [["g28_z196"]]),
    ("G29", "supwald_stat", g29, [["g29_hac_restricted"], ["g29_cand_shift"]]),
    ("G30", "month_alignment", g30, [["g30_gold_shift"]]),
]


def run_guard(fn):
    try:
        return fn()
    except Exception as e:                                    # a guard that crashes has noticed the mutant (or a bug: the plain run shows which)
        return [("guard ran to completion", False, "%s: %s" % (type(e).__name__, e))]


def selftest(mutants=False):
    t0 = time.time()
    bad_guards = 0
    for gid, name, fn, _ in GUARDS:
        res = run_guard(fn)
        fails = [x for x in res if not x[1]]
        real = [x for x in res if not x[0].startswith("info:")]
        print("%-4s %-18s %s  (%d checks)" % (gid, name, "PASS" if not fails else "FAIL", len(real)))
        for nm, ok_, detail in res:
            if nm.startswith("info:"):
                print("       %s %s" % (nm, detail))
            elif not ok_:
                print("       FAIL  %s   <- %s" % (nm, detail))
        bad_guards += bool(fails)
    print("selftest: %d guards PASS, %d FAIL, %.1f s" % (len(GUARDS) - bad_guards, bad_guards, time.time() - t0))
    caught_n = 0
    if mutants:
        print("== mutants (each is applied in memory; the guard must then FAIL)")
        for gid, name, fn, variants in GUARDS:
            allc, first = True, ""
            for v in variants:
                with mutant(*v):
                    res = run_guard(fn)
                fails = [x for x in res if not x[1]]
                if not fails:
                    allc = False
                elif not first:
                    first = "%s: %s" % (fails[0][0], fails[0][2])
                print("   %-4s %-26s %s%s" % (gid, "+".join(v), "caught" if fails else "NOT CAUGHT", ("   <- " + fails[0][0] + (" [" + str(fails[0][2])[:90] + "]" if fails[0][2] else "")) if fails else ""))
            caught_n += allc
        print("selftest --mutants: %d of %d mutants caught (%d mutant variants), %.1f s" % (caught_n, len(GUARDS), sum(len(g[3]) for g in GUARDS), time.time() - t0))
    return 0 if (bad_guards == 0 and (not mutants or caught_n == len(GUARDS))) else 1


# ----------------------------------------------------------------------------------------------------------------------------------
# command line
# ----------------------------------------------------------------------------------------------------------------------------------
def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    sub = ap.add_subparsers(dest="cmd", required=True)
    pf = sub.add_parser("fetch", help="download the cached files (the only network command)")
    pf.add_argument("--cache", default=os.environ.get("GOLD_RY_CACHE") or CACHE_DEFAULT)
    pf.add_argument("--out", default=OUT_DEFAULT, help="where fetch_log.csv is kept")
    pf.add_argument("--sleep", type=float, default=MIN_SLEEP)
    pf.add_argument("--max-requests", type=int, default=MAX_REQUESTS)
    pb = sub.add_parser("build", help="offline: read the cache and write every output")
    pb.add_argument("--cache", default=os.environ.get("GOLD_RY_CACHE") or CACHE_DEFAULT)
    pb.add_argument("--out", default=OUT_DEFAULT)
    ps = sub.add_parser("selftest", help="synthetic data only; --mutants applies every named mutant")
    ps.add_argument("--mutants", action="store_true")
    a = ap.parse_args(argv)
    if a.cmd == "selftest":
        return selftest(mutants=a.mutants)
    try:
        if a.cmd == "build":
            res = build(a.cache, a.out)
            print("\n".join(report(res)))
            bad = [c for c in res["checks"] if c["status"] == "FAIL"]
            print("\nwrote %s in %s; local-only outputs in %s" % (", ".join(sorted(n for n in ALLOWED_FILES if n not in ("README.md", "SOURCES.md"))), tilde(a.out),
                                                                  tilde(os.path.join(os.path.realpath(os.path.expanduser(a.cache)), "local_outputs"))))
            return 1 if bad or res["final"] else 0
        today = dt.datetime.now(dt.timezone.utc).date()
        with Fetcher(a.cache, a.out, sleep=a.sleep, max_requests=a.max_requests) as fe:
            fetch_all(fe, today.year)
        return 0
    except Latched as e:
        print("STOP: %s" % e, file=sys.stderr)
        return 3
    except SocketFault as e:
        print("socket fault or server error (%s): the invocation ends; nothing was latched and nothing is retried" % e, file=sys.stderr)
        return 4
    except MaxRequests as e:
        print("stopped: %s" % e)
        return 0
    except Refused as e:
        print("refused: %s" % e, file=sys.stderr)
        return 5
    except DataError as e:
        print("STOP (data): %s" % e, file=sys.stderr)
        return 2


if __name__ == "__main__":
    sys.exit(main())
