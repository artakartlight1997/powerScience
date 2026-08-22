---
doc_id: t-rl-search-agents
title: "RL 探索エージェント — 報酬設計の潮流（学習せずに流用する）"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [rl, search-r1, reward-design, process-reward, rubric, agentic-search]
confidence: medium-high
primary_sources: [S-043, S-044]
related_topics: [t-information-value-eig, t-verifier-design, t-openai-dr]
contributes_to: [reward-design, scoring]
---

# RL 探索エージェント

**IP は自前で RL 学習をしない。しかし「報酬の定義」は流用できる。**
学習しなくても、**推論時の探索スコア**としてそのまま使えるからだ。

## 1. 系譜

- **Search-R1 / R1-Searcher / DeepResearcher / ZeroSearch**:
  中間ステップの監督なしに、**検索と推論を同時に行う方策**を RL で獲得 `[S-043]`
- **Search-R1 / R1-Searcher は outcome-reward パラダイム**:
  ルールベース検証器が最終回答を正解と照合（**EM / トークン F1**）して採点 `[S-043]`

## 2. 報酬設計の進化

| 世代 | 報酬 | 問題 |
|---|---|---|
| 第1世代 | **outcome reward**（最終答えの EM/F1） | **軌跡レベルの信号は、個々の検索ステップを監督しない** `[S-043]` |
| 第2世代 | outcome + **タスク固有の過程ヒューリスティック**：<br>**情報利得・経路カバレッジ・検索コスト**（StepSearch, Search-P1, SIGHT, InfoFlow, TIPS）`[S-043]` | 設計が職人芸 |
| 第3世代 | **多面・多ターン報酬**：正確性に加え **明瞭性・真実性・簡潔性・効率・幻覚抑制** まで含む `[S-043]` | 重み付けが難しい |
| 補助 | **ARBOR**: 再利用可能な**ルーブリック・バッファ**によるオンライン過程報酬 `[S-044]` | — |

## 3. IP への流用（学習なしで効く）

上記の多面報酬は、**推論時のノード評価関数**としてそのまま使える。

```
Score(node) = w1·InformationGain        ← EIG（→ t-information-value-eig）
            + w2·Disconfirmation        ← 反証力（→ t-structured-analytic-techniques）
            + w3·Verifiability          ← 原文で機械検証できるか（→ t-verifier-design）
            + w4·DecisionRelevance      ← 判断を動かすか
            - w5·Cost                   ← 検索/有償データ/人間時間
```

**注意点**
- 重み `w` は**顧客とタスクで変わる**。学習ではなく**設定と較正**で扱う（ルーブリック・バッファの発想 `[S-044]`）
- 単一スコアに潰さず、**多目的のまま Pareto で提示する**選択肢もある（IC 向けには有用）

## 4. RL を「やらない」判断の根拠

| 論点 | 判断 |
|---|---|
| 学習資源 | 持たない。持つべきでもない（モデルはコモディティ化 `[S-088]`） |
| データ | 投資 DD の教師データは**極めて少なく、機密**。RL に必要な量が集まらない |
| 更新速度 | 市場と規制は変わる。**重みで調整できる方が速い** |
| 説明可能性 | 金融顧客には「なぜこの探索をしたか」の説明が要る。**明示的スコアの方が有利** |

→ ただし将来的に、**顧客固有のルーブリック学習**（どの反証が実際に効いたか）は
[t-memory-continual-learning](memory-and-continual-learning.md) の枠内で扱える。

## 5. 出典

- `[S-043]` *A Comprehensive Survey on RL-based Agentic Search* arXiv:2510.16724 ／ Search-R1 ／ R1-Searcher arXiv:2503.05592 ／ DeepResearcher arXiv:2504.03160
- `[S-044]` *ARBOR* arXiv:2606.03239 ／ *Retrieval, Reward, and Training Protocols: What Matters in Training Search Agents?* arXiv:2605.27881
