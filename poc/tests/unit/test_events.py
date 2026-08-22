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
