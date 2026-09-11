from pathlib import Path
import sys,json,math,io,concurrent.futures
ROOT=Path(__file__).resolve().parent;sys.path.insert(0,str(ROOT/'.geo-libs'))
import requests
from PIL import Image
d=json.loads((ROOT/'actual-data/areas.json').read_text())['nihonbashi'];z=18;circ=40075016.68557849;s=256*2**z/circ
w,b,e,n=d['merc_bounds'];px0=(w+circ/2)*s;py0=(circ/2-n)*s;px1=(e+circ/2)*s;py1=(circ/2-b)*s
x0=int(px0//256);y0=int(py0//256);x1=int(px1//256);y1=int(py1//256)
im=Image.new('RGB',((x1-x0+1)*256,(y1-y0+1)*256),'white')
def tile(t):
 x,y=t;p=ROOT/f'actual-data/tiles/nihonbashi_2019_{z}_{x}_{y}.png'
 if not p.exists():
  r=requests.get(f'https://cyberjapandata.gsi.go.jp/xyz/nendophoto2019/{z}/{x}/{y}.png',timeout=30);r.raise_for_status();p.write_bytes(r.content)
 return x,y,Image.open(p).convert('RGB')
with concurrent.futures.ThreadPoolExecutor(6) as ex:
 for x,y,i in ex.map(tile,[(x,y) for x in range(x0,x1+1) for y in range(y0,y1+1)]):im.paste(i,((x-x0)*256,(y-y0)*256))
im.crop((round(px0-x0*256),round(py0-y0*256),round(px1-x0*256),round(py1-y0*256))).save(ROOT/'actual-data/nihonbashi_2019.png')
print('Saved GSI 2019 fiscal-year aerial; this is a dated reference, not 2026 imagery.')
