---
doc_id: t-verification-claims-audit
title: "検証系・劣化系の主張の裏取り監査 — 確認/訂正/棄却"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: evaluation
language: ja
tags: [claims-audit, verification, fineverify, deepfact, deephallubench, reward-hacking, citation]
confidence: high(裏取り済み)
related_topics: [t-tree-search-algorithms, t-citation-attribution, t-llm-judge-reliability]
contributes_to: [dominance-proof, architecture]
---

# 主張の裏取り監査(アーキテクチャの根拠に使う前の検品)

> 我々自身の規律: **裏取りされていない数値を設計の根拠にしない。**
> 本書はアーキテクチャ v2/v3 が依拠した主張を原典(GitHub raw / 多方向スニペット)で
> 監査した結果である。「訂正」は**本日(2026-08-22)以降に作成・改訂される文書**で
> 修正済みの形のみを使う。旧文書(SUMMARY・coding-strategy 等の初期サーベイ)への
> 遡及一括改訂は別作業として登録(旧「39-77%」「26→58%を時間依存劣化とする併記」が
> 残存箇所あり — sources.json は更新済み)。

## 確認(そのまま使ってよい)

| 主張 | 判定 | 正確な内容 | 出典 |
|---|---|---|---|
| FineVerify: サブ質問分解の検証で候補選択が改善 | **確認(A)** | supported/not-found/contradicted の3値採点。4軌跡で GPT-5-mini +8.2pt(4ベンチ平均)、Gemini-3-flash +5.6%。12サンプルで GPT-5 超え(BrowseComp-Plus) | arXiv:2606.00660, repo README |
| DeepFact: Audit-then-Score で 60.8%→90.9% | **確認(A)+注意** | 数値は**ベンチのラベル(検証者)精度**であってエージェント精度ではない。PhD級専門家の単独ラベルでも 60.8% しかない、という「検証の難しさ」の証拠として使う | arXiv:2603.05912, repo kkkevinkkkkk/DeepFact |
| ルーブリックRLは網羅性に偏り事実性を劣化させる | **確認(A)** | ルーブリック判定者は RL 後を 85.8% で選好、ルーブリック**フリー**判定者は 78.4% でベースを選好。強い検証器でも排除不可 | arXiv:2605.12474 |
| 引用URLの捏造・非解決 | **確認(A)** | 捏造 3–13%、非解決 5–18%(分野差: Business 5.4%〜Theology 11.4%)。同論文の別計測: 商用DRAの**引用正確性78–94%(=誤り率6–22%)** — 両表記は同一論文の別指標であり矛盾しない | arXiv:2604.03173 |
| ツール呼び出し増で引用の事実正確性が劣化(旧 S-057) | **確認+精密化(A)** | **元論文を特定: arXiv:2605.06635 "Cited but Not Verified"**。2→150呼び出し(7段階)で Fact Check 平均約 −42pt。ただし**モデル分散が大きい**(GPT系 −62pt、Claude系 −22pt)。**Link Works/Relevant は 92% 超で安定 = 劣化は「統合段階」特異**(リンク切れ検査では捕捉できない)。Fact Check の水準は **24%(OSS-120B)〜77%(Claude Opus 4.5)** — 旧記載 39–77% は下限改訂(sources.json S-057 更新済み) | arXiv:2605.06635 |

## 訂正(以後この形でのみ使う)

| 旧主張(誤りまたは過剰) | 訂正後 |
|---|---|
| DeepHalluBench の分類は「PIES」 | **PING**(Propagation / Intent / Noise-induced / Grounding)。100タスク×6システム |
| 「計画段階の幻覚が複利で増幅する(定量)」 | **定性的傾向としては確認、定量値は原典で確認できず**。設計根拠には「計画誤りは下流にカスケードする(定性)」までしか使わない |
| 「探索を長くするほど報酬ハッキングが悪化(SpecBench)」 | **不正確**。SpecBench の主結果は「コード規模10倍ごとに Δ+28pt」「支配要因はタスク難度と能力のギャップであり、探索戦略の影響は小さい」。**長時間劣化の根拠には 2605.06635(引用正確性)だけを使う** |

## 確認できず(設計の根拠から降ろす)

- DeepHalluBench の複利伝播の定量値
- DeepRubric の公開コード(論文 arXiv:2606.17029 のみ。手法内容は A- で確認)

## 設計への含意(監査から出た追加要件)

1. **可視ゲートは飽和される**: ルーブリック(=我々の固定スペック)が見えていれば、
   生成側は「項目を埋めた風」に最適化しうる。→ **held-out の抜き打ち検査**
   (スペック外の合成チェック・ランダムな原文再照合)を品質管理に組み込むこと
2. **リンク検証は劣化を捕捉しない**: 劣化は統合段階(引用と本文の対応)で起きる。
   → 我々の grounding(逐語引用の原文照合)はまさに統合段階の検査であり、
   リンク到達性検査で代用してはならない
3. **数値は分散込みで引用する**: 「-42%」単独ではなくモデル分散(−62〜−22pt)込みで
