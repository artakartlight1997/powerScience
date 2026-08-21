# -*- coding: utf-8 -*-
"""
サイト内検索のインデックスを生成する

    python3 scripts/build_search_index.py

レッスン・ハンズオン・用語集を走査して docs/content/search.json を作ります。
見出し（##／###）ごとに1エントリを作るため、検索結果からレッスンの
該当セクションへ直接ジャンプできます。

図(figure)ブロックとコードブロックは本文から除外し、
コードは「コード片」として別フィールドに持ちます。
"""
import io, json, os, re, sys, glob

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
C = os.path.join(ROOT, "docs", "content")
MAX_LESSON = 220        # レッスン概要の抜粋
MAX_SECTION = 110       # 見出しセクションの抜粋（数が多いので短く）
MAX_TERM = 170          # 用語の抜粋
MIN_SECTION = 24        # これより短いセクションは索引しない

FENCE = re.compile(r"```.*?```", re.S)
INLINE_CODE = re.compile(r"`[^`\n]*`")
LINK = re.compile(r"\[([^\]]*)\]\([^)]*\)")
MD_MARK = re.compile(r"[*_>#|\-]{1,}")
WS = re.compile(r"\s+")


def clean(text):
    t = LINK.sub(r"\1", text)
    t = INLINE_CODE.sub(" ", t)
    t = t.replace("[[", "").replace("]]", "")
    t = MD_MARK.sub(" ", t)
    return WS.sub(" ", t).strip()


def sections(md):
    """(見出し, 見出しレベル, 本文) のリストに分解する。図とコードは除去する。"""
    body = FENCE.sub(" ", md)
    out, cur_h, cur_lv, buf = [], None, 0, []
    for line in body.split("\n"):
        m = re.match(r"^(#{2,3})\s+(.*)$", line)
        if m:
            if buf or cur_h:
                out.append((cur_h, cur_lv, clean(" ".join(buf))))
            cur_h, cur_lv, buf = m.group(2).strip(), len(m.group(1)), []
        else:
            buf.append(line)
    if buf or cur_h:
        out.append((cur_h, cur_lv, clean(" ".join(buf))))
    return out


def code_snippets(md):
    langs = []
    for m in re.finditer(r"```(\w+)\s*\n(.*?)```", md, re.S):
        lang = m.group(1).lower()
        if lang in ("dax", "m", "powerquery", "sql", "python"):
            langs.append(WS.sub(" ", m.group(2))[:90])
    return langs[:2]


entries = []
cur_path = os.path.join(C, "curriculum.json")
cur = json.load(io.open(cur_path, encoding="utf-8")) if os.path.exists(cur_path) else {"lessons": []}
lesson_by_id = {l["id"]: l for l in cur.get("lessons", [])}

# ---------------- レッスン ----------------
for path in sorted(glob.glob(os.path.join(C, "lessons", "*.md"))):
    lid = os.path.basename(path)[:-3]
    meta = lesson_by_id.get(lid)
    if not meta:
        continue
    md = io.open(path, encoding="utf-8").read()
    secs = sections(md)
    intro = next((t for h, lv, t in secs if h is None and t), "")
    entries.append({
        "t": "lesson", "id": lid, "url": "lesson.html?id=" + lid,
        "title": meta["title"], "tier": meta.get("tier"), "module": meta.get("module"),
        "mod": meta.get("moduleTitle", ""), "h": "",
        "x": (meta.get("gain", "") + " " + meta.get("why", "") + " " + intro)[:MAX_LESSON],
        "k": meta.get("keywords", []) + meta.get("ds", []),
        "c": code_snippets(md),
    })
    n = 0
    for h, lv, text in secs:
        if not h:
            continue
        n += 1
        if len(text) < MIN_SECTION and len(h) < 6:
            continue
        entries.append({
            "t": "section", "id": lid, "url": "lesson.html?id=" + lid + "#h" + str(n),
            "h": h, "x": text[:MAX_SECTION],
        })

# ---------------- ハンズオン ----------------
lab_index = os.path.join(C, "labs", "index.json")
labs = {}
if os.path.exists(lab_index):
    for lab in json.load(io.open(lab_index, encoding="utf-8")).get("labs", []):
        labs[lab["id"]] = lab
for path in sorted(glob.glob(os.path.join(C, "labs", "LAB*.md"))):
    lid = os.path.basename(path)[:-3]
    meta = labs.get(lid, {})
    md = io.open(path, encoding="utf-8").read()
    entries.append({
        "t": "lab", "id": lid, "url": "lab.html?id=" + lid,
        "title": meta.get("title", lid), "tier": meta.get("tier"), "module": meta.get("module"),
        "mod": "ハンズオン", "h": "",
        "x": (meta.get("goal", "") + " " + clean(FENCE.sub(" ", md))[:MAX_LESSON])[:MAX_LESSON],
        "k": [], "c": code_snippets(md),
    })
    n = 0
    for h, lv, text in sections(md):
        if not h:
            continue
        n += 1
        if len(text) < MIN_SECTION and len(h) < 6:
            continue
        entries.append({
            "t": "section", "id": lid, "url": "lab.html?id=" + lid + "#h" + str(n),
            "h": h, "x": text[:MAX_SECTION],
        })

# ---------------- 用語集 ----------------
gpath = os.path.join(C, "glossary", "index.json")
if os.path.exists(gpath):
    for t in json.load(io.open(gpath, encoding="utf-8")).get("terms", []):
        entries.append({
            "t": "term", "id": t["term"], "url": "glossary.html#" + t["term"],
            "title": t["term"], "tier": t.get("tier"), "module": t.get("module"),
            "mod": "用語集", "h": t.get("en", ""),
            "x": clean(t.get("short", "") + " " + t.get("plain", "") + " " + t.get("desc", ""))[:MAX_TERM],
            "k": (t.get("tags") or []) + (t.get("aliases") or []) + ([t["reading"]] if t.get("reading") else []),
            "c": [],
        })

parents = {}
for e in entries:
    if e["t"] in ("lesson", "lab"):
        parents[e["id"]] = {"title": e["title"], "tier": e.get("tier"), "mod": e.get("mod", "")}
out = {"count": len(entries), "parents": parents, "entries": entries}
dst = os.path.join(C, "search.json")
io.open(dst, "w", encoding="utf-8").write(json.dumps(out, ensure_ascii=False, separators=(",", ":")))

kinds = {}
for e in entries:
    kinds[e["t"]] = kinds.get(e["t"], 0) + 1
size = os.path.getsize(dst) / 1024
print("検索インデックスを生成しました")
print("  エントリ : %d  %s" % (len(entries), kinds))
print("  サイズ   : %.0f KB" % size)
if size > 2048:
    print("  警告: インデックスが大きすぎます。MAX_TEXT を減らしてください")
sys.exit(0)
