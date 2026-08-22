---
doc_id: metadata-glossary
title: "用語集"
version: 0.1.0
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: glossary
language: ja
---

# 用語集

## 探索・推論

| 用語 | 意味 | 関連 |
|---|---|---|
| **推論時スケーリング** (inference-time scaling) | 学習ではなく、推論時の計算量を増やして性能を上げる手法群 | 05 |
| **AB-MCTS** | Adaptive Branching MCTS。ノードごとに「幅（新候補生成）／深さ（既存改良）」を Thompson Sampling で選ぶ | 02, 05 |
| **Thompson Sampling** | 事後分布からサンプリングして腕を選ぶバンディット手法。探索と活用のバランスを確率的に取る | 05 |
| **Best-of-N / Self-Consistency** | N 個生成して選ぶ／多数決を取る。強力なベースライン | 05 |
| **PRM / ORM** | 過程報酬モデル／結果報酬モデル。前者は推論ステップ単位で採点 | 05 |
| **生成-検証の非対称性** | 解くより検証する方が容易という性質。検証側にツールを与えると差が広がる | 05 |
| **EIG（期待情報利得）** | ある質問/実験を行ったときの、事前→事後の KL ダイバージェンス期待値。「次に何を調べるか」の理論的基準 | 05, 11 |
| **BED** | Bayesian Experimental Design。EIG 最大化で実験を選ぶ枠組み | 05 |

## 検証・分析

| 用語 | 意味 | 関連 |
|---|---|---|
| **Attribution / 出典帰属** | 各主張がどの原文に支持されるかの対応づけ | 07 |
| **Fact Check（引用の）** | 引用先の原文が本当にその主張を支持しているかの検証。現状 39-77% | 07 |
| **LLM-as-a-Judge** | LLM に評価させる手法。位置・冗長・権威バイアスと非決定性を持つ | 07 |
| **較正 (calibration)** | 提示確率と実際の的中率の一致度 | 07 |
| **Brier スコア** | 確率予測の二乗誤差。小さいほど良い | 07 |
| **ECE** | Expected Calibration Error。較正のずれの指標 | 07 |
| **ACH** | Analysis of Competing Hypotheses。競合仮説を列挙し、**最も反証されていない**ものを採る技法（Heuer, CIA） | 07, 11 |
| **診断的証拠** | 複数の仮説を切り分ける力のある証拠。EIG の実務的言い換え | 07, 11 |
| **SATs** | Structured Analytic Techniques。情報分析のバイアス対策の型 | 07 |
| **mirror-imaging** | 自分の文化・前提を相手に投影する分析バイアス | 07 |
| **premortem** | 「この投資は失敗した。なぜか」を先に考える技法 | 07 |

## エージェント・文脈

| 用語 | 意味 | 関連 |
|---|---|---|
| **Deep Research (DR)** | 自律的に多段検索・推論し、引用つき長文レポートを出すエージェント類型 | 03, 04 |
| **Ultra Deep Research** | Sakana が Marlin に付した呼称。実行時間（最大8時間）を強調 | 01 |
| **オーケストレータ-ワーカ** | リード agent がサブ agent に分配する構成（Anthropic Research） | 04 |
| **MAST** | Multi-Agent System Failure Taxonomy。14 失敗モード／3 カテゴリ | 04 |
| **context rot** | 文脈が長くなるほど推論品質が落ちる現象 | 06 |
| **compaction** | 履歴を要約して圧縮すること | 06 |
| **IterResearch / Heavy Mode** | 毎ラウンド作業文脈を再構成する長期タスク戦略（Tongyi） | 04, 06 |
| **GraphRAG** | KG を構築しコミュニティ要約でグローバルなセンスメイキングを行う RAG | 06 |
| **HippoRAG** | Personalized PageRank で知識統合する RAG | 06 |
| **ケースベース記憶 (CBL)** | 各実行を「ケース」として蓄積し再利用する | 06, 11 |
| **MCP** | Model Context Protocol。ツール接続の標準 | 04 |

## 投資実務

| 用語 | 意味 |
|---|---|
| **DD** | Due Diligence。買収前調査（財務/商業/法務/人事/IT/ESG） |
| **QoE** | Quality of Earnings。利益の質の検証 |
| **IC** | Investment Committee。投資委員会 |
| **CIM** | Confidential Information Memorandum。売却案件の説明資料 |
| **VDR** | Virtual Data Room |
| **PMI** | Post-Merger Integration |
| **thesis tracking** | 投資仮説が成立し続けているかの継続監視 |
| **MNPI** | Material Non-Public Information。重要な未公開情報 |
| **Chinese Wall** | 情報障壁。部門間の情報遮断 |
| **point-in-time** | ある時点で入手可能だった情報のみを再現すること（リーク防止） |
| **EDINET / TDnet** | 日本の開示システム（有報等／適時開示） |
| **XBRL** | 財務データのタグ付き標準形式 |

## 本プロジェクト固有

| 用語 | 意味 |
|---|---|
| **Integral Prism (IP)** | 本システムの仮称。Prism=案件を複数仮説へ分光、Integral=意思決定へ統合 |
| **decision-relevant EIG** | 「意思決定を反転させうる不確実性」の削減量。IP の探索報酬の中心概念 |
| **証拠構造** | 仮説×証拠の行列＋確率＋残存リスク。IP の一次成果物 |
| **反証エンジン** | 投資仮説を殺しうる事実を探すことを目的関数にした探索系 |
| **介入点** | 人間が割り込める設計上の4地点（仮説承認／反証優先度／一次情報投入／確度上書き） |
