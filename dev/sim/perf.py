# ページを開いて js を1つ実行し、結果を出す（スマホくらいの画面・dpr 2）。使い方: python3 perf.py game_p2.html prof9.js
import asyncio, sys, os
from playwright.async_api import async_playwright
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg=await b.new_page(viewport={'width':390,'height':780},device_scale_factor=2)
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+os.path.abspath(sys.argv[1]))
        await pg.wait_for_timeout(600)
        print(await pg.evaluate(open(sys.argv[2],encoding='utf-8').read())); print('errors',errs[:4])
        await b.close()
asyncio.run(main())
