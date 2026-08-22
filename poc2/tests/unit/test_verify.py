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


def test_no_contradiction_across_dimensions_or_within_tolerance():
    evs = cluster([make_ev(id="e1", num=100.0, unit="%"),
                   make_ev(id="e2", num=95.0, unit="%"),   # 5% 乖離 < 15%
                   make_ev(id="e3", num=200.0, unit="円")])  # 次元が違う(% vs 円)
    assert contradictions("case1", evs, existing=[]) == []


def test_boundary_delta_equal_to_tolerance_is_not_contradiction():
    evs = cluster([make_ev(id="e1", num=100.0, unit="%"),
                   make_ev(id="e2", num=85.0, unit="%")])  # delta = 0.15 ちょうど
    assert contradictions("case1", evs, existing=[], tolerance=0.15) == []


def test_contradiction_across_unit_notations_same_dimension():
    """「10億円」vs「1,500百万円」— 表記は違うが次元は同じ円。矛盾を見逃さない(P20)。"""
    evs = cluster([make_ev(id="e1", quote="売上高10億円", num=1e9, unit="億円"),
                   make_ev(id="e2", quote="売上高1,500百万円", num=1.5e9, unit="百万円")])
    found = contradictions("case1", evs, existing=[])
    assert len(found) == 1


def test_same_number_different_dimension_not_same_cluster():
    """「95%」と「95人」を同一上流と誤認しない(P22)。"""
    out = cluster([make_ev(id="e1", quote="稼働率は95%", num=95.0, unit="%"),
                   make_ev(id="e2", quote="エンジニア95人体制", num=95.0, unit="人")])
    ids = {e.id: e.cluster_id for e in out}
    assert ids["e1"] != ids["e2"]


def test_similar_text_different_numbers_stay_separate_and_contradict():
    """定型文で数値だけ違う引用を文面類似で併合しない — 矛盾検出を殺さない(P20)。"""
    a = make_ev(id="e1", quote="2023年度の国内SES市場規模は約1兆2000億円と推計される",
                num=1.2e12, unit="億円")
    b = make_ev(id="e2", quote="2023年度の国内SES市場規模は約8000億円と推計される",
                num=8e11, unit="億円")
    out = cluster([a, b])
    ids = {e.id: e.cluster_id for e in out}
    assert ids["e1"] != ids["e2"]
    assert len(contradictions("case1", out, existing=[])) == 1


def test_no_num_bridge_cannot_merge_conflicting_numbers():
    """数値なし証拠(範囲表現等)が対立する数値の「橋」になって矛盾検出を殺さない(P20)。"""
    a = make_ev(id="ev-a", quote="当社の売上高は10億円である", num=1e9, unit="億円")
    b = make_ev(id="ev-b", quote="当社の売上高は12億円である", num=1.2e9, unit="億円")
    d = make_ev(id="ev-d", quote="当社の売上高は10〜12億円である")  # num なし
    out = cluster([a, d, b])
    ids = {e.id: e.cluster_id for e in out}
    assert ids["ev-a"] != ids["ev-b"]           # 橋を渡らない
    assert len(contradictions("case1", out, existing=[])) == 1  # 矛盾は生きている


def test_rounding_variants_do_not_become_two_votes():
    """同一上流の丸め違い(95% と 95.4%)を独立2票=filled に化けさせない(P22)。"""
    a = make_ev(id="e1", quote="エンジニアの稼働率は約95%で推移している",
                num=95.0, unit="%")
    b = make_ev(id="e2", quote="エンジニアの稼働率は95.4%で推移している",
                num=95.4, unit="%")
    out = cluster([a, b])
    ids = {e.id: e.cluster_id for e in out}
    assert ids["e1"] == ids["e2"]


def test_cluster_labels_stable_when_new_evidence_added():
    """既存成分のラベルは新証拠の追加で揺れない(無変更 re-put を誘発しない)。"""
    a = make_ev(id="ev-bbb", quote="市場規模は約1兆円である", num=1e12, unit="兆円")
    b = make_ev(id="ev-ccc", quote="市場は1兆円規模と推計される", num=1e12, unit="兆円")
    before = {e.id: e.cluster_id for e in cluster([a, b])}
    c = make_ev(id="ev-aaa", quote="全く別の話題の証拠")  # 辞書順で先頭に来る新証拠
    after = {e.id: e.cluster_id for e in cluster([c, a, b])}
    assert before["ev-bbb"] == after["ev-bbb"]
    assert before["ev-ccc"] == after["ev-ccc"]


def test_reevaluate_resolves_only_dead_contradictions():
    """resolve は証拠状態の変化によってのみ起きる。生きている矛盾は触らない(P20)。"""
    from prism.verify import reevaluate_contradictions
    a = make_ev(id="e1", quote="稼働率95%", num=95.0, unit="%", cluster_id="k-x")
    b = make_ev(id="e2", quote="稼働率80%", num=80.0, unit="%", cluster_id="k-y")
    cx = contradictions("case1", [a, b], existing=[])
    assert len(cx) == 1
    # まだ成立 → 触らない
    assert reevaluate_contradictions(cx, [a, b]) == []
    # 片側の grounding が失われた → resolved
    b_fail = b.model_copy(update={"grounded": "fail"})
    resolved = reevaluate_contradictions(cx, [a, b_fail])
    assert len(resolved) == 1 and resolved[0].status == "resolved"
    # 同一クラスタに組み替わった → resolved
    b_same = b.model_copy(update={"cluster_id": "k-x"})
    assert reevaluate_contradictions(cx, [a, b_same])[0].status == "resolved"


def test_ground_double_llm_error_returns_none_not_fail():
    """検証手段の一時喪失を恒久 fail にしない(次ラウンド再試行)。"""
    from prism.verify import ground

    def boom(r, s, u):
        raise LLMError("down")
    ev = make_ev(quote="本文にない引用", grounded="none")
    assert ground(ev, "別の本文", FakeLLM(boom)) == "none"


def test_cluster_assignment_is_order_invariant():
    """A~B, B~C, A≁C でも union-find で入力順によらず同一の分割になる。"""
    base = "同社の主力事業はITサービスの提供であり顧客基盤は安定している"
    a = make_ev(id="a", quote=base + "とされる")
    b = make_ev(id="b", quote=base + "との評価が多い")
    c = make_ev(id="c", quote=base + "との評価が多いようだが一部に異論もある")

    def partition(evs):
        out = cluster(evs)
        groups = {}
        for e in out:
            groups.setdefault(e.cluster_id, set()).add(e.id)
        return sorted(frozenset(g) for g in groups.values())

    assert partition([a, b, c]) == partition([c, a, b]) == partition([b, c, a])
