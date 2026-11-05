// 自動プレイ（キャンペーン）：草原から順に、クリアするまでくり返す。負けるたび・クリアのたびにお店で買う。
// opts: {upTo:台の番号, tries:1台の最大回数, st:{台番号:{hp:..}} で数字をためす, obj:{HONEY:{heal:.2}} で mk.py が出した入れものを上書き, log:true でウェーブごとのライフ, boss:true で負けたときのボスののこりHP, from:台の番号（下の説明）, deck:true で台に入るときのセットも出す}
(opts)=>{
const T=window.__T,G=T.G;
if(opts.st) for(const i in opts.st) Object.assign(T.STAGES[i],opts.st[i]);
if(opts.obj) for(const k in opts.obj) for(const j in opts.obj[k]){const v=opts.obj[k][j],o=T[k][j];if(v&&typeof v==='object'&&o&&typeof o==='object')Object.assign(o,v);else T[k][j]=v}   // obj:{HONEY:{heal:.2},ENEMIES:{kuma:{hp:1200}}} … __T の入れものを上書き
const upTo=opts.upTo??1, tries=opts.tries??10;
function build(p,k){const t=T.TOWERS[k];G.balls-=t.cost;p.tower=T.newTower(k,p);p.r=Math.max(p.r,7)}
function order(){return G.pegs.filter(p=>!p.fixed).slice().sort((a,b)=>Math.hypot(a.x-188,a.y-250)-Math.hypot(b.x-188,b.y-250))}
const avail=D=>!D.board||T.stageOpen(D.board);
function runBoard(i){
  const c0=G.balls; T.playBoard(i); G.paused=true; G.banners=[];
  const types=Object.keys(T.TOWERS).filter(k=>G.unlocked[k]&&avail(T.TOWERS[k])&&k!=='long');
  const pick=types.length>1?types.filter(k=>k!=='basic'):types;
  let n=0,t=0,act=0,lw=0,boss=null; const dt=1/60, lives=[];
  while(G.state==='play'&&t<900){
    if(G.wave!==lw){lw=G.wave;lives.push(G.life)}
    {const b=G.en.find(e=>!e.dead&&T.ENEMIES[e.t].boss===2&&!e.fake);if(b)boss=b.hp/b.max}   // ボスののこりHP
    T.update(dt); G.time+=dt; t+=dt; act-=dt;
    if(act<=0){act=.5;
      const free=order().filter(p=>!p.tower), k=pick[n%pick.length];
      if(free.length&&G.balls>=T.TOWERS[k].cost+10){build(free[0],k);n++}
      else if(!free.length){const gk=Object.keys(T.GIMMICKS).reverse().find(g=>G.gimmicks[g]&&avail(T.GIMMICKS[g]));
        if(gk){const p=G.pegs.find(p=>p.tower&&!p.tower.gm),M=T.GIMMICKS[gk];if(p&&G.balls>=M.cost+30){G.balls-=M.cost;p.tower.gm=gk}}}
    }
  }
  return {c0,clear:G.state==='clear',wave:G.wave,life:G.life,lives,boss};
}
function shop(){
  const items=[];
  for(const k of Object.keys(T.TOWERS)) if(k!=='basic'&&k!=='long') items.push(['tower',k]);
  for(const k of Object.keys(T.BALLS)) if(T.BALLS[k].el||k==='lead') items.push(['ball',k]);
  for(const k of Object.keys(T.GIMMICKS)) items.push(['gimmick',k]);
  // 新しい台の品を先に
  items.sort((a,b)=>{const D=x=>(x[0]==='ball'?T.BALLS:x[0]==='tower'?T.TOWERS:T.GIMMICKS)[x[1]];return (D(b).board||0)-(D(a).board||0)});
  for(const [kind,k] of items){const D=(kind==='ball'?T.BALLS:kind==='tower'?T.TOWERS:T.GIMMICKS)[k]; if(!avail(D))continue;
    if(kind==='tower'&&G.unlocked[k])continue; if(kind==='gimmick'&&G.gimmicks[k])continue; if(kind==='ball'&&(G.owned[k]||0)>=1)continue;
    const price=kind==='ball'?D.price:D.unlock; if(G.balls<price+60) continue;
    G.balls-=price; if(kind==='ball'){G.owned[k]=(G.owned[k]||0)+1;const j=G.deck.indexOf('normal');if(j>=0)G.deck[j]=k;else{let j2=-1;G.deck.forEach((x,j)=>{const b=T.BALLS[x].board||0;if(b<(D.board||0)&&(j2<0||b<(T.BALLS[G.deck[j2]].board||0)))j2=j});if(j2>=0)G.deck[j2]=k}}   // セットがいっぱいなら、いちばん古い台の玉と入れかえる
    else if(kind==='tower')G.unlocked[k]=true; else G.gimmicks[k]=true;
  }
}
function buyBoard(i){const B=T.BOARDS.find(b=>b.stage===i); if(!B||!B.price) return true; G.bought=G.bought||[]; if(G.bought.includes(i)) return true;
  if(!G.cleared.includes(B.need)||G.balls<B.price) return false; G.balls-=B.price; G.bought.push(i); return true}
localStorage.clear(); T.G.state='hub';
G.balls=150;G.deck=['normal','normal','normal','fire','ice'];G.owned={fire:1,ice:1};G.cleared=[];G.bought=[];
for(const k in G.unlocked) G.unlocked[k]=k==='basic'; for(const k in G.gimmicks) G.gimmicks[k]=false;
const out={};
// from:台の番号 … その前の台はクリアずみ・その台はコインで買ったところから始める（前の台までの品は1つずつ持っている。自動プレイのキャンペーンと同じく、その台の品はまだ買っていない）
// coins:はじめのコイン（なければ 200〜800 のどれか）、deckStart:はじめのセット（なければ キャンペーンでなる形）
if(opts.from){const s0=opts.from, old=D=>(D.board||0)<s0;
  G.cleared=[...Array(s0).keys()]; G.bought=[s0];
  for(const k in T.TOWERS) if(old(T.TOWERS[k])) G.unlocked[k]=true;
  for(const k in T.GIMMICKS) if(old(T.GIMMICKS[k])) G.gimmicks[k]=true;
  for(const k in T.BALLS){const D=T.BALLS[k];if((D.el||k==='lead')&&old(D))G.owned[k]=1}
  G.deck=(opts.deckStart||['water','vine','bolt','fire','ice']).slice(); G.balls=opts.coins??Math.round(200+Math.random()*600);
}
for(let s=opts.from||0;s<=upTo;s++){
  const res=[]; out[T.STAGES[s].name]=res;
  if(opts.deck) res.push('set:'+G.deck.join(','));
  for(let w=0;w<20&&!buyBoard(s);w++){const r=runBoard(s-1);res.push('稼ぎ'+(r.clear?'C':r.wave));shop()}
  if(!T.stageOpen(s)){res.push('開かない');break}
  if(opts.deck&&res.length>1) res.push('set:'+G.deck.join(','));
  for(let k=0;k<tries&&!G.cleared.includes(s);k++){const r=runBoard(T.BOARDS.findIndex(b=>b.stage===s));res.push((r.clear?'C'+r.life:'w'+r.wave+(opts.boss&&r.boss!=null?'('+r.boss.toFixed(2)+')':''))+'@'+r.c0+(opts.log?'['+r.lives.join(',')+']':''));shop()}
  if(!G.cleared.includes(s)) break;
  shop();
}
return out;
}
