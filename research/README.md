---
doc_id: research-index
title: "Integral Prism リサーチ・インデックス"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
owner: artakartlight@gmail.com
project: integral-prism
doc_type: index
language: ja
tags: [index, survey, deep-research, agent, investment-research]
---

# Integral Prism / リサーチ・インデックス

仮称 **Integral Prism（インテグラル・プリズム）** — PE / ファンドの投資プロフェッショナル向け
「実益の大きいリサーチシステム」を設計するための、前段サーベイ一式。

> 本フォルダの目的は **アーキテクチャを決めることではない**。
> アーキテクチャ議論に入る前に、(a) 競合の実像、(b) 学術研究の到達点と未解決点、(c) 投資実務側の制約 を、
> 根拠つきで棚卸しすることにある。

**最初に読む** → [method-and-scope.md](method-and-scope.md)（調査方法・確度スケール・限界）
**議論する** → [notes/discussion-agenda.md](notes/discussion-agenda.md)（未決の論点 D1–D10）

---

## 1. 競合 — `topics/01-competitors/`

| ファイル | 内容 |
|---|---|
| [sakana-marlin.md](topics/01-competitors/sakana-marlin.md) | **Sakana Marlin** の製品事実・推定アーキテクチャ・弱点仮説 W1–W5・戦略評価 |
| [sakana-ab-mcts-treequest.md](topics/01-competitors/sakana-ab-mcts-treequest.md) | **AB-MCTS / TreeQuest** — 適応分岐木探索とマルチモデル集合知 |
| [sakana-ai-scientist.md](topics/01-competitors/sakana-ai-scientist.md) | **The AI Scientist v1/v2** — 研究プロセス自動化の骨格 |
| [sakana-evolution-and-rsi.md](topics/01-competitors/sakana-evolution-and-rsi.md) | Model Merge / ShinkaEvolve / ALE-Agent / **Digital Red Queen** / RSI Lab |
| [sakana-edinet-bench.md](topics/01-competitors/sakana-edinet-bench.md) | **EDINET-Bench** — 日本語金融ベンチという伏兵 |
| [google-gemini-deep-research.md](topics/01-competitors/google-gemini-deep-research.md) | **Gemini Deep Research** — 単価・非同期基盤・計画承認 |
| [google-ai-coscientist.md](topics/01-competitors/google-ai-coscientist.md) | **AI co-scientist** — Elo トーナメントという報酬設計 |
| [openai-deep-research.md](topics/01-competitors/openai-deep-research.md) | **OpenAI DR** — end-to-end RL 路線と、IP が採らない理由 |
| [anthropic-research-system.md](topics/01-competitors/anthropic-research-system.md) | **Anthropic Research** — オーケストレータ/ワーカ型の実装知 |
| [tongyi-deepresearch.md](topics/01-competitors/tongyi-deepresearch.md) | **Tongyi DeepResearch** — オープンモデルの到達点と IterResearch |
| [storm-costorm.md](topics/01-competitors/storm-costorm.md) | **STORM / Co-STORM** — 多視点質問生成と談話プロトコル |
| [dr-agent-taxonomy.md](topics/01-competitors/dr-agent-taxonomy.md) | DR エージェントのタクソノミと **IP の自己位置** |
| [finance-research-platforms.md](topics/01-competitors/finance-research-platforms.md) | AlphaSense / Hebbia / Rogo / BlueFlame |

## 2. 手法 — `topics/02-methods/`

| ファイル | 内容 |
|---|---|
| [test-time-scaling-and-tree-search.md](topics/02-methods/test-time-scaling-and-tree-search.md) | 探索の系譜、予算配分、停止条件 |
| [verifier-design.md](topics/02-methods/verifier-design.md) | **生成-検証の非対称性と、検証器の特権** |
| [information-value-eig.md](topics/02-methods/information-value-eig.md) | **期待情報利得（EIG）— IP の報酬設計の背骨** |
| [rl-search-agents.md](topics/02-methods/rl-search-agents.md) | RL 探索の報酬設計（学習せずに流用する） |
| [multi-agent-orchestration.md](topics/02-methods/multi-agent-orchestration.md) | 勝てる条件、並列性の切り分け、役割の異質性 |
| [multi-agent-debate-risks.md](topics/02-methods/multi-agent-debate-risks.md) | 討論の効果と**投資判断における危険** |
| [failure-modes-mast.md](topics/02-methods/failure-modes-mast.md) | **MAST** — 失敗の 41.8% は仕様と停止条件 |
| [context-engineering.md](topics/02-methods/context-engineering.md) | context rot、圧縮、出典 ID の分離 |
| [memory-and-continual-learning.md](topics/02-methods/memory-and-continual-learning.md) | **ファンドの記憶**と、その落とし穴 |
| [retrieval-and-graphrag.md](topics/02-methods/retrieval-and-graphrag.md) | 局所検索 / 大域センスメイキングの二層、時間つき KG |
| [long-form-report-generation.md](topics/02-methods/long-form-report-generation.md) | 長文・スライド生成（view 層） |
| [human-in-the-loop.md](topics/02-methods/human-in-the-loop.md) | 自律性-対話ジレンマと **4つの介入点** |
| [model-routing-and-cascades.md](topics/02-methods/model-routing-and-cascades.md) | 品質戦略かつ原価戦略、クロスベンダ独立性 |
| [structured-analytic-techniques.md](topics/02-methods/structured-analytic-techniques.md) | **ACH / SATs — 反証を一次データ構造にする** |

## 3. 評価 — `topics/03-evaluation/`

| ファイル | 内容 |
|---|---|
| [citation-attribution.md](topics/03-evaluation/citation-attribution.md) | **「引用されているが検証されていない」問題（最重要）** |
| [llm-judge-reliability.md](topics/03-evaluation/llm-judge-reliability.md) | judge バイアスと設計制約 |
| [calibration-and-forecasting.md](topics/03-evaluation/calibration-and-forecasting.md) | **較正 — 投資プロの母語で話す** |
| [general-dr-benchmarks.md](topics/03-evaluation/general-dr-benchmarks.md) | GAIA / BrowseComp / HLE / レポート級ベンチ |
| [finance-benchmarks.md](topics/03-evaluation/finance-benchmarks.md) | FinanceBench / FinTrace / FinVerBench / IPO Finance Agent |
| [integral-prism-evaluation-design.md](topics/03-evaluation/integral-prism-evaluation-design.md) | **反実仮想 DD ほか、自製評価 A–E** |

## 4. ドメイン — `topics/04-domain/`

| ファイル | 内容 |
|---|---|
| [pe-dd-workflow.md](topics/04-domain/pe-dd-workflow.md) | PE/VC DD の工程と AI の効きどころ、採用実態 |
| [data-sources.md](topics/04-domain/data-sources.md) | 公開 / 準公開 / **プライベート**（堀） |
| [regulation-and-compliance.md](topics/04-domain/regulation-and-compliance.md) | EU AI Act、MNPI、監査証跡 |
| [vc-dd-multi-agent-research.md](topics/04-domain/vc-dd-multi-agent-research.md) | VC DD の学術先行事例（DIALECTIC ほか） |

## 5. 戦略 — `topics/05-strategy/`

| ファイル | 内容 |
|---|---|
| [commoditization-and-moat.md](topics/05-strategy/commoditization-and-moat.md) | コモディティ化の証拠と、残る堀 |
| [pricing-and-unit-economics.md](topics/05-strategy/pricing-and-unit-economics.md) | 価格の空白帯域と原価構造 |
| [competitive-map.md](topics/05-strategy/competitive-map.md) | 競争地図とリスク |

## 6. 統合 — `topics/06-synthesis/`

| ファイル | 内容 |
|---|---|
| [contribution-map.md](topics/06-synthesis/contribution-map.md) | **R1–R34: どの研究がどこに効くか** |
| [differentiation-hypotheses.md](topics/06-synthesis/differentiation-hypotheses.md) | **差別化仮説 A/B/C** |
| [design-principles.md](topics/06-synthesis/design-principles.md) | **設計原則 P1–P12** |

## 7. ノートとメタデータ

| ファイル | 内容 |
|---|---|
| [notes/discussion-agenda.md](notes/discussion-agenda.md) | **未決の議論論点 D1–D10** |
| [notes/open-questions.md](notes/open-questions.md) | 一次確認の宿題 Q1–Q12 |
| [metadata/schema.md](metadata/schema.md) | フロントマター / 参考文献のスキーマ |
| [metadata/index.json](metadata/index.json) | **全ファイルの機械可読インデックス** |
| [metadata/sources.json](metadata/sources.json) | 出典レジストリ（75件、確度・使用箇所つき） |
| [metadata/claims.json](metadata/claims.json) | 主要な事実主張（32件、根拠・再検証手順つき） |
| [metadata/taxonomy.json](metadata/taxonomy.json) | 機能層 L0–L7 / 設計軸 / 設計原則 P1–P12 |
| [metadata/glossary.md](metadata/glossary.md) | 用語集 |

---

## 現時点の一行結論

> Marlin は「**長時間 × 木探索 × マルチモデル**」で、Google DR は「**単一モデル×RL×低単価×分布**」で戦っている。
> どちらも **『出力＝レポート』を最終成果物とする設計**であり、
> 投資プロの実益（＝**意思決定の質と、後から検証できること**）に最適化されてはいない。
> Integral Prism の差別化仮説は「**レポート生成機ではなく、投資判断の反証可能な証拠構造を作る機械**」に置く。
> → [topics/06-synthesis/differentiation-hypotheses.md](topics/06-synthesis/differentiation-hypotheses.md)
