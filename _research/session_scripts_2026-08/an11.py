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
GL,GU=comb(GOV),comb(GOV,'FU'); PL,PU=comb(PRIV),comb(PRIV,'FU')
T=GL+PL
def run(a,b,lab):
    d=pd.DataFrame({'g':GU/T.shift(1),'p':PU/T.shift(1)}).dropna()
    d=d[(d.index>=pd.Period(a))&(d.index<=pd.Period(b))]
    Y=d.p.values; X=np.column_stack([np.ones(len(d)),d.g.values])
    bb=la.lstsq(X,Y,rcond=None)[0]; e=Y-X@bb
    u=X*e[:,None]; Sm=u.T@u
    for L in range(1,5):
        w=1-L/5.0; G=u[L:].T@u[:-L]; Sm=Sm+w*(G+G.T)
    V=la.inv(X.T@X)@Sm@la.inv(X.T@X); se=np.sqrt(np.diag(V))
    r2=1-(e@e)/((Y-Y.mean())@(Y-Y.mean()))
    print(f"{lab:28s} n={len(d):3d}  private-safe issuance = {bb[0]:+.5f} {bb[1]:+.4f} x gov-safe issuance  (NW se {se[1]:.4f}, t={bb[1]/se[1]:+.2f})  R2={r2:.3f}")
    return bb[1]
print("Test: is the TOTAL par-safe quantum demand-determined (coef = -1) or supply-determined (coef = 0)?")
print("  both sides scaled by lagged total par-safe stock; LEVELS of transactions, no shared denominator")
run('1952Q1','2026Q1','full 1952-2026')
run('1952Q1','2011Q3','GLM window')
run('2011Q4','2026Q1','post-GLM')
run('1952Q1','1984Q4','1952-1984')
run('1985Q1','2007Q4','1985-2007')
run('2008Q1','2026Q1','2008-2026 (QE era)')
