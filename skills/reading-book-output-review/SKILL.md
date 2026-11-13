---
name: reading-book-output-review
description: Review indexes, rendering and navigation in a frozen long-course PDF and its matching sources, returning bounded corrections to the reading-book producer. For book-led or topic-led textbook output review, not proof verification, canonical editing or official builds.
---

# 教材の索引・PDF確認

本由来・テーマ型の教材／長いノートをともに対象とする。新規案件の担当入口は
[course-authoring の役割フォルダ](../course-authoring/references/role-folders.md)に従い、
`local/review/<case>/` に置く。既存の結果領域は移動しない。通常確認であり、
本格的な多面的査読は明示依頼された `local/hard_review/<case>/` の別任務とする。

[教材の制作・引継ぎ契約](../reading-book/references/production-handoff.md)を読み、
対象版、確認範囲、資料の対応、専用の書込先、統合担当を確認する。
本文担当が制作を続ける間、固定した本文と出力を確認して具体的な修正箇所を返す。

## 確認の選択

- 索引・番号・参照は [mathematical-navigation](../mathematical-navigation/SKILL.md)、
  検査と証拠の引継ぎはその [PDF手順](../mathematical-navigation/references/pdf-checks.md)を使う。
  その通常ビルド手順はこの担当に公式ビルドの権限を与えない。
- 本文内部参照の種類名・番号・対象環境の一致は
  [型付き参照](../mathematical-navigation/references/typed-references.md)も確認する。
  リンクが到達しても、手書きの「命題」が実際の「定理」と異なる場合は参照表示の所見として返す。
- 対象範囲の本文、定義・記法・式の登録元、生成索引、導入先を突き合わせる。
  本文起点の意味上の網羅性と、既存リンクの構造的な正常性を区別する。
- ラベル差・登録件数・抽出語の不一致は、まず要照合候補とする。同名の式ラベルによる登録が
  なくても、定理ラベルや別名の項目が同じ内容を含む場合がある。欠落と確定する前に、
  本文と代替登録、生成索引の内容・導入先を照合し、表示に関わる疑いは必要なPDF箇所も確認する。
  入力不足で照合できなければ未確認候補として返し、機械抽出だけで重複登録や訂正を要求しない。
- 構造検査、描画確認、ビューア操作、同期を別々に記録する。対象 PDF と設定が一致する
  既存の構造検査は再利用し、新規入力・失敗・未解決の懸念がある場合に追加検査する。
  実施していない表示や操作を成功とせず、初回の未確認範囲は未確認のまま示す。
- 既存証拠と変更の影響から再確認範囲を選ぶ。同じ経路のクリックを毎回繰り返さず、
  全件クリックを新しい完了条件にしない。表示の引継ぎには共通手順の描画証拠を使う。
  改ページの影響を変更行だけで限定しない。共通設定の変更なら影響する範囲を広げる。

## 機械検査を先に

頁の目視より先に機械検査を行う。[output_check.py](scripts/output_check.py) で qpdf、ログ（未定義参照・Overfull・重複定義）、
mathematical-navigation の構造検査、前版から本文が変わった頁の一覧を一度に得て、所見は該当ソース行と照合する。
描画は変更頁のうち見出し・表・長い式を含むものから少数（目安 5 頁）を低解像度で行い、多数の頁画像を読み込まない。
長い教材では、出力確認は毎ビルドではなく数ビルドに一度、変更頁を中心にしてよい。
短い文書（一回の文脈で全体を読める）では、機械検査のあと毎版全頁を確認する。
[規模と確認の水準](../reading-book/references/token-budget.md)。
検査スクリプトの実行は軽量段階でもよいが、所見の判定と描画の確認は軽量段階で行わない（[能力の段階](../reading-book/references/token-budget.md#能力の段階と思考量)）。

## 保存と返却

固定入力を変更せず、画像・検査報告・一時ファイルは依頼専用の領域へ保存する。
検査コマンドにはレポート・描画先を明示し、共通キャッシュの既定パスを使わない。
共有のビルド、期待経路生成、正本修正、公式 PDF・SyncTeX の上書きを行わない。
入力不足・版の不一致・古い期待経路は具体的に本文担当へ返す。影響しない確認は続ける。

所見は共通契約の形式で、対象版、本文ラベル、物理頁と必要なら印刷頁、
索引項目または経路、問題と修正案、影響先、再確認箇所を示す。
組版・描画・操作の未確認と、実際に発見した欠陥を分ける。数学の疑いは位置と理由を
本文担当へ戻し、この確認だけで証明の正しさを認定しない。
正本・出力への反映は本文担当が行う。後続版には、引き継げる証拠と再確認が必要な範囲を返す。
