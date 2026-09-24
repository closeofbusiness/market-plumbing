import sqlite3, pandas as pd, numpy as np
con=sqlite3.connect('z1.db')
def S(sid):
    df=pd.read_sql("SELECT period,value FROM obs WHERE series=? ORDER BY period",con,params=(sid,))
    if df.empty: return None
    s=pd.Series(df.value.values/1e6, index=pd.PeriodIndex(pd.to_datetime(df.period),freq='Q'))
    return s
# --- denominator components (M3.s column 16) ---
comp = {
 'SDRs':'FL893111305','Interbank':'FL894110005','Checkable dep & currency':'FL883120005',
 'Time & savings dep':'FL703130005','Other deposits':'FL893130505','MMF shares':'FL634090005',
 'Open market paper':'FL893169175','Treasury (marketable)':'FL313161105','Agency securities':'FL893161705',
 'Municipal securities':'FL383162005','Corporate & foreign bonds':'FL893163005',
 'Repo & fed funds':'FL892150005','Dep inst loans nec':'FL793068005','Consumer credit':'FL153166000',
 'Mortgages':'FL893065005','Other loans & advances':'FL893169005',
 'Corporate equities':'FL893064105','DI equity (US abroad)':'FL263192101','DI equity (fgn in US)':'FL263092101',
 'Misc other equity':'FL893194905','Mutual fund shares':'FL653164205',
 'Life insurance reserves':'FL893140005','Pension entitlements':'FL893150005',
 'Trade payables':'FL893170005','Taxes payable':'FL893178005',
 'DI intercompany debt (out)':'FL263192305','DI intercompany debt (in)':'FL263092305',
 'Misc liabilities':'FL893190005'}
D=S('FL894194005.Q')
tot=None
rows=[]
for k,v in comp.items():
    s=S(v+'.Q')
    if s is None: print('MISSING',k,v); continue
    tot = s if tot is None else tot.add(s,fill_value=0)
    fr=S('FR'+v[2:]+'.Q')
    frabs = fr.abs().sum() if fr is not None else np.nan
    rows.append((k,v,s.get(pd.Period('1952Q4')),s.get(pd.Period('2026Q1')),frabs))
print("Denominator FL894194005.Q  2026Q1 = %.3f trn ; sum of components = %.3f trn ; diff %.3f"%(
    D.get(pd.Period('2026Q1')), tot.get(pd.Period('2026Q1')), D.get(pd.Period('2026Q1'))-tot.get(pd.Period('2026Q1'))))
df=pd.DataFrame(rows,columns=['item','id','1952Q4','2026Q1','sum|FR|'])
df['sh26']=df['2026Q1']/D.get(pd.Period('2026Q1'))*100
pd.set_option('display.width',200); pd.set_option('display.max_rows',100)
print(df.sort_values('2026Q1',ascending=False).to_string(index=False,float_format=lambda x:f"{x:,.3f}"))
