"""E2E v2(R-0): 入力は社名だけ。資料ファイルなしで、アーキタイプ自動同定 →
Web収集(検索→取得→スナップショット)→ 抽出 → 検証 → 監査 → 射影が完走する。

シナリオ: 公式サイトは稼働率95%を掲載、業界記事は80% — 矛盾は保存され(P20)
filled を阻止。死んだURLからは何も生まれない(R-1)。
補助テスト: IM を後から置くと売り手の主張として突合され、I3 が保たれる。
"""
import shutil
from datetime import date

import pytest

from prism.config import Config
from prism.contracts import Contradiction, Evidence, Source
from prism.pipeline import run, slugify, start_case
from prism.store import Store

from ..conftest import POC_DIR, FakeFetcher, FakeLLM, FakeSearch

OFFICIAL = ("株式会社サンプルテック 公式サイト 会社情報 "
            "当社はSESおよび受託開発を提供する。売上構成はSESが60%、受託開発が40%である。"
            "エンジニアの稼働率は95%で推移している。")
ARTICLE = ("業界メディア分析記事 同社の稼働率は80%程度とみられる。"
           "IT人材市場の市場規模は約1兆円である。"
           "設備投資はほとんど不要であるアセットライト経営が特徴。")
PAGES = {"https://corp.example/about": OFFICIAL,
         "https://media.example/report": ARTICLE}  # dead.example は取得失敗
HITS = [{"url": "https://corp.example/about"},
        {"url": "https://dead.example/x"},
        {"url": "https://media.example/report"}]

_OFFICIAL_EV = {"evidences": [
    {"item_key": "b0-segments", "quote": "売上構成はSESが60%、受託開発が40%である",
     "page": 1, "raw_value": "60%", "status": "value"},
    {"item_key": "ses-utilization", "quote": "エンジニアの稼働率は95%で推移している",
     "page": 1, "raw_value": "95%", "status": "value"},
]}
_ARTICLE_EV = {"evidences": [
    {"item_key": "ses-utilization", "quote": "同社の稼働率は80%程度とみられる",
     "page": 1, "raw_value": "80%", "status": "value"},
    {"item_key": "b1-size", "quote": "IT人材市場の市場規模は約1兆円である",
     "page": 1, "raw_value": "1兆円", "status": "value"},
    {"item_key": "ses-capex", "quote": "設備投資はほとんど不要であるアセットライト経営が特徴",
     "page": 1, "raw_value": None, "status": "NOT_FOUND"},
]}
_IM_EV = {"evidences": [
    {"item_key": "ses-headcount", "quote": "エンジニア数は正社員300名、BP200名である",
     "page": 1, "raw_value": "300名", "status": "value"},
]}


def _handler(role, system, user):
    if role == "online":  # identify(選択肢つき)だけがここに来る
        return {"archetype": "ses_jutaku", "rationale": "SES/受託のITサービス"}
    if role == "generator":
        if "公式サイト" in user:
            return _OFFICIAL_EV
        if "業界メディア" in user:
            return _ARTICLE_EV
        if "IM抜粋" in user:
            return _IM_EV
        return {"evidences": []}
    return {"supported": False}


@pytest.fixture
def env(tmp_path):
    cfg = Config(api_key="", base_url="", models={}, data_dir=tmp_path / "data",
                 inbox_dir=tmp_path / "inbox", out_dir=tmp_path / "out",
                 templates_dir=POC_DIR / "templates")
    store = Store(cfg.data_dir / "prism.db")
    yield cfg, store
    store.close()


def _fakes():
    from prism.contracts import SearchHit
    return (FakeLLM(_handler),
            FakeSearch(lambda q, k: [SearchHit(**h) for h in HITS][:k]),
            FakeFetcher(PAGES))


def test_zero_input_end_to_end(env):
    cfg, store = env
    llm, search, fetcher = _fakes()

    # 入力は社名(と業界ヒント)だけ。資料ファイルは一切置かない(R-0)
    case = start_case(store, cfg, llm, "サンプルテック", industry="ITサービス")
    assert case.archetype == "ses_jutaku"        # 外部情報から自動同定(P23)
    case = run(store, cfg, case.id, llm, search, fetcher, today=date(2026, 8, 22))

    assert case.stop_reason and case.stop_reason.startswith("R3")

    # 収集: 取得成功した2ページだけが Source。死んだURLからは何も生まれない(R-1)
    sources = store.all("source", case.id, Source)
    assert {s.url for s in sources} == set(PAGES)
    assert all(s.kind == "web" and s.snapshot_path for s in sources)

    judgments = store.latest_judgments(case.id)
    by_key = {j.item_id.split(":", 1)[1]: j for j in judgments.values()}

    # 矛盾(95% vs 80%)は保存され filled を阻止(P20)
    cx = store.all("contradiction", case.id, Contradiction)
    assert len(cx) == 1 and cx[0].item_key == "ses-utilization"
    assert by_key["ses-utilization"].status == "thin"
    assert by_key["ses-utilization"].contradiction_open

    # Web証拠は untrusted(P18)だが、grounding は逐語一致で全て pass
    evs = store.all("evidence", case.id, Evidence)
    assert evs and all(e.trust_label == "untrusted" for e in evs)
    assert all(e.grounded == "pass" for e in evs)

    # 証拠ゼロの vdr/expert 項目は unknown + 取得手段(I8)→ 発注仕様書行き
    assert by_key["b2-segments"].status == "unknown"
    assert by_key["b2-segments"].acquisition_path

    # 射影5点 + イベント連鎖
    out = cfg.out_dir / case.id
    for f in ("sakusenban.md", "order_spec.md", "qc.md", "ledger.md", "status.md"):
        assert (out / f).is_file(), f
    assert store.events.verify_chain(case.id)[0]

    # クエリは gap 由来で、vdr/expert 専用項目には浪費されない(P21)
    assert search.queries and all("サンプルテック" in q for q in search.queries)


def test_supplement_im_respects_seller_rule(env):
    """IM を後から置く(任意の補助)— 売り手の主張として突合され I3 が保たれる。"""
    cfg, store = env
    llm, search, fetcher = _fakes()
    case = start_case(store, cfg, llm, "サンプルテック", archetype="ses_jutaku")
    run(store, cfg, case.id, llm, search, fetcher, today=date(2026, 8, 22))

    shutil.copy2(POC_DIR / "tests" / "fixtures" / "2026-01-15_seller_im.txt",
                 cfg.inbox_dir / case.id / "seller" / "2026-01-15_seller_im.txt")
    case = run(store, cfg, case.id, llm, search, fetcher, today=date(2026, 8, 22))

    judgments = store.latest_judgments(case.id)
    by_key = {j.item_id.split(":", 1)[1]: j for j in judgments.values()}
    # IM にしか無い項目は「売り手の主張のみ」で filled にならない(I3)
    assert by_key["ses-headcount"].status == "thin"
    assert "売り手" in by_key["ses-headcount"].rationale


def test_slugify_stable_for_japanese():
    assert slugify("株式会社サンプルテック") == slugify("株式会社サンプルテック")
    assert slugify("Sample Tech Inc.") == "sample-tech-inc"
