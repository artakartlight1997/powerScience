"""射影: Markdown テーブルの安全化(untrusted な引用による崩壊防止)と問いのフィルタ。"""
from datetime import datetime, timezone

from prism.contracts import Case, Question, Source
from prism.project import render_ledger, render_order_spec, render_sakusenban

from ..conftest import make_ev, make_item


def _case():
    return Case(id="case1", name="サンプルテック", archetype="ses_jutaku",
                created_at=datetime.now(timezone.utc).isoformat())


def _src():
    return Source(id="s1", case_id="case1", kind="web", trust_tier=3,
                  as_of="2026-01-01", content_hash="h")


def test_ledger_row_survives_pipes_and_newlines():
    ev = make_ev(quote="悪意|注入\r\n次の行|さらに")  # source_id は conftest 既定の "s1"
    md = render_ledger(_case(), [ev], [_src()])
    row = next(line for line in md.splitlines() if "悪意" in line)
    assert "\n" not in row and row.count("|") == 9  # 1証拠=1行、列数が保たれる


def test_sakusenban_cells_escaped():
    from prism.contracts import Judgment
    item = make_item(label="ラベル|に|パイプ")
    j = Judgment(id="j1", case_id="case1", item_id=item.id, status="thin",
                 rationale="理由|も\n複数行", round=1)
    md = render_sakusenban(_case(), [item], {item.id: j}, [])
    row = next(line for line in md.splitlines() if "ラベル" in line)
    assert "\n" not in row and row.count("|") == 5  # 4列テーブル=パイプ5本のまま


def test_order_spec_shows_only_open_questions():
    item = make_item(key="k1")
    qs = [Question(id="q1", case_id="case1", item_key="k1", text="生きてる問い",
                   channel="web", rank=1, status="open"),
          Question(id="q2", case_id="case1", item_key="k1", text="解決済みの問い",
                   channel="web", rank=2, status="answered")]
    md = render_order_spec(_case(), [item], {}, qs)
    assert "生きてる問い" in md
    assert "解決済みの問い" not in md
