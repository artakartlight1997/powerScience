"""ポリシーゲート。外部との境界は必ずここを通る(C-5, C-6, P18)。"""
from __future__ import annotations

from pathlib import Path
from urllib.parse import urlparse

from .contracts import ConfigError, Evidence, GateError

# untrusted 由来の値を渡してはならない操作(P18: taint された値は特権引数に不可)
PRIVILEGED_OPS = {"shell", "file_write_outside_case", "external_send"}


def check_vendor_separation(generator_model: str, verifier_model: str,
                            allow_same: bool = False) -> None:
    """生成と検証は別ベンダ(C-6)。同一なら起動拒否。明示フラグでのみ解除。"""
    gv = generator_model.split("/")[0].lower()
    vv = verifier_model.split("/")[0].lower()
    if gv == vv and not allow_same:
        raise ConfigError(
            f"生成({generator_model})と検証({verifier_model})が同一ベンダ '{gv}'。"
            " 別ベンダにするか PRISM_ALLOW_SAME_VENDOR=1 を明示せよ(C-6)")


class Gate:
    def __init__(self, allowed_hosts: list[str], data_dir: str | Path):
        self.allowed_hosts = [h.lower() for h in allowed_hosts]
        self.data_dir = Path(data_dir).resolve()

    def check_host(self, url: str) -> None:
        """allowlist が空なら全許可(社内運用)。指定時は完全一致のみ許可。"""
        host = (urlparse(url).hostname or "").lower()
        if not host or urlparse(url).scheme not in ("http", "https"):
            raise GateError(f"不正なURL: {url}")
        if self.allowed_hosts and host not in self.allowed_hosts:
            raise GateError(f"許可されていないホスト: {host}")

    def check_snapshot_path(self, path: str | Path) -> Path:
        """スナップショットの読み書きは data_dir 配下に限定(パス逸脱の拒否)。"""
        p = Path(path).resolve()
        if self.data_dir != p and self.data_dir not in p.parents:
            raise GateError(f"データディレクトリ外へのアクセス: {p}")
        return p

    def check_untainted(self, ev: Evidence, operation: str) -> None:
        """untrusted 証拠の値は特権操作の引数にできない(I4 相当)。"""
        if operation in PRIVILEGED_OPS and ev.trust_label == "untrusted":
            raise GateError(
                f"untrusted 証拠 {ev.id} を特権操作 {operation} に渡すことは禁止(P18)")
