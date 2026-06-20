import json
from pathlib import Path
from typing import List
from core.base import Essay


class Dataset:
    """数据集加载器"""

    def __init__(self, data_dir: str = "data"):
        self.data_dir = Path(data_dir)
        self.essays_dir = self.data_dir / "essays"
        self.annotations_file = self.data_dir / "annotations.json"

    def load_all(self) -> List[Essay]:
        """加载所有作文"""
        essays = []
        if not self.essays_dir.exists():
            return essays
        for json_file in sorted(self.essays_dir.glob("**/*.json")):
            with open(json_file, "r", encoding="utf-8") as f:
                data = json.load(f)
                essays.append(Essay(**{k:v for k,v in data.items() if k in Essay.__dataclass_fields__}))
        return essays

    def load_by_category(self, category: str) -> List[Essay]:
        """按类别加载"""
        essays = []
        cat_dir = self.essays_dir / category
        if cat_dir.exists():
            for json_file in sorted(cat_dir.glob("*.json")):
                with open(json_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                essays.append(Essay(**{k:v for k,v in data.items() if k in Essay.__dataclass_fields__}))
        return essays

    def load_by_strategy(self, strategy: str) -> List[Essay]:
        """按策略标签加载"""
        all_essays = self.load_all()
        return [e for e in all_essays if e.strategy == strategy]

    def get_summary(self) -> dict:
        """数据集统计摘要"""
        essays = self.load_all()
        if not essays:
            return {"total": 0}
        cats = {}
        diffs = {}
        strategies = {}
        for e in essays:
            cats[e.category] = cats.get(e.category, 0) + 1
            diffs[e.difficulty] = diffs.get(e.difficulty, 0) + 1
            strategies[e.strategy] = strategies.get(e.strategy, 0) + 1
        avg_words = sum(e.word_count for e in essays) / len(essays)
        return {
            "total": len(essays),
            "by_category": cats,
            "by_difficulty": diffs,
            "by_strategy": strategies,
            "avg_word_count": round(avg_words, 1),
        }
