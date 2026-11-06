# runsim の出力（prof:true）をまとめる：台ごとに 1回目の「どのウェーブで負けたか」・1〜4ウェーブの ざこが来た深さ（0＝出た所 1＝受け皿）・中ボスを倒すまでの秒
# 使い方: python3 runsim.py 12 '{"from":3,"prof":true,"bt":true}' > out.txt; python3 prof.py out.txt   （stat.py と いっしょに見る）
import sys, json, re, statistics as st
rows=[json.loads(l) for l in open(sys.argv[1],encoding='utf-8') if l.startswith('{')]
names=[]
for r in rows:
    for k in r:
        if k not in names: names.append(k)
for nm in names:
    fw, d1, dall, m1, mall = [], [[] for _ in range(4)], [[] for _ in range(4)], [], []
    for r in rows:
        a=[x for x in r.get(nm,[]) if x[:1] in 'wC']
        for i,x in enumerate(a):
            g=re.search(r'#d=([^#]*)#m=(\S+)',x)
            if not g: continue
            ds=g.group(1).split(','); m=g.group(2)
            for j,v in enumerate(ds[:4]):
                if v!='-': (dall[j]).append(float(v)); (d1[j].append(float(v)) if i==0 else None)
            if m not in '-': (mall.append(m)); (m1.append(m) if i==0 else None)
            if i==0: fw.append('C' if x.startswith('C') else re.match(r'w(\d+)',x).group(1))
    if not fw: continue
    mean=lambda v: f"{st.mean(v):.2f}" if v else '-'
    def mt(v):
        k=[int(x) for x in v if x!='+']; return f"まん中{st.median(k):.0f}秒" if k else '-'
    print(f"{nm}: 1回目の結果 {dict(sorted({w:fw.count(w) for w in set(fw)}.items()))}")
    print(f"  ざこの深さ(1回目) w1〜4: {' '.join(mean(v) for v in d1)}  （全部の回: {' '.join(mean(v) for v in dall)}）")
    print(f"  中ボス 1回目 {mt(m1)}・倒せず{m1.count('+')}/{len(m1)}  全部の回 {mt(mall)}・倒せず{mall.count('+')}/{len(mall)}")
