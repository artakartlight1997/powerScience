---
doc_id: t-decision-boundary
title: "決定境界の形式化と意思決定分析 — 論点 D3 への回答"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [decision-analysis, influence-diagram, evpi, tornado, sensitivity, clarification, pomdp]
confidence: medium-high
primary_sources: [S-121, S-122, S-040]
related_topics: [t-information-value-eig, t-differentiation-hypotheses, t-evidence-aggregation]
contributes_to: [core-architecture, D3]
---

# 決定境界の形式化と意思決定分析

> **論点 D3「『判断が反転する』をどう機械的に定義するか」への回答。**
> 結論から言うと、**車輪を再発明する必要はない。意思決定分析（decision analysis）に完成した道具立てがある。**

## 1. 既存の道具立て（1960年代からある）

| 道具 | 何をするか | IP での用途 |
|---|---|---|
| **決定木 / インフルエンス・ダイアグラム** | 決定・不確実性・結果の依存関係を図式化し、ロールバックで期待値を出す `[S-121]` | 投資判断（Go/No-Go / 価格 / 条件）の構造化 |
| **トルネード図** | **一方向感度分析の視覚的要約**。各パラメータを指定範囲で振り、他を固定して再計算し、**影響の大きさで並べる** `[S-121]` | **「どの前提が判断を反転させるか」の直接的な特定** |
| **決定感度（decision sensitivity）** | トルネードが「リスクの源」を示すのに対し、**「価値の源」を示す** `[S-121]` | 反証の優先順位づけ |
| **EVPI（完全情報の期待価値）** | 完全情報の下での価値と、不完全情報下で今しなければならない決定の価値の差 `[S-122]` | **情報取得の上限価格**（＝この調査に払ってよい金額） |
| **ベイズ改訂・効用関数** | 事前→事後の更新、リスク態度の反映 `[S-121]` | 較正層との接続 |
| ツール | PrecisionTree（Excel アドイン）、TreeAge Pro、**SilverDecisions（OSS）** `[S-121]` | 参照実装として使える |

> **EVPI の重要な性質** `[S-122]`:
> **情報の価値は決してゼロを下回らない**（意思決定者は追加情報を無視できるため）。
> そして **EVPI を超える価値を持つ情報収集活動は存在しない**。
> → **調査予算の理論的上限を与える。** 「この論点に100万円かける価値があるか」に答えられる。

## 2. LLM 側の接続（2025-2026）

| 研究 | 内容 |
|---|---|
| **SAGE-Agent / Structured Uncertainty guided Clarification**（arXiv:2511.08798）`[S-122]` | ツール引数の曖昧性解消を **POMDP として定式化し、EVPI を目的関数**として最適な質問を選ぶ。冗長性を防ぐ**アスペクト単位のコストモデル**つき。<br>**曖昧タスクのカバレッジ +7〜39%、明確化質問の回数は 1.5〜2.7倍削減** |
| **Neural EVPI による明確化質問のランキング** `[S-122]` | 「良い質問を学ぶ」の古典的定式化 |
| **BED-LLM** `[S-040]` | EIG 最大化による逐次質問選択（→ [t-information-value-eig](information-value-eig.md)） |

> **注意**: 検索で確認した範囲では、**古典的な意思決定分析（インフルエンス・ダイアグラム、トルネード）と
> LLM エージェントを本格的に統合した研究は見当たらなかった** `C`。
> ここは**空白**であり、IP が独自に埋める余地がある（＝差別化になりうる）。

## 3. IP への落とし込み（D3 の3案を再評価）

前回提示した3案を、上記を踏まえて再定義する。

### 案3（人力）→ **改め「決定フレームの共同構築」**
人間が「この投資の生死を決める3つの前提」を入力する。
**これはインフルエンス・ダイアグラムの簡易版**であり、決して手抜きではない。
意思決定分析の実務でも、**フレーミングは人間が行うのが標準**（フレーミングの誤りは技法では救えない）。

### 案2（記号）→ **IC チェックリストの命題化 ＋ トルネード**
各命題に「真/偽」と「判断への影響度」を持たせ、**影響度で並べる＝トルネード図**。
影響度は最初は人間が入れ、案件が溜まれば過去データから推定できる。

### 案1（数値）→ **簡易バリュエーションモデルの感度分析**
`Entry Multiple × EBITDA成長 × マージン × Exit Multiple × レバレッジ` の
最小限のモデルを持ち、**各前提を範囲で振ってトルネードを描く**。
「IRR が hurdle を下回る」点を**決定境界**として機械的に定義できる。

> ⚠️ **ただし [t-numeric-verification](../03-evaluation/numeric-and-table-verification.md) の警告に注意**:
> **LLM の素の数値計算精度は約52%**（抽出は88%）`[S-131]`。
> **計算は必ずコードで行い、モデルに計算させない。**

## 4. 推奨アーキテクチャ（叩き台）

```
① 決定フレーム      : 人間 ＋ AI で「決定 / 不確実性 / 結果」を構造化（インフルエンス・ダイアグラム）
② 前提の抽出        : 各不確実性に確率分布（または3点見積り: 悲観/基準/楽観）
③ トルネード        : 各前提を振って IRR / MOIC への影響を計算（★コードで計算）
④ 決定境界の特定    : 「Go/No-Go が反転する閾値」を前提ごとに算出
⑤ EVPI 計算         : 各不確実性を完全に解消できたときの価値 → 調査予算の上限
⑥ 探索予算の配分    : EVPI ÷ 取得コスト でランキング → 上位から調査（＝ decision-relevant EIG）
⑦ 証拠で更新        : 取得した証拠で確率を更新（→ t-evidence-aggregation）
⑧ 停止              : 残る EVPI が取得コストを下回ったら終了
```

**この⑤⑥が IP の中核**であり、**既存 DR には存在しない**。
そして⑤は顧客に説明可能である：**「この調査に払ってよい上限は◯◯円です」**と言える。

## 5. 出典

- `[S-121]` 意思決定分析ツールと技法（Vose Software / TreeAge Pro / PrecisionTree / SilverDecisions / PMI）
- `[S-122]` *Structured Uncertainty guided Clarification for LLM Agents*（SAGE-Agent）arXiv:2511.08798 ／ *Learning to Ask Good Questions: Ranking Clarification Questions using Neural EVPI* ／ EVPI の定義
- `[S-040]` BED-LLM arXiv:2508.21184
