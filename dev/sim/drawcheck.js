(()=>{   // 全部の台 × 全部のおばけ × いろいろな状態（しびれ・ねむり・こおり・根っこ・こんらん・がまん…）で update と draw を動かして、エラーがないか見る。使い方：python3 shot.py out.png "$(cat drawcheck.js)"（先に mk.py）。台の担当は states に自分の状態を足してよい
const T=window.__T,G=T.G,errs=[];let n=0;
const states=[{},{stun:2},{sleep:2},{freeze:1,stun:1,slow:2,slowF:.3},{root:1,vineT:3},{conf:1,dark:3},{burn:3,burnD:1},{psnT:5,psnD:1},{wet:4},{noteT:3,flinch:.5},{shock:2},{guard:2.5,holdT:0},{guard:1,stun:1,sleep:1},{holdT:2.4,stun:1},{ghost:1},{oops:.5},{hurtT:.3},{fear:2,rush:2},{thorn:2},{sandT:2,blind:1,sink:1,mud:1},{windT:2},{mp:'dig',mt:.2},{mp:'under',mt:1,ghost:1},{dash:.5,tail:false},{knot:true},{drink:.5},{aim:.5},{clawStop:1},{shield:2,shHit:.1},{crack:.4},{snowN:2,snowT:3},{snowman:1,manMax:1.5},{cryst:3,crArm:0,crEl:'fire'},{found:2},{pp:'slide',pt:1},{pp:'fall',pt:.5},{armor:1,crk:2,melt:.5,burn:1},{armor:0},{lie:2},{sb:.8},{aim:.5,sb:1},{toss:.3},{cover:9e9},{hide:30},{mag:2},{soak:.5,hk:2},{cool:2},{fly:.5},{burnt:true},{burnt:true,fly:.3},{horn:1,hcrk:2,kin:.1},{horn:0},{fr:1},{rush:.5},{fall:.5},{aim:.5,rush:0},{inh:.6},{breath:.5},{inh:0,breath:0,dg:.01},{curseT:3,curseN:3,hexPop:.2},{mummy:2,curseT:1,curseN:1},{chainT:2,anchor:1,netT:1},{grab:.3},{loot:{k:'el',v:'fire',t:5,c:'#ff7a3d',p:null}},{kt:.01},{noShed:true,fresh:.3,dashT:.5},{shell:true,fake:true,life:2},{stone:1.5,ting:.1},{stone:0,stCD:1,hopY:.3},{chant:.5},{barrier:2},{fanUp:.5},{fan:2,ting:.1},{yt:.01,kt:.01,st:.01}];
for(let s=0;s<T.STAGES.length;s++){
  try{T.playBoard(T.BOARDS.findIndex(b=>b.stage===s));G.paused=true}catch(x){errs.push('play'+s+':'+x.message);continue}
  for(const t of Object.keys(T.ENEMIES)){
    for(const st of states){
      try{G.en=[];const e=T.addEnemy(t,188,260);Object.assign(e,st);T.draw();for(let i=0;i<20;i++){T.update(1/60);G.time+=1/60}T.draw();n++}catch(x){errs.push(s+'/'+t+'/'+JSON.stringify(st)+':'+x.message)}
    }
    // 属性・とくしゅ効果・わざを全部つけて動かす
    try{G.en=[];const e=T.addEnemy(t,188,260),o=T.addEnemy('neko',200,280);
      for(const k of T.EL_ORDER){T.applyEl(e,k,3,2);T.applyEff(e,{sp:k},2)}
      for(const c of Object.keys(T.COMBO))T.applyEff(e,{combo:c},2);
      for(let i=0;i<120;i++){T.update(1/60);G.time+=1/60;if(i%20==0)T.draw()}n++}catch(x){errs.push(s+'/'+t+'/all:'+x.message)}
  }
}
G.en=[];return {n,errs:errs.slice(0,10),ne:errs.length}})()
