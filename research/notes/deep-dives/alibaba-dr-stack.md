# Alibaba (Tongyi) ディープリサーチ・スタック 一次資料調査

調査日: 2026-08-22 / 調査者: powerScience アーキテクチャ調査
一次資料: `Alibaba-NLP/DeepResearch` リポジトリ全体をローカルにclone(`/home/user/alibaba-nlp/deepresearch`、shallow clone, main HEAD)し、コード・プロンプト・同梱の技術報告PDF(`Tech_Report.pdf`, 23頁, arXiv:2510.24701 と同一)をテキスト抽出して読了。
確度表記: **[A]** = repo内コード/プロンプト/同梱Tech Report(一次)、**[B]** = WebSearchスニペット(二次)。

---

## 1. Tongyi DeepResearch 30B-A3B 全体像

### 1.1 モデルと成績 [A: Tech_Report.pdf / README.md]
- ベース: Qwen3-30B-A3B-Base。総パラメータ30.5B、トークンあたり活性3.3B(MoE)。コンテキスト128K。
- 評価条件: temperature=0.85, repetition_penalty=1.1, top_p=0.95、**ツール呼び出し最大128回/タスク**、Avg@3で報告。
- Table 1(Tech Report p.12)[A]:

| ベンチ | Tongyi DR (ReAct) | 参考 |
|---|---|---|
| Humanity's Last Exam | **32.9** | DeepSeek-V3.1 29.8 / OpenAI DR 26.6 |
| BrowseComp | 43.4 | OpenAI o3 49.7, OpenAI DR 51.5 |
| BrowseComp-ZH | 46.7 | o3 58.1 |
| GAIA | 70.9 | Claude-4-Sonnet 68.3 |
| xbench-DeepSearch | **75.0** | DeepSeek-V3.1 71.0 |
| WebWalkerQA | **72.2** | o3 71.7 |
| FRAMES | **90.6** | o3 84.0 |

- Heavy Mode時 [A]: HLE **38.3**、BrowseComp-ZH **58.1**、BrowseComp 58.3(Pass@1)。
- Pass@3 [A]: BrowseComp 59.64、BrowseComp-ZH 63.67、HLE 45.9。

出典: https://raw.githubusercontent.com/Alibaba-NLP/DeepResearch/main/README.md / repo同梱 Tech_Report.pdf

### 1.2 推論モード [A]
**(a) ReAct モード**(コア能力の評価用): vanilla ReAct。thought–action–observation の線形履歴 H_T をそのまま伸ばす。採用理由は明示的に「The Bitter Lesson」— 複雑なワークフロー工学はモデル能力のスケールで陳腐化する、という設計哲学(Tech Report §3.1)。
- 実装 `inference/react_agent.py` [A]: 単一 while ループ。`<think>`,`<tool_call>`,`<tool_response>`,`<answer>` のタグプロトコル。最大 `MAX_LLM_CALL_PER_RUN=100` 回、実行150分でタイムアウト。**トークン数が 110K(110*1024)を超えたら「これ以上ツールを呼ばず今の情報で最終回答せよ」という強制打ち切りメッセージを注入**して回答させる — 極めて単純なコンテキスト超過フォールバック。
- stop シーケンスに `<tool_response>` を指定してモデルの観測捏造(hallucinated tool response)を切断する実装 [A]。

**(b) Context Management パラダイム(IterResearch, 論文名 WebResearcher)**:
- 各ステップで完全履歴を捨て、**「質問 q + 進化するレポート S_t(圧縮メモリ)+ 直前のアクション a_t と観測 o_t」だけからなる再構成ワークスペース**で条件付ける Markov 的状態再構成。式: `S_t, τ_{t+1}, a_{t+1} ~ π(·|S_{t-1}, a_t, o_t)`(Tech Report §3.1)[A]。
- WebResearcher README [A] の用語: 各ラウンドの出力は `Think`(次ラウンドへ持ち越さない)/ `Report`(中央メモリ、持ち越す)/ `Action`(ツール呼び出し or 最終回答)。狙いは (1) Cognitive Workspace Suffocation、(2) Irreversible Noise Contamination、(3) 周期的統合の欠如、の3病理の回避。

**(c) Heavy モード(test-time scaling)** [A: Tech Report §4.3]:
- Research-Synthesis 構成。**n 個の並列エージェント**が各々 IterResearch 方式で走り、各自の最終圧縮レポート S^u_T と答えを出す。**統合モデルが {(S^u_T, answer^u)} だけを見て最終回答を合成**。フル軌跡の結合は2〜3エージェントでコンテキスト超過するが、圧縮レポートなら n 本を1コンテキストに収められる、というのが成立条件。
- 注意: repo 内に Heavy モードの公式実装は無い(`inference/` は ReAct のみ)。姉妹実装 `WebAgent/ParallelMuse/`(compressed_reasoning_aggregation: REPORT_PROMPT で各軌跡を圧縮→INTEGRATE_PROMPT で統合)が同型 [A]。

### 1.3 ツール構成 [A: inference/]
5ツール: `search`(Serper、**クエリ配列を1回で受けるバッチ検索**・各top10)/ `visit`(Jina Readerで取得→**別の要約LLMが goal 条件付きで {rational, evidence, summary} JSON に蒸留**、ページ生テキストは95Kトークンで切詰)/ `PythonInterpreter`(SandboxFusion)/ `google_scholar` / `parse_file`(Dashscope IDP; PDF/DOCX/XLSX/ZIP/MP4等)。
- システムプロンプトは `inference/prompt.py` [A]。ツール定義をXMLの`<tools>`にJSONで列挙し、`<tool_call>` タグで呼ばせる自前プロトコル(OpenAI function calling 非依存)。
- **visit の EXTRACTOR_PROMPT** [A] は「rational / evidence(原文をできるだけ長く保持)/ summary」の3フィールド構造 — これが後述 WebWeaver のメモリバンクのレコード形式の原型。
- RL学習時はツール層を統一サンドボックス化: QPSレート制御、結果キャッシュ、タイムアウト&リトライ、非致命的失敗の graceful degradation、バックアップ検索APIへのフェイルオーバー(Tech Report §3.4.3)[A]。

### 1.4 学習パイプライン [A: Tech_Report.pdf §3.2–3.4]
```
Qwen3-30B-A3B-Base
  → Agentic CPT Stage1 (32K) → Agentic CPT Stage2 (128K)   … mid-training (AgentFounder)
  → Agentic SFT (cold start; 40K→128K の2段階)
  → Agentic RL (厳密 on-policy のGRPO改)
  → Model Merging(同一ベース由来の複数変種の重み加重平均)
```
- **Agentic CPT**(= AgentFounder, arXiv:2509.13310): 次トークン予測のまま、agentic行動データを大量合成して継続事前学習。データは「entity-anchored open-world memory」(webクロール+軌跡を実体単位に構造化)から、Planning行動 / Reasoning行動 / Decision-Making行動(各ステップの潜在行動空間を展開し多段意思決定列に再構成)を合成 [A]。第2段で64K–128Kの長系列行動データを注入。AgentFounder-30B 単体成績: BrowseComp-en 40.0, GAIA 72.8, HLE 31.5, DeepResearch Bench RACE 48.9 [A: Agent/AgentFounder/README.md]。
- **合成QAデータ**(post-training用): (1) ランダムウォークで密結合知識グラフ+実サイト由来の同型テーブルを構築→部分グラフをサンプル→**不確実性注入**で難化(WebSailor系)。(2) 集合論ベースの情報探索の形式化(WebShaper)で、推論ショートカットと構造冗長を抑えつつ制御可能に拡張、**正解の形式検証**も可能に。(3) PhD級問題の反復複雑化エンジン(WebResearcher系)[A]。
- **SFT(cold start)**: ReAct形式と Context Management形式の**混合学習**。後者は (S_{t-1}, a_{t-1}, o_{t-1}) → (S_t, τ_t, a_t) を教師あり学習 — つまり**「ラウンドごとの統合レポート生成」自体が学習された能力** [A]。
- **Agentic RL**: GRPO改。厳密 on-policy(重要度比 1.0)、**報酬は正解一致の0/1のみ(フォーマット報酬なし)**、DAPO流のトークンレベル policy gradient + clip-higher、leave-one-out アドバンテージ、**長さ超過で答えに達しない等の負例をロスから選択除外**(policy collapse対策)。rLLMベースの step-level 非同期 rollout(推論サーバとツールサーバを分離)[A]。
- **自動データカリキュラム**: SFTモデルで全問rollout→全勝/全敗問題を除外して「中難度」だけでRL開始。学習中も裏プロセスが中間checkpointで全データを再サンプルし、習得済み問題を除去し新たな中難度問題を補充。**「agentic RLの成否はアルゴリズムよりデータ品質と環境安定性」**という結論を明記 [A]。
- **シミュレーション環境**: 2024年版WikipediaのローカルDB+RAGツールでWeb環境を模擬し、高速・低コスト・決定的な実験環境として活用(WebSailor-V2の dual-environment と同思想)[A]。

---

## 2. ファミリーリポの中核機構(1段深掘り)

### 2.1 WebWeaver(open-endedレポート生成; arXiv:2509.13312)★最重要
**二重エージェント: Planner(探索+アウトライン)と Writer(節単位執筆)の分離。** 実装は `WebAgent/WebWeaver/` に完全公開 [A]。

**(a) Planner ループ** [A: react_agent_search_id.py + prompt/search_user_prompt_id_3.py]
- 単一ツール `search_and_visit`(クエリ配列+goal)。内部パイプライン: Serper検索 → **SelectURL**(要約LLMがスニペットから関連URL群をJSON抽出)→ 未訪問URLのみ Visit(scraperapi→要約LLMで {rational, evidence, summary})[A: tool/tool_search_and_visit.py, tool_select_url.py]。
- サイクル: `<think>` → `<tool_call>` → `<tool_response>`(**要約のみ**が `<material><id_N>Summary…</id_N></material>` 形式で返る)→ `<write_outline>` でアウトライン更新、を繰り返し `<terminate>` で終了。
- プロンプト規律 [A]: アウトラインは階層4レベルまで、**各サブセクション末尾に `<citation><id_1>,<id_2>…</citation>` を必須**、引用がない節はさらに検索して次サイクルで更新、**最低3回はアウトラインを再構成**、類似節は引用をマージして統合。
- アウトライン更新のたびに「Try to make the outline more comprehensive and ensure the citation for each subsection.」を自動追記して改善圧をかける [A]。

**(b) 証拠メモリバンクの実装構造** [A: react_agent_search_id.py save_page_info/save_url2id]
- 実体は**単なる Python リスト+辞書**(外部DB・ベクトル索引なし):
  - `page_info`: `[{url, goal, summary, evidence}, …]` — visit時に要約LLMが出した **summary(短い要約)と evidence(原文をできるだけ長く保持した抜粋)のペア**をURL単位で保存。同一URLは重複保存しない。
  - `url2id`: `{url: 連番}` — 到着順の整数ID。**プランナーのコンテキストに入るのは `<id_N>` とsummaryだけで、evidence(長文)はコンテキスト外のメモリバンクに待避**。これがコンテキスト膨張の抑止機構の本体。
- Planner 出力 = アウトライン(引用ID付き)+ page_info + url2id を JSONL で次段へ受け渡し。

**(c) Writer の階層的検索・執筆ループ** [A: react_agent_outline_write.py + tool/tool_retrieve.py + prompt/user_prompt.py]
- 入力プロンプト: `<material>` に**全ソースの summary のみ**(`<id_N>Goal+Summary</id_N>`)+ `<outline>`(URLはID表記に置換済み)+ 質問。
- ループ: `<think>` → `<tool_call>{retrieve, url_id:[…], goal}` → **retrieve がメモリバンク(url2page=evidence)から該当IDの全文証拠を返す(20Kトークン上限)** → `<think>` → `<write>` で当該節を執筆 → 次節へ。
- **鍵となるコンテキスト管理**: `<write>` 完了を検知すると、**直前の tool_response 内の証拠本文を「The page content for the previous section has been masked for saving the space.」に置換して履歴から消す** [A: 233–239行]。つまり「今書いている節に必要な証拠だけが常にコンテキストにあり、書き終えた節の証拠は即座に破棄」— これが "loss in the middle" 対策の実装実体。
- 最後に `url2id` から References リスト(`[N]. url`)を機械的に生成して付加 [A] — 引用IDが最初からメモリバンクのキーなので、**引用精度がアーキテクチャ的に担保**される。
- 全部で最大40 LLMコール、コンテキスト上限100K、レポート出力30K。

**(d) 成績** [B: WebSearchスニペット(neurohive / emergentmind / alphaxiv 経由、原典 arXiv:2509.13312)]
- DeepResearch Bench 総合 **50.58**(Gemini-2.5-pro DR 49.71、OpenAI DR 46.45 を上回る)。
- **引用精度 93.37%**(Gemini 78.3% / OpenAI DR 75.01%)— 上記 (b)(c) の機構による。※一次PDFは遮断のため数値はB確度。README [A] も「最良の citation accuracy / effective citations」を主張、数表は画像のため数値未確認。
- アブレーション [B]: アウトライン反復改善の回数が多いほど品質向上; 節単位の階層執筆が「全部入れて一括生成」を明確に上回る。
- WebWeaver-3k: この二重エージェントの軌跡を蒸留したSFTデータで小型モデルに同能力を移植 [A: README]。

### 2.2 WebResearcher / IterResearch(arXiv:2509.13309)
- §1.2(b) 参照。ラウンドごとにワークスペースを (q, 進化レポート, 直前観測) に再構成。TTSは last-k-fusion: 並列rolloutの最終kステップのみをFusion Agentが統合 [A: README]。

### 2.3 ReSum / WebResummer(arXiv:2509.13313)
- ReActへの**プラグイン型**コンテキスト圧縮: 会話が閾値に達したら専用要約モデル(ReSumTool-30B)が「収集済み証拠・情報ギャップ・次の探索方向」を `<summary>` に圧縮し、そこから会話を再開(restartable state)[A: WebResummer/README + src/summary_utils.py]。
- 素の適用で Pass@1 平均 +4.5%; ReSum-GRPO(セグメント分割した長軌跡に軌跡レベルadvantageをブロードキャスト)で+8.2%、1Kサンプルで BrowseComp-zh 33.3% [A: README数値]。
- **学習なしでも機能する(universal compatibility)ことを明示**している点が重要 [A]。

### 2.4 AgentFold(arXiv:2510.24699)
- 「先回りコンテキスト折り畳み」: 各ターン、モデル自身が think / **compress**(過去ステップ範囲を1ブロックに folding)/ motivation / action の4ブロックを出力 [A: WebAgent/AgentFold/infer.py]。
- 実装 [A]: 履歴は `[{start, end, content}]` のステップリスト。モデルの compress 指示(`compress_range`, `compress_text`)で区間を `[Compressed Step i to j]` に置換。**各ターンのプロンプトは毎回「Question + Previous Steps(折り畳み済み)」だけからステートレスに再構成** — IterResearch(全再構成)と ReAct(無圧縮)の中間で、粒度をモデルが自己決定する。

### 2.5 WebSailor / WebSailor-V2(arXiv:2507.02592, 2509.13305)
- 中核は**学習データ側**: SailorFog-QA — 密結合知識グラフ構築→部分グラフ→**情報難読化(obfuscation)による高不確実性Level-3タスク**合成。教師軌跡の思考を簡潔に再構成してスタイル汚染を回避、RFTコールドスタート→**DUPO**(Duplicating Sampling Policy Optimization)でRL [A: WebSailor/README.md]。
- V2: SailorFog-QA-2 + **二重環境RL**(シミュレータで高速反復、実環境で最終学習)。Qwen3-30B-A3Bで BrowseComp-EN 35.3 / ZH 44.1 / HLE 30.6、671BのDeepSeek-V3.1超え [A: WebSailor-V2/README.md]。

### 2.6 WebShaper(arXiv:2507.15061)
- 情報探索タスクの**集合論的形式化**(Knowledge Projection; R-Union / Intersection 演算)を先に定め、それに沿って Expander エージェントが**層状(layer-wise)拡張**で質問を生成・検証するデータ合成。GAIA 60.19(72B)。データ500問を公開(`WebShaper/data/webshaper.500.jsonl`)[A: readme + data]。

### 2.7 その他 [A: 各README]
- **WebWalker**: Webトラバーサルのベンチマーク(WebWalkerQA)+探索/記憶を分離したマルチエージェント枠組み(ACL 2025)。
- **WebDancer**: 4段パイプライン(ブラウジングデータ構築→軌跡サンプリング→SFT→RL)の原型(NeurIPS 2025)。
- **WebLeaper**: entity-intensive タスク + ISR/ISE(情報探索率/効率)で軌跡をフィルタし「効率の良い探索」を学習させる。
- **ParallelMuse**: 並列思考のTTS — 機能特化 partial rollout + 圧縮推論統合。
- **NestBrowse**: ブラウザ操作(MCP)をネストした情報探索。visit要約プロンプトは本体と同一の rational/evidence/summary 形式。
- **AgentScaler**(Agent/): 関数呼び出し環境を read–write DB として自動大量構築し汎用エージェント能力を学習(arXiv:2509.13311)。

---

## 3. 抽出される設計知見

**(a) 長時間タスクのコンテキスト管理 — 3つの流派が同一組織内で共存**
1. **周期的全再構成(IterResearch)**: 毎ラウンド (質問+進化レポート+直前観測) に作り直す。最も急進的。Heavy モードの並列統合の前提でもある(圧縮レポートだから n 本並べられる)。
2. **閾値到達時の要約再開(ReSum)**: 普段はReAct、溢れたら要約して再スタート。既存エージェントに後付け可能。
3. **モデル主導の選択的折り畳み(AgentFold)**: 圧縮の粒度・範囲をモデルが毎ターン宣言。
- 共通する下部構造: **visit ツールの時点で「goal条件付き要約」に落とす**(生ページをコンテキストに入れない)二段LLM構成。ReActですら実際は要約器で守られている。

**(b) 証拠メモリの構造(WebWeaver)**
- レコード = `{url, goal, summary, evidence}`。**summary はコンテキスト内(ID付き)、evidence はコンテキスト外**という二層。ID は到着順整数で、アウトラインの引用・本文の引用・最終Referencesまで一気通貫のキー。ベクトルDB不要 — 「検索」は LLM がアウトライン中の引用IDを見て retrieve を呼ぶだけ。

**(c) 計画と執筆の分離(WebWeaver)**
- Planner: 探索とアウトラインを**交互に**進化させる(静的アウトラインの「化石化」防止)。成果物 = 引用ID付きアウトライン+メモリバンク。
- Writer: アウトラインを契約として節単位に retrieve→write、**書き終えた節の証拠は履歴からマスク**。
- 効果は引用精度に最も顕著(93.37% vs 75–78%)[B]。

**(d) 学習依存 vs 推論時機構の切り分け**
- 学習が本質的に必要: ReActモードの素の探索能力(CPT+SFT+RL の全部)、IterResearch の「良いレポート統合」を書く能力(SFTのContext Management形式データで明示的に教えている)、WebSailor系の高不確実性タスク遂行、WebLeaper の探索効率。
- 純粋に推論時機構(モデル非依存で流用可): WebWeaver の二重エージェント+メモリバンク+節単位執筆(公式実装自体が汎用API(qwen3-235b等)で動く前提 [A: README「planner and writer require a powerful model…」])、ReSum のパラダイム(要約器は汎用LLMでも可、専用化で上積み)、AgentFold のプロトコル(ただし4ブロック出力の遵守はプロンプト頼みだと不安定になり得る)、Heavy モードの並列+統合、visit の goal条件付き要約器、SelectURL、バッチ検索、引用ID規律、強制打ち切り時の「今ある情報で回答」フォールバック。

---

## 4. 我々(PEファンド内製リサーチ)への適用可能性 — 学習なしで流用できる機構

優先度順:
1. **WebWeaver型 Planner/Writer 分離+証拠メモリバンク** — 実装は数百行のプロンプト+ループで、フロンティアモデルのAPIでそのまま再現可能。引用精度が最重要のPE DD用途に最適。要点: (i) visit時に goal付き {summary, evidence} 抽出、(ii) summaryのみID付きでコンテキストへ、(iii) 引用ID必須のアウトラインを探索と交互に更新、(iv) 節単位 retrieve→write→証拠マスク、(v) References機械生成。
2. **goal条件付き二段要約(visitツール)** — どのモードでも効く基礎部品。EXTRACTOR_PROMPT はそのまま流用可 [A: inference/prompt.py]。
3. **ReSum型の要約リスタート** — 長時間調査の保険として後付け容易。要約プロンプト(証拠+ギャップ+次方向)は `WebResummer/src/prompt.py` に一次実装あり。
4. **Heavy型の並列+圧縮統合** — 高価値案件のみ n並列。統合入力を「圧縮レポート+答え」に限定するのが要点。
5. **バッチクエリ検索・SelectURL・強制打ち切りフォールバック** — 小物だが効率と頑健性に効く。
6. IterResearch の毎ラウンド全再構成は、専用SFTなしのフロンティアモデルでもプロンプトで模倣可能だが、レポート統合品質はモデル依存(Tongyiはこれを学習で担保している点に注意)。
- 学習(蒸留)まで踏み込むなら WebWeaver-3k 方式(自前フレームワークの軌跡でSFTデータ化)が最も費用対効果が高い、というのが彼らの実証 [A/B]。

---

## 出典一覧
- [A] リポジトリ(clone): https://github.com/Alibaba-NLP/DeepResearch (raw: https://raw.githubusercontent.com/Alibaba-NLP/DeepResearch/main/README.md)
  - 主要ファイル: `Tech_Report.pdf`(=arXiv:2510.24701)、`inference/{prompt.py,react_agent.py,tool_visit.py,tool_search.py}`、`.env.example`、`WebAgent/WebWeaver/{README.md,react_agent_search_id.py,react_agent_outline_write.py,tool/tool_retrieve.py,tool/tool_search_and_visit.py,tool/tool_select_url.py,prompt/*.py}`、`WebAgent/{WebResearcher,WebResummer,AgentFold,WebSailor,WebSailor-V2,WebShaper,WebLeaper,ParallelMuse,NestBrowse}/`、`Agent/{AgentFounder,AgentScaler}/README.md`
- [B] WebSearch スニペット:
  - Tongyi DR 成績確認: https://tongyi-agent.github.io/blog/introducing-tongyi-deep-research/ (スニペット経由; 直接fetchはproxy遮断)
  - WebWeaver 数値: https://www.emergentmind.com/papers/2509.13312 / https://neurohive.io/en/frameworks/webweaver-open-source-framework-for-deep-research-outperforms-openai-deepresearch-and-gemini-deep-research-on-benchmarks/ / https://www.alphaxiv.org/overview/2509.13312v2 (原典 https://arxiv.org/abs/2509.13312; arxiv直接は遮断)
- 論文インデックス(README掲載、全18本): WebWalker 2501.07572 / WebDancer 2505.22648 / WebSailor 2507.02592 / WebShaper 2507.15061 / WebWatcher 2508.05748 / WebResearcher 2509.13309 / ReSum 2509.13313 / WebWeaver 2509.13312 / WebSailor-V2 2509.13305 / AgentFounder 2509.13310 / AgentScaler 2509.13311 / AgentFold 2510.24699 / WebLeaper 2510.24697 / BrowseConf 2510.23458 / 2510.24694 / ParallelMuse 2510.24698 / AgentFrontier 2510.24695 / NestBrowse 2512.23647
