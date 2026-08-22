"""OpenRouter クライアント。LLMClient Protocol の実装(C-1)。

出力は必ず JSON(C-3)。パース失敗は1回だけ再試行し、それでも失敗なら LLMError。
呼び出し側は項目単位で degrade する(C-7)。ロールごとにモデルを分ける(C-6)。
"""
from __future__ import annotations

import json
import logging
import re
from typing import Literal

import httpx

from .config import Config
from .contracts import LLMError

log = logging.getLogger(__name__)

_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


def parse_json_str(text: str) -> dict:
    """コードフェンス・前後の散文を許容して JSON オブジェクトを取り出す。

    順に試す: ①全文そのまま ②各コードフェンスの中身(最初の1つだけでなく全部)
    ③文中の各 '{' 位置から raw_decode(前後に波括弧を含む散文があっても正しい
    オブジェクトを見つける)。dict 以外(配列・スカラ)は受理しない。
    """
    candidates = [text.strip()] + [m.strip() for m in _FENCE.findall(text)]
    for cand in candidates:
        try:
            obj = json.loads(cand)
            if isinstance(obj, dict):
                return obj
        except ValueError:
            pass
    decoder = json.JSONDecoder()
    idx = text.find("{")
    while idx >= 0:
        try:
            obj, _end = decoder.raw_decode(text, idx)
            if isinstance(obj, dict):
                return obj
        except ValueError:
            pass
        idx = text.find("{", idx + 1)
    raise ValueError("JSON オブジェクトが見つからない")


class OpenRouterClient:
    def __init__(self, cfg: Config):
        self.cfg = cfg
        self.calls = 0  # 停止則 max_llm_calls の材料

    def complete_json(self, role: Literal["generator", "verifier", "online"],
                      system: str, user: str) -> dict:
        model = self.cfg.models[role]
        last: Exception | None = None
        for _attempt in range(2):  # C-3: 再試行は1回だけ
            self.calls += 1
            try:
                r = httpx.post(
                    f"{self.cfg.base_url}/chat/completions",
                    headers={"Authorization": f"Bearer {self.cfg.api_key}",
                             "Content-Type": "application/json"},
                    json={"model": model,
                          "messages": [{"role": "system", "content": system},
                                       {"role": "user", "content": user}],
                          "temperature": 0},
                    timeout=self.cfg.timeout)
                r.raise_for_status()
                content = r.json()["choices"][0]["message"]["content"]
                return parse_json_str(content)
            except Exception as e:  # ネットワーク・HTTP・JSON いずれも同じ扱い
                last = e
                log.warning("LLM失敗 role=%s model=%s 試行%d/2 入力%d字: %r",
                            role, model, _attempt + 1, len(user), e)
        log.error("LLM断念 role=%s model=%s: %r", role, model, last)
        raise LLMError(f"{role}({model}) の JSON 応答に2回失敗: {last}")
