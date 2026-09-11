from PIL import Image, ImageDraw, ImageFont
from pathlib import Path
ROOT=Path(__file__).resolve().parent;OUT=ROOT/'output'
FONT='/System/Library/Fonts/STHeiti Medium.ttc'
REG='/System/Library/Fonts/STHeiti Light.ttc'
BG='#F5F3ED';INK='#243D42';MUTED='#667575'
def font(n,b=False):return ImageFont.truetype(FONT if b else REG,n)
def text(im,xy,s,n=30,c=INK,b=False):ImageDraw.Draw(im).text(xy,s,font=font(n,b),fill=c)
CASES=[
 ('nihonbashi','01','日本橋','NIHONBASHI / TOKYO','高架退場，河川重新成為城市主角',
  'BEFORE  /  高架跨河','AFTER  /  地下化後的空間示意',
  '深灰高架沿日本橋川穿越街區，遮蔽河面與橋上視野。',
  '移除地上高架，補上兩岸步道；藍色量體沿用原檔再開發設定。',
  '地下隧道位於地表下，本圖不以水面上的道路呈現。'),
 ('crossbronx','02','Cross-Bronx','WEST FARMS / NEW YORK','公路仍然運作，綠地跨越道路阻隔',
  'BEFORE  /  路塹與跨河高架','AFTER  /  加蓋公園概念願景',
  '深灰公路切開街區；跨河高架與兩岸既有公園保留。',
  '在原檔指定區間加蓋公園，下面仍是公路，重新連接兩側空間。',
  '加蓋範圍為概念示意，非官方定案；不代表全線拆除。'),
 ('westside','03','West Side Highway','HUDSON RIVER / NEW YORK','從高架邊界，走向可親近的水岸',
  'BEFORE  /  高架與舊碼頭','AFTER  /  平面大道與水岸公園',
  '高架沿水岸形成連續邊界，舊碼頭以褐色量體標示。',
  '以 Route 9A 平面大道、連續綠帶與兩處公園碼頭呈現轉型。',
  '歷史與改造情境比較，非單一年度實景；碼頭造形為量體示意。')]
for key,num,title,en,idea,bef,aft,bc,ac,note in CASES:
    im=Image.new('RGB',(3000,1790),BG);dr=ImageDraw.Draw(im)
    text(im,(90,60),'URBAN INFRASTRUCTURE  /  SPATIAL TRANSFORMATION',24,MUTED)
    text(im,(90,115),title,72,b=True);text(im,(92,207),en,25,MUTED)
    text(im,(1930,125),idea,34,b=True);text(im,(2850,60),num,60,'#ABB7B0')
    dr.line((90,270,2910,270),fill='#CCD2CA',width=2)
    for j,(state,tag,cap) in enumerate([('before',bef,bc),('after',aft,ac)]):
        x=90+j*1490
        text(im,(x,305),tag,32,'#43565A' if j==0 else '#3F785E',True)
        pic=Image.open(OUT/f'{key}_{state}.png').convert('RGBA')
        pic.thumbnail((1420,1105),Image.Resampling.LANCZOS)
        im.paste(pic,(x,365),pic)
        text(im,(x,1490),cap,29,b=True)
    dr.line((1500,365,1500,1460),fill='#D8DDD4',width=2)
    text(im,(90,1565),note,28,MUTED)
    colors=[('#DDDCD4','背景街廓'),('#D4A55C','地標'),('#505A60','公路'),('#72ABBC','河川'),('#78A177','綠地'),('#598D9C','再開發')]
    for i,(c,label) in enumerate(colors):
        x=90+i*245;dr.rectangle((x,1640,x+25,1665),fill=c);text(im,(x+38,1635),label,24,MUTED)
    text(im,(90,1720),'依原始程式座標重建・前後固定視角與比例・垂直高度統一放大 2 倍・非實測或工程圖',23,MUTED)
    text(im,(2390,1720),'CODEX  /  3D STUDY  /  '+num,23,MUTED)
    im.save(OUT/f'{key}_comparison.png')
# Compact overview retains all six images with readable city/state labels.
overview=Image.new('RGB',(2400,3040),BG)
text(overview,(75,55),'高速公路之後，城市如何重新連接？',59,b=True)
text(overview,(78,139),'三個案例・六個場景  /  3D 量體前後對照',30,MUTED)
for i,(key,num,title,en,idea,bef,aft,bc,ac,note) in enumerate(CASES):
    y=230+i*900
    text(overview,(75,y),num+'  '+title,42,b=True)
    text(overview,(1400,y+7),idea,28,MUTED)
    for j,(state,label) in enumerate([('before','BEFORE'),('after','AFTER / 概念願景' if key=='crossbronx' else 'AFTER')]):
        x=60+j*1190;text(overview,(x+25,y+75),label,25,'#3F785E' if j else MUTED,True)
        pic=Image.open(OUT/f'{key}_{state}.png').convert('RGBA');pic.thumbnail((1150,750),Image.Resampling.LANCZOS)
        overview.paste(pic,(x+(1150-pic.width)//2,y+100),pic)
    ImageDraw.Draw(overview).line((75,y+870,2325,y+870),fill='#D0D6CE',width=2)
text(overview,(75,2960),'原始資料重建 / 相同鏡頭比較 / 高度 ×2 / 示意量體，非實測成果',26,MUTED)
overview.save(OUT/'overview.png')
print('Created three presentation boards and overview')
