import sys,pathlib,json
ROOT=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'.geo-libs'))
import requests
DATA=ROOT/'actual-data';areas=json.load(open(DATA/'areas.json'))
base='https://services6.arcgis.com/yG5s3afENB5iO9fj/ArcGIS/rest/services/'
services={'roadbed':'Roadbed_2022','shoreline':'Shoreline_2022','water':'Hydrography_2022','structures':'Hydro_Structure_2022','sidewalk':'Sidewalk_2022'}
for label,service in services.items():
 url=base+service+'/FeatureServer';meta=requests.get(url,params={'f':'json'},timeout=40).json();(DATA/(label+'_metadata.json')).write_text(json.dumps(meta));layer=meta['layers'][0]['id']
 for key in ['crossbronx','westside']:
  p=DATA/f'{key}_{label}.geojson'
  if p.exists():continue
  params={'f':'geojson','where':'1=1','geometry':','.join(map(str,areas[key]['bbox'])),'geometryType':'esriGeometryEnvelope','inSR':4326,'spatialRel':'esriSpatialRelIntersects','outFields':'*','outSR':4326,'resultRecordCount':2000,'resultOffset':0}
  allf=[]
  while True:
   j=requests.get(url+f'/{layer}/query',params=params,timeout=60).json()
   if 'error' in j:raise ValueError(j)
   allf+=j['features']
   if not j.get('properties',{}).get('exceededTransferLimit'):break
   params['resultOffset']+=len(j['features'])
  p.write_text(json.dumps({'type':'FeatureCollection','features':allf}));print(key,label,len(allf),flush=True)
# Complete the truncated building page; never silently omit data.
p=DATA/'crossbronx_buildings.geojson';j=json.load(open(p))
if j.get('properties',{}).get('exceededTransferLimit'):
 params={'f':'geojson','where':'1=1','geometry':','.join(map(str,areas['crossbronx']['bbox'])),'geometryType':'esriGeometryEnvelope','inSR':4326,'spatialRel':'esriSpatialRelIntersects','outFields':'*','outSR':4326,'resultRecordCount':2000,'resultOffset':len(j['features'])}
 while True:
  more=requests.get(base+'BUILDING_view/FeatureServer/0/query',params=params,timeout=60).json();j['features']+=more['features']
  if not more.get('properties',{}).get('exceededTransferLimit'):break
  params['resultOffset']+=len(more['features'])
 j['properties']['exceededTransferLimit']=False;p.write_text(json.dumps(j));print('Complete buildings',len(j['features']),flush=True)
item=requests.get('https://www.arcgis.com/sharing/rest/content/items/423f15185bd04f8dad8d99fba736772f',params={'f':'json'},timeout=30).json()
(DATA/'nyc_2024_item.json').write_text(json.dumps(item));print('2024 imagery',item.get('url'),flush=True)
