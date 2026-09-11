import sys,json,pathlib,math,html,collections
ROOT=pathlib.Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'.geo-libs'))
from shapely.geometry import shape,box,mapping
from shapely.ops import transform
from PIL import Image,ImageDraw,ImageFont
from pyproj import Transformer
DATA=ROOT/'actual-data';OUT=ROOT/'actual-output';OUT.mkdir(exist_ok=True)
AREAS=json.load(open(DATA/'areas.json'));T=Transformer.from_crs(4326,3857,always_xy=True)
F='/System/Library/Fonts/STHeiti Medium.ttc';R='/System/Library/Fonts/STHeiti Light.ttc'
INK='#203C45';SUB='#54676C';BG='#F7F7F2'
def ft(s,b=False):return ImageFont.truetype(F if b else R,s)
def txt(im,x,y,s,size=28,color=INK,b=False):ImageDraw.Draw(im).text((x,y),s,font=ft(size,b),fill=color)
NAMES={'nihonbashi':'日本橋 / Nihonbashi','crossbronx':'Cross-Bronx / West Farms','westside':'West Side / Meatpacking'}
def get_features(key):
 if key=='nihonbashi':
  raw=json.load(open(DATA/'nihonbashi_vectors_3857.geojson'))['features'];return [(f['properties']['source_layer'],shape(f['geometry']),f['properties']) for f in raw]
 fs=[]
 for label in ['water','structures','parks','sidewalk','roadbed','bridges','shoreline','buildings']:
  p=DATA/f'{key}_{label}.geojson'
  if p.exists():
   for f in json.load(open(p))['features']:
    if f['geometry']:fs.append((label,transform(T.transform,shape(f['geometry'])),f['properties']))
 return fs
STYLES={
 'WA':('#CEE6ED','#64909B',1.5),'water':('#CEE6ED','#64909B',1.5),
 'structures':('#EFEEE6','#768383',1),'parks':('#DFE7D7','#819775',1),
 'sidewalk':('#EFEDE3','#C2BEB1',.6),'roadbed':('#FFFFFF','#ADB7B8',1),'bridges':('#E4E9E7','#718789',1.3),
 'BldA':('#E1DBCC','#5D625D',1),'buildings':('#E1DBCC','#5D625D',1),
 'RdEdg':(None,'#9AA4A5',1),'RdCompt':(None,'#A0ABAC',.7),
 'RailCL':(None,'#A9998D',1),'RailTrCL':(None,'#BFB4AC',.5),
 'WL':(None,'#65909C',1.5),'shoreline':(None,'#65909C',1.5)}
ORDER=['WA','water','structures','parks','sidewalk','roadbed','bridges','RailTrCL','RailCL','RdCompt','RdEdg','BldA','buildings','WL','shoreline']
def plan(key):
 d=AREAS[key];bb=d['merc_bounds'];west,south,east,north=bb;bounds=box(*bb)
 w=2800;h=round(w*d['size_m'][1]/d['size_m'][0]);im=Image.new('RGB',(w,h),BG);draw=ImageDraw.Draw(im)
 def xy(x,y):return ((x-west)/(east-west)*w,(north-y)/(north-south)*h)
 svg=[f'<svg xmlns="http://www.w3.org/2000/svg" width="{w}" height="{h}" viewBox="0 0 {w} {h}"><rect width="100%" height="100%" fill="{BG}"/>']
 features=get_features(key);out=[];counts=collections.Counter()
 for layer in ORDER:
  for name,g,p in features:
   if name!=layer:continue
   if not g.is_valid:g=g.buffer(0)
   g=g.intersection(bounds)
   if g.is_empty:continue
   counts[name]+=1;out.append({'type':'Feature','properties':dict(p,source_layer=name),'geometry':mapping(g)})
   fill,stroke,sw=STYLES[name]
   def drawg(g):
    if hasattr(g,'geoms'):
     for gg in g.geoms:drawg(gg)
    elif g.geom_type=='Polygon':
     rings=[g.exterior]+list(g.interiors);paths=[]
     for ri,r in enumerate(rings):
      pts=[xy(x,y) for x,y in r.coords]
      if len(pts)<3:continue
      if fill:draw.polygon(pts,fill=fill if ri==0 else BG)
      draw.line(pts,fill=stroke,width=max(1,round(sw)),joint='curve')
      paths.append('M'+' L'.join(f'{x:.2f},{y:.2f}' for x,y in pts)+' Z')
     svg.append(f'<path d="{" ".join(paths)}" fill="{fill or "none"}" fill-rule="evenodd" stroke="{stroke}" stroke-width="{sw}"/>')
    elif g.geom_type in ['LineString','LinearRing']:
     pts=[xy(x,y) for x,y in g.coords]
     if len(pts)<2:return
     draw.line(pts,fill=stroke,width=max(1,round(sw)),joint='curve')
     svg.append(f'<path d="M'+ ' L'.join(f'{x:.2f},{y:.2f}' for x,y in pts)+f'" fill="none" stroke="{stroke}" stroke-width="{sw}"/>')
   drawg(g)
 labels=[]
 if key=='nihonbashi':
  wanted=['日本銀行','東京駅','日本橋駅','三越前駅','江戸橋ＪＣＴ'];seen=set()
  for f in json.load(open(DATA/'nihonbashi_vectors_3857.geojson'))['features']:
   p=f['properties'];name=p.get('vt_text')
   if name in wanted and name not in seen and f['geometry']['type']=='Point':labels.append((name,*f['geometry']['coordinates']));seen.add(name)
 else:
  wanted=['CROSS BRONX EXPY','SHERIDAN BLVD','BOSTON RD','CROTONA PKWY','E 174 ST BRG'] if key=='crossbronx' else ['WEST ST','GANSEVOORT ST','W 14 ST','WASHINGTON ST']
  fs=json.load(open(DATA/f'{key}_centerline.geojson'))['features']
  for name in wanted:
   lines=[transform(T.transform,shape(f['geometry'])).intersection(bounds) for f in fs if f['properties'].get('STNAME_LABEL')==name]
   lines=[g for g in lines if not g.is_empty]
   if lines:
    g=max(lines,key=lambda x:x.length);pt=g.interpolate(.5,normalized=True);labels.append((name,pt.x,pt.y))
 for name,x,y in labels:
  px,py=xy(x,y);font=ft(25,True);bbx=draw.textbbox((0,0),name,font=font);tw=bbx[2]
  px=max(12,min(w-tw-14,px-tw/2));py=max(12,min(h-50,py-20))
  draw.rectangle((px-7,py-5,px+tw+7,py+32),fill='white');draw.text((px,py),name,font=font,fill=INK)
  svg.append(f'<rect x="{px-7:.2f}" y="{py-5:.2f}" width="{tw+14}" height="37" fill="white"/><text x="{px:.2f}" y="{py+25:.2f}" font-family="sans-serif" font-size="25" fill="{INK}">{html.escape(name)}</text>')
 svg.append('</svg>');(OUT/f'{key}_linework.svg').write_text('\n'.join(svg))
 im.save(DATA/f'{key}_linework.png')
 (OUT/f'{key}_source_geometry_3857.geojson').write_text(json.dumps({'type':'FeatureCollection','crs':{'type':'name','properties':{'name':'EPSG:3857'}},'features':out},ensure_ascii=False))
 print(key,dict(counts),flush=True);return im,counts
def map_panel(im,pic,key,x,y,w,h):
 ratio=min(w/pic.width,h/pic.height);pic=pic.resize((round(pic.width*ratio),round(pic.height*ratio)),Image.Resampling.LANCZOS);xx=x+(w-pic.width)//2;yy=y+(h-pic.height)//2
 im.paste(pic,(xx,yy));dr=ImageDraw.Draw(im);dr.rectangle((xx,yy,xx+pic.width,yy+pic.height),outline='#AAB8BA',width=2)
 # True north in Web Mercator; local ground distance at frame centre.
 dr.rectangle((xx+pic.width-75,yy+14,xx+pic.width-14,yy+117),fill='white')
 txt(im,xx+pic.width-59,yy+22,'N',26,b=True);dr.line((xx+pic.width-45,yy+105,xx+pic.width-45,yy+60),fill=INK,width=3);dr.polygon([(xx+pic.width-45,yy+53),(xx+pic.width-53,yy+70),(xx+pic.width-37,yy+70)],fill=INK)
 bar=pic.width*200/AREAS[key]['size_m'][0]
 dr.rectangle((xx+15,yy+pic.height-75,xx+35+bar,yy+pic.height-13),fill='white')
 dr.line((xx+25,yy+pic.height-34,xx+25+bar,yy+pic.height-34),fill=INK,width=5)
 for bx in [xx+25,xx+25+bar]:dr.line((bx,yy+pic.height-43,bx,yy+pic.height-25),fill=INK,width=3)
 txt(im,xx+25,yy+pic.height-70,'0',21);txt(im,xx+bar-20,yy+pic.height-70,'200 m',21)
 return xx,yy,pic.width,pic.height
NOTES={
 'nihonbashi':['歷史底圖：國土地理院 1974–1978 年空中照片。','現行線圖：GSI 最適化向量圖資，2026-04-01 更新批次。','右圖保留既有高架；地下化方案另見官方平面圖，不冒充完工現況。'],
 'crossbronx':['歷史底圖：NYC 1996 年正射航照，公路已存在。','現行線圖：NYC 2022 平面測繪＋2026-09-11 下載建築輪廓。','2025 官方加蓋願景另頁對照；現行線圖不自行新增加蓋邊界。'],
 'westside':['歷史底圖：NYC 1951 年航照，可核對高架與原有碼頭。','現行線圖：NYC 2022 平面測繪＋2026-09-11 下載建築輪廓。','另附 2024 航照核對頁：Gansevoort 公園內部改造晚於 2022 測繪。']}
for idx,key in enumerate(AREAS,1):
 drawing,counts=plan(key)
 # Primary review: historical evidence vs actual footprint linework.
 board=Image.new('RGB',(3400,2350),BG);dr=ImageDraw.Draw(board)
 txt(board,90,60,'ACTUAL GEOMETRY / PLAN REVIEW',28,SUB)
 txt(board,90,112,NAMES[key],64,b=True)
 txt(board,90,205,'歷史底圖 × 實際輪廓平面圖',34,SUB)
 txt(board,3140,76,f'0{idx}',66,'#9DAFAF')
 dr.line((90,275,3310,275),fill='#BDCBCB',width=2)
 txt(board,90,313,'BEFORE / '+AREAS[key]['old']+' 歷史航照',34,b=True)
 txt(board,1760,313,'現行測繪 / 建築、道路、水域',34,b=True)
 map_panel(board,Image.open(DATA/f'{key}_historic.png'),key,90,385,1550,1630)
 map_panel(board,drawing,key,1760,385,1550,1630)
 for i,line in enumerate(NOTES[key]):txt(board,90,2070+i*49,line,29,SUB)
 txt(board,90,2250,'兩圖同範圍、同北向、同尺度。歷史航照是年代證據，尚未逐棟描繪成歷史向量。',27,INK)
 txt(board,90,2300,'來源：'+('国土地理院 / 地理院タイル・最適化ベクトルタイル（裁切、重繪）' if key=='nihonbashi' else '© City of New York / NYC OTI / CC BY 4.0（裁切、重繪）'),23,SUB)
 board.save(OUT/f'{key}_plan_comparison.png')
 # Readable full-size source-derived plan with legend and scale.
 pw=3200;ph=round(2800*AREAS[key]['size_m'][1]/AREAS[key]['size_m'][0])+570
 sheet=Image.new('RGB',(pw,ph),BG);txt(sheet,95,62,NAMES[key]+' / 實際輪廓平面',52,b=True)
 txt(sheet,95,142,NOTES[key][1],28,SUB)
 map_panel(sheet,drawing,key,200,225,2800,ph-570)
 yy=ph-240
 legend=[('#E1DBCC','建築輪廓'),('#FFFFFF','實際道路面／邊線'),('#CEE6ED','水域／岸線'),('#DFE7D7','測繪公園範圍')]
 for i,(c,l) in enumerate(legend):
  x=95+i*700;ImageDraw.Draw(sheet).rectangle((x,yy,x+30,yy+30),fill=c,outline=INK);txt(sheet,x+48,yy-4,l,26)
 txt(sheet,95,ph-168,'範圍 '+str(AREAS[key]['size_m'][0])+' × '+str(AREAS[key]['size_m'][1])+' m；線圖由官方座標重繪，無隨機街廓或假定建物高度。',27,SUB)
 txt(sheet,95,ph-112,NOTES[key][2],25,SUB)
 txt(sheet,95,ph-58,'來源：'+('国土地理院最適化ベクトルタイル（加工）' if key=='nihonbashi' else '© City of New York / NYC OTI / CC BY 4.0')+'；圖幅為平面核對稿，非施工測量成果。',23,SUB)
 sheet.save(OUT/f'{key}_actual_plan.png')
 if key!='nihonbashi' and (DATA/f'{key}_2024.png').exists():
  image=Image.new('RGB',(3400,2350),BG);txt(image,90,70,NAMES[key]+' / 年代核對',58,b=True)
  txt(image,90,165,'歷史航照與 2024 正射航照；固定範圍、固定北向。',31,SUB)
  for j,(file,label) in enumerate([(f'{key}_historic.png',AREAS[key]['old']+' / BEFORE'),(f'{key}_2024.png','2024 / 現況航照')]):
   txt(image,90+1670*j,275,label,36,b=True);map_panel(image,Image.open(DATA/file),key,90+1670*j,355,1550,1740)
  txt(image,90,2180,'1951 航照採歷史影像人工定位；高樓屋頂位移及歷史定位誤差，不能視為精密地籍界線。' if key=='westside' else '2024 為已取得的較新官方航照年份；不代表全部地物在 2026 年仍相同。',29,SUB)
  txt(image,90,2260,'© City of New York / NYC OTI / CC BY 4.0；資料下載 2026-09-11。',26,SUB)
  image.save(OUT/f'{key}_aerial_comparison.png')
