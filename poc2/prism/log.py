"""ログ(飛行記録)。バグの所在をユーザに報告させないための仕組み。

- data/logs/prism.log にローテーション付きで全レベルを記録
- コンソールには WARNING 以上のみ(ユーザを煩わせない)
- 方針: 資料の本文・引用は書かない(MNPI をログに漏らさない)。
  ID・ハッシュ・件数・URL・例外だけを書く。それで再現調査には足りる。
"""
from __future__ import annotations

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

FORMAT = "%(asctime)s %(levelname)-7s %(name)s: %(message)s"


class _SkipConsole(logging.Filter):
    """extra={"console_suppress": True} の記録はコンソールに出さない
    (CLI が print で別途ユーザ向け文言を出すとき、二重表示を防ぐ)。"""

    def filter(self, record: logging.LogRecord) -> bool:
        return not getattr(record, "console_suppress", False)


class _NoTraceback(logging.Formatter):
    """コンソール用: トレースバックはファイルにだけ残し、画面には出さない。"""

    def format(self, record: logging.LogRecord) -> str:
        exc_info, exc_text = record.exc_info, record.exc_text
        record.exc_info, record.exc_text = None, None
        try:
            return super().format(record)
        finally:
            record.exc_info, record.exc_text = exc_info, exc_text


def setup(data_dir: str | Path, verbose: bool = False) -> Path:
    """'prism' ルートロガーを設定し、ログファイルのパスを返す。多重呼び出しは無害。"""
    log_dir = Path(data_dir) / "logs"
    log_dir.mkdir(parents=True, exist_ok=True)
    path = log_dir / "prism.log"
    root = logging.getLogger("prism")
    root.setLevel(logging.DEBUG)
    # 既存のファイルハンドラ: 同じパスなら再利用、違うパスなら付け替える
    for h in [h for h in root.handlers if isinstance(h, RotatingFileHandler)]:
        if Path(h.baseFilename) != path.resolve():
            root.removeHandler(h)
            h.close()
    if not any(isinstance(h, RotatingFileHandler) for h in root.handlers):
        fh = RotatingFileHandler(path, maxBytes=5_000_000, backupCount=3,
                                 encoding="utf-8")
        fh.setLevel(logging.DEBUG)
        fh.setFormatter(logging.Formatter(FORMAT))
        root.addHandler(fh)
    if not any(isinstance(h, logging.StreamHandler)
               and not isinstance(h, RotatingFileHandler) for h in root.handlers):
        ch = logging.StreamHandler(sys.stderr)
        ch.setLevel(logging.INFO if verbose else logging.WARNING)
        ch.setFormatter(_NoTraceback("%(levelname)s: %(message)s"))
        ch.addFilter(_SkipConsole())
        root.addHandler(ch)
    return path
