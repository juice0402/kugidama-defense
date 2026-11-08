# 玉の 絵を ゲームに 入れる（11/8 5.）
# 使い方：python3 ballfit.py            … balls.json の 玉を ぜんぶ 切りぬいて 1まいの 絵（アトラス・WebP）に ならべ、index.html の BALL_ART（「BALL_ART ここから」〜「ここまで」）を 書きかえる
#         python3 ballfit.py 見本.png   … ついでに 見本（大きい 玉と、ゲームの 中の 大きさの 玉）を 出す
#
# 絵は Canva の もとの絵 balls/src/〇〇.png（200×200・こい紺の 背景）。ballcut.py で まるく 切りぬく（背景けしは 使わない）。
# balls.json の 1つずつ（〇〇＝BALLS の 名前）：
#   "hue"  色あいを まわす 度（hue.py と 同じ。白・灰色は かわらない）。"sat" あざやかさの 倍率。"val" 明るさの 倍率（白い ところは かわらない）
#   "spin" 1 なら まわす 玉（流星・呪詛・七色）：つや（左上の 白い ハイライト）を 〇〇_g に 分けて、のこりの 〇〇 から つやを けす（ゲームでは 〇〇 を まわして、その上に つやを まわさずに かさねる）
# 出すもの：BALL_ART={src, K, at:{名前:[sx,sy,sw,sh,ax,ay]}}（sx..sh＝アトラスの中の 場所、ax,ay＝その 左上から 玉の まん中まで。どれも ピクセル。K＝玉の 半径が 何ピクセル）
import sys, os, io, json, base64
import numpy as np
import cv2
from PIL import Image, ImageDraw
from ballcut import cut

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')


def huesat(rgb, deg=0, sat=1, val=1):
    # hue.py と 同じ まわし方（0〜1 の float の RGB）
    mx = rgb.max(2); mn = rgb.min(2); d = mx - mn
    h = np.zeros_like(mx); m = d > 1e-6
    r, g, b = rgb[..., 0], rgb[..., 1], rgb[..., 2]
    i = m & (mx == r); h[i] = ((g - b)[i] / d[i]) % 6
    i = m & (mx == g) & ~(mx == r); h[i] = (b - r)[i] / d[i] + 2
    i = m & (mx == b) & ~(mx == r) & ~(mx == g); h[i] = (r - g)[i] / d[i] + 4
    h = (h / 6 + deg / 360) % 1
    s = np.clip(np.where(mx > 0, d / np.maximum(mx, 1e-6), 0) * sat, 0, 1)
    v = np.clip(mx * (1 + (val - 1) * s), 0, 1)   # 明るさは 色の ある ところだけ
    k = lambda n: (n + h * 6) % 6
    f = lambda n: v - v * s * np.clip(np.minimum(k(n), 4 - k(n)), 0, 1)
    return np.dstack([f(5), f(3), f(1)])


def gloss_split(rgba, cx, cy, r):
    # 左上の つや（白い ハイライト）を さがして、つやを けした からだ と つや（白＋すけぐあい）に 分ける
    rgb = rgba[..., :3]
    H, W = rgb.shape[:2]
    yy, xx = np.mgrid[:H, :W]
    wmin = rgb.min(2)
    # つやの ある あたり（玉の 左上・まん中の もようより 外）
    area = ((xx - (cx - .40 * r)) ** 2 + (yy - (cy - .58 * r)) ** 2) < (.36 * r) ** 2
    seed = np.unravel_index(np.argmax(np.where(area, wmin, 0)), wmin.shape)
    thr = max(.80, wmin[seed] - .16)
    m = ((wmin > thr) & ((xx - cx) ** 2 + (yy - cy) ** 2 < (.985 * r) ** 2)).astype(np.uint8)
    m = cv2.morphologyEx(m, cv2.MORPH_OPEN, cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5)))   # ほそい ふちの ネオンの 線は けして、太い つやの かたまりだけ
    n, lab = cv2.connectedComponents(m)
    if lab[seed] == 0:   # いちばん 近い かたまり
        ys, xs = np.where(m > 0); j = np.argmin((ys - seed[0]) ** 2 + (xs - seed[1]) ** 2); seed = (ys[j], xs[j])
    hl = ((lab == lab[seed]) & (m > 0)).astype(np.uint8)
    hl = cv2.dilate(hl, np.ones((5, 5), np.uint8))
    img8 = (np.clip(rgb, 0, 1) * 255 + .5).astype(np.uint8)
    body8 = cv2.inpaint(img8, hl * 255, 6, cv2.INPAINT_TELEA)
    body8 = cv2.GaussianBlur(body8, (0, 0), 1.6) * hl[..., None] + body8 * (1 - hl[..., None])   # うめた ところを なめらかに
    body = body8.astype(np.float32) / 255
    a = np.clip(((rgb - body) / np.maximum(1 - body, 1e-3)).max(2), 0, 1) * cv2.dilate(hl, np.ones((3, 3), np.uint8))
    a = cv2.GaussianBlur(a, (0, 0), .6)
    gl = np.dstack([np.ones_like(rgb), a * rgba[..., 3]])
    bd = np.dstack([body, rgba[..., 3]])
    return bd, gl


def crop(rgba, cx, cy, r, K):
    # 玉の 半径を K ピクセルに して、すけていない ところで 切る
    k = K / r
    im = Image.fromarray((np.clip(rgba, 0, 1) * 255 + .5).astype(np.uint8), 'RGBA')
    # すけすけの 色は アルファを かけてから 小さく（ふちが 黒く ならない）
    pm = np.asarray(im).astype(np.float32); pm[..., :3] *= pm[..., 3:4] / 255
    big = Image.fromarray(pm.astype(np.uint8), 'RGBA')
    w, h = max(1, round(im.width * k)), max(1, round(im.height * k))
    sm = np.asarray(big.resize((w, h), Image.LANCZOS)).astype(np.float32)
    sm[..., :3] = np.where(sm[..., 3:4] > 0, sm[..., :3] * 255 / np.maximum(sm[..., 3:4], 1), 0)
    sm = np.clip(sm, 0, 255).astype(np.uint8)
    a = sm[..., 3]
    ys, xs = np.where(a > 6)
    b = (max(0, xs.min() - 1), max(0, ys.min() - 1), min(w, xs.max() + 2), min(h, ys.max() + 2))
    c = Image.fromarray(sm, 'RGBA').crop(b)
    return c, cx * k - b[0], cy * k - b[1]


def pack(cells, width):
    # 左上から じゅんに ならべる（高さの そろう 行）
    x = y = rowh = 0; pos = {}
    for k, (c, ax, ay) in cells.items():
        if x + c.width > width: x = 0; y += rowh + 1; rowh = 0
        pos[k] = (x, y); x += c.width + 1; rowh = max(rowh, c.height)
    H = y + rowh
    at = Image.new('RGBA', (width, H), (0, 0, 0, 0))
    for k, (c, ax, ay) in cells.items(): at.paste(c, pos[k])
    return at, pos


def build(spec):
    K = spec['K']; cells = {}; raw = {}
    for k, o in spec['balls'].items():
        im = Image.open(os.path.join(HERE, 'balls', 'src', k + '.png')).convert('RGB')
        O = np.asarray(im).astype(np.float32) / 255
        if o.get('hue') or o.get('sat', 1) != 1 or o.get('val', 1) != 1:
            O = huesat(O, o.get('hue', 0), o.get('sat', 1), o.get('val', 1))
        rgba, cx, cy, r = cut(O)
        raw[k] = (rgba, cx, cy, r)
        if o.get('spin'):
            bd, gl = gloss_split(rgba, cx, cy, r)
            cells[k] = crop(bd, cx, cy, r, K)
            g, ax, ay = crop(gl, cx, cy, r, K)
            cells[k + '_g'] = (g, ax, ay)
        else:
            cells[k] = crop(rgba, cx, cy, r, K)
    return cells, raw


def main():
    spec = json.load(open(os.path.join(HERE, 'balls.json')))
    K = spec['K']
    cells, raw = build(spec)
    at, pos = pack(cells, spec.get('width', 760))
    buf = io.BytesIO(); at.save(buf, 'WEBP', quality=spec.get('q', 88), method=6, alpha_quality=100); data = buf.getvalue()
    at.save(os.path.join(HERE, 'balls', 'atlas.png'))
    parts = ','.join(f"{k}:[{pos[k][0]},{pos[k][1]},{c.width},{c.height},{ax:.1f},{ay:.1f}]" for k, (c, ax, ay) in cells.items())
    line = f"const BALL_ART={{K:{K},at:{{{parts}}},\n  src:'data:image/webp;base64,{base64.b64encode(data).decode()}'}};   // {at.width}×{at.height} {len(data)}B"
    path = os.path.join(ROOT, 'index.html')
    src = open(path, encoding='utf-8').read()
    a = src.index('// BALL_ART ここから\n') + len('// BALL_ART ここから\n'); b = src.index('// BALL_ART ここまで')
    src = src[:a] + line + '\n' + src[b:]
    open(path, 'w', encoding='utf-8').write(src)
    print('balls', len(spec['balls']), 'cells', len(cells), 'atlas', at.size, 'bytes', len(data))
    if len(sys.argv) > 1:
        sheet(cells, spec, sys.argv[1])


def sheet(cells, spec, out):
    # 見本：上は 大きく（玉の 半径 60px）、下は ゲームの 中の 大きさ（半径 6.5×1.3×2＝13px くらい・鉛 17・BB 10）を 2つの 背景で
    K = spec['K']; names = list(spec['balls'].keys()); n = len(names); cols = 8
    big = 150; rows = (n + cols - 1) // cols
    S = Image.new('RGBA', (cols * big, rows * big + 2 * 60 * rows // 1), (8, 10, 32, 255))
    def place(img, k, x, y, R, ang=0):
        c, ax, ay = cells[k]; s = R / K
        cc = c.resize((max(1, round(c.width * s)), max(1, round(c.height * s))), Image.LANCZOS)
        if ang:
            # まわす 玉：からだを まわして つやを かさねる
            pad = Image.new('RGBA', (cc.width * 3, cc.height * 3), (0, 0, 0, 0)); pad.alpha_composite(cc, (cc.width, cc.height))
            pad = pad.rotate(ang, resample=Image.BICUBIC, center=(cc.width + ax * s, cc.height + ay * s))
            img.alpha_composite(pad, (round(x - ax * s - cc.width), round(y - ay * s - cc.height)))
        else:
            img.alpha_composite(cc, (round(x - ax * s), round(y - ay * s)))
        if k + '_g' in cells: place(img, k + '_g', x, y, R)
    for i, k in enumerate(names):
        x = (i % cols) * big + big // 2; y = (i // cols) * big + big // 2 + 8
        place(S, k, x, y, 52)
    y0 = rows * big
    small = {'lead': 6.5, 'bb': 4}
    for band, col in enumerate([(14, 12, 40, 255), (70, 60, 120, 255)]):
        ImageDraw.Draw(S).rectangle((0, y0 + band * 60 * rows // 2 * 1, S.width, y0 + (band + 1) * 60 * rows // 2), fill=col)
    for i, k in enumerate(names):
        for band in range(2):
            x = i * (S.width // n) + S.width // n // 2; y = y0 + band * 60 * rows // 2 + 30 * rows // 2
            place(S, k, x, y, small.get(k, 5) * 1.3 * 2)
    S.save(out); print('sheet', out)


if __name__ == '__main__':
    main()
