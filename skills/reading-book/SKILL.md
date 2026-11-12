---
name: reading-book
description: Build and resume book-led mathematical courses by mapping source editions, adopted sections and exercises into one canonical local text under course-authoring. Not topic-led notes, ordinary paper reading or short book questions.
---

# Reading Book

本を主資料として長い数学教材を作る。原著の版・章節・採否・本文対応をこのスキルで管理し、
共通の制作・保存・進捗・訂正統合・公式出力は
[course-authoring](../course-authoring/SKILL.md) に従う。全訳を指定された場合はその指定を守る。
本を起点としない教材・長いノートはcourse-authoringから始める。

## 原著から一つの教材へ

1. 既存の計画、進捗冒頭、対象本文、公開依頼・返却を読み、最新の合意と実物から再開する。
   旧ログの全通読や完了済みの復旧・検査へ戻らない。既存本文・保存場所・担当を保つ。
2. [本の処理手順](references/book-workflow.md)で、資料の巻・版・印刷頁とPDF頁、採用範囲、
   必要な演習、本文位置と直接前提を対応付ける。主資料と補助資料の役割を分ける。
   全章配置・資料取得は証明完成や全演習採用を意味しない。
3. 原著の流れを生かして問い・定義・例・定理・証明・応用を組み立てる。同じ内容の
   既存本文は再利用し、原著ごとの独立した第二本文や証明部品庫を増やさない。
   複数資料の定義域・仮定・量化子・正規化・依存を照合する。
4. 採用した範囲は必要な定義・構成・証明・計算・演習解答を閉じる。原著のsketch、引用、
   後続で使わないことを自動的な省略理由にしない。誤りは修正し、原著との差と使用先を追う。
   範囲削除、展望への移動、仮定強化・結論弱化は理由・影響・代替・残る義務を報告する。
5. 自己点検と選択的独立確認を分け、章の区切りでは
   [採用範囲との完了照合](references/book-workflow.md#章講義の完了判定)を行う。
   返却待ちでも依存しない制作を続ける。本格的な敵対的査読は別の固定範囲への依頼とする。

原著の位置と引用は [reading-referenceの出典規則](../reading-reference/references/source-rules.md)。
OCRの式・量化子・添字が疑わしければ原画像で確認する。原著、原画像、抜粋入り固定入力は
ローカル専用Gitを含む**すべてのGitからignoreし、登録しない**。
新規原著は `local/original/`、既存inbox等はそのまま参照できる。移動・複製を自動で行わない。

## 配置・出力・受渡し

- [保存境界](references/storage.md)と[配置](references/layout.md)は共通規則への互換入口。
  新規教材は `local/books/<slug>/`、Gitなしを既定とする。既存materials Gitを移行しない。
- 組版は `scripts/book_materials.py`。新規は `--kind books`、既存materialsコースは従来指定を保つ。
  通常のlabo-buildへ教材rootを渡さない。PDF・SyncTeXの組と索引・参照を実際に確認する。
- 正本・進捗・共通キャッシュ・公式出力は本文担当一人が所有し、数学／出力確認は
  [共通契約](references/production-handoff.md)に従って固定版と専用結果領域を渡す。
  別エージェントが使えなければ自己点検を進め、独立確認未実施の正確な範囲を残す。
- [Leanの局所検査](references/lean-checks.md)は必要な式・補題に選択的に用い、教材全体の
  形式化を必須にしない。[ローカル案内](references/layout.md#workspace-からの案内)から
  正本・PDF・最新進捗へ辿れる状態を保つ。レイアウト表示だけなら変更しない。

長い教材の制作・確認を統括と worker で回すときは[消費予算](references/token-budget.md)に従い、
packet（[make_packet.py](scripts/make_packet.py)）と原著の文字キャッシュ（[source_text_cache.py](scripts/source_text_cache.py)）を使う。

指示書に固定のモデル名・推論設定を埋め込まず、実際のホスト機能に従う。
Luna/Haikuの担当境界は[役割](../research-router/references/editing-capability.md)を参照。
汎用手順の改善だけを[labo-self-improve](../labo-self-improve/SKILL.md)へ返し、実教材をスキルGitへ入れない。
