"""検索クライアント(SearchClient Protocol の実装)。

PoC の既定実装は OpenRouter の online ロール(検索接地モデル、例 perplexity/sonar)に
URL 候補を JSON で出させる。**検索結果は証拠ではない** — 取得+スナップショットに
成功したものだけが Source になる(R-1)ため、実在しない URL はそこで自然に死ぬ。
本物の検索API(Brave/Google CSE 等)への差し替えはこのクラス1つで済む(C-1)。
"""
from __future__ import annotations

import logging

from .contracts import LLMClient, LLMError, SearchHit

log = logging.getLogger(__name__)

SYSTEM = """あなたはPEファンドの外部調査の検索器である。検索クエリに対し、答えが載っている可能性が
高い実在の公開WebページのURLを返す。一次情報(公式サイト・行政・業界統計・信頼できる媒体・
求人/口コミサイト)を優先する。実在に自信のないURLは返さない。
出力は次の JSON のみ: {"results":[{"url":"https://...","title":"..."}]}"""


class OpenRouterSearch:
    def __init__(self, llm: LLMClient):
        self.llm = llm

    def search(self, query: str, k: int) -> list[SearchHit]:
        try:
            out = self.llm.complete_json("online", SYSTEM,
                                         f"検索クエリ: {query}\n最大 {k} 件。")
        except LLMError as e:
            log.warning("検索失敗(スキップ): query=%r: %s", query, e)
            return []
        hits: list[SearchHit] = []
        for row in (out.get("results") or [])[:k]:
            if isinstance(row, dict) and str(row.get("url", "")).startswith("http"):
                hits.append(SearchHit(url=row["url"], title=str(row.get("title", ""))))
        log.info("検索: query=%r → 候補 %d 件", query, len(hits))
        return hits
