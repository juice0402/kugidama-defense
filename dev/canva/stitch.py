# 6まいの見本（2×3）を つなぐ: python3 stitch.py 出す.png t1 t2 t3 t4 t5 t6
import sys
from PIL import Image
out=sys.argv[1]; ts=[Image.open(p).convert('RGB') for p in sys.argv[2:8]]
k=ts[0].width/480          # 見本の倍率（480×572 の ページ → 503×599）
W=round(944*k); H=round(1680*k)
im=Image.new('RGB',(W,H))
for i,t in enumerate(ts):
    c,r=i%2,i//2
    im.paste(t,(round(c*464*k),round(r*554*k)))
im.save(out); print(out,im.size,'k',k)
