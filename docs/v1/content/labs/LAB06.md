所要45分。行レベルセキュリティ（RLS）を実装し、アプリとして安全に配布します。

RLSは、同じレポートでも閲覧者ごとに見える行が変わる仕組みです。

## このラボのゴール

「各店舗の店長は自分の店舗のデータだけが見える」レポートを作り、発行して検証します。

```figure
{ "type":"pipeline", "title":"このラボで作る権限モデル", "caption":"ログイン時のメールから見える店舗が決まる",
  "nodes":[
    {"id":"u","label":"Dim_ユーザー権限\nEmail / StoreID","tone":"blue"},
    {"id":"s","label":"Dim_店舗\n14店舗","tone":"green"},
    {"id":"f","label":"Fact_売上\n約6,900行","tone":"amber"} ],
  "edges":[
    {"from":"u","to":"s","label":"双方向（ブリッジ）"},
    {"from":"s","to":"f","label":"1対多"} ] }
```

## 準備するもの

- `LAB05_ダッシュボード.pbix`（LAB03 / LAB04 の成果物でも可）
- [security_users.csv](data/security_users.csv) と [stores.csv](data/stores.csv)
- Power BI Service にサインインできる組織アカウント（Pro以上）

組織アカウントがなくてもステップ1〜4は実施でき、RLSの動作は確認できます。

```figure
{ "type":"cards", "cols":3, "title":"security_users.csv の中身", "caption":"列は Email と StoreID の2つだけ",
  "items":[
    {"icon":"🏪","title":"tanaka@… → 1行","text":"StoreID は S001。新宿本店の店長。自店だけが見える","tone":"blue"},
    {"icon":"🗾","title":"area-kanto@… → 4行","text":"S001〜S004。関東エリアマネージャ。4店舗が見える","tone":"green"},
    {"icon":"👔","title":"exec@… → 14行","text":"S001〜S014。経営層。全社と同じ数字になる","tone":"violet"} ] }
```

1人が何行でも持てることが、この方式（動的RLS）の利点です。

## ステップ1：権限テーブルを読み込む（5分）

1. **データを取得 → テキスト/CSV** で `security_users.csv` を選択
2. **データの変換** → クエリ名を `Dim_ユーザー権限` に変更
3. `Email` `StoreID` の両列をテキスト型に設定
4. `Email` 列を選択 → **変換 → 書式 → 小文字**
5. **ホーム → 閉じて適用**

```figure
{ "type":"tablediff", "arrowLabel":"小文字化 + トリミング", "title":"取り込み時に表記を揃える",
  "caption":"式側の LOWER() と両側で揃えるのが定石",
  "before":{"title":"CSVのまま","tone":"bad","head":["Email","StoreID"],
    "rows":[["!Tanaka@northstar-retail.example.com","S001"],["suzuki@northstar-retail.example.com","! S003"]]},
  "after":{"title":"整えた後","tone":"good","head":["Email","StoreID"],
    "rows":[["tanaka@northstar-retail.example.com","S001"],["suzuki@northstar-retail.example.com","S003"]]} }
```

## ステップ2：リレーションシップを作る（5分）

モデルビューで `Dim_ユーザー権限[StoreID]` から `Dim_店舗[StoreID]` へ線を引きます。

```figure
{ "type":"cards", "cols":3, "title":"この線に入れる設定", "caption":"1つでも漏れると0件か全件になる",
  "items":[
    {"icon":"🔢","title":"基数","text":"多対1（Dim_ユーザー権限 が多側、Dim_店舗 が1側）","tone":"blue"},
    {"icon":"↔","title":"クロスフィルターの方向","text":"両方","tone":"amber"},
    {"icon":"🔐","title":"セキュリティフィルター","text":"「両方向に適用」をオン","tone":"violet"} ] }
```

> [!WARN] ここだけは双方向にしてよい
> RLSのブリッジは [双方向の罠](lesson.html?id=L1202) の正当な例外です。他の線は単一方向のまま。

```figure
{ "type":"steps", "title":"フィルターが流れる順番", "caption":"3段階のどこかが切れると結果が壊れる",
  "items":[
    {"title":"ログイン情報を受け取る","text":"USERPRINCIPALNAME() が現在のユーザーのメールアドレスを返す","tone":"blue"},
    {"title":"権限テーブルを絞る","text":"ロールのDAX式が Dim_ユーザー権限 を該当行だけに絞る","tone":"green"},
    {"title":"店舗と売上へ伝播する","text":"双方向で Dim_店舗 へ、1対多で Fact_売上 へ流れる","tone":"amber"} ] }
```

## ステップ3：ロールを作成する（8分）

1. **モデリング → ロールの管理 → 作成** でロール名を `店舗担当者` に変更
2. `Dim_ユーザー権限` テーブルを選び、DAX式に次を入力して保存

```dax
[Email] = LOWER( USERPRINCIPALNAME() )
```

```figure
{ "type":"formula", "lang":"dax", "title":"ロールのフィルター式",
  "code":"[Email] = LOWER( USERPRINCIPALNAME() )",
  "caption":"TRUE になる行だけが残る",
  "parts":[
    {"match":"[Email]","label":"Dim_ユーザー権限 の各行の値","tone":"blue"},
    {"match":"LOWER","label":"取り込み時に小文字化した値と揃える","tone":"green"},
    {"match":"USERPRINCIPALNAME()","label":"今ログインしている人のメールアドレスを返す","tone":"violet"} ] }
```

> [!EXAM] `USERNAME()` ではなく `USERPRINCIPALNAME()`
> 前者は Desktop と Service で戻り値が変わります。後者はどちらでも UPN を返します。

## ステップ4：Desktop でテストする（8分）

1. **モデリング → 表示 → ロールとして表示**
2. `店舗担当者` にチェックを入れる（ここを忘れると全件見えます）
3. 「他のユーザー」にチェックし、`tanaka@northstar-retail.example.com` と入力してOK
4. 黄色いバナーが出たら、下図の4パターンを順に試す
5. バナーの「ロールの表示を停止」で通常表示に戻す

```figure
{ "type":"chart", "kind":"bar", "title":"ユーザー別に見える総売上の目安",
  "caption":"exec は全社と一致する。ここがずれたら設定を疑う",
  "categories":["tanaka(S001)","suzuki(S003)","area-kanto(S001-4)","exec(全14店)"],
  "series":[{"name":"見える割合","values":[7,7,29,100],"tone":"blue"}],
  "highlight":3, "unit":"%" }
```

```figure
{ "type":"interactive", "widget":"rls-simulator", "title":"ユーザーを切り替えて見える行を確認する",
  "caption":"店長・エリアマネージャ・経営層で数字がどう変わるか" }
```

```figure
{ "type":"tree", "title":"テストがうまくいかないときの切り分け", "root":{"label":"表示がおかしい"},
  "children":[
    {"label":"何も表示されない","sub":"方向が「両方」か／セキュリティフィルターがオンか／メールが権限表にあるか／小文字化したか","tone":"bad"},
    {"label":"全部見えてしまう","sub":"ロール名のチェックボックスを入れ忘れている","tone":"amber"} ] }
```

## ステップ5：発行してユーザーを割り当てる（13分）

1. **ホーム → 発行** で共有ワークスペースを選ぶ（個人用では共有できません）
2. Service でワークスペースを開き、セマンティックモデルの「**…**」→ **セキュリティ**
3. `店舗担当者` ロールの右欄にユーザーまたはセキュリティグループを追加 → **保存**
4. ロール名の「**…**」→ **ロールとしてテスト** で表示を確認する

```figure
{ "type":"compare", "title":"Desktop と Service の役割分担", "caption":"境界を間違えると「設定したのに効かない」",
  "panels":[
    {"title":"Power BI Desktop","tone":"blue",
     "items":["ロールを作る","DAXフィルター式を書く","ロールとして表示でテスト","ユーザーの割り当てはできない"],
     "note":"定義する場所"},
    {"title":"Power BI Service","tone":"green",
     "items":["ロールにユーザーを割り当てる","セキュリティグループを割り当てる","ロールとしてテスト","フィルター式は変更できない"],
     "note":"運用する場所"} ] }
```

個人ではなく Entra ID のセキュリティグループを割り当てると、異動時も人事側だけで完結します。

## ステップ6：アプリとして配布し、権限を確認する（11分）

1. ワークスペース右上の **アプリの作成** → アプリ名 `Northstar 売上ダッシュボード` を設定
2. **コンテンツ** でレポートを追加し、表示順を調整する
3. **対象ユーザー** で対象ユーザー名を `全社` にし、アクセス権を付与するグループを指定
4. 閲覧のみにする場合は **「ビルド権限を許可する」をオフ** にして **アプリの発行**

```figure
{ "type":"stack", "title":"ワークスペースロールと見え方", "caption":"RLSが効くのはビューアーだけ",
  "layers":[
    {"label":"管理者","sub":"ワークスペースの削除・権限変更。RLS対象外","tone":"bad"},
    {"label":"メンバー","sub":"アプリの発行・更新。RLS対象外","tone":"amber"},
    {"label":"共同作成者","sub":"編集はできるがアプリ発行は不可。RLS対象外","tone":"amber"},
    {"label":"ビューアー","sub":"閲覧者はここ。RLSが適用される","tone":"good"} ] }
```

> [!WARN] 閲覧者に共同作成者以上を与えるとRLSは効かない
> モデルを編集できる立場はRLSの対象外です。「RLSを設定したから安全」は誤りです。

## 完成チェックリスト

- [ ] `Dim_ユーザー権限` を読み込み、`Email` を小文字化した
- [ ] `Dim_ユーザー権限 → Dim_店舗` を双方向にした
- [ ] 「セキュリティフィルターを両方向に適用」をオンにした
- [ ] ロールに `[Email] = LOWER( USERPRINCIPALNAME() )` を設定した
- [ ] 「ロールとして表示」で4パターンとも期待どおりだった
- [ ] `exec@…` の総売上が、RLSなしの総売上と一致した
- [ ] 共有ワークスペースに発行し、ロールにユーザーを割り当てた
- [ ] アプリとして発行し、閲覧者にビューアー権限を付けた

## トラブルシューティング

| 症状 | 原因 | 対処 |
|---|---|---|
| 何も表示されない | 双方向設定の漏れ／メールが権限表にない | 方向を「両方」に。CSVの綴りを確認 |
| 全部見えてしまう | ロール未チェック／共同作成者以上 | チェックを入れる。ビューアーに変更 |
| 一部の店舗だけ見えない | `StoreID` に空白が混入 | トリミングを実施 |
| 商品一覧だけ全件 | 単一方向で商品側に伝播しない | 仕様。必要なら商品側にもRLS |
| 発行後に式を直したい | Service では変更不可 | Desktop で修正して再発行 |
| 更新が失敗する | ゲートウェイか資格情報の漏れ | モデルの設定を確認 |

## 発展課題

### 課題1：静的ロールを追加する（10分）

**ロールの管理 → 作成** で `関東限定` を作り、`Dim_店舗` に次を設定します。

```dax
[Region] = "関東"
```

違いは「誰が見ているかを式が参照するか」。ユーザーが増えても直さずに済むのが動的RLSです。

### 課題2：複数ロールの合成を確かめる（10分）

`店舗担当者` と `関東限定` の両方にチェックを入れるとどうなるか、予想してから試します。

答えはOR（和集合）。片方でも見える行は見えます。ANDにしたいなら1つのロールに複数の式を書きます。

### 課題3：オブジェクトレベルセキュリティを調べる（10分）

RLSは行を隠しますが、列そのものを隠すにはOLS（Tabular Editor が必要）を使います。

給与列など、どんな場面で必要かを考えてみてください。

### 課題4：階層RLSに進む

「配下の全店舗を見る」は `PATH` と `PATHCONTAINS` で実装します。

```dax
PATHCONTAINS(
    Dim_店舗[店舗パス],
    LOOKUPVALUE(
        Dim_ユーザー権限[StoreID],
        Dim_ユーザー権限[Email], LOWER( USERPRINCIPALNAME() )
    )
)
```

実装は [LAB10](lab.html?id=LAB10)、理論は [L1204](lesson.html?id=L1204) で扱います。

## 次のステップ

取得・整形・モデリング・DAX・可視化・配布・セキュリティまでを一通り実装しました。

- 再利用可能なMパイプラインへ → [LAB07](lab.html?id=LAB07)
- DAX上級20本ノックへ → [LAB08](lab.html?id=LAB08)
- 運用の理論 → [ワークスペースとアプリ](lesson.html?id=L1002) / [データ更新](lesson.html?id=L1003)

保存名：`LAB06_RLS.pbix`
