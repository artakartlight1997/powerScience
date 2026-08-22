"""アーキタイプ同定: 選択肢外を受理しない。失敗は推測でなく人間へ(P23)。"""
import pytest

from prism.contracts import ConfigError, LLMError
from prism.identify import archetype

from ..conftest import FakeLLM

CHOICES = ["ses_jutaku"]


def test_valid_choice_accepted():
    llm = FakeLLM(lambda r, s, u: {"archetype": "ses_jutaku", "rationale": "SES企業"})
    assert archetype(llm, "サンプルテック", "ITサービス", CHOICES) == "ses_jutaku"


def test_out_of_choices_rejected():
    llm = FakeLLM(lambda r, s, u: {"archetype": "saas"})  # 選択肢に無い
    with pytest.raises(ConfigError, match="--archetype"):
        archetype(llm, "X社", None, CHOICES)


def test_unknown_answer_asks_human():
    llm = FakeLLM(lambda r, s, u: {"archetype": "unknown"})
    with pytest.raises(ConfigError, match="ses_jutaku"):  # 選択肢を提示する
        archetype(llm, "X社", None, CHOICES)


def test_llm_failure_asks_human_not_guess():
    def boom(r, s, u):
        raise LLMError("down")
    with pytest.raises(ConfigError):
        archetype(FakeLLM(boom), "X社", None, CHOICES)
