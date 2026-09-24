#!/usr/bin/env python3
"""Find vault documents that cite a SESSION SCRATCHPAD path, and report which are gone.

Why this exists: session scratchpads are swept without warning. On 21 Sep 2026, 33 of the 35
scratchpad paths cited across this vault had already vanished — including deliverables named in
P1, P2a, P2c, ATT0, F1, I1b, Oracle and N2c. Those documents survived only because they ALSO
cited a durable path under _research/, data/ or bin/.

A finding whose only cited deliverable is a scratchpad path is not reproducible. Land it in the
vault and cite that. Run this after any pass that produces tables, scripts or CSVs.

Exit code is always 0 — this reports, it does not block.
"""
import os, re, glob, sys

SCRATCH = re.compile(r"/private/tmp/claude-[^\s`),;\"']+")
VAULT   = re.compile(r"`((?:_research|data|bin)/[^`]+)`")

def main():
    docs, allrefs = {}, set()
    for f in sorted(glob.glob("*.md") + glob.glob("_research/*.md")):
        if "snapshot" in f:
            continue
        text = open(f, encoding="utf-8", errors="ignore").read()
        refs = {m.group(0).rstrip(".") for m in SCRATCH.finditer(text)}
        if not refs:
            continue
        allrefs |= refs
        dead = sorted(r for r in refs if not os.path.exists(r))
        if dead:
            durable = sorted(v for v in {m.group(1) for m in VAULT.finditer(text)} if os.path.exists(v))
            docs[f] = (dead, durable)

    gone = sorted(r for r in allrefs if not os.path.exists(r))
    print(f"-- scratchpad citations: {len(gone)} of {len(allrefs)} cited paths are GONE --")
    if not docs:
        print("  ✓ no document cites a missing scratchpad path.")
        return 0

    stranded = [f for f, (_, d) in docs.items() if not d]
    for f, (dead, durable) in docs.items():
        mark = "✗ NO DURABLE COPY" if not durable else f"✓ also cites {durable[0]}"
        print(f"  {f}  ({len(dead)} dead)  {mark}")
    print()
    if stranded:
        print(f"  ✗ {len(stranded)} document(s) cite a missing deliverable with NO vault copy —")
        print("    their working data is gone. Triage before quoting them.")
    else:
        print("  ✓ every affected document also cites a durable vault path.")
    return 0

if __name__ == "__main__":
    sys.exit(main())
