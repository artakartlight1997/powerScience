---
doc_id: t-test-time-scaling
title: "推論時スケーリングと木探索 — 系譜と予算配分"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [test-time-scaling, mcts, tree-of-thoughts, best-of-n, bandit, budget]
confidence: medium-high
primary_sources: [S-008, S-022, S-045]
related_topics: [t-sakana-ab-mcts, t-verifier-design, t-information-value-eig]
contributes_to: [search-policy, architecture]
---

# 推論時スケーリングと木探索

> **このトピックの主題は一つ： 探索を回すのは簡単。何を報酬にするかが全て。**

> 📎 アルゴリズムと報酬の**内部構造の詳細**（統一タクソノミ、rStar、検証粒度、計算最適配分、FineVerify）は
> → [t-tree-search-algorithms](tree-search-algorithms-and-rewards.md)
> 自己改善（DGM / SIFT / Red Queen / AlphaEvolve / GEPA）は
> → [t-recursive-self-improvement](recursive-self-improvement.md)

## 1. 手法の系譜

| 手法 | 幅 | 深さ | 報酬 | 備考 |
|---|---|---|---|---|
| **Best-of-N / Self-Consistency** | ◎ | × | 多数決 | 単純だが強い。**多くのマルチエージェント手法はこれに勝てない** `[S-045]` |
| **Reflexion / Self-Refine** | × | ◎ | 自己批評 | 初手が悪いと抜け出せない |
| **Tree of Thoughts / LATS** | ○ | ○ | 自己評価・環境 | 行動空間が固定的 |
| **AB-MCTS** `[S-008]` | ◎ | ◎ | 外部フィードバック | **生成による分岐**を確率モデルに載せた点が新規 → [t-sakana-ab-mcts](../01-competitors/sakana-ab-mcts-treequest.md) |
| **Elo トーナメント（co-scientist）** `[S-022]` | ◎ | ○ | **ペアワイズ比較** | **絶対報酬が無い領域で機能する** → [t-google-ai-coscientist](../01-competitors/google-ai-coscientist.md) |

### 難易度と予算で最適手法が変わる `[S-101]`
- **ビームサーチは、難しい問題・低予算で有利**
- **Best-of-N は、易しい問題・高予算で有利**
- 両者は「**検証の粒度**」というパラメータで連続的に繋がる（VG-Search）。
  適応制御で **精度 +3.1〜3.6%、FLOPs −52%超** `[S-101]`
→ 詳細は [t-tree-search-algorithms](tree-search-algorithms-and-rewards.md)

### ベースラインの強さを忘れない
Best-of-N / Self-Consistency は**極めて強いベースライン**であり、
多エージェント討論はハイパーパラメータを詰めない限りこれに確実には勝たない `[S-045]`。
→ 複雑な探索構造を入れる前に、**「単純な並列サンプリング＋良い検証器」で足りないか**を必ず検証する。

## 2. 探索は本質的に「予算配分」問題

AB-MCTS の Thompson Sampling は、要するに**多腕バンディットによる計算予算配分**である。
Integral Prism では、配分すべき資源が LLM 呼び出しだけではない点が決定的に重要。

| 資源 | 相対コスト | 特性 |
|---|---|---|
| LLM トークン | 安 | キャッシュが 50〜70% 効く `[S-020]` |
| Web/DB 検索クエリ | 中〜高 | Gemini DR では **1 run の半分以上が検索コスト**になりうる `[S-020]` |
| 有償データ（expert network / 業界レポート / 与信） | 高 | 1コール数万〜数十万円 |
| **人間の時間**（アナリスト、専門家、経営者面談） | 最高 | **最も情報量が高く、最も高い** |

→ **「人間に何を聞くか」も探索アームの一つとして扱う**設計が、実益に直結する。
これは既存 DR には無い発想（既存 DR は Web 検索しか腕を持たない）。

## 3. 停止条件（MAST の教訓）

MAST では**失敗の 41.8% が仕様/設計の欠陥**で、その中に**停止条件の欠落**が含まれる `[S-029]`。
「いつ調べ終わるか」を定義しない探索系は、必ず壊れる。

停止条件の候補:
1. **EIG 閾値**: これ以上調べても判断が動かないと期待されるとき（→ [t-information-value-eig](information-value-eig.md)）
2. **予算枯渇**: 金額・時間・人的コストの上限
3. **反証の枯渇**: 新しい反証仮説が K ラウンド連続で出ないとき
4. **確度の収束**: 主要主張の確率が安定したとき

## 4. 探索を増やすと悪くなる領域がある（重要な反証）

**2つの独立した研究が、別々の領域で同じ形の劣化を報告している。**

| 研究 | 領域 | 劣化 |
|---|---|---|
| *Cited but Not Verified* `[S-057]` | Deep Research の引用 | ツール呼び出し 2 → 150 で**事実整合性 −42%** |
| *Reward Hacking in Self-Improving Code Agents* `[S-103]` | 自己改善コード最適化 | 10 → 100 ステップで**報酬ハッキング 26.4% → 57.8%** |

つまり **「探索量 = 品質」は成立しない**。むしろ**長く走らせるほど、見かけの指標が良くなり実質が悪くなる**。
探索を増やすなら、**同時に検証を強化しなければ純減する**。

→ [t-verifier-design](verifier-design.md) / [t-citation-attribution](../03-evaluation/citation-attribution.md) /
[t-reward-hacking](../03-evaluation/reward-hacking-and-proxy-gaming.md)

## 5. 出典

- `[S-008]` arXiv:2503.04412 ／ `[S-020]` Gemini DR 単価分析 ／ `[S-022]` co-scientist (Nature 2026)
- `[S-029]` MAST arXiv:2503.13657 ／ `[S-045]` Multi-Agent Debate 評価 ／ `[S-057]` *Cited but Not Verified* arXiv:2605.06635
