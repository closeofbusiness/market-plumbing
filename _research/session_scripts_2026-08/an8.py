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
base=[(1,'794190005'),(1,'314190005'),(1,'214190005'),(-1,'653164205'),
      (-1,'893140005'),(-1,'153050005'),(-1,'793178005'),(-1,'313195105'),(-1,'213169203'),
      (-0.15,'423161705'),(-0.15,'793163005'),(-0.15,'793168005'),(-0.15,'793169005')]
N=comb(base); D=comb([(1,'894194005'),(-1,'213169203')]); D0=comb([(1,'894190005'),(-1,'213169203')])
NAR=[(1,'313161105'),(1,'893161705'),(1,'883120005'),(1,'703130005'),(1,'893130505'),
     (1,'634090005'),(1,'892150005'),(1,'893169175'),(1,'894110005'),(1,'383162005')]
A=comb(NAR)
out=pd.DataFrame({'N':N,'D':D,'Dnoeq':D0,'narrow':A})
out['shareA']=out.N/out.D*100; out['shareE']=out.N/out.Dnoeq*100; out['narrow_sh']=out.narrow/out.D*100
ann=out[out.index.quarter==4]
ann.index=ann.index.year
print(ann[['shareA','shareE','narrow_sh']].loc[1952:].round(2).to_string())
out.to_csv('series_out.csv')
