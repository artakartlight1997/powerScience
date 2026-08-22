---
doc_id: t-citation-attribution
title: "出典帰属の検証 — 「引用されているが検証されていない」問題"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: evaluation
language: ja
tags: [citation, attribution, fact-check, hallucination, evaluation, ci]
confidence: high
primary_sources: [S-057]
related_topics: [t-verifier-design, t-sakana-marlin, t-ip-evaluation-design]
contributes_to: [core-differentiation, quality-gate]
---

# 出典帰属の検証

> **本サーベイ全体で最も重要な単一の発見。**
> 競合が最も弱く、投資実務が最も要求する領域。

## 1. 研究

*Cited but Not Verified: Parsing and Evaluating Source Attribution in LLM Deep Research Agents*（arXiv:2605.06635）`[S-057]`

### 手法
- **再現可能な AST パーサ**で、LLM 生成 Markdown レポートの**インライン引用を大規模抽出**
- **引用先の実際のコンテンツを取得**して、人間またはモデルの評価者が各引用を原文に照らして判定
- ループを閉じている点が新しい（従来は「引用があるか」しか見なかった）

### 3つの評価次元と実測値

| 次元 | 内容 | フロンティアモデルの実測 |
|---|---|---|
| **Link Works** | URL が到達可能か | **94% 超** |
| **Relevant Content** | 話題として整合しているか | **80% 超** |
| **Fact Check** | **引用元が実際にその主張を支持するか** | **39〜77%** ← 崩壊 |

### 決定的な発見

> **ツール呼び出しを 2 → 150 に増やすと、Fact Check 精度が
> 2つのフロンティアモデルで平均 約42% 低下する。** `[S-057]`
> — **「もっと検索すれば、もっと正確になる」は成立しない。**

- また、**オープンソースモデルの半数以上**は、
  one-shot 設定で**引用つきレポートを生成すること自体に失敗**する `[S-057]`

## 2. なぜこれが IP の存在理由になるか

1. **「もっと調べる（長時間・多ツール）」は引用の正しさを悪化させる。**
   Marlin の「8時間」は、この劣化を打ち消す仕掛けを持っていなければ**むしろ逆効果** `C`。
   → [t-sakana-marlin](../01-competitors/sakana-marlin.md) W1

2. **引用の Fact Check を機械で閉ループにすることが、そのまま差別化になる。**
   これは**学習を必要とせず、エンジニアリングで到達できる**。

3. **投資実務では 39〜77% は使い物にならない。**
   IC 資料の1文が誤引用なら、資料全体の信頼が飛ぶ。
   PE のアナリストは「AI が作った資料は結局全部裏取りが必要」と言う — それは正しい。
   **裏取りを機械化した瞬間に、価値提案が変わる。**

## 3. IP の実装（検証スタック L0-L1）

```
L0 取得層: 引用時点で原文をスナップショット保存
           { url, retrieved_at, content_hash, span_offsets, archived_body }
           → リンク切れ・改変への耐性、監査要件も同時に満たす

L1 接地層: 主張 ↔ 原文スパンの機械検証
           判定は二値に限定: 「この主張は、この原文のこのスパンに支持されるか」
           Yes / No / Partial のみ（→ t-llm-judge-reliability の設計制約）
           不合格 → 生成に差し戻し、または主張を弱める／削除
```

### 出荷ゲートとして使う
```
合格条件（案）:
  - Link Works       ≥ 99%（スナップショットがあるので原理的に100%可能）
  - Fact Check       ≥ 95%（主要主張）／ ≥ 90%（全主張）
  - ツール呼び出し150回時点でも Fact Check ≥ 90% を維持（劣化曲線の平坦性）
```

**この劣化曲線こそが、競合との比較で最も雄弁な図になる** `C`。

## 4. 最優先の実証（宿題 Q3）

**Marlin を1本走らせ、引用を全数機械検証する。**
本研究の枠組み `[S-057]` をそのまま適用すればよい。
結果は、そのまま**最初の営業資料**になる。

## 5. 出典

- `[S-057]` arXiv:2605.06635 https://arxiv.org/abs/2605.06635
- 関連: *ReportBench* arXiv:2508.15804（学術サーベイ課題での DR 評価）
