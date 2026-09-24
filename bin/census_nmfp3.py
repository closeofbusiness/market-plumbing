#!/usr/bin/env python3
# DEPRECATED 24 Aug 2026 (C-059) — name-map matching: MISSED abbreviated spellings and every unlisted programme (41% coverage).
# Use bin/census_nmfp3_all_positions.py (no name filter, no category filter) and aggregate locally.
"""Full-census of N-MFP3 filings for named ABCP conduit programmes (D8b, 24 Aug 2026).
Enumerates EVERY N-MFP3 filing in a filing month from the EDGAR form index (a full-text-search
sample is not a census - C-053), fetches each primary XML, and matches issuer names against the
verified sponsor->programme map (2026-08-24-Parcel-D8b-Conduit-Return.md).

  bin/census_nmfp3.py 2026-08     # filings filed in Aug 2026 = 31 Jul month-end data
Writes census_nmfp3_hits_<month>.csv in the CWD; copy to data/vintages/nmfp3/ and append
aggregates to data/series.tsv by hand with provenance. ~325 filings, ~7 min, SEC UA inside."""
import sys
FILING_MONTH = sys.argv[1] if len(sys.argv)>1 else "2026-08"
QTR = "QTR"+str((int(FILING_MONTH[5:7])+2)//3)
import re,json,time,urllib.request,ssl,csv,os
UA={"User-Agent":os.environ["SEC_UA"],"Accept-Encoding":"identity"}
CTX=ssl.create_default_context()
def get(u,t=60):
    for a in range(3):
        try: return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t,context=CTX).read()
        except Exception as e:
            if a==2: raise
            time.sleep(2+2*a)
# programme regexes: (group, sponsor, regex)
PATS=[
 ("securities-backed/aggregator","Nearwater",r'resolute funding|saugatuck|endeavou?r funding|aquitaine funding|regatta funding'),
 ("securities-backed/aggregator","Northcross",r'anglesea|longship|glencove|great bear funding|mainbeach|lion bay|st\.? ?lawrence funding|portsea|avalon [a-z]* ?funding'),
 ("securities-backed/aggregator","Guggenheim",r'cedar springs capital|crown point capital|ridgefield funding|great bridge capital'),
 ("securities-backed/aggregator","BenningtonStark(admin?)",r'bennington stark'),
 ("securities-backed/aggregator","BSN",r'chesham finance|halkin finance|ebury finance'),
 ("securities-backed/aggregator","20Gates",r'mountcliff'),
 ("securities-backed/aggregator","Unmapped-Overwatch",r'overwatch (bravo|alpha|charlie)?'),
 ("bank-CCP-style","JPMorgan-CCP",r'collateralized commercial paper|park avenue collateralized'),
 ("bank multi-seller","JPMorgan",r'chariot funding|falcon asset funding|jupiter securitization'),
 ("bank multi-seller","RBC",r'thunder bay funding|old line funding|bedford row'),
 ("bank multi-seller","CreditAgricole",r'atlantic asset securitization|la fayette asset|\blma s\.?a\b'),
 ("bank multi-seller","SocGen",r'\bantalis\b|barton capital'),
 ("bank multi-seller","BNP",r'matchpoint finance|starbird funding'),
 ("bank multi-seller","TD",r'cabot trail|gta funding|reliant trust'),
]
PATS=[(g,s,re.compile(p,re.I)) for g,s,p in PATS]
idx=get(f"https://www.sec.gov/Archives/edgar/full-index/{FILING_MONTH[:4]}/{QTR}/form.idx").decode('latin-1')
lines=[l for l in idx.splitlines() if l.startswith('N-MFP3 ')]
targets=[]
for l in lines:
    m=re.search(r'(\d{4}-\d{2}-\d{2})\s+(edgar/data/\d+/\S+)\.txt',l)
    if m and m.group(1).startswith(FILING_MONTH): targets.append(m.group(2))
print("filings:",len(targets),flush=True)
rows=[]; funds=0; errs=0
for i,path in enumerate(targets):
    cik=path.split('/')[2]; acc=path.split('/')[3].replace('-','')
    base=f"https://www.sec.gov/Archives/edgar/data/{cik}/{acc}"
    try:
        idx=json.loads(get(base+"/index.json"))
        xmls=[f['name'] for f in idx['directory']['item'] if f['name'].endswith('.xml')]
        doc=next((x for x in xmls if 'primary' in x.lower()), xmls[0] if xmls else None)
        if not doc: errs+=1; continue
        x=get(base+"/"+doc).decode('utf-8','ignore')
    except Exception as e:
        errs+=1; time.sleep(0.3); continue
    funds+=1
    fund=re.search(r'<(?:\w+:)?nameOfFund>(.*?)</',x) or re.search(r'<(?:\w+:)?registrantFullName>(.*?)</',x)
    fname=(fund.group(1) if fund else cik)[:80]
    rdate=re.search(r'<(?:\w+:)?reportDate>(.*?)</',x)
    rd=rdate.group(1) if rdate else ''
    # split into security blocks
    for blk in re.split(r'<(?:\w+:)?scheduleOfPortfolioSecuritiesInfo>',x)[1:]:
        iss=re.search(r'<(?:\w+:)?nameOfIssuer>(.*?)</',blk)
        if not iss: continue
        name=iss.group(1)
        for g,sp,pat in PATS:
            if pat.search(name):
                val=re.search(r'<(?:\w+:)?excludingValueOfAnySponsorSupport>(.*?)</',blk)
                cat=re.search(r'<(?:\w+:)?investmentCategory>(.*?)</',blk)
                mat=re.search(r'<(?:\w+:)?finalLegalMaturityDate>(.*?)</',blk)
                v=float(val.group(1)) if val else 0.0
                rows.append({'group':g,'sponsor':sp,'issuer':name,'value':v,'category':cat.group(1) if cat else '','maturity':mat.group(1) if mat else '','fund':fname,'report_date':rd,'cik':cik,'acc':acc})
                break
    if i%25==0: print(f"{i}/{len(targets)} funds={funds} hits={len(rows)} errs={errs}",flush=True)
    time.sleep(0.12)
with open(f'census_nmfp3_hits_{FILING_MONTH}.csv','w',newline='') as f:
    w=csv.DictWriter(f,fieldnames=['group','sponsor','issuer','value','category','maturity','fund','report_date','cik','acc']); w.writeheader(); w.writerows(rows)
print("DONE filings",len(targets),"parsed",funds,"errs",errs,"hits",len(rows),flush=True)
import collections
by=collections.defaultdict(float)
for r in rows: by[(r['group'],r['sponsor'])]+=r['value']
for k in sorted(by,key=lambda k:-by[k]): print(f"{k[0]:28s} {k[1]:22s} {by[k]/1e9:8.2f} bn")
