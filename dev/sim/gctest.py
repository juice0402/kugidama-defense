# Game Center（11/26）：アプリの 中と おなじ 形で、実績（APP_ACHIEVE）と ランキング（APP_SCORE）が よばれるかを ためす
#  1) セーブなしで 開くと 何も 送らない  2) タワー・杭まんたん・FEVER・図鑑・おばけ1000体・クリア・ノーダメージ で 実績
#  3) 開きなおすと、とった 実績と セーブから わかる 分を 全部 送りなおす  4) 'app-gamecenter' でも 送りなおす
#  5) 送った id が ぜんぶ docs/kobo/gamecenter.json に ある
# 使い方: python3 mk.py && python3 gctest.py
import asyncio, os, json
from playwright.async_api import async_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
GCJ=json.load(open(os.path.join(HERE,'..','..','docs','kobo','gamecenter.json'),encoding='utf-8'))
IDS={a['id'] for a in GCJ['achievements']}
INIT="""window.APP_LANGS=['ja'];window.APP_PLATFORM='ios';window.APP_ZOOM=1;window.APP_HAPTIC=()=>{};
window.__ach=[];window.__score=[];window.APP_ACHIEVE=id=>window.__ach.push(id);window.APP_SCORE=n=>window.__score.push(n);
Object.defineProperty(navigator,'webdriver',{get:()=>false});"""
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        ctx=await b.new_context(viewport={'width':393,'height':852},device_scale_factor=1,has_touch=True)
        await ctx.add_init_script(INIT)
        pg=await ctx.new_page(); errs=[]; pg.on('pageerror',lambda e:errs.append(str(e)))
        url='file://'+os.path.join(HERE,'game.html')
        ok=lambda c,m:print(('OK  ' if c else 'NG  ')+m,flush=True)
        got=lambda: pg.evaluate("()=>[window.__ach.slice(),window.__score.slice()]")
        await pg.goto(url); await pg.wait_for_timeout(1200)
        a,s=await got(); ok(a==[] and s==[],f'セーブなしで 開くと 送らない {a} {s}')
        await pg.click('#startBtn'); await pg.wait_for_timeout(900)
        await pg.evaluate("()=>{window.__T.G.balls=99999}")
        await pg.click('.slot.cur .cab'); await pg.wait_for_timeout(2500)
        await pg.click('#tutSkip'); await pg.wait_for_timeout(400)
        # タワー → 杭まんたん
        for i in range(14):
            n=await pg.evaluate("()=>{const T=window.__T,G=T.G;const p=G.pegs.find(p=>!p.fixed&&!p.tower);if(!p)return 0;T.openBuild(p);return 1}")
            if not n: break
            await pg.wait_for_timeout(250); await pg.click('#sheetBody .trow:not(.locked) .buy >> nth=0'); await pg.wait_for_timeout(250)
        a,_=await got(); ok('pachi_first_tower' in a and 'pachi_full_pegs' in a,f'タワー・杭まんたん {a}')
        # FEVER（ヘソ）・図鑑・おばけ1000体
        await pg.evaluate("()=>{const T=window.__T,G=T.G;T.heso(G.heso||{x:188,y:480},{t:'normal'})}")
        await pg.evaluate("()=>{const T=window.__T;let n=0;for(const k of T.EL_ORDER){T.markFound('sp:'+k);if(++n>=29)break}while(n<29)T.markFound('sp:test'+(n++))}")
        a,_=await got(); ok('pachi_first_fever' in a and 'pachi_found_30' not in a and 'pachi_first_combo' not in a,f'FEVER・特殊効果29こ {a}')
        await pg.evaluate("()=>{const T=window.__T,E=T.EL_ORDER;T.markFound(E[0]+'+'+E[1])}")
        a,_=await got(); ok('pachi_first_combo' in a and 'pachi_found_30' in a,'技1つで はじめての技・30こ')
        await pg.evaluate("()=>{const T=window.__T,G=T.G;G.kills=999;T.startWave(1);for(let i=0;i<60*40&&G.kills<1000;i++){G.life=10;T.update(1/60);T.updateFx(1/60);G.time+=1/60}}")
        a,_=await got(); k=await pg.evaluate("()=>window.__T.G.kills"); ok('pachi_kills_1000' in a,f'おばけ1000体（kills {k}）')
        # クリア（ライフが 減っていない）
        await pg.evaluate("()=>{const T=window.__T;T.G.hurt=false;T.G.wave=10;T.stageClear()}"); await pg.wait_for_timeout(1200)
        a,s=await got(); ok('pachi_clear_meadow' in a and 'pachi_no_damage' in a and s and s[-1]>=1000,f'クリア・ノーダメージ・記録 {s[-1:]}')
        bad=[x for x in a if x not in IDS]; ok(not bad,f'送った id は gamecenter.json に ある {bad}')
        ok(len(a)==len(set(a)),'同じ 実績を 2回 送らない（台の 中）')
        # 開きなおし → 送りなおし（セーブの ach＋セーブから わかる 分）
        sv=await pg.evaluate("()=>{for(const k of Object.keys(localStorage)) if(/kugidama-save/.test(k)) return JSON.parse(localStorage.getItem(k)).ach}")
        ok(set(a)<=set(sv or []),f'セーブに ach が のこる {len(sv or [])}')
        await pg.reload(); await pg.wait_for_timeout(1200)
        a2,s2=await got(); ok(set(a)<=set(a2) and s2 and s2[-1]>=1000,f'開いたときに 送りなおす（{len(a2)}こ・記録 {s2[-1:]}）')
        await pg.evaluate("()=>{window.__ach=[];window.__score=[];window.dispatchEvent(new Event('app-gamecenter'))}"); await pg.wait_for_timeout(300)
        a3,s3=await got(); ok(set(a)<=set(a3) and s3,f"'app-gamecenter' で 送りなおす（{len(a3)}こ）")
        # 前から あそんでいる セーブ（ach なし）：クリアと 図鑑と kills から わかる 分
        await pg.evaluate("""()=>{const T=window.__T;for(const k of Object.keys(localStorage)) if(/kugidama-save/.test(k)){const s=JSON.parse(localStorage.getItem(k));
          delete s.ach;s.cleared=[0,1,2,3,4,5,6,7,8];s.kills=5000;const f=[];for(const a of T.EL_ORDER){f.push('sp:'+a);for(const b2 of T.EL_ORDER) if(a<b2) f.push(a+'+'+b2)}s.found=f;localStorage.setItem(k,JSON.stringify(s))}}""")
        await pg.reload(); await pg.wait_for_timeout(1200)
        a4,_=await got(); need={'pachi_'+x for x in ['first_tower','first_combo','clear_meadow','clear_mansion','clear_snow','clear_volcano','clear_heaven','kills_1000','found_30','found_100','found_all']}
        ok(need<=set(a4),f'前からの セーブでも わかる 分を 送る（たりない {sorted(need-set(a4))}）')
        ok(not errs,f'エラー {errs[:3]}')
        await b.close()
asyncio.run(main())
