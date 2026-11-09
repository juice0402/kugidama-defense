# BGM の音の大きさを はかる用のページ bgm.html を作る（使い方: python3 bgmharness.py && python3 bgmcheck.py grass,volcano）
import os
here=os.path.dirname(os.path.abspath(__file__))
s=open(os.path.join(here,'..','..','index.html'),encoding='utf-8').read()
i=s.index('function seeded(seed)'); j=s.index('/* ==================== BGM ここまで ==================== */')
code=s[i:j]
html=f"""<!doctype html><meta charset=utf-8><body><div id=hub class=""></div><script>
let G={{state:'title',en:[],pend:[],fever:0,paused:false}}; const $=id=>document.getElementById(id); const ENEMIES={{}};
{code}
window.__render=async function(key,plan,dur){{
  const sr=22050, X=new OfflineAudioContext(1,Math.ceil(sr*dur),sr);
  const V=X.createGain(); V.gain.value=BGM_VOL; V.connect(X.destination);
  const p=new Player(X,V,key,0.05);
  let maxNodes=0;
  for(let t=0;t<dur;t+=0.05){{
    let w={{mode:0,fv:false}}; for(const q of plan) if(t>=q.t) w=Object.assign({{}},w,q); p.want.mode=w.mode; p.want.fv=w.fv;
    p.pump(t+0.3);
  }}
  const buf=await X.startRendering(), d=buf.getChannelData(0);
  const out=[]; for(let s0=0;s0<d.length;s0+=sr){{let pk=0,sq=0,n=0,bad=0;for(let k=s0;k<Math.min(d.length,s0+sr);k++){{const v=d[k];if(!isFinite(v))bad++;else{{pk=Math.max(pk,Math.abs(v));sq+=v*v;n++}}}}out.push([+(pk.toFixed(3)),+(Math.sqrt(sq/n).toFixed(4)),bad])}}
  return {{nodes:p.n,dur,sec:out}};
}};
</script>"""
open(os.path.join(here,'bgm.html'),'w',encoding='utf-8').write(html)
print('ok')
