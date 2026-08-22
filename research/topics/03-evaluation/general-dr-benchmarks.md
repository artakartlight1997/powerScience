---
doc_id: t-general-dr-benchmarks
title: "汎用 Deep Research ベンチマークの地図"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: evaluation
language: ja
tags: [benchmark, gaia, browsecomp, hle, frames, xbench, report-eval]
confidence: medium-high
primary_sources: [S-066, S-069, S-030]
related_topics: [t-finance-benchmarks, t-ip-evaluation-design, t-tongyi-deepresearch]
contributes_to: [evaluation, positioning]
---

# 汎用 DR ベンチマークの地図

## 1. 短答系（到達力を測る）

| ベンチ | 測るもの | 規模 | IP にとっての意味 |
|---|---|---|---|
| **GAIA** | 実世界の多段推論・ツール使用・Web 閲覧 | — | 基礎体力。必要だが十分でない |
| **BrowseComp** | **見つけにくく絡み合った情報**への粘り強い到達 | **1,266問** | **一次情報到達力**の代理指標。投資では効く |
| **BrowseComp-ZH** | 中国語版 | — | **日本語版が存在しない＝空白** |
| **WebWalkerQA** | 実用的な多段 Web 探索 | — | — |
| **FRAMES** | 検索＋推論の統合 | — | — |
| **xbench-DeepSearch** | 実用検索 | — | — |
| **HLE (Humanity's Last Exam)** | 専門家級の**閉じた**学術知識 | **2,500問** | **IP にはほぼ無関係**（クローズドブック・検索で解けない設計） |
| **MedBrowseComp** | 医療特化の DR ＋ computer use | — | ドメイン特化ベンチの先行例 |

**BrowseComp と HLE の違い** `[S-066]`:
BrowseComp は Web 情報を分析して答えに到達できるが、
HLE は**閉じた学術課題**で、深い推論と専門知識を要求する。
→ **IP が追うべきは BrowseComp 系（到達力）であって HLE ではない。**

### 参考値（Tongyi DeepResearch 30B）`[S-030]`
HLE 32.9 / BrowseComp 43.4 / BrowseComp-ZH 46.7 / WebWalkerQA 72.2 / GAIA 70.9 / xbench-DS 75.0 / FRAMES 90.6

## 2. レポート系（実務に近いが、測るのが難しい）

| ベンチ | 内容 |
|---|---|
| **DeepResearch Bench** | レポート水準の評価 |
| **LiveResearchBench** | 同上（ライブ） |
| **DRBench** | 同上 |
| **ReportBench**（arXiv:2508.15804） | **学術サーベイ課題**での DR 評価 |
| **DeepResearchEval**（arXiv:2601.09688）`[S-066]` | **DR タスクの自動生成**とエージェント評価の枠組み |
| **DeepResearch-9K**（arXiv:2603.01152）`[S-066]` | 大規模な難問データセット |
| **hint-free multi-hop 評価**（arXiv:2510.05137）`[S-069]` | ヒントなし多段質問と**因子分解した指標**で deep search を全体評価 |

**構造的な問題** `[S-066]`:
- 短答ベンチは**測りやすいが実務価値と乖離**する
- レポート級ベンチは**実務に近いが、注釈コストが重く、judge バイアスで信頼性が落ちる**
  （→ [t-llm-judge-reliability](llm-judge-reliability.md)）

## 3. IP の使い方

| 目的 | 使うベンチ |
|---|---|
| 基礎体力の確認（回帰テスト） | GAIA / BrowseComp の**日本語サブセットを自製** |
| 対外的な説明 | BrowseComp 系の数字（あれば） |
| **本当の差別化の証明** | **自製の評価**（→ [t-ip-evaluation-design](integral-prism-evaluation-design.md)） |

> **汎用ベンチでの勝敗は売り文句にはなるが、実益ではない。**
> IP の評価は「見落とし率」「較正」「検証コスト」で定義する。

## 4. 出典

- `[S-066]` DeepResearchEval arXiv:2601.09688 ／ DeepResearch-9K arXiv:2603.01152 ／ ReportBench arXiv:2508.15804
- `[S-069]` *Demystifying deep search* arXiv:2510.05137
- `[S-030]` Tongyi DeepResearch 技術報告
