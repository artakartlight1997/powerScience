---
doc_id: t-memory-continual-learning
title: "記憶と継続学習 — ファンドの資産化と、その落とし穴"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [memory, continual-learning, case-based, agent-kb, experience-reuse, moat]
confidence: medium-high
primary_sources: [S-052, S-053]
related_topics: [t-context-engineering, t-commoditization-moat, t-sakana-evolution-rsi]
contributes_to: [moat, architecture]
---

# 記憶と継続学習

**事業上の堀に直結するトピック。** ただし研究は明確に警告を出している。

## 1. 研究の到達点

| 研究 | 内容 |
|---|---|
| **AgentCL**（arXiv:2606.02461）`[S-052]` | 言語エージェントの継続学習を厳密に評価する枠組み |
| **When Continual Learning Moves to Memory**（arXiv:2604.27003）`[S-052]` | **外部記憶に経験を貯めれば継続学習が解ける、わけではない**。<br>安定性-可塑性ジレンマは**検索段階に再出現**する（古い経験と新しい経験が限られた文脈を奪い合う） |
| **Agent KB**（arXiv:2507.06229）`[S-053]` | 過去ワークフローを**汎化可能な経験単位**に構造化し、タスク/ドメイン/エージェント構成をまたいで再利用 |
| **Case-Based Learning (CBL)**（arXiv:2604.12717）`[S-053]` | 実タスクの各実行を**学習可能なケース**として蓄積。<br>**固定ドメイン知識モジュール**（インタフェース仕様・制約）と経験を分離 |
| **Dynamic Cheatsheet / ExpRAG / ReMem** `[S-052]` | 戦略・スニペット・抽象を test-time に再利用 |
| **Learning How to Remember**（arXiv:2601.07470） | メタ認知的な記憶管理（構造化・転移可能な記憶） |

## 2. IP における意味 — 何を記憶するか

PE ファンドにとっての本当の資産は **「過去の案件で何を見て、何を外したか」**。

```
ケース = {
  案件の型      : 業種 / ビジネスモデル / ディール構造（ロールアップ, カーブアウト, LBO…）
  当時の仮説    : 何を信じて投資した/見送ったか
  検証した証拠  : 何を確認し、何を確認しなかったか
  結果          : 実際に何が起きたか（T+2〜3年）
  ★死因         : 外した理由 / 効いた反証 / 見落とした兆候
}
```

**効果**
1. 案件横断の **「よくある死因（failure archetype）」ライブラリ**が育つ
2. 新規案件で **「この形は 20XX年の××案件と同型。あの時の見落としは△△」** が出せる
3. **反証役が世代的に強くなる**（→ Digital Red Queen の発想 `[S-015]`）
4. **これは Marlin にも Google にも作れない** — 顧客固有データの累積であり、モデル層の資産ではない

## 3. 落とし穴（研究の警告を無視しない）

> **記憶は増やすほど検索が濁る** `[S-052]`。

対策:

| 対策 | 内容 |
|---|---|
| **選別** | 「意思決定に効いた事実」だけを残す。全ログは監査用に別置し、記憶とは分ける |
| **反証結果とセットで残す** | 「効かなかった反証」も価値がある（次回それに時間を使わない） |
| **固定知識と経験の分離** `[S-053]` | 業界の恒久的な構造 vs この案件固有の経験 |
| **時効** | 市場前提には有効期限を付ける（3年前のマルチプルは今の判断に使えない） |
| **索引は構造で引く** | ベクタ類似だけでなく、案件の型・ディール構造で引く |

## 4. 事業的含意

| 効果 | 内容 |
|---|---|
| **スイッチングコスト** | 抜けると過去の判断履歴が失われる |
| **粗利** | 同型ケースの再利用で探索コストが下がる |
| **差別化の持続** | 使うほど強くなる（モデル更新に依存しない） |

→ [t-commoditization-moat](../05-strategy/commoditization-and-moat.md)

**ただし前提**: 顧客ごとのデータ分離（MNPI / Chinese Wall）と両立させる必要がある。
横断学習をどこまで許すかは未決論点（`notes/discussion-agenda.md` D6）。
→ [t-regulation-compliance](../04-domain/regulation-and-compliance.md)

## 5. 出典

- `[S-052]` AgentCL arXiv:2606.02461 ／ When Continual Learning Moves to Memory arXiv:2604.27003 ／ Learning How to Remember arXiv:2601.07470
- `[S-053]` Agent KB arXiv:2507.06229 ／ Transferable Expertise via Real-World Case-Based Learning arXiv:2604.12717
