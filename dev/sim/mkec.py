# お金の流れを数える game_ec.html を作る（先に mk.py）。G.ec に 入ったコイン（kill おばけ・fev FEVER・wave ウェーブクリア・halo 光の輪・clear クリア）と 出たコイン（shot 1発）を足していく
# 使い方: python3 mk.py; python3 mkec.py; GAME=game_ec.html SIM=econ.js python3 runsim.py 4 '{"from":3,"upTo":3,"coins":0,"tries":8}' > e.txt; python3 econstat.py e.txt
import os
here=os.path.dirname(os.path.abspath(__file__))
s=open(os.path.join(here,'game.html'),encoding='utf-8').read()
R=[("e.dead=true; const r=E.reward; G.balls+=r;","e.dead=true; const r=E.reward; G.balls+=r; if(G.ec)G.ec.kill+=r;"),
("if(G.fever>0){G.balls+=FEVER_HIT;","if(G.fever>0){G.balls+=FEVER_HIT; if(G.ec)G.ec.fev+=FEVER_HIT;"),
("G.feverPay--;G.balls++}}","G.feverPay--;G.balls++;if(G.ec)G.ec.fev++}}"),
("if(G.fever<=0){G.fever=0;G.balls+=G.feverPay;G.feverPay=0}","if(G.fever<=0){G.fever=0;G.balls+=G.feverPay;if(G.ec)G.ec.fev+=G.feverPay;G.feverPay=0}"),
("G.waveGap=2.5;G.balls+=15;","G.waveGap=2.5;G.balls+=15;if(G.ec)G.ec.wave+=15;"),
("G.balls+=HALO.coin;","G.balls+=HALO.coin;if(G.ec)G.ec.halo+=HALO.coin;"),
("const bonus=30+G.life*3; G.balls+=bonus;","const bonus=30+G.life*3; G.balls+=bonus; if(G.ec)G.ec.clear+=bonus;"),
("G.state='over'; tutStop(); closeSheet(); G.balls+=G.feverPay;","G.state='over'; tutStop(); closeSheet(); G.balls+=G.feverPay; if(G.ec)G.ec.fev+=G.feverPay;"),
("  G.balls--;\n","  G.balls--; if(G.ec)G.ec.shot++;\n")]
R+=[("e.dead=true; const r=killCoin(E); G.balls+=r;","e.dead=true; const r=killCoin(E); G.balls+=r; if(G.ec)G.ec.kill+=r;")]   # 11/11 から（おばけの コインは killCoin）
for a,b in R:
    n=s.count(a)
    if n==0: continue   # 11/11 から：玉・FEVER・ウェーブ・クリア・光の輪の コインは もう ない
    assert n==1,('2つある：',a); s=s.replace(a,b)
assert 'G.ec.kill+=' in s,'おばけの コインが 見つからない'
open(os.path.join(here,'game_ec.html'),'w',encoding='utf-8').write(s); print('game_ec.html ok')
