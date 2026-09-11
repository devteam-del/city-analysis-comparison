"""Restore embedded delivery-resolution images for editing/rebuilding the single HTML."""
from pathlib import Path
import re,json,base64,io
from PIL import Image
ROOT=Path(__file__).resolve().parent
raw=(ROOT/'urban-history-comparison.html').read_text()
data=json.loads(re.search(r'<script id="case-data" type="application/json">(.*?)</script>',raw,re.S).group(1))
(ROOT/'actual-data').mkdir(exist_ok=True)
(ROOT/'dist').mkdir(exist_ok=True)
for c in data:
    for field,suffix in [('aerial','historic.png'),('current','linework.png'),('recent','2024.png'),('official_img','official_plan_crop.png')]:
        if not c.get(field):continue
        if field=='recent' and c['id']=='nihonbashi':suffix='2019.png'
        path=ROOT/'actual-data'/f'{c["id"]}_{suffix}'
        if path.exists():
            print('Preserved existing',path.name)
            continue
        Image.open(io.BytesIO(base64.b64decode(c[field].split(',',1)[1]))).save(path)
        print('Restored',path.name)
