---
doc_id: t-google-gemini-dr
title: "Gemini Deep Research — プロダクトと API（単価・非同期・計画承認）"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: competitors
language: ja
tags: [google, gemini, deep-research, api, pricing, async, planner]
confidence: medium-high
primary_sources: [S-018, S-019, S-020, S-021]
related_topics: [t-sakana-marlin, t-pricing-unit-economics, t-human-in-the-loop]
contributes_to: [differentiation, cost-model]
---

# Gemini Deep Research

**Google は「アルゴリズム」ではなく「インフラと分布と単価」で戦っている。**

## 1. アーキテクチャ（公開されている範囲）

| 要素 | 内容 | 確度 |
|---|---|---|
| ベース | Gemini（初出は 2.0 Flash Thinking、現行は Gemini 3.x 系）`[S-018][S-021]` | A |
| 計画 | **多段の調査計画を自ら立て、ユーザに提示して編集・承認させる** `[S-018]` | A |
| 制御 | **単一エージェント構成**。RL によるファインチューニングで計画・適応能力を強化 `[S-019]` | B |
| 実行基盤 | **非同期タスクマネージャ**。プランナとタスクモデル間で**共有状態**を保持し、**全体を再実行せずに部分失敗から回復** `[S-018]` | B |
| 文脈 | 100万トークン級の長文脈 ＋ **RAG アンサンブル**で継続性とフォローアップを担保 `[S-018][S-019]` | B |
| UX | 開始後はアプリを閉じてよい。完了時に通知（真の非同期）`[S-018]` | A |

**設計思想**: Sakana が「木探索でマルチモデルを束ねる」のに対し、Google は
**「単一の強いモデルを RL で鍛え、非同期インフラで安定に回す」**。

## 2. Deep Research API（2026-04-21 提供開始）

| 項目 | 内容 |
|---|---|
| モデル | `deep-research-preview-04-2026`（標準, **約 $2/task**）／ `deep-research-max-preview-04-2026`（**約 $5/task**）`[S-020]` |
| 実体 | **Gemini 3.1 Pro を標準レート**（in $2.00/1M, out $12.00/1M）で使用。**エージェント層の上乗せなし** `[S-020]` |
| 検索 | Google Search グラウンディング既定 ON。**標準 80クエリ / Max 160クエリ**、$14/1K → **1 run あたり $1.12〜$2.24** `[S-020]` |
| キャッシュ | **暗黙キャッシュが入力トークンの 50〜70% をカバー**。これがエージェントループを安価に保つ主因 `[S-020]` |
| 文脈 | ループ内の個別呼び出しは小さく始まるが、検索反復で膨張。**200Kトークン閾値**が価格に効く `[S-020]` |
| 提供形態 | **Interactions API**（`generate_content` ではない）、**非同期のみ**、**有料ティア限定** `[S-020][S-021]` |

### 単価比較（本プロジェクトの価格設計の起点）

| | 1回の実行コスト | 所要 |
|---|---|---|
| Gemini DR API（標準 / Max） | **$2 / $5**（≒ ¥300 / ¥800） | 数分〜数十分 |
| Sakana Marlin | **≒ ¥9,800**（100クレジット換算）`[S-004]` | 最大8時間 |

→ **10〜30倍の価格差**。→ [t-pricing-unit-economics](../05-strategy/pricing-and-unit-economics.md)

## 3. 原価設計上の重要な学び（IP に直輸入）

1. **検索コストが LLM コストを超えうる**（1 run で $1.12〜$2.24 が検索）`[S-020]`
   → **クエリ予算の最適配分は、品質問題であると同時に原価問題**。
   ここに [t-information-value-eig](../02-methods/information-value-eig.md) が直接効く。
2. **キャッシュが 50〜70% 効く** `[S-020]`
   → **案件内の文脈再利用設計がそのまま粗利になる**。
3. **非同期・共有状態・部分回復**は、長時間実行の必須要件。
   Marlin の8時間も同種の基盤を持つはず `C`。IP も最初からこの前提で組む。

## 4. UX 上の学び — 「計画の承認」

Gemini DR は **計画をユーザに見せて編集させてから実行する** `[S-018]`。
これは Marlin の「投げたら8時間放置」より**実務的に優れた点**であり、
IP の介入点設計の最低ラインである。
→ [t-human-in-the-loop](../02-methods/human-in-the-loop.md)

## 5. 出典

- `[S-018]` https://gemini.google/overview/deep-research/
- `[S-019]` *Deep Research Agents: A Systematic Examination And Roadmap* arXiv:2506.18096
- `[S-020]` https://tokencost.app/blog/gemini-deep-research-agent-cost
- `[S-021]` https://ai.google.dev/gemini-api/docs/deep-research
