# -*- coding: utf-8 -*-
"""
コンテンツ整合性チェック v2

    python3 scripts/validate_content.py            # 検査
    python3 scripts/validate_content.py --summary  # 進捗サマリだけ表示

検査内容
  * 全JSONがパースできるか
  * Mermaid が残っていないか（v2では全面禁止）
  * figure ブロックのJSONが妥当か・既知のtypeか・interactiveのwidget名が実在するか
  * レッスンに why / gain / unlocks / objectives / pl300 があるか
  * prereq のレッスンIDが実在するか
  * PL-300 スキル項目コードが正規のものか
  * クイズの answer が選択肢の範囲内か、1レッスン5問あるか
  * 用語集の重複・必須フィールド
  * ラボが参照するデータファイルが存在するか
終了コード 0 = エラーなし / 1 = エラーあり
"""
import json, os, io, sys, re, glob
from collections import Counter, defaultdict

ROOT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "..")
DOCS = os.path.join(ROOT, "docs")
C = os.path.join(DOCS, "content")

FIGURE_TYPES = {
    "flow", "steps", "compare", "cards", "stack", "matrix", "tablediff",
    "star", "tree", "timeline", "formula", "chart", "pipeline", "interactive",
}
WIDGETS = {
    "filter-context", "star-explorer", "visual-picker", "dax-anatomy",
    "calc-vs-measure", "join-lab", "cardinality-lab", "context-transition",
    "rls-simulator", "granularity-lab",
}
PL300 = {
    "1.1 データソースへの接続", "1.2 データの取得と変換", "1.3 データのプロファイリング",
    "1.4 データのクリーニング", "1.5 データの構造化", "1.6 パフォーマンスを考慮した取り込み",
    "2.1 データモデルの設計", "2.2 リレーションシップの構成", "2.3 計算列とメジャーの作成",
    "2.4 タイムインテリジェンス", "2.5 モデルの最適化", "2.6 行レベルセキュリティ",
    "3.1 レポートの作成", "3.2 ビジュアルの選択と構成", "3.3 対話機能の設定",
    "3.4 レポートの書式とアクセシビリティ", "3.5 データの探索と分析", "3.6 AI ビジュアルの活用",
    "3.7 モバイル対応",
    "4.1 ワークスペースの管理", "4.2 セマンティックモデルの管理", "4.3 データ更新の管理",
    "4.4 アクセス権とセキュリティ", "4.5 ガバナンスとライフサイクル",
}
AREAS = {"データの準備", "データのモデル化", "視覚化と分析", "資産の管理とセキュリティ", "基礎", "データサイエンス"}

errors, warnings = [], []
def err(m): errors.append(m)
def warn(m): warnings.append(m)

def load(path, required=True):
    if not os.path.exists(path):
        if required:
            err("ファイルがありません: %s" % os.path.relpath(path, ROOT))
        return None
    try:
        with io.open(path, encoding="utf-8") as f:
            return json.load(f)
    except Exception as e:
        err("JSONを読めません: %s (%s)" % (os.path.relpath(path, ROOT), e))
        return None


# ---------------------------------------------------------------- モジュール
modules, lessons = [], []
for path in sorted(glob.glob(os.path.join(C, "modules", "M*.json"))):
    m = load(path)
    if not m:
        continue
    mid = m.get("id") or os.path.basename(path)[:-5]
    for k in ("id", "tier", "title", "goal", "lessons"):
        if k not in m:
            err("%s: モジュールに %s がありません" % (mid, k))
    modules.append(m)
    for l in m.get("lessons", []):
        l["_module"] = mid
        l["_tier"] = m.get("tier")
        lessons.append(l)

lesson_ids = {l.get("id") for l in lessons}

for l in lessons:
    lid = l.get("id", "?")
    for k in ("id", "title", "minutes", "type", "why", "gain", "unlocks", "objectives", "prereq", "pl300"):
        if k not in l:
            err("%s: レッスンに %s がありません" % (lid, k))
    for k in ("why", "gain", "unlocks"):
        v = l.get(k)
        if isinstance(v, str) and len(v) < 10:
            warn("%s: %s が短すぎます" % (lid, k))
    for pid in l.get("prereq", []) or []:
        if pid not in lesson_ids:
            err("%s: 前提レッスン %s が存在しません" % (lid, pid))
    for code in l.get("pl300", []) or []:
        if code not in PL300:
            err("%s: 不正なPL-300スキル項目 '%s'" % (lid, code))
    md = os.path.join(C, "lessons", lid + ".md")
    if not os.path.exists(md):
        warn("%s: 本文 %s.md がありません" % (lid, lid))


# ---------------------------------------------------------------- レッスン本文
fig_count, fig_types = 0, Counter()
lesson_lines = {}
for path in sorted(glob.glob(os.path.join(C, "lessons", "*.md"))):
    name = os.path.basename(path)[:-3]
    s = io.open(path, encoding="utf-8").read()
    lesson_lines[name] = len(s.split("\n"))

    if "```mermaid" in s:
        err("%s: Mermaid は廃止されました。figure ブロックに書き換えてください" % name)
    if s.lstrip().startswith("# "):
        err("%s: 本文に H1 を書かないでください（タイトルは自動表示）" % name)

    figs = re.findall(r"```figure\s*\n(.*?)```", s, re.S)
    if name in lesson_ids and len(figs) < 4:
        warn("%s: 図が %d 枚しかありません（4枚以上を推奨）" % (name, len(figs)))
    for raw in figs:
        fig_count += 1
        try:
            cfg = json.loads(raw)
        except Exception as e:
            err("%s: figure のJSONが不正です (%s)" % (name, str(e)[:70]))
            continue
        t = cfg.get("type")
        fig_types[t] += 1
        if t not in FIGURE_TYPES:
            err("%s: 未知の図の種類 '%s'" % (name, t))
        if t == "interactive":
            w = cfg.get("widget")
            if w not in WIDGETS:
                err("%s: 未実装のウィジェット '%s'" % (name, w))


# ---------------------------------------------------------------- ラボ
lab_index = load(os.path.join(C, "labs", "index.json"), required=False)
lab_ids = set()
if lab_index:
    for lab in lab_index.get("labs", []):
        lab_ids.add(lab.get("id"))
        for ds in lab.get("dataset", []) or []:
            if not os.path.exists(os.path.join(DOCS, "data", ds)):
                err("%s: データファイル data/%s がありません" % (lab.get("id"), ds))
        for lid in lab.get("lessons", []) or []:
            if lesson_ids and lid not in lesson_ids:
                warn("%s: 関連レッスン %s が見つかりません" % (lab.get("id"), lid))

for path in sorted(glob.glob(os.path.join(C, "labs", "LAB*.md"))):
    name = os.path.basename(path)[:-3]
    s = io.open(path, encoding="utf-8").read()
    if "```mermaid" in s:
        err("%s: Mermaid は廃止されました" % name)
    for raw in re.findall(r"```figure\s*\n(.*?)```", s, re.S):
        fig_count += 1
        try:
            cfg = json.loads(raw)
            fig_types[cfg.get("type")] += 1
            if cfg.get("type") not in FIGURE_TYPES:
                err("%s: 未知の図の種類 '%s'" % (name, cfg.get("type")))
        except Exception as e:
            err("%s: figure のJSONが不正です (%s)" % (name, str(e)[:70]))
    for old in set(re.findall(r"lesson\.html\?id=(L\d{3})(?!\d)", s)):
        warn("%s: 旧レッスンIDへのリンク %s" % (name, old))


# ---------------------------------------------------------------- クイズ
quiz_total, quiz_files = 0, 0
skill_counter = Counter()
for path in sorted(glob.glob(os.path.join(C, "quizzes", "*.json"))):
    fn = os.path.basename(path)
    if fn in ("index.json", "EXAM-COVERAGE.json"):
        continue
    q = load(path)
    if not q:
        continue
    quiz_files += 1
    qs = q.get("questions", [])
    quiz_total += len(qs)
    is_exam = fn.startswith("EXAM")
    if not is_exam and q.get("lesson") in lesson_ids and len(qs) < 5:
        warn("%s: 設問が %d 問しかありません（5問を推奨）" % (fn, len(qs)))
    seen = set()
    for item in qs:
        qid = item.get("id", "?")
        if qid in seen:
            err("%s: 設問IDが重複しています %s" % (fn, qid))
        seen.add(qid)
        n = len(item.get("choices", []))
        if n < 2:
            err("%s / %s: 選択肢が足りません" % (fn, qid))
        a = item.get("answer")
        for i in (a if isinstance(a, list) else [a]):
            if not isinstance(i, int) or i < 0 or i >= n:
                err("%s / %s: answer %s が選択肢(%d件)の範囲外" % (fn, qid, a, n))
        if not item.get("explain"):
            err("%s / %s: 解説がありません" % (fn, qid))
        if item.get("area") and item["area"] not in AREAS:
            warn("%s / %s: 未知のarea '%s'" % (fn, qid, item["area"]))
        if item.get("skill"):
            skill_counter[item["skill"]] += 1
            if item["skill"] not in PL300:
                err("%s / %s: 不正なskill '%s'" % (fn, qid, item["skill"]))
        ref = item.get("ref")
        if ref and lesson_ids and ref not in lesson_ids:
            warn("%s / %s: 参照レッスン %s が見つかりません" % (fn, qid, ref))


# ---------------------------------------------------------------- 用語集
FIG_TYPES = {"flow", "steps", "compare", "cards", "stack", "matrix", "tablediff",
             "star", "tree", "timeline", "formula", "chart", "pipeline", "interactive"}
# 予備知識ゼロの読者がつまずくのは統計・データサイエンス系の用語なので、
# これらには「かんたんに言うと」(plain) と図(figure) を必須にする。
PLAIN_TAGS = {"統計", "データサイエンス", "分析"}

terms, term_seen, dup_terms = 0, {}, []
no_plain, no_fig = [], []
for path in sorted(glob.glob(os.path.join(C, "glossary", "*.json"))):
    if os.path.basename(path) == "index.json":
        continue
    g = load(path)
    if not isinstance(g, list):
        if g is not None:
            err("%s: 用語集は配列である必要があります" % os.path.basename(path))
        continue
    for t in g:
        terms += 1
        name = t.get("term")
        if not name:
            err("%s: term がない用語があります" % os.path.basename(path))
            continue
        if name in term_seen:
            dup_terms.append(name)
        term_seen[name] = os.path.basename(path)
        for k in ("short", "desc"):
            if not t.get(k):
                warn("用語'%s': %s がありません" % (name, k))
        tags = set(t.get("tags") or [])
        if tags & PLAIN_TAGS:
            if not t.get("plain"):
                no_plain.append(name)
            if not t.get("figure"):
                no_fig.append(name)
        fig = t.get("figure")
        if fig is not None:
            if not isinstance(fig, dict):
                err("用語'%s': figure はオブジェクトである必要があります" % name)
            elif fig.get("type") not in FIG_TYPES:
                err("用語'%s': figure の type が不正です (%s)" % (name, fig.get("type")))
        if t.get("lesson") and lesson_ids and t["lesson"] not in lesson_ids:
            warn("用語'%s': レッスン %s が見つかりません" % (name, t["lesson"]))


# ---------------------------------------------------------------- 出力
if no_plain:
    warn("統計・データサイエンス系の用語 %d 件に plain（かんたんな説明）がありません: %s ほか"
         % (len(no_plain), "、".join(sorted(set(no_plain))[:6])))
if no_fig:
    warn("統計・データサイエンス系の用語 %d 件に figure（図解）がありません: %s ほか"
         % (len(no_fig), "、".join(sorted(set(no_fig))[:6])))
if dup_terms:
    warn("複数モジュールで定義が重複している用語が %d 件あります（ビルド時にモジュール固有の定義を採用します）: %s ほか"
         % (len(dup_terms), "、".join(sorted(set(dup_terms))[:6])))

tier_counts = Counter(l.get("_tier") for l in lessons)
# v3 では本文を 100〜210 行に圧縮する方針なので、極端に短いものだけ警告する
short_lessons = {k: v for k, v in lesson_lines.items() if k in lesson_ids and v < 100}

print("=" * 62)
print(" コンテンツ サマリ")
print("=" * 62)
print("  モジュール : %3d" % len(modules))
print("  レッスン   : %3d 定義 / %3d 本文あり" % (len(lessons), sum(1 for l in lesson_ids if l in lesson_lines)))
for t in sorted(tier_counts):
    print("      %s : %d 本" % (t, tier_counts[t]))
print("  本文の行数 : 合計 %s 行 / 平均 %d 行" % (
    format(sum(lesson_lines.values()), ","),
    (sum(lesson_lines.values()) // len(lesson_lines)) if lesson_lines else 0))
print("  図         : %3d 枚  %s" % (fig_count, dict(fig_types.most_common(6))))
print("  ラボ       : %3d 本" % len(glob.glob(os.path.join(C, "labs", "LAB*.md"))))
print("  設問       : %3d 問 (%d ファイル)" % (quiz_total, quiz_files))
print("  用語       : %3d 語" % terms)
if skill_counter:
    lo = [k for k in PL300 if skill_counter.get(k, 0) < 8]
    print("  PL-300     : %d / 24 スキル項目に出題あり%s" % (
        len(PL300) - len(lo), ("（8問未満: %d項目）" % len(lo)) if lo else ""))
print("=" * 62)

if "--summary" in sys.argv:
    sys.exit(0)

if short_lessons:
    for k in sorted(short_lessons)[:10]:
        warn("%s: 本文が %d 行と短めです" % (k, short_lessons[k]))

for w in warnings[:60]:
    print("  [警告] " + w)
if len(warnings) > 60:
    print("  [警告] ... 他 %d 件" % (len(warnings) - 60))
for e in errors[:60]:
    print("  [エラー] " + e)
if len(errors) > 60:
    print("  [エラー] ... 他 %d 件" % (len(errors) - 60))

print("\nエラー %d 件 / 警告 %d 件" % (len(errors), len(warnings)))
sys.exit(1 if errors else 0)
