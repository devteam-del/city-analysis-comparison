from fetch_actual import *
for key in ['crossbronx','westside']:
 d=CASES[key];z=18;west,south,east,north=d['merc_bounds'];circ=40075016.68557849;scale=256*2**z/circ
 px0=(west+circ/2)*scale;py0=(circ/2-north)*scale;px1=(east+circ/2)*scale;py1=(circ/2-south)*scale
 x0=int(px0//256);x1=int(px1//256);y0=int(py0//256);y1=int(py1//256)
 im=Image.new('RGB',((x1-x0+1)*256,(y1-y0+1)*256),'white')
 url=json.load(open(DATA/'nyc_2024_item.json'))['url']
 def tile(t):
  x,y=t;p=CACHE/f'{key}_2024_{z}_{x}_{y}.img';b=get(f'{url}/tile/{z}/{y}/{x}',p);return x,y,Image.open(io.BytesIO(b)).convert('RGB')
 with concurrent.futures.ThreadPoolExecutor(max_workers=6) as ex:
  for x,y,pic in ex.map(tile,[(x,y) for x in range(x0,x1+1) for y in range(y0,y1+1)]):im.paste(pic,((x-x0)*256,(y-y0)*256))
 im.crop((round(px0-x0*256),round(py0-y0*256),round(px1-x0*256),round(py1-y0*256))).save(DATA/f'{key}_2024.png');print(key,'2024 done',flush=True)
# Official parks layer for ground-plan colouring.
url='https://services6.arcgis.com/yG5s3afENB5iO9fj/ArcGIS/rest/services/Park_2022/FeatureServer'
meta=S.get(url,params={'f':'json'},timeout=30).json();layer=meta['layers'][0]['id'];(DATA/'parks_metadata.json').write_text(json.dumps(meta))
for key in ['crossbronx','westside']:
 params={'f':'geojson','where':'1=1','geometry':','.join(map(str,CASES[key]['bbox'])),'geometryType':'esriGeometryEnvelope','inSR':4326,'spatialRel':'esriSpatialRelIntersects','outFields':'*','outSR':4326,'resultRecordCount':2000}
 b=get(url+f'/{layer}/query',DATA/f'{key}_parks.geojson',params);print(key,'parks',len(json.loads(b)['features']),flush=True)
