---
doc_id: arch-data-model
title: "設計仕様 01 — データモデル"
version: 1.0.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: architecture
language: ja
tags: [data-model, schema, postgres, append-only]
depends_on: [cs-evidence-graph, cs-bizdd-spec]
---

# 01. データモデル

**PostgreSQL 単体で始める**（グラフDBは規模が問題になってから）。
唯一の真実は追記専用の `events`。他は全てそこから導出できる状態とする（リプレイ可能）。

## 1. テンプレート（コードではなく定義ファイル）

人間の承認を経て版管理する（P13）。**コード変更なしで追加・修正できること**。

```
templates/
  spec/boxes.yaml            # 第1層: 箱0〜10（業態非依存の問い）
  spec/archetypes/           # 第2層: 業態アーキタイプが項目を差し込む
    ses_jutaku.yaml          #   校正済み第1号: ITサービス（SES×受託）
    saas.yaml / manufacturing.yaml / ...
  drivers/                   # 収益方程式の型別ドライバーツリー
    utilization.yaml         #   稼働率型: キャパ×稼働率×単価
    stock.yaml / order.yaml / unit_price.yaml / ...
  fund/standards.yaml        # ファンド標準（一度だけ設定: IRRハードル・許容集中度・鮮度窓）
```

アーキタイプ定義の形（例: `ses_jutaku.yaml` の断片）:
```yaml
archetype: ses            # 稼働率型
revenue_equation: headcount * utilization * rate
items:
  - box: 2                # 箱2（顧客/数量の源泉）に差し込む
    key: engineer_headcount
    label: エンジニア数（正社員/BP比率）
    must: true
    retrievability: {public: low, premium: mid, vdr: high}
    driver: headcount
    freshness_days: 365
  - box: 4
    key: flow_depth
    label: 商流の深さ（何次請けか）
    must: true
    retrievability: {public: low, expert: high}
    driver: rate_ceiling
risk_items:               # 型の定番の死因
  - key: instant_termination_clause
    label: 契約の即時解約条項
```

## 2. コアテーブル

```sql
-- 追記専用イベントログ（唯一の真実。ハッシュ連鎖で改竄検知）
events(
  id BIGSERIAL PK, case_id, kind, payload JSONB,
  actor TEXT,             -- system|model:<id>|human:<name>
  created_at, prev_hash BYTEA, this_hash BYTEA)   -- this_hash = H(prev_hash || payload)

cases(
  id, name,                    -- 社名 or 業界名（起動入力はこれだけ）
  phase TEXT,                  -- T(teaser) | N(named) | DD
  fund_standards_version, created_at)

segments(                      -- 箱0の結果。1社=複数アーキタイプの混合
  id, case_id, label,          -- 例: "SES事業", "受託開発事業"
  archetype TEXT,              -- ses | order | stock | ...
  revenue_share NUMERIC NULL,  -- 不明なら NULL（unknown は正常）
  identified_from evidence_id[])

spec_items(                    -- 実体化されたスペック（テンプレ×セグメントの積）
  id, case_id, segment_id NULL, box INT, key, label,
  must BOOL, retrievability_prior JSONB, driver_node_id NULL,
  template_version)

driver_nodes(
  id, case_id, segment_id, key, label, parent_id NULL,
  thesis_dependence TEXT NULL,  -- high|mid|low（IM入手後に売り手ストーリーから自動推定）
  threat_flags JSONB)

sources(
  id, case_id, kind,            -- filing|premium_db|web|news|jobs|im|consultant_report|expert|vdr
  trust_tier INT,               -- 1(一次)..5(三次)
  seller_provided BOOL,         -- ★IM・売り手資料は true（「主張」として扱う）
  url_or_path, publisher, retrieved_at, as_of DATE,   -- as_of=公に入手可能になった時点
  content_hash, snapshot_uri, license_note)

evidences(
  id, case_id, source_id, locator JSONB,   -- page/bbox/xpath/cell
  text, extracted_value JSONB,             -- {value}|{status:NOT_FOUND}|{status:AMBIGUOUS}
  extraction_confidence, trust_label,      -- trusted|untrusted|derived（taint, P18）
  negative_status TEXT NULL,               -- supported_negative|unknown|not_searched（P21）
  independence_cluster_id,                 -- 同一上流ソースの縮約キー（P22）
  valid_from, valid_until, supersedes_id NULL)

edges(                          -- supports|refutes|contradicts|derived_from|answers|verified_by
  id, case_id, kind, src_id, src_type, dst_id, dst_type,
  strength TEXT NULL)           -- 強/弱/中立（supports/refutes のみ）

coverage_judgments(             -- ★監査の中心成果物。判定は毎回作り直す（最新が有効）
  id, case_id, spec_item_id,
  status TEXT,                  -- filled|thin|missing|unknown
  verified_count INT, independent_clusters INT, freshest_as_of DATE,
  contradiction_open BOOL,
  rationale JSONB,              -- 閾値との比較内訳（説明可能に）
  acquisition_path TEXT NULL,   -- unknown のとき必須: vdr_request|expert_q|mgmt_q|premium|calc
  judged_at, judge_model)

questions(                      -- 反証課題・充填課題（発注仕様書とウォッチリストの源）
  id, case_id, spec_item_id NULL, driver_node_id NULL, text,
  channel TEXT,                 -- web|premium|vdr|expert|mgmt|calc
  priority_rank INT,            -- ★順位のみ。疑似的な精密確率を持たない
  cost_estimate_band TEXT,      -- 無料|〜10万|〜50万|それ以上
  status TEXT)                  -- open|answered|abandoned

tool_calls(id, case_id, tool, args_hash, cost_yen, latency_ms, output_ref)
human_actions(id, case_id, kind, payload, actor, at)   -- 型差替え・耳打ち・承認（任意入力）
```

## 3. 不変条件（CI テスト。設計指針ではない）

| # | 条件 | 検査 |
|---|---|---|
| I1 | filled/thin の judgment は 1件以上の evidence 参照を持つ | SQL |
| I2 | 全 evidence は source と locator を持ち、原文へ到達できる | SQL+snapshot存在 |
| I3 | `seller_provided=true` の source 由来の evidence 単独では filled にできない（外部突合が必須） | SQL |
| I4 | `trust_label=untrusted` 由来の値は特権ツール引数に到達しない | 実行時ゲート |
| I5 | 数値を含む出力は verified_by→tool_call(calc) を持つ | SQL |
| I6 | events のハッシュ連鎖が検証可能 | ジョブ |
| I7 | contradicts 辺は解消イベントなしに消えない | SQL |
| I8 | status=unknown の judgment は acquisition_path を必ず持つ | SQL |
| I9 | 同一 independence_cluster の evidence は verified_count に1回しか数えない | 監査ロジックのテスト |
| I10 | 評価モードでは as_of > cutoff の evidence に到達不能（インデックス分離） | 統合テスト |
