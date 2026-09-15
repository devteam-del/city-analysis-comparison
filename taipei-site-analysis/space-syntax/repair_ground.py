"""Source-tag repair. Executed inside calculate_accessibility.py after ground graph construction.
No XY snapping, no automatic street-junction crossings, no changes to fixed OD nodes.
"""
from shapely.geometry import LineString,Point
from shapely.ops import nearest_points
inverse=Transformer.from_crs(3826,4326,always_xy=True).transform
node_tags=json.load(open(D/'ground-node-tags.json'))
width_rows=json.load(gzip.open(ROOT/'taipei-site-analysis/maps/infrastructure/full-corridor/road-width-basis.json.gz','rt'))
widths={e['id']:e for e in width_rows}
local=lambda e:any(121.508<p['lon']<121.5215 and 25.047<p['lat']<25.053 for p in e.get('geometry',[]))
roadtypes={'primary','secondary','tertiary','residential','unclassified','service','living_street'}
roads=[e for e in ways if e.get('tags',{}).get('highway') in roadtypes and local(e) and grade(e['tags'])=='surface']
road_by_id={e["id"]:e for e in roads}
inc=collections.defaultdict(set)
for e in roads:
 for n in e['nodes']:inc[n].add(e['id'])
audit=[];serial=-1

def synthetic(p,label):
 global serial
 serial-=1;key=(serial,label);positions[key]=p;ll[serial]=inverse(*p);return key

def repair_edge(a,b,length,way,kind,details):
 add(A,a,b,length);add(B,a,b,length)
 edge_records.append(dict(way=way,a=a,b=b,length=length,group=kind,evidence=details))

for e in roads:
 t=e['tags'];ns=e['nodes']
 if t.get('foot') in ['no','private'] or t.get('access') in ['no','private'] or any(n in blocked for n in ns):continue
 if t.get('highway')=='service' and t.get('service')=='alley' and t.get('name'):
  keys={};isolated=[]
  for n in ns:
   # Shared road centres must not become new unverified crossing junctions.
   if len(inc[n])>1 and node_tags.get(str(n),{}).get('highway')!='crossing':
    keys[n]=synthetic(xy[n],'alley_end');isolated.append(n)
   else:keys[n]=(n,'surface');positions[keys[n]]=xy[n]
  for a,b in zip(ns,ns[1:]):repair_edge(keys[a],keys[b],math.dist(xy[a],xy[b]),e['id'],'restored_alley','named OSM alley; unrestricted in source, shared road junctions isolated unless tagged crossing')
  audit.append({'way':e['id'],'name':t['name'],'kind':'restored_alley','unverified_junction_nodes_left_unjoined':isolated})
  continue
 sw=t.get('sidewalk');sides=[]
 for side in ['left','right']:
  explicit=t.get('sidewalk:'+side,t.get('sidewalk:both'))
  if explicit=='yes' or (explicit is None and sw in ['both',side]):sides.append(side)
 if not sides:continue
 wr=widths.get(e['id']);width=wr['width_m'] if wr else None
 if not width:continue
 # Source class widths are a sensitivity assumption, never surveyed curb coordinates.
 offset=width/2
 for side in sides:
  sg=1 if side=='left' else -1
  # Major street intersections remain cut. For three reviewed roads only, service access mouths use an explicit continuity assumption.
  reviewed_road=e['id'] in {244450426,33679741,33679832} and '--conservative-junctions' not in sys.argv
  def must_cut(n):
   others=[road_by_id[r]['tags'] for r in inc[n] if r!=e['id']]
   if not reviewed_road:return bool(others)
   return any(t.get('highway')!='service' for t in others)
  cuts=sorted({0,len(ns)-1}|{i for i,n in enumerate(ns) if must_cut(n)})
  for lo,hi in zip(cuts,cuts[1:]):
   base=LineString([xy[n] for n in ns[lo:hi+1]])
   if base.length<2:continue
   curve=base.offset_curve(sg*offset)
   if curve.geom_type!='LineString' or curve.is_empty:continue
   anchors=[]
   for i in range(lo,hi+1):
    n=ns[i];k=(n,'surface')
    if k not in A:continue
    before=xy[ns[max(lo,i-1)]];after=xy[ns[min(hi,i+1)]];tx,ty=after[0]-before[0],after[1]-before[1]
    for neighbor in list(A[k]):
     # Only original mapped footways can anchor an inferred sidewalk.
     if neighbor[1]!='surface' or neighbor[0]<0:continue
     q=positions[neighbor];vx,vy=q[0]-xy[n][0],q[1]-xy[n][1]
     cross=tx*vy-ty*vx
     if cross*sg<=0:continue
     footway_exists=any(rec['group']=='surface' and {rec['a'],rec['b']}=={k,neighbor} for rec in edge_records)
     if not footway_exists:continue
     footseg=LineString([xy[n],q]);hit=footseg.intersection(curve)
     target_hit=hit
     if hit.is_empty:
      near_foot,near_curb=nearest_points(footseg,curve)
      if near_foot.distance(near_curb)<=1.0:hit=near_foot;target_hit=near_curb
     if hit.geom_type=='Point' and not hit.is_empty:
      hp=(hit.x,hit.y);pos=curve.project(target_hit)
      # Insert an attachment ON the existing footway, not at its distant end.
      anchor=synthetic(hp,'source_footway_split')
      repair_edge(k,anchor,math.dist(xy[n],hp),e['id'],'source_footway_split','cost-preserving subdivision of an existing mapped footway')
      repair_edge(anchor,neighbor,math.dist(hp,q),e['id'],'source_footway_split','cost-preserving subdivision of an existing mapped footway')
      anchors.append((pos,anchor,(target_hit.x,target_hit.y),hit.distance(target_hit)))
     else:
      pos=curve.project(Point(q));target=curve.interpolate(pos);gap=Point(q).distance(target)
      if gap>max(3,offset):continue
      anchors.append((pos,neighbor,(target.x,target.y),gap))
   anchors=sorted({(round(a,6),b,c,d) for a,b,c,d in anchors})
   if len({a[1] for a in anchors})<2:continue
   chain=[]
   # Include actual offset-curve vertices so SVG and edge cost describe the same path.
   for q in curve.coords:chain.append((curve.project(Point(q)),None,tuple(q),0))
   chain+=anchors;chain.sort(key=lambda a:a[0]);prior=None
   for station,k,p,gap in chain:
    u=synthetic(p,'inferred_sidewalk')
    if prior:repair_edge(prior[1],u,station-prior[0],e['id'],'inferred_sidewalk','side-specific offset; '+wr['basis'])
    if k:repair_edge(k,u,gap,e['id'],'inferred_sidewalk','inferred same-side attachment to mapped footway; no field verification')
    prior=(station,u)
   audit.append({'way':e['id'],'name':t.get('name'),'kind':'inferred_sidewalk','side':side,'source_nodes':[ns[lo],ns[hi]],'width_m':width,'width_basis':wr['basis'],'anchors':[a[1][0] for a in anchors],'max_attachment_m':max(a[3] for a in anchors),'status':'conditional_geometry_not_surveyed','service_access_continuity_assumed':reviewed_road,'service_junction_nodes':[n for n in ns[lo:hi+1] if len(inc[n])>1 and not must_cut(n)]})
json.dump(audit,open(OUT/'ground-repair-audit.json','w'),ensure_ascii=False,indent=2)
