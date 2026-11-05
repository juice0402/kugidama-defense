# runsim の出力をまとめる：台ごとに 1回目の失敗率・クリアまでの回数（まん中・平均・分布）・ボス戦の長さ（bt:true のとき。秒のまん中）
# 使い方: python3 runsim.py 40 '{"upTo":2,"bt":true}' > out.txt; python3 stat.py out.txt   （99＝tries 回でクリアできなかった）
import sys, json, re, statistics as st
lines = open(sys.argv[1], encoding='utf-8').read().splitlines() if len(sys.argv) > 1 else sys.stdin.read().splitlines()
rows = [json.loads(l) for l in lines if l.startswith('{')]
names = []
for r in rows:
    for k in r:
        if k not in names: names.append(k)
md = lambda v: round(st.median(v)) if v else '-'
for nm in names:
    first, clr, bt, btw, btl, over = [], [], [], [], [], 0
    for r in rows:
        a = [x for x in r.get(nm, []) if x[:1] in 'wC']        # 稼ぎ・set は数えない
        if not a: continue
        first.append(not a[0].startswith('C'))
        ci = next((i for i, x in enumerate(a) if x.startswith('C')), None)
        clr.append(99 if ci is None else ci + 1)
        for x in a:
            m = re.search(r'/b(\d+)(\+?)', x)
            if not m: continue
            v = int(m.group(1)); bt.append(v); over += bool(m.group(2))
            (btw if x.startswith('C') else btl).append(v)
    n = len(first)
    if not n: continue
    dist = {c: clr.count(c) for c in sorted(set(clr))}
    ok = [c for c in clr if c < 99]
    s = f"{nm}: {n}回 1回目の失敗{100*sum(first)//n}% クリアまで まん中{st.median(clr)}回目 平均{st.mean(ok) if ok else 0:.1f} {dist}"
    if bt: s += f" ボス戦 まん中{md(bt)}秒（勝ち{md(btw)}・負け{md(btl)}）" + (f" 時間切れ{over}" if over else '')
    print(s)
