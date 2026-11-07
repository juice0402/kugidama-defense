# すけすけの絵（*_full.png）を 切りぬいて WebP にし、ゲームに入れる SPRITE_SRC の行を出す
# グループ（かえ絵）は 同じ わくで 切りぬく（入れかわっても 体が ずれないように）
import sys, json, base64, io
from PIL import Image
import os
HERE=os.path.dirname(os.path.abspath(__file__))
G=os.path.join(HERE,'ghosts')+'/'
spec=json.load(open(os.path.join(HERE,'sprites.json')))   # {"groups":[["kakashi","kakashi_nohat"],...],"size":{"wata":[w,by],...}}
groups=[g for g in spec['groups']]
done=set(k for g in groups for k in g)
for k in spec['size']:
    if k not in done: groups.append([k])
def bbox(im):
    return im.getchannel('A').point(lambda v:255 if v>6 else 0).getbbox()
lines=[]; total=0
for g in groups:
    ims={k:Image.open(G+k+'_full.png').convert('RGBA') for k in g}
    bs=[bbox(i) for i in ims.values()]
    b=(min(x[0] for x in bs)-3,min(x[1] for x in bs)-3,max(x[2] for x in bs)+3,max(x[3] for x in bs)+3)
    b=(max(0,b[0]),max(0,b[1]),min(200,b[2]),min(200,b[3]))
    for k,im in ims.items():
        c=im.crop(b); buf=io.BytesIO(); c.save(buf,'WEBP',quality=90,method=6,alpha_quality=100); data=buf.getvalue(); total+=len(data)
        pass
        w,by=spec['size'][k]
        lines.append(f"  {k}:{{w:{w},by:{by},src:'data:image/webp;base64,{base64.b64encode(data).decode()}'}},   // {c.width}×{c.height}")
open(os.path.join(HERE,'sprite_src.js'),'w').write('\n'.join(lines)+'\n')
print('sprites',len(lines),'bytes',total)
