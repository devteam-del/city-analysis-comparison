import xml.etree.ElementTree as E,json,gzip
from pathlib import Path
nodes={};ways={};rels={}
for i in range(4):
 r=E.parse(f'/tmp/site-tile-{i}.xml').getroot()
 for n in r.findall('node'):nodes[n.get('id')]={'lon':float(n.get('lon')),'lat':float(n.get('lat'))}
 for w in r.findall('way'):ways[w.get('id')]=w
 for w in r.findall('relation'):rels[w.get('id')]=w
es=[]
for wid,w in ways.items():
 t={a.get('k'):a.get('v') for a in w.findall('tag')};ids=[a.get('ref') for a in w.findall('nd')]
 if not any(k in t for k in ['building','highway','leisure','landuse']) and not '廣場' in t.get('name',''):continue
 if not all(i in nodes for i in ids):continue
 g=[nodes[i] for i in ids]
 es.append({'type':'way','id':int(wid),'tags':t,'nodes':list(map(int,ids)),'geometry':g})
 for k in ['leisure','landuse']:
  if t.get(k) in ['park','garden','grass']:print(wid,t.get('name'),t.get(k),len(g))
p=Path('taipei-site-analysis/maps/infrastructure');p.mkdir(exist_ok=True)
(p/'source-geometry.json.gz').write_bytes(gzip.compress(json.dumps({'source':'OpenStreetMap API /api/0.6/map','retrieved':'2026-09-14','bbox':[121.503,25.043,121.524,25.055],'elements':es,'note':'Closed ways only for area analysis. Relations not reconstructed; coverage is not completeness.'},ensure_ascii=False).encode()))
print('features',len(es))
