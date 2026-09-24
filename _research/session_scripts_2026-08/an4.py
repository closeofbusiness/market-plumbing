import sqlite3, pandas as pd, numpy as np
con=sqlite3.connect('z1.db')
def S(sid):
    df=pd.read_sql("SELECT period,value FROM obs WHERE series=? ORDER BY period",con,params=(sid,))
    if df.empty: raise KeyError(sid)
    return pd.Series(df.value.values/1e6, index=pd.PeriodIndex(pd.to_datetime(df.period),freq='Q'))
def trio(b): return S('FL'+b+'.Q'), S('FU'+b+'.Q'), S('FR'+b+'.Q')
def comb(terms):
    L=U=R=None
    for w,b in terms:
        l,u,r=trio(b)
        L = w*l if L is None else L.add(w*l,fill_value=0)
        U = w*u if U is None else U.add(w*u,fill_value=0)
        R = w*r if R is None else R.add(w*r,fill_value=0)
    return L,U,R
N_terms=[(1,'794190005'),(1,'314190005'),(1,'214190005'),(-1,'653164205'),
         (-1,'893140005'),(1,'313140003'),(-1,'153050005'),(-1,'793178005'),
         (-0.15,'423161705'),(-0.15,'793163005'),(-0.15,'793168005'),(-0.15,'793169005'),
         (-1,'313140003'),(-1,'313195105'),(-1,'213169203')]
NL,NU,NR=comb(N_terms)
DL,DU,DR=comb([(1,'894194005'),(-1,'213169203')])
NAR=[(1,'313161105'),(1,'893161705'),(1,'883120005'),(1,'703130005'),(1,'893130505'),
     (1,'634090005'),(1,'892150005'),(1,'893169175'),(1,'894110005'),(1,'383162005')]
AL,AU,AR=comb(NAR)
def win(a,b,label):
    a=pd.Period(a); b=pd.Period(b)
    out=[]
    for nm,(L,U,R) in [('SAFE NUMERATOR (GLM-style)',(NL,NU,NR)),('NARROW PAR MONEY',(AL,AU,AR)),('DENOMINATOR (all liab+equity)',(DL,DU,DR))]:
        dL=L[b]-L[a]; u=U[(U.index>a)&(U.index<=b)].sum(); r=R[(R.index>a)&(R.index<=b)].sum()
        out.append((nm,L[a],L[b],dL,u,r,dL-u-r, 100*u/dL if dL else np.nan, 100*r/dL if dL else np.nan))
    print(f"\n=== {label}  ({a} -> {b}) ===")
    print(f"{'':30s} {'start':>9s} {'end':>9s} {'dLevel':>9s} {'Trans':>9s} {'Reval':>9s} {'Other':>8s} {'%trans':>7s} {'%reval':>7s}")
    for o in out:
        print(f"{o[0]:30s} {o[1]:9.2f} {o[2]:9.2f} {o[3]:9.2f} {o[4]:9.2f} {o[5]:9.2f} {o[6]:8.2f} {o[7]:7.1f} {o[8]:7.1f}")
for a,b,l in [('1951Q4','2026Q1','FULL 1952-2026'),('1951Q4','2011Q3','GLM SAMPLE'),
              ('2011Q3','2026Q1','POST-GLM'),('2007Q4','2012Q4','CRISIS+QE1-3'),
              ('2019Q4','2021Q4','COVID'),('2021Q4','2026Q1','2022-26'),
              ('2022Q4','2025Q4','2023-25'),('1994Q4','2026Q1','SINCE 1995')]:
    win(a,b,l)
