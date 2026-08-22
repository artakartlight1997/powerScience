---
doc_id: t-tongyi-deepresearch
title: "Tongyi DeepResearch — オープンモデルの到達点と IterResearch"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: competitors
language: ja
tags: [alibaba, open-source, iterresearch, context-management, benchmark, moe]
confidence: medium-high
primary_sources: [S-030]
related_topics: [t-context-engineering, t-commoditization-moat, t-general-dr-benchmarks]
contributes_to: [architecture, commoditization-evidence]
---

# Tongyi DeepResearch（Alibaba）

**「オープンモデルのコモディティ化」が既に現実であることの、最も強い証拠。**

## 1. 事実

- **30.5B 総パラメータ / 3.3B アクティブ**（MoE）`[S-030]`
- **完全オープンソース**：モデル・学習フレームワーク・ソリューションの全チェーンを公開 `[S-030]`
- OpenAI Deep Research と同等性能を主張する**初の完全オープンな Web エージェント** `[S-030]`

### ベンチマーク（30B で）`[S-030]`

| HLE | BrowseComp | BrowseComp-ZH | WebWalkerQA | GAIA | xbench-DeepSearch | FRAMES |
|---|---|---|---|---|---|---|
| 32.9 | 43.4 | 46.7 | 72.2 | 70.9 | 75.0 | 90.6 |

（xbench-DeepSearch-2510 では 55.0）

## 2. IterResearch / Heavy Mode — 文脈管理の到達点

**長い文脈を積み上げない。ラウンドごとにワークスペースを再構築する。** `[S-030]`

```
従来（ReAct 素の積み上げ）:
  [質問][行動1][観察1][行動2][観察2]...[行動N][観察N] → 文脈が膨張しノイズが蓄積

IterResearch（Heavy Mode）:
  ラウンド1: [質問] + [焦点化された作業空間] → 中間統合
  ラウンド2: [質問] + [再構成された作業空間（前ラウンドの統合結果のみ）] → 中間統合
  ...
  各ラウンド末に「情報収集を続けるか、統合して答えるか」を判断
```

- **ノイズ蓄積を抑える**ことが目的。test-time scaling を「多ラウンドの構造化された統合／再構成」で行う `[S-030]`
- ReAct モード（素の thought/action/observation）も併存し、用途で切り替える `[S-030]`

## 3. Integral Prism への含意

### ✅ IterResearch は直輸入すべき
文脈を「積む」のではなく「毎ラウンド再構成する」。
これは**監査可能性とも相性が良い**（各ラウンドの入力が明示的に定義される）。
→ [t-context-engineering](../02-methods/context-engineering.md)

### ✅ モデル層に価値を置く設計は禁じ手
オープン 30B が BrowseComp 43.4 を出す世界では、
**「良いモデルを使っているから良い」は製品の説明にならない**。
IP は**モデルを差し替えても壊れない構造**でなければならない。
→ [t-commoditization-moat](../05-strategy/commoditization-and-moat.md)

### ✅ 自社運用の選択肢
オープンモデルを自社ホストできる＝
**顧客データを外部 API に出さない構成**が現実的に組める（金融顧客のセキュリティ審査で効く）。
→ [t-regulation-compliance](../04-domain/regulation-and-compliance.md)

## 4. 出典

- `[S-030]` Tongyi DeepResearch 技術報告 arXiv:2510.24701 ／ https://tongyi-agent.github.io/blog/introducing-tongyi-deep-research/ ／ https://huggingface.co/Alibaba-NLP/Tongyi-DeepResearch-30B-A3B
