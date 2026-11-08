# 絵の 光る 色の 色あいだけ まわす（白・灰色は そのまま）。使い方：python3 hue.py 入れる.png 出す.png 度 [あざやかさの 倍率]
# 竜巻タワーの みどり（Canva の 絵は 色あい 102°＝ノーマルタワーと 同じ）を ミント（158°）に（11/8）
import sys, numpy as np
from PIL import Image
im=Image.open(sys.argv[1]); mode=im.mode; im=im.convert('RGBA')
A=np.asarray(im).astype(np.float32)/255
rgb=A[...,:3]; mx=rgb.max(2); mn=rgb.min(2); d=mx-mn
h=np.zeros_like(mx)
m=d>1e-6
r,g,b=rgb[...,0],rgb[...,1],rgb[...,2]
i=m&(mx==r); h[i]=((g-b)[i]/d[i])%6
i=m&(mx==g)&~(mx==r); h[i]=(b-r)[i]/d[i]+2
i=m&(mx==b)&~(mx==r)&~(mx==g); h[i]=(r-g)[i]/d[i]+4
h=(h/6+float(sys.argv[3])/360)%1
s=np.where(mx>0,d/np.maximum(mx,1e-6),0)*(float(sys.argv[4]) if len(sys.argv)>4 else 1); v=mx
k=lambda n:(n+h*6)%6
f=lambda n:v-v*s*np.clip(np.minimum(k(n),4-k(n)),0,1)
out=np.dstack([f(5),f(3),f(1),A[...,3]])
Image.fromarray((np.clip(out,0,1)*255+.5).astype(np.uint8),'RGBA').convert(mode if mode in('RGB','RGBA') else 'RGBA').save(sys.argv[2])
