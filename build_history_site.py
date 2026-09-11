from pathlib import Path
from PIL import Image
import base64,io,json,html,math
ROOT=Path(__file__).resolve().parent
def asset(path,limit=1800):
 im=Image.open(ROOT/path).convert('RGB');im.thumbnail((limit,limit));b=io.BytesIO();im.save(b,format='JPEG',quality=90)
 return 'data:image/jpeg;base64,'+base64.b64encode(b.getvalue()).decode()
areas=json.loads((ROOT/'actual-data/areas.json').read_text())
traces=json.loads((ROOT/'historical/traces.json').read_text())
common='歷史線稿為本次依官方航照人工判讀的選定道路邊緣與屋頂輪廓；不是完整逐棟地籍或測量成果。屋頂受透視位移影響，不能直接視為地面建物足跡。未描繪處不代表當時沒有建物。'
cases=[dict(id='nihonbashi',name='日本橋',city='東京，日本',en='NIHONBASHI / TOKYO',verb='埋入',concept='讓被遮蔽的河川重新成為主角',year='1974–1978',after='2026 地理院向量底圖',size='1,450 × 1,150 m',status='地下化工程進行中；After 方案尚未完成',
 fact='首都高於 1963 年跨越日本橋川。官方地下化計畫將交通轉入新隧道，再拆除河川上方高架；地下路線與周邊再開發共同推進。',
 read='看歷史圖中沿河彎折的紅線：高架利用河道上空穿越密集街廓。它既是交通路徑，也是遮蔽河川的水平構造。現況底圖保留可取得的建物與道路幾何；未將未來拆除的高架提前擦去。',
 post='日本橋的「回到歷史」可以被讀成一次選擇性的編輯。河川與橋重新成為視覺主角，戰後汽車城市的構造則移入地下；兩個時代仍共存，只有可見的順序改變。以後現代視角看，復原的不是一張不曾改寫的原稿，而是當代工程、再開發與歷史意象共同組成的新敘事。',
 question='當河景被重新揭露，戰後基礎設施的記憶要留在哪裡？',
 timeline=[['1963','河川上方路線開通'],['1974–78','本頁歷史航照'],['2019','地下路線方案決定'],['2035 年度','地下路線完成目標'],['2040 年度','高架撤除完成目標']],
 source='https://www.shutoko.jp/ss/nihonbashi-tikaka/overview/',official='nihonbashi_official_plan_crop.png',official_note='首都高官方路線平面圖節錄。圖面含地下化、既有及撤除路段圖例；原圖為方案示意，未強行套疊成精確施工座標。',
 trace_note='河川多被高架或陰影遮蔽，未推算被遮蔽的歷史水岸線。1974–78 是高架使用期，不是江戶時代或高架興建前。'),
 dict(id='crossbronx',name='Cross-Bronx',city='紐約，美國',en='WEST FARMS / NEW YORK',verb='覆蓋',concept='在仍運作的道路上補回城市連結',year='1996',after='2022 平面資料＋更新建物圖資',size='1,700 × 1,250 m',status='2025 官方願景；覆蓋構想仍需研究與資金',
 fact='Reimagine the Cross Bronx 2025 最終願景提出街道、安全與公共空間改善，以及部分路段加蓋等長期構想。West Farms 視窗呈現道路、匝道與 Bronx River 交織的地景。',
 read='歷史線稿沿 Cross-Bronx 與 Sheridan 道路邊緣勾勒分割尺度；藍色虛線只標示可從航照判讀的河流走向。現況仍有高速道路；下方官方圖另列潛在覆蓋位置，不能把整條高速公路讀成已經公園化。',
 post='這裡的歷史不是值得復刻的完整街景，而是仍在發生的分割。覆蓋與跨越可以理解為拼接：車流、河流與居民生活在不同高度上協商位置。後現代的閱讀容許這種矛盾並置，也提醒我們，新的綠色表面不會自動解決下方交通的所有影響；「修補」必須持續接受日常使用者的檢驗。',
 question='連接了兩側地面之後，居民的健康、通行與參與是否也得到改善？',
 timeline=[['1950–60 年代','高速道路主要興建期'],['1996','本頁歷史航照'],['2024','本頁近期航照'],['2025','發布最終願景'],['後續','加蓋須進一步研究、設計與籌資']],
 source='https://www.nyc.gov/html/dot/html/pr2025/final-report-reconnect-communities-cbe.shtml',official='crossbronx_official_plan_crop.png',official_note='Reimagine the Cross Bronx Final Vision，Figure 4.20 潛在加蓋位置圖節錄。此圖是整條走廊尺度，範圍大於上方 West Farms 視窗，不能逐像素對位。',
 trace_note='1996 是高速道路已存在的年代，不能用來推論興建前街廓。樹冠遮蔽的河岸以低可信度虛線表示。'),
 dict(id='westside',name='West Side',city='紐約，美國',en='MEATPACKING / NEW YORK',verb='拆除・轉用',concept='把貨運水岸改寫成公共遊憩地景',year='1951',after='2022 平面資料＋更新建物圖資',size='1,250 × 1,300 m',status='公園已分期開放；另附 2024 航照核對',
 fact='1973 年高架道路局部坍塌成為轉折。1998 年 Hudson River Park Act 建立公園框架，水岸逐步轉向公共休憩。今天的新公園形狀與舊碼頭的狹長節奏形成鮮明對照。',
 read='1951 年圖中一排向水面伸出的屋頂，是可辨識的碼頭倉庫；東側紅色雙線是當時高架路面邊緣。2024 航照可核對 Little Island 與 Gansevoort Peninsula 的近期樣貌；2022 平面資料未包含所有後續公園內部變動。',
 post='West Side 把生產水岸轉譯成遊憩水岸，保留、消失與新造的形狀同時可讀。碼頭的排列不再只服務貨物，而成為人們散步、觀看與辨認地方的線索。從後現代視角看，工業痕跡也可能變成可消費的城市意象；因此不能只看新地景是否精彩，還要追問公共性的使用條件。',
 question='當工業記憶成為遊憩風景，誰能自在、持續地使用這段水岸？',
 timeline=[['1951','本頁歷史航照'],['1973','高架局部坍塌'],['1998','Hudson River Park Act'],['2003','首個完整公園區段開放'],['2024','本頁近期航照']],
 source='https://hudsonriverpark.org/timeline-of-waterfront-history/',official=None,official_note='2024 年 NYC 正射影像作為已落成地景核對；與 1951 年採同一地理範圍。',
 trace_note='1951 航照可見拼接縫與透視位移；碼頭描繪的是可見屋頂，沒有把船舶、水面色差或投影當作岸線。')]
for c in cases:
 k=c['id'];d=traces[k];w,h=d['view'];features=[];parts=[];counts={}
 for i,(layer,label,confidence,pts) in enumerate(d['features']):
  counts[layer]=counts.get(layer,0)+1
  color={'roof':'#253f48','road':'#b74632','water':'#126b95'}[layer]
  dash='stroke-dasharray="7 5"' if confidence=='low' else ''
  tag='polygon' if layer=='roof' else 'polyline'
  p=' '.join(f'{x},{y}' for x,y in pts)
  parts.append(f'<{tag} class="trace-{layer}" points="{p}" fill="none" stroke="{color}" stroke-width="2" {dash} stroke-linejoin="round"><title>{html.escape(label)}｜航照判讀，{confidence}</title></{tag}>')
  west,south,east,north=areas[k]['merc_bounds'];coords=[]
  for x,y in pts:
   mx=west+x/w*(east-west);my=north-y/h*(north-south)
   coords.append([mx/20037508.342789244*180,math.degrees(2*math.atan(math.exp(my/6378137))-math.pi/2)])
  features.append(dict(type='Feature',properties=dict(id=f'{k}-{i+1:02}',layer=layer,label=label,confidence=confidence,method='manual aerial interpretation; roof projection, not surveyed footprint',source_year=c['year']),geometry=dict(type='Polygon' if layer=='roof' else 'LineString',coordinates=[coords] if layer=='roof' else coords)))
 svg=f'<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 {w} {h}" role="img" aria-label="{c["name"]}歷史判讀線稿">'+''.join(parts)+'</svg>'
 (ROOT/f'historical/{k}_historical.svg').write_text(svg)
 (ROOT/f'historical/{k}_historical.geojson').write_text(json.dumps(dict(type='FeatureCollection',features=features),ensure_ascii=False))
 c.update(svg=svg,counts=counts,aerial=asset(Path('actual-data')/(k+'_historic.png')),current=asset(Path('actual-data')/(k+'_linework.png'),2400),recent=asset(Path('actual-data')/(k+'_2024.png')) if k!='nihonbashi' else None,official_img=asset(Path('actual-data')/c['official'],2400) if c['official'] else None,ratio=w/h,width=areas[k]['size_m'][0],common=common)
from focus_plans import augment
augment(cases,areas,traces,asset)
from official_locator import add_locator
add_locator(cases)
template=(ROOT/'site-template.html').read_text()
data=json.dumps(cases,ensure_ascii=False).replace('</','<\\/')
page=template.replace('__CASE_DATA__',data)
(ROOT/'dist/index.html').write_text(page)
(ROOT/'urban-history-comparison.html').write_text(page)
print('Built single HTML:',round(len(page.encode())/1024/1024,2),'MB; historical features:',{c['id']:c['counts'] for c in cases})
