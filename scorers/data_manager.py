"""
数据管理器：加载作文、保存评分结果
"""
import json
import os
import sys
from pathlib import Path
from typing import Dict, List

project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, project_root)

from core.base import Essay
from core.dataset import Dataset


def load_essays(data_dir: str = "data") -> List[Essay]:
    ds = Dataset(data_dir)
    return ds.load_all()


def load_manual_scores(data_dir: str = "data") -> Dict[str, Dict]:
    scores = {}
    for f in sorted(Path(data_dir).glob("manual_scores_batch*.json")):
        with open(f, "r", encoding="utf-8-sig") as fh:
            batch = json.load(fh)
        for entry in batch["essays"]:
            scores[entry["id"]] = entry
    return scores


def save_agent_scores(results: List[Dict], output_path: str = "data/results/agent_scores.json"):
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump({"essays": results}, f, ensure_ascii=False, indent=2)


def save_agent_score(result: Dict, output_path: str = "data/results/agent_scores.json"):
    if os.path.exists(output_path):
        with open(output_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    else:
        data = {"essays": []}
    found = False
    for i, e in enumerate(data["essays"]):
        if e["essay_id"] == result["essay_id"]:
            data["essays"][i] = result
            found = True
            break
    if not found:
        data["essays"].append(result)
    with open(output_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)


def build_score_prompt(essay) -> str:
    """为单篇作文构建评分 prompt"""
    system = """You are an experienced English language examiner grading Chinese college students' English essays (CET-4/6 level).

Score on 4 dimensions, each 0-25 (total 100):
1. Language (0-25): Grammar accuracy, vocabulary range, sentence variety
2. Content (0-25): Relevance to prompt, depth of argument, use of examples
3. Structure (0-25): Paragraph organization, transitions, clear intro/body/conclusion
4. Technical (0-25): Spelling, punctuation, formatting, word count compliance

Rules:
- Be strict but fair. Grade as you would for CET-4/6.
- Consider difficulty and strategy.
- Penalize Chinese-English interference, over-optimization, formulaic feel.
- barely_pass: grade harshly for poor quality.
- chenglish: penalize Chinese interference heavily.
- poor: grade low but not zero if any intelligible English.
- natural: reward authenticity.

Return ONLY valid JSON, no markdown, no backticks:
{"language": X, "content": X, "structure": X, "technical": X, "overall": X, "feedback": "...", "reasoning": "..."}"""

    strat_note = ""
    if essay.strategy == "natural": strat_note = "\nStrategy: NATURAL - reward authenticity."
    elif essay.strategy == "template": strat_note = "\nStrategy: TEMPLATE - bonus for structure but penalize formulaic."
    elif essay.strategy == "barely_pass": strat_note = "\nStrategy: BARELY_PASS - grade harshly."
    elif essay.strategy == "chenglish": strat_note = "\nStrategy: CHINESE-ENGLISH MIX - penalize heavily."
    elif essay.strategy == "poor": strat_note = "\nStrategy: POOR - grade strictly."
    elif essay.strategy == "over_optimized": strat_note = "\nStrategy: OVER-OPTIMIZED - penalize formulaic."
    elif essay.strategy == "chinese_writing": strat_note = "\nStrategy: CHINESE WRITING - not English."

    diff_note = f"\nDifficulty: {essay.difficulty.upper()}"

    return f"{system}\n\n---{diff_note}{strat_note}\n\nPROMPT:\n{essay.prompt}\n\nESSAY ({essay.category}, {essay.word_count} words):\n{essay.content}\n\nScore now. JSON only."