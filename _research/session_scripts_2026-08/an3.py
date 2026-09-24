import sqlite3, pandas as pd, numpy as np
con=sqlite3.connect('z1.db')
def S(sid,req=True):
    df=pd.read_sql("SELECT period,value FROM obs WHERE series=? ORDER BY period",con,params=(sid,))
    if df.empty:
        if req: raise KeyError(sid)
        return None
    return pd.Series(df.value.values/1e6, index=pd.PeriodIndex(pd.to_datetime(df.period),freq='Q'))
# identity check: dFL = FU + FR (+ other volume changes)
for b,lab in [('894194005','All sectors total liabilities & equity (DENOM)'),
              ('794190005','Domestic financial sectors total liabilities'),
              ('314190005','Federal government total liabilities'),
              ('893064105','Corporate equities'),
              ('313161105','Treasury marketable')]:
    L=S('FL'+b+'.Q'); U=S('FU'+b+'.Q'); R=S('FR'+b+'.Q')
    dL=L.diff()
    resid=(dL-U-R).dropna()
    w=resid[resid.index>=pd.Period('1952Q1')]
    print(f"{lab}: mean|resid|={w.abs().mean():.4f}trn/qtr, max|resid|={w.abs().max():.3f} ; sum resid 1952-2026={w.sum():.3f}trn ; sum dL={dL[dL.index>=pd.Period('1952Q1')].sum():.3f}")
