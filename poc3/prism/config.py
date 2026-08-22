"""環境変数からの設定読み込み。検証は gate.check_vendor_separation が行う。"""
from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from .contracts import ConfigError


@dataclass
class Config:
    api_key: str
    base_url: str
    models: dict  # role -> model id ("vendor/model" 形式)
    data_dir: Path
    inbox_dir: Path
    out_dir: Path
    templates_dir: Path
    allow_same_vendor: bool = False
    timeout: float = 120.0


def load_config(env: dict | None = None) -> Config:
    e = env if env is not None else os.environ
    root = Path(e.get("PRISM_ROOT", ".")).resolve()
    cfg = Config(
        api_key=e.get("OPENROUTER_API_KEY", ""),
        base_url=e.get("OPENROUTER_BASE_URL", "https://openrouter.ai/api/v1"),
        models={
            "generator": e.get("PRISM_GENERATOR_MODEL", "anthropic/claude-sonnet-4.5"),
            "verifier": e.get("PRISM_VERIFIER_MODEL", "openai/gpt-4o"),
            "online": e.get("PRISM_ONLINE_MODEL", "perplexity/sonar"),
        },
        data_dir=Path(e.get("PRISM_DATA_DIR", root / "data")),
        inbox_dir=Path(e.get("PRISM_INBOX_DIR", root / "inbox")),
        out_dir=Path(e.get("PRISM_OUT_DIR", root / "out")),
        templates_dir=Path(e.get("PRISM_TEMPLATES_DIR", root / "templates")),
        allow_same_vendor=e.get("PRISM_ALLOW_SAME_VENDOR", "") == "1",
        timeout=_float_env(e, "PRISM_LLM_TIMEOUT", "120"),
    )
    return cfg


def _float_env(e, key: str, default: str) -> float:
    raw = e.get(key, default)
    try:
        return float(raw)
    except ValueError:
        raise ConfigError(f"{key} は数値であること(現在値: {raw!r})") from None


def require_api_key(cfg: Config) -> None:
    if not cfg.api_key:
        raise ConfigError("OPENROUTER_API_KEY が未設定(実LLM実行に必要)")
