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
長い教材では[提出範囲と出力境界](../course-authoring/references/production-handoff.md#まとまった範囲で提出する)に合わせ、
一題の追加ごとの出力確認を既定にしない。短いpacketへ切り出したことだけで短文書の毎版全頁確認へ切り替えない。

## 確認の選択

カードの本では、出力は `book render` の生成物（標準は `--standalone` か本体の `\input`）とその route の版を固定して
受け取る。所見は PDF 側の位置に加えて対応するカード id を示す。生成物の TeX は直さず、直すのはカードである。
共通の組版に起因する所見は、代表位置と影響範囲を制作・統合担当へ報告する。

- HTMLの読者版も渡す場合は [共有の読書画面](../book-harness/references/views.md#reader-facing-html) を使う。
  同版PDFとの参照先、目次、証明の開閉、選択コメントが該当するカードと版に戻ることを代表箇所で確認する。
- [カードと読者版の対応](../book-harness/references/building.md#card-content-in-the-reader-edition)に従い、適用範囲・例外・
  読者向けの注意が実際の本文に届くかを照合する。証明やつなぎに番号がなければ、節または主張のラベルとカード id を使う。
- [読者向けの見出し](../book-harness/references/building.md#reader-facing-build)に従い、表紙・節見出し・目次・PDF のしおり・
  HTML の見出しに制作単位 ID や版管理用のコードが表示されていれば、該当箇所と route のタイトルを記録する。
- 索引・番号・参照は [mathematical-navigation](../mathematical-navigation/SKILL.md)、
  検査と証拠の引継ぎはその [PDF手順](../mathematical-navigation/references/pdf-checks.md)を使う。
  その通常ビルド手順はこの担当に公式ビルドの権限を与えない。
- 本文内部参照の種類名・番号・対象環境の一致は
  [型付き参照](../mathematical-navigation/references/typed-references.md)も確認する。
  表示された種類名・番号、リンクの色、見出し・番号の色、到達先をそれぞれ確認する。
- 対象範囲の本文、定義・記法・式の登録元、生成索引、導入先を突き合わせる。
  本文起点の意味上の網羅性と、既存リンクの構造的な正常性を区別する。
  一つの定義で構造・追加性質・関連概念を複数導入した場合も、各概念の読みから引ける見出し／別名と導入先を確認する。
  分冊では本文と後置登録行の切出し先を照合し、正本全体での登録を対象冊の登録と取り違えない。
  単なる成分変数の一律索引化は求めず、構造の数学的な定義充足は数学確認へ返す。
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
共通契約で認めた新規の排他受付記録を置けるが、既存の受付記録は変更しない。
検査コマンドにはレポート・描画先を明示し、共通キャッシュの既定パスを使わない。
共有のビルド、期待経路生成、正本修正、公式 PDF・SyncTeX の上書きを行わない。
入力不足・版の不一致・古い期待経路は具体的に本文担当へ返す。影響しない確認は続ける。

所見は共通契約の形式で、対象版、本文ラベル、物理頁と必要なら印刷頁、
索引項目または経路、問題と修正案、影響先、再確認箇所を示す。
カードの本では route の版、使用した共通設定の版、PDF のハッシュを残し、再生成後の確認を対応する版へ結び付ける。
組版・描画・操作の未確認と、実際に発見した欠陥を分ける。数学の疑いは位置と理由を
本文担当へ戻し、この確認だけで証明の正しさを認定しない。
正本・出力への反映は本文担当が行う。後続版には、引き継げる証拠と再確認が必要な範囲を返す。


For a chaptered card route, compare the planned hierarchy with the generated PDF contents, bookmarks and
the HTML navigation. Test representative cross-references and index links across chapter boundaries.
Use `python3 .agents/skills/reading-book-output-review/scripts/check_reader_outline.py --root local/materials/book --route ROUTE --pdf FILE --html FILE --toc-pages FIRST LAST`. Pass the inclusive physical pages of the printed contents. The checker compares their chapter and section numbers, PDF bookmarks, HTML headings and HTML anchors against the route. It uses `pdftotext` from Poppler and `mutool` from MuPDF. Inspect the printed titles, representative destinations and index links. When PDF text extraction is unreliable, record the printed pages checked visually.
See [card build and navigation checks](../book-harness/references/building.md#reader-facing-build).


## カード本の式・索引・番号一覧

`typed_navigation: true` を使うカード本では同じ版の出力を照合する。F01/F02 形式では、同じビルドディレクトリに対して
`python3 .agents/skills/reading-book-output-review/scripts/check_reader_references.py --build DIR`
を実行する（`pypdf` が必要）。aux の型、PDF の実際の索引・番号一覧ページにあるリンク、
HTML のアンカーと表示番号を照合する。数式索引では式への着地を確認する。
代表操作では本文の式参照と、折りたたまれた証明または解答への索引リンクを確認する。
