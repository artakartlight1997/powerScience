# CONTRACTS — モジュール契約 v2(実装より先に固定する「こうあるべき論」)

> **本書が正。実装が本書と食い違ったら実装のバグである。**
> 変更は本書を先に改訂し(人間承認)、その後にコードを追従させる。

## -1. poc からの是正(なぜ v2 があるか)

poc(v1)は台帳・監査・検証エンジンは正しかったが、**入力の向きが逆**だった:
資料ドロップを一次経路にし、Web リサーチを `--online` オプションに落としていた。
これは P23(起動入力は社名のみ。残りは全部システムが取りに行く)への違反である。
v2 の契約は **R-0 を全ての原理の上位に置く**。

## 0. 設計原理

| # | 原理 | 帰結 |
|---|---|---|
| **R-0** | **これはリサーチシステムである。起動入力は「社名(または業界名)」のみ。外部収集ループが一次経路であり、既定で有効。資料ドロップ(IM等)は任意の補助入力**(売り手の主張として突合対象になるだけ) | Deep Research の代替+検証・監査。「ファイルを用意しないと動かない」状態は仕様違反 |
| R-1 | **収集は 計画(gap→クエリ)→検索→取得→スナップショット の4段**。スナップショットに残らない Web 情報は証拠になれない | 検索結果の要約やLLMの記憶は証拠にならない。捏造URLは取得段で自然に死ぬ |
| C-1 | モジュールは Protocol にのみ依存(`LLMClient` / `SearchClient` / `Fetcher`) | テストは Fake で回る。検索APIの差し替えが1クラスで済む |
| C-2 | 判定ロジック(audit / fill / **クエリ計画**)は純関数。I/O も LLM も呼ばない | 決定論的・ユニットテスト容易 |
| C-3 | LLM 出力は必ず JSON+pydantic 検証。失敗は1回だけ再試行、それでも失敗なら**その単位を落とす** | 流暢な壊れた出力が入らない |
| C-4 | 全ての状態変更はイベント(追記専用・ハッシュ連鎖)を経由 | 監査・改竄検知・リプレイ |
| C-5 | 外部との境界は gate を必ず通る(ホスト allowlist・パス・taint) | 一箇所で強制 |
| C-6 | 生成モデルと検証モデルは別ベンダ。同一は起動拒否(明示フラグで解除可) | 盲点の共有を防ぐ(P5) |
| C-7 | エラーは握りつぶさない。単位ごとに degrade し、ケース全体は落とさない | 部分失敗が全滅にならない |
| C-8 | 縮退は黙って起きない: WARNING をログへ。未処理例外はトレースバック込みで `data/logs/prism.log`。資料本文はログに書かない(MNPI) | バグの所在をユーザに報告させない |

## 1. データ契約(`prism/contracts.py` が唯一の定義)

v1 と同じ(Case / SpecItem / Source / Evidence / Judgment / Question /
Contradiction / Event)に、以下を追加:

```
Query      { item_key, text }                 ← gap から機械生成する検索クエリ
SearchHit  { url, title, snippet }            ← 検索の生の戻り。証拠ではない
```

## 2. インタフェース契約(Protocol)

```python
class LLMClient(Protocol):
    def complete_json(self, role: Literal["generator","verifier","online"],
                      system: str, user: str) -> dict: ...

class SearchClient(Protocol):
    def search(self, query: str, k: int) -> list[SearchHit]: ...  # 失敗は []

class Fetcher(Protocol):
    def fetch(self, url: str) -> str | None: ...                  # 失敗は None
```

## 3. 主要関数の契約(事前・事後条件)

| 関数 | 事前条件 | 事後条件 |
|---|---|---|
| `pipeline.start_case(name,…)` | **社名だけで呼べる** | Case+スペック実体化。archetype 未指定なら `identify` が外部情報から同定(P23)。同定不能は**推測せず** ConfigError で `--archetype` を要求 |
| `identify.archetype(llm,…)` | 選択肢=templates のアーキタイプID | 選択肢外の答えは受理しない。人間の `--archetype` が常に優先(一言で差し替え) |
| `research.build_queries(case,items,judgments)` | **純関数** | gap の優先順に検索クエリ列。web で取れる見込みのある項目(retrievability に public/premium)だけ。vdr/expert 項目にクエリを浪費しない(P21) |
| `research.collect(queries,…)` | gate 必須 | 検索→取得→**必ずスナップショット**→Source(kind=web, untrusted)。同一 content_hash は登録しない(冪等)。取得できなかった URL からは何も生まれない |
| `ingest.scan(case)` | 任意の補助。フォルダが無くても正常 | v1 と同じ(冪等・as_of 規約・seller は主張扱い) |
| `extract.run` / `verify.*` / `audit.judge` / `fill.*` | v1 と同じ | v1 と同じ(I1/I3/I8/I9、P10/P19/P20/P22) |
| `pipeline.run(case)` | — | 各ラウンド: 補助取込 → **Web収集** → 抽出 → 検証 → 監査 → 停止判定(理由必須) |

## 4. 不変条件 → テストの対応(CI で全て緑であること)

v1 の表(I1/I3/I6/I8/I9、C-5/C-6、E2E)に加えて:

| 不変条件 | テスト |
|---|---|
| R-0: 社名だけで E2E が完走する(資料ファイルなし) | integration/test_research_e2e |
| R-1: スナップショットの無い Web 証拠は grounded=pass になれない | unit/test_verify(v1 から継承) |
| 捏造URL(取得失敗)からは Source も Evidence も生まれない | unit/test_research |
| クエリ計画は vdr/expert 専用項目に浪費しない | unit/test_research |
| identify は選択肢外を受理せず、失敗時は人間に委ねる | unit/test_identify |
| 補助ドロップ(IM)を足しても I3(売り手単独 filled 不可)が保たれる | integration/test_research_e2e |

## 5. 変更管理

- templates/ は定義ファイル。業態追加はコード変更なし
- 本書・EVALUATION.md の変更は人間が承認(P13)
