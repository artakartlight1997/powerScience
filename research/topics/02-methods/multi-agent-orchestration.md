---
doc_id: t-multi-agent-orchestration
title: "マルチエージェント・オーケストレーション — 勝てる条件"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [multi-agent, orchestration, parallelism, patterns, financial-documents]
confidence: medium-high
primary_sources: [S-028, S-029]
related_topics: [t-anthropic-research, t-failure-modes-mast, t-pe-dd-workflow]
contributes_to: [architecture, orchestration]
---

# マルチエージェント・オーケストレーション

## 1. 大原則

> **architecture follows task structure** `[S-028]`
> タスクが**独立並列スレッドに分解できるときにだけ**、マルチエージェントは勝つ。

分解できないタスクに multi-agent を被せると、**コストだけ増えて劣化する**。
「マルチエージェントだから偉い」は誤り。

## 2. オーケストレーション・パターン

金融文書処理での比較研究では、以下のパターンが整理されている `[S-029 関連]`:

| パターン | 形 | 適所 | 危険 |
|---|---|---|---|
| **逐次パイプライン** | A→B→C | 工程が固定的な処理 | 誤りが伝播する |
| **並列ファンアウト＋マージ** | ├─┬─┤ | 独立な調査対象 | マージ時の矛盾処理 |
| **階層型 supervisor-worker** | 中央集権 | 大半の DR タスク | supervisor がボトルネック |
| **反省的自己修正ループ** | A⇄A' | 品質改善 | 収束しない／自己満足 |

Anthropic Research は**階層型 supervisor-worker ＋ 引用専任パス**で構成されている `[S-028]`。
→ [t-anthropic-research](../01-competitors/anthropic-research-system.md)

## 3. 投資 DD における並列性の切り分け

| **独立並列にできる** | **逐次でなければならない** |
|---|---|
| 競合 N 社の財務分解 | バリュエーション前提の整合 |
| 各国・各規制領域の調査 | 仮説 → 反証 → 再仮説のループ |
| 複数の反証課題の個別検証 | 価格・条件への落とし込み |
| チャネル別・地域別の需要検証 | IC 向け結論の統合 |
| 契約書 N 件の条項抽出 | 条項間の相互作用の評価 |

**設計上の帰結**: IP は**二層**にする。
- **下層（並列）**: 反証課題ごとの独立検証エージェント群 — ここは大胆に並列化
- **上層（逐次・中央集権）**: 証拠の統合、矛盾の調停、確率の更新 — ここは単一の統制下に置く

理由は MAST が示す通り、無統制の分散は**誤りを最大17倍に増幅**し、
中央集権＋検証で**約4.4倍**に抑えられるため `[S-029]`。
→ [t-failure-modes-mast](failure-modes-mast.md)

## 4. 異質性の要請

**同じモデルの複製を並べない。** 役割ごとに以下を変える。

| 役割 | モデル | ツール | 権限 |
|---|---|---|---|
| 生成（仮説・調査） | 高性能 | 検索・ブラウザ | 原文取得は可、再計算は不可 |
| **検証** | **別ベンダ** | **原文取得・コード実行・DB** | **特権あり**（→ [t-verifier-design](verifier-design.md)） |
| 反証（レッドチーム） | 高性能・別プロンプト系 | 検索 | 生成の出力を見るが、生成の理由は見ない |
| 統合・調停 | 高性能 | 少数 | 全体を見る唯一の役 |
| 引用付与 | 軽量 | 原文取得 | 文章を書き換えない |

## 5. 出典

- `[S-028]` https://www.anthropic.com/engineering/multi-agent-research-system
- `[S-029]` MAST arXiv:2503.13657 ／ 金融文書処理のオーケストレーション比較 arXiv:2603.22651
