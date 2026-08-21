# -*- coding: utf-8 -*-
"""
コンテンツ整合性チェック

    python3 scripts/validate_content.py

・すべてのJSONがパースできるか
・カリキュラムが参照するレッスン本文・クイズ・ラボが存在するか
・クイズの answer が choices の範囲に収まっているか
・ラボが参照するデータファイルが存在するか
終了コード 0 = 問題なし / 1 = エラーあり
"""
import json, os, io, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DOCS = os.path.join(ROOT, "docs")
C = os.path.join(DOCS, "content")
errors, warnings = [], []

def load(path):
    try:
        with io.open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        errors.append("JSONを読めません: %s (%s)" % (os.path.relpath(path, ROOT), e))
        return None

cur = load(os.path.join(C, "curriculum.json"))
if cur is None:
    print("curriculum.json が読めないため中断します")
    sys.exit(1)

levels = {l["id"] for l in cur["levels"]}
labs = {l["id"] for l in cur["labs"]}

for lsn in cur["lessons"]:
    lid = lsn["id"]
    if lsn["level"] not in levels:
        errors.append("%s: 未知のレベル %s" % (lid, lsn["level"]))
    md = os.path.join(C, "lessons", lid + ".md")
    if not os.path.exists(md):
        warnings.append("%s: 本文 %s.md がありません（サイトは『執筆中』と表示します）" % (lid, lid))
    elif os.path.getsize(md) < 200:
        warnings.append("%s: 本文が極端に短いです" % lid)
    if lsn.get("lab") and lsn["lab"] not in labs:
        errors.append("%s: 未知のラボ参照 %s" % (lid, lsn["lab"]))
    if lsn.get("quiz"):
        qp = os.path.join(C, "quizzes", lsn["quiz"] + ".json")
        if not os.path.exists(qp):
            warnings.append("%s: クイズ %s.json がありません" % (lid, lsn["quiz"]))

for lab in cur["labs"]:
    md = os.path.join(C, "labs", lab["id"] + ".md")
    if not os.path.exists(md):
        warnings.append("%s: 手順 %s.md がありません" % (lab["id"], lab["id"]))
    for ds in lab.get("dataset", []):
        if not os.path.exists(os.path.join(DOCS, "data", ds)):
            errors.append("%s: データファイル data/%s がありません" % (lab["id"], ds))

qdir = os.path.join(C, "quizzes")
total = 0
for fn in sorted(os.listdir(qdir)):
    if not fn.endswith(".json") or fn == "index.json":
        continue
    q = load(os.path.join(qdir, fn))
    if q is None:
        continue
    for item in q.get("questions", []):
        total += 1
        n = len(item.get("choices", []))
        a = item.get("answer")
        idxs = a if isinstance(a, list) else [a]
        for i in idxs:
            if not isinstance(i, int) or i < 0 or i >= n:
                errors.append("%s / %s: answer %s が選択肢(%d件)の範囲外" % (fn, item.get("id"), a, n))
        if not item.get("explain"):
            warnings.append("%s / %s: 解説がありません" % (fn, item.get("id")))
        if item.get("ref") and not os.path.exists(os.path.join(C, "lessons", item["ref"] + ".md")):
            warnings.append("%s / %s: 参照レッスン %s の本文がありません" % (fn, item.get("id"), item["ref"]))

gl = load(os.path.join(C, "glossary.json"))
if isinstance(gl, list):
    for t in gl:
        if t.get("lesson") and not any(l["id"] == t["lesson"] for l in cur["lessons"]):
            errors.append("用語集『%s』: 未知のレッスン参照 %s" % (t.get("term"), t["lesson"]))

print("レッスン: %d / ラボ: %d / 設問: %d / 用語: %d"
      % (len(cur["lessons"]), len(cur["labs"]), total, len(gl or [])))
for wmsg in warnings:
    print("  [警告] " + wmsg)
for e in errors:
    print("  [エラー] " + e)
print("エラー %d 件 / 警告 %d 件" % (len(errors), len(warnings)))
sys.exit(1 if errors else 0)
