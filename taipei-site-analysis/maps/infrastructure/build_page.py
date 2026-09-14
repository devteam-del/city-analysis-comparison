from pathlib import Path
import csv,html
from PIL import Image
B=Path(__file__).resolve().parent
rows=list(csv.DictReader((B.parents[1]/'data/P017-pedestrians-20250625.csv').open()))
s=['<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 1050 390" width="1050" height="390"><rect width="1050" height="390" fill="#f3f3ee"/><g font-family="PingFang TC,Heiti TC,sans-serif" fill="#33413d">','<text x="32" y="40" font-size="24">承德／市民路口：已記錄的行人通行</text>','<text x="32" y="69" font-size="15">P017｜2025-06-25｜人次／各一小時；非尖峰與離峰實驗</text>']
for i,arm in enumerate('ABCD'):
 y=110+i*56;a,b=[r for r in rows if r['arm']==arm];names=['東側／天橋','南側／平面','西側／平面','北側／天橋']
 s.append(f'<text x="32" y="{y+17}" font-size="18">{names[i]}</text>')
 for dy,r,col in [(0,a,'#8d9e82'),(23,b,'#688a98')]:
  v=int(r['total_persons']);s.append(f'<rect x="190" y="{y+dy}" width="{v*.68}" height="17" fill="{col}"/><text x="{200+v*.68}" y="{y+dy+14}" font-size="15">{v}</text><text x="815" y="{y+dy+14}" font-size="14">{r["period_start"]}–{r["period_end"]}</text>')
s.append('<text x="32" y="364" font-size="15">晚間南側調查時窗不同，不合併加總；地面與天橋以外的地下通行未納入。</text></g></svg>')
chart=''.join(s);(B/'P017-chart.svg').write_text(chart)
intro='<p class="eyebrow">TAIPEI / INFRASTRUCTURE STUDY / 2026.09.14</p><h1>先讀設施，再讀關係。</h1><p>市民大道・環河—中山周邊<br>三張同範圍、同比例平面圖。A3 原尺寸 1:5,000。</p><nav><a href="#green">公園綠地</a><a href="#transport">交通</a><a href="#commerce">商業帶</a><a href="#reading">連貫分析</a></nav>'
sections=[]
for id,slug,title,caption in [('green','01-green','01 公園綠地','公園、植被與廣場分開表達；不可把全部開放空間當成綠地。'),('transport','02-transport','02 交通設施','同一片地區有地面、高架、地下三個層次；站體投影不是出入口。'),('commerce','03-commerce','03 商業帶','深褐是商業所在建築；淡褐是文獻商圈的沿街調查圖塊，非逐戶用途。')]:
 svg=(B/f'{slug}.svg').read_text().replace('id="map"',f'id="{slug}-map"').replace('url(#map)',f'url(#{slug}-map)').replace('id="geography"',f'id="{slug}-geography"').replace('id="surface-road-sides"',f'id="{slug}-roads"').replace('id="elevated-road-top"',f'id="{slug}-elevated"');sections.append(f'<section id="{id}"><div class="sectionhead"><h2>{title}</h2><a download href="{slug}.svg">下載 SVG ↗</a></div><div class="map">{svg}</div><p class="caption">{caption}</p>'+('<div class="chart">'+chart+'</div>' if id=='transport' else '')+'</section>')
reading='''<section id="reading"><p class="eyebrow">READING THE THREE MAPS</p><h2>三組設施關係，三種調查情境。</h2><div class="readgrid"><article><h3>01 日常服務 × 休憩</h3><p>玉泉公園與中興院區位在高架兩側。先追查兩者的出入口、過街與停留，檢驗是否存在跨側生活連結。</p></article><article><h3>02 轉乘 × 開放空間</h3><p>北門、鐵道部與行旅廣場相鄰。空間接近是否轉化為連續旅程，仍取決於出口、開放時間和過街條件。</p></article><article><h3>03 街道商業 × 站體商業</h3><p>後站／華陰與京站呈現不同商業形式；南側還有站前店及南陽商圈。應追查出站後的去向，不能只比較車站總流量。</p></article></div><p class="conclusion">這些圖支持「按設施交接處分段調查」，尚未證明整條市民大道造成南北分隔。</p><p>下一步：同時段記錄出入口、地面／地下通行與停留，再檢驗 L0–L2。先不提出改造方案。</p><a href="ANALYSIS.md">完整分析、來源與證據限制 ↗</a></section>'''
foot='''<footer>圖形依實際座標繪製；白色道路雙側線沿用舊路寬推算，非實測路緣。高架寬度示意，留白不等於已確認人行道。<br>公園及建築依 OpenStreetMap／ODbL；商圈依臺北市商業處、臺北旅遊網及業者資料。完整來源見分析文件。</footer>'''
css='''*{box-sizing:border-box}html{scroll-behavior:smooth}body{margin:0;background:#f3f3ee;color:#33413d;font-family:"PingFang TC",sans-serif}header,section,footer{max-width:1500px;margin:auto;padding:36px 32px}header{padding-top:64px}h1{font-size:46px;letter-spacing:-2px;margin:12px 0}h2{font-size:26px}p{line-height:1.9}.eyebrow{font-size:12px;letter-spacing:2px;color:#6e7d72}.sectionhead{display:flex;align-items:center;justify-content:space-between}a{color:#4d706e;text-decoration:none;border-bottom:1px solid #a3b2a5}nav{display:flex;gap:24px;margin-top:30px}.map{background:#e3e5e1;border:1px solid #d5dad2}.map svg{width:100%;height:auto;display:block}.caption{font-size:15px;color:#6a7470}.chart{max-width:1000px;margin:36px auto}.chart svg{width:100%;height:auto}.readgrid{display:grid;grid-template-columns:repeat(3,1fr);gap:36px}.readgrid h3{font-size:20px}.conclusion{font-size:25px;max-width:900px;padding-top:28px;border-top:1px solid #bdc6bb}footer{font-size:12px;line-height:1.8;color:#718073;padding-bottom:64px}@media(max-width:700px){header,section,footer{padding:24px 16px}h1{font-size:32px}.readgrid{grid-template-columns:1fr;gap:10px}nav{gap:12px;font-size:13px}}@media print{nav,a,header,footer,.caption,.chart,#reading,.sectionhead{display:none}section{padding:0;margin:0;break-after:page}.map{border:0}.map svg{width:420mm;height:297mm}@page{size:A3 landscape;margin:0}}'''
(B/'index.html').write_text('<!doctype html><html lang="zh-Hant"><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>市民大道｜三張基礎設施圖</title><style>'+css+'</style><header>'+intro+'</header>'+''.join(sections)+reading+foot+'</html>')
thumb=Image.new('RGB',(2520,594),'#e3e5e1')
for i,n in enumerate(['01-green','02-transport','03-commerce']):thumb.paste(Image.open(B/f'{n}.png').resize((840,594)),(i*840,0))
thumb.save(B/'overview.png')
print('Created standalone index.html, chart, overview')
