---
doc_id: t-multi-agent-debate
title: "マルチエージェント討論 — 効果と、投資判断における危険"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [debate, adversarial, persuasion, consensus, red-team]
confidence: medium-high
primary_sources: [S-045, S-046, S-063]
related_topics: [t-google-ai-coscientist, t-structured-analytic-techniques, t-llm-judge-reliability]
contributes_to: [architecture-constraints, red-team-design]
---

# マルチエージェント討論

## 1. 肯定的な証拠

- 個別討論の精度が **21設定中19で単体ベースラインを上回り、平均 +7.05pt** `[S-045]`
- 複数インスタンスが互いの推論を批判することで、**幻覚が減り事実精度が上がる** `[S-045]`
- GSM8K、multihopQA、factualQA など推論重視タスクで改善が確認されている `[S-045]`
- 改善が最大になる条件 `[S-045]`:
  1. **エージェントが多様**であること
  2. 批評が**明示的なステップや事実に接地**していること
  3. **判定者が検証可能な推論を報酬とし、根拠なき主張を罰する**こと

## 2. 否定的な証拠（こちらが重要）

- **戦略的に設計された敵対エージェント1体**で、
  **集団の精度が 10〜40% 低下**し、**誤答への合意が 30%超増加**する `[S-046]`
  （一貫し、自信に満ち、誤導的な議論が集団を動かす）
- 討論は、ハイパーパラメータを詰めない限り
  **self-consistency や Medprompt に確実には勝たない** `[S-045]`

## 3. 投資判断における含意（致命的）

> **設計原則 P7: 討論を「合意形成」に使ってはならない。**
> **討論は反証（disconfirmation）を生産するために使い、結論は証拠の集約規則で決める。**

理由:
- 説得力の高いエージェントが勝つ仕組み ＝ **もっともらしいストーリーに賭ける**仕組み
- 投資における典型的な失敗は、まさに「魅力的な物語への過信」
- LLM judge は冗長性・権威・自信のシグナルに引っ張られる `[S-058][S-059]`

## 4. IP での討論の使い方

| 使い方 | 可否 | 理由 |
|---|---|---|
| 仮説の優劣を討論で決める | ✗ | 説得力バイアス |
| 討論の合意を結論にする | ✗ | 同上 |
| **討論で反証候補を列挙する** | ◎ | 生産的。出力は「主張」ではなく「検証すべき課題」 |
| **討論の各主張を検証タスクに変換する** | ◎ | 討論 → 検証可能な問い → 機械検証 |
| **ペアワイズ比較で「診断性」を問う** | ○ | 「どちらが判断を切り分けるか」なら比較的安全（ただしバイアス緩和は必須） |

## 5. 関連する構成

- **TriAdReview**（三角敵対レビュー）`[S-063]`: 生成 / 批判 / 裁定を分離するアーキテクチャ
- **Elenchus**（prover-skeptic 対話から知識ベースを生成）`[S-063]`:
  **討論の副産物を知識資産にする**発想。IP のケースベース記憶と接続できる
- **Digital Red Queen**（→ [t-sakana-evolution-rsi](../01-competitors/sakana-evolution-and-rsi.md)）:
  反証役を世代的に強化する

## 6. 出典

- `[S-045]` GroupDebate arXiv:2409.14051 ／ 適応的異種混合討論（JKSU 2025）ほかメタ評価
- `[S-046]` *When collaboration fails: persuasion driven adversarial influence in multi agent LLM debate*, Scientific Reports (2026) https://www.nature.com/articles/s41598-026-42705-7
- `[S-063]` *TriAdReview* arXiv:2606.15074 ／ *Elenchus* arXiv:2603.06974
