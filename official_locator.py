from pathlib import Path
import json
ROOT=Path(__file__).resolve().parent
def add_locator(cases):
 d=json.loads((ROOT/'historical/crossbronx-official-locator.json').read_text())
 def points(key):return ' '.join(f'{x},{y}' for x,y in d[key])
 svg=f'''<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 2653 860" role="img" aria-label="Figure 4.20 上的平面圖範圍索引：紅色實線為描圖視窗，藍色虛線為完整航照範圍">
 <polygon points="{points('aerial_polygon')}" fill="none" stroke="white" stroke-width="7"/>
 <polygon points="{points('aerial_polygon')}" fill="none" stroke="#126b95" stroke-width="3.5" stroke-dasharray="13 9"/>
 <polygon points="{points('focus_polygon')}" fill="#db603f" fill-opacity=".08" stroke="white" stroke-width="9"/>
 <polygon points="{points('focus_polygon')}" fill="none" stroke="#c84328" stroke-width="5"/>
 <path d="M1605 430L1740 312" fill="none" stroke="white" stroke-width="7"/><path d="M1605 430L1740 312" fill="none" stroke="#c84328" stroke-width="3"/>
 <rect x="1710" y="236" width="390" height="92" rx="5" fill="white" stroke="#c84328" stroke-width="2"/>
 <text x="1730" y="273" font-family="sans-serif" font-size="29" font-weight="700" fill="#a52f1b">上方描圖重點視窗</text><text x="1730" y="309" font-family="sans-serif" font-size="23" fill="#714034">West Farms · 概略位置</text>
 <path d="M1697 716L1760 758" fill="none" stroke="white" stroke-width="7"/><path d="M1697 716L1760 758" fill="none" stroke="#126b95" stroke-width="3"/>
 <rect x="1740" y="749" width="280" height="48" rx="4" fill="white" stroke="#126b95" stroke-width="2"/><text x="1757" y="782" font-family="sans-serif" font-size="26" fill="#126b95">完整航照範圍</text>
 </svg>'''
 (ROOT/'historical/crossbronx_official_locator.svg').write_text(svg)
 for c in cases:
  c['officialOverlay']=svg if c['id']=='crossbronx' else ''
  if c['id']=='crossbronx':c['official_note']='Reimagine the Cross Bronx Final Vision，Figure 4.20。紅色實線框對應上方描圖重點視窗，藍色虛線框對應完整航照範圍；依道路與河流交會位置概略定位，框線不是精確測繪邊界。綠色官方圖形才是潛在加蓋位置，請勿與本頁索引框混淆。'
