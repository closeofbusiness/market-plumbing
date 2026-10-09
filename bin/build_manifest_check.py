#!/usr/bin/env python3
"""Check data/THIRD_PARTY_MANIFEST.tsv against the files on disk. Reports; never rewrites the manifest.

Why this exists: the manifest (path, source_url, fetch_date, sha256, size_bytes, reason) was built by hand on 24-27 Sep
2026 and no script regenerates it (grep finds its name only in _research/2026-09-24-Migration-Record.md). On 9 Oct 2026
14 of the 64 paths then present no longer matched their recorded sha256 and size: the series caches that bin/pull_series.py
overwrites on every run ("disposable cache", its docstring says), so a per-file hash on a cache can never stay valid.
This script makes that visible instead of leaving it to be rediscovered, and separates the two cases:

  CACHE DRIFT   the row's reason says it is a series cache: a mismatch is expected after any pull_series.py run.
                Decide per row whether the sha is worth keeping; the reason column is not touched here.
  CHANGED       any other row (a PDF, an extract, a table): the file differs from what was recorded. Investigate.
  ABSENT        the path is not on disk (not committed, gitignored, or removed). Normal for withheld files.

Usage (from anywhere):
  python3 bin/build_manifest_check.py            summary plus every non-matching row
  python3 bin/build_manifest_check.py --all      also list the rows that match
  python3 bin/build_manifest_check.py --strict   exit 1 if any CHANGED row exists (default: exit 0, as the other gates do)
  python3 bin/build_manifest_check.py --root DIR check another working copy of the repo (e.g. one that holds the gitignored files)
Reads only; writes nothing. Standard library only.
"""
import csv
import hashlib
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def sha256_of(path):
    h = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def main(argv):
    show_all = "--all" in argv
    strict = "--strict" in argv
    root = ROOT
    if "--root" in argv:
        root = os.path.abspath(argv[argv.index("--root") + 1])
    manifest = os.path.join(root, "data", "THIRD_PARTY_MANIFEST.tsv")
    if not os.path.isfile(manifest):
        print("manifest not found:", manifest)
        return 0
    with open(manifest, newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f, delimiter="\t"))
    counts = {"MATCH": 0, "CACHE DRIFT": 0, "CHANGED": 0, "ABSENT": 0}
    lines = []
    for r in rows:
        rel = r["path"]
        p = os.path.join(root, rel)
        reason = r.get("reason", "")
        if not os.path.isfile(p):
            state, why = "ABSENT", ""
        else:
            size = os.path.getsize(p)
            sha = sha256_of(p)
            bad = []
            if str(size) != r["size_bytes"].strip():
                bad.append("size %s -> %d" % (r["size_bytes"].strip(), size))
            if sha != r["sha256"].strip():
                bad.append("sha256 differs")
            if not bad:
                state, why = "MATCH", ""
            else:
                state = "CACHE DRIFT" if "series cache" in reason else "CHANGED"
                why = "; ".join(bad)
        counts[state] += 1
        if state != "MATCH" or show_all:
            lines.append((state, "  %-11s %s%s" % (state, rel, ("   (" + why + ")") if why else "")))
    order = {"CHANGED": 0, "CACHE DRIFT": 1, "ABSENT": 2, "MATCH": 3}
    for _, ln in sorted(lines, key=lambda t: (order[t[0]], t[1])):
        print(ln)
    present = counts["MATCH"] + counts["CACHE DRIFT"] + counts["CHANGED"]
    print("\nmanifest rows: %d | present on disk: %d | match: %d | cache drift: %d | changed: %d | absent: %d" % (
        len(rows), present, counts["MATCH"], counts["CACHE DRIFT"], counts["CHANGED"], counts["ABSENT"]))
    if counts["CACHE DRIFT"] or counts["CHANGED"]:
        print("The manifest is a snapshot, not a live index. Nothing was rewritten; the reason column is the ruling and is untouched.")
    return 1 if (strict and counts["CHANGED"]) else 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
