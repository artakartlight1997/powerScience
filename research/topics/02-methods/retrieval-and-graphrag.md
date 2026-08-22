---
doc_id: t-retrieval-graphrag
title: "検索と知識グラフ — 局所検索と大域センスメイキングの二層"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [rag, graphrag, hipporag, raptor, lightrag, knowledge-graph, temporal]
confidence: medium-high
primary_sources: [S-047, S-048, S-049]
related_topics: [t-data-sources, t-context-engineering, t-memory-continual-learning]
contributes_to: [retrieval-architecture]
---

# 検索と知識グラフ

## 1. 手法の地図

| 手法 | 中核アイデア | 適所 |
|---|---|---|
| **RAPTOR** `[S-047]` | クラスタリング＋要約による**階層ツリー**。チャンク検索から構造的推論へ | 長文書の俯瞰 |
| **GraphRAG**（Microsoft）`[S-047]` | LLM がエンティティ KG を構築 → **入れ子コミュニティに分割** → 各コミュニティをボトムアップ要約 → 階層要約木で**大域センスメイキング** | 「この業界で何が起きているか」型 |
| **HippoRAG / HippoRAG2** `[S-048]` | 要約ではなく **Personalized PageRank** で知識統合。dense-sparse 併用、**query-to-triple マッチ**、シードノード重みの最適化 | 連想的な多段ホップ |
| **HiRAG / ArchRAG** `[S-047]` | 階層コミュニティ要約の発展 | 大規模コーパス |
| **LightRAG / MiniRAG / LinearRAG** `[S-047]` | 構築コスト削減、**二層検索**、トポロジ強化探索、テキスト＋エンティティの統合索引 | 実運用の現実解 |
| **TagRAG / MemGraphRAG / LegalGraphRAG** | タグ誘導・記憶型・法務特化の派生（2026） | ドメイン適用 |

## 2. 「全部グラフにする」は誤り

GraphRAG がベクタ RAG に明確に勝つのは **大域的な要約・横断的センスメイキング**のとき `[S-049]`。
局所的なファクト検索は**ベクタ / BM25 の方が安く速い** `[S-049]`。

## 3. IP の二層設計

投資リサーチの問いは、性質の異なる二層に分かれる。**同じ索引で解こうとしない。**

| 層 | 問いの例 | 手法 |
|---|---|---|
| **局所（ファクト）** | 「FY24 の売上総利益率は」「この契約の解約条項は」「CoC 条項の有無」 | ベクタ / BM25 / **XBRL 直参照** ＋ 数値再計算 |
| **大域（センスメイキング）** | 「この市場の勝ち筋は誰にあるか」「なぜこのロールアップは失敗しうるか」 | **GraphRAG 系のコミュニティ要約** |

## 4. 投資領域固有の要求 — 時間つき知識グラフ

> **「2023年のガイダンス」と「2026年の実績」を同一視した瞬間に、分析は死ぬ。**

必要な属性:

```
Node   : 企業 / 人物 / 製品 / 契約 / 規制 / イベント
Edge   : 供給する / 競合する / 出資する / 訴訟中 / 役員兼任 / 依存する
属性   : valid_from, valid_to, asserted_at（誰がいつそう言ったか）, source_id, confidence
```

- **主張の時点**（誰がいつ言ったか）と**事実の有効期間**を分けて持つ
- **改訂履歴**を持つ（決算修正、ガイダンス下方修正はそれ自体がシグナル）
- **point-in-time 再現**ができる（→ [t-ip-evaluation-design](../03-evaluation/integral-prism-evaluation-design.md) の反実仮想 DD に必須）

## 5. 構築コストの現実

GraphRAG は構築が高い。2026年の潮流は **構築の軽量化**（LightRAG, MiniRAG, LinearRAG）`[S-047]`。
IP では以下の割り切りを推奨 `C`:

1. **案件単位でグラフを作る**（全世界のグラフは作らない）
2. **公開開示データ由来の骨格グラフ**（企業・役員・株主・主要取引先）は共通資産として持つ
3. 案件固有の非公開文書は**案件グラフ**に閉じる（MNPI 対応）

## 6. 出典

- `[S-047]` *Towards Practical GraphRAG* arXiv:2507.03226 ／ RAPTOR ／ LightRAG ／ MiniRAG ／ LinearRAG arXiv:2510.10114 ／ TagRAG arXiv:2601.05254
- `[S-048]` *From RAG to Memory*（HippoRAG2）arXiv:2502.14802
- `[S-049]` *RAG vs. GraphRAG: A Systematic Evaluation* arXiv:2502.11371 ／ VentureBeat "Stop graphing everything: When GraphRAG actually beats vector RAG"
