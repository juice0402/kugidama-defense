(()=>{   // Canvaの絵の おばけだけ：その台の おばけ × いろいろな状態で update と draw を すこし動かして、エラーがないか見る（drawcheck.js の かるい版。先に mk.py）
const T=window.__T,G=T.G,errs=[];let n=0;
const states=[{},{stun:1},{sleep:1},{freeze:1,stun:1},{ghost:1},{hurtT:.3,flash:.1},{psnT:3,psnD:1},{wet:3},{burn:2,burnD:1},{fear:2},{rush:2},{dying:true},
  {hatGone:true},{leaf:false},{curl:2},{lick:1},{potGone:1},{lives:0},{lives:0,revived:true},{bp:'hang',bt:9},{armorOff:3},{wind:2},{flap:.4},{howl:2},
  {mp:'dig',mt:.3},{mp:'under',mt:1},{tail:false},{knot:true},{hump:0},{drink:1},{aim:1},{clawStop:1},{shield:2},{crack:1},
  {found:1},{found:0},{armor:0},{crk:2},{melt:1},{lie:2},{sb:1},{sb:1,aim:.5},{sb:.6,toss:.3},{pp:'slide',pt:1},{pp:'fall',pt:.5}];
for(let s=0;s<T.STAGES.length;s++){
  try{T.playBoard(T.BOARDS.findIndex(b=>b.stage===s));G.paused=true}catch(x){errs.push('play'+s+':'+x.message);continue}
  for(const t of T.STAGES[s].foes){
    for(const st of states){
      try{G.en=[];const e=T.addEnemy(t,188,260);Object.assign(e,st);T.draw();for(let i=0;i<5;i++){T.update(1/60);G.time+=1/60}T.draw();n++}catch(x){errs.push(s+'/'+t+'/'+JSON.stringify(st)+':'+x.message)}
    }
  }
}
return n+' ok / errors '+errs.length+' '+errs.slice(0,6).join(' | ');
})()
