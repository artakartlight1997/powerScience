---
doc_id: t-google-ai-coscientist
title: "Google AI co-scientist — Elo トーナメントという報酬設計"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: competitors
language: ja
tags: [google, co-scientist, multi-agent, elo, tournament, hypothesis, test-time-compute]
confidence: medium-high
primary_sources: [S-022, S-023]
related_topics: [t-llm-judge-reliability, t-multi-agent-debate, t-information-value-eig]
contributes_to: [reward-design, architecture]
---

# AI co-scientist（Google DeepMind, Nature 2026）

**Gemini Deep Research より、こちらの方が IP の設計にとって重要。**
理由: **絶対的な正解が存在しない領域で、探索の報酬をどう作るか**の公知の解答だから。

## 1. 構成

```
      ┌─ Generation Agent  : 仮説を生成
      │
      ├─ Reflection Agent  : 批判・レビュー
      │
Supervisor ─ Ranking Agent : ペアワイズ比較で「討論」させ、勝敗を Elo に反映
      │
      ├─ Evolution Agent   : 上位仮説を改良・交配
      │
      ├─ Proximity Agent   : 仮説空間の重複排除・近傍構造化
      │
      └─ Meta-review Agent : 全体傾向を抽出し、次ラウンドの生成にフィードバック
```

Gemini 2.0 ベースの専門エージェント群が **generate → debate → evolve** サイクルを回す `[S-022][S-023]`。

## 2. 核心メカニズム

### (a) トーナメント ＋ Elo
- 仮説をペアワイズ比較し、**Ranking Agent が討論をシミュレートして勝者を決める** `[S-022]`
- 勝者は Elo 加点、敗者は減点。**低 Elo が高 Elo を破ると変動が大きい** `[S-022]`
- 時間とともに Elo が進化し、**高 Elo 仮説が優先的に改良・検証に回される** `[S-022]`

### (b) test-time compute スケーリング
- **計算量を増やすほど Elo が単調に上昇**することを実証 `[S-022][S-023]`
- Elo は**専門家評価による仮説品質と相関**する `[S-022]`

### (c) 重複排除とメタ学習
- **Proximity Agent** — 仮説空間の重複を潰す
- **Meta-review Agent** — 全体傾向を次ラウンドへ還流

## 3. Integral Prism への含意（大）

### ✅ 1. 「絶対報酬がない領域は、ペアワイズなら定義できる」
これは Marlin の未公開部分（報酬設計）に対する、**公知かつ強力な代替解**である。
IP でも「どちらの仮説がより診断的か」「どちらの証拠がより判断を動かすか」はペアワイズで問える。

### ⚠️ 2. ただし Elo をそのまま使うと壊れる
LLM のペアワイズ判定には **位置バイアス・冗長性バイアス・権威バイアス**が実測されている `[S-058][S-059]`。
Elo を素で回すと **「長くて自信満々な仮説」が勝つ**。
投資判断で最悪の失敗モード（もっともらしいストーリーへの賭け）そのもの。
→ [t-llm-judge-reliability](../03-evaluation/llm-judge-reliability.md) の緩和策を必ず併用する。

### ✅ 3. Proximity / Meta-review は必須部品
長時間探索では必ず「同じ結論の再発見」「同じ失敗の反復」が起きる。
- **Proximity** → 仮説の重複排除（IP では「同型の反証課題」の統合）
- **Meta-review** → 探索の自己改善（IP では「この案件で効いた探索パターン」の抽出）

## 4. 未確認

- Elo が judge バイアスをどう扱っているか（順序ランダム化の有無など）→ 宿題 **Q6**

## 5. 出典

- `[S-022]` *Accelerating scientific discovery with Co-Scientist*, Nature (2026) https://www.nature.com/articles/s41586-026-10644-y ／ arXiv:2502.18864
- `[S-023]` https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/
