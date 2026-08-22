# ドラフト誘導・選択的分岐系 研究ライン 裏取りレポート

調査日: 2026-08-22 / 調査者: PEファンド内製リサーチシステム調査員
確度基準: **A** = 一次資料(公式リポジトリraw README / 論文本文スニペット)で直接確認、**B** = 複数の独立スニペット・二次資料で一致確認(原文表は未読)、**C** = 単一ソースまたは推測を含む

環境注記: arxiv.org / huggingface.co / research.google は egress proxy で遮断。一次確認は raw.githubusercontent.com のREADME、補完は WebSearch スニペット(arXiv本文断片を含む)による多方向照合で実施。

---

## 1. TTD-DR (Google, arXiv:2507.16075) — 確認: ほぼ主張どおり。ただし勝率は完全にLLM judge依存

### 確認結果
- **主張「ドラフトを拡散的に反復改訂」: 確認(A相当)**。手法は2本柱:
  1. **Report-Level Denoising with Retrieval**: 予備ドラフト(updatable skeleton)を生成し、各denoisingステップでドラフトのギャップに基づく検索(draft-guided search)→取得情報でドラフト改訂、を反復。
  2. **Component-wise Self-Evolution**: research plan・検索クエリ・合成回答など各コンポーネントを自己進化アルゴリズム(変種生成+評価+改訂)で個別に品質向上。
- **勝率69.1% / 74.5%: 確認(B)**。ベンチは **LongForm Research(69.1%)と DeepConsult(74.5%)**(注意: 一部スニペットで「DeepConsist」と誤記されるが正しくは DeepConsult)。**比較相手は OpenAI Deep Research** とのside-by-side(pairwise)比較。
- **評価者: LLM auto-rater(= LLM judge)で確認(B)**。win rateはauto-raterによるside-by-side判定。加えてHelpfulness/Comprehensivenessのauto-raterスコアも報告。ベースモデル・エージェント基盤はGemini-2.5-pro。短答型(HLE, GAIA等)では正解ベース評価で+4.8/+7.7/+1.7%と別報告あり(こちらはjudge依存度低)。
- **コード: 公式リポジトリは存在しない(B)**。Googleはブログ+論文のみ公開。再現実装は非公式:
  - OptiLLM `deep_research` プラグイン(README明記: 「simplified implementation。self-evolutionとmemory-based synthesisは未実装」)— 再現は**部分的**である点に注意。
  - その他 TTD-DR-Dify (fdb02983rhy)、jh941213/TTD-DR 等いずれも非公式。

### 設計適用上の注意
- **69.1%/74.5%はLLM judge(auto-rater)によるpairwise勝率であり、position bias・judge固有の選好(冗長・網羅的な文章を好む傾向)の影響を受ける**。「OpenAI DRの約7割に勝つ」を品質の絶対保証として扱わないこと。短答ベンチでの正解率向上(+1.7〜7.7%)の方が客観的だが差は小さい。
- 公式コードがないため、「self-evolution」の具体(変種数・評価プロンプト・マージ方法)は論文記述依存。アーキテクチャ根拠にするなら「draft-guided retrieval + 反復改訂」というコア機構までに留め、self-evolutionの効果量は独自検証が必要。

### 出典
- https://arxiv.org/abs/2507.16075 (abs/htmlスニペット経由)
- https://research.google/blog/deep-researcher-with-test-time-diffusion/ (検索スニペット経由、直接fetch不可)
- https://raw.githubusercontent.com/algorithmicsuperintelligence/optillm/main/optillm/plugins/deep_research/README.md (一次・非公式実装)
- https://www.marktechpost.com/2025/07/31/google-ai-introduces-the-test-time-diffusion-deep-researcher-ttd-dr-a-human-inspired-diffusion-framework-for-advanced-deep-research-agents/

---

## 2. WebWeaver (Alibaba Tongyi Lab, arXiv:2509.13312) — 確認: 主張どおり。公式README一次確認済み

### 確認結果
- **公式リポジトリ一次確認(A)**: `Alibaba-NLP/DeepResearch` リポジトリ内 `WebAgent/WebWeaver/` フォルダのREADMEをrawで取得・確認。
- **手法(A)**: dual-agent構成。
  - **Planner**: 検索とアウトライン改訂を動的に交互実行(アウトライン=living document)。証拠は**memory bank**に格納され、アウトラインの各節に**citation IDが埋め込まれる**(citation-grounded outline)。
  - **Writer**: 節ごとにmemory bankから該当citationの証拠のみを**targeted retrieval**して階層的に執筆(long-context問題と引用ハルシネーションの緩和)。
  - 付随: WebWeaver-3k SFTデータセットで小型モデル(Qwen3-30B-A3B-Instruct)に蒸留。
- **引用精度93.37%: 確認(B)**。DeepResearch Benchのcitation accuracy(C.acc)で93.37%、対Gemini-2.5-pro-DR 78.3%、OpenAI DR 75.01%。総合スコアはDeepResearch Bench 50.58(Gemini 49.71、OpenAI 46.45)。READMEでは表が画像(table1.png)のため数値そのものはREADMEテキストからは未確認、二次資料+論文スニペットで一致。
- **実装の実際(A)**: 公式実装はplanner/writerにqwen3系(README表記 `qwen3-256b-a30b-Instruct`)+要約モデル(4×80G GPU要求)+Serper/ScraperAPI。memory bankの実体はページ要約(url2summary)と証拠(url2page)のマッピング。

### 設計適用上の注意
- **DeepResearch Benchの総合スコア(Comp./Insight等)はRACE方式のLLM judge評価**。一方**citation accuracyは「引用が主張を支持するか」の検証(FACT系)で、これもLLMによる判定だが、判定タスクが二値検証に近く相対的に信頼性が高い**。93.37%は「引用の張り方のアーキテクチャ(節ごとのtargeted retrieval)が効く」という主張の裏付けとしては強い。ただし総合スコア差(50.58 vs 49.71)は僅差でありjudgeノイズ範囲内の可能性がある。
- 「証拠メモリバンク+参照付きアウトライン」という我々の要約は正確。追加で「アウトラインは静的でなく検索と交互に最適化される」点が本質(静的アウトラインは論文が明示的に批判する対象)。

### 出典
- https://raw.githubusercontent.com/Alibaba-NLP/DeepResearch/main/WebAgent/WebWeaver/README.md (一次)
- https://arxiv.org/abs/2509.13312
- https://neurohive.io/en/frameworks/webweaver-open-source-framework-for-deep-research-outperforms-openai-deepresearch-and-gemini-deep-research-on-benchmarks/ (93.37%数値の照合)

---

## 3. Chain-in-Tree (Xinzhe Li, arXiv:2509.25835) — 確認: 主張どおり。ただし実証は数学推論のみ

### 確認結果
- **公式リポジトリ一次確認(A)**: `xinzhel/chain_in_tree`(現在deprecated、後継は汎用木探索フレームワーク `xinzhel/lits-llm`)。READMEでデータセットが **"math500", "gsm8k" のみ**であることを直接確認。ACL 2026 Findings採録(bibtex記載)。
- **手法(A)**: 木探索の全ステップで分岐する代わりに、**Branching Necessity (BN) 評価**で分岐要否を判定。自信のある/routineなステップは連鎖(chain)し、不確実な地点のみ分岐。2変種:
  - **BN-DP** (direct prompting): 補助LLMが直接判定
  - **BN-SC** (self-consistency): 複数サンプルの一致度で判定(リポジトリでは "entropy"=sc1, "sc"=sc2 の2実装)
- **75-85%削減: 確認(B)**。BN-DPをToT-BFS、ReST-MCTS、RAPに組み込んだ場合、**GSM8KとMath500において**トークン生成・モデル呼び出し・実行時間を75-85%削減、精度低下はほぼなし。BN-SCは最大80%削減だが**14設定中1-4設定で不安定**(極端に長い推論ステップを生む例が原因)。

### 設計適用上の注意
- **【重要】実証は数学推論(GSM8K/Math500、正解が客観検証可能)のみ。Webリサーチ/深掘り調査への適用は完全に外挿・仮定である**。数学ではステップの「自信」がLLMの内部知識で判定しやすいが、Webリサーチでは分岐要否が外部証拠の未知性に依存するため、BN判定の信頼性は未検証。
- 削減率はjudge非依存(トークン数・呼び出し回数の実測)なので数値自体の信頼性は高い。「精度低下なし」の精度も正解ベース評価で客観的。
- 採用するならBN-DP系(安定)を推奨。BN-SCの不安定性(ロングテール例で暴走)はコスト上限ガードが必須。

### 出典
- https://raw.githubusercontent.com/xinzhel/chain_in_tree/main/README.md (一次)
- https://github.com/xinzhel/lits-llm (後継フレームワーク)
- https://arxiv.org/abs/2509.25835 / https://openreview.net/forum?id=A1qL5AFV8H

---

## 4. TreeSeeker (arXiv:2606.11662, 2026年6月) — 確認: 主張どおり(手法名・構成一致)。数値はスニペット確認のみ

### 確認結果
- **手法(B)**: 「TreeSeeker: Tree-Structured Trial, Error, and Return in Deep Search」。推論時フレームワーク、2コンポーネント:
  - **TreeSearch**(コントローラ): 全サブゴール木を読み、**テキストUCB的シグナル(value / uncertainty / risk)**で「有望枝のexploit / 不確実な代替のexplore / 非生産的継続のprune + 以前の分岐点へのreturn(branch-and-return)」を選択。
  - **TreeMem**: 枝ごとに証拠・不確実性・矛盾・進捗・**失敗の手がかり(failure cues)**をコンパクトに記録し、後の判断に反映。
  - ルート質問をサブゴール分解してから探索。
- **ベンチ結果(B)**: XBench-DeepSearch **56.3**(GPT-5.2バックエンド。Flash-Searcher比+5.6、IterResearch比+12.3、Tongyi-DeepSearch比+11.3)、BrowseComp **47.0**、BrowseComp-ZH **43.0** でオープンソース系ベースライン中首位。gpt-4.1共通バックエンドのablationでも+1.7/+2.0/+2.6でバックエンド非依存の優位を主張。
- **コード: 公開リポジトリ未発見(C)**。GitHub検索・WebSearchともに公式repoを特定できず。数値・詳細はarXiv本文スニペット依存(原文表は未読)。

### 設計適用上の注意
- XBench-DeepSearch / BrowseComp系は**正解のある短答ベンチであり、LLM judge依存度は低い**(回答一致判定にLLMを使うが二値照合)。TTD-DR/WebWeaverの勝率系より客観性は高い。
- ただし**長文レポート生成での有効性は未実証**(BrowseComp系は「深い検索で1つの答えを当てる」タスク)。我々のPEリサーチ(レポート生成)への転用は、branch-and-return機構の移植仮説として扱うこと。
- 一次資料(コード)がないため「テキストUCB」の実装詳細(スコアの数値化方法、プロンプト)は再現不能。確度Bに留まる。

### 出典
- https://arxiv.org/abs/2606.11662 / https://arxiv.org/pdf/2606.11662 (スニペット経由)
- https://huggingface.co/papers/2606.11662 (fetch不可、検索スニペットのみ)

---

## 5. ParallelResearch (arXiv:2510.05145) + 2026年新手法スイープ

### ParallelResearch — 確認(B)、ただし焦点は品質でなく効率
- 論文タイトルは **「Efficient Tree-Structured Deep Research with Adaptive Resource Allocation」**(v2以降「Real-time Agent Orchestration for Efficient Deep Research」表記もあり)。フレームワーク名がParallelResearch。著者: Lunyiu Nie, Nedim Lipka, Ryan A. Rossi, Swarat Chaudhuri(UT Austin + Adobe系)。最新版2026-03-29。
- 構成: (1) クエリ複雑度に応じ計算資源を配分する**adaptive planner**、(2) 冗長パスをpruneし**speculative execution**を行うランタイムオーケストレーション層、(3) 幅・深さ両方向の完全非同期並列実行基盤。
- 注意: 主眼は**レイテンシ/資源効率**(対話的アプリ向け)であり、レポート品質向上の主張ではない。我々の「選択的分岐」根拠としては補助的。

### 見落としスイープで発見した関連手法(要検討)
| 手法 | arXiv | 関連性 |
|---|---|---|
| **AgentCPM-Report** (OpenBMB, 2026/02) | 2602.06540 | **「Interleaving Drafting and Deepening」— まさにドラフト誘導系の直系後続**。MiniCPM4.1-8BのSFT+RLで DeepResearch Bench / DeepConsult / DeepResearchGym 評価。要精査 |
| **ScaffoldAgent** (2026/06) | 2606.20122 | Utility-guided **dynamic outline optimization** — WebWeaver路線の発展(アウトラインを能動的足場として利用)。プロンプトのみ、Qwen3-32B/DeepSeek-V3.2 |
| **DeepPlanner** (ACL 2026 Findings) | 2510.12979 | Advantage shapingでplanning段階をRL最適化 — 計画品質の学習的改善 |
| **ParallelMuse** (Tongyi, 2025/10) | 2510.24698 | Agentic parallel thinking(並列部分ロールアウト+圧縮推論統合)— 分岐系の別解 |
| **Mind2Report** (2026/01) | 2601.04879 | **商用レポート合成特化**の認知型deep researchエージェント — PEユースケースに近い、要精査 |
| **DEEPRUBRIC** (2026/06) | 2606.17029 | Evidence-tree rubric supervisionによるRL — 証拠木という点でTreeSeeker/TreeMemと交差 |
| **FineVerify** (2026/06) | 2606.00660 | 細粒度自己検証でtest-time scaling — 検証側の強化(asymmetric verification系、ICLR 2026にも同系統) |
| **WebAnchor** (2026/01) | 2601.03164 | 長期Web推論の計画アンカリング — 計画の脱線防止 |

**結論(スイープ)**: 我々の4本柱(TTD-DR / WebWeaver / CiT / TreeSeeker)に大きな見落としはないが、**AgentCPM-Report(drafting×deepening交互)とScaffoldAgent(アウトライン最適化のutility誘導)は同一系統の2026年後続であり、次回深掘り対象に追加すべき**。また評価面ではrubric/verification系(DEEPRUBRIC, FineVerify)の台頭が顕著で、LLM judge勝率への依存を下げる潮流と整合する。

### 出典
- https://arxiv.org/abs/2510.05145
- https://raw.githubusercontent.com/DavidZWZ/Awesome-Deep-Research/main/README.md (一次・網羅リスト、ACL 2026 KnowFM)
- https://arxiv.org/abs/2602.06540 / https://arxiv.org/abs/2606.20122 / https://arxiv.org/pdf/2510.12979 / https://arxiv.org/pdf/2601.04879

---

## 総括: LLM judge依存マップ

| 主張 | judge依存度 | 扱い |
|---|---|---|
| TTD-DR勝率69.1%/74.5% | **高**(pairwise auto-rater) | 相対優位の示唆に留める。絶対品質の根拠にしない |
| TTD-DR短答ベンチ+1.7〜7.7% | 低(正解ベース) | 客観的だが効果量小 |
| WebWeaver総合50.58 | **高**(RACE系LLM judge、僅差) | 参考値 |
| WebWeaver引用精度93.37% | 中(引用支持の二値検証) | アーキテクチャ設計の根拠として採用可 |
| CiT 75-85%削減 | **なし**(トークン実測)| 信頼できる。ただし数学のみ→Web適用は仮定 |
| TreeSeekerベンチ首位 | 低(短答正解ベース) | 信頼できるがレポート生成タスクでは未実証 |
