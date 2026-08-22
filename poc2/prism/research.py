"""外部収集ループの中核(R-0/R-1)。計画(純関数)→検索→取得→必ずスナップショット。

- build_queries は純関数(C-2): gap の優先順から検索クエリを機械生成。
  Web で取れる見込みのある項目(retrievability に public/premium)だけに絞り、
  vdr/expert 専用項目にクエリを浪費しない(P21)
- collect は検索候補を gate に通し、取得できたものだけを Source 化。
  スナップショットに残らない情報は証拠になれない — 捏造URLはここで自然に死ぬ
"""
from __future__ import annotations

import hashlib
import logging
import uuid
from datetime import date
from pathlib import Path
from urllib.parse import urlparse

from . import fill
from .contracts import (Case, Fetcher, GateError, Judgment, Query, SearchClient,
                        Source, SpecItem)
from .gate import Gate
from .ingest import snapshot

log = logging.getLogger(__name__)


def build_queries(case: Case, items: list[SpecItem],
                  judgments: dict[str, Judgment], max_queries: int) -> list[Query]:
    """gap の優先順(fill.plan)に沿って検索クエリを作る。純関数。
    「公開経路」の定義は fill.is_public_reachable と共有(R4 判定とのズレ防止)。"""
    if max_queries <= 0:
        return []
    by_id = {it.id: it for it in items}
    queries: list[Query] = []
    for item_id in fill.plan(items, judgments):
        if len(queries) >= max_queries:
            break
        it = by_id[item_id]
        if not fill.is_public_reachable(it):
            continue  # vdr/expert 専用項目は Web に浪費しない(P21)
        seg = f" {it.segment}" if it.segment else ""
        queries.append(Query(item_key=it.key, text=f"{case.name}{seg} {it.label}"))
    return queries


def collect(store, case: Case, gate: Gate, search: SearchClient, fetcher: Fetcher,
            queries: list[Query], data_dir: Path, results_per_query: int,
            max_fetch: int, trust_tier_web: int,
            today: date | None = None) -> list[Source]:
    """検索→取得→スナップショット→Source。取得できなかった URL からは何も生まれない。
    同一 URL はラン内でも既存 Source とも重複取得しない(動的ページで「独立」を
    水増ししない — P22)。"""
    created: list[Source] = []
    fetched = 0
    seen_urls = {s.url for s in store.all("source", case.id, Source) if s.url}
    for q in queries:
        if fetched >= max_fetch:
            log.info("収集: 取得上限 %d 到達(以降のクエリは検索しない)", max_fetch)
            break
        for hit in search.search(q.text, results_per_query):
            if fetched >= max_fetch:
                break
            if hit.url in seen_urls:
                continue
            seen_urls.add(hit.url)
            try:
                gate.check_host(hit.url)
            except GateError as e:
                log.warning("収集: gate が拒否 url=%s: %s", hit.url, e)
                continue
            fetched += 1
            text = fetcher.fetch(hit.url)
            if not text:
                log.info("収集: 取得失敗 url=%s(候補は証拠にならず消える)", hit.url)
                continue
            h = hashlib.sha256(text.encode("utf-8")).hexdigest()
            if store.has_source_hash(case.id, h, kind="web"):
                continue  # 冪等: 同一内容の Web ソースは登録しない
            snap = snapshot(data_dir, case.id, h, None, text, gate)
            src = Source(id=f"src-{uuid.uuid4().hex[:12]}", case_id=case.id,
                         kind="web", trust_tier=trust_tier_web,
                         seller_provided=False, url=hit.url,
                         publisher=urlparse(hit.url).hostname,
                         as_of=(today or date.today()).isoformat(),
                         content_hash=h, snapshot_path=str(snap))
            store.put("source", src)
            created.append(src)
            log.info("収集: source=%s url=%s をスナップショット済みで登録(項目 %s)",
                     src.id, hit.url, q.item_key)
    return created


class HttpxFetcher:
    """既定の Fetcher 実装。HTML はタグ除去した素朴なテキストにする。"""

    def fetch(self, url: str) -> str | None:
        import re

        import httpx
        try:
            r = httpx.get(url, timeout=30, follow_redirects=True,
                          headers={"User-Agent": "integral-prism-poc/0.2"})
            r.raise_for_status()
            text = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", r.text,
                          flags=re.DOTALL | re.IGNORECASE)
            text = re.sub(r"<[^>]+>", " ", text)
            return re.sub(r"\s+", " ", text).strip() or None
        except Exception:
            return None  # 契約: 失敗は None
