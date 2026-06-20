"""
Scorer Registry
"""
from core.scorers import LLMScorer
from core.scorers_iwrite import iWriteScorer
from scorers.agent_scorer import AgentScorer

SCORER_REGISTRY = {
    "deepseek": lambda: LLMScorer("deepseek"),
    "qwen": lambda: LLMScorer("qwen"),
    "openai": lambda: LLMScorer("openai"),
    "iwrite": lambda: iWriteScorer(),
    "agent": lambda: AgentScorer(),
}


def get_scorer(name: str):
    """获取评分器实例"""
    if name not in SCORER_REGISTRY:
        raise ValueError(f"Unknown scorer: {name}. Available: {list(SCORER_REGISTRY.keys())}")
    return SCORER_REGISTRY[name]()
