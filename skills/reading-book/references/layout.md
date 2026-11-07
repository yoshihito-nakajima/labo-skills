# 本の配置

表示依頼では次を**例**として示し、実際の対象があるときだけその実配置を調べる。表示だけで作成・移動しない。

```text
workspace/
├── inbox/                         # 既存原著をその場で参照可、親 Git 除外
├── .agents/                       # 汎用手順・コード・架空テストだけ
└── local/                         # 親 Git の /local/ 除外。ここに .git は置かない
    ├── originals/                 # 任意の新規原著、materials Git の外
    ├── cache/                     # OCR・ページ画像・組版キャッシュ、Git の外
    ├── output/                    # PDF・SyncTeX、Git の外
    └── materials/                 # 独立したローカル専用 Git。remote なし、全 push 拒否
        ├── .git/
        ├── sources/               # 資料 ID・版・位置・役割
        ├── catalog/               # 数学 ID・正本文位置・出典・依存・確認
        ├── shared/                # 実際に共用する数学だけ
        ├── retired/               # 旧稿記録。現行本文ではない
        └── courses/<course>/
            ├── START_HERE.md      # 必要な私的な執筆・再開指示
            ├── plan.md            # 読者・学習順序・資料の役割
            ├── main.tex           # 正本の入口
            ├── chapters/          # 単一の数学本文
            ├── notes/             # 局所的な検討記録
            └── progress.md        # 実際の状態・再開点
```

原著・派生物はローカルのみ。`materials/` だけが独立 Git であり、履歴を取れるが送信しない。`retired/` はこの Git 内の退役記録で、`originals/`、`cache/`、`output/` は Git の外にある。外部 root はユーザーが選んだ場合だけ対応する。`.agents/skills/reading-book/` と `scripts/book_materials.py` は汎用の仕組みで、実資料を含まない場合だけスキル Git の対象となる。

## Workspace からの案内

講義の作成・移行、または再開中に正本・出力の場所が変わったときは、親 workspace の `reading/` から辿れるローカル案内を整える。講義一覧の `reading/README.md` と対象の `reading/<course>/README.md` は一例であり、既存の案内があれば内容を保って統合する。一覧には各講義の入口、正本と出力へのリンクを置き、詳細案内には plan・progress・本文・資料台帳・PDFを結ぶ。状態の正本は course の `progress.md` とし、一覧へ完了数など変動する進捗を複写しない。実在するリンクと保存境界を確認する。

実資料を含む案内は親 Git から**個別のパスで除外し、未追跡を確認してから**書く。対象が既に追跡されているなら、私的なパス・資料名・進捗をそこへ書かず、既存内容を保つ。別の個別除外したローカル案内を設け、追跡される側には必要なら一般的な入口だけを置く。追跡済みファイルを黙って untrack しない。案内のために symlink で教材の保存境界を越えない。表示だけの依頼やスキルのインストールだけでは案内を作らない。
