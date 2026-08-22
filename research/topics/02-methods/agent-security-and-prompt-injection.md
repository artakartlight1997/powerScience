---
doc_id: t-agent-security
title: "エージェントのセキュリティ — 間接プロンプトインジェクション"
version: 0.1.0
status: draft
created: 2026-08-22
updated: 2026-08-22
project: integral-prism
doc_type: topic
topic_group: methods
language: ja
tags: [security, prompt-injection, exfiltration, camel, capability-control, agentdojo, mnpi]
confidence: medium-high
primary_sources: [S-126, S-127]
related_topics: [t-regulation-compliance, t-provenance, t-data-sources]
contributes_to: [architecture-constraints, enterprise-readiness]
---

# エージェントのセキュリティ — 間接プロンプトインジェクション

> **前回までのサーベイの完全な抜け。**
> Web を巡回しながら VDR の機密文書も読むエージェントは、**データ持ち出しの典型的な標的**である。
> 金融機関のセキュリティ審査で最初に問われる論点でもあり、「調べていません」で通る項目ではない。

## 1. 脅威モデル

攻撃者は**間接プロンプトインジェクション**により、
エージェントがタスク実行中に観測する外部保存データを**外部へ持ち出す** `[S-126]`。
攻撃文字列は **メール / クラウドサービス / Web ページ / ツールの説明文** に埋め込まれる `[S-126]`。

### 実際に起きたこと（2025年）`[S-126]`
- **EchoLeak（CVE-2025-32711）** — Microsoft 365 Copilot からの**ゼロクリック・データ持ち出し**
- **Amazon Bedrock エージェントの永続的なメモリ汚染**
- **CSS で隠したインジェクションによる広告審査のバイパス**
- **MCP のツール説明文経由でコーディングエージェントを侵害**

## 2. 定量的な深刻さ

| ベンチマーク | 規模 | 結果 |
|---|---|---|
| **Agent Security Bench (ASB)** `[S-126]` | 16の攻撃 × 11の防御 × 10シナリオ、400+ツール、13 LLM | **最高の平均攻撃成功率 84.3%**。既存防御の効果は限定的 |
| **AgentDojo** `[S-126]` | 97タスク、629のセキュリティテスト（メール/銀行/旅行/ワークスペース） | **有用性とセキュリティを同時に測る**点が特徴 |
| **InjecAgent** `[S-126]` | 1,054テスト、17のユーザツール、62の攻撃ツール | GPT-4 はベースラインで **24%**、強化プロンプトで **47%** 脆弱 |

> ### ⚠️ 最も重要な認識 `[S-126]`
> **プロンプトインジェクションは、現行の LLM アーキテクチャの内部では完全には解けない。**
> モデルレベルの攻撃面は事実上無限であり、**プロンプトで表現された防御はプロンプトで上書きされうる**。
> **単一の防御で解決する方法は存在しない。**
> アーキテクチャ的な統制・実行時監視・ガバナンスの3点セットが要る。

## 3. 有効な方向 — モデルの外で決定論的に統制する

2024〜2026年の研究は **「セキュリティをモデルの外側で、決定論的なポリシーとして強制する」**方向に収斂した `[S-127]`。
代表: **CaMeL / FIDES / Progent / RTBAS / FORGE**（capability、情報フローラベル、参照モニタ）`[S-127]`。

### CaMeL（Google DeepMind, arXiv:2503.18813）`[S-127]`
従来のソフトウェアセキュリティ（**制御フロー整合性・アクセス制御・情報フロー制御**）に着想を得た設計。

```
Privileged LLM   : タスクの統率を担う。信頼できる指示のみを読む。ツール呼び出しの権限を持つ
Quarantined LLM  : 信頼できないデータ（Web、外部文書）を扱う。★ツール呼び出し権限を持たない
カスタムインタプリタ:
   - 全ての値に capability（メタデータ）を付与し、データフローと制御フローを制限
   - 未信頼ソース由来の変数は、以降の全演算に taint を伝播させる
   - ツール呼び出しの直前に、ポリシーを強制
     例: 「メール送信は、宛先が信頼できるソース由来のときのみ許可」
```

**2026年には computer-use エージェントへの拡張**（*CaMeLs Can Use Computers Too*, arXiv:2601.09923）`[S-127]`。
実行時防御としては **ClawGuard**（ツール拡張エージェント向け）、**VIGIL**（verify-before-commit）など `[S-127]`。

## 4. IP への設計要件（P18 として明文化）

> **設計原則 P18: 未信頼コンテンツは隔離し、ツール呼び出しは capability で門番する。
> 「Web を読んだ LLM」に、そのまま機密データへのアクセス権とツール権限を与えない。**

具体的な要件:

| # | 要件 | 理由 |
|---|---|---|
| 1 | **二層 LLM**: Web/外部文書を読むモデルにはツール権限を与えない | CaMeL の中核 `[S-127]` |
| 2 | **taint 伝播**: 全証拠に「未信頼由来か」のラベルを付け、下流に伝播させる | 我々は既に証拠に ID とメタデータを持つ（→ [t-provenance](provenance-and-evidence-tracing.md)）。**同じ構造に載る** |
| 3 | **egress の門番**: 外部への送信（API 呼び出し、要約の投稿、メール）はポリシーで明示許可 | 持ち出し経路を塞ぐ |
| 4 | **案件データの隔離**: 案件 A の VDR を読んだセッションが、案件 B の文脈に触れない | MNPI / Chinese Wall（→ [t-regulation-compliance](../04-domain/regulation-and-compliance.md)） |
| 5 | **ツール説明文も未信頼として扱う** | MCP 経由の侵害事例 `[S-126]` |
| 6 | **実行時監視 ＋ 監査ログ** | 単一防御では不十分という結論 `[S-126]` |

### 我々にとっての追い風
IP は元々**「全証拠に出所メタデータを持たせ、追記専用で記録する」**設計（P11/P12）を採っている。
**taint 伝播も情報フロー制御も、この構造の上に自然に載る。**
→ **セキュリティ要件が、既存の設計方針と衝突しない**（むしろ補強する）。これは幸運な一致である。

### 我々にとっての向かい風
**「Web を自由に巡回する自律エージェント」という売り方は、金融のセキュリティ審査と正面衝突する。**
Marlin の「8時間自律巡回」も同じ問題を抱えるはず `C` → 宿題 Q21。

## 5. 出典

- `[S-126]` Agent Security Bench ／ AgentDojo ／ InjecAgent ／ *The Landscape of Prompt Injection Threats in LLM Agents* arXiv:2602.10453 ／ *Agent Data Injection Attacks are Realistic Threats* arXiv:2607.05120 ／ Zylos "Indirect Prompt Injection: 2026 State of the Art" ／ EchoLeak (CVE-2025-32711)
- `[S-127]` *Defeating Prompt Injections by Design*（CaMeL）arXiv:2503.18813 ／ *CaMeLs Can Use Computers Too* arXiv:2601.09923 ／ ClawGuard arXiv:2604.11790 ／ VIGIL arXiv:2601.05755 ／ *The Attack and Defense Landscape of Agentic AI* arXiv:2603.11088
