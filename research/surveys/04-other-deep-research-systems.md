---
doc_id: survey-04-other-dr
title: "その他の Deep Research システム — OpenAI / Anthropic / Tongyi / STORM ほか"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: survey
language: ja
tags: [openai, anthropic, tongyi, storm, open-source, multi-agent, human-in-the-loop]
confidence: medium-high
primary_sources: [S-026, S-027, S-028, S-029, S-030, S-031, S-032, S-033, S-034]
contributes_to: [architecture, orchestration, context, hitl]
---

# 04. その他の Deep Research システム

## 1. OpenAI Deep Research — 「学習で解く」派の極北

- **単一エージェント**構成。ブラウジングとデータ分析に最適化した o3 系モデル `[S-026]`
- **end-to-end 強化学習**：実タスク（ブラウザ＋Python）で多段軌跡の計画・実行・**バックトラック**を学習 `[S-026][S-027]`
- 中間ステップの人手監督なしに、探索戦略そのものをモデル内部に獲得させた

**含意**: 探索を「外部アルゴリズム（AB-MCTS）」に置くか「モデル内部（RL）」に置くかは、業界の二大路線。
Integral Prism は **どちらでもない第三の選択（外部化された明示的な証拠構造）** を取れる余地がある。
理由は簡単で、**我々はモデルを学習させる資源を持たないし、持つべきでもない**（モデルはコモディティ化する）。

## 2. Anthropic Research（Claude）— オーケストレータ/ワーカ型の実装知

構成 `[S-028]`：

```
LeadResearcher（Opus級）
  ├─ Subagent 1 (Sonnet級)  ┐
  ├─ Subagent 2             ├─ 並列に検索・評価し、発見を返す
  ├─ Subagent 3〜5          ┘
  ↓ 統合・追加調査の要否判断
CitationAgent  ← 出典位置の付与を専任で行う別パス
```

実測・教訓 `[S-028]`：

| 事実 | 数値 |
|---|---|
| マルチエージェント > 単一 Opus（社内リサーチ評価） | **+90.2%** |
| 複雑クエリのリサーチ時間短縮 | **約90%減** |
| 失敗要因の筆頭 | **プロンプト設計**（言い回しの差が効率を決定） |
| 初期の典型的失敗 | 簡単なクエリに過剰なサブエージェント生成、重複検索、協調不全 |

**最重要の教訓**: *architecture follows task structure* —
**タスクが独立並列スレッドに分解できるときにだけ**、マルチエージェントは勝つ。
分解できないタスクに multi-agent を被せると、コストだけ増えて劣化する。

**含意（IP 設計原則 #1）**: 「マルチエージェントだから偉い」は誤り。
投資リサーチのどの部分が**本当に独立並列**なのかを、先に切り分けねばならない。
（例: 「競合5社の財務分解」は並列。「バリュエーション前提の整合」は逐次。）

### 併せて読むべき負のエビデンス — MAST

*Why Do Multi-Agent LLM Systems Fail?*（arXiv:2503.13657, NeurIPS 2025）`[S-029]`

- 7フレームワーク・**1,600超の実行トレース**を注釈し、**14の失敗モード**を3カテゴリに整理
  - **仕様/設計の欠陥 41.8%**（役割の曖昧さ、分解の失敗、停止条件の欠落）
  - **エージェント間の不整合 36.9%**（情報伝達の断絶）
  - **検証の失敗 21.3%**（出力検証の不足、誤りの伝播）
- 未協調のマルチエージェントは誤りを **最大17倍**増幅しうる。中央集権＋検証で **約4.4倍**に抑制 `[S-029]`

**含意（IP 設計原則 #2）**: **停止条件と検証を、アーキテクチャの一級市民にする**。
失敗の 6 割は「賢さ」ではなく「仕様と停止」の問題。

## 3. Tongyi DeepResearch（Alibaba, オープンソース）— 文脈管理の到達点

- 30.5B 総パラメータ / **3.3B アクティブ**（MoE）`[S-030]`
- **IterResearch / Heavy Mode**: 長い文脈を積み上げず、**ラウンドごとにワークスペースを再構築**する
  → 各ラウンドで「情報収集を続けるか、統合して答えるか」を判断。ノイズ蓄積を抑える `[S-030]`
- ReAct モード（素の thought/action/observation）も併存

ベンチマーク（30B で）`[S-030]`:
| HLE | BrowseComp | BrowseComp-ZH | WebWalkerQA | GAIA | xbench-DS | FRAMES |
|---|---|---|---|---|---|---|
| 32.9 | 43.4 | 46.7 | 72.2 | 70.9 | 75.0 | 90.6 |

**含意**: オープンモデルで **クローズドの DR に肉薄**できる。
→ ユーザの言う「オープンモデルのコモディティ化」は既に現実。
→ **モデル層に価値を置く設計は禁じ手**。IP は「モデルを差し替えても壊れない」構造でなければならない。

**IterResearch の思想は IP に直輸入すべき**: 文脈を「積む」のではなく「毎ラウンド再構成する」。
これは監査可能性（各ラウンドの入力が明示的）とも相性が良い。

## 4. STORM / Co-STORM（Stanford）— 「多視点」の作り方

- **STORM** = Synthesis of Topic Outlines through Retrieval and Multi-perspective question asking `[S-031]`
  1. 類似トピックの既存記事を調査して **視点（perspective）を発見**
  2. 各視点の「ライター」と「専門家」の **模擬対話**を回して質問を深掘り
  3. アウトライン生成 → 出典つき長文執筆
- **Co-STORM** `[S-031]`: 複数 LLM 専門家＋人間が参加する **協調的談話プロトコル**（ターン管理方針つき）と、
  発見を蓄積する動的マインドマップ

**含意（IP 設計原則 #3）**: 質問の質は **視点の多様性**から生まれる。
投資リサーチにおける「視点」は自動発見ではなく、**実務由来の型**で与えられる
（買い手/売り手/競合/顧客/規制当局/退職者/債権者/労働組合…）。ここは我々のドメイン知識で殴れる。

## 5. 人間との協働（mixed-initiative）— 空いている領域

- **InterDeepResearch** `[S-032]`: 既存 DR はユーザの介入モデルが貧弱。
  ユーザは**リアルタイムに研究方向を操舵したい**という要求を明確に持つ
- **Interaction as Intelligence**（arXiv:2507.15759）`[S-033]`: 深いリサーチは人間-AI 協働として設計すべき
- **IntentRL** `[S-034]`: オープンエンドな DR における **autonomy-interaction ジレンマ**を定式化。
  潜在意図の明確化を **POMDP** として扱い、RL で「いつ聞くか」を学習
- 実務側でも 2026 年時点で HITL は「オプションの安全網」ではなく**信頼できる AI の中核機能**という位置づけ `[S-035]`

**含意（IP 設計原則 #4）**:
「8時間放置」は売り文句としては強いが、**投資プロは途中で口を出したい**。
むしろ **「介入点が設計されている」ことを売る**方が実益が大きい。
介入点の候補: ①仮説集合の承認 ②反証課題の優先順位 ③一次情報の追加投入 ④結論の確度の上書き。

## 6. 系統整理（DR エージェントのタクソノミ）

*Deep Research Agents: A Systematic Examination And Roadmap*（arXiv:2506.18096）`[S-019]` に従うと：

| 軸 | 分類 | 代表 |
|---|---|---|
| ワークフロー | **静的**（人が設計した固定パイプライン） | STORM, GPT-Researcher |
| | **動的**（実行時に計画が変わる） | OpenAI DR, Marlin, Gemini DR |
| 情報取得 | API ベース検索 | 多く |
| | ブラウザ操作ベース探索 | OpenAI DR, BrowseComp 系 |
| エージェント構成 | 単一 | OpenAI DR, Gemini DR |
| | マルチ | Anthropic Research, co-scientist, Marlin(木＝準マルチ) |
| ツール | コード実行 / マルチモーダル / **MCP** | — |

**IP の位置**: 動的ワークフロー × マルチ（ただし MAST を踏まえ中央集権＋検証） × API/ブラウザ両用 × MCP 前提。

## 7. 参考（出典）

`[S-026]` OpenAI "Introducing deep research" https://openai.com/index/introducing-deep-research/
`[S-027]` Sequoia Podcast "Training AI Agents End-to-End"（OpenAI DR チーム）
`[S-028]` Anthropic Engineering "How we built our multi-agent research system" https://www.anthropic.com/engineering/multi-agent-research-system
`[S-029]` *Why Do Multi-Agent LLM Systems Fail?* arXiv:2503.13657
`[S-030]` Tongyi DeepResearch 技術報告 arXiv:2510.24701 / https://tongyi-agent.github.io/blog/introducing-tongyi-deep-research/
`[S-031]` stanford-oval/storm https://github.com/stanford-oval/storm
`[S-032]` *InterDeepResearch* arXiv:2603.12608
`[S-033]` *Interaction as Intelligence: Deep Research With Human-AI Partnership* arXiv:2507.15759
`[S-034]` *IntentRL* arXiv:2602.03468
`[S-035]` HITL 2026 実務レビュー各種
