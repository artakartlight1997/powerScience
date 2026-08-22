# CONTRACTS — モジュール契約（実装より先に固定する「こうあるべき論」）

> **本書が正。実装が本書と食い違ったら実装のバグである。**
> 変更は本書を先に改訂し（人間承認）、その後にコードを追従させる。

## 0. 設計原理（バグを構造的に減らすための約束）

| # | 原理 | 帰結 |
|---|---|---|
| C-1 | **モジュールは Protocol（インタフェース）にのみ依存する** | LLM・コレクタは差し替え可能。テストは Fake 実装で回る |
| C-2 | **判定ロジック（audit / fill / stop）は純関数**。I/O も LLM も呼ばない | 決定論的・ユニットテスト容易・リプレイ可能 |
| C-3 | **LLM の出力は必ず JSON で受け、pydantic で検証**。失敗は1回だけ再試行、それでも失敗なら**その項目を落とす**（推測で埋めない） | 「流暢な壊れた出力」がシステムに入らない |
| C-4 | **全ての状態変更はイベント**（追記専用・ハッシュ連鎖）を経由する | 監査・改竄検知・リプレイ |
| C-5 | **外部との境界は gate を必ず通る**（ネットワーク・スナップショット外のファイル） | taint 検査・ホスト制限を一箇所で強制 |
| C-6 | **生成モデルと検証モデルは別ベンダ**。同一ベンダは設定エラーとして起動拒否（明示フラグで解除可） | 同一モデルの盲点共有を防ぐ（P5） |
| C-7 | エラーは**握りつぶさない**。項目単位で degrade し、ケース全体は落とさない | 部分失敗が全滅にならない |
| C-8 | **縮退は黙って起きない**: すべての degrade は WARNING としてログに残る。未処理例外はトレースバック込みで `data/logs/prism.log` に記録し、ユーザにはログの場所だけ伝える。**資料の本文・引用はログに書かない**(MNPI) | バグの所在をユーザに報告させない。ログ1ファイルで再現調査が足りる |

## 1. データ契約（`prism/contracts.py` の pydantic モデルが唯一の定義）

```
Case        { id, name, industry?, archetype, phase(T|N|DD), created_at }
SpecItem    { id, case_id, segment, box, key, label, must, retrievability{channel:low|mid|high},
              freshness_days, required_clusters, driver, dependence(high|mid|low) }
Source      { id, case_id, kind(seller|consultant|general|web|filing), trust_tier(1..5),
              seller_provided, path, url?, publisher?, as_of, content_hash, snapshot_dir }
Evidence    { id, case_id, source_id, item_key, quote, value?{raw,num?,unit?}, 
              status(value|NOT_FOUND|AMBIGUOUS), locator{page}, trust_label(trusted|untrusted),
              grounded(none|pass|partial|fail), cluster_id?, as_of }
Judgment    { id, case_id, item_id, status(filled|thin|missing|unknown), verified_clusters,
              contradiction_open, rationale, acquisition_path?, round }
Question    { id, case_id, item_key, text, channel(web|premium|vdr|expert|mgmt), rank, status }
Event       { id, case_id, kind, payload, actor, prev_hash, this_hash, created_at }
```

## 2. インタフェース契約（Protocol）

```python
class LLMClient(Protocol):
    def complete_json(self, role: Literal["generator","verifier","online"],
                      system: str, user: str) -> dict: ...
    # 例外: LLMError のみ。呼び出し側は項目単位で degrade する（C-7）

class Fetcher(Protocol):     # web ページ取得（online 証拠の原文スナップショット用）
    def fetch(self, url: str) -> str | None   # 失敗は None（例外にしない）
```

## 3. 主要関数の契約（事前・事後条件）

| 関数 | 事前条件 | 事後条件 |
|---|---|---|
| `ingest.scan(case)` | inbox/<case>/{seller,consultant,general}/ が存在 | 新規ファイルごとに Source＋snapshot（hash 済み）。**同一 hash は再取り込みしない**（冪等） |
| `extract.run(case, source)` | source に snapshot がある | Evidence[]。**値が読めない項目は出力しない**（NOT_FOUND は「探して無かった」時のみ） |
| `verify.ground(ev)` | ev.quote と原文 snapshot がある | grounded ∈ {pass, partial, fail}。**web で原文が取得できなかったものは pass にならない** |
| `verify.cluster(case)` | — | 同一項目・同一正規化値・高文面類似 → 同一 cluster_id（I9 の実装） |
| `verify.contradictions(case)` | — | 同一項目で数値が相対 tolerance 超乖離 → contradicts 辺。**削除・平均する API は存在しない**（P20） |
| `audit.judge(item, evs, contradiction)` | 純関数 | Judgment。**seller_provided のみの支持は filled 不可**（I3）。**unknown は acquisition_path 必須**（I8） |
| `fill.plan(items, judgments)` | 純関数 | gap の順位付き列。数値スコアは返さない（順位のみ） |
| `fill.should_stop(state)` | 純関数 | (bool, reason)。**reason なしの停止はない** |
| `pipeline.run(case)` | — | 各ラウンド末に必ず audit → イベント記録。停止理由を Case に保存 |

## 4. 不変条件 → テストの対応（CI で全て緑であること）

| 不変条件 | テスト |
|---|---|
| I1 filled/thin は evidence 参照を持つ | unit/test_audit |
| I3 seller 単独では filled 不可 | unit/test_audit |
| I6 イベントのハッシュ連鎖が検証可能・改竄検知 | unit/test_events |
| I8 unknown は acquisition_path を持つ | unit/test_audit |
| I9 同一クラスタは verified_clusters に1回 | unit/test_audit, unit/test_verify |
| C-5 スナップショット外の読み・未許可ホストを gate が拒否 | unit/test_gate |
| C-6 同一ベンダの生成/検証は起動拒否 | unit/test_gate |
| E2E: 取り込み→抽出→検証→監査→充填→射影が Fake LLM で通る | integration/test_pipeline |

## 5. 変更管理

- templates/（スペック・アーキタイプ・ツリー・ファンド標準）は**定義ファイル**。コード変更なしで追加できること
- 本書・EVALUATION.md の変更は PR で人間が承認（P13）
