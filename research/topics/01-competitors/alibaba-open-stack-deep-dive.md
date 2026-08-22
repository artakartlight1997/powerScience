---
doc_id: t-alibaba-stack-deep
title: "Alibaba(Tongyi)公開DRスタック精読 — 動く実装から取れる機構(確度A)"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: competitors
language: ja
tags: [tongyi, deepresearch, webweaver, iterresearch, resum, primary-source]
confidence: high(リポジトリをフルクローン+同梱Tech Report(arXiv:2510.24701)直読)
related_topics: [t-tongyi-deepresearch, t-draft-guided-research, arch-dominance-proof]
contributes_to: [dominance-proof, architecture, L5]
---

# Alibaba 公開DRスタック精読(一次資料)

> 原本: scratchpad/deep-dives/alibaba-dr-stack.md。リポジトリのフルクローンと
> 同梱 Tech Report PDF の直読に基づく(確度A)。**商用級ディープリサーチの
> 「動く実装」を読める唯一の対象**であり、機構の現実的な相場観を与える。

## 1. Tongyi DeepResearch 30B-A3B の実像 [A]

- 推論3形態: (a) **vanilla ReAct**(「Bitter Lesson」を理由に明示採用。110Kトークン
  超で強制回答フォールバック) (b) **IterResearch** = 毎ラウンド「質問+進化する
  レポート+直前の観測」だけにワークスペースを**全再構成**する Markov 的文脈管理
  (c) **Heavy モード** = n 並列 IterResearch の圧縮レポートのみを統合モデルが合成
- 成績: HLE 32.9 / BrowseComp 43.4 / FRAMES 90.6、Heavy で HLE 38.3
- 学習: Agentic CPT → 混合SFT(ReAct+レポート統合の両形式)→ 厳密 on-policy
  GRPO改(0/1報酬のみ)→ モデルマージ。報告書自身が
  「**RL はアルゴリズムよりデータ品質と環境安定性**」と結論

## 2. WebWeaver の実装実体 [A: コード全読]

- 証拠メモリバンクの実体は `page_info=[{url,goal,summary,evidence}]` + 連番 `url2id`
  の**単純なリスト/辞書**。summary のみ ID 付きでコンテキスト内、長文 evidence は
  コンテキスト外(=我々の「文脈にはID、本体は台帳」P8 と同型)
- Planner: 検索とアウトライン更新を交互反復(引用ID必須・最低3回再構成)
- Writer: 節ごとに ID 指定 retrieve(20K上限)→執筆→**書き終えた節の証拠を
  履歴からマスク**(context rot 対策の実装形)
- 引用精度 93.37%(対 Gemini 78.3 / OpenAI DR 75.0)[B]

## 3. 学習なしで流用できる機構(precisely このリスト) [A]

1. **WebWeaver 全体**(公式実装が汎用API前提)
2. **goal 条件付き visit 要約器**(取得ページを {rational, evidence, summary} に落とす二段構成)
3. **ReSum**: 文脈閾値到達時に要約して再開(後付け可能・無学習で +4.5%)
4. **Heavy 並列統合**(並列ワーカーの圧縮レポートのみを統合)
5. バッチ検索 / SelectURL / 打ち切りフォールバック

学習が必須なのは「素の ReAct の探索力」と「IterResearch の統合品質」のみ。

## 4. 我々への含意

- **context rot 対策は「実装済みの定石」が存在する**(節別マスク・ワークスペース
  再構成・参照渡し)。独自発明ではなく定石の採用として設計に入れる
- 証拠メモリは凝ったグラフDBでなく単純構造で 93% の引用精度が出ている —
  我々の SQLite 台帳の方向性を支持
- RL は「データ品質の勝負」という当事者の結論は、内製第一段で RL を採らない
  判断(t-rl-search-agents)を補強する
