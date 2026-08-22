"""パイプラインの縁: R4の正しい計数(偽の完了宣言をしない)・3回目の再実行・
アーキタイプ差替え時の残骸掃除。ミューテーション監査(M5/M13)で実証された
テストの穴を塞ぐ回帰テスト。
"""
import shutil
from datetime import date, datetime, timezone

import pytest

from prism import pipeline
from prism.config import Config
from prism.contracts import Case, Question, SpecItem
from prism.store import Store

from ..conftest import POC_DIR, FakeLLM
from .test_research_e2e import _fakes


@pytest.fixture
def env(tmp_path):
    cfg = Config(api_key="", base_url="", models={}, data_dir=tmp_path / "data",
                 inbox_dir=tmp_path / "inbox", out_dir=tmp_path / "out",
                 templates_dir=POC_DIR / "templates")
    store = Store(cfg.data_dir / "prism.db")
    yield cfg, store
    store.close()


def test_r4_counts_items_not_capped_question_list(env, monkeypatch, tmp_path):
    """M13: 公開経路の gap が質問リスト上限(1件)の外に沈んでも R4 を偽宣言しない。"""
    cfg, store = env
    real_load = pipeline.load_standards

    def tight_standards(tdir):
        std = real_load(tdir)
        std["question_budget"]["max_open_questions"] = 1
        return std

    monkeypatch.setattr(pipeline, "load_standards", tight_standards)
    case = Case(id="case1", name="X社", archetype="ses_jutaku",
                created_at=datetime.now(timezone.utc).isoformat())
    store.put("case", case)
    # must+high の vdr専用項目(質問1位)と、must=False+low の public 項目(2位=切られる)
    store.put("spec_item", SpecItem(id="case1:v", case_id="case1", box="box2", key="v",
                                    label="VDR項目", must=True, dependence="high",
                                    retrievability=["vdr"]))
    store.put("spec_item", SpecItem(id="case1:p", case_id="case1", box="box1", key="p",
                                    label="公開項目", must=False, dependence="low",
                                    retrievability=["public"]))
    (cfg.inbox_dir / "case1" / "general").mkdir(parents=True)
    case = pipeline.run(store, cfg, "case1", FakeLLM(lambda r, s, u: {}),
                        today=date(2026, 8, 22))
    # 公開項目の gap が残っている以上、停止理由が「R4: 公開経路の gap ゼロ」ではない
    assert not case.stop_reason.startswith("R4")


def test_third_rerun_is_not_killed_by_cumulative_round_cap(env):
    """M5: 停止判定に通算 round を使うと3回目の再実行が R1 で誤停止する。"""
    cfg, store = env
    llm, search, fetcher = _fakes()
    case = pipeline.start_case(store, cfg, llm, "サンプルテック", archetype="ses_jutaku")
    for n, fixture in [(1, None), (2, "2026-01-15_seller_im.txt"),
                       (3, "2026-03-01_consultant_note.txt")]:
        if fixture:
            shutil.copy2(POC_DIR / "tests" / "fixtures" / fixture,
                         cfg.inbox_dir / case.id / ("seller" if "seller" in fixture
                                                    else "consultant") / fixture)
        prev_round = case.round
        case = pipeline.run(store, cfg, case.id, llm, search, fetcher,
                            today=date(2026, 8, 22))
        assert case.round >= prev_round + 2   # 毎回、最低でも進捗周+収束周の2周まわれる
        assert case.stop_reason.startswith("R3")  # 通算上限(R1)で誤停止しない


def test_archetype_swap_cleans_stale_judgments_and_questions(env, tmp_path):
    """差替え時に旧アーキタイプの判定・問いが残ってカバレッジ集計を汚さない。"""
    cfg, store = env
    # 一時テンプレディレクトリに第2アーキタイプを用意(定義ファイル追加のみで拡張可能の実証)
    tdir = tmp_path / "templates"
    shutil.copytree(POC_DIR / "templates", tdir)
    (tdir / "archetypes" / "jutaku_only.yaml").write_text(
        "id: jutaku_only\nname: 受託のみ\nsegments:\n"
        "  - {id: jutaku, name: 受託, archetype: order}\nitems: []\n",
        encoding="utf-8")
    cfg = Config(api_key="", base_url="", models={}, data_dir=cfg.data_dir,
                 inbox_dir=cfg.inbox_dir, out_dir=cfg.out_dir, templates_dir=tdir)

    llm, search, fetcher = _fakes()
    case = pipeline.start_case(store, cfg, llm, "サンプルテック", archetype="ses_jutaku")
    pipeline.run(store, cfg, case.id, llm, search, fetcher, today=date(2026, 8, 22))

    # 人間がアーキタイプを差し替え(契約 §3)
    case = pipeline.start_case(store, cfg, llm, "サンプルテック",
                               archetype="jutaku_only", case_id=case.id)
    assert case.archetype == "jutaku_only"
    items = store.all("spec_item", case.id, SpecItem)
    ids = {it.id for it in items}
    keys = {it.key for it in items}
    assert "ses-utilization" not in {it.key for it in items}  # 旧項目は消えた
    # 幽霊が残らない: 判定・問いは現行スペックの範囲内のみ
    assert set(store.latest_judgments(case.id)) <= ids
    assert {q.item_key for q in store.all("question", case.id, Question)} <= keys

    # 再実行してレポートの合計が現行項目数と一致する
    case = pipeline.run(store, cfg, case.id, llm, search, fetcher,
                        today=date(2026, 8, 22))
    out = (cfg.out_dir / case.id / "sakusenban.md").read_text(encoding="utf-8")
    import re
    m = re.search(r"filled (\d+) / thin (\d+) / missing (\d+) / unknown (\d+)(?:.*?)"
                  r"全(\d+)項目", out)
    assert m, out[:300]
    assert sum(int(x) for x in m.groups()[:4]) == int(m.group(5)) == len(items)


def test_slugify_collision_refuses_to_merge_cases(env):
    from prism.contracts import ConfigError
    cfg, store = env
    llm, _, _ = _fakes()
    pipeline.start_case(store, cfg, llm, "ABC株式会社", archetype="ses_jutaku",
                        case_id="abc")
    with pytest.raises(ConfigError, match="別対象"):
        pipeline.start_case(store, cfg, llm, "ABC商事", archetype="ses_jutaku",
                            case_id="abc")