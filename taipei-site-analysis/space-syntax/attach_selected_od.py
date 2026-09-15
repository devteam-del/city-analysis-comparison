"""Select named facilities; attach only to nearby ground edges, never across road centres.
Unresolved selections remain isolated and visible, rather than forced into the main component.
"""
from shapely.strtree import STRtree
from shapely.geometry import LineString,Point
inputs=json.load(open(D/'selected-od-inputs.json'))
segs=[];pairs=[]
for u,adj in A.items():
 for v in adj:
  if u>=v or math.dist(positions[u],positions[v])<1e-5:continue
  pairs.append((u,v));segs.append(LineString([positions[u],positions[v]]))
tree=STRtree(segs)
barriers=[LineString([xy[n] for n in w['nodes']]) for w in ways if w.get('tags',{}).get('highway') in ['primary','secondary','tertiary','trunk'] and grade(w['tags'])=='surface' and len(w.get('nodes',[]))>1]
btree=STRtree(barriers)
axis=[]
for w in ways:
 t=w.get('tags',{})
 if '市民大道' not in t.get('name','') or t.get('highway') not in ['primary','secondary','trunk']:continue
 for a,b in zip(w.get('geometry',[]),w.get('geometry',[])[1:]):
  if abs(a['lon']-b['lon'])>1e-8:axis.append((a,b))
def side(lon,lat):
 ys=[a['lat']+(lat2['lat']-a['lat'])*(lon-a['lon'])/(lat2['lon']-a['lon']) for a,lat2 in axis if min(a['lon'],lat2['lon'])<=lon<=max(a['lon'],lat2['lon'])]
 if not ys:raise ValueError('No corridor axis at longitude '+str(lon))
 ys.sort();return 'N' if lat>ys[len(ys)//2] else 'S'
edge_attachments=collections.defaultdict(list)
samples=[];ids=collections.Counter();by_attachment={};matches=[]
for rec in inputs:
 s=dict(rec);origin=Point(project(s['lon'],s['lat']));ids[s['id']]+=1
 if ids[s['id']]>1:s['id']+='-'+str(ids[s['id']])
 key=(s.get('osm_id'),'surface');hit=None;distance=0
 if key in A:hit=key;status='source_node_on_ground_graph'
 else:
  cap=35 if s.get('frontage_proxy') else 15
  candidates=sorted((origin.distance(segs[int(i)]),int(i)) for i in tree.query(origin.buffer(cap)))
  for gap,i in candidates:
   if gap>cap:continue
   pt=segs[i].interpolate(segs[i].project(origin));connector=LineString([origin,pt])
   if gap>.05 and any(connector.crosses(barriers[int(j)]) for j in btree.query(connector)):continue
   u,v=pairs[i];q=(pt.x,pt.y)
   # Only subdivide the selected edge; this cannot merge disconnected components.
   merge=(i,round(segs[i].project(pt),1))
   if merge in by_attachment:hit=by_attachment[merge]
   elif math.dist(q,positions[u])<.1:hit=u
   elif math.dist(q,positions[v])<.1:hit=v
   else:
    hit=synthetic(q,'od_ground_attachment')
    repair_edge(u,hit,math.dist(positions[u],q),0,'od_ground_attachment','cost-preserving subdivision only')
    repair_edge(hit,v,math.dist(positions[v],q),0,'od_ground_attachment','cost-preserving subdivision only')
   edge_attachments[i].append((segs[i].project(pt),hit))
   by_attachment[merge]=hit;distance=gap;status='frontage_proxy_on_source_ground' if s.get('frontage_proxy') else 'nearby_ground_attachment_conditional';break
 if hit is None:
  hit=synthetic((origin.x,origin.y),'unresolved_od');A[hit];B[hit];status='unresolved_ground_attachment';distance=None
 s.update(node=hit,side=side(s['lon'],s['lat']),attachment_status=status,attachment_distance_m=distance,source_coordinate=[s['lon'],s['lat']],network_coordinate=list(ll[hit[0]]))
 same=next((r for r in samples if tuple(r['node'])==hit),None)
 if same:
  same.setdefault('aliases',[]).append({'id':s['id'],'name':s['name']});matches.append({'id':s['id'],'merged_into':same['id']});continue
 samples.append(s)
for i,items in edge_attachments.items():
 u,v=pairs[i];chain=sorted(set([(0.,u),(segs[i].length,v)]+items))
 for (a,k),(b,j) in zip(chain,chain[1:]):repair_edge(k,j,b-a,0,'od_ground_attachment','ordered cost-preserving subdivision of same source edge')
json.dump(samples,open(D/'fixed-sample-points.json','w'),ensure_ascii=False,indent=2)
json.dump({'selection_count':len(inputs),'physical_OD_count':len(samples),'merged':matches,'unresolved':[s for s in samples if s['attachment_status'].startswith('unresolved')],'attachment_limits_m':{'entrances_bus':15,'named_frontage_proxy':35},'no_new_graph_component_join':True,'major_road_centre_crossing_rejected':True,'not_field_verified':True},open(OUT/'selected-od-audit.json','w'),ensure_ascii=False,indent=2)
