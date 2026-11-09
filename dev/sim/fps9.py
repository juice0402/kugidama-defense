# 9台を ほんとうに 動かして（ゲームの ループのまま）、1コマの 時間と フレーム落ちを はかる（11/9 軽量化）
# 砲台を ぜんぶの 杭に・ギミックも つけて、FEVER（5ウェーブ）と ボス戦を それぞれ 何秒か。CPU を おそくして スマホの かわりに
# 使い方: python3 mk.py && python3 fps9.py [遅さ=4] [秒=3] [台の番号,...]
import asyncio, sys, os, json
from playwright.async_api import async_playwright
RATE=float(sys.argv[1]) if len(sys.argv)>1 else 4
SEC=float(sys.argv[2]) if len(sys.argv)>2 else 3
BOARDS=[int(x) for x in sys.argv[3].split(',')] if len(sys.argv)>3 else list(range(9))
HERE=os.path.dirname(os.path.abspath(__file__))
SETUP=r"""
(b)=>{const T=window.__T,G=T.G;
  G.cleared=[0,1,2,3,4,5,6,7,8];G.bought=[0,1,2,3,4,5,6,7,8];
  const bk=(O,b)=>Object.keys(O).filter(k=>(O[k].board||0)===b);
  T.playBoard(b); G.balls=99999; G.banners=[]; G.paused=false;
  const nb=bk(T.BALLS,b).filter(k=>k!=='normal'), nt=bk(T.TOWERS,b).filter(k=>k!=='basic'), ng=bk(T.GIMMICKS,b);
  G.deck=b===0?['fire','ice','bolt','poison','bb']:[nb[0],nb[1],nb[0],nb[1],'fire'];
  const tw=b===0?['fire','ice','bolt','poison','basic','long']:[nt[0],nt[1],'fire','ice',nt[0],nt[1]];
  G.pegs.forEach((p,i)=>{if(p.fixed)return;p.tower=T.newTower(tw[i%tw.length],p);p.r=Math.max(p.r,7);if(i%2===0)p.tower.gm=(b===0?(i%4?'bumper':'spinner'):ng[0])});
  T.buildStatic();
  let g=0;while(G.wave<5&&g<60*240){G.life=10;if(G.wave>=3)G.fever=8;T.update(1/60);T.updateFx(1/60);G.time+=1/60;g++}
  for(let i=0;i<60*5;i++){G.life=10;G.fever=8;T.update(1/60);T.updateFx(1/60);G.time+=1/60}
  return G.wave}"""
BOSS=r"""()=>{const T=window.__T,G=T.G;G.fever=0;G.en=[];G.pend=[];G.portals=[];G.spawnQ=[];T.startWave(10);
  for(let i=0;i<60*12;i++){G.life=10;T.update(1/60);T.updateFx(1/60);G.time+=1/60} return G.en.length}"""
REC=r"""
(ms)=>new Promise(res=>{const T=window.__T,G=T.G;
  const keepF=G.fever>0; const iv=[];let last=0,up=0,dr=0,n=0;
  const u0=T.update,d0=T.draw;
  // ループの 中の update と draw の 時間（__T の 関数を 入れかえても ループは 中の 名前で よぶので、ここは 1コマの あいだだけ はかる）
  const t0=performance.now();
  function f(t){if(last)iv.push(t-last);last=t;G.life=10;if(keepF)G.fever=8;
    if(t-t0<ms)requestAnimationFrame(f);else{
      iv.sort((a,b)=>a-b);const avg=iv.reduce((a,b)=>a+b,0)/iv.length,p95=iv[Math.floor(iv.length*.95)],drop=iv.filter(x=>x>25).length;
      res({n:iv.length,avg:+avg.toFixed(1),p95:+p95.toFixed(1),max:+iv[iv.length-1].toFixed(1),drop:drop,dropPct:Math.round(drop/iv.length*100),en:G.en.length,fx:G.fx.length,bl:G.bl.length,bs:G.bs.length})}}
  requestAnimationFrame(f)})"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg=await b.new_page(viewport={'width':390,'height':780},device_scale_factor=2)
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        cdp=await pg.context.new_cdp_session(pg)
        await pg.goto('file://'+os.path.join(HERE,'game.html')); await pg.wait_for_timeout(1500)
        out={}
        for bd in BOARDS:
            await cdp.send('Emulation.setCPUThrottlingRate',{'rate':1})
            await pg.evaluate(SETUP,bd); await pg.wait_for_timeout(400)
            await cdp.send('Emulation.setCPUThrottlingRate',{'rate':RATE})
            A=await pg.evaluate(REC,int(SEC*1000))
            await cdp.send('Emulation.setCPUThrottlingRate',{'rate':1})
            await pg.evaluate(BOSS); await pg.wait_for_timeout(300)
            await cdp.send('Emulation.setCPUThrottlingRate',{'rate':RATE})
            B=await pg.evaluate(REC,int(SEC*1000))
            name=await pg.evaluate(f"()=>window.__T.STAGES[{bd}].name")
            print(f"{name}: FEVER 平均{A['avg']}ms p95 {A['p95']} 最大{A['max']} 落ち{A['dropPct']}% (敵{A['en']} fx{A['fx']} 弾{A['bl']} 玉{A['bs']}) | ボス 平均{B['avg']}ms p95 {B['p95']} 最大{B['max']} 落ち{B['dropPct']}% (敵{B['en']} fx{B['fx']})",flush=True)
            out[name]={'fever':A,'boss':B}
        print('errors',errs[:4])
        json.dump(out,open(os.path.join(HERE,'_fps9.json'),'w'),ensure_ascii=False)
        await b.close()
asyncio.run(main())
