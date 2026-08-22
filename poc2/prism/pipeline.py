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
from .contracts import (Case, ConfigError, Contradiction, Evidence, Fetcher,
                        LLMClient, Question, SearchClient, Source, SpecItem,
                        UserInputError)
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
        raise ConfigError(f"ケースIDが不正: {cid!r}(半角英数小文字・ハイフン等のみ)")
    standards = load_standards(cfg.templates_dir)
    existing = store.get("case", cid, cid, Case)
    if existing:
        if existing.name != name:
            # slugify 衝突等で別対象のケースに合流させない(証拠の混線防止)
            raise ConfigError(
                f"ケースID {cid} は別対象({existing.name})に使用済み。"
                f" --case-id で別IDを指定せよ")
        if archetype and archetype != existing.archetype:
            # 契約 §3: 人間の指定が常に勝つ。黙って無視しない。
            # 旧アーキタイプの判定・問いも消す(幽霊項目がレポート集計を汚さないように)
            log.info("アーキタイプ差替え: %s → %s(スペック再実体化)",
                     existing.archetype, archetype)
            existing.archetype = archetype
            store.put("case", existing)
            new_items = build_spec(existing, cfg.templates_dir, standards)
            new_ids = {it.id for it in new_items}
            new_keys = {it.key for it in new_items}
            for it in store.all("spec_item", cid, SpecItem):
                store.delete("spec_item", cid, it.id)
            from .contracts import Judgment
            for j in store.all("judgment", cid, Judgment):
                if j.item_id not in new_ids:
                    store.delete("judgment", cid, j.id)
            for q in store.all("question", cid, Question):
                if q.item_key not in new_keys:
                    store.delete("question", cid, q.id)
            store.put_many("spec_item", new_items)
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
        raise UserInputError(f"ケースが存在しない: {case_id}(先に research)")
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
    llm_budget = int(stop_rules["max_llm_calls"])
    retry_extract: set[str] = set()  # 前ラウンドで LLM 障害だったソース(C-7 再試行)

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
        # 3) 抽出(新規ソース + 前ラウンドで LLM 障害だったソースの再試行)
        sources = {s.id: s for s in store.all("source", case_id, Source)}
        targets = list(new_sources) + [sources[i] for i in sorted(retry_extract)
                                       if i in sources]
        for src in targets:
            evs = extract.run(src, items, llm)
            if evs is None:
                retry_extract.add(src.id)  # 一時障害: 次ラウンドで再試行
            else:
                retry_extract.discard(src.id)
                store.put_many("evidence", evs)
        # 4) 検証: grounding → クラスタ → 矛盾。R2 予算はラウンド内でも守る
        stored = store.all("evidence", case_id, Evidence)
        before = {e.id: (e.grounded, e.cluster_id) for e in stored}
        evidences = []
        deferred = 0
        for ev in stored:
            if ev.grounded == "none":
                if getattr(llm, "calls", 0) >= llm_budget:
                    deferred += 1  # none のまま温存(判定に使われず、R2 で停止する)
                else:
                    snap = ingest.snapshot_text(sources[ev.source_id].snapshot_path)
                    ev = ev.model_copy(update={"grounded": verify.ground(ev, snap, llm)})
            evidences.append(ev)
        if deferred:
            log.warning("R2予算(%d)到達: 証拠 %d 件の照合を保留", llm_budget, deferred)
        evidences = verify.cluster(evidences)
        # 変化した証拠だけ書き戻す(追記専用の連鎖を無変更 put で肥大させない)
        store.put_many("evidence",
                       [e for e in evidences
                        if (e.grounded, e.cluster_id) != before.get(e.id)])
        # 矛盾: 既存 open を現在の証拠状態で再評価(成立しなくなった対は resolved)
        # → その上で新規検出。resolve は新証拠の追加によってのみ起きる(P20)
        existing_cx = store.all("contradiction", case_id, Contradiction)
        resolved = verify.reevaluate_contradictions(existing_cx, evidences)
        store.put_many("contradiction", resolved)
        resolved_ids = {c.id for c in resolved}
        existing_cx = [c for c in existing_cx if c.id not in resolved_ids] + resolved
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
        # 6) 充填計画と問い。gap でなくなった項目の既存の問いは answered へ遷移
        #    (発注仕様書に「filledなのに発注scope」という自己矛盾を残さない)
        gap_keys = {it.key for it in fill.gaps(items, judgments)}
        for q in store.all("question", case_id, Question):
            if q.status == "open" and q.item_key not in gap_keys:
                store.put("question", q.model_copy(update={"status": "answered"}))
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
        raise UserInputError(f"ケースが存在しない: {case_id}")
    chain_ok, _ = store.events.verify_chain(case_id)
    # 防御的フィルタ: アーキタイプ差替え等の残骸(現行スペック外の項目)を
    # 集計・成果物に混入させない。証拠は事実なので無フィルタで台帳に載せる
    items = store.all("spec_item", case_id, SpecItem)
    ids = {it.id for it in items}
    keys = {it.key for it in items}
    judgments = {k: v for k, v in store.latest_judgments(case_id).items() if k in ids}
    return project.write_all(
        cfg.out_dir, case, items, judgments,
        store.all("evidence", case_id, Evidence),
        store.all("source", case_id, Source),
        [c for c in store.all("contradiction", case_id, Contradiction)
         if c.item_key in keys],
        [q for q in store.all("question", case_id, Question) if q.item_key in keys],
        chain_ok)
