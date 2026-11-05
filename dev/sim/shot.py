import asyncio, sys
from playwright.async_api import async_playwright
JS=sys.argv[2] if len(sys.argv)>2 else ''
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome',args=['--autoplay-policy=no-user-gesture-required'])
        pg=await b.new_page(viewport={'width':390,'height':780},device_scale_factor=1.5)
        errs=[]
        pg.on('pageerror',lambda e:errs.append(str(e)))
        pg.on('console',lambda m: errs.append('console:'+m.text) if m.type=='error' else None)
        await pg.goto('file://'+__import__('os').path.join(__import__('os').path.dirname(__import__('os').path.abspath(__file__)),'game.html'))
        await pg.wait_for_timeout(600)
        r=await pg.evaluate(JS) if JS else None
        await pg.wait_for_timeout(int(sys.argv[3]) if len(sys.argv)>3 else 300)
        await pg.screenshot(path=sys.argv[1])
        print('result',r); print('errors',errs[:8])
        await b.close()
asyncio.run(main())
