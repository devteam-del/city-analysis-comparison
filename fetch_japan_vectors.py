import sys,pathlib,json,gzip,math,functools
ROOT=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'.geo-libs'))
import requests,mapbox_vector_tile
from pmtiles.reader import Reader
from shapely.geometry import shape,mapping,box
from shapely.ops import transform,unary_union
DATA=ROOT/'actual-data';cache=DATA/'pmtiles';cache.mkdir(exist_ok=True)
url='https://cyberjapandata.gsi.go.jp/xyz/optimal_bvmap-v1/optimal_bvmap-v1.pmtiles'
@functools.lru_cache(maxsize=256)
def get_bytes(offset,length):
 p=cache/f'{offset}_{length}.bin'
 if not p.exists():
  r=requests.get(url,headers={'Range':f'bytes={offset}-{offset+length-1}'},timeout=45)
  if r.status_code!=206:raise ValueError('Expected HTTP partial response, got '+str(r.status_code))
  p.write_bytes(r.content)
 return p.read_bytes()
reader=Reader(get_bytes);meta=reader.metadata();(DATA/'gsi_vector_metadata.json').write_text(json.dumps(meta,ensure_ascii=False,indent=2))
d=json.load(open(DATA/'areas.json'))['nihonbashi'];west,south,east,north=d['merc_bounds'];circ=40075016.68557849;z=16;n=2**z
x0=int((west+circ/2)/circ*n);x1=int((east+circ/2)/circ*n);y0=int((circ/2-north)/circ*n);y1=int((circ/2-south)/circ*n)
features=[];bounds=box(west,south,east,north);counts={}
for x in range(x0,x1+1):
 for y in range(y0,y1+1):
  b=reader.get(z,x,y)
  if b[:2]==b'\x1f\x8b':b=gzip.decompress(b)
  layers=mapbox_vector_tile.decode(b)
  for name,layer in layers.items():
   counts[name]=counts.get(name,0)+len(layer['features']);extent=layer['extent']
   for f in layer['features']:
    geom=shape(f['geometry']);g=transform(lambda a,b:((x+a/extent)/n*circ-circ/2,circ/2-(y+1-b/extent)/n*circ),geom)
    if not g.is_valid:g=g.buffer(0)
    g=g.intersection(bounds)
    if g.is_empty:continue
    f['geometry']=mapping(g);f['properties']['source_layer']=name;features.append(f)
print(counts,flush=True)
result={'type':'FeatureCollection','crs':{'type':'name','properties':{'name':'EPSG:3857'}},'features':features}
(DATA/'nihonbashi_vectors_3857.geojson').write_text(json.dumps(result,ensure_ascii=False))
print('Features in area:',len(features),flush=True)
for name in sorted(counts):
 fs=[f for f in features if f['properties']['source_layer']==name]
 if fs:print(name,fs[0]['properties'],flush=True)
