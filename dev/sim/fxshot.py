# 演出の 場面を 決まった 時間で 止めて 撮って 1まいに ならべる（11/8 7.。rAF を 止めて 手で update/draw）。先に mk.py
# 使い方: python3 fxshot.py 出す.png [はばx高さ] [場面の 名前 ...]（名前なしで ぜんぶ）。環境変数 WAIT（CSS の 動きを まつ ms）・COLS（よこの 数）・SCALE（ちぢめる）・KEEP（1まいずつも のこす）
# 場面：wave（WAVE）・stage／st0〜8（台の名前）・fever（FEVER の はじめ）・fever2（FEVER の のこり）・boss／bs0〜8（ボス出現）・mid（中ボス）・wclear（WAVE クリア）・hits（わざの 文字と コイン）・
#       clear／clear6（クリア）・over（ゲームオーバー）・ending・set（玉のセット）・crown（王冠の 帯）・toast・zukan・tower・info・build
import asyncio, sys, os, json
from playwright.async_api import async_playwright
from PIL import Image, ImageDraw
GAME=__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'game.html')
PRE=r"""
window.__S={
 stop(){window.requestAnimationFrame=()=>0},
 step(sec,draw=true){const T=__T,G=T.G;const n=Math.round(sec*60);for(let i=0;i<n;i++){if(G.state==='play'&&!G.paused)T.update(1/60);T.updateFx(1/60);G.time+=1/60}if(draw)T.draw()},
 board(i){const T=__T,G=T.G;G.cleared=[0,1,2,3,4,5,6,7,8];G.bought=[0,1,2,3,4,5,6,7,8];T.playBoard(i);G.banners=[];G.balls=500;
   G.pegs.forEach((p,j)=>{if(j%3===0)p.tower=T.newTower(['basic','fire','ice','bolt'][j%4],p)});T.buildStatic()},
};
"""
SC={
 'st0': "__S.board(0);__S.step(.1);__T.G.banners=[];__T.startStage();__T.G.banners=__T.G.banners.filter(b=>b.text.indexOf('WAVE')<0);__S.step(.6)",
 'st1': "__S.board(1);__S.step(.1);__T.G.banners=[];__T.startStage();__T.G.banners=__T.G.banners.filter(b=>b.text.indexOf('WAVE')<0);__S.step(.6)",
 'st2': "__S.board(2);__S.step(.1);__T.G.banners=[];__T.startStage();__T.G.banners=__T.G.banners.filter(b=>b.text.indexOf('WAVE')<0);__S.step(.6)",
 'st3': "__S.board(3);__S.step(.1);__T.G.banners=[];__T.startStage();__T.G.banners=__T.G.banners.filter(b=>b.text.indexOf('WAVE')<0);__S.step(.6)",
 'st4': "__S.board(4);__S.step(.1);__T.G.banners=[];__T.startStage();__T.G.banners=__T.G.banners.filter(b=>b.text.indexOf('WAVE')<0);__S.step(.6)",
 'st5': "__S.board(5);__S.step(.1);__T.G.banners=[];__T.startStage();__T.G.banners=__T.G.banners.filter(b=>b.text.indexOf('WAVE')<0);__S.step(.6)",
 'st6': "__S.board(6);__S.step(.1);__T.G.banners=[];__T.startStage();__T.G.banners=__T.G.banners.filter(b=>b.text.indexOf('WAVE')<0);__S.step(.6)",
 'st7': "__S.board(7);__S.step(.1);__T.G.banners=[];__T.startStage();__T.G.banners=__T.G.banners.filter(b=>b.text.indexOf('WAVE')<0);__S.step(.6)",
 'st8': "__S.board(8);__S.step(.1);__T.G.banners=[];__T.startStage();__T.G.banners=__T.G.banners.filter(b=>b.text.indexOf('WAVE')<0);__S.step(.6)",
 'bs0': "__S.board(0);__S.step(.3);__T.G.wave=10;__T.spawn(__T.STAGES[0].foes[4]);__S.step(.8)",
 'bs1': "__S.board(1);__S.step(.3);__T.G.wave=10;__T.spawn(__T.STAGES[1].foes[4]);__S.step(.8)",
 'bs2': "__S.board(2);__S.step(.3);__T.G.wave=10;__T.spawn(__T.STAGES[2].foes[4]);__S.step(.8)",
 'bs3': "__S.board(3);__S.step(.3);__T.G.wave=10;__T.spawn(__T.STAGES[3].foes[4]);__S.step(.8)",
 'bs4': "__S.board(4);__S.step(.3);__T.G.wave=10;__T.spawn(__T.STAGES[4].foes[4]);__S.step(.8)",
 'bs5': "__S.board(5);__S.step(.3);__T.G.wave=10;__T.spawn(__T.STAGES[5].foes[4]);__S.step(.8)",
 'bs6': "__S.board(6);__S.step(.3);__T.G.wave=10;__T.spawn(__T.STAGES[6].foes[4]);__S.step(.8)",
 'bs7': "__S.board(7);__S.step(.3);__T.G.wave=10;__T.spawn(__T.STAGES[7].foes[4]);__S.step(.8)",
 'bs8': "__S.board(8);__S.step(.3);__T.G.wave=10;__T.spawn(__T.STAGES[8].foes[4]);__S.step(.8)",
 'wave': "__S.board(0);__S.step(.1);__T.G.banners=[];__T.startWave(3);__S.step(.35)",
 'stage': "__S.board(2);__S.step(.1);__T.G.banners=[];__T.startStage();__T.G.banners=__T.G.banners.filter(b=>b.text.indexOf('WAVE')<0);__S.step(.5)",
 'fever': "__S.board(0);__S.step(1);__T.heso(__T.G.heso);__S.step(.45)",
 'fever2': "__S.board(3);__S.step(1);__T.heso(__T.G.heso);__S.step(2.6)",
 'boss': "__S.board(5);__S.step(.5);__T.G.wave=10;__T.spawn(__T.STAGES[5].foes[4]);__S.step(.6)",
 'boss2': "__S.board(7);__S.step(.5);__T.G.wave=10;__T.spawn(__T.STAGES[7].foes[4]);__S.step(.25)",
 'mid': "__S.board(1);__S.step(.5);__T.G.wave=5;__T.spawn(__T.STAGES[1].foes[3]);__S.step(1.0)",
 'wclear': "__S.board(0);__S.step(.3);const G=__T.G;G.spawnQ=[];G.en=[];G.pend=[];G.wave=3;G.waveDone=false;__S.step(.4)",
 'hits': "__S.board(0);__S.step(.3);const T=__T;T.hitText(120,300,'せいなるはしら','#fff0a8','#ffd84a',2);T.hitText(250,380,'ダイヤモンドダスト','#7fd6ff','#fff0a8',3);T.hitText(150,450,'強撃','#ff7a3d','#ff7a3d',1);T.G.texts.push({x:250,y:250,s:'+5',c:'#ffd84a',big:true,t:.8});__S.step(.2)",
 'clear': "__S.board(0);__S.step(.3);__T.G.cleared=[];__T.stageClear()",
 'clear6': "__S.board(6);__S.step(.3);__T.G.cleared=[0,1,2,3,4,5];__T.stageClear()",
 'over': "__S.board(4);__S.step(.3);__T.G.life=0;__S.step(.05)",
 'ending': "__S.board(8);__S.step(.2);__T.showEnding(()=>{});__S.step(2.5)",
 'set': "__T.G.owned={fire:2,ice:1,bolt:3,poison:1,water:1};__T.G.deck=['fire','ice','bolt','normal','normal'];__T.openHub('set')",
 'crown': "__T.G.cleared=[0,1,2,3,4,5,6,7,8];__T.G.bought=[0,1,2,3,4,5,6,7,8];__T.openHub('board')",
 'toast': "__T.openHub('ball');document.getElementById('toast').textContent='森の台をアンロック！ お店に 水弾・蔓弾 がふえたよ';document.getElementById('toast').hidden=false",
 'zukan': "__T.G.found=new Set(['fire+ice','sp:fire']);__T.G.fresh=new Set(['fire+ice']);__T.openHub('zukan')",
 'tower': "__T.openHub('tower')",
 'unlock': "__T.G.cleared=[0,1];__T.G.bought=[];__T.G.balls=5000;__T.openHub('board');__T.buyBoard(2);const sl=document.querySelectorAll('.slot')[2];sl.scrollIntoView({inline:'center',block:'nearest'});sl.classList.add('cur')",
 'info': "__S.board(0);__S.step(.2);const G=__T.G;const p=G.pegs.find(p=>p.tower);p.tower.lv=2;p.tower.xp=3;p.tower.el='fire';p.tower.elT=5;__T.openInfo(p)",
 'build': "__S.board(0);__S.step(.2);const G=__T.G;const p=G.pegs.find(p=>!p.tower&&!p.fixed);__T.openBuild(p)",
}
async def main():
    out=sys.argv[1]; size=sys.argv[2] if len(sys.argv)>2 and 'x' in sys.argv[2] else '390x780'
    names=[a for a in sys.argv[2:] if 'x' not in a] or list(SC)
    W,H=map(int,size.split('x'))
    shots=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        errs=[]
        for nm in names:
            pg=await b.new_page(viewport={'width':W,'height':H},device_scale_factor=1.5)
            pg.on('pageerror',lambda e,nm=nm:errs.append(nm+':'+str(e)))
            await pg.add_init_script(PRE)
            await pg.goto('file://'+GAME)
            await pg.wait_for_timeout(900)
            await pg.evaluate("__S.stop()")
            await pg.wait_for_timeout(100)
            try: await pg.evaluate("()=>{"+SC[nm]+"}")
            except Exception as e: errs.append(nm+':'+str(e)[:200])
            await pg.wait_for_timeout(int(os.environ.get('WAIT','450')))
            f=f'{out}.{nm}.png'; await pg.screenshot(path=f); shots.append((nm,f))
            await pg.close()
        print('errors',errs[:8]); await b.close()
    ims=[(n,Image.open(f)) for n,f in shots]
    cols=min(len(ims),int(os.environ.get('COLS','6'))); rows=(len(ims)+cols-1)//cols
    w=max(i.width for _,i in ims); h=max(i.height for _,i in ims)
    c=Image.new('RGB',(cols*(w+10),rows*(h+30)),(255,255,255)); d=ImageDraw.Draw(c)
    for k,(n,i) in enumerate(ims):
        x=(k%cols)*(w+10); y=(k//cols)*(h+30); c.paste(i,(x,y+26)); d.text((x+4,y+6),n,fill=(0,0,0))
    sc=float(os.environ.get('SCALE','0.5')); c=c.resize((int(c.width*sc),int(c.height*sc)),Image.LANCZOS); c.save(out)
    if not os.environ.get('KEEP'): [os.remove(f) for _,f in shots]
asyncio.run(main())
