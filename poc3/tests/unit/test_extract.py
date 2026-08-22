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
    ("前年比▲3%", -3.0, "%"),     # 負号が文字列先頭でなくても負(P19)
    ("−3%", -3.0, "%"),            # U+2212
    ("3%増", 3.0, "%"),            # 「増」は正のまま
    ("1.5万人", 15000.0, "万人"),
    ("0.5億円", 5e7, "億円"),
])
def test_parse_number(raw, num, unit):
    v = parse_number(raw)
    assert v.num == pytest.approx(num)
    assert v.unit == unit


@pytest.mark.parametrize("raw", ["3〜5億円", "10億円→12億円", "3~5億円"])
def test_parse_number_range_is_not_collapsed(raw):
    """範囲・遷移表現を先頭の裸の数値に潰さない(P19: 誤った数値を台帳に入れない)。"""
    v = parse_number(raw)
    assert v.raw == raw and v.num is None


def test_parse_number_no_digits_keeps_raw_only():
    v = parse_number("不明")
    assert v.raw == "不明" and v.num is None


def test_parse_number_none():
    assert parse_number(None) is None


def _source(tmp_path: Path, kind="seller", seller=True) -> Source:
    snap = tmp_path / "snap"
    snap.mkdir(parents=True)
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


def test_run_llm_failure_returns_none_for_retry(tmp_path):
    """C-7: LLM障害は None(再試行対象)。正常な0件([])と区別する。"""
    def boom(r, s, u):
        raise LLMError("down")
    assert run(_source(tmp_path / "a"), [make_item()], FakeLLM(boom)) is None
    ok = FakeLLM(lambda r, s, u: {"evidences": []})
    assert run(_source(tmp_path / "b", kind="general", seller=False),
               [make_item()], ok) == []


def test_run_caps_excessive_evidence_rows(tmp_path):
    items = [make_item(key="a")]
    rows = [{"item_key": "a", "quote": f"引用{i}", "raw_value": None}
            for i in range(10)]
    llm = FakeLLM(lambda r, s, u: {"evidences": rows})
    evs = run(_source(tmp_path), items, llm)
    assert len(evs) == 2 * len(items)  # 過剰生成は上限で切り詰め(R2予算の保護)


def test_run_without_snapshot_returns_empty(tmp_path):
    src = _source(tmp_path).model_copy(update={"snapshot_path": None})
    assert run(src, [make_item()], FakeLLM()) == []


def test_run_normalizes_status_and_passes_not_found(tmp_path):
    """C-3: 不正な status は AMBIGUOUS に正規化(ValidationErrorで全滅させない)。
    NOT_FOUND(探して無かった)はそのまま通る。"""
    items = [make_item(key="a"), make_item(id="c:b", key="b")]
    llm = FakeLLM(lambda r, s, u: {"evidences": [
        {"item_key": "a", "quote": "何かの記述", "raw_value": None, "status": "weird!!"},
        {"item_key": "b", "quote": "設備投資はほぼ不要", "raw_value": None,
         "status": "NOT_FOUND"},
    ]})
    evs = run(_source(tmp_path), items, llm)
    by = {e.item_key: e for e in evs}
    assert by["a"].status == "AMBIGUOUS"
    assert by["b"].status == "NOT_FOUND"
