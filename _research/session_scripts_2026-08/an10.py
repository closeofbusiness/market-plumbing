import sqlite3, pandas as pd, numpy as np
con=sqlite3.connect('z1.db')
def S(sid):
    df=pd.read_sql("SELECT period,value FROM obs WHERE series=? ORDER BY period",con,params=(sid,))
    return pd.Series(df.value.values/1e6, index=pd.PeriodIndex(pd.to_datetime(df.period),freq='Q'))
def comb(t,p='FL'):
    T=None
    for w,b in t:
        x=w*S(p+b+'.Q'); T=x if T is None else T.add(x,fill_value=0)
    return T
NAR=[(1,'313161105'),(1,'893161705'),(1,'883120005'),(1,'703130005'),(1,'893130505'),
     (1,'634090005'),(1,'892150005'),(1,'893169175'),(1,'894110005'),(1,'383162005')]
AL,AU=comb(NAR,'FL'),comb(NAR,'FU')
DL,DR=S('FL894194005.Q'),S('FR894194005.Q')
iss=(AU/AL.shift(1)); rev=(DR/DL.shift(1))
df=pd.concat([iss.rename('iss'),rev.rename('rev')],axis=1).dropna()
df=df[df.index>=pd.Period('1952Q1')]
print("QUARTERLY corr(iss,rev) =",round(df.iss.corr(df.rev),3),"n=",len(df))
for k in [4,8,20,40]:
    a=df.iss.rolling(k).sum(); b=df.rev.rolling(k).sum()
    c=pd.concat([a,b],axis=1).dropna()
    print(f"  {k}-quarter cumulative corr = {c.iss.corr(c.rev):+.3f} (n={len(c)}, overlapping)")
# non-overlapping 5y
q=df.copy(); q['blk']=(np.arange(len(q))//20)
g=q.groupby('blk').agg({'iss':'sum','rev':'sum'}); g=g[g.index<len(q)//20]
print(f"  non-overlapping 5y blocks: corr = {g.iss.corr(g.rev):+.3f} (n={len(g)})")
print(g.round(3).to_string())
