# -*- coding: utf-8 -*-
"""圧縮で消えた「解答の要点」(<details>) を、圧縮前のコミットから復元する。

    python3 restore_answers.py            # 何が復元されるか表示するだけ
    python3 restore_answers.py --write    # 実際に書き戻す

「理解度チェック」は問題だけ残り解答が消えたレッスンが出たため、
折りたたみ（<details>）の解答ブロックを元のコミットから取り出して戻す。
折りたたみは既定で閉じているので、読む文字の基準には影響しない。
"""
import io, os, re, sys, glob, subprocess

BASE = "e973cf5"                      # 圧縮を始める前のコミット
ROOT = "/home/user/powerScience"
LDIR = os.path.join(ROOT, "docs", "content", "lessons")
DETAILS = re.compile(r"<details>.*?</details>\n?", re.S)

restored, skipped, nosrc = [], [], []
for path in sorted(glob.glob(os.path.join(LDIR, "*.md"))):
    lid = os.path.basename(path)[:-3]
    cur = io.open(path, encoding="utf-8").read()
    if "## 理解度チェック" not in cur:
        skipped.append(lid); continue
    if "<details>" in cur:
        skipped.append(lid); continue

    rel = "docs/content/lessons/%s.md" % lid
    r = subprocess.run(["git", "-C", ROOT, "show", "%s:%s" % (BASE, rel)],
                       capture_output=True, text=True)
    if r.returncode != 0:
        nosrc.append(lid); continue
    blocks = DETAILS.findall(r.stdout)
    if not blocks:
        nosrc.append(lid); continue
    block = blocks[0].rstrip("\n")

    # 「## 理解度チェック」の設問リストの直後（次の見出しの手前）に差し込む
    i = cur.index("## 理解度チェック")
    nxt = cur.find("\n## ", i + 1)
    tail = cur[nxt:] if nxt >= 0 else ""
    head = cur[:nxt] if nxt >= 0 else cur
    new = head.rstrip("\n") + "\n\n" + block + "\n" + tail
    if "--write" in sys.argv:
        io.open(path, "w", encoding="utf-8").write(new)
    restored.append(lid)

print("復元: %d 件" % len(restored))
print("  " + " ".join(restored))
print("対象外（解答がある / 理解度チェックがない）: %d 件" % len(skipped))
if nosrc:
    print("元コミットに解答がなかった: %d 件  %s" % (len(nosrc), " ".join(nosrc)))
if "--write" not in sys.argv:
    print("\n--write を付けると書き戻します")
