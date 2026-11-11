# Local storage and build

原著は **ローカル専用Gitを含む、すべてのGitで追跡しない**。新規原著の置場は
workspace内の `local/original/`。親Gitの `/local/` 除外に加え、local内の
`.gitignore` に `/original/` を明示する。`original/` 自身にも子にもGitを作らず、
原著のコピー・スキャン・抜粋入りの固定入力もGitへ登録しない。既存 `inbox/` や
旧 `local/originals/` の原著は保護を保ってそのまま参照でき、勝手に移動しない。
ignoreは追跡済みファイルを解除しない。既に追跡された原著を見つけたら追加を止め、
既存の履歴を削除せずに対象と修復の必要を報告する。スキルGitへ実資料を入れない。

教材原稿・計画・進捗・レビュー・OCR・出力も外部送信しない。GitHubのprivateも
送信先にしない。汎用のスキル・コード・架空例だけがpolicy Gitの対象となる。

## New projects and existing courses

新規の本由来教材は `local/books/<slug>/`、テーマ型は `local/topics/<slug>/`。
双方とも既定はGitなし。`local/`、`books/`、`topics/`、`review/`、`hard_review/`、
原著・キャッシュ・出力の各フォルダにはGitを作らない。原稿のローカル履歴を
ユーザーが選んだ場合だけ、そのプロジェクトに独立したGitを置ける。remoteなし、
全push拒否hook、外部filter無効化の同じ保護を使う。Git作成は自動で行わない。
原著入りinputやレビュー証拠をこのGitへコピーしない。

既存の `local/materials/.git` と `materials/courses/<slug>/` は互換配置として維持する。
使用中の本文・レビュー・履歴をこのスキル更新で移行・複製・削除しない。
新規フォルダは[担当別配置](role-folders.md)を参照。Gitなしでも、正本、現在進捗、
不変の確認入力と内容hashによって再開・版識別・担当間受渡しを行う。

## Build without requiring Git

`<policy>` は実際に読み込んだスキルcheckoutのルートへ解決する。

```sh
python3 <policy>/scripts/book_materials.py install --workspace <workspace> --kind topics --course <slug>
python3 <policy>/scripts/book_materials.py check --workspace <workspace> --kind topics --course <slug>
python3 <policy>/scripts/book_materials.py build --workspace <workspace> --kind topics --course <slug>
```

本由来なら `--kind books`。installは指定プロジェクトの案内・plan・progress・chaptersのみを
初期化し、数学やmain.texは作らず、Gitも作らない。既存rootを空にする必要はなく、
既存プロジェクトは上書きしない。`main.tex`は制作時に書く。出力は衝突を避けて
`local/output/topics-<slug>.pdf` と同名SyncTeX、キャッシュは `local/cache/topics-<slug>/`。
booksも同じ命名。`--dry-run`はbuildに使える。内部配置では下記の親保護を確認する。

既存コースは従来どおり `--kind`なし、`--course <slug>` を使い、出力名も変わらない。
保存境界確認はGitなしでも行い、GitがあるプロジェクトだけGit固有の保護を検査する。
テーマ型を研究論文の `writing/` へ移したり、通常のlabo-buildへ渡したりしない。

## 配置前の親 Git 保護

教材を書く前に `/local/` を親 `.gitignore` に追加し、`git ls-files -- local` が空で実効的にも除外されることを確認する。独立した親 guard の設定は [source privacy](../../labo-layout/references/reference-privacy.md) に従う。既設 guard の更新には `python3 <policy>/scripts/reference_privacy.py refresh --workspace <workspace>` を使い、既に独立確認済みの二つの baseline をそのまま保つ。未確認 HEAD を新しい baseline にしない。未設定なら refresh は拒否するので、同参照の初回導入手順で既存 remote 履歴を確認する。これは guard 導入を伴う作業の指示であり、スキルの配置だけで Git を変更しない。

`python3 <policy>/scripts/reference_privacy.py check-local --workspace <workspace>` は `/local/` の除外、親 index、現在の policy と一致する guard runtime、実効 hooks と baseline を確認する。親 commit は `local/` のファイルも gitlink も拒否する。push は tip と全到達 commit の `local/` を検査し、途中で追加して後で削除した内容、branch、annotated tag も拒否する。`local/` に履歴例外はない。元の reference/corpus baseline は広げない。

## 既存 materials Git と組版（互換）

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

## 既存教材の移行（別途依頼された場合のみ）

別スレッドを含む執筆者が停止したことを明示的に確認してから移す。活動中の root をコピーして二つの正本を作らない。親保護の確認後、`python3 <policy>/scripts/book_materials.py migrate --workspace <workspace> --from-root <old-root> --writers-stopped` は同一 filesystem 上で root 全体を rename し、Git 履歴・未 commit 内容・全ファイルの hash と mode を比較して、絶対 hooksPath だけを更新する。既存 destination、未確認停止、symlink、filesystem を越える移行は拒否する。失敗時は元へ戻す。

その後、私的な執筆指示・再開記録・案内・絶対 build path を実配置へ合わせ、本文を改変せず再組版する。PDF と SyncTeX の forward/reverse query が新しい正本を示すことを確認してから執筆を再開する。旧場所に活動可能な手順や symlink を残さず、必要なら移動先だけを指すローカル案内を残す。既に他スレッドへ渡した深い入口パスがある場合は、そのパスにも新しい正本への短い案内だけを残せる。本文・Git・旧コマンドを複製せず、旧場所では作業しないことを明示する。入口では最新の合意範囲・進捗・実際の本文を照合し、古い未着手記録や後続構想を現行の指示として残さない。移行前後の検証記録も私的領域に置く。

実際の書名・パス・出典・進捗を含む案内は `local/materials/` に集約できる。`reading/` に入口を置く場合は[ローカル案内](layout.md#workspace-からの案内)に従い個別除外する。追跡済み一覧を私的情報で上書きしない。

hooks は通常の誤操作を防ぐもので、意図的な bypass、別パスへのコピーや直接 upload を技術的に阻止するものではない。それらも保存規則に反する。保護失敗を回避せず修復し、clone・復旧・移行後にはローカル Git と hooks を再確認する。
