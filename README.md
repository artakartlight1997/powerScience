# Power BI Mastery

Power BI を **初級 → 中級 → 上級 → プロ** の4段階で学び、
**PL-300（Microsoft Power BI Data Analyst）合格**と**現場で通用する実力**の両方に届くための学習サイトです。

**公開サイト → https://artakartlight1997.github.io/powerScience/**
（URLは大文字小文字を区別します。`powerScience` の `S` は大文字です）

GitHub Pages で公開でき、スマートフォンからも学習できます。
閲覧統計（どの地域の人が、いつ、どのページを見たか）は、一般には見えない管理画面で確認できます。
管理画面のパスワードはあなた自身が設定します。

---

## このサイトの中身

| 区分 | 内容 |
|---|---|
| ティア | 4段階（初級 / 中級 / 上級 / プロ） |
| モジュール | 22 |
| レッスン | 118 |
| 図解 | 本文 1,842枚 + 用語集 162枚（すべて自前のSVG/HTML。**Mermaidは使っていません**） |
| 操作できる図解 | 10種類（フィルターコンテキスト体験、結合ラボ、RLSシミュレータほか） |
| ハンズオンラボ | 12（サンプルデータ同梱） |
| 演習問題 | レッスン別クイズ + PL-300 模擬試験バンク |
| 用語集 | 796語。検索・索引つき。本文中の用語から自動でリンク |
| 統計・DS用語 | 162語に「かんたんに言うと」（たとえ話）と図解つき |
| サイト内検索 | Ctrl/⌘ + K。レッスン・見出し・ハンズオン・用語を横断検索 |
| 想定学習時間 | 約230時間 |

### 4つのティア

| ティア | 到達点 | モジュール |
|---|---|---|
| **初級** Beginner | BIの考え方を理解し、自分でレポートを1枚作れる | データ分析とBIの基礎 / Power BIの全体像 / はじめてのレポート / データの読み込み入門 |
| **中級** Intermediate | 実務データを整形し正しいモデルを組み、必要な指標をDAXで書ける | Power Query実践 / データモデリング / DAX基礎 / DAXコンテキスト / 可視化の設計 / 共有と運用 |
| **上級** Advanced | 性能・複雑要件・組織展開を扱え、PL-300に合格できる | 高度なデータ整形 / 高度なモデリング / DAX上級 / パフォーマンス / 分析手法とデータサイエンス / PL-300完全対策 |
| **プロ** Professional | 設計をリードし、データから事業価値を出せる | エンタープライズ アーキテクチャ / ガバナンスとライフサイクル / Microsoft Fabric / 高度な分析とAI / デザインとストーリーテリング / 現場で価値を出す |

### 設計方針

**1. なぜ学ぶのかを毎回明示する**
全レッスンの冒頭に「なぜ学ぶのか」「このレッスンで身につく力」「到達目標」「次に開けること」を表示します。
前提レッスンが未完了なら警告が出ます。学習が積み上がっている実感が持てる作りです。

**2. 図で理解させる（読ませない）**
Mermaid は使っていません。図は `figure` ブロックに書いた設定から、専用エンジンが大きなSVG/HTMLとして描画します。
13種類（工程図・比較・スタースキーマ・データ変換の前後・DAXの解剖図・グラフ・階層図ほか）を使い分けます。

説明は文章ではなく図に載せる方針を、機械チェックで強制しています。
**1レッスンあたり「読む文字」は2,200字以下・図は10枚以上**（ハンズオンは2,800字以下・6枚以上）。
1段落は100字まで、段落が3つ続いたらそこは図にします。超過するとビルドと CI が失敗します。

```bash
python3 scripts/check_density.py          # レッスン
python3 scripts/check_density.py --labs   # ハンズオン
python3 scripts/check_density.py --top 20 # 読む文字が多い順
```

**3. 操作して覚える**
フィルターコンテキストや結合の挙動は、読むより触るほうが速く身につきます。
本文中に埋め込まれた10種類のウィジェットで、実際にクリックして挙動を確かめられます。

**4. 用語で迷わせない**
本文中の専門用語は自動的に用語集にリンクされ、ホバーで1文の定義が出ます。
クイズの解説の中でも同じようにリンクされます。
さらに **Ctrl/⌘ + K**（または `/`）で、レッスン本文・見出し・ハンズオン・用語を横断検索できます。
「バイブル」として、分からない語が出てきたらその場で解決できます。

**5. Power BI だけでは足りない知識も入れる**
統計・指標設計・可視化理論・データマネジメントを `データサイエンス視点` として各所に組み込んでいます。
ツールの操作だけ覚えても現場では使えないためです。

確率統計やデータサイエンスが未経験でも詰まらないように、
統計・データサイエンス系の **162語すべてに「かんたんに言うと」（たとえ話の一文）と図解**を付けました。
用語を別の専門用語で説明しないことを条件にしています。
図には必ず具体的な数字が入ります（中央値なら年収5人の実数、CAGR なら 100万→200万・3年 で約26%）。
統計の言い回しは誤りやすいため、p値を「仮説が正しい確率」と書かない、
信頼区間を「95%の確率で真の値がこの中にある」と書かない、といった点を守っています。

**6. PL-300 を1項目も落とさない**
公式の出題範囲24スキル項目すべてにレッスンを対応づけ、
`pl300.html` でカバレッジ表として可視化しています。模擬試験はスキル項目別に採点され、弱点だけを再出題できます。

---

## GitHub で公開する

### よくある質問：GitHub の Web 画面で見られますか？

- **リポジトリのファイル一覧（github.com）で `.html` を開いても、ソースコードが表示されるだけです。**
  GitHub のファイルビューアは HTML を実行しません。
- **サイトとして表示するには GitHub Pages を有効にする必要があります。** 下の手順で数分です。
  有効にすると `https://<ユーザー名>.github.io/<リポジトリ名>/` で誰でも閲覧できます。
- Markdown（`README.md` など）は github.com 上でそのまま読めます。

### 公開手順（3分）

1. リポジトリの **Settings → Pages** を開く
2. Source を **Deploy from a branch** にする
3. Branch を **`main`**、フォルダを **`/docs`** に設定して **Save**

数分後に `https://<ユーザー名>.github.io/<リポジトリ名>/` で公開されます。
以降は `main` に push するだけで自動的に反映されます。

> **この設定だけは、あなたの操作が必要です。**
> GitHub Pages の有効化はリポジトリ管理者の権限が必要で、
> ワークフローの `GITHUB_TOKEN` では実行できません
> （`Resource not accessible by integration` で拒否されます）。

`docs/.nojekyll` を置いてあるため、Jekyll による変換は行われず、
HTML / CSS / JS / JSON はそのまま配信されます。

### 検証ワークフローについて（任意）

`.github/workflows/pages.yml` は**公開処理をしません**。
`main` への push 時に、壊れたまま公開されていないかを検査するだけです。

- カリキュラム・用語集・クイズ・検索インデックスの生成
- 図(figure)のJSON検査
- コンテンツ整合性チェック（リンク切れ・クイズの正解範囲・PL-300コードなど）
- 本文の文字量チェック（読む文字が多すぎる／図が少なすぎるレッスンを弾く）
- 計測APIの単体テスト
- Mermaid が混入していないかの確認
- **生成物のコミット漏れの検出**（`docs/` をそのまま配信するため重要）

> このリポジトリが public であれば **GitHub Actions は無料**です
> （実行時間が課金されるのは private リポジトリのみ）。
> それでも動かしたくない場合は、Actions タブでこのワークフローを Disable してください。
> **公開はワークフローに依存していないので、止めてもサイトは出ます。**

> 注意：`docs/content/curriculum.json` などは生成物です。
> コンテンツを編集したら `python3 scripts/build_all.py` を実行してからコミットしてください。

---

## アクセス統計を有効にする（任意・10分）

統計にはサーバが必要です。GitHub Pages は静的サイトのみのため、**Cloudflare Workers + D1**（無料枠で十分）を使います。
詳細は [`worker/README.md`](worker/README.md) を参照してください。

```bash
npm install -g wrangler
wrangler login

cd worker
wrangler d1 create pbm-analytics          # 出力された database_id を wrangler.toml に貼る
wrangler d1 execute pbm-analytics --remote --file=./schema.sql
wrangler secret put ADMIN_PASSWORD        # ← ここで管理画面のパスワードを設定
wrangler deploy
```

デプロイ後のURLを `docs/assets/js/config.js` の `analyticsEndpoint` に設定し、
`worker/wrangler.toml` の `ALLOWED_ORIGINS` を自分のサイトのオリジンに変更して push します。

管理画面は `https://<あなたのサイト>/admin.html` です。

### 管理画面で見られるもの

ページビュー / ユニーク訪問者 / セッション / 平均滞在時間、日別推移、時間帯（UTC基準）、
**国・地方（州や都道府県）・都市**、ページ別、流入元、デバイス・ブラウザ・OS、利用者のタイムゾーン、
完了されたレッスン、**クイズ平均点が低い順（＝つまずき箇所）**、直近のアクセス、CSVエクスポート。

### プライバシー

- **IPアドレスは保存しません。** 国・地域・都市は Cloudflare がリクエストに付与する位置情報メタデータから取得しています
- 訪問者の識別は個人情報を含まないランダムIDのみ
- リファラはオリジンだけを保存し、パスやクエリは保存しません
- 利用者は「学習記録」ページから自分の端末での計測を停止できます
- 保持期間は `RETENTION_DAYS`（既定400日）で、日次のcronで自動削除されます
- 管理画面のURLは公開されますが、パスワードなしではデータは一切表示されません

> 公開サイトで計測する場合、所在地の法令に応じてプライバシーポリシーの掲示や同意取得が必要になることがあります。

---

## ディレクトリ構成

```
docs/                       GitHub Pages で公開されるサイト本体
├── index.html              トップ（4ティアの全体像）
├── tiers.html              学習の全体像（ティア × モジュール）
├── roadmap.html            詳細ロードマップ（3階層アコーディオン）
├── lesson.html             レッスン表示（?id=L0601）
├── labs.html / lab.html    ハンズオン
├── quizzes.html / quiz.html 理解度クイズ
├── exam.html               PL-300 模擬試験（領域・スキル項目別採点）
├── pl300.html              PL-300 出題範囲カバレッジ表
├── glossary.html           用語集（検索・索引・タグ絞り込み）
├── progress.html           学習記録
├── admin.html              管理ダッシュボード（要パスワード）
├── assets/
│   ├── css/                style / figure / interactive / glossary / lesson
│   └── js/
│       ├── config.js       ★ サイト設定（計測サーバのURLなど）
│       ├── app.js          共通処理・進捗管理・カリキュラム取得
│       ├── render.js       Markdown → HTML（図ブロック・コードハイライト）
│       ├── figure.js       図解エンジン（13種類）
│       ├── interactive.js  操作できる図解（10種類）
│       ├── glossary.js     用語の自動リンクとポップオーバー
│       ├── quiz.js         クイズ・試験エンジン
│       ├── search.js       サイト内検索（Ctrl/⌘ + K）
│       └── analytics.js    計測クライアント
├── content/
│   ├── modules/M01〜M22.json   ★ モジュールとレッスンの定義
│   ├── lessons/*.md            レッスン本文
│   ├── labs/*.md               ハンズオン手順
│   ├── quizzes/*.json          設問
│   ├── glossary/*.json         用語集（モジュール別）
│   ├── curriculum.json         生成物（build_all.py が作る）
│   ├── pl300.json              生成物（スキル項目 → レッスンの逆引き）
│   └── search.json             生成物（サイト内検索のインデックス）
└── data/*.csv              ハンズオン用サンプルデータ

worker/                     アクセス統計バックエンド（Cloudflare Workers + D1）
scripts/                    ビルドと検証
tests/                      ブラウザテスト
AUTHORING_SPEC.md           ★ 執筆・実装の仕様（図の書き方はここ）
```

---

## ローカルで動かす

```bash
python3 scripts/build_all.py       # データ生成 + 検証
cd docs && python3 -m http.server 8000
```

`http://localhost:8000/` を開きます。
`file://` で直接開くとコンテンツの読み込みがブラウザにブロックされるため動きません。

---

## コンテンツを追加・編集する

執筆ルール・図の書き方・クイズの形式はすべて [`AUTHORING_SPEC.md`](AUTHORING_SPEC.md) にまとめています。

```bash
# レッスンを追加する
#   1. docs/content/modules/M06.json の lessons に項目を足す
#   2. docs/content/lessons/L0607.md を書く（図は ```figure ブロック）
#   3. docs/content/quizzes/L0607.json に5問書く
#   4. 新出用語を docs/content/glossary/M06.json に登録する
python3 scripts/build_all.py
```

| コマンド | 内容 |
|---|---|
| `python3 scripts/build_all.py` | すべて生成して検証する（これだけ覚えれば十分） |
| `python3 scripts/build_curriculum.py` | モジュール定義 → curriculum.json / pl300.json |
| `python3 scripts/build_glossary_index.py` | 用語集の統合インデックス |
| `python3 scripts/build_quiz_index.py` | クイズのインデックス |
| `python3 scripts/build_search_index.py` | サイト内検索のインデックス |
| `python3 scripts/fix_figures.py --write` | 図のJSONの機械的な誤りを自動修正 |
| `python3 scripts/validate_content.py` | 整合性チェック |
| `python3 scripts/check_density.py` | 本文の文字量チェック（`--labs` / `--top N`） |
| `python3 scripts/generate_sample_data.py` | サンプルデータの再生成 |

テストは [`tests/README.md`](tests/README.md) を参照してください。

---

## 外部依存

サイトは静的HTML/CSS/JSのみで、ビルド不要・CDN不要です。
Markdownパーサ（marked, MIT）はリポジトリに同梱しています。**外部への通信は発生しません**（計測を有効にした場合を除く）。

---

## 免責

- 本サイトは Microsoft 非公式の学習教材です。Power BI は Microsoft Corporation の商標です
- 掲載している設問はすべてオリジナルであり、実際の試験問題ではありません
- 製品仕様・試験範囲は変更されます。受験前に必ず
  [PL-300 公式ページ](https://learn.microsoft.com/ja-jp/credentials/certifications/exams/pl-300/)
  で最新情報をご確認ください
