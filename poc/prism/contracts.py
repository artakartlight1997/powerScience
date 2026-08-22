"""データ契約と Protocol。docs/CONTRACTS.md §1-2 の実装。型定義はここが唯一。"""
from __future__ import annotations

from typing import Literal, Optional, Protocol

from pydantic import BaseModel, Field

Phase = Literal["T", "N", "DD"]
SourceKind = Literal["seller", "consultant", "general", "web", "filing"]
EvidenceStatus = Literal["value", "NOT_FOUND", "AMBIGUOUS"]  # P19: 三値
Grounded = Literal["none", "pass", "partial", "fail"]
JudgmentStatus = Literal["filled", "thin", "missing", "unknown"]
TrustLabel = Literal["trusted", "untrusted"]  # P18: taint
Dependence = Literal["high", "mid", "low"]


class Case(BaseModel):
    id: str
    name: str
    industry: Optional[str] = None
    archetype: str
    phase: Phase = "N"
    created_at: str
    round: int = 0
    stop_reason: Optional[str] = None  # 停止には必ず理由がある(fill.should_stop)


class SpecItem(BaseModel):
    """固定の物差しの1項目。boxes.yaml(第1層) + アーキタイプ(第2層)から構築。"""
    id: str
    case_id: str
    segment: Optional[str] = None       # None = 全社共通
    box: str
    key: str                            # 証拠との突合キー(= テンプレの item id)
    label: str
    must: bool = True
    retrievability: list[str] = Field(default_factory=list)
    freshness_days: int = 730
    required_clusters: int = 2          # filled に要る独立クラスタ数(P22)
    driver: Optional[str] = None
    dependence: Dependence = "mid"      # thesis_dependence(見張り台帳の重み)
    expect_absent: bool = False         # 「該当なし」が正解の項目(確認済みfilled)


class ExtractedValue(BaseModel):
    raw: str
    num: Optional[float] = None         # 数値はコードで parse する(P19)
    unit: Optional[str] = None


class Source(BaseModel):
    id: str
    case_id: str
    kind: SourceKind
    trust_tier: int                     # 1(開示)〜5(売り手の主張)
    seller_provided: bool = False       # I3: これのみでは filled 不可
    path: Optional[str] = None
    url: Optional[str] = None
    publisher: Optional[str] = None
    as_of: str                          # 情報が入手可能になった時点(point-in-time)
    content_hash: str                   # 冪等取り込みのキー
    snapshot_path: Optional[str] = None # 原文スナップショット(grounding の照合先)


class Evidence(BaseModel):
    id: str
    case_id: str
    source_id: str
    item_key: str
    quote: str                          # 原文からの逐語引用(grounding 対象)
    value: Optional[ExtractedValue] = None
    status: EvidenceStatus = "value"
    locator: dict = Field(default_factory=dict)   # {"page": n} 等
    trust_label: TrustLabel = "trusted"
    grounded: Grounded = "none"
    cluster_id: Optional[str] = None    # 独立性クラスタ(P22)
    seller_provided: bool = False
    as_of: str = ""


class Judgment(BaseModel):
    """カバレッジ監査の判定。audit.judge(純関数)だけが生成する。"""
    id: str
    case_id: str
    item_id: str
    status: JudgmentStatus
    verified_clusters: int = 0
    evidence_ids: list[str] = Field(default_factory=list)  # I1: filled/thin は必ず持つ
    contradiction_open: bool = False
    rationale: str = ""
    acquisition_path: Optional[str] = None  # I8: unknown は必ず持つ
    round: int = 0


class Question(BaseModel):
    """未充足項目から生成する問い。発注仕様書・オンライン収集の入力。"""
    id: str
    case_id: str
    item_key: str
    text: str
    channel: str                        # web / premium / vdr / expert / mgmt
    rank: int                           # 順位のみ。数値スコアは契約上返さない
    status: Literal["open", "routed", "answered"] = "open"


class Contradiction(BaseModel):
    """矛盾は削除も平均もしない(P20)。resolve は新証拠の追加でのみ起きる。"""
    id: str
    case_id: str
    item_key: str
    evidence_a: str
    evidence_b: str
    delta: float                        # 相対乖離
    status: Literal["open", "resolved"] = "open"


class Event(BaseModel):
    seq: Optional[int] = None
    case_id: str
    kind: str
    payload: dict
    actor: str = "system"
    prev_hash: str = ""
    this_hash: str = ""
    created_at: str = ""


# --- 例外(モジュール間で共有する唯一の例外群) ---
class LLMError(Exception):
    """LLM 呼び出し・JSON 検証の失敗。呼び出し側は項目単位で degrade する(C-7)。"""


class GateError(Exception):
    """gate による拒否(ホスト・パス・taint・ベンダ分離)。"""


class ConfigError(Exception):
    """設定不備。起動時に落とす。"""


# --- Protocol(C-1: モジュールはこれにのみ依存する) ---
class LLMClient(Protocol):
    def complete_json(self, role: Literal["generator", "verifier", "online"],
                      system: str, user: str) -> dict: ...


class Fetcher(Protocol):
    def fetch(self, url: str) -> Optional[str]: ...  # 失敗は None(例外にしない)
