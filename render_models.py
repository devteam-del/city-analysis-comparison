import bpy, json, math, random, os
from mathutils import Vector

ROOT=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(ROOT,'output'); os.makedirs(OUT,exist_ok=True)
DATA=json.load(open(os.path.join(ROOT,'source/cities.json')))
Z=2.0  # consistent vertical exaggeration; source units are schematic
COLORS={'ground':'E6E4DB','lot':'DDDCD4','landmark':'D4A55C','water':'72ABBC','road':'505A60','wall':'939B99','path':'DDD0AF','green':'78A177','tree':'427961','new':'598D9C','old':'AD9E86','tunnel':'9279B6','white':'E6E4D5'}
MATS={}
for k,h in COLORS.items():
    m=bpy.data.materials.new(k); m.diffuse_color=tuple(int(h[i:i+2],16)/255 for i in (0,2,4))+(1,)
    m.use_nodes=True;bsdf=m.node_tree.nodes.get('Principled BSDF')
    bsdf.inputs['Base Color'].default_value=tuple(v/12.92 if v<=.04045 else ((v+.055)/1.055)**2.4 for v in m.diffuse_color[:3])+(1,)
    bsdf.inputs['Roughness'].default_value=.85;MATS[k]=m

def poly(name,pts,h,mat,z=0):
    n=len(pts); verts=[(x,y,z*Z) for x,y in pts]+[(x,y,(z+h)*Z) for x,y in pts]
    faces=[tuple(range(n-1,-1,-1)),tuple(range(n,n*2))]+[(i,(i+1)%n,(i+1)%n+n,i+n) for i in range(n)]
    mesh=bpy.data.meshes.new(name); mesh.from_pydata(verts,[],faces); mesh.update()
    o=bpy.data.objects.new(name,mesh); bpy.context.scene.collection.objects.link(o); o.data.materials.append(MATS[mat]); return o
def rect(name,x,y,w,d,h,mat,z=0): return poly(name,[(x,y),(x+w,y),(x+w,y+d),(x,y+d)],h,mat,z)
def band(pts,width,vertical):
    a=[(x-width if vertical else x,y if vertical else y-width) for x,y in pts]
    b=[(x+width if vertical else x,y if vertical else y+width) for x,y in reversed(pts)]
    return a+b
def ribbon(name,pts,width,h,mat,z=0,vertical=True): return poly(name,band(pts,width,vertical),h,mat,z)
def cyl(name,x,y,r,h,mat,z=0,r2=None):
    bpy.ops.mesh.primitive_cone_add(vertices=12,radius1=r,radius2=r if r2 is None else r2,depth=h*Z,location=(x,y,(z+h/2)*Z))
    o=bpy.context.object; o.name=name; o.data.materials.append(MATS[mat]); return o
def tree(x,y,z=0):
    cyl('Tree trunk',x,y,1.1,4,'old',z)
    bpy.ops.mesh.primitive_ico_sphere_add(subdivisions=1,radius=1,location=(x,y,(z+8)*Z))
    o=bpy.context.object; o.name='Tree canopy'; o.scale=(5,5,6*Z);o.data.materials.append(MATS['tree'])
def lerp(pts,v,axis=1):
    for a,b in zip(pts,pts[1:]):
        if a[axis]<=v<=b[axis]:
            t=(v-a[axis])/(b[axis]-a[axis] or 1);return a[1-axis]+(b[1-axis]-a[1-axis])*t
    return pts[0][1-axis] if v<pts[0][axis] else pts[-1][1-axis]
def clipped(pts,lo,hi,axis=1):
    def p(v):return [lerp(pts,v,1),v] if axis==1 else [v,lerp(pts,v,0)]
    return [p(lo)]+[a for a in pts if lo<a[axis]<hi]+[p(hi)]
def intersects(b,r,pad=5):
    return b['x']<r['x']+r['w']+pad and b['x']+b['w']>r['x']-pad and b['y']<r['y']+r['h']+pad and b['y']+b['h']>r['y']-pad
def inside(x,y,pts):
    ok=False
    for a,b in zip(pts,pts[1:]+pts[:1]):
        if (a[1]>y)!=(b[1]>y) and x<(b[0]-a[0])*(y-a[1])/(b[1]-a[1])+a[0]:ok=not ok
    return ok
def allow(b,d,key):
    if b['x']<0 or b['y']<0 or b['x']+b['w']>d['w'] or b['y']+b['h']>d['d']:return False
    for r in d.get('landmarks',[])+d.get('redev',[])+d.get('park',[]):
        if intersects(b,r):return False
    hw=d['highway']
    for i in range(5):
        for j in range(5):
            x=b['x']+b['w']*i/4;y=b['y']+b['h']*j/4
            if inside(x,y,d['river']):return False
            if hw['vertical']:
                if abs(x-lerp(hw['center'],y))<hw['halfW']+24:return False
            elif abs(y-lerp(hw['center'],x,0))<hw['halfW']+15:return False
            if key=='nihonbashi' and abs(x-lerp(hw['center'],y))<52:return False
            if key=='westside' and x<272:return False
    return True
def road(name,pts,width,z,vertical=True):
    ribbon(name,pts,width,1.5,'road',z,vertical)
    for s in (-1,1):
        p=[(x+s*(width-1.4) if vertical else x,y if vertical else y+s*(width-1.4)) for x,y in pts]
        ribbon('Road parapet',p,.7,1.3,'wall',z+1.5,vertical)
    axis=1 if vertical else 0
    for v in range(math.ceil(pts[0][axis])+5,math.floor(pts[-1][axis])-8,25):
        seg=clipped(pts,v,v+10,axis)
        ribbon('Lane marking',seg,.55,.05,'white',z+1.53,vertical)
def build(key,state):
    d=DATA[key]; scene=bpy.data.scenes.new(key+'_'+state);bpy.context.window.scene=scene
    rect('Model base',-25,-25,d['w']+50,d['d']+50,7,'ground',-7)
    poly('River',d['river'],.65,'water',.1)
    for b in d['buildings']:
        if allow(b,d,key):rect('Context block',b['x'],b['y'],b['w'],b['h'],b['height'],'lot')
    for b in d.get('landmarks',[]):rect(b['name'],b['x'],b['y'],b['w'],b['h'],b['height'],'landmark')
    for b in d.get('redev',[]):rect(b['name'],b['x'],b['y'],b['w'],b['h'],b[state],'new' if state=='after' else 'old')
    rng=random.Random(35)
    for p in d.get('park',[]):
        ranges=[(p['y'],p['y']+p['h'])]
        if key=='crossbronx':
            mid=lerp(d['highway']['center'],p['x']+p['w']/2,0)
            ranges=[(p['y'],min(p['y']+p['h'],mid-27)),(max(p['y'],mid+27),p['y']+p['h'])]
        for lo,hi in ranges:
            if hi>lo:rect(p['name'],p['x'],lo,p['w'],hi-lo,1,'green')
        for i in range(18):
            tx=p['x']+10+rng.random()*(p['w']-20);ty=p['y']+10+rng.random()*(p['h']-20)
            if key!='crossbronx' or abs(ty-lerp(d['highway']['center'],tx,0))>33:tree(tx,ty,1)
    hw=d['highway']; c=hw['center']; vertical=hw['vertical']
    if key=='crossbronx':
        a=clipped(c,0,560,0);e=clipped(c,560,1300,0)
        road('Retained trench carriageway',a,22,.5,False);road('Retained viaduct',e,22,11,False)
        for x in range(580,1280,90):cyl('Viaduct pier',x,lerp(c,x,0),3,11,'wall')
        rect('Existing pedestrian bridge',600,225,55,22,3,'path')
        if state=='after':
            cp=clipped(c,340,560,0)
            ribbon('Conceptual park cap',cp,30,2,'green',5,False)
            ribbon('Cap walking route',cp,3,.15,'path',7.1,False)
            for x in range(352,560,24):
                for side in (-1,1):tree(x,lerp(c,x,0)+side*20,7)
    elif state=='before':
        road('Elevated expressway',c,hw['halfW'],11)
        for y in range(40,d['d'],90):
            x=lerp(c,y);cyl('Bridge pier',x,y,2.8,11,'wall');rect('Pier head',x-hw['halfW']+1,y-2,hw['halfW']*2-2,4,1.5,'wall',9)
    if key=='nihonbashi':
        # Added schematic local bridge for legibility, matching the river corridor.
        x=lerp(c,560);rect('Nihonbashi bridge (schematic)',x-52,549,104,22,2,'landmark',2)
        if state=='after':
            for side in (-1,1):
                pts=[(lerp(c,y)+side*37,y) for y in range(150,1101,25)]
                ribbon('River promenade',pts,9,.8,'path',.6)
                for y in range(175,1080,38):tree(lerp(c,y)+side*42,y,1.4)
            # Tunnel intentionally omitted from surface; documented with a separate graphic key.
    if key=='westside':
        bank=d['riverwalkBank']
        for p in d['piers']:
            y0,y1=p['yr'];mid=(y0+y1)/2;bx=lerp(bank,mid)-70
            if state=='before':rect(p['nameBefore'],bx,y0,74,y1-y0,p['before'],'old')
            elif p['little']:
                for i in range(3):
                    xx=bx-25+i*22;yy=mid-40+i*38
                    cyl('Little Island planted platform',xx,yy,26-i*3,2,'green',7+i*2)
                    cyl('Little Island pedestal',xx,yy,5,7+i*2,'path',0,20-i*2)
                    tree(xx,yy,9+i*2)
                rect('Little Island access',bx+10,mid,64,10,2,'path',4)
            else:
                rect('Gansevoort park',bx-25,y0,99,y1-y0,3,'green')
                for i in range(12):tree(bx-15+rng.random()*75,y0+10+rng.random()*(y1-y0-20),3)
        if state=='after':
            road('Route 9A surface boulevard',c,20,.3)
            pts=[(lerp(bank,y)+13,y) for y in range(0,1301,25)]
            ribbon('Hudson River Park greenway',pts,13,1,'green',.3)
            ribbon('Waterfront walking and cycling path',pts,3,.1,'path',1.4)
            for y in range(25,1280,35):tree(lerp(bank,y)+22,y,1.3)
    # Same orthographic camera and scale within each before/after pair.
    bpy.ops.object.camera_add(location=(d['w']/2+1150,d['d']/2-1550,1600))
    camera=bpy.context.object;camera.name='Comparison camera';target=Vector((d['w']/2,d['d']/2,35))
    camera.rotation_euler=(target-camera.location).to_track_quat('-Z','Y').to_euler();camera.data.type='ORTHO';camera.data.ortho_scale=1760;camera.data.clip_end=10000;scene.camera=camera
    scene.render.engine='CYCLES';scene.cycles.samples=24;scene.cycles.use_denoising=True
    bpy.ops.object.light_add(type='AREA',location=(d['w']/2-600,d['d']/2-800,1800))
    light=bpy.context.object;light.data.energy=12000000;light.data.shape='DISK';light.data.size=1000
    light.rotation_euler=(Vector((d['w']/2,d['d']/2,0))-light.location).to_track_quat('-Z','Y').to_euler()
    sh=scene.display.shading;sh.light='STUDIO';sh.studiolight_rotate_z=.4;sh.color_type='MATERIAL';sh.show_shadows=True;sh.show_cavity=True;sh.cavity_type='BOTH';sh.curvature_ridge_factor=1.25;sh.curvature_valley_factor=1.05
    sh.show_specular_highlight=False;sh.background_type='WORLD';sh.show_object_outline=False
    scene.world=bpy.data.worlds.new(key+state+'World');scene.world.use_nodes=True;scene.world.node_tree.nodes['Background'].inputs['Color'].default_value=(.94,.94,.92,1);scene.world.node_tree.nodes['Background'].inputs['Strength'].default_value=.7
    scene.view_settings.view_transform='Standard';scene.render.film_transparent=True
    scene.render.resolution_x=1800;scene.render.resolution_y=1400;scene.render.resolution_percentage=100
    scene.render.image_settings.file_format='PNG';scene.render.image_settings.color_mode='RGBA'
    scene.render.filepath=os.path.join(OUT,key+'_'+state+'.png')
    return scene

for s in list(bpy.data.scenes):
    if len(bpy.data.scenes)>1:bpy.data.scenes.remove(s)
for key in DATA:
    for state in ['before','after']:
        scene=build(key,state)
        bpy.ops.render.render(write_still=True)
bpy.ops.wm.save_as_mainfile(filepath=os.path.join(OUT,'expressway_comparisons.blend'))
print('COMPLETE: six comparison scenes rendered and saved')
