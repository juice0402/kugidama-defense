# いろいろな 画面の 大きさで ぜんぶの 場面を 撮って、はみ出し・字の 切れ・ボタンの 重なり・小さすぎる ボタンを 自動で さがす（11/9）
# 使い方: python3 mk.py && python3 devsweep.py [出す フォルダ=_sweep] [機種の 名前,...]
#   機種ごとに 1まいの 一覧（_sweep/<機種>.png）と、見つけた ものの 一覧（_sweep/report.txt）
import asyncio, sys, os, json
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
HERE=os.path.dirname(os.path.abspath(__file__))
OUT=os.path.join(HERE,sys.argv[1] if len(sys.argv)>1 else '_sweep')
DEV={  # 名前: (はば, 高さ, 細かさ)
 'iPhoneSE':(375,667,2), 'iPhone15':(393,852,3), 'iPhoneProMax':(430,932,3), 'iPhoneSafari':(390,664,3),
 'mini320':(320,568,2), 'Android':(360,800,3), 'iPadPortrait':(820,1180,2), 'iPadLandscape':(1180,820,2),
 'iPadSplit':(590,820,2), 'iPadMini':(744,1133,2), 'iPadPro13':(1032,1376,2), 'iPadPro13Land':(1376,1032,2), 'phoneLandscape':(852,393,3), 'PC':(1440,900,1),
}
ONLY=sys.argv[2].split(',') if len(sys.argv)>2 else list(DEV)
CHECK=r"""(name)=>{const W=innerWidth,H=innerHeight,out=[];
 const vis=e=>e.checkVisibility?e.checkVisibility({opacityProperty:true,visibilityProperty:true}):!!e.getClientRects().length;
 const scroller=e=>{for(let a=e.parentElement;a;a=a.parentElement){const s=getComputedStyle(a);if(/(auto|scroll)/.test(s.overflowY+s.overflowX))return a}return null};
 const lab=e=>(e.id?'#'+e.id:'')+(e.className&&typeof e.className==='string'?'.'+e.className.trim().split(/\s+/).slice(0,2).join('.'):'')+' 「'+(e.textContent||e.getAttribute('aria-label')||'').trim().slice(0,14)+'」';
 const de=document.documentElement; if(de.scrollWidth>W+1||de.scrollHeight>H+1) out.push(`ページが スクロールする ${de.scrollWidth}x${de.scrollHeight}`);
 const btns=[];
 for(const e of document.querySelectorAll('body *')){
   if(!vis(e)) continue; const r=e.getBoundingClientRect(); if(r.width<1||r.height<1) continue;
   const txt=[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim());
   const sc=scroller(e);
   if(txt||e.tagName==='BUTTON'||e.tagName==='IMG'){
     const R=sc?sc.getBoundingClientRect():{left:0,top:0,right:W,bottom:H};
     const L=Math.max(R.left,0),T=Math.max(R.top,0),Rr=Math.min(R.right,W),B=Math.min(R.bottom,H);
     // スクロールの 中で 見えない所は ふつう。画面の 外に はみ出して 半分だけ 見えるのは あやしい
     const ox=Math.max(0,L-r.left)+Math.max(0,r.right-Rr), oy=Math.max(0,T-r.top)+Math.max(0,r.bottom-B);
     const inside=r.right>L+2&&r.left<Rr-2&&r.bottom>T+2&&r.top<B-2;
     if(inside&&(ox>3||(!sc&&oy>3))) out.push(`はみ出し ${lab(e)} ${Math.round(ox)}x${Math.round(oy)}px`);
   }
   if(txt){const s=getComputedStyle(e);
     if((s.overflow!=='visible'||s.textOverflow==='ellipsis')&&(e.scrollWidth>e.clientWidth+2||e.scrollHeight>e.clientHeight+3)&&s.whiteSpace!=='normal'||(s.textOverflow==='ellipsis'&&e.scrollWidth>e.clientWidth+1))
       out.push(`字が 切れる ${lab(e)} ${e.scrollWidth}>${e.clientWidth}`)}
   if((e.tagName==='BUTTON'||e.getAttribute('role')==='button')&&getComputedStyle(e).pointerEvents!=='none'){
     const sc2=scroller(e); if(sc2){const R=sc2.getBoundingClientRect();if(r.bottom<R.top||r.top>R.bottom)continue}
     if(r.right<0||r.left>W||r.bottom<0||r.top>H) continue;
     // 上に シートなどが かぶっている（いまは さわれない）ボタンは みない
     const cx=Math.min(W-1,Math.max(0,r.left+r.width/2)), cy=Math.min(H-1,Math.max(0,r.top+r.height/2)), top=document.elementFromPoint(cx,cy);
     if(!top||!(e===top||e.contains(top)||top.contains(e))) continue;
     btns.push([e,r]); if(Math.min(r.width,r.height)<30) out.push(`小さい ボタン ${lab(e)} ${Math.round(r.width)}x${Math.round(r.height)}`)}
 }
 for(let i=0;i<btns.length;i++)for(let j=i+1;j<btns.length;j++){const [a,A]=btns[i],[b,B]=btns[j];if(a.contains(b)||b.contains(a))continue;
   const ix=Math.min(A.right,B.right)-Math.max(A.left,B.left), iy=Math.min(A.bottom,B.bottom)-Math.max(A.top,B.top);
   if(ix>2&&iy>2&&ix*iy>.15*Math.min(A.width*A.height,B.width*B.height)) out.push(`ボタンが 重なる ${lab(a)} × ${lab(b)}`)}
 return [...new Set(out)]}"""
# すきま しらべ（SPACE=1 の とき）：ボタン・タグ・字 と、いちばん 近い 枠（border-image か 線の ある 箱）の 内がわ との すきま、
#   となりの ボタンどうしの すきま、字と ボタンの 重なり。見つけた 所は 枠ごと 切りぬいて _sweep/space/ に（赤い 線＝その 物）
SPACE=os.environ.get('SPACE')=='1'
SPACEJS=r"""()=>{const W=innerWidth,H=innerHeight,out=[];
 const vis=e=>e.checkVisibility?e.checkVisibility({opacityProperty:true,visibilityProperty:true}):!!e.getClientRects().length;
 const px=v=>parseFloat(v)||0;
 // 枠の 絵の 光る ふちの 内がわ（絵の 点。11/9 dev/canva の 9わけ 絵を はかった）：[上,左,下,右, はみ出し, 9わけ の 大きさ]
 const FR=[['.panel,.buy-in,.sheet-in',[37,33,32,34,8,88]],['.card,.zrow,.item,.setstrip,.pouch',[42,36,34,36,8,88]],['.topper,.cframe,.ammo-case,.ammo-lid',[30,28,28,29,6,58]]];
 const famOf=f=>{for(const [sel,v] of FR) if(f.matches(sel)) return v; return null};
 const framed=f=>!!famOf(f);
 const bw=(f,side)=>{const v=famOf(f),c=getComputedStyle(f),k=px(c.borderImageWidth.split(' ')[0])/v[5];return (v[{Top:0,Left:1,Bottom:2,Right:3}[side]]-v[4])*k};
 const lab=e=>(e.id?'#'+e.id:'')+(typeof e.className==='string'&&e.className?'.'+e.className.trim().split(/\s+/).slice(0,2).join('.'):e.tagName.toLowerCase())+' 「'+(e.textContent||'').trim().slice(0,10)+'」';
 const onTop=(e,r)=>{const t=document.elementFromPoint(Math.min(W-1,Math.max(0,r.left+r.width/2)),Math.min(H-1,Math.max(0,r.top+r.height/2)));return t&&(t===e||e.contains(t)||t.contains(e))};
 const inScrollView=(e,r)=>{for(let a=e.parentElement;a;a=a.parentElement){const c=getComputedStyle(a);if(/(auto|scroll)/.test(c.overflowY)){const R=a.getBoundingClientRect();return r.top>=R.top-1&&r.bottom<=R.bottom+1}}return true};
 const items=[];
 for(const e of document.querySelectorAll('#app *')){
   if(!vis(e))continue;const r=e.getBoundingClientRect();if(r.width<4||r.height<4||r.right<0||r.left>W||r.bottom<0||r.top>H)continue;
   const btn=e.matches('button,[role=button],.price,.tagown,.tg,.cnt,.buy,.x');
   const txt=!btn&&[...e.childNodes].some(n=>n.nodeType===3&&n.textContent.trim())&&!e.closest('button,.price,.tagown,.tg');
   if(!btn&&!txt)continue; if(!inScrollView(e,r)||!onTop(e,r))continue;
   items.push([e,r,btn]);
   let f=e.parentElement; while(f&&f.id!=='app'&&!framed(f)) f=f.parentElement; if(!f||f.id==='app')continue;
   const F=f.getBoundingClientRect(), g={l:r.left-(F.left+bw(f,'Left')),r:(F.right-bw(f,'Right'))-r.right,t:r.top-(F.top+bw(f,'Top')),b:(F.bottom-bw(f,'Bottom'))-r.bottom};
   const lim=btn?5:4;
   for(const [k,v] of Object.entries(g)) if(v<lim) out.push({m:`${btn?'ボタン':'字'}と 枠が ちかい(${k} ${v.toFixed(1)}px) ${lab(e)} in ${lab(f)}`,F:[F.left,F.top,F.width,F.height],E:[r.left,r.top,r.width,r.height],k:lab(f).split(' ')[0]+'|'+lab(e).split(' ')[0]+'|'+k});
 }
 const bs=items.filter(x=>x[2]);
 for(let i=0;i<bs.length;i++)for(let j=i+1;j<bs.length;j++){const [a,A]=bs[i],[b,B]=bs[j];if(a.contains(b)||b.contains(a))continue;
   const dx=Math.max(B.left-A.right,A.left-B.right), dy=Math.max(B.top-A.bottom,A.top-B.bottom);
   if(dx<6&&dy<6&&Math.max(dx,dy)>-1&&(dx<0||dy<0)) out.push({m:`ボタンどうし ちかい(${Math.max(dx,dy).toFixed(1)}px) ${lab(a)} / ${lab(b)}`,F:[Math.min(A.left,B.left),Math.min(A.top,B.top),Math.max(A.right,B.right)-Math.min(A.left,B.left),Math.max(A.bottom,B.bottom)-Math.min(A.top,B.top)],E:[A.left,A.top,A.width,A.height],k:lab(a).split(' ')[0]+'~'+lab(b).split(' ')[0]})}
 for(const [t,T] of items.filter(x=>!x[2]))for(const [b,B] of bs){if(b.contains(t)||t.contains(b))continue;
   const ix=Math.min(T.right,B.right)-Math.max(T.left,B.left), iy=Math.min(T.bottom,B.bottom)-Math.max(T.top,B.top);
   if(ix>2&&iy>2) out.push({m:`字と ボタンが 重なる ${lab(t)} × ${lab(b)}`,F:[Math.min(T.left,B.left),Math.min(T.top,B.top),Math.max(T.right,B.right)-Math.min(T.left,B.left),Math.max(T.bottom,B.bottom)-Math.min(T.top,B.top)],E:[T.left,T.top,T.width,T.height],k:lab(t).split(' ')[0]+'x'+lab(b).split(' ')[0]})}
 const seen=new Set();return out.filter(o=>!seen.has(o.k)&&seen.add(o.k))}"""
PREP="""()=>{const T=window.__T,G=T.G;G.cleared=[0,1,2,3];G.bought=[0,1,2,3,4];G.balls=500000;T.openHub('board');
  for(const k of Object.keys(T.BALLS)) if(k!=='normal') (G.owned||(G.owned={}))[k]=Math.max(G.owned[k]||0,(T.BALLS[k].board||0)<=3?2:0)}"""
async def run(b,name,W,H,D,rep):
    ctx=await b.new_context(viewport={'width':W,'height':H},device_scale_factor=D,has_touch=True)
    pg=await ctx.new_page(); errs=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto('file://'+os.path.join(HERE,'game.html')); await pg.wait_for_timeout(2600)
    shots=[]
    async def shot(label,wait=700):
        await pg.wait_for_timeout(wait)
        f=os.path.join(OUT,f'_{name}_{len(shots):02d}.png'); await pg.screenshot(path=f)
        found=await pg.evaluate(CHECK,label); shots.append((label,f))
        for x in found: rep.append(f'{name} / {label}: {x}')
        if SPACE:
            sp=await pg.evaluate(SPACEJS); im=Image.open(f).convert('RGB')
            os.makedirs(os.path.join(OUT,'space'),exist_ok=True)
            for i,o in enumerate(sp):
                rep.append(f'{name} / {label}: すきま {o["m"]}')
                x,y,w,h=[v*D for v in o['F']]; ex,ey,ew,eh=[v*D for v in o['E']]; pad=10*D
                box=(max(0,int(x-pad)),max(0,int(y-pad)),min(im.width,int(x+w+pad)),min(im.height,int(y+h+pad)))
                if box[2]-box[0]<4 or box[3]-box[1]<4: continue
                c=im.crop(box); dd=ImageDraw.Draw(c); dd.rectangle([ex-box[0],ey-box[1],ex+ew-box[0],ey+eh-box[1]],outline=(255,40,40),width=max(1,int(D)))
                c.save(os.path.join(OUT,'space',f'{name}_{len(shots):02d}_{i:02d}.png'))
    async def tap(sel):
        try: await pg.click(sel,timeout=2500)
        except Exception as e: rep.append(f'{name}: タップ できない {sel} ({str(e).splitlines()[0][:80]})')
    await shot('タイトル',0)
    await tap('#startBtn'); await pg.wait_for_timeout(600); await pg.evaluate(PREP); await shot('台えらび',1400)
    for t,l in [('ball','玉'),('tower','タワー'),('gimmick','ギミック'),('set','セット'),('zukan','図鑑')]:
        await tap(f'#tabs [data-tab="{t}"]'); await shot(l,1100)
    await tap('#tabs [data-tab="ball"]'); await pg.wait_for_timeout(900)
    await tap('#hubBody .card >> nth=2'); await shot('買う',800)
    await tap('#buyNo'); await pg.wait_for_timeout(500)
    await tap('#tabs [data-tab="board"]'); await pg.wait_for_timeout(1000)
    await pg.evaluate("()=>window.__T.openBoardBuy(5)"); await shot('台を買う',800)
    await pg.evaluate("()=>{const b=document.getElementById('buyNo');b&&b.click()}"); await pg.wait_for_timeout(500)
    await pg.evaluate("()=>window.__T.playBoard(1)"); await shot('台',1800)
    await pg.evaluate("()=>{const T=window.__T,G=T.G;const p=G.pegs.filter(p=>!p.fixed&&!p.tower)[3];T.openBuild(p)}"); await shot('タワーを置く',700)
    await pg.evaluate("()=>{const T=window.__T,G=T.G;T.closeSheet();const p=G.pegs.filter(p=>!p.fixed&&!p.tower)[2];p.tower=T.newTower('fire',p);p.tower.land=0;T.openInfo(p)}"); await shot('タワーの 中身',700)
    await pg.evaluate("()=>window.__T.closeSheet()"); await pg.wait_for_timeout(400)
    await tap('#backBtn'); await shot('もどる',600)
    await tap('#quitNo'); await pg.wait_for_timeout(400)
    await pg.evaluate("()=>{const T=window.__T;T.G.wave=10;T.stageClear()}"); await shot('クリア',1500)
    await pg.evaluate("()=>{const T=window.__T;T.playBoard(0);T.gameOver()}"); await shot('ゲームオーバー',1500)
    await pg.evaluate("()=>{const T=window.__T;T.G.cleared=[0,1,2,3,4,5,6,7,8];T.showEnding(()=>{})}"); await shot('エンディング',2500)
    if errs: rep.append(f'{name}: エラー {errs[:4]}')
    await ctx.close()
    # 一覧
    ims=[(l,Image.open(f)) for l,f in shots]; tw=300 if W<H else 420
    th=int(tw*H/W); cols=6 if W<H else 4; rows=(len(ims)+cols-1)//cols
    S=Image.new('RGB',(cols*(tw+8),rows*(th+30)),(24,24,30)); d=ImageDraw.Draw(S)
    try:
        from PIL import ImageFont; F=ImageFont.truetype('/usr/share/fonts/opentype/noto/NotoSansCJK-Regular.ttc',18)
    except Exception: F=None
    for i,(l,im) in enumerate(ims):
        x,y=(i%cols)*(tw+8),(i//cols)*(th+30); S.paste(im.convert('RGB').resize((tw,th)),(x,y+26)); d.text((x+4,y+2),l,fill=(255,255,255),font=F)
    S.save(os.path.join(OUT,name+'.png'))
    for _,f in shots: os.remove(f)
async def main():
    os.makedirs(OUT,exist_ok=True); rep=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        for n in ONLY:
            W,H,D=DEV[n]; await run(b,n,W,H,D,rep); print(n,'ok',flush=True)
        await b.close()
    open(os.path.join(OUT,'report.txt'),'w').write('\n'.join(rep)); print(len(rep),'件')
asyncio.run(main())
