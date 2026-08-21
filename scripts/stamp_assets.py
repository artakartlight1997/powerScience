# -*- coding: utf-8 -*-
"""CSS/JS の参照に内容ハッシュを付けて、更新が確実に反映されるようにする

    python3 scripts/stamp_assets.py           # 差分を表示するだけ
    python3 scripts/stamp_assets.py --write   # 書き戻す

GitHub Pages は CSS/JS をブラウザにキャッシュさせるため、
サイトを更新しても閲覧者には古いファイルが使われ続けることがあります。
（例：サイト名を変えたのにヘッダーが古いまま＝古い config.js が使われている）

    <script src="assets/js/config.js">
      ↓
    <script src="assets/js/config.js?v=1a2b3c4d">

ファイルの中身が変わればハッシュも変わるので、
そのときだけブラウザが取り直します。変わっていなければキャッシュが効いたままです。
"""
import io, os, re, sys, glob, hashlib

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DOCS = os.path.join(ROOT, "docs")

# href="assets/…" / src="assets/…" の ?v=… は付け直す
REF = re.compile(r'((?:href|src)=")(assets/[^"?#]+\.(?:css|js))(?:\?v=[0-9a-f]+)?(")')

_cache = {}


def digest(rel):
    """assets/... の相対パスから、中身の短いハッシュを返す"""
    if rel in _cache:
        return _cache[rel]
    path = os.path.join(DOCS, rel)
    if not os.path.exists(path):
        _cache[rel] = None
        return None
    h = hashlib.md5(io.open(path, "rb").read()).hexdigest()[:8]
    _cache[rel] = h
    return h


write = "--write" in sys.argv
missing, changed, total = [], [], 0

for path in sorted(glob.glob(os.path.join(DOCS, "*.html"))):
    src = io.open(path, encoding="utf-8").read()
    hits = [0]

    def sub(m):
        global total
        rel = m.group(2)
        h = digest(rel)
        if h is None:
            missing.append((os.path.basename(path), rel))
            return m.group(0)
        total += 1
        new = m.group(1) + rel + "?v=" + h + m.group(3)
        if new != m.group(0):
            hits[0] += 1
        return new

    out = REF.sub(sub, src)
    if hits[0]:
        changed.append((os.path.basename(path), hits[0]))
        if write:
            io.open(path, "w", encoding="utf-8").write(out)

print("アセット参照にハッシュを付与しました" if write else "アセット参照のハッシュを検査しました")
print("  対象     : %d 箇所 / %d ファイル" % (total, len(glob.glob(os.path.join(DOCS, "*.html")))))
if changed:
    print("  要更新   : %d ファイル" % len(changed))
    for name, n in changed[:12]:
        print("      %-18s %d 箇所" % (name, n))
else:
    print("  すべて最新です")
if missing:
    print("  [エラー] 参照先が存在しません:")
    for name, rel in missing[:10]:
        print("      %s → %s" % (name, rel))
    sys.exit(1)
if changed and not write:
    print("\n--write を付けると書き戻します")
    sys.exit(1)
sys.exit(0)
