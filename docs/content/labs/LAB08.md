所要90分。[LAB04](lab.html?id=LAB04) の10本を土台に、実務で「これが書ければ困らない」20指標を一気に実装します。手を止めずに20本書き切ることが目的です。

## 準備

`LAB04_DAXメジャー.pbix` を開いてください。`総売上` `原価合計` `粗利` `粗利率` の4本が既にある前提で進めます。

```figure
{ "type":"flow", "title":"20本の内訳", "dir":"row", "caption":"上から順に難度が上がる。1〜5は準備運動、16〜20は設計力を問う",
  "items":[
    {"label":"時系列 1-6","sub":"累計 / 移動平均 / 前年比 / 前月比","tone":"blue"},
    {"label":"順位 7-9","sub":"ランキング / ABC / パレート","tone":"green"},
    {"label":"顧客 10-14","sub":"新規 / 既存 / 復活 / コホート / LTV","tone":"amber"},
    {"label":"商品 15-16","sub":"バスケット / 平均点数","tone":"violet"},
    {"label":"表現 17-20","sub":"目標 / 動的タイトル / 色 / 軸切替","tone":"pink"} ] }
```

> [!TIP] 20本を通しで書くコツ
> 1本ごとに必ずビジュアルに置いて値を確認してください。5本まとめて書いてから確認すると、どこが原因か特定できなくなります。**書く → 置く → 確かめる** を20回繰り返します。

---

## 第1群：時系列（6本）

### 1. 期間累計（期首から）

```dax
売上累計 =
VAR 現在日付 = MAX( Dim_日付[Date] )
RETURN
    CALCULATE(
        [総売上],
        Dim_日付[Date] <= 現在日付,
        REMOVEFILTERS( Dim_日付 )
    )
```

`REMOVEFILTERS` は `ALL` と同じ働きをしますが、「フィルターを消す」という意図が名前に出ます。CALCULATE の修飾子としてはこちらを推奨します。

### 2. 年度累計（4月始まり）

```dax
売上YTD = TOTALYTD( [総売上], Dim_日付[Date], "3/31" )
```

### 3. 3か月移動平均

```dax
売上_3か月移動平均 =
VAR 期間 = DATESINPERIOD( Dim_日付[Date], MAX( Dim_日付[Date] ), -3, MONTH )
VAR 合計 = CALCULATE( [総売上], 期間 )
RETURN
    DIVIDE( 合計, 3 )
```

> [!TRAP] `AVERAGEX` で書くと意味が変わる
> `AVERAGEX( DATESINPERIOD( ... ), [総売上] )` は**1日あたりの平均**を返します。日付テーブルの行は「日」だからです。月単位の移動平均が欲しいなら、3か月分を合計して3で割ります。**反復関数は「何を1行として数えるか」を必ず確認してください。**

### 4. 前年同期売上

```dax
前年売上 = CALCULATE( [総売上], SAMEPERIODLASTYEAR( Dim_日付[Date] ) )
```

### 5. 前年比増減率

```dax
前年比 =
VAR 今年 = [総売上]
VAR 前年 = [前年売上]
RETURN
    IF( ISBLANK( 前年 ) || 前年 = 0, BLANK(), DIVIDE( 今年 - 前年, 前年 ) )
```

### 6. 前月比増減率

```dax
前月売上 = CALCULATE( [総売上], DATEADD( Dim_日付[Date], -1, MONTH ) )
```

```dax
前月比 =
VAR 当月 = [総売上]
VAR 前月 = [前月売上]
RETURN
    IF( ISBLANK( 前月 ) || 前月 = 0, BLANK(), DIVIDE( 当月 - 前月, 前月 ) )
```

> [!EXAM] `DATEADD` と `PARALLELPERIOD` の違い
> `DATEADD` は**選択されている日付の集合をそのままずらす**（1月15日を選べば12月15日）。`PARALLELPERIOD` は**期間全体に広げてからずらす**（1月15日を選べば12月全体）。月次比較なら `DATEADD`、四半期の対比なら `PARALLELPERIOD` が自然です。

---

## 第2群：順位とABC分析（3本）

### 7. 商品ランキング

```dax
商品ランク =
IF(
    ISBLANK( [総売上] ),
    BLANK(),
    RANKX( ALL( Dim_商品[ProductName] ), [総売上], , DESC, DENSE )
)
```

### 8. 累積構成比（パレート）

```dax
売上累積構成比 =
VAR 現在売上 = [総売上]
VAR 全体 = CALCULATE( [総売上], REMOVEFILTERS( Dim_商品 ) )
VAR 自分以上の合計 =
    SUMX(
        FILTER( ALL( Dim_商品[ProductName] ), [総売上] >= 現在売上 ),
        [総売上]
    )
RETURN
    DIVIDE( 自分以上の合計, 全体 )
```

書式：パーセンテージ、小数点1桁。

```figure
{ "type":"chart", "kind":"bar", "title":"パレート図で読むABC分析",
  "caption":"上位数商品で売上の7割に達する。そこがAランクの境目",
  "categories":["1位","2位","3位","4位","5位","6位","7位","8位"],
  "series":[{"name":"累積構成比","values":[22,39,52,63,70,76,81,85],"tone":"blue"}],
  "highlight":4, "unit":"%" }
```

### 9. ABC区分

```dax
商品ABC =
VAR 累積 = [売上累積構成比]
RETURN
    SWITCH( TRUE(),
        ISBLANK( 累積 ), BLANK(),
        累積 <= 0.7,  "A",
        累積 <= 0.9,  "B",
        "C"
    )
```

```figure
{ "type":"formula", "lang":"dax", "title":"累積構成比の考え方",
  "code":"SUMX( FILTER( ALL( Dim_商品[ProductName] ), [総売上] >= 現在売上 ), [総売上] )",
  "caption":"「自分より売れている商品」を集めて足す。これが累積の正体",
  "parts":[
    {"match":"ALL( Dim_商品[ProductName] )","label":"全商品を母集団にする","tone":"blue"},
    {"match":"[総売上] >= 現在売上","label":"自分以上に売れている商品だけ残す","tone":"amber"},
    {"match":"SUMX","label":"残った商品の売上を合計する","tone":"violet"} ] }
```

> [!TRAP] 総計行が「C」になる
> 総計行では商品が1つに絞られていないため、`現在売上` が全社合計になり累積構成比が100%になります。`IF( HASONEVALUE( Dim_商品[ProductName] ), ... )` で総計時は空白を返すようにしてください。

---

## 第3群：顧客分析（5本）

顧客系の指標には、まず `Dim_顧客` に**計算列**を1本追加します。

```dax
初回購入日 = CALCULATE( MIN( Fact_売上[OrderDate] ) )
```

```dax
初回購入月 = FORMAT( Dim_顧客[初回購入日], "YYYY/MM" )
```

> [!NOTE] 計算列で `CALCULATE` を使う理由
> 計算列には行コンテキストしかありません。`CALCULATE` で囲むと**コンテキスト遷移**が起き、「この顧客の行」というフィルターに変換されて `Fact_売上` に伝わります。これがないと全顧客の最小日付が全行に入ります。詳しくは [コンテキスト遷移](lesson.html?id=L1302) を参照してください。

### 10. 新規顧客数

```dax
新規顧客数 =
VAR 期間開始 = MIN( Dim_日付[Date] )
VAR 今期顧客 = VALUES( Fact_売上[CustomerID] )
VAR 過去顧客 =
    CALCULATETABLE(
        VALUES( Fact_売上[CustomerID] ),
        REMOVEFILTERS( Dim_日付 ),
        Dim_日付[Date] < 期間開始
    )
RETURN
    COUNTROWS( EXCEPT( 今期顧客, 過去顧客 ) )
```

### 11. 既存顧客数

```dax
既存顧客数 =
VAR 今期顧客 = COUNTROWS( VALUES( Fact_売上[CustomerID] ) )
RETURN
    今期顧客 - [新規顧客数]
```

### 12. 新規顧客売上

```dax
新規顧客売上 =
VAR 期間開始 = MIN( Dim_日付[Date] )
VAR 過去顧客 =
    CALCULATETABLE(
        VALUES( Fact_売上[CustomerID] ),
        REMOVEFILTERS( Dim_日付 ),
        Dim_日付[Date] < 期間開始
    )
RETURN
    CALCULATE(
        [総売上],
        EXCEPT( VALUES( Fact_売上[CustomerID] ), 過去顧客 )
    )
```

### 13. 復活顧客数

12か月以上離れていた顧客が戻ってきた数です。

```dax
復活顧客数 =
VAR 期間開始 = MIN( Dim_日付[Date] )
VAR 今期顧客 = VALUES( Fact_売上[CustomerID] )
VAR 直近1年顧客 =
    CALCULATETABLE(
        VALUES( Fact_売上[CustomerID] ),
        REMOVEFILTERS( Dim_日付 ),
        Dim_日付[Date] >= 期間開始 - 365,
        Dim_日付[Date] < 期間開始
    )
VAR それ以前顧客 =
    CALCULATETABLE(
        VALUES( Fact_売上[CustomerID] ),
        REMOVEFILTERS( Dim_日付 ),
        Dim_日付[Date] < 期間開始 - 365
    )
RETURN
    COUNTROWS(
        INTERSECT( EXCEPT( 今期顧客, 直近1年顧客 ), それ以前顧客 )
    )
```

> [!TIP] 集合演算3兄弟
> `EXCEPT( A, B )` は「Aにあって Bにない」、`INTERSECT( A, B )` は「両方にある」、`UNION( A, B )` は「どちらかにある」。顧客分析はこの3つの組み合わせで書けます。
### 14. コホート維持率

```dax
コホート顧客数 = DISTINCTCOUNT( Fact_売上[CustomerID] )
```

```dax
コホート規模 =
CALCULATE(
    DISTINCTCOUNT( Fact_売上[CustomerID] ),
    REMOVEFILTERS( Dim_日付 )
)
```

```dax
コホート維持率 = DIVIDE( [コホート顧客数], [コホート規模] )
```

マトリックスの行に `Dim_顧客[初回購入月]`、列に `Dim_日付[年月]`、値に `コホート維持率` を置きます。

```figure
{ "type":"tablediff", "title":"コホート表の読み方", "arrowLabel":"維持率に変換",
  "caption":"左上から右下に落ちていくのが正常。落ち方の差がコホートの質",
  "before":{"title":"顧客数（実数）","tone":"neutral","head":["初回月","1月","2月","3月"],
    "rows":[["2024/01","120","54","41"],["2024/02","—","98","45"]]},
  "after":{"title":"維持率（%）","tone":"good","head":["初回月","1月","2月","3月"],
    "rows":[["2024/01","!100","45","34"],["2024/02","—","!100","46"]]} }
```

### 15. 簡易LTV

```dax
LTV_簡易 =
VAR 平均客単価 = DIVIDE( [総売上], DISTINCTCOUNT( Fact_売上[OrderID] ) )
VAR 平均購入回数 = DIVIDE( DISTINCTCOUNT( Fact_売上[OrderID] ), DISTINCTCOUNT( Fact_売上[CustomerID] ) )
RETURN
    平均客単価 * 平均購入回数
```

> [!DS] LTVの前提
> これは「観測期間内の実績」であり、将来価値の予測ではありません。本来のLTVは継続率と割引率を含めて算出します。指標名が実態より大きな約束をしていないかを常に点検してください。

## 第4群：商品・バスケット（2本）

バスケット分析には、リレーションシップを持たない**切り離しテーブル**を使います。

**モデリング → 新しいテーブル**：

```dax
商品選択 = SELECTCOLUMNS( Dim_商品, "選択商品", Dim_商品[ProductName] )
```

`SELECTCOLUMNS` で作ると系統（リレーションシップの血筋）が切れ、`Dim_商品` とは独立したテーブルになります。この列をスライサーに置きます。

### 16. 併売注文数

```dax
併売注文数 =
VAR 選択商品 = SELECTEDVALUE( 商品選択[選択商品] )
VAR 基準注文 =
    CALCULATETABLE(
        VALUES( Fact_売上[OrderID] ),
        FILTER( ALL( Dim_商品 ), Dim_商品[ProductName] = 選択商品 )
    )
RETURN
    IF(
        ISBLANK( 選択商品 ),
        BLANK(),
        CALCULATE(
            DISTINCTCOUNT( Fact_売上[OrderID] ),
            KEEPFILTERS( Fact_売上[OrderID] IN 基準注文 )
        )
    )
```

テーブルビジュアルに `Dim_商品[ProductName]` と `併売注文数` を置き、スライサーで商品を1つ選ぶと「一緒に買われた商品」が並びます。

### 17. 平均商品点数（バスケットサイズ）

```dax
平均商品点数 =
DIVIDE( SUM( Fact_売上[Quantity] ), DISTINCTCOUNT( Fact_売上[OrderID] ) )
```

## 第5群：表現のためのメジャー（3本）

### 18. 目標達成率

**モデリング → 新しいパラメーター → 数値範囲** で `目標成長率`（最小0、最大0.3、増分0.01）を作ってから：

```dax
目標売上 = [前年売上] * ( 1 + [目標成長率 値] )
```

```dax
目標達成率 = DIVIDE( [総売上], [目標売上] )
```

### 19. 動的タイトル

```dax
分析タイトル =
VAR 期間 =
    FORMAT( MIN( Dim_日付[Date] ), "yyyy年M月" ) & "〜" &
    FORMAT( MAX( Dim_日付[Date] ), "yyyy年M月" )
VAR 対象 =
    SWITCH( TRUE(),
        ISFILTERED( Dim_商品[Category] ),
            CONCATENATEX( VALUES( Dim_商品[Category] ), Dim_商品[Category], "・" ),
        ISFILTERED( Dim_店舗[Region] ),
            CONCATENATEX( VALUES( Dim_店舗[Region] ), Dim_店舗[Region], "・" ),
        "全社"
    )
VAR 達成 = [目標達成率]
RETURN
    対象 & "｜" & 期間 & "｜目標達成率 " & FORMAT( 達成, "0.0%" )
```

### 20. 条件付き書式用の色メジャー

```dax
達成率_色 =
VAR 率 = [目標達成率]
RETURN
    SWITCH( TRUE(),
        ISBLANK( 率 ),  "#8A93A6",
        率 >= 1.0,      "#14926B",
        率 >= 0.9,      "#8FBF5A",
        率 >= 0.8,      "#C77700",
        "#D33A4B"
    )
```

```figure
{ "type":"cards", "cols":3, "title":"色メジャーの設計指針", "caption":"色は装飾ではなく、しきい値を可視化する手段",
  "items":[
    {"icon":"🟢","title":"達成（100%以上）","text":"緑。何もしなくてよい状態","tone":"good"},
    {"icon":"🟡","title":"注意（80〜100%）","text":"黄。要因を確認する状態","tone":"amber"},
    {"icon":"🔴","title":"危険（80%未満）","text":"赤。今日行動が必要な状態","tone":"bad"} ] }
```

> [!WARN] 色だけに意味を載せない
> 赤緑の判別が難しい人がいます。矢印（▲▼）や数値の併記を必ず添えてください。色は「気づかせる」ためのもので、「伝える」役目は文字が担います。

---

## 完成チェックリスト

- [ ] 20本すべてが `_Measures` にあり、書式が設定されている
- [ ] `売上累計` が単調増加している
- [ ] `売上_3か月移動平均` が月次の合計÷3になっている
- [ ] `商品ABC` でAランクが売上の約7割を占める
- [ ] 総計行でABC区分が空白になる
- [ ] `新規顧客数 + 既存顧客数` が当期の顧客数と一致する
- [ ] コホート表が左上から右下に向かって値が下がる
- [ ] `商品選択` テーブルが `Dim_商品` とつながっていない
- [ ] スライサーで商品を選ぶと `併売注文数` が変わる
- [ ] `分析タイトル` がスライサーに応じて変わる
- [ ] 条件付き書式で色が変わる

## トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| 累積構成比が全行100% | 総計行の分岐がない | `HASONEVALUE` で分岐 |
| `初回購入日` が全顧客同じ | 計算列で `CALCULATE` を省略した | `CALCULATE( MIN(...) )` にする |
| 新規顧客数が常に0 | `REMOVEFILTERS( Dim_日付 )` を書いていない | 過去顧客の取得範囲を確認 |
| コホート維持率が全部100% | `コホート規模` で日付フィルターが残っている | `REMOVEFILTERS( Dim_日付 )` を追加 |
| 併売注文数が全商品同じ値 | `KEEPFILTERS` を書いていない | 注文の絞り込みが上書きされている |
| `商品選択` のスライサーが他を絞る | `DISTINCT` で作った（系統が残る） | `SELECTCOLUMNS` で作り直す |
| 目標達成率が空白 | 前年データのない期間 | 仕様。`BLANK()` のままでよい |
| 動的タイトルが「全社」のまま | 相互作用による絞り込み | `ISFILTERED` は強調表示を検知しない |
| マトリックスが数十秒かかる | `SUMX( FILTER( ALL(...) ) )` が重い | [LAB09](lab.html?id=LAB09) で計測して改善 |

## 発展課題

### 課題1：ABC区分を計算列にしてみる（15分）

`商品ABC` をメジャーではなく `Dim_商品` の計算列として実装し、スライサーに使えるようにしてください。メジャー版との違い（計算列は更新時に固定、メジャーは選択に応じて変わる）を体感できます。

### 課題2：RFM分析を作る（30分）

顧客を Recency（最終購入からの日数）・Frequency（購入回数）・Monetary（購入金額）の3軸で5段階に分け、`R5F5M5` のようなスコアを作ります。

```dax
最終購入からの日数 =
VAR 基準日 = MAX( Dim_日付[Date] )
VAR 最終購入 = CALCULATE( MAX( Fact_売上[OrderDate] ) )
RETURN
    DATEDIFF( 最終購入, 基準日, DAY )
```

### 課題3：フィールドパラメーターで軸を切り替える（15分）

**モデリング → 新しいパラメーター → フィールド** で `Dim_商品[Category]` `Dim_店舗[Region]` `Dim_顧客[Segment]` を1つにまとめます。スライサーで軸を選べるようになり、ページ数を1/3に減らせます。

## 次のステップ

- 速度を計測して直すなら → [LAB09](lab.html?id=LAB09)
- 理論を補強するなら → [反復関数](lesson.html?id=L1301) / [実務パターン集](lesson.html?id=L1305)

保存名：`LAB08_DAX20本.pbix`
