---
doc_id: research-index
title: "Integral Prism リサーチ・インデックス"
version: 0.8.0
status: draft
created: 2026-08-22
updated: 2026-08-22
owner: artakartlight@gmail.com
project: integral-prism
doc_type: index
language: ja
tags: [index, survey, deep-research, agent, investment-research]
---

# Integral Prism / リサーチ・インデックス

仮称 **Integral Prism（インテグラル・プリズム）** — PE / ファンドの投資プロフェッショナル向け
「実益の大きいリサーチシステム」を設計するための、前段サーベイ一式。

> 本フォルダの目的は **アーキテクチャを決めることではない**。
> アーキテクチャ議論に入る前に、(a) 競合の実像、(b) 学術研究の到達点と未解決点、(c) 投資実務側の制約 を、
> 根拠つきで棚卸しすることにある。

**★1枚で把握する** → **[SUMMARY.md](SUMMARY.md)（全体サマリー）**
**最初に読む** → [method-and-scope.md](method-and-scope.md)（調査方法・確度スケール・限界）
**議論する** → [notes/discussion-agenda.md](notes/discussion-agenda.md)（未決の論点 D1–D10）
**何を作るか** → **[coding-strategy/](coding-strategy/README.md)（実装戦略）**
**どう設計すべきか** → **[discussion/](discussion/README.md)（設計ディスカッション・v0.7 追加）**

---

## 1. 競合 — `topics/01-competitors/`

| ファイル | 内容 |
|---|---|
| [sakana-marlin.md](topics/01-competitors/sakana-marlin.md) | **Sakana Marlin** の製品事実・推定アーキテクチャ・弱点仮説 W1–W5・戦略評価 |
| [sakana-ab-mcts-treequest.md](topics/01-competitors/sakana-ab-mcts-treequest.md) | **AB-MCTS / TreeQuest** — 適応分岐木探索とマルチモデル集合知 |
| [sakana-ai-scientist.md](topics/01-competitors/sakana-ai-scientist.md) | **The AI Scientist v1/v2** — 研究プロセス自動化の骨格 |
| [sakana-evolution-and-rsi.md](topics/01-competitors/sakana-evolution-and-rsi.md) | Model Merge / ShinkaEvolve / ALE-Agent / **Digital Red Queen** / RSI Lab |
| [sakana-edinet-bench.md](topics/01-competitors/sakana-edinet-bench.md) | **EDINET-Bench** — 日本語金融ベンチという伏兵 |
| [google-gemini-deep-research.md](topics/01-competitors/google-gemini-deep-research.md) | **Gemini Deep Research** — 単価・非同期基盤・計画承認 |
| [google-ai-coscientist.md](topics/01-competitors/google-ai-coscientist.md) | **AI co-scientist** — Elo トーナメントという報酬設計 |
| [openai-deep-research.md](topics/01-competitors/openai-deep-research.md) | **OpenAI DR** — end-to-end RL 路線と、IP が採らない理由 |
| [anthropic-research-system.md](topics/01-competitors/anthropic-research-system.md) | **Anthropic Research** — オーケストレータ/ワーカ型の実装知 |
| [tongyi-deepresearch.md](topics/01-competitors/tongyi-deepresearch.md) | **Tongyi DeepResearch** — オープンモデルの到達点と IterResearch |
| [storm-costorm.md](topics/01-competitors/storm-costorm.md) | **STORM / Co-STORM** — 多視点質問生成と談話プロトコル |
| [dr-agent-taxonomy.md](topics/01-competitors/dr-agent-taxonomy.md) | DR エージェントのタクソノミと **IP の自己位置** |
| [sakana-fugu-and-namazu.md](topics/01-competitors/sakana-fugu-and-namazu.md) | **Fugu / Namazu** — オーケストレーションのモデル化と主権AI戦略（**v0.3 追加**） |
| [finance-research-platforms.md](topics/01-competitors/finance-research-platforms.md) | AlphaSense / Hebbia / Rogo / BlueFlame |

## 2. 手法 — `topics/02-methods/`

| ファイル | 内容 |
|---|---|
| [test-time-scaling-and-tree-search.md](topics/02-methods/test-time-scaling-and-tree-search.md) | 探索の系譜、予算配分、停止条件 |
| [verifier-design.md](topics/02-methods/verifier-design.md) | **生成-検証の非対称性と、検証器の特権** |
| [information-value-eig.md](topics/02-methods/information-value-eig.md) | **期待情報利得（EIG）— IP の報酬設計の背骨** |
| [rl-search-agents.md](topics/02-methods/rl-search-agents.md) | RL 探索の報酬設計（学習せずに流用する） |
| [multi-agent-orchestration.md](topics/02-methods/multi-agent-orchestration.md) | 勝てる条件、並列性の切り分け、役割の異質性 |
| [multi-agent-debate-risks.md](topics/02-methods/multi-agent-debate-risks.md) | 討論の効果と**投資判断における危険** |
| [failure-modes-mast.md](topics/02-methods/failure-modes-mast.md) | **MAST** — 失敗の 41.8% は仕様と停止条件 |
| [context-engineering.md](topics/02-methods/context-engineering.md) | context rot、圧縮、出典 ID の分離 |
| [memory-and-continual-learning.md](topics/02-methods/memory-and-continual-learning.md) | **ファンドの記憶**と、その落とし穴 |
| [retrieval-and-graphrag.md](topics/02-methods/retrieval-and-graphrag.md) | 局所検索 / 大域センスメイキングの二層、時間つき KG |
| [long-form-report-generation.md](topics/02-methods/long-form-report-generation.md) | 長文・スライド生成（view 層） |
| [human-in-the-loop.md](topics/02-methods/human-in-the-loop.md) | 自律性-対話ジレンマと **4つの介入点** |
| [model-routing-and-cascades.md](topics/02-methods/model-routing-and-cascades.md) | 品質戦略かつ原価戦略、クロスベンダ独立性 |
| [structured-analytic-techniques.md](topics/02-methods/structured-analytic-techniques.md) | **ACH / SATs — 反証を一次データ構造にする** |
| [tree-search-algorithms-and-rewards.md](topics/02-methods/tree-search-algorithms-and-rewards.md) | **木探索の詳細地図**（統一タクソノミ / rStar / 検証粒度 / 計算最適配分 / FineVerify）（**v0.3 追加**） |
| [recursive-self-improvement.md](topics/02-methods/recursive-self-improvement.md) | **RSI** — DGM / SIFT / Red Queen / AlphaEvolve / ADAS / GEPA（**v0.3 追加**） |
| [persistent-limits-of-scaling.md](topics/02-methods/persistent-limits-of-scaling.md) | **モデルが賢くなっても消えない制約** — 幻覚の理論的下限 / アレアトリック / jagged frontier / ハーネスの目減り（**v0.4 追加**） |
| [decision-boundary-and-decision-analysis.md](topics/02-methods/decision-boundary-and-decision-analysis.md) | **決定境界の形式化** — インフルエンス図 / トルネード / EVPI（**論点 D3 への回答・v0.5**） |
| [evidence-aggregation-and-belief-update.md](topics/02-methods/evidence-aggregation-and-belief-update.md) | **証拠の集約と信念更新** — ACH 行列から確率へ / 矛盾証拠の扱い（**v0.5**） |
| [agent-security-and-prompt-injection.md](topics/02-methods/agent-security-and-prompt-injection.md) | **エージェントのセキュリティ** — 間接プロンプトインジェクションと CaMeL（**v0.5**） |
| [provenance-and-evidence-tracing.md](topics/02-methods/provenance-and-evidence-tracing.md) | **実行プロヴェナンスと証拠トレース** — 監査可能性の実装形（**v0.5**） |
| [serving-cost-and-caching.md](topics/02-methods/serving-cost-and-caching.md) | **長時間エージェントの原価構造** — KV キャッシュの経済学（**v0.5**） |

## 3. 評価 — `topics/03-evaluation/`

| ファイル | 内容 |
|---|---|
| [citation-attribution.md](topics/03-evaluation/citation-attribution.md) | **「引用されているが検証されていない」問題（最重要）** |
| [llm-judge-reliability.md](topics/03-evaluation/llm-judge-reliability.md) | judge バイアスと設計制約 |
| [calibration-and-forecasting.md](topics/03-evaluation/calibration-and-forecasting.md) | **較正 — 投資プロの母語で話す** |
| [general-dr-benchmarks.md](topics/03-evaluation/general-dr-benchmarks.md) | GAIA / BrowseComp / HLE / レポート級ベンチ |
| [finance-benchmarks.md](topics/03-evaluation/finance-benchmarks.md) | FinanceBench / FinTrace / FinVerBench / IPO Finance Agent |
| [reward-hacking-and-proxy-gaming.md](topics/03-evaluation/reward-hacking-and-proxy-gaming.md) | **報酬ハッキング** — 自己改善と探索の最大の落とし穴（**v0.3 追加**） |
| [benchmark-crisis-and-real-world-gap.md](topics/03-evaluation/benchmark-crisis-and-real-world-gap.md) | **ベンチマークの崩壊と実世界ギャップ** — METR 時間地平 / GDPval / 汚染（**v0.4 追加**） |
| [numeric-and-table-verification.md](topics/03-evaluation/numeric-and-table-verification.md) | **数値・表・財務データの検証** — 「再計算権」の実現可能性（**v0.5**） |
| [point-in-time-and-leakage.md](topics/03-evaluation/point-in-time-and-leakage.md) | **時点再現とリーク防止** — 反実仮想 DD を成立させる技術（**v0.5**） |
| [integral-prism-evaluation-design.md](topics/03-evaluation/integral-prism-evaluation-design.md) | **反実仮想 DD ほか、自製評価 A–E** |

## 4. ドメイン — `topics/04-domain/`

| ファイル | 内容 |
|---|---|
| [pe-dd-workflow.md](topics/04-domain/pe-dd-workflow.md) | PE/VC DD の工程と AI の効きどころ、採用実態 |
| [data-sources.md](topics/04-domain/data-sources.md) | 公開 / 準公開 / **プライベート**（堀） |
| [regulation-and-compliance.md](topics/04-domain/regulation-and-compliance.md) | EU AI Act、MNPI、監査証跡 |
| [vc-dd-multi-agent-research.md](topics/04-domain/vc-dd-multi-agent-research.md) | VC DD の学術先行事例（DIALECTIC ほか） |
| [alpha-decay-and-homogenization.md](topics/04-domain/alpha-decay-and-homogenization.md) | **AI によるアルファ減衰と同質化** — 投資領域固有の構造（**v0.4 追加**） |
| [data-vendor-landscape.md](topics/04-domain/data-vendor-landscape.md) | **データベンダーの垂直統合** — 構造的に最も危険な競合（**v0.5**） |
| [primary-research-and-expert-networks.md](topics/04-domain/primary-research-and-expert-networks.md) | **一次情報の取得** — エキスパートネットワークと質問設計（**v0.5**） |
| [document-understanding.md](topics/04-domain/document-understanding.md) | **文書理解** — 契約書・スキャン PDF・図表（**v0.5**） |

## 5. 戦略 — `topics/05-strategy/`

| ファイル | 内容 |
|---|---|
| [commoditization-and-moat.md](topics/05-strategy/commoditization-and-moat.md) | コモディティ化の証拠と、残る堀 |
| [pricing-and-unit-economics.md](topics/05-strategy/pricing-and-unit-economics.md) | 価格の空白帯域と原価構造 |
| [competitive-map.md](topics/05-strategy/competitive-map.md) | 競争地図とリスク |

## 6. 統合 — `topics/06-synthesis/`

| ファイル | 内容 |
|---|---|
| [contribution-map.md](topics/06-synthesis/contribution-map.md) | **R1–R34: どの研究がどこに効くか** |
| [model-proof-differentiation.md](topics/06-synthesis/model-proof-differentiation.md) | **★モデルが賢くなっても勝てる要素 — 4分類と賭けどころ**（**v0.4 追加**） |
| [differentiation-hypotheses.md](topics/06-synthesis/differentiation-hypotheses.md) | **差別化仮説 A/B/C** |
| [design-principles.md](topics/06-synthesis/design-principles.md) | **設計原則 P1–P20** |

## 7. 実装戦略 — `coding-strategy/`

サーベイから「**何を作るべきか**」を導いた文書群。🔒確定 / 🔧推奨 / ❓未決 を区別して記述している。

| ファイル | 内容 |
|---|---|
| [coding-strategy/README.md](coding-strategy/README.md) | 索引と一枚の結論 |
| [00-from-research-to-requirements.md](coding-strategy/00-from-research-to-requirements.md) | **設計原則 P1–P20 → 実装要件**の変換表 |
| [01-what-to-build-and-not.md](coding-strategy/01-what-to-build-and-not.md) | **作るもの / 作らないもの** |
| [02-evidence-graph.md](coding-strategy/02-evidence-graph.md) | **★中心データモデル（証拠グラフ）** |
| [03-components.md](coding-strategy/03-components.md) | コンポーネント C1–C15 と責務 |
| [04-build-buy-borrow.md](coding-strategy/04-build-buy-borrow.md) | 自作 / 購入 / OSS |
| [05-milestones.md](coding-strategy/05-milestones.md) | **M0（技術検証）〜 M4** と終了条件 |
| [06-tech-choices.md](coding-strategy/06-tech-choices.md) | 技術選択の指針 |
| [07-quality-gates.md](coding-strategy/07-quality-gates.md) | 出荷ゲート G1–G20 |
| [08-risks-and-kill-criteria.md](coding-strategy/08-risks-and-kill-criteria.md) | **撤退・転換基準** |
| [09-open-decisions.md](coding-strategy/09-open-decisions.md) | 実装に効く未決定事項 |

> **一行**: 作るのは「賢いリサーチエージェント」ではなく、
> **「投資判断の証拠グラフを構築・検証・較正し、追記専用で記録する機械」**である。
> 探索・生成・モデル・統率は全て調達可能な部品であり、モデルの進歩に食われる。

## 8. 設計ディスカッション — `discussion/`

**実益から逆算して「どんな設計にすべきか」を討論した記録。**
各論点で両論を強く書き、**【決着】と【反証条件】**を明記している。

| ファイル | 問い |
|---|---|
| [discussion/README.md](discussion/README.md) | 討論の作法（ストローマン禁止・数字で語る） |
| [00-what-is-practical-value.md](discussion/00-what-is-practical-value.md) | **実益とは何か**（V1時間/V2損失回避/V3機会/V4説明責任） |
| [01-a-week-in-the-deal.md](discussion/01-a-week-in-the-deal.md) | 投資プロは実際に何をしているか（時間が溶ける場所 P1–P8） |
| [02-devils-advocate.md](discussion/02-devils-advocate.md) | **★このプロジェクトが失敗する理由**（F1–F6、自社への ACH 適用） |
| [03-who-pays-and-why.md](discussion/03-who-pays-and-why.md) | 誰が何と比較していくら払うか（比較枠で3桁変わる） |
| [04-product-shape.md](discussion/04-product-shape.md) | 一次商品の形（案A/B/C/D の討論） |
| [05-first-wedge.md](discussion/05-first-wedge.md) | 最初の楔（W1–W5） |
| [06-architecture-debates.md](discussion/06-architecture-debates.md) | **設計上の6つの対立点** |
| [07-what-could-embarrass-us.md](discussion/07-what-could-embarrass-us.md) | 経営陣が呆れる11の瞬間と予防 |
| [08-minimum-lovable.md](discussion/08-minimum-lovable.md) | **実益を最短で出す最小形**（成果物と60秒デモ） |
| [09-decisions-and-next.md](discussion/09-decisions-and-next.md) | 決着A1–A12 / 未決U1–U8 / 次の一手 |
| [10-deep-dive-f2-calibration.md](discussion/10-deep-dive-f2-calibration.md) | **★F2 の徹底解剖**（拒否の5メカニズム、表示3案） |
| [11-unit-economics-model.md](discussion/11-unit-economics-model.md) | **単価と原価**（原価内訳・粗利・損益分岐・自社トルネード） |
| [12-competitive-wargame.md](discussion/12-competitive-wargame.md) | **競合ウォーゲーム**（相手の最善手・2年3シナリオ） |
| [13-evaluation-framework.md](discussion/13-evaluation-framework.md) | **★討論の評価**（DQ=4/10、決定の脆さ、期待値、討論の穴） |
| [14-how-we-know-it-works.md](discussion/14-how-we-know-it-works.md) | **検証の設計**（先行/遅行指標、反実仮想DDのプロトコル） |
| [15-open-problems.md](discussion/15-open-problems.md) | **未解決の難問 O1–O10** |

> **討論の結論**: **作るのは「調べる機械」ではなく「調べ終わったことを証明する機械」。**
> 投資プロの実益は「速く調べられた」ではなく
> 「**この仮説を殺しうる事実を、探したのに見つからなかった**」という確信にある。
>
> **討論の自己評価: DQ = 4/10**（論理は 8/10 だが、**顧客情報がゼロ 5/10**、**実行主体が未定 4/10**）。
> **これ以上考えても上がらない。顧客に会い、M0 を回す段階。**

## 9. ノートとメタデータ

| ファイル | 内容 |
|---|---|
| [notes/discussion-agenda.md](notes/discussion-agenda.md) | **未決の議論論点 D1–D10** |
| [notes/open-questions.md](notes/open-questions.md) | 一次確認の宿題 Q1–Q31 |
| [metadata/schema.md](metadata/schema.md) | フロントマター / 参考文献のスキーマ |
| [metadata/index.json](metadata/index.json) | **全ファイルの機械可読インデックス** |
| [metadata/sources.json](metadata/sources.json) | 出典レジストリ（**120件**、確度・使用箇所つき） |
| [metadata/claims.json](metadata/claims.json) | 主要な事実主張（**66件**、根拠・再検証手順つき） |
| [metadata/taxonomy.json](metadata/taxonomy.json) | 機能層 L0–L9 / 設計軸 / 設計原則 **P1–P20** |
| [metadata/glossary.md](metadata/glossary.md) | 用語集 |

---

## v0.3 での更新（木探索・RSI の深掘り）

一周目で薄かった2領域を掘った結果、**競合評価に修正が入った**。

1. **Sakana Fugu を見落としていた**（2026-06）。オーケストレーションは既に独立した商用モデルであり、
   「マルチモデルで束ねる」は IP の差別化にならない。Sakana は **アプリ / 統率 / モデル / 改善エンジン**の
   4層を垂直に固めつつある（Marlin / Fugu / Namazu / RSI Lab）。
2. **「長く走らせるほど良くなる」は、2つの独立研究が否定している**。
   引用の事実精度は探索量とともに **−42%** `[S-057]`、報酬ハッキングは 10→100 ステップで
   **26.4% → 57.8%** `[S-103]`。→ 設計原則 **P15（探索の上限と乖離監視）**を追加。
3. **評価器を共進化させると、品質とコストが同時に改善する**（RQGM: 探索トークン 1.35〜1.72倍削減）`[S-094]`。
   → IP の「反証役」設計の定量的裏付け。
4. **検証は「サブ質問への分解」で実装できる**（FineVerify: 4軌跡で +8.2pt）`[S-102]`。
   → L1 接地層の実装型が具体化した。
5. RSI は範囲を絞れば使える。**スキャフォールドの改善はモデルを跨いで転移する**（DGM）`[S-092]`。
   → 設計原則 **P13 / P14** を追加。

## v0.4 での更新（「モデルが賢くなっても勝てるか」）

**差別化要素を ∂V/∂M（モデル能力に対する価値の微分）で分類した。** → [model-proof-differentiation.md](topics/06-synthesis/model-proof-differentiation.md)

| クラス | 中身 | 判定 |
|---|---|---|
| **A 消える** | 巧妙なスキャフォールド / 統率 / 日本語品質 / 探索アルゴリズム / 生成速度 | 賭けない |
| **B 補完的（∂V/∂M>0）** | **較正と棄権 / 特権を持つ検証 / 問いの設計 / 選別と保証** | **本命** |
| **C 独立（構造的）** | 私有情報 / 責任と署名 / 監査証跡 / 顧客の記憶 / アルファ減衰への耐性 | 本命 |
| **D 減衰するが残存** | 状態管理・エラー回復・長文脈の扱い | 必要条件 |

決め手になった証拠:
- **較正されたモデルは理論的に必ず幻覚する** `[S-109]`。さらに**主要評価の10個中9個が棄権を罰する** `[S-108]`
  → **モデル層は構造的に較正を最適化しない**。較正はアプリ層の補完財である
- **アレアトリック不確実性は削減不能** `[S-115]` → 「当てる」ではなく「較正する」が正しい目標
- **METR の時間地平は成功率50%の定義** `[S-110]` → 業務要求（95%+）との溝が我々の領域
- **GDPval: 生成は専門家の約100倍安い** `[S-112]` → 生成では戦えない。**選別と保証**に価値が移る
- **AI 駆動のアルファ減衰: シグナル半減期 5-7年 → 18ヶ月** `[S-117]`
  → **投資領域では、モデルが賢くなるほどモデル由来の優位が速く消える**
- ⚠️ **人間+AI はしばしば AI 単独に劣る** `[S-114]` → 介入点設計を P17 に修正（承認型をやめる）

## v0.5 での更新（残りギャップの全掘り）

自覚していた9つのホールを全て掘り、10トピックを追加した。設計に直結した発見:

1. **決定境界は意思決定分析で解ける**（論点 D3）。トルネード図が「どの前提が判断を反転させるか」を、
   **EVPI が「この調査に払ってよい上限額」**を与える `[S-121][S-122]`
2. **確率は LLM に計算させない**。LLM は変数と依存関係の抽出に限定し、推論はアルゴリズムに任せる `[S-123][S-124]`
3. **矛盾する証拠を平均・抑制してはいけない** — LLM の既定の振る舞いは投資分析で有害 `[S-125]`（→ P20）
4. **プロンプトインジェクションは深刻**（ASB で最高攻撃成功率 **84.3%**）かつ**アーキテクチャ内では解けない**。
   CaMeL 型の二層 LLM ＋ capability 制御が必要 `[S-126][S-127]`（→ P18）
5. **数値検証は素の LLM では無理**（XBRL 整合性で **13.86%**、素の計算 **52%**、6モデル中4つが捏造）。
   **だからこそ工学的な堀になる** `[S-130][S-131]`（→ P19）
6. **「探索木＝監査証跡」には既に学名がある**（実行プロヴェナンス / 証拠トレース）。
   **1つのグラフで引用検証・規制監査・taint 追跡・デバッグの4要求を満たせる** `[S-128]`
7. **キャッシュヒット率＝粗利率**（0→90% で月額 $20,000→$2,000）`[S-129]`
8. **データベンダーはコネクタで全アプリに供給している** → データによる差別化はアプリ層では起きない。
   Class C の堀は「**ベンダーが持たない情報**」に限定して再定義 `[S-134]`
9. **エキスパートコールは「聞いた後」が埋まり「何を聞くか」が空白** `[S-135]`。EVPI が金額換算できる場所

## 現時点の一行結論

> Marlin は「**長時間 × 木探索 × マルチモデル**」で、Google DR は「**単一モデル×RL×低単価×分布**」で戦っている。
> どちらも **『出力＝レポート』を最終成果物とする設計**であり、
> 投資プロの実益（＝**意思決定の質と、後から検証できること**）に最適化されてはいない。
> Integral Prism の差別化仮説は「**レポート生成機ではなく、投資判断の反証可能な証拠構造を作る機械**」に置く。
> v0.3 の追加調査は、この仮説を**弱めるどころか補強した** — 競合は「どう答えるか」の層を垂直に固めており、
> 「**何を調べるべきか / その主張は本当か / どれくらい確からしいか**」の層は依然として空いている。
>
> v0.4 はさらに、この層が **モデルの進歩に食われないこと**を理論と実証の両面から確認した。
> **賢いモデルを上手に使うものを作ってはいけない。賢いモデルが構造的に提供できないものを作る。**
> それは **①較正された確度 ②特権を持つ検証 ③持たない情報 ④責任の記録** の4つであり、
> **いずれもモデルが賢くなるほど価値が上がる。**
> → [topics/06-synthesis/differentiation-hypotheses.md](topics/06-synthesis/differentiation-hypotheses.md)
