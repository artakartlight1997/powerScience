# アクセス統計バックエンド（Cloudflare Workers + D1）

GitHub Pages は静的サイトしか置けないため、閲覧統計を記録するにはサーバが必要です。
ここでは Cloudflare の無料枠で動く小さなAPIを用意しています。

- 記録するもの：ページビュー・滞在時間・国/地域/都市・デバイス・レッスン完了・クイズ得点
- **IPアドレスは保存しません**（国・地域は Cloudflare がリクエストに付与するメタデータから取得）
- 管理画面のパスワードは、あなたが `wrangler secret` で設定します

## 費用の目安

Cloudflare の無料枠は、執筆時点でおおむね次のとおりです（最新の条件は公式をご確認ください）。

| リソース | 無料枠 |
|---|---|
| Workers リクエスト | 1日 100,000 件 |
| D1 の読み取り | 1日 500 万行 |
| D1 の書き込み | 1日 100,000 行 |
| D1 のストレージ | 5 GB |

個人〜小規模の学習サイトであれば、まず無料枠を超えません。

---

## セットアップ（10分）

### 1. wrangler を用意する

```bash
npm install -g wrangler
wrangler login
```

ブラウザが開くので、Cloudflare アカウントでログインします（アカウントは無料で作れます）。

### 2. D1 データベースを作る

```bash
cd worker
wrangler d1 create pbm-analytics
```

出力に含まれる `database_id` を `wrangler.toml` に貼り付けます。

```toml
[[d1_databases]]
binding = "DB"
database_name = "pbm-analytics"
database_id = "ここに貼り付ける"
```

### 3. テーブルを作る

```bash
wrangler d1 execute pbm-analytics --remote --file=./schema.sql
```

### 4. 管理画面のパスワードを設定する

```bash
wrangler secret put ADMIN_PASSWORD
```

対話的にパスワードの入力を求められます。**入力した値はリポジトリには保存されません。**
Cloudflare 側のシークレットとして保管されます。

> パスワードを変更したいときは、同じコマンドをもう一度実行してください。
> 変更すると、発行済みのログイントークンはすべて無効になります。

### 5. 許可するオリジンを設定する

`wrangler.toml` の `ALLOWED_ORIGINS` を、公開サイトのオリジンに変更します。

```toml
[vars]
ALLOWED_ORIGINS = "https://<ユーザー名>.github.io"
```

複数指定する場合はカンマ区切りにします。`"*"` はすべてのオリジンを許可します（検証用途のみ推奨）。

### 6. デプロイ

```bash
wrangler deploy
```

`https://pbm-analytics.<サブドメイン>.workers.dev` のようなURLが表示されます。

### 7. サイト側に設定する

`docs/assets/js/config.js` を編集します。

```js
window.PBM_CONFIG = {
  analyticsEndpoint: "https://pbm-analytics.xxxx.workers.dev",
  analyticsEnabled: true,
  ...
};
```

コミットして push すれば、計測が始まります。

### 8. 動作確認

```bash
curl https://pbm-analytics.xxxx.workers.dev/health
# => {"ok":true,"hasPassword":true}
```

`hasPassword` が `false` なら、手順4のシークレット設定が未完了です。

その後、`https://<あなたのサイト>/admin.html` を開いてログインしてください。

---

## API 仕様

| メソッド | パス | 認証 | 内容 |
|---|---|---|---|
| GET | `/health` | 不要 | 死活確認 |
| POST | `/collect` | 不要 | イベントの記録（サイトから呼ばれる） |
| POST | `/admin/login` | 不要 | パスワード認証・トークン発行 |
| GET | `/admin/summary?days=30` | 要 | 集計データ |
| GET | `/admin/recent?limit=100` | 要 | 直近イベント |
| GET | `/admin/export.csv?days=30` | 要 | CSVエクスポート |

認証が必要なエンドポイントには `Authorization: Bearer <token>` を付けます。
トークンは `SESSION_HOURS`（既定12時間）で失効し、HMAC-SHA256 で署名されています。

### 記録されるイベント

| event | 発生タイミング |
|---|---|
| `pageview` | ページ表示時 |
| `heartbeat` | 表示中に一定間隔（既定30秒） |
| `leave` | ページ離脱時（滞在秒数つき） |
| `lesson_complete` | レッスンを完了にしたとき |
| `lab_complete` | ラボを完了にしたとき |
| `quiz_answer` | クイズの1問に解答したとき |
| `quiz_result` | クイズを終えたとき（得点つき） |
| `exam_start` / `exam_result` | 模擬試験の開始・終了 |

---

## 運用

### ログの保持期間

`wrangler.toml` の `RETENTION_DAYS`（既定400日）を過ぎたログは、
日次の cron トリガー（`17 3 * * *` UTC）で自動削除されます。

### データを直接確認する

```bash
wrangler d1 execute pbm-analytics --remote \
  --command "SELECT day, COUNT(*) FROM events GROUP BY day ORDER BY day DESC LIMIT 10"
```

### ログをすべて消す

```bash
wrangler d1 execute pbm-analytics --remote --command "DELETE FROM events"
```

### 計測を止める

`docs/assets/js/config.js` の `analyticsEnabled` を `false` にするか、
`analyticsEndpoint` を空文字にして push してください。送信は完全に停止します。

---

## トラブルシューティング

| 症状 | 原因と対処 |
|---|---|
| 管理画面で「サーバエラー(401)」 | パスワードが違うか、トークンが失効。再ログインしてください |
| 管理画面で「ADMIN_PASSWORD が未設定です」 | `wrangler secret put ADMIN_PASSWORD` を実行してください |
| データが1件も記録されない | `config.js` の `analyticsEndpoint` を確認。ブラウザの開発者ツールでCORSエラーが出ていないかも確認 |
| CORSエラーが出る | `wrangler.toml` の `ALLOWED_ORIGINS` に自分のサイトのオリジンを追加して再デプロイ |
| 国や都市が「不明」になる | ローカル環境（localhost）からのアクセスには位置情報が付きません。公開URLで確認してください |
| CSVエクスポートが落ちてこない | トークンをクエリ文字列で渡しています。ブラウザのポップアップブロックを確認してください |

---

## Cloudflare 以外を使う場合

`/collect` に JSON を POST し、`/admin/*` を認証付きで返す実装であれば、
どのプラットフォームでも構いません（Vercel Functions + Postgres、Deno Deploy + KV など）。

ただし、国・地域の情報は Cloudflare が付与する `request.cf` に依存しています。
別のプラットフォームを使う場合は、地理情報の取得方法を差し替えてください。
