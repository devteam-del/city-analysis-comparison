from pathlib import Path
import json,csv,re,gzip,math
b=Path('taipei-site-analysis/space-syntax');src=json.load(open(b/'sources/od-replacement/source-nodes.json'));out=[];used=set()
def add(id,name,lon,lat,kind,osm=None,basis='OSM source point',**kw):
 if osm and str(osm) in used:return
 if osm:used.add(str(osm))
 out.append(dict(id=id,name=name,lon=lon,lat=lat,kind=kind,osm_id=int(osm) if osm else None,coordinate_basis=basis,**kw))
def node(id,name,n,kind,**kw):
 x=src[str(n)];add(id,name,x['lon'],x['lat'],kind,n,**kw)
for r in csv.DictReader(open(b/'sources/exits.csv',encoding='cp950',errors='replace')):
 name=r['出入口名稱'];prefix=next((p for s,p in [('北門站','BM'),('台北車站','TP'),('善導寺站','SD')] if name.startswith(s)),None)
 if not prefix:continue
 ref=r['出入口編號'];add(prefix+'-'+ref,name,float(r['經度']),float(r['緯度']),'metro',basis='official sources/exits.csv')
# Explicit airport exit mapping; the user-confirmed closed 2/4/7 are not selected.
for k,n in {1:5021873865,3:5021873867,5:5021873868,6:5021873869}.items():node('A1-'+str(k),'機捷台北車站出口'+str(k),n,'airport_metro',operation_status='candidate not independently current-gate verified')
bus=json.load(open(b/'transport-bus-source-candidates.json'))['candidates']
for n,x in src.items():
 if x['tags'].get('highway')=='bus_stop' and x['tags'].get('name')=='臺北車站(公園)' and n not in {v['osm_id'] for v in bus}:bus.append(dict(osm_id=n,lon=x['lon'],lat=x['lat'],name=x['tags']['name']))
for r in bus: add('BUS-'+r['osm_id'],r['name']+(('／'+r['local_ref']) if r.get('local_ref') else ''),r['lon'],r['lat'],'bus',r['osm_id'])
for f in json.load(open(b/'candidate-access-points.geojson'))['features']:
 t=f['properties']['tags'];ref=t.get('ref',t.get('name',''));n=f['id']
 if t.get('access') in ['private','no'] or t.get('emergency')=='yes' or t.get('level','0').startswith('-'):continue
 if ref in ['Y18','Y22']:continue
 if re.fullmatch(r'[YKRZ]\d+',ref):node('UG-'+ref,ref+'地面出口',n,'mall_access')
 elif re.fullmatch(r'[東西南北][123]門',ref):node('TRA-'+ref,'台北車站'+ref,n,'rail_station')
# Geographic sampling anchors are disclosed as street-frontage representatives, not surveyed doors.
for id,name,lon,lat in [('C1','京站承德門周邊',121.51704,25.04930),('C2','華陰街×太原路',121.51516,25.05021),('C3','華陰街×重慶北路',121.51375,25.05048),('C5','南陽街×許昌街',121.51612,25.04551),('C6','華山市場入口周邊',121.52481,25.04424),('C7','善導寺忠孝東路入口周邊',121.52528,25.04453),('BT','台北轉運站市民大道旅客入口周邊',121.51853,25.04874)]:
 add(id,name,lon,lat,'commercial' if id!='BT' else 'bus_terminal',basis='named street-frontage selection anchor; approximate, not surveyed door',frontage_proxy=True)
node('C4','新光三越站前店地面入口',5644385151,'commercial')
# Match official exits to OSM entrance counterparts only by station locality and exit ref.
for s in out:
 if s['kind']!='metro':continue
 ref=s['id'].split('-')[1];ref=('M'+ref if s['id'].startswith('TP-') and not ref.startswith('M') else ref)
 cand=[]
 for n,x in src.items():
  t=x['tags'];d=math.hypot((x['lon']-s['lon'])*100800,(x['lat']-s['lat'])*110800)
  if t.get('railway')=='subway_entrance' and t.get('ref')==ref and d<45:cand.append((d,n))
 if cand:s['osm_id']=int(min(cand)[1])
assert out and not any(re.fullmatch('[NS][1-8]',s['id']) for s in out)
(b/'selected-od-inputs.json').write_text(json.dumps(out,ensure_ascii=False,indent=2)+'\n');print(len(out),{k:sum(x['kind']==k for x in out) for k in {x['kind'] for x in out}})
