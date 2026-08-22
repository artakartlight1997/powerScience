---
doc_id: t-dr-taxonomy
title: "Deep Research エージェントのタクソノミと自己位置"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: competitors
language: ja
tags: [taxonomy, survey, deep-research, mcp, positioning]
confidence: high
primary_sources: [S-019]
related_topics: [t-sakana-marlin, t-google-gemini-dr, t-openai-dr, t-anthropic-research]
contributes_to: [positioning, architecture]
---

# DR エージェントのタクソノミと、Integral Prism の自己位置

出典: *Deep Research Agents: A Systematic Examination And Roadmap*（arXiv:2506.18096）`[S-019]`

## 1. DR エージェントの定義（同論文）

複雑な多ターンの情報探索タスクを、以下の組み合わせで解く自律システム `[S-019]`:

- 動的推論
- 適応的な**長期計画**
- **多段（multi-hop）情報検索**
- 反復的なツール利用
- **構造化された分析レポートの生成**

## 2. 分類軸

| 軸 | 分類 | 代表例 |
|---|---|---|
| **ワークフロー** | **静的**（人が設計した固定パイプライン） | STORM, GPT-Researcher |
| | **動的**（実行時に計画が変化） | OpenAI DR, Gemini DR, Marlin |
| **情報取得** | API ベース検索 | 多数 |
| | **ブラウザ操作**ベース探索 | OpenAI DR, BrowseComp 系 |
| **エージェント構成** | 単一 | OpenAI DR, Gemini DR |
| | マルチ | Anthropic Research, co-scientist |
| | 木探索（準マルチ） | Marlin |
| **ツール** | コード実行 / マルチモーダル入力 / **MCP** | — |

論文は、この分類に沿って**計画戦略とエージェント構成でアーキテクチャを整理**している `[S-019]`。

## 3. Integral Prism の自己位置

| 軸 | IP の選択 | 理由 |
|---|---|---|
| ワークフロー | **動的** | 反証は事前に列挙できない |
| 情報取得 | **API + ブラウザ + 構造化DB + 人間** | 有報 XBRL と expert network を含むため |
| エージェント構成 | **マルチ（中央集権 + 検証）** | MAST の教訓：無統制の分散は誤りを17倍増幅 `[S-029]` |
| ツール | **MCP 前提**、ただし**役割ごとにツールを絞る**（tool scoping） | 仕様の曖昧さが失敗の 41.8% `[S-029]` |
| **成果物** | **レポートではなく証拠構造**（ACH 行列＋確率） | ここだけが既存タクソノミの外にある |

**注記**: 既存タクソノミは全て「レポート生成」を終点に置いている。
IP の差別化は**タクソノミの外側**にあるので、
「Deep Research の一種です」と説明した瞬間に比較され不利になる。
→ [t-competitive-map](../05-strategy/competitive-map.md) と `notes/discussion-agenda.md` D9

## 4. 出典

- `[S-019]` arXiv:2506.18096 https://arxiv.org/abs/2506.18096
