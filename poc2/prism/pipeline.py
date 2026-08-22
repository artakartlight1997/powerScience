"""パイプライン v2: 社名だけから外部収集ループで台帳をゼロ構築する(R-0, P23)。

各ラウンド: 補助取込(任意の資料)→ Web収集(一次経路)→ 抽出 → 検証 → 監査 →
充填計画 → 停止判定(理由必須)。判定(audit/fill/クエリ計画)は純関数。
"""
from __future__ import annotations

import hashlib
import logging
import re
from datetime import date, datetime, timezone
from pathlib import Path

from . import audit, extract, fill, identify, ingest, project, research, verify
from .config import Config
from .contracts import (Case, Contradiction, Evidence, Fetcher, LLMClient,
                        Question, SearchClient, Source, SpecItem)
from .gate import Gate
from .store import Store
from .templates import build_spec, list_archetypes, load_standards

log = logging.getLogger(__name__)


_CASE_ID = re.compile(r"^[a-z0-9][a-z0-9_-]{0,63}$")


def slugify(name: str) -> str:
    """社名からケースIDを自動生成(日本語名はハッシュで安定化)。"""
    s = re.sub(r"[^a-z0-9]+", "-", name.lower()).strip("-")
    return s if len(s) >= 3 else "case-" + hashlib.sha1(name.encode("utf-8")).hexdigest()[:8]


def start_case(store: Store, cfg: Config, llm: LLMClient, name: str,
               industry: str | None = None, archetype: str | None = None,
               case_id: str | None = None) -> Case:
    """社名だけで呼べる(R-0)。archetype 未指定なら外部情報から同定(P23)。
    人間の archetype 指定は常に優先: 既存ケースでも差し替えてスペックを再実体化する。"""
    cid = case_id or slugify(name)
    if not _CASE_ID.match(cid):
        from .contracts import ConfigError
        raise ConfigError(f"ケースIDが不正: {cid!r}(半角英数小文字・ハイフン等のみ)")
    standards = load_standards(cfg.templates_dir)
    existing = store.get("case", cid, cid, Case)
    if existing:
        if archetype and archetype != existing.archetype:
            # 契約 §3: 人間の指定が常に勝つ。黙って無視しない
            log.info("アーキタイプ差替え: %s → %s(スペック再実体化)",
                     existing.archetype, archetype)
            for it in store.all("spec_item", cid, SpecItem):
                store.delete("spec_item", cid, it.id)
            existing.archetype = archetype
            store.put("case", existing)
            store.put_many("spec_item",
                           build_spec(existing, cfg.templates_dir, standards))
        return existing
    if not archetype:
        archetype = identify.archetype(llm, name, industry,
                                       list_archetypes(cfg.templates_dir))
    case = Case(id=cid, name=name, industry=industry, archetype=archetype,
                created_at=datetime.now(timezone.utc).isoformat())
    store.put("case", case)
    store.put_many("spec_item", build_spec(case, cfg.templates_dir, standards))
    for sub in ("seller", "consultant", "general"):  # 補助入力(任意)の受け口
        (cfg.inbox_dir / cid / sub).mkdir(parents=True, exist_ok=True)
    log.info("ケース開始: id=%s name=%s archetype=%s", cid, name, archetype)
    return case


def run(store: Store, cfg: Config, case_id: str, llm: LLMClient,
        search: SearchClient | None = None, fetcher: Fetcher | None = None,
        today: date | None = None) -> Case:
    """search+fetcher が両方あるとき Web 収集が有効(既定の姿)。無ければ資料のみ。"""
    case = store.get("case", case_id, case_id, Case)
    if case is None:
        raise ValueError(f"ケースが存在しない: {case_id}(先に research)")
    standards = load_standards(cfg.templates_dir)
    items = store.all("spec_item", case_id, SpecItem)
    gate = Gate(standards["online"]["allowed_hosts"], cfg.data_dir)
    today = today or date.today()
    stop_rules = standards["stop_rules"]
    web_enabled = search is not None and fetcher is not None
    prev_progress = _progress(store.latest_judgments(case_id))
    # 再実行は「続行」: 前回の停止理由・ラウンド数を今回の停止判定に持ち込まない。
    # case.round は通算表示用、停止判定は今回のラン内ラウンド数で行う
    case.stop_reason = None
    rounds_this_run = 0

    while True:
        case.round += 1
        rounds_this_run += 1
        # 1) 補助取込(任意の資料。無くても正常 — R-0)
        new_sources = ingest.scan(store, case, cfg.inbox_dir, cfg.data_dir,
                                  standards["trust_tiers"], gate)
        # 2) Web 収集(一次経路): gap → クエリ(純関数)→ 検索 → 取得 → スナップショット
        if web_enabled:
            queries = research.build_queries(
                case, items, store.latest_judgments(case_id),
                standards["research"]["max_queries_per_round"])
            new_sources += research.collect(
                store, case, gate, search, fetcher, queries, cfg.data_dir,
                standards["research"]["results_per_query"],
                standards["online"]["max_fetch_per_iter"],
                standards["trust_tiers"]["web"], today)
        # 3) 抽出
        for src in new_sources:
            store.put_many("evidence", extract.run(src, items, llm))
        # 4) 検証: grounding → クラスタ → 矛盾
        sources = {s.id: s for s in store.all("source", case_id, Source)}
        stored = store.all("evidence", case_id, Evidence)
        before = {e.id: (e.grounded, e.cluster_id) for e in stored}
        evidences = []
        for ev in stored:
            if ev.grounded == "none":
                snap = ingest.snapshot_text(sources[ev.source_id].snapshot_path)
                ev = ev.model_copy(update={"grounded": verify.ground(ev, snap, llm)})
            evidences.append(ev)
        evidences = verify.cluster(evidences)
        # 変化した証拠だけ書き戻す(追記専用の連鎖を無変更 put で肥大させない)
        store.put_many("evidence",
                       [e for e in evidences
                        if (e.grounded, e.cluster_id) != before.get(e.id)])
        existing_cx = store.all("contradiction", case_id, Contradiction)
        new_cx = verify.contradictions(case_id, evidences, existing_cx)
        store.put_many("contradiction", new_cx)
        all_cx = existing_cx + new_cx
        # 5) 監査(純関数)— 全項目、毎ラウンド
        open_keys = {c.item_key for c in all_cx if c.status == "open"}
        judgments = {}
        for it in items:
            evs = [e for e in evidences if e.item_key == it.key]
            judgments[it.id] = audit.judge(it, evs, it.key in open_keys,
                                           case.round, today)
        store.put_many("judgment", list(judgments.values()))
        # 6) 充填計画と問い
        questions = fill.make_questions(
            case_id, items, judgments, standards["question_budget"]["max_open_questions"])
        store.put_many("question", questions)
        # 7) 停止判定(理由必須)。R4 は質問リスト(上限で切られる)でなく
        #    項目そのものから公開経路の gap を数える(偽の完了宣言を防ぐ)
        progress = _progress(judgments)
        llm_calls = getattr(llm, "calls", 0)
        open_public = fill.open_public_gaps(items, judgments)
        stop, reason = fill.should_stop(rounds_this_run, llm_calls,
                                        progress - prev_progress, open_public, stop_rules)
        log.info("case=%s round=%d(今回%d周目): 新規source=%d 証拠=%d "
                 "進捗(filled+thin)=%d LLM呼び出し累計=%d 停止=%s",
                 case_id, case.round, rounds_this_run, len(new_sources),
                 len(evidences), progress, llm_calls, reason or "続行")
        prev_progress = progress
        if stop:
            case.stop_reason = reason
        store.put("case", case)
        if stop:
            break

    write_outputs(store, cfg, case_id)
    return case


def _progress(judgments: dict) -> int:
    return sum(1 for j in judgments.values() if j.status in ("filled", "thin"))


def write_outputs(store: Store, cfg: Config, case_id: str) -> list[Path]:
    case = store.get("case", case_id, case_id, Case)
    if case is None:
        raise ValueError(f"ケースが存在しない: {case_id}")
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
