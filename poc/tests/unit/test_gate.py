"""ゲート: ベンダ分離(C-6)・ホスト制限・パス逸脱・taint(P18)。"""
import pytest

from prism.contracts import ConfigError, GateError
from prism.gate import Gate, check_vendor_separation

from ..conftest import make_ev


def test_same_vendor_rejected():  # C-6
    with pytest.raises(ConfigError):
        check_vendor_separation("openai/gpt-4o", "openai/gpt-4o-mini")


def test_same_vendor_allowed_with_explicit_flag():
    check_vendor_separation("openai/gpt-4o", "openai/gpt-4o-mini", allow_same=True)


def test_different_vendors_ok():
    check_vendor_separation("anthropic/claude-sonnet-4.5", "openai/gpt-4o")


def test_host_allowlist(tmp_path):
    gate = Gate(["example.com"], tmp_path)
    gate.check_host("https://example.com/page")
    with pytest.raises(GateError):
        gate.check_host("https://evil.example.net/x")
    with pytest.raises(GateError):
        gate.check_host("ftp://example.com/x")


def test_empty_allowlist_allows_all(tmp_path):
    Gate([], tmp_path).check_host("https://anything.example.org/")


def test_snapshot_path_escape_rejected(tmp_path):
    gate = Gate([], tmp_path / "data")
    (tmp_path / "data").mkdir()
    gate.check_snapshot_path(tmp_path / "data" / "case1" / "snap")
    with pytest.raises(GateError):
        gate.check_snapshot_path(tmp_path / "data" / ".." / "secret.txt")
    with pytest.raises(GateError):
        gate.check_snapshot_path("/etc/passwd")


def test_untrusted_evidence_blocked_from_privileged_ops(tmp_path):
    gate = Gate([], tmp_path)
    ev = make_ev(trust_label="untrusted")
    with pytest.raises(GateError):
        gate.check_untainted(ev, "shell")
    gate.check_untainted(ev, "render_report")  # 非特権操作は許可
    gate.check_untainted(make_ev(trust_label="trusted"), "shell")
