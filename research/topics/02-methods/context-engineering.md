---
doc_id: t-context-engineering
title: "文脈工学 — context rot と圧縮の設計"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [context-rot, compaction, note-taking, tool-scoping, iterresearch, ace]
confidence: medium-high
primary_sources: [S-050, S-051, S-030]
related_topics: [t-tongyi-deepresearch, t-memory-continual-learning, t-failure-modes-mast]
contributes_to: [long-horizon-architecture]
---

# 文脈工学（Context Engineering）

**8時間走らせる系では、「何を忘れるか」の設計が「何を調べるか」と同じくらい重要。**

## 1. context rot

- 入力トークン量が増えるほど性能が劣化する現象。
  **Claude Sonnet 4 / GPT-4.1 / Qwen3-32B / Gemini 2.5 Flash** など主要モデル横断で観測 `[S-050]`
- **「窓が埋まったから壊れる」のではない。長い文脈そのものが推論を悪くする** `[S-050]`
  → 余裕があっても劣化する。「文脈が大きいからそのまま全部入れる」は誤り。

## 2. 対策の定石

| 手法 | 内容 |
|---|---|
| **compaction / 要約圧縮** | 履歴が上限に近づいたら要約し、圧縮サマリ＋直近の少量から再開 `[S-050]` |
| **構造化ノートテイキング** | モデルが**文脈外のファイルに自分でメモ**し、必要時に読み直す（永続メモリ）`[S-050]` |
| **targeted retrieval** | 全部載せず、必要な分だけ取りに行く |
| **tool scoping** | 使えるツールを役割ごとに絞る |
| **ACE（Agentic Context Engineering）** | 文脈を**進化するプレイブック**として項目単位で**差分更新**（全書き換えをしない）`[S-050]` |
| **IterResearch / Heavy Mode** | **毎ラウンド作業空間を再構築**する `[S-030]` → [t-tongyi-deepresearch](../01-competitors/tongyi-deepresearch.md) |

### 実測
Anthropic の内部評価 `[S-050]`:
- **context editing のみ： +29%**
- **context editing + memory tool： +39%**

## 3. 圧縮は「検証されるべき対象」

2026年の研究潮流は、圧縮そのものの信頼性に向かっている `[S-051]`。

| 研究 | 内容 |
|---|---|
| **CompactionRL**（arXiv:2607.05378） | 文脈圧縮を RL で学習する |
| **Slipstream**（arXiv:2605.08580） | **軌跡に接地した圧縮の妥当性検証**（圧縮で何が失われたかを検査する） |
| **FoldAct**（arXiv:2512.22733） | 長期探索エージェント向けの効率的・安定な context folding |
| **Self-GC**（arXiv:2607.00692） | 自己統治型の文脈管理 |

## 4. IP の設計要請

> **設計原則 P8: 長時間実行では「何を忘れるか」を設計し、圧縮時に出典 ID を失わない。**

```
文脈に載せるもの : 要約・現在の仮説状態・未解決の反証課題（小さく保つ）
外部ストアに置くもの: 全証拠（原文スパン、URL、取得時刻、スナップショットハッシュ）
                     ↑ 文脈からは ID 参照のみ
```

この分離により同時に達成されること:
1. context rot の回避
2. **監査可能性**（→ [t-regulation-compliance](../04-domain/regulation-and-compliance.md)）
3. **引用の機械検証**（→ [t-citation-attribution](../03-evaluation/citation-attribution.md)）
4. エージェント間の構造化受け渡し（→ [t-failure-modes-mast](failure-modes-mast.md)）

**逆に言えば**: 「要約して次のエージェントに自然言語で渡す」設計を採った瞬間に、
上記4つが同時に壊れる。ここは妥協点がない。

## 5. 出典

- `[S-050]` Context engineering 2026 実務レビュー群（Anthropic の context editing / memory tool 評価値を含む）
- `[S-051]` CompactionRL arXiv:2607.05378 ／ Slipstream arXiv:2605.08580 ／ FoldAct arXiv:2512.22733 ／ Self-GC arXiv:2607.00692
- `[S-030]` Tongyi DeepResearch（IterResearch / Heavy Mode）
