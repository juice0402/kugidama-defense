# ロビーのタブ切りかえ・杭/砲台のシートの重さを、CPU を遅くして測る（スマホのかわり）。
# 使い方: python3 mk.py && python3 uiperf.py [遅さ=6]
import asyncio, sys, os, json
from playwright.async_api import async_playwright
RATE=float(sys.argv[1]) if len(sys.argv)>1 else 6
WAIT=int(sys.argv[2]) if len(sys.argv)>2 else 800   # タイトルで待つms
JS=r"""
async()=>{
  const T=window.__T, G=T.G, out={};
  const raf2=()=>new Promise(r=>requestAnimationFrame(()=>requestAnimationFrame(r)));
  const m=async fn=>{const t=performance.now();fn();const s=performance.now()-t;document.body.offsetHeight;await raf2();return [Math.round(s),Math.round(performance.now()-t)]};
  out.hubFirst=await m(()=>T.openHub('board'));
  const tabs=['ball','tower','gimmick','set','zukan','board'];
  out.tab1={}; for(const t of tabs) out.tab1[t]=await m(()=>T.showTab(t));
  out.tab2={}; for(const t of tabs) out.tab2[t]=await m(()=>T.showTab(t));
  out.enter=await m(()=>T.playBoard(0));
  await new Promise(r=>setTimeout(r,800));
  const pegs=G.pegs.filter(p=>!p.fixed);
  for(const p of pegs.slice(0,6)){p.tower=T.newTower('basic',p);p.r=Math.max(p.r,7)} T.buildStatic();
  const empty=pegs[8], tw=pegs[0];
  out.build1=await m(()=>T.openBuild(empty)); out.close1=await m(()=>T.closeSheet());
  out.build2=await m(()=>T.openBuild(empty)); T.closeSheet();
  out.info1=await m(()=>T.openInfo(tw)); T.closeSheet();
  out.info2=await m(()=>T.openInfo(tw)); T.closeSheet();
  return out;
}"""
async def metrics(cdp):
    r=await cdp.send('Performance.getMetrics'); return {x['name']:x['value'] for x in r['metrics']}
async def window(pg,cdp,label,ms=2000):
    a=await metrics(cdp); await pg.wait_for_timeout(ms); b=await metrics(cdp)
    k=lambda n:round((b[n]-a[n])/(b['Timestamp']-a['Timestamp'])*100)
    print(f'{label}: 忙しさ {k("TaskDuration")}% (script {k("ScriptDuration")}% style {k("RecalcStyleDuration")}% layout {k("LayoutDuration")}%)')
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg=await b.new_page(viewport={'width':390,'height':780},device_scale_factor=2)
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.add_init_script("try{localStorage.setItem('kugidama-test','1')}catch(_){}")
        cdp=await pg.context.new_cdp_session(pg)
        await pg.goto('file://'+os.path.join(os.path.dirname(os.path.abspath(__file__)),'game.html'))
        await pg.wait_for_timeout(WAIT)
        await cdp.send('Performance.enable'); await cdp.send('Emulation.setCPUThrottlingRate',{'rate':RATE})
        r=await pg.evaluate(JS)
        print(f'CPU {RATE}倍おそい。[同期ms, 画面に出るまでms]')
        for k,v in r.items(): print(k, json.dumps(v,ensure_ascii=False))
        await window(pg,cdp,'台で遊んでいる')
        await pg.evaluate("()=>{const T=__T;T.openInfo(T.G.pegs.filter(p=>!p.fixed)[0])}")
        await window(pg,cdp,'砲台の説明を開いている')
        await pg.evaluate("()=>{__T.closeSheet();__T.openHub('board')}")
        await pg.wait_for_timeout(500); await window(pg,cdp,'ロビー 台のタブ')
        await pg.evaluate("()=>__T.showTab('set')"); await pg.wait_for_timeout(300); await window(pg,cdp,'ロビー セットのタブ')
        print('errors',errs[:4]); await b.close()
asyncio.run(main())
