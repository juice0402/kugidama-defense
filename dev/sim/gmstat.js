(()=>{   // ギミックの強さ（玉1つあたり）：台 st の全部の杭に ふつうタワー＋ギミック、おばけなしで 2分。経験値（砲台に当たった数）・玉が台にいる秒・分身の玉の数。使い方：python3 shot.py out.png "$(cat gmstat.js)"（先に mk.py。台は下の st）
const T=window.__T,G=T.G,st=6,res={};
localStorage.clear(); G.cleared=[0,1,2,3,4,5,6,7]; G.bought=[0,1,2,3,4,5,6,7,8];
for(const g of ['none',...Object.keys(T.GIMMICKS)]){
  T.playBoard(T.BOARDS.findIndex(b=>b.stage===st)); G.paused=true; G.balls=99999; G.fever=0; G.banners=[];
  for(const p of G.pegs){p.tower=T.newTower('basic',p);p.r=Math.max(p.r,7);if(g!=='none')p.tower.gm=g}
  const ages=[], cl=[]; let prev=new Set(), n=0;
  for(let i=0;i<60*120;i++){
    G.spawnQ=[];G.en=[];G.pend=[];G.wave=1;G.waveDone=true;G.waveGap=99;
    G.fever=0; T.update(1/60); G.time+=1/60;
    const now=new Set(G.bs); for(const b of now) if(!prev.has(b)&&!b.clone) n++; for(const b of prev) if(!now.has(b)) (b.clone?cl:ages).push(b.age); prev=now;
  }
  const xp=G.pegs.reduce((a,p)=>a+p.tower.xp,0), m=a=>a.length?a.reduce((x,y)=>x+y,0)/a.length:0;
  res[g]={xp:+(xp/n).toFixed(2),sec:+m(ages).toFixed(1),clones:+(cl.length/n).toFixed(2),heso:G.stat.heso||0};
  G.stat={};
}
return res})()
