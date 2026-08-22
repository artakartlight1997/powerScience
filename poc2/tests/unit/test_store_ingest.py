"""ストア(イベント併記)と取り込み(冪等・as_of 規約・C-7耐性・gate配線)。"""
from datetime import datetime, timezone

import pytest

from prism.contracts import Case
from prism.gate import Gate
from prism.ingest import scan
from prism.store import Store

TIERS = {"seller": 5, "consultant": 2, "web": 3}


def _case(store: Store) -> Case:
    case = Case(id="case1", name="サンプルテック", archetype="ses_jutaku",
                created_at=datetime.now(timezone.utc).isoformat())
    store.put("case", case)
    return case


def _env(tmp_path):
    store = Store(tmp_path / "db.sqlite")
    case = _case(store)
    inbox = tmp_path / "inbox"
    (inbox / "case1" / "seller").mkdir(parents=True)
    (inbox / "case1" / "general").mkdir(parents=True)
    gate = Gate([], tmp_path / "data")
    return store, case, inbox, tmp_path / "data", gate


def test_put_emits_event_and_roundtrips(tmp_path):
    store = Store(tmp_path / "db.sqlite")
    case = _case(store)
    got = store.get("case", "case1", "case1", Case)
    assert got == case
    events = store.events.list("case1")
    assert [e.kind for e in events] == ["case.put"]  # C-4: 書き込みはイベント併記
    assert store.events.verify_chain("case1")[0]


def test_put_rejects_empty_case_id(tmp_path):
    from prism.contracts import Source
    store = Store(tmp_path / "db.sqlite")
    src = Source(id="s1", case_id="", kind="web", trust_tier=3,
                 as_of="2026-01-01", content_hash="h")
    with pytest.raises(ValueError):
        store.put("source", src)  # 空 case_id を obj.id へ黙ってフォールバックしない


def test_scan_is_idempotent_and_sets_as_of(tmp_path):
    store, case, inbox, data, gate = _env(tmp_path)
    f = inbox / "case1" / "seller" / "2026-01-15_im.txt"
    f.write_text("稼働率は95%", encoding="utf-8")
    (inbox / "case1" / "general" / "note.txt").write_text("市場規模1兆円", encoding="utf-8")

    first = scan(store, case, inbox, data, TIERS, gate)
    assert len(first) == 2
    seller = next(s for s in first if s.kind == "seller")
    assert seller.as_of == "2026-01-15"          # ファイル名プレフィクスが as_of
    assert seller.seller_provided and seller.trust_tier == 5
    assert (data / "case1" / "snapshots").is_dir()

    assert scan(store, case, inbox, data, TIERS, gate) == []  # 冪等

    f2 = inbox / "case1" / "seller" / "2026-01-16_im_copy.txt"
    f2.write_text("稼働率は95%", encoding="utf-8")  # 同一内容(ハッシュ一致)
    assert scan(store, case, inbox, data, TIERS, gate) == []


def test_broken_pdf_does_not_kill_the_scan(tmp_path, caplog):
    """C-7: 壊れたPDF 1つでケース全体を落とさない。後続ファイルは取り込まれる。"""
    store, case, inbox, data, gate = _env(tmp_path)
    (inbox / "case1" / "seller" / "aaa_broken.pdf").write_bytes(b"not a pdf at all")
    (inbox / "case1" / "seller" / "zzz_good.txt").write_text("良品", encoding="utf-8")
    import logging
    with caplog.at_level(logging.WARNING, logger="prism.ingest"):
        created = scan(store, case, inbox, data, TIERS, gate)
    assert [s.path.endswith("zzz_good.txt") for s in created] == [True]
    assert any("取り込み失敗" in r.message for r in caplog.records)  # C-8: 黙らない


def test_invalid_date_prefix_falls_back_with_warning(tmp_path, caplog):
    store, case, inbox, data, gate = _env(tmp_path)
    (inbox / "case1" / "general" / "2026-13-99_x.txt").write_text("本文", encoding="utf-8")
    import logging
    with caplog.at_level(logging.WARNING, logger="prism.ingest"):
        created = scan(store, case, inbox, data, TIERS, gate)
    assert len(created) == 1
    from datetime import date
    date.fromisoformat(created[0].as_of)  # 正当な日付(mtime由来)に落ちている
    assert any("不正" in r.message for r in caplog.records)


def test_same_content_different_kind_is_registered(tmp_path):
    """売り手資料と同一文面の公開ページは別出所として登録する(I3 との整合)。"""
    store, case, inbox, data, gate = _env(tmp_path)
    (inbox / "case1" / "seller" / "2026-01-15_a.txt").write_text("同一文面", encoding="utf-8")
    (inbox / "case1" / "general" / "2026-02-01_b.txt").write_text("同一文面", encoding="utf-8")
    created = scan(store, case, inbox, data, TIERS, gate)
    assert sorted(s.kind for s in created) == ["general", "seller"]


def test_latest_judgments_picks_max_round(tmp_path):
    from prism.contracts import Judgment
    store = Store(tmp_path / "db.sqlite")
    _case(store)
    for rnd, status in [(1, "missing"), (2, "thin")]:
        store.put("judgment", Judgment(id=f"c:i:r{rnd}", case_id="case1",
                                       item_id="c:i", status=status, round=rnd))
    latest = store.latest_judgments("case1")
    assert latest["c:i"].status == "thin"
    from prism.contracts import Judgment as J
    assert len(store.all("judgment", "case1", J)) == 2  # 履歴は残る
