# -*- coding: utf-8 -*-
"""本文に出てくる数字が、サンプルデータと合っているか検査する

    python3 scripts/check_data.py

読者は sales.csv を自分で読み込む。本文の数字がそれと違うと、
「自分のやり方が間違っているのか」と迷ってしまう。

ただし、わざと別の数字を出す回もある（1週間だけ数えた話など）。
その場合はレッスンの1行目に、理由つきで宣言する。

    <!-- data: 1週間だけ数えた結果。1か月ぶんの実データとは別 -->
"""
import csv, io, os, re, sys, glob, collections

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DATA = os.path.join(ROOT, "docs", "data")
LDIR = os.path.join(ROOT, "docs", "content", "lessons")

rows = list(csv.DictReader(io.open(os.path.join(DATA, "sales.csv"), encoding="utf-8")))
per, yen = collections.Counter(), collections.Counter()
for r in rows:
    per[r["味"]] += int(r["個数"])
    yen[r["味"]] += int(r["金額"])
total_n, total_y = sum(per.values()), sum(yen.values())

# 値段の表も正しい数字なので、照合できるようにしておく
price = {}
fp = os.path.join(DATA, "flavors.csv")
if os.path.exists(fp):
    for r in csv.DictReader(io.open(fp, encoding="utf-8")):
        price[r["味"]] = int(r["値段"])


def forms(n):
    return {str(n), format(n, ",")}


# 実データから確かめられる数は、すべて正しい数として扱う。
#   ・味ごとの個数と金額 / 全体の合計
#   ・曜日ごと、日ごとの合計
#   ・値段
#   ・味どうしの差、全体から1つを引いた残り
import datetime
dow_n, dow_y = collections.Counter(), collections.Counter()
day_n, day_y = collections.Counter(), collections.Counter()
for r in rows:
    d = datetime.date.fromisoformat(r["日付"])
    dow_n[d.weekday()] += int(r["個数"]); dow_y[d.weekday()] += int(r["金額"])
    day_n[r["日付"]] += int(r["個数"]); day_y[r["日付"]] += int(r["金額"])

GLOBAL_OK = set()
for v in ([total_n, total_y, len(rows), 31]
          + list(price.values())
          + list(dow_n.values()) + list(dow_y.values())
          + list(day_n.values()) + list(day_y.values())):
    GLOBAL_OK |= forms(v)
# 差と残り（「1位と2位の差は114個」「チーズ以外は1,938個」など）
vals = list(per.values()) + list(yen.values())
for a in vals:
    GLOBAL_OK |= forms(total_n - a) | forms(total_y - a)
    for b in vals:
        if a > b:
            GLOBAL_OK |= forms(a - b)

NUM = re.compile(r"(?<![0-9.,])([0-9]{3}|[0-9]{1,3},[0-9]{3})(?![0-9.,%])")
DECL = re.compile(r"<!--\s*data:\s*(.+?)\s*-->")
# 「もし〜だったら」の図は、わざと実データと違う数を出す。
# 書き手が仮の話だと明示しているので、そこは数えない。
IF_WORDS = ("もし", "仮に", "たとえば", "もしも")


def hypothetical_lines(src):
    """仮の話だと明示している図の行を集める"""
    out, keep, buf = set(), False, []
    for i, ln in enumerate(src.split("\n")):
        if ln.lstrip().startswith("```"):
            if keep:
                text = "\n".join(x[1] for x in buf)
                if any(w in text for w in IF_WORDS):
                    out |= {x[0] for x in buf}
                keep, buf = False, []
            elif ln.lstrip()[3:].strip().lower() == "figure":
                keep, buf = True, []
            continue
        if keep:
            buf.append((i, ln))
    return out

print("サンプルデータ（docs/data/sales.csv）")
for k, v in per.most_common():
    print("  %-6s %4d個  %8s円  （1個 %d円）" % (k, v, format(yen[k], ","), price.get(k, 0)))
print("  合計    %4d個  %8s円\n" % (total_n, format(total_y, ",")))

bad, skipped = [], []
for p in sorted(glob.glob(os.path.join(LDIR, "*.md"))):
    src = io.open(p, encoding="utf-8").read()
    name = os.path.basename(p)[:-3]
    d = DECL.search(src)
    if d:
        skipped.append((name, d.group(1)))
        continue
    skip = hypothetical_lines(src)
    for i, line in enumerate(src.split("\n")):
        if i in skip:
            continue
        # 1行に複数の味が出ることがある（グラフの見出しと値の並びなど）。
        # その行は、出てくる味すべての数字を正しいものとして扱う。
        here = [f for f in per if f in line]
        if not here:
            continue
        ok = set(GLOBAL_OK)
        for f in here:
            ok |= forms(per[f]) | forms(yen[f])
        for m in NUM.findall(line):
            if m not in ok:
                bad.append((name, "・".join(here), m, per[here[0]]))

if skipped:
    print("別の数字を使うと宣言しているレッスン")
    for name, why in skipped:
        print("  %-6s %s" % (name, why))
    print()

if bad:
    print("本文の数字が、サンプルデータと合っていません（%d件）" % len(bad))
    seen = set()
    for name, flavor, got, want in bad:
        k = (name, flavor, got)
        if k in seen:
            continue
        seen.add(k)
        print("  %-6s 「%s」の行に %s（実データは %d個 / %s円 / 1個%d円）"
              % (name, flavor, got, want, format(yen[flavor], ","), price.get(flavor, 0)))
    print("\n直し方は2つ")
    print("  1. 本文の数字を実データに合わせる")
    print("  2. わざと別の数字なら、レッスンの1行目に理由を書く")
    print("     <!-- data: 1週間だけ数えた結果。1か月ぶんとは別 -->")
    sys.exit(1)

print("本文の数字は、サンプルデータと一致しています")
sys.exit(0)
