#!/usr/bin/env python3
"""Aggregate an all_positions_<month>.csv against the verified sponsor map from
2026-08-24-Parcel-D8b-Conduit-Return.md section 2.1 / 2.1b. Keyword-matches issuer names
(case-insensitive substring, catching spelling variants the way the definitive census is
designed to) into the 19 named programme families, then rolls them into the same
non-bank / bank / unattributed buckets used in the D8b writeup, so July and September are
computed with IDENTICAL code for a like-for-like comparison.

  bin/aggregate_nmfp3_families.py <positions.csv or .csv.gz> [...]
Input: the raw output of bin/census_nmfp3_all_positions.py, or an archived vintage in data/vintages/nmfp3/.
Check before trusting a new month: run it on the 2026-07-31 vintage too; it must print named families
49.69 (non-bank 34.66 + unattributed 15.03), Capitolis 8.83, all ABCP 101.22 — D8b section 2.1's July table.
Written 11 Sep 2026 for the 31 Aug census; the non-bank/unattributed SPLIT is one of three documented
cuts (41.8/7.9, 36.4/13.3, 34.66/15.03) — only their sum is stable, so series.tsv carries the sum.
"""
import csv, sys, collections, gzip

FAMILY_KEYWORDS = {
    'Chesham': ['chesham'],
    'Verto': ['verto'],
    'Ionic': ['ionic'],
    # Northcross's own site names these 8 programmes (2026-08-24-Parcel-D8b-Conduit-Return.md
    # section 2.1 + _research/D8b_Conduit_Scouting_Return.md P1#6) -- the sponsor's own name
    # "Northcross" never appears in N-MFP3 issuer strings.
    'Northcross': ['anglesea','longship','glencove','great bear','mainbeach','lion bay',
                   'st. lawrence','st lawrence','portsea'],
    'Concord Minutemen': ['concord minutemen'],
    'Podium': ['podium'],
    'HQLA Funding': ['hqla'],
    'Paradelle': ['paradelle'],
    # Nearwater's own name likewise never appears on issued paper; programme names per
    # _research/D8b_Conduit_Scouting_Return.md P1#1 plus "Columbia" per the D8b table's
    # "Nearwater (incl. Columbia)" label.
    'Nearwater/Columbia': ['resolute','saugatuck','endeavour','aquitaine','regatta','columbia funding'],
    'Overwatch': ['overwatch'],
    'Ridgefield+Guggenheim': ['ridgefield','cedar springs','crown point'],
    'Washington Morgan': ['washington morgan'],
    'Lexington Parker': ['lexington parker'],
    'Britannia': ['britannia'],
    'Bennington Stark': ['bennington stark'],
    'Intrepid': ['intrepid'],
    'Mackinac': ['mackinac'],
    'Alinghi': ['alinghi'],
    'Mountcliff': ['mountcliff'],
}
# classification per D8b section 2.1 / 2.1b (see doc for sourcing)
NONBANK = {'Chesham','Ionic','HQLA Funding','Northcross','Concord Minutemen','Nearwater/Columbia',
           'Ridgefield+Guggenheim','Lexington Parker','Bennington Stark','Mountcliff'}
BANK = {'Podium','Paradelle'}
UNATTRIB = {'Verto','Overwatch','Washington Morgan','Intrepid','Mackinac','Alinghi','Britannia'}

def load(path):
    with (gzip.open(path,'rt',newline='') if path.endswith('.gz') else open(path, newline='')) as f:
        return list(csv.DictReader(f))

def aggregate(rows, label):
    out = {}
    total_abcp = 0.0
    abcp_issuers = set()
    for r in rows:
        v = float(r['value'])
        if r['category'] == 'Asset Backed Commercial Paper':
            total_abcp += v
            abcp_issuers.add(r['issuer'].strip().lower())
    out['all_abcp_bn'] = total_abcp/1e9
    out['all_abcp_distinct_issuers'] = len(abcp_issuers)

    fam_totals = collections.defaultdict(float)
    fam_hits = collections.defaultdict(set)
    for r in rows:
        name = r['issuer'].lower()
        v = float(r['value'])
        for fam, kws in FAMILY_KEYWORDS.items():
            if any(kw in name for kw in kws):
                fam_totals[fam] += v
                fam_hits[fam].add(r['issuer'].strip())
    out['family_bn'] = {f: fam_totals.get(f,0.0)/1e9 for f in FAMILY_KEYWORDS}
    out['family_issuer_names'] = {f: sorted(fam_hits.get(f,[])) for f in FAMILY_KEYWORDS}

    nonbank_bn = sum(fam_totals[f] for f in NONBANK)/1e9
    bank_bn = sum(fam_totals[f] for f in BANK)/1e9
    unattrib_bn = sum(fam_totals[f] for f in UNATTRIB)/1e9
    named_total_bn = nonbank_bn+bank_bn+unattrib_bn
    capitolis_bn = (fam_totals['Ionic']+fam_totals['HQLA Funding'])/1e9

    out['nonbank_named_bn'] = nonbank_bn
    out['bank_named_bn'] = bank_bn
    out['unattributed_named_bn'] = unattrib_bn
    out['named_families_total_bn'] = named_total_bn
    out['capitolis_bn'] = capitolis_bn
    out['ionic_only_bn'] = fam_totals['Ionic']/1e9
    out['hqla_only_bn'] = fam_totals['HQLA Funding']/1e9

    print(f"=== {label}: total rows={len(rows)} ===")
    print(f"  All ABCP-categorised holdings: {out['all_abcp_bn']:.2f}bn across {out['all_abcp_distinct_issuers']} distinct issuers")
    print(f"  Named families total: {named_total_bn:.2f}bn  (non-bank {nonbank_bn:.2f} + bank {bank_bn:.2f} + unattributed {unattrib_bn:.2f})")
    print(f"  Capitolis (Ionic+HQLA): {capitolis_bn:.2f}bn  [Ionic {out['ionic_only_bn']:.2f} + HQLA {out['hqla_only_bn']:.2f}]")
    print("  Per-family ($bn):")
    for f in sorted(FAMILY_KEYWORDS, key=lambda x:-fam_totals[x]):
        print(f"    {fam_totals[f]/1e9:7.3f}  {f}  (issuer strings matched: {out['family_issuer_names'][f][:4]}{'...' if len(out['family_issuer_names'][f])>4 else ''})")
    print()
    return out

if __name__=='__main__':
    for path in sys.argv[1:]:
        rows = load(path)
        aggregate(rows, path)
