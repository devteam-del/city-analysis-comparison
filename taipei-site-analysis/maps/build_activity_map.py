from pathlib import Path
import json,math,html,gzip
from PIL import Image,ImageDraw,ImageFont
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
im=Image.new('RGB',(W*S,H*S),'#f7f6f2');d=ImageDraw.Draw(im)
font='/System/Library/Fonts/STHeiti Medium.ttc'
sv=['<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 1680 1188">','<rect width="1680" height="1188" fill="#f7f6f2"/>']
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
# All map drawing is masked again in raster before page labels.
for e in es:
 t=e.get('tags',{});g=e.get('geometry',[])
 if e['type']!='way' or not g:continue
 if 'building' in t and t.get('location')!='underground' and int(t.get('layer','0') if t.get('layer','0').lstrip('-').isdigit() else '0')>=0:
  pts=[xy(p['lon'],p['lat']) for p in g];poly(pts,'#deded8','#c4c7c1',.6)
for e in es:
 t=e.get('tags',{});g=e.get('geometry',[])
 if 'highway' not in t or not g or t.get('tunnel')=='yes' or t.get('indoor')=='yes' or t.get('layer','0').startswith('-'):continue
 pts=[xy(p['lon'],p['lat']) for p in g]
 high=t['highway']
 if high in ['footway','path','steps','pedestrian','cycleway','bridleway'] or t.get('footway')=='sidewalk':continue
 w=3
 col='#bdc6c8' if high in ['footway','path','steps','pedestrian'] else '#ffffff'
 if '市民大道' in t.get('name','') or t.get('name')=='鄭州路':col='#d3a649';w=4
 line(pts,col,w)
# Distinct real geometries; no buffers invented as populations.
for eid,col in [(201280863,'#c4dfd9'),(605982572,'#c4dfd9'),(605982576,'#c4dfd9'),(23641610,'#f0d3ba'),(277518268,'#f0d3ba')]:
 g=by[eid]['geometry'];poly([xy(p['lon'],p['lat']) for p in g],'none' if eid in [201280863,277518268] else col,'#77918a' if col=='#c4dfd9' else '#b38b6b',1)
sv.append('</g>')
# Cover anything outside the neatline in the PNG.
for box in [(0,0,W,ymin),(0,ymax,W,H),(0,ymin,xmin,ymax),(xmax,ymin,W,ymax)]:d.rectangle(tuple(z*S for z in box),fill='#f7f6f2')
line([(xmin,ymin),(xmax,ymin),(xmax,ymax),(xmin,ymax),(xmin,ymin)],'#a8afaa',1)
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
for n in nodes:
 x,y=xy(n['lon'],n['lat']);lx=x+n['offset'][0];ly=y+n['offset'][1];c='#217f76' if n['side']=='north' else '#b66739'
 line([(x,y),(lx+10,ly+12)],c,1.3);circle(x,y,7,c);circle(x,y,2,'#ffffff')
 label=n['id']+' '+n['name'];length=len(label)*16
 poly([(lx-5,ly-4),(lx+length,ly-4),(lx+length,ly+28),(lx-5,ly+28)],'#f7f6f2')
 text(lx,ly,label,21,c)
# Sparse road labels at observed official survey points.
text(70,46,'市民大道｜生活與工作節點',36)
text(72,101,'候選聚集點',19,'#6a7475')
circle(1100,108,6,'#217f76');text(1116,94,'北側',19);circle(1200,108,6,'#b66739');text(1216,94,'南側',19)
text(1370,54,'A3  1:5,000',24);text(1370,96,'2026.09.14',17,'#6a7475')
text(1260,610,'市民大道／鄭州路',18,'#9c741e')
text(1230,820,'忠孝西路',17,'#777f80')
# north arrow and true projected-metre graphic scale
line([(1570,260),(1570,205)],'#25313a',2);poly([(1570,190),(1562,210),(1578,210)],'#25313a');text(1563,164,'N',20)
x,y=80,1010
for i in range(4):poly([(x+i*40,y),(x+(i+1)*40,y),(x+(i+1)*40,y+8),(x+i*40,y+8)],'#26333a' if i%2==0 else '#ffffff','#26333a',.8)
text(x,y-26,'0',16);text(x+72,y-26,'100',16);text(x+145,y-26,'200 m',16)
text(70,1080,'候選位置，非人流量  |  留白未區分人行道、車道與空地',17,'#667271')
text(70,1120,'TWD97 / TM2 121  |  © OpenStreetMap contributors / ODbL  |  100% 原尺寸列印',16,'#667271')
sv.append('</svg>');(B/'activity-map.svg').write_text('\n'.join(sv));im.save(B/'activity-map.png')
(B/'activity-map.html').write_text('<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><title>市民大道｜生活與工作節點</title><style>body{margin:0;background:#e8e8e3}svg{display:block;width:100%;height:auto;max-width:1800px;margin:auto}@media print{@page{size:A3 landscape;margin:0}svg{width:420mm;height:297mm}}</style>'+ '\n'.join(sv))
root=B.parents[1];pdf=root/'output/pdf/taipei-activity-map-a3.pdf';pdf.parent.mkdir(exist_ok=True,parents=True)
c=canvas.Canvas(str(pdf),pagesize=(420/25.4*72,297/25.4*72));c.drawImage(ImageReader(im),0,0,width=420/25.4*72,height=297/25.4*72);c.showPage();c.save()
(B/'activity-nodes.json').write_text(json.dumps({'crs':'EPSG:4326','nodes':nodes,'classification':'candidate sites; not measured flows or exact entrances'},ensure_ascii=False,indent=2))
print('Created',pdf,'nodes',len(nodes),'elements',len(es))
