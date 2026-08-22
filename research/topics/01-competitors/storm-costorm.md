---
doc_id: t-storm-costorm
title: "STORM / Co-STORM — 多視点質問生成と協調的談話プロトコル"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: competitors
language: ja
tags: [storm, co-storm, stanford, multi-perspective, outline, discourse, oss]
confidence: high
primary_sources: [S-031]
related_topics: [t-long-form-report, t-human-in-the-loop, t-structured-analytic-techniques]
contributes_to: [question-generation, report-structure]
---

# STORM / Co-STORM（Stanford OVAL）

**「良い質問はどこから来るのか」に対する、最も明快な公開実装。**

## 1. STORM

**S**ynthesis of **T**opic **O**utlines through **R**etrieval and **M**ulti-perspective question asking `[S-031]`

```
1. 視点の発見    : 類似トピックの既存記事を調査し、複数の perspective を抽出
2. 模擬対話      : 各視点の「ライター」と「専門家」の会話を、Web 検索に接地して実行
                   → 理解が更新され、フォローアップ質問が深くなる
3. アウトライン化: 発見を構造化された目次に統合
4. 執筆          : 出典つきの長文記事を生成
```

**核心**: 質問の質は **視点の多様性**から生まれる。
単一視点で深掘りしても、盲点は盲点のまま残る。

## 2. Co-STORM

- 複数の LLM 専門家 ＋ **人間**が参加する**協調的談話プロトコル** `[S-031]`
- **ターン管理方針**を持ち、誰がいつ発言するかを制御 `[S-031]`
- 専門家は外部知識に接地した回答を出すか、談話履歴に基づくフォローアップ質問を出す `[S-031]`
- 発見を蓄積する**動的マインドマップ**を維持

## 3. Integral Prism への含意

### ✅ 視点テンプレートを持つ（自動発見に任せない）
STORM は視点を「既存記事から自動発見」する。
これは百科事典向けの設計であり、**投資 DD では不十分**。
なぜなら [t-structured-analytic-techniques](../02-methods/structured-analytic-techniques.md) が警告する通り、
**LLM が出す視点は訓練分布＝主流コンセンサスに偏る** `[S-061]`。

IP では **実務由来の視点テンプレート**を明示的に持つ：

| 視点 | 問い |
|---|---|
| 買い手（自分） | この価格で買う理由は |
| 売り手 | なぜ今売るのか |
| 競合 | この会社をどう潰すか |
| 顧客 | 明日から乗り換える理由はあるか |
| **退職者** | なぜ辞めたか |
| 債権者 | 資金繰りのどこが危ないか |
| 規制当局 | どの規制変更が効くか |
| 労働組合 / 従業員 | PMI で何が壊れるか |
| サプライヤー | 依存と交渉力はどうか |
| **将来の自分（premortem）** | 3年後この投資が失敗しているとしたら理由は |

### ✅ Co-STORM のターン管理は、人間介入の設計に効く
「人間がいつ割り込めるか」を**プロトコルとして定義する**発想。
→ [t-human-in-the-loop](../02-methods/human-in-the-loop.md)

### ⚠️ STORM は静的ワークフロー
DR タクソノミ上は**静的**（人が設計した固定パイプライン）`[S-019]`。
IP は動的ワークフローを取るので、STORM は**部品として（視点生成と目次生成）**使う。

## 4. 出典

- `[S-031]` https://github.com/stanford-oval/storm ／ https://storm-project.stanford.edu/research/storm/
