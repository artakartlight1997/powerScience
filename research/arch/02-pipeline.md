---
doc_id: arch-pipeline
title: "設計仕様 02 — パイプラインと監査アルゴリズム"
version: 1.0.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: architecture
language: ja
tags: [pipeline, coverage-audit, stop-rule, components]
depends_on: [arch-data-model, disc-internal-build]
---

# 02. パイプライン

## 1. フェーズ別フロー

### フェーズ T（ティーザー段階。社名不明でも動く）
```
入力: 業界名（＋規模・地域のヒントがあれば）
1. 業界の市場地図・競合セットを収集（DR/Web/Speeda手動投入）
2. 業界標準のアーキタイプ候補とドライバーツリーを仮実体化
3. 業界の定番の死因（アーキタイプの risk_items）を列挙
出力: 業界パック ＋「社名判明後に真っ先に確認するリスト」
（任意）ティーザー属性からのターゲット候補推定
```

### フェーズ N（社名判明 / IM 入手。ここが本番）
```
入力: 社名（IM が来たらフォルダに投入）
1. 箱0: セグメント×アーキタイプ同定（外部情報から。誤りは人間が一言で差替え）
2. スペックとツリーを実体化（templates × segments）
3. 収集ファンアウト（並列・未信頼側）→ 取り込み → 抽出（三値）
4. 検証: 接地（別ベンダ）→ 独立性クラスタ → 数値再計算 → 時点整合
5. IM は seller_provided=true で取り込み、全主張を外部証拠と突合 → 矛盾検出
6. カバレッジ監査 → 充填ループ → 停止
出力: 作戦盤＋台帳 / ウォッチリスト / 発注仕様書（コンサル・VDR請求・面談質問）
```

### フェーズ DD
```
入力: VDR 資料・コンサル報告書・専門家記録（届いたら投入）
1. 新資料で unknown/thin を充填（vdr 到達可能性の項目が埋まり始める）
2. コンサル報告書: 全主張を台帳と突合 →「何%が既知・公開再現可能か」を測定（納品物QC）
3. 台帳更新のたび、ウォッチリストと矛盾リストを再射影
出力: 納品物QC / 更新された台帳 / ICメモ骨子
```

## 2. カバレッジ判定アルゴリズム（監査の心臓）

```python
def judge(item, evidences) -> Judgment:
    # 同一クラスタは1回だけ数える（I9, P22）
    clusters = group_by(evidences, "independence_cluster_id")
    verified = [c for c in clusters if any(e.grounded and e.fresh(item.freshness_days)
                and not e.source.seller_provided_only for e in c)]
    if not evidences:
        if searched_channels(item) == []:            return Judgment("unknown", note="not_searched")
        if retrievability_public(item) < THRESHOLD:  return Judgment("unknown", path=best_path(item))  # P21
        return Judgment("missing")
    if len(verified) >= item.required_clusters and not open_contradiction(item):
        return Judgment("filled")     # 該当なしの確認も filled（例: SESの設備投資ほぼ不要）
    return Judgment("thin", rationale=density_breakdown(...))
```

判定は**文字数を一切見ない**。見るのは「検証済み・独立・新鮮な証拠の密度」だけ（P23）。
閾値（required_clusters, freshness_days）は項目ごとにテンプレで定義し、ファンド標準で上書き可。

## 3. 充填ループと優先順位

```
gap = {thin, missing} の項目 ＋ open な矛盾
priority_rank = 順位付けのみ（数値スコアを外部に出さない）:
  1. ストーリー依存度 high のドライバーに繋がる項目
  2. 矛盾が開いている項目（矛盾は最も価値が高い）
  3. must > should
  4. 取得コストが安い順（無料=VDR請求リスト追加 が最上位）
実行: Action Router が channel を選択（→ 03）
  public で埋まる見込み → 追加の狙い撃ち収集
  埋まらない見込み     → questions へ変換（発注仕様書・面談質問・VDR請求）★これも「成果」
```

## 4. 停止規則（P2/P15。必ず止まる）

以下の**いずれか**で自動停止:
1. 全 must 項目が filled または「unknown＋acquisition_path」になった
2. 直近 K ラウンドで filled/thin の遷移がゼロ（収穫逓減）
3. ラウンド上限・コスト上限（ファンド標準で設定）
4. 検証劣化の検知: 接地合格率がラウンドで低下傾向（−42%問題の防波堤）

停止時に必ず「**なぜ止まったか**」を台帳に記録し、作戦盤に表示する。

## 5. コンポーネントと権限（P5/P18: 役割ごとにモデルと権限を変える）

| ID | コンポーネント | 責務 | 権限 | モデル |
|---|---|---|---|---|
| C1 | 業態同定器 | 箱0。セグメント×アーキタイプ | 読み取り | 生成側（案件内固定） |
| C2 | 収集ワーカ群 | DR API・Web・EDINET 等（並列） | **未信頼側。ツール/認証情報なし** | 安価 |
| C3 | 取り込み・抽出 | OCR/パース→三値抽出＋locator | ファイル読み | document AI＋軽量 |
| C4 | 接地検証器 | サブ質問分解→原文照合（二値判定・順序入替） | **原文取得権** | **別ベンダ** |
| C5 | 数値エンジン | 決定論的計算・恒等式 | **コード実行権** | コードのみ |
| C6 | 独立性クラスタラ | derived_from 追跡・クラスタ割当 | 読み取り | 軽量 |
| C7 | 矛盾検出器 | evidence 間の食い違い→ contradicts 辺（解消しない） | 読み取り | 中位 |
| C8 | カバレッジ判定 | 上記アルゴリズム（決定論的。LLM は使わない） | DB | コード |
| C9 | 充填プランナ | gap 順位付け・Router 呼び出し | 予算配分 | 生成側 |
| C10 | 停止判定 | 停止規則（決定論的） | 実行停止 | コード |
| C11 | 射影器 | 6成果物の生成 | 読み取り | 生成側 |
| C12 | ポリシーゲート | 全ツール呼び出しの唯一の通り道・taint 検査 | — | コード |

並列にするのは C2 と C4（証拠単位）のみ。統合と判定は単一統制（P1、誤り増幅 17x→4.4x の教訓）。
