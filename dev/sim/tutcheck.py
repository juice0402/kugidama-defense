# はじめての あそびかた（11/10）を さいごまで 動かして、だんごとに 撮る
# 使い方: python3 mk.py && python3 tutcheck.py [はば x 高さ x 倍率] [出す フォルダ]
#   ① ハンドル（右へ まわす＝キーの →）② おばけ ③ 杭を タップ → シート → 建てる → おわり。とちゅうの エラー・止まった ものを しらべる
#   SKIP=1 で とちゅうの「とばす」も ためす
import asyncio, sys, os
from playwright.async_api import async_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
W,H,D=[float(x) for x in (sys.argv[1] if len(sys.argv)>1 else '393x852x3').split('x')]
OUT=os.path.join(HERE,sys.argv[2] if len(sys.argv)>2 else '_tut'); os.makedirs(OUT,exist_ok=True)
ST="""()=>{const T=window.__T.G,t=T.tut,b=document.getElementById('tutBox');return {step:t&&t.step,en:T.en.length,q:T.spawnQ.length,wave:T.wave,waveT:+T.waveT.toFixed(1),bs:T.bs.length,
  s:+T.strength.toFixed(2),towers:T.pegs.filter(p=>p.tower).length,hidden:document.getElementById('tut').hidden,msg:document.getElementById('tutMsg').textContent,
  box:(r=>[r.left|0,r.top|0,r.width|0,r.height|0])(b.getBoundingClientRect()),done:T.tutDone}}"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        ctx=await b.new_context(viewport={'width':int(W),'height':int(H)},device_scale_factor=D,has_touch=True,is_mobile=W<700)
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+os.path.join(HERE,'game.html')+'#tut'); await pg.wait_for_timeout(1500)
        await pg.click('#startBtn'); await pg.wait_for_timeout(1500)
        await pg.click('.slot.cur .cab'); await pg.wait_for_timeout(2600)
        st=lambda: pg.evaluate(ST)
        async def shot(n,label):
            r=await st(); print(f'{n} {label}:',r,flush=True); await pg.screenshot(path=os.path.join(OUT,f'{n}.png')); return r
        r=await shot(1,'ハンドルの 前')
        await pg.wait_for_timeout(1500); r2=await st(); print('   まわす 前に 玉が 出ない？',r2['bs']==0,' おばけが 出ない？',r2['en']==0, 'ウェーブの 時間',r['waveT'],'→',r2['waveT'])
        if os.environ.get('SKIP'):
            await pg.click('#tutSkip'); await pg.wait_for_timeout(3500); r=await shot(9,'とばした'); print('   おわった？',r['done'],r['hidden'],'玉',r['bs'],'おばけ',r['en']); await b.close(); print('エラー',errs); return
        await pg.focus('#handle')
        for i in range(7): await pg.keyboard.press('ArrowRight'); await pg.wait_for_timeout(60)
        await pg.wait_for_timeout(1200); await shot(2,'玉が 出た')
        for i in range(40):
            await pg.wait_for_timeout(250); r=await st()
            if r['step']=='ghost' and r['en']: break
        await pg.wait_for_timeout(700); await shot(3,'おばけ')
        for i in range(120):
            await pg.wait_for_timeout(250); r=await st()
            if r['step']=='tower': break
        await pg.wait_for_timeout(500); r=await shot(4,'杭を タップ')
        peg=await pg.evaluate("""()=>{const T=window.__T.G.tut.peg,cv=document.getElementById('cv').getBoundingClientRect();return T&&[T.x,T.y]}""")
        xy=await pg.evaluate("""([x,y])=>{const r=document.getElementById('cv').getBoundingClientRect();return [r.left+(window.__T.ox??0),0]}""",peg)
        # 台の 座標 → 画面（ring の 場所を 使う）
        ring=await pg.evaluate("()=>{const r=document.getElementById('tutRing').getBoundingClientRect();return [r.left+r.width/2,r.top+r.height/2]}")
        await pg.mouse.click(ring[0],ring[1]); await pg.wait_for_timeout(900); await shot(5,'シート')
        await pg.click('#sheetBody .trow:not(.locked) .buy'); await pg.wait_for_timeout(900); r=await shot(6,'建てた')
        await pg.wait_for_timeout(3200); r=await shot(7,'おわり')
        print('   おわった？',r['done'],'かくれた？',r['hidden'],'ウェーブ の 時間が すすむ？',r['waveT'])
        await pg.wait_for_timeout(4000); r=await st(); print('   おばけが また 出る？',r['en'],r['q'],r['waveT'])
        sv=await pg.evaluate("()=>JSON.parse(localStorage.getItem('kugidama-save')||localStorage.getItem(Object.keys(localStorage)[0])).tut")
        print('   セーブ tut',sv)
        # 2回目は 出ない
        await pg.evaluate("()=>{window.__T.openHub('board')}"); await pg.wait_for_timeout(800); await pg.evaluate("()=>window.__T.playBoard(0)"); await pg.wait_for_timeout(2500)
        r=await st(); print('   2回目は 出ない？',r['hidden'],r['step'])
        await b.close(); print('エラー',errs)
asyncio.run(main())
