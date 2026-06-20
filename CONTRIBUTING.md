# Contributing

Welcome to GradeLens!

## How to Contribute

### 1. Add a New Scorer

Create a file in `scorers/`, inherit `core.base.Scorer`, implement `score(essay) -> dict`, then register in `core.scorer_registry`.

### 2. Submit Real Human Scores

The bundled reference scores are AI-generated for demo purposes only. Real human scores welcome via PR.

### 3. Improve Evaluation Metrics

Add new methods in `core/evaluator.py`.

## Dev Setup

```bash
pip install -r requirements.txt
pip install pytest
python -m pytest tests/ -v
```