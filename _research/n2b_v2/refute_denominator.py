import csv, os
D=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")  # repo root, wherever it is cloned (was the author's Dropbox path before 24 Sep 2026)
def hist(name):
    return {r['as_of'][:7]:float(r['value']) for r in csv.DictReader(open(f"{D}/history/{name}.csv"))}
tsy=hist('mmf_treasury_repo_bn'); ag=hist('mmf_agency_repo_bn'); oth=hist('mmf_repo_other_collateral_bn'); fed=hist('mmf_repo_with_fed_bn')
alf={r['observation_date'][:7]:float(r['M2SL_20260815']) for r in csv.DictReader(open(f"{D}/vintages/alfred/alf_M2SL_2026-08-15.csv"))}
h8={r['as_of']:(float(r['total_deposits_bn']),float(r['large_time_deposits_bn'])) for r in csv.DictReader(open('h8.csv'))}
m2={r['as_of'][:7]:(float(r['m2_bn']),float(r['currency_bn']),float(r['retail_mmf_bn'])) for r in csv.DictReader(open('m2.csv'))}
z1={r['as_of']:(float(r['hh_checkable_currency_bn']),float(r['hh_time_savings_bn'])) for r in csv.DictReader(open('z1.csv'))}
pf={r['as_of'][:7]:float(r['value'])/1e9 for r in csv.DictReader(open('formpf.csv')) if r['mnemonic']=='FPF-ASSETCLASS_REPO_REVERSEREPO_SUM'}
# H.8 full package: total liabilities B1152, other deposits B1110, borrowings B3094 ($ millions)
rows=list(csv.reader(open('h8_allcombanks_sa_monthly_package.csv'))); mn=rows[5]
ix={m:i for i,m in enumerate(mn)}
pk={r[0]:{k:float(r[ix[k]])/1000 for k in ['B1152NCBAM','B1110NCBAM','B3094NCBAM','B1058NCBAM','B1072NCBAM']} for r in rows[6:] if r[0]>='2021'}
qs=[('2021Q4','2021-12'),('2022Q1','2022-03'),('2022Q2','2022-06'),('2022Q3','2022-09'),('2022Q4','2022-12'),('2023Q1','2023-03'),('2023Q2','2023-06'),('2023Q3','2023-09'),('2023Q4','2023-12'),('2024Q1','2024-03'),('2024Q2','2024-06'),('2024Q3','2024-09'),('2024Q4','2024-12'),('2025Q1','2025-03'),('2025Q2','2025-06'),('2025Q3','2025-09'),('2025Q4','2025-12'),('2026Q1','2026-03')]
z=lambda w,d:100*w/(w+d)
out=[]
for q,m in qs:
    priv=tsy[m]+ag[m]+oth[m]-fed[m]; ltd=h8[m][1]; W1=priv+ltd; W2=W1+pf[m]
    D1=alf[m]; D2=m2[m][0]-m2[m][1]-m2[m][2]; D3=h8[m][0]-ltd; D4=z1[q][0]+z1[q][1]
    D5=pk[m]['B1110NCBAM']            # Board's own "other deposits" (dep less large time)
    D6=pk[m]['B1152NCBAM']-ltd        # total bank liabilities less LTD (adversarial: broadest bank-side base)
    D7=alf[m]+ltd                     # M2 + LTD (M3-like)  -> z = W2/(W2+D7) double counts LTD; use W2/(priv+pf+D7) i.e. W excl LTD + M3ish
    out.append(dict(q=q,W1=W1,W2=W2,D1=D1,D2=D2,D3=D3,D4=D4,D5=D5,D6=D6,
        z11=z(W1,D1),z21=z(W2,D1),z22=z(W2,D2),z23=z(W2,D3),z24=z(W2,D4),z25=z(W2,D5),z26=z(W2,D6),
        z27=100*W2/D7  # wholesale (incl LTD) as % of M2+LTD, a plain ratio to an M3-style aggregate
        ,r21=100*W2/D1))
cols=['z11','z21','z22','z23','z24','z25','z26','z27','r21']
names={'z11':'W1/(W1+M2 alf)','z21':'W2/(W2+M2 alf)','z22':'W2/(W2+M2-cur-rMMF ddp)','z23':'W2/(W2+H8 dep-LTD)','z24':'W2/(W2+Z1 HH dep)','z25':'W2/(W2+H8 other dep B1110)','z26':'W2/(W2+H8 tot liab-LTD)','z27':'W2/(M2+LTD) plain','r21':'W2/M2 plain'}
print('q      W1      W2      D1       D2       D3       D4       D5       D6   | '+' '.join(f'{c:>6}' for c in cols))
for o in out:
    print(f"{o['q']} {o['W1']:7.1f} {o['W2']:7.1f} {o['D1']:8.1f} {o['D2']:8.1f} {o['D3']:8.1f} {o['D4']:8.1f} {o['D5']:8.1f} {o['D6']:8.1f} | "+' '.join(f"{o[c]:6.2f}" for c in cols))
print()
for c in cols:
    s=[o[c] for o in out]
    dq=['+' if b>a else ('-' if b<a else '0') for a,b in zip(s,s[1:])]
    trough=out[s.index(min(s))]['q']; peak=out[s.index(max(s))]['q']
    print(f"{names[c]:32s} start {s[0]:6.2f} end {s[-1]:6.2f} x{s[-1]/s[0]:.2f} +{s[-1]-s[0]:5.2f}pp trough {trough} peak {peak} 25Q4->26Q1 {s[-1]-s[-2]:+.2f} signs {''.join(dq)}")
# decomposition: z21 counterfactuals
o0=out[0]; oe=out[-1]
print('\nDecomposition W2/D1 2021Q4->2026Q1:')
print(' actual', round(z(o0['W2'],o0['D1']),2),'->',round(z(oe['W2'],oe['D1']),2))
print(' W grows, D frozen at 2021Q4 :', round(z(oe['W2'],o0['D1']),2))
print(' D moves, W frozen at 2021Q4 :', round(z(o0['W2'],oe['D1']),2))
for c,d in [('z22','D2'),('z23','D3'),('z24','D4')]:
    print(f" {names[c]}: W frozen ->", round(z(o0['W2'],oe[d]),2), ' D frozen ->', round(z(oe['W2'],o0[d]),2))
# compare vs build csv
b={r['quarter']:r for r in csv.DictReader(open('zk_v2.csv'))}
mx=0
for o,(q,m) in zip(out,qs):
    for mine,theirs in [('z11','z_W1_D1_pct'),('z21','z_W2_D1_pct'),('z22','z_W2_D2_pct'),('z23','z_W2_D3_pct'),('z24','z_W2_D4_pct')]:
        mx=max(mx,abs(o[mine]-float(b[m][theirs])))
print('\nmax abs diff vs build zk_v2.csv (pp):',mx)
