---
doc_id: research-index
title: "Integral Prism リサーチ・インデックス"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
owner: artakartlight@gmail.com
project: integral-prism
doc_type: index
language: ja
tags: [index, survey, deep-research, agent, investment-research]
---

# Integral Prism / リサーチ・インデックス

仮称 **Integral Prism（インテグラル・プリズム）** — PE / ファンドの投資プロフェッショナル向け
「実益の大きいリサーチシステム」を設計するための、前段サーベイ一式。

> 本フォルダの目的は **アーキテクチャを決めることではない**。
> アーキテクチャ議論に入る前に、(a) 競合（Sakana Marlin / Google Deep Research 系）の実像、
> (b) 学術研究の到達点と未解決点、(c) 投資実務側の制約 を、根拠つきで棚卸しすることにある。

## 読む順番

| # | ファイル | 内容 | 主な読者 |
|---|---|---|---|
| 00 | [surveys/00-method-and-scope.md](surveys/00-method-and-scope.md) | 調査方法・信頼度の扱い・限界（**最初に読む**） | 全員 |
| 01 | [surveys/01-sakana-marlin.md](surveys/01-sakana-marlin.md) | Sakana Marlin の実像（製品・価格・アーキテクチャ推定） | 全員 |
| 02 | [surveys/02-sakana-lineage-abmcts.md](surveys/02-sakana-lineage-abmcts.md) | AB-MCTS / AI Scientist / RSI Lab — Sakana の技術系譜と戦略 | 技術 |
| 03 | [surveys/03-google-deep-research.md](surveys/03-google-deep-research.md) | Gemini Deep Research / DR API / AI co-scientist | 技術・事業 |
| 04 | [surveys/04-other-deep-research-systems.md](surveys/04-other-deep-research-systems.md) | OpenAI DR / Anthropic Research / Tongyi / STORM ほか | 技術 |
| 05 | [surveys/05-search-and-test-time-scaling.md](surveys/05-search-and-test-time-scaling.md) | 探索・推論時スケーリング・検証器・RL 探索エージェント | 技術 |
| 06 | [surveys/06-retrieval-memory-context.md](surveys/06-retrieval-memory-context.md) | 検索・知識グラフ・文脈工学・記憶と継続学習 | 技術 |
| 07 | [surveys/07-verification-attribution-calibration.md](surveys/07-verification-attribution-calibration.md) | 出典検証・幻覚・キャリブレーション・構造化分析技法 | 技術・実務 |
| 08 | [surveys/08-benchmarks-and-evaluation.md](surveys/08-benchmarks-and-evaluation.md) | ベンチマークと評価設計（何を測れば勝ちか） | 全員 |
| 09 | [surveys/09-finance-pe-domain.md](surveys/09-finance-pe-domain.md) | PE/VC デューデリ実務・データ源・規制 | 事業・実務 |
| 10 | [surveys/10-market-economics-and-moat.md](surveys/10-market-economics-and-moat.md) | 競合地図・単価構造・コモディティ化と堀 | 事業 |
| 11 | [surveys/11-implications-for-integral-prism.md](surveys/11-implications-for-integral-prism.md) | 各研究が本システムにどう効くか＝設計仮説の種 | 全員 |
| — | [notes/discussion-agenda.md](notes/discussion-agenda.md) | **議論すべき論点リスト（未決）** | 全員 |
| — | [notes/open-questions.md](notes/open-questions.md) | 未検証・要一次確認の宿題 | 全員 |

## メタデータ

後工程（設計文書生成・引用・自動更新）で使うため、機械可読メタデータを分離して置いている。

- [metadata/schema.md](metadata/schema.md) — フロントマター/参考文献のスキーマ定義
- [metadata/sources.json](metadata/sources.json) — 出典レジストリ（ID・URL・種別・信頼度・関連トピック）
- [metadata/taxonomy.json](metadata/taxonomy.json) — 能力タクソノミ（設計要素の分類軸）
- [metadata/claims.json](metadata/claims.json) — 本サーベイ内の主要な「事実主張」と根拠・確度
- [metadata/glossary.md](metadata/glossary.md) — 用語集

## 現時点の一行結論

> Marlin は「**長時間 × 木探索 × マルチモデル**」で勝負しており、Google DR は「**単一モデル×RL×低単価×分布**」で勝負している。
> どちらも **『出力＝レポート』を最終成果物とする設計** であり、
> 投資プロの実益（＝**意思決定の質と、後から検証できること**）に最適化されてはいない。
> Integral Prism の差別化仮説は「**レポート生成機ではなく、投資判断の反証可能な証拠構造を作る機械**」に置く。詳細は 11 番。
