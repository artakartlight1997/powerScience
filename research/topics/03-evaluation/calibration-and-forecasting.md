---
doc_id: t-calibration-forecasting
title: "較正と予測 — 投資プロの母語で話す"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: evaluation
language: ja
tags: [calibration, brier, ece, forecasting, superforecaster, ensemble, argumentation]
confidence: medium-high
primary_sources: [S-060]
related_topics: [t-differentiation-hypotheses, t-llm-judge-reliability, t-ip-evaluation-design]
contributes_to: [core-differentiation, output-design]
---

# 較正と予測

**投資プロは確率で考える職業である。彼らの母語で話す唯一のシステムになれる。**

## 1. 到達点（2026年）

| 事実 | 数値 |
|---|---|
| ForecastBench トーナメントで、複数システムが **superforecaster と統計的に区別できない**（Cassi AI, xAI, Google DeepMind 等）`[S-060]` | — |
| AI がデータセット問題で superforecaster に並んだ時点 | **2026年5月** `[S-060]` |
| **AIA Forecaster**: FB-Market での Brier | **0.0753**（人間 SOTA 0.0740）`[S-060]` |
| **12 LLM のアンサンブル**が、**925人の人間予測者クラウド**と統計的に区別できない精度（3ヶ月トーナメント）`[S-060]` | — |
| **Brier 報酬**での GRPO / ReMax ファインチューン＋厳密な単調データ順序で、精度と較正が改善 | **ECE ≈ 0.042** `[S-060]` |

### Argumentative Coherence Filter `[S-060]`
**論証構造と予測確率の内的整合を強制**し、
**根拠の弱い予測を除去する**ことで集団精度が改善する。

→ これは **投資メモの品質管理そのもの**。
「強気の結論だが、根拠として挙げた事実は弱い」を機械的に検出できる。

## 2. IP への含意

### (a) 確率つきの主張は、もう実現可能
「たぶん伸びます」ではなく
**「3年後に EBITDA マージン 15% 超： 38%（根拠: E12, E31, E44 / 反証未解決: H4）」** が出せる。

### (b) 較正は測定できる → 証明可能な差別化になる
- **Brier スコア**（確率予測の二乗誤差）、**ECE**（期待較正誤差）
- **「うちの 70% は、実際に約70%当たる」を四半期ごとに証明する**
- これは競合が誰も主張していないポジション `C`

### (c) アンサンブルが効く
12 LLM のアンサンブルが人間クラウド並み `[S-060]`。
→ [t-model-routing](../02-methods/model-routing-and-cascades.md) のマルチベンダ構成が、
**品質・原価・独立性に加えて「較正」の理由でも正当化される**。

## 3. 実装上の論点

| 論点 | 内容 |
|---|---|
| **何を予測対象にするか** | 「株価」ではなく **DD で検証可能な命題**（例: 上位顧客の解約が今後2年で起きるか） |
| **解決可能性** | 予測は**後で答え合わせできる形**でなければ較正できない。命題設計が最重要 |
| **時間軸** | PE の保有期間（3〜7年）は長い。**中間指標（leading indicator）**で較正サイクルを短くする |
| **サンプル数** | 案件数は少ない。**案件内の多数の小命題**で較正母数を稼ぐ |
| **主観の混入** | 人間が確度を上書きした場合（介入点 I4）は、**人間の較正も別途測る**（これ自体が顧客価値） |

## 4. 出典

- `[S-060]` ForecastBench（ICLR 2025 / Wharton）／ Forecasting Research Institute "AI models have likely reached parity with superforecasters" ／ AIA Forecaster ／ *Agentic Forecasting using Sequential Bayesian Updating of Linguistic Beliefs* arXiv:2604.18576 ／ *Foresight Arena* arXiv:2605.00420 ／ Thinking Machines Lab "Training LLMs to Predict World Events"
