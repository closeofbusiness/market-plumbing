#!/usr/bin/env python3
"""Fetch the Z.1 fund-sector Treasury tables that bin/nport_treasury_duration.py reconciles against. Stdlib only.

  python3 bin/nport_fetch_z1.py [--out data/vintages/z1_fund_tsy_20260911] [--release 20260911]
  python3 bin/nport_fetch_z1.py --list [--save-zip PATH]      (list the S124 tables in the release; write nothing under --out)
  python3 bin/nport_fetch_z1.py --from-zip PATH               (use a copy of the release zip you already hold; no network)

What it does. One HTTPS request to www.federalreserve.gov for the release's bulk CSV package
(https://www.federalreserve.gov/releases/z1/<release>/z1_csv_files.zip, the route bin/build_closure_2026Q2.py uses),
then extracts four tables and their data dictionaries from it:
  S124_1_s    levels, quarterly       S124_1_t_tu   transactions (unadjusted flows)
  S124_2_s    levels, quarterly       S124_2_t_tu   transactions (unadjusted flows)
The S.124.3 table (the ETF row) is NOT fetched here: it is read from the committed data/vintages/z1_etf1_2026Q2/.
Which sector each of S.124.1 and S.124.2 carries is recorded by the series codes the builder asks for, and the builder
checks each code against the data dictionary text; this script only moves bytes.

Rules it keeps (CLAUDE.md, "SEC requests carry a declared contact"): the host is www.federalreserve.gov and nothing else
(the script refuses any other host); the User-Agent is the neutral research string with NO address; one request, no retries
in a loop, and nothing at all is sent if every file is already on disk (unless --force).

Provenance. Writes z1_provenance.csv (key,value) in --out: release, URL, the release zip's byte count and sha256, and the
sha256 and byte count of every extracted file. No wall-clock time is written, so a re-run on the same release is byte-identical.
The tables are Federal Reserve Board statistical releases (public domain); they are committed, unlike the SEC zips.
"""
import argparse, csv, hashlib, io, os, sys, urllib.parse, urllib.request, zipfile

HOST = "www.federalreserve.gov"
UA = "Mozilla/5.0 (compatible; ThirdDerivativeResearch/1.0; non-commercial research)"
URL = "https://" + HOST + "/releases/z1/{release}/z1_csv_files.zip"
RELEASE = "20260911"
TABLES = ("S124_1_s", "S124_1_t_tu", "S124_2_s", "S124_2_t_tu")
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DEFAULT_OUT = os.path.join(ROOT, "data", "vintages", "z1_fund_tsy_20260911")


def sha256_bytes(b):
    return hashlib.sha256(b).hexdigest()


def fetch_zip(release):
    url = URL.format(release=release)
    if urllib.parse.urlparse(url).hostname != HOST:
        raise SystemExit(f"refusing: {url} is not on {HOST}")
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=300) as r:
        final = r.geturl()                     # urllib follows redirects: the host is checked again on where it ended up
        if urllib.parse.urlparse(final).hostname != HOST:
            raise SystemExit(f"refusing: {url} redirected to {final}, which is not on {HOST}")
        return url, r.read()


def main():
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[0])
    ap.add_argument("--out", default=DEFAULT_OUT)
    ap.add_argument("--release", default=RELEASE)
    ap.add_argument("--from-zip", help="read this local copy of the release zip instead of fetching")
    ap.add_argument("--save-zip", help="also write the fetched release zip here (keep it outside the repository)")
    ap.add_argument("--list", action="store_true", help="print the S124 members of the release and stop")
    ap.add_argument("--force", action="store_true", help="fetch even if every output file is already present")
    a = ap.parse_args()

    want = [f"{t}.csv" for t in TABLES] + [f"{t}.txt" for t in TABLES] + ["z1_provenance.csv"]
    if not a.list and not a.force and not a.from_zip and all(os.path.exists(os.path.join(a.out, n)) for n in want):
        print(f"all {len(want)} files already in {a.out}; nothing fetched (use --force to re-fetch)")
        return 0

    if a.from_zip:
        raw = open(a.from_zip, "rb").read()
        url = "local file " + os.path.basename(a.from_zip)
    else:
        url, raw = fetch_zip(a.release)
    if a.save_zip:
        with open(a.save_zip, "wb") as fh:
            fh.write(raw)
    zsha = sha256_bytes(raw)
    z = zipfile.ZipFile(io.BytesIO(raw))
    names = z.namelist()
    if a.list:
        print(f"{url}  {len(raw):,} bytes  sha256 {zsha}")
        for n in sorted(names):
            if "S124" in n.upper() or "S123" in n.upper() or "S125" in n.upper():
                print("  ", n, z.getinfo(n).file_size)
        return 0

    members = {}
    for t in TABLES:
        for sub, ext in (("csv", "csv"), ("data_dictionary", "txt")):
            m = f"{sub}/{t}.{ext}"
            if m not in names:
                raise SystemExit(f"{m} not in the release zip; run with --list to see the S124 members")
            members[f"{t}.{ext}"] = z.read(m)

    os.makedirs(a.out, exist_ok=True)
    rows = [("release", a.release), ("url", URL.format(release=a.release)),
            ("zip_bytes", len(raw)), ("zip_sha256", zsha), ("user_agent_has_address", "no")]
    for name in sorted(members):
        with open(os.path.join(a.out, name), "wb") as fh:
            fh.write(members[name])
        rows.append((f"file:{name}:bytes", len(members[name])))
        rows.append((f"file:{name}:sha256", sha256_bytes(members[name])))
    with open(os.path.join(a.out, "z1_provenance.csv"), "w", newline="", encoding="utf-8") as fh:
        w = csv.writer(fh, lineterminator="\n")
        w.writerow(["key", "value"])
        w.writerows(rows)
    print(f"{url}: {len(raw):,} bytes, sha256 {zsha}")
    print(f"wrote {len(members)} files + z1_provenance.csv to {a.out}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
