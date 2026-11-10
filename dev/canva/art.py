# 台の奥の景色（bg）と 台の枠（frame）の 絵を ゲームに 入れる（11/8）
# 使い方：python3 art.py          … art.json の 絵を ぜんぶ WebP にして、index.html の ART_SRC（「ART_SRC ここから」〜「ここまで」）を 書きかえる
#         ONLY=meadow_frame,forest_frame python3 art.py … その 絵だけ 作りなおす（ほかの 行は そのまま）
#         python3 art.py 見る.png … ついでに 枠と 景色を 台の 形に かさねた 見本を 出す（さいごの 1つ）
#
# bg   ：Canva の 9:16 の 絵（1180×2100 など）。台の アーチの はば（RO*2+8＝340）で、下を H-6 に そろえて 置く。アーチの外は 見えないので 1色に（軽く）
#        art.json に "ridge" が あれば、手前の 地面の 光る ふちの 線を さがして ridge（台の座標の 点）に する（台の build の artFront で 使う）
# obj  ：台の中の 大きな物（杭と つながった ピラミッド・雪の結晶・火山）。objfit.py で 台の 点に 合わせて ゆがめ、すけすけに（11/9）
# frame：Canva の「まん中に アーチの窓（こい紺の 無地）が ある 枠の絵」。窓の形を 見つけて、台の アーチ（CX,CY,RO と 下の H-6）に ぴったり 合うように
#        ゆがめる（アーチの所は 角度ごとに、まっすぐの所は 行ごとに。窓の外の はばは そのままの 大きさ）。
#        できた 絵は 台の座標の FR（x -45〜405・y -60〜740）を おおう。外がわは base の色に だんだん とけこむ（コードで base を ぬってから 絵を 置く）。
#        光る木の実・宝石など 明るい 丸い 点を さがして glow（G.fruits の 光の ゆらぎ）に する
import sys, os, json, io, base64, re
import numpy as np
from PIL import Image
from scipy import ndimage as nd

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
CX, CY, RO, H = 180, 180, 166, 600
FB = H - 6                      # 台の 下の ふち（fieldPath の bottom）
FR = (-45, -60, 450, 800)       # 枠の絵が おおう ところ（台の座標）
FQ = 2.0                        # 枠の絵の こまかさ（1単位に 何ピクセル）→ 900×1600
BG_W = 720                      # 景色の 絵の はば


def hexc(c):
    return '#%02x%02x%02x' % tuple(int(max(0, min(255, v))) for v in c)


def field_mask(w, h, x0, y0, q, shrink=0):
    """台の アーチの中（fieldPath）の ピクセル。shrink で 内がわへ ちぢめる"""
    ys, xs = np.mgrid[0:h, 0:w]
    gx = x0 + (xs + .5) / q
    gy = y0 + (ys + .5) / q
    r = RO - shrink
    top = (gy < CY) & (np.hypot(gx - CX, gy - CY) < r)
    side = (gy >= CY) & (gy < FB - shrink) & (np.abs(gx - CX) < r)
    return top | side


def window(A):
    """枠の絵の まん中の 窓（こい 無地）を 見つける"""
    h, w, _ = A.shape
    L = A.max(axis=2)
    cy, cx = int(h * .45), w // 2
    ref = np.median(A[cy - 20:cy + 20, cx - 20:cx + 20].reshape(-1, 3), axis=0)
    d = np.abs(A - ref).max(axis=2)
    m = (d < 26) & (L < 90)
    m = nd.binary_opening(m, iterations=2)
    lab, n = nd.label(m)
    m = lab == lab[cy, cx]
    m = nd.binary_fill_holes(nd.binary_closing(m, iterations=4))
    return m, ref


def frame_warp(src, key, th=130, nmax=24, basek=.85):
    A = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
    h, w, _ = A.shape
    m, ref = window(A)
    rows = np.where(m.any(axis=1))[0]
    top = rows[0]
    mid = int(top + (rows[-1] - top) * .55)
    cols = np.where(m[mid])[0]
    acx = (cols[0] + cols[-1]) / 2
    a = (cols[-1] - cols[0]) / 2               # 窓の はばの 半分（ピクセル）
    p = a / RO                                 # 1単位に 何ピクセル（窓の はばで きめる）
    acy = top + a                              # アーチの 中心の 高さ（上が 半円と して）
    # 窓の下：まん中の 列で 窓が おわる 行（すみの 根っこ・草が 窓に かかっても だいじょうぶなように）
    bs = [np.where(m[:, int(x)])[0][-1] for x in np.linspace(acx - a * .4, acx + a * .4, 9) if m[:, int(x)].any()]
    bot = int(np.median(bs))
    # まっすぐの所の 左右の ふち：まん中あたりの 行の 中央値で まっすぐの 線に（こけ・根っこが かかっても ずれない）
    ys = np.arange(int(acy + (bot - acy) * .1), int(acy + (bot - acy) * .7))
    le = [np.where(m[y])[0][0] for y in ys if m[y].any()]; re_ = [np.where(m[y])[0][-1] + 1 for y in ys if m[y].any()]
    Lr = np.full(h, float(np.median(le))); Rr = np.full(h, float(np.median(re_)))
    # アーチの所：角度ごとの 窓の ふちまでの きょり
    ang = np.linspace(-np.pi, 0, 721)
    dd = np.zeros_like(ang)
    for i, t in enumerate(ang):
        for s in np.arange(1, max(w, h)):
            x, y = acx + np.cos(t) * s, acy + np.sin(t) * s
            if x < 0 or y < 0 or x >= w - 1 or y >= h - 1 or not m[int(y), int(x)]:
                dd[i] = s; break
    dd[0], dd[-1] = acx - Lr[int(acy)], Rr[int(acy)] - acx   # 横は まっすぐの所と つなぐ
    e0, e1 = dd[0], dd[-1]
    dd = nd.uniform_filter1d(nd.maximum_filter1d(dd, 41, mode='nearest'), 41, mode='nearest')   # こけが たれた所は 窓が せまく 見えるので 大きい方へ
    # 11/10 しょーくん「アーチが はじまる 所で オレンジの 線が ずれてる」：ならしたので 横（はし）の きょりが まっすぐの所と 合わなく なっていた。
    # はしから 15度 かけて まっすぐの所の きょりへ もどす（アーチと まっすぐの所の つなぎめで 線が つながる）
    nr = 60; ramp = .5 + .5 * np.cos(np.pi * np.arange(nr) / nr)
    dd[:nr] += (e0 - dd[0]) * ramp; dd[-nr:] += ((e1 - dd[-1]) * ramp)[::-1]
    # 台の座標 → 絵の 点
    x0, y0, fw, fh = FR
    W2, H2 = int(fw * FQ), int(fh * FQ)
    ys, xs = np.mgrid[0:H2, 0:W2]
    gx = x0 + (xs + .5) / FQ
    gy = y0 + (ys + .5) / FQ
    ax = np.zeros_like(gx); ay = np.zeros_like(gy)
    # アーチの所（CY より上）
    T = gy < CY
    dx, dy = gx[T] - CX, gy[T] - CY
    r = np.hypot(dx, dy); t = np.arctan2(dy, dx)
    t = np.where(t > 0, np.where(dx < 0, -np.pi, 0), t)
    d = np.interp(t, ang, dd)
    ad = np.where(r >= RO, d + (r - RO) * p, r / RO * d)
    ax[T] = acx + np.cos(t) * ad; ay[T] = acy + np.sin(t) * ad
    # まっすぐの所（CY〜台の下）
    S = (gy >= CY) & (gy <= FB)
    yy = acy + (gy[S] - CY) / (FB - CY) * (bot - acy)
    li = np.interp(yy, np.arange(h), Lr); ri = np.interp(yy, np.arange(h), Rr)
    g = gx[S]
    ax[S] = np.where(g < CX - RO, li - (CX - RO - g) * p, np.where(g > CX + RO, ri + (g - CX - RO) * p, li + (g - (CX - RO)) / (2 * RO) * (ri - li)))
    ay[S] = yy
    # 下（台の 下の ふちより下）
    B = gy > FB
    lb, rb = Lr[bot], Rr[bot]
    g = gx[B]
    ax[B] = np.where(g < CX - RO, lb - (CX - RO - g) * p, np.where(g > CX + RO, rb + (g - CX - RO) * p, lb + (g - (CX - RO)) / (2 * RO) * (rb - lb)))
    ay[B] = bot + (gy[B] - FB) * p
    out = np.stack([nd.map_coordinates(A[..., k], [np.clip(ay, 0, h - 1), np.clip(ax, 0, w - 1)], order=1, mode='nearest') for k in range(3)], axis=2)
    # 台の中は 見えないので 1色に（軽く）
    inside = field_mask(W2, H2, x0, y0, FQ, shrink=3)
    out[inside] = ref
    # まわりの色（base）に だんだん とけこむ：上 8・左右 18・下 14 単位
    edge = np.concatenate([out[2, :], out[-3, :], out[:, 2], out[:, -3]])
    base = np.median(edge, axis=0) * basek   # まわりの色（art.json の "basek"。枠の ふちが 明るい 絵は 小さく して 暗く とけこませる）
    fx = np.minimum((gx - x0) / 18, (x0 + fw - gx) / 18)
    fy = np.minimum((gy - y0) / 8, (y0 + fh - gy) / 14)
    f = np.clip(np.minimum(fx, fy), 0, 1); f = f * f * (3 - 2 * f)
    out = out * f[..., None] + base * (1 - f[..., None])
    # 光る点（木の実・宝石など：ぼかした 明るさの 山）→ glow。th より明るい 山だけ（絵ごとに art.json の glow で かえられる）
    Y = nd.gaussian_filter(out.mean(axis=2), 6)
    vis = (~field_mask(W2, H2, x0, y0, FQ, shrink=-1)) & (gx > -25) & (gx < 385) & (gy > -58) & (gy < 735)
    pk = (Y == nd.maximum_filter(Y, size=30)) & (Y > th) & vis
    glow = []
    keep = []   # 近い 山は いちばん明るい 1つだけ（大きい きのこに 光が いくつも つかないように）
    for py, px in sorted(zip(*np.where(pk)), key=lambda q: -Y[q]):
        if all((py - a) ** 2 + (px - b) ** 2 > 30 ** 2 for a, b in keep): keep.append((py, px))
    keep = keep[:nmax]   # 多すぎると 毎フレーム 重いので 明るい方から nmax こ（art.json の "nglow"。ふつう 24）
    for py, px in keep:
        R = 14
        y1, y2, x1, x2 = max(0, py - R), min(H2, py + R), max(0, px - R), min(W2, px + R)
        P = out[y1:y2, x1:x2].reshape(-1, 3)
        sat = P.max(axis=1) - P.min(axis=1)
        col = P[np.argsort(sat)[-max(3, len(P) // 10):]].mean(axis=0)
        col = col / max(1, col.max()) * 255
        glow.append([round(x0 + px / FQ, 1), round(y0 + py / FQ, 1), round(min(4, 2.2 + (Y[py, px] - th) / 60), 1), hexc(col)])
    glow.sort(key=lambda g: (g[1], g[0]))
    print(key, 'window', dict(top=int(top), bot=int(bot), a=round(a, 1), p=round(p, 3)), 'glow', len(glow))
    im = Image.fromarray(np.clip(out, 0, 255).astype(np.uint8))
    return im, dict(x=x0, y=y0, w=fw, h=fh, base=hexc(base), glow=glow)


def ridge_line(A, x0, y0, k, spec):
    """手前の 地面の 光る ふちの 線（ridge）を さがす → [[x,y],...]（台の座標）。spec＝{"y":[上,下],"w":[R,G,B の おもみ]}。
    台の build で artFront が この線より下を もう一度 かさねて、コードで 描いた 大きな物（ピラミッド など）の すそを 地面の うしろに かくす。
    spec に "line" が あれば さがさずに その 点を そのまま 使う"""
    if 'line' in spec: return spec['line']   # 線を 手で きめる（地面の 光る ふちが 高すぎる 絵。台の座標の 点）
    h, w, _ = A.shape
    lo, hi = [int((v - y0) * k) for v in spec['y']]
    sc = (A[lo:hi] * np.array(spec.get('w', [1, 1, 1]), dtype=np.float32)).sum(axis=2)
    sc = nd.gaussian_filter(sc, 2)
    ys = np.argmax(sc, axis=0) + lo
    ys = nd.median_filter(ys.astype(float), 31, mode='nearest')
    ys = nd.uniform_filter1d(ys, 15, mode='nearest')
    pts = []
    for px in list(range(0, w - 12, 24)) + [w - 1]:
        pts.append([round(x0 + px / k, 1), round(y0 + ys[px] / k, 1)])
    return pts


def bg_fit(src, key, ridge=None):
    im = Image.open(src).convert('RGB')
    w, h = BG_W, round(im.height * BG_W / im.width)
    im = im.resize((w, h), Image.LANCZOS)
    gw = RO * 2 + 8; gh = gw * h / w
    x0, y0 = CX - gw / 2, FB - gh
    A = np.asarray(im).astype(np.float32)
    meta = dict(x=round(x0, 2), y=round(y0, 2), w=gw, h=round(gh, 2))
    if ridge: meta['ridge'] = ridge_line(A, x0, y0, w / gw, ridge); print(key, 'ridge', meta['ridge'][::8])
    inside = field_mask(w, h, x0, y0, w / gw, shrink=-3)
    A[~inside] = np.median(A[~inside], axis=0)          # アーチの外は 見えないので 1色に
    return Image.fromarray(A.astype(np.uint8)), meta


def webp(im, q):
    b = io.BytesIO(); im.save(b, 'WEBP', quality=q, method=6); return b.getvalue()


def main():
    spec = json.load(open(os.path.join(HERE, 'art.json')))
    os.makedirs(os.path.join(HERE, 'art'), exist_ok=True)
    lines = []; last = {}
    p = os.path.join(ROOT, 'index.html')
    html = open(p, encoding='utf-8').read()
    a, b = '// ART_SRC ここから\n', '// ART_SRC ここまで'
    i, j = html.index(a) + len(a), html.index(b)
    # ONLY=キー,キー で その 絵だけ 作りなおす（ほかは いまの 行の まま。11/10）
    only = [k for k in os.environ.get('ONLY', '').split(',') if k]
    old = {m.group(1): m.group(0) for m in re.finditer(r'^  (\w+):\{.*$', html[i:j], re.M)}
    for key, s in spec.items():
        if only and key not in only and key in old:
            lines.append(old[key]); continue
        src = os.path.join(HERE, s['src'])
        if s['kind'] == 'obj':   # 台の中の 大きな物（objfit.py）。すけすけの WebP
            from objfit import obj_fit
            im, meta = obj_fit(s); data = webp(im, s.get('q_webp', 80))
        else:
            im, meta = frame_warp(src, key, s.get('glow', 130), s.get('nglow', 24), s.get('basek', .85)) if s['kind'] == 'frame' else bg_fit(src, key, s.get('ridge'))
            data = webp(im, s.get('q', 78))
        open(os.path.join(HERE, 'art', key + '.webp'), 'wb').write(data)
        if s['kind'] != 'obj': last[s['kind']] = (im, meta)
        g = ''.join(f"[{a},{b},{c},'{d}']," for a, b, c, d in meta.get('glow', [])).rstrip(',')
        extra = ''
        if s['kind'] == 'frame':
            for k in ('cut', 'lift'):
                if k in s: extra += f",{k}:{s[k]}"
            extra += f",base:'{meta['base']}',glow:[{g}]"
        if 'ridge' in meta: extra += ',ridge:[' + ','.join(f'[{a},{b}]' for a, b in meta['ridge']) + ']'
        lines.append(f"  {key}:{{x:{meta['x']},y:{meta['y']},w:{meta['w']},h:{meta['h']}{extra},src:'data:image/webp;base64,{base64.b64encode(data).decode()}'}},   // {im.width}×{im.height} {len(data)//1024}KB")
        print(key, im.size, len(data), 'bytes')
    html = html[:i] + '\n'.join(lines) + '\n' + html[j:]
    open(p, 'w', encoding='utf-8').write(html)
    print('index.html ART_SRC', len(lines))
    if len(sys.argv) > 1 and 'frame' in last and 'bg' in last:   # 見本：枠＋景色
        fim, fm = last['frame']; bim, bm = last['bg']
        k = FQ; v = Image.new('RGB', fim.size); v.paste(fim)
        big = bim.resize((round(bm['w'] * k), round(bm['h'] * k)), Image.LANCZOS)
        mk = Image.fromarray((field_mask(*fim.size, fm['x'], fm['y'], k) * 255).astype(np.uint8))
        lay = Image.new('RGB', fim.size); lay.paste(big, (round((bm['x'] - fm['x']) * k), round((bm['y'] - fm['y']) * k)))
        v.paste(lay, (0, 0), mk); v.save(sys.argv[1]); print('見本', sys.argv[1])


if __name__ == '__main__':
    main()
