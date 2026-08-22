"""I6: イベントはハッシュ連鎖で追記され、改竄は検知される。"""
import sqlite3

from prism.events import EventLog


def _log():
    return EventLog(sqlite3.connect(":memory:"))


def test_chain_verifies():
    log = _log()
    for i in range(3):
        log.append("case1", "test", {"i": i})
    ok, n = log.verify_chain("case1")
    assert ok and n == 3


def test_chain_links_prev_hash():
    log = _log()
    e1 = log.append("case1", "a", {})
    e2 = log.append("case1", "b", {})
    assert e2.prev_hash == e1.this_hash
    assert e1.prev_hash == "genesis"


def test_tamper_detected():
    log = _log()
    log.append("case1", "a", {"v": 1})
    log.append("case1", "b", {"v": 2})
    log.conn.execute("UPDATE events SET payload='{\"v\": 999}' WHERE kind='a'")
    ok, n = log.verify_chain("case1")
    assert not ok and n == 0


def test_cases_have_independent_chains():
    log = _log()
    log.append("case1", "a", {})
    log.append("case2", "a", {})
    log.append("case1", "b", {})
    assert log.verify_chain("case1") == (True, 2)
    assert log.verify_chain("case2") == (True, 1)


def test_tail_truncation_detected():
    """末尾切り詰め(最新の不都合な事実の抹消)は chain_heads アンカーで検知(I6)。"""
    log = _log()
    for i in range(4):
        log.append("case1", "k", {"i": i})
    log.conn.execute(
        "DELETE FROM events WHERE seq=(SELECT MAX(seq) FROM events WHERE case_id='case1')")
    ok, n = log.verify_chain("case1")
    assert not ok and n == 3


def test_full_wipe_detected():
    log = _log()
    log.append("case1", "k", {})
    log.conn.execute("DELETE FROM events WHERE case_id='case1'")
    ok, n = log.verify_chain("case1")
    assert not ok and n == 0


def test_empty_case_verifies_as_zero():
    assert _log().verify_chain("never-existed") == (True, 0)


def test_legacy_db_without_anchor_is_not_false_positive():
    """旧版DB(chain_heads導入前)の健全な連鎖を「改竄」と誤告発しない。
    検証時にアンカーが初期化され、以降は末尾切り詰めも検知できる。"""
    log = _log()
    log.append("case1", "a", {})
    log.append("case1", "b", {})
    log.conn.execute("DELETE FROM chain_heads WHERE case_id='case1'")  # 旧版DBを再現
    assert log.verify_chain("case1") == (True, 2)   # 偽陽性を出さない(バックフィル)
    assert log.verify_chain("case1") == (True, 2)   # 以降も安定
    log.conn.execute(
        "DELETE FROM events WHERE seq=(SELECT MAX(seq) FROM events WHERE case_id='case1')")
    assert log.verify_chain("case1")[0] is False    # アンカー化後は切り詰めを検知


def test_append_to_legacy_db_initializes_anchor_with_true_count():
    log = _log()
    for i in range(3):
        log.append("case1", "k", {"i": i})
    log.conn.execute("DELETE FROM chain_heads WHERE case_id='case1'")
    log.append("case1", "k", {"i": 3})               # 旧版DBへ新コードで追記
    assert log.verify_chain("case1") == (True, 4)    # n=1 でなく実件数で初期化される
