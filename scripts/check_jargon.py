# -*- coding: utf-8 -*-
"""用語を「未定義の別の専門用語」で説明していないか検査する

    python3 scripts/check_jargon.py           # 初級ティアだけ（既定・エラー扱い）
    python3 scripts/check_jargon.py --all     # 全ティア（参考表示）

このサイトの読者には、確率統計やデータサイエンスの未経験者が含まれる。
「確証バイアスとは、代表的な認知バイアスの1つ」のように、
説明の中で未定義の用語を使うと、そこで読者は止まってしまう。

初級ティア（M00〜M04）の用語については、これをエラーとして扱う。
上級の用語は前提知識があるため、--all のときだけ参考表示する。

直し方は2つ。
  1. その語自体を用語集に登録する（いちばん良い）
  2. すでに登録済みの語に言い換える
"""
import io, json, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
IDX = os.path.join(ROOT, "docs", "content", "glossary", "index.json")

BEGINNER = {"M00", "M01", "M02", "M03", "M04"}

# 専門用語らしい語尾。ここに当てはまる語だけを見る
SUFFIX = (
    "バイアス", "分析", "検定", "モデル", "統計", "分布", "効果", "相関", "係数",
    "推定", "回帰", "誤差", "仮説", "母集団", "標本", "確率", "指標", "理論",
    "法則", "パラドックス",
)
PAT = re.compile(r"[ァ-ヶー一-龥A-Za-z]{2,12}(?:%s)" % "|".join(SUFFIX))

# 一般語として通じるため、専門用語とみなさないもの
ALLOW = {
    "統計情報", "統計の手法", "時系列の分析", "測定のばらつき",
}

if not os.path.exists(IDX):
    print("用語集インデックスがありません。先に build_glossary_index.py を実行してください")
    sys.exit(0)

data = json.load(io.open(IDX, encoding="utf-8"))
known = {t["term"] for t in data["terms"]}
for t in data["terms"]:
    for a in t.get("aliases") or []:
        known.add(a)

show_all = "--all" in sys.argv
bad, info = [], []
for t in data["terms"]:
    beginner = t.get("source") in BEGINNER
    if not (beginner or show_all):
        continue
    for key in ("short", "plain", "desc"):
        text = str(t.get(key) or "")
        for m in PAT.findall(text):
            if m in known or m in ALLOW or m == t["term"]:
                continue
            # より長い登録語の一部なら、それは別語ではない
            if any(m in x for x in known):
                continue
            (bad if beginner else info).append((t["term"], t.get("source"), key, m))

seen = set()


def rows(items):
    out = []
    for term, src, key, word in items:
        if (term, word) in seen:
            continue
        seen.add((term, word))
        out.append((term, src, key, word))
    return out


bad, info = rows(bad), rows(info)

if bad:
    print("初級ティアの用語が、未定義の専門用語で説明されています（%d件）" % len(bad))
    for term, src, key, word in bad:
        print("  %-16s (%s) の %-5s に「%s」" % (term, src, key, word))
    print("\n直し方: その語を用語集に登録するか、登録済みの語に言い換えてください")
else:
    print("初級ティア: 未定義の専門用語で説明している箇所はありません")

if show_all and info:
    print("\n[参考] 中級以上（エラーにはしません・%d件）" % len(info))
    for term, src, key, word in info[:40]:
        print("  %-16s (%s) の %-5s に「%s」" % (term, src, key, word))

sys.exit(1 if bad else 0)
