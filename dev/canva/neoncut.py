# ネオンのおばけを すけすけに：Canva の背景けし（体）＋ もとの絵の 光（背景の色との ちがい）を あわせる
# 使い方：neoncut.py もとの絵.png 背景けし.png 出す.png   （切りぬかない。200×200 のまま）
import sys
import numpy as np
from PIL import Image
orig, cut, out = sys.argv[1], sys.argv[2], sys.argv[3]
O = np.asarray(Image.open(orig).convert('RGB')).astype(np.float32)/255
C = np.asarray(Image.open(cut).convert('RGBA').resize(Image.open(orig).size)).astype(np.float32)/255
border = np.concatenate([O[0], O[-1], O[:,0], O[:,-1]])
bg = np.median(border, axis=0)
d = np.abs(O-bg).max(axis=2)
ag = np.clip((d-0.035)*1.5, 0, 1)            # まわりの光（うすく すける）
# 背景けしが けずった こい色の 部品（くまの はちみつツボ など）：背景との ちがいが 大きくて 太い かたまりは 不とうめいに
from PIL import ImageFilter
solid = Image.fromarray(((d>0.3)*255).astype(np.uint8)).filter(ImageFilter.MinFilter(7)).filter(ImageFilter.MaxFilter(7))
solid = np.asarray(solid.filter(ImageFilter.GaussianBlur(1))).astype(np.float32)/255
ag = np.maximum(ag, np.clip((d-0.035)/0.30, 0, 1)*solid)
ac = C[...,3]
a = np.maximum(ac, ag)
F = np.where(a[...,None]>1e-3, (O - bg*(1-a[...,None]))/np.maximum(a[...,None],1e-3), 0)
F = np.clip(F,0,1)
F = F*(1-ac[...,None]) + C[...,:3]*ac[...,None]
res = np.dstack([F, a])
Image.fromarray((res*255+.5).astype(np.uint8), 'RGBA').save(out)
