// 9台を FEVER（5ウェーブ）と ボス戦で 遊ばせて、描く関数ごとの 1コマの命令の数（ops）と 時間を出す（mkprof.py の game_p2.html で開く。11/7）
(async()=>{const T=window.__T,G=T.G,W=window;
window.requestAnimationFrame=()=>0; await new Promise(r=>setTimeout(r,150));
G.cleared=[0,1,2,3,4,5,6,7,8];G.bought=[0,1,2,3,4,5,6,7,8];
const boards=(W.__BOARDS||[0,1,2,3,4,5,6,7,8]), out={};
const bk=(O,b)=>Object.keys(O).filter(k=>(O[k].board||0)===b);
function measure(N,fev){
  W.__P2reset();W.__P2=1;let js=0;
  for(let i=0;i<N;i++){if(fev)G.fever=8;G.life=10;T.update(1/60);T.updateFx(1/60);G.time+=1/60;const a=performance.now();T.draw();js+=performance.now()-a}
  W.__P2=0;
  let tot=0;const rows=[];for(const k in W.__AO){tot+=W.__AO[k];rows.push([k,W.__AO[k]/N,(W.__AT[k]||0)/N,(W.__AC[k]||0)/N])}
  rows.sort((a,b)=>b[1]-a[1]);
  return {ops:Math.round(tot/N),js:+(js/N).toFixed(2),en:G.en.length,fx:G.fx.length,zones:G.zones.length,obs:G.obs.length,bl:G.bl.length,
    top:rows.slice(0,14).map(r=>r[0]+' '+Math.round(r[1])+'/'+r[2].toFixed(2)+'ms×'+Math.round(r[3]))};
}
for(const b of boards){
  T.playBoard(b); G.balls=99999; G.banners=[]; G.paused=false;
  const nb=bk(T.BALLS,b).filter(k=>k!=='normal'), nt=bk(T.TOWERS,b).filter(k=>k!=='basic'), ng=bk(T.GIMMICKS,b);
  const deck=b===0?['fire','ice','bolt','poison','bb']:[nb[0],nb[1],nb[0],nb[1],'fire'];
  G.deck=deck;
  const tw=b===0?['fire','ice','bolt','poison','basic','long']:[nt[0],nt[1],'fire','ice',nt[0],nt[1]];
  G.pegs.forEach((p,i)=>{p.tower=T.newTower(tw[i%tw.length],p);if(i%2===0)p.tower.gm=(b===0?(i%4?'bumper':'spinner'):ng[0])});
  let g=0;while(G.wave<5&&g<60*240){G.life=10;if(G.wave>=3)G.fever=8;T.update(1/60);T.updateFx(1/60);G.time+=1/60;g++}
  for(let i=0;i<60*5;i++){G.life=10;G.fever=8;T.update(1/60);T.updateFx(1/60);G.time+=1/60}
  const A=measure(90,1);
  G.fever=0;G.en=[];G.pend=[];G.portals=[];G.spawnQ=[];T.startWave(10);
  for(let i=0;i<60*12;i++){G.life=10;T.update(1/60);T.updateFx(1/60);G.time+=1/60}
  const B=measure(90,0);
  out[T.STAGES[b].name]={deck:deck.join(','),tw:tw.join(','),FEVER5:A,BOSS:B};
}
return JSON.stringify(out)})()
