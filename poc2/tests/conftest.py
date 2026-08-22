"""テスト共通部品。FakeLLM(C-1: Protocol 実装の差し替え)と組み立てヘルパ。"""
import sys
from pathlib import Path

POC_DIR = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(POC_DIR))

import pytest  # noqa: E402

from prism.contracts import Evidence, ExtractedValue, SpecItem  # noqa: E402
from prism.templates import load_standards  # noqa: E402


class FakeLLM:
    """handler(role, system, user) -> dict を差し込める Fake。LLMClient Protocol 実装。"""

    def __init__(self, handler=None):
        self.calls = 0
        self.handler = handler
        self.log = []

    def complete_json(self, role, system, user):
        self.calls += 1
        self.log.append((role, user[:80]))
        if self.handler:
            return self.handler(role, system, user)
        return {}


class FakeSearch:
    """handler(query, k) -> list[SearchHit] を差し込める Fake。SearchClient 実装。"""

    def __init__(self, handler=None):
        self.handler = handler
        self.queries = []

    def search(self, query, k):
        self.queries.append(query)
        return self.handler(query, k) if self.handler else []


class FakeFetcher:
    """pages: {url: text}。無い URL は None(=取得失敗)。Fetcher 実装。"""

    def __init__(self, pages=None):
        self.pages = pages or {}
        self.fetched = []

    def fetch(self, url):
        self.fetched.append(url)
        return self.pages.get(url)


@pytest.fixture
def templates_dir():
    return POC_DIR / "templates"


@pytest.fixture
def standards(templates_dir):
    return load_standards(templates_dir)


def make_item(**kw) -> SpecItem:
    base = dict(id="case1:it1", case_id="case1", box="box1", key="it1",
                label="テスト項目", retrievability=["public"], required_clusters=2)
    base.update(kw)
    return SpecItem(**base)


def make_ev(id="e1", item_key="it1", quote="引用", num=None, unit=None,
            grounded="pass", cluster_id=None, seller=False, status="value",
            as_of="2026-06-01", **kw) -> Evidence:
    value = ExtractedValue(raw=str(num), num=num, unit=unit) if num is not None else None
    return Evidence(id=id, case_id="case1", source_id="s1", item_key=item_key,
                    quote=quote, value=value, status=status, grounded=grounded,
                    cluster_id=cluster_id, seller_provided=seller, as_of=as_of, **kw)
