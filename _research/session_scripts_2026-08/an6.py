import sqlite3, pandas as pd, numpy as np, numpy.linalg as la
con=sqlite3.connect('z1.db')
def S(sid):
    df=pd.read_sql("SELECT period,value FROM obs WHERE series=? ORDER BY period",con,params=(sid,))
    return pd.Series(df.value.values/1e6, index=pd.PeriodIndex(pd.to_datetime(df.period),freq='Q'))
def comb(t,p):
    T=None
    for w,b in t:
        x=w*S(p+b+'.Q'); T=x if T is None else T.add(x,fill_value=0)
    return T
NAR=[(1,'313161105'),(1,'893161705'),(1,'883120005'),(1,'703130005'),(1,'893130505'),
     (1,'634090005'),(1,'892150005'),(1,'893169175'),(1,'894110005'),(1,'383162005')]
D_terms=[(1,'894194005'),(-1,'213169203')]
AL,AU=comb(NAR,'FL'),comb(NAR,'FU')
DL,DU,DR=comb(D_terms,'FL'),comb(D_terms,'FU'),comb(D_terms,'FR')
EQ_L,EQ_R=S('FL893064105.Q'),S('FR893064105.Q')
# issuance rate of par money, and revaluation return on the denominator
x = (AU/AL.shift(1)).dropna()          # safe issuance rate
y = (DR/DL.shift(1)).dropna()          # revaluation return on total liabilities+equity
z = (EQ_R/EQ_L.shift(1)).dropna()      # equity revaluation return
df=pd.concat([x.rename('iss'),y.rename('rev'),z.rename('eqrev')],axis=1).dropna()
df=df[df.index>=pd.Period('1952Q1')]
def reg(dep,regs,lab,d=df):
    Y=d[dep].values; X=np.column_stack([np.ones(len(d))]+[d[r].values for r in regs])
    b=la.lstsq(X,Y,rcond=None)[0]; e=Y-X@b
    u=X*e[:,None]; Sm=u.T@u
    for L in range(1,5):
        w=1-L/5.0; G=u[L:].T@u[:-L]; Sm=Sm+w*(G+G.T)
    V=la.inv(X.T@X)@Sm@la.inv(X.T@X); se=np.sqrt(np.diag(V))
    r2=1-(e@e)/((Y-Y.mean())@(Y-Y.mean()))
    print(f"{lab}  n={len(d)} R2={r2:.3f}")
    for nm,bb,ss in zip(['const']+regs,b,se):
        print(f"    {nm:12s} {bb:+.4f} (NW se {ss:.4f})  t={bb/ss:+.2f}")
for L in [1,2,3,4]:
    df[f'rev_l{L}']=df['rev'].shift(L); df[f'iss_l{L}']=df['iss'].shift(L)
    df[f'eqrev_l{L}']=df['eqrev'].shift(L)
d=df.dropna()
print("=== Does safe-asset ISSUANCE follow past total revaluation?  (wealth-driven demand) ===")
reg('iss',['iss_l1','iss_l2','rev_l1','rev_l2','rev_l3','rev_l4'],'iss ~ own lags + revaluation lags',d)
print("\n=== Does total REVALUATION follow past safe-asset issuance?  (collateral-driven supply) ===")
reg('rev',['rev_l1','rev_l2','iss_l1','iss_l2','iss_l3','iss_l4'],'rev ~ own lags + issuance lags',d)
print("\n=== Equity revaluation version ===")
reg('eqrev',['eqrev_l1','eqrev_l2','iss_l1','iss_l2','iss_l3','iss_l4'],'eqrev ~ own lags + issuance lags',d)
reg('iss',['iss_l1','iss_l2','eqrev_l1','eqrev_l2','eqrev_l3','eqrev_l4'],'iss ~ own lags + equity reval lags',d)
print("\nsum-of-lag Wald-ish: contemporaneous corr(iss,rev)=%.3f  corr(iss,eqrev)=%.3f"%(df['iss'].corr(df['rev']),df['iss'].corr(df['eqrev'])))
# split sample
for a,b in [('1952Q1','1984Q4'),('1985Q1','2011Q3'),('2011Q4','2026Q1')]:
    s=d[(d.index>=pd.Period(a))&(d.index<=pd.Period(b))]
    print(f"\n--- subsample {a}-{b} (n={len(s)}) ---")
    reg('iss',['iss_l1','rev_l1','rev_l2','rev_l3','rev_l4'],'iss ~ rev lags',s)
    reg('rev',['rev_l1','iss_l1','iss_l2','iss_l3','iss_l4'],'rev ~ iss lags',s)
