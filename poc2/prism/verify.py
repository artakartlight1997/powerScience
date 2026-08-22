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
    errors = 0
    for order in ("ab", "ba"):  # P10: 提示順を入れ替えて2回
        if order == "ab":
            user = f"## 引用文\n{ev.quote}\n\n## 原文抜粋\n{window}"
        else:
            user = f"## 原文抜粋\n{window}\n\n## 引用文\n{ev.quote}"
        try:
            out = llm.complete_json("verifier", VERIFY_SYSTEM, user)
            votes.append(bool(out.get("supported", False)))
        except LLMError as e:
            log.warning("grounding: 証拠 %s の判定票が取れない: %s", ev.id, e)
            errors += 1
            votes.append(False)  # 検証できない票は不支持に倒す(捏造を通さない)
    if errors == 2:
        # 検証手段が一時的に無かっただけ: fail を恒久事実にせず none 温存 → 次ラウンド再試行
        return "none"
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
        # 成分ごとの数値レンジ(次元別 min/max)。併合の結果 tolerance 超の乖離を
        # 内包する成分を作らない — 丸め帯域の中間値が「橋」になって
        # 対立する数値(>tolerance)が推移閉包で同一クラスタ化するのを防ぐ(P20)
        ranges: list[dict[str, tuple[float, float]]] = []
        for e in evs:
            if e.value and e.value.num is not None and _dim(e.value.unit):
                ranges.append({_dim(e.value.unit): (e.value.num, e.value.num)})
            else:
                ranges.append({})

        def find(i: int) -> int:
            while parent[i] != i:
                parent[i] = parent[parent[i]]
                i = parent[i]
            return i

        def try_union(i: int, j: int) -> None:
            ra, rb = find(i), find(j)
            if ra == rb:
                return
            merged = dict(ranges[ra])
            for dim, (lo, hi) in ranges[rb].items():
                mlo, mhi = merged.get(dim, (lo, hi))
                merged[dim] = (min(mlo, lo), max(mhi, hi))
            for lo, hi in merged.values():
                if (hi - lo) / max(abs(hi), abs(lo), 1e-9) > CONTRA_TOLERANCE:
                    return  # 併合拒否: 矛盾候補を内包する成分を作らない
            parent[rb] = ra
            ranges[ra] = merged

        for i in range(len(evs)):
            for j in range(i + 1, len(evs)):
                if _same_cluster(evs[i], evs[j]):
                    try_union(i, j)
        # ラベルは「成分内の最小 evidence.id」— 入力順にもインデックスにも依存せず、
        # 新証拠の追加で既存成分のラベルが揺れない(無変更 re-put を誘発しない)
        comps: dict[int, list[Evidence]] = defaultdict(list)
        for i, e in enumerate(evs):
            comps[find(i)].append(e)
        for members in comps.values():
            label = min(m.id for m in members)
            for m in members:
                out.append(m.model_copy(update={"cluster_id": f"{key}-{label}"}))
    return out


CONTRA_TOLERANCE = 0.15  # contradictions() の既定 tolerance と同じ値を共有する


def _text_sim(a: Evidence, b: Evidence) -> bool:
    return difflib.SequenceMatcher(None, _norm(a.quote), _norm(b.quote)).ratio() > 0.85


def _same_cluster(a: Evidence, b: Evidence) -> bool:
    an = a.value.num if a.value else None
    bn = b.value.num if b.value else None
    if an is not None and bn is not None:
        if _dim(a.value.unit) != _dim(b.value.unit):
            return False  # 次元が違う数値(95% vs 95人)は別物
        base = max(abs(an), abs(bn), 1e-9)
        rel = abs(an - bn) / base
        if rel < 1e-3:
            return True
        if rel > CONTRA_TOLERANCE:
            return False  # 矛盾候補は必ず分離する(P20: 矛盾検出を殺さない)
        # 0.1%〜tolerance の帯域は丸め・概数の再掲でありうる。文面で判定し、
        # 同一上流の丸め違い(95% と 95.4%)を「独立2票」に数えない(P22)
        return _text_sim(a, b)
    if an is None and bn is None:
        return _text_sim(a, b)
    # num あり×なし は併合しない: 範囲表現「10〜12億円」等が対立する数値
    # 10億と12億の「橋」になり、推移閉包で矛盾検出を殺すのを防ぐ(P20)
    return False


def reevaluate_contradictions(existing: list[Contradiction],
                              evidences: list[Evidence],
                              tolerance: float = CONTRA_TOLERANCE,
                              ) -> list[Contradiction]:
    """open 矛盾を現在の証拠状態で再評価し、**もはや成立しない対**を resolved に
    した複製を返す(削除はしない — P20)。resolve が起きるのは新しい証拠の追加が
    クラスタ組替えや grounding の変化を起こした時だけであり、人間の黙認では起きない。"""
    ev = {e.id: e for e in evidences}
    changed: list[Contradiction] = []
    for c in existing:
        if c.status != "open":
            continue
        a, b = ev.get(c.evidence_a), ev.get(c.evidence_b)
        # 「まだ矛盾か」は数値の実乖離だけで判定する。クラスタの一致は理由にしない —
        # 併合バグや橋があっても、実乖離が残る限り open を維持する(防御の二重化)
        still = (
            a is not None and b is not None
            and a.grounded == "pass" and b.grounded == "pass"
            and a.value is not None and b.value is not None
            and a.value.num is not None and b.value.num is not None
            and _dim(a.value.unit) == _dim(b.value.unit)
            and abs(a.value.num - b.value.num)
            / max(abs(a.value.num), abs(b.value.num), 1e-9) > tolerance)
        if not still:
            log.info("矛盾 %s(%s)は証拠状態の変化により解消 → resolved",
                     c.id, c.item_key)
            changed.append(c.model_copy(update={"status": "resolved"}))
    return changed


def contradictions(case_id: str, evidences: list[Evidence],
                   existing: list[Contradiction],
                   tolerance: float = CONTRA_TOLERANCE,
                   ) -> list[Contradiction]:
    """同一項目で数値が tolerance 超乖離する別クラスタ対 → 矛盾(P20)。
    open の既存対は再登録しない。resolved の対が再び成立した場合は**新しい open として
    再検出される**(resolved 記録は履歴として残る — 復帰経路を殺さない)。"""
    seen = {frozenset((c.evidence_a, c.evidence_b))
            for c in existing if c.status == "open"}
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
