"""
Agent-based Essay Scorer
通过 subprocess 调用 hermes chat 实现评分
"""
import json
import os
import subprocess
import sys
from core.base import Scorer
from typing import Any, Dict, Optional


class AgentScorer(Scorer):
    def __init__(self, timeout: int = 120):
        super().__init__("Agent")
        self.timeout = timeout

    def _build_prompt(self, essay: Dict[str, Any]) -> str:
        return (
            "Score this English essay on CET-4/6 criteria. "
            "Language(0-25), Content(0-25), Structure(0-25), Technical(0-25), Overall(0-100). "
            "Return ONLY valid JSON with keys: essay_id, language, content, structure, technical, overall, feedback, reasoning. "
            "No markdown, no backticks.\n\n"
            f"=== {essay['id']} === [{essay['category']}/{essay['difficulty']}/{essay['strategy']}]\n"
            f"Prompt: {essay['prompt']}\n"
            f"Content: {essay['content']}"
        )

    def score(self, essay):
        if hasattr(essay, '__dataclass_fields__'):
            essay = {k: getattr(essay, k) for k in ['id','title','prompt','content','category','difficulty','strategy','word_count']}
        prompt = self._build_prompt(essay)
        try:
            result = subprocess.run(
                ["hermes", "chat", "-q", prompt, "-Q", "--max-turns", "1"],
                capture_output=True, text=True, timeout=self.timeout,
                encoding="utf-8", errors="replace"
            )
            # Extract JSON from output
            output = result.stdout
            start = output.find("{")
            end = output.rfind("}")
            if start >= 0 and end >= 0 and end > start:
                score = json.loads(output[start:end+1])
                return score
        except Exception:
            pass
        return None
