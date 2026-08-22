"""ストア(イベント併記)と取り込み(冪等・as_of 規約)。"""
from datetime import datetime, timezone

from prism.contracts import Case
from prism.ingest import scan
from prism.store import Store

TIERS = {"seller": 5, "consultant": 2, "web": 3}


def _case(store: Store) -> Case:
    case = Case(id="case1", name="サンプルテック", archetype="ses_jutaku",
                created_at=datetime.now(timezone.utc).isoformat())
    store.put("case", case)
    return case


def test_put_emits_event_and_roundtrips(tmp_path):
    store = Store(tmp_path / "db.sqlite")
    case = _case(store)
    got = store.get("case", "case1", "case1", Case)
    assert got == case
    events = store.events.list("case1")
    assert [e.kind for e in events] == ["case.put"]  # C-4: 書き込みはイベント併記
    assert store.events.verify_chain("case1")[0]


def test_scan_is_idempotent_and_sets_as_of(tmp_path):
    store = Store(tmp_path / "db.sqlite")
    case = _case(store)
    inbox = tmp_path / "inbox"
    (inbox / "case1" / "seller").mkdir(parents=True)
    (inbox / "case1" / "general").mkdir(parents=True)
    f = inbox / "case1" / "seller" / "2026-01-15_im.txt"
    f.write_text("稼働率は95%", encoding="utf-8")
    (inbox / "case1" / "general" / "note.txt").write_text("市場規模1兆円", encoding="utf-8")

    first = scan(store, case, inbox, tmp_path / "data", TIERS)
    assert len(first) == 2
    seller = next(s for s in first if s.kind == "seller")
    assert seller.as_of == "2026-01-15"          # ファイル名プレフィクスが as_of
    assert seller.seller_provided and seller.trust_tier == 5
    assert (tmp_path / "data" / "case1" / "snapshots").is_dir()

    assert scan(store, case, inbox, tmp_path / "data", TIERS) == []  # 冪等

    f2 = inbox / "case1" / "seller" / "2026-01-16_im_copy.txt"
    f2.write_text("稼働率は95%", encoding="utf-8")  # 同一内容(ハッシュ一致)
    assert scan(store, case, inbox, tmp_path / "data", TIERS) == []


def test_latest_judgments_picks_max_round(tmp_path):
    from prism.contracts import Judgment
    store = Store(tmp_path / "db.sqlite")
    _case(store)
    for rnd, status in [(1, "missing"), (2, "thin")]:
        store.put("judgment", Judgment(id=f"c:i:r{rnd}", case_id="case1",
                                       item_id="c:i", status=status, round=rnd))
    latest = store.latest_judgments("case1")
    assert latest["c:i"].status == "thin"
    assert len(store.all("judgment", "case1", Judgment)) == 2  # 履歴は残る
