"""射影(レポートは view にすぎない — P11)。台帳から Markdown を生成するだけで、
ここでは何も判定しない。O1 作戦盤 / O2 発注仕様書 / O3 検収QC / O4 証拠台帳 / O5 状況。
"""
from __future__ import annotations

from collections import Counter
from pathlib import Path

from .contracts import Case, Contradiction, Evidence, Judgment, Question, Source, SpecItem

_MARK = {"filled": "✅", "thin": "🟡", "missing": "🔴", "unknown": "⚫"}


def _ev_index(evidences: list[Evidence]) -> dict[str, Evidence]:
    return {e.id: e for e in evidences}


def render_sakusenban(case: Case, items: list[SpecItem], judgments: dict[str, Judgment],
                      contradictions: list[Contradiction]) -> str:
    """O1 作戦盤: 箱×状態の全景 + 見張り台帳(依存度high) + 未解消の矛盾。"""
    counts = Counter(j.status for j in judgments.values())
    lines = [f"# 作戦盤 — {case.name}", "",
             f"アーキタイプ: {case.archetype} / フェーズ: {case.phase} / "
             f"ラウンド: {case.round} / 停止理由: {case.stop_reason or '(実行中)'}", "",
             f"**カバレッジ**: filled {counts.get('filled', 0)} / thin {counts.get('thin', 0)} / "
             f"missing {counts.get('missing', 0)} / unknown {counts.get('unknown', 0)}"
             f"(全{len(items)}項目)", "", "## 箱ごとの状態", ""]
    by_box: dict[str, list[SpecItem]] = {}
    for it in items:
        by_box.setdefault(it.box, []).append(it)
    for box in sorted(by_box):
        lines.append(f"### {box}")
        lines.append("| 項目 | セグメント | 状態 | 根拠 |")
        lines.append("|---|---|---|---|")
        for it in by_box[box]:
            j = judgments.get(it.id)
            st = j.status if j else "-"
            lines.append(f"| {it.label} | {it.segment or '全社'} | "
                         f"{_MARK.get(st, '')} {st} | {j.rationale if j else ''} |")
        lines.append("")
    lines += ["## 見張り台帳(thesis_dependence=high の項目)", "",
              "| ドライバー | 項目 | 状態 | 取得手段 |", "|---|---|---|---|"]
    for it in items:
        if it.dependence == "high":
            j = judgments.get(it.id)
            lines.append(f"| {it.driver} | {it.label} | {j.status if j else '-'} | "
                         f"{(j.acquisition_path if j else None) or '—'} |")
    open_cx = [c for c in contradictions if c.status == "open"]
    lines += ["", f"## 未解消の矛盾({len(open_cx)}件 — 平均も抑制もしない/P20)", ""]
    for c in open_cx:
        lines.append(f"- `{c.item_key}`: 証拠 {c.evidence_a} と {c.evidence_b} が"
                     f"相対乖離 {c.delta:.0%}。追加取得タスクに変換済み")
    return "\n".join(lines) + "\n"


def render_order_spec(case: Case, items: list[SpecItem], judgments: dict[str, Judgment],
                      questions: list[Question]) -> str:
    """O2 発注仕様書: filled=発注不要。unknown/missing/thin が scope(取得手段つき)。"""
    by_key = {it.key: it for it in items}
    lines = [f"# コンサル発注仕様書(叩き台) — {case.name}", "",
             "公開情報で **filled** の項目は発注不要。以下は未充足項目とその取得経路。", "",
             "| # | 問い | チャネル | 現状 |", "|---|---|---|---|"]
    for q in sorted(questions, key=lambda q: q.rank):
        it = by_key.get(q.item_key)
        j = judgments.get(it.id) if it else None
        lines.append(f"| {q.rank} | {q.text} | {q.channel} | {j.status if j else '-'} |")
    filled = [it.label for it in items
              if (j := judgments.get(it.id)) and j.status == "filled"]
    lines += ["", f"## 発注不要(公開情報で確認済み: {len(filled)}件)", ""]
    lines += [f"- {label}" for label in filled]
    return "\n".join(lines) + "\n"


def render_qc(case: Case, items: list[SpecItem], evidences: list[Evidence],
              sources: list[Source]) -> str:
    """O3 検収QC: コンサル成果物のうち公開証拠で再現できた項目の割合。"""
    src = {s.id: s for s in sources}
    cons_items = {e.item_key for e in evidences
                  if src.get(e.source_id) and src[e.source_id].kind == "consultant"}
    repro = {e.item_key for e in evidences if e.grounded == "pass"
             and src.get(e.source_id)
             and src[e.source_id].kind in ("general", "web", "filing")}
    both = cons_items & repro
    pct = f"{len(both) / len(cons_items):.0%}" if cons_items else "n/a(コンサル成果物なし)"
    lines = [f"# 検収QC — {case.name}", "",
             f"コンサル成果物がカバーする項目: {len(cons_items)}件。"
             f"うち公開証拠で独立に再現できた項目: {len(both)}件(**{pct}**)。", "",
             "再現できなかった項目(=コンサル固有の付加価値、または要検証):", ""]
    lines += [f"- {k}" for k in sorted(cons_items - repro)] or ["- (なし)"]
    return "\n".join(lines) + "\n"


def render_ledger(case: Case, evidences: list[Evidence], sources: list[Source]) -> str:
    """O4 証拠台帳: 全証拠の生きた一覧(検証状態・クラスタ・出所つき)。"""
    src = {s.id: s for s in sources}
    lines = [f"# 証拠台帳 — {case.name}", "",
             "| 項目 | 引用(先頭60字) | 値 | 出所 | as_of | grounded | クラスタ | 売り手? |",
             "|---|---|---|---|---|---|---|---|"]
    for e in sorted(evidences, key=lambda e: (e.item_key, e.id)):
        s = src.get(e.source_id)
        v = e.value.raw if e.value else ""
        origin = (s.kind + (f":{s.publisher}" if s and s.publisher else "")) if s else "?"
        lines.append(f"| {e.item_key} | {e.quote[:60].replace('|', '/')} | {v} | "
                     f"{origin} | {e.as_of} | {e.grounded} | {e.cluster_id or ''} | "
                     f"{'○' if e.seller_provided else ''} |")
    return "\n".join(lines) + "\n"


def render_status(case: Case, judgments: dict[str, Judgment],
                  n_sources: int, n_evidences: int, chain_ok: bool) -> str:
    counts = Counter(j.status for j in judgments.values())
    return (f"# 状況 — {case.name}\n\n"
            f"- ラウンド: {case.round} / 停止理由: {case.stop_reason or '(実行中)'}\n"
            f"- ソース: {n_sources} / 証拠: {n_evidences}\n"
            f"- filled {counts.get('filled', 0)} / thin {counts.get('thin', 0)} / "
            f"missing {counts.get('missing', 0)} / unknown {counts.get('unknown', 0)}\n"
            f"- イベント連鎖の検証: {'OK' if chain_ok else '**改竄の疑い**'}\n")


def write_all(out_dir: Path, case: Case, items: list[SpecItem],
              judgments: dict[str, Judgment], evidences: list[Evidence],
              sources: list[Source], contradictions: list[Contradiction],
              questions: list[Question], chain_ok: bool) -> list[Path]:
    d = out_dir / case.id
    d.mkdir(parents=True, exist_ok=True)
    files = {
        "sakusenban.md": render_sakusenban(case, items, judgments, contradictions),
        "order_spec.md": render_order_spec(case, items, judgments, questions),
        "qc.md": render_qc(case, items, evidences, sources),
        "ledger.md": render_ledger(case, evidences, sources),
        "status.md": render_status(case, judgments, len(sources), len(evidences), chain_ok),
    }
    paths = []
    for name, content in files.items():
        p = d / name
        p.write_text(content, encoding="utf-8")
        paths.append(p)
    return paths
