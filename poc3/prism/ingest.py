"""ドロップフォルダ取り込み(任意の補助入力。R-0: 無くても正常)。

inbox/<case>/{seller,consultant,general}/ を走査し、ファイルごとに
Source + スナップショット(原文コピー + 抽出テキスト)を作る。
同一 kind 内の同一 content_hash は再取り込みしない(冪等)。as_of はファイル名の
YYYY-MM-DD_ プレフィクス(不正な日付は警告して更新日時へフォールバック)。
1ファイルの失敗はそのファイルだけを落とす(C-7)。書き込み先は gate を通す(C-5)。
"""
from __future__ import annotations

import hashlib
import logging
import re
import shutil
import uuid
from datetime import date, datetime, timezone
from pathlib import Path

from .contracts import Case, Source
from .gate import Gate
from .store import Store

log = logging.getLogger(__name__)

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
        try:
            return date.fromisoformat(m.group(1)).isoformat()
        except ValueError:
            log.warning("as_of: %s の日付プレフィクス %r が不正 → 更新日時を使う",
                        path.name, m.group(1))
    return datetime.fromtimestamp(path.stat().st_mtime, tz=timezone.utc).date().isoformat()


def snapshot(data_dir: Path, case_id: str, content_hash: str,
             raw: Path | None, text: str, gate: Gate) -> Path:
    """スナップショット書き込み。書き込み先は必ず gate のパス検査を通す(C-5)。"""
    d = gate.check_snapshot_path(Path(data_dir) / case_id / "snapshots" / content_hash)
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
         trust_tiers: dict, gate: Gate) -> list[Source]:
    """新規ファイルを取り込み、作成した Source を返す。1ファイルの失敗は落とすだけ。"""
    created: list[Source] = []
    inbox_root = Path(inbox_dir).resolve()
    for sub, (kind, tier_key, seller) in SUBDIRS.items():
        folder = inbox_dir / case.id / sub
        if not folder.is_dir():
            continue
        for f in sorted(folder.iterdir()):
            if not f.is_file():
                continue
            if f.suffix.lower() not in _EXTS:
                log.warning("取り込みスキップ: %s(対応形式は %s)", f.name,
                            "/".join(sorted(_EXTS)))
                continue
            if inbox_root not in f.resolve().parents:
                log.warning("取り込み拒否: %s は inbox 外を指す(シンボリックリンク?)",
                            f.name)
                continue
            try:
                h = hashlib.sha256(f.read_bytes()).hexdigest()
                if store.has_source_hash(case.id, h, kind=kind):
                    continue  # 冪等: 同一 kind 内の同一内容は二度取り込まない
                text = read_text(f)
                snap = snapshot(data_dir, case.id, h, f, text, gate)
            except (KeyboardInterrupt, SystemExit):
                raise
            except BaseException as e:  # C-7: このファイルだけ落とし、走査は続ける
                # (pypdf のネイティブ依存は Exception 階層外の例外を投げることがある)
                log.warning("取り込み失敗(このファイルのみスキップ): %s: %r", f.name, e)
                continue
            src = Source(id=f"src-{uuid.uuid4().hex[:12]}", case_id=case.id,
                         kind=kind, trust_tier=int(trust_tiers[tier_key]),
                         seller_provided=seller, path=str(f), as_of=_as_of(f),
                         content_hash=h, snapshot_path=str(snap))
            store.put("source", src)
            created.append(src)
            log.info("取り込み: source=%s kind=%s file=%s as_of=%s hash=%s",
                     src.id, kind, f.name, src.as_of, h[:12])
    return created
