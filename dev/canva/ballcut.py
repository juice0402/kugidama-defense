# 玉の 絵を すけすけに（11/8 5.）：Canva の 玉は まんまるなので、背景けし（remove-background）は 使わずに まるで 切りぬく
# 使い方：python3 ballcut.py もとの絵.png 出す_full.png   （ふだんは ballfit.py が cut() を つかう。これは 1つだけ 見たいとき）
#   玉の 形（まる）は 背景の こん色と ちがう ところの いちばん大きな かたまりから さがす（中心と 半径）。
#   まるの 中は 不とうめい、まるの 外（ネオンの 光・ボムの 導火線・光の輪 など）は neoncut.py と 同じく 背景との ちがいで すけすけに。
#   出す絵の PNG の text に 玉の 中心と 半径（cx,cy,r）を 書く
import sys
import numpy as np
from PIL import Image, ImageDraw, ImageFilter, PngImagePlugin


def find_ball(d):
    # 背景との ちがいが 大きい ところの 外がわの ふちを、外から 中心へ むかう 線で さがす → まるを 合わせる（とび出た 部品は のぞく）
    m = d > 0.42
    H, W = m.shape
    ys, xs = np.where(m)
    cx, cy = xs.mean(), ys.mean()
    for _ in range(4):
        rs = []
        for a in np.linspace(0, 2 * np.pi, 120, endpoint=False):
            dx, dy = np.cos(a), np.sin(a)
            for t in np.arange(min(W, H) * .5, 0, -.5):
                x, y = int(round(cx + dx * t)), int(round(cy + dy * t))
                if 0 <= x < W and 0 <= y < H and m[y, x]:
                    rs.append((a, t)); break
        R = np.array([r for _, r in rs])
        med = np.median(R)
        ok = [(a, r) for a, r in rs if abs(r - med) < max(2.5, med * .05)]   # 導火線・光の輪 などで とび出た 所は のぞく
        P = np.array([[cx + np.cos(a) * r, cy + np.sin(a) * r] for a, r in ok])
        A = np.c_[2 * P, np.ones(len(P))]
        b = (P ** 2).sum(1)
        sol = np.linalg.lstsq(A, b, rcond=None)[0]
        cx, cy = sol[0], sol[1]
        r = np.sqrt(sol[2] + cx * cx + cy * cy)
    return cx, cy, r + .5


def cut(O, rin=None):
    # O＝もとの絵（0〜1 の float の RGB）→ すけすけの 絵（RGBA の float）と 玉の 中心・半径
    border = np.concatenate([O[0], O[-1], O[:, 0], O[:, -1]])
    bg = np.median(border, axis=0)
    d = np.abs(O - bg).max(axis=2)
    cx, cy, r = find_ball(d)
    if rin: r = rin
    S = 4   # まるの ふちを なめらかに
    H, W = d.shape
    mk = Image.new('L', (W * S, H * S), 0)
    ImageDraw.Draw(mk).ellipse(((cx - r) * S, (cy - r) * S, (cx + r) * S, (cy + r) * S), fill=255)
    disk = np.asarray(mk.resize((W, H), Image.LANCZOS)).astype(np.float32) / 255
    ag = np.clip((d - 0.035) * 1.5, 0, 1)   # まわりの光（うすく すける）
    solid = Image.fromarray(((d > 0.3) * 255).astype(np.uint8)).filter(ImageFilter.MinFilter(5)).filter(ImageFilter.MaxFilter(5))
    solid = np.asarray(solid.filter(ImageFilter.GaussianBlur(1))).astype(np.float32) / 255
    ag = np.maximum(ag, np.clip((d - 0.035) / 0.30, 0, 1) * solid)
    a = np.maximum(disk, ag)
    F = np.where(a[..., None] > 1e-3, (O - bg * (1 - a[..., None])) / np.maximum(a[..., None], 1e-3), 0)
    F = np.clip(F, 0, 1)
    F = F * (1 - disk[..., None]) + O * disk[..., None]
    return np.dstack([F, a]), cx, cy, r


def main(orig, out, rin=None):
    O = np.asarray(Image.open(orig).convert('RGB')).astype(np.float32) / 255
    res, cx, cy, r = cut(O, rin)
    info = PngImagePlugin.PngInfo(); info.add_text('ball', f'{cx:.2f},{cy:.2f},{r:.2f}')
    Image.fromarray((res * 255 + .5).astype(np.uint8), 'RGBA').save(out, pnginfo=info)
    print(out, f'cx {cx:.1f} cy {cy:.1f} r {r:.1f}')


if __name__ == '__main__':
    main(sys.argv[1], sys.argv[2], float(sys.argv[3]) if len(sys.argv) > 3 else None)
