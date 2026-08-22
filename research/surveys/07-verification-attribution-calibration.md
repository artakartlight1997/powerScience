---
doc_id: survey-07-verification
title: "出典検証・幻覚・較正・構造化分析技法"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: survey
language: ja
tags: [attribution, citation, hallucination, calibration, forecasting, ACH, judge-bias]
confidence: high
primary_sources: [S-057, S-058, S-059, S-060, S-061, S-062, S-063]
contributes_to: [core-differentiation, trust, evaluation]
---

# 07. 検証・出典・較正 — Integral Prism の主戦場

> **本サーベイ全体で最も重要なファイル。** 競合が最も弱く、投資実務が最も要求する領域。

## 1. 「引用されているが、検証されていない」

*Cited but Not Verified: Parsing and Evaluating Source Attribution in LLM Deep Research Agents*（arXiv:2605.06635）`[S-057]`

評価枠組み（AST パーサで Markdown レポートの inline citation を大規模抽出 → 実際に引用先を取得して判定）:

| 次元 | 内容 | フロンティアモデルの実測 |
|---|---|---|
| **Link Works** | URL が到達可能か | **94%超** |
| **Relevant Content** | 話題として整合しているか | **80%超** |
| **Fact Check** | 引用元が実際にその主張を支持するか | **39〜77%** ← ここが崩壊している |

さらに決定的な発見 `[S-057]`:
- **ツール呼び出しを 2 → 150 に増やすと、Fact Check 精度が 2 つのフロンティアモデルで平均 約42% 低下**
- オープンモデルの半数以上は、one-shot で引用つきレポートを生成すること自体に失敗

**含意（IP の存在理由）**:
1. 「もっと調べる（＝長時間・多ツール）」は、**引用の正しさを悪化させる**。
   Marlin の「8時間」は、**この劣化を打ち消す仕掛けを持っていなければ、むしろ逆効果**。
2. **引用の Fact Check を機械で閉ループにすることが、そのまま差別化になる**。
   これは学習を必要とせず、エンジニアリングで到達できる。
3. 投資実務では、Fact Check 精度 39〜77% は **使い物にならない**。
   IC 資料の1文が誤引用なら、資料全体の信頼が飛ぶ。

## 2. LLM 判定（LLM-as-a-Judge）の信頼性

co-scientist の Elo（→03）や、自己評価型の探索報酬は、すべてここに依存する。

- **位置バイアス**: ルーブリックの選択肢の**並び順**でスコアが偏る。方向はモデル固有（先頭を好む/末尾を好む）`[S-058]`
- **冗長性・権威バイアス**、暗黙のバンドワゴン・感情バイアス `[S-058][S-059]`
- **再現性の欠如**: ルーブリック・プロンプトを固定しても判定は非決定的。
  → 報告された「改善」がサンプリングノイズである可能性 `[S-058]`
- 実務: 統制下では 80% 精度でも、**本番のバイアステストでは 50% 超のエラー率**という報告 `[S-059]`

**対策の定石** `[S-058][S-059]`:
- 選択肢順序のランダム化＋両順序評価（position swap）
- **開放的な「品質」評価をやめ、事実基準に制約したルーブリックにする**
- 人間レビューによる較正（judge の judge）

**IP への含意（設計原則 #10）**:
**「良い/悪い」を LLM に聞かない。**「この主張は、この原文のこの行に支持されるか（Yes/No/部分）」だけを聞く。
判定タスクを**検証可能な最小単位まで落とす**ほど、バイアスは効かなくなる。

## 3. 較正（Calibration）と予測 — 投資プロが本当に欲しいもの

- ForecastBench 系の到達点: **複数モデルが superforecaster と統計的に区別できない**水準に到達（2026年5月時点）`[S-060]`
- **AIA Forecaster**: FB-Market で Brier 0.0753（人間 SOTA 0.0740）`[S-060]`
- 12 LLM のアンサンブルが、**925人の人間予測者クラウドと統計的に区別できない**精度 `[S-060]`
- 手法: Brier 報酬での GRPO/ReMax ファインチューンで **ECE ≈ 0.042** まで較正改善 `[S-060]`
- **Argumentative Coherence Filter**: 論証構造と予測確率の内的整合を強制し、
  **根拠の弱い予測を除去することで集団精度が改善** `[S-060]`

**含意（IP 中核仮説の裏付け）**:
1. **確率つきの主張は、もはや実現可能**。「たぶん伸びます」ではなく「3年後に EBITDA マージン 15% 超： 38%（±）」が出せる。
2. **較正は測定できる**（Brier / ECE）。つまり **「うちのシステムは較正されている」を証明可能な形で売れる**。
   これは競合が誰も主張していないポジション。
3. Argumentative Coherence Filter は、**論拠と確率の不整合を検出する**という点で、
   投資メモの品質管理そのもの。

## 4. 構造化分析技法（SATs / ACH）— 型の輸入元

情報コミュニティが数十年かけて磨いた **バイアス対策の型**がある `[S-061][S-062]`。

- **ACH（Analysis of Competing Hypotheses）**: Richards J. Heuer Jr.（CIA, 1970-80s、『Psychology of Intelligence Analysis』1999）
  1. **競合する仮説を網羅的に列挙**する（最初に一つに決めない）
  2. 各証拠について、**どの仮説を支持/反証するか**の行列を作る
  3. **最も反証されていない仮説**を採る（支持証拠が多い仮説ではない）
  4. **診断的な証拠**（仮説を切り分ける力のある証拠）を重視する
- その他 SATs: Key Assumptions Check, Red Team, Devil's Advocacy, Premortem, 年表構築

**LLM で自動化する際の致命的な落とし穴** `[S-061]`:
> LLM が生成する「対立仮説」は訓練分布からサンプリングされる。つまり **その論点の主流的コンセンサスを反映する**。
> 結果、**本当に非主流な仮説は出てこない**。バイアス緩和ステップを自動化すると、**バイアスの自動化になる**。
> 特に mirror-imaging（自文化投影）は、英語中心コーパスで悪化する。

**IP への含意（設計原則 #11）**:
- ACH の**行列構造をシステムの一次データ構造にする**（レポートではなく行列が成果物）
- ただし**仮説の多様性は LLM に任せない**。
  仮説生成は ①実務由来の型（ロールアップ失敗、チャネル依存、キーマンリスク、会計方針変更…）
  ②過去案件のケースベース（→06）③人間の投入、で担保する。
- **「診断的証拠」の概念 = 05 の EIG とほぼ同義**。ACH は EIG の実務的な言い換えである。
  → 理論（BED/EIG）と実務（ACH）が同じ場所を指している。**ここが Integral Prism の設計の背骨**。

## 5. 「反証を生産する」ための機構

- 多エージェント討論は説得力に負ける（→05 `[S-046]`）。**討論ではなく反証タスク化**する。
- **Digital Red Queen**（→02 `[S-015]`）の敵対的共進化は、
  「反証役を世代を通じて強くする」実装アイデアとして直接転用できる。
- **TriAdReview**（三角敵対レビュー）等、生成/批判/裁定を分離する構成も参照 `[S-063]`
- **Elenchus**（prover-skeptic 対話から知識ベースを生成）`[S-063]` は、
  「討論の副産物を知識資産にする」発想として重要。

## 6. まとめ — 検証スタックの構想（議論用の叩き台）

```
L4  較正層     : 主張ごとの確率と、その較正履歴（Brier/ECE を蓄積）
L3  反証層     : ACH 行列 / 反証タスク / レッドチーム（診断的証拠の優先探索）
L2  整合層     : 数値再計算・時系列整合・文書間矛盾の検出
L1  接地層     : 主張 ↔ 原文スパンの機械検証（Fact Check ループ）
L0  取得層     : 出典の恒久保存（スナップショット・ハッシュ・取得時刻）
```

L0-L1 は**エンジニアリングで確実に到達できる**。L2 はドメイン設計。L3-L4 が差別化の頂点。
競合はおおむね L0 の一部（URL を貼る）で止まっている。`C`

## 7. 参考（出典）

`[S-057]` *Cited but Not Verified* arXiv:2605.06635
`[S-058]` *Am I More Pointwise or Pairwise? Revealing Position Bias in Rubric-Based LLM-as-a-Judge* arXiv:2602.02219 ／ *A Systematic Study of Position Bias in LLM-as-a-Judge*（IJCNLP 2025）
`[S-059]` *Bias in the Loop* arXiv:2604.16790 ／ Adaline "LLM-as-a-Judge: Why Frontier Models Fail 50%+ Bias Tests"
`[S-060]` ForecastBench（ICLR 2025 / Wharton）／ Forecasting Research Institute "AI models have likely reached parity with superforecasters" ／ *Agentic Forecasting using Sequential Bayesian Updating* arXiv:2604.18576 ／ Foresight Arena arXiv:2605.00420
`[S-061]` SATs for LLMs https://mattdot.github.io/sats4llms/concepts/structured-analytic-techniques
`[S-062]` Dhami et al. "The analysis of competing hypotheses in intelligence analysis" *Applied Cognitive Psychology* (2019) ／ Heuer, *Psychology of Intelligence Analysis* (1999)
`[S-063]` *TriAdReview* arXiv:2606.15074 ／ *Elenchus* arXiv:2603.06974
