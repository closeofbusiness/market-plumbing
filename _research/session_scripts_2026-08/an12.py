import sqlite3, pandas as pd, numpy as np, numpy.linalg as la
con=sqlite3.connect('z1.db')
def S(sid):
    df=pd.read_sql("SELECT period,value FROM obs WHERE series=? ORDER BY period",con,params=(sid,))
    return pd.Series(df.value.values/1e6, index=pd.PeriodIndex(pd.to_datetime(df.period),freq='Q'))
def comb(t,p='FL'):
    T=None
    for w,b in t:
        x=w*S(p+b+'.Q'); T=x if T is None else T.add(x,fill_value=0)
    return T
GOV=[(1,'313161105'),(1,'893161705'),(1,'383162005')]
PRIV=[(1,'883120005'),(1,'703130005'),(1,'893130505'),(1,'634090005'),(1,'892150005'),(1,'893169175'),(1,'894110005')]
PRIVX=PRIV+[(-1,'713120005')]   # exclude central bank monetary base liabilities
gdp=S('FA086902005.Q'); gg=(gdp/gdp.shift(1)-1)
def run(P,a,b,lab,ctrl=False):
    GL,GU=comb(GOV),comb(GOV,'FU'); PL,PU=comb(P),comb(P,'FU'); T=GL+PL
    d=pd.DataFrame({'g':GU/T.shift(1),'p':PU/T.shift(1),'gg':gg}).dropna()
    d=d[(d.index>=pd.Period(a))&(d.index<=pd.Period(b))]
    cols=['g']+(['gg'] if ctrl else [])
    Y=d.p.values; X=np.column_stack([np.ones(len(d))]+[d[c].values for c in cols])
    bb=la.lstsq(X,Y,rcond=None)[0]; e=Y-X@bb
    u=X*e[:,None]; Sm=u.T@u
    for L in range(1,5):
        w=1-L/5.0; G=u[L:].T@u[:-L]; Sm=Sm+w*(G+G.T)
    V=la.inv(X.T@X)@Sm@la.inv(X.T@X); se=np.sqrt(np.diag(V))
    print(f"{lab:44s} n={len(d):3d} b_gov={bb[1]:+.4f} (NW se {se[1]:.4f}, t={bb[1]/se[1]:+.2f})"+(f" b_gdpgrowth={bb[2]:+.3f}({se[2]:.3f})" if ctrl else ""))
print("PRIVATE SAFE incl. central-bank reserves:")
for a,b,l in [('1952Q1','2026Q1','full'),('1952Q1','2011Q3','GLM window'),('2011Q4','2026Q1','post-GLM')]:
    run(PRIV,a,b,'  '+l); run(PRIV,a,b,'  '+l+' + nominal GDP growth control',True)
print("\nPRIVATE SAFE excl. central-bank reserves (removes the QE accounting link):")
for a,b,l in [('1952Q1','2026Q1','full'),('1952Q1','2011Q3','GLM window'),('2011Q4','2026Q1','post-GLM'),('2008Q1','2026Q1','2008-2026')]:
    run(PRIVX,a,b,'  '+l); run(PRIVX,a,b,'  '+l+' + nominal GDP growth control',True)
