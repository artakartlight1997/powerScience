---
doc_id: t-draft-guided-research
title: "ドラフト誘導・選択的分岐系 — 裏取り済みの実像(木探索の次世代)"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [ttd-dr, webweaver, chain-in-tree, treeseeker, draft-guided, selective-branching]
confidence: high(裏取り済み・確度明記)
related_topics: [t-tree-search-algorithms, t-verification-claims-audit, t-sakana-ab-mcts]
contributes_to: [dominance-proof, architecture, L5]
---

# ドラフト誘導・選択的分岐系(裏取り済み)

> 裏取りの規律: LLM-judge 依存の数値は「弱い根拠」、二値検証・トークン実測は「強い根拠」、
> 別ドメインの実証は「外挿(示唆どまり)」と明示する。

## 1. TTD-DR(Google, arXiv:2507.16075)— 確度B

- **手法(確認)**: ドラフトを「ノイズあり初期版」とみなし、各ステップで検索を実行して
  ドラフト全体を改訂(draft denoising with retrieval)。各コンポーネント(計画・
  質問生成・統合)に self-evolution。**公式コードなし**(OptiLLM 再現は self-evolution
  未実装の簡易版と README 明記)
- **数値の検品**: 勝率 69.1%(LongForm Research)/ 74.5%(DeepConsult)は対 OpenAI DR の
  **LLM auto-rater によるペアワイズ判定 — 完全に judge 依存**(位置バイアス・冗長選好
  リスク)。短答ベンチ +1.7〜7.7% は正解ベースで客観的だが効果量小
- **採用判断**: 「骨子を先に置き、欠落が次の収集を導く」という**構造**は採る
  (我々の作戦盤=構造化ドラフトと同型)。**勝率数値は優越の根拠に使わない**

## 2. WebWeaver(Alibaba, arXiv:2509.13312)— 確度A(公式README一次確認)

- **手法(一次確認)**: planner = 検索×アウトライン改訂の動的ループ+citation ID 埋込。
  writer = 証拠メモリバンクから**節ごとに必要証拠だけを targeted retrieval** して執筆
- **数値の検品**: 引用精度 93.37%(DeepResearch Bench C.acc、対 Gemini 78.3 / OpenAI
  75.01)— **二値検証ベースで相対的に信頼できる**。総合スコア 50.58 vs 49.71 は
  judge 僅差でノイズ域(総合優位の主張には使わない)
- **採用判断**: 証拠メモリバンク+節別取り出しは採用(我々の証拠台帳と同型で、
  引用品質の強い根拠がある)

## 3. Chain-in-Tree(ACL 2026 Findings, arXiv:2509.25835)— 確度A(公式repo確認)

- **手法(一次確認)**: Branching Necessity 判定 — 確信的なステップは分岐せず直列、
  不確実な地点でのみ分岐。BN-DP でトークン 75-85% 削減(**トークン実測=強い根拠**)。
  BN-SC は 14 設定中 1-4 で不安定
- **重大な限界(一次確認)**: **データセットは GSM8K / Math500 のみ。Web リサーチへの
  適用は完全な外挿**。優越証明では「選択的分岐の効率は数学推論で実証、リサーチでは
  構造的類推(DD は定型多数+争点少数)」としてのみ使う

## 4. TreeSeeker(arXiv:2606.11662)— 確度B(コード未発見)

- 手法: テキスト UCB 的シグナル(価値・不確実性・リスク)+TreeMem(失敗手がかり
  付きの枝別記録)+branch-and-return。XBench-DS 56.3 / BrowseComp 47.0(短答系で客観)
- **レポート生成では未実証**。枝評価の発想(テキスト信号+失敗記録)のみ参考にする

## 5. スイープで発見した未評価の直系研究(次回深掘り)

- **AgentCPM-Report**(arXiv:2602.06540): drafting × deepening の交互 — TTD-DR 直系後続
- **ScaffoldAgent**(arXiv:2606.20122): utility 誘導のアウトライン最適化
- ParallelResearch(arXiv:2510.05145)の実タイトルは "Efficient Tree-Structured Deep
  Research with Adaptive Resource Allocation" — 主眼は効率/レイテンシであり品質ではない

## 6. 設計への正味の結論

強い根拠で立つのは: **証拠メモリ接地(WebWeaver, A)** と **選択的分岐の効率(数学で実証)**。
ドラフト誘導の「勝率」は judge 依存で弱い — ただし我々はドラフト誘導を
**品質主張の根拠ではなく制御構造**として使う(作戦盤の欠落が次の収集を導く)ため、
判断はベンチ勝率に依存しない。
