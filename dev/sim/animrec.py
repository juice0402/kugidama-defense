# 動き（11/9）を ためす：ほんとうに タップして ロビー・タブ・買う・セット・台・タワーを 置く を 動画に とる
# 使い方: python3 mk.py && python3 animrec.py 出す.webm [shots]   （shots を つけると とちゅうの スクショも animshots/ に）
import asyncio, sys, os
from playwright.async_api import async_playwright
OUT=sys.argv[1] if len(sys.argv)>1 else 'anim.webm'
SHOTS='shots' in sys.argv
HERE=os.path.dirname(os.path.abspath(__file__))
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--autoplay-policy=no-user-gesture-required'])
        vd=os.path.join(HERE,'_video'); os.makedirs(vd,exist_ok=True)
        ctx=await b.new_context(viewport={'width':390,'height':780},device_scale_factor=2,record_video_dir=vd,record_video_size={'width':390,'height':780})
        pg=await ctx.new_page(); errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.add_init_script("try{localStorage.setItem('kugidama-test','1');localStorage.removeItem('kugidama-test-v1')}catch(_){}")
        await pg.goto('file://'+os.path.join(HERE,'game.html'))
        n=[0]
        async def shot(name,ms=0):
            if ms: await pg.wait_for_timeout(ms)
            if SHOTS:
                os.makedirs(os.path.join(HERE,'animshots'),exist_ok=True); n[0]+=1
                await pg.screenshot(path=os.path.join(HERE,'animshots',f'{n[0]:02d}_{name}.png'))
        await shot('title_drop',350); await shot('title',1300)
        await pg.click('#startBtn'); await shot('wipe',120); await shot('hub_in',260); await pg.wait_for_timeout(700)
        for t in ['ball','tower']:
            await pg.click(f'#tabs [data-tab="{t}"]'); await shot('tab_'+t,150); await pg.wait_for_timeout(750)
        # 玉を 買う
        await pg.click('#tabs [data-tab="ball"]'); await pg.wait_for_timeout(700)
        await pg.click('#hubBody .card >> nth=1'); await shot('buy_open',160); await pg.wait_for_timeout(700)
        await pg.click('#buyYes'); await shot('buy_got',220); await pg.wait_for_timeout(1200)
        # セット
        await pg.click('#tabs [data-tab="set"]'); await shot('set_lid',260); await shot('set_in',500); await pg.wait_for_timeout(500)
        # 穴の 玉を 外して、持ち玉を タップで はめる（カチャッ）
        await pg.click('.foam .chamber.sp >> nth=0'); await pg.wait_for_timeout(600)
        await pg.click('.rack .pouch >> nth=1'); await shot('set_clack',240); await pg.wait_for_timeout(700)
        await pg.click('#tabs [data-tab="zukan"]'); await pg.wait_for_timeout(800)
        # 台へ
        await pg.click('#tabs [data-tab="board"]'); await shot('hall',300); await pg.wait_for_timeout(700)
        await pg.click('.slot.cur .cab'); await shot('sit',300); await shot('board_wipe',450); await shot('board_in',500); await pg.wait_for_timeout(1500)
        # 杭を タップ → タワーを 置く
        await pg.evaluate("()=>{const T=window.__T,G=T.G;const p=G.pegs.filter(p=>!p.fixed&&!p.tower)[4];T.openBuild(p)}")
        await shot('build_sheet',200); await pg.wait_for_timeout(600)
        await pg.click('#sheetBody .trow:not(.locked) .buy >> nth=0'); await shot('drop',90); await shot('spin',160); await shot('spin2',160); await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{const T=window.__T,G=T.G;const p=G.pegs.find(p=>p.tower);T.openInfo(p)}"); await shot('info',300); await pg.wait_for_timeout(600)
        await pg.click('#sheetClose'); await pg.wait_for_timeout(500)
        await pg.click('#backBtn'); await shot('quit',250); await pg.wait_for_timeout(500)
        await pg.click('#quitYes'); await shot('back_hub',150); await pg.wait_for_timeout(1200)
        print('errors',errs[:6])
        v=pg.video; await ctx.close(); path=await v.path(); os.replace(path,OUT); print('video',OUT)
        await b.close()
asyncio.run(main())
