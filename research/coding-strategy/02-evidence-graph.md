---
doc_id: cs-evidence-graph
title: "★中心データモデル — 証拠グラフ"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: strategy
language: ja
tags: [data-model, evidence-graph, provenance, schema, append-only, retrievability, negative-status]
depends_on: [t-provenance, t-citation-attribution, t-point-in-time, t-agent-security, disc-integrated-v2]
---

# 証拠グラフ（Evidence Graph）

> **これが Integral Prism の全てである。**
> **最初に作るのはこれであり、他の全ては、この上に生える。**

## 1. なぜこれが中心なのか

**1つの構造が、独立した5つの要求を同時に満たすから** `[S-128]`。

| 要求 | どう満たされるか |
|---|---|
| **引用の機械検証**（L1） | `Claim --supports--> Evidence --from--> Source` を辿って原文照合 |
| **規制の監査証跡**（L7, P12） | 追記専用＋ハッシュ連鎖＋署名記録（EU AI Act Art.12/13, FINRA） |
| **セキュリティの taint 追跡**（P18） | `trust_label` を辺に沿って伝播（CaMeL の capability と同型）`[S-127]` |
| **時点再現 / リーク防止**（評価A） | 全ノードの `as_of` で「T 時点の部分グラフ」を切り出せる `[S-133]` |
| **文脈圧縮しても壊れない**（P8） | 文脈には ID だけ載せ、本体はグラフに置く |

> **逆に言えば**: これを作らずに個別機能を作ると、上の5つを**別々の仕組みで5回作る**ことになる。
> それが「薄いシステム」になる典型的な失敗経路である。

## 2. ノード型 🔒

```
Source        情報源そのもの
  { id, kind(filing|contract|web|interview|internal|vendor), url|path,
    publisher, trust_tier(1..5), license_terms, retrieved_at, content_hash,
    snapshot_uri, as_of }              ← as_of = 公に入手可能になった時点

Evidence      Source 内の特定の位置にある事実
  { id, source_id, locator(page/bbox/xpath/cell/char_range), text,
    extracted_value: value|NOT_FOUND|AMBIGUOUS,   ← P19
    extraction_confidence, trust_label(trusted|untrusted|derived),  ← P18
    valid_from, valid_until, supersedes(evidence_id?),  ← 修正再表示の追跡
    negative_status(supported_negative|unknown|not_searched),  ← P21（v2.0）
    independence_cluster_id }  ← 上流ソース単位のクラスタ。同一プレスリリース由来の
                                  複数記事を「独立した証拠」と誤算しないための正規化キー（P22, O2 の暫定解）

Hypothesis    仮説（ACH の列）
  { id, text, origin(human|template|case_memory|agent), status(open|supported|refuted),
    prior, posterior, created_at }

Claim         レポートに出る主張
  { id, text, hypothesis_ids[], probability, probability_method,
    verified_status(pass|fail|partial|unverified), model_version, as_of }

Question      未解決の問い（＝反証課題）
  { id, text, targets_hypothesis_ids[], eig_estimate, cost_estimate,
    channel(web|db|expert|human|calc), retrievability_estimate,  ← P21（v2.0）
    status, diagnosticity }
    ★ retrievability_estimate が低いと判定された時点で、channel を
      web から vdr/expert/compute へ切り替える（Action Router, → 17章）

ToolCall      ツール実行の記録
  { id, tool, args_hash, cost, latency, inputs_evidence_ids[], outputs[] }

Decision      意思決定ノード
  { id, question, options[], chosen, rationale_claim_ids[],
    human_signature, signed_at }        ← FINRA の署名要件 `[S-118]`

CaseMemory    過去案件から持ち込んだケース
  { id, archetype, source_deal_id, lesson, expiry }
```

## 3. 辺（関係）🔒

```
supports          Evidence → Hypothesis   （尤度ラベル: 強/弱/中立）
refutes           Evidence → Hypothesis
contradicts       Evidence ↔ Evidence     ★平均も抑制もせず、辺として保存する（P20）
derived_from      Evidence → Evidence     （引用の連鎖 → 一次情報への正規化）
cites             Claim → Evidence
answers           Evidence → Question
verified_by       Claim → ToolCall        （検証の実行記録）
tainted_by        * → Source              （未信頼由来の伝播, P18）
superseded_by     Evidence → Evidence     （修正再表示）
approved_by       * → HumanAction
recalled_from     Hypothesis → CaseMemory
```

## 4. 不変条件（テストで守る）🔒

| # | 不変条件 | 破れたときの意味 |
|---|---|---|
| I1 | **全ての Claim は 1つ以上の Evidence を cites する** | 根拠のない主張が出た |
| I2 | **全ての Evidence は Source と locator を持つ** | 原文に戻れない＝検証不能 |
| I3 | **`as_of > cutoff` の Evidence は、評価モードで到達不能** | リーク（評価が無効になる） |
| I4 | **`trust_label=untrusted` から派生した値は、特権ツールの引数にできない** | インジェクション経路（P18） |
| I5 | **数値を含む Claim は、必ず ToolCall（計算）に verified_by で紐づく** | LLM が計算した（P19 違反） |
| I6 | **グラフは追記専用**。訂正は新ノード＋`superseded_by` | 監査証跡の破壊（P12） |
| I7 | **contradicts 辺は解消されるまで消えない** | 矛盾の握り潰し（P20） |

> **これらは「設計指針」ではなく、CI で落とすテストにする。**（→ [07-quality-gates.md](07-quality-gates.md)）

## 5. 物理設計 🔧

```
イベントストア（追記専用・ハッシュ連鎖）      ← 唯一の真実。全変更はイベント
      │  リプレイ
      ├─▶ グラフのマテリアライズドビュー（クエリ用）
      ├─▶ 全文/ベクタ索引（局所検索）
      └─▶ コミュニティ要約（大域センスメイキング、案件単位で構築）`[S-047]`

原文スナップショット: オブジェクトストレージ（ハッシュをキーに）
案件ごとに物理分離（MNPI / Chinese Wall）`[S-079]`
```

**推奨の初期実装** 🔧: PostgreSQL 単体で始める。
- イベント: 追記専用テーブル ＋ 前レコードのハッシュを含む連鎖
- グラフ: 隣接テーブル（再帰CTEで十分。専用グラフDBは早すぎる）
- ベクタ: pgvector
- **専用グラフDB / KGプラットフォームは、規模が問題になってから**

## 6. 何を最初に書くか

```
1. スキーマ定義（型 + 不変条件）とマイグレーション
2. イベントストアとリプレイ
3. Evidence 取り込み（1ソース種別だけ: まずは PDF or EDINET）
4. 不変条件テスト I1–I7
5. 最小の射影: 「主張一覧 + 出典リンク」を出すだけの view
```

**この5つが動いたら、M1 の骨は通っている。** 探索も生成もまだ要らない。
