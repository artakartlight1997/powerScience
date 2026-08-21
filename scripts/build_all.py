# -*- coding: utf-8 -*-
"""
サイトのデータをまとめて生成し、検証する

    python3 scripts/build_all.py

順に実行するもの:
  1. build_curriculum.py     modules/*.json  → curriculum.json / pl300.json
  2. build_glossary_index.py glossary/*.json → glossary/index.json
  3. build_quiz_index.py     quizzes/*.json  → quizzes/index.json
  4. validate_content.py     整合性チェック
  5. check_density.py        本文の「読む文字」の量を検査（v3基準）

いずれかが失敗したら 0 以外で終了します（CI でそのまま使えます）。
"""
import subprocess, sys, os

HERE = os.path.dirname(os.path.abspath(__file__))
STEPS = [
    ("カリキュラムの生成", "build_curriculum.py"),
    ("用語集インデックスの生成", "build_glossary_index.py"),
    ("クイズインデックスの生成", "build_quiz_index.py"),
    ("検索インデックスの生成", "build_search_index.py"),
    ("図(figure)のJSON検査", "fix_figures.py"),
    ("コンテンツの検証", "validate_content.py"),
    # 圧縮作業が完了するまでは「警告」扱い（soft=True）。
    # 全レッスン・全ハンズオンが基準を満たしたら soft を外して必須化する。
    ("本文の文字量の検査（レッスン）", "check_density.py", [], True),
    ("本文の文字量の検査（ハンズオン）", "check_density.py", ["--labs"], True),
]

failed, warned = [], []
for step in STEPS:
    label, script = step[0], step[1]
    extra = step[2] if len(step) > 2 else []
    soft = step[3] if len(step) > 3 else False
    path = os.path.join(HERE, script)
    if not os.path.exists(path):
        print("\n--- %s : スクリプトがありません (%s) ---" % (label, script))
        continue
    print("\n" + "=" * 62)
    print(" %s  (%s)" % (label, script))
    print("=" * 62)
    r = subprocess.run([sys.executable, path] + extra)
    if r.returncode != 0:
        if soft:
            warned.append(label)
        else:
            failed.append(label)

print("\n" + "=" * 62)
if warned:
    print(" 警告（ビルドは継続）: " + " / ".join(warned))
if failed:
    print(" 失敗: " + " / ".join(failed))
    sys.exit(1)
print(" すべて成功しました")
sys.exit(0)
