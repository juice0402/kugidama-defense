# BGM を はやく描きだして（ふだん→FEVER→中ボス→FEVER→ボス）、1秒ごとの いちばん大きい音と ならした大きさを出す。効果音は 0.03〜0.08 くらい
import asyncio, json, sys, os
from playwright.async_api import async_playwright
SONGS=sys.argv[1].split(',')
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch()
        pg=await b.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e))); pg.on('console',lambda m:errs.append(m.text) if m.type=='error' else None)
        await pg.goto('file://'+os.path.join(os.path.dirname(os.path.abspath(__file__)),'bgm.html'))
        for k in SONGS:
            once=k in('clear','over','unlock')
            plan=[] if once else [{'t':0,'mode':0,'fv':False},{'t':16,'fv':True},{'t':24,'fv':False},{'t':28,'mode':1},{'t':40,'fv':True},{'t':48,'fv':False},{'t':52,'mode':2}]
            dur=5 if once else 62
            r=await pg.evaluate('([k,p,d])=>window.__render(k,p,d)',[k,plan,dur])
            sec=r['sec']
            def seg(a,b):
                xs=sec[a:b]; return max(x[0] for x in xs), round(sum(x[1] for x in xs)/len(xs),4)
            bad=sum(x[2] for x in sec)
            if once: print(f"{k:8} peak/rms {seg(0,4)} nodes {r['nodes']} bad {bad}")
            else: print(f"{k:8} normal {seg(1,16)} fever {seg(17,24)} mid {seg(30,40)} midFV {seg(41,48)} boss {seg(54,62)} nodes/s {r['nodes']/dur:.0f} bad {bad}")
        print('errors',errs[:5])
        await b.close()
asyncio.run(main())
