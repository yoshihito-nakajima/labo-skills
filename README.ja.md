# labo-skills

[English](README.md) | 日本語

実際の数学研究の中で育ててきた、共有の研究用スキル集。
**このリポジトリをフォークし、そのフォークを自分の研究リポジトリの
`.agents` サブモジュールとして追加して使う。** スキル・ルール・ツールは
その checkout の中で使い、改善し、役に立つ変更はここへプルリクエストで返す。
研究リポジトリの名前は何でもよい。以下では例として `labo` と呼ぶ。

研究計画が描くのは、論文の待ち行列ではなく**研究プログラムのストーリー**である。
そのストーリーは、先行文献や関連する Lean 形式化と並行して育て、見直していく。
文献は物語を作り替えることがあり、形式化は仮定・定義・障害を明らかにする。
英語の論文は、この進化する証拠から書く。イントロダクションもストーリーの一部である。
論文、スライド、読書ノート、Web ページは研究室の成果物である。
日本語訳は読解・確認のための補助資料で、原稿の原本は英語のままとする。
式や図も含めて、元の議論をそのまま保った連続した日本語の読み物が必要なときは
[japanese-translation](skills/japanese-translation/SKILL.md) を使う。
日本語で言い回しや推論を吟味できる。

## 公開と非公開の分離、所有

長大な本由来の教材は [reading-book](skills/reading-book/SKILL.md) が正本文、訂正の統合、
引継ぎ、公式出力を担当する。[reading-book-math-review](skills/reading-book-math-review/SKILL.md)
と [reading-book-output-review](skills/reading-book-output-review/SKILL.md) は
[共通の引継ぎ契約](skills/reading-book/references/production-handoff.md)に従い、
固定版を確認して担当別の保存先へ所見を返す。

- 公開: このリポジトリ、そのスキル、番号付きのレビュー規則、ソフトウェア、
  架空の例、プルリクエストで提案される汎用的な変更。
- 原則ローカルのみ: あなたの研究リポジトリ。研究計画、元の inbox 資料、Lean ファイル、
  原稿、参考文献、発表資料、個人用スキル、未公開の文章を置く。
  独立した `.agents` の方針Git以外は、privateを含めGitHubへ送らない。
  pushもPRも方針Gitだけから行い、親Gitはローカル履歴用にする。
  `.claude -> .agents` はローカルの入口であり、別の送信対象ではない。
  共通規則は [公開範囲](skills/labo-git/SKILL.md#publication-boundary)を参照する。
- 配布モデルは**フォークして、使って、改善して、選んで上流に貢献する**こと。
  研究者のフォークがその人の公開研究方針を持ち、非公開の親リポジトリは
  そのフォークのどのコミットを使っているかを記録する。サブモジュールは
  インストール済み CLI を包むオプションではなく、通常の運用形態である。
- `.agents/skills/` に追加したスキルは、方針フォークのものになる。
  非公開専用のスキルは、公開 checkout の外で、ホストが対応する場所に
  ユーザーが選んで置く。公開方針と研究は、独立した Git 履歴を持つ。
- 公開 PR は、**サニタイズされ、単独で再現できるコミット**から用意する。
  非公開の文章が自動で公開されることはない。

`momota1029/labo-skills` が現在の共有上流である。メンテナはここで直接作業できる。
他の研究者は通常、自分のフォークを使う。改善は、上流に提案しても採用されなくても
フォークの中で有用なままである。数学の流儀はさまざまで、ひとつの個人設定に
収束する必要はない。

## フォークをサブモジュールとして使う

まず `momota1029/labo-skills` を自分の GitHub アカウントか組織にフォークする。
研究リポジトリのルートで、`YOUR_ACCOUNT` を**自分のフォーク**の所有者に
置き換えて実行する:

```sh
git submodule add https://github.com/YOUR_ACCOUNT/labo-skills.git .agents
```

作業場所がまだ Git リポジトリでなければ、先に `git init` する。
`.agents` にすでにファイルがある場合は、サブモジュールに置き換える前に退避する。
`.gitmodules` は自分のフォークを指すようにして、上流 PR がマージされる前でも
研究ワークスペースが自分の改善を使えるようにする。

版を採用するときは、親のローカル履歴に `.gitmodules` と `.agents` の gitlink を記録する。
これはスキルのpush・PRとは独立しており、配布のために親を送信する必要はない。
設定済みのローカルワークスペースを復元した後は、記録されたチェックアウトを初期化する:

```sh
git submodule update --init --recursive -- .agents
```

通常の update は記録されたコミットをチェックアウトするだけで、detached HEAD に
なることも多い。「最新の上流版を使う」という意味ではない。方針を編集する前に、
サブモジュールの状態とリモートを確認し、研究者のフォーク上のブランチで作業する。
未コミットの変更は残す。`update --remote` を黙って実行したり、checkout をリセットしたり、
リモートを変えたり、フォークを作ったりしない。

## フォークで改善し、上流へ貢献する

環境の設定は [labo-git](skills/labo-git/SKILL.md) を使う。研究のGitはローカル保存用にし、
スキル側には送信先とレビュー済みコミットを照合するpushチェックを設ける。
既存の資料保護とローカルコミットを保ち、PRの作成は `labo-pr` が担当する。

通常の流れ:

```text
共有 labo-skills → あなたのフォーク → 研究リポジトリの .agents
共有 labo-skills ← 選んだプルリクエスト ← あなたのフォークでの改善
```

1. 研究で使いながら、`.agents` にある実際のスキルやツールを編集する。
   改善はフォークのブランチにコミットする。観察した問題を説明し、
   小さな再現可能な例で変更を確認する。
2. 版を採用するときは、親のローカルな gitlink にコミットを記録する。
   pushの依頼があれば、方針Gitから確認済みのフォークへ対象ブランチを送る。
   両者は互いを前提にせず、親のpushも伴わない。
3. 改善が他の人にも役立つなら、自分のフォークのブランチから共有上流へ
   焦点を絞った PR を送る。再利用できる変更と合成例だけを含め、原稿や
   フォーク固有の選択とは切り離す。改善の開発は `labo-self-improve`、
   貢献の準備は `labo-pr` が担当する。

改善を使うために上流の承認は要らない。PR を送るかは任意で、採用されても
誰かのワークスペースが自動で変わるわけではない。上流の変更を取り込むには、
fetch して内容を確認し、選んだ変更を自分のフォークに統合し、その版を検証してから、
親の gitlink を更新する。`labo-sync` がこの取り込みの流れを案内する。
非公開の研究リポジトリを普通に `git pull` するのに専用スキルは要らない。
フォーク自身の作業は残す。更新戦略として上流へのリセットをしない。

慣例として、`origin` は自分のフォーク、`upstream` は共有リポジトリを指す。
push や PR 先を選ぶ前に、実際の URL を確認する。リモート名だけでは所有者は
分からない。Git 操作はユーザーが求めた範囲に従い、本人が自分で push したい場合も含む。

スキルを非公開リポジトリへコピーするインストーラは無い。`vendor/` も、生成される
転送用 `SKILL.md` も、非公開 README の要件も、他のリポジトリの自動更新も無い。

checkout されたハーネスが唯一の権威である。再利用できる指示、形式、テンプレート、
実装、合成テストはすべてここにある。利用側のワークスペースがこの checkout に合わせるのであり、
逆ではない。使いながら実際の checkout を改善する。先に非公開の `labo` 実装を作って、
共有スキルが別のシステムを説明している状態にしてはいけない。非公開の研究と
ユーザー固有の記録は、親ワークスペースに残る。

## エージェント連携

Codex や Claude Code の実際の設定とネイティブの数学ロールは
[agent-host-setup](skills/agent-host-setup/SKILL.md) を使う。作成専用のインストーラは
モデルと effort の明示を要求し、既存の異なるロールは保持し、この checkout の現在の
契約を参照する。ホストによる検出、ロールの読み込み、実際のモデル実行、
親→子→孫の実行は別々の検証ステップである。
[呼び出し契約](skills/research-router/references/subagent-invocation.md)は、
共有された有限の子孫予算を割り当てる。
[数学ロール](skills/research-router/references/mathematical-roles.md)は、
補題の厳密なインターフェース、仮定の解消、統合、独立検証を定める。
ネイティブの上限と、実際の振る舞い上の割り当ては別々に報告される。

数学ロールの本文と説明は
[math-decomposer](skills/math-decomposer/SKILL.md)、
[math-proof-worker](skills/math-proof-worker/SKILL.md)、
[math-verifier](skills/math-verifier/SKILL.md) にある。プロジェクトの Codex アダプタは、
既存の子の中でこれらのスキルを読む。Claude は、フォークしたスキルの直接実行と、
同じスキルをプリロードするネイティブアダプタの両方に対応する。アダプタは
再度スキルを呼び出さない。Claude 固有の frontmatter が他のハーネスを設定することはない。

この方針ディレクトリは、Codex や一般のハーネス向けには `.agents`、Claude Code 向けには
`.claude` として配布する。両方に対応するには、`.agents` サブモジュールと、ディレクトリ全体への
相対エイリアス `.claude -> .agents` を使う。ネイティブの Claude 用 `agents/` と最小限の
`settings.json` は方針のルートに置いてある。外部の Codex 設定は、同梱のインストーラ/例から
展開する。[デプロイ手順](skills/agent-host-setup/references/deployment.md)は、
個別のスキルリンクや二つ目の方針コピーなしに、この三つの形をカバーする。
実際のサブモジュールを使ったテストが、新規デプロイ、外部の作業ディレクトリ、再配置、
再実行、衝突時の保持を確かめている。

実際のスキルは、この checkout 内の `skills/<name>/SKILL.md` にある。
`plugin.json` は、[Agent Plugin](https://agent-plugins.org/specification) ホスト向けに
このコレクションを記述するものでもある。プラグインのインストールはサブモジュール利用の
前提ではない。checkout したコレクションは、別のコピーを管理せず、場所を保ったまま
ホストに登録する。

[Codex はリポジトリのスキルを](https://developers.openai.com/codex/skills)
`.agents/skills` の下から検出する。このリポジトリを `.agents` にマウントすれば、本物のスキルが
コピーも転送リンクもなくそこに置かれる。他のホストは、それぞれの検出機構を使って
同じ checkout 済みコレクションを登録できる。既存のサブモジュールの配置でもランチャーは
実行できる。配置の移動は別の移行作業である。`AGENTS.md` は完全にユーザーのものとして残る。

ソースローカルのランタイムは、この checkout を `.claude` やユーザーが選んだ別のパスに
マウントしても動く。シェルの例ではそのパスに読み替えるか、実際に読み込まれたスキルの
ディレクトリからランチャーを解決する。ホストの検出は別問題で、ランチャーが動くことは、
どのホストでもあらゆる配置を自動検出することを意味しない。ハーネスの並行コピーは作らない。

各スキルは、自身の `references/` の下に自分の規則を持つ。特に `paper-referee` の基準は
スライドには適用されない。ルーティングやタスク固有の委任は、スキルと現在のエージェントホストが
担うもので、名前付きエージェントや保存済みのサブエージェントプロンプトを必須にするものではない。
非公開リポジトリに、これらの方針の README コピーは要らない。

## checkout 済みツールを動かす

ランタイムには Python 3.11+、Git、PyYAML 6.x が必要。PyYAML が無ければ、
選んだ Python 環境に入れる:

```sh
python3 -m pip install 'PyYAML>=6,<7'
```

ネイティブの Windows では `python3` の代わりに選んだ `python` を使う。
ランタイムに WSL は不要。ただし、証拠・リーダー記録に残るホスト相対の入力名は、
正規化したスラッシュ区切りのパスのままである。CLI のテキスト/JSON 出力は、
Windows でパイプした場合も含めて UTF-8 で、段階的に出す prefix テキストは元の
改行バイトを保つ。

このプロジェクトを**インストールして使うことはしない**。非公開の `labo` ルートから、
サブモジュール内のランチャーを呼ぶ。`example-paper` は実際の論文ディレクトリに置き換える:

```sh
python3 .agents/scripts/labo.py layout init
python3 .agents/scripts/labo.py research check
python3 .agents/scripts/labo.py research list --format json
python3 .agents/scripts/labo.py paper map --paper example-paper
python3 .agents/scripts/labo.py paper section --paper example-paper --name 01-introduction
python3 .agents/scripts/labo.py build --paper example-paper --dry-run
```

ランチャーは自分の隣のコードを import するので、方針 checkout と実行されるツールが
別々のインストールから来ることはない。`--workspace` を明示しない限り、研究ワークスペースは
ランチャーの**スーパープロジェクト**として Git が判定する。シェルのカレントディレクトリは
関係しない。スタンドアロンの checkout では `--workspace /path/to/private/labo` が必要。
エージェントは、シンボリックリンク経由で辿り着いた場合も含め、実際に読み込まれたスキルの
ディレクトリからの相対でランチャーを解決する。明示的に与えた相対ワークスペースパスは、
実行したディレクトリからの相対になる。`--workspace` は、選んだ末端コマンドの後ろに置く。
たとえば `python3 /path/to/labo-skills/scripts/labo.py evidence status --research example
--workspace /path/to/private/labo` のように書き、`evidence` の前のトップレベルオプションには
置けない。

## 研究ワークスペースを作って使う

サブモジュールとランタイム依存が揃ったら、エージェントに
「研究室を初期化して」や「inbox のこれで研究したい」と頼む。`labo-layout` スキルが
必要な構造を作り、`research-management` を使って実際の研究計画を育てる。
初期化は `layout init` として直接も使える。足りないコアディレクトリを追加し、
既存ファイルと `AGENTS.md` の内容を保ち、ワークスペースの ignore パターンを加える。
割り当て前のルート `inbox/` の中身はローカルのステージング置き場である。
割り当て済みの研究原本は、許される範囲でローカル履歴に記録できる。
`reference/` とcorpusは親Gitから除外し、研究資料をGitHubへ送る許可とはしない。
研究プログラムも、方針 README のコピーも作らない。

新しい項目は、layout スキルが管理するテンプレートから作れる:

```sh
python3 .agents/scripts/labo.py layout new research finite-observations \
  --title 'Finite observations and reconstruction' \
  --summary 'Determine which data can be recovered from finite observations.'
python3 .agents/scripts/labo.py layout new paper reconstruction
python3 .agents/scripts/labo.py layout new reference example-source
```

作成コマンドは `--dry-run` を受け付け、既存の項目を上書きしない。研究テンプレートは、
受け入れが終わったと言えるまでに、実際の入力から物語の部分を埋める必要がある。
ツールは inbox の原本をそのまま残し、割り当てと来歴はスキルが扱う。詳細は
[作成ワークフロー](skills/labo-layout/references/creation.md)と
[ディレクトリ契約](skills/labo-layout/references/layout.md)を参照。

## 数学的探索と安全なレイアウト移行

[research-exploration](skills/research-exploration/SKILL.md) は、標準の研究レイアウトに、
入れ子のカテゴリ、定理/問いのノード、コンパクトな進捗ツリーを加える。
`layout new research` は `plan.md`、`inbox/`、空の `exploration/tree.json` を作る。
エージェントが既存プログラムで計画の編集や探索を受け入れると、
[labo-layout](skills/labo-layout/references/research-migration.md) がその作業の一部として
足りない構造を追加し、元資料を保ち、既存ノードを再利用する。一覧化、説明、レポートのみの
レビュー、チェックは読み取り専用のまま。ツリーが無いのは単に構造がまだ無いというだけで、
古い計画や主張のステータスの意味は変わらない。バージョン付きのツリーは自分の形式を
示すので、`plan.md` や `claims.yaml` に別のスタイル欄は要らない。分類、作業の進捗、
数学的依存は別々である。まず要約を読み、必要な詳細ファイルを選んで読む:

```sh
python3 .agents/scripts/labo.py research exploration init --research finite-observations --if-missing
python3 .agents/scripts/labo.py research exploration add --research finite-observations \
  --node reconstruction --kind question --title 'Reconstruction question' \
  --summary 'Identify the hypotheses needed for reconstruction.' \
  --next 'Test a finite counterexample.' --proof-required
python3 .agents/scripts/labo.py research exploration tree --research finite-observations --depth 2
python3 .agents/scripts/labo.py research exploration show --research finite-observations --node reconstruction
python3 .agents/scripts/labo.py research exploration tree --research finite-observations --with-evidence
python3 .agents/scripts/labo.py research exploration check --research finite-observations
```

軽量なツリーはメタデータだけを読み、形式的な記録は未確認と表示する。
`--with-evidence` と `check` は、さらに、リンクされた証拠と入力の鮮度も調べる。
数は範囲を区切った作業を数えたものであり、証明済みの数学の割合ではない。
更新はネイティブのプロセスロック、アトミックな JSON 置換、ノードごとの楽観的リビジョンを使う。
古い更新が失敗したら、読み直して調整する。並列ワーカーは名前付きのノードと別々の
記録/モジュールを持ち、プログラムのストーリー、共有 Lean 定義、最終統合は
一人の統合担当が持つ。

初期化は既存のツリーを、並行作業中でも安全に再利用する。ノードを重複させず、設定も
上書きしない。過去の主張すべてからノードを生成するのではなく、現在の範囲を区切った作業から
始める。具体的な主張を登録するときに `claims.yaml` を作る。逐次/並列モードは実行の選択で、
レイアウトの採用やタスクの権限とは別である。

ツリーに記録された作業では、証明を含むすべての結果が、タスクを `done` にする前に
Lean の証拠を必要とする。定理/補題ノードは自動的に必要となる。その他の数学的結論、例、
反例は `--proof-required` を付ける。`claims.yaml` を定理の索引として再利用し、
正確なソース/宣言、実質的なカーネル報告と数学的アラインメント報告、その主張と前提を
直接カバーする現行の形式レビューを揃える。既存の証拠形式と過去の研究ステータスは
意味を保つ。[Lean の完了条件と配置](skills/research-exploration/references/lean.md)を参照。

小さなモジュールを、Lean 環境ごとにまとめたプロジェクトに置くのを推奨する。現行の
フィンガープリントは、対応づけられたプロジェクト全体の `.lean` ソースにかかるので、
モジュールを足すと別の結果のレビューが古くなりうる。関連する編集を終えてからレビューを
更新する。変更/再利用の境界が違うなら、プロジェクトを分ける理由になる。
古くなった done タスクは再確認が必要になる。`current_records` は入力が一致した評価記録を
指すもので、数学の自動的な認証ではない。既存の選択ソース再生は、用意済みの import を
すべて再ビルドするわけでも、あらゆるローカル依存に対応するわけでもない。
未対応の実行は pending のままとなる。パス型パッケージを使う完了記録には、明示的な
ローカル依存のツリースナップショットが必要。バックグラウンドのスケジューラも、
過去の自動形式化も導入しない。

## 論文読解の完了条件

実質的な論文読解では、[資料台帳](skills/reading-reference/references/resource-ledger.md)
（本文→補足の順、必読の補足、取得の責任）、
[系譜・比較の目録](skills/reading-reference/references/lineage-and-comparison.md)、
[節の連鎖と一文ごとの注釈](skills/reading-reference/references/unit-chain-and-claim-gloss.md)を
一つのデータファイルに記録し、`scripts/check_coverage.py` を完了の検査として通す。
論文の手法のコードは、隔離した環境で実行する
（[実行環境](skills/reading-reference/references/methods.md#execution-environments)）。
方法論文の詳細ノートを、見て動かして理解するには、[reading-companion](skills/reading-companion/SKILL.md)
で私用の1ファイルの HTML を作る。特徴ごとに、背景、売り、既存の方法とそのコード、
パラメータを操作部に結びつけた著者コード、著者コードを格子点で実行した図を並べる。公開はしない。

Web ページ、HTML の解説、コンパニオン、長いノートは、渡す前に
[exposition-review](skills/exposition-review/SKILL.md) の敵対的な査読を通す。
版を固定し、[exposition-flow-review](skills/exposition-flow-review/SKILL.md) が新しい文脈で
全体を読んで実際の流れを書き出し、つなぎ方を含む構成案を出す。
[exposition-critique](skills/exposition-critique/SKILL.md) は想定読者が迷う・誤解する箇所を
引用つきで指摘する。書き手はすべての指摘に判断を付けて直し、新しい版を別の査読者に回す。

証明を、自分のものでも他人のものでも、頼る前に攻めて確かめるには、
[proof-adversarial-review](skills/proof-adversarial-review/SKILL.md) が、固定した主張に対して
七つの独立した視点（逐行監査、独立検証、反例探索、仮定と依存関係の監査、先行研究への攻撃、
敵対的査読、数値確認）を走らせ、親が報告を統合して確定した指摘と疑いを分ける（`findings.py`）。
その結果を 1 枚で見るには、[reading-proof-review](skills/reading-proof-review/SKILL.md) が、出典つきの
ステップ台帳から私用の1ファイルの HTML を作る。依存関係図、証明が畳まれるステップのカード、
キーと標準の比較、査読の指摘、先行研究との比較、規則で上限が決まる論文化の指標を並べる
（`check_ledger.py`、`indicator.py`、`build_review_page.py`、`check_review_page.py`）。
同じスキルは、証明を追うための読解用の本（`proof_book.py`）も作る。証明をブロックに切り、各式の前にその理由を置き、
難所と各ステップの役割を示し、相互にリンクした HTML と、式変形をすべて書いた PDF を 1 つずつ出す。
どちらも原稿を編集せず、正しさを保証しない。

## 必須の研究ポジショニング

プログラムを枠づける、または大きく枠づけ直すとき、実質的な原稿作業を始める、または
貢献の物語を改めるとき、自分の研究の発表で新規性や比較の主張をするときには、スキルは
[研究ポジショニング調査](skills/reading-reference/references/research-positioning.md)を要求する。
問い、結果、仮定、手法が変わったら該当する比較を更新し、投稿前にもう一度探索する。
通常の簿記作業や誤字だけの編集では調査をやり直さない。レポートのみのレビューは
ファイル編集の許可にならない。

調査では、別の用語や隣接分野も探し、引用を両方向にたどり、実際に確認した一次資料の
箇所を、実際の研究の主張と比べる。検索、資料の版、継承した要素と新しい要素、
未解決の手がかり、記法/慣習の決定は、ひとつのプログラム単位のメモにまとめて再利用する。
[メモのテンプレート](skills/reading-reference/assets/research-positioning.md)はこの
checkout にあり、記入済みの非公開記録は研究プログラムと一緒に、通常
`research/<slug>/literature-positioning.md` か既存の適切な記録に置く。
発見と正確な引用は論文自体に持ち込む。どんな検索も、先行研究の網羅を保証せず、
ヒットが無いことから新規性を証明することもできない。これはスキルのワークフローで、
新しい CLI のゲートでも、必須の主張カタログでも、ホスト方針のコピーでもない。

執筆とその範囲のレビューでは、
[コーパスに基づく用語監査](skills/reading-reference/references/terminology-audit.md)も使う。
実際の対象の型、役割、慣習を、確認した定義や式と比べ、正当な別表現は残し、
資料の欠落は記録する。コーパスの文体の手がかりはあくまで弱い手がかりで、
意味の検証は数学そのものを確認する。

イントロダクションの中心的な問い、具体的な意義、語りの順序には、`paper-writing` と並べて
[paper-introduction](skills/paper-introduction/SKILL.md) を使う。実際の結果と
ポジショニングの証拠から物語を形づくり、新規性の主張も固定した段落の型も押しつけない。

論文全体の設計や構造の見直しには [paper-structure](skills/paper-structure/SKILL.md) を使う。
現在の素材を、目的、入力、出力、証明/読者の経路つきの節案に対応づける。
[knowledge-dependencies](skills/knowledge-dependencies/SKILL.md) は、定義・仮定・結果の
出典つきグラフ(任意)を管理し、必須の前提と物語上の参照を区別する。checkout 済みの
Python ハーネスが、宣言された依存を整列し、実際の閉路と下流のブロックされたノードを
区別して診断し、提案された順序全体を検査し、前提の閉包や変更の影響を計算する:

```sh
python3 .agents/scripts/labo.py dependencies sort --graph research/example/dependencies.yaml
python3 .agents/scripts/labo.py dependencies closure --graph research/example/dependencies.yaml --node conclusion
python3 .agents/scripts/labo.py dependencies impact --graph research/example/dependencies.yaml --node uniform
```

[グラフ契約](skills/knowledge-dependencies/references/graph.md)が、スキーマと五つのコマンドを
すべて定義する。検査は**宣言された**必須の辺をすべてカバーするが、完全な抽出と数学的な
妥当性にはソースのレビューが必要。証明の順序と論文の読者向けの順序は、冒頭での明確な
述べ方と後ろでの証明によって異なってよい。通常の原稿に依存グラフへの移行は要らない。

## 任意の証拠とレビュー記録

引き継ぎや再利用が必要な結果には、`research-management` が任意の
[証拠プロトコル](skills/research-management/references/evidence.md)を持つ。安定した主張 ID が、
正確な主張文、証明ノート、確認した文献、主張間の依存、任意の Lean 範囲の対応づけを結ぶ。
これは研究のストーリーを補うもので、プログラムのステータスを増やしたり、ワークスペースの
移行を求めたりしない。

```sh
python3 .agents/scripts/labo.py evidence init \
  --catalog research/finite-observations/claims.yaml
python3 .agents/scripts/labo.py evidence check \
  --catalog research/finite-observations/claims.yaml
python3 .agents/scripts/labo.py evidence snapshot --kind writing \
  --tree writing/reconstruction
```

初期化には既存の親ディレクトリが必要で、置き換えはしない。`snapshot` は、ファイルを書かず
主張を承認もせずに、保留中の YAML 記録を表示する。保存したレビューは、実際の入力バイト
(未コミットの変更を含む)、選んだ依存、この checkout の関連する方針ファイルに結びつく。
実際のレビューの後に、プロトコルの記述どおり、著者、日付、判定、ハッシュ付きの報告を
記録する。その記録は、スナップショットしたツリーの外に置く。

```sh
python3 .agents/scripts/labo.py evidence check \
  --record research/finite-observations/reviews/writing.yaml --strict
```

検査は、現行、保留、古い、失敗、不正な記録を区別する。保留や古い記録は、`--strict` を
付けない限り警告にとどまる。これらは構造と鮮度の検査であって、数学的な認証でも、
Lean の自動実行でも、合格したレビューを更新してよいという許可でもない。通常の研究、
執筆、`research check` には、これらのファイルは要らない。

### 範囲の診断とプログラムの一覧

writing のレビューが原稿をカバーすると判断する前に、文字どおりの TeX 依存を調べ、
意図した選択と比べる:

```sh
python3 .agents/scripts/labo.py evidence scope --paper reconstruction \
  --record research/finite-observations/reviews/writing.yaml --format json
python3 .agents/scripts/labo.py evidence status --research finite-observations
```

[`evidence scope`](skills/research-management/references/evidence-scope.md) は、対応している
文字どおりの include、グラフィックス、参考文献ファイル、ローカルのクラス/パッケージを
たどる。不足、省略、曖昧、未解決の入力は、黙ってレビューに加えず、報告する。
動的な TeX や外部パッケージの解決は、明示された制限として残る。`--record`、`--file`、
`--tree` が無ければ、依存を見つけるだけで、カバー範囲の主張はしない。
診断用のコンパイルルートの既定の候補は、ソースの親ディレクトリ。
`output build --source` のようにワークスペースルートでビルドするなら `--compile-root .` を使い、
別の実際のワークスペース相対の作業ディレクトリは明示して指定する。

[`evidence status`](skills/research-management/references/evidence-status.md) は、選んだ
ひとつのプログラムの任意のカタログとレビューを読み、記録された主張のステータスを、
現行/古い/保留/失敗のレビューカバー範囲とは別に表示する。writing のレビューは証明の
カバーを与えず、依存は、フィンガープリントが含まれたというだけではレビューを継承しない。
過去の記録や矛盾する記録も見える形で残る。狭い範囲で現行記録だけを確認したいときは、
既定の探索ではなく、繰り返し指定できる `--record` を使う。両コマンドは読み取り専用で、
JSON と `--strict` に対応し、カタログを採用していないプログラムを移行することはない。

### 明示的な Lean 再生

ひとつの正確な形式的対応づけについて、読み取り専用の実行計画を調べる:

```sh
python3 .agents/scripts/labo.py evidence replay \
  --catalog research/finite-observations/claims.yaml --claim finite-cover
```

用意済みでバージョン固定のネイティブ Lean ツールチェーンを呼び出すのは、明示的な
`--execute` だけ。[`evidence replay`](skills/research-management/references/formal-replay.md) は、
選んだソースを新しい一時成果物にビルドし、対応づけた宣言の型、出力される定義、
推移的な公理を観察する。実際のコマンド、出力、前後の入力ハッシュを記録し、
`sorryAx` があれば失敗する。それ以外の公理は、信頼性のレビューのために見える形で残る。
監査可能な完全な報告は `--format json` で得る。テキスト出力は、巨大になりうる
ファイルハッシュのマップを省く。

これは完全な Lake 再ビルドでも、独立した証明検査器でもない。用意済みの import は
フィンガープリントされるだけで再ビルドされず、対応する標準レイアウトと厳密な
バージョン要件は意図的に狭い。足りない前提条件は利用不可のままで、Lake、elan、
インストーラ、キャッシュのダウンロード、依存の取得は一切起動されない。
**Lean のコードはコンパイル中に任意のコードを実行しうる**ので、信頼できる
プロジェクト/依存だけを実行するか、外部のサンドボックスを使う。ランナー自体は
ネットワークやファイルシステムの隔離ではない。再生が完了しても、主張は更新されず、
レビューは承認されず、非形式から形式へのアラインメントも成立しない。

### 段階的な初読者の記録

段階的な読みが明示的に求められたとき、コーディネータは
[`paper reading`](skills/paper-referee/references/staged-reading.md) を使える:

```sh
python3 .agents/scripts/labo.py paper reading start \
  --source writing/reconstruction/sections/01-introduction.tex \
  --session research/finite-observations/reviews/reader-one.json --reader reader-one
python3 .agents/scripts/labo.py paper reading next \
  --session research/finite-observations/reviews/reader-one.json --through-line 8
python3 .agents/scripts/labo.py paper reading observe \
  --session research/finite-observations/reviews/reader-one.json \
  --understanding 'The visible text asks ...' --confusion 'The first missing relation is ...'
```

非公開セッションの親ディレクトリは、あらかじめ存在していなければならない。各回の提示は
累積した prefix だけを返し、最初の理解と最初の混乱を記録するまでは、次の提示に進めない。
`observe --rescue` は、最初の記録を書き換えずに、後からの立て直しを追記する。
ソースのバイト列や同一性が変わると、セッションは無効になる。`status` は、先の本文や
観察の文章を見せずに、進み具合を示す。独立した読みのためには、コーディネータが実際に
新しい読者へ中立的な説明と提示済みの prefix だけを渡さなければならず、
`--mode independent` だけでは何も証明されない。これは段階的な出力であって、
ファイルシステムのサンドボックスでも、署名付きログでも、レビューの承認でもない。

## 調べる、ビルドする

`research list` が読むのは、`research/*/plan.md` の YAML frontmatter *だけ*。本文、inbox、
Lean ソース、原稿は読まない。ステータスは `in_progress` と `completed` の二つだけ。
一時的に手を付けていないプロジェクトも `in_progress` のままで、再構成は Git 履歴と
散文の計画で表現する。

`paper map` は、アセンブリファイル `main.tex` を読んで、文字どおりの
`\input{sections/NN-name}` / `\include{sections/NN-name}` を原稿の順序で選び、その各冒頭
(`% LABO:INTRO-END` までの部分)だけを読む。TeX マクロは展開せず、動的/条件付きの
取り込みにも対応しない。`paper section` は選んだ一節だけを読み、論文全体は読まない。
このツールが数学的な主張を認証することは一切ない。

`output build` は `latexmk` に委ねる。中間ファイルは `writing/<paper>/.temp` に、
PDF と SyncTeX は直接 `output/` に `<paper>.pdf` と `<paper>.synctex.gz` として書くので、
すべてのプロジェクトをまとめて選べる。出力の組はプロジェクトの slug で名づけられ、
同じプロジェクト内のルートは同じ組を上書きする。名前を付けたソースは、
中間キャッシュ名を別々に持つ。`--dry-run` は呼び出しを表示する。
実際のコンパイルには `latexmk` を含む TeX ディストリビューションが必要。
成功とは PDF と SyncTeX の両方があることで、キャッシュ済みのビルドなのに
SyncTeX が無いときは、強制再ビルドを最大一回行う。ビルドが成功すると、
既知の古い PDF/SyncTeX の組から、既定で 30 ファイルまで刈り込む。
ビューアは `--open` を付けない限り開かない。保護されたファイルや未認識のファイルが
上限を超えたままにしている場合は警告する。`--max-files` で上限を変え、
コンパイルせずに掃除するには `output prune --max-files 30` を使う。
ワークスペース全体で保持されるロックが、ネイティブの POSIX/Windows ロックにより、
同時ビルドと掃除を直列化する。

既存のドキュメント名には、`writing/<slug>/` か `reading/<slug>/` の下の TeX ルートを指定して
`output build --source` を使う。出力の組はプロジェクトの slug で名づけられるので、
同じ slug の下の複数のルートは互いに上書きする。ソースはその場に残り、キャッシュは
`.temp/` に置かれる。エンジンのディレクティブや `xeCJK` などのパッケージは検出され、
`--engine` で上書きできる。作業ディレクトリの振る舞いは
[ビルド契約](skills/labo-build/references/build-contract.md)に書いてある。

## 品質チェック

この方針 checkout で、ランタイム依存を入れた状態から:

```sh
python3 -m unittest discover -s tests -v
```

テストには、`.agents`、`.claude`、中立的なパスにマウントした実際の一時 Git サブモジュールが
含まれ、このプロジェクトをインストールせずに、無関係な作業ディレクトリからソースローカルの
実行をする。証拠のテストも、ホスト側に方針のコピーが無くても、方針のバイトが変われば
レビューが無効になることを確かめる。
[CI ワークフロー](.github/workflows/ci.yml)は、Python 3.11 と 3.13 で、Linux と Windows の
ネイティブ上で全スイートを走らせ、プロセス間の出力ロックと三つのサブモジュールマウントも
含める。別の Linux ジョブは、固定 URL と固定 SHA-256 から公式 Lean 4.19.0 を明示的に用意し、
本物のスモークテストを要求する: 通常の定理、推移的な `sorryAx`、独自の公理。この依存の準備は
CI のステップで、再生ランナーの暗黙の機能ではない。

ポジショニングの経路検査は、担当するスキルがひとつのローカルプロトコルを共有していることと、
メモのテンプレートが checkout 相対リンクを壊さずにコピーできることを確かめる。
[forward-use パケット](tests/fixtures/reading-reference/research-positioning.md)は、
新しいエージェント向けに、起草、局所編集、比較、更新の小さなタスクを用意するもので、
単体テストスイートでは走らない。リンク検査も、エージェントの実行の成功も、
文献の網羅や数学的新規性を保証しない。

用意済みのローカルツールチェーンで同じ本物のスモークを必須にするには、
`test_formal_replay.py` を実行するときに、そのディレクトリを `LABO_REPLAY_TOOLCHAIN_DIR` に、
`LABO_REQUIRE_REAL_LEAN=1` を設定する。ツールチェーンを選ばなければそのテストは正直に
スキップされ、必須にすれば準備不足は失敗になる。モックテストと Linux の本物の Lean ジョブは、
Windows での本物の Lean 実行や、TeX の見た目の正しさを保証しない。

テストとフィクスチャに非公開の研究は含まれない。ワークスペースへの変更は選んだ非公開
ワークスペースの範囲にとどまる。明示的な Lean 実行は一時ビルドディレクトリも使い、
信頼するコード自身の副作用を持ちうる。CLI 自体は GitHub に対する変更を一切行わない。
`pyproject.toml` は開発や任意のパッケージ化のために残してあるもので、
サブモジュールのデプロイ機構ではない。

## 範囲

ツールが実装するのは、ワークスペースの初期化、項目の作成、研究の一覧、任意の出典つき
数学的依存の検査/整列/閉包/影響、任意の証拠のスナップショット/範囲/ステータス/再生、
範囲を区切った/段階的な TeX の読み、TeX のビルド、出力の掃除。スキルが定義するのは、
レビュー、研究のライフサイクル、ディレクトリレイアウト、自己改善、PR、スライド、
Web 公開のワークフロー。公開 PR は意図的な選択で、利用できる Git/GitHub のツールか人間の
直接の push で行う。特定のコネクタやブランチ命名規則は必要としない。
