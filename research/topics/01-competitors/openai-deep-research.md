---
doc_id: t-openai-dr
title: "OpenAI Deep Research — end-to-end RL で探索をモデル内部化する路線"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: competitors
language: ja
tags: [openai, deep-research, rl, single-agent, browsing]
confidence: medium-high
primary_sources: [S-026, S-027]
related_topics: [t-rl-search-agents, t-google-gemini-dr]
contributes_to: [architecture-choice, strategy]
---

# OpenAI Deep Research

## 1. 事実

- **単一エージェント**構成。Web ブラウジングとデータ分析に最適化した **o3 系モデル** `[S-026]`
- **end-to-end 強化学習**で訓練：実タスク（ブラウザ＋Python）における
  多段軌跡の**計画・実行・バックトラック**を学習 `[S-026][S-027]`
- 中間ステップの人手監督なしに、**探索戦略そのものをモデル内部に獲得**させた `[S-026]`
- 実行時はブラウザツールと Python ツールを持ち、マルチモーダル情報取得・データ分析・可視化まで行う `[S-026]`

## 2. 業界の二大路線と、IP の第三の道

| 路線 | 代表 | 探索をどこに置くか | 必要資源 |
|---|---|---|---|
| **モデル内部化** | OpenAI DR, Gemini DR | RL でモデルに焼き込む | **大規模学習資源** |
| **外部アルゴリズム** | Sakana Marlin (AB-MCTS) | 探索木として外に出す | 探索エンジニアリング |
| **（IP の想定）明示的な証拠構造** | — | **探索対象を「証拠と反証」として外部データ構造化** | ドメイン設計＋検証基盤 |

**なぜ IP が第三の道を取るべきか**

1. モデルを学習させる資源を持たないし、持つべきでもない（**モデルはコモディティ化する** `[S-088]`）
2. 外部アルゴリズムだけでは Marlin と同じ土俵になり、しかも AB-MCTS は OSS `[S-009]`
3. **証拠構造を外部化すると、監査可能性・人間の介入・記憶の蓄積が同時に手に入る**
   → [t-design-principles](../06-synthesis/design-principles.md)

## 3. 学ぶべき点

- **バックトラックの学習**：探索は「戻れること」が本質。IP でも「否定された枝を明示的に保持する」設計が要る
  （ACH では反証された仮説も行列に残す。→ [t-structured-analytic-techniques](../02-methods/structured-analytic-techniques.md)）
- **ツールは少数精鋭**（ブラウザ＋Python）。ツールを増やすほど良いわけではない
  （MAST の「仕様の曖昧さ」失敗と整合 `[S-029]`）

## 4. 出典

- `[S-026]` https://openai.com/index/introducing-deep-research/
- `[S-027]` https://sequoiacap.com/podcast/training-data-deep-research/
