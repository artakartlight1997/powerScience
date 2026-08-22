---
doc_id: t-human-in-the-loop
title: "人間との協働 — 自律性-対話のジレンマと介入点設計"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [hitl, mixed-initiative, steering, intent, pomdp, interaction]
confidence: medium-high
primary_sources: [S-032, S-033, S-034, S-035]
related_topics: [t-sakana-marlin, t-google-gemini-dr, t-storm-costorm]
contributes_to: [ux, differentiation]
---

# 人間との協働（Mixed-Initiative）

**Marlin は「8時間放置」を売る。研究は「ユーザは操舵したい」と言う。ここが空いている。**

## 1. 研究の指摘

| 研究 | 指摘 |
|---|---|
| **InterDeepResearch**（arXiv:2603.12608）`[S-032]` | 既存 DR はユーザの介入モデルが貧弱。**ユーザはリアルタイムに研究方向を操舵したいという明確な要求を持つ** |
| **Interaction as Intelligence**（arXiv:2507.15759）`[S-033]` | 深いリサーチは**人間-AI パートナーシップ**として設計すべき |
| **IntentRL**（arXiv:2602.03468）`[S-034]` | オープンエンド DR における **autonomy-interaction ジレンマ**を定式化。<br>**潜在意図の明確化を POMDP として扱い**、RL で「いつ聞くか」を学習。報告のユーザ意図適合が改善 |
| **選好エージェント** `[S-032]` | ユーザのクエリ修正・情報源の選択パターンを追跡し、ドメインや刊行物種別の選好を学習 |
| 実務レビュー `[S-035]` | 2026年、HITL は「オプションの安全網」ではなく**信頼できる AI の中核機能** |

## 2. 現行製品の介入モデル

| 製品 | 介入 |
|---|---|
| Sakana Marlin | ほぼ無し（投げて8時間待つ）`C` |
| Gemini Deep Research | **計画の承認・編集**（実行前の1回）`[S-018]` |
| Co-STORM | **協調的談話プロトコル**（ターン管理あり）`[S-031]` |
| Anthropic Research | 実行中の介入は限定的 |

## 3. IP の介入点設計（4点）

> **設計原則 P4: 自律だけを売らず、介入点を設計して売る。**

| # | 介入点 | 人間がすること | 効果 |
|---|---|---|---|
| **I1** | **仮説集合の承認** | 「この5つで漏れはないか」「6つ目を足す」 | LLM の主流バイアスを人間の経験で補正（→ ACH の警告 `[S-061]`） |
| **I2** | **反証課題の優先順位** | 「まずキーマン依存を潰せ」 | 予算配分を実務判断で上書き |
| **I3** | **一次情報の投入** | VDR 資料、面談メモ、業界人脈の情報を入れる | **公開情報だけでは届かない領域**に到達 |
| **I4** | **確度の上書き** | 「この確率は低すぎる、根拠はこれ」 | 較正の教師データが貯まる（→ 記憶へ） |

**重要な設計判断**: 介入は **任意（割り込みポイント）**であり、放置すれば自律で走る。
「介入必須」にすると、Marlin の8時間自律に対して**手間が増えた製品**に見える。

## 4. 介入の価値を可視化する

介入は「手間」と受け取られうる。したがって、
**介入1回で何が変わったかを定量表示する**（→ 未決論点 D5）。

```
例: あなたが I1 で追加した仮説「チャネル依存」は、
    その後の探索で 3件の反証課題を生み、うち1件が
    重要な事実（上位2社で売上の68%）に到達しました。
    この仮説の追加により、Go 判断の確率が 71% → 54% に変化しました。
```

これは **人間の貢献を可視化する**という点で、
「AI に仕事を奪われる」という導入抵抗への直接的な回答にもなる。

## 5. 出典

- `[S-032]` *InterDeepResearch* arXiv:2603.12608
- `[S-033]` *Interaction as Intelligence: Deep Research With Human-AI Partnership* arXiv:2507.15759
- `[S-034]` *IntentRL* arXiv:2602.03468
- `[S-035]` HITL 2026 実務レビュー各種
