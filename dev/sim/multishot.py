# いくつかの場面を撮って、横にならべた1枚にする。使い方: python3 multishot.py 出力.png "js1" "js2" ...（各 js のあと 700ms 待って撮る）
import asyncio, sys, os
from playwright.async_api import async_playwright
from PIL import Image
async def main():
    out=sys.argv[1]; steps=sys.argv[2:]; shots=[]
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg=await b.new_page(viewport={'width':390,'height':780},device_scale_factor=1.5)
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.add_init_script("try{localStorage.setItem('kugidama-test','1')}catch(_){}")
        await pg.goto('file://'+os.path.join(os.path.dirname(os.path.abspath(__file__)),'game.html'))
        await pg.wait_for_timeout(1500)
        for i,js in enumerate(steps):
            await pg.evaluate(js); await pg.wait_for_timeout(700)
            f=f'{out}.{i}.png'; await pg.screenshot(path=f); shots.append(f)
        print('errors',errs[:6]); await b.close()
    ims=[Image.open(f) for f in shots]; w=sum(i.width for i in ims)+12*(len(ims)-1); h=max(i.height for i in ims)
    c=Image.new('RGB',(w,h),(255,255,255)); x=0
    for i in ims: c.paste(i,(x,0)); x+=i.width+12
    c.thumbnail((2400,2400)); c.save(out); [os.remove(f) for f in shots]
asyncio.run(main())
