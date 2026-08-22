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

## 関連

- サーベイ本体 → [../README.md](../README.md)
- 実装戦略（何を作るか）→ [../coding-strategy/README.md](../coding-strategy/README.md)
- 未決の論点 D1–D10 → [../notes/discussion-agenda.md](../notes/discussion-agenda.md)
