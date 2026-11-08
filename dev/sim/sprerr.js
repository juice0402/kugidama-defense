(()=>{   // Canvaの絵の おばけだけ：その台の おばけ × いろいろな状態で update と draw を すこし動かして、エラーがないか見る（drawcheck.js の かるい版。先に mk.py）
const T=window.__T,G=T.G,errs=[];let n=0;
const states=[{},{stun:1},{sleep:1},{freeze:1,stun:1},{ghost:1},{hurtT:.3,flash:.1},{psnT:3,psnD:1},{wet:3},{burn:2,burnD:1},{fear:2},{rush:2},{dying:true},
  {hatGone:true},{leaf:false},{curl:2},{lick:1},{potGone:1},{lives:0},{lives:0,revived:true},{bp:'hang',bt:9},{armorOff:3},{wind:2},{flap:.4},{howl:2},
  {mp:'dig',mt:.3},{mp:'under',mt:1},{tail:false},{knot:true},{hump:0},{drink:1},{aim:1},{clawStop:1},{shield:2},{crack:1},
  {found:1},{found:0},{armor:0},{crk:2},{melt:1},{lie:2},{sb:1},{sb:1,aim:.5},{sb:.6,toss:.3},{pp:'slide',pt:1},{pp:'fall',pt:.5},
  {soak:.5},{cool:2},{fly:.5},{burnt:true},{horn:0},{hcrk:2},{aim:.5,rush:0},{rush:1},{fall:.3},{inh:.5},{breath:1},
  {grab:.5},{loot:{c:'#ff5fd2'}},{shell:true,life:1},{noShed:true},{fresh:.5},{stone:1},{chant:1},{fanUp:.5},{fan:1},
  {knot:2},{rp:'ride',rt:1},{rp:'jump',rt:.2},{bar:true},{form:.3},{puff:.5},{op:.5},{gulp:1},
  {clear:2},{hz:'hide'},{walk:2},{hz:'fly'},{ug:.5},{fog:2},{pray:1},{ki:0,kAct:1},{ki:2,kAct:1},{ki:3,kAct:1,ting:.3},{ki:4,kAct:1},{ki:5,kAct:1},{ki:6,kAct:1},{ki:7,kAct:1},{ki:1,kAim:.5},{shield:2,lsh:2}];
for(let s=0;s<T.STAGES.length;s++){
  try{T.playBoard(T.BOARDS.findIndex(b=>b.stage===s));G.paused=true}catch(x){errs.push('play'+s+':'+x.message);continue}
  for(const t of T.STAGES[s].foes){
    for(const st of states){
      try{G.en=[];const e=T.addEnemy(t,188,260);Object.assign(e,st);T.draw();for(let i=0;i<5;i++){T.update(1/60);G.time+=1/60}T.draw();n++}catch(x){errs.push(s+'/'+t+'/'+JSON.stringify(st)+':'+x.message)}
    }
  }
}
// タワー 22種 × ギミック 10種（Canva の 絵・11/8 4.）：12本の 杭に ならべて、ふつうの 状態と 動いている 状態（撃った・ためる・宿った・はじいた など）で 数コマ 描く。お店の アイコンも
try{T.playBoard(0);G.paused=true;G.en=[];G.bs=[]}catch(x){errs.push('tw play:'+x.message)}
const tks=Object.keys(T.TOWERS), gks=[null,...Object.keys(T.GIMMICKS)], combos=[];
for(const tk of tks) for(const gk of gks) combos.push([tk,gk]);
const busy={shot:.08,chg:.3,chgMax:.55,el:'fire',elT:5,bump:.2,door:.2,jump:.2,whirl:.2,gulp:.2,boom:.3,flow:1,split:.2,spinK:.2,hfl:.2,pull:.1,near:.2,bless:9};
for(let i=0;i<combos.length;i+=G.pegs.length){
  for(const st of [{},busy]){
    try{
      G.pegs.forEach((p,j)=>{const c=combos[i+j];p.tower=c?Object.assign(T.newTower(c[0],p),{gm:c[1],pop:0,ang:j*.8,lv:1+j%4},st):null;if(p.tower&&st.spinK)p.tower.orbT=G.time});
      T.draw();for(let f=0;f<3;f++){T.update(1/60);G.time+=1/60}T.draw();n++;
    }catch(x){errs.push('tw '+combos.slice(i,i+12).map(c=>c.join('+')).join(',')+':'+x.message)}
  }
}
for(const p of G.pegs) p.tower=null;
try{for(const k of tks)T.icon('tower',k);for(const k of gks.slice(1))T.icon('gimmick',k);n++}catch(x){errs.push('icon:'+x.message)}
return n+' ok / errors '+errs.length+' '+errs.slice(0,6).join(' | ');
})()
