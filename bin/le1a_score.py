#!/usr/bin/env python3
"""Score LE1-A (the 5 Nov 2026 live-event repo test) from one OFR vintage. Offline: reads files only.

  python3 bin/le1a_score.py --vintage YYYYMMDD            # the scored read; refuses before the gate
  python3 bin/le1a_score.py --vintage 20261103 --selftest # pre-event dry run: scores each baseline day as if it were t*

The vintage is fetched first, by the supervisor, with `python3 bin/term_repo_turns.py fetch --vintage YYYYMMDD`.
The rule is the LE1-A block in _research/2026-11-06-Live-Event-5-Nov-Repo-Prereg.md; its SHA-256 is checked
before anything is read. Arithmetic is exact (fractions from the file's text).
"""
import argparse, datetime as dt, hashlib, json, os, re, sys
from fractions import Fraction as F

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PREREG = os.path.join(ROOT, "_research", "2026-11-06-Live-Event-5-Nov-Repo-Prereg.md")
BLOCK_SHA = "bc39ff240caa0eac796fbed12075ea68ae1f1dde30ee814a1ef884ec6011e1ca"
GATE = dt.datetime(2026, 11, 10, 20, 0, tzinfo=dt.timezone.utc)
TSTAR = dt.date(2026, 11, 5)
BASE_VINTAGE = "20261103"
HI, LO = 9, 3   # ABOVE if S > 9, BELOW if S < 3


def block():
    text = open(PREREG, encoding="utf-8").read()
    sec = text.split("## Amendment LE1-A", 1)[1]
    m = re.search(r"```\n(LE1-A\|.*?\n)```", sec, re.S)
    b = m.group(1).encode("utf-8")
    if hashlib.sha256(b).hexdigest() != BLOCK_SHA:
        sys.exit("STOP: LE1-A block sha mismatch; the rule changed after registration")
    line = [l for l in m.group(1).splitlines() if l.startswith("BASELINE|")][0]
    dates = re.search(r"Dates: (.*)$", line).group(1).split(",")
    return [dt.date.fromisoformat(d.strip()) for d in dates]


def series(vdir, mn):
    obj = json.loads(open(os.path.join(vdir, mn + ".json"), encoding="utf-8").read(), parse_float=str, parse_int=str)
    return {dt.date.fromisoformat(d): (None if v is None else F(v)) for d, v in obj}


def s_bp(b27, oo, d):
    if b27.get(d) is None or oo.get(d) is None:
        return None
    return 100 * (b27[d] - oo[d])


def label(s):
    if s is None:
        return "NO READING"
    return "ABOVE" if s > HI else ("BELOW" if s < LO else "INSIDE")


def fmt(x):
    return "null" if x is None else ("%.2f" % float(x))


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--vintage", required=True)
    ap.add_argument("--selftest", action="store_true")
    a = ap.parse_args()
    vdir = os.path.join(ROOT, "data", "vintages", "ofr_repo", a.vintage)
    bdir = os.path.join(ROOT, "data", "vintages", "ofr_repo", BASE_VINTAGE)   # the block fixes B on vintage 20261103
    base = block()
    b27, oo = series(vdir, "REPO-TRIV1_AR_B27-P"), series(vdir, "REPO-TRIV1_AR_OO-P")
    bb27, boo = series(bdir, "REPO-TRIV1_AR_B27-P"), series(bdir, "REPO-TRIV1_AR_OO-P")
    bs = [s_bp(bb27, boo, d) for d in base]
    if any(x is None for x in bs):
        sys.exit("STOP: a baseline day is null in vintage %s" % BASE_VINTAGE)
    if (lo_hi := (min(bs), max(bs))) != (LO, HI):
        sys.exit("STOP: baseline range %s-%s differs from the registered 3-9" % tuple(fmt(x) for x in lo_hi))
    lo, hi = min(bs), max(bs)
    print("baseline (vintage %s) n=%d  min %s  max %s  (registered 3 to 9)" % (BASE_VINTAGE, len(bs), fmt(lo), fmt(hi)))
    if a.selftest:
        bad = [(d, fmt(x), label(x)) for d, x in zip(base, bs) if label(x) != "INSIDE"]
        print("selftest: every baseline day labels INSIDE" if not bad else "selftest FAIL: %r" % bad)
        if TSTAR in b27 or TSTAR in oo:
            sys.exit("STOP: this vintage already holds t*; use the scored read")
        return 0 if not bad else 1
    if dt.datetime.now(dt.timezone.utc) < GATE:
        sys.exit("refused: before the gate %s" % GATE.isoformat())
    if TSTAR not in b27 or TSTAR not in oo:   # both legs must carry the date; a null value on either is NO READING
        sys.exit("NOT YET: vintage %s does not hold %s; fetch a later vintage" % (a.vintage, TSTAR))
    s = s_bp(b27, oo, TSTAR)
    nxt = TSTAR + dt.timedelta(days=1)
    print("t*=%s  B27 %s  OO %s  S %s bp  ->  LABEL %s" % (TSTAR, fmt(b27.get(TSTAR)), fmt(oo.get(TSTAR)), fmt(s), label(s)))
    print("described: S on %s = %s bp" % (nxt, fmt(s_bp(b27, oo, nxt))))
    print("described later: LE1's withdrawn median and band need its control days (to 2026-11-23); not computable on this read")
    return 0


if __name__ == "__main__":
    sys.exit(main())
