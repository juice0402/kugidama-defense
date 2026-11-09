// 9台を FEVER（5ウェーブ）と ボス戦で 動かして、1コマの update と draw の 時間（JS）と、
// 台の キャンバスに 描いた ピクセルの 量（drawImage・fillRect の 画面の 広さ。スマホの GPU の しごとの めやす）を はかる（11/9 軽量化）
// 使い方：python3 perf.py game.html prof10.js
(async()=>{const T=window.__T,G=T.G,W=window;
window.requestAnimationFrame=()=>0; await new Promise(r=>setTimeout(r,150));
const cv=document.getElementById('cv');
const C=CanvasRenderingContext2D.prototype, dI=C.drawImage, fR=C.fillRect;
let area=0, big={}, on=false;
const tag=()=>{try{throw new Error()}catch(e){const s=e.stack.split('\n').slice(3,6).map(x=>(x.match(/at (\S+)/)||[])[1]).filter(Boolean);return s.find(n=>!/^(blit|glow|glowIn|Object\.|fxFlush|lazyLay|eval)/.test(n))||s[0]||'?'}};
C.drawImage=function(...a){if(on&&this.canvas===cv){const m=this.getTransform(), sx=Math.hypot(m.a,m.b), sy=Math.hypot(m.c,m.d);let w,h;
  if(a.length>=9){w=a[7];h=a[8]}else if(a.length>=5){w=a[3];h=a[4]}else{w=a[0].width;h=a[0].height}
  const A=Math.abs(w*h*sx*sy); area+=A; if(A>20000){const k=tag();big[k]=(big[k]||0)+A}}
  return dI.apply(this,a)};
C.fillRect=function(...a){if(on&&this.canvas===cv){const m=this.getTransform();area+=Math.abs(a[2]*a[3]*m.a*m.d)}return fR.apply(this,a)};
G.cleared=[0,1,2,3,4,5,6,7,8];G.bought=[0,1,2,3,4,5,6,7,8];
const boards=(W.__BOARDS||[0,1,2,3,4,5,6,7,8]), out={};
const bk=(O,b)=>Object.keys(O).filter(k=>(O[k].board||0)===b);
function measure(N,fev){
  let tu=0,td=0; area=0; big={};
  for(let i=0;i<N;i++){if(fev)G.fever=8;G.life=10;let a=performance.now();T.update(1/60);T.updateFx(1/60);G.time+=1/60;tu+=performance.now()-a;on=true;a=performance.now();T.draw();td+=performance.now()-a;on=false}
  const px=cv.width*cv.height, tops=Object.entries(big).sort((a,b)=>b[1]-a[1]).slice(0,5).map(([k,v])=>k+' '+(v/N/px).toFixed(2));
  return {up:+(tu/N).toFixed(2),draw:+(td/N).toFixed(2),fill:+(area/N/px).toFixed(2),en:G.en.length,fx:G.fx.length,bl:G.bl.length,tops};
}
for(const b of boards){
  T.playBoard(b); G.balls=99999; G.banners=[]; G.paused=false;
  const nb=bk(T.BALLS,b).filter(k=>k!=='normal'), nt=bk(T.TOWERS,b).filter(k=>k!=='basic'), ng=bk(T.GIMMICKS,b);
  G.deck=b===0?['fire','ice','bolt','poison','bb']:[nb[0],nb[1],nb[0],nb[1],'fire'];
  const tw=b===0?['fire','ice','bolt','poison','basic','long']:[nt[0],nt[1],'fire','ice',nt[0],nt[1]];
  G.pegs.forEach((p,i)=>{if(p.fixed)return;p.tower=T.newTower(tw[i%tw.length],p);p.r=Math.max(p.r,7);if(i%2===0)p.tower.gm=(b===0?(i%4?'bumper':'spinner'):ng[0])});
  T.buildStatic();
  let g=0;while(G.wave<5&&g<60*240){G.life=10;if(G.wave>=3)G.fever=8;T.update(1/60);T.updateFx(1/60);G.time+=1/60;g++}
  for(let i=0;i<60*5;i++){G.life=10;G.fever=8;T.update(1/60);T.updateFx(1/60);G.time+=1/60}
  const A=measure(120,1);
  G.fever=0;G.en=[];G.pend=[];G.portals=[];G.spawnQ=[];T.startWave(10);
  for(let i=0;i<60*12;i++){G.life=10;T.update(1/60);T.updateFx(1/60);G.time+=1/60}
  const B=measure(120,0);
  out[T.STAGES[b].name]={FEVER:A,BOSS:B};
}
return JSON.stringify(out)})()
