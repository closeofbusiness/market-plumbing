#!/usr/bin/env python3
"""Run every CORRECTIONS.md ban pattern against a published HTML page.

The published "What Holds the Market Up" page lives OUTSIDE bin/check.sh --all, which scans only *.md.
This is the pre-republish check the page promises.

Method (validated 23 Sep): strip tags per line but KEEP line breaks.
  - Raw lines miss phrases split by tags, e.g. "13x the <span>$86.2bn</span>".
  - Flattening the whole page lets a ".*" pattern leap across sections (C-001 false positive).
  - Attribute text that readers get (aria-label, alt, title) is scanned as its own entry on its line.
    Stripping tags deletes it, and a retired phrase lived only in a chart's aria-label (C-120, 24 Sep).
Exit code is always 0 -- read the output line, never $?.  Usage: bin/check_page.py <page.html>
"""
import io, re, sys, html, warnings
warnings.filterwarnings('ignore')
if len(sys.argv) != 2:
    print("usage: bin/check_page.py <page.html>"); sys.exit(0)
C = io.open('CORRECTIONS.md', encoding='utf-8').read()
pats = [l.split('\t', 1) for l in re.search(r'```banned\n(.*?)\n```', C, re.S).group(1).split('\n') if '\t' in l]
raw = re.sub(r'(?is)<style.*?</style>', '', io.open(sys.argv[1], encoding='utf-8').read())
ATTR = re.compile(r'''\b(?:aria-label|alt|title)\s*=\s*(?:"([^"]*)"|'([^']*)')''', re.I)
entries = []  # (line number, text): visible text, then each reader-facing attribute separately
for n, l in enumerate(raw.split('\n'), 1):
    entries.append((n, html.unescape(re.sub(r'<[^>]+>', '', l))))
    entries += [(n, html.unescape(a if a is not None else b)) for a, b in ATTR.findall(l)]
hits = []
for cid, rx in pats:
    try: r = re.compile(rx, re.I)
    except re.error: continue
    for i, l in entries:
        m = r.search(l)
        if m: hits.append((cid, i, m.group(0)[:80]))
for cid, i, g in hits:
    print("  [%s] line %d: %r" % (cid, i, g))
if hits:
    print("⚠  %d killed claim(s) on the page, %d patterns run. Do NOT republish until fixed." % (len(hits), len(pats)))
else:
    print("✓ page clean against all %d ban patterns." % len(pats))
