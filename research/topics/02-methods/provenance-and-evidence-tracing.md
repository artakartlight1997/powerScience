---
doc_id: t-provenance
title: "実行プロヴェナンスと証拠トレース — 監査可能性の実装形"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [provenance, evidence-tracing, audit, trace-graph, accountability, ledger]
confidence: medium-high
primary_sources: [S-128]
related_topics: [t-regulation-compliance, t-citation-attribution, t-agent-security]
contributes_to: [core-architecture, compliance]
---

# 実行プロヴェナンスと証拠トレース

**IP が「探索木そのものを監査証跡にする」（P12）と言ってきたものには、既に学術的な名前と枠組みがある。**

## 1. 定義（サーベイ arXiv:2606.04990）`[S-128]`

- **実行プロヴェナンス（execution provenance）** = **エージェント実行の型付きグラフ**
- **証拠トレース（evidence tracing）** = そのグラフを**証拠-支持関係に射影したもの**

この視点は、以下を**単一の枠組みで結ぶ** `[S-128]`:
> 検索の接地、主張の支持、ツール使用の安全性、記憶の系譜、可観測性、デバッグ、監査、復旧

### 動機（そのまま IP の主張）`[S-128]`
> エージェントの能力拡大は自律性を高めるが、同時に**振る舞いの検証・デバッグ・監査を困難にする**。
> **正しい答えは、それがどう作られたかを何も語らない** —
> どの証拠が各主張を支持したのか、ツール呼び出しは正当だったのか、
> 記憶が後の判断をどう形作ったのか、実行の失敗はどこで生じたのか。

サーベイは文献を **トレースの源 / 証拠の単位 / プロヴェナンス関係 / トレースの粒度 / トレースの時点**
という次元で整理している `[S-128]`。

## 2. 実装形 — LEDGER（Claim-to-Evidence Trace Graphs）`[S-128]`

*LEDGER: Claim-to-Evidence Trace Graphs for Auditing LLM Agents*（arXiv:2608.18398）は、
**主張から証拠へのトレースグラフでエージェントを監査する**という、IP の L0-L1 とほぼ同一の発想。

## 3. IP への含意

### ✅ 良い知らせ
**我々の「証拠構造を一次データにする」という設計は、独自の思いつきではなく、
2026年に立ち上がりつつある研究領域の主流である。**
→ 用語・データモデル・評価指標を**既存研究から借りられる**（自前で発明しなくてよい）。
→ 対外説明でも「実行プロヴェナンス」という確立した語彙が使える。

### ✅ 一石四鳥の構造
同じトレースグラフが、**4つの要求を同時に満たす**。

| 要求 | どう満たされるか |
|---|---|
| **引用の機械検証** | 主張→証拠の辺をたどって原文照合（→ [t-citation-attribution](../03-evaluation/citation-attribution.md)） |
| **規制の監査証跡** | EU AI Act Art.12/13、FINRA の署名記録（→ [t-regulation-compliance](../04-domain/regulation-and-compliance.md)） |
| **セキュリティの taint 追跡** | 未信頼ソース由来の伝播をグラフ上で追う（→ [t-agent-security](agent-security-and-prompt-injection.md)） |
| **デバッグと復旧** | 失敗の起点特定、部分再実行 `[S-128]` |

> **設計上の結論**: この4つを別々の仕組みで作ってはいけない。**1つのグラフで賄う。**
> 逆に言えば、**このグラフのスキーマ設計が、IP のアーキテクチャの中心**になる。

### データモデル（叩き台、再掲＋拡張）
```
Node:  Claim / Evidence / Hypothesis / ToolCall / Decision / HumanAction / MemoryItem
Edge:  supports / refutes / derived_from / retrieved_by / verified_by /
       tainted_by / approved_by / superseded_by
属性:  as_of（主張時点）, valid_until（有効期限）, source_type, trust_label,
       content_hash, model_version, cost, human_signature
制約:  追記専用（append-only）＋ ハッシュ連鎖
```

## 4. 出典

- `[S-128]` *From Agent Traces to Trust: A Survey of Evidence Tracing and Execution Provenance in LLM Agents* arXiv:2606.04990 ／ *LEDGER: Claim-to-Evidence Trace Graphs for Auditing LLM Agents* arXiv:2608.18398
