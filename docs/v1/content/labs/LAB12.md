所要120分（制限時間つき）。取得から発行までを一気通貫でやり切る総仕上げです。時間を計り、調べ物を最小限にして進めてください。
## このラボのルール
1. タイマーを120分にセットしてから始める
2. 各フェーズの制限時間を守る（できなくても次へ進む）
3. 詰まったら「詰まったときの答え」を見てよい。ただし見たことを記録する
4. 最後に採点表を埋める
```figure
{ "type":"timeline", "title":"120分のタイムボックス", "caption":"時間を超えたら未完成でも次へ。全工程に触れることが最優先",
  "items":[
    {"label":"0-25分","title":"取得と整形","text":"CSV読み込み・クレンジング・型定義","tone":"blue"},
    {"label":"25-50分","title":"モデリング","text":"スタースキーマ・日付テーブル・階層","tone":"green"},
    {"label":"50-80分","title":"DAX","text":"基礎指標・時系列・構成比・ランキング","tone":"amber"},
    {"label":"80-105分","title":"可視化","text":"3ページ・ドリルスルー・書式","tone":"violet"},
    {"label":"105-120分","title":"RLSと発行","text":"ロール定義・テスト・発行","tone":"pink"} ] }
```
## 出題シナリオ
Northstar Retail の経営企画室から依頼を受けました。

> 2024年度の売上実績を、エリア別・カテゴリ別に分析できるレポートを作ってほしい。店舗の管理職には自店のデータだけを見せたい。月次会議で使うので、前年比と目標達成率が一目で分かること。

- 使用データ：[sales.csv](data/sales.csv) / [products.csv](data/products.csv) / [customers.csv](data/customers.csv)
- 追加で [stores.csv](data/stores.csv) / [security_users.csv](data/security_users.csv)
```figure
{ "type":"chart", "kind":"hbar", "title":"PL-300 の出題比率とこの演習の配点",
  "caption":"配点は試験の比率に合わせてある。弱い領域が点数に直接現れる",
  "categories":["1. データの準備","2. データのモデル化","3. 視覚化と分析","4. 資産の管理"],
  "series":[{"name":"配点","values":[30,28,27,15],"tone":"blue"}],
  "unit":"点" }
```
## フェーズ1：取得と整形（0〜25分 / 30点）
### 課題1-1：4ファイルを読み込む（8点）
- 4つのCSVを読み込み、クエリ名を `Fact_売上` `Dim_商品` `Dim_顧客` `Dim_店舗` にする
- すべての列に明示的な型を設定する
- 自動追加された「変更された型」ステップは削除し、自分で設定し直す
```figure
{ "type":"cards", "cols":2, "title":"課題1-2 品質を確認する（6点） / 課題1-3 不要な列を落とす（6点）", "caption":"読み込んだ直後にここを済ませると、後の工程が崩れない",
  "items":[
    {"icon":"🔬","title":"課題1-2 品質を確認する（6点）","text":"列の品質・列の分布・列のプロファイルをオンにする／ステータスバーを「データセット全体に基づく」に切り替える／`Fact_売上` にエラー行・空行がないことを確認する","tone":"blue"},
    {"icon":"🗑","title":"課題1-3 不要な列を落とす（6点）","text":"`Dim_店舗[Manager]` を削除する（`ManagerEmail` は残す）／`Fact_売上[ShipDate]` は残す（非アクティブなリレーションシップで使う）","tone":"green"} ] }
```
### 課題1-4：派生列を作る（10点）
- `値引前金額`：`Quantity` × `UnitPrice` ÷ ( 1 − `Discount` ) を四捨五入
- `出荷日数`：`ShipDate` − `OrderDate` の日数
```m
出荷日数 = Duration.Days( [ShipDate] - [OrderDate] )

値引前金額 = if [Discount] >= 1 then null
    else Number.Round( [Quantity] * [UnitPrice] / ( 1 - [Discount] ), 0 )
```
> [!TRAP] 値引前金額の計算
> `UnitPrice` は値引後の単価です。定価に戻すには除算が必要で、`Discount` が 1 なら0除算になります。
## フェーズ2：モデリング（25〜50分 / 28点）
### 課題2-1：日付テーブル（10点）
- `CALENDAR` で 2024/1/1〜2024/12/31 の日付テーブルを作る
- 年・月番号・月・年月・四半期・年度（4月始まり）・曜日・平日区分の列を持たせる
- 日付テーブルとしてマークし、自動の日付/時刻をオフにする
### 課題2-2：リレーションシップ（10点）
```figure
{ "type":"star", "title":"組むべきモデル", "caption":"ディメンション同士を直接つながない。すべてファクト経由",
  "fact":{"label":"Fact_売上","lines":["OrderDate / ShipDate","StoreID / CustomerID / ProductID","Quantity / SalesAmount"]},
  "dims":[
    {"label":"Dim_日付","lines":["Date / 年 / 月","年度 / 四半期"]},
    {"label":"Dim_商品","lines":["Category","SubCategory"]},
    {"label":"Dim_顧客","lines":["Segment","Region"]},
    {"label":"Dim_店舗","lines":["StoreName","Region"]} ],
  "edgeLabel":"1対多・単一" }
```
- 4本のアクティブなリレーションシップを 1対多・単一方向で作る
- `Dim_日付[Date]` → `Fact_売上[ShipDate]` の非アクティブな線を追加する
### 課題2-3：モデルを整える（8点）
- `月` を `月番号` で、`曜日` を `曜日番号` で並べ替える
- キー列（`ProductID` `CustomerID` `StoreID` `OrderID`）を非表示にする
- `商品階層`（Category → SubCategory → ProductName）を作る
- `Dim_店舗[Prefecture]` のデータカテゴリを「都道府県」にする
## フェーズ3：DAX（50〜80分 / 27点）
`_Measures` テーブルを作り、次の9本を実装します（各3点）。書式の設定漏れも減点対象です。
```figure
{ "type":"cards", "cols":3, "title":"実装する9本と要件", "caption":"依存の下にあるものから作る。上から順に書くと参照エラーで時間を溶かす",
  "items":[
    {"icon":"1️⃣","title":"総売上","text":"`SalesAmount` の合計","tone":"blue"},
    {"icon":"2️⃣","title":"販売数量","text":"`Quantity` の合計","tone":"blue"},
    {"icon":"3️⃣","title":"取引件数","text":"`OrderID` の一意な数","tone":"blue"},
    {"icon":"4️⃣","title":"粗利","text":"売上 − 原価（`StandardCost` × `Quantity`）","tone":"green"},
    {"icon":"5️⃣","title":"粗利率","text":"粗利 ÷ 売上。ゼロ除算対策込み","tone":"green"},
    {"icon":"6️⃣","title":"前年売上","text":"前年同期の売上","tone":"amber"},
    {"icon":"7️⃣","title":"前年比","text":"前年がない期間は空白にする","tone":"amber"},
    {"icon":"8️⃣","title":"売上YTD","text":"4月始まりの年度累計","tone":"amber"},
    {"icon":"9️⃣","title":"カテゴリ構成比","text":"選択範囲内での構成比","tone":"violet"} ] }
```
```figure
{ "type":"formula", "lang":"dax", "title":"この演習で最も配点が高い型",
  "code":"CALCULATE( [総売上], SAMEPERIODLASTYEAR( Dim_日付[Date] ) )",
  "caption":"CALCULATE + タイムインテリジェンス。この形を手が覚えているかが分かれ目",
  "parts":[
    {"match":"CALCULATE","label":"フィルターコンテキストを変更する唯一の関数","tone":"violet"},
    {"match":"[総売上]","label":"変更後のコンテキストで評価する式","tone":"blue"},
    {"match":"SAMEPERIODLASTYEAR( Dim_日付[Date] )","label":"日付フィルターを1年前にずらす","tone":"amber"} ] }
```
## フェーズ4：可視化（80〜105分 / 25点）
```figure
{ "type":"cards", "cols":3, "title":"3ページに何を置くか（25点）", "caption":"ページ①→②→③の順に作る。書式と代替テキストまでが得点範囲",
  "items":[
    {"icon":"📊","title":"課題4-1 ページ①「サマリー」（10点）","text":"KPIカード4枚（`総売上` `粗利率` `前年比` `取引件数`）／折れ線：月次の `総売上` と `前年売上`／横棒：エリア別 `総売上`（降順）／スライサー：`Dim_日付[年度]` `Dim_商品[Category]`／テキストボックスか動的タイトル","tone":"blue"},
    {"icon":"🧱","title":"課題4-2 ページ②「商品分析」（8点）","text":"マトリックス：`商品階層` × `総売上` `粗利率` `前年比`／`前年比` に条件付き書式（データバーまたはフォント色）／ツリーマップまたは散布図を1つ","tone":"green"},
    {"icon":"🔎","title":"課題4-3 ページ③「詳細」（7点）","text":"ドリルスルーページを作り `Dim_商品[ProductName]` をドリルスルーフィールドに設定／戻るボタンを配置／全ビジュアルに代替テキスト／ページ①にモバイルレイアウト","tone":"violet"} ] }
```
## フェーズ5：RLSと発行（105〜120分 / 15点）
### 課題5-1：RLS（10点）
- `security_users.csv` を `Dim_ユーザー権限` として読み込み、`Email` を小文字化する
- ロール `店舗担当者` を作り、`Dim_店舗` に次を設定する
```dax
Dim_店舗[StoreID] IN
    CALCULATETABLE(
        VALUES( Dim_ユーザー権限[StoreID] ),
        Dim_ユーザー権限[Email] = LOWER( USERPRINCIPALNAME() )
    )
```
- 「ロールとして表示」で `tanaka@northstar-retail.example.com` と `exec@northstar-retail.example.com` を検証する
### 課題5-2：発行（5点）
- 共有ワークスペースに発行する
- セマンティックモデルのセキュリティ画面でロールを確認する
- アプリとして発行する（対象ユーザーはビューアー）
> [!TRAP] 発行で時間切れになる典型
> フェーズ1〜3で完璧を目指すとフェーズ5に届きません。全工程に触れて8割のほうが価値があります。
## 採点表
| フェーズ | 満点 | 得点 | 参照した回数 |
|---|---|---|---|
| 1. 取得と整形 | 30 | | |
| 2. モデリング | 28 | | |
| 3. DAX | 27 | | |
| 4. 可視化 | 25 | | |
| 5. RLSと発行 | 15 | | |
| **合計** | **125** | | |

| 得点 | 判定 |
|---|---|
| 100点以上 | 実技相当は十分。あとは用語と選択肢の練習 |
| 80〜99点 | 合格圏。取りこぼした領域を1つずつ潰す |
| 60〜79点 | 該当ラボに戻って再演習を推奨 |
| 60点未満 | [LAB03](lab.html?id=LAB03)〜[LAB06](lab.html?id=LAB06) をもう一周 |
```figure
{ "type":"matrix", "title":"次にやることの決め方",
  "caption":"点数だけでなく「参照回数」を見る。参照が多い領域は、知識ではなく手が覚えていない",
  "xLabel":"参照した回数", "yLabel":"得点",
  "xLow":"少","xHigh":"多","yLow":"低","yHigh":"高",
  "quadrants":[
    {"title":"習熟済み","text":"手が覚えている。次の領域へ進む","tone":"good"},
    {"title":"知識はある","text":"手順を反復する。同じラボを時間を計って再実施","tone":"amber"},
    {"title":"未学習","text":"該当ラボとレッスンを最初から","tone":"bad"},
    {"title":"要注意","text":"調べれば分かるが定着していない。翌日にもう一度","tone":"violet"} ] }
```
## 詰まったときの答え
```figure
{ "type":"cards", "cols":2, "title":"フェーズ1・2でよく詰まる箇所", "caption":"ここで15分以上使ったら、答えを見て次へ進む",
  "items":[
    {"icon":"🔤","title":"型が勝手に変わる","text":"自動の「変更された型」ステップを削除し、自分で設定し直す","tone":"blue"},
    {"icon":"➖","title":"出荷日数が負になる","text":"`ShipDate` < `OrderDate` の行を確認。データ誤りとして除外するか記録する","tone":"blue"},
    {"icon":"➗","title":"値引前金額がエラー","text":"`Discount` が 1 の行での0除算。`if` で分岐する","tone":"blue"},
    {"icon":"📅","title":"日付テーブルが作れない","text":"`Dim_日付 = CALENDAR( DATE(2024,1,1), DATE(2024,12,31) )` から始め、`ADDCOLUMNS` を後から足す","tone":"green"},
    {"icon":"🗓","title":"年度の計算","text":"`IF( MONTH([Date]) >= 4, YEAR([Date]), YEAR([Date]) - 1 )`","tone":"green"},
    {"icon":"🔗","title":"非アクティブな線が作れない","text":"既にアクティブな線があれば、2本目は自動で非アクティブになる","tone":"green"} ] }
```
```figure
{ "type":"cards", "cols":2, "title":"フェーズ3・4・5でよく詰まる箇所", "caption":"DAXは型さえ思い出せば書ける。可視化と発行は設定場所の問題",
  "items":[
    {"icon":"💰","title":"粗利が計算できない","text":"`SUMX( Fact_売上, Fact_売上[Quantity] * RELATED( Dim_商品[StandardCost] ) )`","tone":"amber"},
    {"icon":"📉","title":"前年比が全期間空白","text":"日付テーブルとしてマークしていない","tone":"amber"},
    {"icon":"📆","title":"YTDが1月始まり","text":"`TOTALYTD( [総売上], Dim_日付[Date], \"3/31\" )`","tone":"amber"},
    {"icon":"🥧","title":"構成比が100%にならない","text":"`ALLSELECTED( Dim_商品[Category] )` を分母に使う","tone":"amber"},
    {"icon":"🎨","title":"条件付き書式にメジャーが出ない","text":"書式スタイルを「フィールド値」に変更する","tone":"violet"},
    {"icon":"🔎","title":"ドリルスルーが動かない","text":"ドリルスルー元のビジュアルに `ProductName` が含まれるか確認する","tone":"violet"},
    {"icon":"📱","title":"モバイルレイアウトの場所","text":"表示 → モバイル レイアウト。ページごとに設定する","tone":"violet"},
    {"icon":"🔐","title":"RLSで何も見えない / 全部見える","text":"メールの小文字化と権限表への存在を確認。全部見えるならロールのチェック漏れ","tone":"pink"} ] }
```
## 完成チェックリスト
- [ ] 4テーブル＋日付テーブル＋権限テーブルが揃い、全列に明示的な型がある
- [ ] モデルが星形で、すべて1対多・単一方向
- [ ] 日付テーブルとしてマーク済み、自動の日付/時刻はオフ
- [ ] メジャー9本すべてが正しい値を返し、書式が設定されている
- [ ] 3ページ構成でドリルスルーが動く
- [ ] 条件付き書式・代替テキスト・モバイルレイアウトを設定した
- [ ] RLSが2ユーザーで検証済み
- [ ] 共有ワークスペースに発行し、アプリを作成した
- [ ] 採点表を埋めた
## トラブルシューティング
| 症状 | 原因 | 対処 |
|---|---|---|
| 時間が全然足りない | 整形に時間を使いすぎ | フェーズ1は25分で必ず切る |
| フェーズ3で止まる | メジャーの型が手に入っていない | [LAB04](lab.html?id=LAB04) を時間を計って再実施 |
| 数字が合わない | リレーションシップの方向 | モデルビューで全線を目視確認 |
| 可視化が雑になる | 実装順序が決まっていない | [LAB11](lab.html?id=LAB11) で先に描く |
| RLSまで到達しない | 前半で完璧を目指した | 各フェーズ8割で次へ進む |
| 発行できない | ライセンスまたはワークスペース | Desktop 部分だけで採点（満点110点換算） |
## 発展課題
```figure
{ "type":"cards", "cols":2, "title":"発展課題", "caption":"1回やって終わりにしない。速度と再現性が実力になる",
  "items":[
    {"icon":"⏩","title":"課題1 90分で再挑戦する（90分）","text":"同じ課題を90分でやり切る。手順を思い出す時間が消えているはず","tone":"blue"},
    {"icon":"🎯","title":"課題2 弱点だけを反復する（30分）","text":"最も点数の低いフェーズを1つ選び、そこだけ3回繰り返す。全体を3回やるより効率的","tone":"green"},
    {"icon":"📝","title":"課題3 模擬試験を受ける（60分）","text":"[模擬試験](exam.html) で知識問題を確認する。実技で作れるものが試験では言葉で問われる","tone":"amber"},
    {"icon":"🏢","title":"課題4 自分の業務データでやる（180分）","text":"列名の揺れ・権限・更新の失敗など、サンプルでは起きない問題に必ず遭遇する","tone":"violet"} ] }
```
## お疲れさまでした
12本のハンズオンはこれで完了です。取得・整形・モデリング・DAX・可視化・性能改善・セキュリティ・設計・発行まで、Power BI で仕事をする一通りを実装しました。

- 試験対策の総仕上げ → [出題範囲の総ざらい](lesson.html?id=L1601) / [受験直前チェック](lesson.html?id=L1605)
- 組織で展開する段階へ → [エンタープライズ設計](lesson.html?id=L1701)
- 価値を出す進め方 → [成果を測る](lesson.html?id=L2204)

保存名：`LAB12_総合演習.pbix`
