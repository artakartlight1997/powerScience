---
doc_id: survey-02-sakana-lineage
title: "Sakana の技術系譜 — AB-MCTS / AI Scientist / RSI / EDINET-Bench"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: survey
language: ja
tags: [sakana, ab-mcts, treequest, ai-scientist, evolutionary, rsi, edinet]
confidence: medium-high
primary_sources: [S-007, S-008, S-009, S-010, S-011, S-012, S-013]
contributes_to: [architecture, search, evaluation, japan-data]
---

# 02. Sakana の技術系譜

Marlin を理解するには、その下に積まれた5〜6年分の研究系譜を見る必要がある。
**要点は「Sakana は一貫して『大きくする』ではなく『組み合わせる／進化させる』に賭けている」こと。**

## 1. AB-MCTS（Adaptive Branching MCTS）— Marlin の中核

- 論文: *Wider or Deeper? Scaling LLM Inference-Time Compute with Adaptive Branching Tree Search*（arXiv:2503.04412）`[S-008]`
- 実装: **TreeQuest**（Apache-2.0, SakanaAI/treequest）`[S-009]`
- NeurIPS 2025 Spotlight `[S-005]`

### 何を解いたか

推論時スケーリングには2系統がある。

| 系統 | やること | 弱点 |
|---|---|---|
| 並列反復サンプリング（Best-of-N, Self-Consistency） | 幅を取る＝多様な回答を大量生成 | 深掘り（誤りの修正）ができない |
| 逐次改良（Reflexion, Self-Refine） | 深さを取る＝1本の回答を直し続ける | 初手が悪いと抜け出せない |

AB-MCTS は **「幅か深さか」をノードごとに動的決定**する。
具体的には MCTS を **適応的分岐** ＋ **Thompson Sampling による確率的選択** で拡張する `[S-010]`。
既存 MCTS は行動空間が固定だが、LLM は「新しい子ノードをいくらでも生成できる」ため、
「既存の子を選ぶ」と「新しい子を作る」を同じ確率モデル上で比較できるようにしたのが本質。

- **ABMCTS-A**: ノード集約（GEN ノード）を用いた適応分岐 `[S-010]`
- **ABMCTS-M**: PyMC による混合モデル（階層ベイズ）を用いる版 `[S-010]`

### Multi-LLM AB-MCTS（＝集合知）

さらに **「どのモデルを呼ぶか」自体を探索の一次元にする**。
OpenAI / Google / DeepSeek 等のフロンティアモデルを協調させ、試行錯誤させる `[S-010]`。

**成果**: ARC-AGI-2 で **39.2% の solve rate**。単一フロンティアモデル比で **+15pt 以上** `[S-010][S-011]`。
TreeQuest 紹介記事では「マルチモデルチームが単体 LLM を約30%上回る」とも報じられている `[S-011]`。

### Integral Prism への含意

- ✅ **採用すべき**: 幅/深さの動的配分、モデル選択の探索化、Thompson Sampling による予算配分。
- ⚠️ **そのままでは効かない**: AB-MCTS の成果が出ているのは **ARC-AGI-2 / コード生成＝機械検証可能な報酬がある領域**。
  投資リサーチには自明な報酬がない。**報酬設計を持ち込まないと、AB-MCTS は「もっともらしさの最大化」に堕ちる**。
  → 07（検証）と 11（差別化）で扱う本プロジェクトの中心論点。

## 2. The AI Scientist（v1 / v2）— ワークフロー骨格

- v1: アイデア生成 → 実験 → 論文執筆 → 査読、までの完全自動化 `[S-012]`
- v2: *Workshop-Level Automated Scientific Discovery via Agentic Tree Search*（arXiv:2504.08066）`[S-012]`
  → v1 の弱点（テンプレ依存）を、**エージェント的木探索**と実験マネージャで置換
- 2026-03-26 **Nature 掲載** `[S-007]`

**含意**: Marlin の「仮説 → 調査 → 統合 → 自己レビュー」ループは、ここから来ている。
つまり Marlin は *科学の型* をビジネスリサーチに移植した製品である。
逆に言えば、**投資意思決定固有の型（デューデリの型、IC の型、反証の型）は移植されていない**。`C`

## 3. 進化・自己改善の系譜

| 研究 | 内容 | IP への示唆 |
|---|---|---|
| **Evolutionary Model Merge** | 進化計算で複数モデルを統合し、特化モデルを作る `[S-013]` | 顧客固有（ファンド固有）の特化を、学習なしで作る発想の源 |
| **ShinkaEvolve** | オープンエンドかつサンプル効率の良いプログラム進化 `[S-014]` | 「探索の効率」自体を最適化する系譜 |
| **ALE-Agent** (2025) | AtCoder Heuristic Contest 058 で **804人中1位** `[S-007]` | 最適化問題での実証。報酬が明確な領域での強さ |
| **Digital Red Queen** (2026, MIT 共同) | Core War で LLM が敵対的に相互進化。約250世代で人間設計プログラムを常時撃破 `[S-015]` | **敵対的共進化＝「反証役」の自動強化**。IP のレッドチーム設計に直結 |
| **Continuous Thought Machines** | ニューロン同期のダイナミクスで解く新アーキテクチャ `[S-014]` | 直接は無関係 |
| **Text-to-LoRA** | テキスト記述から LoRA アダプタを生成するハイパーネットワーク `[S-014]` | 「案件記述 → 専門家アダプタ生成」の将来オプション |
| **RSI Lab**（2026-06 設立、東京） | AI 開発プロセス自体を AI で再設計。共同創業に Llion Jones `[S-007]` | 長期戦略。負の結果も含め公開する方針 |

## 4. EDINET-Bench — 日本の開示データという伏兵

Sakana は **EDINET-Bench**（有価証券報告書ベースの日本語金融ベンチマーク）を公開している `[S-016]`。

- 2014–2024 の **約4万件以上**の有価証券報告書を利用
- 全タスクにラベルが自動付与され、**データセットの更新・拡張が可能**な設計

**含意（重要）**:
1. Sakana は **日本の開示データを既に触っている**。日本市場での「金融特化」は無風地帯ではない。
2. 同時に、**EDINET/XBRL は構造化の難所**が知られている（タクソノミの企業別拡張、表構造、注記の非定型性）`[S-017]`。
   ここは**エンジニアリングの堀が立つ領域**であり、汎用 DR エージェントが最も苦手とする部分。
3. 有報は「XBRL（構造化）＋ MD&A・リスク情報（非構造化）」の**ハイブリッド文書**であり `[S-017]`、
   数値と物語を突き合わせる推論（＝投資分析そのもの）の教材になる。

## 5. 参考（出典）

`[S-007]` Sakana AI RSI Lab https://sakana.ai/rsi-lab/ ／ the-decoder 記事
`[S-008]` arXiv:2503.04412 *Wider or Deeper?* https://arxiv.org/abs/2503.04412
`[S-009]` SakanaAI/treequest https://github.com/SakanaAI/treequest
`[S-010]` Sakana AI "Inference-Time Scaling and Collective Intelligence for Frontier AI" https://sakana.ai/ab-mcts/
`[S-011]` VentureBeat "Sakana AI's TreeQuest…" https://venturebeat.com/ai/sakana-ais-treequest-deploy-multi-model-teams-that-outperform-individual-llms-by-30
`[S-012]` arXiv:2504.08066 *The AI Scientist-v2* https://arxiv.org/pdf/2504.08066
`[S-013]` Sakana AI Evolutionary Model Merge（各種解説）
`[S-014]` Sakana AI publications https://pub.sakana.ai/
`[S-015]` *Digital Red Queen: Adversarial Program Evolution in Core War with LLMs* https://arxiv.org/html/2601.03335v1
`[S-016]` Sakana AI EDINET-Bench https://sakana.ai/edinet-bench/
`[S-017]` EDINET DB「日本の有価証券報告書 XBRL を構造化するときに直面する4つの課題」 https://edinetdb.jp/blog/xbrl-japan-securities-reports-structuring
