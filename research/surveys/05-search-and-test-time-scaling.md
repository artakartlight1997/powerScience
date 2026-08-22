---
doc_id: survey-05-search
title: "探索・推論時スケーリング・検証器・RL 探索エージェント"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: survey
language: ja
tags: [test-time-scaling, mcts, verifier, prm, rl, information-gain, reward-design]
confidence: medium-high
primary_sources: [S-036, S-037, S-038, S-039, S-040, S-041, S-042, S-043]
contributes_to: [architecture, search-policy, reward-design]
---

# 05. 探索・推論時スケーリング・検証

> このファイルの主題は一つ： **「探索を回すのは簡単。何を報酬にするかが全て」**。

## 1. 探索アルゴリズムの系譜

| 手法 | 幅 | 深さ | 報酬 | 備考 |
|---|---|---|---|---|
| Best-of-N / Self-Consistency | ◎ | × | 多数決 | 単純だが強い。多くのマルチエージェント手法はこれに勝てない `[S-045]` |
| Reflexion / Self-Refine | × | ◎ | 自己批評 | 初手が悪いと抜け出せない |
| Tree of Thoughts / LATS | ○ | ○ | 自己評価/環境 | 行動空間が固定的 |
| **AB-MCTS** `[S-008]` | ◎ | ◎ | 外部フィードバック | **生成による分岐**を確率モデルに載せた点が新規 |
| **Elo トーナメント（co-scientist）** `[S-022]` | ◎ | ○ | **ペアワイズ比較** | 絶対報酬が無い領域で機能する |

### 予算配分の観点

AB-MCTS の Thompson Sampling は本質的に **多腕バンディットによる計算予算配分**である。
Integral Prism では、配分すべき資源が LLM 呼び出しだけではない点が重要：

- LLM トークン（安い）
- Web/DB 検索クエリ（従量。Gemini DR では 1 run の **半分以上が検索コスト**になりうる `[S-020]`）
- **有償データ（expert network, 業界レポート, 与信データ）**（極めて高い）
- **人間の時間**（最も高い）

→ **「人間に何を聞くか」も探索アームの一つとして扱う**設計が、実益に直結する（→ 3節、11）。

## 2. 検証器（Verifier）— ここが勝負

### 生成-検証の非対称性

- 多くの領域で **検証は生成より容易**（generator-verifier gap）`[S-036]`
- **判定側が生成側にないツール（コード実行、DB照合、原文取得）を持つと、ギャップは拡大する** `[S-036]`
- ただし非対称性は一様ではない： 「解くのは難しいが検証は易しい」課題と、
  **「解くのは易しいが検証は難しい」課題**（＝ビジネス判断の多くはこちら）が混在する `[S-036]`
- 検証器の性能は **生成側の確信度に依存して変動**する（自信満々な誤りは検証を通りやすい）`[S-037]`

### 検証器の種類

- **ORM**（結果報酬）vs **PRM**（過程報酬）— PRM は推論ステップ単位で検証 `[S-038]`
- **GenPRM**: PRM 自体に推論時計算を割く（生成的検証）`[S-038]`
- **Multi-Agent Verification**: 複数の検証器で test-time compute をスケール `[S-039]`
- **T1**: ツール統合検証（小型モデルでも外部ツールで検証すれば強い）`[S-038]`

**IP への含意（設計原則 #5）**:
**検証器には、生成器が持たない権限を与える**。具体的には
①原文取得権（引用先を実際に開く）②数値再計算権（XBRL/財務モデルの再実行）③時系列整合権（後知恵バイアスの検出）。
これは Marlin/Gemini DR の「同じモデルが自己評価する」構造に対する、**構造的な優位**になりうる。

## 3. 「次に何を調べるか」を決める理論 — 情報価値

DR エージェントの多くは、次のクエリをヒューリスティック（LLM の気分）で決めている。
ここには**明示的な理論**がある。

- **BED-LLM**（Bayesian Experimental Design with LLMs, arXiv:2508.21184）`[S-040]`
  → **期待情報利得（EIG）を最大化する質問**を逐次選ぶ。
  EIG = 実験結果の周辺分布についての、事前→事後の KL ダイバージェンス期待値。
  20 Questions 型タスク・多段対話で、情報収集効率が実際に改善する `[S-040][S-041]`
- **ASIG (2026)**: BED を LLM の重みに **償却（amortise）**し、推論時最適化なしで逐次情報収集 `[S-041]`
- **Active Task Disambiguation** `[S-042]`: 曖昧なタスクに対し、**どの明確化質問が最も情報量が高いか**を選ぶ

**IP への含意（設計原則 #6 = 中核仮説）**:
投資判断は本質的に **「どの不確実性が意思決定を反転させるか」** の問題である。
したがって探索の報酬は「レポートの見栄え」ではなく、
**「意思決定を反転させうる不確実性の削減量（decision-relevant EIG）」** に置くべきである。

```
古典的 DR:  質問 → 検索 → 要約 → レポート
Integral Prism 仮説:
   投資判断（Go/No-Go, 価格, 条件）
      ↓ どの前提が崩れると判断が反転するか（感度分析）
   反転しうる前提 = 高 EIG ノード
      ↓ そこにだけ探索予算と人間の時間を割く
   出力 = 「判断を支える証拠構造 ＋ 残る反証リスク ＋ 次に確認すべき3件」
```

## 4. RL 探索エージェント（Search-R1 系）の到達点

- **Search-R1 / R1-Searcher / DeepResearcher / ZeroSearch**: 中間ステップ監督なしに、
  検索と推論を同時に行う方策を RL で獲得 `[S-043]`
- 報酬設計の潮流 `[S-043][S-044]`:
  - 初期＝ **outcome reward**（最終答えの EM/F1 をルールベース検証器で採点）
  - 現在＝ **process reward / 多面報酬**：情報利得、経路カバレッジ、検索コスト（StepSearch, SIGHT, InfoFlow, TIPS 等）
  - さらに **明瞭性・真実性・簡潔性・効率・幻覚抑制**まで報酬に含める多面設計へ
- **ARBOR**: 再利用可能なルーブリック・バッファによる**オンライン過程報酬** `[S-044]`

**含意**: 我々は自前で RL 学習をしない。しかし **報酬の定義（＝何を良しとするか）は自前で持てる**。
上記の多面報酬は、そのまま **推論時の探索スコア**として使える。学習しなくても効く。

## 5. マルチエージェント討論の効果と危険

- 肯定側: 21設定中19で単体ベースラインを上回り、平均 **+7.05pt** `[S-045]`。
  多様性がある／批評が明示的な根拠に接地している／**判定者が検証可能な推論を報酬にする**とき効果が最大 `[S-045]`
- 否定側（重要）:
  - **戦略的に設計された敵対エージェント1体で、集団の精度が 10〜40% 低下**し、
    **誤答への合意が 30%超増加**する `[S-046]`
  - 討論は、ハイパーパラメータを詰めない限り **self-consistency や Medprompt に確実には勝たない** `[S-045]`

**IP への含意（設計原則 #7）**: 討論を「合意形成」に使ってはならない。
**討論は反証（disconfirmation）を生産するために使い、結論は証拠の集約規則で決める。**
説得力の高いエージェントが勝つ仕組みは、投資判断では致命的（＝もっともらしいストーリーに賭ける）。

## 6. 参考（出典）

`[S-036]` *Trust but Verify! A Survey on Verification Design for Test-time Scaling* arXiv:2508.16665
`[S-037]` *Exploiting Verification-Generation Gap…* arXiv:2606.03608
`[S-038]` GenPRM arXiv:2504.00891 / T1 arXiv:2504.04718
`[S-039]` *Multi-Agent Verification: Scaling Test-Time Compute with Multiple Verifiers* arXiv:2502.20379
`[S-040]` *BED-LLM: Intelligent Information Gathering with LLMs and Bayesian Experimental Design* arXiv:2508.21184
`[S-041]` *Amortising Bayesian Experimental Design for Sequential…* arXiv:2607.03426
`[S-042]` *Active Task Disambiguation with LLMs* arXiv:2502.04485
`[S-043]` *A Comprehensive Survey on RL-based Agentic Search* arXiv:2510.16724 / Search-R1 / R1-Searcher arXiv:2503.05592
`[S-044]` *ARBOR: Online Process Rewards via a Reusable Rubric Buffer for Search Agents* arXiv:2606.03239 ／ *Retrieval, Reward, and Training Protocols* arXiv:2605.27881
`[S-045]` Multi-Agent Debate 各種（GroupDebate arXiv:2409.14051 ほか、Springer/JKSU 2025 のメタ評価）
`[S-046]` *When collaboration fails: persuasion driven adversarial influence in multi agent LLM debate* (Scientific Reports, 2026) https://www.nature.com/articles/s41598-026-42705-7
