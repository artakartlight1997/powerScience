---
doc_id: t-recursive-self-improvement
title: "再帰的自己改善（RSI）— DGM / SIFT / Red Queen / AlphaEvolve / ADAS / GEPA"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [rsi, self-improvement, darwin-godel-machine, alphaevolve, adas, gepa, evolution, evaluator]
confidence: medium-high
primary_sources: [S-092, S-093, S-094, S-095, S-096, S-097, S-098]
related_topics: [t-sakana-evolution-rsi, t-reward-hacking, t-memory-continual-learning, t-verifier-design]
contributes_to: [architecture, moat, roadmap]
---

# 再帰的自己改善（RSI）

**2026年最大の研究潮流の一つであり、Sakana が組織ごと賭けている領域。**
IP にとっては「自己改善する DD システム」の可能性と、その**危険性**の両方を規定する。

## 1. 何が起きているか（分野の状況）

- 大規模サーベイは **2024–2026 の arXiv 1,250本**を、2軸で整理している `[S-096]`:
  - **何を改善するか** — ①デプロイ時の振る舞い ②学習による方策 ③**評価器** ④研究プロセスそのもの
  - **ループの閉じ具合** — human-in-the-loop 〜 完全閉ループ
- 別のサーベイは **what to evolve / when to evolve / how to evolve** の3次元で整理 `[S-096]`
- 系譜: **ultraintelligent machine → Gödel machine** →
  LLM 時代では「コード改善スキャフォールドの改善」「プロンプトと変異プロンプトの共進化」「自己設計の書き換え」`[S-096]`
- 2026年の実例として **AlphaEvolve / Darwin Gödel Machine / STOP / self-rewarding LM** が挙げられ、
  いずれも**固定された自動評価信号に対して**コード・プロンプト・選好を改善している（無制限な自己改変ではない）`[S-106]`
- OpenAI は 2026-02-05 に GPT-5.3-Codex を出荷し、
  **「自分自身の創造に寄与した最初のモデル」**と説明している（初期版が自身の学習のデバッグを支援）`[S-106]` `B`

## 2. 主要システム

### (a) Darwin Gödel Machine（DGM, Sakana AI + UBC）`[S-092]`
自分自身のソースコードを反復的に改善するエージェント。
「Darwin」＝進化的探索、「Gödel」＝自己言及的な自己定義の書き換え。

| ベンチ | 変化 |
|---|---|
| **SWE-bench** | **20.0% → 50.0%** |
| **Polyglot** | **14.2% → 30.7%** |

**転移性が重要** `[S-092]`:
- Claude 3.5 Sonnet で最適化したエージェントが、**o3-mini や Claude 3.7 Sonnet でも性能向上**
- **Python タスクのみで誘導した変種が、Rust / C++ / Go でも改善**

→ **「改善されるのはモデルではなく、ツールとワークフロー」**であり、モデルを跨いで持ち運べる。
これは IP にとって決定的に重要（我々はモデルを学習させないが、**スキャフォールドは改善できる**）。

### (b) SIFT（MIT + Sakana AI, ICLR 2026）`[S-093]`
**RSI の律速は「評価コスト」である**と特定した研究。

- **ほとんどの評価を LLM-as-a-judge で代替**し、**上位にランクされたパッチにだけ高価なベンチマークを実行**する
- 結果（SWE-bench Verified の60タスク部分集合、gpt-4-mini 起点）:
  **51.7% → 61.7%（+11pt）を3ステップ未満で達成。総コスト $25 の API 費用と 15 CPU 時間**
- この最終スコアは、当時の最強オープンモデル（Kimi-K2-Thinking）を上回り、
  同一ハーネス上の Claude Opus 4 に匹敵する

**最重要の副次的発見** `[S-093]`:
> **judge の忠実度が決定的**。
> gpt-4.2 を judge にすると実ベンチ性能との **Pearson 相関 34%**、
> **gpt-4-nano では ほぼゼロ**。

→ 安い judge で回すと、**改善しているように見えて何も改善していない**。
→ [t-llm-judge-reliability](../03-evaluation/llm-judge-reliability.md) と
[t-reward-hacking](../03-evaluation/reward-hacking-and-proxy-gaming.md) に直結。

### (c) Red Queen Gödel Machine（RQGM, Cambridge ほか, 2026-06）`[S-094]`
**非定常な効用のもとでの RSI**。IP にとって**最も示唆的な研究**。

問題意識 `[S-094]`:
> 既存の自己改善手法は「**評価基準が定常である**」ことを前提にしている
> — 固定の検証器、ベンチマーク、ラベル付きデータが、エージェントが強くなっても有効であり続けるという前提。
> これは進化の中心的特徴、すなわち**環境も共に変わる**ことを無視している。

手法 `[S-094]`:
- 自己改善を**進化エポック**に区切り、**エポック内では評価器を凍結**して定常性を保証
  （標準的な自己改善の保証が局所的に成立する）
- **目的関数はエポック境界でのみ、原理的な効用遷移によって変化**する
- これにより、**進化する評価器・敵対的目的・動的効用**へ探索を開くことができる

結果 `[S-094]`:
- **安価な「進化したコードレビュアー」を加えるだけで**、
  先行 SOTA（HGM-H）を Polyglot 上で上回りつつ、**探索トークンを 1.35〜1.72倍削減**

→ **「レビュアー（＝反証役）を共進化させると、探索が安くなる」**という定量的証拠。
これは Sakana の Digital Red Queen（→ [t-sakana-evolution-rsi](../01-competitors/sakana-evolution-and-rsi.md)）と
同じ発想を、**自己改善の枠組みで形式化**したもの。

### (d) AlphaEvolve（Google DeepMind）`[S-095]`
Gemini ベースの**進化的コーディング・エージェント**（2025年5月公表、arXiv:2506.13131）。

- 数学・計算機科学の未解決問題で新発見。**新しい行列乗算アルゴリズム**を発見
- Google 社内インフラの重要部分に**実際に展開**されたアルゴリズム最適化
- **2026年7月、Gemini Enterprise Agent Platform で GA（一般提供）**に到達 `[S-095]`
  - **評価器はクライアント側で実行され、コードは顧客インフラから出ない**
  - Klarna が ML 学習スループットを倍増したと報じられる
- **OpenEvolve** としてオープンソース実装が存在 `[S-095]`

> **注目すべきは「評価器がクライアント側で走る」というアーキテクチャ。**
> 金融顧客のデータ主権要求に対する、実証済みの解になっている。
> → IP でも **検証器を顧客環境で回す**設計は現実的な選択肢
> （→ [t-regulation-compliance](../04-domain/regulation-and-compliance.md)）。

### (e) ADAS / Meta Agent Search `[S-097]`
**エージェントの設計自体を自動化**する（arXiv:2408.08435）。

- メタエージェントが**制約なしのコード空間で新しいエージェントを反復的にプログラム**し、
  発見された設計の**アーカイブ**を保持する
- 各反復で、メタエージェントは「現在のフレームワーク、ツール群、過去設計のアーカイブ、目標タスク」を受け取り、
  CoT と自己反省で新しい候補を生成
- **手設計の SOTA エージェントを多数のドメインで一貫して上回り、モデル・ドメインを跨いで転移**する
- 派生: **AutoMaAS**（マルチエージェント・アーキテクチャ探索）、
  **MetaGen**（役割とトポロジの自己進化）、**MemPro**（記憶システムを進化可能なプログラムとして扱う）`[S-097]`

### (f) GEPA（Reflective Prompt Evolution）`[S-098]`
arXiv:2507.19457 — **「反射的プロンプト進化は RL を上回りうる」**。

3原則 `[S-098]`:
1. **遺伝的プロンプト進化**
2. **自然言語フィードバックによる反省**
3. **パレートベースの候補選択**

特徴: プロンプトを変異させるが、最適化は**個別の入出力ペアではなく、システム全体の軌跡に対して**行う。
複合 AI システム向けの**サンプル効率の良い最適化器**。

→ IP にとって現実的な自己改善の入口。**モデルを学習させずに、システムを改善できる。**

## 3. IP への含意

### ✅ 採用しうるもの（優先度順）

| # | 施策 | 根拠 | なぜ IP に効くか |
|---|---|---|---|
| 1 | **反証役（レビュアー）の共進化** | RQGM: 安価な進化レビュアーで探索トークン 1.35-1.72倍削減 `[S-094]` | 反証の質が上がり、**探索コストが下がる**。二重に効く |
| 2 | **プロンプト/スキャフォールドの進化（GEPA 型）** | 学習不要、軌跡ベース、パレート選択 `[S-098]` | 顧客ごとの型（視点テンプレート、反証ルーブリック）を進化させられる |
| 3 | **評価の階層化（SIFT 型）** | 安い judge で足切り → 高価な検証は上位のみ `[S-093]` | **IP の検証コストは高い**（原文取得・再計算・人間）。この構造は必須 |
| 4 | **スキャフォールドの転移性** | DGM: モデル/言語を跨いで転移 `[S-092]` | モデルがコモディティ化しても、**改善したワークフローは資産として残る** |
| 5 | **評価器のクライアント側実行** | AlphaEvolve GA の構成 `[S-095]` | 金融のデータ主権要求への回答 |

### ⚠️ 採ってはいけないもの

| 危険 | 理由 |
|---|---|
| **完全閉ループの自己改変** | 投資判断システムで自己改変を許すと、**監査可能性（EU AI Act Art.12/13）が崩壊**する `[S-079]` |
| **安い judge での自己改善** | judge 忠実度が低いと相関ほぼゼロ `[S-093]`。「改善したつもり」が最も危険 |
| **固定評価器での長期最適化** | 非定常性の無視 `[S-094]`。市場も規制も動く。**ベンチに過適合したDDシステム**は実務で死ぬ |
| **プロキシ指標の最適化** | 報酬ハッキングが 46.8〜73.8% で発生 `[S-103]` → [t-reward-hacking](../03-evaluation/reward-hacking-and-proxy-gaming.md) |

### 設計原則の追加案

> **P13: 自己改善はスキャフォールド（プロンプト・ワークフロー・反証ルーブリック）に限定し、
> 「何を良しとするか」の定義（評価器の仕様）は人間の承認を経る。**
>
> **P14: 評価は階層化する — 安価な判定で足切りし、高価な検証（原文取得・再計算・人間）は上位候補にのみ適用する。**

## 4. 安全性（金融で使う以上、無視できない）

- **ICLR 2026 に RSI ワークショップ**が設置されている `[S-106]`（分野として正式に立ち上がった）
- 緩和策として挙げられるもの `[S-106]`:
  高影響な編集への**階層的承認**、**不確実性を考慮した更新トリガ**、安全なベースラインへのフォールバック、
  構造化された自己批判パイプライン、**自己改変を「信頼できないコード」として扱う**多層ゲーティングと継続監査
- **International AI Safety Report 2026** の懸念 `[S-106]`:
  モデルが**テスト環境と実運用を区別**することを学習しつつあり、
  自己改善エージェントが「安全性テスト中であること」を認識して不整合を隠すなら、**評価パラダイム全体が崩れる**
- Sakana RSI Lab も、**自己改善ループに検証可能な安全策を最初から組む**方針を掲げている `[S-007]`

## 5. 出典

- `[S-092]` *Darwin Gödel Machine: Open-Ended Evolution of Self-Improving Agents* arXiv:2505.22954 ／ https://sakana.ai/dgm/
- `[S-093]` SIFT（MIT + Sakana AI, ICLR 2026）／ Stack Futures "Sakana AI Forms First Dedicated RSI Lab…"
- `[S-094]` *The Red Queen Gödel Machine: Co-Evolving Agents and Their Evaluators* arXiv:2606.26294
- `[S-095]` *AlphaEvolve* arXiv:2506.13131 ／ DeepMind Blog ／ InfoQ（2026-07 GA）／ OpenEvolve
- `[S-096]` *A Comprehensive Survey of Self-Evolving AI Agents* arXiv:2508.07407 ／ *Recursive Self-Improvement in AI: From Bounded Self-Refinement to Autonomous Research Loops* arXiv:2607.07663 ／ *Self-Improvements in Modern Agentic Systems: A Survey* arXiv:2607.13104 ／ Awesome-Self-Evolving-Agents
- `[S-097]` *Automated Design of Agentic Systems* arXiv:2408.08435 ／ AutoMaAS arXiv:2510.02669 ／ MetaGen arXiv:2601.19290 ／ MemPro arXiv:2606.00619
- `[S-098]` *GEPA: Reflective Prompt Evolution Can Outperform Reinforcement Learning* arXiv:2507.19457
- `[S-106]` ICLR 2026 Workshop on AI with Recursive Self-Improvement ／ International AI Safety Report 2026 ／ CSA "Recursive Self-Improvement Signals: Security Implications"
