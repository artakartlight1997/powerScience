---
doc_id: t-sakana-edinet-bench
title: "EDINET-Bench — 日本語金融ベンチマークという伏兵"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: competitors
language: ja
tags: [edinet, xbrl, japan, benchmark, sakana, finance]
confidence: medium
primary_sources: [S-016, S-017]
related_topics: [t-data-sources, t-finance-benchmarks, t-ip-evaluation-design]
contributes_to: [data-strategy, evaluation, competitive-risk]
---

# EDINET-Bench

**Sakana は既に日本の開示データを触っている。**「日本市場での金融特化」は無風地帯ではない。

## 1. 事実

- Sakana AI 公開の**日本語金融ベンチマーク**。有価証券報告書を使用 `[S-016]`
- **2014–2024 の有報 約4万件以上**を利用 `[S-016]`
- **全タスクにラベルが自動付与**され、**データセットの更新・拡張が可能**な設計 `[S-016]`
- タスク定義の詳細（不正検知系か、DD 的推論か）は未確認 → 宿題 Q9

## 2. なぜ重要か

### (a) 競合リスク
Sakana は「日本語 × 金融 × 評価基盤」を既に押さえている。
Marlin が今後金融特化を深める場合、**評価軸を自社ベンチで定義できる**立場にある。

### (b) 一方で、そこは難所でもある
EDINET / XBRL の構造化には既知の実務課題がある `[S-017]`。

1. **企業別のタクソノミ拡張**（各社が独自タグを追加する）
2. **表構造の非定型性**
3. **注記の自由記述性**
4. 年度をまたいだ**タグの改定・不連続**

さらに有報は **「XBRL（構造化）＋ MD&A・リスク情報（非構造化）」のハイブリッド文書** `[S-017]`。
→ **数値と物語を突き合わせる推論**（＝投資分析そのもの）の教材になる。

### (c) 汎用 DR エージェントが最も苦手な領域
汎用の Deep Research は「Web を検索して要約する」ことに最適化されている。
**構造化された財務データの再計算・整合検証**は、検索ではなく**データエンジニアリング**の問題であり、
ここには**エンジニアリングの堀が立つ**。

## 3. Integral Prism の取り方

| 選択肢 | 内容 | 評価 |
|---|---|---|
| EDINET-Bench に乗る | 同じ土俵で性能を競う | **不利**。相手の定義した軸で戦う |
| **独自の日本語 DD 評価セットを作る** | 反実仮想デューデリ（point-in-time）を自製 | **推奨**。評価軸そのものが資産になる |
| 英語（EDGAR）に逃げる | 競合過密 | 消極的 |

→ 設計は [t-ip-evaluation-design](../03-evaluation/integral-prism-evaluation-design.md)。

なお 2026 年時点で、実務側には「Claude Code で日本株データを分析する」「J-Quants × EDINET DB」等の
ガイドが出回っており `[S-017]`、**データ取得層はコモディティ化しつつある**。
差がつくのは取得ではなく**整合検証と時点再現**。

## 4. 出典

- `[S-016]` https://sakana.ai/edinet-bench/
- `[S-017]` https://edinetdb.jp/blog/xbrl-japan-securities-reports-structuring
