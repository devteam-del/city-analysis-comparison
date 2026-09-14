from pathlib import Path
import json,math,html,gzip,base64,io,xml.etree.ElementTree as ET
from PIL import Image,ImageDraw,ImageFont
B=Path(__file__).resolve().parent
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
NS='{http://www.w3.org/2000/svg}'
ET.register_namespace('','http://www.w3.org/2000/svg')
old=json.loads(gzip.decompress((B.parent/'osm-source.json.gz').read_bytes()))['elements']
new=json.loads(gzip.decompress((B/'source-geometry.json.gz').read_bytes()))['elements']
by={e['id']:e for e in old};by.update({e['id']:e for e in new});es=list(by.values())
base=ET.parse(B.parent/'activity-map-vector.svg').getroot()
roadvector=ET.tostring(base.find(f'.//{NS}g[@id="surface-road-sides"]'),encoding='unicode')
raster=ET.parse(B.parent/'activity-map.svg').getroot().find(f'.//{NS}g[@id="surface-road-sides"]/{NS}image').get('href')
roadimage=Image.open(io.BytesIO(base64.b64decode(raster.split(',')[1]))).convert('RGBA')
def pts(e):return [xy(q['lon'],q['lat']) for q in e.get('geometry',[])]
def mid(e):
 g=e['geometry'];return (sum(q['lon'] for q in g)/len(g),sum(q['lat'] for q in g)/len(g))
def isbuilding(e):
 t=e.get('tags',{});return 'building' in t and t.get('location')!='underground' and not t.get('layer','0').startswith('-') and len(e.get('geometry',[]))>3
buildings=[e for e in es if isbuilding(e)]
def namedlabel(name,lon,lat,dx=0,dy=0,col='#35453a'):
 x,y=xy(lon,lat);text(max(58,min(xmax-len(name)*20-8,x+dx)),max(162,min(1028,y+dy)),name,20,col)
def labelid(i,name,dx=0,dy=0,col='#35453a'):namedlabel(name,*mid(by[i]),dx,dy,col)
def area(e):
 p=[tm(q['lon'],q['lat']) for q in e['geometry']];return abs(sum(p[i][0]*p[(i+1)%len(p)][1]-p[(i+1)%len(p)][0]*p[i][1] for i in range(len(p))))/2
parks=[e for e in es if '廣場' not in e.get('tags',{}).get('name','') and e.get('tags',{}).get('leisure')=='park' and len(e.get('geometry',[]))>3 and e.get('nodes',[0])[0]==e.get('nodes',[1])[-1]]
greens=[e for e in es if e.get('tags',{}).get('landuse')=='grass' or e.get('tags',{}).get('leisure')=='garden']
plazas=[e for e in es if '廣場' in e.get('tags',{}).get('name','') and (e.get('tags',{}).get('area')=='yes' or e.get('tags',{}).get('leisure')=='park') and not isbuilding(e)]
def inside(e):
 x,y=xy(*mid(e));return xmin<x<xmax and ymin<y<ymax
print('Parks:',[(e['id'],e.get('tags',{}).get('name'),round(area(e))) for e in parks if inside(e)])
print('Plazas:',[(e['id'],e.get('tags',{}).get('name')) for e in plazas if inside(e)])
# Along-street study footprints: distance threshold is selection, not measured retail use.
streets=[]
for e in es:
 t=e.get('tags',{});n=t.get('name','');g=e.get('geometry',[])
 if n in ['華陰街','太原路','鄭州路','重慶北路一段','南陽街','許昌街','館前路','信陽街'] and g:
  a,b=mid(e)
  if (121.512<a<121.5168 and 25.0488<b<25.0528) or (121.514<a<121.519 and 25.0438<b<25.0468):streets.append(e)
def distseg(p,a,b):
 vx,vy=b[0]-a[0],b[1]-a[1];q=((p[0]-a[0])*vx+(p[1]-a[1])*vy)/(vx*vx+vy*vy) if vx*vx+vy*vy else 0;q=max(0,min(1,q));return math.hypot(p[0]-a[0]-q*vx,p[1]-a[1]-q*vy)
segs=[(a,b) for e in streets for a,b in zip(pts(e),pts(e)[1:])]
commercial=[e for e in buildings if inside(e) and ((121.512<mid(e)[0]<121.5168 and 25.0488<mid(e)[1]<25.0528) or (121.514<mid(e)[0]<121.519 and 25.0438<mid(e)[1]<25.0468)) and min((distseg(p,a,b) for p in pts(e) for a,b in segs),default=999)<12]
(B/'mapped-features.json').write_text(json.dumps({'parks':[{'id':e['id'],'name':e.get('tags',{}).get('name'),'polygon_area_m2':round(area(e))} for e in parks if inside(e)],'plazas':[e['id'] for e in plazas if inside(e)],'commerce_study_buildings':[e['id'] for e in commercial],'commerce_rule':'footprint within 15 m of selected documented shopping streets, clipped study window; NOT confirmed per-building commercial use'},ensure_ascii=False,indent=2))
styles=[('01-green','01  公園綠地','#879b73','公園範圍','#bdcba8','草地／花園','#c1b69f','廣場／文化園區'),('02-transport','02  交通設施','#688a98','地面站體','#bed0d4','地下站體投影','#91a4ab','高架'),('03-commerce','03  商業帶','#ac7860','商業所在建築','#d4b9a7','商圈沿街調查圖塊','#bed0d4','地下站體參照')]
for slug,title,c1,l1,c2,l2,c3,l3 in styles:
 im=Image.new('RGB',(W*S,H*S),'#e3e5e1');d=ImageDraw.Draw(im)
 sv=['<svg xmlns="http://www.w3.org/2000/svg" width="420mm" height="297mm" viewBox="0 0 1680 1188">','<desc>Same extent 1980 by 1130 metres. EPSG:3826. A3 1:5000. Road sides reconstructed from historical widths, not surveyed curbs. See ANALYSIS.md for provenance.</desc>','<rect width="1680" height="1188" fill="#e3e5e1"/>',f'<defs><clipPath id="map"><rect x="48" y="152" width="1584" height="904"/></clipPath></defs><g id="geography" clip-path="url(#map)">']
 if slug=='01-green':
  for e in parks:poly(pts(e),c1,None)
  for e in greens:
   if len(pts(e))>3:poly(pts(e),c2,None)
  for e in plazas:poly(pts(e),c3,None)
  poly(pts(by[277518268]),c3,None)
 for e in buildings:poly(pts(e),'#cdd2cb','#c1c8c0',.35)
 if slug=='02-transport':
  for i in [1226069618,646262272]:poly(pts(by[i]),c2,'#688a98',1)
  for i in [23641610,605982576]:poly(pts(by[i]),c1,'#506c78',1)
 if slug=='03-commerce':
  for e in commercial:poly(pts(e),c2,'#b99a83',.7)
  for i in [1226069618,646262272]:poly(pts(by[i]),c3,None)
  poly(pts(by[605982572]),c1,'#93614f',1);poly(pts(by[204711206]),c1,'#93614f',1)
 # Existing reconstructed road-side vectors, same on all maps.
 sv.append(roadvector);im.paste(roadimage,(0,0),roadimage)
 sv.append('<g id="elevated-road-top">')
 for e in es:
  t=e.get('tags',{});g=pts(e)
  if t.get('highway') in ['motorway','motorway_link','trunk','trunk_link'] and (t.get('bridge')=='yes' or t.get('layer','0') in ['1','2','3']) and len(g)>1:line(g,'#586e78',6);line(g,'#91a4ab',4)
 sv.append('</g></g>')
 for box in [(0,0,W,ymin),(0,ymax,W,H),(0,ymin,xmin,ymax),(xmax,ymin,W,ymax)]:d.rectangle(tuple(z*S for z in box),fill='#e3e5e1')
 line([(xmin,ymin),(xmax,ymin),(xmax,ymax),(xmin,ymax),(xmin,ymin)],'#c0c7c0',1)
 if slug=='01-green':
  for e in parks:
   if inside(e) and e.get('tags',{}).get('name'):labelid(e['id'],e['tags']['name'],-45,0)
  for e in plazas:
   if inside(e):labelid(e['id'],e['tags']['name'],-40,10)
  labelid(277518268,'鐵道部園區',-55,40)
  labelid(201280863,'中興院區',-50,0,col='#78817b')
  namedlabel('延平河濱公園',121.5056,25.0522,-30,0)
  namedlabel('建成公園（局部）',121.5178,25.0539,-60,0)
  subtitle='綠地與開放空間分開讀'
  note='公園面積 ≠ 植被覆蓋；文化園區不計作公園。小型綠地及多重面仍待補查。'
 elif slug=='02-transport':
  labelid(23641610,'台北車站',-45,0);labelid(605982576,'轉運站',-25,-35)
  labelid(1226069618,'北門站／地下',-110,15);labelid(646262272,'A1／地下',-35,38)
  namedlabel('承德路口 P017',121.51635,25.04875,40,10)
  
  for name,lon,lat in [('環河北路',121.507,25.0528),('西寧北路',121.5088,25.0501),('塔城街',121.5108,25.0523),('重慶北路',121.5136,25.0525),('承德路',121.5164,25.0516),('中山北路',121.5214,25.0504)]:namedlabel(name,lon,lat,0,0,col='#78817b')
  subtitle='道路層級 × 轉乘站體'
  note='站體不是出入口；地下通道、公車站、無障礙動線尚未完整建模。'
 else:
  namedlabel('後站批發',121.5135,25.0515,-90,-30,col='#805e4c');namedlabel('華陰／太原',121.5151,25.0507,-20,-15,col='#805e4c')
  labelid(605982572,'京站',-10,0,col='#704936');labelid(204711206,'站前店／混合大樓',-90,-10,col='#704936');labelid(23641610,'台北車站',-45,30,col='#758186')
  namedlabel('南陽／許昌：補習商圈調查',121.516,25.0447,-70,20,col='#805e4c')
  subtitle='街道型商圈 × 建築型商業'
  note='淡褐建物為商圈沿街調查範圍，非逐戶用途；地下商業及逐戶用途尚待核對。'
 text(70,42,title,34);text(72,101,subtitle,19,'#6a7475')
 for x,c,l in [(660,c1,l1),(925,c2,l2),(1260,c3,l3)]:poly([(x,100),(x+16,100),(x+16,116),(x,116)],c);text(x+25,96,l,17)
 text(1330,48,'A3  1:5,000',24)
 namedlabel('市民高架',121.5192,25.04835,0,22,col='#4f6670')
 namedlabel('忠孝西路',121.519,25.0469,0,22,col='#777f80')
 line([(1570,260),(1570,205)],'#25313a',2);poly([(1570,190),(1562,210),(1578,210)],'#25313a');text(1563,164,'N',20)
 for i in range(4):poly([(80+i*40,1010),(120+i*40,1010),(120+i*40,1018),(80+i*40,1018)],'#26333a' if i%2==0 else '#fff','#26333a',.8)
 text(80,984,'0',16);text(152,984,'100',16);text(225,984,'200 m',16)
 text(70,1078,note,17,'#667271')
 text(70,1111,'道路雙側線依舊路寬推算，非實測路緣；高架線寬示意。留白不等於已確認人行道。',16,'#667271')
 text(70,1142,'2026.09.14  |  TWD97 / TM2 121  |  © OpenStreetMap contributors / ODbL；臺北市資料',15,'#667271')
 sv.append('</svg>');(B/f'{slug}.svg').write_text('\n'.join(sv));im.save(B/f'{slug}.png')
 print(slug,'complete')
