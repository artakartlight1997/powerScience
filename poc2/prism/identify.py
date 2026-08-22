"""アーキタイプ同定(P23: 収益方程式の型の同定は外部情報から可能。誤りは人間が一言で差替え)。

選択肢は templates/archetypes/ に実在するIDのみ。選択肢外の答えは受理しない。
同定できなければ推測で進まず ConfigError — 人間が --archetype で指定する。
"""
from __future__ import annotations

import logging

from .contracts import ConfigError, LLMClient, LLMError

log = logging.getLogger(__name__)

SYSTEM = """対象会社(または業界)の収益方程式のアーキタイプを、与えられた選択肢から1つ選べ。
判断がつかなければ "unknown" と答えよ。推測で選ぶな。
出力は次の JSON のみ: {"archetype":"選択肢のID または unknown","rationale":"一行"}"""


def archetype(llm: LLMClient, name: str, industry: str | None,
              choices: list[str]) -> str:
    user = (f"対象: {name}" + (f"(業界: {industry})" if industry else "")
            + f"\n選択肢: {', '.join(choices)}")
    out: dict = {}
    try:
        out = llm.complete_json("online", SYSTEM, user)
        ans = str(out.get("archetype", ""))
    except LLMError as e:
        log.warning("アーキタイプ同定のLLM呼び出しに失敗: %s", e)
        ans = ""
    if ans in choices:
        log.info("アーキタイプ同定: %s → %s(%s)", name, ans, out.get("rationale", ""))
        return ans
    raise ConfigError(
        f"アーキタイプを自動同定できなかった(答え: {ans or '失敗'})。"
        f" --archetype で指定せよ。選択肢: {', '.join(choices)}")
