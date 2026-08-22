---
doc_id: cs-bizdd-spec
title: "Biz DD カバレッジ・スペック v0.1（叩き台）— 固定の物差し"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: spec
language: ja
tags: [bizdd, coverage-spec, ten-boxes, driver-tree, fixed-yardstick]
depends_on: [disc-internal-build, cs-evidence-graph]
---

# Biz DD カバレッジ・スペック v0.1（叩き台）

> **これがカバレッジ監査の「固定の物差し」である。**
> 毎回変動する DR・コンサル成果物を、この物差しに突き合わせて filled / thin / missing / unknown を判定する。
> **本版はユーザー（投資プロ）の校正待ちの叩き台**。「うちの物差しと違う」箇所の指摘で確定させる。

## 構造

- **第1軸: 情報カテゴリ 10箱 × 必須項目**（本文書）
- **第2軸: EBITDA ドライバーツリー**（→ discussion/18 拡張。項目は `driver` 列でツリーへ接続）
- 各項目の属性:
  - `must/should` — 必須か推奨か
  - `retrievability` — 到達可能性の事前値: `public`（公開で取れる）/ `premium`（有償DB）/
    `vdr`（VDR・社内資料が必須）/ `expert`（専門家・ヒアリング必須）。Action Router の初期値
  - `driver` — ドライバーツリー上の対応ノード

## 10箱 × 必須項目

### 箱1: 市場
| 項目 | must | retrievability | driver |
|---|---|---|---|
| 市場規模（金額・数量、セグメント別） | must | public/premium | 数量←市場 |
| 過去成長率・将来成長率と予測根拠（出所別に） | must | public/premium | 数量←市場 |
| 成長の分解（数量×価格、構造要因×景気要因） | must | premium/expert | 数量・単価 |
| 市場の構造変化（技術・規制・代替品・顧客行動） | must | public/expert | 市場・脅威 |
| 景気感応度・シクリカリティ | should | public | 市場 |

### 箱2: 顧客
| 項目 | must | retrievability | driver |
|---|---|---|---|
| 顧客セグメントと構成比 | must | vdr | 数量←シェア |
| 上位顧客集中度（Top1/5/10） | must | vdr | 数量（下方リスク） |
| 継続率・解約率（リピート率）の水準と推移 | must | vdr | 数量 |
| 購買決定要因（KPC）と価格感度 | must | expert | 単価 |
| スイッチングコストの実在性 | should | expert | シェア防御 |

### 箱3: 競合
| 項目 | must | retrievability | driver |
|---|---|---|---|
| 競合マップとシェア（推移含む） | must | public/premium | シェア |
| 対象会社のポジショニング（何で勝っているか） | must | public/expert | シェア |
| 競合の戦略的動き（投資・新製品・価格） | must | public | シェア（脅威） |
| 新規参入・代替品の脅威 | must | public/expert | 市場・シェア |
| 競争の基盤の変化可能性（AI 等） | should | expert | 構造変化 |

### 箱4: 製品・価格
| 項目 | must | retrievability | driver |
|---|---|---|---|
| 提供価値と差別化の実体（顧客側の認識か） | must | expert | 単価・シェア |
| 価格設定と価格改定の履歴（値上げ実績） | must | vdr | 単価 |
| 価格転嫁力（コスト上昇時に転嫁できた実績） | must | vdr/expert | 単価・マージン |
| 製品ミックスと収益性の分布 | must | vdr | 単価・マージン |
| パイプライン・製品ライフサイクル | should | vdr | 成長レバー |

### 箱5: チャネル・営業
| 項目 | must | retrievability | driver |
|---|---|---|---|
| チャネル構造と依存度（代理店・プラットフォーム） | must | vdr | 数量（下方リスク） |
| 営業体制と人的依存 | must | vdr/expert | 数量 |
| 顧客獲得の再現性（獲得コスト的観点） | should | vdr | 成長レバー |
| チャネルの構造変化（直販化・EC 化等） | should | public/expert | 数量 |

### 箱6: オペレーション・サプライ
| 項目 | must | retrievability | driver |
|---|---|---|---|
| コスト構造の分解（変動/固定、主要項目） | must | vdr | マージン |
| サプライヤー集中と調達リスク | must | vdr | マージン（下方） |
| キャパシティと拡張性（成長の物理的制約） | must | vdr/expert | 数量上限 |
| 品質・事故・リコール履歴 | should | public/vdr | 下方リスク |

### 箱7: 収益の質
| 項目 | must | retrievability | driver |
|---|---|---|---|
| 収益の性質（リカーリング比率・契約期間・解約条項） | must | vdr | 数量の安定性 |
| 会計方針の変更履歴（★開示から自動検出可能） | must | public | 検証（横断） |
| 顧客単位・製品単位の採算 | must | vdr | マージン |
| 運転資本の特性・季節性 | should | vdr | キャッシュ |
| 予算達成率の履歴（計画の信頼性） | must | vdr | 全ドライバーの信頼度 |

### 箱8: 経営・組織
| 項目 | must | retrievability | driver |
|---|---|---|---|
| キーマン依存（創業者・トップ営業・技術）と継続意向 | must | vdr/expert | 実行リスク |
| 組織の厚み・後継 | must | expert | 実行リスク |
| 離職率・採用力 | should | vdr/public(口コミ) | 実行リスク |
| ガバナンス・関連当事者取引 | must | public/vdr | 下方リスク |

### 箱9: 規制・外部リスク
| 項目 | must | retrievability | driver |
|---|---|---|---|
| 事業に効く規制と改正動向 | must | public | 市場・下方 |
| 許認可・ライセンスの安定性 | must | public/vdr | 事業継続 |
| 訴訟・コンプライアンス履歴 | must | public/vdr | 下方リスク |
| ESG・レピュテーション | should | public | 下方リスク |
| 地政学・為替・マクロ感応度 | should | public | 市場 |

### 箱10: 成長仮説の検証（★ドライバーツリーとの接続点）
| 項目 | must | retrievability | driver |
|---|---|---|---|
| エクイティストーリーの分解（どのドライバーに賭けているか） | must | 初期資料から自動推定 | ツリー全体 |
| 各成長レバーの実現可能性（値上げ/新製品/新地域/クロスセル/M&A/コスト） | must | 混合 | 成長レバー |
| 類似事例の base rate（outside view） | must | premium/記憶 | ツリー全体 |
| ダウンサイドシナリオと撤退可能性 | must | 計算 | 下方 |
| なぜ今売りに出ているか（売り手の動機） | must | expert | 情報の非対称 |

## 業種テンプレートによる変形（例）
| 業種 | 主な変形 |
|---|---|
| SaaS | 箱2を NRR / GRR / 解約コホート / CAC・LTV 中心に。箱7のリカーリング検証を厚く |
| 製造業 | 箱6（キャパ・サプライ・設備投資）を厚く。箱4に原材料転嫁の実績 |
| 消費財・小売 | 箱5（チャネル・棚・EC比率）を厚く。箱2はブランド・リピート |
| ロールアップ | 箱10に統合実績・シナジー実現率の base rate を追加 |

## 運用
1. 判定単位は**項目**（箱ではない）。filled / thin / missing / unknown を項目ごとに付ける
2. `retrievability=vdr/expert` の項目は、公開フェーズでは **unknown が正常**。
   「unknown＋取得手段」として発注仕様書へ流す（→ discussion/18 補正2の射影②）
3. **本スペックの変更は人間の承認を要する**（P13: 評価器の定義は人間が握る）
