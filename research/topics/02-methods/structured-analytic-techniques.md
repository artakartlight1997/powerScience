---
doc_id: t-structured-analytic-techniques
title: "構造化分析技法（SATs / ACH）— 反証を一次データ構造にする"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [ach, sats, heuer, intelligence-analysis, bias, premortem, red-team]
confidence: high
primary_sources: [S-061, S-062]
related_topics: [t-information-value-eig, t-multi-agent-debate, t-differentiation-hypotheses]
contributes_to: [core-differentiation, data-structure]
---

# 構造化分析技法（SATs）と競合仮説分析（ACH）

**情報コミュニティが数十年かけて磨いたバイアス対策の型。IP の一次データ構造の出所。**

## 1. ACH（Analysis of Competing Hypotheses）

- **Richards J. Heuer Jr.** が CIA で 1970-80年代に開発し、
  *Psychology of Intelligence Analysis*（1999）で定式化 `[S-061][S-062]`

### 手順

```
1. 競合する仮説を網羅的に列挙する（最初に一つに決めない）
2. 証拠を集め、各証拠が「どの仮説を支持し、どの仮説を反証するか」の行列を作る
3. 診断的でない証拠（全仮説と整合する証拠）を除外する
4. 最も反証されていない仮説を採る（支持証拠が多い仮説ではない）
5. 結論の頑健性を、どの証拠が覆れば結論が変わるかで評価する
```

### 直観分析との違い `[S-061]`
- **直観**: 最も可能性が高そうな説明を選び、それを支持する証拠を集める（＝確証バイアス）
- **ACH**: **仮説空間の全体から始め、証拠が最も診断的に反証するものを排除していく**

### ACH 行列（IP の一次データ構造）

| 証拠 \ 仮説 | H1: 構造的成長 | H2: 一時的特需 | H3: 会計上の見せかけ | H4: チャネル依存の脆弱性 |
|---|---|---|---|---|
| E1: 3年 CAGR 34% | + | + | + | + | ← **診断的でない（除外）** |
| E2: 上位2顧客で売上68% | 0 | 0 | 0 | **++** |
| E3: 売掛回転が業界比2倍 | − | 0 | **++** | 0 |
| E4: 競合も同時期に成長 | − | **++** | 0 | 0 |

## 2. その他の SATs `[S-061]`

| 技法 | 内容 | IP での自動化可能性 |
|---|---|---|
| **Key Assumptions Check** | 暗黙の前提を洗い出す | ◎ 候補生成は LLM 向き |
| **Red Team / Devil's Advocacy** | 対立する立場から攻める | ◎（→ [t-multi-agent-debate](multi-agent-debate-risks.md)） |
| **Premortem** | 「失敗した。なぜか」を先に考える | ◎ |
| **年表構築（Chronologies）** | 生テキストから時系列を作る | ◎ 機械的 |
| **What-If Analysis** | 低確率高影響の分岐 | ○ |

## 3. LLM で自動化する際の致命的な落とし穴（必読）

> LLM が生成する「対立仮説」は**訓練分布からサンプリングされる**。
> つまり **その論点の主流的コンセンサスを反映する**。
> 結果、**本当に非主流な仮説は出てこない**。
> **バイアス緩和ステップを自動化すると、バイアスの自動化になる**。
> 特に **mirror-imaging**（自文化投影）は、英語中心コーパスで悪化する。 `[S-061]`

### IP の対策（設計原則 P3）
仮説の多様性は **LLM に任せない**。三つの供給源を持つ。

1. **実務由来の型**（ロールアップ失敗、チャネル依存、キーマンリスク、会計方針変更、
   規制反転、価格転嫁不能、サプライヤー集中、PMI 文化衝突 …）
2. **過去案件のケースベース**（→ [t-memory-continual-learning](memory-and-continual-learning.md)）
3. **人間の投入**（介入点 I1 → [t-human-in-the-loop](human-in-the-loop.md)）

## 4. 理論との一致（IP 設計の背骨）

**ACH の「診断的証拠」 ≒ ベイズ実験計画の「期待情報利得（EIG）」**。

| ACH（実務・1970s） | BED / EIG（理論・2020s） |
|---|---|
| 診断的な証拠を優先する | 期待情報利得の高い実験を選ぶ |
| 仮説を切り分ける力 | 事後分布の不確実性削減 |
| 反証されない仮説を採る | 尤度による事後の集中 |

数十年前の情報分析の実務知と、最新のベイズ実験計画が**同じ場所を指している**。
→ [t-information-value-eig](information-value-eig.md)
→ [t-differentiation-hypotheses](../06-synthesis/differentiation-hypotheses.md)

## 5. IP における実装方針

1. **ACH 行列をシステムの一次データ構造にする**（レポートではなく行列が成果物）
2. 行列のセルは **証拠 ID と診断性スコア**を持つ
3. **反証されて捨てた仮説を捨てない**（行列に残す）— それが監査証跡であり、次案件の資産
4. 「診断的でない証拠」を明示的にマークする（＝**調べても無駄だった探索の記録**）

## 6. 出典

- `[S-061]` Structured Analytic Techniques for LLMs https://mattdot.github.io/sats4llms/concepts/structured-analytic-techniques
- `[S-062]` Dhami et al., "The analysis of competing hypotheses in intelligence analysis", *Applied Cognitive Psychology* (2019) ／ Heuer, *Psychology of Intelligence Analysis* (1999)
