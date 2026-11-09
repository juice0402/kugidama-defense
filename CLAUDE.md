# パチおば（記号 pachi・旧名 くぎだまディフェンス）

- ゲームは index.html 1ファイル（HTML・CSS・JS を全部入れる）。外部はGoogle Fontsだけ
- 企画と決まったことは claude.ai プロジェクト「ネット副業」の claude/pachi-game-idea.md
- 見た目：1面はネオンな夜の草原（木のフレームに草とつる・光る木の実、月・星・光るふちの丘・木の杭）。台は画面いっぱい、表示とハンドルは台に重ねる。縦画面・スマホで片手
- 敵はイタズラ好きの白いおばけ＋動物の特ちょう（ENEMIES。台ごとの顔ぶれは STAGES の foes）。森は11/5に作りかえ済み、洋館（3台目）・砂漠（4台目）・雪山（5台目）は11/5、火山（6台目）・魔王城（7台目）・宇宙（8台目）・天国（9台目・さいご）とエンディングは11/6に作成
- 全台づくりの設計図は dev/plan.md、しくみ（フック）は index.html の上のコメント「コードのしくみ」。自動プレイ・スクショは dev/sim（mk.py → runsim.py / shot.py）
- 軽さ：毎フレーム描くものは、絵の使いまわし（sprite）・まとめ描き（fxPath・taperPath）・光の重ね描き（lazyLay）を使い、shadowBlur は使わず clip も なるべく使わない（11/6・11/7 の軽量化。くわしくは「コードのしくみ」の「軽くする道具」）。重さは dev/sim の mkprof.py＋prof9.js で 描く関数ごとの命令の数を 前とくらべる。11/9：GPU の しごと（1コマに 描く ピクセル）は prof10.js、ほんとうの ループの コマの 時間は fps9.py（ここの Chrome は ソフトで 描くので 数は 前後の くらべるだけ）。重い スマホは 自動で 細かさを 下げる（autoQuality）
- BGM（11/8）：コードで鳴らす（音のファイル0）。台ごとに1曲＋ホール・エンディング・ジングル、FEVER とボスで速く派手に。index.html の「BGM ここから」の区切り。試しは dev/sim の bgmcheck.py（音の大きさ）
- Canva の絵（11/8〜）：絵柄は A ネオン（しょーくんが4案から選んだ）。おばけは Canva で作って SPRITE_SRC（WebP）に入れる。作り方・できた台・注意は dev/canva.md、道具は dev/canva/（neoncut.py・pack.py）。ゆっくり作る（一度に大量に作らない）
- 動き（11/9〜）：画面の切りかえ・シート・タブ・ボタン・玉のセット・タワーを置く などの アニメーション。transform と opacity だけ・動きを へらす 設定では 出さない。index.html の「動き ここから」と JS の「動き（11/9）」、くわしくは dev/anim.md。ためしは dev/sim/animrec.py（動画）
- iPhone・iPad（11/9〜）：さいごは iOS アプリに したい。いろいろな 画面の ためしは dev/sim の devsweep.py（11機種）・wk.py（WebKit＝Safari と 同じ エンジンで 開く・11/10）・animstress.py（れんだ・とちゅうで とじる）・canvmem.py（キャンバスの メモリ。iOS は 合計 およそ 224MB が 上限）。直したこと・アプリに する 道すじは dev/ios.md。iPad など 大きい 画面は #app を uiZ 倍に（applyZ。CSS の vw・vh は --vw・--vh を 使う）。枠と ボタン・字の すきまは SPACE=1 devsweep.py と panelshots.py。アプリは juice0402/ios-kobo の apps/pachioba（GitHub Actions の Mac で 組み立て・Mac は いらない）。アプリの 中だけ APP_PLATFORM='ios'・APP_HAPTIC、ストアの スクショは 自動の ためしの ときだけ #shot=
- ゲーム工房（11/9〜）：あそびトークの /kobo/pachioba で公開。工房に出したい版ができたら RELEASES.md のいちばん上に版を足す（書き方はファイルの上）。main にマージされると Actions（release.yml・tools/release/tag_releases.py）がタグを作り、司令塔が工房に取りこむ
- 決まっていない中身を勝手に足さない。迷ったらしょーくんに聞く
