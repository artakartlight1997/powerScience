"""ドロップフォルダ取り込み(v0 の一次コレクタ)。

inbox/<case>/{seller,consultant,general}/ を走査し、ファイルごとに
Source + スナップショット(原文コピー + 抽出テキスト)を作る。
同一 content_hash は再取り込みしない(冪等)。as_of はファイル名の
YYYY-MM-DD_ プレフィクス、なければファイルの更新日時。
"""
from __future__ import annotations

import hashlib
import re
import shutil
import uuid
from datetime import datetime, timezone
from pathlib import Path

from .contracts import Case, Source
from .store import Store

_DATE_PREFIX = re.compile(r"^(\d{4}-\d{2}-\d{2})_")
_EXTS = {".pdf", ".txt", ".md"}

# サブフォルダ → (kind, trust_tier名, seller_provided)
SUBDIRS = {"seller": ("seller", "seller", True),
           "consultant": ("consultant", "consultant", False),
           "general": ("general", "web", False)}


def read_text(path: Path) -> str:
    if path.suffix.lower() == ".pdf":
        from pypdf import PdfReader  # 遅延 import(txt のみの環境でも動く)
        reader = PdfReader(str(path))
        return "\n".join((page.extract_text() or "") for page in reader.pages)
    return path.read_text(encoding="utf-8", errors="replace")


def _as_of(path: Path) -> str:
    m = _DATE_PREFIX.match(path.name)
    if m:
        return m.group(1)
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).date().isoformat()


def snapshot(data_dir: Path, case_id: str, content_hash: str,
             raw: Path | None, text: str) -> Path:
    d = data_dir / case_id / "snapshots" / content_hash
    d.mkdir(parents=True, exist_ok=True)
    if raw is not None:
        shutil.copy2(raw, d / f"raw{raw.suffix.lower()}")
    (d / "text.txt").write_text(text, encoding="utf-8")
    return d


def snapshot_text(snapshot_path: str | None) -> str | None:
    """grounding の照合先。スナップショットがなければ None(pass にはできない)。"""
    if not snapshot_path:
        return None
    p = Path(snapshot_path) / "text.txt"
    return p.read_text(encoding="utf-8") if p.exists() else None


def scan(store: Store, case: Case, inbox_dir: Path, data_dir: Path,
         trust_tiers: dict) -> list[Source]:
    """新規ファイルを取り込み、作成した Source を返す。"""
    created: list[Source] = []
    for sub, (kind, tier_key, seller) in SUBDIRS.items():
        folder = inbox_dir / case.id / sub
        if not folder.is_dir():
            continue
        for f in sorted(folder.iterdir()):
            if not f.is_file() or f.suffix.lower() not in _EXTS:
                continue
            h = hashlib.sha256(f.read_bytes()).hexdigest()
            if store.has_source_hash(case.id, h):
                continue  # 冪等: 同一内容は二度取り込まない
            text = read_text(f)
            snap = snapshot(data_dir, case.id, h, f, text)
            src = Source(id=f"src-{uuid.uuid4().hex[:12]}", case_id=case.id,
                         kind=kind, trust_tier=int(trust_tiers[tier_key]),
                         seller_provided=seller, path=str(f), as_of=_as_of(f),
                         content_hash=h, snapshot_path=str(snap))
            store.put("source", src)
            created.append(src)
    return created
