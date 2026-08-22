---
doc_id: disc-integrated-v2
title: "Integral Prism v2.0 — 統合設計（Decision-Centric Meta-Research Control Plane）"
version: 2.0.0
status: accepted
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: proposal
language: ja
tags: [v2, integrated-design, decision-centric, voi, epistemic-ledger, external-review]
depends_on: [disc-prism-proposal, t-design-principles, cs-evidence-graph, t-decision-boundary, t-information-value-eig]
supersedes: [disc-prism-proposal（Phase 0-3 の枠組みを、より厳密な制御理論として再定式化）]
external_source: [S-137]
---

# Integral Prism v2.0 — 統合設計

> **経緯**: [16-prism-proposal-vs-sakana.md](16-prism-proposal-vs-sakana.md) で
> 「着手時の作戦盤＋生きた台帳」を確定した後、外部から独立に作成された設計評価文書
> （`[S-137]`、以下「外部評価」）を受領した。両者は**独立に同じ結論に収束していた**。
> 本文書は外部評価を査読し、我々の corpus（120出典・討論16本）で補強・修正した**統合版**である。

## 0. 一言で

> **v1（討論16まで）**: 「案件着手時に、判断を分ける論点と決着方法を1枚で返す」
> **v2（本文書）**: それを**制御理論として厳密化**する —
> Prism は LLM ではなく、**複数の Research Worker・データ源・計算・人間質問を
> 「Research Action」として同列に扱い、その中から投資判断に対する期待価値が
> 最大のものを選び続ける制御層**である。

Decision Compiler（何を決めるか）／ Dual Loop（既知の不確実性を潰す INNER と、
モデル自体の欠落を疑う OUTER）／ Epistemic Ledger（証拠を文章でなく状態として持つ）／
Action Router（到達可能性でチャネルを切替）／ Stop Rule（レポートの長さでなく期待価値ゼロで止まる）／
Outcome Calibration（結果でモデルとワーカーを較正する）の6要素からなる。

---

## 1. 外部評価の査読結果（要約）

**採用**（我々の設計を上回っていた3点）:

1. **到達可能性（retrievability）を状態として持つ** — 「Web で見つからないものに Web 予算を浪費しない」。
   我々の Evidence Graph には無かった一級概念 → **P21として採用、スキーマに追加**
2. **Negative status の三分類**（supported_negative / unknown / not_searched）—
   「不在を真に変換しない」を型で強制する。我々の三値抽出（NOT_FOUND）より一段洗練 → **P21に統合**
3. **Dual Loop と surprise-triggered reset** — VoI は「既にモデルに入っている不確実性」しか最適化できず、
   **変数自体が抜けていれば精密に間違える**。この指摘は正しく、静的な仮説空間ビルダーへの重要な補正

**修正して統合**（外部評価の弱点）:

4. **タイミングの欠落** — 外部評価はどこにも「いつ介入するか」を書いていない。
   §8 の例は DD 中盤から始まる。しかし実務判定（討論での却下）により確定した最重要の洞察は
   **「着手時に、予算配分前に効く」**。→ **Decision Compiler の初回実行を Phase 0 に固定**
5. **Decision Compiler の入力負荷** — 機械可読な alternatives/utility/threshold を前提にすると、
   忙しい実務家からは永遠に入力されない（F4′、DQ6）。→ **P23: 最小形からの段階導入**を明記
6. **疑似定量化のリスク** — Priority 式（6因子の積）は、自ら戒めた「精密な posterior の偽装」に
   接近しかけている。ノイズの積は結果をノイズに支配させる。→ 半定量スコアは**順位付けにのみ使い、
   絶対値を顧客に見せない**（△△△△△の5段階等）
7. **較正 Moat の時間軸誇張** — 年5–15件・結果判明2–5年では、較正行列は何年もデータ点数を上回る。
   → **P24: 近期は台帳自体、較正は長期資産**と時間軸を分けて主張する
8. **統治・安全・契約の欠落** — セキュリティ（間接プロンプトインジェクション）、署名・監査（FINRA/EU AI Act）、
   ライセンス（Worker として外部製品を呼べるか）が一切ない。→ **P18/P12 をそのまま適用**
9. **孤立と独立の混同** — Blind challenge lane は multi-agent の同調は防ぐが、
   隔離されたレーンも同じ訓練分布を共有している。**孤立 ≠ 独立**。
   真に非主流な変数の供給源は結局、outside-view の実データと人間（P3/P17）

**保留**（検証不能・要一次確認）:

10. 引用文献 R1–R25（DeepTRACE, ARGUS, CROWN-QA, CAMA, POPPER 等）は
    この環境からアクセス不可のため**未検証**。特に [R2] の著者表記は AB-MCTS 原論文と
    一致しない可能性がある。個別の `S-ID` は付与せず、`[S-137]` 配下に一括で「未検証の外部引用」と記録した。
    **本開発着手前に、一次ソースへの到達可能な環境で再検証すること。**

---

## 2. アーキテクチャ（6要素）

### 2.1 Decision Compiler — 何を決めるのかを機械可読にする（★段階導入 P23）

> ⚠️ **本節の Stage 0 は [18-internal-build-and-zero-input.md](18-internal-build-and-zero-input.md) で改訂された。**
> 「人間が30秒で3行書く（必須）」は撤回。**入力ゼロ**（業界テンプレート自動選択 ＋
> 初期資料からの自動検出 ＋ ファンド標準閾値の一度きり設定）が正となり、人間の入力は任意の補強に格下げされた。

```
Stage 0（着手時・30秒・必須）: 人間が3行書く ← ★撤回済み。18章の入力ゼロ版が正
  「この投資が失敗するとしたら理由」を3つ（P17: AIの出力を見る前に）

Stage 1（自動）: Stage 0 から命題を自動生成
  「顧客集中が高い」「成長が市場要因でなく特需」等の検証可能な命題へ変換

Stage 2（案件が進んだら・任意）: 簡易感度モデル
  Entry Multiple × 成長 × マージン × Exit Multiple × レバレッジ の最小形
  → トルネード図で「どの前提が判断を反転させるか」を機械的に特定
  → 数値計算は必ずコード（P19）。LLMに計算させない
```

**外部評価への修正点**: alternatives / utility / threshold のフル定義を Stage 0 に要求しない。
**Stage 0 が空でも Prism は動く**（型とケース記憶から仮説を出す）。人間の入力は「基準線」であって
「起動条件」ではない。

### 2.2 Dual Loop — INNER（潰す）と OUTER（疑う）

```
INNER LOOP（既知の不確実性を効率よく潰す）
  仮説×証拠のACH行列を持ち、各 Question の期待情報価値（EIG/VoI）でランキング
  VOI(a) の理論定義: Eₒ[max_d E[U(d,θ)|Sₜ,o,a]] − max_d E[U(d,θ)|Sₜ]
  ★ MVP では精密な posterior を偽装しない。半定量スコアで「順位」だけ出す:
    Priority ≈ f(DecisionSensitivity, Uncertainty, DiscriminativePower,
                  Retrievability, Independence) ÷ Cost
    − 5段階ラベルの組み合わせとして提示。数値の絶対値は顧客に見せない

OUTER LOOP（Model Challenge Gate — 定期的に発火。常時ではない）
  1. Inside-view : 通常の事実調査
  2. Falsification: 現行仮説が成り立つなら観測されるはずの事実を作り、反証を探す（ACH/POPPER型）
  3. Outside-view : 類似ディールの base rate（reference class）
  4. Blind challenge: 初期段階では他の結論を見せず独立に欠落変数を出させる
     ★ 孤立 ≠ 独立。真の多様性は「人間の3行」と「過去案件の型」からしか来ない（P3, P17）
  5. Surprise gate : 新証拠が現行モデルで説明できない、または確度が更新されないなら
     → 新変数を追加して INNER LOOP をリセット
```

### 2.3 Epistemic Ledger（＝我々の Evidence Graph の拡張）

`../coding-strategy/02-evidence-graph.md` のスキーマに、外部評価から2つのフィールドを追加した（v0.2.0）:

```
Evidence.negative_status : supported_negative | unknown | not_searched   ← P21
Evidence.independence_cluster_id                                        ← P22（同一プレスリリース由来の縮約）
Question.retrievability_estimate                                        ← P21（チャネル切替の判定材料）
```

### 2.4 Action Router — 「Web で分からない」を永遠に Web 検索しない

```
到達可能性が高い（公開情報で解決可能）    → Web検索 / Deep Research系 / 有償DB
到達可能性が低い（対象企業固有・非公開）  → VDR直参照 / 経営者Q&A / エキスパートコール / 計算
判定不能                                → 探索して retrievability を実測し、閾値以下なら即座に切替
```
**注**: 外部評価は AlphaSense / Marlin / Deep Research 自体を「Worker」として呼ぶ設計を提案している。
これは疎結合の原則（W-1）と一致するが、**ライセンス条項がプログラマティックな再統率を許すかは未確認**（Q26）。
契約前に必ず確認すること。

### 2.5 Stop Rule（レポートの長さでは止まらない）

```
以下の全条件で停止:
  1. 最大の Research Action の Net Value ≤ 閾値（P15: プロキシ-現実の乖離も監視）
  2. 主要な投資判断が、残存不確実性の妥当な範囲の摂動に対して安定
  3. Decision-critical な Unknown は「解消」または「条件付き判断として明示処理」のいずれか
  4. OUTER LOOP を通過し、欠落変数の疑いが未処理でない
  5. 「何が見つかれば判断が変わるか」が明記されている
```

### 2.6 Outcome Calibration（★時間軸を分けて語る — P24）

```
近期（初日から効く）: 台帳そのものの価値
  - 検証済み証拠の量、矛盾検出、Unknown の適切な管理
  - これは「使うほど良くなる」ものではなく「その場で効く」もの

長期（年5-15件×2-5年で育つ）: Worker/Source/Action の較正
  - どのワーカーが、どの論点タイプで、実際に当たったか
  - Firm-specific reference class（自社の過去案件・見送り案件）
  - ★ 「長期的なMoatになる」と主張してよいが、「来年効く」とは言わない
```

---

## 3. Red Team（外部評価の失敗モードに、我々の指摘を追加）

| # | 失敗モード | 出所 | 対策 |
|---|---|---|---|
| 1 | 決定モデルが粗く VoI が誤誘導 | 外部評価 | OUTER challenge、過去案件での重要論点recallがbaseline以下なら停止 |
| 2 | LLM が疑似確率を作る | 外部評価 | MVP は順位のみ。P16と整合（確率は内部保持、外部表示は段階的） |
| 3 | Web-only に閉じる | 外部評価 | retrievability gate（P21） |
| 4 | Agent の同調（孤立≠独立） | 外部評価＋本文書の補正 | challenge lane に加え、**人間の3行と過去案件の型を必ず混ぜる** |
| 5 | 較正効果を焦って主張し、効かないと判定される | 本文書（P24） | 近期価値（台帳）と長期価値（較正）を分離して説明する |
| **6** | **★意思決定モデルが実務家から入力されない（F4′）** | **我々の討論、外部評価には欠落** | P23: 3行入力から段階導入。空でも動く設計にする |
| **7** | **★間接プロンプトインジェクション** | **我々の討論、外部評価には欠落** | P18: 二層LLM・capability・taint 伝播 |
| **8** | **★署名・監査証跡が無い** | **我々の討論、外部評価には欠落** | P12: 追記専用記録、FINRA型の人間署名 |
| **9** | **★Workerライセンスがプログラマティック利用を禁じる** | **我々の討論（Q26）** | 契約前に必ず確認。NGなら Action Router の他社連携部分を縮小 |
| 10 | 成果が「レポート品質」止まりで投資価値を証明できない | 外部評価 | 評価指標を decision change / critical blindspot / calibration に固定。文章評価のみなら中止 |

---

## 4. 評価設計（外部評価の Blinded Benchmark を採用）

外部評価 §12 の3フェーズ設計は、我々の `t-ip-evaluation-design` の評価Aと**独立に同型**であり、そのまま採用する。

```
Phase 1 Retrospective : 過去30-50案件の当時資料で、人間メモ/DR/金融AIと比較
Phase 2 Shadow live    : 10-20件、ICへ影響させず並走。追加論点が実際のDD requestに採用されたか
Phase 3 Prospective    : 限定案件で正式運用

KPI（外部評価＋我々の評価Dを統合）:
  Critical Issue Recall / Decision-Relevant Novel Evidence / False Confidence Rate /
  Calibration(Brier) / Independent Evidence Ratio / Research Efficiency /
  Unknown Integrity / ★アナリストの検証時間（我々の評価D）

Kill criterion（外部評価の文言をそのまま採用）:
  「より長い文書を出すだけで、Critical Issue Recall・Decision-Relevant Evidence・
   Calibration のいずれも改善しないなら、Prism は中止する」
```

---

## 5. 実装ロードマップ（外部評価の段階付けと、我々の M0-M4 を統合）

| 外部評価の段階 | 我々の M | 作るもの | 作らないもの |
|---|---|---|---|
| PoC 0 | **M0-M1** | Decision Compiler最小形（3行→命題）、感度モデル、Ledger、3-5 Action型、半定量Priority | 独自検索エンジン、独自LLM、豪華UI |
| PoC 1 | **M1-M2** | OUTER challenge lane、Evidence checks（P21/P22）、web↔VDR↔計算のRouter | Marlin型の木探索そのもの |
| MVP | **M2-M3** | Workerベンチマーク、retrievability較正、専門家/経営者Q&A連携、Stop Rule | 全金融ワークフローの再実装 |
| Production | **M4** | SSO/権限/監査、案件履歴、Outcome Calibration、IC統合 | コモディティ化した機能の内製維持 |

---

## 6. この統合が変えたもの / 変えなかったもの

**変えなかった**（v1から継続）:
- 一言の結論：「調べる機械」ではなく「調べ終わったことを証明する機械」
- 実益は V2（損失回避）＋V4（説明責任）。V1（時間）では戦わない
- 楔は着手時（W1 の事後校閲は却下のまま）
- サカナ・Google・データベンダーとの戦い方（模倣の非対称、疎結合、私有情報）

**変えた**（v2の修正）:
- 商品の説明を「作戦盤」という比喩から、**Decision-Centric Meta-Research Control Plane**という
  制御理論の言葉に格上げした（対外説明ではどちらを使うかは D9 のまま未決）
- Evidence Graph に retrievability・negative_status・independence_cluster を追加（P21/P22）
- 意思決定モデルの取得を明示的に3段階へ分解し、Stage 0 が空でも動くと明記した（P23）
- 較正 Moat の主張を時間軸で分離した（P24）
- Red Team に F4′・セキュリティ・署名・ライセンスの4項目を追加した

## 7. 次の一手

```
1. R1-R25 の一次検証（arXivアクセス可能な環境で。特にR2の著者確認）
2. Decision Compiler Stage 0（3行入力）のUIモックを、次回の顧客接点で見せる
3. Evidence Graph v0.2.0（retrievability/negative_status）をスキーマ実装に反映
4. Q26（Workerライセンス）を最優先で確認 — Action Routerの前提を左右する
5. Phase 1 Retrospective の評価設計を、外部評価のKPIと我々の評価Dを統合した形で確定する
```
