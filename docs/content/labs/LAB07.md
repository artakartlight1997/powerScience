所要75分。毎月届く同じ形式のファイルを、**人の手を1回も介さずに**取り込む仕組みを作ります。Power Query の「操作を記録する道具」から「プログラムを書く場所」への転換点です。

## このラボのゴール

フォルダーに月次ファイルを置くだけで取り込まれる、壊れにくい変換パイプラインを作ります。

```figure
{ "type":"stack", "title":"作るパイプラインの3層構造", "caption":"層を分けると、壊れた場所がすぐ特定できる",
  "layers":[
    {"label":"出力層","sub":"Fact_売上 / Dim_商品。モデルに読み込む最終形","tone":"pink"},
    {"label":"変換層","sub":"fn_月次売上変換。1ファイルを整える関数","tone":"amber"},
    {"label":"取得層","sub":"pSourceFolder + Folder.Files。どこから読むかだけを決める","tone":"blue"} ] }
```

到達点は次の5つです。

1. パラメーターでフォルダーパスを外出しする
2. 1ファイル分の整形をカスタム関数にする
3. フォルダー接続で全ファイルに関数を適用する
4. 壊れたファイルが混ざっても止まらないようにする
5. 取り込み結果を検証するクエリを持つ

## 準備（10分）

[sales.csv](data/sales.csv) を月別に分割したファイルを用意します。手作業で分けても構いませんが、次のように準備するのが簡単です。

1. 作業フォルダーを作る（例：`C:\PBI\月次売上\`）
2. `sales.csv` をコピーし、`2024-01.csv` `2024-02.csv` `2024-03.csv` の3つに複製する
3. それぞれを Excel かテキストエディタで開き、該当月の行だけ残す
4. さらに検証用として、`2024-99_broken.csv` を作る
   - 中身は1行目に `これは壊れたファイルです` とだけ書いた状態にする

> [!TIP] 壊れたファイルを最初から用意する
> 「正常系だけ動く仕組み」は本番で必ず止まります。**異常系のテストデータを最初に作る**のが、止まらない仕組みを作る唯一の方法です。実務では月末に1ファイルだけ列が増える、といったことが普通に起きます。

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

> [!TRAP] パスの末尾の円記号
> `C:\PBI\月次売上` と `C:\PBI\月次売上\` を混在させると、後の結合で `C:\PBI\月次売上2024-01.csv` のような壊れたパスが生まれます。**末尾に必ず `\` を付ける**と決めて統一してください。

> [!EXAM] パラメーターの用途
> PL-300 では「開発環境と本番環境でソースを切り替える」文脈で問われます。パラメーターにしておけば、Power BI Service 側のセマンティックモデル設定画面から、Desktop を開かずに値を変更できます。

## ステップ2：1ファイル分の整形を作る（12分）

まず「見本」を1つ作ります。

1. **新しいソース → テキスト/CSV** で `2024-01.csv` を選択
2. **データの変換**
3. 通常どおり整形する
   - 1行目をヘッダーとして使用
   - 各列の型を設定（日付・整数・10進数・テキスト）
   - `Discount` が空欄の行を 0 に置換
4. クエリ名を `サンプル月次` にする

この時点で、数式バーの左の **詳細エディタ** を開いてください。次のようなコードが見えるはずです。

```m
let
    ソース = Csv.Document(
        File.Contents( "C:\PBI\月次売上\2024-01.csv" ),
        [Delimiter = ",", Columns = 10, Encoding = 65001, QuoteStyle = QuoteStyle.None]
    ),
    ヘッダー昇格 = Table.PromoteHeaders( ソース, [PromoteAllScalars = true] ),
    型変更 = Table.TransformColumnTypes( ヘッダー昇格, {
        {"OrderID", type text}, {"OrderDate", type date}, {"ShipDate", type date},
        {"StoreID", type text}, {"CustomerID", type text}, {"ProductID", type text},
        {"Quantity", Int64.Type}, {"UnitPrice", Int64.Type},
        {"Discount", type number}, {"SalesAmount", Int64.Type}
    })
in
    型変更
```

> [!NOTE] `let ... in` の読み方
> `let` から `in` までが変数の定義、`in` の後ろが「このクエリの答え」です。各行の `名前 = 式` は、適用したステップ一覧に表示される1ステップに対応します。**GUIの操作は、このコードを1行ずつ書いているのと同じ**です。

## ステップ3：カスタム関数に変える（15分）

`サンプル月次` を関数に作り替えます。詳細エディタを開き、全体を次で置き換えてください。

```m
( ファイル as binary ) as table =>
let
    ソース = Csv.Document(
        ファイル,
        [Delimiter = ",", Encoding = 65001, QuoteStyle = QuoteStyle.Csv]
    ),
    ヘッダー昇格 = Table.PromoteHeaders( ソース, [PromoteAllScalars = true] ),
    空行除去 = Table.SelectRows(
        ヘッダー昇格,
        each not List.IsEmpty( List.RemoveMatchingItems( Record.FieldValues( _ ), {"", null} ) )
    ),
    型変更 = Table.TransformColumnTypes( 空行除去, {
        {"OrderID", type text}, {"OrderDate", type date}, {"ShipDate", type date},
        {"StoreID", type text}, {"CustomerID", type text}, {"ProductID", type text},
        {"Quantity", Int64.Type}, {"UnitPrice", Int64.Type},
        {"Discount", type number}, {"SalesAmount", Int64.Type}
    }),
    値引補完 = Table.ReplaceValue( 型変更, null, 0, Replacer.ReplaceValue, {"Discount"} )
in
    値引補完
```

クエリ名を `fn_月次売上変換` に変更します。左ペインのアイコンが `fx` に変わったら成功です。

```figure
{ "type":"formula", "lang":"m", "title":"カスタム関数の形",
  "code":"( ファイル as binary ) as table => let ... in 結果",
  "caption":"引数を受け取って表を返す。GUIのクエリとの違いは、この矢印だけ",
  "parts":[
    {"match":"( ファイル as binary )","label":"引数。呼び出すときに渡す値と型","tone":"blue"},
    {"match":"as table","label":"戻り値の型。書いておくと誤用に早く気づける","tone":"green"},
    {"match":"=>","label":"これがあるとクエリではなく関数になる","tone":"violet"},
    {"match":"let ... in 結果","label":"中身は普通のクエリと同じ","tone":"amber"} ] }
```

> [!TRAP] `File.Contents(...)` を消し忘れる
> 関数化するときに `Csv.Document( File.Contents( "C:\..." ) )` のままだと、引数を渡しても常に同じファイルを読みます。**引数名（`ファイル`）に置き換える**のを忘れないでください。関数を作ったのに全ファイルの中身が同じ、という症状の原因はほぼこれです。

> [!TIP] GUIから関数を作る方法もある
> クエリを右クリック → **関数の作成** を使うと、パラメーターを引数に持つ関数が自動生成されます。ただし内部でパラメーターへの依存が残るため、動きを理解するには手書きが近道です。

## ステップ4：フォルダーから全ファイルを読む（12分）

1. **新しいソース → その他 → フォルダー**
2. パスに `pSourceFolder` を指定できないため、いったん適当なパスで進める
3. プレビュー画面で **データの変換** を選ぶ（「結合」は押さない）
4. 詳細エディタを開き、全体を次で置き換える

```m
let
    ソース = Folder.Files( pSourceFolder ),
    CSVのみ = Table.SelectRows(
        ソース,
        each Text.Lower( [Extension] ) = ".csv"
    ),
    変換適用 = Table.AddColumn(
        CSVのみ,
        "変換結果",
        each try fn_月次売上変換( [Content] ) otherwise null,
        type nullable table
    ),
    成功のみ = Table.SelectRows( 変換適用, each [変換結果] <> null ),
    必要列 = Table.SelectColumns( 成功のみ, {"Name", "変換結果"} ),
    展開 = Table.ExpandTableColumn(
        必要列,
        "変換結果",
        {"OrderID","OrderDate","ShipDate","StoreID","CustomerID","ProductID","Quantity","UnitPrice","Discount","SalesAmount"}
    ),
    ソースファイル列 = Table.RenameColumns( 展開, {{"Name", "ソースファイル"}} ),
    期間フィルター = Table.SelectRows( ソースファイル列, each [OrderDate] >= pMinDate )
in
    期間フィルター
```

クエリ名を `Fact_売上` にします。

```figure
{ "type":"pipeline", "title":"データが流れる経路", "caption":"1ファイルの整形を関数に閉じ込めると、上流と下流が独立して直せる",
  "nodes":[
    {"id":"p","label":"pSourceFolder\nパラメーター","tone":"gray"},
    {"id":"f","label":"Folder.Files\nファイル一覧","tone":"blue"},
    {"id":"fn","label":"fn_月次売上変換\n1ファイルを整形","tone":"violet"},
    {"id":"t","label":"Table.ExpandTableColumn\n縦に積む","tone":"green"},
    {"id":"o","label":"Fact_売上\nモデルへ","tone":"amber"} ],
  "edges":[
    {"from":"p","to":"f","label":"パスを渡す"},
    {"from":"f","to":"fn","label":"Content列を1件ずつ"},
    {"from":"fn","to":"t","label":"表を返す"},
    {"from":"t","to":"o","label":"読み込み"} ] }
```

> [!NOTE] `try ... otherwise`
> `try 式 otherwise 代替値` は、式がエラーになったときに代替値を返します。壊れたファイル（`2024-99_broken.csv`）があっても、そのファイルだけ `null` になり、処理全体は止まりません。**1ファイルの失敗で全社のレポートを止めない**、という設計です。

## ステップ5：失敗したファイルを可視化する（10分）

`try ... otherwise` で握りつぶすと、失敗に気づけなくなります。失敗一覧を別クエリで持ちます。

1. `Fact_売上` を右クリック → **参照**（複製ではありません）
2. 名前を `_取込エラー一覧` に変更 → 詳細エディタを次で置き換える

```m
let
    ソース = Folder.Files( pSourceFolder ),
    CSVのみ = Table.SelectRows( ソース, each Text.Lower( [Extension] ) = ".csv" ),
    判定 = Table.AddColumn(
        CSVのみ,
        "結果",
        each try fn_月次売上変換( [Content] ),
        type record
    ),
    展開 = Table.ExpandRecordColumn( 判定, "結果", {"HasError", "Error"}, {"エラー有無", "エラー詳細"} ),
    失敗のみ = Table.SelectRows( 展開, each [エラー有無] = true ),
    メッセージ = Table.AddColumn( 失敗のみ, "メッセージ", each [エラー詳細][Message], type text ),
    出力 = Table.SelectColumns( メッセージ, {"Name", "メッセージ"} )
in
    出力
```

このクエリをモデルに読み込み、レポートの管理ページにテーブルとして置いておきます。行が1件でもあれば、その月の取り込みに問題があったことが一目で分かります。

```figure
{ "type":"compare", "title":"参照（Reference）と複製（Duplicate）", "caption":"上流を直したときに追従するかどうかが決定的に違う",
  "panels":[
    {"title":"参照 Reference","tone":"good",
     "items":["元クエリの結果を入力として使う","元クエリを直すと自動で追従する","変換ロジックは1か所だけ"],
     "note":"原則こちら"},
    {"title":"複製 Duplicate","tone":"bad",
     "items":["ステップをまるごとコピーする","元を直しても追従しない","同じ修正を2か所に入れる羽目になる"],
     "note":"ソースが本当に別のときだけ"} ] }
```

## ステップ6：クエリを整理する（8分）

クエリが増えたので、フォルダー分けします。左ペインで右クリック → **グループへ移動 → 新しいグループ**。

| グループ | 入れるクエリ | 読み込み |
|---|---|---|
| `00_パラメーター` | `pSourceFolder` `pMinDate` | しない |
| `10_関数` | `fn_月次売上変換` | しない |
| `20_ステージング` | `サンプル月次` | しない |
| `30_モデル` | `Fact_売上` `Dim_商品` など | する |
| `90_監査` | `_取込エラー一覧` | する |

読み込まないクエリは、右クリック → **読み込みを有効にする** のチェックを外します。

> [!TRAP] 読み込みを有効にしたままだと
> ステージング用のクエリまでモデルに入り、データペインが散らかるうえ、更新時間も倍増します。**モデルに必要なテーブルだけを読み込む**のが原則です。

## ステップ7：動作を検証する（8分）

1. **ホーム → 閉じて適用**
2. `Fact_売上` の行数を確認する（テーブルビューのステータスバー）
3. `_取込エラー一覧` に `2024-99_broken.csv` が1件だけ出ていることを確認
4. 作業フォルダーに `2024-04.csv` を追加し、**ホーム → 更新** を実行
5. **クエリを一切変更せずに**4月分が増えることを確認する

これが「毎月のファイルを自動処理する仕組み」の完成形です。

## 完成チェックリスト

- [ ] `pSourceFolder` と `pMinDate` をパラメーターとして持っている
- [ ] `fn_月次売上変換` が関数（`fx` アイコン）になっている
- [ ] 関数の中にハードコードされたファイルパスがない
- [ ] `Fact_売上` が `Folder.Files` から全CSVを読んでいる
- [ ] `ソースファイル` 列があり、どのファイル由来か追跡できる
- [ ] 壊れたファイルがあっても更新が完走する
- [ ] `_取込エラー一覧` に失敗ファイルが出る
- [ ] クエリがグループ分けされ、不要なものは読み込み無効
- [ ] 新しい月のファイルを置くだけで取り込まれる

## トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| 全ファイルの中身が同じ | 関数内に `File.Contents("...")` が残っている | 引数 `ファイル` に置き換える |
| `pSourceFolder` が式で使えない | パラメーターではなくクエリになっている | パラメーターの管理から作り直す |
| 展開後に列が1つもない | 関数が `null` を返している | `try` を外して素の状態のエラーを読む |
| 「列が見つかりません」 | 月によって列名が違う | `Table.SelectColumns( t, {...}, MissingField.UseNull )` を使う |
| 更新が非常に遅い | ステージングクエリも読み込んでいる | 読み込みを無効にする |
| Service で更新が失敗 | ローカルパスを参照している | ゲートウェイを設定するか SharePoint/OneDrive に置く |
| エラー一覧が常に空 | `try` の結果をレコードで受けていない | `type record` と `HasError` の展開を確認 |
| 型変更でエラーが大量発生 | ロケール差（日付形式） | `Table.TransformColumnTypes( t, {...}, "ja-JP" )` を指定 |

## 発展課題

### 課題1：ファイル名から年月を取り出す（15分）

`ソースファイル` 列（例：`2024-01.csv`）から年月列を作ります。

```m
= Table.AddColumn(
    前のステップ,
    "取込年月",
    each Date.FromText( Text.Start( [ソースファイル], 7 ) & "-01" ),
    type date
  )
```

ファイル名の日付と `OrderDate` の月が一致しないファイルを見つければ、担当者の入れ間違いを検出できます。

### 課題2：列が増えても壊れないようにする（15分）

`Table.SelectColumns` の第3引数に `MissingField.UseNull` を指定すると、列がないファイルでも `null` で埋めて処理を続けます。

```m
= Table.SelectColumns(
    前のステップ,
    {"OrderID","OrderDate","StoreID","ProductID","Quantity","SalesAmount","Channel"},
    MissingField.UseNull
  )
```

`Channel` 列は今のファイルには存在しません。エラーにならず `null` 列ができることを確認してください。

### 課題3：クエリの折りたたみを意識する（15分）

`Folder.Files` はファイルシステムが相手なので折りたたみは効きませんが、SQL Server が相手なら話が変わります。データソースをSQLに置き換えた場合を想定し、次のどちらが速いか考えてください。

1. 全行を読み込んでから Power Query でフィルターする
2. `Table.SelectRows` を書いて、SQL側で `WHERE` に変換させる

答えは2です。ステップを右クリックして **ネイティブクエリの表示** が有効なら、そこまで折りたたまれています。詳しくは [クエリの折りたたみ](lesson.html?id=L1103) を参照してください。

### 課題4：関数に引数を追加する（10分）

`fn_月次売上変換` に、区切り文字を選べる引数を追加してください。

```m
( ファイル as binary, optional 区切り文字 as nullable text ) as table =>
let
    区切り = if 区切り文字 = null then "," else 区切り文字,
    ソース = Csv.Document( ファイル, [Delimiter = 区切り, Encoding = 65001, QuoteStyle = QuoteStyle.Csv] ),
    ...
```

`optional` を付けた引数は省略できます。既存の呼び出し（`fn_月次売上変換( [Content] )`）を書き換えずに済むことを確認してください。

## 次のステップ

- M言語の文法を体系的に押さえるなら → [M言語の基礎](lesson.html?id=L1101)
- 折りたたみと性能を学ぶなら → [クエリの折りたたみ](lesson.html?id=L1103)
- DAX上級へ進むなら → [LAB08](lab.html?id=LAB08)

保存名：`LAB07_変換パイプライン.pbix`
