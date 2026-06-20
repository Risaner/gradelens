"""
LLM-based Essay Scorer
Uses DeepSeek/Qwen/OpenAI as scoring engine
"""
import os
import json
from typing import Dict, Optional
from openai import OpenAI
from core.base import Scorer, Essay


class LLMScorer(Scorer):
    """
    LLM scorer for CET-4/6 English essays.
    Supports DeepSeek, Qwen, OpenAI providers.
    """

    SYSTEM_PROMPT = """You are an experienced English language examiner grading Chinese college students' English essays (CET-4/6 level).

Score the essay on 4 dimensions, each 0-25 points (total 100):

1. Language (0-25): Grammar accuracy, vocabulary range and appropriateness, sentence variety
2. Content (0-25): Relevance to the prompt, depth of argument, use of examples
3. Structure (0-25): Paragraph organization, transition words, clear intro/body/conclusion
4. Technical (0-25): Spelling, punctuation, formatting, word count compliance

Rules:
- Be strict but fair. Grade as you would for CET-4/6.
- Consider the difficulty level when grading.
- Penalize Chinese-English interference, over-optimization, and structural issues.
- Consider the STRATEGY: template essays get bonus for structure words but may lose points for formulaic feel. natural essays should be rewarded for authenticity.

Return ONLY valid JSON, no markdown, no explanation:
{"language": X, "content": X, "structure": X, "technical": X, "overall": X, "feedback": "..."}
"""

    def __init__(self, provider: str = "deepseek"):
        super().__init__(f"LLM({provider})")
        self.provider = provider
        if provider == "deepseek":
            api_key = os.environ.get("DEEPSEEK_API_KEY") or os.environ.get("OPENAI_API_KEY")
            self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com/v1")
            self.model = "deepseek-chat"
        elif provider == "qwen":
            api_key = os.environ.get("DASHSCOPE_API_KEY")
            self.client = OpenAI(api_key=api_key, base_url="https://dashscope.aliyuncs.com/compatible-mode/v1")
            self.model = "qwen-plus"
        elif provider == "openai":
            api_key = os.environ.get("OPENAI_API_KEY")
            self.client = OpenAI(api_key=api_key)
            self.model = "gpt-4o-mini"
        else:
            raise ValueError(f"Unknown provider: {provider}")

    def score(self, essay: Essay) -> Dict:
        """Score an Essay object. Returns dict with language/content/structure/technical/overall/feedback."""
        content = essay.content
        prompt = essay.prompt
        difficulty = essay.difficulty
        strategy = essay.strategy

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"Difficulty: {difficulty} | Strategy: {strategy}\nPrompt: {prompt}\n\nEssay:\n{content}"},
                ],
                temperature=0.3,
                max_tokens=500,
            )
            result_text = response.choices[0].message.content.strip()
            return self._parse_score_json(result_text)
        except Exception as e:
            return {
                "language": 0, "content": 0, "structure": 0, "technical": 0,
                "overall": 0, "feedback": f"Error: {e}", "error": True
            }

    @staticmethod
    def _parse_score_json(text: str) -> Dict:
        """Parse LLM output, handling markdown code blocks and prefixes."""
        import re
        # Strip markdown code blocks
        text = re.sub(r"```(?:json)?\s*", "", text)
        text = re.sub(r"```", "", text)
        text = text.strip()
        # Strip common prefixes
        for prefix in ["Here is", "Sure", "OK", "Below"]:
            if text.startswith(prefix):
                first_brace = text.find("{")
                if first_brace > 0:
                    text = text[first_brace:]
        return json.loads(text)

    def score_raw(self, content: str, prompt: str = "", difficulty: str = "medium", strategy: str = "natural") -> Dict:
        """Score raw essay content (backward-compatible interface for CLI/scripts)."""
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": self.SYSTEM_PROMPT},
                    {"role": "user", "content": f"Difficulty: {difficulty} | Strategy: {strategy}\nPrompt: {prompt}\n\nEssay:\n{content}"},
                ],
                temperature=0.3,
                max_tokens=500,
            )
            result_text = response.choices[0].message.content.strip()
            return self._parse_score_json(result_text)
        except Exception as e:
            return {
                "language": 0, "content": 0, "structure": 0, "technical": 0,
                "overall": 0, "feedback": f"Error: {e}", "error": True
            }