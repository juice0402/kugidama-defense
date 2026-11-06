# econ.js の出力をまとめる：台ごとに 終わりのコインのまん中（1回目・負け・クリア）・入ったときのコイン・クリアまでの回数
import json,sys,statistics as st
rows=[json.loads(l) for l in open(sys.argv[1],encoding='utf-8') if l.startswith('{')]
agg={}
for r in rows:
    for nm,games in r.items():
        A=agg.setdefault(nm,{'c1':[],'first':[],'loss':[],'clear':[],'tries':[],'cin':[]})
        gs=[g for g in games if isinstance(g,dict) and not g['r'].startswith('稼ぎ')]
        ci=next((i for i,g in enumerate(gs) if g['r']=='C'),None); A['tries'].append(99 if ci is None else ci+1)
        for i,g in enumerate(gs):
            A['c1'].append(g['c1']); A['cin'].append(g['cIn'])
            (A['clear'] if g['r']=='C' else A['first'] if i==0 else A['loss']).append(g['c1'])
md=lambda v: round(st.median(v)) if v else '-'
for nm,A in agg.items():
    print(f"{nm}: 終わりのコイン まん中{md(A['c1'])}（1回目{md(A['first'])}・負け{md(A['loss'])}・クリア{md(A['clear'])}） 入る{md(A['cin'])} クリアまで{sorted(A['tries'])}")
