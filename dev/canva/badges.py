# Game Center の 実績の バッジ（11/26）：docs/kobo/achievements/<id>.png（1024×1024・RGB・透明なし・文字なし）
#   今ある Canva の 絵（A：台の 景色・おばけ・タワー・玉）と 光の すじ（fxrays.py の C）を、コードで 描いた ネオンの メダル（C）に のせる。Canva の 新しい 生成は 0
#   ネタバレ：隠さない 実績には、雪山までの 台・おばけ・玉だけを 使う（火山・天国は 隠し実績だけ）
# 使い方: python3 dev/canva/badges.py [id ...]   → docs/kobo/achievements/（SHEET=パス で ならべた 見本の 1まいも）
import os, sys, math, json
from PIL import Image, ImageDraw, ImageFilter, ImageChops
HERE=os.path.dirname(os.path.abspath(__file__)); ROOT=os.path.join(HERE,'..','..')
OUT=os.path.join(ROOT,'docs','kobo','achievements'); os.makedirs(OUT,exist_ok=True)
S=1024; SS=2   # 線は 2倍で 描いて ちぢめる（ふちを なめらかに）
CX=CY=S//2

def load(p): return Image.open(os.path.join(HERE,p)).convert('RGBA')
BG={k:f'bg/{v}_full.png' for k,v in dict(meadow='grass',forest='forest',mansion='mansion',desert='desert',snow='snow',volcano='volcano',heaven='heaven').items()}

def ball(k):
    # 玉の もと（200×200・こい 紺の 背景つき RGB）→ 明るさで すかす（紺の 背景だけ 消えて、光の ふちは のこる）
    im=Image.open(os.path.join(HERE,'balls','src',k+'.png')).convert('RGB')
    a=Image.eval(im.convert('L'),lambda v:max(0,min(255,int((v-28)*255/70))))
    r=im.convert('RGBA'); r.putalpha(a); return r
def ghost(k): return load(f'ghosts/{k}_full.png')
def tower(head='basic'):
    # 台座（上から 見た 丸）＋ 頭（右むき）を 上むきに。ゲームと おなじ 組み方
    base=load('towers/base_full.png'); hd=load(f'towers/{head}_full.png').rotate(90,resample=Image.BICUBIC,expand=False)
    c=Image.new('RGBA',(200,200)); c.alpha_composite(base); c.alpha_composite(hd,(0,-18)); return c
def rays(): return load('fx/rays.png')

def scene(board):
    im=Image.open(os.path.join(HERE,BG[board])).convert('RGB'); w,h=im.size
    top=int(h*.2); im=im.crop((0,top,w,top+w)).resize((S,S),Image.LANCZOS)
    im=Image.eval(im,lambda v:int(v*.62))
    # まわりを 暗く（ビネット）
    m=Image.new('L',(S,S),0); ImageDraw.Draw(m).ellipse((-90,-90,S+90,S+90),fill=255)
    m=m.filter(ImageFilter.GaussianBlur(150))
    return Image.composite(im,Image.new('RGB',(S,S),(6,4,20)),m).convert('RGBA')

def hexrgb(h): h=h.lstrip('#'); return tuple(int(h[i:i+2],16) for i in (0,2,4))
def ringcol(col,ang):
    if col=='rainbow': return hsv(ang/360)
    if isinstance(col,tuple): # 2色の グラデーション
        t=(math.cos(math.radians(ang-135))+1)/2; a,b=hexrgb(col[0]),hexrgb(col[1]); return tuple(int(a[i]*t+b[i]*(1-t)) for i in range(3))
    return hexrgb(col)
def hsv(h):
    import colorsys; r,g,b=colorsys.hsv_to_rgb(h%1,.75,1); return (int(r*255),int(g*255),int(b*255))
def maincol(col): return ringcol(col,135) if col!='rainbow' else (255,255,255)

def arcs(d,r,w,col,n=180):
    # 色が 角度で かわる 輪（n こに 分けて 描く）
    for i in range(n):
        a0,a1=i*360/n,(i+1)*360/n+.8
        d.arc((CX*SS-r*SS,CY*SS-r*SS,CX*SS+r*SS,CY*SS+r*SS),a0,a1,fill=ringcol(col,a0)+(255,),width=int(w*SS))

def medal(bg,col,pts):
    lay=Image.new('RGBA',(S*SS,S*SS)); d=ImageDraw.Draw(lay)
    W={10:20,25:24,50:28,100:32}[pts]
    arcs(d,440,W,col)
    if pts>=25: arcs(d,402,6,col)
    if pts>=50:
        for i in range(24):
            a=math.radians(i*15); x,y=CX+478*math.cos(a),CY+478*math.sin(a); c=ringcol(col,i*15)
            d.ellipse(((x-7)*SS,(y-7)*SS,(x+7)*SS,(y+7)*SS),fill=c+(255,))
    if pts>=100: arcs(d,498,8,'#ffe27a')
    lay=lay.resize((S,S),Image.LANCZOS)
    # 中の 円を 少し 暗く・色を うすく
    inner=Image.new('L',(S,S),0); ImageDraw.Draw(inner).ellipse((CX-430,CY-430,CX+430,CY+430),fill=110)
    tint=Image.new('RGBA',(S,S),(4,2,16,255)); bg.paste(Image.blend(bg,tint,.5),(0,0),inner.filter(ImageFilter.GaussianBlur(6)))
    glow=lay.filter(ImageFilter.GaussianBlur(22)); bg=Image.alpha_composite(bg,glow); bg=Image.alpha_composite(bg,glow)
    return Image.alpha_composite(bg,lay)

def put(bg,im,cx,cy,size,glowcol=None,rot=0):
    im=im.copy()
    if rot: im=im.rotate(rot,resample=Image.BICUBIC,expand=True)
    bb=im.getbbox(); im=im.crop(bb); k=size/max(im.size); im=im.resize((max(1,int(im.width*k)),max(1,int(im.height*k))),Image.LANCZOS)
    x,y=int(cx-im.width/2),int(cy-im.height/2)
    if glowcol:
        g=Image.new('RGBA',im.size,glowcol+(0,)); g.putalpha(im.getchannel('A').point(lambda v:int(v*.85)))
        pad=Image.new('RGBA',(im.width+120,im.height+120)); pad.alpha_composite(g,(60,60)); pad=pad.filter(ImageFilter.GaussianBlur(26))
        bg.alpha_composite(pad,(x-60,y-60))
    bg.alpha_composite(im,(x,y)); return bg
def put_rays(bg,size=980,alpha=.9,cy=CY):
    r=rays().resize((size,size),Image.LANCZOS)
    if alpha<1: r.putalpha(r.getchannel('A').point(lambda v:int(v*alpha)))
    bg.alpha_composite(r,(CX-size//2,cy-size//2)); return bg

EARLY=['normal','fire','ice','bolt','poison','lead','heal','bb','water','vine','sound','shadow','sand','wind','snow','crystal']   # 雪山までの 玉（ネタバレしない）
def ring_of(bg,keys,R,size,start=-90,fn=ball):
    for i,k in enumerate(keys):
        a=math.radians(start+i*360/len(keys)); put(bg,fn(k),CX+R*math.cos(a),CY+R*math.sin(a),size)
    return bg

# id → (台の 景色, 輪の 色, 点, 中の 絵)
B={
 'first_tower':  ('meadow','#7dff9a',10, lambda b,c: put(b,tower(),CX,CY+10,560,c)),
 'first_fever':  ('meadow','rainbow',10, lambda b,c: put(put_rays(b),ball('normal'),CX,CY,470,(255,240,200))),
 'first_combo':  ('forest',('#ff8a3d','#6ce8ff'),10, lambda b,c: put(put(put_rays(b,900,.8),ball('fire'),CX-120,CY-110,380,(255,140,60)),ball('ice'),CX+120,CY+110,380,(110,230,255))),
 'clear_meadow': ('meadow','#a6ff6a',25, lambda b,c: put(b,ghost('uma'),CX,CY+6,640,c)),
 'tower_max':    ('desert','#ffd34a',25, lambda b,c: lvdots(put(put_rays(b,860,.7,CY-30),tower(),CX,CY-40,500,c))),
 'full_pegs':    ('forest','#6cf0ff',25, lambda b,c: put(ring_of(b,range(12),318,178,fn=lambda i:tower().rotate(-(i*30),resample=Image.BICUBIC,expand=True)),ball('normal'),CX,CY,200,(255,240,200))),
 'kills_1000':   ('meadow','#ff8ad8',25, lambda b,c: put(put(put(b,ghost('wata'),CX-170,CY-60,400,c),ghost('kakashi'),CX+170,CY-60,400,c),ghost('usagi'),CX,CY+90,460,c)),
 'clear_mansion':('mansion','#c08aff',25, lambda b,c: put(b,ghost('ookami'),CX,CY+6,640,c)),
 'found_30':     ('desert','#6ce8ff',25, lambda b,c: ring_of(put_rays(b,760,.7),['fire','ice','bolt'],170,330,start=-90)),
 'no_damage':    ('snow','#7dffb0',50, lambda b,c: put(put_rays(b,900,.6),ball('heal'),CX,CY,520,c)),
 'clear_snow':   ('snow','#a8e6ff',50, lambda b,c: put(b,ghost('mammoth'),CX,CY+6,660,c)),
 'found_100':    ('mansion','#d6c8ff',50, lambda b,c: put(ring_of(put_rays(b,820,.7),['fire','ice','bolt','poison','water','vine'],230,240),ball('normal'),CX,CY,220,(255,240,200))),
 'clear_volcano':('volcano','#ff6a3d',50, lambda b,c: put(b,ghost('dragon'),CX,CY+6,660,c)),
 'clear_heaven': ('heaven','#fff0a8',100,lambda b,c: put(put_rays(b,1000,1),ghost('ousama'),CX,CY+10,640,c)),
 'found_all':    ('snow','#ffd34a',100,lambda b,c: put(ring_of(put_rays(b,1000,1),EARLY,330,120),ball('crystal'),CX,CY,260,(255,240,200))),
}
def lvdots(bg):   # レベルの 点 4つ（ゲームの 砲台の 下の 点と おなじ）
    d=ImageDraw.Draw(bg)
    for i in range(4):
        x=CX+(i-1.5)*74; y=CY+250; d.ellipse((x-22,y-22,x+22,y+22),fill=(255,214,74,255),outline=(255,250,220,255),width=4)
    return bg

def make(id):
    board,col,pts,draw=B[id]
    g=gcj[id]; assert g['points']==pts,(id,g['points'],pts)
    bg=medal(scene(board),col,pts)
    bg=draw(bg,maincol(col))
    out=bg.convert('RGB'); out.save(os.path.join(OUT,f'pachi_{id}.png'),dpi=(72,72),optimize=True); return out

gcj={a['id'][6:]:a for a in json.load(open(os.path.join(ROOT,'docs','kobo','gamecenter.json'),encoding='utf-8'))['achievements']}
ids=sys.argv[1:] or list(gcj)
assert set(B)==set(gcj),(set(B)^set(gcj))
outs=[make(i) for i in ids]
# 見本：ならべた 1まい（小さく）
T=256; cols=5; sheet=Image.new('RGB',(T*cols,T*math.ceil(len(outs)/cols)),(20,20,30))
for i,o in enumerate(outs): sheet.paste(o.resize((T,T),Image.LANCZOS),((i%cols)*T,(i//cols)*T))
SHEET=os.environ.get('SHEET')   # 見本の 1まいは リポジトリに 入れない（SHEET=/どこか/sheet.png で 書く）
if SHEET: sheet.save(SHEET)
print('ok',len(outs))
