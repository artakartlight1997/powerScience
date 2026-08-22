# -*- coding: utf-8 -*-
"""初級コースをまとめて検査する

    python3 scripts/build_all.py

順に実行するもの:
  1. check_v2.py    中学生が読める形になっているか（禁止語・文字数・図の数）
  2. check_data.py  本文の数字がサンプルデータと合っているか
  3. check_figs.py  図の書き方が正しいか

いずれかが失敗したら 0 以外で終了します。
前のバージョン（docs/v1）の検査は scripts/v1/build_all.py です。
"""
import subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = [
    ("中学生が読める形か", "check_v2.py"),
    ("数字がデータと合っているか", "check_data.py"),
    ("図の書き方", "check_figs.py"),
]

failed = []
for label, script in STEPS:
    path = os.path.join(HERE, script)
    if not os.path.exists(path):
        continue
    print("\n" + "=" * 62)
    print(" %s  (%s)" % (label, script))
    print("=" * 62)
    if subprocess.run([sys.executable, path]).returncode != 0:
        failed.append(label)

print("\n" + "=" * 62)
if failed:
    print(" 失敗: " + " / ".join(failed))
    sys.exit(1)
print(" すべて成功しました")
sys.exit(0)
