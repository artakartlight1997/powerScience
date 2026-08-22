# Sakana AI AB-MCTS (TreeQuest) — 実装コード精読レポート

- 調査日: 2026-08-22
- 一次資料: `raw.githubusercontent.com` から取得した実コード
  - SakanaAI/treequest@main(v0.3.2, pyproject.toml 確認)
  - SakanaAI/ab-mcts-arc2@main
- 確度表記: **[A]** = raw で取得したコードから直接確認した事実。**[推測]** = コードに書かれていない解釈・推論。
- ローカル保存先(取得済み原本): `/tmp/claude-0/-home-user-powerScience/4fca4bf4-d2ec-5c64-9ce4-5429919b7f91/scratchpad/tq/` および `.../scratchpad/arc2/`

---

## 1. スコア(報酬)インタフェース — 「外部供給・学習しない」の正確な意味

**[A]** 中核となる型定義は `src/treequest/types.py` の 5 行だけである:

```python
# Type of `generate_fn`, which generates the child node given the state of parent node.
# In case the parent node is root, None is given as an argument.
GenerateFnType = Callable[[Optional[NodeStateT]], Tuple[NodeStateT, float]]
```

- ユーザーが渡す `generate_fn(parent_state) -> (new_state, score)` が**生成とスコアリングの両方**を担う。TreeQuest 側には評価器・価値関数・報酬モデルは一切存在しない。ライブラリが受け取るのは float 一個。
- **[A]** 値域は [0,1] 必須。`src/treequest/algos/tree.py` の `Node.__post_init__` で実行時検証される:

```python
# Scores should be in the range from 0 to 1. For root, we set it to be -1.0 as a placeholder.
score: float = -1.0
...
if self.validate_score_range and not (self.score <= 1.0 and self.score >= 0.0):
    raise RuntimeError(f"The score value should be between 0 and 1, while {self.score} is set.")
```

さらに beta 分布使用時は `prob_state.py` の `tell_observation` に `assert obs >= 0 and obs <= 1` がある **[A]**。

- **[A]** 呼ばれ方(`ABMCTSA.step`):
  1. `ask` が Thompson Sampling で「どのノードから・どのアクションで」生成するかを決め、`Trial`(ULID id 付き)を発行
  2. ユーザーの `generate_fn[action](node.state)` が呼ばれる
  3. `tell(state, trial_id, (new_state, score))` が新ノードを木に追加し、スコアを親系列の全確率分布にバックプロパゲート
- 「学習しない」の正確な意味 **[A]**: 探索中に更新されるのは各ノードの Thompson Sampling 用の共役事後分布(Beta / Normal-Inverse-Gamma のパラメータ)**だけ**。スコアを生む関数側は一切適応されず、スコアの意味論はライブラリにとって完全に不透明(opaque float)。同じスコアが (a) GEN/CONT 判断、(b) 子ノード選択、(c) モデル(アクション)選択、(d) 最終 top-k 抽出、の全てに使い回される。
- **オープンエンドタスクで使う場合に書かねばならないもの [A→帰結は推測]**: 「候補 state を受け取り [0,1] の一次元スカラーを返す決定的関数」を自前で用意することが必須。ARC 実装では「訓練デモとの完全一致率」がこれに当たる(§6)。ビジネスリサーチのような正解のない領域では、この float を LLM-judge やヒューリスティックで捏造するしかなく、その品質が探索全体(分岐判断・モデル選択・最終回答選択)を同時に支配する **[推測だがコード構造からの直接の帰結]**。

## 2. 幅/深さの適応分岐(GEN ノード)の実装

### AB-MCTS-A(`algos/ab_mcts_a/prob_state.py`, `algo.py`)**[A]**

各ノードに `NodeProbState` が付き、「GEN(新規子生成=幅)」vs「CONT(既存子を降りる=深さ)」を Thompson Sampling で決める。GEN ノードは実体のあるノードではなく、**GEN/CONT 用の 2 つの確率分布**として実装されている:

```python
self.gen_vs_cont_probas = {"shared": {"GEN": ProbabilisticDist(prior_config),
                                      "CONT": ProbabilisticDist(prior_config)}}
```

選択(`_select_next_multiarm_bandit`)は 2 段階: まず GEN/CONT 分布から 1 サンプルずつ引いて大きい方を採用。GEN なら次にアクション選択(§3)、CONT なら子ノードごとの分布 `node_probas` から Thompson Sampling。

**事前分布(デフォルト)[A]**:

```python
@dataclasses.dataclass
class BetaPrior:          # "The default is Jeffrey's prior"
    a: float = 0.5
    b: float = 0.5

@dataclasses.dataclass
class GaussianPrior:      # Normal-Inverse-Gamma
    m: float = 0
    kappa: float = 1
    nu: float = 1
    tau_square: float = 0.1
```

`ABMCTSA.__init__` のデフォルトは `dist_type="gaussian"`(README のコメントと異なり Beta ではない)。ARC-AGI-2 実験は `DIST_TYPE=beta` を明示指定(§6)。

**更新式 [A]** (`ProbabilisticDist.tell_observation`):
- Beta: `a += obs; b += 1 - obs`(連続スコアを「成功確率の分数観測」として扱う)
- Gaussian: 全観測を保持して Normal-Inverse-Gamma の共役更新(コメントで Murphy の教科書 §3.4.3.3 を参照):

```python
new_kappa = kappa + n
new_nu = nu + n
new_m = (kappa * m + n * ave) / new_kappa
new_tau_square = (nu*tau_square + var + n*kappa*(m-ave)**2/(kappa+n)) / new_nu
```

サンプリングは `sigma² ~ InvGamma(nu/2, nu·tau²/2)`, `mu ~ N(m, sigma²/kappa)` で **mu を返す**(報酬そのものではなく平均の事後サンプル)。

**バックプロパゲーション [A]** (`ABMCTSA._backpropagate`): 新ノードのスコアは (1) グローバルな `all_rewards_store[action]`、(2) 親の GEN 分布とアクション分布、(3) ルートまでの経路上の各祖先における CONT 分布・子ノード分布、の全てに同一値で `tell_observation` される。

### AB-MCTS-M(`algos/ab_mcts_m/pymc_interface.py`)**[A]**

GEN vs CONT を PyMC の**ベイズ混合(階層)モデル**で行う。子ノード(グループ)ごとの効果 `alpha_j = mu_alpha + z_alpha_j * sigma_alpha`(非中心化パラメタライズ)、観測 `y ~ N(alpha_j, sigma_y)`。GEN ノードは「未観測の新グループ」`y_new ~ N(mu_alpha + z_alpha_new * sigma_alpha, sigma_y)` として予測される — これが「混合モデルで新規ノードの報酬分布を外挿する」の実装実体:

```python
mu_alpha = pm.Normal("mu_alpha", mu=self.get_reward_average_prior(action), sigma=self.prior_mu_alpha_sigma)  # mu既定0.5
sigma_alpha = pm.HalfNormal("sigma_alpha", sigma=self.prior_sigma_alpha_sigma)   # 0.2 "answers間のばらつき"
sigma_y = pm.HalfNormal("sigma_y", sigma=self.prior_sigma_y_sigma)               # 0.3 "answer内のばらつき"
```

ハイパーパラメータ **[A]**: `prior_mu_alpha_sigma=0.2, prior_sigma_alpha_sigma=0.2, prior_sigma_y_sigma=0.3`、報酬平均事前は 0.5(コメント: "50% prob of solving the problem")。推論は numpyro NUTS 4 chains。Thompson サンプルは posterior predictive の値から `np.random.choice(arr.values.flatten())` で 1 個引くだけ(`get_score`)。

**枝刈り [A]**: `PruningConfig(min_subtree_size_for_pruning=4, same_score_proportion_threshold=0.75)` — サブツリー内で `round(reward*100)` が同一の観測が 75% 以上を占めると選択候補から除外。**スコアが離散的に張り付くこと(ARC の 0/1 系スコア)を前提にした設計** [A、含意は推測]。

## 3. Multi-LLM(モデル選択の探索化)の実装

**[A]** 「モデル」は単に `generate_fns: dict[str, GenerateFn]` の**キー(アクション名)**である。ARC 実験ではキーがモデル名(`o4-mini-2025-04-16` 等)そのもの。3 戦略が実装されている(A/M 共通のインタフェース):

- `"stack"`: 先にアクション分布 `action_probas`(モデルごとの Beta/Gaussian 事後)から Thompson Sampling でモデルを選び、そのモデル専用の GEN/CONT 分布で幅/深さを決める。
- `"multiarm_bandit_thompson"`(ABMCTSA のデフォルト): 先に共有 GEN/CONT で幅/深さを決め、GEN のときだけ**木全体の全報酬履歴** `all_rewards_store: Dict[action, List[float]]` からモデルごとに事後を再構成して Thompson Sampling(`_select_best_action`)。つまりモデル選択はノード局所ではなく**グローバルなバンディット**。
- `"multiarm_bandit_ucb"`: 同構造で UCB1、探索定数は `sqrt(2)`:

```python
ucb_score = sum(scores)/len(scores) + sqrt(2) * sqrt(log(all_len)/len(scores))
```

**[A]** ab-mcts-arc2 の `config.yaml` は `class_name: ABMCTSA, model_selection_strategy: "stack"` + `run_experiments.sh` で `dist_type=beta` を追加、モデルは o4-mini / DeepSeek-R1-0528 (OpenRouter) / Gemini-2.5-Pro の 3 つ、全て temperature 0.6。

## 4. ノードが保持する状態・並列化・チェックポイント

**[A]** `Node` dataclass の全フィールド: `state(任意のユーザーオブジェクト), score, expand_idx, parent, children, trial_id`。木を降りるとき子に引き継がれるのは**親の `state` オブジェクトだけ**(`generate_fn[action](node.state)`)。会話履歴・祖先系列・兄弟の情報は TreeQuest は一切渡さない — 深さ方向の文脈継承はユーザーが `state` に詰め込んだ分だけ **[A]**。ARC 実装の `NodeState` は `generation_result(プロンプト+生成文), eval_results(デモ毎の出力/正解), model_name` を持ち、リファインプロンプトは**直前ノードの結果のみ**から組み立てられる(祖先全体の履歴は使わない)**[A]**。

- **ask/tell 分離 [A]**: `Trial`(ULID, `node_to_expand`, `action`, `parent_state`, タイムスタンプ, status RUNNING/COMPLETE/INVALID)により、tell は順序非依存・冪等。docstring に「ask と tell の間でプロセスが止まっても再開できる情報を保持する」と明記。
- **並列化 [A]**: ABMCTSA の `ask_batch` は単にループ(「軽量なので並列化しない」とコメント)。ABMCTSM は joblib/loky のプロセスプールで選択計算(PyMC サンプリング)を並列化。README は「大きな batch_size は木を過度に広くする(選択が同一状態から独立に走るため)」と警告し `batch_size<=5` を推奨 **[A]**。
- **チェックポイント [A]**: アルゴリズムオブジェクトは stateless、探索状態(`ABMCTSAAlgoState` = 木 + 全 Thompson 状態 + 全報酬履歴 + TrialStore)は丸ごと **pickle**。arc2 の `run.py` は 10 ノード毎/2 冪毎に `checkpoint_latest.pkl` を書き、再開時は `pickle.load` してノード数の差分だけ回す。`sys.setrecursionlimit(20000)` は親子参照を持つ木の pickle のためとみられる **[A(コードとコメント)/理由付けは推測]**。

## 5. コードから読み取れる構造的限界

1. **最終候補選択 = 外部スコアの argmax [A]**。`ranker.py` の `top_k` は `sorted(state_scores, key=score, reverse=True)[:k]` のみ。探索がどれだけ賢くても、**最後に 1 つを選ぶ機構は「公開スコア降順」以外に存在しない**。
2. **pass@k 問題の実装上の姿 [A]**: arc2 の成績判定 `calculate_is_correct`(`experiments/arc2/utils.py`)は「公開スコア top-k のうち**どれか 1 つでも**隠しテストに完全正解なら True」。さらに `eval/proc_results.py` の集計は `df_test.max(0).sum()`(タスクごとに**全ノードの隠しスコアの最大値** = オラクル的カバレッジ)。つまり報告される性能は「木の中に正解が存在した率」であり、システム自身が正解を同定したことを意味しない。正解の同定は隠しテスト(=外部の正解照合)に依存している。
3. **中間評価の依存先 [A]**: 探索中のスコアは 100% ユーザー供給。ARC では「訓練デモとの完全一致率」という**検証可能なプロキシ**があるから機能する。プロキシと真の目的(隠しテスト)の乖離は `public_scores` vs `private_scores` として明示的に測定されている(proc_results.py が両方を別 CSV に吐く)。
4. **スコアの一次元性 [A]**: GEN/CONT・子選択・モデル選択・最終選択の全判断が同一のスカラーに乗る。多目的(新規性 vs 正確性など)の扱いは構造上ない。
5. **ABMCTSM の枝刈り前提 [A]**: 同一スコア比率 75% での枝刈りは、スコアが離散値に集中する(0, 0.25, 0.5…のような)採点を暗黙に想定。連続でノイジーな LLM-judge スコアでは枝刈りがほぼ発火しない **[推測]**。
6. **深さ方向の文脈は 1 段のみ**(§4)— 「探索木」といっても各リファインは直前の親の答え+フィードバックだけを見る(arc2 実装)**[A]**。

## 6. ab-mcts-arc2 の採点関数の実物 — 「正解照合が存在する」ことの具体像

**[A]** 探索中スコア(public score, `run.py`):

```python
eval_results = task.generate_eval_results(llm_answer=result, kind="transform")
if eval_results is None:
    score = 0.0     # コードブロックが正規表現 ```python ...``` で抽出できなければ0点
else:
    score = sum(eval_result.get_score() for ...) / len(eval_results)
```

- `ARCProblem.run_transform_on_demos`: LLM が書いた `transform` 関数を**訓練デモ各例に対しサンドボックス実行**し、`EvalResultWithAns.get_score()` = `1 if self.answer == self.groundtruth else 0`(グリッドのリスト同士の**完全一致**)。スコア = 一致したデモの割合。
- 実行系 `evaluate_code.py` **[A]**: 別プロセス + `reliability_guard`(メモリ/スタック制限、破壊的 os 機能の無効化)+ timeout 60 秒 + `swallow_io`。unittest テンプレート(`test_transform.py`)は最終的に `self.assertEqual(pred, __PROBLEM_OUTPUT__)` の 1 行に帰着する。
- 最終評価(private score)**[A]**: `evaluate_on_test` が隠しテスト入力に対する完全一致で 0/1。

**対比 [推測、ただし上記事実に立脚]**: この採点は (a) 機械実行可能、(b) 決定的、(c) 正解データ(`demo["output"]`, `test["output"]`)が JSON で存在する、という 3 条件に完全に依存する。ビジネスリサーチには (c) が存在せず、(a)(b) も一般に成り立たないため、AB-MCTS をそのまま移植すると §1 の「[0,1] スカラーを返す関数」を主観評価(LLM-judge 等)で代替することになり、§5-1〜3 の構造(argmax 選択・pass@k 的カバレッジ頼み・プロキシ乖離の無補正)がそのまま弱点として顕在化する。

---

## 付録: 取得できたファイル / 読めなかったもの

**取得成功(確度 A の根拠)**: treequest — README, pyproject.toml, `src/treequest/{__init__,types,ranker,trial}.py`, `algos/{base,tree}.py`, `algos/ab_mcts_a/{algo,prob_state}.py`, `algos/ab_mcts_m/{algo,pymc_interface,numpyro_utils,_ab_mcts_m_imports}.py`。ab-mcts-arc2 — README, pyproject.toml, .gitmodules, `experiments/arc2/{run,prompt,utils}.py`, `configs/config.yaml`, `scripts/run_experiments.sh`, `eval/proc_results.py`, `src/ab_mcts_arc2/{eval_result,evaluate_code,llm_generation_interface}.py`, `tasks/arc/task.py`, `unittest_templates/test_transform.py`。

**未読(404 か未取得)**: ディレクトリ一覧 API は使えないため網羅ではない。未取得: treequest の `standard_mcts.py`, `tree_of_thought_bfs.py`, `best_first_search`, `vis/*`, `docs/PROFILING.md`, テスト群; ab-mcts-arc2 の `llm/llm_builder.py`(LLM API 呼び出し・コスト計算), `src/ab_mcts_arc2/utils.py`(reliability_guard 本体), `model_base.py`, `prompts/base.py`, `grid_repr.py`, `data_types.py`, `eval/visualize.py`。いずれも本レポートの結論(スコアIF・分岐・バンディット・限界)には影響しない周辺部と判断。
