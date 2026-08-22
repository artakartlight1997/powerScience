"""検証層: grounding(原文照合)・独立性クラスタ(P22)・矛盾検出(P20)。

grounding は「良い/悪い」を聞かない。原文支持の二値判定のみ、提示順を入れ替えて
2回聞く(P10)。判定モデルは verifier ロール = 生成と別ベンダ(C-6)。
矛盾は削除も平均もしない — 検出して保存するだけの API しか存在しない。
"""
from __future__ import annotations

import difflib
import logging
import re
import uuid
from collections import defaultdict

from .contracts import Contradiction, Evidence, Grounded, LLMClient, LLMError

log = logging.getLogger(__name__)

_WS = re.compile(r"\s+")
_WINDOW = 16000  # extract._MAX_CHARS と揃える(抽出できた位置の引用が照合窓から漏れないように)

# 単位表記 → 次元。「10億円」と「1,500百万円」は同じ次元(円)として比較する
_DIM = {"兆円": "円", "億円": "円", "百万円": "円", "万円": "円", "千円": "円",
        "円": "円", "%": "%", "％": "%", "万人": "人", "人": "人", "名": "人",
        "件": "件", "社": "社"}

VERIFY_SYSTEM = """与えられた原文抜粋が、与えられた引用文を逐語的または実質的に含むかだけを判定せよ。
内容の良し悪しは判定しない。出力は {"supported": true} または {"supported": false} のみ。"""


def _norm(s: str) -> str:
    return _WS.sub("", s)


def _dim(unit: str | None) -> str | None:
    return _DIM.get(unit) if unit else None


def ground(ev: Evidence, snap_text: str | None, llm: LLMClient) -> Grounded:
    """原文支持の判定。スナップショットが無ければ pass にはならない(契約 §3)。"""
    if not snap_text:
        log.warning("grounding: 証拠 %s に照合先スナップショットがない → fail", ev.id)
        return "fail"
    if _norm(ev.quote) and _norm(ev.quote) in _norm(snap_text):
        return "pass"  # 決定的照合が最優先(LLM を使わない)
    if len(snap_text) > _WINDOW:
        log.warning("grounding: 証拠 %s の照合窓を %d 字に切り詰め(原文 %d 字)",
                    ev.id, _WINDOW, len(snap_text))  # C-8: 縮退は黙って起きない
    window = snap_text[:_WINDOW]
    votes = []
    for order in ("ab", "ba"):  # P10: 提示順を入れ替えて2回
        if order == "ab":
            user = f"## 引用文\n{ev.quote}\n\n## 原文抜粋\n{window}"
        else:
            user = f"## 原文抜粋\n{window}\n\n## 引用文\n{ev.quote}"
        try:
            out = llm.complete_json("verifier", VERIFY_SYSTEM, user)
            votes.append(bool(out.get("supported", False)))
        except LLMError as e:
            log.warning("grounding: 証拠 %s の判定票が取れず不支持に倒す: %s", ev.id, e)
            votes.append(False)  # 検証できない票は不支持に倒す(捏造を通さない)
    if all(votes):
        return "pass"
    return "partial" if any(votes) else "fail"


def cluster(evidences: list[Evidence]) -> list[Evidence]:
    """独立性クラスタの付与(P22)。同一項目で「同じ次元の数値が一致」または
    「数値で区別できず文面が高類似」の証拠は同一クラスタ = 独立支持として二重に
    数えない。union-find で連結成分に併合するため入力順に依存しない(決定性)。
    純関数的(新リスト返却)。"""
    by_item: dict[str, list[Evidence]] = defaultdict(list)
    for e in evidences:
        by_item[e.item_key].append(e)
    out: list[Evidence] = []
    for key, evs in by_item.items():
        parent = list(range(len(evs)))

        def find(i: int) -> int:
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        for i in range(len(evs)):
            for j in range(i + 1, len(evs)):
                if _same_cluster(evs[i], evs[j]):
                    parent[find(j)] = find(i)
        # クラスタ番号は「成分内の最小インデックス」で安定化
        for e, i in zip(evs, range(len(evs))):
            out.append(e.model_copy(update={"cluster_id": f"{key}-c{find(i)}"}))
    return out


def _same_cluster(a: Evidence, b: Evidence) -> bool:
    an = a.value.num if a.value else None
    bn = b.value.num if b.value else None
    if an is not None and bn is not None and _dim(a.value.unit) == _dim(b.value.unit):
        # 同じ次元の数値同士は数値だけで判定する。数値が異なるのに文面類似で
        # 併合すると、矛盾検出(同一クラスタ対は除外)を構造的に殺す(P20)
        base = max(abs(an), abs(bn), 1e-9)
        return abs(an - bn) / base < 1e-3
    return difflib.SequenceMatcher(None, _norm(a.quote), _norm(b.quote)).ratio() > 0.85


def contradictions(case_id: str, evidences: list[Evidence],
                   existing: list[Contradiction], tolerance: float = 0.15,
                   ) -> list[Contradiction]:
    """同一項目で数値が tolerance 超乖離する別クラスタ対 → 矛盾(P20)。
    既存の対は再登録しない。解消はここでは起きない(追加証拠の判断は人間)。"""
    seen = {frozenset((c.evidence_a, c.evidence_b)) for c in existing}
    found: list[Contradiction] = []
    by_item: dict[str, list[Evidence]] = defaultdict(list)
    for e in evidences:
        if e.value and e.value.num is not None and e.grounded == "pass":
            by_item[e.item_key].append(e)
    for key, evs in by_item.items():
        for i in range(len(evs)):
            for j in range(i + 1, len(evs)):
                a, b = evs[i], evs[j]
                if a.cluster_id == b.cluster_id:
                    continue
                # 次元が違う数値の比較は矛盾と断定しない
                # (「10億円」vs「1,500百万円」は同一次元=円として比較される)
                if _dim(a.value.unit) != _dim(b.value.unit):
                    continue
                base = max(abs(a.value.num), abs(b.value.num), 1e-9)
                delta = abs(a.value.num - b.value.num) / base
                if delta > tolerance and frozenset((a.id, b.id)) not in seen:
                    found.append(Contradiction(
                        id=f"cx-{uuid.uuid4().hex[:12]}", case_id=case_id,
                        item_key=key, evidence_a=a.id, evidence_b=b.id,
                        delta=round(delta, 4)))
    return found
