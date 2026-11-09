# 9台を あそんだ あとの キャンバスの メモリ（MB）を、作った 関数ごとに 出す（11/9 iPhone・iPad の 上限 しらべ。iOS は 合計 およそ 224MB で 絵が 出なくなる）
# 使い方: python3 mk.py && python3 canvmem.py はばx高さx細かさ（例 1024x1366x2＝iPad Pro）
import asyncio, sys, os
HERE=os.path.dirname(os.path.abspath(__file__))
from playwright.async_api import async_playwright
SETUP=open(os.path.join(HERE,'fps9.py')).read().split('SETUP=r"""')[1].split('"""')[0]
INIT="""(()=>{window.__cv=[];const ce=Document.prototype.createElement;Document.prototype.createElement=function(t,...a){const e=ce.call(this,t,...a);if(String(t).toLowerCase()==='canvas'){let w='?';try{throw new Error()}catch(x){const f=x.stack.split('\\n').slice(2,5).map(l=>(l.match(/at (\\S+)/)||[])[1]).filter(Boolean);w=f.join('<')}e.__w=w;window.__cv.push(new WeakRef(e))}return e};})()"""
MEAS="""()=>{gc&&gc();let n=0,px=0,big=[];const all=new Set();for(const r of window.__cv){const c=r.deref();if(c)all.add(c)}for(const c of document.querySelectorAll('canvas'))all.add(c);
 for(const c of all){const p=c.width*c.height;if(!p)continue;n++;px+=p;big.push([c.width,c.height,c.className||c.id||''])}
 big.sort((a,b)=>b[0]*b[1]-a[0]*a[1]);const by={};for(const c of all){const p=c.width*c.height;if(!p)continue;const k=c.__w||('dom:'+(c.className||c.id));by[k]=(by[k]||0)+p*4/1048576}
 return {n,MB:Math.round(px*4/1048576),by:Object.entries(by).sort((a,b)=>b[1]-a[1]).slice(0,14).map(([k,v])=>k+' '+v.toFixed(1))}}"""
async def main():
    W,H,D=[float(x) for x in sys.argv[1].split('x')]
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--js-flags=--expose-gc'])
        pg=await b.new_page(viewport={'width':int(W),'height':int(H)},device_scale_factor=D)
        await pg.add_init_script(INIT)
        await pg.goto('file://'+os.path.join(HERE,'game.html')); await pg.wait_for_timeout(1500)
        
        await pg.evaluate("()=>{const T=window.__T;T.G.cleared=[0,1,2,3,4,5,6,7,8];T.G.bought=[0,1,2,3,4,5,6,7,8];T.openHub('board')}"); await pg.wait_for_timeout(9000)
        for t in ['ball','tower','gimmick','set','zukan','board']:
            await pg.evaluate(f"()=>window.__T.showTab('{t}')"); await pg.wait_for_timeout(500)
        
        for bd in range(9):
            await pg.evaluate(SETUP,bd); await pg.wait_for_timeout(500)
            await pg.evaluate("""()=>{const T=window.__T,G=T.G;G.fever=0;G.en=[];G.pend=[];G.portals=[];G.spawnQ=[];T.startWave(10);for(let i=0;i<60*8;i++){G.life=10;T.update(1/60);T.updateFx(1/60);G.time+=1/60;if(i%4==0)T.draw()}}""")
        print('after 9 boards',await pg.evaluate(MEAS))
        await pg.evaluate("()=>{window.__T.openHub('board')}"); await pg.wait_for_timeout(1500)
        print('back to hub',await pg.evaluate(MEAS))
        await b.close()
asyncio.run(main())
