// 自動プレイ（キャンペーン）：草原から順に、クリアするまでくり返す。負けるたび・クリアのたびにお店で買う。
// opts: {upTo:台の番号, tries:1台の最大回数, gm:'ari' で つけるギミックを えらぶ, shop0:true で from の台の1回目の前に お店で買う（'none'＝つけない。ギミックは全部 持っている形にして、お店で買わない。ギミックごとに分けて強さを測る）, st:{台番号:{hp:..}} で数字をためす, obj:{HONEY:{heal:.2}} で mk.py が出した入れものを上書き, log:true でウェーブごとのライフ, bt:true でボスが出てから決着までの秒（ゲーム内。終わらなければ +）, boss:true で負けたときのボスののこりHP, from:台の番号（下の説明）, deck:true で台に入るときのセットも出す, towers:[...] で 建てる タワーの ならび（くり返す）}
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
  let pick=types.length>1?types.filter(k=>k!=='basic'):types;
  if(opts.towers){const L=opts.towers.filter(k=>G.unlocked[k]&&avail(T.TOWERS[k]));if(L.length)pick=L}   // towers:['holy','tenshi','fire'] … 建てる タワーの ならびを えらぶ（持っている物だけ。なければ ふだんの ならび）
  let n=0,t=0,act=0,lw=0,boss=null,bs=null; const dt=1/60, lives=[];
  const trk=new Map(), live=[];   // prof：おばけごとに 出た所・いちばん下まで来た所・倒れた時間
  const prof=()=>{for(const e of G.en){if(e.fake||trk.has(e))continue;const r={e,w:G.wave,y0:e.y,my:e.y,b:T.ENEMIES[e.t].boss||0,t0:t};trk.set(e,r);live.push(r)}
    for(let i=live.length-1;i>=0;i--){const r=live[i];r.my=Math.max(r.my,r.e.y);if(r.e.dead){r.t1=t;r.kill=r.e.hp<=0;live.splice(i,1)}}};
  while(G.state==='play'&&t<900){
    if(G.wave!==lw){lw=G.wave;lives.push(G.life)}
    {const b=G.en.find(e=>!e.dead&&T.ENEMIES[e.t].boss===2&&!e.fake);if(b){boss=b.hp/b.max;if(bs==null)bs=t}}   // ボスののこりHP・ボスが出た時間
    if(opts.prof)prof(); T.update(dt); G.time+=dt; t+=dt; act-=dt; if(opts.prof)prof();
    if(act<=0){act=.5;
      const free=order().filter(p=>!p.tower), k=pick[n%pick.length];
      if(free.length&&G.balls>=T.TOWERS[k].cost+10){build(free[0],k);n++}
      else if(!free.length){const gk=opts.gm?(opts.gm==='none'?null:opts.gm):Object.keys(T.GIMMICKS).reverse().find(g=>G.gimmicks[g]&&avail(T.GIMMICKS[g]));
        if(gk){const p=G.pegs.find(p=>p.tower&&!p.tower.gm),M=T.GIMMICKS[gk];if(p&&G.balls>=M.cost+30){G.balls-=M.cost;p.tower.gm=gk}}}
    }
  }
  let pf='';
  if(opts.prof){const R=[...trk.values()],d=[];   // d＝1〜4ウェーブの ざこが どこまで来たか（出た所0〜受け皿1 の平均）、m＝中ボスを倒すまでの秒（+＝倒せなかった）
    for(let w=1;w<=4;w++){const A=R.filter(r=>r.w===w&&!r.b);if(!A.length){d.push('-');continue}const y0=Math.min(...A.map(r=>r.y0)),S=A.filter(r=>r.y0<=y0+80);
      d.push((S.reduce((a,r)=>a+Math.max(0,Math.min(1,(r.my-r.y0)/(580-r.y0))),0)/S.length).toFixed(2))}
    const M=R.find(r=>r.b===1); pf='#d='+d.join(',')+'#m='+(M?(M.kill?Math.round(M.t1-M.t0):'+'):'-')}
  return {c0,pf,clear:G.state==='clear',wave:G.wave,life:G.life,lives,boss,bt:bs==null?null:Math.round(t-bs)+(G.state==='play'?'+':'')};
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
G.balls=150;G.deck=['normal','normal','normal','normal','normal'];G.owned={};G.cleared=[];G.bought=[];   // はじめは 通常弾だけ（11/10 しょーくん）
for(const k in G.unlocked) G.unlocked[k]=k==='basic'; for(const k in G.gimmicks) G.gimmicks[k]=false;
if(opts.gm) for(const k in T.GIMMICKS) G.gimmicks[k]=true;   // gm：ギミックは全部 持っている（お店で買わない）
const out={};
// from:台の番号 … その前の台はクリアずみ・その台はコインで買ったところから始める（前の台までの品は1つずつ持っている。自動プレイのキャンペーンと同じく、その台の品はまだ買っていない）
// coins:はじめのコイン（数か [下,上]。なければ 200〜800 のどれか。キャンペーンで砂漠に入るときは 300〜2000 くらい）、deckStart:はじめのセット（なければ キャンペーンでなる形）
if(opts.from){const s0=opts.from, old=D=>(D.board||0)<s0;
  G.cleared=[...Array(s0).keys()]; G.bought=[...Array(s0+1).keys()];   // コインで買う前の台（洋館など）も買ってある（前は その台だけで、洋館の品が使えなかった）
  for(const k in T.TOWERS) if(old(T.TOWERS[k])) G.unlocked[k]=true;
  for(const k in T.GIMMICKS) if(old(T.GIMMICKS[k])) G.gimmicks[k]=true;
  for(const k in T.BALLS){const D=T.BALLS[k];if((D.el||k==='lead')&&old(D))G.owned[k]=1}
  G.deck=(opts.deckStart||['water','vine','bolt','fire','ice']).slice(); const cn=opts.coins; G.balls=Array.isArray(cn)?Math.round(cn[0]+Math.random()*(cn[1]-cn[0])):cn??Math.round(200+Math.random()*600);   // coins:[300,2000] で その間のどれか
}
for(let s=opts.from||0;s<=upTo;s++){
  const res=[]; out[T.STAGES[s].name]=res;
  if(opts.deck) res.push('set:'+G.deck.join(','));
  for(let w=0;w<20&&!buyBoard(s);w++){const r=runBoard(s-1);res.push('稼ぎ'+(r.clear?'C':r.wave));shop()}
  if(!T.stageOpen(s)){res.push('開かない');break}
  if(opts.shop0&&s===opts.from) shop();   // shop0：はじめの1回目の前に お店で買う（その台の品を 持った形で 測る）
  if(opts.deck&&res.length>1) res.push('set:'+G.deck.join(','));
  for(let k=0;k<tries&&!G.cleared.includes(s);k++){const r=runBoard(T.BOARDS.findIndex(b=>b.stage===s));res.push((r.clear?'C'+r.life:'w'+r.wave+(opts.boss&&r.boss!=null?'('+r.boss.toFixed(2)+')':''))+'@'+r.c0+(opts.bt&&r.bt!=null?'/b'+r.bt:'')+(opts.log?'['+r.lives.join(',')+']':'')+r.pf);shop()}
  if(!G.cleared.includes(s)) break;
  shop();
}
return out;
}
