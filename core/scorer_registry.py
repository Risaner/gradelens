"""
Scorer Registry
"""
from core.scorers import LLMScorer
from scorers.agent_scorer import AgentScorer
from scorers.iwrite_scorer import IwriteScorer
from scorers.pigai_scorer import PigaiScorer

SCORER_REGISTRY = {
    "deepseek": lambda: LLMScorer("deepseek"),
    "qwen": lambda: LLMScorer("qwen"),
    "openai": lambda: LLMScorer("openai"),
    "iwrite": lambda: IwriteScorer(),
    "agent": lambda: AgentScorer(),
    "pigai": lambda: PigaiScorer(),
}


def get_scorer(name: str):
    if name not in SCORER_REGISTRY:
        raise ValueError(f"Unknown scorer: {name}. Available: {list(SCORER_REGISTRY.keys())}")
    return SCORER_REGISTRY[name]()