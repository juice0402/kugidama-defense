(()=>{   // Canvaのおばけの絵を 台に ならべて 見る（__STAGE__ を 台の番号に かえて shot.py に わたす。先に mk.py）
const T=window.__T,G=T.G,s=__STAGE__;
T.playBoard(T.BOARDS.findIndex(b=>b.stage===s)); G.paused=false; G.spawnQ=[]; G.banners=[];
G.en=[]; if(G.pend) G.pend.length=0;
const foes=T.STAGES[s].foes||[]; const list=[...foes];
const pos=[[70,130],[180,130],[290,130],[75,240],[200,240],[300,250],[80,345],[200,350],[300,350],[70,445],[180,450],[290,450]];
const out=[];
list.forEach((t,i)=>{const [x,y]=pos[i];const e=T.addEnemy(t,x,y);e.sp=0;out.push(t)});
// かえ絵：同じ おばけを もう1つ（状態をかえて）
const extra={0:[['kakashi',{hatGone:true}],['tanuki',{leaf:false}]],1:[['hari',{curl:2}],['kuma',{lick:1}],['kuma',{potGone:1}]],2:[['neko',{lives:0,fear:3}],['neko',{lives:0,revived:true,rush:3}],['koumori',{bp:'hang',bt:99}],['yoroi',{armorOff:9}],['fukurou',{wind:9}],['ookami',{howl:9}]],3:[['mia',{mp:'dig',mt:.4}],['tokage',{tail:false}],['tokage',{knot:true}],['rakuda',{hump:0}],['sasori',{aim:9}],['sasori',{clawStop:9}],['sphinx',{shield:9}]],4:[['okojo',{found:9}],['tonakai',{crk:2}],['tonakai',{armor:0}],['seiuchi',{lie:9}],['mammoth',{sb:1}],['mammoth',{sb:1,aim:.2}]]}[s]||[];
extra.forEach(([t,st],j)=>{const [x,y]=pos[list.length+j];const e=T.addEnemy(t,x,y);e.sp=0;Object.assign(e,st);out.push(t+JSON.stringify(st))});
for(const e of G.en){e.sp=0;e.vy=0;e.born=1}
for(const t in T.ENEMIES) delete T.ENEMIES[t].tick;   // 状態を そのまま 見るため、おばけの うごき（tick）を とめる
G.paused=false; G.spawnQ=[]; G.banners=[];
return new Promise(r=>setTimeout(()=>{G.banners=[];r(out.join(' '))},900));
})()
