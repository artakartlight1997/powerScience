---
doc_id: notes-open-questions
title: "未検証事項・一次確認の宿題"
version: 0.1.0
status: open
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: worklist
language: ja
tags: [open-questions, verification-backlog]
---

# 未検証事項（一次ソース確認の宿題）

本調査は Web 検索結果に基づく。実行環境のエグレス制限で **sakana.ai / arxiv.org / ai.google.dev の本文を直接取得できていない**。
以下は**設計判断に効くのに確度が足りない**項目。優先度順。

| # | 問い | 現状の確度 | 確認方法 |
|---|---|---|---|
| Q1 | **Marlin の探索報酬は何か**（自己評価か、外部検証か、人間フィードバックか） | D | sakana.ai/marlin-release 原文、Marlin のトライアル、AB-MCTS 論文 §手法 |
| Q2 | Marlin は本当にマルチベンダのモデルを本番で使っているか（AB-MCTS 論文の話と製品は別かもしれない） | C | 製品ドキュメント、規約のサブプロセッサ一覧 |
| Q3 | Marlin の出典検証の実態（引用は機械検証されているか） | D | 実際に1本走らせて引用を全数チェック（→08 評価B をそのまま適用） |
| Q4 | Marlin の実勢価格・年間契約の実態 | B | 代理店/直販ヒアリング |
| Q5 | Gemini DR の内部が本当に単一エージェントか（サブエージェントの有無） | B | Google の技術ブログ、DR API のトレース |
| Q6 | co-scientist の Elo が judge バイアスをどう扱っているか | D | Nature 論文本文 §methods |
| Q7 | `Cited but Not Verified` の -42% の実験条件（どのモデル、どのタスク） | B | arXiv:2605.06635 本文 |
| Q8 | ForecastBench の「superforecaster 同等」の条件（質問種別・期間） | B | ForecastBench 論文・リーダーボード |
| Q9 | EDINET-Bench のタスク定義（不正検知等か、DD 的推論か） | C | sakana.ai/edinet-bench 原文 |
| Q10 | EU AI Act 高リスク該当性：投資リサーチ支援は高リスクか（附属書III の解釈） | C | 法務レビュー |
| Q11 | AB-MCTS の実運用コスト（ARC-AGI-2 39.2% を出すための呼び出し回数と単価） | D | 論文 appendix、TreeQuest の実測 |
| Q12 | 日本の PE における実際の支払い意思（1案件あたりいくらまで） | D | 顧客インタビュー 5〜10件 |

## 検証の進め方（提案）

1. **Q3 を最優先**。Marlin を1本走らせ、引用を全数機械検証する。
   → 「競合の引用精度が実測でこれだけ低い」は、**そのまま我々の最初の営業資料**になる。
2. Q12（顧客ヒアリング）を並行。D1/D3/D10 の答えは顧客からしか出ない。
3. 論文一次資料（Q1/Q6/Q7/Q11）はネットワーク制限のない環境でまとめて取得する。
