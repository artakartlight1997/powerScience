---
doc_id: t-failure-modes-mast
title: "マルチエージェントの失敗モード（MAST）— 設計の制約条件"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [mast, failure-modes, reliability, termination, verification]
confidence: high
primary_sources: [S-029]
related_topics: [t-multi-agent-orchestration, t-verifier-design, t-test-time-scaling]
contributes_to: [architecture-constraints, reliability]
---

# MAST — マルチエージェントはなぜ失敗するか

*Why Do Multi-Agent LLM Systems Fail?*（arXiv:2503.13657, NeurIPS 2025）`[S-029]`

**7フレームワーク・1,600超の実行トレースを注釈**し、**14の失敗モード**を3カテゴリに整理した研究。

## 1. 失敗の分布

| カテゴリ | 割合 | 中身 |
|---|---|---|
| **仕様/システム設計の欠陥** | **41.8%** | タスクの誤解釈、**役割定義の曖昧さ**、分解の失敗、役割の重複、**停止条件の欠落** |
| **エージェント間の不整合** | **36.9%** | 実行中の相互作用・協調における**情報伝達の断絶** |
| **タスク検証の失敗** | **21.3%** | 出力検証の不足、**誤りの伝播** |

## 2. 誤り増幅

- 未協調のマルチエージェントは、誤りを **最大17倍**に増幅しうる `[S-029]`
- **中央集権アーキテクチャ＋検証ボトルネック**を置くと、増幅は **約4.4倍**に抑制される `[S-029]`
- 本番環境での失敗率は **41〜86.7%** という報告もある `[S-029]`

## 3. IP への設計制約（そのまま採用）

> **設計原則 P2: 停止条件と検証を、アーキテクチャの一級市民にする。**

失敗の6割超は「賢さ」ではなく **「仕様と停止」** の問題である。

### チェックリスト（アーキテクチャ設計時に必ず埋める）

1. **各エージェントの役割は、他と重複しない一文で書けるか**
2. **各エージェントの停止条件は明示されているか**（何が揃ったら終わるか）
3. **全体の停止条件は明示されているか**（EIG 閾値 / 予算 / 反証枯渇 / 確度収束）
4. **エージェント間で受け渡すデータのスキーマは固定されているか**（自然言語の受け渡しは禁止）
5. **各出力に検証工程が対応しているか**（検証されない出力を下流に流さない）
6. **誤りが検出されたとき、どこまで巻き戻すか**が定義されているか
7. **中央の統制点は1つか**（複数の統制点は不整合を生む）

### 特に「情報伝達の断絶」への対策
IP では、エージェント間の受け渡しを **自然言語ではなく構造化オブジェクト**にする。

```
Claim { id, text, hypothesis_ids[], evidence_ids[], probability, verified_by[], as_of }
Evidence { id, source_id, span, retrieved_at, snapshot_hash, supports[], refutes[] }
Hypothesis { id, text, status(open|refuted|supported), diagnostic_evidence[] }
```

これは同時に [t-regulation-compliance](../04-domain/regulation-and-compliance.md) の監査要件と、
[t-context-engineering](context-engineering.md) の「圧縮時に出典 ID を失わない」要件を満たす。

## 4. 出典

- `[S-029]` https://arxiv.org/pdf/2503.13657 ／ NeurIPS 2025 poster
