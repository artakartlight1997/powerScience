"""検証層: grounding の決定性・クラスタの独立性正規化(P22)・矛盾の保存(P20)。"""
import pytest

from prism.contracts import LLMError
from prism.verify import cluster, contradictions, ground

from ..conftest import FakeLLM, make_ev


class ExplodingLLM(FakeLLM):
    def complete_json(self, role, system, user):
        raise AssertionError("決定的照合で済むケースで LLM を呼んではならない")


def test_ground_exact_substring_passes_without_llm():
    ev = make_ev(quote="稼働率は95%で推移", grounded="none")
    assert ground(ev, "当社の 稼働率は 95%で推移 している。", ExplodingLLM()) == "pass"


def test_ground_no_snapshot_never_passes():
    ev = make_ev(quote="何か", grounded="none")
    assert ground(ev, None, ExplodingLLM()) == "fail"


def test_ground_order_swapped_votes():
    ev = make_ev(quote="売上高は増加傾向にある", grounded="none")
    both_yes = FakeLLM(lambda r, s, u: {"supported": True})
    assert ground(ev, "本文にはない表現", both_yes) == "pass"
    assert both_yes.calls == 2  # P10: 提示順を替えて2回聞く
    votes = FakeLLM(lambda r, s, u: {"supported": u.startswith("## 引用文")})
    assert ground(ev, "本文にはない表現", votes) == "partial"
    both_no = FakeLLM(lambda r, s, u: {"supported": False})
    assert ground(ev, "本文にはない表現", both_no) == "fail"


def test_ground_llm_error_degrades_to_not_pass():
    def boom(r, s, u):
        raise LLMError("down")
    ev = make_ev(quote="本文にない引用", grounded="none")
    assert ground(ev, "別の本文", FakeLLM(boom)) != "pass"


def test_cluster_same_value_same_cluster():
    evs = [make_ev(id="e1", quote="市場規模は約1兆円である", num=1e12),
           make_ev(id="e2", quote="市場は1兆円規模と推計される", num=1e12),
           make_ev(id="e3", quote="市場規模は5000億円", num=5e11)]
    out = {e.id: e.cluster_id for e in cluster(evs)}
    assert out["e1"] == out["e2"]  # 同一値=同一上流とみなす(独立と数えない)
    assert out["e1"] != out["e3"]


def test_cluster_is_per_item():
    evs = [make_ev(id="e1", item_key="a", num=100.0),
           make_ev(id="e2", item_key="b", num=100.0)]
    out = {e.id: e.cluster_id for e in cluster(evs)}
    assert out["e1"] != out["e2"]


def test_contradiction_detected_and_preserved():
    evs = cluster([make_ev(id="e1", quote="稼働率は95%", num=95.0, unit="%"),
                   make_ev(id="e2", quote="稼働率は80%程度", num=80.0, unit="%")])
    found = contradictions("case1", evs, existing=[])
    assert len(found) == 1
    assert found[0].status == "open"
    assert found[0].delta == pytest.approx(15 / 95, abs=1e-3)
    # 既知の対は再登録しない
    assert contradictions("case1", evs, existing=found) == []


def test_no_contradiction_across_units_or_within_tolerance():
    evs = cluster([make_ev(id="e1", num=100.0, unit="%"),
                   make_ev(id="e2", num=95.0, unit="%"),   # 5% 乖離 < 15%
                   make_ev(id="e3", num=200.0, unit="円")])  # 単位が違う
    assert contradictions("case1", evs, existing=[]) == []
