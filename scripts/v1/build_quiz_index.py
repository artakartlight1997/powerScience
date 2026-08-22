# -*- coding: utf-8 -*-
"""
クイズのインデックスを生成する

    python3 scripts/build_quiz_index.py

docs/content/quizzes/*.json を読み、docs/content/quizzes/index.json を書き出します。
一覧ページとトップページの問題数表示がこれを参照します。
"""
import json, os, io, glob, sys
from collections import Counter

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
QDIR = os.path.join(ROOT, "docs", "v1", "content", "quizzes")

idx, total, exam_total = {}, 0, 0
area_counter, skill_counter, diff_counter = Counter(), Counter(), Counter()

for path in sorted(glob.glob(os.path.join(QDIR, "*.json"))):
    fn = os.path.basename(path)
    if fn in ("index.json", "EXAM-COVERAGE.json"):
        continue
    try:
        d = json.load(io.open(path, encoding="utf-8"))
    except Exception as e:
        print("エラー: %s を読めません (%s)" % (fn, e))
        continue
    qs = d.get("questions", [])
    idx[d["id"]] = {
        "title": d.get("title", d["id"]),
        "count": len(qs),
        "lesson": d.get("lesson"),
        "isExam": d["id"].startswith("EXAM"),
    }
    if d["id"].startswith("EXAM"):
        exam_total += len(qs)
    else:
        total += len(qs)
    for q in qs:
        if q.get("area"):
            area_counter[q["area"]] += 1
        if q.get("skill"):
            skill_counter[q["skill"]] += 1
        diff_counter[str(q.get("difficulty", ""))] += 1

out = {
    "totalQuestions": total + exam_total,
    "lessonQuestions": total,
    "examQuestions": exam_total,
    "byArea": dict(area_counter),
    "bySkill": dict(skill_counter),
    "byDifficulty": dict(diff_counter),
    "quizzes": idx,
}
io.open(os.path.join(QDIR, "index.json"), "w", encoding="utf-8").write(
    json.dumps(out, ensure_ascii=False, indent=1))

print("クイズインデックスを生成しました")
print("  ファイル       : %d" % len(idx))
print("  レッスン別設問 : %d 問" % total)
print("  模擬試験       : %d 問" % exam_total)
print("  合計           : %d 問" % (total + exam_total))
if skill_counter:
    print("  スキル項目     : %d 種類に出題あり" % len(skill_counter))
sys.exit(0)
