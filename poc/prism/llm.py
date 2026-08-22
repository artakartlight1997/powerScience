"""OpenRouter クライアント。LLMClient Protocol の実装(C-1)。

出力は必ず JSON(C-3)。パース失敗は1回だけ再試行し、それでも失敗なら LLMError。
呼び出し側は項目単位で degrade する(C-7)。ロールごとにモデルを分ける(C-6)。
"""
from __future__ import annotations

import json
import re
from typing import Literal

import httpx

from .config import Config
from .contracts import LLMError

_FENCE = re.compile(r"```(?:json)?\s*(.*?)\s*```", re.DOTALL)


def parse_json_str(text: str) -> dict:
    """コードフェンス・前後の散文を許容して JSON オブジェクトを取り出す。"""
    m = _FENCE.search(text)
    if m:
        text = m.group(1)
    start = text.find("{")
    end = text.rfind("}")
    if start < 0 or end <= start:
        raise ValueError("JSON オブジェクトが見つからない")
    obj = json.loads(text[start:end + 1])
    if not isinstance(obj, dict):
        raise ValueError("JSON オブジェクトでない")
    return obj


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
        raise LLMError(f"{role}({model}) の JSON 応答に2回失敗: {last}")
