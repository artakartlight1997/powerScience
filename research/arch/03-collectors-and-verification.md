---
doc_id: arch-collectors
title: "設計仕様 03 — 収集系と検証スタック"
version: 1.0.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: architecture
language: ja
tags: [collectors, router, verification, grounding, licensing]
depends_on: [arch-pipeline, t-citation-attribution, t-numeric-verification]
---

# 03. 収集系と検証スタック

## 1. 収集系（Collectors）— 全て差し替え可能なアダプタ

共通インタフェース: `collect(case, spec_item?) -> RawDoc[]`（RawDoc は必ず source メタデータ付き）

| コレクタ | 対象 | 到達可能性 | v0 | ライセンス注意 |
|---|---|---|---|---|
| Google DR API | 公開 Web の深掘り（$2–5/task） | public | ✅ | 利用規約の範囲で |
| Web 検索 API | ニュース・企業サイト・口コミ | public | ✅ | — |
| EDINET/TDnet | 有報・適時開示（**上場のみ**） | public | ✅ | 公的データ |
| 求人（採用サイト等） | 採用動向＝成長制約・戦略の先行指標 | public | ✅ | 規約確認 |
| 官報・登記 | 決算公告・資本異動（非上場の数少ない公開情報） | public | v0.5 | — |
| **手動投入フォルダ** | **Speeda・TDB/TSR の PDF、IM、コンサル報告書、面談メモ** | premium/vdr | ✅ **v0の主役** | 投資プロが普段DLするものを放り込むだけ。**API 契約問題（Q26）を回避** |
| Speeda/TDB API | 自動取得 | premium | 後日 | **Q26（AI利用可否）の確認後** |

**設計判断**: v0 は「手動投入フォルダ」を一級のコレクタとして扱う。
ライセンス交渉を待たずに動き、「資料を放り込むだけ」の UX と完全に整合する。

## 2. Action Router

```
retrievability_prior（テンプレ由来）× 実測（このチャネルで実際に取れたか）で判断:
  public 高     → 追加の狙い撃ち収集（クエリを spec_item から生成）
  premium 高    → 「Speeda で◯◯レポートを落として投入してください」と具体的に依頼（v0）
  vdr/expert 高 → questions へ変換（VDR請求リスト / 面談質問 / コンサルスコープ）
実測でチャネルの成功率を記録し、prior を更新（Worker×チャネル較正の種。効果は長期 P24）
```

## 3. 検証スタック（生成と別ベンダ・特権つき P5）

### L1 接地検証（FineVerify 型）
```
1. 主張を検証可能なサブ質問に分解（数値・固有名詞・日付・比較の各要素）
2. 各サブ質問を原文スパンと照合。judge への問いは二値のみ:
   「このスパンはこの主張を支持するか」Yes/No/Partial（P10）
3. 順序ランダム化＋両順序評価。不一致は Partial 扱いで人間キューへ
4. judge は生成側と別ベンダのモデル。judge と人手判定の一致率(κ)を常時記録（P14）
```

### L2 数値エンジン
```
- 抽出値は三値（value/NOT_FOUND/AMBIGUOUS）。NOT_FOUND を値で埋めたら即テスト失敗
- 計算は全て Python（決定論的）。恒等式: BS一致 / 構成比の合計 / 前期比の連続性 /
  セグメント合計=全社 / 単位・通貨の整合
- 上場のみ: XBRL 計算リンクベース検証（E1 実験の結果を閾値に反映）
```

### L3 独立性クラスタリング（P22）
```
ヒューリスティック（v0）: 同一数値＋同一日付近傍＋類似文面 → 同一クラスタ
derived_from が判明したら確定。クラスタ単位でしか verified_count に数えない
```

### L4 時点整合
```
全 evidence の as_of を検査。鮮度窓（項目ごと）超過は減価。
supersedes 連鎖で修正再表示を追跡（修正の存在自体を赤旗としてウォッチリストへ）
```

### L5 矛盾検出（P20）
```
同一 spec_item に紐づく evidence 間で値・主張が不整合 → contradicts 辺を張る
特に seller_provided（IM）vs 外部証拠 の突合を必ず全数実行
出力では両方を並記。解消は「追加取得」でのみ行い、削除・平均はコードとして存在しない
```
