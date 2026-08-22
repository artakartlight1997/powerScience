---
doc_id: t-pe-dd-workflow
title: "PE/VC デューデリの工程と、AI の効きどころ"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: domain
language: ja
tags: [private-equity, due-diligence, workflow, ic, pmi, adoption]
confidence: medium-high
primary_sources: [S-076, S-077]
related_topics: [t-finance-platforms, t-differentiation-hypotheses, t-data-sources]
contributes_to: [product, scope]
---

# PE/VC デューデリの工程と AI

## 1. 採用実態（2026）

| 指標 | 数値 | 出典 |
|---|---|---|
| 大手 PE のうち、投資ライフサイクルのいずれかで agentic AI を試験導入/拡大中 | **60%超**（McKinsey 推計） | `[S-076]` |
| 生成 AI を使うディールメーカー | **86%** | `[S-076]` |
| 取り組みが期待に一致/超過と回答したファンド | **95%** | `[S-076]` |
| **実際にスケールできている**ファンド | **10〜15%** | `[S-076]` |
| 文書抽出・スクリーニングの時間削減 | **70〜85%**、回収期間 **9ヶ月未満** | `[S-076]` |
| DD 期間 | 「**1週間 → 1日**」の事例報告 | `[S-077]` |
| 文書レビュー・契約・財務スプレッドの手作業削減 | **最大70%**（エンタープライズのセキュリティ要件を満たしつつ） | `[S-077]` |

> **ボトルネックは関心ではなく実行（scaling）である** `[S-076]`。
> 市場が求めているのは「もっと賢いモデル」ではなく、
> **既存ワークフローに接続でき、監査に耐え、繰り返し運用できるシステム**。

また PE チームは「AI で分析する」から
**「AI がワークフローを統率する（市場スキャン、シナリオ、DD の赤旗、統合支援をリアルタイムに）」**
段階へ移行しつつある `[S-076]`。

## 2. 工程図

```
ソーシング → 初期スクリーニング → IOI/LOI → 本格 DD ─┬─ 財務 DD（QoE, 運転資本, 会計方針）
                                                     ├─ 商業 DD（市場規模, 競合, 顧客, チャネル）
                                                     ├─ 法務 DD（契約, 訴訟, 許認可, CoC条項）
                                                     ├─ 人事/組織 DD（キーマン, 離職, 報酬）
                                                     ├─ IT/セキュリティ DD
                                                     └─ ESG/規制 DD
   → IC メモ → 価格・条件交渉 → SPA → PMI/100日計画 → モニタリング → Exit
```

## 3. 工程別の評価

| 工程 | AI の現状 | IP の狙い |
|---|---|---|
| ソーシング/スクリーニング | **既に量産可能（コモディティ）** | ここでは戦わない |
| **商業 DD** | Marlin / DR の主戦場。**一次情報が薄いのが弱点** | 顧客インタビュー設計・専門家への質問の**生成と優先順位付け**（＝ EIG） |
| **財務 DD** | 数値抽出は成熟。**判断（正常化・利益の質）は未解決** | XBRL 再計算 ＋ 会計方針変更の検出 ＝ **検証器の特権**（→ [t-verifier-design](../02-methods/verifier-design.md)） |
| 法務 DD | 抽出は Hebbia 等が強い | 契約条項 → **バリュエーション/リスクへの影響伝播** |
| **IC メモ** | 生成は容易。**IC での質問に耐えるかは別問題** | **反証済みであることを保証する** |
| PMI / モニタリング | **ほぼ手つかず** | **thesis tracking（仮説の追跡）** ＝ 差別化の第二波 |

## 4. 最重要の洞察

> 商業 DD で PE が本当に買っているのは「市場レポート」ではない。
> **「この投資仮説を殺しうる事実が、探したのに見つからなかった」という確信**である。

これは *生成* の問題ではなく ***探索の網羅性の証明*** の問題。
→ [t-information-value-eig](../02-methods/information-value-eig.md)
→ [t-structured-analytic-techniques](../02-methods/structured-analytic-techniques.md)

## 5. 導入戦略の含意

- scaling できているのが 10〜15% `[S-076]` ＝ **PoC 疲れが起きている**
- したがって「全社導入」ではなく **1工程の正本化（system of record）**から入る
- 候補: **IC メモの反証パス**（既存メモを叩いて穴を出す）→ 未決論点 D10

## 6. 出典

- `[S-076]` Accenture "Agentic AI Is Redefining Private Equity in 2026" ／ Multimodal 2026 PE レポート ／ 各種 2026 PE×AI ガイド
- `[S-077]` Third Bridge "PE due diligence with AI: The complete workflow (2026 guide)"
