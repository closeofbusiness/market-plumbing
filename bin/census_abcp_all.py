#!/usr/bin/env python3
# DEPRECATED 24 Aug 2026 (C-059) — category filter: MISSED ~$3.1bn of the same programmes filed as Non-Financial Company CP.
# Use bin/census_nmfp3_all_positions.py (no name filter, no category filter) and aggregate locally.
"""ENUMERATE every ABCP position US money funds hold, from a full N-MFP3 census (D8b, 24 Aug 2026).

Supersedes the name-matching approach in bin/census_nmfp3.py, which could only find programmes we had
already guessed — it covered 41% of MMF-held ABCP (C-059). This script matches on
investmentCategory == "Asset Backed Commercial Paper" and aggregates by normalised issuer, so the
universe defines itself. Classification of issuer -> sponsor/type is a SEPARATE, evidence-based step
(free routes only: Moody's activity notes mirrored on Yahoo, Morningstar DBRS, Fitch scorecard,
sponsor sites, EDGAR credit-agreement exhibits).

  bin/census_abcp_all.py      # edit FILING_MONTH below; ~325 filings, ~8 min
Writes abcp_all_issuers_<month>.csv in the CWD. Requires form.idx for the quarter in the CWD:
  curl -A "<UA>" -o form_q3.idx https://www.sec.gov/Archives/edgar/full-index/2026/QTR3/form.idx
"""
import re,json,time,urllib.request,ssl,csv,collections
import os
if not os.environ.get("SEC_UA"): raise SystemExit('Set SEC_UA first, e.g. export SEC_UA="Your Name you@example.com" -- SEC asks automated requests to name their sender (README, "Checking the work").')
UA={"User-Agent":os.environ["SEC_UA"],"Accept-Encoding":"identity"}
CTX=ssl.create_default_context()
def get(u,t=60):
    for a in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t,context=CTX).read()
        except Exception:
            if a==2: raise
            time.sleep(2+2*a)
lines=[l for l in open('form_q3.idx',encoding='latin-1') if l.startswith('N-MFP3 ')]
targets=[]
for l in lines:
    m=re.search(r'(\d{4}-\d{2}-\d{2})\s+(edgar/data/\d+/\S+)\.txt',l)
    if m and m.group(1).startswith('2026-08'): targets.append(m.group(2))
print("filings:",len(targets),flush=True)
rows=[]; errs=0
for i,path in enumerate(targets):
    cik=path.split('/')[2]; acc=path.split('/')[3].replace('-','')
    base=f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}"
    try:
        idx=json.loads(get(base+"/index.json"))
        xmls=[f['name'] for f in idx['directory']['item'] if f['name'].endswith('.xml')]
        doc=next((x for x in xmls if 'primary' in x.lower()), xmls[0] if xmls else None)
        x=get(base+"/"+doc).decode('utf-8','ignore')
    except Exception:
        errs+=1; time.sleep(0.3); continue
    for blk in re.split(r'<(?:\w+:)?scheduleOfPortfolioSecuritiesInfo>',x)[1:]:
        cat=re.search(r'<(?:\w+:)?investmentCategory>(.*?)</',blk)
        if not cat or 'Asset Backed Commercial Paper' not in cat.group(1): continue
        iss=re.search(r'<(?:\w+:)?nameOfIssuer>(.*?)</',blk)
        val=re.search(r'<(?:\w+:)?excludingValueOfAnySponsorSupport>(.*?)</',blk)
        if not iss: continue
        rows.append({'issuer':iss.group(1),'value':float(val.group(1)) if val else 0.0,'cik':cik})
    if i%50==0: print(f"{i}/{len(targets)} abcp_positions={len(rows)} errs={errs}",flush=True)
    time.sleep(0.12)
# normalise issuer names for aggregation
def norm(n):
    s=n.upper()
    s=re.sub(r'\b(LLC|L\.L\.C\.|LTD|LIMITED|INC|CORP(ORATION)?|CO|COMPANY|PLC|DAC|S\.?A\.?|TRUST|FUNDING|FINANCE|CAPITAL)\b',' ',s)
    s=re.sub(r'SERIES\s+[IVX0-9]+',' ',s); s=re.sub(r'[^A-Z ]',' ',s); s=re.sub(r'\s+',' ',s).strip()
    return s
agg=collections.defaultdict(float); raw=collections.defaultdict(set)
for r in rows: agg[norm(r['issuer'])]+=r['value']; raw[norm(r['issuer'])].add(r['issuer'])
with open('abcp_all_issuers_aug2026.csv','w',newline='') as f:
    w=csv.writer(f); w.writerow(['issuer_normalised','value_usd','n_name_variants','example_name'])
    for k,v in sorted(agg.items(),key=lambda x:-x[1]): w.writerow([k,round(v,2),len(raw[k]),sorted(raw[k])[0]])
tot=sum(agg.values())
print(f"DONE positions={len(rows)} errs={errs} distinct={len(agg)} TOTAL ABCP=${tot/1e9:,.1f}bn",flush=True)
for k,v in sorted(agg.items(),key=lambda x:-x[1])[:45]: print(f"  {v/1e9:7.2f}bn  {k[:52]:52s} {sorted(raw[k])[0][:44]}")
