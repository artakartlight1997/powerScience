# Integral Prism PoC v2

**社名を入れると、システムが自分で調べに行く**リサーチシステム(Deep Research の代替+検証・監査)。
外部収集ループ(計画→検索→取得→スナップショット)が一次経路で、
固定の物差し(箱0〜10×業態アーキタイプ)へのカバレッジ監査で
filled / thin / missing / unknown を**証拠の密度**(検証済み×独立×新鮮)で機械判定し、
作戦盤・発注仕様書・検収QC・証拠台帳へ射影する。

> **poc(v1)との関係**: v1 は台帳・監査・検証エンジンは同じだが、資料ドロップを
> 一次入力にしてしまっていた(R-0 違反)。v2 は「社名だけで起動、Web収集が既定」に
> 是正したもの。v1 は参照用に残置。

- 使い方 → [docs/MANUAL.md](docs/MANUAL.md)
- 設計契約(こうあるべき論。実装より優先) → [docs/CONTRACTS.md](docs/CONTRACTS.md)
- 評価軸 → [docs/EVALUATION.md](docs/EVALUATION.md)
- 上位の設計仕様 → リポジトリの `research/arch/`

## 実行

```bash
cp .env.example .env && docker compose build
docker compose run --rm prism research "株式会社サンプルテック" --industry ITサービス
```

テスト(LLM/ネットワーク不要。全部 Fake で回る):

```bash
pip install -e ".[dev]" && pytest
```

## 各ファイルの役割

### prism/(本体。依存は Protocol のみ=疎結合)

| ファイル | 役割 | 純関数? | 外部I/O |
|---|---|---|---|
| `contracts.py` | 全データ型(pydantic)と Protocol(`LLMClient`/`SearchClient`/`Fetcher`)、共有例外。**型定義はここだけ** | — | — |
| `config.py` | 環境変数 → `Config`(パス・ロール別モデル) | — | — |
| `log.py` | 飛行記録: `data/logs/prism.log`。縮退は必ずWARNING、未処理例外はトレースバック込み。資料本文は書かない | — | — |
| `events.py` | 追記専用イベントログ(SHA256連鎖)。`verify_chain` で改竄検知 | — | DB |
| `store.py` | 状態ストア(SQLite)。書き込みは必ずイベント併記 | — | DB |
| `templates.py` | YAML → ケースの SpecItem 列へ実体化。`list_archetypes` | — | FS |
| `gate.py` | ポリシーゲート: ベンダ分離・ホストallowlist・パス逸脱・taint | — | — |
| `llm.py` | OpenRouter クライアント。JSON強制+1回だけ再試行 | — | HTTP |
| **`identify.py`** | **社名/業界 → アーキタイプ自動同定**(選択肢外は受理せず人間へ) | — | LLM |
| **`research.py`** | **収集ループの中核**: `build_queries`(gap→クエリ、純関数)と `collect`(検索→取得→必ずスナップショット)。`HttpxFetcher` | 一部 | HTTP |
| **`search.py`** | `SearchClient` 実装(OpenRouter online ロールで URL 候補)。実検索APIへの差し替えは1クラス | — | LLM |
| `ingest.py` | (任意の補助)ドロップフォルダ取込。冪等・as_of 規約 | — | FS |
| `extract.py` | 原文から逐語引用を抽出。**数値の解釈はコードのみ**(P19) | — | LLM |
| `verify.py` | grounding(逐語一致→二値判定×提示順入替)・独立性クラスタ(P22)・矛盾検出(P20) | 一部 | LLM |
| `audit.py` | カバレッジ判定 filled/thin/missing/unknown。**純関数** | ○ | — |
| `fill.py` | gap順位付け・問い生成・停止判定(理由必須)。**純関数** | ○ | — |
| `project.py` | 射影のみ(判定しない): 作戦盤・発注仕様書・検収QC・台帳・状況 | ○ | FS |
| `pipeline.py` | `start_case`(社名だけで開始)+ ループ本体 | — | — |
| `cli.py` | CLI(**research** / run / report / status / verify-chain) | — | — |

### templates/ — v1 と同一の物差し + `research` パラメータ(standards.yaml)

### tests/

| 場所 | 内容 |
|---|---|
| `unit/` | v1の不変条件テスト全部 + **test_research**(クエリ計画の純関数性・死んだURLから何も生まれない・gate遵守)+ **test_identify**(選択肢外の拒否) |
| `integration/` | **ゼロ入力E2E**: 社名だけ→自動同定→Web収集→矛盾保存→射影。IM後置きで I3 維持 |

### 実行基盤 — Dockerfile / docker-compose.yml / .env.example / pyproject.toml
