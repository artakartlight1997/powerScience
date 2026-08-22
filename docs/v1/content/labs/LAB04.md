所要60分。[LAB03](lab.html?id=LAB03) のモデルに、実務で使う指標を10本＋発展5本入れます。

`LAB03_スタースキーマ.pbix` を開いてください。モデルが正しくないとDAXは動きません。

```figure
{"type":"flow","title":"このラボで積み上げる10本","dir":"row","caption":"下段は上段を再利用する。だから順番に作る","items":[{"label":"基礎3本","sub":"総売上 / 原価 / 粗利","tone":"blue"},
{"label":"比率2本","sub":"粗利率 / 構成比","tone":"green"},{"label":"時間3本","sub":"前年 / 前年比 / YTD","tone":"amber"},{"label":"順位2本","sub":"ランク / 累計","tone":"violet"}]}
```

## メジャー専用テーブルを作る（5分）

1. **ホーム → データの入力** で、列に何も入力せずテーブル名を `_Measures` にして「読み込む」
2. `Column1` を右クリック → **レポートビューでは非表示**
3. 以降、作ったメジャーは **メジャーツール → ホームテーブル** で `_Measures` に移す

```figure
{"type":"cards","cols":2,"title":"なぜ専用テーブルに集めるのか","caption":"_ で始まる名前はデータペインの先頭に固定される","items":[{"icon":"🗂","title":"Fact_売上 に置くと","text":"列とメジャーが混ざり、データペインで探しにくい","tone":"bad"},
{"icon":"📌","title":"_Measures に置くと","text":"メジャーだけを一望でき、名前で探せる","tone":"good"}]}
```

## 基礎4本：総売上・原価・粗利・粗利率（11分）

```dax
総売上 = SUM( Fact_売上[SalesAmount] )

原価合計 =
SUMX(
    Fact_売上,
    Fact_売上[Quantity] * RELATED( Dim_商品[StandardCost] )
)

粗利 = [総売上] - [原価合計]

粗利率 = DIVIDE( [粗利], [総売上] )
```

書式は金額が「10進数・0桁・桁区切り」、率が「パーセンテージ・1桁」です。

```figure
{"type":"formula","lang":"dax","title":"SUMX と RELATED の関係","code":"SUMX( Fact_売上, Fact_売上[Quantity] * RELATED( Dim_商品[StandardCost] ) )",
"caption":"SUMX が1行ずつ歩くから RELATED が使える","parts":[{"match":"SUMX","label":"テーブルを1行ずつ評価して合計する反復関数","tone":"violet"},
{"match":"Fact_売上,","label":"どのテーブルを1行ずつ歩くか","tone":"blue"},{"match":"Fact_売上[Quantity]","label":"今いる行の数量","tone":"green"},
{"match":"RELATED( Dim_商品[StandardCost] )","label":"今いる行に対応する1側の値を取得","tone":"amber"}]}
```

> [!TRAP] メジャーの中でいきなり `RELATED` は使えない
> `RELATED` は行コンテキストがないと動きません。`SUMX` の外に出すとエラーになります。

```figure
{"type":"cards","cols":2,"title":"この4本に埋め込んだ作法","caption":"どちらも以降の全メジャーで守る","items":[{"icon":"🔁","title":"メジャーからメジャーを呼ぶ","text":"粗利は SUM を書き直さず [総売上] - [原価合計]。定義が1か所に集まり、直すのも1本で済む","tone":"green"},
{"icon":"➗","title":"割り算は必ず DIVIDE","text":"分母が0や空白のとき / は無限大やエラーを返す。DIVIDE は空白を返す。第3引数で代替値も指定できる","tone":"blue"}]}
```

## 時間3本：前年・前年比・年度累計（15分）

```dax
前年売上 = CALCULATE( [総売上], SAMEPERIODLASTYEAR( Dim_日付[Date] ) )

前年比増減率 =
VAR 今年 = [総売上]
VAR 前年 = [前年売上]
RETURN
    IF(
        ISBLANK( 前年 ) || 前年 = 0,
        BLANK(),
        DIVIDE( 今年 - 前年, 前年 )
    )

売上YTD = TOTALYTD( [総売上], Dim_日付[Date], "3/31" )
```

Northstar Retail は4月始まりです。第3引数 `"3/31"` が年度末日にあたります。

```figure
{"type":"cards","cols":3,"title":"時間3本で押さえること","caption":"PL-300「2.4 タイムインテリジェンス」の中心論点","items":[{"icon":"📅","title":"動作の3条件","text":"専用の日付テーブルがある／日付テーブルとしてマーク済み／日付に抜けがない。1つ欠けると結果は空白","tone":"amber"},
{"icon":"⭕","title":"0ではなくBLANK()","text":"前年がない期間に0を返すと折れ線が0まで急落し「前年比0%」と誤読される。BLANK()なら線が途切れる","tone":"violet"},
{"icon":"🗓","title":"年度末日の指定","text":"TOTALYTD の第3引数を省くと暦年（12/31締め）になる","tone":"blue"}]}
```

確認はマトリックスで行います。

1. 行に `Dim_日付[年]` → `Dim_日付[月]`、値に `総売上` と `前年売上` を置く
2. データの最初の年で `前年売上` が空白になることを見る
3. 行を `Dim_日付[年度]` → `Dim_日付[月]` に変え、`売上YTD` が4月から積み上がることを見る

## 構成比：ALL と ALLSELECTED（8分）

```dax
カテゴリ構成比 =
DIVIDE(
    [総売上],
    CALCULATE( [総売上], ALLSELECTED( Dim_商品[Category] ) )
)

カテゴリ構成比_ALL =
DIVIDE( [総売上], CALCULATE( [総売上], ALL( Dim_商品[Category] ) ) )
```

テーブルに `Category` と2本を並べ、カテゴリスライサーで2つだけ選んでください。

```figure
{"type":"compare","title":"ALL と ALLSELECTED","caption":"「何に対する割合か」で選ぶ","panels":[{"title":"ALL","tone":"blue","items":["スライサーの選択も無視する","分母は常に全カテゴリの合計","選択2件の構成比合計は100%未満"],"note":"全社比を出したいとき"},
{"title":"ALLSELECTED","tone":"green","items":["ビジュアル内のフィルターだけ無視する","分母は「今見えている範囲」の合計","選択2件の構成比合計は100%"],"note":"画面内比を出したいとき"}]}
```

## ランキング：RANKX（8分）

```dax
商品ランク =
IF(
    ISBLANK( [総売上] ),
    BLANK(),
    RANKX( ALL( Dim_商品[ProductName] ), [総売上], , DESC, DENSE )
)
```

```figure
{"type":"formula","lang":"dax","title":"RANKX の5つの引数","code":"RANKX( ALL( Dim_商品[ProductName] ), [総売上], , DESC, DENSE )",
"caption":"「何の中での順位か」を第1引数で明示する","parts":[{"match":"ALL( Dim_商品[ProductName] )","label":"第1：順位を付ける母集団","tone":"violet"},
{"match":"[総売上]","label":"第2：順位の基準になる式","tone":"blue"},{"match":"DESC","label":"第4：大きいほうが1位","tone":"amber"},{"match":"DENSE","label":"第5：同順位の次を飛ばさない（1,2,2,3）","tone":"green"}]}
```

> [!TRAP] 第1引数の `ALL` を忘れると全部1位になる
> 各行では商品が1つに絞られているため、母集団が1件になってしまうからです。

## 累計：Running Total（8分）

```dax
売上累計 =
VAR 現在日付 = MAX( Dim_日付[Date] )
RETURN
    CALCULATE(
        [総売上],
        Dim_日付[Date] <= 現在日付,
        ALL( Dim_日付 )
    )
```

折れ線のX軸に `Dim_日付[年月]`、Y軸に `売上累計` を置くと右肩上がりになります。

```figure
{"type":"steps","title":"累計メジャーの3手順","caption":"移動平均・期首残高にも流用できる型","items":[{"title":"現在位置を捕まえる","text":"VAR 現在日付 = MAX( Dim_日付[Date] ) で、今いる行の日付を先に確保する","tone":"blue"},
{"title":"日付フィルターを解除する","text":"ALL( Dim_日付 ) で「今月だけ」という制約を外す","tone":"amber"},{"title":"新しい条件を掛け直す","text":"Dim_日付[Date] <= 現在日付 で期首からの範囲を指定する","tone":"green"}]}
```

> [!TRAP] `VAR` を使わないと全行が同じ値になる
> `MAX` を直接書くと `ALL` 適用後に評価され、常に最終日を返します。

## 発展：さらに5本

```dax
客単価 = DIVIDE( [総売上], DISTINCTCOUNT( Fact_売上[OrderID] ) )

新規顧客数 =
VAR 期間開始 = MIN( Dim_日付[Date] )
VAR 現在顧客 = VALUES( Fact_売上[CustomerID] )
VAR 過去顧客 =
    CALCULATETABLE(
        VALUES( Fact_売上[CustomerID] ),
        Dim_日付[Date] < 期間開始,
        ALL( Dim_日付 )
    )
RETURN
    COUNTROWS( EXCEPT( 現在顧客, 過去顧客 ) )

売上_7日移動平均 =
AVERAGEX(
    DATESINPERIOD( Dim_日付[Date], MAX( Dim_日付[Date] ), -7, DAY ),
    [総売上]
)

値引額 =
SUMX(
    Fact_売上,
    Fact_売上[Quantity] * ( RELATED( Dim_商品[ListPrice] ) - Fact_売上[UnitPrice] )
)

前年比_色 =
VAR 率 = [前年比増減率]
RETURN
    SWITCH( TRUE(),
        ISBLANK( 率 ),  "#8A93A6",
        率 >= 0.1,      "#14926B",
        率 >= 0,        "#8FBF5A",
        率 >= -0.1,     "#C77700",
        "#D33A4B"
    )
```

```figure
{"type":"cards","cols":3,"title":"発展5本の読みどころ","caption":"どれも定型。丸ごと覚えて使い回す","items":[{"icon":"🆕","title":"EXCEPT で新規判定","text":"「A にあって B にない行」を返す。今期買った人から過去に買った人を引けば新規顧客","tone":"violet"},
{"icon":"💸","title":"値引額","text":"定価 ListPrice と実売単価 UnitPrice の差が、値引きで失った金額","tone":"amber"},{"icon":"🎨","title":"SWITCH( TRUE(), … )","text":"上から順に評価し最初に真になった値を返す。IF の入れ子より読みやすい分岐の標準形","tone":"green"}]}
```

`前年比_色` は、テーブルの **条件付き書式 → フォントの色 → 書式スタイル「フィールド値」** に指定します。

## 完成チェックリスト

- [ ] すべてのメジャーが `_Measures` にまとまっている
- [ ] 金額に桁区切り、比率にパーセンテージ書式が付いている
- [ ] 前年データがない期間で前年比が空白になる
- [ ] スライサーを変えても ALLSELECTED 版の構成比合計が100%
- [ ] ランキングが1位から付き、売上のない商品は空白
- [ ] `売上累計` が単調増加になっている
- [ ] `売上YTD` が4月にリセットされる
- [ ] メジャー名から計算内容が推測できる

## トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| `RELATED` でエラー | 行コンテキストがない／方向が逆 | `SUMX` の中で使い、1対多・単一方向を確認 |
| 前年売上が全部空白 | 日付テーブルとしてマークしていない | LAB03 のステップ2を実施 |
| 前年売上が一部だけ空白 | 日付テーブルに抜けがある | `CALENDAR` を年初〜年末に広げる |
| 累計が累計にならない | `ALL( Dim_日付 )` を忘れている | 引数に追加 |
| 累計が全行で同じ値 | `VAR` を使わず `MAX` を直接書いた | `VAR 現在日付` に置き換える |
| ランクが全部1 | `RANKX` の第1引数に `ALL` がない | 母集団を明示する |
| YTDが1月始まり | 第3引数を省略した | `"3/31"` を指定 |
| 総計行の値がおかしい | 行単位の計算を総計でも実行している | `HASONEVALUE` で分岐する |

```dax
商品ランク_総計対応 =
IF( HASONEVALUE( Dim_商品[ProductName] ), [商品ランク], BLANK() )
```

## 発展課題

### 課題1：値引きが粗利に与える影響を測る（15分）

```dax
値引前粗利 = [粗利] + [値引額]
```

散布図のX軸に `値引額`、Y軸に `粗利率`、詳細に `Dim_商品[ProductName]` を置きます。

値引きしても粗利率が落ちない商品と、値引きが粗利を食っている商品が分離します。

### 課題2：曜日別の売れ方を調べる（10分）

`Dim_日付[曜日]` を軸にした縦棒グラフで `総売上` を見ます。月曜から並べば並べ替え列が効いています。

`Dim_日付[平日区分]` をスライサーに置き、平日と週末で売れ筋が変わるかを確認します。

### 課題3：メジャーの依存関係を図に描く（10分）

15本の依存を紙に描きます。`粗利率` → `粗利` → `総売上` / `原価合計` のように矢印でつなぎます。

## 次のステップ

- 可視化へ → [LAB05](lab.html?id=LAB05)
- 上級指標20本へ → [LAB08](lab.html?id=LAB08)
- 理論を固める → [フィルターコンテキスト](lesson.html?id=L0801) / [VARの使い方](lesson.html?id=L0705)

保存名：`LAB04_DAXメジャー.pbix`
