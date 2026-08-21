# -*- coding: utf-8 -*-
"""用語を「未定義の別の専門用語」で説明していないか検査する

    python3 scripts/check_jargon.py

このサイトの読者には、確率統計やデータサイエンスの未経験者が含まれる。
「確証バイアスとは、代表的な認知バイアスの1つ」のように、
説明の中で未定義の用語を使うと、そこで読者は止まってしまう。

初級・上級を問わず、すべての用語をエラーとして扱う。

直し方は2つ。
  1. その語自体を用語集に登録する（いちばん良い）
  2. すでに登録済みの語に言い換える
"""
import io, json, os, re, sys

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
IDX = os.path.join(ROOT, "docs", "content", "glossary", "index.json")

# 専門用語らしい語尾。ここに当てはまる語だけを見る
SUFFIX = (
    "バイアス", "分析", "検定", "モデル", "統計", "分布", "効果", "相関", "係数",
    "推定", "回帰", "誤差", "仮説", "母集団", "標本", "確率", "指標", "理論",
    "法則", "パラドックス",
)
PAT = re.compile(r"[ァ-ヶー一-龥A-Za-z]{2,12}(?:%s)" % "|".join(SUFFIX))

# 一般語の組み合わせであって「調べないと分からない用語」ではないもの。
# ここに足すのは、"AのB" と読めば意味が通る複合語だけにする。
ALLOW = {
    "統計情報", "統計の手法", "時系列の分析", "測定のばらつき",
    # 「〜のモデル」「〜の指標」と読めば通じる複合語
    "分析モデル", "予測モデル", "販売モデル", "購買モデル", "複数モデル",
    "大規模モデル", "小規模モデル", "既存モデル", "子集合モデル", "テーブルモデル",
    "Lakeモデル", "ADKARモデル", "モデル分析",
    "主要指標", "業務指標", "財務指標", "相対指標", "比率指標", "精度指標",
    "時系列指標",
    # 「〜のテーブル/クエリ/統計/分布」と読めば通じるもの
    "起点テーブル", "パラメータテーブル", "閉包テーブル", "オープンテーブル",
    "マルチテーブル", "DAXクエリ", "内部クエリ", "ソース側クエリ",
    "要約統計", "政府統計", "詳細統計", "スコア分布",
    "内部エンジン", "分散処理エンジン", "行列理論", "学習効果", "年間効果",
    "測定誤差",
}

if not os.path.exists(IDX):
    print("用語集インデックスがありません。先に build_glossary_index.py を実行してください")
    sys.exit(0)

data = json.load(io.open(IDX, encoding="utf-8"))
known = {t["term"] for t in data["terms"]}
for t in data["terms"]:
    for a in t.get("aliases") or []:
        known.add(a)

bad = []
for t in data["terms"]:
    for key in ("short", "plain", "desc"):
        text = str(t.get(key) or "")
        for m in PAT.findall(text):
            if m in known or m in ALLOW or m == t["term"]:
                continue
            # より長い登録語の一部なら、それは別語ではない
            if any(m in x for x in known):
                continue
            bad.append((t["term"], t.get("source"), key, m))

seen = set()


def rows(items):
    out = []
    for term, src, key, word in items:
        if (term, word) in seen:
            continue
        seen.add((term, word))
        out.append((term, src, key, word))
    return out


bad = rows(bad)

if bad:
    print("用語が、未定義の専門用語で説明されています（%d件）" % len(bad))
    for term, src, key, word in bad:
        print("  %-16s (%s) の %-5s に「%s」" % (term, src, key, word))
    print("\n直し方: その語を用語集に登録するか、登録済みの語に言い換えてください")
else:
    print("用語の説明: 未定義の専門用語で説明している箇所はありません（全%d語）" % len(data["terms"]))

sys.exit(1 if bad else 0)
