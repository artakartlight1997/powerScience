---
doc_id: t-primary-research
title: "一次情報の取得 — エキスパートネットワークと質的リサーチ"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: domain
language: ja
tags: [expert-network, primary-research, interview, transcript, mnpi, commercial-dd]
confidence: medium
primary_sources: [S-135]
related_topics: [t-information-value-eig, t-pe-dd-workflow, t-regulation-compliance]
contributes_to: [product, differentiation]
---

# 一次情報の取得

> **「持たない情報」を Class C の堀に据えた以上、それをどう取るかを設計しなければ絵に描いた餅になる。**

## 1. 商業 DD における質的リサーチの実態

- **エキスパートコール** = 業界専門家・元役員・セクター専門家との構造化された対話で、
  **市場仮説と競争環境を検証または反証する** `[S-135]`
- **最大のボトルネック**: **1万語 × 30本のトランスクリプトを一貫した分析に変えること**。
  手作業ではシニアアナリストで **3〜4日** `[S-135]`

## 2. AI が既に入っている領域（2026）`[S-135]`

| 工程 | AI の役割 |
|---|---|
| **マッチング** | ブリーフを解釈し、専門家を関連度でランキング |
| **審査（vetting）** | 専門家の質を多次元で自動スコアリング |
| **コンプライアンス** | **通話中のリアルタイム MNPI 検知** |
| **洞察抽出** | トランスクリプト・ライブラリ横断の自然言語クエリ |
| **ワークフロー自動化** | 要約、トピッククラスタリング、企業間比較、**出典リンク付き出力** |
| **音声 AI** | 従来のエキスパートコールを置き換える動きも（**Expert Network Disruption**） |

> **含意**: 「トランスクリプトを要約する」層は**既に埋まっている**。
> ここで差別化しようとしてはいけない。

## 3. IP が取りに行くべき部分 — **質問の設計**

既存プレイヤーが自動化しているのは **「聞いた後」**（要約・検索・抽出）である。
**「何を聞くか」を設計する層は空いている** `C`。

```
IP の流れ:
  ① 投資仮説から「判断を反転させうる前提」を抽出（→ t-decision-boundary）
  ② 各前提について、EVPI ÷ 取得コスト でランキング（→ t-information-value-eig）
  ③ 上位の前提を「誰に、何を、どう聞けば決着するか」に変換
       - 誰に  : 元役員 / 現場の営業 / 離反顧客 / 競合の元社員 / サプライヤー
       - 何を  : ★診断的な質問（仮説を切り分ける質問）だけを聞く（→ ACH）
       - どう  : 誘導を避ける形式、事実と意見の分離、MNPI に触れない聞き方
  ④ 通話後、回答を証拠として ACH 行列に接続し、確率を更新
  ⑤ 「まだ決着していない前提」を次の通話の質問に繰り越す
```

> **エキスパートコールは1本 10〜30万円かかる。**
> **「聞くべきことを聞けたか」の価値は、要約の品質より遥かに大きい。**
> ここは EIG/EVPI の理論が最も直接的に金額換算できる場所である。

## 4. コンプライアンス上の制約（設計要件）

- **MNPI のリアルタイム検知**は既に業界標準になりつつある `[S-135]`
  → IP が質問を生成する場合、**MNPI を引き出す質問を生成しない**ことを保証する必要がある
  （例: 「未公表の受注残は」「次の四半期の着地見込みは」は **生成してはいけない質問**）
- 生成した質問には**コンプラ審査のフラグ**を付ける
- 通話記録の取り扱い（保存期間、アクセス統制）は案件隔離の対象（→ [t-agent-security](../02-methods/agent-security-and-prompt-injection.md)）

> **設計要件**: 質問生成器には**禁止パターンのフィルタ**を必ず通す。
> これは「あると良い」ではなく、**これがないと金融機関に導入できない**。

## 5. 未検証（宿題）

| # | 問い |
|---|---|
| Q27 | エキスパートネットワーク（GLG / AlphaSights / Third Bridge / ミーミル等）は、**API で質問を投入できるか**、それとも人間のリサーチャ経由か |
| Q28 | 日本の PE の商業 DD で、エキスパートコールは実際に何本／案件、いくらか |
| Q29 | MNPI 禁止質問パターンの体系（各社のコンプラ規程を参照できるか） |

## 6. 出典

- `[S-135]` Third Bridge「AI tools for primary market research 2026」「PE due diligence with AI 2026」／ InsightAgent（エキスパートネットワーク解説）／ AuraQu「Expert Network Disruption 2026: Voice AI」／ iqnetwork「How AI Is Changing Expert Networks」／ skimle（商業DDの質的リサーチ）
