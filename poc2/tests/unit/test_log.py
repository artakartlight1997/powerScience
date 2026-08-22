"""ログ(飛行記録): バグの所在をユーザに報告させないこと。

- 縮退(C-7)は黙って起きない: 抽出失敗は WARNING がログに残る
- 未処理例外はトレースバック込みでログファイルに残り、ユーザにはファイルパスの
  一文だけが出る(rc=3)
"""
import logging

from prism import cli
from prism.contracts import LLMError
from prism.extract import run as extract_run
from prism.log import setup

from ..conftest import FakeLLM, make_item


def test_setup_creates_logfile_and_writes(tmp_path):
    path = setup(tmp_path)
    logging.getLogger("prism.test").warning("hello-log")
    assert path.is_file()
    assert "hello-log" in path.read_text(encoding="utf-8")


def test_setup_is_idempotent_no_duplicate_handlers(tmp_path):
    setup(tmp_path)
    setup(tmp_path)
    root = logging.getLogger("prism")
    from logging.handlers import RotatingFileHandler
    assert sum(isinstance(h, RotatingFileHandler) for h in root.handlers) == 1


def test_extract_degradation_is_logged(tmp_path, caplog):
    from prism.contracts import Source
    snap = tmp_path / "snap"
    snap.mkdir()
    (snap / "text.txt").write_text("本文", encoding="utf-8")
    src = Source(id="s1", case_id="case1", kind="seller", trust_tier=5,
                 seller_provided=True, as_of="2026-01-15", content_hash="h",
                 snapshot_path=str(snap))

    def boom(r, s, u):
        raise LLMError("api down")

    with caplog.at_level(logging.WARNING, logger="prism.extract"):
        assert extract_run(src, [make_item()], FakeLLM(boom)) == []
    assert any("抽出失敗" in r.message for r in caplog.records)


def test_unhandled_exception_goes_to_logfile_not_user(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("PRISM_ROOT", str(tmp_path))
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    monkeypatch.setenv("PRISM_GENERATOR_MODEL", "anthropic/x")
    monkeypatch.setenv("PRISM_VERIFIER_MODEL", "openai/y")

    from prism import pipeline

    def crash(*a, **kw):
        raise RuntimeError("simulated-bug-123")

    monkeypatch.setattr(pipeline, "run", crash)
    rc = cli.main(["run", "case1"])
    assert rc == 3

    err = capsys.readouterr().err
    assert "simulated-bug-123" not in err          # ユーザに詳細は見せない
    assert "prism.log" in err                      # ログの場所だけ伝える

    logtext = (tmp_path / "data" / "logs" / "prism.log").read_text(encoding="utf-8")
    assert "simulated-bug-123" in logtext          # 開発者にはここで全部わかる
    assert "Traceback" in logtext


def test_config_error_is_friendly_rc2(tmp_path, monkeypatch, capsys):
    monkeypatch.setenv("PRISM_ROOT", str(tmp_path))
    monkeypatch.setenv("OPENROUTER_API_KEY", "sk-test")
    monkeypatch.setenv("PRISM_GENERATOR_MODEL", "openai/a")
    monkeypatch.setenv("PRISM_VERIFIER_MODEL", "openai/b")   # 同一ベンダ → C-6 拒否
    rc = cli.main(["run", "case1"])
    assert rc == 2
    assert "設定エラー" in capsys.readouterr().err
