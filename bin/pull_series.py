#!/usr/bin/env python3
"""Re-pull the load-bearing series from their ISSUING sources and append a dated vintage row
to data/series.tsv (append-only; never rewrite). Full histories go to data/history/<key>.csv
(disposable cache, overwritten each run). Stdlib only; works over the SMB mount.

  bin/pull_series.py            # pull everything reachable, append latest obs as vintage rows
  bin/pull_series.py --list     # show what would be pulled
  bin/pull_series.py --only ofr # subset: fiscaldata | ofr | ofr_hf | fia | dtcc | finra | fdic | sec | fred | nyfed_pd

FRED note: fred.stlouisfed.org is unreachable from the agent sandbox (curl returns 000); from a
normal terminal it works. If a FRED pull fails, the script says so and moves on — the other
sources are authoritative anyway (FRED is a mirror).
"""
import sys, json, csv, io, os, re, ssl, time, datetime, urllib.request
ROOT=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
TSV=os.path.join(ROOT,"data","series.tsv"); HIST=os.path.join(ROOT,"data","history")
UA={"User-Agent":os.environ["SEC_UA"],"Accept-Encoding":"identity"}
CTX=ssl.create_default_context(); NOW=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%dT%H:%MZ")
def get(u,t=90):
    return urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=t,context=CTX).read()
def append(rows):
    new=not os.path.exists(TSV)
    with open(TSV,"a",encoding="utf-8") as f:
        if new: f.write("pulled_at\tseries_key\tas_of\tvalue\tunit\tsource\tnote\n")
        for r in rows: f.write("\t".join(str(x) for x in r)+"\n")
def hist(key,pairs):
    os.makedirs(HIST,exist_ok=True)
    with open(os.path.join(HIST,key+".csv"),"w",encoding="utf-8") as f:
        f.write("as_of,value\n"); [f.write(f"{d},{v}\n") for d,v in pairs]

def pull_fiscaldata():
    u=("https://api.fiscaldata.treasury.gov/services/api/fiscal_service/v1/debt/mspd/mspd_table_1"
       "?filter=security_type_desc:eq:Marketable,security_class_desc:eq:Bills,record_date:gte:2005-01-01"
       "&fields=record_date,total_mil_amt&sort=record_date&page[size]=10000")
    d=json.loads(get(u))["data"]; pairs=[(r["record_date"],round(float(r["total_mil_amt"])/1000,1)) for r in d]
    hist("bills_outstanding_total_bn",pairs); a,v=pairs[-1]
    return [(NOW,"bills_outstanding_total_bn",a,v,"$bn","FiscalData MSPD Table 1, Marketable/Bills, total","month-end")]
OFR={"MMF-MMF_TOT-M":"mmf_total_investments_bn","MMF-MMF_T_TOT-M":"mmf_treasuries_bn","MMF-MMF_RP_T_TOT-M":"mmf_treasury_repo_bn",
     "MMF-MMF_RP_wFR-M":"mmf_repo_with_fed_bn","MMF-MMF_RP_wFICC-M":"mmf_repo_ficc_cleared_bn","MMF-MMF_RP_OA_TOT-M":"mmf_repo_other_collateral_bn",
     "MMF-MMF_RP_AG_TOT-M":"mmf_agency_repo_bn","MMF-MMF_AG_TOT-M":"mmf_agency_securities_bn","MMF-MMF_BRA_TOT-M":"mmf_bank_related_assets_bn","MMF-MMF_OA_TOT-M":"mmf_other_assets_bn"}
def _series(j):
    st=[j]
    while st:
        o=st.pop()
        if isinstance(o,list) and o and isinstance(o[0],list) and len(o[0])==2 and isinstance(o[0][0],str): return o
        if isinstance(o,dict): st.extend(o.values())
        elif isinstance(o,list): st.extend(o)
def pull_ofr():
    out=[]
    for m,key in OFR.items():
        ts=[(d,v) for d,v in _series(json.loads(get(f"https://data.financialresearch.gov/v1/series/full?mnemonic={m}"))) if v is not None]
        mx=max(abs(v) for d,v in ts); sc=1e-9 if mx>1e11 else (1e-3 if mx>1e5 else 1)
        pairs=[(d,round(v*sc,1)) for d,v in ts]; hist(key,pairs); a,v=pairs[-1]
        out.append((NOW,key,a,v,"$bn",f"OFR MMF Monitor API {m}","N-MFP based, month-end")); time.sleep(0.2)
    return out
def pull_fdic():
    u=("https://banks.data.fdic.gov/api/financials?filters=REPDTE:[20131231%20TO%2020991231]"
       "&fields=DEPUNINS&agg_by=REPDTE&agg_sum_fields=DEPUNINS&agg_limit=200&limit=1")
    d=json.loads(get(u))["data"]; pairs=sorted((r["data"]["REPDTE"],round(r["data"]["sum_DEPUNINS"]/1e6,1)) for r in d)
    pairs=[(f"{a[:4]}-{a[4:6]}-{a[6:]}",v) for a,v in pairs]; hist("uninsured_deposits_all_insts_bn",pairs); a,v=pairs[-1]
    return [(NOW,"uninsured_deposits_all_insts_bn",a,v,"$bn","FDIC BankFind API, DEPUNINS summed over all institutions","quarter-end; Schedule RC-O estimated uninsured")]
SEC={"Microsoft":789019,"Alphabet":1652044,"Amazon":1018724,"Meta":1326801,"Oracle":1341439,"NVIDIA":1045810}
def pull_sec():
    out=[]
    for name,cik in SEC.items():
        for c,lab in (("CashAndCashEquivalentsAtCarryingValue","cash_equivalents_bn"),("MarketableSecuritiesCurrent","marketable_securities_current_bn")):
            try: j=json.loads(get(f"https://data.sec.gov/api/xbrl/companyconcept/CIK{cik:010d}/us-gaap/{c}.json"))
            except Exception: continue
            vals=[v for v in j["units"].get("USD",[]) if v.get("form") in("10-Q","10-K")]
            if not vals: continue
            l=max(vals,key=lambda v:v["end"]); out.append((NOW,f"{name.lower()}_{lab}",l["end"],round(l["val"]/1e9,1),"$bn",f"SEC XBRL companyfacts CIK{cik} {c}",l.get("form","")))
            time.sleep(0.15)
    return out
FRED={"RRPONTSYD":("fed_on_rrp_bn",1),"WRESBAL":("reserve_balances_bn",1e-3),"WSHOBL":("fed_soma_tbills_bn",1e-3),"WLRRAFOIAL":("foreign_official_rrp_bn",1e-3),
      "ABCOMP":("abcp_outstanding_bn",1),"FINCP":("financial_cp_bn",1),"COMPOUT":("cp_total_bn",1),"LTDACBM027NBOG":("large_time_deposits_bn",1),"WRMFNS":("retail_mmf_h6_bn",1)}
def pull_fred():
    out=[]
    for fid,(key,sc) in FRED.items():
        try: t=get(f"https://fred.stlouisfed.org/graph/fredgraph.csv?id={fid}",30).decode()
        except Exception as e: print(f"  FRED {fid} unreachable ({type(e).__name__}) — use the browser route or a normal terminal"); continue
        rows=[l.split(",") for l in t.strip().split("\n")[1:]]; pairs=[(d,round(float(v)*sc,1)) for d,v in rows if v not in(".","")]
        hist(key,pairs); a,v=pairs[-1]; out.append((NOW,key,a,v,"$bn",f"FRED {fid} (mirror of Fed release)",""))
    return out
# OFR Hedge Fund Monitor (Form PF aggregates, Qualifying Hedge Funds, quarterly; same API shape, different base path).
# Added 2026-08-23 for D3 §8. "Cash collateral" per Form PF Q43 INCLUDES Treasuries and agencies — it is cash-LIKE, not cash.
HF_STRATS=["CREDIT","EQUITY","EVENT","FOF","FUTURES","MACRO","MULTI","OTHER","RV"]
OFR_HF={"FPF-ALLQHF_NAV_SUM":"hf_qhf_net_assets_bn","FPF-ALLQHF_GAV_SUM":"hf_qhf_gross_assets_bn",
        "FPF-COLLATERALTYPE_CASH_COLLATERAL_SUM":"hf_collateral_posted_cashlike_bn","FPF-COLLATERALTYPE_SECURITIES_COLLATERAL_SUM":"hf_collateral_posted_securities_bn",
        "FPF-COLLATERALTYPE_OTHER_COLLATERAL_SUM":"hf_collateral_posted_other_bn",
        "FPF-BORROW_REPO_SUM":"hf_repo_borrowing_bn","FPF-BORROW_PRIMEBROKER_SUM":"hf_prime_brokerage_borrowing_bn","FPF-BORROW_OTHERSECURED_SUM":"hf_other_secured_borrowing_bn",
        "FPF-ASSETCLASS_REPO_REVERSEREPO_SUM":"hf_reverse_repo_exposure_bn","FPF-ASSETCLASS_LTREASURY_SUM":"hf_long_treasury_exposure_bn","FPF-ASSETCLASS_STREASURY_SUM":"hf_short_treasury_exposure_bn"}
def pull_ofr_hf():
    out=[]; nav={}; rat={}
    def hf(m): return [(d,v) for d,v in _series(json.loads(get(f"https://data.financialresearch.gov/hf/v1/series/full?mnemonic={m}"))) if v is not None]
    for m,key in OFR_HF.items():
        pairs=[(d,round(v/1e9,1)) for d,v in hf(m)]; hist(key,pairs); a,v=pairs[-1]
        out.append((NOW,key,a,v,"$bn",f"OFR Hedge Fund Monitor API {m}","Form PF, qualifying hedge funds, quarter-end")); time.sleep(0.2)
    for st in HF_STRATS:
        nav[st]=dict(hf(f"FPF-STRATEGY_{st}_NAV_SUM")); rat[st]=dict(hf(f"FPF-STRATEGY_{st}_CASHRATIO_NAVWMEAN")); time.sleep(0.2)
    dates=sorted(set.intersection(*[set(nav[s]) & set(rat[s]) for s in HF_STRATS]))
    pairs=[(d,round(sum(nav[s][d]*rat[s][d]/100 for s in HF_STRATS)/1e9,1)) for d in dates]
    hist("hf_unencumbered_cash_bn",pairs); a,v=pairs[-1]
    out.append((NOW,"hf_unencumbered_cash_bn",a,v,"$bn","OFR Hedge Fund Monitor API, sum over 9 strategies of FPF-STRATEGY_*_CASHRATIO_NAVWMEAN x FPF-STRATEGY_*_NAV_SUM","derived: Form PF Q33/Q9; NAV-weighted mean ratio x strategy NAV = strategy unencumbered cash"))
    return out
# FIA CCP Tracker — public JSON API behind fia.org/fia/initial-margin-combined (added 2026-08-23, N3 return K2).
# Carries PQD item 6.1.1 (initial margin required: house net / client net / client gross, USD) for 15 derivatives
# CCPs, quarterly from Q3 2015. The Authorization value is the page-embedded key every visitor's browser sends;
# if it stops working, re-read it from the page source (function setRequestHeader). FICC is NOT in this set.
FIA_KEY="fcdb8393-c862-43b8-a6c2-f86a96f46f8a"
def _fia(u):
    h=dict(UA); h["Authorization"]=FIA_KEY; h["Accept"]="application/json"
    return json.loads(urllib.request.urlopen(urllib.request.Request(u,headers=h),timeout=60,context=CTX).read())
def pull_fia():
    import urllib.parse
    qs=[q["name"] for q in _fia("https://fiadataapi.azurewebsites.net/api/Data/GetQuarters?Dataset=QtrsList")]
    def qkey(q): a,b=q.split(); return (int(b),int(a[1]))
    tot=[]; perccp={}
    for q in sorted(qs,key=qkey):
        qq=urllib.parse.quote(q)
        ents=_fia(f"https://fiadataapi.azurewebsites.net/api/Data/GetEntityOnQtr?Qtr={qq}&Module=IM&Dataset=CCP")
        ids=",".join(str(e["id"]) for e in ents)
        d=_fia(f"https://fiadataapi.azurewebsites.net/api/Data/GetInitialMargin?Qtr={qq}&Ids={ids}&Dataset=CCP")
        y,n=qkey(q); asof=f"{y}-{n*3:02d}-{[31,30,30,31][n-1]}"
        s_=sum((x.get("house_Net") or 0)+(x.get("client_Gross") or 0) for x in d)
        tot.append((asof,round(s_/1e9,1)))
        for x in d: perccp.setdefault(x["name"].replace(" ","_").lower(),[]).append((asof,round(((x.get("house_Net") or 0)+(x.get("client_Gross") or 0))/1e9,1)))
        time.sleep(0.25)
    hist("ccp_im_required_15ccp_fia_bn",tot)
    for k,v in perccp.items(): hist(f"ccp_im_{k}_fia_bn",v)
    a,v=tot[-1]
    return [(NOW,"ccp_im_required_15ccp_fia_bn",a,v,"$bn","FIA CCP Tracker API (PQD 6.1.1), sum over 15 CCPs of house_net+client_gross","quarter-end; derivatives CCPs only, no FICC; FIA USD conversion")]
# DTCC FICC Sponsored Service volumes — daily CSV behind dtcc.com/charts/membership (added 2026-08-23, N3 return R4).
# From the SPONSORED MEMBER's perspective: TOTAL_REPO = sponsored members borrowing cash (hedge funds);
# TOTAL_REVERSE_REPO = sponsored members lending cash (money funds). Rolling ~5-year window, from Aug 2021.
def pull_dtcc():
    import csv as _csv, io as _io
    h=dict(UA); h["User-Agent"]="Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    t=urllib.request.urlopen(urllib.request.Request("https://www.dtcc.com/data/SponsoredVolume.csv",headers=h),timeout=60,context=CTX).read().decode("utf-8","ignore")
    rows=[]
    for r in _csv.DictReader(_io.StringIO(t)):
        bd=(r.get("BUSINESS_DATE") or "").strip()
        if not bd or bd=="TRAILER": continue
        try: m,d_,y=bd.split("/"); asof=f"{y}-{int(m):02d}-{int(d_):02d}"
        except Exception: continue
        def f(x):
            x=(x or "").replace("$","").replace(",","").strip(); return round(float(x)/1e9,1) if x not in ("",".00") else 0.0
        rows.append((asof,f(r["TOTAL_REPO_AMOUNT"]),f(r["TOTAL_REVERSE_REPO_AMOUNT"]),f(r["DVP_TOTAL_AMOUNT"]),f(r["GC_TOTAL_AMOUNT"]),f(r["TOTAL_AMOUNT"])))
    rows.sort(); rows=[r for r in rows if r[5]>0]
    keys=[("ficc_sponsored_repo_bn",1,"sponsored members borrowing cash (hedge-fund side)"),("ficc_sponsored_reverse_repo_bn",2,"sponsored members lending cash (money-fund side)"),
          ("ficc_sponsored_dvp_bn",3,"DVP leg"),("ficc_sponsored_gc_bn",4,"GC leg"),("ficc_sponsored_total_bn",5,"total sponsored activity")]
    out=[]
    for k,i,note in keys:
        hist(k,[(r[0],r[i]) for r in rows]); a=rows[-1][0]; v=rows[-1][i]
        out.append((NOW,k,a,v,"$bn","DTCC Sponsored Membership Volume CSV (dtcc.com/data/SponsoredVolume.csv)",f"daily; {note}"))
    return out
# FINRA margin statistics (added 2026-08-24). ONE workbook at a fixed URL that FINRA OVERWRITES each month —
# there is no vintage archive at source, so every run also saves a dated copy under data/vintages/finra/.
# Monthly, from 1997-01. Debit balances = customer margin borrowing (retail/brokerage, NOT prime-broker HF financing).
def pull_finra():
    u="https://www.finra.org/sites/default/files/2021-03/margin-statistics.xlsx"
    raw=urllib.request.urlopen(urllib.request.Request(u,headers=UA),timeout=90,context=CTX).read()
    vd=os.path.join(ROOT,"data","vintages","finra"); os.makedirs(vd,exist_ok=True)
    stamp=datetime.datetime.now(datetime.timezone.utc).strftime("%Y-%m-%d")
    open(os.path.join(vd,f"finra_margin_statistics_{stamp}.xlsx"),"wb").write(raw)
    # The workbook uses INLINE strings (no sharedStrings.xml) and omits empty cells, so index by
    # column letter from each cell's r="B7" attribute rather than by position.
    import zipfile, xml.etree.ElementTree as ET
    z=zipfile.ZipFile(io.BytesIO(raw)); NS="{http://schemas.openxmlformats.org/spreadsheetml/2006/main}"
    sheet=ET.fromstring(z.read("xl/worksheets/sheet1.xml"))
    out_rows=[]
    for row in sheet.iter(NS+"row"):
        cells={}
        for c in row.iter(NS+"c"):
            col=re.match(r"([A-Z]+)", c.get("r") or "")
            if not col: continue
            isv=c.find(NS+"is"); v=c.find(NS+"v")
            if isv is not None: cells[col.group(1)]="".join(t.text or "" for t in isv.iter(NS+"t"))
            elif v is not None: cells[col.group(1)]=v.text
        if re.match(r"^\d{4}-\d{2}$", str(cells.get("A",""))): out_rows.append(cells)
    if not out_rows: raise RuntimeError("FINRA workbook parsed to 0 data rows — layout changed, re-inspect")
    keys=[("finra_margin_debit_balances_bn","B"),("finra_free_credit_cash_bn","C"),("finra_free_credit_margin_bn","D")]
    res=[]
    for key,i in keys:
        pairs=sorted((r["A"]+"-01", round(float(r[i])/1000,1)) for r in out_rows if r.get(i))
        hist(key,pairs); a,v=pairs[-1]
        res.append((NOW,key,a[:7],v,"$bn",f"FINRA Margin Statistics workbook (finra.org, column {i}); dated copy saved to data/vintages/finra/","monthly from 1997-01; source file is OVERWRITTEN each month"))
    return res
# DeFiLlama total stablecoin outstanding (added 2026-08-29, D6/N2c engine 5). Free JSON API, on-chain
# mint/burn indexing; the only continuous aggregate — no official series exists under the GENIUS Act yet.
def pull_llama():
    d=json.loads(get("https://stablecoins.llama.fi/stablecoincharts/all"))
    import datetime as _dt
    pairs=[]
    for x in d:
        tot=(x.get("totalCirculating") or {}).get("peggedUSD")
        if tot: pairs.append((str(_dt.datetime.fromtimestamp(int(x["date"]),_dt.timezone.utc).date()),round(tot/1e9,1)))
    hist("stablecoin_total_outstanding_bn",pairs); a,v=pairs[-1]
    return [(NOW,"stablecoin_total_outstanding_bn",a,v,"$bn","DeFiLlama stablecoins.llama.fi/stablecoincharts/all","daily from 2017; USD-pegged circulating")]

PD_VENUE={"pd_ust_repo_out_bn":[("PDSORA-UTSETTOT","")],
 "pd_ust_reverse_in_bn":[("PDSIRRA-UTSETTOT","")],
 "pd_ust_rev_sponsored_dvp_bn":[("PDSIRRA-CBSPUTSET",s) for s in ("","TAL30","TAG30")],
 "pd_ust_repo_sponsored_bn":[("PDSORA-CBSPUTSET",s) for s in ("","TAL30","TAG30")]+[("PDSORA-TRISPUTSET",s) for s in ("","TAL30","TAG30")],
 "pd_ust_repo_triparty_gc_bn":[("PDSORA-TRIGUTSET",s) for s in ("","TAL30","TAG30")],
 "pd_ust_rev_uncleared_bilateral_bn":[("PDSIRRA-UBGUTSET",s) for s in ("","TAL30","TAG30")]+[("PDSIRRA-UBSUTSET",s) for s in ("","TAL30","TAG30")]}
def pull_nyfed_pd():
    # NY Fed Primary Dealer statistics (FR 2004 successor), SBN2024 break; weekly Wednesdays, $mn.
    # Component series summed per key; a venue aggregate is only emitted for a week where EVERY
    # component has an observation (missing week -> component absent -> skip, no silent zeros).
    import collections
    cache={}
    def series(code):
        if code not in cache:
            raw=get(f"https://markets.newyorkfed.org/api/pd/get/{code}.csv").decode()
            rows=list(csv.reader(io.StringIO(raw)))[1:]
            cache[code]={r[0]:float(r[2]) for r in rows if r[2] not in ("","*")}
        return cache[code]
    out=[]
    for key,comps in PD_VENUE.items():
        parts=[series(b+suf) for b,suf in comps]
        dates=set(parts[0]);
        for p in parts[1:]: dates &= set(p)
        pairs=sorted((d,round(sum(p[d] for p in parts)/1000,1)) for d in dates)
        hist(key,pairs); a,v=pairs[-1]
        out.append((NOW,key,a,v,"$bn","NY Fed Primary Dealer statistics API (markets.newyorkfed.org/api/pd), SBN2024 break, UST ex-TIPS","weekly Wed; gross outstanding; PDs only; venue split per 2026-08-30-D10 doc"))
    return out

SOURCES={"nyfed_pd":pull_nyfed_pd,"fiscaldata":pull_fiscaldata,"ofr":pull_ofr,"ofr_hf":pull_ofr_hf,"fia":pull_fia,"dtcc":pull_dtcc,"finra":pull_finra,"llama":pull_llama,"fdic":pull_fdic,"sec":pull_sec,"fred":pull_fred}
if __name__=="__main__":
    if "--list" in sys.argv: print("\n".join(f"  {k}" for k in SOURCES)); sys.exit()
    only=sys.argv[sys.argv.index("--only")+1].split(",") if "--only" in sys.argv else list(SOURCES)
    allrows=[]
    for k in only:
        try: rows=SOURCES[k](); allrows+=rows; print(f"  {k:10s} {len(rows)} series")
        except Exception as e: print(f"  {k:10s} FAILED: {e}")
    append(allrows); print(f"appended {len(allrows)} vintage rows to data/series.tsv at {NOW}")
    for r in allrows: print(f"    {r[1]:40s} {r[2]}  {r[3]:>12,}")
