---
doc_id: t-competitive-map
title: "競争地図とリスク — どこに立つか"
version: 0.2.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: strategy
language: ja
tags: [competitive-map, positioning, risk, differentiation]
confidence: medium
primary_sources: [S-004, S-020, S-076, S-081, S-016]
related_topics: [t-sakana-marlin, t-google-gemini-dr, t-finance-platforms, t-commoditization-moat]
contributes_to: [strategy, positioning]
---

# 競争地図とリスク

## 1. 地図

```
          高単価・意思決定級
                 ▲
   外部DDファーム │
   (¥5M〜30M)    │        ★ Integral Prism（狙う位置）
                 │          = 反証済み証拠構造 + 較正 + 監査
   Sakana Marlin ●（≒¥9,800/run, 月¥150,000〜）
                 │
  Hebbia ● Rogo ●│ ● BlueFlame    ● AlphaSense
                 │
   Gemini DR ●   │  ● OpenAI DR  ● Perplexity
   ($2〜5/task)  ▼
          低単価・情報収集級
     ◀ 汎用 ────────────────────── 特化（PE ワークフロー） ▶
```

## 2. 軸ごとの対比

| 軸 | Marlin | Gemini DR | co-scientist | Hebbia/Rogo/BlueFlame | **Integral Prism（仮説）** |
|---|---|---|---|---|---|
| 制御構造 | 木探索（AB-MCTS） | 単一エージェント+計画 | マルチエージェント+トーナメント | パイプライン/抽出 | 中央集権マルチ + 検証 |
| モデル | **マルチモデル（他社込み）** | 自社 Gemini | 自社 Gemini | 複数束ね | マルチ（**生成と検証を別ベンダ**） |
| 報酬 | 非公開 `D` | RL 済み方策 | **Elo（ペアワイズ）** | なし | **decision-relevant EIG** |
| 成果物 | 100pレポート+スライド | 引用つきレポート | 仮説ランキング | 抽出表・定型資料 | **ACH行列+較正確率+残存リスク+次の3手** |
| 検証 | 自己評価 `C` | 自己評価+グラウンディング | 自己評価 | 抽出の正確性 | **特権を持つ独立検証器** |
| 人間 | 8時間放置 `C` | 計画の承認 | 科学者と協働 | 都度操作 | **4つの介入点** |
| 蓄積 | 実行ごとに消える `C` | しない | しない | 文書は残る | **ケースベース記憶（外した理由込み）** |
| 監査 | 不明 | 不明 | — | 一部 | **探索木＝監査証跡** |
| 単価 | ≒¥9,800/run | $2〜$5/task | — | 席数課金 | **¥100k〜¥1M/案件（想定）** |

**空白地帯**: 「**マルチモデル × 明示的な報酬（反証ベース） × 人間との協働 × 監査可能**」。
ここが Integral Prism の座標。

## 2.5 Sakana の垂直スタック（v0.2 追記）

前回は Marlin 単体で見ていたが、実際には**4層が積まれつつある** `[S-104][S-105]`。

```
  アプリ層         : Sakana Marlin（Ultra Deep Research, ≒¥9,800/run）
  オーケストレーション層: Sakana Fugu / Fugu-Ultra（フロンティア群を統率するモデル）
  モデル層         : Namazu（Kimi K2.6 の日本語特化チューン, $0.95/$4.00 per M）
  改善エンジン層   : RSI Lab（DGM / SIFT / Digital Red Queen）
```

**帰結**:
1. 「マルチモデルで束ねる」は **Fugu が製品化済み**。IP の差別化として語れない
2. 「日本語の品質」は **Namazu が特化済み**。同様
3. **EDINET-Bench ＋ Namazu ＋ Marlin** が揃っている以上、**日本語金融への降下は容易**
4. 一方で、この4層はすべて **「どう答えるか」の層**であり、
   **「何を調べるべきか」「その主張は本当か」「どれくらい確からしいか」の層は空いたまま** `C`

→ IP は **Sakana のスタックの上に載る（あるいは Fugu を呼ぶ）** 位置を取りうる。
→ [t-sakana-fugu-namazu](../01-competitors/sakana-fugu-and-namazu.md)

## 3. リスク

| リスク | 内容 | 緩和 |
|---|---|---|
| **フロンティアが降りてくる** | 「引用検証」を OpenAI/Google が標準搭載 | L0-L1（引用検証）だけでは差がつかない。**L3 反証・L4 較正＋顧客データ**まで積む |
| **Marlin が金融特化を深める** | Sakana は **EDINET-Bench** `[S-016]` に加え **Namazu（日本語モデル）** `[S-105]` を保有。降下は容易 | 実務工程（IC/PMI）と顧客固有データで戦う。**汎用リサーチ品質では戦わない** |
| **オーケストレーション層を握られる** | **Fugu** がモデル群の統率を製品化 `[S-104]` | その層では戦わない。**Fugu を部品として呼ぶ**選択肢も検討（要: ベンダ独立性との整合） |
| **自己改善で離される** | DGM / SIFT で**スキャフォールドが自動改善**される `[S-092][S-093]` | 我々も GEPA 型のプロンプト/ルーブリック進化は取り入れる。ただし**評価器の更新は人間承認**（P13） |
| **BlueFlame 等が同じ層に来る** | 「オーケストレーション」を名乗る `[S-081]` | 目的関数（反証・較正）で差をつける。抽出では戦わない |
| **エージェント PoC 疲れ** | PE 側で scaling は 10-15% `[S-076]` | 「1業務の正本化」から入る。全社導入を狙わない |
| **精度事故** | 誤引用1件で信頼喪失 | 引用 Fact Check ループを**出荷ゲート**にする |
| **説明コスト** | 新カテゴリは伝わらない | 既存メモを叩く（D10）など、**5分で価値が伝わる入口**を作る |

## 4. 一行のポジショニング（案）

- ✗ 「Deep Research の一種です」 → その瞬間に比較され、価格で負ける
- ○ **「投資仮説の反証エンジン」**
- ○ **「デューデリの証拠構造プラットフォーム」**

→ 未決論点 D9（`notes/discussion-agenda.md`）

## 5. 出典

- `[S-004]` Marlin 価格 ／ `[S-020]` Gemini DR 単価 ／ `[S-076]` PE 採用実態 ／ `[S-081]` 金融特化製品比較 ／ `[S-016]` EDINET-Bench
