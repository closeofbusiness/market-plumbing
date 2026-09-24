import re, sqlite3, sys, os
db = 'z1.db'
if os.path.exists(db): os.remove(db)
con = sqlite3.connect(db); cur=con.cursor()
cur.execute("CREATE TABLE obs(series TEXT, period TEXT, value REAL)")
cur.execute("CREATE TABLE meta(series TEXT PRIMARY KEY, descr TEXT, mult REAL)")
ser_re = re.compile(r'SERIES_NAME="([^"]+)"')
mult_re = re.compile(r'UNIT_MULT="([^"]+)"')
obs_re = re.compile(r'OBS_VALUE="([^"]*)" TIME_PERIOD="([^"]+)"')
ann_re = re.compile(r'<common:AnnotationText>(.*?)</common:AnnotationText>')
cur_ser=None; cur_mult=1.0; pending_desc=None; want_desc=False
rows=[]; metas=[]
n=0
with open('Z1_data.xml','r',encoding='utf-8',errors='replace') as f:
    for line in f:
        if '<kf:Series ' in line:
            m=ser_re.search(line)
            cur_ser=m.group(1) if m else None
            mm=mult_re.search(line); cur_mult=float(mm.group(1)) if mm else 1.0
            pending_desc=None
        elif '<common:AnnotationType>Short Description' in line:
            want_desc=True
        elif want_desc and '<common:AnnotationText>' in line:
            a=ann_re.search(line); pending_desc=a.group(1) if a else None
            want_desc=False
            if cur_ser: metas.append((cur_ser,pending_desc,cur_mult))
        elif '<frb:Obs ' in line:
            o=obs_re.search(line)
            if o and cur_ser and o.group(1)!='':
                try: v=float(o.group(1))
                except: continue
                rows.append((cur_ser,o.group(2),v)); n+=1
                if len(rows)>500000:
                    cur.executemany("INSERT INTO obs VALUES(?,?,?)",rows); rows=[]
cur.executemany("INSERT INTO obs VALUES(?,?,?)",rows)
cur.executemany("INSERT OR REPLACE INTO meta VALUES(?,?,?)",metas)
cur.execute("CREATE INDEX i1 ON obs(series,period)")
con.commit()
print("obs",n,"series",len(metas))
