"""充填計画: 順位のみを返すこと・停止には必ず理由があること(P15)。"""
from prism.contracts import Judgment
from prism.fill import make_questions, plan, should_stop

from ..conftest import make_item

RULES = {"max_iterations": 5, "max_llm_calls": 200, "min_new_filled_per_iter": 1}


def _j(item_id, status, rationale=""):
    return Judgment(id=f"{item_id}:r1", case_id="case1", item_id=item_id,
                    status=status, rationale=rationale, round=1,
                    acquisition_path="vdr" if status == "unknown" else None)


def test_plan_returns_ranked_ids_only_for_gaps():
    items = [
        make_item(id="c:a", key="a", must=True, dependence="high"),
        make_item(id="c:b", key="b", must=True, dependence="low"),
        make_item(id="c:c", key="c", must=False, dependence="high"),
        make_item(id="c:d", key="d", must=True, dependence="high"),
    ]
    judgments = {"c:a": _j("c:a", "missing"), "c:b": _j("c:b", "missing"),
                 "c:c": _j("c:c", "thin"), "c:d": _j("c:d", "filled")}
    order = plan(items, judgments)
    assert "c:d" not in order            # filled は gap でない
    assert order[0] == "c:a"             # must + high が先頭
    assert order.index("c:a") < order.index("c:b")   # dependence 順
    assert order.index("c:b") < order.index("c:c")   # must が should に先行


def test_make_questions_maps_channel_and_caps():
    items = [make_item(id=f"c:i{n}", key=f"i{n}", retrievability=["vdr"])
             for n in range(5)]
    judgments = {it.id: _j(it.id, "unknown") for it in items}
    qs = make_questions("case1", items, judgments, max_open=3)
    assert len(qs) == 3
    assert all(q.channel == "vdr" for q in qs)
    assert [q.rank for q in qs] == [1, 2, 3]


def test_stop_always_has_reason():
    stop, reason = should_stop(1, 0, 0, open_public_gaps=5, stop_rules=RULES)
    assert not stop and reason is None
    for kwargs, prefix in [
        (dict(round_no=5, llm_calls=0, new_progress=9, open_public_gaps=5), "R1"),
        (dict(round_no=2, llm_calls=200, new_progress=9, open_public_gaps=5), "R2"),
        (dict(round_no=2, llm_calls=0, new_progress=0, open_public_gaps=5), "R3"),
        (dict(round_no=1, llm_calls=0, new_progress=0, open_public_gaps=0), "R4"),
    ]:
        stop, reason = should_stop(stop_rules=RULES, **kwargs)
        assert stop and reason.startswith(prefix)


def test_first_round_not_stopped_by_diminishing_returns():
    stop, _ = should_stop(1, 0, 0, open_public_gaps=5, stop_rules=RULES)
    assert not stop  # R3 は round>1 のみ


def test_channel_prefers_public_when_mixed():
    """[vdr, public] は web チャネル — audit/research の「含む」判定と揃える。
    先頭要素だけ見ると R4(公開経路の完了)が偽発火する。"""
    items = [make_item(id="c:m", key="m", retrievability=["vdr", "public"])]
    judgments = {"c:m": _j("c:m", "missing")}
    qs = make_questions("case1", items, judgments, max_open=5)
    assert qs[0].channel == "web"


def test_open_public_gaps_counts_items_not_questions():
    from prism.fill import open_public_gaps
    items = [make_item(id="c:a", key="a", retrievability=["vdr", "public"]),
             make_item(id="c:b", key="b", retrievability=["vdr"]),
             make_item(id="c:c", key="c", retrievability=["public"])]
    judgments = {"c:a": _j("c:a", "missing"), "c:b": _j("c:b", "unknown"),
                 "c:c": _j("c:c", "filled")}
    assert open_public_gaps(items, judgments) == 1  # a のみ(c は filled、b は非公開)


def test_box10_ranks_after_box2_numerically():
    items = [make_item(id="c:x10", key="x10", box="box10"),
             make_item(id="c:x2", key="x2", box="box2")]
    order = plan(items, {})
    assert order == ["c:x2", "c:x10"]  # 辞書順の罠("box10" < "box2")を踏まない
