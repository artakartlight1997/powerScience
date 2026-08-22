---
doc_id: t-document-understanding
title: "文書理解 — 契約書・スキャン PDF・図表の抽出"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: domain
language: ja
tags: [document-ai, ocr, layout, contract, table-extraction, realdoc-bench]
confidence: medium
primary_sources: [S-136]
related_topics: [t-numeric-verification, t-vc-dd-multi-agent, t-data-sources]
contributes_to: [ingestion-architecture]
---

# 文書理解

**VDR の実体はスキャン PDF と Excel と契約書の山である。ここで詰まると何も始まらない。**

## 1. 2026年の到達点 `[S-136]`

- OCR は「画素を文字にする」段階を脱し、**レイアウト認識・マルチモーダル理解・LLM ネイティブ出力**を統合
- **表を視覚的構造として解析**し、行列関係の保持、**結合セル・不規則レイアウト**の処理、**ページ跨ぎの継続**に対応
- 図表・画像・視覚要素も処理対象

### 文書種別ごとの推奨構成 `[S-136]`
| 文書 | 推奨 |
|---|---|
| **法務契約書** | **LLM による意味理解 ＋ 人間レビュー** |
| **財務諸表** | **ハイブリッド**（表は OCR、分析は LLM） |
| 規制・金融ワークフロー全般 | **document AI ＋ LLM レビュー**。「1つのモデルがパイプライン全体を兼ねる」は誤り |

## 2. ベンチマークと現実のギャップ（重要）

> **ベンチマークで高得点のモデルが、実際のローン書類や金融ワークフローでは
> 意味のある精度低下を示す。ベンチマークは、本番パイプラインが日々遭遇する
> レイアウトの多様性とスキャン品質の劣化を含んでいないため。** `[S-136]`

- **RealDoc-Bench**（実本番文書での評価、金融サービス等から 1,500+ サンプル）:
  **レイアウト精度 Adjusted F1 = 0.847**、**文書 QA 精度 = 95.7%** `[S-136]`

→ これは [t-benchmark-crisis](../03-evaluation/benchmark-crisis-and-real-world-gap.md) と同じ構図。
**ベンチ精度を信じて設計すると、本番で崩れる。**

## 3. IP への設計要件

| # | 要件 | 理由 |
|---|---|---|
| 1 | **単一モデルで全部やらない** | 規制・金融では document AI ＋ LLM の2段が推奨 `[S-136]` |
| 2 | **抽出の信頼度を持ち回す** | OCR の確信度・レイアウト解析の曖昧性を、下流の確率計算に伝播させる |
| 3 | **原文座標（bbox）を保持** | 引用検証（→ [t-citation-attribution](../03-evaluation/citation-attribution.md)）で**「原文のこの位置」まで返す**ため。<br>「PDFの何ページ目のどこ」を示せると、人間の検証時間が激減する（＝評価D） |
| 4 | **三値（value / NOT_FOUND / AMBIGUOUS）** | 捏造の防止 `[S-090][S-131]` |
| 5 | **日本語文書の追加検証** | 縦書き、和暦、全角数字、押印、旧字体。**RealDoc-Bench 等は日本語を含まない可能性が高い** `C` → 宿題 |
| 6 | **契約書は必ず人間レビュー前提** | LLM 単独の判断を最終としない `[S-136]` |

## 4. 未検証（宿題）

| # | 問い |
|---|---|
| Q30 | 日本語の実務文書（和暦・縦書き・押印・手書き注記）での OCR/レイアウト精度の実測 |
| Q31 | 契約書の条項抽出 → バリュエーション影響への伝播を、どこまで自動化できるか |

## 5. 出典

- `[S-136]` Vision AI Document Processing 2026（Parseur）／ LlamaIndex「Best OCR Software for Finance 2026」「Best AI PDF Parsers 2026」／ Extend「OCR Benchmarks & Real-World Documents (2026-07)」RealDoc-Bench ／ Vellum「Document Data Extraction: LLMs vs OCRs」
