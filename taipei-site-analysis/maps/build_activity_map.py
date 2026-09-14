from pathlib import Path
import json,math,html,gzip
from PIL import Image,ImageDraw,ImageFont,ImageFilter
import base64,io
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader
B=Path(__file__).resolve().parent
src=B/'osm-source.json.gz'
if not src.exists():
 data=json.load(open('/tmp/taipei-osm.json'));data['elements']=[e for e in data['elements'] if e['type']!='relation'];src.write_bytes(gzip.compress(json.dumps(data,ensure_ascii=False).encode()))
data=json.loads(gzip.decompress(src.read_bytes()));es=data['elements'];by={e['id']:e for e in es}
# GRS80 transverse Mercator, TWD97 / TM2 zone 121 (EPSG:3826).
def tm(lon,lat):
 a=6378137.; f=1/298.257222101;e=f*(2-f);ep=e/(1-e);p=math.radians(lat); dl=math.radians(lon-121)
 sn=math.sin(p);cs=math.cos(p);t=math.tan(p)**2;c=ep*cs**2;A=cs*dl;N=a/math.sqrt(1-e*sn*sn)
 M=a*((1-e/4-3*e**2/64-5*e**3/256)*p-(3*e/8+3*e**2/32+45*e**3/1024)*math.sin(2*p)+(15*e**2/256+45*e**3/1024)*math.sin(4*p)-35*e**3/3072*math.sin(6*p))
 return (250000+.9999*N*(A+(1-t+c)*A**3/6+(5-18*t+t*t+72*c-58*ep)*A**5/120),.9999*(M+N*math.tan(p)*(A*A/2+(5-t+9*c+4*c*c)*A**4/24+(61-58*t+t*t+600*c-330*ep)*A**6/720)))
W,H=1680,1188;S=2
im=Image.new('RGB',(W*S,H*S),'#e3e5e1');d=ImageDraw.Draw(im)
font='/System/Library/Fonts/STHeiti Medium.ttc'
sv=['<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 1680 1188">','<rect width="1680" height="1188" fill="#e3e5e1"/>']
def line(pts,col,w=1):
 if len(pts)<2:return
 d.line([(x*S,y*S) for x,y in pts],fill=col,width=max(1,round(w*S)),joint='curve');sv.append('<polyline points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)+f'" fill="none" stroke="{col}" stroke-width="{w}"/>')
def poly(pts,fill,stroke=None,w=1):
 
 if fill!='none':d.polygon([(x*S,y*S) for x,y in pts],fill=fill)
 if stroke:d.line([(x*S,y*S) for x,y in pts+[pts[0]]],fill=stroke,width=max(1,round(w*S)))
 sv.append('<polygon points="'+' '.join(f'{x:.1f},{y:.1f}' for x,y in pts)+f'" fill="{fill}" stroke="{stroke or "none"}" stroke-width="{w}"/>')
def text(x,y,s,size=18,col='#25313a'):
 d.text((x*S,y*S),s,font=ImageFont.truetype(font,size*S),fill=col)
 sv.append(f'<text x="{x}" y="{y+size*.88}" font-family="PingFang TC,Heiti TC,sans-serif" font-size="{size}" fill="{col}">{html.escape(s)}</text>')
def circle(x,y,r,c):
 d.ellipse(((x-r)*S,(y-r)*S,(x+r)*S,(y+r)*S),fill=c);sv.append(f'<circle cx="{x:.2f}" cy="{y:.2f}" r="{r}" fill="{c}"/>')
cx,cy=tm(121.51355,25.0489);scale=.8
# 1980 x 1130 metres, equal x/y scale; A3 100% = 1:5000.
def xy(lon,lat):
 x,y=tm(lon,lat);return 840+(x-cx)*scale,604-(y-cy)*scale
xmin,ymin,xmax,ymax=48,152,1632,1056
sv.append(f'<defs><clipPath id="map"><rect x="{xmin}" y="{ymin}" width="1584" height="904"/></clipPath></defs><g clip-path="url(#map)">')
coords={}
for e in es:
 if e['type']=='way':
  for nid,p in zip(e.get('nodes',[]),e.get('geometry',[])):coords[nid]=(p['lon'],p['lat'])
def intersect(a,b):
 sets=[]
 for n in [a,b]:sets.append(set(nid for e in es if e.get('tags',{}).get('name')==n for nid in e.get('nodes',[])))
 common=sorted(sets[0]&sets[1]);assert common,(a,b)
 return coords[common[0]],common[0]
def center(eid):
 e=by[eid]
 if e['type']=='node':return(e['lon'],e['lat'])
 q=e['bounds'];return((q['minlon']+q['maxlon'])/2,(q['minlat']+q['maxlat'])/2)
nodes=[]
def add(id,name,pos,off,ref,side):nodes.append(dict(id=id,name=name,lon=pos[0],lat=pos[1],offset=off,source=ref,side=side))
add('N1','中興院區',center(201280863),(-175,-60),'way/201280863','north')
p,i=intersect('延平北路一段','鄭州路');add('N2','後站批發',p,(-170,-66),f'node/{i}','north')
p,i=intersect('華陰街','太原路');add('N3','華陰／太原',p,(-140,-54),f'node/{i}','north')
add('N4','京站／轉運站',center(605982572),(50,-80),'way/605982572','north')
p,i=intersect('長安西路','太原路');add('N5','長安街口',p,(20,-75),f'node/{i}','north')
add('S1a','北門站',center(3263840809),(-205,25),'node/3263840809','south')
add('S1b','鐵道部',center(277518268),(-130,75),'way/277518268','south')
add('S2','機捷 A1',center(4653351592),(-20,95),'node/4653351592','south')
# Use north-side station building boundary midpoint, not an invented M1/M2 exit coordinate.
e=by[23641610]['bounds'];add('S3','北車北側',((e['minlon']+e['maxlon'])/2,e['maxlat']),(110,45),'way/23641610 north envelope midpoint','south')
add('S4','北門郵局',center(2619922124),(-210,45),'node/2619922124','south')
p,i=intersect('南陽街','許昌街');add('S5','南陽／許昌',p,(40,35),f'node/{i}','south')
# Layers: underground facility envelopes, buildings/activity blocks, road side lines, elevated road.
cols={'north':'#8d9e82','south':'#b5836c'}
def pts_of(e):return [xy(q['lon'],q['lat']) for q in e.get('geometry',[])]
def building(e):
 t=e.get('tags',{});return e['type']=='way' and 'building' in t and t.get('location')!='underground' and not t.get('layer','0').startswith('-') and len(e.get('geometry',[]))>3
buildings=[e for e in es if building(e)]
# Explicit source polygons for facilities. Station shells are underground projections.
areas=[('N1',201280863),('N4',605982572),('N4',605982576),('S1a',1226069618),('S1b',277518268),('S2',646262272),('S3',23641610)]
chosen={}
for key,eid in areas:
 side=next(n['side'] for n in nodes if n['id']==key);poly(pts_of(by[eid]),'#cbd5c3' if side=='north' else '#decbbd',cols[side],1)
# Street-node colours select nearby existing footprints, never invent circles or block boundaries.
selection=[]
for key,count in [('N2',5),('N3',6),('N5',4),('S4',1),('S5',5)]:
 n=next(n for n in nodes if n['id']==key);x,y=xy(n['lon'],n['lat']);candidates=[]
 for e in buildings:
  a,b=xy(*center(e['id']));dist=math.hypot(a-x,b-y)
  if key=='N2' and b>y-4:continue
  shape=pts_of(e);area=abs(sum(shape[i][0]*shape[(i+1)%len(shape)][1]-shape[(i+1)%len(shape)][0]*shape[i][1] for i in range(len(shape))))/2/(scale*scale)
  if dist<85 and area>=80:candidates.append((dist,e))
 for dist,e in sorted(candidates,key=lambda v:v[0])[:count]:chosen[e['id']]=n['side'];selection.append({'candidate':key,'osm_way':e['id'],'selection':'nearby footprint for survey focus, not verified use or activity extent'})
for e in buildings:
 col=cols.get(chosen.get(e['id']),'#cdd2cb');poly(pts_of(e),col,'#c1c8c0',.35)
# Reapply real aboveground facility footprints in colour.
for eid,side in [(605982572,'north'),(605982576,'north'),(23641610,'south')]:poly(pts_of(by[eid]),cols[side],cols[side],.8)
# Road sides: current OSM alignment with nearest same-name historical official WIDTH.
# WIDTH is used as a recorded width input only; output is explicitly an offset reconstruction.
road_data=json.loads((B/'official-road-widths.json').read_text())['features']
def normalize(n):
 for q in ['一段','二段','三段','四段','五段','六段']:n=n.replace(q,'')
 return n
roadmask=Image.new('L',im.size);rd=ImageDraw.Draw(roadmask);width_log=[];elev=[]
for e in es:
 t=e.get('tags',{});g=e.get('geometry',[]);h=t.get('highway')
 if not h or not g or t.get('tunnel')=='yes' or t.get('indoor')=='yes' or t.get('layer','0').startswith('-'):continue
 if h in ['footway','path','steps','pedestrian','cycleway','bridleway']:continue
 if t.get('bridge')=='yes' or int(t.get('layer','0') if t.get('layer','0').isdigit() else 0)>0:
  
  if h in ['motorway','motorway_link','trunk','trunk_link']:elev.append(e)
  continue
 name=normalize(t.get('name',''));mid=g[len(g)//2];mx,my=tm(mid['lon'],mid['lat']);matches=[]
 for f in road_data:
  a=f['attributes'];w=a.get('WIDTH')
  if not name or normalize(a.get('ROADNAME') or '')!=name or not w or not 2<=w<=50 or a.get('ROADSTRUCT')!=0:continue
  distance=min((math.hypot(q[0]-mx,q[1]-my) for path in f['geometry']['paths'] for q in path),default=1e9)
  if distance<100:matches.append((distance,f))
 if not matches:continue
 f=min(matches,key=lambda v:v[0])[1];w=f['attributes']['WIDTH'];points=pts_of(e)
 rd.line([(x*S,y*S) for x,y in points],fill=255,width=max(2,round(w*scale*S)),joint='curve')
 width_log.append({'osm_way':e['id'],'official_id':f['attributes']['ID'],'width_input':w,'MDATE':f['attributes'].get('MDATE'),'method':'symmetric offset; not verified curb'})
# Only the boundary survives; no centreline strokes. Union clears internal junction seams.
outer=roadmask.filter(ImageFilter.MaxFilter(3));inner=roadmask.filter(ImageFilter.MinFilter(3))
import numpy as np
edge=Image.fromarray((np.asarray(outer)-np.asarray(inner)).astype('uint8'))
edgeim=Image.new('RGBA',im.size,(255,255,255,0));edgeim.putalpha(edge);im.paste(edgeim,(0,0),edgeim)
buf=io.BytesIO();edgeim.save(buf,format='PNG');encoded=base64.b64encode(buf.getvalue()).decode()
sv.append(f'<g id="surface-road-sides" data-status="historical-width-offset-not-survey"><image x="0" y="0" width="1680" height="1188" href="data:image/png;base64,{encoded}"/></g>')
# Elevated infrastructure is the last geographic layer, explicitly above all coloured blocks and roads.
sv.append('<g id="elevated-road-top">')
for e in elev:
 points=pts_of(e);line(points,'#586e78',6);line(points,'#91a4ab',4)
sv.append('</g></g>')
# Mask beyond map boundary and draw frame.
for box in [(0,0,W,ymin),(0,ymax,W,H),(0,ymin,xmin,ymax),(xmax,ymin,W,ymax)]:d.rectangle(tuple(z*S for z in box),fill='#e3e5e1')
line([(xmin,ymin),(xmax,ymin),(xmax,ymax),(xmin,ymax),(xmin,ymin)],'#c0c7c0',1)
# Labels only, without points, leader lines or numbered symbols.
for n in nodes:
 x,y=xy(n['lon'],n['lat']);lx=x+n['offset'][0];ly=y+n['offset'][1];c='#52654c' if n['side']=='north' else '#825947'
 offsets={'N1':(-60,-25),'N2':(-80,-55),'N3':(-50,-55),'N5':(20,-65),'N4':(25,-70),'S1a':(-50,15),'S1b':(-25,48),'S2':(-40,42),'S3':(-20,70),'S4':(-30,35),'S5':(35,40)}
 dx,dy=offsets[n['id']];lx=x+dx;ly=y+dy
 label='台北車站' if n['id']=='S3' else n['name'];length=len(label)*21
 poly([(lx-4,ly-3),(lx+length,ly-3),(lx+length,ly+25),(lx-4,ly+25)],'#e3e5e1')
 text(lx,ly,label,21,c)
(B/'block-selection.json').write_text(json.dumps(selection,ensure_ascii=False,indent=2))
(B/'road-width-matches.json').write_text(json.dumps(width_log,ensure_ascii=False,indent=2))
# Sparse road labels at observed official survey points.
text(70,46,'市民大道｜生活與工作圖塊',32)
text(72,101,'候選活動圖塊',19,'#6a7475')
poly([(1100,97),(1116,97),(1116,113),(1100,113)],cols['north']);text(1126,94,'北側',19);poly([(1200,97),(1216,97),(1216,113),(1200,113)],cols['south']);text(1226,94,'南側',19)
text(1370,54,'A3  1:5,000',24);text(1370,96,'2026.09.14',17,'#6a7475')
text(1260,610,'市民高架',18,'#4f6670')
text(1230,820,'忠孝西路',17,'#777f80')
# north arrow and true projected-metre graphic scale
line([(1570,260),(1570,205)],'#25313a',2);poly([(1570,190),(1562,210),(1578,210)],'#25313a');text(1563,164,'N',20)
x,y=80,1010
for i in range(4):poly([(x+i*40,y),(x+(i+1)*40,y),(x+(i+1)*40,y+8),(x+i*40,y+8)],'#26333a' if i%2==0 else '#ffffff','#26333a',.8)
text(x,y-26,'0',16);text(x+72,y-26,'100',16);text(x+145,y-26,'200 m',16)
text(70,1080,'圖塊＝調查候選範圍  |  道路雙側線依舊路寬推算，非實測路緣',17,'#667271')
text(70,1120,'TWD97 / TM2 121  |  © OpenStreetMap contributors / ODbL；臺北市道路資料  |  高架線寬示意',16,'#667271')
sv.append('</svg>');(B/'activity-map.svg').write_text('\n'.join(sv));im.save(B/'activity-map.png')
(B/'activity-map.html').write_text('<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>市民大道｜生活與工作圖塊</title><style>body{margin:0;background:#e8e8e3}svg{display:block;width:100%;height:auto;max-width:1800px;margin:auto}@media print{@page{size:A3 landscape;margin:0}svg{width:420mm;height:297mm}}</style>'+ '\n'.join(sv))
root=B.parents[1];pdf=root/'output/pdf/taipei-activity-map-a3.pdf';pdf.parent.mkdir(exist_ok=True,parents=True)
c=canvas.Canvas(str(pdf),pagesize=(420/25.4*72,297/25.4*72));c.drawImage(ImageReader(im),0,0,width=420/25.4*72,height=297/25.4*72);c.showPage();c.save()
(B/'activity-nodes.json').write_text(json.dumps({'crs':'EPSG:4326','nodes':nodes,'classification':'candidate sites; not measured flows or exact entrances'},ensure_ascii=False,indent=2))
print('Created',pdf,'nodes',len(nodes),'elements',len(es))
