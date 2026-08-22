---
doc_id: t-point-in-time
title: "時点再現とリーク防止 — 反実仮想 DD を成立させる技術"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: evaluation
language: ja
tags: [point-in-time, bitemporal, look-ahead-bias, leakage, backtest, restatement]
confidence: medium-high
primary_sources: [S-133]
related_topics: [t-ip-evaluation-design, t-retrieval-graphrag, t-benchmark-crisis]
contributes_to: [evaluation, core-differentiation]
---

# 時点再現とリーク防止

> **評価A（反実仮想デューデリ）は IP の売り文句そのものである。**
> **しかし「T 時点の情報だけを与える」は、実装が最も難しい部分でもある。**
> ここが甘いと「見落とし率 X%」という数字自体が信用されない。

## 1. 定石は確立している（金融の実務知）

> **Point-in-time データこそが、look-ahead bias に対する最も有効な単一の防御である。**
> **各日付時点で公に入手可能だった情報のみを記録し、修正・再表示・遡及的な構成銘柄変更を含めない。** `[S-133]`

### バイテンポラル構造 `[S-133]`
**バイテンポラル・データ構造は厳格な時間的整合性を強制し、
バックテストを look-ahead bias から解放し、規制水準の再現性を担保する。**

```
2つの時間軸を持つ:
  valid_time      : その事実が現実に成り立っていた期間（例: FY24 の売上）
  transaction_time: その事実がデータベースに記録された時点（例: 2024-05-15 に開示）

→ 「2024-06-01 時点で知り得たこと」を復元できる
→ 修正再表示（restatement）があっても、当時の値と現在の値の両方を保持
```

非構造の規制ファイリング（10-K / 10-Q / 8-K）を**構造化されたバイテンポラル DB に取り込む**
アプローチが既に実装されている `[S-133]`。

### look-ahead bias の主な発生源 `[S-133]`
1. **point-in-time でなく修正再表示後の財務を使う** ← 最頻出
2. 非同期な取引所フィード間の**タイムスタンプのずれ**
3. **将来の分割比率を知った上での**コーポレートアクション調整

## 2. LLM 特有の、より厄介なリーク

上記は「データのリーク」だが、**LLM には第二のリーク経路がある**。

> **モデルは訓練データで、その後に何が起きたかを既に知っている可能性がある。**

これは金融のバックテストの伝統的な手法では防げない。対策案（IP 独自、`C`）:

| 対策 | 内容 | 限界 |
|---|---|---|
| **匿名化** | 固有名詞・地名・製品名を置換 | 文脈から推定されうる。財務数値の特徴からも特定されうる |
| **カットオフ後の事案を優先** | モデルの知識カットオフ以降に決着した案件を使う | サンプル数が限られる。モデル更新のたびに使えなくなる |
| **後知恵検出器** | 「なぜそう考えたか」の説明を要求し、**T 時点で入手不可能な事実への言及を検出**する | 明示的に言及しなければ検出できない |
| **時点整合の機械チェック** | 引用した全証拠の `as_of` が T 以前であることを検証（IP は全証拠に取得時刻を持つ） | ★**これは我々の構造で確実に効く** |
| **プレースホルダ照合** | 同型の架空案件を混ぜ、既知案件との性能差を測る | 作成コスト |
| **LiveBench 型の設計** | 評価セットを**継続的に更新**し、常に最新のカットオフ後事案を含める `[S-116]` | 運用コスト |

> ### 🔑 IP にとっての構造的な優位
> **我々は全証拠に `as_of`（取得時刻）と `valid_from/valid_until` を持たせる設計**（P8/P12）。
> したがって **「T 以降の証拠を1つも使っていない」を機械的に証明できる**。
> 一般の DR エージェントはこれができない（証拠に時点メタデータを持たないため）。
> **つまり反実仮想 DD は、我々の設計だからこそ実施できる評価**であり、
> **その事実自体が差別化の証明になる。**

## 3. 実装要件

```
証拠ストアの必須フィールド:
  as_of            : この情報が公に入手可能になった時点（開示日、公開日）
  retrieved_at     : 我々が取得した時点
  valid_from/until : 事実として成立する期間
  supersedes       : この記録が置き換えた過去の記録（修正再表示の追跡）
  snapshot_hash    : 取得時点の原文のハッシュ

評価モード:
  as_of_cutoff = T を設定すると、as_of > T の証拠は検索結果から物理的に除外される
  （フィルタではなく、インデックス側で分離する — 「見えていたが使わなかった」を許さない）
```

**修正再表示の追跡（supersedes）は、それ自体が投資分析の材料**でもある。
「この会社は過去3年で2回、売上認識を修正している」は重要な赤旗であり、
**point-in-time DB を持つと、これが副産物として得られる**。

## 4. 出典

- `[S-133]` TEJ Point-in-Time Audited Financial Database ／ *Just-in-Time Historical State Reconstruction for Low-Latency Financial Trading with LLMs*（MDPI AI）／ sharpely「Bias Free Backtesting」／ Inference Systems「What is Look-Ahead Bias?」／ CFA Level 2「Problems in Backtesting」
