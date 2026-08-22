---
doc_id: t-finance-platforms
title: "金融特化リサーチ製品 — AlphaSense / Hebbia / Rogo / BlueFlame"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: competitors
language: ja
tags: [competitor, alphasense, hebbia, rogo, blueflame, fintech, workflow]
confidence: medium
primary_sources: [S-081]
related_topics: [t-pe-dd-workflow, t-competitive-map, t-pricing-unit-economics]
contributes_to: [competitive-analysis, positioning]
---

# 金融特化リサーチ製品

Marlin / Google DR とは別レイヤの直接競合。**実務ワークフローの入口を既に押さえている。**

## 1. 各社

| プロダクト | 中核 | 強み | 空白 |
|---|---|---|---|
| **AlphaSense** | 市場・競合インテリジェンス | 14年の歴史、**6,000社**の顧客、エキスパートコール書き起こし、AI エージェントでピッチ準備・DD リサーチ・市場分析 `[S-081]` | 汎用検索寄り。**判断の較正は扱わない** |
| **Hebbia（Matrix）** | 大規模文書横断の**並列クエリ**と構造化抽出 | 膨大な文書集合に対する行列型のクエリ実行と結果の構造化 `[S-081]` | **抽出**が中心。仮説と反証の構造がない |
| **Rogo** | セルサイド IB ワークフロー特化 | コンプス、企業プロファイル、**CIM**、ピッチ資料の自動化 `[S-081]` | 定型成果物の自動化。判断支援ではない |
| **BlueFlame AI（Amp）** | ディールサイクル全体の**オーケストレーション** | ソーシング/DD/IC準備/ピッチ/実行/ポートフォリオ監視/ボード報告。金融ネイティブで、モデル・ツール・自社コンテンツ・データ源を束ねる `[S-081]` | 束ねるところまで。**反証・較正は未対応** |

推奨用途の整理（各社比較記事より）`[S-081]`:
- 大規模コーパスのリサーチ統合 → Hebbia
- 市場・競合インテリジェンス → AlphaSense
- IB アナリストの生産性 → Rogo
- ディールサイクル横断のワークフロー → BlueFlame

## 2. 読み取り

### (a) 「抽出」と「生成」は既に埋まっている
文書から数字と条項を取り出す、定型資料を作る — これは**コモディティ化済み**。
ここで戦うと、既存顧客基盤と統合の深さで負ける。

### (b) 誰も「反証」と「較正」を売っていない
全員が **「速く・多く・きれいに作る」** を売っている。
**「間違っている確率を下げる」「確からしさを較正する」**を売っている製品は観測されない `C`。

### (c) BlueFlame が最も近い脅威
「オーケストレーション」を名乗っている＝IP と同じ層に来る可能性がある。
ただし現状は**モデル/ツール/コンテンツの束ね**であり、目的関数の設計には踏み込んでいない `C`。

## 3. Integral Prism の取り方

| 戦い方 | 評価 |
|---|---|
| 抽出精度で勝つ | ✗ 既存勢が有利 |
| 定型成果物の自動生成で勝つ | ✗ Rogo/Marlin と正面衝突 |
| **既存製品の出力を「叩く」層になる** | ◎ 補完的に入れる（Hebbia の抽出結果を IP が反証する、等） |
| **反証・較正・監査という新しい軸を定義する** | ◎ 本命 |

→ 具体的な入口案は `notes/discussion-agenda.md` D10（IC メモの反証パス）。

## 4. 出典

- `[S-081]` https://blueflame.ai/blog/blueflame-ai-vs-rogo-vs-hebbia ／ AlphaSense 比較ページ ／ v7labs 比較記事 ／ Forbes "Fintech's Latest Trend: AI Agents For Investment Research"
