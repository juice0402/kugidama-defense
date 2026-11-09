# 景色の絵の 手なおし（11/9。しょーくん「かくれてる絵を 直して」）
# コードで 描く 物（洋館の 燭台・砂漠の オベリスク・天国の 羽の杭）の うしろに かくれていた 絵を、景色の 中で うごかす
# 使い方：python3 bgfix.py [mansion|desert|heaven ...]  → bg/〇〇_full.png を 書きかえる（そのあと python3 art.py）
#   もとの Canva の 絵は bg/orig/〇〇_full.png（なければ git の 521faf5 から 出す：
#   git show 521faf5:dev/canva/bg/〇〇_full.png > bg/orig/〇〇_full.png）
# 台の座標 → 絵の ピクセル：s＝絵の はば/340、X=(x-10)*s、Y=(y-oy)*s（oy＝594-絵の 高さ/s）＝ art.py の 置き方
import sys, os
import numpy as np
from PIL import Image
from scipy import ndimage as nd

HERE = os.path.dirname(os.path.abspath(__file__))


def load(name):
    p = os.path.join(HERE, 'bg', 'orig', name + '_full.png')
    return np.asarray(Image.open(p).convert('RGB')).astype(np.float32)


def save(name, A):
    Image.fromarray(np.clip(A + .5, 0, 255).astype(np.uint8)).save(os.path.join(HERE, 'bg', name + '_full.png'))


def harmonic(A, M, k=4, it=1500):
    """M（True の ところ）を まわりの 色から なめらかに うめる（ラプラスの 式。1/k の 小ささで といて もどす）"""
    h, w, _ = A.shape
    sm = nd.uniform_filter(A, size=(k * 2 + 1, k * 2 + 1, 1))[::k, ::k].copy()
    m = M[::k, ::k]
    sm[m] = sm[~m].mean(axis=0)
    for _ in range(it):
        av = (np.roll(sm, 1, 0) + np.roll(sm, -1, 0) + np.roll(sm, 1, 1) + np.roll(sm, -1, 1)) / 4
        sm[m] = av[m]
    up = np.asarray(Image.fromarray(np.clip(sm, 0, 255).astype(np.uint8)).resize((w, h), Image.BICUBIC)).astype(np.float32)
    return up


def feather(h, w, f):
    """ふちが f ピクセルで だんだん 0 に なる 四角の 重み"""
    y = np.minimum(np.arange(h), np.arange(h)[::-1]) / f
    x = np.minimum(np.arange(w), np.arange(w)[::-1]) / f
    return np.clip(np.minimum(y[:, None], x[None, :]), 0, 1)


def move_patch(A, box, dx, pad=40, f=14):
    """box（x0,y0,x1,y1）の 絵を よこに dx うごかす。うしろの かべは まわりから なめらかに うめて、
    すじの こまかい もようは 絵の 外の かべから うつす"""
    x0, y0, x1, y1 = box
    B = A.copy()
    X0, X1 = min(x0, x0 + dx) - pad, max(x1, x1 + dx) + pad
    Y0, Y1 = y0 - pad, y1 + pad
    R = A[Y0:Y1, X0:X1]
    M = np.zeros(R.shape[:2], bool); M[pad:pad + y1 - y0, x0 - X0:x1 - X0] = True
    lo = harmonic(R, M)                                     # 絵が ない ときの かべの なめらかな 色（絵の まわりから）
    lo[~M] = nd.uniform_filter(R, size=(9, 9, 1))[~M]
    w0 = x1 - x0
    src_x = x1 + 2 if dx > 0 else x0 - w0 - 2              # かべの ある がわ
    tex = A[y0:y1, src_x:src_x + w0]
    tex = tex - nd.uniform_filter(tex, size=(1, 15, 1))   # こまかい もようだけ
    # 1) もとの 場所を かべに（ふちは まわりに とけこむ）
    fill = lo[pad:pad + y1 - y0, x0 - X0:x1 - X0] + tex
    w1 = feather(y1 - y0, w0, 6)[..., None]
    B[y0:y1, x0:x1] = fill * w1 + A[y0:y1, x0:x1] * (1 - w1)
    # 2) 絵を ずらして 置く：かべの 色の ちがいを なおしてから、ふちを ぼかして かさねる
    lo_old = lo[pad:pad + y1 - y0, x0 - X0:x1 - X0]
    lo_new = nd.uniform_filter(B, size=(9, 9, 1))[y0:y1, x0 + dx:x1 + dx]
    P = A[y0:y1, x0:x1] - lo_old + lo_new
    w = feather(y1 - y0, w0, f)[..., None]
    B[y0:y1, x0 + dx:x1 + dx] = P * w + B[y0:y1, x0 + dx:x1 + dx] * (1 - w)
    return B


def mansion():
    # ねこ耳おばけの 肖像画 2つ：かべの 燭台（50,318）（326,318）の ろうそくが がくの 外がわに かさなっていた
    # → 内がわへ 35px（台で 12）ずらす。ろうそくは がくの 外に 出て、となりの 杭（134,292）（242,292）にも かからない（シャンデリアの くさりは 前を とおる）
    A = load('mansion')
    A = move_patch(A, (90, 770, 296, 1102), 35)
    A = move_patch(A, (694, 770, 900, 1102), -35)
    save('mansion', A)


def move_neon(A, box, dx, tex_x, pad=40, th=16, grow=16):
    """暗い 地面の 上の ネオンの 絵（サボテン など）を よこに dx うごかす。
    box の 中の 明るい 所（光と その まわり）だけを 切りとり、もとの 場所は まわりの 地面で うめて、うごかした 先には 光を 足す。
    tex_x＝地面の こまかい もようを うつす 場所（何も ない 地面の x）"""
    x0, y0, x1, y1 = box
    B = A.copy()
    X0, X1, Y0, Y1 = x0 - pad, x1 + pad, y0 - pad, y1 + pad
    R = A[Y0:Y1, X0:X1]
    L = R.max(axis=2)
    gL = np.median(L)
    m = np.zeros(L.shape, bool)
    m[pad:pad + y1 - y0, pad:pad + x1 - x0] = L[pad:pad + y1 - y0, pad:pad + x1 - x0] > gL + th
    lab, n = nd.label(nd.binary_closing(m, iterations=2))      # box の まん中に かかる かたまり（サボテン）だけ
    cy, cx = pad + (y1 - y0) // 2, pad + (x1 - x0) // 2
    keep = set(np.unique(lab[cy - 25:cy + 25, cx - 25:cx + 25])) - {0}
    core = np.isin(lab, list(keep))
    m = nd.binary_dilation(core, iterations=grow)
    m[:pad, :] = m[-pad:, :] = False; m[:, :pad] = m[:, -pad:] = False
    w0, h0 = X1 - X0, Y1 - Y0
    P = A[Y0:Y1, tex_x:tex_x + w0]                            # 何も ない 地面
    plain = nd.uniform_filter(np.median(P, axis=1), size=(15, 1))[:, None, :]
    edge = harmonic(R, m, k=2, it=2500)                       # まわりの 色（となりの サボテンの 光）
    kd = np.exp(-nd.distance_transform_edt(m) / 9)[..., None]
    ground = edge * kd + plain * (1 - kd)                      # 光が ない ときの 地面：まわりの 光は ふちから すぐ 消える
    soft = nd.gaussian_filter(m.astype(np.float32), 3)[..., None]
    tex = np.clip(P - nd.uniform_filter(P, size=(15, 15, 1)), -10, 10)
    B[Y0:Y1, X0:X1] = R * (1 - soft) + (ground + tex) * soft
    mv = nd.gaussian_filter(nd.binary_dilation(core, iterations=10).astype(np.float32), 3)[..., None]
    light = np.clip(R - ground, 0, 255) * mv                  # うごかすのは サボテンと その すぐ まわりの 光
    B[Y0:Y1, X0 + dx:X1 + dx] = B[Y0:Y1, X0 + dx:X1 + dx] + light
    return B


def desert():
    # 小さな まるい サボテン 2つ：オベリスク（100,436）（276,436）の 台の うしろに 花と 上が かくれていた
    # → オベリスクの 内がわ（台の 132 と 244 の あたり・ヘソの 左右の 下）へ
    A = load('desert')
    A = move_neon(A, (150, 1526, 272, 1666), 146, 430)
    A = move_neon(A, (712, 1528, 846, 1670), -101, 430)
    save('desert', A)


def squash_fall(A, xa, xb, ys, ye, yn):
    """xa〜xb の たきの 光を、ys より下だけ たてに ちぢめる（ye まで あった 光が yn で おわる）。
    うしろの 空は 行ごとに 左右の 空の 色を つないで 作る（なめらかな グラデーション）"""
    B = A.copy()
    a = nd.uniform_filter(A[:, xa - 2:xa + 3].mean(axis=1), size=(5, 1))
    b = nd.uniform_filter(A[:, xb - 2:xb + 3].mean(axis=1), size=(5, 1))
    t = ((np.arange(xa, xb) - xa) / (xb - xa))[None, :, None]
    y0 = ys - 30
    sky = a[y0:ye + 10, None, :] * (1 - t) + b[y0:ye + 10, None, :] * t
    light = np.clip(A[y0:ye + 10, xa:xb] - sky, 0, 255)
    k = (ye - ys) / (yn - ys)
    out = np.zeros_like(light)
    for y in range(y0, ye + 10):
        if y < ys:
            out[y - y0] = light[y - y0]
            continue
        sy = ys + (y - ys) * k                                     # ちぢめる前の 行
        if sy >= ye + 9:
            continue
        i = int(sy); f = sy - i
        out[y - y0] = light[i - y0] * (1 - f) + light[min(i + 1, ye + 9) - y0] * f
    # 左右の はしは もとの 絵に なめらかに もどす
    e = np.minimum(np.arange(xb - xa), np.arange(xb - xa)[::-1])
    we = np.clip(e / 8, 0, 1)[None, :, None]
    B[y0:ye + 10, xa:xb] = A[y0:ye + 10, xa:xb] + (out - light) * we          # 光の ぶんだけ 入れかえる（島の 暗い 所は そのまま）
    return B


def heaven():
    # うかぶ島の 光の たき 2つ：たきの 下の きらきらが 羽の杭（60,246）（316,246）の うしろに かかっていた
    # → たきの 下（y 560 より下）を たてに ちぢめて、杭の 少し上（y 690）で おわるように
    A = load('heaven')
    A = squash_fall(A, 92, 214, 560, 790, 690)
    A = squash_fall(A, 776, 912, 560, 790, 690)
    save('heaven', A)


if __name__ == '__main__':
    for n in sys.argv[1:] or ['mansion']:
        globals()[n]()
        print(n, 'ok')
