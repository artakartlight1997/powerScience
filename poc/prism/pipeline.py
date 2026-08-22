"""パイプライン: 取り込み → 抽出 → 検証 → 監査 → 充填計画 →(任意で収集)→ 射影。

各ラウンド末に必ず監査とイベント記録が走る(契約 §3)。停止理由は Case に保存。
LLM を持たないのは audit / fill(純関数)。I/O を持つのは ingest / collectors / project。
"""
from __future__ import annotations

import logging
from datetime import date, datetime, timezone
from pathlib import Path

log = logging.getLogger(__name__)

from . import audit, extract, fill, ingest, project, verify
from .config import Config
from .contracts import Case, Contradiction, Evidence, Fetcher, LLMClient, Question, Source, SpecItem
from .gate import Gate
from .store import Store
from .templates import build_spec, load_standards


def init_case(store: Store, cfg: Config, case_id: str, name: str,
              archetype: str, industry: str | None = None) -> Case:
    case = Case(id=case_id, name=name, industry=industry, archetype=archetype,
                created_at=datetime.now(timezone.utc).isoformat())
    store.put("case", case)
    standards = load_standards(cfg.templates_dir)
    store.put_many("spec_item", build_spec(case, cfg.templates_dir, standards))
    for sub in ("seller", "consultant", "general"):
        (cfg.inbox_dir / case_id / sub).mkdir(parents=True, exist_ok=True)
    return case


def run(store: Store, cfg: Config, case_id: str, llm: LLMClient,
        fetcher: Fetcher | None = None, today: date | None = None) -> Case:
    case = store.get("case", case_id, case_id, Case)
    if case is None:
        raise ValueError(f"ケースが存在しない: {case_id}(先に init-case)")
    standards = load_standards(cfg.templates_dir)
    items = store.all("spec_item", case_id, SpecItem)
    gate = Gate(standards["online"]["allowed_hosts"], cfg.data_dir)
    today = today or date.today()
    stop_rules = standards["stop_rules"]
    prev_progress = _progress(store.latest_judgments(case_id))

    collector = None
    if fetcher is not None:
        from .collectors import OnlineCollector
        collector = OnlineCollector(llm, fetcher, gate)

    while True:
        case.round += 1
        # 1) 取り込み(冪等)と抽出
        new_sources = ingest.scan(store, case, cfg.inbox_dir, cfg.data_dir,
                                  standards["trust_tiers"])
        for src in new_sources:
            store.put_many("evidence", extract.run(src, items, llm))

        # 2) 検証: grounding → クラスタ → 矛盾
        sources = {s.id: s for s in store.all("source", case_id, Source)}
        evidences = store.all("evidence", case_id, Evidence)
        changed = []
        for ev in evidences:
            if ev.grounded == "none":
                snap = ingest.snapshot_text(sources[ev.source_id].snapshot_path)
                changed.append(ev.model_copy(update={"grounded": verify.ground(ev, snap, llm)}))
            else:
                changed.append(ev)
        evidences = verify.cluster(changed)
        store.put_many("evidence", evidences)
        existing_cx = store.all("contradiction", case_id, Contradiction)
        new_cx = verify.contradictions(case_id, evidences, existing_cx)
        store.put_many("contradiction", new_cx)
        all_cx = existing_cx + new_cx

        # 3) 監査(純関数)— 全項目、毎ラウンド
        open_keys = {c.item_key for c in all_cx if c.status == "open"}
        judgments = {}
        for it in items:
            evs = [e for e in evidences if e.item_key == it.key]
            j = audit.judge(it, evs, it.key in open_keys, case.round, today)
            judgments[it.id] = j
        store.put_many("judgment", list(judgments.values()))

        # 4) 充填計画と問い
        questions = fill.make_questions(
            case_id, items, judgments, standards["question_budget"]["max_open_questions"])
        store.put_many("question", questions)

        # 5) 停止判定(理由必須)
        progress = _progress(judgments)
        llm_calls = getattr(llm, "calls", 0)
        open_public = sum(1 for q in questions if q.channel in ("web", "premium"))
        stop, reason = fill.should_stop(case.round, llm_calls,
                                        progress - prev_progress, open_public, stop_rules)
        log.info("case=%s round=%d: 新規source=%d 証拠=%d 進捗(filled+thin)=%d "
                 "LLM呼び出し累計=%d 停止=%s",
                 case_id, case.round, len(new_sources), len(evidences), progress,
                 llm_calls, reason or "続行")
        prev_progress = progress
        if stop:
            case.stop_reason = reason
            store.put("case", case)
            break
        store.put("case", case)

        # 6) オンライン収集(次ラウンドの入力を作る)。収集ゼロなら R3 で自然に停止
        if collector is not None:
            collector.collect(case, questions, store, cfg.data_dir,
                              standards["online"]["max_fetch_per_iter"],
                              standards["trust_tiers"]["web"])

    write_outputs(store, cfg, case_id)
    return case


def _progress(judgments: dict) -> int:
    return sum(1 for j in judgments.values() if j.status in ("filled", "thin"))


def write_outputs(store: Store, cfg: Config, case_id: str) -> list[Path]:
    case = store.get("case", case_id, case_id, Case)
    chain_ok, _ = store.events.verify_chain(case_id)
    return project.write_all(
        cfg.out_dir, case,
        store.all("spec_item", case_id, SpecItem),
        store.latest_judgments(case_id),
        store.all("evidence", case_id, Evidence),
        store.all("source", case_id, Source),
        store.all("contradiction", case_id, Contradiction),
        store.all("question", case_id, Question),
        chain_ok)
