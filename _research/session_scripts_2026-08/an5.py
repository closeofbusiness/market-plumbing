import sqlite3, pandas as pd, numpy as np, numpy.linalg as la
con=sqlite3.connect('z1.db')
def S(sid):
    df=pd.read_sql("SELECT period,value FROM obs WHERE series=? ORDER BY period",con,params=(sid,))
    return pd.Series(df.value.values/1e6, index=pd.PeriodIndex(pd.to_datetime(df.period),freq='Q'))
def comb(terms,p):
    T=None
    for w,b in terms:
        x=w*S(p+b+'.Q'); T=x if T is None else T.add(x,fill_value=0)
    return T
N_terms=[(1,'794190005'),(1,'314190005'),(1,'214190005'),(-1,'653164205'),
         (-1,'893140005'),(-1,'153050005'),(-1,'793178005'),
         (-0.15,'423161705'),(-0.15,'793163005'),(-0.15,'793168005'),(-0.15,'793169005'),
         (-1,'313140003'),(-1,'313195105'),(-1,'213169203')]
D_terms=[(1,'894194005'),(-1,'213169203')]
NAR=[(1,'313161105'),(1,'893161705'),(1,'883120005'),(1,'703130005'),(1,'893130505'),
     (1,'634090005'),(1,'892150005'),(1,'893169175'),(1,'894110005'),(1,'383162005')]
NL,NU=comb(N_terms,'FL'),comb(N_terms,'FU')
DL,DU=comb(D_terms,'FL'),comb(D_terms,'FU')
AL,AU=comb(NAR,'FL'),comb(NAR,'FU')
b0=pd.Period('1951Q4')
def cum(L,U):
    u=U[U.index>b0].cumsum(); return L[b0]+u
NQ,DQ,AQ=cum(NL,NU),cum(DL,DU),cum(AL,AU)
act=(NL/DL).dropna(); q=(NQ/DQ).dropna(); aq=(AQ/DQ).dropna(); aa=(AL/DL).dropna()
def ols(s,lab):
    s=s.dropna(); y=s.values; t=np.arange(1,len(y)+1); X=np.column_stack([np.ones_like(t,float),t])
    b=la.lstsq(X,y,rcond=None)[0]; e=y-X@b; s2=e@e/(len(y)-2); se=np.sqrt(np.diag(s2*la.inv(X.T@X)))
    print(f"{lab:46s} n={len(y):3d} const={b[0]:.4f}(se {se[0]:.4f}) trend={b[1]:+.6f}(se {se[1]:.6f}) mean={y.mean():.4f} sd={y.std():.4f}")
print("--- ACTUAL LEVELS ratio ---")
ols(act[act.index>=pd.Period('1952Q1')],"GLM-style share, full")
ols(act[(act.index>=pd.Period('1952Q1'))&(act.index<=pd.Period('2011Q3'))],"GLM-style share, GLM window")
print("--- TRANSACTIONS-ONLY (cumulated FU, no revaluation) ---")
ols(q[q.index>=pd.Period('1952Q1')],"safe/total, transactions-only, full")
ols(q[(q.index>=pd.Period('1952Q1'))&(q.index<=pd.Period('2011Q3'))],"safe/total, transactions-only, GLM window")
print("--- NARROW PAR ---")
ols(aa[aa.index>=pd.Period('1952Q1')],"narrow par / actual denom, full")
ols(aq[aq.index>=pd.Period('1952Q1')],"narrow par(trans) / denom(trans), full")
print()
print("Key dates: actual vs transactions-only share")
for p in ['1952Q4','1970Q4','1990Q4','2000Q4','2011Q3','2019Q4','2021Q4','2025Q4','2026Q1']:
    pp=pd.Period(p); print(f"  {p}  actual {act[pp]*100:6.2f}%   trans-only {q[pp]*100:6.2f}%   narrow {aa[pp]*100:6.2f}%")
# denominator market-valued share
mkt=['893064105','653164205','263192101','263092101','893194905','893150005','893140005']
M=None
for b in mkt:
    x=S('FL'+b+'.Q'); M=x if M is None else M.add(x,fill_value=0)
sh=(M/DL).dropna()
print("\nShare of denominator in market-revalued instruments (equities, fund shares, DI equity, pension/insurance):")
for p in ['1952Q4','1970Q4','1990Q4','2000Q4','2011Q3','2021Q4','2025Q4','2026Q1']:
    pp=pd.Period(p); print(f"  {p} {sh[pp]*100:6.2f}%  (level {M[pp]:8.2f}trn of {DL[pp]:8.2f}trn)")
# D/GDP
gdp=S('FA086902005.Q')
if gdp is None or gdp.empty: print("no gdp series")
else:
    for p in ['1952Q4','2010Q4','2025Q4']:
        pp=pd.Period(p); print(f"  D/GDP {p}: {DL[pp]/(gdp[pp]):.2f}x   (GDP {gdp[pp]:.3f}trn saar)")
