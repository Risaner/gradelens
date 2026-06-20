# AES-Bench: Agent Evaluation Score Benchmark

**Quantifying the bias between AI essay scorers (iWrite / Pigai) and human-accurate evaluation.**

---

[![Python](https://img.shields.io/badge/Python-3.10+-blue.svg)](https://www.python.org/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![CET-4/6](https://img.shields.io/badge/CET-4%2F6-666.svg)]()

## Overview

AES-Bench is a benchmark dataset and analysis framework for measuring **scoring bias in AI essay scoring systems** (iWrite / 批改网 PIGAI) compared to high-quality manual evaluation.

It uses 48 AI-generated CET-4/6 English essays across 7 writing strategies to answer: **Do AI scorers over-reward template essays and under-reward poor writing?**

### Key Finding

| Strategy | Agent vs Manual Gap | Interpretation |
|---|---|---|
| natural | -0.5 | Fair — no bias |
| template | +1.9 | Fair — slight preference |
| poor | -24.7 | Agent severely under-scores |
| barely_pass | -10.0 | Agent under-scores |
| chenglish | -19.5 | Agent under-scores |

**Overall:** Agent scoring shows -2.0 average gap with manual, **contradicting** the assumption that "AI always favors templates."

## Dataset

- **48 essays** across 4 categories and 3 difficulty levels
- 7 writing strategies: natural, template, poor, barely_pass, chenglish, over_optimized, chinese_writing

| Category | Count | Difficulty |
|---|---|---|
| Argumentative | 23 | High: 36 / Medium: 5 / Low: 7 |
| Chart | 10 | |
| News | 9 | |
| Mixed | 6 | |

## Installation

`ash
# Clone the repo
git clone https://github.com/Risaner/aes-bench.git
cd aes-bench

# Install dependencies
pip install -r requirements.txt
`

## Usage

### Quick start — check agent scores

`python
import json

# Load agent scores (already scored)
with open("data/results/agent_scores.json", encoding="utf-8") as f:
    data = json.load(f)

for essay in data["essays"][:5]:
    print(f"{essay['essay_id']}: {essay['overall']}/100")
`

### Run agent scoring pipeline

`ash
# Score all essays using Agent (via hermes CLI)
python scripts/agent_batch_runner.py

# Run gap analysis against manual scores
python scripts/run_gap_analysis.py
`

### Analysis

`python
from core.dataset import Dataset
from core.evaluator import Evaluator

ds = Dataset("data")
essays = ds.load_all()

# Access individual essays
for essay in essays:
    print(f"{essay.id}: {essay.strategy}, {essay.difficulty}, {essay.word_count} words")

# Evaluation metrics
evaluator = Evaluator()
qwk = evaluator.quadratic_weighted_kappa(...)
pcc = evaluator.pearson_correlation(...)
`

## Project Structure

`
aes-bench/
├── core/                   # Core modules
│   ├── dataset.py          # Essay dataclass + Dataset loader
│   ├── scorer_registry.py  # Scorer registry (agent, iwrite, llm)
│   ├── scorers.py          # LLMScorer base class
│   ├── scorers_iwrite.py   # iWrite browser automation
│   └── evaluator.py        # QWK, PCC, RMSE metrics
├── scorers/                # Scorer implementations
│   ├── __init__.py
│   ├── agent_scorer.py     # ★ Agent-based scorer (hermes chat)
│   ├── llm_scorer.py       # OpenAI-based scorer (placeholder)
│   ├── iwrite_scorer.py    # iWrite browser automation
│   └── pigai_scorer.py     # PIGAI API wrapper
├── scripts/
│   ├── agent_batch_runner.py    # Batch agent scoring
│   └── run_gap_analysis.py      # Gap analysis vs manual scores
├── data/
│   ├── essays/              # 48 essays (JSON + TXT)
│   ├── results/             # Agent scores
│   ├── analysis/            # Gap analysis report
│   ├── figures/             # Visualization PNGs
│   └── manual_scores_*.json # Manual evaluation ground truth
├── pyproject.toml           # Package config
├── requirements.txt         # Dependencies
└── README.md                # This file
`

## Methodology

### Essay Generation
48 AI essays were generated using diverse writing strategies:
- **natural**: Fluent, natural writing with varied structure
- **template**: Heavy use of CET templates (Firstly, Moreover, In conclusion)
- **poor**: Intentionally low-quality with grammar errors
- **barely_pass**: Minimal effort, barely meeting requirements
- **chenglish**: English sentences mixed with Chinese
- **over_optimized**: Over-polished, template-heavy
- **chinese_writing**: Written in Chinese (not English)

### Scoring Criteria (CET-4/6)
Each dimension scored 0-25, total 0-100:
1. **Language**: Grammar, vocabulary range, sentence variety
2. **Content**: Relevance, argument depth, examples
3. **Structure**: Paragraph organization, transitions, intro/body/conclusion
4. **Technical**: Spelling, punctuation, formatting, word count

### Gap Analysis
Gap = Agent Score - Manual Score. Positive = Agent scores higher than manual.

## Results

Full analysis in data/analysis/agent_gap_report.md.

Score distributions and gap charts in data/figures/.

## License

MIT License. See [LICENSE](LICENSE) for details.
