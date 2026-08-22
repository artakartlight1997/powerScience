"""追記専用イベントログ(SHA256ハッシュ連鎖)。全状態変更はここを通る(C-4, I6)。

改竄検知は2段: ①連鎖の再計算(中間削除・並べ替え・payload改竄を検知)
②chain_heads アンカー(件数+末尾ハッシュ)との照合(末尾切り詰め・全消去を検知)。
アンカーが同一DB内にある限り「両方を整合させて改竄する」攻撃は残る —
本番では外部ストレージ/署名へのアンカー退避が必要(PoC の既知の限界。CONTRACTS §4 注記)。
"""
from __future__ import annotations

import hashlib
import json
import sqlite3
from datetime import datetime, timezone

from .contracts import Event

_SCHEMA = """CREATE TABLE IF NOT EXISTS events(
  seq INTEGER PRIMARY KEY AUTOINCREMENT,
  case_id TEXT NOT NULL, kind TEXT NOT NULL, payload TEXT NOT NULL,
  actor TEXT NOT NULL, prev_hash TEXT NOT NULL, this_hash TEXT NOT NULL,
  created_at TEXT NOT NULL)"""
_SCHEMA_HEADS = """CREATE TABLE IF NOT EXISTS chain_heads(
  case_id TEXT PRIMARY KEY, n INTEGER NOT NULL, head_hash TEXT NOT NULL)"""

GENESIS = "genesis"


def _digest(prev: str, case_id: str, kind: str, payload_json: str,
            actor: str, created_at: str) -> str:
    body = "|".join([prev, case_id, kind, payload_json, actor, created_at])
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


class EventLog:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        conn.execute(_SCHEMA)
        conn.execute(_SCHEMA_HEADS)
        conn.commit()

    def _last_hash(self, case_id: str) -> str:
        row = self.conn.execute(
            "SELECT this_hash FROM events WHERE case_id=? ORDER BY seq DESC LIMIT 1",
            (case_id,)).fetchone()
        return row[0] if row else GENESIS

    def append(self, case_id: str, kind: str, payload: dict,
               actor: str = "system") -> Event:
        conn = self.conn
        # read-modify-write を1トランザクションに(並行 append での連鎖破損防止)
        if not conn.in_transaction:
            conn.execute("BEGIN IMMEDIATE")
        try:
            prev = self._last_hash(case_id)
            created = datetime.now(timezone.utc).isoformat()
            pj = json.dumps(payload, ensure_ascii=False, sort_keys=True)
            this = _digest(prev, case_id, kind, pj, actor, created)
            cur = conn.execute(
                "INSERT INTO events(case_id,kind,payload,actor,prev_hash,this_hash,created_at)"
                " VALUES(?,?,?,?,?,?,?)",
                (case_id, kind, pj, actor, prev, this, created))
            conn.execute(
                "INSERT INTO chain_heads(case_id,n,head_hash) VALUES(?,1,?)"
                " ON CONFLICT(case_id) DO UPDATE SET n=n+1, head_hash=excluded.head_hash",
                (case_id, this))
            conn.commit()
        except BaseException:
            conn.rollback()
            raise
        return Event(seq=cur.lastrowid, case_id=case_id, kind=kind, payload=payload,
                     actor=actor, prev_hash=prev, this_hash=this, created_at=created)

    def verify_chain(self, case_id: str) -> tuple[bool, int]:
        """連鎖を再計算し、chain_heads アンカーと照合。(ok, 検証したイベント数)。"""
        prev = GENESIS
        n = 0
        for row in self.conn.execute(
                "SELECT kind,payload,actor,prev_hash,this_hash,created_at FROM events"
                " WHERE case_id=? ORDER BY seq", (case_id,)):
            kind, pj, actor, prev_hash, this_hash, created = row
            if prev_hash != prev:
                return False, n
            if _digest(prev, case_id, kind, pj, actor, created) != this_hash:
                return False, n
            prev = this_hash
            n += 1
        head = self.conn.execute(
            "SELECT n, head_hash FROM chain_heads WHERE case_id=?",
            (case_id,)).fetchone()
        expected_n, expected_head = head if head else (0, GENESIS)
        if n != expected_n or prev != expected_head:
            return False, n  # 末尾切り詰め・全消去・アンカー不整合
        return True, n

    def list(self, case_id: str) -> list[Event]:
        rows = self.conn.execute(
            "SELECT seq,kind,payload,actor,prev_hash,this_hash,created_at FROM events"
            " WHERE case_id=? ORDER BY seq", (case_id,)).fetchall()
        return [Event(seq=r[0], case_id=case_id, kind=r[1], payload=json.loads(r[2]),
                      actor=r[3], prev_hash=r[4], this_hash=r[5], created_at=r[6])
                for r in rows]
