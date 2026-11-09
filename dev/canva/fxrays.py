# 光の すじ（サンバースト）の 絵を 作る（11/8 7.）：まん中から ひろがる 金と クリーム色の やわらかい すじと 小さな きらきら。
# Canva の 演出の 絵の うしろで まわす（FEVER・ボスを たおした・クリア・エンディング・台が あいた）。光だけの 絵なので コードで 作った（Canva の 回数を へらす）
# 使い方：cd dev/canva && python3 fxrays.py → fx/src/rays.png（すけすけの RGBA。ui.json の fx の "rgba":true で そのまま 使う）
import os
import numpy as np
from PIL import Image

HERE = os.path.dirname(os.path.abspath(__file__))
N = 1024; c = (N - 1) / 2
y, x = np.mgrid[0:N, 0:N].astype(np.float32)
dx, dy = x - c, y - c
r = np.hypot(dx, dy) / (N / 2); th = np.arctan2(dy, dx)
rng = np.random.default_rng(7)
# すじ：太い 12本＋細い 12本（すこし ずらす）。外へ いくほど うすく、まん中は ぼんやり
wide = np.clip(np.cos(th * 12) * .5 + .5, 0, 1) ** 2.4
thin = np.clip(np.cos(th * 12 + np.pi / 12 * 1.0) * .5 + .5, 0, 1) ** 14 * .55
fall = np.clip(1 - r, 0, 1) ** 1.6 * np.clip(r / .08, 0, 1) ** .5
ray = (wide * .7 + thin) * fall
core = np.exp(-(r / .16) ** 2) * .9 + np.exp(-(r / .4) ** 2) * .25
a = np.clip(ray + core, 0, 1)
# 色：まん中は 白、すじは 金→クリーム（太い すじは 金、細い すじは クリーム）
gold = np.array([1.0, .84, .29]); cream = np.array([1.0, .96, .78]); white = np.array([1.0, 1.0, 1.0])
k = np.clip(thin / (wide * .7 + thin + 1e-6), 0, 1)[..., None]
col = gold * (1 - k) + cream * k
wc = np.clip(core / (a + 1e-6), 0, 1)[..., None]
col = col * (1 - wc) + white * wc
img = np.dstack([col, a])
# きらきら（4つ角の 星）を すじの 上に 少し
for _ in range(16):
    rr = .22 + rng.random() * .62; t = rng.random() * np.pi * 2
    px, py = c + np.cos(t) * rr * N / 2, c + np.sin(t) * rr * N / 2
    s = 6 + rng.random() * 12
    ddx, ddy = np.abs(x - px), np.abs(y - py)
    star = np.clip(1 - (np.sqrt(ddx) * np.sqrt(ddy)) / (s * .9), 0, 1) * np.clip(1 - np.hypot(ddx, ddy) / (s * 2.2), 0, 1)
    star = np.clip(star * 1.6, 0, 1) * (1 - rr * .6)
    img[..., 3] = np.maximum(img[..., 3], star)
    img[..., :3] = img[..., :3] * (1 - star[..., None]) + cream * star[..., None]
out = os.path.join(HERE, 'fx', 'src', 'rays.png')
Image.fromarray((np.clip(img, 0, 1) * 255 + .5).astype(np.uint8), 'RGBA').save(out)
print(out)
