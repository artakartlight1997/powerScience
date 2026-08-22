---
doc_id: t-sakana-evolution-rsi
title: "Sakana の進化・自己改善系譜 — Model Merge / ShinkaEvolve / ALE-Agent / Digital Red Queen / RSI Lab"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: competitors
language: ja
tags: [sakana, evolution, rsi, model-merge, adversarial-coevolution, red-team]
confidence: medium
primary_sources: [S-007, S-013, S-014, S-015]
related_topics: [t-multi-agent-debate, t-differentiation-hypotheses]
contributes_to: [architecture, red-team-design, competitor-trajectory]
---

# Sakana の進化・自己改善系譜

**Sakana は一貫して「大きくする」ではなく「組み合わせる／進化させる」に賭けている。**
Marlin はその系譜の商用化第一号にすぎず、**次に何が来るか**を読むにはこの系譜を見る必要がある。

## 1. 各研究

| 研究 | 年 | 内容 | IP への示唆 |
|---|---|---|---|
| **Evolutionary Model Merge** | 2024 | 進化計算で複数モデルを統合し、特化モデルを作る `[S-013]` | 「顧客固有の特化を、学習なしで作る」発想の源流 |
| **ShinkaEvolve** | 2025 | オープンエンドかつ**サンプル効率の良い**プログラム進化 `[S-014]` | 探索効率そのものを最適化する系譜 |
| **ALE-Agent** | 2025 | 最適化エージェント。**AtCoder Heuristic Contest 058 で 804人中1位** `[S-007]` | 報酬が明確な領域での圧倒的な強さの実証 |
| **Continuous Thought Machines** | 2025 | ニューロン同期のダイナミクスで解く新アーキテクチャ `[S-014]` | 直接の関連は薄い（基礎研究） |
| **Text-to-LoRA** | 2025 | **テキスト記述から LoRA アダプタを生成**するハイパーネットワーク `[S-014]` | 「案件記述 → 専門家アダプタ生成」の将来オプション |
| **Digital Red Queen** | 2026 | MIT 共同。Core War で LLM が**敵対的に相互進化**。約250世代で人間設計プログラムを常時撃破 `[S-015]` | **反証役の自動強化**。IP のレッドチーム設計に直結 |
| **RSI Lab** | 2026-06 設立（東京） | AI 開発プロセス自体を AI で再設計。共同創業に **Llion Jones**（"Attention Is All You Need" 著者）。負の結果も含めて公開する方針、自己改善ループへの検証可能な安全策を最初から組む方針 `[S-007]` | Sakana の中長期の賭け。**計算資源の軍拡競争を回避する**戦略 |

## 2. Digital Red Queen を深掘りする理由

IP にとって、この系譜で**最も転用価値が高いのは DRQ** `[S-015]`。

- 各ラウンドで、モデルは**それまでの全ての「戦士（プログラム）」を倒す新しい戦士を進化させる**
- 結果として、**敵対者が世代を通じて強くなり続ける**
- 約250反復で人間設計のプログラムを常時撃破するに至った

**IP への転用**: 「投資仮説を殺す役（レッドチーム）」を固定プロンプトで置くのではなく、
**過去に見逃した反証パターンを蓄積し、反証役を世代的に強くする**。
→ [t-memory-continual-learning](../02-methods/memory-and-continual-learning.md) と接続すると、
「ファンドの失敗の記憶」が「反証役の強さ」に変換される。これは競合が持たない循環。

## 3. 競合トラジェクトリの読み

RSI Lab の存在は、Sakana が **Marlin を主力事業にする気があるのか**を曖昧にする `C`。

- 仮説A: Marlin はキャッシュエンジンで、本命は RSI（研究組織としての賭け）
- 仮説B: Marlin で金融顧客を押さえ、RSI の成果を逐次投入して離されないようにする

どちらでも、**IP が「投資実務の深さ」で戦うなら正面衝突は避けられる**。
Sakana が実務ワークフロー（IC / PMI / モニタリング）に降りてくる兆候は、現時点で観測されていない `C`。

## 4. 出典

- `[S-007]` https://sakana.ai/rsi-lab/
- `[S-013]` Evolutionary Model Merge（Sakana 公式・各種解説）
- `[S-014]` https://pub.sakana.ai/
- `[S-015]` *Digital Red Queen* https://arxiv.org/html/2601.03335v1 / https://github.com/SakanaAI/drq
