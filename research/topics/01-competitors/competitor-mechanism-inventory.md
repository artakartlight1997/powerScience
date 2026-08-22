---
doc_id: t-competitor-mechanisms
title: "競合4システムの機構目録(GDR / OpenAI DR / Kimi / Perplexity)— PO-1の物差し"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: competitors
language: ja
tags: [mechanism-inventory, gdr, openai-dr, kimi, perplexity, po-1]
confidence: medium-high(一次ソース本文の引用スニペットを多方向交差)
related_topics: [t-google-gemini-dr, t-openai-dr, arch-dominance-proof]
contributes_to: [dominance-proof]
---

# 競合機構目録(要約版。原本: scratchpad/deep-dives/competitor-mechanisms.md)

| カテゴリ | Gemini DR | OpenAI DR | Kimi-Researcher | Perplexity DR |
|---|---|---|---|---|
| 計画 | 生成→**ユーザー承認/編集必須**+反復再計画 | 明確化質問→計画(編集可・承認弱) | クラリファイのみ、以降RL内部化 | 承認ゲートなし |
| 探索制御 | 多角クエリ一括+ギャップ特定ループ | 5-30分自律、RL学習のバックトラック | 平均23ステップ・70+クエリ・50+イテレーション | 20-50クエリ・2-4分 |
| 検索 | Google検索+**本文読解**+Workspace/MCP | 検索+クリック+スクロール+**Python sandbox** | 並列検索+ブラウザ+コード、200+URL | 自社検索エンジン |
| 検証 | リンク引用+**自己批判複数パス** | 文単位引用(検証機構は明示なし) | 矛盾ソースの相互検証(RLで創発) | インライン引用(FACT 90.24%で1位) |
| 文脈管理 | **1M+RAG** | 不明 | **学習された文脈管理**(破棄で10→50+イテレーション) | 不明 |
| 実行基盤 | **非同期タスクマネージャ・共有状態・部分回復** | background mode+webhook | 非同期rollout・turn-level partial(1.5x) | 同期高速 |
| 学習 | 非公開(多段計画のデータ効率学習) | **end-to-end RL**(o3 FT、multi-task+ルーブリック報酬: 一次引用で確認) | end-to-end agentic RL(REINFORCE変種) | R1改(報道)+TTC |
| 弱点(自認/第三者) | 浅い分析・SEO混入・冗長 | 幻覚・権威/噂の弁別・**確信度較正の弱さ(自認)** | 第三者ベンチほぼ無し | 引用幻覚率37%報告・深さ不足 |

## 重要な単発事実

- OpenAI の「end-to-end RL」は発表文の一次引用で確認(o1と同じRL手法・o3 FT・
  multi-task RL+開放課題はルーブリック採点)
- **FutureSearch のベンチでは「素の o3+search が OpenAI DR を上回る」逆転報告**
  (arXiv:2506.06287, 確度中)— end-to-end RL の優位は絶対ではない
- Gemini DR は RACE 総合1位(48.88)だが引用**精度**は Perplexity に劣後。
  有効引用数 111.21(量で圧倒)
- 全社: ステップ/クエリ上限は未公表。報酬設計は Kimi 以外非公開
- 目録の穴(要追跡): 2026世代(GPT-5.2系DR、DR Max: HLE 54.6 / BrowseComp 85.9
  自己申告)は再計測前の概要のみ
