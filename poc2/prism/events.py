"""追記専用イベントログ(SHA256ハッシュ連鎖)。全状態変更はここを通る(C-4, I6)。"""
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

GENESIS = "genesis"


def _digest(prev: str, case_id: str, kind: str, payload_json: str,
            actor: str, created_at: str) -> str:
    body = "|".join([prev, case_id, kind, payload_json, actor, created_at])
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


class EventLog:
    def __init__(self, conn: sqlite3.Connection):
        self.conn = conn
        conn.execute(_SCHEMA)
        conn.commit()

    def _last_hash(self, case_id: str) -> str:
        row = self.conn.execute(
            "SELECT this_hash FROM events WHERE case_id=? ORDER BY seq DESC LIMIT 1",
            (case_id,)).fetchone()
        return row[0] if row else GENESIS

    def append(self, case_id: str, kind: str, payload: dict,
               actor: str = "system") -> Event:
        prev = self._last_hash(case_id)
        created = datetime.now(timezone.utc).isoformat()
        pj = json.dumps(payload, ensure_ascii=False, sort_keys=True)
        this = _digest(prev, case_id, kind, pj, actor, created)
        cur = self.conn.execute(
            "INSERT INTO events(case_id,kind,payload,actor,prev_hash,this_hash,created_at)"
            " VALUES(?,?,?,?,?,?,?)",
            (case_id, kind, pj, actor, prev, this, created))
        self.conn.commit()
        return Event(seq=cur.lastrowid, case_id=case_id, kind=kind, payload=payload,
                     actor=actor, prev_hash=prev, this_hash=this, created_at=created)

    def verify_chain(self, case_id: str) -> tuple[bool, int]:
        """連鎖を再計算して検証。(ok, 検証したイベント数)。改竄があれば ok=False。"""
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
        return True, n

    def list(self, case_id: str) -> list[Event]:
        rows = self.conn.execute(
            "SELECT seq,kind,payload,actor,prev_hash,this_hash,created_at FROM events"
            " WHERE case_id=? ORDER BY seq", (case_id,)).fetchall()
        return [Event(seq=r[0], case_id=case_id, kind=r[1], payload=json.loads(r[2]),
                      actor=r[3], prev_hash=r[4], this_hash=r[5], created_at=r[6])
                for r in rows]
