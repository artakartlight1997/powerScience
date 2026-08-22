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

v1 と同じ(Case / SpecItem / Source / Evidence(値は ExtractedValue)/ Judgment /
Question / Contradiction / Event)に、以下を追加:

```
Query      { item_key, text }                 ← gap から機械生成する検索クエリ
SearchHit  { url, title, snippet }            ← 検索の生の戻り。証拠ではない
```

数値の扱い(P19 の細則): 抽出値の解釈はコードのみが行う。負号(▲△−-)は数値に
隣接する位置で判定し、範囲・遷移表現(「3〜5億円」「10億円→12億円」)は単一値に
潰さない(num なしで raw のみ保持)。単位は次元(円・%・人…)に正規化して比較する —
「10億円」と「1,500百万円」は同一次元として矛盾検出の対象になる。

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

`LLMClient` は `calls: int`(実呼び出し累計)を持つ — 停止則 R2 の入力。

## 3. 主要関数の契約(事前・事後条件)

| 関数 | 事前条件 | 事後条件 |
|---|---|---|
| `pipeline.start_case(store,cfg,llm,name,…)` | **社名だけで呼べる** | Case+スペック実体化。archetype 未指定なら `identify` が外部情報から同定(P23)。同定不能は**推測せず** ConfigError で `--archetype` を要求。**人間の archetype 指定は既存ケースに対しても常に優先**(黙って無視しない — 差し替え時はスペック再実体化)。case_id は安全な文字集合のみ受理 |
| `identify.archetype(llm,name,industry,choices)` | 選択肢=templates のアーキタイプID | 選択肢外の答えは受理しない |
| `research.build_queries(case,items,judgments,max_queries)` | **純関数** | gap の優先順に最大 max_queries 件。公開経路(public/premium)を含む項目だけ — この述語は `fill.is_public_reachable` を audit・R4 判定と共有する。vdr/expert 項目にクエリを浪費しない(P21) |
| `research.collect(store,case,gate,search,fetcher,queries,…)` | gate 必須 | 検索→取得→**必ずスナップショット(gate のパス検査を通す)**→Source(kind=web, untrusted)。同一 URL・同一 kind 内の同一 content_hash は再取得/再登録しない(冪等・P22)。取得予算(max_fetch)超過後は検索もしない。取得できなかった URL からは何も生まれない |
| `ingest.scan(store,case,inbox_dir,data_dir,trust_tiers,gate)` | 任意の補助。フォルダが無くても正常 | 冪等(同一 kind 内 hash)・as_of 規約(不正日付は警告して mtime へ)・seller は主張扱い。**1ファイルの失敗はそのファイルだけ落とす**(C-7)。inbox 外を指すリンクは拒否 |
| `extract.run` / `verify.*` / `audit.judge` / `fill.*` | v1 と同じ | v1 と同じ(I1/I3/I8/I9、P10/P19/P20/P22)+数値細則(§1)。クラスタは union-find(入力順に依存しない)。未クラスタ証拠は独立と数えない。expect_absent 項目で存在主張と不在確認が併存したら filled 不可 |
| `pipeline.run(store,cfg,case_id,llm,search,fetcher)` | — | 各ラウンド: 補助取込 → **Web収集** → 抽出 → 検証 → 監査 → 停止判定(理由必須)。**再実行は続行**: 前回の停止理由・ラウンド数を今回の停止判定に持ち込まない。R4 は項目そのものから公開 gap を数える(質問リストの上限に影響されない) |

## 4. 不変条件 → テストの対応(CI で全て緑であること)

v1 の表(I1/I3/I6/I8/I9、C-5/C-6、E2E)に加えて:

| 不変条件 | テスト |
|---|---|
| R-0: 社名だけで E2E が完走する(資料ファイルなし) | integration/test_research_e2e |
| R-0: CLI 1コマンド(research)が rc=0 で成果物を出す | integration/test_cli |
| I6: 末尾切り詰め・全消去も検知(chain_heads アンカー) | unit/test_events |
| R-1: スナップショットの無い Web 証拠は grounded=pass になれない | unit/test_verify(v1 から継承) |
| 捏造URL(取得失敗)からは Source も Evidence も生まれない | unit/test_research |
| クエリ計画は vdr/expert 専用項目に浪費しない | unit/test_research |
| identify は選択肢外を受理せず、失敗時は人間に委ねる | unit/test_identify |
| 補助ドロップ(IM)を足しても I3(売り手単独 filled 不可)が保たれる | integration/test_research_e2e |

**既知の限界(明示)**: ①chain_heads アンカーは同一 SQLite 内にあるため、
「イベントとアンカーの両方を整合させて改竄する」攻撃は検知できない。本番では
アンカー(件数+末尾ハッシュ)を外部ストレージ/署名へ退避する。
②C-5 の taint 検査(`gate.check_untainted`)は「特権操作(シェル・外部送信等)」に
untrusted 値を渡す時の門番だが、**PoC には特権操作が存在しない**ため呼び出し箇所も
ない(APIとテストのみ)。特権操作を導入する変更は、必ずこの gate を経由すること。

## 5. 変更管理

- templates/ は定義ファイル。業態追加はコード変更なし
- 本書・EVALUATION.md の変更は人間が承認(P13)
