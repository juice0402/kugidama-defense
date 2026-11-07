# 弾薬箱をさわってみる（タップ・長おしドラッグ・穴から穴・外へ）。使い方: python3 ammotest.py 出力.png
import asyncio, sys, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg=await b.new_page(viewport={'width':390,'height':780},device_scale_factor=1.5)
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.add_init_script("try{localStorage.setItem('kugidama-test','1')}catch(_){}")
        await pg.goto('file://'+os.path.join(os.path.dirname(os.path.abspath(__file__)),'game.html'))
        await pg.wait_for_timeout(1200)
        await pg.evaluate("()=>{__T.G.deck=['normal','normal','normal','fire','ice'];__T.openHub('set')}"); await pg.wait_for_timeout(400)
        deck=lambda: pg.evaluate("()=>__T.G.deck.join(',')")
        async def c(sel): 
            r=await pg.locator(sel).first.bounding_box(); return r['x']+r['width']/2, r['y']+r['height']/2
        async def tap(sel):
            x,y=await c(sel); await pg.mouse.move(x,y); await pg.mouse.down(); await pg.wait_for_timeout(60); await pg.mouse.up(); await pg.wait_for_timeout(450)
        async def drag(a,bsel,hold=260,shot=None):
            x,y=await c(a); X,Y=await c(bsel); await pg.mouse.move(x,y); await pg.mouse.down(); await pg.wait_for_timeout(hold)
            for i in range(1,9): await pg.mouse.move(x+(X-x)*i/8,y+(Y+18-y)*i/8); await pg.wait_for_timeout(16)
            if shot: await pg.screenshot(path=shot)
            await pg.mouse.up(); await pg.wait_for_timeout(450)
        await tap('.pouch[data-k="bb"]'); print('BBをタップ', await deck())
        await tap('.chamber[data-i="3"]'); print('穴4をタップ', await deck())
        await drag('.pouch[data-k="bolt"]','.chamber[data-i="4"]',shot=sys.argv[1]); print('雷弾を穴5へ', await deck())
        await drag('.chamber[data-i="0"]','.chamber[data-i="2"]',hold=30); print('穴1→穴3', await deck())
        await drag('.chamber[data-i="2"]','.sect',hold=30); print('穴3を外へ', await deck())
        x,y=await c('.pouch[data-k="lead"]'); await pg.mouse.move(x,y); await pg.mouse.down(); await pg.mouse.move(x,y-60,steps=4); await pg.mouse.up(); await pg.wait_for_timeout(300)
        print('すぐ動かした（何もしない）', await deck())
        print('errors',errs[:5]); await b.close()
asyncio.run(main())
