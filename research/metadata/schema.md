---
doc_id: metadata-schema
title: "メタデータ・スキーマ定義"
version: 0.1.0
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: schema
language: ja
---

# メタデータ・スキーマ

後工程（設計文書生成・引用の自動検証・進捗管理・RAG 索引化）で機械的に使うための定義。

## 1. 文書フロントマター（すべての .md）

```yaml
doc_id: string          # 一意。ファイル名と対応させる（survey-07-verification など）
title: string
version: semver         # 0.1.0 から
status: draft|review|stable|open
created: YYYY-MM-DD
updated: YYYY-MM-DD
project: integral-prism
doc_type: index|survey|synthesis|agenda|worklist|schema|glossary
language: ja|en
tags: [string]
confidence: high|medium-high|medium|low   # 文書全体の確度（任意）
primary_sources: [S-xxx]                  # 主要出典 ID（任意）
depends_on: [doc_id]                      # 依存文書（任意）
contributes_to: [string]                  # どの設計論点に効くか（任意）
owner: email                              # 任意
```

## 2. sources.json（出典レジストリ）  {#sources}

```jsonc
{
  "id": "S-001",                  // 一意。本文からは `[S-001]` で参照
  "title": "string",
  "url": "string",
  "type": "official|paper|press|industry|blog|code|interview",
  "org": "string",
  "year": 2026,
  "lang": "ja|en",
  "confidence": "A|B|C|D",        // 00-method-and-scope.md の確度スケール
  "topics": ["string"],
  "used_in": ["doc_id"],
  "key_numbers": { "任意のキー": "値" }   // 任意。重要数値のキャッシュ
}
```

**規約**
- ID は再利用しない（削除しても欠番のままにする）
- 一次ソース本文を後で取得したら `confidence` を上げ、`retrieved_full: true` を追加する

## 3. claims.json（事実主張）  {#claims}

```jsonc
{
  "id": "C-014",
  "claim": "string",              // 一文で述べた事実主張
  "value": "string|number",       // 中心となる数値・値
  "sources": ["S-057"],
  "confidence": "A|B|C|D",
  "topic": "string",
  "impact": "string",             // 任意。設計上の意味
  "verify_by": "string"           // 任意。再検証の手順
}
```

**用途**: ①設計判断の根拠追跡 ②一次確認の宿題管理 ③将来的な自動再検証（URL を開いて主張が生きているか確認）

## 4. taxonomy.json（分類軸）  {#taxonomy}

- `layers`: L0〜L7 の機能層。各層に競合カバレッジと IP の優先度を持つ
- `axes`: 設計選択の軸（workflow / agent_composition / reward / … ）
- `design_principles`: P1〜P12。各原則は出典 ID を持つ
- `tags`: 横断タグ

## 5. 命名規約

| 種別 | 形式 | 例 |
|---|---|---|
| サーベイ文書 | `NN-kebab-case.md` | `07-verification-attribution-calibration.md` |
| 出典 ID | `S-NNN` | `S-057` |
| 主張 ID | `C-NNN` | `C-015` |
| 設計原則 | `P-N` / `PN` | `P6` |
| 機能層 | `LN` | `L3` |
| 議論論点 | `D-N` / `DN` | `D2` |
| 未解決 | `Q-N` / `QN` | `Q3` |

## 6. 整合性チェック（推奨 CI）

1. 本文中の `S-xxx` が全て `sources.json` に存在する
2. `sources.json` の `used_in` が実ファイルと一致する
3. `claims.json` の `sources` が全て存在する
4. `confidence: C|D` の主張が、設計決定文書から参照されていない
5. 各 md のフロントマターが必須キーを持つ
