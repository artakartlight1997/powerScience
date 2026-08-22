# vendor

外部ライブラリを同梱しているディレクトリです。CDNに到達できない環境でも
本文が表示されるよう、Markdownパーサだけはここに置いています。

| ファイル | 内容 | 版 |
|---|---|---|
| `marked.umd.js` | Markdown → HTML 変換（MITライセンス） | 12.0.2 |

更新するには：

```bash
npm i marked@12.0.2 --no-save
cp node_modules/marked/lib/marked.umd.js docs/assets/vendor/marked.umd.js
cp node_modules/marked/LICENSE.md docs/assets/vendor/marked.LICENSE.md
```

## Mermaid（図の描画）について

Mermaid は約3.3MB（gzip後 約1MB）と大きいため、既定では CDN から読み込みます。
読み込めない場合、図の位置には案内文と図のソースが表示されます（本文は問題なく読めます）。

外部リクエストを完全になくしたい場合は、次の手順で同梱できます。

```bash
npm i mermaid@10.9.1 --no-save
mkdir -p docs/assets/vendor/mermaid
cp -r node_modules/mermaid/dist/* docs/assets/vendor/mermaid/
```

そのうえで `docs/assets/js/render.js` の `MERMAID_URL` を
`PBM.url("assets/vendor/mermaid/mermaid.esm.min.mjs")` に変更してください。
