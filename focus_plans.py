"""Generate paired vector study windows; historical observations are never inferred from current footprints."""
from pathlib import Path
import sys,json,html,math
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'.geo-libs'))
from shapely.geometry import shape,Polygon,LineString,box,mapping
from shapely.ops import transform
STYLE={'roof':('#e1dbcc','#5d625d'),'road':('#ffffff','#77888c'),'water':('#cee6ed','#64909b'),'land':('#e3eadf','#95a18c'),'rail':('none','#9b8b7c'),'pending':('PATTERN','#b19c77')}
def augment(cases,areas,traces,asset):
 configs=json.loads((ROOT/'historical/focus-v2.json').read_text())
 for c in cases:
  k=c['id'];f=configs[k];bb=f['bbox'];fw=bb[2]-bb[0];fh=bb[3]-bb[1];ow,oh=traces[k]['view'];bounds=box(*bb)
  west,south,east,north=areas[k]['merc_bounds']
  def xy(x,y,z=None):return ((x-west)/(east-west)*ow,(north-y)/(north-south)*oh)
  def geographic(x,y,z=None):
   mx=west+x/ow*(east-west);my=north-y/oh*(north-south)
   return mx/20037508.342789244*180,math.degrees(2*math.atan(math.exp(my/6378137))-math.pi/2)
  def render(entries,side):
   pid=k+'-'+side+'-hatch';svg=[f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="{bb[0]} {bb[1]} {fw} {fh}" role="img" aria-label="{c["name"]}{side}重點平面"><defs><pattern id="{pid}" width="6" height="6" patternUnits="userSpaceOnUse"><rect width="6" height="6" fill="#f4f0e7"/><path d="M0 6L6 0" stroke="#c8b99c" stroke-width=".45"/></pattern></defs><rect x="{bb[0]}" y="{bb[1]}" width="{fw}" height="{fh}" fill="#f7f7f2"/>'];geos=[]
   for layer,label,g in entries:
    if not g.is_valid:g=g.buffer(0)
    g=g.intersection(bounds)
    if g.is_empty:continue
    geos.append({'type':'Feature','properties':{'layer':layer,'label':label,'method':'manual historical aerial interpretation' if side=='before' else 'official current vector data'},'geometry':mapping(transform(geographic,g))})
    fill,stroke=STYLE[layer];fill=fill.replace('PATTERN',f'url(#{pid})')
    def draw(g):
     if hasattr(g,'geoms'):
      for child in g.geoms:draw(child)
     elif g.geom_type=='Polygon':
      d=' '.join('M'+'L'.join(f'{x:.2f},{y:.2f}' for x,y in ring.coords)+'Z' for ring in [g.exterior,*g.interiors])
      svg.append(f'<path d="{d}" fill="{fill}" fill-rule="evenodd" stroke="{stroke}" stroke-width=".6"><title>{html.escape(label)}</title></path>')
     elif g.geom_type=='LineString':svg.append('<path d="M'+'L'.join(f'{x:.2f},{y:.2f}' for x,y in g.coords)+f'" fill="none" stroke="{stroke}" stroke-width=".55"/>')
    draw(g)
   svg.append('</svg>');out=''.join(svg)
   (ROOT/f'historical/{k}_focus_{side}.svg').write_text(out)
   (ROOT/f'historical/{k}_focus_{side}.geojson').write_text(json.dumps({'type':'FeatureCollection','features':geos},ensure_ascii=False))
   return out
  # Pending zones form explicit coverage masks, beneath verified visible features.
  history=[(layer,label,LineString(pts) if layer=='rail' else Polygon(pts)) for layer,label,pts in f['features']]
  history.sort(key=lambda x:['pending','land','water','roof','rail','road'].index(x[0]))
  c['focusBefore']=render(history,'before')
  source=ROOT/f'actual-output/{k}_source_geometry_3857.geojson'
  if source.exists():
   fs=json.loads(source.read_text())['features'];entries=[]
   kinds={'WA':'water','water':'water','parks':'land','structures':'road','sidewalk':'road','roadbed':'road','bridges':'road','BldA':'roof','buildings':'roof','RdEdg':'road','RdCompt':'road','RailCL':'rail','RailTrCL':'rail','WL':'water','shoreline':'water'}
   for feature in fs:
    layer=feature['properties']['source_layer']
    if layer in kinds:entries.append((kinds[layer],layer,transform(xy,shape(feature['geometry']))))
   c['focusAfter']=render(entries,'after')
  else:c['focusAfter']=(ROOT/f'historical/{k}_focus_after.svg').read_text()
  c.update(focus=f,focusWidth=round(areas[k]['size_m'][0]*fw/ow),focusHeight=round(areas[k]['size_m'][1]*fh/oh),focusRatio=fw/fh,originalView=[ow,oh])
  c['recentYear']='2019 年度' if k=='nihonbashi' else '2024'
  if k=='nihonbashi':c['recent']=asset(Path('actual-data/nihonbashi_2019.png'))
