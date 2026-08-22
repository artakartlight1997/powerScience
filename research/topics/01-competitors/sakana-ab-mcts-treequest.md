---
doc_id: t-sakana-ab-mcts
title: "AB-MCTS / TreeQuest — 適応分岐木探索とマルチモデル集合知"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: competitors
language: ja
tags: [ab-mcts, treequest, mcts, thompson-sampling, multi-model, test-time-scaling]
confidence: medium-high
primary_sources: [S-008, S-009, S-010, S-011]
related_topics: [t-sakana-marlin, t-test-time-scaling, t-model-routing]
contributes_to: [architecture, search-policy]
---

# AB-MCTS / TreeQuest

- 論文: *Wider or Deeper? Scaling LLM Inference-Time Compute with Adaptive Branching Tree Search*（arXiv:2503.04412）`[S-008]`
- 実装: **TreeQuest**（SakanaAI/treequest, **Apache-2.0**）`[S-009]`
- **NeurIPS 2025 Spotlight** `[S-005]`

## 1. 解いた問題

推論時スケーリングには2系統があり、どちらも片肺だった。

| 系統 | やること | 弱点 |
|---|---|---|
| **並列反復サンプリング**（Best-of-N, Self-Consistency） | 幅を取る＝多様な回答を大量生成 | 深掘り（誤りの逐次修正）ができない |
| **逐次改良**（Reflexion, Self-Refine） | 深さを取る＝1本の回答を直し続ける | 初手が悪いと抜け出せない |

AB-MCTS は **「幅か深さか」をノードごとに動的決定**する。
既存 MCTS は行動空間が固定だが、**LLM は新しい子ノードを無限に生成できる**。
そこで「既存の子を選ぶ」と「新しい子を作る」を**同一の確率モデル上で比較可能にした**のが本質。

- 手段: **適応的分岐（adaptive branching）＋ Thompson Sampling による確率的選択** `[S-010]`
- 変種:
  - **ABMCTS-A** — ノード集約（GEN ノード）による適応分岐 `[S-010]`
  - **ABMCTS-M** — PyMC を用いた**混合モデル（階層ベイズ）** `[S-010]`

## 2. Multi-LLM AB-MCTS（集合知）

さらに **「どのモデルを呼ぶか」自体を探索の一次元に加える**。
OpenAI / Google / DeepSeek 等のフロンティアモデルを協調させ、試行錯誤させる `[S-010]`。

**成果**
- **ARC-AGI-2 で solve rate 39.2%**、単一フロンティアモデル比 **+15pt 以上** `[S-010]`
- TreeQuest 紹介では「マルチモデルチームが単体 LLM を **約30%上回る**」と報じられている `[S-011]`

## 3. Integral Prism への含意

### ✅ 採用すべきもの
- 幅／深さの**動的配分**
- **モデル選択の探索化**（品質戦略であると同時にコスト戦略。→ [t-model-routing](../02-methods/model-routing-and-cascades.md)）
- Thompson Sampling による**予算配分**という考え方

### ⚠️ そのままでは効かないもの
AB-MCTS の成果が出ているのは **ARC-AGI-2 / コード生成 = 機械検証可能な報酬がある領域**。
投資リサーチには自明な報酬がない。
**報酬設計を持ち込まないと、AB-MCTS は「もっともらしさの最大化」に堕ちる。**

→ 報酬の候補は3つ。詳細は [t-information-value-eig](../02-methods/information-value-eig.md) と
[t-google-ai-coscientist](google-ai-coscientist.md)。

1. ペアワイズ Elo（co-scientist 型）
2. **decision-relevant EIG**（意思決定を反転させうる不確実性の削減）
3. 反証カウント（ACH の非反証性）

### 予算配分の拡張（IP 固有）
AB-MCTS が配分するのは LLM 呼び出しだが、IP が配分すべき資源は4種類ある。

| 資源 | 相対コスト | 備考 |
|---|---|---|
| LLM トークン | 安 | キャッシュが効く |
| Web/DB 検索クエリ | 中〜高 | Gemini DR では 1 run の**半分以上が検索コスト**になりうる `[S-020]` |
| 有償データ（expert network / 業界レポート / 与信） | 高 | 1コールで数万〜数十万円 |
| **人間の時間** | 最高 | 「人間に何を聞くか」も探索アームとして扱うべき |

## 4. 戦略的注意 — これは堀ではない

**TreeQuest は Apache-2.0 で公開されている** `[S-009]`。
つまり AB-MCTS 自体は誰でも使える。**アルゴリズムは差別化にならない。**
→ [t-commoditization-moat](../05-strategy/commoditization-and-moat.md)

## 5. 出典

- `[S-008]` arXiv:2503.04412 https://arxiv.org/abs/2503.04412
- `[S-009]` https://github.com/SakanaAI/treequest
- `[S-010]` https://sakana.ai/ab-mcts/
- `[S-011]` https://venturebeat.com/ai/sakana-ais-treequest-deploy-multi-model-teams-that-outperform-individual-llms-by-30
