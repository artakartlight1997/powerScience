"""CLI v2。使い方は docs/MANUAL.md。入力は社名だけ(R-0)。

  prism research "社名" [--industry 業界] [--archetype id] [--case-id id] [--no-web]
  prism run <case_id> [--no-web]     # 既存ケースの続行(資料追加後の再実行にも)
  prism report <case_id>             # 射影のみ再生成
  prism status <case_id>             # 現況とイベント連鎖検証
  prism verify-chain <case_id>       # 改竄検知
"""
from __future__ import annotations

import argparse
import logging
import os
import sys
from datetime import date

from .config import load_config, require_api_key
from .contracts import Case, ConfigError, GateError, UserInputError
from .gate import check_vendor_separation
from .log import setup as setup_logging
from .store import Store

# 注意: __name__ は `python -m prism.cli` だと "__main__" になり prism 階層から
# 外れてファイルに書かれない。ここだけは名前を固定する。
log = logging.getLogger("prism.cli")


def _store(cfg) -> Store:
    return Store(cfg.data_dir / "prism.db")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="prism", description="Integral Prism PoC v2")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("research", help="社名だけでリサーチ開始(これが本体)")
    sp.add_argument("name", help="対象の社名または業界名")
    sp.add_argument("--industry")
    sp.add_argument("--archetype", help="業態テンプレID(未指定なら自動同定)")
    sp.add_argument("--case-id")
    sp.add_argument("--no-web", action="store_true",
                    help="Web収集を無効化(置いた資料だけで監査)")

    sp = sub.add_parser("run", help="既存ケースの続行(資料追加後の再実行にも)")
    sp.add_argument("case_id")
    sp.add_argument("--no-web", action="store_true")

    for name in ("report", "status", "verify-chain"):
        sp = sub.add_parser(name)
        sp.add_argument("case_id")

    args = p.parse_args(argv)
    cfg = load_config()
    log_path = setup_logging(cfg.data_dir)
    log.info("コマンド開始: %s", vars(args))
    store = _store(cfg)
    try:
        rc = _dispatch(args, cfg, store)
        log.info("コマンド終了: %s rc=%d", args.cmd, rc)
        return rc
    except UserInputError as e:
        # ユーザ入力の誤り(存在しないケースID等): バグ扱いにしない。
        # 汎用 ValueError は捕捉しない — pydantic ValidationError(バグ級)が
        # そのサブクラスであり、rc=3 経路でトレースバックをログに残すべきだから
        log.error("入力エラー: %s", e, extra={"console_suppress": True})
        print(f"{e}", file=sys.stderr)
        return 1
    except (ConfigError, GateError) as e:
        # 想定内の拒否(設定・ポリシー): ユーザが直せるのでメッセージだけ返す
        log.error("設定/ポリシーエラー: %s", e, extra={"console_suppress": True})
        print(f"設定エラー: {e}", file=sys.stderr)
        return 2
    except Exception:
        # バグの可能性: 全トレースバックはログへ。ユーザに状況説明はさせない
        log.exception("未処理例外(バグの可能性)", extra={"console_suppress": True})
        print(f"内部エラーが発生した。詳細な記録は {log_path} にある。\n"
              f"このファイルを開発者に渡せば、何が起きたかの説明は不要。", file=sys.stderr)
        return 3
    finally:
        store.close()


def _make_llm(cfg):
    check_vendor_separation(cfg.models["generator"], cfg.models["verifier"],
                            cfg.allow_same_vendor)
    require_api_key(cfg)
    from .llm import OpenRouterClient
    return OpenRouterClient(cfg)


def _make_web(cfg, llm, no_web: bool):
    if no_web:
        return None, None
    from .research import HttpxFetcher
    from .search import OpenRouterSearch
    return OpenRouterSearch(llm), HttpxFetcher()


def _today() -> date | None:
    """鮮度判定の基準日。通常は None(=今日)。PRISM_TODAY で固定できる(検証・テスト用)。"""
    v = os.environ.get("PRISM_TODAY")
    if not v:
        return None
    try:
        return date.fromisoformat(v)
    except ValueError:
        raise ConfigError(f"PRISM_TODAY が不正: {v!r}(YYYY-MM-DD形式)") from None


def _dispatch(args, cfg, store: Store) -> int:
    from . import pipeline

    if args.cmd == "research":
        today = _today()  # 設定不備はケース作成前に落とす
        llm = _make_llm(cfg)
        search, fetcher = _make_web(cfg, llm, args.no_web)
        case = pipeline.start_case(store, cfg, llm, args.name, args.industry,
                                   args.archetype, args.case_id)
        print(f"ケース {case.id}(アーキタイプ: {case.archetype})でリサーチ開始…")
        case = pipeline.run(store, cfg, case.id, llm, search, fetcher, today)
        print(f"停止: {case.stop_reason}(ラウンド{case.round}, LLM呼び出し{llm.calls}回)")
        print(f"出力: {cfg.out_dir / case.id}/(作戦盤: sakusenban.md)")
        print(f"補助資料(IM等)があれば {cfg.inbox_dir / case.id}/ に置いて"
              f" `prism run {case.id}` で反映")
        return 0

    if args.cmd == "run":
        llm = _make_llm(cfg)
        search, fetcher = _make_web(cfg, llm, args.no_web)
        case = pipeline.run(store, cfg, args.case_id, llm, search, fetcher, _today())
        print(f"停止: {case.stop_reason}(ラウンド{case.round}, LLM呼び出し{llm.calls}回)")
        print(f"出力: {cfg.out_dir / args.case_id}/")
        return 0

    if args.cmd == "report":
        for path in pipeline.write_outputs(store, cfg, args.case_id):
            print(path)
        return 0

    if args.cmd == "status":
        case = store.get("case", args.case_id, args.case_id, Case)
        if case is None:
            print(f"ケースが存在しない: {args.case_id}", file=sys.stderr)
            return 1
        from .contracts import Evidence, Source
        from .project import render_status
        ok, _n = store.events.verify_chain(args.case_id)
        print(render_status(case, store.latest_judgments(args.case_id),
                            len(store.all("source", args.case_id, Source)),
                            len(store.all("evidence", args.case_id, Evidence)), ok))
        return 0

    if args.cmd == "verify-chain":
        ok, n = store.events.verify_chain(args.case_id)
        if ok and n == 0:
            print(f"イベントが存在しない: {args.case_id}(ケースIDを確認)",
                  file=sys.stderr)
            return 1
        print(f"{'OK' if ok else 'NG(改竄の疑い)'}: {n} イベントを検証")
        return 0 if ok else 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
