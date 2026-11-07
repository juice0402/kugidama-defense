(()=>{   // Canvaのおばけの絵を 台に ならべて 見る（__STAGE__ を 台の番号に かえて shot.py に わたす。先に mk.py）
const T=window.__T,G=T.G,s=__STAGE__;
T.playBoard(T.BOARDS.findIndex(b=>b.stage===s)); G.paused=false; G.spawnQ=[]; G.banners=[];
G.en=[]; if(G.pend) G.pend.length=0;
const foes=T.STAGES[s].foes||[]; const list=[...foes];
const pos=[[70,170],[180,170],[290,170],[80,300],[230,300],[100,450],[260,450],[180,560],[300,560]];
const out=[];
list.forEach((t,i)=>{const [x,y]=pos[i];const e=T.addEnemy(t,x,y);e.sp=0;out.push(t)});
// かえ絵：同じ おばけを もう1つ（状態をかえて）
const extra={0:[['kakashi',{hatGone:true}],['tanuki',{leaf:false}]],1:[['hari',{curl:2}],['kuma',{lick:1}],['kuma',{potGone:1}]]}[s]||[];
extra.forEach(([t,st],j)=>{const [x,y]=pos[list.length+j];const e=T.addEnemy(t,x,y);e.sp=0;Object.assign(e,st);out.push(t+JSON.stringify(st))});
for(const e of G.en){e.sp=0;e.vy=0;e.born=1}
G.paused=false; G.spawnQ=[]; G.banners=[];
return new Promise(r=>setTimeout(()=>{G.banners=[];r(out.join(' '))},900));
})()
