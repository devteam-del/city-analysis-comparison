"""Conservative, reproducible source-network reachability; not Space Syntax NAIN/NACH."""
from pathlib import Path
import sys,json,gzip,math,heapq,collections,csv,html
ROOT=Path(__file__).resolve().parents[2];sys.path.insert(0,str(ROOT/'.geo-libs'))
from pyproj import Transformer
D=Path(__file__).parent;OUT=Path(sys.argv[sys.argv.index('--output')+1]) if '--output' in sys.argv else D/'results';OUT.mkdir(parents=True,exist_ok=True)
project=Transformer.from_crs(4326,3826,always_xy=True).transform
raw=json.load(gzip.open(ROOT/'taipei-site-analysis/maps/infrastructure/full-corridor/geometry.json.gz','rt'))
ways=[e for e in raw['elements'] if e.get('type')=='way']; xy={};ll={}
for e in ways:
 for n,p in zip(e.get('nodes',[]),e.get('geometry',[])):ll[n]=(p['lon'],p['lat']);xy[n]=project(*ll[n])
# Node restrictions are read from source points, never guessed by XY snapping.
points=json.load(open(D/'candidate-access-points.geojson'))['features'];blocked=set()
for f in points:
 t=f['properties']['tags'];ref=t.get('ref',t.get('name',''))
 if ref in ['Y18','Y22'] or t.get('access') in ['no','private'] or t.get('emergency')=='yes':blocked.add(int(f['id']))
BRIDGE_SOURCE_WAYS={204711168,204711170,204711171,492117320}
A=collections.defaultdict(dict);B=collections.defaultdict(dict);positions={};edge_records=[];excluded=collections.Counter();horiz=collections.defaultdict(set);surface_nodes=set()
def add(graph,a,b,length):
 if a==b:return
 if b not in graph[a] or length<graph[a][b]:graph[a][b]=length;graph[b][a]=length

def grade(t):
 if t.get('bridge') not in [None,'no']:return 'bridge'
 if t.get('tunnel')=='yes' or t.get('location')=='underground' or t.get('layer','').startswith('-') or t.get('level','').startswith('-'):return 'underground'
 if t.get('layer') not in [None,'0'] or t.get('level') not in [None,'0']:return 'other_level'
 return 'surface'

eligible=[];stairs=[]
for e in ways:
 t=e.get('tags',{});h=t.get('highway');ns=e.get('nodes',[])
 if h not in ['footway','pedestrian','path','steps']:continue
 if t.get('area')=='yes':excluded['area_boundaries_not_routes']+=1;continue
 if t.get('foot') in ['no','private'] or t.get('access') in ['private','no'] or t.get('emergency')=='yes':excluded['access_restricted']+=1;continue
 if any(n in blocked for n in ns):excluded['closed_exit_incident_ways']+=1;continue
 if len(ns)<2 or not all(n in xy for n in ns):excluded['missing_geometry']+=1;continue
 if h=='steps':stairs.append(e);continue
 g=grade(t)
 # Floors deeper than the mapped public corridor remain unverified paid-area candidates.
 if g=='other_level' or t.get('level') in ['-2','-3','-4'] or t.get('layer') in ['-2','-3','-4']:
  excluded['unverified_internal_level']+=1;continue
 if t.get('indoor')=='yes' and g=='surface':excluded['indoor_access_unverified']+=1;continue
 if g!='surface' and e['id'] not in BRIDGE_SOURCE_WAYS:
  excluded['vertical_geometry_not_verified']+=1;continue
 eligible.append((e,g))
 for n in ns:
  key=(n,g);horiz[n].add(g);positions[key]=xy[n]
  if g=='surface':surface_nodes.add(key)
 for a,b in zip(ns,ns[1:]):
  u,v=(a,g),(b,g);length=math.dist(xy[a],xy[b]);add(B,u,v,length)
  if g=='surface':add(A,u,v,length)
  edge_records.append(dict(way=e['id'],a=u,b=v,length=length,group=g,evidence='OSM source topology, not fully field verified'))
# Stair sequences preserve OSM shared IDs; only endpoints join mapped horizontal networks.
# Vertical distance unavailable: all costs are horizontal projected lengths (lower-bound proxy).
step_nodes=set()
for e in stairs:
 ns=e['nodes'];t=e['tags']
 is_surface=grade(t)=='surface' and t.get('indoor')!='yes' and horiz[ns[0]]=={'surface'} and horiz[ns[-1]]=={'surface'}
 if not is_surface and e['id'] not in BRIDGE_SOURCE_WAYS:
  excluded['stair_endpoint_not_verified']+=1;continue
 keys=[(n,'stairs') for n in ns]
 for n,k in zip(ns,keys):positions[k]=xy[n];step_nodes.add(n)
 for a,b,u,v in zip(ns,ns[1:],keys,keys[1:]):
  length=math.dist(xy[a],xy[b]);add(B,u,v,length);edge_records.append(dict(way=e['id'],a=u,b=v,length=length,group='stairs',evidence='OSM stair geometry; z not available'))
 for n,k in [(ns[0],keys[0]),(ns[-1],keys[-1])]:
  for g in horiz[n]:add(B,k,(n,g),0)
# A contains unambiguously surface-to-surface exterior stairs as well; stairs are not banned in A.
for e in stairs:
 ns=e['nodes'];t=e['tags']
 if grade(t)=='surface' and t.get('indoor')!='yes' and horiz[ns[0]]=={'surface'} and horiz[ns[-1]]=={'surface'}:
  keys=[(n,'stairs') for n in ns]
  for a,b,u,v in zip(ns,ns[1:],keys,keys[1:]):add(A,u,v,math.dist(xy[a],xy[b]))
  add(A,keys[0],(ns[0],'surface'),0);add(A,keys[-1],(ns[-1],'surface'),0)
# Explicit assumption: 12:00 normal weekday, user-defined Y corridor hours 10:30–22:00.
# No invented temporary-sidewalk alignment, plaza axis, elevator shaft, or underground joining line.
exec(compile((D/'repair_ground.py').read_text(),str(D/'repair_ground.py'),'exec'))
samples=json.load(open(D/'fixed-sample-points.json'))
for sample in samples:sample['node']=tuple(sample['node'])
def dijkstra(graph,source):
 dist={source:0};prev={};q=[(0,source)]
 while q:
  d,u=heapq.heappop(q)
  if d!=dist[u]:continue
  for v,w in graph[u].items():
   nd=d+w
   if nd<dist.get(v,math.inf):dist[v]=nd;prev[v]=u;heapq.heappush(q,(nd,v))
 return dist,prev
north=[s for s in samples if s['side']=='N'];south=[s for s in samples if s['side']=='S'];rows=[];routes=[]
for s in north:
 da,pa=dijkstra(A,s['node']);db,pb=dijkstra(B,s['node'])
 for t in south:
  a,b=da.get(t['node']),db.get(t['node']);assert a is None or (b is not None and b<=a+1e-7)
  row={'origin':s['id'],'destination':t['id'],'A_horizontal_m':round(a,2) if a is not None else None,'B_horizontal_m':round(b,2) if b is not None else None,'shorter_by_m':round(a-b,2) if a is not None and b is not None else None,'status':'both_connected' if a is not None else ('B_only_connected_in_source' if b is not None else 'unresolved_in_source')}
  for radius in [400,800,1600]:row['A_within_'+str(radius)]=a is not None and a<=radius;row['B_within_'+str(radius)]=b is not None and b<=radius
  rows.append(row)
  if True:
   for label,d,prev in [('A',a,pa),('B',b,pb)]:
    if d is None:continue
    keys=[t['node']]
    while keys[-1]!=s['node']:keys.append(prev[keys[-1]])
    keys.reverse();routes.append({'case':label,'origin':s['id'],'destination':t['id'],'horizontal_m':d,'keys':keys})
def comps(g):
 seen=set();sizes=[]
 for k in g:
  if k in seen:continue
  stack=[k];seen.add(k);count=0
  while stack:
   u=stack.pop();count+=1
   for v in g[u]:
    if v not in seen:seen.add(v);stack.append(v)
  sizes.append(count)
 return sorted(sizes,reverse=True)
summary={'status':'computed_exploratory_source_network','analysis_type':'undirected shortest horizontal route distance, Dijkstra; NOT NAIN/NACH','scope':'北門—台北車站樣區，使用已取得全段OSM線網作背景；外圍資料有限','scenario_time':'平日12:00，Y通道採使用者指定10:30–22:00','radius_type':'network horizontal projected metres','height_cost':'not included: no surveyed z; stair distance is projected proxy','nodes_A':len(A),'nodes_B':len(B),'edges_A':sum(map(len,A.values()))//2,'edges_B':sum(map(len,B.values()))//2,'components_A':len(comps(A)),'components_B':len(comps(B)),'sample_count':len(samples),'cross_side_pairs':len(rows),'connected_A':sum(r['A_horizontal_m'] is not None for r in rows),'connected_B':sum(r['B_horizontal_m'] is not None for r in rows),'B_only_pairs':sum(r['status']=='B_only_connected_in_source' for r in rows),'shorter_pairs':sum((r['shorter_by_m'] or 0)>.01 for r in rows),'radius_counts':{str(rad):{'A':sum(r['A_within_'+str(rad)] for r in rows),'B':sum(r['B_within_'+str(rad)] for r in rows)} for rad in [400,800,1600]},'excluded':dict(excluded),'limitations':['資料中不連通不等於現地不通','地面修復包含標籤推定巷弄通行、人行道偏移與接點；道路製圖寬度不是實測，詳見ground-repair-audit.json','巷弄採OSM線形，人行道含偏移推定；工區臨時人行道與地下示意圖仍未補接','無三維高程，未套用1:12推定；不宣稱真實步行時間／距離','地下連接尚無逐段核實線形，全部暫不接入；A1封閉出口不接入','B本輪只加入承德市民天橋可追溯線段；尚未完成使用者要求的地下通道模型','天橋存在有官方佐證；OSM樓梯落點尚未全部現勘，結果採其線形條件成立時的試算','半徑與背景邊界效果未充分排除','階梯及電扶梯以雙向步行代理，單向運轉未另建時間模型','抽樣為固定網絡節點，非居民或觀測人流']}
summary['ground_repair_segments']=len(audit)
summary['ground_repair_report']='ground-repair-audit.json'
summary['service_access_continuity_assumed']='--conservative-junctions' not in sys.argv
json.dump(summary,open(OUT/'summary.json','w'),ensure_ascii=False,indent=2)
json.dump(samples,open(OUT/'sample-points.json','w'),ensure_ascii=False,indent=2)
with open(OUT/'od-comparison.csv','w') as f:
 w=csv.DictWriter(f,fieldnames=list(rows[0]));w.writeheader();w.writerows(rows)
json.dump([e for e in edge_records if e['way'] in BRIDGE_SOURCE_WAYS],open(OUT/'edge-provenance.json','w'),ensure_ascii=False,indent=2)
json.dump({'type':'FeatureCollection','features':[{'type':'Feature','properties':{k:v for k,v in r.items() if k!='keys'},'geometry':{'type':'LineString','coordinates':[list(ll[k[0]]) for k in r['keys']]}} for r in routes]},open(OUT/'routes.geojson','w'),ensure_ascii=False,indent=2)
# Validation: A must be a cost-identical subgraph; additions restricted to traceable bridge ways.
assert all(v in B[u] and abs(w-B[u][v])<1e-9 for u in A for v,w in A[u].items())
assert not any(e['group']=='underground' for e in edge_records)
assert len({tuple(s['node']) for s in samples})==len(samples)
assert all(math.isfinite(w) and w>=0 for g in [A,B] for adj in g.values() for w in adj.values())
# Same extent and actual projected proportions in both editable SVG maps.
minx,miny=project(121.5088,25.0447);maxx,maxy=project(121.5203,25.0520);W=1400;H=(maxy-miny)/(maxx-minx)*W;scale=W/(maxx-minx)
def P(p):return ((p[0]-minx)*scale,(maxy-p[1])*scale)
def line(points):return ' '.join(f'{a:.2f},{b:.2f}' for a,b in map(P,points))
exec(compile((D/'render_network_surfaces.py').read_text(),str(D/'render_network_surfaces.py'),'exec'))
for case,g in [('A',A),('B',B)]:
 svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1400" height="{H:.2f}" viewBox="0 0 1400 {H:.2f}"><rect width="1400" height="100%" fill="#f2f1eb"/>']
 svg.append(render_surfaces(case,g))
 for r in routes:
  if r['case']==case and r['origin'][1:]==r['destination'][1:]:svg.append('<polyline points="'+line([positions[k] for k in r['keys']])+'" fill="none" stroke="#af613d" stroke-width="4" stroke-opacity=".75"/>')
 for s in samples:
  a,b=P(positions[s['node']]);svg.append(f'<circle cx="{a:.2f}" cy="{b:.2f}" r="5" fill="#233f49"/><text x="{a+7:.2f}" y="{b-7:.2f}" font-size="14" font-family="sans-serif">{s["id"]}</text>')
 svg.append(f'<path d="M40,{H-40:.2f} h{200*scale:.2f}" stroke="#233f49" stroke-width="4"/><text x="40" y="{H-49:.2f}" font-size="14">200 m</text>');svg.append('</svg>');(OUT/(case+'.svg')).write_text(''.join(svg))
report='# A／B 可達性：來源路網試算\n\n已計算，但不是完整現況模型，也不是 Space Syntax NAIN/NACH。採同一固定南北起訖點，以 Dijkstra 求最短水平投影路徑。\n\n'+'天橋官方存在依據：https://bridge.nco.taipei/bms2/guest/Footbridge/inventory.aspx?vid=64 。源線形為OSM，落點未全部現勘。本輪地面修復含推定幾何，不能外推全段。\n\n'+json.dumps(summary,ensure_ascii=False,indent=2)+'\n\nCSV空白為來源網絡無路徑，不能解讀為現地不能走。未填補未知高程或直接用示意圖像素量距。A、B圖為同範圍同比例向量圖，橘色是同編號南北樣點路徑，藍色是B新增來源邊。\n'
(OUT/'README.md').write_text(report)
exec(compile((D/'render_accessibility_page.py').read_text(),str(D/'render_accessibility_page.py'),'exec'))
exec(compile((D/'render_route_heatmap.py').read_text(),str(D/'render_route_heatmap.py'),'exec'))
print(json.dumps(summary,ensure_ascii=False,indent=2))
