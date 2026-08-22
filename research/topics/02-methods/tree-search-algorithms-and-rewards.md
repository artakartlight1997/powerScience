---
doc_id: t-tree-search-algorithms
title: "木探索アルゴリズムと報酬設計 — 2026年時点の詳細地図"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [tree-search, mcts, rstar, prm, verifier-guided-search, compute-optimal, beam-search, granularity]
confidence: medium-high
primary_sources: [S-099, S-100, S-101, S-102, S-107]
related_topics: [t-test-time-scaling, t-sakana-ab-mcts, t-verifier-design, t-information-value-eig]
contributes_to: [search-policy, architecture]
---

# 木探索アルゴリズムと報酬設計（2026年版）

[t-test-time-scaling](test-time-scaling-and-tree-search.md) が「予算配分としての探索」を扱うのに対し、
本ファイルは **アルゴリズムと報酬の内部構造**を詳細に見る。

## 1. 統一的な見方 — 3つの構成要素

*Unifying Tree Search Algorithm and Reward Design for LLM Reasoning: A Survey*（arXiv:2510.09988）`[S-099]`

この分野は2つの前線を持つ `[S-099]`:
- **Test-Time Scaling (TTS)** — 難問に対して**その場で**計算を投入する
- **Self-Improvement** — 探索で生成したデータで**モデルのパラメータを恒久的に改善**する

サーベイは探索アルゴリズムを**3成分に分解**する `[S-099]`:

```
探索アルゴリズム = ① Search Mechanism（探索機構: どう枝を伸ばし、どう選ぶか）
                 + ② Reward Formulation（報酬定式化: 何をスコアにするか）
                 + ③ Transition Function（遷移関数: 「一手」を何と定義するか）
```

さらに **一時的な Search Guidance（TTS 用）** と
**恒久的な Parametric Reward Modeling（自己改善用）** を形式的に区別している `[S-099]`。

> **IP にとっての読み替え**:
> - ③ 遷移関数 ＝ **「一手」を何にするか**。ここが投資 DD では自明でない。
>   候補: 「1回の検索」「1つの仮説の追加」「1つの反証課題の解決」「1つの証拠の検証」
>   → **「一手＝反証課題の解決」と定義するのが IP の設計仮説**（→ [t-differentiation-hypotheses](../06-synthesis/differentiation-hypotheses.md)）
> - ② 報酬 ＝ decision-relevant EIG（→ [t-information-value-eig](information-value-eig.md)）
> - ① 探索機構 ＝ AB-MCTS 系（→ [t-sakana-ab-mcts](../01-competitors/sakana-ab-mcts-treequest.md)）

## 2. 探索機構の系譜

### rStar / rStar-Math（Microsoft）`[S-100]`
- **rStar**: 自己対戦的な**生成-識別**プロセスに推論を分解する。
  1. 対象 SLM が **人間的な推論アクションの豊富な集合**で MCTS を拡張し、高品質な推論軌跡を構成
     （アクション例: 一手を提案する / **サブ質問を生成する** / **問題を言い換える** / サブ質問に再回答する）
  2. **同程度の能力を持つ別の SLM が識別器**として各軌跡を検証する
- **rStar-Math**: 方策 SLM が **SLM ベースの過程報酬モデル(PRM)** に導かれて MCTS で「深く考える」。
  747k 問題・数百万の合成解による**4ラウンドの自己進化**で SOTA 級へ

> **IP への転用**: 「アクション空間を人間的な推論行為で設計する」という発想。
> 投資 DD のアクション空間（案）:
> `仮説を追加` / `仮説を分割` / `反証課題を立てる` / `証拠を取得` / `証拠を検証` /
> `数値を再計算` / `矛盾を指摘` / `人間に聞く` / `確率を更新` / `打ち切る`

### MCTS-RAG `[S-100]`
MCTS と検索を統合し、**推論の途中で動的に外部知識を取りに行く**操作を追加した枠組み。
rStar の生成-識別構造の上に、検索操作を足している。

### ReST-MCTS* `[S-100]`
**過程報酬に導かれた木探索で自己学習データを作る**（探索 → 学習のループ）。

### MoSA（Mixture-of-Search-Agents）`[S-107]`
**MCTS をバックボーンにした複数 LLM の協調探索**。
各エージェントが独立に探索した推論ステップを提案・集約する。
単一エージェントおよび他のマルチエージェント手法を上回る（数学・常識推論）`[S-107]`。

→ AB-MCTS のマルチモデル版と発想は近い。**「マルチモデル×木探索」は複数の研究群が同時に到達した領域**であり、
Sakana 固有の優位ではない。

### その他 `[S-107]`
- **MCCE** — マルチ LLM の協調的**共進化**（静的なアンサンブルではなく、共有経験から成長する）
- **Evolutionary Ensemble of Agents**（arXiv:2605.09018）
- **AgenticSciML** — 構造化討論 ＋ 検索拡張された手法記憶 ＋ **アンサンブル誘導の進化的探索**（npj AI）

## 3. 計算最適な探索（どこに計算を割くか）

### 基本則 `[S-101]`
- *Scaling LLM Test-Time Compute Optimally…*（ICLR 2025 / arXiv:2408.03314）:
  **テスト時計算の最適配分は、モデルパラメータを増やすより効果的でありうる**
- **問題の難易度と予算で最適手法が変わる** `[S-101]`:
  - **ビームサーチは、難しい問題・低予算で有利**
  - **Best-of-N は、易しい問題・高予算で有利**
- *Can 1B LLM Surpass 405B LLM?*（arXiv:2502.06703）— 計算最適 TTS の再考

### 粒度という制御変数（重要）`[S-101]`
*Rethinking Optimal Verification Granularity for Compute-Efficient Test-Time Scaling*（arXiv:2505.11730）:

> **VG-Search（Verifier-Guided Search）は、「検証の粒度」パラメータによって
> ビームサーチと Best-of-N を統一する。**
> 検証頻度を調整することで、精度最大化または FLOPs 最小化に振れる。

適応的 VG-Search は `[S-101]`:
- **ビームサーチ比 +3.1%**、**Best-of-N 比 +3.6%** の精度改善
- 同時に **FLOPs を 52% 超削減**

> **IP への含意**: 「どれくらい細かく検証するか」は**設計パラメータであり、動的に変えるべき**。
> IP では検証コストが極端に非対称（原文取得は安い / 数値再計算は中 / 人間確認は最も高い）なので、
> **粒度の適応制御が原価と品質を同時に決める**。

### さらに新しい方向 `[S-101]`
- **報酬の裾（tail）を推定して探索を導く**（arXiv:2602.01485）＋ **Scaling-Law Guided (SLG) Search**:
  スケーリング則から**最も伸びしろのある中間状態**を予測して計算を割り当てる
- **DORA（Direction-Oriented Resource Allocation）**: テスト時スケーリングを**資源配分問題として定式化**

## 4. FineVerify — 検証の粒度を「サブ質問」に落とす `[S-102]`

*FineVerify: Scaling Test-Time Compute with Fine-Grained Self-Verification for Agentic Search*（arXiv:2606.00660）

**問題意識** `[S-102]`:
> エージェント検索でのテスト時スケーリングは失敗しうる。
> **正解が疎（sparse）**であり、**スコアベースの選択がモデルの較正に依存する**ため。

**手法** `[S-102]`:
```
質問 → 検証可能なサブ質問へ分解
     → サンプルした各候補を、各サブ質問に対して検証
     → 集約スコアが最も高い候補を選択
```
この per-check 構造により、**選択が単純な局所判断の集合になり、
明示的で同一の基準の下でスコアが生成される**。

**結果** `[S-102]`:
- 4つのエージェント検索ベンチ × 2モデルで、標準的なスケーリング手法を一貫して上回る
- **わずか4軌跡のサンプルで、GPT-5-mini を +8.2pt、Gemini-3-flash を平均 +5.6%**
- **解釈可能な検証トレース**を生成し、**ベンチマークの誤りの監査にも使える**

> **これは IP の検証設計そのもの。**
> 「良い/悪い」を聞かず、**検証可能なサブ質問に分解して局所判断させる**という
> 設計原則 P10（→ [t-llm-judge-reliability](../03-evaluation/llm-judge-reliability.md)）の、
> 実装済み・実証済みの形。**IP の L1 接地層は FineVerify 型で組むべき** `C`。

## 5. まとめ — IP の探索設計への落とし込み

| 構成要素 | 選択 | 根拠 |
|---|---|---|
| **遷移関数（一手）** | 「反証課題の解決」を一手とする | 投資判断の構造に合う。ACH と整合 |
| **探索機構** | AB-MCTS 系（幅/深さ/モデルの適応分岐） | `[S-008]` OSS で入手可 |
| **アクション空間** | rStar 型に、DD 固有の行為を設計 | `[S-100]` |
| **報酬** | decision-relevant EIG ＋ 反証力 ＋ 検証可能性 − コスト | `[S-040][S-043]` |
| **検証** | **FineVerify 型のサブ質問分解**、粒度は適応制御 | `[S-102][S-101]` |
| **評価の階層** | 安価な judge で足切り → 高価な検証は上位のみ（SIFT 型） | `[S-093]` |
| **難易度適応** | 難問は深さ（ビーム型）、易問は幅（BoN 型） | `[S-101]` |

## 6. 出典

- `[S-099]` *Unifying Tree Search Algorithm and Reward Design for LLM Reasoning: A Survey* arXiv:2510.09988 ／ Awesome-Search-LLM
- `[S-100]` rStar（*Mutual Reasoning Makes Smaller LLMs Stronger Problem-Solver*）／ rStar-Math arXiv:2501.04519 ／ MCTS-RAG arXiv:2503.20757 ／ ReST-MCTS* ／ DeepSearch arXiv:2509.25454
- `[S-101]` *Scaling LLM Test-Time Compute Optimally* arXiv:2408.03314（ICLR 2025）／ arXiv:2502.06703 ／ *Rethinking Optimal Verification Granularity* arXiv:2505.11730 ／ *Predicting and improving test-time scaling laws via reward tail-guided search* arXiv:2602.01485 ／ DORA
- `[S-102]` *FineVerify* arXiv:2606.00660 ／ https://github.com/XuZhao0/fineverify
- `[S-107]` *Multi-LLM Collaborative Search (MoSA)* arXiv:2502.18873 ／ MCCE arXiv:2510.06270 ／ *Evolutionary Ensemble of Agents* arXiv:2605.09018 ／ AgenticSciML (npj AI)
