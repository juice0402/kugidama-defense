# iOS アプリの 中と おなじ 形（APP_PLATFORM='ios'・APP_HAPTIC・自動の ためし ではない）で ためす（11/9）
#  1) 振動が 出来事で よばれる  2) ためしモード（ロゴ5回）と #shot= が きかない  3) セーブ → 開きなおし で のこる  4) こわれた セーブでも 動く
# 使い方: python3 mk.py && python3 iostest.py
import asyncio, os, json
from playwright.async_api import async_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
INIT="""window.APP_LANGS=['ja'];window.APP_PLATFORM='ios';window.APP_ZOOM=1;window.__hap=[];window.APP_HAPTIC=k=>window.__hap.push(k);
Object.defineProperty(navigator,'webdriver',{get:()=>false});"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        ctx=await b.new_context(viewport={'width':393,'height':852},device_scale_factor=2,has_touch=True)
        await ctx.add_init_script(INIT)
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        url='file://'+os.path.join(HERE,'game.html')
        await pg.goto(url); await pg.wait_for_timeout(1500)
        ok=lambda c,m:print(('OK  ' if c else 'NG  ')+m,flush=True)
        # ためしモード：ロゴ 5回
        for i in range(6): await pg.click('#title .logo',force=True); await pg.wait_for_timeout(80)
        t=await pg.evaluate("()=>[!document.getElementById('titleTest').hidden,localStorage.getItem('kugidama-test')]")
        ok(t==[False,None],f'ためしモードが 出ない {t}')
        await pg.evaluate("()=>{location.hash='shot=play:7'}"); await pg.wait_for_timeout(800)
        ok(await pg.evaluate("()=>window.__T.G.state")=='title','#shot= が きかない')
        # スタート → 玉を 買う → セット
        await pg.click('#startBtn'); await pg.wait_for_timeout(900)
        await pg.evaluate("()=>{window.__T.G.balls=5000}")
        await pg.click('#tabs [data-tab="ball"]'); await pg.wait_for_timeout(900)
        await pg.click('#hubBody .card >> nth=1'); await pg.wait_for_timeout(500); await pg.click('#buyYes'); await pg.wait_for_timeout(900)
        await pg.click('#tabs [data-tab="set"]'); await pg.wait_for_timeout(1300)
        await pg.click('.foam .chamber.sp >> nth=0'); await pg.wait_for_timeout(700); await pg.click('.rack .pouch >> nth=1'); await pg.wait_for_timeout(900)
        # 台 → タワーを 建てる
        await pg.click('#tabs [data-tab="board"]'); await pg.wait_for_timeout(900)
        await pg.click('.slot.cur .cab'); await pg.wait_for_timeout(2500)
        await pg.evaluate("()=>{const T=window.__T,G=T.G;const p=G.pegs.filter(p=>!p.fixed&&!p.tower)[2];T.openBuild(p)}"); await pg.wait_for_timeout(500)
        await pg.click('#sheetBody .trow:not(.locked) .buy >> nth=0'); await pg.wait_for_timeout(900)
        await pg.evaluate("()=>{const T=window.__T,G=T.G;G.fever=0;T.heso&&0}")
        await pg.evaluate("()=>{const T=window.__T,G=T.G;T.startWave(5);for(let i=0;i<60*25;i++){G.life=10;T.update(1/60);T.updateFx(1/60);G.time+=1/60}}"); await pg.wait_for_timeout(500)
        await pg.evaluate("()=>{const T=window.__T;T.G.wave=10;T.stageClear()}"); await pg.wait_for_timeout(1500)
        hap=await pg.evaluate("()=>window.__hap")
        for k in ['success','light','medium','warning']:
            ok(k in hap,f'振動 {k}（{len(hap)}回: {sorted(set(hap))}）')
        st=await pg.evaluate("()=>{const G=window.__T.G;return {balls:G.balls,owned:G.owned,cleared:G.cleared,deck:G.deck}}")
        # 開きなおし
        await pg.reload(); await pg.wait_for_timeout(1500); await pg.click('#startBtn'); await pg.wait_for_timeout(900)
        st2=await pg.evaluate("()=>{const G=window.__T.G;return {balls:G.balls,owned:G.owned,cleared:G.cleared,deck:G.deck}}")
        if st!=st2: print('    diff',{k:(st[k],st2[k]) for k in st if st[k]!=st2[k]})
        ok(st==st2,f'開きなおしても セーブが のこる（coins {st["balls"]}→{st2["balls"]} cleared {st2["cleared"]}）')
        # こわれた セーブ
        await pg.evaluate("()=>{for(const k of Object.keys(localStorage)) if(/kugidama-save/.test(k)) localStorage.setItem(k,'{こわれた')}")
        await pg.reload(); await pg.wait_for_timeout(1500)
        await pg.click('#startBtn'); await pg.wait_for_timeout(900)
        ok(await pg.evaluate("()=>window.__T.G.state")=='hub','こわれた セーブでも 始められる')
        ok(not errs,f'エラー {errs[:3]}')
        await b.close()
asyncio.run(main())
