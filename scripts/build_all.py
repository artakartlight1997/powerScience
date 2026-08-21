# -*- coding: utf-8 -*-
"""
サイトのデータをまとめて生成し、検証する

    python3 scripts/build_all.py

順に実行するもの:
  1. build_curriculum.py     modules/*.json  → curriculum.json / pl300.json
  2. build_glossary_index.py glossary/*.json → glossary/index.json
  3. build_quiz_index.py     quizzes/*.json  → quizzes/index.json
  4. validate_content.py     整合性チェック

いずれかが失敗したら 0 以外で終了します（CI でそのまま使えます）。
"""
import subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = [
    ("カリキュラムの生成", "build_curriculum.py"),
    ("用語集インデックスの生成", "build_glossary_index.py"),
    ("クイズインデックスの生成", "build_quiz_index.py"),
    ("図(figure)のJSON検査", "fix_figures.py"),
    ("コンテンツの検証", "validate_content.py"),
]

failed = []
for label, script in STEPS:
    path = os.path.join(HERE, script)
    if not os.path.exists(path):
        print("\n--- %s : スクリプトがありません (%s) ---" % (label, script))
        continue
    print("\n" + "=" * 62)
    print(" %s  (%s)" % (label, script))
    print("=" * 62)
    r = subprocess.run([sys.executable, path])
    if r.returncode != 0:
        failed.append(label)

print("\n" + "=" * 62)
if failed:
    print(" 失敗: " + " / ".join(failed))
    sys.exit(1)
print(" すべて成功しました")
sys.exit(0)
