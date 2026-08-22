"""search(SearchClient 契約: 失敗は[])と llm(C-3: JSON強制+再試行は1回だけ)。"""
import pytest

from prism.config import Config, load_config
from prism.contracts import ConfigError, LLMError
from prism.llm import OpenRouterClient, parse_json_str
from prism.search import OpenRouterSearch

from ..conftest import FakeLLM


# --- search: 応答の形の異常を吸収し、例外を漏らさない ---
def test_search_non_list_results_returns_empty():
    s = OpenRouterSearch(FakeLLM(lambda r, sys, u: {"results": {"url": "https://x.example"}}))
    assert s.search("q", 3) == []  # dict が来ても例外を漏らさない(契約: 失敗は[])


def test_search_llm_error_returns_empty():
    def boom(r, sys, u):
        raise LLMError("down")
    assert OpenRouterSearch(FakeLLM(boom)).search("q", 3) == []


def test_search_filters_non_http_and_caps_k():
    rows = [{"url": "https://a.example"}, {"url": "ftp://bad.example"},
            {"url": "javascript:alert(1)"}, "broken", {"url": "https://b.example"},
            {"url": "https://c.example"}]
    s = OpenRouterSearch(FakeLLM(lambda r, sys, u: {"results": rows}))
    hits = s.search("q", 3)  # k=3 は「候補行の上限」— その中の妥当な url のみ返る
    assert [h.url for h in hits] == ["https://a.example"]


# --- llm.parse_json_str: フェンス・散文・波括弧入り散文を許容、dict 以外は拒否 ---
@pytest.mark.parametrize("text,expected", [
    ('{"a": 1}', {"a": 1}),
    ('前置き\n```json\n{"a": 1}\n```\n後書き', {"a": 1}),
    ('説明 {see} のあとに ```\n{"a": {"b": 2}}\n```', {"a": {"b": 2}}),
    ('結論は次: {"a": 1} です。補足 {b} も。', {"a": 1}),   # JSON後に波括弧入り散文
    ('注意 {x y z} 事項。本体: {"a": 1}', {"a": 1}),        # JSON前に波括弧入り散文
    ('```\nメモ\n```\n```json\n{"a": 1}\n```', {"a": 1}),   # 第2フェンスが正解
])
def test_parse_json_str_accepts(text, expected):
    assert parse_json_str(text) == expected


@pytest.mark.parametrize("text", ["[1, 2, 3]", "ただの文章", '["a", "b"]', "42"])
def test_parse_json_str_rejects_non_dict(text):
    with pytest.raises(ValueError):
        parse_json_str(text)


# --- llm.complete_json: ちょうど2試行(=再試行1回)で LLMError ---
def _cfg():
    return Config(api_key="k", base_url="https://or.example/api/v1",
                  models={"generator": "a/x", "verifier": "b/y", "online": "c/z"},
                  data_dir=None, inbox_dir=None, out_dir=None, templates_dir=None)


def test_complete_json_retries_exactly_once(monkeypatch):
    import httpx
    attempts = {"n": 0}

    def fake_post(*a, **kw):
        attempts["n"] += 1
        raise httpx.ConnectError("no network")

    monkeypatch.setattr(httpx, "post", fake_post)
    client = OpenRouterClient(_cfg())
    with pytest.raises(LLMError):
        client.complete_json("generator", "s", "u")
    assert attempts["n"] == 2       # C-3: 再試行は1回だけ
    assert client.calls == 2        # R2 の入力は実呼び出し数


def test_complete_json_success_parses_content(monkeypatch):
    import httpx

    class Resp:
        def raise_for_status(self):
            pass

        def json(self):
            return {"choices": [{"message": {"content": '```json\n{"ok": true}\n```'}}]}

    monkeypatch.setattr(httpx, "post", lambda *a, **kw: Resp())
    assert OpenRouterClient(_cfg()).complete_json("verifier", "s", "u") == {"ok": True}


# --- config: 設定タイプミスは ConfigError(バグ扱いにしない) ---
def test_bad_timeout_is_config_error():
    with pytest.raises(ConfigError, match="PRISM_LLM_TIMEOUT"):
        load_config({"PRISM_LLM_TIMEOUT": "abc"})
