"""オンライン収集コレクタ。開いた問いから URL 候補を出し(online ロール)、
Fetcher で取得して必ずスナップショットする(スナップショットなしの Web 証拠は
grounded=pass になれない)。取得は gate を通す(C-5)。Web 由来は untrusted(P18)。
"""
from __future__ import annotations

import hashlib
import uuid
from datetime import date
from pathlib import Path

from .contracts import Case, Fetcher, GateError, LLMClient, LLMError, Question, Source
from .gate import Gate
from .ingest import snapshot

SYSTEM = """あなたはPEファンドの外部調査アシスタントである。対象会社と未解決の問いを渡すので、
それに答えうる公開WebページのURL候補を返す。実在が確実な一次情報(公式サイト、行政、業界統計、
信頼できる媒体)を優先する。出力は次の JSON のみ:
{"urls":[{"url":"https://...","item_key":"...","reason":"..."}]}"""


class OnlineCollector:
    def __init__(self, llm: LLMClient, fetcher: Fetcher, gate: Gate):
        self.llm = llm
        self.fetcher = fetcher
        self.gate = gate

    def collect(self, case: Case, questions: list[Question], store,
                data_dir: Path, max_fetch: int, trust_tier_web: int) -> list[Source]:
        open_web = [q for q in questions if q.channel in ("web", "premium")][:10]
        if not open_web:
            return []
        qtext = "\n".join(f"- ({q.item_key}) {q.text}" for q in open_web)
        user = (f"## 対象会社\n{case.name}"
                + (f"(業界: {case.industry})" if case.industry else "")
                + f"\n\n## 未解決の問い\n{qtext}")
        try:
            out = self.llm.complete_json("online", SYSTEM, user)
        except LLMError:
            return []  # C-7: 収集の失敗はラウンドを止めない
        created: list[Source] = []
        for row in (out.get("urls") or [])[:max_fetch]:
            url = row.get("url") if isinstance(row, dict) else None
            if not url:
                continue
            try:
                self.gate.check_host(url)
            except GateError:
                continue  # 許可外ホストは黙って捨てない方が良いが、PoC ではskip記録のみ
            text = self.fetcher.fetch(url)
            if not text:
                continue
            h = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if store.has_source_hash(case.id, h):
                continue
            snap = snapshot(data_dir, case.id, h, None, text)
            src = Source(id=f"src-{uuid.uuid4().hex[:12]}", case_id=case.id,
                         kind="web", trust_tier=trust_tier_web,
                         seller_provided=False, url=url,
                         as_of=date.today().isoformat(), content_hash=h,
                         snapshot_path=str(snap))
            store.put("source", src)
            created.append(src)
        return created


class HttpxFetcher:
    """既定の Fetcher 実装。HTML はタグ除去した素朴なテキストにする。"""

    def fetch(self, url: str) -> str | None:
        import re

        import httpx
        try:
            r = httpx.get(url, timeout=30, follow_redirects=True,
                          headers={"User-Agent": "integral-prism-poc/0.1"})
            r.raise_for_status()
            text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", r.text,
                          flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<[^>]+>", " ", text)
            return re.sub(r"\s+", " ", text).strip() or None
        except Exception:
            return None  # 契約: 失敗は None
