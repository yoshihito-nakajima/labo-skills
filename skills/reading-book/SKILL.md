---
name: reading-book
description: Build, integrate corrections into, and hand off long mathematical courses from books with one canonical body and local-only materials. Coordinate bounded math and output reviews while retaining production ownership. Also show the book-materials layout. Not for ordinary paper reading or a short book question.
---

# Reading Book

実作業の前に[役割と引継ぎ](../research-router/references/editing-capability.md)を確認し、今回の依頼について[相談手順](../research-router/references/consultation.md)を適用する。既に行った同じ依頼の相談は引き継いで使う。

本を主資料として、正確で自然に読める数学講義を節ごとに作り、再開する。講義本文を唯一の数学的正本とする。全訳、独立した証明部品庫、仮版と厳密版の二重執筆は通常の成果物にしない。忠実な翻訳を明示的に求められた場合は、その指定に従う。

数学的な構成、評価、計算と推論を自然な説明で置き換えない。[証明・計算の基準](../mathematical-exposition/references/mathematical-substance.md)を適用し、学部初年級の既知事項と本文の既出結果から追える証明を書く。原著の流れを生かすが、誤りや仮定の不足は修正し、変更した結果を使う後続箇所まで確認する。学部向けには[undergraduate-lecture](../undergraduate-lecture/SKILL.md)も参照する。

## 実行環境と役割

このスキルと教材の指示書・引継ぎには具体的なモデル名や固定の推論設定を指定しない。
役割は原著読解・本文制作・証明・検証の責任として記す。モデルや起動方法は各ホストの
実際の機能に任せる。[相談の代替手順](../research-router/references/consultation.md)と
[担当範囲](../research-router/references/editing-capability.md)に従い、相談役・証明役の
登録や別エージェント機能がないだけで執筆を停止しない。現在の担当が原著照合・証明補完・
本文執筆・自己点検を順に進める。独立確認ができなければ未実施と記録し、後で確認する
正確な主張と位置を残す。自己点検を独立確認と呼ばず、実際の証明上の未解決は区別する。

長大教材の並行制作・再開・訂正の統合には[制作と引継ぎの契約](references/production-handoff.md)を使う。
この担当だけが正本文、統合進捗、共通キャッシュ、公式 PDF・SyncTeX を更新する。
数学の選択的な独立確認は [reading-book-math-review](../reading-book-math-review/SKILL.md)、
索引・PDF の確認は [reading-book-output-review](../reading-book-output-review/SKILL.md) に
固定した対象版を渡す。確認担当は所見を返し、本文担当が現行正本へ統合して出力へ戻す。
担当を分けても執筆中の自己点検は続ける。依存しない制作は確認の返事を待たず進める。
時間や項目数による自動停止、定期的な許可待ち、全節への両担当の承認を追加しない。
作業をまとめる単位は停止条件ではない。中断・再開はユーザーの指示に従う。

## 開始・再開

1. [保存境界](references/storage.md)を確認する。原著は既存の入力場所に置いたまま参照できる。教材の全派生物は workspace 内の `local/` に置き、`local/materials/` だけを独立したローカル専用 Git とする。親 Git は `/local/` 全体を除外し、commit・push guard で保護する。外部 root はユーザーが選んだ場合だけ用いる。取得や移動、Git 設定変更は読書スキルのインストールだけでは実行しない。
2. [本の処理手順](references/book-workflow.md)に従い、資料の版・ページ対応、講義の学習順序、正確な主張と依存を確認する。再開時は最新の合意範囲・進捗を優先し、当該節と直接の前提だけを読む。初期の案内と現物が食い違う場合は、既存草稿を保存して現行の入口を整え、古い開始点へ戻さない。
3. 意味のまとまりで一節から数節を執筆し、書く過程ですべての数学を確認する。対象節の定義・例・定理・証明・計算・演習を読める本文にする。未解決は明示して次の節へ進む。
4. 章をまとめた参照・構成・組版確認を行い、数学的に重要な箇所は選択的な独立確認へ送る。毎定理の承認待ちは置かない。確認範囲と未確認範囲を進捗に記し、区切りでは[章・講義の完了判定](references/book-workflow.md#章講義の完了判定)を行う。
5. 講義を作成・移行したとき、または再開時に正本や出力の場所が変わったときは、[レイアウトのローカル案内](references/layout.md#workspace-からの案内)も更新する。講義一覧から本文・出力・最新進捗へ実際にたどれる状態にする。

Lean は[短時間の局所検査](references/lean-checks.md)として選択的に使える。既存環境で
気になる式・補題・証明段階を検査し、結果を本文へ戻したら一時コードは破棄できる。
短い記録は残すが、本全体の形式化や研究探索の形式証拠登録を制作の必須条件にしない。

原著の正確な位置は[reading-reference の出典規則](../reading-reference/references/source-rules.md)を使う。OCR の式・量化子・添字が疑わしければページ画像を確認する。読解用の画像・OCR・キャッシュもローカル専用に保管する。外部サービスへの新しいアップロードは別の依頼による。

教材の組版には `scripts/book_materials.py` を使う。詳細は[保存境界](references/storage.md)にある。通常の `labo-build` は親 workspace 内の writing/・reading/ 用であり、`local/materials/` や選択した外部 root をその source に渡さない。

初稿から [mathematical-navigation](../mathematical-navigation/SKILL.md) を使い、
見出し・番号・リンク・索引を整える。範囲・登録・点検の規則は同スキルを正本とする。
索引生成を実際の教材ビルドに含め、PDF の参照先・色・索引から本文への移動まで確認する。
ビルドは [共通 PDF 検査](../mathematical-navigation/references/pdf-checks.md) を使って
現行 PDF の構造を毎回全体検査する。描画と代表経路の操作は同手順で確認し、修正後は
差分と影響範囲を再確認する。組版成功、構造検査、表示・操作確認、索引の網羅性を
区別して進捗へ記録する。検査の失敗・未対応は明記し、影響のない本文制作まで止めない。

「レイアウトを見せて」には[レイアウト](references/layout.md)を表示し、対象があれば実際のパスを確認する。表示だけならファイル・Git 設定を変更しない。

スキルの改善は[labo-self-improve](../labo-self-improve/SKILL.md)で行う。共有できるのは汎用手順・コード・架空のテストだけであり、実際の本、講義、出典台帳、進捗はスキル Git に入れない。PR や送信は別の依頼に従う。
