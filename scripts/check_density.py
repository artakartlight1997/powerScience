# -*- coding: utf-8 -*-
"""
レッスンの「読む文字の多さ」を検査する（v3基準）

    python3 scripts/check_density.py            # 全レッスン
    python3 scripts/check_density.py L0601      # 個別
    python3 scripts/check_density.py --top 20   # 読む文字が多い順

読者が実際に「読む」文字＝地の文＋箇条書き＋表＋コールアウト。
図(figure)のJSONは読む文字に数えない（描画されるため）。

基準
    読む文字      2,200字以下   （地の文700 / 箇条500 / 表600 / コールアウト500 が目安）
    地の文        800字以下
    コールアウト  3個以下・600字以下
    コード        70行以下
    figure        10枚以上
    1段落         100字以下
    連続段落      2つまで
    行数          100〜210行
    H2見出し      5〜9個
終了コード 0 = 基準を満たす / 1 = 違反あり
"""
import io, os, re, sys, glob

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
LDIR = os.path.join(ROOT, "docs", "content", "lessons")
BDIR = os.path.join(ROOT, "docs", "content", "labs")

LIM = {
    "read": 2200, "prose": 800, "callout_chars": 600, "callouts": 3,
    "code_lines": 70, "figs": 10, "para": 100, "run": 2,
    "lines_min": 100, "lines_max": 210, "h2_min": 5, "h2_max": 9,
}
# ハンズオンは手順書なので、箇条書き（＝操作ステップ）を多めに許容する。
# ただし「読ませる地の文」の基準はレッスンと同じ厳しさを保つ。
LAB_LIM = dict(LIM, read=2800, prose=800, code_lines=110,
               figs=6, lines_min=100, lines_max=260, h2_max=14)
FENCE = re.compile(r"```.*?```", re.S)


def analyze(path):
    src = io.open(path, encoding="utf-8").read()
    figs = re.findall(r"```figure\s*\n.*?```", src, re.S)
    code = re.findall(r"```(?!figure)[\s\S]*?```", src)
    body = FENCE.sub("", src)

    prose = bullets = tables = quotes = 0
    paragraphs, run, max_run = [], 0, 0
    for ln in body.split("\n"):
        t = ln.strip()
        if not t:
            run = 0
            continue
        if t.startswith("|"):
            tables += len(t); run = 0
        elif t.startswith(">"):
            quotes += len(t); run = 0
        elif t.startswith(("-", "*")) or re.match(r"^\d+\.", t):
            bullets += len(t); run = 0
        elif t.startswith("#") or t.startswith("<") or set(t) <= set("-|: "):
            run = 0
        else:
            prose += len(t); paragraphs.append(t); run += 1
            max_run = max(max_run, run)

    return {
        "read": prose + bullets + tables + quotes,
        "prose": prose, "bullets": bullets, "tables": tables, "quotes": quotes,
        "callouts": len(re.findall(r"^>\s*\[!", body, re.M)),
        "code_lines": sum(len(c.split("\n")) for c in code),
        "figs": len(figs),
        "para": max((len(p) for p in paragraphs), default=0),
        "run": max_run,
        "lines": len(src.split("\n")),
        "h2": len(re.findall(r"^## ", src, re.M)),
    }


def check(m, LIM=LIM):
    b = []
    if m["read"] > LIM["read"]:                b.append("読む文字 %d字（%d字以下）" % (m["read"], LIM["read"]))
    if m["prose"] > LIM["prose"]:              b.append("地の文 %d字（%d字以下）" % (m["prose"], LIM["prose"]))
    if m["quotes"] > LIM["callout_chars"]:     b.append("コールアウト %d字（%d字以下）" % (m["quotes"], LIM["callout_chars"]))
    if m["callouts"] > LIM["callouts"]:        b.append("コールアウト %d個（%d個以下）" % (m["callouts"], LIM["callouts"]))
    if m["code_lines"] > LIM["code_lines"]:    b.append("コード %d行（%d行以下）" % (m["code_lines"], LIM["code_lines"]))
    if m["figs"] < LIM["figs"]:                b.append("図 %d枚（%d枚以上）" % (m["figs"], LIM["figs"]))
    if m["para"] > LIM["para"]:                b.append("最長段落 %d字（%d字以下）" % (m["para"], LIM["para"]))
    if m["run"] > LIM["run"]:                  b.append("段落%d連続（%dまで）" % (m["run"], LIM["run"]))
    if not (LIM["lines_min"] <= m["lines"] <= LIM["lines_max"]):
        b.append("%d行（%d〜%d行）" % (m["lines"], LIM["lines_min"], LIM["lines_max"]))
    if not (LIM["h2_min"] <= m["h2"] <= LIM["h2_max"]):
        b.append("H2 %d個（%d〜%d個）" % (m["h2"], LIM["h2_min"], LIM["h2_max"]))
    return b


args = [a for a in sys.argv[1:] if not a.startswith("--")]
top = 0
if "--top" in sys.argv:
    i = sys.argv.index("--top")
    top = int(sys.argv[i + 1]) if len(sys.argv) > i + 1 else 20

labs_mode = "--labs" in sys.argv or any(a.startswith("LAB") for a in args)
paths = sorted(glob.glob(os.path.join(BDIR if labs_mode else LDIR, "*.md")))
if args:
    paths = [p for p in paths if os.path.basename(p)[:-3] in args]
lim = LAB_LIM if labs_mode else LIM
kind = "ハンズオン" if labs_mode else "レッスン"

rows, ng = [], 0
for p in paths:
    m = analyze(p)
    bad = check(m, lim)
    rows.append((os.path.basename(p)[:-3], m, bad))
    if bad:
        ng += 1

if top:
    rows.sort(key=lambda r: -r[1]["read"])
    for name, m, bad in rows[:top]:
        print("%-7s 読む%5d字 (地%4d 箇%4d 表%4d 注%4d)  図%3d  コード%4d行  %3d行  %s"
              % (name, m["read"], m["prose"], m["bullets"], m["tables"], m["quotes"],
                 m["figs"], m["code_lines"], m["lines"], "NG" if bad else "OK"))
    sys.exit(0)

for name, m, bad in rows:
    if bad:
        print("NG %-7s %s" % (name, " / ".join(bad)))

n = len(rows) or 1
print("\n%d %s中 %d 件が基準未達" % (len(rows), kind, ng))
print("平均: 読む文字 %d字（地%d 箇%d 表%d 注%d） / 図 %.1f枚 / コード %d行 / %d行"
      % (sum(r[1]["read"] for r in rows) // n, sum(r[1]["prose"] for r in rows) // n,
         sum(r[1]["bullets"] for r in rows) // n, sum(r[1]["tables"] for r in rows) // n,
         sum(r[1]["quotes"] for r in rows) // n, sum(r[1]["figs"] for r in rows) / n,
         sum(r[1]["code_lines"] for r in rows) // n, sum(r[1]["lines"] for r in rows) // n))
sys.exit(1 if ng else 0)
