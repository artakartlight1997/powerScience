# CONTRACTS — モジュール契約 v3(実装より先に固定する「こうあるべき論」)

> v3 = v2(第I部・全条項有効)+ 第II部(探索層 L4/L5)。
> 第II部は research/arch/07(アーキテクチャ確定版)と 08(優越証明 v1.0、
> 特に §1.1 信号設計・M-7 順序規則・§5.5 実装引き継ぎ5点)から導出した。

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
| `pipeline.start_case(store,cfg,llm,name,…)` | **社名だけで呼べる** | Case+スペック実体化。archetype 未指定なら `identify` が外部情報から同定(P23)。同定不能は**推測せず** ConfigError で `--archetype` を要求。**人間の archetype 指定は既存ケースに対しても常に優先**(黙って無視しない — 差し替え時はスペック再実体化+旧項目の判定・問いを削除)。case_id は安全な文字集合のみ受理。**既存ケースと社名が一致しない合流は拒否**(slugify 衝突による証拠混線の防止) |
| `identify.archetype(llm,name,industry,choices)` | 選択肢=templates のアーキタイプID | 選択肢外の答えは受理しない |
| `research.build_queries(case,items,judgments,max_queries)` | **純関数** | gap の優先順に最大 max_queries 件。公開経路(public/premium)を含む項目だけ — この述語は `fill.is_public_reachable` を audit・R4 判定と共有する。vdr/expert 項目にクエリを浪費しない(P21) |
| `research.collect(store,case,gate,search,fetcher,queries,…)` | gate 必須 | 検索→取得→**必ずスナップショット(gate のパス検査を通す)**→Source(kind=web, untrusted)。同一 URL・同一 kind 内の同一 content_hash は再取得/再登録しない(冪等・P22)。取得予算(max_fetch)超過後は検索もしない。取得できなかった URL からは何も生まれない |
| `ingest.scan(store,case,inbox_dir,data_dir,trust_tiers,gate)` | 任意の補助。フォルダが無くても正常 | 冪等(同一 kind 内 hash)・as_of 規約(不正日付は警告して mtime へ)・seller は主張扱い。**1ファイルの失敗はそのファイルだけ落とす**(C-7)。inbox 外を指すリンクは拒否 |
| `extract.run(source,items,llm)` | — | Evidence[](正常。0件もある)または **None(LLM障害=再試行対象)**。1ソースの証拠数は項目数×2で切り詰め(警告つき) |
| `verify.*` / `audit.judge` / `fill.*` | v1 と同じ | v1 と同じ(I1/I3/I8/I9、P10/P19/P20/P22)+数値細則(§1)。クラスタは union-find(入力順・インデックスに依存しないラベル)。同次元の数値が tolerance 超乖離する対は**決して併合しない**(矛盾検出を殺さない)。数値あり×なしも併合しない(橋の防止)。未クラスタ証拠は独立と数えない。expect_absent 項目で存在主張と不在確認が併存したら filled 不可 |
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

**運用セマンティクスの明文化(v2.1 で追補)**:
- **矛盾の resolve**: 矛盾は削除されない。毎ラウンド、open の対を現在の証拠状態で
  再評価し、成立しなくなった対(クラスタ組替え・grounding の喪失)のみ
  `status=resolved` へ遷移する — つまり resolve は**新しい証拠の追加によってのみ**
  起きる。人間の黙認や時間経過では起きない
- **問いの遷移**: gap でなくなった項目の問いは `answered` へ。発注仕様書には
  `open` のみ載る
- **一時障害の扱い**: LLM 障害で抽出できなかったソース・照合票が取れなかった証拠は
  「失敗」を恒久記録せず、次ラウンドで再試行される(R2 予算はラウンド内でも守る:
  予算到達後の照合は保留される)
- **スペックの凍結**: SpecItem(必須項目・独立クラスタ数・鮮度・見張り重み)は
  ケース作成時に焼き込まれ、テンプレ変更は既存ケースに遡及しない(監査履歴の一貫性)。
  例外は人間の archetype 差替え(再実体化+旧項目の判定・問いの削除)。一方
  stop_rules / trust_tiers / research / online の運転パラメータは実行のたびに読む

**既知の限界(明示)**: ①chain_heads アンカーは同一 SQLite 内にあるため、
「イベントとアンカーの両方を整合させて改竄する」攻撃は検知できない。本番では
アンカー(件数+末尾ハッシュ)を外部ストレージ/署名へ退避する(旧版DBの
未アンカー連鎖は改竄扱いせず、検証時にアンカーを初期化する)。
②C-5 の taint 検査(`gate.check_untainted`)は「特権操作(シェル・外部送信等)」に
untrusted 値を渡す時の門番だが、**PoC には特権操作が存在しない**ため呼び出し箇所も
ない(APIとテストのみ)。特権操作を導入する変更は、必ずこの gate を経由すること。
③**Web 収集の as_of は取得日**であり記事の発行日ではない。一次経路(Web)では
「新鮮」の保証が「最近取得した」に弱まる — 台帳にその旨を明記して射影する。
本番では本文からの発行日抽出を追加する。
④Case.phase(T/N/DD)と Source.kind=filing、premium チャネルの収集は v2 では
**未接続**(型と設定の受け口のみ)。業界名での起動は動くが、社名前提の項目まで
クエリされる — フェーズTの意味論は未実装。

## 5. 変更管理

- templates/ は定義ファイル。業態追加はコード変更なし
- 本書・EVALUATION.md の変更は人間が承認(P13)

---

# 第II部: 探索層の契約(v3。L4 知識構造+L5 争点集中型探索)

> 出典: research/arch/07(アーキテクチャ確定版)・08(優越証明 v1.0 —
> 特に §1.1 信号設計・M-7 順序規則・§5.5 実装引き継ぎ5点)。

## 6. 設計原理(追加)

| # | 原理 | 帰結 |
|---|---|---|
| R-2 | **争点集中**: 定型項目は分岐せず並列充足。木を開くのは争点(ACH未決/未解消矛盾/予想外の発見)のみ | 深さの単価を1桁下げる。全面木探索はしない |
| R-3 | **信号の用途分離**: 配分用プロキシ(使い捨てスカラー)は**枝への予算配分のみ**。最終判定・停止・品質は台帳のカウント量+明文の順序規則 | プロキシが腐っても判定は汚染されない(健全性)。完全性の劣化は未充足/leadsとして可視化 |
| R-4 | **検証ゲートは台帳昇格のみを制約し、示唆を捨てない**: 未検証の重要示唆は Lead として保存・出力・トリアージ | 「検証できないが決定的な気配」の黙殺(FM-16)を防ぐ |
| R-5 | **視点はテンプレが配るが、テンプレの外も1回見る**: devil's advocate(テンプレ制約なしの死因探索)を争点フェーズで必ず1回転 | テンプレ盲点(FM-9残存)の軽減 |

## 7. データ契約(追加。`prism/contracts.py` が唯一の定義)

```
Hypothesis   { id, case_id, segment?, driver, kind(story|rival|advocate), text,
               status(open|supported|refuted|contested), scrutiny_count }
               ← scrutiny_count: 反証パス通過回数。順序規則の検分下限に使う
EvidenceLink { id, case_id, hypothesis_id, evidence_id, relation(supports|refutes) }
               ← neutral は保存しない。判定は verifier(別ベンダ)の関係判定のみ(P10)
Contention   { id, case_id, driver, kind(ach|contradiction|surprise),
               status(open|resolved), moves_spent, zero_streak }
Lead         { id, case_id, item_key?, driver?, text, source_url?,
               rank, status(open|escalated|dismissed) }   ← 削除APIは存在しない
Judgment.status に第4値 seller_claimed を追加:
  売り手データしか原理的に存在しない項目。移管先(qoe|mgmt|vdr)を必須で持ち、
  停止判定(R4)の分母から外れる(I3 の恒久未充足による停止不全の防止)
```

## 8. 主要関数の契約(追加)

| 関数 | 事前条件 | 事後条件 |
|---|---|---|
| `ach.seed(case, archetype)` | テンプレに hypotheses 節 | story/rival を実体化(P3)。advocate はここでは作らない |
| `ach.link(llm, hyps, ev)` | **ev.grounded == "pass" のみ**(それ以外を渡すのは契約違反) | supports/refutes 辺。verifier ロール・JSON検証・失敗は [](C-7) |
| `ach.judge(h, links, evs)` | **純関数** | 独立クラスタで計数(I9)。supported = 独立2クラスタ以上の支持+反証0。supports≥1 かつ refutes≥1 → contested。**seller単独クラスタは supported に寄与しない(I3)** |
| `contention.detect(hyps, contradictions, surprises, trust)` | **純関数** | 争点列: ①story/rival とも未決の driver ②未解消矛盾 ③予想外の発見。**低信頼源のみに由来する矛盾は自動昇格せず Lead 化**(偽矛盾DoS対策 D-4) |
| `explore.allocate(arms, history, c_max=2, k=3)` | **純関数** | Thompson(Beta, Jeffreys 0.5/0.5)。観測 = `min(1, progress/c_max)`。**直近 k 手が全ゼロなら EIG 順の決定的選択に退避**(疎性フォールバック)。返すのは選択のみ |
| `explore.step(...)` | 争点が open | 一手 = 反証課題の遂行(反証クエリ生成→収集→検証→リンク→judge)。**深掘りの継続は、直前の一手が grounded=pass の証拠を生んだ場合のみ**(展開ゲート) |
| `advocate.run(llm, case, evidences)` | 争点フェーズで1回 | テンプレ制約なしの死因仮説(kind=advocate)を ACH に追加。**既存仮説の言い換えは新規性チェックで弾く** |
| `leads.triage(leads, k, cap)` | **純関数** | rank 順に上位 k 件を escalated(ラウンド上限 cap まで)。残りは open のまま記録。**dismissed も削除しない** |
| `pipeline.run`(v3) | — | **フェーズ制**: 幅フェーズ(v2ループ)は収穫逓減まで → 争点フェーズ(残予算を争点に EIG 順配分+advocate 1回転)→ 停止(理由必須)。**幅フェーズ中に争点を検出したら取得系クエリのみ即時実行してスナップショット**(分析は繰延 — 消える証拠の保全) |
| 順序規則(仮説の最終序列。純関数) | — | ①適格条件 = scrutiny_count ≥ 1(検分下限) ②支持クラスタ数 → 反証生存数 → 未解消矛盾の少なさ ③タイブレーク = 高信頼源比率 ④同順位は人間へ |

## 9. 不変条件 → テスト(追加)

| 不変条件 | テスト |
|---|---|
| ach.link は grounded=pass 以外を拒否 | unit/test_ach |
| ach.judge: 同一クラスタ1票(I9)・seller単独は supported に寄与しない(I3) | unit/test_ach |
| 低信頼源のみの矛盾は争点に自動昇格しない | unit/test_contention |
| allocate: 全ゼロ k 手で決定的選択に退避 | unit/test_explore |
| 展開ゲート: pass 証拠なしで深掘りが継続しない | unit/test_explore |
| leads: 削除APIなし・昇格は k/cap を超えない | unit/test_leads |
| seller_claimed は移管先必須+R4 分母から除外 | unit/test_audit(v3追加分) |
| advocate の新規性チェックが言い換えを弾く | unit/test_advocate |
| 順序規則: 検分下限未満は序列に載らない | unit/test_ach(順序) |
| E2E: 幅→争点→停止のフェーズ制が Fake 一式で完走し、ACH行列・気配リストが出力される | integration/test_explore_e2e |
| 争点ゼロのケースでは木を一切開かない | integration/test_explore_e2e |
