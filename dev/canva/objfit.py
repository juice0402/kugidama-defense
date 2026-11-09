# 台の中の 大きな物（杭と つながった ピラミッド・雪の結晶・火山）の Canva の 絵を、台の 座標に 合わせて ゆがめて 切りぬく（11/9）
# art.py が 使う（art.json の "kind":"obj"）。ひとつだけ ためす：python3 objfit.py キー 見本.png
#
# art.json の obj：
#   "src"  ：Canva の 絵を 大きく 取った もの（objs/src/〇〇.png。こい紺の 無地の 背景）
#   "pts"  ：[[絵の x, 絵の y, 台の x, 台の y], ...]（絵の 点 → 台の 点。3つなら そのまま ゆがめる、4つ以上なら 三角に わけて ゆがめる）
#   "box"  ：[x0, y0, x1, y1]（台の 座標で 絵を 置く 所）・"q"：1単位に 何ピクセル（ふつう 2.2）
#   "poly" ：[[台の x, 台の y], ...]（この 形の 中は 不とうめい。外は 背景の 紺との ちがいで すけすけの 光。なければ ぜんぶ 光の すけすけ）
#   "shrink"：poly を この はばだけ 内がわへ（ふちの 線が 少し ずれても 紺が 出ないように）
#   "fadey"：[y0, y1]（台の y0 から y1 へ だんだん すける）
#   "dark" ：[こさ, ...]（金・水色など 明るい 線は そのままで、むらさきなどの 面だけ くらく。台の まん中は 暗めに）
#   "inner"：[こさ, はば]（形の 中で ふちから はば より 内がわの 線を くらく）・"keep"：[[台の x, 台の y, 半径], ...]（くらく しない 所）
#   "dim"  ：[[台の x, 台の y, 半径, こさ], ...]（円の 中を くらく。ふちの 外 10 で もとに もどる）
#   "solid"：背景との ちがいが これより 大きい所は 不とうめい（光の すけすけでは なく 物として。ふつう なし）
import sys, os, json
import numpy as np
from PIL import Image, ImageDraw
from skimage.transform import PiecewiseAffineTransform, AffineTransform, warp
from scipy import ndimage as nd

HERE = os.path.dirname(os.path.abspath(__file__))


def obj_fit(s):
    O = np.asarray(Image.open(os.path.join(HERE, s['src'])).convert('RGB')).astype(np.float64) / 255
    x0, y0, x1, y1 = s['box']; q = s.get('q', 2.2)
    W, H = round((x1 - x0) * q), round((y1 - y0) * q)
    P = np.array(s['pts'], float)
    src = P[:, :2]; dst = np.c_[(P[:, 2] - x0) * q, (P[:, 3] - y0) * q]
    aff = AffineTransform.from_estimate(dst, src)
    if len(P) > 3:   # 外がわは まっすぐ のばす（絵の かどを 足す）
        cs = np.array([[0, 0], [W, 0], [0, H], [W, H], [W / 2, 0], [W / 2, H], [0, H / 2], [W, H / 2]], float)
        T = PiecewiseAffineTransform.from_estimate(np.r_[dst, cs], np.r_[src, aff(cs)])
    else:
        T = aff
    bord = np.concatenate([O[0], O[-1], O[:, 0], O[:, -1]]); bg = np.median(bord, axis=0)
    Wp = np.dstack([warp(O[..., i], T, output_shape=(H, W), order=3, mode='constant', cval=bg[i]) for i in range(3)])
    Wp = np.clip(Wp, 0, 1)
    ys, xs = np.mgrid[0:H, 0:W]
    mp = T(np.c_[xs.ravel(), ys.ravel()].astype(float)).reshape(H, W, 2)   # 絵の 外から 来る 所は 何も ない（すける）
    hs, ws = O.shape[:2]
    out_m = np.minimum(np.minimum(mp[..., 0], ws - 1 - mp[..., 0]), np.minimum(mp[..., 1], hs - 1 - mp[..., 1]))
    valid = np.clip(out_m / 6, 0, 1)
    d = np.abs(Wp - bg).max(axis=2)
    a = np.clip((d - .035) * 1.5, 0, 1)                    # まわりの 光（すけすけ）
    if 'solid' in s:
        a = np.maximum(a, np.clip((d - s['solid']) / .08, 0, 1))
    if 'poly' in s:   # 形の 中は 不とうめい（4倍で 描いて ちぢめる＝ふちが なめらか）
        k = 4; m = Image.new('L', (W * k, H * k), 0)
        ImageDraw.Draw(m).polygon([((x - x0) * q * k, (y - y0) * q * k) for x, y in s['poly']], fill=255)
        m = np.asarray(m.resize((W, H), Image.LANCZOS)).astype(np.float64) / 255
        if s.get('shrink'):   # 形を 少し 内がわへ（ふちの ネオンの 線は 光の すけすけで）
            m = np.clip((nd.distance_transform_edt(m > .5) - s['shrink'] * q) / 1.5, 0, 1)
        a = np.maximum(a, m)
    a = a * valid
    if 'fadey' in s:   # 下の はしを だんだん すかす（台の 座標の y0〜y1。手前の 地面に とける）
        f0, f1 = s['fadey']
        a = a * np.clip((f1 - (y0 + (ys + .5) / q)) / (f1 - f0), 0, 1)
    F = np.where(a[..., None] > 1e-3, (Wp - bg * (1 - a[..., None])) / np.maximum(a[..., None], 1e-3), 0)
    F = np.clip(F, 0, 1)
    if 'dark' in s:   # 面だけ くらく（金・水色の 線は みどりが 多い。むらさきの 面は みどりが ほとんど ない）
        lit = np.clip((F[..., 1] - .2) / .3, 0, 1)[..., None]
        F = F * (s['dark'] + (1 - s['dark']) * lit)
    if 'inner' in s and 'poly' in s:   # 形の 中の 線（石の めじ など）を 少し くらく。ふちの ネオンと keep の 円（宝石 など）は そのまま
        k, mg = s['inner'][0], s['inner'][1] * q
        inside = nd.distance_transform_edt(m > .5) > mg
        ys, xs = np.mgrid[0:H, 0:W]
        for cx, cy, r in s.get('keep', []):
            inside &= np.hypot(xs - (cx - x0) * q, ys - (cy - y0) * q) > r * q
        f = nd.gaussian_filter(np.where(inside, k, 1.0), 2)[..., None]
        F = F * f
    if 'dim' in s:   # 円の 中を 少し くらく（台の まん中の 明るい 物。おばけや 玉が 見えるように）
        ys, xs = np.mgrid[0:H, 0:W]
        for cx, cy, r, k in s['dim']:
            t = np.clip((np.hypot(xs - (cx - x0) * q, ys - (cy - y0) * q) - r * q) / (10 * q), 0, 1)
            a = a * (k + (1 - k) * t)                        # すけさせる（白い 物は 白い まま うすく）
    im = Image.fromarray((np.dstack([F, a]) * 255 + .5).astype(np.uint8), 'RGBA')
    meta = dict(x=x0, y=y0, w=x1 - x0, h=y1 - y0)
    return im, meta


if __name__ == '__main__':
    spec = json.load(open(os.path.join(HERE, 'art.json')))
    im, meta = obj_fit(spec[sys.argv[1]])
    print(sys.argv[1], im.size, meta)
    if len(sys.argv) > 2:
        v = Image.new('RGBA', im.size, (40, 30, 60, 255)); v.alpha_composite(im); v.save(sys.argv[2])
