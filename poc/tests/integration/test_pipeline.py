"""E2E(FakeLLM): 取り込み→抽出→検証→監査→充填→射影が通ること(契約 §4)。

シナリオ: 売り手IMは稼働率95%と主張、外部記事は80% — 矛盾は保存され(P20)、
項目は filled にならない。設備投資は外部記事が「ほぼ不要」を明示 — expect_absent
項目の確認済みfilled。判定は全て決定論的(grounding は逐語一致で LLM 不要)。
"""
import shutil
from datetime import date


import pytest

from prism.config import Config
from prism.contracts import Contradiction, Evidence, Question
from prism.pipeline import init_case, run
from prism.store import Store

from ..conftest import POC_DIR, FakeLLM

FIXTURES = POC_DIR / "tests" / "fixtures"

# 抽出のFake応答: quote は必ずフィクスチャ原文の逐語(grounding が決定的に通る)
_SELLER = {"evidences": [
    {"item_key": "b0-segments", "quote": "売上構成はSESが60%、受託開発が40%である",
     "page": 1, "raw_value": "60%", "status": "value"},
    {"item_key": "ses-utilization", "quote": "エンジニアの稼働率は95%で推移している",
     "page": 1, "raw_value": "95%", "status": "value"},
    {"item_key": "ses-headcount", "quote": "エンジニア数は正社員300名、BP200名である",
     "page": 1, "raw_value": "300名", "status": "value"},
]}
_GENERAL = {"evidences": [
    {"item_key": "ses-utilization", "quote": "同社の稼働率は80%程度とみられる",
     "page": 1, "raw_value": "80%", "status": "value"},
    {"item_key": "b1-size", "quote": "IT人材市場の市場規模は約1兆円である",
     "page": 1, "raw_value": "1兆円", "status": "value"},
    {"item_key": "ses-capex", "quote": "設備投資はほとんど不要であるアセットライト経営が特徴",
     "page": 1, "raw_value": None, "status": "NOT_FOUND"},
]}
_CONSULTANT = {"evidences": [
    {"item_key": "b1-size", "quote": "IT人材市場の市場規模は約1兆円である",
     "page": 1, "raw_value": "1兆円", "status": "value"},
]}


def _handler(role, system, user):
    if role == "generator":
        if "IM抜粋" in user:
            return _SELLER
        if "業界レポート" in user:
            return _GENERAL
        if "コンサルタント中間報告" in user:
            return _CONSULTANT
        return {"evidences": []}
    return {"supported": False}  # verifier は本テストでは決定的照合で不要のはず


@pytest.fixture
def env(tmp_path):
    cfg = Config(api_key="", base_url="", models={}, data_dir=tmp_path / "data",
                 inbox_dir=tmp_path / "inbox", out_dir=tmp_path / "out",
                 templates_dir=POC_DIR / "templates")
    store = Store(cfg.data_dir / "prism.db")
    case = init_case(store, cfg, "case1", "サンプルテック", "ses_jutaku", "ITサービス")
    for name, sub in [("2026-01-15_seller_im.txt", "seller"),
                      ("2026-02-01_general_article.txt", "general"),
                      ("2026-03-01_consultant_note.txt", "consultant")]:
        shutil.copy2(FIXTURES / name, cfg.inbox_dir / "case1" / sub / name)
    yield cfg, store, case
    store.close()


def test_end_to_end(env):
    cfg, store, _ = env
    llm = FakeLLM(_handler)
    case = run(store, cfg, "case1", llm, fetcher=None, today=date(2026, 8, 22))

    # 停止は理由つき(収穫逓減 R3: 2周目に新規進捗なし)
    assert case.stop_reason and case.stop_reason.startswith("R3")
    assert case.round == 2

    judgments = store.latest_judgments("case1")
    by_key = {j.item_id.split(":", 1)[1]: j for j in judgments.values()}

    # 矛盾(95% vs 80%)は保存され、filled を阻止する(P20)
    cx = store.all("contradiction", "case1", Contradiction)
    assert len(cx) == 1 and cx[0].item_key == "ses-utilization" and cx[0].status == "open"
    assert by_key["ses-utilization"].status == "thin"
    assert by_key["ses-utilization"].contradiction_open

    # 売り手単独の主張は filled にならない(I3)
    assert by_key["b0-segments"].status == "thin"
    assert "売り手" in by_key["b0-segments"].rationale

    # 同一値のコンサル/記事は同一クラスタ = 独立2票にならない(P22/I9)
    assert by_key["b1-size"].status == "thin"
    assert by_key["b1-size"].verified_clusters == 1

    # expect_absent 項目は「ほぼ不要」の明示的確認だが、独立1クラスタ止まりなので thin
    assert by_key["ses-capex"].status == "thin"

    # 証拠ゼロの vdr/expert 項目は unknown + 取得手段(I8)
    assert by_key["b2-segments"].status == "unknown"
    assert by_key["b2-segments"].acquisition_path

    # 全証拠は grounding 済みで、逐語一致なので LLM(verifier) を使っていない
    evs = store.all("evidence", "case1", Evidence)
    assert evs and all(e.grounded == "pass" for e in evs)
    assert all(r == "generator" for r, _ in llm.log)

    # 射影5点が生成され、イベント連鎖は検証可能
    out = cfg.out_dir / "case1"
    for f in ("sakusenban.md", "order_spec.md", "qc.md", "ledger.md", "status.md"):
        assert (out / f).is_file(), f
    assert store.events.verify_chain("case1")[0]

    # 作戦盤に矛盾と見張り台帳が載る
    sakusen = (out / "sakusenban.md").read_text(encoding="utf-8")
    assert "未解消の矛盾" in sakusen and "ses-utilization" in sakusen
    # 発注仕様書には unknown 項目が chan つきで載る
    order = (out / "order_spec.md").read_text(encoding="utf-8")
    assert "vdr" in order
    # QC: コンサルがカバーした b1-size は公開証拠で再現済み = 100%
    qc = (out / "qc.md").read_text(encoding="utf-8")
    assert "100%" in qc

    # 再実行しても取り込みは冪等(ソース数不変)
    n_src = len(store.all("source", "case1", __import__("prism.contracts",
                                                        fromlist=["Source"]).Source))
    assert n_src == 3

    # 問いは open のまま順位つきで保存されている
    qs = store.all("question", "case1", Question)
    assert qs and all(q.rank >= 1 for q in qs)


def test_rerun_is_idempotent(env):
    cfg, store, _ = env
    run(store, cfg, "case1", FakeLLM(_handler), today=date(2026, 8, 22))
    from prism.contracts import Source
    n1 = len(store.all("source", "case1", Source))
    case2 = run(store, cfg, "case1", FakeLLM(_handler), today=date(2026, 8, 22))
    assert len(store.all("source", "case1", Source)) == n1  # 二重取り込みなし
    assert case2.stop_reason
    assert store.events.verify_chain("case1")[0]
