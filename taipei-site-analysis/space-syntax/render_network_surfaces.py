"""Closed, editable cartographic network envelopes; buffers do not modify routing topology."""
from shapely.geometry import LineString,Polygon,box,mapping
from shapely.ops import unary_union,transform as geom_transform
clip=box(minx,miny,maxx,maxy)
width_table={r['id']:r for r in json.load(gzip.open(ROOT/'taipei-site-analysis/maps/infrastructure/full-corridor/road-width-basis.json.gz','rt'))}
way_lookup={w['id']:w for w in ways}
road_shapes=[];width_audit=[]
def numeric_width(tags,default):
 try:return max(.5,min(30,float(tags.get('width',default))))
 except (ValueError,TypeError):return default
for w in ways:
 t=w.get('tags',{});geo=w.get('geometry',[])
 if t.get('highway') not in {'primary','secondary','tertiary','residential','unclassified','service','living_street'} or grade(t)!='surface' or len(geo)<2:continue
 if not any(minx-50<=xy[n][0]<=maxx+50 and miny-50<=xy[n][1]<=maxy+50 for n in w['nodes']):continue
 wr=width_table.get(w['id']);width=wr['width_m'] if wr else numeric_width(t,4)
 shape=LineString([xy[n] for n in w['nodes']]).buffer(width/2,cap_style=2,join_style=2).intersection(clip)
 if not shape.is_empty:road_shapes.append(shape);width_audit.append({'way':w['id'],'width_m':width,'basis':wr['basis'] if wr else 'osm_width_or_4m_display_default','purpose':'cartographic envelope only; source width may include sidewalks'})
road_surface=unary_union(road_shapes)

def polygon_path(geom):
 polygons=[geom] if geom.geom_type=='Polygon' else [p for p in getattr(geom,'geoms',[]) if p.geom_type=='Polygon']
 result=[]
 for poly in polygons:
  for ring in [poly.exterior,*poly.interiors]:
   ps=[P(q) for q in ring.coords];result.append('M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in ps)+' Z')
 return ' '.join(result)

def filled(geom,color,stroke='#84928e',weight=.7):
 return f'<path d="{polygon_path(geom)}" fill="{color}" fill-rule="evenodd" stroke="{stroke}" stroke-width="{weight}" stroke-linejoin="round"/>'

def render_surfaces(case,g):
 walk=[];vertical=[]
 for e in edge_records:
  a,b=e['a'],e['b']
  if a not in g or b not in g[a]:continue
  p,q=positions[a],positions[b]
  if not (minx-30<=p[0]<=maxx+30 and miny-30<=p[1]<=maxy+30 or minx-30<=q[0]<=maxx+30 and miny-30<=q[1]<=maxy+30):continue
  t=way_lookup.get(e['way'],{}).get('tags',{});width=numeric_width(t,2.0)
  if e['group']=='restored_alley':width=width_table.get(e['way'],{}).get('width_m',3.0)
  poly=LineString([p,q]).buffer(width/2,cap_style=1,join_style=2).intersection(clip)
  (vertical if a not in A or b not in A[a] else walk).append(poly)
 ground=unary_union(walk);up=unary_union(vertical);outer=unary_union([road_surface,ground,up])
 assert outer.is_valid and ground.is_valid
 # Closed polygons with interior holes retained. No polygon union is used to infer routable crossings.
 parts=[f'<g id="road-network">{filled(road_surface,"#dde1df","#b5bfbb",.55)}</g>',f'<g id="pedestrian-network">{filled(ground,"#a8beb4","#738d80",.65)}</g>']
 if not up.is_empty:parts.append(f'<g id="bridge-network">{filled(up,"#7dabbc","#426d80",.8)}</g>')
 parts.append(f'<g id="outer-boundaries"><path d="{polygon_path(outer)}" fill="none" stroke="#82958b" stroke-width=".55"/></g>')
 features=[]
 for label,geom in [('road',road_surface),('pedestrian',ground),('bridge',up),('outer_boundary_area',outer)]:
  if not geom.is_empty:features.append({'type':'Feature','properties':{'layer':label,'case':case,'geometry_status':'source-width and display-width envelope; not surveyed outer curb','default_walk_width_m':2},'geometry':mapping(geom_transform(inverse,geom))})
 (OUT/(case+'-surfaces.geojson.gz')).write_bytes(gzip.compress(json.dumps({'type':'FeatureCollection','features':features},ensure_ascii=False,separators=(',',':')).encode(),mtime=0))
 return ''.join(parts)
json.dump({'road_widths':width_audit,'pedestrian_default_width_m':2,'alley_default_width_m':3,'width_warning':'Mapped width where numeric; otherwise display assumption. Road widths can already include sidewalks; not an area quantity survey.','union_warning':'Closed drawing envelopes do not connect graph nodes or imply all gray roads are walkable.'},open(OUT/'surface-width-audit.json','w'),ensure_ascii=False,indent=2)
