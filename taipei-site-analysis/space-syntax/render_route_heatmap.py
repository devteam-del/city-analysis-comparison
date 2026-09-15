"""Equal-weight OD route frequency, with geometric subdivision and separated levels."""
from shapely.geometry import LineString,Point
from shapely.ops import unary_union
from shapely.strtree import STRtree

import xml.etree.ElementTree as ET
source={'ground':{},'elevated':{}}
for r in routes:
 seen=set()
 for a,b in zip(r['keys'],r['keys'][1:]):
  if math.dist(positions[a],positions[b])<1e-6:continue
  level='ground' if a in A and b in A[a] else 'elevated'
  geom=LineString([positions[a],positions[b]])
  key=tuple(sorted(tuple(p) for p in geom.coords))
  if (level,key) in seen:continue
  seen.add((level,key));record=source[level].setdefault(key,{'geom':geom,'A':set(),'B':set()});record[r['case']].add(r['origin']+'-'+r['destination'])
# Sweep intervals on numerically collinear supports. This avoids counting tiny
# floating-point parallel slivers created by splitting the same original edge.
heat=[]
for level,records in source.items():
 groups=[]
 for record in sorted(records.values(),key=lambda r:-r['geom'].length):
  a,b=map(tuple,record['geom'].coords);length=math.dist(a,b)
  if length<1e-6:continue
  group=None
  for g in groups:
   ox,oy=g['origin'];ux,uy=g['unit']
   if abs((a[0]-ox)*uy-(a[1]-oy)*ux)<1e-6 and abs((b[0]-ox)*uy-(b[1]-oy)*ux)<1e-6:
    group=g;break
  if group is None:
   group={'origin':a,'unit':((b[0]-a[0])/length,(b[1]-a[1])/length),'events':[]};groups.append(group)
  ox,oy=group['origin'];ux,uy=group['unit']
  lo,hi=sorted(((a[0]-ox)*ux+(a[1]-oy)*uy,(b[0]-ox)*ux+(b[1]-oy)*uy))
  group['events'].append((lo,1,record));group['events'].append((hi,-1,record))
 for group in groups:
  active={'A':collections.Counter(),'B':collections.Counter()};last=None
  ox,oy=group['origin'];ux,uy=group['unit']
  for pos,sign,record in sorted(group['events'],key=lambda v:v[0]):
   if last is not None and pos-last>1e-6 and any(active.values()):
    heat.append({'level':level,'A':len(active['A']),'B':len(active['B']),'length_m':pos-last,'xy':[(ox+last*ux,oy+last*uy),(ox+pos*ux,oy+pos*uy)]})
   for c in ['A','B']:
    for od in record[c]:
     active[c][od]+=sign
     if active[c][od]==0:del active[c][od]
   last=pos
denominator=len(rows)
max_count=max((max(e['A'],e['B']) for e in heat),default=0)
assert max_count<=denominator
for e in heat:
 e['A_rate']=e['A']/denominator;e['B_rate']=e['B']/denominator
stops=[(0,(44,97,180)),(.25,(65,165,214)),(.5,(222,221,154)),(.75,(241,141,65)),(1,(192,31,42))]
def color(n):
 t=n/max_count if max_count else 0
 for (a,c1),(b,c2) in zip(stops,stops[1:]):
  if t<=b:
   f=(t-a)/(b-a);return '#'+''.join(f'{round(u+(v-u)*f):02x}' for u,v in zip(c1,c2))
 return '#c01f2a'
heat_svgs={};ns={'s':'http://www.w3.org/2000/svg'}
for c in ['A','B']:
 root=ET.fromstring((OUT/(c+'.svg')).read_text())
 # Retain envelope surfaces and scale; remove old paired-route drawings and sample labels.
 for child in list(root):
  if child.tag.endswith(('polyline','circle')) or (child.tag.endswith('text') and child.text!='200 m'):root.remove(child)
 for group in root.findall('s:g',ns):
  for p in group.findall('s:path',ns):
   if p.get('fill')!='none':p.set('fill','#e1e5e4');p.set('stroke','#b6c0bd')
 g=ET.SubElement(root,'{http://www.w3.org/2000/svg}g',{'id':'route-frequency'})
 for e in sorted(heat,key=lambda e:(e['level']!='ground',e[c])):
  if not e[c]:continue
  coords=line(e['xy']);path=ET.SubElement(g,'{http://www.w3.org/2000/svg}polyline',{'points':coords,'fill':'none','stroke':color(e[c]),'stroke-width':'5','stroke-linecap':'butt','stroke-linejoin':'round','data-count':str(e[c]),'data-level':e['level']})
  ET.SubElement(path,'{http://www.w3.org/2000/svg}title').text=f'{e[c]} / {denominator} = {e[c]/denominator:.2%}'
 ET.register_namespace('','http://www.w3.org/2000/svg');svg=ET.tostring(root,encoding='unicode');(OUT/(c+'-heatmap.svg')).write_text(svg);heat_svgs[c]=svg
json.dump({'method':'equally weighted selected north-to-south OD paths; common denominator includes unresolved OD; levels separate','normalization':'shared linear scale across A and B','max_count':max_count,'denominator':denominator,'selected_points':len(samples),'zero':'neutral gray, not missing','collinear_tolerance_m':1e-6,'not_measured_pedestrian_flow':True,'A_routes':sum(r['case']=='A' for r in routes),'B_routes':sum(r['case']=='B' for r in routes),'segments':[dict(e,xy=None) for e in heat]},open(OUT/'heatmap-summary.json','w'),ensure_ascii=False,indent=2)
json.dump({'metric':'route_overlap_rate','denominator':denominator,'selected_points':len(samples),'demand_weighting':False,'A_connected':sum(r['case']=='A' for r in routes),'B_connected':sum(r['case']=='B' for r in routes),'segments':[dict(e,xy=None) for e in heat]},open(OUT/'route-overlap-rates.json','w'),ensure_ascii=False,indent=2)
# Length-weighted frequency must equal summed path length to numerical tolerance.
checks={}
for c in ['A','B']:
 expected=sum(sum(math.dist(positions[a],positions[b]) for a,b in zip(r['keys'],r['keys'][1:])) for r in routes if r['case']==c);actual=sum(e['length_m']*e[c] for e in heat);checks[c]={'sum_route_m':expected,'frequency_weighted_segment_m':actual,'difference_m':actual-expected};assert abs(actual-expected)<max(1,expected*1e-4),(c,checks[c])
json.dump(checks,open(OUT/'heatmap-validation.json','w'),indent=2)
legend=f'<div class="heatlegend"><span>低重複率 {1/denominator:.2%}</span><i></i><span>高重複率 {max_count/denominator:.2%}</span></div>'
section=f'<section id="heatmaps"><h1>路徑重複率</h1><p class="notice">{len(samples)}個交通／商業節點，{denominator}組南北OD，已接通路徑疊合；未接通OD保留於分母，不受下方篩選影響。相同色階：低頻藍、高頻紅；未經過的網絡維持灰色。</p>'+legend+'<div class="maps"><section><h2>A｜地面</h2>'+heat_svgs['A']+'</section><section><h2>B｜地面＋天橋</h2>'+heat_svgs['B']+'</section></div><p class="notice">每組起訖點等權重；每段以經過的不同OD路徑數除以共同OD總數計算。這是等權路徑重複率，不是實測人流或完整Space Syntax choice。地下通道尚未納入B。</p><p><a href="A-heatmap.svg">下載 A 熱力向量圖</a> · <a href="B-heatmap.svg">下載 B 熱力向量圖</a> · <a href="heatmap-summary.json">計算依據</a></p></section>'
p=OUT/'index.html';page=p.read_text();page=page.replace('<main>','<main>'+section,1).replace('</style>','.heatlegend{display:flex;align-items:center;gap:12px;margin:18px 0;font-size:14px}.heatlegend i{display:block;width:280px;height:14px;background:linear-gradient(90deg,#2c61b4,#41a5d6,#dedd9a,#f18d41,#c01f2a)}#heatmaps svg{width:100%;height:auto}#heatmaps{border-bottom:1px solid #b6c0bd;padding-bottom:24px;margin-bottom:24px}</style>',1);p.write_text(page)
print('Heatmap shared maximum:',max_count,'validation:',checks)
