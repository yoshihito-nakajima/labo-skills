---
name: reading-book-math-review
description: Review bounded mathematical claims and dependencies in a frozen long-course version, returning located findings and recheck scope to its reading-book producer. For book-led or topic-led textbook and course review assignments, not whole-paper refereeing or canonical-source editing.
---

# 教材の数学確認

本由来・テーマ型の教材／長いノートをともに対象とする。新規案件の担当入口は
[course-authoring の役割フォルダ](../course-authoring/references/role-folders.md)に従い、
`local/review/<case>/` に置く。既存の結果領域は移動しない。通常確認であり、
本格的な多面的査読は明示依頼された `local/hard_review/<case>/` の別任務とする。

[教材の制作・引継ぎ契約](../reading-book/references/production-handoff.md)を読み、
現在の依頼の対象版、問い、許可資料、書込先、統合担当を確認する。
担当の目的は、対象の数学的な欠陥と確認できた範囲を、本文担当が反映できる形で返すこと。
全冊の査読や、全定理の承認手続きを既定の仕事にしない。

## 対象と確認

- 基礎結果、利用先の多い結果、修正・一般化された証明、複数資料の接合を優先する。
  依頼された節・主張と必要な前提・使用先から読む。追加の影響先を見つけたら理由を示す。
- 独立した証明確認には [math-verifier](../math-verifier/SKILL.md) を適用する。
  新しい文脈で固定した主張・証明・許可資料を調べる。独立性を満たせない場合はその範囲を
  明記し、確認できた内容と分けて返す。別担当の不在だけで本文担当の制作を止めない。
- 正確な量化子・仮定・補題の適用・境界例・計算と証明の段階を確認する。
  正しさと、対象読者が追える説明の不足を区別する。未確認を誤りとして報告しない。
- 原著との対応は指定された範囲で照合し、教材の原著や抜粋を外部へ送らない。
  許可資料や前提が不足する場合は、その確認対象と必要資料を本文担当へ返す。

## 返却と権限

固定版を読み、専用の結果領域にだけ所見を書く。正本・統合進捗・共通キャッシュ・
公式出力は変更しない。証明を修復する担当へ切り替えたり、追加担当を起動したりしない。
訂正案として欠けた仮定、必要な中間段階、反例、変更すべき範囲を示せるが、
修復した証明の作成と正本への統合は本文担当へ返す。

共通契約の返却項目を使い、各所見の版・ラベル・根拠・訂正の要件・影響先・再確認箇所を示す。
変更影響の依頼では、本文差分のない使用先も前提の変更に照らして調べ、
既存の確認を引き継げる範囲と理由を返す。独立確認の読取範囲とは区別する。
修正後の再依頼は必要な主張と依存に絞り、無関係な全章を再確認しない。
所見の返却を正本への反映済みとは記さない。反映・必要な再確認・PDF更新は本文担当が追跡する。
