# Canva の絵（11/8〜）

しょーくんの依頼（11/8）：「Canva の作成に移行しよう。一度に大量に作ると規制がかかるかもしれないから、時間かかってもいいし、ゆっくりやってね」。順番は決めていないので全部。絵柄は 4案（ネオン・ぷにぷに3D・パステル手描き・ドット絵）から **A ネオン** に決定。

## 作るもの（ぜんぶ）
- おばけ 45体（＋状態で かわる かえ絵）
- 台ごとのハンドル 9つ・台の奥の景色・砲台・タイトルの絵・お店／図鑑のアイコン・ボタンやフレーム

## おばけの作り方
1. Canva の generate-image（正方形）。**参考の絵に うさぎおばけ（MAHaRoS65JU）を わたす**と 絵柄がそろう。文は：
   「パチおばのおばけ（参考の うさぎおばけと 同じ絵柄・同じタッチ。うさぎの耳やリボンは つけない）：イタズラ好きの白いおばけ＋◯◯の特ちょう（見た目の部品）。おばけは1体だけ・正面向きの全身を大きく、まわりに少し余白。ゲームのキャラクターの絵。絵柄：ネオンサイン風（こい紺の無地の背景に、◯色の光るネオンの線でふちどり、体は白くほんのり光る）。かわいい。文字なし」
   - ネオンの色は ENEMIES の color に近い色。ボス・中ボスは「少し大きめ」など。
   - **いたずらの説明（分かれる・とぶ…）は 文に入れない**（絵に描かれてしまう。わたげの1回目は 小さいわたげが 2つ ついた）。見た目だけ書く。
2. 状態で 見た目が かわる おばけは、できた絵を 参考にして「◯◯だけ なくした絵に。ほかは そのまま」で かえ絵を作る（位置が そろう）。
3. remove-background で 背景けし。**それだけだと ネオンの光が けずれる**（こい色の部品＝くまの ツボ なども けずれる）ので、`dev/canva/neoncut.py もとの絵 背景けし 出す_full.png` で、体は 背景けしの形・まわりの光は もとの絵の「背景の こん色との ちがい」から すけすけにする。
4. `dev/canva/pack.py` が `_full.png` を切りぬいて WebP（q90）にして SPRITE_SRC の行を出す。かえ絵の組（sprites.json の groups）は 同じ わくで 切るので、入れかわっても体が ずれない。大きさは sprites.json の size（[w, by]：w＝半径に対する絵のはば、by＝絵の下はし）。かえ絵の 体が ずれているときは place（[dx,dy,倍率]、200×200 の 絵の 点で）で そろえる。
5. ここで 取れる絵は 200×200（Canva の見本の大きさ。もとの 1264×1264 は この作業場から ダウンロードできない＝media.canva.com は 通らない）。おばけは この大きさで足りる。
   **大きい絵（台の奥の景色など）は「ページの見本を 切って 読む」**（11/8 ためし・草原で 成功）：作業用デザイン「パチおば 背景 作業用」（DAHaSyBw7z8）を read-design で ひらき（open_transaction）、480×428 の ページを 8まい 足して、それぞれに 絵を 944×1680 の 大きさで ずらして 置く（left 0／-464、top 0／-417／-835／-1252）。edit-design の 返りの 見本は 600×535（1.25倍）なので、8まいを つなぐと 1180×2100 の 絵になる。おわったら edit-design を cancel（デザインは 保存しない）。ゲームには 幅720 の WebP（約45KB）で。
6. たしかめ：`dev/sim/mk.py` のあと `python3 shot.py out.png "$(sed s/__STAGE__/0/g sprcheck.js)" 60`（0＝草原）。台に その台の おばけと かえ絵が ならぶ。sprcheck.js は おばけの tick を 止めて 状態を そのまま 見せる。エラーは `sprerr.js`（その台の おばけ × 状態。1分くらい。全部の drawcheck.js は 30分でも おわらない）。かえ絵の 状態を 足したら 両方の 表に 足す。

## ゲームの中のしくみ
- `SPRITE_SRC` に絵、`sprOf(e)` が いまの絵（ENEMIES の `sprKey(e)` で かえ絵の名前）。絵があると drawGhost は back・skin・front・top・顔を描かない。絵の上に かさねる 効果は `over(e,r,t,P)`（洋館の まとめは 「Canvaの絵の かえ絵と 上に かさねる 効果（洋館）」の区切り）。
  → 状態で出る効果（たて・まほうじん・ふきだし など）を フックの中で描いている おばけは、絵に かえるときに その効果を 絵の上に 描くよう 分ける（森より先の台で 必要）。
- ボスのHPバーは `sprTop(e)` で 絵の上に出す。

## できたもの
- 草原（11/8）：wata・usagi・kakashi（帽子なし kakashi_nohat）・tanuki（葉っぱ tanuki_leaf＝化ける前の本物と にせもの）・uma（金の王冠）
- 森（11/8）：kinoko・kitsune・hari（まるまり hari_curl）・kuma（なめる kuma_lick・ツボなし kuma_nopot）・taiboku
- 洋館（11/8）：neko（しっぽ1本 neko_1・天使の輪 neko_rev）・koumori（天井で ねむる koumori_hang）・yoroi（よろいが ずれる yoroi_off）・fukurou（羽をためる fukurou_up）・ookami（遠ぼえ ookami_howl）。あせ・いかりマークと 遠ぼえの音は over で 絵の上に
- 砂漠（11/8）：mia（もぐっている間は sprKey が null＝コードの絵、もぐりかけの すなの山は over）・tokage（しっぽ切れ tokage_cut・リボン tokage_knot）・rakuda（こぶが しぼむ rakuda_flat）・sasori（ねらう sasori_aim・だらん sasori_stop）・sphinx（すなのたては over）
  - らくだは 1回目 こぶが 耳に見えたので「頭のうしろに 大きな ふたこぶ・らくだらしい顔」で 作りなおし。しぼんだ こぶも 1回目は 羊の角に見えたので「風船のように 平たく しぼむ・まるまらない」
- 雪山（11/8）：okojo（雪に まぎれる白い おおいと 見つかった輪は over。P.spr＝いまの絵と 場所）・penguin・tonakai（氷のよろい → ひび tonakai_crack → われた tonakai_bare）・seiuchi（ねそべる seiuchi_lie。絵のときは pose で つぶさない）・mammoth（鼻を ふり上げる mammoth_up、鼻の先の 雪玉は over で 絵の中の 鼻の先に）
- 火山（11/8）：buta（タオル buta_soak。ゆげ・ひやっの しずくは over）・hinotori（黒こげ hinotori_burnt）・sai（角のよろい → ひび sai_crack → われた sai_bare）・inoshishi（はないきは over）・dragon（火を はく口 dragon_fire。むねの光と 口の光は over）
- 魔王城（11/8）：karasu（ぬすんだ宝石は over で くちばしに）・hebi（ぬけがらは コードの絵、ばんそうこう・ぴかぴかは over）・kaeru（石 kaeru_stone）・yagi（となえる yagi_chant、足もとの まほうじんは under）・kujaku（羽を広げる kujaku_fan。広げた絵は 体が 下に ずれていたので sprites.json の place で [0,-40,1.05] ずらして 体を そろえた）
- 宇宙（11/8）：kurage（からまって リボン kurage_knot）・iruka（足もとの 流れ星は under）・kame（星のバリアは over で コードの top を そのまま）・tako（ほっぺ ぷくー tako_puff）・kujira（口を あける kujira_open、しおふきは over で 絵の 頭の上から）。しょくしゅや しっぽが 下に のびる おばけは by を 大きく（クラゲ 1.45・タコ 1.4）して 体の まん中を 合わせる
- 天国（11/8）：hitsuji（のっている 雲は under）・hato（羽が ちる hato_walk）・unicorn（角が くもる unicorn_fog、光る角は over）・panda（おいのり panda_pray）・ousama（口を あける ousama_open。まおうの おうぎは under、すなのたて・ふきだしは over）。光のたて（drawLShield）は 天国の 5体 みんな over で
- → おばけ 45体 ぜんぶ 完了（かえ絵 こみで 80まい・WebP で 約0.9MB）
- つぎ：ハンドル 9つ・台の奥の景色・砲台・タイトル・お店／図鑑のアイコン・ボタンやフレーム（大きい絵は ここから ダウンロードできないので やり方を しょーくんと 決める）
- Canva のフォルダ「パチおば おばけ（ネオン）」に 草原の もとの絵（ほかは Canva の アップロードに ある）。Canva の番号は dev/canva/manifest.json
