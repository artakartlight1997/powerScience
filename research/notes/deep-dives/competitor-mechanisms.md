# 競合Deep Research系システム 機構完全目録

調査日: 2026-08-22 / 調査手段: WebSearch多方向照合(英語・日本語)。一次ソース(openai.com, cdn.openai.com, moonshotai.github.io, blog.google, perplexity.ai, arxiv.org, medium等)は本環境の egress proxy で遮断されたため、**WebSearch のスニペット(一次ソース本文の引用を含む)を複数クエリで交差検証**した。
確度定義: **高**=一次ソース本文の引用が複数クエリで一致 / **中**=二次ソースまたは単一スニペット / **低**=報道・推測レベル。

---

## 0. 総括比較表(システム × 機構カテゴリ)

| カテゴリ | Google Gemini DR | OpenAI DR | Kimi-Researcher | Perplexity DR |
|---|---|---|---|---|
| (a) 計画 | モデルが計画生成→**ユーザー承認/編集必須**。実行中も反復再計画 | 中間モデルが**明確化質問**→計画提示(編集可)。承認ゲートは弱い | クラリファイ質問→計画。以降はモデル内部で自律計画(RL学習済) | 計画は内部生成、**承認ゲートなし**。逐次自己修正 |
| (b) 探索制御 | 反復的計画+ギャップ特定。多角クエリ一括生成。Max版は拡張test-time compute | 5–30分自律。バックトラック・方針転換をRLで学習 | 平均23ステップ、70+クエリ/軌道、50+イテレーション | 20–50クエリ、2–4分。反復探索→ギャップ特定→精緻化 |
| (c) 検索・ブラウズ | Google検索+ページ本文読解(スニペットでない)。深部ナビ | 検索・クリック・スクロール・ファイル解釈+Python。数百ソース | 並列内部検索ツール+テキストブラウザ+コーディングツール。200+ URL/タスク | 自社検索エンジン+読解。数百ソース |
| (d) 検証 | 全ソースをリンク引用。自己批判パス複数回 | 文・段落単位の引用。事実検証機構は明示なし | 矛盾ソースの相互検証・回答前の自発的再確認(RLで創発) | インライン引用。引用精度は高い(FACT 90.24%)が捏造率報告も |
| (e) 文脈管理 | 1Mトークン+RAG併用 | 不明(o3系の長文脈。明示なし) | **学習された文脈管理**(重要情報保持・不要文書破棄、10→50+イテレーション化) | 不明(R1系128K推定) |
| (f) 実行基盤 | **非同期タスクマネージャ**、プランナー/タスクモデル共有状態、部分エラー回復 | 非同期(API: background mode+webhook)。所要5–30分 | 非同期rollout、**turn-level partial rollout(1.5x加速)**、統一sandbox(K8s) | 同期的・高速(3分未満) |
| (g) 学習 | 多段計画のデータ効率学習(詳細非公開) | **end-to-end RL**(o3ファインチューン、o1と同じRL手法、多タスク・ルーブリック報酬) | **end-to-end agentic RL**(REINFORCE変種+γ減衰、成果報酬+形式報酬、on-policy、負例制御) | DeepSeek R1改造版(報道)+TTC拡張フレームワーク。独自RLは不明 |
| (h) 出力 | 構造化レポート→Docs出力、Audio Overview、追質問可 | 引用付きレポート、グラフ/画像埋込、同スレッド追質問、後にPDF出力 | インタラクティブHTML/Word/PPT/Excel/PDF、埋込チャート | 5–15頁レポート→PDF/Docs/Perplexity Page共有 |
| (i) 人間介入 | 計画承認・編集(最強のゲート) | 明確化質問応答、実行中の割込追加(後期版) | クラリファイ段階のみ | 実質なし(事後フォローのみ) |
| (j) 弱点 | 浅い分析・SEOソース混入・英語偏重。RACE 48.88(1位)だが | 幻覚・権威/噂の弁別・確信度較正・引用書式エラー(自認) | 第三者ベンチ掲載少。汎用性不明 | 引用幻覚率37%報告、深さ不足(rubric準拠~50%) |

---

## 1. Google Gemini Deep Research

### (a) 計画
- ユーザーの質問から**モデルが複数ステップの研究計画を生成し、ユーザーが承認または修正**してから実行開始。承認前に計画の編集で探索戦略を調整可能。【確度: 高】
- 実行中は「各ステップでこれまでの収集情報にグラウンディングし、欠落情報・不整合を特定して再計画」する反復計画。包括性と計算量/待ち時間のトレードオフを明示的に管理。【確度: 高(Google公式ブログ引用スニペット)】
- 出典: https://blog.google/products/gemini/google-gemini-deep-research/ / https://blog.google/innovation-and-ai/technology/developers-tools/deep-research-agent-gemini-api/ / https://gemini.google/overview/deep-research/

### (b) 探索制御
- 「検索→興味深い情報の発見→それに基づく新検索」の逐次進化型。クエリは学習に応じて絞り込まれる。【確度: 高】
- 計画時に「反論・対立証拠を含む多角的クエリ集合」を一括生成→実行→本文読解→ギャップ特定→再検索のループ。【確度: 高】
- ステップ/クエリ上限の公表値: **不明**。実測では1タスクで数十~数百サイト(一比較テストで47ソース vs ChatGPTの18)。【確度: 中】
- Deep Research Max(2026/4, Gemini 3.1 Pro)は「拡張test-time compute」で反復plan-search-reason-refineを強化。【確度: 中】
- 出典: https://the-decoder.com/google-launches-deep-research-and-deep-research-max-agents-to-automate-complex-research/ / https://www.sectionai.com/blog/chatgpt-vs-gemini-deep-research

### (c) 検索・ブラウズ
- Google検索アルゴリズムでソース選定。スニペットでなく**ソースページ本文を読解**。サイト深部への航行が改良された(API版)。【確度: 高】
- Workspace統合: Gmail/Drive(Docs, Slides, Sheets, PDF)/Chatも検索対象に追加可。Max版はMCP経由で社内システムにも接続。【確度: 中〜高】
- 出典: https://www.developer-tech.com/news/gemini-deep-research-workspace-integration/ / https://ai.google.dev/gemini-api/docs/interactions/deep-research(遮断・タイトルのみ)

### (d) 検証・グラウンディング
- 全ソースをレポート内で引用リンク化(クリックで原典検証可能)。【確度: 高】
- レポート生成時に「情報の批判的評価・主要テーマと不整合の特定・**複数回の自己批判パス**」。【確度: 高】
- 数値の専用検証機構: **不明**。

### (e) 文脈管理
- **1Mトークンのコンテキストウィンドウ+RAGの併用**。セッション内で学習した全内容を「記憶」し、フォローアップに利用。【確度: 高】
- 出典: https://blog.google/products/gemini/google-gemini-deep-research/(スニペット経由)

### (f) 実行基盤
- **新規開発の非同期タスクマネージャ**: プランナーとタスクモデル間で共有状態を維持し、**タスク全体を再起動せずにエラーから優雅に回復**。【確度: 高】
- 完全非同期: 開始後にアプリを離れてもPCを切っても継続、完了時に通知。所要は数分〜十数分。【確度: 高】
- API版(2025/12〜, Gemini 3 Pro基盤 → 2026/4 Gemini 3.1 Pro / Max)はGemini APIのInteractions経由。【確度: 中】

### (g) 学習
- 「多段計画をデータ効率よく学習させることでオープンドメイン対応を実現」との記述のみ。RL/SFTの内訳・報酬設計: **不明(非公開)**。【確度: 中】

### (h) 出力
- 構造化レポート(章立て)。**Google Docsへワンクリック出力**、**Audio Overview(ポッドキャスト型音声)**化、レポートへの追加質問・修正指示が可能。【確度: 高】

### (i) 人間介入点
- ①事前: 計画の承認・編集(4社中最強の介入ゲート) ②事後: フォローアップ質問・Docs上編集。実行中の介入: **不明(基本不可)**。

### (j) 弱点・第三者評価
- **DeepResearch Bench (RACE)**: Gemini-2.5-Pro DR **48.88で総合1位**。FACT: 平均有効引用数 **111.21**(圧倒的多数)だが引用精度はPerplexityに劣後。【確度: 高】 出典: https://deepresearch-bench.github.io/ / https://arxiv.org/pdf/2506.11763
- **HLE**: Gemini 3 Pro版DRで**46.4%**(2025/12) → Max版 **54.6%**、**BrowseComp 85.9%**、DeepSearchQA 93.3%(2026/4, Google自己申告)。【確度: 中】
- DeepResearchEval系評価: rubric準拠 65–70%で首位。【確度: 中】
- 批判: 分析が浅く「quick Google search程度」/SEOソース混入・ソース信頼性/英語ソース偏重/レポートが冗長。人文学研究で「Garbage In, Garbage Out」批判。【確度: 中】
- 出典: https://medium.com/age-of-awareness/garbage-in-garbage-out-why-gemini-deep-research-cant-do-basic-humanities-research-0311c54bdb91 / https://dev.to/criticalmynd/what-users-say-about-gemini-deep-research-3io7

---

## 2. OpenAI Deep Research

### (a) 計画
- 開始前に**中間モデル(intermediate model)がユーザー意図を明確化する質問**(目的・好み・制約)を提示。研究計画も提示され**レビュー・編集可能**。Gemini型の明示的承認ボタンより弱いゲート。【確度: 高】
- 実行中の再計画: RLで「多段軌道の計画・実行・**バックトラック・リアルタイム情報への反応**」を学習済み(=計画はモデル内部化)。【確度: 高】
- 出典: https://help.openai.com/en/articles/10500283-deep-research-faq / https://openai.com/index/introducing-deep-research/

### (b) 探索制御
- **5〜30分自律実行、数百のオンラインソースを閲覧**。途中で方針転換(pivoting)。ステップ上限の公表値: **不明**。【確度: 高】
- 2026/2更新: スコープを特定サイトに限定する指定、MCPサーバでのデータ接続、ステアリング改善。【確度: 中】

### (c) 検索・ブラウズ
- ツール: **検索・クリック・スクロール・ファイル解釈**のブラウジング+**sandbox内Pythonツール**(計算・データ分析・グラフ描画)。テキスト・画像・PDFを読解。ユーザーアップロードファイルも閲覧。【確度: 高(system cardスニペット)】
- agent mode統合(2025/7)でビジュアルブラウザも利用可能に。【確度: 中】
- 出典: https://cdn.openai.com/deep-research-system-card.pdf(遮断・スニペット経由)

### (d) 検証・グラウンディング
- **文・段落単位の引用**(cite specific sentences or passages)。生成グラフ・ウェブ画像の埋込。【確度: 高】
- 明示的な事実検証・数値照合の機構: **不明**(第三者は「検証せず集約するアグリゲータ」と批判)。

### (e) 文脈管理
- 公表なし: **不明**。o3系の長コンテキスト+ブラウジング要約に依存と推定。【確度: 低】

### (f) 実行基盤
- ChatGPT内で非同期実行、サイドバーに実行ステップとソースのリアルタイム要約。API版(2025/6, o3-deep-research / o4-mini-deep-research)は **background mode + webhook通知 + MCP + Code Interpreter**。価格: o3-DR $10/$40、o4-mini-DR $2/$8(per 1M in/out)。【確度: 高】
- 出典: https://developers.openai.com/api/docs/guides/deep-research / https://cookbook.openai.com/examples/deep_research_api/introduction_to_deep_research_api

### (g) 学習 — 「end-to-end RL」の根拠
- 一次根拠①(発表ブログ本文): 「**trained end-to-end with reinforcement learning on hard browsing and reasoning tasks across a range of domains**」— この訓練で多段軌道の計画・実行・バックトラックを学習。【確度: 高】 出典: https://openai.com/index/introducing-deep-research/ / https://cdn.openai.com/API/docs/deep_research_blog.pdf
- 一次根拠②(同ブログ): 「ブラウザ+Pythonツール使用を要する実世界タスクで、**o1と同じRL手法**で訓練」「**o3のファインチューン版**」。【確度: 高】
- 一次根拠③(System Card): 「**multi-task RL**: 正解付き自動採点タスクから**詳細ルーブリックで採点される開放型課題**まで」+o1由来の安全データセット+ブラウジング固有安全データ。【確度: 高】 出典: https://openai.com/index/deep-research-system-card/
- 補強: Sequoia Capital podcast(DRチームのIsa Fulford/Josh Tobin出演)「Training AI Agents End-to-End」、Interconnects (Nathan Lambert) の分析。 出典: https://sequoiacap.com/podcast/training-data-deep-research/ / https://www.interconnects.ai/p/rl-backlog-openais-many-rls-clarifying 【確度: 中】
- 2026/2に基盤がGPT-5.2系へ更新(報道)。【確度: 中】

### (h) 出力
- チャット内の構造化レポート(引用・グラフ埋込)。同スレッドでフォローアップ質問可。後期にPDFエクスポート・レポートUI改善。編集機能はネイティブには**なし**。【確度: 中〜高】

### (i) 人間介入点
- ①事前: 明確化質問への回答+計画レビュー ②実行中: 後期版では割込みでフォロー追加・ソース追加が可能(初期は不可) ③事後: フォローアップ。【確度: 中】

### (j) 弱点・第三者評価
- 自認(発表時): **幻覚・誤推論(従来モデルより低率だが残存)/権威ある情報と噂の弁別が弱い/確信度較正の弱さ(不確実性を伝えられない)/引用・書式の軽微エラー/起動遅延**。【確度: 高】
- ベンチ公表値: **HLE 26.6%**(発表時SOTA)、**GAIA 72.57(cons@64)/67.36(pass@1)で当時SOTA**、内部専門家評価で「数時間の手作業調査を自動化」。**BrowseComp 51.5%**(BrowseComp論文, 2025/4)。【確度: 高】
- DeepResearch Bench: RACEでGemini-2.5-Pro DRに次ぐ2位、**Instruction-Following次元は最高(49.27)**。【確度: 高】
- FutureSearch Deep Research Bench: **素のo3+searchがOpenAI DRを上回る**という逆転結果。【確度: 中】 出典: https://arxiv.org/pdf/2506.06287 / https://futuresearch.ai/deep-research-bench/
- 学術研究: statement hallucination(引用元と内容乖離)とcitation hallucination(参照自体の捏造)の両型を確認。 出典: https://arxiv.org/pdf/2604.03173

---

## 3. Kimi-Researcher(Moonshot AI)

一次ソース: https://moonshotai.github.io/Kimi-Researcher/(遮断・スニペット経由で本文照合)。技術ブログの主要主張は**全て確認できた**: 平均23ステップ・200+URL・文脈管理学習。

### (a) 計画
- 製品(Kimi Deep Research)は「入力分析→**スコープ確認のクラリファイ質問**→研究計画のマップ化→自律実行」の3段階。計画承認UIの詳細: **不明**。【確度: 中】
- モデルレベルでは計画自体をend-to-end RLで内部学習(planning, tool calls, browsing, context updates, final answers の全軌道から学習)。【確度: 高】

### (b) 探索制御
- **1タスク平均23推論ステップ、200+ URL探索、1軌道70+検索クエリ**。文脈管理により**単一rollout軌道が50+イテレーション**(素朴なエージェントは10イテレーションで文脈超過)。【確度: 高】
- 並列性: 検索ツール自体が「**並列・リアルタイム内部検索ツール**」。【確度: 高】

### (c) 検索・ブラウズ
- 3ツール構成: ①並列リアルタイム内部検索ツール ②インタラクティブWebタスク用**テキストベースブラウザ** ③自動コード実行の**コーディングツール**。【確度: 高】

### (d) 検証・グラウンディング
- RLからの**創発行動**として: (1) 矛盾するソース間の**相互検証(cross-verification)**による曖昧性解消、(2) 単純質問でも回答前に**追加検索で自発的に再確認する慎重性(conservative double-check)**、(3) 反復的仮説精緻化。【確度: 高】
- レポートは「数十の引用付きトレーサブルなソース」を埋込。【確度: 中】

### (e) 文脈管理
- **文脈管理メカニズム自体を学習**: 重要情報を保持し不要文書を破棄することを訓練で獲得。アブレーション: 文脈管理ありのモデルは**30%多いイテレーション**を使い、より多くの情報を獲得して高性能。文脈は数十万トークン規模。【確度: 高】

### (f) 実行基盤
- **非同期rolloutシステム**(Gym風拡張インターフェース、サーバベースでactor rollout/環境相互作用/報酬計算を並列オーケストレーション、同期比で遊休時間排除)。【確度: 高】
- **Turn-level Partial Rollout**: 時間予算超過タスクをreplay bufferに保存し、更新後の重みで残りターンを後続イテレーションで実行 → **1.5倍以上のrollout加速**(long-tail問題対策)。【確度: 高】
- **統一sandboxアーキテクチャ**(コンテナ間オーバーヘッド排除+隔離維持、K8sハイブリッドクラウドでゼロダウンタイムスケジューリング)。【確度: 高】

### (g) 学習
- **end-to-end agentic RL**(内部Kimi k系モデル)。アルゴリズム: **REINFORCE系ポリシー勾配**+訓練安定化策=**on-policy厳守、選択的負例サンプリング制御(negative sample dropping)、γ減衰報酬**(短い正解軌道を優遇)。報酬: **成果報酬(正解性)+形式報酬**。【確度: 高】
- 訓練データ: **完全自動の合成タスク生成パイプライン**(大量QA対の生成・検証、頑健なground truth抽出で信頼できる正解を保証)+ツール中心タスク+推論集約タスク。【確度: 高】
- 出典: https://moonshotai.github.io/Kimi-Researcher/ / https://ritvik19.medium.com/papers-explained-417-kimi-researcher-baa1c9f4ae68 / https://www.marktechpost.com/2025/06/24/moonshot-ai-unveils-kimi-researcher-...(いずれもスニペット照合)

### (h) 出力
- 製品版(Kimi Deep Research): **インタラクティブHTMLレポート、Word、PPT、Excel、PDF**の多形式、トピック適応の埋込チャート。【確度: 中】

### (i) 人間介入点
- クラリファイ段階のみ確認。実行中介入・計画承認: **不明**。【確度: 中】

### (j) 弱点・第三者評価
- 自己申告ベンチ: **HLE 26.9% pass@1 / 40.17% pass@4**(2025/6時点SOTA主張)、**xbench-DeepSearch 69% pass@1**(o3+search超え)、FRAMES 78.8%、Seal-0 36.0%、SimpleQA 93.6%程度。【確度: 高(自己申告)】
- **第三者評価(DeepResearch Bench, FutureSearch DRB等)への掲載はほぼ無く独立検証が薄い**のが最大の情報の穴。BrowseComp値も未公表。レポート品質(RACE型)評価なし。【確度: 高(不在の確認)】
- モデル・詳細レシピは非公開(ブログのみ、論文なし)。

---

## 4. Perplexity Deep Research

### (a) 計画
- 「研究計画(高レベル目標数個+十数個の具体的検索クエリ)」を内部生成。**ユーザー承認ゲートなし**、即時実行。学習に応じて計画を自己修正(refining its research plan as it learns)。【確度: 高】
- 出典: https://www.perplexity.ai/hub/blog/introducing-perplexity-deep-research(遮断・スニペット経由)

### (b) 探索制御
- 反復的に「検索→文書読解→次アクションの推論」。**20–50件のターゲットクエリ**、数百ソース読解、知識ギャップ特定→精緻化検索。**2–4分(多くは3分未満)**で完了=4社中最速・最浅。【確度: 高〜中(クエリ数は二次ソース)】
- 基盤: 独自の**Test-Time Compute (TTC) expansion**フレームワーク(分析サイクルの反復で理解を精緻化)。【確度: 中】

### (c) 検索・ブラウズ
- 自社検索インデックス/retrieval engine+文書読解。ブラウザ操作(クリック等)の記述なし: **不明(検索API型と推定)**。【確度: 中】

### (d) 検証・グラウンディング
- インライン引用+推論過程(chain of thought)の透明表示。**FACT引用精度90.24%で4社中最高**。ただし独立調査では引用幻覚率37%・「second-hand hallucination」(AI生成ソースの再引用)も報告され評価が割れる。数値検証機構: **不明**。【確度: 中】

### (e) 文脈管理
- 公表なし: **不明**(R1系128Kと推定)。【確度: 低】

### (f) 実行基盤
- 同期的・短時間(2–4分)特化。非同期・部分回復の記述なし: **不明**。速度最適化を明示的に売りにする。【確度: 中】
- 提供: 無料5クエリ/日(3との報道もあり)、Pro 500クエリ/日。Web先行、Mac/iOS/Android展開。【確度: 高】

### (g) 学習
- **DeepSeek R1の特別調整版(custom/tailored version)が基盤**(複数報道+同社のR1-1776公開実績で補強。ただし公式ブログはモデル名を明言せず)。独自RL訓練の有無: **不明**。【確度: 中】
- 出典: https://opentools.ai/news/perplexity-ai-launches-deep-research-tool-utilizing-deepseeks-r1-for-unrivaled-research-reports / https://www.forbes.com/sites/luisromero/2025/01/28/deepseek-now-in-perplexitys-ai-search-us-ai-dominance-challenged/

### (h) 出力
- 5–15頁のレポート(太字キーファクト・箇条書き・インラインリンク)。**PDF/ドキュメント出力、Perplexity Pageへの変換・共有**。フォローアップ質問可。Pages側は編集自由度が低いとの批判。【確度: 高】

### (i) 人間介入点
- 事前介入なし(モード選択のみ)。事後フォローアップのみ。**4社中最小の介入面**。【確度: 高】

### (j) 弱点・第三者評価
- 公表値: **HLE 21.1%**(Gemini Thinking, o3-mini, o1, DeepSeek-R1超え・当時)、**SimpleQA 93.9%**。【確度: 高(自己申告)】
- DeepResearch Bench: RACE総合でGemini/OpenAIに劣後(~42点台)、引用精度のみ首位。rubric準拠評価では~50%で最下位圏。【確度: 中】
- GPTZero調査: 引用幻覚・AI生成ソースの再引用問題。深さ不足(速度と引き換え)。【確度: 中】
- 出典: https://gptzero.me/news/gptzero-perplexity-investigation/ / https://deepresearch-bench.github.io/

---

## 5. 横断的な第三者ベンチマーク総覧

| ベンチ | Gemini DR | OpenAI DR | Kimi-Researcher | Perplexity DR | 出典 |
|---|---|---|---|---|---|
| HLE | 46.4%(3 Pro版, 自己申告)→54.6%(Max) | 26.6%(発表時) | 26.9% p@1 / 40.17% p@4 | 21.1% | 各社公表 |
| BrowseComp | 85.9%(Max, 自己申告) | 51.5% | 未公表 | 未公表 | BrowseComp論文 / Google |
| GAIA | — | 72.57 cons@64 / 67.36 p@1(SOTA) | — | — | OpenAI |
| DeepResearch Bench RACE | **48.88(1位)** | 2位(IF次元は1位 49.27) | 掲載なし | ~42(引用精度90.24%で1位) | deepresearch-bench.github.io |
| FACT 有効引用数 | **111.21(1位)** | 中位 | — | 精度1位・数は少 | 同上 |
| FutureSearch DRB | 中位 | **素のo3+searchに敗北** | — | 中〜下位 | arxiv 2506.06287 |
| xbench-DeepSearch | — | (o3+search 66%前後) | **69% p@1** | — | Moonshot |

---

## 6. 目録の穴(今後の追加調査対象)

1. **Gemini/OpenAIの訓練詳細**(報酬設計・データ規模)は完全非公開。Kimiのみ機構レベルで公開。
2. **ステップ数/クエリ数の上限値**は4社とも公式未公表(Kimiの平均値のみ)。
3. Kimi-Researcherの**独立第三者評価が不在**(自己申告ベンチのみ)。
4. Perplexityの**モデル基盤(R1改)は報道ベース**で公式確認なし。TTCフレームワークの技術詳細も不明。
5. OpenAI/Perplexityの**文脈管理方式が不明**(要約か破棄か外部メモリか)。
6. 一次ソース遮断のため、全記述はスニペット交差検証。egress緩和後に system card PDF・Moonshotブログ原文・Google APIドキュメントの直接照合を推奨。
7. 2026年時点の世代交代(OpenAI: GPT-5.2系DR、Google: Deep Research Max/Gemini 3.1 Pro、agent mode統合)は本目録では概要のみ。最新版の再計測が必要。

## 主要出典一覧
- OpenAI: openai.com/index/introducing-deep-research / openai.com/index/deep-research-system-card / cdn.openai.com/deep-research-system-card.pdf / help.openai.com/en/articles/10500283 / developers.openai.com/api/docs/guides/deep-research / sequoiacap.com/podcast/training-data-deep-research
- Google: blog.google/products/gemini/google-gemini-deep-research / blog.google/innovation-and-ai/technology/developers-tools/deep-research-agent-gemini-api / blog.google/innovation-and-ai/models-and-research/gemini-models/next-generation-gemini-deep-research / gemini.google/overview/deep-research / ai.google.dev/gemini-api/docs/interactions/deep-research
- Moonshot: moonshotai.github.io/Kimi-Researcher / ritvik19.medium.com/papers-explained-417-kimi-researcher / marktechpost.com (2025/06/24) / kimi.com/features/deep-research
- Perplexity: perplexity.ai/hub/blog/introducing-perplexity-deep-research / x.com/perplexity_ai/status/1890452005472055673
- 第三者評価: deepresearch-bench.github.io (arxiv 2506.11763) / futuresearch.ai/deep-research-bench (arxiv 2506.06287) / arxiv 2506.18096 (Deep Research Agents survey) / arxiv 2604.03173 (引用幻覚) / gptzero.me/news/gptzero-perplexity-investigation
