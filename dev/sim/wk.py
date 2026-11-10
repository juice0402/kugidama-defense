# WebKit（iPhone の Safari と 同じ エンジン。Linux の WebKitGTK）で ためす（11/10 しょーくん「iPhone の Safari で 台えらびの 台が 出ない」）
# ここの Chrome では 見えない WebKit だけの ちがい を さがす。画面の 大きさは iframe で きめる（MiniBrowser の まどは はば 447 より せまく できない）
# じゅんび（1回だけ）: apt-get install -y webkit2gtk-driver xvfb xauth fonts-noto-cjk && pip install --break-system-packages selenium
# 使い方: python3 mk.py && python3 wk.py [はば x 高さ x 倍率] [出す フォルダ] [ゲームの ファイル（dev/sim から）]
#   倍率は GDK_SCALE（1・2・3）。ACC=1 で キャンバスを GPU で 描く 設定に
import os, sys, time, subprocess, json, threading, http.server, functools, socketserver
from selenium import webdriver
from selenium.webdriver.webkitgtk.service import Service
from PIL import Image
HERE=os.path.dirname(os.path.abspath(__file__))
W,H,D=[float(x) for x in (sys.argv[1] if len(sys.argv)>1 else '390x664x2').split('x')]; W,H,D=int(W),int(H),int(D)
OUT=os.path.join(HERE,sys.argv[2] if len(sys.argv)>2 else '_wk'); os.makedirs(OUT,exist_ok=True)
GAME=os.path.abspath(os.path.join(HERE,sys.argv[3] if len(sys.argv)>3 else 'game.html'))
# ゲームを http で 出す（iframe の 中を さわれる ように 同じ 場所から）
class Q(http.server.SimpleHTTPRequestHandler):
    def log_message(self,*a): pass
GD=os.path.dirname(GAME)
srv=socketserver.TCPServer(('127.0.0.1',0),functools.partial(Q,directory=GD)); port=srv.server_address[1]
threading.Thread(target=srv.serve_forever,daemon=True).start()
open(os.path.join(GD,'_wkframe.html'),'w').write(
    '<!doctype html><meta charset="utf-8"><style>html,body{margin:0;background:#222}iframe{border:0;display:block}</style>'
    f'<iframe id="f" src="{os.path.basename(GAME)}" style="width:{W}px;height:{H}px"></iframe>')
disp=':%d'%(60+os.getpid()%30)
xv=subprocess.Popen(['Xvfb',disp,'-screen','0','2400x2600x24','-nolisten','tcp'],stdout=subprocess.DEVNULL,stderr=subprocess.DEVNULL)
time.sleep(1.2)
env=dict(os.environ,DISPLAY=disp,GDK_SCALE=str(D))
for k in ('HTTPS_PROXY','HTTP_PROXY','https_proxy','http_proxy','NO_PROXY','no_proxy'): env.pop(k,None)
opts=webdriver.WebKitGTKOptions(); opts.binary_location='/usr/lib/x86_64-linux-gnu/webkit2gtk-4.1/MiniBrowser'; opts.add_argument('--automation')
if os.environ.get('ACC'): opts.add_argument('--enable-2d-canvas-acceleration=true')
svc=Service(executable_path='/usr/bin/WebKitWebDriver',env=env)
dr=None
def shot(name):
    dr.switch_to.default_content()
    p=os.path.join(OUT,name); dr.save_screenshot(p)
    im=Image.open(p); r=dr.execute_script("const r=document.getElementById('f').getBoundingClientRect();return [r.left,r.top,r.width,r.height]")
    k=im.width/dr.execute_script('return innerWidth')
    im.crop((int(r[0]*k),int(r[1]*k),int((r[0]+r[2])*k),int((r[1]+r[3])*k))).save(p)
    dr.switch_to.frame(dr.find_element('id','f'))
try:
    dr=webdriver.WebKitGTK(options=opts,service=svc)
    dr.set_window_size(W+120,H+160)
    dr.get(f'http://127.0.0.1:{port}/_wkframe.html'); time.sleep(3)
    dr.switch_to.frame(dr.find_element('id','f'))
    js=lambda s,*a: dr.execute_script(s,*a)
    js("window.__E=window.__E||[];addEventListener('error',e=>__E.push(String(e.message)))")
    print('画面',js("return {iw:innerWidth,ih:innerHeight,dpr:devicePixelRatio}"),flush=True)
    shot('1-title.png')
    js("document.getElementById('startBtn').click()"); time.sleep(3.5)
    shot('2-hall.png'); time.sleep(4); shot('3-hall-later.png')
    r=js("""const c=document.querySelectorAll('.cface .face');
      const px=cv=>{if(cv.tagName==='IMG'){if(!cv.complete||!cv.naturalWidth)return 'まだ';const t=document.createElement('canvas');t.width=cv.naturalWidth;t.height=cv.naturalHeight;t.getContext('2d').drawImage(cv,0,0);cv=t}
        try{const g=cv.getContext('2d'),d=g.getImageData(0,0,cv.width,cv.height).data;let n=0,m=0;for(let i=3;i<d.length;i+=4*97){m++;if(d[i]>0&&(d[i-1]+d[i-2]+d[i-3])>30)n++}return Math.round(n/m*100)+'%'}catch(e){return 'err '+e}};
      const sl=[...document.querySelectorAll('.slot')].map(e=>{const r=e.getBoundingClientRect();return [r.left|0,r.top|0,r.width|0,r.height|0]});
      const a=document.querySelector('.aisle'),hw=document.querySelector('.hallwrap');
      return {faces:[...c].map(cv=>({lit:px(cv),r:(b=>[b.left|0,b.top|0,b.width|0,b.height|0])(cv.getBoundingClientRect())})),slots:sl,aisle:a&&[a.clientWidth,a.clientHeight,a.scrollLeft,a.scrollWidth],cw:hw&&getComputedStyle(hw).getPropertyValue('--cw'),err:window.__E}""")
    print('ホール',json.dumps(r,ensure_ascii=False),flush=True)
finally:
    if dr: dr.quit()
    xv.terminate(); srv.shutdown()
    try: os.remove(os.path.join(GD,'_wkframe.html'))
    except Exception: pass
