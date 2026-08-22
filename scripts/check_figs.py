# -*- coding: utf-8 -*-
"""図の書き方が正しいか検査する

    python3 scripts/check_figs.py

図が1枚でも壊れると、そこだけ赤いエラー箱になって読者が止まる。
書式のまちがいは、書いた本人には見えないので機械で見る。
"""
import io, json, os, re, sys, glob

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
LDIR = os.path.join(ROOT, "docs", "content", "lessons")

TYPES = {"flow", "steps", "compare", "cards", "stack", "matrix", "tablediff",
         "star", "tree", "timeline", "formula", "chart", "pipeline"}
# 型ごとに、これが無いと描けないもの
NEED = {
    "flow": ["items"], "steps": ["items"], "cards": ["items"], "stack": ["items"],
    "timeline": ["items"], "tree": ["root"], "compare": ["panels"],
    "matrix": ["quadrants"], "tablediff": ["before", "after"],
    "chart": ["categories", "series"], "formula": ["code"], "star": ["fact", "dims"],
    "pipeline": ["nodes"],
}

bad, total = [], 0
for p in sorted(glob.glob(os.path.join(LDIR, "*.md"))):
    name = os.path.basename(p)[:-3]
    src = io.open(p, encoding="utf-8").read()
    if "mermaid" in src:
        bad.append((name, "mermaid は使わない"))
    if re.findall(r"^# ", src, re.M):
        bad.append((name, "H1 は書かない（題は自動で出る）"))
    if src.count("```") % 2:
        bad.append((name, "``` の数が合っていない"))
    for raw in re.findall(r"```figure\s*\n(.*?)```", src, re.S):
        total += 1
        if "**" in raw:
            bad.append((name, "図の中に ** がある（太字は効かない。「」を使う）"))
        try:
            cfg = json.loads(raw)
        except Exception as e:
            bad.append((name, "図の書き方がこわれている: %s" % str(e)[:60]))
            continue
        t = cfg.get("type")
        if t not in TYPES:
            bad.append((name, "知らない図の種類 '%s'" % t))
            continue
        for k in NEED.get(t, []):
            if not cfg.get(k):
                bad.append((name, "%s の図に %s がない" % (t, k)))
        # tablediff は head と rows。cols と書くと見出しが出ない
        if t == "tablediff":
            for side in ("before", "after"):
                d = cfg.get(side) or {}
                if "cols" in d:
                    bad.append((name, "tablediff は cols ではなく head と書く"))

if bad:
    print("図の書き方に問題があります（%d件 / 図は全部で%d枚）" % (len(bad), total))
    seen = set()
    for name, msg in bad:
        if (name, msg) in seen:
            continue
        seen.add((name, msg))
        print("  %-6s %s" % (name, msg))
    sys.exit(1)

print("図はすべて正しく書けています（%d枚）" % total)
sys.exit(0)
