---
doc_id: t-vc-dd-multi-agent
title: "VC/スタートアップ評価のマルチエージェント研究 — 直接の先行事例"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: domain
language: ja
tags: [venture-capital, due-diligence, multi-agent, dialectic, ocr, hallucination]
confidence: medium
primary_sources: [S-090, S-091]
related_topics: [t-pe-dd-workflow, t-multi-agent-orchestration, t-verifier-design]
contributes_to: [architecture, prior-art]
---

# VC/スタートアップ評価のマルチエージェント研究

学術側にも、**投資デューデリを直接扱った先行研究**がある。IP の最も近い prior art。

## 1. A Multi-Agent Orchestration Framework for Venture Capital Due Diligence

arXiv:2605.13110（Grigorios Alexandrou, Katerina Pramatari — Athens University of Economics and Business）`[S-090]`

| 要素 | 内容 |
|---|---|
| 目的 | **VC の企業デューデリと市場分析の完全自動化** |
| 基盤 | **イベント駆動のオーケストレーション**。LLM ＋ リアルタイム Web 取得で、非構造データを構造化投資インテリジェンスへ |
| **中核の技術貢献** | **プログラム的抽出パイプライン** — 公式の財務ファイリングを**レイアウト認識 OCR** で解析し、<br>**構造的なフォールバック機構が「データが無いこと」を明示的にフラグする**（数値を捏造しない） |
| 狙い | **金融文脈での幻覚に直接対処する** |

### IP への含意（重要）
> **「データが無い」を明示的に出力する**という設計は、金融では決定的に正しい。
> LLM の既定動作は「それらしい数字を埋める」ことであり、これが DD では致命傷になる。

IP の実装要件:
1. 抽出層は **`value | NOT_FOUND | AMBIGUOUS`** の三値を返す
2. `NOT_FOUND` は**欠落として下流に伝播**し、確率計算では**不確実性として扱う**
3. **欠落そのものが探索対象になる**（EIG が高い＝取りに行く価値がある）

## 2. DIALECTIC: A Multi-Agent System for Startup Evaluation

arXiv:2603.12274 `[S-091]`

- ベンチャー評価の**反復的・論争的（argumentative）な性質**をモデル化する LLM システム
- **弁証法的推論（dialectical reasoning）**の原理に依拠し、
  複雑で非構造的な問題に対して**異なる視点の構造化された対決**を行う

### IP への含意
**「反証エンジン」という発想には既に学術的な先行例がある**（＝突飛ではない）。
一方で、DIALECTIC は**討論の構造化**に留まっており、
- 引用の機械検証（→ [t-citation-attribution](../03-evaluation/citation-attribution.md)）
- 較正（→ [t-calibration-forecasting](../03-evaluation/calibration-and-forecasting.md)）
- 記憶の蓄積（→ [t-memory-continual-learning](../02-methods/memory-and-continual-learning.md)）
までは統合していない `C`。**IP の統合が差分になる。**

## 3. 関連

- **金融文書処理のオーケストレーション比較**（arXiv:2603.22651）:
  逐次パイプライン / 並列ファンアウト+マージ / 階層 supervisor-worker / 反省的自己修正ループ を、
  コスト-精度と本番スケーリングの観点で比較 `[S-090]`
- **Orchestration Framework for Financial Agents**（arXiv:2512.02227）`[S-090]`
- **Verified Multi-Agent Orchestration: A Plan-Execute-…**（arXiv:2603.11445）`[S-090]`

## 4. 出典

- `[S-090]` *A Multi-Agent Orchestration Framework for Venture Capital Due Diligence* arXiv:2605.13110 ／ 金融文書処理のオーケストレーション比較 arXiv:2603.22651 ／ Orchestration Framework for Financial Agents arXiv:2512.02227 ／ Verified Multi-Agent Orchestration arXiv:2603.11445
- `[S-091]` *DIALECTIC: A Multi-Agent System for Startup Evaluation* arXiv:2603.12274
