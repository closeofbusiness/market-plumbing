import csv, os
SCR="/private/tmp/claude-501/-Users-martinschroeder-Downloads/c58870c4-abdd-4920-bbdd-957d69c89922/scratchpad/n2b_v2"
DBX=os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), "data")  # repo root, wherever it is cloned (was the author's Dropbox path before 24 Sep 2026)
def rd(p): return list(csv.DictReader(open(p)))
def hist(n):
    return {r["as_of"][:7]:float(r["value"]) for r in rd(f"{DBX}/history/{n}.csv") if r["value"] not in ("",".")}
tsy,agy,oth,fed,ltdv1=[hist(n) for n in ("mmf_treasury_repo_bn","mmf_agency_repo_bn","mmf_repo_other_collateral_bn","mmf_repo_with_fed_bn","large_time_deposits_bn")]
h8={r["as_of"]:(float(r["total_deposits_bn"]),float(r["large_time_deposits_bn"])) for r in rd(f"{SCR}/h8.csv")}
m2={r["as_of"][:7]:(float(r["m2_bn"]),float(r["currency_bn"]),float(r["retail_mmf_bn"])) for r in rd(f"{SCR}/m2.csv")}
alf={r["observation_date"][:7]:float(r["M2SL_20260815"]) for r in rd(f"{DBX}/vintages/alfred/alf_M2SL_2026-08-15.csv") if r["M2SL_20260815"] not in ("",".")}
hf={r["as_of"][:7]:float(r["value"])/1e9 for r in rd(f"{SCR}/formpf.csv") if r["mnemonic"]=="FPF-ASSETCLASS_REPO_REVERSEREPO_SUM"}
z1={}
for r in rd(f"{SCR}/z1.csv"):
    y,q=r["as_of"].split("Q"); z1[f"{y}-{ {'1':'03','2':'06','3':'09','4':'12'}[q]}"]=(float(r["hh_checkable_currency_bn"]),float(r["hh_time_savings_bn"]),float(r["fhlb_advances_bn"]))
Q=["2021-12"]+[f"{y}-{m}" for y in range(2022,2027) for m in ("03","06","09","12")]
Q=[q for q in Q if q<="2026-03"]   # full-input window
lab=lambda q: f"{q[:4]}Q{(int(q[5:])+2)//3}"
z=lambda W,D:100*W/(W+D)
G={}; raw={}
for q in Q:
    pr=tsy[q]+agy[q]+oth[q]-fed[q]; ltd=h8[q][1]
    W1=pr+ltd; W2=W1+hf[q]; W3=W2+z1[q][2]
    D1=alf[q]; D2=m2[q][0]-m2[q][1]-m2[q][2]; D3=h8[q][0]-ltd; D4=z1[q][0]+z1[q][1]
    raw[q]=dict(priv_repo=pr,ltd=ltd,hf=hf[q],fhlb=z1[q][2],W1=W1,W2=W2,W3=W3,D1=D1,D2=D2,D3=D3,D4=D4,fedincl=z(W1+fed[q],D1),v1chk=z(pr+ltdv1[q],D1))
    for wn,W in (("W1",W1),("W2",W2),("W3",W3)):
        for dn,D in (("D1",D1),("D2",D2),("D3",D3),("D4",D4)):
            G[(wn,dn,q)]=z(W,D)
pairs=[(w,d) for w in ("W1","W2","W3") for d in ("D1","D2","D3","D4")]
# 1. compare to build's csv
built={r["quarter"]:r for r in rd(f"{SCR}/zk_v2.csv")}
mx=max(abs(G[(w,d,q)]-float(built[q][f"z_{w}_{d}_pct"])) for (w,d) in pairs for q in Q)
print(f"max |mine - build| over 12x18 grid = {mx:.6f} pp")
# 2. min/max per pair, and where
print("\npair | start 2021Q4 | end 2026Q1 | min (qtr) | max (qtr) | end/start ratio | end-start pp | end==max? | end<max by")
for w,d in pairs:
    s=[(G[(w,d,q)],q) for q in Q]; mn=min(s); mxv=max(s)
    a=G[(w,d,"2021-12")]; b=G[(w,d,"2026-03")]
    print(f"{w}/{d} | {a:.2f} | {b:.2f} | {mn[0]:.2f} ({lab(mn[1])}) | {mxv[0]:.2f} ({lab(mxv[1])}) | {b/a:.2f}x | {b-a:+.2f} | {'yes' if mxv[1]=='2026-03' else 'no'} | {mxv[0]-b:.2f}")
# 3. direction from every start date 2021Q4..2024Q4 to end 2026Q1 (and to alt end 2025Q4)
starts=[q for q in Q if q<="2024-12"]
print("\nDirection test: z(end) > z(start) for every pair, every start 2021Q4..2024Q4")
for end in ("2026-03","2025-12"):
    fails=[(w,d,lab(s),round(G[(w,d,s)],2),round(G[(w,d,end)],2)) for (w,d) in pairs for s in starts if G[(w,d,end)]<=G[(w,d,s)]]
    print(f" end={lab(end)}: failures={fails if fails else 'NONE'}")
# minimum rise from any start
print("\nSmallest end-minus-start rise across starts (worst case per pair), end 2026Q1:")
for w,d in pairs:
    worst=min((G[(w,d,"2026-03")]-G[(w,d,s)],s) for s in starts)
    ratios={s:G[(w,d,"2026-03")]/G[(w,d,s)] for s in starts}
    print(f" {w}/{d}: min rise {worst[0]:+.2f}pp from {lab(worst[1])}; ratio from 2021Q4 {ratios['2021-12']:.2f}x, from 2022Q2 {ratios['2022-06']:.2f}x, from 2023Q4 {ratios['2023-12']:.2f}x, from 2024Q4 {ratios['2024-12']:.2f}x")
# 4. same-shape: sign of q/q change per pair
print("\nQ/Q sign matrix (+/-/0 with |d|<0.05 as 0), rows=pairs, cols=quarters from 2022Q1:")
print(" "*8+" ".join(lab(q)[2:] for q in Q[1:]))
for w,d in pairs:
    sg=""
    for i in range(1,len(Q)):
        dd=G[(w,d,Q[i])]-G[(w,d,Q[i-1])]
        sg+=("  +   " if dd>0.05 else ("  -   " if dd<-0.05 else "  0   "))
    print(f"{w}/{d:3s} {sg}")
# 5. headline numeric claims
r=raw
print("\nHeadline claims:")
print(f" W1/D1 2021Q4 {G[('W1','D1','2021-12')]:.2f} -> 2026Q1 {G[('W1','D1','2026-03')]:.2f}, ratio {G[('W1','D1','2026-03')]/G[('W1','D1','2021-12')]:.2f}x (claim 2.10x, 9.14->19.24)")
print(f" W2/D1 2021Q4 {G[('W2','D1','2021-12')]:.2f} -> 2026Q1 {G[('W2','D1','2026-03')]:.2f}, ratio {G[('W2','D1','2026-03')]/G[('W2','D1','2021-12')]:.2f}x (claim 1.76x, 13.10->23.07)")
print(f" HF leg 2021Q4 {r['2021-12']['hf']:.0f}bn -> 2026Q1 {r['2026-03']['hf']:.0f}bn, growth {r['2026-03']['hf']/r['2021-12']['hf']-1:+.1%} (claim ~1.1trn, ~+30%)")
print(f" W1 (MMF priv repo + LTD) 2021Q4 {r['2021-12']['W1']:.1f} -> 2026Q1 {r['2026-03']['W1']:.1f}, x{r['2026-03']['W1']/r['2021-12']['W1']:.2f} (claim 2.5x)")
print(f" W2/D1 2022Q4->2023Q4: {G[('W2','D1','2023-12')]-G[('W2','D1','2022-12')]:+.2f}pp (claim +6.0pp)")
print(f" trough W1/D1 {min(G[('W1','D1',q)] for q in Q):.2f} at {lab(min(Q,key=lambda q:G[('W1','D1',q)]))}; W2/D1 {min(G[('W2','D1',q)] for q in Q):.2f} at {lab(min(Q,key=lambda q:G[('W2','D1',q)]))} (claim 8.47 / 12.36 at 2022Q2)")
print(f" W3/D1 - W2/D1 gap by quarter: "+", ".join(f"{lab(q)} {G[('W3','D1',q)]-G[('W2','D1',q)]:.2f}" for q in Q))
print(f" W3/D1 rise 2023Q4->2026Q1 {G[('W3','D1','2026-03')]-G[('W3','D1','2023-12')]:+.2f}pp vs W2/D1 {G[('W2','D1','2026-03')]-G[('W2','D1','2023-12')]:+.2f}pp (claim: W3 flattens rise)")
print(f" FHLB: 2023Q1 {r['2023-03']['fhlb']:.1f}, 2026Q1 {r['2026-03']['fhlb']:.1f}, max {max(r[q]['fhlb'] for q in Q):.1f} at {lab(max(Q,key=lambda q:r[q]['fhlb']))}")
fi=[r[q]['fedincl'] for q in Q]; print(f" Fed-incl W1/D1 min {min(fi):.2f} max {max(fi):.2f} (claim flat 15-20)")
print(f" plateau W2/D1 2025Q2..2026Q1: "+", ".join(f"{G[('W2','D1',q)]:.2f}" for q in ('2025-06','2025-09','2025-12','2026-03')))
print(f" plateau W2/D3 2025Q2..2026Q1: "+", ".join(f"{G[('W2','D3',q)]:.2f}" for q in ('2025-06','2025-09','2025-12','2026-03')))
print(" 2026Q1 vs 2025Q4 per pair: "+", ".join(f"{w}/{d} {G[(w,d,'2026-03')]-G[(w,d,'2025-12')]:+.2f}" for w,d in pairs))
print(" 2024Q4 vs 2024Q3 per pair: "+", ".join(f"{w}/{d} {G[(w,d,'2024-12')]-G[(w,d,'2024-09')]:+.2f}" for w,d in pairs))
print(" 2025Q3 vs 2025Q2 per pair: "+", ".join(f"{w}/{d} {G[(w,d,'2025-09')]-G[(w,d,'2025-06')]:+.2f}" for w,d in pairs))
print(" v1 chk (v1 LTD/D1) at v1 dates: "+", ".join(f"{lab(q)} {r[q]['v1chk']:.2f}" for q in ("2021-12","2022-12","2023-06","2023-12","2024-06","2024-12","2025-06","2025-12")))
# 6. the HF dilution claim: decompose W2 rise
print(f"\n W2 rise 2021Q4->2026Q1 {r['2026-03']['W2']-r['2021-12']['W2']:.0f}bn = W1 {r['2026-03']['W1']-r['2021-12']['W1']:.0f} + HF {r['2026-03']['hf']-r['2021-12']['hf']:.0f}; HF share of W2 at start {r['2021-12']['hf']/r['2021-12']['W2']:.1%}, at end {r['2026-03']['hf']/r['2026-03']['W2']:.1%}")
print(f" Private repo leg 2021Q4 {r['2021-12']['priv_repo']:.1f} -> 2026Q1 {r['2026-03']['priv_repo']:.1f}; LTD {r['2021-12']['ltd']:.1f} -> {r['2026-03']['ltd']:.1f}")
# 7. W1 rise decomposition: how much of z rise is D1 falling vs W1 rising (2021Q4->2023Q4)
a,b='2021-12','2023-12'
print(f" 2021Q4->2023Q4: W1 {r[a]['W1']:.0f}->{r[b]['W1']:.0f} (x{r[b]['W1']/r[a]['W1']:.2f}); D1 {r[a]['D1']:.0f}->{r[b]['D1']:.0f} ({r[b]['D1']/r[a]['D1']-1:+.1%}); z with D1 frozen at 2021Q4: {z(r[b]['W1'],r[a]['D1']):.2f} vs actual {G[('W1','D1',b)]:.2f}")
