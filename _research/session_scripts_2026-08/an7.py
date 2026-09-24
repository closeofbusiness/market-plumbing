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
base=[(1,'794190005'),(1,'314190005'),(1,'214190005'),(-1,'653164205'),
      (-1,'893140005'),(-1,'153050005'),(-1,'793178005'),(-1,'313195105'),(-1,'213169203')]
hair=[(-0.15,'423161705'),(-0.15,'793163005'),(-0.15,'793168005'),(-0.15,'793169005')]
lowx=[(-1,'893190005'),(1,'313190005'),(1,'213190005') ]  # rough: strip misc liabs (high-only item)
D194=comb([(1,'894194005'),(-1,'213169203')])
D190=comb([(1,'894190005'),(-1,'213169203')])
variants={
 'A. baseline (high, 85% haircut)': (comb(base+hair), D194),
 'B. no 85% haircut':               (comb(base),      D194),
 'C. drop financial misc liabs (~low)': (comb(base+hair+[(-1,'793190005')]), D194),
 'D. also drop trade payables & security credit': (comb(base+hair+[(-1,'793190005'),(-1,'793170005'),(-1,'313170005'),(-1,'213170003'),(-1,'663167005')]), D194),
 'E. denominator = total liabilities only (no equity)': (comb(base+hair), D190),
 'F. numerator keeps pension entitlements': (comb([t for t in base if t[1]!='153050005']+hair), D194),
}
def ols(s):
    s=s.dropna(); y=s.values; t=np.arange(1,len(y)+1); X=np.column_stack([np.ones_like(t,float),t])
    b=la.lstsq(X,y,rcond=None)[0]; e=y-X@b; s2=e@e/(len(y)-2); se=np.sqrt(np.diag(s2*la.inv(X.T@X)))
    return b,se,len(y)
print(f"{'variant':52s} {'GLMwin const(se)':>22s} {'2011Q3':>8s} {'2026Q1':>8s} {'chg pp':>7s} {'post-GLM trend/qtr(se)':>26s}")
for k,(N,D) in variants.items():
    r=(N/D).dropna()
    g=r[(r.index>=pd.Period('1952Q1'))&(r.index<=pd.Period('2011Q3'))]
    p=r[r.index>=pd.Period('2011Q4')]
    b,se,n=ols(g); b2,se2,n2=ols(p)
    print(f"{k:52s}  {b[0]:.4f}({se[0]:.4f}) n={n:3d} {r[pd.Period('2011Q3')]*100:7.2f}% {r[pd.Period('2026Q1')]*100:7.2f}% {(r[pd.Period('2026Q1')]-r[pd.Period('2011Q3')])*100:+7.2f} {b2[1]:+.6f}({se2[1]:.6f})")
# numerator composition
print("\n--- composition of narrow par-money numerator (trn) ---")
NAR=[('Treasury marketable','313161105'),('Agency secs','893161705'),('Checkable dep+currency','883120005'),
     ('Time & savings dep','703130005'),('Other deposits','893130505'),('MMF shares','634090005'),
     ('Repo+fed funds','892150005'),('Open mkt paper','893169175'),('Interbank','894110005'),('Municipal','383162005')]
rows=[]
for nm,b in NAR:
    s=S('FL'+b+'.Q'); rows.append((nm,s[pd.Period('1952Q4')],s[pd.Period('2007Q4')],s[pd.Period('2011Q3')],s[pd.Period('2026Q1')]))
d=pd.DataFrame(rows,columns=['item','1952Q4','2007Q4','2011Q3','2026Q1'])
d.loc[len(d)]=['TOTAL']+list(d.iloc[:,1:].sum())
print(d.to_string(index=False,float_format=lambda x:f"{x:,.3f}"))
