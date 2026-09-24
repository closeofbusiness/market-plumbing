import urllib.request, csv, io, sys
B="https://stats.bis.org/api/v2/data/dataflow/BIS/WS_LBS_D_PUB/1.0/"
def get(key, n=1, extra=""):
    u=B+key+"?format=csv&lastNObservations=%d"%n+extra
    try:
        r=urllib.request.urlopen(u, timeout=90).read().decode()
    except Exception as e:
        return []
    if r.lstrip().startswith("<"): return []
    rows=list(csv.DictReader(io.StringIO(r)))
    return rows
if __name__=="__main__":
    pass
