# -*- coding: utf-8 -*-
"""レッスンで使っている DAX / M 関数が用語集にあるか検査する

    python3 scripts/check_functions.py            # 一覧を表示
    python3 scripts/check_functions.py --quiet    # 件数だけ

読者が式を見て意味を調べられるようにするため、
本文・ハンズオン・formula図で使った関数はすべて用語集に登録する。
"""
import io, json, re, sys, os, glob, collections

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
C = os.path.join(ROOT, "docs", "content")

DAXF = re.compile(r"\b([A-Z][A-Z0-9]{2,}(?:\.[A-Z][A-Za-z0-9]+)?)\s*\(")
MF = re.compile(r"\b((?:Table|List|Text|Date|Number|Record|Value|Splitter|Csv|Excel|Sql|"
                r"Web|Json|Duration|DateTime|Character|Lines|Binary)\.[A-Za-z]+)\s*\(")
KEYWORDS = {"VAR", "RETURN", "NOT", "AND", "OR", "IF", "IN", "ORDER", "BY", "DEFINE",
            "EVALUATE", "MEASURE", "COLUMN", "TABLE", "START", "AT", "TRUE", "FALSE", "BLANK"}


def code_of(path):
    src = io.open(path, encoding="utf-8").read()
    out, lang, buf = [], None, []
    for ln in src.split("\n"):
        if ln.lstrip().startswith("```"):
            if lang is None:
                lang = ln.lstrip()[3:].strip().lower(); buf = []
            else:
                body = "\n".join(buf)
                if lang in ("dax", "m", "sql"):
                    out.append(body)
                elif lang == "figure":
                    try:
                        def walk(o):
                            if isinstance(o, dict):
                                if o.get("type") == "formula" and o.get("code"):
                                    out.append(str(o["code"]))
                                for v in o.values(): walk(v)
                            elif isinstance(o, list):
                                for x in o: walk(x)
                        walk(json.loads(body))
                    except Exception:
                        pass
                lang, buf = None, []
            continue
        if lang is not None:
            buf.append(ln)
    return "\n".join(out)


idxp = os.path.join(C, "glossary", "index.json")
if not os.path.exists(idxp):
    print("用語集インデックスがありません"); sys.exit(0)
idx = json.load(io.open(idxp, encoding="utf-8"))
known = set()
for t in idx["terms"]:
    known.add(t["term"].upper())
    for a in t.get("aliases") or []:
        known.add(a.upper())

cnt, where = collections.Counter(), collections.defaultdict(set)
for p in sorted(glob.glob(os.path.join(C, "lessons", "*.md")) +
                glob.glob(os.path.join(C, "labs", "*.md"))):
    name = os.path.basename(p)[:-3]
    code = code_of(p)
    for m in set(DAXF.findall(code)) | set(MF.findall(code)):
        if m in KEYWORDS or m.upper() in known:
            continue
        cnt[m] += 1
        where[m].add(name)

if not cnt:
    print("使用している DAX / M 関数はすべて用語集にあります")
    sys.exit(0)

print("用語集に無い関数が %d 個あります" % len(cnt))
if "--quiet" not in sys.argv:
    for w, n in cnt.most_common():
        print("  %-28s %2dファイル  例: %s" % (w, n, "、".join(sorted(where[w])[:3])))
    print("\n直し方: docs/content/glossary/M*.json に term / short / desc を追加してください")
sys.exit(1)
