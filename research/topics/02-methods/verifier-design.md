---
doc_id: t-verifier-design
title: "検証器の設計 — 生成-検証の非対称性と特権"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [verifier, prm, orm, generator-verifier-gap, tool-verification]
confidence: medium-high
primary_sources: [S-036, S-037, S-038, S-039]
related_topics: [t-citation-attribution, t-test-time-scaling, t-llm-judge-reliability]
contributes_to: [core-architecture, differentiation]
---

# 検証器の設計

**IP の技術的中核。ここで差がつく。**

## 1. 生成-検証の非対称性

- 多くの領域で **検証は生成より容易**（generator-verifier gap）`[S-036]`
- **判定側が生成側にないツール（コード実行、DB 照合、原文取得）を持つと、ギャップは拡大する** `[S-036]`
  例: 数学解答を判定する judge がコードを実行できる場合
- ただし非対称性は一様ではない `[S-036]`:

| 種類 | 例 | IP での扱い |
|---|---|---|
| **解くのは難しいが検証は易しい** | 数値の再計算、引用の照合、コードのテスト | **機械検証を全面適用** |
| **解くのは易しいが検証は難しい** | 「この市場は伸びる」「経営陣は優秀だ」 | **反証タスクに変換する**（→ ACH） |

- さらに、検証器の性能は **生成側の確信度に依存して変動**する `[S-037]`
  → **自信満々な誤りは検証を通りやすい**。これは投資判断で最も危険な失敗モード。

## 2. 検証器の種類

| 種類 | 内容 |
|---|---|
| **ORM**（結果報酬モデル） | 最終解の正誤のみを見る |
| **PRM**（過程報酬モデル） | **推論ステップ単位**で検証 `[S-038]` |
| **GenPRM** | PRM 自体に推論時計算を割く（生成的検証）`[S-038]` |
| **T1（ツール統合検証）** | 小型モデルでも**外部ツールで検証すれば強い** `[S-038]` |
| **Multi-Agent Verification** | 複数の検証器で test-time compute をスケール `[S-039]` |

## 3. IP の設計原則 — 検証器に「特権」を与える

> **設計原則 P5: 検証器には、生成器が持たない権限を与える。**

| 特権 | 内容 | 効果 |
|---|---|---|
| **原文取得権** | 引用先 URL / 文書を実際に開き、当該スパンを取得する | 引用の事実整合性を機械判定できる |
| **数値再計算権** | XBRL / 財務モデルを再実行し、主張された数値を再現する | 「それらしい数字」を潰す |
| **時系列整合権** | 全証拠の取得時刻・有効期間を照合し、**後知恵バイアス**と古い前提を検出 | point-in-time の担保 |
| **クロスベンダ権** | **生成と検証を必ず別ベンダのモデルで行う** | 同一モデルの盲点の共有を防ぐ |

**なぜこれが競合優位になるか**:
Marlin / Gemini DR は基本的に **同じモデル系列が自己評価する**構造 `C`。
同じモデルは**同じ盲点**を持つ。検証側にツールとベンダ多様性を与えるだけで、構造的な差が出る。

→ 実装の詳細は [t-citation-attribution](../03-evaluation/citation-attribution.md)、
判定タスクの設計制約は [t-llm-judge-reliability](../03-evaluation/llm-judge-reliability.md)。

## 4. 注意 — 自己検証には限界がある

自己検証（self-verification）の性能は、生成能力との非対称性に縛られる `[S-036][S-037]`。
「もう一度考えさせる」だけでは、構造的な誤りは取れない。
**外部の事実・外部のツール・外部のモデル**を入れることが必要条件。

## 5. 出典

- `[S-036]` *Trust but Verify! A Survey on Verification Design for Test-time Scaling* arXiv:2508.16665
- `[S-037]` *Exploiting Verification-Generation Gap* arXiv:2606.03608
- `[S-038]` GenPRM arXiv:2504.00891 ／ T1 arXiv:2504.04718
- `[S-039]` *Multi-Agent Verification* arXiv:2502.20379
