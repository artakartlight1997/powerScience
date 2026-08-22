"""カバレッジ監査。純関数のみ(C-2): I/O も LLM も呼ばない。

filled / thin / missing / unknown は文字数でなく「検証済み(grounded=pass)×
独立(クラスタ)×新鮮」な証拠の密度で決める。
I1: filled/thin は evidence_ids を持つ。I3: seller 単独では filled 不可。
I8: unknown は acquisition_path を持つ。I9: 同一クラスタは1回だけ数える。
"""
from __future__ import annotations

from datetime import date, timedelta

from .contracts import Evidence, Judgment, SpecItem
from .fill import is_public_reachable  # 「公開経路」の定義は fill と共有(判定のズレ防止)


def _fresh(ev: Evidence, today: date, freshness_days: int) -> bool:
    try:
        return date.fromisoformat(ev.as_of) >= today - timedelta(days=freshness_days)
    except ValueError:
        return False  # as_of が読めない証拠は新鮮と数えない


def judge(item: SpecItem, evidences: list[Evidence], open_contradiction: bool,
          round_no: int, today: date) -> Judgment:
    """1項目の判定。evidences は item_key 一致のもののみ渡すこと(事前条件)。"""
    usable = [e for e in evidences
              if e.grounded == "pass" and e.status in ("value", "NOT_FOUND")
              and _fresh(e, today, item.freshness_days)]
    # expect_absent 項目は「無い」ことの明示的確認(NOT_FOUND)が支持証拠になる。
    # 通常項目では NOT_FOUND は支持でなく「探して無かった」記録なので除外する。
    if not item.expect_absent:
        usable = [e for e in usable if e.status == "value"]

    clusters: dict[str, list[Evidence]] = {}
    for e in usable:
        # I9。cluster_id 未付与は「独立」でなく単一の擬似クラスタに畳む(保守方向)。
        # 未クラスタ証拠2件を独立2票と数えて filled にする事故を防ぐ
        clusters.setdefault(e.cluster_id or "unclustered", []).append(e)
    non_seller = [cid for cid, evs in clusters.items()
                  if any(not e.seller_provided for e in evs)]
    # expect_absent 項目で「存在の主張(value)」と「不在の確認(NOT_FOUND)」が併存
    # したら、それは数値では捕まらない意味的矛盾 — filled にせず人間判断へ(P20)
    absent_conflict = (item.expect_absent
                       and any(e.status == "value" for e in usable)
                       and any(e.status == "NOT_FOUND" for e in usable))

    jid = f"{item.id}:r{round_no}"
    base = dict(id=jid, case_id=item.case_id, item_id=item.id, round=round_no,
                verified_clusters=len(clusters),
                evidence_ids=[e.id for e in usable],
                contradiction_open=open_contradiction)

    if usable:
        if (len(clusters) >= item.required_clusters and non_seller
                and not open_contradiction and not absent_conflict):
            return Judgment(**base, status="filled",
                            rationale=f"独立{len(clusters)}クラスタが原文支持で確認")
        reasons = []
        if len(clusters) < item.required_clusters:
            reasons.append(f"独立クラスタ{len(clusters)}/{item.required_clusters}")
        if not non_seller:
            reasons.append("売り手の主張のみ(I3: 外部突合が必要)")
        if open_contradiction:
            reasons.append("未解消の矛盾あり(P20)")
        if absent_conflict:
            reasons.append("存在の主張と不在の確認が併存(要人間判断)")
        return Judgment(**base, status="thin", rationale="、".join(reasons),
                        acquisition_path=_path(item))
    # 証拠ゼロ: 公開経路で取れるはずなら missing、そうでなければ unknown
    if is_public_reachable(item):
        return Judgment(**base, status="missing",
                        rationale="公開経路で未取得(探索を継続)",
                        acquisition_path=_path(item))
    return Judgment(**base, status="unknown",
                    rationale="公開経路では到達不能(P21: 不在を真に変換しない)",
                    acquisition_path=_path(item))  # I8: 必ず取得手段を付す


def _path(item: SpecItem) -> str:
    return "/".join(item.retrievability) if item.retrievability else "expert"
