---
name: mathematical-navigation
description: Design numbering, heading colors, cross-references and comprehensive indexes in mathematical documents; audit PDF links and bookmarks with offline checks and targeted visual/viewer review. Use for navigation in lectures, textbooks, papers and reading notes; not mathematical proof review.
---

# Mathematical Navigation

数学文書で、定義・記法・結果を見つけ、参照先へ戻れるようにする。
番号、見出し・番号・リンクの色、索引の対象と登録、PDFでの到達確認を担当する。
詳細は [参照・リンク・索引の規則](references/document-navigation.md) を正本とする。
PDF の検査は [構造・描画・操作の確認手順](references/pdf-checks.md) を正本とし、
教材・読書ノートのビルドから共通の検査コードを呼ぶ。

## 適用範囲と他のスキル

- 見出しや番号の色、相互参照、索引の作成・欠落点検、PDF のリンク検査に使う。
  既存文書の一部分を直す場合も、今回の対象と文書全体の未適用範囲を区別する。
- 数学的説明と証明の内容は [mathematical-exposition](../mathematical-exposition/SKILL.md)、
  教材の制作は [reading-book](../reading-book/SKILL.md)、
  学部読者への説明は [undergraduate-lecture](../undergraduate-lecture/SKILL.md) が担当する。
- 組版は文書の既存の入口を使う。このスキルの適用だけで本文の数学、制作範囲、
  保存場所、ビルドシステム、公開先を変えない。投稿先の指定書式は尊重する。
  短い会話の説明へ文書作成や索引を持ち込まない。

## 作業の進め方

1. 文書の入口、実際の入力ファイル、著者方針、共通スタイルと索引登録元を確認する。
   [詳細規則](references/document-navigation.md) を読み、対象範囲と残件を把握する。
2. 定理環境の見出し・自動番号、式番号、Step番号、参照リンクを共通設定で整える。
   本文の内部参照は種類名も自動生成し、手書きの「補題」と自動番号を組み合わせない。
   TeX の共有連番・日本語名・既存稿の移行は[型付き参照](references/typed-references.md)に従う。
   講義・教科書では青色を基本とし、見出しの着色と実際のリンクをそれぞれ実装する。
   有効な既存ラベルを保ち、番号を自動生成し、PDF宛先の衝突を防ぐ。
3. 本文で定義した概念をすべて登録する。導入・説明する記号・記法・演算と、
   定義式・構成式・公式・評価式も網羅する水準で拾う。地の文や例の中も読み、
   本文・登録元・出力索引を突き合わせる。各項目には意味・使用範囲・導入先を持たせる。
   一つの登録元から表示番号・頁とリンクを生成する。
4. 索引生成を既存ビルドへ接続して再生成する。未定義参照、重複宛先、登録の欠落、
   日本語の配列、英語併記、実際の数式表示、改行を確認する。
   [PDF 検査](references/pdf-checks.md)で現行 PDF の内部リンクとしおりを全体検査し、
   必要な経路を登録情報と照合する。描画確認と代表経路のビューア確認は別に記録し、
   必須経路の条件を本文入口の `.navigation.json` から通常ビルドにも渡す。
   修正後は差分と影響範囲を再確認する。同じ経路の GUI クリックを毎回繰り返さない。
5. 既存の文書入口に「適用規則 → 共通設定・登録箇所 → 適用状況」のリンクを置く。
   変更箇所、全件照合した範囲、抜き取り確認の項目、実行した検査と残件を記録する。
   組版成功だけで網羅性・リンク動作・数学の正しさを確認済みとしない。

新しいテンプレートや検査コードは、実際に必要な共通処理がある場合にこのスキル内へ
追加する。共通の PDF 検査は `scripts/check_pdf.py` が担当し、ビルド側は成果物と
補助情報を渡して結果を報告する。教材固有の登録内容・期待する経路・出典・進捗は教材側に残す。
