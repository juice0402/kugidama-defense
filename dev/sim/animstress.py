# 動き（11/9）の いじわる テスト：すごく はやく タップ・動きの とちゅうで とじる・タブを れんだ・動きを へらす 設定
# おわったあと「見えない まま の 物」「止まった 動き」「のこった 部品」「エラー」が ないかを しらべる
# 使い方: python3 mk.py && python3 animstress.py [機種 375x667x2]
import asyncio, sys, os
from playwright.async_api import async_playwright
HERE=os.path.dirname(os.path.abspath(__file__))
W,H,D=[float(x) for x in (sys.argv[1] if len(sys.argv)>1 else '375x667x2').split('x')]
STATE=r"""(label)=>{const bad=[];const $=id=>document.getElementById(id);
  const vis=e=>e.checkVisibility?e.checkVisibility({visibilityProperty:true}):!!e.getClientRects().length;
  // 止まった 動き（くりかえし ではない のに まだ 動いている）
  for(const a of document.getAnimations()){const t=a.effect&&a.effect.getComputedTiming();if(a.playState==='running'&&t&&t.iterations!==Infinity&&t.endTime!==Infinity){const e=a.effect.target;bad.push('おわらない 動き '+(a.animationName||'js')+' '+(e&&(e.id||e.className)||''))}}
  // 見えている 画面の 中で opacity 0 の まま の ボタン・カード
  for(const e of document.querySelectorAll('button,.card,.slot,.chamber,.pouch,.trow,.lines li')){if(!vis(e))continue;let o=1;for(let a=e;a&&a!==document.body;a=a.parentElement)o*=+getComputedStyle(a).opacity;
    const r=e.getBoundingClientRect();if(r.width&&r.bottom>0&&r.top<innerHeight&&o<.05)bad.push('見えない まま '+(e.id||e.className)+' 「'+e.textContent.trim().slice(0,10)+'」')}
  // しまいかけ（.out）の まま の シート
  for(const e of document.querySelectorAll('#quit.out,#buy.out,#sheet.out,#testSheet.out')) if(!e.hidden) bad.push('しまいかけの まま '+(e.id||e.className));
  if(!$('wipe').hidden) bad.push('切りかえの 板が のこっている');
  const fly=document.querySelectorAll('.flycoin,.getpop,.spk').length; if(fly) bad.push('のこった 部品 '+fly);
  return {label,bad:[...new Set(bad)],state:window.__T.G.state,title:$('hubTitle').textContent,n:document.body.querySelectorAll('*').length}}"""
async def flow(b,reduced):
    ctx=await b.new_context(viewport={'width':int(W),'height':int(H)},device_scale_factor=D,has_touch=True,reduced_motion='reduce' if reduced else 'no-preference')
    pg=await ctx.new_page(); errs=[]; out=[]
    pg.on('pageerror',lambda e:errs.append(str(e)))
    await pg.goto('file://'+os.path.join(HERE,'game.html')); await pg.wait_for_timeout(1800)
    async def check(label,wait=1600):
        await pg.wait_for_timeout(wait); r=await pg.evaluate(STATE,label); out.append(r)
        print(('  [動きを へらす] ' if reduced else '  ')+f"{label}: {r['state']} 「{r['title']}」 部品{r['n']} "+('OK' if not r['bad'] else '× '+' / '.join(r['bad'])),flush=True)
    async def tap(sel,delay=0):
        try: await pg.click(sel,timeout=1500,delay=delay)
        except Exception as e: out.append({'label':'tap','bad':['タップ できない '+sel]}); print('  タップ できない',sel)
    # 1 スタートを 2回 れんだ
    await pg.click('#startBtn'); await pg.click('#startBtn',force=True,timeout=800) if await pg.is_visible('#startBtn') else None
    await check('スタート れんだ')
    await pg.evaluate("()=>{const T=window.__T;T.G.balls=99999;T.G.cleared=[0,1,2];T.G.bought=[0,1,2,3]}")
    # 2 タブを はやく 12回
    for t in ['ball','tower','gimmick','set','zukan','board','set','ball','zukan','tower','set','ball']:
        await tap(f'#tabs [data-tab="{t}"]'); await pg.wait_for_timeout(45)
    await check('タブ れんだ')
    ok=await pg.evaluate("()=>{const n=+getComputedStyle(document.getElementById('tsel')).getPropertyValue('--n');return n}")
    print('    えらんだ 光の 場所',ok,'(玉=1)')
    # 3 買う シート：カードを 2回 タップ（2回目は きかない＝買わない）→ 0.36秒で とじる ×5
    c0=await pg.evaluate("()=>window.__T.G.balls")
    for i in range(5):
        await tap('#hubBody .card >> nth=1'); await pg.wait_for_timeout(60); await pg.click('#buyYes',force=True,timeout=800)
        await pg.wait_for_timeout(300); await tap('#buyNo'); await pg.wait_for_timeout(30)
    c1=await pg.evaluate("()=>window.__T.G.balls"); print('    2回 タップで 買って しまわない？',c0==c1)
    await check('買う シート 出し入れ れんだ')
    # 4 買う → すぐ べつの タブ
    await tap('#hubBody .card >> nth=1'); await pg.wait_for_timeout(380); await tap('#buyYes'); await pg.wait_for_timeout(60); await tap('#tabs [data-tab="set"]')
    await check('買って すぐ セットへ')
    # 5 セット：はずす・はめる を はやく
    for i in range(6):
        await tap('.foam .chamber.sp >> nth=0'); await pg.wait_for_timeout(40)
        await tap('.rack .pouch >> nth=1'); await pg.wait_for_timeout(40)
    await check('セット れんだ')
    d=await pg.evaluate("()=>[window.__T.G.deck.length,document.querySelectorAll('.foam .chamber').length]"); print('    セットの 数',d)
    # 6 台へ：台を 2回 タップ
    await tap('#tabs [data-tab="board"]'); await pg.wait_for_timeout(700)
    await tap('.slot.cur .cab'); await pg.wait_for_timeout(60)
    if await pg.is_visible('.slot.cur .cab'): await pg.click('.slot.cur .cab',force=True,timeout=800)
    await check('台へ れんだ',2600)
    # 7 タワーを つぎつぎ 置く → すぐ 中身
    await pg.evaluate("""()=>{const T=window.__T,G=T.G;G.balls=99999}""")
    for i in range(4):
        await pg.evaluate(f"()=>{{const T=window.__T,G=T.G;const p=G.pegs.filter(p=>!p.fixed&&!p.tower)[{i}];T.openBuild(p)}}"); await pg.wait_for_timeout(60)
        await pg.wait_for_timeout(360); await tap('#sheetBody .trow:not(.locked) .buy >> nth=0'); await pg.wait_for_timeout(50)
    await pg.evaluate("()=>{const T=window.__T,G=T.G;const p=G.pegs.find(p=>p.tower);T.openInfo(p)}"); await pg.wait_for_timeout(380); await tap('#sheetClose')
    await check('タワー つぎつぎ',1800)
    lands=await pg.evaluate("()=>window.__T.G.pegs.filter(p=>p.tower).map(p=>+(p.tower.land||0).toFixed(2))"); print('    タワーの 着地 のこり',lands)
    # 8 もどる：2回 れんだ → つづける → もどる → やめる
    await tap('#backBtn'); await pg.click('#backBtn',force=True,timeout=800); await pg.wait_for_timeout(60)
    print('    もどる 2回で シートが のこる？',await pg.evaluate("()=>!document.getElementById('quit').hidden&&!document.getElementById('quit').classList.contains('out')"))
    await pg.wait_for_timeout(320); await tap('#quitNo'); await pg.wait_for_timeout(40)
    await check('もどる れんだ → つづける',900)
    paused=await pg.evaluate("()=>window.__T.G.paused"); print('    止まって いない？',not paused)
    await tap('#backBtn'); await pg.wait_for_timeout(380); await tap('#quitYes')
    await check('やめて もどる')
    # 9 結果画面の ボタン れんだ
    await pg.evaluate("()=>{const T=window.__T;T.playBoard(0);T.gameOver()}"); await pg.wait_for_timeout(900)
    await tap('#resBtn');
    if await pg.is_visible('#resBtn'): await pg.click('#resBtn',force=True,timeout=800)
    await check('結果 れんだ',2000)
    # 10 とちゅうで 画面を かくす（アプリを 切りかえ）→ もどす
    await pg.evaluate("()=>{const T=window.__T;T.openHub('ball')}"); await pg.wait_for_timeout(120)
    await pg.evaluate("()=>{Object.defineProperty(document,'hidden',{configurable:true,get:()=>true});document.dispatchEvent(new Event('visibilitychange'))}"); await pg.wait_for_timeout(600)
    await pg.evaluate("()=>{Object.defineProperty(document,'hidden',{configurable:true,get:()=>false});document.dispatchEvent(new Event('visibilitychange'))}")
    await check('かくして もどす')
    await ctx.close()
    return out,errs
async def main():
    async with async_playwright() as p:
        b=await p.chromium.launch(executable_path='/usr/bin/google-chrome')
        bad=0
        for red in [False,True]:
            print('動きを へらす 設定' if red else 'ふつう',flush=True)
            out,errs=await flow(b,red)
            bad+=sum(len(o['bad']) for o in out)+len(errs)
            if errs: print('  エラー',errs[:5])
        print('のこった もんだい',bad)
        await b.close()
asyncio.run(main())
