所要30分。Power BI Desktop を開き、手を動かしながら進めてください。

## このラボのゴール

架空の小売企業「Northstar Retail」の売上から、レポートを1枚仕上げます。

```figure
{ "type":"flow", "title":"このラボでたどる5工程", "caption":"複雑なレポートもこの繰り返しでできる",
  "items":[
    {"label":"取得","sub":"CSVを読み込む","tone":"blue","icon":"⬇"},
    {"label":"整形","sub":"型を決める","tone":"green"},
    {"label":"モデル","sub":"表と表をつなぐ","tone":"amber"},
    {"label":"計算","sub":"メジャーを書く","tone":"violet"},
    {"label":"可視化","sub":"ビジュアルを置く","tone":"pink"} ] }
```

```figure
{ "type":"cards", "cols":4, "title":"完成するレポートの中身", "caption":"30分の内訳＝読込6/モデル4/計算5/描画12/仕上3",
  "items":[
    {"icon":"🔢","title":"KPIカード3枚","text":"総売上・販売数量・取引件数","tone":"violet"},
    {"icon":"📊","title":"横棒グラフ","text":"カテゴリ別の売上を降順で","tone":"blue"},
    {"icon":"📈","title":"折れ線グラフ","text":"月次の売上推移","tone":"green"},
    {"icon":"🎚","title":"スライサー","text":"店舗で全体を絞り込む","tone":"amber"} ] }
```

## 準備：データと型を決める

[sales.csv](data/sales.csv) と [products.csv](data/products.csv) をダウンロードします。

```figure
{ "type":"cards", "cols":2, "title":"使う2つのファイル", "caption":"行数の差がファクトとディメンションの差",
  "items":[
    {"icon":"🧾","title":"sales.csv / 約6,900行","text":"OrderID・OrderDate・ShipDate・StoreID・CustomerID・ProductID・Quantity・UnitPrice・Discount・SalesAmount","tone":"amber"},
    {"icon":"📦","title":"products.csv / 32行","text":"ProductID・ProductName・Category・SubCategory・StandardCost・ListPrice","tone":"blue"} ] }
```

```figure
{ "type":"tablediff", "arrowLabel":"型を自分で決める", "title":"読み込み時に設定する型",
  "before":{"title":"自動判定のまま（危険）","tone":"bad","head":["列","型"],"rows":[
    ["OrderDate / ShipDate","テキストのことがある"],
    ["Quantity / UnitPrice / SalesAmount","10進数"],
    ["Discount","整数に丸められる"],
    ["OrderID / StoreID / CustomerID / ProductID","数値と判定される場合がある"]]},
  "after":{"title":"明示的に設定した型","tone":"good","head":["列","設定する型"],"rows":[
    ["OrderDate / ShipDate","!日付"],
    ["Quantity / UnitPrice / SalesAmount","!整数"],
    ["Discount","!10進数"],
    ["OrderID / StoreID / CustomerID / ProductID","!テキスト"]]} }
```

## ステップ1：データを読み込む（6分）

1. **ホーム → データを取得 → テキスト/CSV** で `sales.csv` を選択
2. プレビュー右上の「ファイル発生源」が `65001: Unicode (UTF-8)` か確認
3. **「データの変換」** をクリック（「読み込み」ではありません）
4. 列見出し左のアイコンをクリックし、上図の型をすべて設定する
5. 右ペインの **クエリの設定 → プロパティ → 名前** を `Fact_売上` に変更
6. 同じ手順で `products.csv` を読み込み、名前を `Dim_商品` にする
7. **ホーム → 閉じて適用**

> [!TRAP] 「読み込み」を押してしまったとき
> **ホーム → データの変換** でいつでも Power Query エディタに戻れます。

## ステップ2：2つの表をつなぐ（4分）

1. 左端の **モデルビュー**（3つ目のアイコン）を開く
2. `Dim_商品[ProductID]` から `Fact_売上[ProductID]` への線を確認する
3. 線がなければ `Dim_商品[ProductID]` を `Fact_売上[ProductID]` へドラッグ
4. 線をダブルクリックし、下図の3項目になっているか確認する

```figure
{ "type":"pipeline", "title":"このラボのモデル", "caption":"フィルターは常に1側から多側へ流れる",
  "nodes":[
    {"id":"p","label":"Dim_商品\n32行\nマスタ＝1側","tone":"blue"},
    {"id":"f","label":"Fact_売上\n約6,900行\n実績＝多側","tone":"amber"} ],
  "edges":[{"from":"p","to":"f","label":"カテゴリを選ぶと売上が絞られる"}] }
```

```figure
{ "type":"cards", "cols":3, "title":"リレーションシップの設定値", "caption":"値をコピーせず「フィルターの通り道」を作る",
  "items":[
    {"icon":"1️⃣","title":"基数","text":"1対多（1:*）","tone":"blue"},
    {"icon":"➡","title":"クロスフィルターの方向","text":"単一","tone":"green"},
    {"icon":"✅","title":"アクティブ","text":"オン","tone":"violet"} ] }
```

## ステップ3：メジャーを3本作る（5分）

**モデリング → 新しいメジャー** で、次の3本を作ります。

```dax
総売上   = SUM( Fact_売上[SalesAmount] )
販売数量 = SUM( Fact_売上[Quantity] )
取引件数 = DISTINCTCOUNT( Fact_売上[OrderID] )
```

```figure
{ "type":"formula", "lang":"dax", "title":"メジャーの読み方",
  "code":"総売上 = SUM( Fact_売上[SalesAmount] )",
  "caption":"書式は3本とも 10進数・小数点0・桁区切りオン",
  "parts":[
    {"match":"総売上","label":"メジャー名。ビジュアルの見出しになる","tone":"blue"},
    {"match":"SUM","label":"集計方法。合計を取る","tone":"violet"},
    {"match":"Fact_売上[SalesAmount]","label":"集計する列。テーブル名を必ず付ける","tone":"amber"} ] }
```

3本とも選択し **メジャーツール → 書式** を設定します（上図の注記）。

> [!TIP] 取引件数に DISTINCTCOUNT を使う理由
> 1注文に複数明細があるため、`COUNTROWS` だと明細行数になります。

## ステップ4：KPIカードを3枚置く（5分）

1. レポートビューに戻り、キャンバスの**余白**をクリック
2. 視覚化ペインから **カード** を選び、`総売上` をフィールドにドラッグ
3. 書式ペイン（筆アイコン）→ **吹き出しの値 → フォントサイズ 32**、**カテゴリラベル**をオン
4. 同じ手順で `販売数量` `取引件数` のカードを作り、上部に横一列で並べる
5. 3枚を Ctrl で選択 → **書式（リボン）→ 配置 → 上揃え → 横方向に均等配置**

## ステップ5：グラフとスライサー（9分）

```figure
{ "type":"steps", "title":"残り3つのビジュアルの作り方", "caption":"どれも「余白をクリック→視覚化ペインで選ぶ」から",
  "items":[
    {"title":"集合横棒グラフ（4分）","text":"Y軸 = Dim_商品[Category] / X軸 = 総売上 → 右上の「…」→ 軸の並べ替え → 総売上 → 降順 → 書式ペインでデータラベルをオン","tone":"blue"},
    {"title":"折れ線グラフ（5分）","text":"X軸 = Fact_売上[OrderDate] / Y軸 = 総売上 → X軸フィールドの下矢印で「日付の階層」を選択 → 右上の下向き二重矢印で年→四半期→月とドリルダウン","tone":"green"},
    {"title":"スライサー（3分）","text":"フィールドに Fact_売上[StoreID] をドラッグ → 右上の「…」→ ドロップダウンに変更","tone":"amber"} ] }
```

```figure
{ "type":"chart", "kind":"hbar", "title":"できあがる横棒グラフのイメージ",
  "caption":"降順に並べるだけで大小が一瞬で読める",
  "categories":["家電","衣料","食品"],
  "series":[{"name":"総売上","values":[62,25,13],"tone":"blue"}],
  "highlight":0, "unit":"%" }
```

> [!TRAP] 線がギザギザになる／横棒を選ぶ理由
> 日付の階層を選べば日単位になりません。長い日本語ラベルは横棒が読みやすい。

## ステップ6：仕上げと保存（3分）

1. **挿入 → テキストボックス** でタイトル「Northstar Retail 売上ダッシュボード」を追加
2. **表示 → グリッド線を表示 / グリッドにスナップ** をオンにして位置を揃える
3. **ファイル → 名前を付けて保存** → `LAB01_売上ダッシュボード.pbix`

```figure
{ "type":"compare", "title":"よくある作り方と、このラボの作り方",
  "caption":"正しい順序で作れば後戻りが起きない",
  "panels":[
    {"title":"よくある作り方","tone":"bad",
     "items":["読み込みボタンをそのまま押す","型は自動判定に任せる","ビジュアル上で毎回SUMを選び直す","カードの位置は手でドラッグ"],
     "note":"作り直しが増える"},
    {"title":"このラボの作り方","tone":"good",
     "items":["データの変換から入る","型を明示的に決める","メジャーを1回作って使い回す","配置コマンドで整列"],
     "note":"再現性がある"} ] }
```

## 詰まったときの答え

```figure
{ "type":"cards", "cols":2, "title":"症状と対処", "caption":"ほとんどは型かフィールドの入れ違い",
  "items":[
    {"icon":"🈚","title":"日本語が文字化けする","text":"「ファイル発生源」を 65001: Unicode (UTF-8) に変更","tone":"bad"},
    {"icon":"🔗","title":"Dim_商品 に線が引かれない","text":"両テーブルの ProductID の型が違う。両方テキストにして引き直す","tone":"bad"},
    {"icon":"⬜","title":"カードに「(空白)」と出る","text":"列ではなくメジャー 総売上 を入れ直す","tone":"amber"},
    {"icon":"📊","title":"横棒が1本しか出ない","text":"Y軸に Category ではなく ProductID を入れている","tone":"amber"},
    {"icon":"📈","title":"折れ線がドリルできない","text":"X軸が「日付の階層」ではなく OrderDate 単体になっている","tone":"amber"},
    {"icon":"🎚","title":"スライサーが効かない","text":"別ページにある、または相互作用が「なし」になっている","tone":"gray"} ] }
```

## 完成チェックリスト

- [ ] 2テーブルが読み込まれ、全列に明示的な型がある
- [ ] 1対多・単一方向でつながっている
- [ ] メジャー3本に桁区切り書式が付いている
- [ ] KPIカード3枚の上端と間隔が揃っている
- [ ] 横棒グラフが売上の降順に並んでいる
- [ ] 折れ線を月レベルまでドリルダウンできる
- [ ] `S001` を選ぶとカード3枚が変わる
- [ ] `.pbix` として保存した

## 発展課題

### 課題1：粗利を出す（10分）

`Dim_商品[StandardCost]` を使い、KPIカードを4枚目として追加します。

```dax
原価合計 =
SUMX(
    Fact_売上,
    Fact_売上[Quantity] * RELATED( Dim_商品[StandardCost] )
)

粗利 = [総売上] - [原価合計]
```

```figure
{ "type":"formula", "lang":"dax", "title":"RELATED が使える理由",
  "code":"SUMX( Fact_売上, Fact_売上[Quantity] * RELATED( Dim_商品[StandardCost] ) )",
  "caption":"詳細は L0702 で扱う",
  "parts":[
    {"match":"SUMX","label":"表を1行ずつ処理して合計する","tone":"violet"},
    {"match":"Fact_売上[Quantity]","label":"その行の数量","tone":"amber"},
    {"match":"RELATED( Dim_商品[StandardCost] )","label":"多側の行から1側の原価を引いてくる","tone":"blue"} ] }
```

### 課題2：値引きの影響を見る（10分）

1. `Fact_売上[Discount]` をX軸、`総売上` をY軸にした集合縦棒グラフを作る
2. `Discount` の下矢印 → **合計をやめて「グループ化しない」** を選ぶ
3. 値引率0の売上が全体の何割かを読み取る

### 課題3：作り直す（15分）

ゼロからもう一度作ります。2回目は15分を切れるはずです。

## 次のステップ

- モデル設計の理論 → [スタースキーマ](lesson.html?id=L0601)
- 汚いデータの整形 → [LAB02](lab.html?id=LAB02)
- 本格的なスタースキーマ → [LAB03](lab.html?id=LAB03)

`.pbix` は残しておいてください。[LAB09](lab.html?id=LAB09) で計測対象にします。
