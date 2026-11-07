# 本の保存境界

書籍の入力とすべての派生物（講義、主張・証明、台帳、出典対応、進捗、私的な執筆指示・案内、画像、OCR、PDF）はローカル専用で、GitHub の Private を含め外部へ送らない。汎用的な agent 手順・スキル・コード・テンプレート・架空のテストだけを policy checkout に置ける。公開されている原著も、この区分の例外ではない。実教材は PR、コメント、fixture、CI ログへ含めない。共有は汎用部分について将来の明示依頼があるときだけ行い、[公開境界](../../labo-pr/references/publication-gate.md)を適用する。

既定の教材 root は **workspace 内の `local/`** とする。`local/` 自体には Git を置かず、`local/materials/.git` だけが独立したローカル Git で、submodule や worktree にしない。親 workspace の Git は祖先に存在するが、`/local/` 全体を除外する。履歴を取ることと GitHub へ送ることを区別する。外部 root はユーザーが選んだ場合に対応し、単に GitHub を避ける理由で workspace 外へ移さない。

既存 inbox の原著は移動・複製せず参照できる。新規原著の `local/originals/` は任意とし、画像・OCR・組版キャッシュは `local/cache/`、PDF と SyncTeX は `local/output/` に置く。これらはすべて materials Git の外にあり、親 Git からも除外される。既存の他の資料 Git・原著・履歴を変更しない。

## 配置前の親 Git 保護

教材を書く前に `/local/` を親 `.gitignore` に追加し、`git ls-files -- local` が空で実効的にも除外されることを確認する。独立した親 guard の設定は [source privacy](../../labo-layout/references/reference-privacy.md) に従う。既設 guard の更新には `python3 <policy>/scripts/reference_privacy.py refresh --workspace <workspace>` を使い、既に独立確認済みの二つの baseline をそのまま保つ。未確認 HEAD を新しい baseline にしない。未設定なら refresh は拒否するので、同参照の初回導入手順で既存 remote 履歴を確認する。これは guard 導入を伴う作業の指示であり、スキルの配置だけで Git を変更しない。

`python3 <policy>/scripts/reference_privacy.py check-local --workspace <workspace>` は `/local/` の除外、親 index、現在の policy と一致する guard runtime、実効 hooks と baseline を確認する。親 commit は `local/` のファイルも gitlink も拒否する。push は tip と全到達 commit の `local/` を検査し、途中で追加して後で削除した内容、branch、annotated tag も拒否する。`local/` に履歴例外はない。元の reference/corpus baseline は広げない。

## 教材 Git と組版

`python3 <policy>/scripts/book_materials.py install --workspace <workspace>` は新しい空の `<workspace>/local/` を初期化する。`check` も同じ既定 root を用いる。`--root <external-root>` はユーザーが選択した外部配置との互換用であり、他の Git の中に置く任意の入れ子 root は拒否する。

`check` は親保護（内部配置の場合）、独立 Git、remote が空、すべての push を拒否する実行可能な pre-push hook（URL 指定も対象）、Git filter の無効化、原著・キャッシュ・出力が materials Git の外にあること、symlink で境界を越えないことを確かめる。教材 Git に remote を設定しない。既存の別 Git に install を流用しない。

`python3 <policy>/scripts/book_materials.py build --workspace <workspace> --course <slug>` で `materials/courses/<slug>/main.tex` を組版する。`--root` は install/check と共通、`--dry-run` でコマンドを確認できる。XeLaTeX と latexmk を用い、キャッシュは root の `cache/<slug>/`、PDF と SyncTeX は `output/<slug>.*` に置く。両方の非空を確認してから出力を更新する。`main.tex` は `chapters/` を相対入力する。通常の `labo-build output build --source` の対象へ教材 root を渡さない。

出力更新後は [共通 PDF 検査](../../mathematical-navigation/references/pdf-checks.md) を行い、
結果を `cache/<slug>/navigation-main.json` に保存する。前回レポートと同じ文書の情報を
比較し、必要な補助ファイルはこのキャッシュから渡す。検査の失敗・未対応・依存不足は
ビルド結果とともに明示し、生成した PDF/SyncTeX は保持する。構造検査に加える期待経路、
描画画像、ビューア確認記録も教材のローカル境界内に置き、スキル Git や外部へ送らない。
教材の必須経路は本文入口の `main.navigation.json` に置き、同じビルドで照合する。
画像比較の基準 `cache/<slug>/navigation-main.render.json` は構造検査と別に保持する。

## 既存教材の移行

別スレッドを含む執筆者が停止したことを明示的に確認してから移す。活動中の root をコピーして二つの正本を作らない。親保護の確認後、`python3 <policy>/scripts/book_materials.py migrate --workspace <workspace> --from-root <old-root> --writers-stopped` は同一 filesystem 上で root 全体を rename し、Git 履歴・未 commit 内容・全ファイルの hash と mode を比較して、絶対 hooksPath だけを更新する。既存 destination、未確認停止、symlink、filesystem を越える移行は拒否する。失敗時は元へ戻す。

その後、私的な執筆指示・再開記録・案内・絶対 build path を実配置へ合わせ、本文を改変せず再組版する。PDF と SyncTeX の forward/reverse query が新しい正本を示すことを確認してから執筆を再開する。旧場所に活動可能な手順や symlink を残さず、必要なら移動先だけを指すローカル案内を残す。既に他スレッドへ渡した深い入口パスがある場合は、そのパスにも新しい正本への短い案内だけを残せる。本文・Git・旧コマンドを複製せず、旧場所では作業しないことを明示する。入口では最新の合意範囲・進捗・実際の本文を照合し、古い未着手記録や後続構想を現行の指示として残さない。移行前後の検証記録も私的領域に置く。

実際の書名・パス・出典・進捗を含む案内は `local/materials/` に集約できる。`reading/` に入口を置く場合は[ローカル案内](layout.md#workspace-からの案内)に従い個別除外する。追跡済み一覧を私的情報で上書きしない。

hooks は通常の誤操作を防ぐもので、意図的な bypass、別パスへのコピーや直接 upload を技術的に阻止するものではない。それらも保存規則に反する。保護失敗を回避せず修復し、clone・復旧・移行後にはローカル Git と hooks を再確認する。
