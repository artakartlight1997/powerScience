"""充填計画と停止判定。純関数のみ(C-2)。

plan は gap の順位のみを返す(数値スコアは契約上返さない — 偽の精度を出さない)。
should_stop は必ず理由つきで停止する(P15: 長く回すほど良くなるは幻想)。
"""
from __future__ import annotations

from .contracts import Judgment, Question, SpecItem

import re

_DEP = {"high": 0, "mid": 1, "low": 2}
_STATUS = {"missing": 0, "thin": 1, "unknown": 2}
_CHANNEL_MAP = {"public": "web", "premium": "premium", "vdr": "vdr",
                "expert": "expert", "calc": "mgmt", "web": "web"}
PUBLIC_CHANNELS = {"public", "premium", "web"}  # audit / research と共有する唯一の定義


def is_public_reachable(item: SpecItem) -> bool:
    """公開経路(Web/有償DB)で取れる見込みがあるか。R4 判定・クエリ計画・audit で共用。"""
    return any(ch in PUBLIC_CHANNELS for ch in item.retrievability)


def gaps(items: list[SpecItem], judgments: dict[str, Judgment]) -> list[SpecItem]:
    return [it for it in items
            if judgments.get(it.id) is None or judgments[it.id].status != "filled"]


def open_public_gaps(items: list[SpecItem], judgments: dict[str, Judgment]) -> int:
    """公開経路でまだ探索余地のある gap 数。R4(公開経路の完了)の唯一の判定材料。
    質問リスト(上限で切られる)から数えると偽の R4 停止を起こすため、項目から直接数える。"""
    return sum(1 for it in gaps(items, judgments) if is_public_reachable(it))


def _box_order(box: str) -> int:
    m = re.search(r"\d+", box)
    return int(m.group()) if m else 999  # "box10" を "box2" より後ろに(辞書順の罠)


def plan(items: list[SpecItem], judgments: dict[str, Judgment]) -> list[str]:
    """gap 項目の id を優先順で返す。must > thesis_dependence > 状態 > 箱の順。"""
    def sort_key(it: SpecItem):
        j = judgments.get(it.id)
        st = _STATUS.get(j.status, 0) if j else 0
        return (not it.must, _DEP[it.dependence], st, _box_order(it.box), it.key)
    return [it.id for it in sorted(gaps(items, judgments), key=sort_key)]


def make_questions(case_id: str, items: list[SpecItem],
                   judgments: dict[str, Judgment], max_open: int) -> list[Question]:
    """gap を「問い + 取得チャネル」に変換する。unknown は発注仕様書行き(vdr/expert)。"""
    by_id = {it.id: it for it in items}
    out: list[Question] = []
    for rank, item_id in enumerate(plan(items, judgments)[:max_open], start=1):
        it = by_id[item_id]
        j = judgments.get(item_id)
        # 公開経路が1つでもあれば公開チャネルを優先する([vdr, public] は web へ)。
        # 先頭要素だけ見ると audit/research の「含む」判定と食い違い、R4 が偽発火する
        if "public" in it.retrievability or "web" in it.retrievability:
            channel = "web"
        elif "premium" in it.retrievability:
            channel = "premium"
        else:
            channel = _CHANNEL_MAP.get(
                it.retrievability[0] if it.retrievability else "expert", "expert")
        status = j.status if j else "missing"
        why = f"現状{status}" + (f"({j.rationale})" if j and j.rationale else "")
        seg = f"[{it.segment}] " if it.segment else ""
        out.append(Question(id=f"q-{case_id}-{it.key}", case_id=case_id,
                            item_key=it.key, text=f"{seg}{it.label} — {why}",
                            channel=channel, rank=rank))
    return out


def should_stop(round_no: int, llm_calls: int, new_progress: int,
                open_public_gaps: int, stop_rules: dict) -> tuple[bool, str | None]:
    """停止判定。(bool, reason)。reason なしの停止は存在しない(契約 §3)。"""
    if open_public_gaps == 0:
        return True, "R4: 公開経路の gap ゼロ(残りは vdr/expert 行き=発注仕様書へ)"
    if round_no >= int(stop_rules["max_iterations"]):
        return True, f"R1: ラウンド上限 {stop_rules['max_iterations']} に到達(P15)"
    if llm_calls >= int(stop_rules["max_llm_calls"]):
        return True, f"R2: LLM呼び出し上限 {stop_rules['max_llm_calls']} に到達"
    if round_no > 1 and new_progress < int(stop_rules["min_new_filled_per_iter"]):
        return True, f"R3: 収穫逓減(新規進捗 {new_progress} 件/ラウンド)"
    return False, None
