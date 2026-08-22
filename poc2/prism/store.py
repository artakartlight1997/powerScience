"""状態ストア。書き込みは必ずイベントを併記する(C-4)。読み出しはビュー。

レコードは (case_id, kind, id) をキーに JSON で持つ。kind ごとの専用テーブルは
PoC では作らない(スキーマ変更を安くするため)。
"""
from __future__ import annotations

import sqlite3
from pathlib import Path
from typing import Iterable, Optional, Type, TypeVar

from pydantic import BaseModel

from .contracts import Judgment, Source
from .events import EventLog

T = TypeVar("T", bound=BaseModel)

_SCHEMA = """CREATE TABLE IF NOT EXISTS records(
  case_id TEXT NOT NULL, kind TEXT NOT NULL, id TEXT NOT NULL,
  json TEXT NOT NULL, PRIMARY KEY(case_id, kind, id))"""


class Store:
    def __init__(self, db_path: str | Path):
        Path(db_path).parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(db_path))
        self.conn.execute(_SCHEMA)
        self.conn.commit()
        self.events = EventLog(self.conn)

    def close(self) -> None:
        self.conn.close()

    # --- 書き込み(イベント経由のみ) ---
    @staticmethod
    def _case_id_of(obj: BaseModel) -> str:
        from .contracts import Case
        if isinstance(obj, Case):
            return obj.id
        case_id = getattr(obj, "case_id", None)
        if not case_id:
            raise ValueError(f"case_id が空のオブジェクトは保存できない: {obj!r}")
        return case_id

    def put(self, kind: str, obj: BaseModel, actor: str = "system") -> None:
        case_id = self._case_id_of(obj)
        payload = obj.model_dump()
        self.events.append(case_id, f"{kind}.put", payload, actor)
        self.conn.execute(
            "INSERT OR REPLACE INTO records(case_id,kind,id,json) VALUES(?,?,?,?)",
            (case_id, kind, obj.id, obj.model_dump_json()))
        self.conn.commit()

    def put_many(self, kind: str, objs: Iterable[BaseModel], actor: str = "system") -> None:
        for o in objs:
            self.put(kind, o, actor)

    def delete(self, kind: str, case_id: str, id: str, actor: str = "system") -> None:
        """レコードの削除(イベントに記録した上で、マテリアライズドビューから除く)。"""
        self.events.append(case_id, f"{kind}.delete", {"id": id}, actor)
        self.conn.execute(
            "DELETE FROM records WHERE case_id=? AND kind=? AND id=?",
            (case_id, kind, id))
        self.conn.commit()

    # --- 読み出し ---
    def get(self, kind: str, case_id: str, id: str, model: Type[T]) -> Optional[T]:
        row = self.conn.execute(
            "SELECT json FROM records WHERE case_id=? AND kind=? AND id=?",
            (case_id, kind, id)).fetchone()
        return model.model_validate_json(row[0]) if row else None

    def all(self, kind: str, case_id: str, model: Type[T]) -> list[T]:
        rows = self.conn.execute(
            "SELECT json FROM records WHERE case_id=? AND kind=? ORDER BY id",
            (case_id, kind)).fetchall()
        return [model.model_validate_json(r[0]) for r in rows]

    def case_ids(self) -> list[str]:
        rows = self.conn.execute(
            "SELECT DISTINCT case_id FROM records WHERE kind='case'").fetchall()
        return [r[0] for r in rows]

    # --- 特化ビュー ---
    def has_source_hash(self, case_id: str, content_hash: str,
                        kind: str | None = None) -> bool:
        """冪等判定。kind を渡すと同一 kind 内でのみ重複とみなす
        (売り手資料と同一文面の公式サイトは別の出所として登録する — I3 との整合)。"""
        return any(s.content_hash == content_hash and (kind is None or s.kind == kind)
                   for s in self.all("source", case_id, Source))

    def latest_judgments(self, case_id: str) -> dict[str, Judgment]:
        """項目ごとに最新ラウンドの判定。履歴は残る(追記のみ)。"""
        latest: dict[str, Judgment] = {}
        for j in self.all("judgment", case_id, Judgment):
            cur = latest.get(j.item_id)
            if cur is None or j.round > cur.round:
                latest[j.item_id] = j
        return latest
