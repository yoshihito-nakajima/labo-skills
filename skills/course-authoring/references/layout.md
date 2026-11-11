# Local production and role folders

新規配置の例。表示だけでは作成・移動しない。各案件の入口は[役割フォルダ](role-folders.md)、
Gitと原著の保護は[保存規則](storage.md)に従う。

```text
workspace/
├── .agents/                 # 汎用スキル・コードのみ。原著を入れない
└── local/                   # 親Gitの /local/ 除外。ここにGitを作らない
    ├── original/            # 原著。全Gitからignore、ローカルGitにも登録禁止
    ├── books/<slug>/        # 本由来の制作担当、既定Gitなし
    ├── topics/<slug>/       # テーマ型の制作担当、既定Gitなし
    ├── review/<case>/       # 通常確認担当
    ├── hard_review/<case>/  # 本格査読担当
    ├── cache/               # OCR・画像・組版キャッシュ、Gitなし
    ├── output/              # PDF・SyncTeX、Gitなし
    └── materials/           # 既存の独立ローカルGitと教材を維持
```

books/topicsの制作単位は `START_HERE.md`、`plan.md`、`progress.md`、`main.tex`と
本文入力を持つ。原著の台帳は原著を使う案件の必要範囲だけに置く。テーマ型に
原著全章の対応表を要求しない。数学の正本は一つ、レビューには固定入力を渡す。
既存 `materials/courses/<slug>/` の下にある案内・台帳・本文・レビューを移動しない。

## Workspace からの案内

講義の作成・移行、または再開中に正本・出力の場所が変わったときは、親 workspace の `reading/` から辿れるローカル案内を整える。講義一覧の `reading/README.md` と対象の `reading/<course>/README.md` は一例であり、既存の案内があれば内容を保って統合する。一覧には各講義の入口、正本と出力へのリンクを置き、詳細案内には plan・progress・本文・資料台帳・PDFを結ぶ。状態の正本は course の `progress.md` とし、一覧へ完了数など変動する進捗を複写しない。実在するリンクと保存境界を確認する。

実資料を含む案内は親 Git から**個別のパスで除外し、未追跡を確認してから**書く。対象が既に追跡されているなら、私的なパス・資料名・進捗をそこへ書かず、既存内容を保つ。別の個別除外したローカル案内を設け、追跡される側には必要なら一般的な入口だけを置く。追跡済みファイルを黙って untrack しない。案内のために symlink で教材の保存境界を越えない。表示だけの依頼やスキルのインストールだけでは案内を作らない。
