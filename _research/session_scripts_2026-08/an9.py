import sqlite3, pandas as pd, numpy as np, numpy.linalg as la
d=pd.read_csv('series_out.csv',index_col=0); d.index=pd.PeriodIndex(d.index,freq='Q')
con=sqlite3.connect('z1.db')
def S(sid):
    df=pd.read_sql("SELECT period,value FROM obs WHERE series=? ORDER BY period",con,params=(sid,))
    return pd.Series(df.value.values/1e6, index=pd.PeriodIndex(pd.to_datetime(df.period),freq='Q'))
eq=S('FL893064105.Q'); eqR=S('FR893064105.Q'); D=d.D; DR=S('FR894194005.Q')
sh=d.shareA/100
d2=pd.concat([sh.rename('sh'),(eq/D).rename('eqsh')],axis=1).dropna()
d2=d2[d2.index>=pd.Period('1952Q1')]
print("corr(GLM-style share, equity share of denominator) =",round(d2.sh.corr(d2.eqsh),3))
y=d2.sh.values; X=np.column_stack([np.ones(len(d2)),d2.eqsh.values])
b=la.lstsq(X,y,rcond=None)[0]; e=y-X@b
print("share = %.4f %+.4f * equity-share-of-denominator ; R2=%.3f"%(b[0],b[1],1-(e@e)/((y-y.mean())@(y-y.mean()))))
# counterfactual: freeze denominator revaluation after 2011Q3
b0=pd.Period('2011Q3')
cf=D.copy()
rev=DR[DR.index>b0].cumsum()
cf_noreval=D.copy()
cf_noreval[cf_noreval.index>b0]=D[D.index>b0]-rev
print("\nCounterfactual: denominator without post-2011Q3 revaluation")
for p in ['2011Q3','2019Q4','2021Q4','2025Q4','2026Q1']:
    pp=pd.Period(p)
    print(f"  {p}: actual share {d.shareA[pp]:.2f}%   no-post-2011-revaluation share {d.N[pp]/cf_noreval[pp]*100:.2f}%   D {D[pp]:.1f} vs {cf_noreval[pp]:.1f} trn")
# how much did each side grow
print("\nGrowth multiples 2011Q3 -> 2026Q1:")
for c in ['N','D','Dnoeq','narrow']:
    print(f"  {c}: {d[c][pd.Period('2011Q3')]:.2f} -> {d[c][pd.Period('2026Q1')]:.2f} trn  x{d[c][pd.Period('2026Q1')]/d[c][pd.Period('2011Q3')]:.3f}")
print(f"  equity: {eq[pd.Period('2011Q3')]:.2f} -> {eq[pd.Period('2026Q1')]:.2f}  x{eq[pd.Period('2026Q1')]/eq[pd.Period('2011Q3')]:.3f}")
# peaks/troughs check
s=sh[sh.index>=pd.Period('1952Q1')]
print("\n10 lowest quarters:", [(str(i),round(v*100,2)) for i,v in s.nsmallest(10).items()])
print("10 highest quarters:", [(str(i),round(v*100,2)) for i,v in s.nlargest(10).items()])
