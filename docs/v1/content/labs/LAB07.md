所要75分。毎月届く同じ形式のファイルを、人の手を介さず取り込む仕組みを作ります。

## このラボのゴール
```figure
{ "type":"stack", "title":"作るパイプラインの3層構造", "caption":"層を分けると、壊れた場所がすぐ特定できる",
  "layers":[
    {"label":"出力層","sub":"Fact_売上 / Dim_商品。モデルに読み込む最終形","tone":"pink"},
    {"label":"変換層","sub":"fn_月次売上変換。1ファイルを整える関数","tone":"amber"},
    {"label":"取得層","sub":"pSourceFolder + Folder.Files。どこから読むかだけを決める","tone":"blue"} ] }
```

## 準備（10分）
[sales.csv](data/sales.csv) を月別に分割したファイルを用意します。

1. 作業フォルダーを作る（例：`C:\PBI\月次売上\`）
2. `sales.csv` を複製し、`2024-01.csv` `2024-02.csv` `2024-03.csv` の3つにする
3. それぞれを開き、該当月の行だけ残す
4. 検証用に `2024-99_broken.csv` を作り、1行目に `これは壊れたファイルです` とだけ書く

```figure
{ "type":"compare", "title":"異常系のテストデータを最初に作る", "caption":"正常系だけ動く仕組みは、本番で必ず止まる",
  "panels":[
    {"title":"正常系だけで作る","tone":"bad","note":"よくある失敗","items":["3ファイルとも成功して安心する","本番で1ファイル崩れて全社が止まる"]},
    {"title":"壊れたファイルを先に置く","tone":"good","note":"推奨","items":["止まらない設計を最初から強制できる","列の増減も同じ枠で扱える"]} ] }
```

## ステップ1：パラメーターを作る（5分）
1. Power BI Desktop → **ホーム → データの変換**
2. Power Query エディタで **ホーム → パラメーターの管理 → 新しいパラメーター**

| 項目 | 値 |
|---|---|
| 名前 | `pSourceFolder` |
| 種類 | テキスト |
| 推奨される値 | 任意の値 |
| 現在の値 | `C:\PBI\月次売上\` |

3. 同じ手順で `pMinDate`（日付型、現在の値 `2024-01-01`）も作る

```figure
{ "type":"cards", "cols":3, "title":"パラメーターにしておく価値", "caption":"パスは式ではなく、値として1か所に置く",
  "items":[
    {"icon":"🪝","title":"末尾の `\\` を統一する","text":"`C:\\PBI\\月次売上` と `...売上\\` の混在は `...売上2024-01.csv` を生む。末尾に必ず `\\` を付けると決める","tone":"bad"},
    {"icon":"🔁","title":"環境を切り替える","text":"開発フォルダーと本番フォルダーを、値の差し替えだけで往復できる","tone":"blue"},
    {"icon":"☁","title":"Desktopを開かずに直す","text":"Power BI Service のセマンティックモデル設定から値を変更できる。PL-300 の頻出文脈","tone":"violet"} ] }
```

## ステップ2：1ファイル分の整形を作る（12分）
1. **新しいソース → テキスト/CSV** で `2024-01.csv` を選択
2. **データの変換** を押す
3. 1行目をヘッダーとして使用する
4. 各列の型を設定する（日付・整数・10進数・テキスト）
5. `Discount` が空欄の行を 0 に置換する
6. クエリ名を `サンプル月次` にする
7. 数式バー左の **詳細エディタ** を開く

```m
let
    ソース = Csv.Document( File.Contents( "C:\PBI\月次売上\2024-01.csv" ),
        [Delimiter = ",", Columns = 10, Encoding = 65001, QuoteStyle = QuoteStyle.None] ),
    ヘッダー昇格 = Table.PromoteHeaders( ソース, [PromoteAllScalars = true] ),
    型変更 = Table.TransformColumnTypes( ヘッダー昇格,
        {{"OrderID", type text}, {"OrderDate", type date}, {"Quantity", Int64.Type}} )
in
    型変更
```

## ステップ3：カスタム関数に変える（15分）
詳細エディタを開き、全体を次で置き換えます。

```m
( ファイル as binary ) as table =>
let
    ソース = Csv.Document( ファイル,
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv] ),
    ヘッダー昇格 = Table.PromoteHeaders( ソース, [PromoteAllScalars = true] ),
    空行除去 = Table.SelectRows( ヘッダー昇格,
        each not List.IsEmpty( List.RemoveMatchingItems( Record.FieldValues( _ ), {"", null} ) ) ),
    型変更 = Table.TransformColumnTypes( 空行除去, {
        {"OrderID", type text}, {"OrderDate", type date}, {"ShipDate", type date},
        {"StoreID", type text}, {"CustomerID", type text}, {"ProductID", type text},
        {"Quantity", Int64.Type}, {"UnitPrice", Int64.Type},
        {"Discount", type number}, {"SalesAmount", Int64.Type} }),
    値引補完 = Table.ReplaceValue( 型変更, null, 0, Replacer.ReplaceValue, {"Discount"} )
in
    値引補完
```

クエリ名を `fn_月次売上変換` に変更します。アイコンが `fx` になれば成功です。

```figure
{ "type":"formula", "lang":"m", "title":"カスタム関数の形",
  "code":"( ファイル as binary ) as table => let ... in 結果",
  "caption":"引数を受け取って表を返す。クエリとの違いは、この矢印だけ",
  "parts":[
    {"match":"( ファイル as binary )","label":"引数。呼び出すときに渡す値と型","tone":"blue"},
    {"match":"as table","label":"戻り値の型。誤用に早く気づける","tone":"green"},
    {"match":"=>","label":"これがあるとクエリではなく関数になる","tone":"violet"},
    {"match":"let ... in 結果","label":"中身は普通のクエリと同じ","tone":"amber"} ] }
```

```figure
{ "type":"tablediff", "title":"関数化で必ず直す1か所", "arrowLabel":"引数に置き換える",
  "caption":"消し忘れると、全ファイルの中身が同じになる",
  "before":{"title":"クエリのまま（固定）","tone":"bad","head":["書き方","結果"],"rows":[["Csv.Document( !File.Contents(\"C:\\...\\2024-01.csv\") )","常に1月のファイルを読む"],["呼び出し","引数を渡しても無視される"]]},
  "after":{"title":"関数（可変）","tone":"good","head":["書き方","結果"],"rows":[["Csv.Document( !ファイル )","渡されたファイルを読む"],["呼び出し","fn_月次売上変換( [Content] )"]]} }
```

> [!TIP] GUIからも作れる
> クエリを右クリック → **関数の作成**。ただしパラメーター依存が残るため、まずは手書きが近道です。

## ステップ4：フォルダーから全ファイルを読む（12分）
1. **新しいソース → その他 → フォルダー**
2. パスに `pSourceFolder` は指定できないため、いったん適当なパスで進める
3. プレビュー画面で **データの変換** を選ぶ（「結合」は押さない）
4. 詳細エディタを開き、全体を次で置き換える

```m
let
    ソース = Folder.Files( pSourceFolder ),
    CSVのみ = Table.SelectRows( ソース, each Text.Lower( [Extension] ) = ".csv" ),
    変換適用 = Table.AddColumn( CSVのみ, "変換結果",
        each try fn_月次売上変換( [Content] ) otherwise null, type nullable table ),
    成功のみ = Table.SelectRows( 変換適用, each [変換結果] <> null ),
    必要列 = Table.SelectColumns( 成功のみ, {"Name", "変換結果"} ),
    展開 = Table.ExpandTableColumn( 必要列, "変換結果",
        {"OrderID","OrderDate","ShipDate","StoreID","CustomerID","ProductID","Quantity","UnitPrice","Discount","SalesAmount"} ),
    ソースファイル列 = Table.RenameColumns( 展開, {{"Name", "ソースファイル"}} ),
    期間フィルター = Table.SelectRows( ソースファイル列, each [OrderDate] >= pMinDate )
in
    期間フィルター
```

5. クエリ名を `Fact_売上` にする

```figure
{ "type":"pipeline", "title":"データが流れる経路", "caption":"整形を関数に閉じ込めると、上流と下流を別々に直せる",
  "nodes":[
    {"id":"p","label":"pSourceFolder\nパラメーター","tone":"gray"},
    {"id":"f","label":"Folder.Files\nファイル一覧","tone":"blue"},
    {"id":"fn","label":"fn_月次売上変換\n1ファイルを整形","tone":"violet"},
    {"id":"t","label":"ExpandTableColumn\n縦に積む","tone":"green"},
    {"id":"o","label":"Fact_売上\nモデルへ","tone":"amber"} ],
  "edges":[ {"from":"p","to":"f","label":"パスを渡す"}, {"from":"f","to":"fn","label":"Content列を1件ずつ"},
    {"from":"fn","to":"t","label":"表を返す"}, {"from":"t","to":"o","label":"読み込み"} ] }
```

```figure
{ "type":"tree", "title":"`try 式 otherwise 代替値` の分岐", "caption":"1ファイルの失敗で、全社のレポートを止めない",
  "root":{"label":"fn_月次売上変換( [Content] )"},
  "children":[
    {"label":"成功","sub":"表が返る","tone":"good","children":[{"label":"成功のみ に残る","sub":"Fact_売上 へ"}]},
    {"label":"失敗","sub":"otherwise で null","tone":"amber","children":[{"label":"成功のみ で除外","sub":"_取込エラー一覧 で可視化"}]} ] }
```

## ステップ5：失敗したファイルを可視化する（10分）
1. `Fact_売上` を右クリック → **参照**（複製ではありません）
2. 名前を `_取込エラー一覧` に変更し、詳細エディタを次で置き換える

```m
let
    ソース = Folder.Files( pSourceFolder ),
    CSVのみ = Table.SelectRows( ソース, each Text.Lower( [Extension] ) = ".csv" ),
    判定 = Table.AddColumn( CSVのみ, "結果", each try fn_月次売上変換( [Content] ), type record ),
    展開 = Table.ExpandRecordColumn( 判定, "結果", {"HasError", "Error"}, {"エラー有無", "エラー詳細"} ),
    失敗のみ = Table.SelectRows( 展開, each [エラー有無] = true ),
    メッセージ = Table.AddColumn( 失敗のみ, "メッセージ", each [エラー詳細][Message], type text ),
    出力 = Table.SelectColumns( メッセージ, {"Name", "メッセージ"} )
in
    出力
```

3. このクエリをモデルに読み込み、管理ページにテーブルとして置く

```figure
{ "type":"compare", "title":"参照（Reference）と複製（Duplicate）", "caption":"上流を直したときに追従するかどうかが決定的に違う",
  "panels":[
    {"title":"参照 Reference","tone":"good","note":"原則こちら",
     "items":["元クエリの結果を入力として使う","元クエリを直すと自動で追従する","変換ロジックは1か所だけ"]},
    {"title":"複製 Duplicate","tone":"bad","note":"ソースが本当に別のときだけ",
     "items":["ステップをまるごとコピーする","元を直しても追従しない","同じ修正を2か所に入れる"]} ] }
```

## ステップ6：クエリを整理する（8分）
左ペインで右クリック → **グループへ移動 → 新しいグループ**。

| グループ | 入れるクエリ | 読み込み |
|---|---|---|
| `00_パラメーター` | `pSourceFolder` `pMinDate` | しない |
| `10_関数` | `fn_月次売上変換` | しない |
| `20_ステージング` | `サンプル月次` | しない |
| `30_モデル` | `Fact_売上` `Dim_商品` など | する |
| `90_監査` | `_取込エラー一覧` | する |

読み込まないクエリは、右クリック → **読み込みを有効にする** のチェックを外します。

> [!TRAP] 読み込みを有効にしたままだと
> ステージング用クエリまでモデルに入り、データペインが散らかり更新時間も倍増します。

## ステップ7：動作を検証する（8分）
1. **ホーム → 閉じて適用**
2. `Fact_売上` の行数を確認する（テーブルビューのステータスバー）
3. `_取込エラー一覧` に `2024-99_broken.csv` が1件だけ出ていることを確認する
4. 作業フォルダーに `2024-04.csv` を追加し、**ホーム → 更新** を実行する
5. クエリを一切変更せずに4月分が増えることを確認する

## 完成チェックリスト
- [ ] `pSourceFolder` `pMinDate` がパラメーターとして存在する
- [ ] `fn_月次売上変換` が関数（`fx` アイコン）になっている
- [ ] 関数の中にハードコードされたファイルパスがない
- [ ] `Fact_売上` が `Folder.Files` から全CSVを読み、`ソースファイル` 列を持つ
- [ ] 壊れたファイルがあっても更新が完走する
- [ ] クエリがグループ分けされ、不要なものは読み込み無効。`_取込エラー一覧` に失敗ファイルが出る
- [ ] 新しい月のファイルを置くだけで取り込まれる

## トラブルシューティング
| 症状 | 原因 | 対処 |
|---|---|---|
| 全ファイルの中身が同じ | 関数内に `File.Contents("...")` が残っている | 引数 `ファイル` に置き換える |
| `pSourceFolder` が式で使えない | パラメーターではなくクエリになっている | パラメーターの管理から作り直す |
| 展開後に列が1つもない | 関数が `null` を返している | `try` を外して素のエラーを読む |
| 「列が見つかりません」 | 月によって列名が違う | `MissingField.UseNull` を使う |
| 更新が非常に遅い | ステージングも読み込んでいる | 読み込みを無効にする |
| エラー一覧が常に空 | 結果をレコードで受けていない | `type record` と `HasError` を確認 |

## 発展課題
### 課題1：ファイル名から年月を取り出す（15分）
```m
= Table.AddColumn( 前のステップ, "取込年月",
    each Date.FromText( Text.Start( [ソースファイル], 7 ) & "-01" ), type date )
```
ファイル名の年月と `OrderDate` の月が食い違うファイルを検出できます。

### 課題2：列が増えても壊れないようにする（15分）
```m
= Table.SelectColumns( 前のステップ,
    {"OrderID","OrderDate","StoreID","ProductID","Quantity","SalesAmount","Channel"},
    MissingField.UseNull )
```
存在しない `Channel` 列が `null` 列になることを確認します。

### 課題3：関数に引数を追加する（10分）
```m
( ファイル as binary, optional 区切り文字 as nullable text ) as table =>
let
    区切り = if 区切り文字 = null then "," else 区切り文字,
    ソース = Csv.Document( ファイル, [Delimiter = 区切り, Encoding = 65001] )
```
`optional` 引数は省略できます。既存の呼び出しは書き換え不要です。

## 次のステップ
- M言語と折りたたみ → [M言語の基礎](lesson.html?id=L1101) / [クエリの折りたたみ](lesson.html?id=L1103)
- DAX上級へ → [LAB08](lab.html?id=LAB08)

保存名：`LAB07_変換パイプライン.pbix`
