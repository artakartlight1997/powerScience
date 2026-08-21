# Power BI Mastery — 学習サイト

Power BI の初学者が **PL-300（Microsoft Power BI Data Analyst）** 認定レベルまで到達するための、
図解 × ハンズオン × クイズ の学習サイトです。GitHub Pages で公開でき、スマートフォンからも学習できます。

閲覧統計（どの地域の人が、いつ、どのページを見たか）は、一般には見えない管理画面で確認できます。
管理画面のパスワードは、あなたが自分で設定します。

---

## 中身

| 区分 | 内容 |
|---|---|
| 学習ロードマップ | 6レベル（Lv.0〜Lv.5）、想定学習時間 80時間 |
| レッスン | 39本（すべて日本語・図解つき） |
| ハンズオンラボ | 6本（サンプルデータ同梱） |
| 演習問題 | 223問（レッスン別クイズ156問 + 模擬試験バンク67問） |
| 用語集 | 72語（検索可能） |
| サンプルデータ | 架空の小売企業「Northstar Retail」の売上データ 約7,000行 |

### 学習ロードマップ

| レベル | テーマ | PL-300 出題領域 |
|---|---|---|
| Lv.0 | はじめの一歩（全体像・環境構築） | — |
| Lv.1 | データの取得と整形（Power Query / M） | データの準備 25-30% |
| Lv.2 | データモデリング（スタースキーマ） | データのモデル化 25-30% |
| Lv.3 | DAX（フィルターコンテキスト・CALCULATE） | 領域1〜3にまたがる中核 |
| Lv.4 | 可視化とレポート設計 | 視覚化と分析 25-30% |
| Lv.5 | 運用・ガバナンス・試験対策 | 資産の管理とセキュリティ 15-20% |

---

## ディレクトリ構成

```
docs/                      GitHub Pages で公開されるサイト本体
├── index.html             トップページ
├── roadmap.html           学習ロードマップ
├── lesson.html            レッスン表示（?id=L001）
├── labs.html / lab.html   ハンズオン一覧・本文
├── quizzes.html / quiz.html  クイズ一覧・出題
├── exam.html              PL-300 模擬試験（時間制限つき）
├── glossary.html          用語集
├── progress.html          学習記録（端末内に保存）
├── admin.html             管理ダッシュボード（要パスワード）
├── assets/
│   ├── css/style.css      デザインシステム
│   └── js/
│       ├── config.js      ★ サイト設定（計測サーバのURLなど）
│       ├── app.js         共通処理・進捗管理
│       ├── render.js      Markdown / Mermaid図 / DAXハイライト
│       ├── quiz.js        クイズ・試験エンジン
│       └── analytics.js   計測クライアント
├── content/
│   ├── curriculum.json    ★ カリキュラム定義（レベル・レッスン・ラボ）
│   ├── lessons/*.md       レッスン本文
│   ├── labs/*.md          ハンズオン手順
│   ├── quizzes/*.json     設問
│   └── glossary.json      用語集
└── data/*.csv             ハンズオン用サンプルデータ

worker/                    アクセス統計バックエンド（Cloudflare Workers + D1）
├── src/index.js           API 本体
├── schema.sql             D1 のテーブル定義
├── wrangler.toml          デプロイ設定
└── README.md              セットアップ手順

scripts/
├── generate_sample_data.py  サンプルデータ生成
└── validate_content.py      コンテンツ整合性チェック
```

---

## 公開の手順

### 1. GitHub Pages で公開する（5分）

このリポジトリを GitHub に置いたうえで、次のどちらかを選びます。

**方法A：ブランチから公開（もっとも簡単）**

1. リポジトリの **Settings → Pages**
2. Source を **Deploy from a branch**
3. Branch を `main`、フォルダを **`/docs`** に設定して Save

数分後、`https://<ユーザー名>.github.io/<リポジトリ名>/` で公開されます。

**方法B：GitHub Actions で公開（コンテンツ検証つき）**

1. **Settings → Pages** の Source を **GitHub Actions** に設定
2. `main` へ push すると `.github/workflows/pages.yml` が動き、
   コンテンツの整合性チェック（`scripts/validate_content.py`）に通ってからデプロイされます

> この時点で、学習サイトとしては完全に動作します。アクセス統計が不要ならここで完了です。

### 2. アクセス統計を有効にする（10分・任意）

統計を取るにはサーバが必要です。GitHub Pages は静的サイトのみのため、
**Cloudflare Workers + D1**（無料枠で十分）を使います。

手順の詳細は [`worker/README.md`](worker/README.md) を参照してください。要約すると：

```bash
npm install -g wrangler
wrangler login

cd worker
wrangler d1 create pbm-analytics          # 出力された database_id を wrangler.toml に貼る
wrangler d1 execute pbm-analytics --remote --file=./schema.sql
wrangler secret put ADMIN_PASSWORD        # ← ここで管理画面のパスワードを設定
wrangler deploy
```

デプロイ後に表示されるURL（例：`https://pbm-analytics.xxxx.workers.dev`）を、
`docs/assets/js/config.js` の `analyticsEndpoint` に貼り付けて push します。

```js
window.PBM_CONFIG = {
  analyticsEndpoint: "https://pbm-analytics.xxxx.workers.dev",
  ...
};
```

あわせて `worker/wrangler.toml` の `ALLOWED_ORIGINS` を、自分のサイトのオリジンに変更してください。

```toml
ALLOWED_ORIGINS = "https://<ユーザー名>.github.io"
```

### 3. 管理画面を開く

`https://<あなたのサイト>/admin.html` にアクセスし、
計測サーバのURLと、手順2で設定したパスワードを入力します。

---

## 管理ダッシュボードで見られるもの

| 指標 | 内容 |
|---|---|
| ページビュー / 訪問者 / セッション | 期間別（今日・7日・30日・90日・1年） |
| 日別の推移 | 棒グラフ |
| 時間帯 | UTC基準の24時間分布（日本時間 = UTC+9） |
| 国・地域 | 国コード別 |
| 地方 | 州・都道府県レベル |
| 都市 | 市区町村レベル |
| ページ別 | よく見られたページ |
| 流入元 | リファラのオリジン別 |
| デバイス / ブラウザ / OS | スマホ・PCの内訳 |
| タイムゾーン | 利用者の設定タイムゾーン |
| 完了レッスン | どのレッスンが完了されているか |
| クイズ平均点 | 平均点が低い順＝つまずき箇所 |
| 直近のアクセス | 最新120件のイベント |
| CSVエクスポート | 生データのダウンロード |

### プライバシーへの配慮

- **IPアドレスは保存しません。** 国・地域・都市は、Cloudflare がリクエストに付与する位置情報メタデータ（`request.cf`）から取得しています
- 訪問者の識別は、個人情報を含まないランダムなIDのみです
- リファラはオリジン（`https://example.com`）だけを保存し、パスやクエリは保存しません
- 利用者は「学習記録」ページから、自分の端末での計測を停止できます
- ログの保持期間は `wrangler.toml` の `RETENTION_DAYS`（既定400日）で設定でき、日次のcronで自動削除されます
- 管理画面のURL自体は公開されますが、パスワードなしではデータは一切表示されません

> 公開サイトで計測を行う場合、所在地の法令（日本の個人情報保護法、EU向けならGDPR等）に応じて
> プライバシーポリシーの掲示や同意取得が必要になることがあります。運用前にご確認ください。

---

## ローカルで動かす

```bash
cd docs
python3 -m http.server 8000
```

ブラウザで `http://localhost:8000/` を開きます。
`file://` で直接開くと、`fetch` によるコンテンツ読み込みがブラウザにブロックされるため動きません。

コンテンツを編集したら、次のコマンドで確認できます。

```bash
python3 scripts/validate_content.py      # コンテンツの整合性
node worker/test/worker.test.mjs         # 計測APIの単体テスト（依存なし）
```

ブラウザでの表示確認まで含めたテストの一覧は [`tests/README.md`](tests/README.md) を参照してください。

---

## コンテンツを追加・編集する

執筆のルールとMarkdown記法は [`CONTENT_GUIDE.md`](CONTENT_GUIDE.md) にまとめています。

- レッスンを追加：`docs/content/curriculum.json` に項目を足し、`docs/content/lessons/<ID>.md` を作る
- クイズを追加：`docs/content/quizzes/<ID>.json` を作り、`index.json` を更新する
- サンプルデータを作り直す：`python3 scripts/generate_sample_data.py`

---

## 外部依存

サイトは静的HTML/CSS/JSのみで、ビルド不要です。CDNから次の2つだけを読み込みます。

| ライブラリ | 用途 | 読み込めない場合 |
|---|---|---|
| [marked](https://marked.js.org/) 12 | Markdown → HTML | 本文がプレーンテキスト表示になります |
| [mermaid](https://mermaid.js.org/) 10 | 図の描画 | 図の位置に案内文が表示されます |

どちらも読み込みに失敗してもサイト自体は動作します。

---

## 免責

- 本サイトは Microsoft 非公式の学習教材です。Power BI は Microsoft Corporation の商標です
- 掲載している設問はすべてオリジナルであり、実際の試験問題ではありません
- 製品仕様・試験範囲は変更されます。受験前に必ず
  [PL-300 公式ページ](https://learn.microsoft.com/ja-jp/credentials/certifications/exams/pl-300/)
  で最新情報をご確認ください
