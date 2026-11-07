# タブを切りかえたときの、メインスレッドの内わけ（CPU を遅くして）
import asyncio, sys, os
from playwright.async_api import async_playwright
RATE=float(sys.argv[1]) if len(sys.argv)>1 else 6
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg=await b.new_page(viewport={'width':390,'height':780},device_scale_factor=2)
        await pg.add_init_script("try{localStorage.setItem('kugidama-test','1')}catch(_){}")
        cdp=await pg.context.new_cdp_session(pg)
        await pg.goto('file://'+os.path.join(os.path.dirname(os.path.abspath(__file__)),'game.html'))
        await pg.wait_for_timeout(1500)
        await pg.evaluate("()=>__T.openHub('board')"); await pg.wait_for_timeout(1500)
        await cdp.send('Performance.enable'); await cdp.send('Emulation.setCPUThrottlingRate',{'rate':RATE})
        for t in ['ball','board','set','board']:
            a={x['name']:x['value'] for x in (await cdp.send('Performance.getMetrics'))['metrics']}
            await pg.evaluate(f"()=>__T.showTab('{t}')"); await pg.wait_for_timeout(700)
            z={x['name']:x['value'] for x in (await cdp.send('Performance.getMetrics'))['metrics']}
            d=lambda n:round((z[n]-a[n])*1000)
            print(t,'task',d('TaskDuration'),'script',d('ScriptDuration'),'style',d('RecalcStyleDuration'),'layout',d('LayoutDuration'))
        await b.close()
asyncio.run(main())
