---
doc_id: t-information-value-eig
title: "情報価値（EIG）— 「次に何を調べるか」の理論"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [eig, bayesian-experimental-design, bed-llm, information-gain, decision-theory]
confidence: medium-high
primary_sources: [S-040, S-041, S-042]
related_topics: [t-structured-analytic-techniques, t-test-time-scaling, t-differentiation-hypotheses]
contributes_to: [core-differentiation, reward-design]
---

# 情報価値（Expected Information Gain）

**IP の探索報酬の理論的背骨。** 既存 DR の弱点は、次のクエリを**LLM の気分**で決めていること。

## 1. 理論

**期待情報利得（EIG）** = ある実験/質問の結果の周辺分布についての、
**事前分布から事後分布への KL ダイバージェンスの期待値** `[S-040]`。

平たく言えば「**この質問をしたら、どれだけ不確実性が減ると期待できるか**」。

## 2. 主要研究

| 研究 | 内容 |
|---|---|
| **BED-LLM**（arXiv:2508.21184, Apple ほか）`[S-040]` | 逐次ベイズ実験計画の枠組みで、**EIG を最大化する質問**を反復的に選ぶ。20 Questions 型タスク・多段対話で情報収集効率と回答品質が改善 |
| **ASIG / Amortised BED**（arXiv:2607.03426）`[S-041]` | BED を **LLM の重みに償却（amortise）**し、推論時最適化なしで逐次情報収集を行う。LLM を BED エージェントとして扱い、潜在ターゲットの不確実性を最大限減らす実験を反復選択 |
| **Active Task Disambiguation**（arXiv:2502.04485）`[S-042]` | 曖昧なタスクに対し、**どの明確化質問が最も情報量が高いか**を選ぶ |

## 3. IP における読み替え — decision-relevant EIG

素の EIG は「不確実性一般」を減らす。しかし投資判断では**減らすべき不確実性は限定される**。

> **投資判断は本質的に「どの不確実性が意思決定を反転させるか」の問題である。**

したがって探索の報酬は、
**「意思決定を反転させうる不確実性の削減量（decision-relevant EIG）」** に置く。

```
古典的 DR:
   質問 → 検索 → 要約 → レポート

Integral Prism:
   投資判断（Go/No-Go, 価格, 条件）
      ↓ どの前提が崩れると判断が反転するか（感度分析）
   反転しうる前提 = 高 EIG ノード
      ↓ そこにだけ探索予算と人間の時間を割く
   出力 = 「判断を支える証拠構造 ＋ 残る反証リスク ＋ 次に確認すべき3件」
```

### 実装上の分解
1. **決定境界の形式化** — 何が変われば判断が変わるか（→ 未決論点 D3）
   - 案1: 簡易バリュエーションモデルの感度分析（数値的）
   - 案2: IC チェックリストの命題化（記号的）
   - 案3: 人間が「この投資の生死を決める3つの前提」を入力（人力）
2. **各前提の現在の確率と、証拠取得後の期待変動**を見積もる
3. **取得コスト**（Web / 有償データ / 人間の時間）で割って**単位コストあたり EIG** でランキング
4. 上位から探索。EIG が閾値を下回ったら**停止**

## 4. 理論と実務が一致している（重要）

- **理論側**: EIG は「最も不確実性を減らす質問」を選ぶ
- **実務側**: ACH の**診断的証拠**は「最も仮説を切り分ける証拠」を選ぶ（→
  [t-structured-analytic-techniques](structured-analytic-techniques.md)）

**この2つはほぼ同義**。数十年前の情報分析の実務知と、最新のベイズ実験計画が同じ場所を指している。
→ **これが Integral Prism の設計の背骨**であり、
「なぜこの設計なのか」を投資プロにも技術者にも同じ言葉で説明できる根拠になる。

## 5. 副次効果 — 原価が下がる

Gemini DR の実測では、**検索コストが LLM コストを超えうる**（1 run で $1.12〜$2.24）`[S-020]`。
EIG による探索予算配分は、**品質施策であると同時に原価施策**である。
→ [t-pricing-unit-economics](../05-strategy/pricing-and-unit-economics.md)

## 6. 出典

- `[S-040]` *BED-LLM* arXiv:2508.21184 ／ https://machinelearning.apple.com/research/bed-llm
- `[S-041]` *Amortising Bayesian Experimental Design for Sequential Information Gathering* arXiv:2607.03426
- `[S-042]` *Active Task Disambiguation with LLMs* arXiv:2502.04485
