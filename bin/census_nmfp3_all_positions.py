#!/usr/bin/env python3
"""DEFINITIVE N-MFP3 census: EVERY position in EVERY filing of a month, no name filter and no
category filter (D8b, 24 Aug 2026 — written after C-059).

Two earlier attempts were each incomplete in a different direction and between them produced a FALSE
CORRECTION (C-058, retracted):
  * bin/census_nmfp3.py matched a hand-written list of programme names -> missed abbreviated spellings
    ("CHESHAM FIN" vs "CHESHAM FINANCE") and every programme we had not already thought of.
  * bin/census_abcp_all.py filtered on investmentCategory == "Asset Backed Commercial Paper" -> missed
    the ~3bn of the same programmes' paper that filers classify as Non-Financial Company CP.
This script imposes neither filter: it writes all_positions_<month>.csv (~44,500 rows for Aug 2026) and
you aggregate locally, so a matching rule can be revised without re-fetching 325 filings.

  bin/census_nmfp3_all_positions.py 2026-09   # the FILING month, required: 2026-09 = positions at 31 Aug
Needs that quarter's form index in the CWD, named form_q<N>.idx — for 2026-09 (QTR3):
  curl -A "<UA>" -o form_q3.idx https://www.sec.gov/Archives/edgar/full-index/2026/QTR3/form.idx
Writes all_positions_filed_<YYYY-MM>.csv. Aggregate it with bin/aggregate_nmfp3_families.py.
(Until 11 Sep 2026 the month was a hard-coded literal while this docstring said "edit FILING_MONTH", a
variable that did not exist. Run unedited, the script silently re-fetched the August filings.)
"""
import re,json,time,urllib.request,ssl,csv,collections,sys
import os
UA={"User-Agent":os.environ["SEC_UA"],"Accept-Encoding":"identity"}
CTX=ssl.create_default_context()
if len(sys.argv)!=2 or not re.fullmatch(r'\d{4}-(0[1-9]|1[0-2])',sys.argv[1]):
    sys.exit("usage: census_nmfp3_all_positions.py YYYY-MM   (the FILING month; 2026-09 = positions at 31 Aug 2026)")
FILED=sys.argv[1]; IDX=f"form_q{(int(FILED[5:])-1)//3+1}.idx"
def get(u,t=60):
    for a in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t,context=CTX).read()
        except Exception:
            if a==2: raise
            time.sleep(2+2*a)
lines=[l for l in open(IDX,encoding='latin-1') if l.startswith('N-MFP3 ')]
targets=[]
for l in lines:
    m=re.search(r'(\d{4}-\d{2}-\d{2})\s+(edgar/data/\d+/\S+)\.txt',l)
    if m and m.group(1).startswith(FILED): targets.append(m.group(2))
print(f"filing month {FILED} ({IDX}) filings:",len(targets),flush=True)
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
        iss=re.search(r'<(?:\w+:)?nameOfIssuer>(.*?)</',blk)
        if not iss: continue
        cat=re.search(r'<(?:\w+:)?investmentCategory>(.*?)</',blk)
        val=re.search(r'<(?:\w+:)?excludingValueOfAnySponsorSupport>(.*?)</',blk)
        rows.append({'issuer':iss.group(1),'category':cat.group(1) if cat else '','value':float(val.group(1)) if val else 0.0,'cik':cik})
    if i%50==0: print(f"{i}/{len(targets)} positions={len(rows)} errs={errs}",flush=True)
    time.sleep(0.12)
with open(f'all_positions_filed_{FILED}.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['issuer','category','value','cik']); w.writeheader(); w.writerows(rows)
print(f"DONE positions={len(rows)} errs={errs}",flush=True)
# Chesham across ALL categories
ch=[r for r in rows if 'chesham' in r['issuer'].lower()]
byc=collections.defaultdict(float)
for r in ch: byc[r['category']]+=r['value']
print("CHESHAM total across all categories: ${:,.2f}bn".format(sum(r['value'] for r in ch)/1e9))
for k,v in sorted(byc.items(),key=lambda x:-x[1]): print(f"   {v/1e9:6.2f}bn  {k}")
