"""抽出: 数値はコードで parse(P19)。壊れた行は落とす(C-3/C-7)。"""
from pathlib import Path

import pytest

from prism.contracts import LLMError, Source
from prism.extract import parse_number, run

from ..conftest import FakeLLM, make_item


@pytest.mark.parametrize("raw,num,unit", [
    ("95%", 95.0, "%"),
    ("95％", 95.0, "%"),
    ("1,200百万円", 1.2e9, "百万円"),
    ("約5億円", 5e8, "億円"),
    ("▲3億円", -3e8, "億円"),
    ("300名", 300.0, "名"),
])
def test_parse_number(raw, num, unit):
    v = parse_number(raw)
    assert v.num == pytest.approx(num)
    assert v.unit == unit


def test_parse_number_no_digits_keeps_raw_only():
    v = parse_number("不明")
    assert v.raw == "不明" and v.num is None


def test_parse_number_none():
    assert parse_number(None) is None


def _source(tmp_path: Path, kind="seller", seller=True) -> Source:
    snap = tmp_path / "snap"
    snap.mkdir()
    (snap / "text.txt").write_text("稼働率は95%で推移している。", encoding="utf-8")
    return Source(id="s1", case_id="case1", kind=kind, trust_tier=5,
                  seller_provided=seller, as_of="2026-01-15",
                  content_hash="h", snapshot_path=str(snap))


def test_run_drops_invalid_rows_and_parses_values(tmp_path):
    items = [make_item(key="ses-utilization"), make_item(id="c:x", key="b1-size")]
    llm = FakeLLM(lambda r, s, u: {"evidences": [
        {"item_key": "ses-utilization", "quote": "稼働率は95%で推移している",
         "page": 3, "raw_value": "95%", "status": "value"},
        {"item_key": "not-in-spec", "quote": "何か", "raw_value": None},   # 落とす
        {"item_key": "b1-size", "quote": "", "raw_value": "1兆円"},        # 空quoteは落とす
        "壊れた行",                                                        # 落とす
    ]})
    evs = run(_source(tmp_path), items, llm)
    assert len(evs) == 1
    ev = evs[0]
    assert ev.value.num == 95.0 and ev.locator["page"] == 3
    assert ev.seller_provided and ev.trust_label == "trusted"


def test_run_web_source_is_untrusted(tmp_path):
    src = _source(tmp_path, kind="web", seller=False)
    llm = FakeLLM(lambda r, s, u: {"evidences": [
        {"item_key": "ses-utilization", "quote": "稼働率は95%", "raw_value": "95%"}]})
    evs = run(src, [make_item(key="ses-utilization")], llm)
    assert evs[0].trust_label == "untrusted"  # P18


def test_run_llm_failure_degrades_to_empty(tmp_path):
    def boom(r, s, u):
        raise LLMError("down")
    assert run(_source(tmp_path), [make_item()], FakeLLM(boom)) == []  # C-7


def test_run_without_snapshot_returns_empty(tmp_path):
    src = _source(tmp_path).model_copy(update={"snapshot_path": None})
    assert run(src, [make_item()], FakeLLM()) == []
