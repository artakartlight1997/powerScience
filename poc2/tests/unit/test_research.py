"""収集ループ: クエリ計画(純関数)と「取得できないURLからは何も生まれない」(R-1)。"""
from datetime import date, datetime, timezone

from prism.contracts import Case, Judgment, SearchHit
from prism.gate import Gate
from prism.research import build_queries, collect
from prism.store import Store

from ..conftest import FakeFetcher, FakeSearch, make_item


def _case():
    return Case(id="case1", name="サンプルテック", archetype="ses_jutaku",
                created_at=datetime.now(timezone.utc).isoformat())


def _j(item_id, status):
    return Judgment(id=f"{item_id}:r1", case_id="case1", item_id=item_id,
                    status=status, round=1,
                    acquisition_path="vdr" if status == "unknown" else None)


def test_build_queries_skips_vdr_expert_only_items():  # P21
    items = [make_item(id="c:a", key="a", retrievability=["public"]),
             make_item(id="c:b", key="b", retrievability=["vdr", "expert"]),
             make_item(id="c:c", key="c", retrievability=["premium"])]
    qs = build_queries(_case(), items, {}, max_queries=10)
    assert {q.item_key for q in qs} == {"a", "c"}
    assert all("サンプルテック" in q.text for q in qs)


def test_build_queries_respects_priority_and_cap():
    items = [make_item(id="c:lo", key="lo", must=False, dependence="low",
                       retrievability=["public"]),
             make_item(id="c:hi", key="hi", must=True, dependence="high",
                       retrievability=["public"])]
    qs = build_queries(_case(), items, {}, max_queries=1)
    assert len(qs) == 1 and qs[0].item_key == "hi"


def test_build_queries_excludes_filled():
    items = [make_item(id="c:a", key="a", retrievability=["public"])]
    qs = build_queries(_case(), items, {"c:a": _j("c:a", "filled")}, 10)
    assert qs == []


def test_collect_dead_url_produces_nothing(tmp_path):
    """捏造URL(取得失敗)からは Source も生まれない(R-1)。"""
    store = Store(tmp_path / "db.sqlite")
    search = FakeSearch(lambda q, k: [SearchHit(url="https://fake.example/no"),
                                      SearchHit(url="https://real.example/yes")])
    fetcher = FakeFetcher({"https://real.example/yes": "稼働率は80%程度とみられる。"})
    qs = build_queries(_case(), [make_item(key="a", retrievability=["public"])], {}, 5)
    created = collect(store, _case(), Gate([], tmp_path), search, fetcher, qs,
                      tmp_path, results_per_query=3, max_fetch=10,
                      trust_tier_web=3, today=date(2026, 8, 22))
    assert len(created) == 1
    src = created[0]
    assert src.kind == "web" and src.url == "https://real.example/yes"
    assert src.snapshot_path and src.publisher == "real.example"
    # 同一内容の再収集は冪等
    again = collect(store, _case(), Gate([], tmp_path), search, fetcher, qs,
                    tmp_path, 3, 10, 3, today=date(2026, 8, 22))
    assert again == []


def test_collect_respects_gate_allowlist(tmp_path):
    store = Store(tmp_path / "db.sqlite")
    search = FakeSearch(lambda q, k: [SearchHit(url="https://evil.example/x")])
    fetcher = FakeFetcher({"https://evil.example/x": "本文"})
    qs = [q for q in build_queries(_case(),
                                   [make_item(key="a", retrievability=["public"])],
                                   {}, 5)]
    created = collect(store, _case(), Gate(["allowed.example"], tmp_path), search,
                      fetcher, qs, tmp_path, 3, 10, 3, today=date(2026, 8, 22))
    assert created == [] and fetcher.fetched == []  # 取得すら行われない(C-5)
