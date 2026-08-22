"""CLI。使い方は docs/MANUAL.md。

  prism init-case <case_id> --name 対象会社 --archetype ses_jutaku [--industry 業界]
  prism run <case_id> [--online]     # 監査ループを停止条件まで回す
  prism report <case_id>             # 射影のみ再生成
  prism status <case_id>             # 現況とイベント連鎖検証
  prism verify-chain <case_id>       # 改竄検知
"""
from __future__ import annotations

import argparse
import logging
import sys

from .config import load_config, require_api_key
from .contracts import Case, ConfigError, GateError
from .gate import check_vendor_separation
from .log import setup as setup_logging
from .store import Store

# 注意: __name__ は `python -m prism.cli` だと "__main__" になり prism 階層から
# 外れてファイルに書かれない。ここだけは名前を固定する。
log = logging.getLogger("prism.cli")


def _store(cfg) -> Store:
    return Store(cfg.data_dir / "prism.db")


def main(argv: list[str] | None = None) -> int:
    p = argparse.ArgumentParser(prog="prism", description="Integral Prism PoC")
    sub = p.add_subparsers(dest="cmd", required=True)

    sp = sub.add_parser("init-case", help="ケース作成(スペック実体化 + inbox 準備)")
    sp.add_argument("case_id")
    sp.add_argument("--name", required=True)
    sp.add_argument("--archetype", required=True)
    sp.add_argument("--industry")

    sp = sub.add_parser("run", help="監査ループ実行(inbox 取り込み→判定→射影)")
    sp.add_argument("case_id")
    sp.add_argument("--online", action="store_true",
                    help="Web 収集を有効化(gate の allowlist が適用される)")

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
    except (ConfigError, GateError) as e:
        # 想定内の拒否(設定・ポリシー): ユーザが直せるのでメッセージだけ返す
        log.error("設定/ポリシーエラー: %s", e, extra={"console_suppress": True})
        print(f"設定エラー: {e}", file=sys.stderr)
        return 2
    except Exception:
        # バグの可能性: 全トレースバックはログへ。ユーザに状況説明はさせない —
        # ログファイルを渡してもらえば再現調査に足りる(資料本文はログに書かない方針)
        log.exception("未処理例外(バグの可能性)", extra={"console_suppress": True})
        print(f"内部エラーが発生した。詳細な記録は {log_path} にある。\n"
              f"このファイルを開発者に渡せば、何が起きたかの説明は不要。", file=sys.stderr)
        return 3
    finally:
        store.close()


def _dispatch(args, cfg, store: Store) -> int:
    from . import pipeline

    if args.cmd == "init-case":
        case = pipeline.init_case(store, cfg, args.case_id, args.name,
                                  args.archetype, args.industry)
        print(f"ケース {case.id} を作成。資料を {cfg.inbox_dir / case.id} の "
              f"seller/ consultant/ general/ に置いて `prism run {case.id}`")
        return 0

    if args.cmd == "run":
        # 起動時検査: 生成と検証は別ベンダ(C-6)。API キー必須。
        check_vendor_separation(cfg.models["generator"], cfg.models["verifier"],
                                cfg.allow_same_vendor)
        require_api_key(cfg)
        from .llm import OpenRouterClient
        llm = OpenRouterClient(cfg)
        fetcher = None
        if args.online:
            from .collectors import HttpxFetcher
            fetcher = HttpxFetcher()
        case = pipeline.run(store, cfg, args.case_id, llm, fetcher)
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
        from .project import render_status
        from .contracts import Evidence, Source
        ok, n = store.events.verify_chain(args.case_id)
        print(render_status(case, store.latest_judgments(args.case_id),
                            len(store.all("source", args.case_id, Source)),
                            len(store.all("evidence", args.case_id, Evidence)), ok))
        return 0

    if args.cmd == "verify-chain":
        ok, n = store.events.verify_chain(args.case_id)
        print(f"{'OK' if ok else 'NG(改竄の疑い)'}: {n} イベントを検証")
        return 0 if ok else 2

    return 1


if __name__ == "__main__":
    raise SystemExit(main())
