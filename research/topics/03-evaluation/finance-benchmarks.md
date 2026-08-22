---
doc_id: t-finance-benchmarks
title: "金融ドメインのベンチマーク — 評価の重心が「軌跡と較正」に移った"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: evaluation
language: ja
tags: [finance-benchmark, financebench, finqa, fintrace, finverbench, ipo, edinet]
confidence: medium-high
primary_sources: [S-067, S-068, S-016]
related_topics: [t-sakana-edinet-bench, t-ip-evaluation-design, t-pe-dd-workflow]
contributes_to: [evaluation, data-strategy]
---

# 金融ドメインのベンチマーク

2026年に急増している。**評価の重心が「答えの正しさ」から「軌跡・ツール・較正」へ移った。**

## 1. 一覧

| ベンチ | 内容 | 年 |
|---|---|---|
| **FinQA** `[S-067]` | 財務報告書・表に対する**数値推論** | 2021 |
| **FinanceBench** `[S-067]` | 公開企業ファイリングに接地した open-book QA。**1万超の Q-A-evidence 三つ組** | 2023 |
| **Finance Agent Benchmark**（arXiv:2508.00828） | 金融エージェント課題 | 2025 |
| **FinTrace**（arXiv:2604.10015）`[S-068]` | **軌跡レベル**でのツール呼び出し評価（長期金融タスク） | 2026 |
| **Herculean**（arXiv:2605.14355）`[S-068]` | 金融知性のエージェント的ベンチ | 2026 |
| **BizFinBench.v2**（arXiv:2601.06401） | 二言語・専門家水準の金融能力（デュアルモード） | 2026 |
| **FinVerBench**（arXiv:2605.29586）`[S-068]` | **財務諸表検証における妥当性と較正** | 2026 |
| **IPO Finance Agent**（arXiv:2606.23032）`[S-068]` | **S-1 / IPO デューデリ**。ガバナンス分析、共通支配下の会計、資本形成の物語、引受に敏感な開示。**自動ルーブリック生成**つき | 2026 |
| **FinMCP-Bench / FinToolBench**（2026）`[S-068]` | ツール呼び出し精度／ツール選択と意図の整合 | 2026 |
| **M3FinMeeting**（arXiv:2506.02510） | 多言語・多セクタ・多タスクの金融会議理解 | 2025 |
| **LATTICE**（arXiv:2604.26235） | エージェントの**意思決定支援としての有用性**評価（暗号領域） | 2026 |
| **EDINET-Bench**（Sakana）`[S-016]` | **日本語・有価証券報告書**（2014-2024, 約4万件） | 2025 |

## 2. 読み取れること

### (a) 評価トレンドが IP の設計思想と一致している
**FinTrace（軌跡）**、**FinVerBench（検証と較正）**、**LATTICE（意思決定支援としての有用性）** —
どれも「最終回答の正誤」ではなく**過程と較正と実用性**を測っている。
→ IP の「証拠構造そのものを成果物にする」設計は、評価トレンドの正面にある。

### (b) IPO Finance Agent は最も近い先行事例
S-1 デューデリという**実務工程そのもの**をベンチ化し、
**自動ルーブリック生成**を導入している `[S-068]`。
→ IP の評価設計（反実仮想 DD）で**手法を借用できる**。

### (c) 日本語金融の評価基盤は EDINET-Bench がほぼ唯一で、Sakana が握っている
→ **独自の日本語 DD 評価セットを作れば、それ自体が資産になる**。
→ [t-sakana-edinet-bench](../01-competitors/sakana-edinet-bench.md)

## 3. 出典

- `[S-067]` FinanceBench ／ FinQA（各原論文）
- `[S-068]` FinTrace arXiv:2604.10015 ／ FinVerBench arXiv:2605.29586 ／ IPO Finance Agent arXiv:2606.23032 ／ Herculean arXiv:2605.14355 ／ FinMCP-Bench / FinToolBench (2026)
- `[S-016]` https://sakana.ai/edinet-bench/
