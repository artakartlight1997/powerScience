---
doc_id: t-evidence-aggregation
title: "証拠の集約と信念更新 — ACH 行列から確率へ"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [bayesian, belief-update, evidence-aggregation, conflicting-evidence, source-credibility, pgm]
confidence: medium-high
primary_sources: [S-123, S-124, S-125]
related_topics: [t-structured-analytic-techniques, t-calibration-forecasting, t-decision-boundary]
contributes_to: [core-architecture, output-design]
---

# 証拠の集約と信念更新

> **ACH 行列（仮説×証拠）と、較正された確率を、どう機械的につなぐか。**
> ここは前回まで**ハンドウェーブだった部分**である。設計原則 P7 で「結論は証拠の集約規則で決める」と
> 宣言した以上、その規則の中身が要る。

## 1. LLM に素で確率を出させてはいけない

| 発見 | 内容 |
|---|---|
| **LLM は一貫してベイズ的ではない** | *LLMs are not (consistently) Bayesian*（arXiv:2605.06915）— 内的な確率的信念に**不整合**がある `[S-123]` |
| **条件付き独立と整合性に弱い** | 確率計算・不確実性定量・ベイズ更新のうち、**条件付き独立の扱いとコヒーレンスで失敗する** `[S-123]` |
| **教えれば改善する** | *Bayesian teaching enables probabilistic reasoning in LLMs*（Nature Communications）— **規範的ベイズモデルの予測を模倣させると更新能力が改善し、新規タスクにも汎化する** `[S-123]` |

> **IP への含意**: **確率の計算そのものを LLM にやらせない。**
> LLM の役割は「**変数と依存関係を言語から取り出すこと**」に限定し、
> **推論は標準的なアルゴリズムに任せる**。

## 2. 有望な型 — 言語化された確率的グラフィカルモデル（vPGM）

**BayesAgent**（Verbalized Probabilistic Graphical Modeling）`[S-124]`:

```
1. LLM に「潜在変数」と「依存関係」を同定させる（＝言語 → グラフ構造）
2. その構造に標準的なベイズ推論アルゴリズムを適用する
3. → 学習不要（training-free）のベイズ推論が成立する
```

> **これは IP の ACH 行列と、ほぼ同じ形をしている。**
> ACH の「仮説×証拠」行列は、**仮説を潜在変数、証拠を観測ノードとする PGM の簡易表現**と読める。
> したがって：
> - **LLM が担うのは**: 仮説の列挙、証拠の抽出、**尤度の定性的評価**（この証拠はこの仮説を支持/反証/中立か）
> - **アルゴリズムが担うのは**: 事後確率の計算、整合性チェック、感度分析

## 3. 矛盾する証拠をどう扱うか（投資 DD の本質）

LLM が矛盾情報に遭遇したときの既定の振る舞いは、4つに分類される `[S-125]`:

| 戦略 | 内容 | 投資 DD での評価 |
|---|---|---|
| **加重合意** | 権威の高い情報源で最も頻出する立場を採る | ✗ **多数決は真実ではない**。全員が同じ誤りを引用しうる |
| **平均化** | 数値の食い違いを中間値に寄せる | ✗ **最悪**。「売上100億 or 50億」の平均75億は存在しない |
| **抑制** | 高リスクな問いで解消不能なら引用を落とす | ✗ **矛盾こそが最も価値ある発見**なのに捨てている |
| **多視点提示** | 両論を条件つきで併記 | ○ 唯一まとも。ただし判断は先送り |

> ### 🔑 **IP は既定の振る舞いを全部拒否する。**
> **矛盾は「解消すべきノイズ」ではなく「最も価値の高いシグナル」である。**
> - 開示資料と現場ヒアリングが食い違う → **それ自体が最重要の発見**
> - したがって IP は矛盾を**検出して保存し、明示的に提示する**（平均も抑制もしない）
> - 矛盾の解消は**追加の証拠取得タスク**に変換する（＝ EIG の高いノード）

## 4. 情報源の信頼度を明示的に持つ

- 情報源の信頼度を統合する戦略として **Source Filtering / Credibility Weighting /
  Source Background Augmentation** が比較されており、
  **信頼度の手がかりを与えると LLM は矛盾証拠をより適切に解決できる** `[S-125]`
- 多視点の事実検証では、**主張の肯定形と否定形の両方について証拠を集め**、
  **情報源間の不一致をモデルの確信度から定量化**する枠組みがある `[S-125]`

> **IP の実装**: 情報源に**型と信頼度**を持たせる。
> ```
> 一次（有報 XBRL / 契約書原本 / 監査済み財務）     : 信頼度 高、ただし「開示の意図」バイアスあり
> 準一次（適時開示 / IR 説明会 / 決算説明資料）      : 高〜中
> 二次（アナリストレポート / 業界誌）                : 中
> 三次（ニュース / まとめ記事 / Wikipedia）          : 低（**引用の連鎖を辿って一次に到達させる**）
> 現場（面談 / 退職者 / 顧客ヒアリング）             : 高いが n=1。**サンプリングバイアスを明示**
> ```
> 「肯定形と否定形の両方を探す」は、**ACH の反証志向と完全に一致する**。

## 5. 集約アーキテクチャ（叩き台）

```
証拠 e_i（原文スパン + 情報源型 + 取得時刻）
   │  LLM: この証拠は仮説 H_j を 支持 / 反証 / 中立 か（★二値〜三値の局所判断のみ）
   ▼
尤度比 λ(e_i | H_j)  ← 定性ラベル（強く支持/弱く支持/中立/弱く反証/強く反証）を数値に写像
   │  ★ 写像テーブルは公開し、顧客が調整できるようにする（説明可能性）
   ▼
事後確率 P(H_j | e_1..e_n)  ← アルゴリズムで計算（LLM に計算させない）
   │  独立性の仮定を明示（同一ソース由来の証拠は独立ではない ← ここが最大の落とし穴）
   ▼
整合性チェック : 論拠の強さと確率の整合（Argumentative Coherence Filter `[S-060]`）
   ▼
較正の記録   : 実現との突合を蓄積 → Brier / ECE
```

**最大の技術的リスク**: **証拠の独立性の仮定**。
「3つの記事が同じことを言っている」は、**元が同じプレスリリースなら証拠1つ**である。
→ **引用の連鎖を辿って一次情報に正規化する**機構が必須（[t-citation-attribution](../03-evaluation/citation-attribution.md) と統合）。

## 6. 出典

- `[S-123]` *Bayesian teaching enables probabilistic reasoning in LLMs*（Nature Communications）／ *LLMs are not (consistently) Bayesian* arXiv:2605.06915 ／ Probabilistic Reasoning in LLMs
- `[S-124]` *BayesAgent: Bayesian Agentic Reasoning Under Uncertainty via Verbalized Probabilistic Graphical Modeling*
- `[S-125]` *Contradiction to Consensus: Dual-Perspective, Multi-Source Fact Verification*（OpenReview）／ *Resolving Conflicting Evidence in Automated Fact-Checking* arXiv:2505.17762 ／ *When Evidence Conflicts* arXiv:2605.14115 ／ 矛盾処理の4戦略
