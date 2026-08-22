"""テンプレート合成: 第1層(箱) + 第2層(アーキタイプ)が正しく実体化されること。"""
from datetime import datetime, timezone

import pytest

from prism.contracts import Case, ConfigError
from prism.templates import build_spec, load_archetype


def _case():
    return Case(id="case1", name="サンプルテック", archetype="ses_jutaku",
                created_at=datetime.now(timezone.utc).isoformat())


def test_build_spec_merges_boxes_and_archetype(templates_dir, standards):
    items = build_spec(_case(), templates_dir, standards)
    keys = {it.key for it in items}
    assert "b1-size" in keys            # 第1層(箱)
    assert "ses-utilization" in keys    # 第2層(アーキタイプ差し込み)
    assert "jutaku-enjo" in keys
    by_key = {it.key: it for it in items}
    assert by_key["ses-utilization"].segment == "ses"
    assert by_key["jutaku-enjo"].segment == "jutaku"
    assert by_key["b1-size"].segment is None


def test_expect_absent_flag_carried(templates_dir, standards):
    by_key = {it.key: it for it in build_spec(_case(), templates_dir, standards)}
    assert by_key["ses-capex"].expect_absent      # 「該当なし」=確認済みfilled 項目
    assert not by_key["b1-size"].expect_absent


def test_dependence_from_driver_watch_defaults(templates_dir, standards):
    by_key = {it.key: it for it in build_spec(_case(), templates_dir, standards)}
    assert by_key["ses-utilization"].dependence == "high"   # utilization ツリーの high
    assert by_key["ses-headcount"].dependence == "high"     # volume_cap
    assert by_key["ses-capex"].dependence == "mid"          # watch外はmid


def test_required_clusters_come_from_fund_standards(templates_dir, standards):
    items = build_spec(_case(), templates_dir, standards)
    assert all(it.required_clusters == standards["judgment"]["filled_min_clusters"]
               for it in items)


def test_unknown_archetype_raises(templates_dir, standards):
    case = _case().model_copy(update={"archetype": "does_not_exist"})
    with pytest.raises(ConfigError):
        build_spec(case, templates_dir, standards)


def test_archetype_yaml_declares_segments(templates_dir):
    a = load_archetype(templates_dir, "ses_jutaku")
    assert {s["id"] for s in a["segments"]} == {"ses", "jutaku"}
    assert {s["archetype"] for s in a["segments"]} == {"utilization", "order"}
