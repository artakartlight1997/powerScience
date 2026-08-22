---
doc_id: disc-index
title: "設計ディスカッション — インデックスと進め方"
version: 0.1.0
status: open
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: discussion-index
language: ja
tags: [discussion, design, debate, practical-value]
depends_on: [research-index, cs-index]
---

# 設計ディスカッション

**目的**: 「どんな設計にすべきか」を、**実益から逆算して**詰める。

> **この討論の第一原則**
> **実益のない設計は、投資プロを困らせ、経営陣を呆れさせる。**
> したがって全ての論点は、次の問いに答えられなければ**採用しない**。
>
> 1. **月曜の朝、誰の何が変わるのか**（具体的な人と行為）
> 2. **それは何時間 / 何円の話なのか**（測れる量）
> 3. **それが無かった場合、今はどうやっているのか**（代替手段との比較）
> 4. **なぜ我々でなければならないのか**（他社/既存ツール/人手との差）

## 討論の作法 🔒

我々の製品思想は「**反証されない仮説を採る**」（ACH）である。
**その思想を、我々自身の設計に最初に適用する。**

| ルール | 内容 |
|---|---|
| **1. 両論を強く書く** | 反対側を弱く書いて勝つのは禁止（ストローマン禁止） |
| **2. 決着を明記する** | 各論点の末尾に **【決着】** か **【未決：誰が決めるか】** を必ず置く |
| **3. 反証条件を書く** | 決着した論点にも「**これが観測されたら覆る**」を書く |
| **4. 数字で語る** | 「良さそう」で決めない。時間・金額・確率で書く |
| **5. 出典と推定を分ける** | `[S-xxx]` は調査済み、`推定` は我々の判断、`要検証` は顧客に聞く |

## 読む順番

| # | ファイル | 問い |
|---|---|---|
| 00 | [00-what-is-practical-value.md](00-what-is-practical-value.md) | **そもそも「実益」とは何か**（金額と時間で定義する） |
| 01 | [01-a-week-in-the-deal.md](01-a-week-in-the-deal.md) | 投資プロは実際に何をしているのか（工程の解像度を上げる） |
| 02 | [02-devils-advocate.md](02-devils-advocate.md) | **★このプロジェクトが失敗する理由**（自社への ACH 適用） |
| 03 | [03-who-pays-and-why.md](03-who-pays-and-why.md) | 誰が、何と比較して、いくら払うのか |
| 04 | [04-product-shape.md](04-product-shape.md) | 一次商品の形（D1 の徹底討論） |
| 05 | [05-first-wedge.md](05-first-wedge.md) | 最初の楔をどこに打つか（D10） |
| 06 | [06-architecture-debates.md](06-architecture-debates.md) | **設計上の6つの対立点**（討論形式） |
| 07 | [07-what-could-embarrass-us.md](07-what-could-embarrass-us.md) | 経営陣が呆れる瞬間と、その予防 |
| 08 | [08-minimum-lovable.md](08-minimum-lovable.md) | **実益を最短で出す最小形**（具体） |
| 09 | [09-decisions-and-next.md](09-decisions-and-next.md) | 決着一覧・未決一覧・次の一手 |
| **10** | [10-deep-dive-f2-calibration.md](10-deep-dive-f2-calibration.md) | **★F2 の徹底解剖** — 較正は本当に使われないのか（拒否の5メカニズム、表示3案） |
| **11** | [11-unit-economics-model.md](11-unit-economics-model.md) | **単価と原価のモデル** — 数字で殴る（原価内訳・粗利・損益分岐・自社トルネード） |
| **12** | [12-competitive-wargame.md](12-competitive-wargame.md) | **競合ウォーゲーム** — 相手の最善手と我々の応手、2年3シナリオ |
| **13** | [13-evaluation-framework.md](13-evaluation-framework.md) | **★討論そのものの評価** — DQ 採点、決定の脆さ、選択肢の期待値、討論の穴 |
| **14** | [14-how-we-know-it-works.md](14-how-we-know-it-works.md) | **検証の設計** — 先行/遅行指標、反実仮想 DD のプロトコル、撤退トリガー |
| **15** | [15-open-problems.md](15-open-problems.md) | **未解決の難問 O1–O10**（正直に「解けていない」を並べる) |
| **16** | [16-prism-proposal-vs-sakana.md](16-prism-proposal-vs-sakana.md) | **★提案確定版** — サカナに勝る形。**W1（メモ校閲）は却下され、「着手時の作戦盤＋生きた台帳」に差し替え**（A2/A3 を更新） |

## 討論の到達点（2026-08-22）

| 項目 | 状態 |
|---|---|
| **決着** | A1–A12（全て反証条件つき） |
| **未決** | U1–U8（顧客・法務・M0 の結果待ち） |
| **未解決の難問** | O1–O10（正直に列挙。特に O1 定性主張の接地） |
| **討論の質（自己採点）** | **DQ = 4/10** — 弱点は **DQ3（顧客情報がゼロ）** と **DQ6（実行主体が未定）** |
| **脆い決定 Top3** | A9（記憶の3層・法務）／ A2（一次商品）／ A4（価格枠） |
| **最も警戒すべき競合の手** | **Hebbia / Rogo が「想定問答」を足すこと** |

> **総合評価**: 論理は整った（DQ5=8/10）が、**外の情報がゼロ（DQ3=5/10）で実行に落ちていない（DQ6=4/10）**。
> **これ以上考えても DQ は上がらない。** 顧客に会い、M0 を回す段階。

## 関連

- サーベイ本体 → [../README.md](../README.md)
- 実装戦略（何を作るか）→ [../coding-strategy/README.md](../coding-strategy/README.md)
- 未決の論点 D1–D10 → [../notes/discussion-agenda.md](../notes/discussion-agenda.md)
