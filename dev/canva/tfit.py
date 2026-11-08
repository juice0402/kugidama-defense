# タワー（砲台）と ギミックの 絵を ゲームに 入れる（11/8 4.）
# 使い方：python3 tfit.py            … towers.json の 絵を ぜんぶ 合わせて WebP にし、index.html の TWR_SRC（「TWR_SRC ここから」〜「ここまで」）を 書きかえる
#         python3 tfit.py 見る.png   … ついでに 見本（ならべた 絵。杭の まると 砲身の先の しるし つき）を 出す
#
# 絵は neoncut.py で すけすけに した 200×200 の *_full.png（towers/ と gimmicks/）。
# towers.json の 1つずつ：
#   "src"  ファイルの名前（towers/〇〇_full.png など。フォルダから）
#   "rot"  まわす 角度（度・左まわり。砲身が 右を むくように）
#   "piv"  まわしたあとの 絵の中の 中心（砲台の 回る 中心＝杭の まん中）[x,y]
#   "s"    杭の 半径 R が 何ピクセルか（大きさ）。[横, たて] なら たてと 横で ちがう 大きさ
#   "box"  （あれば）切りぬく はんい [x0,y0,x1,y1]（R の 単位・中心から）。なければ 絵の すけていない所 ぜんぶ
#   "half" "front" なら 中心より 下の 半分だけ（惑星リングの 手前の 半分）
#   "circle"（あれば）piv を 中心に この 半径（もとの絵の ピクセル）で まるく 切りぬく（まわす 部品）
# 出すもの：TWR_SRC の 行 {w,h,ax,ay,src}（どれも R の 単位。ax,ay＝絵の 左上から 中心まで）。絵は 1R＝Q ピクセル
import sys, os, json, io, base64, re
import numpy as np
from PIL import Image, ImageDraw

HERE = os.path.dirname(os.path.abspath(__file__))
ROOT = os.path.join(HERE, '..', '..')
Q = 36          # できる 絵の こまかさ（R が 何ピクセル）。画面では R＝11単位×2.2 くらい＝24px、お店の アイコンで 35px


def fit(k, o):
    im = Image.open(os.path.join(HERE, o['src'] + '_full.png')).convert('RGBA')
    if o.get('flip'):
        im = im.transpose(Image.FLIP_TOP_BOTTOM)
    W0, H0 = im.size
    rot = o.get('rot', 0)
    px, py = o['piv']
    if rot:
        # 中心の まわりに まわす（まわした 絵の中の 中心の 位置を 合わせる）
        big = Image.new('RGBA', (W0 * 3, H0 * 3), (0, 0, 0, 0)); big.alpha_composite(im, (W0, H0))
        big = big.rotate(rot, resample=Image.BICUBIC, center=(W0 + px, H0 + py))
        im = big; px += W0; py += H0
    sx, sy = (o['s'], o['s']) if not isinstance(o['s'], list) else o['s']   # [横, たて] で たてだけ ちぢめる（ワープとびら）
    k2 = Q / sx; k3 = Q / sy
    im = im.resize((max(1, round(im.width * k2)), max(1, round(im.height * k3))), Image.LANCZOS)
    px *= k2; py *= k3
    a = np.asarray(im)[..., 3]
    if 'circle' in o:
        # まるく 切りぬく（まわる 部品：たつまきタワーの ファン など。中心＝piv・半径 circle ピクセル（もとの絵で））
        r = o['circle'] * k2
        m = Image.new('L', (im.width * 4, im.height * 4), 0)
        ImageDraw.Draw(m).ellipse(((px - r) * 4, (py - r) * 4, (px + r) * 4, (py + r) * 4), fill=255)
        m = m.resize(im.size, Image.LANCZOS)
        al = np.minimum(np.asarray(im)[..., 3], np.asarray(m))
        im.putalpha(Image.fromarray(al.astype(np.uint8)))
        b = (int(px - r - 1), int(py - r - 1), int(px + r + 2), int(py + r + 2))
    elif 'box' in o:
        x0, y0, x1, y1 = o['box']
        b = (int(px + x0 * Q), int(py + y0 * Q), int(px + x1 * Q + .999), int(py + y1 * Q + .999))
    else:
        ys, xs = np.where(a > 4)
        b = (xs.min() - 2, ys.min() - 2, xs.max() + 3, ys.max() + 3)
    if o.get('half') == 'front':
        b = (b[0], int(py), b[2], b[3])   # 手前の 半分（中心より下）だけ：砲台の 上に かさねて、わっかが 砲台の まわりを まわって 見える
    b = (max(0, b[0]), max(0, b[1]), min(im.width, b[2]), min(im.height, b[3]))
    c = im.crop(b)
    return c, (px - b[0]) / Q, (py - b[1]) / Q


def main():
    spec = json.load(open(os.path.join(HERE, 'towers.json')))
    lines = []; total = 0; outs = {}
    for group in ('heads', 'gims'):
        for k, o in spec.get(group, {}).items():
            c, ax, ay = fit(k, o)
            buf = io.BytesIO(); c.save(buf, 'WEBP', quality=o.get('q', 88), method=6, alpha_quality=100); data = buf.getvalue(); total += len(data)
            outs[k] = (c, ax, ay, group)
            lines.append(f"  {k}:{{w:{c.width / Q:.3f},h:{c.height / Q:.3f},ax:{ax:.3f},ay:{ay:.3f},src:'data:image/webp;base64,{base64.b64encode(data).decode()}'}},   // {c.width}×{c.height} {len(data)}B")
    path = os.path.join(ROOT, 'index.html')
    src = open(path, encoding='utf-8').read()
    a = src.index('// TWR_SRC ここから\n') + len('// TWR_SRC ここから\n'); b = src.index('// TWR_SRC ここまで')
    src = src[:a] + '\n'.join(lines) + '\n' + src[b:]
    open(path, 'w', encoding='utf-8').write(src)
    print('pictures', len(lines), 'bytes', total)
    if len(sys.argv) > 1:
        sheet(outs, spec, sys.argv[1])


def sheet(outs, spec, path):
    """見本：1つずつ こい紺の上に、杭（半径 R）の 円と 砲身の先（muz）の しるし"""
    muz = spec.get('muz', {})
    CW, CH = int(5.6 * Q), int(4.2 * Q); n = len(outs); cols = 6; rows = (n + cols - 1) // cols
    sh = Image.new('RGBA', (cols * CW, rows * CH), (14, 16, 44, 255))
    for i, (k, (c, ax, ay, group)) in enumerate(outs.items()):
        cx = (i % cols) * CW + int(2.3 * Q); cy = (i // cols) * CH + CH // 2; S = CH // 2
        d = ImageDraw.Draw(sh)
        d.ellipse((cx - Q, cy - Q, cx + Q, cy + Q), outline=(120, 90, 60, 255), width=2)
        sh.alpha_composite(c, (int(cx - ax * Q), int(cy - ay * Q)))
        if k in muz:
            m = muz[k] * Q; d.line((cx + m, cy - 8, cx + m, cy + 8), fill=(255, 60, 60, 255), width=2)
        d.text((cx - int(2.3 * Q) + 6, cy - S + 4), k, fill=(255, 255, 255, 255))
    sh.save(path)


if __name__ == '__main__':
    main()
