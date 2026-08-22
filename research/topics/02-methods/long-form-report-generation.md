---
doc_id: t-long-form-report
title: "長文レポート生成 — 階層計画・一貫性・スライド化"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [long-form, report-generation, outline, coherence, multimodal, slides]
confidence: medium
primary_sources: [S-070]
related_topics: [t-storm-costorm, t-sakana-marlin, t-ip-evaluation-design]
contributes_to: [output-layer]
---

# 長文レポート生成

**IP では「レポートは成果物ではなく view」だが、view の品質は購買に効く。**
Marlin は 100ページ＋スライドを出してくる `[S-005]`。ここで見劣りすると土俵に上がれない。

## 1. 課題

LLM は短文生成には強いが、長文では **一貫性・論理的整合・動的な適応**が崩れる `[S-070 関連]`。

## 2. 手法の系譜

| 手法 | アプローチ |
|---|---|
| **事前計画（pre-writing planning）** | 先に包括的なアウトラインを作ってから書く。最も一般的 |
| **階層的生成** | セクション → 段落 → 文と階層的に降りる |
| **Beyond Outlining**（arXiv:2503.08275） | **異種再帰的計画**：アウトライン一本槍でなく、適応的に計画構造を変える |
| **SuperWriter**（ACL Findings 2026） | **反省駆動**の長文生成 |
| **LongWriter**（arXiv:2408.07055） | 1万語超の生成能力の解放 |
| **LLM×MapReduce-V2**（arXiv:2504.05732） | 超長大な資料から長文記事を作る**エントロピー駆動の畳み込み的 test-time scaling** |
| **NexusSum**（ACL 2025） | 長文要約の階層エージェント |
| **三段階エージェント枠組み**（2026） | Plan 段階で **AI コメンテータと執筆者が議論**して構造化された執筆計画を作る |
| **Deep-Reporter**（arXiv:2604.10741） | **接地されたマルチモーダル長文生成**。大域的なセクション一貫性、**画像-テキスト整合**、大量のマルチモーダル文脈管理 |
| **query-specific rubrics**（arXiv:2602.03619）`[S-070]` | 人間の選好から**クエリ固有のルーブリック**を学習して DR レポートを評価・生成 |

## 3. IP での位置づけ

```
[一次データ構造]                      [view として生成]
ACH 行列 / 証拠 / 確率  ──────────▶  ① IC メモ（1〜3ページ）
                        ├─────────▶  ② 反証サマリ（何を潰し、何が残ったか）
                        ├─────────▶  ③ 詳細レポート（数十ページ）
                        └─────────▶  ④ スライド（IC 提出用）
```

**設計上の要点**
1. **レポートから証拠構造を作るのではない。証拠構造からレポートを作る。**
   （逆にすると、引用検証も監査も成立しない）
2. すべての view は**同じ証拠 ID を参照する**。表現が変わっても根拠は同一。
3. **生成後に必ず引用検証を通す**（→ [t-citation-attribution](../03-evaluation/citation-attribution.md)）。
   生成 → 検証 → 不合格箇所の差し戻し、をパイプラインに組み込む。
4. マルチモーダル（図表・スライド）では**画像-テキスト整合**が新たな幻覚源になる（Deep-Reporter の問題意識）。
   数値を含む図は**データから直接描画**し、LLM に描かせない。

## 4. 出典

- `[S-070]` *Learning Query-Specific Rubrics from Human Preferences for DeepResearch Report Generation* arXiv:2602.03619
- 関連: Beyond Outlining arXiv:2503.08275 ／ LongWriter arXiv:2408.07055 ／ LLM×MapReduce-V2 arXiv:2504.05732 ／ Deep-Reporter arXiv:2604.10741 ／ SuperWriter (ACL Findings 2026)
