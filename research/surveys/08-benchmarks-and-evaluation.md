---
doc_id: survey-08-benchmarks
title: "ベンチマークと評価設計 — 何を測れば勝ちなのか"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: survey
language: ja
tags: [benchmark, evaluation, gaia, browsecomp, hle, financebench, rubric]
confidence: medium-high
primary_sources: [S-066, S-067, S-068, S-069, S-070]
contributes_to: [evaluation, product-claims, roadmap]
---

# 08. ベンチマークと評価設計

## 1. 汎用 DR ベンチマークの地図

| ベンチ | 測るもの | 形式 | IP にとっての意味 |
|---|---|---|---|
| **GAIA** | 実世界の多段推論・ツール使用・Web 閲覧 | 短答 | 基礎体力。必要だが十分でない |
| **BrowseComp**（1,266問） | 「見つけにくく絡み合った情報」への粘り強い到達 | 短答 | **一次情報到達力**の代理指標。投資では効く |
| **BrowseComp-ZH / WebWalkerQA / FRAMES / xbench-DeepSearch** | 多言語・多段・実用検索 | 短答 | 日本語版が存在しないのは**空白** |
| **HLE (Humanity's Last Exam)**（2,500問） | 専門家級の閉じた学術知識 | 短答 | IP には**ほぼ無関係**（クローズドブック） |
| **DeepResearch Bench / LiveResearchBench / DRBench** | **レポート水準**の評価 | 長文＋ルーブリック | 方向は正しいが**注釈コストが重い** `[S-066]` |
| **ReportBench** | 学術サーベイ課題での DR 評価 | 長文 | 手法参考 |
| **DeepResearchEval** | DR タスクの**自動生成**とエージェント評価 | 自動 | 評価の自動化手法として重要 `[S-066]` |

**構造的な問題**: 短答ベンチは測りやすいが実務価値と乖離する。
レポート級ベンチは実務に近いが、**注釈コストと judge バイアス（→07）で信頼性が落ちる**。
→ この裂け目こそ、我々が独自評価を作る根拠になる。

## 2. 金融ドメインのベンチマーク（2026 時点で急増中）

| ベンチ | 内容 |
|---|---|
| **FinQA** | 財務報告書・表に対する数値推論 |
| **FinanceBench** | 公開企業ファイリングに接地した open-book QA（1万超の Q-A-evidence 三つ組）`[S-067]` |
| **Finance Agent Benchmark**（arXiv:2508.00828） | 金融エージェント課題 |
| **FinTrace**（arXiv:2604.10015） | **軌跡レベル**でのツール呼び出し評価（長期金融タスク）`[S-068]` |
| **Herculean**（arXiv:2605.14355） | 金融知性のエージェント的ベンチ |
| **BizFinBench.v2** | 二言語・専門家水準の金融能力 |
| **FinVerBench** | **財務諸表検証における妥当性と較正** `[S-068]` |
| **IPO Finance Agent**（arXiv:2606.23032） | **S-1 / IPO デューデリ**、自動ルーブリック生成つき `[S-068]` |
| **FinMCP-Bench / FinToolBench**（2026） | ツール呼び出し精度・意図整合 |
| **EDINET-Bench**（Sakana） | **日本語・有価証券報告書**（2014-2024, 約4万件）`[S-016]` |

**読み取れること**:
1. 2026年は **「答えの正しさ」から「軌跡・ツール・較正」へ**評価の重心が移っている（FinTrace, FinVerBench）。
   → IP の設計思想（証拠構造そのものを成果物にする）は、評価トレンドと一致している。
2. **日本語金融の評価基盤は EDINET-Bench がほぼ唯一**で、それは Sakana が握っている。
   → 我々が独自の日本語 DD 評価セットを作れば、それ自体が資産になる。

## 3. IP 独自の評価設計（提案の叩き台）

汎用ベンチでの勝敗は**売り文句にはなるが、実益ではない**。00 で定義した5軸に沿って自前の評価を組む。

### 評価 A: 反実仮想デューデリ（Retrospective DD）
過去の実案件・実 M&A で、**T 時点までの情報のみ**を与えて分析させ、T+2〜3年の実際の結果と突き合わせる。
- 測るもの: **見落とし率**（後に材料化した事実の事前検出率）、**較正**（Brier）
- 作り方: EDINET/EDGAR ＋ 適時開示 ＋ ニュースを **時点凍結（point-in-time）**で構成。
  **リークの防止が最大の技術課題**（モデルは後年の結果を知っている）
- 先行例: EDINET-Bench はラベル自動付与＋更新可能設計 `[S-016]` — 同じ思想を DD 型に拡張する

### 評価 B: 引用の閉ループ検証
07 の `Cited but Not Verified` 枠組みをそのまま社内 CI にする `[S-057]`。
- 指標: Link Works / Relevant / **Fact Check**、および **探索量に対する Fact Check の劣化曲線**
- **合格条件の例**: ツール呼び出し 150 回時点でも Fact Check ≥ 90% を維持

### 評価 C: 診断力（ACH ベース）
生成された仮説集合が、**実際に起きた事象を含んでいたか**（hypothesis recall）と、
**診断的証拠を優先探索できたか**（EIG 効率）を測る。

### 評価 D: 人的コスト
アナリストが成果物を**検証し直すのに要した時間**。
これは競合が誰も測っていないが、**購買意思決定を最も左右する数字**。`C`

### 判定の作法（07 を反映）
- LLM judge は **「原文に支持されるか」の二値判定にのみ**使う
- 順序ランダム化・両順序評価、複数 judge の一致率（κ）を常時記録
- **判定の判定**：人手サンプルで judge 自体を四半期ごとに較正

## 4. 参考（出典）

`[S-066]` *DeepResearchEval* arXiv:2601.09688 ／ *DeepResearch-9K* arXiv:2603.01152 ／ *ReportBench* arXiv:2508.15804
`[S-067]` FinanceBench / FinQA（各原論文）
`[S-068]` *FinTrace* arXiv:2604.10015 ／ *FinVerBench* arXiv:2605.29586 ／ *IPO Finance Agent* arXiv:2606.23032 ／ *Herculean* arXiv:2605.14355
`[S-069]` *Demystifying deep search: a holistic evaluation with hint-free multi-hop questions* arXiv:2510.05137
`[S-070]` *Learning Query-Specific Rubrics from Human Preferences for DeepResearch Report Generation* arXiv:2602.03619
