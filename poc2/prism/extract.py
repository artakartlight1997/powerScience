"""証拠抽出。LLM(generator)が逐語引用を返し、数値はコードで parse する(P19)。

契約(§3): 値が読めない項目は出力しない。NOT_FOUND は「探して無かった」時のみ。
LLM 失敗はそのソースの抽出を落とすだけ(C-7)。
"""
from __future__ import annotations

import logging
import re
import uuid

from .contracts import Evidence, ExtractedValue, LLMClient, LLMError, Source, SpecItem
from .ingest import snapshot_text

log = logging.getLogger(__name__)

_MAX_CHARS = 16000

SYSTEM = """あなたはPEファンドのビジネスDDの証拠抽出器である。原文から要求項目に関する記述を探し、
逐語引用(quote)だけを返す。要約・言い換え・推測は禁止。原文に無い項目は出力しない。
明示的に「無い/不要/該当しない」と書かれている場合のみ status=NOT_FOUND とし、その記述を quote に入れる。
複数解釈がありうる曖昧な記述は status=AMBIGUOUS。
出力は次の JSON のみ: {"evidences":[{"item_key":"...","quote":"原文の逐語引用","page":1,"raw_value":"95%","status":"value"}]}
raw_value は quote 中の中心的な数値や値の文字列(なければ null)。"""

_NUM = re.compile(r"[▲△-]?\s*([0-9][0-9,]*\.?[0-9]*)\s*(兆円|億円|百万円|万円|千円|万人|%|％|人|円|件|社|名)?")
_SCALE = {"兆円": 1e12, "億円": 1e8, "百万円": 1e6, "万円": 1e4, "千円": 1e3,
          "万人": 1e4, "円": 1, "%": 1, "％": 1, "人": 1, "件": 1, "社": 1, "名": 1}


def parse_number(raw: str | None) -> ExtractedValue | None:
    """数値の解釈はコードのみが行う(P19)。単位を正規化した num を付す。"""
    if not raw:
        return None
    m = _NUM.search(raw)
    if not m:
        return ExtractedValue(raw=raw)
    num = float(m.group(1).replace(",", ""))
    unit = m.group(2)
    if unit:
        num *= _SCALE.get(unit, 1)
        if unit == "％":
            unit = "%"
    neg = raw.strip()[:1] in "▲△-"
    return ExtractedValue(raw=raw, num=-num if neg else num, unit=unit)


def run(source: Source, spec_items: list[SpecItem], llm: LLMClient) -> list[Evidence]:
    text = snapshot_text(source.snapshot_path)
    if not text:
        log.warning("抽出スキップ: source=%s にスナップショット本文がない", source.id)
        return []
    items_desc = "\n".join(
        f"- {it.key}: {it.label}" + (f" [セグメント:{it.segment}]" if it.segment else "")
        for it in spec_items)
    user = (f"## 要求項目\n{items_desc}\n\n## 原文(出所: {source.kind})\n"
            f"{text[:_MAX_CHARS]}")
    try:
        out = llm.complete_json("generator", SYSTEM, user)
    except LLMError as e:
        log.warning("抽出失敗(C-7縮退): source=%s kind=%s: %s", source.id, source.kind, e)
        return []  # C-7: このソースの抽出のみ落とす
    valid_keys = {it.key for it in spec_items}
    evidences: list[Evidence] = []
    dropped = 0
    for row in out.get("evidences", []):
        if not isinstance(row, dict):
            dropped += 1
            continue
        key, quote = row.get("item_key"), row.get("quote")
        if key not in valid_keys or not quote or not str(quote).strip():
            dropped += 1
            continue  # 契約: 読めない項目は出力しない(壊れた行は落とす)
        status = row.get("status", "value")
        if status not in ("value", "NOT_FOUND", "AMBIGUOUS"):
            status = "AMBIGUOUS"
        evidences.append(Evidence(
            id=f"ev-{uuid.uuid4().hex[:12]}", case_id=source.case_id,
            source_id=source.id, item_key=key, quote=str(quote).strip(),
            value=parse_number(row.get("raw_value")), status=status,
            locator={"page": row.get("page")},
            trust_label="untrusted" if source.kind == "web" else "trusted",
            seller_provided=source.seller_provided, as_of=source.as_of))
    if dropped:
        log.warning("抽出: source=%s で壊れた行 %d 件を破棄(C-3)", source.id, dropped)
    log.info("抽出: source=%s kind=%s → 証拠 %d 件", source.id, source.kind, len(evidences))
    return evidences
