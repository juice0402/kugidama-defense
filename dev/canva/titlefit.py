# タイトル画面の 絵を ゲームに 入れる（11/8 6.）
# 使い方：python3 titlefit.py [はば=720] [質=78]
#   title.json の "src"（Canva の 9:16 の 絵を ページの 見本を つないで 大きく した もの。stitch.py で 989×1760）を 幅 W の WebP に して、
#   index.html の CSS の TITLE_ART（「TITLE_ART ここから」〜「ここまで」）に --t-art（絵）と --t-sky（上の はしの 色＝よこ長の 画面の 上を ぬる）を 書く
import sys, os, io, json, base64
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
J = json.load(open(os.path.join(HERE, 'title.json')))
W = int(sys.argv[1]) if len(sys.argv) > 1 else J.get('w', 720)
Q = int(sys.argv[2]) if len(sys.argv) > 2 else J.get('q', 78)
im = Image.open(os.path.join(HERE, J['src'])).convert('RGB')
H = round(im.height * W / im.width)
im = im.resize((W, H), Image.LANCZOS)
b = io.BytesIO(); im.save(b, 'WEBP', quality=Q, method=6); data = b.getvalue()
A = np.asarray(im).astype(float)
sky = '#%02x%02x%02x' % tuple(int(v) for v in np.median(A[:8].reshape(-1, 3), axis=0))
low = '#%02x%02x%02x' % tuple(int(v) for v in np.median(A[-8:].reshape(-1, 3), axis=0))
print('title', im.size, '%dKB' % (len(data) / 1024 + .5), 'sky', sky, 'low', low)
row = '#title{--t-art:url(data:image/webp;base64,%s);--t-sky:%s;--t-low:%s}' % (base64.b64encode(data).decode(), sky, low)
p = os.path.join(ROOT, 'index.html')
s = open(p, encoding='utf-8').read()
a = s.index('/* TITLE_ART ここから'); a = s.index('*/', a) + 2
e = s.index('/* TITLE_ART ここまで')
s = s[:a] + '\n' + row + '\n' + s[e:]
open(p, 'w', encoding='utf-8').write(s)
print('index.html ok')
