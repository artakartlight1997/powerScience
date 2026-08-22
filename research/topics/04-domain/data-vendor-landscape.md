---
doc_id: t-data-vendors
title: "データベンダーの垂直統合 — 構造的には最も危険な競合"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: domain
language: ja
tags: [data-vendor, pitchbook, capital-iq, preqin, factset, connector, moat-risk]
confidence: medium
primary_sources: [S-134]
related_topics: [t-competitive-map, t-data-sources, t-finance-platforms, t-model-proof]
contributes_to: [competitive-analysis, strategy, risk]
---

# データベンダーの垂直統合

> **前回までの競合地図の穴。**
> 我々は「持たない情報こそが Class C の堀」と結論したが、
> **その情報を最初から持っている事業者がいる。**

## 1. 2026年に起きていること

| 動き | 内容 |
|---|---|
| **S&P Global** | 2025年に **With Intelligence（ウェルス・オルタナ領域のデータ提供者）を買収**。2026年7月、そのデータを **S&P Capital IQ Pro に統合**。2026年3月には Capital IQ Pro に債券・バイオファーマ・プライベート市場のデータと **AI 機能**を拡張 `[S-134]` |
| **PitchBook** | AI **「Navigator」**を投入。企業・ディール・市場テーマに関する問いに答え、将来的には**データベース全体と知的財産にアクセス**する計画 `[S-134]` |
| **PitchBook Premium Connector** | プライベート資本市場データを **Claude / ChatGPT / Perplexity Finance / Microsoft Copilot Studio / Hebbia / Rogo / Model ML** などのエンタープライズ AI ツールに供給 `[S-134]` |
| **Rogo** | **PitchBook / Preqin / S&P Capital IQ と提携**し、サードパーティデータと社内データを統合 `[S-134]` |
| **Hebbia** | **FactSet / PitchBook / S&P Capital IQ / Preqin** と統合 `[S-134]` |

## 2. 何が起きているかの解釈

```
      【データ層】              【アプリ層】
   PitchBook / S&P /  ──────▶  Rogo / Hebbia / Model ML / Copilot / Claude / ChatGPT
   Preqin / FactSet      ↑
                    Connector 経由でどこへでも供給
```

**データベンダーは「特定のアプリに独占供給する」のではなく、
コネクタで全アプリに供給する道を選んでいる** `[S-134]`。

### これが意味すること

| 論点 | 含意 |
|---|---|
| **アプリ層は差別化しにくくなる** | 同じデータが Rogo にも Hebbia にも Claude にも流れる。**データによる差別化はアプリ層では起きない** |
| **価値はデータ層に留まる** | commoditize your complement の構図 `[S-120]` — **アプリを商品化して、データを希少に保つ** |
| **ただしベンダーは「公開されたプライベート市場データ」しか持たない** | ディール情報、ファンド情報、企業プロファイル。**個別案件の VDR・面談・自社の判断履歴は持たない** |
| **ベンダー自身がアプリに降りてくるリスク** | PitchBook Navigator は「将来的にデータベース全体にアクセス」`[S-134]`。**垂直統合の意思がある** |

## 3. IP へのリスク評価

### ⚠️ リスク（高）
1. **「データを持っている」ことによる差別化は成立しない**。
   ベンダーデータは誰でも買え、コネクタで誰のアプリにも入る。
2. **ベンダーが反証・較正レイヤに降りてきたら、データ＋分析で完結される**。
   ただし現状、彼らが売っているのは「検索と要約」であり、**反証と較正ではない** `C`。
3. **調達の構図**: ファンドは既にベンダーに年間数千万円を払っている。
   **IP の予算は「新規」ではなく「既存ベンダー予算の奪い合い」**になる可能性。

### ✅ 緩和と機会
1. **我々の Class C は「ベンダーが持たない情報」に限定して定義し直す**:
   - 顧客固有: VDR、IC メモ、面談記録、**過去に見送った案件と理由**
   - 一次情報: 自前で設計した専門家質問、退職者・顧客への接触
   - **ベンダーデータは「買って使う入力」であって、我々の堀ではない**
2. **ベンダーの上に載る**: コネクタで供給されるなら、**我々も同じデータを使える**。
   差は**そのデータで何をするか**（反証・較正・監査）だけになる。これは元々の主張と整合。
3. **むしろ提携先候補**: Rogo が PitchBook / Preqin / Capital IQ と組んだように、
   **IP もデータ層とは競合せず、供給を受ける立場**を取るのが自然。

## 4. 更新: 競合地図の三層

```
【データ層】  PitchBook / S&P Capital IQ / Preqin / FactSet / Moody's
                 ↓ コネクタで全アプリへ供給（差別化されない共通入力に）
【アプリ層】  Rogo / Hebbia / BlueFlame / AlphaSense / Marlin / Gemini DR
                 ↓ 検索・抽出・要約・定型生成（コモディティ化しつつある）
【判断層】    ★ Integral Prism（空白）
                 反証 / 較正 / 監査可能な証拠構造 / 顧客固有の記憶
```

> **結論**: データ層とは戦わない（買う・組む）。アプリ層とも正面では戦わない（上に載る）。
> **判断層を定義して取る。**

## 5. 未検証（宿題）

| # | 問い |
|---|---|
| Q24 | PitchBook Navigator / Capital IQ の AI 機能は、**反証や確度提示に踏み込んでいるか**（現状は検索と要約と見ているが未確認） |
| Q25 | 日本の PE が実際に契約しているデータベンダーと年間予算（Speeda / 帝国データバンク / 東京商工リサーチ / PitchBook 等） |
| Q26 | ベンダーのライセンス条項は、**AI エージェントによる利用・再加工を許すか**（重要な実務制約） |

## 6. 出典

- `[S-134]` S&P Global プレスリリース（2026-03 / 2026-07、With Intelligence 統合）／ PitchBook Navigator・Premium Connector ／ Rogo のデータ提携 ／ Hebbia の統合一覧 ／ 各種比較記事（2026）
