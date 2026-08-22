"""テンプレート読み込みとスペック構築。

templates/ は定義ファイルであり、アーキタイプ追加にコード変更を要しない(変更管理 §5)。
第1層(boxes.yaml: 業態非依存の問い) + 第2層(archetypes/*.yaml: 業態固有項目)を
合成して Case ごとの SpecItem 列を作る。
"""
from __future__ import annotations

from pathlib import Path

import yaml

from .contracts import Case, ConfigError, SpecItem


def load_yaml(path: str | Path) -> dict:
    p = Path(path)
    if not p.exists():
        raise ConfigError(f"テンプレートが見つからない: {p}")
    with open(p, encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_standards(templates_dir: str | Path) -> dict:
    return load_yaml(Path(templates_dir) / "fund" / "standards.yaml")


def load_boxes(templates_dir: str | Path) -> dict:
    return load_yaml(Path(templates_dir) / "boxes.yaml")


def load_archetype(templates_dir: str | Path, archetype_id: str) -> dict:
    return load_yaml(Path(templates_dir) / "archetypes" / f"{archetype_id}.yaml")


def load_driver(templates_dir: str | Path, driver_id: str) -> dict:
    return load_yaml(Path(templates_dir) / "drivers" / f"{driver_id}.yaml")


def _dependence_map(templates_dir: str | Path, archetype: dict) -> dict[str, str]:
    """ドライバーツリーの watch_defaults から項目の thesis_dependence 初期値を引く。"""
    dep: dict[str, str] = {}
    for seg in archetype.get("segments", []):
        tree = load_driver(templates_dir, seg["archetype"])
        for level, nodes in (tree.get("watch_defaults") or {}).items():
            lv = "mid" if level == "medium" else level
            for node in nodes:
                # high は mid を上書きするが、逆はしない
                if dep.get(node) != "high":
                    dep[node] = lv
    return dep


def build_spec(case: Case, templates_dir: str | Path, standards: dict) -> list[SpecItem]:
    """固定の物差しを Case に実体化する。箱0-10 の全項目 + アーキタイプ差し込み。"""
    boxes = load_boxes(templates_dir)
    archetype = load_archetype(templates_dir, case.archetype)
    dep = _dependence_map(templates_dir, archetype)
    jd = standards["judgment"]

    def to_item(row: dict, box_id: str, segment: str | None) -> SpecItem:
        driver = row.get("driver")
        return SpecItem(
            id=f"{case.id}:{row['id']}",
            case_id=case.id,
            segment=segment,
            box=box_id,
            key=row["id"],
            label=row["text"],
            must=bool(row.get("must", True)),
            retrievability=list(row.get("retrievability", [])),
            freshness_days=int(jd["freshness_days"]),
            required_clusters=int(jd["filled_min_clusters"]),
            driver=driver,
            dependence=dep.get(driver or "", "mid"),
            expect_absent=bool(row.get("expect_absent", False)),
        )

    items = [to_item(row, box["id"], None)
             for box in boxes["boxes"] for row in box["items"]]
    items += [to_item(row, row["box"], row.get("segment"))
              for row in archetype.get("items", [])]
    return items
