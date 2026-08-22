---
doc_id: t-ip-evaluation-design
title: "Integral Prism の評価設計 — 何を測れば勝ちなのか"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: evaluation
language: ja
tags: [evaluation-design, counterfactual-dd, point-in-time, leakage, brier, ci]
confidence: medium
primary_sources: [S-057, S-060, S-016, S-068]
related_topics: [t-citation-attribution, t-calibration-forecasting, t-finance-benchmarks]
contributes_to: [product-claims, roadmap]
---

# Integral Prism の評価設計

**汎用ベンチでの勝敗は売り文句にはなるが、実益ではない。**
`method-and-scope.md` で定義した5軸（時間 / 見落とし率 / 反証可能性 / 較正 / 再利用性）に沿って自前で組む。

## 評価 A: 反実仮想デューデリ（Retrospective DD）★最重要

**過去の実案件・実 M&A で、T 時点までの情報のみを与えて分析させ、T+2〜3年の実結果と突き合わせる。**

| 項目 | 内容 |
|---|---|
| 測るもの | **見落とし率**（後に材料化した事実の事前検出率）、**較正**（Brier / ECE） |
| 作り方 | EDINET / EDGAR ＋ 適時開示 ＋ ニュースを **point-in-time（時点凍結）**で構成 |
| 最大の技術課題 | **リーク防止**。モデルは後年の結果を訓練データで知っている可能性がある |
| リーク対策 | ①固有名詞の匿名化 ②訓練カットオフ後の事案を優先 ③「後知恵を使った兆候」の検出器を別に持つ ④予測理由の説明を要求し、時点整合をチェック |
| 先行例 | EDINET-Bench の**ラベル自動付与＋更新可能設計** `[S-016]` ／ IPO Finance Agent の**自動ルーブリック生成** `[S-068]` |
| 工数 | 数人月（→ 未決論点：いつ払うか） |

**なぜ最重要か**: これが**製品の売り文句そのもの**になる。
「我々のシステムは、過去N件の案件で、実際に問題化した事実の X% を事前に指摘した」

## 評価 B: 引用の閉ループ検証（CI 化）

`Cited but Not Verified` の枠組み `[S-057]` をそのまま社内 CI にする。

| 指標 | 合格条件（案） |
|---|---|
| Link Works | ≥ 99%（スナップショット保存により原理的に100%可能） |
| Relevant Content | ≥ 95% |
| **Fact Check** | ≥ 95%（主要主張）／ ≥ 90%（全主張） |
| **劣化曲線** | **ツール呼び出し150回時点でも Fact Check ≥ 90%** |

→ [t-citation-attribution](citation-attribution.md)

## 評価 C: 診断力（ACH ベース）

| 指標 | 内容 |
|---|---|
| **hypothesis recall** | 生成された仮説集合が、**実際に起きた事象を含んでいたか** |
| **診断性効率** | 診断的証拠を優先探索できたか（無駄な証拠取得の割合） |
| **反証の網羅** | 事前に列挙した死因のうち、検証まで到達した割合 |

→ [t-structured-analytic-techniques](../02-methods/structured-analytic-techniques.md)

## 評価 D: 人的コスト（購買を最も左右する）

**アナリストが成果物を検証し直すのに要した時間。**

- 競合は誰も測っていない `C`
- 測り方: 同一案件を ①IP あり ②IP なし ③競合製品 で行い、**IC 提出までの人時**を比較
- 副次指標: **裏取りのために原文を開いた回数**（IP が出典スナップショットを持てば激減するはず）

## 評価 E: 較正の公開

- 主張の確率と実現の突合を蓄積し、**Brier / ECE を四半期ごとに顧客へ開示** `[S-060]`
- 人間が上書きした確度（介入点 I4）は**人間側の較正**として別途集計 — これ自体が顧客価値

## 判定の作法（横断ルール）

1. LLM judge は **「原文に支持されるか」の二値判定にのみ**使う
2. 順序ランダム化・両順序評価、複数 judge の**一致率（κ）を常時記録**
3. **判定の判定**: 人手サンプルで judge 自体を四半期ごとに較正
→ [t-llm-judge-reliability](llm-judge-reliability.md)

## 出典

- `[S-057]` *Cited but Not Verified* ／ `[S-060]` ForecastBench 系 ／ `[S-016]` EDINET-Bench ／ `[S-068]` IPO Finance Agent ほか
