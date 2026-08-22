# Integral Prism PoC

Biz DD の**カバレッジ監査ループ**の PoC。固定の物差し(箱0〜10 × 業態アーキタイプ)に
リサーチ結果を突き合わせ、filled / thin / missing / unknown を**証拠の密度**
(検証済み × 独立 × 新鮮)で機械判定し、作戦盤・発注仕様書・検収QC・証拠台帳へ射影する。

- 使い方 → [docs/MANUAL.md](docs/MANUAL.md)
- 設計契約(こうあるべき論。実装より優先) → [docs/CONTRACTS.md](docs/CONTRACTS.md)
- 評価軸(CIゲート・実LLM検収・実験E) → [docs/EVALUATION.md](docs/EVALUATION.md)
- 上位の設計仕様 → リポジトリの `research/arch/`

## 実行

```bash
cp .env.example .env && docker compose build
docker compose run --rm prism init-case case1 --name 対象会社 --archetype ses_jutaku
# inbox/case1/{seller,consultant,general}/ に資料を置く(YYYY-MM-DD_ プレフィクス)
docker compose run --rm prism run case1
```

テスト(LLM 不要。Fake で回る):

```bash
pip install -e ".[dev]" && pytest
```

## 各ファイルの役割

### prism/(本体。依存は Protocol のみ=疎結合)

| ファイル | 役割 | 純関数? | LLM |
|---|---|---|---|
| `contracts.py` | 全データ型(pydantic)と Protocol(`LLMClient`/`Fetcher`)、共有例外。**型定義はここだけ** | — | — |
| `config.py` | 環境変数 → `Config`。パス・ロール別モデル・タイムアウト | — | — |
| `log.py` | 飛行記録: `data/logs/prism.log`(ローテーション)。縮退は必ずWARNING、未処理例外はトレースバック込み。**資料本文は書かない**(MNPI) | — | — |
| `events.py` | 追記専用イベントログ(SHA256 ハッシュ連鎖)。`verify_chain` で改竄検知 | — | — |
| `store.py` | 状態ストア(SQLite)。**書き込みは必ずイベント併記**。最新判定などのビュー | — | — |
| `templates.py` | YAML(箱・アーキタイプ・ツリー・基準)を読み、ケースの SpecItem 列へ実体化 | — | — |
| `gate.py` | ポリシーゲート: ベンダ分離(C-6)・ホスト allowlist・パス逸脱・taint(P18) | — | — |
| `llm.py` | OpenRouter クライアント。JSON 強制+1回だけ再試行(C-3)。呼び出し回数を計数 | — | ○ |
| `ingest.py` | ドロップフォルダ走査 → Source+スナップショット。内容ハッシュで冪等。as_of 規約 | — | — |
| `extract.py` | 原文から逐語引用を抽出(generator)。**数値の解釈はコードのみ**(P19) | — | ○ |
| `verify.py` | grounding(逐語一致→二値判定×提示順入替)・独立性クラスタ(P22)・矛盾検出(P20) | 一部 | ○(verifier) |
| `audit.py` | カバレッジ判定 filled/thin/missing/unknown。**純関数** | ○ | — |
| `fill.py` | gap の順位付け・問いの生成・停止判定(必ず理由つき)。**純関数** | ○ | — |
| `collectors.py` | オンライン収集(online ロールで URL 候補→gate→取得→必ずスナップショット) | — | ○ |
| `project.py` | 射影のみ(判定しない): 作戦盤・発注仕様書・検収QC・証拠台帳・状況 | ○ | — |
| `pipeline.py` | ループ本体: 取り込み→抽出→検証→監査→充填→(収集)→射影 | — | — |
| `cli.py` | CLI(init-case / run / report / status / verify-chain) | — | — |

### templates/(定義ファイル。コード変更なしで拡張)

| ファイル | 役割 |
|---|---|
| `boxes.yaml` | 第1層: 箱0〜10 の業態非依存の問い(固定の物差し) |
| `archetypes/ses_jutaku.yaml` | 第2層: SES×受託の業態固有項目・セグメント定義(校正済み第1号) |
| `drivers/utilization.yaml` | 稼働率型の EBITDA ドライバーツリーと見張り初期値 |
| `drivers/order.yaml` | 受注型の同上 |
| `fund/standards.yaml` | 判定基準(独立クラスタ数・鮮度)・信頼層・停止則・オンライン制限。**変更は承認制** |

### tests/

| 場所 | 内容 |
|---|---|
| `unit/` | 不変条件のテスト(I1/I3/I6/I8/I9、C-5/C-6、P10/P15/P18/P19/P20/P22 に対応) |
| `integration/` | FakeLLM での E2E: 売り手95% vs 外部80% の矛盾が保存され filled を阻止するシナリオ |
| `fixtures/` | 上記シナリオの資料(txt) |

### 実行基盤

| ファイル | 役割 |
|---|---|
| `Dockerfile` / `docker-compose.yml` | コンテナ実行。inbox/data/out を volume 化 |
| `.env.example` | 必要な環境変数の見本(OpenRouter キー、ロール別モデル) |
| `pyproject.toml` / `requirements.txt` | パッケージ定義(`prism` コマンド)と依存 |

## 設計上の勘所(詳細は CONTRACTS.md)

1. **判定は純関数**(audit/fill) — LLM も I/O も呼ばない。だから決定論的にテストできる
2. **LLM は Protocol 越し** — テストは FakeLLM、実行は OpenRouter。生成と検証は別ベンダ強制
3. **全状態変更はイベント**(追記専用+ハッシュ連鎖) — `verify-chain` でいつでも改竄検知
4. **矛盾は消えない** — 削除・平均する API が存在しない
5. **レポートは view** — 台帳が一次データで、Markdown は何度でも再生成できる
