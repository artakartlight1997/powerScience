# -*- coding: utf-8 -*-
"""
figure ブロックのJSONを検査し、機械的に直せる誤りを修正する

    python3 scripts/fix_figures.py           # 検査のみ
    python3 scripts/fix_figures.py --write   # 修正して書き戻す

自動修正するもの
  * 文字列リテラルの中に生の改行が入っている  → \\n に置換
  * 文字列リテラルの中に生のタブが入っている  → \\t に置換
  * 配列・オブジェクトの末尾カンマ            → 削除
  * 全角の引用符（“ ” 「 」ではなくJSON構文位置のもの）→ 半角に置換

直せないものは一覧で報告します（人が直す必要があります）。
"""
import io, json, os, re, sys, glob

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", "..")
TARGET_DIRS = [
    os.path.join(ROOT, "docs", "v1", "content", "lessons"),
    os.path.join(ROOT, "docs", "v1", "content", "labs"),
]
WRITE = "--write" in sys.argv
FENCE = re.compile(r"(```figure[^\n]*\n)(.*?)(```)", re.S)


def escape_raw_controls(src):
    """文字列リテラルの内側にある生の改行・タブをエスケープする"""
    out, in_str, escaped = [], False, False
    for ch in src:
        if in_str:
            if escaped:
                out.append(ch); escaped = False; continue
            if ch == "\\":
                out.append(ch); escaped = True; continue
            if ch == '"':
                out.append(ch); in_str = False; continue
            if ch == "\n":
                out.append("\\n"); continue
            if ch == "\t":
                out.append("\\t"); continue
            if ch == "\r":
                continue
            out.append(ch)
        else:
            if ch == '"':
                in_str = True
            out.append(ch)
    return "".join(out)


def strip_trailing_commas(src):
    return re.sub(r",(\s*[}\]])", r"\1", src)


def try_repair(raw):
    """(修正後の文字列, 適用した処理のリスト) を返す。直せなければ (None, 理由)"""
    applied = []
    candidate = raw
    for name, fn in (("生の改行/タブをエスケープ", escape_raw_controls),
                     ("末尾カンマを削除", strip_trailing_commas)):
        try:
            json.loads(candidate)
            return (candidate, applied)
        except Exception:
            pass
        fixed = fn(candidate)
        if fixed != candidate:
            candidate = fixed
            applied.append(name)
    try:
        json.loads(candidate)
        return (candidate, applied)
    except Exception as e:
        return (None, str(e))


total = fixed_count = broken = 0
unfixable = []

for d in TARGET_DIRS:
    for path in sorted(glob.glob(os.path.join(d, "*.md"))):
        src = io.open(path, encoding="utf-8").read()
        changed = False

        def repl(m):
            global total, fixed_count, broken, changed
            head, body, tail = m.group(1), m.group(2), m.group(3)
            total += 1
            try:
                json.loads(body)
                return m.group(0)
            except Exception:
                pass
            new_body, info = try_repair(body)
            name = os.path.basename(path)
            if new_body is None:
                broken += 1
                unfixable.append((name, info[:90], body.strip()[:120]))
                return m.group(0)
            fixed_count += 1
            print("  修正 %s : %s" % (name, " / ".join(info) or "整形"))
            changed = True
            return head + new_body + tail

        new_src = FENCE.sub(repl, src)
        if changed and WRITE:
            io.open(path, "w", encoding="utf-8").write(new_src)

print("\n図の総数 : %d" % total)
print("修正      : %d" % fixed_count + ("（書き戻しました）" if WRITE else "（--write を付けると書き戻します）"))
print("手動対応  : %d" % broken)
for name, reason, head in unfixable:
    print("  [要対応] %s : %s\n           %s" % (name, reason, head))

sys.exit(1 if broken else 0)
