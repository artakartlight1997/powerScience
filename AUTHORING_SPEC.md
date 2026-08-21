# 執筆・実装スペック v3（全エージェント共通の契約）

このファイルが唯一の正です。Mermaid は**全面禁止**。図は下記 `figure` ブロックで書きます。

---

## 1. サイト構造（v2）

4段階のティア。各ティアは複数モジュール、各モジュールは複数レッスンを持ちます。

| ティア | ID | 名称 | 到達点 |
|---|---|---|---|
| 1 | `T1` | 初級 Beginner | BIの考え方を理解し、自分でレポートを1枚作れる |
| 2 | `T2` | 中級 Intermediate | 実務データを整形し正しいモデルを組み、必要な指標をDAXで書ける |
| 3 | `T3` | 上級 Advanced | 性能・複雑要件・組織展開を扱え、PL-300に合格できる |
| 4 | `T4` | プロ Professional | 設計をリードし、データから事業価値を出せる |

---

## 2. ファイル配置

```
docs/content/modules/<MID>.json      モジュール定義 + そのレッスン一覧（各エージェントが1ファイルずつ担当）
docs/content/lessons/<LID>.md        レッスン本文
docs/content/quizzes/<LID>.json      レッスンのクイズ
docs/content/glossary/<MID>.json     そのモジュールで導入した用語（配列）
docs/content/labs/<LABID>.md         ハンズオン
```

`docs/content/curriculum.json` は統合担当がモジュール断片から自動生成します。**直接編集しないでください。**

---

## 3. モジュール定義 JSON（`docs/content/modules/<MID>.json`）

```json
{
  "id": "M06",
  "tier": "T2",
  "order": 6,
  "title": "データモデリング",
  "subtitle": "スタースキーマで土台を作る",
  "goal": "スタースキーマを設計でき、リレーションシップの挙動を図で説明できる",
  "estimatedHours": 10,
  "lessons": [
    {
      "id": "L0601",
      "title": "スタースキーマ — Power BI最重要の設計原則",
      "minutes": 35,
      "type": "concept",
      "why": "実務でPower BIが遅い・数字が合わない原因の大半はモデル設計にある。",
      "gain": "フラットな1枚表をファクトとディメンションに分解して設計できる。",
      "objectives": ["スタースキーマの構造を図示できる", "フラットテーブルの問題点を4つ挙げられる", "既存データを分解できる"],
      "prereq": ["L0505"],
      "unlocks": "この設計ができると、DAXが劇的に書きやすくなり、性能問題の8割が消える。",
      "keywords": ["スタースキーマ", "ファクトテーブル", "ディメンションテーブル"],
      "pl300": ["2.1 データモデルの設計"],
      "ds": ["次元モデリング", "データウェアハウス設計"],
      "quiz": "L0601",
      "lab": "LAB03"
    }
  ]
}
```

| フィールド | 必須 | 内容 |
|---|---|---|
| `why` | ○ | **なぜ学ぶのか。実務の困りごとから1〜2文**。レッスン冒頭に自動表示される |
| `gain` | ○ | **このレッスン後にできるようになること。1文**。「〜できる」で終える |
| `unlocks` | ○ | **その力が次に何を可能にするか。1文**。学習の連鎖を示す |
| `prereq` | ○ | 前提レッスンID配列（なければ `[]`） |
| `pl300` | ○ | PL-300スキル項目（該当なしは `[]`）。§7参照 |
| `ds` | ○ | 同時に身につくデータサイエンス/BI知識のキーワード（なければ `[]`） |
| `type` | ○ | `concept` / `hands-on` / `drill` / `exam` |

**レッスンIDは `L` + モジュール2桁 + 連番2桁**（例：M06の3本目 → `L0603`）。

---

## 4. レッスン本文（Markdown）

### 禁止・必須

- **H1（`#`）を書かない。** タイトルは自動表示
- **Mermaid 禁止。** ` ```mermaid ` を書いたらビルドエラー
- **読ませるのではなく、見せる。** 説明が長くなったら文章ではなく図にする
- 断定して書く。「〜かもしれません」を避ける
- 専門用語は初出時に必ず1文で説明する（用語集にも登録する）

### 文字量の上限（v3・機械チェックあり）

読者が実際に読む文字＝**地の文＋箇条書き＋表＋コールアウト**。
図(figure)のJSONは描画されるので文字数に数えません。

| 項目 | レッスン | ハンズオン |
|---|---|---|
| 読む文字（合計） | **2,200字以下** | 2,800字以下 |
| 地の文 | **800字以下** | 800字以下 |
| コールアウト | **3個以下 / 600字以下** | 3個以下 / 600字以下 |
| コード | 70行以下 | 110行以下 |
| figure | **10枚以上** | 6枚以上 |
| 1段落 | 100字以下 | 100字以下 |
| 連続する段落 | 2つまで | 2つまで |
| 全体の行数 | 100〜210行 | 100〜260行 |
| H2見出し | 5〜9個 | 5〜14個 |

```bash
python3 scripts/check_density.py            # 全レッスン
python3 scripts/check_density.py L0601      # 個別
python3 scripts/check_density.py --labs     # ハンズオン
python3 scripts/check_density.py --top 20   # 読む文字が多い順
```

`build_all.py` と CI に組み込まれているため、超過するとビルドが失敗します。

### 文章を図に置き換える対応表

| 書きたくなったもの | 使う figure |
|---|---|
| 手順・工程の説明 | `steps` / `flow` / `pipeline` |
| A と B の違い | `compare` |
| 3〜6個の要素の列挙 | `cards` |
| 階層・入れ子・レイヤ | `stack` / `tree` |
| 2軸の分類・判断基準 | `matrix` |
| 変換前後のデータ | `tablediff` |
| テーブル同士の関係 | `star` |
| 時系列・進化・順序 | `timeline` |
| DAX/M式の各部の意味 | `formula` |
| 数値の大小・傾向 | `chart` |
| 触って確かめてほしい挙動 | `interactive` |

### 使える記法

**コールアウト**

```markdown
> [!NOTE] 要点
> [!TIP] 実務のコツ
> [!WARN] 注意
> [!TRAP] つまずきポイント
> [!EXAM] PL-300で問われる
> [!DS] データサイエンス視点（BI/統計の一般知識）
```

**コード**（`dax` / `m` / `sql` / `python` / `text` を指定。専用ハイライトが効く）

**用語リンク**：用語集に登録済みの語は本文中で自動リンクされます。手動リンクは不要です。
強制的にリンクしたい場合のみ `[[スタースキーマ]]` と書きます。

---

## 5. 図（figure ブロック）— Mermaidの代替

````markdown
```figure
{ "type": "flow", "title": "Power BIの5工程", "caption": "この流れが全レベルの背骨になる",
  "items": [ {"label":"取得","sub":"Excel / DB","tone":"blue"}, {"label":"整形","sub":"Power Query","tone":"green"} ] }
```
````

- `title` は図の見出し、`caption` は図の下の説明（どちらも任意だが原則つける）
- `tone` は `blue` `green` `amber` `pink` `violet` `cyan` `gray` `good` `bad` から選ぶ
- JSONは厳密（末尾カンマ不可、コメント不可）。文字列内の改行は `\n`

### 5.1 `flow` — 工程・流れ

```json
{ "type":"flow", "dir":"row", "items":[
  {"label":"取得","sub":"データを持ってくる","tone":"blue","icon":"⬇"},
  {"label":"整形","sub":"分析できる形にする","tone":"green"} ] }
```
`dir`: `row`（既定・横）/ `col`（縦）。項目は2〜6個。

### 5.2 `steps` — 手順（大きな番号つき縦並び）

```json
{ "type":"steps", "items":[
  {"title":"データを取得する","text":"ホーム → データを取得 → テキスト/CSV","tone":"blue"},
  {"title":"型を確認する","text":"すべての列に明示的な型を設定する"} ] }
```

### 5.3 `compare` — 比較（良い/悪い、Before/After）

```json
{ "type":"compare", "panels":[
  {"title":"フラットテーブル","tone":"bad","items":["同じ値が何百万回も繰り返される","売上0の商品が出てこない"],"note":"アンチパターン"},
  {"title":"スタースキーマ","tone":"good","items":["圧縮が効く","全商品を一覧できる"],"note":"推奨"} ] }
```
`panels` は2〜3個。`tone`: `good` / `bad` / `neutral` / 色名。

### 5.4 `cards` — 並列な概念のカード

```json
{ "type":"cards", "cols":3, "items":[
  {"icon":"📦","title":"インポート","text":"データをPower BI内に圧縮保存する","tone":"blue"} ] }
```

### 5.5 `stack` — 階層・レイヤー（上が上位）

```json
{ "type":"stack", "layers":[
  {"label":"レポート","sub":"見る人が触る層","tone":"pink"},
  {"label":"セマンティックモデル","sub":"数字の定義がある層","tone":"amber"},
  {"label":"データソース","sub":"事実が置かれている層","tone":"blue"} ] }
```

### 5.6 `matrix` — 2×2 マトリクス

```json
{ "type":"matrix", "xLabel":"データ量", "yLabel":"鮮度要求",
  "xLow":"小","xHigh":"大","yLow":"低","yHigh":"高",
  "quadrants":[
    {"title":"インポート","text":"迷ったらこれ","tone":"good"},
    {"title":"DirectQuery","text":"常に最新が必要","tone":"amber"},
    {"title":"インポート","text":"最速","tone":"good"},
    {"title":"複合モデル","text":"集計表を併用","tone":"violet"} ] }
```
`quadrants` の順序は **左上 → 右上 → 左下 → 右下**。

### 5.7 `tablediff` — データの変換前後

```json
{ "type":"tablediff", "arrowLabel":"ピボット解除",
  "before":{"title":"横持ち（分析しにくい）","tone":"bad","head":["商品","1月","2月"],"rows":[["ノートPC","120","135"]]},
  "after":{"title":"縦持ち（整然データ）","tone":"good","head":["商品","月","数量"],"rows":[["ノートPC","1月","120"],["ノートPC","2月","135"]]} }
```
セル値の先頭に `!` を付けると強調表示（例：`"!120"`）。

### 5.8 `star` — スタースキーマ（中心＋放射）

```json
{ "type":"star",
  "fact":{"label":"Fact_売上","lines":["日付 / 商品ID / 店舗ID","数量 / 金額"]},
  "dims":[
    {"label":"Dim_日付","lines":["年 / 月 / 四半期"]},
    {"label":"Dim_商品","lines":["商品名 / カテゴリ"]},
    {"label":"Dim_店舗","lines":["店舗名 / 地域"]},
    {"label":"Dim_顧客","lines":["顧客名 / セグメント"]} ],
  "edgeLabel":"1対多" }
```
`dims` は2〜6個。矢印はディメンション→ファクトで自動描画。

### 5.9 `tree` — 階層・分岐

```json
{ "type":"tree", "root":{"label":"接続方式を選ぶ"},
  "children":[
    {"label":"インポート","sub":"既定。迷ったらこれ","tone":"good",
     "children":[{"label":"増分更新","sub":"大きい表はこれ"}]},
    {"label":"DirectQuery","sub":"常に最新が必要","tone":"amber"} ] }
```

### 5.10 `timeline` — 時系列・ロードマップ

```json
{ "type":"timeline", "items":[
  {"label":"Week 1","title":"Power Query","text":"整形を身につける","tone":"green"} ] }
```

### 5.11 `formula` — 数式の分解（DAXの解剖図）

```json
{ "type":"formula", "lang":"dax",
  "code":"CALCULATE( [売上合計], Dim_商品[カテゴリ] = \"家電\" )",
  "parts":[
    {"match":"CALCULATE","label":"フィルターを変更する唯一の関数","tone":"violet"},
    {"match":"[売上合計]","label":"評価したい式","tone":"blue"},
    {"match":"Dim_商品[カテゴリ] = \"家電\"","label":"適用するフィルター","tone":"amber"} ] }
```
`match` は `code` 内に現れる文字列と完全一致させること。

### 5.12 `chart` — 説明用のグラフ

```json
{ "type":"chart", "kind":"bar", "title":"カテゴリ別売上",
  "categories":["家電","衣料","食品"],
  "series":[{"name":"売上","values":[30,18,52],"tone":"blue"}],
  "highlight":2, "unit":"百万円" }
```
`kind`: `bar` / `hbar` / `line` / `area` / `pie` / `scatter`。`highlight` は強調するインデックス。

### 5.13 `pipeline` — ノードと矢印（自由結線）

```json
{ "type":"pipeline",
  "nodes":[{"id":"a","label":"Excel","tone":"blue"},{"id":"b","label":"Power Query","tone":"green"}],
  "edges":[{"from":"a","to":"b","label":"取り込む"}] }
```

### 5.14 `interactive` — HTMLならではの操作できる図

```json
{ "type":"interactive", "widget":"filter-context", "title":"フィルターコンテキストを体験する" }
```

利用できる `widget`（実装済みのもののみ使用可）：

| widget | 内容 |
|---|---|
| `filter-context` | 表のセルをクリックすると、そのセルに効いているフィルターと計算結果が見える |
| `star-explorer` | スタースキーマ上でディメンションを選ぶと、フィルターの伝播が光って進む |
| `visual-picker` | 「何を知りたいか」を選ぶと最適なビジュアルを提案する |
| `dax-anatomy` | DAX式の各部分にホバーすると役割が表示される |
| `calc-vs-measure` | 計算列とメジャーの評価タイミングをアニメーションで比較 |
| `join-lab` | 結合の種類を切り替えて、残る行が変わる様子を見る |
| `cardinality-lab` | 列のカーディナリティとモデルサイズの関係を体験 |
| `context-transition` | コンテキスト遷移の前後を並べて可視化 |
| `rls-simulator` | ユーザーを切り替えて、見える行が変わる様子を確認 |
| `granularity-lab` | 粒度を変えると何が失われるかを確認 |

---

## 6. 用語集（`docs/content/glossary/<MID>.json`）

配列。そのモジュールで**初めて登場した用語**を必ず全部登録します。

```json
[
  { "term":"スタースキーマ", "en":"Star schema", "reading":"すたーすきーま",
    "short":"ファクト1つを中心にディメンションを放射状に配置する設計。",
    "desc":"中央に数値を持つファクトテーブルを置き、その周りに商品・顧客・日付などの説明的な属性を持つディメンションテーブルを配置する設計。Power BI のエンジンはこの形に最適化されている。",
    "lesson":"L0601", "tags":["モデリング"], "aliases":["スター スキーマ","star schema"] }
]
```

- `short` は**1文**（ホバー表示に使う）。`desc` は2〜4文
- `aliases` に表記ゆれを入れると、その語も自動リンクされる
- 用語は本文中で自動的にリンクされるため、**表記を統一**すること

---

## 7. PL-300 スキル項目コード

`pl300` フィールドには次の文字列を使います（複数可）。

**1. データの準備 (25–30%)**
`1.1 データソースへの接続` / `1.2 データの取得と変換` / `1.3 データのプロファイリング` / `1.4 データのクリーニング` / `1.5 データの構造化` / `1.6 パフォーマンスを考慮した取り込み`

**2. データのモデル化 (25–30%)**
`2.1 データモデルの設計` / `2.2 リレーションシップの構成` / `2.3 計算列とメジャーの作成` / `2.4 タイムインテリジェンス` / `2.5 モデルの最適化` / `2.6 行レベルセキュリティ`

**3. 視覚化と分析 (25–30%)**
`3.1 レポートの作成` / `3.2 ビジュアルの選択と構成` / `3.3 対話機能の設定` / `3.4 レポートの書式とアクセシビリティ` / `3.5 データの探索と分析` / `3.6 AI ビジュアルの活用` / `3.7 モバイル対応`

**4. 資産の管理とセキュリティ (15–20%)**
`4.1 ワークスペースの管理` / `4.2 セマンティックモデルの管理` / `4.3 データ更新の管理` / `4.4 アクセス権とセキュリティ` / `4.5 ガバナンスとライフサイクル`

---

## 8. クイズ（`docs/content/quizzes/<LID>.json`）

```json
{ "id":"L0601", "lesson":"L0601", "title":"スタースキーマ",
  "questions":[
    { "id":"L0601-q1", "type":"single",
      "stem":"実務のシナリオを含む設問文",
      "choices":["...","...","...","..."], "answer":0,
      "explain":"なぜ正解か、**そしてなぜ他が誤りか**を書く。Markdown可。",
      "area":"データのモデル化", "ref":"L0601", "difficulty":3,
      "code":"（任意）設問に添えるコード", "codeLang":"dax" } ] }
```

- `type`: `single`（`answer` は数値）/ `multi`（`answer` は配列）
- `area`: `データの準備` / `データのモデル化` / `視覚化と分析` / `資産の管理とセキュリティ` / `基礎` / `データサイエンス`
- **1レッスンあたり5問**。難易度1〜4を混ぜる。丸暗記で解けない実務シナリオ問題にする

---

## 9. 品質チェック（提出前に必ず）

```bash
python3 scripts/build_all.py          # 生成 + 整合性 + 文字量まで一括
python3 scripts/check_density.py      # 文字量だけ確認したいとき
```

- [ ] Mermaid を1つも使っていない
- [ ] figure ブロックのJSONがすべて妥当
- [ ] `check_density.py` が「0 件が基準未達」で通る
- [ ] 図が1レッスンあたり10枚以上ある
- [ ] `interactive` の図を消していない
- [ ] `why` / `gain` / `unlocks` を全レッスンに書いた
- [ ] 新出用語をすべて用語集に登録した
- [ ] クイズが1レッスン5問ある
- [ ] PL-300スキル項目を割り当てた
