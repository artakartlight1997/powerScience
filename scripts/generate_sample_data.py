# -*- coding: utf-8 -*-
"""
ハンズオン用サンプルデータ生成スクリプト（架空の小売企業 Northstar Retail）

    python3 scripts/generate_sample_data.py

乱数シードを固定しているため、実行するたびに同じデータが生成されます。
出力先: docs/data/
"""
import csv, os, random, io
from datetime import date, timedelta

random.seed(20260821)
OUT = os.path.join(os.path.dirname(__file__), "..", "docs", "data")
os.makedirs(OUT, exist_ok=True)

def w(name, header, rows):
    path = os.path.join(OUT, name)
    with io.open(path, "w", encoding="utf-8", newline="") as f:
        wr = csv.writer(f)
        wr.writerow(header)
        wr.writerows(rows)
    print("%-22s %6d rows  %7.1f KB" % (name, len(rows), os.path.getsize(path) / 1024))

# ---------------- 商品 ----------------
CATALOG = [
    ("家電", "PC・タブレット", [("ノートPC スタンダード", 78000, 128000), ("ノートPC ハイエンド", 142000, 238000),
                              ("タブレット 10インチ", 32000, 54000), ("デスクトップPC", 68000, 112000)]),
    ("家電", "周辺機器",      [("ワイヤレスマウス", 1400, 3200), ("メカニカルキーボード", 5200, 11800),
                              ("27インチモニター", 18000, 32800), ("USB-Cハブ", 2100, 4900),
                              ("ノイズキャンセルヘッドホン", 12000, 27800)]),
    ("家電", "生活家電",      [("空気清浄機", 15000, 29800), ("電気ケトル", 3200, 6980),
                              ("ロボット掃除機", 32000, 64800)]),
    ("衣料", "アウター",      [("ダウンジャケット", 8500, 19800), ("トレンチコート", 7200, 16800),
                              ("マウンテンパーカー", 6400, 14800)]),
    ("衣料", "トップス",      [("オックスフォードシャツ", 1800, 4900), ("カシミヤニット", 6200, 16800),
                              ("スウェット", 2100, 5900), ("Tシャツ 3枚組", 1200, 2980)]),
    ("衣料", "ボトムス",      [("スリムデニム", 2900, 7900), ("チノパンツ", 2200, 5900),
                              ("プリーツスカート", 2600, 6800)]),
    ("食品", "飲料",          [("ドリップコーヒー 50P", 980, 1980), ("緑茶ティーバッグ 100P", 620, 1280),
                              ("ミネラルウォーター 24本", 780, 1580)]),
    ("食品", "菓子",          [("チョコレート詰合せ", 890, 1980), ("せんべい詰合せ", 720, 1580),
                              ("焼菓子ギフト", 1400, 3200)]),
    ("食品", "食材",          [("オリーブオイル 500ml", 980, 2180), ("パスタ 1kg", 380, 780),
                              ("だしパック 30袋", 620, 1380), ("国産米 5kg", 2400, 3980)]),
]
products, pid = [], 0
for cat, sub, items in CATALOG:
    for name, cost, price in items:
        pid += 1
        products.append(["P%04d" % pid, name, cat, sub, cost, price])
w("products.csv", ["ProductID", "ProductName", "Category", "SubCategory", "StandardCost", "ListPrice"], products)

# ---------------- 店舗 ----------------
STORES = [
    ("S001", "新宿本店",   "東京都",   "関東", "2015-04-01", "田中 一郎"),
    ("S002", "渋谷店",     "東京都",   "関東", "2017-09-15", "佐藤 花子"),
    ("S003", "横浜店",     "神奈川県", "関東", "2016-06-01", "鈴木 健太"),
    ("S004", "大宮店",     "埼玉県",   "関東", "2019-03-20", "高橋 美咲"),
    ("S005", "名古屋店",   "愛知県",   "中部", "2016-11-01", "伊藤 大輔"),
    ("S006", "金沢店",     "石川県",   "中部", "2021-07-01", "渡辺 由美"),
    ("S007", "梅田店",     "大阪府",   "近畿", "2015-10-01", "山本 翔太"),
    ("S008", "神戸店",     "兵庫県",   "近畿", "2018-05-10", "中村 彩"),
    ("S009", "京都店",     "京都府",   "近畿", "2020-02-14", "小林 拓也"),
    ("S010", "広島店",     "広島県",   "中国", "2019-08-01", "加藤 沙織"),
    ("S011", "福岡天神店", "福岡県",   "九州", "2017-04-01", "吉田 涼"),
    ("S012", "札幌店",     "北海道",   "北海道", "2018-10-01", "山田 直樹"),
    ("S013", "仙台店",     "宮城県",   "東北", "2020-09-01", "佐々木 亮"),
    ("S014", "オンライン", "—",        "オンライン", "2014-01-01", "松本 恵"),
]
def email(name):
    roma = {"田中":"tanaka","佐藤":"sato","鈴木":"suzuki","高橋":"takahashi","伊藤":"ito","渡辺":"watanabe",
            "山本":"yamamoto","中村":"nakamura","小林":"kobayashi","加藤":"kato","吉田":"yoshida",
            "山田":"yamada","佐々木":"sasaki","松本":"matsumoto"}
    return roma[name.split()[0]] + "@northstar-retail.example.com"
w("stores.csv", ["StoreID", "StoreName", "Prefecture", "Region", "OpenDate", "Manager", "ManagerEmail"],
  [[s[0], s[1], s[2], s[3], s[4], s[5], email(s[5])] for s in STORES])
w("security_users.csv", ["Email", "StoreID"],
  [[email(s[5]), s[0]] for s in STORES] +
  [["area-kanto@northstar-retail.example.com", s] for s in ["S001", "S002", "S003", "S004"]] +
  [["exec@northstar-retail.example.com", s[0]] for s in STORES])

# ---------------- 顧客 ----------------
SEI = ["佐藤","鈴木","高橋","田中","伊藤","渡辺","山本","中村","小林","加藤","吉田","山田","佐々木","松本","井上","木村","林","清水"]
MEI = ["蓮","陽菜","湊","結衣","樹","咲良","悠真","芽依","大翔","杏","蒼","莉子","颯太","結菜","陽翔","美咲","健太","彩"]
SEG = ["一般", "一般", "一般", "ゴールド", "ゴールド", "プラチナ"]
PREF = [("東京都","関東"),("神奈川県","関東"),("埼玉県","関東"),("千葉県","関東"),("愛知県","中部"),
        ("石川県","中部"),("大阪府","近畿"),("兵庫県","近畿"),("京都府","近畿"),("広島県","中国"),
        ("福岡県","九州"),("北海道","北海道"),("宮城県","東北")]
customers = []
for i in range(1, 601):
    pref, region = random.choice(PREF)
    customers.append(["C%05d" % i, random.choice(SEI) + " " + random.choice(MEI),
                      random.choice(SEG), region, pref,
                      (date(2020, 1, 1) + timedelta(days=random.randint(0, 2000))).isoformat()])
w("customers.csv", ["CustomerID", "CustomerName", "Segment", "Region", "Prefecture", "SignupDate"], customers)

# ---------------- 売上 ----------------
START, END = date(2024, 1, 1), date(2025, 12, 31)
DAYS = (END - START).days + 1
SEASON = {1:0.85, 2:0.80, 3:1.10, 4:0.95, 5:0.95, 6:1.05, 7:1.15, 8:0.90,
          9:1.00, 10:1.05, 11:1.20, 12:1.45}          # 12月と7月が繁忙
STORE_W = [1.6, 1.2, 1.1, 0.7, 1.0, 0.4, 1.4, 0.8, 0.6, 0.5, 0.9, 0.7, 0.5, 2.0]

sales, oid = [], 0
for d in range(DAYS):
    day = START + timedelta(days=d)
    base = 8 + (4 if day.weekday() >= 5 else 0)
    growth = 1.0 + 0.10 * (d / DAYS)               # 2年で+10%成長
    n = max(1, int(random.gauss(base * SEASON[day.month] * growth, 2.5)))
    for _ in range(n):
        oid += 1
        store = random.choices(STORES, weights=STORE_W)[0]
        cust = random.choice(customers)
        prod = random.choice(products)
        qty = random.choices([1, 1, 1, 2, 2, 3, 5, 10], weights=[35, 20, 15, 12, 8, 5, 3, 2])[0]
        list_price = prod[5]
        disc = random.choices([0, 0, 0, 0.05, 0.1, 0.2], weights=[60, 12, 8, 10, 7, 3])[0]
        unit = round(list_price * (1 - disc))
        ship = day + timedelta(days=random.choices([0, 1, 2, 3, 5], weights=[40, 30, 15, 10, 5])[0])
        sales.append(["O%06d" % oid, day.isoformat(), ship.isoformat(), store[0], cust[0], prod[0],
                      qty, unit, disc, qty * unit])
w("sales.csv", ["OrderID", "OrderDate", "ShipDate", "StoreID", "CustomerID", "ProductID",
                "Quantity", "UnitPrice", "Discount", "SalesAmount"], sales)

# ---------------- 汚いデータ（LAB02用） ----------------
# 横持ち・全角空白・表記ゆれ・型崩れ・重複・小計行・空行 をわざと含む
dirty_header = ["店舗名", "商品カテゴリ", "2025年1月", "2025年2月", "2025年3月", "2025年4月", "備考"]
dirty = []
for s in STORES[:10]:
    for cat in ["家電", "衣料", "食品"]:
        vals = [random.randint(200000, 3000000) for _ in range(4)]
        name = s[1]
        # 表記ゆれ・全角空白を意図的に混入
        if random.random() < 0.3:
            name = "　" + name + " "
        if random.random() < 0.2:
            cat = cat + "　"
        row = [name, cat]
        for i, v in enumerate(vals):
            r = random.random()
            if r < 0.05:
                row.append("")                       # 空欄
            elif r < 0.09:
                row.append("{:,}".format(v))         # 桁区切り付き文字列
            elif r < 0.12:
                row.append("N/A")                    # エラーになる値
            else:
                row.append(v)
        row.append("" if random.random() < 0.8 else "確認中")
        dirty.append(row)
    dirty.append([s[1] + " 小計", "", "", "", "", "", "※この行は集計対象外"])
dirty.append(["", "", "", "", "", "", ""])
dirty.append(dirty[0][:])                            # 完全重複行
with io.open(os.path.join(OUT, "sales_dirty.csv"), "w", encoding="utf-8", newline="") as f:
    wr = csv.writer(f)
    wr.writerow(["Northstar Retail 月次売上速報（経理部作成）", "", "", "", "", "", ""])  # 余計な1行目
    wr.writerow(dirty_header)
    wr.writerows(dirty)
print("%-22s %6d rows  %7.1f KB" % ("sales_dirty.csv", len(dirty),
      os.path.getsize(os.path.join(OUT, "sales_dirty.csv")) / 1024))
