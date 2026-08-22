---
doc_id: survey-06-retrieval-memory
title: "検索・知識グラフ・文脈工学・記憶と継続学習"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: survey
language: ja
tags: [rag, graphrag, hipporag, context-engineering, compaction, memory, continual-learning]
confidence: medium-high
primary_sources: [S-047, S-048, S-049, S-050, S-051, S-052, S-053]
contributes_to: [architecture, knowledge-asset, long-horizon]
---

# 06. 検索・知識・文脈・記憶

## 1. 構造化検索（GraphRAG 系）

| 手法 | 中核アイデア | 適所 |
|---|---|---|
| **RAPTOR** | クラスタリング＋要約による**階層ツリー**。チャンク検索から構造的推論へ `[S-047]` | 長文書の俯瞰 |
| **GraphRAG**（Microsoft） | LLM がエンティティ KG を構築 → **入れ子コミュニティに分割** → ボトムアップ要約木 → **グローバルなセンスメイキング** `[S-047]` | 「この業界で何が起きているか」型の問い |
| **HippoRAG / HippoRAG2** | 要約ではなく **Personalized PageRank** で知識を統合。dense-sparse 併用、query-to-triple マッチ `[S-048]` | 連想的な多段ホップ |
| **LightRAG / MiniRAG / LinearRAG** | 構築コスト削減、二層検索、トポロジ強化探索 `[S-047]` | 実運用の現実解 |

**実務的な注意**: 「全部グラフにする」は誤り。
GraphRAG がベクタ RAG に明確に勝つのは **グローバルな要約・横断的センスメイキング**のとき `[S-049]`。
局所的なファクト検索はベクタ/BM25 の方が安く速い。

**IP への含意**:
投資リサーチの問いは二層に分かれる。
- **局所**: 「FY24 の売上総利益率は？」「この契約の解約条項は？」→ 通常の検索＋数値抽出
- **大域**: 「この市場の勝ち筋は誰にあるか」「なぜこのロールアップは失敗しうるか」→ **グラフ／コミュニティ要約**
両者を **同じ索引で解こうとしない**こと。

さらに投資領域固有の要求として、**時間軸を持つ KG（誰がいつ何を言ったか、いつ改訂されたか）**が要る。
「2023年のガイダンス」と「2026年の実績」を同一視した瞬間に、分析は死ぬ。

## 2. 文脈工学（Context Engineering）— 長時間実行の生命線

- **Context rot**: 入力トークン量が増えるほど性能が劣化する現象。
  Claude Sonnet 4 / GPT-4.1 / Qwen3-32B / Gemini 2.5 Flash など主要モデル横断で観測 `[S-050]`
  → **「窓が埋まったから壊れる」のではなく、長い文脈そのものが推論を悪くする**
- 対策の定石 `[S-050][S-051]`:
  1. **compaction / 要約圧縮**（履歴を状態に畳む）
  2. **構造化ノートテイキング**（文脈外のファイルに自分でメモし、必要時に読み直す）
  3. **targeted retrieval**（全部載せない）
  4. **tool scoping**（使えるツールを絞る）
  5. **ACE (Agentic Context Engineering)**: 文脈を「進化するプレイブック」として**差分更新**する
- Anthropic の内部評価: **context editing だけで +29%**、**memory tool 併用で +39%** `[S-050]`
- **IterResearch/Heavy Mode**（→04）: 毎ラウンド**ワークスペースを再構築**する `[S-030]`
- **CompactionRL / Slipstream / FoldAct / Self-GC**: 圧縮の学習・**圧縮の妥当性検証**・安定化 `[S-051]`

**IP への含意（設計原則 #8）**:
8時間走らせる系では、**「何を忘れるか」の設計が「何を調べるか」と同じくらい重要**。
そして圧縮は**検証されるべき対象**である（Slipstream の問題意識）。
本システムでは「圧縮＝証拠の要約」なので、**圧縮時に出典 ID を失わない構造**が必須。
→ 文脈に載せるのは要約、**根拠は外部ストアの ID 参照**、という分離。

## 3. 記憶と継続学習 — ファンドの資産化

- **AgentCL** `[S-052]`: 言語エージェントの継続学習を厳密に評価する枠組み
- **When Continual Learning Moves to Memory** `[S-052]`:
  外部記憶に経験を貯めれば継続学習が解ける…**わけではない**。
  安定性-可塑性ジレンマは**検索段階に再出現**する（古い経験と新しい経験が限られた文脈を奪い合う）
- **Agent KB** `[S-053]`: 過去ワークフローを**汎化可能な経験単位**に構造化し、ドメイン/アーキテクチャ横断で再利用
- **Case-Based Learning (CBL)** `[S-053]`: 実タスクの各実行を**学習可能なケース**として蓄積。
  固定ドメイン知識モジュール（インタフェース仕様・制約）と分離
- **Dynamic Cheatsheet / ExpRAG / ReMem**: 戦略・スニペット・抽象を再利用 `[S-052]`

**IP への含意（設計原則 #9 — 事業上の堀に直結）**:
PE ファンドにとっての本当の資産は **「過去の案件で何を見て、何を外したか」**。
これを**ケースベース記憶**として構造化すれば：
- 案件横断の「よくある死因（failure archetype）」ライブラリが育つ
- 新規案件で **「この形は 2023 年の××案件と同型。あの時の見落としは△△」** が出せる
- **これは Marlin にも Google にも作れない**（顧客固有データの累積であり、モデル層の資産ではない）

ただし研究が警告する通り、**記憶は増やすほど検索が濁る**。
→ 記憶は「量」ではなく **「意思決定に効いた事実だけを、反証結果つきで残す」** 設計にする。

## 4. 参考（出典）

`[S-047]` GraphRAG / RAPTOR / LightRAG 系レビュー（*Towards Practical GraphRAG* arXiv:2507.03226 ほか）
`[S-048]` *From RAG to Memory: Non-Parametric Continual Learning for LLMs*（HippoRAG2）arXiv:2502.14802
`[S-049]` *RAG vs. GraphRAG: A Systematic Evaluation* arXiv:2502.11371 ／ VentureBeat "Stop graphing everything"
`[S-050]` Context engineering 2026 実務レビュー（Anthropic context editing/memory の内部評価値を含む）
`[S-051]` *CompactionRL* arXiv:2607.05378 ／ *Slipstream* arXiv:2605.08580 ／ *FoldAct* arXiv:2512.22733 ／ *Self-GC* arXiv:2607.00692
`[S-052]` *AgentCL* arXiv:2606.02461 ／ *When Continual Learning Moves to Memory* arXiv:2604.27003
`[S-053]` *Agent KB* arXiv:2507.06229 ／ *Transferable Expertise via Real-World Case-Based Learning* arXiv:2604.12717
