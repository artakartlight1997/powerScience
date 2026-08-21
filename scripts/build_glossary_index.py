# -*- coding: utf-8 -*-
"""
用語集のインデックスを生成する

    python3 scripts/build_glossary_index.py

docs/content/glossary/M*.json をすべて読み、
docs/content/glossary/index.json に統合したものを書き出します。

クライアント（glossary.js）はこの1ファイルだけを取得すればよくなるため、
存在しないモジュールへの 404 リクエストが発生しません。
"""
import json, os, io, glob, sys
from collections import Counter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
GDIR = os.path.join(ROOT, "docs", "content", "glossary")
CUR = os.path.join(ROOT, "docs", "content", "curriculum.json")

# レッスン → モジュール / ティア の対応（あれば付与する）
lesson_meta = {}
if os.path.exists(CUR):
    try:
        cur = json.load(io.open(CUR, encoding="utf-8"))
        for l in cur.get("lessons", []):
            lesson_meta[l["id"]] = {
                "module": l.get("module"), "tier": l.get("tier"),
                "moduleTitle": l.get("moduleTitle"), "lessonTitle": l.get("title"),
            }
    except Exception as e:
        print("警告: curriculum.json を読めませんでした (%s)" % e)

terms, seen, dupes = [], {}, []
for path in sorted(glob.glob(os.path.join(GDIR, "*.json"))):
    if os.path.basename(path) == "index.json":
        continue
    src = os.path.basename(path)[:-5]
    try:
        data = json.load(io.open(path, encoding="utf-8"))
    except Exception as e:
        print("エラー: %s を読めません (%s)" % (src, e))
        continue
    if not isinstance(data, list):
        print("エラー: %s は配列ではありません" % src)
        continue
    for t in data:
        name = (t.get("term") or "").strip()
        if not name:
            continue
        if name in seen:
            dupes.append((name, seen[name], src))
            continue
        seen[name] = src
        t["source"] = src
        les = t.get("lesson")
        if les and les in lesson_meta:
            t.update({k: v for k, v in lesson_meta[les].items() if v})
        terms.append(t)

# 長い用語ほど先にマッチさせたいので、あらかじめ降順に並べておく
terms.sort(key=lambda t: (-len(t.get("term", "")), t.get("term", "")))

tag_counts = Counter()
for t in terms:
    for tag in t.get("tags", []) or []:
        tag_counts[tag] += 1

out = {
    "count": len(terms),
    "sources": sorted(set(seen.values())),
    "tags": [t for t, _ in tag_counts.most_common()],
    "terms": terms,
}
io.open(os.path.join(GDIR, "index.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))

print("用語集インデックスを生成しました")
print("  用語数   : %d" % len(terms))
print("  ソース   : %d ファイル (%s)" % (len(out["sources"]), ", ".join(out["sources"])))
print("  タグ     : %d 種類" % len(tag_counts))
if dupes:
    print("  重複     : %d 件（先に読み込んだ方を採用）" % len(dupes))
    for name, a, b in dupes[:10]:
        print("      %s : %s / %s" % (name, a, b))
sys.exit(0)
