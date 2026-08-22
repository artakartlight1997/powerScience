---
doc_id: t-regulation-compliance
title: "規制とコンプライアンス — 設計制約であり、同時に堀"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: domain
language: ja
tags: [eu-ai-act, audit-trail, mnpi, chinese-wall, iso42001, security]
confidence: medium
primary_sources: [S-079, S-080, S-005]
related_topics: [t-failure-modes-mast, t-data-sources, t-commoditization-moat]
contributes_to: [architecture-constraints, moat]
---

# 規制とコンプライアンス

**後付けするとコストになる。最初から作ると堀になる。**

## 1. EU AI Act

| 項目 | 内容 |
|---|---|
| 施行 | 高リスク AI システムの義務が **2026-08-02 から完全適用** `[S-079]` |
| 制裁 | 最大 **€35M または全世界売上の 7%** `[S-079]` |
| **監査証跡**（Art.12/13） | **タイムスタンプ付きログ、モデルバージョン追跡、人間レビュー記録** `[S-079][S-080]` |
| 保持 | **展開後10年** `[S-079]` |
| 保存形式 | **改竄検知可能**（追記専用・暗号連鎖）。**通常の DB は要件を満たさない**（記録を静かに書き換えられるため）`[S-080]` |
| **人間の監督** | 異常時に**介入・停止できる設計**が必須 `[S-079]` |
| その他 | ISO/IEC 42001、プライベートネットワーク接続要件などが絡む `[S-079]` |

金融領域では、消費者向け金融サービス（与信スコアリング、保険引受など）に対して
リスク管理・人間の監督・完全な監査証跡を求める枠組みが既に拘束力を持つ `[S-079]`。

> **注**: 投資リサーチ支援が「高リスク」に該当するかは附属書 III の解釈次第（→ 宿題 Q10）。
> ただし**該当しなくても、顧客（金融機関）の内部基準が同等以上を要求する**ことが多い。

## 2. 金融固有の制約

| 制約 | 内容 | 設計要件 |
|---|---|---|
| **MNPI（重要な未公開情報）** | エージェントが横断検索する構造は、**情報障壁（Chinese Wall）を壊しうる** | **案件単位のデータ隔離とアクセス統制**。横断学習の範囲を明示的に制御 |
| **専門家ネットワーク** | 顧客企業の内部情報の取扱い（コンプラ研修・記録） | 取得経路のメタデータ必須 |
| **学習非利用** | Marlin も明示している `[S-005]` | **最低ライン**であって差別化ではない |
| **データ所在** | 国内保管要件（金融機関に多い） | リージョン選択・自社ホストの選択肢（→ オープンモデル） |
| **記録保持** | 金商法・社内規程の保存義務 | 監査ログと同一基盤で満たす |

## 3. IP の設計原則 P12

> **監査証跡を後付けしない。**
> **探索木・証拠・判断の系譜そのものを、改竄検知可能な形で一次記録にする。**

```
記録すべき単位:
  Evidence  { source_id, url, retrieved_at, content_hash, snapshot, span }
  Claim     { text, evidence_ids[], probability, verified_by[], model_version, as_of }
  Hypothesis{ text, status, refuted_by[], created_by(human|agent), at }
  Decision  { question, options, chosen, rationale_claim_ids[], human_overrides[] }
  Search    { query, tool, cost, results[], eig_estimate, decided_by }
保存形式: 追記専用 + ハッシュ連鎖（tamper-evident）
```

**これは L0 検証層と同一のデータ構造である**（→ [t-citation-attribution](../03-evaluation/citation-attribution.md)）。
つまり **規制対応とプロダクト価値が、同じ実装で同時に満たされる稀なケース**。

## 4. 堀としての規制

| 効果 | 内容 |
|---|---|
| **参入障壁** | 監査要件を満たす実装は、後発が軽く作れない |
| **調達を通す** | 金融機関のセキュリティ審査（3〜6ヶ月）を通った実績自体が資産 |
| **価格の正当化** | 「監査に耐える」は高単価の理由になる |

→ [t-commoditization-moat](../05-strategy/commoditization-and-moat.md)

## 5. 出典

- `[S-079]` EU AI Act 2026 コンプライアンス各種（Art.12/13 のトレーサビリティ要件、施行日、制裁）
- `[S-080]` Velt "AI Decision Audit Trails: Regulator Rules June 2026"
- `[S-005]` VentureBeat（Marlin のデータ方針）
