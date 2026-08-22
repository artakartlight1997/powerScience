---
doc_id: cs-index
title: "Integral Prism — 実装戦略インデックス"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: strategy-index
language: ja
tags: [strategy, build, implementation, roadmap]
depends_on: [research-index]
---

# Integral Prism / 実装戦略

**`../` のサーベイ（64トピック・出典120件・設計原則20）から、「何を作るべきか」を導いた文書群。**

> ⚠️ **これはアーキテクチャの確定ではない。**
> 本フォルダは3種類の内容を **厳格に区別**して書く。
>
> | 記号 | 意味 |
> |---|---|
> | 🔒 **確定** | リサーチから機械的に導かれ、**議論の余地がないもの**（原則 P に紐づく） |
> | 🔧 **推奨** | リサーチから導かれるが、**実装の選択肢が複数あるもの** |
> | ❓ **未決** | **顧客と事業判断が要るもの**（`../notes/discussion-agenda.md` の D1–D10） |
>
> 「作れるか」を決める技術検証（M0）を先に回すこと。**M0 が通るまで、M1 以降は仮の計画である。**

## 読む順番

| # | ファイル | 内容 |
|---|---|---|
| 00 | [00-from-research-to-requirements.md](00-from-research-to-requirements.md) | **設計原則 P1–P20 → 実装要件**への変換表（本フォルダの根拠） |
| 01 | [01-what-to-build-and-not.md](01-what-to-build-and-not.md) | **作るもの / 作らないもの**の線引き |
| 02 | [02-evidence-graph.md](02-evidence-graph.md) | **★中心データモデル**（証拠グラフ）— ここから全部が生える |
| 03 | [03-components.md](03-components.md) | コンポーネント一覧と責務（L0–L9 の実体） |
| 04 | [04-build-buy-borrow.md](04-build-buy-borrow.md) | 自作 / 購入 / OSS 利用の判断 |
| 05 | [05-milestones.md](05-milestones.md) | **M0（検証）→ M4** と各段階の終了条件 |
| 06 | [06-tech-choices.md](06-tech-choices.md) | 技術選択の指針 |
| 07 | [07-quality-gates.md](07-quality-gates.md) | 出荷ゲート（CI で測るもの） |
| 08 | [08-risks-and-kill-criteria.md](08-risks-and-kill-criteria.md) | **何が起きたら止めるか** |
| 09 | [09-open-decisions.md](09-open-decisions.md) | 実装に効く未決定事項 |

## 一枚の結論

> **作るのは「賢いリサーチエージェント」ではない。**
> **作るのは「投資判断の証拠グラフを構築・検証・較正し、追記専用で記録する機械」である。**
>
> 探索も、生成も、モデルも、オーケストレーションも、**すべて外から調達できる部品**であり、
> それらは**モデルの進歩に食われる**（Class A）。
> 食われないのは **①較正された確度 ②特権を持つ検証 ③持たない情報 ④責任の記録** の4つで、
> **その4つは全て、たった1つのデータ構造（証拠グラフ）の上に載る。**
>
> → だから **最初に作るのは証拠グラフであり、それ以外ではない。**

## 最短の道筋

```
M0  技術検証（4本）        「そもそも作れるか」を確かめる       ← 今ここ
 ↓  ★ここが通らなければ、以降の計画は書き直し
M1  薄い縦串（1工程）      既存 IC メモを叩いて穴を出す
 ↓
M2  探索の目的関数         決定フレーム → EVPI 駆動探索 → 停止
 ↓
M3  較正と評価             反実仮想 DD、Brier/ECE の蓄積と開示
 ↓
M4  記憶と常駐監視         ケースベース記憶、thesis tracking
```

## 記法

- `P1`–`P20` … 設計原則（[../metadata/taxonomy.json](../metadata/taxonomy.json)）
- `C-001`–`C-066` … 事実主張（[../metadata/claims.json](../metadata/claims.json)）
- `[S-001]`–`[S-136]` … 出典（[../metadata/sources.json](../metadata/sources.json)）
- `L0`–`L9` … 機能層（taxonomy.json の `layers`）
- `D1`–`D10` … 未決の論点（[../notes/discussion-agenda.md](../notes/discussion-agenda.md)）
- `Q1`–`Q31` … 一次確認の宿題（[../notes/open-questions.md](../notes/open-questions.md)）
