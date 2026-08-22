---
doc_id: survey-03-google
title: "Google Deep Research / DR API / AI co-scientist"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: survey
language: ja
tags: [competitor, google, gemini, deep-research, co-scientist, pricing]
confidence: medium-high
primary_sources: [S-018, S-019, S-020, S-021, S-022, S-023]
contributes_to: [differentiation, cost-model, architecture]
---

# 03. Google Deep Research と AI co-scientist

## 1. Gemini Deep Research（プロダクト）

### アーキテクチャ（公開されている範囲）

| 要素 | 内容 | 確度 |
|---|---|---|
| ベース | Gemini（初出は 2.0 Flash Thinking、現在は Gemini 3.x 系）`[S-018][S-021]` | A |
| 計画 | **多段の調査計画を自分で立て、ユーザに提示して編集させる**（人が承認してから実行）`[S-018]` | A |
| 制御 | **単一エージェント構成**。RL によるファインチューニングで計画・適応能力を強化 `[S-019]` | B |
| 実行基盤 | **非同期タスクマネージャ**。プランナとタスクモデルの間で**共有状態**を保持し、途中失敗を全体再実行なしに回復 `[S-018]` | B |
| 文脈 | 100万トークン級の長文脈 ＋ **RAG アンサンブル**で継続性とフォローアップを担保 `[S-018][S-019]` | B |
| UX | 開始後はアプリを閉じてよく、完了時に通知（真の非同期）`[S-018]` | A |

**設計思想の要約**: Sakana が「木探索でマルチモデルを束ねる」のに対し、Google は
**「単一の強いモデルを RL で鍛え、非同期インフラで長時間安定に回す」**。
アルゴリズムではなく **インフラと分布（Workspace/検索）** を堀にしている。`B`

### Deep Research API（2026-04-21 提供開始）

| 項目 | 内容 |
|---|---|
| モデル | `deep-research-preview-04-2026`（標準, **約 $2/task**）、`deep-research-max-preview-04-2026`（**約 $5/task**）`[S-020]` |
| 実体 | Gemini 3.1 Pro を標準レート（in $2.00/1M, out $12.00/1M）で使用。**エージェント層に上乗せなし** `[S-020]` |
| 検索 | Google Search グラウンディングが既定 ON。**標準80クエリ / Max 160クエリ**、$14/1K → 1 run あたり $1.12〜$2.24 `[S-020]` |
| キャッシュ | 暗黙キャッシュが入力トークンの **50〜70%** をカバー。これがエージェントループを安価に保つ主因 `[S-020]` |
| 提供形態 | **Interactions API**（`generate_content` ではない）、**非同期のみ**、有料ティア限定 `[S-020][S-021]` |

> **単価比較（重要）**
> | | 1回の実行コスト | 想定所要 |
> |---|---|---|
> | Gemini DR API（標準/Max） | **$2 / $5**（≒ ¥300 / ¥800） | 数分〜数十分 |
> | Sakana Marlin | **≒ ¥9,800**（100クレジット換算）`[S-004]` | 最大8時間 |
>
> **10〜30倍の価格差**。ここに Integral Prism の価格ポジショニングの空白がある（→10）。
> 「Google と同じ価格帯で戦う」は自殺。「Marlin より高い」も正当化が要る。
> 正当化の唯一の道は **『意思決定に耐える証拠と較正』を売ること**（→11）。

## 2. AI co-scientist（Google DeepMind, Nature 2026）

Gemini DR とは別系統の、**マルチエージェント科学仮説生成システム** `[S-022][S-023]`。
Integral Prism にとっては Gemini DR より **こちらの方が設計的に重要**。

### 構成

```
      ┌─ Generation Agent    : 仮説を生成
      │
      ├─ Reflection Agent    : 批判・レビュー
      │
Supervisor ─ Ranking Agent   : ペアワイズ比較で「討論」させ、勝敗を Elo に反映
      │
      ├─ Evolution Agent     : 上位仮説を改良・交配
      │
      ├─ Proximity Agent     : 仮説空間の重複排除・近傍構造化
      │
      └─ Meta-review Agent   : 全体の傾向を抽出し、次ラウンドの生成にフィードバック
```

- **generate → debate → evolve** のサイクルを回す `[S-022]`
- **トーナメント＋Elo レーティング**で仮説を順位付け。番狂わせ（低 Elo が高 Elo に勝つ）ほどレート変動が大きい `[S-022]`
- **test-time compute を増やすほど Elo が単調に上がる**ことを実証 `[S-022][S-023]`
- Elo は仮説品質（専門家評価）と相関することを示している `[S-022]`

### Integral Prism への含意（大）

1. **「探索の報酬」を Elo（相対比較）で作るという解**。
   絶対スコアが定義できない領域（＝ビジネスリサーチ）で、**ペアワイズ比較なら定義できる**。
   これは Marlin の未公開部分（報酬設計）に対する、**公知かつ強力な代替解**である。
2. ただし LLM ペアワイズ判定には **位置バイアス・冗長性バイアス・権威バイアス**が実測されている `[S-058][S-059]`。
   Elo をそのまま使うと **「長くて自信満々な仮説」が勝つ**。→ 07 で対策を扱う。
3. **Proximity Agent（重複排除）と Meta-review（メタ学習）** は、
   長時間探索で必ず起きる「同じ結論の再発見」「同じ失敗の反復」への直接的な回答であり、
   本システムでも必須部品になる。

## 3. Sakana vs Google — 対比表

| 軸 | Sakana Marlin | Google Gemini DR | co-scientist |
|---|---|---|---|
| 制御構造 | 木探索（AB-MCTS） | 単一エージェント + 計画 | マルチエージェント + トーナメント |
| モデル | **マルチモデル（他社込み）** | 自社 Gemini 単一 | 自社 Gemini |
| 報酬 | 非公開（`D`） | RL で学習済みの方策 | **Elo（ペアワイズ討論）** |
| 実行時間 | 最大8時間 | 数分〜数十分 | 継続的 |
| 単価 | ≒ ¥9,800/run | $2〜$5/task | 研究用途 |
| ユーザ介入 | 少ない（`C`） | **計画の承認・編集** | 科学者との協働前提 |
| 堀 | 探索アルゴリズム＋顧客基盤 | **分布・インフラ・単価** | 研究ブランド |

**空白地帯**: 「マルチモデル × 明示的な報酬（反証ベース） × 人間との協働 × 監査可能」。
ここが Integral Prism の座標である。

## 4. 参考（出典）

`[S-018]` Gemini Deep Research 公式 https://gemini.google/overview/deep-research/
`[S-019]` *Deep Research Agents: A Systematic Examination And Roadmap* arXiv:2506.18096
`[S-020]` TokenCost "Gemini Deep Research pricing: cost per task 2026" https://tokencost.app/blog/gemini-deep-research-agent-cost
`[S-021]` Gemini API Deep Research docs https://ai.google.dev/gemini-api/docs/deep-research
`[S-022]` *Accelerating scientific discovery with Co-Scientist* (Nature, 2026) https://www.nature.com/articles/s41586-026-10644-y ／ arXiv:2502.18864
`[S-023]` Google Research Blog / DeepMind Blog: AI co-scientist https://research.google/blog/accelerating-scientific-breakthroughs-with-an-ai-co-scientist/
