---
doc_id: t-sakana-ai-scientist
title: "The AI Scientist v1/v2 — 研究プロセス自動化の骨格"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: competitors
language: ja
tags: [sakana, ai-scientist, agentic-tree-search, workflow, nature]
confidence: medium-high
primary_sources: [S-007, S-012]
related_topics: [t-sakana-marlin, t-sakana-ab-mcts, t-long-form-report]
contributes_to: [architecture, workflow]
---

# The AI Scientist（v1 / v2）

Marlin の**ワークフロー側の親**。AB-MCTS が「探索」なら、こちらは「研究の型」を与えている。

## 1. 何をするシステムか

- **v1**（2024）: アイデア生成 → 実験実行 → 論文執筆 → **査読（自己レビュー）** までの完全自動化 `[S-012]`
- **v2**（2025）: *Workshop-Level Automated Scientific Discovery via **Agentic Tree Search***（arXiv:2504.08066）`[S-012]`
  - v1 の弱点（テンプレート依存・人手のコード雛形依存）を、**エージェント的木探索**と実験マネージャで置換
  - 生成した論文を実際の学術会場に投稿する実証まで行った
- **2026-03-26 に Nature 掲載** `[S-007]`

## 2. Marlin との関係

Marlin は Sakana 自身が「AB-MCTS と AI Scientist の**直接的な製品化**」と説明している `[S-005][S-006]`。
したがって Marlin の内部ループは、おおむね次の科学的手続きの写像だと推定できる `C`。

```
仮説生成 → 情報収集/実験 → 結果の統合 → 自己レビュー → 執筆
   ↑                                            │
   └────────── 改善ループ（木探索で分岐管理）──────┘
```

## 3. Integral Prism への含意

### ✅ 学ぶべき点
- **「研究の型」を明示的にコード化した**こと自体が強い。エージェントに自由に考えさせるより、型を与えた方が安定する。
- **自己レビュー工程を独立させている**こと（生成と評価の分離）。

### ⚠️ 決定的な差
Marlin が移植したのは **科学の型**であって、**投資意思決定の型ではない** `C`。

| 科学の型 | 投資意思決定の型 |
|---|---|
| 新規性のある仮説を立てる | **既存の投資仮説を殺しにいく** |
| 実験で支持を得る | **反証されないことを確認する** |
| 論文として記述する | **価格・条件・Go/No-Go に落とす** |
| 査読を通す | **IC の詰問に耐える** |
| 再現性が価値 | **時点再現性（point-in-time）が価値** |

→ ここが Integral Prism の設計の出発点。
詳細は [t-structured-analytic-techniques](../02-methods/structured-analytic-techniques.md) と
[t-differentiation-hypotheses](../06-synthesis/differentiation-hypotheses.md)。

## 4. 出典

- `[S-007]` https://sakana.ai/rsi-lab/
- `[S-012]` arXiv:2504.08066 https://arxiv.org/pdf/2504.08066
