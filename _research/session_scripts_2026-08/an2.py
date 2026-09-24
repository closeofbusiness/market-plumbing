import sqlite3, pandas as pd, numpy as np
con=sqlite3.connect('z1.db')
def S(sid, req=True):
    df=pd.read_sql("SELECT period,value FROM obs WHERE series=? ORDER BY period",con,params=(sid,))
    if df.empty:
        if req: raise KeyError(sid)
        return None
    return pd.Series(df.value.values/1e6, index=pd.PeriodIndex(pd.to_datetime(df.period),freq='Q'))
def Z(): return pd.Series(0.0,index=idx)
D=S('FL894194005.Q'); idx=D.index

# ---------- NUMERATOR: GLM "high estimate", rebuilt top-down on current Z.1 ----------
fin  = S('FL794190005.Q')                 # domestic financial sectors, total liabilities
fed  = S('FL314190005.Q')
sl   = S('FL214190005.Q')
# exclusions from financial liabilities (GLM: not information-insensitive)
mfs  = S('FL653164205.Q')                 # mutual fund shares
lifeR= S('FL893140005.Q') - S('FL313140003.Q')   # life insurance reserves, financial sector
pens = S('FL153050005.Q')                 # HH pension entitlements asset (GLM's line)
taxf = S('FL793178005.Q')
# 15% haircut set (long-term financial debt: agency/GSE MBS, fin corp bonds, bank loans nec, other loans)
gse  = S('FL423161705.Q')                 # GSE + agency/GSE mortgage pool securities
fbond= S('FL793163005.Q')
bkln = S('FL793168005.Q')
oth  = S('FL793169005.Q')
haircut = 0.15*(gse+fbond+bkln+oth)
fedX = S('FL313140003.Q') + S('FL313195105.Q')
slX  = S('FL213169203.Q')
N_hi = fin + fed + sl - mfs - lifeR - pens - taxf - haircut - fedX - slX
D_adj= D - slX
ratio = (N_hi/D_adj).dropna()

# ---------- NARROW par-money numerator ----------
narrow = (S('FL313161105.Q')+S('FL893161705.Q')+S('FL883120005.Q')+S('FL703130005.Q')
          +S('FL893130505.Q')+S('FL634090005.Q')+S('FL892150005.Q')+S('FL893169175.Q')
          +S('FL894110005.Q')+S('FL383162005.Q'))
r_narrow=(narrow/D).dropna()

def band(s,lab):
    s=s[s.index>=pd.Period('1952Q1')]
    print(f"{lab}: mean={s.mean():.4f} sd={s.std():.4f} min={s.min():.4f}({s.idxmin()}) max={s.max():.4f}({s.idxmax()})")
    for p in ['1952Q4','1960Q4','1970Q4','1980Q4','1990Q4','2000Q4','2007Q4','2009Q4','2012Q4','2015Q4','2019Q4','2020Q4','2021Q4','2022Q4','2023Q4','2024Q4','2025Q4','2026Q1']:
        pp=pd.Period(p)
        if pp in s.index: print(f"   {p} {s[pp]*100:6.2f}%")
band(ratio,"GLM-style high-estimate share")
print()
band(r_narrow,"Narrow par-money share")
print()
# OLS on time trend, GLM Panel A replication, two samples
import numpy.linalg as la
def ols(s,lab):
    y=s.values; t=np.arange(1,len(y)+1); X=np.column_stack([np.ones_like(t,float),t])
    b=la.lstsq(X,y,rcond=None)[0]; e=y-X@b
    s2=e@e/(len(y)-2); V=s2*la.inv(X.T@X); se=np.sqrt(np.diag(V))
    r2=1-(e@e)/((y-y.mean())@(y-y.mean()))
    # Newey-West lag 8
    u=X*e[:,None]; Sm=u.T@u
    for L in range(1,9):
        w=1-L/9.0; G=u[L:].T@u[:-L]; Sm=Sm+w*(G+G.T)
    Vnw=la.inv(X.T@X)@Sm@la.inv(X.T@X); senw=np.sqrt(np.diag(Vnw))
    print(f"{lab} n={len(y)} {s.index[0]}-{s.index[-1]}: const={b[0]:.4f} (OLS se {se[0]:.4f}; NW8 se {senw[0]:.4f}) trend={b[1]:.6f} (OLS se {se[1]:.6f}; NW8 se {senw[1]:.6f}) R2={r2:.3f} total trend over sample={b[1]*len(y)*100:.2f}pp")
ols(ratio[(ratio.index>=pd.Period('1952Q1'))&(ratio.index<=pd.Period('2011Q3'))],"GLM window 1952Q1-2011Q3")
ols(ratio[ratio.index>=pd.Period('1952Q1')],"Full 1952Q1-2026Q1")
ols(ratio[ratio.index>=pd.Period('2011Q4')],"Post-GLM 2011Q4-2026Q1")
ols(r_narrow[(r_narrow.index>=pd.Period('1952Q1'))&(r_narrow.index<=pd.Period('2011Q3'))],"NARROW 1952Q1-2011Q3")
ols(r_narrow[r_narrow.index>=pd.Period('1952Q1')],"NARROW full")
ols(r_narrow[r_narrow.index>=pd.Period('2011Q4')],"NARROW post-GLM")
ratio.to_csv('ratio.csv'); r_narrow.to_csv('narrow.csv')
pd.DataFrame({'N_hi':N_hi,'D_adj':D_adj,'narrow':narrow,'D':D}).to_csv('levels.csv')
