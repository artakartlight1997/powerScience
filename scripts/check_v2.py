# -*- coding: utf-8 -*-
"""初級コースの本文が「中学生が読める形」になっているか検査する

    python3 scripts/check_v2.py            # 全レッスン
    python3 scripts/check_v2.py L203       # 個別
    python3 scripts/check_v2.py --words    # 禁止語だけ一覧

v1 は専門用語だらけで初学者に通じなかった。同じ失敗をしないよう、
WRITING_RULES.md の決まりを機械で守らせる。

図の中の文字も検査する。図に専門用語を逃がしても意味がないため。
"""
import io, json, os, re, sys, glob

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
LDIR = os.path.join(ROOT, "docs", "content", "lessons")
COURSE = os.path.join(ROOT, "docs", "content", "course.json")

LIM = {"read": 1200, "figs": 8, "sentence": 45, "para_sentences": 2, "run": 2,
       "h2_min": 4, "h2_max": 8}

# 使ってはいけない言葉 → 代わりに使う言葉（WRITING_RULES.md の表と対応）
BANNED = {
    "可視化": "グラフにして見えるようにする",
    "インポート": "読み込む",
    "エクスポート": "書き出す",
    "フィルタ": "しぼりこむ",
    "集計": "合計を出す / 数える",
    "ビジュアル": "グラフ / 図",
    "ダッシュボード": "ひと目でわかる画面",
    "メジャー": "計算のしかたを覚えさせたもの",
    "リレーションシップ": "表と表のつなぎ目",
    "クエリ": "データの取り出し方",
    "セマンティック": "整えたデータのまとまり",
    "モデリング": "データを組み立てること",
    "カーディナリティ": "同じ値がどれくらい重なっているか",
    "ドリルダウン": "もっと細かく見る",
    "インサイト": "気づき",
    "トランザクション": "1件ずつの記録",
    "エンティティ": "もの / 人",
    "ディメンション": "見る切り口",
    "ファクト": "できごとの記録",
    "スキーマ": "表の組み立て方",
    "コンテキスト": "どの範囲を見ているか",
    "パラメータ": "あとから変えられる値",
    "ソリューション": "やり方",
    "ナレッジ": "知っていること",
    "エビデンス": "証拠",
    "アジェンダ": "話す順番",
    "リテラシー": "読み書きの力",
    "スキーム": "やり方",
    "ロジック": "すじみち",
    "バイアス": "かたより",
    "アサイン": "割り当て",
    "コミット": "決めて守ること",
}
# 英字の略語。文中に出たら止める。
# ただし製品名の一部と、中学生にも通じるものは通す。
ABBR = re.compile(r"\b[A-Z]{2,5}\b")
EXEMPT = {
    "BI",                       # 製品名「Power BI」の一部。避けようがない
    "CSV",                      # ファイルの種類。本文で「表のファイル」と説明したうえで使う
    "PC", "PDF", "URL", "ID", "OK", "NG", "AI",
}

FENCE_RE = re.compile(r"```")


def split_doc(src):
    """本文（フェンス外）と、図の中の文字列だけを取り出す"""
    body, figtext, lang, buf = [], [], None, []
    for ln in src.split("\n"):
        if ln.lstrip().startswith("```"):
            if lang is None:
                lang = ln.lstrip()[3:].strip().lower(); buf = []
            else:
                if lang == "figure":
                    try:
                        def walk(o):
                            if isinstance(o, str): figtext.append(o)
                            elif isinstance(o, list): [walk(x) for x in o]
                            elif isinstance(o, dict):
                                for k, v in o.items():
                                    if k not in ("type", "kind", "tone", "dir", "icon"): walk(v)
                        walk(json.loads("\n".join(buf)))
                    except Exception:
                        pass
                lang, buf = None, []
            continue
        (buf if lang is not None else body).append(ln)
    return "\n".join(body), figtext


def sentences(text):
    """句点で文に割る。カッコの中は割らない"""
    out, cur, depth = [], "", 0
    for ch in text:
        if ch in "（(「『【": depth += 1
        elif ch in "）)」』】": depth = max(0, depth - 1)
        cur += ch
        if ch in "。！？" and depth == 0:
            out.append(cur.strip()); cur = ""
    if cur.strip(): out.append(cur.strip())
    return out


def analyze(path):
    src = io.open(path, encoding="utf-8").read()
    body, figtext = split_doc(src)
    figs = len(re.findall(r"```figure\s*\n.*?```", src, re.S))

    read, paras, run, max_run, long_sent, many = 0, [], 0, 0, [], []
    for ln in body.split("\n"):
        t = ln.strip()
        if not t:
            run = 0; continue
        if t.startswith("#") or t.startswith("<"):
            run = 0; continue
        read += len(t)
        if t.startswith((">", "-", "*", "|")) or re.match(r"^\d+\.", t):
            run = 0
        else:
            run += 1; max_run = max(max_run, run); paras.append(t)
        for s in sentences(t):
            if len(s) > LIM["sentence"]:
                long_sent.append(s)
    for p in paras:
        if len(sentences(p)) > LIM["para_sentences"]:
            many.append(p)

    # 禁止語（本文＋図の中）
    hits = {}
    # > [!NOTE] などは書き方の印であって本文ではないので、略語の検査からは外す
    haystack = re.sub(r"\[!\w+\]", "", body) + "\n" + "\n".join(figtext)
    for w, alt in BANNED.items():
        n = haystack.count(w)
        if n:
            hits[w] = (n, alt)
    abbrs = sorted({a for a in ABBR.findall(haystack) if a not in EXEMPT})

    return {"read": read, "figs": figs, "long": long_sent, "many": many, "run": max_run,
            "banned": hits, "abbr": abbrs,
            "h2": len(re.findall(r"^## ", src, re.M)),
            "h1": len(re.findall(r"^# ", src, re.M))}


def check(m):
    b = []
    if m["h1"]: b.append("H1を書かない（%d個）" % m["h1"])
    if m["read"] > LIM["read"]: b.append("読む文字 %d字（%d字以下）" % (m["read"], LIM["read"]))
    if m["figs"] < LIM["figs"]: b.append("図 %d枚（%d枚以上）" % (m["figs"], LIM["figs"]))
    if m["run"] > LIM["run"]: b.append("段落が%d連続（%dまで。次は図にする）" % (m["run"], LIM["run"]))
    if not (LIM["h2_min"] <= m["h2"] <= LIM["h2_max"]):
        b.append("見出し %d個（%d〜%d個）" % (m["h2"], LIM["h2_min"], LIM["h2_max"]))
    for s in m["long"][:3]:
        b.append("長い文 %d字「%s…」" % (len(s), s[:26]))
    for p in m["many"][:2]:
        b.append("1段落に3文以上「%s…」" % p[:26])
    for w, (n, alt) in sorted(m["banned"].items()):
        b.append("禁止語「%s」%d回 → %s" % (w, n, alt))
    if m["abbr"]:
        b.append("略語 %s（初級では使わない）" % "、".join(m["abbr"][:5]))
    return b


if "--words" in sys.argv:
    print("使ってはいけない言葉と、代わりに使う言葉\n")
    for w, alt in sorted(BANNED.items()):
        print("  %-14s → %s" % (w, alt))
    sys.exit(0)

args = [a for a in sys.argv[1:] if not a.startswith("--")]
paths = sorted(glob.glob(os.path.join(LDIR, "*.md")))
if args:
    paths = [p for p in paths if os.path.basename(p)[:-3] in args]

# course.json にあって本文がまだないものも報告する
planned = []
if os.path.exists(COURSE):
    c = json.load(io.open(COURSE, encoding="utf-8"))
    for ch in c.get("chapters", []):
        for l in ch.get("lessons", []):
            planned.append(l["id"])

have = {os.path.basename(p)[:-3] for p in paths}
missing = [i for i in planned if i not in have] if not args else []

ng = 0
for p in paths:
    m = analyze(p)
    bad = check(m)
    if bad:
        ng += 1
        print("NG %-6s %s" % (os.path.basename(p)[:-3], bad[0]))
        for x in bad[1:]:
            print("          %s" % x)

n = len(paths) or 1
print("\n%d 本中 %d 本が基準未達" % (len(paths), ng))
print("平均: 読む文字 %d字 / 図 %.1f枚"
      % (sum(analyze(p)["read"] for p in paths) // n,
         sum(analyze(p)["figs"] for p in paths) / n))
if missing:
    print("本文がまだないレッスン: %d本  %s" % (len(missing), " ".join(missing)))
sys.exit(1 if (ng or missing) else 0)
