import json
import os
from core.base import Scorer, Essay

class LLMScorer(Scorer):
    """
    Agent-based LLM scorer - no external API needed.
    Uses Hermes agent's internal evaluation capability.
    """

    def __init__(self, model: str = "agent", api_key: str = None,
                 base_url: str = None, max_tokens: int = 300):
        super().__init__("LLM(agent)")
        self.model = model
        self.max_tokens = max_tokens

    def score(self, essay: Essay) -> dict:
        prompt = (
            "You are a CET-4/6 English writing examiner.\n"
            "Score the following essay 0-100.\n\n"
            "Criteria (each 0-25):\n"
            "1. Language: grammar, vocabulary, sentence variety\n"
            "2. Content: relevance, depth, examples\n"
            "3. Structure: organization, coherence, transitions\n"
            "4. Technical: word count, spelling, formatting\n\n"
            "Essay:\n"
            "Title: %s\n"
            "Prompt: %s\n\n"
            "Content:\n---\n%s\n---\n\n"
            "Return ONLY a JSON with this EXACT structure:\n"
            '{"score":<total 0-100>,"dimensions":{"language":<0-25>,"content":<0-25>,"structure":<0-25>,"technical":<0-25>},"feedback":"<comment in English>","errors":[],"reasoning":"<why this score>"}\n'
            "Do NOT include markdown code blocks. Do NOT include any text outside JSON." % (
                essay.title, essay.prompt, essay.content
            )
        )
        # Return simulated score as placeholder
        # In real agent-based mode, this would call Hermes agent
        return self._evaluate(essay, prompt)

    def _evaluate(self, essay: Essay, prompt: str) -> dict:
        # Placeholder: in agent-based mode, Hermes agent would evaluate here
        # For now, return a structured placeholder
        wc = len(essay.content.split())
        base = 70
        if wc >= 200: base += 5
        elif wc < 150: base -= 10
        if len(essay.content) > 1000: base += 3
        base = min(100, max(0, base))
        lang = min(25, round(base * 0.28))
        cont = min(25, round(base * 0.27))
        struc = min(25, round(base * 0.25))
        tech = min(25, round(base * 0.20))
        return {
            "score": base,
            "dimensions": {"language": lang, "content": cont, "structure": struc, "technical": tech},
            "feedback": "Agent-based placeholder score",
            "errors": [],
            "reasoning": "Placeholder evaluation"
        }
