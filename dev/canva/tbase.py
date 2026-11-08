# 砲台の 土台の 絵（まん丸）を 円で 切りぬいて、こい 金属に する（白い 頭が 見えるように）。使い方：python3 tbase.py
# もとの絵 towers/src/base.png（Canva MAHaTWxFLt8）→ towers/base_full.png
import os
import numpy as np
from PIL import Image, ImageDraw
HERE=os.path.dirname(os.path.abspath(__file__))
CX,CY,R=99.5,98.5,71.5          # もとの絵の 中の 台の まるの 中心と 半径
DARK=.5; GAM=1.25               # こく する 強さ（明るい所は 少し のこす）
im=Image.open(os.path.join(HERE,'towers/src/base.png')).convert('RGB')
A=np.asarray(im).astype(np.float32)/255
A=np.clip((A**GAM)*DARK*1.08,0,1)
A=A*np.array([.92,.95,1.08])    # ほんの少し 青みの 鉄色（夜の 台に なじむ）
A=np.clip(A,0,1)
m=Image.new('L',(im.width*4,im.height*4),0); ImageDraw.Draw(m).ellipse(((CX-R)*4,(CY-R)*4,(CX+R)*4,(CY+R)*4),fill=255)
m=m.resize(im.size,Image.LANCZOS)
out=Image.fromarray((A*255+.5).astype(np.uint8),'RGB').convert('RGBA'); out.putalpha(m)
out.save(os.path.join(HERE,'towers/base_full.png'))
print('ok')
