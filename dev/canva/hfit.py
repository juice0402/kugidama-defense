# 台ごとの ハンドル（強さの ダイヤル）の 絵を ゲームに 入れる（11/8 6.）
# 使い方：python3 hfit.py [見本.png]   … handles.json の 絵を 板（plate＝止まった ふち）と つまみ（knob＝回る）に 分けて WebP に して、
#         index.html の CSS の HANDLE_ART（「HANDLE_ART ここから」〜「ここまで」）を 書きかえる。見本.png は 9つを ならべた 絵（しらべ用の 線つき）
#
# もとの絵（handles/src/〇〇.png）：Canva の 正方形の 絵を 作業用デザインの 480×480 の ページに 置いた 見本（600×600）。
#   こい紺の 無地の 背景に、まるい ふち（その台の 枠の 素材）＋ まん中の まるい つまみ（たての にぎり・上に 光る 目じるし）。
# さがすもの（handles.json で 手で かえられる）：
#   c＝まん中 [x,y]・rk＝つまみの 半径（つまみと ふちの 間の こい みぞの まん中。ここで 切る）・ro＝ふちの 外の 半径（ここまで 不とうめい）・
#   rp＝板の 絵の 半径（ふちの外の つる・宝石・光 まで）・rot＝つまみを まわす 角度（目じるしが 真上に なるように）・
#   grip＝[はばの 半分, とどく 半径]（にぎりが つまみより 外へ はみ出す 絵だけ。はみ出しも つまみと いっしょに 回す）・q＝WebP の 質（ふつう 80）
#   みぞが こくない 絵（氷 など）は "groove":"light"（明るさの かわりめで さがす）か c・rk を 手で
# ゲームの中：ふちの 外の 半径（ro）を ダイヤルの 半径 36px（.dial は 72px）に 合わせる。板は --h-ps、つまみは --h-ks の 大きさ（px）
import sys, os, json, io, base64, re
import numpy as np
from PIL import Image, ImageDraw
from scipy import ndimage as nd
from scipy.ndimage import map_coordinates

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
DIAL = 36          # ふちの外（ro）を 何 px に するか（.dial の 半径）
DPR = 3            # 絵の こまかさ（画面の 1px に 何ピクセル）
ORDER = ['meadow', 'forest', 'mansion', 'desert', 'snow', 'volcano', 'castle', 'space', 'heaven']


def ring_vals(M, cx, cy, R, n=720):
    th = np.linspace(0, 2 * np.pi, n, endpoint=False)
    return map_coordinates(M, [cy + R * np.sin(th), cx + R * np.cos(th)], order=1), th


def find(A, J):
    h, w, _ = A.shape
    border = np.concatenate([A[0], A[-1], A[:, 0], A[:, -1]])
    bg = np.median(border, axis=0)
    d = np.abs(A - bg).max(axis=2)
    L = A.mean(axis=2)
    # まん中の だいたい：背景と ちがう 太い かたまりの 重心
    m = nd.binary_opening(nd.binary_fill_holes(d > 60), iterations=8)
    lab, n = nd.label(m)
    k = np.argmax(nd.sum(m, lab, range(1, n + 1))) + 1
    ys, xs = np.nonzero(lab == k)
    c0 = (xs.mean(), ys.mean()); r0 = np.sqrt((lab == k).sum() / np.pi)
    # みぞ：つまみの まわりの こい 輪（にぎりの ある 上下 ±25° は のぞく）
    th = np.linspace(0, 2 * np.pi, 360, endpoint=False)
    keep = np.abs(np.abs(np.degrees(th) - 180) - 90) > 25
    M = L if J.get('groove', 'dark') == 'dark' else -np.abs(nd.sobel(L, 0)) - np.abs(nd.sobel(L, 1))
    if 'c' in J and 'rk' in J:
        cx, cy = J['c']; rk = J['rk']
    else:
        best = None
        for cx in np.arange(c0[0] - 16, c0[0] + 17, 2):
            for cy in np.arange(c0[1] - 16, c0[1] + 17, 2):
                for R in np.arange(r0 * .55, r0 * .85, 2):
                    v = map_coordinates(M, [cy + R * np.sin(th), cx + R * np.cos(th)], order=1)
                    s = v[keep].mean()
                    if best is None or s < best[0]: best = (s, cx, cy, R)
        _, cx, cy, rk = best
        if 'c' in J: cx, cy = J['c']
        if 'rk' in J: rk = J['rk']
    # ふちの外：輪の上の 1わりの 所が 背景に なる 半径
    ro = J.get('ro')
    if ro is None:
        for R in np.arange(rk + 10, min(h, w) / 2, 1.0):
            v, _ = ring_vals(d, cx, cy, R)
            if np.percentile(v, 10) < 20: ro = R - 2; break
    rp = J.get('rp')
    if rp is None:
        rp = ro
        for R in np.arange(ro, min(h, w) / 2 - 1, 1.0):
            v, _ = ring_vals(d, cx, cy, R)
            if np.percentile(v, 99) < 14: break
            rp = R
        rp = min(rp + 4, min(cx, cy, w - cx, h - cy) - 1)
    return dict(bg=bg, d=d, cx=float(cx), cy=float(cy), rk=float(rk), ro=float(ro), rp=float(rp))


def cut(key, J):
    src = os.path.join(HERE, J['src'])
    A = np.asarray(Image.open(src).convert('RGB')).astype(np.float32)
    f = find(A, J)
    bg, d, cx, cy, rk, ro, rp = f['bg'], f['d'], f['cx'], f['cy'], f['rk'], f['ro'], f['rp']
    h, w, _ = A.shape
    yy, xx = np.mgrid[0:h, 0:w]
    r = np.hypot(xx + .5 - cx, yy + .5 - cy)
    # 板：ふちの中は 不とうめい、外の 光（つる・宝石）は 背景との ちがいで すけすけに（neoncut.py と 同じ）
    a_in = np.clip(ro - r + .5, 0, 1)
    dn = d / 255
    ag = np.clip((dn - .035) * 1.5, 0, 1)
    solid = nd.binary_opening(dn > .3, iterations=2)
    solid = nd.gaussian_filter(solid.astype(np.float32), 1)
    ag = np.maximum(ag, np.clip((dn - .035) / .3, 0, 1) * solid)
    a = np.maximum(a_in, ag) * (r < rp)
    O = A / 255; B = bg / 255
    F = np.where(a[..., None] > 1e-3, (O - B * (1 - a[..., None])) / np.maximum(a[..., None], 1e-3), 0)
    F = np.clip(F, 0, 1) * (1 - a_in[..., None]) + O * a_in[..., None]
    # つまみの 下は みぞの 色で ぬる（回したとき もとの にぎりが はみ出さない・軽い）
    gv = [map_coordinates(A[..., i], [cy + (rk + 1) * np.sin(t), cx + (rk + 1) * np.cos(t)], order=1) for i in range(3)
          for t in [np.linspace(0, 2 * np.pi, 360, endpoint=False)]]
    gcol = np.median(np.stack(gv, 1), axis=0) / 255
    under = r < rk - 1.5
    F[under] = gcol
    # にぎりが つまみより 外へ はみ出す 絵（grip＝[はばの 半分, とどく 半径]）：はみ出した 所は つまみの 絵に 入れて、板の その所は みぞの 色（半径ごとの まん中の 色）で うめる
    hw, reach = J.get('grip', [0, 0])
    strip = (np.abs(xx + .5 - cx) < hw + 2) & (r < reach + 3) & (r >= rk - 2)
    if strip.any():
        th = np.linspace(0, 2 * np.pi, 720, endpoint=False); keep = np.abs(np.abs(np.degrees(th) - 180) - 90) > 25
        for R in np.unique(np.floor(r[strip]).astype(int)):
            col = np.median(np.stack([map_coordinates(O[..., i], [cy + (R + .5) * np.sin(th[keep]), cx + (R + .5) * np.cos(th[keep])], order=1) for i in range(3)], 1), axis=0)
            m = strip & (np.floor(r).astype(int) == R)
            F[m] = col; a[m] = np.maximum(a[m], 1)
    plate = np.dstack([F, a])
    x0, y0 = int(round(cx - rp)), int(round(cy - rp)); s = int(round(rp * 2))
    plate = plate[y0:y0 + s, x0:x0 + s]
    # つまみ：みぞの まん中で まるく 切る。rot で 目じるしを 真上に
    ka = np.clip(rk - r + .5, 0, 1)
    if hw: ka = np.maximum(ka, np.clip(hw - np.abs(xx + .5 - cx) + .5, 0, 1) * np.clip(reach - r + .5, 0, 1))
    knob = np.dstack([O, ka])
    kr = max(rk, reach)
    kx0, ky0 = int(np.floor(cx - kr - 1)), int(np.floor(cy - kr - 1)); ks = int(np.ceil(kr * 2 + 2))
    knob = knob[ky0:ky0 + ks, kx0:kx0 + ks]
    kim = Image.fromarray((np.clip(knob, 0, 1) * 255 + .5).astype(np.uint8), 'RGBA')
    if J.get('rot'): kim = kim.rotate(-J['rot'], resample=Image.BICUBIC, center=(cx - kx0, cy - ky0))
    pim = Image.fromarray((np.clip(plate, 0, 1) * 255 + .5).astype(np.uint8), 'RGBA')
    ps = 2 * rp / ro * DIAL; kss = ks / ro * DIAL
    P = pim.resize((round(ps * DPR),) * 2, Image.LANCZOS)
    f['kc'] = (cx - kx0, cy - ky0)
    K = kim.resize((round(kss * DPR),) * 2, Image.LANCZOS)
    print(key, 'c=(%.0f,%.0f) rk=%.0f ro=%.0f rp=%.0f' % (cx, cy, rk, ro, rp), 'plate %.1fpx knob %.1fpx' % (ps, kss))
    return dict(P=P, K=K, ps=ps, ks=kss, f=f, A=A)


def webp(im, q):
    b = io.BytesIO(); im.save(b, 'WEBP', quality=q, method=6); return b.getvalue()


def main():
    J = json.load(open(os.path.join(HERE, 'handles.json')))
    rows, res = [], {}
    tot = 0
    for key in ORDER:
        if key not in J: continue
        R = cut(key, J[key]); res[key] = R
        q = J[key].get('q', 80)
        pb, kb = webp(R['P'], q), webp(R['K'], q)
        tot += len(pb) + len(kb)
        print('   webp plate %dKB knob %dKB' % (len(pb) / 1024 + .5, len(kb) / 1024 + .5))
        u = lambda b: 'url(data:image/webp;base64,' + base64.b64encode(b).decode() + ')'
        rows.append('#app[data-board="%s"]{--h-plate:%s;--h-knob:%s;--h-ps:%.1fpx;--h-ks:%.1fpx}' % (key, u(pb), u(kb), R['ps'], R['ks']))
    print('ぜんぶで %dKB' % (tot / 1024 + .5))
    p = os.path.join(ROOT, 'index.html')
    s = open(p, encoding='utf-8').read()
    a = s.index('/* HANDLE_ART ここから'); a = s.index('*/', a) + 2
    b = s.index('/* HANDLE_ART ここまで')
    s = s[:a] + '\n' + '\n'.join(rows) + '\n' + s[b:]
    open(p, 'w', encoding='utf-8').write(s)
    print('index.html ok')
    if len(sys.argv) > 1:   # 見本：もとの絵に 見つけた 円（みどり＝つまみ・水色＝ふちの外・ピンク＝板）／板と つまみを かさねた 絵（0°・−135°・135°）
        T = 220; sheet = Image.new('RGB', (T * 4 + 30, T * len(res) + 10 * (len(res) - 1)), (40, 40, 48))
        for i, (key, R) in enumerate(res.items()):
            f = R['f']; im = Image.fromarray(R['A'].astype(np.uint8)).resize((T, T)); k = T / R['A'].shape[1]
            dr = ImageDraw.Draw(im)
            for rr, col in [(f['rk'], (0, 255, 0)), (f['ro'], (0, 220, 255)), (f['rp'], (255, 80, 200))]:
                dr.ellipse([(f['cx'] - rr) * k, (f['cy'] - rr) * k, (f['cx'] + rr) * k, (f['cy'] + rr) * k], outline=col)
            sheet.paste(im, (0, i * (T + 10)))
            for j, ang in enumerate([0, -135, 135]):
                bgc = Image.new('RGBA', (T, T), (70, 30, 20, 255))
                P = R['P'].resize((round(T * R['ps'] / 100),) * 2, Image.LANCZOS)
                K = R['K'].rotate(-ang, resample=Image.BICUBIC).resize((round(T * R['ks'] / 100),) * 2, Image.LANCZOS)
                bgc.alpha_composite(P, ((T - P.width) // 2, (T - P.height) // 2))
                bgc.alpha_composite(K, ((T - K.width) // 2, (T - K.height) // 2))
                sheet.paste(bgc.convert('RGB'), ((j + 1) * (T + 10), i * (T + 10)))
        sheet.save(sys.argv[1]); print(sys.argv[1])


if __name__ == '__main__':
    main()
