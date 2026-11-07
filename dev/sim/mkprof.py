# game.html → game_p2.html：描く関数ごとに キャンバスの命令の数と時間を はかる（入れ子は 自分の分だけ）。使い方：python3 mk.py; python3 mkprof.py game.html game_p2.html; perf.py で prof9.js を開く
import sys,re
src,dst=sys.argv[1],sys.argv[2]
s=open(src,encoding='utf-8').read()
names=sorted(set(re.findall(r"^function ((?:draw|ghost)\w*|glow|glowIn|fxFlush|blit|layerOn|layerOff)\(",s,re.M)))
names=[n for n in names if n not in ('ghostMood',)]
w="""
(()=>{const W=window;W.__AT={};W.__AO={};W.__AC={};let st=[],ops=0;
const C=CanvasRenderingContext2D.prototype;
for(const m of ['drawImage','fill','stroke','fillRect','strokeRect','fillText','strokeText','clip','createRadialGradient','createLinearGradient','putImageData','getImageData']){const o=C[m];C[m]=function(...a){if(W.__P2&&m!=='getImageData')ops++;return o.apply(this,a)}}
function en(l){if(!W.__P2)return;const n=performance.now();if(st.length){const p=st[st.length-1];W.__AT[p.l]=(W.__AT[p.l]||0)+n-p.t;W.__AO[p.l]=(W.__AO[p.l]||0)+ops-p.o}st.push({l,t:n,o:ops});W.__AC[l]=(W.__AC[l]||0)+1}
function ex(){if(!W.__P2||!st.length)return;const n=performance.now(),p=st.pop();W.__AT[p.l]=(W.__AT[p.l]||0)+n-p.t;W.__AO[p.l]=(W.__AO[p.l]||0)+ops-p.o;if(st.length){const q=st[st.length-1];q.t=n;q.o=ops}}
W.__P2reset=()=>{st=[];ops=0;for(const o of [W.__AT,W.__AO,W.__AC])for(const k in o)delete o[k]};
const wr=(f,l)=>function(...a){en(l);try{return f.apply(this,a)}finally{ex()}};
const wo=(O,pre,hs)=>{for(const k in O){const D=O[k];if(!D||typeof D!=='object')continue;for(const h of hs)if(typeof D[h]==='function')D[h]=wr(D[h],pre+k+'.'+h)}};
wo(ZONES,'zone:',['draw']);wo(OBJK,'obj:',['back','draw','top']);wo(BULLETK,'bul:',['draw']);wo(FXK,'fx:',['draw','glow']);wo(ELEM,'mark:',['mark']);
wo(SPECIAL,'sp:',['under','over']);wo(COMBO,'combo:',['under','over']);wo(TLOCK,'lock:',['draw']);wo(ENEMIES,'en:',['back','front','top','skin','alt']);wo(GIMMICKS,'gm:',['draw','over','under']);wo(TOWERS,'tw:',['over','under','draw']);
STAGES.forEach((S,i)=>{for(const h of ['drawBack','drawFront'])if(typeof S[h]==='function')S[h]=wr(S[h],'stage'+i+'.'+h)});
%s
})();
""" % "\n".join("try{%s=wr(%s,'%s')}catch(_){}"%(n,n,n) for n in names)
i=s.find("window.__T={};")
assert i>0
s=s[:i]+w+s[i:]
open(dst,'w',encoding='utf-8').write(s); print('p2 ok',len(names))
