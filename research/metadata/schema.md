---
doc_id: metadata-schema
title: "メタデータ・スキーマ定義"
version: 0.2.0
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

## 5. ディレクトリ構造（v0.2.0）

```
research/
  README.md                 索引
  method-and-scope.md       調査方法・確度スケール（最初に読む）
  topics/
    01-competitors/         競合（13ファイル）
    02-methods/             手法（14ファイル）
    03-evaluation/          評価（6ファイル）
    04-domain/              ドメイン（4ファイル）
    05-strategy/            戦略（3ファイル）
    06-synthesis/           統合（3ファイル）
  notes/                    未決論点・宿題
  metadata/                 スキーマ・索引・出典・主張・分類・用語
```

**分割方針**: 1ファイル = 1トピック。
「あるトピックについて知りたい人が、そのファイルだけ読めば足りる」ことを基準にする。
そのため**トピック間で事実の重複記述を許す**（ただし出典 ID は共通）。
横断的な統合は `topics/06-synthesis/` に置き、個別トピックからは相互リンクで到達させる。

## 6. 命名規約

| 種別 | 形式 | 例 |
|---|---|---|
| トピック文書 | `kebab-case.md`（トピック群ディレクトリ配下） | `topics/02-methods/verifier-design.md` |
| doc_id | `t-<topic-slug>` | `t-verifier-design` |
| 出典 ID | `S-NNN` | `S-057` |
| 主張 ID | `C-NNN` | `C-015` |
| 設計原則 | `P-N` / `PN` | `P6` |
| 機能層 | `LN` | `L3` |
| 議論論点 | `D-N` / `DN` | `D2` |
| 未解決 | `Q-N` / `QN` | `Q3` |

## 7. index.json（ファイル索引）  {#index}

```jsonc
{
  "doc_id": "t-verifier-design",
  "path": "topics/02-methods/verifier-design.md",
  "title": "検証器の設計 — ...",
  "topic_group": "competitors|methods|evaluation|domain|strategy|synthesis|meta|notes",
  "tags": ["..."],
  "confidence": "high|medium-high|medium|low",
  "primary_sources": ["S-036"],
  "related_topics": ["t-citation-attribution"],
  "lines": 78
}
```

生成は機械的に行う（フロントマターから抽出）。手で編集しない。

## 8. 整合性チェック（推奨 CI）

1. 本文中の `S-xxx` が全て `sources.json` に存在する
2. `sources.json` の `used_in` が実ファイルと一致する（**自動再生成**する）
3. `claims.json` の `sources` が全て存在する
4. `confidence: C|D` の主張が、設計決定文書から参照されていない
5. 各 md のフロントマターが必須キーを持つ
6. **相対リンクが全て解決する**（トピック間リンク）
7. `index.json` が実ファイル一覧と一致する
8. **used_in が空の出典が存在しない**（孤立出典の検出）
