import urllib.request,xml.etree.ElementTree as ET,concurrent.futures,json,time
from pathlib import Path
# Public OSM API only, small bounded map requests; split only if API reports node-count limit.
out=Path('/tmp/civic-api');out.mkdir(exist_ok=True)
boxes=[(round(121.501+i*.0125,5),a,round(121.501+(i+1)*.0125,5),b) for i in range(6) for a,b in [(25.037,25.049),(25.049,25.061)]]
def fetch(v):
 key='_'.join(map(str,v));p=out/(key+'.xml')
 for attempt in range(3):
  try:
   if p.exists():s=p.read_bytes()
   else:
    with urllib.request.urlopen('https://api.openstreetmap.org/api/0.6/map?bbox='+','.join(map(str,v)),timeout=65) as r:s=r.read()
   root=ET.fromstring(s);p.write_bytes(s);print('OK',key,len(s),flush=True);return[str(p)]
  except urllib.error.HTTPError as e:
   msg=e.read().decode(errors='replace')
   if 'too many nodes' in msg:
    x,y,X,Y=v;m=(y+Y)/2;return fetch((x,y,X,m))+fetch((x,m,X,Y))
   print('HTTP',key,e.code,flush=True)
  except Exception as e:print('retry',key,str(e)[:70],flush=True)
 raise RuntimeError(key)
with concurrent.futures.ThreadPoolExecutor(max_workers=3) as ex:
 files=[p for r in ex.map(fetch,boxes) for p in r]
(out/'index.json').write_text(json.dumps(files));print('ALL COMPLETE',len(files),flush=True)
