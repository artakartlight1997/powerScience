---
doc_id: t-data-sources
title: "データ源の地図 — 公開 / 準公開 / プライベート"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: domain
language: ja
tags: [data, edinet, xbrl, edgar, alternative-data, expert-network, private-data]
confidence: medium
primary_sources: [S-078, S-016]
related_topics: [t-sakana-edinet-bench, t-retrieval-graphrag, t-commoditization-moat]
contributes_to: [data-strategy, moat]
---

# データ源の地図

## 1. 公開（機械可読）

### 日本
| データ | 内容 | 論点 |
|---|---|---|
| **EDINET** | 有報・四半期・大量保有・公開買付 | **XBRL 構造化が難所** `[S-078]` |
| **TDnet** | 適時開示 | 速報性。イベント検知に必須 |
| **J-Quants** | 株価・財務 | 2026年時点で EDINET との連携ガイドが出回る `[S-078]` |
| 官報 / 登記 / 法人番号 | 会社の基礎情報、異動 | 名寄せ（entity resolution）が課題 |
| J-PlatPat（特許） | 技術的な堀の検証 | — |
| e-Stat | 産業統計 | 市場規模の三角測量 |

**XBRL の実務課題** `[S-078]`:
1. **企業別のタクソノミ拡張**（各社が独自タグを追加）
2. **表構造の非定型性**
3. **注記の自由記述性**
4. 年度をまたいだ**タグの改定・不連続**

有報は **XBRL（構造化）＋ MD&A・リスク情報（非構造化）のハイブリッド文書** `[S-078]`。
→ **数値と物語を突き合わせる推論**が要る＝汎用 DR が最も苦手な領域。

### 米国
EDGAR / XBRL、8-K、**S-1**、13F、Form D

## 2. 準公開・有償（オルタナティブデータ）

| 種別 | シグナル |
|---|---|
| **求人** | 採用動向＝戦略の**先行指標**（どの職種を何人採るか） |
| **口コミ / レビュー**（Glassdoor 等） | 組織の実態、離職の予兆 |
| Web/アプリ トラフィック | 需要の実態 |
| 輸出入・物流 | サプライチェーンの実態 |
| カード決済集計 | 消費の実態 |
| 衛星・位置情報 | 稼働率 |
| 業界誌・カンファレンス資料 | 業界の暗黙知 |
| **専門家ネットワーク**（expert network） | **一次情報**。最も高価で最も価値がある |

## 3. プライベート（ファンド内）★堀

| データ | 価値 |
|---|---|
| 過去の **IC メモ** | そのファンドの判断の型 |
| 過去の **DD レポート** | 何を見たか |
| **VDR** の資料 | 案件固有の非公開情報 |
| ポートフォリオ実績 | 予測 vs 実績（**較正の教師データ**） |
| CRM / ディールログ | 人脈と経緯 |
| **見送った案件の記録** | **最も価値がある。誰も体系化していない** |

## 4. 戦略的含意

```
公開データ    → 誰でも買える（コモディティ）
オルタナデータ → 金で買える（差別化にならない。むしろ原価）
プライベート  → ★ファンドの独自資産。ここでしか堀は立たない
```

**IP の設計要請**:
1. プライベートデータを**安全に取り込み、外に漏らさずに価値へ変換**する構造
   （→ [t-regulation-compliance](regulation-and-compliance.md)）
2. **見送った案件・外した理由**を構造化して蓄積
   （→ [t-memory-continual-learning](../02-methods/memory-and-continual-learning.md)）
3. 公開データ層は**コモディティとして安く早く**組む（2026年時点で実務ガイドが出回っている `[S-078]`）。
   差がつくのは取得ではなく**整合検証と時点再現（point-in-time）**

## 5. 出典

- `[S-078]` EDINET DB（XBRL 構造化の課題 / 2026年の実務ガイド）https://edinetdb.jp/blog/xbrl-japan-securities-reports-structuring ／ freee EDINET 解説 ／ 日経 xTECH「Pythonによる財務分析」
- `[S-016]` Sakana AI EDINET-Bench https://sakana.ai/edinet-bench/
