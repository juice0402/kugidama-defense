# drawcheck.js の 分けて すすむ 版（11/9 さいごの 総デバッグ）：台ごとに 別の ページで、その台の おばけは ぜんぶの 状態・
# ほかの 台の おばけは 主な 状態だけ。属性・とくしゅ効果・わざを ぜんぶ つけて 動かすのは 全部の おばけ。台ごとに 結果を 出す
# 使い方: python3 mk.py && python3 dcfast.py [台の番号,...]
import asyncio, sys, os, re
from playwright.async_api import async_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
SRC=open(os.path.join(HERE,'drawcheck.js')).read()
STATES=re.search(r'const states=(\[.*?\]);\n',SRC,re.S).group(1)
JS=r"""(s)=>{const T=window.__T,G=T.G,errs=[];let n=0;const states=%s;
const few=[{},{stun:2},{sleep:2},{freeze:1,stun:1,slow:2,slowF:.3},{burn:3,burnD:1},{wet:4},{ghost:1},{hurtT:.3}];
try{T.playBoard(T.BOARDS.findIndex(b=>b.stage===s));G.paused=true}catch(x){return {n,errs:['play'+s+':'+x.message],ne:1}}
const own=new Set(T.STAGES[s].foes);
for(const t of Object.keys(T.ENEMIES)){
  for(const st of (own.has(t)?states:few)){
    try{G.en=[];const e=T.addEnemy(t,188,260);Object.assign(e,st);T.draw();for(let i=0;i<20;i++){T.update(1/60);G.time+=1/60}T.draw();n++}catch(x){errs.push(s+'/'+t+'/'+JSON.stringify(st)+':'+x.message)}
  }
  try{G.en=[];const e=T.addEnemy(t,188,260),o=T.addEnemy('neko',200,280);
    for(const k of T.EL_ORDER){T.applyEl(e,k,3,2);T.applyEff(e,{sp:k},2)}
    for(const c of Object.keys(T.COMBO))T.applyEff(e,{combo:c},2);
    for(let i=0;i<120;i++){T.update(1/60);G.time+=1/60;if(i%%20==0)T.draw()}n++}catch(x){errs.push(s+'/'+t+'/all:'+x.message)}
}
G.en=[];return {n,errs:errs.slice(0,10),ne:errs.length}}"""%STATES
BOARDS=[int(x) for x in sys.argv[1].split(',')] if len(sys.argv)>1 else list(range(9))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        tot=0
        for s in BOARDS:
            pg=await b.new_page(viewport={'width':390,'height':780}); errs=[]
            pg.on('pageerror',lambda e:errs.append(str(e)))
            pg.on('console',lambda m: errs.append('console:'+m.text) if m.type=='error' else None)
            await pg.goto('file://'+os.path.join(HERE,'game.html')); await pg.wait_for_timeout(600)
            r=await pg.evaluate(JS,s); tot+=r['ne']+len(errs)
            print(f'台{s}: {r["n"]} ok / エラー {r["ne"]} {r["errs"][:3]} ページ {errs[:3]}',flush=True)
            await pg.close()
        print('合計 エラー',tot); await b.close()
asyncio.run(main())
