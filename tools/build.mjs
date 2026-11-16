#!/usr/bin/env node
// index.html を つくる（11/16 司令塔「作りの 分割」code-rules.md の B ①）。Node の 標準だけ
//
//   src/index.html（手で 直す もと）＋ assets/（絵の ファイル）→ index.html（遊ぶ 人が 開く・1ファイル・手で 直さない）
//   もとの 中の 絵は「@@assets/〇〇/〇〇.webp@@」。つくる ときに data:image/webp;base64,… に して 埋めこむ
//
//   node tools/build.mjs           … 埋めこみ なおして index.html を 書く（もとに base64 が あれば、先に assets/ に 出す＝extract）
//   node tools/build.mjs --check   … 書かずに くらべる。index.html が もとから 作った ものと ちがえば 1 で おわる（CI 用）
//   node tools/build.mjs --extract … もとの 中の base64 を assets/ に 出すだけ
//
// dev/canva の 絵の 道具（art.py・uifit.py・titlefit.py・hfit.py・tfit.py・ballfit.py）は src/index.html に base64 で 書いて、
// そのあと この ビルドを よぶ → extract が 同じ 名前の ファイルに 上書きして、もとは @@…@@ に もどる
import fs from 'node:fs';
import path from 'node:path';
import { fileURLToPath } from 'node:url';

const ROOT = path.resolve(path.dirname(fileURLToPath(import.meta.url)), '..');
const SRC = path.join(ROOT, 'src', 'index.html');
const OUT = path.join(ROOT, 'index.html');
const MIME = { webp: 'image/webp', png: 'image/png', jpg: 'image/jpeg', gif: 'image/gif' };
const EXT = Object.fromEntries(Object.entries(MIME).map(([e, m]) => [m, e]));
const TOKEN = /@@(assets\/[A-Za-z0-9_\/.-]+)@@/g;
const DATA = /data:(image\/(?:webp|png|jpeg|gif));base64,([A-Za-z0-9+\/=]+)/g;
// もとの 2行目 → index.html では この 1行に（どちらも この 形の まま）
const SRC_NOTE = '<!-- src/index.html：ここを 直して node tools/build.mjs で index.html を 作る（絵は assets/ の ファイルを @@assets/…@@ で 指す） -->';
const OUT_NOTE = '<!-- 自動で 作る ファイル：src/index.html と assets/ から node tools/build.mjs で 作る。手で 直さない -->';

// 絵の かたまり（そこを 書く 道具）→ assets/ の 下の フォルダ。その 行より 前の いちばん 近い 目じるしで きめる
const GROUPS = [
  ['/* HANDLE_ART ここから', 'handle'],   // hfit.py：台ごとの ハンドルの 板と つまみ
  ['/* TITLE_ART ここから', 'title'],     // titlefit.py
  ['/* UI_ART ここから', 'ui'],           // uifit.py：アイコン・ボタンや 板の わく
  ['const SPRITE_SRC={', 'ghost'],        // pack.py → sprite_src.js を はりつけ：おばけ
  ['// TWR_SRC ここから', 'tower'],       // tfit.py：タワー
  ['const BALL_ART=', 'ball'],            // ballfit.py：玉の アトラス
  ['// ART_SRC ここから', 'art'],         // art.py：台の 景色と 枠
];
const ENDS = ['/* HANDLE_ART ここまで', '/* TITLE_ART ここまで', '/* UI_ART ここまで', '// TWR_SRC ここまで', '// BALL_ART ここまで', '// ART_SRC ここまで'];

const slug = s => s.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/^-+|-+$/g, '') || 'img';

// 絵の 名前：CSS の 変数（--i-coin）・JS の キー（kakashi:{…}）・CSS の さいしょの セレクタ（.btn.primary）
function nameAt(line, at, group) {
  const before = line.slice(0, at);
  const v = before.match(/--([A-Za-z0-9-]+)\s*:\s*url\(\s*['"]?$/);
  const board = line.match(/^#app\[data-board="([a-z0-9_-]+)"\]/);
  if (v) return (board ? board[1] + '-' : '') + v[1];
  const k = line.match(/^\s*([A-Za-z_$][\w$]*)\s*:/);
  if (k) return k[1] === 'src' ? (group === 'ball' ? 'atlas' : group) : k[1];
  const sel = line.match(/^\s*([^{,]+?)\s*[,{]/);
  if (sel) return slug(sel[1]);
  return 'img';
}

// もとの 中の base64 を assets/ に 出して @@…@@ に する。かえり：[あたらしい もと, 出した 数]
function extract(src) {
  const lines = src.split('\n');
  let group = 'misc', n = 0;
  const used = new Map();   // group/name → 回数（同じ 名前が 2つ あれば -2・-3…）
  for (let i = 0; i < lines.length; i++) {
    const l = lines[i];
    const g = GROUPS.find(([m]) => l.startsWith(m));
    if (g) group = g[1];
    if (!l.includes(';base64,')) { if (ENDS.some(m => l.startsWith(m))) group = 'misc'; continue; }
    lines[i] = l.replace(DATA, (all, mime, b64, at) => {
      let name = nameAt(l, at, group);
      const key = group + '/' + name, c = (used.get(key) || 0) + 1;
      used.set(key, c); if (c > 1) name += '-' + c;
      const rel = `assets/${group}/${name}.${EXT[mime]}`;
      const file = path.join(ROOT, rel), buf = Buffer.from(b64, 'base64');
      if (buf.toString('base64') !== b64) throw new Error(`base64 が ふつうの 形で ない（もとに もどせない）：${rel}`);
      fs.mkdirSync(path.dirname(file), { recursive: true });
      if (!fs.existsSync(file) || !fs.readFileSync(file).equals(buf)) fs.writeFileSync(file, buf);
      n++;
      return `@@${rel}@@`;
    });
    if (ENDS.some(m => l.startsWith(m))) group = 'misc';
  }
  return [lines.join('\n'), n];
}

function build(src) {
  if (!src.includes(SRC_NOTE)) throw new Error('src/index.html の 2行目の 目じるしが ない');
  const missing = [];
  const out = src.replace(SRC_NOTE, OUT_NOTE).replace(TOKEN, (all, rel) => {
    const file = path.join(ROOT, rel);
    if (!fs.existsSync(file)) { missing.push(rel); return all; }
    const mime = MIME[path.extname(rel).slice(1)];
    if (!mime) throw new Error('この 絵の 形は 埋めこめない：' + rel);
    return `data:${mime};base64,` + fs.readFileSync(file).toString('base64');
  });
  if (missing.length) throw new Error('assets に ない 絵：\n  ' + missing.join('\n  '));
  return out;
}

const arg = process.argv[2] || '';
let src = fs.readFileSync(SRC, 'utf8');
if (arg !== '--check') {
  const [s2, n] = extract(src);
  if (n) { fs.writeFileSync(SRC, s2); src = s2; console.log(`assets/ に 出した 絵：${n}`); }
  if (arg === '--extract') process.exit(0);
}
const out = build(src);
if (arg === '--check') {
  const cur = fs.existsSync(OUT) ? fs.readFileSync(OUT, 'utf8') : '';
  if (cur !== out) { console.error('index.html が src/index.html と assets/ から 作った ものと ちがう → node tools/build.mjs'); process.exit(1); }
  console.log('index.html ok（もとと 同じ）');
} else {
  fs.writeFileSync(OUT, out);
  const used = new Set([...src.matchAll(TOKEN)].map(m => m[1]));
  const all = [];
  const walk = d => { for (const e of fs.readdirSync(path.join(ROOT, d), { withFileTypes: true })) e.isDirectory() ? walk(d + '/' + e.name) : all.push(d + '/' + e.name); };
  if (fs.existsSync(path.join(ROOT, 'assets'))) walk('assets');
  const unused = all.filter(f => !used.has(f));
  console.log(`index.html ${(Buffer.byteLength(out) / 1048576).toFixed(2)}MB・絵 ${used.size}`);
  if (unused.length) console.log('使っていない assets（いらなければ けす）：\n  ' + unused.join('\n  '));
}
