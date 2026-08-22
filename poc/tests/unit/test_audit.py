"""監査の不変条件: I1(根拠参照)・I3(売り手単独不可)・I8(unknownは取得手段)・I9(クラスタ重複排除)。"""
from datetime import date

from prism.audit import judge

from ..conftest import make_ev, make_item

TODAY = date(2026, 8, 22)


def test_filled_requires_independent_clusters_and_has_evidence_ids():
    item = make_item(required_clusters=2)
    evs = [make_ev(id="e1", cluster_id="c1"), make_ev(id="e2", cluster_id="c2")]
    j = judge(item, evs, False, 1, TODAY)
    assert j.status == "filled"
    assert set(j.evidence_ids) == {"e1", "e2"}  # I1


def test_seller_only_cannot_be_filled():  # I3
    item = make_item(required_clusters=2)
    evs = [make_ev(id="e1", cluster_id="c1", seller=True),
           make_ev(id="e2", cluster_id="c2", seller=True)]
    j = judge(item, evs, False, 1, TODAY)
    assert j.status == "thin"
    assert "売り手" in j.rationale


def test_same_cluster_counted_once():  # I9
    item = make_item(required_clusters=2)
    evs = [make_ev(id=f"e{i}", cluster_id="c1") for i in range(3)]
    j = judge(item, evs, False, 1, TODAY)
    assert j.status == "thin"
    assert j.verified_clusters == 1


def test_unknown_has_acquisition_path():  # I8
    item = make_item(retrievability=["vdr", "expert"])
    j = judge(item, [], False, 1, TODAY)
    assert j.status == "unknown"
    assert j.acquisition_path == "vdr/expert"


def test_public_reachable_empty_is_missing_not_unknown():
    item = make_item(retrievability=["public"])
    j = judge(item, [], False, 1, TODAY)
    assert j.status == "missing"


def test_open_contradiction_blocks_filled():  # P20
    item = make_item(required_clusters=2)
    evs = [make_ev(id="e1", cluster_id="c1"), make_ev(id="e2", cluster_id="c2")]
    j = judge(item, evs, True, 1, TODAY)
    assert j.status == "thin"
    assert j.contradiction_open


def test_ungrounded_evidence_does_not_count():
    item = make_item(required_clusters=1)
    evs = [make_ev(id="e1", grounded="partial"), make_ev(id="e2", grounded="fail")]
    j = judge(item, evs, False, 1, TODAY)
    assert j.status == "missing"


def test_stale_evidence_does_not_count():
    item = make_item(required_clusters=1, freshness_days=365)
    j = judge(item, [make_ev(as_of="2020-01-01")], False, 1, TODAY)
    assert j.status == "missing"


def test_expect_absent_accepts_confirmed_not_found():
    """「該当なし」の明示的確認は確認済みfilledに数える(仕様v0.3 ④)。"""
    item = make_item(required_clusters=1, expect_absent=True)
    j = judge(item, [make_ev(status="NOT_FOUND", quote="設備投資はほぼ不要")],
              False, 1, TODAY)
    assert j.status == "filled"


def test_not_found_is_not_support_for_normal_items():
    item = make_item(required_clusters=1)
    j = judge(item, [make_ev(status="NOT_FOUND")], False, 1, TODAY)
    assert j.status == "missing"
