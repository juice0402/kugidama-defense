# 使い方: python3 runsim.py 回数 '{"upTo":1}'   （先に python3 mk.py）。GAME=ほかの.html で、別に作ったページをためせる。SIM=econ.js で お金の記録（mkec.py）
import asyncio, sys, json, os
from playwright.async_api import async_playwright
here=os.path.dirname(os.path.abspath(__file__))
N=int(sys.argv[1]); opts=json.loads(sys.argv[2] if len(sys.argv)>2 else '{}')
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        pg=await b.new_page(viewport={'width':390,'height':780})
        errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        await pg.goto('file://'+os.path.join(here,os.environ.get('GAME','game.html'))); await pg.wait_for_timeout(500)
        js=open(os.path.join(here,os.environ.get('SIM','sim.js'))).read()
        for i in range(N):
            r=await pg.evaluate(f"({js})({json.dumps(opts)})")
            print(json.dumps(r,ensure_ascii=False),flush=True)
        print('errors',errs[:5])
        await b.close()
asyncio.run(main())
