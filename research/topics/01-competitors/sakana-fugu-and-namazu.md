---
doc_id: t-sakana-fugu-namazu
title: "Sakana Fugu / Namazu — オーケストレーションのモデル化と主権AI戦略"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: competitors
language: ja
tags: [sakana, fugu, namazu, orchestration, routing, sovereign-ai, open-weights, japanese]
confidence: medium
primary_sources: [S-104, S-105]
related_topics: [t-sakana-marlin, t-model-routing, t-competitive-map, t-sakana-ab-mcts]
contributes_to: [competitive-analysis, architecture, strategy]
---

# Sakana Fugu / Namazu

> ⚠️ **前回サーベイ（v0.1）の重要な見落とし。**
> 「Sakana のマルチモデル・オーケストレーションは Marlin の内部実装にすぎない」という前提は**誤りだった**。
> Sakana は 2026年6月に **オーケストレーション自体を独立した商用モデルとして出荷している**。

## 1. Sakana Fugu（2026-06-22/23 発表）

### 何か
**フロンティアのエージェント・ワーカ群を、適応的・動的に統率するために訓練された言語モデル族** `[S-104]`。

- **Fugu** — 速度重視。**入力ごとに単一のワーカを選択**し、レイテンシはフロンティアへの直接呼び出しと同等。
  それでいて各クエリを「そのクエリに最も強いエージェント」へ振る `[S-104]`
- **Fugu-Ultra** — 品質重視。**入力ごとに複数エージェントのワークフローを構成**し、
  レイテンシと引き換えに品質を取る。最も複雑なタスク向け `[S-104]`

**ワーカのプール**は差し替え可能（swappable）で、Claude Opus 4.8 / GPT-5.5 / Gemini 3.1 Pro などを含み、
**1つの API の背後で回答を統合する** `[S-104]`。

### ベンチマーク `[S-104]` `B`
| 項目 | 値 |
|---|---|
| Terminal-Bench 2.1（Fugu-Ultra v1.1） | **82.1%** |
| SWE-Bench Pro（同） | **73.7%** |
| その他 | 4つのコーディング系ベンチ、**CharXiv Reasoning**、**Humanity's Last Exam** で首位と報じられる |

評価全体を通じて、Fugu はルーティング分布に**一貫した、かつ多様な適応性**を示し、
モデル間の能力差を学習できていることが示されている `[S-104]`。

### なぜ重要か（IP への影響）

1. **「マルチモデル集合知」はもはや論文でも内部実装でもなく、APIで買える製品になった。**
   → IP が「マルチモデルで束ねます」を差別化として語ることは**もうできない**。
2. 一方で **Fugu は「どのモデルに投げるか」の最適化であって、「何を調べるべきか」の最適化ではない**。
   IP の差別化軸（decision-relevant EIG・反証・較正）とは**レイヤが違う** `C`。
3. **むしろ IP は Fugu を部品として使える可能性がある**（ワーカ選択を外部委譲し、
   我々は探索目的関数と検証に集中する）。ただしベンダ依存と、
   **生成と検証を別ベンダにする原則**（→ [t-verifier-design](../02-methods/verifier-design.md) P5）との整合を要検討。

## 2. Sakana Namazu（2026-08 提供開始）

**Moonshot AI の オープンウェイト Kimi K2.6 を、日本語特化にファインチューンしたモデル** `[S-105]`。

| 項目 | 内容 |
|---|---|
| ベース | **Kimi K2.6（オープンウェイト）** |
| 特化 | 日本語の機微 — **敬語・商習慣・口語**まで含む、Sakana 独自データでの追加チューニング |
| 性能 | AIME26 / MMLU-Pro / LiveCodeBench v6 ではベースの能力を保持しつつ、**日本語特化ベンチで大きく前進**。<br>FairPoliticsQA で **34.10% → 56.30%** |
| 価格 | **$0.95 / 1M 入力、$4.00 / 1M 出力**（OpenAI 互換 API） |
| 文脈 | **262,144 トークン**（出力最大 65,536） |
| 制約 | **EU / 英国 / スイスでは提供なし** |
| 内蔵ツール | Web 検索、コード実行 |

## 3. 戦略の読み替え — 「主権AIは事前学習ではなく、チューニングとオーケストレーション」

報じられている Sakana の戦略 `[S-105]`:

> **Namazu は Kimi K2.6 のファインチューンであり、Fugu の指揮者は Gemma 4 ベースでも数日で検証された。**
> **Sakana の主権AI（sovereign AI）戦略は、事前学習ではなく「チューニングとオーケストレーション」による主権である。**

これは前回サーベイでの評価（「Sakana はモデル非依存に賭けている＝正しい」）を、
より強い形で裏付けると同時に、**競合脅威の性質を変える**。

| 前回の理解（v0.1） | 修正後（v0.2） |
|---|---|
| Sakana の堀＝探索エンジニアリング＋初期顧客 | それに加えて **①オーケストレーション層のモデル資産（Fugu）②日本語特化モデル（Namazu）③RSI 研究基盤** |
| Marlin は単発の商用プロダクト | Marlin は **スタックの最上層**。下に Fugu（統率）と Namazu（日本語）が敷かれつつある |
| 日本語金融は EDINET-Bench のみ | **Namazu（日本語モデル）＋ EDINET-Bench（日本語金融評価）** の組み合わせ |

## 4. IP にとっての帰結

### 戦ってはいけない場所（更新）
- ❌ マルチモデル・オーケストレーション（Fugu が製品化済み）
- ❌ 日本語の言語品質（Namazu が特化済み）
- ❌ 探索アルゴリズム（TreeQuest が OSS）
- ❌ モデルの性能（コモディティ）

### 残る場所（むしろ鮮明になった）
- ✅ **何を調べるべきかの目的関数**（decision-relevant EIG）
- ✅ **主張と原文の機械的な接地と、その劣化耐性**
- ✅ **較正の継続測定と開示**
- ✅ **顧客固有のケース記憶と、監査可能な証拠構造**
- ✅ **投資実務の工程（IC / PMI / モニタリング）への埋め込み**

> **総括**: Sakana は「**モデルとオーケストレーションの層**」を垂直に固めに来ている。
> IP は同じ縦軸で戦わず、**その上に載る「判断の質」の層**を取る。
> 極端に言えば、**Fugu を呼び出す側**に回ってよい。

## 5. 未検証（宿題に追加）

| # | 問い |
|---|---|
| Q13 | Fugu のルーティングは**外部 API として汎用に使えるか**（Marlin 専用ではないか）、価格は |
| Q14 | Fugu-Ultra の「複数エージェントのワークフロー構成」は、**どの粒度で分解しているか**（我々の並列性設計と比較したい） |
| Q15 | Marlin は内部で Fugu を使っているのか（スタックの結合度） |
| Q16 | Namazu の金融ドメイン性能（EDINET-Bench での数値） |

## 6. 出典

- `[S-104]` Sakana Fugu Technical Report arXiv:2606.21228 ／ https://sakana.ai/fugu-release/ ／ MarkTechPost（2026-06-22）／ felloai / techsy / requesty のベンチ・分解記事
- `[S-105]` Sakana Namazu（AI Weekly、OpenRouter 価格、StartupHub、sakutto）／ digitalapplied "Sakana's Playbook: Sovereign AI by Tuning Other Labs"
