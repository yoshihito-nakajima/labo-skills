---
name: long-run-rounds
description: Set up, restart, monitor and correct unattended long runs in which a light producer parent thread and a reviewer parent thread wake on a schedule and hand bounded units to workers — instruction documents, paste-ready restart prompts, status fingerprints, capacity stages and volume-by-volume closing. Use when designing, restarting, diagnosing or revising such runs; not for the mathematical writing or review itself.
---

# 長時間の無人ラウンド

長い教材・本の制作とレビューを、人が張り付かずに何時間・何日も回すための型。
中身の規則（採用範囲・完了判定・レビュー契約）は [reading-book](../reading-book/SKILL.md)・
[course-authoring](../course-authoring/SKILL.md) が持ち、このスキルは**回し方**を持つ。

## 三つの役

| 役 | 誰 | すること | しないこと |
|---|---|---|---|
| 指示役 | ユーザーと話すセッション | 方針を決め、指示書・貼付文・状況表示の道具を書き、ときどき様子を見て規則を直す | スレッドの代わりに worker を回すこと。本文を書くこと |
| 親 | 本文側・レビュー側の各スレッド（軽いモデル） | 状況表示を見て、表どおりに worker を一つ出し、一行記録し、定期再開で起きる | 本文・report・原著を読むこと。数学の判断。ユーザーへの質問 |
| worker | 毎回新しい文脈 | 指示書の §1・§6 を読み、一単位をして、2〜3行で返す | 単位をまたいで続けること。親の判断を代わりにすること |

親を軽くし、重い読み書きは worker に閉じ込める。親が本文を読むと、待機のたびに文脈が膨らんで容量が尽きる。

## 手順

1. **方針を決める。** ユーザーに次を確かめ、指示書の §1 に書く：自走か（スレッドはユーザーに聞かず規則で決める）、
   採るか迷ったときの既定（採る／採らない）、冊の順序（前から閉じる等）、自己完結の要否、容量の扱い。
   指示役が推奨を出してよいが、決めるのはユーザー。
2. **状況表示を用意する。** 親が見るのはこの出力だけ。必要な欄と FINGERPRINT の作り方は
   [状況表示の契約](references/status-contract.md)。容量は reading-book の
   [usage_window.py](../reading-book/scripts/usage_window.py)、レビュー被覆は
   [review_coverage.py](../reading-book/scripts/review_coverage.py) を呼ぶ。
3. **指示書を二つ書く**（本文側・レビュー側）。節の骨組み、親の表、worker への依頼文は
   [指示書の骨組み](references/instruction-doc.md)。
4. **貼付文を書く。** [貼付文の雛形](assets/paste-prompts.md) を埋める。貼付文は短く、
   指示書の path と「§0〜§5 だけ読み §2 から」を言うだけにし、規則は指示書に置く。
5. **見守る。** 様子を聞かれたら、または規則を変えた後に、次を見る：
   - 両スレッドの記録の最後の時刻。定期再開の間隔より長く空いていれば、WAIT が正当かを状況表示で確かめる。
   - 閉じる条件の数（未確認・確認後に変更・照合表の不足）が**減っているか**。減らない・増えるなら、
     規則どうしの食い違いで空回りしていないかを疑う（[失敗と規則](references/failure-patterns.md)）。
   - 成果物が決まった場所にあるか（case の置き場所違いは被覆に数えられない）。
   - 容量の段階と、窓の終わり。
6. **訂正する。** 規則を直すときは：
   - 指示書は**同じファイル名のまま**改訂し、見出しに改訂時刻、§1「経緯」に「失敗 → 規則」を一行足す。
     worker は単位ごとに §1・§6 を読み直すので、そこに置いた規則は次の単位から効く。
   - 親の手順（§3〜§5）を変えたら、**動いているスレッドに貼付文を貼り直す**。定期再開はスレッドごとのもので、
     新しいスレッドからは消せない。新しいスレッドで始めるなら、先に古いスレッドを止める（親が二人になる）。
   - 状況表示の道具に欄を足すときは、その欄を FINGERPRINT にも入れる（入れないと待機中の親が気づかない）。
   - 大きな方針の変更は、言葉で示してユーザーの同意を得てから。
7. **止める・再開する。** 止めるのはユーザーの指示だけ（「止まれ」→ 親が定期再開を消して終える）。
   上限到達・WAIT・ALL_DONE 却下では定期再開を消さない。再開は貼付文を貼る。

## 既定の規則（指示書に必ず入れる）

- 親は WAIT・正当な ALL_DONE・容量の段階による待機・実際の上限・ユーザーの停止指示以外で止まらない。
  一周や build の終わりで最終回答を出さない。
- 「完了」は、冊ごとの採用範囲の照合表が閉じたときだけ。レビュー queue が空なことは完了ではない
  （reading-book の[完了判定](../reading-book/references/book-workflow.md#章講義の完了判定)）。
- 再確認は収束させる：軽微な所見だけなら直して記録し、出し直さない
  （[容量と出し直し](../reading-book/references/capacity-window.md#spend-less-per-result)）。
- 容量の段階（余裕・節約・停止前・上限中）で仕事を変える（同上）。
- worker には model・subagent_type・effort を明示し、run_in_background は false。重い証明は排他 lock で一本だけ。
