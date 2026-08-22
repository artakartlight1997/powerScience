# テスト

## 1. コンテンツ整合性（依存なし）

```bash
python3 scripts/validate_content.py
```

カリキュラムが参照するレッスン本文・クイズ・ラボ・データファイルの存在、
クイズの正解インデックスの妥当性、用語集のリンク切れを検査します。
GitHub Actions のデプロイ前にも実行されます。

## 2. 計測バックエンド（依存なし）

```bash
node worker/test/worker.test.mjs
```

D1 をモックして、ルーティング・パスワード認証・トークン署名・CORS・
SQLのバインド数などを検証します。Cloudflare へのデプロイは不要です。

## 3. ブラウザテスト（Playwright が必要）

```bash
npm i -D playwright && npx playwright install chromium

# 別ターミナルでサイトを起動しておく
cd docs && python3 -m http.server 8123
```

| コマンド | 内容 |
|---|---|
| `node tests/smoke.mjs` | 全ページが表示され、JSエラーが出ないこと |
| `node tests/render-all.mjs` | 全レッスン・全ラボが正しく描画されること（図・表・強調） |
| `node tests/functional.mjs` | 進捗保存・クイズ採点・試験タイマー・ダークモード・オプトアウト |

`functional.mjs` はモバイル幅（390px）で実行し、横スクロールが出ないことも確認します。

> ブラウザテストはネットワーク制限のある環境では Mermaid の読み込みに失敗しますが、
> その場合もフォールバック表示が出るだけで、テスト自体は成功します。
