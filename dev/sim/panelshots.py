# パネル・シート・ボタンの まわりを 1つずつ 大きく 撮る（11/9 すきまの 目で 見る チェック）
# 使い方: python3 mk.py && python3 panelshots.py はばx高さx細かさ [出す フォルダ=_panels]
import asyncio, sys, os
from playwright.async_api import async_playwright
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
W,H,D=[float(x) for x in sys.argv[1].split('x')]
OUT=os.path.join(HERE,sys.argv[2] if len(sys.argv)>2 else '_panels'); os.makedirs(OUT,exist_ok=True)
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        ctx=await b.new_context(viewport={'width':int(W),'height':int(H)},device_scale_factor=D,has_touch=True,reduced_motion='reduce')
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+os.path.join(HERE,'game.html')); await pg.wait_for_timeout(2000)
        n=[0]
        async def el(sel,name,pad=10):
            try:
                loc=pg.locator(sel).first; bb=await loc.bounding_box()
                if not bb: print('no',sel); return
                n[0]+=1; f=os.path.join(OUT,f'{n[0]:02d}_{name}.png')
                await pg.screenshot(path=f,clip={'x':max(0,bb['x']-pad),'y':max(0,bb['y']-pad),'width':min(W,bb['width']+pad*2),'height':min(H,bb['height']+pad*2)})
            except Exception as e: print('err',sel,str(e)[:80])
        await el('#startBtn','title_start',30)
        await pg.click('#startBtn'); await pg.wait_for_timeout(600)
        await pg.evaluate("()=>{const T=window.__T,G=T.G;G.cleared=[0,1,2,3];G.bought=[0,1,2,3,4];G.balls=12345;for(const k of Object.keys(T.BALLS))if(k!=='normal'&&(T.BALLS[k].board||0)<=1)G.owned[k]=2;T.openHub('board')}"); await pg.wait_for_timeout(1500)
        await el('.hub-top','hub_top',4); await el('.hub-body.hall>.setstrip','setstrip'); await el('.slot.cur .topper','topper'); await el('#tabs','tabs',2)
        await pg.click('#tabs [data-tab="ball"]'); await pg.wait_for_timeout(900)
        await el('#hubBody .card.row >> nth=0','card_ball'); await el('#hubBody .card.row >> nth=3','card_ball2')
        await pg.click('#tabs [data-tab="tower"]'); await pg.wait_for_timeout(900)
        await el('#hubBody .card.row >> nth=0','card_tower_own'); await el('#hubBody .card.row >> nth=1','card_tower')
        await pg.click('#tabs [data-tab="set"]'); await pg.wait_for_timeout(1200)
        await el('.settop','set_top',2); await el('.rack','rack',4)
        await pg.click('#tabs [data-tab="zukan"]'); await pg.wait_for_timeout(900)
        await el('.zseg','zseg'); await el('.zrow >> nth=0','zrow')
        await pg.evaluate("()=>{window.__T.G.found.add([...document.querySelectorAll('.zrow[data-k],.zrow')].length?'':'' )}")
        await pg.click('#tabs [data-tab="ball"]'); await pg.wait_for_timeout(900)
        await pg.click('#hubBody .card >> nth=2'); await pg.wait_for_timeout(700); await el('#buyIn','buy_ball',6)
        await pg.click('#buyNo'); await pg.wait_for_timeout(500)
        await pg.click('#tabs [data-tab="board"]'); await pg.wait_for_timeout(900)
        await pg.evaluate("()=>window.__T.openBoardBuy(4)"); await pg.wait_for_timeout(700); await el('#buyIn','buy_board',6)
        await pg.evaluate("()=>document.getElementById('buyNo').click()"); await pg.wait_for_timeout(500)
        await pg.evaluate("()=>window.__T.playBoard(1)"); await pg.wait_for_timeout(1500)
        await el('.hud','hud',2); await el('.bottom','bottom',2)
        await pg.evaluate("()=>{const T=window.__T,G=T.G;G.balls=999;const p=G.pegs.filter(p=>!p.fixed&&!p.tower)[3];T.openBuild(p)}"); await pg.wait_for_timeout(700)
        await el('.sheet-in','sheet_build',4); await el('#sheetBody .trow >> nth=0','trow0'); await el('#sheetBody .trow >> nth=1','trow1')
        await pg.evaluate("()=>{const T=window.__T,G=T.G;T.closeSheet();const p=G.pegs.filter(p=>!p.fixed&&!p.tower)[2];p.tower=T.newTower('fire',p);p.tower.land=0;T.openInfo(p)}"); await pg.wait_for_timeout(700)
        await el('.sheet-in','sheet_info',4)
        await pg.evaluate("()=>window.__T.closeSheet()"); await pg.wait_for_timeout(300)
        await pg.click('#backBtn'); await pg.wait_for_timeout(600); await el('#quitIn','quit',6)
        await pg.wait_for_timeout(300); await pg.click('#quitNo'); await pg.wait_for_timeout(400)
        await pg.evaluate("()=>{const T=window.__T;T.G.wave=10;T.stageClear()}"); await pg.wait_for_timeout(1400); await el('.res-wrap','result_clear',6)
        await pg.evaluate("()=>{const T=window.__T;T.playBoard(0);T.gameOver()}"); await pg.wait_for_timeout(1400); await el('.res-wrap','result_over',6)
        print('errors',errs[:3]); await b.close()
asyncio.run(main())
