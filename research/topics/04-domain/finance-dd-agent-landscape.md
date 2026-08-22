---
doc_id: t-finance-dd-landscape
title: "金融・DD特化エージェントの現況と、我々の新規性の正直な棚卸し"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: domain
language: ja
tags: [finance, dd, hebbia, alphasense, harvey, novelty-audit]
confidence: medium-high
related_topics: [t-failure-mode-catalog, t-pe-dd-workflow, arch-dominance-proof]
contributes_to: [dominance-proof, positioning]
---

# 金融・DD特化の現況(2025-26)と新規性の棚卸し

> 原本: scratchpad/deep-dives/failure-modes-and-finance.md Part2/3。

## 1. 商用の現況

| 製品 | 強い機構 | 限界 |
|---|---|---|
| Hebbia (Matrix) | **文単位引用を全事実に付与・引用グラフ・監査証跡**(citation-first) | 社内文書(データルーム)中心。**公開Web探索・外部証拠との突合が弱い** |
| AlphaSense DR | 5億文書上で全出力を原文の該当文までトレース | 「市場が何を言っているか」中心。DDチェックリスト網羅ではない |
| Rogo | 投資銀行ワークフロー特化 | 引用は response-level 止まり(文単位でない) |
| Harvey | M&A **法務**DDで最深(10万人超の弁護士) | 埋没条項の見落とし事例。構造化タスク以外は上級弁護士必須 |
| StackAI等のPE向け | **チェックリスト駆動は商用化済み**: DDQ取込→証拠付き回答→未回答をIRL化 | データルーム内処理。外部証拠との突合・探索なし |

学術: 買収DDのLLM適用は**法務DDに偏在**。商業/事業DD(市場・競合・事業計画の検証)を
対象とした査読付き研究は実質見つからず(不在の証明は不能だが多方向検索で不在)。
金融DRAベンチは急増(FinDeepResearch / FinSearchComp / Herculean / ICBCBench)。

## 2. 新規性の正直な棚卸し(優越証明で「新規」と主張してよい範囲)

**主張してはいけない(既にやられている)**:
1. 証拠の出所追跡そのもの(Hebbia/AlphaSense 商用確立、学術は AAR 標準 2602.13855 が定式化)
2. チェックリスト駆動DD(複数ベンダー商用化)
3. 証拠充足度ベースの停止(evidence-aware termination 提案済み 2604.24978)
4. プロセス監査型評価(DeepHalluBench 等が確立しつつある)

**主張できる(公開情報上の空白)**:
- **FM-1〜15 を網羅的に機構で塞ぎ、閉塞を検証可能にする統合設計**(個別対策は存在、
  統合の閉塞証明を掲げる製品・論文は未確認)
- **事業DD(commercial DD)特化**: 学術は法務に、商用はデータルーム内に偏在。
  **「公開Web証拠 × データルーム証拠の突合を監査可能に行う事業DD」はほぼ空白**
- **敵対的情報環境の明示的想定**(FM-8: 対象会社側の汚染動機)をDDで機構的に扱う設計

注意: AAR 標準(2602.13855)は我々の監査設計と思想が近い。**競合でなく規格として
乗る**(準拠を明示し差分を言う)のが正しい扱い。Hebbia/Harvey の内部ロードマップは
不可視 — 上記は「公開情報上の空白」にすぎないことを常に付記する。

## 3. 優越証明への接続

- Marlin/GDR は汎用リサーチであり、上の商用勢はデータルーム内が主戦場。
  **「社名だけで外部から証拠構造を立ち上げ、データルーム証拠(売り手の主張)と
  突合する」**ポジションは、両者のどちらの主戦場でもない
- ゆえに PO-1(機構被覆)は Marlin/GDR に対して行い、Hebbia 等は
  「隣接領域の確立済み機構(文単位引用等)を我々も満たしている」ことの確認に使う
