所要45分。スタースキーマと日付テーブルを実データで実装します。

以降のラボはこのモデルの上に積み上がります。

## このラボのゴール

4つのCSVから、日付テーブルを含む完全なスタースキーマを構築します。

```figure
{ "type":"star", "title":"完成形のモデル", "caption":"中央に数値、周囲に「いつ・どこで・誰が・何を」",
  "fact":{"label":"Fact_売上","lines":["OrderDate / StoreID","CustomerID / ProductID","Quantity / SalesAmount","約6,900行"]},
  "dims":[
    {"label":"Dim_日付","lines":["Date / 年 / 月","四半期 / 年度"]},
    {"label":"Dim_商品","lines":["ProductName","Category / SubCategory"]},
    {"label":"Dim_顧客","lines":["CustomerName","Segment / Region"]},
    {"label":"Dim_店舗","lines":["StoreName","Prefecture / Region"]} ],
  "edgeLabel":"1対多・単一方向" }
```

## ステップ1：4つのテーブルを読み込む（8分）

各ファイルを **データを取得 → テキスト/CSV → データの変換** で読み込みます。

```figure
{ "type":"cards", "cols":4, "title":"読み込む4ファイルとクエリ名", "caption":"ファクト1つ＋ディメンション3つ",
  "items":[
    {"icon":"🧾","title":"sales.csv → Fact_売上","text":"約6,900行の売上明細。ファクト（実績）","tone":"amber"},
    {"icon":"📦","title":"products.csv → Dim_商品","text":"32商品。ProductName / Category / SubCategory","tone":"blue"},
    {"icon":"👤","title":"customers.csv → Dim_顧客","text":"600顧客。Segment / Region / Prefecture","tone":"violet"},
    {"icon":"🏪","title":"stores.csv → Dim_店舗","text":"14店舗。StoreName / Prefecture / Region","tone":"green"} ] }
```

1. 4ファイルを個別に読み込み、右ペインでクエリ名を上表のとおりに変更する
2. 日付列 `OrderDate` `ShipDate` `SignupDate` `OpenDate` が日付型かを確認する
3. `Dim_店舗` の `Manager` 列を削除する（`ManagerEmail` は [LAB06](lab.html?id=LAB06) で使うので残す）
4. **ホーム → 閉じて適用**

> [!TRAP] `Prefecture` の全角ダッシュ
> `stores.csv` の `S014 オンライン` は `Prefecture` が `—` です。地図ビジュアルでは除外してください。

```figure
{ "type":"compare", "title":"使わない列を残す / 消す", "caption":"「後で使うかも」で残すとモデルは太る一方",
  "panels":[
    {"title":"残したまま","tone":"bad",
     "items":["列単位の圧縮が効きにくい","ファイルサイズが増える","更新時間が伸びる","作る人がどの列を使うか迷う"],
     "note":"Excelの発想"},
    {"title":"使う列だけ残す","tone":"good",
     "items":["圧縮が効いて軽くなる","更新が速い","必要になったら足せばよい","選択肢が少なく事故が減る"],
     "note":"L1402 で詳説"} ] }
```

## ステップ2：日付テーブルを作る（10分）

**モデリング → 新しいテーブル** で次を入力します。

```dax
Dim_日付 =
VAR MinDate = MIN( Fact_売上[OrderDate] )
VAR MaxDate = MAX( Fact_売上[OrderDate] )
RETURN
ADDCOLUMNS(
    CALENDAR( DATE( YEAR( MinDate ), 1, 1 ), DATE( YEAR( MaxDate ), 12, 31 ) ),
    "年",           YEAR( [Date] ),
    "月番号",       MONTH( [Date] ),
    "月",           FORMAT( [Date], "M月" ),
    "年月",         FORMAT( [Date], "YYYY/MM" ),
    "四半期",       "Q" & ROUNDUP( MONTH( [Date] ) / 3, 0 ),
    "年度",         IF( MONTH( [Date] ) >= 4, YEAR( [Date] ), YEAR( [Date] ) - 1 ),
    "年度月番号",   IF( MONTH( [Date] ) >= 4, MONTH( [Date] ) - 3, MONTH( [Date] ) + 9 ),
    "曜日番号",     WEEKDAY( [Date], 2 ),
    "曜日",         FORMAT( [Date], "aaa" ),
    "平日区分",     IF( WEEKDAY( [Date] , 2 ) >= 6, "週末", "平日" )
)
```

```figure
{ "type":"formula", "lang":"dax", "title":"日付テーブルの骨格",
  "code":"ADDCOLUMNS( CALENDAR( 開始日, 終了日 ), \"年\", YEAR( [Date] ) )",
  "caption":"連続した日付を作り、属性を足す。この2段構えが定石",
  "parts":[
    {"match":"ADDCOLUMNS","label":"既存テーブルに列を足して新しいテーブルを返す","tone":"violet"},
    {"match":"CALENDAR( 開始日, 終了日 )","label":"1日の抜けもない連続した日付を作る","tone":"blue"},
    {"match":"YEAR( [Date] )","label":"各行の日付から属性を計算する","tone":"amber"} ] }
```

続けて2つの設定を行います。

1. `Dim_日付` を選択 → **テーブルツール → 日付テーブルとしてマーク** → 日付列に `Date` を指定
2. **ファイル → オプションと設定 → オプション → 現在のファイル → データの読み込み** で「自動の日付/時刻」のチェックを外す

```figure
{ "type":"cards", "cols":2, "title":"この2設定が効くところ", "caption":"どちらもLAB04の前年比が動くかを左右する",
  "items":[
    {"icon":"📅","title":"日付テーブルとしてマーク","text":"SAMEPERIODLASTYEAR などタイムインテリジェンス関数が正しく動くようになる","tone":"blue"},
    {"icon":"🧹","title":"自動の日付/時刻をオフ","text":"日付列1つにつき隠れた日付テーブルが1つ作られる無駄が消え、モデルが軽くなる","tone":"green"} ] }
```

> [!WARN] オフにすると「日付の階層」が消える
> [LAB01](lab.html?id=LAB01) のレポートは `Dim_日付[年]` `Dim_日付[月]` に置き換えます。

## ステップ3：リレーションシップを作る（8分）

モデルビューで次の4本を作ります（自動検出済みなら設定の確認だけ）。

```figure
{ "type":"pipeline", "title":"作る4本のリレーションシップ", "caption":"すべて 1対多・単一方向・アクティブ",
  "nodes":[
    {"id":"d","label":"Dim_日付[Date]","tone":"blue"},
    {"id":"p","label":"Dim_商品[ProductID]","tone":"violet"},
    {"id":"c","label":"Dim_顧客[CustomerID]","tone":"pink"},
    {"id":"s","label":"Dim_店舗[StoreID]","tone":"green"},
    {"id":"f","label":"Fact_売上","tone":"amber"} ],
  "edges":[
    {"from":"d","to":"f","label":"→ OrderDate"},
    {"from":"p","to":"f","label":"→ ProductID"},
    {"from":"c","to":"f","label":"→ CustomerID"},
    {"from":"s","to":"f","label":"→ StoreID"}] }
```

1. 各線をダブルクリックし、基数「1対多」と方向「単一」を目視で確認する
2. `Dim_日付[Date]` から `Fact_売上[ShipDate]` へも線を引く（自動的に非アクティブ＝点線になる）

> [!TRAP] 自動検出は「多対多」を作ることがある
> ディメンション側にキーの重複があると多対多になり、動いたまま数字がずれ続けます。

出荷日ベースで見たいときは、次のメジャーで一時的に切り替えます。

```dax
出荷ベース売上 =
CALCULATE(
    [総売上],
    USERELATIONSHIP( Dim_日付[Date], Fact_売上[ShipDate] )
)
```

```figure
{ "type":"compare", "title":"フラット1枚表 vs スタースキーマ", "caption":"形が変わると、できることが変わる",
  "panels":[
    {"title":"フラットな1枚表","tone":"bad",
     "items":["商品名が約6,900回繰り返される","売上0の商品は一覧に出てこない","顧客セグメント別の顧客数を数えられない","列を足すたびにファイルが太る"],
     "note":"Excelの延長線上"},
    {"title":"スタースキーマ","tone":"good",
     "items":["商品名は32行に1回だけ持つ","全32商品を一覧できる","顧客テーブルを直接数えられる","DAXが素直に書ける"],
     "note":"Power BIの前提"} ] }
```

```figure
{ "type":"tree", "title":"アクティブな経路は常に1本だけ", "root":{"label":"Dim_日付 と Fact_売上 の間"},
  "children":[
    {"label":"OrderDate（実線）","sub":"アクティブ。既定で使われる","tone":"good"},
    {"label":"ShipDate（点線）","sub":"非アクティブ。USERELATIONSHIP で呼ぶ","tone":"amber"} ] }
```

## ステップ4：モデルを磨く（8分）

```figure
{ "type":"steps", "title":"5つの仕上げ", "caption":"ここを飛ばすと作るたびに小さな事故が起きる",
  "items":[
    {"title":"並べ替え列","text":"Dim_日付[月] を [月番号] で、[曜日] を [曜日番号] で並べ替える。列を選択 → 列ツール → 列で並べ替え。未設定だと「1月, 10月, 11月, 12月, 2月…」の文字列順になる","tone":"blue"},
    {"title":"キー列を非表示","text":"Fact_売上[ProductID] [CustomerID] [StoreID] [OrderID]、Dim_日付[月番号] [曜日番号] [年度月番号] を右クリック → レポートビューでは非表示","tone":"green"},
    {"title":"階層を作る","text":"Dim_商品[Category] を右クリック → 階層の作成 →『商品階層』。SubCategory と ProductName をドラッグ。Dim_店舗 も Region → Prefecture → StoreName で『地域階層』","tone":"violet"},
    {"title":"データカテゴリ","text":"Dim_店舗[Prefecture] を選択 → 列ツール → データカテゴリ → 都道府県。地図ビジュアルが認識できるようになる","tone":"amber"},
    {"title":"書式","text":"Fact_売上[SalesAmount] と [UnitPrice] に桁区切り・小数点0桁。列に設定すればどのビジュアルにも効く","tone":"pink"} ] }
```

非表示は親切心ではなく設計。見える列が少ないほど誤用が減ります。

## ステップ5：動作確認（8分）

```dax
総売上 = SUM( Fact_売上[SalesAmount] )
```

新しいレポートページに、次の4つを配置します。

1. **マトリックス**：行 `Dim_店舗[Region]` / 列 `Dim_日付[年]` / 値 `総売上`
2. **横棒グラフ**：Y軸 `Dim_商品[Category]` / X軸 `総売上`
3. **スライサー**：`Dim_日付[年月]`
4. **スライサー**：`Dim_顧客[Segment]`

4つが互いに連動すれば、モデルは正しく組めています。

```figure
{ "type":"interactive", "widget":"star-explorer", "title":"フィルターの伝播を確かめる",
  "caption":"ディメンションを選ぶと、どの経路でファクトが絞られるかが見える" }
```

## 完成チェックリスト

- [ ] モデル図が「星」の形（ディメンション同士が直接つながっていない）
- [ ] リレーションシップはすべて 1対多・単一方向
- [ ] `Dim_日付` が日付テーブルとしてマークされている
- [ ] 自動の日付/時刻がオフ
- [ ] 月と曜日が正しい順序で並ぶ
- [ ] キー列が非表示になっている
- [ ] `商品階層` と `地域階層` が使える
- [ ] `ShipDate` への非アクティブなリレーションシップがある
- [ ] `LAB03_スタースキーマ.pbix` として保存した

## トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| リレーションシップが作れない | 両側の列の型が違う | Power Query で両方テキスト型に統一 |
| 「多対多」になる | ディメンション側にキーの重複 | 重複の削除を実行 |
| 月が「1月, 10月, 11月…」の順 | 並べ替え列が未設定 | `月` を `月番号` で並べ替え |
| 「循環依存が検出されました」 | 並べ替え列が相互参照 | `月番号` の並べ替えを既定に戻す |
| スライサーが効かない | リレーションシップがない／方向が逆 | 1側から多側へ引き直す |
| `Dim_日付` の作成でエラー | `OrderDate` が日付型でない | Power Query で日付型にして再作成 |
| 前年比が常に空白 | 日付テーブルとしてマークしていない | ステップ2のマーク作業を実行 |

## 発展課題

### 課題1：売上ゼロの商品を見つける（10分）

```dax
販売実績 = IF( ISBLANK( [総売上] ), "実績なし", "あり" )
```

テーブルに `Dim_商品[ProductName]` と `販売実績` を置き、年で絞ります。

フラットテーブルではこの表示ができません。売れていない商品は1行も存在しないからです。

### 課題2：伝播を予想してから確かめる（10分）

顧客セグメントで「プラチナ」を選ぶと商品名の表は絞られるか。予想を書いてから試します。

答えは「絞られない」。顧客 → 売上 は流れますが、売上 → 商品 へは逆流しないためです。

理屈は [双方向の罠](lesson.html?id=L1202) で扱います。

### 課題3：粒度の違うファクトを足す（15分）

「店舗 × 月」の売上目標を追加する場面を、モデル図として紙に描いてください。

正解は `Dim_日付` と `Dim_店舗` を両方のファクトから共有すること。ファクト同士は直接つなぎません。

### 課題4：モデルを日本語化する（10分）

すべての列名を日本語に変更します（`ProductName` → `商品名` など）。

リレーションシップとメジャーは自動的に追従します。

## 次のステップ

このモデルで [LAB04](lab.html?id=LAB04) のDAXメジャーを実装します。

`LAB03_スタースキーマ.pbix` は LAB04・LAB05・LAB06・LAB08 の起点です。
