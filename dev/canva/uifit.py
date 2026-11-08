# UI の 絵（ボタンの 板・パネルの わく・アイコン）を ゲームに 入れる（11/8 6. の 後半）
# 使い方：cd dev/canva && python3 uifit.py [見本.png]
#   ui.json の 絵を すけすけに して WebP に し、index.html の CSS の UI_ART（「UI_ART ここから」〜「ここまで」）を 書きかえる。手で 書かない
#
# もとの絵（ui/src/〇〇.png）：Canva の 絵（こい紺の 無地の 背景）。板・わくは 作業用デザインの 480×480 の ページの 見本（600×600）
# すけすけ：背景の 色との ちがいが 大きい 太い かたまり（穴は うめる）＝不とうめい、まわりの 光は ちがいの 大きさで うすく（neoncut.py と 同じ 考え）
#
# plates（板・わく。CSS の border-image の 9わけ＝9-slice で のびちぢみ）：
#   "src"・"r"＝角の まるみ（もとの絵の px。角の 所は のびない）・"rt"/"rb"（上・下だけ かえる）・"q"
#   "from"＝ほかの 板の もとの絵を 使う ＋ "hue"（色あいを まわす 度）・"sat"（あざやかさの 倍率）・"val"（明るさの 倍率）＝hue.py と 同じ まわし方
#   "use"＝この 板を 使う CSS の セレクタ（ここに 書いた 所に border-image が つく）
#   ゲームの中：border-image の はば＝もとの絵の px × --k（その ボタンの CSS で きめる 長さ。--k:.25px なら 絵の 4px が 画面の 1px。角の まるみが r×k に なる）。光は 外へ（outset）
#   まん中の のびる 所は 1/4 に ちぢめて 入れる（つづいているので つなぎめは 出ない）
# icons（アイコン）："src"・"px"＝WebP の 大きさ（正方形・ふつう 96＝32px を dpr3）・"pad"（まわりの すきま 割合）・"q"
#   ゲームの中：CSS の 変数 --i-〇〇（:root。background-image に 使う。台の ハートは JS が この 変数から 絵を よむ）
import sys, os, json, io, base64, re
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
CFG = json.load(open(os.path.join(HERE, 'ui.json'), encoding='utf-8'))


def hue_rot(A, deg, sat=1, val=1):   # hue.py と 同じ（A は 0〜1 の RGB）
    if not deg and sat == 1 and val == 1: return A
    mx = A.max(2); mn = A.min(2); d = mx - mn
    h = np.zeros_like(mx); r, g, b = A[..., 0], A[..., 1], A[..., 2]; m = d > 1e-6
    i = m & (mx == r); h[i] = ((g - b)[i] / d[i]) % 6
    i = m & (mx == g) & ~(mx == r); h[i] = (b - r)[i] / d[i] + 2
    i = m & (mx == b) & ~(mx == r) & ~(mx == g); h[i] = (r - g)[i] / d[i] + 4
    h = (h / 6 + deg / 360) % 1
    s = np.clip(np.where(mx > 0, d / np.maximum(mx, 1e-6), 0) * sat, 0, 1); v = np.clip(mx * val, 0, 1)
    k = lambda n: (n + h * 6) % 6
    f = lambda n: v - v * s * np.clip(np.minimum(k(n), 4 - k(n)), 0, 1)
    return np.dstack([f(5), f(3), f(1)])


def load(J):
    src = J.get('src') or CFG['plates'][J['from']]['src']
    A = np.asarray(Image.open(os.path.join(HERE, src)).convert('RGB')).astype(np.float32) / 255
    border = np.concatenate([A[0], A[-1], A[:, 0], A[:, -1]])
    bg = np.median(border, axis=0)
    d = np.abs(A - bg).max(axis=2)
    solid = nd.binary_fill_holes(nd.binary_opening(d > J.get('solid', .3), iterations=2))
    lab, n = nd.label(solid)
    if n > 1:   # 小さい かけらは 光として あつかう
        sz = nd.sum(solid, lab, range(1, n + 1)); keep = [i + 1 for i, s in enumerate(sz) if s > sz.max() * J.get('bits', .02)]
        solid = np.isin(lab, keep)
    sa = nd.gaussian_filter(solid.astype(np.float32), .7)
    ag = np.clip((d - .035) * 1.5, 0, 1)
    a = np.maximum(sa, ag)
    F = np.where(a[..., None] > 1e-3, (A - bg * (1 - a[..., None])) / np.maximum(a[..., None], 1e-3), 0)
    F = np.clip(F, 0, 1)
    F = hue_rot(F, J.get('hue', 0), J.get('sat', 1), J.get('val', 1))
    if J.get('alpha'): a = a * J['alpha']
    return np.dstack([F, a]), solid


def webp(img, q):
    b = io.BytesIO(); img.save(b, 'WEBP', quality=q, method=6, alpha_quality=90); return b.getvalue()


def plate(key, J):
    R, solid = load(J)
    ys, xs = np.nonzero(solid)
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    a = R[..., 3]
    gy, gx = np.nonzero(a > .03)
    m = int(max(x0 - gx.min(), gx.max() + 1 - x1, y0 - gy.min(), gy.max() + 1 - y1, 2))
    m = min(m, J.get('glow', 24))
    X0, X1, Y0, Y1 = max(0, x0 - m), x1 + m, max(0, y0 - m), y1 + m
    C = R[Y0:Y1, X0:X1]
    h, w = C.shape[:2]
    r = J['r']; L = m + J.get('rl', r); Rr = m + J.get('rr', r); T = m + J.get('rt', r); B = m + J.get('rb', r)
    # まん中の のびる 所（横）を 1/4 に ちぢめる
    mid = C[:, L:w - Rr]; nm = max(6, mid.shape[1] // J.get('squeeze', 4))
    mid = np.asarray(Image.fromarray((mid * 255 + .5).astype(np.uint8), 'RGBA').resize((nm, h), Image.LANCZOS)).astype(np.float32) / 255
    C = np.concatenate([C[:, :L], mid, C[:, w - Rr:]], axis=1)
    # たても 長い 板（パネル）は ちぢめる
    if J.get('vsqueeze'):
        h = C.shape[0]; midv = C[T:h - B]; nv = max(6, midv.shape[0] // J['vsqueeze'])
        midv = np.asarray(Image.fromarray((midv * 255 + .5).astype(np.uint8), 'RGBA').resize((C.shape[1], nv), Image.LANCZOS)).astype(np.float32) / 255
        C = np.concatenate([C[:T], midv, C[h - B:]], axis=0)
    img = Image.fromarray((np.clip(C, 0, 1) * 255 + .5).astype(np.uint8), 'RGBA')
    data = webp(img, J.get('q', 86))
    k = 'var(--k)'   # --k は 長さ（.25px など。ホールの 台は --cw から calc で）
    rule = (f"{', '.join(J['use'])}{{border-image:url(data:image/webp;base64,{base64.b64encode(data).decode()}) {T} {Rr} {B} {L} fill/"
            f"calc({k}*{T}) calc({k}*{Rr}) calc({k}*{B}) calc({k}*{L})/calc({k}*{m}) stretch}}")
    print(f'plate {key}: {img.size} slice T{T} R{Rr} B{B} L{L} glow{m} body {x1-x0}x{y1-y0} webp {len(data)//1024}KB')
    return rule, img, dict(T=T, R=Rr, B=B, L=L, m=m)


def icon(key, J):
    R, solid = load(J)
    a = R[..., 3]
    ys, xs = np.nonzero(a > J.get('cut', .04))
    x0, x1, y0, y1 = xs.min(), xs.max() + 1, ys.min(), ys.max() + 1
    cx, cy = (x0 + x1) / 2, (y0 + y1) / 2
    if 'c' in J: cx, cy = J['c']
    s = max(x1 - x0, y1 - y0) * (1 + J.get('pad', .04))
    if 'box' in J: s = J['box']
    img = Image.fromarray((np.clip(R, 0, 1) * 255 + .5).astype(np.uint8), 'RGBA')
    img = img.crop((int(round(cx - s / 2)), int(round(cy - s / 2)), int(round(cx + s / 2)), int(round(cy + s / 2))))
    px = J.get('px', 96)
    img = img.resize((px, px), Image.LANCZOS)
    data = webp(img, J.get('q', 86))
    print(f'icon {key}: {px}px webp {len(data)//1024}KB ({len(data)}B)')
    return f"--i-{key}:url(data:image/webp;base64,{base64.b64encode(data).decode()})", img


def sheet(plates, icons, out):
    # 見本：上に 板（いろいろな 大きさに のばした 絵）、下に アイコン（大・小）
    W = 1100; rows = []
    for key, (img, S) in plates.items():
        row = Image.new('RGBA', (W, 150), (16, 12, 34, 255))
        x = 10
        for (bw, bh, k) in [(300, 58, .3), (220, 46, .24), (120, 34, .17), (80, 28, .14), (360, 120, .35)]:
            k2 = k * J_k(key)
            bi = nine(img, S, bw, bh, k2)
            row.alpha_composite(bi, (x, 75 - bi.height // 2)); x += bi.width + 8
        rows.append(row)
    if icons:
        row = Image.new('RGBA', (W, 120), (16, 12, 34, 255)); x = 10
        for key, img in icons.items():
            row.alpha_composite(img.resize((72, 72), Image.LANCZOS), (x, 6))
            row.alpha_composite(img.resize((26, 26), Image.LANCZOS), (x + 23, 84)); x += 80
        rows.append(row)
    H = sum(r.height for r in rows) + 4 * len(rows)
    c = Image.new('RGBA', (W, H), (255, 255, 255, 255)); y = 0
    for r in rows: c.alpha_composite(r, (0, y)); y += r.height + 4
    c.convert('RGB').save(out)


def J_k(key): return CFG['plates'][key].get('k', 1)


def nine(img, S, bw, bh, k):
    # border-image と 同じに 描く（見本用）
    T, R, B, L, m = S['T'], S['R'], S['B'], S['L'], S['m']
    o = m * k; W, H = round(bw + 2 * o), round(bh + 2 * o)
    w, h = img.size
    out = Image.new('RGBA', (W, H))
    tw, rw, bw2, lw = [max(1, round(v * k)) for v in (T, R, B, L)]
    xs = [(0, L, 0, lw), (L, w - R, lw, W - rw), (w - R, w, W - rw, W)]
    ys = [(0, T, 0, tw), (T, h - B, tw, H - bw2), (h - B, h, H - bw2, H)]
    for (sx0, sx1, dx0, dx1) in xs:
        for (sy0, sy1, dy0, dy1) in ys:
            if dx1 - dx0 < 1 or dy1 - dy0 < 1 or sx1 - sx0 < 1 or sy1 - sy0 < 1: continue
            out.alpha_composite(img.crop((sx0, sy0, sx1, sy1)).resize((dx1 - dx0, dy1 - dy0), Image.LANCZOS), (dx0, dy0))
    return out


def main():
    rules, vars_, P, I = [], [], {}, {}
    for key, J in CFG.get('plates', {}).items():
        rule, img, S = plate(key, J); rules.append(rule); P[key] = (img, S)
        img.save(os.path.join(HERE, 'ui', key + '.png'))
    for key, J in CFG.get('icons', {}).items():
        v, img = icon(key, J); vars_.append(v); I[key] = img
        img.save(os.path.join(HERE, 'ui', 'i_' + key + '.png'))
    block = ':root{' + ';'.join(vars_) + '}\n' + '\n'.join(rules) + '\n'
    path = os.path.join(ROOT, 'index.html')
    html = open(path, encoding='utf-8').read()
    a = '/* UI_ART ここから（dev/canva/uifit.py が 書く。手で 書かない） */\n'
    b = '/* UI_ART ここまで */'
    i, j = html.index(a), html.index(b)
    html = html[:i + len(a)] + block + html[j:]
    open(path, 'w', encoding='utf-8').write(html)
    print('index.html UI_ART', len(block) // 1024, 'KB')
    if len(sys.argv) > 1: sheet(P, I, sys.argv[1])


if __name__ == '__main__':
    main()
