import sys, pathlib, json, math, concurrent.futures, io, re
ROOT=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'.geo-libs'))
import requests
from PIL import Image
DATA=ROOT/'actual-data';DATA.mkdir(exist_ok=True)
CACHE=DATA/'tiles';CACHE.mkdir(exist_ok=True)
S=requests.Session();S.headers['User-Agent']='Urban-plan-comparison/1.0 (public GIS research)'
CASES={
 'nihonbashi':{'center':[139.772,35.684],'size_m':[1450,1150],'old':'1974-1978','zoom':18},
 'crossbronx':{'center':[-73.8815,40.835],'size_m':[1700,1250],'old':'1996','zoom':18},
 'westside':{'center':[-74.0085,40.7405],'size_m':[1250,1300],'old':'1951','zoom':18}}
def get(url,path,params=None):
 if path.exists():return path.read_bytes()
 r=S.get(url,params=params,timeout=45);r.raise_for_status();path.write_bytes(r.content);return r.content
def merc(lon,lat):return (lon*20037508.342789244/180,math.log(math.tan(math.pi/4+math.radians(lat)/2))*6378137)
def lonlat(x,y):return [x/20037508.342789244*180,math.degrees(2*math.atan(math.exp(y/6378137))-math.pi/2)]
for key,d in CASES.items():
 cx,cy=merc(*d['center']);c=math.cos(math.radians(d['center'][1]));w,h=[v/c for v in d['size_m']]
 d['merc_bounds']=[cx-w/2,cy-h/2,cx+w/2,cy+h/2]
 d['bbox']=lonlat(cx-w/2,cy-h/2)+lonlat(cx+w/2,cy+h/2)
(DATA/'areas.json').write_text(json.dumps(CASES,indent=2))
def mosaic(key,kind):
 d=CASES[key];z=17 if key=='nihonbashi' and kind=='historic' else 18
 west,south,east,north=d['merc_bounds'];circ=40075016.68557849;scale=256*2**z/circ
 px0=(west+circ/2)*scale;py0=(circ/2-north)*scale;px1=(east+circ/2)*scale;py1=(circ/2-south)*scale
 x0=int(px0//256);x1=int(px1//256);y0=int(py0//256);y1=int(py1//256)
 im=Image.new('RGB',((x1-x0+1)*256,(y1-y0+1)*256),'white')
 if key=='nihonbashi':
  layer='gazo1' if kind=='historic' else 'std';ext='jpg' if kind=='historic' else 'png'
  template=f'https://cyberjapandata.gsi.go.jp/xyz/{layer}/{{z}}/{{x}}/{{y}}.{ext}'
 else:
  layer='photo/'+d['old'] if kind=='historic' else 'carto/basemap';ext='png8' if kind=='historic' else 'jpg'
  template=f'https://maps.nyc.gov/xyz/1.0.0/{layer}/{{z}}/{{x}}/{{y}}.{ext}'
 def tile(t):
  x,y=t;p=CACHE/f'{key}_{kind}_{z}_{x}_{y}.img'
  b=get(template.format(z=z,x=x,y=y),p);return x,y,Image.open(io.BytesIO(b)).convert('RGB')
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
  for x,y,pic in ex.map(tile,[(x,y) for x in range(x0,x1+1) for y in range(y0,y1+1)]):im.paste(pic,((x-x0)*256,(y-y0)*256))
 crop=im.crop((round(px0-x0*256),round(py0-y0*256),round(px1-x0*256),round(py1-y0*256)))
 crop.save(DATA/f'{key}_{kind}.png');print(key,kind,crop.size,flush=True)
 d[kind+'_template']=template
 return crop
if __name__=='__main__':
 for key in CASES:
  for kind in ['historic','current']:
   try:mosaic(key,kind)
   except Exception as e:print('ERROR',key,kind,str(e),flush=True)
 for key in ['crossbronx','westside']:
  d=CASES[key];params={'f':'geojson','where':'1=1','geometry':','.join(map(str,d['bbox'])),'geometryType':'esriGeometryEnvelope','inSR':'4326','spatialRel':'esriSpatialRelIntersects','outFields':'*','outSR':'4326','resultRecordCount':2000}
  try:
   b=get('https://services6.arcgis.com/yG5s3afENB5iO9fj/arcgis/rest/services/BUILDING_view/FeatureServer/0/query',DATA/f'{key}_buildings.geojson',params)
   j=json.loads(b);print(key,'buildings',len(j.get('features',[])),str(j)[:150],flush=True)
  except Exception as e:print('ERROR buildings',key,str(e),flush=True)
 for name,u in {'nihonbashi_official.pdf':'https://www.shutoko.jp/ss/nihonbashi-tikaka/gallery/nihonbashi_pamphlet_2nd.pdf','crossbronx_official.pdf':'https://www.nyc.gov/html/dot/downloads/pdf/reimagine-cross-bronx-final-vision.pdf','nyc_building_metadata.json':'https://services6.arcgis.com/yG5s3afENB5iO9fj/arcgis/rest/services/BUILDING_view/FeatureServer/0?f=pjson'}.items():
  try:print(name,len(get(u,DATA/name)),flush=True)
  except Exception as e:print('ERROR',name,str(e),flush=True)
 (DATA/'areas.json').write_text(json.dumps(CASES,indent=2))
