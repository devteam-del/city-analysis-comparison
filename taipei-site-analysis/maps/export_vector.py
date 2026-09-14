from pathlib import Path
import xml.etree.ElementTree as ET
import numpy as np,base64,io
from PIL import Image
b=Path('taipei-site-analysis/maps');ns='http://www.w3.org/2000/svg';ET.register_namespace('',ns)
root=ET.parse(b/'activity-map.svg').getroot();group=root.find(f'.//{{{ns}}}g[@id="surface-road-sides"]');img=group.find(f'{{{ns}}}image');url=img.attrib['href'];im=Image.open(io.BytesIO(base64.b64decode(url.split(',',1)[1]))).convert('RGBA');mask=np.asarray(im)[:,:,3]>127
# Exact occupied runs, merged vertically: lossless vector representation of the existing edge mask.
active={};rects=[]
for y,row in enumerate(mask):
 change=np.diff(np.r_[False,row,False].astype(np.int8));runs=set(zip(np.where(change==1)[0].tolist(),np.where(change==-1)[0].tolist()))
 for key,start in list(active.items()):
  if key not in runs:rects.append((key[0],start,key[1],y));del active[key]
 for key in runs:
  if key not in active:active[key]=y
for key,start in active.items():rects.append((key[0],start,key[1],mask.shape[0]))
sx=float(img.attrib['width'])/im.width;sy=float(img.attrib['height'])/im.height
path=' '.join(f'M{x1*sx:g},{y1*sy:g}h{(x2-x1)*sx:g}v{(y2-y1)*sy:g}h{-(x2-x1)*sx:g}Z' for x1,y1,x2,y2 in rects)
group.remove(img);ET.SubElement(group,f'{{{ns}}}path',{'d':path,'fill':'#ffffff','stroke':'none','data-origin':'lossless vectorization of reconstructed road-side mask; not measured curbs'})
root.insert(0,ET.Element(f'{{{ns}}}desc'));root[0].text='A3 420 x 297 mm, scale 1:5000 at 100% print. Fully vector shapes and editable text. Roads reconstructed from historical width data; vector conversion does not improve spatial accuracy.'
out=b/'activity-map-vector.svg';ET.ElementTree(root).write(out,encoding='utf-8',xml_declaration=True)
assert not root.findall(f'.//{{{ns}}}image');assert root.findall(f'.//{{{ns}}}text');print(out,'vector rectangles',len(rects),'bytes',out.stat().st_size)
