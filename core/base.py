from dataclasses import dataclass, field
from typing import Dict, List, Optional
from abc import ABC, abstractmethod


@dataclass
class Essay:
    """一篇测试作文的完整数据结构"""
    id: str
    title: str
    prompt: str
    content: str
    category: str
    difficulty: str
    strategy: str
    word_count: int
    manual_score: Optional[float] = None
    tags: List[str] = field(default_factory=list)

    def __post_init__(self):
        if self.tags is None:
            self.tags = []
        if self.word_count == 0:
            self.word_count = len(self.content.split())


class Scorer(ABC):
    """评分器抽象基类"""

    def __init__(self, name: str):
        self.name = name

    @abstractmethod
    def score(self, essay: Essay) -> Dict:
        pass

    def batch_score(self, essays: List[Essay]) -> List[Dict]:
        return [self.score(e) for e in essays]
