from pathlib import Path
import json,gzip,xml.etree.ElementTree as E
B=Path('taipei-site-analysis/maps/infrastructure/full-corridor');features={};nodes={};ways={};rels={}
for p in json.load(open('/tmp/civic-api/index.json')):
 r=E.parse(p).getroot()
 for n in r.findall('node'):nodes[n.get('id')]={'lon':float(n.get('lon')),'lat':float(n.get('lat'))}
 for w in r.findall('way'):ways[w.get('id')]=w
 for r in r.findall('relation'):rels[r.get('id')]=r
for key,w in ways.items():
 t={a.get('k'):a.get('v') for a in w.findall('tag')};ids=[a.get('ref') for a in w.findall('nd')]
 if not any(k in t for k in ['building','highway','leisure','landuse','railway','amenity']):continue
 if not all(i in nodes for i in ids):continue
 features[('way',int(key))]={'type':'way','id':int(key),'tags':t,'nodes':list(map(int,ids)),'geometry':[nodes[i] for i in ids]}
for key,r in rels.items():
 t={a.get('k'):a.get('v') for a in r.findall('tag')}
 if t.get('leisure')!='park':continue
 members=[]
 for m in r.findall('member'):
  w=features.get(('way',int(m.get('ref')))) if m.get('type')=='way' else None
  # Untagged boundary ways must also be reconstructed.
  if not w and m.get('type')=='way' and m.get('ref') in ways:
   ids=[a.get('ref') for a in ways[m.get('ref')].findall('nd')]
   if all(i in nodes for i in ids):w={'geometry':[nodes[i] for i in ids]}
  if w:members.append({'type':'way','ref':int(m.get('ref')),'role':m.get('role'),'geometry':w['geometry']})
 features[('relation',int(key))]={'type':'relation','id':int(key),'tags':t,'members':members}
for i in [3,4]:
 d=json.load(open(f'/tmp/civic-full-{i}.json'));assert d.get('elements') and not d.get('remark')
 for e in d['elements']:features[(e['type'],e['id'])]=e
for e in json.load(open('/tmp/full-civic-route.json'))['elements']:features[(e['type'],e['id'])]=e
(B/'geometry.json.gz').write_bytes(gzip.compress(json.dumps({'retrieved':'2026-09-15','source':'OpenStreetMap API and Overpass kumi','bbox':[121.501,25.037,121.623,25.061],'elements':list(features.values())},ensure_ascii=False).encode()))
print('Saved',len(features),'features')
