---
doc_id: t-anthropic-research
title: "Anthropic Research — オーケストレータ/ワーカ型の実装知と限界"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: competitors
language: ja
tags: [anthropic, orchestrator-worker, subagent, citation-agent, prompting]
confidence: medium-high
primary_sources: [S-028]
related_topics: [t-failure-modes-mast, t-multi-agent-orchestration, t-citation-attribution]
contributes_to: [orchestration, architecture]
---

# Anthropic Research（Claude の Research 機能）

**マルチエージェント実装の、公開された最良の実務知。**

## 1. 構成

```
LeadResearcher（上位モデル）
  ├─ Subagent 1（軽量モデル）  ┐
  ├─ Subagent 2               ├─ 並列に検索・ツール結果評価し、発見を返す
  ├─ Subagent 3〜5            ┘
  ↓ 統合し、追加調査の要否を判断
CitationAgent  ← 出典位置の付与を担当する独立パス
```

- リード agent が計画し、**3〜5 の専門サブエージェントを並列起動**、結果を統合 `[S-028]`
- 各サブエージェントは**独立に**検索しツール結果を評価して LeadResearcher に返す `[S-028]`
- 十分な情報が集まったら、**全発見を CitationAgent に渡し、引用位置を特定させる** `[S-028]`

## 2. 実測値と教訓

| 事実 | 数値 |
|---|---|
| マルチエージェント（Opus リード＋Sonnet サブ）vs 単一 Opus（社内リサーチ評価） | **+90.2%** |
| 複雑クエリのリサーチ時間短縮 | **約90%減** |
| 最重要の制御手段 | **プロンプト設計**（言い回しの差が効率を決めた） |
| 初期の典型的失敗 | 簡単なクエリへの**過剰なサブエージェント生成**、**重複検索**、協調不全 |

### 最重要の教訓
> **architecture follows task structure**
> — タスクが**独立並列スレッドに分解できるときにだけ**、マルチエージェントは勝つ。

## 3. Integral Prism への含意

### 設計原則 P1: 並列性の切り分けを先にやる
投資リサーチのどこが本当に独立並列なのかを、アーキテクチャより先に決める。

| 独立並列にできる | 逐次でなければならない |
|---|---|
| 競合5社の財務分解 | バリュエーション前提の整合 |
| 各国規制の調査 | 仮説 → 反証 → 再仮説のループ |
| 複数の反証課題の検証 | 価格・条件への落とし込み |
| 複数チャネルの顧客インタビュー設計 | IC 向けの結論の統合 |

### 設計原則: Citation は独立工程にする
Anthropic が **CitationAgent を分離している**のは重要。
IP では**さらに踏み込み、引用を「付ける」だけでなく「原文を取得して検証する」**（→
[t-citation-attribution](../03-evaluation/citation-attribution.md)）。

### 注意
+90.2% は **社内リサーチ評価**の数値であり、投資 DD タスクでの再現は保証されない `B`。
また、マルチエージェントはトークン消費が跳ね上がる（コスト増）ことも同記事で言及されている。

## 4. 出典

- `[S-028]` https://www.anthropic.com/engineering/multi-agent-research-system
