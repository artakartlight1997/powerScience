"""CLI 正常系の E2E: research 1コマンド(rc=0)→ 成果物、run --no-web、report/status。
_make_llm/_make_web を Fake に差し替え、実LLM・実ネットワークなしで CLI 層まで通す。
"""

import pytest

from prism import cli

from ..conftest import POC_DIR, FakeFetcher, FakeLLM, FakeSearch
from .test_research_e2e import PAGES, _handler


@pytest.fixture
def cli_env(tmp_path, monkeypatch):
    monkeypatch.setenv("PRISM_ROOT", str(tmp_path))
    monkeypatch.setenv("PRISM_TEMPLATES_DIR", str(POC_DIR / "templates"))
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    monkeypatch.setenv("PRISM_GENERATOR_MODEL", "anthropic/x")
    monkeypatch.setenv("PRISM_VERIFIER_MODEL", "openai/y")
    llm = FakeLLM(_handler)
    monkeypatch.setattr(cli, "_make_llm", lambda cfg: llm)

    def fake_web(cfg, _llm, no_web):
        if no_web:
            return None, None
        from prism.contracts import SearchHit
        return (FakeSearch(lambda q, k: [SearchHit(url=u) for u in PAGES][:k]),
                FakeFetcher(PAGES))

    monkeypatch.setattr(cli, "_make_web", fake_web)
    # 再現性: pipeline.run の today は date.today() だが、鮮度判定は2年窓なので
    # フィクスチャの as_of(2026)が古くなるまでは実日付で問題ない
    return tmp_path, llm


def test_research_command_end_to_end(cli_env, capsys):
    tmp_path, llm = cli_env
    rc = cli.main(["research", "サンプルテック", "--industry", "ITサービス",
                   "--case-id", "case1"])
    assert rc == 0
    out = capsys.readouterr().out
    assert "停止: R" in out                      # 停止には必ず理由(P15)
    for f in ("sakusenban.md", "order_spec.md", "qc.md", "ledger.md", "status.md"):
        assert (tmp_path / "out" / "case1" / f).is_file(), f

    assert cli.main(["status", "case1"]) == 0
    assert cli.main(["report", "case1"]) == 0
    assert cli.main(["verify-chain", "case1"]) == 0


def test_run_no_web_and_user_errors(cli_env, capsys):
    tmp_path, llm = cli_env
    assert cli.main(["research", "サンプルテック", "--case-id", "case1",
                     "--archetype", "ses_jutaku", "--no-web"]) == 0

    # 存在しないケースはユーザエラー(rc=1)であり「内部エラー(バグ)」ではない
    assert cli.main(["run", "no-such-case"]) == 1
    assert cli.main(["report", "no-such-case"]) == 1
    assert cli.main(["verify-chain", "no-such-case"]) == 1
    err = capsys.readouterr().err
    assert "内部エラー" not in err
