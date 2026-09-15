from pathlib import Path
import json,math,gzip,html
from PIL import Image,ImageDraw
B=Path(__file__).resolve().parent
def tm(lon,lat):
 a=6378137.; f=1/298.257222101;e=f*(2-f);ep=e/(1-e);p=math.radians(lat); dl=math.radians(lon-121)
 sn=math.sin(p);cs=math.cos(p);t=math.tan(p)**2;c=ep*cs**2;A=cs*dl;N=a/math.sqrt(1-e*sn*sn)
 M=a*((1-e/4-3*e**2/64-5*e**3/256)*p-(3*e/8+3*e**2/32+45*e**3/1024)*math.sin(2*p)+(15*e**2/256+45*e**3/1024)*math.sin(4*p)-35*e**3/3072*math.sin(6*p))
 return (250000+.9999*N*(A+(1-t+c)*A**3/6+(5-18*t+t*t+72*c-58*ep)*A**5/120),.9999*(M+N*math.tan(p)*(A*A/2+(5-t+9*c+4*c*c)*A**4/24+(61-58*t+t*t+600*c-330*ep)*A**6/720)))
# 12,000 x 2,400 m; 1:10,000 at 1,200 x 240 mm. No visible text or point symbols.
W,H=6000,1200;scale=.5;cx,cy=tm(121.56,25.049)
def xy(p):
 x,y=tm(p['lon'],p['lat']);return (W/2+(x-cx)*scale,H/2-(y-cy)*scale)
data=json.loads(gzip.decompress((B/'geometry.json.gz').read_bytes()));es=data['elements'];by={e['id']:e for e in es if e['type']=='way'}
def pts(e):return [xy(p) for p in e.get('geometry',[]) if p]
def drawpoly(p,col,stroke=None):
 if len(p)<3:return
 d.polygon(p,fill=col)
 if stroke:d.line(p+[p[0]],fill=stroke,width=1)
 sv.append('<polygon points="'+' '.join(f'{x:.2f},{y:.2f}' for x,y in p)+f'" fill="{col}"'+(f' stroke="{stroke}" stroke-width="0.3"' if stroke else '')+'/>')
def band(p,width,col):
 # Filled offset polygon with bounded miter joins; no centreline is drawn.
 p=[q for i,q in enumerate(p) if not i or q!=p[i-1]]
 if len(p)<2:return
 r=width*scale/2;norm=[]
 for (ax,ay),(bx,by) in zip(p,p[1:]):
  length=math.hypot(bx-ax,by-ay);norm.append((-(by-ay)/length,(bx-ax)/length))
 left=[];right=[]
 for i,(x,y) in enumerate(p):
  a=norm[max(0,i-1)];b=norm[min(i,len(norm)-1)];nx,ny=a[0]+b[0],a[1]+b[1];length=math.hypot(nx,ny)
  if length<1e-8:nx,ny=b;factor=r
  else:
   nx/=length;ny/=length;factor=min(2*r,r/max(.01,nx*b[0]+ny*b[1]))
  left.append((x+nx*factor,y+ny*factor));right.append((x-nx*factor,y-ny*factor))
 drawpoly(left+right[::-1],col)
def closed(e):
 g=e.get('geometry',[]);return len(g)>3 and g[0]==g[-1]
def visible(e):
 p=pts(e);return p and max(x for x,y in p)>0 and min(x for x,y in p)<W and max(y for x,y in p)>0 and min(y for x,y in p)<H
ways=[e for e in es if e['type']=='way' and visible(e)]
def building(e):
 t=e.get('tags',{});return 'building'in t and t.get('building')!='no' and t.get('location')!='underground' and not t.get('layer','0').startswith('-') and closed(e)
buildings=[e for e in ways if building(e)]
def high(e):
 t=e.get('tags',{});return t.get('highway') in ['motorway','motorway_link','trunk','trunk_link'] and (t.get('bridge')=='yes' or t.get('layer') in ['1','2','3'])
# Widths are cartographic where OSM does not explicitly record a width; no curb accuracy claim.
widths={'motorway':15,'motorway_link':7,'trunk':15,'trunk_link':7,'primary':20,'primary_link':8,'secondary':16,'secondary_link':7,'tertiary':12,'tertiary_link':6,'residential':7,'unclassified':7,'service':4,'living_street':5,'road':7}
width_log=[]
def norm(n):
 for v in ['一段','二段','三段','四段','五段','六段','七段','八段']:n=n.replace(v,'')
 return n
oldwidth={}
for f in json.loads((B.parents[1]/'official-road-widths.json').read_text())['features']:
 a=f['attributes'];name=norm(a.get('RDNAMESECT') or a.get('ROADNAME') or '')
 if a.get('ROADSTRUCT')==0 and isinstance(a.get('WIDTH'),(int,float)) and 2<=a['WIDTH']<=50:
  oldwidth.setdefault(name,[]).append(f)
def width(e):
 t=e.get('tags',{});v=t.get('width','')
 try:w=float(v.replace('m','').strip());assert 1<=w<=80;origin='osm_width'
 except:
  w=widths.get(t.get('highway'),6);origin='cartographic_class_width'
  g=e.get('geometry',[])
  if g:
   p=g[len(g)//2];x,y=tm(p['lon'],p['lat']);matches=[]
   for f in oldwidth.get(norm(t.get('name','')),[]):
    dd=min((math.hypot(x-q[0],y-q[1]) for a in f['geometry']['paths'] for q in a),default=99999)
    if dd<100:matches.append((dd,f['attributes']['WIDTH']))
   if matches:w=min(matches)[1];origin='historical_official_WIDTH'
 width_log.append({'id':e['id'],'width_m':w,'basis':origin});return w
roads=[e for e in ways if e.get('tags',{}).get('highway') in widths and not high(e) and e.get('tags',{}).get('tunnel')!='yes' and not e.get('tags',{}).get('layer','0').startswith('-')]
roadwidth={e['id']:width(e) for e in roads}
# Commercial use is taken from OSM building/landuse/shop tags, never inferred merely from proximity.
def commercial(e):
 t=e.get('tags',{});return t.get('building') in ['commercial','retail','office','supermarket'] or t.get('shop') not in [None,'no','vacant'] or t.get('landuse') in ['commercial','retail']
def transit(e):
 t=e.get('tags',{});return t.get('building') in ['train_station','transportation'] or t.get('amenity') in ['bus_station','ferry_terminal'] or t.get('railway')=='station'
def number(value):
 try:return float(value)
 except (TypeError,ValueError):return None
def transport_position(e):
 t=e.get('tags',{})
 if not transit(e) and t.get('railway')!='subway_entrance':return None
 layer=number(t.get('layer'));level=number(t.get('level'))
 if t.get('location')=='underground' or (layer is not None and layer<0) or (level is not None and level<0):return 'underground'
 if not closed(e) or t.get('building') in [None,'no']:return 'unknown'
 if (t.get('location') in ['surface','overground','aboveground','elevated'] or
     (layer is not None and layer>=0) or (level is not None and level>=0) or
     (number(t.get('building:levels')) or 0)>0 or (number(t.get('height')) or 0)>0 or
     t.get('railway')=='subway_entrance' or e['id']==605982576):return 'aboveground'
 return 'unknown'
# Basement storey counts alone do not make an aboveground building underground.
classification=[{'id':e['id'],'name':e.get('tags',{}).get('name'),'position':transport_position(e),'tags':e.get('tags',{})} for e in ways if transit(e) or e.get('tags',{}).get('railway')=='subway_entrance']
(B/'transport-classification.json').write_text(json.dumps(classification,ensure_ascii=False,indent=2))
# Reconstruct closed relation rings; open chains are omitted and logged, not closed across missing geometry.
def rings(members,role):
 chains=[[xy(q) for q in m.get('geometry',[]) if q] for m in members if m.get('role','outer')==role and m.get('geometry')]
 out=[]
 while chains:
  chain=chains.pop()
  while chain[0]!=chain[-1]:
   match=None
   for i,c in enumerate(chains):
    if chain[-1]==c[0]:match=(i,c);break
    if chain[-1]==c[-1]:match=(i,c[::-1]);break
   if match is None:break
   i,c=match;chain+=c[1:];chains.pop(i)
  if len(chain)>3 and chain[0]==chain[-1]:out.append(chain)
 return out
parkrels=[e for e in es if e['type']=='relation' and e.get('tags',{}).get('leisure')=='park']
parkmembers={m['ref'] for e in parkrels for m in e.get('members',[]) if m.get('type')=='way'}
for theme in ['01-green','02-transport','03-commerce']:
 im=Image.new('RGB',(W,H),'#e3e5e1');d=ImageDraw.Draw(im)
 sv=[f'<svg xmlns="http://www.w3.org/2000/svg" width="1200mm" height="240mm" viewBox="0 0 {W} {H}"><metadata>EPSG:3826; 12000 x 2400 m; 1:10000 at native size. See SOURCE_NOTES.md. © OpenStreetMap contributors, ODbL.</metadata><defs><clipPath id="frame"><rect width="{W}" height="{H}"/></clipPath></defs><rect width="{W}" height="{H}" fill="#e3e5e1"/><g clip-path="url(#frame)">']
 if theme=='01-green':
  sv.append('<g id="green-areas">')
  for e in ways:
   t=e.get('tags',{})
   if closed(e) and e['id'] not in parkmembers and '廣場' not in t.get('name','') and (t.get('leisure') in ['park','garden'] or t.get('landuse') in ['grass','forest']):drawpoly(pts(e),'#b7c69e' if t.get('landuse')=='grass' or t.get('leisure')=='garden' else '#889d73')
  for e in parkrels:
   outer=rings(e.get('members',[]),'outer');inner=rings(e.get('members',[]),'inner')
   for p in outer:drawpoly(p,'#889d73')
   for p in inner:drawpoly(p,'#e3e5e1')
  sv.append('</g>')
 if theme=='03-commerce':
  for e in ways:
   if closed(e) and e.get('tags',{}).get('landuse') in ['commercial','retail']:drawpoly(pts(e),'#d6bda8')
 sv.append('<g id="building-blocks">')
 for e in buildings:
  col='#c8cec6'
  if theme=='03-commerce' and commercial(e):col='#b68167'
  if theme=='02-transport' and transport_position(e)=='aboveground':col='#6e909c'
  drawpoly(pts(e),col)
 sv.append('</g>')
 if theme=='02-transport':
  sv.append('<g id="underground-transport">')
  for e in ways:
   if closed(e) and transport_position(e)=='underground':drawpoly(pts(e),'#bdcfd2')
  sv.append('</g>')
 if theme=='02-transport':
  sv.append('<g id="aboveground-transport">')
  for e in buildings:
   if transport_position(e)=='aboveground':drawpoly(pts(e),'#6e909c')
  sv.append('</g>')
 # Fill between former side edges. No empty road interiors or centreline symbols.
 sv.append('<g id="filled-surface-roads">')
 for e in roads:band(pts(e),roadwidth[e['id']],'#ffffff')
 sv.append('</g><g id="elevated-road-top">')
 for e in ways:
  if high(e):band(pts(e),11 if 'link' not in e['tags']['highway'] else 7,'#91a4ab')
 sv.append('</g></g></svg>');(B/f'{theme}.svg').write_text(''.join(sv));im.save(B/f'{theme}.png')
 print(theme,len(buildings),len(roads),len(sv))
(B/'road-width-basis.json.gz').write_bytes(gzip.compress(json.dumps(width_log).encode()))
# Visual-only page; controls are placed outside the artwork.
page='<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>市民大道全段</title><style>body{margin:0;background:#e3e5e1}section{overflow:auto;margin:0 0 24px}img{display:block;width:100%;height:auto;min-width:1800px}@media print{section{margin:0;break-after:page;overflow:visible}img{width:1200mm;height:240mm;min-width:0}@page{size:1200mm 240mm;margin:0}}</style>'
for n in ['01-green','02-transport','03-commerce']:page+='<section><img src="'+n+'.svg" alt=""></section>'
page+='</html>';(B/'index.html').write_text(page);B.parent.joinpath('index.html').write_text(page.replace('src="','src="full-corridor/'))
thumb=Image.new('RGB',(3000,1800),'#e3e5e1')
for i,n in enumerate(['01-green','02-transport','03-commerce']):thumb.paste(Image.open(B/f'{n}.png').resize((3000,600)),(0,i*600))
thumb.quantize(colors=64).save(B/'overview.png',optimize=True)
