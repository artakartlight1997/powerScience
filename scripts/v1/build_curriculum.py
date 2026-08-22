#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
build_curriculum.py — docs/content/modules/M*.json を統合して
  docs/content/curriculum.json  (サイト全体が読む統合カリキュラム)
  docs/content/pl300.json       (PL-300スキル項目 → レッスン の逆引き)
を生成する。

・モジュールJSONが1つも無くても、欠番があっても落ちない。
・既存 curriculum.json は初回だけ curriculum.v1.json としてバックアップする。
・旧ページ (progress.html / quizzes.html / labs.html / lesson.html / lab.html) が
  参照する `levels` / `levelById` / `lesson.level` / `lab.level` との互換を保つため、
  ティアを `levels` としても出力し、レッスンとラボに `level`(=ティアID) を付ける。

usage:  python3 scripts/build_curriculum.py
"""

import io, json
import os
import sys
import datetime
import glob
import re

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
CONTENT = os.path.join(ROOT, "docs", "v1", "content")
MODULES_DIR = os.path.join(CONTENT, "modules")
OUT_CURRICULUM = os.path.join(CONTENT, "curriculum.json")
OUT_PL300 = os.path.join(CONTENT, "pl300.json")
BACKUP = os.path.join(CONTENT, "curriculum.v1.json")

VERSION = "2.0.0"
PLANNED = {"tiers": 4, "modules": 22, "lessons": 118, "labs": 6}

# --------------------------------------------------------------------------
# ティア定義（このスクリプトが唯一の正）
# --------------------------------------------------------------------------
TIERS = [
    {
        "id": "T1", "order": 1, "title": "初級", "en": "Beginner",
        "subtitle": "土台を作る",
        "goal": "BIの考え方を理解し、自分でレポートを1枚作れる",
        "color": "#2f6fed",
        "examWeight": None,
    },
    {
        "id": "T2", "order": 2, "title": "中級", "en": "Intermediate",
        "subtitle": "実務で使えるようになる",
        "goal": "実務データを整形し正しいモデルを組み、必要な指標をDAXで書ける",
        "color": "#14926b",
        "examWeight": "PL-300 出題領域 1・2 の中核",
    },
    {
        "id": "T3", "order": 3, "title": "上級", "en": "Advanced",
        "subtitle": "難しい要件と性能を扱う",
        "goal": "性能・複雑要件・組織展開を扱え、PL-300に合格できる",
        "color": "#c77700",
        "examWeight": "PL-300 出題領域 3・4 と総仕上げ",
    },
    {
        "id": "T4", "order": 4, "title": "プロ", "en": "Professional",
        "subtitle": "組織を動かし価値を出す",
        "goal": "設計をリードし、データから事業価値を出せる",
        "color": "#7c4dff",
        "examWeight": None,
    },
]
TIER_IDS = [t["id"] for t in TIERS]

# --------------------------------------------------------------------------
# PL-300 スキル項目（AUTHORING_SPEC.md §7 の24項目）
# --------------------------------------------------------------------------
PL300_AREAS = [
    {
        "id": "A1", "title": "データの準備", "weight": "25-30%",
        "skills": [
            "1.1 データソースへの接続",
            "1.2 データの取得と変換",
            "1.3 データのプロファイリング",
            "1.4 データのクリーニング",
            "1.5 データの構造化",
            "1.6 パフォーマンスを考慮した取り込み",
        ],
    },
    {
        "id": "A2", "title": "データのモデル化", "weight": "25-30%",
        "skills": [
            "2.1 データモデルの設計",
            "2.2 リレーションシップの構成",
            "2.3 計算列とメジャーの作成",
            "2.4 タイムインテリジェンス",
            "2.5 モデルの最適化",
            "2.6 行レベルセキュリティ",
        ],
    },
    {
        "id": "A3", "title": "視覚化と分析", "weight": "25-30%",
        "skills": [
            "3.1 レポートの作成",
            "3.2 ビジュアルの選択と構成",
            "3.3 対話機能の設定",
            "3.4 レポートの書式とアクセシビリティ",
            "3.5 データの探索と分析",
            "3.6 AI ビジュアルの活用",
            "3.7 モバイル対応",
        ],
    },
    {
        "id": "A4", "title": "資産の管理とセキュリティ", "weight": "15-20%",
        "skills": [
            "4.1 ワークスペースの管理",
            "4.2 セマンティックモデルの管理",
            "4.3 データ更新の管理",
            "4.4 アクセス権とセキュリティ",
            "4.5 ガバナンスとライフサイクル",
        ],
    },
]
ALL_SKILLS = [s for a in PL300_AREAS for s in a["skills"]]
SKILL_CODE = {}
for _a in PL300_AREAS:
    for _s in _a["skills"]:
        SKILL_CODE[_s.split(" ", 1)[0]] = _s

# ラボの旧レベル → ティア（レッスンからの逆引きに失敗したときのフォールバック）
LAB_LEVEL_FALLBACK = {"L0": "T1", "L1": "T2", "L2": "T2", "L3": "T2", "L4": "T3", "L5": "T4"}

FALLBACK_LABS = [
    {"id": "LAB01", "title": "はじめてのレポート — 売上ダッシュボードを30分で作る", "level": "T1",
     "minutes": 30, "difficulty": 1, "dataset": ["sales.csv"],
     "goal": "CSVを読み込み、KPIカード・棒グラフ・折れ線を配置したレポートを完成させる。"},
    {"id": "LAB02", "title": "汚いデータを洗う — Power Query実践", "level": "T2",
     "minutes": 45, "difficulty": 2, "dataset": ["sales_dirty.csv"],
     "goal": "全角空白・型崩れ・横持ち・重複を含むデータを整然データに変換する。"},
    {"id": "LAB03", "title": "スタースキーマを組む", "level": "T2",
     "minutes": 45, "difficulty": 3, "dataset": ["sales.csv", "products.csv", "customers.csv", "stores.csv"],
     "goal": "フラットな表を分解し、日付テーブルを含むスタースキーマを構築する。"},
    {"id": "LAB04", "title": "DAXメジャー10本ノック", "level": "T2",
     "minutes": 60, "difficulty": 4, "dataset": ["sales.csv", "products.csv", "customers.csv", "stores.csv"],
     "goal": "売上・粗利・前年比・累計・構成比・ランキングなど10指標を実装する。"},
    {"id": "LAB05", "title": "伝わるダッシュボード設計 + モバイル対応", "level": "T3",
     "minutes": 60, "difficulty": 3, "dataset": ["sales.csv", "products.csv", "customers.csv", "stores.csv"],
     "goal": "1画面で意思決定できるレポートを設計し、スマホビューまで作り込む。"},
    {"id": "LAB06", "title": "RLSを設定して安全に配布する", "level": "T4",
     "minutes": 45, "difficulty": 4, "dataset": ["stores.csv", "security_users.csv"],
     "goal": "店舗別に閲覧範囲を絞る動的RLSを実装し、アプリとして配布する。"},
]


def warn(msg):
    sys.stderr.write("  ! " + msg + "\n")


def load_json(path):
    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return None
    except Exception as e:
        warn("%s を読めませんでした: %s" % (os.path.basename(path), e))
        return None


def module_sort_key(m):
    order = m.get("order")
    if not isinstance(order, int):
        digits = re.sub(r"\D", "", str(m.get("id") or ""))
        order = int(digits) if digits else 999
    tier = m.get("tier") if m.get("tier") in TIER_IDS else "T9"
    return (TIER_IDS.index(tier) if tier in TIER_IDS else 9, order, str(m.get("id") or ""))


def read_modules():
    """docs/v1/content/modules/M*.json をすべて読む。壊れたファイル・欠番はスキップ。"""
    mods = []
    if not os.path.isdir(MODULES_DIR):
        warn("modules ディレクトリがありません: %s" % MODULES_DIR)
        return mods
    for path in sorted(glob.glob(os.path.join(MODULES_DIR, "M*.json"))):
        data = load_json(path)
        name = os.path.basename(path)
        if not isinstance(data, dict):
            warn("%s: オブジェクトではないのでスキップ" % name)
            continue
        mid = data.get("id") or os.path.splitext(name)[0]
        data["id"] = mid
        if data.get("tier") not in TIER_IDS:
            warn("%s: tier が不正 (%r) のためスキップ" % (name, data.get("tier")))
            continue
        lessons = data.get("lessons")
        if not isinstance(lessons, list):
            warn("%s: lessons が配列ではありません。空として扱います" % name)
            data["lessons"] = []
        mods.append(data)
    mods.sort(key=module_sort_key)
    return mods


def as_list(v):
    if v is None:
        return []
    if isinstance(v, list):
        return [x for x in v if x is not None]
    return [v]


def build():
    modules_raw = read_modules()

    # ---- 既存 curriculum.json（ラボの引き継ぎ用）------------------------
    old = load_json(OUT_CURRICULUM) or {}
    old_labs = old.get("labs")
    if not isinstance(old_labs, list) or not old_labs:
        old_labs = None

    # 初回だけバックアップを残す
    if old and not os.path.exists(BACKUP) and old.get("meta", {}).get("version") != VERSION:
        with open(BACKUP, "w", encoding="utf-8") as f:
            json.dump(old, f, ensure_ascii=False, indent=2)
        print("  backup -> %s" % os.path.relpath(BACKUP, ROOT))

    # ---- モジュール & レッスン -----------------------------------------
    tier_by_id = {t["id"]: t for t in TIERS}
    modules = []
    lessons = []
    lab_tier = {}
    order = 0

    for m in modules_raw:
        tid = m["tier"]
        tier = tier_by_id[tid]
        mlessons = m.get("lessons") or []
        minutes = sum(int(l.get("minutes") or 0) for l in mlessons if isinstance(l, dict))
        mod = {
            "id": m["id"],
            "tier": tid,
            "tierTitle": tier["title"],
            "tierColor": tier["color"],
            "order": m.get("order"),
            "title": m.get("title") or m["id"],
            "subtitle": m.get("subtitle") or "",
            "goal": m.get("goal") or "",
            "estimatedHours": m.get("estimatedHours") or 0,
            "lessonCount": len(mlessons),
            "minutes": minutes,
            "lessonIds": [],
        }
        for l in mlessons:
            if not isinstance(l, dict) or not l.get("id"):
                warn("%s: id の無いレッスンをスキップ" % m["id"])
                continue
            order += 1
            lesson = dict(l)
            lesson["module"] = m["id"]
            lesson["moduleTitle"] = mod["title"]
            lesson["tier"] = tid
            lesson["level"] = tid          # 旧ページ互換（lessonsOfLevel / levelById）
            lesson["order"] = order
            lesson["minutes"] = int(l.get("minutes") or 0)
            lesson["pl300"] = as_list(l.get("pl300"))
            lesson["ds"] = as_list(l.get("ds"))
            lesson["prereq"] = as_list(l.get("prereq"))
            lesson["keywords"] = as_list(l.get("keywords"))
            lesson["objectives"] = as_list(l.get("objectives"))
            lessons.append(lesson)
            mod["lessonIds"].append(lesson["id"])
            if lesson.get("lab"):
                lab_tier.setdefault(lesson["lab"], tid)
        modules.append(mod)

    # ---- ティア ---------------------------------------------------------
    tiers = []
    for t in TIERS:
        mine = [m for m in modules if m["tier"] == t["id"]]
        hours = sum(int(m.get("estimatedHours") or 0) for m in mine)
        lesson_n = sum(m["lessonCount"] for m in mine)
        tiers.append({
            "id": t["id"],
            "order": t["order"],
            "title": t["title"],
            "en": t["en"],
            "subtitle": t["subtitle"],
            "goal": t["goal"],
            "color": t["color"],
            "hours": hours,
            "estimatedHours": hours,       # 旧ページ互換
            "examWeight": t["examWeight"],
            "moduleIds": [m["id"] for m in mine],
            "moduleCount": len(mine),
            "lessonCount": lesson_n,
            "minutes": sum(m["minutes"] for m in mine),
        })

    # ---- ラボ -----------------------------------------------------------
    # ラボは docs/content/labs/index.json を正とする（無ければ旧定義にフォールバック）
    lab_index_path = os.path.join(CONTENT, "labs", "index.json")
    index_labs = None
    if os.path.exists(lab_index_path):
        try:
            index_labs = json.load(io.open(lab_index_path, encoding="utf-8")).get("labs")
            if not isinstance(index_labs, list) or not index_labs:
                index_labs = None
        except Exception as e:
            print("  警告: labs/index.json を読めません (%s)" % e)
            index_labs = None

    src_labs = index_labs if index_labs is not None else (old_labs if old_labs is not None else FALLBACK_LABS)
    labs = []
    for lb in src_labs:
        if not isinstance(lb, dict):
            continue
        lab = dict(lb)
        legacy = lab.get("level")
        tid = lab_tier.get(lab.get("id"))
        if tid not in TIER_IDS:
            tid = LAB_LEVEL_FALLBACK.get(legacy, legacy if legacy in TIER_IDS else "T1")
        lab["legacyLevel"] = legacy
        lab["tier"] = tid
        lab["level"] = tid                 # 旧ページ互換
        labs.append(lab)

    # ---- 本文と図の数を数える -------------------------------------------
    lessons_dir = os.path.join(CONTENT, "lessons")
    figures = 0
    written = 0
    fig_re = re.compile(r"^\s*```figure\s*$", re.M)
    for l in lessons:
        path = os.path.join(lessons_dir, l["id"] + ".md")
        try:
            with open(path, "r", encoding="utf-8") as f:
                body = f.read()
        except Exception:
            l["hasBody"] = False
            l["figures"] = 0
            continue
        n = len(fig_re.findall(body))
        l["hasBody"] = True
        l["figures"] = n
        figures += n
        written += 1

    # ---- 出力 -----------------------------------------------------------
    today = datetime.date.today().isoformat()
    curriculum = {
        "meta": {
            "title": "Aki’s Power BI 道場",
            "subtitle": "初学者からPL-300認定合格・実務のプロへ",
            "version": VERSION,
            "targetExam": "PL-300",
            "updated": today,
            "counts": {
                "tiers": len(tiers),
                "modules": len(modules),
                "lessons": len(lessons),
                "labs": len(labs),
                "figures": figures,
                "lessonsWritten": written,
                "modulesPlanned": PLANNED["modules"],
                "lessonsPlanned": PLANNED["lessons"],
            },
            "planned": dict(PLANNED),
        },
        "tiers": tiers,
        "levels": tiers,      # 旧ページ互換のエイリアス
        "modules": modules,
        "lessons": lessons,
        "labs": labs,
    }

    with open(OUT_CURRICULUM, "w", encoding="utf-8") as f:
        json.dump(curriculum, f, ensure_ascii=False, indent=2)
        f.write("\n")

    # ---- PL-300 逆引き ---------------------------------------------------
    index = {s: [] for s in ALL_SKILLS}
    unknown = set()
    for l in lessons:
        for raw in l["pl300"]:
            key = str(raw).strip()
            if key not in index:
                code = key.split(" ", 1)[0]
                if code in SKILL_CODE:      # 表記ゆれはコードで吸収する
                    key = SKILL_CODE[code]
                else:
                    unknown.add(raw)
                    continue
            index[key].append({
                "id": l["id"], "title": l.get("title") or l["id"],
                "module": l["module"], "moduleTitle": l["moduleTitle"],
                "tier": l["tier"], "minutes": l["minutes"], "order": l["order"],
            })
    for v in index.values():
        v.sort(key=lambda x: x["order"])

    pl300 = {
        "meta": {
            "exam": "PL-300",
            "name": "Microsoft Power BI Data Analyst",
            "updated": today,
            "official": "https://learn.microsoft.com/ja-jp/credentials/certifications/exams/pl-300/",
            "skillCount": len(ALL_SKILLS),
            "coveredCount": sum(1 for s in ALL_SKILLS if index[s]),
        },
        "areas": [
            {
                "id": a["id"], "title": a["title"], "weight": a["weight"],
                "skills": [
                    {"code": s.split(" ", 1)[0], "title": s.split(" ", 1)[1], "skill": s,
                     "lessons": index[s], "lessonCount": len(index[s])}
                    for s in a["skills"]
                ],
            }
            for a in PL300_AREAS
        ],
        "index": index,
    }
    with open(OUT_PL300, "w", encoding="utf-8") as f:
        json.dump(pl300, f, ensure_ascii=False, indent=2)
        f.write("\n")

    if unknown:
        warn("未知のPL-300スキル項目（無視しました）: " + ", ".join(sorted(map(str, unknown))))

    # ---- ログ -----------------------------------------------------------
    print("curriculum.json を生成しました")
    print("  tiers   : %d" % len(tiers))
    print("  modules : %d / %d" % (len(modules), PLANNED["modules"]))
    print("  lessons : %d / %d" % (len(lessons), PLANNED["lessons"]))
    print("  labs    : %d" % len(labs))
    print("  figures : %d  (本文あり %d レッスン)" % (figures, written))
    for t in tiers:
        print("    %s %-4s modules=%-2d lessons=%-3d hours=%d"
              % (t["id"], t["title"], t["moduleCount"], t["lessonCount"], t["hours"]))
    missing = [m for m in ("M%02d" % i for i in range(1, PLANNED["modules"] + 1))
               if m not in {x["id"] for x in modules}]
    if missing:
        print("  未作成のモジュール: " + ", ".join(missing))
    print("pl300.json を生成しました（%d/%d 項目にレッスンあり）"
          % (pl300["meta"]["coveredCount"], len(ALL_SKILLS)))
    return 0


if __name__ == "__main__":
    sys.exit(build())
