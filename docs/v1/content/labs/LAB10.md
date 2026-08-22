所要75分。[LAB06](lab.html?id=LAB06) の店舗単位RLSを、組織階層に沿って自動で広がる仕組みに進化させます。
## このラボのゴール
```figure
{ "type":"steps", "title":"3段階で作る", "caption":"いきなり階層RLSに行かない。限界を見てから次へ進む",
  "items":[
    {"title":"段階1：静的RLS","text":"ロールに固定条件を書く。ロール数がユーザー種類だけ増える","tone":"blue"},
    {"title":"段階2：動的RLS","text":"ログインユーザーで権限表を絞る。ユーザーが増えても式は不変","tone":"green"},
    {"title":"段階3：階層RLS","text":"PATH と PATHCONTAINS で配下組織まで自動的に見える","tone":"violet"} ] }
```
## 準備
- `LAB06_RLS.pbix`（なければ [LAB03](lab.html?id=LAB03) の成果物）を開く
- [stores.csv](data/stores.csv) / [security_users.csv](data/security_users.csv) / [sales.csv](data/sales.csv) を使う
## ステップ0：検証用メジャーを先に作る（5分）
```dax
現在のユーザー = USERPRINCIPALNAME()

見える店舗数 = CALCULATE( COUNTROWS( Dim_店舗 ), REMOVEFILTERS() )

見える売上 = CALCULATE( [総売上], REMOVEFILTERS() )
```
- 3本をカードビジュアルで1ページにまとめ、「RLS検証」と名付ける（以降のテストで使う）
```figure
{ "type":"formula", "lang":"dax", "title":"物差しに `REMOVEFILTERS()` を付ける理由",
  "code":"見える店舗数 = CALCULATE( COUNTROWS( Dim_店舗 ), REMOVEFILTERS() )",
  "caption":"RLSだけは外れない。だから「この人に見えている全範囲」が測れる",
  "parts":[
    {"match":"REMOVEFILTERS()","label":"スライサーやビジュアルのフィルターは全部外れる","tone":"blue"},
    {"match":"COUNTROWS( Dim_店舗 )","label":"残るのはRLSのフィルターだけ。これが可視範囲","tone":"violet"} ] }
```
## ステップ1：段階1 — 静的RLS（10分）
1. **モデリング → ロールの管理 → 作成** → 名前 `関東限定`
2. `Dim_店舗` テーブルに `[Region] = "関東"` を設定する
3. 同様に `中部限定`（`[Region] = "中部"`）、`近畿限定` を作る
4. **ロールとして表示** で `関東限定` をテストし、`見える店舗数` が 4 になることを確認する
```figure
{ "type":"compare", "title":"静的RLSの適用範囲", "caption":"ロールが10個を超えたら、動的RLSに切り替えるサイン",
  "panels":[
    {"title":"静的RLSが向く場面","tone":"good","note":"小規模・安定",
     "items":["区分が3〜5種類で固定","権限表を作る手間のほうが大きい","部署ごとに見せる範囲が明確","変更がほとんど起きない"]},
    {"title":"静的RLSの限界","tone":"bad","note":"規模が出ると破綻する",
     "items":["ユーザー種類の数だけロールが増える","人事異動のたびに Desktop で修正・再発行","「関東の3店舗だけ」に対応できない","誰が何を見えるか一覧できない"]} ] }
```
> [!TRAP] ロールを増やし続けてはいけない
> 14店舗それぞれにロールを作ると運用が回りません。ロール数をユーザー数に比例させないのが設計原則です。
## ステップ2：段階2 — 動的RLS（15分）
1. [security_users.csv](data/security_users.csv) を `Dim_ユーザー権限` として読み込み、`Email` を小文字化
2. **ロールの管理 → 作成** → 名前 `動的_店舗担当`
3. `Dim_店舗` テーブルに次の式を設定する
```dax
Dim_店舗[StoreID] IN
    CALCULATETABLE(
        VALUES( Dim_ユーザー権限[StoreID] ),
        Dim_ユーザー権限[Email] = LOWER( USERPRINCIPALNAME() )
    )
```
```figure
{ "type":"formula", "lang":"dax", "title":"IN + CALCULATETABLE による動的RLS",
  "code":"Dim_店舗[StoreID] IN CALCULATETABLE( VALUES( Dim_ユーザー権限[StoreID] ), Dim_ユーザー権限[Email] = LOWER( USERPRINCIPALNAME() ) )",
  "caption":"「この人に許された店舗ID一覧」を作り、その中にあるかで判定する",
  "parts":[
    {"match":"Dim_店舗[StoreID] IN","label":"各行の店舗IDが、右のリストに含まれるか","tone":"blue"},
    {"match":"VALUES( Dim_ユーザー権限[StoreID] )","label":"許可された店舗IDの一覧","tone":"green"},
    {"match":"Dim_ユーザー権限[Email] = LOWER( USERPRINCIPALNAME() )","label":"ログインユーザーの行だけに絞る","tone":"violet"} ] }
```
```figure
{ "type":"compare", "title":"双方向ブリッジと IN + CALCULATETABLE", "caption":"新規に作るなら後者。既存の双方向が動いているなら無理に変えない",
  "panels":[
    {"title":"双方向ブリッジ","tone":"amber","note":"設定は単純",
     "items":["リレーションシップの設定だけで済む","モデル全体のフィルター経路が増える","他のメジャーの挙動に影響が出る"]},
    {"title":"IN + CALCULATETABLE","tone":"good","note":"推奨",
     "items":["モデルを汚さない","権限ロジックがロールの中に閉じる","式を読めば可視範囲が分かる"]} ] }
```
4. **ロールとして表示** で4ユーザーの `見える店舗数` を確認する
```figure
{ "type":"interactive", "widget":"rls-simulator", "title":"ユーザーごとの可視範囲",
  "caption":"同じレポートでも、ログインした人によって行が変わる" }
```
> [!TRAP] 権限表に存在しないユーザー
> 権限表にないアドレスでは0行になります。仕様どおりですが、利用者には「壊れている」と見えます。
```dax
アクセス案内 =
IF( [見える店舗数] = 0,
    "閲覧権限が設定されていません。管理者にご連絡ください（" & USERPRINCIPALNAME() & "）",
    BLANK() )
```
5. このメジャーをカードに置き、**書式 → 全般 → 効果** で背景を目立たせる
## ステップ3：段階3 — 階層RLS（25分）
`area-kanto` の権限は `security_users.csv` に4行を手で書いて実現していました。組織階層を1本持てば、行を足さずに配下が見えます。
```figure
{ "type":"tree", "title":"作る組織階層", "caption":"上位ノードの担当者は、配下のすべてを自動的に見られる",
  "root":{"label":"N000 本社","sub":"exec@..."},
  "children":[
    {"label":"N001 関東エリア","sub":"area-kanto@...","tone":"blue",
     "children":[{"label":"S001 新宿本店","sub":"tanaka@..."},{"label":"S002 渋谷店","sub":"sato@..."},{"label":"S003 横浜店","sub":"suzuki@..."}]},
    {"label":"N002 中部エリア","sub":"担当者未設定","tone":"green","children":[{"label":"S005 名古屋店","sub":"ito@..."}]},
    {"label":"N003 近畿エリア","sub":"担当者未設定","tone":"amber","children":[{"label":"S007 梅田店","sub":"yamamoto@..."}]} ] }
```
### 3-1. Dim_店舗に親ノードの列を足す
1. **ホーム → データの変換** で `Dim_店舗` を選ぶ
2. **列の追加 → カスタム列**（列名 `ParentID`）に次を入れ、型をテキストにする
```m
= if [Region] = "関東" then "N001"
  else if [Region] = "中部" then "N002"
  else if [Region] = "近畿" then "N003"
  else if [Region] = "オンライン" then "N000"
  else "N004"
```
### 3-2. 組織ノードの行を追加する
1. **ホーム → データの入力** で次のテーブルを作り、名前を `組織ノード` にする

| StoreID | StoreName | Prefecture | Region | ParentID |
|---|---|---|---|---|
| N000 | 本社 | — | 全社 | （空欄） |
| N001 | 関東エリア | — | 関東 | N000 |
| N002 | 中部エリア | — | 中部 | N000 |
| N003 | 近畿エリア | — | 近畿 | N000 |
| N004 | その他エリア | — | その他 | N000 |

2. `Dim_店舗` を選び、**ホーム → クエリの追加 → クエリを新規として追加** で連結する
3. 連結後の名前を `Dim_店舗` にし、元の店舗クエリは読み込み無効にする
### 3-3. PATH列を作る
**モデリング → 新しい列**（`Dim_店舗` を選んだ状態）で2本作ります。
```dax
組織パス = PATH( Dim_店舗[StoreID], Dim_店舗[ParentID] )

組織階層レベル = PATHLENGTH( Dim_店舗[組織パス] )
```
```figure
{ "type":"cards", "cols":3, "title":"`PATH` が動くための3条件", "caption":"1つでも欠けるとエラーか循環参照になる",
  "items":[
    {"icon":"📄","title":"同じテーブルの2列","text":"`PATH` は他テーブルの列を受け取れない。子キーと親キーを同じ表に置く","tone":"blue"},
    {"icon":"🔑","title":"親IDが主キーに存在する","text":"`組織ノード` の連結漏れがあると親を辿れない","tone":"amber"},
    {"icon":"🕳","title":"ルート行の親は空欄","text":"本社（N000）の `ParentID` を空にする。空でないと循環参照","tone":"bad"} ] }
```
`S001` の行には `N000|N001|S001` が入ります。これが「本社 → 関東エリア → 新宿本店」の経路そのものです。
### 3-4. 担当ノード表を作る
1. **データの入力** で `Dim_担当ノード` を作る（リレーションシップは結びません）

| Email（ドメインは `@northstar-retail.example.com`） | NodeID |
|---|---|
| exec | N000 |
| area-kanto | N001 |
| tanaka | S001 |
| sato | S002 |
| suzuki | S003 |
| ito | S005 |

### 3-5. 階層ロールを作る
1. **ロールの管理 → 作成** → 名前 `階層セキュリティ`。`Dim_店舗` に次の式を設定する
```dax
COUNTROWS(
    FILTER(
        Dim_担当ノード,
        Dim_担当ノード[Email] = LOWER( USERPRINCIPALNAME() )
            && PATHCONTAINS( Dim_店舗[組織パス], Dim_担当ノード[NodeID] )
    )
) > 0
```
```figure
{ "type":"formula", "lang":"dax", "title":"階層RLSの判定式",
  "code":"PATHCONTAINS( Dim_店舗[組織パス], Dim_担当ノード[NodeID] )",
  "caption":"「この店舗の経路に、私の担当ノードが含まれるか」を1行で判定する",
  "parts":[
    {"match":"PATHCONTAINS","label":"パス文字列に指定の値が含まれるか判定する","tone":"violet"},
    {"match":"Dim_店舗[組織パス]","label":"N000|N001|S001 のような経路","tone":"blue"},
    {"match":"Dim_担当ノード[NodeID]","label":"その人が担当する組織のID","tone":"green"} ] }
```
```figure
{ "type":"compare", "title":"`LOOKUPVALUE` ではなく `COUNTROWS( FILTER( ... ) )`", "caption":"兼務が発生した瞬間に差が出る",
  "panels":[
    {"title":"LOOKUPVALUE","tone":"bad","note":"兼務で破綻",
     "items":["該当行が2件以上あるとエラー","関東と中部を兼務した時点で止まる","原因がRLSだと気づきにくい"]},
    {"title":"COUNTROWS( FILTER( ... ) ) > 0","tone":"good","note":"推奨",
     "items":["何件該当してもエラーにならない","「1件でも該当すれば見える」と読める","担当ノード表に行を足すだけで拡張できる"]} ] }
```
2. **ロールとして表示** で `階層セキュリティ` を選び、動的RLSとの差を確認する
```figure
{ "type":"tablediff", "title":"同じユーザーで、動的RLSと階層RLSを比べる", "arrowLabel":"階層RLSに切り替える",
  "caption":"エリア担当の可視範囲が、権限表に行を足さずに広がる",
  "before":{"title":"動的RLS（権限表の行だけ）","tone":"amber","head":["ユーザー","見える店舗数"],
    "rows":[["tanaka@...","1（新宿本店）"],["suzuki@...","1（横浜店）"],["area-kanto@...","4（手で4行書いた分）"],["exec@...","14（全社）"]]},
  "after":{"title":"階層RLS（担当ノードから自動）","tone":"good","head":["ユーザー（担当ノード）","見える店舗数"],
    "rows":[["tanaka@...（S001）","1（自店のみ）"],["suzuki@...（S003）","1（自店のみ）"],["area-kanto@...（N001）","!5（関東4店舗＋エリアノード）"],["exec@...（N000）","!19（全14店舗＋組織ノード5行）"]]} }
```
### 3-6. 組織ノードをレポートから外す
店舗一覧に「関東エリア」が現れます。`種別` 列を作り、ビジュアルレベルフィルターで `店舗` だけに絞ります。
```m
= if Text.StartsWith( [StoreID], "N" ) then "組織" else "店舗"
```
## ステップ4：発行して Service で検証（10分）
1. **ホーム → 発行** で共有ワークスペースへ発行する
2. セマンティックモデルの「…」→ **セキュリティ** を開く
3. `階層セキュリティ` ロールにセキュリティグループを割り当てる
4. 「…」→ **ロールとしてテスト** で `area-kanto@...` を指定して確認する
> [!WARN] 権限の二重確認
> ワークスペースの**ビューアー**以外はRLSの対象外です。共同作成者以上には全データが見えます。
## 完成チェックリスト
- [ ] 検証用メジャー3本を「RLS検証」ページにまとめた
- [ ] 静的ロールと動的ロールが動作した
- [ ] `Dim_店舗` に `ParentID` 列を追加した
- [ ] 組織ノード5行を連結し、`組織パス` が `N000|N001|S001` の形で入っている
- [ ] `Dim_担当ノード` がどのテーブルともつながっていない
- [ ] エリア担当が配下店舗をすべて見られ、権限のない人には案内が出る
- [ ] `種別` 列で組織ノードをレポートから除外できる
## トラブルシューティング
| 症状 | 原因 | 対処 |
|---|---|---|
| `PATH` がエラー | ルート行の `ParentID` が空でない | 本社行を空欄にする |
| `PATH` がエラー | 親IDが主キーに存在しない | `組織ノード` の連結漏れを確認 |
| 階層ロールで何も見えない | `Dim_担当ノード` にメールがない | 小文字・スペルを確認 |
| 階層ロールで全部見える | ロールにチェックを入れていない | ロール名にチェック |
| 店舗一覧にエリア行が出る | 組織ノードを同一テーブルに入れた | `種別` 列でフィルター |
| 兼務ユーザーの範囲が足りない | 担当ノードが1行しかない | 担当ノード表に行を追加（式は不要） |
## 発展課題
```figure
{ "type":"cards", "cols":2, "title":"発展課題", "caption":"どれも実務でそのまま必要になる作業",
  "items":[
    {"icon":"🪪","title":"課題1 閲覧ログを仕込む（15分）","text":"`現在のユーザー` をレポート下部の小さなカードに常時表示する。問い合わせで「どのアカウントか」を聞く手間が消える","tone":"blue"},
    {"icon":"🏢","title":"課題2 組織改編に対応する（20分）","text":"①`組織ノード` に `N005 首都圏南エリア`（親 `N001`）を追加 ②`Dim_店舗` の `ParentID` を `StoreID = \"S003\"` のとき `N005` に変更。ロールの式は1文字も変わらない","tone":"green"},
    {"icon":"🙈","title":"課題3 OLS と組み合わせる（15分）","text":"RLSは行を隠すが列は隠せない。Tabular Editor で `Dim_店舗[ManagerEmail]` を `階層セキュリティ` から非表示にし、見え方を確認する","tone":"amber"},
    {"icon":"⏱","title":"課題4 性能を測る（15分）","text":"[LAB09] の手順で、ロールなし・動的RLS・階層RLS の3条件を計測して差を表にする。`PATHCONTAINS` は文字列処理を伴う","tone":"violet"} ] }
```
## 次のステップ
- 理論の確認 → [行レベルセキュリティ](lesson.html?id=L1204) / [双方向の罠](lesson.html?id=L1202)
- 設計の総仕上げへ → [LAB11](lab.html?id=LAB11)

保存名：`LAB10_階層RLS.pbix`
